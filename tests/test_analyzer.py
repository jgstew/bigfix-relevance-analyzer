"""Tests for the analyzer skeleton."""

import pytest

from bigfix_relevance_analyzer import __version__
from bigfix_relevance_analyzer.analyzer import RelevanceExpression, parse


def test_version_is_importable_and_nonempty() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_parse_returns_relevance_expression() -> None:
    result = parse('exists file "test.txt" of folder "test"')
    assert isinstance(result, RelevanceExpression)
    assert result.raw == 'exists file "test.txt" of folder "test"'


@pytest.mark.parametrize("bad_input", ["", "   ", "\n\t"])
def test_parse_rejects_blank_input(bad_input: str) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        parse(bad_input)
