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


def _dependabot_uv_entry() -> str:
    """The text of the `uv` ecosystem's entry, up to the next one."""
    text = DEPENDABOT.read_text(encoding="utf-8")
    start = text.index('- package-ecosystem: "uv"')
    end = text.find("- package-ecosystem:", start + 1)
    return text[start : end if end != -1 else None]


def test_everything_else_keeps_the_seven_day_delay() -> None:
    assert _uv_settings()["exclude-newer"] == "7 days"
    assert re.search(r"^\s+default-days: 7$", _dependabot_uv_entry(), re.MULTILINE)


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
    entry = _dependabot_uv_entry()
    block = re.search(r"^\s+exclude:\n((?:\s+- .+\n)+)", entry, re.MULTILINE)
    assert block, "dependabot's uv cooldown has no exclude list"
    names = {line.strip().removeprefix("- ").strip('"') for line in block[1].splitlines()}
    assert names == OWN_PACKAGES
