/* 美股期权课 · shared script
   CK.catalog  课程目录 (首页, 顶栏, 翻页都从这里生成)
   CK.bs       Black-Scholes 定价与希腊字母 (利率默认 4%, 不派息, 天数按 365 计)
   CK.plot     轻量 SVG 绘图 (折线, 柱, 点, 标签, 阴影带, 对数纵轴, 手机宽度自动换比例)
   CK.figure   注册一个绘图函数: 立即执行, 窗口尺寸变化时重绘
*/
(function () {
  "use strict";
  const CK = {};

  CK.catalog = [
    { part: "Part 1", partTitle: "Foundations", items: [
      { n: 1, file: "ch01.html", title: "What an option is, and where the money comes from", sum: "The six terms of a contract, the four basic positions, payoff diagrams at expiry, and the five sources of option profit." },
      { n: 2, file: "ch02.html", title: "US options in practice", sum: "American vs. European style, the expiration calendar, exercise and assignment, accounts and margin, orders and liquidity." },
      { n: 3, file: "ch03.html", title: "An intuition for option pricing", sum: "The six inputs, the intuition behind Black-Scholes, put–call parity, reading prices as probabilities, and mental-math rules." }
    ]},
    { part: "Part 2", partTitle: "The core variables", items: [
      { n: 4, file: "ch04.html", title: "Delta and gamma", sum: "Directional exposure and how fast it changes: share equivalents, beta weighting, P&L approximation and Gamma scalping." },
      { n: 5, file: "ch05.html", title: "Theta and vega", sum: "The shape of time decay, sensitivity to volatility, IV crush, plus Rho and the second-order Greeks." },
      { n: 6, file: "ch06.html", title: "Volatility", sum: "Realized vs. implied, the volatility risk premium, IV Rank, term structure, skew and VIX." }
    ]},
    { part: "Part 3", partTitle: "Strategies", items: [
      { n: 7, file: "ch07.html", title: "Strategies for buyers", sum: "The buyer's three enemies, choosing strike and expiration, debit spreads, LEAPS and management rules." },
      { n: 8, file: "ch08.html", title: "Strategies for sellers", sum: "What selling insurance really means: covered calls, cash-secured puts, the wheel, credit spreads and position stress tests." },
      { n: 9, file: "ch09.html", title: "Neutral and volatility strategies", sum: "Straddles, strangles, iron condors, butterflies, calendars and diagonals: when to buy volatility and when to sell it." },
      { n: 10, file: "ch10.html", title: "Trading events", sum: "The earnings IV cycle, expected vs. historical moves, macro event days, 0DTE and expiration-day effects." },
      { n: 11, file: "ch11.html", title: "Hedging and portfolio protection", sum: "Protective puts, collars, put-spread hedges, tail-hedge budgets, and reshaping a portfolio with options." }
    ]},
    { part: "Part 4", partTitle: "Portfolio and risk management", items: [
      { n: 12, file: "ch12.html", title: "Portfolio Greeks and adjustments", sum: "Adding up a portfolio's four Greeks, reading its shape, the three directions to roll, and when to simply close the position." },
      { n: 13, file: "ch13.html", title: "Risk management for options", sum: "Three measures of position size, rules for buyers and sellers, stress tests, the illusion of diversification, and the margin spiral." },
      { n: 14, file: "ch14.html", title: "Systems and process", sum: "A nine-step process, turning a view into three dimensions, a strategy selection matrix, the trading journal and expectancy statistics." }
    ]},
    { part: "Part 5", partTitle: "Mindset and next steps", items: [
      { n: 15, file: "ch15.html", title: "Psychology and how accounts die", sum: "The psychological traps of buyers and sellers, the five paths to a dead account, and their early warning signs." },
      { n: 16, file: "ch16.html", title: "Where to go next, and a summary", sum: "Advanced directions in volatility trading, a master table of strategies, a 90-day practice plan and a summary of the whole course." }
    ]},
    { part: "Appendix", partTitle: "Quick reference", items: [
      { n: 17, file: "appendix.html", title: "Appendix: glossary, quick reference and templates", sum: "A glossary, a strategy quick-reference table, a gallery of payoff diagrams, four templates, data sources and tools.", label: "A" }
    ]}
  ];
  CK.flat = CK.catalog.flatMap(p => p.items.map(it => Object.assign({ part: p.part, partTitle: p.partTitle }, it)));

  // ---------- math ----------
  function erf(x) {
    const s = x < 0 ? -1 : 1; x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  }
  CK.N = x => 0.5 * (1 + erf(x / Math.SQRT2));
  CK.n = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
  CK.R = 0.04;
  CK.DAY = 365;
  /* bs(S, K, T(年), sigma, kind "c"|"p", r=0.04, q=0)
     返回 price, delta, gamma, theta(每日历天), vega(每 1 个波动率点), rho(每 1% 利率), d1, d2 */
  CK.bs = function (S, K, T, s, kind, r, q) {
    r = r === undefined ? CK.R : r; q = q || 0;
    T = Math.max(T, 1e-6); s = Math.max(s, 1e-4);
    const N = CK.N, n = CK.n;
    const sq = s * Math.sqrt(T);
    const d1 = (Math.log(S / K) + (r - q + s * s / 2) * T) / sq, d2 = d1 - sq;
    const dK = K * Math.exp(-r * T), dS = S * Math.exp(-q * T);
    const call = dS * N(d1) - dK * N(d2);
    const isP = kind === "p";
    const price = isP ? call - dS + dK : call;
    const delta = isP ? Math.exp(-q * T) * (N(d1) - 1) : Math.exp(-q * T) * N(d1);
    const gamma = Math.exp(-q * T) * n(d1) / (S * sq);
    const thetaC = -dS * n(d1) * s / (2 * Math.sqrt(T)) - r * dK * N(d2) + q * dS * N(d1);
    const thetaP = -dS * n(d1) * s / (2 * Math.sqrt(T)) + r * dK * N(-d2) - q * dS * N(-d1);
    const theta = (isP ? thetaP : thetaC) / CK.DAY;
    const vega = dS * n(d1) * Math.sqrt(T) / 100;
    const rho = (isP ? -K * T * Math.exp(-r * T) * N(-d2) : K * T * Math.exp(-r * T) * N(d2)) / 100;
    return { price, delta, gamma, theta, vega, rho, d1, d2 };
  };
  /* 隐含波动率 (二分法) */
  CK.iv = function (price, S, K, T, kind, r) {
    let lo = 0.001, hi = 5;
    for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; if (CK.bs(S, K, T, m, kind, r).price > price) hi = m; else lo = m; }
    return (lo + hi) / 2;
  };
  /* 可复现的随机数 */
  CK.rng = function (seed) {
    let s = seed >>> 0;
    return function () { s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  };
  CK.gauss = function (rand) { let u = 0, v = 0; while (u === 0) u = rand(); while (v === 0) v = rand(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };

  // ---------- formatting ----------
  CK.range = (a, b, st) => { const out = []; for (let v = a; v <= b + 1e-9; v += st) out.push(+v.toFixed(6)); return out; };
  CK.fmt = (v, d) => (v < 0 ? "−" : "") + Math.abs(v).toFixed(d === undefined ? 2 : d);
  CK.signed = (v, d) => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(d === undefined ? 0 : d);
  CK.money = (v, d) => (v >= 0 ? "+$" : "−$") + Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  CK.usd = (v, d) => (v < 0 ? "−$" : "$") + Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  CK.pct = (v, d) => (v < 0 ? "−" : "") + Math.abs(v * 100).toFixed(d === undefined ? 1 : d) + "%";

  // ---------- svg ----------
  const NS = "http://www.w3.org/2000/svg";
  CK.el = function (tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  /* plot(svg, cfg)
     cfg.x [min,max], cfg.y [min,max], cfg.xt / cfg.yt 刻度数组, cfg.xf / cfg.yf 刻度格式化
     cfg.xlabel / cfg.ylabel, cfg.zero (横线), cfg.vline (竖虚线), cfg.ylog (对数纵轴)
     cfg.band [x0, x1, fill], cfg.hband [y0, y1, fill]
     cfg.series [{pts:[[x,y]...], color, w, dash, op, fill}]   fill: 填到 y=fill 的面积色
     cfg.bars [{x, y, w, color, y0}]   cfg.dots [[x, y, color, r]]
     cfg.labels [[x, y, text, dx, dy, anchor, color]]
     返回 {X, Y, g, W, H, m} */
  CK.plot = function (svg, cfg) {
    const el = CK.el;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (!svg.dataset.h) svg.dataset.h = svg.viewBox.baseVal.height || 320;
    const cw = svg.getBoundingClientRect().width || 680;
    const narrow = cw > 0 && cw < 560;
    const W = narrow ? 440 : 680, H = +svg.dataset.h;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    const m = { l: narrow ? 54 : 60, r: narrow ? 12 : 18, t: 16, b: 42 };
    const [x0, x1] = cfg.x, [y0, y1] = cfg.y;
    const ty = cfg.ylog ? v => Math.log10(v) : v => v;
    const X = v => m.l + (v - x0) / (x1 - x0) * (W - m.l - m.r);
    const Y = v => m.t + (1 - (ty(v) - ty(y0)) / (ty(y1) - ty(y0))) * (H - m.t - m.b);
    const g = el("g", { class: "ax" }, svg);
    if (cfg.band) el("rect", { x: X(cfg.band[0]), y: m.t, width: Math.max(0, X(cfg.band[1]) - X(cfg.band[0])), height: H - m.t - m.b, style: "fill: " + (cfg.band[2] || "var(--tint-gamma)") }, g);
    if (cfg.hband) el("rect", { x: m.l, y: Y(cfg.hband[1]), width: W - m.l - m.r, height: Math.max(0, Y(cfg.hband[0]) - Y(cfg.hband[1])), style: "fill: " + (cfg.hband[2] || "var(--tint-delta)") }, g);
    (cfg.yt || []).forEach(v => {
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), style: "stroke: var(--grid)", "stroke-width": 1 }, g);
      el("text", { x: m.l - 8, y: Y(v) + 4, "text-anchor": "end", style: "fill: var(--muted)" }, g).textContent = cfg.yf ? cfg.yf(v) : v;
    });
    (cfg.xt || []).forEach(v => {
      el("line", { x1: X(v), x2: X(v), y1: m.t, y2: H - m.b, style: "stroke: var(--grid)", "stroke-width": 1 }, g);
      el("text", { x: X(v), y: H - m.b + 18, "text-anchor": "middle", style: "fill: var(--muted)" }, g).textContent = cfg.xf ? cfg.xf(v) : v;
    });
    if (cfg.zero !== undefined) el("line", { x1: m.l, x2: W - m.r, y1: Y(cfg.zero), y2: Y(cfg.zero), style: "stroke: var(--muted)", "stroke-width": 1 }, g);
    if (cfg.vline !== undefined) el("line", { x1: X(cfg.vline), x2: X(cfg.vline), y1: m.t, y2: H - m.b, style: "stroke: var(--muted)", "stroke-width": 1, "stroke-dasharray": "3 4" }, g);
    el("text", { x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle", style: "fill: var(--muted); font-family: var(--font-body); font-size: 12.5px" }, g).textContent = cfg.xlabel || "";
    const cy = (m.t + H - m.b) / 2;
    el("text", { x: 11, y: cy, "text-anchor": "middle", transform: `rotate(-90 11 ${cy})`, style: "fill: var(--muted); font-family: var(--font-body); font-size: 12.5px" }, g).textContent = cfg.ylabel || "";
    const id = "ck" + Math.random().toString(36).slice(2, 9);
    const cp = el("clipPath", { id }, svg);
    el("rect", { x: m.l, y: m.t - 2, width: W - m.l - m.r, height: H - m.t - m.b + 4 }, cp);
    const sg = el("g", { "clip-path": `url(#${id})` }, svg);
    (cfg.bars || []).forEach(b => {
      const bw = Math.abs(X(x0 + b.w) - X(x0));
      const base = b.y0 === undefined ? (cfg.ylog ? y0 : Math.max(y0, Math.min(0, y1))) : b.y0;
      const ya = Y(b.y), yb = Y(base);
      el("rect", { x: X(b.x) - bw / 2, y: Math.min(ya, yb), width: bw, height: Math.abs(yb - ya), rx: 2, style: `fill: ${b.color || "var(--delta)"}` }, sg);
    });
    (cfg.series || []).forEach(s => {
      const pts = s.pts.filter(p => isFinite(p[1]) && (!cfg.ylog || p[1] > 0));
      if (!pts.length) return;
      const d = pts.map((p, i) => (i ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join("");
      if (s.fill !== undefined) {
        const fd = d + `L${X(pts[pts.length - 1][0]).toFixed(1)} ${Y(s.fill).toFixed(1)}L${X(pts[0][0]).toFixed(1)} ${Y(s.fill).toFixed(1)}Z`;
        el("path", { d: fd, style: `fill: ${s.fillColor || s.color}; opacity: ${s.fillOp || 0.12}; stroke: none` }, sg);
      }
      el("path", { d, style: `fill: none; stroke: ${s.color}; stroke-width: ${s.w || 2.2}; ${s.dash ? "stroke-dasharray:" + s.dash + ";" : ""} opacity: ${s.op || 1}`, "stroke-linejoin": "round" }, sg);
    });
    (cfg.dots || []).forEach(d => el("circle", { cx: X(d[0]), cy: Y(d[1]), r: d[3] || 4, style: `fill: ${d[2] || "var(--ink)"}` }, sg));
    (cfg.labels || []).forEach(lb => {
      el("text", { x: X(lb[0]) + (lb[3] || 0), y: Y(lb[1]) + (lb[4] === undefined ? -8 : lb[4]), "text-anchor": lb[5] || "middle", style: `fill: ${lb[6] || "var(--ink)"}; font-family: var(--font-mono); font-size: 11.5px` }, sg).textContent = lb[2];
    });
    return { X, Y, g: sg, W, H, m };
  };

  // ---------- figures & resize ----------
  const redraws = [];
  CK.figure = function (fn) { redraws.push(fn); try { fn(); } catch (e) { console.error(e); } return fn; };
  let rt;
  window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => redraws.forEach(f => { try { f(); } catch (e) { console.error(e); } }), 150); });

  // ---------- storage ----------
  CK.store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  // ---------- page chrome ----------
  function chrome() {
    const body = document.body;
    const cur = +body.dataset.ch || 0;
    const sel = document.getElementById("ck-jump");
    if (sel) {
      sel.innerHTML = `<option value="index.html">Course home</option>` + CK.flat.map(it => `<option value="${it.file}"${it.n === cur ? " selected" : ""}>${it.label ? it.label : "Chapter " + it.n + ":"} ${it.title}</option>`).join("");
      sel.addEventListener("change", () => { location.href = sel.value; });
    }
    const pager = document.getElementById("ck-pager");
    if (pager && cur) {
      const i = CK.flat.findIndex(it => it.n === cur);
      const prev = CK.flat[i - 1], next = CK.flat[i + 1];
      pager.innerHTML = (prev ? `<a class="prev" href="${prev.file}"><small>Previous</small>${prev.label ? "" : "Chapter " + prev.n + ": "}${prev.title}</a>` : `<a class="prev" href="index.html"><small>Back</small>Course home</a>`) +
        (next ? `<a class="next" href="${next.file}"><small>Next</small>${next.label ? "" : "Chapter " + next.n + ": "}${next.title}</a>` : `<a class="next" href="index.html"><small>Done</small>Back to course home</a>`);
    }
    // checklists
    const page = (location.pathname.split("/").pop() || "index").replace(".html", "");
    document.querySelectorAll(".card input[type=checkbox]").forEach(cb => {
      const key = "ck-" + page + "-" + cb.id;
      cb.checked = CK.store.get(key) === "1";
      cb.addEventListener("change", () => CK.store.set(key, cb.checked ? "1" : "0"));
    });
    // scrollspy
    const links = [...document.querySelectorAll(".toc a")];
    if (links.length && "IntersectionObserver" in window) {
      const map = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
      const io = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) { links.forEach(a => a.classList.remove("active")); const a = map.get(e.target.id); if (a) a.classList.add("active"); }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      document.querySelectorAll("main section[id]").forEach(s => io.observe(s));
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", chrome); else chrome();

  window.CK = CK;
})();
