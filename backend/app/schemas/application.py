from __future__ import annotations

import uuid
from datetime import datetime

from enum import Enum

from pydantic import BaseModel, Field


class ApplicationStatusEnum(str, Enum):
    draft = "draft"
    optimized = "optimized"
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"


class ApplicationCreate(BaseModel):
    company: str = Field(..., max_length=255)
    role_title: str = Field(..., max_length=255)
    portal_url: str | None = Field(None, max_length=2048)
    jd_snapshot: str = Field(..., max_length=50_000)


class ApplicationUpdate(BaseModel):
    status: ApplicationStatusEnum | None = None
    applied_at: datetime | None = None


class ApplicationOut(BaseModel):
    id: uuid.UUID
    company: str
    role_title: str
    portal_url: str | None
    status: str
    jd_analysis: dict | None
    applied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationDetail(ApplicationOut):
    jd_snapshot: str


class VersionOut(BaseModel):
    id: uuid.UUID
    base_resume_id: uuid.UUID | None
    version_number: int
    ats_score: float | None
    changes_applied: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class VersionDetail(VersionOut):
    latex_source: str
