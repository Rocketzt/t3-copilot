# scripts/ — build and evidence scripts

These run once from the repo root. They may use the packages in `requirements.txt`; the app never imports them.

| Script | Output | Owner |
|---|---|---|
| `build_data.py` | `data/track3.json` | Ziyu |
| `crosscheck_detector.py` | `exports/crosscheck_detector.md`; exits non-zero on any mismatch | Jonathan |
| `make_chart.py` | `exports/hailing_vs_yunchuan.png` and `exports/detector_stats.json` | Jonathan |
| `build_excel_exports.py` | `exports/filled_sheet06.xlsx` and `exports/filled_sheet08.xlsx` (copies of the workbook) | Jonathan |
