#!/usr/bin/env python3
"""Regenerate ``src/bigfix_relevance_analyzer/reference/_prose.py`` from ``docs/reference``.

The authored half of the language reference is written as Markdown under
``docs/reference/`` -- prose is easier to write, review and diff as Markdown
than as string literals in a module. But the wheel packages ``src/`` only
(``[tool.hatch.build.targets.wheel]``), so anything the library must be able to
read at runtime has to *be* a module. This script does the embedding.

That is the same arrangement, for the same reason, as
``tools/generate_inspector_data.py`` and its dumps; ``tests/test_reference.py``
fails if the committed module and the Markdown have drifted, so the duplication
is generated and guarded rather than maintained by hand.

Usage::

    python tools/generate_reference_prose.py           # write the module
    python tools/generate_reference_prose.py --check    # exit 1 if out of date

Every ``*.md`` in ``docs/reference/`` is embedded, keyed by its stem upper-cased
-- ``client_relevance.md`` becomes ``CLIENT_RELEVANCE``. Adding a document means
dropping in a file and re-running this; the only code change is naming it in
:mod:`bigfix_relevance_analyzer.reference` if it should be a servable document
rather than shared prose.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs" / "reference"
TARGET = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "reference" / "_prose.py"

HEADER = '''"""Authored reference prose, embedded from ``docs/reference``. Do not edit by hand.

Regenerate with ``python tools/generate_reference_prose.py``;
``tests/test_reference.py`` fails if this module and the Markdown under
``docs/reference/`` disagree.

Edit the Markdown, not this file. The Markdown is the reviewable copy; this is
only how it reaches the wheel, which packages ``src/`` and nothing else.
"""

from __future__ import annotations

'''


def collect() -> dict[str, str]:
    """Every reference document, keyed by the constant name it will get."""
    documents: dict[str, str] = {}
    for path in sorted(DOCS.glob("*.md")):
        documents[path.stem.upper()] = path.read_text(encoding="utf-8")
    return documents


def render(documents: dict[str, str]) -> str:
    """The module source embedding ``documents``.

    Each document goes in as a single-quoted raw-ish literal built with
    ``repr``, not a triple-quoted block: the prose contains backslashes (Windows
    paths are the whole point of one section), backticks, and quote characters,
    and ``repr`` is the only escaping that is correct for all of them without
    this script having to reason about the content.
    """
    lines = [HEADER]
    lines.append(f"#: Document keys, in the order {Path(__file__).name} found them.\n")
    lines.append("NAMES: tuple[str, ...] = (\n")
    lines.extend(f'    "{name}",\n' for name in documents)
    lines.append(")\n\n")
    for name, text in documents.items():
        lines.append(f"{name}: str = {text!r}\n\n")
    lines.append("#: Every embedded document, keyed as in :data:`NAMES`.\n")
    lines.append("DOCUMENTS: dict[str, str] = {\n")
    lines.extend(f'    "{name}": {name},\n' for name in documents)
    lines.append("}\n")
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the committed module is out of date, instead of writing it",
    )
    args = parser.parse_args(argv)

    if not DOCS.is_dir():
        print(f"no such directory: {DOCS}", file=sys.stderr)
        return 2

    documents = collect()
    if not documents:
        print(f"no *.md found in {DOCS}", file=sys.stderr)
        return 2

    source = render(documents)
    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.is_file() else ""
        if current != source:
            print(
                f"{TARGET.relative_to(REPO_ROOT)} is out of date -- "
                "run `python tools/generate_reference_prose.py` "
                "(edit the Markdown in docs/reference, not the module)",
                file=sys.stderr,
            )
            return 1
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(source, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(REPO_ROOT)}: {len(documents)} document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
