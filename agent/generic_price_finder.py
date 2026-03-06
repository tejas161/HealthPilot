"""
Generic Alternative & Price Transparency Finder tool.
Detects active ingredient, suggests cheaper generics, shows price differences,
flags overpricing, and optionally links Jan Aushadhi. Information only — no recommendation to switch.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _load_json(filename: str) -> list | dict:
    """Load JSON from data/; return empty list if missing or invalid."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _find_entry(medicine_name: str, reference: list) -> dict | None:
    """Find a price-reference entry by brand name or active ingredient. Returns first match."""
    if not reference or not isinstance(reference, list):
        return None
    name_lower = medicine_name.strip().lower()
    if not name_lower:
        return None
    for entry in reference:
        if not isinstance(entry, dict):
            continue
        brands = entry.get("brand_names") or []
        active = (entry.get("active_ingredient") or "").strip().lower()
        if name_lower in active:
            return entry
        for b in brands:
            if name_lower in (b or "").lower():
                return entry
    return None


def find_generic_alternatives(
    medicine_name: str,
    user_price_inr: float | None = None,
) -> dict:
    """
    Find generic alternatives and price transparency for a medicine. India-focused.
    Detects active ingredient, suggests cheaper generics, shows price differences,
    flags overpricing (if user_price_inr is above ceiling or typical), and links Jan Aushadhi when available.
    Use this for information only — always direct user to discuss with doctor/pharmacist before switching.

    Args:
        medicine_name: Brand or generic name of the medicine (e.g. Crocin, Paracetamol, Dolo 650).
        user_price_inr: Optional. Price the user was quoted or paid (INR). If provided and above
                        ceiling/typical, overpricing_flagged will be set.

    Returns:
        dict: status, active_ingredient, generic_alternatives, price_comparison, overpricing_flagged,
              jan_aushadhi (link and info), disclaimer.
    """
    if not medicine_name or not medicine_name.strip():
        return {
            "status": "error",
            "error_message": "Please provide a medicine name (brand or generic).",
        }

    reference = _load_json("medicine_price_reference.json")
    if not isinstance(reference, list):
        reference = []
    entry = _find_entry(medicine_name, reference)
    if not entry:
        return {
            "status": "error",
            "error_message": (
                f"No price data found for '{medicine_name}'. "
                "We may not have this in our reference yet. You can ask your pharmacist for generic options."
            ),
        }

    active = entry.get("active_ingredient") or "—"
    alternatives = entry.get("generic_alternatives") or []
    ceiling = entry.get("ceiling_price_inr")
    jan = entry.get("jan_aushadhi")
    strength = entry.get("strength_common") or ""

    # Build price comparison and sort alternatives by price
    price_comparison = []
    for alt in alternatives:
        if not isinstance(alt, dict):
            continue
        name = alt.get("name") or "—"
        price = alt.get("typical_price_inr")
        if price is not None:
            price_comparison.append({"name": name, "typical_price_inr": price})
    price_comparison.sort(key=lambda x: x.get("typical_price_inr") or 0)

    overpricing_flagged = False
    overpricing_note = ""
    if user_price_inr is not None and user_price_inr > 0:
        if ceiling is not None and user_price_inr > ceiling:
            overpricing_flagged = True
            overpricing_note = (
                f"The price you mentioned (₹{user_price_inr}) is above the typical ceiling (₹{ceiling} INR). "
                "You may find cheaper options at generic pharmacies or Jan Aushadhi."
            )
        elif price_comparison and user_price_inr > (price_comparison[0].get("typical_price_inr") or 0) * 2:
            overpricing_flagged = True
            overpricing_note = (
                f"The price you mentioned (₹{user_price_inr}) is much higher than typical generic prices (around ₹{price_comparison[0].get('typical_price_inr')} INR). "
                "Consider asking for a generic or checking Jan Aushadhi."
            )

    jan_aushadhi_info = None
    if isinstance(jan, dict) and jan.get("available"):
        jan_aushadhi_info = {
            "available": True,
            "product_name": jan.get("product_name") or "—",
            "typical_price_inr": jan.get("typical_price_inr"),
            "portal_url": jan.get("portal_url") or "https://janaushadhi.gov.in/ProductList.aspx",
            "note": "Find your nearest Jan Aushadhi Kendra at janaushadhi.gov.in or call 1800-180-8080.",
        }
    else:
        jan_aushadhi_info = {"available": False, "note": "Check janaushadhi.gov.in for current product list."}

    return {
        "status": "success",
        "active_ingredient": active,
        "strength_common": strength,
        "generic_alternatives": price_comparison,
        "ceiling_price_inr": ceiling,
        "price_comparison_note": (
            "Prices are indicative (market/Jan Aushadhi). Actual prices may vary by pharmacy and location."
        ),
        "overpricing_flagged": overpricing_flagged,
        "overpricing_note": overpricing_note if overpricing_flagged else None,
        "jan_aushadhi": jan_aushadhi_info,
        "disclaimer": (
            "This is for information only. Discuss with your doctor or pharmacist before switching to a generic."
        ),
    }
