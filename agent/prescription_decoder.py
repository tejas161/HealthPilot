"""
Prescription Decoder & Medicine Explainer tool.
Parses prescription text, explains medicines (brand + generic), dosage, side effects, precautions.
Does NOT recommend or prescribe — explanation only. Guardrails apply.
"""

import json
import re
from pathlib import Path

# Project root: parent of agent/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _load_json(filename: str) -> list | dict:
    """Load JSON from data/; return empty list or empty dict if missing/invalid."""
    path = DATA_DIR / filename
    if not path.exists():
        return [] if filename.endswith("s.json") or "reference" in filename else {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return [] if "reference" in filename or "abbrev" in filename else {}


def _get_dosage_abbreviations() -> dict[str, str]:
    """Load dosage abbreviation map (e.g. OD -> Once daily)."""
    data = _load_json("dosage_abbreviations.json")
    return data if isinstance(data, dict) else {}


def _get_drug_reference() -> list[dict]:
    """Load drug reference (name, generic_name, treats, side_effects, precautions, etc.)."""
    data = _load_json("drug_reference.json")
    if isinstance(data, list):
        return data
    return [data] if isinstance(data, dict) and data else []


def _find_abbreviations_in_text(text: str, abbr_map: dict[str, str]) -> list[dict]:
    """Find dosage abbreviations present in text and return their meanings."""
    found: list[dict] = []
    upper = text.upper()
    # Sort by length descending so longer abbreviations match first (e.g. NOCTE before OD)
    for abbr in sorted(abbr_map.keys(), key=len, reverse=True):
        if abbr.upper() in upper:
            # Use word-boundary or comma/newline so we don't match inside words
            pattern = re.compile(r"\b" + re.escape(abbr) + r"\b", re.IGNORECASE)
            if pattern.search(text):
                found.append({"abbreviation": abbr, "meaning": abbr_map[abbr]})
    return found


def _match_medicines_in_text(text: str, drug_ref: list[dict]) -> list[dict]:
    """
    Match drug reference entries to prescription text.
    Returns list of drug info with dosage_meaning filled from text context when possible.
    """
    text_lower = text.lower()
    abbr_map = _get_dosage_abbreviations()
    matched: list[dict] = []
    seen_names: set[str] = set()

    # Sort by name length descending to match "Dolo 650" before "Dolo"
    for drug in sorted(drug_ref, key=lambda d: len((d.get("name") or "")), reverse=True):
        if not isinstance(drug, dict):
            continue
        name = (drug.get("name") or "").strip()
        generic = (drug.get("generic_name") or "").strip()
        if not name or name.lower() in seen_names:
            continue
        if name.lower() not in text_lower and (not generic or generic.lower() not in text_lower):
            continue
        seen_names.add(name.lower())

        # Find dosage abbreviation near this medicine (same line or nearby)
        dosage_meaning = drug.get("dosage_notes") or ""
        for abbr, meaning in abbr_map.items():
            if re.search(r"\b" + re.escape(abbr) + r"\b", text, re.IGNORECASE):
                dosage_meaning = (dosage_meaning + f" Abbreviation '{abbr}' in your prescription means: {meaning}.").strip()

        entry = {
            "name": name,
            "generic_name": generic,
            "treats": drug.get("treats") or "—",
            "dosage_meaning": dosage_meaning or "Follow your doctor's instructions on the prescription.",
            "side_effects": drug.get("side_effects") or "—",
            "precautions": drug.get("precautions") or "—",
            "injection_purpose": drug.get("injection_purpose"),
        }
        if entry["injection_purpose"] is None:
            entry["injection_purpose"] = "Not an injection; for oral/other use."
        matched.append(entry)

    return matched


def decode_prescription(prescription_text: str) -> dict:
    """
    Decode and explain a prescription (text only). For image uploads, use OCR first and pass extracted text.

    Explains: medicine name (brand + generic), what it treats, dosage meaning (OD, BD, TDS, etc.),
    side effects, precautions, and injection purpose if applicable. Explanation only — no recommendation.

    Args:
        prescription_text: Raw prescription text (or OCR output from an image).

    Returns:
        dict: status, dosage_abbreviations_found, medicines (list of explained drugs), and message.
    """
    if not prescription_text or not prescription_text.strip():
        return {
            "status": "error",
            "error_message": "Prescription text is empty. Please paste or type the prescription, or upload an image after we support it.",
            "dosage_abbreviations_found": [],
            "medicines": [],
        }

    text = prescription_text.strip()
    abbr_map = _get_dosage_abbreviations()
    drug_ref = _get_drug_reference()

    dosage_found = _find_abbreviations_in_text(text, abbr_map)
    medicines = _match_medicines_in_text(text, drug_ref)

    return {
        "status": "success",
        "dosage_abbreviations_found": dosage_found,
        "medicines": medicines,
        "message": (
            "This is an explanation only. Always follow your doctor's prescription and consult them "
            "or a pharmacist before changing anything."
        ),
    }
