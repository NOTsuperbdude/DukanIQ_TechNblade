"""Inventory, batches, stock movements, and stock adjustments endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import Product, ProductBatch, StockMovement, UserRole
from app.schemas import StockAdjustmentCreate, InventorySnapshotItem
from app.services import adjust_stock, get_batch_expiry_status

router = APIRouter()


@router.get("/inventory", response_model=List[InventorySnapshotItem])
def get_inventory_snapshot(
    category_id: Optional[int] = Query(None),
    low_stock_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns current stock snapshot for all products."""
    query = db.query(Product).filter(
        Product.shop_id == current_user.shop_id, Product.is_active == True
    )
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.all()
    result = []
    for p in products:
        current_stock = sum(b.available_quantity for b in p.batches if b.available_quantity > 0)
        stock_value = sum(
            b.available_quantity * b.unit_cost
            for b in p.batches if b.available_quantity > 0
        )
        is_low = p.min_stock_threshold > 0 and current_stock <= p.min_stock_threshold
        if low_stock_only and not is_low:
            continue
        result.append(InventorySnapshotItem(
            product_id=p.id,
            product_name=p.name,
            sku=p.sku,
            category=p.category.name if p.category else None,
            unit=p.unit,
            current_stock=current_stock,
            stock_value=stock_value,
            min_threshold=p.min_stock_threshold,
            is_low_stock=is_low,
        ))
    return result


@router.get("/inventory/batches")
def list_batches(
    product_id: Optional[int] = Query(None),
    include_empty: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Lists all batches with expiry status."""
    query = db.query(ProductBatch).join(Product).filter(Product.shop_id == current_user.shop_id)
    if product_id:
        query = query.filter(ProductBatch.product_id == product_id)
    if not include_empty:
        query = query.filter(ProductBatch.available_quantity > 0)

    batches = query.order_by(ProductBatch.expiry_date.asc().nullslast()).all()
    return [
        {
            "id": b.id,
            "product_id": b.product_id,
            "product_name": b.product.name,
            "batch_number": b.batch_number,
            "received_date": b.received_date,
            "expiry_date": b.expiry_date,
            "unit_cost": b.unit_cost,
            "available_quantity": b.available_quantity,
            "expiry_status": get_batch_expiry_status(b.expiry_date).value,
        }
        for b in batches
    ]


@router.get("/inventory/stock-movements")
def list_stock_movements(
    product_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns stock movement ledger."""
    query = db.query(StockMovement).filter(StockMovement.shop_id == current_user.shop_id)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    if start_date:
        query = query.filter(func.date(StockMovement.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(StockMovement.created_at) <= end_date)

    movements = query.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name if m.product else None,
            "batch_id": m.batch_id,
            "movement_type": m.movement_type,
            "quantity_change": m.quantity_change,
            "quantity_before": m.quantity_before,
            "quantity_after": m.quantity_after,
            "reference_type": m.reference_type,
            "reference_id": m.reference_id,
            "reason": m.reason,
            "created_at": m.created_at,
        }
        for m in movements
    ]


@router.post("/inventory/adjustments", status_code=201)
def create_stock_adjustment(
    data: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager, UserRole.inventory_staff))
):
    """Apply a stock adjustment (requires reason). Creates a traceable stock movement."""
    movement = adjust_stock(db, data, current_user.shop_id, current_user.id)
    return {
        "message": "Stock adjustment applied successfully",
        "movement_id": movement.id,
        "quantity_change": movement.quantity_change,
        "quantity_after": movement.quantity_after,
    }


@router.get("/inventory/expiry")
def get_expiry_list(
    status: Optional[str] = Query(None, description="safe|expiring_soon|urgent|expired"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns all batches with expiry date information and current status."""
    batches = db.query(ProductBatch).join(Product).filter(
        Product.shop_id == current_user.shop_id,
        ProductBatch.available_quantity > 0,
        ProductBatch.expiry_date != None
    ).order_by(ProductBatch.expiry_date.asc()).all()

    today = date.today()
    result = []
    for b in batches:
        expiry_status = get_batch_expiry_status(b.expiry_date)
        if status and expiry_status.value != status:
            continue
        days_remaining = (b.expiry_date - today).days
        result.append({
            "batch_id": b.id,
            "product_id": b.product_id,
            "product_name": b.product.name,
            "batch_number": b.batch_number,
            "expiry_date": b.expiry_date,
            "days_remaining": days_remaining,
            "available_quantity": b.available_quantity,
            "unit_cost": b.unit_cost,
            "estimated_value": b.available_quantity * b.unit_cost,
            "expiry_status": expiry_status.value,
        })
    return result
