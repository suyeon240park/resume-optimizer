"""Authentication routes — Google OAuth + JWT token management."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_google_token,
)
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., max_length=10_000)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., max_length=10_000)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    body: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        google_payload = verify_google_token(body.id_token, settings.google_client_id)
    except ValueError:
        raise HTTPException(401, "Invalid Google token")

    # Do not trust unverified emails for account creation or linking (account-takeover risk).
    if google_payload.get("email") and not google_payload.get("email_verified"):
        raise HTTPException(403, "Google email not verified")

    google_id = google_payload["sub"]
    email = google_payload.get("email", "")
    name = google_payload.get("name", "")

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Check if a user with this email already exists (e.g. from the old default flow)
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is not None:
            user.google_id = google_id
            user.name = name
        else:
            user = User(email=email, name=name, google_id=google_id)
            db.add(user)
        await db.commit()
        await db.refresh(user)

    access = create_access_token(str(user.id), settings.jwt_secret)
    refresh = create_refresh_token(str(user.id), settings.jwt_secret)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    payload = decode_token(body.refresh_token, settings.jwt_secret, expected_type="refresh")
    user_id = payload["sub"]
    user = await db.get(User, uuid.UUID(user_id))
    if user is None:
        raise HTTPException(401, "User not found")

    access = create_access_token(str(user.id), settings.jwt_secret)
    refresh = create_refresh_token(str(user.id), settings.jwt_secret)
    return TokenResponse(access_token=access, refresh_token=refresh)
