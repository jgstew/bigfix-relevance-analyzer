# bigfix-relevance-analyzer
A python module for working with BigFix Relevance generically. Extract, Analyze, etc.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and packaging
(build backend: hatchling), with a `src/` layout.

```bash
uv sync                    # create .venv and install project + dev dependencies
uv run pytest              # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy                # type-check
```

Set up the git hooks once (the extra hook types let `uv-sync` re-create `.venv` after a pull or
branch switch, and let the pre-push checks below actually run):

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type post-checkout --hook-type post-merge
```

A few slower checks (`pytest`, `uv lock --check`, `uv build --wheel`) are deferred to `git push`
rather than every commit, via `stages: [pre-push, manual]`. Run them by hand with:

```bash
uv run pre-commit run --all-files --hook-stage pre-push
```

The rest of the manual-only hooks (release/build checks, `uv audit`, pyproject and GitHub Actions
schema validation) don't run automatically at all - CI invokes them with `--hook-stage manual`,
which also picks up the `pre-push` ones above:

```bash
uv run pre-commit run --all-files --hook-stage manual
```

### Dependency freshness delay

`pyproject.toml` sets `[tool.uv] exclude-newer = "7 days"`, so `uv lock`/`uv sync`/`uv add` only
consider package versions that were published at least 7 days ago. This is a rolling window (not a
fixed date), giving newly published releases a week to be pulled before this project can depend on
them. To deliberately bypass this - for example to pull in an urgent security fix - run:

```bash
uv lock --exclude-newer=false
```
