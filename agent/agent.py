"""HealthPilot ADK agent: health cost reduction advisor for India."""

import os
from pathlib import Path

from google.adk.agents import Agent

from agent.drug_safety_checker import check_drug_interaction_and_safety
from agent.generic_price_finder import find_generic_alternatives
from agent.prescription_decoder import decode_prescription
from agent.tools import get_health_tips, get_medicine_info
from guardrails.instructions import get_guardrail_instructions

# Load .env from project root so GEMINI_MODEL (and GOOGLE_API_KEY) are set
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

def _get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

root_agent = Agent(
    name="healthpilot_agent",
    model=_get_model(),
    description=(
        "Health cost reduction advisor for India. Helps users with health tips, "
        "medicine info, prescription decoding, and general guidance to lower healthcare costs. "
        "Uses tools to fetch curated data from the data folder."
    ),
    instruction=(
        "You are HealthPilot, a helpful health advisor focused on reducing healthcare costs for users in India. "
        "Be clear, concise, and supportive. "
        "Use get_health_tips when users ask for cost-saving tips, generic medicine advice, or prescription tips. "
        "Use get_medicine_info when users ask about a specific medicine, its alternatives, or price. "
        "Use decode_prescription when the user shares a prescription (pasted text or says they have uploaded one): "
        "it explains each medicine (brand + generic), what it treats, dosage meaning (OD, BD, TDS, etc.), "
        "side effects, precautions, and injection purpose. Only explain — never recommend changing or stopping any medicine. "
        "Use find_generic_alternatives when the user asks for cheaper options, generic alternatives, price comparison, "
        "whether something is overpriced, or Jan Aushadhi. It returns active ingredient, cheaper generics, price differences, "
        "overpricing flag (if they share the price they paid), and Jan Aushadhi link. Inform only — do not tell them to switch; "
        "direct them to discuss with doctor or pharmacist. "
        "Use check_drug_interaction_and_safety when the user says they are taking multiple medicines and asks if it's safe, "
        "or asks about interactions, contraindications, allergy warnings, age restrictions, or pregnancy safety. "
        "Pass the medicine list as a comma- or 'and'-separated string. Inform only — always tell them to discuss with doctor or pharmacist. "
        "Answer in the same language the user uses (e.g. Hindi, English).\n\n"
        + get_guardrail_instructions()
    ),
    tools=[get_health_tips, get_medicine_info, decode_prescription, find_generic_alternatives, check_drug_interaction_and_safety],
)
