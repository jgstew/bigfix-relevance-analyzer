# Performance tools

Not shipped, not imported by the package, not collected by pytest (`testpaths`
is `tests`). Scripts a human runs by hand, like the generators beside them.

## `parity.py` - the equivalence gate

Optimising this package is supposed to be invisible. This is how that gets
checked: two implementations are run over every relevance statement available
and must produce byte-identical output.

```bash
# every statement in the repo: 284, about a second
python tools/perf/parity.py --arm analyze

# and every statement in a real content checkout: 41,243, about ten seconds
python tools/perf/parity.py --arm parse --extra-corpus ../bigfix-content
```

Arms are `analyze`, `parse` and `tokenize`. `--extra-corpus` is opt-in and no
test passes it, because the committed suite has to run on a machine without
that checkout - but for anything touching the lexer or the parser it is worth
the ten seconds. It found nothing the small corpus missed, so far; the point is
that a 145x wider net is cheap.

`CANDIDATES` is empty on `main`. While an optimisation is in flight, keep the
old implementation beside the new one as a `_legacy` twin and register the pair
there; delete both when it lands. With nothing registered the script compares
an arm with itself, which is still a real check - it exercises the corpus and
each arm's internal assertions, including the tokenizer's roundtrip guarantee,
which no cross-arm comparison could catch because both arms would share the
bug.

## Measuring

There is deliberately no benchmark harness here. Every change made so far had
an effect far larger than measurement noise (1.6x, 1.5x), so `timeit` in a
throwaway `python -c` settled each one, and a harness would have been more code
than the changes it graded.

If something ever lands close to the noise floor, the three things worth
building - and not more - are paired A/B interleaving in one process (separate
runs drift by more than the effects being chased), an A/A calibration to
establish what the floor actually is, and a replication requirement. Anything
smaller than the A/A floor is not a result. Pin the interpreter in whatever you
write: `uv run` resolves CPython 3.13, the bare `python3` on this machine is
3.14, and the two disagree by enough to invert a conclusion.

## Type checking

`tools/perf` is under `mypy --strict` and pyright; the rest of `tools/` is not,
because the two `build_playground.py` files under `tools/playground-wasm/`
share a module name and mypy refuses the tree before checking anything.
Worth fixing, separately.
