from action_pack.analyser import build_prompt_messages, parse_ai_json


def test_build_prompt_messages_requires_strict_json_and_source_quotes():
    messages = build_prompt_messages("Council tax notice text", "council_notice")
    combined = "\n".join(m["content"] for m in messages)
    assert "strict JSON" in combined
    assert "source_text" in combined
    assert "Do not invent" in combined


def test_parse_ai_json_accepts_fenced_json():
    raw = "```json\n{\"title\":\"Notice\",\"document_type\":\"council_notice\",\"audience\":[\"Residents\"],\"plain_english_summary\":[\"Pay soon\"],\"key_dates\":[],\"required_actions\":[],\"optional_actions\":[],\"documents_needed\":[],\"costs\":[],\"contacts\":[],\"risks\":[],\"questions_to_ask\":[],\"urgency_score\":2,\"confidence\":\"medium\",\"source_quotes\":[]}\n```"
    pack = parse_ai_json(raw)
    assert pack.title == "Notice"
    assert pack.document_type == "council_notice"
