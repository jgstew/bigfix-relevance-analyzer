#!/usr/bin/env python3
"""Assert that two implementations produce byte-identical output.

Every optimisation in this package is supposed to be invisible. This script is
how that is checked: it runs two callables -- a *baseline* and a *candidate* --
over every relevance statement the repository knows about, and fails on the
first difference.

Run it with both arms bound to the same function and it must pass; that is the
self-test, and `--self-test` does exactly that.

    python tools/perf/parity.py                # analyze, baseline vs candidate
    python tools/perf/parity.py --self-test    # both arms the same: must pass
    python tools/perf/parity.py --arm tokenize

Why compare *serialized strings* rather than parsed structures: `json.loads`
normalises `1` and `1.0` to the same object, so a candidate that changed a
field's type would slip through. `tools/playground-wasm/parity-test/
test_parity.mjs` makes the same argument for the same reason.

The corpus readers are imported from the test suite rather than reimplemented.
There is one corpus and it should have one reader; `tests/test_perf_tools.py`
asserts that this module really does reuse them.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "tests"))

from test_examples import corpus_files  # noqa: E402
from test_parser_corpus import corpus_cases  # noqa: E402

from bigfix_relevance_analyzer.analyzer import analyze  # noqa: E402
from bigfix_relevance_analyzer.extract import extract_relevance_from_file  # noqa: E402
from bigfix_relevance_analyzer.nodes import to_sexpr  # noqa: E402
from bigfix_relevance_analyzer.parser import ParseError, parse  # noqa: E402
from bigfix_relevance_analyzer.tokenizer import tokenize  # noqa: E402

Arm = Callable[[str], str]


def statements(extra: Path | None = None) -> Iterator[tuple[str, str]]:
    """Every relevance statement available, as ``(id, text)``.

    The two in-repo sources fail differently, so both are used: the
    ``.rlvcorpus`` records are small and deliberately include the malformed
    ones (a candidate that only breaks on an unterminated string must still be
    caught), while the example files are production-shaped.

    ``extra`` points at a checkout of real content -- a directory tree of
    ``.bes`` and friends -- and adds every statement extraction finds in it.
    It is off by default and no test passes it: the committed suite has to run
    on a machine that does not have that checkout. Pass it by hand, with
    ``--extra-corpus``, when a change deserves a wider net than 284 statements.
    """
    for case in corpus_cases():
        yield case.id, case.source
    for path in corpus_files():
        relative = path.relative_to(_ROOT / "tests" / "examples")
        # The id has to be unique or a failure report cannot be acted on, and
        # neither the file name nor the line number is enough on its own: two
        # example files share a name across directories, and one line can carry
        # several relevance sites (a `<Relevance>` and an action script's
        # `{...}` substitution, say). Path plus ordinal is unique by
        # construction; the line stays in because it is what you grep for.
        for index, site in enumerate(extract_relevance_from_file(path)):
            yield f"{relative}#{index}@L{site.line}", site.text
    if extra is None:
        return
    for path in sorted(p for p in extra.rglob("*") if p.is_file()):
        if ".git" in path.parts:
            continue
        try:
            sites = extract_relevance_from_file(path)
        except Exception:
            # An outside tree is not curated the way `tests/examples` is: it
            # holds binaries, half-migrated XML and whatever else. A file that
            # will not even open is not a parity result, so skip it rather than
            # let it mask the comparison this script exists to make.
            continue
        for index, site in enumerate(sites):
            yield f"{extra.name}/{path.relative_to(extra)}#{index}@L{site.line}", site.text


# ---------------------------------------------------------------------------
# Arms: each renders one statement to a string that must match exactly.
# ---------------------------------------------------------------------------


def arm_analyze(text: str) -> str:
    return json.dumps(analyze(text).to_dict(), sort_keys=True, default=str)


def arm_parse(text: str) -> str:
    try:
        return to_sexpr(parse(text))
    except ParseError as error:
        return f"ERROR line {error.line} column {error.column}: {error.message}"


def arm_tokenize(text: str) -> str:
    stream = list(tokenize(text))
    # The roundtrip guarantee is checked per arm rather than by comparing the
    # two arms: a bug that both arms share would produce no difference at all.
    rejoined = "".join(token.text for token in stream)
    if rejoined != text:
        raise AssertionError(f"roundtrip broken: {rejoined!r} != {text!r}")
    return repr([(t.kind.value, t.text, t.offset, t.line, t.column) for t in stream])


ARMS: dict[str, Arm] = {
    "analyze": arm_analyze,
    "parse": arm_parse,
    "tokenize": arm_tokenize,
}

# Populated only while an optimisation is in flight: map an arm name to the
# *candidate* implementation, usually a `_legacy` twin kept beside the new code
# for the life of the pull request. Both the twin and its entry here are
# deleted when that lands, which is why this is empty on `main` -- and why an
# empty registry is a pass, not an error. The recorded run is the artifact.
CANDIDATES: dict[str, Arm] = {}


def check(baseline: Arm, candidate: Arm, extra: Path | None = None) -> tuple[int, list[str]]:
    """Run both arms over every statement; return ``(checked, failures)``."""
    checked = 0
    failures: list[str] = []
    for case_id, text in statements(extra):
        checked += 1
        want, got = baseline(text), candidate(text)
        if want != got:
            failures.append(
                f"{case_id}\n  source:    {text!r}\n  baseline:  {want!r}\n  candidate: {got!r}"
            )
    return checked, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", default="analyze", choices=sorted(ARMS))
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="bind both arms to the same function; a failure means this script is broken",
    )
    parser.add_argument("--show", type=int, default=3, help="how many differences to print")
    parser.add_argument(
        "--extra-corpus",
        type=Path,
        default=None,
        metavar="DIR",
        help="also check statements found in this content tree (e.g. a bigfix-content checkout)",
    )
    args = parser.parse_args(argv)
    if args.extra_corpus is not None and not args.extra_corpus.is_dir():
        parser.error(f"--extra-corpus: not a directory: {args.extra_corpus}")

    baseline = ARMS[args.arm]
    candidate = None if args.self_test else CANDIDATES.get(args.arm)
    if candidate is None:
        # No candidate registered (or --self-test): compare the arm with
        # itself. That still exercises every statement and every arm-internal
        # assertion -- the tokenize arm's roundtrip check, for one -- so it is
        # a real check of the corpus, not a no-op.
        candidate = baseline
        label = f"{args.arm} (self-test)"
    else:
        label = f"{args.arm} (baseline vs candidate)"

    checked, failures = check(baseline, candidate, args.extra_corpus)
    if failures:
        print(f"PARITY FAILED: {len(failures)} of {checked} differ [{label}]")
        for failure in failures[: args.show]:
            print(failure)
        if len(failures) > args.show:
            print(f"... and {len(failures) - args.show} more")
        return 1
    print(f"parity ok: {checked} statements identical [{label}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
