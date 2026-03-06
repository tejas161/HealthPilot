# HealthPilot Data

Store curated data here for the agent. Use the format that fits each use case.

## Suggested formats

| Use case | Format | Example files |
|----------|--------|----------------|
| Medicine list, prices, alternatives | JSON | `medicines.json`, `price_comparison.json` |
| FAQs, health tips, cost-saving tips | JSON | `health_tips.json`, `faq.json` |
| Tabular data (e.g. pharmacy, lab rates) | CSV or JSON | `pharmacy_rates.csv` |
| Static reference (drug names, categories) | JSON | `drug_categories.json` |
| Dosage abbreviations (OD, BD, TDS…) | JSON | `dosage_abbreviations.json` |
| Drug reference (for prescription decoder) | JSON | `drug_reference.json` |

## India-specific

- Keep drug names in line with Indian market (generic + common brand names).
- Prices can be indicative ranges or per-source; document the source/region in the file or in this README.
- Consider adding fields like: `state`, `city_tier`, `source`, `last_updated` where relevant.

## Schema examples (optional)

- **medicines.json**: `name`, `generic_name`, `alternatives`, `price_range_inr`, `category`, `notes`
- **health_tips.json**: `id`, `topic`, `content`, `related_to_cost_saving`, `source`
- **dosage_abbreviations.json**: `"OD": "Once daily..."` (abbreviation → meaning).
- **drug_reference.json**: `name`, `generic_name`, `treats`, `dosage_notes`, `side_effects`, `precautions`, `injection_purpose` (for prescription decoder).

Add your own files and extend schemas as the product grows.
