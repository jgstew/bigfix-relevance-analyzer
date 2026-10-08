"""Everything an editor needs from the analyzer, with no protocol in it.

:class:`DocumentLinter` takes a document -- its URI and the buffer's text --
and returns its diagnostics as plain dicts in LSP's own field names. It knows
nothing of JSON-RPC, message dispatch or document sync. Those belong to the
protocol layer on top: today the hand-rolled
:class:`~bigfix_relevance_analyzer.lsp.server.Server`, later perhaps a pygls
server (issue 10 has the spike). Either is a thin adapter over this object, so
swapping one for the other leaves this module, and its tests, untouched. Nothing
here imports the protocol layer; a test holds that line.

What a document is linted as
----------------------------
Exactly what :func:`~bigfix_relevance_analyzer.lint.lint_file` would report for
the same content, through the same extractors and rules, but over the editor's
buffer rather than the file on disk. The file type comes from the URI's suffix.
A document whose suffix no extractor reads has no diagnostics.

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
the linter keeps each site's findings, keyed by everything about the site but
its position, and moves them to the site's current line on a hit. That is
editor state on purpose: a library cache would be overhead for a pre-commit
hook, which never sees the same document twice.

The large-document guard
------------------------
Linting is synchronous, and a server that blocks for seconds on open is a hung
editor. Real content has one 13 MB generated task with 24,240 sites that takes
about 19 s to lint; every other file in the same corpus is under 410 KB. A
document over :data:`DEFAULT_MAX_DOCUMENT_BYTES` (UTF-8) gets one informational
:data:`DOCUMENT_TOO_LARGE` diagnostic instead of findings. The limit is the
``maxDocumentBytes`` initialization option. That code is the editor
integration's, not a lint rule: it says the document was not judged, never that
it is wrong.

Runs in WASM
------------
This is the code an editor extension runs inside a componentize-py component,
which has only the modules and codecs its build snapshot saw. Hence UTF-8 only,
and UTF-16 lengths counted rather than encoded -- see :func:`_utf16_length`.
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

# Underscore-private on purpose: this package's modules share extract's
# helpers this way (lint.py imports _extract_data and _is_recognized too).
from bigfix_relevance_analyzer.extract import (
    _UNTYPED_TEXT_SUFFIXES,
    RelevanceSite,
    _is_recognized,
)
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    _judge_site,
    _lint_data,
)

logger = logging.getLogger(__name__)

Diagnostic = dict[str, Any]
"""An LSP ``Diagnostic`` as plain JSON-serializable data."""

SOURCE: Final = "bigfix-relevance-analyzer"
"""The ``source`` on every diagnostic, and the server's name in ``serverInfo``."""

DEFAULT_MAX_DOCUMENT_BYTES: Final = 1024 * 1024
"""Documents larger than this, in UTF-8 bytes, are not linted. See the module docstring."""

DOCUMENT_TOO_LARGE: Final = "document-too-large"
"""The code of the one diagnostic an oversized document gets."""

LANGUAGE_ID: Final = "bigfix-relevance"
"""The VS Code language id for whole-file relevance (``.rel``, ``.bsr``).

A buffer whose URI names no recognized file type is still linted, as a single
relevance statement, when the client says it is this language: an unsaved
``untitled:`` buffer, or a file switched to it by hand. The extension
contributes the language under this id; a test keeps the two equal."""

DEFAULT_CACHE_SIZE: Final = 2048
"""Sites whose findings the linter keeps -- as many as lint keeps analyses."""

_LINE_BREAK: Final = re.compile(r"\r\n|\r|\n")
"""What LSP counts as a line break -- only these, unlike :meth:`str.splitlines`,
which also breaks on form feeds and Unicode separators a client does not."""


class _DiagnosticSeverity(enum.IntEnum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3


_SEVERITIES: Final = {
    Severity.ERROR: _DiagnosticSeverity.ERROR,
    Severity.WARNING: _DiagnosticSeverity.WARNING,
}


class CacheStats(NamedTuple):
    """How the per-site cache has done since the linter was created."""

    hits: int
    misses: int
    size: int


class DocumentLinter:
    """Diagnostics for editor documents, with a per-site cache and a size guard.

    One per editor session: the cache is only worth having across the edits of
    one session's documents.
    """

    def __init__(
        self,
        *,
        config: LintConfig | None = None,
        max_document_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ) -> None:
        self.config = config if config is not None else LintConfig(suggest=True)
        """What to lint with. ``suggest`` is on by default: lint recommends it
        for an interactive consumer, and the cache keeps its cost off keystrokes."""

        self.max_document_bytes = max_document_bytes
        self._cache: OrderedDict[RelevanceSite, tuple[Finding, ...]] = OrderedDict()
        self._cache_size = cache_size
        self._hits = 0
        self._misses = 0

    def apply_options(self, options: object) -> None:
        """Take what applies from a client's ``initializationOptions``.

        Only ``maxDocumentBytes`` so far. Anything unusable is logged and
        ignored rather than refused, so a misconfigured client still gets
        diagnostics, under the defaults.
        """
        if options is None:
            return
        if not isinstance(options, Mapping):
            logger.warning("ignoring initialization options %r: not an object", options)
            return
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

    def cache_stats(self) -> CacheStats:
        return CacheStats(self._hits, self._misses, len(self._cache))

    def diagnostics(self, uri: str, text: str, language_id: str | None = None) -> list[Diagnostic]:
        """The diagnostics to publish for the document at ``uri`` holding ``text``.

        The file type comes from the URI's suffix. Only when that names nothing
        the extractor reads does ``language_id`` (the client's ``languageId``)
        decide: :data:`LANGUAGE_ID` means whole-file relevance. A ``.md`` stays
        markdown whatever the client calls it.
        """
        data = text.encode("utf-8", errors="surrogatepass")
        if len(data) > self.max_document_bytes:
            message = (
                f"not linted: {len(data)} bytes is over the {self.max_document_bytes}-byte "
                "limit (maxDocumentBytes)"
            )
            # Only line 0 is needed, and the guard is there so that a document
            # this size is never processed whole, so no full split.
            first = text[: next((i for i, c in enumerate(text) if c in "\r\n"), len(text))]
            return [
                _diagnostic(
                    [first], 0, _DiagnosticSeverity.INFORMATION, DOCUMENT_TOO_LARGE, message
                )
            ]
        findings = _lint_data(_document_path(uri, language_id), data, self.config, self._judge)
        if not findings:
            return []
        lines = _LINE_BREAK.split(text)
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


def _document_path(uri: str, language_id: str | None) -> Path:
    """The path whose suffix picks the extractor for this document."""
    path = _path_of(uri)
    if language_id == LANGUAGE_ID and not _is_recognized(path):
        # Plain relevance, the same as a `.rel` file: dialect from the content.
        (untyped,) = _UNTYPED_TEXT_SUFFIXES
        return path.with_name(f"{path.name}{untyped}")
    return path


def _utf16_length(line: str) -> int:
    """``line``'s length in UTF-16 code units: two for an astral character.

    Counted rather than encoded on purpose. A WASM host has only the codecs its
    build snapshot saw, and ``str.encode("utf-16-le")`` raised ``LookupError``
    inside a componentize-py component, losing every diagnostic.
    """
    return len(line) + sum(1 for char in line if ord(char) > 0xFFFF)


def _diagnostic(
    lines: list[str], line: int, severity: _DiagnosticSeverity, code: str, message: str
) -> Diagnostic:
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
