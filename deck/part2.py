"""Slides 23-36: RAG, advanced RAG, MCP, architecture."""
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION

from lib import *  # noqa: F401,F403

SEC_F, SEC_G, SEC_H, SEC_I = "F. RAG: from documents to answers", "G. Advanced RAG", "H. MCP", "I. Our architecture and the live demo"


def s23_rag(d):
    s = d.slide("Why RAG: the open-book exam", SEC_F,
                "RAG means retrieve, then generate. First find the right pages. Then let the model answer using them. Steps 1 to 4 happen once for each document. Steps 5 and 6 happen for every question.", tag="BUILT")
    text(s, "Lane 1", 0.6, 1.5, 6.0, 0.3, [("ONCE FOR EACH DOCUMENT", 13, True, MUTED)])
    flow(s, "Prepare", 0.6, 1.9, 12.13, 1.15, [("Documents", "PDF, Word, web"), ("1 Extract", "files to text"), ("2 Chunk", "small passages"), ("3 Embed", "numbers for meaning"), ("4 Store", "vector database")],
         fills=[GREYFILL, WHITE, WHITE, WHITE, BLUE], borders=[GREYLINE, BLUE, BLUE, BLUE, BLUE], gap=0.4)
    text(s, "Lane 2", 0.6, 3.45, 6.0, 0.3, [("FOR EVERY QUESTION", 13, True, MUTED)])
    box(s, "Question", 0.6, 3.85, 3.2, 1.15, [("Question", 16, True, INK)], fill=GREYFILL, border=GREYLINE, radius=0.14)
    box(s, "Retrieve", 4.95, 3.85, 3.2, 1.15, [("5 Retrieve", 15, True, INK), ("find the closest passages", 12, False, MUTED)], fill=WHITE, border=BLUE, radius=0.14)
    box(s, "Answer", 9.3, 3.85, 3.43, 1.15, [("6 Write the answer", 15, True, WHITE), ("with sources", 12, False, "DCE9F8")], fill=BLUE, radius=0.14)
    arrow(s, "q to r", 3.8, 4.42, 4.95, 4.42)
    arrow(s, "r to a", 8.15, 4.42, 9.3, 4.42)
    arrow(s, "store down", 11.65, 3.05, 11.65, 3.35, head=False, color=BLUE, dash=True)
    arrow(s, "store across", 11.65, 3.35, 6.55, 3.35, head=False, color=BLUE, dash=True)
    arrow(s, "store to retrieve", 6.55, 3.35, 6.55, 3.85, color=BLUE, dash=True)
    example(s, 0.6, 5.35, 12.13, 1.5, "An open-book exam. You do not memorize the whole book. You find the right page and write your answer from it.", bsize=20)


def s24_extract(d):
    s = d.slide("Step 1: extraction", SEC_F,
                "Turn files into clean text, one page at a time. The hard parts are tables, scanned pages that need OCR, and pages with many columns.", tag="BUILT")
    box(s, "PDF page", 0.8, 1.7, 2.4, 3.0, [], fill=WHITE, border=GREYLINE, shape=MSO_SHAPE.FOLDED_CORNER)
    for i, wd in enumerate((1.8, 1.8, 1.2, 1.8, 1.5, 1.8)):
        box(s, f"PDF line {i}", 1.1, 2.1 + i * 0.38, wd, 0.12, [], fill=GREYLINE, shape=MSO_SHAPE.RECTANGLE)
    text(s, "PDF label", 0.8, 4.8, 2.4, 0.3, [("a PDF page", 13, False, MUTED)], align=CENTER)
    arrow(s, "to text", 3.5, 3.2, 4.6, 3.2, color=BLUE, width=2.5)
    box(s, "Clean text", 4.9, 1.7, 4.3, 3.0, [("Damage in transit must be reported within 7 days of delivery. Customers must provide photographs...", 15, False, INK, MONO)],
        fill=PALE, border=BLUE, align=LEFT, anchor=TOP, margins=(0.25, 0.2, 0.25, 0.2), radius=0.06)
    text(s, "Text label", 4.9, 4.8, 4.3, 0.3, [("clean text, page by page", 13, False, MUTED)], align=CENTER)
    card(s, "Hard parts", 9.55, 1.7, 3.18, 3.4, "Hard parts", ["Tables", "Scanned pages (need OCR)", "Pages with many columns"], hsize=19, bsize=17, fill=AMBER_FILL, hcolor=AMBER_INK)
    code(s, "Code: extract", 0.6, 5.35, 7.3, 1.0, 'reader = PdfReader("02_shipping_and_delivery_sla.pdf")\ntext = reader.pages[0].extract_text()', size=14)
    example(s, 8.2, 5.35, 4.53, 1.5, "Copy a table from a PDF and it often turns into a mess. Extraction tools try to keep it tidy.", bsize=15)


def s25_chunk(d):
    s = d.slide("Step 2: chunking", SEC_F,
                "Cut the text into small passages the model can use. Our rule is about 900 characters each, with 150 characters of overlap so a sentence is not cut in half. Our 5 PDFs became 21 chunks.", tag="BUILT")
    box(s, "Page", 0.6, 1.55, 3.2, 5.3, [], fill=WHITE, border=GREYLINE, radius=0.04)
    text(s, "Page label", 0.6, 1.6, 3.2, 0.3, [("one page of text", 13, True, MUTED)], align=CENTER)
    for k, (y, fill, lab) in enumerate(((2.05, "CFE3F8", "Chunk 1"), (3.55, "FFE8B5", "Chunk 2"), (5.05, "D5F0E2", "Chunk 3"))):
        box(s, f"Chunk {k + 1}", 0.85, y, 2.7, 1.75, [(lab, 15, True, INK)], fill=fill, border=GREYLINE, radius=0.08, anchor=TOP, margins=(0.15, 0.1, 0.1, 0.1))
    text(s, "Overlap label", 4.0, 3.45, 2.6, 0.7, [("overlap: the end of one chunk repeats at the start of the next", 12, False, AMBER_INK)])
    arrow(s, "overlap arrow", 3.95, 3.7, 3.55, 3.7, color=AMBER, width=2)
    stat(s, "Stat chunk", 7.0, 1.6, 2.8, "900", "characters per chunk")
    stat(s, "Stat overlap", 10.0, 1.6, 2.7, "150", "characters of overlap")
    stat(s, "Stat count", 7.0, 3.0, 5.7, "5 PDFs → 21 chunks", "small enough to find, big enough to make sense", big_size=34)
    code(s, "Code: chunk", 7.0, 4.35, 5.73, 0.95, "CHUNK_CHARS = 900\nCHUNK_OVERLAP = 150   # keeps sentences whole", size=14)
    example(s, 7.0, 5.5, 5.73, 1.35, "Index cards. Too big and you cannot find the fact. Too small and the card makes no sense alone.", bsize=16)


def s26_embed(d):
    s = d.slide("Step 3: embeddings", SEC_F,
                "An embedding turns text into a list of numbers, ours has 768. Texts with similar meaning get similar numbers, so refund and money back land close together. "
                "Use the same embedding model for the documents and for the questions.", tag="BUILT")
    box(s, "Map", 0.6, 1.55, 6.9, 4.4, [], fill=LIGHT, radius=0.03)
    text(s, "Map label", 0.8, 1.62, 6.5, 0.3, [("a map of meaning (simplified to 2 numbers)", 12, True, MUTED)])
    pts_a = [("refund", 1.2, 2.5), ("money back", 2.4, 2.1), ("return policy", 1.5, 3.4)]
    pts_b = [("delivery truck", 4.3, 4.7), ("late delivery", 5.2, 4.1), ("shipping SLA", 4.1, 3.5)]
    for lab, x, y in pts_a:
        box(s, f"Dot {lab}", x, y, 0.24, 0.24, [], fill=BLUE, shape=MSO_SHAPE.OVAL)
        text(s, f"Pt {lab}", x + 0.3, y - 0.04, 1.8, 0.3, [(lab, 13, True, BLUE)])
    for lab, x, y in pts_b:
        box(s, f"Dot {lab}", x, y, 0.24, 0.24, [], fill=AMBER, shape=MSO_SHAPE.OVAL)
        text(s, f"Pt {lab}", x + 0.3, y - 0.04, 1.8, 0.3, [(lab, 13, True, AMBER_INK)])
    box(s, "Cluster returns", 0.95, 1.95, 3.1, 2.1, [], fill=None, border=BLUE, dash=True, shape=MSO_SHAPE.OVAL)
    box(s, "Cluster shipping", 3.9, 3.1, 3.2, 2.2, [], fill=None, border=AMBER, dash=True, shape=MSO_SHAPE.OVAL)
    stat(s, "Stat 768", 7.9, 1.55, 4.8, "768", "numbers for every piece of text")
    code(s, "Code: embed", 7.9, 2.95, 4.83, 1.9, 'client.models.embed_content(\n  model="gemini-embedding-001",\n  contents=chunks)', size=14)
    example(s, 7.9, 5.05, 4.83, 1.9, "A map. Restaurants close to each other have similar coordinates. Embeddings are coordinates for meaning.", bsize=16)
    text(s, "Same model note", 0.6, 6.15, 6.9, 0.7, [("Use the same embedding model for the documents and for the questions.", 15, True, NAVY)])


def s27_store(d):
    s = d.slide("Step 4: storing in a vector database", SEC_F,
                "A vector database finds the closest vectors fast. We use Qdrant. It saves plain files, and each vector keeps its text, file name and page. "
                "On free hosting the disk is wiped, so our app rebuilds the index when it starts. That takes a few seconds for 21 chunks.", tag="BUILT")
    box(s, "Vector item", 0.6, 1.7, 3.6, 1.7, [("a vector", 17, True, INK), ("+ text, file, page", 14, False, MUTED)], fill=WHITE, border=BLUE, radius=0.12)
    box(s, "Qdrant", 5.0, 1.7, 3.0, 1.7, [("Qdrant", 22, True, WHITE), ("stored as plain files", 13, False, "DCE9F8")], fill=BLUE, radius=0.12)
    box(s, "Closest", 8.8, 1.7, 3.93, 1.7, [("5 closest chunks", 17, True, INK), ("found in a blink", 14, False, MUTED)], fill=WHITE, border=BLUE, radius=0.12)
    arrow(s, "v to q", 4.2, 2.55, 5.0, 2.55)
    arrow(s, "q to c", 8.0, 2.55, 8.8, 2.55)
    stat(s, "Stat vectors", 0.6, 3.75, 3.5, "21", "vectors for 5 PDFs")
    stat(s, "Stat numbers", 4.3, 3.75, 3.5, "768", "numbers in each vector")
    card(s, "Render note", 8.2, 3.75, 4.53, 3.1, "On free hosting", ["The disk is wiped when the app restarts.", "So the app rebuilds the index at startup. It takes a few seconds."], hsize=18, bsize=16, fill=AMBER_FILL, hcolor=AMBER_INK)
    example(s, 0.6, 5.15, 7.2, 1.7, "A library where books are placed by topic, not by alphabet.", bsize=20)


def s28_retrieve(d):
    s = d.slide("Steps 5 and 6: retrieve, then write", SEC_F,
                "The question becomes a vector. We fetch the closest chunks. The model writes an answer using only those chunks and shows its sources. Sources let a person check the answer.", tag="BUILT")
    flow(s, "Answering", 0.6, 1.6, 12.13, 1.2, [("Question", ""), ("Make a vector", ""), ("Find closest chunks", ""), ("Build the prompt", "question + passages"), ("Answer", "with sources")],
         fills=[GREYFILL, WHITE, WHITE, WHITE, BLUE], borders=[GREYLINE, BLUE, BLUE, BLUE, BLUE], gap=0.4)
    text(s, "Prompt label", 0.6, 3.1, 7.0, 0.3, [("WHAT THE MODEL SEES (SIMPLIFIED)", 13, True, MUTED)])
    code(s, "Prompt sample", 0.6, 3.5, 7.4, 2.2,
         'Question: What is the refund window\n  for damaged items?\n\nPassage [Returns Policy, p.1]:\n"Damage in transit must be reported\n within 7 days of delivery..."', size=15)
    example(s, 8.4, 3.5, 4.33, 3.35, "An HR bot gets “How many leave days do I get?”. It finds the leave-policy page and quotes it.", bsize=19)
    text(s, "Sources note", 0.6, 5.95, 7.4, 0.8, [("Sources let a person check the answer.", 17, True, NAVY)])


def s29_hybrid(d):
    s = d.slide("Hybrid search and reranking", SEC_G,
                "Mix search by meaning with search by exact words, then merge the two lists. For example, searching Platinum: vector search may mix it up with other tiers, exact-word search finds it right away. "
                "A reranker is an extra step that re-checks the top results with a stronger model. We built the hybrid part. The reranker is only an idea for now.", tag="BUILT")
    box(s, "Question", 0.6, 3.0, 2.0, 1.2, [("Question", 16, True, INK)], fill=GREYFILL, border=GREYLINE)
    box(s, "Meaning search", 3.4, 1.75, 3.2, 1.2, [("Search by meaning", 15, True, INK), ("vectors", 12, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Word search", 3.4, 4.25, 3.2, 1.2, [("Search by exact words", 15, True, INK), ("BM25", 12, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Merge", 7.4, 3.0, 2.6, 1.2, [("Merge the lists", 15, True, WHITE), ("rank fusion", 12, False, "DCE9F8")], fill=BLUE)
    box(s, "Best", 10.8, 3.0, 1.93, 1.2, [("Best results", 15, True, INK)], fill=WHITE, border=BLUE)
    arrow(s, "q1", 2.6, 3.4, 3.4, 2.5)
    arrow(s, "q2", 2.6, 3.8, 3.4, 4.7)
    arrow(s, "m1", 6.6, 2.5, 7.4, 3.4)
    arrow(s, "m2", 6.6, 4.7, 7.4, 3.8)
    arrow(s, "b1", 10.0, 3.6, 10.8, 3.6)
    box(s, "Reranker", 10.2, 4.55, 2.53, 0.8, [("+ reranker (idea)", 13, True, MUTED)], fill=GREYFILL, border=GREYLINE, dash=True)
    code(s, "Code: fusion", 0.6, 5.75, 7.0, 0.65, "score += 1.0 / (60 + rank + 1)   # merge rankings", size=14)
    example(s, 7.9, 5.6, 4.83, 1.25, "Search for “Platinum”: exact words find it at once.", bsize=16)


def s30_agentic(d):
    s = d.slide("Agentic RAG with documents and a database", SEC_G,
                "The agent chooses what to look up, from which source, in how many steps. Documents give the rule. SQL gives the numbers. Both together apply the rule to the data. "
                "Rewriting the question and multi-step lookups are further ideas we did not build. All numbers on this slide were checked with our own SQL.", tag="BUILT")
    flow(s, "Agent chain", 0.6, 1.6, 12.13, 1.45, [("search_docs", "credit bands: 5% / 10% / 15%"), ("list_tables", "and describe_table"), ("run_sql", "count late orders per band"), ("Answer", "with sources and a table")],
         fills=[WHITE, WHITE, WHITE, BLUE], gap=0.45, tsize=15, dsize=13)
    text(s, "Question line", 0.6, 3.2, 12.13, 0.4, [("Question: which delivered orders were late, and what credit does the policy give per band?", 15, True, MUTED)], align=CENTER)
    stat(s, "Stat late", 0.6, 3.85, 3.6, "50 of 287", "delivered shipments were late")
    stat(s, "Stat bands", 4.5, 3.85, 4.2, "20 · 17 · 13", "late shipments in the three bands")
    stat(s, "Stat check", 9.0, 3.85, 3.7, "100%", "of numbers matched our own check")
    example(s, 0.6, 5.35, 12.13, 1.5, "The agent searched the policy for the credit bands, looked at the shipments table, then ran one SQL query. Documents for the rule, SQL for the numbers.", label="From our project", bsize=18)


def s31_test(d):
    s = d.slide("Testing, safety rules and cost", SEC_G,
                "Measure, do not guess. Our prompt is about 1,400 tokens and got no automatic cache hits. A test prompt of about 9,500 tokens reused 6,121 tokens from the cache. "
                "Caching helps only when the repeated part is big. The explicit cache feature was not available on our free key. Our agent now shows prompt tokens and cached tokens for every answer.", tag="BUILT")
    card(s, "Testing", 0.6, 1.55, 5.9, 1.65, "Test with real questions", "Check the answers yourself. We recalculated every number with direct SQL.", hsize=19, bsize=17, fill=LIGHT)
    card(s, "Safety", 0.6, 3.4, 5.9, 1.65, "Safety rules", "Read-only SQL, one statement, limits on rows, time and requests.", hsize=19, bsize=17, fill=LIGHT)
    card(s, "Cost", 0.6, 5.25, 5.9, 1.6, "Cost and speed", "Prompt caching reuses the part of the prompt that never changes.", hsize=19, bsize=17, fill=LIGHT)
    cd = CategoryChartData()
    cd.categories = ["Our prompt (about 1,400 tokens)", "Test prompt (about 9,500 tokens)"]
    cd.add_series("Prompt tokens", (1391, 9460))
    cd.add_series("Read from cache", (0, 6121))
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.9), Inches(1.5), Inches(5.83), Inches(5.0), cd)
    gf.name = "Chart: prompt cache measured"
    ch = gf.chart
    ch.font.name, ch.font.size = FONT, Pt(12)
    ch.has_title = True
    ch.chart_title.text_frame.text = "Automatic caching, measured"
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.BOTTOM
    ch.legend.include_in_layout = False
    plot = ch.plots[0]
    plot.gap_width = 70
    plot.has_data_labels = True
    plot.data_labels.number_format = "#,##0"
    plot.data_labels.number_format_is_linked = False
    plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.font.size = Pt(12)
    for ser, col in zip(plot.series, (BLUE, GREEN)):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = rgb(col)
    ch.value_axis.maximum_scale = 11000
    ch.value_axis.minimum_scale = 0
    ch.value_axis.major_gridlines.format.line.color.rgb = rgb("E4E9F0")
    ch.value_axis.tick_labels.font.size = Pt(11)
    ch.value_axis.tick_labels.number_format = "#,##0"
    ch.value_axis.tick_labels.number_format_is_linked = False
    text(s, "Chart note", 6.9, 6.55, 5.83, 0.4, [("One test run each. Caching pays off only when the repeated part is big.", 12, False, MUTED)])


def s32_mcp(d):
    s = d.slide("What is MCP?", SEC_H,
                "Model Context Protocol, or MCP, is an open standard. It lets any AI app connect to tools and data in the same way. Without MCP, 5 apps and 5 tools need 25 custom links. With MCP you need 5 plus 5.", tag="BUILT")
    for i, c in enumerate(("Claude", "Other agents", "Code editors")):
        box(s, f"Client {c}", 0.6, 1.8 + i * 1.5, 2.6, 1.0, [(c, 16, True, INK)], fill=WHITE, border=BLUE)
        arrow(s, f"c{i}", 3.2, 2.3 + i * 1.5, 4.6, 3.6, color=BLUE, head=False)
    box(s, "MCP hub", 4.6, 2.85, 2.6, 1.5, [("MCP", 26, True, WHITE), ("one standard plug", 13, False, "DCE9F8")], fill=BLUE, radius=0.15)
    for i, c in enumerate(("Documents server", "Database server", "Calendar server")):
        box(s, f"Server {c}", 8.6, 1.8 + i * 1.5, 2.6, 1.0, [(c, 15, True, INK)], fill=WHITE, border=BLUE)
        arrow(s, f"s{i}", 7.2, 3.6, 8.6, 2.3 + i * 1.5, color=BLUE, head=False)
    stat(s, "Stat old", 11.45, 1.7, 1.4, "25", "custom links", color=RED, big_size=30)
    stat(s, "Stat new", 11.45, 3.4, 1.4, "5 + 5", "with MCP", color=GREEN, big_size=30)
    example(s, 0.6, 6.0, 12.13, 0.95, "USB-C. One plug works with many devices. Before it, every device had its own cable.", bsize=16)


def s33_ourmcp(d):
    s = d.slide("Our MCP server", SEC_H,
                "Six tools. The server only returns data. The caller's own model writes the answer. The tool descriptions are the rules the caller reads. "
                "Two doors lead to the same retrieval code: /mcp returns data only, and /agent adds a Gemini answer.", tag="BUILT")
    tools = ["search_docs", "list_documents", "get_document_page", "list_tables", "describe_table", "run_sql"]
    text(s, "Tools title", 0.6, 1.55, 3.5, 0.35, [("SIX TOOLS", 13, True, MUTED)])
    for i, t in enumerate(tools):
        box(s, f"Tool {t}", 0.6, 2.0 + i * 0.75, 3.5, 0.62, [(t, 15, True, CODE_INK, MONO)], fill=CODE_BG, radius=0.25)
    code(s, "Code: tool", 4.5, 1.9, 8.23, 2.0, '@mcp.tool()\ndef search_docs(query: str, k: int = 5) -> dict:\n    """Search the company policy PDFs ...\n    Returns passages with a citation."""\n    return {"results": retrieval.search_docs(query, k)}', size=14)
    box(s, "Shared retrieval", 4.5, 4.3, 3.6, 1.0, [("Shared retrieval code", 15, True, WHITE)], fill=BLUE)
    box(s, "Door mcp", 8.9, 4.1, 3.83, 0.85, [("/mcp: data only", 15, True, INK)], fill=WHITE, border=BLUE)
    box(s, "Door agent", 8.9, 5.15, 3.83, 0.85, [("/agent: data + Gemini answer", 15, True, INK)], fill=WHITE, border=BLUE)
    arrow(s, "r1", 8.1, 4.7, 8.9, 4.5)
    arrow(s, "r2", 8.1, 4.9, 8.9, 5.55)
    text(s, "Server note", 4.5, 5.6, 4.3, 1.2, [("It only returns data. The caller's own model writes the answer.", 15, False, INK)])


def s34_share(d):
    s = d.slide("Sharing it with other agents", SEC_H,
                "One link and one secret let any MCP-ready agent use your data. We tested with a real MCP client and with the live link.", tag="BUILT")
    for i, c in enumerate(("Claude on the web", "Claude Code", "Another MCP agent")):
        box(s, f"Client {c}", 0.6, 1.6 + i * 1.15, 3.2, 0.9, [(c, 15, True, INK)], fill=WHITE, border=BLUE)
        arrow(s, f"c{i}", 3.8, 2.05 + i * 1.15, 4.9, 3.1, color=BLUE)
    box(s, "URL", 4.9, 2.55, 3.4, 1.1, [("https://.../mcp", 17, True, CODE_INK, MONO), ("one link + a secret", 12, False, "9EBEE8")], fill=CODE_BG, radius=0.12)
    box(s, "Server", 9.1, 2.55, 3.63, 1.1, [("Our server", 17, True, WHITE), ("on Render", 13, False, "DCE9F8")], fill=BLUE)
    arrow(s, "u to s", 8.3, 3.1, 9.1, 3.1)
    text(s, "Cmd title", 0.6, 5.0, 12.0, 0.35, [("CLAUDE CODE: ONE COMMAND", 13, True, MUTED)])
    code(s, "Code: add server", 0.6, 5.4, 12.13, 0.85, 'claude mcp add --transport http brightline <url> --header "Authorization: Bearer <token>"', size=14)
    text(s, "Web note", 0.6, 6.4, 12.13, 0.5, [("Claude on the web: Settings, Connectors, add a custom connector with the link.", 15, False, INK)])


def s35_safe(d):
    s = d.slide("Keeping an MCP server safe", SEC_H,
                "A token inside a link is like a key under the doormat: fine for a demo, not for a bank. Never paste keys or tokens into chats or slides. If one leaks, change it. "
                "A lesson we learned: a hosted server rejects unknown website names until you set it up.", tag="BUILT")
    items = [("Secret token", "Every request needs it.", "BUILT", BLUE), ("Read-only database", "Nobody can change the data.", "BUILT", BLUE),
             ("Request limits", "Stops one user using it all up.", "BUILT", BLUE), ("OAuth sign-in", "Each user has their own permission. Real products use this.", "CONCEPT", MUTED)]
    for i, (h, b, tg, col) in enumerate(items):
        x, y = 0.6 + (i % 2) * 6.15, 1.55 + (i // 2) * 1.85
        card(s, f"Safety {h}", x, y, 5.98, 1.65, h, b, hsize=21, bsize=18, fill=LIGHT)
        pill(s, f"Safety tag {h}", x + 4.5, y + 0.15, 1.3, 0.34, tg, fill=BLUE if tg == "BUILT" else GREYFILL, color=WHITE if tg == "BUILT" else MUTED, size=11, border=None if tg == "BUILT" else GREYLINE)
    example(s, 0.6, 5.3, 6.0, 1.55, "A token inside a link is like a key under the doormat. Fine for a demo, not for a bank.", bsize=17)
    card(s, "Lesson", 6.75, 5.3, 5.98, 1.55, "A lesson we learned", "A hosted server rejects unknown website names until you set it up.", hsize=15, bsize=16, fill=AMBER_FILL, hcolor=AMBER_INK)


def s36_arch(d):
    s = d.slide("Our project architecture", SEC_I,
                "This is the map of the whole talk. A question comes in through one of two doors. /agent writes a full answer. /mcp only returns data, so other agents reason for themselves. "
                "On the /agent side, the intent classifier is the next feature: a small first step that reads the question and picks a route, documents, database, both, or other. "
                "Today the model picks the route by itself by reading tool descriptions and skills. With a classifier, routing becomes an explicit step we can test, and the model sees fewer tools so it makes fewer mistakes. "
                "The cost is one extra model call, and a wrong route could hide the right tool, so the safe fallback is: if unsure, use both. "
                "Both doors use the same retrieval layer: Qdrant and BM25 for the PDFs, and a read-only SQLite database.")
    text(s, "Subtitle", 0.6, 1.12, 8.0, 0.35, [("One question in. The right route picks the tools.", 14, False, MUTED)])
    box(s, "Legend: built", 7.75, 0.62, 1.4, 0.38, [("BUILT", 12, True, WHITE)], fill=BLUE, radius=0.3)
    box(s, "Legend: next", 9.3, 0.62, 1.4, 0.38, [("NEXT", 12, True, AMBER_INK)], fill=AMBER_FILL, border=AMBER, dash=True, radius=0.3)
    box(s, "Users", 0.4, 1.55, 1.8, 4.75, [("Users", 16, True, INK), ("web app", 13, False, MUTED), ("Claude", 13, False, MUTED), ("other agents", 13, False, MUTED)], fill=GREYFILL, border=GREYLINE, radius=0.08)
    box(s, "Door: /agent", 2.8, 1.9, 1.75, 0.8, [("/agent", 16, True, WHITE), ("answers", 12, False, "CFE0F5")], fill=BLUE)
    box(s, "Door: /mcp", 2.8, 5.55, 1.75, 0.75, [("/mcp", 16, True, WHITE), ("data only", 12, False, "CFE0F5")], fill=BLUE)
    arrow(s, "Arrow: users to /agent", 2.2, 2.3, 2.8, 2.3)
    arrow(s, "Arrow: users to /mcp", 2.2, 5.925, 2.8, 5.925)
    box(s, "Intent classifier (next)", 5.05, 1.65, 1.95, 1.3, [("Intent classifier", 15, True, INK), ("NEXT", 12, True, AMBER_INK), ("picks a route", 12, False, AMBER_INK)], fill=AMBER_FILL, border=AMBER, border_w=2.25, dash=True)
    arrow(s, "Arrow: /agent to classifier", 4.55, 2.3, 5.05, 2.3, color=AMBER, width=2.25, dash=True)
    text(s, "Today vs next", 2.8, 3.55, 4.2, 1.5, [("Today", 14, True, BLUE), ("The model picks its own tools by reading their descriptions.", 13, False, INK), ("", 6, False, INK),
                                                    ("Next", 14, True, AMBER_INK), ("A classifier picks the route first, so the model sees fewer tools.", 13, False, INK)])
    routes = [("Documents", "PDF search tools", BLUE), ("Database", "SQL tools", BLUE), ("Both", "documents, then SQL", BLUE), ("Other", "polite answer, no tools", GREYLINE)]
    for i, (name, detail, border) in enumerate(routes):
        ry = 1.55 + i * 0.9
        box(s, f"Route: {name}", 7.45, ry, 2.3, 0.75, [(name, 14, True, INK), (detail, 12, False, MUTED)], fill=WHITE, border=border, radius=0.2)
        arrow(s, f"Arrow: bus to {name}", 7.2, ry + 0.375, 7.45, ry + 0.375, color=AMBER, width=1.75, dash=True)
    arrow(s, "Line: classifier to bus", 7.0, 2.3, 7.2, 2.3, color=AMBER, width=1.75, dash=True, head=False)
    arrow(s, "Line: route bus", 7.2, 1.925, 7.2, 4.625, color=AMBER, width=1.75, dash=True, head=False)
    box(s, "LangGraph agent", 10.25, 1.55, 2.65, 2.2, [("LangGraph agent", 16, True, WHITE), ("persona + skills", 13, False, "DCE9F8"), ("prompt cache", 13, False, "DCE9F8"), ("Gemini writes the answer", 13, True, WHITE)], fill=BLUE, radius=0.1)
    for i in range(4):
        arrow(s, f"Line: route {i + 1} to bus", 9.75, 1.925 + i * 0.9, 10.0, 1.925 + i * 0.9, head=False, width=1.5)
    arrow(s, "Line: agent bus", 10.0, 1.925, 10.0, 4.625, head=False, width=1.5)
    arrow(s, "Arrow: routes to agent", 10.0, 2.65, 10.25, 2.65)
    box(s, "Shared retrieval layer", 4.95, 5.35, 7.95, 1.65, [], fill=LIGHT, border=BLUE, border_w=2, radius=0.06)
    text(s, "Retrieval layer label", 5.2, 5.42, 5.0, 0.4, [("Shared retrieval layer", 15, True, BLUE)])
    box(s, "Store: Qdrant + BM25", 5.2, 5.95, 3.55, 0.8, [("Qdrant + BM25", 14, True, INK), ("meaning + word search over 5 PDFs", 12, False, MUTED)], fill=WHITE, border=BLUE, radius=0.15)
    box(s, "Store: SQLite", 9.0, 5.95, 3.65, 0.8, [("SQLite database", 14, True, INK), ("read-only, 6 tables", 12, False, MUTED)], fill=WHITE, border=BLUE, radius=0.15)
    arrow(s, "Arrow: /mcp to retrieval", 4.55, 5.925, 4.95, 5.925)
    arrow(s, "Arrow: agent calls tools", 11.57, 3.75, 11.57, 5.35)
    text(s, "Label: calls tools", 11.7, 4.35, 1.3, 0.5, [("calls tools", 12, False, MUTED)])


ORDER = [s23_rag, s24_extract, s25_chunk, s26_embed, s27_store, s28_retrieve, s29_hybrid, s30_agentic, s31_test, s32_mcp, s33_ourmcp, s34_share, s35_safe, s36_arch]
