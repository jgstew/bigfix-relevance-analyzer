# Relevance syntax fundamentals

> **Expansive layer.** This document is the source of truth; the tighter
> MCP-served summary distilled from it is
> [`reference/syntax.md`](reference/syntax.md), which may omit anything
> here but must never contradict it. See [`README.md`](README.md).

True of both dialects. What differs between them is *vocabulary* - which
inspectors exist - not the grammar below.

## There are no reserved words

Relevance has no keyword list. `of`, `whose`, `it`, `as`, `exists`, `if`,
`then`, `else`, `not`, `and`, `or`, `mod`, `item` are structural, but they are
ordinary words the moment they appear inside an inspector name - and inspector
names are multi-word phrases, so this happens constantly. `starts of ranges`
uses `starts` as a plural inspector name, not as the first word of the
`starts with` operator.

The practical consequence when writing: **parenthesize anything that could
split two ways.** You cannot rely on a keyword being unambiguous, because it
is not a keyword.

`true` and `false` are the same story from the other direction: they read
like boolean literals but are not special-cased grammar at all - they are
ordinary zero-argument inspectors (`true: boolean`, `false: boolean` in the
property tables), present identically in both dialects. Nothing stops a
platform from not defining them, in principle; nothing in the sampled dumps
suggests one doesn't.

## `of` chains read right to left

`a of b of c` means `a of (b of c)` - `of` is right-associative. Evaluation
starts at the far right with the outermost object and works leftward, so the
chain reads naturally backwards: *the names of the files of the folder* starts
from the folder.

Written left to right, each step narrows: `names of files of folder "/tmp"`
takes the folder, gets its files, gets their names.

An explicit `(a of b) of c` is a different expression and keeps its own
grouping.

## Singular versus plural is part of the type system

Every expression yields either one value or many, and the distinction is
enforced. `file "/tmp/x"` is singular; `files of folder "/tmp"` is plural. Most
inspectors come in both forms with different names - `file`/`files`,
`key`/`keys`, `value`/`values` - and the plural form is usually what takes a
`whose` filter.

In the type system this is spelled `X with multiplicity`, which is a child type
of `X`. That is why plurality survives a cast and why a diagnostic can say an
operand was not singular.

**Which name you write settles the phrase**, whatever the object's own
plurality. `names of files of folders "/"` is plural; `name of files of folders
"/"` is singular - and it asserts something about the object that may not hold:

```
Q: name of files of folders "/"
A: besserverupgrad2.log
E: Singular expression refers to non-unique object.
```

One name, not one per file. The error is raised at evaluation and is about the
*object*, which is a different complaint from the static `A singular expression
is required.` that a genuinely plural operand earns. Written with an object
that does hold one value, the same phrase is clean:

```
Q: name of files "besserverupgrad2.log" of folders "/"
A: besserverupgrad2.log
```

The object decides only where the property has no name of its own to speak
with - a cast, a nested `of`. `(it as string) of files of folder "c:\"` is
plural off a singular `it`.

**`whose` is transparent to this.** `X whose (P)` keeps whichever spelling of
`X` was written, filter or no filter - it is not made plural by having a
predicate at all:

```
Q: (line whose (it contains "...") of file "...") as string contains "..."
A: True
Q: (line whose (it contains "...") of file "...") as string      -- filter matches several lines
A: True
E: Singular expression refers to non-unique object.
Q: (lines whose (it contains "...") of file "...") as string contains "..."
E: A singular expression is required.
```

Singular stays a runtime risk, exactly as the bare `name of files ...` case
above; plural is a static error in the same position. The empty-match case is
the mirror image and uses the *other* runtime message:

```
Q: (line whose (it contains "<nothing matches>") of file "...") as string
E: Singular expression refers to nonexistent object.
Q: number of (lines whose (it contains "<nothing matches>") of file "...")
A: 0
```

Practically: filtering does not make a singular spelling safe, and it does not
make it more dangerous than the bare form either - `key whose (...) of key
"HKLM\SOFTWARE" of registry` carries the same risk as `key of key
"HKLM\SOFTWARE" of registry`, no more. The safer habit either way is to stay
plural for as long as the chain runs, filtering the plural spelling, and
collapse once at the very end - with a plain index if one match is guaranteed,
or with the aggregate `unique value of` below if it is not.

Four other constructs turn a plural into something singular:

- `exists <plural>` - a boolean: did it produce anything at all.
- `number of <plural>` - an integer count.
- `item N of (...)` - the N-th value, **0-based**, where N must be an integer
  literal.
- the singular spelling of an **aggregate** - a property whose job is to
  consume a collection: `unique value of`, `concatenation of` (and its `html`,
  `local encoding`, `fxf encoding` variants), `maximum of`, `minimum of`,
  `set of`, `sum of`, `union of`, `intersection of`, `conjunction of`,
  `disjunction of`. `unique value of ("a";"a")` is `a`; `unique value of
  ("a";"b")` answers `a` and then errors, for the reason above - which makes it
  the *safer* way to assert singularity, since it dedups first.

## `whose` filters, and `it` refers to the context

`<plural> whose (<boolean>)` keeps only the values for which the boolean holds.
Inside the filter, `it` is the value being tested:

```client_relevance
files whose (size of it > 1000) of folder "/tmp"
```

**`of` binds `it` as well.** In `a of b`, an `it` inside `a` refers to `b`:

```client_relevance
(it as string) of values "SearchList" of keys "..." of registries
```

This matters because the BigFix runtime's own error message for a misplaced
`it` says `"It" used outside of "whose" clause.`, which describes a narrower
rule than the engine implements. The message is wrong; `of` binds too.

`if`/`then`/`else` introduces no context, so an `it` in a branch still refers
to whatever bound it from outside.

**Binding `it` is not the same as scoping every name.** A bare name inside a
`whose` filter is resolved against the *world*, not against the item being
tested -- `files whose (exists properties)` reads `properties` as the world's and
is valid, while `files whose (exists properties of it)` asks for a property of
the file and is refused. Adding `of it` is what changes the question. Verified on
both engines; see
[`universal_relevance.md`](universal_relevance.md#a-bare-name-inside-whose-is-a-world-reference-not-a-property-of-the-item).

## Casts convert with `as`

`<value> as <type>` converts. These are ordinary, not exotic: `it as string`,
`it as lowercase`, `it as trimmed string`, `it as integer`, `it as hexadecimal`
appear throughout real content, and they chain - `it as string as lowercase`.

`it as hexadecimal` is worth a second look before copying: it **encodes**
`it`'s own bytes to a hex string, whatever `it` is - it does not parse a hex
*string* back into the number it names. See the transcript in
[`universal_relevance.md`](universal_relevance.md#as-hexadecimal-encodes-it-does-not-decode-a-hex-string).

A cast that cannot succeed is an error, not a null; see error fallback below.

## `|` is error fallback, not "or"

`a | b` evaluates `a`, and yields `b` only if `a` **errored**. It is not
boolean or, and it is not a null-coalescing operator on a false value - `a`
failing is the trigger.

This is the idiomatic way to give a default for something that may not exist:

```session_relevance
(name of it | "unknown") of bes computers
```

**Both operands must be singular.** A plural spelling on either side is
refused before evaluation, on both engines:

```
Q: (names whose (length of it = 999) of files "hosts" of folder "/etc") | "fallback"
E: A singular expression is required.
```

That requirement is why the default idiom is inherently a *singular* idiom,
and it is load-bearing: the "value is missing" case must arrive as an
**error** -- a singular spelling that finds nothing raises `Singular
expression refers to nonexistent object.`, and that error is what trips the
fallback. A plural finding nothing answers 0 values, which is not an error --
so even if a plural were accepted here, the fallback would never run. A
`setting "X" whose (value of it = "1") of client | ERROR "disabled"` is
therefore *correctly* singular, however plural-preferring the rest of the
chain is; see the empty-case findings in
[`universal_relevance.md`](universal_relevance.md#the-empty-case-a-singular-that-finds-nothing-and-what-rescues-it).

**Not every error is rescued.** `nonexistent` trips the fallback;
`non-unique` does not -- a singular over several values has already answered
its first value when uniqueness is violated, and the expression still errors
with the fallback unused. Transcripts in the same section.

The singularity rule catches `nothing`, which reads like a null but is an
**empty plural** - it answers no values at all, so it cannot be a `|` operand
on either engine:

```
Q: nothing
T: 31
Q: (1) | nothing
E: A singular expression is required.
```

(That bare `T:` with no `A:` line is the tell; see [`qna.md`](qna.md).) The
singular undefined-typed spelling is `ERROR "..."`, which is what the idiom
actually wants - it is a value that *errors*, so it also works as the left
operand where `nothing` would be silently empty:

```
Q: (1) | ERROR "x"
A: 1
```

`|` has no row in the operator table at all, because the grammar defines it
rather than the inspector layer. The same is true of `and` and `or`.

It binds tighter than comparisons, `+`/`-`, `and` and `or` - `0 = x | 999`
is `0 = (x | 999)` - but a bare `*`, `/`, `mod` or `&` result cannot meet
`|` at all: `2 * 3 | 5` is a parse error; write `(2 * 3) | 5`. `exists`
and `not` do not absorb a fallback: `exists x | false` is `(exists x) | false`.

One thing `|` does **not** rescue: a name the engine does not define, which
raises rather than falling back. Only an untaken `if` branch absorbs that. See
[`universal_relevance.md`](universal_relevance.md#an-undefined-name-raises-wherever-it-appears---except-in-an-untaken-if-branch).

## Errors propagate, except where a plural flattens them

An error in a singular context is an error. In a *plural* context it is
flattened to "produced nothing", which is why `number of (1/0)` is `0` while
`exists number of (1/0)` is `True`. A count of zero and an error are therefore
indistinguishable from the outside - the engine does not separate them, so
neither can any tool.

## An unprintable result is not an error

A result with no `as string` cast draws `E: The operator "string" is not
defined.` - not a true error: the expression evaluated, only printing it
failed. Verify with `number of (...)` that results flow through. A truly
undefined phrase names itself: `The operator "attr lists" is not defined.`

## String literals

Delimited by `"`. A literal **cannot contain a raw double quote**: one is
written as `%22` inside the string. **A backslash escapes nothing** - `"C:\x"`
is a backslash followed by `x`, which is why Windows paths are written plainly:

```relevance
"C:\Windows\Temp\file.txt"
```

This is the part of relevance syntax most often written wrongly by anyone
carrying habits over from C-like languages.

## Number literals

A run of digits, nothing else - `42`, `340282366920938463463374607431768211455`.
Magnitude is free to write, but the engine settles a numeral's type from its
size while parsing, in three tiers:

| Up to | Type | |
| --- | --- | --- |
| `2^63 - 1` | `integer` | [INFER] read off the type table's reported size, not yet confirmed live |
| `2^128 - 1` | `large integer` | confirmed live - still a real, usable literal everywhere, bare or in arithmetic |
| beyond that | rejected outright | confirmed live - `An integer constant was too large.`, wherever the literal appears |

See `nodes.MAX_INTEGER` / `nodes.MAX_LARGE_INTEGER` for the exact boundaries and
how each was established.

**There is no decimal-point numeral syntax at all.** `.` is not a legal
character in relevance source outside a string literal - not as a decimal
point, not anywhere. Verified live 2026-09-01 (client QnA, macOS 14.6.1;
session `bf160001489`): every one of these draws the identical lexical error,
`This expression contained a character which is not allowed.`, regardless of
position or spacing:

```
1.5        3.0        1.        .5        1 . 5        1.2.3        (1).(5)
```

The only way to a `floating point` value is a cast - from a string literal, or
from an ordinary numeric expression, which is computed in floating point
rather than reinterpreting an already-truncated integer result:

```
1/2                           -> 0        (integer division)
"1.5" as floating point      -> 1.5
1/2 as floating point         -> 0.5
```

There is no hexadecimal literal syntax either: `0x1F` lexes as the number `0`
followed by the word `x1F` - two tokens, not one. `hexadecimal` only ever
appears as a cast target or as its own decode inspector, and the two are easy
to reach for backwards; see the transcript in
[`universal_relevance.md`](universal_relevance.md#as-hexadecimal-encodes-it-does-not-decode-a-hex-string).

## Comments

`/* ... */`, and they do not nest - a comment ends at the first `*/`. There is
no line comment: `//` is division followed by division.

## Tuples and collections

`,` builds a tuple, `;` builds a collection. Both are ways of producing several
values from one expression:

```session_relevance
(id of site of it, id of it, applicable computer count of it) of fixlets of bes sites
```

```client_relevance
(packages "docker-ce" of debianpackage; packages "docker" of rpm)
```

## Operator spellings collapse

Relevance accepts many spellings of the same comparison, and several have no
definition of their own - the engine rewrites them. `a > b` *is* `b < a`;
`is contained by` is `contains` with the operands swapped; `is not equal to` is
a negated `=`. The generated operator table in each dialect's reference lists
every spelling against the operator it really is.

This matters when reading an error: a type error names the **canonical**
operator, not what you wrote. Writing `>` and being told about `<` is not a
bug.

## Comparisons do not chain

Two comparisons cannot meet without parentheses. `1 = 1 = true`, `1 < 2 < 3`
and `1 is 1 is true` are all parse errors, and mixing spellings does not help -
`"a" contains "a" = true` is refused too. Parenthesize the first comparison and
the second one is fine: `(1 = 1) = true` is `True`.

## What a static analyzer can and cannot tell you

This package's inspector tables are a *snapshot* captured from real engines.
They are evidence, not a specification:

- A name the tables do not define is a **lead**, not proof of a typo. The
  snapshot does not cover every platform or product version.
- Platform coverage is **reported, never enforced**. A platform absent from the
  snapshot has not been shown to lack an inspector; it may simply never have
  been captured.
- A statement that type-checks cleanly is not proven to run. "Nothing
  contradicts this" is the strongest available claim.

Treat an `unknown-inspector` warning as something to look at, not as an error.

## Where the semantics live

This document covers **grammar and shape**: what parses, and how it groups.
What the evaluator then *does* with a well-formed statement - comparison
semantics, short-circuit order, which constructs absorb errors - is recorded in
[`universal_relevance.md`](universal_relevance.md), with the engine transcripts
that establish it.

The distinction matters when reading a surprising result. Every trap documented
in `universal_relevance.md` is in a statement that parses cleanly and
type-checks: the grammar is not what went wrong.

## Version literals have three spellings

All three are quoted - the dots inside `"1.2.3"` are text, not the illegal
bare-numeral punctuation the [Number literals](#number-literals) section
above rules out; a version literal is never written unquoted. All three
produce a `version`, and the choice is stylistic:

```
version "1.2.3"
"1.2.3" as version
(it as version) of ...
```

Only **one** operand of a comparison needs to be a version for the comparison
to be a version comparison - the other is coerced. That makes the spelling
load-bearing in a way most casts are not: whether a comparison of two
version-looking strings is a *version* comparison or a *lexicographic string*
comparison turns on whether either side says so.

This is the single most consequential piece of syntax in the language, and the
failure is silent in both directions. See
[`universal_relevance.md`](universal_relevance.md#version-comparison-is-the-sharpest-edge-in-the-language).

## Comparisons and guards evaluate left to right

`and` and `or` short-circuit strictly left to right, so a guard protects only
what is written to its right. This runs against the right-to-left reading of an
`of` chain above, which is why it is easy to get wrong; the evidence is in
[`universal_relevance.md`](universal_relevance.md#and-and-or-short-circuit-strictly-left-to-right).
