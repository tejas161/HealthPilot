"""Guardrail constants: scope, disclaimers, and patterns to detect risky content."""

# What HealthPilot is and is NOT
SCOPE_DESCRIPTION = (
    "HealthPilot is for general health cost-saving information and medicine price/alternative "
    "awareness in India. It is NOT a substitute for a doctor, pharmacist, or emergency care."
)

# Short disclaimer appended when discussing medicines or treatment-related topics
MEDICINE_DISCLAIMER = (
    "This is general information only. Always consult your doctor or pharmacist before "
    "changing or starting any medicine."
)

# Full disclaimer for high-sensitivity responses
FULL_DISCLAIMER = (
    "Important: HealthPilot provides general information only and does not give medical advice, "
    "diagnosis, or treatment. Always consult a qualified healthcare provider for your situation. "
    "In an emergency, contact local emergency services."
)

# Phrases that must NOT appear in agent output (we are not prescribing or diagnosing)
FORBIDDEN_OUTPUT_PHRASES = (
    "you should take",
    "you should use",
    "take this medicine",
    "stop taking",
    "start taking",
    "your diagnosis",
    "you have a ",
    "you have the ",
    "you don't have ",
    "i diagnose",
    "i recommend you take",
    "prescribe",
    "dosage for you",
    "your dose",
    "emergency—",
    "call an ambulance",
    "go to the er",
    "rush to hospital",
    "you need to see a doctor immediately",  # We can say "consult a doctor" but not "immediately" in urgent tone
)

# Normalized (lowercased) for comparison
FORBIDDEN_OUTPUT_PHRASES_LOWER = tuple(p.strip().lower() for p in FORBIDDEN_OUTPUT_PHRASES)

# Safe fallback when response is flagged
SAFE_FALLBACK_MESSAGE = (
    "I can only share general information about health costs and medicines. "
    "For any personal health decision, please consult your doctor or a pharmacist. "
    "If this is an emergency, please contact local emergency services."
)
