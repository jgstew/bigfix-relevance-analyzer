"""The componentize-py app module for the ``lsp`` world in wit/lsp.wit.

The language server the "BigFix Relevance Developer" extension runs:
:class:`bigfix_relevance_analyzer.lsp.server.Server`, unchanged, behind three
string exports. server.js passes it one JSON-RPC message per call.

componentize-py runs this module's top level at *build* time and snapshots the
interpreter, so every import must happen here, at module top level. A module
first imported at runtime does not exist inside the component
(bytecodealliance/componentize-py#23), and neither does a codec first looked up
at runtime -- see ``_utf16_length`` in ``lsp/linter.py``. The imports below are
load-bearing for that reason. tests/test_vscode_component_app.py runs this file
on host CPython with a stand-in for ``wit_world``.
"""

import json

# BES XML extraction parses with expat. componentize-py's CPython ships pyexpat,
# and importing it here puts it in the snapshot.
import xml.parsers.expat  # noqa: F401

import wit_world

# `lint` imports `inspectors.suggest` inside a function, on the
# `unknown-inspector` path; this puts the module in the snapshot.
import bigfix_relevance_analyzer.inspectors  # noqa: F401
from bigfix_relevance_analyzer import __version__
from bigfix_relevance_analyzer.lsp.server import ErrorCode, Server, error_response

_server = Server()


class WitWorld(wit_world.WitWorld):
    """Implements the three exports of the `lsp` world."""

    def handle(self, message: str) -> str:
        try:
            parsed = json.loads(message)
        except ValueError as error:
            return json.dumps([error_response(None, ErrorCode.PARSE_ERROR, str(error))])
        # Server.handle never raises: a failing handler becomes an error response.
        return json.dumps(_server.handle(parsed))

    def exit_code(self) -> int | None:
        return _server.exit_code

    def version(self) -> str:
        return __version__
