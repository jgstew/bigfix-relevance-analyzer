"""The release's pre-commit gate: the same hooks that guard PRs, minus uv-audit.

A release runs every manual-stage hook over the full tree through the reusable
pre-commit workflow. ``uv-audit`` checks the lock against live advisories, so a
fresh one fails a release that the PR it came from passed, and the fixed
version is often still inside the 7-day dependency cooldown. James's call
(PR #200): skip it on a release. PRs and pushes to main still run it.
"""

from __future__ import annotations

import re

from _helpers import REPO_ROOT

WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _job(text: str, name: str) -> str:
    """The YAML of top-level job ``name``: up to the next job at its indent."""
    match = re.search(rf"^  {name}:\n(.*?)(?=^  \S|\Z)", text, re.M | re.S)
    assert match, name
    return match.group(1)


def test_the_release_skips_uv_audit_in_its_pre_commit_gate() -> None:
    job = _job((WORKFLOWS / "tag_and_release.yaml").read_text("utf-8"), "pre-commit")
    assert "uses: ./.github/workflows/pre-commit.yaml" in job
    assert re.search(r"^      skip-hooks: uv-audit$", job, re.M), job


def test_pre_commit_takes_hooks_to_skip_only_from_a_caller() -> None:
    """The input is added to SKIP; without one (a PR, a push, a dispatch)
    only the hook that can never pass on a runner is skipped."""
    text = (WORKFLOWS / "pre-commit.yaml").read_text("utf-8")
    trigger = text[text.index("  workflow_call:") : text.index("\npermissions:")]
    assert "skip-hooks:" in trigger
    assert "default: ''" in trigger or 'default: ""' in trigger
    (skip,) = re.findall(r"^      SKIP: (.*)$", text, re.M)
    assert "no-commit-to-branch" in skip
    assert "inputs.skip-hooks" in skip
