from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import pytest

from venture_lab.cli import main
from venture_lab.experiments import get
from venture_lab.ledger import Ledger
from venture_lab.portfolio import tick
from venture_lab.subscription import AGENT_ENV, claude_command, run_with_claude_code


def fake_claude(result: dict, returncode: int = 0):
    calls = []

    def runner(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        return SimpleNamespace(returncode=returncode, stdout=json.dumps(result), stderr="")

    runner.calls = calls
    return runner


def test_claude_command_restricts_tools(settings):
    cmd = claude_command(settings, "SYSTEM", "PROMPT")
    assert cmd[:3] == ["claude", "-p", "PROMPT"]
    tools = cmd[cmd.index("--allowedTools") + 1].split(",")
    assert "Bash(venture-lab agent *)" in tools and "Bash" not in tools
    assert cmd[cmd.index("--permission-mode") + 1] == "dontAsk"
    assert cmd[cmd.index("--output-format") + 1] == "json"


def test_session_runs_on_subscription_without_api_keys(settings, ledger, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-not-leak")
    runner = fake_claude({"result": "DONE: research/verticals.md", "is_error": False, "num_turns": 12})
    run = run_with_claude_code(get("voice-receptionist"), settings, ledger, runner=runner)

    assert run["status"] == "ok" and run["summary"].startswith("DONE: research/verticals.md")
    assert run["cost_usd"] == 0
    call = runner.calls[0]
    assert "ANTHROPIC_API_KEY" not in call["env"] and call["env"][AGENT_ENV] == "1"
    assert call["cwd"].name == "voice-receptionist"
    system = call["cmd"][call["cmd"].index("--append-system-prompt") + 1]
    assert "venture-lab agent request voice-receptionist" in system and "voice-spec" in system


def test_session_errors_are_recorded(settings, ledger):
    run = run_with_claude_code(
        get("ai-ops-audit"), settings, ledger, runner=fake_claude({"is_error": True, "result": "limit"}, 1)
    )
    assert run["status"] == "error"

    def timeout(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 1)

    assert run_with_claude_code(get("ai-ops-audit"), settings, ledger, runner=timeout)["status"] == "error"


def test_tick_caps_sessions_per_run(settings, ledger, monkeypatch):
    settings.backend = "claude-code"
    settings.subscription.max_sessions_per_tick = 2
    for exp_id in ("voice-receptionist", "speed-to-lead", "ai-ops-audit"):
        ledger.set_state(exp_id, status="active")
    ran = []
    monkeypatch.setattr(
        "venture_lab.subscription.run_with_claude_code",
        lambda exp, s, led, **kw: ran.append(exp.id) or {"status": "ok", "cost_usd": 0.0},
    )
    tick(settings, ledger)
    assert ran == ["voice-receptionist", "speed-to-lead"]


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    monkeypatch.setenv("VENTURES_HOME", str(tmp_path))
    monkeypatch.setenv("VENTURES_CONFIG", str(tmp_path / "none.toml"))
    return tmp_path


def test_agent_cli_records_as_agent_and_humans_only_commands_are_blocked(cli_env, monkeypatch, capsys):
    main(["agent", "begin", "ai-ops-audit"])
    out = capsys.readouterr().out
    assert out.startswith("RUN ID: 1") and "venture-lab agent learn ai-ops-audit" in out

    monkeypatch.setenv(AGENT_ENV, "1")
    main(["agent", "metric", "ai-ops-audit", "audits_sold", "3"])
    main(["agent", "request", "ai-ops-audit", "--kind", "outreach", "--title", "Email", "--details-json", "{}"])
    main(["agent", "finish", "1", "--summary", "DONE: x"])
    with pytest.raises(SystemExit):
        main(["metric", "ai-ops-audit", "audits_sold", "3"])
    with pytest.raises(SystemExit):
        main(["approve", "1"])

    led = Ledger(cli_env / "ledger.sqlite3")
    assert led.latest_metrics("ai-ops-audit")["audits_sold"]["source"] == "agent"
    assert led.approvals("ai-ops-audit", "pending")[0]["kind"] == "outreach"
    assert led.run(1)["status"] == "ok"
    led.close()
