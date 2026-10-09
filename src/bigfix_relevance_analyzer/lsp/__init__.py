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
embed it by constructing a :class:`Server` and passing each parsed JSON-RPC
message to :meth:`Server.handle`.

``Server`` is imported on first use rather than here, so that importing the
linter alone -- as a different protocol layer would -- never loads this one.
"""

from typing import TYPE_CHECKING, Any

from bigfix_relevance_analyzer.lsp.linter import DocumentLinter

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.lsp.server import Server

__all__ = ["DocumentLinter", "Server"]


def __getattr__(name: str) -> Any:
    if name == "Server":
        from bigfix_relevance_analyzer.lsp.server import Server

        return Server
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
