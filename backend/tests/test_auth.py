"""Tests for the authentication module — JWT creation, decoding, and the
Google OAuth endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.main import app

from tests.conftest import JWT_SECRET


class TestJWTCreation:
    def test_access_token_roundtrip(self):
        uid = str(uuid.uuid4())
        token = create_access_token(uid, JWT_SECRET)
        payload = decode_token(token, JWT_SECRET, expected_type="access")
        assert payload["sub"] == uid
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        uid = str(uuid.uuid4())
        token = create_refresh_token(uid, JWT_SECRET)
        payload = decode_token(token, JWT_SECRET, expected_type="refresh")
        assert payload["sub"] == uid
        assert payload["type"] == "refresh"

    def test_wrong_type_rejected(self):
        uid = str(uuid.uuid4())
        token = create_refresh_token(uid, JWT_SECRET)
        with pytest.raises(Exception, match="Wrong token type"):
            decode_token(token, JWT_SECRET, expected_type="access")

    def test_expired_token_rejected(self):
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token = pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")
        with pytest.raises(Exception, match="Token expired"):
            decode_token(token, JWT_SECRET)

    def test_invalid_token_rejected(self):
        with pytest.raises(Exception, match="Invalid token"):
            decode_token("not.a.token", JWT_SECRET)


class TestGoogleAuthEndpoint:
    @pytest.mark.asyncio
    async def test_google_login_success(self, client: AsyncClient):
        mock_payload = {
            "sub": "google-user-123",
            "email": "test@gmail.com",
            "email_verified": True,
            "name": "Test User",
        }

        with patch("app.api.routes.auth.verify_google_token", return_value=mock_payload):
            resp = await client.post(
                "/api/auth/google",
                json={"id_token": "fake-google-token"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_google_login_rejects_unverified_email(self, client: AsyncClient):
        mock_payload = {
            "sub": "google-unverified",
            "email": "evil@gmail.com",
            "email_verified": False,
            "name": "Unverified",
        }
        with patch("app.api.routes.auth.verify_google_token", return_value=mock_payload):
            resp = await client.post(
                "/api/auth/google",
                json={"id_token": "fake-google-token"},
            )
            assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_google_login_invalid_token(self, client: AsyncClient):
        with patch(
            "app.api.routes.auth.verify_google_token",
            side_effect=ValueError("Invalid token"),
        ):
            resp = await client.post(
                "/api/auth/google",
                json={"id_token": "bad-token"},
            )
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_google_login_upserts_user(self, client: AsyncClient):
        mock_payload = {
            "sub": "google-upsert-test",
            "email": "upsert@gmail.com",
            "email_verified": True,
            "name": "Upsert User",
        }

        with patch("app.api.routes.auth.verify_google_token", return_value=mock_payload):
            resp1 = await client.post(
                "/api/auth/google",
                json={"id_token": "token-1"},
            )
            assert resp1.status_code == 200

            resp2 = await client.post(
                "/api/auth/google",
                json={"id_token": "token-2"},
            )
            assert resp2.status_code == 200


class TestRefreshEndpoint:
    @pytest.mark.asyncio
    async def test_refresh_flow(self, client: AsyncClient):
        mock_payload = {
            "sub": "google-refresh-test",
            "email": "refresh@gmail.com",
            "email_verified": True,
            "name": "Refresh User",
        }

        with patch("app.api.routes.auth.verify_google_token", return_value=mock_payload):
            login_resp = await client.post(
                "/api/auth/google",
                json={"id_token": "fake-token"},
            )
            refresh_token = login_resp.json()["refresh_token"]

            resp = await client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["access_token"] != login_resp.json()["access_token"]
