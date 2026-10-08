"""Find the relevance statements in BigFix content.

Extracts every relevance statement from BES XML documents, console dashboards
and web reports, ClientUI dashboards, plain-relevance files, and markdown code
blocks, recording where each one came from and which dialect it is written in.

Two independent opinions decide a statement's dialect, and every
:class:`RelevanceSite` keeps both:

* **Context** -- which element, of which kind of file, a statement was found
  in. Definite context wins, because it says which engine will actually
  evaluate the statement.
* **Content** --
  :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect` reading
  the inspectors the statement uses. It fills in the dialect wherever context
  was :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN` (a plain
  ``.rel`` file, a markdown code block, a ClientUI document that also evaluates
  relevance from JavaScript), and it may itself have no opinion.

Where the two disagree, :attr:`RelevanceSite.dialect_conflict` is true and a
warning is logged: relevance in the wrong place fails at evaluation time.

XML is parsed with the standard library's expat by default, so the package has
no dependencies outside the standard library. Projects that already parse BES
XML with lxml can hand over their tree via
:func:`extract_relevance_from_lxml_tree` instead of paying to re-parse it.
"""

from __future__ import annotations

import enum
import logging
import os
import re
import xml.parsers.expat
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal

from bigfix_relevance_analyzer._serialize import _as_path, _enum
from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect, is_definite

if TYPE_CHECKING:  # pragma: no cover - typing only
    from lxml import etree

__all__ = [
    "HtmlContext",
    "RelevanceSite",
    "SiteKind",
    "SourceMap",
    "SourceSpan",
    "extract_relevance_from_actionscript",
    "extract_relevance_from_bes_xml",
    "extract_relevance_from_file",
    "extract_relevance_from_html_text",
    "extract_relevance_from_lxml_tree",
    "extract_relevance_from_markdown",
    "looks_like_clientui",
]

logger = logging.getLogger(__name__)

SiteKind = Literal[
    "relevance",
    "success-criteria",
    "analysis-property",
    "actionscript-substitution",
    "actionscript-condition",
    "relevance-pi",
    "javascript-call",
    "plain-text",
    "markdown-codeblock",
]


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """One run of a site's text, and the bytes of the file it was decoded from."""

    start: int
    end: int
    """The run's range in :attr:`RelevanceSite.text`."""

    raw_start: int
    raw_end: int
    """The run's range in the file's bytes."""

    atomic: bool
    """Whether the bytes are not simply the text's UTF-8 encoding.

    An entity or character reference (``&lt;`` for ``<``), or a CRLF or lone
    CR line ending the XML parser folded to ``\n``. An edit may replace an
    atomic run whole, but never part of one: there is no part of ``&lt;`` that
    is part of ``<``. A run that is not atomic maps character by character.
    """


@dataclass(frozen=True, slots=True)
class SourceMap:
    """Where each character of a site's text sits in the bytes of its file.

    :attr:`RelevanceSite.text` is decoded and stripped, so it cannot be found in
    the file by searching for it. This is what a fix needs to be written back
    instead: :meth:`raw_range` turns a range of the text into the bytes that
    hold it, keeping every entity, CDATA section and line ending as written.
    """

    text: str
    """The text mapped: the site's :attr:`RelevanceSite.text`."""

    spans: tuple[SourceSpan, ...]
    """Runs covering the whole of :attr:`text`, in order, with no gaps."""

    def _byte_offset(self, span: SourceSpan, position: int) -> int:
        """Where ``position``, inside or at either end of ``span``, sits in the file."""
        if position == span.start:
            return span.raw_start
        if position == span.end:
            return span.raw_end
        return span.raw_start + _utf8_len(self.text, span.start, position)

    def raw_range(self, start: int, end: int) -> tuple[int, int] | None:
        """The bytes holding ``text[start:end]``, or ``None`` if there are none.

        ``None`` when the range splits an atomic run, or when its text is not
        one unbroken stretch of the file -- ``cl<![CDATA[ient]]>`` is
        ``client`` in the text, but no byte range holds exactly those six
        characters.
        """
        if not 0 <= start < end <= len(self.text):
            return None
        raw_start: int | None = None
        raw_end: int | None = None
        for span in self.spans:
            if span.end <= start:
                continue
            if span.start >= end:
                break
            if span.atomic and (start > span.start or end < span.end):
                return None
            if raw_start is None:
                raw_start = self._byte_offset(span, max(start, span.start))
            elif span.raw_start != raw_end:
                return None
            raw_end = self._byte_offset(span, min(end, span.end))
        if raw_start is None or raw_end is None:
            return None
        return raw_start, raw_end


@dataclass(frozen=True, slots=True)
class RelevanceSite:
    """One relevance statement, and where it was found."""

    kind: SiteKind
    """What sort of place the statement was found in."""

    text: str
    """The relevance statement itself, stripped of surrounding whitespace."""

    line: int
    """1-based line of the source file the statement starts on."""

    context: str
    """Short label naming where this came from, for use in messages."""

    dialect: Dialect
    """Which relevance dialect the statement is written in.

    The resolved verdict: :attr:`context_dialect` when context was definite,
    otherwise :attr:`content_dialect`, otherwise
    :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN`.
    """

    context_dialect: Dialect = Dialect.UNCERTAIN
    """What the extraction context alone said, before content was consulted.

    :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN` means the
    mechanism this was found in does not settle the dialect -- a plain
    ``.rel`` file, a markdown code block, or a ClientUI document that also
    evaluates relevance from JavaScript.
    """

    content_dialect: Dialect | None = None
    """What the content classifier made of the statement itself.

    ``None`` means it had no opinion: nothing in the statement is specific to
    either dialect. See
    :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`.
    """

    source_map: SourceMap | None = field(default=None, compare=False, hash=False, repr=False)
    """Which bytes of the file each character of :attr:`text` came from.

    What lets a fix be written back into the file
    (:mod:`~bigfix_relevance_analyzer.fixfile`). Only BES XML read as bytes
    (:func:`extract_relevance_from_bes_xml`, so also
    :func:`extract_relevance_from_file` on a ``.bes``) has one so far; it is
    ``None`` everywhere else, and for an element whose bytes are not its text
    in UTF-8. Left out of equality, hashing and :meth:`to_dict`: it says
    where a statement is, not what it is, and a site from lxml or from a
    string must still compare equal to the same site read from bytes.
    """

    column: int | None = field(default=None, compare=False, hash=False, repr=False)
    """1-based column, in the decoded text of :attr:`line`, where :attr:`text` starts.

    Set by the text extractors -- a whole ``.rel`` or ``.bsr`` file, a markdown
    fence, an HTML processing instruction or JavaScript call, an ActionScript
    substitution -- and counted in characters of the text they read, so after
    ``\r\n`` and ``\r`` are folded to ``\n``, which moves no character within
    a line. With :attr:`line`, it is what places a span of :attr:`text` in an
    editor's buffer (:mod:`bigfix_relevance_analyzer.lsp.positions`).

    ``None`` for BES XML, whose :attr:`source_map` places every character
    already, and whenever :attr:`text` does not start on :attr:`line`: a fence
    or ``<?Relevance`` whose statement starts on a later line, after blank
    ones. Left out of equality, hashing, ``repr`` and :meth:`to_dict` for the
    reason :attr:`source_map` is: it says where a statement is, not what it
    is, and the editor's per-site cache must still hit for a statement that
    only moved sideways.
    """

    def to_dict(self) -> dict[str, Any]:
        """This site as JSON-serializable plain data.

        :attr:`dialect_conflict` is included even though it is derived: it is
        the most actionable single fact about a site -- session inspectors sat
        in a client-relevance element, or the reverse -- and every consumer
        recomputing it from the three dialect fields is three chances to get
        the ``UNCERTAIN`` handling subtly wrong.
        """
        return {
            "kind": self.kind,
            "text": self.text,
            "line": self.line,
            "context": self.context,
            "dialect": self.dialect.value,
            "context_dialect": self.context_dialect.value,
            "content_dialect": _enum(self.content_dialect),
            "dialect_conflict": self.dialect_conflict,
        }

    @property
    def dialect_conflict(self) -> bool:
        """Whether context and content each reached a definite, *different* dialect.

        Worth surfacing: it usually means the statement is in the wrong place --
        session inspectors in a fixlet's ``<Relevance>``, say, which every
        endpoint will fail to evaluate. :attr:`dialect` still reports what
        context said, since which engine evaluates the statement is a fact about
        where it was found, not about what it says.
        """
        return (
            is_definite(self.context_dialect)
            and is_definite(self.content_dialect)
            and self.context_dialect is not self.content_dialect
        )


class HtmlContext(enum.Enum):
    """Where an HTML document holding relevance gets rendered.

    This is what decides the dialect of a static ``<?Relevance ?>``
    substitution, since the syntax is identical in both places.
    """

    CONSOLE = "console"
    """Console dashboard, web report or WebUI: substitutions are session relevance."""

    CLIENTUI = "clientui"
    """ClientUI dashboard, rendered by the BES Client: substitutions are client relevance."""

    UNKNOWN = "unknown"
    """Renderer not established, so substitutions get no dialect from context.

    A bare `.html` file is this: unlike `.ojo` or `.besrpt`, the extension says
    nothing about which side renders it. A JavaScript relevance call in the
    document still settles it, since only the console side can make one.
    """


def _make_site(
    *,
    kind: SiteKind,
    text: str,
    line: int,
    context: str,
    context_dialect: Dialect,
    source_map: SourceMap | None = None,
    column: int | None = None,
) -> RelevanceSite:
    """Build a site, settling its dialect and keeping both opinions on record.

    Every site is built here, so the classifier is consulted even when context
    already settled the dialect. That costs two regex scans per site and buys
    conflict detection: a statement whose content reads as the *other* dialect
    than its surroundings imply is usually in the wrong place, and gets a
    warning. Context still wins the resolved :attr:`RelevanceSite.dialect` --
    which engine will evaluate a statement is a fact about where it was found.
    """
    content_dialect = classify_relevance_dialect(text)
    if is_definite(context_dialect):
        dialect = context_dialect
        if is_definite(content_dialect) and content_dialect is not context_dialect:
            logger.warning(
                "dialect conflict in %s at line %d: found in %s relevance but reads as %s "
                "relevance: %s",
                context,
                line,
                context_dialect.value,
                content_dialect.value,
                text,
            )
    elif content_dialect is not None:
        dialect = content_dialect
    else:
        dialect = Dialect.UNCERTAIN
    return RelevanceSite(
        kind=kind,
        text=text,
        line=line,
        context=context,
        dialect=dialect,
        context_dialect=context_dialect,
        content_dialect=content_dialect,
        source_map=source_map,
        column=column,
    )


class _TextSource:
    """Where each piece of an element's decoded text sits in the file's bytes.

    Built from the pieces expat reports one at a time, each with its byte
    index; :meth:`site_map` cuts out the part one site's text came from. The
    spans are worked out on the first call, not up front: most elements a
    walk collects -- a ``<Description>`` with no relevance in it, say --
    never yield a site, and mapping every one of them cost about a third of
    the extraction time over a real content repository.
    """

    def __init__(self, data: bytes, indexes: Sequence[int], chunks: Sequence[str]) -> None:
        self.text = "".join(chunks)
        self._data: bytes | None = data
        self._pieces = tuple(zip(indexes, chunks, strict=True))
        self._spans: tuple[SourceSpan, ...] | None = None

    @property
    def spans(self) -> tuple[SourceSpan, ...] | None:
        """The element's spans, or ``None`` if its bytes are not recognizably its text."""
        if self._data is not None:
            self._spans = _text_spans(self._data, self._pieces)
            self._data = None  # the spans are all that is needed from it now
            self._pieces = ()
        return self._spans

    def site_map(self, offset: int, length: int) -> SourceMap | None:
        """The map for ``text[offset:offset + length]``, re-based to start at 0.

        ``None`` if the cut would split an atomic piece -- not something
        stripping whitespace or cutting at a brace can do with the references
        XML defines, but checked rather than assumed.
        """
        element_spans = self.spans
        if element_spans is None:
            return None
        end = offset + length
        spans: list[SourceSpan] = []
        for span in element_spans:
            if span.end <= offset:
                continue
            if span.start >= end:
                break
            start, stop = max(span.start, offset), min(span.end, end)
            if span.atomic:
                if (start, stop) != (span.start, span.end):
                    return None
                raw_start, raw_end = span.raw_start, span.raw_end
            else:
                raw_start = span.raw_start + _utf8_len(self.text, span.start, start)
                raw_end = raw_start + _utf8_len(self.text, start, stop)
            spans.append(SourceSpan(start - offset, stop - offset, raw_start, raw_end, span.atomic))
        return SourceMap(self.text[offset:end], tuple(spans))


def _utf8_len(text: str, start: int, end: int) -> int:
    """How many bytes ``text[start:end]`` takes in the UTF-8 file it came from."""
    return len(text[start:end].encode("utf-8"))


def _site_map(source: _TextSource | None, offset: int, text: str) -> SourceMap | None:
    return None if source is None else source.site_map(offset, len(text))


def _column(text: str, offset: int, anchor: int, column_offset: int | None) -> int | None:
    """The 1-based column of ``text[offset]`` in its document, when it is known.

    ``anchor`` is where the site's reported line was taken from -- a
    ``<?Relevance``, a fence -- so ``None`` when the statement starts on a
    later line than the site says, where no column on the site's line is right.

    ``column_offset`` is to columns what ``line_offset`` is to lines: how far
    into its document's line ``text`` starts, so it shifts only ``text``'s
    first line. ``None`` when ``text``'s columns are not its document's at
    all -- a BES element's body, which starts after a tag and has its
    entities decoded -- and then no site has a column.
    """
    if column_offset is None:
        return None
    line_start = text.rfind("\n", 0, offset) + 1
    if line_start > anchor:
        return None
    return offset - line_start + 1 + (column_offset if line_start == 0 else 0)


def _stripped(text: str, start: int = 0, end: int | None = None) -> tuple[int, str]:
    """``text[start:end].strip()``, and where in ``text`` it starts."""
    chunk = text[start:end]
    body = chunk.strip()
    return start + len(chunk) - len(chunk.lstrip()), body


# ---------------------------------------------------------------------------
# ActionScript `{...}` substitution scanner
# ---------------------------------------------------------------------------

# `createfile until X` / `appendfile until X` open a heredoc: every following
# line up to a line that is exactly `X` is file content. The action engine
# still substitutes relevance in it -- the official `createfile until`
# reference uses `{name of operating system}` in a block body as its example,
# and it is why heredoc payloads escape a literal brace as `{{` -- so the body
# is scanned for substitutions, just not as ActionScript: `//` is not a
# comment there, and `if {...}` is text, not a condition (issue 52).
_HEREDOC_RE = re.compile(r"^\s*(?:create|append)file\s+until\s+(\S+)\s*$", re.IGNORECASE)

# `if`, `elseif`, `continue if` write their condition directly against the
# keyword -- `if{...}`, `elseif {...}`, `continue if{...}` -- confirmed
# against real `.bes` content in both spacings, never with a bare condition or
# a parenthesized `if(...)`. The `(?:^|[^A-Za-z0-9_])` prefix is load-bearing:
# without it, `endif{...}` would match on its own trailing `if`, since the
# alternation only anchors the *end* of the match to the brace.
_CONDITION_KEYWORD_RE = re.compile(
    r"(?:^|[^A-Za-z0-9_])(?:continue\s+if|elseif|if)\s*$", re.IGNORECASE
)


def _iter_substitution_spans(
    body: str, unterminated: list[int] | None = None
) -> Iterator[tuple[int, int, str, bool]]:
    """Yield ``(line, offset, relevance_text, is_condition)`` for each `{...}`
    substitution in ``body``, ``offset`` being where the text starts in it.

    The line of each `{` that is never closed and is not the line's last
    character -- a runtime failure, see below -- is appended to
    ``unterminated`` when one is given.

    Handles `{{`/`}}` literal-brace escapes, ignores `}` inside a relevance
    string literal, and skips `//` comment lines entirely -- except inside
    heredoc content, where `//` is file content. ``is_condition`` is
    whether the substitution is the condition of an `if`/`elseif`/`continue
    if` command, which the type checker holds to a different requirement than
    an ordinary substitution -- see `_SLOT_REQUIREMENTS` in `lint.py`.
    """
    lines = body.split("\n")
    heredoc_terminator: str | None = None

    # Offset of the start of each line within `body`, so each site's text can
    # be mapped back to its position in the source.
    index = 0
    for line_number, line in enumerate(lines, start=1):
        line_start = index
        index += len(line) + 1

        in_heredoc = heredoc_terminator is not None
        if in_heredoc:
            if line.strip() == heredoc_terminator:
                heredoc_terminator = None
                continue
        else:
            heredoc_match = _HEREDOC_RE.match(line)
            if heredoc_match:
                heredoc_terminator = heredoc_match.group(1)
                continue

            # A `//` line is an ActionScript comment: it never runs, so its
            # substitutions are never evaluated. Only outside a heredoc,
            # where `//` is file content.
            if line.lstrip().startswith("//"):
                continue

        column = 0
        while column < len(line):
            brace = line.find("{", column)
            if brace == -1:
                break
            if line.startswith("{{", brace):
                column = brace + 2
                continue

            # Line by line: a `}` on a later line never closes this one.
            end = _find_substitution_end(body, line_start + brace + 1, line_start + len(line))
            if end is None:
                # A `{` that is the line's very last character is written
                # literally (`try {`); one with anything after it, even
                # whitespace, fails the action (real actions, issue 52).
                if brace == len(line) - 1:
                    logger.debug("literal `{` at the end of line %d", line_number)
                else:
                    if unterminated is not None:
                        unterminated.append(line_number)
                    logger.warning(
                        "unterminated relevance substitution opened at line %d; skipping it",
                        line_number,
                    )
                break

            offset, text = _stripped(body, line_start + brace + 1, end)
            if text:
                is_condition = (
                    not in_heredoc and _CONDITION_KEYWORD_RE.search(line[:brace]) is not None
                )
                yield line_number, offset, text, is_condition
            else:
                logger.debug("empty relevance substitution at line %d", line_number)

            column = end + 1 - line_start


def _find_substitution_end(body: str, start: int, stop: int) -> int | None:
    """Index of the `}` closing a substitution opened just before ``start``.

    Only ``body[start:stop]`` -- the rest of the opening line -- is searched:
    the action engine substitutes line by line, so a substitution split over
    lines never closes (real actions, issue 52).
    """
    position = start
    in_string = False
    while position < stop:
        char = body[position]
        if in_string:
            if char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "}":
            if body.startswith("}}", position):
                position += 2
                continue
            return position
        position += 1
    return None


def extract_relevance_from_actionscript(
    body: str,
    *,
    context: str = "ActionScript",
    dialect: Dialect = Dialect.CLIENT,
    line_offset: int = 0,
    column_offset: int | None = 0,
) -> list[RelevanceSite]:
    """Extract the `{...}` relevance substitutions from an ActionScript body.

    Lines are 1-based within ``body`` plus ``line_offset``, for a body embedded
    in a larger file; ``column_offset`` is how far into its line ``body``
    starts there, or ``None`` if unknown (see :attr:`RelevanceSite.column`).
    ActionScript runs on the endpoint, so substitutions in it are client
    relevance, which is what ``dialect`` says by default.
    """
    return _actionscript_sites(
        body,
        context=context,
        dialect=dialect,
        line_offset=line_offset,
        column_offset=column_offset,
    )


@dataclass(frozen=True, slots=True)
class _ExtractionProblem:
    """Something wrong with the content around the relevance, found while
    extracting it, that ``lint`` reports as a finding of its own.

    Private on purpose: the public extractors return only sites, and only
    ``lint`` and ``fixfile`` ask for these, through the private ``_extract_*``
    entry points.
    """

    code: str
    """The lint rule this is reported under, e.g. ``unterminated-substitution``."""

    line: int
    """1-based line, absolute in the file -- the convention of :attr:`RelevanceSite.line`."""

    message: str
    context: str


_UNTERMINATED_MESSAGE: Final = (
    "`{` opens a relevance substitution that is not closed on this line; the action "
    "fails here. Close it with `}` on the same line, or write `{{` for a literal brace"
)


_UNTERMINATED_PI_MESSAGE: Final = (
    "`<?Relevance` has no closing `?>` after it, so the relevance in it was not linted. "
    "Close it with `?>`"
)


def _unterminated_pi_message(problem_context: str) -> str:
    """:data:`_UNTERMINATED_PI_MESSAGE`, worded for where the processing
    instruction sits: in a BES `<Description>` (``problem_context`` is then
    the element's path) the `?>` must come before `</Description>`."""
    if problem_context.rsplit("/", 1)[-1] == "Description":
        return f"{_UNTERMINATED_PI_MESSAGE} before `</Description>`"
    return _UNTERMINATED_PI_MESSAGE


_UNTERMINATED_FENCE_MESSAGE: Final = (
    "this relevance code fence is never closed, so the relevance in it was not linted. "
    "Close it with a matching fence line"
)


def _actionscript_sites(
    body: str,
    *,
    context: str,
    dialect: Dialect,
    line_offset: int,
    source: _TextSource | None = None,
    problems: list[_ExtractionProblem] | None = None,
    column_offset: int | None = 0,
) -> list[RelevanceSite]:
    """The substitution sites of ``body``; see :func:`_column` for ``column_offset``."""
    unterminated: list[int] = []
    sites = [
        _make_site(
            kind="actionscript-condition" if is_condition else "actionscript-substitution",
            text=text,
            line=line + line_offset,
            context=context,
            context_dialect=dialect,
            source_map=_site_map(source, offset, text),
            # A substitution never spans lines, so it starts on its own line.
            column=_column(body, offset, offset, column_offset),
        )
        for line, offset, text, is_condition in _iter_substitution_spans(body, unterminated)
    ]
    if problems is not None:
        problems.extend(
            _ExtractionProblem(
                code="unterminated-substitution",
                line=line + line_offset,
                message=_UNTERMINATED_MESSAGE,
                context=context,
            )
            for line in unterminated
        )
    return sites


# ---------------------------------------------------------------------------
# HTML / text scanner: <?Relevance ?> and JavaScript relevance calls
# ---------------------------------------------------------------------------

_PI_OPEN_RE = re.compile(r"<\?relevance\b", re.IGNORECASE)

# `Relevance(` or `EvaluateRelevance(`, but not when it is the tail of a longer
# identifier or a property access (`bigfix.relevance.errorWrapper`), nor the
# opener of a processing instruction whose body starts with a parenthesis
# (`<?Relevance ("x") ?>`), which would otherwise be a second, bogus site. Only
# `<?` is excluded, not a bare `?`: minified JavaScript calls it straight after
# a ternary's `?` (`a?Relevance("x"):b`).
_JS_CALL_RE = re.compile(r"(?<![\w.$])(?<!<\?)(?:Evaluate)?Relevance\s*\(")

_CLIENTUI_MARKER_RE = re.compile(
    r"""product\s*=\s*["']CustomDashboardClientUI["']|cid:load\?page=|takeoffer:""",
    re.IGNORECASE,
)


def looks_like_clientui(text: str) -> bool:
    """Whether ``text`` carries a marker only a ClientUI dashboard would have.

    Corroborating evidence only: a ClientUI need not have any of these markers,
    so a ``False`` result does not mean a document is not one. Dialect is
    decided by the mechanism the relevance uses, not by this.
    """
    return _CLIENTUI_MARKER_RE.search(text) is not None


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _iter_pi_spans(
    text: str, unterminated: list[int] | None = None, column_offset: int | None = 0
) -> Iterator[tuple[int, int, str, int | None]]:
    """Yield ``(line, offset, relevance_text, column)`` for each `<?Relevance ?>` in ``text``.

    A body may span lines. The line of each `<?Relevance` with no `?>` anywhere
    after it in ``text`` is appended to ``unterminated`` when one is given.
    ``text`` is one element's body when it comes from a BES `<Description>`, so
    the `?>` has to close before that element does.
    """
    for match in _PI_OPEN_RE.finditer(text):
        end = text.find("?>", match.end())
        if end == -1:
            if unterminated is not None:
                unterminated.append(_line_of(text, match.start()))
            logger.warning(
                "unterminated <?Relevance ?> processing instruction at line %d; skipping it",
                _line_of(text, match.start()),
            )
            continue
        offset, body = _stripped(text, match.end(), end)
        if body:
            column = _column(text, offset, match.start(), column_offset)
            yield _line_of(text, match.start()), offset, body, column
        else:
            logger.debug(
                "empty <?Relevance ?> processing instruction at line %d",
                _line_of(text, match.start()),
            )


def _read_js_string_literal(text: str, start: int) -> tuple[str, int] | None:
    """Read a JS string literal at ``start``; return ``(contents, end_index)``."""
    if start >= len(text) or text[start] not in "\"'":
        return None
    quote = text[start]
    position = start + 1
    while position < len(text):
        char = text[position]
        if char == "\\":
            position += 2
            continue
        if char == quote:
            return text[start + 1 : position], position + 1
        if char == "\n":
            # An unescaped newline ends a JS string literal; this is not one.
            return None
        position += 1
    return None


def _iter_js_call_spans(
    text: str, column_offset: int | None = 0
) -> Iterator[tuple[int, int, str, int | None]]:
    """Yield ``(line, offset, relevance_text, column)`` for each JS relevance call in ``text``.

    Only a call whose argument is one complete string literal is yielded. A
    call built from a variable, or concatenated with one, has no statement to
    extract -- the fragment on its own would not be valid relevance.
    """
    for match in _JS_CALL_RE.finditer(text):
        position = match.end()
        while position < len(text) and text[position] in " \t":
            position += 1

        literal = _read_js_string_literal(text, position)
        if literal is None:
            logger.debug(
                "relevance call at line %d has a non-literal argument; skipping it",
                _line_of(text, match.start()),
            )
            continue

        _, end = literal
        # Anything other than `)` or `,` after the literal means the argument
        # was an expression the literal is only part of (e.g. `'x ' + query`).
        tail = text[end:].lstrip(" \t")
        if not tail.startswith((")", ",")):
            logger.debug(
                "relevance call at line %d concatenates its argument; skipping it",
                _line_of(text, match.start()),
            )
            continue

        offset, body = _stripped(text, position + 1, end - 1)
        if body:
            column = _column(text, offset, match.start(), column_offset)
            yield _line_of(text, match.start()), offset, body, column


def extract_relevance_from_html_text(
    text: str,
    *,
    context: HtmlContext,
    line_offset: int = 0,
    label: str | None = None,
    column_offset: int | None = 0,
) -> list[RelevanceSite]:
    """Extract relevance from an HTML/text document, in document order.

    ``context`` decides the dialect of static `<?Relevance ?>` substitutions:
    session relevance in a console dashboard or web report, client relevance in
    a ClientUI dashboard, and no opinion at all when the renderer is
    :attr:`HtmlContext.UNKNOWN`. JavaScript relevance calls are always session
    relevance -- a ClientUI cannot evaluate relevance from JavaScript, so such a
    call is itself proof the document is not one, wherever it is found. A
    ClientUI document that also has a JS call contradicts itself, so context
    settles nothing for its substitutions either; both cases fall to the
    content classifier, which may in turn have no opinion.

    ``line_offset`` is added to every line, for scanning a fragment embedded in
    a larger file, and ``column_offset`` is how far into its line the fragment
    starts there, or ``None`` if unknown (see :attr:`RelevanceSite.column`).
    """
    return _html_sites(
        text, context=context, line_offset=line_offset, label=label, column_offset=column_offset
    )


def _html_sites(
    text: str,
    *,
    context: HtmlContext,
    line_offset: int,
    label: str | None,
    source: _TextSource | None = None,
    problems: list[_ExtractionProblem] | None = None,
    problem_context: str = "HTML",
    column_offset: int | None = 0,
) -> list[RelevanceSite]:
    """The sites of an HTML document or fragment; see :func:`_column` for
    ``column_offset``."""
    unterminated: list[int] = []
    pi_spans = list(_iter_pi_spans(text, unterminated, column_offset))
    if problems is not None:
        problems.extend(
            _ExtractionProblem(
                code="unterminated-processing-instruction",
                line=line + line_offset,
                message=_unterminated_pi_message(problem_context),
                context=problem_context,
            )
            for line in unterminated
        )
    js_spans = list(_iter_js_call_spans(text, column_offset))

    if context is HtmlContext.CLIENTUI and js_spans:
        pi_dialect = Dialect.UNCERTAIN
        logger.debug(
            "ClientUI document also evaluates relevance from JavaScript; "
            "treating its substitutions as an uncertain dialect"
        )
    elif context is HtmlContext.CLIENTUI:
        pi_dialect = Dialect.CLIENT
    elif context is HtmlContext.CONSOLE:
        pi_dialect = Dialect.SESSION
    elif js_spans:
        # A JS relevance call proves this is not a ClientUI, even though
        # nothing told us which renderer it is otherwise.
        pi_dialect = Dialect.SESSION
    else:
        pi_dialect = Dialect.UNCERTAIN

    pi_label = label or (
        "ClientUI HTML relevance substitution"
        if context is HtmlContext.CLIENTUI
        else "HTML relevance substitution"
    )
    js_label = label or "JavaScript relevance call"

    def sites_from(
        spans: Iterable[tuple[int, int, str, int | None]],
        kind: SiteKind,
        context: str,
        dialect: Dialect,
    ) -> list[RelevanceSite]:
        return [
            _make_site(
                kind=kind,
                text=body,
                line=line + line_offset,
                context=context,
                context_dialect=dialect,
                source_map=_site_map(source, offset, body),
                column=column,
            )
            for line, offset, body, column in spans
        ]

    sites = sites_from(pi_spans, "relevance-pi", pi_label, pi_dialect)
    sites += sites_from(js_spans, "javascript-call", js_label, Dialect.SESSION)
    return sorted(sites, key=lambda site: site.line)


# ---------------------------------------------------------------------------
# Markdown and plain relevance files
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")

_MARKDOWN_RELEVANCE_TAGS: dict[str, Dialect] = {
    "relevance": Dialect.UNCERTAIN,
    "client_relevance": Dialect.CLIENT,
    "session_relevance": Dialect.SESSION,
}
"""Fence language tags that mark a code block as relevance, and the context
dialect each commits to.

``relevance`` names the language without committing to a dialect, the same
"no signal either way" position an untagged fence used to take; ``client_``/
``session_relevance`` commit, which is a real context signal a markdown fence
otherwise cannot carry at all -- there is no element or file type here for
:attr:`RelevanceSite.context_dialect` to read the way BES XML or an HTML
processing instruction can.
"""


def extract_relevance_from_markdown(text: str) -> list[RelevanceSite]:
    """Extract each relevance-tagged fenced code block of ``text`` as one statement.

    Only a fence tagged ```` ```relevance ````, ```` ```client_relevance ````, or
    ```` ```session_relevance ```` (case-insensitive) is extracted. Every other
    fence -- untagged, or tagged as some other language entirely (` ```python `,
    ` ```bash `, ...) -- is skipped, because most markdown in the wild fences
    plenty of things that are not relevance at all, and a fence carries no
    signal by default about what its contents even are, let alone which
    dialect. Requiring one of these three tags is how a document says "this
    one actually is relevance" rather than this module guessing from content
    alone and finding whatever else happens to parse.
    """
    return _markdown_sites(text)


def _markdown_sites(
    text: str, problems: list[_ExtractionProblem] | None = None
) -> list[RelevanceSite]:
    """:func:`extract_relevance_from_markdown`, adding an unclosed relevance
    fence to ``problems``.

    Only a relevance fence is a problem: CommonMark runs any unclosed fence to
    the end of the document, so the markdown is valid, but this extractor never
    reads a relevance fence it did not see closed.
    """
    sites: list[RelevanceSite] = []
    lines = text.split("\n")
    fence: str | None = None
    context_dialect = Dialect.UNCERTAIN
    extracting = False
    block: list[str] = []
    block_start = 0

    for line_number, line in enumerate(lines, start=1):
        match = _FENCE_RE.match(line)
        if fence is None:
            if match and match.group(2):
                fence = match.group(2)[0] * 3
                tag = match.group(3).strip().lower()
                context_dialect = _MARKDOWN_RELEVANCE_TAGS.get(tag, Dialect.UNCERTAIN)
                extracting = tag in _MARKDOWN_RELEVANCE_TAGS
                block = []
                block_start = line_number + 1
            continue

        if match and match.group(2).startswith(fence) and not match.group(3).strip():
            if extracting:
                joined = "\n".join(block)
                offset, body = _stripped(joined)
                if body:
                    sites.append(
                        _make_site(
                            kind="markdown-codeblock",
                            text=body,
                            line=block_start,
                            context="markdown code block",
                            context_dialect=context_dialect,
                            column=_column(joined, offset, 0, 0),
                        )
                    )
            fence = None
            continue

        if extracting:
            block.append(line)

    if fence is not None:
        logger.warning("unterminated markdown code fence opened at line %d", block_start - 1)
        if extracting and problems is not None:
            problems.append(
                _ExtractionProblem(
                    code="unterminated-code-fence",
                    line=block_start - 1,
                    message=_UNTERMINATED_FENCE_MESSAGE,
                    context="markdown code block",
                )
            )

    return sites


def _extract_plain_text(text: str, dialect: Dialect) -> list[RelevanceSite]:
    """Treat the whole of ``text`` as a single relevance statement."""
    offset, body = _stripped(text)
    if not body:
        return []
    return [
        _make_site(
            kind="plain-text",
            text=body,
            line=_line_of(text, offset),
            context="whole file",
            context_dialect=dialect,
            column=_column(text, offset, offset, 0),
        )
    ]


# ---------------------------------------------------------------------------
# BES XML extraction
# ---------------------------------------------------------------------------

# ActionScript that is not a Windows-Shell script (or has no MIMEType at all)
# is a different language whose braces are not relevance substitutions.
_ACTIONSCRIPT_MIMETYPES = frozenset({"application/x-fixlet-windows-shell"})


@dataclass(frozen=True, slots=True)
class _Element:
    """One XML element, flattened to what the extractor needs from it.

    The seam that keeps the walker independent of which parser produced it.
    """

    path: tuple[str, ...]
    attrib: dict[str, str]
    text: str

    line: int
    """1-based line the element's *body* starts on.

    Not necessarily the line its start tag opens on: for a start tag whose
    attributes span several lines, the body starts on the line the tag closes
    on. This is the line offsets inside the body are measured from, so getting
    it wrong shifts every reported line in the file.
    """

    source: _TextSource | None = None
    """Where :attr:`text` sits in the file's bytes, when the parser said."""

    @property
    def tag(self) -> str:
        return self.path[-1]


def _body_site(element: _Element, *, kind: SiteKind, context: str) -> list[RelevanceSite]:
    """The one client-relevance site an element's whole (stripped) body is,
    or none when the body is blank."""
    offset, body = _stripped(element.text)
    if not body:
        return []
    return [
        _make_site(
            kind=kind,
            text=body,
            line=element.line,
            context=context,
            context_dialect=Dialect.CLIENT,
            source_map=_site_map(element.source, offset, body),
        )
    ]


def _sites_for_element(
    element: _Element, problems: list[_ExtractionProblem] | None = None
) -> list[RelevanceSite]:
    """The relevance sites, if any, that one XML element contributes, adding
    any problem found on the way to ``problems``."""
    tag = element.tag
    text = element.text
    context = "/".join(element.path)

    if tag == "Relevance":
        return _body_site(element, kind="relevance", context=context)

    if tag == "SuccessCriteria":
        # Only Option="CustomRelevance" carries a relevance statement; the
        # other options are fixed behaviors with an empty body.
        if element.attrib.get("Option") != "CustomRelevance":
            return []
        return _body_site(element, kind="success-criteria", context=context)

    if tag == "Property":
        # `<Property>` is an analysis property only inside an Analysis; it
        # means something else elsewhere (e.g. inside a MIMEField).
        if "Analysis" not in element.path[:-1]:
            return []
        name = element.attrib.get("Name")
        return _body_site(
            element,
            kind="analysis-property",
            context=f'{context}[Name="{name}"]' if name else context,
        )

    if tag == "ActionScript":
        mimetype = element.attrib.get("MIMEType")
        if mimetype is not None and mimetype.lower() not in _ACTIONSCRIPT_MIMETYPES:
            logger.debug(
                "skipping ActionScript with MIMEType %r at line %d", mimetype, element.line
            )
            return []
        return _actionscript_sites(
            text,
            context=context,
            dialect=Dialect.CLIENT,
            line_offset=element.line - 1,
            source=element.source,
            problems=problems,
            column_offset=None,
        )

    if tag == "Description":
        # A Description is HTML rendered by the console, so relevance in it --
        # whether a static substitution or a JavaScript call -- is session
        # relevance, unlike everything else in a BES document.
        return [
            replace(site, context=f"{context}: {site.context}")
            for site in _html_sites(
                text,
                context=HtmlContext.CONSOLE,
                line_offset=element.line - 1,
                label=None,
                source=element.source,
                problems=problems,
                problem_context=context,
                column_offset=None,
            )
        ]

    return []


_RELEVANT_TAGS = frozenset(
    {"Relevance", "SuccessCriteria", "Property", "ActionScript", "Description"}
)


def _sites_from_elements(
    elements: Iterable[_Element], problems: list[_ExtractionProblem] | None = None
) -> list[RelevanceSite]:
    sites: list[RelevanceSite] = []
    for element in elements:
        sites.extend(_sites_for_element(element, problems))
    return sites


_REFERENCES = {b"lt": "<", b"gt": ">", b"amp": "&", b"quot": '"', b"apos": "'"}


def _reference(raw: bytes) -> str | None:
    """What the XML reference ``raw`` (``&lt;``, ``&#60;``, ``&#x3C;``) stands for."""
    name = raw[1:-1]
    if name.startswith(b"#"):
        try:
            code = int(name[2:], 16) if name[1:2] in (b"x", b"X") else int(name[1:])
            return chr(code)
        except (ValueError, OverflowError):
            return None
    return _REFERENCES.get(name)


def _raw_piece(data: bytes, index: int, text: str) -> tuple[int, bool] | None:
    """How many bytes at ``index`` the piece ``text`` was decoded from, and
    whether that piece is atomic (see :attr:`SourceSpan.atomic`).

    ``None`` when the bytes there are not recognizably ``text``: then the
    element gets no map at all, rather than one that might be wrong.
    """
    if index < 0:
        return None
    encoded = text.encode("utf-8")
    if data.startswith(encoded, index):
        return len(encoded), False
    if text == "\n":
        if data.startswith(b"\r\n", index):
            return 2, True
        if data.startswith(b"\r", index):
            return 1, True
    if data.startswith(b"&", index):
        end = data.find(b";", index, index + 12)
        if end != -1 and _reference(data[index : end + 1]) == text:
            return end + 1 - index, True
    return None


def _text_spans(data: bytes, pieces: Sequence[tuple[int, str]]) -> tuple[SourceSpan, ...] | None:
    """The spans of an element whose text arrived as ``pieces`` of ``(byte_index, text)``."""
    spans: list[SourceSpan] = []
    position = 0
    for index, text in pieces:
        if not text:
            continue
        raw = _raw_piece(data, index, text)
        if raw is None:
            return None
        length, atomic = raw
        spans.append(SourceSpan(position, position + len(text), index, index + length, atomic))
        position += len(text)
    return tuple(spans)


def _iter_elements_expat(
    data: bytes, *, mapped: bool = True, problems: list[_ExtractionProblem] | None = None
) -> Iterator[_Element]:
    """Walk ``data`` with stdlib expat, yielding the elements worth looking at.

    Character data arrives already decoded and with CDATA merged in, so a
    body's text is whatever the parser accumulated between its tags. Each
    piece arrives in its own callback, at its own byte index, which is what
    :attr:`_Element.source` is built from when ``mapped``.
    """
    collected: list[_Element] = []
    path: list[str] = []

    class _Frame:
        """An open element of interest: where its body starts and what is in it."""

        def __init__(self, tag_line: int, attrib: dict[str, str]) -> None:
            self.tag_line = tag_line
            self.attrib = attrib
            self.chunks: list[str] = []
            self.indexes: list[int] = []
            self.body_line: int | None = None

    open_frames: list[_Frame] = []

    parser = xml.parsers.expat.ParserCreate()
    # Buffering would coalesce the body into one callback reported at its *end*,
    # losing the line the body starts on.
    parser.buffer_text = False

    def start_element(name: str, attrib: dict[str, str]) -> None:
        path.append(name)
        if name in _RELEVANT_TAGS:
            open_frames.append(_Frame(parser.CurrentLineNumber, dict(attrib)))

    def character_data(data: str) -> None:
        if not open_frames:
            return
        frame = open_frames[-1]
        if frame.body_line is None:
            # `CurrentLineNumber` at a start-element event is the line the tag
            # *opens* on, which for a multi-line start tag is before the body.
            # The first character-data event is at the body itself.
            frame.body_line = parser.CurrentLineNumber
        frame.chunks.append(data)
        frame.indexes.append(parser.CurrentByteIndex)

    def end_element(name: str) -> None:
        if name in _RELEVANT_TAGS and open_frames:
            frame = open_frames.pop()
            collected.append(
                _Element(
                    path=tuple(path),
                    attrib=frame.attrib,
                    text="".join(frame.chunks),
                    # An empty element has no body to anchor to.
                    line=frame.body_line if frame.body_line is not None else frame.tag_line,
                    source=(_TextSource(data, frame.indexes, frame.chunks) if mapped else None),
                )
            )
        if path:
            path.pop()

    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = character_data

    try:
        parser.Parse(data, True)
    except xml.parsers.expat.ExpatError as error:
        # Document validity is not this package's job; a consumer that cares
        # runs a schema check. Report nothing rather than half a file.
        logger.warning("could not parse BES XML: %s", error)
        if problems is not None:
            problems.append(
                _ExtractionProblem(
                    code="xml-parse-error",
                    line=error.lineno,
                    message=(
                        f"the BES XML does not parse ({xml.parsers.expat.ErrorString(error.code)}"
                        f" at column {error.offset + 1}), so nothing in this file was linted"
                    ),
                    context="BES XML",
                )
            )
        return

    yield from collected


def _as_bytes(data: str | bytes) -> bytes:
    return data.encode("utf-8") if isinstance(data, str) else data


def extract_relevance_from_bes_xml(data: str | bytes) -> list[RelevanceSite]:
    """Extract every relevance statement from a BES XML document.

    Covers `<Relevance>` bodies, `<SuccessCriteria Option="CustomRelevance">`,
    analysis `<Property>` bodies, `{...}` substitutions in Windows-Shell
    `<ActionScript>` bodies, and session relevance embedded in `<Description>`
    HTML. Returns an empty list, having logged a warning, if the document
    cannot be parsed.
    """
    return _extract_bes_xml(data)[0]


def _extract_bes_xml(
    data: str | bytes,
) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
    """:func:`extract_relevance_from_bes_xml`, plus the problems found on the way."""
    problems: list[_ExtractionProblem] = []
    # A `str` is encoded before parsing, so offsets into it would describe
    # bytes the caller never had: only bytes get a map.
    sites = _sites_from_elements(
        _iter_elements_expat(_as_bytes(data), mapped=isinstance(data, bytes), problems=problems),
        problems,
    )
    return (
        sorted(sites, key=lambda site: site.line),
        sorted(problems, key=lambda problem: problem.line),
    )


def _lxml_record(element: etree._Element, path: tuple[str, ...]) -> _Element:
    """Flatten one lxml element into the same record expat produces.

    lxml's ``sourceline`` is the line an element's start tag *closes* on, which
    is the line its body starts on -- the same anchor the expat walker uses, so
    line numbers from the two agree even for a start tag spanning several lines.
    """
    source_line: object = element.sourceline
    if isinstance(source_line, int):
        line = source_line
    else:
        # `sourceline` is None for a tree built in memory rather than parsed
        # from a source, where there are no line numbers to report.
        logger.warning("lxml element <%s> has no source line; reporting line 0", element.tag)
        line = 0

    # `itertext` so a body split by entities or CDATA reads as the single string
    # expat accumulates. It can yield bytes for some node types.
    text = "".join(
        chunk if isinstance(chunk, str) else chunk.decode("utf-8", errors="replace")
        for chunk in element.itertext()
    )

    return _Element(
        path=path,
        attrib={str(key): str(value) for key, value in element.attrib.items()},
        text=text,
        line=line,
    )


def _iter_elements_lxml(tree: etree._ElementTree | etree._Element) -> Iterator[_Element]:
    """Walk an already-parsed lxml tree, yielding the same records as expat."""
    # Imported here, not at module scope: lxml is an optional extra, needed only
    # by callers that already hold a tree built with it.
    from lxml import etree as lxml_etree

    root = tree.getroot() if isinstance(tree, lxml_etree._ElementTree) else tree
    root_tag = root.tag if isinstance(root.tag, str) else ""

    def walk(element: etree._Element, path: tuple[str, ...]) -> Iterator[_Element]:
        for child in element:
            tag = child.tag
            if not isinstance(tag, str):  # comments and processing instructions
                continue
            child_path = (*path, tag)
            if tag in _RELEVANT_TAGS:
                yield _lxml_record(child, child_path)
            yield from walk(child, child_path)

    if root_tag in _RELEVANT_TAGS:
        yield _lxml_record(root, (root_tag,))
    yield from walk(root, (root_tag,))


def extract_relevance_from_lxml_tree(
    tree: etree._ElementTree | etree._Element,
) -> list[RelevanceSite]:
    """Extract relevance from a BES document already parsed with lxml.

    For projects that parse BES XML with lxml anyway and would rather not pay
    to parse it twice. Results, line numbers included, match
    :func:`extract_relevance_from_bes_xml` on the same document. Requires the
    optional ``lxml`` extra, but only for callers that hold an lxml tree --
    importing this module never needs it.
    """
    sites = _sites_from_elements(_iter_elements_lxml(tree))
    return sorted(sites, key=lambda site: site.line)


# ---------------------------------------------------------------------------
# Dispatch by file type
# ---------------------------------------------------------------------------

_BES_XML_SUFFIXES = frozenset({".bes"})
_CONSOLE_HTML_SUFFIXES = frozenset({".ojo", ".besrpt", ".beswrpt", ".webreport"})
_CLIENTUI_HTML_SUFFIXES = frozenset({".html", ".htm"})
_SESSION_TEXT_SUFFIXES = frozenset({".bsr"})
_UNTYPED_TEXT_SUFFIXES = frozenset({".rel"})
_MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})


def _significant_suffixes(path: Path) -> Sequence[str]:
    """Suffixes of ``path``, lowercased, innermost last.

    A `.bes.xml` file holds BES XML, so the whole suffix chain matters, not
    only the last one.
    """
    return [suffix.lower() for suffix in path.suffixes]


def _is_bes_xml(path: Path) -> bool:
    """Whether :func:`extract_relevance_from_file` reads ``path`` as BES XML."""
    return any(suffix in _BES_XML_SUFFIXES for suffix in _significant_suffixes(path))


_TEXT_SUFFIXES = (
    _CONSOLE_HTML_SUFFIXES
    | _CLIENTUI_HTML_SUFFIXES
    | _SESSION_TEXT_SUFFIXES
    | _UNTYPED_TEXT_SUFFIXES
    | _MARKDOWN_SUFFIXES
)

_RECOGNIZED_SUFFIXES: Final = tuple(sorted(_BES_XML_SUFFIXES | _TEXT_SUFFIXES))
"""Every suffix :func:`extract_relevance_from_file` reads, for messages."""


def _is_recognized(path: Path) -> bool:
    """Whether :func:`extract_relevance_from_file` has an extractor for ``path``.

    Decided from the name alone, so asking never opens the file -- which
    matters for a FIFO, where opening blocks until a writer appears.
    """
    suffixes = _significant_suffixes(path)
    return _is_bes_xml(path) or (bool(suffixes) and suffixes[-1] in _TEXT_SUFFIXES)


def extract_relevance_from_file(path: str | bytes | os.PathLike[str]) -> list[RelevanceSite]:
    """Extract every relevance statement from a file, keyed off its type.

    Recognizes BES XML (`.bes`, `.bes.xml`), console dashboards and web reports
    (`.ojo`, `.besrpt`, `.beswrpt`, `.webreport`), HTML (`.html`, `.htm`),
    whole-file relevance (`.bsr`, `.rel`) and markdown (`.md`) -- the latter
    only from fences explicitly tagged ```` ```relevance ````,
    ```` ```client_relevance ````, or ```` ```session_relevance ````; see
    :func:`extract_relevance_from_markdown`. Returns an empty list for a file
    type it does not recognize.

    `.html`/`.htm` gets no context dialect from the extension alone -- unlike
    `.ojo` or `.besrpt`, it does not say which side renders the document.
    :func:`looks_like_clientui` is checked first; a corroborating marker gets
    the ClientUI treatment, and otherwise the document's own mechanism (a
    JavaScript relevance call, if any) or the content classifier decides.
    """
    return _extract_file(_as_path(path))[0]


def _extract_file(file_path: Path) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
    """:func:`extract_relevance_from_file`, plus the problems found on the way.

    Problems are content this extractor could not read relevance out of: an
    unclosed ActionScript `{`, an unterminated `<?Relevance`, an unclosed
    relevance code fence, or BES XML that does not parse.

    An unrecognized type is never opened -- see :func:`_is_recognized` for why
    that matters.
    """
    if not _is_recognized(file_path):
        logger.debug("no relevance extractor for %s; skipping it", file_path.name)
        return [], []
    return _extract_data(file_path, file_path.read_bytes())


def _extract_data(
    file_path: Path, data: bytes
) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
    """:func:`_extract_file` over ``data`` rather than whatever is on disk.

    ``file_path`` only chooses the extractor, from its suffixes, and is never
    opened. This is how an editor buffer gets linted before it is saved.
    """
    if _is_bes_xml(file_path):
        return _extract_bes_xml(data)
    problems: list[_ExtractionProblem] = []
    sites = _extract_text(file_path, _decode_text(data), problems)
    return sites, sorted(problems, key=lambda problem: problem.line)


def _extract_text(
    file_path: Path, text: str, problems: list[_ExtractionProblem]
) -> list[RelevanceSite]:
    """:func:`_extract_data` for every type but BES XML."""
    suffixes = _significant_suffixes(file_path)
    last = suffixes[-1] if suffixes else ""

    if last in _CONSOLE_HTML_SUFFIXES:
        return _html_sites(
            text,
            context=HtmlContext.CONSOLE,
            line_offset=0,
            label=None,
            problems=problems,
        )

    if last in _CLIENTUI_HTML_SUFFIXES:
        # The extension alone does not say who renders this -- unlike `.ojo` or
        # `.besrpt`, a bare `.html` is also how a WebUI fragment, an exported
        # dashboard, or plain documentation would be named. A ClientUI marker
        # in the document is corroborating evidence worth trusting; without
        # one, only the content mechanism (a JS call, or the classifier on
        # what a static substitution says) gets to decide.
        context = HtmlContext.CLIENTUI if looks_like_clientui(text) else HtmlContext.UNKNOWN
        return _html_sites(text, context=context, line_offset=0, label=None, problems=problems)

    if last in _SESSION_TEXT_SUFFIXES:
        return _extract_plain_text(text, Dialect.SESSION)

    if last in _UNTYPED_TEXT_SUFFIXES:
        return _extract_plain_text(text, Dialect.UNCERTAIN)

    if last in _MARKDOWN_SUFFIXES:
        return _markdown_sites(text, problems)

    logger.debug("no relevance extractor for %s; skipping it", file_path.name)
    return []


def _decode_text(data: bytes) -> str:
    """``data`` as the text a text-mode read of the same file would give.

    BES content is UTF-8 in practice, but a stray byte in a hand-edited file
    should not lose the rest of the relevance in it. Line endings are folded
    exactly as ``Path.read_text`` folds them -- this replaced that call, and
    the lines every finding reports depend on it.
    """
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
