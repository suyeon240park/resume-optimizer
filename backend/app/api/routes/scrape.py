"""JD analysis endpoint — accepts raw text, returns structured extraction."""

from __future__ import annotations

import anthropic
from fastapi import APIRouter, Depends, Request

from app.config import Settings, get_settings
from app.core.auth import get_current_user
from app.core.jd_analyzer import analyze_jd
from app.db.models import User
from app.rate_limit import limiter
from app.schemas.optimization import ScrapeRequest, ScrapeResponse

router = APIRouter(tags=["scrape"])


@router.post("/scrape", response_model=ScrapeResponse)
@limiter.limit("10/minute")
async def scrape_jd(
    request: Request,
    body: ScrapeRequest,
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    jd_analysis = await analyze_jd(client, body.jd_text)
    return ScrapeResponse(jd_analysis=jd_analysis)
