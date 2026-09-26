"""Go-to-market plans per experiment. Organic first; every paid line is an optional
test that unlocks only after organic results prove the funnel converts.
Ad-cost figures are planning estimates, not quotes."""

from __future__ import annotations

from venture_lab.experiments.base import CostItem, Marketing

MARKETING: dict[str, Marketing] = {
    "voice-receptionist": Marketing(
        positioning="'Never miss an emergency call again': the AI receptionist built only for <trade> companies in <metro>.",
        channels=(
            "Personalised cold email from your own mailbox (max 20/day) to owners found in public Google Maps listings, each with a specific observation (hours, reviews mentioning unanswered calls).",
            "After-hours 'missed-call audit': the human calls the prospect's line after hours (no recording) and sends a short written note of what happened, plus the demo line number.",
            "Live demo phone number on the landing page and in every email: the product sells itself on a call.",
            "Trade partnerships: supply houses/distributors, trade associations and local business groups (talks, co-branded offers).",
            "Owner communities (trade Facebook groups, subreddits): useful posts about missed-call economics, no pitching.",
            "Referral loop: one free month for the referrer and the new client.",
        ),
        seo=(
            "One landing page per vertical x city ('AI answering service for HVAC companies in Denver'): low volume, high intent, easy to rank.",
            "Comparison and cost pages: 'AI receptionist vs answering service cost', 'best answering service for plumbers'.",
            "Google Business Profile for the agency plus client-approved case-study pages with real numbers.",
            "Free 'missed call revenue calculator' as a linkable asset (built in micro-tools-seo).",
        ),
        paid=(
            CostItem(
                "Google Search ads on 'answering service for <trade>' (test)",
                0,
                450,
                required=False,
                note="$300-600/mo estimate; only after 2 closed deals give a real close rate",
            ),
            CostItem(
                "Local chamber / trade association membership", 0, 40, required=False, note="~$300-600/yr estimate"
            ),
        ),
        funding="Not needed to start. Outreach and SEO are $0 beyond the foundation. Paid search (~$300-600/mo) is optional after the first 2 deals.",
    ),
    "speed-to-lead": Marketing(
        positioning="'Every lead answered in 60 seconds': stop paying for leads you never call back.",
        channels=(
            "Target businesses visibly paying for leads: public Google Ads Transparency Center and Meta Ad Library listings show who runs ads.",
            "Free 'lead response audit': the human submits the prospect's web form and times the reply; the agent writes the report and email.",
            "Cross-sell to every experiment-1 prospect who isn't ready for voice AI (cheaper first step).",
            "Partnerships with local marketing agencies that generate leads but can't follow them up (revenue share from revenue).",
        ),
        seo=(
            "'Missed call text back for <trade>' and 'speed to lead <trade>' pages.",
            "Free 'lead leakage calculator' (leads x response delay x close rate x job value) as a lead magnet.",
        ),
        paid=(
            CostItem(
                "Meta retargeting of calculator users (test)",
                0,
                150,
                required=False,
                note="estimate; only after the calculator gets 500+ visits/mo",
            ),
        ),
        funding="Not needed. Audits and calculators are organic. Retargeting (~$150/mo) is optional later.",
    ),
    "ai-ops-audit": Marketing(
        positioning="'Know exactly where AI pays off in your business in 5 days': a fixed price and a plan you keep.",
        channels=(
            "Audit call-to-action in every newsletter issue and YouTube description (experiments 8-9).",
            "Founder-led LinkedIn: agent drafts 3 posts/week from real experiment builds; the human edits and posts.",
            "Free 60-minute 'AI for your business' workshops with chambers, SBDCs and libraries; audit offer at the end.",
            "Referral partners (bookkeepers, IT managed-service providers) at 10-20% of the audit fee, paid only from revenue.",
            "Warm network outreach: past colleagues and clients.",
        ),
        seo=(
            "Public sample audit report as a gated lead magnet.",
            "'AI readiness checklist for <trade>' and 'how much does AI automation cost for a small business' guides.",
        ),
        paid=(
            CostItem("LinkedIn post boosts for the workshop announcements", 0, 100, required=False, note="estimate"),
        ),
        funding="Not needed. Referral fees come out of revenue. Boosts (~$100/mo) are optional.",
    ),
    "support-deflection": Marketing(
        positioning="'Resolve 30-50% of your support tickets automatically without risking a wrong answer': draft mode first, auto only after it proves accuracy.",
        channels=(
            "Cold email to Shopify stores with public support-pain signals (large FAQ/help centres, public reviews citing slow replies).",
            "DTC operator communities (Slack/Discord groups, Shopify community forums): share deflection benchmarks, not pitches.",
            "Case studies with before/after reply time and cost per ticket.",
            "Later: Shopify App Store listing ($19 one-time) with App Store search optimisation (title, keywords, screenshots, reviews).",
        ),
        seo=(
            "'Shopify returns/order-status automation' how-tos with free prompt snippets.",
            "Honest comparison pages against native helpdesk AI add-ons, plus a 'support cost per ticket' calculator.",
        ),
        paid=(
            CostItem(
                "Shopify App Store search ads (only once listed and reviewed)", 0, 300, required=False, note="estimate"
            ),
        ),
        funding="Not needed for the first clients. App Store ads (~$300/mo) only after the app has reviews.",
    ),
    "doc-extraction": Marketing(
        positioning="'Your stack of <documents> as a clean spreadsheet by tomorrow, accuracy checked': priced per document.",
        channels=(
            "Cold email to the niche from public directories and registries (e.g. FMCSA broker data for freight; association directories for property managers).",
            "Free 25-document trial: the product proves itself on the prospect's own files.",
            "Helpful answers in niche forums/subreddits where self-promotion rules allow, linking the free single-document tool.",
            "Partnerships with niche software consultants and bookkeeping firms (white-label, revenue share).",
        ),
        seo=(
            "Service pages for exact-match intent: 'lease abstraction service', 'rate confirmation to Excel', 'invoice data entry service'.",
            "Free single-document extractor (rate-limited, capped cost) as a lead magnet; shares the micro-tools-seo stack.",
        ),
        paid=(
            CostItem(
                "Google Search ads on exact-match service keywords (test)",
                0,
                300,
                required=False,
                note="$200-400/mo estimate; B2B high intent; after 1 paid pilot",
            ),
        ),
        funding="Not needed. Search ads (~$200-400/mo) are optional after a paid pilot.",
    ),
    "micro-tools-seo": Marketing(
        positioning="The fastest free <niche> calculators on the web: no sign-up, works on a phone on the job site.",
        channels=(
            "Organic search is the product's main channel (see SEO plan).",
            "Embeddable widgets with a credit link: each embed on a trade blog or supplier site is a backlink.",
            "Launch listings in free tool directories and Product Hunt; answer forum questions with the tool where allowed.",
            "Cross-links from the newsletter, YouTube descriptions and the other experiments' sites.",
        ),
        seo=(
            "Keyword research from Search Console, autocomplete and 'People also ask'; one tool per search intent, no thin variants.",
            "Static pages that load fast; SoftwareApplication/FAQ schema; unique explanatory copy and worked examples on every page.",
            "Hub-and-spoke internal linking per trade; XML sitemap in Search Console; monthly prune-or-improve pass from Search Console data.",
            "Link building through embeds and resource-page outreach (outreach goes through approval).",
        ),
        paid=(
            CostItem(
                "Entry-level SEO research tool", 0, 50, required=False, note="optional; free tools suffice at first"
            ),
        ),
        funding="Not needed. SEO is time, not money. A keyword tool (~$50/mo) is optional.",
    ),
    "automation-templates": Marketing(
        positioning="'Copy-paste automations for <trade> businesses, tested on real clients.'",
        channels=(
            "Short videos (Reels, Shorts, TikTok) that end with 'comment WORKFLOW'; the keyword triggers a DM with the free lead magnet, then the paid pack (link-free funnel).",
            "Free mini-templates in community galleries and forums that point to the full paid pack (where the rules allow).",
            "Newsletter and YouTube cross-promotion; bundle offers to audit clients.",
            "Affiliate program for other creators (30% commission, paid from revenue).",
            "Gumroad Discover marketplace (30% fee on those sales).",
        ),
        seo=(
            "Product pages targeting '<tool> <use case> template' (e.g. 'n8n missed call text back template').",
            "Blog posts giving a free simplified version, with the full pack as the upgrade.",
        ),
        paid=(
            CostItem(
                "ManyChat Pro for keyword DMs", 0, 15, required=False, note="needed once Instagram posting starts"
            ),
            CostItem(
                "Meta ads promoting the free lead magnet (test)",
                0,
                225,
                required=False,
                note="$5-10/day estimate; only after organic DM-to-sale conversion is measured",
            ),
        ),
        funding="Mostly organic. ~$15/mo for DM automation once videos start. The ad test (~$150-300/mo) is optional.",
    ),
    "ai-ops-newsletter": Marketing(
        positioning="'One tested AI automation for your service business every week. No hype, real numbers.'",
        channels=(
            "SEO-indexed issue archive plus 1 long-form post a week.",
            "LinkedIn and X drafts from each issue (human posts).",
            "Newsletter recommendations/cross-promotions with adjacent small-business newsletters (free swaps).",
            "Lead magnets from experiments 6-7 (calculators, templates) gated by subscription.",
            "YouTube descriptions and workshop sign-ups (experiments 3 and 9).",
        ),
        seo=(
            "Evergreen guides per trade ('AI tools for HVAC companies 2026') updated quarterly.",
            "Honest tool reviews and comparisons with disclosed affiliate links.",
        ),
        paid=(
            CostItem(
                "Paid subscriber acquisition (e.g. Beehiiv Boosts) test",
                0,
                200,
                required=False,
                note="~$1-3 per subscriber estimate; only once revenue per subscriber is known",
            ),
        ),
        funding="Not needed. Paid subscriber growth (~$100-300/mo) is optional once each subscriber's value is known.",
    ),
    "faceless-edu-channel": Marketing(
        positioning="'Watch real AI automations get built for real small businesses.'",
        channels=(
            "YouTube search: how-to walkthroughs targeting specific problems.",
            "Shorts repurposed to TikTok, Instagram Reels and LinkedIn with a comment-keyword CTA (shared with experiment 7).",
            "Collaborations and guest spots with trade-focused creators and podcasts.",
            "Videos embedded in newsletter issues and SEO posts for extra watch time.",
        ),
        seo=(
            "Titles and descriptions from YouTube autocomplete research; chapters; pinned comment with a lead magnet.",
            "One pillar walkthrough per experiment build, linked from the matching tool/template page.",
        ),
        paid=(),
        funding="Not needed. Ads on videos aren't recommended at this stage; ElevenLabs (~$22/mo) only if the host doesn't use their own voice.",
    ),
    "kdp-activity-books": Marketing(
        positioning="Giftable, niche-specific activity books ('large-print word search for quilters').",
        channels=(
            "Amazon search: title/subtitle keywords, 7 backend keyword slots, the right 3 categories, A+ content.",
            "Series pages and author page to cross-sell titles.",
            "Pinterest pins for gift-driven niches; seasonal timing (Q4 gifting, Mother's/Father's Day).",
        ),
        seo=("Keyword research from Amazon autocomplete and bestseller lists in each niche; one niche per series.",),
        paid=(
            CostItem(
                "Amazon Ads auto-campaign test",
                0,
                150,
                required=False,
                note="~$5/day; optional, keep ACoS below royalty",
            ),
        ),
        funding="Not needed. Organic Amazon search works for niche titles. A ~$150/mo ads test is optional.",
    ),
}

PORTFOLIO_FLYWHEEL = (
    "Audience assets (newsletter, YouTube, free tools, templates) build trust at $0.",
    "Trust converts into $750 audits, and audits convert into implementation retainers (voice, speed-to-lead, support, extraction).",
    "Client builds become the next videos, issues, templates and case studies, so marketing content comes free from delivery.",
    "Rule: no paid acquisition until an organic channel shows a measured conversion rate; then test with capped budgets.",
)
