# scripts/ — build and evidence scripts

These run once from the repo root. They may use the packages in `requirements.txt`; the app never imports them.

| Script | Output | Owner |
|---|---|---|
| `build_data.py` | `data/track3.json` | Jason |
| `crosscheck_detector.py` | `exports/crosscheck_detector.md`; compares our detector with the ClawsGO CSV and exits non-zero on an unexplained mismatch | Jason |
| `make_chart.py` | `exports/hailing_vs_yunchuan.png` and `exports/detector_stats.json` | Jonathan |

The filled Excel copies of the workbook (sheets 06 and 08) are cut from scope (ROLES.md).
