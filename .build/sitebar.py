"""Shared site chrome for hanoptions.trade.

sitebar_css()       -> CSS for the slim site bar (uses the page's own --paper/--rule/--ink/--muted/--grid/--plate/--font-mono tokens)
sitebar_html(slug)  -> the bar markup, with the current course marked
"""

COURSES = [
    ("options",    "美股期权课"),
    ("psychology", "交易心理学"),
    ("macro",      "宏观交易框架"),
    ("policy",     "政策叙事投资"),
    ("rebound",    "超卖反弹清单"),
]

def sitebar_css():
    return """
/* ---------- site bar (hanoptions.trade) ---------- */
.sitebar { border-bottom: 1px solid var(--rule); background: var(--paper); font-size: 13.5px; line-height: 1.4; }
.sitebar-inner { max-width: 1180px; margin: 0 auto; padding: 9px 24px; display: flex; gap: 18px; align-items: center; justify-content: space-between; }
.sitebar-home { font-family: var(--font-mono); color: var(--muted); text-decoration: none; letter-spacing: .02em; white-space: nowrap; }
.sitebar-home:hover { color: var(--ink); }
.sitebar-links { display: flex; gap: 2px; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
.sitebar-links::-webkit-scrollbar { display: none; }
.sitebar-links a { color: var(--muted); text-decoration: none; padding: 3px 9px; border-radius: 4px; white-space: nowrap; }
.sitebar-links a:hover { color: var(--ink); background: var(--grid); }
.sitebar-links a[aria-current="page"] { color: var(--ink); background: var(--plate); box-shadow: inset 0 0 0 1px var(--rule); }
@media (max-width: 900px) { .sitebar-inner { padding-inline: 16px; } }
@media (max-width: 480px) { .sitebar-inner { gap: 10px; } .sitebar-links a { padding: 3px 7px; } }
"""

def sitebar_html(current):
    links = "".join(
        f'<a href="/{slug}/"{" aria-current=\"page\"" if slug == current else ""}>{name}</a>'
        for slug, name in COURSES
    )
    return (
        '<nav class="sitebar" aria-label="站点导航"><div class="sitebar-inner">'
        '<a class="sitebar-home" href="/">hanoptions.trade</a>'
        f'<div class="sitebar-links">{links}</div>'
        '</div></nav>\n'
    )
