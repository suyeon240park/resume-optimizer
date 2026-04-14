"""Compilation and version download endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.auth import get_current_user
from app.core.compiler import compile_latex
from app.db.models import Application, ResumeVersion, User
from app.db.session import get_db

router = APIRouter(tags=["compile"])


async def _get_owned_version(
    version_id: uuid.UUID, user: User, db: AsyncSession
) -> ResumeVersion:
    """Fetch a version and verify the current user owns the parent application."""
    result = await db.execute(
        select(ResumeVersion)
        .options(joinedload(ResumeVersion.application))
        .where(ResumeVersion.id == version_id)
    )
    version = result.unique().scalar_one_or_none()
    if version is None or version.application.user_id != user.id:
        raise HTTPException(404, "Version not found")
    return version


@router.post("/versions/{version_id}/compile")
async def compile_version(
    version_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    version = await _get_owned_version(version_id, user, db)

    result = await compile_latex(version.latex_source)

    if not result.success:
        raise HTTPException(
            422,
            detail={
                "message": "LaTeX compilation failed",
                "errors": [{"line": e.line} for e in result.errors],
            },
        )

    version.compiled_pdf = result.pdf_bytes
    await db.commit()

    return {"message": "Compiled successfully", "version_id": str(version_id)}


@router.get("/versions/{version_id}/pdf")
async def download_pdf(
    version_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    version = await _get_owned_version(version_id, user, db)

    if version.compiled_pdf is None:
        result = await compile_latex(version.latex_source)
        if not result.success:
            raise HTTPException(
                422,
                detail={
                    "message": "LaTeX compilation failed",
                    "errors": [{"line": e.line} for e in result.errors],
                },
            )
        version.compiled_pdf = result.pdf_bytes
        await db.commit()

    return Response(
        content=version.compiled_pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="resume_v{version.version_number}.pdf"'},
    )


@router.get("/versions/{version_id}/diff/{other_id}")
async def diff_versions(
    version_id: uuid.UUID,
    other_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    v1 = await _get_owned_version(version_id, user, db)
    v2 = await _get_owned_version(other_id, user, db)

    return {
        "version_a": {"id": str(v1.id), "version_number": v1.version_number, "changes": v1.changes_applied},
        "version_b": {"id": str(v2.id), "version_number": v2.version_number, "changes": v2.changes_applied},
    }
