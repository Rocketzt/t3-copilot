"""Offline template writer for T3 Ops Copilot.

Turns a fact sheet (CONTRACT.md section 6) into the organizer's 17-field output plus three
audience drafts. No network, no third-party packages. The writer only uses text and numbers
that already exist in the fact sheet; it never invents a fact.

The "bad" mode exists so the checker demo has a fabricated number to block.
"""

from __future__ import annotations

from datetime import datetime

SIM_LABEL = "模拟 / SIMULATED"

FIELDS = [
    ("f01", "Event ID", "事件编号"),
    ("f02", "Generated At", "生成时间"),
    ("f03", "Risk Level", "风险等级"),
    ("f04", "Airport & Time Window", "适用机场与时间"),
    ("f05", "Evidence", "判断依据"),
    ("f06", "Possible Impact", "可能影响"),
    ("f07", "Assumptions to Verify", "待核查假设"),
    ("f08", "Information Gaps", "信息缺口"),
    ("f09", "First Action", "第一步行动"),
    ("f10", "Follow-up Actions", "后续行动"),
    ("f11", "Escalation Conditions", "升级条件"),
    ("f12", "Decisions Requiring a Human", "必须人工决定事项"),
    ("f13", "Internal Ops Note", "内部运营提示"),
    ("f14", "Airport Coordination Message", "机场协调信息"),
    ("f15", "Passenger Message Draft", "旅客信息草案"),
    ("f16", "Cited Sources", "引用来源"),
    ("f17", "Output Status", "输出状态"),
]

RISK_DISPLAY = {
    "low": ("Low", "低"),
    "medium": ("Medium", "中"),
    "high": ("High", "高"),
    "cant_tell": ("Can't tell", "无法判断"),
}


def _risk_text(risk: dict) -> str:
    level = (risk or {}).get("level", "medium")
    en, zh = RISK_DISPLAY.get(level, ("Medium", "中"))
    return f"{en} ({zh})"


def _warn_format(text: str) -> str:
    return " ".join(str(text).split())


def _facts_line(fact: dict) -> str:
    return f"[FACT: {fact.get('source', 'EVENT')}] {fact.get('text', '')}".strip()


def _first_action(facts: dict, event: dict) -> str:
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
            f"Previous staff decision ({fb.get('event_id')}, {fb.get('rec_id')}): {fb.get('result')} - "
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
    # keep the three audiences textually distinct even if a fixture supplies similar text
    if passengers.strip() == airport.strip():
        passengers = passengers + " Passengers: please check official channels before travelling."
    return {"ops": ops, "airport": airport, "passengers": passengers}


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

    evidence = [_facts_line(f) for f in (facts.get("facts") or [])][:6]
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
        "f17": f"Pending human review 待复核 - {SIM_LABEL}",
    }

    if mode == "bad":
        # Deliberately fabricated number, used only by the checker demo.
        values["f05"] = values["f05"] + "\n[FACT: SIM-BASE] The drop is 20 points below normal."

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
