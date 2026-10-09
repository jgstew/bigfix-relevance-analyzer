"""Where a finding's span sits in an editor's buffer, with no protocol in it.

A :class:`~bigfix_relevance_analyzer.lint.TextSpan` is an offset into a site's
text: decoded, stripped, and for BES XML with its entities and CDATA already
resolved. An editor wants a line and a character in the buffer it holds --
line endings, entities and all -- with characters counted in UTF-16 code units,
LSP's default. :class:`DocumentIndex` makes that move once per document, by one
of two routes:

* **BES XML read through expat** has a
  :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.source_map`, which
  gives the span's bytes in the file. Those become a line and character
  through a per-document index of where each line's bytes start.
* **Every text extractor** (``.rel``, ``.bsr``, markdown, HTML, JavaScript
  calls, ActionScript) records the
  :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.column` its text
  starts at on :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.line`.
  A span goes through line and column rather than an offset into the
  document, because the text was read with ``\\r\\n`` folded to ``\\n``:
  offsets drift in a CRLF file, lines and columns do not.

Hover needs the opposite move, from a position in the buffer to an offset in
a site's text: :meth:`DocumentIndex.site_offset`, by the same two routes run
backwards. Whatever offset it finds is mapped forward again and kept only if
that range covers the position, so the way back can never disagree with the
way there.

On the second route the buffer is read back at the range found and compared
with the span's text; any difference means the range is ``None``. That catches
a replacement character where the buffer's bytes did not decode, and any
extractor that turned out not to keep text as written. ``None`` always means
"fall back to the whole line": a wrong underline is worse than a wide one.

Runs in WASM, like the rest of the editor layer: UTF-8 is the only codec used,
and UTF-16 lengths are counted, never encoded.
"""

from __future__ import annotations

import bisect
import re
from collections.abc import Iterable
from typing import Final

from bigfix_relevance_analyzer.extract import RelevanceSite
from bigfix_relevance_analyzer.lint import TextSpan

Position = tuple[int, int]
"""``(line, character)``: both 0-based, the character in UTF-16 code units."""

Range = tuple[Position, Position]
"""``(start, end)``, end exclusive, as LSP's ``Range`` is."""

_LINE_BREAK: Final = re.compile(r"\r\n|\r|\n")
"""What LSP counts as a line break -- only these, unlike :meth:`str.splitlines`,
which also breaks on form feeds and Unicode separators a client does not."""

_BYTE_LINE_BREAK: Final = re.compile(rb"\r\n|\r|\n")


def utf16_length(text: str) -> int:
    """``text``'s length in UTF-16 code units: two for an astral character.

    Counted rather than encoded on purpose. A WASM host has only the codecs its
    build snapshot saw, and ``str.encode("utf-16-le")`` raised ``LookupError``
    inside a componentize-py component, losing every diagnostic.
    """
    return len(text) + sum(1 for char in text if ord(char) > 0xFFFF)


class DocumentIndex:
    """One editor buffer, indexed to turn spans of its sites into ranges.

    Built once per lint of a document: the line split is shared by every
    finding, and the byte index only built if a BES site asks for it.
    """

    def __init__(self, text: str, data: bytes) -> None:
        """``text`` is the buffer; ``data`` the bytes it was linted as, its UTF-8."""
        self.text = text
        self.data = data
        self.lines: list[str] = []
        """The buffer's lines, split where LSP splits them, without their breaks."""
        self._starts: list[int] = []
        position = 0
        for match in _LINE_BREAK.finditer(text):
            self._starts.append(position)
            self.lines.append(text[position : match.start()])
            position = match.end()
        self._starts.append(position)
        self.lines.append(text[position:])
        self._byte_starts: list[int] | None = None

    def line_length(self, line: int) -> int:
        """Line ``line``'s length in UTF-16 code units; 0 past the end."""
        return utf16_length(self.lines[line]) if 0 <= line < len(self.lines) else 0

    def site_range(self, site: RelevanceSite, span: TextSpan) -> Range | None:
        """Where ``span`` of ``site.text`` is in the buffer, or ``None`` if unsure.

        An empty span -- a parse error at the end of the statement -- covers
        the character after it, or the one before it at the end: a point is
        not something every client draws.
        """
        widened = _widen(site.text, span)
        if widened is None:
            return None
        start, end = widened
        if site.source_map is not None:
            return self._mapped_range(site, start, end)
        if site.column is not None:
            return self._text_range(site, start, end)
        return None

    def site_offset(self, site: RelevanceSite, position: Position) -> int | None:
        """The offset in ``site.text`` of the character at ``position``, or ``None``.

        ``None`` when the position is not on a character of the site -- in the
        markup around it, past a line's end, on another line -- or when the
        character there cannot be placed for certain. Every character of an
        entity such as ``&gt;`` is the one character it stands for, and either
        half of a surrogate pair is the astral character it encodes.
        """
        point = self._point(position)
        if point is None:
            return None
        return self._offset_at(site, position, point, self._byte_at(*point))

    def locate(
        self, sites: Iterable[RelevanceSite], position: Position
    ) -> tuple[RelevanceSite, int] | None:
        """The first of ``sites`` with a character at ``position``, and its offset.

        The position is resolved once, and a site that cannot hold it is
        skipped without mapping: a BES site by its source map's bytes, a text
        site by the lines its text spans. Not by a BES site's ``line``, which an
        encoded line feed can shift (#111); the bytes are exact.
        """
        point = self._point(position)
        if point is None:
            return None
        line, _ = point
        byte: int | None = None
        for site in sites:
            if site.source_map is not None:
                if byte is None:
                    byte = self._byte_at(*point)
                spans = site.source_map.spans
                if not spans or not spans[0].raw_start <= byte < spans[-1].raw_end:
                    continue
            elif site.column is not None:
                first = site.line - 1
                if line < first or line > first + site.text.count("\n"):
                    continue
            offset = self._offset_at(site, position, point, byte)
            if offset is not None:
                return site, offset
        return None

    def _point(self, position: Position) -> tuple[int, int] | None:
        """``(line, code point index in it)`` of ``position``, if it is on a character."""
        line, character = position
        if not 0 <= line < len(self.lines):
            return None
        index = _code_point_at(self.lines[line], character)
        return None if index is None else (line, index)

    def _offset_at(
        self, site: RelevanceSite, position: Position, point: tuple[int, int], byte: int | None
    ) -> int | None:
        """:meth:`site_offset` for a resolved ``point``; ``byte`` is its byte
        offset when known (a BES site needs it, and works it out otherwise)."""
        if site.source_map is not None:
            offset = self._mapped_offset(site, byte if byte is not None else self._byte_at(*point))
        elif site.column is not None:
            offset = self._text_offset(site, *point)
        else:
            return None
        if offset is None:
            return None
        # The guard: the forward mapping of what was found must cover `position`.
        found = self.site_range(site, TextSpan(offset, offset + 1))
        if found is None or not found[0] <= position < found[1]:
            return None
        return offset

    # -- BES XML: through the source map's bytes ---------------------------

    def _mapped_range(self, site: RelevanceSite, start: int, end: int) -> Range | None:
        assert site.source_map is not None
        raw = site.source_map.raw_range(start, end)
        if raw is None:
            return None
        first = self._byte_position(raw[0])
        last = self._byte_position(raw[1])
        if first is None or last is None:
            return None
        return first, last

    def _line_byte_starts(self) -> list[int]:
        if self._byte_starts is None:
            self._byte_starts = [
                0,
                *(match.end() for match in _BYTE_LINE_BREAK.finditer(self.data)),
            ]
        return self._byte_starts

    def _byte_position(self, offset: int) -> Position | None:
        starts = self._line_byte_starts()
        if not 0 <= offset <= len(self.data):
            return None
        line = bisect.bisect_right(starts, offset) - 1
        try:
            prefix = self.data[starts[line] : offset].decode("utf-8")
        except UnicodeDecodeError:
            # Mid-character, or bytes that are not the buffer's text.
            return None
        if line >= len(self.lines) or not self.lines[line].startswith(prefix):
            return None
        return line, utf16_length(prefix)

    def _byte_at(self, line: int, index: int) -> int:
        """The byte offset of code point ``index`` of ``line``, in :attr:`data`."""
        starts = self._line_byte_starts()
        if line >= len(starts):
            # Not this buffer's bytes (a caller-built index): matches no source map.
            return -1
        prefix = self.lines[line][:index].encode("utf-8", errors="surrogatepass")
        return starts[line] + len(prefix)

    def _mapped_offset(self, site: RelevanceSite, byte: int) -> int | None:
        """The offset in ``site.text`` whose bytes hold byte ``byte`` of the file."""
        assert site.source_map is not None
        for span in site.source_map.spans:
            if not span.raw_start <= byte < span.raw_end:
                continue
            if span.atomic:
                return span.start
            position = span.raw_start
            for offset in range(span.start, span.end):
                position += _utf8_length(site.text[offset])
                if byte < position:
                    return offset
        return None

    # -- Text extractors: through the site's line and column ----------------

    def _text_range(self, site: RelevanceSite, start: int, end: int) -> Range | None:
        first = self._text_point(site, start)
        last = self._text_point(site, end)
        if first is None or last is None:
            return None
        # The guard: the buffer over this range must be the span's text.
        written = self.text[self._starts[first[0]] + first[1] : self._starts[last[0]] + last[1]]
        if _LINE_BREAK.sub("\n", written) != site.text[start:end]:
            return None
        return (
            (first[0], utf16_length(self.lines[first[0]][: first[1]])),
            (last[0], utf16_length(self.lines[last[0]][: last[1]])),
        )

    def _text_offset(self, site: RelevanceSite, line: int, index: int) -> int | None:
        """The offset in ``site.text`` written at code point ``index`` of ``line``:
        :meth:`_text_point` backwards."""
        assert site.column is not None
        relative = line - (site.line - 1)
        if relative < 0:
            return None
        start = 0
        for _ in range(relative):
            start = site.text.find("\n", start) + 1
            if start == 0:
                return None
        end = site.text.find("\n", start)
        if end == -1:
            end = len(site.text)
        offset = start + index - (site.column - 1 if relative == 0 else 0)
        return offset if start <= offset < end else None

    def _text_point(self, site: RelevanceSite, offset: int) -> tuple[int, int] | None:
        """``(line, code point index in it)`` of ``site.text[offset]`` in the buffer."""
        assert site.column is not None
        relative = site.text.count("\n", 0, offset)
        in_line = offset - (site.text.rfind("\n", 0, offset) + 1)
        line = site.line - 1 + relative
        index = (site.column - 1 if relative == 0 else 0) + in_line
        if not 0 <= line < len(self.lines) or index > len(self.lines[line]):
            return None
        return line, index


def _code_point_at(line: str, character: int) -> int | None:
    """The index in ``line`` of the code point UTF-16 unit ``character`` is in,
    or ``None`` past its end. Either half of a surrogate pair is its character."""
    units = 0
    for index, char in enumerate(line):
        units += 2 if ord(char) > 0xFFFF else 1
        if character < units:
            return index if character >= 0 else None
    return None


def _utf8_length(char: str) -> int:
    """How many bytes UTF-8 spends on ``char``, counted rather than encoded."""
    code = ord(char)
    return 1 if code < 0x80 else 2 if code < 0x800 else 3 if code < 0x10000 else 4


def _widen(text: str, span: TextSpan) -> tuple[int, int] | None:
    """``span`` as a non-empty ``(start, end)`` within ``text``, or ``None``."""
    start, end = span.start, span.end
    if not 0 <= start <= end <= len(text):
        return None
    if start < end:
        return start, end
    if start < len(text) and text[start] != "\n":
        return start, start + 1
    if start > 0 and text[start - 1] != "\n":
        return start - 1, start
    return None
