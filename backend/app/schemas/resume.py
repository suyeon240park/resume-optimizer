from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    name: str = Field(..., max_length=255)
    latex_source: str = Field(..., max_length=200_000)
    preset_type: str | None = Field(None, max_length=50)


class ResumeUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    latex_source: str | None = Field(None, max_length=200_000)
    preset_type: str | None = Field(None, max_length=50)


class ResumeOut(BaseModel):
    id: uuid.UUID
    name: str
    preset_type: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetail(ResumeOut):
    latex_source: str
    sections: list[dict] | None = None
