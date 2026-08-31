# Documentation layers

The language documentation exists at two levels of detail, deliberately.

| Layer | Path | Audience | Constraints |
| --- | --- | --- | --- |
| **Expansive** | `docs/*.md` | humans, and anyone adding a finding | none - as long as it needs to be |
| **Distilled** | `docs/reference/*.md` | the MCP reference tools | tight; hard character budget |

**The expansive layer is the source of truth.** Each `docs/reference/*.md` is a
summary distilled from its `docs/` counterpart. A distilled document may omit
anything, and should - but it must never contradict the expansive one. When a
finding changes, change `docs/` first, then re-distil.

## Why the split exists

Every `*.md` under `docs/reference/` is embedded verbatim into
`src/bigfix_relevance_analyzer/reference/_prose.py` by
`tools/generate_reference_prose.py`, because the wheel packages `src/` only.
Those documents are then served as reference material, where they compete for a
context budget: `tests/test_reference.py` enforces a ceiling per document at
each detail level.

So the reference documents have to stay short, and that pressure is at odds
with recording *evidence* - verbatim engine transcripts, the host and date a
behaviour was confirmed on, the reasoning behind a rule, and the near-misses
worth not re-investigating. That material is what makes a finding trustworthy
and maintainable, and it is exactly what a size budget squeezes out first.

Nothing outside `docs/reference/` is read by the generator, so the expansive
layer is free of that budget entirely.

## The documents

| Expansive | Distilled | Covers |
| --- | --- | --- |
| [`universal_relevance.md`](universal_relevance.md) | [`reference/universal_relevance.md`](reference/universal_relevance.md) | evaluator semantics confirmed on **both** engines |
| [`syntax.md`](syntax.md) | [`reference/syntax.md`](reference/syntax.md) | grammar and shape - what parses, and how it groups |
| [`dialects.md`](dialects.md) | [`reference/dialects.md`](reference/dialects.md) | telling the two dialects apart |
| [`client_relevance.md`](client_relevance.md) | [`reference/client_relevance.md`](reference/client_relevance.md) | endpoint dialect; the platform axis |
| [`session_relevance.md`](session_relevance.md) | [`reference/session_relevance.md`](reference/session_relevance.md) | server dialect; the cardinality axis |
| [`qna.md`](qna.md) | *none, by design* | driving the local `QnA` evaluator: flags, output grammar, gotchas |

`qna.md` is the odd one out: a **tool** guide, not a language reference. It has
no distilled counterpart on purpose, because an MCP consumer cannot run a local
binary -- what it would do with the knowledge is nothing. The *findings* obtained
with QnA do reach the distilled layer, through `universal_relevance.md` and the
dialect documents; only the mechanics of driving it stay here.

The split between `syntax.md` and `universal_relevance.md` is grammar versus
semantics: **syntax** is what parses and how it groups, **universal relevance**
is what the evaluator then does with it. A fact earns a place in
`universal_relevance.md` only once it has been confirmed on a client engine and
a session engine, with the transcript pasted in.
