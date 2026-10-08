"""Tests for the language server: :mod:`bigfix_relevance_analyzer.lsp`.

Most of these drive :meth:`Server.handle` directly -- the embedded transport a
WASM host uses -- with already-parsed JSON-RPC messages, and read back the
messages it answers with. The stdio transport gets its own tests for framing
only, plus one end-to-end run as a real subprocess.

Judgement is not re-tested here: a diagnostic is right when it carries what
:mod:`~bigfix_relevance_analyzer.lint` found for the same content, so these
compare against ``lint_file`` rather than restating its rules.
"""

from __future__ import annotations

import io
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from _helpers import BES_EXAMPLE, BROKEN, CLIENT, UNKNOWN_INSPECTOR, run_fresh_python, write

from bigfix_relevance_analyzer import __version__
from bigfix_relevance_analyzer.lint import LintConfig, lint_file
from bigfix_relevance_analyzer.lsp import linter as linter_module
from bigfix_relevance_analyzer.lsp import stdio
from bigfix_relevance_analyzer.lsp.linter import (
    DEFAULT_MAX_DOCUMENT_BYTES,
    DOCUMENT_TOO_LARGE,
    SOURCE,
    DocumentLinter,
)
from bigfix_relevance_analyzer.lsp.server import Server

Message = dict[str, Any]

ROOT_URI = "file:///workspace"

E_ACUTE = chr(0xE9)
"""Two bytes in UTF-8, spelled so the source stays ASCII (a pre-commit hook enforces it)."""


def uri(name: str) -> str:
    return f"{ROOT_URI}/{name}"


def request(method: str, params: Any = None, id_: int = 1) -> Message:
    message: Message = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        message["params"] = params
    return message


def notification(method: str, params: Any = None) -> Message:
    message: Message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    return message


def initialize(server: Server, **options: Any) -> Message:
    params: dict[str, Any] = {"processId": None, "rootUri": ROOT_URI, "capabilities": {}}
    if options:
        params["initializationOptions"] = options
    (response,) = server.handle(request("initialize", params))
    assert server.handle(notification("initialized", {})) == []
    return response


def started(**options: Any) -> Server:
    server = Server()
    initialize(server, **options)
    return server


def did_open(server: Server, name: str, text: str, version: int = 1) -> list[Message]:
    document = {"uri": uri(name), "languageId": "plaintext", "version": version, "text": text}
    return server.handle(notification("textDocument/didOpen", {"textDocument": document}))


def did_change(server: Server, name: str, text: str, version: int) -> list[Message]:
    return server.handle(
        notification(
            "textDocument/didChange",
            {
                "textDocument": {"uri": uri(name), "version": version},
                "contentChanges": [{"text": text}],
            },
        )
    )


def published(messages: list[Message], name: str) -> Message:
    """The one ``publishDiagnostics`` notification for ``name`` in ``messages``."""
    matches = [
        message["params"]
        for message in messages
        if message.get("method") == "textDocument/publishDiagnostics"
        and message["params"]["uri"] == uri(name)
    ]
    assert len(matches) == 1, messages
    params: Message = matches[0]
    return params


def diagnostics(messages: list[Message], name: str) -> list[Message]:
    found: list[Message] = published(messages, name)["diagnostics"]
    return found


def as_lint(found: list[Message]) -> list[tuple[str, str, int]]:
    """Diagnostics reduced to what a lint finding says: code, message, 1-based line."""
    return [(d["code"], d["message"], d["range"]["start"]["line"] + 1) for d in found]


def lint_expected(path: Path) -> list[tuple[str, str, int]]:
    """What lint reports for ``path``, in the shape :func:`as_lint` reduces to."""
    return [
        (finding.code, finding.message, finding.line)
        for finding in lint_file(path, LintConfig(suggest=True))
    ]


# ---------------------------------------------------------------------------
# Lifecycle and dispatch
# ---------------------------------------------------------------------------


def test_initialize_advertises_full_sync_and_names_the_server() -> None:
    response = initialize(Server())
    assert response["id"] == 1
    assert response["result"]["capabilities"] == {
        "textDocumentSync": {"openClose": True, "change": 1, "save": {"includeText": False}},
    }
    assert response["result"]["serverInfo"] == {"name": SOURCE, "version": __version__}


def test_a_request_before_initialize_is_refused() -> None:
    (response,) = Server().handle(request("textDocument/hover", {}, id_=7))
    assert response["id"] == 7
    assert response["error"]["code"] == -32002


def test_a_notification_before_initialize_is_dropped() -> None:
    server = Server()
    assert did_open(server, "a.rel", BROKEN) == []


def test_unknown_request_is_method_not_found_and_unknown_notification_is_ignored() -> None:
    server = started()
    (response,) = server.handle(request("textDocument/frobnicate", {}, id_=3))
    assert response == {
        "jsonrpc": "2.0",
        "id": 3,
        "error": {"code": -32601, "message": "method not found: textDocument/frobnicate"},
    }
    assert server.handle(notification("textDocument/frobnicate", {})) == []
    assert server.handle(notification("$/cancelRequest", {"id": 3})) == []


def test_a_message_that_is_not_a_request_is_invalid() -> None:
    server = started()
    (response,) = server.handle({"jsonrpc": "2.0", "id": 4})
    assert response["id"] == 4
    assert response["error"]["code"] == -32600


def test_a_response_from_the_client_is_ignored() -> None:
    assert started().handle({"jsonrpc": "2.0", "id": 9, "result": None}) == []


def test_shutdown_then_exit_is_a_clean_exit() -> None:
    server = started()
    (response,) = server.handle(request("shutdown", id_=2))
    assert response == {"jsonrpc": "2.0", "id": 2, "result": None}
    (refused,) = server.handle(request("textDocument/hover", {}, id_=3))
    assert refused["error"]["code"] == -32600
    assert server.exit_code is None
    assert server.handle(notification("exit")) == []
    assert server.exit_code == 0


def test_exit_without_shutdown_is_an_unclean_exit() -> None:
    server = started()
    server.handle(notification("exit"))
    assert server.exit_code == 1


def test_a_failing_handler_is_logged_and_does_not_escape(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError("boom")

    server = started()
    monkeypatch.setattr(linter_module, "_lint_data", explode)
    with caplog.at_level(logging.ERROR, logger="bigfix_relevance_analyzer"):
        assert did_open(server, "a.rel", BROKEN) == []
    assert "boom" in caplog.text


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def test_a_clean_document_publishes_an_empty_list() -> None:
    params = published(did_open(started(), "clean.rel", CLIENT), "clean.rel")
    assert params == {"uri": uri("clean.rel"), "version": 1, "diagnostics": []}


def test_a_broken_statement_is_an_error_spanning_its_line() -> None:
    found = diagnostics(did_open(started(), "broken.rel", BROKEN), "broken.rel")
    assert found
    for diagnostic in found:
        assert diagnostic["severity"] == 1
        assert diagnostic["source"] == SOURCE
        assert diagnostic["range"] == {
            "start": {"line": 0, "character": 0},
            "end": {"line": 0, "character": len(BROKEN)},
        }
    assert "error-token" in {diagnostic["code"] for diagnostic in found}


def test_line_end_is_counted_in_utf16_code_units() -> None:
    """LSP's default position encoding: an astral character is two units."""
    text = '"\U0001f600" & ' + BROKEN
    (first, *_) = diagnostics(did_open(started(), "emoji.rel", text), "emoji.rel")
    assert first["range"]["end"] == {"line": 0, "character": len(text) + 1}


def test_diagnostics_need_no_codec_beyond_utf8() -> None:
    """A WASM host has no codecs it was not built with.

    componentize-py snapshots the interpreter at build time, so a codec first
    looked up at runtime is missing there: ``str.encode("utf-16-le")`` raised
    ``LookupError`` inside the component and every diagnostic was lost. Blocking
    the UTF-16 codecs in a fresh interpreter reproduces that on the host.
    """
    run_fresh_python(
        """
import sys
for name in ("encodings.utf_16", "encodings.utf_16_le", "encodings.utf_16_be"):
    sys.modules[name] = None
from bigfix_relevance_analyzer.lsp.server import Server
server = Server()
server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
text = '"\\U0001f600" & exists file "unterminated'
(reply,) = server.handle({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {
    "textDocument": {"uri": "file:///w/a.rel", "languageId": "x", "version": 1, "text": text}}})
found = reply["params"]["diagnostics"]
assert found, reply
assert found[0]["range"]["end"]["character"] == len(text) + 1, found
print("ok")
"""
    )


def test_a_warning_is_severity_two() -> None:
    found = diagnostics(did_open(started(), "u.rel", UNKNOWN_INSPECTOR), "u.rel")
    assert [(d["code"], d["severity"]) for d in found] == [("unknown-inspector", 2)]


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("example.bes", BES_EXAMPLE.read_text()),
        ("unknown.rel", UNKNOWN_INSPECTOR),
        ("two.md", f"# doc\n\n```relevance\n{CLIENT}\n```\n\n```relevance\n{BROKEN}\n```\n"),
    ],
)
def test_diagnostics_carry_exactly_what_lint_finds(tmp_path: Path, name: str, text: str) -> None:
    """Including ``suggest``, which lint recommends for an interactive consumer."""
    found = diagnostics(did_open(started(), name, text), name)
    assert as_lint(found) == lint_expected(write(tmp_path, name, text))


def test_an_unsaved_buffer_is_linted_not_the_file_on_disk(tmp_path: Path) -> None:
    on_disk = write(tmp_path, "doc.rel", CLIENT)
    server = started()
    document = {"uri": on_disk.as_uri(), "languageId": "x", "version": 1, "text": BROKEN}
    messages = server.handle(notification("textDocument/didOpen", {"textDocument": document}))
    (params,) = (m["params"] for m in messages)
    assert params["diagnostics"]


def test_did_change_replaces_the_text_and_tracks_the_version() -> None:
    server = started()
    did_open(server, "a.rel", CLIENT)
    params = published(did_change(server, "a.rel", BROKEN, version=2), "a.rel")
    assert params["version"] == 2
    assert params["diagnostics"]
    params = published(did_change(server, "a.rel", CLIENT, version=3), "a.rel")
    assert params == {"uri": uri("a.rel"), "version": 3, "diagnostics": []}


def test_did_save_relints() -> None:
    server = started()
    did_open(server, "a.rel", BROKEN)
    messages = server.handle(
        notification("textDocument/didSave", {"textDocument": {"uri": uri("a.rel")}})
    )
    assert diagnostics(messages, "a.rel")


def test_did_close_clears_diagnostics_and_forgets_the_document() -> None:
    server = started()
    did_open(server, "a.rel", BROKEN)
    messages = server.handle(
        notification("textDocument/didClose", {"textDocument": {"uri": uri("a.rel")}})
    )
    assert published(messages, "a.rel") == {"uri": uri("a.rel"), "diagnostics": []}
    assert did_change(server, "a.rel", BROKEN, version=2) == []


def test_an_unrecognized_file_type_publishes_nothing_to_report() -> None:
    assert diagnostics(did_open(started(), "notes.txt", BROKEN), "notes.txt") == []


def test_a_ranged_change_is_ignored_since_only_full_sync_is_offered(
    caplog: pytest.LogCaptureFixture,
) -> None:
    server = started()
    did_open(server, "a.rel", CLIENT)
    change = {
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 1}},
        "text": "x",
    }
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        messages = server.handle(
            notification(
                "textDocument/didChange",
                {"textDocument": {"uri": uri("a.rel"), "version": 2}, "contentChanges": [change]},
            )
        )
    assert messages == []
    assert "ranged" in caplog.text


# ---------------------------------------------------------------------------
# Per-site cache
# ---------------------------------------------------------------------------

TWO_SITES = f"```relevance\n{UNKNOWN_INSPECTOR}\n```\n\n```relevance\n{BROKEN}\n```\n"


def test_an_unchanged_site_is_served_from_the_cache() -> None:
    server = started()
    did_open(server, "doc.md", TWO_SITES)
    assert server.linter.cache_stats().misses == 2
    did_change(server, "doc.md", TWO_SITES.replace(BROKEN, CLIENT), version=2)
    stats = server.linter.cache_stats()
    assert (stats.hits, stats.misses) == (1, 3)


def test_a_cached_site_that_moved_reports_its_new_line(tmp_path: Path) -> None:
    server = started()
    did_open(server, "doc.md", TWO_SITES)
    moved = "intro\n\n\n" + TWO_SITES
    found = diagnostics(did_change(server, "doc.md", moved, version=2), "doc.md")
    assert server.linter.cache_stats().misses == 2
    assert as_lint(found) == lint_expected(write(tmp_path, "doc.md", moved))


def test_the_same_statement_in_two_documents_keeps_each_documents_lines(tmp_path: Path) -> None:
    server = started()
    did_open(server, "a.md", TWO_SITES)
    shifted = "\n\n\n\n" + TWO_SITES
    found = diagnostics(did_open(server, "b.md", shifted), "b.md")
    assert server.linter.cache_stats().misses == 2
    assert as_lint(found) == lint_expected(write(tmp_path, "b.md", shifted))


def test_the_cache_is_bounded() -> None:
    server = Server(DocumentLinter(cache_size=2))
    initialize(server)
    for index in range(4):
        did_open(server, f"{index}.rel", f"{UNKNOWN_INSPECTOR} {index}")
    assert server.linter.cache_stats().size == 2


# ---------------------------------------------------------------------------
# Large-document guard
# ---------------------------------------------------------------------------


def test_the_default_limit_is_one_mebibyte() -> None:
    assert DEFAULT_MAX_DOCUMENT_BYTES == 1024 * 1024


def test_an_oversized_document_is_reported_not_linted() -> None:
    server = started(maxDocumentBytes=10)
    found = diagnostics(did_open(server, "big.rel", BROKEN), "big.rel")
    assert server.linter.cache_stats().misses == 0
    (diagnostic,) = found
    assert diagnostic["code"] == DOCUMENT_TOO_LARGE
    assert diagnostic["severity"] == 3
    assert diagnostic["source"] == SOURCE
    assert diagnostic["range"]["start"] == {"line": 0, "character": 0}
    assert str(len(BROKEN)) in diagnostic["message"]
    assert "maxDocumentBytes" in diagnostic["message"]


def test_the_limit_counts_utf8_bytes() -> None:
    text = f'"{E_ACUTE}" & ' + BROKEN  # one character, two bytes
    assert len(text.encode()) == len(text) + 1
    exact = len(text.encode())
    found = diagnostics(did_open(started(maxDocumentBytes=exact), "a.rel", text), "a.rel")
    assert DOCUMENT_TOO_LARGE not in {d["code"] for d in found}
    found = diagnostics(did_open(started(maxDocumentBytes=exact - 1), "a.rel", text), "a.rel")
    assert [d["code"] for d in found] == [DOCUMENT_TOO_LARGE]


@pytest.mark.parametrize("value", ["10", -1, True, 1.5, None])
def test_an_invalid_limit_keeps_the_default(
    value: object, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        server = started(maxDocumentBytes=value)
    assert server.linter.max_document_bytes == DEFAULT_MAX_DOCUMENT_BYTES
    assert "maxDocumentBytes" in caplog.text


# ---------------------------------------------------------------------------
# stdio transport
# ---------------------------------------------------------------------------


def frame(message: Message | bytes) -> bytes:
    body = message if isinstance(message, bytes) else json.dumps(message).encode()
    return b"Content-Length: %d\r\n\r\n" % len(body) + body


def unframe(data: bytes) -> list[Message]:
    stream = io.BytesIO(data)
    messages = []
    while (message := stdio.read_message(stream)) is not None:
        messages.append(message)
    return messages


def test_read_message_counts_bytes_not_characters_and_skips_other_headers() -> None:
    message = notification("x", {"text": E_ACUTE + "\U0001f600"})
    body = json.dumps(message, ensure_ascii=False).encode()
    data = b"Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n" + frame(body)
    stream = io.BytesIO(data + frame(message))
    assert stdio.read_message(stream) == message
    assert stdio.read_message(stream) == message
    assert stdio.read_message(stream) is None


def test_write_message_frames_with_the_byte_length() -> None:
    stream = io.BytesIO()
    message = notification("x", {"text": "e"})
    stdio.write_message(stream, message)
    assert unframe(stream.getvalue()) == [message]
    header, _, body = stream.getvalue().partition(b"\r\n\r\n")
    assert header == b"Content-Length: %d" % len(body)


def test_run_answers_until_exit_and_returns_the_exit_code() -> None:
    stdin = io.BytesIO(
        frame(request("initialize", {"capabilities": {}}, id_=1))
        + frame(request("shutdown", id_=2))
        + frame(notification("exit"))
        + frame(request("shutdown", id_=3))  # after exit: never read
    )
    stdout = io.BytesIO()
    assert stdio.run(Server(), stdin, stdout) == 0
    assert [message["id"] for message in unframe(stdout.getvalue())] == [1, 2]


def test_run_treats_end_of_input_as_an_unclean_exit() -> None:
    assert stdio.run(Server(), io.BytesIO(), io.BytesIO()) == 1


def test_run_answers_unparsable_json_with_a_parse_error_and_carries_on() -> None:
    stdin = io.BytesIO(frame(b"{not json") + frame(notification("exit")))
    stdout = io.BytesIO()
    assert stdio.run(Server(), stdin, stdout) == 1
    (response,) = unframe(stdout.getvalue())
    assert response["id"] is None
    assert response["error"]["code"] == -32700


@pytest.mark.parametrize("flags", [[], ["--stdio"]], ids=["bare", "--stdio"])
def test_the_server_runs_over_stdio_as_a_module(flags: list[str]) -> None:
    """``--stdio`` too: vscode-languageclient appends it for a stdio transport,
    as many clients do, and rejecting it killed the server in PoC 1."""
    document = {"uri": uri("a.rel"), "languageId": "x", "version": 1, "text": BROKEN}
    stdin = (
        frame(request("initialize", {"capabilities": {}}, id_=1))
        + frame(notification("initialized", {}))
        + frame(notification("textDocument/didOpen", {"textDocument": document}))
        + frame(request("shutdown", id_=2))
        + frame(notification("exit"))
    )
    result = subprocess.run(
        [sys.executable, "-m", "bigfix_relevance_analyzer.lsp", *flags],
        input=stdin,
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr.decode()
    messages = unframe(result.stdout)
    assert [message.get("id") for message in messages] == [1, None, 2]
    assert diagnostics(messages, "a.rel")


def test_read_message_refuses_a_negative_content_length() -> None:
    """``read(-1)`` reads to EOF: the server would swallow every later message."""
    with pytest.raises(ValueError, match="negative"):
        stdio.read_message(io.BytesIO(b"Content-Length: -1\r\n\r\n{}"))


def test_run_stops_on_a_negative_content_length() -> None:
    stdin = io.BytesIO(b"Content-Length: -1\r\n\r\n{}" + frame(notification("exit")))
    assert stdio.run(Server(), stdin, io.BytesIO()) == 1


@pytest.mark.parametrize("params", [[], [1], "x", 3])
def test_params_that_are_not_an_object_are_invalid(params: object) -> None:
    server = Server()
    (response,) = server.handle(
        {"jsonrpc": "2.0", "id": 5, "method": "initialize", "params": params}
    )
    assert response["id"] == 5
    assert response["error"]["code"] == -32602
    assert server.handle(notification("textDocument/didOpen", params)) == []
