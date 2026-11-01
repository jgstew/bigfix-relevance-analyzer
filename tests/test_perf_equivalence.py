"""Pin everything a consumer reads from the analyzer, so an optimisation cannot move it.

#199 makes the per-statement hot paths faster: the type checker's row lookups,
the tokenizer, the complexity pass, enum hashing. Every one of those changes is
supposed to be invisible. ``tools/perf/parity.py`` checks that by hand while a
change is in flight; this is the committed version of the same promise, so a
later change that breaks it fails CI rather than waiting for someone to run a
script.

For every statement in the repository's fixtures -- the ``.rlvcorpus`` records,
malformed ones included, and every site extracted from ``tests/examples`` -- it
records a digest of:

* ``analyze`` -- :meth:`RelevanceAnalysis.to_dict` with no dialect forced, plus
  ``resolved_dialect`` and ``dialect_assumed``, which ``to_dict`` does not carry;
* ``analyze/site`` -- the same with the dialect extraction worked out, which is
  what the lint hook and the LSP run (examples only);
* ``analyze/<platform>`` -- the same narrowed to one client platform, so the
  platform half of :meth:`TypeEnvironment.visible` is pinned too;
* ``dialect_fit`` -- dialects, basis and the two exclusive-reference lists;
* ``highlight`` -- every span, start, end and kind;
* ``tokens`` -- the whole token stream, positions included.

and, per example file, a digest of the lint report.

Digests rather than the payloads themselves: the full payloads run to megabytes,
and ``tests/golden/analysis_payload.json`` already pins the payload's *shape*
readably. What this file adds is breadth. When it fails it names the statement
and the field; ``python tools/perf/parity.py`` with the previous implementation
registered as a candidate shows the actual difference.

The baseline was recorded from ``main`` at 1.43.0, before any of #199's changes,
and is stable across hash seeds (checked by generating it under two). Regenerate
it only for a change that *means* to move output, and then only from a tree
that does nothing else:

    UPDATE_GOLDEN=1 pytest tests/test_perf_equivalence.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from _corpus import EXAMPLES, corpus_cases, corpus_files, extracted_sites
from _helpers import golden_text

from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.dialect import Dialect, dialect_fit
from bigfix_relevance_analyzer.highlight import highlight
from bigfix_relevance_analyzer.lint import LintConfig, lint_paths_to_dict
from bigfix_relevance_analyzer.tokenizer import tokenize

GOLDEN = Path(__file__).parent / "golden" / "perf_equivalence.json"

# One client platform is enough to exercise the `platform is not None` branch of
# every visibility check; windows has the most rows, so the most to get wrong.
_PLATFORM = "windows"


def _digest(value: Any) -> str:
    # `default=str` for the enums and frozensets a dataclass repr would carry;
    # `sort_keys` so a dict's insertion order is not part of the pin.
    text = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _analysis(text: str, dialect: Dialect | None = None, platform: str | None = None) -> str:
    result = analyze(text, dialect, platform)
    resolved = result.resolved_dialect
    return _digest(
        {
            "payload": result.to_dict(),
            "resolved_dialect": None if resolved is None else resolved.value,
            "dialect_assumed": result.dialect_assumed,
        }
    )


def _statement(text: str, site_dialect: Dialect | None) -> dict[str, str]:
    fit = dialect_fit(text)
    record = {
        "analyze": _analysis(text),
        f"analyze/{_PLATFORM}": _analysis(text, Dialect.CLIENT, _PLATFORM),
        "dialect_fit": _digest(
            {
                "dialects": sorted(dialect.value for dialect in fit.dialects),
                "basis": fit.basis,
                "client_only": list(fit.client_only),
                "session_only": list(fit.session_only),
            }
        ),
        "highlight": _digest([(s.start, s.end, s.kind.value) for s in highlight(text)]),
        "tokens": _digest(
            [(t.kind.value, t.text, t.offset, t.line, t.column) for t in tokenize(text)]
        ),
    }
    if site_dialect is not None:
        record["analyze/site"] = _analysis(text, site_dialect)
    return record


def _snapshot() -> dict[str, Any]:
    statements: dict[str, dict[str, str]] = {}
    for case in corpus_cases():
        statements[f"corpus/{case.id}"] = _statement(case.source, None)
    ordinals: dict[Path, int] = {}
    for path, site in extracted_sites():
        index = ordinals[path] = ordinals.get(path, -1) + 1
        key = f"examples/{path.relative_to(EXAMPLES).as_posix()}#{index}@L{site.line}"
        statements[key] = _statement(site.text, site.dialect)
    lint = {
        path.relative_to(EXAMPLES).as_posix(): _digest(lint_paths_to_dict([path], LintConfig()))
        for path in corpus_files()
    }
    return {"statements": statements, "lint": lint}


def _differences(want: dict[str, Any], got: dict[str, Any], prefix: str = "") -> list[str]:
    found: list[str] = []
    for key in sorted(want.keys() | got.keys()):
        where = f"{prefix}{key}"
        if key not in got:
            found.append(f"{where}: missing")
        elif key not in want:
            found.append(f"{where}: not in the baseline")
        elif isinstance(want[key], dict) and isinstance(got[key], dict):
            found.extend(_differences(want[key], got[key], f"{where} / "))
        elif want[key] != got[key]:
            found.append(f"{where}: {want[key]} -> {got[key]}")
    return found


def test_output_is_identical_to_the_recorded_baseline() -> None:
    """Every finding, dialect, resolution, highlight span and token is unchanged."""
    actual = _snapshot()
    pinned = json.loads(golden_text(GOLDEN, json.dumps(actual, indent=1, sort_keys=True) + "\n"))
    differences = _differences(pinned, actual)
    assert not differences, f"{len(differences)} outputs moved:\n" + "\n".join(differences[:20])


def test_the_baseline_covers_both_corpora_and_every_lint_report() -> None:
    """A baseline over an empty corpus would pass anything; refuse that."""
    pinned = json.loads(GOLDEN.read_text(encoding="utf-8"))
    keys = pinned["statements"].keys()
    assert sum(key.startswith("corpus/") for key in keys) == len(corpus_cases())
    assert sum(key.startswith("examples/") for key in keys) == len(extracted_sites())
    assert len(pinned["lint"]) == len(corpus_files())
