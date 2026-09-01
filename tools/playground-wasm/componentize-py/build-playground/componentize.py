#!/usr/bin/env python3
"""Compile the analyzer wheel and ``app.py`` into one WebAssembly component.

    python tools/playground-wasm/componentize-py/build-playground/componentize.py \\
        --wheel dist/bigfix_relevance_analyzer-*.whl \\
        --work dist/componentize

Step 1 of 3 in building the componentize-py page:

    componentize.py   wheel            -> <work>/analyzer.wasm     (this script)
    transpile.mjs     analyzer.wasm    -> <work>/bundle.mjs + cores
    build_playground.py  those         -> playground/....html

It is the componentize-py analogue of the Pyodide pipeline's
``precompile_wheel.mjs``: the step that turns the built wheel into whatever form
that runtime actually consumes.

Two things here are load-bearing and easy to get wrong.

**Only the app module goes on the Python path.** ``componentize-py`` bundles what
it finds in each ``-p`` directory, so pointing it at this source directory --
which also holds a template, a JS stub and these scripts -- put 3.5 MiB of
non-Python files inside the component, measured. Worse, a built page left in
here would be embedded into the next component. ``app.py`` is therefore copied
into a staging directory that contains nothing else.

**The wheel is installed, not copied.** ``uv pip install --target`` is what
produces the ``.dist-info`` directory that ``importlib.metadata`` reads, and
``bigfix_relevance_analyzer.__init__`` resolves ``__version__`` through it.
Vendoring the package directory alone would build a component that works but
reports version ``0.0.0``. The smoke test asserts it does not.
"""

from __future__ import annotations

import argparse
import glob
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
WIT_DIR = HERE / "wit"
APP_MODULE = HERE / "app.py"

# The world in wit/analyzer.wit. The app module may not share this name --
# componentize-py generates a module for the world and Python cannot load two
# top-level modules with the same name -- which is why the app is `app.py`.
WORLD = "analyzer"


def _run(argv: list[str], label: str) -> None:
    sys.stderr.write(f"  {label}\n")
    subprocess.run(argv, check=True)


def _resolve_single(pattern: str, *, kind: str) -> Path:
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise SystemExit(f"no {kind} found matching {pattern!r}")
    if len(matches) > 1:
        raise SystemExit(
            f"expected exactly one {kind} matching {pattern!r}, found {len(matches)}: {matches}"
        )
    return Path(matches[0])


def componentize(wheel_path: Path, work_dir: Path) -> Path:
    """Build the component into ``work_dir`` and return its path."""
    deps = work_dir / "deps"
    bindings = work_dir / "bindings"
    app_dir = work_dir / "app"
    out_path = work_dir / f"{WORLD}.wasm"

    # A stale staging directory would silently contribute to the component.
    for stale in (deps, bindings, app_dir):
        shutil.rmtree(stale, ignore_errors=True)
    app_dir.mkdir(parents=True, exist_ok=True)

    # See the module docstring: installed, not vendored, so .dist-info exists
    # and __version__ resolves to something other than "0.0.0".
    _run(
        ["uv", "pip", "install", "--quiet", "--target", str(deps), str(wheel_path)],
        f"stage {wheel_path.name}",
    )

    # Generating the bindings is optional -- `componentize` would generate them
    # internally -- but doing it explicitly puts wit_world/ somewhere readable,
    # which is the only way to check the generated protocol's shape. It is named
    # for the module (`wit_world.WitWorld`), not for the WIT world, and the
    # implementing class in app.py must match it exactly.
    _run(
        ["componentize-py", "-d", str(WIT_DIR), "-w", WORLD, "bindings", str(bindings)],
        "generate bindings",
    )

    # Only the app module, nothing else from this source directory.
    shutil.copy2(APP_MODULE, app_dir / APP_MODULE.name)

    componentize_argv = [
        "componentize-py",
        "-d",
        str(WIT_DIR),
        "-w",
        WORLD,
        "componentize",
        "-p",
        str(app_dir),
        "-p",
        str(bindings),
        "-p",
        str(deps),
        APP_MODULE.stem,
        "-o",
    ]

    # Two passes, and the first one's output is thrown away.
    #
    # componentize-py imports the app at build time using its own embedded
    # CPython, which writes __pycache__ into these staging directories as a side
    # effect -- too late for the pass that caused it. On a subsequent pass it
    # finds those .pyc files and bundles them instead of the .py source, which
    # measured 3.4 MiB smaller: 24.9 MB cold versus 21.5 MB warm, from
    # byte-identical inputs.
    #
    # That is a build-determinism bug as much as a size one -- the same wheel
    # produced two different components depending on whether the directory had
    # been used before. Warming up deliberately makes the small result the only
    # result. It is the same trade the Pyodide pipeline makes in
    # precompile_wheel.mjs, and for the same reason: compile with the runtime's
    # own CPython, because a .pyc from the host's Python has the wrong magic
    # number and would simply be ignored.
    #
    # This buys stable *size*, not byte-for-byte reproducibility:
    # componentize-py 0.25.0 emits components differing by a couple of hundred
    # bytes across runs on byte-identical inputs (measured). That is upstream
    # and nothing here can fix it, so do not write a test asserting two builds
    # are identical -- assert on size instead.
    warmup_path = work_dir / f"{WORLD}.warmup.wasm"
    _run([*componentize_argv, str(warmup_path)], "componentize (warm-up pass, discarded)")
    warmup_size = warmup_path.stat().st_size
    warmup_path.unlink()

    if not any(deps.rglob("__pycache__")):
        raise SystemExit(
            "the warm-up pass did not leave __pycache__ in the staged deps -- "
            "componentize-py's build-time import behaviour has changed, so this "
            "script's two-pass trick is no longer doing anything. Re-measure "
            "before removing it."
        )

    _run([*componentize_argv, str(out_path)], "componentize")

    size = out_path.stat().st_size
    mib = size / (1024 * 1024)
    print(
        f"wrote {out_path} ({mib:.1f} MiB, {(warmup_size - size) / 1048576:.1f} MiB "
        f"smaller than the cold pass)"
    )
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wheel", required=True, help="path or glob to the built wheel")
    parser.add_argument("--work", required=True, help="working directory for staging + output")
    args = parser.parse_args(argv)

    work_dir = Path(args.work)
    work_dir.mkdir(parents=True, exist_ok=True)
    componentize(_resolve_single(args.wheel, kind="wheel"), work_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
