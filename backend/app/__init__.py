"""
DukanIQ Backend — FastAPI Application Entry Point

A comprehensive shop management system backend for small retailers.
Covers: Authentication, Products, Inventory, Purchases, Sales,
        Suppliers, Expiry, Damaged Goods, Reports, and Audit Logs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router

# Import all models to ensure they are registered with SQLAlchemy
import app.models  # noqa: F401

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=f"{settings.APP_NAME} — Shop Management System",
    description="""
## DukanIQ Backend API

A complete backend for small retail shop management.

### Modules
- **Authentication** — JWT-based login, role-based access (Owner, Manager, Cashier, Inventory Staff)
- **Products & Categories** — Product catalogue with search, barcode, expiry tracking
- **Inventory** — Batch-level stock tracking, FEFO, stock movements ledger
- **Purchases** — Supplier purchase entry with atomic batch receipt and stock update
- **Sales** — POS-style sale entry with FEFO batch allocation and receipt generation
- **Suppliers** — Supplier directory, ledger, and payment tracking
- **Damaged Goods** — Damage recording with stock write-off
- **Reports** — Sales, purchase, inventory, gross profit, damage reports
- **Dashboard** — KPI cards for today's sales, purchases, stock value, alerts
- **Notifications** — Low stock, expiry, damage, and supplier payment alerts
- **Audit Logs** — Traceable history of all sensitive operations
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "database": "connected"}
