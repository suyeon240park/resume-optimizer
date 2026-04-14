"""Tests for the LLM engine — mocks the Anthropic client to verify prompt
formatting and response parsing."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.llm_engine import OptimizationEngine


def _make_mock_response(text: str):
    block = MagicMock()
    block.text = text
    resp = MagicMock()
    resp.content = [block]
    return resp


@pytest.fixture
def engine():
    return OptimizationEngine(api_key="test-key")


class TestAnalyzeJD:
    @pytest.mark.asyncio
    async def test_returns_parsed_json(self, engine: OptimizationEngine):
        expected = {
            "role_title": "Backend Engineer",
            "seniority": "mid",
            "team_function": "backend",
            "required_skills": [{"skill": "Python", "category": "language", "importance": "critical"}],
            "domain_keywords": ["microservices"],
            "soft_signals": ["ownership"],
            "ats_keywords": ["REST API"],
        }
        engine.client.messages.create = AsyncMock(return_value=_make_mock_response(json.dumps(expected)))

        result = await engine.analyze_jd("We need a backend engineer...")
        assert result == expected

    @pytest.mark.asyncio
    async def test_prompt_contains_jd_text(self, engine: OptimizationEngine):
        engine.client.messages.create = AsyncMock(return_value=_make_mock_response("{}"))
        await engine.analyze_jd("Looking for a Rust developer")
        call_args = engine.client.messages.create.call_args
        prompt_text = call_args.kwargs["messages"][0]["content"]
        assert "Rust developer" in prompt_text


class TestScoreAlignment:
    @pytest.mark.asyncio
    async def test_returns_alignment(self, engine: OptimizationEngine):
        expected = {
            "bullet_scores": [{"section": "Experience", "bullet": "test", "relevance": 0.8, "matched_skills": ["Python"], "notes": ""}],
            "gap_analysis": {"missing_critical": [], "missing_preferred": [], "strongest_matches": ["Python"]},
        }
        engine.client.messages.create = AsyncMock(return_value=_make_mock_response(json.dumps(expected)))
        result = await engine.score_alignment({"sections": []}, {"required_skills": []})
        assert result == expected


class TestGenerateMutations:
    @pytest.mark.asyncio
    async def test_returns_changes_list(self, engine: OptimizationEngine):
        changes = [
            {
                "type": "edit",
                "section": "Experience",
                "target": "Old bullet",
                "proposed": "New bullet",
                "rationale": "Better keywords",
                "keywords_addressed": ["Python"],
            }
        ]
        engine.client.messages.create = AsyncMock(
            return_value=_make_mock_response(json.dumps({"changes": changes}))
        )
        result = await engine.generate_mutations({}, {}, {})
        assert len(result) == 1
        assert result[0]["type"] == "edit"


class TestFullPipeline:
    @pytest.mark.asyncio
    async def test_runs_three_stages(self, engine: OptimizationEngine):
        jd_resp = _make_mock_response(json.dumps({
            "role_title": "SWE",
            "seniority": "mid",
            "team_function": "backend",
            "required_skills": [],
            "domain_keywords": [],
            "soft_signals": [],
            "ats_keywords": [],
        }))
        align_resp = _make_mock_response(json.dumps({
            "bullet_scores": [],
            "gap_analysis": {"missing_critical": [], "missing_preferred": [], "strongest_matches": []},
        }))
        mut_resp = _make_mock_response(json.dumps({"changes": []}))

        engine.client.messages.create = AsyncMock(side_effect=[jd_resp, align_resp, mut_resp])

        result = await engine.run_full_pipeline({"sections": []}, "Some JD text")
        assert engine.client.messages.create.call_count == 3
        assert result.mutations == []
