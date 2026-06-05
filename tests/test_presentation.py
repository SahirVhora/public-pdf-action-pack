from action_pack.presentation import action_label, source_is_duplicate
from action_pack.renderer import render_markdown
from action_pack.schemas import ActionItem, ActionPack
from action_pack.text_utils import guess_title


def test_source_is_duplicate_when_caption_repeats_checkbox_text():
    action = ActionItem(
        action="If you are buying a property with another person, you must consider how you will own",
        owner="Reader",
        priority="high",
        source_text="If you are buying a property with another person, you must consider how you will own",
    )
    assert source_is_duplicate(action) is True


def test_source_is_not_duplicate_when_evidence_adds_context():
    action = ActionItem(
        action="Pay £650.00 on account",
        owner="Reader",
        priority="high",
        source_text="Cheque / bank transfer / card payment for £650.00 made payable to Sydney Mitchell",
    )
    assert source_is_duplicate(action) is False


def test_action_label_contains_owner_priority_and_deadline_once():
    action = ActionItem(
        action="Return the form",
        owner="Reader",
        priority="high",
        deadline="2026-06-14",
        source_text="Return the form",
    )
    assert action_label(action) == "Return the form (high) - Reader - due 2026-06-14"


def test_markdown_does_not_repeat_duplicate_source_text():
    pack = ActionPack(
        title="Test",
        document_type="housing_property",
        audience=["Reader"],
        plain_english_summary=["Summary"],
        required_actions=[
            ActionItem(
                action="Return the form",
                owner="Reader",
                priority="high",
                source_text="Return the form",
            )
        ],
        source_quotes=[],
    )
    markdown = render_markdown(pack)
    assert markdown.count("Return the form") == 1
    assert "Evidence:" not in markdown


def test_guess_title_handles_joint_tenants_heading():
    text = """
BUYING A PROPERTY IN JOINT NAMES
Introduction
If you are buying a property with another person, you must consider how you will own the property.
"""
    assert guess_title(text) == "BUYING A PROPERTY IN JOINT NAMES"
