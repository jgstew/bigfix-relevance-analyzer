# Client relevance vs. session relevance

> **Expansive layer.** This document is the source of truth; the tighter
> MCP-served summary distilled from it is
> [`reference/dialects.md`](reference/dialects.md), which may omit anything
> here but must never contradict it. See [`README.md`](README.md).

BigFix has two distinct relevance dialects that share overlapping syntax but
are otherwise **not the same language**: they run in different places, have
access to different inspectors, and are used for different purposes.

- **Client relevance** - evaluated locally by the BES Client (the agent) on
  each endpoint. Used in Fixlet/Task/Analysis/Baseline `<Relevance>`
  elements and in computer group `SearchComponentRelevance`. Only
  client-side inspectors are available (e.g. `operating system`, `registry`,
  `files`, `client`).
- **Session relevance** - evaluated by the root server (or a console/WebUI
  session) against server-side data: fixlets, sites, computers, properties,
  actions, etc. Used in dashboards (`.ojo`), web reports (`.besrpt`/
  `.webreport`), the Fixlet Debugger's QnA view, and REST API relevance
  queries. Inspectors like `bes computers`, `bes fixlets`, `types`, and
  `properties` only exist here - they have no meaning on a client.

  Session relevance shows up two ways in dashboards, web reports, and
  Fixlet/Task descriptions: **statically**, via a `<?relevance ?>` /
  `<?Relevance ?>` processing instruction that the server substitutes once
  when it renders the page, and **dynamically**, via a JavaScript call -
  `Relevance(...)`, `EvaluateRelevance(...)` - that runs in the browser
  after the page has loaded (e.g. in response to a click, a typed query, or
  on a timer) and can be re-evaluated repeatedly. Both are session
  relevance; the difference is *when* and *how* it's triggered, not which
  dialect it is.

Never write plain "relevance" in code, docs, or file/variable names when a
specific one is meant - say **client relevance** or **session relevance**.
"Relevance" alone is reserved for statements that are genuinely true of both.

## ClientUI dashboards: the exception to "HTML means session relevance"

Relevance embedded in HTML, or evaluated from JavaScript, is *almost* always
session relevance - but **ClientUI dashboards are client relevance**. A
ClientUI is an HTML file in the client's `__UISupport` folder (default
`C:\Program Files (x86)\BigFix Enterprise\BES Client\__BESData\__UISupport`,
or in relevance terms `(it & "\__UISupport") of pathnames of data folders of
client`) that the BES Client renders **on the endpoint**. It uses the
*identical* `<?Relevance ?>` substitution syntax as a console dashboard, so
syntax alone cannot tell the two apart.

What does tell them apart is the **mechanism**: a ClientUI cannot evaluate
relevance from JavaScript at all - the only way to update its results is to
reload the whole page. A console dashboard or web report can, via
`Relevance(...)` / `EvaluateRelevance(...)`. So:

| Signal | Dialect |
| --- | --- |
| static `<?Relevance ?>` in a `.html` file | **client** (ClientUI) |
| static `<?Relevance ?>` in `.ojo` / `.besrpt` / `.beswrpt` / `.webreport` | session |
| a JavaScript `Relevance(...)` / `EvaluateRelevance(...)` call, anywhere | session |

Corroborating (but not required) ClientUI markers: a
`<meta ... product="CustomDashboardClientUI"/>` tag, `cid:load?page=...`
links, and `takeoffer:nnn` links. `clientui_dashboard_no_product_meta.html`
deliberately has none of them.

Note also that ClientUI client relevance freely uses `sites`,
`relevant fixlets of sites`, and `relevant offer actions of sites` -
inspectors that *look* session-only but are perfectly valid on a client. Any
future attempt to type relevance from the inspectors it uses must not treat
bare `sites` / `fixlets` / `offer actions` as session markers.

The real deployed filenames are `_dashboard.html` (visible to the end user)
and `_technician.html` (`CTRL-ALT-SHIFT-T` from the client UI); the copies
here are renamed to match this folder's naming convention, which also proves
that classification does not depend on the basename.

## Naming them, in code and in prose

Never write plain "relevance" in code, docs, or file and variable names when a
specific dialect is meant - say **client relevance** or **session relevance**.
"Relevance" alone is reserved for statements that are genuinely true of both.

This is not style pedantry. The two dialects share enough syntax that a
statement can look completely ordinary and still be impossible in the place it
was written, and the single most common way that happens is somebody reading
"relevance" in a document, an issue, or a function name and assuming the
dialect they had in mind.

## Each engine rejects the other's vocabulary outright

Confirmed on both engines (see
[`universal_relevance.md`](universal_relevance.md) for the method):

```
Q: number of bes computers                                 (client)
E: The operator "bes computers" is not defined.

Q: number of processors                                    (session)
E: The operator "processors" is not defined.
```

The failure mode is worth understanding precisely, because it shapes what
tooling can do. A dialect mistake is:

- **cheap to catch at an engine** - it is a hard undefined-operator error
  naming the offending phrase, not a wrong answer;
- **invisible before then** - the statement is perfectly well-formed. It
  tokenizes, parses, and groups exactly as intended. Nothing but a vocabulary
  check can notice.

So the cost of a dialect error is entirely a function of how late it is found,
and it is found either instantly or in production. That asymmetry is the reason
this package types statements by content at all, rather than trusting the file
they were found in.

It also means the two failures are *not* symmetric in consequence. A session
statement in a `<Relevance>` element fails on every endpoint in the deployment,
quietly, as non-applicability. A client statement in a dashboard fails once, in
front of the person who wrote it.
