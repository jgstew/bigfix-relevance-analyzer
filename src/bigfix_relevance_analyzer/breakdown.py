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

**A context has to be made self-contained.** A node's source text is written
relative to wherever it sits, so it cannot simply be quoted as another node's
context. A sub-expression reaches its context in one of two ways, and they need
opposite treatment: through ``it``, which is replaced by the context's text; or
by being applied to it below an ``of``, in which case it is composed back on
with ``of``. Getting that backwards turns an absolute ``file "a"`` inside a
filter into ``file "a" of files``.

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
from typing import Any, assert_never

from bigfix_relevance_analyzer._serialize import _span
from bigfix_relevance_analyzer.binding import resolve_it_bindings
from bigfix_relevance_analyzer.nodes import (
    Bar,
    Binary,
    Cast,
    Collection,
    Exists,
    If,
    It,
    ItemOf,
    Node,
    NumberLiteral,
    NumberOf,
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

    def to_dict(self) -> dict[str, Any]:
        """This probe as JSON-serializable plain data.

        ``relevance`` is the field that matters to a consumer: it is ready to
        hand to an evaluator as-is. The other three are what it was built from,
        kept so a report can explain a probe rather than just quote it.
        """
        return {
            "relevance": self.relevance,
            "kind": self.kind.value,
            "measured": self.measured,
            "context": self.context,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """This level as JSON-serializable plain data.

        ``probe`` and ``unfiltered_probe`` are the probe *text* rather than
        nested probe objects, matching what this payload has always emitted:
        the two extra fields on a :class:`Probe` are the same ``kind`` for every
        level and the ``context``, which the label already conveys. A consumer
        wanting the full objects has :attr:`probe` itself.
        """
        return {
            "label": self.label,
            **_span(self.span),
            "probe": self.probe.relevance,
            "unfiltered_probe": None if self.unfiltered is None else self.unfiltered.relevance,
            "probe_kind": self.probe.kind.value,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """This outcome as JSON-serializable plain data.

        ``count`` stays ``None`` rather than becoming ``0`` when the level was
        not evaluable: zero is a real answer here and
        :attr:`Outcome.EMPTY_OR_ERROR` already means it, so collapsing the two
        would destroy the one distinction this type exists to carry.
        """
        return {"outcome": self.outcome.value, "count": self.count}


@dataclass(frozen=True, slots=True)
class _Visit:
    """Walk this node, in this context."""

    node: Node
    context: str | None
    applied: bool
    """Whether the context is this node's **direct object**.

    True below an ``of``'s property, where everything is applied to the object.
    False in an *ambient* position -- a ``whose`` filter, an ``if`` branch, an
    operand, an index -- where the context is reachable only through ``it``.
    """


@dataclass(frozen=True, slots=True)
class _Emit:
    """Report this level, once its object has been walked."""

    level: Node
    head: Node | None
    head_source: str
    context: str


def breakdown_probes(
    source: str, node: Node, *, kind: ProbeKind = ProbeKind.COUNT
) -> tuple[Level, ...]:
    """One :class:`Level` per measurable level of ``node``, innermost first.

    ``source`` is the text ``node`` was parsed from, and is required separately
    because measured expressions are sliced out of it by span:
    :attr:`~bigfix_relevance_analyzer.nodes.Reference.phrase` is case-folded and
    space-normalized, so it is not what the engine should be handed back.

    The whole expression comes first as a contextless level, then the rest in
    post-order -- an object before the level that consumes it -- which is the
    order the debugger's own worked example reports and the order a graph is
    drawn in.

    A level is any ``of``-shaped node (:class:`~bigfix_relevance_analyzer.nodes.Of`,
    :class:`~bigfix_relevance_analyzer.nodes.ItemOf`,
    :class:`~bigfix_relevance_analyzer.nodes.NumberOf`) **wherever it appears** --
    inside a ``whose`` filter, an operator's operand, an ``if`` branch or a tuple
    item, not only along the outermost chain. Other constructs are not levels
    themselves but are walked through to find the ones inside them.

    What makes that possible is threading a *self-contained* context rather than
    reading one off a single node; see :func:`_self_text`. A node's own source
    text is only self-contained on the object side of an ``of``. On the property
    side it is written relative to a context further out, and probing it as
    written yields either an unbound ``it`` or a property stripped of its direct
    object.
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

    def head_text(level: Node, operand: Node) -> str:
        """The text a level is written with, before its `of`.

        `ItemOf` and `NumberOf` keep no node for their head the way `Of` keeps a
        `prop`, so it is sliced back out of the source -- which also keeps it
        verbatim, spacing and comments included.
        """
        head = source[level.span.start : operand.span.start].rstrip()
        if head.lower().endswith("of"):
            head = head[:-2].rstrip()
        return head

    def unfiltered_probe(measured_head: Node, context: str | None) -> Probe | None:
        """The paired probe for a filtered level: the collection without its filter."""
        if not isinstance(measured_head, Whose):
            return None
        collection = text_of(measured_head.collection)
        return build(collection if context is None else f"{collection} of it", context)

    def self_text(target: Node, context: str | None, applied: bool) -> str:
        """``target``'s text, rewritten so it evaluates on its own.

        Source text is written *relative to* wherever the node sits, so it is
        self-contained only at the outermost level. A node reaches its context
        in one of two ways, and they need opposite treatment:

        * **Through ``it``.** Every ``it`` in ``target`` that binds outside it is
          replaced by the context's text. ``it`` alone is the degenerate case
          and comes back as the context itself.
        * **By being applied to it.** Below an ``of``'s property everything is
          applied to that object, so a node with no ``it`` of its own is
          composed back onto the context with ``of``.

        The distinction matters because a sub-expression in an ambient position
        may be perfectly absolute -- ``file "a"`` inside a filter means the same
        thing wherever it sits, and composing it into ``file "a" of files``
        would be nonsense. Only a node that actually reaches out for its context
        gets rewritten.
        """
        if context is None:
            return text_of(target)

        free = [
            binding.it
            for binding in resolve_it_bindings(target)
            if binding.context is None  # unbound *within target* -- so bound outside it
        ]
        if free:
            # Splice by span rather than replacing the text `it`, which would
            # also hit `it` inside a string literal or a longer word.
            rendered = []
            at = target.span.start
            for it_node in free:
                rendered.append(source[at : it_node.span.start])
                rendered.append(context)
                at = it_node.span.end
            rendered.append(source[at : target.span.end])
            return "".join(rendered)

        return f"{text_of(target)} of {context}" if applied else text_of(target)

    levels: list[Level] = []

    def emit(level_node: Node, head: Node | None, head_source: str, context: str) -> None:
        levels.append(
            Level(
                label=text_of(level_node),
                span=level_node.span,
                probe=build(f"{head_source} of it", context),
                unfiltered=None if head is None else unfiltered_probe(head, context),
            )
        )

    # The root, measured as written and with no context to bind `it` to.
    levels.append(
        Level(
            label=text_of(node),
            span=node.span,
            probe=build(text_of(node), None),
            unfiltered=unfiltered_probe(node, None),
        )
    )

    # An explicit worklist rather than recursion, for the reason
    # `binding.py` gives: this is handed whole trees and must stay total on
    # them. Emission is post-order, so a level is pushed back as a deferred
    # `_Emit` after its object has been walked.
    work: list[_Visit | _Emit] = [_Visit(node, None, applied=False)]
    while work:
        item = work.pop()
        if isinstance(item, _Emit):
            emit(item.level, item.head, item.head_source, item.context)
            continue

        current, context, applied = item.node, item.context, item.applied
        match current:
            case Of(prop=prop, obj=obj):
                obj_self = self_text(obj, context, applied)
                # Popped in reverse: object first, then this level, then the
                # property -- everything in which is applied to the object.
                work.append(_Visit(prop, obj_self, applied=True))
                work.append(_Emit(current, prop, text_of(prop), obj_self))
                work.append(_Visit(obj, context, applied=applied))
            case ItemOf(operand=operand) | NumberOf(operand=operand):
                # Written with `of` and measured like one. Splitting them out of
                # `Of` was a change to the taxonomy, not to what gets probed.
                work.append(
                    _Emit(
                        current,
                        None,
                        head_text(current, operand),
                        self_text(operand, context, applied),
                    )
                )
                work.append(_Visit(operand, context, applied=applied))
            case Whose(collection=collection, predicate=predicate):
                # The filter is not a level of its own, but the expressions
                # inside it are -- measured against the collection *before*
                # filtering, which is what `it` means in there. Inside the
                # filter the context is ambient, not a direct object.
                work.append(
                    _Visit(predicate, self_text(collection, context, applied), applied=False)
                )
                work.append(_Visit(collection, context, applied=applied))
            case Unary(operand=operand) | Exists(operand=operand) | Cast(operand=operand):
                work.append(_Visit(operand, context, applied=applied))
            case Binary(left=left, right=right) | Bar(left=left, right=right):
                # Not levels themselves, but their operands are walked: an `of`
                # chain inside one is still a level.
                work.append(_Visit(right, context, applied=False))
                work.append(_Visit(left, context, applied=False))
            case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
                # `if` passes its context through to all three branches.
                work.append(_Visit(else_branch, context, applied=False))
                work.append(_Visit(then_branch, context, applied=False))
                work.append(_Visit(condition, context, applied=False))
            case TupleExpr(items=items) | Collection(items=items):
                for item_node in reversed(items):
                    work.append(_Visit(item_node, context, applied=False))
            case Reference(index=index):
                # An index is an argument, not something applied to the object:
                # `it` inside it means the object, but an absolute expression
                # there stands on its own.
                if index is not None:
                    work.append(_Visit(index, context, applied=False))
            case It() | NumberLiteral() | StringLiteral():
                pass
            case _:  # pragma: no cover - exhaustiveness over the Node union
                assert_never(current)

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
