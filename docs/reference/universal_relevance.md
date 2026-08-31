# Universal relevance: what the evaluator does

Semantics confirmed on **both** a live client engine and a live session engine.
This is the core language: true whichever dialect you are writing. What differs
between the dialects is *vocabulary*, covered in `dialects.md`; the grammar is
covered in each dialect reference's syntax section.

Every trap below is in a statement that parses cleanly and type-checks. The
grammar is not what goes wrong.

## Version comparison has two silent traps

The highest-consequence facts in the language, because each produces a **wrong
answer** rather than an error.

### Comparison truncates to the shorter operand's component count

Only as many components as the shorter side has are compared:

```
Q: version "1.2.3" = version "1.2"
A: True
```

So `=` behaves as "matches this prefix". On a host running `14.6.1`:

| Expression | Answer | |
| --- | --- | --- |
| `version of operating system = version "14"` | `True` | matches all 14.x |
| `version of operating system > version "14"` | **`False`** | the damaging one |
| `version of operating system >= version "14"` | `True` | |

`> version "14"` is `False` because the comparison truncates to one component
and `14 > 14` is false. **A fixlet gating on "newer than 14" matches nothing on
14.6.1** - it excludes exactly the machines it was written for, without
erroring.

Fix with `pad of` on **both** sides:

```
pad of version of operating system > pad of version "14"    -> True
pad of version of operating system = pad of version "14"    -> False
```

`pad of` is defined in every captured source, client and session. Its
*ordering* is correct on every platform, but its rendered string is
platform-dependent (macOS differs from Windows and the server), so use it to
compare - never to print, store, or substring-match.

### Typing one side coerces the other; typing neither compares strings

A comparison is a version comparison if **either** operand is a version. One
`as version` or `version "..."` is enough.

| Expression | Both engines | |
| --- | --- | --- |
| `"2.10.1" > "2.3.3" as version` | `True` | version compare |
| `version "2.10.1" > "2.3.3"` | `True` | version compare |
| `"2.10.1" > "2.3.3"` | **`False`** | *lexicographic* compare |

With no version anywhere this compares strings, and `"2.10.1" < "2.3.3"`
because `'1' < '3'` at the third character. It answers the opposite of intent
whenever a component crosses a digit-width boundary - `1.9` to `1.10`, the
common case, and precisely where a comparison matters.

### The traps compose

`as version` fixes the string compare and leaves truncation fully intact:

```
Q: "2.10" > version "2.3.3"
A: True
```

Two components each after truncation: `2.10` against `2.3`. So a correct
comparison of unknown-shaped versions needs `pad of` regardless of casts.

## Equality is otherwise type-strict

```
Q: 1 = "1"
E: The operator "equal" is not defined.
```

No numeric/string coercion. The message names `equal`, the canonical operator,
not `=` as written. Version coercion above is the exception, not the pattern.

## `and` and `or` short-circuit strictly left to right

```
Q: false and (1/0 = 1)      A: False
Q: (1/0 = 1) and false      E: Singular expression refers to nonexistent object.
```

**A guard protects only what is written to its right.** This cuts against the
right-to-left reading of an `of` chain, which is why misplaced guards survive
review: evaluation order and read order are opposite.

`if`/`then`/`else` is the strongest guard - only the taken branch is evaluated
at all (`if false then (1/0) else 5` is `5`).

## A bare name inside `whose` is a world reference

`whose` binds `it`, but it does not make every bare name inside the filter a
property of the item. A bare name resolves against the **world**; only `of it`
asks for it on the item. Identical on both engines:

```
Q: number of files whose (exists properties) of folder "/etc"
A: 58
Q: number of files whose (exists properties of it) of folder "/etc"
E: The operator "properties" is not defined.
```

The first is valid because `properties` is a world property; the second is
refused because `properties of <file>` does not exist. So a filter may freely
mention world state, and a mixed one is ordinary -- `files whose (name of it =
name of operating system)` reads the item's name and the world's.

Consequence when reading an error: `The operator "X" is not defined.` inside a
`whose` often means an `of it` was added to something already correct as a bare
world reference. Dropping `of it` is the fix as often as fixing the name is.

## Errors are values, and some constructs absorb them

`exists (1/0)` is `False` and `number of (1/0)` is `0`, so a count of zero and
an error are indistinguishable from the outside - no tool can separate them,
because the engine does not.

`not` does not absorb: `not (1/0 = 1)` errors. A collection reports per
element, so `(7; 1/0)` answers `7` *and* errors. For a deliberate default, use
the error-fallback operator `|`.

## A singular spelling over several objects fails at evaluation

Both engines reject it, and the complaint is about the *object*:

```
Q: name of running application                  (client)
A: BESAgent.app
E: Singular expression refers to non-unique object.

Q: operating system of bes computer             (session)
E: Singular expression refers to non-unique object.
```

The client case answers *and then* errors, so a truncated reading of the output
looks like success.

A `whose` filter does **not** make a singular spelling safe - it narrows the
candidates without asserting there is one. Genuine world singletons are clean
(`computer name`, `current date`, `name of operating system`).

The distinction is visible in the inspector tables. Each of these has an
ordinary unindexed row -- that is why the bare spelling type-checks. What marks
it as one of many is an **indexed sibling returning the same type**
(`filesystem "/"`, `bes computer <id>`): that row is how you pick one, so its
existence says there are several. `operating system`, `computer name` and
`current date` have no indexed row and are clean.

The same-return-type part matters: `april` has an indexed sibling (`april
2026`), but it returns a `date` rather than a `month`, so it is a different
operation and bare `april` is fine.

## Two runtime errors that are easy to confuse

Both engines use identical wording, so neither is a dialect signal:

- `nonexistent object` - the singular expression found nothing.
- `non-unique object` - it found more than one, and a singular spelling may
  speak for only one.

## Each dialect rejects the other's vocabulary outright

```
Q: number of bes computers      (client)   E: The operator "bes computers" is not defined.
Q: number of processors         (session)  E: The operator "processors" is not defined.
```

A hard error naming the phrase - cheap to catch at an engine, invisible before
then, since the statement is perfectly well-formed.
