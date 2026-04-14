"""
LaTeX compilation service — writes .tex to a work directory, invokes
pdflatex, and reads back the resulting PDF.
"""

from __future__ import annotations

import asyncio
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from app.config import get_settings


@dataclass
class CompilationError:
    line: int | None
    message: str


@dataclass
class CompilationResult:
    success: bool
    pdf_bytes: bytes | None = None
    errors: list[CompilationError] = field(default_factory=list)
    log: str = ""


def _parse_log_errors(log_text: str) -> list[CompilationError]:
    """Extract error lines from pdflatex log output."""
    errors: list[CompilationError] = []
    for m in re.finditer(r"^! (.+)$", log_text, re.MULTILINE):
        line_num = None
        line_match = re.search(r"l\.(\d+)", log_text[m.end() : m.end() + 200])
        if line_match:
            line_num = int(line_match.group(1))
        errors.append(CompilationError(line=line_num, message=m.group(1)))
    return errors


async def compile_latex(latex_source: str) -> CompilationResult:
    """
    Compile a LaTeX source string to PDF.

    Writes the source to ``LATEX_COMPILE_DIR/<job_id>.tex``, runs
    ``pdflatex`` twice (for cross-references), reads the PDF, and
    cleans up.
    """
    settings = get_settings()
    work_dir = Path(settings.latex_compile_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    job_id = uuid.uuid4().hex
    tex_path = work_dir / f"{job_id}.tex"
    pdf_path = work_dir / f"{job_id}.pdf"
    log_path = work_dir / f"{job_id}.log"

    tex_path.write_text(latex_source, encoding="utf-8")

    try:
        # Run pdflatex twice for references / page numbers
        for _ in range(2):
            proc = await asyncio.create_subprocess_exec(
                "pdflatex",
                "-no-shell-escape",
                "-interaction=nonstopmode",
                f"-output-directory={work_dir}",
                str(tex_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()

        log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        errors = _parse_log_errors(log_text)

        if pdf_path.exists():
            pdf_bytes = pdf_path.read_bytes()
            return CompilationResult(success=True, pdf_bytes=pdf_bytes, errors=errors, log=log_text)

        return CompilationResult(success=False, errors=errors or [CompilationError(line=None, message="PDF not generated")], log=log_text)

    finally:
        for ext in (".tex", ".pdf", ".log", ".aux", ".out", ".fls", ".fdb_latexmk"):
            p = work_dir / f"{job_id}{ext}"
            if p.exists():
                p.unlink()
