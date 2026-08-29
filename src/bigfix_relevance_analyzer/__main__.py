"""Command line: analyse one relevance statement and print the result.

    python -m bigfix_relevance_analyzer 'exists file "C:\\foo.txt"'
    echo 'names of processes' | python -m bigfix_relevance_analyzer --json
    python -m bigfix_relevance_analyzer --mermaid 'names of files of folder "/tmp"'
    python -m bigfix_relevance_analyzer MyFixlet.bes

The parse tree's Mermaid flowchart is behind ``--mermaid`` in both output
modes -- Markdown and ``--json`` -- because it costs a line per box and per
edge, which on a real statement outweighs every other section combined, and
the S-expression right beside it already says the same thing in one line.

The last form is not relevance itself -- it is a path to a real file. When the
sole argument names one that exists, it is run through
:func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file` first,
and every :class:`~bigfix_relevance_analyzer.extract.RelevanceSite` it finds is
analysed and reported in turn, each against the dialect extraction already
determined for it. Anything else -- including a nonexistent path, which is far
more often a typo in a relevance statement than a real intended file -- is
analysed directly as relevance text.

This is the one module in the package that writes to stdout, and it runs only
when invoked as a script -- importing the library, including
:mod:`~bigfix_relevance_analyzer.analyzer`, still prints nothing, which is what
keeps it safe inside a stdio MCP server.

Rendering only; every conclusion comes from
:func:`~bigfix_relevance_analyzer.analyzer.analyze` and
:func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file`.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_file
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    LintConfig,
    Severity,
    counts,
    lint_directory,
    lint_paths,
    rules,
)
from bigfix_relevance_analyzer.typecheck import Plurality


def _heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def _cell(text: str, *, max_len: int = 72) -> str:
    """Render arbitrary text as a table cell: collapsed, truncated, escaped.

    Relevance source is table-hostile in two ways a fixed value never is: it
    can run to hundreds of characters (a `whose` context can be the entire
    outer expression), and `|` is a real operator (error fallback) that would
    otherwise be read as a column break -- even inside the code span this
    wraps it in, which is a GFM quirk, not an oversight. Collapsing whitespace
    also flattens a source snippet's own embedded newlines onto one line.
    """
    collapsed = " ".join(text.split())
    if len(collapsed) > max_len:
        collapsed = collapsed[: max_len - 1] + "..."
    return f"`{collapsed.replace('|', chr(92) + '|')}`"


def _fence(text: str, *, lang: str = "") -> list[str]:
    return [f"```{lang}", text, "```"]


def _dialect_summary(report: RelevanceAnalysis) -> str:
    if report.dialect_assumed:
        return f"`{report.dialect.value}` - assumed, nothing settles it"
    return f"`{report.dialect.value}`"


def _render_summary(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "Summary"), "", "| | |", "|---|---|"]
    lines.append(f"| Dialect | {_dialect_summary(report)} |")
    if report.parsed:
        parsed = f"{len(report.nodes)} nodes, tree depth {report.tree_depth}"
        lines.append(f"| Parse | :white_check_mark: ok - {parsed} |")
    else:
        assert report.parse_error is not None
        error = report.parse_error
        lines.append(f"| Parse | :x: line {error.line}, col {error.column}: {error.message} |")
    if report.check is not None:
        types = report.check.value.types
        plurality = report.check.value.plurality
        if types is None:
            rendered = "unknown"
        elif not types:
            rendered = "none"
        else:
            prefix = "" if plurality is Plurality.UNKNOWN else f"{plurality.value} "
            rendered = prefix + " or ".join(sorted(types))
        lines.append(f"| Type | {rendered} |")
    if report.dialect is Dialect.CLIENT and report.parsed:
        lines.append(
            f"| Platforms | {len(report.platforms)}/{len(report.environment.universe)} viable |"
        )
    lines.append(f"| Complexity score | {report.complexity.score:.3g} |")
    if report.complexity.evaluation_cost:
        lines.append(f"| Evaluation cost | {report.complexity.evaluation_cost:.3g} |")
    lines.append("")
    return lines


def _render_lexing(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "Lexing"), ""]
    lines.append(f"- {len(report.code_tokens)} code tokens of {len(report.tokens)} total")
    lines.append(f"- by kind: {_cell(str(report.token_kinds), max_len=200)}")
    for token in report.error_tokens:
        lines.append(
            f"- :warning: ERROR token {_cell(token.text)} at line {token.line}, col {token.column}"
        )
    lines.append("")
    return lines


def _render_parse(report: RelevanceAnalysis, level: int, *, mermaid: bool) -> list[str]:
    lines = [_heading(level, "Parse tree"), ""]
    lines.append(f"- {len(report.nodes)} nodes, tree depth {report.tree_depth} of {200} max")
    lines.append(f"- node kinds: {_cell(str(report.node_kinds), max_len=200)}")
    lines.append("")
    assert report.sexpr is not None
    lines.extend(_fence(report.sexpr))
    lines.append("")
    # Opt-in: the diagram is one line per box and per edge, so it outweighs
    # every other section combined on anything but a small statement.
    if mermaid:
        assert report.mermaid is not None
        lines.extend(_fence(report.mermaid, lang="mermaid"))
        lines.append("")
    return lines


def _render_platforms(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "Platforms"), ""]
    if report.dialect is not Dialect.CLIENT:
        lines.append("Not an axis: session relevance runs on the server, not an endpoint.")
        lines.append("")
        return lines
    viable = sorted(report.platforms)
    missing = sorted(report.missing_platforms)
    lines.append(f"- **Viable:** {', '.join(viable) or 'none reported'}")
    lines.append(f"- **Missing:** {', '.join(missing) or 'none'}")
    lines.append("- _Tables only - a platform absent from the dumps is not proven unsupported._")
    lines.append("")
    return lines


def _render_inspectors(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "Inspectors"), ""]
    if not report.references:
        lines.append("No names to resolve.")
        lines.append("")
        return lines
    lines.append("| Name | Status | Returns | Platforms |")
    lines.append("|---|---|---|---|")
    for entry in report.references:
        if entry.visible:
            status = ":white_check_mark: ok"
        elif entry.known:
            status = ":warning: not visible here"
        else:
            status = ":x: unknown"
        platforms = ", ".join(sorted(entry.platforms & report.environment.universe))
        returns = ", ".join(entry.return_types) or "-"
        lines.append(f"| `{entry.phrase}` | {status} | {returns} | {platforms or '-'} |")
    lines.append("")
    if report.unknown_references:
        lines.append(f"**Unknown to every dump:** {', '.join(report.unknown_references)}")
        lines.append("")
    return lines


def _render_bindings(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "`it` bindings"), ""]
    if not report.it_bindings:
        lines.append("None.")
        lines.append("")
        return lines
    lines.append("| Location | Binder | Bound to |")
    lines.append("|---|---|---|")
    for entry in report.it_bindings:
        where = f"{entry.it.span.line}:{entry.it.span.column}"
        if entry.context is None:
            lines.append(f"| {where} | - | :warning: **UNBOUND** - used with no context |")
            continue
        context = report.text[entry.context.span.start : entry.context.span.end]
        binder = entry.binder.value if entry.binder else "?"
        lines.append(f"| {where} | {binder} | {_cell(context)} |")
    lines.append("")
    return lines


def _render_levels(report: RelevanceAnalysis, level: int) -> list[str]:
    lines = [_heading(level, "Breakdown probes"), ""]
    if not report.levels:
        lines.append("No measurable levels.")
        lines.append("")
        return lines
    for index, probe_level in enumerate(report.levels, 1):
        lines.append(f"{index}. **{_cell(probe_level.label, max_len=88)}**")
        lines.extend(f"   {line}" for line in _fence(probe_level.probe.relevance))
        if probe_level.unfiltered is not None:
            lines.append("   unfiltered:")
            lines.extend(f"   {line}" for line in _fence(probe_level.unfiltered.relevance))
    lines.append("")
    return lines


def _render_complexity(report: RelevanceAnalysis, level: int) -> list[str]:
    metrics = report.complexity
    lines = [_heading(level, "Complexity"), ""]
    lines.append(
        f"Score **{metrics.score:.3g}**, evaluation cost **{metrics.evaluation_cost:.3g}**."
    )
    lines.append("")
    nonzero = [
        (field.name, getattr(metrics, field.name))
        for field in dataclasses.fields(metrics)
        if field.name not in {"evaluation_cost", "costly_inspectors"}
        and getattr(metrics, field.name)
    ]
    if nonzero:
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        # Only the non-zero counts: a metric a statement does not exercise
        # says nothing, and printing thirty zeroes buries the ones that do.
        lines.extend(f"| {name} | {value} |" for name, value in nonzero)
        lines.append("")
    for rule in report.cost_rules:
        cost = rule.cost_for(report.dialect)
        lines.append(f"- **{rule.label}** (+{cost:.3g}) - {rule.why}")
    if report.cost_rules:
        lines.append("")
    return lines


def render(
    report: RelevanceAnalysis,
    *,
    level: int = 1,
    heading: str | None = None,
    mermaid: bool = False,
) -> str:
    """Render the whole analysis as Markdown. Returns the text; prints nothing.

    ``level`` is the heading depth for this report's own title (``#`` by
    default); every section below it nests one level deeper, so a report
    embedded under a file's per-site heading still forms a coherent outline.
    Tree-dependent sections are skipped when the statement did not parse,
    since there is nothing to report in them.

    ``mermaid`` adds the parse tree's flowchart to the parse section. Off by
    default because it costs a line per box and per edge, which on a real
    statement outweighs the whole rest of the report; the S-expression right
    above it already says the same thing in one line.
    """
    lines = [_heading(level, heading or "Relevance Analysis"), ""]
    lines.extend(_fence(report.text))
    lines.append("")
    lines.extend(_render_summary(report, level + 1))
    lines.extend(_render_lexing(report, level + 1))
    if report.parsed:
        lines.extend(_render_parse(report, level + 1, mermaid=mermaid))
        lines.extend(_render_platforms(report, level + 1))
        lines.extend(_render_inspectors(report, level + 1))
        lines.extend(_render_bindings(report, level + 1))
        lines.extend(_render_levels(report, level + 1))
    else:
        assert report.parse_error is not None
        lines.append(_heading(level + 1, "Parse error"))
        lines.append("")
        error = report.parse_error
        lines.append(f"> Line {error.line}, column {error.column}: {error.message}")
        lines.append("")
    lines.extend(_render_complexity(report, level + 1))
    return "\n".join(lines).rstrip() + "\n"


def _site_heading(site: RelevanceSite) -> str:
    return f"{site.context} (line {site.line}, {site.kind})"


def _analyze_site(
    site: RelevanceSite, forced: Dialect | None, platform: str | None
) -> RelevanceAnalysis:
    # A site the extractor already classified is a stronger signal than
    # re-classifying the bare fragment: --dialect still wins when the caller
    # forced one, but otherwise trust extraction's read of the surrounding
    # document over guessing from the statement alone.
    dialect = (
        forced if forced is not None else (site.dialect if is_definite(site.dialect) else None)
    )
    return analyze(site.text, dialect, platform)


def _run_file(
    path: Path,
    forced: Dialect | None,
    platform: str | None,
    *,
    as_json: bool,
    mermaid: bool,
) -> int:
    sites = extract_relevance_from_file(path)
    if not sites:
        if as_json:
            json.dump({"file": str(path), "sites": []}, sys.stdout, indent=2)
            print()
        else:
            print(f"# Relevance Analysis: {path}\n\nNo relevance found.")
        return 0

    reports = [(site, _analyze_site(site, forced, platform)) for site in sites]
    if as_json:
        json.dump(
            {
                "file": str(path),
                "sites": [
                    {
                        "kind": site.kind,
                        "line": site.line,
                        "context": site.context,
                        "site_dialect": site.dialect.value,
                        "analysis": report.to_dict(mermaid=mermaid),
                    }
                    for site, report in reports
                ],
            },
            sys.stdout,
            indent=2,
        )
        print()
    else:
        print(f"# Relevance Analysis: {path}\n")
        print(f"{len(sites)} relevance site(s) found.\n")
        for index, (site, report) in enumerate(reports, 1):
            heading = f"Site {index}: {_site_heading(site)}"
            print(render(report, level=2, heading=heading, mermaid=mermaid))
    return 0 if all(report.parsed for _site, report in reports) else 1


def _run_check(
    paths: list[str],
    forced: Dialect | None,
    platform: str | None,
    *,
    max_score: float | None,
    max_evaluation_cost: float | None,
    max_depth: int,
) -> int:
    """Lint every path: one grep-able line per finding, for a hook or CI.

    Given no paths at all, walks the current directory (see
    :func:`~bigfix_relevance_analyzer.lint.lint_directory`) instead of erroring --
    an *explicit* path, including ``.``, is never expanded this way.

    The full rule set and its severities live in
    :mod:`~bigfix_relevance_analyzer.lint`; ``bigfix-relevance-lint`` (see
    :mod:`~bigfix_relevance_analyzer._lint_cli`) offers the rest of that
    module's knobs (per-code severity overrides, ``--fail-on-warning``,
    ``--quiet``) for a caller that needs them -- this flag exists so the same
    judgement is reachable without a second console script installed.
    """
    config = LintConfig(
        max_score=max_score,
        max_evaluation_cost=max_evaluation_cost,
        dialect=forced,
        platform=platform,
    )
    if paths:
        findings = lint_paths(paths, config)
    else:
        findings = lint_directory(".", config, max_depth=max_depth)
    for finding in findings:
        print(finding)
    # Same verdict `bigfix-relevance-lint` exits on, from the same tally -- see
    # :func:`~bigfix_relevance_analyzer.lint.counts`.
    return 0 if counts(findings)[Severity.ERROR.value] == 0 else 1


def _run_rules(*, as_json: bool) -> int:
    """Print the lint rule catalog -- see :data:`~bigfix_relevance_analyzer.lint.RULES`.

    Here as well as on ``bigfix-relevance-lint`` because the codes show up in
    this CLI's ``--check`` output too, and a code should be lookup-able with
    whichever entry point produced it.
    """
    listed = rules()
    if as_json:
        json.dump([rule.to_dict() for rule in listed], sys.stdout, indent=2)
        print()
        return 0

    print("# Lint rules\n")
    print("| Code | Default | Fires when | Needs |")
    print("| --- | --- | --- | --- |")
    for rule in listed:
        needs = f"`{rule.threshold}`" if rule.threshold else "always on"
        print(f"| `{rule.code}` | {rule.default_severity.value} | {rule.summary} | {needs} |")
    return 0


def _run_reference(slug: str, *, brief: bool, as_json: bool) -> int:
    """Print one language reference document.

    ``--reference client`` is spelled the way the ``--dialect`` flag is rather
    than as the document's own slug, because a caller already knows the dialect
    names from every other flag here; the slug is translated rather than made
    the user's problem. Imported inside the function for the same reason the
    package does not import :mod:`~bigfix_relevance_analyzer.reference` at all:
    nothing pays for a document it did not ask for.
    """
    from bigfix_relevance_analyzer import reference

    document = reference.get_document(slug if slug == "dialects" else f"{slug}-relevance")
    detail = reference.Detail.BRIEF if brief else reference.Detail.STANDARD
    if as_json:
        json.dump(document.to_dict(detail=detail), sys.stdout, indent=2)
        print()
    else:
        print(document.read(detail=detail), end="")
    return 0


def _run_search(query: str, dialect: Dialect | None, *, as_json: bool) -> int:
    """Search the inspector tables and print what was found.

    Here for the same reason ``--reference`` is: it makes the capability
    discoverable, and it gives the documentation something a reader can actually
    run. ``--dialect`` narrows it, since suggesting a session inspector to
    somebody writing client relevance is worse than suggesting nothing.

    Exits 0 even when nothing matched -- an empty result is an answer, not a
    failure, and a script asking "is there anything called this" should be able
    to tell the two apart by reading the output rather than the status.
    """
    from bigfix_relevance_analyzer import inspectors

    results = inspectors.search(query, dialect=dialect)
    if as_json:
        json.dump(
            {"query": query, "results": [result.to_dict() for result in results]},
            sys.stdout,
            indent=2,
        )
        print()
        return 0

    if not results:
        print(f"# Inspector search: {query}\n\nNothing matched.")
        return 0

    print(f"# Inspector search: {query}\n")
    print("| Match | Name | Found via | Overloads | Returns |")
    print("| --- | --- | --- | --- | --- |")
    for result in results:
        returns = ", ".join(f"`{name}`" for name in result.return_types[:3])
        if len(result.return_types) > 3:
            returns += " ..."
        print(
            f"| {result.match.value} | {_cell(result.name)} | {_cell(result.matched)} "
            f"| {len(result.inspectors)} | {returns} |"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, analyse, print. Returns a process exit status."""
    parser = argparse.ArgumentParser(
        prog="python -m bigfix_relevance_analyzer",
        description=(
            "Analyse one BigFix Relevance statement: dialect, parse, types, "
            "platforms, bindings, breakdown probes, complexity. Given a path to "
            "an existing file instead, extract and analyse every relevance site "
            "in it."
        ),
    )
    parser.add_argument(
        "relevance",
        nargs="*",
        help=(
            "the statement, or a file path; omit to read stdin. "
            "With --check, one or more files to lint"
        ),
    )
    parser.add_argument(
        "--dialect",
        choices=[Dialect.CLIENT.value, Dialect.SESSION.value],
        help="force the dialect instead of classifying it (or trusting extraction)",
    )
    parser.add_argument("--platform", help="narrow client lookups to one platform, e.g. windows")
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="add the parse tree as a Mermaid flowchart (verbose: a line per box and edge)",
    )
    parser.add_argument("--json", action="store_true", help="emit the analysis as JSON")
    parser.add_argument(
        "--rules",
        action="store_true",
        help="print the lint rule catalog and exit, instead of analysing anything",
    )
    parser.add_argument(
        "--reference",
        choices=["client", "session", "dialects"],
        help=(
            "print a relevance language reference and exit -- the same Markdown "
            "an MCP server would serve as a resource"
        ),
    )
    parser.add_argument(
        "--search",
        metavar="QUERY",
        help=(
            "search the inspector tables for QUERY and exit -- partial names, "
            "typos, and phrases like 'registry keys' all work"
        ),
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="with --reference, the authored prose only, without the generated tables",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "lint the given files instead of analysing a single statement -- "
            "one grep-able line per finding, for a pre-commit hook or CI"
        ),
    )
    parser.add_argument(
        "--max-score",
        type=float,
        default=None,
        help="with --check, fail a site scoring above this",
    )
    parser.add_argument(
        "--max-evaluation-cost",
        type=float,
        default=None,
        help="with --check, fail a site whose evaluation cost is above this",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=(
            "with --check and no paths, how many directory levels to walk "
            f"(default {DEFAULT_MAX_DEPTH})"
        ),
    )
    args = parser.parse_args(argv)
    forced = Dialect(args.dialect) if args.dialect else None

    # Both of these are questions about the language or the tool rather than
    # about a statement, so they are answered before anything else looks at the
    # positional arguments -- and they exit 0 even alongside a broken file.
    if args.rules:
        return _run_rules(as_json=args.json)

    if args.reference is not None:
        return _run_reference(args.reference, brief=args.brief, as_json=args.json)

    if args.search is not None:
        return _run_search(args.search, forced, as_json=args.json)

    if args.check:
        return _run_check(
            args.relevance,
            forced,
            args.platform,
            max_score=args.max_score,
            max_evaluation_cost=args.max_evaluation_cost,
            max_depth=args.max_depth,
        )

    if len(args.relevance) > 1:
        parser.error("only one statement or file is accepted without --check")

    if args.relevance:
        candidate = Path(args.relevance[0])
        try:
            is_file = candidate.is_file()
        except OSError:
            # A statement long or strange enough to trip the filesystem (name
            # too long, embedded NUL) is relevance text, not a path -- treat it
            # as such rather than letting the OSError escape.
            is_file = False
        if is_file:
            return _run_file(
                candidate, forced, args.platform, as_json=args.json, mermaid=args.mermaid
            )
        text = args.relevance[0].strip()
    else:
        text = sys.stdin.read().strip()

    if not text:
        parser.error("no relevance statement given")

    report = analyze(text, forced, args.platform)
    if args.json:
        json.dump(report.to_dict(mermaid=args.mermaid), sys.stdout, indent=2)
        print()
    else:
        print(render(report, mermaid=args.mermaid), end="")
    # Unparsable input is a finding, not a crash, but a hook wants to know.
    return 0 if report.parsed else 1


if __name__ == "__main__":
    raise SystemExit(main())
