"""Turn the 超卖反弹清单 handbook (an unwrapped single-page artifact file) into rebound/index.html.

Same treatment as convert_handbooks.py: real <head>, site bar CSS appended to the page's own <style>,
site bar markup injected before the masthead.
usage: python3 .build/convert_rebound.py /path/to/rebound.html
"""
import re, sys
sys.path.insert(0, "/home/claude/hanoptions.trade/.build")
from sitebar import sitebar_css, sitebar_html

src = sys.argv[1]
DST = "/home/claude/hanoptions.trade/rebound/index.html"
TITLE = "超卖反弹清单（2026 年 9–10 月）"
DESC = "二十家「短线可能反弹」的候选公司，每家单独一章，从基本面、消息面和技术面分析。数据截至 2026 年 10 月 9 日。"

s = open(src, encoding="utf-8").read()
head_end = s.index('<header class="mast">')
head_bits, body = s[:head_end], s[head_end:]
head_bits = re.sub(r"<title>.*?</title>\s*", "", head_bits, count=1, flags=re.S)
head_bits = head_bits.replace("</style>", sitebar_css() + "</style>", 1)
page = (
    "<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n"
    "<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    f"<title>{TITLE} · hanoptions.trade</title>\n"
    f"<meta name=\"description\" content=\"{DESC}\">\n"
    + head_bits.strip() + "\n</head>\n<body>\n"
    + sitebar_html("rebound")
    + body.rstrip() + "\n</body>\n</html>\n"
)
open(DST, "w", encoding="utf-8").write(page)
print(DST, len(page), "bytes; sitebar:", page.count('class="sitebar"'))
