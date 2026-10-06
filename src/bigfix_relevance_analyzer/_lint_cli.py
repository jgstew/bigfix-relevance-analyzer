"""Command line for :mod:`~bigfix_relevance_analyzer.lint`: one line per finding.

    bigfix-relevance-lint MyFixlet.bes MyTask.bes
    bigfix-relevance-lint --max-score=800 --max-evaluation-cost=80 *.bes
    bigfix-relevance-lint
    bigfix-relevance-lint "(version of client, name of it) of operating system"

Shaped for a pre-commit hook, not a human report -- see ``__main__`` for that.
Findings go to stdout, one per line, in the compact form a hook or CI log can
grep; the pass/fail summary goes to stderr so ``--quiet`` output still pipes
cleanly into something else. Exit status is ``0`` when nothing at
error-severity was found (warnings do not fail a commit unless
``--fail-on-warning`` says otherwise), ``1`` when something did, ``2`` on a
usage error.

``--max-score``/``--max-evaluation-cost`` *raise* the complexity/evaluation-cost
ceilings above :mod:`~bigfix_relevance_analyzer.lint`'s built-in defaults
(:data:`~bigfix_relevance_analyzer.lint.DEFAULT_MAX_SCORE`,
:data:`~bigfix_relevance_analyzer.lint.DEFAULT_MAX_EVALUATION_COST`) rather
than switching the rules on -- they are on by default. There is no CLI
spelling to disable them entirely; a caller that wants that uses the library
API directly.

``--fix`` applies every safe fix in place first (see
:mod:`~bigfix_relevance_analyzer.fixfile`), printing one line per fix --
``path:line: fixed [rule] setting -> settings``, or ``not fixed [rule]`` and
the reason -- and then the findings left standing. It exits ``1`` whenever it
fixed anything, even if nothing is left to report: a rewritten file is a change
the author has not seen yet, and pre-commit's convention is that a hook which
modifies files fails, so the fix is reviewed and staged rather than committed
unread.

A positional argument that names nothing on disk *and* contains whitespace is
linted as relevance text rather than reported as a missing file -- a filename
rarely has a space in it, and a statement almost always does. Findings for it
carry no path, only a line relative to the text. ``--fix`` does not apply to
such text: there is no file to rewrite.

Called with no paths at all, this walks the current directory (see
:func:`~bigfix_relevance_analyzer.lint.lint_directory`) instead of erroring --
an *explicit* path, including ``.``, is never expanded this way; it is taken
literally, the same as any other path argument.

This is the console script (``[project.scripts]`` in ``pyproject.toml``)
``pre-commit-bigfix``'s hook entry calls; kept out of ``__main__.py`` because
that module renders full reports for a human, and this one does not import
it, so a stdio consumer of the library that never touches either CLI module
still prints nothing on its own.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bigfix_relevance_analyzer._cli_common import (
    add_ceiling_args,
    add_format_args,
    add_scope_args,
    config_from_args,
    emit_json,
    lint_targets,
    output_format,
    print_rules,
)
from bigfix_relevance_analyzer.fixfile import FileFix, FixResult, fix_directory, fix_paths
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_EVALUATION_COST,
    DEFAULT_MAX_SCORE,
    Finding,
    Severity,
    _findings_dict,
    counts,
    lint_text,
)

__all__ = ["main"]


def _severity_map(pairs: list[str] | None, severity: Severity) -> dict[str, Severity]:
    return {code: severity for code in (pairs or [])}


def _is_relevance_text(arg: str) -> bool:
    """Whether a positional argument is a relevance statement rather than a path.

    Only when nothing exists at that path and the argument contains whitespace:
    a pre-commit hook passes real files, which always exist, so its behaviour
    is unchanged, and a mistyped filename without a space still surfaces as
    ``file-error`` rather than as a parse error on nonsense relevance.
    """
    if not any(char.isspace() for char in arg):
        return False
    try:
        return not Path(arg).exists()
    except OSError:
        # Too long or strange for the filesystem (name too long, embedded
        # NUL): relevance text, not a path.
        return True


def main(argv: list[str] | None = None, *, prog: str = "bigfix-relevance-lint") -> int:
    """Parse arguments, lint every path, print findings. Returns a process exit status.

    ``prog`` is the name usage and errors are reported under:
    ``bigfix-relevance-analyzer --check`` hands its arguments here (see
    ``__main__``) and says so, rather than keeping a second linter of its own.
    """
    parser = argparse.ArgumentParser(
        prog=prog,
        description=(
            "Lint every relevance site found in the given files: parse failures, "
            "unbound `it`, and type errors are always errors, unknown inspectors "
            "are always warnings, and complexity / evaluation cost are errors "
            f"past a built-in ceiling (default {DEFAULT_MAX_SCORE:g} / "
            f"{DEFAULT_MAX_EVALUATION_COST:g}) that --max-score/--max-evaluation-cost raise."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "files to lint, or relevance statements (any argument with whitespace that "
            "is not an existing path); omit entirely to walk the current directory"
        ),
    )
    add_ceiling_args(
        parser,
        max_score_help=f"fail a site scoring above this (default {DEFAULT_MAX_SCORE:g})",
        max_evaluation_cost_help=(
            "fail a site whose evaluation cost is above this "
            f"(default {DEFAULT_MAX_EVALUATION_COST:g})"
        ),
        max_depth_help=(
            f"with no paths given, how many directory levels to walk (default {DEFAULT_MAX_DEPTH})"
        ),
    )
    parser.add_argument(
        "--error",
        action="append",
        metavar="CODE",
        help="treat CODE as an error (repeatable)",
    )
    parser.add_argument(
        "--warn",
        action="append",
        metavar="CODE",
        help="treat CODE as a warning (repeatable)",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        metavar="CODE",
        help="silence CODE entirely (repeatable)",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="exit non-zero if anything, even a warning, was found",
    )
    parser.add_argument("--quiet", action="store_true", help="print nothing; exit code still set")
    add_format_args(parser, json_help="emit findings as one JSON object instead of one line each")
    add_scope_args(
        parser,
        dialect_help="force the dialect instead of trusting extraction",
        platform_help="narrow lookups to one evaluation context, e.g. windows or session:console",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help=(
            "apply every safe fix in place, report each one, then lint what is left; "
            "exits non-zero if anything was fixed"
        ),
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print every rule, its default severity and what it means, then exit",
    )
    args = parser.parse_args(argv)

    output = output_format(args)
    if args.list_rules:
        return print_rules(output)

    severities: dict[str, Severity] = {}
    severities.update(_severity_map(args.warn, Severity.WARNING))
    severities.update(_severity_map(args.error, Severity.ERROR))
    severities.update(_severity_map(args.ignore, Severity.IGNORE))

    config = config_from_args(args, severities=severities)

    texts = [arg for arg in args.paths if _is_relevance_text(arg)]
    paths = [arg for arg in args.paths if arg not in texts]
    if texts and args.fix:
        parser.error("--fix rewrites files in place; it cannot fix relevance given as text")

    scope = _scope(paths, texts)
    fixes: FixResult | None = None
    if args.fix:
        fixes = (
            fix_paths(paths, config)
            if paths
            else fix_directory(".", config, max_depth=args.max_depth)
        )
        findings = fixes.findings
    elif texts:
        findings = tuple(f for text in texts for f in lint_text(text, config))
        if paths:
            findings += lint_targets(paths, config, max_depth=args.max_depth)
    else:
        findings = lint_targets(paths, config, max_depth=args.max_depth)

    # One tally, from `lint.counts`, feeding the summary, the exit status and
    # the JSON payload alike -- rather than each recounting the findings and
    # risking three answers to one question.
    tallies = counts(findings)
    errors = tallies[Severity.ERROR.value]
    warnings = tallies[Severity.WARNING.value]

    if not args.quiet:
        if output == "json":
            payload = fixes.to_dict() if fixes is not None else _findings_dict(findings)
            emit_json({**payload, "scope": scope})
        elif output == "markdown":
            print(_markdown_report(findings, fixes, _summary(errors, warnings, scope)), end="")
        else:
            if fixes is not None:
                for fix in fixes.applied:
                    print(_fix_line(fix))
                for fix in fixes.unapplied:
                    print(_fix_line(fix))
            for finding in findings:
                print(finding)

    summary = _summary(errors, warnings, scope)
    if fixes is not None:
        summary = (
            f"{len(fixes.applied)} fix(es) applied in {len(fixes.changed)} file(s), "
            f"{len(fixes.unapplied)} not applied; {summary}"
        )
    print(summary, file=sys.stderr)

    if errors or (args.fail_on_warning and warnings) or (fixes is not None and fixes.changed):
        return 1
    return 0


def _markdown_report(findings: tuple[Finding, ...], fixes: FixResult | None, summary: str) -> str:
    """The same lines the text form prints, as a Markdown list under a heading."""
    lines = ["# Lint results", ""]
    if fixes is not None:
        lines.extend(
            f"- {_code_span(_fix_line(fix))}" for fix in (*fixes.applied, *fixes.unapplied)
        )
    lines.extend(f"- {_code_span(str(finding))}" for finding in findings)
    if len(lines) == 2:
        lines.append("No issues found.")
    lines += ["", f"**{summary}**"]
    return "\n".join(lines) + "\n"


def _code_span(text: str) -> str:
    """``text`` as one inline code span.

    Findings quote names in single backticks (``no dump defines `fooz```), so
    those need a double-backtick fence, padded with spaces as CommonMark
    requires when the content itself starts or ends with a backtick.
    """
    if "`" in text:
        return f"`` {text} ``"
    return f"`{text}`"


def _fix_line(fix: FileFix) -> str:
    """``path:line: fixed [rule] old -> new``, or ``not fixed [rule] reason``."""
    rules = ",".join(fix.autofix.applied_rules) or "autofix"
    where = f"{fix.path}:{fix.line}"
    if fix.reason is not None:
        return f"{where}: not fixed [{rules}] {fix.reason}"
    original = fix.autofix.original
    changes = "; ".join(
        f"{original[edit.start : edit.end]} -> {edit.replacement}" for edit in fix.autofix.edits
    )
    return f"{where}: fixed [{rules}] {changes}"


def _scope(paths: list[str], texts: list[str]) -> str:
    parts = []
    if paths:
        parts.append(f"{len(paths)} file(s)")
    if texts:
        parts.append(f"{len(texts)} statement(s)")
    return " and ".join(parts) or "the current directory"


def _summary(errors: int, warnings: int, scope: str) -> str:
    return f"{errors} error(s), {warnings} warning(s) in {scope}"


if __name__ == "__main__":
    raise SystemExit(main())
