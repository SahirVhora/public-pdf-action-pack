# Security Notes

Public PDF Action Pack is designed for public-sector documents that are already safe to share. It is not intended for private letters, medical records, immigration documents, bank statements, payroll files, or other sensitive personal data.

## Document Handling

- Do not upload sensitive private documents.
- Do not commit uploaded documents, extracted text, generated action packs, or screenshots containing personal details.
- Demo files should stay synthetic or clearly public-domain.
- If AI mode is enabled with `OPENROUTER_API_KEY`, extracted document text may be sent to OpenRouter. Use `--no-ai` or turn AI off for local deterministic analysis.

## Publishing Checklist

- Run `pytest -q` before publishing changes.
- Review demos and generated exports for personal data.
- Keep `.env`, local outputs, and temporary upload folders out of version control.
