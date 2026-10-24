# D04 — Data and rules explanation

> 模拟 / SIMULATED — all airports, events and numbers are fictional (organizer data).

**Status:** Sections 1–2: Ziyu’s checked draft. Sections 3–6: Jason’s completion from `data/track3.json`, `engine/facts.py`, `engine/writer.py`, `engine/checker.py` and the fresh offline exam (21/21).

We are the operations assistant for **one fictional airline's disruption desk**. This document
explains to our own staff and to reviewers where every number we show comes from, and which
rules the assistant applies before it drafts anything.

## 1. The data we use (all simulated)

One organizer workbook (`Track 3 Data.xlsx`, 14 sheets), exported once to `data/track3.json`;
rebuilding the export reproduces the file exactly.

| Sheet | What we take from it | Rows |
|---|---|---:|
| 01 Monthly operating baseline | completion, release, own 12-month average, peer average, gap column | 192 |
| 02 Airports & airline business | size tier and **importance to our airline** (高/中/低) | 8 |
| 03 Monthly weather | precipitation, max wind, bad-weather days, missing-data flag | 192 |
| 04 Events (EVT001–EVT005) | time window, weather/ops text, importance, known/unknown | 5 |
| 05 Rules (RULE001–012) | triggers, checks, actions, escalation, forbidden actions | 12 |
| 07 Human feedback | 3 seed records (Accept / Edit / Reject + reason) | 3 |
| 08 Tests (TEST001–TEST015) | official acceptance questions | 15 |
| 09–12 | the 17 output fields, source list, data-quality notes, checklist | — |

- **8 airports × 24 months = 192 airport-months** (2024-01 → 2025-12).
- **Column I (与自身平均差) is already in percentage points.** We never multiply it by 100.
- **Four weather rows are marked missing** (values exist in the sheet but must not be used):
  Qinglan 2025-03, Gaoyuan 2025-09, Linjiang 2025-11, Hailing 2025-11. We never impute them;
  confidence drops and the output must say so (checker C10).
- Data sources are `SIM-BASE`, `SIM-SCALE`, `SIM-WEATHER`; rules are `RULE001–012`; events are
  `EVT001–005`. `REF-CAAC` / `REF-CMA` are reference-only and may never back a claim.

## 2. What counts as a disruption (our definition)

Three comparisons per airport-month; each fires a **signal** when it is **≤ −5.0 pp**:

1. **Own history** — completion vs the airport's own 12-month average (column I, already pp).
2. **Same-size peers** — completion minus the same-class average.
3. **Same month last year** — 2025 month vs the same 2024 month (2024 rows have no YoY).

| Signals | Verdict |
|---:|---|
| 0 | normal |
| 1 | watch |
| 2 | unusual |
| 3 | clearly unusual |

With fewer than 2 comparisons available the verdict is **"can't tell"** (never happens in this
24-month dataset; the rule is still in the code). **Confidence** = 1 − 0.15 × (3 − comparisons
available) − 0.1 × (weather missing).

Across the whole network today: **192 airport-months, 12 own-history flags, 13 airport-months
with ≥ 1 signal**, signal counts **179 / 11 / 1 / 1** — only **2** months are multi-signal.

**Worked example — Hailing International Airport 2025-07** (the planted anomaly):

| Comparison | Value | Signal |
|---|---:|---|
| Own history: 69.49% vs own average 85.11% | −15.62 pp | yes |
| Same-size peers | −5.46 pp | yes |
| Same month last year | −11.48 pp | yes |

3 signals → **clearly unusual**, confidence 1.0. Hailing 2025-08 follows at −10.99 / −3.66 /
−9.14 pp → 2 signals, **unusual**.

**The contrast — Yunchuan 2025-07:** own history −6.07 pp (a flag) but peers **+5.47 pp** and
YoY **−0.80 pp** → 1 signal, *watch*. Its July dip is **seasonal**, not a disruption: the
network's mean completion is 78.80% in July and 78.51% in August against 84.29% in March. We do
not escalate a seasonal dip. (Beiling 2025-12 is the opposite edge: it flags on **YoY alone**,
own −4.74 / peer −3.86 / YoY −5.59 pp → 1 signal, watch.)

## 3. The twelve organizer rules

This table copies the organizer records in `data/track3.json`; “Yes” and “No” reflect `manual_approval`. `engine/rules.py` applies deterministic event-text and detector conditions. RULE003 uses the own-history signal; RULE007 uses the decision words, as recorded in `docs/planning/ERRATA.md`.

| ID | Topic | Trigger | Action | Escalate to | Human approval | Forbidden |
|---|---|---|---|---|---|---|
| RULE001 | 信息不足 | 关键数据缺失或来源冲突 | 降低判断强度并列出缺失信息 | 运营负责人 | Yes | 不得发布确定性结论 |
| RULE002 | 天气风险 | 天气提示达到中高风险但尚无正式运行状态 | 准备监测清单与沟通草案 | 运行协调人员 | Yes | 不得声称航班一定延误 |
| RULE003 | 异常波动 | 当前指标低于过去十二个月平均五个百分点以上 | 标记为重点复核 | 运营分析人员 | No | 不得直接归因于天气 |
| RULE004 | 持续运行压力 | 上一时段表现下降且后续任务仍集中 | 按时间顺序列出核查事项 | 运营负责人 | Yes | 不得调整真实航班计划 |
| RULE005 | 旅客沟通 | 存在风险但没有正式航班状态 | 生成明确标注“草案”的提示 | 旅客服务负责人 | Yes | 不得作为正式通知自动发送 |
| RULE006 | 人工否决 | 专业人员拒绝建议 | 根据新事实调整建议并保留原记录 | 模型负责人 | Yes | 不得覆盖或删除人工意见 |
| RULE007 | 重大运行决定 | 涉及取消、放行、调度、维修或赔付 | 仅整理所需信息 | 相应专业负责人 | Yes | 不得自动作出决定 |
| RULE008 | 高风险升级 | 多个独立风险信号同时存在且影响范围可能扩大 | 建议升级并说明触发依据 | 运营负责人 | Yes | 不得跳过人工审批 |
| RULE009 | 引用要求 | 输出包含数字或正式状态 | 在输出中列出来源 | 输出复核人 | Yes | 不得无来源生成事实 |
| RULE010 | 模拟标识 | 使用模拟事件或模拟数值 | 统一标注“模拟” | 项目负责人 | No | 不得称为真实事件 |
| RULE011 | 隐私保护 | 输入包含旅客或员工个人信息 | 只使用汇总信息 | 数据负责人 | Yes | 不得保存个人敏感信息 |
| RULE012 | 停止条件 | 无法判断来源可靠性或出现安全相关问题 | 输出信息缺口和人工升级对象 | 运营负责人 | Yes | 不得继续给出确定建议 |

## 4. Facts, assumptions, unknowns and the checker

`engine/facts.py` builds a fact sheet before the writer drafts prose. Each fact has an ID, text and source. Every quotable numeric value also appears in `facts.numbers` with value, unit, display, source and fact ID. SIM-BASE supplies detector comparisons and signal counts; SIM-WEATHER supplies selected-month observations when present; event-text numbers are sourced to the event ID. Missing weather is disclosed, never imputed.

`facts.assumptions` is marked `[ASSUMPTION]`; `facts.unknowns` comes from the event; `facts.missing_data` records limits of the monthly data. Conflicting evidence yields “Can’t tell” and a verification action. PII is redacted, and decision requests in displayed event text are replaced by a neutral RULE007 notice.

The writer turns this bounded input into the fixed fields and distinct audience drafts. `engine/checker.py` evaluates every output against the fact sheet and returns `passed`, per-check status and failure details:

| Check | Implemented gate |
|---|---|
| C01 | all 17 fields present and non-empty |
| C02 | every number is within 0.01 of a fact-sheet value |
| C03 | every [FACT] tag cites a fact-sheet source |
| C04 | no committed-action wording and no assistant decisions outside f12 |
| C05 | passenger message is a draft, points to official channels, asserts no delay |
| C06 | ops, airport and passenger messages are pairwise distinct |
| C07 | no mobile numbers, ID numbers or email addresses |
| C08 | 模拟 present in f13, f14, f15 and f17 |
| C09 | f03 risk matches the fact-sheet conflict state |
| C10 | no undisclosed missing weather data |
| C11 | prior feedback mentioned in f10/f13 (or none exists) |
| C12 | no unhedged weather-causation claim |
| C13 | f12 lists cancellation, release, dispatch, maintenance and compensation |

The bad-writer demo inserts “20 points” into f05. It is absent from `facts.numbers`, so C02 blocks it; the fresh offline exam’s negative case passed. A checker pass is not human approval of operational advice.

## 5. The fixed seventeen-field output

These English and Chinese labels are from the implemented `engine/writer.py` mapping and match `CONTRACT.md` §6.

| Key | English label | Chinese label |
|---|---|---|
| f01 | Event ID | 事件编号 |
| f02 | Generated At | 生成时间 |
| f03 | Risk Level | 风险等级 |
| f04 | Airport & Time Window | 适用机场与时间 |
| f05 | Evidence | 判断依据 |
| f06 | Possible Impact | 可能影响 |
| f07 | Assumptions to Verify | 待核查假设 |
| f08 | Information Gaps | 信息缺口 |
| f09 | First Action | 第一步行动 |
| f10 | Follow-up Actions | 后续行动 |
| f11 | Escalation Conditions | 升级条件 |
| f12 | Decisions Requiring a Human | 必须人工决定事项 |
| f13 | Internal Ops Note | 内部运营提示 |
| f14 | Airport Coordination Message | 机场协调信息 |
| f15 | Passenger Message Draft | 旅客信息草案 |
| f16 | Cited Sources | 引用来源 |
| f17 | Output Status | 输出状态 |

f13 is for our operations staff; f14 asks the airport coordination team to confirm its information; f15 is a passenger draft for review. f12 reserves cancellation, release, dispatch, maintenance and compensation for qualified people.

## 6. Limits

- All organizer data is **模拟 / SIMULATED** and describes airport-month aggregates, not individual flights or live operating status.
- A monthly gap can prioritize verification, but cannot identify an affected flight, aircraft, crew member or gate. Weather association does not establish causation.
- Missing weather is disclosed with reduced confidence. Conflicting sources require “Can’t tell” and a check of update times and definitions.
- The offline exam passed 21/21 specified cases, including the fabricated-number negative case. Automated checks still need human review of tone, order and operational suitability.

## What we did not build

We did not connect live airline or airport feeds; validate flight-level causation; automate operational decisions; send passenger notices; or establish real-world performance. The default demo writer is offline and deterministic.
