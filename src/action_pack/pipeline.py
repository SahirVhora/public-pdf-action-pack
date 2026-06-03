from __future__ import annotations

from pathlib import Path

from .analyser import analyse_with_ai_or_fallback
from .extractor import extract_text_from_path
from .fallback_analyser import analyse_without_ai
from .renderer import render_markdown
from .schemas import ActionPack
from .validators import validate_action_pack, ValidationResult


class PipelineResult:
    def __init__(self, text: str, pack: ActionPack, markdown: str, validation: ValidationResult):
        self.text = text
        self.pack = pack
        self.markdown = markdown
        self.validation = validation


def process_text(text: str, use_ai: bool = True) -> PipelineResult:
    pack = analyse_with_ai_or_fallback(text) if use_ai else analyse_without_ai(text)
    validation = validate_action_pack(pack)
    markdown = render_markdown(pack)
    return PipelineResult(text=text, pack=pack, markdown=markdown, validation=validation)


def process_file(path: str | Path, use_ai: bool = True) -> PipelineResult:
    text = extract_text_from_path(path)
    return process_text(text, use_ai=use_ai)
