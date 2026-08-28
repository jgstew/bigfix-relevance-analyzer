"""Command line: analyse one relevance statement and print the result.

    python -m bigfix_relevance_analyzer 'exists file "C:\\foo.txt"'
    echo 'names of processes' | python -m bigfix_relevance_analyzer --json

This is the one module in the package that writes to stdout, and it runs only
when invoked as a script -- importing the library, including
:mod:`~bigfix_relevance_analyzer.analyzer`, still prints nothing, which is what
keeps it safe inside a stdio MCP server.

Rendering only; every conclusion comes from
:func:`~bigfix_relevance_analyzer.analyzer.analyze`.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.typecheck import Plurality

_WIDTH = 62


def _section(title: str) -> None:
    print(f"\n== {title} " + "=" * max(3, _WIDTH - len(title)))


def _render_dialect(report: RelevanceAnalysis) -> None:
    _section("dialect")
    classified = report.classified_dialect
    print(f"classified: {classified.value if classified else 'undetermined'}")
    if report.requested_dialect is not None:
        print(f"forced:     {report.requested_dialect.value}")
    suffix = "  (assumed -- nothing in the text settles it)" if report.dialect_assumed else ""
    print(f"effective:  {report.dialect.value}{suffix}")


def _render_lexing(report: RelevanceAnalysis) -> None:
    _section("lexing")
    print(f"{len(report.code_tokens)} code tokens of {len(report.tokens)}: {report.token_kinds}")
    for token in report.error_tokens:
        print(f"  ERROR token {token.text!r} at line {token.line}, column {token.column}")


def _render_parse(report: RelevanceAnalysis) -> None:
    _section("parse")
    if report.parse_error is not None:
        error = report.parse_error
        print(f"FAILED at line {error.line}, column {error.column}: {error.message}")
        return
    print(f"ok: {len(report.nodes)} nodes, tree depth {report.tree_depth}")
    print(f"kinds: {report.node_kinds}")
    print(f"sexpr: {report.sexpr}")


def _render_types(report: RelevanceAnalysis) -> None:
    checked = report.check
    if checked is None:
        return
    _section("types")
    types = checked.value.types
    plurality = checked.value.plurality
    if types is None:
        rendered = "unknown -- no table entry settles it"
    elif not types:
        rendered = "none -- every candidate was ruled out"
    else:
        # The engine's own diagnostics word this pair as '{plurality} {type}'.
        prefix = "" if plurality is Plurality.UNKNOWN else f"{plurality.value} "
        rendered = prefix + " or ".join(sorted(types))
    print(f"evaluates to: {rendered}")
    if not checked.diagnostics:
        print("diagnostics: none")
    for diagnostic in checked.diagnostics:
        where = f"line {diagnostic.span.line}, col {diagnostic.span.column}"
        print(f"  [{diagnostic.code}] {where}: {diagnostic.message}")


def _render_platforms(report: RelevanceAnalysis) -> None:
    _section("platforms")
    if report.dialect is not Dialect.CLIENT:
        print("not an axis: session relevance runs on the server, not an endpoint")
        return
    print(f"viable:  {', '.join(sorted(report.platforms)) or 'none reported'}")
    print(f"missing: {', '.join(sorted(report.missing_platforms)) or 'none'}")
    print("note:    tables only -- a platform absent from the dumps is not proven unsupported")


def _render_inspectors(report: RelevanceAnalysis) -> None:
    _section("inspectors")
    if not report.references:
        print("no names to resolve")
    for entry in report.references:
        if entry.visible:
            mark = "ok"
        elif entry.known:
            mark = "??"  # real, but not reachable in this dialect or platform
        else:
            mark = "!!"
        print(f"{mark} {entry.phrase!r} -> {', '.join(entry.return_types) or 'unknown'}")
        for signature in sorted({row.signature for row in entry.resolved}):
            print(f"     {signature}")
        visible_platforms = entry.platforms & report.environment.universe
        if visible_platforms:
            print(f"     platforms: {', '.join(sorted(visible_platforms))}")
        if entry.known and not entry.visible:
            print(f"     not visible as {report.dialect.value} relevance here")
    if report.unknown_references:
        print(f"unknown to every dump: {', '.join(report.unknown_references)}")


def _render_bindings(report: RelevanceAnalysis) -> None:
    _section("it bindings")
    if not report.it_bindings:
        print("none")
    for entry in report.it_bindings:
        where = f"line {entry.it.span.line}, col {entry.it.span.column}"
        if entry.context is None:
            print(f"{where}: UNBOUND -- 'it' used with no context")
            continue
        context = report.text[entry.context.span.start : entry.context.span.end]
        binder = entry.binder.value if entry.binder else "?"
        print(f"{where}: bound by {binder} to {context!r}")


def _render_levels(report: RelevanceAnalysis) -> None:
    _section("breakdown probes")
    if not report.levels:
        print("no measurable levels")
    for level in report.levels:
        print(f"level: {level.label}")
        print(f"  {level.probe.relevance}")
        if level.unfiltered is not None:
            print(f"  unfiltered: {level.unfiltered.relevance}")


def _render_complexity(report: RelevanceAnalysis) -> None:
    metrics = report.complexity
    _section("complexity")
    print(f"score: {metrics.score:.3g}   evaluation cost: {metrics.evaluation_cost:.3g}")
    # Only the non-zero counts: a metric a statement does not exercise says
    # nothing, and printing thirty zeroes buries the handful that do.
    for field in dataclasses.fields(metrics):
        value = getattr(metrics, field.name)
        if value and field.name not in {"evaluation_cost", "costly_inspectors"}:
            print(f"  {field.name}: {value}")
    for rule in report.cost_rules:
        print(f"  cost rule: {rule.label} (+{rule.cost_for(report.dialect):.3g}) -- {rule.why}")


def render(report: RelevanceAnalysis) -> None:
    """Print the whole analysis. Tree-dependent sections are skipped when the
    statement did not parse, since there is nothing to report in them."""
    _section("input")
    print(report.text)
    _render_dialect(report)
    _render_lexing(report)
    _render_parse(report)
    if report.parsed:
        _render_types(report)
        _render_platforms(report)
        _render_inspectors(report)
        _render_bindings(report)
        _render_levels(report)
    _render_complexity(report)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, analyse, print. Returns a process exit status."""
    parser = argparse.ArgumentParser(
        prog="python -m bigfix_relevance_analyzer",
        description=(
            "Analyse one BigFix Relevance statement: dialect, parse, types, "
            "platforms, bindings, breakdown probes, complexity."
        ),
    )
    parser.add_argument("relevance", nargs="?", help="the statement; omit to read stdin")
    parser.add_argument(
        "--dialect",
        choices=[Dialect.CLIENT.value, Dialect.SESSION.value],
        help="force the dialect instead of classifying it from the text",
    )
    parser.add_argument("--platform", help="narrow client lookups to one platform, e.g. windows")
    parser.add_argument("--json", action="store_true", help="emit the analysis as JSON")
    args = parser.parse_args(argv)

    text = (args.relevance if args.relevance is not None else sys.stdin.read()).strip()
    if not text:
        parser.error("no relevance statement given")

    report = analyze(text, Dialect(args.dialect) if args.dialect else None, args.platform)
    if args.json:
        json.dump(report.to_dict(), sys.stdout, indent=2)
        print()
    else:
        render(report)
    # Unparsable input is a finding, not a crash, but a hook wants to know.
    return 0 if report.parsed else 1


if __name__ == "__main__":
    raise SystemExit(main())
