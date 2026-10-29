# Real BES templates, vendored for the grammar tests

Two Mustache-templated BES files from the Unlicense-licensed
[jgstew/bigfix-content](https://github.com/jgstew/bigfix-content), copied
at commit `d524c7381bd53fb7f9ddb826d1ced9223c721d82` (#122), unchanged but for
line endings: both are CRLF here, as this repository's `.editorconfig` requires
of BES files (upstream, the Meltdown file mixes CRLF and LF, and the BIOS file
is LF).

| Here | There |
|---|---|
| `meltdown-spectre-detection.bes.mustache` | `templates/Run Microsoft Meltdown and Spectre Detection Tool - {{version}} - Windows.bes.mustache` |
| `bios-update.bes.template` | `fixlet/BIOS Update {{vendor}} {{model}} to {{bios_version}} - Windows.bes.template` |

They are renamed only because their real names hold `{{` and `}}`.
`../../grammar.test.mjs` tokenizes both as BES XML, to show that Mustache
placeholders and sections (`{{#name}}`/`{{/name}}`) open nothing that leaks past
`</BES>`.
