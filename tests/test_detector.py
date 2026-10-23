"""Workbook-derived detector invariants."""

import unittest
from collections import Counter

from engine.data import load_data
from engine.detector import airport_context, compute_all, ranking


class DetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.rows = compute_all(cls.data)
        cls.lookup = {(r["airport"], r["year"], r["month"]): r for r in cls.rows}

    def assert_points(self, actual, expected):
        self.assertAlmostEqual(actual, expected, delta=0.02)

    def test_counts_and_seasonality(self):
        self.assertEqual(len(self.rows), 192)
        own = [r for r in self.rows if r["delta_pp"] <= -5]
        self.assertEqual(len(own), 12)
        self.assertEqual(sum(r["month"] in (7, 8) for r in own), 11)
        self.assertEqual(dict(Counter(r["signal_count"] for r in self.rows)), {0: 179, 1: 11, 2: 1, 3: 1})
        self.assertEqual(ranking(self.data)["flags_any"], 13)

    def test_named_examples(self):
        examples = (
            ("海陵国际机场", 2025, 7, -15.62, -5.46, -11.48, 3),
            ("海陵国际机场", 2025, 8, -10.99, -3.66, -9.14, 2),
            ("云川国际机场", 2025, 7, -6.07, 5.47, -0.80, 1),
            ("北岭机场", 2025, 12, -4.74, -3.86, -5.59, 1),
        )
        for airport, year, month, own, peer, yoy, count in examples:
            with self.subTest(airport=airport, month=month):
                row = self.lookup[(airport, year, month)]
                self.assert_points(row["delta_pp"], own)
                self.assert_points(row["peer_delta_pp"], peer)
                self.assert_points(row["yoy_delta_pp"], yoy)
                self.assertEqual(row["signal_count"], count)

    def test_weather_missing_exactly_four(self):
        missing = {(r["airport"], r["year"], r["month"]) for r in self.rows if r["weather_missing"]}
        self.assertEqual(missing, {("青岚机场", 2025, 3), ("高原机场", 2025, 9),
                                   ("海陵国际机场", 2025, 11), ("临江机场", 2025, 11)})

    def test_context_marks_selected_month(self):
        context = airport_context(self.data, "海陵国际机场")
        self.assertEqual(context["month_label"], "2025-08")
        self.assertIn("Latest anomalous month", context["selection_reason"])


if __name__ == "__main__":
    unittest.main()
