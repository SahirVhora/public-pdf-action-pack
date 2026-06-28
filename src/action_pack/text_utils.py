from __future__ import annotations

import re

MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06",
    "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12",
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "jun": "06", "jul": "07", "aug": "08", "sep": "09", "sept": "09", "oct": "10", "nov": "11", "dec": "12",
}

_DATE_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s+(\d{4})\b", re.I)
_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
_COST_RE = re.compile(r"£\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|£\s?\d+(?:\.\d{2})?")


def normalise_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def split_lines(text: str) -> list[str]:
    return [normalise_spaces(line) for line in text.splitlines() if normalise_spaces(line)]


def extract_dates_with_context(text: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for line in split_lines(text):
        for match in _DATE_RE.finditer(line):
            day, month, year = match.groups()
            iso = f"{year}-{MONTHS[month.lower()]}-{int(day):02d}"
            results.append((iso, line))
    return results


def extract_emails_with_context(text: str) -> list[tuple[str, str]]:
    return [(match.group(0), line) for line in split_lines(text) for match in _EMAIL_RE.finditer(line)]


def extract_costs_with_context(text: str) -> list[tuple[str, str]]:
    return [(match.group(0).replace(" ", ""), line) for line in split_lines(text) for match in _COST_RE.finditer(line)]


def guess_title(text: str) -> str:
    lines = split_lines(text)
    skip_prefixes = ("dear ", "page ", "--- page", "sydney mitchell llp is", "date:", ":")
    candidates = [line for line in lines[:30] if len(line) > 8 and not line.lower().startswith(skip_prefixes)]
    title_keywords = [
        "trip", "notice", "guidance", "policy", "reminder", "letter", "client care",
        "purchase", "buying a property", "joint names", "joint tenancy",
        "appointment", "appointment", "clinic", "hospital", "surgery",
        "recovery action", "final notice", "council tax",
        "planning", "benefit", "eligibility",
    ]
    for line in candidates:
        if any(word in line.lower() for word in title_keywords):
            return line[:90]
    # Fallback: prefer shorter lines (titles are usually brief)
    short = sorted([c for c in candidates if len(c) < 80], key=len)
    return short[0][:90] if short else (candidates[0][:90] if candidates else "Untitled document")


def infer_deadline_label(line: str) -> str:
    lower = line.lower()
    if "consent" in lower:
        return "Consent form deadline"
    if "payment" in lower or "pay" in lower or "due" in lower:
        return "Payment deadline"
    if "visit" in lower or "trip" in lower or "appointment" in lower:
        return "Event date"
    if "return" in lower:
        return "Return deadline"
    return "Important date"


_PAGE_MARKER = re.compile(r"--- Page (\d+) ---", re.I)


def page_for_line(text: str, line: str) -> int | None:
    """Return the page number for a given line of source text, or None if no page markers found."""
    marker_pages: list[tuple[int, int]] = []  # (char_position, page_number)
    for match in _PAGE_MARKER.finditer(text):
        marker_pages.append((match.start(), int(match.group(1))))
    if not marker_pages:
        return None
    # Find the position of the line in the text
    line_pos = text.find(line)
    if line_pos < 0:
        return None
    # Find the closest page marker before this line
    current_page = 1
    for marker_pos, page_num in marker_pages:
        if marker_pos < line_pos:
            current_page = page_num
        else:
            break
    return current_page
