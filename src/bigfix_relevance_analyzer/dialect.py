"""Which relevance dialect a statement is written in, and how to guess it.

BigFix has two relevance dialects that share overlapping syntax but are not the
same language: **client relevance**, evaluated by the BES Client on an endpoint,
and **session relevance**, evaluated by the root server against server-side
data. They have different inspectors available, so a statement that is valid in
one is usually meaningless in the other.

:func:`classify_relevance_dialect` decides a statement's dialect from the
inspectors used *inside* it. That is a separate question from the dialect
:mod:`bigfix_relevance_analyzer.extract` derives from **context** -- which
element of which kind of file a statement was found in. Context is the stronger
evidence when it is available, because it is a fact about which engine will
evaluate the statement rather than an inference; content analysis fills in the
gaps context leaves, and disagreement between the two is worth surfacing.

How the classifier works
------------------------
Markers are matched against the statement with string literals and ``/* */``
comments removed: only text that actually evaluates can say what dialect a
statement is in, so an inspector name merely mentioned in a quoted string or a
comment must not type it. A marker only ever appears in one of two curated
sets, and the sets are
validated against the inspector dumps in
``tests/examples/relevance_inspectors/`` by ``tests/test_dialect_markers.py``.

The two directions are not equally strong evidence:

* **Session markers are strong.** The ``bes `` prefix is the product's own
  namespace for server-side inspectors and covers ~92% of session-only
  signatures. It needs an exception set, though: ``bes license`` and
  ``bes product`` are defined on clients too.
* **Client markers are weaker.** These markers are drawn from session
  **properties**, which has been sampled from the console and Web Reports --
  identical inspector surfaces -- but not from the WebUI, the Fixlet Debugger or
  the REST API, so an inspector that looks client-only against the data we have
  might turn out to exist in an unsampled session context. (The REST API has
  been sampled for the *other* introspection categories -- casts, operators,
  types -- which is separate evidence with its own dumps; see
  ``tests/examples/relevance_inspectors/README.md``. It does not narrow this
  gap, since none of those categories contribute markers here.) The client
  list is therefore short and made of distinctive multi-word phrases rather
  than everything client-only.

Only *positive* evidence is ever used: an inspector nobody recognizes
contributes nothing, and the answer for a statement made entirely of unknown
inspectors is ``None``. That matters because the dumps are a snapshot -- new
BigFix versions add inspectors to both dialects -- so an unrecognized name is
never grounds for calling a statement invalid, or for typing it by elimination.
Flagging unknown inspectors is a useful thing to want, but it is a different job
from typing a dialect and does not belong in this module.

Three traps, all names that *read* as server-side but are valid on a client
------------------------------------------------------------------------------
See ``tests/examples/relevance_inspectors/README.md`` for the per-platform data.

**ClientUI dashboards.** HTML rendered by the BES Client on the endpoint
contains *client* relevance that freely uses ``sites``, ``relevant fixlets of
sites``, ``relevant offer actions of sites``, ``ids of it`` and
``headers "Subject" of it``. So bare ``sites`` / ``fixlets`` / ``offer
actions`` are not session markers. See
``tests/examples/client_relevance/clientui/`` for content exercising this.

**The introspection meta-layer.** ``properties``, ``types``, ``casts``,
``binary operators``, ``unary operators``, ``type <string>`` and
``name of <type>`` exist *identically* on every client platform sampled and in
session relevance -- the client ships the same reflection inspectors as the
server. None of them may be a marker for either side. ``types`` in particular
looks server-only and is not.

**macOS-only statistics-shaped inspectors.** The BES Client on macOS -- and
only macOS, of the five platforms sampled (Windows, macOS, Ubuntu, Debian,
RHEL-family) -- defines ``rate``, ``linear projection`` and
``exponential projection``. Those read like the Web Reports statistics layer
(``statistical bin``, ``linear fit of <statistical bin>``) and would be a
false-positive session marker if typed from a non-macOS client sample alone.

Deciding which evaluation contexts a statement can actually run in is a further
question this module does not answer:
:class:`~bigfix_relevance_analyzer.typecheck.TypeEnvironment` does, over one
axis carrying both dialects -- client platforms by name, session surfaces as
``session:<context>``. Client relevance is often written to run on many
platforms, and inspectors that are not shared have to be guarded so an endpoint
never evaluates relevance not meant for it; the same axis is what lets a
statement every dialect defines say so.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeGuard

from bigfix_relevance_analyzer.tokenizer import _normalize_phrase

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis

__all__ = ["Dialect", "DialectFit", "classify_relevance_dialect", "dialect_fit", "is_definite"]


class Dialect(enum.Enum):
    """Which relevance dialect a statement is written in."""

    CLIENT = "client"
    """Client relevance, evaluated by the BES Client on an endpoint."""

    SESSION = "session"
    """Session relevance, evaluated by the root server, console or WebUI."""

    UNCERTAIN = "uncertain"
    """Could not be determined. A conclusion, unlike a classifier's ``None``."""

    BOTH = "both"
    """Valid as either dialect: every inspector used is available to both.

    Only a parse can prove it, so the text classifier never returns it;
    :attr:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis.resolved_dialect`
    does, once every known reference is in both dialects in the form written.
    """


def is_definite(dialect: Dialect | None) -> TypeGuard[Dialect]:
    """Whether ``dialect`` names one specific dialect.

    ``None``, :attr:`Dialect.UNCERTAIN` and :attr:`Dialect.BOTH` are all "not
    one specific dialect", for different reasons.
    """
    return dialect is Dialect.CLIENT or dialect is Dialect.SESSION


# ---------------------------------------------------------------------------
# Marker tables
# ---------------------------------------------------------------------------

# Session-only phrases, each verified present in the Web Reports dump and absent
# from all five client platform dumps. The `bes *` namespace is handled by
# _BES_PHRASE_RE below rather than listed here.
_SESSION_MARKERS: frozenset[str] = frozenset(
    {
        "current console user",
        "current bes server",
        "current fixlet",
        # Web Reports statistics layer.
        "statistical bin",
        "statistical bins",
        "statistic range",
        "statistic ranges",
        "historical computer count",
        "historical computer counts",
        "fixlet count pair",
        "fixlet count pairs",
        # Context probes.
        "in console context",
        "in web reports context",
        "webui enabled",
        "pending license update",
        "datastore inspector",
        "datastore inspectors",
        "shared variable",
        "shared variables",
        "private variable",
        "private variables",
        "mime field",
        "mime fields",
    }
)

# `bes <word>` phrases that exist in client relevance too, so they are not
# session evidence. Both are license inspectors shipped to the endpoint.
_BES_PREFIX_CLIENT_PHRASES: frozenset[str] = frozenset(
    {"bes license", "bes licenses", "bes product", "bes products"}
)

# Client-only phrases, each verified present in at least one client dump and
# absent from the Web Reports dump.
#
# Deliberately excluded, and why:
#   - single common English words (`service`, `processor`, `file`): technically
#     client-only as inspectors, but far too collision-prone in prose-like
#     relevance to be evidence.
#   - `pending restart`, `operating system`, `active directory`: all present in
#     the session dump (`bes action status pending restart`,
#     `operating system of <bes computer>`, `active directory of <...>`).
#   - everything in the three traps documented in the module docstring.
_CLIENT_MARKERS: frozenset[str] = frozenset(
    {
        "windows of operating system",
        "iokit registry",
        "iokit registries",
        "native registry",
        "logged on user",
        "logged on users",
        "client folder",
        "client folders",
        "action lock state",
        "running application",
        "running applications",
        "regapp",
        "regapps",
        "filesystem",
        "filesystems",
    }
)


def _marker_pattern(markers: frozenset[str]) -> re.Pattern[str]:
    """Compile ``markers`` into one word-boundary-anchored alternation.

    Longest first, so an alternation never settles for a shorter marker that
    prefixes a longer one.
    """
    alternatives = "|".join(re.escape(m) for m in sorted(markers, key=lambda m: (-len(m), m)))
    return re.compile(rf"\b(?:{alternatives})\b")


_SESSION_MARKER_RE = _marker_pattern(_SESSION_MARKERS)
_CLIENT_MARKER_RE = _marker_pattern(_CLIENT_MARKERS)
_BES_PHRASE_RE = re.compile(r"\bbes\s+([a-z_]+)\b")
# A string literal or a `/* */` comment, whichever opens first. One alternation
# rather than two passes, because each construct hides the other's delimiters: a
# `/*` inside a literal is just text, and a `"` inside a comment opens nothing.
# `//` is not treated as a comment -- nothing in the corpus uses it that way and
# `/` is division, so assuming it would risk discarding real relevance.
_NOT_CODE_RE = re.compile(r'"[^"]*"|/\*.*?\*/', re.DOTALL)


def _strip_non_code(text: str) -> str:
    """Remove string literals and comments from ``text``, leaving a space behind.

    A relevance string literal cannot contain a raw double quote -- one is
    written as an escape *inside* the string rather than backslashed -- so
    pairing quotes off left to right is exact. Each literal or comment becomes a
    single space, so it still separates the tokens around it.

    Anything left unterminated -- an odd quote, or a `/*` with no `*/` -- takes
    the rest of the text with it, since none of it is code that will evaluate.
    """
    stripped = _NOT_CODE_RE.sub(" ", text)
    ends = [at for at in (stripped.find('"'), stripped.find("/*")) if at != -1]
    return stripped[: min(ends)] if ends else stripped


def _has_session_evidence(normalized: str) -> bool:
    """Whether ``normalized`` uses an inspector only session relevance has."""
    if _SESSION_MARKER_RE.search(normalized):
        return True
    return any(
        f"bes {match.group(1)}" not in _BES_PREFIX_CLIENT_PHRASES
        for match in _BES_PHRASE_RE.finditer(normalized)
    )


def classify_relevance_dialect(text: str) -> Dialect | None:
    """Guess which dialect ``text`` is written in from the relevance itself.

    Returns ``None`` for "unknown" -- no opinion about this statement, because
    nothing in it is specific to either dialect. That is deliberately distinct
    from :attr:`Dialect.UNCERTAIN`, which is a recorded conclusion, returned
    here when the statement uses inspectors from *both* dialects and so cannot
    be valid as either.

    Never returns :attr:`Dialect.BOTH`: proving every inspector in a statement
    is available to both dialects needs the future relevance parser, not marker
    matching. See the module docstring for the traps the marker lists avoid.
    """
    normalized = _normalize_phrase(_strip_non_code(text))
    session = _has_session_evidence(normalized)
    client = bool(_CLIENT_MARKER_RE.search(normalized))
    if session and client:
        return Dialect.UNCERTAIN
    if session:
        return Dialect.SESSION
    if client:
        return Dialect.CLIENT
    return None


# ---------------------------------------------------------------------------
# Which dialects to run a statement as
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DialectFit:
    """Which dialects a statement can run as: the ones worth evaluating it in.

    :attr:`basis` says how that was decided:

    - ``"resolved"``: every resolved reference belongs to the one dialect
    - ``"type-check"``: references exist in both, but only one dialect's type
      check accepts the statement (``name of operating system``: session has
      ``operating system of <bes computer>``, never a bare ``operating system``)
    - ``"either"``: both type checks accept it, e.g. ``now``
    - ``"unclear"``: neither type check accepts it (a typo) and the text gives
      no hint: client, as for a statement that doesn't parse
    - ``"mixed"``: it uses references from both dialects (``Dialect.UNCERTAIN``)
    - ``"classified"``: it doesn't parse or type-check, but the text classifier
      has a view (``bes <word>`` reads as session)
    - ``"default"``: it doesn't parse and nothing hints at session: client
    """

    dialects: frozenset[Dialect]
    """``CLIENT`` and/or ``SESSION``; never empty."""
    basis: str
    client_only: tuple[str, ...] = ()
    """References only client relevance has."""
    session_only: tuple[str, ...] = ()
    """References only session relevance has."""


def _type_checks(analysis: RelevanceAnalysis, dialect: Dialect) -> bool:
    """Whether ``analysis``'s statement type-checks cleanly under ``dialect``.

    No diagnostics is not enough on its own: an unknown name is silent, and
    leaves only an unknown plurality behind (#141's gotchas). Reads the check
    :func:`~bigfix_relevance_analyzer.analyzer.analyze` already ran as
    ``dialect`` where there is one, which is whenever the names say BOTH and
    one is known; otherwise checks again, as before.
    """
    from bigfix_relevance_analyzer.analyzer import analyze
    from bigfix_relevance_analyzer.typecheck import Plurality

    check = analysis._dialect_checks.get(dialect) or analyze(analysis.text, dialect=dialect).check
    return (
        check is not None
        and not check.diagnostics
        and check.value.plurality is not Plurality.UNKNOWN
    )


def dialect_fit(text: str) -> DialectFit:
    """Decide which dialects ``text`` can run as, from its references and type checks.

    For a front end choosing whether to evaluate a statement as client
    relevance, session relevance or both: the answer is never empty, says why
    (:attr:`DialectFit.basis`), and covers statements that do not parse or
    type-check by falling back on :func:`classify_relevance_dialect`.

    It branches on the dialects the reference *names* settle on, and when
    those say ``BOTH``, on whether each dialect's type check is clean. That is
    one step stricter than
    :attr:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis.resolved_dialect`,
    which since #141 also narrows ``BOTH`` by the form each name is written in
    (``name of operating system`` is CLIENT there, ``"type-check"`` here) but
    does not ask for a clean check: ``nme of operating system`` is CLIENT
    there and ``"unclear"`` here. The checks are the ones the analysis already
    ran, so this costs one analysis, not three.
    """
    # Imported here: `analyzer` builds on this module.
    from bigfix_relevance_analyzer.analyzer import analyze

    both = frozenset({Dialect.CLIENT, Dialect.SESSION})
    analysis = analyze(text)
    client_only = analysis.references_only_in(Dialect.CLIENT)
    session_only = analysis.references_only_in(Dialect.SESSION)

    def fit(dialects: frozenset[Dialect], basis: str) -> DialectFit:
        return DialectFit(dialects, basis, client_only, session_only)

    classified = analysis.classified_dialect
    resolved = analysis._named_dialect
    if is_definite(resolved):
        return fit(frozenset({resolved}), "resolved")
    if resolved is Dialect.UNCERTAIN:
        return fit(both, "mixed")
    if resolved is Dialect.BOTH:
        ok = frozenset(d for d in both if _type_checks(analysis, d))
        if len(ok) == 1:
            return fit(ok, "type-check")
        if ok:
            return fit(both, "either")
        if is_definite(classified):
            return fit(frozenset({classified}), "classified")
        return fit(frozenset({Dialect.CLIENT}), "unclear")
    # Unparsed, or nothing resolved: fall back on the text classifier.
    if is_definite(classified):
        return fit(frozenset({classified}), "classified")
    if classified is Dialect.UNCERTAIN:
        return fit(both, "mixed")
    return fit(frozenset({Dialect.CLIENT}), "default")
