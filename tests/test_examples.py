"""Corpus tests: run the extractor over every file in `tests/examples/`.

`EXPECTED` is the assertion. Each entry lists, in document order, the
`(kind, dialect, line)` of every relevance site the extractor must find in
that file. Line numbers are 1-based lines of the file itself and were derived
by reading the examples, not by recording the implementation's output.

`text_prefixes` pins the first few characters of each site's text so a site
cannot silently match the wrong statement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import extract_relevance_from_file

EXAMPLES = Path(__file__).parent / "examples"

CLIENT = Dialect.CLIENT
SESSION = Dialect.SESSION
UNCERTAIN = Dialect.UNCERTAIN

REL = "relevance"
PROP = "analysis-property"
SUB = "actionscript-substitution"
PI = "relevance-pi"
JS = "javascript-call"
PLAIN = "plain-text"
MD = "markdown-codeblock"

# Only to keep the longest example paths inside the line limit.
DYNAMIC_JS = "session_relevance/dynamic_javascript"


@dataclass(frozen=True)
class Expected:
    """Expected extraction result for one example file."""

    sites: tuple[tuple[str, Dialect, int], ...]
    text_prefixes: tuple[str, ...] = ()
    note: str = ""


EXPECTED: dict[str, Expected] = {
    # ---------------- client relevance: fixlets / tasks ----------------
    "client_relevance/fixlets/fixlet_multi_clause_relevance.bes": Expected(
        sites=((REL, CLIENT, 6), (REL, CLIENT, 7)),
        text_prefixes=("windows of operating system", "not exists files"),
        note="ActionScript has no {...} substitutions.",
    ),
    "client_relevance/fixlets/fixlet_registry_and_active_directory_relevance.bes": Expected(
        sites=(
            (REL, CLIENT, 6),
            (REL, CLIENT, 7),
            (REL, CLIENT, 8),
            (REL, CLIENT, 9),
            (SUB, CLIENT, 31),
        ),
        text_prefixes=(
            "windows of operating system",
            "exists dns domainnames",
            "exists (it as trimmed string)",
            "not exists (it as trimmed string)",
            "concatenations",
        ),
    ),
    "client_relevance/tasks/task_time_based_relevance.bes": Expected(
        sites=((REL, CLIENT, 6), (REL, CLIENT, 7), (SUB, CLIENT, 28), (SUB, CLIENT, 28)),
        text_prefixes=(
            "unix of operating system",
            "not exists files",
            "(concatenations",
            "if windows of operating system",
        ),
        note="Two substitutions on the same ActionScript line.",
    ),
    # ---------------- client relevance: analyses ----------------
    "client_relevance/analyses/analysis_relevance_simple_property.bes": Expected(
        sites=((REL, CLIENT, 6), (PROP, CLIENT, 14)),
    ),
    "client_relevance/analyses/analysis_relevance_complex_property.bes": Expected(
        sites=((REL, CLIENT, 6), (PROP, CLIENT, 14)),
        text_prefixes=("exists smbios", "unique values of"),
    ),
    # ---------------- client relevance: baselines ----------------
    "client_relevance/baselines/baseline_relevance_with_components.bes": Expected(
        sites=(
            (REL, CLIENT, 6),
            (REL, CLIENT, 7),
            (REL, CLIENT, 8),
            (SUB, CLIENT, 25),
            (SUB, CLIENT, 29),
            (REL, CLIENT, 34),
            (SUB, CLIENT, 40),
            (SUB, CLIENT, 45),
            (REL, CLIENT, 50),
        ),
        note=(
            "Both <SuccessCriteria> here are RunToCompletion/OriginalRelevance, "
            "not CustomRelevance, so neither is a relevance site."
        ),
    ),
    # ---------------- client relevance: computer groups ----------------
    "client_relevance/computer_groups/computer_group_manual_relevance.bes": Expected(
        sites=((REL, CLIENT, 8),),
        text_prefixes=("(unix of operating system)",),
    ),
    "client_relevance/computer_groups/computer_group_automatic_relevance.bes": Expected(
        sites=((REL, CLIENT, 8),),
        text_prefixes=("exists (",),
    ),
    # ---------------- client relevance: ClientUI dashboards ----------------
    # ClientUI dashboards are HTML rendered by the BES Client on the endpoint.
    # They use the same <?Relevance ?> syntax as console dashboards but hold
    # CLIENT relevance -- the one case where HTML relevance is not session
    # relevance. A ClientUI cannot evaluate relevance from JavaScript, so the
    # presence of a static PI (and absence of any JS call) is the signal.
    "client_relevance/clientui/clientui_dashboard_client_relevance_substitution.html": Expected(
        sites=(
            (PI, CLIENT, 27),
            (PI, CLIENT, 28),
            (PI, CLIENT, 31),
            (PI, CLIENT, 67),
            (PI, CLIENT, 68),
            (PI, CLIENT, 69),
        ),
        text_prefixes=(
            "number of relevant fixlets",
            "uls of html concatenations",
            'html tags "details"',
            "now as universal string",
            "free space of drives",
            "total space of drives",
        ),
        note=(
            "Uses `relevant fixlets ... of sites` and `relevant offer actions of sites` "
            "-- client-valid inspectors that a naive session-marker heuristic would "
            "misread as session relevance."
        ),
    ),
    "client_relevance/clientui/clientui_dashboard_no_product_meta.html": Expected(
        sites=((PI, CLIENT, 11),),
        text_prefixes=("ps of bs of (it as string) of now",),
        note=(
            "Has none of the corroborating ClientUI markers (no "
            'product="CustomDashboardClientUI" meta, no cid:load link), so it pins '
            "that classification rests on the mechanism, not on those markers."
        ),
    ),
    # ---------------- client relevance: plain text / markdown ----------------
    "client_relevance/plain_text/client_relevance_plain_text.rel": Expected(
        sites=((PLAIN, UNCERTAIN, 1),),
        text_prefixes=("windows of operating system AND",),
        note=".rel carries no context signal; the future content classifier resolves it.",
    ),
    "client_relevance/markdown_codeblocks/client_relevance_markdown_codeblock.md": Expected(
        sites=((MD, UNCERTAIN, 6),),
        text_prefixes=("unique values of strings",),
        note="A markdown fence carries no context signal, so UNCERTAIN despite the folder.",
    ),
    # ---------------- session relevance: dashboards ----------------
    "session_relevance/dashboards/dashboard_session_relevance_html_table.ojo": Expected(
        sites=((PI, SESSION, 16), (PI, SESSION, 17), (PI, SESSION, 18), (PI, SESSION, 25)),
    ),
    "session_relevance/dashboards/dashboard_session_relevance_chart.ojo": Expected(
        sites=((PI, SESSION, 20),),
    ),
    # ---------------- session relevance: web reports ----------------
    "session_relevance/webreports/webreport_session_relevance_basic.besrpt": Expected(
        sites=((PI, SESSION, 3),),
        text_prefixes=('("There are "',),
    ),
    "session_relevance/webreports/webreport_session_relevance_chart.besrpt": Expected(
        sites=((PI, SESSION, 40),),
    ),
    # ---------------- session relevance: dynamic JavaScript ----------------
    f"{DYNAMIC_JS}/dashboard_relevance_via_javascript_static_and_dynamic.ojo": (
        Expected(
            sites=((PI, SESSION, 19), (JS, SESSION, 24)),
            text_prefixes=("ps of concatenations", "tables of tbodys"),
        )
    ),
    f"{DYNAMIC_JS}/dashboard_relevance_via_javascript_interactive.ojo": Expected(
        sites=(),
        note=(
            "Both calls take a variable, not a string literal "
            "(Relevance(relevance, callbackObj) / EvaluateRelevance(relevance)), so neither "
            "is an extractable statement."
        ),
    ),
    f"{DYNAMIC_JS}/webreport_relevance_via_javascript.besrpt": Expected(
        sites=((PI, SESSION, 18), (PI, SESSION, 20), (PI, SESSION, 21)),
        note=(
            "The EvaluateRelevance( on line 44 concatenates a variable "
            "(... + SessionRelevanceQuery), so it is skipped."
        ),
    ),
    f"{DYNAMIC_JS}/fixlet_description_relevance_via_javascript.bes": Expected(
        sites=(
            # Session relevance: Relevance('...') calls in the <Description> HTML.
            (JS, SESSION, 13),
            (JS, SESSION, 14),
            (JS, SESSION, 15),
            (JS, SESSION, 16),
            (JS, SESSION, 17),
            (JS, SESSION, 18),
            (JS, SESSION, 18),
            (JS, SESSION, 18),
            (JS, SESSION, 24),
            (JS, SESSION, 24),
            (JS, SESSION, 24),
            (JS, SESSION, 24),
            (JS, SESSION, 24),
            (JS, SESSION, 24),
            # Client relevance: the Fixlet's own applicability.
            (REL, CLIENT, 30),
            (REL, CLIENT, 31),
            (REL, CLIENT, 32),
            (REL, CLIENT, 33),
            # Client relevance: ActionScript substitutions. Several lines carry
            # many of them -- a curl command line alone accounts for eight.
            # The embedded BES document on line 105 sits inside a
            # `createfile until END_OF_FILE` heredoc, so its braces are
            # deliberately NOT extracted.
            (SUB, CLIENT, 55),
            (SUB, CLIENT, 56),
            (SUB, CLIENT, 57),
            (SUB, CLIENT, 58),
            *((SUB, CLIENT, 85),) * 2,
            *((SUB, CLIENT, 88),) * 3,
            (SUB, CLIENT, 92),
            *((SUB, CLIENT, 95),) * 8,
            (SUB, CLIENT, 112),
            *((SUB, CLIENT, 114),) * 9,
            (SUB, CLIENT, 119),
        ),
        note="Mixed context: client applicability plus dynamic session relevance in JS.",
    ),
    # ---------------- session relevance: plain text / markdown ----------------
    "session_relevance/plain_text/session_relevance_plain_text.bsr": Expected(
        sites=((PLAIN, SESSION, 1),),
        text_prefixes=("(id of site of it",),
    ),
    "session_relevance/markdown_codeblocks/session_relevance_markdown_codeblock.md": Expected(
        sites=((MD, UNCERTAIN, 8),),
        note="A markdown fence carries no context signal, so UNCERTAIN despite the folder.",
    ),
    # ---------------- mixed context ----------------
    "mixed_context/task_with_client_and_session_relevance.bes": Expected(
        sites=((PI, SESSION, 7), (REL, CLIENT, 9)),
        text_prefixes=("names of current fixlets", "NOT in proxy agent context"),
        note="One file, both dialects: a session PI in the Description, client applicability.",
    ),
}


def corpus_files() -> list[Path]:
    return sorted(
        path
        for path in EXAMPLES.rglob("*")
        if path.is_file()
        and path.name != "README.md"
        # Raw inspector-name dumps for the analyzer's property tables, not
        # documents with embedded relevance to extract - see
        # relevance_properties/README.md.
        and "relevance_properties" not in path.relative_to(EXAMPLES).parts
    )


def test_every_example_file_has_an_expectation() -> None:
    """A new example file must come with an expectation, not be silently ignored."""
    found = {path.relative_to(EXAMPLES).as_posix() for path in corpus_files()}
    assert found == set(EXPECTED), {
        "missing_expectation": sorted(found - set(EXPECTED)),
        "expectation_without_file": sorted(set(EXPECTED) - found),
    }


@pytest.mark.parametrize("relative_path", sorted(EXPECTED))
def test_example_extraction(relative_path: str) -> None:
    expected = EXPECTED[relative_path]
    sites = extract_relevance_from_file(EXAMPLES / relative_path)

    assert [(site.kind, site.dialect, site.line) for site in sites] == list(expected.sites)

    for site, prefix in zip(sites, expected.text_prefixes, strict=False):
        assert site.text.startswith(prefix), (site.line, site.text[:80])

    for site in sites:
        assert site.text.strip() == site.text, "site text must be stripped"
        assert site.text, "a site must carry non-empty text"
        assert site.context, "a site must carry a context label"


@pytest.mark.parametrize(
    "relative_path", sorted(path for path in EXPECTED if path.endswith(".bes"))
)
def test_lxml_adapter_agrees_with_expat_across_the_corpus(relative_path: str) -> None:
    """The two parsers must not disagree on a single line, on any real file."""
    lxml_etree = pytest.importorskip("lxml.etree")
    from bigfix_relevance_analyzer.extract import extract_relevance_from_lxml_tree

    path = EXAMPLES / relative_path
    tree = lxml_etree.fromstring(path.read_bytes()).getroottree()
    assert extract_relevance_from_lxml_tree(tree) == extract_relevance_from_file(path)


def test_corpus_extraction_is_silent(capsys: pytest.CaptureFixture[str]) -> None:
    """Nothing may reach stdout/stderr: the package must be safe in a stdio server."""
    for path in corpus_files():
        extract_relevance_from_file(path)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
