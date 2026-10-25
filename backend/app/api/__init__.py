"""Main API v1 router — assembles all endpoint routers"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, suppliers, purchases, sales, inventory, damaged_goods, reports, gemini

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(products.router, prefix="", tags=["Products & Categories"])
api_router.include_router(suppliers.router, prefix="", tags=["Suppliers"])
api_router.include_router(purchases.router, prefix="", tags=["Purchases"])
api_router.include_router(sales.router, prefix="", tags=["Sales"])
api_router.include_router(inventory.router, prefix="", tags=["Inventory"])
api_router.include_router(damaged_goods.router, prefix="", tags=["Damaged Goods"])
api_router.include_router(reports.router, prefix="", tags=["Reports & Dashboard"])
api_router.include_router(gemini.router, prefix="/gemini", tags=["Gemini AI Retail Intelligence"])

