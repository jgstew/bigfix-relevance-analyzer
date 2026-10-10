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

Quick fixes
-----------
:meth:`DocumentLinter.fixes` offers each fixable statement's safe fix as an
editor action, and one more that fixes the whole file. Nothing about whether a
fix is safe is decided here: :func:`~bigfix_relevance_analyzer.fixfile._plan`
plans it against the buffer's own bytes, exactly as ``--fix`` and the
pre-commit hook plan a file, and its byte edits become ranges through
:meth:`~bigfix_relevance_analyzer.lsp.positions.DocumentIndex.byte_range`. A
plan it refuses is no action, with the reason logged at debug level. An editor
asks on every cursor move, so nothing is planned unless a fixable diagnostic
is in the requested range, and plans are kept with the document's extraction
until its text changes.

Completion
----------
:meth:`DocumentLinter.completions` offers what fits at the cursor: after ``X
of``, inside ``whose (`` and at the start of a statement, ranked by how real
content uses each inspector (:mod:`bigfix_relevance_analyzer.completion`). The
cursor is placed by
:meth:`~bigfix_relevance_analyzer.lsp.positions.DocumentIndex.site_cursor`,
which also finds it just past the end of a half-typed statement; the context
comes from the tokens before it. Completion shares the extraction cache with
hover, and nothing else: it never analyses a statement, so it neither pays for
nor disturbs the findings diagnostics and quick fixes share. The dialect is
the one lint would use for the site; when that is not definite, both are
offered.

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
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, Final, NamedTuple
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.autofix import AutofixResult, _kept
from bigfix_relevance_analyzer.completion.context import scan_context
from bigfix_relevance_analyzer.completion.rank import rank
from bigfix_relevance_analyzer.dialect import Dialect

# Underscore-private on purpose: this package's modules share extract's
# helpers this way (lint.py imports _extract_file and _is_recognized too).
from bigfix_relevance_analyzer.extract import (
    _UNTYPED_TEXT_SUFFIXES,
    RelevanceSite,
    _extract_data,
    _ExtractionProblem,
    _is_recognized,
)
from bigfix_relevance_analyzer.fixfile import SiteAnchor, SiteFix, _plan, _site_anchor, site_fixes
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    TextSpan,
    _analyze_site,
    _judge_site,
    _lint_extracted,
    _site_dialect,
)
from bigfix_relevance_analyzer.lsp.hover import describe
from bigfix_relevance_analyzer.lsp.positions import DocumentIndex, Position, Range, utf16_length
from bigfix_relevance_analyzer.typecheck import TypeEnvironment

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

QUICKFIX_KIND: Final = "quickfix"
"""The code action kind of a fix for one statement."""

FIX_ALL_KIND: Final = "source.fixAll.bigfix-relevance"
"""The code action kind of the fix for the whole file: what
``editor.codeActionsOnSave`` names to fix on save."""

FIX_ALL_TITLE: Final = "Fix all safe issues in this file"

DEFAULT_CACHE_SIZE: Final = 2048
"""Sites whose findings the linter keeps -- as many as lint keeps analyses."""

COMPLETION_LIMIT: Final = 50
"""The most completions one request returns. A list that hits it says it is
incomplete, so the client asks again as more of the word is typed."""

EXTRACTION_CACHE_SIZE: Final = 8
"""Documents whose last extraction the linter keeps, for hover to reuse."""

EXTRACTION_CACHE_BYTES: Final = 2 * 1024 * 1024
"""How much document, in UTF-8 bytes, the extractions kept may add up to.

An extraction holds far more than its text: its sites, their source maps and
the line index. A 995 KiB BES task's held 8.7 MiB, so eight of them would
approach 70 MiB, much of a WebAssembly component's memory. The document most
recently extracted is always kept, whatever its size: it is the one being
edited and hovered, which is what the cache is for."""


@dataclasses.dataclass(frozen=True, slots=True)
class _Planned:
    """One fix plan, kept as what an action needs: its edits as ranges in the
    buffer, and the sites it applies to (by :func:`_site_anchor`)."""

    edits: tuple[tuple[Range, str], ...]
    applied: frozenset[SiteAnchor]


@dataclasses.dataclass(slots=True)
class _Extraction:
    """One document's text, as extracted: what diagnostics and hover share."""

    path: Path
    text: str
    data: bytes
    sites: list[RelevanceSite]
    problems: list[_ExtractionProblem]
    _index: DocumentIndex | None = None
    fixes: dict[SiteAnchor | None, _Planned | None] = dataclasses.field(default_factory=dict)
    """Planned quick-fix edits for this text, by site anchor (``None`` for the
    whole file); ``None`` for one that may not be offered. The edits, not the
    plans: a plan holds two copies of the document."""

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


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentFix:
    """One code action, as plain data: what the protocol layer turns into a
    ``CodeAction`` with a ``WorkspaceEdit``."""

    title: str
    kind: str
    """:data:`QUICKFIX_KIND` or :data:`FIX_ALL_KIND`."""

    diagnostics: tuple[Diagnostic, ...]
    """The diagnostics it fixes, exactly as :meth:`DocumentLinter.diagnostics` publishes them."""

    edits: tuple[tuple[Range, str], ...]
    """Ranges in the buffer and the text that replaces each; an insertion's
    range is empty. Disjoint, in document order."""

    is_preferred: bool = False
    """Whether it is the one fix for its diagnostics: what "Auto Fix" applies."""


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentCompletion:
    """One completion, as plain data: what the protocol layer turns into a
    ``CompletionItem``."""

    label: str
    detail: str
    """The signature it was ranked as, and its return type."""

    insert_text: str
    """What to insert: the label, or a snippet when the client takes them."""

    is_snippet: bool
    sort_text: str
    """The rank, zero-padded: the order to show while nothing typed decides it."""

    range: Range | None
    """The buffer range the insertion replaces: the partial word being typed,
    or the cursor itself when there is none. ``None`` when the partial word
    cannot be placed for certain; the client then uses its own word range."""


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
            result["range"] = lsp_range(mapped)
        return result

    def completions(
        self,
        uri: str,
        text: str,
        position: Position,
        language_id: str | None = None,
        *,
        snippets: bool = False,
    ) -> list[DocumentCompletion]:
        """What to offer at ``position`` in the document at ``uri`` holding ``text``.

        ``position`` is LSP's, as for :meth:`hover`; ``snippets`` says the
        client takes snippet insert text. Empty where nothing fits -- see
        :mod:`bigfix_relevance_analyzer.completion` -- and for a document
        :meth:`diagnostics` would not lint. Best first, at most
        :data:`COMPLETION_LIMIT`.
        """
        data = text.encode("utf-8", errors="surrogatepass")
        if len(data) > self.max_document_bytes:
            return []
        extracted = self._extract(uri, text, data, language_id)
        if extracted is None:
            return []
        index = extracted.index
        cursor = index.site_cursor(extracted.sites, position)
        if cursor is None:
            return []
        site, offset, after_space = cursor
        dialect = _site_dialect(site, self.config.dialect)
        context = scan_context(site.text, offset, after_space, dialect)
        if context is None:
            return []
        candidates = rank(
            context,
            [
                self._environment(each)
                for each in (
                    (dialect,) if dialect is not None else (Dialect.CLIENT, Dialect.SESSION)
                )
            ],
            limit=COMPLETION_LIMIT,
        )
        # From the start of what is being typed to the cursor: past the site's
        # text when a space was typed after a multi-word partial (`bes |`).
        start, end = context.replace
        replace: Range | None = (position, position)
        if start < end:
            typed = index.site_range(site, TextSpan(start, end))
            if typed is None and " " in context.partial:
                # Without a range the client replaces only its own word, the
                # last: `bes c` would become `bes bes computers`.
                return []
            replace = None if typed is None else (typed[0], position)
        return [
            DocumentCompletion(
                label=candidate.label,
                detail=candidate.detail,
                insert_text=candidate.snippet
                if snippets and candidate.snippet
                else candidate.label,
                is_snippet=snippets and candidate.snippet is not None,
                sort_text=f"{candidate.rank:04d}",
                range=replace,
            )
            for candidate in candidates
        ]

    def _environment(self, dialect: Dialect) -> TypeEnvironment:
        """The environment to rank in for ``dialect``: the configured platform
        only when it is one of that dialect's (a client platform would hide
        every session row)."""
        platform = self.config.platform
        if platform is not None and inspectors._dialect_of_context(platform) is not dialect:
            platform = None
        return TypeEnvironment.create(dialect, platform)

    def fixes(
        self,
        uri: str,
        text: str,
        language_id: str | None = None,
        *,
        range: Range | None = None,
        only: Sequence[str] | None = None,
    ) -> list[DocumentFix]:
        """The code actions for ``range`` of the document at ``uri`` holding ``text``.

        One :data:`QUICKFIX_KIND` action per statement with a fixable
        diagnostic in ``range`` (all of them when ``range`` is ``None``), each
        applying that statement's whole fix; then, when the file has two or
        more, a second-choice quick fix for all of them; then the
        :data:`FIX_ALL_KIND` action. ``only`` keeps just the kinds it names or
        is a prefix of, as LSP's ``context.only`` does, and asking for the
        fix-all kind by name gets it wherever ``range`` is: fix on save. The
        file type is chosen exactly as :meth:`diagnostics` chooses it.
        """

        def wanted(kind: str) -> bool:
            return only is None or any(kind == want or kind.startswith(f"{want}.") for want in only)

        data = text.encode("utf-8", errors="surrogatepass")
        if len(data) > self.max_document_bytes:
            return []
        extracted = self._extract(uri, text, data, language_id)
        if extracted is None:
            return []
        findings = _lint_extracted(
            extracted.path, extracted.sites, extracted.problems, self.config, self._judge
        )
        fixable = site_fixes(findings)
        if not fixable:
            return []
        # One pass over the findings, each fixable diagnostic kept with its
        # range, so the range test compares tuples rather than reading dicts.
        index = extracted.index
        ranged: dict[int, list[tuple[Range, Diagnostic]]] = {}
        for finding in findings:
            if finding.site is not None and finding.autofix is not None:
                ranged.setdefault(id(finding.site), []).extend(_ranged_diagnostics(index, finding))

        def published(fix: SiteFix) -> tuple[Diagnostic, ...]:
            return tuple(diagnostic for _, diagnostic in ranged.get(id(fix.site), ()))

        in_range = [
            fix
            for fix in fixable
            if range is None
            or any(_overlaps(found, range) for found, _ in ranged.get(id(fix.site), ()))
        ]
        asked_for_all = only is not None and wanted(FIX_ALL_KIND)
        if not in_range and not asked_for_all:
            return []

        actions: list[DocumentFix] = []
        if wanted(QUICKFIX_KIND):
            for fix in in_range:
                planned = self._planned(extracted, _site_anchor(fix.site))
                if planned is not None:
                    actions.append(
                        DocumentFix(
                            _title(fix.autofix),
                            QUICKFIX_KIND,
                            published(fix),
                            planned.edits,
                            is_preferred=True,
                        )
                    )
        if (len(fixable) > 1 and in_range and wanted(QUICKFIX_KIND)) or wanted(FIX_ALL_KIND):
            whole = self._planned(extracted, None)
            # Only what the whole-file plan applied: it may refuse a site alone
            # and fix the rest, and an action must not claim what it leaves.
            applied = (
                []
                if whole is None
                else [fix for fix in fixable if _site_anchor(fix.site) in whole.applied]
            )
            if whole is not None and applied:
                fixed = tuple(diagnostic for fix in applied for diagnostic in published(fix))
                reached = any(fix in in_range for fix in applied)
                if len(applied) > 1 and reached and wanted(QUICKFIX_KIND):
                    actions.append(DocumentFix(FIX_ALL_TITLE, QUICKFIX_KIND, fixed, whole.edits))
                if wanted(FIX_ALL_KIND) and (reached or asked_for_all):
                    actions.append(DocumentFix(FIX_ALL_TITLE, FIX_ALL_KIND, fixed, whole.edits))
        return actions

    def _planned(self, extracted: _Extraction, anchor: SiteAnchor | None) -> _Planned | None:
        """The fix for one site (``anchor``) or the whole file (``None``), as
        ranges in the buffer; ``None`` when no fix may be offered."""
        if anchor not in extracted.fixes:
            extracted.fixes[anchor] = self._plan_edits(extracted, anchor)
        return extracted.fixes[anchor]

    def _plan_edits(self, extracted: _Extraction, anchor: SiteAnchor | None) -> _Planned | None:
        """:meth:`_planned`, uncached."""
        only = None if anchor is None else {anchor}
        plan = _plan(extracted.path, extracted.data, self.config, judge=self._judge, only=only)
        for refused in plan.unapplied:
            logger.debug("no quick fix at line %d: %s", refused.line, refused.reason)
        if not plan.applied:
            return None
        edits: list[tuple[Range, str]] = []
        for edit in plan.edits:
            found = extracted.index.byte_range(edit.start, edit.end)
            if found is None:
                logger.debug("no quick fix: bytes %d-%d do not map", edit.start, edit.end)
                return None
            edits.append((found, edit.replacement.decode("utf-8")))
        return _Planned(tuple(edits), frozenset(_site_anchor(fix.site) for fix in plan.applied))

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


def _title(autofix: AutofixResult) -> str:
    """A quick fix's title: the one change it makes, or how many it makes.

    Worded as lint words what a fix did (``lint._with_fix``)."""
    count = sum(autofix.applied.values())
    if count == 1 and len(autofix.edits) == 1:
        (edit,) = autofix.edits
        if _kept(edit, autofix.original) is not None:
            return "Wrap in `unique value of`"
        return f"Change `{autofix.original[edit.start : edit.end]}` to `{edit.replacement}`"
    return f"Apply {count} safe fixes to this statement"


def _overlaps(found: Range, wanted: Range) -> bool:
    """Whether ``found`` meets ``wanted``, touching included: a cursor at
    either end of a squiggle is on it."""
    return found[0] <= wanted[1] and wanted[0] <= found[1]


def _diagnostics(index: DocumentIndex, finding: Finding) -> list[Diagnostic]:
    """``finding``'s diagnostics: one per span when all of them map, else one
    over its whole line. See the module docstring."""
    return [diagnostic for _, diagnostic in _ranged_diagnostics(index, finding)]


def _ranged_diagnostics(index: DocumentIndex, finding: Finding) -> list[tuple[Range, Diagnostic]]:
    """:func:`_diagnostics`, each with its range as a tuple."""
    severity = _SEVERITIES[finding.severity]
    site = finding.site
    if site is not None and finding.spans:
        ranges = [index.site_range(site, span) for span in finding.spans]
        mapped = [found for found in ranges if found is not None]
        if len(mapped) == len(ranges):
            return [
                (found, _diagnostic(found, severity, finding.code, span.message or finding.message))
                for found, span in zip(mapped, finding.spans, strict=True)
            ]
    line = max(finding.line - 1, 0)
    whole = ((line, 0), (line, index.line_length(line)))
    return [(whole, _diagnostic(whole, severity, finding.code, finding.message))]


def _diagnostic(found: Range, severity: _DiagnosticSeverity, code: str, message: str) -> Diagnostic:
    """A diagnostic over ``found``: 0-based lines, UTF-16 code unit characters."""
    return {
        "range": lsp_range(found),
        "severity": int(severity),
        "code": code,
        "source": SOURCE,
        "message": message,
    }


def lsp_range(found: Range) -> dict[str, dict[str, int]]:
    """``found`` as an LSP ``Range``: 0-based lines, UTF-16 code unit characters.

    The one place a range is written out, for diagnostics, hover and the
    protocol layer's code action edits alike."""
    (start_line, start), (end_line, end) = found
    return {
        "start": {"line": start_line, "character": start},
        "end": {"line": end_line, "character": end},
    }
