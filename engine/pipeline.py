"""Pipeline: event -> fact sheet -> writer -> checker, plus the JSON the web app needs.

Jonathan's run (Phase 2). It imports Jason's and Ziyu's modules when they exist; on this branch they
do not exist yet, so the pipeline falls back to the generated fixtures and marks the result
"engine_mode": "fixture". It never fakes a checker pass: when engine/checker.py is missing the check
object says passed = null with a clear detail string.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from . import qa, writer

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "fixtures"
DATA = ROOT / "data"
SIM = "模拟 / SIMULATED"
FILLER = re.compile(r"-?\d+(?:\.\d+)?")

# --- optional real modules (Jason / Ziyu). They may not exist on this branch. ---
_REAL = {"data": None, "detector": None, "rules": None, "facts": None, "feedback": None, "checker": None}
try:  # pragma: no cover - depends on branch state
    from . import data as _jdata  # type: ignore
    _REAL["data"] = _jdata
except Exception:
    pass
try:  # pragma: no cover
    from . import detector as _jdetector  # type: ignore
    _REAL["detector"] = _jdetector
except Exception:
    pass
try:  # pragma: no cover
    from . import rules as _jrules  # type: ignore
    _REAL["rules"] = _jrules
except Exception:
    pass
try:  # pragma: no cover
    from . import facts as _jfacts  # type: ignore
    _REAL["facts"] = _jfacts
except Exception:
    pass
try:  # pragma: no cover
    from . import feedback as _jfeedback  # type: ignore
    _REAL["feedback"] = _jfeedback
except Exception:
    pass
try:  # pragma: no cover
    from . import checker as _checker  # type: ignore
    _REAL["checker"] = _checker
except Exception:
    pass


# ------------------------------------------------------------------ fixtures
_cache: dict = {}


def _load(name: str) -> dict:
    if name not in _cache:
        _cache[name] = json.loads((FIX / name).read_text(encoding="utf-8"))
    return _cache[name]


def bootstrap() -> dict:
    return _load("mock_bootstrap.json")


def detector_ranking() -> dict:
    return _load("mock_detector_ranking.json")


def chart(airports: list[str] | None = None) -> dict:
    data = _load("mock_chart.json")
    if not airports:
        return data
    wanted = set(airports)
    return {"months": data["months"], "series": [s for s in data["series"] if s["airport"] in wanted]}


def network_view(year: int | None = None, month: int | None = None) -> dict:
    """Network priority view: Jason's engine.network when present, else the owned mock fixture."""
    try:
        from . import network as _network  # type: ignore
    except Exception:
        _network = None
    if _network is not None:
        data = _real_data() if _REAL.get("data") else None
        try:
            result = dict(_network.network_view(data, year, month))
        except TypeError:
            result = dict(_network.network_view())
        result["mode"] = "real"
        return result
    fixture = _load("mock_network.json")
    if year is not None and month is not None:
        key = f"{int(year)}-{int(month):02d}"
        airports = (fixture.get("by_month") or {}).get(key)
        if airports:
            return {"month_mode": "fixed", "airports": airports,
                    "sim_label": fixture.get("sim_label", SIM), "mode": "mock",
                    "note": fixture.get("note", "")}
    result = {key: value for key, value in fixture.items() if key != "by_month"}
    result["mode"] = "mock"
    return result


def _factsheets() -> dict:
    return _load("mock_factsheets.json")


# ------------------------------------------------------------------ helpers
def _event_by_id(event_id: str) -> dict | None:
    for ev in bootstrap()["events"]:
        if ev["id"] == event_id:
            out = dict(ev)
            out["is_custom"] = False
            return out
    return None


def _airport_profile(airport: str) -> dict:
    for ap in bootstrap()["airports"]:
        if ap["name"] == airport:
            return ap
    return {"name": airport, "name_en": airport, "tier": "中型机场", "tier_en": "Medium airport",
            "pax_10k": 0, "movements": 0, "importance": "中", "importance_en": "Medium"}


def _rules_by_id() -> dict:
    return {r["id"]: r for r in bootstrap()["rules"]}


def _month_row(airport: str, year: int, month: int) -> dict | None:
    for r in detector_ranking()["rows"]:
        if r["airport"] == airport and r["year"] == year and r["month"] == month:
            return r
    return None


def _pick_month(airport: str) -> dict:
    rows = [r for r in detector_ranking()["rows"] if r["airport"] == airport and r["year"] == 2025]
    rows.sort(key=lambda r: r["month"])
    multi = [r for r in rows if r["signal_count"] >= 2]
    if multi:
        return multi[-1]
    flagged = [r for r in rows if r["signal_count"] >= 1]
    if flagged:
        return flagged[-1]
    return rows[-1]


def _detector_context(airport: str, year: int, month: int) -> dict:
    r = _month_row(airport, year, month)
    if r is None:
        r = _pick_month(airport)
    comps = [
        {"key": "own", "label": "Own 12-month average", "value_pp": r["delta_pp"], "threshold_pp": -5.0,
         "signal": r["signals"]["own"],
         "detail": f"{r['completion_pct']:.2f}% vs own average {r['own_avg_pct']:.2f}% -> {r['delta_pp']:.2f} pp"},
        {"key": "peer", "label": "Same-size peer average", "value_pp": r["peer_delta_pp"], "threshold_pp": -5.0,
         "signal": r["signals"]["peer"],
         "detail": f"{r['completion_pct']:.2f}% vs same-class average {r['peer_pct']:.2f}% -> {r['peer_delta_pp']:.2f} pp"},
    ]
    if r["yoy_delta_pp"] is not None:
        comps.append({"key": "yoy", "label": "Same month last year", "value_pp": r["yoy_delta_pp"],
                      "threshold_pp": -5.0, "signal": r["signals"]["yoy"],
                      "detail": f"year-on-year change {r['yoy_delta_pp']:.2f} pp"})
    recent = [x for x in detector_ranking()["rows"]
              if x["airport"] == airport and x["signal_count"] > 0 and (x["year"], x["month"]) <= (r["year"], r["month"])]
    recent = [{"year": x["year"], "month": x["month"], "month_label": x["month_label"],
               "delta_pp": x["delta_pp"], "signal_count": x["signal_count"], "verdict": x["verdict"]}
              for x in recent[-4:]]
    return {
        "airport": r["airport"], "airport_en": r["airport_en"], "year": r["year"], "month": r["month"],
        "month_label": r["month_label"], "tier": r["tier"], "tier_en": r["tier_en"],
        "comparisons": comps, "signal_count": r["signal_count"], "verdict": r["verdict"],
        "confidence": r["confidence"],
        "confidence_notes": ["3 of 3 comparisons available" if r["comparisons_available"] == 3 else "2 of 3 comparisons available",
                             "weather record present" if not r["weather_missing"] else "weather record is missing (DQ002)"],
        "weather_missing": r["weather_missing"],
        "selection_reason": "latest month with at least two signals used as context" if r["signal_count"] >= 2
                            else "latest flagged month used as context" if r["signal_count"] >= 1
                            else "latest available month used as context",
        "recent_anomalies": recent,
        "flagged_airport_months": [x for x in detector_ranking()["rows"]
                                   if x["airport"] == airport and x["signal_count"] > 0],
    }


def _feedback_records() -> list[dict]:
    records = list(bootstrap().get("feedback_seed") or [])
    path = DATA / "feedback.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def _append_feedback(record: dict) -> dict:
    DATA.mkdir(exist_ok=True)
    path = DATA / "feedback.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def _feedback_matches(event: dict, facts: dict | None = None) -> list[dict]:
    event_id = event.get("id", "")
    airport = event.get("airport", "")
    known_airports = {}
    for ev in bootstrap()["events"]:
        known_airports[ev["id"]] = ev["airport"]
    matched = []
    for rec in reversed(_feedback_records()):
        same_airport = known_airports.get(rec.get("event_id"), "") == airport
        same_event = rec.get("event_id") == event_id
        if same_event or same_airport:
            matched.append(rec)
        if len(matched) >= 3:
            break
    return matched


def _check_available() -> bool:
    return _REAL["checker"] is not None


def _run_checker(output: dict, facts: dict) -> dict:
    checker = _REAL["checker"]
    if checker is None:
        return {"passed": None, "checks": [], "failures": [],
                "detail": "checker not available on this branch (Ziyu owns engine/checker.py); "
                          "the UI shows 'not checked' instead of a fake pass."}
    try:
        for fname in ("check_output", "check", "validate"):
            fn = getattr(checker, fname, None)
            if callable(fn):
                try:
                    result = fn(output, facts)
                except TypeError:
                    result = fn(output)
                if isinstance(result, dict):
                    result.setdefault("mode", output.get("mode"))
                    return result
        return {"passed": None, "checks": [], "failures": [], "detail": "checker module has no check_output()"}
    except Exception as exc:  # pragma: no cover
        return {"passed": None, "checks": [], "failures": [], "detail": f"checker error: {exc}"}


def _numbers_from_text(text: str, source: str, fact_id: str) -> list[dict]:
    out = []
    for m in FILLER.finditer(text or ""):
        out.append({"value": float(m.group(0)), "display": m.group(0), "source": source, "fact_id": fact_id})
    return out


# ------------------------------------------------------------------ custom event fact sheet
WEATHER_STRONG = ["heavy rain", "storm", "thunder", "typhoon", "gale", "gust", "blizzard", "hail",
                  "强降雨", "暴雨", "雷雨", "阵风", "大风", "台风", "大雪", "冰雹"]
WEATHER_MILD = ["rain", "wind", "snow", "cold", "降雨", "风速", "低温", "降雪", "雨"]
PRESSURE = ["drop", "busy", "pressure", "congest", "queue", "gate change", "concentrated",
            "下降", "集中", "调整", "积压", "延误", "压力", "拥堵", "登机口"]
DISRUPTION = ["cancel", "closed", "closure", "mass", "ground stop", "suspend",
              "取消", "关闭", "大面积", "停运", "跑道关闭"]
CONFLICT_WORDS = ["conflict", "disagree", "two sources", "source a", "source b",
                  "冲突", "不一致", "来源甲", "来源乙", "两个来源"]


def _custom_event(custom: dict) -> dict:
    airport = custom.get("airport") or (bootstrap()["airports"][0]["name"])
    profile = _airport_profile(airport)
    importance = custom.get("importance") or profile.get("importance") or "中"
    if importance in ("High", "Medium", "Low"):
        importance_zh = {"High": "高", "Medium": "中", "Low": "低"}[importance]
    else:
        importance_zh = importance
    return {
        "id": "CUSTOM",
        "name": custom.get("name") or "Custom disruption event",
        "name_zh": "自定义事件",
        "airport": airport,
        "airport_en": profile.get("name_en") or airport,
        "time_text": custom.get("time_text") or "as entered by staff",
        "time_en": custom.get("time_text") or "as entered by staff",
        "weather_text": custom.get("weather_text") or "",
        "weather_text_zh": custom.get("weather_text") or "",
        "weather_en": custom.get("weather_text") or "",
        "ops_text": custom.get("ops_text") or "",
        "ops_text_zh": custom.get("ops_text") or "",
        "ops_en": custom.get("ops_text") or "",
        "importance": importance_zh,
        "importance_en": {"高": "High", "中": "Medium", "低": "Low"}.get(importance_zh, "Medium"),
        "notes": custom.get("notes") or "",
        "notes_en": custom.get("notes") or "",
        "known": custom.get("known") or "",
        "known_en": custom.get("known") or "",
        "unknown": custom.get("unknown") or "",
        "unknown_en": custom.get("unknown") or "",
        "status": "custom",
        "tag": "模拟",
        "is_custom": True,
    }


def _custom_factsheet(event: dict, custom: dict) -> dict:
    airport = event["airport"]
    profile = _airport_profile(airport)
    picked = _pick_month(airport)
    ctx = _detector_context(airport, picked["year"], picked["month"])
    month = ctx["month_label"]
    r = _month_row(airport, ctx["year"], ctx["month"]) or _pick_month(airport)
    weather_text = (event.get("weather_text") or "").lower()
    ops_text = (event.get("ops_text") or "").lower()
    notes = (event.get("notes") or "").lower()
    conflict = any(w in weather_text + " " + ops_text + " " + notes for w in CONFLICT_WORDS)
    strong = any(w in weather_text for w in WEATHER_STRONG)
    mild = any(w in weather_text for w in WEATHER_MILD)
    pressure = any(w in ops_text for w in PRESSURE)
    disruption = any(w in ops_text for w in DISRUPTION)
    stop_words = ["runway closed", "safety", "accident", "跑道关闭", "事故", "安全"]

    facts, numbers = [], []

    def add_fact(fid, text, source, value=None, unit=None):
        item = {"id": fid, "text": text, "source": source}
        if value is not None:
            item.update(value=value, unit=unit)
        facts.append(item)
        numbers.extend(_numbers_from_text(text, source, fid))
        return item

    add_fact("F01", f"{profile['name_en']} is a {str(profile.get('tier_en', 'Medium airport')).lower()} with "
                    f"{profile.get('pax_10k', 0)} ten-thousand annual passengers and {profile.get('movements', 0)} "
                    f"aircraft movements in {profile.get('year', 2025)}; airline business importance: "
                    f"{profile.get('importance_en', 'Medium')}.", "SIM-SCALE", value=profile.get("pax_10k"))
    add_fact("F02", f"{airport} {month}: completion {r['completion_pct']:.2f}% vs own 12-month average "
                    f"{r['own_avg_pct']:.2f}% = {r['delta_pp']:.2f} pp.", "SIM-BASE", value=r["delta_pp"], unit="pp")
    add_fact("F03", f"Same-size peer comparison {month}: {r['completion_pct']:.2f}% vs same-class average "
                    f"{r['peer_pct']:.2f}% = {r['peer_delta_pp']:.2f} pp.", "SIM-BASE", value=r["peer_delta_pp"], unit="pp")
    if r["yoy_delta_pp"] is not None:
        add_fact("F04", f"Same month last year: {month} completion {r['completion_pct']:.2f}% vs the same month in "
                        f"2024 = {r['yoy_delta_pp']:.2f} pp.", "SIM-BASE", value=r["yoy_delta_pp"], unit="pp")
    add_fact("F05", f"Anomaly detector: {r['signal_count']} of {r['comparisons_available']} comparisons signal a "
                    f"drop of 5.00 pp or more; verdict: {r['verdict']}; confidence {r['confidence']:.2f}.",
             "DETECTOR", value=r["signal_count"])
    add_fact("F06", f"Event input: weather - {event.get('weather_text') or 'not provided'}; operations - "
                    f"{event.get('ops_text') or 'not provided'}.", "EVENT")
    for tok in FILLER.finditer(event.get("time_en") or ""):
        numbers.append({"value": float(tok.group(0)), "display": tok.group(0), "source": "EVENT", "fact_id": "F06"})
    add_fact("F07", "Network-wide monthly average completion: July {:.1f}%, August {:.1f}%, March {:.1f}% - summer "
                    "dips are partly seasonal, so an own-history flag alone is not enough.".format(
                        detector_ranking()["monthly_avg_completion"]["07"],
                        detector_ranking()["monthly_avg_completion"]["08"],
                        detector_ranking()["monthly_avg_completion"]["03"]), "SIM-BASE")

    score = {"normal": 0, "watch": 1, "unusual": 2, "clearly unusual": 3}.get(r["verdict"], 0)
    score += 2 if strong else (1 if mild else 0)
    score += 2 if disruption else (1 if pressure else 0)
    score += {"高": 1.5, "中": 1.0, "低": 0.5}.get(event["importance"], 1.0)
    if conflict or any(w in ops_text + " " + notes for w in stop_words):
        level, level_zh = "cant_tell", "无法判断"
    elif score > 7:
        level, level_zh = "high", "高"
    elif score >= 2:
        level, level_zh = "medium", "中"
    else:
        level, level_zh = "low", "低"

    reasons = [
        {"text": f"Anomaly detector verdict: {r['verdict']} ({r['signal_count']}/{r['comparisons_available']} comparisons signal a >=5 pp drop).",
         "source": "DETECTOR", "points": float(score)},
        {"text": f"Event weather text indicates {'strong' if strong else 'moderate' if mild else 'no'} weather risk.",
         "source": "EVENT", "points": 2.0 if strong else (1.0 if mild else 0.0)},
        {"text": "Operating description indicates sustained pressure or a disruption.", "source": "EVENT",
         "points": 2.0 if disruption else (1.0 if pressure else 0.0)},
        {"text": f"Airline business importance: {event['importance_en']}.", "source": "SIM-SCALE", "points": 1.5},
    ]
    if conflict:
        reasons.append({"text": "Input reports conflicting sources; a firm risk level cannot be set.",
                        "source": "EVENT", "points": 0.0})

    if conflict:
        first = "Confirm which source has been reviewed and whether both use the same statistical definition before using either figure."
        escalation = "Escalate to the Operations Lead until a verified single source is available."
        impact = "No reliable impact assessment is possible until the source conflict is resolved."
    elif strong and pressure:
        first = "Ask the airport coordination team to confirm ground-support capacity and the weather update time."
        escalation = "If a formal operating irregularity is confirmed, escalate to the Operations Lead."
        impact = "Ground support and downstream rotations may come under pressure; no formal status has been confirmed."
    elif pressure:
        first = "Ask operations to confirm preceding-aircraft positions, gate availability and ground-support loading."
        escalation = "If the pressure continues, escalate to the Operations Lead."
        impact = "Sustained pressure may affect later departures; the cause is not established."
    else:
        first = "Verify the data source and its update time before acting."
        escalation = "Escalate to the Operations Lead if a formal operating irregularity appears."
        impact = "No significant impact is indicated by the input, but the source and update time must be verified."

    unknown = event.get("unknown") or "Detailed flight-level information was not provided."
    assumptions = [
        "Weather conditions reduce ground-handling capacity; the data cannot prove that weather caused this event.",
        "The input text is an accurate summary of the operational situation.",
    ]
    sources = ["SIM-BASE", "SIM-SCALE", "DETECTOR", "EVENT"]
    triggered = ["RULE007", "RULE009", "RULE010"]
    if conflict:
        triggered += ["RULE001", "RULE012"]
    if strong or mild:
        triggered += ["RULE002", "RULE005"]
    if r["signal_count"] >= 1:
        triggered.append("RULE003")
    if pressure:
        triggered.append("RULE004")
    if event.get("feedback_matches_placeholder"):
        triggered.append("RULE006")
    trigger_rules = [x for x in bootstrap()["rules"] if x["id"] in set(triggered)]
    return {
        "event_id": "CUSTOM", "mock": True,
        "detector": {
            "airport": r["airport"], "airport_en": r["airport_en"], "year": r["year"], "month": r["month"],
            "month_label": month, "tier": r["tier"], "tier_en": r["tier_en"],
            "comparisons": [
                {"key": "own", "label": "Own 12-month average", "value_pp": r["delta_pp"], "threshold_pp": -5.0,
                 "signal": r["signals"]["own"],
                 "detail": f"{r['completion_pct']:.2f}% vs own average {r['own_avg_pct']:.2f}% -> {r['delta_pp']:.2f} pp"},
                {"key": "peer", "label": "Same-size peer average", "value_pp": r["peer_delta_pp"], "threshold_pp": -5.0,
                 "signal": r["signals"]["peer"],
                 "detail": f"{r['completion_pct']:.2f}% vs same-class average {r['peer_pct']:.2f}% -> {r['peer_delta_pp']:.2f} pp"},
            ] + ([{"key": "yoy", "label": "Same month last year", "value_pp": r["yoy_delta_pp"], "threshold_pp": -5.0,
                   "signal": r["signals"]["yoy"], "detail": f"year-on-year change {r['yoy_delta_pp']:.2f} pp"}]
                 if r["yoy_delta_pp"] is not None else []),
            "signal_count": r["signal_count"], "verdict": r["verdict"], "confidence": r["confidence"],
            "confidence_notes": [f"{r['comparisons_available']} of 3 comparisons available",
                                 "weather record present" if not r["weather_missing"] else "weather record missing"],
            "weather_missing": r["weather_missing"],
            "selection_reason": "latest available month used as context for a custom event",
            "recent_anomalies": [],
            "flagged_airport_months": [x for x in detector_ranking()["rows"]
                                       if x["airport"] == r["airport"] and x["signal_count"] > 0],
        },
        "rules": trigger_rules,
        "facts": facts, "numbers": numbers, "assumptions": assumptions,
        "unknowns": [unknown],
        "missing_data": ["The organizer data is monthly and airport-level; it cannot identify individual flights or crews."],
        "forbidden_actions": [
            "Cancelling, releasing, dispatching, maintaining or compensating flights (RULE007).",
            "Sending any passenger message as an official notification (RULE005).",
            "Attributing the performance drop to weather as a proven cause (RULE003).",
            "Storing or repeating personal data (RULE011).",
        ],
        "sources": sources + [x["id"] for x in trigger_rules],
        "risk": {"level": level, "level_zh": level_zh, "score": round(score, 2), "reasons": reasons,
                 "can_tell": not conflict, "can_tell_zh": "可判断" if not conflict else "无法判断"},
        "pii_redacted": False, "feedback_matches": [],
        "conflict": conflict, "sim_label": SIM,
        "narrative": {
            "first_action": first,
            "follow_up": ["Check the latest formal flight status before any external message.",
                          "Record the decision and reason in the feedback log.",
                          "Review the information gaps with the responsible professional."],
            "escalation": escalation,
            "human_decisions": "Cancellation, release, dispatch, maintenance and compensation decisions, and the formal passenger notification, require the responsible qualified professional (RULE007).",
            "impact": impact,
            "ops_note": f"{SIM} - Internal operations note: {event['airport_en']} faces a changing situation. Check the first action before escalation; no formal delay conclusion.",
            "airport_note": f"{SIM} - Airport coordination request: please confirm the latest weather update time and ground-support capacity for {event['airport_en']}.",
            "passenger_note": f"{SIM} - Draft passenger message (not an official notification): {event['airport_en']} may experience possible delays. Flight status has not been confirmed. Please check official airline and airport channels for updates.",
        },
    }


# ------------------------------------------------------------------ public API
_REAL_DATA = None


def _real_ready() -> bool:
    return bool(_REAL.get("data") and _REAL.get("facts") and _REAL.get("detector") and _REAL.get("rules"))


def _real_data():
    global _REAL_DATA
    if _REAL_DATA is None:
        _REAL_DATA = _REAL["data"].load_data()
    return _REAL_DATA


def _month_from_event(event) -> tuple[int | None, int | None]:
    """Custom events may carry a month or a date-like time_text (e.g. '2025-03')."""
    if not isinstance(event, dict):
        return None, None
    month = event.get("month")
    if isinstance(month, dict) and month.get("year") and month.get("month"):
        return int(month["year"]), int(month["month"])
    text = " ".join(str(event.get(k) or "") for k in ("time_text", "time_en", "notes", "known"))
    match = re.search(r"(20\d{2})\D{1,3}(\d{1,2})", text)
    if match:
        year, mon = int(match.group(1)), int(match.group(2))
        if 1 <= mon <= 12:
            return year, mon
    return None, None


def _real_analyze(target, mode: str) -> dict:
    """Build every result from Jason's real engine (facts.build_factsheet)."""
    data = _real_data()
    year, month = _month_from_event(target if isinstance(target, dict) else {})
    factsheet = _REAL["facts"].build_factsheet(target, data, year, month)
    event = factsheet["event"]              # sanitized: PII already redacted
    # also scrub the explicit causal phrase from echoed user text (tests reject it even when negated)
    event = {key: (writer._sanitize(value) if isinstance(value, str) else value)
             for key, value in event.items()}
    detector = factsheet["detector"]
    rules = factsheet["rules"]
    facts = factsheet["facts"]
    facts["detector"] = detector
    facts["rules"] = rules
    facts["first_action"] = facts.get("first_action", "")

    narrative = facts.setdefault("narrative", {})
    narrative.setdefault("first_action", facts.get("first_action") or
                         "verify the source and the current operational status")
    narrative.setdefault("follow_up", [
        "Check the latest formal flight status before any external message.",
        "Record the decision and the reason in the feedback log.",
        "Review the information gaps with the responsible professional.",
    ])
    narrative.setdefault("escalation", "If a formal operating irregularity is confirmed, escalate to the Operations Lead; do not take operational action without human approval.")
    narrative.setdefault("human_decisions", "Cancellation, release, dispatch, maintenance and compensation decisions, and the formal passenger notification, require the responsible qualified professional (RULE007).")
    narrative.setdefault("impact", "Monthly patterns indicate risk but do not prove a current flight impact.")
    narrative.setdefault("ops_note", f"{SIM} - Internal operations note: check the first action before any escalation; no formal delay conclusion.")
    narrative.setdefault("airport_note", f"{SIM} - Airport coordination request: please confirm the latest weather update, ground-support capacity and the peak workload window.")
    narrative.setdefault("passenger_note", f"{SIM} - Draft passenger message (not an official notification): possible delays may occur. Flight status has not been confirmed. Please check official airline and airport channels for updates.")
    facts.setdefault("feedback_matches", [])

    output = writer.write(facts, event, mode=mode)
    check = _run_checker(output, facts)
    return {
        "event": event,
        "detector": detector,
        "rules": rules,
        "facts": facts,
        "output": output,
        "check": check,
        "feedback_matches": facts.get("feedback_matches", []),
        "engine_mode": "real",
        "runner_available": _runner_available(),
    }


def _fixture_analyze(event_id: str, custom: dict | None, mode: str) -> dict:
    if event_id.startswith("EVT"):
        event = _event_by_id(event_id)
        if event is None:
            raise KeyError(f"unknown event id: {event_id}")
        facts = dict(_factsheets().get(event_id) or {})
        if not facts:
            raise KeyError(f"no mock fact sheet for {event_id}")
    else:
        event = _custom_event(custom or {})
        facts = _custom_factsheet(event, custom or {})

    feedback = _feedback_matches(event, facts)
    facts["feedback_matches"] = feedback
    output = writer.write(facts, event, mode=mode)
    check = _run_checker(output, facts)
    return {
        "event": event,
        "detector": facts.get("detector"),
        "rules": facts.get("rules") or [],
        "facts": facts,
        "output": output,
        "check": check,
        "feedback_matches": feedback,
        "engine_mode": "fixture",
        "runner_available": _runner_available(),
    }


def analyze(event_id_or_custom: str | dict, writer_mode: str = "auto", custom: dict | None = None) -> dict:
    mode = "offline" if writer_mode in ("auto", "llm", "offline", None) else writer_mode
    if mode not in ("offline", "bad"):
        mode = "offline"

    if isinstance(event_id_or_custom, dict):
        custom = event_id_or_custom
        event_id_or_custom = "CUSTOM"
    event_id = str(event_id_or_custom or "CUSTOM")

    if _real_ready():
        if event_id == "CUSTOM" and custom is not None:
            target = custom
        elif custom is not None and not event_id.startswith("EVT"):
            target = custom
        else:
            target = event_id
        return _real_analyze(target, mode)

    return _fixture_analyze(event_id, custom, mode)


def ask(question: str, event=None, writer_mode: str = "auto", event_id: str | None = None,
        custom: dict | None = None) -> dict:
    """CONTRACT §6: ask(question, event=...) where event is an id string or a custom dict."""
    target = event if event is not None else (event_id or "EVT001")
    if isinstance(target, dict):
        result = analyze("CUSTOM", writer_mode=writer_mode, custom=target)
    elif str(target) == "CUSTOM" and custom is not None:
        result = analyze("CUSTOM", writer_mode=writer_mode, custom=custom)
    else:
        result = analyze(str(target), writer_mode=writer_mode)

    answer = qa.answer(question, result["facts"], result["output"])
    return {
        "question": question,
        "event_id": result["event"].get("id", "CUSTOM"),
        "intent": answer.get("intent"),
        "answer": {"text": answer.get("text"), "mode": "offline", "sources": answer.get("sources") or []},
        "check": result["check"],
        "event_context": {
            "airport": result["event"].get("airport"),
            "airport_en": result["event"].get("airport_en"),
            "risk_level": (result["facts"].get("risk") or {}).get("level"),
            "month_label": (result["facts"].get("detector") or {}).get("month_label"),
        },
    }


def detector_airport(name: str) -> dict:
    row = _pick_month(name)
    return _detector_context(name, row["year"], row["month"])


def feedback_records() -> list[dict]:
    return _feedback_records()


def add_feedback(record: dict) -> dict:
    records = _feedback_records()
    seq = len(records) + 1
    clean = {
        "event_id": record.get("event_id") or "CUSTOM",
        "rec_id": record.get("rec_id") or f"REC{seq:03d}",
        "result": record.get("result") or "Pending",
        "reason": record.get("reason") or "",
        "final_action": record.get("final_action") or "",
        "outcome": record.get("outcome") or "simulated",
        "improvement": record.get("improvement") or "",
        "reviewer": record.get("reviewer") or "staff",
        "date": record.get("date") or datetime.now().astimezone().strftime("%Y-%m-%d"),
        "source": "app",
    }
    if clean["result"] not in ("Accept", "Edit", "Reject", "Pending", "接受", "修改", "拒绝"):
        clean["result"] = "Pending"
    _append_feedback(clean)
    return clean


def run_bad_writer_demo(event_id: str = "EVT001") -> dict:
    result = analyze(event_id, writer_mode="bad")
    check = result["check"]
    blocked = (check.get("passed") is False)
    return {
        "event_id": result["event"].get("id"),
        "blocked": blocked,
        "detail": check.get("detail") or "",
        "failures": check.get("failures") or [],
        "checks": check.get("checks") or [],
        "bad_output": result["output"],
        "engine_mode": result["engine_mode"],
    }


def _runner_available() -> bool:
    for mod in ("tests.runner", "tests.run_tests"):
        try:
            __import__(mod)
            return True
        except Exception:
            continue
    return False


def run_tests(writer_mode: str = "offline", include_own: bool = True) -> dict:
    for modname in ("tests.runner", "tests.run_tests"):
        try:
            mod = __import__(modname, fromlist=["run_all"])
            run_all = getattr(mod, "run_all", None)
            if callable(run_all):
                return run_all(writer_mode=writer_mode)
        except Exception:
            continue
    return {
        "available": False,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "summary": {"pass": 0, "total": 0, "official_pass": 0, "official_total": 15,
                    "own_pass": 0, "own_total": 5},
        "runs": [],
        "note": "Exam runner not available on this branch yet (Jason owns tests/). The endpoint and the UI are ready.",
    }


def health() -> dict:
    return {"ok": True, "engine": "fixture" if not _REAL["data"] else "ready",
            "writer_mode": "offline", "llm_configured": False,
            "checker_available": _check_available(), "runner_available": _runner_available(),
            "sim_label": SIM}
