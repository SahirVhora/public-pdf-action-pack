from __future__ import annotations

import re

from .classifier import classify_document
from .schemas import ActionItem, ActionPack, ContactItem, CostItem, DecisionItem, KeyDate, RiskItem
from .text_utils import (
    extract_costs_with_context,
    extract_dates_with_context,
    extract_emails_with_context,
    guess_title,
    infer_deadline_label,
    split_lines,
)


def analyse_without_ai(text: str) -> ActionPack:
    doc_type = classify_document(text)
    title = guess_title(text)
    lines = split_lines(text)
    dates = [KeyDate(date=date, label=infer_deadline_label(ctx), source_text=ctx) for date, ctx in extract_dates_with_context(text)]
    costs = [CostItem(amount=amount, label="Amount mentioned", source_text=ctx) for amount, ctx in extract_costs_with_context(text)]
    contacts = [ContactItem(label="Email", value=email, source_text=ctx) for email, ctx in extract_emails_with_context(text)]

    required_actions = _extract_required_actions(lines)
    optional_actions = _extract_optional_actions(lines)
    risks = _extract_risks(lines)
    summary = _summary_for(doc_type, title, bool(required_actions), bool(dates), bool(costs))

    urgency = 2
    if required_actions:
        urgency += 1
    if dates:
        urgency += 1
    if any(word in text.lower() for word in ["avoid", "must", "urgent", "deadline", "recovery action"]):
        urgency += 1
    urgency = min(5, urgency)

    return ActionPack(
        title=title,
        document_type=doc_type,
        audience=_audience_for(doc_type),
        plain_english_summary=summary,
        key_dates=dates,
        required_actions=required_actions,
        optional_actions=optional_actions,
        documents_needed=_documents_needed(lines),
        costs=costs,
        contacts=contacts,
        risks=risks,
        decisions_to_make=_decisions_for(doc_type, lines),
        child_checklist=_child_checklist_for(doc_type, lines),
        questions_to_ask=_questions_for(doc_type, bool(costs), bool(dates), bool(required_actions), text),
        urgency_score=urgency,
        confidence="medium",
        source_quotes=_source_quotes(lines),
    )


def _extract_required_actions(lines: list[str]) -> list[ActionItem]:
    actions: list[ActionItem] = []
    actions.extend(_extract_return_section_actions(lines))
    for line in lines:
        lower = line.lower()
        if "return" in lower and "consent" in lower:
            actions.append(ActionItem(action="Return the consent form", owner="Parent/guardian", deadline=_line_deadline(line), priority="high", source_text=line))
        elif ("cheque" in lower or "bank transfer" in lower or "card payment" in lower) and "£" in line:
            amount = _first_cost(line)
            label = f"Pay {amount} on account" if amount else "Make the requested payment"
            actions.append(ActionItem(action=label, owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "one signed copy of letter of instruction" in lower:
            actions.append(ActionItem(action="Return one signed copy of the letter of instruction", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "completed and signed conveyancing instruction" in lower:
            actions.append(ActionItem(action="Return the completed and signed Conveyancing Instruction form", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "completed joint purchasers" in lower:
            actions.append(ActionItem(action="Return the completed Joint Purchasers Information form", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "proof of identity" in lower and "proof of address" in lower:
            actions.append(ActionItem(action="Provide original proof of identity and proof of address", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "documentary evidence of source of funds" in lower:
            actions.append(ActionItem(action="Return documentary evidence of source of funds", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "signed client care" in lower or "client care letter" in lower and "signed" in lower:
            actions.append(ActionItem(action="Return the signed client care letter", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "source of funds" in lower and ("questionnaire" in lower or "complete" in lower or "completed" in lower):
            actions.append(ActionItem(action="Complete the source of funds questionnaire", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif _mentions_payment_request(lower):
            actions.append(ActionItem(action="Make the required payment", owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "i must ask you to pay" in lower and "£" in line:
            amount = _first_cost(line)
            actions.append(ActionItem(action=f"Pay {amount} on account" if amount else line.rstrip("."), owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif lower.startswith("you must") or " must " in lower:
            action = line.rstrip(".")
            actions.append(ActionItem(action=action[0].upper() + action[1:], owner="Reader", deadline=_line_deadline(line), priority="high", source_text=line))
        elif "please" in lower and any(word in lower for word in ["return", "complete", "bring", "contact", "pay"]):
            actions.append(ActionItem(action=line.rstrip("."), owner="Reader", deadline=_line_deadline(line), priority="medium", source_text=line))
    return _dedupe_actions(actions)


def _extract_return_section_actions(lines: list[str]) -> list[ActionItem]:
    marker_index = next((i for i, line in enumerate(lines) if "please return to us the following" in line.lower()), None)
    if marker_index is None:
        return []

    actions: list[ActionItem] = []
    for line in lines[marker_index + 1 : marker_index + 25]:
        lower = line.lower().strip()
        if lower.startswith("please return to:") or lower == "our bank details":
            break
        if lower in {"", "•"} or lower.rstrip(".").isdigit():
            continue
        if "cheque" in lower or "bank transfer" in lower or "card payment" in lower:
            amount = _first_cost(line)
            actions.append(ActionItem(action=f"Pay {amount} on account" if amount else "Make the requested payment", owner="Reader", priority="high", source_text=line))
        elif "one signed copy of letter of instruction" in lower:
            actions.append(ActionItem(action="Return one signed copy of the letter of instruction", owner="Reader", priority="high", source_text=line))
        elif "completed and signed conveyancing instruction" in lower:
            actions.append(ActionItem(action="Return the completed and signed Conveyancing Instruction form", owner="Reader", priority="high", source_text=line))
        elif "completed joint purchasers" in lower:
            actions.append(ActionItem(action="Return the completed Joint Purchasers Information form", owner="Reader", priority="high", source_text=line))
        elif "proof of identity" in lower and "proof of address" in lower:
            actions.append(ActionItem(action="Provide original proof of identity and proof of address", owner="Reader", priority="high", source_text=line))
        elif "documentary evidence of source of funds" in lower:
            actions.append(ActionItem(action="Return documentary evidence of source of funds", owner="Reader", priority="high", source_text=line))
    return actions


def _extract_optional_actions(lines: list[str]) -> list[ActionItem]:
    actions: list[ActionItem] = []
    for line in lines:
        lower = line.lower()
        if "if you" in lower and any(word in lower for word in ["cannot", "need", "would like"]):
            actions.append(ActionItem(action=line.rstrip("."), owner="Reader", priority="medium", source_text=line))
    return _dedupe_actions(actions)


def _extract_risks(lines: list[str]) -> list[RiskItem]:
    risks: list[RiskItem] = []
    for line in lines:
        lower = line.lower()
        if any(word in lower for word in ["avoid", "recovery action", "may not", "cannot", "deadline"]):
            risks.append(RiskItem(risk=line.rstrip("."), severity="high" if "recovery action" in lower else "medium", source_text=line))
    return risks[:5]


def _documents_needed(lines: list[str]) -> list[str]:
    docs = []
    for line in lines:
        lower = line.lower()
        if "consent form" in lower:
            docs.append("Consent form")
        if "medical" in lower:
            docs.append("Medical information")
    return sorted(set(docs))


def _decisions_for(doc_type: str, lines: list[str]) -> list[DecisionItem]:
    if doc_type != "housing_property":
        return []

    full_text = "\n".join(lines).lower()
    decisions: list[DecisionItem] = []

    ownership_source = _first_line_containing(lines, ["joint tenants", "tenants in common"])
    if ownership_source:
        decisions.append(
            DecisionItem(
                decision="How to own the property",
                options=["Joint tenants", "Tenants in common"],
                what_to_ask="Ask which ownership option best protects your deposit, contribution, inheritance wishes, and future sale position.",
                priority="high",
                source_text=ownership_source,
            )
        )

    contribution_source = _first_line_containing(lines, ["unequal contribution", "unequal contributions", "declaration of trust"])
    if contribution_source or ("unequal" in full_text and "contribution" in full_text):
        decisions.append(
            DecisionItem(
                decision="Whether unequal contributions need protecting",
                options=["No extra protection", "Declaration of trust", "Tenants in common with defined shares"],
                what_to_ask="Ask whether a declaration of trust is needed to record unequal deposits, mortgage payments, bills, or ownership shares.",
                priority="high",
                source_text=contribution_source or _first_line_containing(lines, ["unequal"]) or "Unequal contributions are mentioned.",
            )
        )

    wills_source = _first_line_containing(lines, ["will", "wills", "dies", "death", "inheritance"])
    if wills_source and any(word in full_text for word in ["joint tenant", "tenants in common", "property"]):
        decisions.append(
            DecisionItem(
                decision="Whether wills are needed",
                options=["Make or update wills", "Confirm existing wills are still suitable"],
                what_to_ask="Ask whether your ownership choice changes what happens on death and whether both buyers should make or update wills before completion.",
                priority="medium",
                source_text=wills_source,
            )
        )

    return _dedupe_decisions(decisions)


def _first_line_containing(lines: list[str], needles: list[str]) -> str | None:
    for line in lines:
        lower = line.lower()
        if any(needle in lower for needle in needles):
            return line
    return None


def _dedupe_decisions(decisions: list[DecisionItem]) -> list[DecisionItem]:
    seen: set[str] = set()
    deduped: list[DecisionItem] = []
    for decision in decisions:
        key = decision.decision.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(decision)
    return deduped[:8]


def _child_checklist_for(doc_type: str, lines: list[str]) -> list[str]:
    if doc_type != "school_letter":
        return []

    full_text = "\n".join(lines).lower()
    items: list[str] = []

    for needle_phrase in ["your child will need", "children will need", "pupils will need", "please bring", "your child should bring", "children should bring"]:
        for line in lines:
            lower = line.lower()
            if needle_phrase in lower:
                after = lower.split(needle_phrase, 1)[1]
                after = after.lstrip(": ").rstrip(".")
                chunks = [c.strip().rstrip(".") for c in after.replace(",", "\n").replace(" and ", "\n").replace(";", "\n").split("\n")]
                for chunk in chunks:
                    chunk = chunk.strip().rstrip(").").lstrip(": ")
                    if chunk and len(chunk) > 2 and not any(skip in chunk for skip in ["please", "the school", "if your", "inform", "medication", "no large"]):
                        items.append(chunk)
                break

    for line in lines:
        lower = line.lower()
        matched_wear = False
        if "wear" in lower and "should" in lower:
            matched_wear = True
            after = lower.split("wear", 1)[1].strip().rstrip(".")
            # Split if there's "and bring" appended
            for part in after.replace(" and bring ", "\n").replace(" and carry ", "\n").split("\n"):
                part = part.strip().rstrip(".")
                if part and len(part) > 3:
                    items.append(part)

        if not matched_wear and ("bring a" in lower or "bring an" in lower):
            after = lower.split("bring", 1)[1].strip().rstrip(".)")
            if after and not any(skip in after for skip in ["please", "the school"]):
                items.append(after)

    useful: list[str] = []
    for item in items:
        item = item.strip().rstrip(".").lstrip(": ")
        if item and len(item) > 3 and item not in useful:
            useful.append(item)
    return useful[:12]


def _questions_for(doc_type: str, has_costs: bool, has_dates: bool, has_actions: bool, text: str = "") -> list[str]:
    questions = []
    if has_costs:
        questions.append("Is financial support or an alternative payment option available?")
    if has_dates:
        questions.append("Can you confirm the exact deadline and whether late submissions are accepted?")
    if has_actions:
        questions.append("Is there anything else I need to submit or bring?")
    if doc_type == "school_letter":
        questions.append("What should my child bring on the day, and what time will they return?")
        if "medication" in text.lower() or "medical" in text.lower():
            questions.append("What is the procedure for administering medication during the trip?")
        if "packed lunch" in text.lower() or "lunch" in text.lower():
            questions.append("Are school meals provided, or should I send money for food?")
    elif doc_type == "council_notice":
        questions.append("What happens if I cannot meet the deadline?")
    elif doc_type == "nhs_guidance":
        questions.append("Should I bring my NHS number or any medical records to the appointment?")
    elif doc_type == "housing_property":
        questions.append("Are there any additional fees or charges not listed?")
    elif doc_type == "hr_policy":
        questions.append("Does this policy apply to my specific contract type or employment status?")
    return questions[:7]


def _summary_for(doc_type: str, title: str, has_actions: bool, has_dates: bool, has_costs: bool) -> list[str]:
    readable = doc_type.replace("_", " ")
    summary = [f"This appears to be a {readable}: {title}."]
    if has_actions:
        summary.append("There are actions the reader should complete.")
    if has_dates:
        summary.append("The document includes important dates or deadlines.")
    if has_costs:
        summary.append("The document mentions a payment or cost.")
    return summary


def _audience_for(doc_type: str) -> list[str]:
    return {
        "school_letter": ["Parents", "Guardians", "Pupils"],
        "council_notice": ["Residents", "Council service users"],
        "nhs_guidance": ["Patients", "Carers"],
        "housing_property": ["Buyers", "Renters", "Homeowners"],
        "hr_policy": ["Employees", "Managers"],
        "government_guidance": ["Citizens", "Applicants"],
    }.get(doc_type, ["Readers"])


def _source_quotes(lines: list[str]) -> list[str]:
    useful = [line for line in lines if any(word in line.lower() for word in ["must", "please", "due", "by ", "contact", "payment", "return"])]
    return useful[:8]


def _mentions_payment_request(lower_line: str) -> bool:
    words = set(re.findall(r"[a-z]+", lower_line))
    return ("payment" in words and ("due" in words or "pay" in words)) or "payable" in words


def _line_deadline(line: str) -> str | None:
    from .text_utils import extract_dates_with_context
    dates = extract_dates_with_context(line)
    return dates[0][0] if dates else None


def _first_cost(line: str) -> str | None:
    from .text_utils import extract_costs_with_context
    costs = extract_costs_with_context(line)
    return costs[0][0] if costs else None


def _dedupe_actions(actions: list[ActionItem]) -> list[ActionItem]:
    seen: set[str] = set()
    deduped: list[ActionItem] = []
    for action in actions:
        key = action.action.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(action)
    return deduped[:15]
