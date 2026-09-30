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
what the statement evaluates to (its types or plurality). Fix-carrying
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
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, Literal

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze

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
the result's types and plurality must not change.
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

    @property
    def changed(self) -> bool:
        return self.fixed != self.original

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
        }


def _rule_for(code: str) -> str:
    # Imported here, not at module scope: `lint` imports `analyzer`, which
    # reaches this module from `RelevanceAnalysis.autofix`.
    from bigfix_relevance_analyzer.lint import _CHECK_RULES

    return _CHECK_RULES.get(code, "type-error")


def _normalized(phrase: str) -> str:
    return " ".join(phrase.split()).casefold()


def _anchored(text: str, fix: TypeFix, code: str) -> TextEdit | None:
    """``fix`` as an edit on ``text``, or ``None`` if its range does not hold
    the name it expects.

    The checker only has spans; this is where they meet the text. Whitespace
    at either end of the range is left in place, so `of  Setting  "x"` keeps
    its spacing.
    """
    written = text[fix.start : fix.end]
    name = written.strip()
    if not name or _normalized(name) != _normalized(fix.expected):
        return None
    start = fix.start + len(written) - len(written.lstrip())
    return TextEdit(start, start + len(name), fix.replacement, code)


def _fixable(report: RelevanceAnalysis) -> tuple[TypeDiagnostic, ...]:
    if report.check is None:
        return ()
    return tuple(diagnostic for diagnostic in report.check.diagnostics if diagnostic.fix)


def _edits(report: RelevanceAnalysis) -> tuple[TextEdit, ...]:
    """Every fix ``report``'s diagnostics carry, anchored to its text, in order."""
    found: set[TextEdit] = set()
    for diagnostic in _fixable(report):
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


def _map_back(start: int, end: int, edits: Sequence[TextEdit]) -> tuple[int, int] | None:
    """Where ``[start, end)`` after ``edits`` sat before them.

    ``edits`` are one round's, sorted and disjoint, in pre-round offsets.
    ``None`` when the range touches replaced text: that range did not exist
    before the round.
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
        return None
    return start - shift, end - shift


@dataclass(frozen=True, slots=True)
class _State:
    """One accepted text, with how it was reached from the original."""

    text: str
    report: RelevanceAnalysis
    applied: Counter[str]
    rounds: tuple[tuple[TextEdit, ...], ...] = ()


class _Guard:
    """Whether a candidate is no worse than the original."""

    def __init__(self, original: RelevanceAnalysis, guard: Guard) -> None:
        from bigfix_relevance_analyzer.lint import DEFAULT_SEVERITIES, Severity

        self._severities = DEFAULT_SEVERITIES
        self._default = Severity.WARNING
        self._counted = (
            {Severity.ERROR} if guard == "errors" else {Severity.ERROR, Severity.WARNING}
        )
        self.original = original
        self._round_baseline = self.problems(original, fixable=False)
        self._full_baseline = self.problems(original, fixable=True)
        self._original_fixes = {
            (diagnostic.fix.start, diagnostic.fix.end)
            for diagnostic in _fixable(original)
            if diagnostic.fix is not None
        }

    def _counts(self, rule: str) -> bool:
        return self._severities.get(rule, self._default) in self._counted

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
        return (
            report.check.value.types == original.check.value.types
            and report.check.value.plurality is original.check.value.plurality
        )

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
        for diagnostic in _fixable(state.report):
            assert diagnostic.fix is not None
            span: tuple[int, int] | None = (diagnostic.fix.start, diagnostic.fix.end)
            for edits in reversed(state.rounds):
                if span is None:
                    break
                span = _map_back(*span, edits)
            if span not in self._original_fixes:
                return False
        return True


def _autofix(
    original: RelevanceAnalysis,
    dialect: Dialect | None,
    platform: str | None,
    guard: Guard,
    max_rounds: int,
) -> AutofixResult:
    if guard not in _GUARDS:
        raise ValueError(f"guard must be one of {sorted(_GUARDS)}, not {guard!r}")
    if max_rounds < 0:
        raise ValueError(f"max_rounds must not be negative, not {max_rounds}")

    def analysed(text: str) -> RelevanceAnalysis:
        return analyze(text, dialect, platform)

    # Cheap exit for the overwhelmingly common case: nothing proposes a fix.
    if not _edits(original):
        return AutofixResult(original=original.text, fixed=original.text)

    judge = _Guard(original, guard)
    states = [_State(original.text, original, Counter())]
    seen = {original.text}
    for _ in range(max_rounds):
        current = states[-1]
        edits = _disjoint(_edits(current.report))
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
            )
        )

    # The original always passes against itself, so this always finds one.
    final = next(state for state in reversed(states) if judge.final(state))
    return AutofixResult(
        original=original.text,
        fixed=final.text,
        applied=dict(sorted(final.applied.items())),
        unapplied=dict(sorted(Counter(d.code for d in _fixable(final.report)).items())),
        rounds=len(final.rounds),
    )


def autofix(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    guard: Guard = "warnings",
    max_rounds: int = DEFAULT_MAX_ROUNDS,
) -> AutofixResult:
    """Apply every safe fix to ``text``, cascades included, and report the result.

    ``dialect`` and ``platform`` mean what they do for
    :func:`~bigfix_relevance_analyzer.analyzer.analyze`, and every round is
    analysed with the same pair. ``guard`` is what a fix may not add more of;
    see :data:`Guard`. ``max_rounds`` bounds the cascade; one reached
    mid-cascade falls back to the last state that passes the full check,
    which may be the original.

    Raises :class:`ValueError` only for a bad ``guard`` or ``max_rounds`` --
    never for bad relevance, which simply has nothing to fix.
    """
    return _autofix(analyze(text, dialect, platform), dialect, platform, guard, max_rounds)
