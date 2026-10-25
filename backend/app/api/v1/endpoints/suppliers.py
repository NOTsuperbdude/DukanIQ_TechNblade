"""Supplier management endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import Supplier, Purchase, SupplierPayment, UserRole, PurchaseStatus
from app.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierPaymentCreate, SupplierPaymentResponse
)
from app.services import record_supplier_payment, get_supplier_outstanding

router = APIRouter()


@router.get("/suppliers", response_model=List[SupplierResponse])
def list_suppliers(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(Supplier).filter(Supplier.shop_id == current_user.shop_id)
    if search:
        query = query.filter(Supplier.business_name.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)
    suppliers = query.all()

    result = []
    for s in suppliers:
        outstanding = get_supplier_outstanding(db, s.id, current_user.shop_id)
        resp = SupplierResponse.model_validate(s)
        resp.outstanding_balance = outstanding
        result.append(resp)
    return result


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    supplier = Supplier(shop_id=current_user.shop_id, **data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    resp = SupplierResponse.model_validate(supplier)
    resp.outstanding_balance = 0.0
    return resp


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id, Supplier.shop_id == current_user.shop_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    outstanding = get_supplier_outstanding(db, supplier.id, current_user.shop_id)
    resp = SupplierResponse.model_validate(supplier)
    resp.outstanding_balance = outstanding
    return resp


@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id, Supplier.shop_id == current_user.shop_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    outstanding = get_supplier_outstanding(db, supplier.id, current_user.shop_id)
    resp = SupplierResponse.model_validate(supplier)
    resp.outstanding_balance = outstanding
    return resp


@router.get("/suppliers/{supplier_id}/ledger")
def supplier_ledger(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns the supplier's purchase and payment ledger."""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id, Supplier.shop_id == current_user.shop_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    purchases = db.query(Purchase).filter(
        Purchase.supplier_id == supplier_id,
        Purchase.shop_id == current_user.shop_id,
        Purchase.status == PurchaseStatus.posted
    ).order_by(Purchase.purchase_date.asc()).all()

    payments = db.query(SupplierPayment).filter(
        SupplierPayment.supplier_id == supplier_id
    ).order_by(SupplierPayment.payment_date.asc()).all()

    total_invoiced = sum(p.total_amount for p in purchases)
    total_paid = sum(p.amount for p in payments) + supplier.opening_balance
    outstanding = max(0, total_invoiced - total_paid)

    return {
        "supplier_id": supplier_id,
        "business_name": supplier.business_name,
        "opening_balance": supplier.opening_balance,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding_balance": outstanding,
        "purchases": [
            {
                "purchase_ref": p.purchase_ref,
                "date": p.purchase_date,
                "total_amount": p.total_amount,
                "amount_paid": p.amount_paid,
                "outstanding": p.outstanding_balance,
                "payment_status": p.payment_status,
            }
            for p in purchases
        ],
        "payments": [
            {
                "payment_date": p.payment_date,
                "amount": p.amount,
                "method": p.payment_method,
                "reference": p.reference,
            }
            for p in payments
        ],
    }


@router.post("/suppliers/payments", response_model=SupplierPaymentResponse, status_code=201)
def add_payment(
    data: SupplierPaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    return record_supplier_payment(db, data, current_user.shop_id, current_user.id)
