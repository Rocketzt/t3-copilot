"""Honest must/must-not grading against the shared engine pipeline."""

from __future__ import annotations

import importlib
import json
import re
from datetime import datetime, timezone

from .cases_official import official_cases
from .own_events import OWN_EVENTS


class PipelineUnavailable(RuntimeError):
    pass


def _output_text(payload: dict, mode: str) -> str:
    if mode == "ask":
        answer = payload.get("answer", {})
        return "\n".join([str(answer.get("text", "")), " ".join(answer.get("sources", []))])
    # An echoed hostile input is a real privacy failure.
    return json.dumps(payload, ensure_ascii=False, default=str)


def grade_case(case: dict, payload: dict) -> dict:
    text = _output_text(payload, case.get("mode", "ask"))
    failed = []
    evidence = []
    for pattern in case.get("must", []):
        match = re.search(pattern, text, re.I)
        if match is None:
            failed.append(f"missing required pattern: {pattern}")
        else:
            evidence.append(match.group(0))
    for pattern in case.get("must_not", []):
        match = re.search(pattern, text, re.I)
        if match is not None:
            failed.append(f"forbidden pattern: {pattern}")
            evidence.append(match.group(0))
    check = payload.get("check", {})
    if case.get("expect_blocked"):
        if check.get("passed") is not False:
            failed.append("bad writer was not blocked")
    elif check.get("passed") is not True:
        failed.append("pipeline checker did not pass")
    if case["id"] == "TEST006":
        messages = payload.get("output", {}).get("messages", {})
        if len(set(messages.get(k, "") for k in ("ops", "airport", "passengers"))) != 3:
            failed.append("audience messages are not distinct")
    return {"id": case["id"], "group": case["group"], "type": case["type"],
            "question": case["question"], "expected": case.get("expected", "; ".join(case.get("must", []))),
            "forbidden": case.get("forbidden", "; ".join(case.get("must_not", []))),
            "result": "pass" if not failed else "fail", "evidence": evidence,
            "error_note": "; ".join(failed), "fix_note": ""}


def _call(pipeline, case: dict, writer_mode: str) -> dict:
    event = case.get("custom") or case.get("event_id")
    mode = case.get("mode", "ask")
    if mode == "bad":
        return pipeline.analyze(event, writer_mode="bad")
    if mode == "analyze":
        return pipeline.analyze(event, writer_mode=writer_mode)
    return pipeline.ask(case["question"], event=event, writer_mode=writer_mode)


def run_all(writer_mode: str = "offline", pipeline_module=None) -> dict:
    if pipeline_module is None:
        try:
            pipeline_module = importlib.import_module("engine.pipeline")
        except ImportError as exc:
            raise PipelineUnavailable("pipeline not available") from exc
    cases = official_cases() + OWN_EVENTS
    cases = [{**c, "mode": "analyze" if c["id"] == "TEST006" else c["mode"]} for c in cases]
    runs = []
    for case in cases:
        try:
            payload = _call(pipeline_module, case, writer_mode)
            runs.append(grade_case(case, payload))
        except Exception as exc:
            runs.append({"id": case["id"], "group": case["group"], "type": case["type"],
                         "question": case["question"], "expected": case.get("expected", ""),
                         "forbidden": case.get("forbidden", ""), "result": "fail", "evidence": [],
                         "error_note": f"pipeline error: {type(exc).__name__}: {exc}", "fix_note": ""})
    def passed(group: str) -> int:
        return sum(r["result"] == "pass" for r in runs if r["group"] == group)
    return {"summary": {"pass": sum(r["result"] == "pass" for r in runs), "total": len(runs),
                        "official_pass": passed("official"), "official_total": 15,
                        "own_pass": passed("own"), "own_total": 5,
                        "negative_pass": passed("negative"), "negative_total": 1},
            "runs": runs, "generated_at": datetime.now(timezone.utc).isoformat(), "writer_mode": writer_mode}
