"""Tests for pluralizing singular spellings everywhere the plural is valid (#67).

Three tiers, by design (see the issue):

* **Analysis** reports `singular-spelling-pluralizable` and suggests its fix
  by default.
* **Lint / `--fix`**, default: the rule `plural-everywhere` is off, and its
  edits only *ride along* with another enabled fix of the same statement. A
  statement with no other fix is untouched, so a default `--fix` over a large
  repo changes exactly the statements it changed before.
* **Lint with the rule enabled**: fixed and reported everywhere.

Engine facts these lean on, confirmed on 20 client targets and in session
(#67 comments)::

    Q: exists files "x" of folder "zz_none"
    E: Singular expression refers to nonexistent object.
    Q: exists files "x" of folders "zz_none"
    A: False
    Q: number of name of file of folder "/etc"
    E: Singular expression refers to non-unique object.
    Q: number of names of files of folders "/etc"
    A: 58
    Q: names of operating systems = "x"
    E: A singular expression is required.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _helpers import SETTING

from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.fixfile import fix_file
from bigfix_relevance_analyzer.lint import (
    DEFAULT_SEVERITIES,
    RULES,
    LintConfig,
    Severity,
    lint_analysis,
)
from bigfix_relevance_analyzer.typecheck import Plurality

CODE = "singular-spelling-pluralizable"
RULE = "plural-everywhere"
ENABLED = LintConfig(severities={RULE: Severity.WARNING})

# Only pluralizable spellings: nothing the default rules fix.
ONLY_ROOT = 'exists files "hosts" of folder "/zz_none"'
ONLY_ROOT_FIXED = 'exists files "hosts" of folders "/zz_none"'

# A default `plural-preferred` fix (`file` -> `files`) plus a pluralizable root.
MIXED = 'exists file "hosts" of folder "/zz_none"'
MIXED_DEFAULT = 'exists files "hosts" of folder "/zz_none"'
MIXED_FULL = 'exists files "hosts" of folders "/zz_none"'


def codes(text: str) -> list[str]:
    report = analyze(text, Dialect.CLIENT)
    assert report.check is not None
    return [diagnostic.code for diagnostic in report.check.diagnostics]


def fixed(text: str) -> str:
    return analyze(text, Dialect.CLIENT).autofix().fixed


# -- where it fires -------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # The chain root below `exists`, which `singular-spelling-mid-chain`
        # never reaches.
        (ONLY_ROOT, ONLY_ROOT_FIXED),
        ("not " + ONLY_ROOT, "not " + ONLY_ROOT_FIXED),
        # Every link of a chain under `number of`, the property included.
        (
            'number of name of file of folder "/etc"',
            'number of names of files of folders "/etc"',
        ),
        # A plural aggregate's operand.
        (
            'unique values of names of files of folder "/etc"',
            'unique values of names of files of folders "/etc"',
        ),
        # Below a plural link anywhere: the result is plural either way.
        ('names of files of folder "/etc"', 'names of files of folders "/etc"'),
        # The subject of a `whose`, in those contexts.
        (
            'exists file whose (name of it = "hosts") of folder "/etc"',
            'exists files whose (name of it = "hosts") of folders "/etc"',
        ),
    ],
)
def test_pluralizes_where_the_plural_is_valid(text: str, expected: str) -> None:
    assert CODE in codes(text)
    assert fixed(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        # A comparison operand must stay singular: `names of operating
        # systems = "x"` is `A singular expression is required.`.
        'name of operating system = "x"',
        # An `if` condition.
        'if (name of operating system = "x") then 1 else 2',
        # Left of `|`, the singular's error is the fallback's trigger:
        # pluralizing would answer False where the fallback answered True.
        'exists files "hosts" of folder "/zz_none" | true',
        # A bare singular value the statement returns.
        "name of operating system",
    ],
)
def test_does_not_fire_where_a_singular_is_required(text: str) -> None:
    assert CODE not in codes(text)


def test_the_diagnostic_carries_a_respelling_of_the_written_name() -> None:
    report = analyze(ONLY_ROOT, Dialect.CLIENT)
    assert report.check is not None
    (diagnostic,) = (d for d in report.check.diagnostics if d.code == CODE)
    assert diagnostic.fix is not None
    assert ONLY_ROOT[diagnostic.fix.start : diagnostic.fix.end].strip() == "folder"
    assert diagnostic.fix.replacement == "folders"


def test_a_mid_chain_link_is_reported_once_not_twice() -> None:
    """`singular-spelling-mid-chain` already names `file` here; the new code
    adds only the root."""
    assert codes(MIXED).count(CODE) == 1


# -- below a singular last link ---------------------------------------------------
#
# Engine facts (QnA, client, macOS), the same answer as the singular spelling in
# every case tried::
#
#     Q: file "hosts" of folder "/etc"
#     A: ...
#     Q: file "hosts" of folders "/etc"
#     A: ... (identical)
#     Q: file "" of folder "" of folder ""
#     E: Singular expression refers to nonexistent object.
#     Q: file "" of folders "" of folders ""
#     E: Singular expression refers to nonexistent object.
#     Q: files "" of folder "/etc" | files ""
#     E: A singular expression is required.

BELOW = "singular-spelling-pluralizable-below-singular"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # A comparison operand, which requires a singular.
        (
            'name of file "x" of folder "/etc" = "z"',
            'name of files "x" of folders "/etc" = "z"',
        ),
        # The right of a `|` is a singular position too, but nothing there
        # depends on the error.
        (
            '"y" | name of file "x" of folder "/etc"',
            '"y" | name of files "x" of folders "/etc"',
        ),
        # An `if` condition.
        (
            'if (name of file "x" of folder "/etc" = "z") then 1 else 2',
            'if (name of files "x" of folders "/etc" = "z") then 1 else 2',
        ),
    ],
)
def test_a_singular_last_link_keeps_its_plurality_and_what_is_below_it_goes_plural(
    text: str, expected: str
) -> None:
    assert BELOW in codes(text)
    assert fixed(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        # Left of a `|` the error is the fallback's trigger, and a plural below
        # could answer where the singular erred.
        '(name of file "x" of folder "/etc") | "y"',
        '(version of file "x" of folder "/etc" as string) | "y"',
    ],
)
def test_the_left_of_a_pipe_is_never_pluralized(text: str) -> None:
    assert BELOW not in codes(text)
    assert CODE not in codes(text)
    assert fixed(text) == text


def test_the_result_stays_singular() -> None:
    text = 'name of file "x" of folder "/etc" = "z"'
    before = analyze(text, Dialect.CLIENT)
    after = analyze(fixed(text), Dialect.CLIENT)
    assert before.check is not None and after.check is not None
    assert after.check.value.plurality is before.check.value.plurality
    assert after.check.value.types == before.check.value.types


def test_a_bare_singular_with_nothing_below_it_is_left_alone() -> None:
    assert BELOW not in codes("name of operating system")
    assert fixed("name of operating system") == "name of operating system"


# The statement's own value has no consumer, so nothing requires it singular --
# but only a chain that takes a parameter has anything to pluralize. Engine,
# client::
#
#     Q: files "" of folders "" of folders ""
#     A: (empty, no error)
#     Q: wmis "root/cimv2" ...   (plural spelling of the same root)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('file "" of folder "" of folder ""', 'files "" of folders "" of folders ""'),
        ('wmi "root/cimv2"', 'wmis "root/cimv2"'),
        ('name of folder "/etc"', 'names of folders "/etc"'),
        ('selects "x" of wmi "root/cimv2"', 'selects "x" of wmis "root/cimv2"'),
        # The bare `wmi` stays; the links above it take a parameter or sit on
        # one, and go plural.
        ('string value of select "" of wmi', 'string values of selects "" of wmi'),
    ],
)
def test_the_statements_own_chain_goes_plural_all_the_way_up_when_it_takes_a_parameter(
    text: str, expected: str
) -> None:
    assert CODE in codes(text)
    assert fixed(text) == expected


@pytest.mark.parametrize("text", ["wmi", "name of operating system", "operating system"])
def test_a_statements_own_chain_that_takes_no_parameter_stays_singular(text: str) -> None:
    assert CODE not in codes(text)
    assert fixed(text) == text


def test_pluralizing_the_statements_own_chain_changes_only_its_plurality() -> None:
    text = 'file "" of folder "" of folder ""'
    before = analyze(text, Dialect.CLIENT)
    after = analyze(fixed(text), Dialect.CLIENT)
    assert before.check is not None and after.check is not None
    assert before.check.value.plurality is Plurality.SINGULAR
    assert after.check.value.plurality is Plurality.PLURAL
    assert after.check.value.types == before.check.value.types


def test_it_is_a_second_pass_fixed_point() -> None:
    once = fixed('file "" of folder "" of folder ""')
    assert fixed(once) == once


def test_default_lint_stays_quiet_for_it() -> None:
    findings = lint_analysis(
        analyze('file "" of folder "" of folder ""', Dialect.CLIENT), LintConfig()
    )
    assert not findings


def test_enabled_lint_reports_and_fixes_it() -> None:
    findings = lint_analysis(analyze('file "" of folder "" of folder ""', Dialect.CLIENT), ENABLED)
    # One finding per link, each carrying the whole statement's fix.
    assert [f.code for f in findings] == [RULE] * 3
    assert {f.autofix.fixed for f in findings if f.autofix} == {
        'files "" of folders "" of folders ""'
    }


# -- analysis: on by default ------------------------------------------------------


def test_analysis_autofix_includes_the_pluralizing_edits_by_default() -> None:
    assert fixed(MIXED) == MIXED_FULL


def test_autofix_can_be_limited_to_some_codes() -> None:
    result = analyze(MIXED, Dialect.CLIENT).autofix(codes={"singular-spelling-mid-chain"})
    assert result.fixed == MIXED_DEFAULT
    assert CODE not in result.applied


def test_a_bare_root_stays_singular() -> None:
    """A root with no argument or filter is a singleton: `clients` would be
    valid, but adds nothing."""
    assert fixed(SETTING) == 'exists values of settings "x" of client'


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("exists files of windows folder", "exists files of windows folder"),
        ('exists files "x" of folder "/etc"', 'exists files "x" of folders "/etc"'),
        (
            'exists selects "x" of wmi',
            'exists selects "x" of wmi',
        ),
        (
            'exists selects "x" of wmi "root\\cimv2"',
            'exists selects "x" of wmis "root\\cimv2"',
        ),
        (
            "exists names of bes computer whose (false)",
            "exists names of bes computers whose (false)",
        ),
        # Directly under `exists`, a filtered root already answers False
        # rather than erroring; the idiom stays as written.
        ("exists true whose (1 = 1)", "exists true whose (1 = 1)"),
        ("number of true whose (1 = 1)", "number of true whose (1 = 1)"),
        ("exists bes computer whose (false)", "exists bes computer whose (false)"),
    ],
)
def test_a_root_is_pluralized_only_with_an_argument_or_filter(text: str, expected: str) -> None:
    dialect = Dialect.SESSION if "bes computer" in text else Dialect.CLIENT
    assert analyze(text, dialect).autofix().fixed == expected


# -- lint: off by default, rides along --------------------------------------------


def test_the_rule_is_registered_and_off_by_default() -> None:
    assert DEFAULT_SEVERITIES[RULE] is Severity.IGNORE
    assert RULES[RULE].default_severity is Severity.IGNORE


def test_default_lint_reports_nothing_for_a_pluralizable_only_statement() -> None:
    findings = lint_analysis(analyze(ONLY_ROOT, Dialect.CLIENT), LintConfig())
    assert not any(finding.code == RULE for finding in findings)
    assert all(finding.autofix is None for finding in findings)


def test_default_lint_fix_rides_along_with_another_fix() -> None:
    findings = lint_analysis(analyze(MIXED, Dialect.CLIENT), LintConfig())
    (finding,) = (f for f in findings if f.autofix is not None)
    assert finding.code == "plural-preferred"
    assert finding.autofix is not None
    assert finding.autofix.fixed == MIXED_FULL
    assert finding.autofix.applied_rules == {"plural-everywhere": 1, "plural-preferred": 1}
    assert not any(f.code == RULE for f in findings)


def test_enabled_lint_reports_and_fixes_a_pluralizable_only_statement() -> None:
    findings = lint_analysis(analyze(ONLY_ROOT, Dialect.CLIENT), ENABLED)
    (finding,) = (f for f in findings if f.code == RULE)
    assert finding.autofix is not None
    assert finding.autofix.fixed == ONLY_ROOT_FIXED


# -- fixing files ------------------------------------------------------------------

HEAD = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    "\t<Task>\n"
    "\t\t<Title>t</Title>\n"
)
TAIL = "\t</Task>\n</BES>\n"


def task_file(tmp_path: Path, relevance: str) -> Path:
    path = tmp_path / "t.bes"
    path.write_text(f"{HEAD}\t\t<Relevance>{relevance}</Relevance>\n{TAIL}", encoding="utf-8")
    return path


def test_default_fix_leaves_a_pluralizable_only_statement_untouched(tmp_path: Path) -> None:
    """The scale guarantee: the rule being off must not change *which*
    statements a default `--fix` rewrites."""
    path = task_file(tmp_path, ONLY_ROOT)
    before = path.read_bytes()
    result = fix_file(path, LintConfig())
    assert not result.changed
    assert path.read_bytes() == before


def test_default_fix_applies_the_ride_along_edits(tmp_path: Path) -> None:
    path = task_file(tmp_path, MIXED)
    result = fix_file(path, LintConfig())
    assert result.changed
    assert MIXED_FULL in path.read_text(encoding="utf-8")
    assert not fix_file(path, LintConfig()).changed


def test_enabled_fix_rewrites_a_pluralizable_only_statement(tmp_path: Path) -> None:
    path = task_file(tmp_path, ONLY_ROOT)
    assert fix_file(path, ENABLED).changed
    assert ONLY_ROOT_FIXED in path.read_text(encoding="utf-8")
    assert not fix_file(path, ENABLED).changed


def test_ignoring_the_triggering_rule_ignores_the_ride_along_too(tmp_path: Path) -> None:
    path = task_file(tmp_path, MIXED)
    before = path.read_bytes()
    config = LintConfig(severities={"plural-preferred": Severity.IGNORE})
    assert not fix_file(path, config).changed
    assert path.read_bytes() == before


def test_a_combined_fix_that_fixes_less_falls_back_to_the_base_fix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Riding along never costs the fix that triggered it: if the full result
    leaves a default-rule diagnostic unfixed, the base result is kept."""
    from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis
    from bigfix_relevance_analyzer.autofix import AutofixResult

    real = RelevanceAnalysis.autofix

    def worse_when_full(self: RelevanceAnalysis, **kwargs: object) -> AutofixResult:
        result = real(self, **kwargs)  # type: ignore[arg-type]
        if kwargs.get("codes") is None:
            return AutofixResult(
                original=result.original,
                fixed=result.original,
                unapplied={"singular-spelling-mid-chain": 1},
            )
        return result

    monkeypatch.setattr(RelevanceAnalysis, "autofix", worse_when_full)
    findings = lint_analysis(analyze(MIXED, Dialect.CLIENT), LintConfig())
    (finding,) = (f for f in findings if f.autofix is not None)
    assert finding.autofix is not None
    assert finding.autofix.fixed == MIXED_DEFAULT


def test_an_unmappable_riding_edit_falls_back_to_the_base_fix(tmp_path: Path) -> None:
    """`folder` split by a CDATA section cannot be written back; `files`
    still is."""
    path = task_file(tmp_path, 'exists file "x" of fol<![CDATA[der]]> "/etc"')
    assert fix_file(path, LintConfig()).changed
    assert 'exists files "x" of fol<![CDATA[der]]> "/etc"' in path.read_text(encoding="utf-8")
