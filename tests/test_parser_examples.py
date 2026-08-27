"""The parser against every real relevance site in the example corpus.

This is the integration ratchet: the whole corpus currently parses, and this
test keeps it that way. A new example that fails to parse is a finding --
either a grammar gap worth a corpus record in ``tests/corpus/``, or broken
relevance worth knowing about -- never something to silence.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.parser import try_parse
from bigfix_relevance_analyzer.tokenizer import code_tokens


def corpus_sites() -> list[tuple[str, str]]:
    return [
        (f"{path.name}:{site.line}", site.text)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
    ]


def test_the_corpus_yields_relevance_to_parse() -> None:
    assert len(corpus_sites()) > 20


def test_every_corpus_site_parses() -> None:
    offenders = [
        (label, str(result.error))
        for label, text in corpus_sites()
        if not (result := try_parse(text)).ok
    ]
    assert offenders == []


def test_every_parsed_root_span_covers_all_the_code_tokens() -> None:
    for label, text in corpus_sites():
        result = try_parse(text)
        if result.node is None:
            continue
        tokens = list(code_tokens(text))
        assert result.node.span.start == tokens[0].offset, label
        assert result.node.span.end == tokens[-1].offset + len(tokens[-1].text), label


def test_parsing_the_corpus_is_silent(capsys: pytest.CaptureFixture[str]) -> None:
    """Nothing may reach stdout/stderr: the package must be safe in a stdio server."""
    for _label, text in corpus_sites():
        try_parse(text)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_the_parser_is_exported_from_the_package_root() -> None:
    import bigfix_relevance_analyzer as pkg

    assert pkg.parse_relevance is not None
    assert pkg.try_parse_relevance is not None
    assert pkg.ParseError is not None
    assert pkg.to_sexpr is not None
    assert {"ParseError", "parse_relevance", "to_sexpr", "try_parse_relevance"} <= set(pkg.__all__)
