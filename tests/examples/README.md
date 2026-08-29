# Example relevance files

Sample content used by tests to measure relevance extraction. A corresponding
test (e.g. `tests/test_examples.py`) should iterate these directories to
parse/extract/analyze each file and assert expected results.

## Which dialect is which

The explanation of client relevance versus session relevance - where each is
evaluated, which file types and elements carry which, the ClientUI exception to
"HTML means session relevance", and the signal-to-dialect table - lives in
[`docs/reference/dialects.md`](../../docs/reference/dialects.md). It moved there
because it is the language reference this package *ships* (see
`bigfix_relevance_analyzer.reference`), not merely notes about this folder, and
keeping a second copy here would mean neither could be edited on its own.

This folder is organized by which dialect each example belongs to, plus a
`mixed_context/` folder for the (real-world, common) case of a single BES file
that uses both in different parts of itself.

## Layout

```
client_relevance/
    fixlets/            Fixlet .bes files (applicability + description)
    tasks/               Task .bes files
    analyses/            Analysis .bes files (relevance + Property relevance)
    baselines/           Baseline .bes files (top-level + per-component relevance)
    computer_groups/     Manual and automatic computer group .bes files
                          (SearchComponentRelevance)
    clientui/            ClientUI dashboard .html files, rendered by the BES
                          Client on the endpoint, with client relevance in
                          <?Relevance ?> processing instructions - the one
                          case where HTML relevance is *client* relevance
                          (see docs/reference/dialects.md)
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
| `client_relevance/clientui/clientui_dashboard_client_relevance_substitution.html` | `clientui/information/_dashboard.html` |
| `client_relevance/clientui/clientui_dashboard_no_product_meta.html` | `clientui/refresh/_dashboard.html` |
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
