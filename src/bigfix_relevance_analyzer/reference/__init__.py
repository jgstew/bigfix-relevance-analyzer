"""Servable language references: what relevance is, and how to write it.

Three documents, as GitHub-flavored Markdown:

* ``dialects`` -- client relevance versus session relevance. Serve this first;
  the distinction is the thing most often got wrong, and it is a prerequisite
  for the other two making sense.
* ``client-relevance`` and ``session-relevance`` -- one per dialect: where it is
  evaluated, where you write it, the syntax fundamentals, the operator and
  precedence tables, a starter vocabulary, the type sketch, what is expensive,
  and what the engine says when something is wrong.

Each is a hybrid. The prose is authored (``docs/reference/*.md``, embedded by
``tools/generate_reference_prose.py``); the tables are generated at call time
from the same data the analyzer itself uses, so they cannot drift from the
inspector snapshot -- see :mod:`bigfix_relevance_analyzer.reference._tables`.

Why this exists here rather than in each consumer
-------------------------------------------------
A server whose job is to help write relevance has to tell a model what
relevance *is*. Written per-consumer, that description is re-invented every
time, and each copy is wrong in a different way -- the client/session
distinction blurred, the escaping rule guessed, a name recalled that no engine
defines. Written once here, next to the tables that can check most of it, every
consumer says the same true thing.

Sizing
------
These are read by something with a context window, so they are deliberately
short: :attr:`Detail.STANDARD` targets a few thousand tokens, and a test pins a
character ceiling per document so a generated section cannot quietly grow into a
manual. The full inspector table is not a reference and is not served here --
:func:`~bigfix_relevance_analyzer.inspectors.lookup` and
:meth:`~bigfix_relevance_analyzer.inspectors.Inspector.to_dict` are how a
consumer answers a question about one name.

Import cost
-----------
Nothing here builds a document at import. ``_prose`` and ``_tables`` are
imported inside function bodies, and every renderer is cached, so importing this
module -- or the package, which does not import this module at all -- costs
nothing but this docstring. That is the same reasoning that keeps the package
safe and cheap to import inside a stdio MCP server.

    from bigfix_relevance_analyzer import reference

    for document in reference.documents():
        register(document.slug, document.title, document.summary, document.read)
"""

from __future__ import annotations

import enum
import functools
from dataclasses import dataclass, field
from typing import Any

from bigfix_relevance_analyzer.dialect import Dialect, is_definite

__all__ = [
    "MIME_TYPE",
    "Detail",
    "ReferenceDocument",
    "client_relevance_reference",
    "documents",
    "get_document",
    "markdown",
    "session_relevance_reference",
]

MIME_TYPE = "text/markdown"
"""What every document here is. A constant, not a field: it does not vary."""


class Detail(enum.Enum):
    """How much of a document to render.

    There is deliberately no ``FULL``. The next step up from ``STANDARD`` would
    be dumping the inspector table, which is a search index rather than a
    reference and would swamp any context it was loaded into.
    """

    BRIEF = "brief"
    """Authored prose only, no generated tables. Sized for a system prompt."""

    STANDARD = "standard"
    """Prose plus the generated tables. Sized for a resource read."""


@dataclass(frozen=True, slots=True)
class ReferenceDocument:
    """One servable document, with the metadata a resource listing needs.

    ``title`` and ``summary`` are here rather than left to the caller because an
    MCP ``list_resources`` needs a name and a description for every resource,
    and a bare ``-> str`` API would make each server invent its own -- which is
    the duplication this module exists to remove.

    No ``uri`` field: the URI scheme belongs to the server's namespace, and
    :attr:`slug` is enough to build one from.
    """

    slug: str
    """Stable identifier, e.g. ``"client-relevance"``. Safe in a URI path."""

    title: str
    """One short line, for a resource listing's name."""

    summary: str
    """One sentence on what this document covers, for a listing's description."""

    dialect: Dialect | None
    """Which dialect this documents, or ``None`` for the shared explainer."""

    _render: Any = field(repr=False, compare=False)
    """The builder. Excluded from ``repr``/``==`` so a document compares by identity."""

    def read(self, *, detail: Detail = Detail.STANDARD) -> str:
        """This document as Markdown."""
        render: Any = self._render
        return str(render(detail))

    def to_dict(self, *, detail: Detail = Detail.STANDARD) -> dict[str, Any]:
        """This document, and its text, as JSON-serializable plain data."""
        return {
            "slug": self.slug,
            "title": self.title,
            "summary": self.summary,
            "dialect": None if self.dialect is None else self.dialect.value,
            "mime_type": MIME_TYPE,
            "detail": detail.value,
            "text": self.read(detail=detail),
        }


def _section(heading: str, body: str) -> str:
    """One ``## heading`` and its body, or nothing at all when the body is empty.

    A heading with no table under it reads as a bug in the document rather than
    as an absence of data, so an empty section is omitted entirely.
    """
    return f"\n## {heading}\n\n{body}\n" if body.strip() else ""


@functools.cache
def _dialects(detail: Detail) -> str:
    """The shared client-versus-session explainer. No generated tables to add."""
    from bigfix_relevance_analyzer.reference import _prose

    del detail  # BRIEF and STANDARD are the same here: this document is all prose.
    return _prose.DIALECTS


@functools.cache
def _dialect_document(dialect: Dialect, detail: Detail) -> str:
    """One dialect's document: its prose, the shared syntax, then the tables."""
    from bigfix_relevance_analyzer.reference import _prose, _tables

    prose = {
        Dialect.CLIENT: _prose.CLIENT_RELEVANCE,
        Dialect.SESSION: _prose.SESSION_RELEVANCE,
    }[dialect]

    parts = [prose.rstrip(), "", _prose.SYNTAX.rstrip()]
    if detail is Detail.STANDARD:
        parts.extend(
            [
                "",
                f"# Generated tables ({dialect.value} relevance)",
                "",
                _tables.coverage_note(dialect),
                _section("Operators and precedence", _tables.operator_table()),
                _section("Starter vocabulary", _tables.starter_vocabulary(dialect)),
                _section("Common casts", _tables.cast_examples(dialect)),
                _section("Types you will meet", _tables.type_sketch(dialect)),
                _section("Expensive constructs", _tables.expensive_constructs(dialect)),
                _section("What the type checker says", _tables.engine_diagnostics()),
            ]
        )
    return "\n".join(part for part in parts if part is not None).rstrip() + "\n"


def _client(detail: Detail) -> str:
    return _dialect_document(Dialect.CLIENT, detail)


def _session(detail: Detail) -> str:
    return _dialect_document(Dialect.SESSION, detail)


@functools.cache
def documents() -> tuple[ReferenceDocument, ...]:
    """Every servable document, in the order a consumer should offer them.

    The shared explainer first: it is the prerequisite for the other two, and a
    consumer registering them in listing order gets that for free.

    Enumerable on purpose. A server can loop over this and register everything
    without naming a document in its own source, which is what makes adding a
    fourth reference later a non-event for consumers rather than a change each
    of them has to make.
    """
    return (
        ReferenceDocument(
            slug="dialects",
            title="BigFix relevance: client versus session",
            summary=(
                "The two relevance dialects, where each is evaluated, and which files "
                "and elements carry which -- including the ClientUI exception."
            ),
            dialect=None,
            _render=_dialects,
        ),
        ReferenceDocument(
            slug="client-relevance",
            title="BigFix client relevance: language reference",
            summary=(
                "Writing relevance evaluated on the endpoint: where it goes, the syntax, "
                "the operator table, a starter vocabulary, and what is expensive."
            ),
            dialect=Dialect.CLIENT,
            _render=_client,
        ),
        ReferenceDocument(
            slug="session-relevance",
            title="BigFix session relevance: language reference",
            summary=(
                "Writing relevance evaluated on the server against the BigFix database: "
                "where it goes, the syntax, the `bes` namespace, and what is expensive."
            ),
            dialect=Dialect.SESSION,
            _render=_session,
        ),
    )


def get_document(slug: str) -> ReferenceDocument:
    """One document by :attr:`~ReferenceDocument.slug`.

    Raises :class:`KeyError` for an unknown slug, naming the ones that exist --
    a consumer hitting this has a typo or a stale hardcoded name, and the valid
    set is short enough to be the most useful thing to say.
    """
    for document in documents():
        if document.slug == slug:
            return document
    known = ", ".join(sorted(entry.slug for entry in documents()))
    raise KeyError(f"no reference document {slug!r}; available: {known}")


def markdown(which: str | Dialect, *, detail: Detail = Detail.STANDARD) -> str:
    """One document as Markdown, by slug or by dialect.

    ``Dialect.BOTH`` and ``Dialect.UNCERTAIN`` raise :class:`ValueError`: those
    are conclusions the analyzer reaches about a *statement*, not documents that
    exist. Silently falling back to the shared explainer would answer a question
    the caller did not ask.
    """
    if isinstance(which, Dialect):
        if not is_definite(which):
            raise ValueError(
                f"no reference document for {which.value!r}; "
                f"pass {Dialect.CLIENT.value!r} or {Dialect.SESSION.value!r}, "
                'or the slug "dialects" for the explainer'
            )
        which = f"{which.value}-relevance"
    return get_document(which).read(detail=detail)


def client_relevance_reference(*, detail: Detail = Detail.STANDARD) -> str:
    """The client relevance reference as Markdown. Front door for the common case."""
    return markdown(Dialect.CLIENT, detail=detail)


def session_relevance_reference(*, detail: Detail = Detail.STANDARD) -> str:
    """The session relevance reference as Markdown. Front door for the common case."""
    return markdown(Dialect.SESSION, detail=detail)
