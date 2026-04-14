"""Post-optimization ATS keyword-match scorer."""

from __future__ import annotations

# Common synonyms / aliases for tech terms so partial matches still count.
_SYNONYM_MAP: dict[str, list[str]] = {
    "javascript": ["js"],
    "typescript": ["ts"],
    "python": ["py"],
    "kubernetes": ["k8s"],
    "postgresql": ["postgres"],
    "amazon web services": ["aws"],
    "google cloud platform": ["gcp"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"],
    "ci/cd": ["cicd", "continuous integration", "continuous deployment"],
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "natural language processing": ["nlp"],
    "react.js": ["react", "reactjs"],
    "node.js": ["node", "nodejs"],
    "vue.js": ["vue", "vuejs"],
    "next.js": ["next", "nextjs"],
    "rest api": ["restful api", "rest apis"],
}


def get_synonyms(keyword: str) -> list[str]:
    """Return known synonyms for a keyword (case-insensitive)."""
    key = keyword.lower()
    synonyms = _SYNONYM_MAP.get(key, [])
    for canonical, aliases in _SYNONYM_MAP.items():
        if key in aliases:
            synonyms.append(canonical)
    return synonyms


def calculate_ats_score(resume_text: str, jd_analysis: dict) -> dict:
    """
    Score a resume's text against the required_skills from a JD analysis.

    Returns a breakdown of matched / partial / missing keywords and an
    overall 0–100 score.
    """
    resume_lower = resume_text.lower()
    required_skills: list[dict] = jd_analysis.get("required_skills", [])

    matched: list[dict] = []
    partial: list[dict] = []
    missing: list[dict] = []

    for skill in required_skills:
        if not isinstance(skill, dict) or "skill" not in skill:
            continue
        keyword = skill["skill"].lower()
        if keyword in resume_lower:
            matched.append(skill)
        elif any(syn in resume_lower for syn in get_synonyms(keyword)):
            partial.append(skill)
        else:
            missing.append(skill)

    total = len(required_skills)
    matched_score = len(matched) + 0.5 * len(partial)
    score = round((matched_score / total) * 100, 1) if total > 0 else 0.0

    return {
        "score": score,
        "matched": matched,
        "partial": partial,
        "missing": missing,
    }
