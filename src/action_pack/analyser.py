from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

from .classifier import classify_document
from .fallback_analyser import analyse_without_ai
from .schemas import ActionPack

DEFAULT_MODEL = "openai/gpt-4o-mini"


def build_prompt_messages(text: str, document_type: str | None = None) -> list[dict[str, str]]:
    doc_type = document_type or classify_document(text)
    schema_hint = ActionPack.model_json_schema()
    return [
        {
            "role": "system",
            "content": (
                "You convert public-sector documents into practical action packs. "
                "Return strict JSON only. Do not invent dates, costs, contacts, risks, or actions. "
                "Every key date, required action, cost, contact, and risk must include source_text copied from the document. "
                "If information is not found, use an empty list."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Document type guess: {doc_type}\n\n"
                f"JSON schema to follow:\n{json.dumps(schema_hint, indent=2)}\n\n"
                "Analyse this document and return strict JSON matching the schema.\n\n"
                f"DOCUMENT TEXT:\n{text[:18000]}"
            ),
        },
    ]


def analyse_with_ai_or_fallback(text: str, api_key: str | None = None, model: str | None = None) -> ActionPack:
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        return analyse_without_ai(text)
    try:
        messages = build_prompt_messages(text)
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/SahirVhora/public-pdf-action-pack",
                "X-Title": "Public PDF Action Pack",
            },
            json={"model": model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL), "messages": messages, "temperature": 0.1},
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        return parse_ai_json(raw)
    except Exception:
        return analyse_without_ai(text)


def parse_ai_json(raw: str) -> ActionPack:
    payload = _extract_json(raw)
    return ActionPack.model_validate(payload)


def _extract_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= start:
            text = text[start : end + 1]
    return json.loads(text)
