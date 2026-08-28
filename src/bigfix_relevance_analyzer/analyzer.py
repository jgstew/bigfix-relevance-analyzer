"""Every analysis this package offers, run over one relevance statement.

The other modules each answer one question -- which dialect is this, does it
parse, what does it evaluate to, where can it run, what does it cost. A
consumer that wants all of them (an editor hover, a pre-commit report, an MCP
server answering "tell me about this relevance") otherwise has to wire them
together itself, in the right order, and know which results are only available
once the statement parses. This module is that wiring, done once.

Nothing here evaluates relevance. Types and platforms come from the inspector
tables, and :attr:`RelevanceAnalysis.levels` is probe *text* for an evaluator
the caller supplies; see :mod:`~bigfix_relevance_analyzer.breakdown`.

It is also print-free, like the rest of the package -- rendering lives in
``__main__``, so importing this inside a stdio MCP server stays safe.

    from bigfix_relevance_analyzer import analyze_relevance

    report = analyze_relevance('exists file "C:\\\\foo.txt"')
    print(report.dialect, report.check.value.plurality if report.check else None)
    print(report.complexity.score)

Analysis never raises on bad input: a statement that does not lex or parse
comes back with :attr:`RelevanceAnalysis.error` set and the tree-dependent
fields empty, because the callers this exists for -- editors, hooks -- are
handed broken text constantly and a half-written statement is the normal case,
not an exceptional one. What *is* still reported for such a statement is
everything that does not need a tree: the dialect, the token stream with its
error tokens positioned, and the complexity metrics, which are lexical.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.binding import ItBinding, resolve_it_bindings
from bigfix_relevance_analyzer.breakdown import Level, ProbeKind, breakdown_probes
from bigfix_relevance_analyzer.complexity import (
    CostRule,
    RelevanceComplexity,
    evaluation_cost_rules,
)
from bigfix_relevance_analyzer.complexity import analyze as analyze_complexity
from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect, is_definite
from bigfix_relevance_analyzer.nodes import Node, Reference, Span, to_mermaid, to_sexpr
from bigfix_relevance_analyzer.parser import ParseError, try_parse
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, tokenize
from bigfix_relevance_analyzer.typecheck import CheckResult, TypeEnvironment, check

__all__ = [
    "ReferenceReport",
    "RelevanceAnalysis",
    "analyze",
]


def _is_node(value: object) -> bool:
    """Whether a field value is a child node.

    A :class:`~bigfix_relevance_analyzer.nodes.Span` is a dataclass too but is
    position, not structure; a dataclass *class* can reach here because
    :func:`dataclasses.is_dataclass` accepts types as well as instances.
    """
    return dataclasses.is_dataclass(value) and not isinstance(value, Span | type)


def _children(node: Node) -> list[Node]:
    """The direct child nodes of ``node``, in field order."""
    found: list[Node] = []
    for field in dataclasses.fields(node):
        value = getattr(node, field.name)
        if isinstance(value, tuple):
            found.extend(cast("Node", item) for item in value if _is_node(item))
        elif _is_node(value):
            found.append(cast("Node", value))
    return found


def _walk(node: Node) -> Iterator[Node]:
    """Every node in the tree, parents before children.

    Iterative for the same reason
    :func:`~bigfix_relevance_analyzer.binding.resolve_it_bindings` is: relevance
    permits trees deeper than CPython's recursion limit, and wild content must
    never be a crash.
    """
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(_children(current))


def _tree_depth(node: Node) -> int:
    """The height of the tree, iteratively."""
    deepest = 0
    stack: list[tuple[Node, int]] = [(node, 1)]
    while stack:
        current, level = stack.pop()
        deepest = max(deepest, level)
        stack.extend((child, level + 1) for child in _children(current))
    return deepest


@dataclass(frozen=True, slots=True)
class ReferenceReport:
    """One name in the statement, and what the inspector tables say about it."""

    reference: Reference
    """The node itself; its :attr:`~bigfix_relevance_analyzer.nodes.Span` is
    where to point a message."""

    matches: tuple[inspectors.Inspector, ...]
    """Every table row with this name, in any dialect or platform."""

    visible: tuple[inspectors.Inspector, ...]
    """The subset of :attr:`matches` the analysed environment can see.

    Empty alongside a non-empty :attr:`matches` means the name is real but not
    reachable as written here -- a session inspector used in client relevance,
    or a Windows one under ``--platform macos``.
    """

    @property
    def phrase(self) -> str:
        """The case-folded, space-normalized name, e.g. ``operating system``."""
        return self.reference.phrase

    @property
    def known(self) -> bool:
        """Whether any dump defines this name at all."""
        return bool(self.matches)

    @property
    def resolved(self) -> tuple[inspectors.Inspector, ...]:
        """What to report: the visible rows, or every row when none are visible.

        Falling back to :attr:`matches` is deliberate. A name that exists but is
        out of scope is a more useful thing to show than nothing, and
        :attr:`known` and :attr:`visible` are what distinguish the two cases.
        """
        return self.visible or self.matches

    @property
    def return_types(self) -> tuple[str, ...]:
        """The distinct types this name can evaluate to, sorted."""
        return tuple(sorted({entry.return_type for entry in self.resolved}))

    @property
    def platforms(self) -> frozenset[str]:
        """Client platforms defining any resolved row. Empty for session-only."""
        found: frozenset[str] = frozenset()
        for entry in self.resolved:
            found |= entry.platforms
        return found


@dataclass(frozen=True, slots=True)
class RelevanceAnalysis:
    """Everything known about one statement. Built by :func:`analyze`."""

    text: str
    """The statement as given, verbatim."""

    classified_dialect: Dialect | None
    """What :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
    concluded, or ``None`` when the text carries no evidence either way."""

    requested_dialect: Dialect | None
    """The dialect the caller forced, if any."""

    environment: TypeEnvironment
    """The dialect and platform every lookup ran against."""

    tokens: tuple[Token, ...]
    """The full token stream, trivia included, so a caller can re-render it."""

    parse_error: ParseError | None
    """Why parsing failed, positioned, or ``None`` when it succeeded."""

    node: Node | None
    """The root of the tree, or ``None`` when :attr:`parse_error` is set."""

    check: CheckResult | None
    """The type-check result, or ``None`` when there is no tree to check."""

    references: tuple[ReferenceReport, ...]
    """One per :class:`~bigfix_relevance_analyzer.nodes.Reference`, in the order
    the walk found them."""

    it_bindings: tuple[ItBinding, ...]
    """Every ``it``, with what it refers to. An entry whose
    :attr:`~bigfix_relevance_analyzer.binding.ItBinding.context` is ``None`` is
    an error the type checker also reports."""

    levels: tuple[Level, ...]
    """Breakdown probes, one per measurable level. Text, not results."""

    complexity: RelevanceComplexity
    """Readability and evaluation-cost metrics. Present even for text that does
    not parse, because they are counted lexically."""

    cost_rules: tuple[CostRule, ...]
    """The heavy-inspector rules this statement matched, in table order."""

    @property
    def dialect(self) -> Dialect:
        """The dialect analysis actually ran as."""
        return self.environment.dialect

    @property
    def resolved_dialect(self) -> Dialect | None:
        """Which dialect every resolved reference's own table facts settle on.

        :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
        runs on raw text, before parsing, and is deliberately blind to common
        English words such as ``file`` -- see its module docstring -- because
        in unparsed text those are too collision-prone to trust. Once the
        statement has parsed, that risk is gone: a :class:`ReferenceReport`'s
        :attr:`~ReferenceReport.matches` are inspector-table rows resolved by
        name, not a guess about a word in prose, so ``files`` or ``folders``
        being client-only is real evidence a text classifier could never use.

        Computed as the intersection, across every reference with at least one
        known match, of the dialects that reference's rows are defined in --
        the same "valid in every dialect this could be" reasoning
        :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
        cannot apply without a parse tree. An unknown name (no match at all)
        contributes no evidence either way.

        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.CLIENT` or
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.SESSION` means every
        resolved reference supports that dialect and not both dialects at
        once. :attr:`~bigfix_relevance_analyzer.dialect.Dialect.BOTH` means
        every resolved reference supports both -- provable here in a way the
        text classifier's own docstring says it cannot be, because a parse
        tree already exists by this point.
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN` means the
        references contradict each other: some resolve only in client
        relevance, others only in session, so this statement cannot be valid
        as either. ``None`` means nothing parsed, or nothing resolved to a
        known name at all.
        """
        if self.node is None:
            return None
        supported: frozenset[Dialect] | None = None
        for reference in self.references:
            found: frozenset[Dialect] = frozenset(
                dialect for entry in reference.matches for dialect in entry.dialects
            )
            if not found:
                continue  # an unknown name, or one with no dialect at all
            supported = found if supported is None else supported & found
        if supported is None:
            return None
        if supported == {Dialect.CLIENT, Dialect.SESSION}:
            return Dialect.BOTH
        if supported == {Dialect.CLIENT}:
            return Dialect.CLIENT
        if supported == {Dialect.SESSION}:
            return Dialect.SESSION
        return Dialect.UNCERTAIN  # empty intersection: genuinely contradictory

    @property
    def dialect_assumed(self) -> bool:
        """Whether :attr:`dialect` is a fallback rather than a finding.

        False when the caller forced a dialect, when the pre-parse text
        classifier reached a verdict, or when :attr:`resolved_dialect` -- the
        reference table's own post-parse evidence -- settles on one specific
        dialect by itself. True only when none of the three determined
        anything, so every dialect-dependent conclusion below is conditional
        on a guess, which a report should say out loud.
        """
        if self.requested_dialect is not None or self.classified_dialect is not None:
            return False
        return not is_definite(self.resolved_dialect)

    @property
    def parsed(self) -> bool:
        """Whether the statement parsed."""
        return self.node is not None

    @property
    def valid(self) -> bool:
        """Whether it parsed *and* the tables found nothing wrong with it.

        Not proof that it runs: the tables are dumps of what some engines
        reported, so a clean result on an inspector no dump covers means
        "nothing contradicts this", not "this is correct".
        """
        return self.node is not None and self.check is not None and self.check.ok

    @property
    def error_tokens(self) -> tuple[Token, ...]:
        """Text the tokenizer could not lex. Non-empty means broken input."""
        return tuple(token for token in self.tokens if token.kind is TokenKind.ERROR)

    @property
    def code_tokens(self) -> tuple[Token, ...]:
        """The tokens that carry meaning: no whitespace, no comments."""
        return tuple(token for token in self.tokens if not token.is_trivia())

    @property
    def token_kinds(self) -> dict[str, int]:
        """How many tokens of each lexical kind, trivia included."""
        counts: dict[str, int] = {}
        for token in self.tokens:
            counts[token.kind.value] = counts.get(token.kind.value, 0) + 1
        return counts

    @property
    def nodes(self) -> tuple[Node, ...]:
        """Every node in the tree, parents first. Empty when it did not parse."""
        return () if self.node is None else tuple(_walk(self.node))

    @property
    def node_kinds(self) -> dict[str, int]:
        """How many nodes of each class, keyed by class name."""
        counts: dict[str, int] = {}
        for item in self.nodes:
            name = type(item).__name__
            counts[name] = counts.get(name, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def tree_depth(self) -> int:
        """The height of the tree; 0 when it did not parse."""
        return 0 if self.node is None else _tree_depth(self.node)

    @property
    def sexpr(self) -> str | None:
        """The tree as an S-expression, the corpus's own notation."""
        return None if self.node is None else to_sexpr(self.node)

    @property
    def mermaid(self) -> str | None:
        """The tree as a Mermaid ``flowchart``, via
        :func:`~bigfix_relevance_analyzer.nodes.to_mermaid` -- a real graph
        of the parsed structure, not a description of one. ``None`` when it
        did not parse.
        """
        return None if self.node is None else to_mermaid(self.node)

    @property
    def platforms(self) -> frozenset[str]:
        """Client platforms the statement as a whole can run on.

        Empty for session relevance, where platform is not an axis, and empty
        when there is no tree to check.
        """
        return frozenset() if self.check is None else self.check.platforms

    @property
    def missing_platforms(self) -> frozenset[str]:
        """Platforms in play that this statement is *not* viable on.

        Reported, never enforced: a platform absent from the dumps has not been
        proven unsupported, only never observed.
        """
        return self.environment.universe - self.platforms

    @property
    def unknown_references(self) -> tuple[str, ...]:
        """Names no dump defines, sorted and de-duplicated.

        The most actionable single signal here for a typo, but not proof of
        one: the dumps do not cover every platform or product version.
        """
        return tuple(sorted({report.phrase for report in self.references if not report.known}))

    @property
    def unbound_its(self) -> tuple[ItBinding, ...]:
        """Occurrences of ``it`` with no context to bind to."""
        return tuple(entry for entry in self.it_bindings if entry.context is None)

    def to_dict(self, *, mermaid: bool = False) -> dict[str, Any]:
        """The whole analysis as JSON-serializable plain data.

        For consumers across a wire -- an MCP server, a report file -- that
        cannot hold the node objects. Lossy by design: nodes become source
        text and S-expressions, enums become their values.

        ``mermaid`` adds the parse tree's flowchart under ``parse.mermaid``.
        Off by default for the same reason the CLI's ``--mermaid`` flag is
        opt-in: a line per box and per edge dwarfs the rest of the payload on
        a real statement, and the S-expression already carries the same tree.
        """
        report: dict[str, Any] = {
            "text": self.text,
            "dialect": {
                "classified": self.classified_dialect.value if self.classified_dialect else None,
                "resolved": self.resolved_dialect.value if self.resolved_dialect else None,
                "requested": self.requested_dialect.value if self.requested_dialect else None,
                "effective": self.dialect.value,
                "assumed": self.dialect_assumed,
            },
            "lexing": {
                "tokens": len(self.tokens),
                "code_tokens": len(self.code_tokens),
                "by_kind": self.token_kinds,
                "errors": [
                    {
                        "text": token.text,
                        "line": token.line,
                        "column": token.column,
                        "offset": token.offset,
                    }
                    for token in self.error_tokens
                ],
            },
            "parse": {
                "ok": self.parsed,
                "error": (
                    None
                    if self.parse_error is None
                    else {
                        "message": self.parse_error.message,
                        "line": self.parse_error.line,
                        "column": self.parse_error.column,
                        "offset": self.parse_error.offset,
                    }
                ),
                "sexpr": self.sexpr,
                **({"mermaid": self.mermaid} if mermaid else {}),
                "node_count": len(self.nodes),
                "tree_depth": self.tree_depth,
                "node_kinds": self.node_kinds,
            },
            "complexity": {
                "score": self.complexity.score,
                "evaluation_cost": self.complexity.evaluation_cost,
                "costly_inspectors": list(self.complexity.costly_inspectors),
                "metrics": {
                    field.name: getattr(self.complexity, field.name)
                    for field in dataclasses.fields(self.complexity)
                },
                "cost_rules": [
                    {
                        "label": rule.label,
                        "cost": rule.cost_for(self.dialect),
                        "why": rule.why,
                    }
                    for rule in self.cost_rules
                ],
            },
        }
        if self.check is not None:
            report["types"] = {
                "types": (
                    None if self.check.value.types is None else sorted(self.check.value.types)
                ),
                "plurality": self.check.value.plurality.value,
                "known": self.check.value.known,
                "ok": self.check.ok,
                "diagnostics": [
                    {
                        "code": diagnostic.code,
                        "message": diagnostic.message,
                        "line": diagnostic.span.line,
                        "column": diagnostic.span.column,
                    }
                    for diagnostic in self.check.diagnostics
                ],
            }
        report["platforms"] = {
            "viable": sorted(self.platforms),
            "universe": sorted(self.environment.universe),
            "missing": sorted(self.missing_platforms),
        }
        report["references"] = [
            {
                "phrase": report_entry.phrase,
                "line": report_entry.reference.span.line,
                "column": report_entry.reference.span.column,
                "known": report_entry.known,
                "visible_here": bool(report_entry.visible),
                "signatures": sorted({entry.signature for entry in report_entry.resolved}),
                "return_types": list(report_entry.return_types),
                "platforms": sorted(report_entry.platforms & self.environment.universe),
            }
            for report_entry in self.references
        ]
        report["unknown_references"] = list(self.unknown_references)
        report["it_bindings"] = [
            {
                "line": entry.it.span.line,
                "column": entry.it.span.column,
                "binder": entry.binder.value if entry.binder else None,
                "context": (
                    None
                    if entry.context is None
                    else self.text[entry.context.span.start : entry.context.span.end]
                ),
                "bound": entry.context is not None,
            }
            for entry in self.it_bindings
        ]
        report["levels"] = [
            {
                "label": level.label,
                "line": level.span.line,
                "column": level.span.column,
                "probe": level.probe.relevance,
                "unfiltered_probe": level.unfiltered.relevance if level.unfiltered else None,
            }
            for level in self.levels
        ]
        return report


def analyze(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    probe_kind: ProbeKind = ProbeKind.COUNT,
) -> RelevanceAnalysis:
    """Run every analysis over ``text`` and return the results together.

    ``dialect`` forces the dialect instead of classifying it -- pass the
    :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.dialect` extraction
    already worked out, rather than having it guessed a second time from a
    fragment out of context. When it is ``None`` and classification is
    undetermined, client is assumed and :attr:`RelevanceAnalysis.dialect_assumed`
    says so.

    ``platform`` narrows client lookups to one platform. Leaving it out keeps
    every platform in play and lets narrowing do the work, which is what makes
    :attr:`RelevanceAnalysis.platforms` meaningful.

    Never raises for bad relevance: see the module docstring.
    """
    classified = classify_relevance_dialect(text)
    effective = dialect or classified or Dialect.CLIENT
    environment = TypeEnvironment.create(effective, platform)

    parsed = try_parse(text)
    node = parsed.node

    references: tuple[ReferenceReport, ...] = ()
    it_bindings: tuple[ItBinding, ...] = ()
    levels: tuple[Level, ...] = ()
    checked: CheckResult | None = None
    if node is not None:
        checked = check(node, environment)
        references = tuple(
            ReferenceReport(
                reference=item,
                matches=(matches := inspectors.lookup(item.phrase)),
                visible=tuple(entry for entry in matches if environment.visible(entry)),
            )
            for item in _walk(node)
            if isinstance(item, Reference)
        )
        it_bindings = resolve_it_bindings(node)
        levels = breakdown_probes(text, node, kind=probe_kind)

    return RelevanceAnalysis(
        text=text,
        classified_dialect=classified,
        requested_dialect=dialect,
        environment=environment,
        tokens=tuple(tokenize(text)),
        parse_error=parsed.error,
        node=node,
        check=checked,
        references=references,
        it_bindings=it_bindings,
        levels=levels,
        complexity=analyze_complexity(text, effective),
        cost_rules=evaluation_cost_rules(text, effective),
    )
