"""Builds a platform-neutral inbound voice receptionist spec (importable into
Vapi, Retell or GoHighLevel Voice AI by hand or via their APIs)."""

from __future__ import annotations

import json
import re
from typing import Any

from anthropic import beta_tool

REQUIRED_FIELDS = ("business_name", "vertical", "state", "timezone", "hours", "services", "transfer_number")

DEFAULT_EMERGENCY = {
    "hvac": ["no heat", "gas smell", "carbon monoxide", "co alarm", "smoke"],
    "plumbing": ["flooding", "burst pipe", "sewage", "no water", "gas smell"],
    "roofing": ["active leak", "tree on roof", "storm damage"],
    "electrical": ["sparks", "burning smell", "power line down", "shock"],
    "dental": ["severe pain", "swelling", "knocked out tooth", "bleeding"],
}

CALL_TOOLS = [
    {
        "name": "check_availability",
        "description": "Return open appointment slots for a service and date range.",
        "parameters": {"service": "string", "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD"},
    },
    {
        "name": "book_appointment",
        "description": "Book a slot once the caller confirms name, phone, address and time.",
        "parameters": {
            "slot_id": "string",
            "name": "string",
            "phone": "string",
            "address": "string",
            "notes": "string",
        },
    },
    {
        "name": "transfer_call",
        "description": "Warm-transfer to the on-call human for emergencies or on request.",
        "parameters": {"reason": "string"},
    },
    {
        "name": "log_lead",
        "description": "Write the call summary and qualification fields to the CRM.",
        "parameters": {
            "name": "string",
            "phone": "string",
            "service": "string",
            "urgency": "emergency|soon|flexible",
            "outcome": "booked|callback|transferred|not_a_fit",
            "summary": "string",
        },
    },
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "business"


def build_voice_spec(profile: dict[str, Any]) -> dict[str, Any]:
    missing = [f for f in REQUIRED_FIELDS if not profile.get(f)]
    if missing:
        raise ValueError(f"business profile is missing: {', '.join(missing)}")

    name = profile["business_name"]
    vertical = str(profile["vertical"]).lower()
    services = profile["services"]
    emergencies = profile.get("emergency_keywords") or DEFAULT_EMERGENCY.get(vertical, [])
    faqs = profile.get("faqs", [])
    booking = profile.get("booking_method", "calendar")

    first_message = (
        f"Thanks for calling {name}. I'm the office's AI assistant, and this call is recorded "
        "so we can serve you better. How can I help today?"
    )
    system_prompt = f"""You are the virtual receptionist for {name}, a {vertical} business in {profile["state"]}.
Office hours: {profile["hours"]} ({profile["timezone"]}). Services: {", ".join(services)}.
Service area: {profile.get("service_area", "ask the caller for their address and confirm we serve it")}.
Pricing policy: {profile.get("pricing_policy", "do not quote prices; offer a technician visit or a callback")}.

Goals, in order:
1. If the caller mentions any of these, or anything that sounds dangerous or urgent, call transfer_call
   immediately: {", ".join(emergencies) or "a safety emergency"}. If life is at risk, tell them to hang up and call 911 first.
2. Qualify: name, callback number, service needed, address, urgency, preferred time.
3. Book with check_availability then book_appointment ({booking}); read the booking back to confirm.
4. Always finish with log_lead, whatever the outcome.

Rules:
- If asked whether you are a person, say you are an AI assistant. Never claim to be human.
- Keep turns short (one or two sentences). Let the caller interrupt; stop talking when they do.
- Never diagnose, give safety instructions beyond calling emergency services, or promise prices,
  arrival times or outcomes you were not given.
- If you don't know, offer a callback from the team and log it.
- Do not collect payment card numbers, social security numbers or health details on the call."""

    return {
        "name": f"{name} receptionist",
        "slug": slugify(name),
        "first_message": first_message,
        "system_prompt": system_prompt,
        "knowledge_base": [{"q": f.get("q", ""), "a": f.get("a", "")} for f in faqs],
        "tools": CALL_TOOLS,
        "transfer": {"number": profile["transfer_number"], "triggers": emergencies + ["asks for a human"]},
        "after_hours": profile.get(
            "after_hours", "Same flow; emergencies transfer to on-call, everything else books or schedules a callback."
        ),
        "post_call": {
            "sms_confirmation": "Only if the caller agreed on the call to receive a text confirmation.",
            "crm_fields": ["name", "phone", "service", "urgency", "outcome", "summary", "recording_url"],
        },
        "compliance": {
            "ai_disclosure": "Stated in the greeting and whenever asked.",
            "recording_notice": "Stated in the greeting; required in all-party-consent states and good practice everywhere.",
            "outbound": "Inbound only. Outbound AI calls or texts need prior express written consent (TCPA).",
            "sms": "Business SMS in the US requires A2P 10DLC brand and campaign registration.",
            "data": "Store transcripts in the client's CRM; set a retention period in the service agreement.",
        },
        "platform_notes": {
            "vapi": "Create an assistant with firstMessage + model.messages[system]; map tools to server URL functions; add transferCall destination.",
            "retell": "Create a Retell LLM with general_prompt + begin_message; map tools to custom functions; add transfer_call tool.",
            "gohighlevel": "Voice AI agent: paste prompt into agent goals/instructions, set the greeting, enable calendar booking and call transfer actions.",
        },
    }


def voice_spec_tool(workspace: Any) -> Any:
    @beta_tool
    def build_voice_agent_spec(business_profile_json: str) -> str:
        """Generate an inbound AI receptionist spec (greeting, system prompt, call tools,
        transfer rules, compliance notes, platform import notes) for one business and
        save it under voice/<slug>/. Use it for demos and client builds.

        Args:
            business_profile_json: JSON with business_name, vertical, state, timezone, hours,
                services (list), transfer_number, and optional service_area, pricing_policy,
                booking_method, emergency_keywords (list), faqs (list of {q, a}), after_hours.
        """
        try:
            spec = build_voice_spec(json.loads(business_profile_json))
        except (ValueError, TypeError) as exc:
            return f"Error: {exc}"
        path = workspace.resolve(f"voice/{spec['slug']}/spec.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        (path.parent / "system_prompt.md").write_text(spec["system_prompt"], encoding="utf-8")
        return f"Saved voice/{spec['slug']}/spec.json and system_prompt.md."

    return build_voice_agent_spec
