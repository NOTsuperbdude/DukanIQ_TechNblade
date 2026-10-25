"""
DukanIQ — Business Logic Services

Contains transactional logic for:
  - Purchase posting (atomic: purchase + batches + stock movements + supplier balance)
  - Sale completion (atomic: sale + batch allocation + stock movements + payment)
  - Damage recording (atomic: damage record + stock deduction + stock movement)
  - Expiry write-off (atomic: write-off record + stock deduction)
  - Stock adjustment
  - Dashboard stats
  - Supplier ledger
  - Notification generation
"""

import random
import string
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status

from app.models import (
    Shop, User, Product, ProductBatch, Supplier, Purchase, PurchaseItem,
    Sale, SaleItem, StockMovement, DamagedGoods, SupplierPayment,
    Notification, AuditLog,
    PurchaseStatus, PaymentStatus, SaleStatus, MovementType, DamageStatus,
    ExpiryStatus, NotificationType
)
from app.schemas import (
    PurchaseCreate, SaleCreate, DamagedGoodsCreate, StockAdjustmentCreate,
    SupplierPaymentCreate
)


# ─────────────────────────── HELPERS ─────────────────────────────

def generate_ref(prefix: str, length: int = 8) -> str:
    """Generate a unique reference code like PUR-A1B2C3D4."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}-{suffix}"


def log_audit(
    db: Session,
    shop_id: int,
    actor_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    reason: Optional[str] = None,
):
    log = AuditLog(
        shop_id=shop_id,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_data=before_data,
        after_data=after_data,
        reason=reason,
    )
    db.add(log)


def create_notification(
    db: Session,
    shop_id: int,
    notif_type: NotificationType,
    title: str,
    message: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
):
    notif = Notification(
        shop_id=shop_id,
        notification_type=notif_type,
        title=title,
        message=message,
        related_entity_type=entity_type,
        related_entity_id=entity_id,
    )
    db.add(notif)


def get_batch_expiry_status(expiry_date: Optional[date], warning_days: int = 30, urgent_days: int = 7) -> ExpiryStatus:
    if not expiry_date:
        return ExpiryStatus.safe
    today = date.today()
    days_remaining = (expiry_date - today).days
    if days_remaining < 0:
        return ExpiryStatus.expired
    elif days_remaining <= urgent_days:
        return ExpiryStatus.urgent
    elif days_remaining <= warning_days:
        return ExpiryStatus.expiring_soon
    return ExpiryStatus.safe


# ───────────────────────── PURCHASE SERVICE ────────────────────────

def post_purchase(db: Session, purchase_data: PurchaseCreate, shop_id: int, actor_id: int) -> Purchase:
    """
    Atomically creates a purchase, batch receipts, stock movements, and updates supplier balance.
    Raises HTTPException if validation fails.
    """
    # Validate supplier belongs to shop
    supplier = db.query(Supplier).filter(
        Supplier.id == purchase_data.supplier_id,
        Supplier.shop_id == shop_id,
        Supplier.is_active == True
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Validate all products
    items_data = []
    subtotal = 0.0
    for item in purchase_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.shop_id == shop_id,
            Product.is_active == True
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        # Calculate line total
        gross = item.quantity * item.unit_cost
        discount = gross * (item.discount_percent / 100)
        after_discount = gross - discount
        tax = after_discount * (item.tax_percent / 100)
        line_total = after_discount + tax
        subtotal += line_total
        items_data.append((item, product, line_total))

    total_amount = subtotal - purchase_data.discount_amount + purchase_data.tax_amount + purchase_data.additional_charges
    amount_paid = min(purchase_data.amount_paid, total_amount)
    outstanding_balance = total_amount - amount_paid

    # Determine payment status
    if amount_paid <= 0:
        payment_status = PaymentStatus.unpaid
    elif amount_paid < total_amount:
        payment_status = PaymentStatus.partial
    else:
        payment_status = PaymentStatus.paid

    # Create the Purchase record
    purchase_ref = generate_ref("PUR")
    purchase = Purchase(
        shop_id=shop_id,
        supplier_id=supplier.id,
        purchase_ref=purchase_ref,
        supplier_invoice_number=purchase_data.supplier_invoice_number,
        purchase_date=purchase_data.purchase_date,
        payment_due_date=purchase_data.payment_due_date,
        status=PurchaseStatus.posted,
        payment_status=payment_status,
        subtotal=subtotal,
        discount_amount=purchase_data.discount_amount,
        tax_amount=purchase_data.tax_amount,
        additional_charges=purchase_data.additional_charges,
        total_amount=total_amount,
        amount_paid=amount_paid,
        outstanding_balance=outstanding_balance,
        notes=purchase_data.notes,
        created_by=actor_id,
    )
    db.add(purchase)
    db.flush()  # get purchase.id without committing

    # Create purchase items, batches, and stock movements
    for item, product, line_total in items_data:
        # Create or find batch
        batch = ProductBatch(
            product_id=product.id,
            supplier_id=supplier.id,
            batch_number=item.batch_number or generate_ref("BATCH", 6),
            received_date=purchase_data.purchase_date,
            expiry_date=item.expiry_date,
            unit_cost=item.unit_cost,
            original_quantity=item.quantity,
            available_quantity=item.quantity,
        )
        db.add(batch)
        db.flush()

        # Create purchase item
        p_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            batch_id=batch.id,
            batch_number=batch.batch_number,
            expiry_date=item.expiry_date,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            discount_percent=item.discount_percent,
            tax_percent=item.tax_percent,
            line_total=line_total,
        )
        db.add(p_item)

        # Stock movement — get current stock for before/after
        current_stock = db.query(func.sum(ProductBatch.available_quantity)).filter(
            ProductBatch.product_id == product.id,
            ProductBatch.available_quantity > 0
        ).scalar() or 0.0

        movement = StockMovement(
            shop_id=shop_id,
            product_id=product.id,
            batch_id=batch.id,
            movement_type=MovementType.purchase_receipt,
            quantity_change=item.quantity,
            quantity_before=current_stock - item.quantity,  # before this batch was added
            quantity_after=current_stock,
            reference_type="purchase",
            reference_id=purchase.id,
            actor_id=actor_id,
            reason=f"Purchase received: {purchase_ref}",
        )
        db.add(movement)

        # Check for low stock (after adding — should be fine, but covers threshold edge cases)
        # Low stock check on product current stock
        new_stock = current_stock
        if new_stock <= product.min_stock_threshold and product.min_stock_threshold > 0:
            # Still low even after purchase? Notify
            pass

    # Record payment if any amount was paid
    if amount_paid > 0:
        payment = SupplierPayment(
            supplier_id=supplier.id,
            purchase_id=purchase.id,
            payment_date=purchase_data.purchase_date,
            amount=amount_paid,
            payment_method="cash",
            recorded_by=actor_id,
        )
        db.add(payment)

    # Audit log
    log_audit(
        db, shop_id, actor_id, "POST_PURCHASE", "purchase", purchase.id,
        after_data={"purchase_ref": purchase_ref, "total_amount": total_amount}
    )

    db.commit()
    db.refresh(purchase)
    return purchase


# ───────────────────────── SALE SERVICE ─────────────────────────────

def complete_sale(db: Session, sale_data: SaleCreate, shop_id: int, cashier_id: int) -> Sale:
    """
    Atomically creates a sale, allocates stock from batches (FEFO), creates stock movements, and records payment.
    """
    items_data = []
    subtotal = 0.0

    for item in sale_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.shop_id == shop_id,
            Product.is_active == True
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        unit_price = item.unit_price if item.unit_price is not None else product.selling_price
        gross = item.quantity * unit_price
        discount = gross * (item.discount_percent / 100)
        line_total = gross - discount
        subtotal += line_total

        # FEFO batch allocation: select batches by earliest expiry date first
        today = date.today()
        batches = db.query(ProductBatch).filter(
            ProductBatch.product_id == product.id,
            ProductBatch.available_quantity > 0,
            # Exclude expired batches by default
            or_(
                ProductBatch.expiry_date == None,
                ProductBatch.expiry_date >= today
            )
        ).order_by(
            ProductBatch.expiry_date.asc().nullslast(),
            ProductBatch.received_date.asc()
        ).all()

        # Check total available
        total_available = sum(b.available_quantity for b in batches)
        if total_available < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'. Available: {total_available}, Requested: {item.quantity}"
            )

        items_data.append((item, product, unit_price, line_total, batches))

    total_amount = subtotal - sale_data.discount_amount
    amount_received = sale_data.amount_received
    change_amount = max(0, amount_received - total_amount)
    payment_status = PaymentStatus.paid if amount_received >= total_amount else PaymentStatus.partial

    # Create sale record
    receipt_number = generate_ref("RCPT")
    sale = Sale(
        shop_id=shop_id,
        cashier_id=cashier_id,
        receipt_number=receipt_number,
        sale_date=sale_data.sale_date,
        status=SaleStatus.completed,
        payment_method=sale_data.payment_method,
        payment_reference=sale_data.payment_reference,
        payment_status=payment_status,
        subtotal=subtotal,
        discount_amount=sale_data.discount_amount,
        total_amount=total_amount,
        amount_received=amount_received,
        change_amount=change_amount,
        customer_name=sale_data.customer_name,
        notes=sale_data.notes,
    )
    db.add(sale)
    db.flush()

    # Allocate batches and create stock movements
    for item, product, unit_price, line_total, batches in items_data:
        remaining_qty = item.quantity
        used_batch = None
        for batch in batches:
            if remaining_qty <= 0:
                break
            deduct = min(batch.available_quantity, remaining_qty)
            before_qty = batch.available_quantity
            batch.available_quantity -= deduct
            remaining_qty -= deduct
            used_batch = batch

            # Stock movement
            movement = StockMovement(
                shop_id=shop_id,
                product_id=product.id,
                batch_id=batch.id,
                movement_type=MovementType.sale,
                quantity_change=-deduct,
                quantity_before=before_qty,
                quantity_after=batch.available_quantity,
                reference_type="sale",
                reference_id=sale.id,
                actor_id=cashier_id,
                reason=f"Sale: {receipt_number}",
            )
            db.add(movement)

        # Create sale item (linked to the primary batch used)
        s_item = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            batch_id=used_batch.id if used_batch else None,
            quantity=item.quantity,
            unit_price=unit_price,
            unit_cost_snapshot=used_batch.unit_cost if used_batch else 0.0,
            discount_percent=item.discount_percent,
            line_total=line_total,
        )
        db.add(s_item)

        # Check if product is now low stock
        new_total = db.query(func.sum(ProductBatch.available_quantity)).filter(
            ProductBatch.product_id == product.id,
            ProductBatch.available_quantity > 0
        ).scalar() or 0.0

        if product.min_stock_threshold > 0 and new_total <= product.min_stock_threshold:
            create_notification(
                db, shop_id, NotificationType.low_stock,
                f"Low Stock: {product.name}",
                f"Stock for '{product.name}' is now {new_total} {product.unit}, below threshold of {product.min_stock_threshold}.",
                "product", product.id
            )

    # Audit log
    log_audit(
        db, shop_id, cashier_id, "COMPLETE_SALE", "sale", sale.id,
        after_data={"receipt_number": receipt_number, "total_amount": total_amount}
    )

    db.commit()
    db.refresh(sale)
    return sale


# ───────────────────────── DAMAGE SERVICE ────────────────────────────

def record_damage(db: Session, damage_data: DamagedGoodsCreate, shop_id: int, actor_id: int) -> DamagedGoods:
    """
    Atomically records damage and deducts from the batch/product stock.
    """
    product = db.query(Product).filter(
        Product.id == damage_data.product_id,
        Product.shop_id == shop_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    batch = None
    unit_cost = product.default_purchase_price

    if damage_data.batch_id:
        batch = db.query(ProductBatch).filter(
            ProductBatch.id == damage_data.batch_id,
            ProductBatch.product_id == product.id
        ).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        if batch.available_quantity < damage_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient batch stock. Available: {batch.available_quantity}"
            )
        unit_cost = batch.unit_cost
        before_qty = batch.available_quantity
        batch.available_quantity -= damage_data.quantity
    else:
        # Find any batch with sufficient quantity
        available_batches = db.query(ProductBatch).filter(
            ProductBatch.product_id == product.id,
            ProductBatch.available_quantity > 0
        ).order_by(ProductBatch.received_date.asc()).all()
        total_available = sum(b.available_quantity for b in available_batches)
        if total_available < damage_data.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for damage record")
        # Deduct from first available
        remaining = damage_data.quantity
        for b in available_batches:
            if remaining <= 0:
                break
            deduct = min(b.available_quantity, remaining)
            before_qty = b.available_quantity
            b.available_quantity -= deduct
            remaining -= deduct
            if batch is None:
                batch = b
                unit_cost = b.unit_cost

    estimated_value = damage_data.quantity * unit_cost

    damage = DamagedGoods(
        shop_id=shop_id,
        product_id=product.id,
        batch_id=batch.id if batch else None,
        damage_date=damage_data.damage_date,
        quantity=damage_data.quantity,
        unit_cost=unit_cost,
        estimated_value=estimated_value,
        reason=damage_data.reason,
        notes=damage_data.notes,
        status=DamageStatus.recorded,
        reporter_id=actor_id,
    )
    db.add(damage)
    db.flush()

    # Stock movement
    current_qty = db.query(func.sum(ProductBatch.available_quantity)).filter(
        ProductBatch.product_id == product.id,
        ProductBatch.available_quantity > 0
    ).scalar() or 0.0

    movement = StockMovement(
        shop_id=shop_id,
        product_id=product.id,
        batch_id=batch.id if batch else None,
        movement_type=MovementType.damage_write_off,
        quantity_change=-damage_data.quantity,
        quantity_before=current_qty + damage_data.quantity,
        quantity_after=current_qty,
        reference_type="damage",
        reference_id=damage.id,
        actor_id=actor_id,
        reason=damage_data.reason or "Damage write-off",
    )
    db.add(movement)

    create_notification(
        db, shop_id, NotificationType.damage_alert,
        f"Damage Recorded: {product.name}",
        f"{damage_data.quantity} {product.unit} of '{product.name}' recorded as damaged. Value: ₹{estimated_value:.2f}",
        "damaged_goods", damage.id
    )

    log_audit(db, shop_id, actor_id, "RECORD_DAMAGE", "damaged_goods", damage.id,
              after_data={"product_id": product.id, "quantity": damage_data.quantity, "value": estimated_value})

    db.commit()
    db.refresh(damage)
    return damage


# ───────────────────────── STOCK ADJUSTMENT ──────────────────────────

def adjust_stock(db: Session, adjustment: StockAdjustmentCreate, shop_id: int, actor_id: int) -> StockMovement:
    """
    Applies a stock adjustment with a reason. Requires authorization at the API level.
    """
    product = db.query(Product).filter(
        Product.id == adjustment.product_id, Product.shop_id == shop_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    current_qty = db.query(func.sum(ProductBatch.available_quantity)).filter(
        ProductBatch.product_id == product.id,
        ProductBatch.available_quantity > 0
    ).scalar() or 0.0

    new_qty = current_qty + adjustment.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Adjustment would result in negative stock")

    batch = None
    if adjustment.batch_id:
        batch = db.query(ProductBatch).filter(ProductBatch.id == adjustment.batch_id).first()
        if batch:
            batch.available_quantity = max(0, batch.available_quantity + adjustment.quantity_change)
    else:
        # Apply to the oldest batch if deducting, or create an adjustment batch if adding
        if adjustment.quantity_change > 0:
            adj_batch = ProductBatch(
                product_id=product.id,
                batch_number=generate_ref("ADJ", 6),
                received_date=date.today(),
                unit_cost=product.default_purchase_price,
                original_quantity=adjustment.quantity_change,
                available_quantity=adjustment.quantity_change,
            )
            db.add(adj_batch)
            db.flush()
            batch = adj_batch
        else:
            # Deduct from oldest batch
            oldest_batches = db.query(ProductBatch).filter(
                ProductBatch.product_id == product.id,
                ProductBatch.available_quantity > 0
            ).order_by(ProductBatch.received_date.asc()).all()
            remaining = abs(adjustment.quantity_change)
            for b in oldest_batches:
                if remaining <= 0:
                    break
                deduct = min(b.available_quantity, remaining)
                b.available_quantity -= deduct
                remaining -= deduct
                if batch is None:
                    batch = b

    movement = StockMovement(
        shop_id=shop_id,
        product_id=product.id,
        batch_id=batch.id if batch else None,
        movement_type=MovementType.stock_adjustment,
        quantity_change=adjustment.quantity_change,
        quantity_before=current_qty,
        quantity_after=new_qty,
        reference_type="adjustment",
        reference_id=None,
        actor_id=actor_id,
        reason=adjustment.reason,
    )
    db.add(movement)
    log_audit(db, shop_id, actor_id, "STOCK_ADJUSTMENT", "product", product.id,
              before_data={"stock": current_qty}, after_data={"stock": new_qty, "reason": adjustment.reason})

    db.commit()
    db.refresh(movement)
    return movement


# ───────────────────────── SUPPLIER PAYMENT SERVICE ────────────────────

def record_supplier_payment(db: Session, payment_data: SupplierPaymentCreate, shop_id: int, actor_id: int) -> SupplierPayment:
    supplier = db.query(Supplier).filter(
        Supplier.id == payment_data.supplier_id, Supplier.shop_id == shop_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    payment = SupplierPayment(
        supplier_id=supplier.id,
        purchase_id=payment_data.purchase_id,
        payment_date=payment_data.payment_date,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        reference=payment_data.reference,
        notes=payment_data.notes,
        recorded_by=actor_id,
    )
    db.add(payment)

    # Update purchase outstanding balance if linked to a specific purchase
    if payment_data.purchase_id:
        purchase = db.query(Purchase).filter(
            Purchase.id == payment_data.purchase_id,
            Purchase.shop_id == shop_id
        ).first()
        if purchase:
            purchase.amount_paid += payment_data.amount
            purchase.outstanding_balance = max(0, purchase.total_amount - purchase.amount_paid)
            if purchase.outstanding_balance <= 0:
                purchase.payment_status = PaymentStatus.paid
            elif purchase.amount_paid > 0:
                purchase.payment_status = PaymentStatus.partial

    log_audit(db, shop_id, actor_id, "RECORD_PAYMENT", "supplier_payment", None,
              after_data={"supplier_id": supplier.id, "amount": payment_data.amount})

    db.commit()
    db.refresh(payment)
    return payment


# ───────────────────────── DASHBOARD SERVICE ───────────────────────────

def get_dashboard_stats(db: Session, shop_id: int) -> dict:
    today = date.today()

    # Product counts
    total_products = db.query(func.count(Product.id)).filter(Product.shop_id == shop_id).scalar()
    active_products = db.query(func.count(Product.id)).filter(
        Product.shop_id == shop_id, Product.is_active == True
    ).scalar()

    # Today's sales
    today_sales = db.query(
        func.count(Sale.id), func.sum(Sale.total_amount)
    ).filter(
        Sale.shop_id == shop_id,
        Sale.sale_date == today,
        Sale.status == SaleStatus.completed
    ).first()
    today_sales_count = today_sales[0] or 0
    today_sales_amount = today_sales[1] or 0.0

    # Today's purchases
    today_purchases_amount = db.query(func.sum(Purchase.total_amount)).filter(
        Purchase.shop_id == shop_id,
        Purchase.purchase_date == today,
        Purchase.status == PurchaseStatus.posted
    ).scalar() or 0.0

    # Stock value (sum of batch available_qty * unit_cost)
    stock_value_result = db.query(
        func.sum(ProductBatch.available_quantity * ProductBatch.unit_cost)
    ).join(Product).filter(
        Product.shop_id == shop_id,
        ProductBatch.available_quantity > 0
    ).scalar()
    current_stock_value = stock_value_result or 0.0

    # Low stock count
    products = db.query(Product).filter(
        Product.shop_id == shop_id, Product.is_active == True, Product.min_stock_threshold > 0
    ).all()
    low_stock_count = 0
    for p in products:
        total_qty = sum(b.available_quantity for b in p.batches if b.available_quantity > 0)
        if total_qty <= p.min_stock_threshold:
            low_stock_count += 1

    # Expiry counts
    expiring_soon_count = 0
    expired_stock_count = 0
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    warning_days = shop.expiry_warning_days if shop else 30
    urgent_days = shop.expiry_urgent_days if shop else 7

    batches = db.query(ProductBatch).join(Product).filter(
        Product.shop_id == shop_id,
        ProductBatch.available_quantity > 0,
        ProductBatch.expiry_date != None
    ).all()
    for b in batches:
        status = get_batch_expiry_status(b.expiry_date, warning_days, urgent_days)
        if status == ExpiryStatus.expired:
            expired_stock_count += 1
        elif status in (ExpiryStatus.expiring_soon, ExpiryStatus.urgent):
            expiring_soon_count += 1

    # Damaged goods count (unresolved)
    damaged_stock_count = db.query(func.count(DamagedGoods.id)).filter(
        DamagedGoods.shop_id == shop_id,
        DamagedGoods.status.in_([DamageStatus.recorded, DamageStatus.supplier_claim_pending])
    ).scalar() or 0

    # Supplier outstanding
    supplier_outstanding = db.query(func.sum(Purchase.outstanding_balance)).filter(
        Purchase.shop_id == shop_id,
        Purchase.status == PurchaseStatus.posted,
        Purchase.outstanding_balance > 0
    ).scalar() or 0.0

    return {
        "total_products": total_products or 0,
        "total_active_products": active_products or 0,
        "today_sales_amount": today_sales_amount,
        "today_sales_count": today_sales_count,
        "today_purchases_amount": today_purchases_amount,
        "current_stock_value": current_stock_value,
        "low_stock_count": low_stock_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_stock_count": expired_stock_count,
        "damaged_stock_count": damaged_stock_count,
        "supplier_outstanding": supplier_outstanding,
    }


def get_supplier_outstanding(db: Session, supplier_id: int, shop_id: int) -> float:
    result = db.query(func.sum(Purchase.outstanding_balance)).filter(
        Purchase.supplier_id == supplier_id,
        Purchase.shop_id == shop_id,
        Purchase.status == PurchaseStatus.posted,
    ).scalar()
    return result or 0.0


def generate_expiry_notifications(db: Session, shop_id: int):
    """Check all batches and generate expiry notifications."""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    warning_days = shop.expiry_warning_days if shop else 30
    urgent_days = shop.expiry_urgent_days if shop else 7

    batches = db.query(ProductBatch).join(Product).filter(
        Product.shop_id == shop_id,
        ProductBatch.available_quantity > 0,
        ProductBatch.expiry_date != None
    ).all()

    for b in batches:
        expiry_status = get_batch_expiry_status(b.expiry_date, warning_days, urgent_days)
        if expiry_status in (ExpiryStatus.expiring_soon, ExpiryStatus.urgent, ExpiryStatus.expired):
            days_remaining = (b.expiry_date - date.today()).days
            title = f"Expiry Alert: {b.product.name}"
            if expiry_status == ExpiryStatus.expired:
                msg = f"Batch {b.batch_number} of '{b.product.name}' has EXPIRED ({abs(days_remaining)} days ago). Qty: {b.available_quantity}"
            else:
                msg = f"Batch {b.batch_number} of '{b.product.name}' expires in {days_remaining} days. Qty: {b.available_quantity}"
            create_notification(
                db, shop_id, NotificationType.expiry_alert, title, msg, "batch", b.id
            )
    db.commit()
