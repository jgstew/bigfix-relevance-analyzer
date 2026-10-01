"""Small helpers and fixed statements shared across test modules.

The statements are shared because several modules pin the same behaviour
through different entry points (the library, ``__main__``, the lint CLI); one
spelling keeps a change to the example from silently testing two different
things.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

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

BES_EXAMPLE = REPO_ROOT / "tests/examples/mixed_context/task_with_client_and_session_relevance.bes"
"""A real document with both a client and a session site. Anchored on this file
rather than the working directory, so the suite also runs from inside ``tests/``."""


def write(directory: Path, name: str, text: str) -> Path:
    """Write ``text`` to ``directory / name`` and return the path."""
    path = directory / name
    path.write_text(text)
    return path


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
