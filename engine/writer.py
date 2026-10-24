"""Offline template writer for T3 Ops Copilot.

Turns a fact sheet (CONTRACT.md section 6) into the organizer's 17-field output plus three
audience drafts. No network, no third-party packages. The writer only uses text and numbers
that already exist in the fact sheet; it never invents a fact.

The "bad" mode exists so the checker demo has a fabricated number to block.
"""

from __future__ import annotations

import re
from datetime import datetime

SIM_LABEL = "\u6a21\u62df / SIMULATED"

FIELDS = [
    ("f01", "Event ID", "\u4e8b\u4ef6\u7f16\u53f7"),
    ("f02", "Generated At", "\u751f\u6210\u65f6\u95f4"),
    ("f03", "Risk Level", "\u98ce\u9669\u7b49\u7ea7"),
    ("f04", "Airport & Time Window", "\u9002\u7528\u673a\u573a\u4e0e\u65f6\u95f4"),
    ("f05", "Evidence", "\u5224\u65ad\u4f9d\u636e"),
    ("f06", "Possible Impact", "\u53ef\u80fd\u5f71\u54cd"),
    ("f07", "Assumptions to Verify", "\u5f85\u6838\u67e5\u5047\u8bbe"),
    ("f08", "Information Gaps", "\u4fe1\u606f\u7f3a\u53e3"),
    ("f09", "First Action", "\u7b2c\u4e00\u6b65\u884c\u52a8"),
    ("f10", "Follow-up Actions", "\u540e\u7eed\u884c\u52a8"),
    ("f11", "Escalation Conditions", "\u5347\u7ea7\u6761\u4ef6"),
    ("f12", "Decisions Requiring a Human", "\u5fc5\u987b\u4eba\u5de5\u51b3\u5b9a\u4e8b\u9879"),
    ("f13", "Internal Ops Note", "\u5185\u90e8\u8fd0\u8425\u63d0\u793a"),
    ("f14", "Airport Coordination Message", "\u673a\u573a\u534f\u8c03\u4fe1\u606f"),
    ("f15", "Passenger Message Draft", "\u65c5\u5ba2\u4fe1\u606f\u8349\u6848"),
    ("f16", "Cited Sources", "\u5f15\u7528\u6765\u6e90"),
    ("f17", "Output Status", "\u8f93\u51fa\u72b6\u6001"),
]

RISK_DISPLAY = {
    "low": ("Low", "\u4f4e"),
    "medium": ("Medium", "\u4e2d"),
    "high": ("High", "\u9ad8"),
    "cant_tell": ("Can't tell", "\u65e0\u6cd5\u5224\u65ad"),
    "can't tell": ("Can't tell", "\u65e0\u6cd5\u5224\u65ad"),
    "cannot tell": ("Can't tell", "\u65e0\u6cd5\u5224\u65ad"),
    "\u65e0\u6cd5\u5224\u65ad": ("Can't tell", "\u65e0\u6cd5\u5224\u65ad"),
    "\u4f4e": ("Low", "\u4f4e"),
    "\u4e2d": ("Medium", "\u4e2d"),
    "\u9ad8": ("High", "\u9ad8"),
}

# "weather caused" must never appear, even inside a sentence that denies causation.
_BAD_PHRASES = (
    (re.compile(r"weather\s+caused", re.I), "the monthly data shows only an association with weather, not a cause"),
    (re.compile(r"caused\s+by\s+weather", re.I), "associated with weather, not a proven cause"),
)


def _sanitize(text: str) -> str:
    value = str(text)
    for pattern, replacement in _BAD_PHRASES:
        value = pattern.sub(replacement, value)
    return value


def _risk_text(risk: dict) -> str:
    raw = str((risk or {}).get("level", "medium")).strip()
    en, _zh = RISK_DISPLAY.get(raw, RISK_DISPLAY.get(raw.lower(), ("Medium", "\u4e2d")))
    return en


def _warn_format(text: str) -> str:
    return " ".join(str(text).split())


def _facts_line(fact: dict) -> str:
    return f"[FACT: {fact.get('source', 'EVENT')}] {fact.get('text', '')}".strip()


def _first_action(facts: dict, event: dict) -> str:
    if facts.get("first_action"):
        return str(facts["first_action"])
    narrative = facts.get("narrative") or {}
    if narrative.get("first_action"):
        return narrative["first_action"]
    if facts.get("conflict"):
        return ("Confirm which source has been reviewed and whether both use the same statistical definition "
                "before using either figure.")
    for fb in facts.get("feedback_matches") or []:
        if str(fb.get("result", "")).lower() == "reject":
            return "Confirm current on-site resources with the operations team before considering escalation."
    detector = facts.get("detector") or {}
    verdict = detector.get("verdict", "normal")
    if verdict in ("unusual", "clearly unusual"):
        return ("Ask the airport coordination team to confirm the latest ground-support capacity and the "
                "weather update time.")
    if detector.get("signal_count", 0) >= 1:
        return "Ask operations to confirm preceding-aircraft positions, gate availability and ground-support loading."
    return "Verify the data source and its update time before acting."


def _follow_up(facts: dict, event: dict) -> list[str]:
    narrative = facts.get("narrative") or {}
    items = list(narrative.get("follow_up") or [])
    if not items:
        if facts.get("conflict"):
            items = ["Compare the two sources' update times and definitions.",
                     "Do not combine the two figures in the advice.",
                     "Escalate to the Operations Lead if the conflict cannot be resolved."]
        else:
            items = ["Check the latest formal flight status before any external message.",
                     "Record the decision and the reason in the feedback log.",
                     "Review the information gaps with the responsible professional."]
    for fb in facts.get("feedback_matches") or []:
        items.append(
            f"Prior staff feedback record ({fb.get('event_id')}, {fb.get('rec_id')}): {fb.get('result')} - "
            f"{fb.get('reason') or 'no reason recorded'}; apply it to the first action."
        )
    return items


def _messages(facts: dict, event: dict) -> dict:
    narrative = facts.get("narrative") or {}
    airport_en = event.get("airport_en") or (facts.get("detector") or {}).get("airport_en") or "the airport"
    risk = _risk_text(facts.get("risk") or {})
    first = _first_action(facts, event)
    ops = narrative.get("ops_note") or (
        f"{SIM_LABEL} - Internal operations note: {airport_en} faces a changing operating situation. "
        f"Risk level: {risk}. First check: {first} No formal flight status has been confirmed. "
        "This note is decision support for a human reviewer."
    )
    airport = narrative.get("airport_note") or (
        f"{SIM_LABEL} - Airport coordination request: please confirm the latest weather update time, "
        f"ground-support capacity and the peak workload window for {airport_en}. "
        "This is a coordination draft only; no operational action has been taken."
    )
    passengers = narrative.get("passenger_note") or (
        f"{SIM_LABEL} - Draft passenger message (not an official notification): {airport_en} may experience "
        "possible delays over the next few hours. Flight status has not been confirmed. Please check official "
        "airline and airport channels for updates."
    )
    if passengers.strip() == airport.strip():
        passengers = passengers + " Passengers: please check official channels before travelling."
    return {"ops": _sanitize(ops), "airport": _sanitize(airport), "passengers": _sanitize(passengers)}


def _tagged(items, tag: str) -> str:
    return "\n".join(f"[{tag}] {_warn_format(x)}" for x in (items or []) if str(x).strip())


def write(facts: dict, event: dict | None = None, mode: str = "offline") -> dict:
    """Build the 17-field output from a fact sheet.

    mode: "offline" (default) or "bad" (injects one fabricated number for the checker demo).
    """
    facts = facts or {}
    event = event or {}
    detector = facts.get("detector") or {}
    risk = facts.get("risk") or {}
    narrative = facts.get("narrative") or {}

    event_id = event.get("id") or facts.get("event_id") or "EVENT"
    airport_en = event.get("airport_en") or detector.get("airport_en") or event.get("airport") or "the airport"
    time_en = event.get("time_en") or event.get("time_text") or "the event window"

    fact_lines = [_facts_line(f) for f in (facts.get("facts") or [])][:6]
    reason_lines = []
    for reason in (risk.get("reasons") or [])[:3]:
        if isinstance(reason, dict):
            reason_lines.append(f"[FACT: {reason.get('source', 'DETECTOR')}] {reason.get('text', '')}")
        else:
            reason_lines.append(f"[FACT: DETECTOR] {reason}")
    evidence = fact_lines + reason_lines
    evidence_text = "\n".join(evidence) if evidence else "[UNKNOWN] No facts available."

    impact = narrative.get("impact") or (
        "Ground support and downstream rotations may come under pressure, but the data does not prove the cause "
        "of any individual delay."
    )
    impact_text = f"{impact} [ASSUMPTION] Impact is a risk statement, not a confirmed operational status."

    assumptions = _tagged(facts.get("assumptions"), "ASSUMPTION") or "[ASSUMPTION] None recorded."
    gaps_items = list(facts.get("unknowns") or []) + list(facts.get("missing_data") or [])
    gaps = _tagged(gaps_items, "UNKNOWN") or "[UNKNOWN] No information gaps recorded."
    first = _first_action(facts, event)
    follow = "\n".join(f"{i + 1}) {_warn_format(x)}" for i, x in enumerate(_follow_up(facts, event)))
    escalation = narrative.get("escalation") or (
        "If a formal operating irregularity is confirmed, escalate to the Operations Lead. "
        "Do not take operational action without human approval."
    )
    human = narrative.get("human_decisions") or (
        "Cancellation, release, dispatch, maintenance and compensation decisions, and the formal passenger "
        "notification, require the responsible qualified professional (RULE007)."
    )
    messages = _messages(facts, event)

    sources = list(facts.get("sources") or [])
    sources_text = "; ".join(sources) if sources else "SIM-BASE"

    values = {
        "f01": event_id,
        "f02": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "f03": _risk_text(risk),
        "f04": f"{airport_en} - {time_en}",
        "f05": evidence_text,
        "f06": impact_text,
        "f07": assumptions,
        "f08": gaps,
        "f09": first,
        "f10": follow,
        "f11": escalation,
        "f12": f"[HUMAN] {human}",
        "f13": messages["ops"],
        "f14": messages["airport"],
        "f15": messages["passengers"],
        "f16": sources_text,
        "f17": f"Pending human review \u5f85\u590d\u6838 - {SIM_LABEL}",
    }

    if mode == "bad":
        # Deliberately fabricated number, used only by the checker demo.
        values["f05"] = values["f05"] + "\n[FACT: SIM-BASE] The drop is 20 points below normal."

    values = {key: _sanitize(value) for key, value in values.items()}
    fields = [{"key": key, "label_en": en, "label_zh": zh, "value": values[key]} for key, en, zh in FIELDS]

    return {
        "event_id": event_id,
        "generated_at": values["f02"],
        "mode": mode if mode in ("offline", "bad") else "offline",
        "fields": fields,
        "sources": sources,
        "status": values["f17"],
        "messages": messages,
        "risk_level": _risk_text(risk),
    }
