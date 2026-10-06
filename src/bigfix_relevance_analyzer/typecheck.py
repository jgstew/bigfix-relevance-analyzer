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
"Platform" here is one axis over both dialects: the five sampled client
platforms by their bare names, and the three session surfaces as
``session:console`` / ``session:rest_api`` / ``session:web_reports``. Session
relevance used to report nothing at all on this axis, which read as "no answer"
when the dumps had one. A statement whose inspectors every dialect defines is
viable in all eight, and says so.

Where the dumps' coverage is uneven the axis widens rather than narrows -- only
the REST API dump captured session casts and operators, so the console and Web
Reports surfaces are not counted out of them; see
:attr:`~bigfix_relevance_analyzer.inspectors.Inspector.contexts`.

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
import functools
import itertools
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from types import MappingProxyType
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
from bigfix_relevance_analyzer.tokenizer import code_tokens

__all__ = [
    "SINGULAR_REQUIRED",
    "CheckResult",
    "Plurality",
    "RelevanceValue",
    "TypeDiagnostic",
    "TypeEnvironment",
    "TypeFix",
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

    tuple_types: frozenset[str] = frozenset()
    """Tuple spellings this value also answers to, when it is a tuple.

    A tuple is two things at once as far as the tables are concerned. Its
    elements have types -- which is what `item 2 of (...)` and the operators
    read -- but the tables also name the tuple *itself*, as `( string, string
    )`, and a handful of rows take one in that form: `attr lists of <( string,
    string )>`, `substring <( integer, integer )> of <string>`. Flattening the
    elements into :attr:`types` loses that name and the row stops matching,
    which is the whole reason this field exists.

    It is kept beside :attr:`types` rather than replacing it because only the
    property lookup is known to want the tuple name. The operator tables carry
    no tuple rows at all, so a value that answered *only* to `( string, string
    )` would make `("a", "b") = ("a", "b")` a fresh false positive -- trading
    one for another. Additive, the lookup gains a candidate and nothing loses
    one. See :func:`_subject`.
    """

    platforms: frozenset[str] = frozenset()
    """The evaluation contexts in which this reading is viable.

    Client platforms by their bare name and session surfaces as
    ``session:<context>`` -- see
    :attr:`~bigfix_relevance_analyzer.inspectors.Inspector.contexts`, whose
    spelling this carries. Named ``platforms`` because that is what it is on
    the client side, which is most of what anyone reads it for, and because the
    name is the public JSON key.

    Reported, never enforced -- see the module docstring.
    """

    @property
    def known(self) -> bool:
        return self.types is not None


@dataclass(frozen=True, slots=True)
class TypeFix:
    """A textual rewrite that resolves one diagnostic, as the checker sees it.

    The checker has no source text -- only spans -- so this is a proposal, not
    an edit: :mod:`~bigfix_relevance_analyzer.autofix` trims whitespace off
    ``text[start:end]`` and applies :attr:`replacement` only when what is left
    reads as :attr:`expected` (case-insensitively, whitespace-normalized), so
    a span that does not cover the name it claims to -- a comment between two
    words of a phrase -- is skipped rather than mangled.

    Two shapes, one record. A *respelling* replaces only a name: the range is
    the name as written and :attr:`expected` is that name. A *wrap* -- the
    `unique value of` fix for a :data:`SINGULAR_REQUIRED` diagnostic --
    replaces the whole operand: the range is the operand, :attr:`expected` is
    its text as written, and :attr:`replacement` is that same text behind
    `unique value of`, parenthesized where it has to be. The whole-operand
    form, rather than an insertion at either end, keeps a fix one range, so
    anchoring, overlap and offsets work exactly as they do for a respelling;
    the price is that the checker needs the source text to write one (see
    :func:`check`).
    """

    start: int
    """0-based offset of the range to replace, inclusive."""

    end: int
    """0-based offset of the range to replace, exclusive. May include trailing
    whitespace; see the class docstring."""

    replacement: str

    expected: str
    """The phrase the range is expected to hold, as the checker read it."""


@dataclass(frozen=True, slots=True)
class TypeDiagnostic:
    """One finding, in the engine's own wording."""

    code: str
    """The key in :data:`~bigfix_relevance_analyzer.diagnostics.DIAGNOSTICS`."""

    message: str
    span: Span

    fix: TypeFix | None = None
    """How to rewrite the text so this diagnostic goes away, when that is
    mechanical and meaning-preserving. Two kinds set one.
    `singular-spelling-mid-chain`: the plural spelling answers the same values
    where the singular answers, and answers empty where it errors.
    `filtered-singular-spelling` deliberately does not -- it fires in singular
    contexts, where the plural spelling would trade it for
    `singular-over-plural-object` or worse. And the :data:`SINGULAR_REQUIRED`
    codes: the original never runs, the engine refusing it up front, so a
    rewrite that runs whenever there is one value cannot be worse.

    Not part of :meth:`to_dict`; the analysis payload's ``autofix`` key is the
    rewrite a consumer should read, worked out over every fix at once.
    """

    def to_dict(self) -> dict[str, Any]:
        """This diagnostic as JSON-serializable plain data."""
        return {"code": self.code, "message": self.message, **_span(self.span)}


@dataclass(frozen=True, slots=True)
class CheckResult:
    """What :func:`check` produced."""

    value: RelevanceValue
    diagnostics: tuple[TypeDiagnostic, ...] = ()

    resolutions: Mapping[int, tuple[inspectors.Inspector, ...]] = field(
        default_factory=lambda: MappingProxyType({}), repr=False
    )
    """Which table rows each `Reference` actually resolved to, keyed by ``id``.

    The narrowing :func:`resolve_property` performs is otherwise thrown away:
    the walk keeps the resulting types and discards the rows that produced
    them, so a caller wanting to say *why* a name typed the way it did had to
    look it up again bare -- and got the union over every overload rather than
    the one the direct object selected.

    Keyed by ``id`` of the node, so it is only meaningful while the tree that
    was checked is still alive. That is the whole of its intended use: a
    consumer reads it during the same call that produced the tree. It is walk
    state rather than a finding, so it is deliberately absent from
    :meth:`to_dict`. Absent for a reference the walk never resolved -- one
    suppressed by another finding, or reached through a context that was
    itself unresolved.
    """

    def __getstate__(self) -> tuple[object, object, dict[int, tuple[inspectors.Inspector, ...]]]:
        """Unwrap the read-only view so the result can cross a process boundary.

        A ``mappingproxy`` is not picklable, and a report that cannot be
        pickled cannot be returned from a worker pool. Note the standing caveat
        on :attr:`resolutions`: its keys are ``id()`` values of the checked
        tree, so they do not mean anything on the far side of a pickle --
        the tree there is a different object. Carrying them is what this
        class has always done; reading them after a round trip is not.
        """
        return (self.value, self.diagnostics, dict(self.resolutions))

    def __setstate__(
        self, state: tuple[object, object, dict[int, tuple[inspectors.Inspector, ...]]]
    ) -> None:
        """Rebuild, restoring the read-only view rather than a bare dict."""
        value, diagnostics, resolutions = state
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "resolutions", MappingProxyType(resolutions))

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

        `world-property-not-defined` is the one advisory that carries the
        type-check origin -- the dumps knowing a name only with a direct
        object does not prove it has no top-level definition in a context the
        dumps do not cover (proxy agent inspectors) -- so it is excluded by
        code rather than by origin. :func:`_is_type_error` is where that line
        is drawn, so the ``if`` rule counting branch errors draws it too.
        """
        return not any(_is_type_error(diagnostic) for diagnostic in self.diagnostics)

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
            # A tuple is typed by its own spelling, as the engine types it (#69).
            "types": (
                sorted(self.value.tuple_types)
                if self.value.tuple_types
                else None
                if self.value.types is None
                else sorted(self.value.types)
            ),
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
        """Every context in play -- all of them, or just the one selected.

        Both dialects, always. The axis used to be client-only, which left
        session relevance reporting an empty set and the report explaining the
        emptiness away in prose; the dumps record session availability just as
        precisely, so there was nothing to explain.
        """
        if self.platform is not None:
            return frozenset({self.platform})
        return self._all_platforms or _platform_universe()

    def visible(self, entry: inspectors.Inspector) -> bool:
        """Whether this row counts, given the dialect and platform selected."""
        if self.dialect not in entry.dialects:
            return False
        if self.platform is not None:
            return self.platform in entry.contexts
        return True

    def platforms_of(self, entries: list[inspectors.Inspector]) -> frozenset[str]:
        return inspectors._contexts_of(entries) & self.universe


def _client_platforms() -> frozenset[str]:
    """The client half of the context universe, for the one rule that reasons
    about "could one machine take both branches" -- see
    :meth:`_Checker.branches_coexist`. Derived, and cached, by the same
    function that spells :attr:`~bigfix_relevance_analyzer.inspectors.Inspector.platforms`."""
    return inspectors._platforms_for(frozenset(inspectors.sources()))


def _platform_universe() -> frozenset[str]:
    """Every context the dumps name, spelled the way
    :attr:`~bigfix_relevance_analyzer.inspectors.Inspector.contexts` spells
    them -- by the function that spells those, so the two cannot drift."""
    return inspectors._sampled_contexts_for(frozenset(inspectors.sources()))


def _describe_types(types: frozenset[str] | None) -> str:
    """A type set as a reader sees it: ``unknown``, ``none``, or ``a or b``."""
    if types is None:
        return "unknown"
    if not types:
        return "none"
    return " or ".join(sorted(types))


_STRING_INDEXES: Final = frozenset({"string", "binary_string"})
"""Index types a `;`-separated list of strings can fill, one string at a time."""

STRING_LIST_HINT: Final = (
    ' -- the `,` built one tuple; to pass several values use `;`, as in {phrase} ("a"; "b")'
)
"""Renders the ``{hint}`` slot of ``index-type-not-accepted``."""


def _describe_value(value: RelevanceValue) -> str:
    """A value's type as a reader sees it -- a tuple by its own spelling.

    The engine types a tuple as one ordered, positional thing that keeps
    duplicates and nests: `( version, string, version )`, `( ( integer, string
    ), boolean )`. Its member types, :attr:`RelevanceValue.types`, read as a
    union -- `string or version` -- which is not what it answers (#69).
    """
    if value.tuple_types:
        return " or ".join(sorted(value.tuple_types))
    return _describe_types(value.types)


MAX_TUPLE_SPELLINGS: Final = 8
"""How many tuple spellings one tuple may be given before none is.

An element whose type is a union multiplies the spellings out: `("a", it)`
with `it` a `boolean or string` is both `( string, boolean )` and `( string,
string )`. The product is one or two in every real expression, and the cap is
only a guard against a pathological one. Exceeding it falls back to the
element-flattened reading, which is what this file did before tuple spellings
existed -- a lost match, never a wrong one.
"""


def _tuple_spellings(values: Sequence[RelevanceValue]) -> frozenset[str]:
    """The tables' own names for a tuple built from ``values``, in order.

    The tables write a tuple type `( string, string )` -- one space inside each
    bracket, `, ` between -- and that spelling is what the rows are keyed by,
    so it is reproduced exactly rather than approximated. Order is significant:
    `attr lists of <( string, string )>` and the two `administrator <( bes
    computer, bes user )>` / `<( bes user, bes computer )>` rows are separate
    entries precisely because the engine distinguishes them.

    A nested tuple is spelled as a tuple, not as its members: the engine types
    `((1, "a"), true)` as `( ( integer, string ), boolean )`.

    Empty when any element is untyped, or when the product would exceed
    :data:`MAX_TUPLE_SPELLINGS`.
    """
    if not values or any(not value.types for value in values):
        return frozenset()
    names = [sorted(value.tuple_types or value.types or ()) for value in values]
    total = 1
    for spellings in names:
        total *= len(spellings)
        if total > MAX_TUPLE_SPELLINGS:
            return frozenset()
    return frozenset(
        "( " + ", ".join(combination) + " )" for combination in itertools.product(*names)
    )


def _subject(value: RelevanceValue) -> frozenset[str] | None:
    """The candidate direct-object types ``value`` offers a property lookup.

    Both readings of a tuple at once -- see
    :attr:`RelevanceValue.tuple_types`. ``None`` propagates: an object whose
    own type is undetermined determines nothing about a property of it.
    """
    if value.types is None:
        return None
    return value.types | value.tuple_types


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


_RULED_OUT: Final = RelevanceValue(types=frozenset(), platforms=frozenset())
"""The value of an expression whose every candidate was eliminated -- see
:func:`_ruled_out`. Viable nowhere, since it never evaluates."""


def _either(
    first: RelevanceValue, second: RelevanceValue, *, platforms: frozenset[str]
) -> RelevanceValue:
    """A value that is one of two alternatives, never both: ``|``'s sides, or
    an ``if``'s branches. Either's types, and a plurality only when they agree;
    the caller says where it runs, since that differs between the two."""
    return RelevanceValue(
        types=(None if first.types is None or second.types is None else first.types | second.types),
        plurality=first.plurality if first.plurality is second.plurality else Plurality.UNKNOWN,
        platforms=platforms,
    )


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


#: A *bare* string literal shaped unmistakably like a dotted version -- at least
#: one dot, digits throughout. Deliberately strict, because nothing in the source
#: says this string is a version: `"1.2"` and `"10.20.30"` match, while `"a.b"`,
#: `"1"` and `"1.2-beta"` do not. `"1"` is excluded on purpose -- a bare `"1"` is
#: far more often a number written as a string than a one-component version.
_VERSION_SHAPED = re.compile(r"^\d+(?:\.\d+)+$")

#: The same shape where the source has already *said* `version`, via
#: `version "..."` or `... as version`. The dot becomes optional, because
#: `version "14"` is an ordinary one-component version literal -- and it is
#: exactly the shape that makes a truncating comparison bite hardest.
_VERSION_LITERAL_SHAPED = re.compile(r"^\d+(?:\.\d+)*$")

#: The canonical operators for which component count changes the answer. `>`
#: and `>=` reduce to these by :data:`grammar.CANONICAL_BINARY`'s operand swap,
#: and `!=` to `=` negated, so all six spellings land here. `contains`,
#: `starts with` and `ends with` share the relational binding power but are not
#: orderings, and are excluded.
_ORDERING_OPERATORS = frozenset({"=", "<", "<="})

VERSION = "version"
"""The type name the tables use, and the pivot for the version comparison checks."""


def _version_components(node: Node) -> int | None:
    """How many components a *statically visible* version literal has.

    ``None`` means "not visible from the source", which is the common case: a
    property's value is only known at evaluation. Three spellings are visible,
    and all three appear in real content:

    - ``version "1.2.3"``    -- a ``Reference`` with a string literal index
    - ``"1.2.3" as version`` -- a ``Cast`` whose target is ``version``
    - ``"1.2.3"``            -- a bare literal, coerced by the other operand

    The bar is higher for the bare form. Where the source has written
    ``version`` the string is a version by declaration, so ``version "14"``
    counts as one component; a bare ``"14"`` does not count at all, since
    nothing distinguishes it from a number written as a string.

    A ``pad of`` wrapper is deliberately *not* unwrapped: padding is what makes
    the count irrelevant, and :func:`_is_padded` is what asks about it.
    """
    declared = False
    if isinstance(node, Cast):
        if node.target != VERSION:
            return None
        node, declared = node.operand, True
    elif isinstance(node, Reference) and node.phrase == VERSION and node.index is not None:
        node, declared = node.index, True
    if not isinstance(node, StringLiteral):
        return None
    pattern = _VERSION_LITERAL_SHAPED if declared else _VERSION_SHAPED
    if pattern.match(node.content):
        return node.content.count(".") + 1
    return None


def _indexable_world_collection(name: str, environment: TypeEnvironment, *, indexed: bool) -> bool:
    """Whether a bare world singular is really one of many.

    True when the tables define both an unindexed row for ``name`` and an
    *indexed* row returning the same type. The indexed row is how you pick one
    of the collection -- `filesystem "/"`, `application "Safari.app"` -- so its
    existence says the unindexed spelling has several to choose between, and the
    engine agrees: `name of filesystem` answers one name and then raises
    `Singular expression refers to non-unique object.`

    The same-return-type condition is doing real work, not tidying. Month
    constants have an indexed sibling too -- `april 2026` -- but it returns a
    `date` where bare `april` returns a `month`, so it is a different operation
    rather than a collection index. Bare `april` answers `April` cleanly, and
    without this condition it would be reported. Confirmed on a live engine
    alongside the positives (2026-08-31).

    Deliberately world-level only (``subject`` is always ``None`` here). The
    same reasoning extends to a property of an object -- `key of registry` --
    but every case checked against an engine was world-level, and this package
    does not report on reasoning it has not tested.
    """
    if indexed:
        return False
    bare = _matched_rows(name, None, environment, indexed=False)
    every = _matched_rows(name, None, environment, indexed=None)
    if not bare or not every:
        return False
    returns = {entry.return_type for entry in bare}
    return any(entry.index_type is not None and entry.return_type in returns for entry in every)


def _is_padded(node: Node) -> bool:
    """Whether this operand is a ``pad of ...`` application.

    `pad of` gives both sides the same shape, which is the documented fix for
    the truncating comparison -- so an expression that already uses it must not
    then be warned about. Only the immediate application counts; a `pad of`
    buried under further arithmetic is not the idiom and is not recognised.
    """
    return isinstance(node, Of) and isinstance(node.prop, Reference) and node.prop.phrase == "pad"


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


_COLLAPSE_RISKS: Final = frozenset(
    {"singular-over-plural-object", "singular-of-multivalued-property"}
)
"""The two statically-reported collapse risks; see :meth:`_Checker.accept_collapse`."""

_MULTIVALUED_RISK: Final = frozenset({"singular-of-multivalued-property"})
"""Just the property-side risk, for the sites that exempt only it."""

_FILTERED_RISK: Final = frozenset({"singular-of-filtered-collection"})
"""The `whose`-filtered risk, which only a direct `exists` operand exempts.

Deliberately outside :data:`_COLLAPSE_RISKS` and :data:`_MULTIVALUED_RISK`:
this one survives a singular context, a `whose` predicate, a `|` fallback and
a tuple element, because the engine does not forgive it in any of them. Only
`exists` immediately over the filtered form flattens it away, and only
immediately -- one cast in between and the error is back::

    Q: exists (line whose (it contains "e") of file "<f>")
    A: True
    Q: exists ((line whose (it contains "e") of file "<f>") as string)
    E: Singular expression refers to non-unique object.

which is why :meth:`_Checker.retract_exact` matches the span rather than
containing it. `|` does not rescue it either -- `((line whose (it contains
"e") of file "<f>") as string) | "fallback"` answers with the first line *and*
the error, not the fallback.
"""

_FILTERED_SPELLING: Final = frozenset({"filtered-singular-spelling", "singular-spelling-mid-chain"})
"""The shape rules, retracted left of a `|` -- and only there.

`filtered-singular-spelling` names two things against an indexed filtered
singular: the mid-chain habit, and the *nonexistent* error where the filter
matches nothing. `singular-spelling-mid-chain` names the same pair for an
unfiltered singular a plural is built from. Left of a `|`, that error is not a
hazard -- it is the trigger the fallback is built on: `setting "X" whose
(value of it = "1") of client | ERROR "disabled"` reaches the fallback
*because* the empty case errors. The plural spelling would answer 0 rows
without erroring, the fallback would never run, and the expression would
answer something else -- so here the plural rewrite changes what the
expression means, and the singular is required, not a habit.

A direct `exists` used to retract these too, since the empty case answers
`False` there rather than erroring. It no longer does, by the maintainer's
call: the singular errors again the moment the `exists` is dropped while the
relevance is expanded, one cast in between is enough::

    Q: exists name whose (length of it = 99) of file "/etc/hosts"
    A: False
    Q: exists ((name whose (length of it = 99) of file "/etc/hosts") as string)
    E: Singular expression refers to nonexistent object.

and with a plural property over the singular, `exists` never hid it at all::

    Q: exists values of setting "_zz_none" of client
    E: Singular expression refers to nonexistent object.

`singular-of-filtered-collection` stays under `|`, because the non-unique
error is one `|` genuinely does not rescue (see `_FILTERED_RISK`).
"""


def _written_reference(prop: Node) -> Reference | None:
    """The reference whose written form settles an `of`'s plurality, if any.

    `X whose (P)` speaks with `X`'s own name. A filter does not make a
    singular spelling plural -- the engine settles the phrase by what was
    written and leaves the rest to evaluation, confirmed live in qna::

        Q: (line whose (it contains "<text on one line>") of file "<f>") as string contains "text"
        A: True
        Q: (line whose (it contains "<text on 34 lines>") of file "<f>") as string contains "z"
        A: True
        E: Singular expression refers to non-unique object.
        Q: (lines whose (it contains "<text on one line>") of file "<f>") as string contains "text"
        E: A singular expression is required.

    The singular spelling answers, and only *evaluation* objects, and only
    once the filter has actually matched more than one; the plural spelling is
    rejected statically in the same singular position. So a `whose` is
    transparent here, and its collection is the written form
    :meth:`_Checker.combine_of` must read.
    """
    match prop:
        case Reference():
            return prop
        case Whose(collection=Reference() as collection):
            return collection
        case _:
            return None


def _is_type_error(diagnostic: TypeDiagnostic) -> bool:
    """Whether a diagnostic is a fault rather than a risk.

    The one definition of the line :attr:`CheckResult.ok` draws, for the same
    reason it gives: a runtime risk is something the statement runs *with*,
    not something wrong with it. By origin, except
    ``world-property-not-defined`` -- advisory despite its type-check origin;
    see :attr:`CheckResult.ok`.
    """
    return (
        DIAGNOSTICS[diagnostic.code].origin is Origin.TYPE_CHECK
        and diagnostic.code != "world-property-not-defined"
    )


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


def _respelling(written: Reference, spelling: str) -> TypeFix:
    """Replace the name ``written`` was spelled with -- and only the name.

    The range runs from the reference's start to its index, when it has one
    (`setting "x"` keeps its `"x"`), else to the reference's end.
    """
    end = written.span.end if written.index is None else written.index.span.start
    return TypeFix(start=written.span.start, end=end, replacement=spelling, expected=written.phrase)


SINGULAR_REQUIRED: Final = frozenset(
    {"left-operand-not-singular", "right-operand-not-singular", "argument-not-singular"}
)
"""The engine's `A singular expression is required.`, which it raises before
evaluating anything: an operator, or `|`, handed a plural operand.

Each carries a fix (:func:`_singular_fix`), and the autofix guard lets that
fix -- and only that fix -- change the statement's plurality. Deliberately not
the `*-not-boolean` codes: those fire on a wrong *type* as well, which no
rewrite of the operand's plurality repairs.
"""

_UNIQUE_VALUE: Final = "unique value of "


def _aggregate_singular(phrase: str) -> str | None:
    """The singular spelling of ``phrase``, when it is a plural-spelled
    aggregate that has exactly one.

    Every aggregate qualifies in a singular-required position, not just the
    ones exact everywhere. `concatenations` is one value even over nothing, so
    its singular is exact anywhere; `maxima` answers nothing over nothing where
    `maximum` errors, which matters where a plural is wanted -- but here the
    alternative is `unique value of maxima`, which errors on nothing too. qna::

        Q: maximum of (1;2) whose (it > 5) | 9
        A: 9
        Q: unique value of maxima of (1;2) whose (it > 5) | 9
        A: 9
        Q: number of concatenations ", " of ("a";"b") whose (false)
        A: 1

    and `unique value of unique values of X` is `unique value of X`. The
    singular is the shorter rewrite and keeps the aggregate's own type, where
    `unique value of` answers `<type> with multiplicity`.
    """
    rows = [
        entry
        for entry in inspectors.lookup(phrase, kind=inspectors.InspectorKind.PROPERTY)
        if entry.name in AGGREGATES
    ]
    if not rows or any(entry.name != phrase for entry in rows):
        return None  # not an aggregate, or written in its singular already
    singulars = {entry.singular_name for entry in rows}
    if len(singulars) != 1:
        return None
    (singular,) = singulars
    return singular


def _parenthesized(text: str) -> bool:
    """Whether ``text`` is one parenthesized group, outer parens to outer parens.

    Tokenized rather than matched by character, so a paren inside a string
    literal or a comment does not count: a string is one token, quotes and
    all, and a comment is trivia `code_tokens` leaves out.
    """
    tokens = list(code_tokens(text))
    depth = 0
    for position, token in enumerate(tokens):
        if token.text == "(":
            depth += 1
        elif token.text == ")":
            depth -= 1
            if depth == 0:
                return position == len(tokens) - 1
    return False


def _singular_fix(operand: Node, value: RelevanceValue, source: str | None) -> TypeFix | None:
    """The rewrite for a plural ``operand`` where a singular is required.

    The exact singular spelling of a plural aggregate when the operand is one
    (see :func:`_aggregate_singular`), else the operand behind `unique value
    of`. That runs whenever the operand has one distinct value, and fails on
    none or several just as the singular spelling would -- strictly more
    forgiving, because repeats of one value still work. Whether the operand's
    type takes `unique value of` is left to the autofix guard: a client `file`
    does not and adds `property-not-defined`, a session `bes computer` does.

    Parenthesized unless the operand is a name, an `of` chain or already one
    parenthesized group, all of which `unique value of` takes whole. `None`
    for a tuple, which the engine defines no aggregate on at all -- `unique
    value of ("a", "b")` is `The operator "unique value" is not defined.` --
    and which the checker would not catch, resolving a property of a tuple
    against its elements too. `None` too without ``source``: a wrap copies
    the operand as written.
    """
    if isinstance(operand, Of) and not operand.prop_grouped:
        written = _written_reference(operand.prop)
        if written is not None and (singular := _aggregate_singular(written.phrase)):
            return _respelling(written, singular)
    if source is None or value.tuple_types or isinstance(operand, TupleExpr):
        return None
    text = source[operand.span.start : operand.span.end]
    bare = isinstance(operand, Reference | Of) or _parenthesized(text)
    return TypeFix(
        start=operand.span.start,
        end=operand.span.end,
        replacement=_UNIQUE_VALUE + (text if bare else f"({text})"),
        expected=text,
    )


_VISIBLE_ROWS_CACHE_SIZE: Final = 4096
"""How many ``(name, environment, indexed)`` slices :func:`_visible_rows` keeps.

Bounded because ``name`` comes from parsed relevance, which is untrusted input
for a hook running over arbitrary content. The real working set is small -- 613
entries served 455,492 lookups over a whole content repository.
"""


@functools.lru_cache(maxsize=_VISIBLE_ROWS_CACHE_SIZE)
def _visible_rows(
    name: str, environment: TypeEnvironment, indexed: bool | None
) -> tuple[inspectors.Inspector, ...]:
    """The rows ``name`` has in this dialect and platform, before type narrowing.

    Split out of :func:`_matched_rows` and memoized because this half does not
    vary with the subject: a name's overloads, and which of them the selected
    dialect and platform can see, are fixed for the run. Re-deriving it per
    call meant filtering every overload through
    :meth:`TypeEnvironment.visible` thousands of times -- the single largest
    cost in type checking.

    ``environment`` is a frozen dataclass whose ``_all_platforms`` field is
    excluded from comparison, so it hashes on exactly the ``(dialect,
    platform)`` pair this depends on. A tuple is returned rather than a list
    so a caller cannot mutate the cached slice.
    """
    rows = tuple(
        entry
        for entry in inspectors.lookup(name, kind=inspectors.InspectorKind.PROPERTY)
        if environment.visible(entry)
    )
    if indexed is not None:
        rows = tuple(entry for entry in rows if (entry.index_type is not None) is indexed)
    return rows


def _matched_rows(
    name: str,
    subject: frozenset[str] | None,
    environment: TypeEnvironment,
    *,
    indexed: bool | None = None,
) -> list[inspectors.Inspector] | None:
    """The visible property rows ``name`` resolves to against ``subject``.

    ``None`` when no visible row carries the name at all -- the "not in this
    snapshot" case :func:`resolve_property` must keep distinct from an empty
    match, which *is* a finding. Parameters mean what they mean there.
    """
    rows = _visible_rows(name, environment, indexed)
    if not rows:
        return None

    if subject is None:
        return [entry for entry in rows if not entry.operands]
    return [
        entry
        for entry in rows
        if any(_accepts(operand, candidate) for candidate in subject for operand in entry.operands)
    ]


def _plural_alternative(
    name: str,
    subject: frozenset[str] | None,
    environment: TypeEnvironment,
    *,
    indexed: bool | None = None,
) -> str | None:
    """The plural spelling to suggest for a multivalued property, or ``None``.

    Positive evidence only, the same policy as :func:`resolve_property`'s
    plurality: a suggestion comes back only when every matched visible row is
    recorded as multivalued *and* they all agree on one plural name distinct
    from what was written. `name of <SELinux boolean>` has the plural form
    `names` yet is not multivalued -- the two facts are independent in the
    tables, and only the multivalued ones can raise `Singular expression
    refers to non-unique object.`
    """
    matched = _matched_rows(name, subject, environment, indexed=indexed) or []
    if not all(entry.multivalued for entry in matched):
        return None
    return _sole_plural(matched, name)


def _plural_spelling(
    name: str,
    subject: frozenset[str] | None,
    environment: TypeEnvironment,
    *,
    indexed: bool | None = None,
) -> str | None:
    """The plural name for ``name``, whether or not the tables call it multivalued.

    :func:`_plural_alternative` gates on `multivalued` because it is naming
    the fix for something that *can* raise `Singular expression refers to
    non-unique object.`, and a property that answers exactly one value never
    will. This one names the plural spelling for a filtered form, where the
    hazard is not the question: `file "x" whose (...)` cannot collapse, and
    `files "x" whose (...)` is still the better shape.
    """
    return _sole_plural(_matched_rows(name, subject, environment, indexed=indexed) or [], name)


def _sole_plural(matched: list[inspectors.Inspector], name: str) -> str | None:
    """The one plural name every row in ``matched`` agrees on, when it differs
    from the ``name`` written; ``None`` for no rows, disagreeing rows, or a
    name already plural."""
    plurals = {entry.plural_name for entry in matched}
    if len(plurals) != 1:
        return None
    (plural,) = plurals
    if plural is None or plural.casefold() == name.casefold():
        return None
    return plural


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
    matched = _matched_rows(name, subject, environment, indexed=indexed)
    if matched is None:
        return RelevanceValue(types=None, platforms=environment.universe)

    return RelevanceValue(
        types=frozenset(entry.return_type for entry in matched),
        plurality=_written_plurality(name, matched),
        platforms=environment.platforms_of(matched),
    )


def _written_plurality(name: str, rows: Iterable[inspectors.Inspector]) -> Plurality:
    """The plurality ``name`` is spelled with, when every row agrees on it."""
    forms = {inspectors.written_form_of(entry, name) for entry in rows}
    if forms == {inspectors.WrittenForm.PLURAL}:
        return Plurality.PLURAL
    if forms == {inspectors.WrittenForm.SINGULAR}:
        return Plurality.SINGULAR
    return Plurality.UNKNOWN


def check(node: Node, environment: TypeEnvironment, *, source: str | None = None) -> CheckResult:
    """Type ``node``, reporting findings in the engine's own wording.

    A name the tables do not contain comes back with ``types=None`` rather than
    a guess, and ``None`` propagates without ever becoming an error. The checker
    is quiet about what it cannot reason about rather than wrong about it.

    ``source`` is the text ``node`` was parsed from. Only fixes read it: a
    wrap in `unique value of` copies its operand as written, comments and all,
    and is not proposed without it. Every finding is the same either way.
    """
    checker = _Checker(environment, source)
    value = checker.run(node)
    return CheckResult(
        value=value,
        diagnostics=tuple(checker.diagnostics),
        # A read-only view, not the checker's own dict. The annotation already
        # says `Mapping`; this makes that true at runtime, which matters
        # because a `CheckResult` is shared -- `lint` caches one analysis per
        # distinct statement across a run, so a write here would reach every
        # other site that resolved to the same text.
        resolutions=MappingProxyType(checker.resolutions),
    )


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

    def __init__(self, environment: TypeEnvironment, source: str | None = None) -> None:
        self.env = environment
        self.source = source
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
        # Reference nodes written *as* the property of an `of` -- the ones that
        # named a direct object out loud. See `combine_reference`.
        self.explicit_objects: set[int] = set()
        # Reference nodes written as the property of an `of` but inside their
        # own parentheses, which names no direct object at all.
        self.world_only: set[int] = set()
        # Per-item types, so `item N of (...)` can pick one out after the tuple
        # as a whole has been collapsed to a single value.
        self.tuple_items: dict[int, tuple[RelevanceValue, ...]] = {}
        # Which rows each reference resolved to. See `CheckResult.resolutions`.
        self.resolutions: dict[int, tuple[inspectors.Inspector, ...]] = {}
        # `Of` nodes written as a bare singular spelling that has a plural one,
        # with the fields to report them by. Nothing is wrong with one alone;
        # `report_mid_chain` reports it once its consumer turns out to be
        # building a plural (a plural property of it, or a direct `exists`).
        # The fix rides along because only `combine_of` still has the
        # reference whose written name it replaces.
        self.mid_chain: dict[int, tuple[str, str, TypeFix]] = {}

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

    def report_mid_chain(self, node: Node) -> None:
        """Report ``node`` as `singular-spelling-mid-chain`, if it is one."""
        fields = self.mid_chain.get(id(node))
        if fields is not None:
            phrase, plural_phrase, fix = fields
            # Attached here rather than passed through `report`, whose keyword
            # arguments are message placeholders -- `version-truncating-compare`
            # already has one called `{fix}`.
            diagnostic = _diagnostic(
                "singular-spelling-mid-chain",
                node.span,
                phrase=phrase,
                plural_phrase=plural_phrase,
            )
            self.diagnostics.append(replace(diagnostic, fix=fix))

    def unknown(self) -> RelevanceValue:
        return RelevanceValue(types=None, platforms=self.env.universe)

    def record(self, node: Reference, subject: frozenset[str] | None) -> None:
        """Keep the rows `node` resolved to, for `CheckResult.resolutions`.

        Called with whichever subject actually produced the value returned, so
        a reference rescued by the world fallback records the world's rows
        rather than the ones that failed to match.
        """
        rows = _matched_rows(node.phrase, subject, self.env, indexed=node.index is not None)
        self.resolutions[id(node)] = tuple(rows or ())

    def literal(self, name: str, platforms: frozenset[str] | None = None) -> RelevanceValue:
        """A value of one known type, singular.

        ``platforms`` defaults to the whole universe, which is right for an
        actual literal -- ``"x"`` and ``1`` are readable anywhere the statement
        is. A *computed* fixed type is different: `exists X` answers boolean
        whatever `X` is, but only where `X` itself resolves, so its callers
        pass the set they were built from rather than taking the default. See
        the module docstring's chain rule.
        """
        return RelevanceValue(
            types=frozenset({name}),
            plurality=Plurality.SINGULAR,
            platforms=self.env.universe if platforms is None else platforms,
        )

    def rows(self, entries: tuple[inspectors.Inspector, ...]) -> list[inspectors.Inspector]:
        return [entry for entry in entries if self.env.visible(entry)]

    def from_rows(
        self,
        rows: list[inspectors.Inspector],
        *,
        plurality: Plurality,
        fallback_platforms: frozenset[str],
        types: frozenset[str] | None = None,
    ) -> RelevanceValue:
        """The value an operator or cast yields through the table ``rows`` it
        matched: their return types unless ``types`` overrides them, viable
        where those rows are -- or, when the dumps place none of them, where
        the operands were (``fallback_platforms``)."""
        return RelevanceValue(
            types=frozenset(entry.return_type for entry in rows) if types is None else types,
            plurality=plurality,
            platforms=self.env.platforms_of(rows) or fallback_platforms,
        )

    def retract(self, codes: frozenset[str], span: Span) -> None:
        """Withdraw the already-emitted ``codes`` diagnostics inside ``span``.

        Retraction rather than a check up front, because the walk is an
        iterative work queue: `combine_of` cannot see the parent that will
        consume it, but the consuming site knows the operand's span, and
        containment then identifies the findings that operand raised, however
        deep -- the reported webreport put one two levels down, under a cast.

        The list is edited in place and only above ``span``, which is what
        keeps the `_BeginBranch` marks in :attr:`marks` valid: a finding inside
        this operand was appended after any mark that is still open, so no
        index below one ever moves.
        """
        self.withdraw(codes, lambda found: span.start <= found.start and found.end <= span.end)

    def retract_exact(self, codes: frozenset[str], span: Span) -> None:
        """Withdraw ``codes`` reported on ``span`` itself, not merely inside it.

        The containment :meth:`retract` uses is right for a site that forgives
        everything under it; `exists` is not one, forgiving only the collapse
        it flattens directly (see :data:`_FILTERED_RISK`).
        """
        self.withdraw(codes, lambda found: (found.start, found.end) == (span.start, span.end))

    def withdraw(self, codes: frozenset[str], where: Callable[[Span], bool]) -> None:
        """Drop the ``codes`` diagnostics whose span satisfies ``where``, in place
        -- see :meth:`retract` for why in place."""
        self.diagnostics[:] = [
            diagnostic
            for diagnostic in self.diagnostics
            if not (diagnostic.code in codes and where(diagnostic.span))
        ]

    def accept_collapse(self, span: Span) -> None:
        """Withdraw the collapse risks inside ``span``: something needed them.

        `singular-over-plural-object` says a singular form was written over an
        object that may hold several; `singular-of-multivalued-property` says
        the property itself may answer with several. Where the value flows
        into a position that *requires* a singular, that collapse is what
        makes the expression legal at all, and reporting it would say the
        author should have written something they had no way to write. Every
        site that demands a singular already calls :meth:`require_singular` or
        :meth:`require_singular_boolean` with the operand's span, and those
        delegate here.
        """
        self.retract(_COLLAPSE_RISKS, span)

    def require_singular_boolean(
        self, value: RelevanceValue, span: Span, code: str, **fields: object
    ) -> None:
        """Only complain on positive evidence: an unknown type is not a finding."""
        self.accept_collapse(span)
        if value.types is None or _ruled_out(value):
            return
        if "boolean" not in value.types or value.plurality is Plurality.PLURAL:
            self.report(
                code,
                span,
                plurality=value.plurality.value,
                type=_describe_types(value.types),
                **fields,
            )

    def require_singular(
        self, value: RelevanceValue, operand: Node, code: str, **fields: object
    ) -> None:
        """The engine's `A singular expression is required.`, said precisely.

        Positive evidence only, the same as :meth:`require_singular_boolean`:
        `Plurality.UNKNOWN` is not a finding. Takes the operand itself rather
        than its span, because the fix it attaches reads the node: an
        aggregate is respelled where anything else is wrapped.
        """
        self.accept_collapse(operand.span)
        if value.plurality is Plurality.PLURAL:
            diagnostic = _diagnostic(code, operand.span, **fields)
            # Attached here rather than passed through `report`, as in
            # `report_mid_chain`: its keyword arguments are message fields.
            fix = _singular_fix(operand, value, self.source)
            self.diagnostics.append(diagnostic if fix is None else replace(diagnostic, fix=fix))

    def context_value(self, span: Span) -> RelevanceValue:
        """What `it` refers to here, reporting the unbound case.

        Always singular, however plural the context is: `A of B` evaluates `A`
        once per element of `B`, so `it` is one element and not the collection.
        """
        if not self.contexts:
            self.report("used-without-context", span, token="it")
            return self.unknown()
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
                if isinstance(node, Of) and isinstance(node.prop, Reference):
                    # Written with a direct object, which is what stops the
                    # world fallback in `combine_reference` from rescuing a
                    # world-only name. Only the property *itself* counts: a
                    # reference deeper inside the subtree named no object.
                    #
                    # Unless it was parenthesized, which un-names the object
                    # again: `(A) of B` evaluates `A` on its own with `it`
                    # bound to `B`, so `A` resolves against the world and `B`
                    # is not its direct object. The engine is emphatic in both
                    # directions -- `computer name of file "/etc/hosts"` is
                    # `E: The operator "computer name" is not defined.` while
                    # `(computer name) of file "/etc/hosts"` answers, and
                    # `name of file "/etc/hosts"` answers where `(name) of
                    # file "/etc/hosts"` is `E: ... not defined.`
                    if node.prop_grouped:
                        self.world_only.add(id(node.prop))
                    else:
                        self.explicit_objects.add(id(node.prop))
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
                (operand,) = self.pop(1)
                # Under `exists` the non-unique error genuinely never fires --
                # confirmed live in qna: `exists file of folder "/"` and
                # `exists file of folders "/"` both answer `True`, no error,
                # however many files exist ("Errors propagate, except where a
                # plural flattens them" in the syntax reference). So the
                # property-side risk is retracted here. The object side
                # (`singular-over-plural-object`) is left standing by choice:
                # it does not error under `exists` either, but the spelling is
                # still not ideal relevance, and its message blames the
                # singular context rather than promising an error.
                self.retract(_MULTIVALUED_RISK, node.operand.span)
                # The filtered risk only where `exists` sits directly over it:
                # `exists (line whose (...) of file "<f>")` is clean, and the
                # same form under one cast raises the non-unique error again.
                self.retract_exact(_FILTERED_RISK, node.operand.span)
                # The shape rule is *not* retracted here: a direct `exists`
                # answers `False` where the empty case would have erred, but
                # the singular spelling errors again the moment the `exists`
                # is dropped (see `_FILTERED_SPELLING`). For the same reason
                # a bare singular spelling mid-chain is reported here too.
                self.report_mid_chain(node.operand)
                # Boolean everywhere it can be asked, and it can only be asked
                # where the operand resolves: `exists` swallows a *runtime*
                # nonexistent object, not a missing inspector. Confirmed live
                # in qna on macOS: `exists (1/0)` answers `False`, while
                # `exists key "x" of registry` is `E: The operator "key" is not
                # defined.`
                self.values.append(self.literal("boolean", operand.platforms))
            case NumberOf():
                (operand,) = self.pop(1)
                # The same, for the same reason: `number of applications of
                # registry` on macOS is `E: The operator "applications" is not
                # defined.`, not a count of zero.
                self.values.append(self.literal("integer", operand.platforms))
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
        if isinstance(node, TupleExpr):
            # A tuple element's plurality is load-bearing: a plural item
            # multiplies the tuples out (a cross product), a singular one
            # asserts a single row. Suggesting the plural would change what
            # the expression *means*, not how safely it says it, so the risk
            # is retracted here. `;` items stay: a collection just pools
            # values, and plural elements are the same statement said safely.
            for item in node.items:
                self.retract(_MULTIVALUED_RISK, item.span)
        if any(value.types is None for value in values):
            return self.unknown()
        types: frozenset[str] = frozenset()
        for value in values:
            types |= value.types or frozenset()
        if isinstance(node, TupleExpr):
            tuple_types = _tuple_spellings(values)
        else:
            # Only `,` builds a tuple -- `(a; b)` is two values of one type,
            # not one value of a pair type -- so `;` mints no spelling of its
            # own. But pooling does not strip the items of theirs: each
            # element of `(("a", it); ("b", "c"))` is still a `( string,
            # string )`, so the items' spellings ride along. Verified in qna
            # 11.0.6.137: `attr lists of (("onclick", "x"); ("href", "y"))`
            # evaluates -- aggregating every pair into one attribute list.
            tuple_types = frozenset().union(*(value.tuple_types for value in values))
        # Both spellings need every element, so the platform sets intersect --
        # this is a chain, not a set of alternatives. `,` is obvious: qna
        # `(1, 1/0)` errors. `;` reads as tolerant and is not, for the failure
        # that matters here: `(1; 1/0)` answers `1` *and* reports the error,
        # but `(1; keys of registry)` on macOS is `E: The operator "keys" is
        # not defined.` -- and a platform lacking an inspector is that second
        # case, not the first.
        platforms = self.env.universe
        for value in values:
            platforms &= value.platforms
        return RelevanceValue(
            types=types,
            # A tuple with a plural member is the cross product of its members:
            # `(("a";"b"), 1)` answers twice in the engine (#69).
            plurality=(
                Plurality.PLURAL
                if isinstance(node, Collection)
                else _widen(*(value.plurality for value in values))
            ),
            tuple_types=tuple_types,
            platforms=platforms,
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

        That fallback is for an **implicit** context only. A `whose` surrounds a
        bare reference without claiming the item is what the name belongs to; an
        `of` says exactly that, out loud, and is wrong when it is not true. The
        engine draws the same line, and it is the whole difference between two
        expressions over the same objects::

            number of files whose (exists properties) of folder "/etc"
                                                          -> A: 58
            number of files whose (exists properties of it) of folder "/etc"
                                                          -> E: ... not defined.

        1,372 names resolve as a bare world property on a client and 1,008 of
        those are world-*only*, so falling back for an explicit object would
        silently accept any of them written as `<name> of <anything>`.
        Which reference is which is decided syntactically, at the parent: the
        `prop` of an `of` named an object, anything else did not. It has to be
        the node rather than the context stack, because a reference nested
        inside the property subtree is *not* the one the object was written
        for -- in `(value of setting "x" of client | "none") of setting "y"`,
        the innermost context is explicit but `client` is the object of its own
        inner `of` and still resolves against the world.
        """
        if id(node) in self.suppressed:
            return self.unknown()
        if self.contexts and _ruled_out(self.contexts[-1]):
            return self.contexts[-1]
        # Parenthesized: the object binds `it` and nothing else, so this is a
        # bare world reference that happens to sit left of an `of`. It takes
        # the world path whole -- including the softer finding, since a name
        # the dumps do not know here proves no more than it does anywhere else
        # they are silent -- and skips the unresolved-context guard below,
        # which asks about a direct object this reference does not have.
        world_only = id(node) in self.world_only
        subject = None if world_only else (_subject(self.contexts[-1]) if self.contexts else None)
        if not world_only and self.contexts and subject is None:
            # The context itself is unresolved, so nothing can be concluded
            # about a property of it -- except that a singular-spelled
            # aggregate is one value whatever it consumes. Without this the
            # plural object decides in `combine_of`, and `concatenation "," of
            # (item 1 of it) of <tuples>` -- `a,b` in qna -- reads plural.
            # Only the singular spelling: `concatenations` is statically plural
            # (`"x" & concatenations "" of "a"` is `A singular expression is
            # required.`), but asserting that here cascades through whatever
            # untyped property sits over it, so it keeps deferring to the object.
            if _is_aggregate(node.phrase):
                rows = inspectors.lookup(node.phrase, kind=inspectors.InspectorKind.PROPERTY)
                if _written_plurality(node.phrase, rows) is Plurality.SINGULAR:
                    return replace(self.unknown(), plurality=Plurality.SINGULAR)
            return self.unknown()
        value = resolve_property(node.phrase, subject, self.env, indexed=node.index is not None)
        self.record(node, subject)
        explicit = id(node) in self.explicit_objects
        if subject is not None and not explicit and value.types is not None and not value.types:
            world = resolve_property(node.phrase, None, self.env, indexed=node.index is not None)
            if world.types:
                self.record(node, None)
                return self.check_index(node, index, None, world)
        if value.types is not None and not value.types:
            index_fragment = (
                ""
                if index is None
                else PROPERTY_INDEX_FRAGMENT.format(name=_describe_types(index.types))
            )
            if subject is None:
                # A bare world reference whose name the dumps know only with a
                # direct object. That is not proof of a mistake: the dumps do
                # not cover every evaluation context, and proxy agent
                # inspectors define top-level names (`devices`) that collide
                # with captured operand-taking ones (`device of <grub file
                # location>`). Report the softer finding -- `lint` demotes it
                # to `unknown-inspector` -- and carry on as if the name were
                # not in the snapshot at all, so nothing downstream cascades.
                self.report(
                    "world-property-not-defined",
                    node.span,
                    phrase=node.phrase,
                    index=index_fragment,
                )
                return self.unknown()
            self.report(
                "property-not-defined",
                node.span,
                phrase=node.phrase,
                index=index_fragment,
                direct_object=(
                    ""
                    if subject is None
                    else PROPERTY_DIRECT_OBJECT_FRAGMENT.format(
                        # A tuple names itself. Listing the flattened elements
                        # beside the spelling -- `<( string, string ) or
                        # string>` -- would describe an object the source does
                        # not contain; the tuple spelling alone is what the
                        # tables call it, and how they write it.
                        name=_describe_types(self.contexts[-1].tuple_types or subject)
                    )
                ),
            )
        elif (
            subject is None
            and value.plurality is Plurality.SINGULAR
            and not _is_aggregate(node.phrase)
            and _indexable_world_collection(node.phrase, self.env, indexed=node.index is not None)
        ):
            # A bare world object the tables also define with an index: one of
            # many, written as though it were the only one. Same diagnostic as
            # the `of`-chain case in `combine_of`, because it is the same
            # runtime error about the same mistake -- the object here is the
            # world rather than a plural expression.
            self.report("singular-over-plural-object", node.span, phrase=node.phrase)
        return self.check_index(node, index, subject, value)

    def check_index(
        self,
        node: Reference,
        index: RelevanceValue | None,
        subject: frozenset[str] | None,
        value: RelevanceValue,
    ) -> RelevanceValue:
        """``value``, ruled out when no matched row takes ``index``'s shape (#14).

        Only the tuple-versus-scalar shape is compared, never a scalar's type:
        a string literal satisfies a `<binary_string>` index through a
        conversion this package does not model (see :func:`resolve_property`).
        A tuple has to match a row's tuple spelling exactly -- the engine
        rejects `folders ("a", "b")` and `substring ("a", "b") of "x"` alike
        with `The operator "<name>" is not defined.` -- and a scalar cannot
        fill a row that takes only a tuple (session `private variable "a"`).
        Positive evidence only: an untyped index, or a tuple too ambiguous to
        spell, decides nothing.
        """
        if index is None or index.types is None or not value.types:
            return value
        given = index.tuple_types | {name for name in index.types if name.startswith("(")}
        rows = _matched_rows(node.phrase, subject, self.env, indexed=True) or []
        if not rows:
            return value

        def takes(row: inspectors.Inspector) -> bool:
            assert row.index_type is not None
            if given:
                return row.index_type in given
            return not row.index_type.startswith("(")

        if any(takes(row) for row in rows):
            return value
        accepted = sorted({row.index_type for row in rows if row.index_type is not None})
        # The `,`-for-`;` reading is only justified when a row takes a list
        # element the comma list was presumably meant to supply.
        hint = (
            STRING_LIST_HINT.format(phrase=node.phrase)
            if given and any(row.index_type in _STRING_INDEXES for row in rows)
            else ""
        )
        self.report(
            "index-type-not-accepted",
            node.span,
            phrase=node.phrase,
            index=" or ".join(sorted(given)) if given else _describe_types(index.types),
            accepted=" or ".join(f"<{name}>" for name in accepted),
            hint=hint,
        )
        return replace(value, types=frozenset())

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
        own to speak with -- a cast, a nested `of`, a parenthesized property --
        which is why `(it as string) of files of folder "c:\\"` is plural off a
        singular `it`.
        """
        index = self.bad_tuple_index(node)
        if index is not None:
            self.report("tuple-index-not-literal", node.span, token=index.text)
            return _RULED_OUT

        # `resolve_property` already read the written form; it leaves plurality
        # `UNKNOWN` for a name it could not match, or one whose matched rows
        # disagree, and there the object is still the best evidence there is.
        plurality: Plurality
        # A `whose` is transparent to the written form (`_written_reference`),
        # so `value whose (...) of it` is read here exactly as `value of it`
        # is: same plurality, same risk, same suggested plural spelling.
        # A parenthesized property has no written form to lend this `of`: it is
        # evaluated once per element with `it` bound to that element, so it
        # distributes where the bare spelling would collapse. The engine keeps
        # the two apart sharply::
        #
        #     Q: name of files of folder "/etc"
        #     A: afpovertcp.cfg
        #     E: Singular expression refers to non-unique object.
        #     Q: (name of it) of files of folder "/etc"
        #     A: afpovertcp.cfg
        #     A: aliases
        #     ...
        #
        # so it joins the cast and the nested `of` in the `else` branch below,
        # where the object settles plurality and none of the collapse risks
        # apply.
        written = None if node.prop_grouped else _written_reference(node.prop)
        filtered = written is not None and written is not node.prop
        if written is not None and prop.plurality is not Plurality.UNKNOWN:
            plurality = prop.plurality
            # What every check below asks about the written name, worked out once.
            aggregate = _is_aggregate(written.phrase)
            subject = _subject(obj)
            indexed = written.index is not None
            if (
                plurality is Plurality.SINGULAR
                and obj.plurality is Plurality.PLURAL
                # The filtered form included: `key whose (...) of <plural
                # keys>` carries exactly the risk `key of <plural keys>` does,
                # and qna raises `Singular expression refers to non-unique
                # object.` for both. `exists key whose (...) of (keys "A" of
                # it; keys "B" of it) of registry` is a shipped idiom -- one
                # content site holds 45,000 of them -- and the `exists` does
                # flatten the error away, but only for as long as the `exists`
                # is there and only by luck about how many keys exist today.
                and not aggregate
            ):
                self.report("singular-over-plural-object", node.span, phrase=written.phrase)
            elif (
                plurality is Plurality.SINGULAR
                and obj.plurality is Plurality.SINGULAR
                # An aggregate is exempt over a singular object for the same
                # reason it is over a plural one: `unique value of X` dedups
                # before asserting singularity, so it succeeds exactly where a
                # bare singular form would not. Latent until now -- an `if`
                # branch swallowed its own risks, and `if true then (unique
                # value of "a") else "b"` was the case that hid here.
                and not aggregate
                and (
                    alternative := _plural_alternative(
                        written.phrase, subject, self.env, indexed=indexed
                    )
                )
                is not None
            ):
                # The object holds exactly one, but the tables say the property
                # itself may answer with several -- `file of folder "c:\"` is
                # `Singular expression refers to non-unique object.` the moment
                # a second file exists. Best practice is the plural form unless
                # a singular is required, so the sites that make the singular
                # deliberate retract this: anything `require_singular` guards,
                # a `whose` predicate (elements are handled one at a time
                # there), an `exists` operand, a tuple element, a `|` fallback.
                # A filter asks for a set and then asserts it holds one, which
                # is a sharper claim than a bare singular property makes, and
                # one the author could have written safely -- so it reports as
                # its own code, which `accept_collapse` does not withdraw.
                self.report(
                    "singular-of-filtered-collection"
                    if filtered
                    else "singular-of-multivalued-property",
                    node.span,
                    phrase=written.phrase,
                    plural_phrase=alternative,
                )
            elif (
                filtered
                and not aggregate
                and (
                    spelling := _plural_spelling(written.phrase, subject, self.env, indexed=indexed)
                )
            ):
                # The non-unique error cannot fire here: an index makes `file
                # "x.bes" whose (...) of folder "c:\"` unique whatever the
                # filter says. What is left is the shape -- a singular in the
                # middle of a chain, the habit the two risks above are the
                # consequence of -- plus the empty case, which qna raises as
                # `Singular expression refers to nonexistent object.` where
                # the plural spelling answers 0. Its own rule, since the
                # hazard it names is not the one above.
                self.report(
                    "filtered-singular-spelling",
                    node.span,
                    phrase=written.phrase,
                    plural_phrase=spelling,
                )
            elif (
                plurality is Plurality.SINGULAR
                and not aggregate
                and (
                    spelling := _plural_spelling(written.phrase, subject, self.env, indexed=indexed)
                )
            ):
                # The same habit without a filter, and not yet a finding: a
                # singular that is consumed singularly is the author asserting
                # one. Only a consumer building a plural reports it -- see
                # `report_mid_chain`.
                self.mid_chain[id(node)] = (
                    written.phrase,
                    spelling,
                    _respelling(written, spelling),
                )
            if plurality is Plurality.PLURAL:
                # A plural taken of a singular spelling distributes over its
                # error rather than hiding it, so even `exists values of
                # setting "x" of client` raises when the setting is absent.
                self.report_mid_chain(node.obj)
        else:
            plurality = _widen(prop.plurality, obj.plurality)
        return RelevanceValue(
            types=prop.types,
            plurality=plurality,
            # `of` is right-associative, so the tuple in `attr lists of
            # ("title", it) of <computer>` is not the object of the outer `of`
            # -- it is the *property* of an inner one, evaluated in the
            # computer's context. Applying a context does not stop a tuple
            # being a tuple, so the spelling rides along; without this the
            # outer lookup sees only the flattened elements again.
            tuple_types=prop.tuple_types,
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
        if node.prop.phrase not in grammar.TUPLE_INDEX_WORDS or not isinstance(
            index, NumberLiteral | StringLiteral
        ):
            return None
        return index

    def branches_coexist(self, then_value: RelevanceValue, else_value: RelevanceValue) -> bool:
        """Whether any one platform sees both branches of an `if` at once.

        The type axis has to answer to the platform axis here. Two branches
        with no platform in common are alternatives *by construction* -- one
        reading exists on Windows, the other on Linux -- and their types
        differing is the whole point, not a mistake. Only branches that some
        single platform could take together can disagree about type.

        Deliberately the *client* half of the context axis, not the whole of
        it. The three session dumps are sampled unevenly, so two branches
        sharing no session surface is a gap in the data rather than proof that
        nothing sees both -- and letting the session half in would also let a
        shared session surface make two genuinely Windows-vs-Linux branches
        look simultaneous, silencing a finding this rule exists to keep. Under
        session relevance itself the axis says nothing usable, so every branch
        coexists there, as before.
        """
        if self.env.dialect is not Dialect.CLIENT:
            return True
        return bool(then_value.platforms & else_value.platforms & _client_platforms())

    def combine_whose(
        self, node: Whose, collection: RelevanceValue, predicate: RelevanceValue
    ) -> RelevanceValue:
        """`X whose (P)` -- `X`'s type, filtered.

        The filter must be boolean but **may be plural**, which is the asymmetry
        against an `if` condition. The message reproduces that: it names no
        plurality because the rule does not have one.
        """
        # Inside the predicate the collection is handled one element at a
        # time, so a singular form there is the natural spelling, not a risk
        # -- `files whose (exists version of it)` has nothing to answer for.
        # Only the property-side risk: the object-side one is about a chain
        # the predicate wrote plural-of-plural, which `whose` does not excuse.
        self.retract(_MULTIVALUED_RISK, node.predicate.span)
        if (
            predicate.types is not None
            and not _ruled_out(predicate)
            and "boolean" not in predicate.types
        ):
            self.report(
                "whose-filter-not-boolean",
                node.predicate.span,
                type=_describe_types(predicate.types),
            )
        return RelevanceValue(
            types=collection.types,
            # A filter is transparent to plurality: the collection keeps its
            # own spelling, named or not. See `_written_reference` for the
            # named case's transcript; the unnamed ones behave identically,
            # confirmed live in qna (client engine, 2026-09)::
            #
            #     Q: ((" /p=" & "abcdefgh") whose (length of it > 7)) | "x"
            #     A:  /p=abcdefgh
            #     Q: ((it as string) whose (it contains "z") of 5) | "x"
            #     A: x
            #     Q: ((line 1 of file "/etc/hosts") whose (it contains "z")) | "x"
            #     A: x
            #     Q: ((concatenation of ("a";"b")) whose (it contains "z")) | "x"
            #     A: x
            #     Q: ((if true then "a" else "b") whose (it contains "z")) | "x"
            #     A: x
            #     Q: (("a";"b") whose (length of it > 0)) | "x"
            #     E: A singular expression is required.
            #     Q: ((lines of file "/etc/hosts") whose (it contains "z")) | "x"
            #     E: A singular expression is required.
            #
            # Only a plural collection makes the filter plural. Filtering a
            # singular leaves it singular and merely *risky* -- an empty
            # result raises `Singular expression refers to nonexistent
            # object.` at evaluation, which is precisely the error the `|`
            # fallback idiom is built to catch. Calling the unnamed cases
            # plural instead failed every `(<expr> whose (...)) | <default>`
            # in the wild with a static `A singular expression is required.`
            # the engine does not raise.
            plurality=collection.plurality,
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
                source_type=_describe_types(operand.types),
                token="as",
                cast_name=node.target,
            )
            return _RULED_OUT
        return self.from_rows(
            rows, plurality=operand.plurality, fallback_platforms=operand.platforms
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
            # Only the left operand narrows: both spellings short-circuit, so
            # the right one may never be evaluated. qna: `false and (1 = 1/0)`
            # answers `False` and `true or (1 = 1/0)` answers `True`, while
            # `false or (1 = 1/0)` errors. This is what lets the ordinary guard
            # -- `<platform test> and <platform-specific relevance>` -- be
            # written at all; intersecting would report it viable nowhere.
            return self.literal("boolean", left.platforms)

        # An operator takes one value a side, whatever its types. This is the
        # engine's `A singular expression is required.`, and it is the
        # operator's own rule -- `sizes of it > 1000` inside a `whose` fails
        # here, not on the filter, which may itself be plural.
        self.require_singular(left, node.left, "left-operand-not-singular", token=node.op)
        self.require_singular(right, node.right, "right-operand-not-singular", token=node.op)

        if _ruled_out(left) or _ruled_out(right):
            return _RULED_OUT

        form = grammar.CANONICAL_BINARY.get(node.op)
        if form is None or left.types is None or right.types is None:
            return self.unknown()

        if form.operator in _ORDERING_OPERATORS:
            self.check_version_comparison(node, form, left.types, right.types)

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
                left_type=_describe_types(left.types),
                right_type=_describe_types(right.types),
            )
            return _RULED_OUT

        return self.from_rows(
            rows,
            plurality=Plurality.SINGULAR,
            fallback_platforms=left.platforms & right.platforms,
            types=_BOOLEAN if form.negated else None,
        )

    def check_version_comparison(
        self,
        node: Binary,
        form: grammar.OperatorForm,
        left_types: frozenset[str],
        right_types: frozenset[str],
    ) -> None:
        """The two version-comparison advisories -- gotchas, not defect reports.

        Neither is a type error: the engine accepts these and answers them, on
        purpose. Truncating equality in particular looks like deliberate design
        (see below), so someone may be relying on it. What earns the warning is
        only that the answer commonly differs from what an author who was not
        relying on it would expect, which no other check in this module can say.

        Ordering matters between the two branches. A comparison with a version
        anywhere in it *is* a version comparison -- one `as version` coerces the
        other operand, confirmed on both engines -- so the truncation branch has
        to be considered first, and the string-compare branch only applies when
        neither side is a version at all.

        **Only half the operators are actually affected by truncation**, which is
        what keeps this rule quiet enough to be worth having. Truncation makes
        the engine treat `1.2.3` and `1.2` as *equal*, so it only changes the
        answer for the operators that turn on equality in the direction of the
        discarded tail. Confirmed exhaustively on a live engine (2026-08-31):

        ==============  ==================  ==================
        operator        left is longer      right is longer
        ==============  ==================  ==================
        ``>``           **affected**        unaffected
        ``>=``          unaffected          **affected**
        ``<``           unaffected          **affected**
        ``<=``          **affected**        unaffected
        ``=`` / ``!=``  **affected**        **affected**
        ==============  ==================  ==================

        For `=`, being affected reads as deliberate design -- it is what lets
        `version "1.2.3" = version "1.2"` work as a prefix match, with no
        separate `starts with`-for-versions operator needed. Applied to the
        ordering operators the same rule falls out as a side effect, producing
        an answer that differs from full-precision comparison for exactly half
        the possible directions. That is a gotcha worth flagging, not proof the
        engine misbehaves.

        The dropped tail can only make its side *larger*, so the side that loses
        it is under-valued, and only a comparison that would flip at equality is
        affected. This is why `version of operating system >= version "5.1"` --
        the shape most real content uses, and three of this repo's own example
        files -- is left alone, while
        `version of operating system > version "14"` (`False` on a 14.6.1 host,
        the case this rule warns on) is reported.
        """
        left_count = _version_components(node.left)
        right_count = _version_components(node.right)

        if VERSION in left_types or VERSION in right_types:
            # `pad of` on both sides is the documented fix; having taken it,
            # the author is owed silence.
            if _is_padded(node.left) and _is_padded(node.right):
                return
            # With no literal on either side there is nothing to anchor the
            # claim to: two properties may well hold the same shape, and
            # warning on every such comparison would be noise rather than
            # evidence.
            if left_count is None and right_count is None:
                return
            if left_count == right_count:
                return  # nothing is truncated away

            # Which side loses its tail. An unknown count is taken to be the
            # longer one: it is a property, and a real version carries more
            # components than the threshold literal it is tested against.
            if left_count is None:
                left_loses = True
            elif right_count is None:
                left_loses = False
            else:
                left_loses = left_count > right_count

            # `=` and `!=` are affected whichever side is longer: the engine calls
            # unequal versions equal, which is also what makes truncating equality
            # useful as a deliberate prefix match. `form.operator` is `=` for
            # both, since a negation keeps the canonical operator. `pad of` is
            # the only fix here -- there is no single other operator that would
            # do instead.
            if form.operator == "=":
                self.report(
                    "version-truncating-compare",
                    node.span,
                    token=node.op,
                    fix="use 'pad of' on both sides",
                )
                return

            # `form.swapped` is what separates `>` from `<` and `>=` from `<=`,
            # since `>` has no row of its own and reduces to a swapped `<`.
            strict = form.operator == "<"
            affected = (strict == form.swapped) if left_loses else (strict != form.swapped)
            if affected:
                # `>` (and its word form `is greater than`) is `form.operator ==
                # "<"` with `swapped` set -- the one case in this branch with an
                # obvious, more-common one-operator fix than `pad of`: the
                # author almost always meant `>=`, the idiom the unaffected half
                # of this same table uses. The other three affected spellings
                # (`>=`, `<`, `<=`) keep the general `pad of` suggestion.
                fix = (
                    "did you mean '>='?"
                    if strict and form.swapped
                    else "use 'pad of' on both sides"
                )
                self.report("version-truncating-compare", node.span, token=node.op, fix=fix)
            return

        # No version anywhere, and both sides are dotted-numeric literals: the
        # engine compares them as strings, so `"2.10.1" < "2.3.3"`.
        if left_count is not None and right_count is not None:
            self.report("version-like-string-compare", node.span, token=node.op)

    def combine_unary(self, node: Unary, operand: RelevanceValue) -> RelevanceValue:
        if node.op == "not":
            self.require_singular_boolean(
                operand, node.operand.span, "argument-not-boolean", token="not"
            )
            # `not` evaluates its operand -- qna: `not (1 = 1/0)` errors rather
            # than answering -- so it runs only where the operand does.
            return self.literal("boolean", operand.platforms)
        self.require_singular(operand, node.operand, "argument-not-singular", token=node.op)
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
                argument_type=_describe_types(operand.types),
            )
            return _RULED_OUT
        return self.from_rows(
            rows, plurality=operand.plurality, fallback_platforms=operand.platforms
        )

    def combine_bar(self, node: Bar, left: RelevanceValue, right: RelevanceValue) -> RelevanceValue:
        # Both operands must be singular, and the engine refuses a plural
        # before evaluating anything -- the absent `T:` line marks a
        # compile-time refusal rather than a runtime error. Confirmed on both
        # engines, so this is not dialect-gated::
        #
        #     Q: (names of files of folder "/etc") | "x"
        #     E: A singular expression is required.
        #     Q: "x" | (names of files of folder "/etc")
        #     E: A singular expression is required.
        #
        # This is also *why* the fallback idiom is inherently singular: the
        # missing case has to arrive as an error to trip the fallback, and a
        # plural that finds nothing answers 0 values rather than erroring.
        #
        # `require_singular` delegates to `accept_collapse`, so the retraction
        # a fallback earns rides along with the check: `a | b` yields `b` when
        # `a` errored, making a collapse risk inside `a` one the author has
        # already answered -- the corpus's `free space of drives of system
        # folders | 0`. The right operand earns it for the plainer reason
        # every `require_singular` site does: a position that demands a
        # singular cannot also advise writing the plural.
        self.require_singular(left, node.left, "left-operand-not-singular", token="|")
        self.require_singular(right, node.right, "right-operand-not-singular", token="|")
        # The shape rule too, and only on the left: there the empty case
        # erroring is the mechanism the fallback runs on, and the suggested
        # plural spelling would answer 0 rows without tripping it (see
        # `_FILTERED_SPELLING`). Nothing on the right needs the error.
        self.retract(_FILTERED_SPELLING, node.left.span)

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
                left_type=_describe_types(left.types),
                right_type=_describe_types(right.types),
            )
        # Error fallback is an alternative: either side may be the one that runs.
        return _either(left, right, platforms=left.platforms | right.platforms)

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
            return _RULED_OUT
        if node.index.kind is NumberKind.LARGE_INTEGER:
            self.report("tuple-index-unreasonable", node.span, token=node.index.text)
            return _RULED_OUT
        # A `whose` filters the tuples without changing what any one position
        # holds, so `items 1 of (a, b) whose (...)` indexes the same tuple.
        subscripted = node.operand
        while isinstance(subscripted, Whose):
            subscripted = subscripted.collection
        if not isinstance(subscripted, TupleExpr):
            # It may still be a tuple-valued expression; nothing is known yet.
            return self.unknown()
        items = self.tuple_items.get(id(subscripted), ())
        index = int(node.index.text)
        if index >= len(items):  # 0-based, checked while type checking
            self.report(
                "tuple-index-out-of-range", node.span, token=node.index.text, total=len(items)
            )
            return _RULED_OUT
        picked = items[index]
        # The plural spelling answers plurally whatever it indexed -- the
        # engine reads that off the phrase, not off the tuple (see
        # `ItemOf.plural`) -- and indexing a plural object is plural too.
        if (operand.plurality is Plurality.PLURAL or node.plural) and (
            picked.plurality is not Plurality.PLURAL
        ):
            return replace(picked, plurality=Plurality.PLURAL)
        return picked

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
        # "at most one branch may have *type errors*" is what the rule says,
        # and a runtime risk is not one -- `CheckResult.ok` draws the same
        # line by origin. Counting risks here made a statement whose branches
        # each hold a `singular-over-plural-object` warning report a type
        # error, which is the opposite of what either diagnostic means: 164
        # sites in one shipped content site failed that way.
        then_errors = [entry for entry in then_found if _is_type_error(entry)]
        else_errors = [entry for entry in else_found if _is_type_error(entry)]
        if then_errors and else_errors:
            self.report("both-if-branches-have-type-errors", node.span)
            self.diagnostics.extend(then_found)
            self.diagnostics.extend(else_found)
        else:
            # A branch's *errors* are tolerated -- one branch is allowed not
            # to type, because it may be the one that never runs on this platform
            # -- but its risks are about the code as written, whichever branch
            # runs, so they are not swallowed with them.
            self.diagnostics.extend(
                entry for entry in then_found + else_found if not _is_type_error(entry)
            )

        if (
            then_value.types
            and else_value.types
            and not _types_compatible(then_value.types, else_value.types)
            and not (then_errors or else_errors)
            and self.branches_coexist(then_value, else_value)
        ):
            # Both branches typed cleanly and share nothing: the statement has
            # no single type, whichever branch runs.
            self.report(
                "if-branch-types-incompatible",
                node.span,
                if_true_type=_describe_types(then_value.types),
                if_false_type=_describe_types(else_value.types),
            )

        # Alternatives: only one branch ever runs, so the statement covers
        # the union of what its branches cover -- qna on macOS, where
        # `registry` does not exist: `if false then (exists key "x" of
        # registry) else true` answers `True`, the untaken branch's missing
        # inspector tolerated. The condition gets no such tolerance: it
        # runs every time, so it narrows the union.
        return _either(
            then_value,
            else_value,
            platforms=condition.platforms & (then_value.platforms | else_value.platforms),
        )


_NUMBER_TYPES = {
    NumberKind.INTEGER: "integer",
    NumberKind.LARGE_INTEGER: "large integer",
    # Unreachable from any tokenized `NumberLiteral` -- relevance has no
    # decimal-point numeral syntax, so `kind` can no longer return this. Kept
    # so the mapping stays total over every `NumberKind`; see its docstring.
    NumberKind.NOT_AN_INTEGER: "floating point",
}
