"""A language server for BigFix Relevance: lint diagnostics in any LSP editor.

:mod:`~bigfix_relevance_analyzer.lsp.server` is the protocol logic, with no
I/O; :mod:`~bigfix_relevance_analyzer.lsp.stdio` is the standard transport
around it. Run it with ``bigfix-relevance-lsp`` or
``python -m bigfix_relevance_analyzer.lsp``; embed it by constructing a
:class:`Server` and passing each parsed JSON-RPC message to
:meth:`Server.handle`.
"""

from bigfix_relevance_analyzer.lsp.server import Server

__all__ = ["Server"]
