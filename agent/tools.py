"""HealthPilot agent tools. Load data from the data/ folder."""

import json
from pathlib import Path

# Project root: parent of agent/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _load_json(filename: str) -> list | dict:
    """Load a JSON file from data/; return empty list if missing or invalid."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def get_health_tips(topic: str | None = None) -> dict:
    """Fetch cost-saving health tips from curated data. Optionally filter by topic.

    Args:
        topic: Optional topic filter (e.g. 'generic_medicines', 'prescription').
               If None, returns all tips.

    Returns:
        dict: status and list of tips (each with id, topic, content, related_to_cost_saving).
    """
    tips = _load_json("health_tips_sample.json")
    if not tips:
        tips = _load_json("health_tips.json")
    if not isinstance(tips, list):
        tips = [tips] if tips else []

    if topic:
        topic_lower = topic.strip().lower()
        tips = [t for t in tips if isinstance(t, dict) and t.get("topic", "").lower() == topic_lower]

    return {"status": "success", "tips": tips, "count": len(tips)}


def get_medicine_info(medicine_name: str) -> dict:
    """Look up medicine info (alternatives, price range) from data. India-focused.

    Args:
        medicine_name: Name or generic name of the medicine.

    Returns:
        dict: status and medicine info if found; else status error and message.
    """
    medicines = _load_json("medicines.json")
    if not isinstance(medicines, list):
        medicines = [medicines] if medicines else []

    name_lower = medicine_name.strip().lower()
    for m in medicines:
        if not isinstance(m, dict):
            continue
        if name_lower in (m.get("name") or "").lower() or name_lower in (m.get("generic_name") or "").lower():
            return {"status": "success", "medicine": m}

    return {
        "status": "error",
        "error_message": f"No data found for '{medicine_name}'. Add entries to data/medicines.json for lookup.",
    }
