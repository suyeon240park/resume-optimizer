"""Tests for the LaTeX parser — command discovery, section/node extraction,
and round-trip reconstruction."""

from pathlib import Path

from app.core.latex_parser import LaTeXParser, _extract_brace_arg

FIXTURE = Path(__file__).parent / "fixtures" / "jake_resume.tex"


def _load_fixture() -> str:
    return FIXTURE.read_text(encoding="utf-8")


# ------------------------------------------------------------------
# Brace extraction
# ------------------------------------------------------------------

class TestBraceExtraction:
    def test_simple(self):
        assert _extract_brace_arg("{hello}", 0) == ("hello", 7)

    def test_nested(self):
        result = _extract_brace_arg(r"{O(n \log n)}", 0)
        assert result is not None
        assert result[0] == r"O(n \log n)"

    def test_escaped_brace(self):
        result = _extract_brace_arg(r"{80\%}", 0)
        assert result is not None
        assert result[0] == r"80\%"

    def test_skip_whitespace(self):
        result = _extract_brace_arg("  {content}", 0)
        assert result is not None
        assert result[0] == "content"

    def test_no_brace(self):
        assert _extract_brace_arg("no brace", 0) is None

    def test_deeply_nested(self):
        result = _extract_brace_arg(r"{\textbf{Cloud Cost Analyzer} $|$ \emph{Python}}", 0)
        assert result is not None
        assert "Cloud Cost Analyzer" in result[0]
        assert "Python" in result[0]


# ------------------------------------------------------------------
# Command discovery
# ------------------------------------------------------------------

class TestCommandDiscovery:
    def test_discovers_custom_commands(self):
        parser = LaTeXParser(_load_fixture())
        assert "resumeSubheading" in parser.commands
        assert parser.commands["resumeSubheading"] == 4
        assert "resumeItem" in parser.commands
        assert parser.commands["resumeItem"] == 1
        assert "resumeProjectHeading" in parser.commands
        assert parser.commands["resumeProjectHeading"] == 2

    def test_excludes_environment_markers(self):
        parser = LaTeXParser(_load_fixture())
        assert "resumeSubHeadingListStart" not in parser.commands
        assert "resumeItemListStart" not in parser.commands


# ------------------------------------------------------------------
# Section extraction
# ------------------------------------------------------------------

class TestSectionExtraction:
    def test_finds_all_sections(self):
        parser = LaTeXParser(_load_fixture())
        sections = parser.extract_sections()
        names = [s.name for s in sections]
        assert "Experience" in names
        assert "Projects" in names
        assert "Skills" in names

    def test_experience_has_subheadings(self):
        parser = LaTeXParser(_load_fixture())
        sections = parser.extract_sections()
        exp = next(s for s in sections if s.name == "Experience")
        subheadings = [n for n in exp.nodes if n.command == "resumeSubheading"]
        assert len(subheadings) == 2
        assert subheadings[0].args[0] == "Software Developer"
        assert subheadings[1].args[0] == "Backend Developer Intern"

    def test_items_nested_under_subheading(self):
        parser = LaTeXParser(_load_fixture())
        sections = parser.extract_sections()
        exp = next(s for s in sections if s.name == "Experience")
        first_sub = next(n for n in exp.nodes if n.command == "resumeSubheading")
        assert len(first_sub.children) == 2
        assert "data pipeline" in first_sub.children[0].args[0]
        assert "container memory" in first_sub.children[1].args[0]

    def test_project_heading_with_nested_braces(self):
        parser = LaTeXParser(_load_fixture())
        sections = parser.extract_sections()
        proj = next(s for s in sections if s.name == "Projects")
        heading = next(n for n in proj.nodes if n.command == "resumeProjectHeading")
        assert "Cloud Cost Analyzer" in heading.args[0]

    def test_nested_braces_in_item(self):
        parser = LaTeXParser(_load_fixture())
        sections = parser.extract_sections()
        proj = next(s for s in sections if s.name == "Projects")
        heading = next(n for n in proj.nodes if n.command == "resumeProjectHeading")
        anomaly_item = heading.children[1]
        assert r"O(n \log n)" in anomaly_item.args[0]


# ------------------------------------------------------------------
# Reconstruction (round-trip)
# ------------------------------------------------------------------

class TestReconstruction:
    def test_replace_single_node(self):
        source = _load_fixture()
        parser = LaTeXParser(source)
        sections = parser.extract_sections()
        exp = next(s for s in sections if s.name == "Experience")
        first_sub = next(n for n in exp.nodes if n.command == "resumeSubheading")
        first_item = first_sub.children[0]

        new_text = "Engineered a high-throughput streaming pipeline processing 5M events/day with Kafka and Flink"
        new_source = parser.replace_node(first_item, [new_text])

        assert new_text in new_source
        assert first_item.args[0] not in new_source
        # Everything else untouched
        assert "Reduced container memory" in new_source
        assert r"\documentclass" in new_source

    def test_apply_multiple_mutations(self):
        source = _load_fixture()
        parser = LaTeXParser(source)
        sections = parser.extract_sections()
        exp = next(s for s in sections if s.name == "Experience")
        first_sub = next(n for n in exp.nodes if n.command == "resumeSubheading")

        new_bullet_1 = "New bullet one"
        new_bullet_2 = "New bullet two"

        mutations = [
            (first_sub.children[0], [new_bullet_1]),
            (first_sub.children[1], [new_bullet_2]),
        ]
        new_source = parser.apply_mutations(mutations)

        assert new_bullet_1 in new_source
        assert new_bullet_2 in new_source
        assert first_sub.children[0].args[0] not in new_source
        assert first_sub.children[1].args[0] not in new_source

    def test_to_json_serialisable(self):
        parser = LaTeXParser(_load_fixture())
        data = parser.to_json()
        assert isinstance(data, list)
        assert all("name" in s and "entries" in s for s in data)
