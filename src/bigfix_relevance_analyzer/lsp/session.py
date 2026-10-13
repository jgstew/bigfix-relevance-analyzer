"""The language server for one statement, embedded without a language client.

An editor that speaks LSP has a client to keep the server's copy of a document
current. A web page, a notebook or a WebAssembly playground usually has none: it
holds the text itself and wants answers about it. :class:`StatementSession` is
that client, cut down to one document and run in-process over
:meth:`Server.handle() <bigfix_relevance_analyzer.lsp.server.Server.handle>`::

    from bigfix_relevance_analyzer.lsp import StatementSession

    session = StatementSession()          # or StatementSession(dialect=Dialect.SESSION)
    diagnostics = session.sync(text)      # None when the text has not changed
    hover = session.request("textDocument/hover", {"position": position}, text)
    session.close()

The caller owns the text and hands it to every call; the session opens the
document on first use and sends a full-text change whenever the text differs,
so a request is always answered against the text it was asked about. Answers
are the server's own LSP JSON: whatever the VS Code extension is told, a
session is told the same.

Runs in WASM
------------
The playground's componentize-py component keeps only the modules imported
when it is built, so everything here is imported at module level, and nothing
needs a codec but UTF-8 (positions are UTF-16 counted, never encoded).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import LintConfig
from bigfix_relevance_analyzer.lsp.linter import (
    FIX_ALL_KIND,
    LANGUAGE_ID,
    QUICKFIX_KIND,
    DocumentLinter,
)
from bigfix_relevance_analyzer.lsp.server import Server

_PUBLISH_DIAGNOSTICS: Final = "textDocument/publishDiagnostics"


class LspError(Exception):
    """A JSON-RPC error response from the language server."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"{message} (code {code})")
        self.code = code
        """The JSON-RPC error code, e.g. ``-32601`` for an unknown method."""
        self.message = message
        """The server's message, without the code."""

    def __reduce__(self) -> tuple[type[LspError], tuple[int, str]]:
        # `args` holds only the formatted text, which __init__ cannot take back.
        return type(self), (self.code, self.message)


class StatementSession:
    """One relevance statement held in an in-process :class:`~bigfix_relevance_analyzer.lsp.Server`.

    For an editor that is not a language client (a web page, a notebook):
    the caller owns the text and hands it to every call, and the session
    keeps the server's copy current, opening the document on first use and
    sending a full-text change whenever the text differs. So a request is
    always answered against the text it was asked about.

    The document is :attr:`URI` with language :attr:`LANGUAGE_ID`: one plain
    statement, as a ``.rel`` file. ``dialect`` forces it, as
    :attr:`LintConfig.dialect <bigfix_relevance_analyzer.lint.LintConfig.dialect>`
    does; ``None`` lets the server decide.

    Positions are LSP's: 0-based line and UTF-16 character, which is also
    what CodeMirror 6 counts in. Not thread-safe: one caller at a time.
    """

    URI: Final = "untitled:statement"
    LANGUAGE_ID: Final = LANGUAGE_ID
    CAPABILITIES: Final[Mapping[str, Any]] = {
        "textDocument": {
            "codeAction": {
                "codeActionLiteralSupport": {
                    "codeActionKind": {"valueSet": [QUICKFIX_KIND, FIX_ALL_KIND]}
                }
            },
            # No snippet support: plain insert text is all a minimal client handles.
            "completion": {"completionItem": {"snippetSupport": False}},
        },
        # Plain {uri: [TextEdit]} edits; this session never versions edits.
        "workspace": {"workspaceEdit": {"documentChanges": False}},
    }
    """What the session tells the server it can take, at ``initialize``."""

    def __init__(self, *, dialect: Dialect | None = None) -> None:
        self.dialect = dialect
        """The dialect forced on the statement; ``None`` when the server decides."""
        config = LintConfig(suggest=True, dialect=dialect)
        self._server = Server(linter=DocumentLinter(config=config))
        self._ids = 0
        self._text: str | None = None
        self.version = 0
        """Bumped on every text the server is sent; 0 before the first."""
        self.diagnostics: list[dict[str, Any]] = []
        """The server's diagnostics for the text it holds, however it got there
        (:meth:`sync` or the sync inside :meth:`request`)."""
        self._closed = False
        self._call("initialize", {"processId": None, "capabilities": self.CAPABILITIES})
        self._notify("initialized", {})

    def sync(self, text: str) -> list[dict[str, Any]] | None:
        """Make the server's copy ``text``. Its diagnostics if that changed it, else None.

        None means "nothing new", not "no diagnostics": :attr:`diagnostics`
        always has the latest. Raises :class:`RuntimeError` once closed.

        The server never fails a notification: should linting itself fail, it
        logs the error and publishes nothing, which reads here as no
        diagnostics for that text.
        """
        if self._closed:
            raise RuntimeError("StatementSession is closed")
        if text == self._text:
            return None
        self.version += 1
        if self._text is None:
            document = {
                "uri": self.URI,
                "languageId": self.LANGUAGE_ID,
                "version": self.version,
                "text": text,
            }
            replies = self._notify("textDocument/didOpen", {"textDocument": document})
        else:
            replies = self._notify(
                "textDocument/didChange",
                {
                    "textDocument": {"uri": self.URI, "version": self.version},
                    "contentChanges": [{"text": text}],
                },
            )
        self._text = text
        self.diagnostics = next(
            (
                list(reply["params"]["diagnostics"])
                for reply in replies
                if reply.get("method") == _PUBLISH_DIAGNOSTICS
            ),
            [],
        )
        return list(self.diagnostics)

    def request(self, method: str, params: Mapping[str, Any], text: str) -> Any:
        """``method``'s result for the document holding ``text``.

        ``params`` without ``textDocument``; the session adds it, replacing
        any given. Raises :class:`LspError` for an error response, and
        :class:`RuntimeError` once closed.
        """
        self.sync(text)
        return self._call(method, {**params, "textDocument": {"uri": self.URI}})

    def close(self) -> None:
        """Close the document and shut the server down. Safe to call twice.

        Closed afterwards in any case: a ``shutdown`` already sent through
        :meth:`request` makes this raise :class:`LspError` once, not again."""
        if self._closed:
            return
        self._closed = True
        if self._text is not None:
            self._notify("textDocument/didClose", {"textDocument": {"uri": self.URI}})
        try:
            self._call("shutdown", None)
        finally:
            self._notify("exit", None)

    def _call(self, method: str, params: Mapping[str, Any] | None) -> Any:
        self._ids += 1
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": self._ids, "method": method}
        if params is not None:
            message["params"] = params
        for reply in self._server.handle(message):
            if reply.get("id") != self._ids:
                continue
            if "error" in reply:
                error = reply["error"]
                raise LspError(error["code"], error["message"])
            return reply.get("result")
        raise LspError(-32603, f"no response to {method}")

    def _notify(self, method: str, params: Mapping[str, Any] | None) -> list[dict[str, Any]]:
        message: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        return self._server.handle(message)
