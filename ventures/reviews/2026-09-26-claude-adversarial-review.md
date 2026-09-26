# Adversarial review of PLAN.md (26 Sep 2026)

An independent Claude reviewer wrote this review with web research. It was asked to attack the plan and find better opportunities.
It is **not** the GPT-6 Astra review that was requested: no ChatGPT/Codex CLI or OpenAI credentials are available in the build environment. Run `reviews/run_gpt_review.sh` to get that one, using the same prompt.

Status key:
- ✅ applied in this commit
- ❓ needs the owner's decision
- ⏸ deferred

## Weaknesses found

| # | Finding | Fix proposed | Status |
|---|---|---|---|
| 1 | Voice receptionist is priced far above the market. Trade-specific AI receptionists list at ~$29–199/mo (Jobber AI Receptionist $99, Numa $49, Trillet $49, Goodcall $66–208, NextPhone $199), some bundled into field-service software. The plan charges $497/mo + $750 setup. | $149–249/mo, no setup fee or a $0 pilot. Compete on integration with the client's field-service software and on correct emergency routing. | ❓ |
| 2 | Wave 1 needs ~12–21 h/wk against a 10–15 h budget, before daily approval review. "Capital efficiency" scores 5 for 9 of 10 experiments, so it tells them apart on nothing, while hours, the real bottleneck, aren't scored. | Score "human hours per $". Run ≤3 experiments at once. Batch approvals into one daily review. | ✅ partly: subscription mode runs ≤3 sessions per scheduled run. Re-scoring ❓ |
| 3 | Experiments 1, 2 and 4 are three retainer services competing for the same sales and onboarding hours. Experiments 1 and 2 pitch overlapping products to the same owners. | Merge 1 + 2 into one offer ladder (text-back as the entry tier, voice as the upsell), in one vertical and one metro. | ❓ |
| 4 | Cold email from the brand domain with no warm-up damages deliverability. The first ~2 weeks go to warm-up, so the day-30 call gates are too early. | Add a secondary domain + mailbox and warm it up in week 1. Move the call gates later. | ✅ secondary domain/mailbox added to the foundation ($10.44 + $8.40/mo); discovery-call gates moved from day 30 to day 45; cold email from the brand domain forbidden in the agents' compliance rules |
| 5 | The AI cost model assumed API credits, but the owner has a Claude subscription. Opus-heavy daily sessions could hit caps. | Run on the subscription; use Opus only where it matters. | ✅ `backend = "claude-code"` added. Verified: `claude -p` draws from normal plan limits; Anthropic's planned separate SDK credit is paused (Help Center, Sep 2026). |
| 6 | Support deflection competes with free Shopify Inbox/Sidekick AI replies and per-resolution tools (~$0.99/resolution). Order lookups need Shopify protected-customer-data approval. | Cut #4. | ❓ |
| 7 | The content audience (AI enthusiasts) isn't the buyer (trade owners). The flywheel assumes they are the same people. KDP is saturated, with a $100/mo target. | Replace newsletter/YouTube/KDP with founder-led LinkedIn. Start SEO tools only after first revenue. | ❓ |
| 8 | Liability is underweighted. A wrong AI emergency triage is E&O exposure, and insurers may exclude AI. Recording calls to prospects can breach all-party-consent laws. Insurance is effectively required. Document work needs data-processing agreements (DPAs). | Get an insurance quote in week 1. Hard-code "always transfer on emergency keywords". Drop call recording from the missed-call audit. | ✅ recording removed (written note instead) and banned in the compliance rules; insurance described as required before the first service client; always-transfer on emergency keywords already hard-coded in the voice spec |

## Better opportunities proposed

| Idea | Offer / buyer / price | First $ | Start cost | Would replace |
|---|---|---|---|---|
| A. Joomla 3/4 → Joomla 6 migration & security rescue | Joomla 4 security support ended Oct 2025; Joomla 5 bug fixes end 13 Oct 2026. Nonprofits, schools and small businesses on unsupported versions; many sites expose their version, so lead lists are easy. $900–3,000 fixed + $79–149/mo maintenance. Claude Code is strong at porting extensions and templates. | 2–4 wks | ~$0 | #4 support deflection (only if the owner can do PHP / Joomla) |
| B. AI automation gigs on Upwork/Contra | Existing demand, no domain warm-up. n8n/Make/Claude integration jobs, $500–3,000 per project. Agents screen postings and draft proposals; the human submits them. | 1–3 wks | <$20 Connects | #9 YouTube |
| C. White-label AI fulfilment for local marketing agencies | One agency deal reaches many end clients. $300–1,500 per build + $50–100 per client per month. | 3–5 wks | $0 | #2 as a standalone offer |
| D. Accessibility (WCAG 2.1 AA) fix-and-monitor | The European Accessibility Act is enforceable and US ADA demand letters continue. ~$600 audit + fixes, then $99–149/mo monitoring. Never promise legal compliance; no overlays; EAA exempts microenterprises. | 3–6 wks | $0 | #10 KDP |

## Reviewer's verdict

- **Run first (≤3–4 at once):**
  1. #3 audit, sold to the warm network with LinkedIn as the only content channel.
  2. A merged #1 + #2 missed-call-to-voice ladder at market pricing, from a warmed domain.
  3. #5 document extraction (highest agent leverage, fewest human hours).
  4. Joomla migration (A) if the owner's skills fit, otherwise Upwork gigs (B).
- **Cut:** #4 support deflection, #9 YouTube, #10 KDP.
- **Defer until first revenue:** #6 SEO tools, #7 templates, #8 newsletter.

## Sources cited by the reviewer

- https://lunacal.ai/blogs/ai-receptionist-for-plumbers
- https://pipelineon.com/blog/ai-receptionist-contractor/
- https://www.getnextphone.com/blog/best-virtual-receptionist-for-hvac
- https://trillet.ai/blogs/best-ai-answering-service-for-trades-2026
- https://www.shopify.com/blog/ai-chatbot-customer-service
- https://fin.ai/learn/best-ai-agents-shopify
- https://www.unifygtm.com/explore/cold-email-2026-domain-setup-deliverability-sequences
- https://outboundsystem.com/blog/google-workspace-cold-email-limits
- https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan (checked directly: the change is paused)
- https://endoflife.date/joomla
- https://www.levelaccess.com/compliance-overview/european-accessibility-act-eaa/
