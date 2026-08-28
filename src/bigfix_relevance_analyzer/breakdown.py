"""Per-level object counts, as relevance you hand to an evaluator.

The BigFix Fixlet Debugger's graphical "breakdown" mode reports how many objects
each level of an expression produced. The mechanism turns out to be much simpler
than instrumenting an evaluator: it **synthesizes an ordinary relevance query per
level** and runs it through the normal engine. That makes it something this
package can do too, with no evaluator and no new dependency -- it is string
generation over a tree.

So this module emits probe text and stops. The caller evaluates it against
whatever engine it has (``qna.exe``, session relevance, the REST ``clientquery``
API) and passes the rows back to :func:`interpret_count_results`. That split is
what puts a Windows-GUI-only capability in reach of everything else.

Findings and the verified probe strings are recorded in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_.

The two things that are easy to get wrong
-----------------------------------------
**The measured expression is rewritten against ``it``, not copied from source.**
The template binds ``it`` to the context via a trailing ``of {context}``, so the
measured text has to be written relative to that context. For the level
``files of folder "C:\\Windows"`` the measured text is ``files of it``, not
``files``: a property without its direct object is not a valid expression, and
splicing the raw source yields ``The operator "files" is not defined.``

**A probe returns a list, not a scalar.** When the context is plural, ``of``
distributes and the probe answers once per context object. That is exactly what a
breakdown graph wants -- not "this level produced N objects" but "each of the M
parents produced n_i children" -- and it is why results are reconciled
positionally against the context objects.
"""

from __future__ import annotations

import enum
from collections.abc import Sequence
from dataclasses import dataclass
from typing import assert_never

from bigfix_relevance_analyzer.nodes import (
    Binary,
    Cast,
    Collection,
    Exists,
    If,
    It,
    Node,
    NumberLiteral,
    Of,
    Reference,
    Span,
    StringLiteral,
    TupleExpr,
    Unary,
    Whose,
)

__all__ = [
    "Level",
    "Outcome",
    "Probe",
    "ProbeKind",
    "ProbeOutcome",
    "breakdown_probes",
    "interpret_count_results",
]


class ProbeKind(enum.Enum):
    """Which family of probe to emit. The two answer different questions."""

    COUNT = "count"
    """How many objects this level produced. See :func:`interpret_count_results`."""

    VALUE = "value"
    """What this level actually evaluates to -- the debugger's
    ``Current Selection Evaluates To:`` panel. Failure is *no rows at all*
    rather than a sentinel, so there is no numeric interpretation of it."""


# The context form binds `it` to the parent level via the trailing `of {context}`;
# the contextless form uses `true whose` for a level that has no parent.
#
# The guard idioms differ between the families on purpose. `exists number of (X)`
# converts an evaluation failure into False instead of propagating it, which is
# what makes the count total: one broken level never kills the whole breakdown.
# `(true) of (X)` yields one `true` per result of X, so `exists` of it means
# "evaluated without error and produced at least one object".
_TEMPLATES: dict[ProbeKind, tuple[str, str]] = {
    # (contextless, context)
    ProbeKind.COUNT: (
        "(if exists true whose (exists number of ({r1})) then number of ({r2}) else -1)",
        "(if exists it whose (exists number of ({r1})) then number of ({r2}) else -1) of {c}",
    ),
    ProbeKind.VALUE: (
        "(if exists true whose ((true) of ({r1})) then ({r2}) else nothing)",
        "(if exists it whose ((true) of ({r1})) then ({r2}) else nothing) of {c}",
    ),
}
# The count template really does keep two distinct substitution keys for its two
# occurrences of the measured text -- the guard and the counted expression *can*
# differ. Nothing here needs them to, so both receive the same text.


@dataclass(frozen=True, slots=True)
class Probe:
    """One relevance statement to evaluate."""

    relevance: str
    """The probe text, ready to hand to an evaluator."""

    kind: ProbeKind
    """Which family it came from, and so how to read its result."""

    measured: str
    """The measured expression, already rewritten against ``it``."""

    context: str | None
    """The context expression, or ``None`` for the contextless root form."""


@dataclass(frozen=True, slots=True)
class Level:
    """One measurable level of the expression."""

    label: str
    """The level's source text, for labelling a graph node or a report row."""

    span: Span
    """Where the level sits in the source that produced it."""

    probe: Probe
    """The level as written."""

    unfiltered: Probe | None = None
    """The same level with its ``whose`` filter removed, when it has one.

    A ``whose`` level reports its *filtered* count, so the filter's selectivity
    is invisible from that number alone. Evaluating both and comparing is what
    makes it visible: in the reference example the pair answers 21 and 25.
    ``None`` on every level that is not filtered.
    """


class Outcome(enum.Enum):
    """How to read one row of a count probe's result."""

    COUNT = "count"
    """The level produced this many objects."""

    EMPTY_OR_ERROR = "empty-or-error"
    """Zero. Deliberately not reported as a plain count of 0.

    Relevance flattens plural-context errors to empty rather than failing
    (``number of (1/0)`` is ``0``, while ``exists number of (1/0)`` is ``True``),
    so this value conflates "genuinely produced nothing" with "errored in a
    plural context". The engine does not distinguish them and neither can this.
    """

    NOT_EVALUABLE = "not-evaluable"
    """The level could not be evaluated -- the ``-1`` sentinel.

    Ambiguous with a legitimately computed ``-1``. The debugger accepts that
    ambiguity and so does this; it is a property of the probe design, not
    something the caller can resolve.
    """


@dataclass(frozen=True, slots=True)
class ProbeOutcome:
    """One context object's answer."""

    outcome: Outcome
    count: int | None
    """The number of objects, or ``None`` when :attr:`outcome` is
    :attr:`Outcome.NOT_EVALUABLE`."""


def breakdown_probes(
    source: str, node: Node, *, kind: ProbeKind = ProbeKind.COUNT
) -> tuple[Level, ...]:
    """One :class:`Level` per measurable level of ``node``, innermost first.

    ``source`` is the text ``node`` was parsed from, and is required separately
    because measured expressions are sliced out of it by span:
    :attr:`~bigfix_relevance_analyzer.nodes.Reference.phrase` is case-folded and
    space-normalized, so it is not what the engine should be handed back.

    The whole expression comes first as a contextless level, then the ``of``
    spine from the innermost level outwards -- the order the debugger's own
    worked example reports, and the order a graph is drawn in.

    Levels are the root plus each ``of``. Other constructs are transparent: they
    are measured as part of whichever level encloses them, which is what the
    debugger does too.
    """
    contextless_template, context_template = _TEMPLATES[kind]

    def text_of(target: Node) -> str:
        return source[target.span.start : target.span.end]

    def build(measured: str, context: str | None) -> Probe:
        if context is None:
            relevance = contextless_template.format(r1=measured, r2=measured)
        else:
            relevance = context_template.format(r1=measured, r2=measured, c=context)
        return Probe(relevance=relevance, kind=kind, measured=measured, context=context)

    def unfiltered_probe(measured_head: Node, context: str | None) -> Probe | None:
        """The paired probe for a filtered level: the collection without its filter."""
        if not isinstance(measured_head, Whose):
            return None
        collection = text_of(measured_head.collection)
        return build(collection if context is None else f"{collection} of it", context)

    levels: list[Level] = []

    # The root, measured as written and with no context to bind `it` to.
    levels.append(
        Level(
            label=text_of(node),
            span=node.span,
            probe=build(text_of(node), None),
            unfiltered=unfiltered_probe(node, None),
        )
    )

    # Then the `of` spine, walked object-first so the innermost level is
    # reported before the ones that consume it.
    stack: list[Node] = [node]
    spine: list[Of] = []
    while stack:
        current = stack.pop()
        match current:
            case Of(prop=prop, obj=obj):
                spine.append(current)
                stack.append(obj)
                stack.append(prop)
            case Whose(collection=collection, predicate=_predicate):
                # The predicate is measured as part of this level, not as one of
                # its own: it is a filter, not a step in the `of` chain.
                stack.append(collection)
            case Unary(operand=operand) | Exists(operand=operand) | Cast(operand=operand):
                stack.append(operand)
            case Reference() | It() | NumberLiteral() | StringLiteral():
                pass
            case Binary() | If() | TupleExpr() | Collection():
                # Compound values, not levels of a single chain. Their parts are
                # measured within whichever level encloses them.
                pass
            case _:  # pragma: no cover - exhaustiveness over the Node union
                assert_never(current)

    for of_node in reversed(spine):
        context = text_of(of_node.obj)
        measured = f"{text_of(of_node.prop)} of it"
        levels.append(
            Level(
                label=text_of(of_node),
                span=of_node.span,
                probe=build(measured, context),
                unfiltered=unfiltered_probe(of_node.prop, context),
            )
        )

    return tuple(levels)


def interpret_count_results(rows: Sequence[str]) -> tuple[ProbeOutcome, ...]:
    """Read a count probe's answer rows, one outcome per context object.

    Reconcile the result positionally against the context objects: a length
    mismatch is an internal error, and is the condition behind the debugger's
    own ``Result counts do not match result number`` diagnostic. This function
    cannot check that for you -- it never sees the context objects -- so the
    caller compares the lengths.

    Raises :class:`ValueError` for a row that is not an integer. A count probe
    can only answer with integers, so anything else means the rows did not come
    from one, and silently coercing that would report a fabricated count.
    """
    outcomes: list[ProbeOutcome] = []
    for row in rows:
        try:
            value = int(row.strip())
        except ValueError:
            raise ValueError(f"not a count probe result: {row!r}") from None
        if value < 0:
            outcomes.append(ProbeOutcome(outcome=Outcome.NOT_EVALUABLE, count=None))
        elif value == 0:
            outcomes.append(ProbeOutcome(outcome=Outcome.EMPTY_OR_ERROR, count=0))
        else:
            outcomes.append(ProbeOutcome(outcome=Outcome.COUNT, count=value))
    return tuple(outcomes)
