"""Turn the three single-page handbook artifacts into proper site pages.

For each: strip the artifact wrapper, write a real <head>, inject the site bar before the masthead.
"""
import re, sys
sys.path.insert(0, "/home/claude/hanoptions.trade/.build")
from sitebar import sitebar_css, sitebar_html

SRC = "/home/claude/incoming"
DST = "/home/claude/hanoptions.trade"

META = {
    "psychology": ("交易心理学", "十一章研习手册：概率思维、认知偏差、仓位数学、连败概率与复盘。知道和做到之间的那段距离。"),
    "macro":      ("宏观交易框架", "十二章研习手册：跨资产仪表盘、利率与估值、市场体制、广度与资金流、事件剧本，从观点到交易。"),
    "policy":     ("政策叙事投资", "十二章研习手册：把新闻里的宏大叙事拆成可以验证、可以下注、也可以认错的投资主题。"),
}

for slug, (title, desc) in META.items():
    s = open(f"{SRC}/{slug}/index.html", encoding="utf-8").read()
    body_start = s.index("<body>") + len("<body>")
    inner = s[body_start:]
    # inner = "\n<title>..</title>\n<link..>..<style>..</style>\n<header class="mast">...</body></html>"
    head_end = inner.index('<header class="mast">')
    head_bits = inner[:head_end]
    body = inner[head_end:]
    assert body.rstrip().endswith("</body></html>"), slug
    body = body.rstrip()[: -len("</body></html>")].rstrip() + "\n"
    # drop the <title> from head_bits; we write our own
    head_bits = re.sub(r"<title>.*?</title>\s*", "", head_bits, count=1, flags=re.S)
    # add site bar CSS into the page's own <style> block (append before its first </style>)
    head_bits = head_bits.replace("</style>", sitebar_css() + "</style>", 1)
    page = (
        "<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        f"<title>{title} · hanoptions.trade</title>\n"
        f"<meta name=\"description\" content=\"{desc}\">\n"
        + head_bits.strip() + "\n</head>\n<body>\n"
        + sitebar_html(slug)
        + body
        + "</body>\n</html>\n"
    )
    out = f"{DST}/{slug}/index.html"
    open(out, "w", encoding="utf-8").write(page)
    print(slug, "->", out, len(page), "bytes; sitebar:", page.count('class="sitebar"'), "; title:", re.search(r"<title>(.*?)</title>", page).group(1))
