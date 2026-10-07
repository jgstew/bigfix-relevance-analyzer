"""Work out the fully fixed statement, as one final result.

The checker proposes fixes one diagnostic at a time, against spans it cannot
read (see :class:`~bigfix_relevance_analyzer.typecheck.TypeFix`). A consumer
wants something else: the statement with every safe fix applied, so a hook can
print it when auto-fix is off and swap it in when it is on, without owning any
of the logic that decides what "safe" means. This module is that logic.

    from bigfix_relevance_analyzer.autofix import autofix

    result = autofix('exists values of setting "x" of client')
    result.fixed    # 'exists values of settings "x" of client'
    result.applied  # {'singular-spelling-mid-chain': 1}

Fixes can cascade. Pluralizing `folder "etc"` in `files of folder "etc" of
folder "private" of folder "/"` makes `folder "private"` the singular a plural
is now built from, and it fires on the next analysis. So this runs in rounds:
collect every fix, drop overlaps, apply right to left, re-analyze, repeat.

Nothing is applied that makes the statement worse. The guard compares every
candidate against the *original* -- never the previous round, or a sequence of
individually tolerable steps could drift arbitrarily far -- and rejects one
that raises the count of any problem, changes the resolved dialect, or changes
what the statement evaluates to (its types or plurality). One exception, the
repair of a plural where the engine requires a singular (see
:data:`~bigfix_relevance_analyzer.typecheck.SINGULAR_REQUIRED`): the original
never runs, so there is no meaning to keep, and a candidate with fewer of
those diagnostics may change its plurality and narrow its types. Fix-carrying
diagnostics are left out of that count during rounds, since a cascade moves
one down the chain by design; the final result is then held to a full check
that counts them, and that also refuses a fix-carrying diagnostic the edits
*introduced* -- half a cascade, which is what a round limit reached mid-chain
leaves, moves the finding rather than fixing it. The last accepted state that
passes is what is reported.

Print-free and never raises on bad relevance, like the rest of the package.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, Literal

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.tokenizer import _normalize_phrase
from bigfix_relevance_analyzer.typecheck import _UNIQUE_VALUE, SINGULAR_REQUIRED

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.dialect import Dialect
    from bigfix_relevance_analyzer.typecheck import TypeDiagnostic, TypeFix

__all__ = [
    "AutofixResult",
    "Guard",
    "TextEdit",
    "autofix",
]

Guard = Literal["warnings", "errors"]
"""What a fix may not add more of.

``"warnings"`` (the default) counts every problem whose lint rule defaults to
an error or a warning; ``"errors"`` counts only the ones defaulting to an
error, so a fix may trade a style note for a risk. Either way the dialect and
the result's types and plurality must not change -- except while repairing a
plural where a singular is required; see the module docstring.
"""

_GUARDS: Final = frozenset({"warnings", "errors"})

DEFAULT_MAX_ROUNDS: Final = 16
"""Far more than any real cascade: each round fixes one level of a chain."""


@dataclass(frozen=True, slots=True)
class TextEdit:
    """One replacement in the statement's text, attributed to its diagnostic."""

    start: int
    end: int
    replacement: str
    code: str
    """The checker diagnostic this edit resolves."""


@dataclass(frozen=True, slots=True)
class AutofixResult:
    """The statement before and after every fix that was safe to apply."""

    original: str
    fixed: str
    """The final text. Equal to :attr:`original` when nothing was applied."""

    applied: Mapping[str, int] = field(default_factory=dict, hash=False)
    """How many edits were applied to reach :attr:`fixed`, by diagnostic code."""

    unapplied: Mapping[str, int] = field(default_factory=dict, hash=False)
    """Fixable diagnostics still standing in :attr:`fixed`, by code -- the ones
    whose fix the guard refused, the ones whose span did not read as the
    expected name, and any a round limit left behind."""

    rounds: int = 0
    """How many rounds of edits :attr:`fixed` took. 0 when unchanged."""

    edits: tuple[TextEdit, ...] = ()
    """Every edit, measured against :attr:`original`, that turns it into :attr:`fixed`.

    Each round's edits are measured against that round's text; these are
    composed across rounds, so a consumer writing the fix back into a file
    can map each one to where the original statement was written. Sorted,
    and neither overlapping nor touching: a later round's edit that overlaps
    or touches an earlier one is merged into it, keeping the earlier one's
    :attr:`TextEdit.code`. Applying them right to left to :attr:`original`
    gives :attr:`fixed`; empty when nothing changed.
    """

    @property
    def changed(self) -> bool:
        return self.fixed != self.original

    @property
    def applied_rules(self) -> Mapping[str, int]:
        """:attr:`applied`, tallied by the lint rule each code reports under.

        What a consumer that disables rules by name -- a repo's hook config --
        checks a fix against, without carrying the code-to-rule mapping.
        """
        tallies: Counter[str] = Counter()
        for code, count in self.applied.items():
            tallies[_rule_for(code)] += count
        return dict(sorted(tallies.items()))

    def to_dict(self) -> dict[str, Any]:
        """This result as JSON-serializable plain data.

        Each code is joined to the lint rule it reports under, so a hook can
        name its own code for it without carrying the mapping itself.
        """

        def entries(tallies: Mapping[str, int]) -> list[dict[str, Any]]:
            return [
                {"code": code, "rule": _rule_for(code), "count": count}
                for code, count in sorted(tallies.items())
            ]

        return {
            "original": self.original,
            "fixed": self.fixed,
            "changed": self.changed,
            "rounds": self.rounds,
            "applied": entries(self.applied),
            "unapplied": entries(self.unapplied),
            "edits": [
                {
                    "start": edit.start,
                    "end": edit.end,
                    "replacement": edit.replacement,
                    "code": edit.code,
                }
                for edit in self.edits
            ],
        }


def _rule_for(code: str) -> str:
    # Imported here, not at module scope: `lint` imports `analyzer`, which
    # reaches this module from `RelevanceAnalysis.autofix`.
    from bigfix_relevance_analyzer.lint import _rule_for

    return _rule_for(code)


def _anchored(text: str, fix: TypeFix, code: str) -> TextEdit | None:
    """``fix`` as an edit on ``text``, or ``None`` if its range does not hold
    the name it expects.

    The checker only has spans; this is where they meet the text. Whitespace
    at either end of the range is left in place, so `of  Setting  "x"` keeps
    its spacing.
    """
    written = text[fix.start : fix.end]
    name = written.strip()
    if not name or _normalize_phrase(name, fold=True) != _normalize_phrase(fix.expected, fold=True):
        return None
    start = fix.start + len(written) - len(written.lstrip())
    replacement = fix.replacement
    if not replacement.startswith(_UNIQUE_VALUE):
        # A respelling, not a wrap: write it the way the author wrote the name.
        replacement = _match_case(name, replacement)
    return TextEdit(start, start + len(name), replacement, code)


_ACRONYMS: Final = frozenset(
    {
        # Drawn from the words the inspector tables pluralize, where an all-caps
        # spelling reads as an acronym. A short all-caps word that is not one
        # -- `KEY`, `DAY`, `LOG`, `SET` -- is why this is a list, not a length.
        *("acl", "ace", "bcc", "bios", "bssid", "cpu", "dacl", "dmi", "fpu"),
        *("ghz", "gid", "guid", "html", "ia64", "id", "ip", "ipv4", "ipv6"),
        *("irtt", "json", "khz", "lan", "ldap", "mac", "md5", "mhz", "mtu"),
        *("pid", "ppid", "ram", "rpm", "rssi", "rtt", "sacl", "scsi", "sha1"),
        *("sha224", "sha256", "sha384", "sha512", "sid", "smbios", "ssid"),
        *("ssl", "tcb", "tcp", "tty", "udp", "uid", "uri", "url", "usb"),
        *("uuid", "wmi", "wow64", "x32", "x64", "xml", "yaml"),
    }
)
"""All-caps words :func:`_match_case` pluralizes with a lowercase suffix."""


def _match_case(written: str, spelling: str) -> str:
    """``spelling`` (as the inspector tables write it) in ``written``'s capitalization.

    Only some names in a statement are rewritten, so a lowercase plural in a
    capitalized statement looks inconsistent unless the author wrote it so.
    Word by word, the letters the two words share keep the author's case
    (`Setting` -> `Settings`, `SIDs` -> `SID`, `WiFi` -> `WiFis`), and only
    the letters the respelling adds need one: uppercase after an all-caps word
    (`KEY` -> `KEYS`) unless it is one of :data:`_ACRONYMS`, the usual way to
    pluralize an acronym (`WMI` -> `WMIs`, `BIOS` -> `BIOSes`), and lowercase
    otherwise. A word sharing nothing keeps at least a leading capital
    (`Nil` -> `Nothings`). Lowercase, by far the common spelling, is left
    alone, and so is a name whose words do not line up one to one with the
    spelling's.
    """
    words, targets = written.split(), spelling.split()
    if len(words) != len(targets):
        return spelling
    matched = []
    for word, target in zip(words, targets, strict=True):
        shared = 0
        while (
            shared < min(len(word), len(target)) and word[shared].lower() == target[shared].lower()
        ):
            shared += 1
        shouted = word.isupper() and word.lower() not in _ACRONYMS
        added = target[shared:].upper() if shouted else target[shared:].lower()
        result = word[:shared] + added
        if shared == 0 and word[:1].isupper():
            result = result[:1].upper() + result[1:]
        matched.append(result)
    return " ".join(matched)


def _fixable(
    report: RelevanceAnalysis, codes: Collection[str] | None = None
) -> tuple[TypeDiagnostic, ...]:
    """``report``'s fix-carrying diagnostics, limited to ``codes`` when given."""
    if report.check is None:
        return ()
    return tuple(
        diagnostic
        for diagnostic in report.check.diagnostics
        if diagnostic.fix and (codes is None or diagnostic.code in codes)
    )


def _edits(report: RelevanceAnalysis, codes: Collection[str] | None = None) -> tuple[TextEdit, ...]:
    """Every fix ``report``'s diagnostics carry, anchored to its text, in order."""
    found: set[TextEdit] = set()
    for diagnostic in _fixable(report, codes):
        assert diagnostic.fix is not None
        edit = _anchored(report.text, diagnostic.fix, diagnostic.code)
        if edit is not None:
            found.add(edit)
    return tuple(sorted(found, key=lambda edit: (edit.start, edit.end, edit.replacement)))


def _disjoint(edits: Iterable[TextEdit]) -> list[TextEdit]:
    """The leftmost edit wins an overlap; the loser can return next round."""
    kept: list[TextEdit] = []
    for edit in sorted(edits, key=lambda edit: (edit.start, edit.end)):
        if not kept or edit.start >= kept[-1].end:
            kept.append(edit)
    return kept


def _apply(text: str, edits: Iterable[TextEdit]) -> str:
    """Apply non-overlapping ``edits``, right to left so no offset moves."""
    for edit in sorted(edits, key=lambda edit: edit.start, reverse=True):
        text = text[: edit.start] + edit.replacement + text[edit.end :]
    return text


def _kept(edit: TextEdit, before: str) -> int | None:
    """Where ``edit``'s replacement keeps the text it replaced, verbatim, if
    it is a `unique value of` wrap -- else ``None``.

    A wrap replaces a whole operand to keep each fix one range (see
    :class:`~bigfix_relevance_analyzer.typecheck.TypeFix`), but the operand
    survives inside it unchanged, and so do the positions within it.
    """
    old = before[edit.start : edit.end]
    if edit.replacement == _UNIQUE_VALUE + old:
        return len(_UNIQUE_VALUE)
    if edit.replacement == f"{_UNIQUE_VALUE}({old})":
        return len(_UNIQUE_VALUE) + 1
    return None


def _map_back(
    start: int, end: int, edits: Sequence[TextEdit], before: str | None = None
) -> tuple[int, int] | None:
    """Where ``[start, end)`` after ``edits`` sat before them.

    ``edits`` are one round's, sorted and disjoint, in pre-round offsets, and
    ``before`` is the text they were applied to. ``None`` when the range
    touches replaced text: that range did not exist before the round -- unless
    it lies within the operand a wrap kept verbatim (see :func:`_kept`), which
    did.
    """
    shift = 0
    for edit in edits:
        new_start = edit.start + shift
        new_end = new_start + len(edit.replacement)
        if end <= new_start:
            break
        if start >= new_end:
            shift += len(edit.replacement) - (edit.end - edit.start)
            continue
        kept = None if before is None else _kept(edit, before)
        if kept is None:
            return None
        inner = new_start + kept
        if not (inner <= start and end <= inner + (edit.end - edit.start)):
            return None
        return edit.start + start - inner, edit.start + end - inner
    return start - shift, end - shift


def _compose(
    original: str, earlier: Sequence[TextEdit], later: Sequence[TextEdit]
) -> tuple[TextEdit, ...]:
    """``earlier`` then ``later``, as one set of edits against ``original``.

    ``earlier`` is against ``original`` -- sorted, disjoint, not touching, as
    this returns -- and ``later`` is one round's edits against the text
    ``earlier`` produced. A later edit that overlaps or touches an earlier
    one, or another later one, is merged with it into one edit spanning both,
    which keeps the leftmost earlier edit's code (else the leftmost later
    one's): that is where the fix started.
    """
    current = _apply(original, earlier)

    # Every edit's range in `current`, earlier ones tagged 0 so a tie sorts
    # them first, along with how far each earlier one moved what follows it.
    ranges: list[tuple[int, int, int, TextEdit]] = []
    moved: list[tuple[int, int, int]] = []  # (current start, current end, shift after)
    shift = 0
    for edit in earlier:
        start = edit.start + shift
        end = start + len(edit.replacement)
        shift += len(edit.replacement) - (edit.end - edit.start)
        ranges.append((start, end, 0, edit))
        moved.append((start, end, shift))
    ranges += [(edit.start, edit.end, 1, edit) for edit in later]
    ranges.sort(key=lambda item: (item[0], item[1], item[2]))

    def to_original(position: int, *, at_start: bool) -> int:
        shift_before = 0
        for (start, end, shift_after), edit in zip(moved, earlier, strict=True):
            if position < start or (position == start and at_start):
                break
            if position <= end:
                # Only ever an edge of an earlier edit in the same cluster.
                return edit.start if position == start and at_start else edit.end
            shift_before = shift_after
        return position - shift_before

    composed: list[TextEdit] = []
    index = 0
    while index < len(ranges):
        start, end, _, _ = ranges[index]
        cluster = [ranges[index]]
        index += 1
        while index < len(ranges) and ranges[index][0] <= end:
            end = max(end, ranges[index][1])
            cluster.append(ranges[index])
            index += 1
        rewrites = [edit for _, _, tag, edit in cluster if tag == 1]
        if not rewrites:
            composed.append(cluster[0][3])
            continue
        replacement = _apply(
            current[start:end],
            [
                TextEdit(edit.start - start, edit.end - start, edit.replacement, edit.code)
                for edit in rewrites
            ],
        )
        first = next((edit for _, _, tag, edit in cluster if tag == 0), rewrites[0])
        original_start = to_original(start, at_start=True)
        original_end = to_original(end, at_start=False)
        if original[original_start:original_end] != replacement:
            composed.append(TextEdit(original_start, original_end, replacement, first.code))
    return tuple(composed)


@dataclass(frozen=True, slots=True)
class _State:
    """One accepted text, with how it was reached from the original."""

    text: str
    report: RelevanceAnalysis
    applied: Counter[str]
    rounds: tuple[tuple[TextEdit, ...], ...] = ()
    round_texts: tuple[str, ...] = ()
    """The text each of :attr:`rounds` was applied to, in step with it."""
    edits: tuple[TextEdit, ...] = ()
    """Every round's edits composed, against the original -- see :func:`_compose`."""


class _Guard:
    """Whether a candidate is no worse than the original."""

    def __init__(
        self, original: RelevanceAnalysis, guard: Guard, codes: Collection[str] | None = None
    ) -> None:
        from bigfix_relevance_analyzer.lint import LintConfig, Severity

        # The default configuration's severities: the guard judges by what a
        # plain lint run would report, not by any one caller's overrides.
        self._config = LintConfig()
        self._counted = (
            {Severity.ERROR} if guard == "errors" else {Severity.ERROR, Severity.WARNING}
        )
        self.original = original
        self._codes = codes
        self._round_baseline = self.problems(original, fixable=False)
        self._full_baseline = self.problems(original, fixable=True)
        self._original_fixes = {
            (diagnostic.fix.start, diagnostic.fix.end)
            for diagnostic in _fixable(original, codes)
            if diagnostic.fix is not None
        }
        self._required = _singular_required(original)

    def _counts(self, rule: str) -> bool:
        return self._config.severity_for(rule) in self._counted

    def problems(self, report: RelevanceAnalysis, *, fixable: bool) -> Counter[str]:
        """Per-code problem counts, for the codes this guard counts.

        Keyed by lint rule for the lexical and naming problems, and by checker
        code for diagnostics, so trading one type error for another is still
        caught.
        """
        found: Counter[str] = Counter()
        if report.parse_error is not None and self._counts("parse-error"):
            found["parse-error"] += 1
        if self._counts("error-token"):
            found["error-token"] += len(report.error_tokens)
        if self._counts("unknown-inspector"):
            found["unknown-inspector"] += len(report.unknown_references)
        if report.check is not None:
            for diagnostic in report.check.diagnostics:
                if diagnostic.fix is not None and not fixable:
                    continue
                if self._counts(_rule_for(diagnostic.code)):
                    found[diagnostic.code] += 1
        return +found  # drop zeros

    def _same_meaning(self, report: RelevanceAnalysis) -> bool:
        original = self.original
        if report.dialect is not original.dialect:
            return False
        if report.resolved_dialect is not original.resolved_dialect:
            return False
        if (report.check is None) != (original.check is None):
            return False
        if report.check is None or original.check is None:
            return True
        before, after = original.check.value, report.check.value
        if after.types == before.types and after.plurality is before.plurality:
            return True
        # The one licensed change: a plural where the engine requires a
        # singular is being repaired. The original never runs, so its
        # plurality is nothing to keep. Licensed by the count going down, not
        # by which edit made the change -- every other check still applies.
        return _singular_required(report) < self._required and _narrowed(before.types, after.types)

    def accepts(self, report: RelevanceAnalysis) -> bool:
        """The per-round check: fix-carrying diagnostics are not counted."""
        found = self.problems(report, fixable=False)
        return self._same_meaning(report) and all(
            count <= self._round_baseline[code] for code, count in found.items()
        )

    def final(self, state: _State) -> bool:
        """The full check: fix-carrying diagnostics counted, none introduced."""
        found = self.problems(state.report, fixable=True)
        if not self._same_meaning(state.report) or any(
            count > self._full_baseline[code] for code, count in found.items()
        ):
            return False
        for diagnostic in _fixable(state.report, self._codes):
            assert diagnostic.fix is not None
            span: tuple[int, int] | None = (diagnostic.fix.start, diagnostic.fix.end)
            for edits, before in zip(
                reversed(state.rounds), reversed(state.round_texts), strict=True
            ):
                if span is None:
                    break
                span = _map_back(*span, edits, before)
            if span not in self._original_fixes:
                return False
        return True


def _singular_required(report: RelevanceAnalysis) -> int:
    """How many plurals ``report`` has where the engine requires a singular."""
    if report.check is None:
        return 0
    return sum(diagnostic.code in SINGULAR_REQUIRED for diagnostic in report.check.diagnostics)


def _narrowed(before: frozenset[str] | None, after: frozenset[str] | None) -> bool:
    """Whether ``after`` claims nothing ``before`` did not, give or take
    multiplicity.

    `unique value of X` answers `<type> with multiplicity` -- the engine's own
    type for it, qna's `I:` line -- which every operator takes as `<type>`, so
    that spelling of a type ``before`` had is not a new type. An undetermined
    ``before`` constrains nothing.
    """
    if before is None:
        return True
    if after is None:
        return False
    return after <= before | {f"{name} with multiplicity" for name in before}


def _autofix(
    original: RelevanceAnalysis,
    dialect: Dialect | None,
    platform: str | None,
    guard: Guard,
    max_rounds: int,
    codes: Collection[str] | None = None,
) -> AutofixResult:
    if guard not in _GUARDS:
        raise ValueError(f"guard must be one of {sorted(_GUARDS)}, not {guard!r}")
    if max_rounds < 0:
        raise ValueError(f"max_rounds must not be negative, not {max_rounds}")

    def analysed(text: str) -> RelevanceAnalysis:
        return analyze(text, dialect, platform)

    # Cheap exit for the overwhelmingly common case: nothing proposes a fix.
    if not _edits(original, codes):
        return AutofixResult(original=original.text, fixed=original.text)

    judge = _Guard(original, guard, codes)
    states = [_State(original.text, original, Counter())]
    seen = {original.text}
    for _ in range(max_rounds):
        current = states[-1]
        edits = _disjoint(_edits(current.report, codes))
        if not edits:
            break
        text = _apply(current.text, edits)
        report = analysed(text)
        if judge.accepts(report):
            accepted = edits
        else:
            # Something in the batch made it worse. Find out what, one edit at
            # a time, from the right so earlier offsets stay valid.
            accepted = []
            text, report = current.text, current.report
            for edit in reversed(edits):
                attempt = _apply(text, [edit])
                attempt_report = analysed(attempt)
                if judge.accepts(attempt_report):
                    accepted.append(edit)
                    text, report = attempt, attempt_report
            accepted.sort(key=lambda edit: edit.start)
        if not accepted or text == current.text or text in seen:
            break
        seen.add(text)
        states.append(
            _State(
                text,
                report,
                current.applied + Counter(edit.code for edit in accepted),
                (*current.rounds, tuple(accepted)),
                (*current.round_texts, current.text),
                _compose(original.text, current.edits, accepted),
            )
        )

    # The original always passes against itself, so this always finds one.
    final = next(state for state in reversed(states) if judge.final(state))
    return AutofixResult(
        original=original.text,
        fixed=final.text,
        applied=dict(sorted(final.applied.items())),
        unapplied=dict(sorted(Counter(d.code for d in _fixable(final.report, codes)).items())),
        rounds=len(final.rounds),
        edits=final.edits,
    )


def autofix(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    guard: Guard = "warnings",
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    codes: Collection[str] | None = None,
) -> AutofixResult:
    """Apply every safe fix to ``text``, cascades included, and report the result.

    ``dialect`` and ``platform`` mean what they do for
    :func:`~bigfix_relevance_analyzer.analyzer.analyze`, and every round is
    analysed with the same pair. ``guard`` is what a fix may not add more of;
    see :data:`Guard`. ``max_rounds`` bounds the cascade; one reached
    mid-cascade falls back to the last state that passes the full check,
    which may be the original. ``codes`` limits the fixes applied to those
    checker codes; ``None``, the default, applies every fix.

    Raises :class:`ValueError` only for a bad ``guard`` or ``max_rounds`` --
    never for bad relevance, which simply has nothing to fix.
    """
    return _autofix(analyze(text, dialect, platform), dialect, platform, guard, max_rounds, codes)
