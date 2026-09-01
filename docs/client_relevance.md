# Client relevance

> **Expansive layer.** This document is the source of truth; the tighter
> MCP-served summary distilled from it is
> [`reference/client_relevance.md`](reference/client_relevance.md), which may omit anything
> here but must never contradict it. See [`README.md`](README.md).

Evaluated **on the endpoint**, by the BES Client (the agent), against the
machine it is running on. It answers questions about *this computer*: what
operating system it runs, which files and registry keys exist, what is
installed, what is running.

It has no access to server-side data. There are no fixlets-across-the-estate,
no computer lists, no action results - those are session relevance. A statement
that asks about other computers cannot be client relevance, whatever file it is
written in.

## Where you write it

| Surface | How |
| --- | --- |
| Fixlet, Task, Analysis, Baseline | `<Relevance>` elements (applicability) |
| Baseline components | per-component `<Relevance>` |
| Analysis properties | each property's relevance |
| Success criteria | `<SuccessCriteria>` |
| Automatic computer groups | `SearchComponentRelevance` |
| Action script | `{...}` substitutions inside ActionScript |
| ClientUI dashboards | static `<?Relevance ?>` in an HTML file under the client's `__UISupport` folder |
| Plain files | a `.rel` file whose whole content is one expression |
| Documentation | a fenced code block in a Markdown file, where the block is the whole expression |

The ClientUI case is the one that surprises people: HTML holding relevance is
*almost* always session relevance, and a ClientUI dashboard is the exception.
See [`dialects.md`](dialects.md) for how to tell them apart - and note that
ClientUI client relevance legitimately uses `sites`, `relevant fixlets of
sites`, and `relevant offer actions of sites`, which look session-only and are
not.

## Platform matters here

Client relevance is the only dialect where platform is a real axis. An
inspector can exist on Windows and not on Linux, and the same name can mean
different things: `drives` is `drive` on Windows, `filesystem` on Debian, RHEL
and Ubuntu, and `volume` on macOS.

Portable client relevance either sticks to inspectors present everywhere or
guards platform-specific parts explicitly - and the guard has to be an `if`,
for the reason worked through below:

```
if (windows of operating system) then (exists keys "x" of registry) else false
```

`windows of operating system`, `mac of operating system`, `unix of operating
system` are the usual guards.

Three inspectors that look session-only but are macOS **client** inspectors:
`rate`, `linear projection`, `exponential projection`.

## Common mistakes

- **Session inspectors in a `<Relevance>` element.** Anything starting `bes ` -
  `bes computers`, `bes fixlets` - has no meaning on a client. This is the
  single most common dialect error, and it fails on every endpoint.
- **Assuming platform coverage.** A statement that works on Windows may have no
  meaning on Linux. Guard, or stay portable.
- **An unbound `it`.** `size of it` with nothing to bind to is meaningless to
  the engine, not merely unusual.
- **Backslash escaping in paths.** `"C:\Windows"` is correct as written; a
  backslash escapes nothing.
- **Expensive constructs in applicability relevance.** Applicability is
  evaluated repeatedly, on every endpoint. Whole-file hashing and directory
  recursion in a `<Relevance>` element are the classic causes of client CPU
  complaints - see the cost table below.

## Where to read more

The full inspector reference is at
<https://developer.bigfix.com/relevance/reference/>.

## `pad of` compares correctly everywhere, but its string form is platform-dependent

`pad of` is the fix for the version-truncation trap documented in
[`universal_relevance.md`](universal_relevance.md) - and it is the one place
where a *core-language* operator has been observed to differ by platform.

The **ordering** it produces is correct on every platform. The **string it
renders** is not the same. On macOS 14.6.1:

```
Q: pad of version "1"          A: 1.0.00
Q: pad of version "1.2"        A: 1.2.00
Q: pad of version "1.2.3"      A: 1.2.30
Q: pad of version "1.2.3.4"    A: 1.2.3.4
Q: pad of version "10.20.30"   A: 10.20.300
```

The session engine, and Windows clients, pad to four components instead:

```
pad of version "1"          ->  1.0.0.0
pad of version "1.2"        ->  1.2.0.0
pad of version "1.2.3"      ->  1.2.3.0
pad of version "10.20.30"   ->  10.20.30.0
```

*(macOS and session verified directly, 2026-08-30. The Windows/session
correspondence is reported rather than measured here - macOS is the outlier.)*

Two practical consequences:

- **Comparing is safe.** `pad of a > pad of b` and `pad of a = pad of b` behave
  as intended on every platform. Spot-checked on macOS across boundary cases
  (`1.2.3` vs `1.2.10`, `2` vs `1.9`, `1.2.3.4` vs `1.2.4`), all correct.
- **Rendering is not portable.** Never compare `pad of X as string`, never
  substring-match a padded version, and never store one expecting another
  platform to reproduce it. If you need the text of a version, take the
  unpadded `as string`.

`pad of` is defined in all captured sources, so guarding its *availability* by
platform is unnecessary. It is only the output text that varies.

## Only `if` guards a platform-specific inspector

An inspector that does not exist on this platform is an undefined name, and
[`universal_relevance.md`](universal_relevance.md#an-undefined-name-raises-wherever-it-appears---except-in-an-untaken-if-branch)
has the general rule: it raises **wherever it appears**, so no guard to its
left prevents it and none of `exists`, `number of` or `|` absorbs it. Only a
branch of an `if` that is not taken escapes. Confirmed on a macOS client
(11.0.6, 2026-08-31):

```
Q: false and (exists keys "x" of registry)
E: The operator "keys" is not defined.
Q: (windows of operating system) and (exists keys "x" of registry)
E: The operator "keys" is not defined.
Q: if (windows of operating system) then (exists keys "x" of registry) else false
A: False
```

So the portable idiom is not "put the cheap test on the left" - there is no
left that works - it is `if`/`then`/`else`:

```
if (windows of operating system) then (exists keys "x" of registry) else false
```

`regapps` is a near-miss worth recording rather than re-investigating. It is
the natural example to reach for, and it proves nothing: `exists regapps "x"`
answers `A: False` on macOS, so `(exists regapps "x") and (windows of operating
system)` is safe there for a reason that has nothing to do with the guard. Only
a name the platform genuinely lacks - `keys ... of registry` on a Mac - shows
the rule.

Left-to-right order still matters, but for the other failure - an evaluation
error, where a guard on the left genuinely does protect what is written to its
right. See
[`universal_relevance.md`](universal_relevance.md#and-and-or-short-circuit-strictly-left-to-right).

## Enumerating the registry is not the same as reading it

Registry access on Windows is **fast**. It is a memory-mapped, OS-cached store,
and reading a key is not remotely the kind of operation that a WMI query or an
event-log scan is. Nothing here should be read as "avoid the registry" - it is
the cheapest way to answer most Windows applicability questions, and content
that uses it heavily is content doing the right thing.

What still has a cost is *how many* reads a statement asks for.
`keys "Uninstall" of key "HKLM\SOFTWARE\..." of registry` is a lookup by name:
one key, bounded, and how essentially all shipped Windows content reads the
registry. `keys of key "HKLM\SOFTWARE" of registry` enumerates a hive level,
and that count is unbounded. Only the second is charged, and only at the lowest
tier in the table - enough that walking several hives accumulates into
something visible, not enough to rank one hive walk alongside a disk recursion.

Measured over one shipped content site (6,439 fixlets, 160,249 relevance
sites): 55,218 sites use the named form and 1,440 the enumerating one. A rule
that could not tell them apart would be a cost on nearly every Windows fixlet
in existence, saying nothing.

### The filter form, and a rule that cannot be written - a recorded non-finding

`keys whose (...) of key "<hive>" of registry` enumerates and then filters, so
it costs what the enumeration costs; 4,424 sites in the same corpus write it
that way, and the classic instance is a scan of the `CurrentVersion\Uninstall`
hive. It is **not** charged, and the reason is worth recording so that nobody
re-derives it: cost patterns match runs of adjacent *word* tokens, and a string
literal deliberately breaks a run - an inspector named inside a string cannot
be charged for. The hive path is a string literal, so no pattern can see which
hive is being walked, and `keys whose` on its own does not say registry at all
(a macOS iokit dictionary has keys too). Charging it would mean charging an
ambiguous shape, which is the same over-reach as charging the named lookup.

The same mechanism is what makes the named form safe by construction rather
than by a careful regex: the string literal between `keys` and `of` means the
two are never one phrase.
