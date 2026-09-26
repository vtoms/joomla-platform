"""Data model for an experiment: thesis, offer, costs, phases and kill gates."""

from __future__ import annotations

import operator
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

OPS: dict[str, Callable[[float, float], bool]] = {
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
}


@dataclass(frozen=True)
class CostItem:
    item: str
    one_time_usd: float = 0.0
    monthly_usd: float = 0.0
    variable: str = ""  # usage-based fees, described in words
    required: bool = True  # False = optional / only when scaling
    note: str = ""


@dataclass(frozen=True)
class Marketing:
    """Go-to-market plan: organic channels first, paid tests only after proof."""

    positioning: str
    channels: tuple[str, ...]  # in priority order
    seo: tuple[str, ...]
    paid: tuple[CostItem, ...] = ()  # optional paid tests, with the trigger that unlocks them
    funding: str = ""  # verdict: does marketing need money, and when

    def paid_monthly(self) -> float:
        return sum(c.monthly_usd for c in self.paid)


@dataclass(frozen=True)
class Phase:
    name: str
    days: int  # nominal length
    goal: str
    tasks: tuple[str, ...]
    cadence: str = "daily"  # daily | weekdays | weekly


@dataclass(frozen=True)
class Gate:
    """A kill/continue check evaluated `day` days after the experiment starts.

    `verified` gates only count metrics reported by a human or an integration,
    never numbers the agent recorded itself (revenue, paying customers...)."""

    day: int
    metric: str
    op: str
    threshold: float
    verified: bool = True
    hard: bool = True  # failing a hard gate auto-pauses the experiment

    def evaluate(self, metrics: dict[str, dict[str, Any]], age_days: float) -> str:
        if age_days < self.day:
            return "pending"
        m = metrics.get(self.metric)
        if m is None or (self.verified and m["source"] == "agent"):
            return "fail"
        return "pass" if OPS[self.op](float(m["value"]), self.threshold) else "fail"

    def describe(self) -> str:
        return f"day {self.day}: {self.metric} {self.op} {self.threshold:g}" + (" (verified)" if self.verified else "")


@dataclass(frozen=True)
class Experiment:
    id: str
    rank: int
    name: str
    one_liner: str
    thesis: str
    customer: str
    offer: str
    pricing: str
    evidence: tuple[str, ...]
    risks: tuple[str, ...]
    compliance: tuple[str, ...]
    agent_does: tuple[str, ...]
    human_does: tuple[str, ...]
    costs: tuple[CostItem, ...]
    phases: tuple[Phase, ...]
    gates: tuple[Gate, ...]
    kpis: tuple[str, ...]
    api_budget_usd_month: float = 40.0
    model: str = "strategist"
    effort: str = "high"
    extra_tools: tuple[str, ...] = ()
    feeds: tuple[str, ...] = field(default=())  # experiments this one generates demand for
    marketing: Marketing | None = None

    # -- cost roll-ups (external spend only; API spend is capped separately) --
    def setup_cost(self, required_only: bool = True) -> float:
        return sum(c.one_time_usd for c in self.costs if c.required or not required_only)

    def monthly_cost(self, required_only: bool = True) -> float:
        return sum(c.monthly_usd for c in self.costs if c.required or not required_only)

    def phase(self, index: int) -> Phase:
        return self.phases[min(index, len(self.phases) - 1)]

    def brief(self) -> str:
        """Stable, cacheable description of the experiment for the system prompt."""

        def bullets(items: tuple[str, ...]) -> str:
            return "\n".join(f"- {i}" for i in items)

        phases = "\n".join(
            f"{n}. {p.name} (~{p.days} days, {p.cadence}) - goal: {p.goal}\n" + "\n".join(f"   - {t}" for t in p.tasks)
            for n, p in enumerate(self.phases)
        )
        costs = "\n".join(
            f"- {c.item}: ${c.one_time_usd:,.0f} one-time, ${c.monthly_usd:,.0f}/mo"
            + (f", {c.variable}" if c.variable else "")
            + ("" if c.required else " (optional)")
            for c in self.costs
        )
        gates = "\n".join(f"- {g.describe()}" for g in self.gates)
        marketing = "(not defined)"
        if self.marketing:
            m = self.marketing
            paid = (
                "\n".join(f"- {c.item}: ${c.monthly_usd:,.0f}/mo" + (f" - {c.note}" if c.note else "") for c in m.paid)
                or "- none"
            )
            marketing = f"""Positioning: {m.positioning}

Channels (priority order):
{bullets(m.channels)}

SEO plan:
{bullets(m.seo)}

Paid tests (optional; each needs a `spend` request):
{paid}

Funding verdict: {m.funding}"""
        return f"""# Experiment {self.rank}: {self.name} (`{self.id}`)
{self.one_liner}

## Thesis
{self.thesis}

## Customer
{self.customer}

## Offer and pricing
{self.offer}
Pricing: {self.pricing}

## Evidence behind the bet
{bullets(self.evidence)}

## Known risks
{bullets(self.risks)}

## Compliance rules (non-negotiable)
{bullets(self.compliance)}

## What you (the agent) own
{bullets(self.agent_does)}

## What the human operator owns
{bullets(self.human_does)}

## Phase plan
{phases}

## Kill / continue gates
{gates}

## KPIs to track
{bullets(self.kpis)}

## Marketing and distribution
{marketing}

## External costs (each must go through a `spend` request)
{costs}
"""
