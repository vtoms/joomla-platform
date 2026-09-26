"""Subscription backend: agent sessions run by Claude Code on a Pro/Max plan
instead of pay-as-you-go API credits.

Two ways to use it:
- Local cron: `venture-lab tick` with `backend = "claude-code"` shells out to
  `claude -p` once per due experiment, with tools restricted to web research,
  file edits inside the experiment's workspace, and `venture-lab agent ...`.
- Cloud routine: a scheduled Claude Code session runs `venture-lab due`, then
  `venture-lab agent begin <id>` and does the work itself (see deploy/cloud-routine.md).
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from venture_lab.agent import OPERATING_PRINCIPLES, build_session_prompt
from venture_lab.config import Settings
from venture_lab.experiments.base import Experiment
from venture_lab.ledger import Ledger
from venture_lab.policy import ACTION_KINDS
from venture_lab.tools import Workspace

AGENT_ENV = "VENTURES_AGENT_SESSION"


def protocol(experiment: Experiment, settings: Settings, workspace: Workspace) -> str:
    cli = f"{settings.subscription.cli} agent"
    e = experiment.id
    kinds = ", ".join(ACTION_KINDS)
    extra = ""
    if "voice_agent_spec" in experiment.extra_tools:
        extra += f"\n- build_voice_agent_spec -> `{cli} voice-spec {e} --profile-json '<json>'`"
    if "unit_economics" in experiment.extra_tools:
        extra += (
            f"\n- calculate_unit_economics -> `{cli} economics --price 497 --clients 3 "
            "--variable-cost 200 --fixed-cost 50 [--setup-fee 750] [--churn-pct 5]`"
        )
    if "batch_extraction" in experiment.extra_tools:
        extra += (
            "\n- submit/collect_extraction_batch are API-only. On the subscription, extract small samples by "
            "reading the documents yourself and writing results to extractions/<job>/results.csv."
        )
    return f"""## How to act in this environment (Claude Code on a subscription)
Wherever these instructions name a tool, use the equivalent here:
- save_artifact / read_artifact / list_artifacts -> your file tools, ONLY inside {workspace.root}
- web_search / web_fetch -> WebSearch / WebFetch
- record_metric -> `{cli} metric {e} <name> <value> --note "<how measured>"`
- log_learning -> `{cli} learn {e} "<lesson>"`
- request_action -> `{cli} request {e} --kind <kind> --title "<one line>" --details-json '<json object>' \
[--one-time <usd>] [--monthly <usd>]` (kinds: {kinds})
- list_actions -> `{cli} actions {e} [--status pending|approved|rejected|executed]`
- advance_phase -> `{cli} advance {e} --reason "<evidence>"`{extra}
Never run other `{settings.subscription.cli}` commands (approve, reject, metric without `agent`, activate...):
those are the human operator's. Never touch files outside the workspace. There is no API budget here;
instead keep each session focused (it runs on the operator's plan usage limits)."""


def session_instructions(
    experiment: Experiment, settings: Settings, ledger: Ledger, task: str | None = None
) -> tuple[str, str]:
    """(system prompt addition, user prompt) for one Claude Code session."""
    workspace = Workspace(settings.artifacts_dir, experiment.id)
    system = "\n\n".join([OPERATING_PRINCIPLES, protocol(experiment, settings, workspace), experiment.brief()])
    return system, build_session_prompt(experiment, ledger, workspace, task)


def allowed_tools(settings: Settings) -> list[str]:
    return [
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "WebSearch",
        "WebFetch",
        f"Bash({settings.subscription.cli} agent *)",
    ]


def claude_command(settings: Settings, system: str, prompt: str) -> list[str]:
    sub = settings.subscription
    cmd = [
        sub.claude_bin,
        "-p",
        prompt,
        "--append-system-prompt",
        system,
        "--allowedTools",
        ",".join(allowed_tools(settings)),
        "--permission-mode",
        sub.permission_mode,
        "--max-turns",
        str(sub.max_turns),
        "--output-format",
        "json",
    ]
    if sub.model:
        cmd += ["--model", settings.models.resolve(sub.model)]
    return cmd


def agent_env(settings: Settings) -> dict[str, str]:
    env = {**os.environ, AGENT_ENV: "1", "VENTURES_HOME": str(settings.home.resolve())}
    if settings.config_path:
        env["VENTURES_CONFIG"] = str(settings.config_path.resolve())
    # These take precedence over the subscription login and would bill the API instead of the plan.
    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(var, None)
    return env


def run_with_claude_code(
    experiment: Experiment,
    settings: Settings,
    ledger: Ledger,
    *,
    task: str | None = None,
    runner: Any = subprocess.run,
) -> dict[str, Any]:
    if ledger.get_state(experiment.id) is None:
        ledger.set_state(experiment.id, status="active")
    workspace = Workspace(settings.artifacts_dir, experiment.id)
    system, prompt = session_instructions(experiment, settings, ledger, task)
    run_id = ledger.start_run(experiment.id, "agent", f"claude-code:{settings.subscription.model or 'default'}")
    try:
        proc = runner(
            claude_command(settings, system, prompt),
            cwd=workspace.root,
            env=agent_env(settings),
            capture_output=True,
            text=True,
            timeout=settings.subscription.timeout_minutes * 60,
        )
    except FileNotFoundError:
        ledger.finish_run(run_id, "error", f"`{settings.subscription.claude_bin}` not found; install Claude Code.")
        return ledger.run(run_id)
    except subprocess.TimeoutExpired:
        ledger.finish_run(run_id, "error", f"Timed out after {settings.subscription.timeout_minutes} minutes.")
        return ledger.run(run_id)

    try:
        result = json.loads(proc.stdout)
    except ValueError:
        result = {"is_error": True, "result": (proc.stdout or proc.stderr or "no output").strip()[-2000:]}
    status = "error" if proc.returncode != 0 or result.get("is_error") else "ok"
    summary = str(result.get("result", "")).strip()
    if "num_turns" in result:
        summary += f"\n\n(claude-code: {result['num_turns']} turns on the subscription)"
    ledger.finish_run(run_id, status, summary)
    return ledger.run(run_id)
