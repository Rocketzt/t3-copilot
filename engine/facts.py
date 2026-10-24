"""Source-backed, privacy-scrubbed fact sheets for the writer and checker."""

from __future__ import annotations

import re

from .data import Data, load_data
from .detector import airport_context, compute_all
from .feedback import match
from .i18n import AIRPORT_EN, IMPORTANCE_EN
from .rules import CONFLICT, WEATHER, evaluate, has_any

SIM_LABEL = "模拟 / SIMULATED"
_EVENT_NUMBER = re.compile(r"(?<![0-9])[-+]?[0-9]+(?:\.[0-9]+)?(?![0-9])")
_EVENT_TEXT_FIELDS = ("weather_text", "ops_text", "known", "unknown", "notes")
_PII_PATTERNS = (
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    re.compile(r"(?<!\d)\d{17}[\dXx](?!\w)"),
    re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    re.compile(r"(?i)(Passenger\s+)[\u4e00-\u9fff]{2,4}"),
    re.compile(r"(旅客\s*[:：]?\s*)(?!信息|服务|提示|草案|状态)([\u4e00-\u9fff]{2,4})(?=\s|[,，。;；]|$|表示|说|称|反馈|询问|要求|的)"),
    re.compile(r"(姓名\s*[:：]\s*)[\u4e00-\u9fff]{2,4}"),
)


def redact_text(text: str) -> str:
    value = str(text)
    for pattern in _PII_PATTERNS:
        if pattern.groups:
            value = pattern.sub(r"\1[REDACTED]", value)
        else:
            value = pattern.sub("[REDACTED]", value)
    return value


def sanitize_event(event: dict) -> tuple[dict, bool]:
    clean = {key: redact_text(value) if isinstance(value, str) else value for key, value in event.items()}
    return clean, clean != event


def _text_numbers(text: str) -> list[tuple[float, str]]:
    """Extract only Arabic numeric literals present in sanitized event text."""
    return [(float(token), "") for token in _EVENT_NUMBER.findall(text)]


def _risk(event: dict, context: dict, rules: list[dict], feedback_matches: list[dict]) -> dict:
    full = " ".join(str(event.get(k) or "") for k in ("name", "notes", "known", "unknown", "ops_text"))
    if has_any(full, CONFLICT) or context["verdict"] == "can't tell":
        return {"level": "Can't tell", "level_zh": "无法判断", "score": None,
                "reasons": [{"text": "Sources conflict; verify update times and definitions before deciding", "source": "RULE001"}],
                "can_tell": False, "can_tell_zh": "无法判断"}
    weather_risk = has_any(str(event.get("weather_text") or ""), WEATHER)
    pressure = any(r["id"] == "RULE004" for r in rules)
    score = context["signal_count"] * 1.25 + 2 * weather_risk + pressure + (event.get("importance") == "高")
    reasons = [{"text": f'{context["signal_count"]} detector signals for {context["month_label"]}', "source": "SIM-BASE"}]
    if weather_risk:
        reasons.append({"text": "Weather risk is described in the event, not proven flight impact", "source": event.get("id", "EVENT")})
    if pressure:
        reasons.append({"text": "Operational pressure is described in the event", "source": event.get("id", "EVENT")})
    if any(r["result"] == "Reject" for r in feedback_matches):
        score = max(0, score - 2.5)
        reasons.append({"text": "Human rejection reports adequate resources; verify current resources", "source": "RULE006"})
    level = "High" if score >= 7 else "Medium" if score >= 3.5 else "Low"
    return {"level": level, "level_zh": {"High": "高", "Medium": "中", "Low": "低"}[level],
            "score": round(score, 2), "reasons": reasons, "can_tell": True, "can_tell_zh": "可判断"}


def build_facts(data: Data, event: dict, context: dict | None = None,
                rules: list[dict] | None = None) -> dict:
    clean, redacted = sanitize_event(event)
    if context is None:
        context = airport_context(data, clean["airport"])
    initial_rules = rules if rules is not None else evaluate(data, clean, context)
    matches = match(clean, initial_rules)
    if matches and rules is None:
        clean["has_feedback"] = True
        initial_rules = evaluate(data, clean, context)
    risk = _risk(clean, context, initial_rules, matches)
    source_event = clean.get("id", "EVENT")
    airport = clean["airport"]
    selected = next(r for r in compute_all(data) if (r["airport"], r["year"], r["month"]) ==
                    (airport, context["year"], context["month"]))
    relevant = [r for r in compute_all(data) if r["airport"] == airport and r["year"] == 2025 and r["signal_count"] >= 1]
    if selected not in relevant:
        relevant.insert(0, selected)
    else:
        relevant.sort(key=lambda r: (r["year"], r["month"]), reverse=True)
    facts = []
    numbers = []

    def add(text: str, source: str, values: list[tuple[float, str]] = ()) -> None:
        fact_id = f'F{len(facts) + 1:02d}'
        facts.append({"id": fact_id, "text": text, "source": source, **({"value": values[0][0], "unit": values[0][1]} if values else {})})
        for value, unit in values:
            display = f'{value:+.2f} {unit}' if unit == "pp" else f'{value:.2f}{unit}' if unit == "%" else f'{value:g} {unit}' if unit else f'{value:g}'
            numbers.append({"value": value, "unit": unit, "display": display, "source": source, "fact_id": fact_id})

    for row in relevant:
        completion = round(row["completion"] * 100, 2)
        avg = round(row["own_avg12"] * 100, 2)
        text = (f'{AIRPORT_EN.get(airport, airport)} {row["month_label"]}: completion {completion:.2f}% '
                f'versus own average {avg:.2f}% ({row["delta_pp"]:+.2f} pp); '
                f'peer gap {row["peer_delta_pp"]:+.2f} pp')
        values = [(completion, "%"), (avg, "%"), (row["delta_pp"], "pp"), (row["peer_delta_pp"], "pp")]
        if row["yoy_delta_pp"] is not None:
            text += f'; YoY gap {row["yoy_delta_pp"]:+.2f} pp'
            values.append((row["yoy_delta_pp"], "pp"))
        text += f'; {row["signal_count"]} detector signals'
        values.append((row["signal_count"], "signals"))
        add(text + ".", "SIM-BASE", values)
    airport_info = next(a for a in data.airports if a["name"] == airport)
    add(f'{AIRPORT_EN.get(airport, airport)} is a {airport_info["tier"]} airport; airline importance {IMPORTANCE_EN.get(clean.get("importance"), clean.get("importance"))}.', "SIM-SCALE")
    weather_row = next((r for r in data.weather if (r["airport"], r["year"], r["month"]) ==
                        (airport, context["year"], context["month"])), None)
    if weather_row is None:
        raise ValueError(f'Weather row absent for {airport} {context["month_label"]}')
    if weather_row["missing"]:
        add(f'Weather observation for {AIRPORT_EN.get(airport, airport)} {context["month_label"]} is marked missing; no precipitation, wind, or bad-weather-day values are used.', "SIM-WEATHER")
    else:
        precipitation = weather_row["precipitation_mm"]
        wind = weather_row["max_wind_ms"]
        bad_days = weather_row["bad_weather_days"]
        add(f'Weather observation for {AIRPORT_EN.get(airport, airport)} {context["month_label"]}: '
            f'precipitation {precipitation:g} mm, max wind {wind:g} m/s, '
            f'bad-weather days {bad_days:g}.',
            "SIM-WEATHER", [(precipitation, "mm"), (wind, "m/s"), (bad_days, "days")])
    add(f'Event weather description: {clean.get("weather_text") or "not supplied"}. Forecast is not proof of per-flight impact.',
        source_event, _text_numbers(str(clean.get("weather_text") or "")))
    for field in _EVENT_TEXT_FIELDS[1:]:
        field_text = str(clean.get(field) or "")
        values = _text_numbers(field_text)
        if values:
            add(f'Event {field}: {field_text}', source_event, values)
    unknowns = [redact_text(s.strip()) for s in re.split(r"[、;,；]", str(clean.get("unknown") or "")) if s.strip()]
    missing_data = ["Monthly baselines cannot establish per-flight causation or current aircraft, crew, and gate status"]
    if context["weather_missing"]:
        missing_data.append(f'Weather row missing for {airport} {context["month_label"]}; no weather value imputed')
    if risk["level"] == "Can't tell":
        missing_data.append("Conflicting sources require update-time and definition verification")
    if risk["level"] == "Can't tell":
        first_action = "verify source update times and definitions"
    elif any(r["result"] == "Reject" for r in matches):
        first_action = "confirm current resources"
    elif any(r["id"] == "RULE002" for r in initial_rules):
        first_action = "confirm ground-support capacity and weather update time with airport coordination"
    else:
        first_action = "verify current operational status with the responsible team"
    sources = sorted({f["source"] for f in facts} | {r["id"] for r in initial_rules})
    return {"facts": facts, "numbers": numbers,
            "assumptions": ["[ASSUMPTION] Monthly patterns may indicate risk but do not prove a current flight impact"],
            "unknowns": unknowns, "missing_data": missing_data,
            "forbidden_actions": ["Cancel, release, dispatch, maintain, or compensate flights without human approval [RULE007]",
                                  "Publish a passenger notice without human review [RULE005]"],
            "sources": sources, "risk": risk, "pii_redacted": redacted,
            "feedback_matches": matches, "conflict": risk["level"] == "Can't tell",
            "sim_label": SIM_LABEL, "first_action": first_action, "event": clean}


def build_factsheet(event: dict | str, data: Data | None = None, year: int | None = None,
                    month: int | None = None) -> dict:
    data = data or load_data()
    selected_event = next(e for e in data.events if e["id"] == event) if isinstance(event, str) else event
    clean, input_redacted = sanitize_event(selected_event)
    context = airport_context(data, clean["airport"], year, month)
    facts = build_facts(data, clean, context)
    facts["pii_redacted"] = facts["pii_redacted"] or input_redacted
    clean = facts.pop("event")
    rules = evaluate(data, {**clean, "has_feedback": bool(facts["feedback_matches"])}, context)
    return {"event": {**clean, "airport_en": AIRPORT_EN.get(clean["airport"], clean["airport"]),
                      "importance_en": IMPORTANCE_EN.get(clean.get("importance"), clean.get("importance")),
                      "is_custom": clean.get("id") not in {e["id"] for e in data.events}},
            "detector": context, "rules": rules, "facts": facts}
