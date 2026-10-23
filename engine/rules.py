"""Pure, deterministic implementations of organizer rules RULE001-012."""

from __future__ import annotations

import re

from .data import Data

CONFLICT = ("冲突", "不一致", "两个来源", "矛盾", "conflict", "discrepan")
WEATHER = ("强降雨", "阵风", "雷雨", "暴雨", "大风", "低温", "降雪", "大雪", "storm", "heavy rain", "thunder", "typhoon", "gale", "snow")
NO_FORMAL = ("没有正式", "尚未", "暂无", "未发布", "没有正式延误", "no formal", "not yet")
PRESSURE = ("下降", "集中", "调整", "积压", "延误", "压力", "繁忙增加", "拥堵", "drop", "busy", "pressure", "congest", "queue")
DECISIONS = ("取消", "放行", "调度", "维修", "赔付", "cancel", "release", "dispatch", "maintenance", "compensation")
SAFETY = ("安全", "事故", "跑道关闭", "飞机故障", "safety", "incident", "runway closed")
OVERRULE = ("拒绝", "否决", "reject", "overrule", "人工反馈")
TOPICS_EN = {
    "RULE001": "Insufficient information", "RULE002": "Weather risk", "RULE003": "Own-history anomaly",
    "RULE004": "Sustained operational pressure", "RULE005": "Passenger communication",
    "RULE006": "Human overrule", "RULE007": "Major operational decisions",
    "RULE008": "High-risk escalation", "RULE009": "Citations", "RULE010": "Simulation label",
    "RULE011": "Privacy", "RULE012": "Stop condition",
}


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _text(event: dict, *keys: str) -> str:
    return " ".join(str(event.get(key) or "") for key in keys)


def _has_pii(text: str) -> bool:
    return bool(re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)|(?<!\d)\d{17}[\dXx](?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|姓名\s*[:：]|手机", text))


def _shape(row: dict) -> dict:
    return {"id": row["id"], "topic": row["topic"], "topic_en": TOPICS_EN[row["id"]],
            "trigger": row["trigger"], "checks": [s for s in re.split(r"[、；;]", row["checks"] or "") if s],
            "action": row["action"], "action_en": "", "escalate_to": row["escalate_to"],
            "escalate_to_en": "", "manual_approval": bool(row["manual_approval"]),
            "forbidden": row["forbidden"], "forbidden_en": "", "source": row["source"]}


def all_rules(data: Data) -> list[dict]:
    return [_shape(r) for r in data.rules]


def evaluate(data: Data, event: dict, context: dict) -> list[dict]:
    full = _text(event, "name", "weather_text", "ops_text", "notes", "known", "unknown", "question")
    weather_text = _text(event, "weather_text")
    ops_known = _text(event, "ops_text", "known", "notes")
    unknown = _text(event, "unknown")
    conflict = has_any(full, CONFLICT)
    missing_defs = sum(token in unknown for token in ("来源", "口径", "更新时间")) >= 2
    weather_risk = has_any(weather_text, WEATHER)
    no_formal = has_any(ops_known, NO_FORMAL)
    pressure = has_any(_text(event, "ops_text"), PRESSURE)
    risk_signals = sum((context.get("signal_count", 0) >= 2, weather_risk, pressure, conflict))
    fired = {
        "RULE001": conflict or missing_defs,
        "RULE002": weather_risk and no_formal,
        "RULE003": any(c.get("key") == "own" and c.get("signal") is True for c in context.get("comparisons", [])),
        "RULE004": pressure,
        "RULE005": weather_risk and no_formal,
        "RULE006": bool(event.get("has_feedback")) or has_any(_text(event, "notes"), OVERRULE),
        "RULE007": has_any(full, DECISIONS),  # ERRATA C8: decision words only.
        "RULE008": risk_signals >= 2,
        "RULE009": True,
        "RULE010": True,
        "RULE011": _has_pii(full),
        "RULE012": conflict or has_any(full, SAFETY) or context.get("verdict") == "can't tell",
    }
    return [_shape(r) for r in data.rules if fired[r["id"]]]
