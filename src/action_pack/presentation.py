from __future__ import annotations

from .schemas import ActionItem


def source_is_duplicate(action: ActionItem) -> bool:
    action_text = _normalise(action.action)
    source_text = _normalise(action.source_text or "")
    if not action_text or not source_text:
        return False
    return (
        action_text == source_text
        or action_text in source_text
        or source_text in action_text
    )


def action_label(action: ActionItem) -> str:
    owner = f" - {action.owner}" if action.owner else ""
    deadline = f" - due {action.deadline}" if action.deadline else ""
    return f"{action.action} ({action.priority}){owner}{deadline}"


def _normalise(value: str) -> str:
    return " ".join(value.lower().replace(".", "").strip().split())
