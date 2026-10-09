#!/usr/bin/env python3
"""Regenerate the ActionScript word lists from the console's schclass.

Two outputs, both committed:

* ``src/bigfix_relevance_analyzer/_actionscript_keywords.py``: the command
  words that can never be relevance (the lint guard, below);
* ``tools/data/actionscript_verbs.txt``: every command verb, for the VS Code
  ActionScript grammar (``tools/generate_tmlanguage.py``, issue #116). CI has
  no pre-commit-bigfix checkout, so the grammar generator reads this file.

The source is the BigFix console's own ActionScript lexical grammar, as
vendored by pre-commit-bigfix (``pre_commit_bigfix/schclass_data/``): every
``token:tag`` value in ``ExpandedActionScript.schclass`` plus
``bigfix_overrides.schclass``, lowercased. That is not vendored again here --
the result is a small word list, so only the list is embedded, and this script
reads a pre-commit-bigfix checkout to rebuild it.

For the lint guard, a command word is kept only if it can never be relevance:

* a single word -- a multi-word verb's first word is often an inspector
  (`action ...`, `setting ...`), and the parser reads those as ordinary
  inspector phrases;
* not an inspector name in any dialect (`parameter`, `setting`, `wait`, ...
  are everyday relevance);
* parsed by our parser as a name at all -- `if` and `else` are relevance
  grammar words, already a parse error on their own.

Usage::

    python tools/generate_actionscript_keywords.py --schclass-dir DIR          # write both
    python tools/generate_actionscript_keywords.py --schclass-dir DIR --check  # 1 if stale

where ``DIR`` is ``pre_commit_bigfix/schclass_data`` in a pre-commit-bigfix checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "_actionscript_keywords.py"
VERBS_TARGET = REPO_ROOT / "tools" / "data" / "actionscript_verbs.txt"
SCHCLASS_FILES = ("ExpandedActionScript.schclass", "bigfix_overrides.schclass")

# `token:tag = 'download now as'`; one value per line in both files.
_TOKEN_TAG = re.compile(r"^\s*token:tag\s*=\s*'([^']*)'", re.MULTILINE)


def command_words(schclass_dir: Path) -> set[str]:
    """Every ActionScript command word the grammar defines, lowercased."""
    words: set[str] = set()
    for name in SCHCLASS_FILES:
        text = (schclass_dir / name).read_text(encoding="utf-8")
        words.update(" ".join(tag.lower().split()) for tag in _TOKEN_TAG.findall(text))
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


def render_verbs(schclass_dir: Path) -> str:
    """Every command verb, one per line, under a header naming its source.

    The source files are named by content hash rather than by commit, so the
    check stays exact without failing on unrelated pre-commit-bigfix commits.
    """
    sources = "".join(
        f"# {name} sha256 {hashlib.sha256((schclass_dir / name).read_bytes()).hexdigest()}\n"
        for name in SCHCLASS_FILES
    )
    words = sorted(command_words(schclass_dir))
    return (
        "# Every BigFix ActionScript command verb, lowercased and single-spaced.\n"
        "# Do not edit by hand: regenerate with tools/generate_actionscript_keywords.py\n"
        "# from a jgstew/pre-commit-bigfix checkout (pre_commit_bigfix/schclass_data/):\n"
        f"{sources}"
        f"# {len(words)} verbs\n" + "".join(f"{word}\n" for word in words)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate the ActionScript word lists.")
    parser.add_argument("--schclass-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="exit 1 if either file is stale")
    args = parser.parse_args(argv)
    outputs = {
        TARGET: render(keywords(args.schclass_dir)),
        VERBS_TARGET: render_verbs(args.schclass_dir),
    }
    if args.check:
        stale = [
            target
            for target, rendered in outputs.items()
            if (target.read_text(encoding="utf-8") if target.exists() else "") != rendered
        ]
        for target in stale:
            print(f"{target} is out of date", file=sys.stderr)
        return 1 if stale else 0
    for target, rendered in outputs.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
