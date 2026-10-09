"""Write safe fixes back into the files they were found in.

:mod:`~bigfix_relevance_analyzer.autofix` works out the fixed statement;
this module puts it back where the statement was written, changing nothing
else in the file:

    from bigfix_relevance_analyzer.fixfile import fix_paths
    from bigfix_relevance_analyzer.lint import LintConfig

    result = fix_paths(changed_paths, LintConfig())
    for fix in result.applied:
        print(f"{fix.path}:{fix.line}: {fix.autofix.fixed}")
    for fix in result.unapplied:
        print(f"{fix.path}:{fix.line}: not fixed: {fix.reason}")

A site's text is decoded and stripped, so it cannot be searched for in the
file. Instead each of the fix's :attr:`~bigfix_relevance_analyzer.autofix.AutofixResult.edits`
is split into the smallest pieces that make it -- a wrap is an insertion of
``unique value of ``, a respelling ``+s`` -- and each piece is mapped to the
exact bytes it goes in at. BES XML maps through the site's
:attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.source_map`; every
other file type through the site's line and
:attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.column`, checked
against the bytes found there. A piece only ever writes new text, never
anything copied from the statement, so every entity, CDATA section, escaped
quote, line ending and byte of encoding around it stays as written.

What keeps a fix from doing damage, in order:

1. the analyzer's own guard decided the fix is safe to apply at all (see
   :mod:`~bigfix_relevance_analyzer.autofix`), and no rule it applies under
   is :attr:`~bigfix_relevance_analyzer.lint.Severity.IGNORE` in the config;
2. every piece writes only names, spaces and parentheses, which need no
   escaping anywhere relevance is written, and maps to the bytes it reads as
   -- never part of an entity, across markup, or next to bytes that are not
   UTF-8;
3. the edited bytes are extracted again before anything is written, and every
   site must read back exactly as expected -- the fixed text where a fix
   went, the original text everywhere else -- or nothing in that file is
   written;
4. the fixed file is linted again, and no rule may report more findings than
   it did before: a fix may not trade a warning for a new error (adding
   ``unique value of`` raises a statement's complexity, say);
5. the file is read back before writing and must still be what was planned,
   and is read back after writing and restored to its original bytes if it
   does not hold what was written.

Planning is separate from writing (:func:`plan_fix`, :func:`write_fix`), so
a caller can put its own check between the two; :func:`fix_file` is both.
``str`` documents and lxml trees have no bytes, so nothing found in them can
be written back.

Print-free, and never raises on bad relevance or an unreadable file: those
become ``file-error`` findings, the same as :func:`~bigfix_relevance_analyzer.lint.lint_file`.
"""

from __future__ import annotations

import dataclasses
import itertools
import os
import re
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from bigfix_relevance_analyzer._serialize import _as_path, _path
from bigfix_relevance_analyzer.autofix import _SAFE_TEXT, AutofixResult, _edit_pieces
from bigfix_relevance_analyzer.extract import (
    RelevanceSite,
    SourceMap,
    _decode_text,
    _extract_data,
    _ExtractionProblem,
)
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    Finding,
    LintConfig,
    Severity,
    SiteJudge,
    _depth_findings,
    _file_error,
    _findings_dict,
    _judge_site,
    _lint_extracted,
    _unlintable,
    _walk_files,
    lint_file,
)

__all__ = [
    "ByteEdit",
    "FileFix",
    "FileFixResult",
    "FixPlan",
    "FixResult",
    "SiteFix",
    "Unmapped",
    "fix_directory",
    "fix_file",
    "fix_paths",
    "fix_paths_to_dict",
    "plan_fix",
    "site_fixes",
    "source_edits",
    "write_fix",
]


@dataclass(frozen=True, slots=True)
class ByteEdit:
    """One replacement of a run of a file's bytes; an insertion when ``start == end``."""

    start: int
    end: int
    replacement: bytes


@dataclass(frozen=True, slots=True)
class Unmapped:
    """Why a fix could not be mapped onto the file's bytes."""

    reason: str


@dataclass(frozen=True, slots=True)
class SiteFix:
    """The one fix a site has: what every fixable finding from it carries."""

    site: RelevanceSite
    autofix: AutofixResult


@dataclass(frozen=True, slots=True)
class FileFix:
    """One site's fix, applied to its file or not."""

    path: Path
    line: int
    """1-based line the site starts on -- :attr:`RelevanceSite.line`."""

    site: RelevanceSite
    """The site as it was before the fix."""

    autofix: AutofixResult

    reason: str | None = None
    """Why the fix was not applied. ``None`` when it was."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": _path(self.path),
            "line": self.line,
            "site": self.site.to_dict(),
            "autofix": self.autofix.to_dict(),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class FileFixResult:
    """What :func:`fix_file` did to one file."""

    path: Path
    applied: tuple[FileFix, ...]
    unapplied: tuple[FileFix, ...]
    findings: tuple[Finding, ...]
    """Lint findings for the file as it now is: after the fixes, if any went in."""

    changed: bool
    """Whether the file was rewritten."""


@dataclass(frozen=True, slots=True)
class FixPlan:
    """What :func:`write_fix` would write into one file, worked out without writing.

    Every check but the ones around the write itself has passed: a fix that
    failed one is in :attr:`unapplied` with the reason, and is not in
    :attr:`fixed`.
    """

    path: Path
    original: bytes
    """The file's bytes as read. Empty when the file could not be read."""

    fixed: bytes
    """What would be written. Equal to :attr:`original` when nothing applies."""

    applied: tuple[FileFix, ...]
    """The fixes in :attr:`fixed`."""

    unapplied: tuple[FileFix, ...]
    """The fixes left out, each with its reason, in line order."""

    findings: tuple[Finding, ...]
    """Lint findings for :attr:`fixed` (so for :attr:`original` when nothing applies)."""

    original_findings: tuple[Finding, ...]
    """Lint findings for :attr:`original`: what to report if :attr:`fixed` is not written."""

    edits: tuple[ByteEdit, ...]
    """The edits that turn :attr:`original` into :attr:`fixed`, sorted and
    disjoint, as offsets into :attr:`original`. Each writes only new text."""

    config: LintConfig = dataclasses.field(repr=False, compare=False)
    """What it was planned under; :func:`write_fix` reports with it."""

    @property
    def changed(self) -> bool:
        return self.fixed != self.original


@dataclass(frozen=True, slots=True)
class FixResult:
    """What :func:`fix_paths` did, over every path."""

    applied: tuple[FileFix, ...]
    unapplied: tuple[FileFix, ...]
    findings: tuple[Finding, ...]
    """Lint findings after the fixes, in path order."""

    changed: tuple[Path, ...]
    """The files that were rewritten, in path order."""

    def to_dict(self) -> dict[str, Any]:
        """This result as JSON-serializable plain data, with the lint verdict.

        ``counts`` and ``ok`` are :func:`~bigfix_relevance_analyzer.lint.lint_paths_to_dict`'s,
        over the findings left after fixing.
        """
        return {
            "applied": [fix.to_dict() for fix in self.applied],
            "unapplied": [fix.to_dict() for fix in self.unapplied],
            "changed": [_path(path) for path in self.changed],
            **_findings_dict(self.findings),
        }


def site_fixes(findings: Iterable[Finding]) -> tuple[SiteFix, ...]:
    """The fix each site's findings carry, once per site, in finding order.

    Every fixable finding from one site carries the same
    :attr:`~bigfix_relevance_analyzer.lint.Finding.autofix`, so it is applied
    once, not once per finding. Sites are told apart by identity rather than
    equality: two equal sites -- the same statement twice on one line -- are
    still two places in the file, and each gets its own fix.
    """
    seen: set[int] = set()
    fixes: list[SiteFix] = []
    for finding in findings:
        if finding.autofix is None or finding.site is None or id(finding.site) in seen:
            continue
        seen.add(id(finding.site))
        fixes.append(SiteFix(finding.site, finding.autofix))
    return tuple(fixes)


SiteAnchor = tuple[str, int, int | None, int | None, str]


def _site_anchor(site: RelevanceSite) -> SiteAnchor:
    """Where ``site`` is in its file, as a value another extraction can match.

    Identity tells sites apart within one extraction (see :func:`site_fixes`),
    but :func:`_plan` extracts again, so a caller's site objects are never its
    own. Equality is not enough either: the same statement twice on one line
    gives two equal sites. This tells them apart by the first byte a BES site
    came from, or a text site's column, and is the same for the same bytes
    extracted twice.
    """
    spans = site.source_map.spans if site.source_map is not None else ()
    raw = spans[0].raw_start if spans else None
    return (site.kind, site.line, site.column, raw, site.text)


_BYTE_LINE_BREAK: Final = re.compile(rb"\r\n|\r|\n")
_UTF8_BOM: Final = b"\xef\xbb\xbf"


class _ByteLines:
    """A text file's bytes, cut into the lines its sites' text was read as.

    Built once per file and shared by its sites, and only split if one asks.
    Lines break where :func:`~bigfix_relevance_analyzer.extract._decode_text`
    folds line endings, so line N here is a site's line N. Line 1 starts where
    that decoding starts: after a leading byte order mark if it drops one
    (#107), or at the mark if it keeps it as a character the columns count.
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self._bounds: list[tuple[int, int]] | None = None
        self._text: dict[int, str | None] = {}

    def _split(self) -> list[tuple[int, int]]:
        if self._bounds is None:
            dropped = self.data.startswith(_UTF8_BOM) and not _decode_text(_UTF8_BOM)
            start = len(_UTF8_BOM) if dropped else 0
            self._bounds = []
            for match in _BYTE_LINE_BREAK.finditer(self.data, start):
                self._bounds.append((start, match.start()))
                start = match.end()
            self._bounds.append((start, len(self.data)))
        return self._bounds

    def line(self, number: int) -> tuple[int, str] | Unmapped:
        """Where 1-based line ``number``'s bytes start, and its text.

        :class:`Unmapped` if the line's bytes are not UTF-8: decoding put a
        replacement character in the site's text there, and an offset next
        to bytes that did not decode cannot be trusted.
        """
        bounds = self._split()
        if not 1 <= number <= len(bounds):
            return Unmapped(f"line {number} is not in the file")
        start, end = bounds[number - 1]
        if number not in self._text:
            try:
                self._text[number] = self.data[start:end].decode("utf-8")
            except UnicodeDecodeError:
                self._text[number] = None
        text = self._text[number]
        if text is None:
            return Unmapped(f"undecodable bytes on line {number}")
        return start, text


def source_edits(
    site: RelevanceSite, autofix: AutofixResult, data: bytes | None = None
) -> tuple[ByteEdit, ...] | Unmapped:
    """``autofix`` as minimal edits of the bytes of the file ``site`` came from.

    Each edit is split into pieces that write only new text (see
    :func:`~bigfix_relevance_analyzer.autofix._pieces`), each piece placed at
    the bytes it belongs at; a wrap is an insertion. ``data`` is the file's
    bytes, which a site from a text extractor (anything but BES XML) is
    mapped through; a BES site needs only its source map.

    :class:`Unmapped`, with the reason, when ``autofix`` is not for this
    site's text, a piece would write text needing escaping, a piece would
    split an entity or span markup, ``data`` is missing for a text site or
    does not read back as the site's text where a piece goes, or the site has
    no way to place it at all (a ``str`` document, an lxml tree).
    """
    return _source_edits(site, autofix, None if data is None else _ByteLines(data))


def _source_edits(
    site: RelevanceSite, autofix: AutofixResult, lines: _ByteLines | None
) -> tuple[ByteEdit, ...] | Unmapped:
    """:func:`source_edits`, with the file's lines shared by every site in it."""
    source_map = site.source_map
    if source_map is None:
        if site.column is None:
            return Unmapped(
                f"no source map for a {site.kind} site: it was not read from a file's bytes"
            )
        if lines is None:
            return Unmapped(f"a {site.kind} site is placed through its file: pass the file's bytes")
    if autofix.original != site.text:
        return Unmapped("fix is for a different statement than the site's")
    edits: list[ByteEdit] = []
    for edit in autofix.edits:
        written = autofix.original[edit.start : edit.end]
        for piece in _edit_pieces(autofix.original, edit):
            if not _SAFE_TEXT.fullmatch(piece.replacement):
                return Unmapped(f"text {piece.replacement!r} would need escaping")
            if source_map is not None:
                raw = _mapped(source_map, piece.start, piece.end)
                if raw is None:
                    return Unmapped(f"{written!r} is split by an entity or markup in the file")
            else:
                assert lines is not None
                placed = _placed(site, piece.start, piece.end, lines)
                if placed is None:
                    return Unmapped(_misread(written, site, piece.start))
                if isinstance(placed, Unmapped):
                    return placed
                raw = placed
            edits.append(ByteEdit(raw[0], raw[1], piece.replacement.encode("utf-8")))
    return tuple(sorted(edits, key=lambda edit: edit.start))


def _mapped(source_map: SourceMap, start: int, end: int) -> tuple[int, int] | None:
    """The bytes ``[start, end)`` of a BES site's text are at, or an insertion
    point for ``start == end``.

    An insertion goes before the bytes of the character after it, or else
    after the bytes of the one before it: before an entity's ``&``, after a
    CDATA section's ``]]>``. Both are safe for text that holds no markup.
    """
    if start < end:
        return source_map.raw_range(start, end)
    after = source_map.raw_range(start, start + 1)
    if after is not None:
        return after[0], after[0]
    before = source_map.raw_range(start - 1, start)
    return None if before is None else (before[1], before[1])


def _placed(
    site: RelevanceSite, start: int, end: int, lines: _ByteLines
) -> tuple[int, int] | Unmapped | None:
    """The bytes ``[start, end)`` of a text site's text are at, read back.

    Through the site's line and column: text extractors keep text as written
    but for line endings, which move no character within a line. The bytes
    found must be the text expected -- the characters either side of an
    insertion, the whole of a replaced range -- since an extractor that does
    unescape something would put the offsets out. ``None`` for a read-back
    that does not match, which the caller words.
    """
    first = _text_point(site, start, lines)
    if first is None or isinstance(first, Unmapped):
        return first
    number, first_byte, line, index = first
    text = site.text
    if start == end:
        checks = []
        if start < len(text) and text[start] != "\n":
            checks.append(index < len(line) and line[index] == text[start])
        if start > 0 and text[start - 1] != "\n":
            checks.append(index > 0 and line[index - 1] == text[start - 1])
        return (first_byte, first_byte) if checks and all(checks) else None
    last = _text_point(site, end, lines)
    if last is None or isinstance(last, Unmapped):
        return last
    held = _BYTE_LINE_BREAK.sub(b"\n", lines.data[first_byte : last[1]])
    try:
        matches = held.decode("utf-8") == text[start:end]
    except UnicodeDecodeError:
        return Unmapped(f"undecodable bytes on line {number}")
    return (first_byte, last[1]) if matches else None


def _text_point(
    site: RelevanceSite, offset: int, lines: _ByteLines
) -> tuple[int, int, str, int] | Unmapped | None:
    """Where ``site.text[offset]`` is: its line number, byte offset, that
    line's text, and its index in that text. ``None`` past the line's end."""
    assert site.column is not None
    relative = site.text.count("\n", 0, offset)
    in_line = offset - (site.text.rfind("\n", 0, offset) + 1)
    number = site.line + relative
    index = (site.column - 1 if relative == 0 else 0) + in_line
    found = lines.line(number)
    if isinstance(found, Unmapped):
        return found
    line_start, line = found
    if index > len(line):
        return None
    return number, line_start + len(line[:index].encode("utf-8")), line, index


def _misread(written: str, site: RelevanceSite, offset: int) -> str:
    return (
        f"{written!r} does not read back at line {site.line + site.text.count(chr(10), 0, offset)}"
    )


def _ignored_rules(autofix: AutofixResult, config: LintConfig) -> tuple[str, ...]:
    """The rules ``autofix`` applies under that ``config`` switches off.

    A disabled rule produces no finding, so a fix reaching here under one is
    a fix whose site *also* had an enabled one. The fix is a single result over
    every edit, so it cannot be applied in part: it is not applied at all.
    """
    return tuple(
        rule for rule in autofix.applied_rules if config.severity_for(rule) is Severity.IGNORE
    )


def _extract(file_path: Path, data: bytes) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
    """``file_path``'s sites and extraction problems, from ``data``: never the disk.

    The one place planning extracts, before a fix and after it alike.
    """
    return _extract_data(file_path, data)


def _write(file_path: Path, data: bytes) -> None:
    # In place, not via a temporary file and a rename: that would lose the
    # file's mode, ownership and hard links, and a hook must not change those.
    file_path.write_bytes(data)


def _splice(data: bytes, edits: Sequence[ByteEdit]) -> bytes:
    """Apply sorted, disjoint ``edits``, right to left so no offset moves."""
    for edit in reversed(edits):
        data = data[: edit.start] + edit.replacement + data[edit.end :]
    return data


def _site_key(site: RelevanceSite, text: str | None = None) -> tuple[str, int, str, str]:
    return (site.kind, site.line, site.context, site.text if text is None else text)


def plan_fix(path: str | bytes | os.PathLike[str], config: LintConfig) -> FixPlan:
    """Lint one file and work out every safe fix to it, without writing anything.

    Reads the file once. See the module docstring for what makes a fix safe;
    :func:`write_fix` writes the result, and a caller may check the plan in
    between -- validate :attr:`FixPlan.fixed` against a schema, say. A path
    that is not a readable file gives an unchanged plan whose findings report
    it, as :func:`~bigfix_relevance_analyzer.lint.lint_file` reports it.
    """
    return _plan_path(_as_path(path), config, explicit=True)


def _plan_path(file_path: Path, config: LintConfig, *, explicit: bool) -> FixPlan:
    """:func:`plan_fix`, or the directory walk's quieter version of it: every
    check on the path itself, before :func:`_plan` gets its bytes."""

    def unread(findings: tuple[Finding, ...]) -> FixPlan:
        return FixPlan(file_path, b"", b"", (), (), findings, findings, (), config)

    blocked = _unlintable(file_path, config, explicit=explicit)
    if blocked is not None:
        return unread(blocked)
    if not file_path.is_file():
        # A FIFO or device reads once and cannot take the edit back.
        return unread(lint_file(file_path, config))
    try:
        data = file_path.read_bytes()
    except OSError as error:
        return unread(_file_error(file_path, error.strerror or str(error), config))
    return _plan(file_path, data, config)


def _plan(
    file_path: Path,
    data: bytes,
    config: LintConfig,
    *,
    judge: SiteJudge = _judge_site,
    only: Iterable[SiteAnchor] | None = None,
) -> FixPlan:
    """Plan the fixes to ``data``, the bytes of ``file_path``, which is never opened.

    Every decision about whether a fix is safe is made here, once, for
    :func:`plan_fix` and the language server's quick fixes alike. ``data`` lets
    an editor plan its open buffer rather than the file on disk; ``judge`` lets
    it reuse its per-site findings cache; and ``only``, a set of
    :func:`_site_anchor` values, plans just those sites -- one quick fix.
    Sites outside ``only`` stay as written and are not reported, while the
    re-extract and finding-count checks still cover the whole file.
    """
    wanted = None if only is None else frozenset(only)
    sites, problems = _extract(file_path, data)
    # A problem is not a site, so it never blocks a fix; it is reported
    # before and after one alike, or `--fix` would look cleaner than lint.
    findings = _lint_extracted(file_path, sites, problems, config, judge)
    lines = _ByteLines(data)

    def record(fix: SiteFix, reason: str | None = None) -> FileFix:
        return FileFix(file_path, fix.site.line, fix.site, fix.autofix, reason)

    planned: list[tuple[SiteFix, tuple[ByteEdit, ...]]] = []
    unapplied: list[FileFix] = []
    for fix in site_fixes(findings):
        if wanted is not None and _site_anchor(fix.site) not in wanted:
            continue
        ignored = _ignored_rules(fix.autofix, config)
        if ignored:
            unapplied.append(record(fix, f"rule {', '.join(ignored)} is ignored"))
            continue
        edits = _source_edits(fix.site, fix.autofix, lines)
        if isinstance(edits, Unmapped):
            unapplied.append(record(fix, edits.reason))
        elif edits:
            planned.append((fix, edits))

    def plan(
        reason: str | None = None,
        *,
        fixed: bytes = data,
        after: tuple[Finding, ...] = findings,
        edits: tuple[ByteEdit, ...] = (),
    ) -> FixPlan:
        """The plan; with a ``reason``, every planned fix refused for it."""
        applied = [record(fix) for fix, _ in planned] if reason is None else []
        refused = [] if reason is None else [record(fix, reason) for fix, _ in planned]
        return FixPlan(
            file_path,
            data,
            fixed if reason is None else data,
            tuple(applied),
            tuple(sorted([*unapplied, *refused], key=lambda fix: fix.line)),
            after if reason is None else findings,
            findings,
            edits if reason is None else (),
            config,
        )

    if not planned:
        return plan()

    byte_edits = tuple(
        sorted((edit for _, edits in planned for edit in edits), key=lambda e: e.start)
    )
    # Two edits at one byte -- an insertion where another begins -- have no
    # order that is right for both, so they are refused as overlapping.
    if any(
        left.end > right.start or left.start == right.start
        for left, right in itertools.pairwise(byte_edits)
    ):
        return plan("overlapping edits")
    fixed = _splice(data, byte_edits)

    # Read the edited bytes back before anything is written: every site must
    # be there, fixed where a fix went and untouched everywhere else.
    fixed_text = {id(fix.site): fix.autofix.fixed for fix, _ in planned}
    expected = Counter(_site_key(site, fixed_text.get(id(site))) for site in sites)
    new_sites, new_problems = _extract(file_path, fixed)
    if Counter(_site_key(site) for site in new_sites) != expected:
        return plan("re-extract mismatch")

    # The analyzer's guard judges each statement by the default configuration;
    # this judges the file by the caller's, ceilings and every site rule
    # included, so no fix trades a warning for a new error.
    after = _lint_extracted(file_path, new_sites, new_problems, config, judge)
    before = Counter(finding.code for finding in findings)
    added = sorted(
        code
        for code, count in Counter(finding.code for finding in after).items()
        if count > before[code]
    )
    if added:
        return plan(f"the fix would add {_findings_named(added)}")
    return plan(fixed=fixed, after=after, edits=byte_edits)


def _findings_named(codes: Sequence[str]) -> str:
    return f"a {codes[0]} finding" if len(codes) == 1 else f"{', '.join(codes)} findings"


def write_fix(plan: FixPlan) -> FileFixResult:
    """Write ``plan`` into its file, and report what that did.

    Writes only if the plan changes the file, and only if the file still holds
    what was planned from: one changed since is left alone, its fixes reported
    unapplied. The file is rewritten in place -- mode, owner and links kept --
    read back, and restored to its original bytes if it does not hold what was
    written.
    """
    path = plan.path

    def result(
        findings: tuple[Finding, ...],
        applied: Sequence[FileFix] = (),
        unapplied: Sequence[FileFix] = (),
        *,
        changed: bool = False,
    ) -> FileFixResult:
        ordered = sorted(unapplied, key=lambda fix: fix.line)
        return FileFixResult(path, tuple(applied), tuple(ordered), findings, changed)

    if not plan.changed:
        return result(plan.findings, (), plan.unapplied)

    def refuse(reason: str, findings: tuple[Finding, ...]) -> FileFixResult:
        refused = [dataclasses.replace(fix, reason=reason) for fix in plan.applied]
        return result(findings, (), [*plan.unapplied, *refused])

    data = plan.original
    try:
        current = path.read_bytes()
    except OSError as error:
        detail = error.strerror or str(error)
        return refuse(
            f"could not re-read: {detail}",
            plan.original_findings + _file_error(path, detail, plan.config),
        )
    if current != data:
        sites, problems = _extract(path, current)
        return refuse(
            "file changed since it was planned",
            _lint_extracted(path, sites, problems, plan.config),
        )

    try:
        _write(path, plan.fixed)
        if path.read_bytes() != plan.fixed:
            _write(path, data)
            return refuse(
                "file did not hold what was written; original restored", plan.original_findings
            )
    except OSError as error:
        detail = error.strerror or str(error)
        try:
            if path.read_bytes() != data:
                _write(path, data)
        except OSError:
            detail += "; the file may be left partly written"
        return refuse(
            f"could not write: {detail}",
            plan.original_findings + _file_error(path, detail, plan.config),
        )
    return result(plan.findings, plan.applied, plan.unapplied, changed=True)


def fix_file(path: str | bytes | os.PathLike[str], config: LintConfig) -> FileFixResult:
    """Lint one file, apply every safe fix to it in place, and lint it again.

    :func:`write_fix` of :func:`plan_fix`. See the module docstring for what
    makes a fix safe to write. A file is written only if it changes, and
    either every fix planned for it goes in or none does: the per-file checks
    refuse the whole file. A path that is not a readable file is reported the
    way :func:`~bigfix_relevance_analyzer.lint.lint_file` reports it.
    """
    return write_fix(plan_fix(path, config))


def fix_paths(paths: Iterable[str | bytes | os.PathLike[str]], config: LintConfig) -> FixResult:
    """:func:`fix_file` over many paths, in order.

    Each path is taken literally, as :func:`~bigfix_relevance_analyzer.lint.lint_paths`
    takes it; :func:`fix_directory` is the one that walks.
    """
    return _combine([fix_file(path, config) for path in paths])


def fix_directory(
    root: str | bytes | os.PathLike[str],
    config: LintConfig,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> FixResult:
    """:func:`fix_file` over every file under ``root``, walked as
    :func:`~bigfix_relevance_analyzer.lint.lint_directory` walks it, depth
    findings included."""
    root_path = _as_path(root)
    files, exceeded = _walk_files(root_path, max_depth)
    combined = _combine(
        [write_fix(_plan_path(file_path, config, explicit=False)) for file_path in files]
    )
    return FixResult(
        combined.applied,
        combined.unapplied,
        _depth_findings(root_path, exceeded, max_depth, config) + combined.findings,
        combined.changed,
    )


def _combine(results: Sequence[FileFixResult]) -> FixResult:
    return FixResult(
        applied=tuple(fix for result in results for fix in result.applied),
        unapplied=tuple(fix for result in results for fix in result.unapplied),
        findings=tuple(finding for result in results for finding in result.findings),
        changed=tuple(result.path for result in results if result.changed),
    )


def fix_paths_to_dict(
    paths: Iterable[str | bytes | os.PathLike[str]], config: LintConfig
) -> dict[str, Any]:
    """:func:`fix_paths` as JSON-serializable plain data -- see :meth:`FixResult.to_dict`."""
    return fix_paths(paths, config).to_dict()
