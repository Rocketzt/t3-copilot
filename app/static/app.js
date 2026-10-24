/* T3 Ops Copilot - vanilla JS front end (no dependencies, offline). */
"use strict";

const SIM = "模拟 / SIMULATED";

const state = {
  bootstrap: null,
  selectedEvent: null,
  analysis: null,
  lastRequest: null,
  msgTab: "ops",
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

function esc(value) {
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
  if (!Number.isFinite(v)) return esc(n);
  return v.toFixed(digits);
}

function signed(n, digits = 2) {
  if (n === null || n === undefined) return "—";
  const v = Number(n);
  return (v > 0 ? "+" : "") + v.toFixed(digits);
}

const TAG_NAMES = ["ASSUMPTION", "UNKNOWN", "HUMAN"];

function tag(text) {
  const style = { assumption: "tag-assumption", unknown: "tag-unknown", human: "tag-human" }[String(text).toLowerCase()] || "";
  return `<span class="tag-chip ${style}">${esc(text)}</span>`;
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
  let html = esc(collapseLeadingTags(humanize(text)));
  html = html.replace(/\[FACT:\s*([A-Za-z0-9_\-\s]+)\]/g,
    (m, src) => `<span class="tag-chip tag-fact" title="Fact source">FACT · ${esc(src.trim())}</span>`);
  html = html.replace(/\[(ASSUMPTION|UNKNOWN|HUMAN)\]/g, (m, t) => tag(t));
  html = html.replace(/\n/g, "<br>");
  return html;
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
    badge.textContent = "engine: " + state.engineMode;
    const meta = [];
    if (health && typeof health.checker_available === "boolean") {
      meta.push("checker " + (health.checker_available ? "available" : "not available"));
    }
    if (health && typeof health.runner_available === "boolean") {
      meta.push("runner " + (health.runner_available ? "available" : "not available"));
    }
    if (health && health.writer_mode) meta.push("writer: " + health.writer_mode);
    badge.title = meta.length ? meta.join(" · ") : "Mode reported by /api/health and /api/analyze";
  }
  const footer = $("#footer-mode");
  if (footer) footer.textContent = state.engineMode + " / offline";
}

async function init() {
  let health = null;
  try {
    state.bootstrap = await api("/api/bootstrap");
    try {
      health = await api("/api/health");
    } catch (e) {
      health = null; /* the badge falls back to bootstrap data; the page still works */
    }
  } catch (err) {
    setStatus("#assistant-status", "Could not load /api/bootstrap: " + err.message, "error");
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
  setStatus("#assistant-status", `${b.counts.airports} airports · ${b.counts.airport_months} airport-months · ${b.counts.rules} rules · ${b.counts.tests} tests — all simulated.`, "ok");

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
  const wrap = $("#event-cards");
  wrap.innerHTML = "";
  b.events.forEach((ev) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "event-card";
    card.dataset.event = ev.id;
    card.innerHTML = `
      <div class="eid">${esc(ev.id)} · ${esc(ev.time_text)}</div>
      <div class="ename">${esc(ev.name)}</div>
      <div class="emeta">${esc(ev.airport)} · importance ${esc(ev.importance)}</div>
      <span class="etag">${esc(ev.id === "EVT003" ? "conflict → can't tell" : ev.id === "EVT005" ? "human overrule" : ev.id === "EVT004" ? "passenger comms" : ev.id === "EVT002" ? "sustained pressure" : "weather risk")}</span>`;
    card.addEventListener("click", () => selectEvent(ev.id));
    wrap.appendChild(card);
  });
}

function selectEvent(id) {
  state.selectedEvent = id;
  $$(".event-card").forEach((c) => c.classList.toggle("selected", c.dataset.event === id));
  $("#analyze-selected").disabled = false;
  $("#selected-hint").textContent = "Selected: " + id;
}

function renderAirportSelect() {
  const sel = $("#custom-airport");
  sel.innerHTML = "";
  state.bootstrap.airports.forEach((ap) => {
    const opt = document.createElement("option");
    opt.value = ap.name;
    opt.textContent = `${ap.name_en} (${ap.tier_en})`;
    sel.appendChild(opt);
  });
}

function renderAskChips() {
  const wrap = $("#ask-chips");
  wrap.innerHTML = "";
  const tests = state.bootstrap.tests || [];
  tests.forEach((t) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "qchip";
    chip.textContent = t.label || t.question_en;
    chip.title = `${t.id} · ${t.question_en}`;
    chip.addEventListener("click", () => askQuestion(t.question_en));
    wrap.appendChild(chip);
  });
}

function renderAbout() {
  const b = state.bootstrap;
  $("#about-counts").textContent =
    `${b.counts.airports} airports · ${b.counts.months} months · ${b.counts.airport_months} airport-months · ` +
    `${b.counts.rules} rules · ${b.counts.tests} tests · ${b.counts.events} events — ${b.sim_label}`;
  const dq = $("#about-dq");
  dq.innerHTML = (b.data_quality || []).map((d) => `
    <div class="fact-item"><strong>${esc(d.id)}</strong> · ${esc(d.description || d.kind)}<br>
    <span class="hint">Handling: ${esc(d.handling || "—")} · status: ${esc(d.status || "—")}</span></div>`).join("");
  const rules = $("#about-rules");
  rules.innerHTML = `
    <thead><tr><th>Rule</th><th>Topic</th><th>Trigger</th><th>Action</th><th>Escalate to</th><th>Manual?</th></tr></thead>
    <tbody>${(b.rules || []).map((r) => `
      <tr><td class="num">${esc(r.id)}</td><td>${esc(r.topic_en || r.topic)}</td>
      <td>${esc(r.trigger_en || r.trigger)}</td><td>${esc(r.action_en || r.action)}</td>
      <td>${esc(r.escalate_to_en || r.escalate_to)}</td><td>${r.manual_approval ? "Yes" : "No"}</td></tr>`).join("")}
    </tbody>`;
}

/* ------------------------------------------------------------------ analyze */
async function analyzeEvent(payload) {
  setStatus("#assistant-status", "Analyzing event…");
  const btn = payload.event_id ? $("#analyze-selected") : $("#analyze-custom");
  btn.disabled = true;
  try {
    const result = await api("/api/analyze", { method: "POST", body: JSON.stringify(payload) });
    state.analysis = result;
    state.lastRequest = payload;
    renderResult(result);
    renderEngineBadge(result.engine_mode || "fixtures", state.health);
    setStatus("#assistant-status", `Analyzed ${result.event.id} (${result.event.airport_en || result.event.airport}) — engine mode: ${result.engine_mode || "fixture"}.`, "ok");
    $("#result").hidden = false;
    $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    setStatus("#assistant-status", "Analyze failed: " + err.message + (err.detail ? " — " + err.detail : ""), "error");
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
        <div class="hint">Risk level · 风险等级</div>
        <div class="risk-level">${esc(levelEn)}<span class="zh">${esc(levelZh)}</span></div>
      </div>
      <div class="risk-score">score ${fmt(risk.score, 2)}<br>${facts.conflict ? "conflict flag" : esc(result.engine_mode || "fixture")}</div>
    </div>
    <ul class="reason-list">${(risk.reasons || []).map((r) => `<li>${esc(r.text)} <span class="src-chip">${esc(r.source)}</span></li>`).join("")}</ul>
    <div class="disclaimer">Decision support only. Cancelling, releasing, dispatching, maintaining or compensating flights — and formal passenger notices — require the responsible qualified professional. ${SIM}</div>`;

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
      <h2>Is this unusual?</h2>
      <span class="hint">${esc(det.month_label || "")} · ${esc(det.airport_en || det.airport || "")}</span>
    </div>
    ${comps.map((c) => `
      <div class="compare-row">
        <div class="compare-label">${esc(c.label || c.key)}</div>
        <div class="compare-detail">${esc(c.detail || "")}</div>
        <div><span class="signal-chip ${c.signal ? "on" : "off"}">${c.signal ? "SIGNAL" : "no signal"} · ${signed(c.value_pp)} pp</span></div>
      </div>`).join("")}
    <div class="verdict-line">
      <span class="verdict-badge ${cls}">${esc(verdict)}</span>
      <span class="hint">${det.signal_count || 0} of ${det.comparisons_available || comps.length} comparisons signal · confidence ${fmt(det.confidence, 2)}</span>
    </div>
    <p class="hint">${esc(det.selection_reason || "")}${det.weather_missing ? " · weather record missing (DQ002), confidence reduced" : ""}</p>
    <p class="hint">${esc((det.confidence_notes || []).join(" · "))}</p>`;
}

function renderFactsCard(facts) {
  const factsList = facts.facts || [];
  const feedback = facts.feedback_matches || [];
  const section = (title, items, tagName) => {
    if (!items || !items.length) return "";
    return `<div class="subhead">${esc(title)}</div><div class="fact-list">` +
      items.map((x) => `<div class="fact-item">${tagName ? tag(tagName) : ""}${esc(humanize(stripLeadingTag(x)))}</div>`).join("") + `</div>`;
  };
  $("#facts-card").innerHTML = `
    <div class="card-head"><h2>Fact sheet <span class="zh">事实表</span></h2>
      <span class="hint">${factsList.length} facts · every number has a source</span></div>
    <div class="subhead">Facts</div>
    <div class="fact-list">${factsList.map((f) => `
      <div class="fact-item"><span class="src-chip">${esc(f.source)}</span>${esc(humanize(f.text))}</div>`).join("") || '<div class="empty">No facts.</div>'}</div>
    ${section("Assumptions to verify", facts.assumptions, "ASSUMPTION")}
    ${section("Known information gaps", facts.unknowns, "UNKNOWN")}
    ${section("Missing / limited data", facts.missing_data, "UNKNOWN")}
    ${section("Forbidden actions", facts.forbidden_actions, "")}
    <div class="subhead">Sources cited</div>
    <div class="pill-list">${(facts.sources || []).map((s) => `<span class="pill">${esc(s)}</span>`).join("")}</div>
    ${feedback.length ? `<div class="subhead">Prior feedback loaded</div><div class="feedback-matches">${feedback.map(feedbackItem).join("")}</div>` : ""}`;
}

function renderFields(output) {
  const fields = output.fields || [];
  $("#fields-grid").innerHTML = fields.map((f) => `
    <div class="field-card">
      <div class="field-key">${esc(f.key)}</div>
      <div class="field-label">${esc(f.label_en)}<span class="zh">${esc(f.label_zh)}</span></div>
      <div class="field-value">${rich(f.value)}</div>
    </div>`).join("") || '<div class="empty">No fields.</div>';
}

function renderMessages(output) {
  const msgs = output.messages || {};
  const current = msgs[state.msgTab] || msgs.ops || "";
  $("#msg-body").textContent = current;
  $$(".msg-tab").forEach((b) => b.classList.toggle("active", b.dataset.msg === state.msgTab));
}

function renderChecker(check) {
  const card = $("#checker-card");
  if (check.passed === null || check.passed === undefined) {
    card.innerHTML = `<div class="card-head"><h2>Checker</h2></div>
      <div class="not-checked">${esc(check.detail || "Checker not available on this branch. The UI shows 'not checked' instead of a fake pass.")}</div>`;
    return;
  }
  const checks = check.checks || [];
  const failures = check.failures || [];
  const blocked = check.passed === false;
  card.innerHTML = `
    <div class="card-head"><h2>Checker</h2>
      <span class="hint">${checks.length} checks · ${blocked ? "blocked" : "pass"}</span></div>
    ${blocked ? `<div class="blocked-banner">BLOCKED — a fabricated or unsupported claim was found. This is the live negative test.</div>` : ""}
    ${checks.map((c) => `
      <div class="check-row"><span class="check-dot ${c.status === "pass" ? "pass" : c.status === "fail" ? "fail" : ""}"></span>
        <div><div class="check-name">${esc(c.id)} · ${esc(c.name)}</div>
        <div class="check-detail">${esc(c.detail || "")}</div></div></div>`).join("")}
    ${failures.length ? `<div class="subhead">Failures</div><div class="fact-list">${failures.map((f) => `<div class="fact-item">${esc(f.id ? f.id + " · " : "")}${esc(f.detail || f.name || f)}</div>`).join("")}</div>` : ""}`;
}

function feedbackItem(r) {
  return `<div class="feedback-item"><span class="rec">${esc(r.rec_id)} · ${esc(r.event_id)}</span><br>
    <strong>${esc(r.result)}</strong> — ${esc(r.reason || "no reason recorded")}<br>
    <span class="hint">Final action: ${esc(r.final_action || "—")} · reviewer: ${esc(r.reviewer || "—")} · ${esc(r.date || "")}</span></div>`;
}

function renderFeedbackMatches(records) {
  const wrap = $("#feedback-matches");
  if (!records || !records.length) { wrap.innerHTML = ""; return; }
  wrap.innerHTML = `<div class="subhead">Prior feedback for a similar event</div>` + records.map(feedbackItem).join("");
}

/* ------------------------------------------------------------------ feedback POST */
async function submitFeedback(result) {
  if (!state.analysis) { toast("Analyze an event first.", true); return; }
  const reason = $("#feedback-reason").value.trim();
  const reviewer = $("#feedback-reviewer").value.trim() || "Duty manager";
  setStatus("#feedback-status", "Saving…");
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
    $("#feedback-status").textContent = `Saved ${data.record.rec_id} (${result}).`;
    $("#feedback-reason").value = "";
    state.feedback = data.records || [];
    renderFeedbackMatches((data.records || []).slice(-3));
    toast(`Feedback saved: ${result}`);
    state.feedbackLoaded = false;
  } catch (err) {
    $("#feedback-status").textContent = "Save failed: " + err.message;
    toast("Feedback save failed", true);
  }
}

/* ------------------------------------------------------------------ ask */
async function askQuestion(question) {
  if (!state.analysis) { toast("Analyze an event first.", true); return; }
  const box = $("#ask-answer");
  box.innerHTML = '<div class="loading">Thinking…</div>';
  const payload = state.lastRequest || { event_id: state.analysis.event.id };
  const body = Object.assign({}, payload, { question: question || $("#ask-input").value.trim() });
  if (!body.question) { box.innerHTML = ""; toast("Type a question first.", true); return; }
  try {
    const data = await api("/api/ask", { method: "POST", body: JSON.stringify(body) });
    const check = data.check || {};
    const checkText = check.passed === null || check.passed === undefined
      ? "checker: not available"
      : "checker: " + (check.passed ? "pass" : "blocked");
    box.innerHTML = `<div class="answer-card">
      <div class="answer-intent">intent: ${esc(data.intent || "fallback")} · mode: offline · ${esc(checkText)}</div>
      <div class="answer-text">${rich((data.answer || {}).text || "")}</div>
      <div class="answer-meta">sources: ${((data.answer || {}).sources || []).map(esc).join(", ") || "—"}</div>
    </div>`;
    $("#ask-input").value = "";
  } catch (err) {
    box.innerHTML = `<div class="error-banner">Ask failed: ${esc(err.message)}</div>`;
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
      $("#network-map").innerHTML = `<div class="error-banner">Network priority failed: ${esc(networkError.message)}</div>`;
      $("#network-mode").textContent = "network: unavailable";
    }
  } catch (err) {
    $("#det-stats").innerHTML = `<div class="error-banner">Detector load failed: ${esc(err.message)}</div>`;
  }
}

function renderDetectorStats(ranking) {
  const multi = (ranking.multi_signal || []).length;
  const stats = [
    ["192", "airport-months"],
    [String(ranking.flags_own), "official RULE003 flags"],
    [String(ranking.flags_any), "any-signal months"],
    [String(multi), "multi-signal months"],
    ["1", "three-signal month (Hailing 2025-07)"],
  ];
  $("#det-stats").innerHTML = stats.map(([n, l]) =>
    `<div class="stat-card"><div class="stat-num">${esc(n)}</div><div class="stat-label">${esc(l)}</div></div>`).join("");
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
  const wrap = $("#network-map");
  const airports = (data.airports || []).slice().sort((a, b) => a.priority_rank - b.priority_rank);
  if (!airports.length) {
    wrap.innerHTML = '<div class="empty">No network data.</div>';
    return;
  }
  const isMock = data.mode === "mock";
  $("#network-mode").textContent = `mode: ${isMock ? "mock fixture" : "real engine"} · month: ${data.month_mode || "context"} · 模拟`;
  if (data.note) $("#network-mode").title = data.note;

  const width = 900, height = 400;
  const nodes = airports.map((record, index) => {
    const position = NETWORK_LAYOUT[record.airport] || [140 + (index % 4) * 200, 110 + Math.floor(index / 4) * 150];
    const [cx, cy] = position;
    const r = networkRadius(record);
    const short = shortAirport(record);
    return `<g class="network-node" data-airport="${esc(record.airport)}" tabindex="0" role="button"
        aria-label="${esc(record.airport_en || record.airport)}: ${esc(record.verdict)}, priority rank ${record.priority_rank}. ${esc(record.reason)}">
      <title>${esc(record.reason)}</title>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="${networkColour(record.verdict)}" fill-opacity="0.92"
        stroke="#ffffff" stroke-width="2"></circle>
      <text x="${cx}" y="${cy + r + 17}" text-anchor="middle" class="network-label">${esc(short)}</text>
      <text x="${cx}" y="${cy + r + 30}" text-anchor="middle" class="network-sub">#${record.priority_rank} · ${record.signal_count} signal${record.signal_count === 1 ? "" : "s"}</text>
    </g>`;
  }).join("");

  wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="400" role="img"
      aria-label="Schematic network priority map: ${esc(data.mode || "mock")}">
    <text x="16" y="24" class="network-caption">Schematic — not geographic · 模拟 / SIMULATED</text>
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
    `<span><span class="legend-dot" style="background:${networkColour(verdict)}"></span>${esc(verdict)}</span>`).join("")
    + `<span><span class="legend-dot legend-dot-sm" style="background:#6b7a90"></span>small importance</span>`
    + `<span><span class="legend-dot" style="background:#6b7a90"></span>medium</span>`
    + `<span><span class="legend-dot legend-dot-lg" style="background:#6b7a90"></span>large</span>`;
}

function renderNetworkTable(airports) {
  const rows = airports.slice().sort((a, b) => a.priority_rank - b.priority_rank);
  $("#network-table").innerHTML = `
    <thead><tr><th>Rank</th><th>Airport</th><th>Month</th><th>Signals</th><th>Verdict</th>
      <th>Importance</th><th>Reason</th></tr></thead>
    <tbody>${rows.map((record) => `
      <tr>
        <td class="num">#${record.priority_rank}</td>
        <td>${esc(record.airport_en || record.airport)}<div class="hint">${esc(record.airport)}</div></td>
        <td class="num">${esc(record.month_label)}</td>
        <td class="num">${record.signal_count}</td>
        <td><span class="signal-chip ${record.signal_count > 0 ? "on" : "off"}">${esc(record.verdict)}</span></td>
        <td>${esc(record.importance_en || record.importance)}</td>
        <td class="hint">${esc(record.reason)}</td>
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
  toast("Opened " + (record.airport_en || record.airport) + " in the Assistant tab");
}

function renderChart(chart) {
  const wrap = $("#det-chart");
  const months = chart.months || [];
  if (!months.length || !(chart.series || []).length) {
    wrap.innerHTML = '<div class="empty">No chart data.</div>';
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
      s.values.map((v, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(v.completion_pct).toFixed(1)}" r="3" fill="${colors[idx % colors.length]}"><title>${esc(s.airport)} ${esc(v.month)}: ${fmt(v.completion_pct)}%</title></circle>`).join("");
  }).join("");
  const peerVals = chart.series[0].values;
  const peerPts = peerVals.map((v, i) => `${x(i).toFixed(1)},${y(v.peer_pct).toFixed(1)}`).join(" ");
  const grid = [];
  for (let g = Math.ceil(min / 5) * 5; g <= max; g += 5) {
    grid.push(`<line x1="${padL}" y1="${y(g).toFixed(1)}" x2="${width - padR}" y2="${y(g).toFixed(1)}" stroke="#e6ebf3"></line>` +
      `<text x="${padL - 8}" y="${(y(g) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="#66748a">${g}%</text>`);
  }
  const labels = months.map((m, i) => (i % 3 === 0 ? `<text x="${x(i).toFixed(1)}" y="${height - 18}" text-anchor="middle" font-size="10" fill="#66748a">${esc(m)}</text>` : "")).join("");
  const highlight = months.map((m, i) => (m === "2025-07" || m === "2025-08")
    ? `<rect x="${x(i) - 7}" y="${padT}" width="14" height="${innerH}" fill="#fdecea" opacity="0.75"></rect>` : "").join("");
  wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" role="img" aria-label="Hailing versus Yunchuan monthly completion">
    ${highlight}${grid.join("")}${labels}
    <polyline fill="none" stroke="#9aa8bd" stroke-width="1.5" stroke-dasharray="6 5" points="${peerPts}"></polyline>
    ${paths}
  </svg>
  <div class="chart-legend">
    <span><span class="legend-swatch" style="background:#1f6feb"></span>Hailing</span>
    <span><span class="legend-swatch" style="background:#d97706"></span>Yunchuan</span>
    <span><span class="legend-swatch" style="background:#9aa8bd"></span>Same-class peer average (dashed)</span>
    <span>Highlighted: 2025-07/08 (planted anomaly)</span>
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
    <thead><tr><th>Airport</th><th>Month</th><th>Tier</th><th>Completion</th><th>Peer</th>
      <th>Own Δpp</th><th>Peer Δpp</th><th>YoY Δpp</th><th>Signals</th><th>Verdict</th><th>Conf.</th></tr></thead>
    <tbody>${filtered.map((r) => `
      <tr class="${r.signal_count >= 2 ? "top-row" : ""}">
        <td>${esc(r.airport_en)}<div class="hint">${esc(r.airport)}</div></td>
        <td class="num">${esc(r.month_label)}</td>
        <td>${esc(humanize(r.tier_en || r.tier))}</td>
        <td class="num">${fmt(r.completion_pct)}%</td>
        <td class="num">${fmt(r.peer_pct)}%</td>
        <td class="num">${signed(r.delta_pp)}</td>
        <td class="num">${signed(r.peer_delta_pp)}</td>
        <td class="num">${r.yoy_delta_pp === null ? "n/a" : signed(r.yoy_delta_pp)}</td>
        <td class="num">${r.signal_count}</td>
        <td><span class="signal-chip ${r.signal_count > 0 ? "on" : "off"}">${esc(r.verdict)}</span></td>
        <td class="num">${fmt(r.confidence, 2)}</td>
      </tr>`).join("") || `<tr><td colspan="11" class="empty">No rows match.</td></tr>`}</tbody>`;
}

/* ------------------------------------------------------------------ exam */
async function runExam() {
  const btn = $("#run-exam");
  btn.disabled = true;
  setStatus("#exam-status", "Running the exam (offline writer)…");
  try {
    const data = await api("/api/tests/run", { method: "POST", body: JSON.stringify({ writer_mode: "offline", include_own: true }) });
    state.exam = data;
    const s = data.summary || {};
    const stats = [
      [String(s.official_pass ?? 0) + "/" + String(s.official_total ?? 15), "official tests"],
      [String(s.own_pass ?? 0) + "/" + String(s.own_total ?? 5), "own / adversarial"],
      [String(s.pass ?? 0) + "/" + String(s.total ?? 0), "total"],
    ];
    $("#exam-summary").innerHTML = stats.map(([n, l]) => `<div class="stat-card"><div class="stat-num">${esc(n)}</div><div class="stat-label">${esc(l)}</div></div>`).join("");
    const table = $("#exam-table");
    const runs = data.runs || [];
    if (!runs.length) {
      setStatus("#exam-status", data.note || "Exam runner not available on this branch yet.", "error");
      table.innerHTML = `<tbody><tr><td class="empty">${esc(data.note || "No exam results.")}</td></tr></tbody>`;
    } else {
      setStatus("#exam-status", `Exam finished: ${s.pass}/${s.total} passed.`, "ok");
      table.innerHTML = `
        <thead><tr><th>ID</th><th>Group</th><th>Type</th><th>Question</th><th>Expected</th><th>Forbidden</th><th>Result</th><th>Evidence</th></tr></thead>
        <tbody>${runs.map((r) => `
          <tr><td class="num">${esc(r.id)}</td><td>${esc(r.group)}</td><td>${esc(r.type)}</td>
          <td>${esc(r.question)}</td><td class="hint">${esc(r.expected || "")}</td><td class="hint">${esc(r.forbidden || "")}</td>
          <td class="${r.result === "pass" ? "pass" : "fail"}">${esc(r.result)}</td><td class="hint">${esc(r.evidence || r.error_note || "")}</td></tr>`).join("")}
        </tbody>`;
      $("#download-exam").disabled = false;
    }
  } catch (err) {
    setStatus("#exam-status", "Exam failed: " + err.message, "error");
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
async function loadFeedback() {
  try {
    const data = await api("/api/feedback");
    state.feedback = data.records || [];
    state.feedbackLoaded = true;
    const counts = { Accept: 0, Edit: 0, Reject: 0, Pending: 0 };
    state.feedback.forEach((r) => { counts[r.result] = (counts[r.result] || 0) + 1; });
    $("#feedback-stats").innerHTML = Object.entries(counts).map(([k, v]) =>
      `<div class="stat-card"><div class="stat-num">${v}</div><div class="stat-label">${esc(k)}</div></div>`).join("");
    const table = $("#feedback-table");
    table.innerHTML = `
      <thead><tr><th>Record</th><th>Event</th><th>Result</th><th>Reason</th><th>Final action</th><th>Reviewer</th><th>Date</th><th>Source</th></tr></thead>
      <tbody>${state.feedback.map((r) => `
        <tr><td class="num">${esc(r.rec_id)}</td><td>${esc(r.event_id)}</td>
        <td><strong>${esc(r.result)}</strong></td><td>${esc(r.reason || "—")}</td>
        <td>${esc(r.final_action || "—")}</td><td>${esc(r.reviewer || "—")}</td>
        <td>${esc(r.date || "—")}</td><td>${esc(r.source || "—")}</td></tr>`).join("")}</tbody>`;
  } catch (err) {
    $("#feedback-stats").innerHTML = `<div class="error-banner">Feedback load failed: ${esc(err.message)}</div>`;
  }
}

/* ------------------------------------------------------------------ wire up */
function bind() {
  $$(".tab-btn").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));

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
  $("#copy-msg").addEventListener("click", async () => {
    const text = $("#msg-body").textContent || "";
    try { await navigator.clipboard.writeText(text); toast("Message copied"); }
    catch (e) { toast("Copy not available in this browser", true); }
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
