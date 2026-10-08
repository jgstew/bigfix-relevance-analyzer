"""What pre-commit-bigfix's ``bes-relevance-lint`` hook relies on, pinned here.

pre-commit-bigfix (github.com/jgstew/pre-commit-bigfix) depends on this package
with no upper bound (``bigfix-relevance-analyzer >= 1.19.0``), so every release
of this one reaches its users at once. Its hook,
``pre_commit_bigfix/bes_relevance_lint.py`` (read at its commit 53063b1):

* imports ``LintConfig``, ``Severity``, ``lint_directory`` and ``lint_paths``
  from the package, and ``Dialect`` from ``bigfix_relevance_analyzer.dialect``;
* builds ``LintConfig(severities=..., max_score=..., max_evaluation_cost=...,
  platform=..., dialect=Dialect("client" | "session"))``, every keyword but
  ``severities`` optional;
* calls ``lint_paths(files, config)``, or ``lint_directory(".", config,
  max_depth=n)`` and opens each finding's ``path`` relative to the working
  directory;
* maps every name in ``RULES`` to its own E/W-code, and fails its own build
  when a name is missing (its CODES table);
* prints each finding as ``{path}:{line}: [{code}] {warning: }{message}
  ({rule})``, then ``    suggested fix: {autofix.fixed}`` once per
  ``(path, site.line, autofix.original)``; a finding is a warning when its
  severity ``is Severity.WARNING`` and an error otherwise.

The point is to know when a change here breaks the hook, not to make one
impossible. These tests fail on any change to that surface, and the golden
report fails on any change to the output itself: lines, messages, codes, order
and suggested fixes, over every example file plus the deliberately broken
fixtures in ``tests/golden/pre_commit_bigfix/`` (which cover the token-level
rules the examples do not: parse and type errors, ``it`` with nothing to bind,
unknown inspectors, unterminated substitutions and fences, in multi-line
statements, a CRLF file and an XML entity). A failure is a prompt to decide:
avoid the break if it isn't warranted, or make it on purpose, say so in the
release notes, and change pre-commit-bigfix to match if it needs to.

Precise diagnostic ranges (issue #96, item 1) are planned to leave all of it
alone: ``Finding.line`` keeps its meaning, and anything new is additive.

A deliberate change to the output (a reworded message, say) regenerates the
golden, and its diff is exactly what the hook's users will see::

    UPDATE_GOLDEN=1 uv run pytest tests/test_downstream_pre_commit_bigfix.py

With a pre-commit-bigfix checkout importable (or its path in
``PRE_COMMIT_BIGFIX_SRC``), one more test runs the real hook over the same
files and checks it prints exactly the golden report, which is what keeps the
copy of its format below honest.
"""

from __future__ import annotations

import contextlib
import dataclasses
import importlib
import inspect
import io
import os
import re
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import pytest

from bigfix_relevance_analyzer import LintConfig, Severity, lint_directory, lint_paths
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import _is_recognized
from bigfix_relevance_analyzer.lint import RULES, Finding

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = Path("tests/examples")
FIXTURES = Path("tests/golden/pre_commit_bigfix")
GOLDEN = REPO_ROOT / "tests" / "golden" / "pre_commit_bigfix_report.txt"

# The hook's CODES keys at 53063b1. A new rule is fine, but the hook has to map
# it too (its own test goes red until it does, and its _report raises KeyError
# on an unmapped name), so updating this set is the moment to open the change
# there.
HOOK_RULES = frozenset(
    {
        "parse-error",
        "error-token",
        "unbound-it",
        "type-error",
        "complexity",
        "evaluation-cost",
        "max-depth-exceeded",
        "file-error",
        "site-type-mismatch",
        "mixed-dialect",
        "actionscript-keyword",
        "singular-required",
        "unterminated-substitution",
        "unterminated-processing-instruction",
        "xml-parse-error",
        "unknown-inspector",
        "non-unique-risk",
        "plural-preferred",
        "version-like-string-compare",
        "version-truncating-compare",
        "non-renderable-substitution",
        "plural-substitution",
        "unterminated-code-fence",
    }
)

# The hook switches xml-parse-error off unless a repo enables it (its
# DEFAULT_DISABLED), so that is the configuration its users run by default.
HOOK_DEFAULT_SEVERITIES = {"xml-parse-error": Severity.IGNORE}


@contextlib.contextmanager
def _in_repo_root() -> Iterator[None]:
    # pre-commit runs hooks from the repository root with relative paths, and
    # the hook prints the paths it was given; so do these tests.
    previous = Path.cwd()
    os.chdir(REPO_ROOT)
    try:
        yield
    finally:
        os.chdir(previous)


def _example_files() -> list[str]:
    """The example corpus plus the contract fixtures, as relative paths."""
    with _in_repo_root():
        return sorted(
            str(path)
            for root in (EXAMPLES, FIXTURES)
            for path in root.rglob("*")
            if path.is_file() and _is_recognized(path)
        )


def _hook_report(findings: Iterable[Finding]) -> str:
    """The hook's ``_report`` output, with its rule-name-to-code mapping left out.

    The E/W-codes are the hook's own vocabulary, so the rule name stands in for
    them here; everything the analyzer supplies is printed as the hook prints it.
    """
    out: list[str] = []
    suggested: set[tuple[str, int | None, str]] = set()
    for finding in findings:
        label = "warning: " if finding.severity is Severity.WARNING else ""
        out.append(
            f"{finding.path}:{finding.line}: [{finding.code}] {label}{finding.message} "
            f"({finding.code})"
        )
        fix = getattr(finding, "autofix", None)
        if fix is not None:
            site_line = finding.site.line if finding.site is not None else None
            key = (str(finding.path), site_line, fix.original)
            if key not in suggested:
                suggested.add(key)
                out.append(f"    suggested fix: {fix.fixed}")
    return "".join(f"{line}\n" for line in out)


def _golden_report() -> str:
    files = _example_files()
    with _in_repo_root():
        findings = lint_paths(files, LintConfig(severities=dict(HOOK_DEFAULT_SEVERITIES)))
    return _hook_report(findings)


# ---------------------------------------------------------------------------
# The API surface the hook calls
# ---------------------------------------------------------------------------


def test_the_hook_imports_resolve() -> None:
    package = importlib.import_module("bigfix_relevance_analyzer")
    for name in ("LintConfig", "Severity", "lint_directory", "lint_paths"):
        assert hasattr(package, name), name
    assert Dialect("client") is Dialect.CLIENT
    assert Dialect("session") is Dialect.SESSION


def test_lint_config_takes_every_keyword_the_hook_passes() -> None:
    config = LintConfig(
        severities={"complexity": Severity.IGNORE},
        max_score=10_000.0,
        max_evaluation_cost=10_000.0,
        platform="windows",
        dialect=Dialect("client"),
    )
    assert config.severities == {"complexity": Severity.IGNORE}
    assert LintConfig(severities={}) is not None, "every keyword but severities is optional"


def test_the_severities_the_hook_compares_against() -> None:
    # `is Severity.WARNING` decides warning versus error; IGNORE is what its
    # --disable sets, and must drop the finding.
    assert {member.name for member in Severity} >= {"ERROR", "WARNING", "IGNORE"}


def test_the_lint_entry_points_take_the_hooks_arguments() -> None:
    assert list(inspect.signature(lint_paths).parameters)[:2] == ["paths", "config"]
    directory = inspect.signature(lint_directory).parameters
    assert list(directory)[:2] == ["root", "config"]
    assert "max_depth" in directory


def test_the_rule_names_are_the_ones_the_hook_maps() -> None:
    """A new rule needs a code in the hook (its CODES) before release."""
    assert set(RULES) == HOOK_RULES


def test_a_finding_has_every_attribute_the_hook_reads() -> None:
    fields = {field.name for field in dataclasses.fields(Finding)}
    assert {"code", "severity", "message", "path", "line", "site", "autofix"} <= fields
    # Reading attributes by name is all the hook does; it never constructs a
    # Finding. These are the ones whose meaning it depends on.
    finding = next(f for f in _findings_with_autofix())
    assert isinstance(finding.line, int) and finding.line >= 1
    assert finding.site is not None and isinstance(finding.site.line, int)
    assert isinstance(finding.autofix.original, str)  # type: ignore[union-attr]
    assert isinstance(finding.autofix.fixed, str)  # type: ignore[union-attr]


def _findings_with_autofix() -> list[Finding]:
    with _in_repo_root():
        findings = lint_paths(_example_files(), LintConfig(severities={}))
    with_fix = [finding for finding in findings if finding.autofix is not None]
    assert with_fix, "no example yields an autofix; add one so this stays tested"
    return with_fix


# ---------------------------------------------------------------------------
# Behaviour the hook depends on
# ---------------------------------------------------------------------------


def test_ignore_drops_a_finding() -> None:
    files = _example_files()
    with _in_repo_root():
        everything = lint_paths(files, LintConfig(severities={}))
        codes = {finding.code for finding in everything}
        assert codes, "the examples produce no findings to switch off"
        quiet = lint_paths(files, LintConfig(severities=dict.fromkeys(codes, Severity.IGNORE)))
    assert quiet == ()


def test_raising_max_score_clears_a_complexity_finding() -> None:
    """The hook's --max-score raises E604's ceiling; it must take effect."""
    files = _example_files()
    with _in_repo_root():
        default = lint_paths(files, LintConfig(severities={}))
        raised = lint_paths(files, LintConfig(severities={}, max_score=1e9))
    assert any(finding.code == "complexity" for finding in default)
    assert not any(finding.code == "complexity" for finding in raised)


def test_lint_directory_paths_open_from_the_working_directory(tmp_path: Path) -> None:
    """The hook opens each finding's path to look for its opt-out marker."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "broken.rel").write_text('exists file "unterminated\n')
    previous = Path.cwd()
    os.chdir(tmp_path)
    try:
        findings = lint_directory(".", LintConfig(severities={}), max_depth=6)
        assert findings
        for finding in findings:
            assert finding.path is not None
            assert Path(finding.path).is_file(), finding.path
    finally:
        os.chdir(previous)


# ---------------------------------------------------------------------------
# The hook's output, pinned
# ---------------------------------------------------------------------------


def test_the_hooks_report_over_the_examples_is_unchanged() -> None:
    """Every line the hook prints for the example corpus, by default config.

    ``Finding.line`` in particular: precise ranges (#96 item 1) add spans,
    they do not move lines.
    """
    report = _golden_report()
    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.write_text(report, encoding="utf-8")
        pytest.fail("golden rewritten -- review the diff, then rerun without UPDATE_GOLDEN")
    assert GOLDEN.is_file(), f"missing {GOLDEN}; regenerate with UPDATE_GOLDEN=1"
    expected = GOLDEN.read_text(encoding="utf-8")
    # Compare per file, so a failure names the file that moved.
    by_file = _split_by_file
    assert by_file(report) == by_file(expected)


def _split_by_file(report: str) -> dict[str, list[str]]:
    files: dict[str, list[str]] = {}
    current = ""
    for line in report.splitlines():
        if not line.startswith("    "):
            current = line.split(":", 1)[0]
        files.setdefault(current, []).append(line)
    return files


def test_the_golden_report_covers_every_kind_of_line() -> None:
    """Errors, warnings and a suggested fix, so no part of the format is unpinned;
    and the rules item 1 will give token spans, so their lines are pinned too."""
    expected = GOLDEN.read_text(encoding="utf-8")
    assert "] warning: " in expected
    assert any("] " in line and "] warning: " not in line for line in expected.splitlines()), (
        "no error line"
    )
    assert "\n    suggested fix: " in expected
    for rule in (
        "parse-error",
        "error-token",
        "type-error",
        "unbound-it",
        "unknown-inspector",
        "unterminated-substitution",
        "unterminated-processing-instruction",
        "unterminated-code-fence",
    ):
        assert f": [{rule}] " in expected, rule


def _hook_module() -> Any:
    source = os.environ.get("PRE_COMMIT_BIGFIX_SRC")
    if source:
        sys.path.insert(0, source)
    try:
        return importlib.import_module("pre_commit_bigfix.bes_relevance_lint")
    except ImportError:
        pytest.skip("pre-commit-bigfix is not importable; set PRE_COMMIT_BIGFIX_SRC to a checkout")
    finally:
        if source:
            sys.path.remove(source)


def test_the_real_hook_prints_the_golden_report() -> None:
    """The format copied in ``_hook_report`` is the hook's, checked against it.

    Its E/W-codes become rule names for the comparison, the one difference the
    copy makes on purpose; and its closing count lines are left out.
    """
    hook = _hook_module()
    output = io.StringIO()
    with _in_repo_root(), contextlib.redirect_stdout(output):
        status = hook.main(_example_files())
    assert status in (0, 1)
    rules_by_code = {code: rule for rule, code in hook.CODES.items()}
    lines = []
    for line in output.getvalue().splitlines():
        if line.endswith(("warning(s).", "issue(s).")):
            continue
        for code, rule in rules_by_code.items():
            line = line.replace(f": [{code}] ", f": [{rule}] ", 1)
        lines.append(line)
    assert "".join(f"{line}\n" for line in lines) == GOLDEN.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The CI job that runs pre-commit-bigfix's own tests against this analyzer
# ---------------------------------------------------------------------------

DOWNSTREAM_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "downstream.yaml"


def _workflow() -> str:
    assert DOWNSTREAM_WORKFLOW.is_file(), DOWNSTREAM_WORKFLOW
    return DOWNSTREAM_WORKFLOW.read_text("utf-8")


def test_a_workflow_runs_pre_commit_bigfixs_tests_against_this_analyzer() -> None:
    text = _workflow()
    assert "repository: jgstew/pre-commit-bigfix" in text
    # Its own suite, then this module with the real hook importable, so the
    # golden-report check that skips in `test` runs here.
    assert "python -m pytest" in text
    assert "PRE_COMMIT_BIGFIX_SRC:" in text
    assert "tests/test_downstream_pre_commit_bigfix.py" in text


def test_it_tests_the_latest_release_unless_given_a_ref() -> None:
    """What users run by default; a branch can be tried by hand."""
    text = _workflow()
    assert "gh release view --repo jgstew/pre-commit-bigfix" in text
    assert "workflow_dispatch:" in text
    assert "ref:" in text.split("workflow_dispatch:", 1)[1].split("jobs:", 1)[0]


def test_it_installs_this_commits_analyzer_not_pypis() -> None:
    """One resolve with the checkout as a requirement, then proof of where the
    installed analyzer came from: a version number alone cannot tell a
    checkout from the PyPI release of the same version."""
    commands = re.sub(r"\\\n\s*", "", _workflow())  # join `\` continuation lines
    assert re.search(
        r'uv pip install .*"downstream/pre-commit-bigfix\[test\]".* \.\s*$', commands, re.M
    )
    text = _workflow()
    assert "direct_url.json" in text


def test_it_keeps_the_release_age_cooldown_for_third_party_packages() -> None:
    """Seven days for PyPI packages, as everywhere in this repository; jgstew's
    own packages are exempt, as bigfix-remote-client-relevance is in
    pyproject.toml."""
    text = _workflow()
    assert '--exclude-newer "7 days"' in text
    exempt = set(re.findall(r'--exclude-newer-package "([\w-]+)=0 days"', text))
    assert exempt == {"bigfix-prefetch", "validate-bes-xml"}


def test_it_is_advisory_and_never_gates_a_release() -> None:
    """A deliberate break has to land here before the hook can follow, so a
    required check would block exactly that. It runs and shows red; it is not
    called by the release workflow."""
    release = (REPO_ROOT / ".github" / "workflows" / "tag_and_release.yaml").read_text("utf-8")
    assert "downstream" not in release
    assert "continue-on-error" not in _workflow(), "red must stay visible"


def test_it_runs_when_the_analyzer_changes_and_weekly() -> None:
    text = _workflow()
    for path in (
        '"src/**"',
        '"pyproject.toml"',
        '"uv.lock"',
        '"tests/test_downstream_pre_commit_bigfix.py"',
        '"tests/golden/**"',
        '".github/workflows/downstream.yaml"',
    ):
        assert path in text, path
    assert "paths: *inputs" in text
    # Weekly, for changes on the hook's side against this repository's main.
    assert re.search(r"schedule:\s*\n\s*- cron:", text)


def test_its_actions_are_pinned_and_its_token_read_only() -> None:
    text = _workflow()
    uses = re.findall(r"uses:\s*(\S+)", text)
    assert uses
    for action in uses:
        assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action), action
    assert "permissions:\n  contents: read" in text
    assert text.count("persist-credentials: false") == text.count("actions/checkout@")
