"""
Gemini AI Endpoints for DukanIQ
Endpoints:
- POST /api/v1/gemini/chat — Interactive Retail Copilot Chat
- POST /api/v1/gemini/loss-intelligence — Store Loss & Risk Analysis
- POST /api/v1/gemini/categorize — Smart Product Categorization
- GET  /api/v1/gemini/status — Check Gemini integration status
- POST /api/v1/gemini/key — Configure/Save Gemini API key
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Product, ProductBatch, DamagedGoods, Sale, Supplier
from app.services import get_dashboard_stats
from app.services.gemini_service import (
    ask_gemini_copilot,
    analyze_loss_intelligence,
    categorize_sku,
    get_gemini_api_key,
    save_gemini_api_key,
)

router = APIRouter()


class GeminiChatRequest(BaseModel):
    prompt: str
    include_context: bool = True


class GeminiKeyRequest(BaseModel):
    api_key: str


class GeminiCategorizeRequest(BaseModel):
    name: str
    description: Optional[str] = ""


def _build_shop_context(db: Session, shop_id: int) -> Dict[str, Any]:
    stats = get_dashboard_stats(db, shop_id)
    
    # Get top 3 expiring products
    from datetime import date, timedelta
    today = date.today()
    expiring_batches = (
        db.query(ProductBatch)
        .join(Product)
        .filter(
            Product.shop_id == shop_id,
            ProductBatch.quantity_remaining > 0,
            ProductBatch.expiry_date != None,
            ProductBatch.expiry_date <= today + timedelta(days=7),
        )
        .limit(5)
        .all()
    )
    expiring_info = [
        f"{b.product.name} (Lot {b.batch_number}, Qty: {b.quantity_remaining}, Exp: {b.expiry_date})"
        for b in expiring_batches if b.product
    ]

    # Get low stock products
    low_stock_prods = (
        db.query(Product)
        .filter(
            Product.shop_id == shop_id,
            Product.current_stock <= Product.min_stock_level,
            Product.is_active == True,
        )
        .limit(5)
        .all()
    )
    low_stock_info = [f"{p.name} (Stock: {p.current_stock}, Min: {p.min_stock_level})" for p in low_stock_prods]

    return {
        "shop_name": "ShopIQ Main Store",
        "today_sales": stats.get("today_sales", 0),
        "stock_value": stats.get("stock_valuation", 0),
        "active_skus": stats.get("total_products", 0),
        "active_batches": stats.get("total_active_lots", 0),
        "expiring_items_count": stats.get("fefo_expiry_count", 0),
        "low_stock_count": stats.get("low_stock_count", 0),
        "damage_value": stats.get("damaged_loss_value", 0),
        "pending_payables": stats.get("vendor_payables", 0),
        "expiring_products": ", ".join(expiring_info) if expiring_info else "None within 7 days",
        "low_stock_products": ", ".join(low_stock_info) if low_stock_info else "None",
    }


@router.get("/status")
def gemini_status():
    """Check whether Gemini API is configured and operational."""
    key = get_gemini_api_key()
    has_key = bool(key and len(key) > 5)
    masked_key = f"{key[:6]}...{key[-4:]}" if has_key and len(key) > 10 else None
    return {
        "status": "ready" if has_key else "needs_key",
        "has_api_key": has_key,
        "masked_key": masked_key,
        "model": "gemini-2.5-flash",
        "features": [
            "retail_copilot_chat",
            "loss_intelligence_audit",
            "sku_auto_categorization",
            "fefo_promo_recommendations"
        ]
    }


@router.post("/key")
def configure_gemini_key(
    data: GeminiKeyRequest,
    current_user=Depends(get_current_active_user)
):
    """Save or update the Google Gemini API key."""
    if not data.api_key or len(data.api_key.strip()) < 10:
        raise HTTPException(status_code=400, detail="Invalid Gemini API key provided")
    
    success = save_gemini_api_key(data.api_key.strip())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save API key to server environment")
    
    return {
        "status": "success",
        "message": "Gemini API key saved successfully. Gemini 2.5 Flash is now active!",
        "has_api_key": True
    }


@router.post("/chat")
def gemini_chat(
    data: GeminiChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Chat with the DukanIQ Retail Copilot grounded on real shop data."""
    context = None
    if data.include_context:
        context = _build_shop_context(db, current_user.shop_id)
    
    result = ask_gemini_copilot(data.prompt, shop_context=context)
    return result


@router.post("/loss-intelligence")
def gemini_loss_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Trigger an AI Loss Intelligence & FEFO Risk audit."""
    context = _build_shop_context(db, current_user.shop_id)
    result = analyze_loss_intelligence(context)
    return result


@router.post("/categorize")
def gemini_categorize(
    data: GeminiCategorizeRequest,
    current_user=Depends(get_current_active_user)
):
    """Auto-categorize product name and suggest tags and GST slab."""
    result = categorize_sku(data.name, data.description)
    return result
