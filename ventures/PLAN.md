# AI Monetization Experiments: Top-10 Plan (Q4 2026)

Source: the Q3 2026 ecosystem analysis (20 creator videos, the AI arbitrage agency economics, micro-SaaS, automated media, digital-product funnels, Claude API cost structure).
Prices checked 26 Sep 2026 from vendor pages and secondary sources. Re-check them before paying anything; figures marked *est.* are planning estimates.

## TL;DR

- **The portfolio.** Ten experiments, ranked by how quickly they can earn, how little capital they need, how much an agent can do, and risk. Services come first. The report's own conclusion is that cash sits in vertical workflow integration and distribution, not in generic AI output.
- **Money needed to start (updated after the review).** The agents run on your **Claude subscription** (`backend = "claude-code"`), so **no API credits are needed**. The shared foundation is **~$21 upfront + ~$23/mo**: brand domain, a secondary outreach domain, two mailboxes and a small server. Running all ten adds only **~$65 upfront + ~$4/mo** in required tools. Nothing needs a loan or outside investment.
- **API credits are optional.** Only if you switch to `backend = "api"`: prepaid credits (e.g. $100) with spend capped at $250/mo.
- **Required before the first paying service client.** About **$100** for an LLC and **~$90–170/mo** for general liability and professional (E&O) insurance. Once you sell services, the real monthly cost is **~$115–195**.
- **Adversarial review.** See [reviews/2026-09-26-claude-adversarial-review.md](reviews/2026-09-26-claude-adversarial-review.md). Its low-risk fixes are applied: warmed secondary domain, gates moved later, no call recording, insurance required. Its portfolio changes (reprice voice, merge 1+2, swap #4/#9/#10) are awaiting a decision.
- **Marketing.** **No experiment needs marketing money to start.** Every go-to-market plan begins organic: personalised outreach, SEO pages, free tools, content. Paid tests are optional and capped. They unlock only after an organic channel shows a measured conversion rate. If every paid test ran at once it would total ~$2,000/mo.
- **The agents.** Each experiment has its own Claude agent. It researches, builds, writes, drafts outreach and content, tracks KPIs, and advances its phase plan on a schedule. A portfolio manager checks kill gates weekly and auto-pauses losers.
- **Human-gated actions.** Agents **cannot spend money, create accounts or make legal commitments.** Those always wait for your approval. Sending and publishing also wait by default, until you choose to auto-approve them.
- **Your job.** Approve actions, take sales calls, and report real numbers (revenue, clients, replies). Budget **~10–15 hours/week** for the recommended first wave.

## What the analysis actually supports (and what I corrected)

**Takeaways used to shape the portfolio:**

1. **Generic AI agencies churn and fail.** The report cites ~90% failing within six months. Vertical specialists that own a whole workflow keep clients. So every service experiment targets one niche.
2. **Distribution beats building.** Code and media are nearly free to produce, so each experiment gets an explicit marketing and SEO plan. The agents spend at least a third of their sessions on distribution once something sellable exists.
3. **Speed-to-lead and tier-1 support deflection are the highest-ROI workflows.** Leads answered within 5 minutes are ~21× likelier to qualify than at 30 minutes. Agents can deflect 30–60% of tier-1 support tickets. These become experiments 1, 2 and 4.
4. **The API cost levers are real.** Prompt caching (cache reads cost 10% of the input rate), the Batch API (50% off), and model routing (strongest model for strategy, Sonnet 5 for drafting, Haiku 4.5 for bulk). All three are built into the agent framework.
5. **Selling education and affiliate links is the most reliable creator business.** Experiments 8 and 9 do it honestly, with real build notes, and feed the service funnel.

**Caveats and corrections:**

- **Unsourced statistics.** Several figures are creator or industry claims without a primary source: the 90% agency failure rate, the "21×" figure, and $39k/mo faceless channels. They were used as directional signals, not as forecasts.
- **YouTube bar is rising.** The Partner Program ads tier currently needs 1,000 subscribers and 4,000 watch hours (or 10M Shorts views in 90 days). **From 1 Feb 2027 new applicants need 8,000 hours or 20M Shorts views.** A new channel shouldn't count on ad revenue, so experiment 9 is judged on funnel leads.
- **Old model in the brief.** The brief's voice stack cites Claude 3.5 Sonnet, now a legacy model. The agents use Opus 5 for strategy, Sonnet 5 for drafting and Haiku 4.5 for bulk work.
- **Named creator tools.** The tools the videos mention mostly check out as real products or repos: Floot, SlopMonster, Archify, DeepSeek Harness, Hostinger Horizons, Seedance 2.5, Wan 3.0 and others. None of them is required here; the framework only needs the Anthropic SDK.
- **KDP royalty change.** Books priced **under $9.99** now earn a 50% royalty instead of 60% (since June 2025). AI-generated content must be disclosed, and there is a limit of 3 new titles per day.

## How the ten were ranked

Each experiment was scored 1–5 on five criteria. For risk, 5 means low compliance or platform risk. The weights were revenue 25%, speed 25%, capital 15%, agent leverage 20% and risk 15%.

| Rank | Experiment | Revenue potential | Speed to first $ | Capital efficiency | Agent leverage | Risk (5 = low) | Score |
|---|---|---|---|---|---|---|---|
| 1 | Vertical AI voice receptionist | 5 | 4 | 4 | 4 | 3 | **4.1** |
| 2 | Speed-to-lead automation | 4 | 4 | 5 | 4 | 3 | **4.0** |
| 3 | Productized AI workflow audit | 3 | 5 | 5 | 4 | 5 | **4.3** |
| 4 | Shopify tier-1 support deflection | 4 | 3 | 5 | 4 | 3 | **3.8** |
| 5 | Batch document extraction service | 4 | 3 | 5 | 5 | 4 | **4.1** |
| 6 | Programmatic-SEO micro-tools | 3 | 1 | 5 | 5 | 4 | **3.4** |
| 7 | Automation templates + comment-to-DM funnel | 3 | 3 | 5 | 4 | 3 | **3.5** |
| 8 | "AI that actually works" newsletter | 3 | 2 | 5 | 4 | 5 | **3.6** |
| 9 | Human-edited educational YouTube channel | 3 | 1 | 5 | 3 | 3 | **2.8** |
| 10 | KDP activity/puzzle books | 2 | 3 | 5 | 4 | 3 | **3.3** |

The rank is a portfolio priority, not a pure sort by score. Where the two differ, it's for one of these reasons:
- **Audit (4.3) is #3, behind voice (4.1).** The audit is the funnel entry and its revenue is capped by your hours. The voice receptionist is the recurring-revenue engine the audit sells into.
- **Speed-to-lead (4.0) and support deflection (3.8) rank above document extraction (4.1).** Speed-to-lead reuses the voice experiment's prospect list and build. Support deflection has the higher recurring ceiling per client ($500–1,500/mo). Document extraction stands alone and can start in wave 2 without losing anything.
- **Micro-tools (3.4) and templates (3.5) rank above the newsletter (3.6).** SEO compounds, so it should start early. Templates are almost free to produce from the wave-1 builds.
- **YouTube (2.8) ranks above KDP (3.3).** Its videos feed the newsletter, templates and audit. KDP is a standalone, small bet.

**Portfolio flywheel:**
- Content (8, 9) and free assets (6, 7) build trust at $0.
- That trust converts into audits (3).
- Audits convert into retainers (1, 2, 4, 5).
- Every client build becomes the next video, issue, template and case study.

## Investment summary

### Foundation (shared, buy once)

| Item | Upfront | Monthly | Needed? |
|---|---|---|---|
| Claude usage for the agents: runs on your Claude Pro/Max subscription | – | included in plan | **Required** (you have it) |
| Anthropic API credits (only for `backend = "api"`). Spend is capped at $250/mo total plus a per-experiment cap | $100 | usage ≤ cap | Optional |
| Secondary outreach domain + mailbox, warmed up 2–4 weeks before cold email | $10.44/yr | $8.40 | **Required** for experiments 1, 2, 4, 5 |
| Brand .com domain (Cloudflare Registrar, at cost) | $10.44/yr | – | **Required** |
| Google Workspace Business Starter, 1 mailbox | – | $8.40 ($7 on an annual plan) | **Required** |
| DigitalOcean Basic droplet (runs the agents' cron, n8n and small services) | – | $6 | **Required** |
| Stripe (payment links, invoices) | – | 2.9% + $0.30 per payment | **Required** (fees only) |
| LLC (e.g. Wyoming $100 + $60/yr; $35–$500 by state) | ~$100 | ~$5 | Recommended before client contracts |
| General liability + E&O insurance | – | ~$90–170 | Recommended before the first service client |
| **Required total** | **~$21** | **~$23** | |

### Per experiment

On the subscription backend there is no API spend. On the API backend, spend is capped separately: $15–40/mo per experiment and $250 for the portfolio. Paid marketing is always an optional test that unlocks only after organic proof.

| # | Experiment | Required setup | Required monthly | Optional ops (when scaling) | Optional paid marketing (after proof) | API cap/mo | Human hrs/wk | Time to first $ |
|---|---|---|---|---|---|---|---|---|
| 1 | Voice receptionist | $20 voice credits for demos | $1.15 Twilio number | Cold-email stack ~$21 + $64/mo; GoHighLevel $297/mo at ≥3 clients | Google Search ads $300–600 *est.*; chamber ~$40 | $40 | 5–8 | 4–8 wks |
| 2 | Speed-to-lead | $19.50 (10DLC brand $4.50 + $15 vetting) | ~$2.65 | n8n Cloud €24 instead of self-host | Retargeting ~$150 *est.* | $25 | 3–5 | 3–6 wks |
| 3 | AI workflow audit | $0 | $0 | – | LinkedIn boosts ~$100 *est.* | $25 | 3–6 per audit | 2–4 wks |
| 4 | Support deflection | $0 (Shopify Partner and dev store free) | $0 | App Store listing $19 one-time | App Store ads ~$300 *est.* | $30 | 4–6 | 6–10 wks |
| 5 | Document extraction | $0 | $0 (~$0.001–0.01/doc in API) | – | Search ads $200–400 *est.* | $25 | 2–4 | 4–8 wks |
| 6 | Micro-tools SEO | $10.44 domain | $0 (Cloudflare Pages free) | – | SEO tool ~$50 | $30 | 1–2 | 3–6 months |
| 7 | Automation templates | $0 (Gumroad: 10% + $0.50/sale) | $0 | ManyChat Pro ~$15 | Meta ads $150–300 *est.* | $20 | 2–4 | 3–6 wks |
| 8 | Newsletter | $0 (Beehiiv free to 2,500 subs / Kit to 10,000) | $0 | Beehiiv Scale $49 | Paid subscriber growth $100–300 *est.* | $20 | 1–2 | 2–4 months |
| 9 | YouTube channel | $0 | $0 | ElevenLabs Creator $22 (if not using your own voice) | none recommended | $20 | 3–5 | 3–6 months |
| 10 | KDP books | ~$15 proof copies | $0 | – | Amazon Ads ~$150 | $15 | 1–2 | 4–8 wks |
| | **All ten** | **~$65** | **~$4** | | **up to ~$2,000 if every test ran** | **$250** | | |

**Card-fee note.** Card processing (Stripe 2.9% + $0.30, Gumroad 10% + $0.50, Etsy/KDP marketplace cuts) comes out of revenue, not your pocket.

## The ten experiments

Each section is the summary. The full brief each agent works from is in `venture_lab/experiments/catalog.py` (offer, phases, gates, KPIs) and `marketing.py` (go-to-market plan). Print one with `venture-lab show <id>`.

### 1. Vertical AI voice receptionist (`voice-receptionist`)

- **Offer.** An inbound AI receptionist for one trade (HVAC, plumbing, electrical, garage door or roofing) in one metro. It answers 24/7, sends emergencies to the on-call tech, books jobs into the calendar and texts the owner a summary.
- **Pricing.** **$497/mo** (up to 1,000 min) plus a $750 setup fee.
- **Unit economics.** Retell or Vapi cost ~$0.13–0.31/min all-in. That leaves a ~60–75% gross margin at typical volumes. The agent models this with a deterministic calculator.
- **The agent does:**
  - Picks the vertical from evidence and prices competitors.
  - Writes the offer and landing page.
  - Builds demo and client receptionist specs. The `build_voice_agent_spec` tool outputs a greeting with AI disclosure and a recording notice, emergency transfer rules, booking tools, and import notes for Vapi, Retell and GoHighLevel.
  - Researches 30 prospects a week and drafts personalised emails.
  - Writes weekly client call reports.
- **You do:** approve spend and accounts, import specs, run discovery calls and demos, close deals, and report outcomes.
- **Marketing and SEO:**
  - Personalised cold email (max 20/day, from your own mailbox, $0).
  - An after-hours missed-call audit: you call the prospect's line after hours (no recording) and send a short written note of what happened.
  - A live demo line on the landing page.
  - Trade partnerships with supply houses and associations, plus a referral month.
  - SEO: one landing page per vertical × city ("AI answering service for HVAC companies in Denver"), cost and comparison pages, a Google Business Profile, and case studies.
- **Funding.** None needed to start. Search ads (~$300–600/mo *est.*) only after 2 closed deals give a real close rate. Insurance before the first client.
- **Gates.** Kill or rethink if any of these fails:
  - Day 45: ≥3 discovery calls booked (moved from day 30 to allow for the domain warm-up).
  - Day 60: ≥1 paying client.
  - Day 90: ≥3 clients (target $1,500 MRR).
- **Compliance.** Inbound calls only; outbound AI calls need prior express written consent under TCPA. Sending texts needs A2P 10DLC registration. Healthcare and legal verticals are excluded until HIPAA and bar-rule handling exists.

### 2. Speed-to-lead automation (`speed-to-lead`)

- **Offer.** A missed-call text-back plus an instant web-form reply within 60 seconds. The AI qualifies the lead over SMS or email, sends a booking link and alerts the owner.
- **Pricing.** $297/mo + $500 setup. It's the cheaper first step and the upsell path into experiment 1.
- **Build.** n8n self-hosted on the $6 VPS, plus Twilio SMS (~$0.012/segment including carrier fees). Each client needs its own 10DLC registration, passed through at cost.
- **Marketing and SEO:**
  - Target businesses visibly paying for leads (public Google Ads Transparency Center and Meta Ad Library).
  - A free "lead response audit": you submit the prospect's web form and time the reply; the agent writes the report.
  - Cross-sell to experiment 1's prospects who aren't ready for voice.
  - SEO: "missed call text back for <trade>" pages and a free lead-leakage calculator.
- **Funding.** None. Retargeting (~$150/mo) is optional later.
- **Gates.** Day 45: ≥3 discovery calls. Day 60: ≥1 client. Day 90: ≥4 clients.

### 3. Productized AI workflow audit (`ai-ops-audit`)

- **Offer.** A $750 fixed-price audit ($450 for the first 3) for 10–50 person businesses. It includes an intake form, a 60-minute interview (you), and a report delivered in 5 days: a workflow map, the top-5 automations ranked by ROI, build-vs-buy picks and a 90-day roadmap. The fee is credited against implementation.
- **Why.** The report's core finding is that value lives in workflow mapping and change management. This monetises that directly, and it feeds experiments 1, 2, 4 and 5.
- **Marketing and SEO:**
  - A call to action in every newsletter issue and video.
  - Founder-led LinkedIn: the agent drafts 3 posts a week and you post them.
  - Free workshops with chambers of commerce and SBDCs.
  - Bookkeeper and IT-provider referral partners (10–20% fee, paid from revenue).
  - SEO: a gated sample report and "AI readiness checklist for <trade>" guides.
- **Funding.** None. LinkedIn boosts (~$100) are optional.
- **Gates.** Day 21: ≥1 audit sold. Day 45: ≥3 sold. Day 90: ≥1 implementation deal.

### 4. Shopify tier-1 support deflection (`support-deflection`)

- **Offer.** A grounded agent (store policies plus order lookups) for DTC stores with 300–3,000 tickets/month. It runs in draft mode for 2 weeks, then goes automatic on the intents that reach ≥95% accuracy. Weekly deflection reports.
- **Pricing.** $500–1,500/mo + $1,000 setup. API cost is ~$0.01–0.03/ticket with caching.
- **Marketing and SEO:**
  - Cold email to stores with public support-pain signals.
  - DTC operator communities.
  - Before/after case studies.
  - Later, a Shopify App Store listing ($19 one-time; 0% revenue share on the first $1M) with App Store search optimisation.
  - SEO: Shopify returns and order-status automation how-tos, an honest comparison with native helpdesk AI, and a support cost calculator.
- **Funding.** None for the first clients. App Store ads are optional once there are reviews.
- **Gates.** Day 45: ≥3 calls. Day 60: ≥1 pilot store. Day 90: ≥2 paying clients (target ≥30% deflection).

### 5. Batch document extraction service (`doc-extraction`)

- **Offer.** Pick one niche: lease abstraction for property managers, rate confirmations and bills of lading for freight brokers, or invoices for bookkeepers. Folder in, spreadsheet out in 24h, with confidence flags.
- **Pricing.** $1–3/doc or $300/mo. Cost is ~$0.001–0.01/doc on Haiku 4.5 through the Batch API.
- **Built-in tools.** `submit_extraction_batch` / `collect_extraction_batch`: schema-constrained output, cached instructions, 50% batch discount, and cost booked per job.
- **Marketing and SEO:**
  - Cold email from public registries (e.g. FMCSA broker data) and association directories.
  - A free 25-document trial.
  - Niche forum answers.
  - White-label partnerships.
  - SEO: exact-match service pages ("lease abstraction service", "rate confirmation to Excel") and a free, rate-limited single-document tool.
- **Funding.** None. Exact-match search ads (~$200–400) optional after a paid pilot.
- **Gates.** Day 21: ≥95% field accuracy on 30 documents you labelled. Day 45: ≥1 paid pilot. Day 90: $1k MRR target.

### 6. Programmatic-SEO micro-tools (`micro-tools-seo`)

- **Offer.** Free calculators and generators for the same trades, hosted on Cloudflare Pages (free, commercial use allowed; Vercel Hobby is not). Revenue comes from AdSense, affiliates and a $5–9/mo pro tier.
- **SEO plan:**
  - One tool per search intent.
  - Fast static pages with schema markup and unique worked examples.
  - Hub-and-spoke internal links, with the sitemap submitted to Search Console.
  - A monthly prune-or-improve pass using Search Console data.
  - Backlinks through embeddable widgets and resource-page outreach.
- **Funding.** None. SEO costs time, not money; a keyword tool (~$50/mo) is optional.
- **Gates.** Day 30: ≥5 tools live. Day 75: ≥300 organic clicks in the last 28 days. Day 150: $100/mo revenue target.
- **Timing.** Slow burn. Judge it at 3–6 months.

### 7. Automation template store + comment-to-DM funnel (`automation-templates`)

- **Offer.** n8n workflow packs for trades, at $29–99 each and $149 for the bundle. They're packaged from the builds in experiments 1–2.
- **Distribution.** Short videos ending with "comment WORKFLOW". The keyword triggers an automated DM with a lead magnet, then the paid pack. That's the report's link-free funnel. Instagram allows one private reply per comment within 7 days.
- **Marketing and SEO:**
  - Free mini-templates in community galleries.
  - A creator affiliate program (30%, paid from revenue).
  - Gumroad Discover.
  - SEO: "<tool> <use case> template" product pages and free simplified versions on the blog.
- **Funding.** ~$15/mo ManyChat once you post regularly. A Meta ads test (~$150–300) is optional after organic conversion is measured.
- **Gates.** Day 30: ≥3 products live. Day 60: ≥10 sales. Day 90: $300/mo target.

### 8. "AI that actually works" newsletter (`ai-ops-newsletter`)

- **Offer.** A weekly issue with one tested automation, one tool review and one number, drawn from the experiments' real builds.
- **Monetisation.** Disclosed affiliates: GoHighLevel 40% recurring, Make 35% for 12 months, n8n 30% for 12 months (no paid ads). Plus audit leads.
- **Marketing and SEO:**
  - SEO-indexed archive plus a weekly long-form post.
  - LinkedIn and X drafts from each issue.
  - Free newsletter cross-recommendations.
  - Lead magnets from experiments 6–7.
  - Quarterly-updated guides ("AI tools for HVAC companies 2026").
- **Funding.** None. Paid subscriber growth (~$1–3/sub *est.*) is optional once each subscriber's value is known.
- **Gates.** Day 30: ≥100 subscribers. Day 75: ≥300. Day 120: $100/mo target.

### 9. Human-edited educational YouTube channel (`faceless-edu-channel`)

- **Offer.** Two Shorts a week plus a walkthrough every two weeks. Every video uses real screen recordings of experiment builds and gets a human edit. That passes YouTube's inauthentic-content bar, which pure AI "slop" channels fail.
- **Marketing and SEO:**
  - YouTube search: titles from autocomplete research, chapters, and a pinned lead magnet.
  - Shorts repurposed to TikTok, Reels and LinkedIn.
  - Creator collaborations.
  - Videos embedded in the newsletter and SEO posts.
- **Funding.** None. ElevenLabs ($22/mo) only if you don't use your own voice.
- **Gates.** Day 30: ≥8 videos. Day 60: ≥250 subscribers. Day 90: 50 funnel leads target.

### 10. KDP activity and puzzle books (`kdp-activity-books`)

- **Offer.** Code-generated puzzles (deterministic, not low-quality AI filler) for narrow hobby niches, proofed by you. $9.99–12.99 paperbacks earn ~$2–4 each.
- **Marketing and SEO:**
  - Amazon search optimisation: title and subtitle keywords, 7 backend keyword slots, categories and A+ content.
  - Series pages.
  - Pinterest pins for gift niches.
  - Seasonal timing.
- **Funding.** None. An Amazon Ads auto-campaign test (~$150/mo) is optional.
- **Gates.** Day 30: ≥3 titles live. Day 60: ≥20 units sold. Day 120: $100/mo target.

## Launch sequence

| Wave | When | Experiments | Why | API cap to set (API backend only) |
|---|---|---|---|---|
| 1 | Week 1 | 3 audit, 1 voice receptionist, 2 speed-to-lead, 8 newsletter | Fastest cash, shared prospect research, audience from day one | ~$110/mo |
| 2 | Week 3–4 | 5 doc extraction, 6 micro-tools, 7 templates | Reuse wave-1 builds; long-lead SEO starts early | +$75/mo |
| 3 | After first revenue (~month 2) | 4 support deflection, 9 YouTube, 10 KDP | Needs case studies/footage; lower-priority bets | +$65/mo |

Every Monday the portfolio manager (`venture-lab report --memo`) recommends whether to double down, hold or kill. Hard-gate failures auto-pause an experiment. You can resume one with `venture-lab activate <id> --override "reason"`.

## How the agents run

```
cron / cloud routine ──► venture-lab tick   (backend: claude-code = your subscription | api = API credits)
                             │
                             ├─ portfolio review: evaluate gates on verified metrics → auto-pause hard failures
                             └─ for each active experiment whose cadence is due:
                                  Claude agent session (tool runner, prompt-cached brief)
                                    tools: web_search/web_fetch, save/read artifacts, record_metric,
                                           log_learning, request_action, list_actions, advance_phase,
                                           + specialised (voice spec builder, unit economics, batch extraction)
                                    ├─ artifacts → var/artifacts/<experiment>/
                                    ├─ usage $ → ledger (stops mid-session at the cap)
                                    └─ outward actions → approval queue ──► you (`venture-lab approve 12`)
                                                                          └─► optional webhook executor (n8n)
```

**Guardrails built into the code, not just the prompt:**
- `spend`, `account` and `legal` actions can never be auto-approved.
- Any action with a price attached is reclassified as `spend`.
- The per-experiment and portfolio API caps are checked after every model turn.
- Gates count only human- or integration-reported numbers for revenue, clients and sales. The agent can't talk its way past a kill gate.
- Artifacts are sandboxed to the experiment's workspace.

**Subscription backend.** Each session is `claude -p`, with tools limited to: web search and fetch, file edits inside the experiment's workspace, and `venture-lab agent …` commands. Anything else is denied, not prompted. The owner-only commands (approve, metric, activate…) refuse to run inside agent sessions. A live test on 26 Sep 2026 confirmed that the agent wrote its file, recorded its metric, and was blocked from `approve`.

**Model routing (API backend).**
- Strategy and sales experiments use `claude-opus-5` with adaptive thinking and server-side refusal fallback.
- Content-heavy experiments use `claude-sonnet-5`.
- Bulk extraction uses `claude-haiku-4-5` through the Batch API.
- You can change any of these in `venture_lab.toml`.

## Considered and not selected

- **Generic "AI chatbot" agency.** It's the model the report says fails ~90% of the time; replaced by vertical experiments 1, 2 and 4.
- **White-label GoHighLevel SaaS reselling.** $497/mo upfront, and it lands you on the churn treadmill. It stays an optional scale-up inside experiment 1.
- **Print-on-demand merch.** Thin margins and saturated marketplaces. KDP is the cheaper marketplace test.
- **Outbound AI cold-calling.** High legal risk under TCPA; excluded.
- **"Make money with AI" courses.** Credible only after these experiments produce results. Revisit at month 4 with real case studies.

## Your first-week checklist

1. **Foundation.** Buy the brand domain and a secondary outreach domain, create two Workspace mailboxes and a Stripe account (≈$21 + $23/mo). Start warming up the outreach mailbox on day 1.
2. **Pick where the agents run (both use your subscription, no API key):**
   - **Cloud:** a scheduled Claude Code routine, as described in [deploy/cloud-routine.md](deploy/cloud-routine.md). State is committed to the repo.
   - **Your computer:** `pip install -e ventures/`, copy `venture_lab.example.toml` to `venture_lab.toml` (it defaults to `backend = "claude-code"`), then cron `venture-lab tick`.
3. **Activate.** `venture-lab activate ai-ops-audit voice-receptionist speed-to-lead ai-ops-newsletter`, or the reviewed line-up once you decide. At most 3 sessions run per scheduled run, to protect your plan's usage limits.
4. **Approvals.** Review the queue daily with `venture-lab approvals -v`, then `approve`/`reject` with a note. The agents read your notes.
5. **Report real numbers.** `venture-lab metric voice-receptionist discovery_calls_booked 2` and similar.
6. **Before the first paying service client:** LLC and insurance (~$100 + ~$90–170/mo).
