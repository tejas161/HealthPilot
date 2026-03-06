# HealthPilot Data

Store curated data here for the agent. Use the format that fits each use case. When adding a new tool, add a short description and its data files in **Tools and their data** below.

---

## Tools and their data

Each agent tool is listed with the data files it reads. Keep these files updated so the tool responses stay accurate.

| Tool | Description | Data files |
|------|-------------|------------|
| **Prescription Decoder & Medicine Explainer** | User pastes or uploads a prescription; explains each medicine (brand + generic), what it treats, dosage meaning (OD, BD, TDS, etc.), side effects, precautions, injection purpose. | `dosage_abbreviations.json`, `drug_reference.json` |
| **Generic Alternative & Price Transparency Finder** | Detects active ingredient, suggests cheaper generics, shows price differences, flags overpricing (if user shares price), links Jan Aushadhi. | `medicine_price_reference.json` |
| **Drug Interaction & Safety Checker** | User enters “I am taking X and Y. Safe?” — checks interaction severity, contraindications, allergy warnings, age restrictions, pregnancy safety. | `drug_interactions.json`, `drug_safety.json` (uses `medicine_price_reference.json` for brand→ingredient) |
| **Hospital Finder + Treatment Cost Estimator** | **A) Hospital Locator:** filter by disease, government/private, city, specialization. **B) Treatment Cost Estimator:** cost ranges only (consultation, diagnostics, medicines, admission) with disclaimer; never exact cost. | `hospitals.json`, `treatment_cost_ranges.json` |
| **Disease Guide & Early Prevention Advisor** | User asks e.g. “Tell me about diabetes” — provides what it is, early symptoms, risk factors, preventive lifestyle, when to see doctor. Education only; never diagnose. | `disease_guides.json` |
| **Health tips** | Returns cost-saving tips (generic medicines, prescription reuse, etc.). | `health_tips_sample.json`, `health_tips.json` |
| **Medicine info** | Lookup by name: basic medicine info, alternatives, price range. | `medicines.json` |

---

## Suggested formats (by use case)

| Use case | Format | Example files |
|----------|--------|----------------|
| Medicine list, prices, alternatives | JSON | `medicines.json`, `price_comparison.json` |
| FAQs, health tips, cost-saving tips | JSON | `health_tips.json`, `faq.json` |
| Tabular data (e.g. pharmacy, lab rates) | CSV or JSON | `pharmacy_rates.csv` |
| Static reference (drug names, categories) | JSON | `drug_categories.json` |
| Dosage abbreviations (OD, BD, TDS…) | JSON | `dosage_abbreviations.json` |
| Drug reference (prescription decoder) | JSON | `drug_reference.json` |
| Generic alternatives & price (NPPA-style, Jan Aushadhi) | JSON | `medicine_price_reference.json` |
| Drug interactions (pairwise severity) | JSON | `drug_interactions.json` |
| Drug safety (contraindications, allergy, age, pregnancy) | JSON | `drug_safety.json` |
| Hospitals (locator: city, type, specialization, disease, PMJAY) | JSON | `hospitals.json` |
| Treatment cost ranges (consultation, diagnostics, medicines, admission) | JSON | `treatment_cost_ranges.json` |
| Disease guides (symptoms, risk, prevention, when to see doctor) | JSON | `disease_guides.json` |

## India-specific

- Keep drug names in line with Indian market (generic + common brand names).
- Prices can be indicative ranges or per-source; document the source/region in the file or in this README.
- Consider adding fields like: `state`, `city_tier`, `source`, `last_updated` where relevant.

## Schema examples (by file)

- **medicines.json** (Medicine info): `name`, `generic_name`, `alternatives`, `price_range_inr`, `category`, `notes`
- **health_tips.json** / **health_tips_sample.json** (Health tips): `id`, `topic`, `content`, `related_to_cost_saving`, `source`
- **dosage_abbreviations.json** (Prescription Decoder): `"OD": "Once daily..."` (abbreviation → meaning). Add entries for OD, BD, TDS, QID, HS, SOS, AC, PC, etc.
- **drug_reference.json** (Prescription Decoder): `name`, `generic_name`, `treats`, `dosage_notes`, `side_effects`, `precautions`, `injection_purpose`. One entry per drug; used to explain each medicine in a prescription.
- **medicine_price_reference.json** (Generic Alternative & Price Finder): `brand_names`, `active_ingredient`, `strength_common`, `generic_alternatives` (name, typical_price_inr), `ceiling_price_inr`, `jan_aushadhi` (available, product_name, typical_price_inr, portal_url). Align ceiling with NPPA when available.
- **drug_interactions.json** (Drug Interaction & Safety Checker): pairwise entries with `ingredient1`, `ingredient2`, `severity` (major/moderate/minor), `description`, `action`. Use canonical ingredient names (same as in drug_safety / medicine_price_reference).
- **drug_safety.json** (Drug Interaction & Safety Checker): per-ingredient `ingredient`, `contraindications` (array), `allergy_warning`, `age_restrictions`, `pregnancy_safety`. One entry per active ingredient.
- **hospitals.json** (Hospital Locator): `name`, `city`, `state`, `type` (government/private), `specializations` (array), `diseases_handled` (array), `pmjay_empaneled`, `address`. Can align with government/PMJAY datasets.
- **treatment_cost_ranges.json** (Treatment Cost Estimator): `disease_or_category`, `hospital_type`, `city_tier`, `*_min_inr` / `*_max_inr` for consultation, diagnostics, medicines, admission; `notes`. Always ranges only; add disclaimer in tool.
- **disease_guides.json** (Disease Guide & Early Prevention Advisor): `name`, `aliases` (array), `what_it_is`, `early_symptoms` (array), `risk_factors` (array), `preventive_lifestyle` (array), `when_to_see_doctor`, `source_notes`. Can align with WHO/gov health portal; education only.

When you add a new tool, add a row in **Tools and their data** and a schema line here. Add your own files and extend schemas as the product grows.
