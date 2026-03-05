"""HealthPilot ADK agent: health cost reduction advisor for India."""

import os
from pathlib import Path

from google.adk.agents import Agent

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
        "medicine info, alternatives, and general guidance to lower healthcare costs. "
        "Uses tools to fetch curated data from the data folder."
    ),
    instruction=(
        "You are HealthPilot, a helpful health advisor focused on reducing healthcare costs for users in India. "
        "Be clear, concise, and supportive. Use the get_health_tips tool when users ask for cost-saving tips, "
        "generic medicine advice, or prescription tips. Use get_medicine_info when users ask about a specific "
        "medicine, its alternatives, or price. Answer in the same language the user uses (e.g. Hindi, English).\n\n"
        + get_guardrail_instructions()
    ),
    tools=[get_health_tips, get_medicine_info],
)
