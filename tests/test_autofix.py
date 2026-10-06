"""Tests for analyzer-side auto-fix (:mod:`bigfix_relevance_analyzer.autofix`).

The analyzer works out the fully fixed statement itself, as one final result,
so a hook only has to print it (auto-fix off) or swap it in (auto-fix on).
Only `singular-spelling-mid-chain` carries a fix today; everything else here is
the machinery that keeps a fix from making a statement worse.

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
            {"start": edit.start, "end": edit.end, "replacement": "folders", "code": MID_CHAIN}
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
