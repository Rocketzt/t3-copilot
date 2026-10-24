"""Deterministic checker for writer output against the fact sheet.

``check(output, facts)`` compares a CONTRACT §6 "output" object with the
fact-sheet facts dict (the ``facts`` block of ``fixtures/factsheet_EVT*.json``;
a whole fact-sheet dict is also accepted and unwrapped) and returns

    {"passed": bool,
     "checks": [{"id": "C01", "name": ..., "status": "pass|fail", "detail"}, ...],
     "failures": [{"id", "name", "detail"}, ...]}

A failing check names the offending text in its ``detail``. Pure standard
library, no LLM calls, no I/O: the same inputs always give the same result.

Masking rules for C02 (numbers must be whitelisted): IDs (``SIM-*``,
``RULE0xx``, ``EVT0xx``, ``TEST0xx``, ``REC0xx``, fact/field keys ``Fxx``),
dates (ISO, slash, Chinese, bare years), times, and list numbering are removed
before number extraction, so they are never treated as numeric claims.
"""

from __future__ import annotations

import re

FIELD_KEYS = [f"f{i:02d}" for i in range(1, 18)]
TOLERANCE = 0.01

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# C02: masked (replaced with a space) before numbers are extracted.
_MASKS = (
    re.compile(r"SIM-[A-Za-z]+"),                          # data source IDs
    re.compile(r"(?i)\b(?:RULE|EVT|TEST|REC)\d+\b"),       # organizer IDs
    re.compile(r"(?i)\bf\d{1,2}\b"),                       # fact IDs F01.. and field keys f01..
    re.compile(r"\d{4}-\d{1,2}(?:-\d{1,2})?"),             # ISO dates 2025-08, 2026-10-24
    re.compile(r"\d{4}/\d{1,2}(?:/\d{1,2})?"),             # slash dates 2025/8
    re.compile(r"\d{4}\s*年(?:\s*\d{1,2}\s*月)?(?:\s*\d{1,2}\s*日)?"),  # Chinese dates
    re.compile(r"\d{1,2}\s*月\s*\d{1,2}\s*日"),            # Chinese month-day
    re.compile(r"\b(?:19|20)\d{2}\b"),                     # bare years (period mentions)
    re.compile(r"第\s*\d+\s*天"),                          # 第4天
    re.compile(r"(?i)\bday\s*\d+\b"),                      # day 4
    re.compile(r"\d{1,2}:\d{2}"),                          # times 14:00
    re.compile(r"(?m)^\s*\d+\s*[.)、）]\s*"),               # list numbering at line starts
    re.compile(r"[(（]\s*\d+\s*[)）]"),                     # inline enumerators (1)
)
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

# C03
_FACT_TAG = re.compile(r"\[FACT:\s*([^\]]*)\]")

# C04
_COMMITTED = (
    re.compile(r"已取消|已发送|已放行|已通知"),
    re.compile(r"(?i)\b(?:has|have|had)\s+been\s+(?:cancelled|canceled|sent|released|dispatched)\b"),
)
_ASSISTANT_DECIDES = re.compile(
    r"(?i)\b(?:we|i|the\s+assistant|the\s+copilot|copilot)\s+"
    r"(?:will|shall|should|would|have|has|had|decide\w*|propose\w*|now)\s*"
    r"(?:to\s+)?(?:cancel|releas|dispatch|maintain|compensat)\w*")

# C05
_DELAY_AS_FACT = re.compile(
    r"(?i)\b(?:is|are|was|were|has\s+been|have\s+been|will\s+be)\s+(?:delayed|cancelled|canceled)\b")
_DELAY_AS_FACT_ZH = re.compile(r"(?<!可能)(?<!或)(?<!预计)(?:已延误|已取消|航班延误|航班取消)")
_DRAFT_WORD = re.compile(r"(?i)\bdraft\b|草案")
_OFFICIAL_CHANNELS = re.compile(r"(?i)official\s+channels|正式渠道|正式通知|以正式.{0,8}为准")

# C07 (same shapes as engine/facts.py)
_PII = (
    ("mobile number", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("ID number", re.compile(r"(?<!\d)\d{17}[\dXx](?!\w)")),
    ("email address", re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")),
)

# C08
_SIM_WORD = re.compile(r"模拟|SIMULATED", re.I)

# C09
_CANT_TELL = re.compile(r"(?i)can'?t\s+tell|cannot\s+tell|无法判断")

# C10
_WEATHER_MISSING_IN_FACTS = re.compile(
    r"(?i)weather[^;]{0,80}\b(?:missing|absent|imputed|unavailable|not available)\b")
_WEATHER_MISSING_IN_OUTPUT = re.compile(
    r"(?i)(?:weather|天气)[^。;\n]{0,60}(?:missing|absent|unavailable|not available|no data|缺失|缺少|无数据|未提供)"
    r"|(?:missing|absent|unavailable|not available|no data|缺失|缺少|无数据|未提供)[^。;\n]{0,40}(?:weather|天气)")

# C11
_FEEDBACK_MENTION = re.compile(r"(?i)\bfeedback\b|\bprior\b|\bprevious\b|\bearlier\b|反馈|此前|历史")

# C12: a causal claim stands unless a hedge word precedes it.
_CAUSAL = re.compile(
    r"(?i)\bweather\s+caused\b|\bcaused\s+by\s+weather\b|\bdue\s+to\s+(?:the\s+)?weather\b"
    r"|天气导致|因天气导致|由于天气")
_HEDGE = re.compile(
    r"(?i)\b(?:may|might|could|can|possibly|potential\w*|appear\w*|seem\w*|likely|uncertain\w*|not proven)\b"
    r"|可能|或许|也许")

# C13: the five human-decision categories (English or Chinese wording).
_DECISION_CATEGORIES = (
    ("cancellation", re.compile(r"(?i)cancell|取消")),
    ("release", re.compile(r"(?i)releas|放行")),
    ("dispatch", re.compile(r"(?i)dispatch|调度|派遣")),
    ("maintenance", re.compile(r"(?i)maintain|maintenance|维修|维护")),
    ("compensation", re.compile(r"(?i)compensat|赔付|赔偿")),
)

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _unwrap_output(output) -> dict:
    if not isinstance(output, dict):
        raise TypeError("output must be a dict in the CONTRACT §6 'output' shape")
    if "fields" not in output and isinstance(output.get("output"), dict):
        output = output["output"]          # a full pipeline payload was passed
    return output


def _facts_of(facts) -> dict:
    if not isinstance(facts, dict):
        raise TypeError("facts must be a dict")
    inner = facts.get("facts")
    if isinstance(inner, dict):            # a full fact sheet was passed
        facts = inner
    return facts


def _field_map(output) -> dict:
    raw = output.get("fields", [])
    if isinstance(raw, dict):
        return {str(key): str(value or "") for key, value in raw.items()}
    fields = {}
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict) and item.get("key"):
            fields[str(item["key"])] = str(item.get("value") or "")
    return fields


def _messages(output) -> dict:
    raw = output.get("messages", {})
    if not isinstance(raw, dict):
        raw = {}
    return {key: str(raw.get(key) or "") for key in ("ops", "airport", "passengers")}


def _scan_texts(fields: dict, messages: dict) -> list:
    texts = [(f"field {key}", value) for key, value in fields.items()]
    texts += [(f"message {key}", messages[key]) for key in ("ops", "airport", "passengers")]
    return texts


def _snippet(text: str, pos: int, width: int = 28) -> str:
    start = max(0, pos - width)
    end = min(len(text), pos + width)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end].strip() + suffix


def _mask(text: str) -> str:
    for pattern in _MASKS:
        text = pattern.sub(" ", text)
    return text


# ---------------------------------------------------------------------------
# Checks C01-C13: each returns a failure detail (naming the offending text)
# or None when the check passes.
# ---------------------------------------------------------------------------


def _c01(ctx) -> str | None:
    missing = [key for key in FIELD_KEYS if not ctx["fields"].get(key, "").strip()]
    return f"missing or empty field(s): {', '.join(missing)}" if missing else None


def _c02(ctx) -> str | None:
    allowed = [float(item["value"]) for item in ctx["facts"].get("numbers", []) or []
               if isinstance(item, dict) and isinstance(item.get("value"), (int, float))]
    problems = []
    for where, text in ctx["texts"]:
        for match in _NUMBER.finditer(_mask(text)):
            value = float(match.group())
            if any(abs(value - a) <= TOLERANCE for a in allowed):
                continue
            problems.append(
                f"unwhitelisted number {match.group()} in {where}: '{_snippet(text, match.start())}'")
    return "; ".join(problems) if problems else None


def _c03(ctx) -> str | None:
    allowed = set(ctx["facts"].get("sources", []) or [])
    problems = []
    for where, text in ctx["texts"]:
        for match in _FACT_TAG.finditer(text):
            source = match.group(1).strip()
            if source not in allowed:
                problems.append(f"{where}: [FACT: {source}] cites a source not in the fact sheet")
    return "; ".join(problems) if problems else None


def _c04(ctx) -> str | None:
    problems = []
    for where, text in ctx["texts"]:
        for pattern in _COMMITTED:
            for match in pattern.finditer(text):
                problems.append(f"{where}: committed-action wording '{match.group()}'")
    for where, text in ctx["texts"]:
        if where == "field f12":
            continue
        for match in _ASSISTANT_DECIDES.finditer(text):
            problems.append(f"{where}: the assistant decides to '{match.group()}' (only f12 may list these)")
    return "; ".join(problems) if problems else None


def _c05(ctx) -> str | None:
    passenger = ctx["fields"].get("f15", "") + "\n" + ctx["messages"]["passengers"]
    problems = []
    for pattern in (_DELAY_AS_FACT, _DELAY_AS_FACT_ZH):
        for match in pattern.finditer(passenger):
            problems.append(f"passenger message states a delay/cancellation as fact: '{match.group()}'")
    if not _DRAFT_WORD.search(passenger):
        problems.append('passenger message lacks "draft"/草案')
    if not _OFFICIAL_CHANNELS.search(passenger):
        problems.append('passenger message lacks an "official channels" phrase')
    return "; ".join(problems) if problems else None


def _c06(ctx) -> str | None:
    messages = ctx["messages"]
    for first, second in (("ops", "airport"), ("ops", "passengers"), ("airport", "passengers")):
        if messages[first].strip() == messages[second].strip():
            return f"messages '{first}' and '{second}' are identical"
    return None


def _c07(ctx) -> str | None:
    problems = []
    for where, text in ctx["texts"]:
        for label, pattern in _PII:
            for match in pattern.finditer(text):
                problems.append(f"{where}: PII {label} '{match.group()}'")
    return "; ".join(problems) if problems else None


def _c08(ctx) -> str | None:
    missing = [key for key in ("f13", "f14", "f15", "f17")
               if not _SIM_WORD.search(ctx["fields"].get(key, ""))]
    return f"模拟 label missing from {', '.join(missing)}" if missing else None


def _c09(ctx) -> str | None:
    if not ctx["facts"].get("conflict"):
        return None
    f03 = ctx["fields"].get("f03", "")
    if not _CANT_TELL.search(f03):
        return (f"fact sheet reports a source conflict but the f03 risk is not "
                f"Can't tell/无法判断: '{f03.strip()}'")
    return None


def _c10(ctx) -> str | None:
    entries = [str(item) for item in ctx["facts"].get("missing_data", []) or []
               if _WEATHER_MISSING_IN_FACTS.search(str(item))]
    if not entries:
        return None
    for _, text in ctx["texts"]:
        if _WEATHER_MISSING_IN_OUTPUT.search(text):
            return None
    return f"weather data is missing for the month but the output does not say so: {entries[0]}"


def _c11(ctx) -> str | None:
    if not ctx["facts"].get("feedback_matches"):
        return None
    mention = ctx["fields"].get("f10", "") + "\n" + ctx["fields"].get("f13", "")
    if not _FEEDBACK_MENTION.search(mention):
        return "prior feedback exists but neither f10 nor f13 mentions it"
    return None


def _c12(ctx) -> str | None:
    problems = []
    for where, text in ctx["texts"]:
        for match in _CAUSAL.finditer(text):
            prefix = text[max(0, match.start() - 30):match.start()]
            if not _HEDGE.search(prefix):
                problems.append(f"{where}: weather causal overclaim '{match.group()}'")
    return "; ".join(problems) if problems else None


def _c13(ctx) -> str | None:
    f12 = ctx["fields"].get("f12", "")
    missing = [name for name, pattern in _DECISION_CATEGORIES if not pattern.search(f12)]
    return f"f12 lacks human-decision categories: {', '.join(missing)}" if missing else None


_CHECKS = (
    ("C01", "All 17 fields present", _c01),
    ("C02", "Numbers traceable to the fact sheet", _c02),
    ("C03", "FACT tags cite known sources", _c03),
    ("C04", "No committed actions", _c04),
    ("C05", "Passenger message is a safe draft", _c05),
    ("C06", "Three distinct audience messages", _c06),
    ("C07", "No PII", _c07),
    ("C08", "模拟 label on f13/f14/f15/f17", _c08),
    ("C09", "Conflict shown as Can't tell", _c09),
    ("C10", "Missing weather data disclosed", _c10),
    ("C11", "Prior feedback mentioned", _c11),
    ("C12", "No weather causal overclaim", _c12),
    ("C13", "f12 lists the human decisions", _c13),
)

_PASS_DETAILS = {
    "C01": "all 17 fields present and non-empty",
    "C02": "every number is within 0.01 of a fact-sheet value",
    "C03": "every [FACT] tag cites a fact-sheet source",
    "C04": "no committed-action wording and no assistant decisions outside f12",
    "C05": "passenger message is a draft, points to official channels, asserts no delay",
    "C06": "ops, airport and passenger messages are pairwise distinct",
    "C07": "no mobile numbers, ID numbers or email addresses",
    "C08": "模拟 present in f13, f14, f15 and f17",
    "C09": "f03 risk matches the fact-sheet conflict state",
    "C10": "no undisclosed missing weather data",
    "C11": "prior feedback mentioned in f10/f13 (or none exists)",
    "C12": "no unhedged weather-causation claim",
    "C13": "f12 lists cancellation, release, dispatch, maintenance and compensation",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check(output, facts) -> dict:
    """Verify a writer output against the fact sheet; see the module docstring."""
    output = _unwrap_output(output)
    facts = _facts_of(facts)
    context = {"fields": _field_map(output), "facts": facts}
    context["messages"] = _messages(output)
    context["texts"] = _scan_texts(context["fields"], context["messages"])

    checks = []
    failures = []
    for cid, name, func in _CHECKS:
        detail = func(context)
        checks.append({"id": cid, "name": name,
                       "status": "fail" if detail else "pass",
                       "detail": detail if detail else _PASS_DETAILS[cid]})
        if detail:
            failures.append({"id": cid, "name": name, "detail": detail})
    return {"passed": not failures, "checks": checks, "failures": failures}
