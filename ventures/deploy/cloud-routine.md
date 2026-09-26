# Running the agents as scheduled Claude Code cloud sessions (subscription)

No API key and no server needed. A Routine starts a fresh Claude Code cloud session on a
schedule. That session *is* the agent for up to 3 due experiments, then commits the ledger and
artifacts back to the branch. Usage comes out of your Claude plan's limits (as of Sep 2026,
`claude -p` and cloud sessions draw from normal plan limits, not API credits).

## Routine prompt (fresh session each firing)

```text
You are the Venture Lab scheduler for github.com/vtoms/joomla-platform.

1. git fetch origin claude/ai-monetization-experiments-lsfwkk && git checkout claude/ai-monetization-experiments-lsfwkk && git pull
2. cd ventures && pip install -q -e . && export VENTURES_CONFIG=$PWD/venture_lab.cloud.toml VENTURES_AGENT_SESSION=1
3. Run `venture-lab due --limit 3`. For each experiment id it prints, in order:
   a. Run `venture-lab agent begin <id>` and read ALL of its output: it is your brief, rules and
      session state. Act as that experiment's agent exactly as it says.
   b. Write files only under ventures/state/artifacts/<id>/. Use only `venture-lab agent ...`
      commands for metrics, learnings, action requests and phase changes. Never run approve,
      reject, metric (without `agent`), activate, pause or kill: those belong to the owner.
   c. Finish with `venture-lab agent finish <run id> --summary "<the DONE/WAITING/METRICS/NEXT/PHASE report>"`.
4. Run `venture-lab report`.
5. git add ventures/state && git commit -m "ventures: scheduled run $(date -u +%F)" && git push origin claude/ai-monetization-experiments-lsfwkk
   (retry the push up to 4 times on network errors).
6. Reply with a short digest: one line per experiment worked, then every pending approval
   (id, experiment, title, cost) the owner needs to decide.
```

Suggested schedule: weekdays once a day (e.g. 07:40 in your time zone). Weekly-cadence
experiments are skipped automatically until they are due.

## Deciding approvals and reporting numbers

Open any Claude Code session on this repo and say, for example:
"In ventures/, approve #4 with note 'go', reject #5 with note 'lead with the audit', record
voice-receptionist discovery_calls_booked 2, then commit and push."
The session runs `venture-lab --config venture_lab.cloud.toml approve 4 --note go` and so on.
Or run the same commands locally after `git pull` and push.

## Guardrails in this mode

- Agent sessions set `VENTURES_AGENT_SESSION=1`, which makes the owner-only commands refuse to
  run. In a cloud session the agent could technically unset it, so this is a guardrail, not a
  security boundary. The git history shows every change a scheduled run made.
- Agents hold no payment, email or social credentials, so approved actions are still executed
  by you (or by a webhook you configure).
- Kill gates only count metrics you record, never ones the agent recorded.
