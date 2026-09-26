"""Command-line interface: `python -m venture_lab <command>` (or `venture-lab`)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime

from venture_lab.agent import dry_run_payload, run_experiment
from venture_lab.config import load_settings
from venture_lab.experiments import EXPERIMENTS, get
from venture_lab.experiments.catalog import FOUNDATION, foundation_monthly, foundation_setup
from venture_lab.ledger import Ledger
from venture_lab.policy import BudgetExceeded, Policy
from venture_lab.portfolio import portfolio_memo, report_markdown, status_of, tick


def cmd_list(args, settings, ledger) -> None:
    print(f"{'#':>2}  {'id':<22} {'status':<9} {'setup $':>8} {'$/mo':>7} {'mkt $/mo*':>9}  name")
    for e in EXPERIMENTS:
        print(
            f"{e.rank:>2}  {e.id:<22} {status_of(e, settings, ledger):<9} {e.setup_cost():>8.2f} "
            f"{e.monthly_cost():>7.2f} {e.marketing.paid_monthly():>9.0f}  {e.name}"
        )
    print("\n* optional paid-marketing tests, unlocked only after organic proof")


def cmd_costs(args, settings, ledger) -> None:
    print("Foundation (shared, bought once):")
    for c in FOUNDATION:
        tag = "" if c.required else " (optional)"
        print(f"  - {c.item}: ${c.one_time_usd:,.2f} + ${c.monthly_usd:,.2f}/mo{tag} {c.variable}".rstrip())
    print(f"  = required ${foundation_setup():,.2f} upfront + ${foundation_monthly():,.2f}/mo\n")
    total_setup, total_monthly, total_mkt = foundation_setup(), foundation_monthly(), 0.0
    for e in EXPERIMENTS:
        print(
            f"{e.rank}. {e.name}: ${e.setup_cost():,.2f} setup + ${e.monthly_cost():,.2f}/mo required; "
            f"API cap ${e.api_budget_usd_month:,.0f}/mo; optional marketing ${e.marketing.paid_monthly():,.0f}/mo"
        )
        total_setup += e.setup_cost()
        total_monthly += e.monthly_cost()
        total_mkt += e.marketing.paid_monthly()
    print(
        f"\nAll 10 running: ${total_setup:,.2f} upfront + ${total_monthly:,.2f}/mo tools "
        f"+ API cap ${settings.global_api_budget_usd_month:,.0f}/mo; optional marketing up to ${total_mkt:,.0f}/mo"
    )


def cmd_show(args, settings, ledger) -> None:
    print(get(args.experiment).brief())


def cmd_set_status(args, settings, ledger) -> None:
    status = {"activate": "active", "pause": "paused", "kill": "killed", "scale": "scaling"}[args.command]
    note = getattr(args, "override", None)
    for exp_id in args.experiments:
        get(exp_id)
        state = ledger.set_state(exp_id, status=status, note=f"override: {note}" if note else "")
        print(f"{exp_id}: {state['status']}")


def cmd_set_phase(args, settings, ledger) -> None:
    exp = get(args.experiment)
    if not 1 <= args.phase <= len(exp.phases):
        sys.exit(f"phase must be 1-{len(exp.phases)}")
    ledger.set_state(exp.id, phase_index=args.phase - 1)
    print(f"{exp.id}: phase {args.phase} ({exp.phases[args.phase - 1].name})")


def cmd_run(args, settings, ledger) -> None:
    exp = get(args.experiment)
    if args.dry_run:
        print(dry_run_payload(exp, settings, ledger, args.task))
        return
    try:
        run = run_experiment(exp, settings, ledger, task=args.task)
    except BudgetExceeded as exc:
        sys.exit(str(exc))
    print(
        f"[{run['status']}] ${run['cost_usd']:.4f}, {run['input_tokens']} in / {run['output_tokens']} out, "
        f"{run['cache_read_tokens']} cached\n\n{run['summary']}"
    )


def cmd_tick(args, settings, ledger) -> None:
    for line in tick(settings, ledger, dry_run=args.dry_run):
        print(line)


def cmd_approvals(args, settings, ledger) -> None:
    rows = ledger.approvals(args.experiment, args.status)
    for a in rows:
        cost = f" ${a['one_time_usd']:,.2f} + ${a['monthly_usd']:,.2f}/mo" if a["kind"] == "spend" else ""
        print(f"#{a['id']} [{a['status']}] {a['experiment']} {a['kind']}{cost}: {a['title']}")
        if args.verbose:
            print("   " + json.dumps(json.loads(a["details"]), indent=2).replace("\n", "\n   "))
    if not rows:
        print("(none)")


def cmd_decide(args, settings, ledger) -> None:
    status = {"approve": "approved", "reject": "rejected", "done": "executed"}[args.command]
    action = ledger.decide(args.id, status, args.note or "")
    print(f"#{action['id']} -> {action['status']}")
    if status == "approved" and settings.webhook_url:
        sent = Policy(settings, ledger).dispatch(args.id)
        print("dispatched to executor webhook" if sent else "webhook dispatch failed; execute manually")


def cmd_metric(args, settings, ledger) -> None:
    get(args.experiment)
    ledger.record_metric(args.experiment, args.name, args.value, source=args.source, note=args.note or "")
    print(f"{args.experiment}: {args.name}={args.value:g} [{args.source}]")


def cmd_report(args, settings, ledger) -> None:
    text = report_markdown(settings, ledger)
    if args.memo:
        text += "\n## Portfolio manager memo\n\n" + portfolio_memo(settings, ledger) + "\n"
    out = settings.artifacts_dir / "portfolio" / f"report-{datetime.now(UTC):%Y-%m-%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"(saved to {out})")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="venture-lab", description=__doc__)
    p.add_argument("--config", help="path to venture_lab.toml")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list experiments with costs and status").set_defaults(fn=cmd_list)
    sub.add_parser("costs", help="investment summary").set_defaults(fn=cmd_costs)
    s = sub.add_parser("show", help="print an experiment brief")
    s.add_argument("experiment")
    s.set_defaults(fn=cmd_show)

    for name, help_text in [
        ("activate", "start experiments"),
        ("pause", "pause"),
        ("kill", "kill"),
        ("scale", "mark as scaling"),
    ]:
        s = sub.add_parser(name, help=help_text)
        s.add_argument("experiments", nargs="+")
        if name == "activate":
            s.add_argument("--override", help="reason to keep running despite a failed gate")
        s.set_defaults(fn=cmd_set_status)

    s = sub.add_parser("set-phase", help="move an experiment to phase N (1-based)")
    s.add_argument("experiment")
    s.add_argument("phase", type=int)
    s.set_defaults(fn=cmd_set_phase)

    s = sub.add_parser("run", help="run one agent session now")
    s.add_argument("experiment")
    s.add_argument("--task", help="override this session's task")
    s.add_argument("--dry-run", action="store_true", help="print the request without calling the API")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("tick", help="scheduler heartbeat: gates, auto-pause, run due experiments")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_tick)

    s = sub.add_parser("approvals", help="list requested actions")
    s.add_argument("--experiment")
    s.add_argument("--status", choices=["pending", "approved", "rejected", "executed"])
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_approvals)

    for name in ("approve", "reject", "done"):
        s = sub.add_parser(name, help=f"{name} an action by id")
        s.add_argument("id", type=int)
        s.add_argument("--note", help="decision note the agent will read (required context for rejections)")
        s.set_defaults(fn=cmd_decide)

    s = sub.add_parser("metric", help="record a verified metric (revenue, clients, replies...)")
    s.add_argument("experiment")
    s.add_argument("name")
    s.add_argument("value", type=float)
    s.add_argument("--source", default="human", choices=["human", "integration"])
    s.add_argument("--note")
    s.set_defaults(fn=cmd_metric)

    s = sub.add_parser("report", help="write the portfolio report")
    s.add_argument("--memo", action="store_true", help="add an AI portfolio-manager memo (uses the API)")
    s.set_defaults(fn=cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(args.config)
    ledger = Ledger(settings.db_path)
    try:
        args.fn(args, settings, ledger)
    finally:
        ledger.close()
    return 0
