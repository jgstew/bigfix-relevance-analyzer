"""Find the relevance statements in BigFix content.

Extracts every relevance statement from BES XML documents, console dashboards
and web reports, ClientUI dashboards, plain-relevance files, and markdown code
blocks, recording where each one came from and which dialect it is written in.

Dialect comes from **context** -- which element, of which kind of file, a
statement was found in -- not from the relevance itself. Guessing a dialect
from the inspectors a statement uses is a separate seam,
:func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`, which
has no opinion yet; when it grows one it fills in only sites that context left
:attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN`.

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
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect

if TYPE_CHECKING:  # pragma: no cover - typing only
    from lxml import etree

__all__ = [
    "HtmlContext",
    "RelevanceSite",
    "SiteKind",
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
    "relevance-pi",
    "javascript-call",
    "plain-text",
    "markdown-codeblock",
]


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
    """Which relevance dialect the statement is written in."""


class HtmlContext(enum.Enum):
    """Where an HTML document holding relevance gets rendered.

    This is what decides the dialect of a static ``<?Relevance ?>``
    substitution, since the syntax is identical in both places.
    """

    CONSOLE = "console"
    """Console dashboard, web report or WebUI: substitutions are session relevance."""

    CLIENTUI = "clientui"
    """ClientUI dashboard, rendered by the BES Client: substitutions are client relevance."""


# ---------------------------------------------------------------------------
# ActionScript `{...}` substitution scanner
# ---------------------------------------------------------------------------

# `createfile until X` / `appendfile until X` open a heredoc: every following
# line up to a line that is exactly `X` is literal file content, so braces in
# it are not relevance substitutions.
_HEREDOC_RE = re.compile(r"^\s*(?:create|append)file\s+until\s+(\S+)\s*$", re.IGNORECASE)


def _iter_substitution_spans(body: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line, relevance_text)`` for each `{...}` substitution in ``body``.

    Handles `{{`/`}}` literal-brace escapes, ignores `}` inside a relevance
    string literal, and skips heredoc content entirely.
    """
    lines = body.split("\n")
    heredoc_terminator: str | None = None

    # Offset of the start of each line within `body`, so a substitution that
    # spans lines can be scanned as one string while still reporting the line
    # it opened on.
    index = 0
    for line_number, line in enumerate(lines, start=1):
        line_start = index
        index += len(line) + 1

        if heredoc_terminator is not None:
            if line.strip() == heredoc_terminator:
                heredoc_terminator = None
            continue

        heredoc_match = _HEREDOC_RE.match(line)
        if heredoc_match:
            heredoc_terminator = heredoc_match.group(1)
            continue

        column = 0
        while column < len(line):
            brace = line.find("{", column)
            if brace == -1:
                break
            if line.startswith("{{", brace):
                column = brace + 2
                continue

            end = _find_substitution_end(body, line_start + brace + 1)
            if end is None:
                logger.warning(
                    "unterminated relevance substitution opened at line %d; skipping it",
                    line_number,
                )
                return

            text = body[line_start + brace + 1 : end].strip()
            if text:
                yield line_number, text
            else:
                logger.debug("empty relevance substitution at line %d", line_number)

            if end < line_start + len(line):
                column = end + 1 - line_start
            else:
                # The substitution ran past this line; resume scanning from the
                # line the closing brace landed on.
                break


def _find_substitution_end(body: str, start: int) -> int | None:
    """Index of the `}` closing a substitution opened just before ``start``."""
    position = start
    in_string = False
    while position < len(body):
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
) -> list[RelevanceSite]:
    """Extract the `{...}` relevance substitutions from an ActionScript body.

    Lines are 1-based within ``body``; a caller that knows where the body sits
    in a file adds its own offset. ActionScript runs on the endpoint, so
    substitutions in it are client relevance.
    """
    return [
        RelevanceSite(
            kind="actionscript-substitution",
            text=text,
            line=line,
            context=context,
            dialect=dialect,
        )
        for line, text in _iter_substitution_spans(body)
    ]


# ---------------------------------------------------------------------------
# HTML / text scanner: <?Relevance ?> and JavaScript relevance calls
# ---------------------------------------------------------------------------

_PI_OPEN_RE = re.compile(r"<\?relevance\b", re.IGNORECASE)

# `Relevance(` or `EvaluateRelevance(`, but not when it is the tail of a longer
# identifier or a property access (`bigfix.relevance.errorWrapper`).
_JS_CALL_RE = re.compile(r"(?<![\w.$])(?:Evaluate)?Relevance\s*\(")

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


def _iter_pi_spans(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line, relevance_text)`` for each `<?Relevance ?>` in ``text``."""
    for match in _PI_OPEN_RE.finditer(text):
        end = text.find("?>", match.end())
        if end == -1:
            logger.warning(
                "unterminated <?Relevance ?> processing instruction at line %d; skipping it",
                _line_of(text, match.start()),
            )
            continue
        body = text[match.end() : end].strip()
        if body:
            yield _line_of(text, match.start()), body
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


def _iter_js_call_spans(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line, relevance_text)`` for each JS relevance call in ``text``.

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

        body, end = literal
        # Anything other than `)` or `,` after the literal means the argument
        # was an expression the literal is only part of (e.g. `'x ' + query`).
        tail = text[end:].lstrip(" \t")
        if not tail.startswith((")", ",")):
            logger.debug(
                "relevance call at line %d concatenates its argument; skipping it",
                _line_of(text, match.start()),
            )
            continue

        body = body.strip()
        if body:
            yield _line_of(text, match.start()), body


def extract_relevance_from_html_text(
    text: str,
    *,
    context: HtmlContext,
    line_offset: int = 0,
    label: str | None = None,
) -> list[RelevanceSite]:
    """Extract relevance from an HTML/text document, in document order.

    ``context`` decides the dialect of static `<?Relevance ?>` substitutions:
    session relevance in a console dashboard or web report, client relevance in
    a ClientUI dashboard. JavaScript relevance calls are always session
    relevance -- a ClientUI cannot evaluate relevance from JavaScript, so such
    a call is itself proof the document is not one. When a document contains
    both mechanisms the signals contradict each other, and substitutions are
    reported as :attr:`Dialect.UNCERTAIN` rather than assumed to be client
    relevance.

    ``line_offset`` is added to every line, for scanning a fragment embedded in
    a larger file.
    """
    pi_spans = list(_iter_pi_spans(text))
    js_spans = list(_iter_js_call_spans(text))

    if context is HtmlContext.CLIENTUI and js_spans:
        pi_dialect = Dialect.UNCERTAIN
        logger.debug(
            "ClientUI document also evaluates relevance from JavaScript; "
            "treating its substitutions as an uncertain dialect"
        )
    elif context is HtmlContext.CLIENTUI:
        pi_dialect = Dialect.CLIENT
    else:
        pi_dialect = Dialect.SESSION

    pi_label = label or (
        "ClientUI HTML relevance substitution"
        if context is HtmlContext.CLIENTUI
        else "HTML relevance substitution"
    )
    js_label = label or "JavaScript relevance call"

    sites = [
        RelevanceSite(
            kind="relevance-pi",
            text=body,
            line=line + line_offset,
            context=pi_label,
            dialect=pi_dialect,
        )
        for line, body in pi_spans
    ]
    sites += [
        RelevanceSite(
            kind="javascript-call",
            text=body,
            line=line + line_offset,
            context=js_label,
            dialect=Dialect.SESSION,
        )
        for line, body in js_spans
    ]
    return sorted(sites, key=lambda site: site.line)


# ---------------------------------------------------------------------------
# Markdown and plain relevance files
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def extract_relevance_from_markdown(text: str) -> list[RelevanceSite]:
    """Extract each fenced code block of ``text`` as one relevance statement.

    A markdown fence carries no signal about which dialect its contents is, so
    every site is :attr:`Dialect.UNCERTAIN` unless the content classifier has
    an opinion.
    """
    sites: list[RelevanceSite] = []
    lines = text.split("\n")
    fence: str | None = None
    block: list[str] = []
    block_start = 0

    for line_number, line in enumerate(lines, start=1):
        match = _FENCE_RE.match(line)
        if fence is None:
            if match and match.group(2):
                fence = match.group(2)[0] * 3
                block = []
                block_start = line_number + 1
            continue

        if match and match.group(2).startswith(fence) and not match.group(3).strip():
            body = "\n".join(block).strip()
            if body:
                sites.append(
                    RelevanceSite(
                        kind="markdown-codeblock",
                        text=body,
                        line=block_start,
                        context="markdown code block",
                        dialect=_resolve(Dialect.UNCERTAIN, body),
                    )
                )
            fence = None
            continue

        block.append(line)

    if fence is not None:
        logger.warning("unterminated markdown code fence opened at line %d", block_start - 1)

    return sites


def _extract_plain_text(text: str, dialect: Dialect) -> list[RelevanceSite]:
    """Treat the whole of ``text`` as a single relevance statement."""
    body = text.strip()
    if not body:
        return []
    return [
        RelevanceSite(
            kind="plain-text",
            text=body,
            line=_line_of(text, len(text) - len(text.lstrip())),
            context="whole file",
            dialect=_resolve(dialect, body),
        )
    ]


def _resolve(from_context: Dialect, text: str) -> Dialect:
    """Settle a site's dialect: definite context wins, else ask the classifier.

    The classifier has no opinion today, so this currently always returns
    ``from_context``. Wiring it here means implementing content-based typing
    later needs no change to the extractors.
    """
    if from_context is not Dialect.UNCERTAIN:
        return from_context
    return classify_relevance_dialect(text) or Dialect.UNCERTAIN


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

    @property
    def tag(self) -> str:
        return self.path[-1]


def _sites_for_element(element: _Element) -> list[RelevanceSite]:
    """The relevance sites, if any, that one XML element contributes."""
    tag = element.tag
    text = element.text
    context = "/".join(element.path)

    if tag == "Relevance":
        body = text.strip()
        if not body:
            return []
        return [
            RelevanceSite(
                kind="relevance",
                text=body,
                line=element.line,
                context=context,
                dialect=Dialect.CLIENT,
            )
        ]

    if tag == "SuccessCriteria":
        # Only Option="CustomRelevance" carries a relevance statement; the
        # other options are fixed behaviors with an empty body.
        if element.attrib.get("Option") != "CustomRelevance":
            return []
        body = text.strip()
        if not body:
            return []
        return [
            RelevanceSite(
                kind="success-criteria",
                text=body,
                line=element.line,
                context=context,
                dialect=Dialect.CLIENT,
            )
        ]

    if tag == "Property":
        # `<Property>` is an analysis property only inside an Analysis; it
        # means something else elsewhere (e.g. inside a MIMEField).
        if "Analysis" not in element.path[:-1]:
            return []
        body = text.strip()
        if not body:
            return []
        name = element.attrib.get("Name")
        return [
            RelevanceSite(
                kind="analysis-property",
                text=body,
                line=element.line,
                context=f'{context}[Name="{name}"]' if name else context,
                dialect=Dialect.CLIENT,
            )
        ]

    if tag == "ActionScript":
        mimetype = element.attrib.get("MIMEType")
        if mimetype is not None and mimetype.lower() not in _ACTIONSCRIPT_MIMETYPES:
            logger.debug(
                "skipping ActionScript with MIMEType %r at line %d", mimetype, element.line
            )
            return []
        return [
            replace(site, line=site.line + element.line - 1, context=context)
            for site in extract_relevance_from_actionscript(text)
        ]

    if tag == "Description":
        # A Description is HTML rendered by the console, so relevance in it --
        # whether a static substitution or a JavaScript call -- is session
        # relevance, unlike everything else in a BES document.
        return [
            replace(site, context=f"{context}: {site.context}")
            for site in extract_relevance_from_html_text(
                text, context=HtmlContext.CONSOLE, line_offset=element.line - 1
            )
        ]

    return []


_RELEVANT_TAGS = frozenset(
    {"Relevance", "SuccessCriteria", "Property", "ActionScript", "Description"}
)


def _sites_from_elements(elements: Iterable[_Element]) -> list[RelevanceSite]:
    sites: list[RelevanceSite] = []
    for element in elements:
        sites.extend(_sites_for_element(element))
    return sites


def _iter_elements_expat(data: bytes) -> Iterator[_Element]:
    """Walk ``data`` with stdlib expat, yielding the elements worth looking at.

    Character data arrives already decoded and with CDATA merged in, so a
    body's text is whatever the parser accumulated between its tags.
    """
    collected: list[_Element] = []
    path: list[str] = []

    class _Frame:
        """An open element of interest: where its body starts and what is in it."""

        def __init__(self, tag_line: int, attrib: dict[str, str]) -> None:
            self.tag_line = tag_line
            self.attrib = attrib
            self.chunks: list[str] = []
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
    sites = _sites_from_elements(_iter_elements_expat(_as_bytes(data)))
    return sorted(sites, key=lambda site: site.line)


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


def extract_relevance_from_file(path: str | bytes | os.PathLike[str]) -> list[RelevanceSite]:
    """Extract every relevance statement from a file, keyed off its type.

    Recognizes BES XML (`.bes`, `.bes.xml`), console dashboards and web reports
    (`.ojo`, `.besrpt`, `.beswrpt`, `.webreport`), ClientUI dashboards
    (`.html`, `.htm`), whole-file relevance (`.bsr`, `.rel`) and markdown
    (`.md`). Returns an empty list for a file type it does not recognize.
    """
    file_path = Path(os.fsdecode(path))
    suffixes = _significant_suffixes(file_path)
    last = suffixes[-1] if suffixes else ""

    if any(suffix in _BES_XML_SUFFIXES for suffix in suffixes):
        return extract_relevance_from_bes_xml(file_path.read_bytes())

    if last in _CONSOLE_HTML_SUFFIXES:
        return extract_relevance_from_html_text(_read_text(file_path), context=HtmlContext.CONSOLE)

    if last in _CLIENTUI_HTML_SUFFIXES:
        return extract_relevance_from_html_text(_read_text(file_path), context=HtmlContext.CLIENTUI)

    if last in _SESSION_TEXT_SUFFIXES:
        return _extract_plain_text(_read_text(file_path), Dialect.SESSION)

    if last in _UNTYPED_TEXT_SUFFIXES:
        return _extract_plain_text(_read_text(file_path), Dialect.UNCERTAIN)

    if last in _MARKDOWN_SUFFIXES:
        return extract_relevance_from_markdown(_read_text(file_path))

    logger.debug("no relevance extractor for %s; skipping it", file_path.name)
    return []


def _read_text(path: Path) -> str:
    # BES content is UTF-8 in practice, but a stray byte in a hand-edited file
    # should not lose the rest of the relevance in it.
    return path.read_text(encoding="utf-8", errors="replace")
