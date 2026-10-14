"""The playground's language server: one shim, two runtimes (#142 H1).

``tools/playground-wasm/common/lsp_shim.py`` wraps one module-level
``lsp.Server`` in two string functions, ``handle`` and ``exit_code``, exactly as
the VS Code extension's component does. Both playground runtimes use that one
file: the componentize-py ``app.py`` imports it (``componentize.py`` stages it
beside the app) and exports it through the ``analyzer`` world, and the Pyodide
page writes it into Pyodide's filesystem and imports it. So the parity test
compares two runtimes, not two copies of the shim.

Tested here on host CPython, with a stand-in for the ``wit_world`` bindings,
like ``test_vscode_component_app.py``; what only a real component proves is
the smoke and parity stages' job.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import types
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from _helpers import BROKEN, REPO_ROOT, load_tool, run_fresh_python

from bigfix_relevance_analyzer import __version__

PLAYGROUND = REPO_ROOT / "tools" / "playground-wasm"
COMMON = PLAYGROUND / "common"
SHIM = COMMON / "lsp_shim.py"
BUILD = PLAYGROUND / "componentize-py" / "build-playground"
APP = BUILD / "app.py"
WIT = BUILD / "wit" / "analyzer.wit"
COMPONENTIZE = BUILD / "componentize.py"
PYODIDE_BUILD = PLAYGROUND / "pyodide" / "build-playground"
VSCODE_BUILD = REPO_ROOT / "tools/vscode-extension/componentize-py/build-component"


def _load(path: Path, name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def shim(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """A fresh shim module (its own server state), importable as ``lsp_shim``."""
    module = _load(SHIM, "lsp_shim")
    monkeypatch.setitem(sys.modules, "lsp_shim", module)
    yield module


@pytest.fixture
def app(shim: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    bindings = types.ModuleType("wit_world")
    bindings.WitWorld = object  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "wit_world", bindings)
    yield _load(APP, "_playground_component_app").WitWorld()


@pytest.fixture(params=["shim", "app"])
def server(request: pytest.FixtureRequest) -> Any:
    """The same exports, called through the shim and through the component's app."""
    target = request.getfixturevalue(request.param)
    return types.SimpleNamespace(handle=target.handle, exit_code=target.exit_code)


def call(server: Any, message: dict[str, Any]) -> list[dict[str, Any]]:
    text = server.handle(json.dumps(message))
    assert isinstance(text, str)
    replies: list[dict[str, Any]] = json.loads(text)
    return replies


def did_open(document: dict[str, Any]) -> dict[str, Any]:
    params = {"textDocument": document}
    return {"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": params}


def initialize(server: Any) -> dict[str, Any]:
    (response,) = call(server, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    return response


def test_handle_is_json_in_and_a_json_array_out(server: Any) -> None:
    response = initialize(server)
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["version"] == __version__
    assert response["result"]["capabilities"]["hoverProvider"]


def test_diagnostics_come_back_as_notifications(server: Any) -> None:
    initialize(server)
    document = {
        "uri": "untitled:statement",
        "languageId": "bigfix-relevance",
        "version": 1,
        "text": BROKEN,
    }
    (published,) = call(server, did_open(document))
    assert published["method"] == "textDocument/publishDiagnostics"
    assert published["params"]["version"] == 1
    assert published["params"]["diagnostics"]


def test_hover_answers_for_an_open_statement(server: Any) -> None:
    initialize(server)
    document = {
        "uri": "untitled:statement",
        "languageId": "bigfix-relevance",
        "version": 1,
        "text": "name of operating system",
    }
    call(server, did_open(document))
    where = {"line": 0, "character": 12}
    params = {"textDocument": {"uri": "untitled:statement"}, "position": where}
    hover = {"jsonrpc": "2.0", "id": 2, "method": "textDocument/hover", "params": params}
    (response,) = call(server, hover)
    assert "operating system" in json.dumps(response["result"])


def test_unparsable_json_is_a_parse_error_not_an_exception(server: Any) -> None:
    (response,) = json.loads(server.handle("{not json"))
    assert response["id"] is None
    assert response["error"]["code"] == -32700


def test_a_message_nested_too_deep_to_parse_is_an_error_reply(server: Any) -> None:
    """json.loads raises RecursionError, not ValueError, past the recursion limit."""
    depth = sys.getrecursionlimit() * 10
    (response,) = json.loads(server.handle("[" * depth + "]" * depth))
    assert response["id"] is None
    assert response["error"]["code"] == -32700


def test_exit_code_is_none_until_exit(server: Any) -> None:
    initialize(server)
    assert server.exit_code() is None
    call(server, {"jsonrpc": "2.0", "id": 2, "method": "shutdown"})
    assert server.exit_code() is None
    call(server, {"jsonrpc": "2.0", "method": "exit"})
    assert server.exit_code() == 0


def test_exit_without_shutdown_is_one(server: Any) -> None:
    initialize(server)
    call(server, {"jsonrpc": "2.0", "method": "exit"})
    assert server.exit_code() == 1


def test_the_app_keeps_analyze_and_version(app: Any) -> None:
    payload = json.loads(app.analyze("name of operating system"))
    assert payload["parse"]["ok"] is True
    assert app.version() == __version__


def test_the_world_exports_handle_and_exit_code_beside_analyze() -> None:
    text = WIT.read_text(encoding="utf-8")
    assert "export analyze: func(text: string) -> string;" in text
    assert "export version: func() -> string;" in text
    assert "export handle: func(message: string) -> string;" in text
    assert "export exit-code: func() -> option<s32>;" in text


def test_the_app_and_the_pyodide_page_use_the_one_shim() -> None:
    assert "import lsp_shim" in APP.read_text(encoding="utf-8")
    assert "Server(" not in APP.read_text(encoding="utf-8")
    template = (PYODIDE_BUILD / "template.html").read_text(encoding="utf-8")
    assert "%%LSP_SHIM_PY_BASE64%%" in template
    assert 'pyimport("lsp_shim")' in template
    module = load_tool(PYODIDE_BUILD / "build_playground.py", "_pyodide_build_playground_h1")
    assert module.LSP_SHIM == SHIM
    copies = [p for p in PLAYGROUND.rglob("lsp_shim.py") if "node_modules" not in p.parts]
    assert copies == [SHIM]


def test_componentize_stages_the_shim_beside_the_app_and_nothing_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_tool(COMPONENTIZE, "_componentize_py_componentize_h1")
    parameters = inspect.signature(module.componentize).parameters
    assert parameters["extra_modules"].default == (SHIM,)
    staged: list[str] = []

    def fake_run(argv: list[str], label: str) -> None:
        if argv[:2] == ["uv", "pip"]:
            (tmp_path / "deps" / "__pycache__").mkdir(parents=True)
        elif "componentize" in argv:
            staged[:] = sorted(p.name for p in (tmp_path / "app").iterdir())
            Path(argv[-1]).write_bytes(b"\0asm")

    monkeypatch.setattr(module, "_run", fake_run)
    module.componentize(tmp_path / "x.whl", tmp_path)
    assert staged == ["app.py", "lsp_shim.py"]


def test_the_vscode_component_stages_no_shim() -> None:
    """Its own app.py wraps its own Server; the playground's shim is not its."""
    text = (VSCODE_BUILD / "build_component.py").read_text(encoding="utf-8")
    assert "extra_modules=()" in text


def test_the_shim_needs_no_codec_beyond_utf8() -> None:
    """It runs inside the component, which has no UTF-16 codec."""
    run_fresh_python(
        f"""
import json, sys
for name in ("encodings.utf_16", "encodings.utf_16_le", "encodings.utf_16_be"):
    sys.modules[name] = None
sys.path.insert(0, {str(COMMON)!r})
import lsp_shim
def call(message):
    return json.loads(lsp_shim.handle(json.dumps(message)))
call({{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {{}}}})
doc = {{"uri": "untitled:s", "languageId": "bigfix-relevance", "version": 1,
        "text": "nme of oprating system \\U0001F600"}}
(published,) = call({{"jsonrpc": "2.0", "method": "textDocument/didOpen",
                      "params": {{"textDocument": doc}}}})
assert published["params"]["diagnostics"], published
where = {{"textDocument": {{"uri": "untitled:s"}}, "position": {{"line": 0, "character": 8}}}}
call({{"jsonrpc": "2.0", "id": 2, "method": "textDocument/hover", "params": where}})
call({{"jsonrpc": "2.0", "id": 3, "method": "textDocument/completion", "params": where}})
print("ok")
"""
    )
