"""Command line for :mod:`~bigfix_relevance_analyzer.lint`: one line per finding.

    bigfix-relevance-lint MyFixlet.bes MyTask.bes
    bigfix-relevance-lint --max-score=350 --max-evaluation-cost=40 *.bes
    bigfix-relevance-lint

Shaped for a pre-commit hook, not a human report -- see ``__main__`` for that.
Findings go to stdout, one per line, in the compact form a hook or CI log can
grep; the pass/fail summary goes to stderr so ``--quiet`` output still pipes
cleanly into something else. Exit status is ``0`` when nothing at
error-severity was found (warnings do not fail a commit unless
``--fail-on-warning`` says otherwise), ``1`` when something did, ``2`` on a
usage error.

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

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    LintConfig,
    Severity,
    lint_directory,
    lint_paths,
)

__all__ = ["main"]


def _severity_map(pairs: list[str] | None, severity: Severity) -> dict[str, Severity]:
    return {code: severity for code in (pairs or [])}


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, lint every path, print findings. Returns a process exit status."""
    parser = argparse.ArgumentParser(
        prog="bigfix-relevance-lint",
        description=(
            "Lint every relevance site found in the given files: parse failures "
            "and unbound `it` are always errors, unknown inspectors are always "
            "warnings, and complexity / evaluation cost are checked only when a "
            "threshold is given."
        ),
    )
    parser.add_argument(
        "paths", nargs="*", help="files to lint; omit entirely to walk the current directory"
    )
    parser.add_argument(
        "--max-score", type=float, default=None, help="fail a site scoring above this"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=(
            f"with no paths given, how many directory levels to walk (default {DEFAULT_MAX_DEPTH})"
        ),
    )
    parser.add_argument(
        "--max-evaluation-cost",
        type=float,
        default=None,
        help="fail a site whose evaluation cost is above this",
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
    parser.add_argument(
        "--dialect",
        choices=[Dialect.CLIENT.value, Dialect.SESSION.value],
        help="force the dialect instead of trusting extraction",
    )
    parser.add_argument("--platform", help="narrow client lookups to one platform, e.g. windows")
    args = parser.parse_args(argv)

    severities: dict[str, Severity] = {}
    severities.update(_severity_map(args.warn, Severity.WARNING))
    severities.update(_severity_map(args.error, Severity.ERROR))
    severities.update(_severity_map(args.ignore, Severity.IGNORE))

    config = LintConfig(
        max_score=args.max_score,
        max_evaluation_cost=args.max_evaluation_cost,
        severities=severities,
        dialect=Dialect(args.dialect) if args.dialect else None,
        platform=args.platform,
    )

    if args.paths:
        findings = lint_paths(args.paths, config)
        scope = f"{len(args.paths)} file(s)"
    else:
        findings = lint_directory(".", config, max_depth=args.max_depth)
        scope = "the current directory"

    if not args.quiet:
        for finding in findings:
            print(finding)

    errors = sum(1 for f in findings if f.severity is Severity.ERROR)
    warnings = sum(1 for f in findings if f.severity is Severity.WARNING)
    print(_summary(errors, warnings, scope), file=sys.stderr)

    if errors or (args.fail_on_warning and warnings):
        return 1
    return 0


def _summary(errors: int, warnings: int, scope: str) -> str:
    return f"{errors} error(s), {warnings} warning(s) in {scope}"


if __name__ == "__main__":
    raise SystemExit(main())
