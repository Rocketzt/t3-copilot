/* T3 Ops Copilot - vanilla JS front end (no dependencies, offline).
 *
 * Bilingual UI (EN / 中文): all display strings go through i18n.js (t/tr/pair/bi).
 * Translation is display-only: request payloads and stored records are unchanged.
 */
"use strict";

const SIM = "模拟 / SIMULATED";

const state = {
  bootstrap: null,
  selectedEvent: null,
  analysis: null,
  lastRequest: null,
  msgTab: "ops",
  showOriginalMsg: false,
  ranking: null,
  chart: null,
  network: null,
  exam: null,
  feedback: [],
  detectorLoaded: false,
  feedbackLoaded: false,
  health: null,
  engineMode: "fixtures",
};

/* ------------------------------------------------------------------ helpers */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function esc2(value) {
  return String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fmt(n, digits = 2) {
  if (n === null || n === undefined || n === "") return "—";
  const v = Number(n);
  if (!Number.isFinite(v)) return esc2(n);
  return v.toFixed(digits);
}

function signed(n, digits = 2) {
  if (n === null || n === undefined) return "—";
  const v = Number(n);
  return (v > 0 ? "+" : "") + v.toFixed(digits);
}

/* Plain (non-HTML) bilingual text for tooltips, status lines and <option> labels. */
function biText(en, zh) {
  const left = en ? String(en) : "";
  const right = zh ? String(zh) : "";
  if (!left && !right) return "";
  if (!right || left === right) return left;
  return getLang() === "zh" ? right + " · " + left : left + " · " + right;
}

/* Pair from an explicit field table, rendered with the 译 marker when translated. */
function pairHTML(obj, spec, opts) {
  return renderTr(pair(obj, spec), opts || {});
}

/* Translate + bilingual entities + 译 marker; `opts.rich` renders chips for tagged text. */
function trBi(value, opts) {
  const result = tr(value);
  result.text = bilingualizeEntities(result.text);
  return renderTr(result, opts || {});
}

const TAG_NAMES = ["ASSUMPTION", "UNKNOWN", "HUMAN"];

function tag(text) {
  const style = { assumption: "tag-assumption", unknown: "tag-unknown", human: "tag-human" }[String(text).toLowerCase()] || "";
  return `<span class="tag-chip ${style}">${esc2(text)}</span>`;
}

/* Human-readable English for labels the data layer still keeps in Chinese. */
function humanize(text) {
  return String(text === null || text === undefined ? "" : text)
    .replace(/大型机场/g, "Large")
    .replace(/中型机场/g, "Medium")
    .replace(/小型机场/g, "Small");
}

/* Strip one leading [TAG] (the caller re-adds it as a chip). */
function stripLeadingTag(text) {
  return String(text === null || text === undefined ? "" : text).replace(/^\s*\[(ASSUMPTION|UNKNOWN|HUMAN)\]\s*/i, "");
}

/* Collapse a run of identical leading tags, e.g. "[ASSUMPTION] [ASSUMPTION] x" -> "[ASSUMPTION] x". */
function collapseLeadingTags(text) {
  let out = String(text === null || text === undefined ? "" : text);
  TAG_NAMES.forEach((name) => {
    const re = new RegExp("^\\s*\\[" + name + "\\]\\s*(?:\\[" + name + "\\]\\s*)+", "i");
    out = out.replace(re, "[" + name + "] ");
  });
  return out;
}

function rich(text) {
  let html = esc2(collapseLeadingTags(humanize(text)));
  html = html.replace(/\[FACT:\s*([A-Za-z0-9_\-\s]+)\]/g,
    (m, src) => `<span class="tag-chip tag-fact" title="Fact source">FACT · ${esc2(src.trim())}</span>`);
  html = html.replace(/\[(ASSUMPTION|UNKNOWN|HUMAN)\]/g, (m, tk) => tag(tk));
  html = html.replace(/\n/g, "<br>");
  return html;
}

/* Verdict/level with both languages; missing twin uses the curated table. */
function biTermEn(en) {
  const zh = (typeof EXACT_EN2ZH !== "undefined" && EXACT_EN2ZH[en]) ? EXACT_EN2ZH[en] : "";
  return bi(en, zh);
}

async function api(path, options) {
  const opts = Object.assign({ headers: { "Content-Type": "application/json" } }, options || {});
  const res = await fetch(path, opts);
  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { error: text }; }
  if (!res.ok) {
    const err = new Error(data.error || `HTTP ${res.status}`);
    err.detail = data.detail || "";
    err.status = res.status;
    throw err;
  }
  return data;
}

function setStatus(target, message, kind) {
  const el = typeof target === "string" ? $(target) : target;
  if (!el) return;
  el.textContent = message || "";
  el.className = "status-line" + (kind ? " " + kind : "");
}

let toastTimer = null;
function toast(message, isError) {
  const el = $("#toast");
  el.textContent = message;
  el.className = "toast" + (isError ? " error" : "");
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 3200);
}

/* ------------------------------------------------------------------ tabs */
function switchTab(name) {
  $$(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  $$(".tab-panel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + name));
  if (name === "detector") loadDetector();
  if (name === "feedback") loadFeedback();
}

/* ------------------------------------------------------------------ bootstrap */
function renderEngineBadge(mode, health) {
  state.engineMode = String(mode || "fixtures");
  const badge = $("#engine-mode");
  if (badge) {
    badge.textContent = t("common.engine") + " " + state.engineMode;
    const meta = [];
    if (health && typeof health.checker_available === "boolean") {
      meta.push(t("assistant.checker") + " " + (health.checker_available ? "✓" : "✗"));
    }
    if (health && typeof health.runner_available === "boolean") {
      meta.push(t("exam.title") + " " + (health.runner_available ? "✓" : "✗"));
    }
    if (health && health.writer_mode) meta.push("writer: " + health.writer_mode);
    badge.title = meta.length ? meta.join(" · ") : "Mode reported by /api/health and /api/analyze";
  }
  const footer = $("#footer-mode");
  if (footer) footer.textContent = state.engineMode + " / " + t("common.offline");
}

function updateAssistantStatus() {
  const b = state.bootstrap;
  if (!b) return;
  if (state.analysis && state.analysis.event) {
    const ev = state.analysis.event;
    setStatus("#assistant-status", t("assistant.analyzed", {
      id: ev.id,
      airport: biText(ev.airport_en, ev.airport),
      mode: state.analysis.engine_mode || "fixture",
    }), "ok");
  } else {
    setStatus("#assistant-status", t("about.counts", {
      airports: b.counts.airports,
      months: b.counts.months,
      airportMonths: b.counts.airport_months,
      rules: b.counts.rules,
      tests: b.counts.tests,
      events: b.counts.events,
    }), "ok");
  }
}

async function init() {
  applyStatic(document);
  let health = null;
  try {
    state.bootstrap = await api("/api/bootstrap");
    try {
      health = await api("/api/health");
    } catch (e) {
      health = null; /* the badge falls back to bootstrap data; the page still works */
    }
  } catch (err) {
    setStatus("#assistant-status", t("assistant.analyzeFailed") + err.message, "error");
    return;
  }
  const b = state.bootstrap;
  state.health = health;
  const healthMode = health && health.engine === "ready" ? "real" : "fixtures";
  renderEngineBadge(healthMode, health || {
    checker_available: b.checker_available,
    runner_available: b.runner_available,
  });
  renderEventCards();
  renderAirportSelect();
  renderAskChips();
  renderAbout();
  updateAssistantStatus();

  /* deep links for demo/screenshots: ?tab=<name> and/or ?event=EVT00x (inert without params) */
  const params = new URLSearchParams(window.location.search);
  const tab = params.get("tab");
  if (tab && document.getElementById("tab-" + tab)) switchTab(tab);
  const eventId = params.get("event");
  if (eventId && (b.events || []).some((ev) => ev.id === eventId)) {
    selectEvent(eventId);
    analyzeEvent({ event_id: eventId, writer_mode: "offline" });
  }
}

function renderEventCards() {
  const b = state.bootstrap;
  if (!b) return;
  const wrap = $("#event-cards");
  wrap.innerHTML = "";
  b.events.forEach((ev) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "event-card";
    card.dataset.event = ev.id;
    const tagKey = ev.id === "EVT003" ? "assistant.tagConflict" : ev.id === "EVT005" ? "assistant.tagOverrule"
      : ev.id === "EVT004" ? "assistant.tagPassenger" : ev.id === "EVT002" ? "assistant.tagPressure" : "assistant.tagWeather";
    card.innerHTML = `
      <div class="eid">${esc2(ev.id)} · ${pairHTML(ev, { en: "time_en", zh: "time_text" })}</div>
      <div class="ename">${pairHTML(ev, { en: "name", zh: "name_zh" })}</div>
      <div class="emeta">${bi(ev.airport_en, ev.airport)} · ${esc2(t("assistant.importanceMeta"))} ${pairHTML(ev, { en: "importance_en", zh: "importance" })}</div>
      <span class="etag">${esc2(t(tagKey))}</span>`;
    if (ev.id === state.selectedEvent) card.classList.add("selected");
    card.addEventListener("click", () => selectEvent(ev.id));
    wrap.appendChild(card);
  });
}

function selectEvent(id) {
  state.selectedEvent = id;
  $$(".event-card").forEach((c) => c.classList.toggle("selected", c.dataset.event === id));
  const btn = $("#analyze-selected");
  if (btn) btn.disabled = false;
  const hint = $("#selected-hint");
  if (hint) hint.textContent = t("assistant.selectedPrefix") + id;
}

function renderAirportSelect() {
  const sel = $("#custom-airport");
  if (!sel) return;
  if (!state.bootstrap) return;
  sel.innerHTML = "";
  state.bootstrap.airports.forEach((ap) => {
    const opt = document.createElement("option");
    opt.value = ap.name;
    opt.textContent = biText(ap.name_en, ap.name) + " (" + biText(ap.tier_en, ap.tier) + ")";
    opt.title = t("assistant.airport") + ": " + biText(ap.name_en, ap.name);
    sel.appendChild(opt);
  });
}

function renderAskChips() {
  const wrap = $("#ask-chips");
  if (!wrap || !state.bootstrap) return;
  wrap.innerHTML = "";
  const tests = state.bootstrap.tests || [];
  tests.forEach((item) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "qchip";
    const q = pair(item, { en: "question_en", zh: "question_zh" });
    chip.textContent = q.text;
    chip.title = `${item.id} · ${item.question_en || ""}`;
    chip.addEventListener("click", () => askQuestion(item.question_en));
    wrap.appendChild(chip);
  });
}

function renderAbout() {
  const b = state.bootstrap;
  if (!b) return;
  $("#about-counts").textContent = t("about.counts", {
    airports: b.counts.airports,
    months: b.counts.months,
    airportMonths: b.counts.airport_months,
    rules: b.counts.rules,
    tests: b.counts.tests,
    events: b.counts.events,
  }) + " — " + t("sim.label");
  const dq = $("#about-dq");
  dq.innerHTML = (b.data_quality || []).map((d) => {
    const desc = tr(d.description || d.kind || "");
    desc.text = bilingualizeEntities(desc.text);
    return `<div class="fact-item"><strong>${esc2(d.id)}</strong> · ${renderTr(desc)}<br>
    <span class="hint">${esc2(t("about.dqHandling"))} ${trBi(d.handling || "—")} · ${esc2(t("about.dqStatus"))} ${trBi(d.status || "—")}</span></div>`;
  }).join("");
  const rules = $("#about-rules");
  rules.innerHTML = `
    <thead><tr><th>${esc2(t("about.rule"))}</th><th>${esc2(t("about.topic"))}</th><th>${esc2(t("about.trigger"))}</th>
      <th>${esc2(t("about.action"))}</th><th>${esc2(t("about.escalate"))}</th><th>${esc2(t("about.manual"))}</th></tr></thead>
    <tbody>${(b.rules || []).map((r) => `
      <tr><td class="num">${esc2(r.id)}</td>
      <td>${pairHTML(r, { en: "topic_en", zh: "topic" })}</td>
      <td>${pairHTML(r, { en: "trigger_en", zh: "trigger" })}</td>
      <td>${pairHTML(r, { en: "action_en", zh: "action" })}</td>
      <td>${pairHTML(r, { en: "escalate_to_en", zh: "escalate_to" })}</td>
      <td>${r.manual_approval ? esc2(t("common.yes")) : esc2(t("common.no"))}</td></tr>`).join("")}
    </tbody>`;
  const note = $("#lang-note");
  if (note) note.textContent = getLang() === "zh" ? "当前界面语言：中文。切换后无需刷新。" : "Current interface language: English. Switching needs no reload.";
}

/* ------------------------------------------------------------------ analyze */
async function analyzeEvent(payload) {
  setStatus("#assistant-status", t("assistant.analyzing"));
  const btn = payload.event_id ? $("#analyze-selected") : $("#analyze-custom");
  btn.disabled = true;
  try {
    const result = await api("/api/analyze", { method: "POST", body: JSON.stringify(payload) });
    state.analysis = result;
    state.lastRequest = payload;
    state.showOriginalMsg = false;
    renderResult(result);
    renderEngineBadge(result.engine_mode || "fixtures", state.health);
    updateAssistantStatus();
    $("#result").hidden = false;
    $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    setStatus("#assistant-status", t("assistant.analyzeFailed") + err.message + (err.detail ? " — " + err.detail : ""), "error");
  } finally {
    btn.disabled = false;
  }
}

function renderResult(result) {
  const facts = result.facts || {};
  const risk = facts.risk || {};
  const level = (risk.level || "medium").toLowerCase();
  const levelEn = risk.level_en || ({ low: "Low", medium: "Medium", high: "High", cant_tell: "Can't tell" }[level] || "Medium");
  const levelZh = risk.level_zh || "";
  $("#risk-card").className = "card risk-card " + level;
  $("#risk-card").innerHTML = `
    <div class="risk-head">
      <div>
        <div class="hint">${esc2(t("assistant.riskLevel"))}</div>
        <div class="risk-level">${bi(levelEn, levelZh)}</div>
      </div>
      <div class="risk-score">${esc2(t("assistant.score"))} ${fmt(risk.score, 2)}<br>${facts.conflict ? esc2(t("assistant.conflictFlag")) : esc2(result.engine_mode || "fixture")}</div>
    </div>
    <ul class="reason-list">${(risk.reasons || []).map((r) => `<li>${trBi(r.text)} <span class="src-chip">${esc2(r.source)}</span></li>`).join("")}</ul>
    <div class="disclaimer">${esc2(t("assistant.disclaimer"))} ${SIM}</div>`;

  renderDetectorCard(facts.detector || result.detector || {});
  renderFactsCard(facts);
  renderFields(result.output || {});
  renderMessages(result.output || {});
  renderChecker(result.check || {});
  renderFeedbackMatches(result.feedback_matches || []);
  $("#ask-answer").innerHTML = "";
}

function renderDetectorCard(det) {
  const comps = det.comparisons || [];
  const verdict = (det.verdict || "normal");
  const cls = verdict.indexOf("clearly") >= 0 ? "clearly" : verdict;
  $("#detector-card").innerHTML = `
    <div class="card-head">
      <h2>${esc2(t("assistant.detectorTitle"))}</h2>
      <span class="hint">${esc2(det.month_label || "")} · ${bi(det.airport_en, det.airport)}</span>
    </div>
    ${comps.map((c) => `
      <div class="compare-row">
        <div class="compare-label">${trBi(c.label || c.key)}</div>
        <div class="compare-detail">${trBi(c.detail || "")}</div>
        <div><span class="signal-chip ${c.signal ? "on" : "off"}">${esc2(c.signal ? t("assistant.signal") : t("assistant.noSignal"))} · ${signed(c.value_pp)} pp</span></div>
      </div>`).join("")}
    <div class="verdict-line">
      <span class="verdict-badge ${cls}">${biTermEn(verdict)}</span>
      <span class="hint">${esc2(t("assistant.comparisonsSignal", { on: det.signal_count || 0, total: det.comparisons_available || comps.length, conf: fmt(det.confidence, 2) }))}</span>
    </div>
    <p class="hint">${trBi(det.selection_reason || "")}${det.weather_missing ? " · " + esc2(t("assistant.weatherMissing")) : ""}</p>
    <p class="hint">${(det.confidence_notes || []).map((n) => trBi(n)).join(" · ")}</p>`;
}

function renderFactsCard(facts) {
  const factsList = facts.facts || [];
  const feedback = facts.feedback_matches || [];
  const section = (titleKey, items, tagName) => {
    if (!items || !items.length) return "";
    return `<div class="subhead">${esc2(t(titleKey))}</div><div class="fact-list">` +
      items.map((x) => `<div class="fact-item">${tagName ? tag(tagName) : ""}${trBi(humanize(stripLeadingTag(x)))}</div>`).join("") + `</div>`;
  };
  $("#facts-card").innerHTML = `
    <div class="card-head"><h2>${esc2(t("assistant.factSheet"))}</h2>
      <span class="hint">${esc2(t("assistant.factsHint", { n: factsList.length }))}</span></div>
    <div class="subhead">${esc2(t("assistant.facts"))}</div>
    <div class="fact-list">${factsList.map((f) => `
      <div class="fact-item"><span class="src-chip">${esc2(f.source)}</span>${trBi(humanize(f.text))}</div>`).join("") || '<div class="empty">' + esc2(t("assistant.noFacts")) + '</div>'}</div>
    ${section("assistant.assumptions", facts.assumptions, "ASSUMPTION")}
    ${section("assistant.unknowns", facts.unknowns, "UNKNOWN")}
    ${section("assistant.missingData", facts.missing_data, "UNKNOWN")}
    ${section("assistant.forbidden", facts.forbidden_actions, "")}
    <div class="subhead">${esc2(t("assistant.sources"))}</div>
    <div class="pill-list">${(facts.sources || []).map((s) => `<span class="pill">${esc2(s)}</span>`).join("")}</div>
    ${feedback.length ? `<div class="subhead">${esc2(t("assistant.priorFeedback"))}</div><div class="feedback-matches">${feedback.map(feedbackItem).join("")}</div>` : ""}`;
}

function renderFields(output) {
  const fields = output.fields || [];
  $("#fields-grid").innerHTML = fields.map((f) => `
    <div class="field-card">
      <div class="field-key">${esc2(f.key)}</div>
      <div class="field-label">${pairHTML(f, { en: "label_en", zh: "label_zh" })}</div>
      <div class="field-value">${trBi(f.value, { rich: rich })}</div>
    </div>`).join("") || '<div class="empty">' + esc2(t("assistant.noFields")) + '</div>';
}

function renderMessages(output) {
  const msgs = output.messages || {};
  const original = msgs[state.msgTab] || msgs.ops || "";
  const translated = tr(original);
  const shown = state.showOriginalMsg ? original : translated.text;
  $("#msg-body").textContent = shown;
  $$(".msg-tab").forEach((b) => b.classList.toggle("active", b.dataset.msg === state.msgTab));
  const hint = $("#msg-lang-hint");
  if (hint) {
    hint.innerHTML = esc2(t("assistant.msgHint")) +
      (translated.translated ? ' <span class="i18n-note">· ' + esc2(t("assistant.msgTranslated")) + " 译</span>" : "");
  }
  const toggle = $("#toggle-original");
  if (toggle) {
    toggle.hidden = !translated.translated;
    toggle.textContent = state.showOriginalMsg ? t("common.hideOriginal") : t("common.showOriginal");
  }
}

function renderChecker(check) {
  const card = $("#checker-card");
  if (check.passed === null || check.passed === undefined) {
    card.innerHTML = `<div class="card-head"><h2>${esc2(t("assistant.checker"))}</h2></div>
      <div class="not-checked">${esc2(t("assistant.checkerUnavailable"))}</div>`;
    return;
  }
  const checks = check.checks || [];
  const failures = check.failures || [];
  const blocked = check.passed === false;
  card.innerHTML = `
    <div class="card-head"><h2>${esc2(t("assistant.checker"))}</h2>
      <span class="hint">${esc2(t("assistant.checks", { n: checks.length, result: blocked ? t("common.blocked") : t("common.pass") }))}</span></div>
    ${blocked ? `<div class="blocked-banner">${esc2(t("assistant.checkerBlockedBanner"))}</div>` : ""}
    ${checks.map((c) => `
      <div class="check-row"><span class="check-dot ${c.status === "pass" ? "pass" : c.status === "fail" ? "fail" : ""}"></span>
        <div><div class="check-name">${esc2(c.id)} · ${trBi(c.name)}</div>
        <div class="check-detail">${trBi(c.detail || "")}</div></div></div>`).join("")}
    ${failures.length ? `<div class="subhead">${esc2(t("assistant.failures"))}</div><div class="fact-list">${failures.map((f) => `<div class="fact-item">${trBi(typeof f === "string" ? f : (f.id ? f.id + " · " : "") + (f.detail || f.name || ""))}</div>`).join("")}</div>` : ""}`;
}

function feedbackItem(r) {
  return `<div class="feedback-item"><span class="rec">${esc2(r.rec_id)} · ${esc2(r.event_id)}</span><br>
    <strong>${trBi(r.result)}</strong> — ${r.reason ? trBi(r.reason) : esc2(t("assistant.noReason"))}<br>
    <span class="hint">${esc2(t("assistant.finalAction"))} ${trBi(r.final_action || "—")} · ${esc2(t("assistant.reviewerLabel"))} ${trBi(r.reviewer || "—")} · ${trBi(r.date || "")}</span></div>`;
}

function renderFeedbackMatches(records) {
  const wrap = $("#feedback-matches");
  if (!wrap) return;
  if (!records || !records.length) { wrap.innerHTML = ""; return; }
  wrap.innerHTML = `<div class="subhead">${esc2(t("assistant.priorFeedbackTitle"))}</div>` + records.map(feedbackItem).join("");
}

/* ------------------------------------------------------------------ feedback POST */
async function submitFeedback(result) {
  if (!state.analysis) { toast(t("assistant.analyzeFirst"), true); return; }
  const reason = $("#feedback-reason").value.trim();
  const reviewer = $("#feedback-reviewer").value.trim() || t("feedback.dutyManager");
  setStatus("#feedback-status", t("feedback.saving"));
  try {
    const data = await api("/api/feedback", {
      method: "POST",
      body: JSON.stringify({
        event_id: state.analysis.event.id,
        result,
        reason,
        reviewer,
        final_action: result === "Reject" ? "No action; continue monitoring" : "Follow the advice with human review",
        outcome: "simulated",
      }),
    });
    $("#feedback-status").textContent = t("assistant.feedbackSaved", { id: data.record.rec_id, result });
    $("#feedback-reason").value = "";
    state.feedback = data.records || [];
    renderFeedbackMatches((data.records || []).slice(-3));
    toast(t("assistant.feedbackSaved", { id: data.record.rec_id, result }));
    state.feedbackLoaded = false;
  } catch (err) {
    $("#feedback-status").textContent = t("assistant.feedbackFailed") + err.message;
    toast(t("assistant.feedbackFailed"), true);
  }
}

/* ------------------------------------------------------------------ ask */
async function askQuestion(question) {
  if (!state.analysis) { toast(t("assistant.analyzeFirst"), true); return; }
  const box = $("#ask-answer");
  box.innerHTML = '<div class="loading">' + esc2(t("assistant.thinking")) + "</div>";
  const payload = state.lastRequest || { event_id: state.analysis.event.id };
  const body = Object.assign({}, payload, { question: question || $("#ask-input").value.trim() });
  if (!body.question) { box.innerHTML = ""; toast(t("assistant.typeQuestion"), true); return; }
  try {
    const data = await api("/api/ask", { method: "POST", body: JSON.stringify(body) });
    const check = data.check || {};
    const checkText = check.passed === null || check.passed === undefined
      ? t("assistant.checker") + ": —"
      : t("assistant.checker") + ": " + (check.passed ? t("common.pass") : t("common.blocked"));
    const answer = trBi((data.answer || {}).text || "", { rich: rich });
    box.innerHTML = `<div class="answer-card">
      <div class="answer-intent">${esc2(t("assistant.intent"))} ${esc2(data.intent || "fallback")} · ${esc2(t("common.offline"))} · ${esc2(checkText)}</div>
      <div class="answer-text">${answer}</div>
      <div class="answer-meta">${esc2(t("assistant.sourcesLabel"))} ${((data.answer || {}).sources || []).map(esc2).join(", ") || "—"}</div>
    </div>`;
    $("#ask-input").value = "";
  } catch (err) {
    box.innerHTML = `<div class="error-banner">${esc2(t("assistant.askFailed"))}${esc2(err.message)}</div>`;
  }
}

/* ------------------------------------------------------------------ detector tab */
async function loadDetector() {
  if (state.detectorLoaded) return;
  try {
    const [ranking, chart] = await Promise.all([api("/api/detector/ranking"), api("/api/detector/chart")]);
    state.ranking = ranking;
    state.chart = chart;
    state.detectorLoaded = true;
    renderDetectorStats(ranking);
    renderChart(chart);
    renderRanking();
    try {
      state.network = await api("/api/network");
      renderNetwork(state.network);
    } catch (networkError) {
      $("#network-map").innerHTML = `<div class="error-banner">${esc2(t("detector.networkFailed"))}${esc2(networkError.message)}</div>`;
      $("#network-mode").textContent = t("detector.networkUnavailable");
    }
  } catch (err) {
    $("#det-stats").innerHTML = `<div class="error-banner">${esc2(t("detector.detectorFailed"))}${esc2(err.message)}</div>`;
  }
}

function renderDetectorStats(ranking) {
  if (!ranking) return;
  const multi = (ranking.multi_signal || []).length;
  const stats = [
    ["192", t("detector.statAirportMonths")],
    [String(ranking.flags_own), t("detector.statOfficial")],
    [String(ranking.flags_any), t("detector.statAny")],
    [String(multi), t("detector.statMulti")],
    ["1", t("detector.statThree")],
  ];
  $("#det-stats").innerHTML = stats.map(([n, l]) =>
    `<div class="stat-card"><div class="stat-num">${esc2(n)}</div><div class="stat-label">${esc2(l)}</div></div>`).join("");
}

/* ------------------------------------------------------------------ network priority map */
const NETWORK_LAYOUT = {
  "北岭机场": [350, 92],
  "云川国际机场": [560, 118],
  "海陵国际机场": [735, 192],
  "星湖机场": [285, 195],
  "南湾机场": [455, 292],
  "青岚机场": [765, 322],
  "临江机场": [170, 300],
  "高原机场": [155, 128],
};
const NETWORK_COLORS = {
  "normal": "#1f8a4c",
  "watch": "#e6a23c",
  "unusual": "#d97706",
  "clearly unusual": "#b42318",
  "can't tell": "#7b61ff",
};

function shortAirport(record) {
  return String(record.airport_en || record.airport || "")
    .replace(/ International/g, "")
    .replace(/ Airport/g, "");
}

function airportZh(record) {
  return String(record.airport || AIRPORT_ZH[record.airport_en] || "");
}

function networkColour(verdict) {
  return NETWORK_COLORS[String(verdict || "").toLowerCase()] || "#6b7a90";
}

function networkRadius(record) {
  const importance = String(record.importance_en || record.importance || "").toLowerCase();
  if (importance === "high" || importance === "高") return 26;
  if (importance === "medium" || importance === "中") return 19;
  return 14;
}

function renderNetwork(data) {
  if (!data) return;
  const wrap = $("#network-map");
  const airports = (data.airports || []).slice().sort((a, b) => a.priority_rank - b.priority_rank);
  if (!airports.length) {
    wrap.innerHTML = '<div class="empty">' + esc2(t("detector.noNetwork")) + "</div>";
    return;
  }
  const isMock = data.mode === "mock";
  $("#network-mode").textContent = (isMock ? "mock fixture" : "real engine") + " · " + (data.month_mode || "context") + " · 模拟";
  if (data.note) $("#network-mode").title = data.note;

  const width = 900, height = 400;
  const nodes = airports.map((record, index) => {
    const position = NETWORK_LAYOUT[record.airport] || [140 + (index % 4) * 200, 110 + Math.floor(index / 4) * 150];
    const [cx, cy] = position;
    const r = networkRadius(record);
    const short = shortAirport(record);
    const zh = airportZh(record);
    const reason = tr(record.reason || "");
    return `<g class="network-node" data-airport="${esc2(record.airport)}" tabindex="0" role="button"
        aria-label="${esc2(short)} / ${esc2(zh)}: ${esc2(biText(record.verdict, EXACT_EN2ZH[record.verdict] || ""))}, priority rank ${record.priority_rank}. ${esc2(reason.text)}">
      <title>${esc2(short)} / ${esc2(zh)} · ${esc2(reason.text)}</title>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="${networkColour(record.verdict)}" fill-opacity="0.92"
        stroke="#ffffff" stroke-width="2"></circle>
      <text x="${cx}" y="${cy + r + 15}" text-anchor="middle" class="network-label">${esc2(short)}</text>
      <text x="${cx}" y="${cy + r + 28}" text-anchor="middle" class="network-sub network-zh">${esc2(zh)}</text>
      <text x="${cx}" y="${cy + r + 41}" text-anchor="middle" class="network-sub">#${record.priority_rank} · ${record.signal_count} ${esc2(t("common.signals"))}</text>
    </g>`;
  }).join("");

  wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="400" role="img"
      aria-label="${esc2(t("detector.schematic"))}: ${esc2(data.mode || "mock")}">
    <text x="16" y="24" class="network-caption">${esc2(t("detector.schematic"))} · 模拟 / SIMULATED</text>
    ${nodes}
  </svg>`;
  wrap.querySelectorAll(".network-node").forEach((element) => {
    const airport = element.getAttribute("data-airport");
    const record = airports.find((item) => item.airport === airport);
    element.addEventListener("click", () => openAirportAnalysis(record));
    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openAirportAnalysis(record);
      }
    });
  });
  renderNetworkLegend();
  renderNetworkTable(airports);
  window.__networkRendered = true;
}

function renderNetworkLegend() {
  const verdicts = ["normal", "watch", "unusual", "clearly unusual", "can't tell"];
  $("#network-legend").innerHTML = verdicts.map((verdict) =>
    `<span><span class="legend-dot" style="background:${networkColour(verdict)}"></span>${biTermEn(verdict)}</span>`).join("")
    + `<span><span class="legend-dot legend-dot-sm" style="background:#6b7a90"></span>${esc2(t("detector.legendSmall"))}</span>`
    + `<span><span class="legend-dot" style="background:#6b7a90"></span>${esc2(t("detector.legendMedium"))}</span>`
    + `<span><span class="legend-dot legend-dot-lg" style="background:#6b7a90"></span>${esc2(t("detector.legendLarge"))}</span>`;
}

function renderNetworkTable(airports) {
  const rows = airports.slice().sort((a, b) => a.priority_rank - b.priority_rank);
  $("#network-table").innerHTML = `
    <thead><tr><th>${esc2(t("detector.tableRank"))}</th><th>${esc2(t("common.airport"))}</th><th>${esc2(t("common.month"))}</th>
      <th>${esc2(t("detector.tableSignals"))}</th><th>${esc2(t("common.verdict"))}</th>
      <th>${esc2(t("common.importance"))}</th><th>${esc2(t("common.reason"))}</th></tr></thead>
    <tbody>${rows.map((record) => `
      <tr>
        <td class="num">#${record.priority_rank}</td>
        <td>${bi(record.airport_en || shortAirport(record), record.airport)}</td>
        <td class="num">${esc2(record.month_label)}</td>
        <td class="num">${record.signal_count}</td>
        <td><span class="signal-chip ${record.signal_count > 0 ? "on" : "off"}">${biTermEn(record.verdict)}</span></td>
        <td>${bi(record.importance_en, record.importance)}</td>
        <td class="hint">${trBi(record.reason)}</td>
      </tr>`).join("")}</tbody>`;
}

function openAirportAnalysis(record) {
  if (!record) return;
  switchTab("assistant");
  const event = (state.bootstrap.events || []).find((item) => item.airport === record.airport);
  if (event) {
    selectEvent(event.id);
    analyzeEvent({ event_id: event.id, writer_mode: "offline" });
  } else {
    analyzeEvent({
      custom: {
        airport: record.airport,
        time_text: "selected month " + record.month_label,
        weather_text: "see monthly baseline",
        ops_text: "network schematic drill-down",
        importance: record.importance,
        notes: "",
        known: "monthly baseline",
        unknown: "current flight-level status",
      },
      writer_mode: "offline",
    });
  }
  toast(biText(record.airport_en, record.airport) + " → " + t("tab.assistant"));
}

function renderChart(chart) {
  const wrap = $("#det-chart");
  if (!wrap) return;
  const months = chart.months || [];
  if (!months.length || !(chart.series || []).length) {
    wrap.innerHTML = '<div class="empty">' + esc2(t("detector.chartNoData")) + "</div>";
    return;
  }
  const width = 1080, height = 360, padL = 52, padR = 20, padT = 18, padB = 48;
  const innerW = width - padL - padR, innerH = height - padT - padB;
  const values = [];
  chart.series.forEach((s) => s.values.forEach((v) => { values.push(v.completion_pct); values.push(v.peer_pct); }));
  let min = Math.min.apply(null, values), max = Math.max.apply(null, values);
  min = Math.floor(min - 2); max = Math.ceil(max + 2);
  const x = (i) => padL + (months.length <= 1 ? 0 : (i * innerW) / (months.length - 1));
  const y = (v) => padT + innerH - ((v - min) / (max - min)) * innerH;
  const colors = ["#1f6feb", "#d97706"];
  const paths = chart.series.map((s, idx) => {
    const pts = s.values.map((v, i) => `${x(i).toFixed(1)},${y(v.completion_pct).toFixed(1)}`).join(" ");
    return `<polyline fill="none" stroke="${colors[idx % colors.length]}" stroke-width="2.5" points="${pts}"></polyline>` +
      s.values.map((v, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(v.completion_pct).toFixed(1)}" r="3" fill="${colors[idx % colors.length]}"><title>${esc2(biText(AIRPORT_EN[s.airport] || s.airport, s.airport))} ${esc2(v.month)}: ${fmt(v.completion_pct)}%</title></circle>`).join("");
  }).join("");
  const peerVals = chart.series[0].values;
  const peerPts = peerVals.map((v, i) => `${x(i).toFixed(1)},${y(v.peer_pct).toFixed(1)}`).join(" ");
  const grid = [];
  for (let g = Math.ceil(min / 5) * 5; g <= max; g += 5) {
    grid.push(`<line x1="${padL}" y1="${y(g).toFixed(1)}" x2="${width - padR}" y2="${y(g).toFixed(1)}" stroke="#e6ebf3"></line>` +
      `<text x="${padL - 8}" y="${(y(g) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="#66748a">${g}%</text>`);
  }
  const labels = months.map((m, i) => (i % 3 === 0 ? `<text x="${x(i).toFixed(1)}" y="${height - 18}" text-anchor="middle" font-size="10" fill="#66748a">${esc2(m)}</text>` : "")).join("");
  const highlight = months.map((m, i) => (m === "2025-07" || m === "2025-08")
    ? `<rect x="${x(i) - 7}" y="${padT}" width="14" height="${innerH}" fill="#fdecea" opacity="0.75"></rect>` : "").join("");
  wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" role="img" aria-label="${esc2(t("detector.hailingTitle"))}">
    ${highlight}${grid.join("")}${labels}
    <polyline fill="none" stroke="#9aa8bd" stroke-width="1.5" stroke-dasharray="6 5" points="${peerPts}"></polyline>
    ${paths}
  </svg>
  <div class="chart-legend">
    <span><span class="legend-swatch" style="background:#1f6feb"></span>${bi("Hailing", "海陵")}</span>
    <span><span class="legend-swatch" style="background:#d97706"></span>${bi("Yunchuan", "云川")}</span>
    <span><span class="legend-swatch" style="background:#9aa8bd"></span>${esc2(t("detector.legendPeer"))}</span>
    <span>${esc2(t("detector.legendHighlight"))}</span>
  </div>`;
}

function renderRanking() {
  if (!state.ranking) return;
  const filterText = ($("#det-filter").value || "").trim().toLowerCase();
  const filterVerdict = $("#det-verdict").value;
  const rows = (state.ranking.rows || []).slice().sort((a, b) =>
    (b.signal_count - a.signal_count) || (a.delta_pp - b.delta_pp) ||
    String(a.airport).localeCompare(String(b.airport)));
  const filtered = rows.filter((r) => {
    const okText = !filterText || r.airport.toLowerCase().includes(filterText) || r.airport_en.toLowerCase().includes(filterText);
    const okVerdict = !filterVerdict || r.verdict === filterVerdict;
    return okText && okVerdict;
  });
  const table = $("#det-table");
  table.innerHTML = `
    <thead><tr><th>${esc2(t("common.airport"))}</th><th>${esc2(t("common.month"))}</th><th>${esc2(t("detector.tableTier"))}</th>
      <th>${esc2(t("detector.tableCompletion"))}</th><th>${esc2(t("detector.tablePeer"))}</th>
      <th>${esc2(t("detector.tableOwnDelta"))}</th><th>${esc2(t("detector.tablePeerDelta"))}</th><th>${esc2(t("detector.tableYoY"))}</th>
      <th>${esc2(t("detector.tableSignals"))}</th><th>${esc2(t("common.verdict"))}</th><th>${esc2(t("detector.tableConfidence"))}</th></tr></thead>
    <tbody>${filtered.map((r) => `
      <tr class="${r.signal_count >= 2 ? "top-row" : ""}">
        <td>${bi(r.airport_en, r.airport)}</td>
        <td class="num">${esc2(r.month_label)}</td>
        <td>${pairHTML(r, { en: "tier_en", zh: "tier" })}</td>
        <td class="num">${fmt(r.completion_pct)}%</td>
        <td class="num">${fmt(r.peer_pct)}%</td>
        <td class="num">${signed(r.delta_pp)}</td>
        <td class="num">${signed(r.peer_delta_pp)}</td>
        <td class="num">${r.yoy_delta_pp === null ? esc2(t("detector.na")) : signed(r.yoy_delta_pp)}</td>
        <td class="num">${r.signal_count}</td>
        <td><span class="signal-chip ${r.signal_count > 0 ? "on" : "off"}">${biTermEn(r.verdict)}</span></td>
        <td class="num">${fmt(r.confidence, 2)}</td>
      </tr>`).join("") || `<tr><td colspan="11" class="empty">${esc2(t("detector.noRows"))}</td></tr>`}</tbody>`;
}

/* ------------------------------------------------------------------ exam */
function renderExam(data) {
  if (!data) return;
  const s = data.summary || {};
  const stats = [
    [String(s.official_pass ?? 0) + "/" + String(s.official_total ?? 15), t("exam.official")],
    [String(s.own_pass ?? 0) + "/" + String(s.own_total ?? 5), t("exam.own")],
    [String(s.pass ?? 0) + "/" + String(s.total ?? 0), t("exam.total")],
  ];
  $("#exam-summary").innerHTML = stats.map(([n, l]) => `<div class="stat-card"><div class="stat-num">${esc2(n)}</div><div class="stat-label">${esc2(l)}</div></div>`).join("");
  const table = $("#exam-table");
  const runs = data.runs || [];
  if (!runs.length) {
    setStatus("#exam-status", data.note || t("exam.noRunner"), "error");
    table.innerHTML = `<tbody><tr><td class="empty">${esc2(data.note || t("exam.noResults"))}</td></tr></tbody>`;
    return;
  }
  setStatus("#exam-status", t("exam.finished", { pass: s.pass, total: s.total }), "ok");
  table.innerHTML = `
    <thead><tr><th>${esc2(t("exam.id"))}</th><th>${esc2(t("exam.group"))}</th><th>${esc2(t("exam.type"))}</th>
      <th>${esc2(t("exam.question"))}</th><th>${esc2(t("exam.expected"))}</th><th>${esc2(t("exam.forbidden"))}</th>
      <th>${esc2(t("exam.result"))}</th><th>${esc2(t("exam.evidence"))}</th></tr></thead>
    <tbody>${runs.map((r) => `
      <tr><td class="num">${esc2(r.id)}</td><td>${esc2(r.group)}</td><td>${trBi(r.type)}</td>
      <td>${trBi(r.question)}</td><td class="hint">${trBi(r.expected || "")}</td><td class="hint">${trBi(r.forbidden || "")}</td>
      <td class="${r.result === "pass" ? "pass" : "fail"}">${esc2(r.result)}</td><td class="hint">${esc2(Array.isArray(r.evidence) ? r.evidence.join(", ") : (r.evidence || r.error_note || ""))}</td></tr>`).join("")}
    </tbody>`;
}

async function runExam() {
  const btn = $("#run-exam");
  btn.disabled = true;
  setStatus("#exam-status", t("exam.running"));
  try {
    const data = await api("/api/tests/run", { method: "POST", body: JSON.stringify({ writer_mode: "offline", include_own: true }) });
    state.exam = data;
    renderExam(data);
    $("#download-exam").disabled = false;
  } catch (err) {
    setStatus("#exam-status", t("exam.failed") + err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

function downloadExam() {
  if (!state.exam) return;
  const blob = new Blob([JSON.stringify(state.exam, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "t3_exam_results.json"; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/* ------------------------------------------------------------------ feedback tab */
function renderFeedback(records) {
  const counts = { Accept: 0, Edit: 0, Reject: 0, Pending: 0 };
  records.forEach((r) => { counts[r.result] = (counts[r.result] || 0) + 1; });
  $("#feedback-stats").innerHTML = Object.entries(counts).map(([k, v]) =>
    `<div class="stat-card"><div class="stat-num">${v}</div><div class="stat-label">${trBi(k)}</div></div>`).join("");
  const table = $("#feedback-table");
  table.innerHTML = `
    <thead><tr><th>${esc2(t("feedback.record"))}</th><th>${esc2(t("feedback.event"))}</th><th>${esc2(t("feedback.result"))}</th>
      <th>${esc2(t("feedback.reason"))}</th><th>${esc2(t("feedback.finalAction"))}</th><th>${esc2(t("feedback.reviewer"))}</th>
      <th>${esc2(t("feedback.date"))}</th><th>${esc2(t("feedback.source"))}</th></tr></thead>
    <tbody>${records.map((r) => `
      <tr><td class="num">${esc2(r.rec_id)}</td><td>${esc2(r.event_id)}</td>
      <td><strong>${trBi(r.result)}</strong></td><td>${trBi(r.reason || "—")}</td>
      <td>${trBi(r.final_action || "—")}</td><td>${trBi(r.reviewer || "—")}</td>
      <td>${trBi(r.date || "—")}</td><td>${esc2(r.source || "—")}</td></tr>`).join("")}</tbody>`;
}

async function loadFeedback() {
  try {
    const data = await api("/api/feedback");
    state.feedback = data.records || [];
    state.feedbackLoaded = true;
    renderFeedback(state.feedback);
  } catch (err) {
    $("#feedback-stats").innerHTML = `<div class="error-banner">${esc2(t("feedback.loadFailed"))}${esc2(err.message)}</div>`;
  }
}

/* ------------------------------------------------------------------ language switching */
function renderAll() {
  applyStatic(document);
  if (!state.bootstrap) return;
  renderEngineBadge(state.engineMode, state.health);
  renderEventCards();
  renderAirportSelect();
  renderAskChips();
  renderAbout();
  if (state.selectedEvent) selectEvent(state.selectedEvent);
  if (state.analysis) renderResult(state.analysis);
  if (state.ranking) { renderDetectorStats(state.ranking); renderChart(state.chart); renderRanking(); }
  if (state.network) renderNetwork(state.network);
  if (state.exam) renderExam(state.exam);
  if (state.feedback.length) renderFeedback(state.feedback);
  updateAssistantStatus();
}

/* ------------------------------------------------------------------ wire up */
function bind() {
  $$(".tab-btn").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));
  $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.getAttribute("data-lang"))));
  window.addEventListener("t3:langchange", renderAll);

  $("#analyze-selected").addEventListener("click", () => {
    if (!state.selectedEvent) return;
    analyzeEvent({ event_id: state.selectedEvent, writer_mode: $("#writer-mode").value || "offline" });
  });

  $("#custom-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const custom = {
      airport: $("#custom-airport").value,
      time_text: $("#custom-time").value.trim() || "as entered by staff",
      weather_text: $("#custom-weather").value.trim(),
      ops_text: $("#custom-ops").value.trim(),
      importance: $("#custom-importance").value,
      notes: $("#custom-notes").value.trim(),
      known: $("#custom-known").value.trim(),
      unknown: $("#custom-unknown").value.trim(),
    };
    analyzeEvent({ custom, writer_mode: $("#writer-mode").value || "offline" });
  });

  $$(".msg-tab").forEach((b) => b.addEventListener("click", () => { state.msgTab = b.dataset.msg; renderMessages(state.analysis.output); }));
  $("#toggle-original").addEventListener("click", () => {
    state.showOriginalMsg = !state.showOriginalMsg;
    if (state.analysis) renderMessages(state.analysis.output);
  });
  $("#copy-msg").addEventListener("click", async () => {
    const text = $("#msg-body").textContent || "";
    try { await navigator.clipboard.writeText(text); toast(t("common.copied")); }
    catch (e) { toast(t("common.copyFail"), true); }
  });
  $$("[data-feedback]").forEach((b) => b.addEventListener("click", () => submitFeedback(b.dataset.feedback)));

  $("#ask-btn").addEventListener("click", () => askQuestion($("#ask-input").value.trim()));
  $("#ask-input").addEventListener("keydown", (e) => { if (e.key === "Enter") askQuestion($("#ask-input").value.trim()); });

  $("#det-filter").addEventListener("input", renderRanking);
  $("#det-verdict").addEventListener("change", renderRanking);
  $("#run-exam").addEventListener("click", runExam);
  $("#download-exam").addEventListener("click", downloadExam);
  $("#reload-feedback").addEventListener("click", loadFeedback);
}

document.addEventListener("DOMContentLoaded", () => { bind(); init(); });
