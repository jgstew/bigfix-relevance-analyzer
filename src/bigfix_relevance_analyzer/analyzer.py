"""Core relevance-expression types and parsing entry point.

This is a minimal skeleton: it validates input and wraps it in a
`RelevanceExpression`. Real BigFix Relevance grammar/analysis is not
implemented yet.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelevanceExpression:
    """A single BigFix Relevance expression, held as raw source text."""

    raw: str


def parse(text: str) -> RelevanceExpression:
    """Wrap ``text`` in a :class:`RelevanceExpression`.

    Raises:
        ValueError: if ``text`` is not a non-empty, non-blank string.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("relevance expression text must be a non-empty string")
    return RelevanceExpression(raw=text)
