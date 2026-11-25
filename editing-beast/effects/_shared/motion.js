/* Shared motion curves for every effect template (loaded before the template's own script).
   Values: emilkowalski/skills (MIT) "animate" + mengto/skills web-design (MIT). Rules used in the templates:
   entrances ease out, things moving on screen ease in-out, exits are ~75 % of the entrance and never ease in
   (except a deliberate acceleration, like flying into a letter), never scale from 0, overshoot only on sticky things. */
(function () {
  function bezier(x1, y1, x2, y2) {
    // cubic-bezier(x1,y1,x2,y2) as a GSAP ease: solve x(t) = p by Newton, return y(t)
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = t => ((ax * t + bx) * t + cx) * t, Y = t => ((ay * t + by) * t + cy) * t, dX = t => (3 * ax * t + 2 * bx) * t + cx;
    return p => {
      if (p <= 0) return 0; if (p >= 1) return 1;
      let t = p;
      for (let i = 0; i < 8; i++) { const d = dX(t); if (Math.abs(d) < 1e-6) break; t -= (X(t) - p) / d; }
      t = Math.min(1, Math.max(0, t));
      return Y(t);
    };
  }
  window.EASE = {
    out: bezier(0.23, 1, 0.32, 1),        // entrances
    inOut: bezier(0.77, 0, 0.175, 1),     // moving on screen, exits
    drawer: bezier(0.32, 0.72, 0, 1),     // panels and cards sliding in
    rise: bezier(0.16, 1, 0.3, 1),        // words rising out of a mask
  };
  // staggers shrink as a group goes on (never uniform): 0, 80, 140, 180, 210 ms …
  window.STAGGER = (i, first = 0.08) => { let t = 0, g = first; for (let k = 0; k < i; k++) { t += g; g *= 0.72; } return t; };
})();
