# -*- coding: utf-8 -*-
"""
DukanIQ — Seed Script
Creates a demo shop, owner, categories, suppliers, products, a sample purchase, and a sample sale.
Run with: py seed.py
"""

import sys
import os

# Make sure the backend directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
import app.models  # noqa — register all models
from app.models import (
    Shop, User, Category, Product, Supplier, UserRole
)
from app.core.security import get_password_hash
from app.schemas import (
    PurchaseCreate, PurchaseItemCreate, SaleCreate, SaleItemCreate
)
from app.services import post_purchase, complete_sale

# Create tables
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        # ── Shop & Owner ──────────────────────────────────────────────────
        existing = db.query(User).filter(User.email == "owner@dukaniq.com").first()
        if existing:
            print("Seed data already exists. Skipping.")
            return

        shop = Shop(
            name="Mehul's General Store",
            address="123 Market Road, Indore, MP",
            phone="+91 98765 43210",
            currency="INR",
            timezone="Asia/Kolkata",
            low_stock_warning_days=30,
            expiry_warning_days=30,
            expiry_urgent_days=7,
        )
        db.add(shop)
        db.flush()

        owner = User(
            shop_id=shop.id,
            name="Mehul Sharma",
            email="owner@dukaniq.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.owner,
            phone="+91 98765 43210",
        )
        manager = User(
            shop_id=shop.id,
            name="Priya Singh",
            email="manager@dukaniq.com",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.manager,
        )
        cashier = User(
            shop_id=shop.id,
            name="Raju Cashier",
            email="cashier@dukaniq.com",
            hashed_password=get_password_hash("cashier123"),
            role=UserRole.cashier,
        )
        db.add_all([owner, manager, cashier])
        db.flush()

        # ── Categories ───────────────────────────────────────────────────
        categories = [
            Category(shop_id=shop.id, name="Packaged Food"),
            Category(shop_id=shop.id, name="Beverages"),
            Category(shop_id=shop.id, name="Snacks"),
            Category(shop_id=shop.id, name="Dairy"),
            Category(shop_id=shop.id, name="Household"),
        ]
        db.add_all(categories)
        db.flush()
        cat_food = categories[0]
        cat_bev = categories[1]
        cat_snacks = categories[2]
        cat_dairy = categories[3]

        # ── Suppliers ─────────────────────────────────────────────────────
        supplier1 = Supplier(
            shop_id=shop.id,
            business_name="ABC Distributors",
            contact_person="Rahul Verma",
            phone="+91 94444 11111",
            address="Indore, MP",
            opening_balance=0.0,
        )
        supplier2 = Supplier(
            shop_id=shop.id,
            business_name="PQR Wholesale",
            contact_person="Sunita Patel",
            phone="+91 94444 22222",
            address="Bhopal, MP",
            opening_balance=500.0,
        )
        db.add_all([supplier1, supplier2])
        db.flush()

        # ── Products ─────────────────────────────────────────────────────
        products = [
            Product(shop_id=shop.id, category_id=cat_food.id, name="Parle-G Biscuits",
                    sku="PRD001", default_purchase_price=8.0, selling_price=10.0,
                    unit="packet", min_stock_threshold=20, track_expiry=True),
            Product(shop_id=shop.id, category_id=cat_snacks.id, name="Lay's Chips",
                    sku="PRD002", default_purchase_price=10.0, selling_price=20.0,
                    unit="packet", min_stock_threshold=15, track_expiry=True),
            Product(shop_id=shop.id, category_id=cat_bev.id, name="Thums Up 500ml",
                    sku="PRD003", default_purchase_price=20.0, selling_price=40.0,
                    unit="bottle", min_stock_threshold=10, track_expiry=True),
            Product(shop_id=shop.id, category_id=cat_dairy.id, name="Amul Butter 100g",
                    sku="PRD004", default_purchase_price=48.0, selling_price=60.0,
                    unit="pack", min_stock_threshold=5, track_expiry=True),
            Product(shop_id=shop.id, category_id=cat_food.id, name="Maggi Noodles",
                    sku="PRD005", default_purchase_price=12.0, selling_price=15.0,
                    unit="packet", min_stock_threshold=20, track_expiry=True),
        ]
        db.add_all(products)
        db.flush()
        db.commit()

        # ── Sample Purchase ───────────────────────────────────────────────
        purchase_data = PurchaseCreate(
            supplier_id=supplier1.id,
            supplier_invoice_number="INV-2026-001",
            purchase_date=date.today(),
            payment_due_date=date.today() + timedelta(days=30),
            amount_paid=1000.0,
            notes="Initial stock purchase",
            items=[
                PurchaseItemCreate(product_id=products[0].id, quantity=100, unit_cost=8.0,
                                   batch_number="BATCH-001",
                                   expiry_date=date.today() + timedelta(days=180)),
                PurchaseItemCreate(product_id=products[1].id, quantity=50, unit_cost=10.0,
                                   batch_number="BATCH-002",
                                   expiry_date=date.today() + timedelta(days=120)),
                PurchaseItemCreate(product_id=products[2].id, quantity=30, unit_cost=20.0,
                                   batch_number="BATCH-003",
                                   expiry_date=date.today() + timedelta(days=90)),
                PurchaseItemCreate(product_id=products[3].id, quantity=20, unit_cost=48.0,
                                   batch_number="BATCH-004",
                                   expiry_date=date.today() + timedelta(days=20)),  # expiring soon!
                PurchaseItemCreate(product_id=products[4].id, quantity=60, unit_cost=12.0,
                                   batch_number="BATCH-005",
                                   expiry_date=date.today() + timedelta(days=365)),
            ]
        )
        purchase = post_purchase(db, purchase_data, shop.id, owner.id)
        print(f"[OK] Purchase created: {purchase.purchase_ref} | Total: INR {purchase.total_amount:.2f}")

        # Sample Sale
        sale_data = SaleCreate(
            sale_date=date.today(),
            payment_method="cash",
            amount_received=150.0,
            customer_name="Walk-in Customer",
            items=[
                SaleItemCreate(product_id=products[0].id, quantity=2),
                SaleItemCreate(product_id=products[1].id, quantity=3),
                SaleItemCreate(product_id=products[2].id, quantity=1),
            ]
        )
        sale = complete_sale(db, sale_data, shop.id, cashier.id)
        print(f"[OK] Sale created: {sale.receipt_number} | Total: INR {sale.total_amount:.2f}")

        print("\n" + "="*50)
        print("[SUCCESS] Seed data created successfully!")
        print("="*50)
        print(f"Shop:    {shop.name}")
        print(f"Owner:   owner@dukaniq.com / admin123")
        print(f"Manager: manager@dukaniq.com / manager123")
        print(f"Cashier: cashier@dukaniq.com / cashier123")
        print(f"API:     http://localhost:8000/docs")
        print("="*50)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
