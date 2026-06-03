# Public PDF Action Pack

Turn public-sector PDFs into plain-English actions, deadlines, and checklists.

MVP status: local prototype.

## What it does

- Upload PDF, TXT, or Markdown
- Extract document text
- Classify the document type
- Generate an action pack with:
  - plain-English summary
  - required actions
  - key dates
  - costs
  - contacts
  - questions to ask
  - risks if ignored
  - source quotes
- Export Markdown and JSON

## Privacy model

MVP is for public documents only. Do not upload sensitive private documents. The app does not store documents by default. If `OPENROUTER_API_KEY` is set and AI mode is enabled, extracted text is sent to OpenRouter. Turn AI off for deterministic local fallback.

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
PYTHONPATH=src python3 -m action_pack.cli examples/school-trip-letter.txt --no-ai --out /tmp/action-pack.md
```

## Tests

```bash
pytest -q
```

## Architecture

```text
PDF/TXT upload
  -> extractor.py
  -> classifier.py
  -> analyser.py or fallback_analyser.py
  -> validators.py
  -> renderer.py
  -> Streamlit UI / CLI output
```

## Suggested first public positioning

Turn any public PDF into a plain-English action checklist.
