"""Tools every experiment agent gets, bound to that experiment's workspace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anthropic import beta_tool

from venture_lab.ledger import Ledger
from venture_lab.policy import ACTION_KINDS, Policy

MAX_ARTIFACT_CHARS = 200_000


class Workspace:
    """Per-experiment artifact directory with path-traversal protection."""

    def __init__(self, root: Path, experiment: str):
        self.root = (root / experiment).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        path = (self.root / relative_path).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError(f"path escapes the experiment workspace: {relative_path}")
        return path

    def list(self) -> list[str]:
        return sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file())


def build_tools(experiment: str, ledger: Ledger, policy: Policy, workspace: Workspace) -> list[Any]:
    kinds = ", ".join(f"{k} ({v})" for k, v in ACTION_KINDS.items())

    @beta_tool
    def save_artifact(path: str, content: str) -> str:
        """Create or overwrite a file in this experiment's workspace: plans, copy,
        email drafts, landing pages, configs, research notes, reports.

        Args:
            path: Relative path such as "research/competitors.md" or "site/index.html".
            content: Full file content (UTF-8 text).
        """
        if len(content) > MAX_ARTIFACT_CHARS:
            return f"Error: content is {len(content)} chars; split it into files under {MAX_ARTIFACT_CHARS}."
        target = workspace.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Saved {path} ({len(content)} chars)."

    @beta_tool
    def read_artifact(path: str) -> str:
        """Read a file from this experiment's workspace.

        Args:
            path: Relative path returned by list_artifacts.
        """
        target = workspace.resolve(path)
        if not target.is_file():
            return f"Error: {path} does not exist."
        return target.read_text(encoding="utf-8")[:MAX_ARTIFACT_CHARS]

    @beta_tool
    def list_artifacts() -> str:
        """List every file in this experiment's workspace."""
        files = workspace.list()
        return "\n".join(files) if files else "(workspace is empty)"

    @beta_tool
    def record_metric(name: str, value: float, note: str = "") -> str:
        """Record a KPI you measured yourself (e.g. pages published, prospects
        researched, drafts produced). Revenue, customers and replies must come
        from the human or an integration; record those only if you can cite the source.

        Args:
            name: snake_case metric key matching the experiment KPIs, e.g. "prospects_researched".
            value: Current cumulative value (not a delta).
            note: How it was measured.
        """
        ledger.record_metric(experiment, name, value, source="agent", note=note)
        return f"Recorded {name}={value:g} (source=agent)."

    @beta_tool
    def log_learning(text: str) -> str:
        """Save a durable lesson for future runs of this experiment: what worked,
        what failed, a decision and its reason. Keep each entry to 1-3 sentences.

        Args:
            text: The lesson.
        """
        ledger.add_learning(experiment, text)
        return "Learning saved."

    @beta_tool
    def request_action(
        kind: str,
        title: str,
        details_json: str,
        one_time_usd: float = 0.0,
        monthly_usd: float = 0.0,
    ) -> str:
        """Ask to perform an outward-facing or paid action. Spending money, creating
        accounts and legal commitments always wait for a human. Put everything the
        executor needs in details_json (recipient, exact message text, URL, vendor,
        plan name, justification) so it can be approved without follow-up questions.

        Args:
            kind: One of: spend, account, legal, outreach, customer_comms, publish_social, publish_owned, deploy.
            title: One-line summary a busy human can approve at a glance.
            details_json: JSON object with the full specifics of the action.
            one_time_usd: Upfront cost in USD, if any.
            monthly_usd: Recurring monthly cost in USD, if any.
        """
        try:
            details = json.loads(details_json)
            if not isinstance(details, dict):
                raise TypeError("details_json must be a JSON object")
        except (TypeError, ValueError) as exc:
            return f"Error: invalid details_json ({exc})."
        if kind not in ACTION_KINDS:
            return f"Error: unknown kind {kind!r}. Valid kinds: {kinds}"
        decision = policy.request_action(experiment, kind, title, details, one_time_usd, monthly_usd)
        return decision.message()

    @beta_tool
    def list_actions(status: str = "") -> str:
        """List this experiment's requested actions and their decisions, to see
        what the human approved, rejected (with reasons) or executed.

        Args:
            status: Optional filter: pending, approved, rejected or executed.
        """
        rows = ledger.approvals(experiment, status or None)
        if not rows:
            return "(no actions)"
        return "\n".join(
            f"#{r['id']} [{r['status']}] {r['kind']}: {r['title']}"
            + (f" - note: {r['decision_note']}" if r["decision_note"] else "")
            for r in rows[-40:]
        )

    return [save_artifact, read_artifact, list_artifacts, record_metric, log_learning, request_action, list_actions]
