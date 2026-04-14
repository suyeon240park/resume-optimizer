"""CRUD routes for base LaTeX resumes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.latex_parser import LaTeXParser
from app.db.models import BaseResume, User
from app.db.session import get_db
from app.schemas.resume import ResumeCreate, ResumeDetail, ResumeOut, ResumeUpdate

router = APIRouter(tags=["resumes"])


@router.post("/resumes", response_model=ResumeOut, status_code=201)
async def create_resume(
    body: ResumeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = BaseResume(user_id=user.id, **body.model_dump())
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/resumes", response_model=list[ResumeOut])
async def list_resumes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BaseResume)
        .where(BaseResume.user_id == user.id)
        .order_by(BaseResume.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/resumes/{resume_id}", response_model=ResumeDetail)
async def get_resume(
    resume_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await db.get(BaseResume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    parser = LaTeXParser(resume.latex_source)
    sections = parser.to_json()
    return ResumeDetail(
        id=resume.id,
        name=resume.name,
        preset_type=resume.preset_type,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        latex_source=resume.latex_source,
        sections=sections,
    )


@router.patch("/resumes/{resume_id}", response_model=ResumeOut)
async def update_resume(
    resume_id: uuid.UUID,
    body: ResumeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await db.get(BaseResume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(resume, field, value)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.delete("/resumes/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await db.get(BaseResume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    await db.delete(resume)
    await db.commit()
