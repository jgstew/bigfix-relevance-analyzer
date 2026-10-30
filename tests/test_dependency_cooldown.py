"""The Python half of the 7-day release-age policy, and its one exception.

Everything uv resolves waits 7 days after release, by hand (`exclude-newer` in
pyproject.toml) and automated (dependabot's `cooldown`), because a release
published minutes ago is the likeliest to be a compromised one. The author's
own `bigfix*` libraries from github.com/jgstew are exempt: they carry fixes
this project wants as soon as they ship. The npm half lives in
`test_playground_layout`.

The two entry points cannot see each other, so this holds them to one list.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPENDABOT = REPO_ROOT / ".github" / "dependabot.yml"

#: The author's own libraries this project resolves. Exempt, and nothing else is.
OWN_PACKAGES = {"bigfix-remote-client-relevance", "bigfix-remote-session-relevance"}


def _uv_settings() -> dict[str, object]:
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        settings: dict[str, object] = tomllib.load(handle)["tool"]["uv"]
    return settings


def _dependabot_uv_cooldown() -> dict[str, object]:
    """The `uv` ecosystem's `cooldown` mapping: scalars, and lists of strings.

    Read by indentation rather than with a YAML parser, which is not a
    dependency here; it covers the flat block this file actually holds.
    """
    lines = DEPENDABOT.read_text(encoding="utf-8").splitlines()
    start = next(
        i for i, line in enumerate(lines) if re.match(r'\s*- package-ecosystem: "?uv"?\s*$', line)
    )
    entry_indent = len(lines[start]) - len(lines[start].lstrip())
    cooldown: dict[str, object] = {}
    key_indent: int | None = None
    current: str | None = None
    inside = False
    for line in lines[start + 1 :]:
        code = line.split(" #", 1)[0].rstrip()
        if not code.strip() or code.lstrip().startswith("#"):
            continue
        indent = len(code) - len(code.lstrip())
        if indent <= entry_indent:
            break  # the next ecosystem
        if not inside:
            inside = code.strip() == "cooldown:"
            continue
        if key_indent is None:
            key_indent = indent
        if indent < key_indent:
            break  # back out of the cooldown block
        item = code.strip()
        if indent == key_indent:
            key, _, value = item.partition(":")
            current = key
            cooldown[key] = value.strip().strip('"') if value.strip() else []
        elif item.startswith("- ") and current is not None:
            values = cooldown[current]
            assert isinstance(values, list)
            values.append(item.removeprefix("- ").strip().strip('"'))
    return cooldown


def test_everything_else_keeps_the_seven_day_delay() -> None:
    assert _uv_settings()["exclude-newer"] == "7 days"
    assert _dependabot_uv_cooldown()["default-days"] == "7"


def test_uv_exempts_exactly_the_authors_own_libraries() -> None:
    assert _uv_settings()["exclude-newer-package"] == dict.fromkeys(OWN_PACKAGES, "0 days")


def test_every_exempt_library_is_one_the_lock_resolves() -> None:
    """An exemption for a package nothing resolves is a stale entry."""
    lock = (REPO_ROOT / "uv.lock").read_text(encoding="utf-8")
    resolved = set(re.findall(r'^name = "([^"]+)"$', lock, re.MULTILINE))
    assert resolved >= OWN_PACKAGES
    assert {name for name in resolved if name.startswith("bigfix")} == OWN_PACKAGES | {
        "bigfix-relevance-analyzer"  # this project itself
    }


def test_dependabot_exempts_the_same_libraries_as_uv() -> None:
    excluded = _dependabot_uv_cooldown().get("exclude")
    assert isinstance(excluded, list), "dependabot's uv cooldown has no exclude list"
    assert set(excluded) == OWN_PACKAGES
