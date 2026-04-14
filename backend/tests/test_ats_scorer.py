"""Tests for ATS keyword scoring."""

from app.core.ats_scorer import calculate_ats_score, get_synonyms


class TestGetSynonyms:
    def test_direct_lookup(self):
        assert "k8s" in get_synonyms("kubernetes")

    def test_reverse_lookup(self):
        assert "kubernetes" in get_synonyms("k8s")

    def test_no_synonyms(self):
        assert get_synonyms("obscurelang") == []

    def test_case_insensitive(self):
        assert "k8s" in get_synonyms("Kubernetes")


class TestATSScore:
    def _jd(self, skills: list[dict]) -> dict:
        return {"required_skills": skills}

    def test_perfect_match(self):
        resume = "I use Python and Docker every day."
        jd = self._jd([
            {"skill": "Python", "category": "language", "importance": "critical"},
            {"skill": "Docker", "category": "tool", "importance": "critical"},
        ])
        result = calculate_ats_score(resume, jd)
        assert result["score"] == 100.0
        assert len(result["matched"]) == 2
        assert len(result["missing"]) == 0

    def test_partial_via_synonym(self):
        resume = "Deployed services on K8s clusters."
        jd = self._jd([
            {"skill": "Kubernetes", "category": "tool", "importance": "critical"},
        ])
        result = calculate_ats_score(resume, jd)
        assert len(result["partial"]) == 1
        assert result["score"] == 50.0

    def test_missing_skill(self):
        resume = "I write Java code."
        jd = self._jd([
            {"skill": "Rust", "category": "language", "importance": "critical"},
        ])
        result = calculate_ats_score(resume, jd)
        assert len(result["missing"]) == 1
        assert result["score"] == 0.0

    def test_mixed(self):
        resume = "Experienced with Python, AWS, and CI/CD pipelines."
        jd = self._jd([
            {"skill": "Python", "category": "language", "importance": "critical"},
            {"skill": "Amazon Web Services", "category": "tool", "importance": "critical"},
            {"skill": "Go", "category": "language", "importance": "preferred"},
        ])
        result = calculate_ats_score(resume, jd)
        assert len(result["matched"]) == 1  # Python
        assert len(result["partial"]) == 1  # AWS via synonym
        assert len(result["missing"]) == 1  # Go
        expected = round((1 + 0.5) / 3 * 100, 1)
        assert result["score"] == expected

    def test_empty_jd(self):
        result = calculate_ats_score("anything", {"required_skills": []})
        assert result["score"] == 0.0
