"""Compare the untouched ClawsGO CSV with the runtime detector, row by row."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.data import load_data  # noqa: E402
from engine.detector import compute_all  # noqa: E402

INPUT = ROOT / "evidence" / "ai" / "clawsgo" / "crosscheck" / "crosscheck_ranking.csv"
OUTPUT = ROOT / "exports" / "crosscheck_detector.md"
TOLERANCE_PP = 0.02
REQUIRED = {"airport", "year", "month", "delta_pp", "peer_delta_pp", "yoy_delta_pp", "signal_count", "weather_missing"}
PP_FIELDS = ("delta_pp", "peer_delta_pp", "yoy_delta_pp")


def _key(row: dict) -> tuple[str, int, int]:
    return row["airport"], int(row["year"]), int(row["month"])


def _pp(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def _compare(csv_row: dict, detector_row: dict) -> list[str]:
    differences = []
    for field in PP_FIELDS:
        try:
            actual, expected = _pp(csv_row[field]), _pp(detector_row[field])
        except (TypeError, ValueError) as exc:
            differences.append(f"{field}: invalid value ({exc})")
            continue
        if (actual is None) != (expected is None) or (actual is not None and abs(actual - expected) > TOLERANCE_PP + 1e-9):
            differences.append(f"{field}: CSV={actual!r}, detector={expected!r}")
    try:
        signals = int(csv_row["signal_count"])
    except (TypeError, ValueError):
        signals = None
    if signals != detector_row["signal_count"]:
        differences.append(f'signal_count: CSV={csv_row["signal_count"]!r}, detector={detector_row["signal_count"]!r}')
    weather_flag = csv_row["weather_missing"].strip()
    weather_missing = {"是": True, "否": False}.get(weather_flag)
    if weather_missing is None or weather_missing != detector_row["weather_missing"]:
        differences.append(f'weather_missing: CSV={weather_flag!r}, detector={detector_row["weather_missing"]!r}')
    return differences


def check(input_path: Path = INPUT, output_path: Path = OUTPUT) -> tuple[int, int]:
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")
        csv_rows = list(reader)
    detector_rows = compute_all(load_data())
    detector = {_key(row): row for row in detector_rows}
    if len(detector) != len(detector_rows):
        raise ValueError("Detector has duplicate airport-month keys")
    seen = set()
    mismatches: list[tuple[str, list[str], dict | None, dict | None]] = []
    checked = 0
    for row_number, csv_row in enumerate(csv_rows, start=2):
        try:
            key = _key(csv_row)
        except (KeyError, TypeError, ValueError) as exc:
            mismatches.append((f"CSV row {row_number}", [f"invalid airport/year/month key: {exc}"], csv_row, None))
            continue
        label = f"{key[0]} {key[1]}-{key[2]:02d}"
        if key in seen:
            mismatches.append((label, ["duplicate CSV key"], csv_row, detector.get(key)))
            continue
        seen.add(key)
        expected = detector.get(key)
        if expected is None:
            mismatches.append((label, ["CSV key absent from detector"], csv_row, None))
            continue
        checked += 1
        differences = _compare(csv_row, expected)
        if differences:
            mismatches.append((label, differences, csv_row, expected))
    for key in sorted(detector.keys() - seen):
        expected = detector[key]
        mismatches.append((f"{key[0]} {key[1]}-{key[2]:02d}", ["detector key absent from CSV"], None, expected))

    lines = ["# ClawsGO detector cross-check — 模拟 / SIMULATED", "",
             f"Source: `{input_path.relative_to(ROOT).as_posix()}` (raw, unedited).",
             f"Compared with `engine.detector.compute_all()` using {TOLERANCE_PP:.2f} pp tolerance.", "",
             f"- CSV rows: {len(csv_rows)}", f"- Detector rows: {len(detector_rows)}",
             f"- Rows checked by airport + year + month: {checked}",
             f"- Mismatches: {len(mismatches)}", "", "## Top 10 CSV ranking rows", "",
             "| Rank | Airport | Month | Own pp | Peer pp | YoY pp | Signals | Weather missing |",
             "|---:|---|---|---:|---:|---:|---:|---|"]
    for rank, row in enumerate(csv_rows[:10], start=1):
        label = row.get("month_label") or f'{row["year"]}-{int(row["month"]):02d}'
        lines.append(f'| {rank} | {row["airport"]} | {label} | {row["delta_pp"]} | {row["peer_delta_pp"]} | '
                     f'{row["yoy_delta_pp"] or "—"} | {row["signal_count"]} | {row["weather_missing"]} |')
    lines.extend(["", "## Mismatches", ""])
    if mismatches:
        for label, differences, csv_row, detector_row in mismatches:
            lines.extend([f"### {label}", "", *[f"- {item}" for item in differences], "",
                          "CSV row (full):", "", "```json",
                          json.dumps(csv_row, ensure_ascii=False, indent=2), "```", "",
                          "Detector row (full):", "", "```json",
                          json.dumps(detector_row, ensure_ascii=False, indent=2), "```", ""])
    else:
        lines.extend(["None.", "", "three independent implementations agree", ""])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checked, len(mismatches)


if __name__ == "__main__":
    checked_rows, mismatch_count = check()
    print(f"Rows checked: {checked_rows}; mismatches: {mismatch_count}")
    raise SystemExit(1 if mismatch_count else 0)
