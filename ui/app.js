/* Vetto Video Engine — the editor page.
   One project = one piece of raw footage. A project has versions: the same cut edited in different styles.
   Every step ends with Alina's approval; nothing renders until the storyboard is approved. */
'use strict';
const STEPS = [
  { id: 'footage', name: 'Footage' }, { id: 'brief', name: 'Brief' }, { id: 'cut', name: 'Cut' },
  { id: 'style', name: 'Style' }, { id: 'hook', name: 'Hook' }, { id: 'effects', name: 'Effects' },
  { id: 'memes', name: 'Memes' }, { id: 'text', name: 'Text' }, { id: 'sound', name: 'Sound' }, { id: 'outputs', name: 'Outputs' },
  { id: 'storyboard', name: 'Trim & view' }, { id: 'export', name: 'Check & export' },
];
const ACCOUNTS = ['Fred Mey', 'Frank Mey', 'feedmeplzthanks 2', 'Hongry Royalty'];
const PALETTE_FOR_ACCOUNT = { 'Fred Mey': 'fred', 'Frank Mey': 'frank', 'feedmeplzthanks 2': 'fmpt2', 'Hongry Royalty': 'hr' };
// PDF styles name type by look, not by family: these are the closest Vetto faces (a draft until Alina picks)
const STYLE_FONT = { 'Inter Tight 600': 'Instrument Sans', 'Inter Tight 800': 'Instrument Sans', 'Inter 600': 'Instrument Sans',
  'Inter 700': 'Instrument Sans', 'Inter 800': 'TikTok Sans', 'Instrument Serif Italic': 'Bodoni Moda' };

let LIB = null, P = null, STEP = 'footage', IMAGES = [], ATTACH = [], PENDING = [], SETTINGS = {}, CJOB = null, VIEW = null, STOCK = null, MEMES = null, MEMELIB = null;
let cutMode = 'cut';
let selWord = null, selEnd = null, lastClick = null, fontFilter = 'all', hookQuery = '', sfxCat = 'all', effGroup = 'all';
let saveTimer = null, playOriginal = false;

const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = t => { t = Math.max(0, t || 0); const m = Math.floor(t / 60); return `${m}:${(t - m * 60).toFixed(1).padStart(4, '0')}`; };
const api = async (path, opts = {}) => {
  const r = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
};
const V = () => P.versions.find(v => v.id === P.current);
const lib = k => LIB[k] || [];
const styleById = id => lib('styles').find(s => s.id === id);
const effectById = id => lib('effects').find(e => e.id === id);
const formatById = id => lib('formats').find(f => f.id === id);
const fontByName = n => (LIB?.looks?.fonts || []).find(f => f.family === n);
const pace = () => lib('pacing').find(x => x.name === (P.brief.pace || 'Medium')) || {};

function toast(msg) {
  const t = document.createElement('div'); t.className = 'toast-mini'; t.textContent = msg;
  document.body.append(t); setTimeout(() => t.remove(), 2600);
}

/* ------------------------------------------------------------ edit decisions (mirror of engine/edit.py) */
function keepRanges() {
  // mirror of engine/edit.py keep_ranges: voice-snapped edges, pace beats, only silence merged back
  if (!P.edl) return P.source ? [[0, P.source.duration]] : [];
  const E = P.edl, { words, pauses } = E, total = P.source.duration;
  const shortTo = E.short_to ?? 0.15, pauseMin = E.pause_min ?? 0.45, leadM = E.lead ?? 0.06, tailM = E.tail ?? 0.10, minCut = E.min_cut ?? 0.25;
  const ws = w => w.start_r ?? w.start, we = w => w.end_r ?? w.end;
  const byAfter = new Map(pauses.filter(p => p.after_word != null).map(p => [p.after_word, p]));
  const leadPause = pauses.find(p => p.after_word == null);
  const beat = w => { const n = words[w.i + 1]; if (n && n.seg !== w.seg && /[.!?]$/.test(w.text)) return E.beat_topic ?? .9;
    if (/[.!?…]$/.test(w.text)) return E.beat_sentence ?? .45; return shortTo; };
  const r = [];
  for (const w of words) {
    if (w.cut) continue;
    const prev = w.i ? words[w.i - 1] : null, nxt = words[w.i + 1] || null;
    let s = ws(w), e = we(w);
    const pp = w.i ? byAfter.get(w.i - 1) : leadPause;
    if (pp && !pp.keep) s = Math.max(pp.start, prev ? s - beat(prev) * .4 : s - leadM);
    else if (pp && pp.keep) s = prev == null ? pp.start : s;
    else if (prev && prev.cut) s = Math.max((we(prev) + s) / 2, s - leadM);
    else if (!prev) s = Math.max(0, s - leadM);
    const p = byAfter.get(w.i);
    if (p) e = p.keep ? p.end : Math.min(p.end, e + beat(w) * .6);
    else if (nxt && nxt.cut) e = Math.min((e + ws(nxt)) / 2, e + tailM);
    else if (nxt) e = Math.max(e, Math.min(ws(nxt), e + pauseMin));
    else e = Math.min(total, e + tailM);
    r.push([s, e, !!(prev && prev.cut)]);
  }
  const m = [];
  for (const x of r) {
    const last = m[m.length - 1];
    if (last && x[0] - last[1] < minCut && !x[2] && x[0] >= last[0]) last[1] = Math.max(last[1], x[1]);
    else m.push([x[0], x[1]]);
  }
  return m.filter(([a, b]) => b - a > 0.04).map(([a, b]) => [a, Math.min(b, total)]);
}
function mapTime(t, ranges) {
  let acc = 0;
  for (const [a, b] of ranges) { if (t < a) return null; if (t <= b) return acc + (t - a); acc += b - a; }
  return null;
}
const outLen = ranges => ranges.reduce((s, [a, b]) => s + b - a, 0);
function recomputePauses() {
  if (!P.edl) return;
  const p = pace(), min = p.shorten_pauses_over ?? 0.45, keep = new Map(P.edl.pauses.map(x => [x.after_word + ':' + x.before_word, x.keep]));
  const W = P.edl.words, total = P.source.duration, out = [];
  const edges = [[0, W[0]?.start ?? 0, null, 0], ...W.slice(0, -1).map((a, k) => [a.end, W[k + 1].start, a.i, W[k + 1].i]), [W[W.length - 1].end, total, W[W.length - 1].i, null]];
  for (const [s, e, before, after] of edges) {
    if (e - s < min) continue;
    const prev = before != null ? W[before].text : '';
    out.push({ id: 'p' + out.length, start: s, end: e, dur: +(e - s).toFixed(2), after_word: before, before_word: after,
      keep: keep.get(before + ':' + after) ?? false, hint: prev.endsWith('?') ? 'after a question: worth keeping?' : null, edge: before == null || after == null });
  }
  P.edl.pauses = out; P.edl.pause_min = min;
  Object.assign(P.edl, { short_to: p.beat_mid ?? .15, beat_sentence: p.beat_sentence ?? .45, beat_topic: p.beat_topic ?? .9,
    min_cut: p.min_cut ?? .25, lead: p.lead ?? .06, tail: p.tail ?? .10, punch_in: p.punch_in ?? null, lufs: p.lufs ?? -14 });
}
function sentences() {
  if (!P.edl) return [];
  const out = []; let cur = [];
  for (const w of P.edl.words) {
    cur.push(w);
    if (/[.?!…]$/.test(w.text) || (P.edl.words[w.i + 1] && P.edl.words[w.i + 1].seg !== w.seg && cur.length > 3)) { out.push(cur); cur = []; }
  }
  if (cur.length) out.push(cur);
  return out;
}
function beats() {
  const ranges = keepRanges();
  return sentences().map((ws, k) => {
    const kept = ws.filter(w => !w.cut);
    if (!kept.length) return null;
    const s = mapTime(kept[0].start, ranges), e = mapTime(kept[kept.length - 1].end, ranges) ?? s + 0.5;
    const idx = new Set(ws.map(w => w.i));
    const v = V();
    return { k, words: kept, text: kept.map(w => w.text).join(' '), src: kept[0].start, start: s ?? 0, end: e,
      effects: v.effects.filter(x => idx.has(x.word_i) && x.status !== 'removed'),
      overlays: v.overlays.filter(x => idx.has(x.word_i) && x.status !== 'removed'),
      sfx: v.sfx.filter(x => idx.has(x.word_i) && x.status !== 'removed') };
  }).filter(Boolean);
}
function stats() {
  const r = keepRanges(), out = outLen(r);
  if (!P.edl) return { out, src: P.source?.duration || 0 };
  const kept = P.edl.words.filter(w => !w.cut).length;
  return { out, src: P.source.duration, cut: P.edl.words.filter(w => w.cut).length, words: P.edl.words.length,
    pauses: P.edl.pauses.length, short: P.edl.pauses.filter(p => !p.keep).length, wpm: out ? Math.round(kept / out * 60) : 0 };
}

/* ------------------------------------------------------------ saving and approvals */
/* save the project; if another tab (or a finished job) saved a newer copy, take that one instead of overwriting it */
async function putP() {
  const r = await fetch(`/api/projects/${P.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(P) });
  const j = await r.json().catch(() => ({}));
  if (r.status === 409 && j.project) {
    P = j.project; LAST = JSON.stringify(P); HIST = [];
    renderHead(); renderPanel(); setSource(); updateChanges();
    toast('This video was changed in another tab: showing the newest version. Please redo your last change.');
    return false;
  }
  if (!r.ok) throw new Error(j.error || r.statusText);
  P = j; return true;
}
function save() {
  $('#saved').textContent = 'Saving…'; $('#saved').className = 'pill';
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {
    try { const ok = await putP(); $('#saved').textContent = ok ? 'Saved' : 'Reloaded'; $('#saved').className = ok ? 'pill ok' : 'pill warn'; }
    catch (e) { $('#saved').textContent = 'Not saved'; $('#saved').className = 'pill bad'; }
  }, 450);
}
function touch(step, ...also) {
  if (LAST) { HIST.push(LAST); if (HIST.length > 60) HIST.shift(); }
  for (const st of [step, ...also]) {
    const s = V().steps[st];
    if (s && s.status === 'approved') { s.status = 'changed'; s.note = 'changed after approval'; }
  }
  if (step !== 'storyboard' && step !== 'export' && V().steps.storyboard.status === 'approved') V().steps.storyboard.status = 'changed';
  save(); renderHead();
  LAST = JSON.stringify(P); updateChanges();
}
function approve(step) {
  V().steps[step] = { status: 'approved', at: new Date().toISOString().slice(0, 16).replace('T', ' ') };
  save();
  const i = STEPS.findIndex(s => s.id === step);
  go(STEPS[Math.min(i + 1, STEPS.length - 1)].id);
}
const stepState = id => V().steps[id]?.status || 'open';

/* ------------------------------------------------------------ jobs */
async function runJob(promise, label) {
  const j = await promise;
  if (j.error) throw new Error(j.error);
  toast(label + '…');
  for (;;) {
    await new Promise(r => setTimeout(r, 1000));
    const s = await api(`/api/jobs/${j.id}`);
    if (s.status === 'done') { P = await api(`/api/projects/${P.id}`); LAST = JSON.stringify(P); toast(label + ': done'); return s.result; }
    if (s.status === 'error') { toast(label + ' failed'); console.error(s.error); alert(label + ' failed:\n' + s.error.slice(0, 600)); return null; }
  }
}

/* ------------------------------------------------------------ routing */
async function route() {
  const m = location.hash.match(/^#\/p\/([^/]+)(?:\/(\w+))?/);
  if (!LIB) LIB = await api('/api/library');
  SETTINGS = await api('/api/settings').catch(() => SETTINGS);
  if (!m) { P = null; return renderStart(); }
  if (!P || P.id !== m[1]) {
    // a video that was deleted (or a stale tab): back to the start screen instead of an empty editor (18 Nov 2026)
    const got = await api(`/api/projects/${m[1]}`).catch(() => null);
    if (!got || !got.id || !got.versions) { P = null; location.hash = '#/'; toast('That video is not here any more (deleted?)'); return; }
    P = got; IMAGES = await api(`/api/projects/${m[1]}/images`).catch(() => []);
    ATTACH = await api(`/api/projects/${m[1]}/attachments`).catch(() => []); PENDING = []; CJOB = null; renderEditor();
    const running = (await api('/api/jobs').catch(() => [])).find(j => j.kind === 'claude-edit' && (j.args || []).includes(P.id));
    if (running) watchClaude(running, running.args[2]);
  }
  STEP = m[2] || STEP;
  renderHead(); renderPanel();
}
function go(step) { location.hash = `#/p/${P.id}/${step}`; }
window.addEventListener('hashchange', route);

/* ------------------------------------------------------------ start screen */
async function renderStart() {
  $('#dock').hidden = true;
  const list = await api('/api/projects');
  $('#main').innerHTML = `
  <div class="start">
    <div>
      <p class="eyebrow">Vetto · video engine</p>
      <h1 class="statement">Vetto Video<br>Editing Engine</h1>
      <p class="lead">In your style, with your face and your voice. Cut by word, a named style, a hook, effects on words, text and sound: you check every step and the storyboard before anything is exported.</p>
      <div class="cards">
        ${list.map(p => `<a class="card item" href="#/p/${p.id}/footage"><button class="small remove del-proj" type="button" data-del="${p.id}" data-name="${esc(p.name)}" title="Move this video to the Trash">✕ Delete</button><b>${esc(p.name)}</b><span class="meta">${esc(p.account || 'no account yet')} · ${p.versions} version${p.versions > 1 ? 's' : ''} · ${p.has_source ? 'footage in' : 'no footage yet'}</span><span class="meta">updated ${esc(p.updated.replace('T', ' '))}</span></a>`).join('') || '<div class="empty">No videos yet. Start one on the right.</div>'}
      </div>
    </div>
    <form class="card" id="newp">
      <h2>New video</h2>
      <label>Working name<input name="name" placeholder="e.g. Frank tries the €15 bonus" required></label>
      <p class="meta">You add the footage on the next screen.</p>
      <button class="primary" type="submit">Start</button>
    </form>
  </div>`;
  document.querySelectorAll('[data-del]').forEach(b => b.onclick = async e => {
    e.preventDefault(); e.stopPropagation();
    if (!confirm(`Delete “${b.dataset.name}”?\n\nThe whole video (footage, cut, versions, renders) moves to the Trash on this Mac. You can put it back from the Trash.`)) return;
    const r = await fetch(`/api/projects/${b.dataset.del}/delete-project`, { method: 'POST' });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { alert(j.error || 'Could not delete it.'); return; }
    toast('Moved to the Trash'); renderStart();
  });
  $('#newp').onsubmit = async e => {
    e.preventDefault();
    const p = await api('/api/projects', { method: 'POST', body: JSON.stringify({ name: e.target.name.value }) });
    location.hash = `#/p/${p.id}/footage`;
  };
}

/* ------------------------------------------------------------ editor skeleton */
function renderEditor() {
  $('#main').innerHTML = `
    <div class="studio">
      <aside class="left">
        <div class="viewseg" id="viewseg"></div>
        <div class="frame" id="frame">
          <video id="vid" playsinline preload="auto"></video>
          <div class="ov" id="ov"><div class="safe"></div></div>
          <div class="txtedit" id="txtedit"></div>
          <div class="empty-frame" id="noclip">Your footage plays here, cut and captioned as you go.</div>
          <span class="cutclock" id="clock">cut 0:00.0 / 0:00.0</span>
        </div>
        <div class="ctl"><button type="button" data-seek="-5">−5 s</button><button type="button" id="play">▶ Play</button><button type="button" data-seek="5">+5 s</button></div>
        <div class="scrub" id="scrub"><i id="scrubfill"></i><b id="scrubdot"></b></div>
        <div class="ctl2"><span id="changes">Nothing changed yet</span><button class="small" id="undo" type="button" disabled>Undo</button></div>
        <div class="opts-row"><label class="check"><input type="checkbox" id="orig"> original</label><label class="check"><input type="checkbox" id="safe"> safe zone</label><label class="check"><input type="checkbox" id="edtext" checked> move text</label></div>
        <p class="note">The clip skips what you cut, live. Captions, the hook and images show roughly where they will sit in the final reel.</p>
        <div class="thumbs" id="thumbs"></div>
        <div class="versions" id="versions"></div>
      </aside>
      <section class="right">
        <div class="head" id="head"></div>
        <div class="panel" id="panel"></div>
      </section>
    </div>`;
  const vid = $('#vid');
  $('#play').onclick = () => { if (!vid.src) return; if (vid.paused) { const r = keepRanges(); if (!playOriginal && r.length && mapTime(vid.currentTime, r) == null) vid.currentTime = r[0][0]; vid.play(); } else vid.pause(); };
  vid.onplay = () => $('#play').textContent = '■ Pause';
  vid.onpause = () => $('#play').textContent = '▶ Play';
  document.querySelectorAll('[data-seek]').forEach(b => b.onclick = () => { if (vid.src) vid.currentTime = Math.max(0, vid.currentTime + +b.dataset.seek); });
  $('#scrub').onclick = e => { if (!vid.duration) return; const r = $('#scrub').getBoundingClientRect(); vid.currentTime = (e.clientX - r.left) / r.width * vid.duration; };
  $('#undo').onclick = undo;
  $('#orig').onchange = e => { playOriginal = e.target.checked; };
  $('#safe').onchange = e => $('#frame').classList.toggle('show-safe', e.target.checked);
  $('#edtext').onchange = e => { $('#txtedit').hidden = !e.target.checked; };
  bindTextEdit();
  HIST = []; LAST = JSON.stringify(P); updateChanges();
  setSource();
  requestAnimationFrame(tick);
}
/* undo: every change keeps the project as it was just before */
let HIST = [], LAST = null;
function updateChanges() {
  const u = $('#undo'); if (!u) return;
  u.disabled = !HIST.length;
  $('#changes').textContent = HIST.length ? `${HIST.length} change${HIST.length > 1 ? 's' : ''} this session` : 'Nothing changed yet';
}
function undo() {
  if (!HIST.length) return;
  P = JSON.parse(HIST.pop()); LAST = JSON.stringify(P);
  save(); renderHead(); renderPanel(); updateChanges(); toast('Undone');
}
/* the finished reel of this version (18–24 Nov 2026: the preview must match Check & export once a reel exists) */
function finalRender() {
  const rs = (V()?.renders || []).filter(r => !r.preview);
  return rs[rs.length - 1] || null;
}
function viewMode() {
  const fr = finalRender();
  if (!fr) return 'live';
  if (VIEW) return VIEW;
  return fr.claude ? 'final' : 'live';       // after Claude's edit the preview opens on that reel
}
function renderViewSeg() {
  const seg = $('#viewseg'); if (!seg || !P) return;
  const fr = finalRender();
  if (!fr) { seg.innerHTML = ''; return; }
  const m = viewMode();
  seg.innerHTML = `<div class="seg"><a href="#" data-view="final" ${m === 'final' ? 'aria-current="true"' : ''}>Final reel${fr.claude ? ' · Claude' : ''}</a><a href="#" data-view="live" ${m === 'live' ? 'aria-current="true"' : ''}>Live edit</a></div>`;
  seg.onclick = e => { const a = e.target.closest('a[data-view]'); if (!a) return; e.preventDefault(); VIEW = a.dataset.view; setSource(); renderViewSeg(); };
}
function setSource() {
  const vid = $('#vid');
  if (!vid) return;
  const fin = viewMode() === 'final' && finalRender();
  ['ov', 'txtedit'].forEach(id => { const el = $('#' + id); if (el) el.style.display = fin ? 'none' : ''; });
  const note = $('#frame')?.parentElement?.querySelector('.note');
  if (note) note.textContent = fin ? `You are watching the finished reel, exactly as it was exported (${fin.claude ? 'Claude edit' : fin.quick ? 'quick export' : 'export'}, ${fmt(fin.duration || 0)}). “Live edit” shows the engine's draft you change step by step.`
    : 'The clip skips what you cut, live. Captions, the hook and images show roughly where they will sit in the final reel.';
  if (fin) {
    const url = `/files/${P.id}/${fin.file}`;
    if (!vid.src.endsWith(encodeURI(url)) && !vid.src.endsWith(url)) { vid.src = url; vid.onloadedmetadata = () => { vid.currentTime = 0; }; }
    $('#noclip').hidden = true;
    return;
  }
  if (P.source) {
    const url = `/files/${P.id}/${P.source.proxy}`;
    if (!vid.src.endsWith(url)) { vid.src = url; vid.onloadedmetadata = () => { vid.currentTime = (keepRanges()[0]?.[0] || 0) + 0.05; }; }
    $('#noclip').hidden = true;
    $('#thumbs').innerHTML = P.source.thumbs.map((t, k) => `<img src="/files/${P.id}/${t}" data-t="${k}" alt="">`).join('');
    $('#thumbs').onclick = e => { const t = e.target.dataset.t; if (t != null) vid.currentTime = +t; };
  }
}

/* the live preview: skips cuts, draws captions, hook title, images and effect tags */
let lastNow = -1;
function tick() {
  requestAnimationFrame(tick);
  const vid = $('#vid');
  if (!vid || !P || !P.source) return;
  if (viewMode() === 'final' && finalRender()) {   // the finished reel: plain playback, no cut skipping, no overlays
    const t = vid.currentTime, d = vid.duration || finalRender().duration || 0;
    $('#clock').textContent = `final ${fmt(t)} / ${fmt(d)}`;
    if (d) { const k = Math.min(1, t / d) * 100; $('#scrubfill').style.width = k + '%'; $('#scrubdot').style.left = k + '%'; }
    return;
  }
  const ranges = keepRanges(), t = vid.currentTime;
  if (!vid.paused && !playOriginal && ranges.length) {
    const inside = ranges.find(([a, b]) => t >= a && t < b);
    if (!inside) {
      const next = ranges.find(([a]) => a > t);
      if (next) vid.currentTime = next[0]; else { vid.pause(); vid.currentTime = ranges[0][0]; }
      return;
    }
  }
  const out = mapTime(t, ranges);
  $('#clock').textContent = `cut ${fmt(out ?? 0)} / ${fmt(outLen(ranges))}`;
  syncHead();
  if (vid.duration) { const k = Math.min(1, t / vid.duration) * 100; $('#scrubfill').style.width = k + '%'; $('#scrubdot').style.left = k + '%'; }
  drawOverlay(t, out, ranges);
}
function capStyle(tx) {
  const pal = { color: tx.color, hi: tx.highlight, ol: tx.outline, box: tx.box_color || '#000' };
  const f = lib('looks').fonts?.find(x => x.family === tx.font) || {};
  let css = `font-family:'${tx.font}';font-weight:${f.weight || 700};font-style:${f.style || 'normal'};color:${pal.color};`;
  const ow = tx.outline_w ?? 6;
  if (tx.glow) css += `text-shadow:0 0 .07em ${tx.glow}8c,0 0 .16em ${tx.glow}4d,0 .04em .18em rgb(0 0 0 / .3);`;
  else if (tx.box === 'none' || !tx.box) css += (ow > 0 ? `-webkit-text-stroke:${(.09 * ow / 6).toFixed(3)}em ${pal.ol};paint-order:stroke fill;` : '') + `text-shadow:0 .06em .2em rgb(0 0 0 / ${tx.shadow || ow > 0 ? .35 : .2});`;
  return { css, pal, box: tx.box || 'none' };
}
function spanBox(box, pal) {
  if (box === 'box') return `background:${pal.box};`;
  if (box === 'plate') return 'background:rgb(0 0 0 / .55);';
  if (box === 'glass') return 'background:rgb(255 255 255 / .18);backdrop-filter:blur(6px);';
  if (box === 'sticker') return 'background:#fff;color:#111;';
  return '';
}
/* where captions and the title sit: a dragged place (x, y = centre, w = width, fractions of the frame) or the preset */
const PRESET_Y = { upper: .22, middle: .48, lower: .74 };
function placeOf(kind) {
  const tx = V().text;
  if (kind === 'cap') return tx.cap_pos || { x: .5, y: PRESET_Y[tx.position || 'lower'] ?? .74, w: .86 };
  return tx.title_pos || { x: .5, y: .15, w: .84 };
}
const sizeOf = kind => { const tx = V().text; return kind === 'cap' ? (+tx.size || 78) : (+tx.title_size || Math.round((+tx.size || 78) * 1.15)); };
const placeCss = (kind, scale = 1) => { const p = placeOf(kind);
  return `left:${p.x * 100}%;top:${p.y * 100}%;width:${p.w * 100}%;right:auto;bottom:auto;transform:translate(-50%,-50%);font-size:${sizeOf(kind) / 1080 * 100 * scale}cqw;`; };
function drawTextBoxes() {
  if (P && viewMode() === 'final' && finalRender()) { const L = $('#txtedit'); if (L) L.innerHTML = ''; return; }
  const L = $('#txtedit'); if (!L || !P) return;
  const v = V(), fw = $('#frame').clientWidth;
  const kinds = [...(v.captions !== false ? ['cap'] : []), ...(v.hook.text ? ['title'] : [])];
  L.innerHTML = kinds.map(k => {
    const p = placeOf(k), px = sizeOf(k) / 1080 * fw, h = px * 1.3 * (k === 'cap' ? 1.25 : 2.1) / $('#frame').clientHeight;
    const custom = k === 'cap' ? v.text.cap_pos : v.text.title_pos;
    return `<div class="tbox ${custom ? 'custom' : ''}" data-kind="${k}" title="Drag to move · corner to resize · double-click to put it back"
      style="left:${(p.x - p.w / 2) * 100}%;top:${(p.y - h / 2) * 100}%;width:${p.w * 100}%;height:${h * 100}%">
      <span class="tlabel">${k === 'cap' ? 'Captions' : 'Title'} · ${sizeOf(k)}</span><i class="thandle" data-kind="${k}"></i></div>`;
  }).join('');
}
function bindTextEdit() {
  const L = $('#txtedit'); let drag = null;
  const key = k => k === 'cap' ? 'cap_pos' : 'title_pos';
  L.addEventListener('pointerdown', e => {
    const box = e.target.closest('.tbox'); if (!box) return;
    e.preventDefault(); const vid = $('#vid'); if (vid && !vid.paused) vid.pause();
    const k = box.dataset.kind, r = $('#frame').getBoundingClientRect(), p = { ...placeOf(k) };
    drag = { k, r, p0: p, sx: e.clientX, sy: e.clientY, resize: e.target.classList.contains('thandle'), size0: sizeOf(k),
      d0: Math.hypot(e.clientX - (r.left + p.x * r.width), e.clientY - (r.top + p.y * r.height)) || 1 };
    L.setPointerCapture(e.pointerId);
  });
  L.addEventListener('pointermove', e => {
    if (!drag) return;
    const { k, r, p0 } = drag, tx = V().text;
    if (drag.resize) {
      // pull the corner away from the centre = bigger, towards it = smaller (size and width together)
      const f = Math.hypot(e.clientX - (r.left + p0.x * r.width), e.clientY - (r.top + p0.y * r.height)) / drag.d0;
      const size = Math.round(Math.min(220, Math.max(28, drag.size0 * f)));
      if (k === 'cap') tx.size = size; else tx.title_size = size;
      tx[key(k)] = { ...p0, w: Math.min(1, Math.max(.2, p0.w * f)) };
    } else {
      const x = Math.min(1 - p0.w / 2 + .05, Math.max(p0.w / 2 - .05, p0.x + (e.clientX - drag.sx) / r.width));
      const y = Math.min(.95, Math.max(.05, p0.y + (e.clientY - drag.sy) / r.height));
      tx[key(k)] = { ...p0, x: +x.toFixed(4), y: +y.toFixed(4) };
    }
    drawTextBoxes();
  });
  const end = () => { if (!drag) return; drag = null; touch('text'); if (STEP === 'text') renderPanel(); };
  L.addEventListener('pointerup', end); L.addEventListener('pointercancel', end);
  L.addEventListener('dblclick', e => {
    const box = e.target.closest('.tbox'); if (!box) return;
    const tx = V().text; delete tx[key(box.dataset.kind)]; if (box.dataset.kind === 'title') delete tx.title_size;
    touch('text'); drawTextBoxes(); if (STEP === 'text') renderPanel(); toast('Back to the style\'s place');
  });
}
function drawOverlay(t, out, ranges) {
  const ov = $('#ov'); if (!ov) return;
  const v = V(), tx = v.text;
  const gcss = lib('looks').grades?.find(g => g.id === v.grade)?.css || 'none';
  const vid = $('#vid'); if (vid && vid.style.filter !== gcss) vid.style.filter = gcss === 'none' ? '' : gcss;
  let html = '<div class="safe"></div>';
  // the word being said now, for the word strips
  let nowWord = null;
  if (P.edl) {
    for (const w of P.edl.words) { if (t >= w.start && t <= w.end + 0.05) { nowWord = w; break; } }
    if ((nowWord?.i ?? -1) !== lastNow) {
      document.querySelectorAll('.w.now').forEach(x => x.classList.remove('now'));
      if (nowWord) document.querySelectorAll(`.w[data-i="${nowWord.i}"]`).forEach(x => x.classList.add('now'));
      lastNow = nowWord?.i ?? -1;
    }
  }
  if (out != null && P.edl) {
    if (v.hook.text && out < (v.hook.duration || 2.6)) {
      const st = capStyle({ ...tx, font: tx.title_font || tx.font, color: tx.title_color || tx.color });
      html += `<div class="title" style="${st.css};${placeCss('title')}"><span style="${spanBox(st.box, st.pal)}">${esc(v.hook.text)}</span></div>`;
    }
    if (v.captions !== false && nowWord && !nowWord.cut) {
      const kept = P.edl.words.filter(w => !w.cut), per = +tx.words_per_line || 3;
      const k = kept.findIndex(w => w.i === nowWord.i), g = kept.slice(k - (k % per), k - (k % per) + per);
      const st = capStyle(tx);
      const cs = x => tx.case === 'upper' ? x.toUpperCase() : tx.case === 'lower' ? x.toLowerCase() : x;
      const an = tx.anim || 'pop', gg = an === 'punch' ? [nowWord] : g, ki = gg.findIndex(w => w.i === nowWord.i);
      const key = an === 'slam' ? gg.reduce((b, w, i) => w.text.length > gg[b].text.length ? i : b, 0) : -1;
      const wcss = (w, i) => {
        const on = w.i === nowWord.i;
        if ((an === 'reveal' || an === 'blurin') && i > ki) return 'visibility:hidden;';
        if (an === 'slam' && i === key) return `background:${st.pal.hi};color:${tx.box_text || '#111'};-webkit-text-stroke:0;`;
        if (an === 'karaoke') return i <= ki ? `color:${st.pal.hi};` : '';
        if (!on) return an === 'box' ? '-webkit-text-stroke:0;' : '';
        if (an === 'box') return `background:${st.pal.hi};color:${tx.box_text || '#111'};-webkit-text-stroke:0;`;
        if (an === 'glow') return `color:${st.pal.hi};text-shadow:0 0 .35em ${st.pal.hi},0 0 .7em ${st.pal.hi};`;
        if (an === 'bounce' || an === 'punch') return `color:${st.pal.hi};display:inline-block;transform:scale(1.14);`;
        if (an === 'still' || an === 'rise' || an === 'reveal' || an === 'slam') return `color:${st.pal.hi};`;
        return `color:${st.pal.hi};`;
      };
      if (an === 'lexicon') {
        // Cinema Lexicon: 1–3 small words, the key word alone and big (≤ 5 letters in caps, longer in italic)
        const keys = new Set(tx.keys || []), kw = keys.has(nowWord.i);
        const lg = kw ? [nowWord] : kept.slice(Math.max(0, k - 2), k + 1).filter((w, i, a) => !keys.has(w.i) && a.slice(i + 1).every(x => !keys.has(x.i))).slice(-3);
        const core = nowWord.text.replace(/[^\w']/g, '');
        const word = kw ? (core.length <= 5 ? nowWord.text.toUpperCase() : cs(nowWord.text)) : lg.map(w => cs(w.text)).join(' ');
        html += `<div class="cap" style="${st.css};${placeCss('cap', kw ? 2.8 : 1)}"><span style="${kw && core.length > 5 ? 'font-style:italic;' : ''}">${esc(word)}</span></div>`;
      } else {
      const big = an === 'punch' ? 1.5 : 1;
      html += `<div class="cap" style="${st.css};${placeCss('cap', big)}">${gg.map((w, i) =>
        `<span class="${w.i === nowWord.i && an === 'pop' ? 'hi' : ''}" style="${spanBox(st.box, st.pal)}${wcss(w, i)}">${esc(cs(w.text))}</span>`).join(' ')}</div>`;
      }
    }
    for (const o of v.overlays) {
      if (o.status === 'removed') continue;
      const a = mapTime(o.at, ranges);
      if (a == null || out < a || out >= a + (o.hold || 1.6)) continue;
      if (o.kind === 'clip') {   // Cinema Lexicon example clip: full frame (the export plays the clip itself)
        html += o.image ? `<div class="exclip" style="position:absolute;inset:0;background:#000"><video src="${imgUrl(o.image)}#t=${(+o.media_start || 0) + (out - a)}" muted playsinline style="width:100%;height:100%;object-fit:cover"></video></div>`
          : `<div class="exclip" style="position:absolute;inset:0;background:#1d1a1a;color:#fff;display:flex;align-items:center;justify-content:center;text-align:center;padding:12%;font:600 14px/1.4 sans-serif">example clip still to find<br>“${esc(o.phrase || '')}”</div>`;
        continue;
      }
      // placed where the export puts it (x / y / scale / tilt); a cut-out has no white card
      const px = { left: 'left:6%', right: 'right:6%', center: 'left:50%;translate:-50% 0' }[o.x || 'right'] || 'right:6%';
      const py = { top: 'top:10%', upper: 'top:20%', middle: 'top:50%;translate:0 -50%' }[o.y || 'upper'] || 'top:20%';
      const gif = /\.gif$/i.test(o.image || ''), sc = (+o.scale || 0.42) * 100;
      // the export's size: as wide as scale allows, but never taller than max_h (both from the frame size)
      const wcq = o.max_h && o.ow && o.oh ? Math.min(sc, o.max_h * 177.8 * o.ow / o.oh) : sc;
      html += `<div class="pop${o.cutout || gif ? ' cut' : ''}" style="${px};${py};width:${wcq.toFixed(1)}cqw;rotate:${+o.tilt || -3}deg"><img src="${imgUrl(o.image)}" alt=""></div>`;
    }
    const fx = v.effects.find(e => { if (e.status === 'removed') return false; const a = mapTime(e.at, ranges); return a != null && out >= a && out < a + 3; });
    if (fx) html += `<span class="fxtag">${esc(effectById(fx.effect)?.name || fx.effect)} · “${esc(fx.word)}”</span>`;
  }
  if (ov.innerHTML !== html) ov.innerHTML = html;
}
const imgUrl = p => { const n = String(p).split('/').pop(); return `/files/${P.id}/images/${encodeURIComponent(n)}`; };

/* ------------------------------------------------------------ head: title, versions, step bar, dock */
function renderHead() {
  if (!P) return;
  renderViewSeg(); setSource();
  requestAnimationFrame(drawTextBoxes);
  const v = V(), st = styleById(v.style_id), s = stats();
  const onScreen = v.effects.filter(e => e.status !== 'removed').length + v.overlays.filter(o => o.status !== 'removed').length + (v.hook.text ? 1 : 0);
  const sounds = v.sfx.filter(x => x.status !== 'removed').length;
  $('#head').innerHTML = `
    <a class="crumb" href="#/">← All videos</a>
    <p class="eyebrow">Vetto video engine · Studio${P.account ? ' · ' + esc(P.account) : ''}</p>
    <h1>${esc(P.name)}</h1>
    <p class="status">${P.source ? `The reel is now <b>${fmt(s.out)}</b>, ${onScreen} element${onScreen === 1 ? '' : 's'} on screen, ${sounds} sound${sounds === 1 ? '' : 's'}.` : 'No footage yet.'}
      ${esc(v.name)}${st && !v.name.includes(st.name) ? ' · ' + esc(st.name) : ''}${P.plan_unit ? ' · ' + esc(P.plan_unit.label) : ''}</p>
    <nav class="tabs">${STEPS.map(x => {
      const state = stepState(x.id);
      return `<button type="button" class="${x.id === STEP ? 'on' : ''} ${state === 'approved' ? 'ok' : state === 'changed' ? 'changed' : ''}" data-step="${x.id}" title="${esc(state)}">${esc(x.name)}</button>`;
    }).join('')}</nav>`;
  $('#head').querySelectorAll('.tabs button').forEach(b => b.onclick = () => go(b.dataset.step));
  $('#versions').innerHTML = `<p class="meta" style="margin-bottom:6px">Versions of this video (same cut, its own style)</p><div class="seg">${P.versions.map(x => `<a href="#" data-v="${x.id}" ${x.id === P.current ? 'aria-current="true"' : ''}>${esc(x.name)}</a>`).join('')}<a href="#" data-v="+">+ Version</a></div>`;
  $('#versions').onclick = e => {
    const a = e.target.closest('a[data-v]'); if (!a) return; e.preventDefault();
    if (a.dataset.v === '+') return newVersion();
    P.current = a.dataset.v; save(); renderHead(); renderPanel();
  };
  const i = STEPS.findIndex(x => x.id === STEP), state = stepState(STEP);
  const open = STEPS.filter(x => stepState(x.id) !== 'approved').length;
  const dock = $('#dock'); dock.hidden = false;
  let label = state === 'approved' ? 'Approved · next' : 'Approve this step';
  if (STEP === 'storyboard') label = 'Approve the storyboard';
  if (STEP === 'export') label = 'Export the reel';
  const enabled = STEP === 'export' ? stepState('storyboard') === 'approved' && !!P.edl : canApprove();
  const sty = styleById(v.style_id);
  dock.innerHTML = CJOB ? `<span class="what claude-run"><b>Claude is editing it in ${esc(styleById(CJOB.style)?.name || CJOB.style)}</b> · ${esc(Math.round((Date.now() - CJOB.t0) / 60000))} min<br><span class="meta">${esc(CJOB.progress || 'reading the style guide…')}</span></span>
    <button class="big ghost" id="cstop">Stop</button>`
  : `<span class="what"><b>${esc(STEPS[i].name)}:</b> ${esc(dockLine())}<br>${open} step${open === 1 ? '' : 's'} not approved yet (they stay as the engine proposed)</span>
    ${sty && P.edl ? `<button class="big ghost" id="editnow" title="Claude edits the whole video in ${esc(sty.name)}, like in a chat: about 15–40 min">Edit now</button>` : ''}
    <button class="big" id="approve" ${enabled ? '' : 'disabled'}>${esc(label)}</button>`;
  if ($('#editnow')) $('#editnow').onclick = () => editNow();
  if ($('#cstop')) $('#cstop').onclick = async () => { if (confirm('Stop Claude? Its work so far stays in the Editing Beast projects folder.')) await fetch(`/api/projects/${P.id}/claude-stop`, { method: 'POST' }); };
  if (CJOB) return;
  $('#approve').onclick = () => {
    if (STEP === 'export') return $('#panel [data-act="render"]:not([data-preview])')?.click();
    stepState(STEP) === 'approved' ? go(STEPS[Math.min(i + 1, STEPS.length - 1)].id) : approve(STEP);
  };
}
/* Edit now (18 Nov 2026): Claude edits the whole video in the picked style, the way it does in a chat (engine/claude_edit.py) */
async function editNow() {
  const v = V(), st = styleById(v.style_id);
  if (!confirm(`Claude edits the whole video in ${st.name}, like in a chat: captions, text effects, transitions, B-roll, sounds and music, adapted to what you say.\n\nIt takes about 15–40 minutes and uses your Claude usage. You can keep working; the finished reel appears in Check & export.`)) return;
  clearTimeout(saveTimer); if (!(await putP())) return;
  const r = await fetch(`/api/projects/${P.id}/claude-edit`, { method: 'POST', body: JSON.stringify({ version: v.id, style: v.style_id }) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { alert(j.login ? 'One-time setup: ' + j.error + '\n\nA browser page opens to sign in. After that, press Edit now again.' : (j.error || 'Edit now did not start')); return; }
  watchClaude(j, v.style_id);
}
async function watchClaude(j, style) {
  CJOB = { id: j.id, style, t0: Date.parse(j.started) || Date.now(), progress: j.progress };
  renderHead();
  for (;;) {
    await new Promise(r => setTimeout(r, 3000));
    const s = await api(`/api/jobs/${j.id}`).catch(() => null);
    if (!s || !CJOB) return;
    CJOB.progress = s.progress || s.progress_tool;
    if (s.status === 'running') { if (P) renderHead(); continue; }
    CJOB = null;
    if (!P) return;
    if (s.status === 'done') { P = await api(`/api/projects/${P.id}`); LAST = JSON.stringify(P); VIEW = 'final'; toast('Claude finished the edit'); go('export'); renderHead(); renderPanel(); }
    else { renderHead(); alert('Edit now stopped:\n' + String(s.error || '').split('\n')[0]); }
    return;
  }
}
function canApprove() {
  if (STEP === 'footage') return !!P.source;
  if (STEP === 'cut') return !!P.edl;
  if (STEP === 'style') return !!V().style_id;
  if (STEP === 'storyboard') return STEPS.slice(0, STEPS.findIndex(s => s.id === 'storyboard')).every(s => stepState(s.id) === 'approved');
  return true;
}
function dockLine() {
  const v = V(), s = stats();
  switch (STEP) {
    case 'footage': return P.source ? `${P.source.width}×${P.source.height}, ${fmt(P.source.duration)}${P.account ? ' · ' + P.account : ''}` : 'Add the raw take first';
    case 'brief': return P.brief.prompt ? P.brief.prompt.slice(0, 90) : 'Say what this video should become';
    case 'cut': return P.edl ? `${fmt(s.src)} → ${fmt(s.out)} · ${s.cut} words cut · ${s.short} of ${s.pauses} pauses shortened` : 'Transcribe first (Brief step)';
    case 'style': return styleById(v.style_id)?.name || 'Pick a style';
    case 'hook': return v.hook.text || 'no hook yet';
    case 'effects': return `${v.effects.filter(e => e.status !== 'removed').length} effects, ${v.overlays.filter(o => o.status !== 'removed').length} images on words`;
    case 'memes': { const n = v.overlays.filter(o => o.kind === 'meme' && o.status !== 'removed').length; return n ? `${n} meme${n > 1 ? 's' : ''} on phrases` : 'Reaction GIFs and memes on your phrases'; }
    case 'text': return `${v.text.font} · ${v.text.box} · ${v.text.position}`;
    case 'sound': return `${v.sfx.filter(x => x.status !== 'removed').length} sounds placed`;
    case 'outputs': return ['Reel', v.outputs.stories.length ? `${v.outputs.stories.length} stories` : null, v.outputs.carousel.slides.length ? `${v.outputs.carousel.slides.length}-slide carousel` : null].filter(Boolean).join(' · ');
    case 'storyboard': return canApprove() ? 'Everything before this is approved' : 'Approve steps 1 to 10 first';
    default: return stepState('storyboard') === 'approved' ? 'Storyboard approved: you can export' : 'Export opens after the storyboard is approved';
  }
}
function newVersion(styleId) {
  const base = V(), n = P.versions.length + 1, v = JSON.parse(JSON.stringify(base));
  v.id = 'v' + Math.random().toString(16).slice(2, 8); v.renders = [];
  v.name = `Version ${n}`;
  for (const s of STEPS) if (!['footage', 'brief', 'cut'].includes(s.id)) v.steps[s.id] = { status: 'open' };
  P.versions.push(v); P.current = v.id;
  if (styleId) applyStyle(styleId);
  save(); renderHead(); renderPanel(); toast(`${v.name}: same footage and cut, its own style`);
}

/* ------------------------------------------------------------ panels */
function overview(rows) { return `<dl class="overview">${rows.filter(Boolean).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl>`; }
function askBox(step) {
  const reqs = P.requests.filter(r => r.step === step).slice(-4);
  return `<div class="ask">
    <label>Want a change? Type it, Claude does it<textarea id="ask" rows="2" placeholder="e.g. cut the second take of the intro, put the pizza photo on “pizza”"></textarea></label>
    <div class="row2"><button class="small" data-act="ask">Send to Claude</button>
      <label class="button small quiet attach" title="A photo or video for Claude: a green-screen background, a green-screen clip, a logo…">📎 Attach a file<input type="file" id="ask-file" accept="image/*,video/*" multiple hidden></label>
      <span class="meta">Saved in the project. In Claude Code say “apply my video engine requests”.</span></div>
    ${PENDING.length ? `<div class="attached">${PENDING.map(n => `<span class="pill">📎 ${esc(n)}</span>`).join(' ')} <span class="meta" style="display:inline">goes with your next message${STEP === 'effects' ? ' · the Green-screen background uses the last file you attach' : ''}</span></div>` : ''}
    ${reqs.length ? `<div class="reqs">${reqs.map(r => `<div>${r.status === 'done' ? '✓' : '○'} ${esc(r.text)}${(r.files || []).length ? ` <span class="meta" style="display:inline">📎 ${r.files.map(f => esc(f.split('/').pop())).join(', ')}</span>` : ''} <span class="meta" style="display:inline">· ${esc(r.status)}</span></div>`).join('')}</div>` : ''}
  </div>`;
}
function cardHead(title, extra = '') {
  const st = stepState(STEP);
  return `<div class="row" style="justify-content:space-between"><h2 class="sec">${esc(title)} ${st === 'approved' ? '<span class="pill ok">Approved</span>' : st === 'changed' ? '<span class="pill warn">Changed after approval</span>' : '<span class="pill">Waiting for you</span>'}</h2>${extra}</div>`;
}
function renderPanel() {
  const f = { footage: pFootage, brief: pBrief, cut: pCut, style: pStyle, hook: pHook, effects: pEffects, memes: pMemes, text: pText, sound: pSound,
    outputs: pOutputs, storyboard: pStoryboard, export: pExport }[STEP];
  $('#panel').innerHTML = f() + (STEP !== 'export' ? askBox(STEP) : '');
  bindPanel(); sizePreviews();
  if (STEP === 'storyboard') bindTimeline();
}

function pFootage() {
  const s = P.source;
  return cardHead('Footage') + overview([
    ['Clip', s ? `${esc(s.file.split('/').pop())} · ${s.width}×${s.height} · ${fmt(s.duration)} · ${s.has_audio ? 'with sound' : 'no sound'}` : 'none yet'],
    ['Account', esc(P.account || 'not set')],
    ['Vetto plan', P.plan_unit ? esc(P.plan_unit.label) : 'not linked'],
    ['Images for words', `${IMAGES.length} in the bank`],
  ]) + `
  <label class="drop" id="drop"><input type="file" id="file" accept="video/*" hidden>
    <b style="color:var(--ink)">Drop your raw take here</b><span>or click to choose a video. It stays on this Mac.</span></label>
  <div class="inline" style="margin-top:var(--g2)">
    <label>Or a file path on this Mac<input id="path" placeholder="/Users/…/Desktop/take.mov"></label>
    <button class="small" data-act="import">Use this file</button>
  </div>
  <div class="inline" style="margin-top:var(--g1)">
    <label>Or pull one of your own reels (link)<input id="pull" placeholder="https://www.tiktok.com/@…/video/…"></label>
    <button class="small" data-act="pull">Pull</button>
  </div>
  <p class="meta">TikTok links work logged out; Instagram often refuses logged-out downloads, then save the video and drop the file.</p>
  ${P.source && P.source.width > P.source.height ? `<h3 class="section-title">Landscape take: where is the face?</h3>
  <p class="help">The reel is cut to 9:16 around this point. 0 = left edge, 100 = right edge.</p>
  <input type="range" min="0" max="100" value="${Math.round((P.focus_x ?? .5) * 100)}" data-focus>` : ''}
  <h3 class="section-title">Link to the content plan</h3>
  <div class="grid-form">
    <label>Account<select data-bind="p.account" data-step="footage"><option value="">Choose…</option>${ACCOUNTS.map(a => `<option ${P.account === a ? 'selected' : ''}>${esc(a)}</option>`).join('')}</select></label>
    <label>Batch unit<select id="unit"><option value="">${PLAN.units.length ? 'Choose…' : 'No Vetto plan synced yet'}</option>${PLAN.units.map((u, k) => `<option value="${k}" ${P.plan_unit?.label === u.label ? 'selected' : ''}>${esc(u.label)}</option>`).join('')}</select></label>
  </div>
  ${P.plan_unit ? overview(Object.entries(P.plan_unit).filter(([k]) => k !== 'label').map(([k, v]) => [k, esc(v)])) : `<p class="meta">When the plan is linked, the unit's format, hook and script steer every step. Sync: ask Claude “sync my Vetto batches into the video engine”.</p>`}
  <h3 class="section-title">Image bank <span class="count">${IMAGES.length}</span></h3>
  <p class="help">Add a photo, then type the word or phrase it belongs to and press <b>Put it there</b>: it shows when you say it. (Photos named after a word you say, like pizza.jpg, are also proposed on that word by themselves.)</p>
  <div class="imgbank">${IMAGES.map((im, k) => { const ov = V().overlays.find(o => o.status !== 'removed' && String(o.image).split('/').pop() === im.name);
    return `<div class="imgrow"><img src="${im.url}" alt="${esc(im.name)}" title="${esc(im.name)}">
      <div class="imgrow-main"><span class="meta">${esc(im.name)}${ov ? ` · on “${esc(ov.phrase || P.edl?.words[ov.word_i]?.text || '')}” at ${fmt(ov.at)}${ov.status === 'proposed' ? ' (proposed)' : ''}` : ' · not placed yet'}</span>
        <div class="inline"><input data-imgphrase="${k}" placeholder="${P.edl ? 'Which word or phrase? e.g. pizza, the app' : 'Transcribe first (Brief step)'}" value="${esc(ov?.phrase || '')}" ${P.edl ? '' : 'disabled'}>
          <button class="small" data-act="img-word" data-k="${k}" ${P.edl ? '' : 'disabled'}>Put it there</button>
          ${ov ? `<button class="small remove" data-act="img-unplace" data-k="${k}">Take off</button>` : ''}</div></div></div>`; }).join('')}
    <label class="button small" style="flex-direction:row;color:var(--ink);align-self:flex-start">Add photos<input type="file" id="imgs" accept="image/*" multiple hidden></label></div>`;
}

function pBrief() {
  const b = P.brief, seg = (key, opts) => `<div class="seg">${opts.map(o => `<a href="#" data-seg="${key}" data-val="${esc(o)}" ${b[key] === o ? 'aria-current="true"' : ''}>${esc(o)}</a>`).join('')}</div>`;
  const pc = pace();
  return cardHead('Brief') + overview([
    ['Outcome', esc(b.prompt || 'not written yet')],
    ['Polish · pace', `${esc(b.polish)} · ${esc(b.pace)} (pauses over ${pc.shorten_pauses_over} s get shortened to ${pc.beat_mid} s)`],
    ['Outputs', esc((b.outputs || []).join(', '))],
    ['Language', esc(b.language)],
    ['Transcript', P.transcript ? `${esc(P.transcript.language)} · ${P.edl.words.length} words` : 'not yet'],
  ]) + `
  <label>What should the outcome be?<textarea rows="4" data-bind="p.brief.prompt" data-step="brief" placeholder="e.g. A 30 s reel for Frank: hook in the first second, cut every dead moment, photos of the food on the words that name them, then a carousel and today's stories from it.">${esc(b.prompt)}</textarea></label>
  <div style="margin-top:16px">
  <div class="qcard"><h4>How polished do you want it?</h4>${seg('polish', ['Full', 'Medium', 'Quick'])}</div>
  <div class="qcard"><h4>Which pace?</h4>${seg('pace', ['Calm', 'Medium', 'Very lively'])}</div>
  <div class="qcard"><h4>Which word goes at the end?</h4><input data-bind="p.brief.closing_word" data-step="brief" value="${esc(b.closing_word)}" placeholder="the comment keyword, e.g. FOOD, or leave empty"></div>
  <div class="qcard"><h4>What should come out?</h4><div class="row">${['reel', 'stories', 'carousel'].map(o => `<label class="check"><input type="checkbox" data-out="${o}" ${(b.outputs || []).includes(o) ? 'checked' : ''}> ${o[0].toUpperCase() + o.slice(1)}</label>`).join('')}</div></div>
  <div class="qcard"><h4>Which language is spoken?</h4>
  <select data-bind="p.brief.language" data-step="brief">${[['auto', 'Detect'], ['en', 'English'], ['ro', 'Romanian'], ['nl', 'Dutch'], ['ru', 'Russian']].map(([k, n]) => `<option value="${k}" ${b.language === k ? 'selected' : ''}>${n}</option>`).join('')}</select></div>
  </div>
  <div class="row" style="margin-top:var(--g3)"><button data-act="analyze" ${P.source ? '' : 'disabled'}>${P.edl ? 'Transcribe again' : 'Transcribe and propose the cut'}</button>
    <span class="meta">${P.edl ? 'Transcribing again replaces the cut you made.' : 'Whisper large-v3 on this Mac, every word timed.'}</span></div>`;
}

function pCut() {
  if (!P.edl) return cardHead('Cut') + `<div class="empty">No transcript yet. Go to the Brief step and press “Transcribe and propose the cut”.</div>`;
  const s = stats(), byAfter = new Map(P.edl.pauses.map(p => [p.after_word, p]));
  const lead = P.edl.pauses.find(p => p.after_word == null);
  const pz = p => `<button class="pz ${p.keep ? 'keep' : ''} ${p.hint && !p.keep ? 'hint' : ''}" data-act="pause" data-id="${p.id}" title="${esc(p.hint || (p.keep ? 'kept as is' : 'shortened'))}">|| ${p.dur.toFixed(2)} s ${p.keep ? 'kept' : 'shortened'}</button>`;
  return cardHead('Cut', `<div class="row"><button class="small quiet" data-act="restore-all">Restore every word</button></div>`) + `
  <p class="statline">reel <b>${fmt(s.out)}</b> from ${fmt(s.src)} · <b>${s.cut}</b> words cut · <b>${s.short}</b> of ${s.pauses} pauses shortened · ${s.wpm} words/min</p>
  <p class="help"><b>Every word in the clip.</b> Click a word to cut it or put it back; hold Shift to cut from the last word you clicked up to here. Long pauses are shortened (dotted label); click one to keep it. A pause after a question or before something important is worth keeping.<br>
  <span lang="ro">Fiecare cuvânt din clip. Apasă pe un cuvânt ca să-l tai sau să-l pui înapoi; ține apăsat Shift ca să tai de la ultimul cuvânt apăsat până aici. Pauzele lungi sunt scurtate (eticheta punctată); apasă pe una ca s-o păstrezi.</span></p>
  <div class="row" style="margin:4px 0 14px"><span class="meta" style="display:inline">Click a word to:</span>
    <div class="seg" style="margin:0"><a href="#" data-cutmode="cut" ${cutMode === 'cut' ? 'aria-current="true"' : ''}>✂ Cut it</a><a href="#" data-cutmode="edit" ${cutMode === 'edit' ? 'aria-current="true"' : ''}>✎ Change its text</a></div>
    <span class="meta" style="display:inline">${cutMode === 'edit' ? 'Type the right word, Enter to save, Esc to cancel. Captions and exports use your text; the timing stays.' : '⌥-click a word to change its text without switching.'}</span></div>
  ${P.edl.retakes.length ? `<p class="meta">${P.edl.retakes.length} retake${P.edl.retakes.length > 1 ? 's' : ''} found: the earlier attempt is cut, the last one kept. Red words show why on hover.</p>` : ''}
  <div class="script">${lead ? `<div class="line"><time></time><div class="words">${pz(lead)}</div></div>` : ''}${sentences().map(ws => `
    <div class="line"><time data-t="${ws[0].start}">${fmt(ws[0].start)}</time><div class="words">${ws.map(w =>
      `<button class="w ${w.cut ? 'cut' : ''} ${w.p < 0.5 && !w.orig ? 'low' : ''} ${w.orig != null ? 'edited' : ''} ${cutMode === 'edit' ? 'editable' : ''}" data-act="word" data-i="${w.i}" title="${esc(w.orig != null ? `you changed it; Whisper heard “${w.orig}”` : w.why || (w.p < 0.5 ? 'Whisper is unsure of this word: click ✎ to fix it' : fmt(w.start)))}">${esc(w.text)}</button>${byAfter.get(w.i) ? pz(byAfter.get(w.i)) : ''}`).join('')}</div></div>`).join('')}
  </div>`;
}

function stageFor(st) {
  // the style on a person: its title, its caption with the spoken word highlighted, and a step card
  const pal = st.palette || {}, bg = pal.bg || pal.bg2 || '#3b2b2d', acc = pal.accent || pal.text || '#fff', txt = pal.text || '#fff';
  const ff = x => STYLE_FONT[x] || (fontByName(x) ? x : null);
  const tf = ff(st.fonts?.title) || ff(st.fonts?.caption) || 'TikTok Sans', cf = ff(st.fonts?.caption) || tf;
  const tStyle = (fontByName(tf)?.style) || (/Serif|Bodoni/.test(tf) ? 'italic' : 'normal');
  const gradeCss = lib('looks').grades?.find(g => g.id === st.grade)?.css || 'none';
  const caseT = x => st.caption?.case === 'upper' ? x.toUpperCase() : st.caption?.case === 'lower' ? x.toLowerCase() : x;
  const box = /glass/.test(st.caption?.box || '') ? 'background:rgba(255,255,255,.18);' : /plate/.test(st.caption?.box || '') ? 'background:rgba(0,0,0,.55);' : '';
  return `<div class="stage" style="background:radial-gradient(ellipse at 50% 40%, ${acc}44, transparent 65%), ${bg}">
    <div style="position:absolute;inset:0;filter:${gradeCss}"><div class="face"></div><div class="body"></div></div>
    <div class="s-title" style="font-family:'${tf}';font-style:${tStyle};color:${txt}">${caseT('How I plan my week')}</div>
    <div class="s-cap" style="font-family:'${cf}';color:${txt}"><span style="${box}padding:0 .2em;border-radius:.2em">${caseT('this is the')} <span style="color:${acc}">${caseT('important part')}</span></span></div>
    <div class="s-step" style="background:${/glass/.test(st.textbox || '') ? 'rgba(255,255,255,.18)' : /dark/.test(st.textbox || '') ? 'rgba(0,0,0,.6)' : '#fff'};color:${/glass|dark/.test(st.textbox || '') ? '#fff' : '#1e1e1e'}"><small style="color:${acc}">Step 1</small>Write everything down</div>
  </div>`;
}
/* export straight away in the picked style, without approving the other steps (Alina, 18 Nov 2026) */
/* a style with a director (Clean White, Cinema Lexicon, Neon Dimension) makes the whole edit: effects, transitions,
   punch-ins, sounds and music on your words, as proposals (engine/director.py) */
const DIRECTED = ['clean-white', 'cinema-lexicon', 'neon-dimension'];
const AUTO_MEMES = ['meme-chaos'];   // these styles put memes and GIFs on the video by themselves (25 Nov 2026)
async function styleEdit(id) {
  if (!(DIRECTED.includes(id) || AUTO_MEMES.includes(id)) || !P.edl) return;
  clearTimeout(saveTimer); if (!(await putP())) return;
  toast('Making the style edit…');
  const r = await fetch(`/api/projects/${P.id}/style-edit`, { method: 'POST', body: JSON.stringify({ version: V().id, style: id }) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast(j.error || 'The style edit did not work'); return; }
  P = j.project; LAST = JSON.stringify(P); renderPanel(); renderHead();
  if (j.summary) toast(`${styleById(id)?.name}: ${j.summary.effects} effects and transitions, ${j.summary.sounds} sounds, ${j.summary.punches} punch-ins, music` +
    (j.summary.clips ? `, ${j.summary.clips} example clips` : ''));
  if (j.prep_job) await lexiconPrep(Promise.resolve(j.prep_job));
  if (j.meme_job) {
    const r = await runJob(Promise.resolve(j.meme_job), 'Putting memes and GIFs on your phrases');
    MEMES = null; renderPanel(); renderHead();
    if (r) toast(r.placed.length ? `${r.placed.length} memes on your video (${r.placed.map(x => fmt(x.at)).join(', ')}) · swap or remove them in Memes` : 'No phrase needed a meme');
  }
}
// Cinema Lexicon (18 Nov 2026): after the edit the engine makes the brand kit (only from a link or attached kit) and finds
// the example clips on Pexels by itself
async function lexiconPrep(promise) {
  const r = await runJob(promise, 'Brand kit and example clips');
  renderPanel(); renderHead();
  if (!r) return;
  const parts = [];
  if (r.brand) parts.push(`brand kit: ${r.brand}`);
  if (r.clips_filled) parts.push(`${r.clips_filled} example clips found on ${r.clips_source || 'Mixkit'}`);
  if (r.clips_missing) parts.push(`${r.clips_missing} clips not found: Claude will look for them`);
  if (parts.length) toast(parts.join(' · '));
}
function styleEditBox(sel) {
  if (!DIRECTED.includes(sel.id)) return '';
  const v = V(), se = v.style_edit, mine = v.effects.filter(e => String(e.by || '').startsWith('style:') && e.status !== 'removed');
  const music = lib('music').find(m => m.id === v.music?.id);
  return `<div class="style-edit"><b>The ${esc(sel.name)} edit ${se?.style === sel.id ? '' : '(not made yet)'}</b>
    ${se?.style === sel.id ? `<p class="meta">On your words, as in the Editing Beast guide: ${mine.map(e => effectById(e.effect)?.name).filter((x, i, a) => a.indexOf(x) === i).map(n => `${mine.filter(e => effectById(e.effect)?.name === n).length}× ${esc(n)}`).join(' · ')} · ${v.sfx.filter(s => String(s.by || '').startsWith('style:') && s.status !== 'removed').length} sounds · ${(v.punches || []).length} punch-ins · music: ${esc(music?.name || 'none')}${v.music?.status === 'removed' ? ' (off)' : ''}.
      ${se.clips ? `${se.clips} example clips on phrases${se.clips_missing ? ` (<b>${se.clips_missing} still to find</b>: say “apply my video engine requests” in Claude Code)` : ''}. ` : ''}${se.brand ? `Brand kit: <b>${esc(se.brand)}</b>. ` : se.style === 'cinema-lexicon' ? 'No brand kit yet (ask Claude for one from the store link): the cards use cream and magenta, no app buttons. ' : ''}
      Everything is marked “proposed”: keep, change or remove each one in Effects and Sound.</p>
      <p class="meta">The look stays the style's. The sounds follow what you say (a swipe, a tap, money, a surprise…) and the music follows the mood${v.music?.why ? `: <b>${esc(music?.name || '')}</b>, picked from ${esc(v.music.why)}` : ''}.</p>
      ${music?.credit ? `<p class="meta">Music licence ${esc(music.licence)}: ${esc(music.note || '')} Credit: ${esc(music.credit)}</p>` : ''}` : '<p class="meta">Places the effects, transitions, punch-ins, sounds and music of this style on your words.</p>'}
    <div class="inline" style="margin-top:8px"><label>Music vibe (optional)<input id="vibe" value="${esc(v.music_vibe || '')}" placeholder="e.g. upbeat funky, dark cinematic, chill hip-hop"></label>
      <button class="small" data-act="vibe">Use this vibe</button></div>
    ${sel.id === 'cinema-lexicon' ? lexiconBox(se) : ''}
    <div class="row"><button class="small" data-act="style-edit">${se?.style === sel.id ? 'Make the style edit again' : 'Make the style edit'}</button>
    ${v.music?.id ? `<button class="small" data-act="music-toggle">${v.music.status === 'removed' ? 'Music back on' : 'No music'}</button>` : ''}</div></div>`;
}
function lexiconBox(se) {
  const v = V(), clips = v.overlays.filter(o => o.kind === 'clip' && o.status !== 'removed'), found = clips.filter(o => o.image).length;
  return `<div class="lexicon" style="margin-top:10px;display:grid;gap:8px">
    <div class="inline"><label>Product link (only for an ad: App Store, Google Play or the website; or attach a brand kit in the chat bar)
      <input id="brandurl" value="${esc(P.brand_url || '')}" placeholder="https://apps.apple.com/…"></label>
      <button class="small" data-act="brand-kit">Make the brand kit</button></div>
    <p class="meta">${se?.brand ? `Brand kit: <b>${esc(se.brand)}</b> (colours, icon, screens from the link or your files).` : 'No brand kit: the cards are cream and magenta, no app buttons.'}</p>
    <p class="meta">Example clips: ${clips.length ? `${found} of ${clips.length} found${found < clips.length ? '' : ' ✓'}` : 'none in this edit'}.
      The engine finds them by itself when you pick the style, on ${SETTINGS.pexels ? 'Pexels' : 'Mixkit (free, no watermark)'}; swap any of them in Effects or ask Claude for a better one.</p>
    ${found < clips.length ? '<div class="row"><button class="small" data-act="find-clips">Find the missing clips</button></div>' : ''}
  </div>`;
}
function quickExportBox(sel) {
  const v = V(), can = !!(P.edl && P.source);
  if (isBeast(sel)) return `<div class="quick-export"><div><b>Export in ${esc(sel.name)} now</b>
    <p class="meta">Claude edits your video exactly like the approved ${esc(sel.name)} example in Editing Beast: same fonts, caption system, effects, transitions, sounds and music, adapted to what you say. About 15–40 min; the reel appears in Check &amp; export. (The previews in the steps are a rough draft; this is the real edit.)</p></div>
    <button class="primary" data-act="edit-now" ${can ? '' : 'disabled'}>Export now</button>
    ${can ? '' : '<p class="meta" style="grid-column:1/-1">Add footage and transcribe first (Footage and Brief steps).</p>'}</div>`;
  const last = v.renders.filter(r => r.quick).slice(-1)[0];
  return `<div class="quick-export"><div><b>Export in ${esc(sel.name)} now</b>
    <p class="meta">Your cut, in this style, full size. No need to approve the other steps first. Anything you already set (hook, effects, sounds) goes in too.</p></div>
    <button class="primary" data-act="quick-export" ${can ? '' : 'disabled'}>Export now</button>
    ${last ? `<p class="meta" style="grid-column:1/-1">Last quick export: ${esc(last.at.replace('T', ' '))} · <a href="#/p/${P.id}/export">see it in Check &amp; export</a></p>` : ''}
    ${can ? '' : '<p class="meta" style="grid-column:1/-1">Add footage and transcribe first (Footage and Brief steps).</p>'}</div>`;
}
function pStyle() {
  const v = V(), sel = styleById(v.style_id), learned = lib('styles').filter(s => /^learned/.test(s.source || ''));
  return cardHead('Style') + (sel ? overview([
    ['Style', `${esc(sel.name)} <span class="src">${esc(sel.source)}${sel.page ? ' p.' + sel.page : ''}</span>`],
    ['Look', esc(sel.look)],
    ['Colours', `<span class="swatches">${Object.values(sel.palette || {}).filter(c => c.startsWith('#')).map(c => `<i style="background:${c}"></i>`).join('')}</span>`],
    ['Type', `${esc(Object.values(sel.fonts || {}).join(' / '))} <span class="draft">${esc(sel.fonts_status || '')}</span>`],
    ['Captions', esc(`${sel.caption.mode}, ${sel.caption.position}, ${sel.caption.box}`)],
    ['Text box', esc(sel.textbox)],
    ['Pacing', esc(sel.pacing.value)],
    sel.anim || sel.text?.anim ? ['Caption motion', esc(lib('looks').caption_anims?.find(a => a.id === (sel.text?.anim))?.name || '')] : null,
    sel.grade ? ['Colour grade', esc(lib('looks').grades?.find(g => g.id === sel.grade)?.name || sel.grade)] : null,
    sel.effects_suggested ? ['Effects that fit', esc(sel.effects_suggested.map(id => effectById(id)?.name || id).join(', '))] : null,
    sel.status === 'draft' ? ['Status', '<span class="draft">draft by Claude, waiting for your approval</span>'] : null,
    ['Renders with', 'this engine: cut, captions and title in this style; its signature looks come from the effects you put on words'],
  ]) + styleEditBox(sel) + quickExportBox(sel) : '<p class="help">Pick a style name: the video is edited in that style. Each version of this video can have its own style.</p>') + `
  <div class="opts">${lib('styles').map(st => `<button class="opt" data-act="style" data-id="${st.id}" aria-pressed="${v.style_id === st.id}">
    ${P.source?.proxy ? `<div class="fxprev"><iframe loading="lazy" src="${styleExampleSrc(st)}" tabindex="-1" aria-label="Example of ${esc(st.name)}"></iframe></div>` : stageFor(st)}<div class="name">${esc(st.name)}</div><p style="text-align:center">${esc(st.source)}${st.page ? ' p.' + st.page : ''}</p></button>`).join('')}</div>
  ${sel ? `<div class="row" style="margin-top:var(--g2)"><button class="small" data-act="style-version">Also make a new version in another style</button></div>` : ''}
  <h3 class="section-title">Colour grade <span class="count">the footage itself · ${lib('looks').grades?.length || 0}</span></h3>
  <p class="help">Each grade is shown on the same frame of your take. The final reel gets the full grade on export.</p>
  <div class="opts">${(lib('looks').grades || []).map(g => `<button class="opt" data-act="grade" data-id="${g.id}" aria-pressed="${(v.grade || 'natural') === g.id}">
    <div class="stage" style="width:100%;aspect-ratio:9/12;background:#2a1a1c url('${P.source ? thumbAt(Math.min(P.source.duration - 1, 2)) : ''}') center/cover;filter:${g.css}">${P.source ? '' : '<div class="face"></div><div class="body"></div>'}</div><h4>${esc(g.name)}</h4></button>`).join('')}</div>
  <h3 class="section-title">Teach the engine a new style ${learned.length ? `<span class="count">${learned.length} learned</span>` : ''}</h3>
  <p class="help">Paste 3 to 5 example videos (links or files on this Mac). Claude studies them with StyleLab and saves one named style you can pick here.</p>
  <label>Example videos<textarea id="teach-links" rows="3" placeholder="one link or file path per line"></textarea></label>
  <label style="margin-top:var(--g1)">Style name<input id="teach-name" placeholder="e.g. Frank chaos"></label>
  <div class="row" style="margin-top:var(--g1)"><button class="small" data-act="teach">Study these videos and pull the fonts, colors, captions and pacing into one style</button></div>`;
}
/* what a style does to the text and the grade, without changing anything (used to apply it and for its live example) */
function styleLook(st) {
  const v = V(), pal = st.palette || {}, text = JSON.parse(JSON.stringify(v.text));
  if (st.text) return { text: Object.assign(text, st.text), grade: st.grade || v.grade || 'natural' };   // newer styles say exactly how the text looks
  const capFont = STYLE_FONT[st.fonts?.caption] || text.font, titleFont = STYLE_FONT[st.fonts?.title] || capFont;
  Object.assign(text, { font: capFont, title_font: titleFont, color: pal.text || '#FFFFFF', title_color: pal.text || '#FFFFFF',
    highlight: pal.accent || text.highlight, box: /glass/.test(st.caption.box) ? 'glass' : /plate/.test(st.caption.box) ? 'plate' : 'none',
    position: /chest|middle|under card|panel/.test(st.caption.position) ? 'middle' : /above/.test(st.caption.position) ? 'lower' : text.position,
    words_per_line: /one big word|panel word/.test(st.caption.mode) ? 1 : /3-line/.test(st.caption.mode) ? 4 : 3,
    case: st.caption.case === 'upper' ? 'upper' : st.caption.case === 'lower' ? 'lower' : 'as spoken' });
  return { text, grade: v.grade || 'natural' };
}
/* a style from the Editing Beast folder: its approved example is only reproduced by Claude (Edit now) */
const isBeast = st => !!st && /Editing Beast/.test((st.source || '') + (st.source_file || ''));
function applyStyle(id) {
  const st = styleById(id), v = V(); if (!st) return;
  if (v.style_id !== id) {
    // 24 Nov 2026 (Alina: the Star Glitch export still had Clean White pieces): what another style placed goes away
    const other = x => String(x.by || '').startsWith('style:') && x.by !== 'style:' + id;
    v.effects = v.effects.filter(x => !other(x));
    v.sfx = v.sfx.filter(x => !other(x));
    if (other(v.music || {})) delete v.music;
    if (v.style_edit && v.style_edit.style !== id) { delete v.style_edit; delete v.punches; delete v.punch_in; delete v.lufs; }
  }
  v.style_id = id;
  const lk = styleLook(st);
  v.text = lk.text;
  if (st.text && st.grade) v.grade = st.grade;
  if (!/Version \d+ ·/.test(v.name)) v.name = v.name.replace(/ · .*$/, '') + ' · ' + st.name;
  else v.name = v.name.replace(/ · .*$/, ' · ' + st.name);
}
/* a style card's live example: your frame, graded, with your words captioned in that style (engine/hf/preview/_style.html) */
function styleExampleSrc(st) {
  const lk = styleLook(st), tx = { ...lk.text };
  const ff = fontByName(tx.font), tf = fontByName(tx.title_font);
  Object.assign(tx, { font_weight: ff?.weight || 700, font_style: ff?.style || 'normal', title_weight: tf?.weight || 700, title_style: tf?.style || 'normal' });
  let ws = selWords();
  if (!ws.length) { const line = sentences().map(l => l.filter(w => !w.cut)).find(l => l.length) || []; ws = line; }
  const t0 = ws[0]?.start ?? 1;
  ws = ws.filter(w => w.start - t0 < 2.7);
  const rel = ws.map(w => ({ text: w.text, t: +(w.start - t0 + .1).toFixed(2), e: +(w.end - t0 + .1).toFixed(2) }));
  const grade = lib('looks').grades?.find(g => g.id === lk.grade)?.css || 'none';
  const q = new URLSearchParams({ t: t0.toFixed(1), text: ws.map(w => w.text).join(' ') || 'your words here', ws: JSON.stringify(rel),
    params: JSON.stringify({ tx, grade_css: grade, title: V().hook?.text || '' }) });
  return `/prev/${P.id}/_style?${q}`;
}

function pHook() {
  const v = V(), q = hookQuery.toLowerCase();
  const hooks = lib('hooks').filter(h => !q || (h.template + ' ' + (h.example || '')).toLowerCase().includes(q));
  return cardHead('Hook') + overview([
    ['Hook on screen', v.hook.text ? `“${esc(v.hook.text)}” for ${v.hook.duration} s` : 'none yet'],
    ['From', v.hook.id ? `${esc(v.hook.id)} · 100+ Viral Hooks doc` : '—'],
    ['Other openings', v.hook.variants.length ? v.hook.variants.map(x => '“' + esc(x) + '”').join(', ') + ' (trial reels)' : 'none'],
  ]) + `
  <label>Hook text (shown in the first seconds)<input data-bind="v.hook.text" data-step="hook" value="${esc(v.hook.text)}" placeholder="Pick one below or write your own"></label>
  <div class="inline" style="margin-top:var(--g1)"><label>Seconds on screen<input type="number" min="1" max="6" step="0.2" data-bind="v.hook.duration" data-num data-step="hook" value="${v.hook.duration}"></label>
    <button class="small" data-act="variant" ${v.hook.text ? '' : 'disabled'}>Keep as another opening</button></div>
  <h3 class="section-title">Hooks <span class="count">${hooks.length} of ${lib('hooks').length} · 100+ Viral Hooks doc</span></h3>
  <input id="hookq" placeholder="Search hooks…" value="${esc(hookQuery)}">
  <div class="rows" style="margin-top:var(--g1)">${hooks.map(h => `<div class="rowi" aria-pressed="${v.hook.id === h.id}"><div><span class="t">${esc(h.template)}</span>${h.example ? `<span class="m">e.g. ${esc(h.example)}</span>` : ''}</div>
    <div class="acts"><button class="small" data-act="hook" data-id="${h.id}" data-use="template">Use template</button>${h.example ? `<button class="small quiet" data-act="hook" data-id="${h.id}" data-use="example">Use example</button>` : ''}</div></div>`).join('')}</div>`;
}

/* the selected word, or words (Shift-click a second word, or "whole line"): kept words only */
function selWords() {
  if (selWord == null || !P.edl) return [];
  const a = Math.min(selWord, selEnd ?? selWord), z = Math.max(selWord, selEnd ?? selWord);
  return P.edl.words.slice(a, z + 1).filter(w => !w.cut);
}
const selText = () => selWords().map(w => w.text).join(' ');
/* one effect box: the effect's own template, looping on a still of your take at the selected words */
function fxPreviewSrc(effId) {
  const ws = selWords(), first = ws[0];
  const t0 = first ? first.start : (P.edl?.words.find(w => !w.cut)?.start ?? 1);
  const rel = ws.map(w => ({ text: w.text, t: +(w.start - t0).toFixed(2), e: +(w.end - t0).toFixed(2) }));
  const q = new URLSearchParams({ t: t0.toFixed(1), text: ws.length ? selText() : 'your words here', ws: JSON.stringify(rel) });
  if (effId === 'xp-background') q.set('att', (ATTACH.slice(-1)[0] || {}).name || '');
  return `/prev/${P.id}/${effId}?${q}`;
}
function sizePreviews() { document.querySelectorAll('.fxprev').forEach(el => el.style.setProperty('--k', el.clientWidth / 1080)); }
window.addEventListener('resize', sizePreviews);

function wordStrip(note, lines) {
  if (!P.edl) return '<div class="empty">Transcribe first (Brief step).</div>';
  const v = V(), fxWords = new Set([...v.effects, ...v.overlays, ...v.sfx].filter(x => x.status !== 'removed').flatMap(x => { const o = []; for (let k = x.word_i; k <= (x.word_end_i ?? x.word_i); k++) o.push(k); return o; }));
  const selSet = new Set(selWords().map(w => w.i)); if (selWord != null) selSet.add(selWord);
  return `<p class="help">${note}</p><div class="script strip">${sentences().map(ws => {
    const kept = ws.filter(w => !w.cut); if (!kept.length) return '';
    return `<div class="line"><time data-t="${kept[0].start}">${fmt(kept[0].start)}</time><div class="words">${kept.map(w =>
      `<button class="w ${selSet.has(w.i) ? 'sel' : ''} ${fxWords.has(w.i) ? 'has-fx' : ''}" data-act="pick" data-i="${w.i}">${esc(w.text)}</button>`).join('')}${lines ? `<button class="w line-pick" data-act="pick-line" data-a="${kept[0].i}" data-z="${kept[kept.length - 1].i}" title="Select the whole line">⤢ whole line</button>` : ''}</div></div>`;
  }).join('')}</div>`;
}
function effectFields(x) {
  const eff = effectById(x.effect); if (!eff || !eff.fields?.length || x.status === 'removed') return '';
  x.params = x.params || {};
  return `<div class="fx-fields">${eff.fields.map(f => f.type === 'note' ? `<p class="meta">${esc(f.label)} · ${IMAGES.length} photos now</p>` :
    `<label>${esc(f.label)}${f.required ? ' *' : ''}<input ${f.type === 'color' ? 'type="color" style="height:40px;padding:3px"' : ''} data-fx="${x.id}" data-key="${f.key}"
      value="${esc(x.params[f.key] ?? (f.type === 'color' ? f.placeholder : ''))}" placeholder="${esc(f.placeholder === 'the word' || f.placeholder === 'the words you selected' ? x.word : (f.placeholder || ''))}"></label>`).join('')}</div>`;
}
function placedCard(kind, x, title, sub, thumb) {
  const labels = { effect: 'Effect', image: 'Image', sound: 'Sound' };
  return `<div class="placed ${x.status === 'removed' ? 'removed' : ''} ${x.status === 'proposed' ? 'proposed' : ''}">
    ${thumb ? `<img src="${thumb}" alt="">` : `<img alt="">`}
    <div><span class="kind">${esc(labels[kind] || kind)}${x.status === 'proposed' ? ' · proposed' : x.status === 'removed' ? ' · removed' : ''}</span>
      <div class="ttl">${esc(title)}</div><span class="meta">${esc(sub || '')}</span>
      <div class="acts">${x.status === 'removed' ? `<button class="small keep" data-act="status" data-kind="${kind}" data-id="${x.id}" data-to="kept">↺ Put back</button>` : `
        <button class="small keep" data-act="status" data-kind="${kind}" data-id="${x.id}" data-to="kept">✓ Keep</button>
        <button class="small change" data-act="change" data-kind="${kind}" data-id="${x.id}">✎ Change</button>
        <button class="small remove" data-act="status" data-kind="${kind}" data-id="${x.id}" data-to="removed">✕ Remove</button>`}</div></div>
    <span class="timepill">${fmt(x.at)}</span>
    ${kind === 'effect' ? effectFields(x) : ''}</div>`;
}
const thumbAt = t => P.source ? `/files/${P.id}/${P.source.thumbs[Math.min(P.source.thumbs.length - 1, Math.floor(t))]}` : '';
/* stock on your words (24 Nov 2026): Pexels photos pop up on a word, Pexels videos play as a short cutaway on it */
function stockBox() {
  const has = !!SETTINGS.pexels;
  return `<h3 class="section-title">Stock on your words <span class="count">Pexels · free, no watermark</span></h3>
  <p class="help">The engine finds the words you say that can be shown (food, a phone, friends, the city…) and searches Pexels for photos and videos for each. <b>Click one</b>: a photo pops up on that word, a video plays as a short cutaway while you keep talking. Or type anything and search yourself (it goes on the word you selected above).</p>
  ${has ? '' : `<div class="inline"><label>Your free Pexels key (pexels.com/api → “Your API key”, takes a minute)<input id="pexelskey2" placeholder="paste the key here"></label><button class="small" data-act="pexels-key2">Save key</button></div>`}
  <div class="inline" style="margin:8px 0"><button class="small" data-act="stock-find" ${has ? '' : 'disabled'}>Find stock for my words</button>
    <input id="stockq" placeholder="or search Pexels: e.g. pizza delivery at night" ${has ? '' : 'disabled'}><button class="small" data-act="stock-search" ${has ? '' : 'disabled'}>Search</button></div>
  ${STOCK ? (STOCK.length ? STOCK.map((r, k) => `<div class="stockrow"><b>${r.word_i != null ? '“' + esc(r.word) + '”' : esc(r.query)}</b> <span class="meta">${r.at != null ? fmt(r.at) + ' · ' : ''}searched “${esc(r.query)}”</span>
    <div class="stockgrid">${(r.items || []).map((it, j) => `<button class="stockitem" data-act="stock-pick" data-k="${k}" data-j="${j}" title="${it.kind === 'video' ? 'Insert this video on the word' : 'Pop this photo up on the word'}${it.by ? ' · by ' + esc(it.by) : ''}"><img src="${esc(it.thumb)}" alt="" loading="lazy">${it.kind === 'video' ? `<span class="vtag">▶ ${Math.round(it.duration || 0)} s</span>` : '<span class="vtag">photo</span>'}</button>`).join('') || `<span class="meta">${esc(r.error || 'Nothing found on Pexels')}</span>`}</div></div>`).join('')
    : '<p class="meta">No words in this video name something to show. Search for one yourself.</p>') : ''}`;
}
/* Memes on phrases (25 Nov 2026): the engine reads the phrases, matches their words with a reaction category and offers
   GIFs (GIPHY) and pictures from Alina's Pinterest library for each; plus a reaction library for any second. */
const memeTag = it => it.kind === 'gif' ? 'GIF' : it.folder === 'Obiecte' ? 'object' : 'Pinterest';
const memeThumb = (it, act, k, j, placed) => `<button class="stockitem memeitem${placed ? ' on' : ''}" data-act="${act}" data-k="${k}" data-j="${j}" title="${esc(it.kind === 'gif' ? (it.title || 'GIF') + (it.by ? ' · by ' + it.by : '') + ' · GIPHY' : it.shows + (it.meaning ? ' — ' + it.meaning : '') + ' · ' + it.file)}"><img src="${esc(it.thumb)}" alt="" loading="lazy"><span class="vtag">${memeTag(it)}</span>${placed ? '<span class="vtag ok">✓ on</span>' : ''}</button>`;
function memePlacedAt(at, it) { return V().overlays.some(o => o.kind === 'meme' && o.status !== 'removed' && Math.abs(o.at - at) < 0.05 && (!it || String(o.image).includes(it.kind === 'gif' ? it.id : String(it.cutout || it.file).split('/').pop()))); }
function pMemes() {
  const v = V(), on = v.overlays.filter(o => o.kind === 'meme' && o.status !== 'removed');
  const vid = $('#vid'), now = vid ? vid.currentTime : 0;
  return cardHead('Memes on phrases') + overview([
    ['On screen', on.length ? `${on.length} meme${on.length > 1 ? 's' : ''} · ${on.map(o => fmt(o.at)).join(', ')}` : 'none yet'],
    ['GIFs', SETTINGS.giphy ? 'GIPHY, searched live' : 'add your free GIPHY key below to get GIFs'],
    ['Pictures', 'your Pinterest library (Pinterest FeedMe - Emotii, by emotion, plus Obiecte) and pins you paste'],
  ]) + `
  <p class="help">The engine reads your phrases and matches their words with a kind of reaction (mind blown, no idea, fingers crossed, for nothing…). For each moment it shows <b>GIFs from GIPHY</b> and <b>pictures from your Pinterest library</b>. <b>Click one</b> to put it on that phrase; click another to swap it. <b>Show 12 more</b> opens more, <b>No meme here</b> skips the moment, or type your own search. Below is the whole reaction library for any second.</p>
  ${SETTINGS.giphy ? '' : `<div class="inline"><label>Your free GIPHY key (developers.giphy.com → Create an App → API → copy the key)<input id="giphykey" placeholder="paste the key here"></label><button class="small" data-act="giphy-key">Save key</button></div>`}
  <div class="inline" style="margin:8px 0"><button class="small" data-act="memes-find" ${P.edl ? '' : 'disabled'}>${MEMES ? 'Look again' : 'Find meme moments in my phrases'}</button>${P.edl ? '' : '<span class="meta">Transcribe first (Brief step).</span>'}</div>
  ${MEMES ? (MEMES.length ? MEMES.map((m, k) => `<div class="stockrow memerow">
    <div class="row" style="gap:8px;align-items:baseline;flex-wrap:wrap"><span class="timepill">${fmt(m.start)}</span><b>„${esc(m.text)}”</b><span class="meta">${esc(m.cat_names.join(' · '))} · searched: ${esc(m.terms.join(' / '))}</span></div>
    <div class="stockgrid">${(m.items || []).map((it, j) => memeThumb(it, 'meme-pick', k, j, memePlacedAt(m.start, it))).join('') || `<span class="meta">${esc(m.error || 'Nothing found. Try your own words below.')}</span>`}</div>
    <div class="row" style="gap:6px;margin-top:6px"><button class="small" data-act="meme-more" data-k="${k}" ${SETTINGS.giphy ? '' : 'disabled'}>Show 12 more</button><button class="small" data-act="meme-none" data-k="${k}">No meme here</button>
      <input data-memeq="${k}" placeholder="None fit? Type what to search (e.g. happy dance)" style="flex:1;min-width:200px"><button class="small" data-act="meme-q" data-k="${k}">Search</button></div>
  </div>`).join('') : '<p class="meta">No phrase here has a clear reaction. Use the library below for any second.</p>') : ''}
  <h3 class="section-title">Reaction library <span class="count">for any second · goes on ${fmt(now)}, where the player is</span></h3>
  <p class="help">Pause the video where you want the meme, then click one. Pick a reaction, one of your Pinterest folders, or search anything.</p>
  <div class="chips">${(MEMELIB?.cats || []).map(c => `<a href="#" data-act="meme-cat" data-id="${esc(c.id)}" class="${MEMELIB?.label === c.name ? 'on' : ''}">${esc(c.name)}</a>`).join('')}</div>
  <div class="chips">${(MEMELIB?.folders || []).map(f => `<a href="#" data-act="meme-folder" data-id="${esc(f)}" class="${MEMELIB?.label === f ? 'on' : ''}">📌 ${esc(f)}</a>`).join('')}</div>
  <div class="inline" style="margin:6px 0"><input id="memelibq" placeholder="search GIPHY and your library: e.g. mind blown, hungry cat, finally"><button class="small" data-act="meme-libsearch">Search</button></div>
  <div class="inline" style="margin:6px 0"><input id="pinurl" placeholder="add from Pinterest: paste a pin link (pinterest.com/pin/… or pin.it/…)"><button class="small" data-act="meme-pin">Add pin</button></div>
  ${MEMELIB?.items ? `<p class="meta">${esc(MEMELIB.label || '')} · ${MEMELIB.items.length} ${MEMELIB.error ? '· ' + esc(MEMELIB.error) : ''}</p><div class="stockgrid">${MEMELIB.items.map((it, j) => memeThumb(it, 'meme-libpick', 0, j, false)).join('') || '<span class="meta">Nothing found.</span>'}</div>` : ''}
  <h3 class="section-title">Memes on screen</h3>
  <div class="stack" style="gap:6px">${on.sort((a, b) => a.at - b.at).map(o => placedCard('image', o, `Meme on „${o.phrase || P.edl?.words[o.word_i]?.text || ''}”`, o.source, imgUrl(o.image))).join('') || '<p class="meta">Nothing yet.</p>'}</div>
  <p class="meta" style="margin-top:12px">GIFs: Powered by GIPHY. Pictures: your Pinterest boards.</p>`;
}

function pEffects() {
  const v = V(), groups = ['all', ...new Set(lib('effects').map(e => e.group))];
  const ws = selWords(), txt = selText();
  const effs = lib('effects').filter(e => effGroup === 'all' || e.group === effGroup);
  const short = txt.length > 34 ? txt.slice(0, 32) + '…' : txt;
  return cardHead('Effects on words') + overview([
    ['On screen', `${v.effects.filter(e => e.status !== 'removed').length} effects · ${v.overlays.filter(o => o.status !== 'removed').length} images on words`],
    ['Selected', ws.length ? `“${esc(txt)}” at ${fmt(ws[0].start)}${ws.length > 1 ? ` · ${ws.length} words` : ''}` : 'click a word below (Shift-click a second word for a phrase, or “whole line”)'],
    ['Rendered by', `all ${lib('effects').length} effects render on export: ffmpeg or a HyperFrames template, each one 3 s from the first selected word`],
  ]) + wordStrip('Pick the word or sentence: click a word, <b>Shift-click</b> another word to take everything between, or <b>⤢ whole line</b>. Every effect box below then plays that effect with your words on your own frame. Press <b>Apply</b> on the one you like.', true) + `
  <h3 class="section-title">On screen, in order</h3>
  <div class="stack" style="gap:6px">${[...v.effects.map(e => ({ ...e, _k: 'effect' })), ...v.overlays.map(o => ({ ...o, _k: 'image' }))].sort((a, b) => a.at - b.at).map(x =>
    x._k === 'effect' ? placedCard('effect', x, `${effectById(x.effect)?.name || x.effect} on “${x.word}”`, x.note || effectById(x.effect)?.layer, thumbAt(x.at))
      : x.kind === 'clip' ? placedCard('image', x, x.image ? `Example clip on “${x.phrase || ''}”` : `Example clip to find: “${x.phrase || ''}”`, `${x.source || 'search: ' + (x.query || '')} · ${x.why || ''}`, thumbAt(x.at))
      : placedCard('image', x, `${x.image.split('/').pop()} on “${P.edl?.words[x.word_i]?.text || ''}”`, x.why, imgUrl(x.image))).join('') || '<p class="meta">Nothing yet.</p>'}</div>
  ${stockBox()}
  <h3 class="section-title">Effect library <span class="count">${lib('effects').length}${ws.length ? ` · previews with “${esc(short)}”` : ' · previews with sample words until you pick'}</span></h3>
  <div class="chips">${groups.map(g => `<a href="#" class="${effGroup === g ? 'on' : ''}" data-effg="${esc(g)}">${esc(g)}</a>`).join('')}</div>
  ${P.source?.proxy ? '' : '<p class="meta">Add footage first: the previews play on a frame of your take.</p>'}
  <div class="fxgrid">${effs.map(e => `<div class="fxcard" title="${esc(e.trigger || '')}">
    <h4>${esc(e.name)}${e.status === 'draft' ? ' <span class="draft">draft</span>' : ''}</h4>
    <div class="fxprev">${P.source?.proxy ? `<iframe loading="lazy" src="${fxPreviewSrc(e.id)}" tabindex="-1" aria-label="Preview of ${esc(e.name)}"></iframe>` : ''}</div>
    ${e.id === 'word-image-pop' && IMAGES.length ? `<select data-img style="width:100%;padding:4px 8px;font-size:12px">${IMAGES.map(i => `<option value="${esc(i.path)}">${esc(i.name)}</option>`).join('')}</select>` : ''}
    <button class="small" data-act="put-effect" data-id="${e.id}" ${ws.length ? '' : 'disabled'}>${ws.length ? 'Apply to “' + esc(short) + '”' : 'Pick words first'}</button>
  </div>`).join('')}</div>`;
}

function pText() {
  const v = V(), tx = v.text, looks = lib('looks'), sample = v.hook.text || P.edl?.words.slice(0, 4).map(w => w.text).join(' ') || 'Your words here';
  const fonts = looks.fonts.filter(f => fontFilter === 'all' || f.group === fontFilter);
  const seg = (key, opts) => `<div class="seg">${opts.map(([val, n]) => `<a href="#" data-tx="${key}" data-val="${val}" ${String(tx[key]) === String(val) ? 'aria-current="true"' : ''}>${n}</a>`).join('')}</div>`;
  return cardHead('Text: fonts, colours, boxes') + overview([
    ['Captions', `${esc(tx.font)} · ${tx.words_per_line} word${tx.words_per_line > 1 ? 's' : ''} at a time · ${esc(tx.position)} · ${esc(tx.case)}`],
    ['Title', esc(tx.title_font)],
    ['Colours', `<span class="swatches"><i style="background:${tx.color}" title="text"></i><i style="background:${tx.highlight}" title="spoken word"></i><i style="background:${tx.outline}" title="outline"></i></span>`],
    ['Text box', esc(looks.textboxes.find(b => b.id === tx.box)?.name || tx.box)],
  ]) + `
  <label class="check"><input type="checkbox" data-captions ${v.captions !== false ? 'checked' : ''}> Word-by-word captions</label>
  <p class="help" style="margin-top:10px"><b>Move and resize on the preview:</b> drag the dashed Captions or Title box to any place; pull its corner to make it bigger or smaller. Double-click a box to put it back where the style places it.</p>
  <div class="row"><button class="small" data-act="reset-place" data-k="cap" ${tx.cap_pos ? '' : 'disabled'}>Captions back to the style's place</button><button class="small" data-act="reset-place" data-k="title" ${tx.title_pos || tx.title_size ? '' : 'disabled'}>Title back to the style's place</button></div>
  <h3 class="section-title">Caption motion <span class="count">${(looks.caption_anims || []).length}</span></h3>
  <div class="opts">${(looks.caption_anims || []).map(a => `<button class="opt" data-act="anim" data-id="${a.id}" aria-pressed="${(tx.anim || 'pop') === a.id}"><h4>${esc(a.name)}</h4><p>${esc(a.note)}</p></button>`).join('')}</div>
  <h3 class="section-title">Font <span class="count">${looks.fonts.length} · Vetto faces + Google Fonts</span></h3>
  <div class="chips">${looks.font_groups.map(g => `<a href="#" class="${fontFilter === g ? 'on' : ''}" data-ff="${g}">${g}</a>`).join('')}</div>
  <div class="opts">${fonts.map(f => `<button class="opt fontcard" data-act="font" data-f="${esc(f.family)}" aria-pressed="${tx.font === f.family}">
    <div class="sample" style="font-family:'${esc(f.family)}';font-weight:${f.weight};font-style:${f.style}">${esc(sample)}</div>
    <div class="row"><h4>${esc(f.family)}${f.ro === false ? ' · <span style="color:var(--warn)">no ș ț</span>' : ''}</h4><a href="#" class="meta" data-act="titlefont" data-f="${esc(f.family)}" style="margin:0">${tx.title_font === f.family ? 'title ✓' : 'use for title'}</a></div></button>`).join('')}</div>
  <h3 class="section-title">Colours <span class="count">${looks.palettes.length}</span></h3>
  <div class="row" style="margin-bottom:10px"><button class="small" data-act="palette-from-video" ${P.source ? '' : 'disabled'}>Colours from my video (this frame)</button><span class="meta">Pause on a frame you like; the engine picks its main colours.</span></div>
  <div class="opts">${looks.palettes.map(p => `<button class="opt" data-act="palette" data-id="${p.id}"><div class="swatches">${[p.text, p.highlight, p.outline, ...(p.swatches || [])].map(c => `<i style="background:${c}"></i>`).join('')}</div><h4>${esc(p.name)}</h4><p>${esc(p.source)}</p></button>`).join('')}</div>
  <div class="grid-form" style="grid-template-columns:repeat(4,minmax(0,1fr))">
    ${[['color', 'Text'], ['highlight', 'Spoken word'], ['outline', 'Outline'], ['box_color', 'Box']].map(([k, n]) => `<label>${n}<input type="color" data-bind="v.text.${k}" data-step="text" value="${tx[k] || '#000000'}" style="height:44px;padding:4px"></label>`).join('')}
  </div>
  <h3 class="section-title">Text box</h3>
  <div class="opts">${looks.textboxes.map(b => `<button class="opt" data-act="box" data-id="${b.id}" aria-pressed="${tx.box === b.id}"><h4>${esc(b.name)}</h4><p>${esc(b.note)}</p></button>`).join('')}</div>
  <h3 class="section-title">Where</h3>${seg('position', [['upper', 'Top'], ['middle', 'Middle'], ['lower', 'Bottom']])}
  <h3 class="section-title">Words at a time</h3>${seg('words_per_line', [[1, '1'], [2, '2'], [3, '3'], [4, '4']])}
  <h3 class="section-title">Case</h3>${seg('case', [['as spoken', 'As spoken'], ['upper', 'UPPER'], ['lower', 'lower']])}
  <h3 class="section-title">Size</h3><input type="range" min="48" max="120" data-bind="v.text.size" data-num data-step="text" value="${tx.size}">`;
}

let audio = null;
function pSound() {
  const v = V(), cats = ['all', ...new Set(lib('sfx').map(s => s.category))], w = selWord != null ? P.edl?.words[selWord] : null;
  return cardHead('Sound') + overview([
    ['Sounds placed', `${v.sfx.filter(x => x.status !== 'removed').length}`],
    ['Voice', 'denoised and levelled to −14 LUFS on render'],
    ['Library', `${lib('sfx').length} sounds: your Drive folder + the Meme Chaos packs`],
    ['Selected word', w ? `“${esc(w.text)}” at ${fmt(w.start)}` : 'click a word below'],
  ]) + wordStrip('Click a word, then press <b>Put here</b> on a sound. Quick rules below make proposals you keep or remove.') + `
  <div class="row" style="margin:var(--g2) 0"><button class="small" data-act="rule" data-rule="images">Whoosh on every image</button><button class="small" data-act="rule" data-rule="effects">Pop on every effect</button><button class="small" data-act="rule" data-rule="hook">Sparkle when the hook ends</button></div>
  <div class="stack" style="gap:6px">${v.sfx.slice().sort((a, b) => a.at - b.at).map(x => placedCard('sound', x, `${x.name} on “${P.edl?.words[x.word_i]?.text || ''}”`, `volume ${Math.round((x.volume ?? .5) * 100)}%`, thumbAt(x.at))).join('') || '<p class="meta">No sounds yet.</p>'}</div>
  <h3 class="section-title">Library</h3>
  <div class="chips">${cats.map(c => `<a href="#" class="${sfxCat === c ? 'on' : ''}" data-sfxc="${c}">${c}</a>`).join('')}</div>
  <div class="rows">${lib('sfx').filter(s => sfxCat === 'all' || s.category === sfxCat).map(s => `<div class="rowi"><div><span class="t">${esc(s.name)}</span><span class="m">${esc(s.category)} · ${(+s.duration_s || 0).toFixed(2)} s</span></div>
    <div class="acts"><button class="small quiet" data-act="play-sfx" data-f="${esc(s.file)}">▶</button><button class="small" data-act="put-sfx" data-id="${s.id}" ${w ? '' : 'disabled'}>Put here</button></div></div>`).join('')}</div>`;
}

function pOutputs() {
  const v = V(), bs = beats(), want = P.brief.outputs || [];
  return cardHead('Outputs') + overview([
    ['Reel', P.source ? `${fmt(stats().out)} · 1080×1920` : '—'],
    ['Stories', v.outputs.stories.length ? v.outputs.stories.map((s, k) => `${k + 1}: ${fmt(s.from)}–${fmt(s.to)}`).join(' · ') : (want.includes('stories') ? 'not split yet' : 'not asked for in the brief')],
    ['Carousel', v.outputs.carousel.slides.length ? `${v.outputs.carousel.slides.length} slides, 4:5` : (want.includes('carousel') ? 'not drafted yet' : 'not asked for in the brief')],
  ]) + `
  <p class="help">The reel already has the idea. Stories and the carousel are drafted from its beats: change any text, drop a slide, or ask Claude to rewrite them in your words.</p>
  <h3 class="section-title">Stories (15 s or less each)</h3>
  <div class="row"><button class="small" data-act="split-stories" ${bs.length ? '' : 'disabled'}>Split the reel at sentence ends</button></div>
  <div class="row" style="margin-top:var(--g1)">${v.outputs.stories.map((s, k) => `<span class="pill">${k + 1} · ${fmt(s.from)}–${fmt(s.to)} · ${(s.to - s.from).toFixed(1)} s</span>`).join('')}</div>
  <h3 class="section-title">Carousel</h3>
  <div class="row"><button class="small" data-act="draft-carousel" ${bs.length ? '' : 'disabled'}>Draft slides from the beats</button></div>
  <div class="slides" style="margin-top:var(--g2)">${v.outputs.carousel.slides.map((s, k) => `<div class="slide"><div class="s" style="background-image:url('${thumbAt(s.t)}')">${k + 1}</div>
    <textarea data-slide="${k}">${esc(s.text)}</textarea><button class="small quiet" data-act="drop-slide" data-k="${k}">Remove</button></div>`).join('')}</div>`;
}

/* ---------- Trim & view (24 Nov 2026, Alina: "a trim and view page that shows the full video with all the cuts and the
   text, music, effects… just like in CapCut, so if I want to cut something, change the text or add another sound I can do
   it from there"). One timeline in reel time: video (what stays after the cut), text (hook + captions), effects, images,
   sounds, music. Drag on the video track to select a part and cut it; click a caption word to change it; drag effects and
   sounds to move them; + Sound / + Effect at the playhead. Everything edits the same data as the other steps. */
const TL = { pps: 0, sel: null, range: null, add: null };
function outToSrc(o, ranges) {
  let acc = 0;
  for (const [a, b] of ranges) { if (o <= acc + (b - a)) return a + Math.max(0, o - acc); acc += b - a; }
  return ranges.length ? ranges[ranges.length - 1][1] : 0;
}
function tlData() {
  const v = V(), ranges = keepRanges(), dur = outLen(ranges);
  const segs = []; let acc = 0;
  for (const [a, b] of ranges) { segs.push({ o: acc, e: acc + b - a, a, b }); acc += b - a; }
  const kept = (P.edl?.words || []).filter(w => !w.cut).map(w => ({ w, o: mapTime(w.start, ranges) })).filter(x => x.o != null);
  const per = Math.max(1, +v.text.words_per_line || 3), caps = [];
  if (v.captions !== false) for (let k = 0; k < kept.length; k += per) {
    const g = kept.slice(k, k + per), nxt = kept[k + per];
    caps.push({ o: g[0].o, e: nxt ? nxt.o : Math.min(dur, g[g.length - 1].o + .6), words: g.map(x => x.w) });
  }
  const sfxLen = f => +(lib('sfx').find(x => x.file === f)?.duration_s) || .6;
  const fx = v.effects.filter(e => e.status !== 'removed').map(e => ({ e, o: mapTime(e.at, ranges) })).filter(x => x.o != null)
    .map(x => ({ ...x, d: ['light-leak', 'light-burn'].includes(x.e.effect) ? .5 : 3 }));
  const imgs = v.overlays.filter(x => x.status !== 'removed').map(x => ({ x, o: mapTime(x.at, ranges) })).filter(y => y.o != null);
  const snd = v.sfx.filter(x => x.status !== 'removed').map(x => ({ x, o: x.clock === 'output' ? x.at : mapTime(x.at, ranges), d: sfxLen(x.file) })).filter(y => y.o != null);
  return { v, ranges, dur, segs, kept, caps, fx, imgs, snd };
}
function nearestWord(o, d) { return (d.kept.reduce((b, x) => Math.abs(x.o - o) < Math.abs(b.o - o) ? x : b, d.kept[0] || { o: 0 })).w; }
function pStoryboard() {
  const v = V(), notApproved = STEPS.slice(0, STEPS.findIndex(s => s.id === 'storyboard')).filter(s => stepState(s.id) !== 'approved');
  if (!P.edl) return cardHead('Trim & view') + '<div class="empty">Add footage and transcribe it first (Footage and Brief steps).</div>';
  if (viewMode() === 'final' && finalRender()) setTimeout(() => { VIEW = 'live'; setSource(); renderViewSeg(); });
  const d = tlData(), box = $('#panel')?.clientWidth || 700;
  if (!TL.pps) TL.pps = Math.max(18, Math.min(160, (box - 120) / Math.max(1, d.dur)));
  const X = o => (o * TL.pps).toFixed(1) + 'px', W = (o, e) => Math.max(4, (e - o) * TL.pps).toFixed(1) + 'px';
  const ticks = []; const step = TL.pps > 60 ? 1 : TL.pps > 25 ? 2 : 5;
  for (let t = 0; t <= d.dur + .01; t += step) ticks.push(`<span style="left:${X(t)}">${fmt(t).replace(/\.\d$/, '')}</span>`);
  const thumbs = seg => { const out = []; for (let t = seg.o; t < seg.e; t += Math.max(1, 60 / TL.pps)) out.push(`<img src="${thumbAt(seg.a + (t - seg.o))}" style="left:${((t - seg.o) * TL.pps).toFixed(1)}px" alt="">`); return out.join(''); };
  const sel = TL.sel, isSel = (k, id) => sel && sel.kind === k && sel.id === id ? 'sel' : '';
  const music = lib('music').find(m => m.id === v.music?.id);
  return cardHead('Trim & view') + `
  <p class="help">Your whole reel on one timeline, like in CapCut. <b>Drag on the video</b> to select a part, then ✂ Cut it. <b>Click a caption word</b> to change its text. <b>Drag</b> effects and sounds to move them, click one to change or remove it. <b>+ Sound</b> and <b>+ Effect</b> add at the playhead. The preview plays your changes live.${notApproved.length ? ` <span class="meta">Steps not approved yet: ${notApproved.map(s => esc(s.name)).join(', ')}.</span>` : ''}</p>
  <div class="tl-bar">
    <button class="small" data-tl="play">▶ / ❚❚</button>
    <button class="small" data-tl="cut" ${TL.range ? '' : 'disabled'}>✂ Cut ${TL.range ? fmt(TL.range[0]) + '–' + fmt(TL.range[1]) : 'selection'}</button>
    <button class="small" data-tl="add-sound">+ Sound</button><button class="small" data-tl="add-fx">+ Effect</button>
    <button class="small" data-tl="undo" ${HIST.length ? '' : 'disabled'}>↶ Undo</button>
    <label class="tl-zoom">Zoom<input type="range" min="12" max="200" value="${Math.round(TL.pps)}" data-tl="zoom"></label>
    <span class="meta">${fmt(d.dur)} · ${d.caps.length} caption lines · ${d.fx.length} effects · ${d.snd.length} sounds${music && v.music?.status !== 'removed' ? ' · music' : ''}</span>
  </div>
  <div class="tl" id="tl"><div class="tl-in" style="width:${X(d.dur + 1)}">
    <div class="tl-ruler" data-tlk="ruler">${ticks.join('')}</div>
    <div class="tl-row" data-row="video"><b class="tl-lab">Video</b>${d.segs.map((g, k) => `<div class="tl-clip vid" style="left:${X(g.o)};width:${W(g.o, g.e)}" title="${fmt(g.a)}–${fmt(g.b)} of the take">${thumbs(g)}</div>`).join('')}
      ${TL.range ? `<div class="tl-range" style="left:${X(TL.range[0])};width:${W(TL.range[0], TL.range[1])}"></div>` : ''}</div>
    <div class="tl-row" data-row="text"><b class="tl-lab">Text</b>
      ${v.hook.text ? `<div class="tl-clip hook ${isSel('hook', 'hook')}" data-tlk="hook" data-id="hook" style="left:0;width:${W(0, Math.min(d.dur, +v.hook.duration || 2.6))}">Hook · ${esc(v.hook.text)}</div>` : ''}
      ${d.caps.map(c => `<div class="tl-clip cap" style="left:${X(c.o)};width:${W(c.o, c.e)}">${c.words.map(w => `<button class="tl-w" data-wi="${w.i}" title="Click to change the text">${esc(w.text)}</button>`).join(' ')}</div>`).join('')}</div>
    <div class="tl-row" data-row="fx"><b class="tl-lab">Effects</b>${d.fx.map(x => `<div class="tl-clip fx ${isSel('fx', x.e.id)} ${x.e.status === 'proposed' ? 'prop' : ''}" data-tlk="fx" data-id="${x.e.id}" style="left:${X(x.o)};width:${W(x.o, x.o + x.d)}">${esc(effectById(x.e.effect)?.name || x.e.effect)}</div>`).join('')}
      ${d.imgs.map(y => `<div class="tl-clip img ${isSel('img', y.x.id)}" data-tlk="img" data-id="${y.x.id}" style="left:${X(y.o)};width:${W(y.o, y.o + (+y.x.hold || 1.6))}">🖼 ${esc(y.x.image.split('/').pop())}</div>`).join('')}</div>
    <div class="tl-row" data-row="sfx"><b class="tl-lab">Sounds</b>${d.snd.map(y => `<div class="tl-clip snd ${isSel('snd', y.x.id)} ${y.x.status === 'proposed' ? 'prop' : ''}" data-tlk="snd" data-id="${y.x.id}" style="left:${X(y.o)};width:${W(y.o, y.o + y.d)}">♪ ${esc(y.x.name || y.x.file)}</div>`).join('')}</div>
    <div class="tl-row" data-row="music"><b class="tl-lab">Music</b>${v.music?.id ? `<div class="tl-clip mus ${isSel('music', 'music')} ${v.music.status === 'removed' ? 'off' : ''}" data-tlk="music" data-id="music" style="left:0;width:${W(0, d.dur)}">♫ ${esc(music?.name || v.music.id)}${v.music.status === 'removed' ? ' (off)' : ''}</div>` : `<button class="small quiet" data-tl="add-music" style="margin-left:8px">+ Music</button>`}</div>
    <div class="tl-head" id="tl-head" title="Drag to move through the video"><i></i></div>
  </div></div>
  <div class="tl-insp" id="tl-insp">${tlInspector(d)}</div>`;
}
function tlInspector(d) {
  const v = V(), s = TL.sel, opts = (list, cur) => list.map(([val, name]) => `<option value="${esc(val)}" ${val === cur ? 'selected' : ''}>${esc(name)}</option>`).join('');
  if (TL.add === 'sound') return `<b>Add a sound at ${fmt(tlNow())}</b><div class="inline"><select id="tl-pick">${opts(lib('sfx').map(x => [x.file, `${x.category} · ${x.name}`]), '')}</select><button class="small" data-tl="play-pick">▶</button><button class="small" data-tl="do-add-sound">Add</button><button class="small quiet" data-tl="close">Cancel</button></div>`;
  if (TL.add === 'fx') return `<b>Add an effect on the word at ${fmt(tlNow())}</b><div class="inline"><select id="tl-pick">${opts(lib('effects').filter(e => e.id !== 'word-image-pop').map(e => [e.id, `${e.group} · ${e.name}`]), '')}</select><button class="small" data-tl="do-add-fx">Add</button><button class="small quiet" data-tl="close">Cancel</button></div>`;
  if (TL.add === 'music') return `<b>Add music</b><div class="inline"><select id="tl-pick">${opts(lib('music').map(m => [m.id, m.name]), '')}</select><button class="small" data-tl="do-add-music">Add</button><button class="small quiet" data-tl="close">Cancel</button></div>`;
  if (!s) return '<p class="meta">Select a clip on the timeline to change it.</p>';
  if (s.kind === 'fx') { const e = v.effects.find(x => x.id === s.id); if (!e) return '';
    return `<b>${esc(effectById(e.effect)?.name || e.effect)}</b> on “${esc(e.word)}” at ${fmt(mapTime(e.at, keepRanges()) || 0)}${e.status === 'proposed' ? ' · proposed' : ''}
      <div class="inline"><label>Change to<select data-tlset="effect">${opts(lib('effects').filter(x => x.id !== 'word-image-pop').map(x => [x.id, `${x.group} · ${x.name}`]), e.effect)}</select></label>
      <button class="small keep" data-tl="keep">✓ Keep</button><button class="small" data-tl="to-head">Move to playhead</button><button class="small remove" data-tl="remove">✕ Remove</button></div>`; }
  if (s.kind === 'snd') { const x = v.sfx.find(y => y.id === s.id); if (!x) return '';
    return `<b>♪ ${esc(x.name || x.file)}</b>${x.why ? ` <span class="meta">${esc(x.why)}</span>` : ''}
      <div class="inline"><label>Sound<select data-tlset="sound">${opts(lib('sfx').map(y => [y.file, `${y.category} · ${y.name}`]), x.file)}</select></label>
      <label>Volume <input type="range" min="0" max="1" step=".05" value="${x.volume ?? .5}" data-tlset="volume"></label>
      <button class="small" data-tl="play-snd">▶</button><button class="small keep" data-tl="keep">✓ Keep</button><button class="small" data-tl="to-head">Move to playhead</button><button class="small remove" data-tl="remove">✕ Remove</button></div>`; }
  if (s.kind === 'img') { const x = v.overlays.find(y => y.id === s.id); if (!x) return '';
    return `<b>🖼 ${esc(x.image.split('/').pop())}</b><div class="inline"><label>Seconds on screen<input type="number" min=".4" max="6" step=".1" value="${x.hold || 1.6}" data-tlset="hold"></label><button class="small" data-tl="to-head">Move to playhead</button><button class="small remove" data-tl="remove">✕ Remove</button></div>`; }
  if (s.kind === 'hook') return `<b>Hook</b><div class="inline"><label>Text<input data-tlset="hook" value="${esc(v.hook.text)}"></label><label>Seconds<input type="number" min="1" max="6" step=".2" value="${v.hook.duration}" data-tlset="hookdur"></label></div>`;
  if (s.kind === 'music') { const m = v.music;
    return `<b>♫ Music</b><div class="inline"><label>Track<select data-tlset="music">${opts(lib('music').map(x => [x.id, x.name]), m.id)}</select></label>
      <label>Volume <input type="range" min="0" max=".6" step=".01" value="${m.volume ?? .12}" data-tlset="mvol"></label>
      <button class="small" data-tl="music-onoff">${m.status === 'removed' ? 'Music on' : 'Music off'}</button></div>
      ${lib('music').find(x => x.id === m.id)?.credit ? `<p class="meta">${esc(lib('music').find(x => x.id === m.id).credit)}</p>` : ''}`; }
  return '';
}
/* the red playhead follows the video: every screen refresh (tick) and every time update of the video, so it keeps up
   even when the browser slows refreshes down */
function syncHead() {
  const head = STEP === 'storyboard' && $('#tl-head'), vid = $('#vid');
  if (!head || !vid || TL.dragging) return;
  const out = mapTime(vid.currentTime, keepRanges()); if (out == null) return;
  head.style.left = (out * TL.pps) + 'px';
  const tl = $('#tl'), x = out * TL.pps + 78;
  if (tl && !vid.paused && (x > tl.scrollLeft + tl.clientWidth - 40 || x < tl.scrollLeft)) tl.scrollLeft = Math.max(0, x - 120);
}
function tlNow() { const vid = $('#vid'); return vid ? (mapTime(vid.currentTime, keepRanges()) ?? 0) : 0; }
function tlStep(kind) { return { fx: 'effects', img: 'effects', snd: 'sound', music: 'sound', hook: 'hook', cut: 'cut' }[kind] || 'storyboard'; }
function bindTimeline() {
  const tl = $('#tl'); if (!tl) return;
  const v = V(), vid = $('#vid'), xo = e => (e.clientX - tl.querySelector('.tl-in').getBoundingClientRect().left) / TL.pps;
  const rerender = () => { const sc = tl.scrollLeft; renderPanel(); const n = $('#tl'); if (n) n.scrollLeft = sc; };
  // the red playhead: drag it (or drag on the ruler, or click an empty spot of any track) to move through the video
  const head = $('#tl-head'), dur = outLen(keepRanges());
  const place = o => { head.style.left = (o * TL.pps) + 'px'; };
  place(tlNow());
  if (!vid.__tlSync) { vid.__tlSync = true; ['timeupdate', 'seeked', 'play', 'pause'].forEach(ev => vid.addEventListener(ev, syncHead)); }
  const scrub = e => {
    e.preventDefault(); e.stopPropagation();
    const wasPlaying = !vid.paused; vid.pause(); TL.dragging = true;
    const go = ev => {
      const o = Math.max(0, Math.min(dur, xo(ev)));
      place(o); vid.currentTime = outToSrc(o, keepRanges());
      const r = tl.getBoundingClientRect();     // keep the playhead in view while dragging near the edges
      if (ev.clientX > r.right - 30) tl.scrollLeft += 20; else if (ev.clientX < r.left + 90) tl.scrollLeft -= 20;
    };
    go(e);
    const up = () => { document.removeEventListener('mousemove', go); document.removeEventListener('mouseup', up); TL.dragging = false; if (wasPlaying) vid.play(); };
    document.addEventListener('mousemove', go); document.addEventListener('mouseup', up);
  };
  head.onmousedown = scrub;
  tl.querySelector('.tl-ruler').onmousedown = scrub;
  tl.querySelectorAll('.tl-row:not([data-row="video"])').forEach(r => r.addEventListener('mousedown', e => { if (e.target === r) scrub(e); }));
  const vrow = tl.querySelector('[data-row="video"]');
  vrow.onmousedown = e => {
    if (e.target.closest('.tl-lab')) return;
    const o0 = Math.max(0, xo(e)); let o1 = o0;
    const mv = ev => { o1 = Math.max(0, xo(ev)); TL.range = [Math.min(o0, o1), Math.max(o0, o1)]; const r = vrow.querySelector('.tl-range') || vrow.appendChild(Object.assign(document.createElement('div'), { className: 'tl-range' }));
      r.style.left = TL.range[0] * TL.pps + 'px'; r.style.width = Math.max(2, (TL.range[1] - TL.range[0]) * TL.pps) + 'px'; };
    const up = () => { document.removeEventListener('mousemove', mv); document.removeEventListener('mouseup', up);
      if (Math.abs(o1 - o0) < .08) { TL.range = null; vid.currentTime = outToSrc(o0, keepRanges()); } rerender(); };
    document.addEventListener('mousemove', mv); document.addEventListener('mouseup', up);
  };
  // caption words: click to change the text
  tl.querySelectorAll('.tl-w').forEach(b => b.onclick = e => { e.stopPropagation(); const w = P.edl.words[+b.dataset.wi]; vid.currentTime = w.start; editWord(b, w); });
  // clips: click selects, drag moves (effects and images snap to a word; sounds keep their exact time)
  tl.querySelectorAll('[data-tlk]').forEach(c => {
    if (c.dataset.tlk === 'ruler') return;
    c.onmousedown = e => {
      e.stopPropagation();
      const kind = c.dataset.tlk, id = c.dataset.id, x0 = e.clientX, left0 = parseFloat(c.style.left);
      let moved = false;
      const mv = ev => { const dx = ev.clientX - x0; if (Math.abs(dx) > 3 && ['fx', 'snd', 'img'].includes(kind)) { moved = true; c.style.left = (left0 + dx) + 'px'; c.classList.add('drag'); } };
      const up = ev => {
        document.removeEventListener('mousemove', mv); document.removeEventListener('mouseup', up);
        TL.sel = { kind, id }; TL.add = null;
        if (moved) tlMoveTo(kind, id, Math.max(0, (left0 + ev.clientX - x0) / TL.pps));
        rerender();
      };
      document.addEventListener('mousemove', mv); document.addEventListener('mouseup', up);
    };
  });
  // toolbar and inspector
  $('#panel').querySelectorAll('[data-tl]').forEach(b => {
    const act = b.dataset.tl;
    if (act === 'zoom') { b.oninput = () => { TL.pps = +b.value; rerender(); }; return; }
    b.onclick = () => tlAction(act, rerender);
  });
  $('#panel').querySelectorAll('[data-tlset]').forEach(inp => inp.onchange = () => tlSet(inp.dataset.tlset, inp.value, rerender));
}
function tlItem() {
  const v = V(), s = TL.sel; if (!s) return null;
  return s.kind === 'fx' ? v.effects.find(x => x.id === s.id) : s.kind === 'snd' ? v.sfx.find(x => x.id === s.id) : s.kind === 'img' ? v.overlays.find(x => x.id === s.id) : null;
}
function tlMoveTo(kind, id, o) {
  const d = tlData(), v = V(), w = nearestWord(o, d); if (!w) return;
  if (kind === 'fx') { const e = v.effects.find(x => x.id === id); Object.assign(e, { word_i: w.i, word_end_i: w.i, word: w.text, at: w.start }); }
  if (kind === 'img') { const x = v.overlays.find(y => y.id === id); Object.assign(x, { word_i: w.i, at: w.start }); }
  if (kind === 'snd') { const x = v.sfx.find(y => y.id === id); Object.assign(x, { clock: 'output', at: +o.toFixed(3), word_i: w.i }); }
  touch(tlStep(kind), 'storyboard');
}
function tlAction(act, rerender) {
  const v = V(), vid = $('#vid'), d = tlData(), it = tlItem();
  if (act === 'play') { vid.paused ? vid.play() : vid.pause(); return; }
  if (act === 'undo') { $('#undo')?.click(); return; }
  if (act === 'close') { TL.add = null; return rerender(); }
  if (act === 'add-sound') { TL.add = 'sound'; TL.sel = null; return rerender(); }
  if (act === 'add-fx') { TL.add = 'fx'; TL.sel = null; return rerender(); }
  if (act === 'add-music') { TL.add = 'music'; TL.sel = null; return rerender(); }
  if (act === 'play-pick') { new Audio(`/lib/sfx/${encodeURIComponent($('#tl-pick').value)}`).play(); return; }
  if (act === 'play-snd' && it) { const a = new Audio(`/lib/sfx/${encodeURIComponent(it.file)}`); a.volume = Math.min(1, it.volume ?? .5); a.play(); return; }
  if (act === 'do-add-sound') {
    const f = $('#tl-pick').value, meta = lib('sfx').find(x => x.file === f), o = tlNow(), w = nearestWord(o, d);
    const x = { id: 's' + Math.random().toString(16).slice(2, 7), file: f, name: meta?.name || f, clock: 'output', at: +o.toFixed(3), word_i: w?.i ?? 0, volume: .4, status: 'kept', why: 'added in Trim & view' };
    v.sfx.push(x); TL.add = null; TL.sel = { kind: 'snd', id: x.id }; touch('sound', 'storyboard'); return rerender();
  }
  if (act === 'do-add-fx') {
    const eff = effectById($('#tl-pick').value), w = nearestWord(tlNow(), d); if (!w) return;
    const e = { id: 'e' + Math.random().toString(16).slice(2, 7), effect: eff.id, word_i: w.i, word_end_i: w.i, word: w.text, at: w.start, status: 'kept', params: {}, note: 'added in Trim & view' };
    v.effects.push(e); TL.add = null; TL.sel = { kind: 'fx', id: e.id }; touch('effects', 'storyboard'); return rerender();
  }
  if (act === 'do-add-music') { v.music = { ...(v.music || {}), id: $('#tl-pick').value, volume: v.music?.volume ?? .12, status: 'kept', why: 'added in Trim & view' }; TL.add = null; TL.sel = { kind: 'music', id: 'music' }; touch('sound', 'storyboard'); return rerender(); }
  if (act === 'music-onoff') { v.music.status = v.music.status === 'removed' ? 'kept' : 'removed'; touch('sound', 'storyboard'); return rerender(); }
  if (act === 'cut' && TL.range) {
    const [a, b] = TL.range, hit = d.kept.filter(x => x.o >= a - .05 && x.o < b);
    if (!hit.length) { toast('No words in that part (only a pause): shorten pauses in the Cut step'); TL.range = null; return rerender(); }
    hit.forEach(x => { x.w.cut = true; x.w.why = 'cut in Trim & view'; });
    TL.range = null; toast(`Cut ${hit.length} word${hit.length > 1 ? 's' : ''}: “${hit.map(x => x.w.text).join(' ').slice(0, 60)}”`);
    touch('cut', 'storyboard'); return rerender();
  }
  if (!it && TL.sel?.kind !== 'hook') return;
  if (act === 'keep') { it.status = 'kept'; touch(tlStep(TL.sel.kind), 'storyboard'); return rerender(); }
  if (act === 'remove') { it.status = 'removed'; const k = TL.sel.kind; TL.sel = null; touch(tlStep(k), 'storyboard'); return rerender(); }
  if (act === 'to-head') { tlMoveTo(TL.sel.kind, TL.sel.id, tlNow()); return rerender(); }
}
function tlSet(key, val, rerender) {
  const v = V(), it = tlItem();
  if (key === 'effect' && it) { it.effect = val; it.params = {}; touch('effects', 'storyboard'); }
  if (key === 'sound' && it) { const m = lib('sfx').find(x => x.file === val); it.file = val; it.name = m?.name || val; touch('sound', 'storyboard'); }
  if (key === 'volume' && it) { it.volume = +val; touch('sound', 'storyboard'); }
  if (key === 'hold' && it) { it.hold = +val; touch('effects', 'storyboard'); }
  if (key === 'hook') { v.hook.text = val; touch('hook', 'storyboard'); }
  if (key === 'hookdur') { v.hook.duration = +val; touch('hook', 'storyboard'); }
  if (key === 'music') { const m = lib('music').find(x => x.id === val); v.music.id = val; v.music.start = m?.start || 0; touch('sound', 'storyboard'); }
  if (key === 'mvol') { v.music.volume = +val; touch('sound', 'storyboard'); }
  rerender();
}

function hookRead(v) {
  // reading time (lemo-opuscar readcheck): characters ÷ 15 + 1.5 s
  if (!v.hook.text) return ['todo', 'No hook to time'];
  const need = v.hook.text.length / 15 + 1.5, has = +v.hook.duration || 2.6;
  return [has + .05 >= need ? 'ok' : 'warn', has + .05 >= need ? `The hook stays long enough to read (${has.toFixed(1)} s)` : `The hook needs about ${need.toFixed(1)} s to read; it is on screen ${has.toFixed(1)} s`];
}
function sfxSpacing(v) {
  const ts = v.sfx.filter(x => x.status !== 'removed').map(x => x.at).sort((a, b) => a - b);
  const tight = ts.filter((t, i) => i && t - ts[i - 1] < .15).length, dur = stats().out || 1;
  const dense = ts.length / dur > 1.2;
  return [tight || dense ? 'warn' : 'ok', !ts.length ? 'No sound effects' : tight ? `${tight} sound${tight > 1 ? 's' : ''} land within 0.15 s of another` : dense ? 'More than about one sound a second' : `${ts.length} sounds, well spaced`];
}
function pExport() {
  const v = V(), s = stats(), ok = stepState('storyboard') === 'approved';
  const missing = v.effects.filter(e => e.status !== 'removed' && (effectById(e.effect)?.fields || []).some(f => f.required && !String(e.params?.[f.key] ?? '').trim()));
  const needImg = v.effects.filter(e => e.status !== 'removed' && ['pov-carousel-spin', 'greenscreen-cutout'].includes(e.effect) && !IMAGES.length);
  missing.push(...needImg);
  const checks = [
    [s.out <= 90 ? 'ok' : 'warn', `Reel is ${fmt(s.out)}${s.out > 90 ? ': longer than 90 s' : ''}`],
    [s.src && (1 - s.out / s.src) > 0.45 ? 'warn' : 'ok', `${Math.round((1 - s.out / (s.src || 1)) * 100)}% of the footage removed${s.src && (1 - s.out / s.src) > 0.45 ? ': over 45% often means something good went' : ''}`],
    [s.wpm > 190 ? 'warn' : 'ok', `${s.wpm} words a minute${s.wpm > 190 ? ': feels rushed' : ''}`],
    [v.hook.text ? (v.hook.text.split(/\s+/).length > 8 ? 'warn' : 'ok') : 'todo', v.hook.text ? `Hook has ${v.hook.text.split(/\s+/).length} words${v.hook.text.split(/\s+/).length > 8 ? ' (Vetto issue: hooks over 8 words)' : ''}` : 'No hook text'],
    [v.outputs.stories.every(x => x.to - x.from <= 15.05) ? 'ok' : 'bad', `${v.outputs.stories.length} stories, each 15 s or less`],
    [missing.length ? 'bad' : 'ok', missing.length ? `${missing.length} effect${missing.length > 1 ? 's' : ''} missing required fields: ${missing.map(e => effectById(e.effect)?.name).join(', ')}` : 'Every effect has what it needs'],
    hookRead(v),
    sfxSpacing(v),
    [v.hook.text ? 'ok' : 'todo', v.hook.text ? 'The hook is on the very first frame (the cover the grid shows)' : 'No hook: the first frame is the cover, a title helps'],
    [ok ? 'ok' : 'bad', ok ? 'Storyboard approved' : 'Storyboard not approved yet'],
  ];
  return cardHead('Check & export') + `<ul class="checks">${checks.map(([c, t]) => `<li class="${c}">${esc(t)}</li>`).join('')}</ul>
  <div class="row" style="margin:var(--g3) 0"><button data-act="render" data-preview="1" ${P.edl ? '' : 'disabled'}>Quick preview (half size)</button>
    <button class="primary" data-act="render" ${ok ? '' : 'disabled'}>Export the reel</button>
    ${ok ? '' : `<button data-act="${isBeast(styleById(v.style_id)) ? 'edit-now' : 'quick-export'}" ${P.edl && v.style_id ? '' : 'disabled'}>Export now in ${esc(styleById(v.style_id)?.name || 'the style')} (skip approvals)</button>`}
    <button data-act="carousel" ${ok && v.outputs.carousel.slides.length ? '' : 'disabled'}>Export carousel frames</button></div>
  ${ok ? '' : '<p class="meta">The full export opens once the storyboard is approved. “Export now” makes the same full-size reel straight away, without the approvals.</p>'}
  <h3 class="section-title">Open the cut in another editor</h3>
  <p class="help">The approved cut as a project for Premiere Pro or DaVinci Resolve (XML), any editor (EDL), and the captions as a subtitle file (SRT) for CapCut and others. The engine's effects, colour grade and burned captions stay out: these carry the cut and the words, pointing at your original footage.</p>
  <div class="row"><button class="small" data-act="export-nle" ${P.edl ? '' : 'disabled'}>Make the files</button>
  ${v.nle ? Object.entries(v.nle.files).map(([k, f]) => `<a class="button small" href="/files/${P.id}/${f}" download>↓ ${k.toUpperCase()}</a>`).join('') + `<span class="meta">made ${esc(v.nle.at.replace('T', ' '))}</span>` : ''}</div>
  <h3 class="section-title">Renders of this version <span class="count">${v.renders.length}</span></h3>
  <div class="hub renders">${v.renders.slice().reverse().map(r => `<div><video src="/files/${P.id}/${r.file}" controls preload="metadata"></video><div class="render-acts"><a class="button small" href="/files/${P.id}/${r.file}" download>↓ Download</a><button class="small remove" data-act="delete-render" data-file="${esc(r.file)}">✕ Delete</button></div>${r.claude ? `<p class="meta"><b>Claude edit · ${esc(styleById(r.style)?.name || r.style)}</b> ${esc(r.summary || '')}${(r.credits || []).length ? '<br>Credits: ' + r.credits.map(esc).join(' · ') : ''}</p>` : ''}<p class="meta">${r.preview ? 'preview' : r.quick ? 'quick export (steps not approved)' : r.claude ? 'Claude edit' : r.fmt} · ${fmt(r.duration)} · ${esc(r.at.replace('T', ' '))}${r.effects_done?.length ? ` · ${r.effects_done.length} effects in` : ''}</p>${(r.effects_skipped || []).map(x => `<p class="meta" style="color:var(--warn)">Not in this render: ${esc(effectById(x.effect)?.name || x.effect)}: ${esc(x.reason)}</p>`).join('')}</div>`).join('') || '<p class="meta">None yet.</p>'}</div>`;
}

/* ------------------------------------------------------------ events */
let PLAN = { units: [] };
function setPath(path, val) {
  const [root, ...keys] = path.split('.'); let o = root === 'v' ? V() : P;
  for (const k of keys.slice(0, -1)) o = o[k];
  o[keys[keys.length - 1]] = val;
}
function bindPanel() {
  const pn = $('#panel');
  pn.querySelectorAll('[data-bind]').forEach(el => {
    const ev = el.tagName === 'SELECT' || el.type === 'color' || el.type === 'range' ? 'change' : 'input';
    el.addEventListener(ev, () => {
      setPath(el.dataset.bind, el.dataset.num != null ? +el.value : el.value);
      if (el.dataset.bind === 'p.account' && P.account) { const pal = lib('looks').palettes.find(p => p.id === PALETTE_FOR_ACCOUNT[P.account]); }
      touch(el.dataset.step || STEP);
      if (el.tagName === 'SELECT' || el.type === 'range' || el.type === 'color') renderPanel();
    });
  });
  const file = $('#file');
  if (file) {
    const drop = $('#drop');
    file.onchange = () => file.files[0] && upload(file.files[0]);
    drop.ondragover = e => { e.preventDefault(); drop.classList.add('over'); };
    drop.ondragleave = () => drop.classList.remove('over');
    drop.ondrop = e => { e.preventDefault(); drop.classList.remove('over'); e.dataTransfer.files[0] && upload(e.dataTransfer.files[0]); };
  }
  const imgs = $('#imgs');
  if (imgs) imgs.onchange = async () => {
    for (const f of imgs.files) await fetch(`/api/projects/${P.id}/upload?kind=image&name=${encodeURIComponent(f.name)}`, { method: 'POST', body: f });
    IMAGES = await api(`/api/projects/${P.id}/images`); P = await api(`/api/projects/${P.id}`); renderPanel(); renderHead();
  };
  const af = $('#ask-file');
  if (af) af.onchange = async () => {
    const typed = $('#ask')?.value || '';
    for (const f of af.files) {
      const r = await fetch(`/api/projects/${P.id}/upload?kind=attachment&name=${encodeURIComponent(f.name)}`, { method: 'POST', body: f });
      if (r.ok) PENDING.push(f.name);
    }
    ATTACH = await api(`/api/projects/${P.id}/attachments`).catch(() => ATTACH);
    renderPanel(); if ($('#ask')) $('#ask').value = typed;
    toast(`Attached ${af.files.length > 1 ? af.files.length + ' files' : af.files[0].name}`);
  };
  const unit = $('#unit');
  if (unit) unit.onchange = () => { P.plan_unit = unit.value === '' ? null : PLAN.units[+unit.value]; touch('footage'); renderPanel(); };
  const hq = $('#hookq');
  if (hq) hq.oninput = () => { hookQuery = hq.value; const pos = hq.selectionStart; renderPanel(); const n = $('#hookq'); n.focus(); n.setSelectionRange(pos, pos); };
  pn.querySelectorAll('[data-out]').forEach(cb => cb.onchange = () => {
    const s = new Set(P.brief.outputs || []); cb.checked ? s.add(cb.dataset.out) : s.delete(cb.dataset.out); P.brief.outputs = [...s]; touch('brief'); renderPanel();
  });
  const fxr = pn.querySelector('[data-focus]'); if (fxr) fxr.onchange = () => { P.focus_x = +fxr.value / 100; P.versions.forEach(x => x.focus_x = P.focus_x); touch('footage'); };
  pn.querySelectorAll('[data-fx]').forEach(inp => inp.addEventListener(inp.type === 'color' ? 'change' : 'input', () => {
    const x = V().effects.find(e => e.id === inp.dataset.fx); x.params = x.params || {}; x.params[inp.dataset.key] = inp.value; touch('effects');
  }));
  const capt = pn.querySelector('[data-captions]'); if (capt) capt.onchange = () => { V().captions = capt.checked; touch('text'); };
  pn.querySelectorAll('[data-slide]').forEach(t => t.oninput = () => { V().outputs.carousel.slides[+t.dataset.slide].text = t.value; touch('outputs'); });
  pn.querySelectorAll('[data-beatnote]').forEach(t => t.oninput = () => { V().beats[t.dataset.beatnote].note = t.value; save(); });
  pn.querySelectorAll('time[data-t]').forEach(t => t.onclick = () => { $('#vid').currentTime = +t.dataset.t; });
}

async function upload(f) {
  $('#drop').innerHTML = `<b>Uploading ${esc(f.name)}…</b>`;
  const j = await fetch(`/api/projects/${P.id}/upload?kind=footage&name=${encodeURIComponent(f.name)}`, { method: 'POST', body: f }).then(r => r.json());
  await runJob(Promise.resolve(j), 'Preparing the footage');
  setSource(); renderHead(); renderPanel();
}

document.addEventListener('click', async e => {
  if (!P) return;
  const cm = e.target.closest('a[data-cutmode]');
  if (cm) { e.preventDefault(); cutMode = cm.dataset.cutmode; renderPanel(); return; }
  const segA = e.target.closest('a[data-seg]');
  if (segA) { e.preventDefault(); P.brief[segA.dataset.seg] = segA.dataset.val; if (segA.dataset.seg === 'pace') recomputePauses(); touch('brief'); renderPanel(); return; }
  const txA = e.target.closest('a[data-tx]');
  if (txA) { e.preventDefault(); const k = txA.dataset.tx; if (k === 'position') delete V().text.cap_pos; V().text[k] = k === 'words_per_line' ? +txA.dataset.val : txA.dataset.val; touch('text'); renderPanel(); return; }
  const ff = e.target.closest('a[data-ff]'); if (ff) { e.preventDefault(); fontFilter = ff.dataset.ff; renderPanel(); return; }
  const sc = e.target.closest('a[data-sfxc]'); if (sc) { e.preventDefault(); sfxCat = sc.dataset.sfxc; renderPanel(); return; }
  const eg = e.target.closest('a[data-effg]'); if (eg) { e.preventDefault(); effGroup = eg.dataset.effg; renderPanel(); return; }
  const b = e.target.closest('[data-act]'); if (!b || !$('#panel')?.contains(b)) return;
  const act = b.dataset.act, v = V();
  if (b.tagName === 'A') e.preventDefault();
  switch (act) {
    case 'word': {
      const i = +b.dataset.i, w = P.edl.words[i];
      if (cutMode === 'edit' || e.altKey) { editWord(b, w); break; }
      if (e.shiftKey && lastClick != null) {
        const [a, z] = [Math.min(lastClick, i), Math.max(lastClick, i)];
        for (let k = a; k <= z; k++) { P.edl.words[k].cut = true; P.edl.words[k].why = 'cut by you'; }
      } else { w.cut = !w.cut; w.why = w.cut ? 'cut by you' : null; }
      lastClick = i; touch('cut'); renderPanel(); renderHead(); break;
    }
    case 'pause': { const p = P.edl.pauses.find(x => x.id === b.dataset.id); p.keep = !p.keep; touch('cut'); renderPanel(); renderHead(); break; }
    case 'restore-all': P.edl.words.forEach(w => { w.cut = false; w.why = null; }); touch('cut'); renderPanel(); break;
    case 'import': {
      const path = $('#path').value.trim(); if (!path) return;
      await runJob(api(`/api/projects/${P.id}/import`, { method: 'POST', body: JSON.stringify({ path }) }), 'Preparing the footage');
      setSource(); renderHead(); renderPanel(); break;
    }
    case 'pull': {
      const url = $('#pull').value.trim(); if (!url) return;
      try { await runJob(api(`/api/projects/${P.id}/pull`, { method: 'POST', body: JSON.stringify({ url }) }), 'Pulling the reel'); setSource(); renderPanel(); }
      catch (err) { alert(err.message); }
      break;
    }
    case 'analyze': {
      if (P.edl && !confirm('Transcribe again? The cut you made will be replaced.')) return;
      clearTimeout(saveTimer); if (!(await putP())) return;
      b.disabled = true; b.textContent = 'Transcribing…';
      await runJob(api(`/api/projects/${P.id}/analyze`, { method: 'POST' }), 'Transcribing');
      IMAGES = await api(`/api/projects/${P.id}/images`);
      renderHead(); go('cut'); break;
    }
    case 'style': applyStyle(b.dataset.id); touch('style', 'text'); renderPanel(); renderHead(); await styleEdit(b.dataset.id); break;
    case 'style-edit': await styleEdit(v.style_id); break;
    case 'style-version': newVersion(); go('style'); break;
    case 'teach': {
      const links = $('#teach-links').value.trim(), name = $('#teach-name').value.trim();
      if (!links) return;
      await ask(`Teach a new style${name ? ' named “' + name + '”' : ''}: study these videos and pull the fonts, colors, captions and pacing into one style (StyleLab).\n${links}`, 'style', 'teach-style');
      break;
    }
    case 'format': v.format_id = b.dataset.id; touch('hook'); renderPanel(); break;
    case 'hook': { const h = lib('hooks').find(x => x.id === b.dataset.id); v.hook.id = h.id; v.hook.text = b.dataset.use === 'example' ? h.example : h.template; touch('hook'); renderPanel(); renderHead(); break; }
    case 'variant': if (v.hook.text && !v.hook.variants.includes(v.hook.text)) v.hook.variants.push(v.hook.text); touch('hook'); renderPanel(); break;
    case 'pick': {
      const i = +b.dataset.i;
      if (e.shiftKey && selWord != null && STEP === 'effects') selEnd = i; else { selWord = i; selEnd = null; }
      $('#vid').currentTime = P.edl.words[Math.min(selWord, selEnd ?? selWord)].start; renderPanel(); break;
    }
    case 'pick-line': selWord = +b.dataset.a; selEnd = +b.dataset.z; $('#vid').currentTime = P.edl.words[selWord].start; renderPanel(); break;
    case 'put-effect': {
      const ws = selWords(), w = ws[0], eff = effectById(b.dataset.id); if (!w) return;
      if (eff.id === 'word-image-pop') {
        const sel = b.parentElement.querySelector('[data-img]');
        if (!sel) { alert('Add photos in the Footage step first.'); return; }
        v.overlays.push({ id: 'o' + Math.random().toString(16).slice(2, 7), word_i: w.i, at: w.start, image: sel.value, hold: 1.6, x: 'right', y: 'upper', tilt: -3, scale: 0.42, status: 'kept', why: 'placed by you' });
      } else v.effects.push({ id: 'e' + Math.random().toString(16).slice(2, 7), effect: eff.id, word_i: w.i, word_end_i: ws[ws.length - 1].i, word: selText(), at: w.start, status: 'kept', params: {}, note: '' });
      touch('effects'); renderPanel(); break;
    }
    case 'status': {
      const list = b.dataset.kind === 'effect' ? v.effects : b.dataset.kind === 'image' ? v.overlays : v.sfx;
      list.find(x => x.id === b.dataset.id).status = b.dataset.to; touch(b.dataset.kind === 'sound' ? 'sound' : 'effects'); renderPanel(); break;
    }
    case 'change': {
      const what = prompt('What should change? Claude will do it.'); if (!what) return;
      const list = b.dataset.kind === 'effect' ? v.effects : b.dataset.kind === 'image' ? v.overlays : v.sfx;
      const x = list.find(y => y.id === b.dataset.id); x.status = 'change'; x.note = what;
      await ask(`${b.dataset.kind} ${x.id} at ${fmt(x.at)}: ${what}`, STEP); break;
    }
    case 'font': if (e.target.closest('[data-act="titlefont"]')) return; v.text.font = b.dataset.f; touch('text'); renderPanel(); break;
    case 'titlefont': v.text.title_font = b.dataset.f; touch('text'); renderPanel(); break;
    case 'palette': { const p = lib('looks').palettes.find(x => x.id === b.dataset.id); Object.assign(v.text, { color: p.text, highlight: p.highlight, outline: p.outline, box_color: p.box_color, title_color: p.text }); touch('text'); renderPanel(); break; }
    case 'box': v.text.box = b.dataset.id; touch('text'); renderPanel(); break;
    case 'reset-place': { if (b.dataset.k === 'cap') delete v.text.cap_pos; else { delete v.text.title_pos; delete v.text.title_size; } touch('text'); drawTextBoxes(); renderPanel(); break; }
    case 'anim': v.text.anim = b.dataset.id; if (b.dataset.id === 'punch') v.text.words_per_line = 1; touch('text'); renderPanel(); break;
    case 'grade': v.grade = b.dataset.id; touch('style'); renderPanel(); break;
    case 'palette-from-video': {
      const c = paletteFromFrame(); if (!c) { toast('Pause on a frame first'); return; }
      Object.assign(v.text, c); touch('text'); renderPanel(); toast('Colours taken from this frame'); break;
    }
    case 'export-nle': {
      clearTimeout(saveTimer); if (!(await putP())) return;
      const r = await api(`/api/projects/${P.id}/export-nle`, { method: 'POST', body: JSON.stringify({ version: v.id }) });
      P = await api(`/api/projects/${P.id}`); LAST = JSON.stringify(P); renderPanel(); toast('Files for other editors are ready'); break;
    }
    case 'play-sfx': if (audio) audio.pause(); audio = new Audio('/lib/sfx/' + encodeURIComponent(b.dataset.f)); audio.play(); break;
    case 'put-sfx': {
      const s = lib('sfx').find(x => x.id === b.dataset.id), w = P.edl.words[selWord];
      v.sfx.push({ id: 's' + Math.random().toString(16).slice(2, 7), file: s.file, name: s.name, word_i: w.i, at: w.start, volume: 0.3, status: 'kept' });
      touch('sound'); renderPanel(); break;
    }
    case 'rule': {
      const pick = cat => lib('sfx').find(x => x.category === cat);
      const add = (s, wi, at) => { if (!v.sfx.some(x => x.word_i === wi && x.file === s.file)) v.sfx.push({ id: 's' + Math.random().toString(16).slice(2, 7), file: s.file, name: s.name, word_i: wi, at, volume: 0.45, status: 'proposed' }); };
      if (b.dataset.rule === 'images') v.overlays.filter(o => o.status !== 'removed').forEach(o => add(pick('whoosh'), o.word_i, Math.max(0, o.at - 0.15)));
      if (b.dataset.rule === 'effects') v.effects.filter(o => o.status !== 'removed').forEach(o => add(pick('pop'), o.word_i, o.at));
      if (b.dataset.rule === 'hook' && P.edl) {
        const r = keepRanges(), kept = P.edl.words.filter(w => !w.cut), w = kept.find(x => (mapTime(x.start, r) ?? 0) >= (v.hook.duration || 2.6)) || kept[0];
        if (w) add(lib('sfx').find(x => x.category === 'sparkle'), w.i, w.start);
      }
      touch('sound'); renderPanel(); break;
    }
    case 'split-stories': {
      const bs = beats(), out = []; let cur = null;
      for (const bt of bs) {
        if (!cur) cur = { from: bt.start, to: bt.end };
        else if (bt.end - cur.from <= 15) cur.to = bt.end;
        else { out.push(cur); cur = { from: bt.start, to: bt.end }; }
      }
      if (cur) out.push(cur);
      v.outputs.stories = out.map(s => ({ from: +s.from.toFixed(2), to: +Math.min(s.to, s.from + 15).toFixed(2) })); touch('outputs'); renderPanel(); break;
    }
    case 'draft-carousel': {
      const bs = beats();
      v.outputs.carousel.slides = [{ t: bs[0]?.src ?? 0, text: v.hook.text || bs[0]?.text || '' }, ...bs.slice(v.hook.text ? 0 : 1, 9).map(bt => ({ t: bt.src + 0.3, text: bt.text }))].slice(0, 10);
      touch('outputs'); renderPanel(); break;
    }
    case 'drop-slide': v.outputs.carousel.slides.splice(+b.dataset.k, 1); touch('outputs'); renderPanel(); break;
    case 'beat': { v.beats = v.beats || {}; const k = b.dataset.k, cur = v.beats[k] || {}; v.beats[k] = { ...cur, state: cur.state === b.dataset.to ? null : b.dataset.to }; touch('storyboard'); renderPanel(); break; }
    case 'render': {
      clearTimeout(saveTimer); if (!(await putP())) return;
      b.disabled = true; b.textContent = 'Rendering…';
      await runJob(api(`/api/projects/${P.id}/render`, { method: 'POST', body: JSON.stringify({ version: v.id, fmt: 'reel', preview: !!b.dataset.preview }) }), 'Rendering');
      renderPanel(); break;
    }
    case 'vibe': {
      v.music_vibe = $('#vibe').value.trim(); touch('style');
      await styleEdit(v.style_id);
      const vv = V();
      if (vv.music_vibe && /ask Claude/.test(vv.music?.why || '')) await ask(`Find a song for this video, vibe: “${vv.music_vibe}”. No track in the engine's music library fits; add one (licence that allows posting) to library/music.json with vibe tags, then make the style edit again.`, 'style', 'music');
      break;
    }
    case 'brand-kit': {
      P.brand_url = $('#brandurl').value.trim();
      clearTimeout(saveTimer); if (!(await putP())) return;
      await lexiconPrep(api(`/api/projects/${P.id}/brand`, { method: 'POST', body: JSON.stringify({ version: v.id, url: P.brand_url }) }));
      break;
    }
    case 'find-clips': {
      clearTimeout(saveTimer); if (!(await putP())) return;
      await lexiconPrep(api(`/api/projects/${P.id}/brand`, { method: 'POST', body: JSON.stringify({ version: v.id, url: P.brand_url || '' }) }));
      break;
    }
    case 'pexels-key2': {
      const key = $('#pexelskey2').value.trim(); if (!key) return;
      const r = await fetch('/api/settings', { method: 'POST', body: JSON.stringify({ pexels_key: key }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || !j.pexels) { toast('That key did not work on Pexels'); return; }
      SETTINGS = j; toast('Pexels key saved'); renderPanel(); break;
    }
    case 'giphy-key': {
      const key = $('#giphykey').value.trim(); if (!key) return;
      const r = await fetch('/api/settings', { method: 'POST', body: JSON.stringify({ giphy_key: key }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || !j.giphy) { toast('That key did not work on GIPHY'); return; }
      SETTINGS = j; toast('GIPHY key saved'); MEMES = null; renderPanel(); break;
    }
    case 'memes-find': {
      b.disabled = true; b.textContent = 'Reading your phrases…';
      clearTimeout(saveTimer); if (!(await putP())) return;
      const j = await api(`/api/projects/${P.id}/memes`).catch(e => ({ error: e.message }));
      if (j.error) { toast(j.error); renderPanel(); break; }
      MEMES = j.moments; if (!MEMELIB) MEMELIB = await api('/api/memes/library').catch(() => null);
      renderPanel(); break;
    }
    case 'meme-pick': case 'meme-libpick': {
      const lib = act === 'meme-libpick', m = lib ? null : MEMES[+b.dataset.k], it = lib ? MEMELIB.items[+b.dataset.j] : m.items[+b.dataset.j];
      const vid = $('#vid'), at = lib ? (vid ? vid.currentTime : 0) : m.start;
      const words = P.edl?.words || [], w = lib ? words.reduce((a, x) => Math.abs(x.start - at) < Math.abs(a.start - at) ? x : a, words[0]) : null;
      const hold = lib ? 1.6 : Math.max(1.2, Math.min(2.5, m.end - m.start));
      clearTimeout(saveTimer); if (!(await putP())) return;
      b.classList.add('busy');
      const r = await api(`/api/projects/${P.id}/memes-place`, { method: 'POST', body: JSON.stringify({ version: v.id, item: it, at, word_i: lib ? w?.i : m.word_i, phrase: lib ? (w?.text || '') : m.text, hold }) }).catch(e => ({ error: e.message }));
      if (r.error) { toast(r.error); b.classList.remove('busy'); break; }
      P = r.project; LAST = JSON.stringify(P);
      if (!lib) P.versions.find(x => x.id === v.id).overlays.forEach(o => { if (o.kind === 'meme' && o.by === 'memes' && Math.abs(o.at - at) < 0.05 && o.id !== r.overlay.id) o.status = 'removed'; });
      IMAGES = await api(`/api/projects/${P.id}/images`).catch(() => IMAGES);
      toast(`Meme on ${fmt(at)} · see it in the preview and Trim & view`); renderPanel(); renderHead(); break;
    }
    case 'meme-more': case 'meme-q': {
      const m = MEMES[+b.dataset.k], q = act === 'meme-q' ? ($(`[data-memeq="${b.dataset.k}"]`)?.value || '').trim() : m.query;
      if (!q) { toast('Type what to search for'); break; }
      b.disabled = true;
      const j = await api(`/api/memes/library?q=${encodeURIComponent(q)}&offset=${act === 'meme-more' ? m.offset : 0}`).catch(e => ({ error: e.message, items: [] }));
      if (act === 'meme-more') { m.items = [...m.items, ...j.items]; m.offset += 12; } else { m.items = j.items; m.query = q; m.offset = 12; m.terms = [q]; }
      if (j.error) m.error = j.error;
      renderPanel(); break;
    }
    case 'meme-none': {
      const m = MEMES[+b.dataset.k];
      v.overlays.forEach(o => { if (o.kind === 'meme' && Math.abs(o.at - m.start) < 0.05) o.status = 'removed'; });
      MEMES.splice(+b.dataset.k, 1); save(); renderPanel(); break;
    }
    case 'meme-cat': case 'meme-folder': case 'meme-libsearch': {
      const q = act === 'meme-libsearch' ? ($('#memelibq')?.value || '').trim() : b.dataset.id;
      if (!q) { toast('Type what to search for'); break; }
      if (!MEMELIB) MEMELIB = await api('/api/memes/library').catch(() => ({}));
      const j = await api(`/api/memes/library?${act === 'meme-folder' ? 'folder' : 'q'}=${encodeURIComponent(q)}`).catch(e => ({ error: e.message, items: [] }));
      MEMELIB.items = j.items; MEMELIB.error = j.error;
      MEMELIB.label = act === 'meme-cat' ? (MEMELIB.cats.find(c => c.id === q)?.name || q) : q;
      renderPanel(); break;
    }
    case 'meme-pin': {
      const url = ($('#pinurl')?.value || '').trim(); if (!url) { toast('Paste a Pinterest pin link'); break; }
      b.disabled = true; b.textContent = 'Getting the pin…';
      const r = await fetch('/api/memes/pin', { method: 'POST', body: JSON.stringify({ url }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) { toast(j.error || 'Could not get that pin'); renderPanel(); break; }
      if (!MEMELIB) MEMELIB = await api('/api/memes/library').catch(() => ({}));
      MEMELIB.items = [j.item, ...(MEMELIB.label === 'Din engine' ? MEMELIB.items || [] : [])]; MEMELIB.label = 'Din engine';
      toast('Pin added to your library (folder “Din engine”). Pause where you want it and click it.'); renderPanel(); break;
    }
    case 'stock-find': case 'stock-search': {
      const q = act === 'stock-search' ? ($('#stockq')?.value || '').trim() : '';
      if (act === 'stock-search' && !q) { toast('Type what to search for'); break; }
      clearTimeout(saveTimer); if (!(await putP())) return;
      b.disabled = true; b.textContent = 'Searching Pexels…';
      const r = await fetch(`/api/projects/${P.id}/stock-find`, { method: 'POST', body: JSON.stringify({ version: v.id, query: q }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) { toast(j.error || 'Pexels search failed'); renderPanel(); break; }
      STOCK = act === 'stock-search' ? [...j.words, ...(STOCK || []).filter(x => x.word_i != null)] : j.words; renderPanel(); break;
    }
    case 'stock-pick': {
      const row = STOCK[+b.dataset.k], it = row.items[+b.dataset.j];
      const wi = row.word_i != null ? row.word_i : selWord;
      if (wi == null) { toast('Click the word it belongs to first (word list above), then pick again'); break; }
      clearTimeout(saveTimer); if (!(await putP())) return;
      const res = await runJob(api(`/api/projects/${P.id}/stock-place`, { method: 'POST', body: JSON.stringify({ version: v.id, word_i: wi, item: it }) }), it.kind === 'video' ? 'Adding the video' : 'Adding the photo');
      if (res) toast(`${it.kind === 'video' ? 'Video' : 'Photo'} on “${P.edl.words[wi].text}” · see it in On screen and Trim & view`);
      IMAGES = await api(`/api/projects/${P.id}/images`).catch(() => IMAGES); renderPanel(); renderHead(); break;
    }
    case 'pexels-key': {
      const key = $('#pexelskey').value.trim(); if (!key) return;
      const r = await fetch('/api/settings', { method: 'POST', body: JSON.stringify({ pexels_key: key }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || !j.pexels) { toast('That key did not work on Pexels'); return; }
      SETTINGS = j; toast('Pexels key saved');
      clearTimeout(saveTimer); if (!(await putP())) return;
      await lexiconPrep(api(`/api/projects/${P.id}/brand`, { method: 'POST', body: JSON.stringify({ version: v.id, url: P.brand_url || '' }) }));
      break;
    }
    case 'img-word': {   // put a photo on the word / phrase Alina typed (24 Nov 2026)
      const im = IMAGES[+b.dataset.k], phrase = ($(`[data-imgphrase="${b.dataset.k}"]`)?.value || '').trim();
      if (!im || !phrase) { toast('Type the word or phrase first'); break; }
      const norm = x => x.toLowerCase().replace(/[^\p{L}\p{N}']+/gu, '');
      const want = phrase.split(/\s+/).map(norm).filter(Boolean), ws = P.edl.words.filter(w => !w.cut);
      let hit = -1;
      for (let k = 0; k + want.length <= ws.length && hit < 0; k++) if (want.every((x, j) => norm(ws[k + j].text) === x)) hit = k;
      if (hit < 0) for (let k = 0; k < ws.length && hit < 0; k++) if (norm(ws[k].text).startsWith(want[0])) hit = k;   // plural / -ing forms
      if (hit < 0) { alert(`“${phrase}” isn't in what you say in this video (only words you didn't cut count). Check the spelling against the Cut step.`); break; }
      const first = ws[hit], last = ws[Math.min(ws.length - 1, hit + want.length - 1)];
      const hold = Math.max(1.6, Math.min(4, (last.end - first.start) + .8));
      let ov = v.overlays.find(o => String(o.image).split('/').pop() === im.name);
      if (!ov) { ov = { id: 'o' + Math.random().toString(16).slice(2, 7), image: im.path, x: 'right', y: 'upper', tilt: -3, scale: 0.42 }; v.overlays.push(ov); }
      Object.assign(ov, { word_i: first.i, at: first.start, hold, phrase, status: 'kept', why: `you: on “${phrase}”` });
      touch('footage', 'effects'); toast(`${im.name} → “${phrase}” at ${fmt(first.start)}`); renderPanel(); break;
    }
    case 'img-unplace': {
      const im = IMAGES[+b.dataset.k];
      v.overlays.filter(o => String(o.image).split('/').pop() === im.name).forEach(o => { o.status = 'removed'; });
      touch('footage', 'effects'); renderPanel(); break;
    }
    case 'music-toggle': v.music.status = v.music.status === 'removed' ? 'proposed' : 'removed'; touch('sound'); renderPanel(); break;
    case 'edit-now': await editNow(); break;
    case 'quick-export': {
      if ((DIRECTED.includes(v.style_id) && v.style_edit?.style !== v.style_id) || (AUTO_MEMES.includes(v.style_id) && !v.overlays.some(o => o.kind === 'meme' && o.status !== 'removed'))) await styleEdit(v.style_id);
      clearTimeout(saveTimer); if (!(await putP())) return;
      b.disabled = true; b.textContent = 'Exporting…';
      const r = await runJob(api(`/api/projects/${P.id}/render`, { method: 'POST', body: JSON.stringify({ version: v.id, fmt: 'reel', preview: false, quick: true }) }), 'Exporting');
      if (r) { toast('Exported: it is in Check & export'); go('export'); } else renderPanel();
      break;
    }
    case 'carousel': {
      clearTimeout(saveTimer); if (!(await putP())) return;
      const r = await runJob(api(`/api/projects/${P.id}/carousel`, { method: 'POST', body: JSON.stringify({ version: v.id }) }), 'Carousel frames');
      if (r) toast(`${r.frames.length} frames saved in the project's renders folder`); break;
    }
    case 'delete-render': {
      const r = v.renders.find(x => x.file === b.dataset.file);
      if (!confirm(`Delete this ${r?.preview ? 'preview' : 'render'} (${fmt(r?.duration || 0)}, ${r?.at.replace('T', ' ') || ''})?\nThe video file goes to your Mac's Trash, so you can still get it back from there.`)) return;
      clearTimeout(saveTimer); if (!(await putP())) return;
      P = await api(`/api/projects/${P.id}/delete-render`, { method: 'POST', body: JSON.stringify({ version: v.id, file: b.dataset.file }) });
      LAST = JSON.stringify(P); renderPanel(); toast('Deleted (in the Trash)'); break;
    }
    case 'ask': { const t = $('#ask').value.trim() || (PENDING.length ? `Attached: ${PENDING.join(', ')}` : ''); if (t) await ask(t, STEP); break; }
  }
});
/* colours from the frame on screen: the most common bright and dark colours become the caption colours */
function paletteFromFrame() {
  const vid = $('#vid'); if (!vid || !vid.videoWidth) return null;
  const c = document.createElement('canvas'); c.width = 64; c.height = 112;
  const x = c.getContext('2d'); x.drawImage(vid, 0, 0, 64, 112);
  const d = x.getImageData(0, 0, 64, 112).data, bins = new Map();
  for (let i = 0; i < d.length; i += 4) {
    const k = ((d[i] >> 5) << 6) | ((d[i + 1] >> 5) << 3) | (d[i + 2] >> 5);
    const b = bins.get(k) || [0, 0, 0, 0]; b[0] += d[i]; b[1] += d[i + 1]; b[2] += d[i + 2]; b[3]++; bins.set(k, b);
  }
  const cols = [...bins.values()].sort((a, b) => b[3] - a[3]).slice(0, 12).map(b => [b[0] / b[3], b[1] / b[3], b[2] / b[3]]);
  const lum = c => .2126 * c[0] + .7152 * c[1] + .0722 * c[2], sat = c => Math.max(...c) - Math.min(...c);
  const hex = c => '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
  const vivid = cols.slice().sort((a, b) => sat(b) - sat(a))[0], dark = cols.slice().sort((a, b) => lum(a) - lum(b))[0];
  const boost = c => { const m = Math.max(...c); return c.map(v => Math.min(255, v * (230 / Math.max(1, m)))); };
  return { color: '#FFFFFF', highlight: hex(boost(vivid)), outline: hex(dark.map(v => v * .5)), box_color: hex(dark), title_color: '#FFFFFF' };
}
/* change the text of one word: the timing stays, only what the captions and exports say changes */
function editWord(btn, w) {
  const inp = document.createElement('input');
  inp.className = 'wedit'; inp.value = w.text; inp.size = Math.max(3, w.text.length + 1);
  btn.replaceWith(inp); inp.focus(); inp.select();
  let done = false;
  const finish = save => {
    if (done) return; done = true;
    const t = inp.value.trim();
    if (save && t && t !== w.text) {
      if (w.orig == null) w.orig = w.text;
      w.text = t;
      if (w.text === w.orig) delete w.orig;   // typed it back: no longer an edit
      touch('cut'); toast(`“${w.orig ?? t}” → “${t}”`);
    }
    renderPanel(); renderHead();
  };
  inp.addEventListener('input', () => { inp.size = Math.max(3, inp.value.length + 1); });
  inp.addEventListener('keydown', ev => { if (ev.key === 'Enter') { ev.preventDefault(); finish(true); } if (ev.key === 'Escape') finish(false); });
  inp.addEventListener('blur', () => finish(true));
}
async function ask(text, step, kind) {
  clearTimeout(saveTimer); if (!(await putP())) return;
  await api(`/api/projects/${P.id}/request`, { method: 'POST', body: JSON.stringify({ text, step, version: P.current, kind, files: PENDING }) });
  PENDING = [];
  P = await api(`/api/projects/${P.id}`); LAST = JSON.stringify(P); toast('Saved for Claude'); renderPanel();
}

(async () => { try { PLAN = await api('/api/plan'); } catch (e) { /* no plan yet */ } route(); })();
