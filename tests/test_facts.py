"""Rules, source-backed facts, privacy, and append-only feedback."""

import json
import tempfile
import unittest
from pathlib import Path

from engine.data import load_data
from engine.facts import build_factsheet
from engine.feedback import append_record, load_records, match
from engine.rules import evaluate


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

    def test_pii_is_redacted_from_facts(self):
        event = {"id": "CUSTOM", "airport": "海陵国际机场", "importance": "中", "time_text": "Tonight",
                 "weather_text": "heavy rain", "ops_text": "Passenger 张伟 13812345678, a@b.com, 12345678901234567X",
                 "notes": "", "known": "", "unknown": ""}
        sheet = build_factsheet(event, self.data)
        encoded = json.dumps(sheet, ensure_ascii=False)
        self.assertTrue(sheet["facts"]["pii_redacted"])
        for private in ("张伟", "13812345678", "a@b.com", "12345678901234567X"):
            self.assertNotIn(private, encoded)

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
