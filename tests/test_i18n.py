"""Language switch (EN / 中文): UI key coverage, bilingual pair integrity, static whitelist.

These tests are static/offline: they read the front-end files and the engine payloads, and never
touch the network. They are the guard rail for docs/planning/LANGUAGE_SWITCH_PLAN.md §9.
"""

import re
import unittest
from pathlib import Path

from engine import pipeline

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"
I18N_SOURCE = (STATIC / "i18n.js").read_text(encoding="utf-8")
INDEX_SOURCE = (STATIC / "index.html").read_text(encoding="utf-8")
APP_SOURCE = (STATIC / "app.js").read_text(encoding="utf-8")
SERVER_SOURCE = (ROOT / "app" / "server.py").read_text(encoding="utf-8")

KEY_LINE = re.compile(r'^\s{4}"([A-Za-z][A-Za-z0-9_.]*)"\s*:', re.M)


def ui_blocks():
    """Return (english keys, chinese keys) from the UI table in i18n.js."""
    start = I18N_SOURCE.index("const UI = {")
    end = I18N_SOURCE.index("const EXACT_ZH2EN")
    body = I18N_SOURCE[start:end]
    en_start = body.index("  en: {")
    zh_start = body.index("  zh: {")
    en_keys = KEY_LINE.findall(body[en_start:zh_start])
    zh_keys = KEY_LINE.findall(body[zh_start:])
    return en_keys, zh_keys


class UiKeyCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.en_keys, cls.zh_keys = ui_blocks()
        cls.en = set(cls.en_keys)
        cls.zh = set(cls.zh_keys)

    def test_both_languages_are_present_and_balanced(self):
        self.assertGreater(len(self.en), 100, "the UI table should cover the whole page")
        self.assertEqual(len(self.en_keys), len(self.en), "duplicate English key")
        self.assertEqual(len(self.zh_keys), len(self.zh), "duplicate Chinese key")
        self.assertEqual(self.en, self.zh, "English and Chinese tables must have the same keys")

    def test_every_html_key_exists(self):
        used = set(re.findall(r'data-i18n(?:-title|-placeholder|-aria)?="([^"]+)"', INDEX_SOURCE))
        self.assertTrue(used, "index.html should carry data-i18n attributes")
        self.assertEqual(sorted(used - self.en), [], "keys used in index.html but missing from UI")

    def test_every_js_key_exists(self):
        used = set(re.findall(r'\bt\("([A-Za-z][A-Za-z0-9_.]*)"', APP_SOURCE))
        self.assertTrue(used, "app.js should call t() for UI strings")
        self.assertEqual(sorted(used - self.en), [], "keys used in app.js but missing from UI")

    def test_i18n_module_exposes_the_contract(self):
        for name in ("getLang", "setLang", "t", "applyStatic", "pair", "bi",
                     "renderTr", "tr", "bilingualizeEntities"):
            self.assertRegex(I18N_SOURCE, r"function\s+" + name + r"\s*\(", name)

    def test_index_loads_i18n_before_app(self):
        i18n_pos = INDEX_SOURCE.find('<script src="i18n.js">')
        app_pos = INDEX_SOURCE.find('<script src="app.js">')
        self.assertGreaterEqual(i18n_pos, 0, "index.html must load i18n.js")
        self.assertGreater(app_pos, i18n_pos, "i18n.js must load before app.js")

    def test_no_hardcoded_english_left_in_static_headings_without_a_key(self):
        # every static <h1>/<h2> and tab button must carry data-i18n
        for pattern in (r"<h1[^>]*>", r"<h2[^>]*>", r'<button class="tab-btn[^"]*"[^>]*>'):
            for match in re.finditer(pattern, INDEX_SOURCE):
                tag = match.group(0)
                self.assertIn("data-i18n", tag, "missing data-i18n on: " + tag)


class BilingualPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bootstrap = pipeline.bootstrap()

    def test_events_carry_both_languages(self):
        expected = ("name", "name_zh", "time_text", "time_en", "weather_text", "weather_en",
                    "ops_text", "ops_en", "notes", "notes_en", "known", "known_en",
                    "unknown", "unknown_en", "airport", "airport_en",
                    "importance", "importance_en")
        for event in self.bootstrap["events"]:
            for field in expected:
                self.assertIn(field, event, "event missing " + field)
                self.assertTrue(str(event[field]).strip(), "event %s has empty %s" % (event["id"], field))

    def test_airports_and_rules_carry_both_languages(self):
        for airport in self.bootstrap["airports"]:
            self.assertTrue(airport.get("name"))
            self.assertTrue(airport.get("name_en"))
            self.assertTrue(airport.get("tier_en"))
        for rule in self.bootstrap["rules"]:
            for field in ("topic", "topic_en", "trigger", "trigger_en", "action", "action_en",
                          "escalate_to", "escalate_to_en"):
                self.assertTrue(str(rule.get(field, "")).strip(), "%s missing %s" % (rule["id"], field))

    def test_tests_carry_question_in_both_languages(self):
        for case in self.bootstrap["tests"]:
            self.assertTrue(case.get("question_en"))
            self.assertTrue(case.get("question_zh"))

    def test_analyze_fields_have_bilingual_labels_and_messages(self):
        result = pipeline.analyze("EVT001")
        fields = result["output"]["fields"]
        self.assertEqual(len(fields), 17)
        for field in fields:
            self.assertTrue(field.get("label_en"), field.get("key"))
            self.assertTrue(field.get("label_zh"), field.get("key"))
        messages = result["output"]["messages"]
        for key in ("ops", "airport", "passengers"):
            self.assertTrue(str(messages.get(key, "")).strip())


class TranslationTableTests(unittest.TestCase):
    def test_curated_tables_are_populated(self):
        self.assertGreater(len(re.findall(r'^\s{2}"', I18N_SOURCE, re.M)), 80,
                           "curated/UI tables should be substantial")
        # spot-check the reviewed tier for strings without an English twin in the payload
        self.assertIn('"不得声称一定延误"', I18N_SOURCE)
        self.assertIn('"Own 12-month average"', I18N_SOURCE)
        self.assertIn('"模拟 / SIMULATED - Internal operations note', I18N_SOURCE)

    def test_pattern_rules_cover_the_time_window(self):
        self.assertIn("第", I18N_SOURCE)
        self.assertIn("Day ", I18N_SOURCE)
        self.assertIn("completion", I18N_SOURCE)
        self.assertIn("detector signals", I18N_SOURCE)

    def test_entity_pairs_match_the_engine_table(self):
        from engine.i18n import AIRPORT_EN
        for zh_name, en_name in AIRPORT_EN.items():
            self.assertIn('"%s", "%s"' % (zh_name, en_name), I18N_SOURCE,
                          "JS airport pair missing for " + zh_name)


class StaticWhitelistTests(unittest.TestCase):
    def test_i18n_is_served(self):
        block = SERVER_SOURCE[SERVER_SOURCE.index("STATIC_FILES"):SERVER_SOURCE.index("CONTENT_TYPES")]
        self.assertIn('"/i18n.js": "i18n.js"', block)

    def test_only_the_whitelist_changed_in_server(self):
        self.assertEqual(SERVER_SOURCE.count('"/i18n.js": "i18n.js"'), 1)


if __name__ == "__main__":
    unittest.main()
