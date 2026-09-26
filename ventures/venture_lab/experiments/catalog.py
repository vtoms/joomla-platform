"""The top-10 experiment portfolio. Prices checked September 2026; re-check before paying."""

from __future__ import annotations

from dataclasses import replace

from venture_lab.experiments.base import CostItem, Experiment, Gate, Phase
from venture_lab.experiments.marketing import MARKETING

# Shared by every experiment; bought once for the whole portfolio.
FOUNDATION: tuple[CostItem, ...] = (
    CostItem(
        "Anthropic API credits (prepaid; spend is capped in venture_lab.toml)",
        100,
        0,
        "draws down at the portfolio cap, $250/mo by default",
        required=False,
        note="only for backend = api; $0 when agents run on your Claude subscription (backend = claude-code)",
    ),
    CostItem("Brand .com domain (Cloudflare Registrar, at cost)", 10.44, 0, "renews ~$10.44/yr"),
    CostItem("Google Workspace Business Starter, 1 mailbox (Flexible)", 0, 8.40, note="$7/mo on an annual plan"),
    CostItem(
        "Secondary outreach domain + mailbox, warmed up 2-4 weeks before any cold email",
        10.44,
        8.40,
        note="protects the brand domain's deliverability (experiments 1, 2, 4, 5)",
    ),
    CostItem("Stripe account (payment links, invoices)", 0, 0, "2.9% + $0.30 per US card payment"),
    CostItem("VPS for n8n and small services (DigitalOcean Basic 1 GB)", 0, 6),
    CostItem(
        "LLC formation (e.g. Wyoming $100 + $60/yr; varies $35-$500 by state)",
        100,
        5,
        required=False,
        note="recommended before signing client contracts",
    ),
    CostItem(
        "General liability + professional (E&O) insurance",
        0,
        130,
        required=False,
        note="~$90-170/mo; required in practice before the first paying service client (experiments 1-5)",
    ),
)


def foundation_setup(required_only: bool = True) -> float:
    return sum(c.one_time_usd for c in FOUNDATION if c.required or not required_only)


def foundation_monthly(required_only: bool = True) -> float:
    return sum(c.monthly_usd for c in FOUNDATION if c.required or not required_only)


LOCAL_SERVICE_COMPLIANCE = (
    "Outreach: personalised B2B email only, at most 20/day during validation, truthful sender, physical address and opt-out (CAN-SPAM).",
    "Cold email goes only from the warmed secondary domain, never the brand domain; stop if spam complaints near 0.1%.",
    "Never record calls with prospects (all-party-consent states); describe what happened in writing instead.",
    "No outbound AI calls or AI texts to consumers without prior express written consent (TCPA).",
    "Business SMS needs A2P 10DLC brand + campaign registration before sending.",
    "The AI must disclose it is an AI when asked; greetings announce recording.",
    "No earnings or results guarantees in sales copy; case studies only with written client permission.",
)

_EXPERIMENTS: tuple[Experiment, ...] = (
    Experiment(
        id="voice-receptionist",
        rank=1,
        name="Vertical AI voice receptionist for home-service trades",
        one_liner="Done-for-you inbound AI receptionist that answers, qualifies and books calls for one trade vertical.",
        thesis=(
            "Local service businesses miss a large share of inbound calls, especially after hours, and each missed call "
            "is a lost job. Voice AI with sub-second latency, interruption handling and live booking is now good enough "
            "to sell as an outcome (captured jobs), not a chatbot. Generic agencies churn; specialising in one trade "
            "with its own scripts, emergency rules and integrations is the moat."
        ),
        customer="Owner-operated HVAC, plumbing, electrical, garage-door or roofing companies with 2-25 staff in one metro area.",
        offer="Inbound AI receptionist live in 7 days: answers 24/7, triages emergencies to the on-call tech, books into the calendar, texts a summary. Monthly call report.",
        pricing="$497/mo (up to 1,000 min) + $750 setup; pilots at $250 setup. Target gross margin >= 65%.",
        evidence=(
            "Brief: white-label platform + ~1,000 min/mo costs ~$170 against $797 pricing (~79% gross margin).",
            "Brief: responding within 5 minutes makes a lead ~21x more likely to qualify than at 30 minutes.",
            "Brief: generic AI agencies reportedly fail at ~90% within 6 months; the survivors are vertical specialists.",
            "Verified Sep 2026: Retell ~$0.13-0.31/min all-in, Vapi ~$0.12-0.25/min all-in, Twilio number $1.15/mo.",
        ),
        risks=(
            "Churn when the novelty wears off: tie reporting to booked jobs and revenue captured.",
            "Platforms (GoHighLevel, phone systems) bundling native voice AI.",
            "Owners distrust AI with customers: offer a 14-day pilot with call recordings they can audit.",
        ),
        compliance=LOCAL_SERVICE_COMPLIANCE
        + ("Healthcare and legal verticals are out of scope until HIPAA / bar-rule handling is in place.",),
        agent_does=(
            "Pick the vertical and metro from evidence; write the offer, landing page and one-page PDF.",
            "Build the demo receptionist spec and QA scripts with build_voice_agent_spec.",
            "Research prospects from public sources and draft personalised emails as outreach requests.",
            "Build per-client specs, weekly call reports and case studies (with permission).",
        ),
        human_does=(
            "Approve spend and accounts (voice platform, phone number); import specs into the platform.",
            "Take discovery calls and demos, sign clients, collect payment.",
            "Report replies, calls booked, clients and MRR with `venture-lab metric`.",
        ),
        costs=(
            CostItem(
                "Voice platform credits for demos (Retell or Vapi, pay-as-you-go)",
                20,
                0,
                "~$0.13-0.31/min all-in per client minute, passed into pricing",
            ),
            CostItem("Twilio demo phone number", 0, 1.15, "$0.0085/min inbound"),
            CostItem(
                "Google Places API for prospect research", 0, 0, "5,000 free Text Search Pro calls/mo, then ~$32/1k"
            ),
            CostItem(
                "Cold email sending tool (Instantly Growth) + 2 warmed secondary domains/mailboxes",
                21,
                64,
                required=False,
                note="only after hand-sent outreach proves the message",
            ),
            CostItem(
                "GoHighLevel Unlimited (white-label CRM + voice AI)",
                0,
                297,
                required=False,
                note="only at >= 3 clients; voice ~$0.06-0.08/min",
            ),
        ),
        phases=(
            Phase(
                "Niche and offer",
                7,
                "Chosen vertical + metro, priced offer, landing copy, demo accounts requested.",
                (
                    "Compare 4-5 trade verticals on call volume, job value, seasonality and competition; pick one with reasons.",
                    "Price competing receptionist services (human answering services and AI receptionists); position against them.",
                    "Model unit economics at 1, 3 and 10 clients with calculate_unit_economics.",
                    "Write offer one-pager and landing page copy; request spend for a demo number and voice credits.",
                ),
            ),
            Phase(
                "Demo build",
                7,
                "A working demo line a prospect can call.",
                (
                    "Build the demo receptionist spec for a realistic fictional business in the vertical.",
                    "Write a 20-scenario QA script (emergencies, pricing questions, angry caller, spam, Spanish speaker).",
                    "Write the 2-minute demo call script and the discovery-call agenda.",
                ),
            ),
            Phase(
                "Prospecting",
                21,
                "At least 3 discovery calls booked.",
                (
                    "Research 30 prospects a week from public sources (website, hours, reviews that mention unanswered calls).",
                    "Draft personalised first-touch emails and one follow-up each as outreach requests (max 20/day).",
                    "Refine messaging weekly from the human's reply notes; log what works.",
                ),
                cadence="weekdays",
            ),
            Phase(
                "Pilot clients",
                30,
                "1-3 paying pilots live with weekly reports.",
                (
                    "Build each client's receptionist spec from their intake form; prepare the import checklist.",
                    "Produce weekly call reports: calls answered, jobs booked, emergencies transferred, revenue captured.",
                    "Draft a case study for client approval.",
                ),
                cadence="weekdays",
            ),
            Phase(
                "Productize and scale",
                60,
                "3+ clients, repeatable onboarding, referral loop.",
                (
                    "Write onboarding SOPs and templates so a client goes live in under 5 days.",
                    "Design a referral offer; decide whether a white-label platform now pays for itself.",
                ),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(45, "discovery_calls_booked", ">=", 3),  # ~30 days of sending after warm-up
            Gate(60, "paying_clients", ">=", 1),
            Gate(90, "paying_clients", ">=", 3),
            Gate(90, "mrr_usd", ">=", 1500, hard=False),
        ),
        kpis=(
            "prospects_researched",
            "outreach_sent",
            "replies",
            "discovery_calls_booked",
            "demos_given",
            "paying_clients",
            "mrr_usd",
            "minutes_handled",
            "gross_margin_pct",
            "churned_clients",
        ),
        api_budget_usd_month=40,
        extra_tools=("voice_agent_spec", "unit_economics"),
        feeds=("speed-to-lead",),
    ),
    Experiment(
        id="speed-to-lead",
        rank=2,
        name="Speed-to-lead: missed-call text-back and instant web-lead qualification",
        one_liner="Automation that replies to every missed call and web form within 60 seconds, qualifies the lead and books it.",
        thesis=(
            "The cheapest proof of AI value for a local business is not a voice agent but never letting a lead go cold. "
            "A fast SMS/email response plus AI qualification is simpler to sell, cheaper to run, and a natural "
            "step up to the voice receptionist."
        ),
        customer="Same trades as experiment 1, plus med spas, home remodelers and auto repair shops that buy leads or run ads.",
        offer="Missed-call text-back, instant web-form reply, AI qualification over SMS/email, booking link, owner alert; monthly lead-response report.",
        pricing="$297/mo + $500 setup (10DLC registration fees passed through at cost).",
        evidence=(
            "Brief: response within 5 minutes is ~21x more likely to qualify than at 30 minutes.",
            "Brief: inbound lead qualification and routing is among the highest-ROI AI workflows in 2026.",
            "Verified Sep 2026: n8n self-hosted is free; Twilio SMS ~$0.0079/segment + carrier fees; 10DLC brand $4.50-$46, campaign vetting $15.",
        ),
        risks=(
            "Commodity: CRMs ship text-back natively. Differentiate on qualification quality and reporting.",
            "A2P 10DLC registration delays of 1-3 weeks per client.",
        ),
        compliance=LOCAL_SERVICE_COMPLIANCE
        + ("Texts only reply to people who contacted the business first; every text carries STOP opt-out language.",),
        agent_does=(
            "Design the n8n workflow (as importable JSON) and the qualification prompts.",
            "Write setup SOPs, 10DLC registration copy, and the client report template.",
            "Research prospects and draft outreach, reusing experiment 1's research.",
        ),
        human_does=(
            "Approve accounts and spend; import and test workflows on the VPS.",
            "Sell, onboard, register 10DLC per client, and report outcomes.",
        ),
        costs=(
            CostItem(
                "Twilio number + A2P 10DLC brand (low-volume) + campaign vetting",
                19.50,
                2.65,
                "SMS ~$0.012/segment incl. carrier fees; per-client registration passed through",
            ),
            CostItem("n8n (self-hosted on the foundation VPS)", 0, 0, note="or n8n Cloud Starter ~EUR24/mo"),
        ),
        phases=(
            Phase(
                "Build the workflow",
                10,
                "Tested workflow + demo that texts back a missed call.",
                (
                    "Write the n8n workflow JSON: Twilio missed-call webhook -> SMS -> AI qualification -> booking link -> owner alert.",
                    "Write the qualification prompt and a 15-case test set; route classification to the bulk model.",
                    "Model per-client costs at 100, 300 and 1,000 leads/month.",
                ),
            ),
            Phase(
                "Sell",
                30,
                "At least 3 discovery calls booked.",
                (
                    "Draft outreach to businesses visibly running ads or lead forms; offer a free missed-lead audit.",
                    "Build the one-page ROI calculator (leads/month x close rate x job value).",
                ),
                cadence="weekdays",
            ),
            Phase(
                "Deliver and upsell",
                50,
                "4+ clients, first upsell to voice receptionist.",
                ("Monthly lead-response reports; flag clients whose volume justifies the voice receptionist.",),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(45, "discovery_calls_booked", ">=", 3),  # ~30 days of sending after warm-up
            Gate(60, "paying_clients", ">=", 1),
            Gate(90, "paying_clients", ">=", 4),
            Gate(90, "mrr_usd", ">=", 1000, hard=False),
        ),
        kpis=(
            "workflows_tested",
            "outreach_sent",
            "discovery_calls_booked",
            "paying_clients",
            "mrr_usd",
            "median_response_seconds",
            "leads_qualified",
            "upsells_to_voice",
        ),
        api_budget_usd_month=25,
        extra_tools=("unit_economics",),
        feeds=("voice-receptionist",),
    ),
    Experiment(
        id="ai-ops-audit",
        rank=3,
        name="Productized AI workflow audit",
        one_liner="Fixed-price audit that maps a small business's workflows and hands back a costed 90-day automation roadmap.",
        thesis=(
            "The brief's core finding: value sits in workflow mapping, data quality and change management, not in "
            "the AI itself. A fixed-price audit monetises that expertise directly, qualifies buyers, and converts "
            "into implementation work for experiments 1, 2, 4 and 5."
        ),
        customer="10-50 employee businesses in the chosen trade vertical (or professional services) whose owner is curious about AI but has no plan.",
        offer="Intake form + 60-minute interview; delivered in 5 days: workflow map, top-5 automations ranked by ROI, build-vs-buy picks, 90-day roadmap.",
        pricing="$750 fixed ($450 for the first 3 clients), credited against any implementation project.",
        evidence=(
            "Brief: MIT's 'GenAI Divide' report found ~95% of generative AI pilots returned nothing measurable. Businesses need connected workflows, not point tools.",
            "Brief: Gartner attributes ~85% of AI project failures to poor data or missing context.",
            "Near-zero capital; the agent does most of the analysis and writing.",
        ),
        risks=(
            "Hard to sell to people without trust: lean on the newsletter and channel audience.",
            "Scope creep: keep a fixed deliverable and time box.",
        ),
        compliance=(
            "No guaranteed savings; ROI figures are labelled as estimates with their assumptions.",
            "Client data stays in the client's folder; NDA available on request; delete raw notes after 90 days.",
        ),
        agent_does=(
            "Write the intake questionnaire, interview guide, report template and sales page.",
            "Do pre-call research on each client; turn interview notes into the audit report.",
            "Draft implementation proposals that route work to experiments 1, 2, 4 and 5.",
        ),
        human_does=("Sell and run the interview; review every report before it goes out; invoice.",),
        costs=(CostItem("Booking + payment (Cal.com free, Stripe payment link)", 0, 0, "Stripe 2.9% + $0.30"),),
        phases=(
            Phase(
                "Package",
                7,
                "Sales page, intake form, interview guide and sample report ready.",
                (
                    "Write the sales page and a realistic sample report for a fictional business.",
                    "Write the intake questionnaire and interview guide.",
                ),
            ),
            Phase(
                "Sell and deliver",
                45,
                "3 audits delivered, 1 converted to implementation.",
                (
                    "Draft outreach to warm contacts and newsletter readers; prepare pre-call research.",
                    "Turn interview notes into audit reports within 48 hours.",
                ),
                cadence="weekdays",
            ),
        ),
        gates=(
            Gate(21, "audits_sold", ">=", 1),
            Gate(45, "audits_sold", ">=", 3),
            Gate(90, "implementation_deals", ">=", 1),
        ),
        kpis=("audits_sold", "audit_revenue_usd", "implementation_deals", "nps"),
        api_budget_usd_month=25,
        feeds=("voice-receptionist", "speed-to-lead", "support-deflection", "doc-extraction"),
    ),
    Experiment(
        id="support-deflection",
        rank=4,
        name="Tier-1 support deflection agent for Shopify stores",
        one_liner="Grounded AI agent that resolves order-status, returns, shipping and sizing tickets for DTC stores.",
        thesis=(
            "Well-built support agents handle 30-60% of tier-one inquiries. Shopify merchants with 300+ tickets/month "
            "pay for helpdesk seats and staff; a grounded agent (store policies + order lookups) with measured "
            "accuracy and human handoff is a clear ROI sale."
        ),
        customer="Shopify DTC brands doing $500k-$10M/yr with 300-3,000 support tickets per month.",
        offer="Agent drafts replies for 2 weeks (human approves), then auto-resolves the categories that hit >= 95% accuracy; weekly deflection report.",
        pricing="$500/mo up to 1,000 tickets, $1,500/mo up to 5,000; $1,000 setup.",
        evidence=(
            "Brief: 30-60% tier-one deflection is achievable; 10k tickets/day on Sonnet with caching costs ~$95/day, so small stores cost cents per ticket.",
            "Verified Sep 2026: Shopify Partner account free; App Store listing $19 one-time; 0% revenue share on the first $1M.",
        ),
        risks=(
            "Helpdesks (Gorgias, Zendesk) ship native AI; compete on accuracy and done-for-you setup.",
            "Wrong answers damage the brand: draft mode first, strict grounding, and escalation on low confidence.",
        ),
        compliance=(
            "Customer PII only through the store's own APIs; no storage beyond the ticket context; DPA with each client.",
            "The agent discloses it is an automated assistant and always offers a human.",
        ),
        agent_does=(
            "Design the agent (policy grounding, order-lookup tools, escalation rules) and the eval set.",
            "Research prospects, draft outreach, and write weekly accuracy/deflection reports.",
        ),
        human_does=(
            "Create partner/dev-store accounts; sell; connect client helpdesks; approve go-live of auto mode.",
        ),
        costs=(
            CostItem("Shopify Partner account + development store", 0, 0),
            CostItem("Shopify App Store listing fee (only if productised as an app)", 19, 0, required=False),
            CostItem(
                "Hosting for the ticket webhook service (foundation VPS)",
                0,
                0,
                "Claude API ~$0.01-0.03 per ticket with caching",
            ),
        ),
        phases=(
            Phase(
                "Prototype",
                14,
                "Agent + 100-ticket eval on a dev store with >= 90% correct answers.",
                (
                    "Write the agent spec: intents, grounding sources, tools (order status, return eligibility), escalation.",
                    "Build a 100-ticket synthetic eval set from public store policies; score it.",
                ),
            ),
            Phase(
                "Pilot",
                45,
                "1-2 stores in draft mode, then auto on safe intents.",
                (
                    "Draft outreach to stores with public support pain (slow reply complaints, large FAQ pages).",
                    "Weekly accuracy and deflection reports during pilots.",
                ),
                cadence="weekdays",
            ),
        ),
        gates=(
            Gate(45, "discovery_calls_booked", ">=", 3),  # ~30 days of sending after warm-up
            Gate(60, "pilot_stores", ">=", 1),
            Gate(90, "paying_clients", ">=", 2),
            Gate(90, "deflection_rate_pct", ">=", 30, hard=False),
        ),
        kpis=(
            "eval_accuracy_pct",
            "discovery_calls_booked",
            "pilot_stores",
            "paying_clients",
            "mrr_usd",
            "deflection_rate_pct",
            "escalation_rate_pct",
            "cost_per_ticket_usd",
        ),
        api_budget_usd_month=30,
        extra_tools=("unit_economics",),
    ),
    Experiment(
        id="doc-extraction",
        rank=5,
        name="Batch document extraction service for one back-office niche",
        one_liner="Turns piles of niche documents (leases, rate confirmations, invoices) into clean spreadsheets for a per-document fee.",
        thesis=(
            "Haiku on the Batch API costs well under a cent per document, while back offices pay staff minutes per "
            "document. Selling per-document extraction with a guaranteed accuracy check is a high-margin, "
            "low-support business that needs no audience."
        ),
        customer="Property managers (lease abstraction), freight brokers (rate confirmations/BOLs) or bookkeepers (vendor invoices); pick one.",
        offer="Upload a folder, get a spreadsheet in 24h with per-field confidence flags and a human-reviewed sample.",
        pricing="$1-3 per document or $300/mo for up to 300 documents; free 25-document trial.",
        evidence=(
            "Brief: 50k documents/day on Haiku 4.5 Batch costs ~$1,500/month, i.e. ~$0.001/document.",
            "Batch API is 50% off; cached shared instructions cut cost further.",
        ),
        risks=(
            "Accuracy on messy scans; mitigate with confidence flags and human QA of samples.",
            "Data sensitivity; offer deletion after delivery and a DPA.",
        ),
        compliance=(
            "Process client documents only under a written agreement; delete inputs after delivery.",
            "No financial or legal advice about document contents.",
        ),
        agent_does=(
            "Pick the niche; design schemas; run extraction batches; score accuracy on labelled samples; write the sales page and outreach.",
        ),
        human_does=("Label 30 sample documents for accuracy checks; sell; receive and return client files securely.",),
        costs=(
            CostItem(
                "No fixed tools; Claude Batch API usage only", 0, 0, "~$0.001-0.01 per document on the bulk model"
            ),
        ),
        phases=(
            Phase(
                "Prove accuracy",
                21,
                ">= 95% field accuracy on 30 human-labelled public/sample documents.",
                (
                    "Choose the niche and field schema; collect public sample documents into samples/.",
                    "Run submit_extraction_batch, then collect results and compare with labels.",
                ),
            ),
            Phase(
                "Sell",
                60,
                "Paying pilots and a monthly customer.",
                ("Sales page with the accuracy report; outreach offering the free 25-document trial.",),
                cadence="weekdays",
            ),
        ),
        gates=(
            Gate(21, "sample_accuracy_pct", ">=", 95),
            Gate(45, "paid_pilots", ">=", 1),
            Gate(90, "mrr_usd", ">=", 1000, hard=False),
        ),
        kpis=(
            "sample_accuracy_pct",
            "cost_per_doc_usd",
            "trials_started",
            "paid_pilots",
            "documents_processed",
            "mrr_usd",
        ),
        api_budget_usd_month=25,
        extra_tools=("batch_extraction", "unit_economics"),
    ),
    Experiment(
        id="micro-tools-seo",
        rank=6,
        name="Programmatic-SEO portfolio of niche micro-tools",
        one_liner="Single-purpose calculators and generators on free hosting, monetised with ads, affiliates and a small pro tier.",
        thesis=(
            "Software is nearly free to build, so the moat is distribution. Search demand for narrow utilities "
            "(trade calculators, compliance checklists, template generators) is durable. Build many cheap tools, "
            "keep those that rank."
        ),
        customer="Search visitors in the same trades as experiments 1-2 (e.g. 'HVAC tonnage calculator', 'plumbing estimate template').",
        offer="Free tools; a $5-9/mo pro tier for saved/branded outputs; contextual affiliate links.",
        pricing="Ads (AdSense) + affiliate + $5-9/mo pro.",
        evidence=(
            "Brief: winning micro-SaaS operators out-distribute rather than out-build.",
            "Verified Sep 2026: Cloudflare Pages free tier allows commercial use (Vercel Hobby does not).",
        ),
        risks=(
            "SEO takes 3-6 months; AI answers reduce clicks. Target tools that need interaction, not facts.",
            "Thin programmatic pages get devalued: every page must do something useful.",
        ),
        compliance=(
            "AdSense publisher policies; affiliate disclosure on every page with links.",
            "No health, legal or financial calculators that imply professional advice without disclaimers.",
        ),
        agent_does=("Keyword research; build tools as static HTML/JS in site/; write page copy; propose deploys.",),
        human_does=(
            "Set up Cloudflare Pages + Search Console + AdSense; approve deploys; report Search Console numbers.",
        ),
        costs=(
            CostItem("Second domain for the tools site", 10.44, 0),
            CostItem("Cloudflare Pages + Web Analytics + Search Console", 0, 0),
        ),
        phases=(
            Phase(
                "Build 10 tools",
                30,
                "10 tools live with unique, useful pages.",
                (
                    "Find 30 candidate tools with search demand and weak competition; pick 10.",
                    "Build each as a self-contained static page with schema markup; request a deploy per batch.",
                ),
            ),
            Phase(
                "Iterate on data",
                90,
                "Double down on tools that get impressions.",
                (
                    "Read Search Console numbers from the human; improve winners, prune losers, add pro tier to the top tool.",
                ),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(30, "tools_live", ">=", 5, verified=False),
            Gate(75, "organic_clicks_28d", ">=", 300),
            Gate(150, "revenue_usd_month", ">=", 100, hard=False),
        ),
        kpis=("tools_live", "indexed_pages", "organic_clicks_28d", "revenue_usd_month", "pro_subscribers"),
        api_budget_usd_month=30,
        model="worker",
    ),
    Experiment(
        id="automation-templates",
        rank=7,
        name="Automation template store with a link-free comment-to-DM funnel",
        one_liner="Sell ready-to-import n8n workflow packs and SOPs for trades, distributed by short videos and keyword DMs.",
        thesis=(
            "Experiments 1-2 produce tested workflows anyway; packaging them as $29-99 templates earns from the DIY "
            "segment. Keyword comment-to-DM funnels turn short videos into leads without outbound links, which "
            "platforms suppress."
        ),
        customer="DIY owners, freelancers and new automation agencies serving the same trades.",
        offer="Workflow pack (JSON + setup video + SOP) per use case; free lead magnet via DM; bundle upsell.",
        pricing="$29-99 per pack, $149 bundle.",
        evidence=(
            "Brief: digital guides have ~100% margins; link-free keyword funnels avoid reach penalties.",
            "Verified Sep 2026: Instagram private replies allow one automated DM per comment within 7 days.",
        ),
        risks=(
            "Templates are easy to copy; the edge is niche specificity and support.",
            "Instagram automation limits; stay inside Meta's messaging policy.",
        ),
        compliance=(
            "Meta messaging rules: one private reply per comment, 24-hour window after the user replies.",
            "No income claims; refund policy on every product page.",
        ),
        agent_does=(
            "Package workflows from experiments 1-2; write product pages, lead magnets and 30 short video scripts.",
        ),
        human_does=("Record/approve videos; set up Gumroad/Lemon Squeezy and ManyChat; approve publishing.",),
        costs=(
            CostItem("Storefront (Gumroad; no monthly fee)", 0, 0, "10% + $0.50 per direct sale + card processing"),
            CostItem(
                "ManyChat Pro for keyword DMs", 0, 15, required=False, note="once an Instagram account posts regularly"
            ),
        ),
        phases=(
            Phase(
                "Products",
                21,
                "3 packs + 1 lead magnet live.",
                ("Pick 3 use cases with proven demand; write each pack's docs and product page.",),
            ),
            Phase(
                "Distribution",
                60,
                "30 videos with keyword CTAs; funnel converting.",
                ("Write video scripts with a comment keyword CTA; write DM sequences; weekly performance review.",),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(30, "products_live", ">=", 3, verified=False),
            Gate(60, "sales_count", ">=", 10),
            Gate(90, "revenue_usd_month", ">=", 300, hard=False),
        ),
        kpis=("products_live", "videos_published", "dm_leads", "sales_count", "revenue_usd_month", "refund_rate_pct"),
        api_budget_usd_month=20,
        model="worker",
    ),
    Experiment(
        id="ai-ops-newsletter",
        rank=8,
        name="Hands-on 'AI that actually works' newsletter for trade operators",
        one_liner="A weekly, tested, no-hype newsletter that builds the audience the service experiments sell to, monetised by disclosed affiliates.",
        thesis=(
            "The brief's own conclusion: the most reliable earners sell education and affiliate software to people "
            "trying AI. Doing that honestly, with real build notes from experiments 1-7, builds trust and a "
            "pipeline for the audit."
        ),
        customer="Owners and office managers of small service businesses.",
        offer="Free weekly issue: one tested automation, one tool review, one number. Paid tier later.",
        pricing="Affiliates (GoHighLevel 40% recurring, Make 35% for 12 months, n8n 30% for 12 months, no paid ads) + audit leads.",
        evidence=(
            "Brief: educational creators monetise through affiliates and communities.",
            "Verified Sep 2026: Beehiiv free to 2,500 subscribers; Kit free to 10,000.",
        ),
        risks=("Slow audience growth; combine SEO posts, LinkedIn and cross-promotions.",),
        compliance=(
            "FTC affiliate disclosure in every issue; honest reviews, including negatives.",
            "CAN-SPAM: confirmed opt-in, unsubscribe link, physical address.",
        ),
        agent_does=("Research and draft every issue from experiment learnings; write SEO posts and LinkedIn drafts.",),
        human_does=("Review and send issues; share on personal channels; approve affiliate sign-ups.",),
        costs=(CostItem("Newsletter platform (Beehiiv Launch / Kit free tier)", 0, 0),),
        phases=(
            Phase("Launch", 14, "Publication set up, 4 issues banked.", ("Positioning, welcome email, 4 issues.",)),
            Phase(
                "Grow",
                90,
                "300+ subscribers, first affiliate revenue.",
                ("Weekly issue + 2 LinkedIn drafts + 1 SEO post; track sources of subscribers.",),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(30, "subscribers", ">=", 100),
            Gate(75, "subscribers", ">=", 300),
            Gate(120, "revenue_usd_month", ">=", 100, hard=False),
        ),
        kpis=("issues_sent", "subscribers", "open_rate_pct", "click_rate_pct", "audit_leads", "revenue_usd_month"),
        api_budget_usd_month=20,
        model="worker",
        feeds=("ai-ops-audit",),
    ),
    Experiment(
        id="faceless-edu-channel",
        rank=9,
        name="Human-edited educational YouTube channel on small-business automation",
        one_liner="Shorts and walkthroughs built from real experiment builds, with a human editor on every video.",
        thesis=(
            "Pure AI slop gets demonetised under YouTube's inauthentic-content policy. Real screen recordings of "
            "working builds plus AI-drafted scripts pass the originality bar and feed the newsletter, templates "
            "and audit."
        ),
        customer="Same audience as the newsletter.",
        offer="Two Shorts a week + one walkthrough every two weeks.",
        pricing="Funnel value (newsletter signups, template sales) first; ad revenue only after YPP.",
        evidence=(
            "Verified Sep 2026: YPP needs 1,000 subs + 4,000 watch hours (or 10M Shorts views in 90 days); from 1 Feb 2027 new applicants need 8,000 hours / 20M views.",
            "July 2025: YouTube renamed 'repetitious' to 'inauthentic content'. Mass-produced templated AI videos can't be monetised.",
        ),
        risks=("Ad revenue is unlikely within 6 months; judge on funnel conversions.",),
        compliance=(
            "Every video has human review and original footage; label realistic synthetic media per YouTube rules.",
            "No 'get rich' framing; affiliate disclosures in descriptions.",
        ),
        agent_does=("Plan topics from search data; write scripts, titles, descriptions and shot lists.",),
        human_does=("Record screen and voice (or approve AI voice), edit, publish; report channel stats.",),
        costs=(
            CostItem("ElevenLabs Creator (only if not using own voice)", 0, 22, required=False, note="$11 first month"),
        ),
        phases=(
            Phase(
                "Pilot content",
                30,
                "12 videos published.",
                ("Script 12 videos from experiment builds.",),
                cadence="weekly",
            ),
            Phase(
                "Double down",
                60,
                "Formats that convert viewers to subscribers and leads.",
                ("Analyse retention/CTR the human reports; iterate formats.",),
                cadence="weekly",
            ),
        ),
        gates=(
            Gate(30, "videos_published", ">=", 8),
            Gate(60, "subscribers", ">=", 250),
            Gate(90, "funnel_leads", ">=", 50, hard=False),
        ),
        kpis=("videos_published", "subscribers", "views_28d", "avg_view_duration_s", "funnel_leads"),
        api_budget_usd_month=20,
        model="worker",
        feeds=("ai-ops-newsletter", "automation-templates"),
    ),
    Experiment(
        id="kdp-activity-books",
        rank=10,
        name="Niche activity and puzzle books on Amazon KDP",
        one_liner="Code-generated, human-proofed puzzle and activity books for narrow hobby niches.",
        thesis=(
            "A cheap test of long-tail marketplace demand: publishing is free, puzzles can be generated "
            "deterministically by code (not low-quality AI filler), and niches with specific interests are underserved."
        ),
        customer="Amazon shoppers buying gifts or hobby books (large-print word search for a hobby, trade-themed logic puzzles).",
        offer="100-page paperback activity books at $9.99-12.99.",
        pricing="60% royalty minus print cost at >= $9.99 (50% below $9.99).",
        evidence=(
            "Verified Sep 2026: KDP free to publish; 3 new titles/day limit; AI-generated content must be disclosed.",
        ),
        risks=("Saturated; low per-unit profit (~$2-4/book).", "Amazon quality enforcement against low-content spam."),
        compliance=(
            "Disclose AI-generated content on KDP; no trademarked names or characters; original puzzles only.",
        ),
        agent_does=("Niche research; write puzzle-generator code and interior layout; write listings and keywords.",),
        human_does=("Create the KDP account; review proofs; upload and publish; report sales.",),
        costs=(
            CostItem("Printed proof copies", 15, 0, "~$5-8 each with shipping"),
            CostItem("Amazon Ads test", 0, 150, required=False),
        ),
        phases=(
            Phase(
                "First 3 titles",
                30,
                "3 titles live.",
                ("Research niches; generate interiors; write listings.",),
                cadence="weekly",
            ),
            Phase(
                "Series", 90, "Expand winning niche into a series.", ("Analyse sales; build series.",), cadence="weekly"
            ),
        ),
        gates=(
            Gate(30, "titles_live", ">=", 3),
            Gate(60, "units_sold", ">=", 20),
            Gate(120, "royalties_usd_month", ">=", 100, hard=False),
        ),
        kpis=("titles_live", "units_sold", "royalties_usd_month", "acos_pct"),
        api_budget_usd_month=15,
        model="worker",
    ),
)

EXPERIMENTS: tuple[Experiment, ...] = tuple(replace(e, marketing=MARKETING[e.id]) for e in _EXPERIMENTS)
BY_ID: dict[str, Experiment] = {e.id: e for e in EXPERIMENTS}


def get(experiment_id: str) -> Experiment:
    try:
        return BY_ID[experiment_id]
    except KeyError:
        raise KeyError(f"unknown experiment {experiment_id!r}; choose from {', '.join(BY_ID)}") from None
