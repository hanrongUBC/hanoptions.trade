"""Shared site chrome for hanoptions.trade.

sitebar_css()               -> CSS for the slim site bar and the language switch (uses each page's own
                               --paper/--rule/--ink/--muted/--grid/--plate/--font-mono tokens)
sitebar_html(slug, lang)    -> the bar markup, with the current book marked and a link to the other language
lang_switch(rel, lang)      -> just the language-switch link (used in the options chapter top bar)
LANG_SCRIPT                 -> remembers the reader's choice and keeps the current #chapter when switching
alternates(rel)             -> <link rel="alternate" hreflang=...> tags for a page
"""

COURSES = [
    ("options",    "美股期权课",   "US Options Course"),
    ("psychology", "交易心理学",   "Trading Psychology"),
    ("macro",      "宏观交易框架", "Macro Trading Framework"),
    ("policy",     "政策叙事投资", "Policy Narrative Investing"),
    ("rebound",    "超卖反弹清单", "Oversold Rebound List"),
]

SITE = "https://hanoptions.trade"


def page_url(rel, lang):
    """rel is the Chinese source path, e.g. 'options/ch04.html', 'psychology/index.html', 'index.html'."""
    path = "/" + rel
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return ("/en" + path) if lang == "en" else path


def sitebar_css():
    return """
/* ---------- site bar (hanoptions.trade) ---------- */
.sitebar { border-bottom: 1px solid var(--rule); background: var(--paper); font-size: 13.5px; line-height: 1.4; }
.sitebar-inner { max-width: 1180px; margin: 0 auto; padding: 9px 24px; display: flex; gap: 18px; align-items: center; justify-content: space-between; }
.sitebar-home { font-family: var(--font-mono); color: var(--muted); text-decoration: none; letter-spacing: .02em; white-space: nowrap; }
.sitebar-home:hover { color: var(--ink); }
.sitebar-links { display: flex; gap: 2px; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; flex: 0 1 auto; min-width: 0; margin-left: auto; justify-content: flex-start; }
.sitebar-links::-webkit-scrollbar { display: none; }
.sitebar-links a { color: var(--muted); text-decoration: none; padding: 3px 9px; border-radius: 4px; white-space: nowrap; }
.sitebar-links a:hover { color: var(--ink); background: var(--grid); }
.sitebar-links a[aria-current="page"] { color: var(--ink); background: var(--plate); box-shadow: inset 0 0 0 1px var(--rule); }
""" + LANG_CSS + """
@media (max-width: 900px) { .sitebar-inner { padding-inline: 16px; } }
@media (max-width: 480px) { .sitebar-inner { gap: 10px; } .sitebar-links a { padding: 3px 7px; } }
"""


LANG_CSS = """
.lang-switch { flex: none; display: inline-flex; align-items: center; gap: 6px; padding: 3px 11px; border: 1px solid var(--rule); border-radius: 999px;
  background: var(--plate); color: var(--ink); text-decoration: none; font-size: 13px; line-height: 1.5; white-space: nowrap; font-family: var(--font-body); letter-spacing: 0; }
.lang-switch:hover { border-color: var(--ink); }
.lang-switch svg { width: 13px; height: 13px; flex: none; }
"""

GLOBE = ('<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.2"/>'
         '<path d="M1.5 8h13M8 1.5c2 2 2.8 4.2 2.8 6.5S10 12.5 8 14.5M8 1.5C6 3.5 5.2 5.7 5.2 8S6 12.5 8 14.5" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>')


def lang_switch(rel, lang):
    """the link shown on a page in `lang`, pointing to the other language"""
    if lang == "zh":
        return f'<a class="lang-switch" href="{page_url(rel, "en")}" hreflang="en" lang="en" data-lang="en">{GLOBE}English</a>'
    return f'<a class="lang-switch" href="{page_url(rel, "zh")}" hreflang="zh-CN" lang="zh-CN" data-lang="zh">{GLOBE}中文</a>'


LANG_SCRIPT = ('<script>(function(){document.querySelectorAll(".lang-switch").forEach(function(a){a.addEventListener("click",function(){'
               'try{localStorage.setItem("hl-lang",a.getAttribute("data-lang"))}catch(e){}'
               'var h=a.getAttribute("href");if(location.hash&&h.indexOf("#")<0)a.setAttribute("href",h+location.hash);});});})();</script>')


def alternates(rel):
    return (f'<link rel="alternate" hreflang="zh-CN" href="{SITE}{page_url(rel, "zh")}">'
            f'<link rel="alternate" hreflang="en" href="{SITE}{page_url(rel, "en")}">')


def sitebar_html(current, lang="zh", rel=None):
    rel = rel or (f"{current}/index.html" if current else "index.html")
    prefix = "/en" if lang == "en" else ""
    links = "".join(
        f'<a href="{prefix}/{slug}/"{" aria-current=\"page\"" if slug == current else ""}>{en if lang == "en" else zh}</a>'
        for slug, zh, en in COURSES
    )
    label = "Site navigation" if lang == "en" else "站点导航"
    return (
        f'<nav class="sitebar" aria-label="{label}"><div class="sitebar-inner">'
        f'<a class="sitebar-home" href="{prefix}/">hanoptions.trade</a>'
        f'<div class="sitebar-links">{links}</div>'
        f'{lang_switch(rel, lang)}'
        '</div></nav>\n'
    )
