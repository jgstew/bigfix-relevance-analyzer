"""Plain terminal rendering of an analysis: the CLI's default output.

The Markdown report (``__main__.render``, behind ``--markdown``) is for pasting
into an issue or a PR; ``--json`` is for a program. This is for a person at a
terminal: a verdict up front, aligned label/value rows instead of tables, a
caret under a parse error, and a closing line that says plainly whether
anything is wrong -- a clean statement says so instead of leaving it to be
inferred from the absence of an ``Issues`` section.

Colour is decided once, by :func:`Style.for_stream`: only on a terminal, never
when ``NO_COLOR`` is set (https://no-color.org). Every symbol sits next to a
word that carries the same meaning, so nothing is lost without colour, and the
symbols themselves fall back to ASCII when the stream's encoding (a legacy
Windows console, say) cannot represent them.

Rendering only, like ``__main__``: every conclusion comes from the analysis and
the findings passed in.
"""

from __future__ import annotations

import dataclasses
import os
from typing import TextIO

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis
from bigfix_relevance_analyzer.lint import Finding, LintConfig, Severity
from bigfix_relevance_analyzer.typecheck import Plurality, _describe_types

__all__: list[str] = []

_LABEL_WIDTH = 12
_INDENT = "  "


@dataclasses.dataclass(frozen=True)
class Style:
    """How to decorate text for one output stream."""

    color: bool = False
    unicode: bool = True

    @classmethod
    def for_stream(cls, stream: TextIO) -> Style:
        try:
            tty = stream.isatty()
        except (AttributeError, ValueError):
            tty = False
        color = tty and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
        try:
            "\u2713\u2717".encode(stream.encoding or "ascii")
        except (LookupError, UnicodeEncodeError):
            return cls(color=color, unicode=False)
        return cls(color=color, unicode=True)

    def _wrap(self, code: str, text: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if self.color else text

    def bold(self, text: str) -> str:
        return self._wrap("1", text)

    def dim(self, text: str) -> str:
        return self._wrap("2", text)

    def good(self, text: str) -> str:
        return self._wrap("32", text)

    def bad(self, text: str) -> str:
        return self._wrap("31", text)

    def caution(self, text: str) -> str:
        return self._wrap("33", text)

    @property
    def ok_mark(self) -> str:
        return self.good("\u2713" if self.unicode else "OK")

    @property
    def error_mark(self) -> str:
        return self.bad("\u2717" if self.unicode else "x")

    @property
    def warning_mark(self) -> str:
        return self.caution("!")


def _row(label: str, value: str, style: Style) -> str:
    return f"{_INDENT}{style.dim(label.ljust(_LABEL_WIDTH))}  {value}"


def _continuation(value: str) -> str:
    return f"{_INDENT}{' ' * _LABEL_WIDTH}  {value}"


def _severity_count(findings: tuple[Finding, ...], severity: Severity) -> int:
    return sum(1 for finding in findings if finding.severity is severity)


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


def _status(report: RelevanceAnalysis, findings: tuple[Finding, ...], style: Style) -> str:
    dialect = f"{report.dialect.value} relevance"
    if report.dialect_assumed:
        dialect += style.dim(" (dialect assumed: nothing in the statement settles it)")
    errors = _severity_count(findings, Severity.ERROR)
    warnings = _severity_count(findings, Severity.WARNING)
    if errors:
        verdict = f"{style.error_mark} {style.bad(style.bold('Problems found'))}"
    elif warnings:
        verdict = f"{style.warning_mark} {style.caution(style.bold('Parses, with warnings'))}"
    else:
        verdict = f"{style.ok_mark} {style.good(style.bold('OK'))}"
    return f"{_INDENT}{verdict}  {style.dim('-')}  {dialect}"


def _returns(report: RelevanceAnalysis) -> str | None:
    if report.check is None:
        return None
    types = report.check.value.types
    plurality = report.check.value.plurality
    rendered = _describe_types(types)
    if types and plurality is not Plurality.UNKNOWN:
        rendered = f"{plurality.value} {rendered}"
    return rendered


def _ceiling(value: float, limit: float | None, style: Style) -> str:
    """``value``, in red past ``limit``. The limit itself is not printed: past
    it, the ``complexity``/``evaluation-cost`` issue already says so, and under
    it the number means nothing to a reader."""
    text = f"{value:.3g}"
    return style.bad(text) if limit is not None and value > limit else text


def _summary(
    report: RelevanceAnalysis,
    findings: tuple[Finding, ...],
    config: LintConfig,
    style: Style,
) -> list[str]:
    lines = [_status(report, findings, style)]
    if report.parsed:
        returns = _returns(report)
        if returns is not None:
            lines.append(_row("Returns", returns, style))
        viable = sorted(report.platforms)
        missing = sorted(report.missing_platforms)
        lines.append(_row("Platforms", ", ".join(viable) or style.bad("none"), style))
        if missing and viable:
            lines.append(_continuation(style.dim(f"not available: {', '.join(missing)}")))
        lines += _inspector_rows(report, style)
        lines += _binding_rows(report, style)
        lines.append(_row("Structure", _structure(report, style), style))
    metrics = report.complexity
    lines.append(_row("Complexity", _ceiling(metrics.score, config.max_score, style), style))
    if metrics.evaluation_cost:
        cost = _ceiling(metrics.evaluation_cost, config.max_evaluation_cost, style)
        lines.append(_row("Eval cost", cost, style))
    return lines


_STRUCTURE_WIDTH = 100
"""Where the one-line S-expression is cut; ``--verbose`` always prints it whole."""


def _structure(report: RelevanceAnalysis, style: Style) -> str:
    assert report.sexpr is not None
    sexpr = report.sexpr
    size = f"{len(report.nodes)} nodes, depth {report.tree_depth}"
    if len(sexpr) > _STRUCTURE_WIDTH:
        sexpr = sexpr[: _STRUCTURE_WIDTH - 3] + "..."
        size += "; --verbose for all of it"
    return f"{sexpr} {style.dim(f'({size})')}"


def _inspector_rows(report: RelevanceAnalysis, style: Style) -> list[str]:
    """One ``name -> returns`` per distinct inspector, in the order they appear.

    The compact form of ``--verbose``'s Inspectors section, like the web
    playground's references table: what each name resolved to is usually the
    first thing to check when a result type surprises. An unknown name is
    marked here as well as reported under Issues.
    """
    seen: dict[str, str] = {}
    for entry in report.references:
        if entry.phrase in seen:
            continue
        if not entry.known:
            seen[entry.phrase] = style.bad("unknown")
        else:
            seen[entry.phrase] = ", ".join(entry.return_types) or "?"
    if not seen:
        return []
    width = max(len(phrase) for phrase in seen)
    rows = [f"{phrase.ljust(width)}  -> {returns}" for phrase, returns in seen.items()]
    return [_row("Inspectors", rows[0], style), *(_continuation(row) for row in rows[1:])]


def _binding_rows(report: RelevanceAnalysis, style: Style) -> list[str]:
    """What each ``it`` refers to, grouped: ``it -> operating systems (of, 2 uses)``."""
    if not report.it_bindings:
        return []
    groups: dict[tuple[str, str], int] = {}
    for entry in report.it_bindings:
        if entry.context is None:
            key = ("?", style.bad("UNBOUND - used with no context"))
        else:
            text = report.text[entry.context.span.start : entry.context.span.end]
            key = (entry.binder.value if entry.binder else "?", " ".join(text.split()))
        groups[key] = groups.get(key, 0) + 1
    rows = []
    for (binder, context), uses in groups.items():
        detail = f"{binder}, {_plural(uses, 'use')}" if binder != "?" else _plural(uses, "use")
        rows.append(f"{context} {style.dim(f'({detail})')}")
    return [_row("it", rows[0], style), *(_continuation(row) for row in rows[1:])]


def _caret(report: RelevanceAnalysis, line: int, column: int, style: Style) -> list[str]:
    """The offending source line with a ``^`` under ``column`` (both 1-based)."""
    source = report.text.splitlines() or [""]
    if not 1 <= line <= len(source):
        return []
    text = source[line - 1].expandtabs(1)
    pad = " " * max(column - 1, 0)
    return [f"{_INDENT * 3}{text}", f"{_INDENT * 3}{pad}{style.bad('^')}"]


def _issues(report: RelevanceAnalysis, findings: tuple[Finding, ...], style: Style) -> list[str]:
    if not findings:
        return []
    lines = ["", style.bold("Issues")]
    for finding in findings:
        if finding.severity is Severity.ERROR:
            mark, label = style.error_mark, style.bad("error  ")
        else:
            mark, label = style.warning_mark, style.caution("warning")
        where = f"line {finding.line}"
        lines.append(
            f"{_INDENT}{mark} {label} {style.dim(f'[{finding.code}]')} {where}: {finding.message}"
        )
        if finding.code == "parse-error" and report.parse_error is not None:
            error = report.parse_error
            lines.extend(_caret(report, error.line, error.column, style))
    return lines


def _autofix(report: RelevanceAnalysis, findings: tuple[Finding, ...], style: Style) -> list[str]:
    """The statement with every safe fix applied -- see ``__main__._render_autofix``."""
    fixed = next((finding.autofix for finding in findings if finding.autofix), None)
    if fixed is None:
        fixed = report.autofix()
    if not fixed.changed:
        return []
    lines = ["", style.bold("Suggested fix"), f"{_INDENT}{style.good(fixed.fixed)}"]
    rounds = _plural(fixed.rounds, "round")
    for entry in fixed.to_dict()["applied"]:
        lines.append(
            style.dim(
                f"{_INDENT}applied {entry['count']} {entry['code']} ({entry['rule']}) over {rounds}"
            )
        )
    for entry in fixed.to_dict()["unapplied"]:
        lines.append(
            style.dim(f"{_INDENT}left {entry['count']} {entry['code']} ({entry['rule']}) unfixed")
        )
    return lines


def _section(title: str, style: Style) -> list[str]:
    return ["", style.bold(title)]


def _verbose(report: RelevanceAnalysis, style: Style, *, mermaid: bool) -> list[str]:
    lines = _section("Tokens", style)
    lines.append(
        f"{_INDENT}{len(report.code_tokens)} code tokens of {len(report.tokens)} total: "
        + ", ".join(f"{kind} {count}" for kind, count in report.token_kinds.items())
    )
    for token in report.error_tokens:
        lines.append(
            f"{_INDENT}{style.error_mark} error token {token.text!r} "
            f"at line {token.line}, col {token.column}"
        )
    if report.parsed:
        assert report.sexpr is not None
        lines += _section("Parse tree", style)
        lines.append(
            f"{_INDENT}{len(report.nodes)} nodes, depth {report.tree_depth}: "
            + ", ".join(f"{kind} {count}" for kind, count in report.node_kinds.items())
        )
        lines.append(f"{_INDENT}{report.sexpr}")
        if mermaid:
            assert report.mermaid is not None
            lines += _section("Mermaid", style)
            lines.extend(f"{_INDENT}{line}" for line in report.mermaid.splitlines())
        lines += _inspectors(report, style)
        lines += _bindings(report, style)
        lines += _probes(report, style)
    lines += _metrics(report, style)
    return lines


def _inspectors(report: RelevanceAnalysis, style: Style) -> list[str]:
    lines = _section("Inspectors", style)
    if not report.references:
        lines.append(f"{_INDENT}none")
        return lines
    width = max(len(entry.phrase) for entry in report.references)
    for entry in report.references:
        if entry.visible:
            status = f"{style.ok_mark} ok     "
        elif entry.known:
            status = f"{style.warning_mark} hidden "
        else:
            status = f"{style.error_mark} unknown"
        returns = ", ".join(entry.return_types) or "-"
        lines.append(f"{_INDENT}{status}  {entry.phrase.ljust(width)}  -> {returns}")
    return lines


def _bindings(report: RelevanceAnalysis, style: Style) -> list[str]:
    if not report.it_bindings:
        return []
    lines = _section("`it` bindings", style)
    for entry in report.it_bindings:
        where = f"{entry.it.span.line}:{entry.it.span.column}"
        if entry.context is None:
            lines.append(f"{_INDENT}{where}  {style.bad('UNBOUND')} - used with no context")
            continue
        context = " ".join(report.text[entry.context.span.start : entry.context.span.end].split())
        binder = entry.binder.value if entry.binder else "?"
        lines.append(f"{_INDENT}{where}  {binder:<6} {context}")
    return lines


def _probes(report: RelevanceAnalysis, style: Style) -> list[str]:
    if not report.levels:
        return []
    lines = _section("Breakdown probes", style)
    for index, level in enumerate(report.levels, 1):
        lines.append(f"{_INDENT}{index}. {style.bold(level.label)}")
        lines.append(f"{_INDENT}   {style.dim(level.probe.relevance)}")
        if level.unfiltered is not None:
            lines.append(f"{_INDENT}   {style.dim('unfiltered: ' + level.unfiltered.relevance)}")
    return lines


def _metrics(report: RelevanceAnalysis, style: Style) -> list[str]:
    metrics = report.complexity
    lines = _section("Complexity", style)
    nonzero = [
        (field.name, getattr(metrics, field.name))
        for field in dataclasses.fields(metrics)
        if field.name not in {"evaluation_cost", "costly_inspectors"}
        and getattr(metrics, field.name)
    ]
    width = max((len(name) for name, _value in nonzero), default=0)
    lines.extend(f"{_INDENT}{name.ljust(width)}  {value}" for name, value in nonzero)
    for rule in report.cost_rules:
        cost = rule.cost_for(report.dialect)
        lines.append(f"{_INDENT}+{cost:.3g} {rule.label}: {rule.why}")
    return lines


def verdict_line(findings: tuple[Finding, ...], style: Style) -> str:
    """The closing line: ``No issues found.`` or the error/warning tally."""
    errors = _severity_count(findings, Severity.ERROR)
    warnings = _severity_count(findings, Severity.WARNING)
    if not errors and not warnings:
        return style.good("No issues found.")
    parts = []
    if errors:
        parts.append(style.bad(_plural(errors, "error")))
    if warnings:
        parts.append(style.caution(_plural(warnings, "warning")))
    return ", ".join(parts) + "."


def render_text(
    report: RelevanceAnalysis,
    findings: tuple[Finding, ...],
    config: LintConfig,
    style: Style,
    *,
    heading: str | None = None,
    verbose: bool = False,
    mermaid: bool = False,
) -> str:
    """One statement's report as terminal text. Returns it; prints nothing.

    ``heading``, when given (a site extracted from a file), is printed above
    the statement. ``verbose`` adds every other section the Markdown report's
    ``--verbose`` has, as plain indented text; ``mermaid`` adds the flowchart
    source to it.
    """
    lines = []
    if heading is not None:
        lines.append(style.bold(heading))
    lines.append(style.bold(report.text) if "\n" not in report.text else report.text)
    lines.append("")
    lines += _summary(report, findings, config, style)
    lines += _issues(report, findings, style)
    lines += _autofix(report, findings, style)
    if verbose:
        lines += _verbose(report, style, mermaid=mermaid)
    lines += ["", verdict_line(findings, style)]
    return "\n".join(lines) + "\n"
