"""Network priority view follows detector output and specified ordering."""

import unittest

from engine.data import load_data
from engine.detector import airport_context, compute_all
from engine.network import network_view


class NetworkViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.detector_rows = {(row["airport"], row["year"], row["month"]): row
                             for row in compute_all(cls.data)}

    def test_eight_airports_have_unique_consecutive_ranks(self):
        view = network_view(self.data)
        self.assertEqual(view["month_mode"], "context")
        self.assertEqual(view["sim_label"], "模拟 / SIMULATED")
        self.assertEqual(len(view["airports"]), 8)
        self.assertEqual(len({a["airport"] for a in view["airports"]}), 8)
        self.assertEqual([a["priority_rank"] for a in view["airports"]], list(range(1, 9)))
        self.assertEqual(view, network_view(self.data))

    def test_hailing_leads_in_context_and_fixed_july(self):
        context = network_view(self.data)
        fixed = network_view(self.data, 2025, 7)
        self.assertEqual(context["airports"][0]["airport"], "海陵国际机场")
        self.assertEqual(fixed["month_mode"], "fixed")
        self.assertEqual(fixed["airports"][0]["airport"], "海陵国际机场")
        self.assertTrue(all(a["month_label"] == "2025-07" for a in fixed["airports"]))

    def test_every_number_comes_from_selected_detector_row(self):
        importance_rank = {"高": 3, "中": 2, "低": 1}
        for args in ({}, {"year": 2025, "month": 7}, {"year": 2024, "month": 7}):
            view = network_view(self.data, **args)
            rows = view["airports"]
            self.assertEqual(rows, sorted(rows, key=lambda a: (
                -a["signal_count"], -importance_rank[a["importance"]], a["own_pp"])))
            for item in rows:
                context = airport_context(self.data, item["airport"], **args)
                row = self.detector_rows[(item["airport"], context["year"], context["month"])]
                self.assertEqual(item["month_label"], row["month_label"])
                for output_key, detector_key in (("signal_count", "signal_count"),
                                                 ("confidence", "confidence"),
                                                 ("own_pp", "delta_pp"),
                                                 ("peer_pp", "peer_delta_pp"),
                                                 ("yoy_pp", "yoy_delta_pp")):
                    self.assertEqual(item[output_key], row[detector_key])
                self.assertEqual(item["weather_missing"], row["weather_missing"])
                self.assertEqual(item["verdict"], row["verdict"])
                self.assertEqual(item["reason"],
                                 f'{row["signal_count"]} of {row["comparisons_available"]} comparisons signal '
                                 f'for {row["month_label"]}; importance to our airline: {item["importance_en"]}.')


if __name__ == "__main__":
    unittest.main()
