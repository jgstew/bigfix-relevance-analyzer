#!/usr/bin/env python3
"""Regenerate ``src/bigfix_relevance_analyzer/_actionscript_keywords.py`` from the schclass.

The source is the BigFix console's own ActionScript lexical grammar, as
vendored by pre-commit-bigfix (``pre_commit_bigfix/schclass_data/``): every
``token:tag`` value in ``ExpandedActionScript.schclass`` plus
``bigfix_overrides.schclass``, lowercased. That is not vendored again here --
the result is a small word list, so only the list is embedded, and this script
reads a pre-commit-bigfix checkout to rebuild it.

A command word is kept only if it can never be relevance:

* a single word -- a multi-word verb's first word is often an inspector
  (`action ...`, `setting ...`), and the parser reads those as ordinary
  inspector phrases;
* not an inspector name in any dialect (`parameter`, `setting`, `wait`, ...
  are everyday relevance);
* parsed by our parser as a name at all -- `if` and `else` are relevance
  grammar words, already a parse error on their own.

Usage::

    python tools/generate_actionscript_keywords.py --schclass-dir DIR          # write the module
    python tools/generate_actionscript_keywords.py --schclass-dir DIR --check  # exit 1 if stale

where ``DIR`` is ``pre_commit_bigfix/schclass_data`` in a pre-commit-bigfix checkout.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "_actionscript_keywords.py"
SCHCLASS_FILES = ("ExpandedActionScript.schclass", "bigfix_overrides.schclass")

# `token:tag = 'download now as'`; one value per line in both files.
_TOKEN_TAG = re.compile(r"^\s*token:tag\s*=\s*'([^']*)'", re.MULTILINE)


def command_words(schclass_dir: Path) -> set[str]:
    """Every ActionScript command word the grammar defines, lowercased."""
    words: set[str] = set()
    for name in SCHCLASS_FILES:
        text = (schclass_dir / name).read_text(encoding="utf-8")
        words.update(tag.strip().lower() for tag in _TOKEN_TAG.findall(text))
    return words


def every_inspector_name() -> frozenset[str]:
    """Every spelling any inspector answers to, in any dialect.

    Wider than ``inspector_names()``, which indexes written phrases only: the
    singular of an aggregate (`set`, of `sets`) is a name too.
    """
    from bigfix_relevance_analyzer.inspectors import all_inspectors

    return frozenset(
        name
        for row in all_inspectors()
        for name in (row.name, row.singular_name, row.plural_name, row.usual_name, row.written_name)
        if name
    )


def keywords(schclass_dir: Path) -> list[str]:
    """The command words that can never be relevance, sorted."""
    from bigfix_relevance_analyzer.analyzer import analyze

    names = every_inspector_name()
    kept = []
    for word in sorted(command_words(schclass_dir)):
        if " " in word or word in names:
            continue
        report = analyze(f"exists {word}")
        if not report.parsed:
            continue  # a relevance grammar word, e.g. `if`
        kept.append(word)
    return kept


def render(words: list[str]) -> str:
    body = "".join(f'        "{word}",\n' for word in words)
    return (
        '"""ActionScript command words that are never relevance. Do not edit by hand.\n'
        "\n"
        "Regenerate with ``python tools/generate_actionscript_keywords.py``; see\n"
        "that script for how the list is derived, and ``tests/test_lint.py`` for\n"
        "the test pinning it against the inspector tables.\n"
        '"""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from typing import Final\n"
        "\n"
        f"# {len(words)} words\n"
        "ACTIONSCRIPT_KEYWORDS: Final = frozenset(\n"
        "    {\n"
        f"{body}"
        "    }\n"
        ")\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate the ActionScript keyword list.")
    parser.add_argument("--schclass-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="exit 1 if the module is stale")
    args = parser.parse_args(argv)
    rendered = render(keywords(args.schclass_dir))
    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != rendered:
            print(f"{TARGET} is out of date", file=sys.stderr)
            return 1
        return 0
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
