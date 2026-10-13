"""Tests for :class:`~bigfix_relevance_analyzer.lsp.session.StatementSession` (#142).

The way to embed the language server without a language client: one statement,
owned by the caller, held in an in-process :class:`~bigfix_relevance_analyzer.lsp.Server`.
Ported from bigfix-relevance-debugger, where it was prototyped against this
library's public API (jgstew/bigfix-relevance-debugger#20, #21). Every test
runs the real server in-process; nothing touches a socket or a file.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from _helpers import run_fresh_python

from bigfix_relevance_analyzer import Dialect, LintConfig
from bigfix_relevance_analyzer import lsp as lsp_package
from bigfix_relevance_analyzer.lsp import DocumentLinter, LspError, Server, StatementSession

SETTING = 'exists values of setting "x" of client'


def at(line: int, character: int) -> dict[str, int]:
    return {"line": line, "character": character}


def span(start: tuple[int, int], end: tuple[int, int]) -> dict[str, dict[str, int]]:
    return {"start": at(*start), "end": at(*end)}


@pytest.fixture
def session() -> Iterator[StatementSession]:
    s = StatementSession()
    yield s
    s.close()


# --- the package's API ------------------------------------------------------------


def test_the_session_and_its_error_are_exported() -> None:
    assert {"StatementSession", "LspError"} <= set(lsp_package.__all__)
    assert StatementSession.__module__ == "bigfix_relevance_analyzer.lsp.session"
    assert issubclass(LspError, Exception)


def test_importing_the_package_still_loads_neither_server_nor_session() -> None:
    """A protocol layer that wants only the linter pays for neither."""
    run_fresh_python(
        "import sys\n"
        "import bigfix_relevance_analyzer.lsp\n"
        "for name in ('bigfix_relevance_analyzer.lsp.server',"
        " 'bigfix_relevance_analyzer.lsp.session'):\n"
        "    assert name not in sys.modules, name\n"
        "from bigfix_relevance_analyzer.lsp import StatementSession, LspError\n"
        "assert 'bigfix_relevance_analyzer.lsp.server' in sys.modules\n"
        "print('ok')\n"
    )


def test_importing_the_session_brings_everything_a_wasm_snapshot_needs() -> None:
    """componentize-py keeps only what is imported at build time: importing the
    session module must import the server it drives, at module level."""
    run_fresh_python(
        "import sys\n"
        "import bigfix_relevance_analyzer.lsp.session\n"
        "for name in ('bigfix_relevance_analyzer.lsp.server',"
        " 'bigfix_relevance_analyzer.lsp.linter',"
        " 'bigfix_relevance_analyzer.completion.rank'):\n"
        "    assert name in sys.modules, name\n"
        "print('ok')\n"
    )


def test_a_session_needs_no_codec_beyond_utf8() -> None:
    """The playground's component has no UTF-16 codec: see test_lsp's twins."""
    run_fresh_python(
        """
import sys
for name in ("encodings.utf_16", "encodings.utf_16_le", "encodings.utf_16_be"):
    sys.modules[name] = None
from bigfix_relevance_analyzer.lsp.session import StatementSession
session = StatementSession()
text = '"\\U0001f600" & nme of operating system'
(found,) = session.sync(text)
assert found["range"]["start"]["character"] == text.index("nme") + 1, found
hover = session.request("textDocument/hover", {"position": {"line": 0, "character": 26}}, text)
assert "operating system" in hover["contents"]["value"], hover
session.close()
print("ok")
"""
    )


# --- diagnostics ------------------------------------------------------------------


def test_first_sync_publishes_diagnostics(session: StatementSession) -> None:
    diagnostics = session.sync("nme of operating system")

    assert diagnostics is not None
    [diagnostic] = diagnostics
    assert diagnostic["code"] == "unknown-inspector"
    assert diagnostic["range"] == span((0, 0), (0, 3))
    assert session.version == 1


def test_unchanged_text_sends_nothing(session: StatementSession) -> None:
    session.sync("name of operating system")

    assert session.sync("name of operating system") is None
    assert session.version == 1


def test_changed_text_publishes_again(session: StatementSession) -> None:
    session.sync("nme of operating system")

    assert session.sync("name of operating system") == []
    assert session.version == 2


def test_clean_text_has_no_diagnostics(session: StatementSession) -> None:
    assert session.sync("name of operating system") == []


def test_the_returned_list_is_the_callers_own(session: StatementSession) -> None:
    returned = session.sync("nme of operating system")
    assert returned is not None
    returned.clear()
    assert [d["code"] for d in session.diagnostics] == ["unknown-inspector"]


# --- requests ---------------------------------------------------------------------


def test_completion_after_of(session: StatementSession) -> None:
    result = session.request("textDocument/completion", {"position": at(0, 8)}, "name of ")

    assert "operating system" in [item["label"] for item in result["items"]]


def test_a_request_syncs_its_text_first(session: StatementSession) -> None:
    session.sync("nme")

    result = session.request("textDocument/completion", {"position": at(1, 8)}, "\nname of ")

    assert session.version == 2
    assert "operating system" in [item["label"] for item in result["items"]]


def test_completion_inserts_plain_text(session: StatementSession) -> None:
    """The session advertises no snippet support: no `$1` placeholders."""
    result = session.request("textDocument/completion", {"position": at(0, 13)}, "names of fold")
    assert result["items"]
    assert all("insertTextFormat" not in item for item in result["items"])


def test_hover_describes_the_inspector(session: StatementSession) -> None:
    result = session.request(
        "textDocument/hover", {"position": at(0, 12)}, "name of operating system"
    )

    assert "operating system" in result["contents"]["value"]
    assert result["range"] == span((0, 8), (0, 24))


def test_hover_on_nothing_is_none(session: StatementSession) -> None:
    assert session.request("textDocument/hover", {"position": at(0, 4)}, "name of x") is None


def test_quick_fix_edits_the_statement(session: StatementSession) -> None:
    actions = session.request(
        "textDocument/codeAction",
        {"range": span((0, 20), (0, 20)), "context": {"diagnostics": []}},
        SETTING,
    )

    [quick] = [a for a in actions if a["kind"] == "quickfix"]
    assert quick["title"] == "Change `setting` to `settings`"
    # A minimal edit: `setting` becomes `settings` by inserting the `s`.
    [edit] = quick["edit"]["changes"][StatementSession.URI]
    assert edit == {"range": span((0, 24), (0, 24)), "newText": "s"}


def test_fix_all_is_offered(session: StatementSession) -> None:
    actions = session.request(
        "textDocument/codeAction",
        {
            "range": span((0, 0), (0, 0)),
            "context": {"diagnostics": [], "only": ["source.fixAll.bigfix-relevance"]},
        },
        SETTING,
    )

    assert [a["kind"] for a in actions] == ["source.fixAll.bigfix-relevance"]


def test_only_quickfix_leaves_out_fix_all(session: StatementSession) -> None:
    # A client listing the fixes for one problem asks for just those.
    actions = session.request(
        "textDocument/codeAction",
        {"range": span((0, 20), (0, 20)), "context": {"diagnostics": [], "only": ["quickfix"]}},
        SETTING,
    )

    assert [a["kind"] for a in actions] == ["quickfix"]


def test_the_request_names_the_document_whatever_params_say(session: StatementSession) -> None:
    """``textDocument`` is the session's to fill in: a caller's is replaced."""
    result = session.request(
        "textDocument/hover",
        {"position": at(0, 12), "textDocument": {"uri": "file:///elsewhere.rel"}},
        "name of operating system",
    )
    assert result is not None


def test_did_you_mean_comes_through_as_data_and_replacements(session: StatementSession) -> None:
    """#142 S1 through the session: each unknown name's leads as diagnostic
    data, and a "Replace" quick fix per lead, as the browser client asks."""
    text = "exists oprating system"
    (diagnostic,) = session.sync(text) or []
    leads = diagnostic["data"]["suggestions"]
    assert leads[0] == "operating system"
    actions = session.request(
        "textDocument/codeAction",
        {
            "range": diagnostic["range"],
            "context": {"diagnostics": [diagnostic], "only": ["quickfix"]},
        },
        text,
    )
    assert [a["title"] for a in actions] == [
        f"Replace `oprating system` with `{lead}`" for lead in leads
    ]
    [edit] = actions[0]["edit"]["changes"][StatementSession.URI]
    assert edit == {"range": span((0, 7), (0, 22)), "newText": "operating system"}


def test_an_error_response_raises(session: StatementSession) -> None:
    with pytest.raises(LspError) as raised:
        session.request("textDocument/nonsense", {}, "now")

    assert raised.value.code == -32601
    assert "textDocument/nonsense" in str(raised.value)
    assert raised.value.message in str(raised.value)


# --- dialect ----------------------------------------------------------------------


def hover_text(session: StatementSession, text: str, character: int) -> str:
    result: dict[str, Any] = session.request(
        "textDocument/hover", {"position": at(0, character)}, text
    )
    value: str = result["contents"]["value"]
    return value


def test_dialect_defaults_to_whatever_the_statement_says() -> None:
    # `computer` alone is a client inspector (macOS) and a session one; an
    # undecided statement is analysed as client relevance.
    session = StatementSession()

    assert session.dialect is None
    assert "session" not in hover_text(session, "name of computer", 10)


def test_a_forced_dialect_reaches_the_server() -> None:
    session = StatementSession(dialect=Dialect.SESSION)

    assert session.dialect is Dialect.SESSION
    assert "session" in hover_text(session, "name of computer", 10)


def test_a_server_forced_to_a_dialect_by_its_linter() -> None:
    """#142 S3: the supported way to force an embedded server's dialect, which
    the session builds on. Pinned at the Server, without the session."""
    server = Server(linter=DocumentLinter(config=LintConfig(suggest=True, dialect=Dialect.SESSION)))
    server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    server.handle({"jsonrpc": "2.0", "method": "initialized", "params": {}})
    uri = "untitled:Untitled-1"
    document = {"uri": uri, "languageId": "bigfix-relevance", "version": 1}
    server.handle(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": {**document, "text": "name of computer"}},
        }
    )
    (reply,) = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "textDocument/hover",
            "params": {"textDocument": {"uri": uri}, "position": at(0, 10)},
        }
    )
    assert "session" in reply["result"]["contents"]["value"]


# --- lifecycle --------------------------------------------------------------------


def test_closed_session_refuses_work() -> None:
    session = StatementSession()
    session.sync("now")

    session.close()
    session.close()  # idempotent

    with pytest.raises(RuntimeError, match="closed"):
        session.sync("now")
    with pytest.raises(RuntimeError, match="closed"):
        session.request("textDocument/hover", {"position": at(0, 0)}, "now")


def test_a_session_never_synced_closes_too() -> None:
    session = StatementSession()
    session.close()
    session.close()


# --- the latest diagnostics -------------------------------------------------------


def test_diagnostics_start_empty(session: StatementSession) -> None:
    assert session.diagnostics == []
    assert session.version == 0


def test_diagnostics_are_kept_for_the_text_the_server_holds(session: StatementSession) -> None:
    session.sync("nme of operating system")

    assert session.sync("nme of operating system") is None  # nothing new to report...
    [diagnostic] = session.diagnostics  # ...but the latest are still at hand
    assert diagnostic["code"] == "unknown-inspector"


def test_a_requests_sync_keeps_its_diagnostics(session: StatementSession) -> None:
    # request() syncs first; a caller that publishes afterwards must still be
    # able to get that text's diagnostics.
    session.request("textDocument/hover", {"position": at(0, 1)}, "nme of operating system")

    assert [d["code"] for d in session.diagnostics] == ["unknown-inspector"]
