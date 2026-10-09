#!/usr/bin/env python3
"""Generate the VS Code TextMate grammars for BigFix Relevance.

    uv run python tools/generate_tmlanguage.py

Writes four grammars into the "BigFix Relevance Developer" extension
(tools/vscode-extension/componentize-py/syntaxes/):

* ``bigfix-relevance.tmLanguage.json``: whole-file relevance (``.rel``,
  ``.bsr``, and untitled buffers in the language).
* ``markdown-relevance.injection.json``: relevance inside the markdown fences
  the extractor reads (```` ```relevance ```` and its dialect-tagged forms).
* ``bigfix-actionscript.tmLanguage.json``: ActionScript (``.actionscript``),
  with relevance inside ``{...}`` substitutions.
* ``bigfix-bes.tmLanguage.json``: BES XML (``.bes``), XML with the
  ActionScript and relevance bodies the extractor reads embedded.

Generated, never hand-edited: the vocabulary comes from the parser's own tables
in ``grammar.py``, the articles from ``tokenizer.py``, the fence tags, heredoc
rule and ActionScript MIME types from ``extract.py``, and the ActionScript verbs
from ``tools/data/actionscript_verbs.txt``, so the editor colors what the
analyzer parses.
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

from bigfix_relevance_analyzer.extract import (
    _ACTIONSCRIPT_MIMETYPES,
    _HEREDOC_RE,
    _MARKDOWN_RELEVANCE_TAGS,
)
from bigfix_relevance_analyzer.grammar import (
    BP_AND,
    BP_MULTIPLICATIVE,
    BP_OR,
    BP_RELATIONAL,
    PUNCT_INFIX,
    STRUCTURAL_WORDS,
    WORD_INFIX,
)
from bigfix_relevance_analyzer.tokenizer import _ARTICLES

# Run with `uv run`, which installs this package into the environment: no
# sys.path changes needed. The underscore-private tables are imported on
# purpose, as elsewhere in this repository (lint.py imports extract's), so the
# grammar has no second copy of them to drift.
REPO_ROOT = Path(__file__).resolve().parent.parent

SYNTAXES = Path("tools/vscode-extension/componentize-py/syntaxes")
RELEVANCE_PATH = SYNTAXES / "bigfix-relevance.tmLanguage.json"
MARKDOWN_PATH = SYNTAXES / "markdown-relevance.injection.json"
ACTIONSCRIPT_PATH = SYNTAXES / "bigfix-actionscript.tmLanguage.json"
BES_PATH = SYNTAXES / "bigfix-bes.tmLanguage.json"
VERBS_PATH = Path("tools/data/actionscript_verbs.txt")

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


def _fence_rule(char: str, tags: str) -> dict[str, Any]:
    """The rule for fences of one character: `` ` `` or ``~``.

    Mirrors ``extract._markdown_sites``: it opens on three or more of the
    character with exactly one of the tags as the info string, and closes on
    any line of three or more of the *same* character with nothing after it,
    whatever the opener's length. A fence of the other character inside is
    content, not a close.
    """
    run = char + "{3,}"  # neither ` nor ~ is special in a regex
    return {
        "name": "markup.fenced_code.block.markdown",
        "begin": r"(^|\G)(\s*)(" + run + r")\s*(?i:(" + tags + r"))\s*$",
        "beginCaptures": {
            "3": {"name": "punctuation.definition.markdown"},
            "4": {"name": "fenced_code.block.language.markdown"},
        },
        "end": r"(^|\G)\s*(" + run + r")\s*$",
        "endCaptures": {"2": {"name": "punctuation.definition.markdown"}},
        "patterns": [
            {
                "begin": r"(^|\G)(\s*)(.*)",
                "while": r"(^|\G)(?!\s*" + run + r"\s*$)",
                "contentName": EMBEDDED,
                "patterns": [{"include": SCOPE}],
            }
        ],
    }


def markdown_injection() -> dict[str, Any]:
    """Relevance inside the markdown fences the extractor reads.

    The extractor takes a fence only when its info string, stripped and
    lowercased, is exactly one of the tags, so a fence with any other info
    (``relevance foo``) is left uncolored here too. Backtick and tilde fences
    get a rule each, because each closes only on its own character.
    """
    tags = "|".join(re.escape(tag) for tag in fence_tags())
    return {
        "comment": "Generated by tools/generate_tmlanguage.py; do not edit by hand.",
        "scopeName": "markdown.bigfix-relevance.codeblock",
        "injectionSelector": "L:text.html.markdown",
        "patterns": [{"include": "#backtick-fence"}, {"include": "#tilde-fence"}],
        "repository": {
            "backtick-fence": _fence_rule("`", tags),
            "tilde-fence": _fence_rule("~", tags),
        },
    }


# ---------------------------------------------------------------------------
# ActionScript
# ---------------------------------------------------------------------------

ACTIONSCRIPT_SCOPE = "source.bigfix-actionscript"
SUBSTITUTION_CONTENT = "meta.embedded.line.bigfix-relevance"

# Flow control, colored apart from the commands. Every other verb in the data
# file is a command.
CONTROL_VERBS = frozenset({"if", "elseif", "else", "endif", "continue if", "pause while"})

# Verbs with a rule of their own: what follows them is not ordinary arguments.
BLOCK_VERBS = frozenset({"createfile until", "appendfile", "override run", "override wait"})

# The `keyword=value` options an `override run|wait` block takes, one per line
# until the command itself. A closed set: from pre-commit-bigfix's
# bes_actionscript_lint_schclass.py (E303), as the BigFix action guide lists them.
OVERRIDE_OPTIONS = (
    "asadmin",
    "completion",
    "detached",
    "disposition",
    "hidden",
    "password",
    "priority",
    "runas",
    "targetuser",
    "timeout_seconds",
    "user",
)

# The end of a `.bes` body. No ActionScript ever reaches past one, so no rule
# may run over it either: the BES grammar has to see it to close the element,
# and a rule that swallowed it would color the rest of the file as
# ActionScript. Harmless in a raw `.actionscript` file, which never has one.
_HOST_END = r"\]\]>|</ActionScript\s*>"
_REST = rf"(?:(?!{_HOST_END}).)"
"""One character of the rest of the line, up to the end of a `.bes` body."""

# A line's first token, the way the action engine reads one: verbs, `//`, a
# heredoc are recognized only there. `\G` also lets the first line of a body
# that starts right after `<![CDATA[` count as a line start.
_LINE_START = r"(?:^|\G)\s*"

# After a verb: whitespace, the end of the line or body, or the `{` of a
# condition written against its keyword (`if{...}`, as real content does).
_VERB_END = rf"(?=[\s{{]|$|{_HOST_END})"

# A `{...}` substitution, scanned as the extractor scans one
# (`_find_substitution_end`): on one line, `}}` is a literal brace, a `}`
# inside a relevance string does not close it, and an unclosed string or brace
# makes it no substitution at all. Possessive, so `}}` is never split.
_SUBSTITUTION_BODY = rf'(?:"[^"]*"|\}}\}}|(?!{_HOST_END})[^}}"])*+'
_SUBSTITUTION = rf"(\{{)({_SUBSTITUTION_BODY})(\}})"

# A string's content: `{{`, whole substitutions (quotes and all), or any other
# character but a quote, up to the end of the body.
_STRING_BODY = rf'(?:\{{\{{|\{{{_SUBSTITUTION_BODY}\}}|(?!{_HOST_END})[^"])*+'

# The console's `url` and `url_https` classes, ended as its overrides end them:
# at a space, tab, `*`, `"`, `}` or the line's end.
_URL = rf'https?:(?:(?!{_HOST_END})[^\s*"}}])+'


def actionscript_verbs() -> list[str]:
    """Every ActionScript command verb, from the committed data file."""
    text = (REPO_ROOT / VERBS_PATH).read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line and not line.startswith("#")]


def _verb_alternation(verbs: list[str]) -> str:
    """``verbs`` longest first, any whitespace between a phrase's words."""
    ordered = sorted(verbs, key=lambda verb: (-len(verb), verb))
    return "|".join(r"\s+".join(re.escape(word) for word in verb.split()) for verb in ordered)


def _verb_rule(verbs: list[str], scope: str) -> dict[str, Any]:
    return {
        "match": rf"(?i){_LINE_START}({_verb_alternation(verbs)}){_VERB_END}",
        "captures": {"1": {"name": f"{scope}.bigfix-actionscript"}},
    }


_RAW_TEXT_PATTERNS = [{"include": "#substitution-escape"}, {"include": "#substitution"}]
"""File content (heredoc and ``appendfile`` text): raw, but still substituted."""


def _heredoc_begin() -> str:
    """``extract._HEREDOC_RE``, with the verb captured and the anchor widened.

    Its source is checked here rather than rewritten blindly, so a change to
    the extractor's rule fails generation instead of drifting.
    """
    expected = r"^\s*(?:create|append)file\s+until\s+(\S+)\s*$"
    if _HEREDOC_RE.pattern != expected or not _HEREDOC_RE.flags & re.IGNORECASE:
        raise SystemExit("extract._HEREDOC_RE changed; update _heredoc_begin() to match")
    # In a `.bes`, the end of the body is the end of its last line: the marker
    # stops there, as the extractor (which sees the decoded body) reads it.
    return (
        rf"(?i){_LINE_START}((?:create|append)file\s+until)\s+"
        rf"((?:(?!{_HOST_END})\S)+)\s*(?:$|(?={_HOST_END}))"
    )


def actionscript_grammar() -> dict[str, Any]:
    """ActionScript: whole files, and the body the BES grammar embeds.

    Every rule is a single-line ``match``, which cannot leak past its line,
    except the two block constructs, each of which also stops at the end of a
    ``.bes`` body. Unknown words are left uncolored, as the console leaves
    them; a mid-line ``//`` is not a comment (URLs hold one, and the action
    engine reads comments only at line start).
    """
    verbs = actionscript_verbs()
    missing = sorted((CONTROL_VERBS | BLOCK_VERBS) - set(verbs))
    if missing:
        raise SystemExit(f"{VERBS_PATH} lacks {missing}; regenerate it")
    commands = [verb for verb in verbs if verb not in CONTROL_VERBS | BLOCK_VERBS]
    options = "|".join(OVERRIDE_OPTIONS)
    repository: dict[str, Any] = {
        "comment": {
            "name": "comment.line.double-slash.bigfix-actionscript",
            "match": rf"{_LINE_START}//{_REST}*",
        },
        "heredoc": {
            "begin": _heredoc_begin(),
            "beginCaptures": {
                "1": {"name": "keyword.other.command.bigfix-actionscript"},
                "2": {"name": "constant.other.heredoc-marker.bigfix-actionscript"},
            },
            # The marker alone on a line (the extractor strips the line), or
            # the end of a `.bes` body for a heredoc left open.
            "end": rf"^\s*(\2)\s*$|(?={_HOST_END})",
            "endCaptures": {"1": {"name": "constant.other.heredoc-marker.bigfix-actionscript"}},
            "contentName": "string.unquoted.heredoc.bigfix-actionscript",
            "patterns": _RAW_TEXT_PATTERNS,
        },
        "appendfile": {
            "match": rf"(?i){_LINE_START}(appendfile){_VERB_END}({_REST}*)",
            "captures": {
                "1": {"name": "keyword.other.command.bigfix-actionscript"},
                "2": {
                    "name": "string.unquoted.file-content.bigfix-actionscript",
                    "patterns": _RAW_TEXT_PATTERNS,
                },
            },
        },
        # The block lasts while lines are options: it ends, without consuming
        # anything, at the start of the first line that is not an option, a
        # `//` comment or blank (the command it overrides, as pre-commit-
        # bigfix's lint reads the block), or at the end of a `.bes` body. Not
        # a `while` rule: inside one the engine never tries the body's own
        # end, so an override left open at `</ActionScript>` would leak.
        "override": {
            "begin": rf"(?i){_LINE_START}(override\s+(?:run|wait)){_VERB_END}",
            "beginCaptures": {"1": {"name": "keyword.other.command.bigfix-actionscript"}},
            "end": rf"(?i)^(?!\s*(?:(?:{options})\s*=|//)|\s*$)|(?={_HOST_END})",
            "patterns": [
                {"include": "#comment"},
                {
                    "match": rf"(?i)(?:^|\G)\s*({options})\s*(=)({_REST}*)",
                    "captures": {
                        "1": {"name": "variable.parameter.option.bigfix-actionscript"},
                        "2": {"name": "keyword.operator.assignment.bigfix-actionscript"},
                        "3": {
                            "name": "string.unquoted.option-value.bigfix-actionscript",
                            "patterns": _RAW_TEXT_PATTERNS,
                        },
                    },
                },
            ],
        },
        "control": _verb_rule(sorted(CONTROL_VERBS), "keyword.control"),
        "command": _verb_rule(commands, "keyword.other.command"),
        "substitution-escape": {
            "name": "constant.character.escape.brace.bigfix-actionscript",
            "match": r"\{\{",
        },
        "substitution": {
            "name": "meta.interpolation.substitution.bigfix-actionscript",
            "match": _SUBSTITUTION,
            "captures": {
                "1": {"name": "punctuation.section.embedded.begin.bigfix-actionscript"},
                "2": {"name": SUBSTITUTION_CONTENT, "patterns": [{"include": SCOPE}]},
                "3": {"name": "punctuation.section.embedded.end.bigfix-actionscript"},
            },
        },
        # No escape character (pre-commit-bigfix#16): `"C:\Bes\"` is closed.
        # A substitution inside may hold quotes of its own, and the string
        # ends at the line, or the body, when it is never closed.
        "string": {
            "name": "string.quoted.double.bigfix-actionscript",
            "match": rf'(")({_STRING_BODY})("|(?={_HOST_END})|$)',
            "captures": {
                "1": {"name": "punctuation.definition.string.begin.bigfix-actionscript"},
                "2": {"patterns": [*_RAW_TEXT_PATTERNS, {"include": "#url"}]},
                "3": {"name": "punctuation.definition.string.end.bigfix-actionscript"},
            },
        },
        "url": {
            "name": "markup.underline.link.bigfix-actionscript",
            "match": rf"(?i)(?<![\w]){_URL}",
        },
        # Never matches. The engine loads an embedded grammar only when it
        # finds the include among `patterns`, never among `captures` (both
        # vscode-textmate's dependency walk and so VS Code's), and the
        # relevance in a substitution is only ever included from captures.
        # Without this, a `.actionscript` file opened on its own would leave
        # every substitution uncolored.
        "relevance-dependency": {
            "begin": "(?!)",
            "end": "(?!)",
            "patterns": [{"include": SCOPE}],
        },
    }
    order = [
        "comment",
        "heredoc",
        "appendfile",
        "override",
        "control",
        "command",
        "substitution-escape",
        "substitution",
        "string",
        "url",
        "relevance-dependency",
    ]
    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "BigFix ActionScript",
        "scopeName": ACTIONSCRIPT_SCOPE,
        "comment": "Generated by tools/generate_tmlanguage.py; do not edit by hand.",
        "patterns": [{"include": f"#{name}"} for name in order],
        "repository": repository,
    }


# ---------------------------------------------------------------------------
# BES XML
# ---------------------------------------------------------------------------

BES_SCOPE = "text.xml.bigfix-bes"


# A start tag's attributes, quote-aware: a `>` inside a quoted value does not
# end the tag. One pattern for every place a start tag is read.
_ATTRIBUTE_TEXT = r"""(?:"[^"]*"|'[^']*'|[^>"'])*"""

_TAG = "punctuation.definition.tag.xml"
_TAG_NAME = "entity.name.tag.localname.xml"


def _attributes() -> list[dict[str, Any]]:
    """An XML start tag's attributes, scoped as VS Code's own XML grammar does."""
    return [
        {
            "match": r"([-\w.:]+)\s*(=)",
            "captures": {
                "1": {"name": "entity.other.attribute-name.localname.xml"},
                "2": {"name": "punctuation.separator.key-value.xml"},
            },
        },
        {"name": "string.quoted.double.xml", "match": r'"[^"]*"'},
        {"name": "string.quoted.single.xml", "match": r"'[^']*'"},
    ]


def _cdata(body: list[dict[str, Any]]) -> dict[str, Any]:
    """A CDATA section in a body: the element's own embedded scope covers it."""
    return {
        "begin": r"<!\[CDATA\[",
        "beginCaptures": {"0": {"name": "punctuation.definition.string.begin.xml"}},
        "end": r"\]\]>",
        "endCaptures": {"0": {"name": "punctuation.definition.string.end.xml"}},
        "patterns": body,
    }


# The elements whose bodies are relevance, as the extractor reads them. Both
# the start rule and the body-end guard are built from this one list, so a tag
# cannot open a body that its guard does not close.
RELEVANCE_TAGS = ("Relevance", "Property", "SuccessCriteria")

# Where a relevance body ends: its element's end tag, or its CDATA section's.
_RELEVANCE_BODY_END = rf"(?=</(?:{'|'.join(RELEVANCE_TAGS)})\s*>|\]\]>)"


def _relevance_body() -> dict[str, Any]:
    """A relevance body, in or out of CDATA.

    Relevance strings and comments may span lines, so in a ``.bes`` one left
    open would run on to the next quote anywhere in the file. Here they also
    end at the end of the body: the relevance grammar's own rules, with the
    end widened, listed first so they win where both would start.
    """
    repository = relevance_grammar()["repository"]
    guarded = [
        {**repository[name], "end": f"{repository[name]['end']}|{_RELEVANCE_BODY_END}"}
        for name in ("string", "comment")
    ]
    return {"patterns": [*guarded, {"include": SCOPE}]}


def _actionscript_element(mimetypes: str) -> dict[str, dict[str, Any]]:
    """``<ActionScript>``, in two stages, so its start tag may span lines.

    Real content often puts the MIMEType on the line after ``<ActionScript``
    (641 of 7,759 Windows-Shell action scripts in a local corpus), and a
    TextMate rule's begin sees one line. So the element opens on the name
    alone, and inside it, in order of priority:

    * a MIMEType naming another language ends the tag as a tag (attributes,
      then ``/>`` or ``>``) and hands the body to the XML grammar (the
      extractor skips those bodies too);
    * a ``/>`` ends an element with no body;
    * attributes are colored as attributes;
    * the tag's own ``>`` opens the ActionScript body, which runs to the end tag.
    """
    other_language = (
        r"\b(MIMEType)\s*(=)\s*"
        rf"(\"(?!(?i:{mimetypes})\")[^\"]*\"|'(?!(?i:{mimetypes})')[^']*')"
    )
    up_to_end_tag = r"(?=</ActionScript\s*>)"
    return {
        "actionscript": {
            "begin": r"(<)(ActionScript)(?=[\s>/]|$)",
            "beginCaptures": {"1": {"name": _TAG}, "2": {"name": _TAG_NAME}},
            # The end tag, or straight after a self-closing `/>`.
            "end": r"(</)(ActionScript)\s*(>)|(?<=/>)",
            "endCaptures": {
                "1": {"name": _TAG},
                "2": {"name": _TAG_NAME},
                "3": {"name": _TAG},
            },
            "patterns": [
                {"include": "#actionscript-other-language"},
                {"include": "#actionscript-self-closing"},
                {"include": "#attributes"},
                {"include": "#actionscript-body"},
            ],
        },
        "actionscript-other-language": {
            "begin": other_language,
            "beginCaptures": {
                "1": {"name": "entity.other.attribute-name.localname.xml"},
                "2": {"name": "punctuation.separator.key-value.xml"},
                "3": {"name": "string.quoted.xml"},
            },
            # The end tag, or straight after a self-closing `/>`; the body, once
            # open, hides both from this rule.
            "end": r"(?=</ActionScript\s*>)|(?<=/>)",
            "patterns": [
                {"include": "#actionscript-self-closing"},
                {"include": "#attributes"},
                {"include": "#actionscript-other-body"},
            ],
        },
        "actionscript-other-body": {
            "begin": "(>)",
            "beginCaptures": {"1": {"name": _TAG}},
            "end": up_to_end_tag,
            "patterns": [{"include": "text.xml"}],
        },
        "actionscript-self-closing": {"name": _TAG, "match": "/>"},
        "actionscript-body": {
            "begin": "(>)",
            "beginCaptures": {"1": {"name": _TAG}},
            "end": up_to_end_tag,
            "contentName": "meta.embedded.block.bigfix-actionscript",
            "patterns": [
                {"include": "#cdata-actionscript"},
                {"include": "#entity"},
                {"include": ACTIONSCRIPT_SCOPE},
            ],
        },
        "cdata-actionscript": _cdata([{"include": ACTIONSCRIPT_SCOPE}]),
    }


def _relevance_element() -> dict[str, dict[str, Any]]:
    """``<Relevance>``, ``<Property>``, ``<SuccessCriteria Option="CustomRelevance">``.

    One rule whose begin holds the whole start tag, so ``Option`` can be
    checked: such a tag split across lines is left uncolored (a documented
    limitation; no real content splits these tags). ``<Property>`` holds
    relevance at the top level of a BES file (a global property) and inside
    an ``<Analysis>``. The schema also allows a ``<Property>`` naming a
    property inside an action's ``<Whose>`` settings, which is not relevance;
    a lexical grammar cannot tell them apart, and no file in a 6,295-file
    corpus has one, so it is colored too.
    """
    # The extractor compares the option exactly, so the grammar does too. No
    # capture groups here: they would renumber the begin rule's captures.
    custom_relevance = (
        rf"(?={_ATTRIBUTE_TEXT}?\bOption\s*=\s*(?:\"CustomRelevance\"|'CustomRelevance'))"
    )
    # Only `SuccessCriteria` has a condition: `Option="CustomRelevance"`.
    conditions = {"SuccessCriteria": rf"(?=\s){custom_relevance}"}
    names = "|".join(f"{tag}{conditions.get(tag, '')}" for tag in RELEVANCE_TAGS)
    tags = rf"(?:{names})(?=[\s>])"
    return {
        "relevance": {
            "begin": rf"(<)({tags})((?:\s{_ATTRIBUTE_TEXT})?)(?<!/)(>)",
            "beginCaptures": {
                "1": {"name": _TAG},
                "2": {"name": _TAG_NAME},
                "3": {"patterns": [{"include": "#attributes"}]},
                "4": {"name": _TAG},
            },
            # The name the start tag matched: its attribute conditions say
            # nothing about an end tag.
            "end": r"(</)(\2)\s*(>)",
            "endCaptures": {
                "1": {"name": _TAG},
                "2": {"name": _TAG_NAME},
                "3": {"name": _TAG},
            },
            "contentName": "meta.embedded.block.bigfix-relevance",
            "patterns": [
                {"include": "#cdata-relevance"},
                {"include": "#entity"},
                {"include": "#relevance-body"},
            ],
        },
        "relevance-body": _relevance_body(),
        "cdata-relevance": _cdata([{"include": "#relevance-body"}]),
    }


def bes_grammar() -> dict[str, Any]:
    """BES XML: VS Code's XML grammar, with the bodies the extractor reads embedded.

    Windows-Shell ``<ActionScript>`` (or one with no MIMEType) is ActionScript;
    any other MIMEType is another language and stays XML. ``<Relevance>``,
    ``<Property>`` and ``<SuccessCriteria Option="CustomRelevance">`` bodies
    are relevance. Session relevance in ``<Description>`` HTML is not colored.
    """
    mimetypes = "|".join(re.escape(mimetype) for mimetype in sorted(_ACTIONSCRIPT_MIMETYPES))
    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "BigFix BES XML",
        "scopeName": BES_SCOPE,
        "comment": "Generated by tools/generate_tmlanguage.py; do not edit by hand.",
        "patterns": [
            {"include": "#actionscript"},
            {"include": "#relevance"},
            {"include": "text.xml"},
        ],
        "repository": {
            **_actionscript_element(mimetypes),
            **_relevance_element(),
            "attributes": {"patterns": _attributes()},
            "entity": {
                "name": "constant.character.entity.xml",
                "match": r"&(?:[A-Za-z_:][\w:.-]*|#[0-9]+|#x[0-9A-Fa-f]+);",
            },
        },
    }


def render() -> dict[Path, dict[str, Any]]:
    """Every generated grammar, keyed by its path relative to the repository."""
    return {
        RELEVANCE_PATH: relevance_grammar(),
        MARKDOWN_PATH: markdown_injection(),
        ACTIONSCRIPT_PATH: actionscript_grammar(),
        BES_PATH: bes_grammar(),
    }


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
