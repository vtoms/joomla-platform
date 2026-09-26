from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest
from conftest import FakeClient, message, text, tool_use, usage

from venture_lab.agent import dry_run_payload, run_experiment
from venture_lab.config import ExperimentSettings, usage_cost_usd
from venture_lab.experiments import EXPERIMENTS, get
from venture_lab.policy import BudgetExceeded, Policy
from venture_lab.portfolio import is_due, review
from venture_lab.specialized import REGISTRY
from venture_lab.specialized.economics import unit_economics
from venture_lab.specialized.voice import build_voice_spec
from venture_lab.tools import Workspace


def test_catalog_is_complete():
    assert [e.rank for e in EXPERIMENTS] == list(range(1, 11))
    assert len({e.id for e in EXPERIMENTS}) == 10
    for e in EXPERIMENTS:
        assert e.marketing and e.marketing.channels and e.marketing.seo and e.marketing.funding
        assert e.phases and e.gates and e.kpis
        assert all(name in REGISTRY for name in e.extra_tools)
        assert all(g.metric in e.kpis for g in e.gates), e.id
        assert "Marketing and distribution" in e.brief()
    assert sum(e.api_budget_usd_month for e in EXPERIMENTS) <= 250


def test_usage_cost():
    u = usage(inp=1_000_000, out=1_000_000, cache_read=1_000_000)
    assert usage_cost_usd("claude-opus-5", u) == pytest.approx(5 + 25 + 0.5)
    assert usage_cost_usd("claude-haiku-4-5", u, batch=True) == pytest.approx((1 + 5 + 0.1) / 2)


def test_money_accounts_and_legal_never_auto_approve(settings, ledger):
    settings.auto_approve = ["spend", "account", "legal", "publish_owned"]
    policy = Policy(settings, ledger)
    assert policy.request_action("x", "spend", "buy", {}, 10).status == "pending"
    assert policy.request_action("x", "account", "signup", {}).status == "pending"
    assert policy.request_action("x", "publish_owned", "post", {}).status == "approved"
    # A priced action is reclassified as spend, so it can't slip through as auto-approved.
    decision = policy.request_action("x", "publish_owned", "boosted post", {}, monthly_usd=50)
    assert decision.status == "pending"
    assert ledger.approval(decision.approval_id)["kind"] == "spend"


def test_budget_caps(settings, ledger):
    policy = Policy(settings, ledger)
    run = ledger.start_run("x", "agent", "claude-opus-5")
    ledger.add_usage(run, usage(), 12.0)
    with pytest.raises(BudgetExceeded):
        policy.check_budget("x", 10)
    settings.experiments["x"] = ExperimentSettings(api_budget_usd_month=20)
    policy.check_budget("x", 10)  # override raises the cap
    settings.global_api_budget_usd_month = 5
    with pytest.raises(BudgetExceeded):
        policy.check_budget("y", 100)


def test_workspace_blocks_path_traversal(tmp_path):
    ws = Workspace(tmp_path, "exp")
    assert ws.resolve("a/b.md").is_relative_to(ws.root)
    with pytest.raises(ValueError):
        ws.resolve("../other/secret.txt")


def test_agent_session_runs_tools_and_books_cost(settings, ledger):
    exp = get("voice-receptionist")
    profile = {
        "business_name": "Demo Heating & Air",
        "vertical": "hvac",
        "state": "CO",
        "timezone": "America/Denver",
        "hours": "Mon-Fri 7am-6pm",
        "services": ["AC repair", "furnace repair"],
        "transfer_number": "+15550100",
    }
    script = [
        message(
            tool_use("save_artifact", path="offer/one-pager.md", content="# Offer"),
            tool_use("build_voice_agent_spec", business_profile_json=json.dumps(profile)),
            tool_use(
                "request_action",
                kind="spend",
                title="Retell credits for demo",
                details_json=json.dumps({"vendor": "Retell", "amount": 20}),
                one_time_usd=20,
            ),
            tool_use("record_metric", name="prospects_researched", value=12),
            stop_reason="tool_use",
        ),
        message(text("DONE: offer\nWAITING ON HUMAN: #1\nMETRICS: -\nNEXT: demo\nPHASE: stay")),
    ]
    client = FakeClient(script)
    run = run_experiment(exp, settings, ledger, client=client)

    assert run["status"] == "ok"
    assert run["summary"].startswith("DONE: offer")
    assert run["cost_usd"] == pytest.approx(2 * usage_cost_usd("claude-opus-5", usage()))
    ws = Workspace(settings.artifacts_dir, exp.id)
    assert "offer/one-pager.md" in ws.list()
    assert "voice/demo-heating-air/spec.json" in ws.list()
    assert ledger.approvals(exp.id, "pending")[0]["kind"] == "spend"
    assert ledger.latest_metrics(exp.id)["prospects_researched"]["source"] == "agent"
    call = client.calls[0]
    assert call["model"] == "claude-opus-5" and call["fallbacks"] == "default"
    assert call["system"][-1]["cache_control"] == {"type": "ephemeral"}


def test_agent_stops_at_budget(settings, ledger):
    exp = get("ai-ops-audit")
    settings.experiments[exp.id] = ExperimentSettings(api_budget_usd_month=0.01)
    script = [message(tool_use("list_artifacts"), stop_reason="tool_use", u=usage(100_000, 10_000))] * 3
    run = run_experiment(exp, settings, ledger, client=FakeClient(script))
    assert run["status"] == "budget_stop"
    with pytest.raises(BudgetExceeded):
        run_experiment(exp, settings, ledger, client=FakeClient(script))


def test_gates_pause_on_unverified_or_missing_metrics(settings, ledger):
    exp = get("ai-ops-audit")
    ledger.set_state(exp.id, status="active")
    started = (datetime.now(UTC) - timedelta(days=22)).isoformat(timespec="seconds")
    ledger.conn.execute("UPDATE experiment_state SET started_at = ? WHERE experiment = ?", (started, exp.id))
    ledger.record_metric(exp.id, "audits_sold", 5, source="agent")  # agent-claimed: doesn't count
    review(settings, ledger)
    assert ledger.get_state(exp.id)["status"] == "paused"

    ledger.set_state(exp.id, status="active")
    ledger.record_metric(exp.id, "audits_sold", 1, source="human")
    review(settings, ledger)
    assert ledger.get_state(exp.id)["status"] == "active"


def test_override_prevents_auto_pause(settings, ledger):
    exp = get("ai-ops-audit")
    ledger.set_state(exp.id, status="active", note="override: holiday season")
    started = (datetime.now(UTC) - timedelta(days=22)).isoformat(timespec="seconds")
    ledger.conn.execute("UPDATE experiment_state SET started_at = ? WHERE experiment = ?", (started, exp.id))
    review(settings, ledger)
    assert ledger.get_state(exp.id)["status"] == "active"


def test_cadence(ledger):
    exp = get("voice-receptionist")
    ledger.set_state(exp.id, status="active", phase_index=2)  # weekdays cadence
    saturday = datetime(2026, 9, 26, 12, tzinfo=UTC)
    assert not is_due(exp, ledger, saturday)
    assert is_due(exp, ledger, saturday + timedelta(days=2))
    ledger.start_run(exp.id, "agent", "m")
    assert not is_due(exp, ledger, datetime.now(UTC) + timedelta(hours=2))


def test_voice_spec_requires_fields_and_discloses_ai():
    with pytest.raises(ValueError, match="transfer_number"):
        build_voice_spec(
            {"business_name": "A", "vertical": "hvac", "state": "TX", "timezone": "x", "hours": "x", "services": ["x"]}
        )
    spec = build_voice_spec(
        {
            "business_name": "A",
            "vertical": "plumbing",
            "state": "TX",
            "timezone": "x",
            "hours": "x",
            "services": ["x"],
            "transfer_number": "1",
        }
    )
    assert "AI assistant" in spec["first_message"] and "recorded" in spec["first_message"]
    assert "burst pipe" in spec["transfer"]["triggers"]


def test_unit_economics_matches_brief_example():
    # Brief: ~$170 cost to serve at $797/mo -> ~79% gross margin (before card fees).
    r = unit_economics(797, 1, 120, 50, payment_fee_pct=0)
    assert r["gross_margin_pct"] == pytest.approx(78.7, abs=0.2)
    assert r["breakeven_clients"] == 1


def test_dry_run_lists_real_tool_names(settings, ledger):
    payload = json.loads(dry_run_payload(get("doc-extraction"), settings, ledger))
    assert "submit_extraction_batch" in payload["tools"] and "web_search" in payload["tools"]
