# Venture Lab

Autonomous, budget-capped Claude agents that run a portfolio of ten AI monetization experiments. **Start with [PLAN.md](PLAN.md)**: it covers the ranked experiments, the investment each needs, marketing and SEO plans, and the launch sequence.

Each experiment has an agent that works in scheduled sessions. In each session it:
- Researches, with web search.
- Builds and writes offers, pages, specs, drafts and reports, saved to its workspace.
- Tracks KPIs and advances through its phase plan.
- Asks you before anything outward-facing.

A portfolio manager evaluates kill gates on verified metrics, auto-pauses failures, and writes a weekly memo.

## Two ways to pay for the agents' Claude usage

- **Subscription (default, recommended).** `backend = "claude-code"`: each session runs `claude -p` on your Claude Pro/Max plan. No API key; usage counts against your plan's limits. Run it from cron on your computer, or as a scheduled Claude Code cloud routine ([deploy/cloud-routine.md](deploy/cloud-routine.md)).
- **API credits.** `backend = "api"`: Anthropic SDK tool runner with per-experiment dollar caps, prompt caching and the Batch API (needed for large document-extraction jobs).

## Setup

```bash
cd ventures
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp venture_lab.example.toml venture_lab.toml     # budgets, models, auto-approvals
# Subscription backend: just be logged in to Claude Code (`claude`); no API key.
# API backend only: export ANTHROPIC_API_KEY=sk-ant-...
venture-lab costs                                 # what you'd be paying for
venture-lab activate ai-ops-audit voice-receptionist speed-to-lead ai-ops-newsletter
venture-lab run voice-receptionist --dry-run      # API backend: inspect the request, no API call
venture-lab run voice-receptionist                # one real session
```

Then schedule `venture-lab tick` with [deploy/crontab.example](deploy/crontab.example). A GitHub Actions alternative is in [deploy/github-actions.example.yml](deploy/github-actions.example.yml).

## Daily operation

| You want to | Command |
|---|---|
| See the portfolio | `venture-lab list`, `venture-lab report` (add `--memo` for the AI portfolio-manager memo) |
| Read an experiment's brief | `venture-lab show speed-to-lead` |
| Review what agents want to do | `venture-lab approvals --status pending -v` |
| Decide | `venture-lab approve 12 --note "go"`, `venture-lab reject 13 --note "too salesy; lead with the audit"`, `venture-lab done 12` once you've executed it |
| Report real numbers (these drive the gates) | `venture-lab metric voice-receptionist paying_clients 1` |
| Agent-side commands (used by sessions on the subscription) | `venture-lab agent begin/finish/metric/learn/request/actions/advance/economics/voice-spec` |
| Steer a session | `venture-lab run doc-extraction --task "Label-check the 30 sample leases and report accuracy"` |
| Pause / kill / resume despite a failed gate | `venture-lab pause X`, `venture-lab kill X`, `venture-lab activate X --override "seasonal dip"` |

Artifacts live in `var/artifacts/<experiment>/`. The ledger (runs, spend, metrics, approvals, learnings) is `var/ledger.sqlite3`.

## Safety model

- **Always human-approved.** Agents hold no payment or account credentials. `spend`, `account` and `legal` actions always go to the approval queue, whatever the config says. Any action with a price is reclassified as `spend`.
- **Everything else outward-facing** (outreach, publishing, customer messages, deploys) is queued by default. Add kinds to `approvals.auto_approve` once you trust an experiment. Approved actions can be POSTed to a webhook, for example an n8n workflow that sends from your mailbox.
- **Budgets.** API spend is checked after every model turn against the experiment's cap and the portfolio cap. A session that hits either one stops.
- **Kill gates** count only metrics you or an integration reported. Agent-recorded numbers never keep an experiment alive.
- **Prompt-level rules:** no spam, TCPA-safe voice/SMS (inbound only), AI disclosure, no fake reviews or income claims, respect platform terms.

## Code map

| Path | What it is |
|---|---|
| `venture_lab/experiments/catalog.py` | The 10 experiments: thesis, offer, costs, phases, gates, KPIs |
| `venture_lab/experiments/marketing.py` | Go-to-market, SEO plan and funding verdict per experiment |
| `venture_lab/subscription.py` | Subscription backend: `claude -p` sessions, tool allowlist, agent protocol |
| `reviews/` | Adversarial review of the plan, plus `run_gpt_review.sh` for a second opinion via the Codex CLI |
| `venture_lab/agent.py` | One agent session: SDK tool runner, cached brief, cost accounting, pause-turn handling |
| `venture_lab/tools.py` | Shared tools (artifacts, metrics, learnings, action requests) |
| `venture_lab/specialized/` | Voice receptionist spec builder, unit economics, Batch-API document extraction |
| `venture_lab/policy.py` | Approval rules, webhook executor, budget caps |
| `venture_lab/portfolio.py` | Gates, auto-pause, scheduling, report and memo |
| `venture_lab/ledger.py` | SQLite ledger |
| `tests/` | Offline tests, including the real SDK against a local fake API server |

Run the tests with `pytest` (no API key needed).
