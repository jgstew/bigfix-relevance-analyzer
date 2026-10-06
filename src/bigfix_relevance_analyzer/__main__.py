"""Command line: analyse one relevance statement and print the result.

    python -m bigfix_relevance_analyzer 'exists file "C:\\foo.txt"'
    echo 'names of processes' | python -m bigfix_relevance_analyzer --json
    python -m bigfix_relevance_analyzer --verbose 'names of files of folder "/tmp"'
    python -m bigfix_relevance_analyzer MyFixlet.bes

Default output is plain terminal text from
:mod:`~bigfix_relevance_analyzer._text`: a verdict, aligned summary rows, any
issues, and a closing ``No issues found.`` or error/warning tally.
``--markdown`` renders the same report as Markdown via :func:`render` (below),
for pasting into an issue or a PR; ``--json`` is for a program.

The Markdown report is compact: the statement, a one-screen summary, and -- only
when :mod:`~bigfix_relevance_analyzer.lint`'s rules found something worth
flagging (a parse error, an unbound ``it``, a type error, an unknown
inspector, or complexity/evaluation cost past its default ceiling) -- an
``Issues`` list of one grep-able line each, the same wording ``--check``
prints. A clean statement's default output is just the summary: nothing to
say about something that isn't wrong is itself the point. ``--verbose``
restores every other section (lexing, the parse tree, platforms, inspectors,
``it`` bindings, breakdown probes, complexity metrics) for when the full
picture is wanted rather than only what might be wrong. ``--json`` always
includes everything, verbose or not, plus the same findings under
``"findings"``.

The parse tree's Mermaid flowchart is additionally behind ``--mermaid`` (and
implies ``--verbose``, since the parse tree only renders there) -- because it
costs a line per box and per edge, which on a real statement outweighs every
other section combined, and the S-expression right beside it already says the
same thing in one line.

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
:func:`~bigfix_relevance_analyzer.analyzer.analyze`,
:func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file`, and
:func:`~bigfix_relevance_analyzer.lint.lint_analysis`.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

from bigfix_relevance_analyzer._cli_common import (
    add_ceiling_args,
    add_format_args,
    add_scope_args,
    config_from_args,
    dialect_from_args,
    emit_json,
    output_format,
    print_rules,
)
from bigfix_relevance_analyzer._markdown import capped, code_cell, table
from bigfix_relevance_analyzer._serialize import _path
from bigfix_relevance_analyzer._text import Style, render_text, verdict_line
from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_file
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_EVALUATION_COST,
    DEFAULT_MAX_SCORE,
    Finding,
    LintConfig,
    _analyze_site,
    _analyze_text,
    _passed,
    counts,
    lint_analysis,
)
from bigfix_relevance_analyzer.typecheck import Plurality, _describe_types


def _heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def _cell(text: str, *, max_len: int = 72) -> str:
    """Arbitrary relevance text as a table cell: collapsed, truncated, escaped."""
    return code_cell(text, max_len=max_len)


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
        rendered = _describe_types(types)
        if types and plurality is not Plurality.UNKNOWN:
            rendered = f"{plurality.value} {rendered}"
        lines.append(f"| Type | {rendered} |")
    if report.parsed:
        lines.append(
            f"| Platforms | {len(report.platforms)}/{len(report.environment.universe)} viable |"
        )
    lines.append(f"| Complexity score | {report.complexity.score:.3g} |")
    if report.complexity.evaluation_cost:
        lines.append(f"| Evaluation cost | {report.complexity.evaluation_cost:.3g} |")
    lines.append("")
    return lines


def _render_issues(findings: tuple[Finding, ...], level: int) -> list[str]:
    """The compact, grep-able signal a caller should not have to go looking for.

    One bullet per :class:`~bigfix_relevance_analyzer.lint.Finding`, in
    :meth:`~bigfix_relevance_analyzer.lint.Finding.__str__`'s own wording --
    the same line ``--check`` prints, so a finding reads identically wherever
    it surfaces. Empty when nothing fired, and then this renders nothing at
    all: a clean statement should not have to say so.
    """
    if not findings:
        return []
    lines = [_heading(level, "Issues"), ""]
    lines.extend(f"- {finding}" for finding in findings)
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
    viable = sorted(report.platforms)
    missing = sorted(report.missing_platforms)
    lines.append(f"- **Viable:** {', '.join(viable) or 'none reported'}")
    lines.append(f"- **Missing:** {', '.join(missing) or 'none'}")
    lines.append("- _Where this can evaluate: client platforms by name, server-side")
    lines.append("  surfaces as `session:<context>`._")
    lines.append("- _Tables only - a context absent from the dumps is not proven unsupported._")
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


def _render_autofix(
    report: RelevanceAnalysis, findings: tuple[Finding, ...], level: int
) -> list[str]:
    """The statement with every safe fix applied, when there is one.

    Shown in compact output too: a fixed statement is the most actionable line
    a report can carry, and a hook with auto-fix off prints exactly this.
    Reuses the result a finding already carries rather than working it out
    twice; a finding configured off leaves nothing to reuse, so the analysis
    is asked directly.
    """
    fixed = next((finding.autofix for finding in findings if finding.autofix), None)
    if fixed is None:
        fixed = report.autofix()
    if not fixed.changed:
        return []
    lines = [_heading(level, "Suggested fix"), ""]
    lines.extend(_fence(fixed.fixed))
    lines.append("")
    rounds = f"{fixed.rounds} round{'' if fixed.rounds == 1 else 's'}"
    for entry in fixed.to_dict()["applied"]:
        lines.append(
            f"- applied {entry['count']} `{entry['code']}` (`{entry['rule']}`) over {rounds}"
        )
    for entry in fixed.to_dict()["unapplied"]:
        lines.append(f"- left {entry['count']} `{entry['code']}` (`{entry['rule']}`) unfixed")
    lines.append("")
    return lines


def render(
    report: RelevanceAnalysis,
    *,
    level: int = 1,
    heading: str | None = None,
    mermaid: bool = False,
    findings: tuple[Finding, ...] = (),
    verbose: bool = False,
) -> str:
    """Render the analysis as Markdown. Returns the text; prints nothing.

    ``level`` is the heading depth for this report's own title (``#`` by
    default); every section below it nests one level deeper, so a report
    embedded under a file's per-site heading still forms a coherent outline.

    Compact by default (``verbose=False``): just the ``Summary`` table, plus
    an ``Issues`` section listing ``findings`` -- one grep-able line each, in
    :class:`~bigfix_relevance_analyzer.lint.Finding`'s own wording -- when
    there are any, and a ``Suggested fix`` section with the auto-fixed
    statement and what was applied, when a fix exists. Nothing to flag means
    nothing further to print; a clean statement's report ends after the
    summary.

    ``verbose=True`` additionally renders every other section this analysis
    can produce (Lexing, Parse tree, Platforms, Inspectors, ``it`` bindings,
    Breakdown probes, Complexity), tree-dependent ones skipped when the
    statement did not parse since there is nothing to report in them. This is
    the only mode that can show anything from ``mermaid=True`` -- the parse
    tree section is where the flowchart lives, so ``--mermaid`` implies
    ``--verbose`` on the CLI.
    """
    lines = [_heading(level, heading or "Relevance Analysis"), ""]
    lines.extend(_fence(report.text))
    lines.append("")
    lines.extend(_render_summary(report, level + 1))
    lines.extend(_render_issues(findings, level + 1))
    lines.extend(_render_autofix(report, findings, level + 1))
    if not verbose:
        return "\n".join(lines).rstrip() + "\n"
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


def _prog() -> str:
    """The name to report usage under: the console script, or ``python -m``."""
    name = Path(sys.argv[0]).name
    return name if name.startswith("bigfix-relevance") else "python -m bigfix_relevance_analyzer"


def _site_heading(site: RelevanceSite) -> str:
    return f"{site.context} (line {site.line}, {site.kind})"


def _run_file(
    path: Path,
    config: LintConfig,
    *,
    output: str,
    mermaid: bool,
    verbose: bool,
) -> int:
    sites = extract_relevance_from_file(path)
    if not sites:
        if output == "json":
            emit_json({"file": _path(path), "sites": []})
        elif output == "markdown":
            print(f"# Relevance Analysis: {path}\n\nNo relevance found.")
        else:
            print(f"{path}: no relevance found.")
        return 0

    # Each site in its extracted dialect unless --dialect forced one, through
    # the same analysis (and cache) `--check` and the lint CLI use.
    reports = [(site, _analyze_site(site, config)) for site in sites]
    findings = [
        lint_analysis(report, config, path=path, base_line=site.line, site=site)
        for site, report in reports
    ]
    if output == "json":
        emit_json(
            {
                "file": _path(path),
                "sites": [
                    {
                        "kind": site.kind,
                        "line": site.line,
                        "context": site.context,
                        "site_dialect": site.dialect.value,
                        "analysis": report.to_dict(mermaid=mermaid),
                        "findings": [finding.to_dict() for finding in site_findings],
                    }
                    for (site, report), site_findings in zip(reports, findings, strict=True)
                ],
            }
        )
    elif output == "text":
        style = Style.for_stream(sys.stdout)
        print(style.bold(f"{path}: {len(sites)} relevance site(s) found."))
        total = len(sites)
        paired = enumerate(zip(reports, findings, strict=True), 1)
        for index, ((site, report), site_findings) in paired:
            heading = f"Site {index} of {total}: {_site_heading(site)}"
            print()
            print(
                render_text(
                    report,
                    site_findings,
                    config,
                    style,
                    heading=heading,
                    verbose=verbose,
                    mermaid=mermaid,
                ),
                end="",
            )
        if total > 1:
            every = tuple(finding for site_findings in findings for finding in site_findings)
            print()
            print(style.bold(f"All {total} sites: ") + verdict_line(every, style))
    else:
        print(f"# Relevance Analysis: {path}\n")
        print(f"{len(sites)} relevance site(s) found.\n")
        paired = enumerate(zip(reports, findings, strict=True), 1)
        for index, ((site, report), site_findings) in paired:
            heading = f"Site {index}: {_site_heading(site)}"
            print(
                render(
                    report,
                    level=2,
                    heading=heading,
                    mermaid=mermaid,
                    findings=site_findings,
                    verbose=verbose,
                )
            )
    return (
        0 if _passed(counts(tuple(f for site_findings in findings for f in site_findings))) else 1
    )


def _run_reference(slug: str, *, brief: bool, as_json: bool) -> int:
    """Print one language reference document.

    ``--reference client`` is spelled the way the ``--dialect`` flag is rather
    than as the document's own slug, because a caller already knows the dialect
    names from every other flag here; the slug is translated rather than made
    the user's problem. ``universal`` translates the same way, to
    ``universal-relevance``; only ``dialects`` is already its own slug.
    Imported inside the function for the same reason the package does not import
    :mod:`~bigfix_relevance_analyzer.reference` at all: nothing pays for a
    document it did not ask for.
    """
    from bigfix_relevance_analyzer import reference

    document = reference.get_document(slug if slug == "dialects" else f"{slug}-relevance")
    detail = reference.Detail.BRIEF if brief else reference.Detail.STANDARD
    if as_json:
        emit_json(document.to_dict(detail=detail))
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
        emit_json({"query": query, "results": [result.to_dict() for result in results]})
        return 0

    if not results:
        print(f"# Inspector search: {query}\n\nNothing matched.")
        return 0

    print(f"# Inspector search: {query}\n")
    rows = [
        (
            result.match.value,
            _cell(result.name),
            _cell(result.matched),
            str(len(result.inspectors)),
            capped(code_cell(name) for name in result.return_types),
        )
        for result in results
    ]
    print(table(("Match", "Name", "Found via", "Overloads", "Returns"), rows))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, analyse, print. Returns a process exit status."""
    arguments = sys.argv[1:] if argv is None else list(argv)
    if "--check" in arguments:
        # Linting has one implementation: `bigfix-relevance-lint`'s. Every
        # other argument is handed to it untouched, so `--check` takes all of
        # that command's flags and can never drift from it.
        from bigfix_relevance_analyzer import _lint_cli

        arguments.remove("--check")
        return _lint_cli.main(arguments, prog=f"{_prog()} --check")
    parser = argparse.ArgumentParser(
        prog=_prog(),
        description=(
            "Analyse one BigFix Relevance statement: dialect, parse, types, "
            "platforms, bindings, breakdown probes, complexity. Prints a "
            "compact summary plus any issues found (parse errors, unbound `it`, "
            "type errors, unknown inspectors, complexity/evaluation cost past a "
            "default ceiling); --verbose adds every other section. Given a path "
            "to an existing file instead, extract and analyse every relevance "
            "site in it."
        ),
    )
    parser.add_argument(
        "relevance",
        nargs="*",
        help="the statement, or a file path; omit to read stdin",
    )
    add_scope_args(
        parser,
        dialect_help="force the dialect instead of classifying it (or trusting extraction)",
        platform_help="narrow client lookups to one platform, e.g. windows",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "print every section (lexing, parse tree, platforms, inspectors, "
            "`it` bindings, breakdown probes, complexity) instead of just the "
            "summary and any issues found"
        ),
    )
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help=(
            "add the parse tree as a Mermaid flowchart (verbose: a line per box "
            "and edge); implies --verbose, since that is the only mode with a "
            "parse tree section to add it to"
        ),
    )
    add_format_args(
        parser, json_help="emit the analysis as JSON, for a program, an MCP server or an AI agent"
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print every lint rule, its default severity and what it means, then exit",
    )
    # The pre-1.16 spelling, kept working but unlisted: `--list-rules` is the
    # name `bigfix-relevance-lint` uses, and both commands now share it.
    parser.add_argument("--rules", dest="list_rules", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--reference",
        choices=["client", "session", "dialects", "universal"],
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
    # Never parsed here: `main` hands everything to `bigfix-relevance-lint`
    # first. Declared only so `--help` lists it.
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "lint files (or statements) instead -- exactly `bigfix-relevance-lint`, "
            "with all of its flags; see `--check --help`"
        ),
    )
    add_ceiling_args(
        parser,
        max_score_help=(
            "raise the complexity ceiling above its default "
            f"({DEFAULT_MAX_SCORE:g}); a score over it is always reported"
        ),
        max_evaluation_cost_help=(
            "raise the evaluation-cost ceiling above its default "
            f"({DEFAULT_MAX_EVALUATION_COST:g}); a cost over it is always reported"
        ),
        max_depth_help=None,
    )
    args = parser.parse_args(argv)
    forced = dialect_from_args(args)
    # "Did you mean" candidates cost milliseconds per unknown name -- nothing
    # for the one statement or one file this command analyses.
    config = dataclasses.replace(config_from_args(args), suggest=True)
    output = output_format(args)
    # The parse tree section -- where the flowchart lives -- only renders in
    # verbose mode, so --mermaid without --verbose would otherwise do nothing.
    verbose = args.verbose or args.mermaid

    # Both of these are questions about the language or the tool rather than
    # about a statement, so they are answered before anything else looks at the
    # positional arguments -- and they exit 0 even alongside a broken file.
    if args.list_rules:
        return print_rules(output)

    if args.reference is not None:
        return _run_reference(args.reference, brief=args.brief, as_json=args.json)

    if args.search is not None:
        return _run_search(args.search, forced, as_json=args.json)

    if len(args.relevance) > 1:
        parser.error("only one statement or file is accepted; use --check to lint several")

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
                candidate, config, output=output, mermaid=args.mermaid, verbose=verbose
            )
        text = args.relevance[0].strip()
    else:
        text = sys.stdin.read().strip()

    if not text:
        parser.error("no relevance statement given")

    report = _analyze_text(text, config)
    findings = lint_analysis(report, config)
    if output == "json":
        emit_json(
            {
                **report.to_dict(mermaid=args.mermaid),
                "findings": [finding.to_dict() for finding in findings],
            }
        )
    elif output == "markdown":
        print(render(report, mermaid=args.mermaid, findings=findings, verbose=verbose), end="")
    else:
        style = Style.for_stream(sys.stdout)
        text_report = render_text(
            report, findings, config, style, verbose=verbose, mermaid=args.mermaid
        )
        print(text_report, end="")
    # The same gate `--check` and `bigfix-relevance-lint` exit on: anything at
    # error severity -- a parse failure, but also a type error or an unbound
    # `it` -- fails, so the exit status agrees with the "N errors." it printed.
    return 0 if _passed(counts(findings)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
