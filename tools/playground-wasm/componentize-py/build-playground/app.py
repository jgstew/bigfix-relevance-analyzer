"""The componentize-py app module for the ``analyzer`` world in wit/analyzer.wit.

componentize-py runs this module's top level at *build* time, inside the
component's own CPython, and snapshots the resulting interpreter heap into the
wasm. Two consequences shape everything below:

* **Every import must happen here, at module top level.** An import first
  reached at runtime fails, because there is no filesystem left to import from
  (bytecodealliance/componentize-py#23). None of the imports below are
  tidy-able; each one is load-bearing.
* **Anything printed here appears during the build, not at runtime.** The
  diagnostic at the bottom is deliberate: it is the only place the build can
  tell you which CPython-for-WASI it actually got.

The implementing class must be named exactly ``WitWorld``. componentize-py looks
up ``<app module>.<protocol name>``, and the generated protocol is named for the
bindings *module* (``wit_world``), not for the WIT world -- which is also why
this file is ``app.py`` and the bindings land in ``wit_world/``: the app module
may not share a name with the world it targets.
"""

import json
import sys
import types

# `bigfix_relevance_analyzer.__init__` imports `extract`, which imports
# `xml.parsers.expat` (pyexpat, a C extension) at top level. componentize-py
# 0.25.0's embedded CPython 3.14 does ship pyexpat, so the `try` below is what
# normally runs -- but componentize-py's build.rs only explicitly enables
# _sqlite3 and says nothing about pyexpat, so that is a property of the build,
# not a promise. The fallback keeps a future build that drops pyexpat from
# taking the whole package down with it.
#
# Nothing the playground calls needs expat: it analyzes one pasted statement,
# and only `extract`'s BES-XML path parses XML. Every use in extract.py is
# attribute-qualified (`xml.parsers.expat.ParserCreate`, `.ExpatError`), so a
# module object carrying those two names satisfies both the import and the
# `except xml.parsers.expat.ExpatError` clause.
#
# If file upload ever lands, this stub stops being acceptable -- extraction
# would then be on the hot path and would need either real pyexpat or a
# pure-Python fallback in extract.py.
try:
    import xml.parsers.expat

    _EXPAT = "real"
except ImportError:  # pragma: no cover - only in a WASI build without pyexpat
    import xml.parsers

    _stub = types.ModuleType("xml.parsers.expat")
    _stub.ExpatError = type("ExpatError", (Exception,), {})

    def _no_expat(*_args, **_kwargs):
        raise RuntimeError("this build has no pyexpat; BES XML extraction is unavailable here")

    _stub.ParserCreate = _no_expat
    sys.modules["xml.parsers.expat"] = _stub
    xml.parsers.expat = _stub
    _EXPAT = "stub"

import wit_world

# Covers the function-local import at lint.py:804, which the build-time snapshot
# would otherwise miss and which analyze_to_dict can reach. `reference` is
# deliberately left out: __init__.py:92-95 keeps it off the import path on
# purpose, only __main__ reaches it, and it is the one submodule measured in
# kilobytes of text -- there is no reason to pay for it in the wasm.
import bigfix_relevance_analyzer.inspectors  # noqa: F401
from bigfix_relevance_analyzer import __version__, analyze_relevance_to_dict

# Build-time diagnostic, on stderr so it cannot be mistaken for component
# output. `expat=stub` is the one line worth noticing here -- see above.
print(f"componentize-py build: expat={_EXPAT} analyzer={__version__}", file=sys.stderr)


class WitWorld(wit_world.WitWorld):
    """Implements the two exports of the `analyzer` world."""

    def analyze(self, text: str) -> str:
        # json.dumps here rather than in JS on purpose: the Pyodide page does
        # exactly the same, so the two pages' outputs are comparable as strings.
        # analyze_relevance_to_dict never raises for bad relevance -- a parse
        # failure comes back as data in the payload.
        return json.dumps(analyze_relevance_to_dict(text))

    def version(self) -> str:
        # Resolved through importlib.metadata in the package's __init__, which
        # means it depends on the wheel's .dist-info surviving into the
        # component. It does -- componentize-py carries non-.py files from
        # --python-path -- and the smoke test asserts this is not "0.0.0".
        return __version__
