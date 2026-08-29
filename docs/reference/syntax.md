# Relevance syntax fundamentals

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

Three constructs turn a plural into something singular:

- `exists <plural>` - a boolean: did it produce anything at all.
- `number of <plural>` - an integer count.
- `item N of (...)` - the N-th value, **0-based**, where N must be an integer
  literal.

## `whose` filters, and `it` refers to the context

`<plural> whose (<boolean>)` keeps only the values for which the boolean holds.
Inside the filter, `it` is the value being tested:

```
files whose (size of it > 1000) of folder "/tmp"
```

**`of` binds `it` as well.** In `a of b`, an `it` inside `a` refers to `b`:

```
(it as trimmed string) of values "SearchList" of keys "..." of registries
```

This matters because the BigFix runtime's own error message for a misplaced
`it` says `"It" used outside of "whose" clause.`, which describes a narrower
rule than the engine implements. The message is wrong; `of` binds too.

`if`/`then`/`else` introduces no context, so an `it` in a branch still refers
to whatever bound it from outside.

## Casts convert with `as`

`<value> as <type>` converts. These are ordinary, not exotic: `it as string`,
`it as lowercase`, `it as trimmed string`, `it as integer`, `it as hexadecimal`
appear throughout real content, and they chain - `it as string as lowercase`.

A cast that cannot succeed is an error, not a null; see error fallback below.

## `|` is error fallback, not "or"

`a | b` evaluates `a`, and yields `b` only if `a` **errored**. It is not
boolean or, and it is not a null-coalescing operator on a false value - `a`
failing is the trigger.

This is the idiomatic way to give a default for something that may not exist:

```
id of site of it | 0
```

`|` has no row in the operator table at all, because the grammar defines it
rather than the inspector layer. The same is true of `and` and `or`.

## Errors propagate, except where a plural flattens them

An error in a singular context is an error. In a *plural* context it is
flattened to "produced nothing", which is why `number of (1/0)` is `0` while
`exists number of (1/0)` is `True`. A count of zero and an error are therefore
indistinguishable from the outside - the engine does not separate them, so
neither can any tool.

## String literals

Delimited by `"`. A literal **cannot contain a raw double quote**: one is
written as `%22` inside the string. **A backslash escapes nothing** - `"C:\x"`
is a backslash followed by `x`, which is why Windows paths are written plainly:

```
"C:\Windows\Temp\file.txt"
```

This is the part of relevance syntax most often written wrongly by anyone
carrying habits over from C-like languages.

## Comments

`/* ... */`, and they do not nest - a comment ends at the first `*/`. There is
no line comment: `//` is division followed by division.

## Tuples and collections

`,` builds a tuple, `;` builds a collection. Both are ways of producing several
values from one expression:

```
(id of site of it, id of it, applicable computer count of it) of fixlets of bes sites
```

```
(packages "docker-ce" of it; packages "docker" of it)
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
