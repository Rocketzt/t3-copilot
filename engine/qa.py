"""Bounded question answering for the Assistant page (offline, deterministic).

The panel is not an open chatbot: a small intent router answers questions that the fact sheet can
support, and returns a bounded "what we can say" answer otherwise. Every answer ends with the
simulated label and cites the sources it used.
"""

from __future__ import annotations

import re

SIM = "模拟 / SIMULATED"
PII_PATTERNS = [
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"),
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
]

DELAY = ["definitely", "certain", "sure", "will it be delayed", "is it delayed", "一定", "肯定", "延误"]
WHY = ["why", "why risk", "reason", "basis", "为什么", "依据", "凭什么"]
CONFLICT = ["which source", "two sources", "disagree", "conflict", "哪个来源", "冲突", "不一致"]
CAUSALITY = ["cause", "caused", "because of weather", "did weather", "导致", "因果", "因为天气"]
CANCEL = ["cancel", "cancel flights", "automatically", "取消", "自动"]
SEND = ["send", "publish", "notify passengers now", "发送", "发布", "直接通知"]
PYI = ["passenger name", "phone", "mobile", "身份证", "手机号", "姓名"]
REAL = ["real airport", "is this real", "actually real", "真实的", "真的机场"]
REJECT = ["reject", "overrule", "refuse", "拒绝", "否决"]
MISSING = ["aircraft position", "which flights", "flight by flight", "前序飞机", "飞机位置", "具体航班"]
DOWNGRADE = ["resources sufficient", "capacity sufficient", "wind within limits", "ground resources", "资源充足", "保障能力", "风速"]
TIME = ["which period", "which month", "time range", "what data", "时段", "哪个月", "数据范围"]
STOP = ["source reliability", "cannot be determined", "can't tell", "unknown source", "可靠性", "无法判断"]
TWO_MSG = ["two messages", "operations and passengers", "separate messages", "分别写", "运营人员和旅客"]
NEW_AIRPORT = ["new airport", "linjiang", "unseen", "临江", "新机场"]


def _has(pattern_list, text: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in pattern_list)


def _pii(text: str) -> str | None:
    for pat in PII_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


def _num(facts: dict, key: str):
    comps = (facts.get("detector") or {}).get("comparisons") or []
    for c in comps:
        if c.get("key") == key:
            return c.get("value_pp")
    return None


def _detector_sentence(facts: dict) -> str:
    det = facts.get("detector") or {}
    airport = det.get("airport_en") or det.get("airport") or "the airport"
    month = det.get("month_label", "")
    verdict = det.get("verdict", "normal")
    comps = det.get("comparisons") or []
    parts = []
    for c in comps[:3]:
        val = c.get("value_pp")
        if val is None:
            continue
        parts.append(f"{c.get('label', c.get('key'))} {val:+.2f} pp")
    detail = "; ".join(parts) if parts else "no comparison values available"
    return (f"{airport} {month}: {detail} [FACT: SIM-BASE]. "
            f"Detector verdict: {verdict} ({det.get('signal_count', 0)} comparisons signal a >=5 pp drop) [FACT: DETECTOR].")


def _sources(facts: dict, *preferred: str) -> list[str]:
    available = list(facts.get("sources") or [])
    out = [s for s in preferred if s in available]
    for s in ("SIM-BASE", "SIM-WEATHER", "SIM-SCALE", "DETECTOR", "EVENT"):
        if s in available and s not in out:
            out.append(s)
    return out[:4] or available[:4]


def answer(question: str, facts: dict, output: dict | None = None) -> dict:
    """Return {text, sources, intent}. Deterministic, offline, fact-sheet grounded."""
    q = (question or "").strip()
    facts = facts or {}
    det = facts.get("detector") or {}
    risk = facts.get("risk") or {}
    risk_en = str(risk.get("level", "medium")).replace("cant_tell", "can't tell")
    airport = det.get("airport_en") or det.get("airport") or "the airport"
    narrative = facts.get("narrative") or {}
    first = narrative.get("first_action") or "Verify the data source and update time first."

    if len(q) > 500:
        return {"intent": "too_long", "sources": [],
                "text": "The question is too long. Please ask a short question about this event. " + SIM}

    if _pii(q):
        return {"intent": "pii", "sources": ["RULE011"],
                "text": ("I will not use or repeat personal data such as names, phone numbers or ID numbers. "
                         "Please remove or anonymise it before sharing the event; I can still work with aggregate "
                         "information. " + SIM)}

    if _has(CANCEL, q):
        return {"intent": "auto_action", "sources": ["RULE007"],
                "text": ("I cannot cancel, release, dispatch, maintain or compensate flights, and I cannot act "
                         "automatically. Those decisions belong to the responsible qualified professional "
                         "(Operations Lead). I can only list the information they need and the checks to run first. "
                         + SIM)}

    if _has(SEND, q):
        return {"intent": "send", "sources": ["RULE005"],
                "text": ("I cannot send or publish passenger messages. I can only produce a draft clearly marked "
                         "as a draft; a person must review it and the official channels must issue any real notice. "
                         + SIM)}

    if _has(REAL, q):
        return {"intent": "simulation", "sources": ["RULE010"],
                "text": ("No. All airports, events and numbers in this project are fictional simulations generated "
                         "by the organizers (DQ001). The scenario is designed to practise decision support, not a "
                         "real-world event. " + SIM)}

    if _has(CONFLICT, q):
        return {"intent": "conflict", "sources": ["RULE001", "RULE012"],
                "text": ("I cannot choose one source. The event reports two sources with different update times and "
                         "no verified single source; the risk level is Can't tell. First action: confirm which source "
                         "has been reviewed and whether both use the same statistical definition. " + SIM)}

    if _has(CAUSALITY, q):
        return {"intent": "causality", "sources": ["SIM-WEATHER", "SIM-BASE", "RULE003"],
                "text": ("The data can show an association, not a proven cause. The monthly weather record and the "
                         "monthly completion baseline are recorded at airport-month level; there is no per-flight "
                         "cause data. Do not state that the weather caused the operational disruption. " + SIM)}

    if _has(DELAY, q):
        return {"intent": "delay_certainty", "sources": _sources(facts, "SIM-BASE", "EVT001"),
                "text": ("No. A risk is not a confirmed delay, and no formal flight status was provided. "
                         + _detector_sentence(facts) + " First check: " + first + " " + SIM)}

    if _has(WHY, q):
        return {"intent": "why_risk", "sources": _sources(facts, "SIM-BASE", "SIM-WEATHER", "SIM-SCALE"),
                "text": ("The assessment uses three comparisons. " + _detector_sentence(facts) +
                         " It also uses the event's weather description and the airport's business importance. "
                         "Weather is background evidence, not a proven cause. " + SIM)}

    if _has(MISSING, q) or _has(["unknown", "gap", "无法知道", "不知道"], q):
        gaps = list(facts.get("unknowns") or [])[:3]
        gap_text = "; ".join(gaps) if gaps else "detailed flight-level information is not available"
        return {"intent": "missing_info", "sources": ["EVENT", "RULE009"],
                "text": ("The event data does not include that. Known gaps: " + gap_text + ". "
                         "List these as information gaps and assign a person to verify them; do not invent a "
                         "flight or aircraft position. " + SIM)}

    if _has(REJECT, q):
        return {"intent": "rejection", "sources": ["RULE006", "FEEDBACK-HISTORY"],
                "text": ("When a professional rejects the advice, the reason is recorded in an append-only log, the "
                         "original advice is preserved and the next similar event quotes the decision. Nothing is "
                         "overwritten. " + SIM)}

    if _has(DOWNGRADE, q):
        return {"intent": "downgrade", "sources": _sources(facts, "SIM-BASE", "FEEDBACK-HISTORY"),
                "text": ("New information can change the assessment: if resources are confirmed sufficient and the "
                         "wind is within limits, the risk should be reviewed downward and the first action should be "
                         "to record the confirmed position and continue monitoring. The previous advice remains on "
                         "record. " + SIM)}

    if _has(TIME, q):
        return {"intent": "time_range", "sources": ["SIM-BASE"],
                "text": ("The baseline is monthly data for 2024-01 to 2025-12 (192 airport-months). The event window "
                         "is separate and short (for example the next six hours). Do not mix a single month with the "
                         "cumulative window. " + SIM)}

    if _has(STOP, q):
        return {"intent": "stop", "sources": ["RULE012"],
                "text": ("Stop generating firm conclusions. When source reliability cannot be judged, output the "
                         "information gaps and a named escalation target (Operations Lead) instead of a definitive "
                         "recommendation. " + SIM)}

    if _has(NEW_AIRPORT, q):
        return {"intent": "new_airport", "sources": _sources(facts, "SIM-BASE", "EVENT"),
                "text": ("Use the New event form to enter the new airport and event. The app looks up that airport's "
                         "own monthly baseline and recomputes the three comparisons; it does not replay a canned "
                         "Hailing answer. " + SIM)}

    if _has(TWO_MSG, q):
        msgs = (output or {}).get("messages") or {}
        return {"intent": "two_messages", "sources": ["RULE002", "RULE005"],
                "text": ("Operations audience: " + (msgs.get("ops") or "prepare a monitoring checklist.") +
                         "\n\nPassenger audience: " + (msgs.get("passengers") or "a draft saying possible delays and "
                         "check official channels.") + " " + SIM)}

    # bounded fallback
    first_action = first
    gaps = list(facts.get("unknowns") or [])[:2]
    return {"intent": "fallback", "sources": _sources(facts, "SIM-BASE", "EVENT"),
            "text": ("The event data cannot answer that question. What we can say: risk level is " + risk_en +
                     "; first action: " + first_action +
                     ("; known gaps: " + "; ".join(gaps) if gaps else "") + ". " + SIM)}
