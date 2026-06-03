from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

DocumentType = Literal[
    "school_letter",
    "council_notice",
    "nhs_guidance",
    "housing_property",
    "hr_policy",
    "government_guidance",
    "general_public_document",
]

Confidence = Literal["low", "medium", "high"]
Priority = Literal["low", "medium", "high"]


class KeyDate(BaseModel):
    date: str = Field(description="ISO date when known, otherwise original date text")
    label: str
    source_text: str


class ActionItem(BaseModel):
    action: str
    owner: str = "Reader"
    deadline: str | None = None
    priority: Priority = "medium"
    source_text: str


class CostItem(BaseModel):
    amount: str
    label: str = "Cost"
    source_text: str


class ContactItem(BaseModel):
    label: str = "Contact"
    value: str
    source_text: str


class RiskItem(BaseModel):
    risk: str
    severity: Priority = "medium"
    source_text: str


class ActionPack(BaseModel):
    title: str
    document_type: DocumentType
    audience: list[str] = Field(default_factory=list)
    plain_english_summary: list[str] = Field(default_factory=list)
    key_dates: list[KeyDate] = Field(default_factory=list)
    required_actions: list[ActionItem] = Field(default_factory=list)
    optional_actions: list[ActionItem] = Field(default_factory=list)
    documents_needed: list[str] = Field(default_factory=list)
    costs: list[CostItem] = Field(default_factory=list)
    contacts: list[ContactItem] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(default_factory=list)
    urgency_score: int = Field(ge=1, le=5, default=2)
    confidence: Confidence = "medium"
    source_quotes: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    ok: bool
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
