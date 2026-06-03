from __future__ import annotations

import re
from .schemas import DocumentType

_RULES: list[tuple[DocumentType, list[str]]] = [
    ("school_letter", ["school", "parents", "pupils", "year ", "consent form", "packed lunch", "term"]),
    ("council_notice", ["council", "council tax", "borough", "recovery action", "planning", "resident"]),
    ("nhs_guidance", ["nhs", "patient", "appointment", "clinic", "hospital", "health"]),
    ("housing_property", ["property", "solicitor", "survey", "mortgage", "tenant", "landlord", "lease"]),
    ("hr_policy", ["employee", "manager", "hr", "policy", "annual leave", "payroll"]),
    ("government_guidance", ["gov.uk", "government", "eligibility", "benefit", "apply"]),
]


def classify_document(text: str) -> DocumentType:
    lower = re.sub(r"\s+", " ", text.lower())
    scores: dict[DocumentType, int] = {}
    for doc_type, keywords in _RULES:
        scores[doc_type] = sum(1 for keyword in keywords if keyword in lower)
    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "general_public_document"
    return best_type
