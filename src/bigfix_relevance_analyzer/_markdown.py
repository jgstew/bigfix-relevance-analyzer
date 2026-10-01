"""Markdown helpers shared by the CLI's reports and the generated reference.

A neutral module of its own: ``__main__`` imports
:mod:`~bigfix_relevance_analyzer.reference` only inside the one function that
needs it, so the two cannot share helpers by importing each other.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

__all__: list[str] = []


def escape_cell(text: str) -> str:
    """Make ``text`` safe inside a Markdown table cell.

    ``|`` is a real relevance operator -- error fallback -- and would otherwise
    be read as a column break even inside a code span, which is a GFM quirk
    rather than an oversight here.
    """
    return text.replace("|", "\\|")


def code_cell(text: str, *, max_len: int | None = None) -> str:
    """``text`` as an escaped code span for a table cell.

    With ``max_len``, relevance source is also made table-friendly: it can run
    to hundreds of characters (a ``whose`` context can be the entire outer
    expression) and carry its own newlines, so whitespace is collapsed onto one
    line and anything longer than ``max_len`` is truncated with ``...``.
    """
    if max_len is not None:
        text = " ".join(text.split())
        if len(text) > max_len:
            text = text[: max_len - 1] + "..."
    return f"`{escape_cell(text)}`"


def capped(cells: Iterable[str], *, limit: int = 3) -> str:
    """The first ``limit`` of ``cells``, comma-joined, with `` ...`` when more were cut."""
    listed = list(cells)
    shown = ", ".join(listed[:limit])
    return shown + " ..." if len(listed) > limit else shown


def table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """One GFM table. Empty rows yield an empty string, not a headerless table."""
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)
