"""Optimization endpoints — run the LLM pipeline and apply approved mutations."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.auth import get_current_user
from app.core.ats_scorer import calculate_ats_score
from app.core.latex_parser import LaTeXParser
from app.core.llm_engine import OptimizationEngine
from app.db.models import Application, BaseResume, ResumeVersion, User
from app.db.session import get_db
from app.rate_limit import limiter
from app.schemas.optimization import (
    ApplyRequest,
    ApplyResponse,
    MutationItem,
    OptimizeRequest,
    OptimizeResponse,
)

router = APIRouter(tags=["optimize"])


@router.post("/applications/{app_id}/optimize", response_model=OptimizeResponse)
@limiter.limit("10/minute")
async def optimize(
    request: Request,
    app_id: uuid.UUID,
    body: OptimizeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")

    resume = await db.get(BaseResume, body.base_resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(404, "Base resume not found")

    parser = LaTeXParser(resume.latex_source)
    resume_json = parser.to_json()

    engine = OptimizationEngine(api_key=settings.anthropic_api_key)
    result = await engine.run_full_pipeline(resume_json, app.jd_snapshot)

    # Persist the JD analysis on the application if not already set
    if app.jd_analysis is None:
        app.jd_analysis = result.jd_analysis
        await db.commit()

    return OptimizeResponse(
        jd_analysis=result.jd_analysis,
        alignment=result.alignment,
        mutations=[MutationItem(**m) for m in result.mutations],
    )


@router.post("/applications/{app_id}/apply", response_model=ApplyResponse)
@limiter.limit("20/minute")
async def apply_mutations(
    request: Request,
    app_id: uuid.UUID,
    body: ApplyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")

    resume = await db.get(BaseResume, body.base_resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(404, "Base resume not found")

    parser = LaTeXParser(resume.latex_source)
    sections = parser.extract_sections()

    # Build a lookup: (section_name, original_text) -> ContentNode
    node_lookup: dict[tuple[str, str], object] = {}
    for section in sections:
        for node in section.nodes:
            if node.command in ("resumeItem", "resumeSubItem"):
                node_lookup[(section.name, node.args[0])] = node
            for child in node.children:
                node_lookup[(section.name, child.args[0])] = child

    mutations_to_apply = []
    for mut in body.mutations:
        if mut.type == "edit" and mut.target and mut.proposed:
            key = (mut.section, mut.target)
            node = node_lookup.get(key)
            if node is not None:
                mutations_to_apply.append((node, [mut.proposed]))

    new_source = parser.apply_mutations(mutations_to_apply) if mutations_to_apply else resume.latex_source

    # ATS scoring
    ats = None
    if app.jd_analysis:
        ats_result = calculate_ats_score(new_source, app.jd_analysis)
        ats = ats_result["score"]

    # Retry loop to handle concurrent version number collisions
    from sqlalchemy.exc import IntegrityError

    for _attempt in range(3):
        result = await db.execute(
            select(func.coalesce(func.max(ResumeVersion.version_number), 0))
            .where(ResumeVersion.application_id == app_id)
        )
        next_version = result.scalar_one() + 1

        version = ResumeVersion(
            application_id=app_id,
            base_resume_id=body.base_resume_id,
            latex_source=new_source,
            changes_applied=[m.model_dump() for m in body.mutations],
            ats_score=ats,
            version_number=next_version,
        )
        db.add(version)
        try:
            await db.commit()
            break
        except IntegrityError:
            await db.rollback()
    else:
        raise HTTPException(409, "Could not allocate version number; please retry")
    await db.refresh(version)

    return ApplyResponse(
        version_id=version.id,
        version_number=version.version_number,
        ats_score=float(ats) if ats is not None else None,
        latex_source=new_source,
    )
