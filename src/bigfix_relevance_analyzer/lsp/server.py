"""The language server's protocol layer: JSON-RPC messages in, messages out.

No I/O happens here. :meth:`Server.handle` takes one already-parsed message and
returns the messages to send back -- responses and notifications alike, in
order -- so the same object runs behind :mod:`~bigfix_relevance_analyzer.lsp.stdio`
for any editor and testing, and behind a plain function call where a host has
no stdio to give it (a WASM runtime inside an editor extension). One
implementation, two transports: what the stdio tests exercise is exactly what
an embedded host runs.

This is a thin adapter, on purpose
----------------------------------
Only the protocol lives here: dispatch, the initialize/shutdown/exit
lifecycle, error responses, and the store of open documents. What the editor
is *told* -- diagnostics, the per-site cache, the large-document guard, the
options that tune them -- is :class:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter`,
which knows nothing of JSON-RPC. Replacing this module with a pygls server
(issue 10 has the measured spike) means writing another adapter over the same
linter, not porting any of it.

What is served
--------------
Diagnostics and hover. A document is linted on open, change and
save, and its diagnostics are published as ``textDocument/publishDiagnostics``;
closing it publishes an empty list. Sync is full-document only: relevance
statements are short, and incrementality pays off per *site* (the linter's
cache), not per keystroke within one. A document whose suffix no extractor
reads gets an empty list rather than silence, so nothing stale is left behind
if it was renamed.

``textDocument/hover`` answers from the stored text of an open document, with
a null result for a document that is not open or a position with nothing to
say. Hover params that are not a URI and two integers are invalid params.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
from collections.abc import Mapping
from typing import Any, TypeGuard

from bigfix_relevance_analyzer.lsp.linter import SOURCE, DocumentLinter

logger = logging.getLogger(__name__)

Message = dict[str, Any]


class ErrorCode(enum.IntEnum):
    """The JSON-RPC and LSP error codes this server and its transport answer with."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_NOT_INITIALIZED = -32002


class _SyncKind(enum.IntEnum):
    FULL = 1


@dataclasses.dataclass(slots=True)
class _Document:
    text: str
    version: int | None
    language_id: str | None = None


class Server:
    """One language server session's state. Feed it messages with :meth:`handle`."""

    def __init__(self, linter: DocumentLinter | None = None) -> None:
        self.linter = linter if linter is not None else DocumentLinter()
        """Where every diagnostic comes from. See the module docstring."""

        self.exit_code: int | None = None
        """``None`` until ``exit``; then 0 if ``shutdown`` came first, else 1, per the spec."""

        self._initialized = False
        self._shutdown = False
        self._documents: dict[str, _Document] = {}

    def handle(self, message: Mapping[str, Any]) -> list[Message]:
        """Every message to send in answer to ``message``, in order. Never raises.

        A handler that fails is logged; a request then gets an internal-error
        response, a notification gets nothing.
        """
        if not isinstance(message, Mapping):
            return [error_response(None, ErrorCode.INVALID_REQUEST, "a message must be an object")]
        method = message.get("method")
        has_id = "id" in message
        if method is None:
            # A response to a request this server never sends, or junk.
            if has_id and ("result" in message or "error" in message):
                return []
            return [error_response(message.get("id"), ErrorCode.INVALID_REQUEST, "no method")]
        # Absent means empty; only `None` does. `or {}` would also turn `[]` into `{}`.
        params = message.get("params")
        if params is None:
            params = {}
        # JSON-RPC also allows an array, but LSP defines only object params.
        if not isinstance(params, Mapping):
            if has_id:
                return [
                    error_response(
                        message["id"], ErrorCode.INVALID_PARAMS, "params must be an object"
                    )
                ]
            return []
        try:
            if has_id:
                return self._request(message["id"], method, params)
            return self._notification(method, params)
        except Exception as error:
            logger.exception("%s failed", method)
            if has_id:
                return [
                    error_response(message["id"], ErrorCode.INTERNAL_ERROR, f"{method}: {error}")
                ]
            return []

    # -- requests -------------------------------------------------------------

    def _request(self, id_: Any, method: str, params: Mapping[str, Any]) -> list[Message]:
        if method == "initialize":
            if self._initialized:
                return [error_response(id_, ErrorCode.INVALID_REQUEST, "already initialized")]
            return [_result(id_, self._initialize(params))]
        if not self._initialized:
            return [error_response(id_, ErrorCode.SERVER_NOT_INITIALIZED, "not initialized")]
        if self._shutdown:
            return [error_response(id_, ErrorCode.INVALID_REQUEST, "shutting down")]
        if method == "shutdown":
            self._shutdown = True
            return [_result(id_, None)]
        if method == "textDocument/hover":
            return [self._hover(id_, params)]
        return [error_response(id_, ErrorCode.METHOD_NOT_FOUND, f"method not found: {method}")]

    def _initialize(self, params: Mapping[str, Any]) -> Message:
        from bigfix_relevance_analyzer import __version__

        self.linter.apply_options(params.get("initializationOptions"))
        self._initialized = True
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": int(_SyncKind.FULL),
                    "save": {"includeText": False},
                },
                "hoverProvider": True,
            },
            "serverInfo": {"name": SOURCE, "version": __version__},
        }

    def _hover(self, id_: Any, params: Mapping[str, Any]) -> Message:
        identifier = params.get("textDocument")
        position = params.get("position")
        uri = identifier.get("uri") if isinstance(identifier, Mapping) else None
        line = position.get("line") if isinstance(position, Mapping) else None
        character = position.get("character") if isinstance(position, Mapping) else None
        if not isinstance(uri, str) or not _is_index(line) or not _is_index(character):
            return error_response(
                id_, ErrorCode.INVALID_PARAMS, "hover needs a textDocument uri and a position"
            )
        document = self._documents.get(uri)
        if document is None:
            return _result(id_, None)
        found = self.linter.hover(uri, document.text, (line, character), document.language_id)
        return _result(id_, found)

    # -- notifications --------------------------------------------------------

    def _notification(self, method: str, params: Mapping[str, Any]) -> list[Message]:
        if method == "exit":
            self.exit_code = 0 if self._shutdown else 1
            return []
        # Before `initialize`, the spec says to drop every notification but
        # `exit`; after `shutdown`, the server does no more work.
        if not self._initialized or self._shutdown:
            return []
        if method == "textDocument/didOpen":
            document = params["textDocument"]
            uri = document["uri"]
            self._documents[uri] = _Document(
                document["text"], document.get("version"), document.get("languageId")
            )
            return [self._publish(uri)]
        if method == "textDocument/didChange":
            return self._did_change(params)
        if method == "textDocument/didSave":
            uri = params["textDocument"]["uri"]
            return [self._publish(uri)] if uri in self._documents else []
        if method == "textDocument/didClose":
            uri = params["textDocument"]["uri"]
            self._documents.pop(uri, None)
            return [_notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})]
        return []

    def _did_change(self, params: Mapping[str, Any]) -> list[Message]:
        identifier = params["textDocument"]
        uri = identifier["uri"]
        document = self._documents.get(uri)
        if document is None:
            return []
        changes = params.get("contentChanges") or []
        if any("range" in change for change in changes):
            # Only full sync is advertised, so this is a client that ignored it.
            # The stored text no longer matches the buffer, so the findings on
            # screen are stale: clear them, and forget the document so a later
            # save cannot publish new stale ones. It is linted again once the
            # client reopens it.
            logger.warning("ignoring a ranged change to %s: only full sync is supported", uri)
            del self._documents[uri]
            return [_notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})]
        if not changes:
            return []
        document.text = changes[-1]["text"]
        document.version = identifier.get("version")
        return [self._publish(uri)]

    # -- diagnostics ----------------------------------------------------------

    def _publish(self, uri: str) -> Message:
        document = self._documents[uri]
        params: Message = {
            "uri": uri,
            "version": document.version,
            "diagnostics": self.linter.diagnostics(uri, document.text, document.language_id),
        }
        return _notify("textDocument/publishDiagnostics", params)


def _is_index(value: object) -> TypeGuard[int]:
    """Whether ``value`` is a JSON integer, as a line or character must be."""
    return isinstance(value, int) and not isinstance(value, bool)


def _result(id_: Any, result: Any) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def error_response(id_: Any, code: ErrorCode, message: str) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": int(code), "message": message}}


def _notify(method: str, params: Message) -> Message:
    return {"jsonrpc": "2.0", "method": method, "params": params}
