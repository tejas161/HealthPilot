# HealthPilot

HealthPilot is an AI-powered health advisor focused on **reducing healthcare costs** for users in **India**. It helps with cost-saving tips, medicine info, alternatives, and transparent health guidance — making healthcare more affordable and accessible.

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
│   ├── health_tips_sample.json
│   └── (your JSON/CSV files)
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

## Data

- **Health tips**: Add or edit `data/health_tips.json` (see `data/health_tips_sample.json` for shape).
- **Medicines**: Add `data/medicines.json` with fields like `name`, `generic_name`, `alternatives`, `price_range_inr`, etc., for the medicine lookup tool.
- **Price transparency**: `data/medicine_price_reference.json` — `brand_names`, `active_ingredient`, `generic_alternatives`, `ceiling_price_inr`, `jan_aushadhi` (for generic/price finder tool). You can align ceiling with NPPA data when available.

## Guardrails (safety)

HealthPilot is a **sensitive, health-related** product. Guardrails keep all user-facing information cautious and in-scope:

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
