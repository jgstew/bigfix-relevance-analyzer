# QnA: the local relevance evaluator

`QnA` is the command-line client-relevance evaluator that ships with the BES
Agent. It answers **client relevance** against the machine it runs on, which
makes it the only way to check a client-relevance assumption without deploying
anything -- and therefore the authority this project defers to whenever a
grammar or semantics question is in doubt.

It is the same evaluator the Windows Fixlet Debugger drives from its QnA tab.
This document is about the command-line binary.

> **Expansive layer.** A tool guide rather than language reference: it has no
> `docs/reference/` counterpart, because an MCP consumer cannot run a local
> binary. The *findings* obtained with it belong in
> [`universal_relevance.md`](universal_relevance.md) and the dialect documents.
> See [`README.md`](README.md).

Everything below was observed on the binary itself, on macOS 14.6.1, BES Agent
build dated 2026-03-30, on 2026-08-31.

## Where it is

On macOS:

```
/Library/BESAgent/BESAgent.app/Contents/MacOS/QnA
```

Locate it rather than assuming a path on other platforms -- it ships inside the
agent's own install tree, which differs per platform, and this document has only
been checked on macOS. On Windows the same evaluator is normally reached through
the Fixlet Debugger GUI.

**It needs to run as root here.** Without sufficient privilege it does not
report a clean permission error; it aborts on an uncaught C++ exception while
reading agent state:

```
libc++abi: terminating due to uncaught exception of type FileIOError: ...
```

So a crash of that shape means "run me with more privilege", not "the expression
was wrong". This is also the one case that sets a non-zero exit status: 134,
i.e. `SIGABRT`.

## Usage

The binary's own `-help` output is authoritative:

```
qna [-t] [-showtypes] [-o output-file name] [zero or more input-file names]
     -t displays execution time in non-interactive mode
     -showtypes shows the result type of each query on a line prefixed by "I:"
     -help prints this message.
```

`-help` takes **one** dash. `--help` is not a flag, and because any unrecognised
argument is treated as an input filename you get `--help: No such file or
directory` rather than a usage error. The same is true of every flag guess: an
unknown one silently becomes a missing file.

## The two input modes take opposite conventions

This is the single most confusing thing about the tool, and worth getting right
before anything else.

**Piped on stdin -- write the expression bare.** No prefix:

```bash
printf '%s\n' 'name of operating system' \
  | sudo -n /Library/BESAgent/BESAgent.app/Contents/MacOS/QnA
```

A `q:` or `Q:` prefix here is a *syntax error*, because `:` is not a legal
character in relevance:

```
E: This expression contained a character which is not allowed.
```

**From an input file -- every line needs a `Q:` prefix.** Lines without it are
echoed verbatim and never evaluated, which looks like the tool silently doing
nothing:

```
$ cat q.txt
name of operating system
$ qna q.txt
name of operating system          <- echoed, not evaluated

$ cat q3.txt
Q: name of operating system
$ qna q3.txt
Q: name of operating system
A: macOS
```

That echoing behaviour makes an unprefixed file a convenient way to keep
commentary alongside queries, but it is a trap if you did not intend it.

Timing also differs by mode: piped stdin prints `T:` always, while file mode
prints it only under `-t` (what the usage text calls "non-interactive mode").

`-o <file>` sends the `Q:`/`A:` transcript to a file instead of stdout.

## Output grammar

One statement per input line. Statements are separated by a blank line, and each
produces some of:

| Prefix | Meaning |
| --- | --- |
| `A:` | an answer. **One line per value** -- a plural prints many |
| `E:` | an error, evaluation or otherwise |
| `T:` | evaluation time in **microseconds** |
| `I:` | the result's type, only under `-showtypes` |
| `Q:` | the query echoed back, in file mode only |

Order within a statement is all `A:` lines, then `T:`, then `I:`.

**Streams:** `A:`/`E:`/`T:`/`I:` go to **stdout**. Startup chatter goes to
**stderr** and is safe to discard:

```
Default masthead location, using /Library/Application Support/BigFix/BES Agent/actionsite.afxm
No entry for terminal type "unknown";
using dumb terminal settings.
```

**Exit status says nothing about the relevance.** It is 0 for a good answer, a
runtime error, a syntax error, an undefined operator, *and* a missing input
file. The only non-zero status observed is 134 (`SIGABRT`) from the privilege
crash above -- so a non-zero exit means the process died, never that the
expression was bad. Parse the output; do not branch on `$?` to judge an
expression.

## `T:` tells you whether the expression ran

The most useful undocumented signal in the output. A `T:` line is present only
when the expression compiled and was evaluated, so its presence separates two
very different failures that both print `E:`:

```
Q: 1/0
E: Singular expression refers to nonexistent object.
T: 108                        <- it ran, and failed at evaluation

Q: bogus thing
E: The operator "bogus thing" is not defined.
                              <- no T: -- it never ran
```

No `T:` means the expression never got as far as evaluating: a parse error, an
undefined operator, no matching overload (`1 = "1"`), or an unprintable result.
With `T:`, the expression is well-formed and the failure is about this machine's
actual state.

### Timing is microseconds, and the first statement is not representative

Every session pays a one-time warm-up of roughly 2.5 ms on its **first**
statement, whatever that statement is:

```
$ printf '1+1\n1+1\n1+1\n' | qna
T: 2703
T: 59
T: 58
```

`1+1` costs about 58 microseconds once warm. To time an expression, put a throwaway
statement first, or run it twice and read the second -- otherwise you are
measuring startup. Verified against wall clock: a statement reporting
`T: 52545` adds ~60 ms to the run.

## `-showtypes` is the type oracle

`-showtypes` adds an `I:` line naming the result type, using the same type names
as the inspector tables. That makes it a direct check on this package's type
checker:

```
$ printf 'version "1.2.3"\nnow\n("a";"b")\n' | qna -showtypes
A: 1.2.3
T: 96
I: version

A: Mon, 31 Aug 2026 06:21:56 -0400
T: 575
I: time

A: a
A: b
T: 44
I: string
```

Two details worth knowing:

- A plural gets **one** `I:` for the whole result, naming the element type --
  plurality is not part of what `I:` reports.
- A runtime failure still reports the type it *would* have had: `1/0` gives
  `E: ...nonexistent object.`, `T: 108`, `I: integer`. So `-showtypes` answers a
  typing question even where the expression cannot produce a value on this host,
  which is exactly the case a static checker most needs settled.

## Gotchas

**An answer and an error can both come back.** The answer is printed *first*, so
reading only the first line looks like success:

```
Q: name of running application
A: BESAgent.app
E: Singular expression refers to non-unique object.
```

This is the non-uniqueness failure described in
[`universal_relevance.md`](universal_relevance.md), and the ordering is why it is
easy to miss.

**A valid inspector can fail for want of a context.** Some inspectors are only
defined inside an evaluation context QnA does not provide -- an action context,
for instance -- and asking for one outside it gives:

```
Q: action lock state
E: No inspector context.
T: 92
```

Note the `T:` line: this is a *runtime* failure, so the inspector compiled and
exists. **You cannot conclude non-existence from it**, which matters whenever
QnA is being used as an oracle for what the language defines. A name that truly
does not exist says so instead -- `The operator "..." is not defined.` -- and
carries no `T:`. For existence questions, prefer the introspection queries above
over inferring from a failure.

**An unprintable result is not an error.** A result with no string
representation draws an error naming `string`, and the expression itself was
fine:

```
Q: processors
E: The operator "string" is not defined.
```

Wrap it in `number of (...)` or `exists ...` to confirm values flow through. A
genuinely undefined phrase names *itself* instead -- `The operator "bogus thing"
is not defined.`

**A newline ends the statement.** There is no continuation, so an expression
spanning two lines becomes two broken statements:

```
Q: number of
E: This expression could not be parsed.
Q: processors
E: The operator "string" is not defined.
```

Join multi-line relevance into one line before piping it.

**Blank lines are errors, not skips.** An empty line draws
`E: This expression could not be parsed.`, and so does a line holding only a
`/* comment */`. Filter empties before feeding a batch.

**There is no output cap.** A plural prints one `A:` line per value: `names of
files of folder "/usr/bin"` produced 983 lines here. Prefer `number of ...`
while exploring.

**Quotes inside a string literal are `%22`.** A literal cannot contain a raw
double quote:

```
Q: concatenation of ("say "; "%22hi%22")
A: say "hi"
```

**Case does not matter, and leading whitespace is tolerated.** `NAME OF
OPERATING SYSTEM` and `    1+1   ` both answer normally.

## A batch probe script

What this project used to gather the findings in
[`universal_relevance.md`](universal_relevance.md). It runs one expression per
input line, skips blanks, drops the startup chatter, and keeps each answer
beside the expression that produced it:

```bash
#!/bin/zsh
# probe client relevance; one expression per line on stdin
QNA=/Library/BESAgent/BESAgent.app/Contents/MacOS/QnA
while IFS= read -r line; do
  [ -z "$line" ] && continue
  out=$(printf '%s\n' "$line" | sudo -n "$QNA" 2>/dev/null \
        | grep -E '^(A|E|I):' | head -3 | tr '\n' ' | ')
  printf '%-58s => %s\n' "$line" "$out"
done
```

One process per expression keeps a slow or wedged statement from stalling the
rest, at the cost of paying start-up each time. For a large batch, feed every
expression to a single invocation instead and split the output on blank lines --
but remember the first statement absorbs the warm-up.

## One machine answers one machine's question

The script above only ever reports what *this* endpoint's client thinks, and
this project's tables are per-platform, per-version snapshots. Whenever the
answer might depend on *which* client -- a name that exists on one platform and
not another, or behaviour that changed between client versions -- reach for
[`bigfix-remote-client-relevance`](https://pypi.org/project/bigfix-remote-client-relevance/)
instead. It evaluates across Docker containers, SSH endpoints and the local
agent, and across several pinned `qna` versions in one call. It is a dev
dependency of this project. The first container run pays a slow warm-up while
the image and the `qna` build are fetched; afterwards it is fast.

```python
from bigfix_remote_client_relevance import Target, evaluate_client_relevance_stream

async for result in evaluate_client_relevance_stream(
    expression, targets, qna_version=["11.0", "10.0"]
):
    ...  # result.answers, result.answer_types, result.error, result.error_kind
```

- `evaluate_client_relevance` returns the whole fan-out in target-then-version
  order; the `_stream` variant yields in completion order, so a slow SSH host
  never holds up a container that has already answered.
- It runs `qna -t -showtypes`, so `result.answer_types` carries the `I:` line
  described in [`-showtypes` is the type oracle](#-showtypes-is-the-type-oracle)
  -- the engine's own name for the result type, per answer.
- Failures arrive *inside* results rather than raised: `error_kind` separates a
  real relevance `E:` from transport and provisioning trouble, so one
  unreachable host does not end a sweep.
- One expression per call. `client_relevance` is a single string and `answers`
  is a flat list, so feeding it N expressions loses the boundary between them.
  For a few hundred expressions on one machine, the batch script above is still
  the right tool; use the package when the answer depends on which machine.

## Asking the engine what exists

QnA can be asked about the language itself, not just about this machine. The
introspection meta-layer -- `properties`, `types`, `casts`, `binary operators`,
`unary operators` -- is queryable relevance like anything else, and it exists in
both dialects. This is where the inspector tables in this package come from
(`tools/generate_client_dumps.py`), and it is the authoritative answer to "does
this inspector exist", which no snapshot can settle on its own.

**Does a property exist on a given type?**

```
Q: exists properties whose (usual name of it = "name"
                            and name of direct object type of it = "processor")
A: False
```

So `name of processor` is not defined -- positive evidence, from the engine,
without deploying or guessing. The useful columns on a `property` are
`singular name`, `plural name`, `usual name`, `multivalued`, `result type`,
`direct object type` and `index type`; each is a property of the property, and
`| ""` gives a default where one is absent.

**What properties does a type have?**

```
Q: number of properties whose (name of direct object type of it = "processor")
A: 13
Q: (usual name of it) of properties whose (name of direct object type of it = "processor")
A: vendor name
A: type
A: family
...
```

**Is a captured dump still complete?** Each category's row count is the engine's
own, so comparing them detects a stale or truncated capture:

```
Q: number of properties
A: 2369
```

against `wc -l tests/examples/relevance_inspectors/client_relevance_properties_macos.txt`
-- 2369 here, i.e. current for this agent build.
`generate_client_dumps.py` makes this check itself, which is what catches a
dropped row: a table one short is invisible in the output but not in the count.

## Its place in this project

QnA settles questions the inspector tables cannot -- and it is also where those
tables came from, via the introspection queries above. The tables are a
*snapshot* of what names existed on the platforms that were captured; the engine
is the live version of the same source, plus the only local source of truth for
what the evaluator actually *does* with those names -- comparison semantics,
short-circuit order, error propagation, name resolution inside a `whose`, and
which spellings collapse onto which operator.

That distinction is worth keeping straight when using QnA to settle a question:

- **"Does this exist?"** -- ask the introspection layer. Do not infer it from a
  failure, because `No inspector context.` is a failure of a name that does
  exist.
- **"What does this do?"** -- evaluate it, and read `T:` to confirm it actually
  ran.

Where this project's documentation and the published inspector reference
disagree, QnA decided it, and the disagreement is recorded rather than
smoothed over. `tests/corpus/*.rlvcorpus` marks cases `[unverified]` precisely
to distinguish inferred behaviour from behaviour confirmed here.

For **session** relevance the equivalent authority is a server-side relevance
query, not QnA -- QnA has no access to the deployment, and asking it a `bes`
question returns `The operator "bes computers" is not defined.` See
[`dialects.md`](dialects.md).

### Differential testing: is the checker calibrated?

Beyond settling individual questions, QnA can be run against the type checker
in bulk: analyse an expression, evaluate it, and compare the verdicts. Three
axes, in increasing order of what they prove:

1. **Rejection.** The analyzer rejecting what the engine accepts is a false
   positive. The analyzer accepting what the engine rejects with a *type* error
   is a miss -- but only a type error: `nonexistent object`, `non-unique
   object` and `No inspector context.` are runtime or environment facts, and
   `The operator "string" is not defined.` is usually the display artifact
   above, not a finding.
2. **Type inference.** Compare `I:` against the type the checker inferred. This
   tests what the checker computes, not merely what it refuses, and it needs
   `-showtypes`.
3. **Platform and version.** The same probe on several clients and `qna`
   versions tests the snapshot the tables encode, which is what the
   multi-client evaluator above is for.

Last run over 134 expressions -- this repo's client-dialect corpus sites that a
Mac can evaluate, plus every `parse("...")` literal in
`tests/test_typecheck.py` -- against macOS client 11.0.6:

| | count |
| --- | --- |
| analyzer rejects, engine accepts (**false positives**) | **0** |
| analyzer rejects, engine rejects (agreement, matching message) | 23 |
| analyzer accepts, engine reports a type error | 15 |

All 15 are deliberate: an `unknown-inspector` warning leaves `ok` true on
purpose, one bad `if` branch is tolerated on purpose, and the rest are the
unprintable-result artifact. Re-run this after changing the checker; the
false-positive column is the one that must stay at zero.
