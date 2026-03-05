"""Guardrail checks: validate agent output for risky or out-of-scope content."""

from guardrails.constants import (
    FORBIDDEN_OUTPUT_PHRASES_LOWER,
    FULL_DISCLAIMER,
    SAFE_FALLBACK_MESSAGE,
)


def contains_risky_content(text: str) -> bool:
    """
    Return True if the text contains phrases that should not be in agent output
    (e.g. prescribing, diagnosing, or emergency instructions).
    """
    if not text or not text.strip():
        return False
    lower = text.strip().lower()
    return any(phrase in lower for phrase in FORBIDDEN_OUTPUT_PHRASES_LOWER)


def get_safe_fallback() -> str:
    """Return a safe, generic message when the agent response is flagged."""
    return SAFE_FALLBACK_MESSAGE


def get_full_disclaimer() -> str:
    """Return the full disclaimer text."""
    return FULL_DISCLAIMER


def validate_response(response_text: str) -> tuple[bool, str]:
    """
    Validate agent response. Returns (is_safe, final_text).
    If not safe, returns (False, safe_fallback_message).
    """
    if not response_text or not response_text.strip():
        return True, response_text or ""
    if contains_risky_content(response_text):
        return False, get_safe_fallback()
    return True, response_text.strip()
