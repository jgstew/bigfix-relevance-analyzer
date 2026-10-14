"""The playground's language server: ``lsp.Server`` behind two string functions.

Shared by both playground runtimes, so they run the same code:

* componentize-py: ``componentize.py`` stages this file beside ``app.py``,
  which imports it and exports ``handle`` and ``exit_code`` through the
  ``analyzer`` world (``wit/analyzer.wit``);
* Pyodide: ``build_playground.py`` embeds it, and the page writes it into
  Pyodide's filesystem and imports it.

The same shape as the VS Code extension's component
(``tools/vscode-extension/componentize-py/build-component/app.py``): one
JSON-RPC message in, a JSON array of the messages to send back out. JSON is
dumped here rather than in JavaScript so the two pages' replies compare as
strings (``../parity-test/``).

Every import is at module top level: componentize-py snapshots the interpreter
at build time, and a module first imported at runtime does not exist inside the
component.
"""

import json

from bigfix_relevance_analyzer.lsp.server import ErrorCode, Server, error_response

_server = Server()


def handle(message: str) -> str:
    """One JSON-RPC message in; the JSON array of the replies out. Never raises."""
    try:
        parsed = json.loads(message)
    except ValueError as error:
        return json.dumps([error_response(None, ErrorCode.PARSE_ERROR, str(error))])
    # Server.handle never raises: a failing handler becomes an error response.
    return json.dumps(_server.handle(parsed))


def exit_code() -> int | None:
    """None until the client sends ``exit``; then 0 if ``shutdown`` came first, else 1."""
    return _server.exit_code
