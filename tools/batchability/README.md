# Batchability measurement

How accurate `batchability()` (#225) is, and the data to check it again. Not
imported by the package and not in the wheel (the sdist carries `tools/`, as
it always has).

| file | what |
| --- | --- |
| `corpus.jsonl` | 545 client-relevance statements: every fixlet/analysis/group `relevance`, `analysis-property` and `global-property` this package extracts from [bigfix-content](https://github.com/jgstew/bigfix-content) `24dd4bd` as client relevance, deduplicated, at most 40 files per directory (seed 78), plus 70 hand-picked edge cases |
| `outcomes.jsonl` | what qna 11.0.7.61 did with each statement on each of four hosts (2,180 rows) |
| `score.py` | joins the classifier's verdicts with those outcomes |
| `scores.md` | its output, pinned by `tests/test_batchability_scores.py` |

```bash
python tools/batchability/score.py > tools/batchability/scores.md
```

## Where it came from

The classifier and this measurement were written in
[bigfix-remote-client-relevance](https://github.com/jgstew/bigfix-remote-client-relevance)'s
`tools/batchability/` (its #78, PR #97, released in 1.13.0) and moved here,
because that library must not depend on this one. The corpus is copied
verbatim. The outcomes were reduced from its raw results, which are not
public: they hold host names, paths and environment variables. Each row keeps
only the statement id, a public host label, the analyzer platform, the qna
version, the outcome, and, for an error, the first line of the engine's
message (cut at ` -- `, which is where a harness message starts adding paths).

## Method

Each statement was evaluated twice through the client library's
`evaluate_many`: alone, and as `((E), "bfrcr-78-sentinel")`. That is qna's
stdin batch path, except for most of the Windows corpus, which ran one qna per
expression (`--no-batch`) because the batch hung now and then over SSH (timing,
not content); the answers are the same. A statement's outcome is **`one`** (batchable)
when alone it answered exactly one value with no error, and the tuple came
back as exactly one answer that splits on `", "` into that value and the
sentinel, with no part holding `,`, `(` or `)`. Otherwise it is `error`,
`empty`, `plural` or `split`. `env-error` marks errors the container itself
causes (no SMBIOS/DMI tables; Rocky's image cannot set up the RPM inspector),
which no real endpoint shares and which are left out of the precision table.

Hosts: macOS 15.7 and Windows Server 2022 (x86_64, over SSH, BES agent
installed), Rocky Linux 9.3 and Ubuntu 26.04 (arm64 containers). The rules
were tuned on even-numbered statements only; odd ones are the holdout.

## Result

With the endpoint's platform passed, a `safe` verdict was right **97.0%** of
the time (846 of 872 (statement, host) pairs), catching 84.5% of what really
was batchable; 96.7% on the holdout half alone. Without the platform, 81.3%,
mostly from Windows-only inspectors on other platforms: of the 170
(statement, host) pairs the platform turns from a wrong `safe` into a right
refusal, 107 use a Windows-only inspector, 22 one only macOS and Windows have,
and 29 a Linux-only one. The analyzer's plurality alone (`SINGULAR`) scores 70.1%.

Of the 26 misses, 25 are errors the tables cannot foresee: 22 inspectors that
need the agent's client context (`No inspector context.` under qna, and under
Fast Query without `UseClientContext`), and 3 that the tables list for a
platform whose qna lacks them. The last is a Windows path with `(x86)` in it,
which a caller's split check refuses: a fallback, not a wrong answer.

## Caveats

- Counts are (statement, host) pairs: the 872 `safe` verdicts cover 306
  distinct statements.
- Ground truth is qna, tupled with one sentinel in last position. It does not
  exercise Fast Query itself, ten-item tuples, or an item that is not last;
  that a caller's split check holds for those rests on the display rule, which
  REST Fast Query matched in a handful of live queries.
- qna's context is the one Fast Query uses without `UseClientContext`; with
  it, the 22 `No inspector context.` misses would most likely answer.
- An evaluation that timed out counts as `error`, which can only lower the
  number of truly batchable statements (none did in these runs).
- Two rules were added in the move, after review: `not-client-relevance` (a
  session inspector) never fires on the corpus, and `property-without-object`
  (`exists size`) fires on one statement, which errored on all four hosts and
  was already refused. Neither moves a number.
