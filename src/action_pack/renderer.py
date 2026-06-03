from __future__ import annotations

from .schemas import ActionPack


def render_markdown(pack: ActionPack) -> str:
    lines: list[str] = [f"# {pack.title}", ""]
    lines.append(f"Document type: {pack.document_type.replace('_', ' ')}")
    lines.append(f"Urgency score: {pack.urgency_score}/5")
    lines.append(f"Confidence: {pack.confidence}")
    lines.append("")

    lines.append("## Plain-English summary")
    for item in pack.plain_english_summary:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Required actions")
    if pack.required_actions:
        for action in pack.required_actions:
            deadline = f" by {action.deadline}" if action.deadline else ""
            lines.append(f"- [{action.priority}] {action.action}{deadline} - owner: {action.owner}")
            lines.append(f"  Source: {action.source_text}")
    else:
        lines.append("- No required actions found.")
    lines.append("")

    lines.append("## Key dates")
    if pack.key_dates:
        lines.append("| Date | Label | Source |")
        lines.append("|---|---|---|")
        for item in pack.key_dates:
            lines.append(f"| {item.date} | {item.label} | {item.source_text} |")
    else:
        lines.append("No key dates found.")
    lines.append("")

    lines.append("## Costs")
    if pack.costs:
        for cost in pack.costs:
            lines.append(f"- {cost.amount}: {cost.label} - {cost.source_text}")
    else:
        lines.append("- No costs found.")
    lines.append("")

    lines.append("## Contacts")
    if pack.contacts:
        for contact in pack.contacts:
            lines.append(f"- {contact.label}: {contact.value}")
    else:
        lines.append("- No contacts found.")
    lines.append("")

    lines.append("## Questions to ask")
    for question in pack.questions_to_ask or ["No suggested questions generated."]:
        lines.append(f"- {question}")
    lines.append("")

    lines.append("## Risks if ignored")
    if pack.risks:
        for risk in pack.risks:
            lines.append(f"- [{risk.severity}] {risk.risk}")
    else:
        lines.append("- No explicit risks found.")
    lines.append("")

    lines.append("## Source quotes")
    for quote in pack.source_quotes or ["No source quotes captured."]:
        lines.append(f"> {quote}")
    lines.append("")
    return "\n".join(lines)


def render_copy_message(pack: ActionPack) -> str:
    actions = "; ".join(action.action for action in pack.required_actions[:3]) or "review the document"
    dates = "; ".join(f"{d.label}: {d.date}" for d in pack.key_dates[:3]) or "no clear dates found"
    return f"I reviewed '{pack.title}'. Main actions: {actions}. Key dates: {dates}."
