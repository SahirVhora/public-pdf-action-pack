from pathlib import Path

from action_pack.extractor import extract_text_from_path
from action_pack.fallback_analyser import analyse_without_ai
from action_pack.renderer import render_markdown
from action_pack.text_utils import extract_costs_with_context, guess_title


def test_pdf_extraction_reads_all_pages(tmp_path):
    from reportlab.pdfgen import canvas

    pdf = tmp_path / "multi-page.pdf"
    c = canvas.Canvas(str(pdf))
    for page in range(1, 4):
        c.drawString(72, 760, f"Unique page {page} content")
        c.showPage()
    c.save()

    text = extract_text_from_path(pdf)

    assert "Unique page 1 content" in text
    assert "Unique page 2 content" in text
    assert "Unique page 3 content" in text


def test_guess_title_ignores_page_markers_and_firm_footer():
    text = """
--- Page 1 ---
Sydney Mitchell LLP is a Limited Liability Partnership registered in England No. OC342756
Client Care Letter for 5 Horrell Road
Dear Client
"""
    assert guess_title(text) == "Client Care Letter for 5 Horrell Road"


def test_cost_extraction_keeps_comma_amounts_intact():
    text = "Our legal fee is £1,125.00 and total estimate is £6,473.60. Payment on account is £650.00."
    amounts = [amount for amount, _ in extract_costs_with_context(text)]
    assert "£1,125.00" in amounts
    assert "£6,473.60" in amounts
    assert "£650.00" in amounts
    assert "£1" not in amounts


def test_joint_tenants_repayment_sentence_not_treated_as_payment_action():
    pack = analyse_without_ai("""
BUYING A PROPERTY IN JOINT NAMES
Where co-owners are going to be making unequal contributions to the repayment mortgage payments and household bills.
""")
    assert "Make the required payment" not in "\n".join(action.action for action in pack.required_actions)


def test_client_care_return_section_extracts_specific_required_items():
    text = """
Client Care Letter for 5 Horrell Road
PLEASE RETURN TO US THE FOLLOWING:
1. Cheque / bank transfer / card payment for £650.00 made payable to Sydney Mitchell LLP.
2. One signed copy of letter of instruction.
3. Completed and signed Conveyancing Instruction form.
4. Completed Joint Purchasers Information form.
5. Original proof of identity and proof of address.
6. documentary evidence of source of funds.
Please return to: Sydney Mitchell LLP.
"""
    pack = analyse_without_ai(text)
    actions = "\n".join(action.action for action in pack.required_actions)
    assert "Pay £650.00 on account" in actions
    assert "Return one signed copy of the letter of instruction" in actions
    assert "Return documentary evidence of source of funds" in actions


def test_property_joint_names_generates_decisions_to_make():
    text = """
BUYING A PROPERTY IN JOINT NAMES
If you are buying a property with another person, you must consider how you will own the property.
You can own as joint tenants or tenants in common.
Where co-owners are making unequal contributions to the purchase price, mortgage payments or household bills, you should consider a declaration of trust.
Joint tenancy affects what happens to the property when one owner dies and you should consider making wills.
"""

    pack = analyse_without_ai(text)

    assert pack.document_type == "housing_property"
    assert [decision.decision for decision in pack.decisions_to_make] == [
        "How to own the property",
        "Whether unequal contributions need protecting",
        "Whether wills are needed",
    ]
    assert pack.decisions_to_make[0].options == ["Joint tenants", "Tenants in common"]
    assert "declaration of trust" in pack.decisions_to_make[1].what_to_ask.lower()
    assert pack.decisions_to_make[2].priority == "medium"


def test_markdown_renders_decisions_to_make_table():
    text = """
BUYING A PROPERTY IN JOINT NAMES
You can own as joint tenants or tenants in common.
Where co-owners make unequal contributions, consider a declaration of trust.
"""

    markdown = render_markdown(analyse_without_ai(text))

    assert "## Choices / decisions to make" in markdown
    assert "| Decision | Options | What to ask | Priority |" in markdown
    assert "How to own the property" in markdown
    assert "Joint tenants; Tenants in common" in markdown


def test_school_trip_letter_generates_child_checklist():
    text = """
Year 4 School Trip to Warwick Castle
Dear Parents and Guardians,
We are pleased to announce a school trip to Warwick Castle on Friday 20th June 2026.
The cost of the trip is £18.50 per pupil, payable by Friday 6th June.
Please complete and return the attached consent form by the same date.
Your child will need: a packed lunch, a water bottle, comfortable walking shoes, and a waterproof coat.
Children should wear school uniform and bring a small backpack (no large bags).
The coach will depart at 8:45am and return by 3:30pm.
If your child requires any medication during the trip, please inform the school office.
"""

    pack = analyse_without_ai(text)

    assert pack.document_type == "school_letter"
    checklist_text = " ".join(pack.child_checklist)
    assert "packed lunch" in checklist_text
    assert "water bottle" in checklist_text
    assert "waterproof coat" in checklist_text
    assert "comfortable walking shoes" in checklist_text
    assert "school uniform" in checklist_text
    assert "small backpack" in checklist_text


def test_school_trip_generates_better_questions():
    text = """
Year 4 School Trip to Warwick Castle
Cost: £18.50 per pupil, payable by Friday 6th June 2026.
Please return the consent form by Friday 6th June.
Your child will need a packed lunch and a water bottle.
The coach departs at 8:45am and returns by 3:30pm.
If your child requires medication during the trip, please contact the school.
"""

    pack = analyse_without_ai(text)

    questions = pack.questions_to_ask
    assert any("financial" in q.lower() for q in questions)
    assert any("late" in q.lower() or "deadline" in q.lower() for q in questions)
    assert any("bring" in q.lower() for q in questions)
    assert any("return" in q.lower() or "time" in q.lower() for q in questions)
    assert any("medication" in q.lower() or "medical" in q.lower() for q in questions)


def test_markdown_renders_child_checklist():
    text = """
Year 4 School Trip
Your child will need: a packed lunch, a water bottle.
Children should wear school uniform.
"""
    markdown = render_markdown(analyse_without_ai(text))

    assert "## Child checklist" in markdown
    assert "packed lunch" in markdown
    assert "water bottle" in markdown
    assert "school uniform" in markdown


def test_council_recovery_notice_detects_high_urgency():
    text = """
COUNCIL TAX RECOVERY ACTION
Dear Resident,
Despite previous reminders, we have not received payment of your Council Tax.
The outstanding amount of £1,247.50 must be paid by 20th June 2026 to avoid recovery action.
If you do not pay by the deadline we may apply for a liability order through the magistrates court.
This will add costs of £95.00 to your account.
If you cannot pay, you must contact us immediately on 020 8825 7000.
"""

    pack = analyse_without_ai(text)

    assert pack.document_type == "council_notice"
    assert pack.urgency_score >= 4
    assert any("pay" in action.action.lower() for action in pack.required_actions)
    assert any("contact" in action.action.lower() for action in pack.required_actions)


def test_council_notice_generates_consequence_risks():
    text = """
COUNCIL TAX FINAL NOTICE
If payment is not received within 14 days we will begin recovery proceedings.
This may result in bailiff action and additional costs.
"""

    pack = analyse_without_ai(text)

    assert any("recovery" in risk.risk.lower() or "bailiff" in risk.risk.lower() for risk in pack.risks)
    assert any("cost" in risk.risk.lower() for risk in pack.risks)


def test_nhs_appointment_extracts_preparation():
    text = """
NHS Outpatient Appointment
Your appointment at Solihull Hospital is on Monday 15th June 2026 at 10:30am.
Please arrive 15 minutes before your appointment time.
Bring your appointment letter and a list of any medications you are taking.
You may be asked to provide a urine sample on arrival.
The Cardiology department is on the first floor, follow the blue signs.
"""

    pack = analyse_without_ai(text)

    assert pack.document_type == "nhs_guidance"
    assert any("medication" in item.lower() for item in pack.child_checklist) or \
           any("appointment letter" in item.lower() for item in pack.child_checklist)
    assert any("nhs number" in q.lower() or "medical record" in q.lower() for q in pack.questions_to_ask)


def test_markdown_hides_child_checklist_for_non_school():
    text = """
COUNCIL TAX REMINDER
Please pay £500 by 1st July 2026.
"""
    markdown = render_markdown(analyse_without_ai(text))

    assert "## Child checklist" in markdown
    assert "- No checklist items found." in markdown


def test_multipage_pdf_actions_get_page_numbers():
    text = """--- Page 1 ---
Client Care Letter
Please return the signed copy by 1st June.
--- Page 2 ---
Payment of £650.00 must be made by bank transfer.
--- Page 3 ---
Contact us at solicitor@example.com for any questions.
"""

    pack = analyse_without_ai(text)

    return_action = next(a for a in pack.required_actions if "signed" in a.action.lower())
    assert "Page 1" in return_action.source_text

    payment_action = next(a for a in pack.required_actions if "pay" in a.action.lower())
    assert "Page 2" in payment_action.source_text

    for cost in pack.costs:
        assert "Page 2" in cost.source_text

    for contact in pack.contacts:
        assert "Page 3" in contact.source_text


def test_no_page_marker_leaves_source_unchanged():
    text = """Return the consent form by Friday.
Payment of £18.50 is required.
"""
    pack = analyse_without_ai(text)

    for action in pack.required_actions:
        assert "Page" not in action.source_text
