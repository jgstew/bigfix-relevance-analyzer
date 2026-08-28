#!/usr/bin/env python3
"""Regenerate ``src/bigfix_relevance_analyzer/_inspector_data.py`` from the dumps.

The inspector dumps live under ``tests/examples/relevance_inspectors/`` and are
test-only reference data -- the wheel packages ``src/`` only, so a table the
library needs at runtime has to be embedded in a module. This script does the
embedding; ``tests/test_inspector_data.py`` fails if the committed module and
the dumps have drifted, so the duplication is generated and guarded rather than
maintained by hand.

Usage::

    python tools/generate_inspector_data.py          # write the module
    python tools/generate_inspector_data.py --check   # exit 1 if out of date

Dump filenames carry their own provenance, as
``{dialect}_relevance_{category}[_{context}].txt``:

* ``dialect`` is ``client`` or ``session``.
* ``category`` is one of the introspection categories BigFix exposes over
  itself -- ``properties``, ``casts``, ``binary_operators``,
  ``unary_operators``, ``types``.
* ``context`` is optional, naming the platform or session surface the dump came
  from (``windows``, ``console``, ...). Omit it when only one capture exists for
  that dialect and category.

So ``client_relevance_properties_windows.txt`` and
``session_relevance_casts.txt`` are both well-formed, and adding a client-side
cast dump means dropping in ``client_relevance_casts_windows.txt`` and
re-running this script -- no code change.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DUMPS = REPO_ROOT / "tests" / "examples" / "relevance_inspectors"
TARGET = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "_inspector_data.py"

DIALECTS = ("client", "session")

# Longest first, so `unary_operators` is not read as category `unary` with
# context `operators`.
CATEGORIES = (
    "binary_operators",
    "unary_operators",
    "properties",
    "casts",
    "types",
)


def parse_dump_filename(filename: str) -> tuple[str, str, str]:
    """Split a dump filename into ``(dialect, category, context)``.

    ``context`` is the empty string when the filename carries none.
    """
    stem = filename.removesuffix(".txt")
    for dialect in DIALECTS:
        prefix = f"{dialect}_relevance_"
        if not stem.startswith(prefix):
            continue
        rest = stem[len(prefix) :]
        for category in CATEGORIES:
            if rest == category:
                return dialect, category, ""
            if rest.startswith(f"{category}_"):
                return dialect, category, rest[len(category) + 1 :]
        raise ValueError(f"{filename}: no known category in {rest!r}")
    raise ValueError(f"{filename}: does not start with a known dialect")


def source_label(dialect: str, context: str) -> str:
    """The name this dump's rows are attributed to, e.g. ``client:windows``."""
    return f"{dialect}:{context}" if context else dialect


def _row_key(line: str) -> str:
    """The identity a line is merged on: everything before its first tab.

    A dump line is either bare (``signature: type``, no tabs) or that same
    text followed by tab-separated enrichment columns from a richer capture
    (see ``session_relevance_properties_rest_api.txt``). Two dumps naming the
    same inspector must merge into one row even when only one of them was
    captured with enrichment -- keying on the pre-tab text is what makes that
    possible instead of the bare and enriched spellings splitting into two.
    """
    return line.partition("\t")[0]


def collect() -> tuple[tuple[str, ...], dict[str, dict[str, tuple[int, str]]]]:
    """Read every dump into ``(source_labels, {category: {key: (mask, line)}})``.

    A row is stored once per category no matter how many dumps hold it; which
    dumps those were is recorded as a bitmask over ``source_labels``. When
    dumps disagree on enrichment for the same row, the line with the most
    tab-separated columns wins as the stored text -- the richer capture is
    strictly more informative, never contradictory, since enrichment only
    adds columns a bare line lacks.
    """
    by_source: dict[tuple[str, str], list[str]] = {}
    for path in sorted(DUMPS.glob("*.txt")):
        dialect, category, context = parse_dump_filename(path.name)
        label = source_label(dialect, context)
        key = (category, label)
        if key in by_source:
            raise ValueError(f"two dumps claim category {category} of {label}")
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            # An empty dump is a placeholder for a capture nobody has made yet.
            # Registering it would add a source bit that no row ever sets,
            # which reads as "captured, found nothing" -- the opposite of true.
            print(f"skipping empty dump {path.name}", file=sys.stderr)
            continue
        by_source[key] = lines

    labels = tuple(sorted({label for _category, label in by_source}))
    bit = {label: 1 << index for index, label in enumerate(labels)}

    tables: dict[str, dict[str, tuple[int, str]]] = defaultdict(dict)
    for (category, label), lines in sorted(by_source.items()):
        for line in lines:
            row_key = _row_key(line)
            mask, chosen = tables[category].get(row_key, (0, line))
            if line.count("\t") > chosen.count("\t"):
                chosen = line
            tables[category][row_key] = (mask | bit[label], chosen)
    return labels, tables


def render(labels: tuple[str, ...], tables: dict[str, dict[str, tuple[int, str]]]) -> str:
    """Render the generated module source."""
    out = [
        '"""Inspector tables, generated from the dumps. Do not edit by hand.',
        "",
        "Regenerate with ``python tools/generate_inspector_data.py``;",
        "``tests/test_inspector_data.py`` fails if this file and the dumps in",
        "``tests/examples/relevance_inspectors/`` disagree.",
        "",
        "Each table is one row per line, ``<source mask in hex>\\t<dump line>``.",
        "The mask indexes :data:`SOURCES`, recording which dumps defined the row --",
        "a row present in every client platform and no session surface is client-only",
        "vocabulary, and one present in both dialects is shared.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "SOURCES: tuple[str, ...] = (",
    ]
    out += [f'    "{label}",' for label in labels]
    out += [")", ""]

    for category in sorted(tables):
        rows = tables[category]
        out.append(f"# {len(rows)} rows")
        out.append(f'{category.upper()}: str = """\\')
        out += [f"{mask:x}\t{line}" for _key, (mask, line) in sorted(rows.items())]
        out.append('"""')
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if the committed module is out of date",
    )
    args = parser.parse_args()

    rendered = render(*collect())
    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != rendered:
            print(f"{TARGET.relative_to(REPO_ROOT)} is out of date", file=sys.stderr)
            return 1
        print(f"{TARGET.relative_to(REPO_ROOT)} is up to date")
        return 0

    TARGET.write_text(rendered, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
