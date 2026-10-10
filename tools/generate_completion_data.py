#!/usr/bin/env python3
"""Regenerate ``src/bigfix_relevance_analyzer/_completion_data.py`` from content.

Completion ranks what fits after ``X of``, inside ``whose (`` and at the start of
a statement by how real content uses it (#127). This mines those counts from
local checkouts of content repositories into a small table the package ships.
The table holds inspector names and counts only, never content, so counts from
private repositories may ship in the public package (decided on #127). The
provenance it records is one commit per repo -- ``unknown`` for a directory
that is not a git checkout -- and never a repo's name (decided on PR #129).

Usage, from the analyzer checkout with the content repos as siblings::

    uv run python tools/generate_completion_data.py ../bigfix-content ../besapi ...
    uv run python tools/generate_completion_data.py --evaluate ../bigfix-content ...

``--evaluate`` writes nothing. It prints each context kind's top-1/3/5/10
accuracy, leave-one-repo-out: each repo's statements ranked with a table mined
from the *other* repos only, so no repo is scored on its own data. Run it on
every regeneration to see whether the ranking held.

What is mined
-------------
Every recognized file under 1 MiB, every extracted site, and each distinct
statement once across all repos: 88% of real statements are boilerplate copies,
and counting copies would rank by what was pasted most. Each statement is
parsed, and from its tree:

* ``after-of``: every ``X of Y``. The consumer is the head inspector of ``X``,
  the producer the head of ``Y`` (through ``of``, ``whose`` and ``item ...
  of``), with whether the consumer has an index and what consumes it in turn
  (``version`` in ``version of name of Y``). ``number of Y`` counts too, with
  ``number`` as the consumer: aggregation, but the same seat for completion.
* ``whose-it``: every ``X of it`` directly inside ``C whose (...)``, keyed by
  the head of ``C``. A nested ``whose`` rebinds ``it``, so it is not entered.
* ``statement-start``: the head of each expression in a starting position --
  the statement, each side of ``and``/``or``, each part of ``if`` -- after any
  ``exists``, ``not`` or ``number of``.

Names are canonical singulars (:func:`~bigfix_relevance_analyzer.completion.context.canonical`).
A producer the inspector tables do not know is dropped: a typo in content must
never become a suggestion.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import NamedTuple

from bigfix_relevance_analyzer.completion.context import (
    CompletionContext,
    canonical,
    expected_types,
    head,
    subject_types,
    written_plural,
)
from bigfix_relevance_analyzer.completion.rank import CompletionTable, TableRow, rank
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import (
    _is_recognized,
    extract_relevance_from_file,
)
from bigfix_relevance_analyzer.lint import _walk_files
from bigfix_relevance_analyzer.nodes import (
    Binary,
    Collection,
    Exists,
    If,
    It,
    Node,
    NumberOf,
    Of,
    Reference,
    TupleExpr,
    Unary,
    Whose,
    children,
    walk,
)
from bigfix_relevance_analyzer.parser import try_parse
from bigfix_relevance_analyzer.typecheck import TypeEnvironment

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "_completion_data.py"

SCHEMA_VERSION = 1
MAX_FILE_BYTES = 1024 * 1024
MAX_DEPTH = 64
NUMBER = "number"
"""The consumer ``number of`` is mined as: no property, but the same seat."""


class Observation(NamedTuple):
    """One producer seen in one context of one statement."""

    kind: str
    consumer: str | None
    indexed: bool
    outer: str | None
    producer: str
    producer_indexed: bool
    producer_plural: bool


# ---------------------------------------------------------------------------
# Reading content
# ---------------------------------------------------------------------------


def statements(repo: Path) -> dict[str, Dialect | None]:
    """Every distinct statement in ``repo``, with its dialect when definite."""
    found: dict[str, Dialect | None] = {}
    files, _exceeded = _walk_files(repo, MAX_DEPTH)
    for path in files:
        if not _is_recognized(path):
            continue
        try:
            if path.stat().st_size >= MAX_FILE_BYTES:
                continue
            sites = extract_relevance_from_file(path)
        except (OSError, ValueError) as error:
            print(f"skipping {path}: {error}", file=sys.stderr)
            continue
        for site in sites:
            dialect = next(
                (d for d in (site.context_dialect, site.dialect) if is_definite(d)), None
            )
            found.setdefault(site.text, dialect)
    return found


def source_of(repo: Path) -> str:
    """The provenance of ``repo``: its ``HEAD`` commit, or ``unknown`` when it
    is not the top of a git checkout. Never its name: a private repo may
    contribute counts, but its name does not ship (decided on PR #129)."""
    resolved = repo.resolve()
    try:
        top = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "--show-toplevel", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    if len(top) != 2 or Path(top[0]).resolve() != resolved:
        return "unknown"
    return top[1]


# ---------------------------------------------------------------------------
# Mining one statement
# ---------------------------------------------------------------------------


def _name(reference: Reference | None) -> str | None:
    """The canonical name of a head, or ``None`` when there is none or the
    tables do not know it: a row keyed by a typo could never be looked up."""
    if reference is None:
        return None
    return canonical(reference.phrase)


def _producer(
    kind: str, consumer: str | None, indexed: bool, outer: str | None, node: Node
) -> Observation | None:
    found = head(node)
    if found is None:
        return None
    name = canonical(found.phrase)
    if name is None:
        return None
    return Observation(
        kind, consumer, indexed, outer, name, found.index is not None, written_plural(found.phrase)
    )


def _it_properties(predicate: Node) -> Iterator[Of]:
    """Every ``X of it`` in a ``whose`` predicate whose ``it`` is that
    ``whose``'s: a nested ``whose`` rebinds ``it``, so its predicate is skipped."""
    stack = [predicate]
    while stack:
        node = stack.pop()
        if isinstance(node, Of) and isinstance(node.obj, It):
            yield node
        if isinstance(node, Whose):
            stack.append(node.collection)
            continue
        stack.extend(children(node))


def _starts(node: Node) -> Iterator[Node]:
    """The expressions in a starting position, with ``exists``, ``not`` and
    ``number of`` stripped: what follows ``(``, ``and``, ``or``, ``if`` and the rest."""
    if isinstance(node, Exists | NumberOf) or (isinstance(node, Unary) and node.op == "not"):
        yield from _starts(node.operand)
    elif isinstance(node, Binary):
        yield from _starts(node.left)
        if node.op in {"and", "or"}:
            yield from _starts(node.right)
    elif isinstance(node, If):
        for part in (node.condition, node.then_branch, node.else_branch):
            yield from _starts(part)
    elif isinstance(node, TupleExpr | Collection):
        # Each item after a `,` or `;` starts an expression of its own.
        for item in node.items:
            yield from _starts(item)
    else:
        yield node


def observations(text: str) -> list[Observation]:
    """What ``text`` contributes to the table: nothing when it does not parse."""
    result = try_parse(text)
    if result.node is None:
        return []
    root = result.node
    parents = {id(child): node for node in walk(root) for child in children(node)}

    def outer_of(node: Node) -> str | None:
        parent = parents.get(id(node))
        if isinstance(parent, NumberOf):
            return NUMBER
        if isinstance(parent, Of) and parent.obj is node:
            return _name(head(parent.prop))
        return None

    found: list[Observation] = []
    for node in walk(root):
        if isinstance(node, Of):
            consumer = head(node.prop)
            name = _name(consumer)
            if consumer is not None and name is not None:
                seen = _producer(
                    "after-of",
                    name,
                    consumer.index is not None,
                    outer_of(node),
                    node.obj,
                )
                if seen is not None:
                    found.append(seen)
        elif isinstance(node, NumberOf):
            seen = _producer("after-of", NUMBER, False, outer_of(node), node.operand)
            if seen is not None:
                found.append(seen)
        elif isinstance(node, Whose):
            filtered = head(node.collection)
            collection = _name(filtered)
            if filtered is not None and collection is not None:
                indexed = filtered.index is not None
                for of in _it_properties(node.predicate):
                    seen = _producer("whose-it", collection, indexed, None, of.prop)
                    if seen is not None:
                        found.append(seen)
    for start in _starts(root):
        seen = _producer("statement-start", None, False, None, start)
        if seen is not None:
            found.append(seen)
    return found


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------

Key = tuple[str, str, str, str, str]


def table(texts: Iterable[str]) -> dict[Key, tuple[int, int, int]]:
    """``(kind, consumer, indexed, outer, producer)`` to ``(count, indexed
    count, plural count)`` over ``texts``, one count per statement and context."""
    counts: Counter[Key] = Counter()
    indexed: Counter[Key] = Counter()
    plural: Counter[Key] = Counter()
    for text in texts:
        for seen in observations(text):
            key = (
                seen.kind,
                seen.consumer or "-",
                "1" if seen.indexed else "0",
                seen.outer or "-",
                seen.producer,
            )
            counts[key] += 1
            indexed[key] += seen.producer_indexed
            plural[key] += seen.producer_plural
    return {key: (counts[key], indexed[key], plural[key]) for key in counts}


def render(rows: dict[Key, tuple[int, int, int]], sources: Sequence[str]) -> str:
    """The generated module's text."""
    lines = sorted("\t".join((*key, *(str(n) for n in rows[key]))) for key in rows)
    # Double-quoted, as `ruff format` would leave them: a regeneration must not
    # be rewritten by the commit hooks.
    provenance = "".join(f"    {json.dumps(commit)},\n" for commit in sources)
    body = "".join(f"{line}\n" for line in lines)
    return (
        '"""Completion ranking counts, mined from content. Do not edit by hand.\n'
        "\n"
        "Regenerate with ``uv run python tools/generate_completion_data.py <content repo>\n"
        "[<content repo> ...]``; see that script for what is mined, and\n"
        "``tests/test_completion_data.py`` for what every regeneration must keep.\n"
        "\n"
        "One row per line, tab-separated: context kind, consumer, whether the consumer\n"
        "has an index, outer consumer (``-`` for none), producer, then how many distinct\n"
        "statements used it, how many of those wrote the producer with an index, and how\n"
        "many wrote it plural. Inspector names and counts only: no content.\n"
        '"""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        f"SCHEMA_VERSION: int = {SCHEMA_VERSION}\n"
        "\n"
        "SOURCES: tuple[str, ...] = (\n"
        f"{provenance}"
        ")\n"
        '"""One entry per content repo mined: its commit, or ``unknown`` for one\n'
        "that is not a git checkout. Never its name: a private repo contributes\n"
        'counts only."""\n'
        "\n"
        f"# {len(lines)} rows\n"
        f'ROWS: str = """\\\n{body}"""\n'
    )


KINDS = ("after-of", "whose-it", "statement-start")
TOP = (1, 3, 5, 10)


def _table_rows(rows: dict[Key, tuple[int, int, int]]) -> list[TableRow]:
    return [
        TableRow(
            kind,
            None if consumer == "-" else consumer,
            indexed == "1",
            None if outer == "-" else outer,
            producer,
            *counts,
        )
        for (kind, consumer, indexed, outer, producer), counts in rows.items()
    ]


def _context(seen: Observation, dialect: Dialect | None) -> CompletionContext:
    """The context an editor would have had where ``seen`` was written: built
    with the scan's own type helpers, so the evaluation scores what it sees."""
    expected = subject = None
    if seen.consumer is not None and seen.kind == "after-of":
        expected = expected_types(seen.consumer, indexed=seen.indexed)
    if seen.consumer is not None and seen.kind == "whose-it":
        subject = subject_types(seen.consumer, indexed=seen.indexed)
    return CompletionContext(
        kind=seen.kind,  # type: ignore[arg-type]
        replace=(0, 0),
        partial="",
        dialect=dialect,
        consumer=seen.consumer,
        consumer_indexed=seen.indexed,
        outer=seen.outer,
        expected_types=expected,
        subject_types=subject,
    )


def hit_ranks(
    per_repo: dict[str, dict[str, Dialect | None]],
) -> dict[str, list[tuple[str, int | None]]]:
    """For each repo, the rank of every producer written in it, ranked with a
    table mined from the other repos only: ``(kind, rank)``, rank ``None``
    past the tenth."""
    environments = {
        Dialect.CLIENT: (TypeEnvironment.create(Dialect.CLIENT),),
        Dialect.SESSION: (TypeEnvironment.create(Dialect.SESSION),),
    }
    either = (*environments[Dialect.CLIENT], *environments[Dialect.SESSION])
    hits: dict[str, list[tuple[str, int | None]]] = {}
    for held_out, found in per_repo.items():
        training: dict[str, None] = {}
        for repo, texts in per_repo.items():
            if repo != held_out:
                training.update(dict.fromkeys(texts))
        fold = CompletionTable(_table_rows(table(training)))
        ranks: list[tuple[str, int | None]] = []
        for text, dialect in found.items():
            for seen in observations(text):
                offered = rank(
                    _context(seen, dialect),
                    environments.get(dialect, either) if dialect else either,
                    table=fold,
                    limit=max(TOP),
                )
                position = next((c.rank for c in offered if c.name == seen.producer), None)
                ranks.append((seen.kind, position))
        hits[held_out] = ranks
    return hits


def top_k(ranks: Sequence[int | None], k: int) -> float:
    """The share of ``ranks`` inside the top ``k``."""
    return sum(1 for r in ranks if r is not None and r < k) / len(ranks) if ranks else 0.0


def evaluate(per_repo: dict[str, dict[str, Dialect | None]]) -> str:
    """Leave-one-repo-out accuracy per context kind, as a printable report."""
    hits = hit_ranks(per_repo)
    lines = [
        (
            f"{len(per_repo)} repos, {sum(map(len, per_repo.values()))} statements "
            "(distinct per repo), leave-one-repo-out"
        ),
        f"{'kind':<16}{'pairs':>8}" + "".join(f"{f'top {k}':>9}" for k in TOP),
    ]
    for kind in KINDS:
        ranks = [r for found in hits.values() for seen_kind, r in found if seen_kind == kind]
        lines.append(
            f"{kind:<16}{len(ranks):>8}" + "".join(f"{top_k(ranks, k):>9.1%}" for k in TOP)
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the completion table from content repo checkouts."
    )
    parser.add_argument("repos", nargs="+", type=Path, help="content repo checkouts to mine")
    parser.add_argument("--output", type=Path, default=TARGET, help="the module to write")
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="print leave-one-repo-out accuracy instead of writing the module",
    )
    args = parser.parse_args(argv)
    for repo in args.repos:
        if not repo.is_dir():
            parser.error(f"not a directory: {repo}")
    per_repo = {repo: statements(repo) for repo in args.repos}
    if args.evaluate:
        print(evaluate({repo.name: found for repo, found in per_repo.items()}))
        return 0
    everything: dict[str, None] = {}
    for found in per_repo.values():
        everything.update(dict.fromkeys(found))
    rows = table(everything)
    args.output.write_text(render(rows, [source_of(repo) for repo in args.repos]))
    print(f"wrote {len(rows)} rows from {len(everything)} statements to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
