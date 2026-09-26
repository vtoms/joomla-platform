"""Guardrails: which actions an agent may take alone, and API budget caps.

Agents never hold payment credentials or sign up for accounts. Anything that
spends money, creates an account / accepts terms of service, or makes a legal
commitment is always queued for a human, whatever the config says. Other
outward-facing actions are queued by default and can be switched to
auto-approve per kind in `venture_lab.toml` once you trust an experiment.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any

from venture_lab.config import Settings
from venture_lab.ledger import Ledger

ACTION_KINDS: dict[str, str] = {
    "spend": "Pay for anything: a subscription, credits, ads, a domain, a contractor.",
    "account": "Create an account, accept terms of service, or connect an integration.",
    "legal": "Sign or send a contract, register an entity, make compliance or earnings claims.",
    "outreach": "First-touch message to a prospect (email, DM, LinkedIn, form).",
    "customer_comms": "Message an existing customer or lead who opted in.",
    "publish_social": "Post to a third-party platform (YouTube, Instagram, TikTok, Reddit, X).",
    "publish_owned": "Publish on a property you own (your site, blog, newsletter, store listing).",
    "deploy": "Deploy code or configuration to a live, customer-facing system.",
}
NEVER_AUTO = frozenset({"spend", "account", "legal"})


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class ActionDecision:
    approval_id: int
    status: str  # pending | approved

    def message(self) -> str:
        if self.status == "approved":
            return (
                f"Action #{self.approval_id} auto-approved by policy and handed to the executor. "
                "Treat it as done once it shows as executed."
            )
        return (
            f"Action #{self.approval_id} queued for human approval. Do not assume it will happen; "
            "continue with work that does not depend on it."
        )


class Policy:
    def __init__(self, settings: Settings, ledger: Ledger):
        self.settings = settings
        self.ledger = ledger

    # -- approvals --------------------------------------------------------
    def auto_approves(self, kind: str) -> bool:
        return kind not in NEVER_AUTO and kind in self.settings.auto_approve

    def request_action(
        self,
        experiment: str,
        kind: str,
        title: str,
        details: dict[str, Any],
        one_time_usd: float = 0.0,
        monthly_usd: float = 0.0,
    ) -> ActionDecision:
        if kind not in ACTION_KINDS:
            raise ValueError(f"unknown action kind {kind!r}; expected one of {sorted(ACTION_KINDS)}")
        if (one_time_usd or monthly_usd) and kind != "spend":
            # Anything with a price tag is a spend decision, whatever it was labelled.
            details = {**details, "original_kind": kind}
            kind = "spend"
        status = "approved" if self.auto_approves(kind) else "pending"
        approval_id = self.ledger.add_approval(
            experiment, kind, title, details, one_time_usd, monthly_usd, status=status
        )
        if status == "approved":
            self.dispatch(approval_id)
        return ActionDecision(approval_id, status)

    def dispatch(self, approval_id: int) -> bool:
        """Send an approved action to the executor webhook (e.g. an n8n workflow
        that sends the email from your own mailbox). Returns True if sent."""
        action = self.ledger.approval(approval_id)
        if action["status"] != "approved" or not self.settings.webhook_url:
            return False
        payload = {**action, "details": json.loads(action["details"])}
        req = urllib.request.Request(
            self.settings.webhook_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:  # operator-configured URL
            ok = 200 <= resp.status < 300
        if ok:
            self.ledger.decide(approval_id, "executed", "dispatched to webhook")
        return ok

    # -- API budget -------------------------------------------------------
    def api_budget(self, experiment: str, default_usd: float) -> float:
        override = self.settings.for_experiment(experiment).api_budget_usd_month
        return float(override if override is not None else default_usd)

    def check_budget(self, experiment: str, default_usd: float) -> None:
        spent_global = self.ledger.spend_this_month()
        if spent_global >= self.settings.global_api_budget_usd_month:
            raise BudgetExceeded(
                f"global API budget reached: ${spent_global:.2f} of "
                f"${self.settings.global_api_budget_usd_month:.2f} this month"
            )
        cap = self.api_budget(experiment, default_usd)
        spent = self.ledger.spend_this_month(experiment)
        if spent >= cap:
            raise BudgetExceeded(f"{experiment} API budget reached: ${spent:.2f} of ${cap:.2f} this month")
