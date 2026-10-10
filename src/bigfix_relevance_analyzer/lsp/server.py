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
Diagnostics, hover, completion and quick fixes. A document is linted on open, change and
save, and its diagnostics are published as ``textDocument/publishDiagnostics``;
closing it publishes an empty list. Sync is full-document only: relevance
statements are short, and incrementality pays off per *site* (the linter's
cache), not per keystroke within one. A document whose suffix no extractor
reads gets an empty list rather than silence, so nothing stale is left behind
if it was renamed.

``textDocument/hover`` answers from the stored text of an open document, with
a null result for a document that is not open or a position with nothing to
say. Hover params that are not a URI and two integers are invalid params.

``textDocument/completion`` answers from the stored text the same way, with a
``CompletionList`` of the linter's completions, best first: each a property
item with a ``sortText`` from its rank and a ``textEdit`` over what is being
typed. Its insert text is a snippet (``folders "$1"``) only for a client that
says it takes them (``completionItem.snippetSupport``). The list says it is
incomplete when it was cut short, so the client asks again as more is typed.
It is advertised with no trigger characters: a space would fire on every
word, and clients already ask as letters are typed and on an explicit request.

``textDocument/codeAction`` answers with the linter's quick fixes for the
requested range, as ``CodeAction`` literals carrying a ``WorkspaceEdit``. It is
advertised only to a client that takes literals (``codeActionLiteralSupport``);
there is no ``Command`` fallback. The edit is versioned (``documentChanges``,
with the document's version) when the client supports that, so it refuses an
edit made for text that has since changed; otherwise it is plain ``changes``.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
from collections.abc import Mapping
from typing import Any, TypeGuard

from bigfix_relevance_analyzer.lsp.linter import (
    COMPLETION_LIMIT,
    FIX_ALL_KIND,
    QUICKFIX_KIND,
    SOURCE,
    DocumentLinter,
    lsp_range,
)

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


class _CompletionItemKind(enum.IntEnum):
    PROPERTY = 10


class _InsertTextFormat(enum.IntEnum):
    SNIPPET = 2


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
        self._code_action_literals = False
        self._document_changes = False
        self._snippets = False
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
        if method == "textDocument/completion":
            return [self._completion(id_, params)]
        if method == "textDocument/codeAction":
            return [self._code_action(id_, params)]
        return [error_response(id_, ErrorCode.METHOD_NOT_FOUND, f"method not found: {method}")]

    def _initialize(self, params: Mapping[str, Any]) -> Message:
        from bigfix_relevance_analyzer import __version__

        self.linter.apply_options(params.get("initializationOptions"))
        self._initialized = True
        client = params.get("capabilities")
        self._code_action_literals = _has(
            client, "textDocument", "codeAction", "codeActionLiteralSupport"
        )
        self._document_changes = _has(client, "workspace", "workspaceEdit", "documentChanges")
        self._snippets = _has(
            client, "textDocument", "completion", "completionItem", "snippetSupport"
        )
        capabilities: Message = {
            "textDocumentSync": {
                "openClose": True,
                "change": int(_SyncKind.FULL),
                "save": {"includeText": False},
            },
            "hoverProvider": True,
            "completionProvider": {"resolveProvider": False},
        }
        if self._code_action_literals:
            capabilities["codeActionProvider"] = {"codeActionKinds": [QUICKFIX_KIND, FIX_ALL_KIND]}
        return {
            "capabilities": capabilities,
            "serverInfo": {"name": SOURCE, "version": __version__},
        }

    def _hover(self, id_: Any, params: Mapping[str, Any]) -> Message:
        identifier = params.get("textDocument")
        uri = identifier.get("uri") if isinstance(identifier, Mapping) else None
        position = _position(params.get("position"))
        if not isinstance(uri, str) or position is None:
            return error_response(
                id_, ErrorCode.INVALID_PARAMS, "hover needs a textDocument uri and a position"
            )
        document = self._documents.get(uri)
        if document is None:
            return _result(id_, None)
        found = self.linter.hover(uri, document.text, position, document.language_id)
        return _result(id_, found)

    def _completion(self, id_: Any, params: Mapping[str, Any]) -> Message:
        identifier = params.get("textDocument")
        uri = identifier.get("uri") if isinstance(identifier, Mapping) else None
        position = _position(params.get("position"))
        if not isinstance(uri, str) or position is None:
            return error_response(
                id_, ErrorCode.INVALID_PARAMS, "completion needs a textDocument uri and a position"
            )
        document = self._documents.get(uri)
        if document is None:
            return _result(id_, {"isIncomplete": False, "items": []})
        found = self.linter.completions(
            uri, document.text, position, document.language_id, snippets=self._snippets
        )
        items = []
        for completion in found:
            item: Message = {
                "label": completion.label,
                "kind": int(_CompletionItemKind.PROPERTY),
                "detail": completion.detail,
                "sortText": completion.sort_text,
                "filterText": completion.label,
            }
            if completion.range is not None:
                item["textEdit"] = {
                    "range": lsp_range(completion.range),
                    "newText": completion.insert_text,
                }
            else:
                item["insertText"] = completion.insert_text
            if completion.is_snippet:
                item["insertTextFormat"] = int(_InsertTextFormat.SNIPPET)
            items.append(item)
        return _result(id_, {"isIncomplete": len(found) >= COMPLETION_LIMIT, "items": items})

    def _code_action(self, id_: Any, params: Mapping[str, Any]) -> Message:
        identifier = params.get("textDocument")
        uri = identifier.get("uri") if isinstance(identifier, Mapping) else None
        found = _range(params.get("range"))
        if not isinstance(uri, str) or found is None:
            return error_response(
                id_, ErrorCode.INVALID_PARAMS, "codeAction needs a textDocument uri and a range"
            )
        document = self._documents.get(uri)
        if document is None:
            return _result(id_, [])
        context = params.get("context")
        only = context.get("only") if isinstance(context, Mapping) else None
        kinds = [kind for kind in only if isinstance(kind, str)] if isinstance(only, list) else None
        fixes = self.linter.fixes(uri, document.text, document.language_id, range=found, only=kinds)
        actions = []
        for fix in fixes:
            edits = [
                {"range": lsp_range(found), "newText": new_text} for found, new_text in fix.edits
            ]
            if self._document_changes:
                edit: Message = {
                    "documentChanges": [
                        {"textDocument": {"uri": uri, "version": document.version}, "edits": edits}
                    ]
                }
            else:
                edit = {"changes": {uri: edits}}
            action: Message = {
                "title": fix.title,
                "kind": fix.kind,
                "diagnostics": list(fix.diagnostics),
                "edit": edit,
            }
            if fix.is_preferred:
                action["isPreferred"] = True
            actions.append(action)
        return _result(id_, actions)

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
            self.linter.forget(uri)
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
            self.linter.forget(uri)
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


def _has(value: object, *keys: str) -> bool:
    """Whether ``value[keys[0]][keys[1]]...`` is there and truthy: a client
    capability, which an absent object at any level leaves off."""
    for key in keys:
        if not isinstance(value, Mapping):
            return False
        value = value.get(key)
    return bool(value)


def _position(value: object) -> tuple[int, int] | None:
    """An LSP ``Position`` as ``(line, character)``, if it is one."""
    if not isinstance(value, Mapping):
        return None
    line, character = value.get("line"), value.get("character")
    return (line, character) if _is_index(line) and _is_index(character) else None


def _range(value: object) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """An LSP ``Range`` as ``((line, character), (line, character))``, if it is
    one: two positions, the start not after the end."""
    if not isinstance(value, Mapping):
        return None
    start, end = _position(value.get("start")), _position(value.get("end"))
    if start is None or end is None or start > end:
        return None
    return start, end


def _is_index(value: object) -> TypeGuard[int]:
    """Whether ``value`` is a JSON integer, as a line or character must be."""
    return isinstance(value, int) and not isinstance(value, bool)


def _result(id_: Any, result: Any) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def error_response(id_: Any, code: ErrorCode, message: str) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": int(code), "message": message}}


def _notify(method: str, params: Message) -> Message:
    return {"jsonrpc": "2.0", "method": method, "params": params}
