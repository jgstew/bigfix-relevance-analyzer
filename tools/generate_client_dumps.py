#!/usr/bin/env python3
"""Capture the five inspector dumps from a local BigFix ``QnA`` binary.

``tools/generate_inspector_data.py`` builds the shipped tables *from* the dumps
in ``tests/examples/relevance_inspectors/``. This script produces those dumps in
the first place, so a platform or a client version can be re-captured instead of
being transcribed by hand.

Usage::

    python tools/generate_client_dumps.py --qna /path/to/QnA --context ubuntu
    python tools/generate_client_dumps.py --qna C:\\qna\\qna.exe --context windows

Output goes to the dump folder as ``client_relevance_{category}_{context}.txt``,
which is what ``generate_inspector_data.py`` reads. ``--out`` writes elsewhere
(review first, then copy in) and ``--stdout`` prints without writing anything.

The queries are the enriched, tab-delimited ones documented under "Producing the
enriched format" in the dump folder's README, verbatim. They are the same text
in both dialects; only this script's transport is client-specific.

Two traps, both of which produce plausible-looking output when missed
-------------------------------------------------------------------
1. **The prompt has no trailing newline.** Reading a query from a pipe, ``QnA``
   writes ``Q: `` and then answers on that same line, so the first answer of
   every query arrives as ``Q: A: ...``. Filtering on ``startswith("A: ")``
   silently drops exactly one row per category -- a table that is one short
   everywhere and wrong nowhere obvious.
2. **The output is percent-encoded.** ``mod`` comes back as ``%25``, tab as
   ``%09``. Undecoded, the operator tables gain a second, bogus ``%25``
   operator; that defect reached three committed Linux dumps once already.

Both are handled by :func:`answers`, which is pure and covered by
``tests/test_generate_client_dumps.py`` over captured fixture text -- the parts
that need a real engine are the parts that stay untested.

Completeness
------------
Each category's row count is checked against the engine's own
``number of <category>``. That is the check that catches trap 1: a dropped row
is invisible in the output but not in the count. ``--no-verify`` skips it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
DUMPS = REPO_ROOT / "tests" / "examples" / "relevance_inspectors"

TAB = "character 9"

# Category -> (the enriched capture query, the query that counts its rows).
# Column order matches "Enriched columns" in the dump README; `|` supplies the
# empty cell for "no direct object", "no index", "root type", "unknown size".
QUERIES: dict[str, str] = {
    "properties": (
        f"(it as string & {TAB} & singular name of it & {TAB} & plural name of it"
        f' & {TAB} & usual name of it & {TAB} & (if multivalued of it then "1" else "0")'
        f" & {TAB} & name of result type of it"
        f' & {TAB} & (name of direct object type of it | "")'
        f' & {TAB} & (name of index type of it | "")) of properties'
    ),
    "casts": (
        f"(it as string & {TAB} & name of it & {TAB} & name of operand type of it"
        f" & {TAB} & name of result type of it) of casts"
    ),
    "binary_operators": (
        f"(it as string & {TAB} & name of it & {TAB} & symbol of it"
        f" & {TAB} & name of left operand type of it"
        f" & {TAB} & name of right operand type of it"
        f" & {TAB} & name of result type of it) of binary operators"
    ),
    "unary_operators": (
        f"(it as string & {TAB} & name of it & {TAB} & symbol of it"
        f" & {TAB} & name of operand type of it"
        f" & {TAB} & name of result type of it) of unary operators"
    ),
    "types": (
        f'(name of it & {TAB} & (name of parent of it | "")'
        f' & {TAB} & ((size of it as string) | "")) of types'
    ),
}

COUNTS: dict[str, str] = {
    "properties": "number of properties",
    "casts": "number of casts",
    "binary_operators": "number of binary operators",
    "unary_operators": "number of unary operators",
    "types": "number of types",
}


class QnaError(RuntimeError):
    """The engine answered with an error, or could not be run at all."""


def answers(output: str) -> list[str]:
    """The answer rows in one ``QnA`` transcript, decoded.

    Handles both traps in the module docstring: the ``Q: `` prompt fused onto
    the first answer, and percent-encoding. ``T:`` timing lines and ``I:``
    notices are dropped; an ``E:`` line raises, because a partial table that
    looks complete is worse than no table.
    """
    rows: list[str] = []
    for raw in output.splitlines():
        line = raw.removeprefix("Q: ")  # trap 1: the prompt has no newline
        if line.startswith("E: "):
            raise QnaError(line.removeprefix("E: "))
        if line.startswith("A: "):
            rows.append(unquote(line.removeprefix("A: ")))  # trap 2
    return rows


def ask(qna: Path, query: str, timeout: float = 300.0) -> list[str]:
    """Put one query to ``QnA`` and return its answer rows."""
    try:
        # The binary is the path the caller passed; nothing here is shell-parsed.
        completed = subprocess.run(
            [str(qna)],
            input=f"{query}\n",
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except OSError as error:
        raise QnaError(f"could not run {qna}: {error}") from error
    if completed.returncode != 0:
        raise QnaError(f"{qna} exited {completed.returncode}: {completed.stderr.strip()}")
    return answers(completed.stdout)


def expected_count(rows: Sequence[str]) -> int:
    """The single integer a ``number of ...`` query answered with."""
    if len(rows) != 1 or not rows[0].strip().isdigit():
        raise QnaError(f"expected one integer, got {list(rows)!r}")
    return int(rows[0].strip())


def capture(qna: Path, category: str, *, verify: bool = True) -> list[str]:
    """One category's rows, checked against the engine's own count."""
    rows = ask(qna, QUERIES[category])
    if verify:
        total = expected_count(ask(qna, COUNTS[category]))
        if len(rows) != total:
            raise QnaError(
                f"{category}: captured {len(rows)} rows but the engine reports {total}"
                " -- one short usually means the `Q: ` prompt ate the first answer"
            )
    return rows


def render(rows: Iterable[str]) -> str:
    """The dump file's text: one row per line, trailing newline, LF endings."""
    return "".join(f"{row}\n" for row in rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--qna", type=Path, required=True, help="path to the QnA binary")
    parser.add_argument(
        "--context",
        required=True,
        help="platform this capture is from, e.g. `windows` -- becomes part of the filename",
    )
    parser.add_argument(
        "--out", type=Path, default=DUMPS, help=f"directory to write into (default: {DUMPS})"
    )
    parser.add_argument("--stdout", action="store_true", help="print instead of writing files")
    parser.add_argument(
        "--no-verify", action="store_true", help="skip the row-count check against the engine"
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(QUERIES),
        help="capture only this category (repeatable; default: all five)",
    )
    args = parser.parse_args(argv)

    categories = args.category or sorted(QUERIES)
    for category in categories:
        try:
            rows = capture(args.qna, category, verify=not args.no_verify)
        except QnaError as error:
            print(f"{category}: {error}", file=sys.stderr)
            return 1
        text = render(rows)
        name = f"client_relevance_{category}_{args.context}.txt"
        if args.stdout:
            print(f"=== {name} ({len(rows)} rows) ===")
            print(text, end="")
            continue
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {name} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
