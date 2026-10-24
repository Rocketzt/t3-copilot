# ClawsGO detector cross-check — 模拟 / SIMULATED

Source: `evidence/ai/clawsgo/crosscheck/crosscheck_ranking.csv` (raw, unedited).
Compared with `engine.detector.compute_all()` using 0.02 pp tolerance.

- CSV rows: 192
- Detector rows: 192
- Rows checked by airport + year + month: 192
- Mismatches: 0

## Top 10 CSV ranking rows

| Rank | Airport | Month | Own pp | Peer pp | YoY pp | Signals | Weather missing |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 海陵国际机场 | 2025-07 | -15.62 | -5.46 | -11.48 | 3 | 否 |
| 2 | 海陵国际机场 | 2025-08 | -10.99 | -3.66 | -9.14 | 2 | 否 |
| 3 | 青岚机场 | 2025-08 | -6.49 | 0.54 | 0.21 | 1 | 否 |
| 4 | 临江机场 | 2024-07 | -6.36 | -1.26 | — | 1 | 否 |
| 5 | 青岚机场 | 2024-07 | -6.20 | 0.26 | — | 1 | 否 |
| 6 | 青岚机场 | 2024-08 | -6.18 | -1.60 | — | 1 | 否 |
| 7 | 高原机场 | 2025-02 | -6.10 | -4.14 | -1.14 | 1 | 否 |
| 8 | 云川国际机场 | 2025-07 | -6.07 | 5.47 | -0.80 | 1 | 否 |
| 9 | 云川国际机场 | 2025-08 | -5.94 | 3.66 | -3.10 | 1 | 否 |
| 10 | 北岭机场 | 2025-08 | -5.61 | -1.38 | -3.32 | 1 | 否 |

## Mismatches

None.

three independent implementations agree

