from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    jd_text: str = Field(..., max_length=50_000)


class ScrapeResponse(BaseModel):
    jd_analysis: dict


class OptimizeRequest(BaseModel):
    base_resume_id: uuid.UUID


class MutationItem(BaseModel):
    type: str = Field(..., pattern=r"^(edit|add|remove|reorder)$")
    section: str = Field(..., max_length=255)
    target: str | None = Field(None, max_length=2000)
    proposed: str | None = Field(None, max_length=2000)
    rationale: str = Field(..., max_length=1000)
    keywords_addressed: list[str] = Field(default_factory=list, max_length=50)


class OptimizeResponse(BaseModel):
    jd_analysis: dict
    alignment: dict
    mutations: list[MutationItem]


class ApplyRequest(BaseModel):
    """Accepted mutations (user may have edited ``proposed`` text)."""
    base_resume_id: uuid.UUID
    mutations: list[MutationItem] = Field(..., max_length=100)


class ApplyResponse(BaseModel):
    version_id: uuid.UUID
    version_number: int
    ats_score: float | None
    latex_source: str


class ATSScoreResponse(BaseModel):
    score: float
    matched: list[dict]
    partial: list[dict]
    missing: list[dict]
