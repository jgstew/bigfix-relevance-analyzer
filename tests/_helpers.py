"""Small helpers and fixed statements shared across test modules.

The statements are shared because several modules pin the same behaviour
through different entry points (the library, ``__main__``, the lint CLI); one
spelling keeps a change to the example from silently testing two different
things.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
"""A clean client statement: parses, type-checks, nothing to report."""

BROKEN = 'exists file "unterminated'
"""A statement that does not lex: an unterminated string."""

UNKNOWN_INSPECTOR = "totally bogus made up inspector"
"""A name no dump defines."""

MIXED_DIALECT = '(exists files of folders "/") AND (exists bes computers)'
"""Client-only and session-only inspectors in one statement."""

SETTING = 'exists values of setting "x" of client'
"""A singular spelling mid-chain, which the plural autofix rewrites to ``settings``."""

MID_CHAIN = "singular-spelling-mid-chain"
"""The checker code :data:`SETTING` raises."""

BES_BROKEN = (
    '<?xml version="1.0" encoding="UTF-8"?>\n<BES>\n<Task>\n'
    f"\t<Relevance>{BROKEN}</Relevance>\n"
    f"\t<Relevance>{SETTING}</Relevance>\n"
    "</Task>\n</BES>\n"
)
"""A task with :data:`BROKEN` on line 3 and the fixable :data:`SETTING` on line 4
(LSP lines, 0-based): what a fixlet pasted into an unsaved tab looks like."""

BES_EXAMPLE = REPO_ROOT / "tests/examples/mixed_context/task_with_client_and_session_relevance.bes"
"""A real document with both a client and a session site. Anchored on this file
rather than the working directory, so the suite also runs from inside ``tests/``."""


def write(directory: Path, name: str, text: str) -> Path:
    """Write ``text`` to ``directory / name`` and return the path."""
    path = directory / name
    path.write_text(text)
    return path


def golden_text(path: Path, actual: str) -> str:
    """The pinned contents of the golden file ``path``, to compare ``actual`` with.

    With ``UPDATE_GOLDEN`` set in the environment, ``actual`` is written to
    ``path`` instead and the test fails, so a regeneration is never mistaken
    for a pass: review the diff, then rerun without it. Every golden in the
    suite goes through here, so regenerating one works like regenerating any.
    """
    if os.environ.get("UPDATE_GOLDEN"):
        path.write_text(actual, encoding="utf-8")
        pytest.fail(f"{path.name} rewritten -- review the diff, then rerun without UPDATE_GOLDEN")
    assert path.is_file(), f"missing {path}; regenerate with UPDATE_GOLDEN=1"
    return path.read_text(encoding="utf-8")


Position = tuple[int, int]
"""An LSP position, ``(line, character)``: 0-based, the character in UTF-16 units."""


def lsp_lines(buffer: str) -> tuple[list[str], list[str]]:
    """``buffer``'s lines and the breaks after them, split only where LSP splits:
    ``\r\n``, ``\r`` and ``\n``, unlike :meth:`str.splitlines`."""
    pieces = re.split(r"(\r\n|\r|\n)", buffer)
    return pieces[0::2], pieces[1::2]


def _code_point_index(line: str, character: int) -> int:
    """Where UTF-16 offset ``character`` falls in ``line``, in code points."""
    units = 0
    for index, char in enumerate(line):
        if units == character:
            return index
        assert units < character, f"character {character} is inside a surrogate pair"
        units += 2 if ord(char) > 0xFFFF else 1
    assert units == character, f"character {character} is past the end of {line!r}"
    return len(line)


def lsp_text(buffer: str, start: Position, end: Position) -> str:
    """What ``buffer`` holds between two LSP positions, line breaks as written."""
    lines, breaks = lsp_lines(buffer)
    (start_line, start_char), (end_line, end_char) = start, end
    first = _code_point_index(lines[start_line], start_char)
    last = _code_point_index(lines[end_line], end_char)
    if start_line == end_line:
        return lines[start_line][first:last]
    middle = "".join(lines[i] + breaks[i] for i in range(start_line + 1, end_line))
    return lines[start_line][first:] + breaks[start_line] + middle + lines[end_line][:last]


def diagnostic_text(buffer: str, diagnostic: dict[str, Any]) -> str:
    """What ``buffer`` holds over an LSP diagnostic's range."""
    start, end = diagnostic["range"]["start"], diagnostic["range"]["end"]
    return lsp_text(buffer, (start["line"], start["character"]), (end["line"], end["character"]))


def load_tool(path: Path, name: str) -> ModuleType:
    """Import a ``tools/`` script, which lives outside any package, by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_fresh_python(script: str) -> None:
    """Run ``script`` in a new interpreter and require it to print exactly ``ok``.

    For assertions about import-time state -- what is loaded or cached before
    anything is asked -- which this already-warm test process cannot observe.
    """
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "ok"
