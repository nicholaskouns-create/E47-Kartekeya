/* 02 FOLD · Levinthal's paradox, resolved by spectral depth
   E47-Kartekeya · The Mathematical City
   Every number on this page is computed in the browser from the formulas shown.
   No network data. Measured folding times are cited constants (E3). */
(function () {
  'use strict';

  // ───────────────────────── constants ─────────────────────────
  const TAU0 = 1e-13;                       // s · elementary step (research/levinthal-recursive-contraction.md)
  const YEAR_S = 365.25 * 86400;
  const UNIVERSE_S = 13.8e9 * YEAR_S;       // age of the universe
  const C = {
    cyan: '#6edfd4', mint: '#c1e8ce', bronze: '#bc9c6c', hot: '#d87e74',
    fg: '#edf2ef', muted: '#98a6a8', faint: '#657478', line: '#243138', bg: '#090b0d'
  };
  const MONO = '"IBM Plex Mono", "Noto Sans Math", "DejaVu Sans Mono", ui-monospace, monospace';
  const SANS = '"IBM Plex Sans", "Noto Sans Math", system-ui, sans-serif';
  const MATH = '"STIX Two Text", "Noto Sans Math", "Cambria Math", "Times New Roman", serif';

  const PRESETS = [
    { id: 'cln025', name: 'CLN025', N: 10, seq: 'YYDPETGTWY',
      fold: { t: 1.0e-7, lo: 0.82e-7, hi: 1.24e-7, label: '≈ 100 ns', ref: 'Davis et al., JACS 134, 14476 (2012)' } },
    { id: 'trpcage', name: 'Trp-cage', N: 20, seq: 'NLYIQWLKDGGPSSGRPPPS',
      fold: { t: 4e-6, lo: 4e-6, hi: 4e-6, label: '≈ 4 µs', ref: 'Qiu et al., JACS 124, 12952 (2002)' } },
    { id: 'villin', name: 'Villin HP-35', N: 35, seq: 'LSDEDFKAVFGMTRSAFANLPLWKQQNLKKEKGLF',
      fold: { t: Math.sqrt(1e-6 * 5e-6), lo: 1e-6, hi: 5e-6, label: 'a few µs', ref: 'Kubelka et al., PNAS 105, 18655 (2008)' } },
    { id: 'ala14', name: 'Ala-14', N: 14, seq: 'AAAAAAAAAAAAAA', fold: null },
    { id: 'n100', name: 'Levinthal · N = 100', N: 100, seq: null, fold: null }
  ];

  // ───────────────────────── formatting ─────────────────────────
  const SUP = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻' };
  const sup = (s) => String(s).replace(/[0-9-]/g, (c) => SUP[c]);
  const int = (v) => Math.round(v).toLocaleString('en-US');

  function sci(log10v, digits = 2) {
    if (!Number.isFinite(log10v)) return '∞';
    let e = Math.floor(log10v);
    let m = Math.pow(10, log10v - e);
    let ms = m.toFixed(digits - 1);
    if (parseFloat(ms) >= 10) { e += 1; ms = (m / 10).toFixed(digits - 1); }
    if (e >= 0 && e <= 5) return int(Math.pow(10, log10v));
    return `${ms} × 10${sup(e)}`;
  }

  function small(v) {
    if (v >= 100) return Math.round(v).toString();
    if (v >= 10) return v.toFixed(0);
    if (v >= 1) return v.toFixed(1);
    return v.toPrecision(2);
  }

  function duration(log10s) {
    const s = Math.pow(10, log10s);
    if (log10s < -9) return `${small(s * 1e12)} ps`;
    if (log10s < -6) return `${small(s * 1e9)} ns`;
    if (log10s < -3) return `${small(s * 1e6)} µs`;
    if (log10s < 0) return `${small(s * 1e3)} ms`;
    if (s < 120) return `${small(s)} s`;
    if (s < 2 * 3600) return `${small(s / 60)} min`;
    if (s < 3 * 86400) return `${small(s / 3600)} h`;
    if (s < 2 * YEAR_S) return `${small(s / 86400)} days`;
    const ly = log10s - Math.log10(YEAR_S);
    if (ly < 6) return `${int(Math.pow(10, ly))} years`;
    return `${sci(ly)} years`;
  }

  // ───────────────────────── spectral numerics ─────────────────────────
  // Householder tridiagonalisation + implicit QL, eigenvalues only (symmetric input).
  function tred2(a, n, d, e) {
    for (let i = n - 1; i > 0; i--) {
      const l = i - 1;
      let h = 0;
      if (l > 0) {
        let scale = 0;
        for (let k = 0; k <= l; k++) scale += Math.abs(a[i][k]);
        if (scale === 0) {
          e[i] = a[i][l];
        } else {
          for (let k = 0; k <= l; k++) { a[i][k] /= scale; h += a[i][k] * a[i][k]; }
          let f = a[i][l];
          let g = f >= 0 ? -Math.sqrt(h) : Math.sqrt(h);
          e[i] = scale * g;
          h -= f * g;
          a[i][l] = f - g;
          f = 0;
          for (let j = 0; j <= l; j++) {
            g = 0;
            for (let k = 0; k <= j; k++) g += a[j][k] * a[i][k];
            for (let k = j + 1; k <= l; k++) g += a[k][j] * a[i][k];
            e[j] = g / h;
            f += e[j] * a[i][j];
          }
          const hh = f / (h + h);
          for (let j = 0; j <= l; j++) {
            f = a[i][j];
            e[j] = g = e[j] - hh * f;
            for (let k = 0; k <= j; k++) a[j][k] -= f * e[k] + g * a[i][k];
          }
        }
      } else {
        e[i] = a[i][l];
      }
      d[i] = h;
    }
    e[0] = 0;
    for (let i = 0; i < n; i++) d[i] = a[i][i];
  }

  function tqli(d, e, n) {
    for (let i = 1; i < n; i++) e[i - 1] = e[i];
    if (n > 0) e[n - 1] = 0;
    for (let l = 0; l < n; l++) {
      let iter = 0;
      let m;
      do {
        for (m = l; m < n - 1; m++) {
          const dd = Math.abs(d[m]) + Math.abs(d[m + 1]);
          if (Math.abs(e[m]) <= Number.EPSILON * dd) break;
        }
        if (m !== l) {
          if (iter++ === 80) throw new Error('tqli did not converge');
          let g = (d[l + 1] - d[l]) / (2 * e[l]);
          let r = Math.hypot(g, 1);
          g = d[m] - d[l] + e[l] / (g + (g >= 0 ? r : -r));
          let s = 1, c = 1, p = 0;
          let i;
          let underflow = false;
          for (i = m - 1; i >= l; i--) {
            let f = s * e[i];
            const b = c * e[i];
            e[i + 1] = r = Math.hypot(f, g);
            if (r === 0) { d[i + 1] -= p; e[m] = 0; underflow = true; break; }
            s = f / r; c = g / r;
            g = d[i + 1] - p;
            r = (d[i] - g) * s + 2 * c * b;
            p = s * r;
            d[i + 1] = g + p;
            g = c * r - b;
          }
          if (underflow) continue;
          d[l] -= p; e[l] = g; e[m] = 0;
        }
      } while (m !== l);
    }
  }

  function symEigenvalues(flat, n) {
    const a = [];
    for (let i = 0; i < n; i++) a.push(Float64Array.from(flat.subarray(i * n, (i + 1) * n)));
    const d = new Float64Array(n), e = new Float64Array(n);
    tred2(a, n, d, e);
    tqli(d, e, n);
    return Array.from(d).sort((x, y) => x - y);
  }

  // ───────────────────────── the convex funnel (2D Gō model) ─────────────────────────
  // Native: a compact β-meander on the square lattice (k strands of length s).
  function nativeFold(N) {
    const k = Math.max(2, Math.round(Math.sqrt(N / 2.5)));
    const s = Math.ceil(N / k);
    const P = new Float64Array(2 * N);
    for (let i = 0; i < N; i++) {
      const r = Math.floor(i / s), c = i % s;
      P[2 * i] = r % 2 === 0 ? c : s - 1 - c;
      P[2 * i + 1] = r;
    }
    return { P, k, s };
  }

  // Edges: backbone bonds, plus native contacts (lattice neighbours with |i − j| > 1).
  function goEdges(N, P, contacts) {
    const E = [];
    for (let i = 0; i < N - 1; i++) E.push(i, i + 1);
    let nContacts = 0;
    if (contacts) {
      const idx = new Map();
      for (let i = 0; i < N; i++) idx.set(P[2 * i] + ',' + P[2 * i + 1], i);
      for (let i = 0; i < N; i++) {
        for (const [dx, dy] of [[1, 0], [0, 1]]) {
          const j = idx.get((P[2 * i] + dx) + ',' + (P[2 * i + 1] + dy));
          if (j !== undefined && Math.abs(i - j) > 1) { E.push(Math.min(i, j), Math.max(i, j)); nContacts++; }
        }
      }
    }
    return { E: Int32Array.from(E), nContacts };
  }

  function laplacian(N, E) {
    const L = new Float64Array(N * N);
    for (let t = 0; t < E.length; t += 2) {
      const i = E[t], j = E[t + 1];
      L[i * N + i] += 1; L[j * N + j] += 1; L[i * N + j] -= 1; L[j * N + i] -= 1;
    }
    return L;
  }

  const goCache = new Map();
  function goModel(N, contacts) {
    const key = N + (contacts ? 'c' : 'b');
    if (goCache.has(key)) return goCache.get(key);
    const nat = nativeFold(N);
    const { E, nContacts } = goEdges(N, nat.P, contacts);
    const ev = symEigenvalues(laplacian(N, E), N);
    const model = { N, P: nat.P, k: nat.k, s: nat.s, E, nContacts, lam2: ev[1], lmax: ev[N - 1], R: ev[N - 1] / ev[1] };
    goCache.set(key, model);
    return model;
  }

  // Depth law: D(δ) = ⌈ln(1/δ) / ln(1/q∗)⌉, q∗ = (ℛ − 1)/(ℛ + 1).
  function depthFromR(R, delta) {
    if (R <= 1 + 1e-12) return 1;
    const lnInvQ = Math.log1p(2 / (R - 1));
    return Math.ceil(Math.log(1 / delta) / lnInvQ);
  }
  const qFromR = (R) => (R - 1) / (R + 1);

  // ───────────────────────── lumped Metropolis chain (exact MFPT) ─────────────────────────
  // N residues, b states each (1 native, b − 1 not); E = −ε·n with n native residues.
  // Energy depends on n only, so the single-residue Metropolis chain lumps exactly onto n.
  // u(n) = N − n, d(n) = n(b − 1)e^(−ε) per τ₀. Mean first-passage time 0 → N, in units of τ₀.
  const LNF = (() => { const t = [0]; for (let i = 1; i <= 2000; i++) t[i] = t[i - 1] + Math.log(i); return t; })();
  const lse = (x, y) => (x === -Infinity ? y : y === -Infinity ? x : Math.max(x, y) + Math.log1p(Math.exp(-Math.abs(x - y))));
  function mfptLog10(N, b, eps) {
    const a = eps - Math.log(b - 1);
    let cum = -Infinity, total = -Infinity;
    for (let m = 0; m < N; m++) {
      const lp = LNF[N] - LNF[m] - LNF[N - m] + m * a;
      cum = lse(cum, lp);
      total = lse(total, cum - lp - Math.log(N - m));
    }
    return total / Math.LN10;
  }

  // ───────────────────────── canvas helpers ─────────────────────────
  function fitCanvas(canvas, fixed) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = fixed ? fixed.w : canvas.getBoundingClientRect().width;
    const h = fixed ? fixed.h : canvas.getBoundingClientRect().height;
    const pw = Math.max(1, Math.round(w * dpr)), ph = Math.max(1, Math.round(h * dpr));
    if (canvas.width !== pw || canvas.height !== ph) { canvas.width = pw; canvas.height = ph; }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    return { ctx, w, h };
  }

  function rrect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // ───────────────────────── the depth ledger (hero + share card) ─────────────────────────
  function ledgerRows(preset, b, delta) {
    const N = preset.N;
    const go = goModel(N, true);
    const D = depthFromR(go.R, delta);
    const rows = [{
      key: 'blind', label: 'BLIND ENUMERATION', sub: `|Σ| = ${b}${sup(N)} configurations`,
      v: N * Math.log10(b), color: C.hot
    }];
    if (preset.fold) {
      rows.push({
        key: 'measured', label: 'MEASURED FOLDING', sub: `folding time ${preset.fold.label}, ÷ τ₀`,
        v: Math.log10(preset.fold.t / TAU0),
        lo: Math.log10(preset.fold.lo / TAU0), hi: Math.log10(preset.fold.hi / TAU0), color: C.mint
      });
    }
    rows.push({
      key: 'depth', label: 'SPECTRAL DEPTH', sub: `D(δ), convex funnel, ℛ = ${go.R.toFixed(1)}`,
      v: Math.log10(D), steps: D, color: C.cyan
    });
    return { rows, go, D };
  }

  function drawLedger(canvas, preset, opts = {}) {
    const b = opts.b || 9;
    const delta = opts.delta || 1e-6;
    const { ctx, w, h } = fitCanvas(canvas, opts.size);
    const { rows } = ledgerRows(preset, b, delta);
    const compact = w < 520;
    const padL = compact ? 14 : 20, padR = compact ? 14 : 24;
    const top = compact ? 46 : 56, bottom = compact ? 34 : 40;
    const plotW = w - padL - padR;
    const maxV = Math.max(...rows.map((r) => r.hi || r.v));
    const xMax = Math.max(10, Math.ceil((maxV + 1.5) / 5) * 5);
    const X = (v) => padL + (Math.max(0, v) / xMax) * plotW;

    // header
    ctx.fillStyle = C.muted;
    ctx.font = `500 ${compact ? 10 : 11}px ${MONO}`;
    ctx.textBaseline = 'alphabetic';
    const head = preset.seq ? `${preset.name.toUpperCase()} · N = ${preset.N}` : `${preset.name.toUpperCase()}`;
    ctx.fillText(head, padL, compact ? 18 : 22);
    ctx.fillStyle = C.faint;
    ctx.fillText(`log₁₀ elementary steps · τ₀ = 10⁻¹³ s`, padL, compact ? 32 : 38);

    // grid + ticks
    const step = xMax <= 20 ? 5 : xMax <= 60 ? 10 : 20;
    ctx.font = `400 ${compact ? 9 : 10}px ${MONO}`;
    for (let t = 0; t <= xMax; t += step) {
      const x = X(t);
      ctx.strokeStyle = 'rgba(36,49,56,.75)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x + 0.5, top - 8); ctx.lineTo(x + 0.5, h - bottom + 4); ctx.stroke();
      ctx.fillStyle = C.faint;
      const lab = `10${sup(t)}`;
      const tw = ctx.measureText(lab).width;
      ctx.fillText(lab, Math.min(Math.max(x - tw / 2, padL - 2), w - padR - tw + 4), h - bottom + 20);
    }

    // age-of-universe marker
    const uni = Math.log10(UNIVERSE_S / TAU0);
    if (uni < xMax) {
      const x = X(uni);
      ctx.save();
      ctx.setLineDash([3, 4]);
      ctx.strokeStyle = 'rgba(216,126,116,.55)';
      ctx.beginPath(); ctx.moveTo(x + 0.5, top - 10); ctx.lineTo(x + 0.5, h - bottom + 4); ctx.stroke();
      ctx.restore();
      ctx.fillStyle = 'rgba(216,126,116,.8)';
      ctx.font = `400 ${compact ? 8.5 : 9.5}px ${MONO}`;
      const t1 = 'age of universe';
      const tw = ctx.measureText(t1).width;
      ctx.fillText(t1, Math.min(x + 5, w - padR - tw), top - 12);
    }

    // rows
    const rowH = (h - top - bottom) / rows.length;
    rows.forEach((r, i) => {
      const y0 = top + i * rowH;
      const barY = y0 + rowH * 0.52, barH = Math.max(6, Math.min(14, rowH * 0.2));
      ctx.fillStyle = r.color;
      ctx.font = `600 ${compact ? 9.5 : 10.5}px ${MONO}`;
      ctx.fillText(r.label, padL, y0 + rowH * 0.3);
      const lw = ctx.measureText(r.label).width;
      ctx.font = `400 ${compact ? 9.5 : 11}px ${MONO}`;
      ctx.fillStyle = C.faint;
      const subW = ctx.measureText('  ' + r.sub).width;
      if (padL + lw + 4 + subW < w - padR) ctx.fillText('  ' + r.sub, padL + lw + 4, y0 + rowH * 0.3);
      // track
      ctx.fillStyle = 'rgba(36,49,56,.55)';
      rrect(ctx, padL, barY - barH / 2, plotW, barH, barH / 2); ctx.fill();
      // bar
      const xe = X(r.v);
      const grad = ctx.createLinearGradient(padL, 0, xe, 0);
      grad.addColorStop(0, r.color + '33');
      grad.addColorStop(1, r.color);
      ctx.fillStyle = grad;
      rrect(ctx, padL, barY - barH / 2, Math.max(barH, xe - padL), barH, barH / 2); ctx.fill();
      if (r.lo !== undefined && r.hi > r.lo + 1e-9) {
        ctx.strokeStyle = C.fg; ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(X(r.lo), barY - barH); ctx.lineTo(X(r.lo), barY + barH);
        ctx.moveTo(X(r.lo), barY); ctx.lineTo(X(r.hi), barY);
        ctx.moveTo(X(r.hi), barY - barH); ctx.lineTo(X(r.hi), barY + barH);
        ctx.stroke();
      }
      // value
      const val = r.key === 'depth' ? `${int(r.steps)} steps` : `${sci(r.v)} steps`;
      ctx.font = `600 ${compact ? 11 : 13}px ${MONO}`;
      const vw = ctx.measureText(val).width;
      let vx = xe + 10;
      if (vx + vw > w - padR + 6) vx = xe - vw - 10;
      const inside = vx < xe;
      ctx.fillStyle = inside ? C.bg : C.fg;
      if (inside) {
        ctx.fillStyle = 'rgba(9,11,13,.72)';
        rrect(ctx, vx - 5, barY - 10, vw + 10, 20, 6); ctx.fill();
        ctx.fillStyle = C.fg;
      }
      ctx.textBaseline = 'middle';
      ctx.fillText(val, vx, barY + 0.5);
      ctx.textBaseline = 'alphabetic';
    });
  }

  // ───────────────────────── public API (share card + tests) ─────────────────────────
  const API = { PRESETS, TAU0, UNIVERSE_S, goModel, depthFromR, qFromR, mfptLog10, symEigenvalues, nativeFold, ledgerRows, drawLedger, sci, duration };
  if (typeof window !== 'undefined') window.LEVINTHAL = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  if (typeof document === 'undefined' || !document.getElementById('ledger')) return;

  // ───────────────────────── page wiring ─────────────────────────
  const $ = (id) => document.getElementById(id);
  const state = {
    preset: PRESETS[1], N: 20, b: 9, delta: 1e-6, mode: 'L', contacts: true, eps: 2, seed: 47
  };

  function setPressed(groupSel, attr, value) {
    document.querySelectorAll(groupSel).forEach((btn) => btn.setAttribute('aria-pressed', String(btn.dataset[attr] === String(value))));
  }

  // ── hero ledger
  function renderLedger() {
    const p = state.preset.N === state.N ? state.preset : { id: 'custom', name: 'Custom chain', N: state.N, seq: null, fold: null };
    drawLedger($('ledgerCanvas'), p, { b: state.b, delta: 1e-6 });
    const { rows, go, D } = ledgerRows(p, state.b, 1e-6);
    const blind = rows.find((r) => r.key === 'blind');
    const meas = rows.find((r) => r.key === 'measured');
    $('seq').textContent = p.seq ? p.seq.split('').join(' ') : `${p.N} residues · no sequence (toy count)`;
    $('ledgerBlind').innerHTML = `${sci(blind.v)} steps <span>= ${duration(blind.v + Math.log10(TAU0))}</span>`;
    $('ledgerMeasured').innerHTML = meas
      ? `${sci(meas.v)} steps <span>· folding time ${p.fold.label} · ${p.fold.ref}</span>`
      : `<span>no cited measurement for this chain</span>`;
    $('ledgerDepth').innerHTML = `${int(D)} steps <span>= ${duration(Math.log10(D * TAU0))} · ℛ = ${go.R.toFixed(1)}, δ = 10⁻⁶</span>`;
    const gap = meas ? blind.v - meas.v : blind.v - Math.log10(D);
    $('ledgerGap').textContent = meas
      ? `Measured folding beats blind enumeration by ${gap.toFixed(1)} orders of magnitude.`
      : `Spectral depth beats blind enumeration by ${gap.toFixed(1)} orders of magnitude.`;
  }

  // ── §1 count
  function renderCount() {
    const L = state.N * Math.log10(state.b);
    $('countN').textContent = state.N;
    $('countB').textContent = state.b;
    $('countSigma').textContent = sci(L, 3);
    $('countTime').textContent = `${sci(L + Math.log10(TAU0), 3)} s`;
    $('countHuman').textContent = duration(L + Math.log10(TAU0));
    const ratio = L + Math.log10(TAU0) - Math.log10(UNIVERSE_S);
    $('countUniverse').textContent = `${sci(ratio, 2)} × the age of the universe`;
  }

  // ── §3 live fold
  const fold = { model: null, d: null, d0r: 1, n: 0, D: 0, R: 1, eps: 0, q: 0, hist: [], running: false, done: false, scale: 1, tmp1: null, tmp2: null, raf: 0, spf: 1 };

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function applyL(E, src, dst) {
    dst.fill(0);
    for (let t = 0; t < E.length; t += 2) {
      const i = E[t] * 2, j = E[t + 1] * 2;
      const dx = src[i] - src[j], dy = src[i + 1] - src[j + 1];
      dst[i] += dx; dst[i + 1] += dy; dst[j] -= dx; dst[j + 1] -= dy;
    }
  }

  function residual(d) {
    const N = d.length / 2;
    let mx = 0, my = 0;
    for (let i = 0; i < N; i++) { mx += d[2 * i]; my += d[2 * i + 1]; }
    mx /= N; my /= N;
    let s = 0;
    for (let i = 0; i < N; i++) { const a = d[2 * i] - mx, b = d[2 * i + 1] - my; s += a * a + b * b; }
    return Math.sqrt(s);
  }

  function resetFold() {
    cancelAnimationFrame(fold.raf);
    const N = state.N;
    const m = goModel(N, state.contacts);
    fold.model = m;
    fold.R = state.mode === 'L' ? m.R : m.R * m.R;
    const l2 = state.mode === 'L' ? m.lam2 : m.lam2 * m.lam2;
    const lm = state.mode === 'L' ? m.lmax : m.lmax * m.lmax;
    fold.eps = 2 / (lm + l2);
    fold.q = qFromR(fold.R);
    fold.D = depthFromR(fold.R, state.delta);
    // random coil with unit bonds, seeded
    const rnd = mulberry32(state.seed);
    const x = new Float64Array(2 * N);
    for (let i = 1; i < N; i++) {
      const th = rnd() * 2 * Math.PI;
      x[2 * i] = x[2 * i - 2] + Math.cos(th);
      x[2 * i + 1] = x[2 * i - 1] + Math.sin(th);
    }
    fold.d = new Float64Array(2 * N);
    for (let i = 0; i < 2 * N; i++) fold.d[i] = x[i] - m.P[i];
    fold.tmp1 = new Float64Array(2 * N);
    fold.tmp2 = new Float64Array(2 * N);
    fold.d0r = residual(fold.d) || 1;
    fold.n = 0; fold.hist = [[0, 0]]; fold.done = false; fold.running = false;
    fold.spf = Math.max(1, Math.ceil(fold.D / 280));
    // fixed drawing scale: fit both the native and the coil
    const ext = (arr) => {
      let mx = 0, my = 0;
      for (let i = 0; i < N; i++) { mx += arr[2 * i]; my += arr[2 * i + 1]; }
      mx /= N; my /= N;
      let r = 0;
      for (let i = 0; i < N; i++) r = Math.max(r, Math.abs(arr[2 * i] - mx), Math.abs(arr[2 * i + 1] - my));
      return r;
    };
    fold.extent = Math.max(ext(m.P), ext(x), 2) + 0.8;
    $('runBtn').textContent = 'Run Λ';
    renderFoldReadouts();
    drawFold();
    drawResidual();
  }

  function stepFold(k) {
    const m = fold.model, d = fold.d, t1 = fold.tmp1, t2 = fold.tmp2;
    for (let s = 0; s < k && !fold.done; s++) {
      applyL(m.E, d, t1);
      if (state.mode === 'L2') { applyL(m.E, t1, t2); for (let i = 0; i < d.length; i++) d[i] -= fold.eps * t2[i]; }
      else { for (let i = 0; i < d.length; i++) d[i] -= fold.eps * t1[i]; }
      fold.n++;
      const ratio = residual(d) / fold.d0r;
      if (fold.n % fold.spf === 0 || ratio <= state.delta) fold.hist.push([fold.n, Math.log10(Math.max(ratio, 1e-300))]);
      if (ratio <= state.delta) fold.done = true;
    }
  }

  function loop() {
    if (!fold.running) return;
    stepFold(fold.spf);
    renderFoldReadouts();
    drawFold();
    drawResidual();
    if (fold.done) { fold.running = false; $('runBtn').textContent = 'Run again'; return; }
    fold.raf = requestAnimationFrame(loop);
  }

  function renderFoldReadouts() {
    const m = fold.model;
    const N = state.N;
    const ratio = residual(fold.d) / fold.d0r;
    const op = state.mode === 'L' ? 'A = L' : 'A = L²';
    $('fOp').textContent = op;
    $('fN').textContent = `${N} beads · ${m.nContacts} native contacts${state.contacts ? '' : ' (off)'}`;
    $('fLam').textContent = state.mode === 'L'
      ? `λ₂ = ${m.lam2.toFixed(4)} · λₘₐₓ = ${m.lmax.toFixed(3)}`
      : `λ₂² = ${(m.lam2 * m.lam2).toExponential(3)} · λₘₐₓ² = ${(m.lmax * m.lmax).toFixed(2)}`;
    $('fR').textContent = fold.R < 1e5 ? fold.R.toFixed(fold.R < 100 ? 2 : 1) : fold.R.toExponential(3);
    $('fEps').textContent = fold.eps.toPrecision(4);
    $('fQ').textContent = fold.q.toFixed(fold.q > 0.999 ? 6 : 4);
    $('fD').textContent = int(fold.D);
    $('fStep').textContent = int(fold.n);
    $('fRes').textContent = ratio.toExponential(2);
    $('fBound').textContent = Math.pow(fold.q, fold.n).toExponential(2);
    $('fBlind').textContent = `${sci(N * Math.log10(state.b))}`;
    const gate = $('fGate');
    if (fold.done) {
      gate.textContent = `Ω gate locked at n = ${int(fold.n)} ≤ D(δ) = ${int(fold.D)}`;
      gate.className = 'gate locked';
    } else {
      gate.textContent = fold.n === 0 ? 'Ω gate open · random coil' : `contracting · ${(100 * fold.n / fold.D).toFixed(0)}% of D(δ)`;
      gate.className = 'gate';
    }
  }

  function drawFold() {
    const cv = $('foldCanvas');
    const { ctx, w, h } = fitCanvas(cv);
    const m = fold.model, d = fold.d, N = state.N;
    const sc = Math.min(w, h) / (2 * fold.extent);
    const cx = w / 2, cy = h / 2;
    // centroids
    let nx = 0, ny = 0, lx = 0, ly = 0;
    for (let i = 0; i < N; i++) {
      nx += m.P[2 * i]; ny += m.P[2 * i + 1];
      lx += m.P[2 * i] + d[2 * i]; ly += m.P[2 * i + 1] + d[2 * i + 1];
    }
    nx /= N; ny /= N; lx /= N; ly /= N;
    const NX = (i) => cx + (m.P[2 * i] - nx) * sc, NY = (i) => cy - (m.P[2 * i + 1] - ny) * sc;
    const LX = (i) => cx + (m.P[2 * i] + d[2 * i] - lx) * sc, LY = (i) => cy - (m.P[2 * i + 1] + d[2 * i + 1] - ly) * sc;
    // native ghost (bronze)
    ctx.strokeStyle = 'rgba(188,156,108,.28)';
    ctx.lineWidth = Math.max(2, sc * 0.32);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath();
    for (let i = 0; i < N; i++) (i ? ctx.lineTo(NX(i), NY(i)) : ctx.moveTo(NX(i), NY(i)));
    ctx.stroke();
    // contacts (mint, by formation)
    const E = m.E;
    ctx.lineWidth = 1;
    for (let t = 2 * (N - 1); t < E.length; t += 2) {
      const i = E[t], j = E[t + 1];
      const dx = (m.P[2 * i] + d[2 * i]) - (m.P[2 * j] + d[2 * j]);
      const dy = (m.P[2 * i + 1] + d[2 * i + 1]) - (m.P[2 * j + 1] + d[2 * j + 1]);
      const err = Math.abs(Math.hypot(dx, dy) - 1);
      const a = Math.max(0, 1 - err / 1.2);
      if (a <= 0.02) continue;
      ctx.strokeStyle = `rgba(193,232,206,${(0.55 * a).toFixed(3)})`;
      ctx.setLineDash([2, 3]);
      ctx.beginPath(); ctx.moveTo(LX(i), LY(i)); ctx.lineTo(LX(j), LY(j)); ctx.stroke();
    }
    ctx.setLineDash([]);
    // live chain
    const locked = fold.done;
    ctx.lineWidth = Math.max(1.6, sc * 0.12);
    for (let i = 0; i < N - 1; i++) {
      const f = i / Math.max(1, N - 2);
      ctx.strokeStyle = locked ? C.mint : mixColor(C.cyan, C.bronze, f);
      ctx.beginPath(); ctx.moveTo(LX(i), LY(i)); ctx.lineTo(LX(i + 1), LY(i + 1)); ctx.stroke();
    }
    const r = Math.max(2.2, Math.min(7, sc * 0.2));
    for (let i = 0; i < N; i++) {
      const f = i / Math.max(1, N - 1);
      ctx.fillStyle = locked ? C.mint : mixColor(C.cyan, C.bronze, f);
      ctx.beginPath(); ctx.arc(LX(i), LY(i), r, 0, 2 * Math.PI); ctx.fill();
    }
    // terminus labels
    ctx.font = `500 10px ${MONO}`;
    ctx.fillStyle = C.muted;
    ctx.fillText('N', LX(0) + r + 3, LY(0) - r - 2);
    ctx.fillText('C', LX(N - 1) + r + 3, LY(N - 1) - r - 2);
    // legend
    ctx.fillStyle = C.faint;
    ctx.font = `400 10px ${MONO}`;
    ctx.fillText(w < 460 ? 'ghost bronze · live cyan · contacts mint' : 'native ghost bronze · live cyan → bronze · contacts mint · locked mint', 10, h - 10);
  }

  function mixColor(a, b, t) {
    const pa = [1, 3, 5].map((k) => parseInt(a.slice(k, k + 2), 16));
    const pb = [1, 3, 5].map((k) => parseInt(b.slice(k, k + 2), 16));
    const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }

  function drawResidual() {
    const cv = $('resCanvas');
    const { ctx, w, h } = fitCanvas(cv);
    const padL = 44, padR = 12, padT = 14, padB = 26;
    const pw = w - padL - padR, ph = h - padT - padB;
    const nMax = Math.max(10, fold.D * 1.06);
    const yMin = Math.log10(state.delta) - 1;
    const X = (n) => padL + (n / nMax) * pw;
    const Y = (v) => padT + (v / yMin) * ph;
    // axes + grid
    ctx.strokeStyle = 'rgba(36,49,56,.9)'; ctx.lineWidth = 1;
    ctx.font = `400 10px ${MONO}`; ctx.fillStyle = C.faint;
    for (let v = 0; v >= yMin; v -= (yMin < -8 ? 2 : 1)) {
      const y = Y(v);
      ctx.beginPath(); ctx.moveTo(padL, y + 0.5); ctx.lineTo(w - padR, y + 0.5); ctx.stroke();
      ctx.fillText(`10${sup(v)}`, 6, y + 3);
    }
    ctx.fillText('0', padL - 3, h - 8);
    const nl = int(fold.D);
    ctx.fillText(`D(δ) = ${nl}`, Math.min(X(fold.D) - 30, w - padR - 80), h - 8);
    // δ line
    ctx.strokeStyle = 'rgba(193,232,206,.7)'; ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(padL, Y(Math.log10(state.delta)) + 0.5); ctx.lineTo(w - padR, Y(Math.log10(state.delta)) + 0.5); ctx.stroke();
    // D marker
    ctx.strokeStyle = 'rgba(110,223,212,.35)';
    ctx.beginPath(); ctx.moveTo(X(fold.D) + 0.5, padT); ctx.lineTo(X(fold.D) + 0.5, h - padB); ctx.stroke();
    // bound q∗ⁿ
    ctx.strokeStyle = C.bronze; ctx.setLineDash([5, 4]); ctx.lineWidth = 1.4;
    ctx.beginPath(); ctx.moveTo(X(0), Y(0));
    ctx.lineTo(X(nMax), Y(Math.max(yMin, nMax * Math.log10(fold.q || 1e-300))));
    ctx.stroke();
    ctx.setLineDash([]);
    // actual
    ctx.strokeStyle = fold.done ? C.mint : C.cyan; ctx.lineWidth = 2;
    ctx.beginPath();
    fold.hist.forEach(([n, v], k) => (k ? ctx.lineTo(X(n), Y(Math.max(v, yMin))) : ctx.moveTo(X(n), Y(Math.max(v, yMin)))));
    ctx.stroke();
    // legend
    ctx.font = `400 10px ${MONO}`;
    ctx.fillStyle = C.bronze; ctx.fillText('q∗ⁿ bound', w - padR - 150, padT + 12);
    ctx.fillStyle = C.cyan; ctx.fillText('‖Ψₙ − PΨ₀‖ / ‖(I−P)Ψ₀‖', w - padR - 150, padT + 26);
    ctx.fillStyle = C.mint; ctx.fillText('δ', w - padR - 10, Y(Math.log10(state.delta)) - 4);
  }

  // ── §4 landscape chart
  const chart = { Nmax: 120, data: null, hover: null };

  function computeChart() {
    const { b, eps, delta } = state;
    const blind = [], golf = [], bias = [], funnel = [];
    for (let N = 2; N <= chart.Nmax; N++) {
      blind.push([N, N * Math.log10(b)]);
      golf.push([N, mfptLog10(N, b, 0)]);
      bias.push([N, mfptLog10(N, b, eps)]);
      const g = goModel(N, true);
      const R = state.mode === 'L' ? g.R : g.R * g.R;
      funnel.push([N, Math.log10(depthFromR(R, delta))]);
    }
    chart.data = { blind, golf, bias, funnel };
  }

  function drawChart() {
    if (!chart.data) return;
    const cv = $('landCanvas');
    const { ctx, w, h } = fitCanvas(cv);
    const compact = w < 560;
    const padL = compact ? 40 : 52, padR = compact ? 12 : 150, padT = 18, padB = 34;
    const pw = w - padL - padR, ph = h - padT - padB;
    const yMaxRaw = Math.max(...chart.data.blind.map((p) => p[1]));
    const yMax = Math.ceil(yMaxRaw / 10) * 10 + 5;
    const X = (N) => padL + ((N - 0) / chart.Nmax) * pw;
    const Y = (v) => padT + (1 - v / yMax) * ph;
    // grid
    ctx.font = `400 10px ${MONO}`;
    const ystep = yMax > 100 ? 20 : 10;
    for (let v = 0; v <= yMax; v += ystep) {
      ctx.strokeStyle = 'rgba(36,49,56,.8)'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(padL, Y(v) + 0.5); ctx.lineTo(padL + pw, Y(v) + 0.5); ctx.stroke();
      ctx.fillStyle = C.faint; ctx.fillText(`10${sup(v)}`, 4, Y(v) + 3);
    }
    for (let N = 0; N <= chart.Nmax; N += 20) {
      ctx.fillStyle = C.faint; ctx.fillText(String(N), X(N) - 6, h - padB + 16);
    }
    ctx.fillStyle = C.muted;
    ctx.fillText('N residues →', padL + pw - 80, h - 6);
    // age of universe
    const uni = Math.log10(UNIVERSE_S / TAU0);
    ctx.strokeStyle = 'rgba(216,126,116,.45)'; ctx.setLineDash([3, 5]);
    ctx.beginPath(); ctx.moveTo(padL, Y(uni) + 0.5); ctx.lineTo(padL + pw, Y(uni) + 0.5); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(216,126,116,.85)';
    ctx.fillText('age of the universe', padL + 6, Y(uni) - 5);
    // series
    const series = [
      { k: 'blind', color: C.hot, width: 2, dash: [], label: 'bᴺ · blind enumeration' },
      { k: 'golf', color: C.hot, width: 1.5, dash: [6, 4], label: 'golf course · exact MFPT' },
      { k: 'bias', color: C.bronze, width: 2, dash: [], label: `uniform bias U = ${state.eps.toFixed(1)} kT` },
      { k: 'funnel', color: C.cyan, width: 2.4, dash: [], label: `convex funnel · D(δ), ${state.mode === 'L' ? 'A = L' : 'A = L²'}` }
    ];
    series.forEach((s) => {
      ctx.strokeStyle = s.color; ctx.lineWidth = s.width; ctx.setLineDash(s.dash);
      ctx.beginPath();
      chart.data[s.k].forEach(([N, v], i) => (i ? ctx.lineTo(X(N), Y(Math.min(v, yMax))) : ctx.moveTo(X(N), Y(Math.min(v, yMax)))));
      ctx.stroke();
    });
    ctx.setLineDash([]);
    // measured
    PRESETS.filter((p) => p.fold).forEach((p) => {
      const v = Math.log10(p.fold.t / TAU0);
      const lo = Math.log10(p.fold.lo / TAU0), hi = Math.log10(p.fold.hi / TAU0);
      ctx.strokeStyle = C.mint; ctx.lineWidth = 1.2;
      if (hi > lo) { ctx.beginPath(); ctx.moveTo(X(p.N), Y(lo)); ctx.lineTo(X(p.N), Y(hi)); ctx.stroke(); }
      ctx.fillStyle = C.mint;
      ctx.beginPath(); ctx.arc(X(p.N), Y(v), 4, 0, 2 * Math.PI); ctx.fill();
      if (!compact) {
        ctx.font = `500 10px ${MONO}`;
        const tw = ctx.measureText(p.name).width;
        const lx = X(p.N) + 8, ly = Y(v) + 16;
        ctx.fillStyle = 'rgba(9,11,13,.85)';
        rrect(ctx, lx - 4, ly - 11, tw + 8, 15, 4); ctx.fill();
        ctx.fillStyle = C.mint; ctx.fillText(p.name, lx, ly);
      }
    });
    // end labels
    if (!compact) {
      ctx.font = `500 10px ${MONO}`;
      const ends = series.map((s) => ({ s, y: Y(Math.min(chart.data[s.k][chart.data[s.k].length - 1][1], yMax)) }));
      ends.sort((a, b) => a.y - b.y);
      for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 13) ends[i].y = ends[i - 1].y + 13;
      ends.forEach(({ s, y }) => { ctx.fillStyle = s.color; wrapText(ctx, s.label, padL + pw + 8, y + 3, padR - 12, 12); });
    }
    // hover
    if (chart.hover) {
      const N = chart.hover;
      const x = X(N);
      ctx.strokeStyle = 'rgba(237,242,239,.35)'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x + 0.5, padT); ctx.lineTo(x + 0.5, padT + ph); ctx.stroke();
      const get = (k) => chart.data[k][N - 2][1];
      const lines = [
        [`N = ${N}`, C.fg],
        [`bᴺ          ${sci(get('blind'))}`, C.hot],
        [`golf course ${sci(get('golf'))}`, C.hot],
        [`bias        ${sci(get('bias'))}`, C.bronze],
        [`funnel D(δ) ${int(Math.pow(10, get('funnel')))}`, C.cyan]
      ];
      ctx.font = `500 10.5px ${MONO}`;
      const bw = Math.max(...lines.map((l) => ctx.measureText(l[0]).width)) + 16;
      const bh = lines.length * 15 + 10;
      let bx = x + 10; if (bx + bw > w - 4) bx = x - bw - 10;
      const by = padT + 8;
      ctx.fillStyle = 'rgba(9,11,13,.92)'; ctx.strokeStyle = C.line;
      rrect(ctx, bx, by, bw, bh, 8); ctx.fill(); ctx.stroke();
      lines.forEach(([t, c], i) => { ctx.fillStyle = c; ctx.fillText(t, bx + 8, by + 18 + i * 15); });
    }
    // compact legend (HTML handles it); nothing more
  }

  function wrapText(ctx, text, x, y, maxW, lh) {
    const words = text.split(' ');
    let line = '', yy = y;
    for (const wd of words) {
      const test = line ? line + ' ' + wd : wd;
      if (ctx.measureText(test).width > maxW && line) { ctx.fillText(line, x, yy); line = wd; yy += lh; }
      else line = test;
    }
    if (line) ctx.fillText(line, x, yy);
  }

  function renderChartReadouts() {
    const r = 1 + (state.b - 1) * Math.exp(-state.eps);
    $('epsVal').textContent = `${state.eps.toFixed(1)} kT`;
    $('biasBase').textContent = `growth per residue 1 + (b − 1)e⁻ᵁ = ${r.toFixed(3)} · b = ${state.b}`;
    $('bVal').textContent = String(state.b);
  }

  // ── §5 E47 witness
  function renderE47() {
    const lam = [108 * 108, 112 * 112, 140 * 140, 180 * 180, 432 * 432];
    const lmin = Math.min(...lam), lmax = Math.max(...lam);
    const R = lmax / lmin;
    const epsInv = (lmax + lmin) / 2;
    $('eR').textContent = R.toString();
    $('eEps').textContent = `1/${epsInv}`;
    $('eQ').textContent = '15/17';
    $('eD').textContent = String(depthFromR(R, 1e-12));
    const cv = $('e47Canvas');
    const { ctx, w, h } = fitCanvas(cv);
    const dims = [1, 9, 25, 28, 27, 22, 13];
    const cas = [0, 2, 6, 12, 20, 30, 42];
    const padB = 34, padT = 16;
    const bw = (w - 20) / dims.length;
    const maxd = 28;
    dims.forEach((dv, J) => {
      const sel = J === 2 || J === 5;
      const bh = (dv / maxd) * (h - padT - padB);
      const x = 10 + J * bw + bw * 0.18;
      const y = h - padB - bh;
      ctx.fillStyle = sel ? C.cyan : 'rgba(101,116,120,.45)';
      rrect(ctx, x, y, bw * 0.64, bh, 4); ctx.fill();
      ctx.fillStyle = sel ? C.fg : C.faint;
      ctx.font = `500 10px ${MONO}`;
      const t = String(dv);
      ctx.fillText(t, x + bw * 0.32 - ctx.measureText(t).width / 2, y - 4);
      ctx.fillStyle = sel ? C.cyan : C.faint;
      const jl = `J=${J}`;
      ctx.fillText(jl, x + bw * 0.32 - ctx.measureText(jl).width / 2, h - padB + 14);
      const cl = `C=${cas[J]}`;
      ctx.fillStyle = C.faint;
      ctx.fillText(cl, x + bw * 0.32 - ctx.measureText(cl).width / 2, h - padB + 27);
    });
  }

  // ── wiring
  function setN(N) {
    state.N = Math.max(2, Math.min(150, Math.round(N)));
    $('nSlider').value = state.N;
    const match = PRESETS.find((p) => p.N === state.N && p.id === state.preset.id);
    if (!match) setPressed('[data-preset]', 'preset', 'custom');
  }

  function selectPreset(id) {
    const p = PRESETS.find((x) => x.id === id) || PRESETS[1];
    state.preset = p;
    state.N = p.N;
    $('nSlider').value = p.N;
    setPressed('[data-preset]', 'preset', p.id);
    renderAll(true);
  }

  function renderAll(resetFolder) {
    renderLedger();
    renderCount();
    if (resetFolder) resetFold();
    renderChartReadouts();
  }

  function onResize() {
    renderLedger();
    drawFold();
    drawResidual();
    drawChart();
    renderE47();
  }

  function init() {
    document.querySelectorAll('[data-preset]').forEach((b) => b.addEventListener('click', () => selectPreset(b.dataset.preset)));
    $('nSlider').addEventListener('input', (e) => {
      setN(+e.target.value);
      if (state.preset.N !== state.N) setPressed('[data-preset]', 'preset', 'custom');
      renderAll(true);
    });
    $('bSlider').addEventListener('input', (e) => { state.b = +e.target.value; renderAll(false); resetFold(); computeChart(); drawChart(); });
    $('epsSlider').addEventListener('input', (e) => { state.eps = +e.target.value; renderChartReadouts(); computeChart(); drawChart(); });
    document.querySelectorAll('[data-mode]').forEach((b) => b.addEventListener('click', () => {
      state.mode = b.dataset.mode; setPressed('[data-mode]', 'mode', state.mode); resetFold(); computeChart(); drawChart();
    }));
    document.querySelectorAll('[data-contacts]').forEach((b) => b.addEventListener('click', () => {
      state.contacts = b.dataset.contacts === 'on'; setPressed('[data-contacts]', 'contacts', b.dataset.contacts); resetFold();
    }));
    document.querySelectorAll('[data-delta]').forEach((b) => b.addEventListener('click', () => {
      state.delta = +b.dataset.delta; setPressed('[data-delta]', 'delta', b.dataset.delta); resetFold(); computeChart(); drawChart();
    }));
    $('runBtn').addEventListener('click', () => {
      if (fold.done) { resetFold(); }
      fold.running = !fold.running;
      $('runBtn').textContent = fold.running ? 'Pause' : 'Run Λ';
      if (fold.running) fold.raf = requestAnimationFrame(loop);
    });
    $('coilBtn').addEventListener('click', () => { state.seed += 1; resetFold(); });
    $('skipBtn').addEventListener('click', () => {
      fold.running = false;
      stepFold(Math.max(0, fold.D * 2));
      $('runBtn').textContent = fold.done ? 'Run again' : 'Run Λ';
      renderFoldReadouts(); drawFold(); drawResidual();
    });
    const lc = $('landCanvas');
    const hover = (ev) => {
      const r = lc.getBoundingClientRect();
      const compact = r.width < 560;
      const padL = compact ? 40 : 52, padR = compact ? 12 : 150;
      const x = ev.clientX - r.left;
      const N = Math.round(((x - padL) / (r.width - padL - padR)) * chart.Nmax);
      chart.hover = N >= 2 && N <= chart.Nmax ? N : null;
      drawChart();
    };
    lc.addEventListener('pointermove', hover);
    lc.addEventListener('pointerdown', hover);
    lc.addEventListener('pointerleave', () => { chart.hover = null; drawChart(); });

    setPressed('[data-preset]', 'preset', state.preset.id);
    setPressed('[data-mode]', 'mode', state.mode);
    setPressed('[data-contacts]', 'contacts', 'on');
    setPressed('[data-delta]', 'delta', String(state.delta));
    $('nSlider').value = state.N;
    $('bSlider').value = state.b;
    $('epsSlider').value = state.eps;
    renderAll(true);
    renderE47();
    // the chart needs ~120 eigen-decompositions; let the first paint land first
    setTimeout(() => { computeChart(); drawChart(); }, 30);
    let rt = 0;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(onResize, 120); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(onResize);
  }

  init();
})();
