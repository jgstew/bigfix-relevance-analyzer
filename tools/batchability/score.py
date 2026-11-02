"""Score :func:`~bigfix_relevance_analyzer.batchability` against what qna did.

Not shipped, and needs no qna: the outcomes are committed beside it. Run from
the repository root, and commit the result when it changes on purpose::

    python tools/batchability/score.py > tools/batchability/scores.md

``tests/test_batchability_scores.py`` regenerates this in memory and compares,
so a change that moves a verdict on the corpus shows up as a diff to review
(``UPDATE_GOLDEN=1`` rewrites it, like every golden in the suite).

**Actual outcome**, per (statement, host), in ``outcomes.jsonl``:

- ``one`` -- exactly one answer, no error, and tupled with a sentinel it came
  back as exactly one answer that splits on ``", "`` into the statement's answer
  and the sentinel, with no part holding ``,``, ``(`` or ``)``. Batchable.
- ``error`` / ``empty`` / ``plural`` -- what went wrong on its own;
  ``env-error`` when the container itself was the cause (no SMBIOS tables,
  no RPM inspector), which no real endpoint shares and which is left out.
- ``split`` -- one clean answer, but not one a tuple can carry.

Rows are split into a **dev** half (even ids), which the rules were tuned on,
and a **holdout** half (odd ids), which they were not.
"""

from __future__ import annotations

import collections
import json
import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from bigfix_relevance_analyzer import analyze_relevance, batchability
from bigfix_relevance_analyzer.nodes import Binary, Exists, NumberOf, Unary

HERE = Path(__file__).resolve().parent

OUTCOMES = ("one", "error", "env-error", "empty", "plural", "split")

# Operators that answer one boolean from singular operands.
_BOOLEAN_OPS = frozenset(
    {"=", "!=", "<", ">", "<=", ">=", "and", "or", "contains", "starts with", "ends with"}
    | {"does not contain", "does not start with", "does not end with", "is", "is not"}
    | {"is equal to", "is not equal to", "is greater than", "is less than"}
)

Predictor = Callable[[str, str], bool]


def _boolean_shape(text: str) -> bool:
    """The shape rule alone: the root is `exists`, `not exists`, `number of`,
    a comparison or `and` / `or` / `not` -- what applicability relevance
    usually is -- with no type checking at all."""
    match analyze_relevance(text).node:
        case Exists() | NumberOf():
            return True
        case Unary(op=op):
            return op.lower() == "not"
        case Binary(op=op):
            return op.lower() in _BOOLEAN_OPS
        case _:
            return False


PREDICTORS: dict[str, Predictor] = {
    "classifier (platform-agnostic)": lambda text, platform: batchability(text).safe,
    "classifier (platform known)": lambda text, platform: (
        batchability(text, platform=platform).safe
    ),
    "plurality == SINGULAR only": lambda text, platform: (
        batchability(text).plurality.value == "singular"
    ),
    "shape only (exists / number of / comparison / and-or-not at the root)": (
        lambda text, platform: _boolean_shape(text)
    ),
}


def _read_jsonl(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _precision(tp: int, fp: int) -> str:
    return f"{tp / (tp + fp):.1%}" if tp + fp else "n/a"


def report(corpus: Iterable[dict[str, str]], outcomes: Iterable[dict[str, str]]) -> str:
    """The whole of ``scores.md``."""
    texts = {row["id"]: row["text"] for row in corpus}
    rows = list(outcomes)
    hosts = list(dict.fromkeys(row["host"] for row in rows))
    out: list[str] = ["# Batchability scores", ""]

    out += ["## Actual outcomes per host", ""]
    out += ["| host | qna | total | " + " | ".join(OUTCOMES) + " |"]
    out += ["|---|---|---:|" + "---:|" * len(OUTCOMES)]
    for host in hosts:
        mine = [row for row in rows if row["host"] == host]
        counts = collections.Counter(row["outcome"] for row in mine)
        cells = " | ".join(str(counts[outcome]) for outcome in OUTCOMES)
        out.append(f"| {host} | {mine[0]['qna']} | {len(mine)} | {cells} |")

    rows = [row for row in rows if row["outcome"] != "env-error"]
    verdicts: dict[tuple[str, str, str], bool] = {}

    def predicted(name: str, row: dict[str, str]) -> bool:
        key = (name, row["id"], row["platform"])
        if key not in verdicts:
            verdicts[key] = PREDICTORS[name](texts[row["id"]], row["platform"])
        return verdicts[key]

    out += ["", '## Precision of a "safe to batch" verdict', ""]
    out += [
        (
            "Container environment errors (no SMBIOS, Rocky's RPM symlink) are left out "
            "of every count below; the raw counts are in the table above."
        ),
        "",
        "| predictor | half | host | predicted safe | actually one | precision | recall |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    false_safe: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for name in PREDICTORS:
        for half, parity in (("dev", 0), ("holdout", 1), ("all", None)):
            for host in [*hosts, "all hosts"]:
                tp = fp = positives = 0
                for row in rows:
                    if host != "all hosts" and row["host"] != host:
                        continue
                    if parity is not None and int(row["id"][1:]) % 2 != parity:
                        continue
                    one = row["outcome"] == "one"
                    positives += one
                    if predicted(name, row):
                        tp += one
                        fp += not one
                        if not one and half == "all" and host == "all hosts":
                            false_safe[name].append(row)
                recall = f"{tp / positives:.1%}" if positives else "n/a"
                out.append(
                    f"| {name} | {half} | {host} | {tp + fp} | {tp} | {_precision(tp, fp)} "
                    f"| {recall} |"
                )

    out += ["", "## Verdicts against actual outcomes (platform known, all hosts)", ""]
    table: collections.Counter[tuple[str, str]] = collections.Counter()
    for row in rows:
        kind = batchability(texts[row["id"]], platform=row["platform"]).kind.value
        table[(kind, row["outcome"])] += 1
    shown = [outcome for outcome in OUTCOMES if outcome != "env-error"]
    out += ["| verdict | " + " | ".join(shown) + " |", "|---|" + "---:|" * len(shown)]
    for kind in ("safe", "split-risk", "plural-risk", "unknown", "error-risk"):
        out.append(f"| {kind} | " + " | ".join(str(table[(kind, o)]) for o in shown) + " |")

    for name, items in false_safe.items():
        if not name.startswith("classifier"):
            continue
        out += ["", f'## False "safe": {name} ({len(items)})', ""]
        for row in items:
            error = row.get("error", "")
            out.append(
                f"- {row['host']}: {row['outcome']} `{row['id']}` "
                f"`{texts[row['id']][:120]}` {error}".rstrip()
            )
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    corpus = _read_jsonl(HERE / "corpus.jsonl")
    outcomes = _read_jsonl(HERE / "outcomes.jsonl")
    sys.stdout.write(report(corpus, outcomes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
