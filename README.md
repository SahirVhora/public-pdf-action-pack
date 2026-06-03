# Public PDF Action Pack

Turn public-sector PDFs into plain-English actions, deadlines, and checklists.

## What it does

- Upload PDF, TXT, or Markdown
- Extract document text with page tracking
- Classify document type (school letter, council notice, NHS guidance, housing/property, HR policy, government guidance)
- Generate an action pack with:
  - Plain-English summary
  - Required actions with page-linked evidence
  - Key dates
  - Costs and contacts
  - Questions to ask (tailored per document type)
  - Choices / decisions to make (property documents)
  - Child checklist (school letters, NHS appointments)
  - Risks if ignored with severity levels
  - Source quotes with page numbers
- Export: Markdown, JSON, WhatsApp-friendly summary
- Tabbed premium UI
- "Not advice" disclaimer on all output
- Works fully offline (deterministic fallback, no AI needed)

## Privacy model

MVP is for public documents only. Do not upload sensitive private documents. The app does not store documents. If `OPENROUTER_API_KEY` is set and AI mode is enabled, extracted text is sent to OpenRouter. Turn AI off for deterministic local fallback.

## Demo PDFs

Sample documents in `demos/`:

| File | Type | What it demonstrates |
|---|---|---|
| `school-trip-letter.pdf` | School letter | Child checklist, payment, consent, questions |
| `council-tax-reminder.pdf` | Council notice | Recovery action risks, urgency, deadlines |
| `nhs-appointment-letter.pdf` | NHS guidance | Preparation checklist, appointment details |
| `property-solicitor-letter.pdf` | Property | Return section extraction, decisions, costs |

## Run locally

```bash
cd ~/projects/public-pdf-action-pack
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
streamlit run app.py
```

## CLI

```bash
PYTHONPATH=src python3 -m action_pack.cli demos/school-trip-letter.pdf --no-ai --out /tmp/action-pack.md
```

## Tests

```bash
pytest -q   # 30 tests
```

## Architecture

```text
PDF/TXT upload
  -> extractor.py (with page tracking)
  -> classifier.py (6 document types)
  -> analyser.py or fallback_analyser.py
  -> validators.py
  -> renderer.py (markdown, WhatsApp, copy message)
  -> Streamlit UI (tabbed layout) / CLI output
```
