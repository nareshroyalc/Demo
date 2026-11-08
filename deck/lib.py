"""Shared helpers for the webinar deck: colours, text, shapes, cards, tables, code boxes, flows, footers."""
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

NAVY, BLUE, LIGHT, PALE, SKY = "0B1F3A", "0066CC", "F1F6FC", "E6F0FA", "BBD6F3"
INK, MUTED, GREYLINE, WHITE, GREYFILL = "1A2433", "5B6B7F", "C9D2DF", "FFFFFF", "F3F5F8"
AMBER, AMBER_FILL, AMBER_INK = "E39A00", "FFF4DC", "7A4B00"
GREEN, GREEN_FILL, RED, RED_FILL = "1E8E5A", "E3F4EC", "C0392B", "FBE9E7"
CODE_BG, CODE_INK, CODE_NOTE = "0F2A4D", "E8F0FA", "8FB4E3"
FONT, MONO = "Calibri", "Consolas"
LEFT, CENTER, RIGHT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MIDDLE = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE
FOOTER = "VIT-AP  |  From zero to deployed AI agents"


def rgb(h):
    return RGBColor.from_string(h)


def set_text(shape, paras, align=CENTER, anchor=MIDDLE, margins=(0.1, 0.05, 0.1, 0.05), gap=0):
    """paras: list of (text, size, bold, hex[, font]). gap = space after each paragraph (pt)."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (Inches(m) for m in margins)
    for i, para in enumerate(paras):
        text, size, bold, color = para[:4]
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if gap:
            p.space_after = Pt(gap)
        r = p.add_run()
        r.text = text
        r.font.size, r.font.bold = Pt(size), bold
        r.font.name = para[4] if len(para) > 4 else FONT
        r.font.color.rgb = rgb(color)


def text(slide, name, x, y, w, h, paras, align=LEFT, anchor=TOP, margins=(0, 0, 0, 0), gap=0):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    set_text(s, paras, align, anchor, margins, gap)
    return s


def bullets(slide, name, x, y, w, h, items, size=16, color=INK, gap=8, bold_first=False):
    """Real bullet paragraphs (hanging indent). Items may be 'text' or ('bold lead', 'rest')."""
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Inches(0.28)))
        pPr.set("indent", str(-Inches(0.28)))
        bf = etree.SubElement(pPr, qn("a:buFont"))
        bf.set("typeface", "Arial")
        bc = etree.SubElement(pPr, qn("a:buChar"))
        bc.set("char", "•")
        parts = it if isinstance(it, tuple) else (it,)
        for j, part in enumerate(parts):
            r = p.add_run()
            r.text = (part if j == 0 else " " + part)
            r.font.size, r.font.name = Pt(size), FONT
            r.font.bold = isinstance(it, tuple) and j == 0
            r.font.color.rgb = rgb(color)
    return s


def box(slide, name, x, y, w, h, paras, fill=WHITE, border=None, border_w=1.5, dash=False,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18, align=CENTER, anchor=MIDDLE, margins=(0.1, 0.05, 0.1, 0.05), gap=0):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    if border:
        s.line.color.rgb = rgb(border)
        s.line.width = Pt(border_w)
        if dash:
            s.line.dash_style = MSO_LINE.DASH
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if paras:
        set_text(s, paras, align, anchor, margins, gap)
    return s


def arrow(slide, name, x1, y1, x2, y2, color=MUTED, width=1.75, dash=False, head=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    if head:
        tail = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
    return c


def card(slide, name, x, y, w, h, heading, body, fill=PALE, hcolor=BLUE, hsize=16, bsize=14, border=None, radius=0.08,
         anchor=TOP, align=LEFT, margins=(0.22, 0.14, 0.22, 0.12)):
    paras = [(heading, hsize, True, hcolor)] if heading else []
    for line in ([body] if isinstance(body, str) else body):
        paras.append((line, bsize, False, INK))
    return box(slide, name, x, y, w, h, paras, fill=fill, border=border, radius=radius, align=align, anchor=anchor,
               margins=margins, gap=4)


def example(slide, x, y, w, h, body, label="Real-life example", bsize=16):
    return card(slide, "Example card", x, y, w, h, label.upper(), body, fill=PALE, hsize=12, bsize=bsize)


def pill(slide, name, x, y, w, h, label, fill=PALE, color=BLUE, size=13, border=None):
    return box(slide, name, x, y, w, h, [(label, size, True, color)], fill=fill, border=border, radius=0.5, margins=(0.08, 0.02, 0.08, 0.02))


def num(slide, x, y, n, d=0.5, fill=BLUE, color=WHITE, size=18):
    return box(slide, f"Step number {n}", x, y, d, d, [(str(n), size, True, color)], fill=fill, shape=MSO_SHAPE.OVAL, margins=(0, 0, 0, 0))


def stat(slide, name, x, y, w, big, small, color=BLUE, big_size=40):
    return text(slide, name, x, y, w, 1.2, [(big, big_size, True, color), (small, 14, False, MUTED)], align=LEFT, gap=0)


def code(slide, name, x, y, w, h, body, size=13):
    paras = []
    for line in body.split("\n"):
        note = line.strip().startswith("#")
        paras.append((line if line else " ", size, False, CODE_NOTE if note else CODE_INK, MONO))
    return box(slide, name, x, y, w, h, paras, fill=CODE_BG, radius=0.04, align=LEFT, anchor=TOP, margins=(0.22, 0.16, 0.2, 0.1))


def table(slide, name, x, y, widths, rows, size=14, row_h=0.5, header_fill=BLUE, first_col_bold=True):
    shp = slide.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * len(rows)))
    shp.name = name
    tbl = shp.table
    for i, w in enumerate(widths):
        tbl.columns[i].width = Inches(w)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(row_h)
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(header_fill if r == 0 else (WHITE if r % 2 else LIGHT))
            cell.vertical_anchor = MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.12)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size, run.font.name = Pt(size), FONT
            run.font.bold = r == 0 or (c == 0 and first_col_bold)
            run.font.color.rgb = rgb(WHITE if r == 0 else INK)
    return shp


def flow(slide, name, x, y, w, h, items, gap=0.38, fills=None, borders=None, tsize=14, dsize=12, arrow_color=MUTED, dash=False):
    """Horizontal boxes joined by arrows. items: (title, detail)."""
    n = len(items)
    bw = (w - gap * (n - 1)) / n
    out = []
    for i, (t, d) in enumerate(items):
        fill = (fills or [WHITE] * n)[i]
        border = (borders or [BLUE] * n)[i]
        paras = [(t, tsize, True, WHITE if fill in (BLUE, NAVY) else INK)]
        if d:
            paras.append((d, dsize, False, "DCE9F8" if fill in (BLUE, NAVY) else MUTED))
        bx = x + i * (bw + gap)
        out.append(box(slide, f"{name} {i + 1}", bx, y, bw, h, paras, fill=fill, border=border, radius=0.14, dash=dash))
        if i < n - 1:
            arrow(slide, f"{name} arrow {i + 1}", bx + bw, y + h / 2, bx + bw + gap, y + h / 2, color=arrow_color, dash=dash)
    return out


def bracket(slide, name, x1, x2, y, drop=0.35, color=BLUE, width=2.25):
    """A U-shaped link under two words."""
    arrow(slide, f"{name} left", x1, y, x1, y + drop, color=color, width=width, head=False)
    arrow(slide, f"{name} base", x1, y + drop, x2, y + drop, color=color, width=width, head=False)
    arrow(slide, f"{name} right", x2, y + drop, x2, y, color=color, width=width, head=False)


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.L_TITLE, self.L_TITLE_ONLY = self.prs.slide_layouts[0], self.prs.slide_layouts[5]

    def slide(self, title, section, say, tag=None, footer=True):
        """A content slide: section label, 36pt title, optional BUILT/CONCEPT/NEXT chip, footer, speaker notes."""
        s = self.prs.slides.add_slide(self.L_TITLE_ONLY)
        t = s.shapes.title
        t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.46), Inches(10.6), Inches(0.8)
        tf = t.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MIDDLE
        tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.alignment = LEFT
        r = p.add_run()
        r.text = title
        r.font.size, r.font.bold, r.font.name = Pt(36), True, FONT
        r.font.color.rgb = rgb(NAVY)
        text(s, "Section label", 0.6, 0.2, 8.0, 0.28, [(section.upper(), 12, True, BLUE)])
        if tag:
            kinds = {"BUILT": (BLUE, WHITE, None, False), "CONCEPT": (GREYFILL, MUTED, GREYLINE, False),
                     "NEXT": (AMBER_FILL, AMBER_INK, AMBER, True)}
            fill, col, border, dash = kinds[tag]
            box(s, f"Tag: {tag}", 11.4, 0.55, 1.35, 0.38, [(tag, 12, True, col)], fill=fill, border=border, dash=dash, radius=0.4,
                margins=(0.05, 0, 0.05, 0))
        if footer:
            text(s, "Footer", 0.6, 7.12, 8.0, 0.28, [(FOOTER, 10, False, MUTED)])
            num_box = s.shapes.add_textbox(Inches(11.7), Inches(7.12), Inches(1.03), Inches(0.28))
            num_box.name = "Slide number"
            pp = num_box.text_frame.paragraphs[0]
            pp.alignment = RIGHT
            fld = etree.SubElement(pp._p, qn("a:fld"))
            fld.set("id", "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}")
            fld.set("type", "slidenum")
            rpr = etree.SubElement(fld, qn("a:rPr"))
            rpr.set("lang", "en-US")
            rpr.set("sz", "1000")
            sf = etree.SubElement(rpr, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr")).set("val", MUTED)
            etree.SubElement(fld, qn("a:t")).text = "‹#›"
        s.notes_slide.notes_text_frame.text = say
        return s
