"""bigfix-relevance-analyzer: work with BigFix Relevance generically (extract, analyze, etc.)."""

import logging
from importlib.metadata import PackageNotFoundError, version

from bigfix_relevance_analyzer.analyzer import ReferenceReport, RelevanceAnalysis
from bigfix_relevance_analyzer.analyzer import analyze as analyze_relevance
from bigfix_relevance_analyzer.analyzer import analyze_to_dict as analyze_relevance_to_dict
from bigfix_relevance_analyzer.binding import Binder, ItBinding, resolve_it_bindings
from bigfix_relevance_analyzer.breakdown import (
    Level,
    Outcome,
    Probe,
    ProbeKind,
    ProbeOutcome,
    breakdown_probes,
    interpret_count_results,
)
from bigfix_relevance_analyzer.complexity import (
    COST_RULES,
    CostRule,
    RelevanceComplexity,
)
from bigfix_relevance_analyzer.complexity import analyze as analyze_relevance_complexity
from bigfix_relevance_analyzer.complexity import score as score_relevance_complexity
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS, Diagnostic, Origin
from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect, is_definite
from bigfix_relevance_analyzer.extract import (
    HtmlContext,
    RelevanceSite,
    SiteKind,
    extract_relevance_from_actionscript,
    extract_relevance_from_bes_xml,
    extract_relevance_from_file,
    extract_relevance_from_html_text,
    extract_relevance_from_markdown,
    looks_like_clientui,
)
from bigfix_relevance_analyzer.inspectors import (
    Inspector,
    InspectorKind,
    RelevanceType,
    all_inspectors,
    ancestors,
    inspector_names,
    known_types,
    lookup,
    relevance_types,
)
from bigfix_relevance_analyzer.lint import (
    RULES,
    Finding,
    LintConfig,
    LintRule,
    Severity,
    lint_analysis,
    lint_directory,
    lint_file,
    lint_paths,
    lint_paths_to_dict,
    rules,
)
from bigfix_relevance_analyzer.nodes import to_mermaid, to_sexpr
from bigfix_relevance_analyzer.parser import MAX_PARSE_DEPTH, ParseError, ParseResult
from bigfix_relevance_analyzer.parser import parse as parse_relevance
from bigfix_relevance_analyzer.parser import try_parse as try_parse_relevance
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, code_tokens, tokenize
from bigfix_relevance_analyzer.typecheck import (
    CheckResult,
    Plurality,
    TypeEnvironment,
)
from bigfix_relevance_analyzer.typecheck import (
    check as check_types,
)

try:
    __version__ = version("bigfix-relevance-analyzer")
except PackageNotFoundError:  # pragma: no cover - only hit for an uninstalled checkout
    __version__ = "0.0.0"

# A library must not configure logging on its consumer's behalf. This handler
# only keeps Python quiet when a consumer has configured nothing at all; what
# gets emitted, and where, stays entirely theirs to decide. Nothing in this
# package writes to stdout, so it is safe to import inside a stdio MCP server.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# `reference` is deliberately NOT imported here. It is the only submodule whose
# work is measured in kilobytes of text rather than microseconds, and a stdio
# MCP server that never serves a document should not pay for one at import. Same
# reasoning as `inspectors`' own note: reach it with an explicit
# `from bigfix_relevance_analyzer import reference`.

__all__ = [
    "COST_RULES",
    "DIAGNOSTICS",
    "MAX_PARSE_DEPTH",
    "RULES",
    "Binder",
    "CheckResult",
    "CostRule",
    "Diagnostic",
    "Dialect",
    "Finding",
    "HtmlContext",
    "Inspector",
    "InspectorKind",
    "ItBinding",
    "Level",
    "LintConfig",
    "LintRule",
    "Origin",
    "Outcome",
    "ParseError",
    "ParseResult",
    "Plurality",
    "Probe",
    "ProbeKind",
    "ProbeOutcome",
    "ReferenceReport",
    "RelevanceAnalysis",
    "RelevanceComplexity",
    "RelevanceSite",
    "RelevanceType",
    "Severity",
    "SiteKind",
    "Token",
    "TokenKind",
    "TypeEnvironment",
    "__version__",
    "all_inspectors",
    "analyze_relevance",
    "analyze_relevance_complexity",
    "analyze_relevance_to_dict",
    "ancestors",
    "breakdown_probes",
    "check_types",
    "classify_relevance_dialect",
    "code_tokens",
    "extract_relevance_from_actionscript",
    "extract_relevance_from_bes_xml",
    "extract_relevance_from_file",
    "extract_relevance_from_html_text",
    "extract_relevance_from_markdown",
    "inspector_names",
    "interpret_count_results",
    "is_definite",
    "known_types",
    "lint_analysis",
    "lint_directory",
    "lint_file",
    "lint_paths",
    "lint_paths_to_dict",
    "looks_like_clientui",
    "lookup",
    "parse_relevance",
    "relevance_types",
    "resolve_it_bindings",
    "rules",
    "score_relevance_complexity",
    "to_mermaid",
    "to_sexpr",
    "tokenize",
    "try_parse_relevance",
]
