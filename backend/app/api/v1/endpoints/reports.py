"""Reports and Analytics endpoints"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import (
    Sale, SaleItem, Purchase, PurchaseItem, Product, ProductBatch,
    DamagedGoods, Supplier, Notification, UserRole,
    SaleStatus, PurchaseStatus, DamageStatus
)
from app.schemas import DashboardResponse, SalesReportResponse
from app.services import get_dashboard_stats, generate_expiry_notifications

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns all dashboard KPI cards and summary stats."""
    stats = get_dashboard_stats(db, current_user.shop_id)
    return DashboardResponse(**stats)


@router.get("/reports/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    cashier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Sales summary report for a date range."""
    query = db.query(Sale).filter(
        Sale.shop_id == current_user.shop_id,
        Sale.status == SaleStatus.completed,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
    )
    if cashier_id:
        query = query.filter(Sale.cashier_id == cashier_id)

    sales = query.all()
    total_sales = len(sales)
    gross_revenue = sum(s.subtotal for s in sales)
    total_discount = sum(s.discount_amount for s in sales)
    net_revenue = sum(s.total_amount for s in sales)

    # Payment method breakdown
    by_method: dict = {}
    for s in sales:
        m = s.payment_method or "cash"
        by_method[m] = by_method.get(m, 0) + s.total_amount

    # Daily breakdown
    daily: dict = {}
    for s in sales:
        key = str(s.sale_date)
        if key not in daily:
            daily[key] = {"count": 0, "amount": 0.0}
        daily[key]["count"] += 1
        daily[key]["amount"] += s.total_amount

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": total_sales,
        "gross_revenue": gross_revenue,
        "total_discount": total_discount,
        "net_revenue": net_revenue,
        "by_payment_method": by_method,
        "daily_breakdown": daily,
    }


@router.get("/reports/purchases")
def purchases_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    supplier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Purchase summary report."""
    query = db.query(Purchase).filter(
        Purchase.shop_id == current_user.shop_id,
        Purchase.status == PurchaseStatus.posted,
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date,
    )
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    purchases = query.all()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_purchases": len(purchases),
        "total_invoiced": sum(p.total_amount for p in purchases),
        "total_paid": sum(p.amount_paid for p in purchases),
        "total_outstanding": sum(p.outstanding_balance for p in purchases),
        "purchases": [
            {
                "purchase_ref": p.purchase_ref,
                "supplier": p.supplier.business_name,
                "date": p.purchase_date,
                "total_amount": p.total_amount,
                "amount_paid": p.amount_paid,
                "outstanding": p.outstanding_balance,
                "payment_status": p.payment_status,
            }
            for p in purchases
        ],
    }


@router.get("/reports/inventory")
def inventory_report(
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Current inventory snapshot report."""
    query = db.query(Product).filter(
        Product.shop_id == current_user.shop_id, Product.is_active == True
    )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    products = query.all()

    items = []
    total_value = 0.0
    for p in products:
        current_stock = sum(b.available_quantity for b in p.batches if b.available_quantity > 0)
        stock_value = sum(b.available_quantity * b.unit_cost for b in p.batches if b.available_quantity > 0)
        total_value += stock_value
        items.append({
            "product_id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category.name if p.category else None,
            "current_stock": current_stock,
            "unit": p.unit,
            "stock_value": stock_value,
            "min_threshold": p.min_stock_threshold,
            "is_low_stock": p.min_stock_threshold > 0 and current_stock <= p.min_stock_threshold,
        })

    return {
        "total_products": len(items),
        "total_stock_value": total_value,
        "items": items,
    }


@router.get("/reports/gross-profit")
def gross_profit_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """
    Gross profit estimate: net sales revenue - cost of goods sold.
    Uses unit_cost_snapshot captured at the time of sale.
    """
    sale_items = db.query(SaleItem).join(Sale).filter(
        Sale.shop_id == current_user.shop_id,
        Sale.status == SaleStatus.completed,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
    ).all()

    revenue = sum(si.line_total for si in sale_items)
    cogs = sum(si.quantity * si.unit_cost_snapshot for si in sale_items)
    gross_profit = revenue - cogs
    margin_percent = (gross_profit / revenue * 100) if revenue > 0 else 0.0

    return {
        "start_date": start_date,
        "end_date": end_date,
        "revenue": revenue,
        "cost_of_goods_sold": cogs,
        "gross_profit": gross_profit,
        "gross_margin_percent": round(margin_percent, 2),
    }


@router.get("/reports/damage")
def damage_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    query = db.query(DamagedGoods).filter(
        DamagedGoods.shop_id == current_user.shop_id,
        DamagedGoods.damage_date >= start_date,
        DamagedGoods.damage_date <= end_date,
    )
    if product_id:
        query = query.filter(DamagedGoods.product_id == product_id)
    damages = query.all()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_records": len(damages),
        "total_estimated_value": sum(d.estimated_value for d in damages),
        "records": [
            {
                "product": d.product.name,
                "batch": d.batch.batch_number if d.batch else None,
                "date": d.damage_date,
                "quantity": d.quantity,
                "estimated_value": d.estimated_value,
                "reason": d.reason,
                "status": d.status,
            }
            for d in damages
        ],
    }


@router.get("/notifications")
def list_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(Notification).filter(Notification.shop_id == current_user.shop_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(100).all()


@router.post("/notifications/{notification_id}/read", status_code=200)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.shop_id == current_user.shop_id
    ).first()
    if notif:
        notif.is_read = True
        from datetime import datetime, timezone
        notif.read_at = datetime.now(timezone.utc)
        db.commit()
    return {"message": "Marked as read"}


@router.post("/notifications/generate-expiry", status_code=201)
def trigger_expiry_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Manually trigger expiry notification generation for all batches."""
    generate_expiry_notifications(db, current_user.shop_id)
    return {"message": "Expiry notifications generated"}


@router.get("/audit-logs")
def list_audit_logs(
    entity_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner))
):
    """Owner-only: view audit logs for the shop."""
    from app.models import AuditLog
    query = db.query(AuditLog).filter(AuditLog.shop_id == current_user.shop_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "actor": l.actor.name if l.actor else "system",
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "reason": l.reason,
            "before_data": l.before_data,
            "after_data": l.after_data,
            "created_at": l.created_at,
        }
        for l in logs
    ]
