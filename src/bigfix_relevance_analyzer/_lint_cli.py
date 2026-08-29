"""Command line for :mod:`~bigfix_relevance_analyzer.lint`: one line per finding.

    bigfix-relevance-lint MyFixlet.bes MyTask.bes
    bigfix-relevance-lint --max-score=800 --max-evaluation-cost=80 *.bes
    bigfix-relevance-lint

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
import dataclasses
import json
import sys

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_EVALUATION_COST,
    DEFAULT_MAX_SCORE,
    LintConfig,
    Severity,
    counts,
    lint_directory,
    lint_paths,
    rules,
)

__all__ = ["main"]


def _severity_map(pairs: list[str] | None, severity: Severity) -> dict[str, Severity]:
    return {code: severity for code in (pairs or [])}


def _print_rules(*, as_json: bool) -> int:
    """List every rule and what it means, from :data:`~bigfix_relevance_analyzer.lint.RULES`.

    Here so that the codes in a hook's output can be looked up with the same
    tool that produced them, rather than by reading this package's source. The
    aligned columns are built from the widest code present, so adding a rule
    does not leave the table crooked.
    """
    listed = rules()
    if as_json:
        json.dump([rule.to_dict() for rule in listed], sys.stdout, indent=2)
        print()
        return 0

    defaults = LintConfig()
    width = max(len(rule.code) for rule in listed)
    for rule in listed:
        if rule.threshold:
            ceiling = getattr(defaults, rule.threshold)
            flag = f"--{rule.threshold.replace('_', '-')}"
            gate = f" (default {ceiling:g}, raise with {flag})"
        else:
            gate = ""
        print(f"{rule.code:<{width}}  {rule.default_severity.value:<7}  {rule.summary}{gate}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, lint every path, print findings. Returns a process exit status."""
    parser = argparse.ArgumentParser(
        prog="bigfix-relevance-lint",
        description=(
            "Lint every relevance site found in the given files: parse failures, "
            "unbound `it`, and type errors are always errors, unknown inspectors "
            "are always warnings, and complexity / evaluation cost are errors "
            f"past a built-in ceiling (default {DEFAULT_MAX_SCORE:g} / "
            f"{DEFAULT_MAX_EVALUATION_COST:g}) that --max-score/--max-evaluation-cost raise."
        ),
    )
    parser.add_argument(
        "paths", nargs="*", help="files to lint; omit entirely to walk the current directory"
    )
    parser.add_argument(
        "--max-score",
        type=float,
        default=None,
        help=f"fail a site scoring above this (default {DEFAULT_MAX_SCORE:g})",
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
        help=(
            "fail a site whose evaluation cost is above this "
            f"(default {DEFAULT_MAX_EVALUATION_COST:g})"
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit findings as one JSON object instead of one line each",
    )
    parser.add_argument(
        "--dialect",
        choices=[Dialect.CLIENT.value, Dialect.SESSION.value],
        help="force the dialect instead of trusting extraction",
    )
    parser.add_argument("--platform", help="narrow client lookups to one platform, e.g. windows")
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print every rule, its default severity and what it means, then exit",
    )
    args = parser.parse_args(argv)

    if args.list_rules:
        return _print_rules(as_json=args.json)

    severities: dict[str, Severity] = {}
    severities.update(_severity_map(args.warn, Severity.WARNING))
    severities.update(_severity_map(args.error, Severity.ERROR))
    severities.update(_severity_map(args.ignore, Severity.IGNORE))

    # Only override `max_score`/`max_evaluation_cost` when the flag was
    # actually given -- omitting a flag means "use LintConfig's own default
    # ceiling", not "pass None and disable the rule".
    config = LintConfig(
        severities=severities,
        dialect=Dialect(args.dialect) if args.dialect else None,
        platform=args.platform,
    )
    if args.max_score is not None:
        config = dataclasses.replace(config, max_score=args.max_score)
    if args.max_evaluation_cost is not None:
        config = dataclasses.replace(config, max_evaluation_cost=args.max_evaluation_cost)

    if args.paths:
        findings = lint_paths(args.paths, config)
        scope = f"{len(args.paths)} file(s)"
    else:
        findings = lint_directory(".", config, max_depth=args.max_depth)
        scope = "the current directory"

    # One tally, from `lint.counts`, feeding the summary, the exit status and
    # the JSON payload alike -- rather than each recounting the findings and
    # risking three answers to one question.
    tallies = counts(findings)
    errors = tallies[Severity.ERROR.value]
    warnings = tallies[Severity.WARNING.value]

    if not args.quiet:
        if args.json:
            json.dump(
                {
                    "findings": [finding.to_dict() for finding in findings],
                    "counts": dict(tallies),
                    "ok": errors == 0,
                    "scope": scope,
                },
                sys.stdout,
                indent=2,
            )
            print()
        else:
            for finding in findings:
                print(finding)

    print(_summary(errors, warnings, scope), file=sys.stderr)

    if errors or (args.fail_on_warning and warnings):
        return 1
    return 0


def _summary(errors: int, warnings: int, scope: str) -> str:
    return f"{errors} error(s), {warnings} warning(s) in {scope}"


if __name__ == "__main__":
    raise SystemExit(main())
