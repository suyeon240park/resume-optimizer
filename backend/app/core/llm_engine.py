"""
Stages 2–3 of the optimization pipeline and top-level orchestrator.

Stage 2: Alignment scoring (resume × JD)
Stage 3: Mutation generation
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import anthropic

from app.core.jd_analyzer import analyze_jd, _safe_parse_json

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

ALIGNMENT_PROMPT = """\
You are a resume-to-JD alignment engine. Given a structured resume and a \
structured JD analysis, score each resume bullet for relevance and identify \
gaps.

Respond ONLY with valid JSON, no commentary or markdown fences.

{{
  "bullet_scores": [
    {{
      "section": "Experience",
      "bullet": "original bullet text",
      "relevance": 0.0 to 1.0,
      "matched_skills": ["Python", "AWS"],
      "notes": "optional short note"
    }}
  ],
  "gap_analysis": {{
    "missing_critical": ["skill not in resume but critical in JD"],
    "missing_preferred": ["skill not in resume but preferred in JD"],
    "strongest_matches": ["top 3 strongest existing matches"]
  }}
}}

CANDIDATE RESUME (structured):
{resume_json}

JD ANALYSIS:
{jd_analysis_json}
"""

MUTATION_PROMPT = """\
You are optimizing a software engineer's resume for a specific role.

RULES — follow these exactly:
1. PRESERVE AUTHENTICITY: Never fabricate experiences, metrics, or technologies \
   the candidate hasn't used. You may reframe existing work to emphasise \
   relevance, but never invent.
2. QUANTIFY: Every bullet should include a measurable outcome where possible. \
   Use formats like: "reduced X by Y%", "processed N records/day", \
   "improved latency from Xms to Yms".
3. KEYWORD INTEGRATION: Naturally weave in ATS keywords from the JD. \
   Don't keyword-stuff. The keyword should feel organic in context.
4. ACTION VERBS: Lead with strong, specific verbs. Prefer "Architected", \
   "Optimized", "Migrated" over "Worked on", "Helped with", "Was responsible for".
5. TECHNICAL DEPTH: Include the specific technologies, protocols, and patterns \
   used. "Built a REST API" < "Built a REST API using Spring Boot with JWT auth, \
   Redis caching, and PostgreSQL persistence".
6. ONE-LINE CONSTRAINT: Each bullet must fit on 1-2 lines of a standard \
   LaTeX resume (approximately 15-25 words). Brevity is mandatory.

For each proposed change, output ONLY valid JSON (no commentary or markdown \
fences):

{{
  "changes": [
    {{
      "type": "edit | add | remove | reorder",
      "section": "Experience | Projects | Skills | ...",
      "target": "original bullet text or null for additions",
      "proposed": "new bullet text or null for removals",
      "rationale": "why this change improves JD alignment",
      "keywords_addressed": ["Kubernetes", "CI/CD"]
    }}
  ]
}}

CANDIDATE RESUME (structured):
{resume_json}

JD ANALYSIS:
{jd_analysis_json}

ALIGNMENT SCORES:
{alignment_json}
"""


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

@dataclass
class OptimizationResult:
    jd_analysis: dict
    alignment: dict
    mutations: list[dict]


class OptimizationEngine:
    def __init__(self, api_key: str, *, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def analyze_jd(self, jd_text: str) -> dict:
        return await analyze_jd(self.client, jd_text, model=self.model)

    async def score_alignment(self, resume_json: dict, jd_analysis: dict) -> dict:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": ALIGNMENT_PROMPT.format(
                    resume_json=json.dumps(resume_json, indent=2),
                    jd_analysis_json=json.dumps(jd_analysis, indent=2),
                ),
            }],
        )
        return _safe_parse_json(response.content[0].text)

    async def generate_mutations(
        self,
        resume_json: dict,
        jd_analysis: dict,
        alignment: dict,
    ) -> list[dict]:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": MUTATION_PROMPT.format(
                    resume_json=json.dumps(resume_json, indent=2),
                    jd_analysis_json=json.dumps(jd_analysis, indent=2),
                    alignment_json=json.dumps(alignment, indent=2),
                ),
            }],
        )
        result = _safe_parse_json(response.content[0].text)
        if "changes" not in result:
            from fastapi import HTTPException
            raise HTTPException(502, "LLM response missing 'changes' key")
        return result["changes"]

    async def run_full_pipeline(
        self, resume_json: dict, jd_text: str
    ) -> OptimizationResult:
        """Execute all three stages sequentially and return the combined result."""
        jd_analysis = await self.analyze_jd(jd_text)
        alignment = await self.score_alignment(resume_json, jd_analysis)
        mutations = await self.generate_mutations(resume_json, jd_analysis, alignment)
        return OptimizationResult(
            jd_analysis=jd_analysis,
            alignment=alignment,
            mutations=mutations,
        )
