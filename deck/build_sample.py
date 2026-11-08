"""Build the 3-slide SAMPLE of the webinar deck (title, agent = LLM + harness, architecture).

Run:  python deck/build_sample.py      -> deck/Brightline_Webinar_SAMPLE.pptx

All visuals are native, editable PowerPoint shapes (no downloaded images). Fonts: Calibri.
Palette: navy 0B1F3A (dark slides), blue 0066CC (main), light blue F1F6FC, amber for "NEXT" items.
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "Brightline_Webinar_SAMPLE.pptx"

NAVY, BLUE, LIGHT, PALE = "0B1F3A", "0066CC", "F1F6FC", "E6F0FA"
INK, MUTED, GREYLINE, WHITE = "1A2433", "5B6B7F", "C9D2DF", "FFFFFF"
AMBER, AMBER_FILL, AMBER_INK = "E39A00", "FFF4DC", "7A4B00"
FONT = "Calibri"


def rgb(h):
    return RGBColor.from_string(h)


def set_text(shape, paras, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margins=(0.1, 0.05, 0.1, 0.05)):
    """paras: list of (text, size_pt, bold, hex_color)."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (Inches(m) for m in margins)
    for i, (text, size, bold, color) in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = text
        r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
        r.font.color.rgb = rgb(color)


def box(slide, name, x, y, w, h, paras, fill=WHITE, border=None, border_w=1.5, dash=False,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
        margins=(0.1, 0.05, 0.1, 0.05)):
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
        set_text(s, paras, align, anchor, margins)
    return s


def arrow(slide, name, x1, y1, x2, y2, color=MUTED, width=1.75, dash=False, head=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    if head:
        tail = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))  # arrow head at the end point
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
    return c


def title(slide, text, color=NAVY, size=40):
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.85)
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.name = Pt(size), True, FONT
    r.font.color.rgb = rgb(color)
    return t


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
L_TITLE, L_TITLE_ONLY = prs.slide_layouts[0], prs.slide_layouts[5]

# =========================================================================== slide 1: title (dark)
s = prs.slides.add_slide(L_TITLE)
s.background.fill.solid()
s.background.fill.fore_color.rgb = rgb(NAVY)

tag = s.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(6.2), Inches(0.4))
tag.name = "Tag"
set_text(tag, [("WEBINAR FOR STUDENTS", 14, True, "7FB2EA")], align=PP_ALIGN.LEFT, margins=(0, 0, 0, 0))

t = s.shapes.title
t.left, t.top, t.width, t.height = Inches(0.8), Inches(2.5), Inches(6.3), Inches(1.75)
tf = t.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.TOP
tf.margin_left = tf.margin_right = 0
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
r = p.add_run()
r.text = "From zero to deployed AI agents"
r.font.size, r.font.bold, r.font.name = Pt(48), True, FONT
r.font.color.rgb = rgb(WHITE)

sub = s.placeholders[1]
sub.left, sub.top, sub.width, sub.height = Inches(0.8), Inches(4.4), Inches(6.1), Inches(1.2)
set_text(sub, [("How modern AI works, and how we built one that answers from documents and a database.", 20, False, "CFE0F5")],
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0))

# illustration: PDFs + database -> AI agent -> answer
doc = box(s, "Illustration: PDF", 7.6, 1.55, 1.5, 1.95, [], fill=WHITE, shape=MSO_SHAPE.FOLDED_CORNER)
for i, wd in enumerate((1.0, 1.0, 0.7, 1.0, 0.8)):
    box(s, f"Illustration: PDF line {i + 1}", 7.85, 1.95 + i * 0.3, wd, 0.1, [], fill=GREYLINE, shape=MSO_SHAPE.RECTANGLE)
lbl = s.shapes.add_textbox(Inches(7.2), Inches(3.6), Inches(2.3), Inches(0.4))
lbl.name = "Label: PDFs"
set_text(lbl, [("5 policy PDFs", 14, False, "CFE0F5")], margins=(0, 0, 0, 0))

box(s, "Illustration: database", 7.65, 4.5, 1.4, 1.6, [], fill=WHITE, shape=MSO_SHAPE.CAN)
lbl = s.shapes.add_textbox(Inches(7.2), Inches(6.2), Inches(2.3), Inches(0.4))
lbl.name = "Label: database"
set_text(lbl, [("Sales database", 14, False, "CFE0F5")], margins=(0, 0, 0, 0))

box(s, "Illustration: AI agent", 10.0, 3.0, 1.9, 1.9, [("AI", 28, True, WHITE), ("agent", 16, False, WHITE)],
    fill=BLUE, shape=MSO_SHAPE.OVAL)
box(s, "Illustration: answer", 10.0, 5.55, 2.8, 0.95, [("Answer with sources", 16, True, NAVY)],
    fill=WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT)
arrow(s, "Arrow: PDFs to agent", 9.2, 2.6, 10.1, 3.45, color="7FB2EA", width=2.25)
arrow(s, "Arrow: database to agent", 9.15, 5.2, 10.1, 4.5, color="7FB2EA", width=2.25)
arrow(s, "Arrow: agent to answer", 10.95, 4.95, 10.95, 5.5, color="7FB2EA", width=2.25)

notes(s, "Welcome. By the end of this session you will understand the words you hear all the time: LLM, RAG, agent and MCP. "
         "You will also see one working example from start to finish: an agent that reads policy PDFs and a database to answer one question.")

# =========================================================================== slide 2: agent = LLM + harness
s = prs.slides.add_slide(L_TITLE_ONLY)
title(s, "Agent = LLM + harness")

left = s.shapes.add_textbox(Inches(0.6), Inches(1.6), Inches(5.3), Inches(2.9))
left.name = "Explanation"
set_text(left, [
    ("The LLM is the engine.", 24, True, BLUE),
    ("It reads and writes language.", 16, False, INK),
    ("", 10, False, INK),
    ("The harness is everything around it.", 24, True, BLUE),
    ("The loop, the tools, the memory, the context control and the safety rules.", 16, False, INK),
], align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0))

box(s, "Analogy card", 0.6, 4.55, 5.3, 1.7,
    [("Think of a car", 16, True, BLUE),
     ("An engine alone cannot drive anywhere. The body, wheels, steering and brakes make it useful.", 16, False, INK)],
    fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1, align=PP_ALIGN.LEFT, margins=(0.25, 0.1, 0.25, 0.1))

cap = s.shapes.add_textbox(Inches(0.6), Inches(6.45), Inches(5.3), Inches(0.55))
cap.name = "Caption"
set_text(cap, [("In our project: a loop that can call 6 tools and stops after 8 steps.", 12, False, MUTED)],
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0))

box(s, "Harness container", 6.3, 1.6, 6.5, 5.25, [], fill=LIGHT, border=BLUE, border_w=2.25, radius=0.05)
hl = s.shapes.add_textbox(Inches(6.6), Inches(1.7), Inches(3.0), Inches(0.4))
hl.name = "Harness label"
set_text(hl, [("THE HARNESS", 14, True, BLUE)], align=PP_ALIGN.LEFT, margins=(0, 0, 0, 0))

box(s, "LLM engine", 6.6, 3.15, 2.0, 2.4, [("LLM", 30, True, WHITE), ("the engine", 14, False, "CFE0F5")], fill=NAVY, radius=0.12)
pills = [
    ("Loop", "think, act, look, repeat"),
    ("Tools", "search documents, run SQL"),
    ("Memory", "saved chat state"),
    ("Context control", "keep the prompt short and clear"),
    ("Safety rules", "read-only data, limits, review"),
]
for i, (name, detail) in enumerate(pills):
    py = 2.2 + i * 0.88
    box(s, f"Harness part: {name}", 9.3, py, 3.25, 0.74, [(name, 15, True, INK), (detail, 12, False, MUTED)],
        fill=WHITE, border=BLUE, border_w=1.5, radius=0.2)
    arrow(s, f"Arrow: LLM to {name}", 8.6, 4.35, 9.3, py + 0.37, color=BLUE, width=1.75)

notes(s, "Think of an engine inside a car. The engine alone cannot drive anywhere. The harness is the rest of the car: the loop that keeps going, "
         "the tools the model can use, the memory, the control over what goes into the prompt, and the safety rules. "
         "In our project the harness is a loop that can call six tools and stops after eight steps.")

# =========================================================================== slide 3: architecture
s = prs.slides.add_slide(L_TITLE_ONLY)
title(s, "Our project architecture")
subt = s.shapes.add_textbox(Inches(0.6), Inches(1.0), Inches(8.0), Inches(0.4))
subt.name = "Subtitle"
set_text(subt, [("One question in. The right route picks the tools.", 14, False, MUTED)], align=PP_ALIGN.LEFT,
         margins=(0, 0, 0, 0))

box(s, "Legend: built", 9.4, 0.62, 1.55, 0.4, [("BUILT", 12, True, WHITE)], fill=BLUE, radius=0.3)
box(s, "Legend: next", 11.15, 0.62, 1.55, 0.4, [("NEXT", 12, True, AMBER_INK)], fill=AMBER_FILL, border=AMBER, dash=True, radius=0.3)

# users and the two doors
box(s, "Users", 0.4, 1.55, 1.8, 4.75, [("Users", 16, True, INK), ("web app", 13, False, MUTED), ("Claude", 13, False, MUTED), ("other agents", 13, False, MUTED)],
    fill="F3F5F8", border=GREYLINE, radius=0.08)
box(s, "Door: /agent", 2.8, 1.9, 1.75, 0.8, [("/agent", 16, True, WHITE), ("answers", 12, False, "CFE0F5")], fill=BLUE)
box(s, "Door: /mcp", 2.8, 5.55, 1.75, 0.75, [("/mcp", 16, True, WHITE), ("data only", 12, False, "CFE0F5")], fill=BLUE)
arrow(s, "Arrow: users to /agent", 2.2, 2.3, 2.8, 2.3)
arrow(s, "Arrow: users to /mcp", 2.2, 5.925, 2.8, 5.925)

# intent classifier (NEXT)
box(s, "Intent classifier (next)", 5.05, 1.65, 1.95, 1.3,
    [("Intent classifier", 15, True, INK), ("NEXT", 12, True, AMBER_INK), ("picks a route", 12, False, AMBER_INK)],
    fill=AMBER_FILL, border=AMBER, border_w=2.25, dash=True)
arrow(s, "Arrow: /agent to classifier", 4.55, 2.3, 5.05, 2.3, color=AMBER, width=2.25, dash=True)

# today vs next
tn = s.shapes.add_textbox(Inches(2.8), Inches(3.55), Inches(4.2), Inches(1.5))
tn.name = "Today vs next"
set_text(tn, [
    ("Today", 14, True, BLUE),
    ("The model picks its own tools by reading their descriptions.", 13, False, INK),
    ("", 6, False, INK),
    ("Next", 14, True, AMBER_INK),
    ("A classifier picks the route first, so the model sees fewer tools.", 13, False, INK),
], align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0))

# routes
routes = [
    ("Documents", "PDF search tools", BLUE),
    ("Database", "SQL tools", BLUE),
    ("Both", "documents, then SQL", BLUE),
    ("Other", "polite answer, no tools", GREYLINE),
]
for i, (name, detail, border) in enumerate(routes):
    ry = 1.55 + i * 0.9
    box(s, f"Route: {name}", 7.45, ry, 2.3, 0.75, [(name, 14, True, INK), (detail, 12, False, MUTED)],
        fill=WHITE, border=border, border_w=1.5, radius=0.2)
    arrow(s, f"Arrow: bus to {name}", 7.2, ry + 0.375, 7.45, ry + 0.375, color=AMBER, width=1.75, dash=True)
arrow(s, "Line: classifier to bus", 7.0, 2.3, 7.2, 2.3, color=AMBER, width=1.75, dash=True, head=False)
arrow(s, "Line: route bus", 7.2, 1.925, 7.2, 4.625, color=AMBER, width=1.75, dash=True, head=False)

# agent
box(s, "LangGraph agent", 10.25, 1.55, 2.65, 2.2,
    [("LangGraph agent", 16, True, WHITE), ("persona + skills", 13, False, "DCE9F8"), ("prompt cache", 13, False, "DCE9F8"),
     ("Gemini writes the answer", 13, True, WHITE)],
    fill=BLUE, radius=0.1)
for i in range(4):
    arrow(s, f"Line: route {i + 1} to bus", 9.75, 1.925 + i * 0.9, 10.0, 1.925 + i * 0.9, color=MUTED, width=1.5, head=False)
arrow(s, "Line: agent bus", 10.0, 1.925, 10.0, 4.625, color=MUTED, width=1.5, head=False)
arrow(s, "Arrow: routes to agent", 10.0, 2.65, 10.25, 2.65, color=MUTED, width=1.75)

# shared retrieval layer with its two stores inside
box(s, "Shared retrieval layer", 4.95, 5.35, 7.95, 1.65, [], fill=LIGHT, border=BLUE, border_w=2, radius=0.06)
rl = s.shapes.add_textbox(Inches(5.2), Inches(5.42), Inches(5.0), Inches(0.4))
rl.name = "Retrieval layer label"
set_text(rl, [("Shared retrieval layer", 15, True, BLUE)], align=PP_ALIGN.LEFT, margins=(0, 0, 0, 0))
box(s, "Store: Qdrant + BM25", 5.2, 5.95, 3.55, 0.8, [("Qdrant + BM25", 14, True, INK), ("meaning + word search over 5 PDFs", 12, False, MUTED)],
    fill=WHITE, border=BLUE, radius=0.15)
box(s, "Store: SQLite", 9.0, 5.95, 3.65, 0.8, [("SQLite database", 14, True, INK), ("read-only, 6 tables", 12, False, MUTED)],
    fill=WHITE, border=BLUE, radius=0.15)
arrow(s, "Arrow: /mcp to retrieval", 4.55, 5.925, 4.95, 5.925)
arrow(s, "Arrow: agent calls tools", 11.57, 3.75, 11.57, 5.35, color=MUTED, width=1.75)
ct = s.shapes.add_textbox(Inches(11.7), Inches(4.35), Inches(1.3), Inches(0.5))
ct.name = "Label: calls tools"
set_text(ct, [("calls tools", 12, False, MUTED)], align=PP_ALIGN.LEFT, margins=(0, 0, 0, 0))

notes(s, "This is the map of the whole talk. A question comes in through one of two doors. /agent writes a full answer. /mcp only returns data, so other agents can reason for themselves. "
         "On the /agent side, the intent classifier is the next feature we want to build: a small first step that reads the question and picks a route, either documents, database, both, or other. "
         "Today the model picks the route by itself by reading the tool descriptions and skills. With a classifier, routing becomes an explicit step that we can test, and the model sees fewer tools so it makes fewer mistakes. "
         "The cost is one extra model call, and a wrong route could hide the right tool, so the safe fallback is: if unsure, use both. "
         "Both doors use the same retrieval layer: Qdrant and BM25 for the PDFs, and a read-only SQLite database.")

prs.save(OUT)
print("saved", OUT)
