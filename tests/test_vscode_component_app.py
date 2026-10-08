"""The componentize-py app module behind the primary VS Code extension.

``tools/vscode-extension/componentize-py/build-component/app.py`` is what
componentize-py compiles into the WebAssembly component the extension runs.
Building a component takes tens of seconds and a 15 MiB toolchain, so the
export logic is tested here on host CPython instead, with a stand-in for the
``wit_world`` bindings module. What only a real component can prove (that its
build snapshot holds every import and codec) is ``build_component.py``'s own
smoke check, and the shared VS Code smoke test's job.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from _helpers import BROKEN

from bigfix_relevance_analyzer import __version__

APP = (
    Path(__file__).resolve().parent.parent
    / "tools/vscode-extension/componentize-py/build-component/app.py"
)


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """A fresh instance of the app's ``WitWorld``, with its own server state."""
    bindings = types.ModuleType("wit_world")
    bindings.WitWorld = object  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "wit_world", bindings)
    spec = importlib.util.spec_from_file_location("_vscode_component_app", APP)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module.WitWorld()


def call(app: Any, message: dict[str, Any]) -> list[dict[str, Any]]:
    replies: list[dict[str, Any]] = json.loads(app.handle(json.dumps(message)))
    return replies


def initialize(app: Any) -> list[dict[str, Any]]:
    return call(app, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})


def test_handle_is_json_in_and_a_json_array_out(app: Any) -> None:
    (response,) = initialize(app)
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["version"] == __version__


def test_diagnostics_come_back_as_notifications(app: Any) -> None:
    initialize(app)
    document = {"uri": "file:///w/a.rel", "languageId": "x", "version": 1, "text": BROKEN}
    (published,) = call(
        app,
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": document},
        },
    )
    assert published["method"] == "textDocument/publishDiagnostics"
    assert published["params"]["diagnostics"]


def test_unparsable_json_is_a_parse_error_not_an_exception(app: Any) -> None:
    (response,) = json.loads(app.handle("{not json"))
    assert response["id"] is None
    assert response["error"]["code"] == -32700


def test_exit_code_is_none_until_exit(app: Any) -> None:
    initialize(app)
    assert app.exit_code() is None
    call(app, {"jsonrpc": "2.0", "id": 2, "method": "shutdown"})
    assert app.exit_code() is None
    call(app, {"jsonrpc": "2.0", "method": "exit"})
    assert app.exit_code() == 0


def test_exit_without_shutdown_is_one(app: Any) -> None:
    initialize(app)
    call(app, {"jsonrpc": "2.0", "method": "exit"})
    assert app.exit_code() == 1


def test_version_is_the_packages(app: Any) -> None:
    assert app.version() == __version__
