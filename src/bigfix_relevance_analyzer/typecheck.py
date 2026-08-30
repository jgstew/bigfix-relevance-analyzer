"""Static type checking over the relevance AST.

The BigFix Fixlet Debugger carries a full static type checker, separate from the
terse errors the evaluator prints, and it is the piece nothing in the open-source
ecosystem reproduces. This module is one: the type model, the environment
resolution runs against, and checking for every construct in the language --
including the ones that need property resolution, which is most of them.

Context, and why the walk is not in source order
------------------------------------------------
``of`` and ``whose`` introduce the context ``it`` refers to, and the object
comes *first*: in ``A of B``, ``B`` is typed in the enclosing context and only
then becomes the context ``A`` is typed in. The walk therefore queues the
second child before the first, which is the one place its order departs from
the source. :mod:`bigfix_relevance_analyzer.binding` states the same rule for
the same reason, and the two are held together by a test.

A context does not hide the world: a global name written inside one still
resolves against the world when the context defines nothing by that name.

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
from typing import Any, Final, assert_never

from bigfix_relevance_analyzer import grammar, inspectors
from bigfix_relevance_analyzer._serialize import _span
from bigfix_relevance_analyzer.diagnostics import (
    DIAGNOSTICS,
    PROPERTY_DIRECT_OBJECT_FRAGMENT,
    PROPERTY_INDEX_FRAGMENT,
    Origin,
)
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.nodes import (
    MAX_LARGE_INTEGER,
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
        """Whether the statement type-checks -- not whether it is unremarkable.

        A diagnostic the *runtime* raises is a risk the statement runs with,
        not a fault in it: `value of results ...` is a well-typed singular
        expression that errors only if its object turns out to hold other than
        one value. The checker reports it, and `ok` stays true, because a
        consumer asking "does this type-check" is not asking "is this without
        risk". `Origin` is what separates them, so a new advisory entry needs
        no change here.
        """
        return not any(
            DIAGNOSTICS[diagnostic.code].origin is Origin.TYPE_CHECK
            for diagnostic in self.diagnostics
        )

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


def _ruled_out(value: RelevanceValue) -> bool:
    """Whether every candidate type was already eliminated.

    The finding was reported where it happened. Anything downstream of it can
    only repeat the same mistake in different words -- `<none> as trimmed
    string`, `<none> != <string>` -- so a ruled-out value silences the checks
    it feeds rather than cascading through them. The value stays empty rather
    than becoming `None`: the statement really is known-broken, and
    :attr:`CheckResult.ok` must keep saying so.
    """
    return value.types is not None and not value.types


UNTYPED: Final = "undefined"
"""The type the tables record when there is no value to have a type.

Exactly three rows return it -- `nil`, `null` and `error` -- which between
them are written `nothing`, `nothings`, `null value` and `error`: the
idiomatic "no result" constructs, not a type anything conflicts with. `if
windows of operating system then (x64 variables ("X") of it) else nothings`
is ordinary, shipped content, and the evaluator accepts it: the `nothings`
branch contributes no value rather than a value of the wrong type.

So `undefined` is an *absence* of type information, and every comparison in
this module treats it as matching whatever it is held against -- see
:func:`_types_compatible` and :func:`_accepts`. Left to compare as an
ordinary type name it unifies with nothing, which is what made
:meth:`_Checker.combine_bar`, :meth:`_Checker.combine_if`,
:meth:`_Checker.combine_binary`, :meth:`_Checker.combine_unary` and
:func:`resolve_property` all report on valid relevance -- 41 of the 46
type errors over a 1,108-file corpus of real content were this one bug.
"""


def _accepts(declared: str, candidate: str) -> bool:
    """Whether a row declaring operand type ``declared`` takes a ``candidate`` value.

    The is-a walk every lookup site in this module already did inline, plus
    :data:`UNTYPED`, which no row declares but any row accepts: a `nothing`
    handed to a cast, an operator or a property propagates rather than
    failing to resolve.
    """
    return candidate == UNTYPED or declared in inspectors.ancestors(candidate)


def _types_compatible(left: frozenset[str], right: frozenset[str]) -> bool:
    """Whether any type on one side shares a common ancestor with any type on
    the other -- the same is-a relationship every other type comparison in
    this module already resolves through :func:`~bigfix_relevance_analyzer.
    inspectors.ancestors` (:meth:`_Checker.combine_cast`,
    :meth:`_Checker.combine_binary`, :meth:`_Checker.combine_unary`,
    :func:`resolve_property`), rather than a literal type-name match.

    Confirmed live against a real evaluator: ``<T with multiplicity>`` and
    ``T`` are compatible (they share the ancestor ``T``), and so are two
    unrelated *siblings* under one umbrella type -- ``file`` and ``folder``
    both evaluate cleanly against each other because they share ``filesystem
    object``, even though neither is a subtype of the other. A literal
    ``left & right`` set intersection catches neither case, which is what
    made :meth:`_Checker.combine_bar` and :meth:`_Checker.combine_if` report
    ``operand-types-incompatible`` / ``if-branch-types-incompatible`` on
    perfectly valid content -- see the regression tests this fixes.

    :data:`UNTYPED` short-circuits to compatible on either side, for the
    reason given there: it is the absence of a type, not one that conflicts.
    """
    if UNTYPED in left or UNTYPED in right:
        return True
    left_ancestors = {ancestor for name in left for ancestor in inspectors.ancestors(name)}
    right_ancestors = {ancestor for name in right for ancestor in inspectors.ancestors(name)}
    return bool(left_ancestors & right_ancestors)


AGGREGATES: Final = frozenset(
    {
        "concatenations",
        "conjunctions",
        "disjunctions",
        "fxf encoding concatenations",
        "html concatenations",
        "intersections",
        "local encoding concatenations",
        "maxima",
        "minima",
        "sets",
        "sums",
        "unions",
        "unique values",
    }
)
"""Properties whose whole job is to consume a collection.

Spelled as the tables spell them, which is the plural form; both written forms
resolve to it. Handing one of these a plural object is what it is *for*, so
`singular-over-plural-object` stays quiet over them -- `unique value of X` most
sharply of all, since it dedups before asserting singularity and so succeeds
where a bare singular form over the same object would not.

Curated rather than inferred, because the tables cannot answer it. An
aggregate's operand is recorded as the *element* type -- `unique values of <bes
action>` -- never as the collection, so "declared to take a plural" is not
something the data says. The nearest type-shape predicate (return type equal to
the operand type, or to it with multiplicity, or to a set of it) matches 70
names, `parent`, `first child`, `next sibling` and `absolute value` among them:
all of which distribute, and must keep warning.
"""


def _is_aggregate(phrase: str) -> bool:
    return any(
        entry.name in AGGREGATES
        for entry in inspectors.lookup(phrase, kind=inspectors.InspectorKind.PROPERTY)
    )


def _widen(*pluralities: Plurality) -> Plurality:
    """Plural anywhere in a chain makes the chain plural; unknown poisons."""
    if Plurality.PLURAL in pluralities:
        return Plurality.PLURAL
    if Plurality.UNKNOWN in pluralities:
        return Plurality.UNKNOWN
    return Plurality.SINGULAR


def _diagnostic(code: str, span: Span, **fields: object) -> TypeDiagnostic:
    entry = DIAGNOSTICS[code]
    return TypeDiagnostic(code=code, message=entry.format(**fields), span=span)


def resolve_property(
    name: str,
    subject: frozenset[str] | None,
    environment: TypeEnvironment,
    *,
    indexed: bool | None = None,
) -> RelevanceValue:
    """Resolve a property against the types its direct object might have.

    ``subject`` is the set of possible direct-object types, or ``None`` for a
    property written without one -- ``processors``, ``drives`` -- which the
    tables record with no operands.

    ``indexed`` says whether the property was written with an index argument --
    the ``"foo"`` in ``key "foo" of registry``. ``True`` keeps only rows that
    take one and ``False`` only rows that do not, which is how ``processors``
    and ``processor 0`` are told apart; ``None``, the default, does not
    discriminate.

    Only the *presence* of an index is matched, never its type. A string
    literal legitimately satisfies a ``<binary_string>`` index -- the engine
    converts implicitly, and this package does not model conversions -- so
    comparing the two would reject ``file "c:\\windows"``, which is about the
    most common expression in the language.

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

    if indexed is not None:
        rows = [entry for entry in rows if (entry.index_type is not None) is indexed]

    if subject is None:
        matched = [entry for entry in rows if not entry.operands]
    else:
        matched = [
            entry
            for entry in rows
            if any(
                _accepts(operand, candidate) for candidate in subject for operand in entry.operands
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

    A name the tables do not contain comes back with ``types=None`` rather than
    a guess, and ``None`` propagates without ever becoming an error. The checker
    is quiet about what it cannot reason about rather than wrong about it.
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


@dataclass(frozen=True, slots=True)
class _PushContext:
    """Make the value just computed the context `it` refers to.

    Queued between the two children of an `of` or a `whose`, so that the object
    is typed in the *enclosing* context and only the property sees it.
    """


@dataclass(frozen=True, slots=True)
class _PopContext:
    """Leave that context again."""


_Work = _Descend | _Combine | _BeginBranch | _EndBranch | _PushContext | _PopContext


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
        # What `it` refers to, innermost last. Empty is the implicit world, and
        # an `it` reached with it empty is the `used-without-context` finding.
        # There is deliberately no World node: absence of a context *is* the
        # root, and inventing a node for it would change every parse tree.
        self.contexts: list[RelevanceValue] = []
        # Reference nodes whose own resolution is not the finding to report.
        self.suppressed: set[int] = set()
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
                case _PushContext():
                    # The object's value is still on the value stack; its
                    # `combine` has not run yet.
                    self.contexts.append(self.values[-1])
                case _PopContext():
                    self.contexts.pop()
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

    def accept_collapse(self, span: Span) -> None:
        """Withdraw the collapse risks inside ``span``: something needed them.

        `singular-over-plural-object` says a singular form was written over an
        object that may hold several. Where the value flows into a position
        that *requires* a singular, that collapse is what makes the expression
        legal at all, and reporting it would say the author should have written
        something they had no way to write.

        Retraction rather than a check up front, because the walk is an
        iterative work queue: `combine_of` cannot see the parent that will
        consume it, but every site that demands a singular already calls
        :meth:`require_singular` or :meth:`require_singular_boolean` with the
        operand's span. Containment then identifies the risks that operand
        raised, however deep -- the reported webreport put one two levels down,
        under a cast.

        The list is edited in place and only above ``span``, which is what
        keeps the `_BeginBranch` marks in :attr:`marks` valid: a risk inside
        this operand was appended after any mark that is still open, so no
        index below one ever moves.
        """
        self.diagnostics[:] = [
            diagnostic
            for diagnostic in self.diagnostics
            if not (
                diagnostic.code == "singular-over-plural-object"
                and span.start <= diagnostic.span.start
                and diagnostic.span.end <= span.end
            )
        ]

    def require_singular_boolean(
        self, value: RelevanceValue, span: Span, code: str, **fields: object
    ) -> None:
        """Only complain on positive evidence: an unknown type is not a finding."""
        self.accept_collapse(span)
        if value.types is None or _ruled_out(value):
            return
        if "boolean" not in value.types or value.plurality is Plurality.PLURAL:
            self.report(
                code, span, plurality=value.plurality.value, type=_render(value.types), **fields
            )

    def require_singular(
        self, value: RelevanceValue, span: Span, code: str, **fields: object
    ) -> None:
        """The engine's `A singular expression is required.`, said precisely.

        Positive evidence only, the same as :meth:`require_singular_boolean`:
        `Plurality.UNKNOWN` is not a finding.
        """
        self.accept_collapse(span)
        if value.plurality is Plurality.PLURAL:
            self.report(code, span, **fields)

    def context_value(self, span: Span) -> RelevanceValue:
        """What `it` refers to here, reporting the unbound case.

        Always singular, however plural the context is: `A of B` evaluates `A`
        once per element of `B`, so `it` is one element and not the collection.
        """
        if not self.contexts:
            self.report("used-without-context", span, token="it")
            return RelevanceValue(types=None, platforms=self.env.universe)
        context = self.contexts[-1]
        return RelevanceValue(
            types=context.types, plurality=Plurality.SINGULAR, platforms=context.platforms
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
            case NumberLiteral(kind=NumberKind.CONSTANT_TOO_LARGE):
                # Unlike `large integer`, this numeral fails to parse *at all*,
                # wherever it appears -- not only as a tuple index. Confirmed
                # live: a bare literal this size errors identically.
                self.report(
                    "integer-constant-too-large",
                    node.span,
                    token=node.text,
                    max_value=MAX_LARGE_INTEGER,
                )
                # Typed as `integer`, not ruled out to `frozenset()`. `_ruled_out`
                # exists to stop a finding from cascading into restatements of
                # the same mistake -- but a sibling problem elsewhere in the
                # same expression (`... | "string"`) is not a restatement, it is
                # independent: the token is still, visibly, an integer literal,
                # just one this large the engine can't parse into a value.
                # Ruling it out would silently swallow that second finding, and
                # confirmed live, `|` does not rescue either finding here --
                # unlike a genuine runtime failure (`1/0`, which `|` really does
                # catch and fall back from), a too-large constant is a type-shaped
                # failure that survives `|` no matter what is on the other side.
                self.values.append(self.literal("integer"))
            case NumberLiteral(kind=kind):
                self.values.append(self.literal(_NUMBER_TYPES[kind]))
            case StringLiteral():
                self.values.append(self.literal("string"))
            case It():
                self.values.append(self.context_value(node.span))
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
            case Of(prop=first, obj=second) | Whose(collection=second, predicate=first):
                # The context-introducing constructs, and the reason this walk
                # cannot simply queue children in source order: `second` -- the
                # object of an `of`, the collection of a `whose` -- is typed in
                # the *enclosing* context, and only then becomes the context
                # `first` is typed in. Getting this backwards silently binds the
                # wrong node in every nested expression. `binding.py` spells out
                # the same rule for the same reason.
                if isinstance(node, Of) and self.bad_tuple_index(node) is not None:
                    # `item "a" of (1,2,3)` is one mistake, not two: the tuple
                    # rule is the finding, so the name is not also resolved as
                    # the `item <string> of <folder>` property it is not.
                    self.suppressed.add(id(node.prop))
                work.append(_Combine(node))
                work.append(_PopContext())
                work.append(_Descend(first))
                work.append(_PushContext())
                work.append(_Descend(second))
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
            case Of():
                # Pushed object-first by `descend`, so that is the order back.
                obj, prop = self.pop(2)
                self.values.append(self.combine_of(node, prop, obj))
            case Whose():
                collection, predicate = self.pop(2)
                self.values.append(self.combine_whose(node, collection, predicate))
            case Reference(index=index):
                taken = self.pop(0 if index is None else 1)
                self.values.append(self.combine_reference(node, taken[0] if taken else None))
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

    def combine_reference(self, node: Reference, index: RelevanceValue | None) -> RelevanceValue:
        """A name, resolved against whatever context encloses it.

        At the root there is no context, and a property is looked up among the
        rows that take no direct object -- `processors`, `drives`, `true`. That
        is the same lookup the debugger makes against the implicit world.

        A context does not hide the world. A global name written inside one
        still resolves against the world when the context defines nothing by
        that name -- `files whose (name of it = name of operating system)` is
        ordinary relevance, and the corpus contains
        `packages ... whose (exists properties whose (...))`, where `properties`
        is the world's. So resolution falls back, and only a name the *world*
        does not define either is a finding.
        """
        if id(node) in self.suppressed:
            return self.unknown()
        if self.contexts and _ruled_out(self.contexts[-1]):
            return self.contexts[-1]
        subject = self.contexts[-1].types if self.contexts else None
        if self.contexts and subject is None:
            # The context itself is unresolved, so nothing can be concluded
            # about a property of it.
            return self.unknown()
        value = resolve_property(node.phrase, subject, self.env, indexed=node.index is not None)
        if subject is not None and value.types is not None and not value.types:
            world = resolve_property(node.phrase, None, self.env, indexed=node.index is not None)
            if world.types:
                return world
        if value.types is not None and not value.types:
            self.report(
                "property-not-defined",
                node.span,
                phrase=node.phrase,
                index=(
                    ""
                    if index is None
                    else PROPERTY_INDEX_FRAGMENT.format(name=_render(index.types))
                ),
                direct_object=(
                    ""
                    if subject is None
                    else PROPERTY_DIRECT_OBJECT_FRAGMENT.format(name=_render(subject))
                ),
            )
        return value

    def combine_of(self, node: Of, prop: RelevanceValue, obj: RelevanceValue) -> RelevanceValue:
        """`A of B` -- the property's own type, and the written form's plurality.

        Whichever of the property's two names was written settles the phrase,
        whatever the object's own plurality::

            Q: name of files of folders "/"
            A: besserverupgrad2.log
            E: Singular expression refers to non-unique object.

        One name, not one per file -- and an error *about the object*, raised
        at evaluation, not the static `A singular expression is required.` that
        a genuinely plural operand earns. `names of files of folders "/"` is
        the plural phrase, and `name of files "besserverupgrad2.log" of folders
        "/"` answers cleanly because the object turned out to be unique.

        The object decides only where the property has no written form of its
        own to speak with -- a cast, a nested `of` -- which is why `(it as
        string) of files of folder "c:\\"` is plural off a singular `it`.
        """
        index = self.bad_tuple_index(node)
        if index is not None:
            self.report("tuple-index-not-literal", node.span, token=index.text)
            return RelevanceValue(types=frozenset(), platforms=frozenset())

        # `resolve_property` already read the written form; it leaves plurality
        # `UNKNOWN` for a name it could not match, or one whose matched rows
        # disagree, and there the object is still the best evidence there is.
        plurality: Plurality
        if isinstance(node.prop, Reference) and prop.plurality is not Plurality.UNKNOWN:
            plurality = prop.plurality
            if (
                plurality is Plurality.SINGULAR
                and obj.plurality is Plurality.PLURAL
                and not _is_aggregate(node.prop.phrase)
            ):
                self.report("singular-over-plural-object", node.span, phrase=node.prop.phrase)
        else:
            plurality = _widen(prop.plurality, obj.plurality)
        return RelevanceValue(
            types=prop.types,
            plurality=plurality,
            # A chain intersects: every step has to hold at once.
            platforms=prop.platforms & obj.platforms,
        )

    def bad_tuple_index(self, node: Of) -> NumberLiteral | StringLiteral | None:
        """The offending index of an `item <not an integer literal> of <tuple>`.

        The parser builds :class:`~...nodes.ItemOf` only for an integer-literal
        index, because telling a tuple subscript from the real `item <string> of
        <folder>` property needs the object's type -- which the checker has and
        the parser deliberately does not. So the rule lands here.

        Only a literal index is recognised, since the message names the
        offending token and the checker is not given the source text to quote a
        computed one from.
        """
        if not isinstance(node.obj, TupleExpr) or not isinstance(node.prop, Reference):
            return None
        index = node.prop.index
        if node.prop.phrase != "item" or not isinstance(index, NumberLiteral | StringLiteral):
            return None
        return index

    def branches_coexist(self, then_value: RelevanceValue, else_value: RelevanceValue) -> bool:
        """Whether any one platform sees both branches of an `if` at once.

        The type axis has to answer to the platform axis here. Two branches
        with no platform in common are alternatives *by construction* -- one
        reading exists on Windows, the other on Linux -- and their types
        differing is the whole point, not a mistake. Only branches that some
        single platform could take together can disagree about type.

        Session relevance has no platform axis, so every branch coexists there.
        """
        if self.env.dialect is not Dialect.CLIENT:
            return True
        return bool(then_value.platforms & else_value.platforms)

    def combine_whose(
        self, node: Whose, collection: RelevanceValue, predicate: RelevanceValue
    ) -> RelevanceValue:
        """`X whose (P)` -- `X`'s type, filtered.

        The filter must be boolean but **may be plural**, which is the asymmetry
        against an `if` condition. The message reproduces that: it names no
        plurality because the rule does not have one.
        """
        if (
            predicate.types is not None
            and not _ruled_out(predicate)
            and "boolean" not in predicate.types
        ):
            self.report(
                "whose-filter-not-boolean", node.predicate.span, type=_render(predicate.types)
            )
        return RelevanceValue(
            types=collection.types,
            plurality=Plurality.PLURAL,
            platforms=collection.platforms & predicate.platforms,
        )

    def combine_cast(self, node: Cast, operand: RelevanceValue) -> RelevanceValue:
        if operand.types is None:
            return self.unknown()
        if _ruled_out(operand):
            return operand
        rows = [
            entry
            for entry in self.rows(
                inspectors.lookup(node.target, kind=inspectors.InspectorKind.CAST)
            )
            if entry.name == node.target
            and any(
                _accepts(source, candidate)
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

        # An operator takes one value a side, whatever its types. This is the
        # engine's `A singular expression is required.`, and it is the
        # operator's own rule -- `sizes of it > 1000` inside a `whose` fails
        # here, not on the filter, which may itself be plural.
        self.require_singular(left, node.left.span, "left-operand-not-singular", token=node.op)
        self.require_singular(right, node.right.span, "right-operand-not-singular", token=node.op)

        if _ruled_out(left) or _ruled_out(right):
            return RelevanceValue(types=frozenset(), platforms=frozenset())

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
            and any(_accepts(entry.operands[0], t) for t in lhs.types or frozenset())
            and any(_accepts(entry.operands[1], t) for t in rhs.types or frozenset())
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
        self.require_singular(operand, node.operand.span, "argument-not-singular", token=node.op)
        if operand.types is None:
            return self.unknown()
        if _ruled_out(operand):
            return operand
        rows = [
            entry
            for entry in self.rows(
                inspectors.lookup(node.op, kind=inspectors.InspectorKind.UNARY_OPERATOR)
            )
            if any(_accepts(o, t) for t in operand.types for o in entry.operands)
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
        # `a | b` yields `b` when `a` errored, so a collapse risk inside `a` is
        # a risk the author has already answered -- this is what the corpus's
        # `free space of drives of system folders | 0` is for.
        self.accept_collapse(node.left.span)

        # The evaluator's own message for this is the terse "Incompatible types."
        # -- qna/the debugger don't say what was actually mismatched. The
        # template leads with that confirmed string verbatim and appends the
        # two names, since the built-in message alone isn't enough to act on.
        if (
            left.types
            and right.types
            and not _ruled_out(left)
            and not _ruled_out(right)
            and not _types_compatible(left.types, right.types)
            # Same tolerance as an `if`: two sides no single platform sees
            # together are alternatives, and their types differing is the point.
            and self.branches_coexist(left, right)
        ):
            self.report(
                "operand-types-incompatible",
                node.span,
                token="|",
                left_type=_render(left.types),
                right_type=_render(right.types),
            )
        types = None if left.types is None or right.types is None else left.types | right.types
        return RelevanceValue(
            types=types,
            plurality=left.plurality if left.plurality is right.plurality else Plurality.UNKNOWN,
            # Error fallback is an alternative: either side may be the one that runs.
            platforms=left.platforms | right.platforms,
        )

    def combine_item_of(self, node: ItemOf, operand: RelevanceValue) -> RelevanceValue:
        if node.index.kind is NumberKind.CONSTANT_TOO_LARGE:
            # This numeral never parses, regardless of context -- the same
            # finding `descend` would report for it anywhere else. It is
            # caught here too because the index is read directly off the node
            # rather than descended into as a child value (see `descend`).
            self.report(
                "integer-constant-too-large",
                node.span,
                token=node.index.text,
                max_value=MAX_LARGE_INTEGER,
            )
            return RelevanceValue(types=frozenset(), platforms=frozenset())
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

        if (
            then_value.types
            and else_value.types
            and not _types_compatible(then_value.types, else_value.types)
            and not (then_found or else_found)
            and self.branches_coexist(then_value, else_value)
        ):
            # Both branches typed cleanly and share nothing: the statement has
            # no single type, whichever branch runs.
            self.report(
                "if-branch-types-incompatible",
                node.span,
                if_true_type=_render(then_value.types),
                if_false_type=_render(else_value.types),
            )

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
