"""Deterministic network priority view from detector airport-month output."""

from __future__ import annotations

from .data import Data, load_data
from .detector import airport_context, compute_all
from .i18n import IMPORTANCE_EN, TIER_EN

SIM_LABEL = "模拟 / SIMULATED"
_IMPORTANCE_RANK = {"高": 3, "中": 2, "低": 1}


def network_view(data: Data | None = None, year: int | None = None,
                 month: int | None = None) -> dict:
    """Rank airports by detector signals, airline importance, then own gap."""
    data = data or load_data()
    detector_rows = {(row["airport"], row["year"], row["month"]): row
                     for row in compute_all(data)}
    airports = []
    for info in data.airports:
        airport = info["name"]
        context = airport_context(data, airport, year, month)
        row = detector_rows[(airport, context["year"], context["month"])]
        importance = info["importance"]
        importance_en = IMPORTANCE_EN.get(importance, importance)
        airports.append({
            "airport": airport,
            "airport_en": row["airport_en"],
            "tier_en": TIER_EN.get(info["tier"], info["tier"]),
            "importance": importance,
            "importance_en": importance_en,
            "month_label": row["month_label"],
            "signal_count": row["signal_count"],
            "verdict": row["verdict"],
            "confidence": row["confidence"],
            "own_pp": row["delta_pp"],
            "peer_pp": row["peer_delta_pp"],
            "yoy_pp": row["yoy_delta_pp"],
            "weather_missing": row["weather_missing"],
            "reason": (f'{row["signal_count"]} of {row["comparisons_available"]} comparisons signal '
                       f'for {row["month_label"]}; importance to our airline: {importance_en}.'),
        })
    airports.sort(key=lambda item: (-item["signal_count"],
                                    -_IMPORTANCE_RANK[item["importance"]], item["own_pp"]))
    for rank, airport in enumerate(airports, start=1):
        airport["priority_rank"] = rank
    return {"month_mode": "fixed" if year is not None else "context",
            "airports": airports, "sim_label": SIM_LABEL}
