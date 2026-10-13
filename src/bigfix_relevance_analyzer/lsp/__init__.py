"""A language server for BigFix Relevance: lint diagnostics and hover in any LSP editor.

Two layers, kept apart so the protocol one can be swapped (for pygls, say)
without touching the other:

- :mod:`~bigfix_relevance_analyzer.lsp.linter` -- :class:`DocumentLinter`,
  everything the editor is told, with no protocol in it; what a hover says
  is :mod:`~bigfix_relevance_analyzer.lsp.hover`'s.
- :mod:`~bigfix_relevance_analyzer.lsp.server` -- :class:`Server`, the
  hand-rolled JSON-RPC adapter over it, with no I/O;
  :mod:`~bigfix_relevance_analyzer.lsp.stdio` is the standard transport around
  that.

Run it with ``bigfix-relevance-lsp`` or ``python -m bigfix_relevance_analyzer.lsp``;
embed it in a language client's host by constructing a :class:`Server` and
passing each parsed JSON-RPC message to :meth:`Server.handle`. Force its dialect
with ``Server(linter=DocumentLinter(config=LintConfig(suggest=True, dialect=...)))``.

Without a language client -- a web page, a notebook, a WASM playground that
holds the text itself -- use :class:`StatementSession`
(:mod:`~bigfix_relevance_analyzer.lsp.session`): one statement, synced on
change, with requests answered against the text they were asked about, and
:class:`LspError` for an error response.

``Server``, ``StatementSession`` and ``LspError`` are imported on first use
rather than here, so that importing the linter alone -- as a different protocol
layer would -- never loads the protocol layer. Code that must have them loaded
up front (a componentize-py build, which keeps only what it saw imported)
imports their modules by name.
"""

from typing import TYPE_CHECKING, Any

from bigfix_relevance_analyzer.lsp.linter import DocumentLinter

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.lsp.server import Server
    from bigfix_relevance_analyzer.lsp.session import LspError, StatementSession

__all__ = ["DocumentLinter", "LspError", "Server", "StatementSession"]


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})


def __getattr__(name: str) -> Any:
    if name == "Server":
        from bigfix_relevance_analyzer.lsp.server import Server

        return Server
    if name in ("StatementSession", "LspError"):
        from bigfix_relevance_analyzer.lsp import session

        return getattr(session, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
