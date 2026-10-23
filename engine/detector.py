"""Deterministic monthly airport comparisons using simulated workbook data."""

from __future__ import annotations

from collections import Counter, defaultdict

from .data import Data, load_data
from .i18n import AIRPORT_EN, IMPORTANCE_EN

THRESHOLD_PP = 5.0
VERDICTS = {0: "normal", 1: "watch", 2: "unusual", 3: "clearly unusual"}
DEFAULT_AIRPORTS = ("海陵国际机场", "云川国际机场")


def _pp(value: float) -> float:
    return round(float(value) + 0.0, 2)


def compute_all(data: Data | None = None) -> list[dict]:
    data = data or load_data()
    by_key = {(r["airport"], r["year"], r["month"]): r for r in data.baseline}
    weather = {(r["airport"], r["year"], r["month"]): r for r in data.weather}
    airport_info = {a["name"]: a for a in data.airports}
    if len(by_key) != len(data.baseline) or len(weather) != len(data.weather):
        raise ValueError("Duplicate baseline or weather airport-month")
    output = []
    for row in sorted(data.baseline, key=lambda r: (r["year"], r["month"], r["airport"])):
        key = (row["airport"], row["year"], row["month"])
        if key not in weather:
            raise ValueError("Missing weather airport-month")
        prior = by_key.get((row["airport"], row["year"] - 1, row["month"]))
        own = _pp(row["delta_pp"])  # Workbook column I is already percentage points.
        peer = _pp((row["completion"] - row["peer_avg"]) * 100)
        yoy = _pp((row["completion"] - prior["completion"]) * 100) if prior else None
        signals = {"own": own <= -THRESHOLD_PP, "peer": peer <= -THRESHOLD_PP, "yoy": yoy is not None and yoy <= -THRESHOLD_PP}
        count = sum(signals.values())
        available = 2 + (yoy is not None)
        missing = weather[key]["missing"]
        notes = []
        if yoy is None:
            notes.append("No previous-year comparison available")
        if missing:
            notes.append("Weather record missing; weather values are not evidence")
        info = airport_info[row["airport"]]
        output.append({
            "airport": row["airport"], "airport_en": AIRPORT_EN.get(row["airport"], row["airport"]),
            "year": row["year"], "month": row["month"], "month_label": f'{row["year"]}-{row["month"]:02d}',
            "tier": row["tier"], "importance": IMPORTANCE_EN.get(info["importance"], info["importance"]),
            "completion": row["completion"], "release": row["release"], "peer_avg": row["peer_avg"],
            "own_avg12": row["own_avg12"], "delta_pp": own, "peer_delta_pp": peer, "yoy_delta_pp": yoy,
            "signals": signals, "signal_count": count, "comparisons_available": available,
            "weather_missing": missing, "verdict": VERDICTS[count] if available >= 2 else "can't tell",
            "confidence": round(1 - 0.15 * (3 - available) - 0.1 * missing, 2), "notes": notes,
        })
    return output


def ranking(data: Data | None = None) -> dict:
    rows = compute_all(data)
    rank = {"High": 3, "Medium": 2, "Low": 1}
    rows.sort(key=lambda r: (-r["signal_count"], r["delta_pp"], -rank.get(r["importance"], 0), r["month_label"], r["airport"]))
    counts = Counter(r["signal_count"] for r in rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[f'{row["month"]:02d}'].append(row["completion"] * 100)
    monthly = {month: round(sum(vals) / len(vals), 2) for month, vals in sorted(grouped.items())}
    return {"rows": rows, "total": len(rows), "flags_own": sum(r["signals"]["own"] for r in rows),
            "flags_any": sum(r["signal_count"] > 0 for r in rows),
            "counts": {str(n): counts[n] for n in range(4)},
            "multi_signal": [r for r in rows if r["signal_count"] >= 2],
            "monthly_avg_completion": monthly}


def airport_context(data: Data, airport: str, year: int | None = None, month: int | None = None) -> dict:
    rows = [r for r in compute_all(data) if r["airport"] == airport]
    if not rows:
        raise KeyError(f"Unknown airport: {airport}")
    if (year is None) != (month is None):
        raise ValueError("year and month must be supplied together")
    if year is not None:
        chosen = next((r for r in rows if (r["year"], r["month"]) == (year, month)), None)
        if chosen is None:
            raise KeyError(f"No baseline for {airport} {year}-{month:02d}")
        reason = "Explicitly requested month"
    else:
        recent = [r for r in rows if r["year"] == 2025]
        multi = [r for r in recent if r["signal_count"] >= 2]
        any_signal = [r for r in recent if r["signal_count"] >= 1]
        if multi:
            chosen = max(multi, key=lambda r: r["month"])
            reason = "Latest anomalous month used as context (2+ signals); event date was not supplied"
        elif any_signal:
            chosen = max(any_signal, key=lambda r: r["month"])
            reason = "Latest anomalous month used as context (1 signal); event date was not supplied"
        else:
            chosen = max(recent, key=lambda r: r["month"])
            reason = "Latest 2025 month used as context; event date was not supplied"
    def comparison(key: str, label: str, value: float | None, comparator: float | None) -> dict:
        if value is None:
            detail = "No 2024 comparison available"
        else:
            detail = f'{chosen["completion"] * 100:.2f}% vs {comparator * 100:.2f}% = {value:+.2f} pp'
        return {"key": key, "label": label, "value_pp": value, "threshold_pp": -THRESHOLD_PP,
                "signal": chosen["signals"][key] if value is not None else None, "detail": detail}
    prior = next((r for r in rows if r["year"] == chosen["year"] - 1 and r["month"] == chosen["month"]), None)
    comparisons = [comparison("own", "Own 12-month average", chosen["delta_pp"], chosen["own_avg12"]),
                   comparison("peer", "Same-size peer average", chosen["peer_delta_pp"], chosen["peer_avg"]),
                   comparison("yoy", "Same month previous year", chosen["yoy_delta_pp"], prior["completion"] if prior else None)]
    flags = [{"year": r["year"], "month": r["month"], "month_label": r["month_label"],
              "signal_count": r["signal_count"], "delta_pp": r["delta_pp"], "verdict": r["verdict"]}
             for r in rows if r["signal_count"] >= 1]
    recent = [r for r in flags if (r["year"], r["month"]) <= (chosen["year"], chosen["month"]) and
              (r["year"] * 12 + r["month"]) > (chosen["year"] * 12 + chosen["month"] - 12)]
    return {"airport": airport, "airport_en": chosen["airport_en"], "year": chosen["year"],
            "month": chosen["month"], "month_label": chosen["month_label"], "tier": chosen["tier"],
            "selection_reason": reason, "comparisons": comparisons, "signal_count": chosen["signal_count"],
            "verdict": chosen["verdict"], "confidence": chosen["confidence"],
            "confidence_notes": [f'{chosen["comparisons_available"]} of 3 comparisons available',
                                 "weather record missing" if chosen["weather_missing"] else "weather record present"],
            "weather_missing": chosen["weather_missing"], "recent_anomalies": recent,
            "flagged_airport_months": flags}


def chart_series(data: Data, airports: list[str] | None = None, start: tuple[int, int] = (2024, 1), end: tuple[int, int] = (2025, 12)) -> dict:
    airports = list(airports or DEFAULT_AIRPORTS)
    rows = [r for r in compute_all(data) if start <= (r["year"], r["month"]) <= end]
    months = sorted({r["month_label"] for r in rows})
    series = []
    for airport in airports:
        selected = {r["month_label"]: r for r in rows if r["airport"] == airport}
        if not selected:
            raise KeyError(f"Unknown airport: {airport}")
        values = [{"month": label, "completion_pct": round(selected[label]["completion"] * 100, 2),
                   "peer_pct": round(selected[label]["peer_avg"] * 100, 2),
                   "own_avg_pct": round(selected[label]["own_avg12"] * 100, 2),
                   "delta_pp": selected[label]["delta_pp"]} for label in months if label in selected]
        series.append({"airport": airport, "airport_en": AIRPORT_EN.get(airport, airport), "values": values})
    return {"months": months, "series": series}


def summary(data: Data | None = None) -> dict:
    ranked = ranking(data)
    return {"total": ranked["total"], "airports": len({r["airport"] for r in ranked["rows"]}),
            "months": len({r["month_label"] for r in ranked["rows"]}), "flags_own": ranked["flags_own"],
            "flags_any": ranked["flags_any"], "multi_signal": len(ranked["multi_signal"]),
            "missing_weather": sum(r["weather_missing"] for r in ranked["rows"])}
