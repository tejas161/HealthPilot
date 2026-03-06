"""
Disease Guide & Early Prevention Advisor tool.
Provides: what it is, early symptoms, risk factors, preventive lifestyle, when to see doctor.
Information and prevention only — never diagnose; always direct user to see a doctor for diagnosis.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

DISCLAIMER = (
    "This is general health education only. It does not diagnose any condition. "
    "Always see a doctor for proper diagnosis and treatment. Early prevention can reduce healthcare costs and harm."
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


def _find_guide(disease_name: str, guides: list) -> dict | None:
    """Find a disease guide by name or alias (case-insensitive). Returns first match."""
    if not disease_name or not disease_name.strip():
        return None
    query = disease_name.strip().lower()
    for g in guides:
        if not isinstance(g, dict):
            continue
        if query in (g.get("name") or "").lower():
            return g
        for alias in g.get("aliases") or []:
            if query in (alias or "").lower():
                return g
    return None


def get_disease_guide(disease_name: str) -> dict:
    """
    Get a disease guide: what it is, early symptoms, risk factors, preventive lifestyle changes,
    and when to see a doctor. For education and early prevention only — never use to diagnose.
    Always direct the user to see a doctor for diagnosis.

    Args:
        disease_name: Name or common alias (e.g. "diabetes", "sugar", "hypertension", "heart disease").

    Returns:
        dict: status, name, what_it_is, early_symptoms, risk_factors, preventive_lifestyle,
              when_to_see_doctor, disclaimer.
    """
    if not disease_name or not disease_name.strip():
        return {
            "status": "error",
            "error_message": "Please specify a disease or condition (e.g. diabetes, hypertension, heart disease).",
        }

    data = _load_json("disease_guides.json")
    if not isinstance(data, list):
        data = []
    guides = [g for g in data if isinstance(g, dict) and g.get("name")]
    guide = _find_guide(disease_name, guides)
    if not guide:
        return {
            "status": "error",
            "error_message": (
                f"No guide found for '{disease_name}'. Try 'diabetes', 'hypertension', 'heart disease', "
                "'respiratory infections', or 'thyroid'. We can add more conditions to our database."
            ),
        }

    return {
        "status": "success",
        "name": guide.get("name"),
        "what_it_is": guide.get("what_it_is") or "—",
        "early_symptoms": guide.get("early_symptoms") or [],
        "risk_factors": guide.get("risk_factors") or [],
        "preventive_lifestyle": guide.get("preventive_lifestyle") or [],
        "when_to_see_doctor": guide.get("when_to_see_doctor") or "—",
        "disclaimer": DISCLAIMER,
    }
