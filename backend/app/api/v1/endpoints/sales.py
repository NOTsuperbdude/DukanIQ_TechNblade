"""Sales management endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import Sale, SaleStatus, UserRole
from app.schemas import SaleCreate, SaleResponse
from app.services import complete_sale

router = APIRouter()


@router.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager, UserRole.cashier))
):
    """
    Complete a sale atomically: sale record + FEFO batch allocation + stock movements + receipt number.
    Validates stock availability and blocks expired stock.
    """
    return complete_sale(db, data, current_user.shop_id, current_user.id)


@router.get("/sales", response_model=List[SaleResponse])
def list_sales(
    cashier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(Sale).filter(Sale.shop_id == current_user.shop_id)
    if cashier_id:
        query = query.filter(Sale.cashier_id == cashier_id)
    if status:
        query = query.filter(Sale.status == status)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if search:
        query = query.filter(
            (Sale.receipt_number.ilike(f"%{search}%")) |
            (Sale.customer_name.ilike(f"%{search}%"))
        )
    return query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()


@router.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    sale = db.query(Sale).filter(
        Sale.id == sale_id, Sale.shop_id == current_user.shop_id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.get("/sales/{sale_id}/receipt")
def get_receipt(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Returns receipt data for a completed sale."""
    sale = db.query(Sale).filter(
        Sale.id == sale_id, Sale.shop_id == current_user.shop_id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return {
        "receipt_number": sale.receipt_number,
        "sale_date": sale.sale_date,
        "cashier": sale.cashier.name if sale.cashier else "N/A",
        "customer_name": sale.customer_name,
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percent": item.discount_percent,
                "line_total": item.line_total,
            }
            for item in sale.items
        ],
        "subtotal": sale.subtotal,
        "discount_amount": sale.discount_amount,
        "total_amount": sale.total_amount,
        "amount_received": sale.amount_received,
        "change_amount": sale.change_amount,
        "payment_method": sale.payment_method,
    }
