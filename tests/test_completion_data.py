"""The completion table: the shipped module's shape, and how it is mined (#127).

``src/bigfix_relevance_analyzer/_completion_data.py`` is generated from local
content checkouts by ``tools/generate_completion_data.py``. CI has no content
repos, so it cannot regenerate the table to compare; these tests pin what any
regeneration must keep -- the schema, that every row parses, that the names in
it are real -- and the generator's mining, on small repos built here.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from _helpers import REPO_ROOT, load_tool

from bigfix_relevance_analyzer import _completion_data
from bigfix_relevance_analyzer.completion.context import canonical

GENERATOR = REPO_ROOT / "tools" / "generate_completion_data.py"
KINDS = {"after-of", "whose-it", "statement-start"}

UNKNOWN_CONSUMERS = {"number"}
"""Consumers that are no property: ``number of`` is aggregation, mined because
it is the same seat for completion as any ``X of``."""


@pytest.fixture(scope="module")
def tool() -> ModuleType:
    return load_tool(GENERATOR, "_generate_completion_data")


def _rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines()]


# ---------------------------------------------------------------------------
# The shipped table
# ---------------------------------------------------------------------------


def test_the_schema_version() -> None:
    assert _completion_data.SCHEMA_VERSION == 1


def test_the_sources_name_each_repo_and_commit() -> None:
    assert _completion_data.SOURCES
    for name, commit in _completion_data.SOURCES:
        assert name and "/" not in name
        assert commit


def test_every_row_parses() -> None:
    rows = _rows(_completion_data.ROWS)
    assert len(rows) > 300
    keys = set()
    for row in rows:
        assert len(row) == 8, row
        kind, consumer, indexed, outer, producer, count, indexed_count, plural_count = row
        assert kind in KINDS, row
        assert indexed in {"0", "1"}, row
        assert consumer and producer and outer, row
        assert int(count) > 0, row
        assert 0 <= int(indexed_count) <= int(count), row
        assert 0 <= int(plural_count) <= int(count), row
        key = (kind, consumer, indexed, outer, producer)
        assert key not in keys, row
        keys.add(key)


def test_the_rows_are_sorted_so_a_regeneration_diffs_cleanly() -> None:
    lines = _completion_data.ROWS.splitlines()
    assert lines == sorted(lines)


def test_every_kind_has_rows() -> None:
    assert {row[0] for row in _rows(_completion_data.ROWS)} == KINDS


def test_statement_start_rows_have_no_consumer() -> None:
    for row in _rows(_completion_data.ROWS):
        if row[0] == "statement-start":
            assert row[1:4] == ["-", "0", "-"], row


def test_every_name_in_the_table_is_a_real_inspector() -> None:
    """A producer is offered as a completion, so it must be a name the tables
    know, written canonically. A typo mined from content must never ship."""
    for kind, consumer, _indexed, outer, producer, *_ in _rows(_completion_data.ROWS):
        assert canonical(producer) == producer, producer
        for name in {consumer, outer} - {"-"}:
            assert canonical(name) == name or name in UNKNOWN_CONSUMERS, (kind, name)


# ---------------------------------------------------------------------------
# Mining
# ---------------------------------------------------------------------------


def observed(tool: ModuleType, text: str) -> set[tuple[object, ...]]:
    return set(tool.observations(text))


def test_after_of_observations(tool: ModuleType) -> None:
    found = observed(tool, 'names of files of folders "x"')
    # (kind, consumer, indexed, outer, producer, producer indexed, producer plural)
    assert ("after-of", "name", False, None, "file", False, True) in found
    assert ("after-of", "file", False, "name", "folder", True, True) in found


def test_an_indexed_consumer(tool: ModuleType) -> None:
    found = observed(tool, 'values "x" of keys "y" of registry')
    assert ("after-of", "value", True, None, "key", True, True) in found
    assert ("after-of", "key", True, "value", "registry", False, False) in found


def test_number_of_is_a_consumer(tool: ModuleType) -> None:
    found = observed(tool, 'number of files of folder "x"')
    assert ("after-of", "number", False, None, "file", False, True) in found
    assert ("after-of", "file", False, "number", "folder", True, False) in found


def test_whose_it_observations(tool: ModuleType) -> None:
    found = observed(tool, 'exists files whose (name of it = "a" and size of it > 1) of folder "x"')
    assert ("whose-it", "file", False, None, "name", False, False) in found
    assert ("whose-it", "file", False, None, "size", False, False) in found


def test_whose_it_does_not_reach_into_a_nested_whose(tool: ModuleType) -> None:
    text = 'exists folders whose (exists files whose (size of it > 1) of it) of folder "x"'
    whose = {row for row in observed(tool, text) if row[0] == "whose-it"}
    assert ("whose-it", "file", False, None, "size", False, False) in whose
    assert all(row[1] != "folder" or row[4] != "size" for row in whose)


def test_statement_start_observations(tool: ModuleType) -> None:
    starts = {
        row[4:]
        for text in (
            'exists files of folder "x"',
            'not exists keys "x" of registry',
            "number of processes",
            'value "x" of key "y" of registry = "1"',
            '(name of operating system) and (version of client > "1")',
        )
        for row in observed(tool, text)
        if row[0] == "statement-start"
    }
    assert ("file", False, True) in starts
    assert ("key", True, True) in starts
    assert ("process", False, True) in starts
    assert ("value", True, False) in starts
    assert ("name", False, False) in starts
    assert ("version", False, False) in starts


def test_an_unknown_producer_is_not_observed(tool: ModuleType) -> None:
    found = observed(tool, 'exists files of totallybogus "x"')
    assert all(row[4] != "totallybogus" for row in found)


def test_an_unknown_consumer_is_not_observed_and_an_unknown_outer_is_none(
    tool: ModuleType,
) -> None:
    found = observed(tool, 'totallybogus of files of folder "x"')
    assert all(row[1] != "totallybogus" for row in found)
    assert ("after-of", "file", False, None, "folder", True, False) in found


def test_a_statement_that_does_not_parse_is_skipped(tool: ModuleType) -> None:
    assert observed(tool, 'exists files of "unterminated') == set()


def _repo(root: Path, files: dict[str, str]) -> Path:
    root.mkdir()
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def _load(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("_mined", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_generator_writes_a_module(tool: ModuleType, tmp_path: Path) -> None:
    same = 'exists files of folders "x"'
    one = _repo(
        tmp_path / "one",
        {"a.rel": same, "sub/b.rel": same, "c.rel": 'names of files of folder "y"'},
    )
    big = 'exists files of folder "z"' + " " * (1024 * 1024)
    two = _repo(tmp_path / "two", {"d.rel": same, "big.rel": big})
    target = tmp_path / "out.py"
    assert tool.main([str(one), str(two), "--output", str(target)]) == 0
    module = _load(target)
    assert module.SCHEMA_VERSION == 1
    assert module.SOURCES == (("one", "unknown"), ("two", "unknown"))
    rows = {tuple(row[:5]): tuple(int(n) for n in row[5:]) for row in _rows(module.ROWS)}
    # The same statement in three files and two repos counts once; the file
    # over 1 MiB is not read.
    assert rows[("after-of", "file", "0", "-", "folder")] == (1, 1, 1)
    assert rows[("after-of", "file", "0", "name", "folder")] == (1, 1, 0)
    assert rows[("after-of", "name", "0", "-", "file")] == (1, 0, 1)
    assert rows[("statement-start", "-", "0", "-", "file")] == (1, 0, 1)
    assert rows[("statement-start", "-", "0", "-", "name")] == (1, 0, 1)
    assert module.ROWS.splitlines() == sorted(module.ROWS.splitlines())
    assert "Do not edit by hand" in (module.__doc__ or "")


def test_the_generator_records_a_git_commit(tool: ModuleType, tmp_path: Path) -> None:
    repo = _repo(tmp_path / "repo", {"a.rel": 'exists files of folder "x"'})
    run = {"cwd": repo, "check": True, "capture_output": True}
    subprocess.run(["git", "init", "-q"], **run)  # type: ignore[call-overload]
    subprocess.run(["git", "add", "."], **run)  # type: ignore[call-overload]
    subprocess.run(  # type: ignore[call-overload]
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], **run
    )
    head = subprocess.run(  # type: ignore[call-overload]
        ["git", "rev-parse", "HEAD"], **run, text=True
    ).stdout.strip()
    assert tool.source_of(repo) == ("repo", head)


def test_the_generator_refuses_a_missing_repo(tool: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        tool.main([str(tmp_path / "nope"), "--output", str(tmp_path / "out.py")])


def test_the_generator_runs_as_a_script(tmp_path: Path) -> None:
    repo = _repo(tmp_path / "repo", {"a.rel": 'exists files of folder "x"'})
    target = tmp_path / "out.py"
    subprocess.run(
        [sys.executable, str(GENERATOR), str(repo), "--output", str(target)],
        check=True,
        capture_output=True,
    )
    assert "after-of\tfile\t0\t-\tfolder\t1\t1\t0" in target.read_text()
