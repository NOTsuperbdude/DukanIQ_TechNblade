"""
DukanIQ — Pydantic Schemas for Request/Response validation
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import date, datetime
from app.models import (
    UserRole, PaymentStatus, PurchaseStatus, SaleStatus,
    MovementType, DamageStatus, ReturnType, NotificationType
)


# ────────────────────────── SHOP ────────────────────────────────

class ShopCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None
    receipt_header: Optional[str] = None
    low_stock_warning_days: Optional[int] = None
    expiry_warning_days: Optional[int] = None
    expiry_urgent_days: Optional[int] = None


class ShopResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    currency: str
    timezone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── AUTH / USER ──────────────────────────

class UserRegisterRequest(BaseModel):
    shop_name: str
    name: str
    email: str
    password: str
    phone: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole = UserRole.cashier
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    shop_id: int
    name: str
    email: str
    role: UserRole
    phone: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str  # email
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ────────────────────────── CATEGORY ──────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    shop_id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ────────────────────────── PRODUCT ──────────────────────────────

class ProductCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    unit: str = "piece"
    default_purchase_price: float = 0.0
    selling_price: float
    min_stock_threshold: float = 0.0
    track_expiry: bool = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    default_purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    min_stock_threshold: Optional[float] = None
    track_expiry: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    shop_id: int
    category_id: Optional[int]
    name: str
    sku: Optional[str]
    barcode: Optional[str]
    unit: str
    default_purchase_price: float
    selling_price: float
    min_stock_threshold: float
    track_expiry: bool
    is_active: bool
    current_stock: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── SUPPLIER ──────────────────────────────

class SupplierCreate(BaseModel):
    business_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    notes: Optional[str] = None
    opening_balance: float = 0.0


class SupplierUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    id: int
    shop_id: int
    business_name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    gstin: Optional[str]
    opening_balance: float
    is_active: bool
    outstanding_balance: float = 0.0

    class Config:
        from_attributes = True


# ────────────────────────── PURCHASE ──────────────────────────────

class PurchaseItemCreate(BaseModel):
    product_id: int
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    quantity: float
    unit_cost: float
    discount_percent: float = 0.0
    tax_percent: float = 0.0


class PurchaseCreate(BaseModel):
    supplier_id: int
    supplier_invoice_number: Optional[str] = None
    purchase_date: date
    payment_due_date: Optional[date] = None
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    additional_charges: float = 0.0
    amount_paid: float = 0.0
    notes: Optional[str] = None
    items: List[PurchaseItemCreate]


class PurchaseItemResponse(BaseModel):
    id: int
    product_id: int
    batch_number: Optional[str]
    expiry_date: Optional[date]
    quantity: float
    unit_cost: float
    discount_percent: float
    tax_percent: float
    line_total: float

    class Config:
        from_attributes = True


class PurchaseResponse(BaseModel):
    id: int
    shop_id: int
    supplier_id: int
    purchase_ref: str
    supplier_invoice_number: Optional[str]
    purchase_date: date
    status: PurchaseStatus
    payment_status: PaymentStatus
    subtotal: float
    discount_amount: float
    tax_amount: float
    additional_charges: float
    total_amount: float
    amount_paid: float
    outstanding_balance: float
    notes: Optional[str]
    items: List[PurchaseItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── SALE ──────────────────────────────────

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: Optional[float] = None  # if None, use product selling_price
    discount_percent: float = 0.0


class SaleCreate(BaseModel):
    sale_date: date
    payment_method: str = "cash"
    payment_reference: Optional[str] = None
    discount_amount: float = 0.0
    amount_received: float = 0.0
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    items: List[SaleItemCreate]


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    batch_id: Optional[int]
    quantity: float
    unit_price: float
    unit_cost_snapshot: float
    discount_percent: float
    line_total: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    shop_id: int
    cashier_id: int
    receipt_number: str
    sale_date: date
    status: SaleStatus
    payment_method: str
    payment_status: PaymentStatus
    subtotal: float
    discount_amount: float
    total_amount: float
    amount_received: float
    change_amount: float
    customer_name: Optional[str]
    items: List[SaleItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── DAMAGED GOODS ─────────────────────────

class DamagedGoodsCreate(BaseModel):
    product_id: int
    batch_id: Optional[int] = None
    damage_date: date
    quantity: float
    reason: Optional[str] = None
    notes: Optional[str] = None


class DamagedGoodsUpdate(BaseModel):
    status: Optional[DamageStatus] = None
    notes: Optional[str] = None


class DamagedGoodsResponse(BaseModel):
    id: int
    shop_id: int
    product_id: int
    batch_id: Optional[int]
    damage_date: date
    quantity: float
    unit_cost: float
    estimated_value: float
    reason: Optional[str]
    status: DamageStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── SUPPLIER PAYMENT ──────────────────────

class SupplierPaymentCreate(BaseModel):
    supplier_id: int
    purchase_id: Optional[int] = None
    payment_date: date
    amount: float
    payment_method: str = "cash"
    reference: Optional[str] = None
    notes: Optional[str] = None


class SupplierPaymentResponse(BaseModel):
    id: int
    supplier_id: int
    purchase_id: Optional[int]
    payment_date: date
    amount: float
    payment_method: str
    reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── STOCK ADJUSTMENT ──────────────────────

class StockAdjustmentCreate(BaseModel):
    product_id: int
    batch_id: Optional[int] = None
    quantity_change: float  # positive or negative
    reason: str


# ────────────────────────── NOTIFICATION ──────────────────────────

class NotificationResponse(BaseModel):
    id: int
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── REPORTS ──────────────────────────────

class DateRangeFilter(BaseModel):
    start_date: date
    end_date: date


class SalesReportResponse(BaseModel):
    start_date: date
    end_date: date
    total_sales: int
    gross_revenue: float
    total_discount: float
    net_revenue: float
    by_payment_method: dict


class InventorySnapshotItem(BaseModel):
    product_id: int
    product_name: str
    sku: Optional[str]
    category: Optional[str]
    unit: str
    current_stock: float
    stock_value: float
    min_threshold: float
    is_low_stock: bool


class DashboardResponse(BaseModel):
    total_products: int
    total_active_products: int
    today_sales_amount: float
    today_sales_count: int
    today_purchases_amount: float
    current_stock_value: float
    low_stock_count: int
    expiring_soon_count: int
    expired_stock_count: int
    damaged_stock_count: int
    supplier_outstanding: float
