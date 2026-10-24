# Cross-check report — Track 3 Data.xlsx

**SIMULATED / 模拟.** Fictional values, `Track 3 Data.xlsx` only; computed by
`scripts/crosscheck_ranking.py`, read from `exports/crosscheck_ranking.csv`.

## 1. Data checks

| Check | Result |
|---|---|
| a) Rows — 01_机场月度运行基线 | 192 (8 airports × 24 months) |
| a) Rows — 02_机场年度规模 | 16 (8 airports × 2 years) |
| a) Rows — 03_机场天气月度 | 192 |
| Structural | duplicate airport-months: 0 in sheet 01, 0 in sheet 03; blanks in E/G/H/I: 0 |
| b) I = (E − H) × 100 | 6 of 192 rows differ by more than 0.005 pp |
| c) G = same-size mean of E | 9 of 192 rows differ by more than 0.005 pp (0 at a 0.010 pp tolerance) |
| d) Weather rows marked 是 | 4 |

**b) I vs (E − H) × 100** — largest difference 0.01 pp (I stored to 2 dp):

| month | airport | E | H | I | (E−H)×100 | diff (pp) |
|---|---|---|---|---|---|---|
| 2024-03 | 南湾机场 | 0.8149 | 0.7906 | +2.42 | 2.4300 | -0.0100 |
| 2024-09 | 临江机场 | 0.8209 | 0.7976 | +2.32 | 2.3300 | -0.0100 |
| 2025-03 | 临江机场 | 0.8129 | 0.8077 | +0.51 | 0.5200 | -0.0100 |
| 2025-07 | 青岚机场 | 0.7870 | 0.8173 | -3.02 | -3.0300 | +0.0100 |
| 2025-08 | 临江机场 | 0.7515 | 0.8058 | -5.44 | -5.4300 | -0.0100 |
| 2025-09 | 临江机场 | 0.8097 | 0.8035 | +0.61 | 0.6200 | -0.0100 |

**c) G vs recomputed same-size mean** — largest difference 0.0067 pp (4-decimal rounding);
0 at 0.010 pp:

| month | airport | class | G | mean of E | diff (pp) |
|---|---|---|---|---|---|
| 2024-04 | 青岚机场 | 小型机场 | 0.8321 | 0.8320 | +0.0067 |
| 2024-04 | 临江机场 | 小型机场 | 0.8321 | 0.8320 | +0.0067 |
| 2024-04 | 高原机场 | 小型机场 | 0.8321 | 0.8320 | +0.0067 |
| 2024-07 | 北岭机场 | 中型机场 | 0.8128 | 0.8129 | -0.0067 |
| 2024-07 | 星湖机场 | 中型机场 | 0.8128 | 0.8129 | -0.0067 |
| 2024-07 | 南湾机场 | 中型机场 | 0.8128 | 0.8129 | -0.0067 |
| 2025-01 | 青岚机场 | 小型机场 | 0.7813 | 0.7814 | -0.0067 |
| 2025-01 | 临江机场 | 小型机场 | 0.7813 | 0.7814 | -0.0067 |
| 2025-01 | 高原机场 | 小型机场 | 0.7813 | 0.7814 | -0.0067 |

**d) Rows with 是否缺少数据 = 是**

| month | airport |
|---|---|
| 2025-03 | 青岚机场 |
| 2025-09 | 高原机场 |
| 2025-11 | 海陵国际机场 |
| 2025-11 | 临江机场 |

Nothing was corrected; I and G used as stored.

## 2. Step 3 counts

| Measure | Value |
|---|---|
| Rows with own_gap_pp ≤ −5.00 | 12 |
| … of those in July or August (any year) | 11 |
| Rows with at least one signal | 13 |
| Signal count distribution 0 / 1 / 2 / 3 | 179 / 11 / 1 / 1 |
| Rows with yoy_delta_pp blank (2024, comparison unavailable) | 96 |
| Confidence values present | 0.85 (96 rows), 0.90 (4 rows), 1.00 (92 rows) |

13 rows carry a signal; ranks 14–15 show 0. Top: **海陵国际机场 2025-07**, 3 signals (own -15.62, peer -5.46, YoY -11.48 pp), confidence 1.00.

## 3. Top 15 rows

Sort: signal_count ↓, own_gap_pp ↑, tier 高>中>低.

| # | airport | month | tier | completion | own_pp | peer_pp | yoy_pp | signals | verdict | conf. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 海陵国际机场 | 2025-07 | 高 | 0.6949 | -15.62 | -5.46 | -11.48 | 3 | clearly unusual | 1.00 |
| 2 | 海陵国际机场 | 2025-08 | 高 | 0.7316 | -10.99 | -3.66 | -9.14 | 2 | unusual | 1.00 |
| 3 | 青岚机场 | 2025-08 | 低 | 0.7545 | -6.49 | +0.54 | +0.21 | 1 | watch | 1.00 |
| 4 | 临江机场 | 2024-07 | 低 | 0.7458 | -6.36 | -1.26 | — | 1 | watch | 0.85 |
| 5 | 青岚机场 | 2024-07 | 低 | 0.7610 | -6.20 | +0.26 | — | 1 | watch | 0.85 |
| 6 | 青岚机场 | 2024-08 | 低 | 0.7524 | -6.18 | -1.60 | — | 1 | watch | 0.85 |
| 7 | 高原机场 | 2025-02 | 低 | 0.7288 | -6.10 | -4.14 | -1.14 | 1 | watch | 1.00 |
| 8 | 云川国际机场 | 2025-07 | 高 | 0.8042 | -6.07 | +5.47 | -0.80 | 1 | watch | 1.00 |
| 9 | 云川国际机场 | 2025-08 | 高 | 0.8048 | -5.94 | +3.66 | -3.10 | 1 | watch | 1.00 |
| 10 | 北岭机场 | 2025-08 | 中 | 0.7820 | -5.61 | -1.38 | -3.32 | 1 | watch | 1.00 |
| 11 | 临江机场 | 2025-08 | 低 | 0.7515 | -5.44 | +0.24 | -2.76 | 1 | watch | 1.00 |
| 12 | 云川国际机场 | 2024-07 | 高 | 0.8122 | -5.43 | +0.12 | — | 1 | watch | 0.85 |
| 13 | 北岭机场 | 2025-12 | 中 | 0.7849 | -4.74 | -3.86 | -5.59 | 1 | watch | 1.00 |
| 14 | 海陵国际机场 | 2024-07 | 高 | 0.8097 | -4.81 | -0.13 | — | 0 | normal | 0.85 |
| 15 | 高原机场 | 2025-08 | 低 | 0.7414 | -4.75 | -0.77 | -3.22 | 0 | normal | 1.00 |

## 4. Surprises

1. **H is seeded with E in 2024-01** (I = 0 for all 8 airports); 2024 H averages only the months so far, so
2024 gaps rest on 0–11 months.
2. **All 96 2024 rows have confidence 0.85** (no YoY).
3. **11 of 12 own-gap flags fall in July or August** — an association only; the workbook cannot
show weather caused any drop.
4. **No missing-weather month is flagged**, so that flag never meets a signal.
5. **One row flags on YoY alone** — 北岭机场 2025-12 (own -4.74 pp); an I-only ranking misses it.
6. **The large class has 2 airports**, so G inherits the other: 云川 2025-07 peer +5.47 pp, own
-6.07 pp.
