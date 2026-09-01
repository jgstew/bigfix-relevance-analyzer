# Universal relevance

Findings that hold in **both** dialects. This is the core language: the
evaluator's own semantics, independent of which inspectors happen to be in
scope. A fact belongs here only once it has been confirmed on a client engine
*and* a session engine.

Anything that differs between the two belongs in
[`dialects.md`](dialects.md); anything that differs between platforms belongs
in [`client_relevance.md`](client_relevance.md), since session relevance has no
platform axis.

> **Expansive layer.** This document is the source of truth; the tighter
> MCP-served summary distilled from it is
> [`reference/universal_relevance.md`](reference/universal_relevance.md),
> served under the slug `universal-relevance`. The distilled version may omit
> anything here but must never contradict it. See [`README.md`](README.md).

## How these findings were established

Two live engines, queried directly:

| Dialect | Engine | How |
| --- | --- | --- |
| client | BES Agent QnA, macOS 14.6.1 | `printf '%s\n' '<expr>' \| sudo -n /Library/BESAgent/BESAgent.app/Contents/MacOS/QnA` |
| session | BigFix SaaS root server `bf160001489` | session relevance query endpoint |

Confirmed 2026-08-30/31 unless a finding says otherwise. QnA prefixes an answer
with `A:` and an error with `E:`, and prints `T:` timing; a plural result prints
one `A:` line per value.

Two details of that output matter when reading the transcripts below, and both
are easy to misread -- a `T:` line appears only when the expression actually
evaluated, so its absence marks a compile-time failure rather than a runtime
one, and an answer can be followed by an error, with the answer printed first.
[`qna.md`](qna.md) covers driving the tool: its flags (including `-showtypes`,
which names the result type), the full output grammar, and the gotchas.

**An engine answer outranks any assumed grammar.** Where this document and the
published inspector reference disagree, the engine won and the disagreement is
called out. Two such cases are recorded below (`it` binding, and version
comparison), and one non-finding is recorded so it is not re-investigated.

When adding a finding: probe both engines, paste the verbatim answers, name the
host and date, and say plainly if you verified only one side.

## Version comparison is the sharpest edge in the language

Two independent traps, and they compose. Both dialects behave identically.

### Comparison truncates to the shorter operand's component count

A `version` comparison only compares as many components as the *shorter* side
has. The remainder of the longer side is not consulted at all.

```
Q: version "1.2.3" = version "1.2"
A: True
```

They compare equal because `1.2` has two components, so only `1`, `2` are
examined. Session agrees. This is not a rounding artifact - it is the defined
comparison, and it makes `=` behave as "matches this prefix".

On a host running macOS 14.6.1:

| Expression | Answer | |
| --- | --- | --- |
| `version of operating system = version "14"` | `True` | matches all of 14.x |
| `version of operating system = version "14.6"` | `True` | matches all of 14.6.x |
| `version of operating system > version "14"` | **`False`** | the damaging one |
| `version of operating system >= version "14"` | `True` | |

`> version "14"` is `False` because the comparison truncates to one component
and `14 > 14` is false. **A fixlet gating on "newer than 14" therefore matches
nothing on 14.6.1** - it silently excludes exactly the machines it was written
for. Nothing errors; the statement is well-typed and answers cleanly.

`pad of` restores the expected ordering by giving both sides the same shape:

```
Q: pad of version of operating system > pad of version "14"
A: True
Q: pad of version of operating system = pad of version "14"
A: False
```

**Rule: compare versions with `pad of` on both sides, or compare only
same-shaped versions.** `pad of` is defined in every captured source, client
and session alike, so reaching for it costs no portability.

One caveat, and it is the reason to use `pad of` for *comparison only*: its
rendered string is platform-dependent. See
[`client_relevance.md`](client_relevance.md).

### Typing one side coerces the other - and untyped is a string compare

A comparison becomes a version comparison if **either** operand is a version.
One `as version` or one `version "..."` is enough; the other side is coerced.

| Expression | Both engines | |
| --- | --- | --- |
| `"2.10.1" > "2.3.3" as version` | `True` | version compare |
| `version "2.10.1" > "2.3.3"` | `True` | version compare |
| `"2.10.1" > version "2.3.3"` | `True` | version compare |
| `"2.10.1" > "2.3.3"` | **`False`** | *string* compare |

The last row is the trap. With no version anywhere, this is a lexicographic
comparison of two strings, and `"2.10.1" < "2.3.3"` because `'1' < '3'` at the
third character. It answers the exact opposite of what the author meant, and it
does so silently on both engines.

The failure needs only one component to cross a digit-width boundary, which is
routine in real version numbers - `1.9` to `1.10` is the common case, and it is
precisely where a comparison matters.

Note this coercion is *specific to version*. Equality is otherwise type-strict
(below), so the version behaviour is a deliberate convenience rather than a
general rule you can lean on.

### The two traps compose

Coercing does not escape truncation:

```
Q: "2.10" > version "2.3.3"
A: True
```

Two components each after truncation: `2.10` against `2.3`, and `10 > 3`. The
third component of the right operand is never read. So `as version` fixes the
*string-compare* trap while leaving the *truncation* trap fully intact, and a
correct comparison of unknown-shaped versions needs `pad of` regardless.

### Padding is per-component, not decimal

`pad of` widens components; it does not compare as a decimal number. Both
engines order `pad of version "1.2.3"` below `pad of version "1.2.10"`, which
is what you want and what a naive `as string` compare gets wrong.

## Equality is type-strict

No numeric/string coercion, on either engine:

```
Q: 1 = "1"
E: The operator "equal" is not defined.
```

The message names `equal`, the canonical operator, rather than `=` as written -
see the note on operator spellings in [`syntax.md`](syntax.md). It reads like a
missing-inspector complaint but means "no `equal` is defined over *these two
types*". Cast one side.

Contrast the version case above: `version` is the exception, not the pattern.

## `and` and `or` short-circuit strictly left to right

They short-circuit, and the direction is fixed:

```
Q: false and (1/0 = 1)
A: False
Q: (1/0 = 1) and false
E: Singular expression refers to nonexistent object.
```

Same asymmetry for `or`:

```
Q: true or (1/0 = 1)
A: True
Q: (1/0 = 1) or true
E: Singular expression refers to nonexistent object.
```

**A guard only protects what is written to its right.** This is worth stating
explicitly because it cuts against the way relevance is usually read: `of`
chains read right to left (see [`syntax.md`](syntax.md)), so the habit of
reading a statement from its rightmost object is a good one everywhere *except*
here. Evaluation order and read order are opposite, and that is exactly why
misplaced guards survive review.

The platform guard idiom in [`client_relevance.md`](client_relevance.md) relies
on this: the cheap, always-safe test goes first.

```
if (windows of operating system) then (exists regapps "x") else false
```

`if`/`then`/`else` is the strongest form of guard, because only the taken
branch is evaluated at all:

```
Q: if false then (1/0) else 5
A: 5
```

## A bare name inside `whose` is a world reference, not a property of the item

`whose` binds `it` to the value being tested, but it does **not** make every
bare name inside the filter a property of that value. A name written bare is
resolved against the *world*; only `of it` asks for it on the item. Both engines
behave identically.

Client, over a folder holding 58 files:

```
Q: number of files whose (exists properties) of folder "/etc"
A: 58
Q: number of files whose (exists properties of it) of folder "/etc"
E: The operator "properties" is not defined.
```

Session, over a deployment with two computers:

```
number of bes computers whose (exists current console user)        -> 2
number of bes computers whose (exists current console user of it)  -> error
```

In each pair the first is valid because the name is a world property and is read
as one; the second is refused because the name is not defined *on that object
type*. `properties of <file>` and `current console user of <bes computer>` do
not exist, and adding `of it` is what asks for them.

Read the other way round, this is the useful half: **a `whose` filter can freely
mention world state**, and does not have to relate everything to `it`. A filter
combining both is ordinary:

```
files whose (name of it = name of operating system)
```

`name of it` is the item's; `name of operating system` is the world's.

The consequence when reading an error: `The operator "X" is not defined.` inside
a `whose` usually means an `of it` was added to something that was already
correct as a bare world reference -- not that `X` is misspelled. Dropping `of
it` is the fix as often as correcting the name is.

## Errors are values, and some constructs absorb them

An error in a singular context propagates. Several constructs swallow it
instead, turning it into an absence:

```
Q: exists (1/0)
A: False
Q: number of (1/0)
A: 0
```

So a count of zero and an error are indistinguishable from the outside. The
engine does not separate them, and therefore no tool can - a static analyzer
cannot promise that `number of (...)` being `0` means "found nothing" rather
than "failed".

`not` does **not** absorb; it is an ordinary singular boolean operator:

```
Q: not (1/0 = 1)
E: Singular expression refers to nonexistent object.
```

A collection does not absorb either - it reports per element, so a healthy
value and an error can come back from one expression:

```
Q: (7; 1/0)
A: 7
E: Singular expression refers to nonexistent object.
```

**Absorption is direct-operand only.** `exists` forgives an erroring operand,
but not an error one construct further down -- a single cast between the
`exists` and the erroring expression and the error propagates again. Both
engines:

```
Q: exists ("abc" whose (length of it = 999))
A: False
Q: exists (("abc" whose (length of it = 999)) as string)
E: Singular expression refers to nonexistent object.
```

The operand of the `exists` in the second query is the *cast*, and the cast is
a singular context: the error reaches it, and an erroring cast is an erroring
operand `exists` never gets the chance to flatten. The same boundary holds for
the non-unique error (client, a file of 34 matching lines):

```
Q: exists (line whose (it contains "e") of file "<f>")
A: True
Q: exists ((line whose (it contains "e") of file "<f>") as string)
E: Singular expression refers to non-unique object.
```

For a deliberate default, use the error-fallback operator `|`, documented in
[`syntax.md`](syntax.md). `exists`/`number of` absorbing an error is a
byproduct of plural flattening; `|` is the construct that means it -- but note
`|` rescues fewer errors than it appears to; see the next section.

Everything above is about an error raised *during* evaluation. An undefined
name is a different thing entirely, and of everything here only an untaken `if`
branch absorbs it -- see the next section.

## An undefined name raises wherever it appears - except in an untaken `if` branch

The absorbers above, the short-circuit rule, and `|` all deal with a statement
that ran and went wrong. A name the engine does not define is a different
thing: it raises from any position it is written in, including one whose value
is never used.

Confirmed on both engines with a name each one lacks - `registry` is
client-only vocabulary, so the session engine is the one refusing it below,
and a macOS client refuses `keys ... of registry` in exactly the same words:

```
Q: false and (exists keys "x" of registry)
E: The operator "registry" is not defined.        (session)
E: The operator "keys" is not defined.            (client, macOS 14.6.1)
Q: false and (1/0 = 1)
A: False                                          (both)
```

The contrast is the whole finding. Same guard, same position, same engine -
one is absorbed and the other is not, and the difference is only whether the
name exists:

| construct | evaluation error `1/0` | undefined name |
| --- | --- | --- |
| `exists (...)` | `False` | raises |
| `number of (...)` | `0` | raises |
| `(7; ...)` collection | `7`, then the error | raises, nothing returned |
| `false and (...)` | `False` | raises |
| `(...) \| fallback` | the fallback | raises |
| `not (...)` | propagates | raises |
| untaken `if` branch | skipped | **skipped** |

### The one exception, and what it is not

A branch of an `if` that is not taken absorbs an undefined name, in either
position:

```
Q: if true then false else (exists keys "x" of registry)
A: False
Q: if false then (exists keys "x" of registry) else 1
A: 1
```

It is a **runtime** decision, not a literal the engine could fold away. Give
the condition something it has to evaluate and the untaken branch is still
spared, on both engines:

```
Q: if (exists file "/nope-xyz") then (exists keys "x" of registry) else false
A: False                                                            (client)
Q: if (number of bes computers > 999999) then (exists keys "x" of registry) else false
A: False                                                            (session)
```

Take the branch and it raises, so this is about the branch not running rather
than about `if` being special-cased for undefined names:

```
Q: if true then (exists keys "x" of registry) else false
E: The operator "registry" is not defined.        (both)
```

The `if` keeps working inside the constructs that do not absorb, so an
`if`-guarded name is safe wherever it is put:

```
Q: false and (if false then (exists keys "x" of registry) else false)
A: False                                          (both)
Q: (if false then (exists keys "x" of registry) else false) | true
A: False                                          (client)
```

**The untaken branch is not skipped wholesale**, which is the part that
resists a tidy explanation: it is still type-checked, on both engines.

```
Q: if false then 1 else "a"
E: Incompatible types.                            (both)
```

So the branch is compiled and typed, and it is the *name* error specifically
that does not fire there. No mechanism is asserted here to reconcile that with
`false and (...)` raising: the observations are firm and any story about when
resolution happens would not be.

Two consequences worth carrying. Guarding a dialect-specific or
platform-specific name with `and` does not work, in either operand order -
only `if`/`then`/`else` does; the platform case is worked through in
[`client_relevance.md`](client_relevance.md#only-if-guards-a-platform-specific-inspector).
And when reading an `is not defined` error, nothing about where the name sat
in the statement made it fire: it fires wherever the name appears, unless it
sat in a branch that did not run.

## The empty case: a singular that finds nothing, and what rescues it

The complement of the non-unique finding below: where a singular spelling over
*several* values errors with `non-unique object`, a singular spelling over
*none* errors with `nonexistent object` -- and the plural spelling of the same
question does not error at all, it answers 0 values. Both engines:

```
Q: "abc" whose (length of it = 999)
E: Singular expression refers to nonexistent object.
Q: number of (names whose (length of it = 999) of files "hosts" of folder "/etc")
A: 0
```

(The session engine agrees on both, via `bes computers` in place of files.)

Three constructs meet this error, and they treat it differently:

- **`exists`, directly over it**, flattens it to `False` -- but only directly;
  one cast in between and the error is back (see the boundary transcripts in
  the section above). `exists name whose (length of it = 12) of it` inside a
  `whose` filter is therefore the ordinary idiom for testing a singular
  property against a predicate, and is clean however the filter turns out.

- **`|` runs on it.** The fallback operator *requires* singular operands --
  a plural spelling on either side is refused before evaluation with
  `A singular expression is required.`, on both engines -- and the
  `nonexistent` error is precisely the trigger that makes the default idiom
  work:

  ```
  Q: ("abc" whose (length of it = 999)) | "fallback"
  A: fallback
  Q: (names whose (length of it = 999) of files "hosts" of folder "/etc") | "fallback"
  E: A singular expression is required.
  ```

  So a fallback chain is *correctly* written singular: the plural spelling
  cannot be written there, and its "found nothing answers 0" behaviour is the
  opposite of what the idiom needs.

- **`|` does not rescue `non-unique`.** A singular over several values has
  already produced its first value when uniqueness is violated; the error
  arrives after an answer, and the fallback never runs:

  ```
  Q: (name of files of folder "/etc") | "fallback"
  A: afpovertcp.cfg
  E: Singular expression refers to non-unique object.
  ```

  Session answers the bare error for the same shape (`(name of bes computers)
  | "fallback"`). Either way, the fallback is unused: `|` rescues an error
  that arrives *instead of* a value, not one that arrives after the first.

The practice that falls out of all three: **stay plural for as long as the
chain runs, and collapse once at the end** -- with `unique value of` where a
singular is actually required, since it dedups before asserting. The two
places a mid-chain singular is right rather than a habit are exactly the two
rescues above: the left side of a `|` (required, and the error is the
trigger) and directly under an `exists` (the predicate-testing idiom).

## Runtime error wording is shared - a recorded non-finding

The two engines do **not** word the same runtime error differently. The same
condition returns the same string on both:

```
Q: 1/0
E: Singular expression refers to nonexistent object.      (client)
E: Singular expression refers to nonexistent object.      (session)
```

This is recorded because it is an easy mistake to make from partial evidence:
`nonexistent object` and `non-unique object` are two *different conditions*,
not one condition worded two ways, and seeing one from each engine looks like a
dialect divergence.

- **nonexistent** - the singular expression found nothing.
- **non-unique** - it found more than one, and a singular spelling may only
  speak for one.

Consequently the runtime diagnostic templates in this package need no
per-dialect variants.

## Singular spellings over multi-valued objects fail at evaluation

Both engines reject a singular spelling that turns out to cover more than one
object, and the complaint is about the *object*, not the type:

```
Q: name of running application                            (client)
A: BESAgent.app
E: Singular expression refers to non-unique object.

Q: operating system of bes computer                        (session)
E: Singular expression refers to non-unique object.
```

Note the client case answers *and then* errors: the first value is printed
before uniqueness is violated, so a truncated reading of the output looks like
success.

A `whose` filter does not make a singular spelling safe - it narrows the
candidates without asserting there is one:

```
Q: name of filesystem whose (name of it = "Macintosh HD")
A: Macintosh HD
E: Singular expression refers to non-unique object.
```

Genuine world singletons are clean, because they are defined as one value
rather than filtered down to one:

```
Q: computer name
A: LP1-US-51719315 (796)
Q: current date
A: Sun, 30 Aug 2026
Q: name of operating system
A: macOS
```

The distinction is visible statically in the captured inspector tables, and it
is not about the name. Each of these has a perfectly ordinary *unindexed* row --
that is what makes the bare spelling parse and type-check. What marks it as one
of many is an **indexed sibling returning the same type**: `filesystem "/"`,
`application "Safari.app"` and `bes computer <id>` are how you pick one, so the
existence of that row says the unindexed spelling has several to choose between.

`operating system`, `computer name` and `current date` have no indexed row at
all, and are clean.

The same-return-type condition matters, and it is easy to miss. Month constants
have an indexed sibling too -- `april 2026` -- but it returns a `date` where
bare `april` returns a `month`. That is a different operation, not a way of
picking one of many, and bare `april` answers `April` cleanly:

```
Q: april
A: April
Q: family name of processor
A: Apple M1 Pro
E: Singular expression refers to non-unique object.
```

*(This corrects an earlier reading of the tables which held that these names
were defined only with an index. They are not -- the unindexed row exists, and
the indexed sibling is the signal.)*

See [`syntax.md`](syntax.md) for the four constructs that turn a plural into a
singular safely, and note that the aggregate spellings (`unique value of` and
friends) are the safest, since they dedup before asserting.

This section is the *several* half; the *empty* half -- a singular spelling
that finds nothing, which errors differently and is rescued differently -- is
[its own finding above](#the-empty-case-a-singular-that-finds-nothing-and-what-rescues-it).

## Each dialect rejects the other's vocabulary outright

Not a soft failure - an undefined-operator error naming the phrase:

```
Q: number of bes computers                                 (client)
E: The operator "bes computers" is not defined.

Q: number of processors                                    (session)
E: The operator "processors" is not defined.
```

This is what makes a dialect mistake cheap to catch once it reaches an engine,
and expensive before then: the statement is perfectly well-formed, so nothing
short of the vocabulary check notices. See [`dialects.md`](dialects.md).
