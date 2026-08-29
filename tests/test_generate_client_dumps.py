"""The two traps in capturing a dump from ``QnA``, held to fixture transcripts.

``tools/generate_client_dumps.py`` needs a real engine to do its job, so only
the pure parts are testable here -- which is fine, because both known ways to
produce a plausible-looking-but-wrong dump live in those parts:

* the ``Q: `` prompt has no trailing newline, so the first answer of a query
  arrives fused onto the prompt and a naive filter drops exactly one row;
* the output is percent-encoded, and an undecoded ``%25`` once reached three
  committed dumps and became a second, bogus ``%`` operator in the shipped
  tables.

The transcripts below are shaped like real ``QnA`` output. Style follows
``tests/test_inspector_data.py``, which loads its generator the same way.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "tools" / "generate_client_dumps.py"

# One query's worth of transcript: the prompt fused onto the first answer, an
# encoded `%` in the second, and a timing line to ignore.
TRANSCRIPT = (
    "Q: A: <integer> + <integer>: integer\tplus\t+\tinteger\tinteger\tinteger\n"
    "A: <integer> %25 <integer>: integer\tmod\t%25\tinteger\tinteger\tinteger\n"
    "T: 0.302 ms\n"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_generate_client_dumps", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tool() -> ModuleType:
    return _load()


def test_the_first_answer_is_not_lost_to_the_prompt(tool: ModuleType) -> None:
    """`Q: ` has no trailing newline, so answer one shares its line.

    A `startswith("A: ")` filter drops exactly one row per category, which is
    invisible in the output and visible only in the count.
    """
    rows = tool.answers(TRANSCRIPT)
    assert len(rows) == 2
    assert rows[0].startswith("<integer> + <integer>: integer\t")


def test_percent_encoding_is_decoded(tool: ModuleType) -> None:
    """`mod` is `%`, not `%25`. Undecoded it becomes a second operator."""
    assert tool.answers(TRANSCRIPT)[1] == (
        "<integer> % <integer>: integer\tmod\t%\tinteger\tinteger\tinteger"
    )


def test_a_tab_arrives_as_a_real_tab(tool: ModuleType) -> None:
    """`character 9` in the query, `%09` on the wire, a tab in the file."""
    assert tool.answers("A: a%09b") == ["a\tb"]


def test_an_error_answer_stops_the_capture(tool: ModuleType) -> None:
    """A partial table that looks complete is worse than no table."""
    with pytest.raises(tool.QnaError, match="not defined"):
        tool.answers('A: fine\nE: The operator "bogus" is not defined.\n')


def test_notices_and_timings_are_not_rows(tool: ModuleType) -> None:
    assert tool.answers("I: connected\nA: only\nT: 0.1 ms\n") == ["only"]


def test_the_engines_own_count_is_read_back(tool: ModuleType) -> None:
    assert tool.expected_count(["376"]) == 376
    with pytest.raises(tool.QnaError):
        tool.expected_count(["376", "377"])
    with pytest.raises(tool.QnaError):
        tool.expected_count(["not a number"])


def test_the_rendered_dump_is_one_row_per_line(tool: ModuleType) -> None:
    assert tool.render(["a", "b"]) == "a\nb\n"


def test_every_category_has_both_a_capture_and_a_count_query(tool: ModuleType) -> None:
    """The count check is what catches the dropped first row, so no category
    may have a capture query without one."""
    assert set(tool.QUERIES) == set(tool.COUNTS)
    assert set(tool.QUERIES) == {
        "binary_operators",
        "casts",
        "properties",
        "types",
        "unary_operators",
    }


def test_the_queries_match_the_dump_readmes_recipe(tool: ModuleType) -> None:
    """The README is the record of what produced the committed dumps; drift
    between it and this script would silently change the format."""
    readme = (REPO_ROOT / "tests" / "examples" / "relevance_inspectors" / "README.md").read_text(
        encoding="utf-8"
    )
    for category, query in tool.QUERIES.items():
        assert query in readme, f"{category}: query is not the one the README documents"
