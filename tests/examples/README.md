# Example relevance files

Sample content used by tests to measure relevance extraction. A corresponding
test (e.g. `tests/test_examples.py`) should iterate these directories to
parse/extract/analyze each file and assert expected results.

## Client relevance vs. session relevance

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

This folder is organized by which dialect each example belongs to, plus a
`mixed_context/` folder for the (real-world, common) case of a single BES
file that uses both in different parts of itself.

## Layout

```
client_relevance/
    fixlets/            Fixlet .bes files (applicability + description)
    tasks/               Task .bes files
    analyses/            Analysis .bes files (relevance + Property relevance)
    baselines/           Baseline .bes files (top-level + per-component relevance)
    computer_groups/     Manual and automatic computer group .bes files
                          (SearchComponentRelevance)
    plain_text/          Files whose entire contents is one client relevance
                          expression, no markup
    markdown_codeblocks/ Markdown files with client relevance in a fenced
                          ``` code block, where the whole block is the
                          expression

session_relevance/
    dashboards/          Dashboard .ojo files with <?relevance ?> / <?Relevance ?>
                          processing instructions embedded in HTML (static:
                          substituted once when the page renders)
    webreports/          Web report .besrpt/.beswrpt/.webreport files (same
                          static <?Relevance ?> mechanism)
    dynamic_javascript/  Dashboards, a web report, and a Fixlet description
                          that evaluate session relevance *dynamically* from
                          JavaScript in the browser (Relevance(...) /
                          EvaluateRelevance(...)) instead of, or in addition
                          to, a static processing instruction
    plain_text/          Files whose entire contents is one session relevance
                          expression, no markup
    markdown_codeblocks/ Markdown files with session relevance in a fenced
                          ``` code block, where the whole block is the
                          expression

mixed_context/
    A Task .bes file whose <Relevance> (applicability, client relevance) is
    separate from a <?relevance ?> processing instruction embedded in its
    <Description> (rendered by the console, session relevance) - one file,
    two distinct relevance dialects, each doing a different job.
```

## Naming

Files are named for what they're an example *of* (content type + notable
relevance feature), not for the original content's title - e.g.
`fixlet_registry_and_active_directory_relevance.bes` rather than
`Add AD Domain to DNS Suffix Search List if missing - Windows.bes`. Names
avoid spaces so paths are shell- and URL-friendly.

## Provenance

Most files here are copied from the public
[`jgstew/bigfix-content`](https://github.com/jgstew/bigfix-content) repo, a
large real-world collection of BigFix content, chosen as small, clean,
self-contained examples of each content type. Content is unchanged except
for being renamed, with one exception:
`session_relevance/dynamic_javascript/fixlet_description_relevance_via_javascript.bes`
also had a few incidental corrections applied by this project's own
`typos`/`codespell`/`fix-files-to-ascii` pre-commit hooks before those hooks
were configured to leave this directory alone - the relevance expressions
and JS mechanism are otherwise untouched.

| File in this folder | Original source (`bigfix-content/...`) |
| --- | --- |
| `client_relevance/fixlets/fixlet_multi_clause_relevance.bes` | `fixlet/Backup Windows Security Log.bes` |
| `client_relevance/fixlets/fixlet_registry_and_active_directory_relevance.bes` | `fixlet/Add AD Domain to DNS Suffix Search List if missing - Windows.bes` |
| `client_relevance/tasks/task_time_based_relevance.bes` | `fixlet/Check Disk Usage - Linux.bes` |
| `client_relevance/analyses/analysis_relevance_simple_property.bes` | `analyses/SSH Config - Linux Unix.bes` |
| `client_relevance/analyses/analysis_relevance_complex_property.bes` | `analyses/Hardware Information (Universal) - SMBIOS.bes` |
| `client_relevance/baselines/baseline_relevance_with_components.bes` | `baselines/Docker - Stop & Delete all containers - Linux.bes` |
| `client_relevance/computer_groups/computer_group_manual_relevance.bes` | `groups/Linux Docker Hosts.bes` |
| `client_relevance/computer_groups/computer_group_automatic_relevance.bes` | `AutomaticComputerGroups/VM - AWS.bes` |
| `session_relevance/dashboards/dashboard_session_relevance_html_table.ojo` | `dashboards/SessionRelevanceProperties.ojo` |
| `session_relevance/dashboards/dashboard_session_relevance_chart.ojo` | `dashboards/ReportingPieCharts.ojo` |
| `session_relevance/webreports/webreport_session_relevance_basic.besrpt` | `webreports/PC_Models_By_Domain.besrpt` |
| `session_relevance/webreports/webreport_session_relevance_chart.besrpt` | `webreports/HiddenContentChart.besrpt` |
| `session_relevance/plain_text/session_relevance_plain_text.bsr` | `session_relevance/Site-ID-ApplicableOFpatches.bsr` |
| `session_relevance/dynamic_javascript/dashboard_relevance_via_javascript_static_and_dynamic.ojo` | `dashboards/HelloWorld_template.ojo` |
| `session_relevance/dynamic_javascript/dashboard_relevance_via_javascript_interactive.ojo` | `dashboards/AnotherSessionRelevanceTester.ojo` |
| `session_relevance/dynamic_javascript/webreport_relevance_via_javascript.besrpt` | `webreports/GenericDataTables.besrpt` |
| `session_relevance/dynamic_javascript/fixlet_description_relevance_via_javascript.bes` | `fixlet/RESTAPI_ Generate uninstall tasks for all MSI applications on target computer - Windows.bes` |
| `mixed_context/task_with_client_and_session_relevance.bes` | `fixlet/Session Relevance in Description Example - Universal.bes` |

`fixlet_description_relevance_via_javascript.bes` is itself a mixed-context
example: its top-level `<Relevance>` elements (applicability) are client
relevance, while the `Relevance('...')` calls inside its `<Description>`'s
`<script>` are dynamic session relevance. It's filed under
`dynamic_javascript/` because that JS mechanism is the point of the example,
but it belongs conceptually alongside `mixed_context/` too.

Two files were **not** found as-is in that source (it has no
plain-relevance-only files for client relevance, and none of its markdown
uses fenced ``` code blocks - only inline single-backtick spans). They were
constructed for this project by combining or re-wrapping real relevance
expressions pulled from that repo, so the relevance content itself is real
and valid, only the file/wrapper is new:

- `client_relevance/plain_text/client_relevance_plain_text.rel` combines the
  two `<Relevance>` clauses from `bigfix-content/fixlet/Backup Windows
  Security Log.bes`.
- `client_relevance/markdown_codeblocks/client_relevance_markdown_codeblock.md`
  re-wraps one line from `bigfix-content/relevance/Mac_ModelName.md`.
- `session_relevance/markdown_codeblocks/session_relevance_markdown_codeblock.md`
  re-wraps one line from `bigfix-content/session_relevance/link-to-docs.md`.
