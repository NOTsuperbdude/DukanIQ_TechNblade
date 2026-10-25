"""Products and Categories CRUD endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models import Product, Category, ProductBatch, UserRole
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse
)

router = APIRouter()


# ─────────────── CATEGORIES ──────────────────

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    return db.query(Category).filter(
        Category.shop_id == current_user.shop_id
    ).all()


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    cat = Category(shop_id=current_user.shop_id, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    cat = db.query(Category).filter(
        Category.id == category_id, Category.shop_id == current_user.shop_id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


# ─────────────── PRODUCTS ──────────────────

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    low_stock_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = db.query(Product).filter(Product.shop_id == current_user.shop_id)
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%")) |
            (Product.barcode.ilike(f"%{search}%"))
        )
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    products = query.all()

    result = []
    for p in products:
        current_stock = sum(b.available_quantity for b in p.batches if b.available_quantity > 0)
        if low_stock_only and (p.min_stock_threshold <= 0 or current_stock > p.min_stock_threshold):
            continue
        resp = ProductResponse.model_validate(p)
        resp.current_stock = current_stock
        result.append(resp)
    return result


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    product = Product(shop_id=current_user.shop_id, **data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    resp = ProductResponse.model_validate(product)
    resp.current_stock = 0.0
    return resp


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.shop_id == current_user.shop_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    current_stock = sum(b.available_quantity for b in product.batches if b.available_quantity > 0)
    resp = ProductResponse.model_validate(product)
    resp.current_stock = current_stock
    return resp


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.shop_id == current_user.shop_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    current_stock = sum(b.available_quantity for b in product.batches if b.available_quantity > 0)
    resp = ProductResponse.model_validate(product)
    resp.current_stock = current_stock
    return resp


@router.delete("/products/{product_id}", status_code=204)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.owner, UserRole.manager))
):
    """Deactivates a product (soft delete — preserves historical transaction records)."""
    product = db.query(Product).filter(
        Product.id == product_id, Product.shop_id == current_user.shop_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
