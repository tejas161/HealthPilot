# HealthPilot

HealthPilot is an AI-powered health advisor focused on **reducing healthcare costs** for users in **India**. It helps with cost-saving tips, medicine info, alternatives, and transparent health guidance — making healthcare more affordable and accessible.

## Features

- 💊 **Prescription Decoder**: Upload or paste prescriptions to understand medicines, dosages, and side effects
- 💰 **Generic Alternative Finder**: Find cheaper alternatives and compare prices with Jan Aushadhi options  
- ⚠️ **Drug Safety Checker**: Check interactions, contraindications, and safety warnings for medicines
- 🏥 **Hospital Finder**: Locate hospitals by specialization, city, and type (government/private)
- 📊 **Treatment Cost Estimator**: Get cost ranges for consultations, diagnostics, and treatments
- 💡 **Health Tips**: Cost-saving advice and medicine guidance

## Tech stack

- **UI**: Streamlit (chat interface)
- **Agent**: Google ADK (Agent Development Kit), Gemini 2.0 Flash
- **Data**: Local JSON (and other formats) in the `data/` folder

## Project structure

```
HealthPilot/
├── app.py              # Streamlit chat UI
├── agent/
│   ├── agent.py           # ADK agent definition (HealthPilot)
│   ├── tools.py           # get_health_tips, get_medicine_info
│   ├── prescription_decoder.py  # Prescription decoder & medicine explainer tool
│   ├── generic_price_finder.py # Generic alternatives & price transparency (Jan Aushadhi)
│   ├── drug_safety_checker.py   # Drug interaction & safety (contraindications, allergy, age, pregnancy)
│   ├── hospital_cost_tool.py    # Hospital Locator + Treatment Cost Estimator (ranges only)
│   ├── runner_helper.py   # Run agent from Streamlit (Runner + InMemorySessionService)
│   └── __init__.py
├── utils/
│   └── ocr.py            # OCR helper for prescription images (Tesseract)
├── ui/
│   └── prescription_section.py  # Streamlit UI: paste/upload prescription
├── guardrails/         # Safety: scope, disclaimers, output validation
│   ├── constants.py    # Forbidden phrases, disclaimers, scope
│   ├── checks.py       # validate_response(), contains_risky_content()
│   ├── instructions.py # Guardrail text for agent system prompt
│   └── __init__.py
├── data/
│   ├── README.md       # Data format guidance
│   ├── dosage_abbreviations.json  # OD, BD, TDS, etc.
│   ├── drug_reference.json       # For prescription decoder (treats, side effects, etc.)
│   ├── medicine_price_reference.json  # Generic alternatives, ceiling prices, Jan Aushadhi
│   ├── drug_interactions.json  # Pairwise interactions (severity, description)
│   ├── drug_safety.json        # Contraindications, allergy, age, pregnancy per ingredient
│   ├── hospitals.json         # Hospital locator (city, type, specialization, PMJAY)
│   ├── treatment_cost_ranges.json  # Cost ranges: consultation, diagnostics, medicines, admission
│   ├── health_tips_sample.json
│   └── (your JSON/CSV files)
├── docs/               # Documentation (placeholder)
├── .env                # GOOGLE_API_KEY (copy from .env.example)
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

1. **Clone and create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment**

   - Copy `.env.example` to `.env`
   - Set your [Google AI Studio API key](https://aistudio.google.com/app/apikey):  
     `GOOGLE_API_KEY=your_key`
   - Optionally set `GEMINI_MODEL` (default: `gemini-2.0-flash`). Change this to switch models when needed.

4. **Add data (optional)**

   - Put health tips, medicine lists, etc. in `data/` (see `data/README.md`).

5. **Prescription image OCR (optional)**

   - For decoding prescriptions from photos, install [Tesseract](https://github.com/tesseract-ocr/tesseract) on your system (e.g. `brew install tesseract` on macOS). Python deps (Pillow, pytesseract) are in `requirements.txt`.

## Run

From the project root:

```bash
streamlit run app.py
```

Open the URL shown in the terminal (e.g. http://localhost:8501) and chat with HealthPilot.

## Tools (agent)

- **Prescription Decoder & Medicine Explainer**: User pastes or uploads a prescription; the agent explains each medicine (brand + generic), what it treats, dosage meaning (OD, BD, TDS, etc.), side effects, precautions, and injection purpose. Data: `data/dosage_abbreviations.json`, `data/drug_reference.json`. Optional OCR for images via Tesseract (see `utils/ocr.py`).

- **Generic Alternative & Price Transparency Finder**: Detects active ingredient from brand/generic name, suggests cheaper generics, shows price differences, flags overpricing (if user shares the price they paid vs ceiling/typical), and links Jan Aushadhi (PMBJP). Data: `data/medicine_price_reference.json`. Tool: `find_generic_alternatives(medicine_name, user_price_inr=None)`.

- **Drug Interaction & Safety Checker**: User says e.g. “I am taking X and Y. Safe?” — agent checks interaction severity, contraindications, allergy warnings, age restrictions, pregnancy safety. Data: `data/drug_interactions.json`, `data/drug_safety.json`; uses `medicine_price_reference.json` to resolve brand names to ingredients. Tool: `check_drug_interaction_and_safety(medicine_list)`.

- **Hospital Finder + Treatment Cost Estimator** (two sub-modules): **A) Hospital Locator** — filter by disease, government/private, city, specialization; **B) Treatment Cost Estimator** — cost ranges only (consultation, diagnostics, medicines, admission) with disclaimer; never exact cost. Data: `data/hospitals.json`, `data/treatment_cost_ranges.json`. Tools: `find_hospitals(disease, city, hospital_type, specialization)`, `get_treatment_cost_estimate(disease_or_procedure, city, hospital_type)`.

## Data & Customization

All agent data is stored in the `data/` folder. You can customize or extend these files to improve responses:

- **Health tips**: `data/health_tips_sample.json` - Add cost-saving tips and advice
- **Medicine prices**: `data/medicine_price_reference.json` - Brand names, generics, Jan Aushadhi alternatives  
- **Drug interactions**: `data/drug_interactions.json` - Medicine interaction warnings and severity
- **Drug safety**: `data/drug_safety.json` - Contraindications, allergy warnings, age/pregnancy restrictions
- **Hospitals**: `data/hospitals.json` - Hospital directory with specializations and PMJAY status
- **Treatment costs**: `data/treatment_cost_ranges.json` - Cost ranges by procedure and hospital type
- **Drug reference**: `data/drug_reference.json` - Medicine explanations for prescription decoder
- **Dosage abbreviations**: `data/dosage_abbreviations.json` - Medical abbreviation meanings (OD, BD, etc.)

See `data/README.md` for detailed schemas and formatting guidelines.

## Guardrails & Safety

HealthPilot is a **sensitive, health-related** product with strict safety measures. Guardrails ensure all information is cautious and within scope:

- **Scope**: The agent is for cost-saving and general medicine-awareness only. It does not diagnose, prescribe, or give emergency advice.
- **Agent instructions**: The agent’s system prompt includes strict rules (in `guardrails/instructions.py`): no diagnosis, no “you should take X”, no dosage advice; always direct users to doctors/pharmacists for personal decisions.
- **Output validation**: Every agent response is checked in `guardrails/checks.py`. If risky phrases are detected (e.g. prescribing or diagnosing language), the response is replaced with a safe fallback message.
- **Disclaimers**: Medicine-related answers are guided to include a short “consult your doctor/pharmacist” disclaimer.

Do not remove or weaken guardrails without explicit product/legal review. To extend them, edit `guardrails/constants.py` (forbidden phrases, disclaimers) and `guardrails/instructions.py` (agent rules).

## Code quality

- **Modularity**: Keep logic split across small, focused files — no single large file with all major code.
- **Helpers**: Extract reusable logic into helper modules/functions for readability and reuse.
- **Readability**: Prefer clear names, short functions, and code that is easy to modify.
- **OOP**: Use classes and OOP where it improves structure (stateful or cohesive behavior); prefer composition.

## Notes

- **India-only** for now; data and wording are aimed at the Indian market.
- The agent suggests consulting a doctor before changing medications; it does not replace professional advice.
- For production, consider replacing `InMemorySessionService` with a persistent session store (e.g. Vertex AI or DB).
