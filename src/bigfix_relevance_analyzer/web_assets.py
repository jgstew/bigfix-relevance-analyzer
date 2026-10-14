"""The browser editor files the wheel ships, described for their hosts (#159).

``web/`` holds JavaScript only: ``relevance_editor.js`` (the CodeMirror 6
client) and ``relevance_language.js`` (the highlighter). Each imports nothing;
the page passes its own CodeMirror namespace, and each module checks up front
that the namespace has every name in its ``REQUIRED_CM`` list. A host bringing
its own bundle (NiceGUI's, say) checks the same names here, as data, instead of
parsing them out of the JavaScript::

    from bigfix_relevance_analyzer.web_assets import REQUIRED_CM, web_dir

    my_bundle_exports: set[str] = ...  # what the host's CodeMirror bundle exports
    missing = {n for names in REQUIRED_CM.values() for n in names} - my_bundle_exports
    client = web_dir() / "relevance_editor.js"

The JavaScript stays the source of truth: ``tests/test_web_assets.py`` holds
these lists equal to each file's ``export const REQUIRED_CM``.

Not imported by the package ``__init__``: only editor hosts need it.
"""

from __future__ import annotations

from collections.abc import Mapping
from importlib.resources import files
from importlib.resources.abc import Traversable
from types import MappingProxyType
from typing import Final

__all__ = ["REQUIRED_CM", "WEB_MODULES", "web_dir"]

WEB_MODULES: Final[tuple[str, ...]] = ("relevance_editor.js", "relevance_language.js")
"""Every file in ``web/``, by name."""

REQUIRED_CM: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "relevance_editor.js": (
            "Decoration",
            "EditorState",
            "EditorView",
            "GutterMarker",
            "Prec",
            "RangeSetBuilder",
            "StateEffect",
            "StateField",
            "ViewPlugin",
            "closeHoverTooltips",
            "gutter",
            "hoverTooltip",
            "keymap",
            "showTooltip",
        ),
        "relevance_language.js": ("StreamLanguage",),
    }
)
"""The CodeMirror names each module in ``WEB_MODULES`` takes from the page's
namespace, sorted: what a host's bundle must export. Read-only; serialize
``dict(REQUIRED_CM)``, since a ``MappingProxyType`` neither JSON-dumps nor
pickles."""


def web_dir() -> Traversable:
    """``web/`` in the installed package: ``files("bigfix_relevance_analyzer") / "web"``."""
    return files("bigfix_relevance_analyzer") / "web"
