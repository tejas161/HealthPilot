"""
Drug Interaction & Safety Checker tool.
Checks interaction severity between medicines; highlights contraindications,
allergy warnings, age restrictions, pregnancy safety. Information only — user must discuss with doctor.
"""

import json
import re
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


def _build_brand_to_ingredient_map() -> dict[str, str]:
    """Build map from brand/generic name (lower) to canonical ingredient name."""
    ref = _load_json("medicine_price_reference.json")
    if not isinstance(ref, list):
        ref = []
    mapping: dict[str, str] = {}
    for entry in ref:
        if not isinstance(entry, dict):
            continue
        ingredient = (entry.get("active_ingredient") or "").strip()
        if not ingredient:
            continue
        mapping[ingredient.lower()] = ingredient
        for brand in entry.get("brand_names") or []:
            if brand:
                mapping[(brand or "").strip().lower()] = ingredient
    return mapping


def _parse_medicine_list(user_input: str) -> list[str]:
    """Parse 'X and Y' or 'X, Y, Z' into a list of trimmed medicine names."""
    if not user_input or not user_input.strip():
        return []
    text = user_input.strip()
    # Split by " and ", ",", "&", newlines
    parts = re.split(r"\s+and\s+|\s*,\s*|\s+&\s+|\n+", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def _normalize_to_ingredients(medicine_names: list[str], brand_map: dict[str, str]) -> list[str]:
    """Resolve each name to canonical ingredient; unknown names kept as-is for display."""
    ingredients: list[str] = []
    seen: set[str] = set()
    for name in medicine_names:
        key = name.lower()
        ingredient = brand_map.get(key)
        if ingredient and ingredient not in seen:
            ingredients.append(ingredient)
            seen.add(ingredient)
        elif not ingredient and name not in seen:
            ingredients.append(name)
            seen.add(name)
    return ingredients


def _find_interactions(ingredients: list[str]) -> list[dict]:
    """Return pairwise interactions from drug_interactions.json for the given ingredient list."""
    data = _load_json("drug_interactions.json")
    if not isinstance(data, list):
        return []
    found: list[dict] = []
    ingredient_set = {i.lower() for i in ingredients}
    for row in data:
        if not isinstance(row, dict):
            continue
        i1 = (row.get("ingredient1") or "").strip().lower()
        i2 = (row.get("ingredient2") or "").strip().lower()
        if i1 in ingredient_set and i2 in ingredient_set:
            found.append({
                "ingredient1": row.get("ingredient1"),
                "ingredient2": row.get("ingredient2"),
                "severity": row.get("severity") or "unknown",
                "description": row.get("description") or "—",
                "action": row.get("action") or "Discuss with your doctor or pharmacist.",
            })
    return found


def _find_safety_per_drug(ingredients: list[str]) -> list[dict]:
    """Return safety info (contraindications, allergy, age, pregnancy) for each ingredient."""
    data = _load_json("drug_safety.json")
    if not isinstance(data, list):
        return []
    result: list[dict] = []
    by_ingredient = {(e.get("ingredient") or "").strip().lower(): e for e in data if isinstance(e, dict) and e.get("ingredient")}
    for ing in ingredients:
        key = ing.lower()
        entry = by_ingredient.get(key)
        if entry:
            result.append({
                "ingredient": entry.get("ingredient"),
                "contraindications": entry.get("contraindications") or [],
                "allergy_warning": entry.get("allergy_warning") or "—",
                "age_restrictions": entry.get("age_restrictions") or "—",
                "pregnancy_safety": entry.get("pregnancy_safety") or "—",
            })
        else:
            result.append({
                "ingredient": ing,
                "contraindications": [],
                "allergy_warning": "No safety data in our database for this medicine.",
                "age_restrictions": "—",
                "pregnancy_safety": "—",
            })
    return result


def check_drug_interaction_and_safety(medicine_list: str) -> dict:
    """
    Check drug interactions and safety for a list of medicines. User can pass e.g. "Paracetamol and Amoxicillin"
    or "Crocin, Omeprazole". Returns interaction severity, contraindications, allergy warnings, age restrictions,
    pregnancy safety. For information only — always direct user to discuss with doctor or pharmacist.

    Args:
        medicine_list: Comma- or "and"-separated list of medicine names (brand or generic), e.g. "I am taking X and Y".

    Returns:
        dict: status, ingredients_checked, interactions, safety_per_drug, disclaimer.
    """
    if not medicine_list or not medicine_list.strip():
        return {
            "status": "error",
            "error_message": "Please provide at least one medicine name (e.g. 'Paracetamol and Amoxicillin').",
        }

    names = _parse_medicine_list(medicine_list)
    if not names:
        return {
            "status": "error",
            "error_message": "Could not parse medicine names. Try: 'Medicine A and Medicine B' or 'Medicine A, Medicine B'.",
        }

    brand_map = _build_brand_to_ingredient_map()
    ingredients = _normalize_to_ingredients(names, brand_map)
    interactions = _find_interactions(ingredients)
    safety_per_drug = _find_safety_per_drug(ingredients)

    return {
        "status": "success",
        "ingredients_checked": ingredients,
        "interactions": interactions,
        "safety_per_drug": safety_per_drug,
        "disclaimer": (
            "This is general information only. It does not replace a doctor or pharmacist. "
            "Always discuss your full medicine list and any concerns with your healthcare provider."
        ),
    }
