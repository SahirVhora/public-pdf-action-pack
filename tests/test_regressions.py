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
