"""Language chrome for hanoptions.trade (used by i18n.py apply and run directly).

  python3 .build/site_i18n.py chinese    add the English switch, hreflang links and the switch script to the Chinese pages
                                         (idempotent; safe to re-run after a book is regenerated)

finish_english(rel, html)  turns a translated copy of a Chinese page into the finished English page
finish_assets()            copies the shared course stylesheet into en/
"""
import re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sitebar import sitebar_html, lang_switch, LANG_SCRIPT, LANG_CSS, alternates  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

HANDBOOKS = ["psychology", "macro", "policy", "rebound"]

EN_HEAD = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700'
    '&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700;8..60,900&display=swap">\n'
    '<style id="en-overrides">\n'
    'html[lang="en"] { --font-display: "Source Serif 4", "Noto Serif SC", Georgia, serif; '
    '--font-body: "Source Sans 3", "Noto Sans SC", system-ui, sans-serif; }\n'
    'html[lang="en"] body { line-height: 1.7; }\n'
    'html[lang="en"] body * { letter-spacing: normal !important; }\n'
    'html[lang="en"] p, html[lang="en"] li, html[lang="en"] td, html[lang="en"] figcaption { hyphens: auto; -webkit-hyphens: auto; }\n'
    'html[lang="en"] p { text-wrap: pretty; }\n'
    'html[lang="en"] .toc a { grid-template-columns: 48px 1fr; }\n'
    '</style>\n')

LANG_STYLE = '<style id="lang-css">' + LANG_CSS + """
.sitebar-links { flex: 0 1 auto; min-width: 0; margin-left: auto; justify-content: flex-start; }
</style>
"""

COURSE_CSS_EXTRA = "\n/* ---------- language switch ---------- */" + LANG_CSS + """
.topbar-inner { gap: 12px; }
.topbar select { max-width: min(400px, 46vw); }
.topbar-tools { display: flex; align-items: center; gap: 10px; min-width: 0; }
@media (max-width: 600px) {
  .topbar-brand { display: none; }
  .topbar-tools { flex: 1 1 auto; }
  .topbar select { flex: 1 1 auto; max-width: none; min-width: 0; }
}
"""


def slug_of(rel):
    return rel.split("/")[0] if "/" in rel else ""


# ------------------------------------------------------------------ Chinese pages
def add_chinese_chrome(rel):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    slug = slug_of(rel)
    if '<nav class="sitebar"' in s:
        s = re.sub(r'<nav class="sitebar".*?</nav>\n?', lambda m: sitebar_html(slug, "zh", rel), s, count=1, flags=re.S)
        s = re.sub(r'<style id="lang-css">.*?</style>\n?', "", s, flags=re.S)
        s = s.replace("</head>", LANG_STYLE + "</head>", 1)
    elif 'class="topbar"' in s:
        s = re.sub(r'<a class="lang-switch".*?</a>', "", s, flags=re.S)
        s = re.sub(r'<div class="topbar-tools">(<select id="ck-jump"[^>]*></select>)</div>', r"\1", s)
        s = re.sub(r'(<select id="ck-jump"[^>]*></select>)',
                   lambda m: f'<div class="topbar-tools">{m.group(1)}{lang_switch(rel, "zh")}</div>', s, count=1)
    if 'rel="alternate" hreflang' not in s:
        s = s.replace("</head>", alternates(rel) + "\n</head>", 1)
    if 'id="lang-js"' not in s:
        s = s.replace("</body>", LANG_SCRIPT.replace("<script>", '<script id="lang-js">') + "\n</body>", 1)
    p.write_text(s, encoding="utf-8")


def add_course_css():
    p = ROOT / "options/assets/course.css"
    s = p.read_text(encoding="utf-8")
    s = s.split("\n/* ---------- language switch ---------- */")[0].rstrip() + "\n"
    p.write_text(s + COURSE_CSS_EXTRA, encoding="utf-8")


def chinese():
    add_course_css()
    rels = ["options/index.html"] + [f"options/ch{n:02d}.html" for n in range(1, 17)] + ["options/appendix.html"]
    rels += [f"{h}/index.html" for h in HANDBOOKS]
    for rel in rels:
        add_chinese_chrome(rel)
        print("zh chrome:", rel)


# ------------------------------------------------------------------ English pages
def punct(s):
    s = re.sub(r"(?<=[\w%)\]])（", " (", s)
    s = re.sub(r"）(?=[A-Za-z0-9])", ") ", s)
    table = {"（": "(", "）": ")", "，": ", ", "；": "; ", "：": ": ", "、": ", ", "。": ". ", "　": " ",
             "「": "“", "」": "”", "『": "‘", "』": "’", "《": "“", "》": "”", "！": "!", "？": "?",
             "～": "~", "％": "%", "＋": "+", "／": "/", "——": "—"}
    for a, b in table.items():
        s = s.replace(a, b)
    return s


def glossary(m):
    body = m.group(0)
    rows = []
    tb = re.search(r"<tbody>(.*?)</tbody>", body, re.S)
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tb.group(1) if tb else "", re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        if len(cells) >= 3:
            rows.append(f"        <tr><td>{cells[1]}</td><td>{cells[2]}</td></tr>")
    return ('<!--EN-GLOSSARY-START--><h3>Key terms</h3>\n'
            '      <p>The main terms in this handbook, in the order they first appear.</p>\n'
            '      <div class="tbl"><table><thead><tr><th>Term</th><th>First appears</th></tr></thead><tbody>\n'
            + "\n".join(rows) + "\n      </tbody></table></div>\n<!--EN-GLOSSARY-END-->")


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def drop_dup_small(m):
    head, text, small = m.group(1), m.group(2), m.group(3)
    a, b = norm(text), norm(small)
    if a and b and (a == b or b in a or a in b):
        return head + text
    return m.group(0)


def finish_english(rel, s):
    s = punct(s)
    if rel.endswith(".js"):
        return s
    slug = slug_of(rel)
    s = s.replace('<html lang="zh-CN">', '<html lang="en">', 1)
    # internal absolute links -> English pages
    s = re.sub(r'(href=")(/(?!/|en/)[^"]*)"', lambda m: f'{m.group(1)}/en{m.group(2)}"', s)
    if '<nav class="sitebar"' in s:
        s = re.sub(r'<nav class="sitebar".*?</nav>\n?', lambda m: sitebar_html(slug, "en", rel), s, count=1, flags=re.S)
    s = re.sub(r'<a class="lang-switch".*?</a>', lambda m: lang_switch(rel, "en"), s, flags=re.S)
    s = re.sub(r'<a class="brand" href="index.html">.*?</a>', '<a class="brand" href="index.html">US Options <span>Course</span></a>', s, flags=re.S)
    s = re.sub(r"<!--EN-GLOSSARY-START-->.*?<!--EN-GLOSSARY-END-->", glossary, s, flags=re.S)
    s = re.sub(r"(<h[1-6][^>]*>)([^<]+?)\s*<small>([^<]+)</small>", drop_dup_small, s)
    s = s.replace("</head>", EN_HEAD + "</head>", 1)
    return s


def finish_assets():
    dst = ROOT / "en/options/assets"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "options/assets/course.css", dst / "course.css")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chinese":
        chinese()
    else:
        print(__doc__)
