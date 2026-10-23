"""Small fake pipeline verifies grading without claiming official results."""

import unittest

from tests.runner import _call, grade_case, run_all


class FakePipeline:
    @staticmethod
    def ask(question, event=None, writer_mode="offline"):
        return {"answer": {"text": "Formal status is unknown; verify with a human. 模拟 / SIMULATED",
                           "sources": ["SIM-BASE"]}, "check": {"passed": True}}

    @staticmethod
    def analyze(event, writer_mode="offline"):
        if writer_mode == "bad":
            return {"check": {"passed": False, "failures": ["fabricated 20 points"]}}
        return {"output": {"messages": {"ops": "Operations", "airport": "Airport", "passengers": "Passengers"}},
                "check": {"passed": True}}


class RunnerSelfCheck(unittest.TestCase):
    def test_must_and_forbidden(self):
        case = {"id": "SELF", "group": "self", "type": "check", "question": "", "mode": "ask",
                "must": [r"unknown", r"SIM-BASE"], "must_not": [r"definitely delayed"]}
        self.assertEqual(grade_case(case, FakePipeline.ask(""))["result"], "pass")
        bad = {"answer": {"text": "Definitely delayed", "sources": []}, "check": {"passed": True}}
        result = grade_case(case, bad)
        self.assertEqual(result["result"], "fail")
        self.assertIn("forbidden pattern", result["error_note"])

    def test_checker_gate_and_negative(self):
        case = {"id": "SELF", "group": "self", "type": "check", "question": "", "mode": "ask",
                "must": [], "must_not": []}
        self.assertEqual(grade_case(case, {"answer": {"text": "safe"}, "check": {"passed": False}})["result"], "fail")
        negative = {**case, "id": "NEG001", "mode": "bad", "expect_blocked": True, "must": [r"20"]}
        self.assertEqual(grade_case(negative, _call(FakePipeline, negative, "offline"))["result"], "pass")

    def test_full_dispatch_without_real_pipeline(self):
        result = run_all(pipeline_module=FakePipeline)
        self.assertEqual(result["summary"]["total"], 21)
        self.assertEqual(result["summary"]["negative_pass"], 1)
        self.assertLess(result["summary"]["pass"], 21)  # Fake answers must not be reported as real passes.


if __name__ == "__main__":
    unittest.main()
