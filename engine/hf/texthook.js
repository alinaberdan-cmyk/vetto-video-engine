/* Helpers shared by the text-hook templates (17 Nov 2026). */
(function () {
  window.HK = {
    // the text: the field, else the words Alina selected
    text: (P, V) => String(P.text || V.word || 'your words here').replace(/[“”"]/g, '').trim(),
    words: s => s.split(/\s+/).filter(Boolean),
    // split words into n lines with about the same number of letters
    lines(words, n) {
      n = Math.max(1, Math.min(n, words.length));
      const total = words.join(' ').length, out = [[]]; let acc = 0;
      words.forEach((w, i) => {
        const cur = out[out.length - 1];
        if (cur.length && out.length < n && acc + w.length / 2 > total * out.length / n) out.push([]);
        out[out.length - 1].push(w); acc += w.length + 1;
      });
      return out.map(l => l.join(' '));
    },
    // shrink an element's font until it is no wider than maxW
    fit(el, maxW, base) { el.style.fontSize = base + 'px'; const w = el.getBoundingClientRect().width; if (w > maxW) el.style.fontSize = (base * maxW / w) + 'px'; return el; },
    face: V => V.face || [324, 346, 432, 422],
    hands: V => { for (const t of V.track || []) if (t.hands && t.hands.length) return t.hands; return []; },
    // when each word is said (relative), else an even stagger
    at(V, i, step) { const w = (V.words || [])[i]; return w && w.t != null && w.t < 2.4 ? Math.max(.05, w.t) : .08 + i * (step || .22); },
    esc: s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])),
  };
})();
/* Meme Chaos helpers (18 Nov 2026). Motion that can't be a single tween (shake, wave, beams) is written as one
   tl.set per frame, so a seek always lands on the right picture (no onUpdate callbacks, which seeks suppress). */
(function () {
  window.FX = {
    // where assets live: the render's project folder, or the editor's preview route
    A: V => (V.preview ? '/prev/a/' : 'assets/'),
    // call fn(t) for every frame in [t0, t1]; it returns [[target, props], …] to set at t
    frames(tl, t0, t1, fn, fps) {
      fps = fps || 30;
      for (let k = Math.round(t0 * fps); k <= Math.round(t1 * fps); k++) {
        const t = k / fps, r = fn(t) || [];
        r.forEach(([el, props]) => tl.set(el, props, t));
      }
    },
    // a keyed green-screen clip (engine/hf/fx/memes/<name>/fNNN.webp): one <img> per frame inside `box`,
    // shown in turn from t0; loops until t1 when loop is true. Returns the clip length in seconds.
    meme(tl, box, V, name, t0, t1, loop) {
      const m = (V.memes || {})[name]; if (!m) return 0;
      const imgs = [];
      for (let i = 0; i < m.n; i++) {
        const im = document.createElement('img');
        im.src = FX.A(V) + 'fx/memes/' + name + '/f' + String(i).padStart(3, '0') + '.webp';
        im.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;visibility:hidden';
        box.appendChild(im); imgs.push(im);
      }
      const len = m.n / m.fps, end = t1 == null ? t0 + len : t1;
      let prev = null;
      for (let t = t0, k = 0; t < end - 1e-6; t += 1 / m.fps, k++) {
        if (!loop && k >= m.n) break;
        const cur = imgs[k % m.n];
        if (prev && prev !== cur) tl.set(prev, { visibility: 'hidden' }, t);
        tl.set(cur, { visibility: 'visible' }, t); prev = cur;
      }
      if (prev) tl.set(prev, { visibility: 'hidden' }, Math.min(end, t0 + (loop ? 1e9 : len)));
      return len;
    },
    // a 4-point sparkle (SVG) of size s px
    sparkle(s, color) {
      const d = document.createElement('div'), c = color || '#fff';
      d.style.cssText = `position:absolute;width:${s * 2.6}px;height:${s * 2.6}px;margin:${-s * 1.3}px 0 0 ${-s * 1.3}px;filter:drop-shadow(0 0 ${s * .3}px rgba(255,245,190,.9))`;
      const r = s * 1.3, k = s * .18;
      d.innerHTML = `<svg viewBox="0 0 ${s * 2.6} ${s * 2.6}" width="100%" height="100%"><polygon fill="${c}" points="${r},${r - s} ${r + k},${r - k} ${r + s},${r} ${r + k},${r + k} ${r},${r + s} ${r - k},${r + k} ${r - s},${r} ${r - k},${r - k}"/></svg>`;
      return d;
    },
    num: (v, d) => { const x = parseFloat(v); return isNaN(x) ? d : x; },
  };
})();
