"""CRUD routes for job applications and their resume versions."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.models import Application, ResumeVersion, User
from app.db.session import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationOut,
    ApplicationUpdate,
    VersionOut,
)

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationOut, status_code=201)
async def create_application(
    body: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = Application(user_id=user.id, **body.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/applications", response_model=list[ApplicationOut])
async def list_applications(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Application).where(Application.user_id == user.id)
    if status:
        stmt = stmt.where(Application.status == status)
    stmt = stmt.order_by(Application.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/applications/{app_id}", response_model=ApplicationDetail)
async def get_application(
    app_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")
    return app


@router.patch("/applications/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: uuid.UUID,
    body: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/applications/{app_id}", status_code=204)
async def delete_application(
    app_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")
    await db.delete(app)
    await db.commit()


@router.get("/applications/{app_id}/versions", response_model=list[VersionOut])
async def list_versions(
    app_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await db.get(Application, app_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(404, "Application not found")
    result = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.application_id == app_id)
        .order_by(ResumeVersion.version_number.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()
