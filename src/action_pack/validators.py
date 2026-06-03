from __future__ import annotations

from .schemas import ActionPack, ValidationResult


def validate_action_pack(pack: ActionPack) -> ValidationResult:
    issues: list[str] = []
    warnings: list[str] = []

    if not pack.title.strip():
        issues.append("Title is missing.")
    if not pack.plain_english_summary:
        issues.append("Plain-English summary is missing.")

    for index, date in enumerate(pack.key_dates, start=1):
        if not date.source_text.strip():
            issues.append(f"Key date {index} is missing a source quote.")
    for index, action in enumerate(pack.required_actions, start=1):
        if not action.source_text.strip():
            issues.append(f"Required action {index} is missing a source quote.")
    for index, cost in enumerate(pack.costs, start=1):
        if not cost.source_text.strip():
            issues.append(f"Cost {index} is missing a source quote.")
    for index, decision in enumerate(pack.decisions_to_make, start=1):
        if not decision.source_text.strip():
            issues.append(f"Decision {index} is missing a source quote.")

    if pack.urgency_score >= 4 and not pack.required_actions:
        warnings.append("Urgency is high but no required actions were extracted.")
    if not pack.key_dates:
        warnings.append("No dates were found. Check whether the source document is scanned or poorly extracted.")

    return ValidationResult(ok=not issues, issues=issues, warnings=warnings)
