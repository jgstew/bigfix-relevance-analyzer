"""Tests for :attr:`~bigfix_relevance_analyzer.lint.Finding.spans` (issue #96, item 1).

A span says which characters of the analysed statement a finding is about:
0-based, end-exclusive offsets into the site's text (or the bare statement),
so it is intrinsic to the statement and survives the statement moving. An
empty ``spans`` means the finding is about the statement as a whole.

``Finding.line`` keeps its meaning throughout; these tests check the two
agree, they never move a line.
"""

from __future__ import annotations

import dataclasses

import pytest
from _helpers import BROKEN, UNKNOWN_INSPECTOR

from bigfix_relevance_analyzer import TextSpan
from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.extract import (
    extract_relevance_from_actionscript,
    extract_relevance_from_bes_xml,
    extract_relevance_from_markdown,
)
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    _judge_site,
    lint_analysis,
    lint_text,
)
from bigfix_relevance_analyzer.lsp.linter import DocumentLinter

EVERYTHING = LintConfig(max_score=0.0, max_evaluation_cost=0.0)
"""Every statement-level rule a bare statement can trip, switched on."""


def only(findings: tuple[Finding, ...], code: str) -> Finding:
    (finding,) = (finding for finding in findings if finding.code == code)
    return finding


def covered(text: str, finding: Finding) -> list[str]:
    return [text[span.start : span.end] for span in finding.spans]


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# ---------------------------------------------------------------------------
# The type
# ---------------------------------------------------------------------------


def test_a_text_span_is_a_frozen_start_and_end() -> None:
    span = TextSpan(3, 7)
    assert (span.start, span.end) == (3, 7)
    assert [field.name for field in dataclasses.fields(TextSpan)] == ["start", "end", "message"]
    assert span.message is None
    with pytest.raises(dataclasses.FrozenInstanceError):
        span.start = 1  # type: ignore[misc]


def test_spans_is_the_last_field_and_defaults_to_empty() -> None:
    """Additive: every existing positional or keyword construction still works."""
    fields = dataclasses.fields(Finding)
    assert fields[-1].name == "spans"
    assert [field.name for field in fields[:-1]] == [
        "code",
        "severity",
        "message",
        "path",
        "line",
        "site",
        "suggestions",
        "autofix",
    ]
    finding = lint_text(BROKEN, LintConfig())[0]
    bare = Finding(finding.code, finding.severity, finding.message, None, 1)
    assert bare.spans == ()


# ---------------------------------------------------------------------------
# What each rule's span covers
# ---------------------------------------------------------------------------


def test_error_token_covers_the_unlexable_text() -> None:
    finding = only(lint_text(BROKEN, LintConfig()), "error-token")
    assert covered(BROKEN, finding) == ['"unterminated']
    assert finding.spans == (TextSpan(12, 25),)


def test_parse_error_covers_the_offending_token() -> None:
    text = 'exists file "a" ('
    finding = only(lint_text(text, LintConfig()), "parse-error")
    assert covered(text, finding) == ["("]


def test_parse_error_at_end_of_input_is_an_empty_span_there() -> None:
    text = 'exists file "x" whose (it\n    is'
    finding = only(lint_text(text, LintConfig()), "parse-error")
    assert finding.spans == (TextSpan(len(text), len(text)),)


def test_parse_error_on_an_unterminated_string_covers_it() -> None:
    finding = only(lint_text(BROKEN, LintConfig()), "parse-error")
    assert covered(BROKEN, finding) == ['"unterminated']


def test_unbound_it_covers_it() -> None:
    text = "name of it as lowercase"
    finding = only(lint_text(text, LintConfig()), "unbound-it")
    assert covered(text, finding) == ["it"]


def test_a_type_error_covers_the_comparison() -> None:
    """What the checker's span covers today: the whole binary expression."""
    text = 'exists file "x" whose (size of it = "big")'
    finding = only(lint_text(text, LintConfig()), "type-error")
    assert covered(text, finding) == ['size of it = "big"']


def test_plural_preferred_covers_the_chain_from_the_singular() -> None:
    text = 'exists value "a" of key "b" of registry'
    finding = only(lint_text(text, LintConfig()), "plural-preferred")
    assert covered(text, finding) == ['value "a" of key "b" of registry']


def test_non_unique_risk_covers_the_singular_chain() -> None:
    text = 'names of file of folder "c:\\x"'
    finding = only(lint_text(text, LintConfig()), "non-unique-risk")
    assert covered(text, finding) == ['file of folder "c:\\x"']


def test_a_version_compare_covers_the_comparison() -> None:
    text = 'version of file "x" > "1.2"'
    finding = only(lint_text(text, LintConfig()), "version-truncating-compare")
    assert covered(text, finding) == [text]


def test_every_check_diagnostic_carries_the_checkers_span() -> None:
    """Every rule fed from the checker, not just the ones named above."""
    for text in (
        'exists value "a" of key "b" of registry',
        'names of file of folder "c:\\x"',
        "name of operating system = 3",
        'exists wait2 of file "x"',
        'version of file "x" > "1.2"',
    ):
        report = analyze(text)
        assert report.check is not None
        expected = [
            TextSpan(diagnostic.span.start, diagnostic.span.end)
            for diagnostic in report.check.diagnostics
            if diagnostic.code != "used-without-context"
        ]
        findings = [
            finding
            for finding in lint_analysis(report, LintConfig())
            if finding.code not in {"parse-error", "error-token", "unbound-it", "unknown-inspector"}
        ]
        assert [span for finding in findings for span in finding.spans] == expected, text
        for finding in findings:
            assert len(finding.spans) == 1
            assert finding.spans[0].start < finding.spans[0].end


def test_an_actionscript_keyword_covers_the_word() -> None:
    text = 'exists run of file "x"'
    finding = only(lint_text(text, LintConfig()), "actionscript-keyword")
    assert covered(text, finding) == ["run"]


def test_an_actionscript_keyword_covers_its_first_use_only() -> None:
    text = 'exists run of file "x" or exists run of file "y"'
    finding = only(lint_text(text, LintConfig()), "actionscript-keyword")
    assert finding.spans == (TextSpan(7, 10),)


def test_unknown_inspector_stays_one_finding_with_a_span_per_use() -> None:
    """One finding, as lint and the hook count it; a span for every use of
    every unknown name, in source order, covering the name and not its argument."""
    text = 'exists totally bogus whose (exists bogus thing "x") and exists totally bogus'
    findings = lint_text(text, LintConfig())
    finding = only(findings, "unknown-inspector")
    assert covered(text, finding) == ["totally bogus", "bogus thing", "totally bogus"]
    assert [span.start for span in finding.spans] == sorted(span.start for span in finding.spans)


def test_each_unknown_use_carries_a_message_for_its_own_name() -> None:
    """Worded in lint, not re-derived by a consumer from the finding's message."""
    text = "exists bogus one whose (exists bogus two) and exists bogus one"
    finding = only(lint_text(text, LintConfig()), "unknown-inspector")
    assert [span.message for span in finding.spans] == [
        "no dump defines `bogus one`",
        "no dump defines `bogus two`",
        "no dump defines `bogus one`",
    ]


def test_each_unknown_use_offers_only_its_own_leads() -> None:
    text = "exists oprating system and exists bogus two"
    finding = only(lint_text(text, LintConfig(suggest=True)), "unknown-inspector")
    typo, bogus = (span.message for span in finding.spans)
    assert typo is not None and bogus is not None
    assert typo.startswith("no dump defines `oprating system` -- did you mean `operating system`")
    assert bogus == "no dump defines `bogus two`"


def test_one_unknown_name_has_the_findings_own_message() -> None:
    for config in (LintConfig(), LintConfig(suggest=True)):
        finding = only(lint_text("exists oprating system", config), "unknown-inspector")
        assert [span.message for span in finding.spans] == [finding.message]


def test_spans_of_other_rules_have_no_message_of_their_own() -> None:
    for finding in lint_text(
        'exists file "x" whose (size of it = "big") or ' + BROKEN, LintConfig()
    ):
        assert finding.spans
        assert all(span.message is None for span in finding.spans), finding.code


def test_unknown_inspector_with_one_name() -> None:
    finding = only(lint_text(f"exists {UNKNOWN_INSPECTOR}", LintConfig()), "unknown-inspector")
    assert [(span.start, span.end) for span in finding.spans] == [(7, 7 + len(UNKNOWN_INSPECTOR))]


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ('(exists files of folders "/") AND (exists bes computers)', "mixed-dialect"),
        ('exists file "x"', "complexity"),
        ('exists descendants of folder "c:\\"', "evaluation-cost"),
    ],
)
def test_statement_level_findings_have_no_spans(text: str, code: str) -> None:
    finding = only(lint_text(text, EVERYTHING), code)
    assert finding.spans == ()


def test_substitution_findings_are_statement_level() -> None:
    (site,) = extract_relevance_from_actionscript('wait {names of files of folder "x"}')
    finding = only(_judge_site(None, site, LintConfig()), "plural-substitution")
    assert finding.spans == ()


def test_a_site_type_mismatch_is_statement_level() -> None:
    (site,) = extract_relevance_from_bes_xml(
        b'<BES><Fixlet><Relevance>names of files of folder "x"</Relevance></Fixlet></BES>'
    )
    finding = only(_judge_site(None, site, LintConfig()), "site-type-mismatch")
    assert finding.spans == ()


# ---------------------------------------------------------------------------
# Spans and lines agree
# ---------------------------------------------------------------------------

MULTI_LINE = [
    '(exists file "a" AND\n\texists file "b"',
    'exists file "x"\n  whose (size of it = "big")',
    'exists file "x" whose (it\n    is',
    'exists file "x"\n  whose (name of it as lowercase = "a") and name of it = "b"',
    'exists file "x" and\nexists value "a" of key "b" of registry',
    'exists file "x" or\n  exists file "unterminated',
]


@pytest.mark.parametrize("text", MULTI_LINE)
def test_a_span_starts_on_the_line_its_finding_reports(text: str) -> None:
    findings = lint_text(text, LintConfig())
    spanned = [finding for finding in findings if finding.spans]
    assert spanned
    for finding in spanned:
        if finding.code == "unknown-inspector":
            continue
        assert finding.line == line_of(text, finding.spans[0].start), finding


def test_spans_follow_a_site_whose_line_is_not_one() -> None:
    """Site-relative: a site deep in a file has spans into ``site.text`` all the same."""
    markdown = (
        '# Title\n\nprose\n\n```relevance\nexists file "x"\n  whose (size of it = "big")\n```\n'
    )
    (site,) = extract_relevance_from_markdown(markdown)
    finding = only(_judge_site(None, site, LintConfig()), "type-error")
    assert covered(site.text, finding) == ['size of it = "big"']
    assert finding.line == site.line + line_of(site.text, finding.spans[0].start) - 1


def test_unknown_inspector_still_reports_the_statements_first_line() -> None:
    text = 'exists file "x" and\n  exists totally bogus'
    finding = only(lint_text(text, LintConfig()), "unknown-inspector")
    assert finding.line == 1
    assert line_of(text, finding.spans[0].start) == 2


# ---------------------------------------------------------------------------
# Serialization and the editor's cache
# ---------------------------------------------------------------------------


def test_to_dict_adds_spans_and_keeps_every_other_key() -> None:
    finding = only(lint_text(BROKEN, LintConfig()), "error-token")
    payload = finding.to_dict()
    assert list(payload) == [
        "code",
        "severity",
        "message",
        "path",
        "line",
        "site",
        "suggestions",
        "autofix",
        "text",
        "spans",
    ]
    assert payload["spans"] == [{"start": 12, "end": 25, "message": None}]
    assert payload["text"] == str(finding)


def test_a_statement_level_finding_serializes_empty_spans() -> None:
    finding = only(lint_text('exists file "x"', EVERYTHING), "complexity")
    assert finding.to_dict()["spans"] == []


def test_str_is_unchanged_by_spans() -> None:
    finding = only(lint_text(BROKEN, LintConfig()), "error-token")
    assert str(finding) == "line 1: error [error-token] unlexable text '\"unterminated'"


def test_lint_text_spans_are_into_the_stripped_statement() -> None:
    """Like ``line``: lint_text analyses ``text.strip()``, and both are relative to that."""
    padded = f"\n\n   {BROKEN}   \n"
    assert only(lint_text(padded, LintConfig()), "error-token").spans == (TextSpan(12, 25),)


def test_the_editors_cache_keeps_spans_right_for_a_moved_site() -> None:
    markdown = '```relevance\nexists file "x"\n  whose (size of it = "big")\n```\n'
    moved = "intro\n\n\n" + markdown
    (site,) = extract_relevance_from_markdown(markdown)
    (moved_site,) = extract_relevance_from_markdown(moved)
    linter = DocumentLinter()
    linter._judge(None, site, linter.config)
    cached = linter._judge(None, moved_site, linter.config)
    assert linter.cache_stats().hits == 1
    uncached = _judge_site(None, moved_site, linter.config)
    assert [finding.spans for finding in cached] == [finding.spans for finding in uncached]
    assert [finding.line for finding in cached] == [finding.line for finding in uncached]
    assert all(finding.spans for finding in cached)
