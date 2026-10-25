"""
DukanIQ — All SQLAlchemy ORM Models
Covers: Shop, User, Category, Product, Supplier, ProductBatch,
        Purchase, PurchaseItem, Sale, SaleItem, StockMovement,
        DamagedGoods, SupplierPayment, Return, Notification, AuditLog
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum, JSON, Date, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


# ─────────────────────────── ENUMS ──────────────────────────────

class UserRole(str, enum.Enum):
    owner = "owner"
    manager = "manager"
    cashier = "cashier"
    inventory_staff = "inventory_staff"


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    partial = "partial"
    unpaid = "unpaid"


class PurchaseStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"
    reversed = "reversed"


class SaleStatus(str, enum.Enum):
    draft = "draft"
    completed = "completed"
    returned = "returned"
    cancelled = "cancelled"


class MovementType(str, enum.Enum):
    purchase_receipt = "purchase_receipt"
    sale = "sale"
    customer_return = "customer_return"
    supplier_return = "supplier_return"
    damage_write_off = "damage_write_off"
    expiry_write_off = "expiry_write_off"
    stock_adjustment = "stock_adjustment"


class DamageStatus(str, enum.Enum):
    recorded = "recorded"
    supplier_claim_pending = "supplier_claim_pending"
    replacement_requested = "replacement_requested"
    replacement_received = "replacement_received"
    written_off = "written_off"
    resolved = "resolved"


class ExpiryStatus(str, enum.Enum):
    safe = "safe"
    expiring_soon = "expiring_soon"
    urgent = "urgent"
    expired = "expired"


class ReturnType(str, enum.Enum):
    customer_return = "customer_return"
    supplier_return = "supplier_return"


class NotificationType(str, enum.Enum):
    low_stock = "low_stock"
    expiry_alert = "expiry_alert"
    damage_alert = "damage_alert"
    purchase_alert = "purchase_alert"
    supplier_payment_due = "supplier_payment_due"


# ─────────────────────────── MODELS ─────────────────────────────

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    gstin = Column(String(20))
    currency = Column(String(10), default="INR")
    timezone = Column(String(50), default="Asia/Kolkata")
    receipt_header = Column(Text)
    low_stock_warning_days = Column(Integer, default=30)
    expiry_warning_days = Column(Integer, default=30)
    expiry_urgent_days = Column(Integer, default=7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="shop")
    categories = relationship("Category", back_populates="shop")
    products = relationship("Product", back_populates="shop")
    suppliers = relationship("Supplier", back_populates="shop")
    purchases = relationship("Purchase", back_populates="shop")
    sales = relationship("Sale", back_populates="shop")
    notifications = relationship("Notification", back_populates="shop")
    audit_logs = relationship("AuditLog", back_populates="shop")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.cashier, nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="users")
    sales = relationship("Sale", back_populates="cashier")
    audit_logs = relationship("AuditLog", back_populates="actor")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shop = relationship("Shop", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sku = Column(String(50), index=True)
    barcode = Column(String(100), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    unit = Column(String(30), default="piece")
    default_purchase_price = Column(Float, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    min_stock_threshold = Column(Float, default=0.0)
    track_expiry = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="products")
    category = relationship("Category", back_populates="products")
    batches = relationship("ProductBatch", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    damaged_goods = relationship("DamagedGoods", back_populates="product")

    @property
    def current_stock(self):
        return sum(b.available_quantity for b in self.batches if b.available_quantity > 0)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    business_name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    gstin = Column(String(20))
    notes = Column(Text)
    opening_balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")
    payments = relationship("SupplierPayment", back_populates="supplier")


class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    batch_number = Column(String(100))
    received_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    unit_cost = Column(Float, nullable=False, default=0.0)
    original_quantity = Column(Float, nullable=False)
    available_quantity = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="batches")
    supplier = relationship("Supplier")
    purchase_items = relationship("PurchaseItem", back_populates="batch")
    sale_items = relationship("SaleItem", back_populates="batch")
    stock_movements = relationship("StockMovement", back_populates="batch")
    damaged_goods = relationship("DamagedGoods", back_populates="batch")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    purchase_ref = Column(String(50), unique=True, index=True)
    supplier_invoice_number = Column(String(100))
    purchase_date = Column(Date, nullable=False)
    payment_due_date = Column(Date, nullable=True)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.draft)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    additional_charges = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    outstanding_balance = Column(Float, default=0.0)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    payments = relationship("SupplierPayment", back_populates="purchase")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True)
    batch_number = Column(String(100))
    expiry_date = Column(Date, nullable=True)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)
    tax_percent = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")
    batch = relationship("ProductBatch", back_populates="purchase_items")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receipt_number = Column(String(50), unique=True, index=True)
    sale_date = Column(Date, nullable=False)
    status = Column(Enum(SaleStatus), default=SaleStatus.draft)
    payment_method = Column(String(30), default="cash")  # cash, upi, card, other
    payment_reference = Column(String(100))
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    amount_received = Column(Float, default=0.0)
    change_amount = Column(Float, default=0.0)
    customer_name = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="sales")
    cashier = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost_snapshot = Column(Float, default=0.0)  # cost at time of sale for profit calc
    discount_percent = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    batch = relationship("ProductBatch", back_populates="sale_items")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity_change = Column(Float, nullable=False)  # positive = in, negative = out
    quantity_before = Column(Float, nullable=False)
    quantity_after = Column(Float, nullable=False)
    reference_type = Column(String(50))  # "purchase", "sale", "damage", etc.
    reference_id = Column(Integer)
    actor_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="stock_movements")
    batch = relationship("ProductBatch", back_populates="stock_movements")


class DamagedGoods(Base):
    __tablename__ = "damaged_goods"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True)
    damage_date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)
    estimated_value = Column(Float, default=0.0)
    reason = Column(Text)
    notes = Column(Text)
    status = Column(Enum(DamageStatus), default=DamageStatus.recorded)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="damaged_goods")
    batch = relationship("ProductBatch", back_populates="damaged_goods")


class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(30), default="cash")
    reference = Column(String(100))
    notes = Column(Text)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier", back_populates="payments")
    purchase = relationship("Purchase", back_populates="payments")


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    return_type = Column(Enum(ReturnType), nullable=False)
    original_sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    original_purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=True)
    return_date = Column(Date, nullable=False)
    reason = Column(Text)
    total_amount = Column(Float, default=0.0)
    processed_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("ReturnItem", back_populates="return_record", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    return_record = relationship("Return", back_populates="items")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String(50))
    related_entity_id = Column(Integer)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    shop = relationship("Shop", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    reason = Column(Text)
    before_data = Column(JSON)
    after_data = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shop = relationship("Shop", back_populates="audit_logs")
    actor = relationship("User", back_populates="audit_logs")
