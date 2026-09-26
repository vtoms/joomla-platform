"""Portfolio manager: evaluates kill gates, auto-pauses failing experiments,
schedules due agent sessions, and writes the portfolio report."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import anthropic

from venture_lab.agent import age_days, run_experiment
from venture_lab.config import Settings, usage_cost_usd
from venture_lab.experiments import EXPERIMENTS, Experiment
from venture_lab.ledger import Ledger
from venture_lab.policy import BudgetExceeded, Policy

CADENCE_MIN_HOURS = {"daily": 20, "weekdays": 20, "weekly": 156}


def status_of(experiment: Experiment, settings: Settings, ledger: Ledger) -> str:
    state = ledger.get_state(experiment.id)
    if state:
        return state["status"]
    return settings.for_experiment(experiment.id).status or "proposed"


def evaluate(experiment: Experiment, ledger: Ledger) -> dict[str, Any]:
    state = ledger.get_state(experiment.id)
    metrics = ledger.latest_metrics(experiment.id)
    days = age_days(state)
    results = [(g, g.evaluate(metrics, days)) for g in experiment.gates]
    return {
        "age_days": days,
        "gates": results,
        "hard_failures": [g for g, r in results if r == "fail" and g.hard],
        "soft_failures": [g for g, r in results if r == "fail" and not g.hard],
    }


def is_due(experiment: Experiment, ledger: Ledger, now: datetime | None = None) -> bool:
    now = now or datetime.now(UTC)
    state = ledger.get_state(experiment.id) or {"phase_index": 0}
    cadence = experiment.phase(int(state["phase_index"])).cadence
    if cadence == "weekdays" and now.weekday() >= 5:
        return False
    last = ledger.last_run_at(experiment.id)
    if last is None:
        return True
    hours = (now - datetime.fromisoformat(last)).total_seconds() / 3600
    return hours >= CADENCE_MIN_HOURS[cadence]


def review(settings: Settings, ledger: Ledger, auto_pause: bool = True) -> list[dict[str, Any]]:
    """Evaluate gates for every experiment; pause active ones that fail a hard gate."""
    rows = []
    for exp in EXPERIMENTS:
        status = status_of(exp, settings, ledger)
        ev = evaluate(exp, ledger)
        overridden = (ledger.get_state(exp.id) or {}).get("note", "").startswith("override")
        if auto_pause and status == "active" and ev["hard_failures"] and not overridden:
            reasons = "; ".join(g.describe() for g in ev["hard_failures"])
            ledger.set_state(exp.id, status="paused", note=f"auto-paused: failed {reasons}")
            ledger.add_learning(exp.id, f"Auto-paused by portfolio manager after failing: {reasons}")
            status = "paused"
        rows.append({"experiment": exp, "status": status, **ev})
    return rows


def tick(
    settings: Settings,
    ledger: Ledger,
    *,
    client: anthropic.Anthropic | None = None,
    dry_run: bool = False,
) -> list[str]:
    """One scheduler heartbeat: review gates, then run every due active experiment."""
    log = []
    for row in review(settings, ledger, auto_pause=not dry_run):
        exp = row["experiment"]
        if row["status"] != "active":
            continue
        if not is_due(exp, ledger):
            log.append(f"{exp.id}: not due")
            continue
        if dry_run:
            log.append(f"{exp.id}: would run")
            continue
        try:
            run = run_experiment(exp, settings, ledger, client=client)
            log.append(f"{exp.id}: {run['status']} (${run['cost_usd']:.2f})")
        except BudgetExceeded as exc:
            log.append(f"{exp.id}: skipped - {exc}")
        except anthropic.APIError as exc:
            log.append(f"{exp.id}: error - {exc}")
    return log


def report_markdown(settings: Settings, ledger: Ledger) -> str:
    lines = [
        f"# Portfolio report - {datetime.now(UTC):%Y-%m-%d}",
        "",
        f"API spend this month: ${ledger.spend_this_month():.2f} of ${settings.global_api_budget_usd_month:.2f} cap",
    ]
    one_time, monthly = ledger.committed_external_spend()
    lines += [f"Approved external spend: ${one_time:,.2f} one-time, ${monthly:,.2f}/mo", ""]
    lines += ["| # | Experiment | Status | Day | Phase | API $ (mo) | Gates |", "|---|---|---|---|---|---|---|"]
    for row in review(settings, ledger, auto_pause=False):
        exp = row["experiment"]
        state = ledger.get_state(exp.id) or {"phase_index": 0}
        gates = ", ".join(f"{g.metric}:{r}" for g, r in row["gates"])
        lines.append(
            f"| {exp.rank} | {exp.name} | {row['status']} | {row['age_days']:.0f} | "
            f"{int(state['phase_index']) + 1}/{len(exp.phases)} | ${ledger.spend_this_month(exp.id):.2f} | {gates} |"
        )
    pending = ledger.approvals(status="pending")
    lines += ["", f"## Pending approvals ({len(pending)})"]
    lines += [
        f"- #{a['id']} [{a['experiment']}] {a['kind']}: {a['title']}"
        + (f" (${a['one_time_usd']:,.0f} + ${a['monthly_usd']:,.0f}/mo)" if a["kind"] == "spend" else "")
        for a in pending
    ] or ["- none"]
    lines += ["", "## Latest verified metrics"]
    for exp in EXPERIMENTS:
        metrics = {k: v for k, v in ledger.latest_metrics(exp.id).items() if v["source"] != "agent"}
        if metrics:
            lines.append(f"- **{exp.id}**: " + ", ".join(f"{k}={v['value']:g}" for k, v in metrics.items()))
    return "\n".join(lines) + "\n"


MEMO_PROMPT = """You are the portfolio manager for a set of AI monetization experiments.
Below is this week's portfolio report. Write a one-page memo for the owner:
1. Which experiments to double down on, hold, or kill, with the evidence.
2. How to reallocate the API budget and any approved spend.
3. The 3 decisions the owner must make this week (link approval ids).
Judge only on verified metrics; call out where data is missing. Be blunt and brief."""


def portfolio_memo(settings: Settings, ledger: Ledger, client: anthropic.Anthropic | None = None) -> str:
    Policy(settings, ledger).check_budget("portfolio", settings.global_api_budget_usd_month)
    client = client or anthropic.Anthropic()
    model = settings.models.strategist
    run_id = ledger.start_run("portfolio", "portfolio", model)
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=MEMO_PROMPT,
        messages=[{"role": "user", "content": report_markdown(settings, ledger)}],
    )
    ledger.add_usage(run_id, response.usage, usage_cost_usd(response.model, response.usage))
    memo = "\n".join(b.text for b in response.content if b.type == "text")
    ledger.finish_run(run_id, "refused" if response.stop_reason == "refusal" else "ok", memo)
    return memo
