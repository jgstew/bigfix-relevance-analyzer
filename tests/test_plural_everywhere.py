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
