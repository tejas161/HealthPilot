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
│   ├── agent.py        # ADK agent definition (HealthPilot)
│   ├── tools.py        # Tools: get_health_tips, get_medicine_info (read from data/)
│   ├── runner_helper.py # Run agent from Streamlit (Runner + InMemorySessionService)
│   └── __init__.py
├── data/
│   ├── README.md       # Data format guidance
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
   - The agent uses `health_tips_sample.json` (and `health_tips.json`, `medicines.json`) via its tools.

## Run

From the project root:

```bash
streamlit run app.py
```

Open the URL shown in the terminal (e.g. http://localhost:8501) and chat with HealthPilot.

## Data

- **Health tips**: Add or edit `data/health_tips.json` (see `data/health_tips_sample.json` for shape).
- **Medicines**: Add `data/medicines.json` with fields like `name`, `generic_name`, `alternatives`, `price_range_inr`, etc., for the medicine lookup tool.

## Code quality

- **Modularity**: Keep logic split across small, focused files — no single large file with all major code.
- **Helpers**: Extract reusable logic into helper modules/functions for readability and reuse.
- **Readability**: Prefer clear names, short functions, and code that is easy to modify.
- **OOP**: Use classes and OOP where it improves structure (stateful or cohesive behavior); prefer composition.

## Notes

- **India-only** for now; data and wording are aimed at the Indian market.
- The agent suggests consulting a doctor before changing medications; it does not replace professional advice.
- For production, consider replacing `InMemorySessionService` with a persistent session store (e.g. Vertex AI or DB).
