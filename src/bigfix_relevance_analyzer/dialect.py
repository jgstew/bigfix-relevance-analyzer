"""Which relevance dialect a statement is written in, and the seam for guessing it.

BigFix has two relevance dialects that share overlapping syntax but are not the
same language: **client relevance**, evaluated by the BES Client on an endpoint,
and **session relevance**, evaluated by the root server against server-side
data. They have different inspectors available, so a statement that is valid in
one is usually meaningless in the other.

:func:`classify_relevance_dialect` is the seam for deciding a statement's
dialect from the inspectors and grammar *inside* it. It is deliberately not
implemented yet -- it returns ``None`` ("no opinion") -- so nothing currently
depends on content analysis. Today a statement's dialect comes entirely from
the context it was extracted from (which element of which kind of file), which
:mod:`bigfix_relevance_analyzer.extract` determines.

Notes for whoever implements the content classifier
---------------------------------------------------
The obvious approach -- match inspector names against a session-only and a
client-only word list -- has a trap worth knowing about before starting.

ClientUI dashboards (HTML rendered by the BES Client on the endpoint) contain
*client* relevance that freely uses ``sites``, ``relevant fixlets of sites``,
``relevant offer actions of sites``, ``ids of it`` and
``headers "Subject" of it``. Those read as server-side inspectors but are
perfectly valid on a client, so bare ``sites`` / ``fixlets`` / ``offer
actions`` must **not** be treated as session markers. Restrict the session
list to genuinely server-only forms: ``bes computers``, ``bes fixlets``,
``bes sites``, ``bes tasks``, ``bes property``, ``current console user``,
``current bes server``, ``current fixlet``, ``types``.

Matching also has to ignore text inside relevance string literals, or a
statement that merely mentions an inspector name in a quoted string gets
typed by it. See ``tests/examples/client_relevance/clientui/`` for content
that exercises the trap.
"""

from __future__ import annotations

import enum

__all__ = ["Dialect", "classify_relevance_dialect"]


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

    Real but rare. Nothing emits this yet -- proving it of a statement requires
    resolving every inspector in it, which needs the future relevance parser.
    """


def classify_relevance_dialect(text: str) -> Dialect | None:
    """Guess which dialect ``text`` is written in from the relevance itself.

    Returns ``None`` for "unknown" -- no opinion about this statement. That is
    deliberately distinct from :attr:`Dialect.UNCERTAIN`, which is a recorded
    conclusion ("we looked and could not tell").

    Currently returns ``None`` for every input: typing relevance by the
    inspectors and grammar it uses is future work, so dialect comes only from
    the context a statement was extracted from. Callers should already be
    written to handle a real answer here -- see the module docstring for the
    constraints an implementation has to respect.
    """
    del text  # Intentionally unused until content-based typing is implemented.
    return None
