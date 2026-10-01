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


def emit_rules_json() -> int:
    """The lint rule catalog as JSON -- the one rules listing both CLIs share.

    Their text forms differ on purpose (an aligned list for a hook's terminal,
    a Markdown table for a report), so only this one lives here.
    """
    emit_json([rule.to_dict() for rule in rules()])
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
    max_depth_help: str,
) -> None:
    """``--max-score``, ``--max-evaluation-cost`` and ``--max-depth``.

    The two ceilings default to ``None``, meaning "not given" -- see
    :func:`config_from_args` for why that must not reach
    :class:`~bigfix_relevance_analyzer.lint.LintConfig` as-is.
    """
    parser.add_argument("--max-score", type=float, default=None, help=max_score_help)
    parser.add_argument(
        "--max-evaluation-cost", type=float, default=None, help=max_evaluation_cost_help
    )
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
