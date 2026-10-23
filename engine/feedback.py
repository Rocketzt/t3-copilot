"""Append-only human feedback with immutable organizer seeds."""

from __future__ import annotations

import json
from pathlib import Path

from .data import load_data

ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_PATH = ROOT / "data" / "feedback.jsonl"
SEED_PATH = ROOT / "data" / "feedback_seed.json"
RESULT_EN = {"接受": "Accept", "修改": "Edit", "拒绝": "Reject"}
FIELDS = ("event_id", "rec_id", "result", "reason", "final_action", "outcome", "improvement", "reviewer", "date")


def _seeds(path: Path = SEED_PATH) -> list[dict]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [{**r, "result": RESULT_EN.get(r["result"], r["result"]), "source": "organizer_seed"} for r in rows]


def load_records(path: str | Path | None = None) -> list[dict]:
    target = Path(path) if path is not None else FEEDBACK_PATH
    records = _seeds()
    if target.exists():
        with target.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Invalid feedback JSONL line {line_no}") from exc
    return records


def append_record(record: dict, path: str | Path | None = None) -> dict:
    from .facts import redact_text

    target = Path(path) if path is not None else FEEDBACK_PATH
    clean = {key: redact_text(str(record.get(key) or "")) for key in FIELDS}
    clean["result"] = RESULT_EN.get(clean["result"], clean["result"])
    if clean["result"] not in ("Accept", "Edit", "Reject"):
        raise ValueError("result must be Accept, Edit, or Reject")
    if not clean["event_id"] or not clean["rec_id"]:
        raise ValueError("event_id and rec_id are required")
    if any(r["rec_id"] == clean["rec_id"] for r in load_records(target)):
        raise ValueError("Duplicate feedback rec_id")
    clean["source"] = "app"
    if record.get("rule_ids"):
        clean["rule_ids"] = list(record["rule_ids"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(clean, ensure_ascii=False) + "\n")
    return clean


def match(factsheet_or_event: dict, triggered_rules: list[dict] | list[str] | None = None,
          path: str | Path | None = None) -> list[dict]:
    event = factsheet_or_event.get("event", factsheet_or_event)
    event_id = event.get("id") or event.get("event_id")
    airport = event.get("airport")
    rules = {r["id"] if isinstance(r, dict) else r for r in (triggered_rules or [])}
    event_airports = {e["id"]: e["airport"] for e in load_data().events}
    return [r for r in load_records(path) if r["event_id"] == event_id or
            (airport and event_airports.get(r["event_id"]) == airport) or
            bool(rules.intersection(r.get("rule_ids", [])))]
