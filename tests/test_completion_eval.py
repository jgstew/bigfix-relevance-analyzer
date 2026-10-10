"""The completion evaluation set: a floor no regeneration or ranking change may
drop below (#127).

``tests/examples/`` is held out: the table is mined from content repositories,
never from this one. For every real ``X of Y`` in it, the text up to ``Y`` is
scanned and ranked exactly as an editor would at that cursor, and the rank of
the producer actually written is recorded; likewise for ``X of it`` inside
``whose (``, and for the first inspector of a statement.

The floors are what was measured when this landed, less a small margin. A
regenerated table or a ranking change that drops below one fails here, with
every kind's accuracy printed. This is also the bar for later work: a
recovering parser that produces contexts for these same prefixes must meet or
beat it before it replaces the scan for that context kind (#96 item 3).
"""

from __future__ import annotations

from collections.abc import Iterator

from _corpus import parsed_corpus_sites

from bigfix_relevance_analyzer.completion.context import (
    _opens_expression,
    canonical,
    head,
    scan_context,
)
from bigfix_relevance_analyzer.completion.rank import rank
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import _site_dialect
from bigfix_relevance_analyzer.nodes import (
    Exists,
    It,
    Node,
    NumberOf,
    Of,
    Unary,
    Whose,
    children,
    walk,
)
from bigfix_relevance_analyzer.tokenizer import code_tokens
from bigfix_relevance_analyzer.typecheck import TypeEnvironment

TOP = 3
"""The cut the floors are for: VS Code shows about this many above the fold
when nothing typed decides the order."""

FLOORS = {"after-of": 0.75, "whose-it": 0.76, "statement-start": 0.14}
"""Top-3 accuracy per kind, measured 2026-10-10 less a margin of about two
misses: after-of 77.9% of 272, whose-it 80.9% of 47, statement-start 18.4% of
49. (Whose-it was 92.6% of 27 before the scan also claimed the seats after
``exists``, ``if``, ``then``, ``else``, ``,`` and ``;`` inside ``whose (``;
those 27 still score 92.6%.) Statement starts rank low because the table's counts are not split by
dialect and most of its starts are client (`value`, `key`), while many of these
examples are session relevance."""

ENVIRONMENTS = {
    Dialect.CLIENT: (TypeEnvironment.create(Dialect.CLIENT),),
    Dialect.SESSION: (TypeEnvironment.create(Dialect.SESSION),),
}
EITHER = (*ENVIRONMENTS[Dialect.CLIENT], *ENVIRONMENTS[Dialect.SESSION])


def _whose_it(predicate: Node) -> Iterator[Of]:
    """``X of it`` in a predicate, not inside a nested ``whose`` (which rebinds ``it``)."""
    stack = [predicate]
    while stack:
        node = stack.pop()
        if isinstance(node, Of) and isinstance(node.obj, It):
            yield node
        if isinstance(node, Whose):
            stack.append(node.collection)
            continue
        stack.extend(children(node))


def _first(node: Node) -> Node:
    """The statement's first expression after ``exists``, ``not`` and ``number of``."""
    while isinstance(node, Exists | NumberOf | Unary) and not (
        isinstance(node, Unary) and node.op != "not"
    ):
        node = node.operand
    return node


def _opens_a_condition(text: str, offset: int) -> bool:
    """Whether ``offset`` is where a new expression starts -- after ``(``,
    ``,``, ``;``, ``and``, ``or``, ``not``, ``exists``, ``if``, ``then`` or
    ``else`` -- the seats inside ``whose (`` the scan claims for ``X of it``.
    One after ``=`` waits for recovery, and is not evaluated here."""
    tokens = list(code_tokens(text[:offset]))
    return bool(tokens) and _opens_expression(tokens[-1])


def _positions(text: str, root: Node) -> Iterator[tuple[str, int, Node]]:
    """``(kind, cursor offset, what was written there)`` for every evaluated position."""
    for node in walk(root):
        if isinstance(node, Of):
            yield "after-of", node.obj.span.start, node.obj
        elif isinstance(node, Whose):
            for of in _whose_it(node.predicate):
                if _opens_a_condition(text, of.span.start):
                    yield "whose-it", of.span.start, of.prop
    yield "statement-start", _first(root).span.start, _first(root)


def measure() -> dict[str, list[int | None]]:
    """The rank of every written producer, by kind; ``None`` when it is not
    offered, or the scan finds no context of that kind there."""
    ranks: dict[str, list[int | None]] = {kind: [] for kind in FLOORS}
    seen: set[tuple[str, Dialect | None]] = set()
    for _path, site, root in parsed_corpus_sites():
        dialect = _site_dialect(site, None)
        if (site.text, dialect) in seen:
            continue  # boilerplate copies count once, as the table counts them
        seen.add((site.text, dialect))
        for kind, offset, written in _positions(site.text, root):
            found = head(written)
            name = canonical(found.phrase) if found is not None else None
            if name is None:
                continue
            context = scan_context(site.text, offset, False, dialect)
            if context is None or context.kind != kind:
                ranks[kind].append(None)
                continue
            environments = ENVIRONMENTS.get(dialect, EITHER) if dialect else EITHER
            offered = rank(context, environments, limit=10)
            ranks[kind].append(next((c.rank for c in offered if c.name == name), None))
    return ranks


def share(ranks: list[int | None], top: int) -> float:
    return sum(1 for r in ranks if r is not None and r < top) / len(ranks)


def test_the_ranking_holds_its_floor() -> None:
    ranks = measure()
    report = {
        kind: (len(found), *(round(share(found, k), 3) for k in (1, 3, 10)))
        for kind, found in ranks.items()
    }
    for kind, floor in FLOORS.items():
        assert ranks[kind], kind
        assert share(ranks[kind], TOP) >= floor, f"{kind} below its floor: {report}"
    print(report)
