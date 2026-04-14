"""Stage 1 of the optimization pipeline — structured JD extraction."""

from __future__ import annotations

import json
import re

import anthropic
from fastapi import HTTPException

JD_ANALYSIS_PROMPT = """\
You are a technical recruiter analyst. Given a job description,
extract the following structured information. Respond ONLY with valid JSON,
no commentary or markdown fences.

{{
  "role_title": "...",
  "seniority": "intern | junior | mid | senior | staff | principal",
  "team_function": "backend | frontend | fullstack | ml | infra | embedded | devops | data | mobile | security | other",
  "required_skills": [
    {{ "skill": "Java", "category": "language", "importance": "critical" }},
    {{ "skill": "Kubernetes", "category": "tool", "importance": "preferred" }}
  ],
  "domain_keywords": ["distributed systems", "microservices"],
  "soft_signals": ["ownership", "cross-functional"],
  "ats_keywords": ["CI/CD", "REST API"]
}}

Job Description:
{jd_text}
"""

_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)


def _safe_parse_json(text: str) -> dict:
    """Parse JSON from LLM output, stripping markdown fences if present."""
    cleaned = text.strip()
    fence_match = _FENCE_RE.search(cleaned)
    if fence_match:
        cleaned = fence_match.group(1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            502, f"LLM returned invalid JSON: {exc.msg} (pos {exc.pos})"
        ) from None


async def analyze_jd(client: anthropic.AsyncAnthropic, jd_text: str, *, model: str = "claude-sonnet-4-20250514") -> dict:
    """
    Run Stage 1: parse raw job-description text into a structured
    extraction of skills, keywords, and seniority signals.
    """
    response = await client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": JD_ANALYSIS_PROMPT.format(jd_text=jd_text)}],
    )
    return _safe_parse_json(response.content[0].text)
