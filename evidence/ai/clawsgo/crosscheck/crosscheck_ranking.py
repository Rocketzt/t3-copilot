#!/usr/bin/env python3
"""Independent cross-check of Track 3 Data.xlsx -> ranking CSV, check report, chart.

SIMULATED / 模拟 — every airport and number in the workbook is fictional.

Reads only "Track 3 Data.xlsx". Writes to exports/:
  crosscheck_ranking.csv   one row per airport-month, ranked
  crosscheck_report.md     Step 1 checks, Step 3 counts, top 15, surprises
  hailing_vs_yunchuan.png  1200x640 chart

Run from the repo root:  python scripts/crosscheck_ranking.py
Requires pandas, openpyxl, matplotlib (see requirements.txt).

Field mapping (sheet 01):
  E 按计划完成航班的比例        completion rate (fraction)
  F 机场放行正常比例            release rate — NOT used
  G 同类机场平均比例            same-size average (fraction)
  H 该机场过去12个月平均比例     own 12-month average (fraction)
  I 与自身平均差（百分点）       own gap, already in percentage points

Column "tier" in the CSV holds 航空公司业务重要程度 (高/中/低) from sheet 02,
because it is the third ranking key. Airport size class is compared via column G.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "Track 3 Data.xlsx"
OUT = ROOT / "exports"

SHEET_BASE = "01_机场月度运行基线"
SHEET_SCALE = "02_机场年度规模"
SHEET_WEATHER = "03_机场天气月度"

TOL_PP = 0.005  # tolerance for the two identity checks, in percentage points
GAP_THRESHOLD = -5.00  # a signal fires at or below this many percentage points

VERDICT = {0: "normal", 1: "watch", 2: "unusual", 3: "clearly unusual"}
IMPORTANCE_ORDER = {"高": 3, "中": 2, "低": 1}

# Colour-blind-safe palette (Okabe-Ito)
C_BLUE = "#0072B2"
C_ORANGE = "#D55E00"
C_GREY = "#555555"
C_SHADE = "#D9D9D9"


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = pd.read_excel(WORKBOOK, sheet_name=SHEET_BASE)
    scale = pd.read_excel(WORKBOOK, sheet_name=SHEET_SCALE)
    weather = pd.read_excel(WORKBOOK, sheet_name=SHEET_WEATHER)
    for df, name in ((base, "01"), (weather, "03")):
        df["月序"] = df["年份"] * 12 + df["月份"]
    return base, scale, weather


def check_rows(base, scale, weather) -> dict:
    """Step 1a plus structural integrity: duplicates and blanks in the used columns."""
    e_col, g_col, h_col, i_col = base.columns[[4, 6, 7, 8]]
    return {
        "base_rows": len(base),
        "scale_rows": len(scale),
        "weather_rows": len(weather),
        "base_airports": base["机场名称"].nunique(),
        "base_months": base["月序"].nunique(),
        "dup_base": int(base.duplicated(["年份", "月份", "机场名称"]).sum()),
        "dup_weather": int(weather.duplicated(["年份", "月份", "机场名称"]).sum()),
        "na_used": int(base[[e_col, g_col, h_col, i_col]].isna().sum().sum()),
    }


def check_own_gap(base) -> pd.DataFrame:
    """Step 1b: does I == (E - H) * 100?"""
    e_col, h_col, i_col = base.columns[[4, 7, 8]]
    out = base[["年份", "月份", "机场名称", e_col, h_col, i_col]].copy()
    out["recomputed"] = (out[e_col] - out[h_col]) * 100
    out["diff_pp"] = out[i_col] - out["recomputed"]
    return out[out["diff_pp"].abs() > TOL_PP].reset_index(drop=True)


def check_peer_avg(base) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Step 1c: does G == mean of E over same-size airports in the same month?"""
    e_col, g_col = base.columns[[4, 6]]
    out = base.copy()
    out["peer_mean"] = out.groupby(["年份", "月份", "机场分类"])[e_col].transform("mean")
    out["diff_pp"] = (out[g_col] - out["peer_mean"]) * 100
    return out[out["diff_pp"].abs() > TOL_PP].reset_index(drop=True), out


def check_weather(weather) -> pd.DataFrame:
    """Step 1d: weather rows flagged 是 (missing)."""
    return weather.loc[
        weather["是否缺少数据"] == "是", ["年份", "月份", "机场名称"]
    ].reset_index(drop=True)


def build_table(base, scale, weather) -> pd.DataFrame:
    """Step 2: gaps, signals, verdict, confidence for all 192 airport-months."""
    e_col, g_col, h_col, i_col = base.columns[[4, 6, 7, 8]]

    df = base[
        ["年份", "月份", "机场名称", "机场分类", e_col, g_col, h_col, i_col]
    ].copy()
    df.columns = [
        "year", "month", "airport", "size_class", "completion", "peer_avg",
        "own_avg12", "own_gap_pp",
    ]
    df["month_label"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

    # Importance: 2025 rows of sheet 02 (constant per airport across both years).
    imp = (
        scale.loc[scale["年份"] == 2025, ["机场名称", "航空公司业务重要程度"]]
        .rename(columns={"机场名称": "airport", "航空公司业务重要程度": "tier"})
        .set_index("airport")["tier"]
    )
    df["tier"] = df["airport"].map(imp)
    missing_tier = df.loc[df["tier"].isna(), "airport"].unique().tolist()
    if missing_tier:
        raise ValueError(f"no 2025 importance row for: {missing_tier}")

    # Peer gap.
    df["peer_delta_pp"] = (df["completion"] - df["peer_avg"]) * 100

    # Year-on-year: same airport, same month of 2024. Blank for 2024 rows.
    prev = df.loc[df["year"] == 2024, ["airport", "month", "completion"]].rename(
        columns={"completion": "completion_2024"}
    )
    df = df.merge(prev, on=["airport", "month"], how="left")
    df["yoy_delta_pp"] = np.where(
        df["year"] == 2025, (df["completion"] - df["completion_2024"]) * 100, np.nan
    )

    # Weather flag, joined on airport-month.
    wflag = weather[["年份", "月份", "机场名称", "是否缺少数据"]].rename(
        columns={"年份": "year", "月份": "month", "机场名称": "airport"}
    )
    df = df.merge(wflag, on=["year", "month", "airport"], how="left", validate="1:1")
    df["weather_missing"] = df["是否缺少数据"].fillna("否")

    # Signals: one per available comparison at or below the threshold.
    df["sig_own"] = df["own_gap_pp"] <= GAP_THRESHOLD
    df["sig_peer"] = df["peer_delta_pp"] <= GAP_THRESHOLD
    df["sig_yoy"] = df["yoy_delta_pp"].notna() & (df["yoy_delta_pp"] <= GAP_THRESHOLD)
    df["signal_count"] = df[["sig_own", "sig_peer", "sig_yoy"]].sum(axis=1).astype(int)
    df["verdict"] = df["signal_count"].map(VERDICT)

    # Confidence: -0.15 per unavailable comparison, -0.10 if that month's weather is missing.
    df["unavailable"] = (
        df["own_gap_pp"].isna().astype(int)
        + df["peer_delta_pp"].isna().astype(int)
        + df["yoy_delta_pp"].isna().astype(int)
    )
    df["confidence"] = (
        1.0
        - 0.15 * df["unavailable"]
        - 0.10 * (df["weather_missing"] == "是").astype(int)
    ).round(4)
    return df


def rank(df: pd.DataFrame) -> pd.DataFrame:
    """Step 3: signals desc, own gap most negative first, importance 高 > 中 > 低."""
    out = df.copy()
    out["_imp"] = out["tier"].map(IMPORTANCE_ORDER)
    out = out.sort_values(
        ["signal_count", "own_gap_pp", "_imp", "year", "month", "airport"],
        ascending=[False, True, False, True, True, True],
    ).reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out.drop(columns="_imp")


def write_csv(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    cols = [
        "airport", "year", "month", "month_label", "tier", "completion",
        "peer_avg", "own_avg12", "delta_pp", "peer_delta_pp", "yoy_delta_pp",
        "signal_count", "verdict", "confidence", "weather_missing",
    ]
    out = pd.DataFrame(
        {
            "airport": df["airport"],
            "year": df["year"].astype(int),
            "month": df["month"].astype(int),
            "month_label": df["month_label"],
            "tier": df["tier"],
            "completion": df["completion"].round(4),
            "peer_avg": df["peer_avg"].round(4),
            "own_avg12": df["own_avg12"].round(4),
            # Fixed 2 dp as text so values like -6.20 keep both decimals.
            "delta_pp": df["own_gap_pp"].map(lambda v: f"{v:.2f}" if pd.notna(v) else ""),
            "peer_delta_pp": df["peer_delta_pp"].map(lambda v: f"{v:.2f}" if pd.notna(v) else ""),
            "yoy_delta_pp": df["yoy_delta_pp"].map(lambda v: f"{v:.2f}" if pd.notna(v) else ""),
            "signal_count": df["signal_count"],
            "verdict": df["verdict"],
            "confidence": df["confidence"].map(lambda v: f"{v:.2f}"),
            "weather_missing": df["weather_missing"],
        }
    )[cols]
    out.to_csv(path, index=False, encoding="utf-8-sig", float_format=None, na_rep="")
    return out


def make_chart(df: pd.DataFrame, path: Path) -> None:
    """Hailing vs Yunchuan monthly completion, large-airport average, Jul-Aug 2025 shaded."""
    ap_h, ap_y = "海陵国际机场", "云川国际机场"
    fig, ax = plt.subplots(figsize=(12, 6.4), dpi=100)

    months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    x = np.arange(len(months))

    for name, colour, label in (
        (ap_h, C_BLUE, "海陵国际机场 Hailing"),
        (ap_y, C_ORANGE, "云川国际机场 Yunchuan"),
    ):
        s = (
            df.loc[df["airport"] == name]
            .sort_values(["year", "month"])
            .reset_index(drop=True)
        )
        ax.plot(x, s["completion"] * 100, color=colour, lw=2.2, marker="o", ms=4,
                label=label, zorder=3)

    large = (
        df.loc[df["size_class"] == "大型机场"]
        .groupby(["year", "month"])["peer_avg"]
        .first()
        .reset_index()
        .sort_values(["year", "month"])
    )
    ax.plot(x, large["peer_avg"] * 100, color=C_GREY, lw=1.8, ls="--",
            label="大型机场平均 Large-airport average (G)", zorder=2)

    # Shade July and August 2025.
    july = list(months).index(pd.Timestamp("2025-07-01"))
    ax.axvspan(july - 0.5, july + 1.5, color=C_SHADE, alpha=0.55, zorder=1,
               label="2025 年 7–8 月 Jul–Aug 2025")

    ax.set_xticks(x[::2])
    ax.set_xticklabels([m.strftime("%Y-%m") for m in months][::2], rotation=45, ha="right",
                       fontsize=9)
    ax.set_xlim(-0.6, len(months) - 0.4)
    ax.set_ylabel("按计划完成航班比例 (%)  Completion rate (%)")
    ax.set_xlabel("月份 Month")
    ax.grid(axis="y", color="#DDDDDD", lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    lo = min(df["completion"].min(), df["peer_avg"].min()) * 100
    hi = max(df["completion"].max(), df["peer_avg"].max()) * 100
    ax.set_ylim(np.floor(lo - 2), np.ceil(hi + 2))

    ax.set_title(
        "Monthly completion rate — 海陵 vs 云川, 2024-01 to 2025-12\n"
        "SIMULATED / 模拟 — fictional airports and values, Track 3 Data.xlsx",
        fontsize=13, loc="left", pad=12,
    )
    ax.legend(loc="lower left", fontsize=9, frameon=False, ncol=2)
    fig.text(0.99, 0.015, "SIMULATED / 模拟", ha="right", va="bottom", fontsize=10,
             color="#8B0000", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8B0000", lw=0.8))

    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)

    # Flatten the alpha channel so the PNG opens the same everywhere.
    try:
        from PIL import Image

        with Image.open(path) as im:
            im.convert("RGB").save(path)
    except ImportError:
        pass


def md_table(df: pd.DataFrame, cols: dict[str, str]) -> str:
    head = "| " + " | ".join(cols.values()) + " |"
    sep = "|" + "|".join(["---"] * len(cols)) + "|"
    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if pd.isna(v):
                cells.append("—")
            elif c in ("delta_pp", "own_gap_pp", "peer_delta_pp", "yoy_delta_pp"):
                cells.append(f"{v:+.2f}")
            elif c in ("completion", "peer_avg", "own_avg12", "按计划完成航班的比例",
                       "该机场过去12个月平均比例", "同类机场平均比例", "recomputed", "peer_mean",
                       "E", "H", "G"):
                cells.append(f"{v:.4f}")
            elif c in ("diff_pp", "与自身平均差（百分点）"):
                cells.append(f"{v:+.4f}")
            elif c == "I":
                cells.append(f"{v:+.2f}")
            elif c == "confidence":
                cells.append(f"{v:.2f}")
            else:
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([head, sep] + rows)


def write_report(
    path: Path,
    checks: dict,
    bad_b: pd.DataFrame,
    bad_c: pd.DataFrame,
    bad_c_tight: pd.DataFrame,
    weather_bad: pd.DataFrame,
    df: pd.DataFrame,
    ranked: pd.DataFrame,
    csv: pd.DataFrame,
) -> None:
    own_hits = df["own_gap_pp"] <= GAP_THRESHOLD
    n_own = int(own_hits.sum())
    n_own_ja = int((own_hits & df["month"].isin([7, 8])).sum())
    dist = df["signal_count"].value_counts().reindex([0, 1, 2, 3], fill_value=0)
    n_sig = int((df["signal_count"] > 0).sum())
    top = ranked.head(15)
    b_max = bad_b["diff_pp"].abs().max() if len(bad_b) else 0.0
    c_max = bad_c["diff_pp"].abs().max() if len(bad_c) else 0.0
    yc = df[(df["airport"] == "云川国际机场") & (df["month_label"] == "2025-07")].iloc[0]
    peer_yc, own_yc = yc["peer_delta_pp"], yc["own_gap_pp"]
    yoy_only = df[df["sig_yoy"] & ~df["sig_own"] & ~df["sig_peer"]]
    yoy_only_txt = (
        f"**{'One' if len(yoy_only) == 1 else len(yoy_only)} row flags on YoY alone** — "
        + ", ".join(
            f"{r.airport} {r.month_label} (own {r.own_gap_pp:+.2f} pp)"
            for r in yoy_only.itertuples()
        )
        + "; an I-only ranking misses it."
        if len(yoy_only)
        else "**No row flags on YoY alone.**"
    )

    def rows_bad(frame: pd.DataFrame, rename: dict[str, str], extra: dict[str, str]) -> str:
        if frame.empty:
            return "_none_"
        d = frame.rename(columns=rename).copy()
        d["month_label"] = d["月份"].astype(str).str.zfill(2)
        d["month_label"] = frame["年份"].astype(str) + "-" + d["month_label"]
        return md_table(d, extra)

    report = f"""# Cross-check report — Track 3 Data.xlsx

**SIMULATED / 模拟.** Fictional values, `Track 3 Data.xlsx` only; computed by
`scripts/crosscheck_ranking.py`, read from `exports/crosscheck_ranking.csv`.

## 1. Data checks

| Check | Result |
|---|---|
| a) Rows — 01_机场月度运行基线 | {checks['base_rows']} ({checks['base_airports']} airports × {checks['base_months']} months) |
| a) Rows — 02_机场年度规模 | {checks['scale_rows']} (8 airports × 2 years) |
| a) Rows — 03_机场天气月度 | {checks['weather_rows']} |
| Structural | duplicate airport-months: {checks['dup_base']} in sheet 01, {checks['dup_weather']} in sheet 03; blanks in E/G/H/I: {checks['na_used']} |
| b) I = (E − H) × 100 | {len(bad_b)} of {checks['base_rows']} rows differ by more than {TOL_PP} pp |
| c) G = same-size mean of E | {len(bad_c)} of {checks['base_rows']} rows differ by more than {TOL_PP} pp ({len(bad_c_tight)} at a {2 * TOL_PP:.3f} pp tolerance) |
| d) Weather rows marked 是 | {len(weather_bad)} |

**b) I vs (E − H) × 100** — largest difference {b_max:.2f} pp (I stored to 2 dp):

{rows_bad(bad_b, {'机场名称': 'airport', '按计划完成航班的比例': 'E', '该机场过去12个月平均比例': 'H', '与自身平均差（百分点）': 'I'}, {'month_label': 'month', 'airport': 'airport', 'E': 'E', 'H': 'H', 'I': 'I', 'recomputed': '(E−H)×100', 'diff_pp': 'diff (pp)'})}

**c) G vs recomputed same-size mean** — largest difference {c_max:.4f} pp (4-decimal rounding);
{len(bad_c_tight)} at {2 * TOL_PP:.3f} pp:

{rows_bad(bad_c, {'机场名称': 'airport', '机场分类': 'class', '同类机场平均比例': 'G'}, {'month_label': 'month', 'airport': 'airport', 'class': 'class', 'G': 'G', 'peer_mean': 'mean of E', 'diff_pp': 'diff (pp)'})}

**d) Rows with 是否缺少数据 = 是**

{md_table(weather_bad.assign(month_label=weather_bad['年份'].astype(str) + '-' + weather_bad['月份'].astype(str).str.zfill(2)), {'month_label': 'month', '机场名称': 'airport'})}

Nothing was corrected; I and G used as stored.

## 2. Step 3 counts

| Measure | Value |
|---|---|
| Rows with own_gap_pp ≤ −5.00 | {n_own} |
| … of those in July or August (any year) | {n_own_ja} |
| Rows with at least one signal | {n_sig} |
| Signal count distribution 0 / 1 / 2 / 3 | {dist[0]} / {dist[1]} / {dist[2]} / {dist[3]} |
| Rows with yoy_delta_pp blank (2024, comparison unavailable) | {int(df['yoy_delta_pp'].isna().sum())} |
| Confidence values present | {', '.join(f'{c:.2f} ({n} rows)' for c, n in df['confidence'].value_counts().sort_index().items())} |

{n_sig} rows carry a signal; ranks {n_sig + 1}–15 show 0. Top: **{ranked.iloc[0]['airport']} {ranked.iloc[0]['month_label']}**, 3 signals (own {ranked.iloc[0]['own_gap_pp']:+.2f}, peer {ranked.iloc[0]['peer_delta_pp']:+.2f}, YoY {ranked.iloc[0]['yoy_delta_pp']:+.2f} pp), confidence {ranked.iloc[0]['confidence']:.2f}.

## 3. Top 15 rows

Sort: signal_count ↓, own_gap_pp ↑, tier 高>中>低.

{md_table(top, {'rank': '#', 'airport': 'airport', 'month_label': 'month', 'tier': 'tier', 'completion': 'completion', 'own_gap_pp': 'own_pp', 'peer_delta_pp': 'peer_pp', 'yoy_delta_pp': 'yoy_pp', 'signal_count': 'signals', 'verdict': 'verdict', 'confidence': 'conf.'})}

## 4. Surprises

1. **H is seeded with E in 2024-01** (I = 0 for all 8 airports); 2024 H averages only the months so far, so
2024 gaps rest on 0–11 months.
2. **All 96 2024 rows have confidence 0.85** (no YoY).
3. **{n_own_ja} of {n_own} own-gap flags fall in July or August** — an association only; the workbook cannot
show weather caused any drop.
4. **No missing-weather month is flagged**, so that flag never meets a signal.
5. {yoy_only_txt}
6. **The large class has 2 airports**, so G inherits the other: 云川 2025-07 peer {peer_yc:+.2f} pp, own
{own_yc:+.2f} pp.
"""
    path.write_text(report, encoding="utf-8")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    base, scale, weather = load()

    checks = check_rows(base, scale, weather)
    bad_b = check_own_gap(base)
    bad_c, _ = check_peer_avg(base)
    bad_c_tight = bad_c[bad_c["diff_pp"].abs() > 2 * TOL_PP]
    weather_bad = check_weather(weather)

    df = build_table(base, scale, weather)
    ranked = rank(df)
    csv = write_csv(ranked, OUT / "crosscheck_ranking.csv")
    make_chart(df, OUT / "hailing_vs_yunchuan.png")
    write_report(OUT / "crosscheck_report.md", checks, bad_b, bad_c, bad_c_tight,
                 weather_bad, df, ranked, csv)

    print(f"rows 01/02/03: {checks['base_rows']}/{checks['scale_rows']}/{checks['weather_rows']}")
    print(f"b) I != (E-H)*100 : {len(bad_b)} rows")
    print(f"c) G != peer mean : {len(bad_c)} rows (>0.005pp), {len(bad_c_tight)} at >0.01pp")
    print(f"d) weather 是     : {len(weather_bad)} rows")
    print("signal_count distribution:",
          df["signal_count"].value_counts().reindex([0, 1, 2, 3], fill_value=0).to_dict())
    print(f"own_gap <= -5.00  : {int((df['own_gap_pp'] <= GAP_THRESHOLD).sum())} rows, "
          f"{int(((df['own_gap_pp'] <= GAP_THRESHOLD) & df['month'].isin([7, 8])).sum())} in Jul/Aug")
    print("top 5:")
    print(ranked.head(5)[["airport", "month_label", "own_gap_pp", "peer_delta_pp",
                          "yoy_delta_pp", "signal_count"]].to_string(index=False))
    print(f"written: {OUT/'crosscheck_ranking.csv'}, {OUT/'crosscheck_report.md'}, "
          f"{OUT/'hailing_vs_yunchuan.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
