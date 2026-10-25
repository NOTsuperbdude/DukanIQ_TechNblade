"""Damaged Goods endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import DamagedGoods, DamageStatus, UserRole
from app.schemas import DamagedGoodsCreate, DamagedGoodsUpdate, DamagedGoodsResponse
from app.services import record_damage

router = APIRouter()


@router.post("/damaged-goods", response_model=DamagedGoodsResponse, status_code=201)
def create_damage_record(
    data: DamagedGoodsCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager, UserRole.inventory_staff))
):
    """
    Record damaged goods. Atomically deducts from batch stock and creates stock movement.
    """
    return record_damage(db, data, current_user.shop_id, current_user.id)


@router.get("/damaged-goods", response_model=List[DamagedGoodsResponse])
def list_damage_records(
    product_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(DamagedGoods).filter(DamagedGoods.shop_id == current_user.shop_id)
    if product_id:
        query = query.filter(DamagedGoods.product_id == product_id)
    if status:
        query = query.filter(DamagedGoods.status == status)
    if start_date:
        query = query.filter(DamagedGoods.damage_date >= start_date)
    if end_date:
        query = query.filter(DamagedGoods.damage_date <= end_date)
    return query.order_by(DamagedGoods.damage_date.desc()).offset(skip).limit(limit).all()


@router.get("/damaged-goods/{damage_id}", response_model=DamagedGoodsResponse)
def get_damage_record(
    damage_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    damage = db.query(DamagedGoods).filter(
        DamagedGoods.id == damage_id, DamagedGoods.shop_id == current_user.shop_id
    ).first()
    if not damage:
        raise HTTPException(status_code=404, detail="Damage record not found")
    return damage


@router.patch("/damaged-goods/{damage_id}", response_model=DamagedGoodsResponse)
def update_damage_status(
    damage_id: int,
    data: DamagedGoodsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Update damage record status (e.g., mark as resolved, supplier_claim_pending, etc.)"""
    damage = db.query(DamagedGoods).filter(
        DamagedGoods.id == damage_id, DamagedGoods.shop_id == current_user.shop_id
    ).first()
    if not damage:
        raise HTTPException(status_code=404, detail="Damage record not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(damage, field, value)
    db.commit()
    db.refresh(damage)
    return damage
