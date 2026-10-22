"""PDF -> Markdown converter for scanned / OCR'd books.

Two layout styles are supported:

  * style 1 - two-column OCR scan (Finereader): running heads, indented
    paragraphs, bold interviewer questions, bullet lists, an index in
    several columns.  Chapter titles are recognised by font size.
  * style 2 - single-column text with "==== question ====" markers and
    12pt bold headings (Word -> PostScript -> PDF).

The style is detected automatically.  The tool removes page numbers and
running heads, rebuilds paragraphs (including de-hyphenation across line and
page breaks), keeps bold/italic runs, renders interviewer questions as
blockquotes, and generates a linked table of contents.

Known limitation: this is not a generic PDF-to-Markdown engine.  It was
written for two Jack Schwager books; the OCR repair table (OCR_FIXES) and the
chapter map for "Stock Market Wizards" are specific to those scans.
"""

import argparse
import os
import re
import sys
from collections import Counter

import pymupdf
from wordfreq import top_n_list, zipf_frequency

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def norm_space(s):
    s = s.replace("\u00a0", " ").replace("\t", " ")
    s = re.sub(r"[ ]{2,}", " ", s)
    return s


def style_of(font):
    bold = "Bold" in font or "Semibold" in font
    ital = "Italic" in font or "Oblique" in font
    return bold, ital


def page_lines(page, split_gap=45, merge_gap=45):
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            spans = sorted([s for s in line["spans"] if s["text"]],
                           key=lambda s: s["bbox"][0])
            if not spans:
                continue
            # a PDF "line" may glue several columns together - split on wide gaps
            groups = [[spans[0]]]
            for prev_s, s in zip(spans, spans[1:]):
                if abs(s["bbox"][0] - prev_s["bbox"][2]) > split_gap:
                    groups.append([s])
                else:
                    groups[-1].append(s)
            for grp in groups:
                text = "".join(s["text"] for s in grp)
                if not text.strip():
                    continue
                x0 = min(s["bbox"][0] for s in grp)
                y0 = min(s["bbox"][1] for s in grp)
                x1 = max(s["bbox"][2] for s in grp)
                y1 = max(s["bbox"][3] for s in grp)
                out.append(
                    dict(
                        text=norm_space(text),
                        spans=grp,
                        x0=x0,
                        x1=x1,
                        y0=y0,
                        y1=y1,
                        size=max(s["size"] for s in grp),
                        font=max(grp, key=lambda s: len(s["text"]))["font"],
                    )
                )
    # merge fragments that sit on the same baseline (PDF sometimes splits them)
    out.sort(key=lambda l: (round(l["y0"], 1), l["x0"]))
    merged = []
    for ln in out:
        if merged and abs(ln["y0"] - merged[-1]["y0"]) < 2.0:
            prev = merged[-1]
            gap = ln["x0"] - prev["x1"]
            if 0 <= gap < merge_gap:
                prev["text"] = norm_space(prev["text"] + " " + ln["text"])
                prev["spans"] = prev["spans"] + ln["spans"]
                prev["x1"] = ln["x1"]
                prev["y1"] = max(prev["y1"], ln["y1"])
                prev["size"] = max(prev["size"], ln["size"])
                continue
        merged.append(ln)
    return merged


def line_segments(line):
    """List of (text, bold, italic) for a line, whitespace-normalised."""
    segs = []
    for s in line["spans"]:
        if not s["text"]:
            continue
        bold, ital = style_of(s["font"])
        t = norm_space(s["text"])
        if not t:
            continue
        if segs and segs[-1][1] == bold and segs[-1][2] == ital:
            segs[-1] = (segs[-1][0] + t, bold, ital)
        else:
            segs.append((t, bold, ital))
    # trim outer whitespace of the whole line
    if segs:
        segs[0] = (segs[0][0].lstrip(), segs[0][1], segs[0][2])
        segs[-1] = (segs[-1][0].rstrip(), segs[-1][1], segs[-1][2])
        segs = [s for s in segs if s[0]]
    return segs


PAGE_NUM_RE = re.compile(r"^[0-9IVXLCivxlc]{1,6}$")
SPACED_CAPS_RE = re.compile(r"^(?:[A-Z0-9.'\"\-]\s){3,}[A-Za-z0-9.'\"]?$")


def is_page_number(line):
    t = line["text"].strip()
    return bool(PAGE_NUM_RE.match(t)) and len(t) <= 6


VOCAB = {w for w in top_n_list("en", 60000) if w.isalpha() and len(w) >= 3}
FUNCTION_WORDS = {"of", "to", "in", "and", "or", "the", "a", "an", "is", "as",
                  "at", "by", "on", "for", "with", "from", "but", "if"}


def join_hyphen(a, b):
    """De-hyphenate a line break; decide whether the hyphen is real."""
    a = a.rstrip()
    b = b.lstrip()
    if not a.endswith("-"):
        return a + " " + b
    stem = a[:-1]
    m = re.search(r"([A-Za-z]+)$", stem)
    m2 = re.match(r"^([A-Za-z]+)", b)
    if not (m and m2):
        return stem + b
    head, tail = m.group(1), m2.group(1)
    if head.lower() in FUNCTION_WORDS:
        return stem + " " + b
    joined = (head + tail).lower()
    if joined in VOCAB and zipf_frequency(joined, "en") >= 2.0 and len(joined) >= 5:
        return stem + b
    return stem + "-" + b


def render_segments(segs, escape=True):
    """Turn (text, bold, italic) segments into inline markdown."""
    out = []
    for text, bold, ital in segs:
        t = text
        if escape:
            t = t.replace("*", r"\*").replace("_", r"\_").replace("`", r"\`")
            t = re.sub(r"<", r"&lt;", t)
            t = re.sub(r">", r"&gt;", t)
        stripped = t.strip()
        if not stripped:
            out.append(t)
            continue
        lead = t[: len(t) - len(t.lstrip())]
        trail = t[len(t.rstrip()):]
        if bold and ital:
            core = "***" + stripped + "***"
        elif bold:
            core = "**" + stripped + "**"
        elif ital:
            core = "*" + stripped + "*"
        else:
            core = stripped
        out.append(lead + core + trail)
    s = "".join(out)
    s = re.sub(r"[ ]{2,}", " ", s)
    return s.strip()


# --------------------------------------------------------------------------
# OCR / typography clean-up
# --------------------------------------------------------------------------

def fix_span_hyphen(text):
    """Repair words that the PDF split with 'hyphen + space'."""
    return re.sub(r"([A-Za-z]{2,})-\s+([A-Za-z]{2,})",
                  lambda m: join_hyphen(m.group(1) + "-", m.group(2)), text)


def fix_common(text):
    text = fix_span_hyphen(text)
    text = text.replace("\u2014\u2014", "\u2014")
    text = text.replace(" \u2014", "\u2014").replace("\u2014 ", "\u2014 ")
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\$\s+(?=\d)", "$", text)
    # OCR slips that are safe to correct globally in these books
    text = text.replace("o-f ", "of ")
    text = re.sub(r"\b1\s+(?=[a-z])", "I ", text)   # "1 really did" -> "I really did"
    text = re.sub(r"\b1\b(?=,|\s+percent)", "1", text)
    text = text.replace(" ,", ",")
    return text


# --------------------------------------------------------------------------
# Book 1: Stock Market Wizards
# --------------------------------------------------------------------------

B1_CHAPTERS = {
    2: ("h2", "Copyright"),
    4: ("h2", "Acknowledgments"),
    5: ("h2", "Prologue: An Inauspicious Beginning"),
    7: ("h2", "Stuart Walton: Back from the Abyss"),
    22: ("h2", "Michael Lauer: The Wisdom of Value, the Folly of Fad"),
    34: ("h2", "Steve Watson: Dialing for Dollars"),
    44: ("h2", "Dana Galante: Against the Current"),
    54: ("h2", "Mark D. Cook: Harvesting S&P Profits"),
    70: ("h2", 'Alphonse "Buddy" Fletcher Jr.: Win-Win Investing'),
    81: ("h2", "Ahmet Okumus: From Istanbul to Wall Street Bull"),
    91: ("h2", "Mark Minervini: Stock Around the Clock"),
    101: ("h2", "Steve Lescarbeau: The Ultimate Trading System"),
    110: ("h2", "Michael Masters: Swimming Through the Markets"),
    117: ("h2", "John Bender: Questioning the Obvious"),
    126: ("h2", "Claudio Guazzoni: Eliminating the Downside"),
    134: ("h2", "David Shaw: The Quantitative Edge"),
    144: ("h2", "Steve Cohen: The Trading Room"),
    151: ("h2", "Ari Kiev, M.D.: The Mind of a Winner"),
    156: ("h2", "Wizard Lessons"),
    170: ("h2", "Appendix: Options\u2014Understanding the Basics"),
    172: ("h2", "Index"),
}


def dedupe_lines(lines):
    """Drop OCR duplicates (a repeated line inside the same page)."""
    out = []
    for ln in lines:
        key = re.sub(r"\W+", "", ln["text"]).lower()[:70]
        dup = False
        if len(key) > 25:
            for prev in out[-8:]:
                pkey = re.sub(r"\W+", "", prev["text"]).lower()[:70]
                if pkey == key and abs(len(prev["text"]) - len(ln["text"])) < 15:
                    dup = True
                    break
        if not dup:
            out.append(ln)
    return out


def b1_page_items(page, merge_gap=45):
    """Return a list of raw lines in reading order for Stock Market Wizards."""
    lines = page_lines(page, merge_gap=merge_gap)
    h = page.rect.height
    w = page.rect.width
    split = w / 2.0
    kept = []
    for ln in lines:
        t = ln["text"].strip()
        # running heads / page numbers in the margins
        if ln["y0"] <= 52 and ln["size"] < 13:
            continue
        if is_page_number(ln) and (ln["y0"] >= h - 72 or ln["y1"] <= 52):
            continue
        if SPACED_CAPS_RE.match(t) and ln["size"] < 9.5:
            continue
        if is_page_number(ln) and ln["size"] < 8.5:
            continue
        ln["col"] = 0 if ln["x0"] < split else 1
        kept.append(ln)
    kept.sort(key=lambda l: (l["col"], round(l["y0"], 1), l["x0"]))
    return dedupe_lines(kept)


BULLET_CHARS = set(">*!\u2022\u2014\u00b7\u25aa\u25cf\u25a0^")


def strip_bullet(text):
    """Return text without the printed bullet marker, or None if not a bullet."""
    # a lone 'K' followed by a space is an OCR'd bullet in this scan
    if re.match(r"^K\s+[A-Z\"'(\[]", text):
        return text[2:]
    i = 0
    while i < len(text) and (text[i] in BULLET_CHARS or text[i] == " "):
        i += 1
    marker = text[:i].strip()
    rest = text[i:]
    if not marker or not rest:
        return None
    if not re.match(r"[A-Za-z\"'(\[]", rest):
        return None
    strong = any(ch in marker for ch in ">\u2022\u2014\u00b7\u25aa\u25cf\u25a0")
    if strong or text.startswith("* ") or len(marker) >= 2 or marker in ("^", "!"):
        return rest
    return None


def strip_marker_from_segs(segs):
    """Remove the printed bullet characters from the beginning of a paragraph."""
    out = list(segs)
    while out:
        text, bold, ital = out[0]
        i = 0
        while i < len(text) and (text[i] in BULLET_CHARS or text[i] == " "):
            i += 1
        if i == 0:
            break
        rest = text[i:]
        out[0] = (rest, bold, ital)
        if rest:
            break
        out.pop(0)
    return [s for s in out if s[0]]


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
    return values[idx]


def b1_items(page):
    """Paragraph-level items for book 1."""
    lines = b1_page_items(page)
    margins, rights, sizes = {}, {}, {}
    for col in (0, 1):
        # dominant type size of the column (pages are scanned at different scales)
        pool = [l for l in lines
                if l["col"] == col and l["size"] >= 6.0 and (l["x1"] - l["x0"]) > 90]
        if pool:
            sizes[col] = Counter(round(l["size"], 1) for l in pool).most_common(1)[0][0]
        else:
            sizes[col] = 9.9
        body = [l for l in pool
                if abs(l["size"] - sizes[col]) <= 1.2
                and not all(style_of(s["font"])[0] for s in l["spans"]
                            if s["text"].strip())]
        margins[col] = Counter(round(l["x0"] / 2) * 2 for l in body).most_common(1)
        margins[col] = margins[col][0][0] if margins[col] else None
        rights[col] = percentile([round(l["x1"]) for l in body], 0.90)

    items = []
    cur = None            # dict(kind=..., segs=[...], size=..., col=..., y1=...)
    prev = None
    for ln in lines:
        t = ln["text"].strip()
        size = ln["size"]
        is_title = size >= 13.5
        is_sub = (ln["font"].startswith("Helvetica") and 9.3 <= size <= 12.6)
        is_question = all(style_of(s["font"])[0] for s in ln["spans"]
                          if s["text"].strip())
        margin = margins.get(ln["col"])
        indent = margin is not None and (ln["x0"] - margin) > 10
        body_size = sizes.get(ln["col"]) or 9.9
        is_fn = size < body_size - 1.0
        gap = (ln["y0"] - prev["y1"]) if (prev and prev["col"] == ln["col"]) else 99
        newcol = prev is not None and prev["col"] != ln["col"]
        prev_short = True
        if prev and prev["col"] == ln["col"] and rights.get(ln["col"]):
            prev_short = prev["x1"] < rights[ln["col"]] - 14

        bullet_text = strip_bullet(t) if size >= 8.5 and not is_fn else None
        is_bullet = bullet_text is not None

        start_new = True
        if cur is not None and not newcol:
            same_font = abs(size - cur["size"]) <= 1.2
            tight = gap <= 5.0 and not indent
            if is_title or is_sub or is_bullet:
                start_new = True
            elif is_fn or cur["kind"] == "fn":
                start_new = not (cur["kind"] == "fn" and gap <= 5.0)
            elif is_question:
                start_new = not (cur["kind"] == "q" and tight)
            elif cur["kind"] == "li":
                start_new = gap > 5.5 or not same_font
            elif cur["kind"] in ("p",):
                start_new = (not tight) or prev_short or not same_font
            # a line ending in a hyphen always continues the broken word
            if (prev is not None and prev["text"].rstrip().endswith("-")
                    and cur["kind"] in ("p", "fn", "li") and not is_title):
                start_new = False

        if start_new:
            kind = "p"
            if is_title:
                kind = "title"
            elif is_sub:
                kind = "h3"
            elif is_fn:
                kind = "fn"
            elif is_question:
                kind = "q"
            elif is_bullet:
                kind = "li"
            cur = dict(kind=kind, segs=[], size=size, col=ln["col"], y1=ln["y1"],
                       text="")
            items.append(cur)
        cur["y1"] = ln["y1"]
        cur["x1"] = ln["x1"]
        segs = line_segments(ln)
        if not segs:
            continue
        if is_bullet and not cur["segs"]:
            segs = strip_marker_from_segs(segs)
            if not segs:
                prev = ln
                continue
        if cur["segs"]:
            last_text = cur["segs"][-1][0]
            merged = join_hyphen(last_text, segs[0][0])
            cur["segs"][-1] = (merged, cur["segs"][-1][1], cur["segs"][-1][2])
            for s in segs[1:]:
                cur["segs"].append(s)
        else:
            cur["segs"].extend(segs)
        cur["text"] = "".join(s[0] for s in cur["segs"])
        prev = ln
    return items


B1_DROP_COLS = {4: {0}}   # page 4: left column is the tail of the printed contents


def b1_index_items(page, only_col=None):
    """Index pages are set in several columns; order by column, keep indents."""
    lines = b1_page_items(page, merge_gap=12)
    if only_col is not None:
        lines = [l for l in lines if l["col"] == only_col]
    xs = sorted({round(l["x0"]) for l in lines})
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][1] <= 40:
            clusters[-1][1] = x
        else:
            clusters.append([x, x])

    def cidx(x):
        best = 0
        for i, (a, b) in enumerate(clusters):
            if a - 40 <= x <= b + 40:
                best = i
        return best

    lines.sort(key=lambda l: (cidx(round(l["x0"])), round(l["y0"], 1), l["x0"]))
    items = []
    for ln in lines:
        if ln["size"] >= 13:
            continue
        base = clusters[cidx(round(ln["x0"]))][0]
        kind = "li" if (round(ln["x0"]) - base) <= 4 else "lisub"
        segs = line_segments(ln)
        if not segs:
            continue
        text = "".join(s[0] for s in segs)
        if (items and items[-1]["kind"] == kind
                and items[-1]["text"].rstrip().endswith(",")
                and kind == "li"):
            items[-1]["text"] = items[-1]["text"].rstrip() + " " + text.strip()
            continue
        items.append(dict(kind=kind, segs=[(text, False, False)], col=0, text=text))
    return items


def merge_mid_sentence(items):
    """Merge paragraph pairs split by a page boundary, and wrapped headings."""
    out = []
    for it in items:
        if (out and it["kind"] == "h3" and out[-1]["kind"] == "h3"):
            prev = out[-1]
            wrapped = (
                not re.match(r"^\d+\.\s", it["text"].strip())
                and not re.search(r"[.:;?!]$", prev["text"].strip())
                and len(prev["text"].strip()) > 40
            )
            if wrapped:
                merged = prev["text"].rstrip() + " " + it["text"].lstrip()
                prev["segs"] = [(merged, False, False)]
                prev["text"] = merged
                continue
        # find the previous body paragraph, skipping footnotes in between
        idx = None
        for j in range(len(out) - 1, -1, -1):
            kind = out[j]["kind"]
            if kind in ("h3", "title", "lisub"):
                break
            if kind in ("p", "li", "q"):
                idx = j
                break
            if kind == "fn" and not re.search(r"[A-Za-z0-9,;:(\-]$",
                                              out[j]["text"].strip()):
                continue
            if kind == "fn":
                idx = j
                break
        if (it["kind"] == "p" and idx is not None
                and re.search(r"[A-Za-z0-9,;:(\-]$", out[idx]["text"].strip())
                and re.match(r"^[a-z]", it["text"].strip())):
            prev = out[idx]
            if prev["kind"] == "q":
                # a "question" that ends mid-sentence is really body text
                prev["kind"] = "p"
                prev["segs"] = [(t, False, False) for t, _, _ in prev["segs"]]
            merged = join_hyphen(prev["segs"][-1][0], it["text"].lstrip())
            prev["segs"][-1] = (merged, prev["segs"][-1][1], prev["segs"][-1][2])
            prev["segs"].extend(it["segs"][1:])
            prev["text"] = "".join(s[0] for s in prev["segs"])
            prev["y1"] = it.get("y1", prev.get("y1"))
            continue
        out.append(it)
    return out


def split_caret_items(items):
    """Bullets that the scan joined with ' ^ ' are split apart again."""
    out = []
    for it in items:
        if it["kind"] in ("p", "li") and " ^ " in it["text"]:
            parts = re.split(r"\s+\^\s+", it["text"])
            for k, part in enumerate(parts):
                kind = "li" if (k > 0 or it["kind"] == "li") else "p"
                out.append(dict(kind=kind, segs=[(part, False, False)],
                                text=part, size=it.get("size", 10.0)))
        else:
            out.append(it)
    return out


def looks_like_running_head(text):
    toks = text.split()
    if len(toks) < 4:
        return False
    short = sum(1 for w in toks if len(w.strip(".,'\"")) <= 2)
    return short / len(toks) >= 0.6


def make_title(title_items):
    """Build a chapter title out of the (possibly multi-line) title block."""
    parts = []
    for it in title_items:
        text = re.sub(r"\s+", " ", it["text"]).strip()
        if not text:
            continue
        # skip letter-spaced running heads such as "S T U A R T W A L T O N"
        if re.match(r"^(?:\S\s){3,}\S?$", text) or looks_like_running_head(text):
            continue
        if text.upper() == text:
            text = smart_title(text)
        parts.append(text.rstrip(",;"))
    if not parts:
        return None
    return " \u2014 ".join(parts)


def b1_convert(path, use_map=True):
    doc = pymupdf.open(path)
    chapters = []          # list of (title, [items])

    for page in doc:
        pn = page.number
        if use_map:
            if pn in (0, 1, 3):           # cover, title page, printed contents
                continue
        elif len(page.get_text().strip()) < 300:
            continue                      # cover / title page
        if use_map and pn == 172:         # left column: appendix tail; right: index
            std = b1_items(page)
            chapters[-1]["items"].extend([it for it in std if it["col"] == 0])
            chapters.append(dict(title="Index", items=b1_index_items(page, only_col=1),
                                 level="h2"))
            continue
        if chapters and chapters[-1]["title"] == "Index":
            chapters[-1]["items"].extend(b1_index_items(page))
            continue
        items = b1_items(page)
        if use_map and pn in B1_CHAPTERS:
            lvl, title = B1_CHAPTERS[pn]
            drop_cols = B1_DROP_COLS.get(pn, set())
            items = [it for it in items if it["col"] not in drop_cols]
            title_items = [it for it in items if it["kind"] == "title"]
            title_col = title_items[0]["col"] if title_items else 0
            body = [it for it in items if it["kind"] != "title"]
            if title_col == 1:
                left = [it for it in body if it["col"] == 0]
                right = [it for it in body if it["col"] == 1]
                if chapters:
                    chapters[-1]["items"].extend(left)
                chapters.append(dict(title=title, items=right, level=lvl))
            else:
                chapters.append(dict(title=title, items=body, level=lvl))
        else:
            title_items = [it for it in items if it["kind"] == "title"]
            body = [it for it in items if it["kind"] != "title"]
            title = make_title(title_items) if title_items else None
            if title and title.lower().startswith("contents"):
                continue                  # printed table of contents
            if title:
                title_col = title_items[0]["col"]
                if title_col == 1:
                    left = [it for it in body if it["col"] == 0]
                    right = [it for it in body if it["col"] == 1]
                    if chapters:
                        chapters[-1]["items"].extend(left)
                    chapters.append(dict(title=title, items=right, level="h2"))
                else:
                    chapters.append(dict(title=title, items=body, level="h2"))
            else:
                if not chapters:
                    chapters.append(dict(title=None, items=[], level="h2"))
                chapters[-1]["items"].extend(body)

    for ch in chapters:
        ch["items"] = split_caret_items(merge_mid_sentence(ch["items"]))
    return chapters, None


# --------------------------------------------------------------------------
# Book 2: The New Market Wizards
# --------------------------------------------------------------------------

B2_FRONT_BACK = {
    "Preface", "Acknowledgments", "Prologue", "A Personal Reflection", "Glossary",
}


def b2_page_lines(page):
    lines = page_lines(page)
    h = page.rect.height
    kept = []
    for ln in lines:
        if is_page_number(ln) and ln["size"] <= 13 and (ln["y1"] < 60 or ln["y0"] > h - 60):
            continue
        if re.search(r"_{3,}|\.{5,}", ln["text"]):
            continue                      # dotted leaders of the printed contents
        if ln["size"] < 7.5 and re.match(r"^\d+\.\s+[A-Z]", ln["text"].strip()):
            continue                      # 7pt mini contents block
        kept.append(ln)
    kept.sort(key=lambda l: (round(l["y0"], 1), l["x0"]))
    return dedupe_lines(kept)


def b2_is_heading(ln):
    fonts = [s["font"] for s in ln["spans"] if s["text"].strip()]
    return any("TimesNewRomanPS-Bold" in f for f in fonts) and ln["size"] >= 11.0


def b2_is_subheading(ln):
    t = ln["text"].strip()
    if not re.match(r"^\d+\.\s+[A-Z]", t):
        return False
    fonts = [s["font"] for s in ln["spans"] if s["text"].strip()]
    if any("BoldItalic" in f for f in fonts):
        return True
    if any("Italic" in f for f in fonts) and t.upper() == t:
        return True
    # a few headings are set in regular Verdana caps
    return t.upper() == t and len(t) < 90


def smart_title(text):
    small = {"a", "an", "the", "and", "or", "nor", "but", "of", "to", "in", "on",
             "at", "for", "by", "as", "vs", "via", "with", "from"}

    def cap(w):
        m = re.match(r"^([^\w]*)([\w'\u2019\-]*)([^\w]*)$", w)
        if not m:
            return w
        pre, core, post = m.groups()
        if not core:
            return w
        if "'" in core or "\u2019" in core:
            core = core.lower().capitalize()
        elif "-" in core:
            core = "-".join(p.lower().capitalize() if p.isalpha() else p
                            for p in core.split("-"))
        elif core.isalpha():
            core = core.lower().capitalize()
        return pre + core + post

    words = text.split(" ")
    out = []
    sentence_start = True
    for w in words:
        core = w.strip(".,:;?!")
        if (not sentence_start and core.lower() in small and core.isalpha()):
            out.append(w.lower())
        else:
            out.append(cap(w))
        sentence_start = bool(re.search(r"[.:;?!]$", w))
    return " ".join(out)


B2_COPYRIGHT = [
    "This book was originally published in 1992 by HarperBusiness, a division of "
    "HarperCollins Publishers.",
    "THE NEW MARKET WIZARDS. Copyright \u00a9 1992 by Jack D. Schwager. All rights "
    "reserved. Printed in the United States of America. No part of this book may be "
    "used or reproduced in any manner whatsoever without written permission except in "
    "the case of brief quotations embodied in critical articles and reviews. For "
    "information address HarperCollins Publishers, Inc., 10 East 53rd Street, "
    "New York, NY 10022.",
    "HarperCollins books may be purchased for educational, business, or sales "
    "promotional use. For information please write: Special Markets Department, "
    "HarperCollins Publishers, Inc., 10 East 53rd Street, New York, NY 10022.",
    "First paperback edition published 1994. Designed by Alma Hochhauser Orenstein",
    "The Library of Congress has catalogued the hardcover edition as follows: "
    "Schwager, Jack D., 1948- The new market wizards : conversations with America's "
    "top traders / Jack D. Schwager. \u2014 1st ed. \u2014 p. cm. Sequel to: Market "
    "wizards. ISBN 0-88730-587-3. 1. Floor traders (Finance)\u2014United "
    "States\u2014Interviews. 2. Futures market\u2014United States\u2014Interviews. "
    "3. Financial futures\u2014United States. I. Schwager, Jack D., 1948- . Market "
    "wizards. II. Title. HG4621.S283 1992 332.64'0973\u2014dc20 92-52612. "
    "ISBN 0-88730-667-5 (pbk.)",
]


def split_markers(lines):
    """Turn '====' into standalone marker lines, wherever they appear."""
    out = []
    for ln in lines:
        if "====" not in ln["text"]:
            out.append(ln)
            continue
        parts = ln["text"].split("====")
        for idx, part in enumerate(parts):
            if idx:
                m = dict(ln)
                m["text"] = "===="
                m["spans"] = []
                m["marker"] = True
                out.append(m)
            if part.strip():
                piece = dict(ln)
                piece["text"] = part.strip()
                base = ln["spans"][0] if ln["spans"] else {"font": "Verdana", "size": 9.0, "bbox": ln["bbox"]}
                piece["spans"] = [dict(base, text=part.strip())]
                out.append(piece)
    return out


def b2_convert(path):
    doc = pymupdf.open(path)
    sections = []
    cur = dict(title=None, level="h2", items=[])
    sections.append(cur)
    in_glossary = False
    q_open = False
    q_buf = []

    for page in doc:
        pn = page.number
        if pn == 0:                      # title page - rebuilt by hand
            continue
        if pn == 1:                      # copyright page - rebuilt by hand
            sections.append(dict(title="Copyright", level="h2",
                                 items=[dict(kind="p", segs=[(t, False, False)],
                                             text=t) for t in B2_COPYRIGHT]))
            cur = sections[-1]
            continue
        if pn == 2:                      # printed contents - regenerated
            continue
        lines = split_markers(b2_page_lines(page))
        i = 0
        pending_heading = []
        while i < len(lines):
            ln = lines[i]
            t = ln["text"].strip()

            if b2_is_heading(ln):
                if pending_heading and ln["y0"] - pending_heading[-1]["y1"] < 12:
                    pending_heading.append(ln)
                    i += 1
                    continue
                # a new chapter always starts outside a question
                if q_open:
                    q = " ".join(x for x in q_buf if x).strip().replace("**", "")
                    if q:
                        cur["items"].append(dict(kind="p", text=q,
                                                 segs=[(q, False, False)]))
                    q_open = False
                    q_buf = []
                if pending_heading:
                    _flush_heading(pending_heading, sections, cur)
                    cur = sections[-1]
                    in_glossary = cur["title"] == "Glossary"
                    pending_heading = []
                pending_heading = [ln]
                i += 1
                continue
            if pending_heading:
                _flush_heading(pending_heading, sections, cur)
                cur = sections[-1]
                in_glossary = cur["title"] == "Glossary"
                pending_heading = []

            if b2_is_subheading(ln):
                title_txt = smart_title(re.sub(r"\s{2,}", " ", t).strip())
                cur["items"].append(dict(kind="h3", text=title_txt,
                                         segs=[(title_txt, False, False)], sub=True))
                i += 1
                continue

            # question / glossary term markers
            if t == "====":
                if q_open:
                    q = " ".join(x for x in q_buf if x).strip().replace("**", "")
                    if q:
                        kind = "term" if in_glossary else "q"
                        cur["items"].append(dict(kind=kind, text=q,
                                                 segs=[(q, False, False)]))
                    q_open = False
                    q_buf = []
                else:
                    q_open = True
                    q_buf = []
                i += 1
                continue
            if q_open:
                q_buf.append(t)
                i += 1
                continue

            # normal paragraph
            items = cur["items"]
            page_lines_body = [l for l in lines if 8.0 <= l["size"] <= 10.0]
            right = percentile([round(l["x1"]) for l in page_lines_body], 0.90) or 556.0
            indent = (ln["x0"] - 52.0) > 8
            prev = items[-1] if items else None
            gap = 99
            if prev and prev.get("y1") is not None:
                gap = ln["y0"] - prev["y1"]
            segs = line_segments(ln)
            if not segs:
                i += 1
                continue

            prev_terminal = True
            prev_short = True
            if prev is not None and prev["kind"] in ("p", "li"):
                prev_text = prev["text"].rstrip()
                prev_terminal = bool(prev_text) and prev_text[-1] in ".!?\"'\u201d\u2019):"
                prev_short = (prev.get("x1", 0) < right - 20)

            same = (
                prev is not None and prev["kind"] == "p"
                and gap <= 5.0
                and (not prev_terminal or not (indent or prev_short))
                and abs(ln["size"] - prev.get("size", ln["size"])) < 1.0
            )
            if (prev is not None and prev["kind"] == "p"
                    and prev["text"].rstrip().endswith("-")):
                same = True
            if same:
                last = prev["segs"][-1][0]
                merged = join_hyphen(last, segs[0][0])
                prev["segs"][-1] = (merged, prev["segs"][-1][1], prev["segs"][-1][2])
                prev["segs"].extend(segs[1:])
                prev["text"] = "".join(s[0] for s in prev["segs"])
                prev["y1"] = ln["y1"]
                prev["x1"] = ln["x1"]
            else:
                items.append(dict(kind="p", segs=segs, size=ln["size"],
                                  y1=ln["y1"], x1=ln["x1"],
                                  text="".join(s[0] for s in segs)))
            i += 1

        if pending_heading:
            _flush_heading(pending_heading, sections, cur)
            cur = sections[-1]

        in_glossary = bool(sections) and sections[-1]["title"] == "Glossary"

    q = " ".join(x for x in q_buf if x).strip().replace("**", "")
    if q:
        cur["items"].append(dict(kind="term" if in_glossary else "q", text=q,
                                 segs=[(q, False, False)]))

    for sec in sections:
        sec["items"] = merge_mid_sentence(sec["items"])
        # some interviewer questions lost their "====" markers in this scan
        its = sec["items"]
        for k, it in enumerate(its[:-1]):
            t = it["text"].strip()
            if (it["kind"] == "p" and t.endswith("?") and len(t) <= 300
                    and its[k + 1]["kind"] == "p" and it.get("size", 9) > 8.5):
                it["kind"] = "q"
    return sections


def _flush_heading(heading_lines, sections, cur):
    text = " ".join(x["text"].strip() for x in heading_lines)
    text = re.sub(r"\s+", " ", text).strip()
    if text.startswith("PART "):
        level = "h2"
    elif text.split()[0].strip(":") in B2_FRONT_BACK or text.startswith(("Appendix", "Glossary")):
        level = "h2"
    else:
        level = "h3"
    sections.append(dict(title=text, level=level, items=[]))


# --------------------------------------------------------------------------
# Markdown assembly
# --------------------------------------------------------------------------

def paragraphs_from_items(items):
    """Yield markdown blocks (str) from a list of items."""
    out = []
    for it in items:
        kind = it["kind"]
        if kind in ("h3",):
            text = it["text"].strip()
            out.append(("#### " if it.get("sub") else "### ") + text)
        elif kind == "q":
            out.append("> **" + fix_common(it["text"]) + "**")
        elif kind == "term":
            text = fix_common(it["text"]).rstrip(".")
            out.append("**" + text + "**")
        elif kind in ("li", "lisub"):
            body = render_segments(it["segs"])
            out.append(("- " if kind == "li" else "  - ") + fix_common(body))
        elif kind == "title":
            out.append("@@TITLE@@" + it["text"])
        else:
            body = render_segments(it["segs"])
            out.append(fix_common(body))
    return out


POST_FIXES_BOTH = [
    ("th'ere", "there"),
    ("the comer", "the corner"),
    ("stem enforcer", "stern enforcer"),
]

# Word-level OCR repairs for the two scans.  Applied to the finished text;
# "r" strings are regex patterns, so \b marks word boundaries.
OCR_FIXES = [
    # --- numbers where OCR read the digit 1 as a capital I ------------------
    (r"(\$\d)\.I\s*(billion|million|trillion|thousand|percent)\b", r"\1.1 \2"),
    (r"(\d)\.I\b(?=\s*[A-Za-z])", r"\1. I"),
    (r"\$I\b", "$1"),
    (r"\bI percent\b", "1 percent"),
    # --- Stock Market Wizards ---------------------------------------------
    (r"\bwaitfing\]", "waiting"),
    (r"\btolcl\b", "told"),
    (r"\bcoulcl\b", "could"),
    (r"\bovercompensatecl\b", "overcompensated"),
    (r"\bBobsledcling\b", "Bobsledding"),
    (r"\bsendees\b", "services"),
    (r"\bnexi\b", "next"),
    (r"\bmalting that phone call\b", "making that phone call"),
    (r"\blour or live years\b", "four or five years"),
    (r"\bapproach lor achieving\b", "approach for achieving"),
    (r"\ba lortune in their own company\b", "a fortune in their own company"),
    (r"\bthank Cod\b", "thank God"),
    (r"\bin vestors in the fund\b", "investors in the fund"),
    (r"\bpermits the in vestor\b", "permits the investor"),
    (r"\bmuch ol anything\b", "much of anything"),
    (r"\bhis with drawals\b", "his withdrawals"),
    (r"\bincoq\^orates\b", "incorporates"),
    (r"\bWTien\b", "When"),
    (r"TraJiMg to Ww, \(kg Psychology of Mostcrmg tbc Markets",
     "Trading to Win: The Psychology of Mastering the Markets"),
    (r"TraJiwg iw the Zone", "Trading in the Zone"),
    (r"\bThcSlreet\.com\b", "TheStreet.com"),
    (r"\bSlock Market Logic\b", "Stock Market Logic"),
    (r"Sjrperper/ormtiMce Sfocfa \(Love\),!71",
     "Superperformance Stocks (Love), 171"),
    (r"\bScholcs\b", "Scholes"),
    (r"\bRouwcnhort\b", "Rouwenhorst"),
    (r"\bLiz Claibornc\b", "Liz Claiborne"),
    (r"\bFlere, the catalyst\b", "Here, the catalyst"),
    (r"\bPro\?\.ac\b", "Prozac"),
    (r"the Far Bast\b", "the Far East"),
    (r"a shan, dote rally", "a sharp, volatile rally"),
    (r"Gutfreund and me firm", "Gutfreund and the firm"),
    (r"known as me theme", "known as the theme"),
    (r"into avoiding\.my potent", "into avoiding a potent"),
    (r"in a few days-nme", "in a few days' time"),
    (r"start of fall employment", "start of full employment"),
    (r"Elliot! Wave", "Elliott Wave"),
    (r"\bhold tme\b", "hold true"),
    (r"\bmodem-day\b", "modern-day"),
    (r"\ba very lage dollar position\b", "a very large dollar position"),
    (r"sufficient liquid, y to ex, the position",
     "sufficient liquidity to exit the position"),
    (r"the dollar wa weaker", "the dollar was weaker"),
    (r"as disci-D •'\n\nplined as I should be\.",
     "as disciplined as I should be."),
    (r"hardworking, and\n\n\^Pseudonym\n\ndisciplined\.",
     "hardworking, and disciplined."),
    (r"whether I he catalyst s t i l l applies\. I'or example",
     "whether the catalyst still applies. For example"),
    (r"he would l a l i\.", "he would fall."),
    (r"one after die other", "one after the other"),
    (r"add die stipulation", "add the stipulation"),
    (r"defy die laws", "defy the laws"),
    (r"\bYork I\? Institute of Finance", "York Institute of Finance"),
    (r"\bby by the conscious mind", "by the conscious mind"),
    (r"phenomenal\u2014-a complete blowout", "phenomenal\u2014a complete blowout"),
    (r"\blick indicators, 107-1 1", "tick indicators, 107-11"),
    (r"9-10, 1 10-1 1", "9-10, 110-11"),
    (r"U\.S\., I l l, 118", "U.S., 111, 118"),
    (r"in the bro-You just unilaterally lowered commissions\?"
     r" kerage industry\.(.*?)\n\n",
     "in the brokerage industry.\\1\n\n"
     "> **You just unilaterally lowered commissions?**\n\n"),
    # --- The New Market Wizards -------------------------------------------
    (r"\bmtuitively\b", "intuitively"),
    (r"\bmshing in\b", "rushing in"),
    (r"feet above the mnway\b", "feet above the runway"),
    (r"\btakeover mmor\b", "takeover rumor"),
    (r"139-monm track record", "139-month track record"),
    (r"\bnianager\b", "manager"),
    (r"hit the naii on the head", "hit the nail on the head"),
    (r"\binstmment\b", "instrument"),
    (r"\binstmctor\b", "instructor"),
    (r"\bA fmal analogy\b", "A final analogy"),
    (r"\bto fmition\b", "to fruition"),
    (r"\bshort a ftmd\b", "short a fund"),
    (r"\blimit to the amoiint\b", "limit to the amount"),
    (r"\bahnost as if\b", "almost as if"),
    (r"\balarmmg regularity\b", "alarming regularity"),
    (r"\bpmdent investors\b", "prudent investors"),
    (r"\bfelt phenomonally good\b", "felt phenomenally good"),
    (r"answered with scom in his voice", "answered with scorn in his voice"),
    (r"with greater scmtiny", "with greater scrutiny"),
    (r"\bsystcmatizing\b", "systematizing"),
    (r"\battain tmly superior\b", "attain truly superior"),
    (r"\btfiat I had\b", "that I had"),
    (r"\bteli whether\b", "tell whether"),
    (r"\bchanged trom the basic\b", "changed from the basic"),
    (r"\ba stocJc portfolio\b", "a stock portfolio"),
    (r"\bslighdy\b", "slightly"),
    (r"\busefiil\b", "useful"),
    (r"\btruthfalness\b", "truthfulness"),
    (r"\bunrealisncally\b", "unrealistically"),
    (r"\bunweildly\b", "unwieldy"),
    (r"\brecoupingmost\b", "recouping most"),
    (r"\bbuy-and nold\b", "buy-and-hold"),
    (r"pure fundamental ists\b", "pure fundamentalists"),
    (r"\blopes\b|\blypes\b", "types"),
    (r"\binteriewed\b", "interviewed"),
    (r"\bhmchtime\b", "lunchtime"),
    (r"\bTeff Yass\b", "Jeff Yass"),
    (r"\bHverything\b", "Everything"),
    (r"\bBvery effort\b", "Every effort"),
    (r"\bread Ehe Appendix\b", "read the Appendix"),
    (r"\bEIliott\b", "Elliott"),
    (r"\bDeufsche\b", "Deutsche"),
    (r"\bother major Grms\b", "other major firms"),
    (r"\band JAJlis enthusiasm\b", "and his enthusiasm"),
    (r"\bIfX, Y, or Z\b", "If X, Y, or Z"),
    (r"\bDennises approach\b", "Dennis's approach"),
    (r"\brepre sents\b", "represents"),
    (r"\bat Comell\b", "at Cornell"),
    (r"U\.S\. Surgical \[USSj", "U.S. Surgical [USS]"),
    (r"Blockbuster Entertainment \[BVj", "Blockbuster Entertainment [BV]"),    (r"\bTewles\b", "Teweles"),
    (r"\bCamaby Street\b", "Carnaby Street"),
    (r"Crown Zeilerbach", "Crown Zellerbach"),
    (r"\bToghiaie\b", "Toghraie"),
    (r"classical chart analysis, Ganri,", "classical chart analysis, Gann,"),
    (r"\bwas that\. atter more than four years\b", "was that after more than four years"),
    (r"\bagiuns simultaneously\b", "against simultaneously"),
    (r"\bin each caseJt worked\b", "in each case it worked"),
    (r"terms fwnesty and integrity", "terms of honesty and integrity"),
    (r"seminar mn by Dr\. Van Tharp", "seminar run by Dr. Van Tharp"),
    (r"\bhid/ask spread\b", "bid/ask spread"),
    # --- pojedyncze miejsca, w ktorych skan poprzestawial kolumny ----------
    (r"The very need to win a stem master that seldom tolerates the carelessness "
     r"associated with trades born of desperation\.\n\npoisoned the trade-m this "
     r"instance, through grossly excessive leverage and a lack of planning\. "
     r"The market is",
     "The very need to win poisoned the trade\u2014in this instance, through grossly "
     "excessive leverage and a lack of planning. The market is a stern master that "
     "seldom tolerates the carelessness associated with trades born of desperation."),
    (r"endure periodic losses\n\n5\. Recognize and control your greed\.\n\n"
     r"in open profits greater than the risk level that would be advisable when a "
     r"position is first implemented\.",
     "endure periodic losses in open profits greater than the risk level that would "
     "be advisable when a position is first implemented.\n\n"
     "5. Recognize and control your greed."),
    (r"beware of acting on the obvious\.\n\nthe trading-related references in this "
     r"chapter\.//\n\n//\\\*\\\*Note:\\\*\\\*// //Readers unfamiliar with options may "
     r"wish to read the Appendix in order to understand",
     "beware of acting on the obvious.\n\n//\\*\\*Note:\\*\\*// //Readers unfamiliar "
     "with options may wish to read the Appendix in order to understand the "
     "trading-related references in this chapter.//"),
    (r"I told him that I was quite interested in his work because it Note: ID several "
     r"instances in this interview, where I thought iE would help clarify or expand "
     r"the information, I supplemented Faulkner's responses with adapted excerpts "
     r"from the Nightingale-Conant tape series NLP: The New Technology of "
     r"Achievement NLP, for which Faulkner was the program designer and principal "
     r"coauthor\.\n\nmight fit as a feature in the new book but that my scheduling on "
     r"that trip did not leave enough time for an interview\. He gave me a boxed "
     r"tape set, asking me to see what I thought about it\.",
     "I told him that I was quite interested in his work because it might fit as a "
     "feature in the new book but that my scheduling on that trip did not leave "
     "enough time for an interview. He gave me a boxed tape set, asking me to see "
     "what I thought about it.\n\n**Note:** In several instances in this interview, "
     "where I thought it would help clarify or expand the information, I "
     "supplemented Faulkner's responses with adapted excerpts from the "
     "Nightingale-Conant tape series *NLP: The New Technology of Achievement*, for "
     "which Faulkner was the program designer and principal coauthor."),
    (r"The trick is that people who volunteer to go of individuals who like to "
     r"perform in public\. pie who want to show off-closet showbiz calling\. "
     r"Hypnosis merely brings out these bypassing the behavioral controls enforced "
     r"It's virtually impossible to get a naturally shy on stage\.\n\nup on stage "
     r"are the type Typically, they are peo-types who missed their natural "
     r"inclinations by the conscious mind\. person to do silly things",
     "The trick is that people who volunteer to go up on stage are the type of "
     "individuals who like to perform in public. Typically, they are people who "
     "want to show off\u2014closet showbiz calling. Hypnosis merely brings out "
     "these tendencies, bypassing the behavioral controls enforced by the conscious "
     "mind. It's virtually impossible to get a naturally shy person to do silly "
     "things on stage."),
    (r"\bOku-mus\b", "Okumus"),
    (r"\bStrau-ss\b", "Strauss"),
    (r"lose the entire investment in any other\n\n!\n\nprice scenario\.\] I bought",
     "lose the entire investment in any other price scenario.] I bought"),
    (r"cannot be used lo\n\npredict future prices", "cannot be used to predict future prices"),
    (r"The grocery owner chased us out of his\n\nWhen did you make the transition "
     r"from a broker to a fund man-store, swinging a big loaf of bread at us, and "
     r"yelling, \"I don't want to\n\n> \*\*ager\?\*\*\n\ntalk to you brokers\. "
     r"Get out of here!\" \*\[He laughs lengthily at the recollection\.\]\*",
     "The grocery owner chased us out of his store, swinging a big loaf of bread at "
     "us, and yelling, \"I don't want to talk to you brokers. Get out of here!\" "
     "*[He laughs lengthily at the recollection.]*\n\n"
     "> **When did you make the transition from a broker to a fund manager?**"),
    (r"\[USSj", "[USS]"),
    (r"\[BVj", "[BV]"),
    (r"the market's last gasp, it will", "the market's last gasp; it will"),
    (r"\bTelt Overture\b", "Tell Overture"),
    (r"\bZwieg\b", "Zweig"),
]


def fix_index_numbers(text):
    """Page numbers in the printed index were OCR'd with stray characters."""
    i = text.find("## Index")
    if i < 0:
        return text
    head, idx = text[:i], text[i:]
    idx = re.sub(r"(?<=[ ,])([!\]i])(\d{2,3})\b", r"1\2", idx)
    idx = re.sub(r"\b([1i]) (\d{2,3})\b", r"1\2", idx)
    return head + idx


def apply_ocr_fixes(text, stats=None):
    for pat, rep in OCR_FIXES:
        text, n = re.subn(pat, rep, text)
        if stats is not None and n:
            stats.append((pat, n))
    return text

POST_FIXES_B1 = [
    ("peak Of his", "peak of his"),
    ("one of the. most", "one of the most"),
    ("lelt", "left"),
    ("tben", "then"),
    ("quicldy", "quickly"),
    ("ancl", "and"),
    ("Mas Nothing", "Has Nothing"),
    ("tbe fundamentals", "the fundamentals"),
    ("WTiat", "What"),
    ("expecled", "expected"),
    ("slock", "stock"),
    ("comlortable", "comfortable"),
    ("differenct", "difference"),
    ("timc", "time"),
    ("fourlecn-hour", "fourteen-hour"),
    ("die other", "the other"),
    ("die stipulation", "the stipulation"),
    ("die laws", "the laws"),
    ("OkumilS", "Okumus"),
    ("Rouwenhort", "Rouwenhorst"),
    ("the lacker", "the kicker"),
    ("Designed lay", "Designed by"),
]

POST_FIXES_B2 = [
    ("leam", "learn"),
    ("mnning", "running"),
    ("cmde", "crude"),
    ("thmg", "thing"),
    ("tewnty", "twenty"),
    ("shaiply", "sharply"),
    ("befors", "before"),
    ("cuirency", "currency"),
    ("reasoos", "reasons"),
    ("ssee", "see"),
    ("jnst", "just"),
    ("retnrns", "returns"),
    ("worksy they", "works, they"),
    ("cmsh", "cash"),
    ("cmst", "cost"),
    ("ftoor", "floor"),
    ("hunded", "hundred"),
    ("mnner", "runner"),
    ("siress", "stress"),
    ("optipn", "option"),
    ("overconcem", "overconcern"),
    ("rerference", "reference"),
    ("mnaway", "runaway"),
    ("plummeling", "plummeting"),
    ("Gutfreuod", "Gutfreund"),
    ("Seykola", "Seykota"),
    ("AlWeiss", "Al Weiss"),
    ("JeffGrable", "Jeff Grable"),
    ("fundamentatist", "fundamentalist"),
    ("holds tme", "holds true"),
    ("strained comec ure", "strained conjecture"),
    ("Modem-day", "modern-day"),
    ("Tolookfor", "to Look For"),
    ('it is us. "', 'it is us."'),
    ('"Pogo, "', '"Pogo,"'),
    ("$I trillion", "$1 trillion"),
    ("Getting hack to", "Getting back to"),
    ("hi come fifty", "In come fifty"),
    ("off the floor", "off the floor"),
]


def apply_fixes(text, fixes):
    for a, b in fixes:
        text = text.replace(a, b)
    return text


def fix_hi(text):
    """OCR reads 'in' as 'hi' in these scans."""
    def repl(m):
        start = m.start()
        before = text[max(0, start - 2):start]
        if start == 0 or re.search(r"[.!?]\s*$", before) or before.endswith("\n"):
            return "In"
        return "in"

    return re.sub(r"\bhi\b", repl, text)


def slug(text):
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip())
    s = re.sub(r"-{2,}", "-", s)
    return s


def build_book1(path, use_map=True, meta=None):
    chapters, _ = b1_convert(path, use_map=use_map)
    fixes = POST_FIXES_BOTH + POST_FIXES_B1
    meta = meta or DEFAULT_META[1]
    lines = [f"# {meta['title']}"]
    if meta.get("subtitle"):
        lines += ["", f"*{meta['subtitle']}*"]
    if meta.get("author"):
        lines += ["", f"**{meta['author']}**"]
    if meta.get("imprint"):
        lines += ["", f"> {meta['imprint']}"]
    lines.append("")

    toc = []
    for ch in chapters:
        if ch["title"]:
            title = apply_fixes(ch["title"], fixes)
            toc.append(f"- [{title}](#{slug(title)})")
    lines.append("## Contents")
    lines.append("")
    lines.extend(toc)
    lines.append("")

    for ch in chapters:
        blocks = paragraphs_from_items(ch["items"])
        if ch["title"]:
            lines.append("## " + apply_fixes(ch["title"], fixes))
            lines.append("")
        num = 0
        for b in blocks:
            if b.startswith("@@TITLE@@"):
                continue
            if re.match(r"^### \d+\.\s", b):
                num += 1
                b = re.sub(r"^### \d+\.\s", "### %d. " % num, b)
            lines.append(apply_fixes(b, fixes))
            lines.append("")
    md = "\n".join(lines)
    md = fix_index_numbers(md)
    stats = []
    md = apply_ocr_fixes(md, stats)
    if os.environ.get("PDF2MD_STATS"):
        print("ocr fixes:", sum(n for _, n in stats), "replacements")
        for pat, n in stats:
            print(f"   {n:3d}  {pat}")
    return md


def build_book2(path, meta=None):
    sections = b2_convert(path)
    fixes = POST_FIXES_BOTH + POST_FIXES_B2
    meta = meta or DEFAULT_META[2]
    lines = [f"# {meta['title']}"]
    if meta.get("subtitle"):
        lines += ["", f"*{meta['subtitle']}*"]
    if meta.get("author"):
        lines += ["", f"**{meta['author']}**"]
    if meta.get("imprint"):
        lines += ["", f"> {meta['imprint']}"]
    lines.append("")
    toc = []
    for sec in sections:
        if sec["title"]:
            toc.append((sec["level"], apply_fixes(sec["title"], fixes)))
    lines.append("## Contents")
    lines.append("")
    for lvl, title in toc:
        indent = "" if lvl == "h2" else "  "
        lines.append(f"{indent}- [{title}](#{slug(title)})")
    lines.append("")

    for sec in sections:
        blocks = paragraphs_from_items(sec["items"])
        if sec["title"]:
            level = "##" if sec["level"] == "h2" else "###"
            lines.append(level + " " + apply_fixes(sec["title"], fixes))
            lines.append("")
        num = 0
        for b in blocks:
            if re.match(r"^#### \d+\.\s", b):
                num += 1
                b = re.sub(r"^#### \d+\.\s", "#### %d. " % num, b)
            lines.append(apply_fixes(b, fixes))
            lines.append("")
    md = "\n".join(lines)
    md = fix_hi(md)
    stats = []
    md = apply_ocr_fixes(md, stats)
    if os.environ.get("PDF2MD_STATS"):
        print("ocr fixes:", sum(n for _, n in stats), "replacements")
        for pat, n in stats:
            print(f"   {n:3d}  {pat}")
    return md


DEFAULT_META = {
    1: dict(title="Stock Market Wizards",
            subtitle="Interviews with America's Top Stock Traders",
            author="Jack D. Schwager",
            imprint="HarperBusiness \u2014 An Imprint of HarperCollins Publishers, 2001"),
    2: dict(title="The New Market Wizards",
            subtitle="Conversations with America's Top Traders",
            author="Jack D. Schwager",
            imprint="HarperBusiness, 1992 (first paperback edition 1994)"),
}


def detect_style(doc):
    """1 = Finereader-style scan (two columns, running heads), 2 = '====' markers."""
    markers = 0
    for page in doc:
        markers += page.get_text().count("====")
    return 2 if markers > 50 else 1


KNOWN_BOOKS = {
    1: ("Stock Market Wizards", 177),
    2: ("The New Market Wizards", 190),
}


def main(argv):
    ap = argparse.ArgumentParser(
        description="Convert a scanned/text PDF book into Markdown.")
    ap.add_argument("pdf", help="input PDF")
    ap.add_argument("-o", "--output", help="output .md (default: next to the PDF)")
    ap.add_argument("--style", choices=["auto", "1", "2"], default="auto",
                    help="layout style: 1 = two-column OCR scan, 2 = '====' markers")
    ap.add_argument("--no-map", action="store_true",
                    help="ignore the built-in chapter map (needed for other books)")
    ap.add_argument("--title", help="book title override")
    args = ap.parse_args(argv)

    path = os.path.abspath(args.pdf)
    out = args.output or os.path.splitext(path)[0] + ".md"
    doc = pymupdf.open(path)
    style = detect_style(doc)
    if args.style != "auto":
        style = int(args.style)
    frag, pages = KNOWN_BOOKS[style]
    known = frag in os.path.basename(path) and doc.page_count == pages
    use_map = known and not args.no_map
    meta = dict(DEFAULT_META[style])
    if args.title:
        meta["title"] = args.title
    elif not known:
        meta["title"] = os.path.splitext(os.path.basename(path))[0]
        meta["subtitle"] = ""
        meta["author"] = doc.metadata.get("author") or ""
        meta["imprint"] = ""
    doc.close()

    if style == 1:
        md = build_book1(path, use_map=use_map, meta=meta)
    else:
        md = build_book2(path, meta=meta)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"{out}: {len(md.split())} words")


if __name__ == "__main__":
    main(sys.argv[1:])
