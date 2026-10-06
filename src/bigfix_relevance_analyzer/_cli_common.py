"""Plumbing both command lines share: their common flags, the
:class:`~bigfix_relevance_analyzer.lint.LintConfig` those flags build, and JSON
output.

A module of its own rather than a home in either CLI: ``_lint_cli``
deliberately does not import ``__main__`` (see its docstring), and the two must
not drift on what an omitted ceiling flag means -- exactly the bug two copies
of :func:`config_from_args` would invite.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from collections.abc import Sequence

from bigfix_relevance_analyzer._markdown import table
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    Finding,
    LintConfig,
    Severity,
    lint_directory,
    lint_paths,
    rules,
)

__all__: list[str] = []


def emit_json(payload: object) -> None:
    """Write ``payload`` to stdout as indented JSON, newline-terminated."""
    json.dump(payload, sys.stdout, indent=2)
    print()


def add_format_args(parser: argparse.ArgumentParser, *, json_help: str) -> None:
    """``--json`` and ``--markdown``: the two opt-in alternatives to plain text.

    Mutually exclusive, and the same pair on every CLI here, so a caller learns
    one spelling: text for a person at a terminal by default, ``--markdown``
    for pasting into an issue or a PR, ``--json`` for a program.
    """
    formats = parser.add_mutually_exclusive_group()
    formats.add_argument("--json", action="store_true", help=json_help)
    formats.add_argument(
        "--markdown",
        action="store_true",
        help="emit Markdown instead, e.g. to paste into an issue or PR",
    )


def output_format(args: argparse.Namespace) -> str:
    """``"json"``, ``"markdown"`` or ``"text"``, from :func:`add_format_args`' flags."""
    if args.json:
        return "json"
    return "markdown" if args.markdown else "text"


def print_rules(output: str) -> int:
    """The lint rule catalog -- see :data:`~bigfix_relevance_analyzer.lint.RULES`.

    The one listing both CLIs print, in whichever :func:`output_format` was
    asked for, so a code in either one's output can be looked up with
    whichever entry point produced it. The text columns are aligned to the
    widest code present, so adding a rule does not leave the list crooked.
    """
    listed = rules()
    if output == "json":
        emit_json([rule.to_dict() for rule in listed])
        return 0

    defaults = LintConfig()

    def ceiling(threshold: str) -> str:
        return f"{getattr(defaults, threshold):g}"

    if output == "markdown":
        rows = [
            (
                f"`{rule.code}`",
                rule.default_severity.value,
                rule.summary,
                (
                    f"`{rule.threshold}` (default {ceiling(rule.threshold)})"
                    if rule.threshold
                    else "always on"
                ),
            )
            for rule in listed
        ]
        print("# Lint rules\n")
        print(table(("Code", "Default", "Fires when", "Ceiling"), rows))
        return 0

    width = max(len(rule.code) for rule in listed)
    for rule in listed:
        gate = ""
        if rule.threshold:
            flag = f"--{rule.threshold.replace('_', '-')}"
            gate = f" (default {ceiling(rule.threshold)}, raise with {flag})"
        print(f"{rule.code:<{width}}  {rule.default_severity.value:<7}  {rule.summary}{gate}")
    return 0


def add_scope_args(
    parser: argparse.ArgumentParser, *, dialect_help: str, platform_help: str
) -> None:
    """``--dialect`` and ``--platform``: which relevance, evaluated where."""
    parser.add_argument(
        "--dialect",
        choices=[Dialect.CLIENT.value, Dialect.SESSION.value],
        help=dialect_help,
    )
    parser.add_argument("--platform", help=platform_help)


def add_ceiling_args(
    parser: argparse.ArgumentParser,
    *,
    max_score_help: str,
    max_evaluation_cost_help: str,
    max_depth_help: str | None,
) -> None:
    """``--max-score``, ``--max-evaluation-cost`` and, unless its help is ``None``, ``--max-depth``.

    The two ceilings default to ``None``, meaning "not given" -- see
    :func:`config_from_args` for why that must not reach
    :class:`~bigfix_relevance_analyzer.lint.LintConfig` as-is.
    """
    parser.add_argument("--max-score", type=float, default=None, help=max_score_help)
    parser.add_argument(
        "--max-evaluation-cost", type=float, default=None, help=max_evaluation_cost_help
    )
    if max_depth_help is not None:
        parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH, help=max_depth_help)


def dialect_from_args(args: argparse.Namespace) -> Dialect | None:
    """The ``--dialect`` the caller forced, or ``None`` to classify/trust extraction."""
    return Dialect(args.dialect) if args.dialect else None


def config_from_args(
    args: argparse.Namespace, *, severities: dict[str, Severity] | None = None
) -> LintConfig:
    """Build a :class:`~bigfix_relevance_analyzer.lint.LintConfig` from parsed flags.

    ``max_score``/``max_evaluation_cost`` come straight from ``argparse``,
    which defaults each to ``None`` when its flag is omitted. Passing that
    ``None`` through would override :class:`LintConfig`'s own built-in ceiling
    to "disabled" -- the opposite of what an omitted flag should mean. So a
    field is overridden only when the caller actually gave a value.
    """
    config = LintConfig(
        severities=severities or {},
        dialect=dialect_from_args(args),
        platform=args.platform,
    )
    if args.max_score is not None:
        config = dataclasses.replace(config, max_score=args.max_score)
    if args.max_evaluation_cost is not None:
        config = dataclasses.replace(config, max_evaluation_cost=args.max_evaluation_cost)
    return config


def lint_targets(
    paths: Sequence[str | os.PathLike[str]], config: LintConfig, *, max_depth: int
) -> tuple[Finding, ...]:
    """Lint ``paths`` literally, or walk the current directory when there are none.

    An *explicit* path, including ``.``, is never expanded -- see
    :func:`~bigfix_relevance_analyzer.lint.lint_directory`.
    """
    if paths:
        return lint_paths(paths, config)
    return lint_directory(".", config, max_depth=max_depth)
