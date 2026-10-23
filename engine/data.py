"""Standard-library access to the validated workbook export."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "track3.json"


@dataclass(frozen=True)
class Data:
    airports: list[dict]
    airport_names: list[str]
    baseline: list[dict]
    weather: list[dict]
    events: list[dict]
    rules: list[dict]
    tests: list[dict]
    feedback_seed: list[dict]
    field_defs: list[dict]
    data_quality: list[dict]
    checklist: list[dict]
    sources: dict[str, dict]
    meta: dict

    def by_airport(self, name: str) -> list[dict]:
        return [r for r in self.baseline if r["airport"] == name]


def load_data(path: str | Path | None = None) -> Data:
    source = Path(path) if path is not None else DATA_PATH
    payload = json.loads(source.read_text(encoding="utf-8"))
    return Data(**payload)
