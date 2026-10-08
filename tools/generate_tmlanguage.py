#!/usr/bin/env python3
"""Generate the VS Code TextMate grammars for BigFix Relevance.

    uv run python tools/generate_tmlanguage.py

Writes two grammars into the "BigFix Relevance Developer" extension
(tools/vscode-extension/componentize-py/syntaxes/):

* ``bigfix-relevance.tmLanguage.json``: whole-file relevance (``.rel``,
  ``.bsr``, and untitled buffers in the language).
* ``markdown-relevance.injection.json``: relevance inside the markdown fences
  the extractor reads (```` ```relevance ```` and its dialect-tagged forms).

Generated, never hand-edited: the vocabulary comes from the parser's own tables
in ``grammar.py``, the articles from ``tokenizer.py`` and the fence tags from
``extract.py``, so the editor colors what the analyzer parses.
tests/test_vscode_extension_layout.py fails when a committed grammar differs
from this script's output; rerun it after changing any of those tables.

A static grammar is lexical. It cannot tell the ``starts`` of ``starts with``
from the inspector ``date range starts``, which needs the parser (a semantic-
tokens job; see issue #96). It colors keywords and operators, not inspector
names.

The idea of allowing articles between the words of a multi-word operator comes
from https://github.com/bigfix/hljs-bigfix-relevance (Apache-2.0). The word
lists here are this package's own.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from bigfix_relevance_analyzer.extract import _MARKDOWN_RELEVANCE_TAGS  # noqa: E402
from bigfix_relevance_analyzer.grammar import (  # noqa: E402
    BP_AND,
    BP_MULTIPLICATIVE,
    BP_OR,
    BP_RELATIONAL,
    PUNCT_INFIX,
    STRUCTURAL_WORDS,
    WORD_INFIX,
)
from bigfix_relevance_analyzer.tokenizer import _ARTICLES  # noqa: E402

SYNTAXES = Path("tools/vscode-extension/componentize-py/syntaxes")
RELEVANCE_PATH = SYNTAXES / "bigfix-relevance.tmLanguage.json"
MARKDOWN_PATH = SYNTAXES / "markdown-relevance.injection.json"

SCOPE = "source.bigfix-relevance"
EMBEDDED = "meta.embedded.block.bigfix-relevance"

# Every structural word needs a scope here: a word added to STRUCTURAL_WORDS
# without one fails generation rather than going uncolored.
STRUCTURAL_SCOPES = {
    "if": "keyword.control.conditional",
    "then": "keyword.control.conditional",
    "else": "keyword.control.conditional",
    "whose": "keyword.control.filter",
    "of": "keyword.operator.of",
    "as": "keyword.operator.cast",
    "it": "variable.language.it",
    "not": "keyword.operator.logical",
    "exists": "keyword.operator.logical",
    "exist": "keyword.operator.logical",
}

# Word operators by the class their binding power puts them in.
OPERATOR_CLASS_SCOPES = {
    BP_OR: "keyword.operator.logical",
    BP_AND: "keyword.operator.logical",
    BP_RELATIONAL: "keyword.operator.comparison",
    BP_MULTIPLICATIVE: "keyword.operator.arithmetic",
}

CONSTANTS = ("true", "false")


def _phrase_regex(words: tuple[str, ...]) -> str:
    """``words`` as one case-insensitive phrase, articles allowed between words.

    The tokenizer drops articles as trivia anywhere, so ``is not equal to the``
    style spellings parse the same; the grammar colors them the same.
    """
    articles = "|".join(sorted(_ARTICLES))
    gap = rf"\s+(?:(?:{articles})\s+)*"
    return gap.join(re.escape(word) for word in words)


def _alternation(phrases: list[tuple[str, ...]]) -> str:
    """A case-insensitive alternation, longest phrase first, on word boundaries."""
    ordered = sorted(phrases, key=lambda words: (-len(" ".join(words)), words))
    return r"(?i)\b(?:" + "|".join(_phrase_regex(words) for words in ordered) + r")\b"


def _word_operator_patterns() -> list[dict[str, Any]]:
    by_scope: dict[str, list[tuple[str, ...]]] = {}
    for words, op in WORD_INFIX.items():
        scope = OPERATOR_CLASS_SCOPES.get(op.lbp)
        if scope is None:
            raise SystemExit(f"no scope for the binding power of {op.canonical!r}")
        by_scope.setdefault(scope, []).append(words)
    return [
        {"name": f"{scope}.bigfix-relevance", "match": _alternation(phrases)}
        for scope, phrases in sorted(by_scope.items())
    ]


def _structural_patterns() -> list[dict[str, Any]]:
    missing = sorted(set(STRUCTURAL_WORDS) - set(STRUCTURAL_SCOPES))
    if missing:
        raise SystemExit(
            f"no scope for structural word(s) {missing}; add them to STRUCTURAL_SCOPES"
        )
    by_scope: dict[str, list[tuple[str, ...]]] = {}
    for word in sorted(STRUCTURAL_WORDS):
        by_scope.setdefault(STRUCTURAL_SCOPES[word], []).append((word,))
    return [
        {"name": f"{scope}.bigfix-relevance", "match": _alternation(words)}
        for scope, words in sorted(by_scope.items())
    ]


def relevance_grammar() -> dict[str, Any]:
    """The whole-file relevance grammar."""
    punctuation = sorted(PUNCT_INFIX, key=lambda op: (-len(op), op))
    repository: dict[str, Any] = {
        # Non-nesting, like the tokenizer: the comment ends at the first `*/`.
        "comment": {
            "name": "comment.block.bigfix-relevance",
            "begin": r"/\*",
            "end": r"\*/",
        },
        # No backslash escapes in relevance: a literal quote is written `%22`,
        # so quotes pair off left to right, and a string may span lines.
        "string": {
            "name": "string.quoted.double.bigfix-relevance",
            "begin": '"',
            "end": '"',
            "patterns": [
                {
                    "name": "constant.character.escape.bigfix-relevance",
                    "match": "%[0-9A-Fa-f]{2}",
                }
            ],
        },
        "number": {"name": "constant.numeric.integer.bigfix-relevance", "match": r"\b[0-9]+\b"},
        # Multi-word operators before single structural words, so `is not
        # equal to` is one operator rather than `is` plus a `not`.
        "word-operator": {"patterns": _word_operator_patterns()},
        "structural": {"patterns": _structural_patterns()},
        "constant": {
            "name": "constant.language.bigfix-relevance",
            "match": _alternation([(word,) for word in CONSTANTS]),
        },
        "punctuation-operator": {
            "name": "keyword.operator.bigfix-relevance",
            "match": "|".join(re.escape(op) for op in punctuation),
        },
        "separator": {"name": "punctuation.separator.bigfix-relevance", "match": "[;,]"},
        "paren": {"name": "punctuation.section.parens.bigfix-relevance", "match": r"[()]"},
    }
    order = [
        "comment",
        "string",
        "number",
        "word-operator",
        "structural",
        "constant",
        "punctuation-operator",
        "separator",
        "paren",
    ]
    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "BigFix Relevance",
        "scopeName": SCOPE,
        "comment": "Generated by tools/generate_tmlanguage.py; do not edit by hand.",
        "patterns": [{"include": f"#{name}"} for name in order],
        "repository": repository,
    }


def fence_tags() -> list[str]:
    """The fence info strings the extractor reads, and so the grammar colors."""
    return sorted(_MARKDOWN_RELEVANCE_TAGS)


def markdown_injection() -> dict[str, Any]:
    """Relevance inside the markdown fences the extractor reads.

    The extractor takes a fence only when its info string, stripped and
    lowercased, is exactly one of the tags, so a fence with any other info
    (``relevance foo``) is left uncolored here too.
    """
    tags = "|".join(re.escape(tag) for tag in fence_tags())
    return {
        "comment": "Generated by tools/generate_tmlanguage.py; do not edit by hand.",
        "scopeName": "markdown.bigfix-relevance.codeblock",
        "injectionSelector": "L:text.html.markdown",
        "patterns": [{"include": "#fenced-relevance"}],
        "repository": {
            "fenced-relevance": {
                "name": "markup.fenced_code.block.markdown",
                "begin": r"(^|\G)(\s*)(`{3,}|~{3,})\s*(?i:(" + tags + r"))\s*$",
                "beginCaptures": {
                    "3": {"name": "punctuation.definition.markdown"},
                    "4": {"name": "fenced_code.block.language.markdown"},
                },
                "end": r"(^|\G)(\2|\s{0,3})(\3)\s*$",
                "endCaptures": {"3": {"name": "punctuation.definition.markdown"}},
                "patterns": [
                    {
                        "begin": r"(^|\G)(\s*)(.*)",
                        "while": r"(^|\G)(?!\s*([`~]{3,})\s*$)",
                        "contentName": EMBEDDED,
                        "patterns": [{"include": SCOPE}],
                    }
                ],
            }
        },
    }


def render() -> dict[Path, dict[str, Any]]:
    """Every generated grammar, keyed by its path relative to the repository."""
    return {RELEVANCE_PATH: relevance_grammar(), MARKDOWN_PATH: markdown_injection()}


def main() -> int:
    for path, grammar in render().items():
        target = REPO_ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
