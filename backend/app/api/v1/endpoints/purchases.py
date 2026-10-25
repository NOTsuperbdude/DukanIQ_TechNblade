"""Purchase management endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import Purchase, PurchaseStatus, PaymentStatus, UserRole
from app.schemas import PurchaseCreate, PurchaseResponse
from app.services import post_purchase

router = APIRouter()


@router.post("/purchases", response_model=PurchaseResponse, status_code=201)
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager, UserRole.inventory_staff))
):
    """
    Creates and immediately posts a purchase.
    This is atomic: purchase record + batch receipts + stock movements + supplier balance update.
    """
    return post_purchase(db, data, current_user.shop_id, current_user.id)


@router.get("/purchases", response_model=List[PurchaseResponse])
def list_purchases(
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(Purchase).filter(Purchase.shop_id == current_user.shop_id)
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    if status:
        query = query.filter(Purchase.status == status)
    if payment_status:
        query = query.filter(Purchase.payment_status == payment_status)
    if start_date:
        query = query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        query = query.filter(Purchase.purchase_date <= end_date)
    if search:
        query = query.filter(
            (Purchase.purchase_ref.ilike(f"%{search}%")) |
            (Purchase.supplier_invoice_number.ilike(f"%{search}%"))
        )
    return query.order_by(Purchase.purchase_date.desc()).offset(skip).limit(limit).all()


@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id, Purchase.shop_id == current_user.shop_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase
