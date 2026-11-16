/* Video Studio dashboard. Vanilla JS, hash routing, talks to helpers/studio_ui.py. */
const app = document.getElementById("app");
let STATE = null;
const fmt = (s) => { s = Math.max(0, +s || 0); const m = Math.floor(s / 60); return `${m}:${(s - m * 60).toFixed(2).padStart(5, "0")}`; };
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`(.+?)`/g, "<code>$1</code>").replace(/\n/g, "<br>");
const toast = (msg) => { let t = document.querySelector(".toast"); if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); } t.textContent = msg; t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1600); };

async function loadState() { STATE = await (await fetch("/api/state")).json(); document.getElementById("clock").textContent = "scanned " + new Date(STATE.generated).toLocaleTimeString(); }

function setNav(name) { document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("active", a.dataset.nav === name)); }


/* ---------- Upload (clips + separate voice recordings) ---------- */
const MODE_HINT = { voiceover: "my recording drives the cut; the clips are footage under it", commentary: "the clip keeps its own sound; my voice rides on top and the clip ducks under me", clips: "talking-head clips, no separate audio" };
function uploadForm(folder, mode) {
  const m = mode || "voiceover";
  return `<form class="upload" data-folder="${esc(folder || "")}">
    ${folder ? "" : `<label>Name <input name="slug" placeholder="e.g. claude-code-hooks" required></label>`}
    <div class="modes">${Object.entries(MODE_HINT).map(([k, hint]) => `<label><input type="radio" name="mode" value="${k}" ${k === m ? "checked" : ""}> <b>${k}</b><span>${hint}</span></label>`).join("")}</div>
    <label>Video clips <input type="file" name="footage" accept="video/*,.mov,.mp4,.m4v,.mkv,.webm" multiple></label>
    <label>Voice recording <input type="file" name="voice" accept="audio/*,.mp3,.m4a,.wav,.aac,.flac,.ogg" multiple></label>
    <label>Voice starts at <input name="voice_offset_s" type="number" step="0.1" min="0" value="0" style="width:80px"> s into the clip <span class="muted">(commentary only)</span></label>
    <label>Notes for the edit <input name="notes" placeholder="what the voice says over which clip; anything to keep or cut"></label>
    <div class="row"><button class="primary" type="submit">${folder ? "Add files" : "Create video"}</button><progress value="0" max="100" hidden></progress><span class="muted upstatus"></span></div>
  </form>`;
}
function wireUpload(form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const files = [...form.querySelectorAll("input[type=file]")].flatMap((i) => [...i.files]);
    const folder = form.dataset.folder;
    if (!files.length) return toast("pick at least one file");
    const prog = form.querySelector("progress"), st = form.querySelector(".upstatus");
    const xhr = new XMLHttpRequest();
    xhr.open("POST", folder ? "/api/upload/" + encodeURIComponent(folder) : "/api/upload");
    prog.hidden = false;
    xhr.upload.onprogress = (ev) => { if (ev.lengthComputable) prog.value = Math.round((ev.loaded / ev.total) * 100); };
    xhr.onload = async () => {
      let r = {}; try { r = JSON.parse(xhr.responseText); } catch (_) { /* not json */ }
      if (xhr.status !== 200 || r.error) { st.textContent = r.error || `upload failed (${xhr.status})`; prog.hidden = true; return; }
      toast(`saved to videos/${r.folder}` + (r.skipped.length ? ` · skipped ${r.skipped.join(", ")}` : ""));
      await loadState();
      const target = "#/video/" + encodeURIComponent(r.folder);
      if (location.hash === target) route(); else location.hash = target;
    };
    xhr.onerror = () => { st.textContent = "upload failed (network)"; prog.hidden = true; };
    st.textContent = `uploading ${files.length} file${files.length === 1 ? "" : "s"}… (${(files.reduce((a, f) => a + f.size, 0) / 1e6).toFixed(0)} MB)`;
    xhr.send(new FormData(form));
  });
}

/* ---------- Library ---------- */
function library() {
  setNav("library");
  const v = STATE.videos;
  const done = v.filter((x) => x.status === "done").length;
  app.innerHTML = `
    <h1>Library</h1><div class="sub">${v.length} video folder${v.length === 1 ? "" : "s"} · ${done} done · ${STATE.cards.length}/12 cards · ${STATE.inbox.length} drop${STATE.inbox.length === 1 ? "" : "s"} in the inbox</div>
    <details class="panel" id="newvideo"><summary><b>＋ New video</b> <span class="muted">— upload phone clips and, if you recorded one, a separate voice file</span></summary>${uploadForm(null)}</details>
    <div class="grid">${v.map((x, i) => `
      <a class="card" href="#/video/${encodeURIComponent(x.folder)}" style="animation-delay:${i * 40}ms">
        <div class="thumb ${x.clips[0] && x.clips[0].height > x.clips[0].width ? "vertical" : ""}" style="${x.thumb ? `background-image:url('${x.thumb}')` : ""}">
          ${x.duration || (x.clips[0] && x.clips[0].duration) ? `<span class="dur">${fmt(x.duration || x.clips[0].duration)}</span>` : ""}
        </div>
        <div class="body">
          <div class="title">${esc(x.slug)}</div>
          <div class="row"><span class="pill status-${esc(x.status)}">${esc(x.status)}</span><span class="muted">${esc(x.date)}</span><span class="muted">· ${x.clips.length} clip${x.clips.length === 1 ? "" : "s"}</span>${x.voice && x.voice.length ? `<span class="pill kind-sound" title="${esc(x.brief ? x.brief.mode : "")}">🎙 ${x.brief ? esc(x.brief.mode) : "voice"}</span>` : ""}</div>
          ${x.note ? `<div class="muted" style="margin-top:6px;font-size:13px">${esc(x.note)}</div>` : ""}
          <div class="dots" title="transcript · EDL · scenes · captions · sound · critic">
            ${["takes_packed.md", "edl.json", "scenes.json", "master.ass", "sound.json", "critic.md"].map((k) => `<span class="dot ${x.has[k] ? "on" : ""}"></span>`).join("")}
          </div>
        </div>
      </a>`).join("")}
      ${v.length === 0 ? `<div class="empty">No videos yet. Use “New video” above or drop clips into <code>videos/YYYY-MM-DD_slug/</code>.</div>` : ""}
    </div>`;
  wireUpload(document.querySelector("#newvideo form"));
  if (v.length === 0) document.getElementById("newvideo").open = true;
}

/* ---------- Video ---------- */
async function video(folder) {
  setNav("library");
  app.innerHTML = `<div class="loading">Loading ${esc(folder)}…</div>`;
  const d = await (await fetch("/api/video/" + encodeURIComponent(folder))).json();
  if (d.error) { app.innerHTML = `<div class="empty">${esc(d.error)}</div>`; return; }
  const edl = d.edl && !d.edl._error ? d.edl : null;
  const scenes = d.scenes && d.scenes.stretches ? d.scenes : null;
  const dur = +(edl && edl.total_duration_s) || (d.captions.length ? d.captions[d.captions.length - 1].end : 0) || 1;
  let notes = (d.feedback && d.feedback.notes) || [];

  const verdictMatch = /VERDICT:\s*(PASS|FIX FIRST|FAIL)/.exec(d.critic || "");
  const verdict = verdictMatch ? verdictMatch[1] : null;
  const vcls = verdict ? verdict.split(" ")[0] : "";

  const beats = edl ? (() => { let off = 0; return edl.ranges.map((r) => { const s = off; const len = +r.end - +r.start; off += len; return { s, e: off, ...r }; }); })() : [];
  const stretches = scenes ? scenes.stretches : [];
  const payoffs = stretches.filter((s) => s.graphic && s.graphic.payoff_t != null);
  const sfx = d.sound && d.sound.effects ? d.sound.effects : [];

  app.innerHTML = `
    <a class="muted" href="#/">← Library</a>
    <div class="row" style="margin:8px 0 4px"><h1 style="margin:0">${esc(d.slug)}</h1><span class="pill status-${esc(d.status)}">${esc(d.status)}</span>${verdict ? `<span class="verdict ${vcls}">critic: ${verdict}</span>` : ""}</div>
    <div class="sub">${esc(d.date)} · ${d.clips.length} source clip${d.clips.length === 1 ? "" : "s"}${d.preview_name ? ` · showing <code>${esc(d.preview_name)}</code>` : ""}${d.note ? ` · ${esc(d.note)}` : ""}</div>
    <div class="video-layout">
      <div>
        ${d.preview ? `<div class="player"><video id="vid" controls preload="metadata" src="${d.preview}"></video></div>` : `<div class="empty">No preview rendered yet. ${d.clips.length ? `Say <b>"edit videos/${esc(d.folder)}"</b> to start.` : "No clips in this folder."}</div>`}
        <div class="timeline" id="tl">
          ${beats.length ? `<div class="track" style="margin-top:14px"><span class="label">cuts · ${beats.length} ranges</span>${beats.map((b) => `<div class="seg beat" data-t="${b.s}" style="left:${(b.s / dur) * 100}%;width:${((b.e - b.s) / dur) * 100}%" title="${esc(b.beat)} · ${esc(b.source)} ${(+b.start).toFixed(2)}–${(+b.end).toFixed(2)}\n${esc(b.quote || "")}">${esc(b.beat || "")}</div>`).join("")}</div>` : ""}
          ${stretches.length ? `<div class="track" style="margin-top:18px"><span class="label">scenes</span>${stretches.map((s) => `<div class="seg" data-t="${s.start}" style="left:${(s.start / dur) * 100}%;width:${((s.end - s.start) / dur) * 100}%;background:var(--${esc(s.layout)},#333)" title="${esc(s.id)} ${esc(s.layout)}${s.graphic ? " · " + esc(s.graphic.slot) + " · " + esc(s.graphic.brief || "") : ""}">${esc(s.layout)}${s.graphic ? " ✦" : ""}</div>`).join("")}
            ${payoffs.map((s) => `<div class="mark payoff" data-t="${s.graphic.payoff_t}" style="left:${(s.graphic.payoff_t / dur) * 100}%"><span class="tip">payoff “${esc(s.graphic.payoff_word)}” @ ${fmt(s.graphic.payoff_t)}</span></div>`).join("")}</div>` : ""}
          ${d.captions.length ? `<div class="track" style="margin-top:18px"><span class="label">captions · ${d.captions.length} word events</span>${d.captions.map((c, i) => `<div class="seg cue" data-i="${i}" data-t="${c.start}" style="left:${(c.start / dur) * 100}%;width:${Math.max(0.15, ((c.end - c.start) / dur) * 100)}%" title="${esc(c.text)}"></div>`).join("")}</div>` : ""}
          ${sfx.length || notes.length ? `<div class="track" style="margin-top:18px;background:transparent"><span class="label">sound · notes</span>
            ${sfx.map((f) => `<div class="mark sfx" data-t="${f.contact_s}" style="left:${(f.contact_s / dur) * 100}%"><span class="tip">${esc(f.effect)} @ ${fmt(f.contact_s)} · ${esc(f.event || "")}</span></div>`).join("")}
            <span id="notemarks"></span></div>` : ""}
          <div class="playhead" id="ph" style="left:14px"></div>
          <div class="ruler"><span>0:00</span><span>${fmt(dur / 2)}</span><span>${fmt(dur)}</span></div>
        </div>
        <div id="cue" class="muted" style="margin-top:8px;min-height:22px;font-size:18px;font-weight:700"></div>

        <div class="tabs" id="tabs">${["Cut", "Scenes", "Sound", "Captions", "Animations", "Critic", "Transcript", "Memory"].map((t, i) => `<button data-tab="${t}" class="${i === 0 ? "active" : ""}">${t}</button>`).join("")}</div>
        <div id="tabbody"></div>
      </div>
      <aside>
        <div class="panel notes">
          <h3>Notes for “apply my notes”</h3>
          <div class="muted" style="font-size:13px;margin-bottom:8px">Pause where something is wrong, write the note, add. Saved to <code>edit/feedback.json</code>.</div>
          <textarea id="notetext" placeholder="e.g. cut is late, caption hides the number, music too loud here"></textarea>
          <div class="row" style="margin-top:8px"><button class="primary" id="addnote">Add at <span id="notet">0:00.00</span></button><button class="ghost" id="clearnotes" title="Remove all notes">clear</button></div>
          <div id="notelist"></div>
        </div>
        <div class="panel">
          <h3>Sources</h3>
          ${d.brief ? `<div class="row" style="margin-bottom:10px"><span class="pill kind-sound">${esc(d.brief.mode)}</span><span class="muted" style="font-size:12px">${esc(MODE_HINT[d.brief.mode] || "")}</span></div>` : ""}
          ${d.clips.map((c) => `<div class="kv" style="margin-bottom:8px"><b>${esc(c.name)}</b><span class="mono">${c.width}×${c.height} · ${c.fps} fps · ${fmt(c.duration)} · ${c.size_mb} MB</span></div>`).join("") || `<span class="muted">no clips</span>`}
          ${(d.voice || []).map((v) => `<div class="kv" style="margin-top:8px"><b>🎙 ${esc(v.name)}</b><span class="mono">${fmt(v.duration)} · ${v.size_mb} MB</span></div><audio controls preload="none" src="${v.url}" style="width:100%;height:32px;margin:4px 0 6px"></audio>`).join("")}
          ${d.brief ? `<form id="brieff" class="upload" style="margin-top:10px">
            <label>Mode <select name="mode">${Object.keys(MODE_HINT).map((k) => `<option value="${k}" ${d.brief.mode === k ? "selected" : ""}>${k}</option>`).join("")}</select></label>
            <label>Voice starts at <input name="voice_offset_s" type="number" step="0.1" min="0" value="${+d.brief.voice_offset_s || 0}" style="width:80px"> s</label>
            <label>Notes <input name="notes" value="${esc(d.brief.notes || "")}"></label>
            <button type="submit">Save brief</button></form>` : ""}
          <details style="margin-top:12px"><summary>Add files</summary>${uploadForm(d.folder, d.brief ? d.brief.mode : "clips")}</details>
        </div>
        <div class="panel">
          <h3>Artifacts</h3>
          <div class="kv">${Object.entries(d.has).map(([k, v]) => `<b>${esc(k)}</b><span style="color:${v ? "var(--ok)" : "var(--muted)"}">${v ? "✓" : "—"}</span>`).join("")}</div>
        </div>
      </aside>
    </div>`;

  wireUpload(document.querySelector("aside .upload[data-folder]"));
  const brieff = document.getElementById("brieff");
  if (brieff) brieff.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(brieff);
    const r = await (await fetch("/api/brief/" + encodeURIComponent(folder), { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: fd.get("mode"), voice_offset_s: +fd.get("voice_offset_s") || 0, notes: fd.get("notes") }) })).json();
    toast(r.error ? r.error : "brief saved");
  });
  const vid = document.getElementById("vid");
  const tl = document.getElementById("tl");
  const ph = document.getElementById("ph");
  const cueEl = document.getElementById("cue");
  const seek = (t) => { if (vid) { vid.currentTime = +t; vid.play().catch(() => {}); } };
  tl.querySelectorAll("[data-t]").forEach((el) => el.addEventListener("click", (e) => { e.stopPropagation(); seek(el.dataset.t); }));
  const inner = () => { const r = tl.getBoundingClientRect(); return { left: 14, width: r.width - 28 }; };
  tl.addEventListener("click", (e) => { const r = tl.getBoundingClientRect(); const { left, width } = inner(); seek(Math.max(0, Math.min(dur, ((e.clientX - r.left - left) / width) * dur))); });
  const paint = (t) => {
    const { left, width } = inner();
    ph.style.left = left + (t / dur) * width + "px";
    document.getElementById("notet").textContent = fmt(t);
    const ev = d.captions.find((c) => t >= c.start && t < c.end);
    cueEl.innerHTML = ev ? ev.text.split(" ").map((w, i) => (i === ev.hl ? `<span style="color:var(--accent);font-size:1.12em">${esc(w)}</span>` : esc(w))).join(" ") : "";
    tl.querySelectorAll(".seg.cue").forEach((el) => el.classList.toggle("hl", ev && d.captions[+el.dataset.i] === ev));
  };
  if (vid) vid.addEventListener("timeupdate", () => paint(vid.currentTime));
  paint(0);

  /* notes */
  const renderNotes = () => {
    document.getElementById("notelist").innerHTML = notes.length ? notes.map((n, i) => `
      <div class="note ${n.done ? "done" : ""}"><span class="t" data-t="${n.t}">${fmt(n.t)}</span><span class="text">${esc(n.text)}</span><span class="x" data-i="${i}" title="remove">✕</span></div>`).join("")
      : `<div class="muted" style="padding-top:10px;font-size:13px">No notes yet.</div>`;
    document.querySelectorAll("#notelist .t").forEach((el) => el.addEventListener("click", () => seek(el.dataset.t)));
    document.querySelectorAll("#notelist .x").forEach((el) => el.addEventListener("click", () => { notes = notes.filter((_, i) => i !== +el.dataset.i); save(); }));
    const nm = document.getElementById("notemarks");
    if (nm) nm.innerHTML = notes.map((n) => `<div class="mark note" data-t="${n.t}" style="left:${(n.t / dur) * 100}%"><span class="tip">${esc(n.text)}</span></div>`).join("");
    if (nm) nm.querySelectorAll("[data-t]").forEach((el) => el.addEventListener("click", (e) => { e.stopPropagation(); seek(el.dataset.t); }));
  };
  const save = async () => {
    const r = await (await fetch("/api/feedback/" + encodeURIComponent(folder), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes }) })).json();
    renderNotes(); toast(r.ok ? "saved to edit/feedback.json" : "save failed");
  };
  document.getElementById("addnote").addEventListener("click", () => {
    const ta = document.getElementById("notetext"); const text = ta.value.trim(); if (!text) return;
    notes = [...notes, { t: vid ? vid.currentTime : 0, text }].sort((a, b) => a.t - b.t); ta.value = ""; save();
  });
  document.getElementById("clearnotes").addEventListener("click", () => { if (notes.length && confirm("Remove all notes?")) { notes = []; save(); } });
  renderNotes();

  /* tabs */
  const body = document.getElementById("tabbody");
  const tabs = {
    Cut: () => edl ? `<table><tr><th>#</th><th>beat</th><th>source</th><th>in → out</th><th>len</th><th>quote / reason</th></tr>${beats.map((b, i) => `<tr><td class="mono">${i + 1}</td><td>${esc(b.beat)}</td><td class="mono">${esc(b.source)}</td><td class="mono">${(+b.start).toFixed(2)} → ${(+b.end).toFixed(2)}</td><td class="mono">${(b.e - b.s).toFixed(2)}s</td><td><div>${esc(b.quote || "")}</div><div class="muted">${esc(b.reason || "")}</div></td></tr>`).join("")}</table><div class="row" style="margin-top:12px"><span class="stat"><b>${fmt(dur)}</b><span>total</span></span><span class="stat"><b>${beats.length}</b><span>ranges</span></span><span class="stat"><b>${esc(edl.grade || "—")}</b><span>grade</span></span><span class="stat"><b>${esc(edl.profile || "—")}</b><span>profile</span></span></div>` : `<div class="empty">No EDL yet.</div>`,
    Scenes: () => scenes ? `<table><tr><th>id</th><th>start → end</th><th>layout</th><th>graphic</th></tr>${stretches.map((s) => `<tr><td class="mono">${esc(s.id)}</td><td class="mono">${fmt(s.start)} → ${fmt(s.end)}</td><td>${esc(s.layout)}</td><td>${s.graphic ? `<b>${esc(s.graphic.slot)}</b> · ${esc(s.graphic.card || "")}<br><span class="muted">payoff “${esc(s.graphic.payoff_word)}” @ ${fmt(s.graphic.payoff_t)} · enter ${fmt(s.graphic.enter_t)} · exit ${fmt(s.graphic.exit_t)}</span><br>${esc(s.graphic.brief || "")}` : "—"}</td></tr>`).join("")}</table>` : `<div class="empty">No scenes.json yet.</div>`,
    Sound: () => d.sound ? `${d.sound_report && d.sound_report.final ? `<div class="row" style="margin-bottom:12px"><span class="stat"><b>${d.sound_report.final.integrated_lufs ?? "—"}</b><span>LUFS</span></span><span class="stat"><b>${d.sound_report.final.true_peak_dbtp ?? "—"}</b><span>dBTP</span></span>${d.sound_report.music && d.sound_report.music.bed_under_speech_db != null ? `<span class="stat"><b>${d.sound_report.music.bed_under_speech_db} dB</b><span>music under speech</span></span>` : ""}</div>` : ""}<table><tr><th>effect</th><th>contact</th><th>event</th><th>file</th></tr>${sfx.map((f) => `<tr><td>${esc(f.effect)}</td><td class="mono">${fmt(f.contact_s)}</td><td>${esc(f.event || "")}</td><td class="mono muted">${esc(f.file)}</td></tr>`).join("")}</table>${d.sound.music ? `<p class="muted">music: <code>${esc(d.sound.music.file)}</code> at ${d.sound.music.gain_db} dB</p>` : ""}${d.sound_report && d.sound_report.sections && d.sound_report.sections.length ? `<h3>Sections</h3><table><tr><th>name</th><th>range</th><th>LUFS</th><th>TP</th></tr>${d.sound_report.sections.map((s) => `<tr><td>${esc(s.name)}</td><td class="mono">${fmt(s.start)}–${fmt(s.end)}</td><td class="mono">${s.integrated_lufs ?? "—"}</td><td class="mono">${s.true_peak_dbtp ?? "—"}</td></tr>`).join("")}</table>` : ""}` : `<div class="empty">No sound.json yet.</div>`,
    Captions: () => d.captions.length ? `<table><tr><th>start</th><th>end</th><th>cue (highlighted word in yellow)</th></tr>${d.captions.map((c) => `<tr><td class="mono">${fmt(c.start)}</td><td class="mono">${fmt(c.end)}</td><td>${c.text.split(" ").map((w, i) => (i === c.hl ? `<b style="color:var(--accent)">${esc(w)}</b>` : esc(w))).join(" ")}</td></tr>`).join("")}</table>` : `<div class="empty">No master.ass yet.</div>`,
    Animations: () => d.animations.length ? d.animations.map((a) => `<div class="anim">${a.landing ? `<img src="${a.landing}" alt="landing frame">` : `<div></div>`}<div><b>${esc(a.slot)}</b>${a.render ? ` · <a href="${a.render}" target="_blank" style="color:var(--accent-2)">open render</a>` : ""}<details><summary>reasoning</summary><pre>${esc(a.reasoning)}</pre></details></div></div>`).join("") : `<div class="empty">No animation slots yet.</div>`,
    Critic: () => d.critic ? `<pre>${esc(d.critic)}</pre>` : `<div class="empty">No critic report yet.</div>`,
    Transcript: () => d.takes_packed ? `<pre>${esc(d.takes_packed)}</pre>` : `<div class="empty">Not transcribed yet.</div>`,
    Memory: () => d.project ? `<pre>${esc(d.project)}</pre>` : `<div class="empty">No project.md yet (written at the end of the first session).</div>`,
  };
  const show = (name) => { body.innerHTML = tabs[name](); document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name)); };
  document.querySelectorAll("#tabs button").forEach((b) => b.addEventListener("click", () => show(b.dataset.tab)));
  show("Cut");
}

/* ---------- Cards ---------- */
function cards() {
  setNav("cards");
  app.innerHTML = `<h1>Cards</h1><div class="sub">${STATE.cards.length} of 12 · patterns learned from references, rewritten in my brand · drop references into <code>cards/_inbox/</code> and say “process the inbox”${STATE.inbox.length ? ` · <b style="color:var(--accent)">${STATE.inbox.length} unprocessed drop${STATE.inbox.length === 1 ? "" : "s"}</b>` : ""}</div>
    <div class="cardsgrid">${STATE.cards.map((c, i) => `<div class="card cardx" style="animation-delay:${i * 35}ms"><div class="body">
      <div class="row"><span class="pill kind-${esc(c.kind)}">${esc(c.kind)}</span><span class="muted mono" style="font-size:11px">${esc(c.file)}</span></div>
      <div class="title" style="margin-top:8px">${esc(c.title)}</div>
      <div class="what">${esc(c.what)}</div>
      <div class="kv"><b>use when</b><span>${esc(c.use_when)}</span><b>avoid when</b><span>${esc(c.avoid_when)}</span></div>
      <details style="margin-top:8px"><summary>prompt</summary><div class="prompt open">${esc(c.prompt)}</div></details>
    </div></div>`).join("")}</div>`;
}

/* ---------- Rules / Decisions / How ---------- */
function rules() {
  setNav("rules");
  const bySection = {};
  STATE.style.forEach((r) => (bySection[r.section] = bySection[r.section] || []).push(r));
  app.innerHTML = `<h1>STYLE.md</h1><div class="sub">${STATE.style.length} rules · every agent reads these, the critic checks every line · say “learn from my reviews” to add more</div>
    ${Object.entries(bySection).map(([s, rs]) => `<div class="panel"><h3>${esc(s)}</h3>${rs.map((r) => `<div class="rule"><span>${esc(r.rule)}</span><span class="meta">${esc(r.date)} · ${esc(r.origin)}</span></div>`).join("")}</div>`).join("")}`;
}
function decisions() {
  setNav("decisions");
  app.innerHTML = `<h1>DECISIONS.md</h1><div class="sub">${STATE.decisions.length} entries, newest first</div>
    ${STATE.decisions.map((d) => `<div class="decision"><span class="d">${esc(d.date)}</span> <b>${esc(d.title)}</b><p>${md(d.body)}</p></div>`).join("")}`;
}
function how() {
  setNav("how");
  const rows = STATE.how.split("\n").filter((l) => l.startsWith("|") && !/^\|\s*-/.test(l) && !/^\|\s*#/.test(l)).map((l) => l.split("|").slice(1, -1).map((c) => c.trim()));
  const tail = STATE.how.split("\n").filter((l) => l.startsWith("Side loops")).join(" ");
  app.innerHTML = `<h1>How it works</h1><div class="sub">one video through the system</div>
    <table><tr><th>#</th><th>I say / it does</th><th>file produced</th></tr>${rows.map((r) => `<tr><td class="mono">${esc(r[0])}</td><td>${md(r[1])}</td><td class="mono muted">${md(r[2])}</td></tr>`).join("")}</table>
    <p class="muted" style="margin-top:16px">${md(tail)}</p>`;
}

/* ---------- router ---------- */
async function route() {
  if (!STATE) await loadState();
  const h = location.hash || "#/";
  if (h.startsWith("#/video/")) return video(decodeURIComponent(h.slice(8)));
  if (h === "#/cards") return cards();
  if (h === "#/rules") return rules();
  if (h === "#/decisions") return decisions();
  if (h === "#/how") return how();
  return library();
}
window.addEventListener("hashchange", route);
document.getElementById("refresh").addEventListener("click", async () => { await loadState(); route(); toast("rescanned"); });
route();
