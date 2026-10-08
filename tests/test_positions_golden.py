"""Where findings land, pinned over real files: in an editor and through the API.

Two goldens, over the example corpus plus the contract fixtures in
``tests/golden/pre_commit_bigfix/`` -- the same inputs
:mod:`test_downstream_pre_commit_bigfix` pins the hook's report over:

* ``lsp_diagnostics.json``: every diagnostic
  :class:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter` publishes for
  each file, opened the way an editor holds it (line endings as written). A
  change to an editor range is meant to show up here as a reviewable diff.
* ``finding_lines.json``: ``(code, line, site line)`` for every
  :class:`~bigfix_relevance_analyzer.lint.Finding`, under the default config
  and under ``suggest=True`` (the editor's). ``Finding.line`` is an API
  consumers depend on -- pre-commit-bigfix prints it -- so unlike the editor
  ranges, this one is not expected to change at all.

Regenerate deliberately, and read the diff::

    UPDATE_GOLDEN=1 uv run pytest tests/test_positions_golden.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from bigfix_relevance_analyzer.extract import _is_recognized
from bigfix_relevance_analyzer.lint import LintConfig, lint_file
from bigfix_relevance_analyzer.lsp.linter import DocumentLinter

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
LSP_GOLDEN = GOLDEN_DIR / "lsp_diagnostics.json"
LINES_GOLDEN = GOLDEN_DIR / "finding_lines.json"
ROOTS = ("tests/examples", "tests/golden/pre_commit_bigfix")

CONFIGS = {"default": LintConfig(), "suggest": LintConfig(suggest=True)}


def _files() -> list[str]:
    return sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for root in ROOTS
        for path in (REPO_ROOT / root).rglob("*")
        if path.is_file() and _is_recognized(path)
    )


def _buffer(relative: str) -> str:
    """The file as an editor buffer holds it: decoded, line endings untouched."""
    return (REPO_ROOT / relative).read_bytes().decode("utf-8")


def _diagnostics() -> dict[str, Any]:
    return {
        relative: DocumentLinter().diagnostics(f"file:///workspace/{relative}", _buffer(relative))
        for relative in _files()
    }


def _finding_lines() -> dict[str, Any]:
    return {
        name: {
            relative: [
                [finding.code, finding.line, None if finding.site is None else finding.site.line]
                for finding in lint_file(REPO_ROOT / relative, config)
            ]
            for relative in _files()
        }
        for name, config in CONFIGS.items()
    }


def _dump(value: Any, indent: str = "") -> str:
    """JSON with one diagnostic (or finding) per line, so a diff reads per item."""
    if (
        isinstance(value, dict)
        and value
        and all(isinstance(v, (dict, list)) for v in value.values())
    ):
        inner = indent + "  "
        items = ",\n".join(
            f"{inner}{json.dumps(key)}: {_dump(value[key], inner).lstrip()}"
            for key in sorted(value)
        )
        return f"{indent}{{\n{items}\n{indent}}}"
    if isinstance(value, list) and value:
        inner = indent + "  "
        items = ",\n".join(f"{inner}{json.dumps(item, sort_keys=True)}" for item in value)
        return f"{indent}[\n{items}\n{indent}]"
    return f"{indent}{json.dumps(value, sort_keys=True)}"


def _check(golden: Path, actual: dict[str, Any]) -> None:
    if os.environ.get("UPDATE_GOLDEN"):
        golden.write_text(_dump(actual) + "\n", encoding="utf-8")
        pytest.fail(f"{golden.name} rewritten -- review the diff, then rerun without UPDATE_GOLDEN")
    assert golden.is_file(), f"missing {golden}; regenerate with UPDATE_GOLDEN=1"
    expected = json.loads(golden.read_text(encoding="utf-8"))
    actual = json.loads(json.dumps(actual))
    # Key by key, so a failure names the file that moved.
    for key in expected:
        assert actual.get(key) == expected[key], f"{golden.name}: {key} changed"
    assert set(actual) == set(expected), f"{golden.name}: the set of pinned files changed"


def test_the_inputs_cover_every_contract_fixture() -> None:
    files = _files()
    assert {
        "tests/golden/pre_commit_bigfix/notes.md",
        "tests/golden/pre_commit_bigfix/page.html",
        "tests/golden/pre_commit_bigfix/task_errors.bes",
        "tests/golden/pre_commit_bigfix/whole_file.rel",
    } <= set(files)
    # The CRLF fixture is what makes the editor buffer differ from the
    # decoded text extraction sees; it must stay CRLF to be worth pinning.
    assert "\r\n" in _buffer("tests/golden/pre_commit_bigfix/task_errors.bes")


def test_editor_diagnostics_are_unchanged() -> None:
    _check(LSP_GOLDEN, _diagnostics())


def test_finding_lines_are_unchanged() -> None:
    _check(LINES_GOLDEN, _finding_lines())
