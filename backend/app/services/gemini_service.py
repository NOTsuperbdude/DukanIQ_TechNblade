"""
Gemini AI Service for DukanIQ
Integrates Google Gemini (via google-genai SDK) to provide:
1. Real-time Retail Copilot & Kirana Business Advisor
2. Loss Intelligence & Expiry Risk Analysis
3. SKU Auto-Categorization & Smart Tagging
"""

import os
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types
from app.core.config import settings


def get_gemini_api_key() -> Optional[str]:
    """Retrieve Gemini API key from settings or environment."""
    return os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)


def save_gemini_api_key(api_key: str) -> bool:
    """Save Gemini API key to .env file and environment."""
    os.environ["GEMINI_API_KEY"] = api_key
    settings.GEMINI_API_KEY = api_key
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    try:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={api_key}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"GEMINI_API_KEY={api_key}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Error saving to .env: {e}")
        return False


def get_gemini_client() -> Optional[genai.Client]:
    """Create a genai.Client instance if key is available."""
    api_key = get_gemini_api_key()
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None


def ask_gemini_copilot(
    prompt: str,
    shop_context: Optional[Dict[str, Any]] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Chat with the DukanIQ Gemini Copilot.
    Uses shop_context (sales, inventory, expiry, losses) to ground responses.
    """
    api_key = get_gemini_api_key()
    system_instruction = (
        "You are DukanIQ AI — an expert Kirana and Retail Business Intelligence Advisor "
        "designed specifically for Indian shopkeepers, supermarket owners, and small retailers. "
        "You understand Indian retail terminology (Kirana, Khata, Udhar, Mandi, Margins, FEFO, SKU). "
        "Give actionable, clear, concise, and highly practical advice. "
        "When store context is provided, reference actual numbers and products from their store. "
        "Format responses with neat markdown bullet points, bold highlights, and rupee symbol (₹)."
    )

    context_str = ""
    if shop_context:
        context_str = (
            f"\n\n[CURRENT STORE METRICS & DATA]:\n"
            f"- Shop Name: {shop_context.get('shop_name', 'My Store')}\n"
            f"- Today's Sales: ₹{shop_context.get('today_sales', 0):,.2f}\n"
            f"- Total Stock Value: ₹{shop_context.get('stock_value', 0):,.2f}\n"
            f"- Active SKUs: {shop_context.get('active_skus', 0)}\n"
            f"- Active Batches: {shop_context.get('active_batches', 0)}\n"
            f"- Items Near Expiry (FEFO): {shop_context.get('expiring_items_count', 0)}\n"
            f"- Low Stock Alerts: {shop_context.get('low_stock_count', 0)}\n"
            f"- Total Recorded Loss/Damages: ₹{shop_context.get('damage_value', 0):,.2f}\n"
            f"- Supplier Payables Pending: ₹{shop_context.get('pending_payables', 0):,.2f}\n"
        )
        if "expiring_products" in shop_context:
            context_str += f"- Urgent Expiry Items: {shop_context['expiring_products']}\n"
        if "low_stock_products" in shop_context:
            context_str += f"- Urgent Reorder SKUs: {shop_context['low_stock_products']}\n"

    full_prompt = f"{prompt}{context_str}"

    if not api_key:
        # Fallback offline simulation when API key is not yet set
        fallback_msg = (
            f"**[Gemini Offline Mode]**\n\n"
            f"To enable real-time Google Gemini intelligence, enter your **Gemini API Key** in "
            f"**Store Settings & Audit Logs > Gemini AI Configuration**.\n\n"
            f"### Quick Store Health Summary:\n"
            f"- **Today's Sales**: ₹{shop_context.get('today_sales', 18450):,.2f}\n"
            f"- **Immediate Action Required**: {shop_context.get('expiring_items_count', 7)} batches are reaching expiry within 7 days. "
            f"Apply a 20-30% clearance discount on the front shelf immediately.\n"
            f"- **Stock Refill**: {shop_context.get('low_stock_count', 9)} products are below reorder threshold. Generate purchase PO before stockouts occur.\n"
            f"- **Cash Flow Tip**: Clear the 2 nearest vendor invoices to maintain distributor goodwill and credit limits."
        )
        return {
            "reply": fallback_msg,
            "has_api_key": False,
            "model": "offline-rule-engine",
        }

    try:
        client = get_gemini_client()
        if not client:
            raise ValueError("Could not initialize Gemini client")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=config,
        )

        return {
            "reply": response.text,
            "has_api_key": True,
            "model": "gemini-2.5-flash",
        }
    except Exception as e:
        return {
            "reply": f"⚠️ Gemini AI encountered an error: {str(e)}.\nPlease verify your API key in Store Settings.",
            "has_api_key": True,
            "error": str(e),
            "model": "gemini-2.5-flash",
        }


def analyze_loss_intelligence(shop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run an in-depth Loss Intelligence analysis using Gemini.
    """
    prompt = (
        "Generate a comprehensive 'DukanIQ Loss Intelligence & Profit Maximization Audit' "
        "based on the following store telemetry. Identify:\n"
        "1. Critical Expiry & FEFO risks (suggest exact clearance % and timeline)\n"
        "2. Shrinkage & Damaged Goods reduction plan\n"
        "3. Fast Reorder and Dead Stock optimization\n"
        "4. Estimated monthly profit recovery if these 3 actions are taken."
    )
    return ask_gemini_copilot(prompt, shop_context=shop_data)


def categorize_sku(product_name: str, description: Optional[str] = "") -> Dict[str, Any]:
    """
    Use Gemini to automatically categorize a product, suggest tax slab, and storage conditions.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {
            "category": "General Grocery",
            "suggested_gst_percent": 5,
            "storage_type": "Ambient Shelf",
            "tags": ["groceries", "retail", "fmcg"],
            "has_api_key": False,
        }

    try:
        client = get_gemini_client()
        prompt = (
            f"Analyze this retail product:\n"
            f"Product Name: {product_name}\n"
            f"Description: {description or 'N/A'}\n\n"
            f"Return JSON strictly with fields:\n"
            f"- category (e.g. Dairy & Eggs, Staples & Grains, Snacks, Personal Care, Beverages, Spices & Masala)\n"
            f"- suggested_gst_percent (number: 0, 5, 12, or 18)\n"
            f"- storage_type (Ambient Shelf, Cold Storage, Frozen, Dry Dark)\n"
            f"- tags (list of 3-4 keywords)\n"
            f"- estimated_shelf_days (number of days typical shelf life)"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        import json
        data = json.loads(response.text)
        data["has_api_key"] = True
        return data
    except Exception as e:
        return {
            "category": "Packaged Goods",
            "suggested_gst_percent": 5,
            "storage_type": "Ambient Shelf",
            "tags": ["retail", "packaged"],
            "has_api_key": True,
            "error": str(e),
        }
