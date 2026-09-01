"""The inspectors BigFix relevance defines, as a structured, queryable table.

Relevance has no published grammar, and the hard part of parsing it is that the
language has **no reserved words and multi-word inspector names**: nothing about
the text of ``logged on users of bes computers`` says where one name ends and
the next begins. That ambiguity is resolved with a name table, which makes this
module a prerequisite for the parser rather than something built on top of one.

Four introspection categories are represented as :class:`Inspector` rows --
properties, casts, binary operators and unary operators -- plus the type
universe as :class:`RelevanceType`. Each row records the **sources** that
defined it (which client platforms, which session surfaces), so nothing is
collapsed into a bare "client or session" verdict that a later consumer would
have to regenerate the table to recover.

The data is generated from the dumps in
``tests/examples/relevance_inspectors/`` into
:mod:`bigfix_relevance_analyzer._inspector_data`; see
``tools/generate_inspector_data.py``. Tables are parsed lazily and cached, so
importing this module costs only the data module's own load -- a few
milliseconds cold, and effectively nothing once bytecode is cached.

That laziness is what makes the module cheap to reach. The package root does
import it -- :func:`lookup`, :func:`search` and the row types are re-exported
from there, because a consumer answering a question about a name should not have
to know which submodule holds it -- but importing the package still does not
parse a table. The first call does. Either spelling works, and neither costs
anything until you ask a question::

    from bigfix_relevance_analyzer import inspectors    # or: ... import lookup

What this table is not
----------------------
It is a **snapshot**, not a specification. New BigFix versions add inspectors,
and the dumps cover the platforms and surfaces someone happened to capture --
see the dump README for the gaps. So absence from this table is never proof that
a name is invalid: it is grounds for a warning at most. Only *positive* evidence
should ever be drawn from it, the same discipline
:mod:`bigfix_relevance_analyzer.dialect` applies to dialect markers.
"""

from __future__ import annotations

import difflib
import enum
import functools
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from bigfix_relevance_analyzer import _inspector_data
from bigfix_relevance_analyzer._serialize import _enums, _names
from bigfix_relevance_analyzer.dialect import Dialect

__all__ = [
    "SIGNATURE_SAMPLE",
    "Inspector",
    "InspectorKind",
    "MatchKind",
    "RelevanceType",
    "SearchResult",
    "WrittenForm",
    "ancestors",
    "binary_operators",
    "casts",
    "inspector_names",
    "known_types",
    "lookup",
    "properties",
    "search",
    "sources",
    "suggest",
    "unary_operators",
    "written_form_of",
    "written_forms",
]


class WrittenForm(enum.Enum):
    """Which spelling of an inspector an expression used."""

    SINGULAR = "singular"
    PLURAL = "plural"
    UNKNOWN = "unknown"
    """The row records no name matching what was written -- an older dump that
    predates the singular/plural capture, or a match on the signature's own
    form only."""


class InspectorKind(enum.Enum):
    """Which introspection category a row came from."""

    PROPERTY = "property"
    """A named property, e.g. ``windows of <operating system>``."""

    CAST = "cast"
    """An ``as`` conversion, e.g. ``<string> as trimmed string``."""

    BINARY_OPERATOR = "binary-operator"
    """An infix operator, e.g. ``<string> starts with <string>``."""

    UNARY_OPERATOR = "unary-operator"
    """A prefix operator; in practice only ``-``."""


@dataclass(frozen=True, slots=True)
class _Sourced:
    """Something attributed to the set of dumps that defined it."""

    sources: frozenset[str]
    """Source labels from :data:`_inspector_data.SOURCES`, e.g. ``client:windows``."""

    @property
    def dialects(self) -> frozenset[Dialect]:
        """Which dialects define this, derived from :attr:`sources`."""
        found = set()
        for source in self.sources:
            dialect, _, _context = source.partition(":")
            if dialect == "client":
                found.add(Dialect.CLIENT)
            elif dialect == "session":
                found.add(Dialect.SESSION)
        return frozenset(found)

    @property
    def platforms(self) -> frozenset[str]:
        """The client platforms that define this, e.g. ``{"windows", "macos"}``.

        Empty for something no client dump defines. A platform missing here has
        not necessarily been ruled out -- it may simply never have been
        captured; see the dump README for which platforms exist.
        """
        return frozenset(
            context
            for source in self.sources
            for dialect, _, context in [source.partition(":")]
            if dialect == "client" and context
        )

    @property
    def contexts(self) -> frozenset[str]:
        """Where this can evaluate, as the analysis reports it.

        The same set as :attr:`sampled_contexts` for anything not carrying an
        introspection category to reason about; :class:`Inspector` overrides
        this to apply the sampling discipline its :attr:`~Inspector.kind`
        makes possible.
        """
        return self.sampled_contexts

    @property
    def sampled_contexts(self) -> frozenset[str]:
        """Every evaluation context whose dump literally carries this row.

        The axis the analysis reports against, where :attr:`platforms` is the
        narrower table fact behind half of it. Client contexts keep their bare
        platform name -- ``windows``, ``macos`` -- and session contexts keep
        the ``session:`` prefix of their source label, because a bare
        ``console`` sitting in a list beside ``macos`` reads as a platform and
        is not one.

        Session availability is recorded with exactly the same fidelity as
        client availability -- one bit per dump in the same mask -- so leaving
        it out of the axis threw away an answer the tables already had.

        Literal, so a context missing here has not been ruled out -- it may
        simply never have been captured. :attr:`Inspector.contexts` is the
        reporting axis, and applies that discipline for the one gap that is
        systematic rather than incidental.
        """
        return frozenset(
            context if dialect == "client" else source
            for source in self.sources
            for dialect, _, context in [source.partition(":")]
            if context
        )


@dataclass(frozen=True, slots=True)
class Inspector(_Sourced):
    """One inspector signature, as BigFix reported it."""

    kind: InspectorKind
    """Which introspection category this came from."""

    signature: str
    """The signature verbatim, e.g. ``key <string> of <registry>``."""

    name: str
    """The identifying phrase, with types and operators stripped.

    For a property this is its name (``key``, from ``key <string> of
    <registry>``); for a cast, the target of the conversion (``trimmed
    string``, from ``<string> as trimmed string``); for an operator, the
    operator itself (``starts with``, ``&``).
    """

    return_type: str
    """The name of the type this evaluates to."""

    index_type: str | None = None
    """The bracketed argument between name and object, if any.

    ``string`` in ``key <string> of <registry>``. Properties are
    the only category that has one, and never more than one.
    """

    operands: tuple[str, ...] = ()
    """The type names this applies to, in signature order.

    A property's direct object (``registry``), or ``()`` when it is global like
    ``bes computers``. A cast's source type. A binary operator's left and
    right. A unary operator's single operand.
    """

    singular_name: str | None = None
    """A property's singular written form, e.g. ``key``.

    From the session engine's own introspection of the ``property`` type
    (``singular name of <property>``) -- see
    ``session_relevance_properties_rest_api.txt``. ``None`` for dumps that
    predate this capture, which is every client dump today.
    """

    plural_name: str | None = None
    """A property's plural written form, e.g. ``keys``. See :attr:`singular_name`."""

    usual_name: str | None = None
    """Which form -- singular or plural -- this row is normally written as.

    ``plural name`` when :attr:`multivalued`, ``singular name`` otherwise; the
    engine computes it directly (``usual name of <property>``) rather than
    this package deriving it, so it survives if that rule ever changes.
    """

    multivalued: bool | None = None
    """Whether this property yields multiple values per input.

    This is the plurality fact the earlier, signature-only dumps could not
    carry: ``key <string> of <json value>`` and ``keys of <json value>`` are
    the same property with :attr:`singular_name` and :attr:`plural_name`
    swapped as :attr:`usual_name`, distinguished only by this flag.
    """

    written_name: str | None = None
    """A binary or unary operator's written name, e.g. ``mod`` for ``%``.

    :attr:`name` stays the symbol-shaped text the signature itself uses (see
    its docstring) so existing lookups by symbol keep working; this is the
    separate spoken form the session engine's own introspection reports
    (``name of <binary operator>``), not recoverable from the signature.
    """

    symbol: str | None = None
    """A binary or unary operator's engine-reported symbol, e.g. ``%``.

    Usually identical to :attr:`name`; kept distinct because the two are
    conceptually different fields upstream (``symbol of <binary operator>``).
    """

    @property
    def contexts(self) -> frozenset[str]:
        """Where this row can evaluate, as the analysis reports it.

        :attr:`sampled_contexts`, widened by the contexts that never sampled
        this row's :attr:`kind` at all. Only the REST API dump captured casts
        and operators session-side; the console and Web Reports dumps are
        `properties` only. Reading their silence as an absence collapses every
        session statement using an operator -- which is nearly all of them --
        to `session:rest_api`, reporting a fact about our dumps as a fact about
        BigFix.

        The widening is per *dialect*, so it never invents a presence: a row
        no session dump defines gains no session context, because there the
        silence is the properties dumps' and they did sample it.
        """
        found = self.sampled_contexts
        return found | frozenset(
            context
            for dialect in self.dialects
            for context in _unsampled_contexts(self.kind)
            if _dialect_of_context(context) is dialect
        )

    def to_dict(self) -> dict[str, Any]:
        """This inspector as JSON-serializable plain data.

        Every field, plus the three derived facts a consumer would otherwise
        have to rebuild: :func:`written_forms` (the spellings this is actually
        written as), and :attr:`dialects` / :attr:`platforms`, which mean
        re-parsing ``"client:windows"`` strings by hand if they are not here.
        ``sources`` stays too -- it is the evidence those two are derived from,
        and a consumer auditing a surprising answer wants it.

        The ``None``-valued fields are emitted, not dropped. ``multivalued`` is
        why: ``None`` there means the dump that defined this row predates the
        capture that reports plurality, which is a different statement from
        ``false``. See :mod:`bigfix_relevance_analyzer._serialize`.
        """
        return {
            "kind": self.kind.value,
            "signature": self.signature,
            "name": self.name,
            "return_type": self.return_type,
            "index_type": self.index_type,
            "operands": list(self.operands),
            "singular_name": self.singular_name,
            "plural_name": self.plural_name,
            "usual_name": self.usual_name,
            "multivalued": self.multivalued,
            "written_name": self.written_name,
            "symbol": self.symbol,
            "written_forms": list(written_forms(self)),
            "sources": _names(self.sources),
            "dialects": _enums(self.dialects),
            "platforms": _names(self.platforms),
        }


@dataclass(frozen=True, slots=True)
class RelevanceType(_Sourced):
    """One type name in the relevance type universe."""

    name: str
    """The type name, e.g. ``bes computer``, ``registry key``, ``string``."""

    parent: str | None = None
    """This type's supertype, e.g. ``string`` for ``substring``.

    From the session engine's own introspection (``parent of <type>``) --
    see ``session_relevance_types_rest_api.txt``. ``None`` for a root type
    (``string`` itself has none) or for a dump that predates this capture.
    Every ``X with multiplicity`` type is a child of ``X``, which is how
    plurality is expressed in the type system itself.
    """

    size: int | None = None
    """This type's internal size, in bytes, when the engine reports one."""

    def to_dict(self) -> dict[str, Any]:
        """This type as JSON-serializable plain data.

        ``ancestors`` is the walk up to the root, resolved here via
        :func:`ancestors` so a consumer does not have to follow :attr:`parent`
        one lookup at a time across a wire.
        """
        return {
            "name": self.name,
            "parent": self.parent,
            "size": self.size,
            "ancestors": list(ancestors(self.name)),
            "sources": _names(self.sources),
            "dialects": _enums(self.dialects),
            "platforms": _names(self.platforms),
        }


# ---------------------------------------------------------------------------
# Signature parsing
# ---------------------------------------------------------------------------

# A property is `NAME[ <INDEX>][ of <OBJECT>]`. `name` cannot contain `<`, and
# the trailing groups are anchored, so backtracking settles names that contain
# the word "of" on their own (`day of month of <date>` is `day of month` of a
# date, not `day` of something).
_PROPERTY_RE = re.compile(r"^(?P<name>[^<]+?)(?P<index>(?: <[^>]+>)*)(?: of (?P<object><[^>]+>))?$")
_CAST_RE = re.compile(r"^<(?P<source>[^>]+)> as (?P<name>.+)$")
_BINARY_RE = re.compile(r"^<(?P<left>[^>]+)> (?P<name>.+?) <(?P<right>[^>]+)>$")
_UNARY_RE = re.compile(r"^(?P<name>.+?) <(?P<operand>[^>]+)>$")


def _rows(table: str) -> list[tuple[frozenset[str], str]]:
    """Split a generated table into ``(sources, line)`` pairs."""
    parsed = []
    for row in table.splitlines():
        mask_text, _, line = row.partition("\t")
        mask = int(mask_text, 16)
        labels = frozenset(
            label for index, label in enumerate(_inspector_data.SOURCES) if mask & (1 << index)
        )
        parsed.append((labels, line))
    return parsed


def _split_return_type(line: str) -> tuple[str, str]:
    """Split a ``signature: return type`` line. No signature contains ``": "``."""
    signature, _, return_type = line.rpartition(": ")
    return signature, return_type


def _split_enrichment(line: str, width: int) -> tuple[str, tuple[str, ...] | None]:
    """Split a dump line into its legacy ``signature: type`` text and, when
    present, exactly ``width`` extra tab-separated enrichment columns.

    A dump captured before the introspection meta-layer was queried directly
    (every client dump today) carries no tabs at all, and this returns
    ``None`` for the enrichment half -- callers must treat every enriched
    field as optional, never inferring absence as a negative fact.
    """
    base, _, rest = line.partition("\t")
    if not rest:
        return base, None
    fields = tuple(rest.split("\t"))
    if len(fields) != width:  # pragma: no cover - guarded by test_inspector_data.py
        raise ValueError(f"expected {width} enrichment columns, got {len(fields)}: {line!r}")
    return base, fields


def _parse_property(sources: frozenset[str], line: str) -> Inspector:
    base, enrichment = _split_enrichment(line, width=7)
    signature, return_type = _split_return_type(base)
    match = _PROPERTY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed property signature: {signature!r}")
    index = match.group("index").strip()
    obj = match.group("object")
    singular = plural = usual = None
    multivalued = None
    if enrichment is not None:
        singular, plural, usual, multivalued_text, _result, _obj, _index = enrichment
        multivalued = multivalued_text == "1"
    return Inspector(
        sources=sources,
        kind=InspectorKind.PROPERTY,
        signature=signature,
        name=match.group("name").strip(),
        return_type=return_type,
        index_type=index.strip("<>") if index else None,
        operands=(obj.strip("<>"),) if obj else (),
        singular_name=singular or None,
        plural_name=plural or None,
        usual_name=usual or None,
        multivalued=multivalued,
    )


def _parse_cast(sources: frozenset[str], line: str) -> Inspector:
    base, _enrichment = _split_enrichment(line, width=3)
    signature, return_type = _split_return_type(base)
    match = _CAST_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed cast signature: {signature!r}")
    return Inspector(
        sources=sources,
        kind=InspectorKind.CAST,
        signature=signature,
        name=match.group("name"),
        return_type=return_type,
        operands=(match.group("source"),),
    )


def _parse_binary(sources: frozenset[str], line: str) -> Inspector:
    base, enrichment = _split_enrichment(line, width=5)
    signature, return_type = _split_return_type(base)
    match = _BINARY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed binary operator signature: {signature!r}")
    written_name = symbol = None
    if enrichment is not None:
        written_name, symbol, _left, _right, _result = enrichment
    return Inspector(
        sources=sources,
        kind=InspectorKind.BINARY_OPERATOR,
        signature=signature,
        name=match.group("name"),
        return_type=return_type,
        operands=(match.group("left"), match.group("right")),
        written_name=written_name,
        symbol=symbol,
    )


def _parse_unary(sources: frozenset[str], line: str) -> Inspector:
    base, enrichment = _split_enrichment(line, width=4)
    signature, return_type = _split_return_type(base)
    match = _UNARY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed unary operator signature: {signature!r}")
    written_name = symbol = None
    if enrichment is not None:
        written_name, symbol, _operand, _result = enrichment
    return Inspector(
        sources=sources,
        kind=InspectorKind.UNARY_OPERATOR,
        signature=signature,
        name=match.group("name"),
        return_type=return_type,
        operands=(match.group("operand"),),
        written_name=written_name,
        symbol=symbol,
    )


# ---------------------------------------------------------------------------
# Public tables
# ---------------------------------------------------------------------------


@functools.cache
def properties() -> tuple[Inspector, ...]:
    """Every named property, e.g. ``windows of <operating system>``."""
    return tuple(_parse_property(s, line) for s, line in _rows(_inspector_data.PROPERTIES))


@functools.cache
def casts() -> tuple[Inspector, ...]:
    """Every ``as`` conversion, e.g. ``<string> as trimmed string``."""
    return tuple(_parse_cast(s, line) for s, line in _rows(_inspector_data.CASTS))


@functools.cache
def binary_operators() -> tuple[Inspector, ...]:
    """Every infix operator, e.g. ``<string> starts with <string>``."""
    return tuple(_parse_binary(s, line) for s, line in _rows(_inspector_data.BINARY_OPERATORS))


@functools.cache
def unary_operators() -> tuple[Inspector, ...]:
    """Every prefix operator. In the sampled data, only ``-``."""
    return tuple(_parse_unary(s, line) for s, line in _rows(_inspector_data.UNARY_OPERATORS))


def _parse_type(sources: frozenset[str], line: str) -> RelevanceType:
    name, enrichment = _split_enrichment(line, width=2)
    if enrichment is None:
        return RelevanceType(sources=sources, name=name)
    parent, size_text = enrichment
    return RelevanceType(
        sources=sources,
        name=name,
        parent=parent or None,
        size=int(size_text) if size_text else None,
    )


@functools.cache
def relevance_types() -> tuple[RelevanceType, ...]:
    """Every type name, e.g. ``bes computer``, ``registry key``, ``string``."""
    return tuple(_parse_type(s, line) for s, line in _rows(_inspector_data.TYPES))


@functools.cache
def _by_type_name() -> dict[str, RelevanceType]:
    """Types indexed by name, for the ancestor walk."""
    return {entry.name: entry for entry in relevance_types()}


@functools.cache
def ancestors(name: str) -> tuple[str, ...]:
    """``name`` and every type it inherits from, nearest first.

    Resolving a property against a type **requires** this walk rather than
    merely benefiting from it: a property is declared on the base type, so
    ``size`` lives on ``file`` and resolving ``size of <application>`` against
    ``application`` alone finds nothing. The real chain is
    ``client -> application -> file -> filesystem object``.

    Most types are roots and the walk stops immediately -- that is what the
    engine reports, not missing data. An unknown name comes back as itself, on
    the usual rule that absence from this snapshot proves nothing.
    """
    index = _by_type_name()
    chain = [name]
    seen = {name}
    while (entry := index.get(chain[-1])) is not None:
        parent = entry.parent
        if parent is None or parent in seen:  # cycle-safe, though none is known
            break
        chain.append(parent)
        seen.add(parent)
    return tuple(chain)


@functools.cache
def known_types() -> frozenset[str]:
    """Just the type names, for membership tests."""
    return frozenset(entry.name for entry in relevance_types())


def _dialect_of_context(context: str) -> Dialect | None:
    """Which engine evaluates ``context``, from the way the axis spells it."""
    dialect, _, _rest = context.partition(":")
    return Dialect.SESSION if dialect == "session" else Dialect.CLIENT


@functools.cache
def _unsampled_contexts(kind: InspectorKind) -> frozenset[str]:
    """Contexts whose dumps carry no row of ``kind`` at all.

    A systematic gap rather than an incidental one: the console and Web
    Reports captures are `properties` dumps, so they say nothing whatsoever
    about casts or operators. Silence over a whole category is not evidence,
    and :attr:`Inspector.contexts` refuses to read it as any.
    """
    sampled = {
        source for entry in all_inspectors() if entry.kind is kind for source in entry.sources
    }
    return frozenset(
        context if dialect == "client" else source
        for source in sources()
        for dialect, _, context in [source.partition(":")]
        if context and source not in sampled
    )


@functools.cache
def all_inspectors() -> tuple[Inspector, ...]:
    """Every row of all four inspector categories."""
    return properties() + casts() + binary_operators() + unary_operators()


@functools.cache
def inspector_names() -> frozenset[str]:
    """Every identifying phrase across all four categories.

    This is the set a tokenizer needs in order to decide where a multi-word
    inspector name ends.

    It is **not** the right pool for a "did you mean", which this docstring used
    to claim: it holds each row's :attr:`~Inspector.name` only, so it is some
    2,500 entries short of what :func:`lookup` will actually match. The missing
    ones are mostly plurals -- ``absolute values``, ``access modes`` -- and a
    suggester drawn from here would therefore never propose a plural spelling,
    which is half of how relevance is written. :func:`search` and
    :func:`suggest` index every written form instead, plus the spoken operator
    names that no written form carries.
    """
    return frozenset(entry.name for entry in all_inspectors())


def written_forms(entry: Inspector) -> tuple[str, ...]:
    """Every spelling ``entry`` can be written as, lowercased.

    A property's signature carries one form, but relevance is written with
    either: ``name of <file>`` and ``names of <folder>`` are the same row seen
    singular and plural. Indexing only the signature's form loses whichever one
    it did not happen to record.
    """
    forms = (entry.name, entry.singular_name, entry.plural_name)
    return tuple(dict.fromkeys(form.lower() for form in forms if form))


@functools.cache
def _by_name() -> dict[str, tuple[Inspector, ...]]:
    index: dict[str, list[Inspector]] = {}
    for entry in all_inspectors():
        for form in written_forms(entry):
            index.setdefault(form, []).append(entry)
    return {name: tuple(entries) for name, entries in index.items()}


def lookup(name: str, *, kind: InspectorKind | None = None) -> tuple[Inspector, ...]:
    """Every inspector that can be written as ``name``, case-insensitively.

    A name is usually overloaded -- the same property applies to several object
    types, each with its own return type -- so this returns all of them and
    lets the caller pick by operand type. Empty when nothing matches, which
    means "not in this snapshot", not "invalid".

    Matching covers every form the engine reports a row under, not just the one
    its signature happens to use: ``lookup("names")`` finds the rows whose
    signature reads ``name``. Use :func:`written_form_of` to recover which form
    matched, which is what says whether the expression is singular or plural.
    """
    found = _by_name().get(name.strip().lower(), ())
    if kind is not None:
        found = tuple(entry for entry in found if entry.kind is kind)
    return found


def written_form_of(entry: Inspector, name: str) -> WrittenForm:
    """Which of ``entry``'s spellings ``name`` is.

    The distinction is the plurality of the *expression*, and it is not the same
    question as :attr:`Inspector.multivalued`, which is a fact about the row:
    ``name of <SELinux Boolean>`` is not multivalued and still has the plural
    form ``names``. So plurality is derived here, at the point of use, rather
    than stored.
    """
    wanted = name.strip().lower()
    if entry.plural_name and entry.plural_name.lower() == wanted:
        return WrittenForm.PLURAL
    if entry.singular_name and entry.singular_name.lower() == wanted:
        return WrittenForm.SINGULAR
    return WrittenForm.UNKNOWN


def sources() -> tuple[str, ...]:
    """The dump labels rows are attributed to, e.g. ``client:windows``."""
    return _inspector_data.SOURCES


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
# `lookup` resolves a name you already have. This resolves a name you do not:
# a half-remembered phrase, a typo, or a description of a relationship
# ("registry keys"). The two are siblings rather than layers -- search hands
# back an identifier, `lookup` hands back the rows -- and both draw on the same
# `_by_name` index, which is why they live in one module.


class MatchKind(enum.Enum):
    """How a result matched. **Declaration order is the ranking**, strongest first.

    The tier is the useful answer, which is why there is no numeric score:
    :attr:`EXACT` means do not say "did you mean", :attr:`FUZZY` means say it
    out loud, and :attr:`SIGNATURE` means "no name reads like that, but this
    expression does". A float cannot express any of those, and exposing
    :mod:`difflib`'s ratio would make its internals part of this package's
    public API -- a caller writing ``if score > 0.8`` would pin a stdlib
    implementation detail and freeze the cutoff forever.
    """

    EXACT = "exact"
    """The query is a written form, verbatim after normalization."""

    PREFIX = "prefix"
    """A written form starts with the query. What a completion wants."""

    WORDS = "words"
    """Every word of the query is a word of some written form, in any order."""

    SIGNATURE = "signature"
    """Every word of the query appears in a *signature*, and in no name.

    The tier that answers a relationship question. ``registry keys`` is not the
    name of anything; ``keys of <registry key>`` is the only right answer, and
    only the signature contains both words.
    """

    SUBSTRING = "substring"
    """The query appears inside a written form, but not at its start."""

    FUZZY = "fuzzy"
    """Nothing above matched and :mod:`difflib` judged a form close. A typo, probably."""


_MATCH_RANK: Final[dict[MatchKind, int]] = {kind: rank for rank, kind in enumerate(MatchKind)}
"""Tier order, derived from the declaration order rather than restated.

A second hand-maintained table would be one more thing to drift, and the
enum's own order is already the documented ranking.
"""

SIGNATURE_SAMPLE: Final = 5
"""How many signatures :meth:`SearchResult.to_dict` includes.

A payload cap, not a data limit -- :attr:`SearchResult.inspectors` always holds
every row. It exists because the full rows are enormous: ``lookup("name")`` is
96 overloads and about 43,000 bytes of JSON for one name, so a 25-result search
that embedded them would cost a six-figure token count to answer "did you mean".
``signatures_omitted`` reports whatever this dropped, so the count is never
silently lost. Same shape as the ``returns[:3]`` cap in
:mod:`bigfix_relevance_analyzer.reference._tables`.
"""


@dataclass(frozen=True, slots=True)
class SearchResult:
    """One thing a query found, and how it was found."""

    name: str
    """The form to write in relevance, and one :func:`lookup` can always resolve.

    Not necessarily the text that matched -- see :attr:`matched`. For a spoken
    operator form this is the symbol (``%`` for a ``mod`` query), because that
    is what :func:`lookup` answers to.
    """

    match: MatchKind
    matched: str
    """The text that actually hit: a written form, a signature, or a spoken name.

    Kept separate from :attr:`name` because a "did you mean" has to quote what
    it recognised. A ``names`` query matching rows whose signature says ``name``
    should say ``names``, not silently correct itself.
    """

    inspectors: tuple[Inspector, ...]
    """Every row behind :attr:`name`, after this search's filters. Never empty."""

    @property
    def signatures(self) -> tuple[str, ...]:
        """Every distinct signature behind this result, sorted."""
        return tuple(sorted({entry.signature for entry in self.inspectors}))

    @property
    def return_types(self) -> tuple[str, ...]:
        """Every distinct type this can evaluate to, sorted."""
        return tuple(sorted({entry.return_type for entry in self.inspectors}))

    @property
    def kinds(self) -> frozenset[InspectorKind]:
        """Which introspection categories the rows behind this come from."""
        return frozenset(entry.kind for entry in self.inspectors)

    @property
    def dialects(self) -> frozenset[Dialect]:
        """Every dialect that defines any row behind this result."""
        return frozenset(dialect for entry in self.inspectors for dialect in entry.dialects)

    @property
    def contexts(self) -> frozenset[str]:
        """Every evaluation context that defines any row behind this result."""
        return frozenset(context for entry in self.inspectors for context in entry.contexts)

    def to_dict(self) -> dict[str, Any]:
        """This result as JSON-serializable plain data, sized for a wire.

        Identifiers and a sample, never the rows themselves -- see
        :data:`SIGNATURE_SAMPLE` for why, and use :func:`lookup` on
        :attr:`name` to get the full rows for the one result a consumer settled
        on. ``overloads`` is always the true count even when ``signatures`` is
        capped, so a reader can tell a one-row answer from a ninety-six-row one.
        """
        signatures = self.signatures
        return {
            "name": self.name,
            "match": self.match.value,
            "matched": self.matched,
            "kinds": _enums(self.kinds),
            "dialects": _enums(self.dialects),
            "return_types": list(self.return_types),
            "overloads": len(self.inspectors),
            "signatures": list(signatures[:SIGNATURE_SAMPLE]),
            "signatures_omitted": max(0, len(signatures) - SIGNATURE_SAMPLE),
        }


def _words(text: str) -> frozenset[str]:
    """The distinct words of ``text``, with signature punctuation split off.

    ``<`` and ``>`` become separators so ``keys of <registry key>`` yields
    ``{keys, of, registry, key}`` -- otherwise a query word would have to match
    ``<registry`` with the bracket attached.
    """
    return frozenset(text.lower().replace("<", " ").replace(">", " ").split())


@dataclass(frozen=True, slots=True)
class _SearchIndex:
    """Everything a query needs, built once.

    One unfiltered index rather than one per ``(dialect, kind)``: the build is a
    few milliseconds and a filtered pass over the rows is a fraction of one, so
    per-filter variants would trade eight builds for nothing -- and a
    :func:`functools.cache` keyed on filters is a leak waiting for a caller that
    passes many.
    """

    forms: tuple[str, ...]
    """Every searchable form, sorted. The candidate pool :mod:`difflib` scans."""

    by_form: Mapping[str, tuple[Inspector, ...]]
    """Rows per form. A superset of :func:`_by_name`'s keys -- see the note below."""

    form_words: Mapping[str, frozenset[str]]
    signature_words: tuple[tuple[str, frozenset[str], Inspector], ...]


@functools.cache
def _search_index() -> _SearchIndex:
    """Build the search index. Cached, and never built at import.

    The pool is deliberately **wider than** :func:`lookup`'s. It adds each row's
    :attr:`~Inspector.written_name` and :attr:`~Inspector.symbol` -- the engine's
    own spoken words for an operator -- which :func:`written_forms` does not
    carry. Without them ``search("mod")`` finds nothing, though ``mod`` is
    exactly how modulo is written in relevance source, and a reader who saw the
    engine's own ``the operator 'plus' is not defined`` has no way in either.

    :func:`lookup` is left alone on purpose:
    :data:`~bigfix_relevance_analyzer.grammar.CANONICAL_BINARY` already maps
    ``mod`` to ``%`` before the tokenizer and type-checker consult it, so the
    gap is a discovery problem rather than a resolution one, and widening a
    function the parser depends on to fix a search issue would be the wrong
    trade.
    """
    by_form: dict[str, list[Inspector]] = {}
    for entry in all_inspectors():
        forms = [*written_forms(entry)]
        forms.extend(extra.lower() for extra in (entry.written_name, entry.symbol) if extra)
        for form in dict.fromkeys(forms):
            by_form.setdefault(form, []).append(entry)

    frozen = {form: tuple(entries) for form, entries in by_form.items()}
    return _SearchIndex(
        forms=tuple(sorted(frozen)),
        by_form=frozen,
        form_words={form: _words(form) for form in frozen},
        signature_words=tuple(
            (entry.signature, _words(entry.signature), entry) for entry in all_inspectors()
        ),
    )


def _normalize_query(query: str) -> str:
    """Lowercase ``query`` and collapse every whitespace run to one space.

    Stronger than :func:`lookup`'s ``.strip().lower()``, deliberately: a search
    query is typed or pasted, so ``"Registry  Keys"`` and ``"registry keys"``
    have to be the same question. :func:`lookup` stays literal because it
    answers about an exact name.
    """
    return " ".join(query.split()).lower()


def _canonical_name(form: str, entries: tuple[Inspector, ...]) -> str:
    """The form to report as :attr:`SearchResult.name` for a match on ``form``.

    ``form`` itself when :func:`lookup` can resolve it, which is the usual case.
    Otherwise the rows' own name -- that is how a spoken-form match on ``mod``
    reports ``%``, keeping the invariant that every result's ``name`` resolves.
    """
    return form if form in _by_name() else entries[0].name


def search(
    query: str,
    *,
    dialect: Dialect | None = None,
    kind: InspectorKind | None = None,
    fuzzy: bool = True,
    limit: int = 25,
) -> tuple[SearchResult, ...]:
    """Find inspectors from a partial, misspelled, or descriptive ``query``.

    The counterpart to :func:`lookup`: this answers "what is this called", and
    :func:`lookup` then answers "how do I use it". One result per matched text,
    best first, with :attr:`SearchResult.match` saying how each was found.

    ``dialect`` narrows to one side of the language. ``kind`` narrows to one
    introspection category. **There is deliberately no** ``platform`` **filter**,
    despite :class:`~bigfix_relevance_analyzer.lint.LintConfig` having one: this
    module's rule is that absence from the snapshot is never evidence, and
    filtering on platform would *remove* candidates on the strength of a gap in
    the dumps -- in a "did you mean", the way to fail is to hide the right
    answer. ``dialect`` is different in kind, because the dumps cover both sides
    and so proposing ``bes computers`` for client relevance is positively wrong
    rather than merely unobserved. Filter on
    :attr:`~Inspector.platforms` yourself if you want it.

    ``fuzzy=False`` skips the :mod:`difflib` pass. That is a cost and a
    semantics switch, not a tuning knob: the precise tiers are well under a
    millisecond and the fuzzy pass can reach tens, and a caller doing
    completion rather than correction does not want invented near-misses. With
    it off, every result is a form that genuinely exists.

    Returns ``()`` for a blank query or a non-positive ``limit`` -- never the
    whole table -- and ``()`` when nothing matched, which is the honest answer
    and the one a suggester needs. Never raises.
    """
    normalized = _normalize_query(query)
    if not normalized or limit <= 0:
        return ()

    index = _search_index()

    # Filter before ranking, always. A row that cannot be returned must not
    # occupy a slot -- otherwise a narrow search comes back empty while answers
    # existed -- and the pool is rebuilt from what survives, so a form whose
    # every row was filtered out disappears rather than lingering as an empty
    # result. `Inspector.dialects` recomputes on each access, so the membership
    # test is resolved here, once per row, rather than inside a sort callback.
    def keep(entry: Inspector) -> bool:
        if kind is not None and entry.kind is not kind:
            return False
        return not (dialect is not None and dialect not in entry.dialects)

    filtered = kind is not None or dialect is not None
    by_form: Mapping[str, tuple[Inspector, ...]]
    if filtered:
        by_form = {
            form: kept
            for form, entries in index.by_form.items()
            if (kept := tuple(entry for entry in entries if keep(entry)))
        }
        signature_words = tuple(row for row in index.signature_words if keep(row[2]))
    else:
        by_form = index.by_form
        signature_words = index.signature_words
    forms = tuple(sorted(by_form)) if filtered else index.forms

    query_words = _words(normalized)
    found: dict[str, tuple[MatchKind, str, tuple[Inspector, ...]]] = {}

    def offer(matched: str, kind_: MatchKind, name: str, entries: tuple[Inspector, ...]) -> None:
        """Record a match, keeping the strongest tier for any given matched text."""
        current = found.get(matched)
        if current is None or _MATCH_RANK[kind_] < _MATCH_RANK[current[0]]:
            found[matched] = (kind_, name, entries)

    # Name tiers, keyed on the form: this is what collapses `name`'s 96 rows
    # into a single answer.
    for form in forms:
        entries = by_form[form]
        name = _canonical_name(form, entries)
        if form == normalized:
            offer(form, MatchKind.EXACT, name, entries)
        elif form.startswith(normalized):
            offer(form, MatchKind.PREFIX, name, entries)
        elif query_words <= index.form_words[form]:
            offer(form, MatchKind.WORDS, name, entries)
        elif normalized in form:
            offer(form, MatchKind.SUBSTRING, name, entries)

    # Signature tier, keyed on the *signature*, because there the signature is
    # the answer: `files of <folder>` and `fifo files of <folder>` are two
    # genuinely different things, and collapsing both to `files` would discard
    # what the query was asking about.
    if not any(state[0] is MatchKind.EXACT for state in found.values()):
        for signature, words, entry in signature_words:
            if query_words <= words:
                form = written_forms(entry)[0]
                offer(
                    signature,
                    MatchKind.SIGNATURE,
                    _canonical_name(form, (entry,)),
                    by_form.get(form, (entry,)),
                )

    if fuzzy and len(found) < limit:
        for close in difflib.get_close_matches(normalized, forms, n=limit, cutoff=0.6):
            entries = by_form[close]
            offer(close, MatchKind.FUZZY, _canonical_name(close, entries), entries)

    def sort_key(
        item: tuple[str, tuple[MatchKind, str, tuple[Inspector, ...]]],
    ) -> tuple[int, int, float, int, str]:
        matched, (kind_, _name, _entries) = item
        # The first-character preference applies to the fuzzy tier only, which
        # is where it was measured: raw ratio ranks `lines` above `files` for
        # `flies`, and this fixes it. In the exact and prefix tiers it is always
        # zero, and in the substring tier the first character by definition does
        # not match, so applying it there would be noise dressed as a heuristic.
        penalty = 0 if kind_ is not MatchKind.FUZZY else int(not matched.startswith(normalized[:1]))
        # Likewise the ratio: meaningful only where the tier itself does not
        # already order things, and inert (1.0) above.
        ratio = (
            difflib.SequenceMatcher(None, normalized, matched).ratio()
            if kind_ in (MatchKind.SUBSTRING, MatchKind.FUZZY)
            else 1.0
        )
        return (_MATCH_RANK[kind_], penalty, -ratio, len(matched), matched)

    ordered = sorted(found.items(), key=sort_key)
    return tuple(
        SearchResult(name=name, match=kind_, matched=matched, inspectors=entries)
        for matched, (kind_, name, entries) in ordered[:limit]
    )


def suggest(name: str, *, dialect: Dialect | None = None, limit: int = 3) -> tuple[str, ...]:
    """Names ``name`` was plausibly meant to be, best first. ``()`` when none are.

    The join a consumer of the ``unknown-inspector`` rule would otherwise write,
    and it is here because it carries decisions they should not each make
    differently: how many leads help before they become noise, and that ``name``
    itself is never among them -- echoing back the name just reported as unknown
    reads as a contradiction, and it can happen, because a name can be a real
    written form that this *dialect* does not define.

    Names rather than :class:`SearchResult`s: a message wants a few strings, and
    a caller that wants the rows has :func:`search` and :func:`lookup`.
    """
    return tuple(
        result.name
        for result in search(name, dialect=dialect, limit=limit + 1)
        if result.name != _normalize_query(name)
    )[:limit]
