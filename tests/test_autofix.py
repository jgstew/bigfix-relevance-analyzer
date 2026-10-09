"""Tests for analyzer-side auto-fix (:mod:`bigfix_relevance_analyzer.autofix`).

The analyzer works out the fully fixed statement itself, as one final result,
so a hook only has to print it (auto-fix off) or swap it in (auto-fix on).
`singular-spelling-mid-chain` and the singular-required codes (#66) carry a
fix; everything else here is the machinery that keeps a fix from making a
statement worse.

The engine facts these lean on were confirmed live in qna::

    Q: number of names of files of folder "etc" of folder "private" of folder "/"
    A: 58
    Q: number of names of files of folders "etc" of folders "private" of folder "/"
    A: 58
    Q: exists values of  Setting  "_zz_none" of client
    E: Singular expression refers to nonexistent object.
    Q: exists values of  settings  "_zz_none" of client
    A: False

With "zz" in place of "etc" the singular errors (nonexistent object) where the
plural answers 0 -- which is the whole reason the plural is preferred.
"""

from __future__ import annotations

import itertools
import json
from typing import cast

import pytest
from _helpers import MID_CHAIN, SETTING

from bigfix_relevance_analyzer import autofix as autofix_module
from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.autofix import AutofixResult, TextEdit, autofix
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import LintConfig, lint_analysis

CASCADE = 'number of names of files of folder "etc" of folder "private" of folder "/"'
CASCADE_FIXED = 'number of names of files of folders "etc" of folders "private" of folder "/"'


# -- the fix the checker attaches ------------------------------------------------


def test_the_mid_chain_diagnostic_carries_a_fix_on_the_written_name() -> None:
    """The range is the property name as written, up to its index; the
    replacement is the plural spelling."""
    report = analyze(SETTING, Dialect.CLIENT)
    assert report.check is not None
    (diagnostic,) = report.check.diagnostics
    assert diagnostic.code == MID_CHAIN
    fix = diagnostic.fix
    assert fix is not None
    assert SETTING[fix.start : fix.end].strip() == "setting"
    assert fix.replacement == "settings"
    assert fix.expected == "setting"


def test_filtered_singular_spelling_carries_no_fix() -> None:
    """It fires in singular contexts, where pluralizing would add a W601."""
    report = analyze('exists values of setting "x" whose (true) of client', Dialect.CLIENT)
    assert report.check is not None
    (diagnostic,) = report.check.diagnostics
    assert diagnostic.code == "filtered-singular-spelling"
    assert diagnostic.fix is None


# -- autofix() -------------------------------------------------------------------


def test_a_single_fix() -> None:
    result = autofix(SETTING, Dialect.CLIENT)
    assert result.original == SETTING
    assert result.fixed == 'exists values of settings "x" of client'
    assert result.changed
    assert result.applied == {MID_CHAIN: 1}
    assert result.unapplied == {}
    assert result.rounds == 1


def test_spacing_and_case_around_the_name_are_kept() -> None:
    """Whitespace around the name survives; the name itself becomes the
    plural spelling, lower-cased like every table phrase."""
    text = 'exists values of  Setting  "x" of client'
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == 'exists values of  settings  "x" of client'
    assert result.applied == {MID_CHAIN: 1}


def test_a_cascade_takes_two_rounds() -> None:
    """Fixing `folder "etc"` makes `folder "private"` fire next round; the
    root `folder "/"` is never flagged."""
    result = autofix(CASCADE, Dialect.CLIENT)
    assert result.fixed == CASCADE_FIXED
    assert result.applied == {MID_CHAIN: 2}
    assert result.unapplied == {}
    assert result.rounds == 2


def test_two_fixes_in_one_round() -> None:
    text = 'exists values of setting "x" of client or exists values of setting "y" of client'
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == (
        'exists values of settings "x" of client or exists values of settings "y" of client'
    )
    assert result.applied == {MID_CHAIN: 2}
    assert result.rounds == 1


@pytest.mark.parametrize(
    "text",
    [
        'exists values of settings "x" of client',  # nothing to fix
        "exists files (",  # does not parse
    ],
)
def test_nothing_to_fix_leaves_the_text_unchanged(text: str) -> None:
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert not result.changed
    assert result.applied == {}
    assert result.unapplied == {}
    assert result.rounds == 0


def test_an_unfixable_error_carries_through() -> None:
    """A fix does not have to clear every problem, only not add one."""
    text = SETTING + " and 1"
    report = analyze(text, Dialect.CLIENT)
    assert report.check is not None
    assert [d.code for d in report.check.diagnostics] == [MID_CHAIN, "right-operand-not-boolean"]

    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == 'exists values of settings "x" of client and 1'
    assert result.applied == {MID_CHAIN: 1}
    fixed = analyze(result.fixed, Dialect.CLIENT)
    assert fixed.check is not None
    assert [d.code for d in fixed.check.diagnostics] == ["right-operand-not-boolean"]


def test_max_rounds_one_on_the_cascade_falls_back_to_the_original() -> None:
    """Half a cascade is not a final result: the first round only moves the
    finding one step down the chain, so the original is what is reported."""
    result = autofix(CASCADE, Dialect.CLIENT, max_rounds=1)
    assert result.fixed == CASCADE
    assert not result.changed
    assert result.applied == {}
    assert result.unapplied == {MID_CHAIN: 1}
    assert result.rounds == 0


# -- the guard -------------------------------------------------------------------


def _force(monkeypatch: pytest.MonkeyPatch, old: str, new: str, *, only_if: str) -> None:
    """Make `_edits` propose replacing the first ``old`` with ``new``, whenever
    the text still contains ``only_if``."""

    def forced(report: RelevanceAnalysis) -> tuple[TextEdit, ...]:
        if only_if not in report.text:
            return ()
        start = report.text.index(old)
        return (TextEdit(start, start + len(old), new, "forced"),)

    monkeypatch.setattr(autofix_module, "_edits", forced)


def test_the_guard_rejects_an_edit_that_adds_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    text = "exists client"
    _force(monkeypatch, "client", "client + 1", only_if="exists client")
    worse = analyze("exists client + 1", Dialect.CLIENT).check
    assert worse is not None
    assert [d.code for d in worse.diagnostics] == ["binary-operator-not-defined"]
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}
    assert result.rounds == 0


def test_the_guard_rejects_an_edit_that_adds_an_unknown_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text = "exists client"
    _force(monkeypatch, "client", "clientzz", only_if="exists client")
    assert analyze("exists clientzz", Dialect.CLIENT).unknown_references == ("clientzz",)
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}


def test_the_guard_counts_warnings_by_default_but_not_with_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`files` -> `file` over a plural object adds `singular-over-plural-object`,
    a warning: rejected by default, accepted when only errors are guarded."""
    text = 'names of files of folders "/"'
    worse = 'names of file of folders "/"'
    _force(monkeypatch, "files", "file", only_if="files")

    assert autofix(text, Dialect.CLIENT).fixed == text

    result = autofix(text, Dialect.CLIENT, guard="errors")
    assert result.fixed == worse
    assert result.applied == {"forced": 1}


def test_a_failing_round_keeps_the_edits_that_pass_on_their_own(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One bad edit in a batch does not sink the good ones beside it."""
    real_edits = autofix_module._edits

    def with_a_bad_one(report: RelevanceAnalysis) -> tuple[TextEdit, ...]:
        start = report.text.index("client")
        bad = TextEdit(start, start + len("client"), "clientzz", "forced")
        return (*real_edits(report), bad)

    monkeypatch.setattr(autofix_module, "_edits", with_a_bad_one)
    result = autofix(SETTING, Dialect.CLIENT)
    assert result.fixed == 'exists values of settings "x" of client'
    assert result.applied == {MID_CHAIN: 1}
    assert result.rounds == 1


def test_an_unknown_guard_is_refused() -> None:
    with pytest.raises(ValueError, match="guard"):
        autofix(SETTING, Dialect.CLIENT, guard="everything")  # type: ignore[arg-type]


# -- edits against the original --------------------------------------------------


def _assert_edits_rebuild_fixed(result: AutofixResult) -> None:
    """The invariant a consumer writing the fix back relies on."""
    assert autofix_module._apply(result.original, result.edits) == result.fixed
    for left, right in itertools.pairwise(result.edits):
        assert left.end < right.start, "edits are sorted, disjoint and not touching"


def test_a_single_fix_has_one_edit_on_the_original() -> None:
    result = autofix(SETTING, Dialect.CLIENT)
    (edit,) = result.edits
    assert SETTING[edit.start : edit.end] == "setting"
    assert edit.replacement == "settings"
    assert edit.code == MID_CHAIN
    _assert_edits_rebuild_fixed(result)


def test_a_cascade_reports_every_rounds_edit_against_the_original() -> None:
    """The second round's edit sits after the first's, so its offsets moved;
    reported against the original, both point at what was written."""
    result = autofix(CASCADE, Dialect.CLIENT)
    assert result.rounds == 2
    assert [(CASCADE[edit.start : edit.end], edit.replacement) for edit in result.edits] == [
        ("folder", "folders"),
        ("folder", "folders"),
    ]
    _assert_edits_rebuild_fixed(result)


def test_two_fixes_in_one_round_are_two_edits() -> None:
    text = 'exists values of setting "x" of client or exists values of setting "y" of client'
    result = autofix(text, Dialect.CLIENT)
    assert len(result.edits) == 2
    _assert_edits_rebuild_fixed(result)


@pytest.mark.parametrize("text", ['exists values of settings "x" of client', "exists files ("])
def test_nothing_fixed_has_no_edits(text: str) -> None:
    assert autofix(text, Dialect.CLIENT).edits == ()


def test_a_fallback_to_the_original_has_no_edits() -> None:
    assert autofix(CASCADE, Dialect.CLIENT, max_rounds=1).edits == ()


def test_a_later_edit_overlapping_an_earlier_one_merges_into_it() -> None:
    """`setting` -> `settings`, then `settings` -> `settingz`: one edit."""
    original = "a setting b"
    first = (TextEdit(2, 9, "settings", "one"),)
    second = (TextEdit(2, 10, "settingz", "two"),)
    composed = autofix_module._compose(
        original, autofix_module._compose(original, (), first), second
    )
    assert composed == (TextEdit(2, 9, "settingz", "one"),)
    assert autofix_module._apply(original, composed) == "a settingz b"


def test_a_later_edit_touching_an_earlier_one_merges_into_it() -> None:
    original = "a setting b"
    first = (TextEdit(2, 9, "settings", "one"),)
    second = (TextEdit(10, 11, "_", "two"),)  # the space after `settings`
    composed = autofix_module._compose(
        original, autofix_module._compose(original, (), first), second
    )
    assert composed == (TextEdit(2, 10, "settings_", "one"),)
    assert autofix_module._apply(original, composed) == "a settings_b"


def test_composition_rebuilds_every_round_of_random_edits() -> None:
    """Whatever the rounds, the composed edits turn the original into the last text."""
    import random

    rng = random.Random(1234)
    for _ in range(500):
        original = "".join(rng.choice("abc ") for _ in range(rng.randrange(1, 30)))
        text = original
        composed: tuple[TextEdit, ...] = ()
        for _ in range(rng.randrange(1, 5)):
            cuts = sorted(rng.sample(range(len(text) + 1), min(len(text) + 1, 4)))
            edits = tuple(
                TextEdit(start, end, rng.choice(["", "x", "yy", "zzz"]), "r")
                for start, end in zip(cuts[::2], cuts[1::2], strict=False)
                if end > start
            )
            text = autofix_module._apply(text, edits)
            composed = autofix_module._compose(original, composed, edits)
            assert autofix_module._apply(original, composed) == text, (original, composed)
            for left, right in itertools.pairwise(composed):
                assert left.end < right.start


def test_applied_rules_names_the_lint_rule_of_each_applied_code() -> None:
    assert autofix(CASCADE, Dialect.CLIENT).applied_rules == {"plural-preferred": 2}
    assert autofix("exists files (", Dialect.CLIENT).applied_rules == {}


# -- serialization ---------------------------------------------------------------


def test_to_dict_shape() -> None:
    result = autofix(CASCADE, Dialect.CLIENT)
    payload = result.to_dict()
    assert payload == {
        "original": CASCADE,
        "fixed": CASCADE_FIXED,
        "changed": True,
        "rounds": 2,
        "applied": [{"code": MID_CHAIN, "rule": "plural-preferred", "count": 2}],
        "unapplied": [],
        "edits": [
            {
                "start": edit.start,
                "end": edit.end,
                "replacement": "folders",
                "code": MID_CHAIN,
                "rule": "plural-preferred",
            }
            for edit in result.edits
        ],
    }
    assert len(payload["edits"]) == 2
    json.dumps(payload)


def test_the_analysis_payload_carries_the_autofix() -> None:
    fixable = analyze(SETTING, Dialect.CLIENT)
    assert isinstance(fixable.autofix(), AutofixResult)
    assert fixable.to_dict()["autofix"] == autofix(SETTING, Dialect.CLIENT).to_dict()

    clean = analyze('exists values of settings "x" of client', Dialect.CLIENT)
    assert clean.to_dict()["autofix"] is None


# -- lint ------------------------------------------------------------------------


def test_lint_attaches_the_autofix_to_the_fixable_finding_only() -> None:
    report = analyze(SETTING + " and 1", Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    by_code = {finding.code: finding for finding in findings}

    fixable = by_code["plural-preferred"]
    assert fixable.autofix is not None
    assert fixable.autofix.fixed == 'exists values of settings "x" of client and 1'
    assert fixable.to_dict()["autofix"] == fixable.autofix.to_dict()

    other = by_code["type-error"]
    assert other.autofix is None
    assert other.to_dict()["autofix"] is None


def test_lint_attaches_nothing_to_filtered_singular_spelling() -> None:
    report = analyze('exists values of setting "x" whose (true) of client', Dialect.CLIENT)
    (finding,) = lint_analysis(report, LintConfig())
    assert finding.code == "plural-preferred"
    assert finding.autofix is None
    assert finding.to_dict()["autofix"] is None


# -- a plural where a singular is required (#66) --------------------------------
#
# The engine refuses a plural operand before evaluating anything -- `A
# singular expression is required.` -- so the original can never run. The fix
# respells a plural aggregate as its singular, else wraps the operand in
# `unique value of`. Engine evidence for every pair here is on #66.

LEFT = "left-operand-not-singular"
RIGHT = "right-operand-not-singular"
ARGUMENT = "argument-not-singular"

NIRCMD = (
    '(integer values of selects "CurrentBrightness FROM WmiMonitorBrightness WHERE Active=True"'
    ' of wmis "ROOT/WMI") != ( maxima of (it; 5) ) of ( minima of (it; 100) ) of'
    ' ( ((it as integer) of (parameter "iDesiredBrightness")) | 0 )'
)
"""`fixlet/NirCmd - setbrightness - Windows.bes:41` in bigfix-content: a
SuccessCriteria that can never evaluate, plural on both sides of `!=`. The
right side is plural too, though it holds at most one value: the grouped
`maxima` is written plural, and qna refuses `7 != ( maxima of (it; 5) ) of
...` with `A singular expression is required.`"""


SINGULAR_REQUIRED_CASES = [
    pytest.param(
        'pathnames of files "x" | pathnames of files "y"',
        Dialect.CLIENT,
        'unique value of pathnames of files "x" | unique value of pathnames of files "y"',
        {LEFT: 1, RIGHT: 1},
        id="both-operands-one-round",
    ),
    pytest.param(
        'pathnames of files "x" | "y"',
        Dialect.CLIENT,
        'unique value of pathnames of files "x" | "y"',
        {LEFT: 1},
        id="left-only",
    ),
    pytest.param(
        '"y" | pathnames of files "x"',
        Dialect.CLIENT,
        '"y" | unique value of pathnames of files "x"',
        {RIGHT: 1},
        id="right-only",
    ),
    pytest.param(
        '"x" & pathnames of files "y"',
        Dialect.CLIENT,
        '"x" & unique value of pathnames of files "y"',
        {RIGHT: 1},
        id="ampersand",
    ),
    pytest.param(
        '(sizes of files "x") + 1',
        Dialect.CLIENT,
        'unique value of (sizes of files "x") + 1',
        {LEFT: 1},
        id="plus",
    ),
    pytest.param(
        '- sizes of files "x"',
        Dialect.CLIENT,
        '- unique value of sizes of files "x"',
        {ARGUMENT: 1},
        id="unary-minus",
    ),
    pytest.param(
        '(concatenations ", " of pathnames of files "x") | "y"',
        Dialect.CLIENT,
        '(concatenation ", " of pathnames of files "x") | "y"',
        {LEFT: 1},
        id="aggregate-respelled",
    ),
    pytest.param(
        'pathnames /* keep me */ of files "x" | "y"',
        Dialect.CLIENT,
        'unique value of pathnames /* keep me */ of files "x" | "y"',
        {LEFT: 1},
        id="comment-kept",
    ),
    pytest.param(
        'pathnames of files "x" as lowercase = "y"',
        Dialect.CLIENT,
        'unique value of (pathnames of files "x" as lowercase) = "y"',
        {LEFT: 1},
        id="cast-parenthesized",
    ),
    pytest.param(
        "(bes computers) | (unique value of bes computers)",
        Dialect.SESSION,
        "unique value of (bes computers) | (unique value of bes computers)",
        {LEFT: 1},
        id="session-bes-computers-accepted",
    ),
    pytest.param(
        NIRCMD,
        Dialect.CLIENT,
        "unique value of " + NIRCMD.replace(" != ", " != unique value of ", 1),
        {LEFT: 1, RIGHT: 1},
        id="corpus-nircmd",
    ),
]
"""One statement per shape the singular-required fix takes, with what it gives."""


@pytest.mark.parametrize(("text", "dialect", "fixed", "applied"), SINGULAR_REQUIRED_CASES)
def test_a_plural_in_a_singular_position_is_fixed(
    text: str, dialect: Dialect, fixed: str, applied: dict[str, int]
) -> None:
    result = autofix(text, dialect)
    assert result.fixed == fixed
    assert result.applied == applied
    assert result.unapplied == {}
    assert result.rounds == 1
    _assert_edits_rebuild_fixed(result)
    after = analyze(result.fixed, dialect).check
    assert after is not None
    assert not [d.code for d in after.diagnostics if d.code in (LEFT, RIGHT, ARGUMENT)]


def test_a_wrap_whose_range_no_longer_holds_the_operand_is_skipped() -> None:
    """The anchoring rule, for a whole-operand fix: the range has to read as
    the operand the checker saw, or nothing is edited."""
    text = 'pathnames of files "x" | "y"'
    report = analyze(text, Dialect.CLIENT)
    assert report.check is not None
    (diagnostic,) = report.check.diagnostics
    fix = diagnostic.fix
    assert fix is not None
    assert autofix_module._anchored(text, fix, diagnostic.code) is not None
    moved = 'pathnames of files "z" | "y"'  # same length, different operand
    assert autofix_module._anchored(moved, fix, diagnostic.code) is None


def test_a_wrap_that_adds_property_not_defined_is_rejected() -> None:
    """Client `unique value of` takes no `file`: qna `exists unique value of
    (files of folders "zz_none")` is `The operator "unique value" is not
    defined.` The guard sees the new `property-not-defined` and keeps the
    original, counting the fix as unapplied."""
    text = '(files "hosts" of folders "/etc") | file "/etc/hosts"'
    wrapped = analyze("unique value of " + text, Dialect.CLIENT).check
    assert wrapped is not None
    assert "property-not-defined" in [d.code for d in wrapped.diagnostics]

    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}
    assert result.unapplied == {LEFT: 1}
    assert result.edits == ()


def test_a_tuple_operand_is_left_alone() -> None:
    """No aggregate is defined on a tuple (qna: `unique value of ("a", "b")`
    is `The operator "unique value" is not defined.`), so nothing is offered."""
    text = '(pathnames of files "x", 1) = ("a", 1)'
    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}


def test_the_wrap_changes_plurality_and_adds_only_with_multiplicity() -> None:
    """What the relaxed guard has to allow, pinned rather than assumed. The
    engine types `unique value of X` as `<type> with multiplicity` (qna `I:`
    line: `unique value of (1;1)` is `integer with multiplicity`, `maximum of
    (1;2)` is `integer`), and the checker agrees -- so a wrap does not merely
    narrow, it adds that one spelling of each type it already had."""
    text = 'pathnames of files "x" | pathnames of files "y"'
    before = analyze(text, Dialect.CLIENT).check
    after = analyze(autofix(text, Dialect.CLIENT).fixed, Dialect.CLIENT).check
    assert before is not None and after is not None
    assert before.value.types == frozenset({"string"})
    # Both sides wrapped, so every candidate is the multiplicity spelling.
    assert after.value.types == frozenset({"string with multiplicity"})
    assert before.value.plurality.value == "plural"
    assert after.value.plurality.value == "singular"


def test_a_respelling_keeps_the_type() -> None:
    text = '(concatenations ", " of pathnames of files "x") | "y"'
    before = analyze(text, Dialect.CLIENT).check
    after = analyze(autofix(text, Dialect.CLIENT).fixed, Dialect.CLIENT).check
    assert before is not None and after is not None
    assert after.value.types is not None and before.value.types is not None
    assert after.value.types <= before.value.types


def test_a_plurality_change_elsewhere_is_still_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """The relaxation is for the repair, not for any edit in a statement that
    happens to need one: this edit changes the result's plurality and leaves
    the singular-required diagnostic standing, so the strict check applies."""
    text = 'if (pathnames of files "x" | "y") = "z" then name of file "a" else "b"'
    _force(monkeypatch, "name of file", "names of file", only_if="name of file")
    report = analyze(text.replace("name of file", "names of file"), Dialect.CLIENT)
    assert report.check is not None
    assert [d.code for d in report.check.diagnostics] == [LEFT]
    original = analyze(text, Dialect.CLIENT).check
    assert original is not None
    assert report.check.value.plurality is not original.value.plurality

    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}


def test_a_repair_may_not_change_the_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fewer singular-required diagnostics licenses a plurality change, not a
    new type: this rewrite repairs both operands and adds no problem, but
    answers integers where the original answered strings."""
    text = 'pathnames of files "x" | pathnames of files "y"'
    other = 'unique value of sizes of files "x" | unique value of sizes of files "y"'
    _force(monkeypatch, text, other, only_if="pathnames")
    report = analyze(other, Dialect.CLIENT)
    assert report.check is not None
    assert report.check.diagnostics == ()
    assert report.check.value.types == frozenset({"integer with multiplicity"})

    result = autofix(text, Dialect.CLIENT)
    assert result.fixed == text
    assert result.applied == {}


def test_no_back_and_forth_with_the_mid_chain_plural_fix() -> None:
    """Both fixes in one statement: the wrap goes first (it starts first and
    the inner respelling overlaps it), the respelling the round after, and
    neither undoes the other -- a loop would spend every round."""
    text = '"x" & values of setting "y" of client'
    report = analyze(text, Dialect.CLIENT)
    assert report.check is not None
    assert sorted(d.code for d in report.check.diagnostics) == [RIGHT, MID_CHAIN]

    result = autofix(text, Dialect.CLIENT, max_rounds=8)
    assert result.fixed == '"x" & unique value of values of settings "y" of client'
    assert result.applied == {RIGHT: 1, MID_CHAIN: 1}
    assert result.unapplied == {}
    assert result.rounds == 2
    _assert_edits_rebuild_fixed(result)


def test_a_wrap_survives_a_round_limit_before_the_respelling_inside_it() -> None:
    """The mid-chain diagnostic still standing after round one is the original
    one, carried inside the wrapped operand -- not one the wrap introduced --
    so the wrap is a final result on its own."""
    text = '"x" & values of setting "y" of client'
    result = autofix(text, Dialect.CLIENT, max_rounds=1)
    assert result.fixed == '"x" & unique value of values of setting "y" of client'
    assert result.applied == {RIGHT: 1}
    assert result.unapplied == {MID_CHAIN: 1}
    assert result.rounds == 1


def test_the_new_rule_names_itself_in_to_dict() -> None:
    payload = autofix('pathnames of files "x" | "y"', Dialect.CLIENT).to_dict()
    assert payload["applied"] == [{"code": LEFT, "rule": "singular-required", "count": 1}]


# -- CLI and package surface -----------------------------------------------------


@pytest.mark.parametrize("flags", [[], ["--verbose"]])
def test_the_cli_shows_the_suggested_relevance_and_applied_counts(
    flags: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--markdown", *flags, "--dialect", "client", CASCADE]) == 0
    out = capsys.readouterr().out
    assert "## Suggested fix" in out
    assert f"```\n{CASCADE_FIXED}\n```" in out
    assert f"- applied 2 `{MID_CHAIN}` (`plural-preferred`) over 2 rounds" in out


def test_the_cli_shows_no_suggested_fix_when_nothing_fixes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--markdown", "--dialect", "client", CASCADE_FIXED]) == 0
    assert "Suggested fix" not in capsys.readouterr().out


def test_autofix_is_exported_from_the_package() -> None:
    import bigfix_relevance_analyzer as package

    assert package.autofix_relevance is autofix
    assert package.AutofixResult is AutofixResult


# -- minimal pieces: what a fix writes into a file (#115) -------------------------
#
# A wrap's edit replaces the whole operand with a copy of itself behind
# `unique value of`, and that copy is the *decoded* statement: written back
# into a file whole, it would un-escape whatever the author escaped (`&lt;` in
# BES XML, `\"` in a JavaScript string). `_pieces` splits every edit into the
# smallest changes that turn the original into the fixed text, so what a fix
# writes is only ever new text, never anything copied from the statement.


def _hand_built(original: str, *edits: TextEdit) -> AutofixResult:
    return AutofixResult(
        original=original, fixed=autofix_module._apply(original, edits), edits=edits
    )


def _assert_pieces_rebuild_fixed(result: AutofixResult) -> tuple[TextEdit, ...]:
    """The invariants the byte mapping relies on; returns the pieces."""
    pieces = autofix_module._pieces(result)
    assert autofix_module._apply(result.original, pieces) == result.fixed, result
    for left, right in itertools.pairwise(pieces):
        assert left.end <= right.start and left.start < right.start, pieces
    by_edit = {edit.code for edit in result.edits}
    for piece in pieces:
        assert piece.code in by_edit
        assert any(edit.start <= piece.start <= piece.end <= edit.end for edit in result.edits)
        assert autofix_module._SAFE_TEXT.fullmatch(piece.replacement), piece
    return pieces


def test_a_respelling_is_one_insertion() -> None:
    pieces = _assert_pieces_rebuild_fixed(autofix(SETTING, Dialect.CLIENT))
    assert pieces == (TextEdit(24, 24, "s", MID_CHAIN),)
    assert SETTING[:24].endswith("setting")


@pytest.mark.parametrize(
    ("word", "fixed", "piece"),
    [
        pytest.param("property", "properties", (7, 8, "ies"), id="y-to-ies"),
        pytest.param("analysis", "analyses", (6, 7, "e"), id="i-to-e"),
        pytest.param("concatenations", "concatenation", (13, 14, ""), id="aggregate-singular"),
    ],
)
def test_a_respelling_inside_the_word_is_one_short_replacement(
    word: str, fixed: str, piece: tuple[int, int, str]
) -> None:
    """The real-content shapes that are not pure insertions (#115 S1)."""
    original = f'names of bes {word} "x"'
    start = original.index(word)
    result = _hand_built(original, TextEdit(start, start + len(word), fixed, MID_CHAIN))
    (only,) = _assert_pieces_rebuild_fixed(result)
    assert (only.start - start, only.end - start, only.replacement) == piece


def test_a_wrap_is_only_the_inserted_prefix() -> None:
    text = 'pathnames of files "x" | "y"'
    pieces = _assert_pieces_rebuild_fixed(autofix(text, Dialect.CLIENT))
    assert pieces == (TextEdit(0, 0, "unique value of ", "left-operand-not-singular"),)


def test_a_parenthesized_wrap_is_two_insertions() -> None:
    text = 'pathnames of files "x" as lowercase = "y"'
    pieces = _assert_pieces_rebuild_fixed(autofix(text, Dialect.CLIENT))
    end = text.index(" = ")
    assert [(p.start, p.end, p.replacement) for p in pieces] == [
        (0, 0, "unique value of ("),
        (end, end, ")"),
    ]


def test_a_merged_wrap_and_respelling_is_two_insertions_and_copies_no_quote() -> None:
    """A cascade merges these into one edit that is neither (#113 S2)."""
    text = 'names of files of folder "a" of folder "b" = "y"'
    result = autofix(text, Dialect.CLIENT)
    (edit,) = result.edits
    assert '"' in edit.replacement
    pieces = _assert_pieces_rebuild_fixed(result)
    folder = text.index('folder "a"') + len("folder")
    assert [(p.start, p.end, p.replacement) for p in pieces] == [
        (0, 0, "unique value of "),
        (folder, folder, "s"),
    ]
    assert not any('"' in piece.replacement for piece in pieces)


def test_nothing_fixed_has_no_pieces() -> None:
    assert autofix_module._pieces(autofix(SETTINGS_FIXED, Dialect.CLIENT)) == ()


SETTINGS_FIXED = 'exists values of settings "x" of client'


def _every_fixable_statement() -> list[tuple[str, Dialect | None]]:
    from _corpus import corpus_cases, extracted_sites

    statements: list[tuple[str, Dialect | None]] = [
        (SETTING, Dialect.CLIENT),
        (CASCADE, Dialect.CLIENT),
        *((str(case.values[0]), cast(Dialect, case.values[1])) for case in SINGULAR_REQUIRED_CASES),
        *((case.source, None) for case in corpus_cases()),
        *((site.text, site.dialect) for _, site in extracted_sites()),
    ]
    return statements


def test_every_fixable_statement_splits_into_safe_pieces() -> None:
    """Over this file's cases, the parse corpus and the examples: applying the
    pieces gives the fixed text, they are sorted and disjoint, keep their
    edit's code, and only ever write ``[A-Za-z0-9 ()]``."""
    fixed = 0
    for text, dialect in _every_fixable_statement():
        result = autofix(text, dialect)
        if result.edits:
            fixed += 1
            _assert_pieces_rebuild_fixed(result)
    assert fixed >= 15, "too few fixable statements for this to mean much"


def test_safe_text_is_names_spaces_and_parentheses_only() -> None:
    safe = autofix_module._SAFE_TEXT
    for text in ("", "s", "ies", "unique value of ", "unique value of (", ")", "Abc 123"):
        assert safe.fullmatch(text), text
    for text in ('"', "'", "&", "<", ">", "\\", "]]>", "?>", "}", "{", "\r", "\n", "\t", "\u00e9"):
        assert not safe.fullmatch(text), text


def test_difflib_is_imported_when_the_module_loads() -> None:
    """componentize-py snapshots only what is imported at build time, so a
    lazy ``import difflib`` inside ``_pieces`` would work here and fail in the
    VS Code extension. A module attribute is what only a top-level import sets."""
    import difflib

    assert getattr(autofix_module, "difflib", None) is difflib


# -- the rule an edit reports under (#115 A3) -------------------------------------


def test_an_edit_names_its_lint_rule() -> None:
    from bigfix_relevance_analyzer.lint import _rule_for

    for text, dialect in [(SETTING, Dialect.CLIENT), ('pathnames of files "x" | "y"', None)]:
        result = autofix(text, dialect)
        assert result.edits
        for edit, payload in zip(result.edits, result.to_dict()["edits"], strict=True):
            assert edit.rule == _rule_for(edit.code)
            assert payload["rule"] == edit.rule
    assert autofix(SETTING, Dialect.CLIENT).edits[0].rule == "plural-preferred"
