from action_pack.classifier import classify_document
from action_pack.fallback_analyser import analyse_without_ai
from action_pack.renderer import render_markdown
from action_pack.validators import validate_action_pack

SCHOOL_TEXT = """
St Mary's Primary School
Year 4 Museum Trip
Dear Parents,
Year 4 pupils will visit the Science Museum on 21 June 2026.
Please return the consent form by 14 June 2026.
Payment of £25 is due by 16 June 2026.
Contact the school office at office@example.school if you need support.
Children should bring a packed lunch.
"""

COUNCIL_TEXT = """
Borough Council
Council Tax Reminder Notice
You must pay £120 by 30 June 2026 to avoid further recovery action.
If you cannot pay, contact revenues@example.gov.uk.
"""


def test_classifies_school_letter_from_trip_and_parent_language():
    assert classify_document(SCHOOL_TEXT) == "school_letter"


def test_classifies_council_notice_from_council_tax_language():
    assert classify_document(COUNCIL_TEXT) == "council_notice"


def test_fallback_analysis_extracts_dates_costs_contacts_and_actions():
    pack = analyse_without_ai(SCHOOL_TEXT)
    assert pack.title == "Year 4 Museum Trip"
    assert pack.document_type == "school_letter"
    assert any(
        item.date == "2026-06-14" and "consent" in item.label.lower()
        for item in pack.key_dates
    )
    assert any(cost.amount == "£25" for cost in pack.costs)
    assert any(contact.value == "office@example.school" for contact in pack.contacts)
    assert any(
        "Return the consent form" in action.action for action in pack.required_actions
    )
    assert pack.urgency_score >= 3


def test_validator_flags_actions_without_source_quote():
    pack = analyse_without_ai(SCHOOL_TEXT)
    pack.required_actions[0].source_text = ""
    result = validate_action_pack(pack)
    assert not result.ok
    assert any("source quote" in issue.lower() for issue in result.issues)


def test_render_markdown_contains_action_sections():
    pack = analyse_without_ai(SCHOOL_TEXT)
    markdown = render_markdown(pack)
    assert "# Year 4 Museum Trip" in markdown
    assert "## Required actions" in markdown
    assert "## Key dates" in markdown
    assert "Return the consent form" in markdown
    assert "£25" in markdown
