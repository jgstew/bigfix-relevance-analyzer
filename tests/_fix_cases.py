"""Files whose fix is easy to write back wrong, with the exact bytes the fix gives.

Shared on purpose. A fix travels two mappings: from offsets in a site's text to
the file's bytes (:func:`~bigfix_relevance_analyzer.fixfile.source_edits`,
#115), and from those bytes to an editor's line and UTF-16 character (the
language server's quick fixes, #113). Both are held to these same inputs --
line endings of every kind, an astral character before the fix, a byte order
mark, entities, CDATA, escaped JavaScript quotes -- so neither side can pass on
easier cases than the other.

Each :attr:`FixCase.fixed` is :attr:`FixCase.data` with only the new text
inserted: everything the author wrote stays byte for byte. Non-ASCII is written
as escapes, never literally: this repo's pre-commit rewrites literal non-ASCII
in tests to ``?``.
"""

from __future__ import annotations

from dataclasses import dataclass

SETTING = b'exists values of setting "x" of client'
SETTINGS = b'exists values of settings "x" of client'
BOM = b"\xef\xbb\xbf"
ASTRAL = "\U0001f600".encode()  # 4 bytes, 1 code point, 2 UTF-16 units

_HEAD = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    b"\t<Task>\n"
    b"\t\t<Title>t</Title>\n"
)
_TAIL = b"\t</Task>\n</BES>\n"


def task(*lines: bytes) -> bytes:
    """A BES task with ``lines`` in it, each on its own tab-indented line."""
    return _HEAD + b"".join(b"\t\t" + line + b"\n" for line in lines) + _TAIL


def _action(script: bytes) -> bytes:
    return task(
        b'<DefaultAction ID="Action1">',
        b'<ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
        + script
        + b"</ActionScript>",
        b"</DefaultAction>",
    )


WRAP = b"unique value of "
LT_OPERAND = b'pathnames of files whose (size of it &lt; 5) of folder "x"'
MERGED = b'names of files of folder "a" of folder "b" = "y"'
MERGED_FIXED = b'unique value of names of files of folders "a" of folder "b" = "y"'
SESSION = b'names of bes computers | "y"'
SESSION_FIXED = WRAP + SESSION


@dataclass(frozen=True, slots=True)
class FixCase:
    id: str
    name: str
    """The file name; its suffix picks the extractor."""
    data: bytes
    fixed: bytes
    sites: int = 1
    """How many sites the fix applies to."""


CASES: tuple[FixCase, ...] = (
    # -- BES XML: through the source map -------------------------------------
    FixCase(
        "bes-wrap-over-lt",
        "t.bes",
        task(b"<Relevance>" + LT_OPERAND + b' | "y"</Relevance>'),
        task(b"<Relevance>" + WRAP + LT_OPERAND + b' | "y"</Relevance>'),
    ),
    FixCase(
        "bes-wrap-over-quot",
        "t.bes",
        task(b"<Relevance>pathnames of files &quot;x&quot; | &quot;y&quot;</Relevance>"),
        task(
            b"<Relevance>" + WRAP + b"pathnames of files &quot;x&quot; | &quot;y&quot;</Relevance>"
        ),
    ),
    FixCase(
        "bes-name-split-by-cdata",
        "t.bes",
        task(b'<Relevance>exists values of sett<![CDATA[ing]]> "x" of client</Relevance>'),
        task(b'<Relevance>exists values of sett<![CDATA[ing]]>s "x" of client</Relevance>'),
    ),
    FixCase(
        "bes-substitution-wrap-over-lt",
        "t.bes",
        _action(b'parameter "v"="{' + LT_OPERAND + b' | "y"}"'),
        _action(b'parameter "v"="{' + WRAP + LT_OPERAND + b' | "y"}"'),
    ),
    FixCase(
        "bes-merged-wrap-and-respelling",
        "t.bes",
        task(b"<Relevance>" + MERGED + b"</Relevance>"),
        task(b"<Relevance>" + MERGED_FIXED + b"</Relevance>"),
    ),
    FixCase(
        "bes-crlf",
        "t.bes",
        task(b"<Relevance>true and\r\n" + SETTING + b"</Relevance>").replace(b"\n", b"\r\n"),
        task(b"<Relevance>true and\r\n" + SETTINGS + b"</Relevance>").replace(b"\n", b"\r\n"),
    ),
    # -- whole-file relevance: through line and column -----------------------
    FixCase("rel", "t.rel", SETTING + b"\n", SETTINGS + b"\n"),
    FixCase("bsr-wrap", "t.bsr", SESSION + b"\n", SESSION_FIXED + b"\n"),
    FixCase(
        "rel-crlf",
        "t.rel",
        b"true and\r\n" + SETTING + b"\r\n",
        b"true and\r\n" + SETTINGS + b"\r\n",
    ),
    FixCase(
        "rel-cr-only", "t.rel", b"true and\r" + SETTING + b"\r", b"true and\r" + SETTINGS + b"\r"
    ),
    FixCase(
        "rel-astral-before-the-fix-crlf",
        "t.rel",
        b"/* " + ASTRAL + b" */ " + SETTING + b"\r\n",
        b"/* " + ASTRAL + b" */ " + SETTINGS + b"\r\n",
    ),
    FixCase(
        # The fix is on line 1, behind the BOM. VS Code strips the BOM from its
        # buffer (and keeps it on disk), so the editor plans against these
        # bytes without it; both must come out right.
        "rel-bom-line-1",
        "t.rel",
        BOM + b"(" + SETTING + b")\n",
        BOM + b"(" + SETTINGS + b")\n",
    ),
    # -- markdown fences -----------------------------------------------------
    FixCase(
        "md-two-fences-from-line-3",
        "t.md",
        b"# T\n\n```relevance\n" + SETTING + b"\n```\n\n```relevance\n" + SETTING + b"\n```\n",
        b"# T\n\n```relevance\n" + SETTINGS + b"\n```\n\n```relevance\n" + SETTINGS + b"\n```\n",
        sites=2,
    ),
    FixCase(
        "md-crlf",
        "t.md",
        b"# T\r\n\r\n```relevance\r\n" + SETTING + b"\r\n```\r\n",
        b"# T\r\n\r\n```relevance\r\n" + SETTINGS + b"\r\n```\r\n",
    ),
    FixCase(
        "md-mixed-line-endings",
        "t.md",
        b"# T\r\n\n```relevance\r" + SETTING + b"\n```\r\n",
        b"# T\r\n\n```relevance\r" + SETTINGS + b"\n```\r\n",
    ),
    # -- HTML family ---------------------------------------------------------
    FixCase(
        "ojo-two-identical-pis-on-one-line",
        "t.ojo",
        b"<p><?Relevance " + SESSION + b" ?> and <?Relevance " + SESSION + b" ?></p>\n",
        b"<p><?Relevance " + SESSION_FIXED + b" ?> and <?Relevance " + SESSION_FIXED + b" ?></p>\n",
        sites=2,
    ),
    FixCase(
        "html-js-call-single-quotes",
        "t.html",
        b"<script>Relevance('" + SESSION + b"')</script>\n",
        b"<script>Relevance('" + SESSION_FIXED + b"')</script>\n",
    ),
    FixCase(
        "html-js-call-escaped-quotes",
        "t.html",
        b'<script>Relevance("names of bes computers | \\"y\\"")</script>\n',
        b'<script>Relevance("unique value of names of bes computers | \\"y\\"")</script>\n',
    ),
)
