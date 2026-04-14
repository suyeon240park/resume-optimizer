"""
LaTeX resume parser — extracts a content AST from a .tex file without
disturbing formatting.  Supports arbitrary custom commands defined via
\\newcommand and handles nested braces in arguments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ContentNode:
    command: str
    args: list[str]
    children: list[ContentNode] = field(default_factory=list)
    source_start: int = 0
    source_end: int = 0

    def to_dict(self) -> dict:
        d: dict = {
            "command": self.command,
            "args": self.args,
            "source_range": [self.source_start, self.source_end],
        }
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d


@dataclass
class Section:
    name: str
    nodes: list[ContentNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "entries": [n.to_dict() for n in self.nodes],
        }


def _extract_brace_arg(source: str, pos: int) -> tuple[str, int] | None:
    """
    Starting at *pos*, skip whitespace then extract the content of a
    ``{...}`` group, correctly handling nested braces.
    Returns ``(content, end_pos)`` where *end_pos* is one past the
    closing brace, or ``None`` if no opening brace is found.
    """
    i = pos
    while i < len(source) and source[i] in (" ", "\t", "\n", "\r"):
        i += 1
    if i >= len(source) or source[i] != "{":
        return None
    depth = 0
    start = i + 1
    while i < len(source):
        ch = source[i]
        if ch == "\\" and i + 1 < len(source):
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start:i], i + 1
        i += 1
    return None


class LaTeXParser:
    """
    Parses a LaTeX resume into a content tree.

    1. Discovers custom commands from ``\\newcommand`` definitions.
    2. Extracts ``\\section`` boundaries.
    3. Within each section, finds all invocations of registered commands
       and builds a tree of ``ContentNode`` objects with source offsets.
    """

    # Commands from the Jake Gutierrez template that are always recognised
    # even if their \\newcommand appears inside a \\makeatletter block or
    # is otherwise hard to regex.
    BUILTIN_COMMANDS: dict[str, int] = {
        "resumeSubheading": 4,
        "resumeItem": 1,
        "resumeProjectHeading": 2,
        "resumeSubItem": 1,
    }

    # Environment markers we skip over (not content)
    ENVIRONMENT_MARKERS = {
        "resumeSubHeadingListStart",
        "resumeSubHeadingListEnd",
        "resumeItemListStart",
        "resumeItemListEnd",
    }

    # Commands whose children are the \\resumeItem nodes that follow them
    # before the next heading-level command or list-end marker.
    HEADING_COMMANDS = {"resumeSubheading", "resumeProjectHeading"}

    def __init__(self, source: str):
        self.source = source
        self.commands: dict[str, int] = dict(self.BUILTIN_COMMANDS)
        self._discover_commands()

    def _discover_commands(self) -> None:
        """Scan for ``\\newcommand`` / ``\\renewcommand`` and extract arity."""
        pattern = r"\\(?:re)?newcommand\{\\(\w+)\}\s*\[(\d+)\]"
        for m in re.finditer(pattern, self.source):
            name = m.group(1)
            if name not in self.ENVIRONMENT_MARKERS:
                self.commands[name] = int(m.group(2))

    def _body_range(self) -> tuple[int, int]:
        """Return (start, end) byte offsets of the document body."""
        begin = re.search(r"\\begin\{document\}", self.source)
        end = re.search(r"\\end\{document\}", self.source)
        start = begin.end() if begin else 0
        stop = end.start() if end else len(self.source)
        return start, stop

    def extract_sections(self) -> list[Section]:
        """Extract all ``\\section{...}`` blocks and their child content nodes."""
        body_start, body_end = self._body_range()
        body = self.source[body_start:body_end]

        section_pat = re.compile(r"\\section\{([^}]*)\}")
        matches = list(section_pat.finditer(body))

        sections: list[Section] = []
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            block = body[start:end]
            section = Section(name=m.group(1))
            section.nodes = self._extract_nodes(block, offset=body_start + start)
            section.nodes = self._nest_items(section.nodes)
            sections.append(section)

        return sections

    def _extract_nodes(self, block: str, offset: int) -> list[ContentNode]:
        """
        Extract all registered command invocations from a text block,
        using brace-aware argument extraction.
        """
        nodes: list[ContentNode] = []
        cmd_pattern = re.compile(r"\\(" + "|".join(re.escape(c) for c in self.commands) + r")(?![a-zA-Z])")

        for m in cmd_pattern.finditer(block):
            cmd_name = m.group(1)
            if cmd_name in self.ENVIRONMENT_MARKERS:
                continue
            arg_count = self.commands[cmd_name]
            args: list[str] = []
            pos = m.end()
            valid = True
            for _ in range(arg_count):
                result = _extract_brace_arg(block, pos)
                if result is None:
                    valid = False
                    break
                arg_text, pos = result
                args.append(arg_text)
            if not valid:
                continue
            node = ContentNode(
                command=cmd_name,
                args=args,
                source_start=offset + m.start(),
                source_end=offset + (pos - 0),
            )
            nodes.append(node)

        # Sort by source position
        nodes.sort(key=lambda n: n.source_start)
        return nodes

    def _nest_items(self, flat_nodes: list[ContentNode]) -> list[ContentNode]:
        """
        Group ``\\resumeItem`` / ``\\resumeSubItem`` nodes as children
        of the preceding heading-level node.
        """
        result: list[ContentNode] = []
        current_heading: ContentNode | None = None

        for node in flat_nodes:
            if node.command in self.HEADING_COMMANDS:
                current_heading = node
                result.append(node)
            elif node.command in ("resumeItem", "resumeSubItem"):
                if current_heading is not None:
                    current_heading.children.append(node)
                else:
                    result.append(node)
            else:
                result.append(node)

        return result

    def to_json(self) -> list[dict]:
        """Return the full AST as a JSON-serialisable list."""
        return [s.to_dict() for s in self.extract_sections()]

    def replace_node(self, node: ContentNode, new_args: list[str]) -> str:
        """
        Replace a single content node's arguments in the source,
        preserving the command name and all surrounding formatting.
        """
        rebuilt = f"\\{node.command}" + "".join(f"{{{a}}}" for a in new_args)
        return self.source[: node.source_start] + rebuilt + self.source[node.source_end :]

    def apply_mutations(self, mutations: list[tuple[ContentNode, list[str]]]) -> str:
        """
        Apply multiple node replacements.  Processes in reverse source order
        so earlier offsets remain valid.
        """
        sorted_muts = sorted(mutations, key=lambda m: m[0].source_start, reverse=True)
        result = self.source
        for node, new_args in sorted_muts:
            rebuilt = f"\\{node.command}" + "".join(f"{{{a}}}" for a in new_args)
            result = result[: node.source_start] + rebuilt + result[node.source_end :]
        return result
