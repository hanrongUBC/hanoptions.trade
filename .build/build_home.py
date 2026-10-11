"""Build the hanoptions.trade home page (index.html).

The five handbooks are shown as printed books lying on the desk. Each cover's line art is computed
from the book's own subject, so the drawing on the cover is a real chart, not decoration:

  options     straddle values from one year out to expiry (Black-Scholes)
  psychology  100 equity curves of a +0.35R system (45% win rate, +2R / -1R)
  macro       yield-curve shapes over one rate cycle (Nelson-Siegel, illustrative)
  policy      daily slogan heat vs a slow multi-year capital-flow trend (illustrative)
  rebound     the 20 stocks' moves since 9/30, from the overview table in rebound/ chapter 2

Edit BOOKS below to change titles, copy or tables of contents, then run:
    python3 .build/build_home.py
"""
import math, random, re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- art
def f1(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def poly(pts, style, extra=""):
    p = " ".join(f"{f1(x)},{f1(y)}" for x, y in pts)
    return f'<polyline points="{p}" style="{style}"{extra}/>'


def art_options():
    K, sig, r = 100.0, 0.32, 0.04
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def straddle(S, T):
        if T <= 0:
            return abs(S - K)
        sq = sig * math.sqrt(T)
        d1 = (math.log(S / K) + (r + sig * sig / 2) * T) / sq
        d2 = d1 - sq
        C = S * N(d1) - K * math.exp(-r * T) * N(d2)
        return 2 * C - S + K * math.exp(-r * T)

    X = lambda S: (S - 55) / 90 * 200
    Y = lambda v: 165 - v * 2.6
    Ts = [1.0, .8, .64, .5, .4, .32, .25, .19, .14, .1, .07, .045, .025, .012]
    out = []
    for j, T in enumerate(Ts):
        op = .26 + .6 * j / (len(Ts) - 1)
        pts = [(X(S), Y(straddle(S, T))) for S in [55 + i * 1.5 for i in range(61)]]
        out.append(poly(pts, f"fill:none;stroke:var(--c-line);stroke-width:.7;stroke-opacity:{op:.2f}"))
    out.append(poly([(X(55), Y(45)), (X(100), Y(0)), (X(145), Y(45))],
                    "fill:none;stroke:var(--c-spot);stroke-width:2;stroke-linejoin:round"))
    out.append(f'<circle cx="{f1(X(100))}" cy="{f1(Y(0))}" r="2.4" style="fill:var(--c-spot)"/>')
    return "".join(out), {}


def art_psychology():
    rng = random.Random(11)
    paths = []
    for _ in range(100):
        e, pts = 0, [0]
        for _n in range(100):
            e += 2 if rng.random() < .45 else -1
            pts.append(e)
        paths.append(pts)
    neg10 = sum(1 for p in paths if p[10] < 0)
    neg100 = sum(1 for p in paths if p[100] < 0)
    lo = min(min(p) for p in paths); hi = max(max(p) for p in paths)
    top, bot = 14, 160
    sc = (bot - top) / (hi - lo)
    Y = lambda e: top + (hi - e) * sc
    X = lambda n: n * 2
    finals = sorted(p[100] for p in paths); med = finals[len(finals) // 2]
    cand = [p for p in paths if p[10] < 0]
    hl = min(cand, key=lambda p: abs(p[100] - med))
    out = [f'<line x1="0" x2="200" y1="{f1(Y(0))}" y2="{f1(Y(0))}" style="stroke:var(--c-line);stroke-width:.6;stroke-opacity:.55;stroke-dasharray:2 2"/>',
           f'<line x1="{X(10)}" x2="{X(10)}" y1="{top}" y2="{bot}" style="stroke:var(--c-line);stroke-width:.6;stroke-opacity:.45;stroke-dasharray:1.5 2"/>']
    for p in paths:
        if p is hl:
            continue
        pts = [(X(n), Y(p[n])) for n in range(0, 101, 2)]
        out.append(poly(pts, "fill:none;stroke:var(--c-line);stroke-width:.55;stroke-opacity:.26"))
    pts = [(X(n), Y(hl[n])) for n in range(0, 101)]
    out.append(poly(pts, "fill:none;stroke:var(--c-spot);stroke-width:1.6;stroke-linejoin:round"))
    return "".join(out), {"neg10": neg10, "neg100": neg100}


def art_macro():
    mats = [0.25 * (30 / 0.25) ** (i / 39) for i in range(40)]
    lx = lambda m: 8 + 184 * (math.log(m) - math.log(.25)) / (math.log(30) - math.log(.25))
    tau = 1.8

    def ns(m, b0, b1, b2):
        a = m / tau
        g = (1 - math.exp(-a)) / a
        return b0 + b1 * g + b2 * (g - math.exp(-a))

    n = 14
    curves = []
    for k in range(n):
        ph = 2 * math.pi * k / (n - 1)
        b1 = -1.8 + 2.7 * (1 - math.cos(ph)) / 2
        b2 = 1.1 * math.sin(ph)
        b0 = 3.6 + 1.0 * math.sin(ph / 2)
        curves.append((k, b1, [(lx(m), ns(m, b0, b1, b2)) for m in mats]))
    hl = max(curves, key=lambda c: c[1])[0]
    out = []
    for k, b1, pts in curves:
        y0 = 50 + k * 8.2
        ys = [(x, y0 - (y - 2.0) * 15) for x, y in pts]
        area = ys + [(ys[-1][0], y0 + 12), (ys[0][0], y0 + 12)]
        p = " ".join(f"{f1(x)},{f1(y)}" for x, y in area)
        out.append(f'<polygon points="{p}" style="fill:var(--c-bg);stroke:none"/>')
        if k == hl:
            out.append(poly(ys, "fill:none;stroke:var(--c-spot);stroke-width:1.7;stroke-linejoin:round"))
        else:
            out.append(poly(ys, "fill:none;stroke:var(--c-line);stroke-width:.85"))
    return "".join(out), {}


def art_policy():
    rng = random.Random(5)
    out = [f'<line x1="0" x2="200" y1="92" y2="92" style="stroke:var(--c-line);stroke-width:.6;stroke-opacity:.6"/>']
    for i in range(150):
        x = 2 + i * 196 / 149
        h = min(60, rng.expovariate(1 / 8.5) + (rng.random() < .06) * rng.uniform(18, 40))
        op = .3 + .6 * min(1, h / 45)
        out.append(f'<line x1="{f1(x)}" x2="{f1(x)}" y1="92" y2="{f1(92 - h)}" style="stroke:var(--c-line);stroke-width:.7;stroke-opacity:{op:.2f}"/>')
    trend = [(x, 160 - 54 / (1 + math.exp(-(x - 96) / 27)) + 1.1 * math.sin(x / 9)) for x in range(0, 201, 4)]
    area = trend + [(200, 172), (0, 172)]
    out.append('<polygon points="' + " ".join(f"{f1(x)},{f1(y)}" for x, y in area) + '" style="fill:var(--c-spot);fill-opacity:.22;stroke:none"/>')
    out.append(poly(trend, "fill:none;stroke:var(--c-spot);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round"))
    return "".join(out), {}


def rebound_moves():
    s = (ROOT / "rebound/index.html").read_text(encoding="utf-8")
    i = s.find('<article class="chapter" id="c2"'); j = s.find('<article class="chapter" id="c3"')
    table = re.findall(r"<table.*?</table>", s[i:j], re.S)[0]
    rows = []
    for r in re.findall(r"<tr.*?</tr>", table, re.S)[1:]:
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
        rows.append((cells[0], float(cells[3].replace("−", "-").replace("%", ""))))
    return rows


def art_rebound():
    rows = sorted(rebound_moves(), key=lambda r: r[1])
    zero, sc = 96, 12
    step = 172 / len(rows); w = step * .7
    out = []
    for i, (tk, v) in enumerate(rows):
        x = 14 + i * step
        y, h = (zero - v * sc, v * sc) if v >= 0 else (zero, -v * sc)
        col = "var(--c-line)" if v >= 0 else "var(--c-spot)"
        out.append(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(max(h, .8))}" style="fill:{col}"/>')
    out.append(f'<line x1="8" x2="192" y1="{zero}" y2="{zero}" style="stroke:var(--c-line);stroke-width:.7"/>')
    ups = sum(1 for _, v in rows if v > 0)
    return "".join(out), {"ups": ups, "n": len(rows)}


# ---------------------------------------------------------------- content
def handbook_toc(slug, lang):
    base = ROOT / ("en" if lang == "en" else "") / slug / "index.html"
    s = base.read_text(encoding="utf-8")
    return [(c, html.unescape(t)) for c, t in re.findall(r'<article class="chapter" id="(c\d+)" data-title="([^"]*)"', s)]


def toc_items(slug, lang="zh"):
    items = []
    pre = "/en" if lang == "en" else ""
    for cid, title in handbook_toc(slug, lang):
        n = int(cid[1:])
        if lang == "en":
            k = f"{n:02d}"
            title = re.sub(r"^Introduction: ", "", title)
            title = title[:1].upper() + title[1:]
            title = {"RTX (Raytheon)": "RTX RTX Corp. (Raytheon)", "SLB (Schlumberger)": "SLB SLB (Schlumberger)"}.get(title, title)
        else:
            k = "导" if n == 0 else f"{n:02d}"
            title = re.sub(r"^导读：", "", title)
        items.append((k, f"{pre}/{slug}/#{cid}", title))
    return items


OPTIONS_TOC = {
    "zh": [("基础", None), ("01", "期权是什么，钱从哪里来"), ("02", "美股期权实务"), ("03", "期权定价的直觉"),
           ("核心变量", None), ("04", "Delta 与 Gamma"), ("05", "Theta 与 Vega"), ("06", "波动率"),
           ("策略", None), ("07", "买方策略"), ("08", "卖方策略"), ("09", "中性与波动率策略"), ("10", "事件交易"), ("11", "对冲与组合保护"),
           ("组合与风险管理", None), ("12", "组合 Greeks 与调仓"), ("13", "期权的风险管理"), ("14", "系统与流程"),
           ("心性与进阶", None), ("15", "心理与常见死法"), ("16", "进阶方向与总结"), ("附", "术语、速查与模板")],
    "en": [("Foundations", None), ("01", "What an option is, and where the money comes from"), ("02", "US options in practice"),
           ("03", "An intuition for option pricing"),
           ("The core variables", None), ("04", "Delta and gamma"), ("05", "Theta and vega"), ("06", "Volatility"),
           ("Strategies", None), ("07", "Strategies for buyers"), ("08", "Strategies for sellers"), ("09", "Neutral and volatility strategies"),
           ("10", "Trading events"), ("11", "Hedging and portfolio protection"),
           ("Portfolio and risk management", None), ("12", "Portfolio Greeks and adjustments"), ("13", "Risk management for options"),
           ("14", "Systems and process"),
           ("Mindset and next steps", None), ("15", "Psychology and how accounts die"), ("16", "Where to go next, and a summary"),
           ("A", "Appendix: glossary, quick reference and templates")],
}


def options_toc(lang):
    pre = "/en" if lang == "en" else ""
    out = []
    for k, t in OPTIONS_TOC[lang]:
        if t is None:
            out.append((k, None))
        else:
            f = "appendix.html" if k in ("附", "A") else f"ch{k}.html"
            out.append((k, f"{pre}/options/{f}", t))
    return out


def rebound_toc(lang="zh"):
    items = toc_items("rebound", lang)
    parts = {"zh": ("方法与总览", "二十家公司", "工具"), "en": ("Method and overview", "Twenty companies", "Toolkit")}[lang]
    return [(parts[0], None)] + items[:3] + [(parts[1], None)] + items[3:23] + [(parts[2], None)] + items[23:]


VOL = {"zh": ["第一册", "第二册", "第三册", "第四册", "第五册"],
       "en": ["Volume 1", "Volume 2", "Volume 3", "Volume 4", "Volume 5"]}
SERIES = {"zh": "交易研习手册　{v}", "en": "Trading Study Handbooks Vol. {n}"}

BOOKS = [
    dict(slug="options", c_bg="#23449e", c_ink="#f6f1e6", c_line="#f6f1e6", c_spot="#f3c74c",
         c_text="#23449e", c_text_dark="#8aa4ff", thick=9, art=art_options, toc=options_toc,
         zh=dict(title="美股期权课", sub="从零开始，到能管理一个期权账户",
                 facts="十六章加一篇附录，约十四万字，七十七个图表与计算工具。",
                 deck="整门课只讲一件事：股票只有涨跌一个维度，期权有方向、时间、波动率三个维度。每一种策略都是这三个维度的组合，每一笔亏损都来自某个你没意识到的维度。",
                 note="封面是一组跨式组合（同时买入平值看涨和看跌）的价值曲线，从到期前一年画到到期日。越接近到期，曲线越贴近底下那条 V 形折线。"),
         en=dict(title="US Options Course", sub="From zero to running an options account",
                 facts="Sixteen chapters and an appendix, about 120,000 words, 77 charts and calculators.",
                 deck="The whole course comes down to one idea: a stock moves in one dimension, up or down, while an option has three: direction, time and volatility. Every strategy is a mix of the three, and every loss comes from the one you weren’t watching.",
                 note="The cover shows the value of a straddle (an at-the-money call plus an at-the-money put) from a year before expiry down to expiration day. The closer to expiry, the closer the curves hug the V-shaped line at the bottom.")),
    dict(slug="psychology", c_bg="#0e5d56", c_ink="#f6f1e6", c_line="#f6f1e6", c_spot="#ff9c80",
         c_text="#0e5d56", c_text_dark="#5cc4b6", thick=3, art=art_psychology, toc=lambda lang: toc_items("psychology", lang),
         zh=dict(title="交易心理学", sub="知道和做到之间的那段距离",
                 facts="导读加十章，约八千字，六个图表。",
                 deck="多数人亏钱，不是因为不懂市场，而是在不确定和情绪里做不到自己知道该做的事：概率思维、认知偏差、仓位、连败、复盘。",
                 note="封面是同一个正期望系统的一百条资金曲线，胜率 45%，赢 2R、输 1R。第 10 笔交易时其中 {neg10} 条还在零线以下，高亮的就是一条；{end100_zh}"),
         en=dict(title="Trading Psychology", sub="The gap between knowing and doing",
                 facts="An introduction and ten chapters, about 6,000 words, six charts.",
                 deck="Most people don’t lose money because they don’t understand markets. They lose it because, under uncertainty and emotion, they can’t do what they already know they should. Probabilistic thinking, biases, position size, losing streaks, review.",
                 note="The cover shows 100 equity curves from the same positive-edge system: a 45% win rate, winners of 2R, losers of 1R. After 10 trades, {neg10} of them are still below zero, the highlighted one among them; {end100_en}")),
    dict(slug="macro", c_bg="#c8902f", c_ink="#17283a", c_line="#183f66", c_spot="#fbf1da",
         c_text="#8a5a10", c_text_dark="#e0ac55", thick=5, art=art_macro, toc=lambda lang: toc_items("macro", lang),
         zh=dict(title="宏观交易框架", sub="油价、美元、利率与政策的地图",
                 facts="导读加十一章，约两万字，九个图表。",
                 deck="股价最终由盈利和利率决定，盈利和利率又被油价、美元、就业和政策推着走。这本手册讲每天看什么、怎么推演、什么时候相信、怎样下注。",
                 note="封面是收益率曲线在一个利率周期里的形状变化：从陡峭到走平、倒挂（浅色那条），再回到正常。示意，不是真实数据。"),
         en=dict(title="Macro Trading Framework", sub="A map of oil, the dollar, rates and policy",
                 facts="An introduction and eleven chapters, about 13,000 words, nine charts.",
                 deck="Stock prices come down to earnings and interest rates, and those are pushed around by oil, the dollar, jobs and policy. This handbook covers what to watch each day, how to reason it through, when to believe it and how to bet.",
                 note="The cover shows how the yield curve changes shape over one rate cycle: steep, then flat, then inverted (the light line), then back to normal. Illustrative, not real data.")),
    dict(slug="policy", c_bg="#463b8a", c_ink="#f6f1e6", c_line="#f6f1e6", c_spot="#ffc7a6",
         c_text="#463b8a", c_text_dark="#a99cf0", thick=4, art=art_policy, toc=lambda lang: toc_items("policy", lang),
         zh=dict(title="政策叙事投资", sub="把宏大叙事拆成投资主题",
                 facts="导读加十一章，约一万五千字，五个图表。",
                 deck="政治口号每天都在变，政策带来的资本流向却能持续好几年。这本手册讲怎样把新闻里的宏大叙事，拆成可以验证、可以下注、也可以认错的投资主题。",
                 note="封面上半部分是口号和新闻的热度，天天大起大落；下半部分是政策带来的资金流向，慢，但能持续好几年。示意图。"),
         en=dict(title="Policy Narrative Investing", sub="Turning big narratives into investable themes",
                 facts="An introduction and eleven chapters, about 10,000 words, five charts.",
                 deck="Political slogans change every day, but the capital that policy sets moving can keep flowing for years. This handbook shows how to break the big narratives in the news into investment themes you can test, bet on and admit you got wrong.",
                 note="The top half of the cover is the heat of slogans and headlines, up and down every day. The bottom half is the money that policy moves: slow, but it lasts for years. Illustrative.")),
    dict(slug="rebound", c_bg="#9f3f19", c_ink="#f6f1e6", c_line="#f6f1e6", c_spot="#4f1b08",
         c_text="#9f3f19", c_text_dark="#f0a27a", thick=6, art=art_rebound, toc=rebound_toc,
         zh=dict(title="超卖反弹清单", sub="2026 年 9–10 月，二十家公司",
                 facts="二十家公司各一章，加上方法、总览和工具，约三万五千字。数据截至 2026 年 10 月 9 日收盘。",
                 deck="一位交易者在 9 月底列出的「短线会反弹」的股票，加上他 10 月初实际买入的几只。每家公司从基本面、消息面和技术面拆开看，附对比总表和财报日历。",
                 note="封面是清单上二十只股票从 9 月 30 日到 10 月 9 日的涨跌，从跌得最多排到涨得最多，{n} 只里 {ups} 只上涨（浅色）。数据来自第 2 章的总览表。"),
         en=dict(title="Oversold Rebound List", sub="Sep–Oct 2026, twenty companies",
                 facts="A chapter for each of twenty companies, plus method, overview and toolkit, about 28,000 words. Data as of the October 9, 2026 close.",
                 deck="The stocks a trader listed in late September as likely to bounce, plus the few he actually bought in early October. Each company is taken apart through its fundamentals, news and technicals, with a comparison table and an earnings calendar.",
                 note="The cover shows how each of the twenty stocks moved from September 30 to October 9, sorted from the biggest drop to the biggest gain; {ups} of {n} rose (the light bars). The data comes from the overview table in Chapter 2.")),
]

HERO_POSE = [(-8, 26), (-3, 6), (1.5, 0), (5, 12), (9, 30)]   # rotate deg, translateY px

UI = {
    "zh": dict(lang="zh-CN", title="交易研习手册 · hanoptions.trade",
               desc="五本自学笔记：美股期权课、交易心理学、宏观交易框架、政策叙事投资、超卖反弹清单。",
               h1="交易研习手册",
               lead="<span>五本自学笔记：</span><span>一门期权课，三本研习手册，</span><span>一本个股研究。</span>",
               open="打开《{t}》", read="开始阅读", src="源文件在 GitHub", quote=("《", "》")),
    "en": dict(lang="en", title="Trading Study Handbooks · hanoptions.trade",
               desc="Five self-study books: US Options Course, Trading Psychology, Macro Trading Framework, Policy Narrative Investing and the Oversold Rebound List.",
               h1="Trading Study Handbooks",
               lead="<span>Five self-study books:&nbsp;</span><span>an options course, three study handbooks&nbsp;</span><span>and one stock-by-stock case study.</span>",
               open="Open {t}", read="Start reading", src="Source on GitHub", quote=("", "")),
}


# ---------------------------------------------------------------- html
def pages_shadow(t):
    layers = [f"{i}px {i}px 0 {'#fbf8f1' if i % 2 else '#d9d4c9'}" for i in range(1, t + 1)]
    layers.append(f"{t + 1}px {t + 1}px 0 rgba(40,32,20,.18)")
    return ", ".join(layers)


def cover(b, i, cls, attrs, lang):
    t = b[lang]
    pre = "/en" if lang == "en" else ""
    series = SERIES[lang].format(v=VOL["zh"][i], n=i + 1)
    return (f'<a class="book {cls} k-{b["slug"]}" href="{pre}/{b["slug"]}/" {attrs}>'
            f'<span class="cover">'
            f'<svg class="art" viewBox="0 0 200 170" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<use href="#art-{b["slug"]}" width="200" height="170"/></svg>'
            f'<span class="series">{series}</span>'
            f'<span class="cap"><span class="title">{t["title"]}</span><span class="sub">{t["sub"]}</span></span>'
            f'</span></a>')


def render(lang, arts):
    from sitebar import sitebar_html, alternates, LANG_SCRIPT, LANG_CSS
    from site_i18n import EN_HEAD
    ui = UI[lang]
    pre = "/en" if lang == "en" else ""
    sprite, book_css, hero, entries, order_links = [], [], [], [], {}
    for i, b in enumerate(BOOKS):
        art, stats = arts[b["slug"]]
        t = b[lang]
        note = t["note"].format(**stats)
        sprite.append(f'<symbol id="art-{b["slug"]}" viewBox="0 0 200 170">{art}</symbol>')
        book_css.append(
            f'.k-{b["slug"]} {{ --c-bg: {b["c_bg"]}; --c-ink: {b["c_ink"]}; --c-line: {b["c_line"]}; --c-spot: {b["c_spot"]}; '
            f'--c-text: {b["c_text"]}; --pages: {pages_shadow(b["thick"])}; --pages-mini: {pages_shadow(max(2, round(b["thick"] * .55)))}; }}')
        book_css.append(f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .k-{b["slug"]} {{ --c-text: {b["c_text_dark"]}; }} }}')
        book_css.append(f':root[data-theme="dark"] .k-{b["slug"]} {{ --c-text: {b["c_text_dark"]}; }}')
        r, y = HERO_POSE[i]
        label = ui["open"].format(t=t["title"])
        hero.append(cover(b, i, "on-desk", f'style="--i:{i};--r:{r}deg;--y:{y}px;--z:{i + 1}" aria-label="{html.escape(label)}"', lang))
        lis = []
        for item in b["toc"](lang):
            if item[1] is None:
                lis.append(f'<li class="part">{item[0]}</li>')
            else:
                k, href, tt = item
                tt = html.escape(tt)
                m = re.match(r"^([A-Z]{2,5}) (.+)$", tt)
                if m and b["slug"] == "rebound":
                    tt = f'<span class="tk">{m.group(1)}</span>{m.group(2)}'
                lis.append(f'<li><span class="k">{k}</span><a href="{href}">{tt}</a></li>')
        entries.append(f'''
  <section class="entry k-{b["slug"]}" id="{b["slug"]}" aria-labelledby="h-{b["slug"]}">
    <div class="entry-side">
      {cover(b, i, "mini", 'tabindex="-1" aria-hidden="true"', lang)}
      <div class="entry-meta">
        <p class="vol">{VOL[lang][i]}</p>
        <h2 id="h-{b["slug"]}"><a href="{pre}/{b["slug"]}/">{t["title"]}</a></h2>
        <p class="facts">{t["facts"]}</p>
        <a class="read" href="{pre}/{b["slug"]}/">{ui["read"]}</a>
      </div>
    </div>
    <div class="entry-body">
      <p class="deck">{t["deck"]}</p>
      <p class="note">{note}</p>
      <ol class="toc">{"".join(lis)}</ol>
    </div>
  </section>''')
        q0, q1 = ui["quote"]
        order_links[b["slug"]] = f'<a class="k-{b["slug"]}" href="#{b["slug"]}">{q0}{t["title"]}{q1}</a>'

    L = order_links
    if lang == "zh":
        order = (f'<p class="order"><b>建议顺序</b>　先读{L["options"]}前六章，把定价和希腊字母学扎实；'
                 f'进入策略部分前插读{L["psychology"]}；再用{L["macro"]}和{L["policy"]}学会选方向、选时机；'
                 f'最后翻开{L["rebound"]}，看这些方法怎样落到二十家具体公司上。</p>')
    else:
        order = (f'<p class="order"><b>Suggested order</b>&ensp;Start with the first six chapters of the {L["options"]} to get pricing '
                 f'and the Greeks down. Read {L["psychology"]} before you move on to the strategies. Then use the {L["macro"]} and '
                 f'{L["policy"]} to choose direction and timing, and finish with the {L["rebound"]} to see the methods applied to twenty real companies.</p>')

    head = alternates("index.html")
    if lang == "zh":
        head += ('\n<script>(function(){try{var p=localStorage.getItem("hl-lang");if(p==="zh")return;'
                 'if(p==="en"){location.replace("/en/");return}var l=navigator.languages||[navigator.language||""];'
                 'if(!l.some(function(x){return /^zh/i.test(x)}))location.replace("/en/")}catch(e){}})();</script>')
    else:
        head += "\n" + EN_HEAD
    page = (TEMPLATE
            .replace("{{LANG}}", ui["lang"]).replace("{{TITLE}}", ui["title"]).replace("{{DESC}}", ui["desc"])
            .replace("{{HEAD_EXTRA}}", head).replace("{{LANG_CSS}}", LANG_CSS)
            .replace("{{H1}}", ui["h1"]).replace("{{LEAD}}", ui["lead"])
            .replace("{{SITEBAR}}", sitebar_html("", lang, "index.html").replace('class="sitebar-inner"', 'class="wrap sitebar-inner"'))
            .replace("{{SRC}}", ui["src"]).replace("{{BODY_END}}", LANG_SCRIPT)
            .replace("{{BOOK_CSS}}", "\n".join(book_css))
            .replace("{{SPRITE}}", "".join(sprite))
            .replace("{{HERO}}", "\n      ".join(hero))
            .replace("{{ORDER}}", order)
            .replace("{{ENTRIES}}", "".join(entries)))
    out = ROOT / ("en/index.html" if lang == "en" else "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(out.relative_to(ROOT), len(page), "bytes")


def main():
    import sys
    sys.path.insert(0, str(ROOT / ".build"))
    arts = {}
    for b in BOOKS:
        art, stats = b["art"]()
        if "neg100" in stats:
            n = stats["neg100"]
            stats["end100_zh"] = "到第 100 笔，一百条已经全部回到零线以上。" if n == 0 else f"到第 100 笔，还在亏的只剩 {n} 条。"
            stats["end100_en"] = "by trade 100, every one of them is back above zero." if n == 0 else f"by trade 100, only {n} are still losing."
        arts[b["slug"]] = (art, stats)
    render("zh", arts)
    render("en", arts)


GRAIN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .55 0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")")

TEMPLATE = """<!doctype html>
<html lang="{{LANG}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
{{HEAD_EXTRA}}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@700;900&display=swap">
<style>
/* hanoptions.trade · 首页
   Five handbooks lie on a graph-paper desk. Each cover is a printed object: a series colour, page-block
   thickness by length, and line art computed from the book's own subject (see .build/build_home.py). */
:root {
  --paper: #f4f7f6; --desk: #e8eeec; --grid: #dbe4e1; --ink: #15202a; --muted: #5b6873; --rule: #d6dee1;
  --drop: 0 1px 1.5px rgba(16,24,32,.28), 10px 24px 30px -12px rgba(16,24,32,.42);
  --font-display: "Noto Serif SC", "Songti SC", "STSong", serif;
  --font-body: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #0f161c; --desk: #121b22; --grid: #1a262e; --ink: #e3e9ed; --muted: #93a2ad; --rule: #27343e;
    --drop: 0 1px 2px rgba(0,0,0,.6), 10px 26px 34px -10px rgba(0,0,0,.75);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #0f161c; --desk: #121b22; --grid: #1a262e; --ink: #e3e9ed; --muted: #93a2ad; --rule: #27343e;
  --drop: 0 1px 2px rgba(0,0,0,.6), 10px 26px 34px -10px rgba(0,0,0,.75);
  color-scheme: dark;
}
{{BOOK_CSS}}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 16.5px; line-height: 1.85; -webkit-font-smoothing: antialiased; }
a { color: inherit; text-underline-offset: 3px; }
a:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; border-radius: 2px; }
.wrap { max-width: 1180px; margin: 0 auto; padding-inline: 24px; }

/* ---------- site bar ---------- */
.sitebar { border-bottom: 1px solid var(--rule); background: var(--paper); font-size: 13.5px; line-height: 1.4; }
.sitebar-inner { display: flex; gap: 18px; align-items: center; justify-content: space-between; padding-block: 9px; }
.sitebar-home { font-family: var(--font-mono); color: var(--ink); text-decoration: none; letter-spacing: .02em; white-space: nowrap; }
.sitebar-links { display: flex; gap: 2px; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
.sitebar-links::-webkit-scrollbar { display: none; }
.sitebar-links a { color: var(--muted); text-decoration: none; padding: 3px 9px; border-radius: 4px; white-space: nowrap; }
.sitebar-links a:hover { color: var(--ink); background: var(--grid); }
.sitebar-links { flex: 0 1 auto; min-width: 0; margin-left: auto; justify-content: flex-start; }
{{LANG_CSS}}

/* ---------- desk ---------- */
.desk { background-color: var(--desk);
  background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 24px 24px; background-position: center -1px; border-bottom: 1px solid var(--rule); overflow: hidden; }
.desk-inner { padding-block: 60px 104px; text-align: center; }
.desk h1 { font-family: var(--font-display); font-weight: 900; font-size: clamp(40px, 6.2vw, 70px); line-height: 1.1; letter-spacing: .08em; margin: 0; }
.desk .lead { margin: 14px auto 0; max-width: 30em; color: var(--muted); font-size: 17px; }
.desk .lead span { display: inline-block; }
.spread { --w: clamp(150px, 16.5vw, 208px); display: flex; justify-content: center; align-items: flex-start; margin-top: 64px; }
.spread .book + .book { margin-left: calc(var(--w) * -.07); }

/* ---------- book object ---------- */
.book { position: relative; display: block; flex: none; width: var(--w); aspect-ratio: 5 / 7; container-type: inline-size; color: inherit; text-decoration: none; }
.cover { position: absolute; inset: 0; overflow: hidden; background: var(--c-bg); color: var(--c-ink);
  border-radius: 1.2cqw 2.6cqw 2.6cqw 1.2cqw; box-shadow: var(--pages), var(--drop); }
.cover::before { content: ""; position: absolute; top: 0; bottom: 0; left: 6%; width: 1.4cqw; z-index: 2;
  background: linear-gradient(to right, rgba(0,0,0,.18), rgba(255,255,255,.12) 55%, transparent); }
.cover::after { content: ""; position: absolute; inset: 0; z-index: 3; pointer-events: none; background-image: """ + GRAIN + """; opacity: .3; mix-blend-mode: multiply; }
.art { position: absolute; left: 0; top: 0; width: 100%; height: 63%; display: block; }
.series { position: absolute; top: 6.5cqw; left: 11cqw; font-size: 4.4cqw; letter-spacing: .16em; line-height: 1; opacity: .85; white-space: nowrap; }
.cap { position: absolute; left: 11cqw; right: 12cqw; bottom: 8.5cqw; display: flex; flex-direction: column; gap: 2.6cqw; text-align: left; }
.title { font-family: var(--font-display); font-weight: 900; font-size: 11.2cqw; line-height: 1.12; letter-spacing: .02em; }
.sub { font-size: 5.1cqw; line-height: 1.5; opacity: .86; }
html[lang="en"] .title { font-size: 10cqw; line-height: 1.06; }
html[lang="en"] .series { letter-spacing: .02em !important; font-size: 4.2cqw; }
html[lang="en"] .desk h1 { letter-spacing: 0; }
html[lang="en"] .desk .lead span { display: inline; }

.on-desk { z-index: var(--z); transform: translateY(var(--y)) rotate(var(--r));
  transition: transform .45s cubic-bezier(.2,.8,.2,1);
  animation: settle .9s cubic-bezier(.2,.8,.2,1) backwards; animation-delay: calc(var(--i) * 90ms + 100ms); }
.on-desk:hover, .on-desk:focus-visible { z-index: 20; transform: translateY(calc(var(--y) - 18px)) rotate(calc(var(--r) * .3)); }
.on-desk:focus-visible { outline: none; }
.on-desk:focus-visible .cover { outline: 2px solid var(--ink); outline-offset: 5px; }
@keyframes settle { from { opacity: 0; transform: translateY(calc(var(--y) - 48px)) rotate(calc(var(--r) * 2.2)); } }

.mini { width: 132px; }
.mini .cover { box-shadow: var(--pages-mini), 0 1px 1.5px rgba(16,24,32,.25), 6px 12px 18px -8px rgba(16,24,32,.35); }

/* ---------- reading order & entries ---------- */
.order { margin: 44px 0 4px; max-width: 46em; color: var(--muted); }
.order b { color: var(--ink); font-weight: 500; }
.order a { color: var(--c-text); text-decoration: none; font-weight: 500; }
.order a:hover { text-decoration: underline; }

.entry { display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 28px 64px; padding-block: 56px; border-top: 1px solid var(--rule); }
.entry:first-of-type { margin-top: 36px; }
.entry-side .mini { margin-bottom: 28px; }
.vol { margin: 0 0 2px; font-size: 14px; color: var(--muted); }
.entry h2 { font-family: var(--font-display); font-weight: 900; font-size: 32px; line-height: 1.25; letter-spacing: .03em; margin: 0 0 12px; color: var(--c-text); }
.entry h2 a { text-decoration: none; }
.entry h2 a:hover { text-decoration: underline; text-decoration-thickness: 2px; }
.facts { margin: 0 0 20px; font-size: 15px; color: var(--muted); line-height: 1.75; }
.read { display: inline-block; background: var(--c-bg); color: var(--c-ink); text-decoration: none; padding: 9px 20px; border-radius: 6px; font-size: 15px; font-weight: 500; }
.read:hover { filter: brightness(1.08); }
.deck { margin: 0 0 14px; font-size: 17.5px; max-width: 38em; }
.note { margin: 0 0 8px; font-size: 14px; color: var(--muted); max-width: 46em; line-height: 1.75; }
.toc { list-style: none; margin: 22px 0 0; padding: 0; columns: 2; column-gap: 36px; font-size: 14.5px; line-height: 1.55; max-width: 48em; }
.toc li { break-inside: avoid; display: grid; grid-template-columns: 2.1em 1fr; gap: 8px; padding: 7px 0; border-top: 1px solid var(--rule); }
.toc li.part { display: block; border-top: 0; padding: 16px 0 4px; font-size: 13px; font-weight: 500; color: var(--c-text); break-after: avoid; }
.toc li:first-child { padding-top: 0; }
.toc li.part + li { border-top: 0; }
.toc .k { font-family: var(--font-display); font-size: 13px; color: var(--muted); padding-top: 1px; }
.toc a { color: var(--ink); text-decoration: none; }
.toc a:hover { color: var(--c-text); text-decoration: underline; }
.toc .tk { display: inline-block; min-width: 3.4em; font-family: var(--font-mono); font-size: 12.5px; color: var(--muted); }

.foot { border-top: 1px solid var(--rule); padding-block: 22px 56px; font-size: 13.5px; color: var(--muted); display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.foot a { color: var(--muted); }
.foot a:hover { color: var(--ink); }

@media (max-width: 900px) {
  .wrap { padding-inline: 16px; }
  .entry { grid-template-columns: minmax(0, 1fr); gap: 20px; padding-block: 40px; }
  .entry-side { display: grid; grid-template-columns: 104px minmax(0, 1fr); gap: 0 20px; align-items: start; }
  .entry-side .mini { width: 104px; margin-bottom: 0; }
  .entry h2 { font-size: 27px; }
}
@media (max-width: 760px) {
  .desk-inner { padding-block: 40px 64px; }
  .spread { --w: min(40vw, 184px); flex-wrap: wrap; gap: 30px 16px; max-width: 420px; margin: 44px auto 0; }
  .spread .book + .book { margin-left: 0; }
  .on-desk { transform: translateY(calc(var(--y) * .25)) rotate(calc(var(--r) * .45)); }
  .on-desk:hover, .on-desk:focus-visible { transform: translateY(calc(var(--y) * .25 - 10px)) rotate(0deg); }
  .toc { columns: 1; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .on-desk { animation: none; transition: none; }
}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>{{SPRITE}}</defs></svg>

{{SITEBAR}}

<header class="desk">
  <div class="wrap desk-inner">
    <h1>{{H1}}</h1>
    <p class="lead">{{LEAD}}</p>
    <div class="spread">
      {{HERO}}
    </div>
  </div>
</header>

<main class="wrap">
  {{ORDER}}
  {{ENTRIES}}
  <footer class="foot">
    <span>hanoptions.trade</span>
    <a href="https://github.com/hanrongUBC/hanoptions.trade">{{SRC}}</a>
  </footer>
</main>
{{BODY_END}}
</body>
</html>
"""

if __name__ == "__main__":
    main()
