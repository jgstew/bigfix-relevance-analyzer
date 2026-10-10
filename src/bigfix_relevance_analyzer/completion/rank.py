"""What fits a :class:`~.context.CompletionContext`, best first.

Ranking reads the context and nothing else -- never the tokens, never how the
context was found -- so a recovering parser that produces contexts uses this
unchanged.

The order
---------
Types alone narrow too little: ``files of`` allows some 200 rows returning a
``<folder>``. What makes the list usable is how real content uses each pair,
from the table :mod:`bigfix_relevance_analyzer._completion_data` (mined by
``tools/generate_completion_data.py``). The order backs off from the most
specific key the table has to the type-valid rest:

1. the table's producers for this kind, consumer, index flag and outer consumer;
2. then for the kind, consumer and index flag;
3. then for the kind and consumer, each by count;
4. then every type-valid candidate not listed yet -- the reverse lookup
   (:func:`~bigfix_relevance_analyzer.inspectors.producers_of`) after ``of``,
   the forward one (:func:`~bigfix_relevance_analyzer.inspectors.applicable_to`)
   inside ``whose (``, every property with no object
   (:func:`~bigfix_relevance_analyzer.inspectors.global_properties`) at the
   start -- by how often it is a producer at all in this kind, then
   alphabetically. When the types are not known, every producer the table has
   for the kind, the same way.

A table pair is never dropped because the static types disagree with it: the
tables type ``unique values``, ``preceding text`` and others less precisely than
real content uses them. It is dropped only when no row of its name is visible in
the environment -- the wrong dialect, or a platform that lacks it. Measured
leave-one-repo-out in #127, this puts the producer written in the top 3 for
about three in four real ``X of`` pairs.

What to insert
--------------
Each candidate carries its written form (the plural when content usually writes
it plural, as lint's ``plural-preferred`` would push the author to anyway), and
a snippet with an index placeholder when content usually gives it one
(``folders "$1"``, ``csidl folders ${1:0}``). "Usually" is read under the most
specific key the table has the candidate for, backing off as the order does:
``file`` is written singular under ``key "x" of section "y" of``, though plural
nearly everywhere else.
"""

from __future__ import annotations

import functools
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from bigfix_relevance_analyzer import _completion_data, inspectors
from bigfix_relevance_analyzer.completion.context import CompletionContext, singular
from bigfix_relevance_analyzer.inspectors import Inspector, InspectorKind
from bigfix_relevance_analyzer.typecheck import TypeEnvironment

__all__ = ["Candidate", "CompletionTable", "TableRow", "default_table", "rank"]

SCHEMA_VERSION: Final = 1
"""The table schema this module reads; a test pins the generated module to it."""

_STRING_INDEXES: Final = frozenset({"string", "binary_string"})
_NUMBER_INDEXES: Final = frozenset({"integer"})


@dataclass(frozen=True, slots=True)
class Candidate:
    """One thing to offer, in the order offered."""

    name: str
    """The canonical (singular) name: what the table and the tables know it by."""

    label: str
    """The written form to insert: the plural when content usually writes it so."""

    detail: str
    """A signature and its return type, e.g. ``folder <string> of <folder>: folder``."""

    snippet: str | None
    """The label with an index placeholder, e.g. ``folders "$1"``, when content
    usually indexes it; ``None`` otherwise. For a client that takes snippets."""

    rank: int
    """0-based position in the list."""


@dataclass(frozen=True, slots=True)
class TableRow:
    """One row of the completion table."""

    kind: str
    consumer: str | None
    indexed: bool
    outer: str | None
    producer: str
    count: int
    """How many distinct statements used this producer in this context."""

    indexed_count: int
    """How many of those wrote the producer with an index."""

    plural_count: int
    """How many of those wrote the producer plural."""


class CompletionTable:
    """The completion table, indexed for the backoff in :func:`rank`."""

    def __init__(self, rows: Iterable[TableRow]) -> None:
        self.rows = tuple(rows)
        self._keys: dict[tuple[object, ...], Counter[str]] = {}
        self._producers: dict[str, Counter[str]] = {}
        self._usage: dict[tuple[object, ...], tuple[int, int, int]] = {}
        for row in self.rows:
            keys = _backoff(row.kind, row.consumer, row.indexed, row.outer)
            for key in keys:
                self._keys.setdefault(key, Counter())[row.producer] += row.count
            self._producers.setdefault(row.kind, Counter())[row.producer] += row.count
            # How the producer is written, under every key it can be asked by,
            # down to the kind and then to every kind.
            for key in (*keys, (row.kind,), ()):
                count, indexed, plural = self._usage.get((*key, row.producer), (0, 0, 0))
                self._usage[(*key, row.producer)] = (
                    count + row.count,
                    indexed + row.indexed_count,
                    plural + row.plural_count,
                )

    @classmethod
    def parse(cls, text: str) -> CompletionTable:
        """A table from the generated module's ``ROWS`` text."""

        def optional(field: str) -> str | None:
            return None if field == "-" else field

        rows = []
        for line in text.splitlines():
            kind, consumer, indexed, outer, producer, count, indexed_count, plural = line.split(
                "\t"
            )
            rows.append(
                TableRow(
                    kind,
                    optional(consumer),
                    indexed == "1",
                    optional(outer),
                    producer,
                    int(count),
                    int(indexed_count),
                    int(plural),
                )
            )
        return cls(rows)

    def producer_counts(self, kind: str) -> Mapping[str, int]:
        """How often each name is a producer at all, in ``kind``."""
        return self._producers.get(kind, Counter())

    def seen(self, context: CompletionContext) -> list[str]:
        """The producers the table has for ``context``, in backoff order."""
        ordered: dict[str, None] = {}
        for key in _context_keys(context):
            counts = self._keys.get(key)
            if counts:
                ordered.update(dict.fromkeys(_by_count(counts, counts)))
        return list(ordered)

    def usage(self, context: CompletionContext, producer: str) -> tuple[int, int, int] | None:
        """``(count, indexed count, plural count)`` for ``producer`` under the
        most specific of ``context``'s keys that has it, then its kind, then
        every kind: how content writes it *here*. ``None`` when never seen."""
        for key in (*_context_keys(context), (context.kind,), ()):
            found = self._usage.get((*key, producer))
            if found is not None:
                return found
        return None


def _backoff(
    kind: str, consumer: str | None, indexed: bool, outer: str | None
) -> tuple[tuple[object, ...], ...]:
    """The table keys from most specific to least: what :func:`rank` backs off through."""
    return ((kind, consumer, indexed, outer), (kind, consumer, indexed), (kind, consumer))


def _context_keys(context: CompletionContext) -> tuple[tuple[object, ...], ...]:
    return _backoff(context.kind, context.consumer, context.consumer_indexed, context.outer)


@functools.cache
def default_table() -> CompletionTable:
    """The shipped table, parsed once, on first use."""
    if _completion_data.SCHEMA_VERSION != SCHEMA_VERSION:  # pragma: no cover - test-pinned
        raise ValueError(f"completion table schema {_completion_data.SCHEMA_VERSION}")
    return CompletionTable.parse(_completion_data.ROWS)


def rank(
    context: CompletionContext,
    environment: TypeEnvironment | Sequence[TypeEnvironment],
    *,
    table: CompletionTable | None = None,
    limit: int = 50,
) -> list[Candidate]:
    """What fits ``context``, best first, at most ``limit`` of them.

    ``environment`` decides what is visible: one, or several when the dialect
    is not known (a candidate any of them allows is kept). ``table`` is the
    shipped one unless given.
    """
    environments = (
        (environment,) if isinstance(environment, TypeEnvironment) else tuple(environment)
    )
    table = table if table is not None else default_table()
    if limit <= 0:
        return []
    ordered = dict.fromkeys(table.seen(context))
    overall = table.producer_counts(context.kind)
    ordered.update(dict.fromkeys(_by_count(_type_valid(context, environments, overall), overall)))
    partial = context.partial.lower()
    found: list[Candidate] = []
    for name in ordered:
        # Cheap first: a name none of whose spellings can match costs no lookup.
        if partial and not any(_matches(partial, form, name) for form in _spellings(name)):
            continue
        rows = _visible_rows(name, environments)
        if not rows:
            continue
        label, snippet = _insertion(name, rows, table.usage(context, name))
        if partial and not _matches(partial, label, name):
            continue
        found.append(Candidate(name, label, _detail(rows, context, snippet), snippet, len(found)))
        if len(found) == limit:
            break
    return found


def _by_count(names: Iterable[str], counts: Mapping[str, int]) -> list[str]:
    """``names`` most-counted first, then alphabetically."""
    return sorted(names, key=lambda name: (-counts.get(name, 0), name))


def _type_valid(
    context: CompletionContext,
    environments: Sequence[TypeEnvironment],
    overall: Mapping[str, int],
) -> set[str]:
    """The fallback pool: names the types allow here, or, when the types are
    not known, every producer the table has for this kind."""
    rows: Iterable[Inspector]
    if context.kind == "after-of" and context.expected_types is not None:
        rows = (
            row
            for environment in environments
            for row in inspectors.producers_of(context.expected_types, environment)
        )
    elif context.kind == "whose-it" and context.subject_types is not None:
        rows = (
            row
            for environment in environments
            for row in inspectors.applicable_to(context.subject_types, environment)
        )
    elif context.kind == "statement-start":
        rows = (
            row for environment in environments for row in inspectors.global_properties(environment)
        )
    else:
        return set(overall)
    return {singular(row) for row in rows}


@functools.cache
def _all_spellings() -> dict[str, frozenset[str]]:
    """Every written form of each canonical name: its singular and plurals."""
    forms: dict[str, set[str]] = {}
    for row in inspectors.properties():
        name = singular(row)
        forms.setdefault(name, {name}).update(
            form.lower() for form in (row.plural_name,) if form is not None
        )
    return {name: frozenset(found) for name, found in forms.items()}


def _spellings(name: str) -> frozenset[str]:
    return _all_spellings().get(name, frozenset({name}))


def _visible_rows(name: str, environments: Sequence[TypeEnvironment]) -> list[Inspector]:
    """The property rows written ``name`` that some environment can see, in table order."""
    return [
        row
        for row in inspectors.lookup(name, kind=InspectorKind.PROPERTY)
        if singular(row) == name and any(env.visible(row) for env in environments)
    ]


def _insertion(
    name: str, rows: list[Inspector], usage: tuple[int, int, int] | None
) -> tuple[str, str | None]:
    """The label to insert, and its snippet when content usually indexes it."""
    plural = next((row.plural_name for row in rows if row.plural_name), None)
    label = name
    if plural is not None and (usage is None or 2 * usage[2] >= usage[0]):
        label = plural.lower()
    indexed = [row for row in rows if row.index_type is not None]
    if not indexed:
        return label, None
    usually = 2 * usage[1] >= usage[0] if usage is not None else len(indexed) == len(rows)
    if not usually:
        return label, None
    index_type = indexed[0].index_type
    if index_type in _STRING_INDEXES:
        return label, f'{label} "$1"'
    if index_type in _NUMBER_INDEXES:
        return label, f"{label} ${{1:0}}"
    return label, f"{label} ($1)"


def _matches(partial: str, label: str, name: str) -> bool:
    """Whether ``partial`` (lowercased) is being typed as this candidate: the
    start of any word of its label or name, or for a multi-word partial
    (``bes c``, ``bes ``) the start of the label or name itself."""
    if " " in partial:
        return label.lower().startswith(partial) or name.startswith(partial)
    return any(word.startswith(partial) for word in f"{label} {name}".lower().split())


def _detail(rows: list[Inspector], context: CompletionContext, snippet: str | None) -> str:
    """The signature of the row that best fits ``context``, with its type."""

    def fits(row: Inspector) -> bool:
        if context.kind == "after-of" and context.expected_types:
            return bool(set(inspectors.ancestors(row.return_type)) & context.expected_types)
        if context.kind == "whose-it" and context.subject_types:
            subjects = {a for t in context.subject_types for a in inspectors.ancestors(t)}
            return bool(row.operands) and row.operands[-1] in subjects
        return True

    def preference(row: Inspector) -> tuple[bool, bool, bool, int]:
        # What fits, indexed as inserted, then the plainest spelling of it:
        # `folder <string>` over `folder <binary_string> of <encoding>`.
        return (
            not fits(row),
            (row.index_type is not None) != (snippet is not None),
            row.index_type not in (None, "string"),
            len(row.operands),
        )

    best = min(rows, key=preference)
    return f"{best.signature}: {best.return_type}"
