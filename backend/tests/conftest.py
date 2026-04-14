"""Shared test configuration — single test DB engine and app overrides."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.core.auth import create_access_token
from app.db.models import Base, User
from app.db.session import get_db
from app.main import app

FIXTURE_TEX = (Path(__file__).parent / "fixtures" / "jake_resume.tex").read_text(encoding="utf-8")
JWT_SECRET = "test-secret-that-is-long-enough-for-hmac"

engine_test = create_async_engine("sqlite+aiosqlite:///", echo=False)
test_session_factory = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

_test_settings = Settings(
    database_url="sqlite+aiosqlite:///",
    jwt_secret=JWT_SECRET,
    google_client_id="test-google-client-id",
    anthropic_api_key="test-anthropic-key",
)


async def _override_get_db():
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_settings] = lambda: _test_settings


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_test_user() -> tuple[User, str]:
    """Create a user in the test DB and return (user, access_token)."""
    async with test_session_factory() as session:
        user = User(email="test@example.com", name="Test User", google_id="google-123")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token(str(user.id), JWT_SECRET)
        return user, token


@pytest.fixture
async def authed_client():
    """AsyncClient with a valid Authorization header."""
    _, token = await create_test_user()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
