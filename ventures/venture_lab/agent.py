"""Runs one experiment agent session with the SDK tool runner."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import anthropic
from anthropic import beta_tool

from venture_lab.config import (
    ADAPTIVE_THINKING_MODELS,
    SERVER_FALLBACK_BETA,
    SERVER_FALLBACK_MODELS,
    Settings,
    usage_cost_usd,
)
from venture_lab.experiments.base import Experiment
from venture_lab.ledger import Ledger
from venture_lab.policy import BudgetExceeded, Policy
from venture_lab.specialized import extra_tools
from venture_lab.tools import Workspace, build_tools

OPERATING_PRINCIPLES = """You are an autonomous operator running one business experiment inside a
portfolio of AI monetization experiments. You work in scheduled sessions; each
session you pick the highest-leverage next steps in the current phase, do them
with your tools, and leave the workspace and ledger in a state the next session
(or a human) can pick up cold.

How you work:
- Produce real work products, not plans about plans. Save them with save_artifact
  (research notes, offer pages, email drafts, configs, scripts, reports).
- Use web search to ground market, competitor, pricing and policy claims. Cite
  URLs in the artifacts. If you cannot verify something, say so.
- You cannot pay, sign up, send, post or deploy by yourself. Use request_action
  with complete, ready-to-execute details. Money, accounts and legal commitments
  always wait for a human; check list_actions for decisions and follow the
  human's notes on rejected items.
- Record only metrics you measured. Never invent customers, revenue, replies,
  testimonials, reviews, case studies or statistics.
- Distribution is the moat: once something sellable exists, spend at least a
  third of each session on the experiment's marketing plan (outreach drafts,
  SEO pages, content). Paid marketing is a `spend` request, allowed only after an
  organic channel has shown a measured conversion rate.
- Log durable lessons with log_learning so later sessions don't repeat work.
- Stay inside the experiment's API budget: be decisive, batch related work,
  avoid redundant searches.

Hard rules:
- No spam: outreach goes only to businesses with a plausible need, is
  personalised, identifies the sender truthfully, includes an opt-out, and
  complies with CAN-SPAM / CASL / GDPR / PECR as applicable.
- No outbound AI phone calls or texts to people who have not given prior
  express consent (TCPA). Inbound-only for voice agents unless the human says
  consent is documented.
- Disclose AI use where platforms or law require it (voice agents must identify
  as AI when asked or where required; KDP AI-generated disclosure; YouTube
  altered/synthetic content labels).
- No impersonation of real people or brands, no fake reviews, no guaranteed
  income or results claims, no medical/legal/financial advice to end users.
- Respect platform terms: no scraping behind logins, no automation that a
  platform forbids, no engagement manipulation.

End every session with a short status report in this exact shape:
DONE: <what you produced this session, with artifact paths>
WAITING ON HUMAN: <action ids and what they unblock, or "nothing">
METRICS: <metrics you recorded>
NEXT: <the 1-3 highest-value next steps>
PHASE: <stay | ready to advance, with reason>"""


def _format_rows(rows: list[dict[str, Any]], fmt: str, empty: str = "(none)") -> str:
    return "\n".join(fmt.format(**r) for r in rows) if rows else empty


def age_days(state: dict[str, Any] | None) -> float:
    if not state or not state.get("started_at"):
        return 0.0
    started = datetime.fromisoformat(state["started_at"])
    return (datetime.now(UTC) - started).total_seconds() / 86400


def build_system(experiment: Experiment) -> list[dict[str, Any]]:
    # Stable content only, so the prefix caches across sessions of this experiment.
    return [
        {"type": "text", "text": OPERATING_PRINCIPLES},
        {"type": "text", "text": experiment.brief(), "cache_control": {"type": "ephemeral"}},
    ]


def build_session_prompt(experiment: Experiment, ledger: Ledger, workspace: Workspace, task: str | None) -> str:
    state = ledger.get_state(experiment.id) or {"phase_index": 0, "started_at": None}
    phase_index = int(state["phase_index"])
    phase = experiment.phase(phase_index)
    metrics = ledger.latest_metrics(experiment.id)
    days = age_days(state)
    gates = "\n".join(f"- {g.describe()}: {g.evaluate(metrics, days)}" for g in experiment.gates)
    decided = [a for a in ledger.approvals(experiment.id) if a["status"] != "pending"][-15:]
    pending = ledger.approvals(experiment.id, "pending")
    runs = ledger.recent_runs(experiment.id, limit=3)
    artifacts = workspace.list()
    metrics_text = _format_rows(list(metrics.values()), "- {name} = {value:g} [{source}] {note}")
    pending_text = _format_rows(pending, "- #{id} {kind}: {title}")
    decided_text = _format_rows(decided, "- #{id} [{status}] {kind}: {title} {decision_note}")
    learnings_text = _format_rows(ledger.learnings(experiment.id), "- {text}")
    runs_text = _format_rows(runs, "--- {started_at} ({status})\n{summary}")
    files_text = "\n".join(artifacts[-60:]) if artifacts else "(empty)"
    task_text = task or "Advance the current phase: pick the highest-leverage unfinished tasks and complete them."

    return f"""Session date: {datetime.now(UTC):%Y-%m-%d} (day {days:.0f} of the experiment)
Current phase: {phase_index + 1}/{len(experiment.phases)} - {phase.name}
Phase goal: {phase.goal}

## Metrics (latest)
{metrics_text}

## Gates
{gates}

## Pending human approvals
{pending_text}

## Recent decisions
{decided_text}

## Lessons from earlier sessions
{learnings_text}

## Last session reports
{runs_text}

## Workspace files
{files_text}

## Your task this session
{task_text}"""


def _phase_tool(experiment: Experiment, ledger: Ledger) -> Any:
    @beta_tool
    def advance_phase(reason: str) -> str:
        """Move this experiment to its next phase once the current phase's goal is met.

        Args:
            reason: Evidence that the phase goal is met (artifacts, metrics, approvals).
        """
        state = ledger.get_state(experiment.id) or {"phase_index": 0}
        nxt = int(state["phase_index"]) + 1
        if nxt >= len(experiment.phases):
            return "Already in the final phase."
        ledger.set_state(experiment.id, phase_index=nxt)
        ledger.add_learning(experiment.id, f"Advanced to phase {nxt + 1} ({experiment.phases[nxt].name}): {reason}")
        return f"Advanced to phase {nxt + 1}: {experiment.phases[nxt].name}."

    return advance_phase


# Models documented to support the dynamic-filtering web tool versions.
DYNAMIC_WEB_TOOL_MODELS = {"claude-opus-5", "claude-sonnet-5", "claude-sonnet-4-6"}


def server_tools(model: str, max_uses: int) -> list[dict[str, Any]]:
    if model in DYNAMIC_WEB_TOOL_MODELS:
        search, fetch = "web_search_20260209", "web_fetch_20260209"
    else:
        search, fetch = "web_search_20250305", "web_fetch_20250910"
    return [
        {"type": search, "name": "web_search", "max_uses": max_uses},
        {"type": fetch, "name": "web_fetch", "max_uses": max_uses},
    ]


def request_params(experiment: Experiment, settings: Settings) -> dict[str, Any]:
    override = settings.for_experiment(experiment.id)
    model = settings.models.resolve(override.model or experiment.model)
    params: dict[str, Any] = {
        "model": model,
        "max_tokens": 16000,
        "max_iterations": settings.max_iterations_per_run,
        "system": build_system(experiment),
    }
    if model in ADAPTIVE_THINKING_MODELS:
        params["thinking"] = {"type": "adaptive"}
        params["output_config"] = {"effort": override.effort or experiment.effort}
    if model in SERVER_FALLBACK_MODELS:
        # On a safety-classifier refusal the API reruns the turn on a fallback model.
        params["betas"] = [SERVER_FALLBACK_BETA]
        params["fallbacks"] = "default"
    return params


def run_experiment(
    experiment: Experiment,
    settings: Settings,
    ledger: Ledger,
    *,
    task: str | None = None,
    client: anthropic.Anthropic | None = None,
) -> dict[str, Any]:
    """Run one agent session. Returns the run record from the ledger."""
    policy = Policy(settings, ledger)
    policy.check_budget(experiment.id, experiment.api_budget_usd_month)
    if ledger.get_state(experiment.id) is None:
        ledger.set_state(experiment.id, status="active")

    client = client or anthropic.Anthropic()
    workspace = Workspace(settings.artifacts_dir, experiment.id)
    params = request_params(experiment, settings)
    tools: list[Any] = [
        *build_tools(experiment.id, ledger, policy, workspace),
        _phase_tool(experiment, ledger),
        *extra_tools(
            experiment.extra_tools,
            experiment.id,
            ledger,
            workspace,
            client,
            settings,
            policy.api_budget(experiment.id, experiment.api_budget_usd_month),
        ),
        *server_tools(params["model"], settings.web_search_max_uses),
    ]
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": build_session_prompt(experiment, ledger, workspace, task)}
    ]

    run_id = ledger.start_run(experiment.id, "agent", params["model"])
    status, summary, last = "ok", "", None
    try:
        for _restart in range(5):
            runner = client.beta.messages.tool_runner(tools=tools, messages=messages, **params)
            for message in runner:
                last = message
                cost = usage_cost_usd(getattr(message, "model", params["model"]), message.usage)
                ledger.add_usage(run_id, message.usage, cost)
                # Mirror history so a pause_turn can be resumed with a fresh runner.
                messages.append({"role": "assistant", "content": message.content})
                tool_response = runner.generate_tool_call_response()
                if tool_response is not None:
                    messages.append(tool_response)
                policy.check_budget(experiment.id, experiment.api_budget_usd_month)
            if last is None or last.stop_reason != "pause_turn":
                break
        if last is not None and last.stop_reason == "refusal":
            status = "refused"
        summary = "\n".join(b.text for b in (last.content if last else []) if getattr(b, "type", "") == "text")
    except BudgetExceeded as exc:
        status, summary = "budget_stop", f"Stopped: {exc}"
    except anthropic.APIError as exc:
        status, summary = "error", f"API error: {exc}"
        ledger.finish_run(run_id, status, summary)
        raise
    ledger.finish_run(run_id, status, summary.strip())
    return ledger.run(run_id)


def dry_run_payload(experiment: Experiment, settings: Settings, ledger: Ledger, task: str | None = None) -> str:
    """The request an agent session would send, without calling the API."""
    policy = Policy(settings, ledger)
    workspace = Workspace(settings.artifacts_dir, experiment.id)
    params = request_params(experiment, settings)
    budget = policy.api_budget(experiment.id, experiment.api_budget_usd_month)
    tools = [
        *build_tools(experiment.id, ledger, policy, workspace),
        _phase_tool(experiment, ledger),
        *extra_tools(experiment.extra_tools, experiment.id, ledger, workspace, None, settings, budget),
    ]
    tool_names = [t.name for t in tools] + [t["name"] for t in server_tools(params["model"], 0)]
    return json.dumps(
        {
            **{k: v for k, v in params.items() if k != "system"},
            "tools": tool_names,
            "system_chars": sum(len(b["text"]) for b in params["system"]),
            "user_prompt": build_session_prompt(experiment, ledger, workspace, task),
        },
        indent=2,
    )
