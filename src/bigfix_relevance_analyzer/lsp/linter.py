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

Where a diagnostic goes
-----------------------
Over the text a finding is about, wherever it has
:attr:`~bigfix_relevance_analyzer.lint.Finding.spans` and every one of them
maps into the buffer (:mod:`~bigfix_relevance_analyzer.lsp.positions`): one
diagnostic per span, in finding order, then span order. That is one for most
findings, and one per use of each unknown name for ``unknown-inspector``,
which lint reports as a single finding per statement. A span with a message of
its own (:attr:`~bigfix_relevance_analyzer.lint.TextSpan.message`) shows that
instead of the finding's: each unknown name's diagnostic names just that name
and offers just its leads.

Otherwise -- a statement-level rule, an extraction problem, or a span that
cannot be placed for certain -- the diagnostic covers the finding's whole line,
as every diagnostic did before ranges existed.

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

Hover
-----
:meth:`DocumentLinter.hover` answers what the cursor is on, through the same
extractors and the same analysis cache as the diagnostics: the position is
mapped back into a site (:meth:`~bigfix_relevance_analyzer.lsp.positions.DocumentIndex.locate`),
the site analysed as linting analyses it, and the answer is
:mod:`~bigfix_relevance_analyzer.lsp.hover`'s. No hover anywhere the
diagnostics would not look either: past the size guard, or in a document no
extractor reads.

Runs in WASM
------------
This is the code an editor extension runs inside a componentize-py component,
which has only the modules and codecs its build snapshot saw. Hence UTF-8 only,
and UTF-16 lengths counted rather than encoded -- see
:func:`~bigfix_relevance_analyzer.lsp.positions.utf16_length`.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
from collections import OrderedDict
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any, Final, NamedTuple
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

# Underscore-private on purpose: this package's modules share extract's
# helpers this way (lint.py imports _extract_file and _is_recognized too).
from bigfix_relevance_analyzer.extract import (
    _UNTYPED_TEXT_SUFFIXES,
    RelevanceSite,
    _extract_data,
    _ExtractionProblem,
    _is_recognized,
)
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    _analyze_site,
    _judge_site,
    _lint_extracted,
)
from bigfix_relevance_analyzer.lsp.hover import describe
from bigfix_relevance_analyzer.lsp.positions import DocumentIndex, Position, Range, utf16_length

logger = logging.getLogger(__name__)

Diagnostic = dict[str, Any]
"""An LSP ``Diagnostic`` as plain JSON-serializable data."""

HoverResult = dict[str, Any]
"""An LSP ``Hover`` as plain JSON-serializable data."""

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

EXTRACTION_CACHE_SIZE: Final = 8
"""Documents whose last extraction the linter keeps, for hover to reuse."""

EXTRACTION_CACHE_BYTES: Final = 2 * 1024 * 1024
"""How much document, in UTF-8 bytes, the extractions kept may add up to.

An extraction holds far more than its text: its sites, their source maps and
the line index. A 995 KiB BES task's held 8.7 MiB, so eight of them would
approach 70 MiB, much of a WebAssembly component's memory. The document most
recently extracted is always kept, whatever its size: it is the one being
edited and hovered, which is what the cache is for."""


@dataclasses.dataclass(slots=True)
class _Extraction:
    """One document's text, as extracted: what diagnostics and hover share."""

    path: Path
    text: str
    data: bytes
    sites: list[RelevanceSite]
    problems: list[_ExtractionProblem]
    _index: DocumentIndex | None = None

    @property
    def index(self) -> DocumentIndex:
        """Built on first use: a clean document never needs one."""
        if self._index is None:
            self._index = DocumentIndex(self.text, self.data)
        return self._index


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
        self._extractions: OrderedDict[str, _Extraction] = OrderedDict()

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
                    ((0, 0), (0, utf16_length(first))),
                    _DiagnosticSeverity.INFORMATION,
                    DOCUMENT_TOO_LARGE,
                    message,
                )
            ]
        extracted = self._extract(uri, text, data, language_id)
        if extracted is None:
            return []
        findings = _lint_extracted(
            extracted.path, extracted.sites, extracted.problems, self.config, self._judge
        )
        if not findings:
            return []
        return [
            diagnostic
            for finding in findings
            for diagnostic in _diagnostics(extracted.index, finding)
        ]

    def hover(
        self, uri: str, text: str, position: Position, language_id: str | None = None
    ) -> HoverResult | None:
        """What to show for ``position`` in the document at ``uri`` holding ``text``.

        ``position`` is LSP's: a 0-based line and a UTF-16 character. ``None``
        when there is nothing to say there -- see :mod:`~bigfix_relevance_analyzer.lsp.hover`
        -- or the document is one :meth:`diagnostics` would not lint. The file
        type is chosen exactly as :meth:`diagnostics` chooses it.
        """
        data = text.encode("utf-8", errors="surrogatepass")
        if len(data) > self.max_document_bytes:
            return None
        extracted = self._extract(uri, text, data, language_id)
        if extracted is None:
            return None
        index = extracted.index
        located = index.locate(extracted.sites, position)
        if located is None:
            return None
        site, offset = located
        found = describe(_analyze_site(site, self.config), offset)
        if found is None:
            return None
        result: HoverResult = {"contents": {"kind": "markdown", "value": found.markdown}}
        mapped = index.site_range(site, found.span)
        if mapped is not None:
            (start_line, start), (end_line, end) = mapped
            result["range"] = {
                "start": {"line": start_line, "character": start},
                "end": {"line": end_line, "character": end},
            }
        return result

    def forget(self, uri: str) -> None:
        """Drop what is kept for ``uri``: the client closed it, or its text is
        no longer known. Nothing happens for a URI never seen."""
        self._extractions.pop(uri, None)

    def _extract(
        self, uri: str, text: str, data: bytes, language_id: str | None
    ) -> _Extraction | None:
        """The document's sites and index, reused while its text and type are
        unchanged; ``None`` for a type no extractor reads.

        Hover asks on every pause of the mouse, and re-extracting a large BES
        file each time is an XML parse per hover: about 50 ms of a 60 ms hover
        on a 382 KiB task. Keyed by URI and checked against the whole text --
        a comparison, far cheaper than the parse -- and the file type, which
        picks the extractor and can change under the same URI and text.
        """
        path = _document_path(uri, language_id)
        if not _is_recognized(path):
            return None
        cached = self._extractions.get(uri)
        if cached is not None and cached.path == path and cached.text == text:
            self._extractions.move_to_end(uri)
            return cached
        sites, problems = _extract_data(path, data)
        extracted = _Extraction(path, text, data, sites, problems)
        self._extractions[uri] = extracted
        self._extractions.move_to_end(uri)
        held = sum(len(kept.data) for kept in self._extractions.values())
        while len(self._extractions) > 1 and (
            len(self._extractions) > EXTRACTION_CACHE_SIZE or held > EXTRACTION_CACHE_BYTES
        ):
            _, dropped = self._extractions.popitem(last=False)
            held -= len(dropped.data)
        return extracted

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
        # The suffix only picks the extractor, and every untyped suffix picks
        # the same one, so any member will do. `min` rather than unpacking a
        # single element: a second untyped suffix must not break this.
        return path.with_name(f"{path.name}{min(_UNTYPED_TEXT_SUFFIXES)}")
    return path


def _diagnostics(index: DocumentIndex, finding: Finding) -> list[Diagnostic]:
    """``finding``'s diagnostics: one per span when all of them map, else one
    over its whole line. See the module docstring."""
    severity = _SEVERITIES[finding.severity]
    site = finding.site
    if site is not None and finding.spans:
        ranges = [index.site_range(site, span) for span in finding.spans]
        mapped = [found for found in ranges if found is not None]
        if len(mapped) == len(ranges):
            return [
                _diagnostic(found, severity, finding.code, span.message or finding.message)
                for found, span in zip(mapped, finding.spans, strict=True)
            ]
    line = max(finding.line - 1, 0)
    whole = ((line, 0), (line, index.line_length(line)))
    return [_diagnostic(whole, severity, finding.code, finding.message)]


def _diagnostic(found: Range, severity: _DiagnosticSeverity, code: str, message: str) -> Diagnostic:
    """A diagnostic over ``found``: 0-based lines, UTF-16 code unit characters."""
    (start_line, start), (end_line, end) = found
    return {
        "range": {
            "start": {"line": start_line, "character": start},
            "end": {"line": end_line, "character": end},
        },
        "severity": int(severity),
        "code": code,
        "source": SOURCE,
        "message": message,
    }
