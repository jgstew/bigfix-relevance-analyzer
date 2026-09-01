"""Shared plumbing for the ``build-playground`` scripts of both WASM runtimes.

Each runtime's ``build_playground.py`` differs only in *what* it embeds --
Pyodide's runtime assets and a wheel, or componentize-py's gzipped core wasm
modules and a bundled JS glue. The mechanics of getting bytes into
``template.html`` are identical, and so are the two failure modes worth being
paranoid about:

* a placeholder left unreplaced, which would ship a page containing the literal
  text ``%%BUNDLE_JS%%`` and fail only when someone opened it;
* a shared partial that silently failed to inject, which would ship a page with
  no styling or no rendering code.

Both are hard failures here rather than warnings.

Pure standard library, deliberately: these scripts run in CI from a bare
``python3`` with nothing installed, before (and independently of) the package's
own dependencies. See ``.github/workflows/wasm-html.yaml``.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

COMMON_DIR = Path(__file__).parent

# The partials every template injects, and the placeholder each one lands at.
# A template need not use all of them -- see `render` -- but a partial named
# here that is missing from disk is a hard failure.
SHARED_PARTIALS = {
    "%%SHARED_STYLE%%": "shared_style.html",
    "%%SHARED_PREFLIGHT%%": "shared_preflight.html",
    "%%SHARED_SCRIPT%%": "shared_script.html",
}

# Anything of the form %%NAME%%. Used to catch leftovers, including placeholders
# a caller forgot about entirely rather than only the ones it tried to fill.
_PLACEHOLDER_RE = re.compile(r"%%[A-Z0-9_]+%%")


def b64_file(path: Path) -> str:
    """Base64 of a file's bytes, as ASCII text ready to paste into a template."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def read_partial(name: str) -> str:
    """Read one shared partial, stripping its leading HTML comment.

    Each partial opens with a comment explaining that it is shared and must be
    edited at the source. That is guidance for whoever opens the partial, not
    something worth repeating in every built page, so it is dropped here.
    """
    path = COMMON_DIR / name
    if not path.is_file():
        raise SystemExit(f"missing shared partial {path}")
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("<!--"):
        _, _, text = text.partition("-->")
    return text.lstrip("\n")


def render(template_path: Path, substitutions: dict[str, str]) -> str:
    """Return ``template_path`` with the shared partials and ``substitutions`` filled in.

    Partials are injected first so a partial containing its own placeholder
    still gets filled by ``substitutions`` -- one level of nesting, which is all
    that is wanted; more would make a template's final content hard to predict
    from reading it.

    Raises ``SystemExit`` if a named substitution has no placeholder to fill (a
    caller and template that disagree), or if any placeholder survives.
    """
    rendered = template_path.read_text(encoding="utf-8")

    for placeholder, filename in SHARED_PARTIALS.items():
        if placeholder in rendered:
            rendered = rendered.replace(placeholder, read_partial(filename))

    for placeholder, value in substitutions.items():
        if placeholder not in rendered:
            raise SystemExit(f"template {template_path} has no {placeholder} placeholder")
        rendered = rendered.replace(placeholder, value)

    leftover = sorted(set(_PLACEHOLDER_RE.findall(rendered)))
    if leftover:
        raise SystemExit(
            f"{template_path} still contains unreplaced placeholder(s) after "
            f"substitution: {leftover}"
        )
    return rendered


def write_page(out_path: Path, rendered: str) -> int:
    """Write the built page, creating its directory, and return its size in bytes."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    return out_path.stat().st_size


def mib(byte_count: int) -> str:
    """Format a byte count the way both build scripts report sizes."""
    return f"{byte_count / (1024 * 1024):.1f} MiB"
