"""Rules, source-backed facts, privacy, and append-only feedback."""

import json
import re
import tempfile
import unittest
from pathlib import Path

from engine.data import load_data
from engine.detector import compute_all
from engine.facts import build_factsheet, redact_text
from engine.feedback import append_record, load_records, match
from engine.rules import evaluate
from tests.own_events import OWN_EVENTS


class FactSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()

    def test_expected_risk_and_conflict(self):
        first = build_factsheet("EVT001", self.data)
        self.assertEqual(first["facts"]["risk"]["level"], "Medium")
        self.assertIn("ground-support", first["facts"]["first_action"])
        self.assertTrue(all(f["source"] for f in first["facts"]["facts"]))
        conflict = build_factsheet("EVT003", self.data)
        self.assertEqual(conflict["facts"]["risk"]["level"], "Can't tell")
        self.assertTrue(conflict["facts"]["conflict"])
        self.assertIn("update times", conflict["facts"]["first_action"])

    def test_rejection_lowers_risk_and_changes_first_action(self):
        sheet = build_factsheet("EVT005", self.data)
        self.assertEqual(sheet["facts"]["risk"]["level"], "Low")
        self.assertEqual(sheet["facts"]["first_action"], "confirm current resources")
        self.assertTrue(any(r["result"] == "Reject" for r in sheet["facts"]["feedback_matches"]))
        self.assertIn("RULE006", {r["id"] for r in sheet["rules"]})

    def test_isolated_live_feedback_records_are_recalled_without_rewriting_seed(self):
        path = Path(__file__).parent / "feedback_live_records.jsonl"
        before = build_factsheet("EVT005", self.data)
        after = build_factsheet("EVT005", self.data, feedback_path=path)
        self.assertEqual([r["rec_id"] for r in before["facts"]["feedback_matches"]], ["REC003"])
        self.assertEqual([r["rec_id"] for r in after["facts"]["feedback_matches"]],
                         ["REC003", "LIVE003"])
        self.assertEqual(after["facts"]["risk"], before["facts"]["risk"])
        self.assertEqual(after["facts"]["first_action"], "confirm current resources")

    def test_pii_is_redacted_from_facts(self):
        event = {"id": "CUSTOM", "airport": "海陵国际机场", "importance": "中", "time_text": "Tonight",
                 "weather_text": "heavy rain", "ops_text": "Passenger 张伟 13812345678, a@b.com, 12345678901234567X",
                 "notes": "", "known": "", "unknown": ""}
        sheet = build_factsheet(event, self.data)
        encoded = json.dumps(sheet, ensure_ascii=False)
        self.assertTrue(sheet["facts"]["pii_redacted"])
        for private in ("张伟", "13812345678", "a@b.com", "12345678901234567X"):
            self.assertNotIn(private, encoded)

    def test_chinese_names_after_passenger_are_redacted(self):
        event = {"id": "CUSTOM", "airport": "海陵国际机场", "importance": "中", "time_text": "Tonight",
                 "weather_text": "", "ops_text": "旅客张伟, 旅客：李雷; 旅客 王芳 asked for 旅客信息; 旅客赵敏表示担忧",
                 "notes": "", "known": "", "unknown": ""}
        sheet = build_factsheet(event, self.data)
        encoded = json.dumps(sheet, ensure_ascii=False)
        self.assertTrue(sheet["facts"]["pii_redacted"])
        for name in ("张伟", "李雷", "王芳", "赵敏"):
            self.assertNotIn(name, encoded)
        self.assertIn("旅客信息", redact_text("旅客信息"))

    def test_baseline_peer_and_yoy_numbers_match_every_month_fact(self):
        lookup = {(r["airport"], r["month_label"]): r for r in compute_all(self.data)}
        for event_id in ("EVT001", "EVT002", "EVT003", "EVT004", "EVT005"):
            sheet = build_factsheet(event_id, self.data)
            airport = sheet["event"]["airport"]
            for fact in sheet["facts"]["facts"]:
                if fact["source"] != "SIM-BASE":
                    continue
                label = re.search(r"20\d{2}-\d{2}", fact["text"]).group(0)
                row = lookup[(airport, label)]
                number_rows = [n for n in sheet["facts"]["numbers"] if n["fact_id"] == fact["id"]]
                self.assertIn(f'peer gap {row["peer_delta_pp"]:+.2f} pp', fact["text"])
                self.assertIn((row["peer_delta_pp"], "pp", "SIM-BASE"),
                              {(n["value"], n["unit"], n["source"]) for n in number_rows})
                if row["yoy_delta_pp"] is not None:
                    self.assertIn(f'YoY gap {row["yoy_delta_pp"]:+.2f} pp', fact["text"])
                    self.assertIn((row["yoy_delta_pp"], "pp", "SIM-BASE"),
                                  {(n["value"], n["unit"], n["source"]) for n in number_rows})
                else:
                    self.assertNotIn("YoY gap", fact["text"])
        hailing = build_factsheet("EVT001", self.data)
        august = next(f for f in hailing["facts"]["facts"] if f["source"] == "SIM-BASE" and "2025-08" in f["text"])
        self.assertIn("peer gap -3.66 pp; YoY gap -9.14 pp", august["text"])
        old = build_factsheet("EVT001", self.data, 2024, 7)
        selected = next(f for f in old["facts"]["facts"] if f["source"] == "SIM-BASE" and "2024-07" in f["text"])
        self.assertNotIn("YoY gap", selected["text"])

    def test_signal_count_is_whitelisted_for_every_quoted_month(self):
        lookup = {(r["airport"], r["month_label"]): r for r in compute_all(self.data)}
        for event_id in ("EVT001", "EVT002", "EVT003", "EVT004", "EVT005"):
            sheet = build_factsheet(event_id, self.data)
            airport = sheet["event"]["airport"]
            for fact in sheet["facts"]["facts"]:
                if fact["source"] != "SIM-BASE":
                    continue
                label = re.search(r"20\d{2}-\d{2}", fact["text"]).group(0)
                count = lookup[(airport, label)]["signal_count"]
                self.assertIn(f"{count} detector signals", fact["text"])
                self.assertIn((count, "signals", "SIM-BASE"),
                              {(n["value"], n["unit"], n["source"]) for n in sheet["facts"]["numbers"]
                               if n["fact_id"] == fact["id"]})
        old = build_factsheet("EVT001", self.data, 2024, 7)
        old_fact = next(f for f in old["facts"]["facts"] if f["source"] == "SIM-BASE" and "2024-07" in f["text"])
        self.assertIn("0 detector signals", old_fact["text"])
        self.assertTrue(any(n["value"] == 0 and n["unit"] == "signals" and n["fact_id"] == old_fact["id"]
                            for n in old["facts"]["numbers"]))

    def test_arabic_digits_in_each_event_text_field_are_whitelisted(self):
        event = {"id": "CUSTOM", "airport": "海陵国际机场", "importance": "中", "time_text": "99 hours",
                 "weather_text": "rain for 6 hours", "ops_text": "2 gates", "known": "3.5 crews",
                 "unknown": "4 aircraft", "notes": "5 updates"}
        sheet = build_factsheet(event, self.data)
        event_facts = [f for f in sheet["facts"]["facts"] if f["source"] == "CUSTOM"]
        event_numbers = [n for n in sheet["facts"]["numbers"] if n["source"] == "CUSTOM"]
        self.assertEqual({n["value"] for n in event_numbers}, {2, 3.5, 4, 5, 6})
        self.assertNotIn(99, {n["value"] for n in event_numbers})
        self.assertTrue(all(any(f["id"] == n["fact_id"] and str(n["display"]) in f["text"]
                                for f in event_facts) for n in event_numbers))

    def test_hostile_own005_decision_request_is_not_quoted(self):
        own005 = next(e for e in OWN_EVENTS if e["id"] == "OWN005")
        sheet = build_factsheet(own005["custom"], self.data)
        payload = json.dumps(sheet, ensure_ascii=False).lower()
        self.assertNotIn("weather caused it", payload)
        self.assertNotIn("cancel flight", payload)
        self.assertNotIn("张伟", payload)
        self.assertNotIn("13812345678", payload)
        self.assertIn("the event text requests an operational decision", payload)
        self.assertIn("RULE007", {rule["id"] for rule in sheet["rules"]})

    def test_selected_month_weather_numbers(self):
        sheet = build_factsheet("EVT001", self.data)
        fact = next(f for f in sheet["facts"]["facts"] if f["source"] == "SIM-WEATHER")
        weather = next(r for r in self.data.weather if (r["airport"], r["year"], r["month"]) ==
                       ("海陵国际机场", sheet["detector"]["year"], sheet["detector"]["month"]))
        self.assertIn(sheet["detector"]["month_label"], fact["text"])
        values = {(n["value"], n["unit"], n["source"]) for n in sheet["facts"]["numbers"] if n["fact_id"] == fact["id"]}
        self.assertEqual(values, {(weather["precipitation_mm"], "mm", "SIM-WEATHER"),
                                  (weather["max_wind_ms"], "m/s", "SIM-WEATHER"),
                                  (weather["bad_weather_days"], "days", "SIM-WEATHER")})

    def test_missing_weather_has_fact_but_no_weather_numbers(self):
        sheet = build_factsheet("EVT001", self.data, 2025, 11)
        weather_facts = [f for f in sheet["facts"]["facts"] if f["source"] == "SIM-WEATHER"]
        self.assertEqual(len(weather_facts), 1)
        self.assertIn("marked missing", weather_facts[0]["text"])
        self.assertFalse(any(n["source"] == "SIM-WEATHER" for n in sheet["facts"]["numbers"]))

    def test_rule003_own_only_and_rule007_words_only(self):
        event = {"id": "CUSTOM", "airport": "北岭机场", "ops_text": "ordinary operations", "weather_text": "", "notes": ""}
        sheet = build_factsheet(event, self.data, 2025, 12)
        ids = {r["id"] for r in sheet["rules"]}
        self.assertNotIn("RULE003", ids)  # Only YoY is below threshold.
        self.assertNotIn("RULE007", ids)
        event["ops_text"] = "dispatch request"
        self.assertIn("RULE007", {r["id"] for r in evaluate(self.data, event, sheet["detector"])})

    def test_append_only_feedback(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "feedback.jsonl"
            seed_count = len(load_records(path))
            record = {"event_id": "EVT005", "rec_id": "APP001", "result": "Reject", "reason": "verify resource",
                      "final_action": "continue monitoring", "outcome": "pending", "improvement": "recheck",
                      "reviewer": "Tester", "date": "2026-10-24"}
            first = append_record(record, path)
            initial_bytes = path.read_bytes()
            self.assertEqual(first["source"], "app")
            self.assertEqual(len(load_records(path)), seed_count + 1)
            record["rec_id"] = "APP002"
            append_record(record, path)
            self.assertTrue(path.read_bytes().startswith(initial_bytes))
            self.assertEqual(len(load_records(path)), seed_count + 2)
            self.assertTrue(any(r["rec_id"] == "APP001" for r in match({"id": "EVT005"}, path=path)))


if __name__ == "__main__":
    unittest.main()
