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
is mapped through the site's
:attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.source_map` to the
exact bytes it replaces, and only those bytes are rewritten. Every entity,
CDATA section, line ending and byte of encoding around them stays as it was.

What keeps a fix from doing damage, in order:

1. the analyzer's own guard decided the fix is safe to apply at all (see
   :mod:`~bigfix_relevance_analyzer.autofix`), and no rule it applies under
   is :attr:`~bigfix_relevance_analyzer.lint.Severity.IGNORE` in the config;
2. every edit maps to one unbroken run of bytes, never part of an entity or
   across markup, and its replacement needs no escaping;
3. the edited bytes are extracted again before anything is written, and every
   site must read back exactly as expected -- the fixed text where a fix
   went, the original text everywhere else -- or nothing in that file is
   written;
4. the file is read back after writing, and restored to its original bytes
   if it does not hold what was written.

Only sites extracted from BES XML bytes (``.bes``, ``.bes.xml``) have a source
map so far. A fix anywhere else is reported unapplied, with the reason.

Print-free, and never raises on bad relevance or an unreadable file: those
become ``file-error`` findings, the same as :func:`~bigfix_relevance_analyzer.lint.lint_file`.
"""

from __future__ import annotations

import itertools
import os
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from bigfix_relevance_analyzer._serialize import _path
from bigfix_relevance_analyzer.autofix import AutofixResult
from bigfix_relevance_analyzer.extract import (
    RelevanceSite,
    _is_bes_xml,
    extract_relevance_from_bes_xml,
    extract_relevance_from_file,
)
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    Finding,
    LintConfig,
    Severity,
    _depth_findings,
    _file_error,
    _lint_sites,
    _walk,
    counts,
    lint_file,
)

__all__ = [
    "ByteEdit",
    "FileFix",
    "FileFixResult",
    "FixResult",
    "SiteFix",
    "Unmapped",
    "fix_directory",
    "fix_file",
    "fix_paths",
    "fix_paths_to_dict",
    "site_fixes",
    "source_edits",
]

_NEEDS_ESCAPING: Final = frozenset("&<>\"'\r")
"""Characters a replacement may not contain.

Every fix today replaces an inspector name with another one, so none of these
can occur. Refused rather than escaped: a replacement that needed escaping
would be a fix this module was not written for, and guessing how to spell it
(``&quot;`` or ``"``? inside CDATA or not?) is how a file gets corrupted.
"""


@dataclass(frozen=True, slots=True)
class ByteEdit:
    """One replacement of a run of a file's bytes."""

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
        tallies = counts(self.findings)
        return {
            "applied": [fix.to_dict() for fix in self.applied],
            "unapplied": [fix.to_dict() for fix in self.unapplied],
            "changed": [_path(path) for path in self.changed],
            "findings": [finding.to_dict() for finding in self.findings],
            "counts": dict(tallies),
            "ok": tallies[Severity.ERROR.value] == 0,
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


def source_edits(site: RelevanceSite, autofix: AutofixResult) -> tuple[ByteEdit, ...] | Unmapped:
    """``autofix``'s edits as edits of the bytes of the file ``site`` came from.

    Each replacement is written as UTF-8 in place of exactly the bytes that
    held the text it replaces. :class:`Unmapped`, with the reason, when the
    site has no :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.source_map`,
    ``autofix`` is not for this site's text, an edit would split an entity or
    span markup (``cl<![CDATA[ient]]>``), or a replacement would need escaping.
    """
    source_map = site.source_map
    if source_map is None:
        return Unmapped(f"no source map for a {site.kind} site; only BES XML is fixable for now")
    if autofix.original != site.text:
        return Unmapped("fix is for a different statement than the site's")
    edits: list[ByteEdit] = []
    for edit in autofix.edits:
        written = autofix.original[edit.start : edit.end]
        if _NEEDS_ESCAPING.intersection(edit.replacement) or "]]>" in edit.replacement:
            return Unmapped(f"replacement {edit.replacement!r} would need escaping")
        raw = source_map.raw_range(edit.start, edit.end)
        if raw is None:
            return Unmapped(f"{written!r} is split by an entity or markup in the file")
        edits.append(ByteEdit(raw[0], raw[1], edit.replacement.encode("utf-8")))
    return tuple(sorted(edits, key=lambda edit: edit.start))


def _ignored_rules(autofix: AutofixResult, config: LintConfig) -> tuple[str, ...]:
    """The rules ``autofix`` applies under that ``config`` switches off.

    A disabled rule produces no finding, so a fix reaching here under one is
    a fix whose site *also* had an enabled one. The fix is a single result over
    every edit, so it cannot be applied in part: it is not applied at all.
    """
    return tuple(
        rule for rule in autofix.applied_rules if config.severity_for(rule) is Severity.IGNORE
    )


def _extract(file_path: Path, data: bytes) -> list[RelevanceSite]:
    """``file_path``'s sites, from ``data`` itself when it is BES XML."""
    if _is_bes_xml(file_path):
        return extract_relevance_from_bes_xml(data)
    return extract_relevance_from_file(file_path)


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


def fix_file(path: str | bytes | os.PathLike[str], config: LintConfig) -> FileFixResult:
    """Lint one file, apply every safe fix to it in place, and lint it again.

    See the module docstring for what makes a fix safe to write. A file is
    written only if it changes, and either every fix planned for it goes in or
    none does: the per-file checks refuse the whole file. A path that is not a
    readable file is reported the way :func:`~bigfix_relevance_analyzer.lint.lint_file`
    reports it.
    """
    file_path = Path(os.fsdecode(path))

    def result(
        findings: tuple[Finding, ...],
        applied: Sequence[FileFix] = (),
        unapplied: Sequence[FileFix] = (),
        *,
        changed: bool = False,
    ) -> FileFixResult:
        ordered = sorted(unapplied, key=lambda fix: fix.line)
        return FileFixResult(file_path, tuple(applied), tuple(ordered), findings, changed)

    if not file_path.is_file():
        return result(lint_file(file_path, config))
    try:
        data = file_path.read_bytes()
        sites = _extract(file_path, data)
    except OSError as error:
        return result(_file_error(file_path, error.strerror or str(error), config))
    findings = _lint_sites(file_path, sites, config)

    def fix_record(fix: SiteFix, reason: str | None = None) -> FileFix:
        return FileFix(file_path, fix.site.line, fix.site, fix.autofix, reason)

    planned: list[tuple[SiteFix, tuple[ByteEdit, ...]]] = []
    unapplied: list[FileFix] = []
    for fix in site_fixes(findings):
        ignored = _ignored_rules(fix.autofix, config)
        if ignored:
            unapplied.append(fix_record(fix, f"rule {', '.join(ignored)} is ignored"))
            continue
        edits = source_edits(fix.site, fix.autofix)
        if isinstance(edits, Unmapped):
            unapplied.append(fix_record(fix, edits.reason))
        elif edits:
            planned.append((fix, edits))

    def refuse(reason: str, extra: tuple[Finding, ...] = ()) -> FileFixResult:
        return result(
            findings + extra, (), unapplied + [fix_record(fix, reason) for fix, _ in planned]
        )

    if not planned:
        return result(findings, (), unapplied)

    byte_edits = sorted((edit for _, edits in planned for edit in edits), key=lambda e: e.start)
    if any(left.end > right.start for left, right in itertools.pairwise(byte_edits)):
        return refuse("overlapping edits")
    fixed = _splice(data, byte_edits)

    # Read the edited bytes back before anything is written: every site must
    # be there, fixed where a fix went and untouched everywhere else.
    fixed_text = {id(fix.site): fix.autofix.fixed for fix, _ in planned}
    expected = Counter(_site_key(site, fixed_text.get(id(site))) for site in sites)
    try:
        new_sites = _extract(file_path, fixed)
    except OSError as error:
        return refuse(f"could not re-read: {error.strerror or error}")
    if Counter(_site_key(site) for site in new_sites) != expected:
        return refuse("re-extract mismatch")

    try:
        _write(file_path, fixed)
        if file_path.read_bytes() != fixed:
            _write(file_path, data)
            return refuse("file did not hold what was written; original restored")
    except OSError as error:
        detail = error.strerror or str(error)
        try:
            if file_path.read_bytes() != data:
                _write(file_path, data)
        except OSError:
            detail += "; the file may be left partly written"
        return refuse(f"could not write: {detail}", _file_error(file_path, detail, config))

    applied = [fix_record(fix) for fix, _ in planned]
    return result(_lint_sites(file_path, new_sites, config), applied, unapplied, changed=True)


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
    root_path = Path(os.fsdecode(root))
    files, exceeded = _walk(root_path, max_depth)
    combined = _combine([fix_file(file_path, config) for file_path in files])
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
