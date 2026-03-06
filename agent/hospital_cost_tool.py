"""
Hospital Finder + Treatment Cost Estimator (two sub-modules).
A) Hospital Locator: filter by disease, government/private, city, specialization.
B) Treatment Cost Estimator: cost ranges only (consultation, diagnostics, medicines, admission) with disclaimer.
Never give exact cost — always range with disclaimer. Information only.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

COST_DISCLAIMER = (
    "Costs are indicative ranges only and can vary by hospital, city, and case. "
    "Always confirm with the hospital. Ayushman Bharat (PMJAY) may cover eligible beneficiaries in empaneled hospitals."
)


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


# ---------- A) Hospital Locator ----------


def find_hospitals(
    disease: str | None = None,
    city: str | None = None,
    hospital_type: str | None = None,
    specialization: str | None = None,
) -> dict:
    """
    Find hospitals based on disease, city, government vs private, and/or specialization.
    Returns list of matching hospitals with name, city, type, specializations, PMJAY empanelment.
    For information only — does not recommend a specific hospital for treatment.

    Args:
        disease: Condition or disease (e.g. "Heart disease", "Diabetes").
        city: City name (e.g. "New Delhi", "Mumbai", "Bengaluru").
        hospital_type: "government" or "private".
        specialization: Department/specialization (e.g. "Cardiology", "Orthopedics").

    Returns:
        dict: status, hospitals (list), pmjay_note, disclaimer.
    """
    data = _load_json("hospitals.json")
    if not isinstance(data, list):
        data = []
    hospitals = [h for h in data if isinstance(h, dict)]
    if not hospitals:
        return {
            "status": "error",
            "error_message": "No hospital data available. Add entries to data/hospitals.json.",
            "hospitals": [],
        }

    disease_lower = (disease or "").strip().lower()
    city_lower = (city or "").strip().lower()
    type_lower = (hospital_type or "").strip().lower()
    if type_lower not in ("government", "private", ""):
        type_lower = ""
    spec_lower = (specialization or "").strip().lower()

    filtered = []
    for h in hospitals:
        if city_lower and city_lower not in (h.get("city") or "").lower():
            continue
        if type_lower and (h.get("type") or "").lower() != type_lower:
            continue
        if disease_lower:
            diseases = [d for d in (h.get("diseases_handled") or []) if disease_lower in (d or "").lower()]
            if not diseases:
                continue
        if spec_lower:
            specs = [s for s in (h.get("specializations") or []) if spec_lower in (s or "").lower()]
            if not specs:
                continue
        filtered.append({
            "name": h.get("name"),
            "city": h.get("city"),
            "state": h.get("state"),
            "type": h.get("type"),
            "specializations": h.get("specializations") or [],
            "pmjay_empaneled": h.get("pmjay_empaneled", False),
            "address": h.get("address"),
        })

    return {
        "status": "success",
        "hospitals": filtered,
        "count": len(filtered),
        "pmjay_note": "PMJAY (Ayushman Bharat) empaneled hospitals can provide cashless treatment to eligible beneficiaries. Check eligibility at pmjay.gov.in.",
        "disclaimer": "This list is for information only. Always contact the hospital for availability and admission. We do not recommend any specific hospital for your treatment.",
    }


# ---------- B) Treatment Cost Estimator ----------


def _normalize_disease_for_cost(disease: str) -> str:
    """Map user input to disease_or_category keys in cost data (partial match)."""
    d = disease.strip().lower()
    if not d:
        return "General consultation"
    if any(x in d for x in ["heart", "cardio", "cardiac"]):
        return "Cardiology / Heart"
    if any(x in d for x in ["bone", "joint", "ortho", "fracture"]):
        return "Orthopedics / Bone & joint"
    if any(x in d for x in ["diabetes", "sugar", "general medicine"]):
        return "Diabetes / General medicine"
    return "General consultation"


def _get_city_tier(city: str | None) -> str:
    """Return city_tier for cost lookup (tier1/tier2); default tier1."""
    if not city or not city.strip():
        return "tier1"
    c = city.strip().lower()
    tier2_cities = ["chandigarh", "vellore", "nagpur", "indore", "coimbatore", "kochi", "jaipur", "pune", "ahmedabad"]
    if any(t in c for t in tier2_cities):
        return "tier2"
    return "tier1"


def get_treatment_cost_estimate(
    disease_or_procedure: str,
    city: str | None = None,
    hospital_type: str | None = None,
) -> dict:
    """
    Get indicative cost ranges for treatment (consultation, diagnostics, medicines, admission).
    Never returns exact cost — only ranges with disclaimer. For information only.

    Args:
        disease_or_procedure: Condition or procedure (e.g. "heart", "diabetes", "fracture", "general").
        city: Optional city for city_tier (affects range).
        hospital_type: "government" or "private"; if None, returns both.

    Returns:
        dict: status, disease_category, cost_ranges (by type if applicable), disclaimer.
    """
    if not disease_or_procedure or not disease_or_procedure.strip():
        return {
            "status": "error",
            "error_message": "Please specify a disease or procedure (e.g. 'heart', 'diabetes', 'general consultation').",
        }

    category = _normalize_disease_for_cost(disease_or_procedure)
    city_tier = _get_city_tier(city)
    type_filter = (hospital_type or "").strip().lower()
    if type_filter not in ("government", "private"):
        type_filter = ""

    data = _load_json("treatment_cost_ranges.json")
    if not isinstance(data, list):
        data = []
    rows = [r for r in data if isinstance(r, dict) and (r.get("disease_or_category") or "").strip().lower() == category.lower()]
    if not rows:
        rows = [r for r in data if isinstance(r, dict) and (r.get("disease_or_category") or "").strip().lower() == "general consultation"]
    if not rows:
        return {
            "status": "error",
            "error_message": f"No cost range data for '{disease_or_procedure}'. Try 'general consultation', 'heart', 'diabetes', or 'orthopedics'.",
        }

    # Filter by city_tier and hospital_type
    matching = [r for r in rows if (r.get("city_tier") or "tier1") == city_tier]
    if not matching:
        matching = [r for r in rows if (r.get("city_tier") or "tier1") == "tier1"]
    if type_filter:
        matching = [r for r in matching if (r.get("hospital_type") or "").lower() == type_filter]
    if not matching:
        matching = rows[:2]  # show one govt one private if no type specified

    cost_ranges = []
    for r in matching:
        cost_ranges.append({
            "hospital_type": r.get("hospital_type"),
            "city_tier": r.get("city_tier") or "tier1",
            "consultation_range_inr": f"₹{r.get('consultation_min_inr', 0)} - ₹{r.get('consultation_max_inr', 0)}",
            "diagnostics_range_inr": f"₹{r.get('diagnostics_min_inr', 0)} - ₹{r.get('diagnostics_max_inr', 0)}",
            "medicines_range_inr": f"₹{r.get('medicines_min_inr', 0)} - ₹{r.get('medicines_max_inr', 0)}",
            "admission_range_inr": f"₹{r.get('admission_min_inr', 0)} - ₹{r.get('admission_max_inr', 0)}",
            "notes": r.get("notes"),
        })

    return {
        "status": "success",
        "disease_or_category": category,
        "cost_ranges": cost_ranges,
        "disclaimer": COST_DISCLAIMER,
    }
