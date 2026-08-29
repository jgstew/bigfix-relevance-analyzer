"""Static type checking over the relevance AST.

The BigFix Fixlet Debugger carries a full static type checker, separate from the
terse errors the evaluator prints, and it is the piece nothing in the open-source
ecosystem reproduces. This module is the start of one: the type model, the
environment resolution runs against, and checking for every construct that does
not need property resolution.

Set-valued types
----------------
A value's type is a **set**, not a single name. Two independent reasons:
inspectors are overloaded across direct-object types, and the same name can
resolve differently per platform -- ``drives`` yields ``drive`` on Windows,
``volume`` on macOS and ``filesystem`` on Linux. Carrying the whole set lets a
later inspector narrow it, and lets an unspecified platform stay honest rather
than guess.

:attr:`RelevanceValue.types` distinguishes ``None`` from the empty set on
purpose. ``None`` is "the table said nothing", the snapshot discipline this
package applies everywhere -- absence is grounds for a warning at most, never
proof. Empty is "every candidate was ruled out", which is a finding.

Platform coverage is reported, not enforced
-------------------------------------------
One relevance statement routinely targets several platforms at once, guarding
platform-specific inspectors behind ``if``/``then``/``else`` so the wrong
platform never evaluates the branch that would fail on it. The statement is
correct; each branch is correct only somewhere. This repo's own example corpus
contains a fixlet whose ``then`` branch is Debian/Ubuntu-only and whose ``else``
branch is RHEL-only.

So platform sets **intersect along a chain** and **union across alternatives**
(``if`` branches, and the two sides of ``|``), and an empty platform set is
**never** an error on its own. Errors live on the type axis and have to hold on
every platform: a property no candidate type defines anywhere, a cast that
exists for no operand type. "Only runs on Linux" is information.

The engine agrees: its own checker carries ``at most one branch of an
if-statement may have type errors`` -- deliberate tolerance for exactly this
idiom, which :func:`check` implements.

Findings and message wording come from
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, assert_never

from bigfix_relevance_analyzer import grammar, inspectors
from bigfix_relevance_analyzer._serialize import _span
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS
from bigfix_relevance_analyzer.dialect import Dialect
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
    NumberKind,
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
    "CheckResult",
    "Plurality",
    "RelevanceValue",
    "TypeDiagnostic",
    "TypeEnvironment",
    "check",
    "resolve_property",
]

_BOOLEAN = frozenset({"boolean"})
_INTEGER = frozenset({"integer"})


class Plurality(enum.Enum):
    """Whether an expression yields one value or many.

    A separate axis from the type name, which is how the engine's own
    diagnostics treat it -- they interpolate ``'{plurality} {type}'``.
    """

    SINGULAR = "singular"
    PLURAL = "plural"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RelevanceValue:
    """What an expression evaluates to, as far as the tables can say."""

    types: frozenset[str] | None
    """The possible type names. ``None`` when undetermined; empty when every
    candidate was ruled out."""

    plurality: Plurality = Plurality.UNKNOWN

    platforms: frozenset[str] = frozenset()
    """Client platforms on which this reading is viable.

    Reported, never enforced -- see the module docstring. Empty under
    :attr:`~bigfix_relevance_analyzer.dialect.Dialect.SESSION`, where platform
    is not a meaningful axis.
    """

    @property
    def known(self) -> bool:
        return self.types is not None


@dataclass(frozen=True, slots=True)
class TypeDiagnostic:
    """One finding, in the engine's own wording."""

    code: str
    """The key in :data:`~bigfix_relevance_analyzer.diagnostics.DIAGNOSTICS`."""

    message: str
    span: Span

    def to_dict(self) -> dict[str, Any]:
        """This diagnostic as JSON-serializable plain data."""
        return {"code": self.code, "message": self.message, **_span(self.span)}


@dataclass(frozen=True, slots=True)
class CheckResult:
    """What :func:`check` produced."""

    value: RelevanceValue
    diagnostics: tuple[TypeDiagnostic, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.diagnostics

    @property
    def platforms(self) -> frozenset[str]:
        """Where the statement as a whole can run."""
        return self.value.platforms

    def to_dict(self) -> dict[str, Any]:
        """This result as JSON-serializable plain data.

        The :class:`RelevanceValue` is flattened in rather than nested: a
        consumer wants "what type is this, and is it singular" as one answer,
        and the extra level of nesting bought nothing. ``platforms`` is not
        here either -- it belongs to the analysis, which knows the platform
        universe this was narrowed against and can therefore also say which
        platforms are *missing*.
        """
        return {
            "types": None if self.value.types is None else sorted(self.value.types),
            "plurality": self.value.plurality.value,
            "known": self.value.known,
            "ok": self.ok,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True, slots=True)
class TypeEnvironment:
    """The slice of the inspector tables resolution runs against.

    ``dialect`` is required: client and session are genuinely different
    languages, and extraction already hands callers a
    :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.dialect`.
    ``platform`` is optional -- leaving it out starts every lookup with all
    platforms in play and lets narrowing do the work, which is what makes the
    coverage report meaningful.
    """

    dialect: Dialect
    platform: str | None = None
    _all_platforms: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    @classmethod
    def create(cls, dialect: Dialect, platform: str | None = None) -> TypeEnvironment:
        return cls(dialect=dialect, platform=platform, _all_platforms=_platform_universe())

    @property
    def universe(self) -> frozenset[str]:
        """Every platform in play -- all of them, or just the one selected."""
        if self.dialect is not Dialect.CLIENT:
            return frozenset()
        if self.platform is not None:
            return frozenset({self.platform})
        return self._all_platforms or _platform_universe()

    def visible(self, entry: inspectors.Inspector) -> bool:
        """Whether this row counts, given the dialect and platform selected."""
        if self.dialect not in entry.dialects:
            return False
        if self.dialect is Dialect.CLIENT and self.platform is not None:
            return self.platform in entry.platforms
        return True

    def platforms_of(self, entries: list[inspectors.Inspector]) -> frozenset[str]:
        if self.dialect is not Dialect.CLIENT:
            return frozenset()
        found: frozenset[str] = frozenset()
        for entry in entries:
            found |= entry.platforms
        return found & self.universe


def _platform_universe() -> frozenset[str]:
    return frozenset(
        context
        for source in inspectors.sources()
        for dialect, _, context in [source.partition(":")]
        if dialect == "client" and context
    )


def _render(types: frozenset[str] | None) -> str:
    if types is None:
        return "unknown"
    if not types:
        return "none"
    return " or ".join(sorted(types))


def _diagnostic(code: str, span: Span, **fields: object) -> TypeDiagnostic:
    entry = DIAGNOSTICS[code]
    return TypeDiagnostic(code=code, message=entry.format(**fields), span=span)


def resolve_property(
    name: str, subject: frozenset[str] | None, environment: TypeEnvironment
) -> RelevanceValue:
    """Resolve a property against the types its direct object might have.

    ``subject`` is the set of possible direct-object types, or ``None`` for a
    property written without one -- ``processors``, ``drives`` -- which the
    tables record with no operands.

    This is where the set narrows. Only the candidate types that actually define
    ``name`` survive, and the platform set contracts to the rows that matched,
    so a chain answers "where can this run?" as a side effect of being typed::

        drives                       -> {drive, filesystem, volume}  all platforms
          block size of it           -> {integer}                    debian, rhel, ubuntu
          allocation block count of it -> {integer}                  macos
          bogus property of it       -> {}                           nothing defines it

    An empty result is a real finding: not "unknown property" but "no possible
    type defines it". A result of ``None`` means the name is not in this
    snapshot at all, which proves nothing -- callers must not treat it as an
    error.

    The ancestor walk is mandatory here, not an optimisation: a property is
    declared on the base type, so ``size`` resolves for ``application`` only
    through ``application -> file``.
    """
    rows = [
        entry
        for entry in inspectors.lookup(name, kind=inspectors.InspectorKind.PROPERTY)
        if environment.visible(entry)
    ]
    if not rows:
        return RelevanceValue(types=None, platforms=environment.universe)

    if subject is None:
        matched = [entry for entry in rows if not entry.operands]
    else:
        matched = [
            entry
            for entry in rows
            if any(
                operand in inspectors.ancestors(candidate)
                for candidate in subject
                for operand in entry.operands
            )
        ]

    plurality = Plurality.UNKNOWN
    forms = {inspectors.written_form_of(entry, name) for entry in matched}
    if forms == {inspectors.WrittenForm.PLURAL}:
        plurality = Plurality.PLURAL
    elif forms == {inspectors.WrittenForm.SINGULAR}:
        plurality = Plurality.SINGULAR

    return RelevanceValue(
        types=frozenset(entry.return_type for entry in matched),
        plurality=plurality,
        platforms=environment.platforms_of(matched),
    )


def check(node: Node, environment: TypeEnvironment) -> CheckResult:
    """Type ``node``, reporting findings in the engine's own wording.

    Constructs needing property resolution -- :class:`~...nodes.Reference`,
    :class:`~...nodes.Of`, :class:`~...nodes.It`, :class:`~...nodes.Whose` --
    come back with ``types=None`` rather than a guess, and ``None`` propagates
    without ever becoming an error. The checker is quiet about what it cannot
    yet reason about rather than wrong about it.
    """
    checker = _Checker(environment)
    value = checker.run(node)
    return CheckResult(value=value, diagnostics=tuple(checker.diagnostics))


@dataclass(frozen=True, slots=True)
class _Descend:
    """Walk into this node."""

    node: Node


@dataclass(frozen=True, slots=True)
class _Combine:
    """Type this node, now that its children have been."""

    node: Node


@dataclass(frozen=True, slots=True)
class _BeginBranch:
    """Start holding findings back -- an `if` branch is about to be checked."""


@dataclass(frozen=True, slots=True)
class _EndBranch:
    """Set aside the findings this branch produced."""


_Work = _Descend | _Combine | _BeginBranch | _EndBranch


class _Checker:
    """A post-order walk over an explicit stack.

    Not recursion, for the reason `binding.py` and `breakdown.py` give: this is
    handed whole trees and has to stay total on them. The parser bounds how
    *deeply nested* an expression it will return, but not how *wide* one is, and
    a left-associative chain is shallow to parse and deep in the tree -- a
    generated `x = 1 or x = 2 or ...` of a few thousand terms parses fine and
    would overflow a recursive checker.
    """

    def __init__(self, environment: TypeEnvironment) -> None:
        self.env = environment
        self.diagnostics: list[TypeDiagnostic] = []
        self.values: list[RelevanceValue] = []
        self.marks: list[int] = []
        self.branches: list[list[TypeDiagnostic]] = []
        # Per-item types, so `item N of (...)` can pick one out after the tuple
        # as a whole has been collapsed to a single value.
        self.tuple_items: dict[int, tuple[RelevanceValue, ...]] = {}

    def run(self, root: Node) -> RelevanceValue:
        work: list[_Work] = [_Descend(root)]
        while work:
            item = work.pop()
            match item:
                case _Descend(node=node):
                    self.descend(node, work)
                case _Combine(node=node):
                    self.combine(node)
                case _BeginBranch():
                    self.marks.append(len(self.diagnostics))
                case _EndBranch():
                    at = self.marks.pop()
                    self.branches.append(self.diagnostics[at:])
                    del self.diagnostics[at:]
                case _:  # pragma: no cover - exhaustiveness over _Work
                    assert_never(item)
        return self.values.pop()

    # -- helpers ------------------------------------------------------------

    def report(self, code: str, span: Span, **fields: object) -> None:
        self.diagnostics.append(_diagnostic(code, span, **fields))

    def unknown(self) -> RelevanceValue:
        return RelevanceValue(types=None, platforms=self.env.universe)

    def literal(self, name: str) -> RelevanceValue:
        return RelevanceValue(
            types=frozenset({name}),
            plurality=Plurality.SINGULAR,
            platforms=self.env.universe,
        )

    def rows(self, entries: tuple[inspectors.Inspector, ...]) -> list[inspectors.Inspector]:
        return [entry for entry in entries if self.env.visible(entry)]

    def require_singular_boolean(
        self, value: RelevanceValue, span: Span, code: str, **fields: object
    ) -> None:
        """Only complain on positive evidence: an unknown type is not a finding."""
        if value.types is None:
            return
        if "boolean" not in value.types or value.plurality is Plurality.PLURAL:
            self.report(
                code, span, plurality=value.plurality.value, type=_render(value.types), **fields
            )

    def pop(self, count: int) -> list[RelevanceValue]:
        """The last `count` child values, back in source order."""
        if count == 0:
            return []
        taken = self.values[-count:]
        del self.values[-count:]
        return taken

    # -- descending ---------------------------------------------------------

    def descend(self, node: Node, work: list[_Work]) -> None:
        """Queue `node`'s children, then `node` itself.

        Children are appended in reverse, because the work list is a stack:
        the last one appended is the first one taken.
        """
        match node:
            case NumberLiteral(kind=kind):
                self.values.append(self.literal(_NUMBER_TYPES[kind]))
            case StringLiteral():
                self.values.append(self.literal("string"))
            case It():
                self.values.append(self.unknown())
            case Cast(operand=operand) | Unary(operand=operand) | Exists(operand=operand):
                work.append(_Combine(node))
                work.append(_Descend(operand))
            case NumberOf(operand=operand) | ItemOf(operand=operand):
                work.append(_Combine(node))
                work.append(_Descend(operand))
            case Binary(left=left, right=right) | Bar(left=left, right=right):
                work.append(_Combine(node))
                work.append(_Descend(right))
                work.append(_Descend(left))
            case Of(prop=first, obj=second) | Whose(collection=first, predicate=second):
                # Not typed yet -- but still walked, because a type error inside
                # one is a type error wherever it sits.
                work.append(_Combine(node))
                work.append(_Descend(second))
                work.append(_Descend(first))
            case Reference(index=index):
                work.append(_Combine(node))
                if index is not None:
                    work.append(_Descend(index))
            case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
                work.append(_Combine(node))
                work.append(_EndBranch())
                work.append(_Descend(else_branch))
                work.append(_BeginBranch())
                work.append(_EndBranch())
                work.append(_Descend(then_branch))
                work.append(_BeginBranch())
                work.append(_Descend(condition))
            case TupleExpr(items=items) | Collection(items=items):
                work.append(_Combine(node))
                for item in reversed(items):
                    work.append(_Descend(item))
            case _:  # pragma: no cover - exhaustiveness over the Node union
                assert_never(node)

    # -- combining ----------------------------------------------------------

    def combine(self, node: Node) -> None:
        match node:
            case Cast():
                (operand,) = self.pop(1)
                self.values.append(self.combine_cast(node, operand))
            case Unary():
                (operand,) = self.pop(1)
                self.values.append(self.combine_unary(node, operand))
            case Binary():
                left, right = self.pop(2)
                self.values.append(self.combine_binary(node, left, right))
            case Bar():
                left, right = self.pop(2)
                self.values.append(self.combine_bar(node, left, right))
            case Exists():
                self.pop(1)
                self.values.append(self.literal("boolean"))
            case NumberOf():
                self.pop(1)
                self.values.append(self.literal("integer"))
            case ItemOf():
                (operand,) = self.pop(1)
                self.values.append(self.combine_item_of(node, operand))
            case If():
                condition, then_value, else_value = self.pop(3)
                self.values.append(self.combine_if(node, condition, then_value, else_value))
            case TupleExpr(items=items) | Collection(items=items):
                values = self.pop(len(items))
                self.tuple_items[id(node)] = tuple(values)
                self.values.append(self.combine_sequence(node, values))
            case Of() | Whose():
                self.pop(2)
                self.values.append(self.unknown())
            case Reference(index=index):
                self.pop(0 if index is None else 1)
                self.values.append(self.unknown())
            case NumberLiteral() | StringLiteral() | It():  # pragma: no cover - never queued
                pass
            case _:  # pragma: no cover - exhaustiveness over the Node union
                assert_never(node)

    def combine_sequence(self, node: Node, values: list[RelevanceValue]) -> RelevanceValue:
        if any(value.types is None for value in values):
            return self.unknown()
        types: frozenset[str] = frozenset()
        for value in values:
            types |= value.types or frozenset()
        return RelevanceValue(
            types=types,
            plurality=Plurality.PLURAL if isinstance(node, Collection) else Plurality.SINGULAR,
            platforms=self.env.universe,
        )

    def combine_cast(self, node: Cast, operand: RelevanceValue) -> RelevanceValue:
        if operand.types is None:
            return self.unknown()
        rows = [
            entry
            for entry in self.rows(
                inspectors.lookup(node.target, kind=inspectors.InspectorKind.CAST)
            )
            if entry.name == node.target
            and any(
                source in inspectors.ancestors(candidate)
                for candidate in operand.types
                for source in entry.operands
            )
        ]
        if not rows:
            self.report(
                "cast-not-defined",
                node.span,
                source_type=_render(operand.types),
                token="as",
                cast_name=node.target,
            )
            return RelevanceValue(types=frozenset(), platforms=frozenset())
        return RelevanceValue(
            types=frozenset(entry.return_type for entry in rows),
            plurality=operand.plurality,
            platforms=self.env.platforms_of(rows) or operand.platforms,
        )

    def combine_binary(
        self, node: Binary, left: RelevanceValue, right: RelevanceValue
    ) -> RelevanceValue:
        if node.op in grammar.GRAMMAR_LEVEL_BINARY:
            # `and` / `or`: fixed rules, no table row to look up.
            self.require_singular_boolean(
                left, node.left.span, "left-operand-not-boolean", token=node.op
            )
            self.require_singular_boolean(
                right, node.right.span, "right-operand-not-boolean", token=node.op
            )
            return self.literal("boolean")

        form = grammar.CANONICAL_BINARY.get(node.op)
        if form is None or left.types is None or right.types is None:
            return self.unknown()

        lhs, rhs = (right, left) if form.swapped else (left, right)
        rows = [
            entry
            for entry in self.rows(
                inspectors.lookup(form.operator, kind=inspectors.InspectorKind.BINARY_OPERATOR)
            )
            if len(entry.operands) == 2
            and any(entry.operands[0] in inspectors.ancestors(t) for t in lhs.types or frozenset())
            and any(entry.operands[1] in inspectors.ancestors(t) for t in rhs.types or frozenset())
        ]
        if not rows:
            self.report(
                "binary-operator-not-defined",
                node.span,
                token=node.op,
                left_type=_render(left.types),
                right_type=_render(right.types),
            )
            return RelevanceValue(types=frozenset(), platforms=frozenset())

        types = _BOOLEAN if form.negated else frozenset(entry.return_type for entry in rows)
        return RelevanceValue(
            types=types,
            plurality=Plurality.SINGULAR,
            platforms=self.env.platforms_of(rows) or (left.platforms & right.platforms),
        )

    def combine_unary(self, node: Unary, operand: RelevanceValue) -> RelevanceValue:
        if node.op == "not":
            self.require_singular_boolean(
                operand, node.operand.span, "argument-not-boolean", token="not"
            )
            return self.literal("boolean")
        if operand.types is None:
            return self.unknown()
        rows = [
            entry
            for entry in self.rows(
                inspectors.lookup(node.op, kind=inspectors.InspectorKind.UNARY_OPERATOR)
            )
            if any(o in inspectors.ancestors(t) for t in operand.types for o in entry.operands)
        ]
        if not rows:
            self.report(
                "unary-operator-not-defined",
                node.span,
                token=node.op,
                argument_type=_render(operand.types),
            )
            return RelevanceValue(types=frozenset(), platforms=frozenset())
        return RelevanceValue(
            types=frozenset(entry.return_type for entry in rows),
            plurality=operand.plurality,
            platforms=self.env.platforms_of(rows) or operand.platforms,
        )

    def combine_bar(self, node: Bar, left: RelevanceValue, right: RelevanceValue) -> RelevanceValue:
        if left.types is not None and right.types is not None and not (left.types & right.types):
            self.report("incompatible-types", node.span)
        types = None if left.types is None or right.types is None else left.types | right.types
        return RelevanceValue(
            types=types,
            plurality=left.plurality if left.plurality is right.plurality else Plurality.UNKNOWN,
            # Error fallback is an alternative: either side may be the one that runs.
            platforms=left.platforms | right.platforms,
        )

    def combine_item_of(self, node: ItemOf, operand: RelevanceValue) -> RelevanceValue:
        if node.index.kind is NumberKind.LARGE_INTEGER:
            self.report("tuple-index-unreasonable", node.span, token=node.index.text)
            return RelevanceValue(types=frozenset(), platforms=frozenset())
        if not isinstance(node.operand, TupleExpr):
            # It may still be a tuple-valued expression; nothing is known yet.
            return self.unknown()
        items = self.tuple_items.get(id(node.operand), ())
        index = int(node.index.text)
        if index >= len(items):  # 0-based, checked while type checking
            self.report(
                "tuple-index-out-of-range", node.span, token=node.index.text, total=len(items)
            )
            return RelevanceValue(types=frozenset(), platforms=frozenset())
        return items[index]

    def combine_if(
        self,
        node: If,
        condition: RelevanceValue,
        then_value: RelevanceValue,
        else_value: RelevanceValue,
    ) -> RelevanceValue:
        self.require_singular_boolean(
            condition, node.condition.span, "if-condition-not-singular-boolean"
        )
        else_found = self.branches.pop()
        then_found = self.branches.pop()
        if then_found and else_found:
            self.report("both-if-branches-have-type-errors", node.span)
            self.diagnostics.extend(then_found)
            self.diagnostics.extend(else_found)

        types = (
            None
            if then_value.types is None or else_value.types is None
            else then_value.types | else_value.types
        )
        return RelevanceValue(
            types=types,
            plurality=(
                then_value.plurality
                if then_value.plurality is else_value.plurality
                else Plurality.UNKNOWN
            ),
            # Alternatives: only one branch ever runs, so the statement covers
            # the union of what its branches cover.
            platforms=then_value.platforms | else_value.platforms,
        )


_NUMBER_TYPES = {
    NumberKind.INTEGER: "integer",
    NumberKind.LARGE_INTEGER: "large integer",
    NumberKind.NOT_AN_INTEGER: "floating point",
}
