"""bigfix-relevance-analyzer: work with BigFix Relevance generically (extract, analyze, etc.)."""

import logging
from importlib.metadata import PackageNotFoundError, version

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
from bigfix_relevance_analyzer.complexity import RelevanceComplexity
from bigfix_relevance_analyzer.complexity import analyze as analyze_relevance_complexity
from bigfix_relevance_analyzer.complexity import score as score_relevance_complexity
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
from bigfix_relevance_analyzer.nodes import to_sexpr
from bigfix_relevance_analyzer.parser import ParseError, ParseResult
from bigfix_relevance_analyzer.parser import parse as parse_relevance
from bigfix_relevance_analyzer.parser import try_parse as try_parse_relevance

try:
    __version__ = version("bigfix-relevance-analyzer")
except PackageNotFoundError:  # pragma: no cover - only hit for an uninstalled checkout
    __version__ = "0.0.0"

# A library must not configure logging on its consumer's behalf. This handler
# only keeps Python quiet when a consumer has configured nothing at all; what
# gets emitted, and where, stays entirely theirs to decide. Nothing in this
# package writes to stdout, so it is safe to import inside a stdio MCP server.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "Binder",
    "Dialect",
    "HtmlContext",
    "ItBinding",
    "Level",
    "Outcome",
    "ParseError",
    "ParseResult",
    "Probe",
    "ProbeKind",
    "ProbeOutcome",
    "RelevanceComplexity",
    "RelevanceSite",
    "SiteKind",
    "__version__",
    "analyze_relevance_complexity",
    "breakdown_probes",
    "classify_relevance_dialect",
    "extract_relevance_from_actionscript",
    "extract_relevance_from_bes_xml",
    "extract_relevance_from_file",
    "extract_relevance_from_html_text",
    "extract_relevance_from_markdown",
    "interpret_count_results",
    "is_definite",
    "looks_like_clientui",
    "parse_relevance",
    "resolve_it_bindings",
    "score_relevance_complexity",
    "to_sexpr",
    "try_parse_relevance",
]
