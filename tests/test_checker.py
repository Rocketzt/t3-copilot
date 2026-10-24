"""Contract tests for engine.checker: a good output passes C01-C13, and each
check fails on cue and names the offending text.

Jonathan's fixtures/output_*.json do not exist yet, so the good and bad
outputs are built inline in the CONTRACT §6 "output" shape, using only
numbers that appear in the corresponding factsheet's "numbers" list
(fixtures/factsheet_EVT001.json and factsheet_EVT003.json, Jason's real
fact sheets). The bad output carries the fabricated "20 points" number the
bad writer mode produces (CONTRACT §11).
"""

import copy
import json
import unittest
from pathlib import Path

from engine.checker import check

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
CHECK_IDS = [f"C{i:02d}" for i in range(1, 14)]


def _factsheet(event_id: str) -> dict:
    with open(FIXTURES / f"factsheet_{event_id}.json", encoding="utf-8") as handle:
        return json.load(handle)


def _fields(pairs) -> list:
    return [{"key": key, "label_en": "", "label_zh": "", "value": value} for key, value in pairs]


def _output(event_id: str, pairs, sources, messages) -> dict:
    return {"event_id": event_id, "generated_at": "2026-10-24 10:00", "mode": "offline",
            "fields": _fields(pairs), "sources": sources,
            "status": "Pending human review 待复核", "messages": messages}


_PASSENGER_DRAFT = ("模拟 / SIMULATED — Draft (草案): adverse weather may lead to possible "
                    "delays at Hailing International Airport. Please check official channels "
                    "for the latest flight status; this is a draft, not an official notice.")

GOOD_EVT001 = _output(
    "EVT001",
    [
        ("f01", "EVT001 (模拟 / SIMULATED)"),
        ("f02", "2026-10-24 10:00 simulated clock"),
        ("f03", "Medium / 中"),
        ("f04", "Hailing International Airport (海陵国际机场), day 4 afternoon; context month "
                "2025-08 (latest anomalous month)"),
        ("f05", "Hailing International Airport 2025-08: completion 73.16% versus own average "
                "84.15% (-10.99 pp) [FACT: SIM-BASE]; 2025-07 completion 69.49% (-15.62 pp) "
                "[FACT: SIM-BASE]; precipitation 111.6 mm, max wind 15 m/s [FACT: SIM-WEATHER]"),
        ("f06", "Possible completion pressure and possible passenger delays; per-flight impact "
                "is not proven [ASSUMPTION] monthly patterns may indicate risk but do not "
                "prove a current flight impact"),
        ("f07", "[ASSUMPTION] Monthly patterns may indicate risk but do not prove a current "
                "flight impact"),
        ("f08", "[UNKNOWN] Per-flight plans; aircraft rotation; crew and ground-support status"),
        ("f09", "Confirm ground-support capacity and the weather update time with airport "
                "coordination"),
        ("f10", "1. Recall the accepted prior feedback (check resources before escalating)\n"
                "2. Monitor completion 73.16% against the own average 84.15% [FACT: SIM-BASE]\n"
                "3. Keep the passenger message as a draft for human review"),
        ("f11", "Escalate to the operations lead if the updated weather data confirms strong "
                "rainfall, or if multiple independent risk signals appear (RULE008)"),
        ("f12", "Human decisions required: flight cancellation, release, dispatch, maintenance, "
                "and compensation approvals [RULE007]; the assistant does not take these actions"),
        ("f13", "模拟 / SIMULATED — Internal ops note: completion 73.16% versus own average "
                "84.15% (-10.99 pp) [FACT: SIM-BASE]; recall the accepted prior feedback "
                "(check resources before escalating); drafts only, no actions taken"),
        ("f14", "模拟 / SIMULATED — To airport coordination: confirm ground-support capacity "
                "and the latest weather update; Hailing International Airport 2025-08 "
                "completion 73.16%, own average 84.15%, gap -10.99 pp [FACT: SIM-BASE]; "
                "max wind 15 m/s, precipitation 111.6 mm [FACT: SIM-WEATHER]"),
        ("f15", _PASSENGER_DRAFT),
        ("f16", "EVT001, RULE002, RULE003, RULE004, RULE005, RULE006, RULE008, RULE009, "
                "RULE010, SIM-BASE, SIM-SCALE, SIM-WEATHER"),
        ("f17", "Pending human review 待复核 — 模拟 / SIMULATED"),
    ],
    ["EVT001", "RULE002", "RULE003", "RULE004", "RULE005", "RULE006", "RULE008", "RULE009",
     "RULE010", "SIM-BASE", "SIM-SCALE", "SIM-WEATHER"],
    {
        "ops": "Operations: completion 73.16% versus own average 84.15% (-10.99 pp) "
               "[FACT: SIM-BASE]; verify ground-support capacity and the weather update time "
               "before any escalation; no committed actions, every decision requires a human",
        "airport": "Airport coordination: please confirm ground-support capacity and the latest "
                   "weather update for Hailing International Airport 2025-08; precipitation "
                   "111.6 mm, max wind 15 m/s [FACT: SIM-WEATHER]",
        "passengers": _PASSENGER_DRAFT,
    })

_EVT003_PASSENGER = ("模拟 / SIMULATED — Draft (草案): information is being verified at Yunchuan "
                     "International Airport; possible delays may occur. Please check official "
                     "channels for the latest flight status; this is a draft, not an official notice.")

GOOD_EVT003 = _output(
    "EVT003",
    [
        ("f01", "EVT003 (模拟 / SIMULATED)"),
        ("f02", "2026-10-24 10:00 simulated clock"),
        ("f03", "Can't tell / 无法判断 (sources conflict; verify update times and definitions)"),
        ("f04", "Yunchuan International Airport (云川国际机场), day 6 morning; context month 2025-08"),
        ("f05", "Yunchuan International Airport 2025-08: completion 80.48% versus own average "
                "86.42% (-5.94 pp) [FACT: SIM-BASE]; precipitation 125 mm, max wind 16.2 m/s "
                "[FACT: SIM-WEATHER]; sources conflict on the current status [FACT: EVT003]"),
        ("f06", "Possible indicator divergence between the two sources; per-flight impact is "
                "not proven [ASSUMPTION] monthly patterns may indicate risk but do not prove "
                "a current flight impact"),
        ("f07", "[ASSUMPTION] Monthly patterns may indicate risk but do not prove a current "
                "flight impact"),
        ("f08", "[UNKNOWN] Which source has completed review; whether the statistical "
                "definitions match"),
        ("f09", "Verify source update times and definitions"),
        ("f10", "1. Verify the update times and statistical definitions of both sources\n"
                "2. Monitor completion 80.48% against the own average 86.42% [FACT: SIM-BASE]\n"
                "3. Keep outputs as drafts for human review"),
        ("f11", "Escalate to the operations lead while the source conflict is unresolved "
                "(RULE001, RULE012)"),
        ("f12", "Human decisions required: flight cancellation, release, dispatch, maintenance, "
                "and compensation approvals [RULE007]; the assistant does not take these actions"),
        ("f13", "模拟 / SIMULATED — Internal ops note: sources conflict; completion 80.48% "
                "versus own average 86.42% (-5.94 pp) [FACT: SIM-BASE]; hold firm conclusions; "
                "drafts only, no actions taken"),
        ("f14", "模拟 / SIMULATED — To airport coordination: confirm which source has completed "
                "review; Yunchuan International Airport 2025-08 completion 80.48% "
                "[FACT: SIM-BASE]; max wind 16.2 m/s [FACT: SIM-WEATHER]"),
        ("f15", _EVT003_PASSENGER),
        ("f16", "EVT003, RULE001, RULE003, RULE004, RULE008, RULE009, RULE010, RULE012, "
                "SIM-BASE, SIM-SCALE, SIM-WEATHER"),
        ("f17", "Pending human review 待复核 — 模拟 / SIMULATED"),
    ],
    ["EVT003", "RULE001", "RULE003", "RULE004", "RULE008", "RULE009", "RULE010", "RULE012",
     "SIM-BASE", "SIM-SCALE", "SIM-WEATHER"],
    {
        "ops": "Operations: sources conflict; completion 80.48% versus own average 86.42% "
               "(-5.94 pp) [FACT: SIM-BASE]; verify update times and definitions before any "
               "conclusion; no committed actions, every decision requires a human",
        "airport": "Airport coordination: please confirm which source has completed review for "
                   "Yunchuan International Airport 2025-08; precipitation 125 mm, max wind "
                   "16.2 m/s [FACT: SIM-WEATHER]",
        "passengers": _EVT003_PASSENGER,
    })


class CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts_evt001 = _factsheet("EVT001")["facts"]
        cls.facts_evt003 = _factsheet("EVT003")["facts"]

    # -- helpers ------------------------------------------------------------

    def check_ids(self, result):
        return [entry["id"] for entry in result["checks"]]

    def failed_ids(self, result):
        return [entry["id"] for entry in result["checks"] if entry["status"] == "fail"]

    def detail_of(self, result, cid):
        return next(entry["detail"] for entry in result["checks"] if entry["id"] == cid)

    def assertOnlyFailure(self, result, cid):
        self.assertFalse(result["passed"])
        self.assertEqual(self.failed_ids(result), [cid])

    def variant(self, modifier, base=None, facts=None):
        output = copy.deepcopy(base or GOOD_EVT001)
        modifier(output)
        return check(output, copy.deepcopy(facts or self.facts_evt001))

    def set_field(self, output, key, value):
        next(item for item in output["fields"] if item["key"] == key)["value"] = value

    # -- good outputs -------------------------------------------------------

    def test_good_evt001_output_passes_every_check(self):
        result = check(copy.deepcopy(GOOD_EVT001), copy.deepcopy(self.facts_evt001))
        self.assertTrue(result["passed"])
        self.assertEqual(self.check_ids(result), CHECK_IDS)
        self.assertTrue(all(entry["status"] == "pass" for entry in result["checks"]))
        self.assertEqual(result["failures"], [])

    def test_good_evt003_conflict_output_passes_every_check(self):
        result = check(copy.deepcopy(GOOD_EVT003), copy.deepcopy(self.facts_evt003))
        self.assertTrue(result["passed"])
        self.assertEqual(self.failed_ids(result), [])

    # -- C02: the bad writer's fabricated number is blocked and named --------

    def test_c02_bad_output_fabricated_20_points_is_blocked(self):
        def inject(output):
            self.set_field(output, "f05", "Hailing International Airport 2025-08: completion "
                                          "fell by 20 points versus the own average "
                                          "[FACT: SIM-BASE].")
        result = self.variant(inject)
        self.assertOnlyFailure(result, "C02")
        self.assertEqual(result["failures"][0]["id"], "C02")
        self.assertIn("20", self.detail_of(result, "C02"))
        self.assertIn("f05", self.detail_of(result, "C02"))

    # -- one failing example per check C01, C03-C13 --------------------------

    def test_c01_field_missing_and_empty(self):
        def remove_f07(output):
            output["fields"] = [item for item in output["fields"] if item["key"] != "f07"]
        result = self.variant(remove_f07)
        self.assertOnlyFailure(result, "C01")
        self.assertIn("f07", self.detail_of(result, "C01"))

        def blank_f07(output):
            self.set_field(output, "f07", "   ")
        result = self.variant(blank_f07)
        self.assertOnlyFailure(result, "C01")

    def test_c03_fact_tag_cites_unknown_source(self):
        def bad_source(output):
            self.set_field(output, "f05", "Hailing International Airport 2025-08: completion "
                                          "73.16% versus own average 84.15% [FACT: SIM-CREW]")
        result = self.variant(bad_source)
        self.assertOnlyFailure(result, "C03")
        self.assertIn("SIM-CREW", self.detail_of(result, "C03"))

    def test_c04_committed_action_wording(self):
        def assistant_decides(output):
            self.set_field(output, "f09", "We will cancel the remaining flights this afternoon.")
        result = self.variant(assistant_decides)
        self.assertOnlyFailure(result, "C04")
        self.assertIn("cancel", self.detail_of(result, "C04"))

        def already_sent(output):
            output["messages"]["ops"] += " 已发送通知给旅客"
        result = self.variant(already_sent)
        self.assertOnlyFailure(result, "C04")
        self.assertIn("已发送", self.detail_of(result, "C04"))

    def test_c05_passenger_message_unsafe(self):
        def delay_as_fact(output):
            text = ("模拟 / SIMULATED — Your flight is delayed. Please check official channels "
                    "for the latest status. (draft)")
            self.set_field(output, "f15", text)
            output["messages"]["passengers"] = text
        result = self.variant(delay_as_fact)
        self.assertOnlyFailure(result, "C05")
        self.assertIn("delayed", self.detail_of(result, "C05"))

        def no_draft_no_channels(output):
            text = "模拟 / SIMULATED — Possible delays today at the airport."
            self.set_field(output, "f15", text)
            output["messages"]["passengers"] = text
        result = self.variant(no_draft_no_channels)
        self.assertOnlyFailure(result, "C05")
        self.assertIn("draft", self.detail_of(result, "C05"))
        self.assertIn("official channels", self.detail_of(result, "C05"))

    def test_c06_two_messages_identical(self):
        def duplicate(output):
            output["messages"]["airport"] = output["messages"]["ops"]
        result = self.variant(duplicate)
        self.assertOnlyFailure(result, "C06")
        self.assertIn("ops", self.detail_of(result, "C06"))
        self.assertIn("airport", self.detail_of(result, "C06"))

    def test_c07_pii_is_blocked(self):
        def email(output):
            self.set_field(output, "f06", "Possible completion pressure and possible passenger "
                                          "delays; contact the ops desk at ops-desk@example.com")
        result = self.variant(email)
        self.assertOnlyFailure(result, "C07")
        self.assertIn("email", self.detail_of(result, "C07"))

        def mobile(output):
            self.set_field(output, "f06", "Possible delays; passenger contact 13812345678")
        result = self.variant(mobile)
        self.assertIn("C07", self.failed_ids(result))          # C02 also fires: echoed digits
        self.assertIn("mobile", self.detail_of(result, "C07"))
        self.assertIn("C02", self.failed_ids(result))

        def id_number(output):
            self.set_field(output, "f06", "Possible delays; staff ID 310101199001011234")
        result = self.variant(id_number)
        self.assertIn("C07", self.failed_ids(result))
        self.assertIn("ID number", self.detail_of(result, "C07"))

    def test_c08_sim_label_missing(self):
        def strip_sim(output):
            self.set_field(output, "f17", "Pending human review 待复核")
        result = self.variant(strip_sim)
        self.assertOnlyFailure(result, "C08")
        self.assertIn("f17", self.detail_of(result, "C08"))

    def test_c09_conflict_not_shown_as_cant_tell(self):
        def medium_risk(output):
            self.set_field(output, "f03", "Medium / 中")
        result = self.variant(medium_risk, base=GOOD_EVT003, facts=self.facts_evt003)
        self.assertOnlyFailure(result, "C09")
        self.assertIn("f03", self.detail_of(result, "C09"))

    def test_c10_missing_weather_not_disclosed(self):
        facts = copy.deepcopy(self.facts_evt001)
        facts["missing_data"].append("Weather row missing for 海陵国际机场 2025-03; "
                                     "no weather value imputed")
        result = check(copy.deepcopy(GOOD_EVT001), facts)
        self.assertOnlyFailure(result, "C10")
        self.assertIn("weather", self.detail_of(result, "C10"))

        def disclose(output):
            self.set_field(output, "f14", "模拟 / SIMULATED — To airport coordination: the "
                                          "2025-03 weather record is missing, so no weather "
                                          "value is used; confirm ground-support capacity")
        result = self.variant(disclose, facts=facts)
        self.assertEqual(self.failed_ids(result), [])

    def test_c11_feedback_not_mentioned(self):
        def drop_feedback(output):
            self.set_field(output, "f10", "1. Monitor completion against the own average\n"
                                          "2. Keep the passenger message as a draft for human review")
            self.set_field(output, "f13", "模拟 / SIMULATED — Internal ops note: monitor "
                                          "completion; drafts only, no actions taken")
        result = self.variant(drop_feedback)
        self.assertOnlyFailure(result, "C11")
        self.assertIn("f10", self.detail_of(result, "C11"))

    def test_c12_weather_causal_overclaim(self):
        def overclaim(output):
            self.set_field(output, "f06", "The completion drop is due to the weather.")
        result = self.variant(overclaim)
        self.assertOnlyFailure(result, "C12")
        self.assertIn("due to the weather", self.detail_of(result, "C12"))

        def hedged(output):
            self.set_field(output, "f06", "The completion drop may be due to the weather; "
                                          "this is not proven.")
        result = self.variant(hedged)
        self.assertEqual(self.failed_ids(result), [])

    def test_c13_f12_lacks_decision_categories(self):
        def thin_f12(output):
            self.set_field(output, "f12", "Human review required for this event.")
        result = self.variant(thin_f12)
        self.assertOnlyFailure(result, "C13")
        for category in ("cancellation", "release", "dispatch", "maintenance", "compensation"):
            self.assertIn(category, self.detail_of(result, "C13"))

    # -- shape tolerance ----------------------------------------------------

    def test_accepts_full_pipeline_payload_and_fact_sheet(self):
        payload = {"event_id": "EVT001", "output": copy.deepcopy(GOOD_EVT001)}
        result = check(payload, _factsheet("EVT001"))
        self.assertTrue(result["passed"])
        self.assertEqual(self.check_ids(result), CHECK_IDS)
        self.assertEqual(len(result["checks"]), len(CHECK_IDS))


if __name__ == "__main__":
    unittest.main()
