"""The language server's protocol logic: JSON-RPC messages in, messages out.

No I/O happens here. :meth:`Server.handle` takes one already-parsed message and
returns the messages to send back -- responses and notifications alike, in
order -- so the same object runs behind :mod:`~bigfix_relevance_analyzer.lsp.stdio`
for any editor and testing, and behind a plain function call where a host has
no stdio to give it (a WASM runtime inside an editor extension). One
implementation, two transports: what the stdio tests exercise is exactly what
an embedded host runs.

What is served
--------------
Diagnostics, and nothing else yet. A document is linted on open, change and
save -- exactly as :func:`~bigfix_relevance_analyzer.lint.lint_file` would lint
it, through the same extractors and rules -- and its findings are published as
``textDocument/publishDiagnostics``. Sync is full-document only: relevance
statements are short, and incrementality pays off per *site* (the cache below),
not per keystroke within one.

The file type comes from the document URI's suffix, as it does for the linter.
A document whose suffix no extractor reads gets an empty diagnostic list
rather than silence, so nothing stale is left behind if it was renamed.

A diagnostic spans its whole line. A finding records a line, not a range, and
the column a parse error has is already in its message. Precise ranges need
findings to carry a span through extraction's source map, a change to
:class:`~bigfix_relevance_analyzer.lint.Finding` worth making on its own.

The per-site cache
------------------
:mod:`~bigfix_relevance_analyzer.lint` already memoizes ``analyze`` per
statement, but not the judgement over it, and the judgement is not always
cheap: an editor wants ``unknown-inspector``'s "did you mean" leads
(:attr:`LintConfig.suggest`), and those cost tens of milliseconds per unknown
name. On a keystroke every site but one is byte-identical to the last pass, so
the server keeps each site's findings, keyed by everything about the site but
its position, and moves them to the site's current line on a hit. That is
server state on purpose: a library cache would be overhead for a pre-commit
hook, which never sees the same document twice.

The large-document guard
------------------------
Linting is synchronous, and a server that blocks for seconds on open is a hung
editor. Real content has one 13 MB generated task with 24,240 sites that takes
about 19 s to lint; every other file in the same corpus is under 410 KB. A
document over :data:`DEFAULT_MAX_DOCUMENT_BYTES` (UTF-8) gets one informational
:data:`DOCUMENT_TOO_LARGE` diagnostic instead of findings. The limit is the
``maxDocumentBytes`` initialization option. That code is the server's, not a
lint rule: it says the document was not judged, never that it is wrong.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import re
from collections import OrderedDict
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any, Final, NamedTuple
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from bigfix_relevance_analyzer.extract import RelevanceSite
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    _judge_site,
    _lint_data,
)

logger = logging.getLogger(__name__)

Message = dict[str, Any]

SOURCE: Final = "bigfix-relevance-analyzer"
"""The ``source`` on every diagnostic, and the server's name in ``serverInfo``."""

DEFAULT_MAX_DOCUMENT_BYTES: Final = 1024 * 1024
"""Documents larger than this, in UTF-8 bytes, are not linted. See the module docstring."""

DOCUMENT_TOO_LARGE: Final = "document-too-large"
"""The code of the one diagnostic an oversized document gets."""

DEFAULT_CACHE_SIZE: Final = 2048
"""Sites whose findings the server keeps -- as many as lint keeps analyses."""


_LINE_BREAK: Final = re.compile(r"\r\n|\r|\n")
"""What LSP counts as a line break -- only these, unlike :meth:`str.splitlines`,
which also breaks on form feeds and Unicode separators a client does not."""


class ErrorCode(enum.IntEnum):
    """The JSON-RPC and LSP error codes this server and its transport answer with."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INTERNAL_ERROR = -32603
    SERVER_NOT_INITIALIZED = -32002


class _SyncKind(enum.IntEnum):
    FULL = 1


class _DiagnosticSeverity(enum.IntEnum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3


_SEVERITIES: Final = {
    Severity.ERROR: _DiagnosticSeverity.ERROR,
    Severity.WARNING: _DiagnosticSeverity.WARNING,
}


class CacheStats(NamedTuple):
    """How the per-site cache has done since the server started."""

    hits: int
    misses: int
    size: int


@dataclasses.dataclass(slots=True)
class _Document:
    text: str
    version: int | None


class Server:
    """One language server session's state. Feed it messages with :meth:`handle`."""

    def __init__(self, *, cache_size: int = DEFAULT_CACHE_SIZE) -> None:
        self.max_document_bytes = DEFAULT_MAX_DOCUMENT_BYTES
        self.exit_code: int | None = None
        """``None`` until ``exit``; then 0 if ``shutdown`` came first, else 1, per the spec."""

        self._config = LintConfig(suggest=True)
        self._initialized = False
        self._shutdown = False
        self._documents: dict[str, _Document] = {}
        self._cache: OrderedDict[RelevanceSite, tuple[Finding, ...]] = OrderedDict()
        self._cache_size = cache_size
        self._hits = 0
        self._misses = 0

    def cache_stats(self) -> CacheStats:
        return CacheStats(self._hits, self._misses, len(self._cache))

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
        params = message.get("params") or {}
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
            return [_result(id_, self._initialize(params))]
        if not self._initialized:
            return [error_response(id_, ErrorCode.SERVER_NOT_INITIALIZED, "not initialized")]
        if self._shutdown:
            return [error_response(id_, ErrorCode.INVALID_REQUEST, "shutting down")]
        if method == "shutdown":
            self._shutdown = True
            return [_result(id_, None)]
        return [error_response(id_, ErrorCode.METHOD_NOT_FOUND, f"method not found: {method}")]

    def _initialize(self, params: Mapping[str, Any]) -> Message:
        from bigfix_relevance_analyzer import __version__

        options = params.get("initializationOptions") or {}
        if "maxDocumentBytes" in options:
            limit = options["maxDocumentBytes"]
            # `bool` is an `int`; `True` bytes is not a limit anyone meant.
            if isinstance(limit, int) and not isinstance(limit, bool) and limit >= 0:
                self.max_document_bytes = limit
            else:
                logger.warning(
                    "ignoring maxDocumentBytes %r: not a non-negative integer; keeping %d",
                    limit,
                    self.max_document_bytes,
                )
        self._initialized = True
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": int(_SyncKind.FULL),
                    "save": {"includeText": False},
                },
            },
            "serverInfo": {"name": SOURCE, "version": __version__},
        }

    # -- notifications --------------------------------------------------------

    def _notification(self, method: str, params: Mapping[str, Any]) -> list[Message]:
        if method == "exit":
            self.exit_code = 0 if self._shutdown else 1
            return []
        # Before `initialize`, the spec says to drop every notification but `exit`.
        if not self._initialized:
            return []
        if method == "textDocument/didOpen":
            document = params["textDocument"]
            uri = document["uri"]
            self._documents[uri] = _Document(document["text"], document.get("version"))
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
            logger.warning("ignoring a ranged change to %s: only full sync is supported", uri)
            return []
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
            "diagnostics": self._diagnostics(uri, document.text),
        }
        return _notify("textDocument/publishDiagnostics", params)

    def _diagnostics(self, uri: str, text: str) -> list[Message]:
        data = text.encode("utf-8", errors="surrogatepass")
        lines = _LINE_BREAK.split(text)
        if len(data) > self.max_document_bytes:
            message = (
                f"not linted: {len(data)} bytes is over the {self.max_document_bytes}-byte "
                "limit (maxDocumentBytes)"
            )
            return [
                _diagnostic(lines, 0, _DiagnosticSeverity.INFORMATION, DOCUMENT_TOO_LARGE, message)
            ]
        findings = _lint_data(_path_of(uri), data, self._config, self._judge)
        return [
            _diagnostic(
                lines,
                max(finding.line - 1, 0),
                _SEVERITIES[finding.severity],
                finding.code,
                finding.message,
            )
            for finding in findings
        ]

    def _judge(
        self, file_path: Path | None, site: RelevanceSite, config: LintConfig
    ) -> tuple[Finding, ...]:
        """:func:`~bigfix_relevance_analyzer.lint._judge_site`, cached per site.

        Keyed on the site with its line zeroed, so a statement that only moved
        is a hit. ``source_map`` is excluded from a site's equality already,
        and nothing in a finding depends on it. Findings are computed as if the
        site were at line 1 with no path, then moved: a finding's line is
        ``site.line`` plus its offset within the statement.
        """
        key = dataclasses.replace(site, line=1)
        cached = self._cache.get(key)
        if cached is None:
            self._misses += 1
            cached = _judge_site(None, key, config)
            self._cache[key] = cached
            if len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
        else:
            self._hits += 1
            self._cache.move_to_end(key)
        return tuple(
            dataclasses.replace(
                finding, line=finding.line + site.line - 1, path=file_path, site=site
            )
            for finding in cached
        )


def _path_of(uri: str) -> Path:
    """The path a document URI names, for its suffix. Never opened."""
    parsed = urlparse(uri)
    if parsed.scheme == "file":
        return Path(url2pathname(parsed.path))
    # `untitled:Untitled-1` and the like: whatever name there is, for its suffix.
    return Path(PurePosixPath(unquote(parsed.path)).name or "untitled")


def _utf16_length(line: str) -> int:
    """``line``'s length in UTF-16 code units: two for an astral character.

    Counted rather than encoded on purpose. A WASM host has only the codecs its
    build snapshot saw, and ``str.encode("utf-16-le")`` raised ``LookupError``
    inside a componentize-py component, losing every diagnostic.
    """
    return len(line) + sum(1 for char in line if ord(char) > 0xFFFF)


def _diagnostic(
    lines: list[str], line: int, severity: _DiagnosticSeverity, code: str, message: str
) -> Message:
    """A diagnostic over the whole of ``line`` (0-based), in UTF-16 code units."""
    end = _utf16_length(lines[line]) if line < len(lines) else 0
    return {
        "range": {
            "start": {"line": line, "character": 0},
            "end": {"line": line, "character": end},
        },
        "severity": int(severity),
        "code": code,
        "source": SOURCE,
        "message": message,
    }


def _result(id_: Any, result: Any) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def error_response(id_: Any, code: ErrorCode, message: str) -> Message:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": int(code), "message": message}}


def _notify(method: str, params: Message) -> Message:
    return {"jsonrpc": "2.0", "method": method, "params": params}
