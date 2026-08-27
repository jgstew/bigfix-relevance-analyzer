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

That cost is small but not free, and most callers only want to extract
relevance, so this module is deliberately **not** re-exported from the package
root. Reach for it explicitly::

    from bigfix_relevance_analyzer import inspectors

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

import enum
import functools
import re
from dataclasses import dataclass

from bigfix_relevance_analyzer import _inspector_data
from bigfix_relevance_analyzer.dialect import Dialect

__all__ = [
    "Inspector",
    "InspectorKind",
    "RelevanceType",
    "binary_operators",
    "casts",
    "inspector_names",
    "known_types",
    "lookup",
    "properties",
    "sources",
    "unary_operators",
]


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


@dataclass(frozen=True, slots=True)
class RelevanceType(_Sourced):
    """One type name in the relevance type universe."""

    name: str
    """The type name, e.g. ``bes computer``, ``registry key``, ``string``."""


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


def _parse_property(sources: frozenset[str], line: str) -> Inspector:
    signature, return_type = _split_return_type(line)
    match = _PROPERTY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed property signature: {signature!r}")
    index = match.group("index").strip()
    obj = match.group("object")
    return Inspector(
        sources=sources,
        kind=InspectorKind.PROPERTY,
        signature=signature,
        name=match.group("name").strip(),
        return_type=return_type,
        index_type=index.strip("<>") if index else None,
        operands=(obj.strip("<>"),) if obj else (),
    )


def _parse_cast(sources: frozenset[str], line: str) -> Inspector:
    signature, return_type = _split_return_type(line)
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
    signature, return_type = _split_return_type(line)
    match = _BINARY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed binary operator signature: {signature!r}")
    return Inspector(
        sources=sources,
        kind=InspectorKind.BINARY_OPERATOR,
        signature=signature,
        name=match.group("name"),
        return_type=return_type,
        operands=(match.group("left"), match.group("right")),
    )


def _parse_unary(sources: frozenset[str], line: str) -> Inspector:
    signature, return_type = _split_return_type(line)
    match = _UNARY_RE.match(signature)
    if match is None:  # pragma: no cover - every sampled signature parses
        raise ValueError(f"unparsed unary operator signature: {signature!r}")
    return Inspector(
        sources=sources,
        kind=InspectorKind.UNARY_OPERATOR,
        signature=signature,
        name=match.group("name"),
        return_type=return_type,
        operands=(match.group("operand"),),
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


@functools.cache
def relevance_types() -> tuple[RelevanceType, ...]:
    """Every type name, e.g. ``bes computer``, ``registry key``, ``string``."""
    return tuple(RelevanceType(sources=s, name=line) for s, line in _rows(_inspector_data.TYPES))


@functools.cache
def known_types() -> frozenset[str]:
    """Just the type names, for membership tests."""
    return frozenset(entry.name for entry in relevance_types())


@functools.cache
def all_inspectors() -> tuple[Inspector, ...]:
    """Every row of all four inspector categories."""
    return properties() + casts() + binary_operators() + unary_operators()


@functools.cache
def inspector_names() -> frozenset[str]:
    """Every identifying phrase across all four categories.

    This is the set a tokenizer needs in order to decide where a multi-word
    inspector name ends, and the candidate pool a "did you mean" suggester
    should be drawn from.
    """
    return frozenset(entry.name for entry in all_inspectors())


@functools.cache
def _by_name() -> dict[str, tuple[Inspector, ...]]:
    index: dict[str, list[Inspector]] = {}
    for entry in all_inspectors():
        index.setdefault(entry.name.lower(), []).append(entry)
    return {name: tuple(entries) for name, entries in index.items()}


def lookup(name: str, *, kind: InspectorKind | None = None) -> tuple[Inspector, ...]:
    """Every inspector whose :attr:`~Inspector.name` is ``name``, case-insensitively.

    A name is usually overloaded -- the same property applies to several object
    types, each with its own return type -- so this returns all of them and
    lets the caller pick by operand type. Empty when nothing matches, which
    means "not in this snapshot", not "invalid".
    """
    found = _by_name().get(name.strip().lower(), ())
    if kind is not None:
        found = tuple(entry for entry in found if entry.kind is kind)
    return found


def sources() -> tuple[str, ...]:
    """The dump labels rows are attributed to, e.g. ``client:windows``."""
    return _inspector_data.SOURCES
