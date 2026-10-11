"""Chinese -> English pipeline for hanoptions.trade.

  python3 .build/i18n.py extract           write .i18n/src/<batch>.txt (segments to translate, document order)
  python3 .build/i18n.py check <batch>     validate .i18n/en/<batch>/*.txt against the source batch
  python3 .build/i18n.py status            per-batch progress
  python3 .build/i18n.py apply             write the English pages under en/

A segment is one of
  html  inner HTML of a leaf block element (p, li, h1-h6, td, th, figcaption, summary, ...)
  text  a run of text between tags that is not inside a leaf block
  attr  an attribute value (title, aria-label, data-title, content, placeholder, alt, ...)
  js    a JavaScript string literal
  tpl   a JavaScript template literal; ${...} expressions are shown as {0}, {1}, ...
Markup, CSS, ids, classes and script logic are never sent for translation, so the English
pages keep exactly the same structure and behaviour as the Chinese ones.
"""
import hashlib, html, json, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N = ROOT / ".i18n"
CJK = re.compile(r"[㐀-鿿豈-﫿　-〿＀-￯]")
HAN = re.compile(r"[㐀-鿿豈-﫿]")

PAGES = (["options/index.html"] + [f"options/ch{n:02d}.html" for n in range(1, 17)] + ["options/appendix.html",
          "options/assets/course.js", "psychology/index.html", "macro/index.html", "policy/index.html", "rebound/index.html"])

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "dt", "dd", "figcaption", "caption", "summary",
         "label", "button", "option", "title", "blockquote", "legend", "text", "tspan"}
SKIP_CONTENT = {"script", "style"}
ATTR_RE = re.compile(r"""(\s)([A-Za-z_:][-\w:.]*)(\s*=\s*)("([^"]*)"|'([^']*)')""")


def seg_id(kind, text):
    return hashlib.sha1((kind + "\x00" + text).encode("utf-8")).hexdigest()[:10]


# ------------------------------------------------------------------ HTML structure
class Spans(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.marks = []      # (start, end) of every markup token
        self.elements = []   # dict(tag, s, se, es, e, parent)
        self.stack = []
        self.starttags = []  # (start, end, tag)

    def off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        s = self.off(); raw = self.get_starttag_text(); e = s + len(raw)
        self.marks.append((s, e)); self.starttags.append((s, e, tag))
        el = dict(tag=tag, s=s, se=e, es=e, e=e, parent=self.stack[-1] if self.stack else None)
        if tag in VOID:
            self.elements.append(el)
        else:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        s = self.off(); raw = self.get_starttag_text(); e = s + len(raw)
        self.marks.append((s, e)); self.starttags.append((s, e, tag))
        self.elements.append(dict(tag=tag, s=s, se=e, es=e, e=e, parent=self.stack[-1] if self.stack else None))

    def handle_endtag(self, tag):
        s = self.off(); e = self.src.index(">", s) + 1
        self.marks.append((s, e))
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k]["tag"] == tag:
                el = self.stack[k]; el["es"], el["e"] = s, e
                for opened in self.stack[k:]:
                    if opened is not el:
                        opened["es"] = opened["e"] = s
                    self.elements.append(opened)
                del self.stack[k:]
                return

    def handle_comment(self, data):
        s = self.off(); self.marks.append((s, self.src.index("-->", s) + 3))

    def handle_decl(self, decl):
        s = self.off(); self.marks.append((s, self.src.index(">", s) + 1))

    def handle_pi(self, data):
        s = self.off(); self.marks.append((s, self.src.index(">", s) + 1))


# ------------------------------------------------------------------ JavaScript literals
KW_BEFORE_REGEX = re.compile(r"(?:^|[^\w$])(return|typeof|case|in|of|new|delete|void|throw|else|do|yield|await)\s*$")


def js_unescape(raw):
    def rep(m):
        c = m.group(1)
        if c.startswith("u"):
            return chr(int(c[1:], 16))
        return {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "'": "'", '"': '"', "`": "`", "0": "\0"}.get(c, c)
    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", rep, raw)


def js_escape(text, q):
    text = text.replace("\\", "\\\\").replace(q, "\\" + q).replace("\n", "\\n")
    return text


def scan_string(code, i):
    q = code[i]; j = i + 1
    while j < len(code) and code[j] != q:
        j += 2 if code[j] == "\\" else 1
    return j + 1


def scan_expr(code, k):
    """from just after '${', return index of the matching '}'"""
    depth = 0; n = len(code)
    while k < n:
        c = code[k]
        if c in "\"'":
            k = scan_string(code, k); continue
        if c == "`":
            k = scan_template(code, k)[0]; continue
        if code.startswith("//", k):
            j = code.find("\n", k); k = n if j < 0 else j; continue
        if code.startswith("/*", k):
            j = code.find("*/", k + 2); k = n if j < 0 else j + 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            if depth == 0:
                return k
            depth -= 1
        k += 1
    return n


def scan_template(code, i):
    """returns (end_index, statics[], exprs[]) for the template literal starting at i"""
    j = i + 1; n = len(code); statics, exprs = [], []; start = j
    while j < n:
        c = code[j]
        if c == "\\":
            j += 2; continue
        if c == "`":
            statics.append(code[start:j]); return j + 1, statics, exprs
        if code.startswith("${", j):
            statics.append(code[start:j]); e = scan_expr(code, j + 2)
            exprs.append(code[j + 2:e]); j = e + 1; start = j; continue
        j += 1
    statics.append(code[start:n]); return n, statics, exprs


def transform_js(code, H, ctx_base=""):
    out = []; i = 0; n = len(code); prev = ""
    while i < n:
        c = code[i]
        if c in "\"'":
            j = scan_string(code, i); raw = code[i + 1:j - 1]
            if HAN.search(raw):
                ctx = code[max(0, i - 50):min(n, j + 30)].replace("\n", " ")
                new = H.js(js_unescape(raw), ctx)
                out.append(c + js_escape(new, c) + c)
            else:
                out.append(code[i:j])
            i = j; prev = "a"; continue
        if c == "`":
            j, statics, exprs = scan_template(code, i)
            new_exprs = [transform_js(e, H) for e in exprs]
            masked = "".join(s + (f"{{{k}}}" if k < len(exprs) else "") for k, s in enumerate(statics))
            if HAN.search("".join(statics)):
                ctx = code[max(0, i - 40):min(n, i + 20)].replace("\n", " ")
                tr = H.tpl(masked, ctx)
                parts = re.split(r"\{(\d+)\}", tr)
                buf = []
                for k, p in enumerate(parts):
                    if k % 2 == 0:
                        buf.append(p.replace("`", "\\`").replace("${", "\\${"))
                    else:
                        buf.append("${" + new_exprs[int(p)] + "}")
                out.append("`" + "".join(buf) + "`")
            else:
                buf = []
                for k, s in enumerate(statics):
                    buf.append(s)
                    if k < len(new_exprs):
                        buf.append("${" + new_exprs[k] + "}")
                out.append("`" + "".join(buf) + "`")
            i = j; prev = "a"; continue
        if code.startswith("//", i):
            j = code.find("\n", i); j = n if j < 0 else j; out.append(code[i:j]); i = j; continue
        if code.startswith("/*", i):
            j = code.find("*/", i + 2); j = n if j < 0 else j + 2; out.append(code[i:j]); i = j; continue
        if c == "/" and (prev in "" or prev in "(,=:[!&|?{};+-*%<>~^" or KW_BEFORE_REGEX.search(code[:i])):
            j = i + 1; in_cls = False
            while j < n:
                if code[j] == "\\":
                    j += 2; continue
                if code[j] == "[":
                    in_cls = True
                elif code[j] == "]":
                    in_cls = False
                elif code[j] == "/" and not in_cls:
                    break
                elif code[j] == "\n":
                    break
                j += 1
            j += 1
            while j < n and code[j].isalpha():
                j += 1
            out.append(code[i:j]); i = j; prev = "a"; continue
        out.append(c)
        if not c.isspace():
            prev = "a" if (c.isalnum() or c in "_$)]") else c
        i += 1
    return "".join(out)


# ------------------------------------------------------------------ page processing
class Collect:
    def __init__(self):
        self.segs = []; self.seen = set()

    def add(self, kind, text, ctx=None):
        key = seg_id(kind, text)
        if key not in self.seen:
            self.seen.add(key); self.segs.append((key, kind, text, ctx))
        return text

    def html(self, t): return self.add("html", t)
    def text(self, t): return self.add("text", t)
    def attr(self, t): return self.add("attr", t)
    def js(self, t, ctx): return self.add("js", t, ctx)
    def tpl(self, t, ctx): return self.add("tpl", t, ctx)


class Apply:
    def __init__(self, tr):
        self.tr = tr; self.missing = []

    def get(self, kind, text):
        key = seg_id(kind, text)
        if key in self.tr:
            t = self.tr[key]
            if kind in ("js", "tpl") and t:
                if text[-1:].isspace() and t[-1:].isalnum():
                    t = t + " "
                if text[:1].isspace() and t[:1].isalnum():
                    t = " " + t
            return t
        self.missing.append((key, kind, text[:60])); return text

    def html(self, t): return self.get("html", t)
    def text(self, t): return self.get("text", t)
    def attr(self, t): return self.get("attr", t)
    def js(self, t, ctx): return self.get("js", t)
    def tpl(self, t, ctx): return self.get("tpl", t)


def strip_ws(s):
    m = re.match(r"^(\s*)(.*?)(\s*)$", s, re.S)
    return m.group(1), m.group(2), m.group(3)


def process_html(src, H):
    p = Spans(src); p.feed(src); p.close()
    for el in p.stack:  # unclosed at EOF
        el["es"] = el["e"] = len(src); p.elements.append(el)
    els = p.elements
    children_blocks = {}
    for el in els:
        el["has_cjk"] = bool(HAN.search(src[el["se"]:el["es"]]))
    # leaf blocks: BLOCK elements with CJK content and no descendant BLOCK element with CJK
    leaf = []
    for el in els:
        if el["tag"] in BLOCK and el["has_cjk"]:
            el["is_block"] = True
    for el in els:
        if el.get("is_block"):
            q = el["parent"]
            while q is not None:
                q["has_block_desc"] = True
                q = q["parent"]
    skip_spans = []
    for el in els:
        if el["tag"] in SKIP_CONTENT:
            skip_spans.append((el["se"], el["es"], el["tag"]))
    for el in els:
        if el.get("is_block") and not el.get("has_block_desc"):
            inside_skip = any(a <= el["s"] < b for a, b, _ in skip_spans)
            if not inside_skip:
                leaf.append((el["se"], el["es"]))
    leaf.sort()
    reps = []  # (start, end, new_text)
    for a, b in leaf:
        lead, core, trail = strip_ws(src[a:b])
        reps.append((a, b, lead + H.html(core) + trail))

    def in_leaf(pos):
        return any(a <= pos < b for a, b in leaf)

    # text runs between markup tokens
    marks = sorted(p.marks)
    pos = 0
    for s, e in marks + [(len(src), len(src))]:
        if s > pos:
            seg = src[pos:s]
            if HAN.search(seg) and not in_leaf(pos) and not any(a <= pos < b for a, b, _ in skip_spans):
                lead, core, trail = strip_ws(seg)
                reps.append((pos, s, lead + H.text(core) + trail))
        pos = max(pos, e)
    # attributes outside leaf blocks
    for s, e, tag in p.starttags:
        if in_leaf(s):
            continue
        raw = src[s:e]
        if not HAN.search(raw):
            continue
        for m in ATTR_RE.finditer(raw):
            val = m.group(5) if m.group(5) is not None else m.group(6)
            if val is None or not HAN.search(val):
                continue
            name = m.group(2).lower()
            vs = s + m.start(4) + 1; ve = s + m.end(4) - 1
            if name.startswith("on"):
                reps.append((vs, ve, html.escape(transform_js(html.unescape(val), H), quote=True)))
            else:
                reps.append((vs, ve, html.escape(H.attr(html.unescape(val)), quote=True)))
    # scripts
    for a, b, tag in skip_spans:
        if tag == "script" and HAN.search(src[a:b]):
            reps.append((a, b, transform_js(src[a:b], H)))
    reps.sort()
    out = []; pos = 0
    for a, b, t in reps:
        if a < pos:
            raise ValueError(f"overlapping replacement at {a}")
        out.append(src[pos:a]); out.append(t); pos = b
    out.append(src[pos:])
    return "".join(out)


def process_file(rel, H):
    src = (ROOT / rel).read_text(encoding="utf-8")
    if rel.endswith(".js"):
        return transform_js(src, H)
    return process_html(src, H)


def batch_name(rel):
    return rel.replace("/index.html", "").replace("/", "-").replace(".html", "").replace(".js", "-js")


# ------------------------------------------------------------------ segment files
def write_src(name, rel, segs):
    lines = [f"## source: {rel}  ({len(segs)} segments)"]
    for key, kind, text, ctx in segs:
        lines.append(f"@@ {key} {kind}")
        if ctx:
            lines.append(f"## code: {ctx}")
        lines.append(text)
    (I18N / "src" / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_blocks(text):
    blocks = {}; order = []; cur = None; buf = []
    for line in text.split("\n"):
        m = re.match(r"^@@ ([0-9a-f]{10}) (\w+)\s*$", line)
        if m:
            if cur:
                blocks[cur[0]] = (cur[1], "\n".join(buf).strip("\n"))
            cur = (m.group(1), m.group(2)); order.append(cur[0]); buf = []
        elif line.startswith("## "):
            continue
        elif cur:
            buf.append(line)
    if cur:
        blocks[cur[0]] = (cur[1], "\n".join(buf).strip("\n"))
    return blocks, order


def read_en(name):
    d = I18N / "en" / name
    text = ""
    if d.is_dir():
        for f in sorted(d.glob("*.txt")):
            text += f.read_text(encoding="utf-8") + "\n"
    return read_blocks(text)[0]


EK = re.compile(r'<span class="ek">.*?</span>', re.S)
TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)([^>]*)>")
FREE_ATTRS = re.compile(r'\s(title|alt|aria-label|placeholder|data-title)\s*=\s*("[^"]*"|\'[^\']*\')')


def tag_signature(s):
    s = EK.sub("", s)
    sig = []
    for m in TAG.finditer(s):
        attrs = FREE_ATTRS.sub("", m.group(3)).strip()
        sig.append(f"<{m.group(1)}{m.group(2).lower()} {attrs}>")
    return sorted(sig)


def check(name, quiet=False):
    src, order = read_blocks((I18N / "src" / f"{name}.txt").read_text(encoding="utf-8"))
    en = read_en(name)
    problems = []
    for key in order:
        kind, s = src[key]
        if key not in en:
            problems.append((key, "missing")); continue
        k2, t = en[key]
        if t == "<empty>" and kind in ("js", "tpl"):
            continue
        if not t.strip() and not (kind in ("js", "tpl") and t):
            problems.append((key, "empty translation")); continue
        if HAN.search(t):
            problems.append((key, "still contains Chinese: " + "".join(HAN.findall(t))[:20]))
        if kind == "html" and tag_signature(s) != tag_signature(t):
            a, b = tag_signature(s), tag_signature(t)
            diff = [x for x in a if x not in b][:2] + ["+" + x for x in b if x not in a][:2]
            problems.append((key, "tags differ: " + " ".join(diff)))
        if kind in ("text", "attr", "js") and TAG.search(t) and not TAG.search(s):
            problems.append((key, "added HTML tags"))
        if kind in ("js", "tpl"):
            ps, pt = sorted(re.findall(r"\{\d+\}", s)), sorted(re.findall(r"\{\d+\}", t))
            if ps != pt:
                problems.append((key, f"placeholders differ: {ps} vs {pt}"))
            if tag_signature(s) != tag_signature(t):
                problems.append((key, "tags differ inside JS string"))
    extra = [k for k in en if k not in src]
    if not quiet:
        print(f"{name}: {len(order)} segments, {len(en)} translated, {len(problems)} problems, {len(extra)} unknown ids")
        for key, msg in problems[:40]:
            print(f"  @@ {key}: {msg}")
        if len(problems) > 40:
            print(f"  ... {len(problems) - 40} more")
        for k in extra[:10]:
            print(f"  unknown id {k} (not in source; check for typos)")
    return problems, extra


# ------------------------------------------------------------------ commands
def cmd_extract():
    (I18N / "src").mkdir(parents=True, exist_ok=True)
    manifest = {}
    for rel in PAGES:
        C = Collect(); process_file(rel, C)
        name = batch_name(rel)
        chars = sum(len(HAN.findall(t)) for _, _, t, _ in C.segs)
        parts = 1 if chars <= 13000 else -(-chars // 11000)
        if parts == 1:
            write_src(name, rel, C.segs); manifest[name] = dict(rel=rel, segments=len(C.segs), chars=chars)
        else:
            per = chars / parts; k = 0; acc = 0; chunk = []
            for seg in C.segs:
                chunk.append(seg); acc += len(HAN.findall(seg[2]))
                if acc >= per * (k + 1) and k < parts - 1:
                    write_src(f"{name}-{k + 1}", rel, chunk)
                    manifest[f"{name}-{k + 1}"] = dict(rel=rel, segments=len(chunk), chars=sum(len(HAN.findall(s[2])) for s in chunk))
                    chunk = []; k += 1
            write_src(f"{name}-{k + 1}", rel, chunk)
            manifest[f"{name}-{k + 1}"] = dict(rel=rel, segments=len(chunk), chars=sum(len(HAN.findall(s[2])) for s in chunk))
    (I18N / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in manifest.items():
        print(f"{k:22s} {v['segments']:5d} segments {v['chars']:7d} chars")
    print("total chars", sum(v["chars"] for v in manifest.values()))


def all_translations():
    tr = {}
    for d in sorted((I18N / "en").glob("*")):
        if d.is_dir():
            for k, (kind, t) in read_en(d.name).items():
                tr[k] = "" if t == "<empty>" else t
    return tr


def cmd_status():
    m = json.loads((I18N / "manifest.json").read_text(encoding="utf-8"))
    for name in m:
        probs, extra = check(name, quiet=True)
        print(f"{name:22s} {m[name]['segments']:5d} segs  problems {len(probs):5d}")


def en_path(rel):
    return ROOT / "en" / rel


def cmd_apply():
    sys.path.insert(0, str(ROOT / ".build"))
    import site_i18n
    tr_all = all_translations()
    manifest = json.loads((I18N / "manifest.json").read_text(encoding="utf-8"))
    total_missing = 0
    for rel in PAGES:
        tr = dict(tr_all)
        for name, info in manifest.items():
            if info["rel"] == rel:
                for k, (kind, t) in read_en(name).items():
                    tr[k] = "" if t == "<empty>" else t
        A = Apply(tr)
        out = process_file(rel, A)
        out = site_i18n.finish_english(rel, out)
        dst = en_path(rel); dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        left = len(HAN.findall(re.sub(r"<!--.*?-->|/\*.*?\*/", "", out, flags=re.S)))
        total_missing += len(A.missing)
        print(f"{rel:28s} missing {len(A.missing):4d}  chinese chars left {left}")
    site_i18n.finish_assets()
    print("missing segments total:", total_missing)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "extract":
        cmd_extract()
    elif cmd == "check":
        probs, extra = check(sys.argv[2])
        sys.exit(1 if probs or extra else 0)
    elif cmd == "status":
        cmd_status()
    elif cmd == "apply":
        cmd_apply()
    else:
        print(__doc__)
