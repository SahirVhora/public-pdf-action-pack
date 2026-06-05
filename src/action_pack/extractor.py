from __future__ import annotations

from pathlib import Path
import tempfile

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}


def extract_text_from_path(path: str | Path) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")


def extract_text_from_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(content)
        tmp.flush()
        return extract_text_from_path(tmp.name)


def _extract_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF is required for PDF extraction. Install pymupdf."
        ) from exc

    parts: list[str] = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                parts.append(f"\n--- Page {index} ---\n{text}")
    return "\n".join(parts).strip()
