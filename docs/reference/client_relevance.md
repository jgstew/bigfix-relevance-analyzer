# Client relevance

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
guards platform-specific parts explicitly, with `if` - see below, because the
guard has to be an `if`. `windows of operating system`, `mac of operating
system` and `unix of operating system` are the usual tests.

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

## `pad of` compares safely; its string form does not travel

`pad of` is how you avoid the version-truncation trap - see the
`universal-relevance` reference, which also covers why an untyped comparison of
two version-looking strings answers backwards. Its *ordering* is correct on
every platform; its text is not. macOS renders `pad of version "1.2"` as
`1.2.00` where Windows and the server give `1.2.0.0`, so compare with it
freely, but never compare `pad of X as string` or substring-match a padded
version.

## Only `if` guards a platform-specific inspector

An `and` guard does not guard. A name the platform does not define raises
**wherever it appears**, so nothing to its left prevents it, and nothing that
absorbs an evaluation error absorbs this - not `exists`, `number of` or `|`.
On macOS `false and (exists keys "x" of registry)` errors, where `false and
(1/0 = 1)` is `A: False`. A branch of an `if` that is not taken is the only
escape, either side, and it is chosen at runtime:

```
if (windows of operating system) then (exists keys "x" of registry) else false
```

## Where to read more

The full inspector reference is at
<https://developer.bigfix.com/relevance/reference/>.
