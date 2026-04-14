"""Integration tests for the API using an in-memory SQLite database."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import FIXTURE_TEX


class TestResumesAPI:
    @pytest.mark.asyncio
    async def test_create_and_list(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/resumes", json={
            "name": "Master Resume",
            "latex_source": FIXTURE_TEX,
            "preset_type": "master",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Master Resume"
        resume_id = data["id"]

        resp = await authed_client.get("/api/resumes")
        assert resp.status_code == 200
        assert any(r["id"] == resume_id for r in resp.json())

    @pytest.mark.asyncio
    async def test_get_detail_includes_sections(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/resumes", json={
            "name": "Test",
            "latex_source": FIXTURE_TEX,
        })
        resume_id = resp.json()["id"]

        resp = await authed_client.get(f"/api/resumes/{resume_id}")
        assert resp.status_code == 200
        detail = resp.json()
        assert "sections" in detail
        assert any(s["name"] == "Experience" for s in detail["sections"])

    @pytest.mark.asyncio
    async def test_update(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/resumes", json={
            "name": "Old Name",
            "latex_source": FIXTURE_TEX,
        })
        resume_id = resp.json()["id"]

        resp = await authed_client.patch(f"/api/resumes/{resume_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_delete(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/resumes", json={
            "name": "To Delete",
            "latex_source": FIXTURE_TEX,
        })
        resume_id = resp.json()["id"]

        resp = await authed_client.delete(f"/api/resumes/{resume_id}")
        assert resp.status_code == 204

        resp = await authed_client.get(f"/api/resumes/{resume_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_not_found(self, authed_client: AsyncClient):
        fake_id = str(uuid.uuid4())
        resp = await authed_client.get(f"/api/resumes/{fake_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/resumes")
        assert resp.status_code == 401


class TestApplicationsAPI:
    @pytest.mark.asyncio
    async def test_crud_flow(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/applications", json={
            "company": "Acme",
            "role_title": "Backend Engineer",
            "jd_snapshot": "We need a Python developer...",
        })
        assert resp.status_code == 201
        app_id = resp.json()["id"]

        resp = await authed_client.get("/api/applications")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

        resp = await authed_client.patch(f"/api/applications/{app_id}", json={"status": "applied"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "applied"

        resp = await authed_client.get(f"/api/applications/{app_id}")
        assert resp.status_code == 200
        assert resp.json()["jd_snapshot"] == "We need a Python developer..."

    @pytest.mark.asyncio
    async def test_filter_by_status(self, authed_client: AsyncClient):
        await authed_client.post("/api/applications", json={
            "company": "A", "role_title": "R", "jd_snapshot": "J",
        })
        resp2 = await authed_client.post("/api/applications", json={
            "company": "B", "role_title": "R", "jd_snapshot": "J",
        })
        app_id = resp2.json()["id"]
        await authed_client.patch(f"/api/applications/{app_id}", json={"status": "interview"})

        resp = await authed_client.get("/api/applications", params={"status": "interview"})
        assert resp.status_code == 200
        assert all(a["status"] == "interview" for a in resp.json())

    @pytest.mark.asyncio
    async def test_versions_empty(self, authed_client: AsyncClient):
        resp = await authed_client.post("/api/applications", json={
            "company": "X", "role_title": "Y", "jd_snapshot": "Z",
        })
        app_id = resp.json()["id"]

        resp = await authed_client.get(f"/api/applications/{app_id}/versions")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/applications")
        assert resp.status_code == 401
