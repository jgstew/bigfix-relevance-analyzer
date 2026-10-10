"""Tests for :mod:`bigfix_relevance_analyzer.completion.rank`: what fits a
context, in the order real content uses it (#127).

Contexts are built here by hand, not scanned: ranking reads only the
:class:`~bigfix_relevance_analyzer.completion.context.CompletionContext`, and
building it directly is what proves that a second producer of contexts (a
recovering parser) can use ranking unchanged.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _helpers import REPO_ROOT, load_tool

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.completion.context import CompletionContext, scan_context
from bigfix_relevance_analyzer.completion.rank import (
    Candidate,
    CompletionTable,
    TableRow,
    default_table,
    rank,
)
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.typecheck import TypeEnvironment

CLIENT = TypeEnvironment.create(Dialect.CLIENT)
SESSION = TypeEnvironment.create(Dialect.SESSION)


def context_at(prefix: str, dialect: Dialect | None = None) -> CompletionContext:
    text = prefix.rstrip()
    found = scan_context(text, len(text), text != prefix, dialect)
    assert found is not None, prefix
    return found


def names(candidates: list[Candidate]) -> list[str]:
    return [candidate.name for candidate in candidates]


def labels(candidates: list[Candidate]) -> list[str]:
    return [candidate.label for candidate in candidates]


# ---------------------------------------------------------------------------
# after `X of`
# ---------------------------------------------------------------------------


def test_files_of_offers_folders_first() -> None:
    found = rank(context_at("files of "), CLIENT)
    assert found[0].name == "folder"
    assert found[0].label == "folders"
    top = names(found[:10])
    assert "csidl folder" in top
    assert {"windows folder", "data folder"} <= set(names(found[:15]))


def test_every_candidate_after_files_of_returns_a_folder_or_was_seen() -> None:
    found = rank(context_at("files of "), CLIENT, limit=500)
    seen = {row.producer for row in default_table().rows if row.consumer == "file"}
    for candidate in found:
        rows = inspectors.lookup(candidate.name, kind=inspectors.InspectorKind.PROPERTY)
        returns = {ancestor for row in rows for ancestor in inspectors.ancestors(row.return_type)}
        assert candidate.name in seen or returns & {"folder", "service"}, candidate


def test_name_of_offers_the_operating_system_first() -> None:
    assert rank(context_at("name of "), CLIENT)[0].name == "operating system"


def test_an_indexed_key_offers_the_registries() -> None:
    """With no outer consumer, ``key "x" of`` is most often an ini file's
    ``key "x" of section "y" of file``; the registries follow, from the
    consumer and index flag without the outer one."""
    top = names(rank(context_at('key "x" of '), CLIENT)[:8])
    assert top[0] == "section"
    assert {"registry", "x64 registry", "x32 registry"} <= set(top)
    # Under `value of`, it is the registry: the outer consumer decides.
    assert names(rank(context_at('value "a" of key "x" of '), CLIENT))[0] == "registry"


def test_the_outer_consumer_refines_the_order() -> None:
    plain = names(rank(context_at("files of "), CLIENT))
    under_pathname = names(rank(context_at("pathnames of files of "), CLIENT))
    assert plain[0] == "folder"
    assert under_pathname[0] == "csidl folder"


def test_an_unknown_consumer_falls_back_to_the_overall_order() -> None:
    found = rank(context_at("totally bogus of "), CLIENT)
    assert found
    overall = default_table().producer_counts("after-of")
    counts = [overall.get(candidate.name, 0) for candidate in found]
    assert counts == sorted(counts, reverse=True)


def _has_session_rows(name: str) -> bool:
    rows = inspectors.lookup(name, kind=inspectors.InspectorKind.PROPERTY)
    return any(Dialect.SESSION in row.dialects for row in rows)


def test_a_session_context_offers_no_client_only_rows() -> None:
    found = rank(context_at("names of "), SESSION, limit=500)
    assert found
    assert all(_has_session_rows(candidate.name) for candidate in found)
    client_only = {
        candidate.name
        for candidate in rank(context_at("names of "), CLIENT, limit=500)
        if not _has_session_rows(candidate.name)
    }
    assert {"drive", "process"} <= client_only
    assert not client_only & set(names(found))
    # Offered, though not near the top: the table's counts are not split by
    # dialect, and its 390 session pairs rarely write `names of bes computers`.
    assert "bes computer" in names(found)


def test_several_environments_offer_what_any_of_them_allows() -> None:
    both = names(rank(context_at("names of "), (CLIENT, SESSION), limit=500))
    assert "operating system" in both
    assert "bes computer" in both


def test_a_platform_drops_what_it_cannot_evaluate() -> None:
    windows = TypeEnvironment.create(Dialect.CLIENT, "windows")
    assert "apple extras folder" in names(rank(context_at("files of "), CLIENT, limit=500))
    assert "apple extras folder" not in names(rank(context_at("files of "), windows, limit=500))


def test_the_partial_word_filters_by_the_start_of_any_word() -> None:
    found = rank(context_at("files of fold"), CLIENT, limit=500)
    assert found[0].name == "folder"
    assert "data folder" in names(found)
    assert "registry" not in names(found)
    for candidate in found:
        words = (candidate.label + " " + candidate.name).lower().split()
        assert any(word.startswith("fold") for word in words), candidate


def test_a_multi_word_partial_filters_by_the_start_of_the_name() -> None:
    found = rank(context_at("names of bes c"), (CLIENT, SESSION), limit=500)
    assert "bes computer" in names(found)
    assert all(
        candidate.label.startswith("bes c") or candidate.name.startswith("bes c")
        for candidate in found
    )
    # A space after a whole name still offers the longer names it starts.
    longer = rank(context_at("files of folder "), CLIENT)
    assert "folder ending in" in names(longer)
    assert all(candidate.name.startswith("folder ") for candidate in longer)


def test_the_partial_word_is_case_insensitive() -> None:
    assert names(rank(context_at("files of FOLD"), CLIENT))[0] == "folder"


def test_the_ranks_are_the_positions() -> None:
    found = rank(context_at("files of "), CLIENT)
    assert [candidate.rank for candidate in found] == list(range(len(found)))


def test_the_limit() -> None:
    assert len(rank(context_at("files of "), CLIENT, limit=3)) == 3
    assert rank(context_at("files of "), CLIENT, limit=0) == []


def test_each_name_is_offered_once() -> None:
    found = names(rank(context_at("files of "), CLIENT, limit=500))
    assert len(found) == len(set(found))


# ---------------------------------------------------------------------------
# inside `whose (`, and at the start
# ---------------------------------------------------------------------------


def test_inside_whose_on_files_offers_name_first() -> None:
    found = rank(context_at("files whose ("), CLIENT)
    assert found[0].name == "name"
    for candidate in found:
        rows = inspectors.lookup(candidate.name, kind=inspectors.InspectorKind.PROPERTY)
        assert any(row.operands for row in rows), candidate


def test_inside_whose_on_keys_offers_value_first() -> None:
    assert rank(context_at("keys whose ("), CLIENT)[0].name == "value"


def test_statement_start_offers_value_and_key_first() -> None:
    top = names(rank(context_at(""), CLIENT)[:3])
    assert {"value", "key"} <= set(top)


# ---------------------------------------------------------------------------
# What to insert
# ---------------------------------------------------------------------------


def test_a_usually_plural_usually_indexed_producer() -> None:
    (folder,) = (c for c in rank(context_at("files of "), CLIENT) if c.name == "folder")
    assert folder.label == "folders"
    assert folder.snippet == 'folders "$1"'
    assert folder.detail.endswith(": folder")


def test_a_never_indexed_producer_has_no_snippet() -> None:
    (client,) = (c for c in rank(context_at("settings of "), CLIENT) if c.name == "client")
    assert client.label == "client"
    assert client.snippet is None


def test_a_numeric_index_gets_a_numeric_placeholder() -> None:
    (csidl,) = (c for c in rank(context_at("files of "), CLIENT) if c.name == "csidl folder")
    assert csidl.snippet == "csidl folders ${1:0}"


def test_a_usually_singular_producer_is_offered_singular() -> None:
    (system,) = (c for c in rank(context_at("name of "), CLIENT) if c.name == "operating system")
    assert system.label == "operating system"


def test_the_detail_is_a_signature_and_its_type() -> None:
    (system,) = (c for c in rank(context_at("name of "), CLIENT) if c.name == "operating system")
    assert system.detail == "operating system: operating system"


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------


def _table(*rows: str) -> CompletionTable:
    return CompletionTable.parse("".join(f"{row}\n" for row in rows))


def test_a_table_parses_its_rows() -> None:
    table = _table("after-of\tfile\t0\t-\tfolder\t3\t2\t1")
    assert table.rows == (TableRow("after-of", "file", False, None, "folder", 3, 2, 1),)


def test_ranking_backs_off_from_the_most_specific_key() -> None:
    table = _table(
        "after-of\tfile\t0\tpathname\tcsidl folder\t5\t5\t0",
        "after-of\tfile\t0\t-\tfolder\t3\t3\t3",
        "after-of\tfile\t1\t-\tdrive\t9\t0\t0",
    )
    context = CompletionContext(
        kind="after-of",
        replace=(0, 0),
        partial="",
        dialect=Dialect.CLIENT,
        consumer="file",
        outer="pathname",
        expected_types=frozenset({"folder"}),
    )
    found = names(rank(context, CLIENT, table=table, limit=500))
    # The exact key, then the index flag, then the consumer alone, then types.
    assert found[:3] == ["csidl folder", "folder", "drive"]
    assert "windows folder" in found[3:]


def test_a_corpus_pair_is_kept_when_the_static_types_disagree() -> None:
    """`folder of unique values`: real, though the tables type it otherwise."""
    table = _table("after-of\tfolder\t0\t-\tunique value\t4\t0\t4")
    context = CompletionContext(
        kind="after-of",
        replace=(0, 0),
        partial="",
        dialect=Dialect.CLIENT,
        consumer="folder",
        expected_types=frozenset({"folder"}),
    )
    assert rank(context, CLIENT, table=table)[0].name == "unique value"


def test_the_default_table_is_built_once() -> None:
    assert default_table() is default_table()


# ---------------------------------------------------------------------------
# The generator's leave-one-repo-out evaluation
# ---------------------------------------------------------------------------


def test_the_evaluation_reports_each_kind(tmp_path: Path) -> None:
    tool = load_tool(REPO_ROOT / "tools" / "generate_completion_data.py", "_gcd_evaluate")
    per_repo = {
        "one": {'exists files of folders "a"': None, 'names of files of folder "b"': None},
        "two": {'exists files of folders "c"': None, "names of operating system": None},
    }
    report = tool.evaluate(per_repo)
    for kind in ("after-of", "whose-it", "statement-start"):
        assert kind in report
    assert "top 3" in report
    hits = tool.hit_ranks(per_repo)
    # `files of folders` in repo two is ranked with repo one's counts: first.
    assert ("after-of", 0) in hits["two"]


@pytest.mark.parametrize("limit", [1, 3, 5, 10])
def test_top_k_is_a_share(limit: int) -> None:
    tool = load_tool(REPO_ROOT / "tools" / "generate_completion_data.py", "_gcd_topk")
    assert tool.top_k([0, 1, 4, None], limit) == {1: 0.25, 3: 0.5, 5: 0.75, 10: 0.75}[limit]
