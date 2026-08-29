# Session relevance

Evaluated **on the server** - by the root server, or a console, WebUI or Web
Reports session - against the BigFix database. It answers questions about the
*deployment*: which computers exist, which fixlets are relevant where, what
actions ran, what property values were reported.

It cannot touch an endpoint's filesystem. There is no `files of folder`, no
registry, no processes; it reads what computers have already reported. A
statement that inspects a local disk cannot be session relevance.

## Where you write it

| Surface | How |
| --- | --- |
| Console dashboards | static `<?Relevance ?>` in a `.ojo` file, substituted once when the page renders |
| Web reports | static `<?Relevance ?>` in `.besrpt` / `.beswrpt` / `.webreport` |
| Dashboards and reports, dynamically | a JavaScript `Relevance(...)` or `EvaluateRelevance(...)` call, re-evaluated in the browser |
| Fixlet descriptions | the same JavaScript calls inside a `<Description>` |
| Fixlet Debugger | the QnA view |
| REST API | relevance query endpoints |
| Plain files | a `.bsr` file whose whole content is one expression |
| Documentation | a fenced code block in a Markdown file, where the block is the whole expression |

A JavaScript relevance call is *always* session relevance, wherever it appears
- a ClientUI cannot evaluate relevance from JavaScript at all. That is the
mechanism that separates a ClientUI dashboard from a console one, since the
static substitution syntax is identical in both.

Note that one file can carry both dialects: a Task whose `<Relevance>` is
client relevance and whose `<Description>` embeds a session-relevance
substitution is ordinary, not a mistake.

## Platform is not an axis

Unlike client relevance, session relevance has no per-platform variation - it
runs in one place. An `operating system` here is a *reported property of a
`bes computer`*, not a question about the machine evaluating the statement.

## The `bes ` namespace, and the traps around it

Most session-only vocabulary starts with `bes `: `bes computers`, `bes
fixlets`, `bes sites`, `bes actions`, `bes properties`. Roughly 92% of
session-only signatures mention a `bes ` object.

Two exceptions worth knowing:

- `bes license`, `bes licenses`, `bes product`, `bes products` exist in
  **client** relevance too - they are license inspectors shipped to the
  endpoint. A `bes ` prefix is therefore strong evidence of session relevance,
  not proof.
- Bare `sites`, `fixlets` and `offer actions` are **not** session markers.
  ClientUI client relevance uses them freely.

The introspection meta-layer - `types`, `properties`, `casts`, `binary
operators` - exists in both dialects, identically. It is how the inspector
tables in this package were captured, and it is not a dialect signal.

## Performance is shaped differently here

The expensive things in session relevance are not I/O but *cardinality*.
`results of bes fixlets` expands to the fixlet-by-computer matrix, growing with
the product of both rather than the sum, and `applicable computers of bes
fixlets` evaluates applicability per computer. A query that is instant on a
small deployment can be unusable on a large one.

The error-fallback operator is idiomatic here for exactly this reason -
per-object properties that may be missing get a default rather than failing the
whole query:

```
(id of site of it | 0, id of it | 0, applicable computer count of it | 0)
of fixlets of bes sites
```

## Common mistakes

- **Client inspectors in a dashboard or web report.** `files`, `registries`,
  `processes` have no meaning on the server.
- **Assuming a JavaScript call could be client relevance.** It cannot be.
- **Forgetting error fallback on per-object properties.** One object missing a
  property errors the whole tuple without a `| default`.
- **Unbounded cross products.** See the cost table below before shipping a
  query that joins fixlets to computers.

## Where to read more

The full inspector reference is at
<https://developer.bigfix.com/relevance/reference/>.
