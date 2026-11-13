"""Intro slide, agenda, section dividers and the two tools slides."""
from lib import *  # noqa: F401,F403

TITLE = "From Classroom to Real-World AI Agents"
THEME = "Bridging Academia and Industry through Intelligent Technologies"


def intro(d):
    s = d.prs.slides.add_slide(d.L_TITLE_ONLY)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(WHITE)
    box(s, "Maroon bar", 0, 0, 0.28, 7.5, [], fill=MAROON, shape=MSO_SHAPE.RECTANGLE)
    logo(s, 9.55, 0.4, 3.3)
    pill(s, "Event chip", 0.8, 0.75, 3.6, 0.48, "INDUSTRY GUEST LECTURE", fill=MAROON, color=WHITE, size=15)
    text(s, "Theme", 0.8, 1.55, 8.4, 0.9, [(THEME, 22, True, MAROON)])
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.8), Inches(2.65), Inches(11.8), Inches(1.0)
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MIDDLE
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.alignment = LEFT
    r = p.add_run()
    r.text = TITLE
    r.font.size, r.font.bold, r.font.name = Pt(48), True, FONT
    r.font.color.rgb = rgb(NAVY)
    text(s, "Subtitle", 0.8, 3.75, 11.5, 0.5, [("How LLMs, RAG, agents and MCP work, explained simply and built live.", 22, False, MUTED)])
    box(s, "Rule", 0.8, 4.5, 2.6, 0.06, [], fill=MAROON, shape=MSO_SHAPE.RECTANGLE)
    for i, lab in enumerate(("AI and ML basics", "LLMs", "Agents and tools", "RAG", "MCP", "Going live")):
        pill(s, f"Topic {lab}", 0.8 + i * 1.98, 4.85, 1.8, 0.48, lab, fill=PALE, color=BLUE, size=13)
    text(s, "Speaker", 0.8, 5.85, 8.0, 0.9, [("Speaker: Your Name", 18, True, INK), ("Role, Company", 15, False, MUTED)])
    text(s, "Venue", 8.3, 6.2, 4.55, 0.4, [("VIT-AP University", 15, True, MAROON)], align=RIGHT)
    s.notes_slide.notes_text_frame.text = (
        "Welcome, VIT-AP. This is an industry guest lecture: the aim is to connect what you learn in class with how companies build AI today. "
        "By the end you will understand LLM, RAG, agent and MCP, and you will see one working project that we built and put online.")


def agenda(d):
    s = d.slide("Today's journey", "Agenda",
                "This is our map for the next two hours. We start with the basics, then move to agents and RAG, then see our real project, "
                "and end with how to put it online and where to get models. Questions are welcome at the end of each part.")
    parts = [("AI basics", "AI, machine learning, deep learning", "10 min"),
             ("Large language models", "What an LLM is and how companies use it", "12 min"),
             ("Agents and tools", "LLM + harness, tools, LangChain, LangGraph", "15 min"),
             ("Personas, skills, plugins", "Roles, playbooks and packages", "10 min"),
             ("RAG", "Answers from your own documents", "15 min"),
             ("Advanced RAG and our project", "Documents + a database, together", "10 min"),
             ("MCP", "Share your tools with any AI", "12 min"),
             ("Our build and live demo", "Architecture, streaming, demo", "15 min"),
             ("Putting it online", "Deploying on Render", "6 min"),
             ("Where to get models", "Providers, free tiers, self-hosting", "8 min")]
    for i, (h, sub, mins) in enumerate(parts):
        col, row = divmod(i, 5)
        x, y = 0.6 + col * 6.2, 1.45 + row * 1.02
        num(s, x, y + 0.14, i + 1, d=0.62, size=18)
        text(s, f"Part {i + 1}", x + 0.85, y + 0.06, 4.1, 0.85, [(h, 18, True, NAVY), (sub, 14, False, MUTED)])
        pill(s, f"Time {i + 1}", x + 4.95, y + 0.24, 0.98, 0.38, mins, fill=GREYFILL, color=MUTED, size=12)
    text(s, "Wrap", 0.6, 6.62, 12.13, 0.35, [("Then: wrap-up and questions (7 min)", 14, True, MAROON)], align=CENTER)


DIVIDERS = {
    1: ("AI basics", "How a computer learns from examples, step by step.",
        ["The AI map", "How machines learn", "Neural nets, transformers"]),
    2: ("Large language models", "What tools like ChatGPT and Gemini really are, and where they fall short.",
        ["What an LLM is", "Big models and open models", "How companies use them"]),
    3: ("Agents and tools", "An LLM can only talk. Tools and a loop let it do real work.",
        ["Agent = LLM + harness", "Tools: the agent's hands", "LangChain and LangGraph"]),
    4: ("Personas, skills and plugins", "How to give one agent different roles, rules and a ready-to-share package.",
        ["Personas: roles", "Skills: playbooks", "Plugins: the package"]),
    5: ("RAG: answers from your documents", "Let the model read your files before it answers, like an open-book exam.",
        ["Extract and chunk", "Embeddings and vector database", "Retrieve, then write"]),
    6: ("Advanced RAG and our project", "Better search, then a real question that needs documents and a database.",
        ["Hybrid search", "Our project", "Agentic RAG"]),
    7: ("MCP: share your tools with any AI", "One standard plug so any AI app can use our search and database tools.",
        ["What MCP is", "Our MCP server", "Keeping it safe"]),
    8: ("Our build and the live demo", "All the pieces together, working live.",
        ["Architecture", "Streaming", "Live demo"]),
    9: ("Putting it online", "From a laptop to a public link, for free.",
        ["Deploy on Render", "Secrets and access", "Updates and fixes"]),
    10: ("Where to get models", "Paid, free and run-it-yourself options, and how to choose.",
         ["Providers", "Free tiers", "Self-hosting"]),
}


def divider(n):
    title, line, learn = DIVIDERS[n]

    def build(d):
        s = d.prs.slides.add_slide(d.L_TITLE_ONLY)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(NAVY)
        logo(s, 11.0, 0.35, 1.85, panel=True)
        box(s, "Part bar", 0.8, 2.0, 0.12, 2.3, [], fill=MAROON, shape=MSO_SHAPE.RECTANGLE)
        text(s, "Part number", 1.2, 1.95, 6.0, 0.5, [(f"PART {n} OF 10", 16, True, "7FB2EA")])
        t = s.shapes.title
        t.left, t.top, t.width, t.height = Inches(1.2), Inches(2.45), Inches(11.0), Inches(1.0)
        tf = t.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MIDDLE
        tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.alignment = LEFT
        r = p.add_run()
        r.text = title
        r.font.size, r.font.bold, r.font.name = Pt(44), True, FONT
        r.font.color.rgb = rgb(WHITE)
        text(s, "One line", 1.2, 3.55, 10.5, 0.8, [(line, 20, False, "CFE0F5")])
        text(s, "Learn label", 1.2, 4.85, 6.0, 0.4, [("IN THIS PART", 13, True, "7FB2EA")])
        for i, item in enumerate(learn):
            pill(s, f"Learn {i + 1}", 1.2 + i * 3.75, 5.3, 3.5, 0.6, item, fill="17335C", color=WHITE, size=16)
        s.notes_slide.notes_text_frame.text = f"Part {n}: {title}. {line}"

    build.__name__ = f"divider_{n}"
    return build


SEC_D = "D. Agent = LLM + harness"


def tools_what(d):
    s = d.slide("Tools: the agent's hands", SEC_D,
                "A tool is just a normal function with a name, a short description and inputs. The model cannot run code by itself. "
                "It reads the list of tools, decides which one it needs, and asks for it. The harness runs the function and hands back the result. "
                "Our project has six tools: three for documents and three for the database. All of them only read data, they never change it.", tag="BUILT")
    text(s, "Explanation", 0.6, 1.55, 5.2, 2.8, [("A tool is a normal function.", 22, True, BLUE),
                                                ("It has a name, a short description and inputs.", 16, False, INK), ("", 8, False, INK),
                                                ("The model only asks.", 22, True, BLUE),
                                                ("The harness runs the tool and gives the result back to the model.", 16, False, INK)])
    example(s, 0.6, 4.1, 5.2, 2.0, "A manager and an assistant. The manager (the model) decides who to call and what to ask. "
                                    "The assistant (the harness) makes the call and brings back the answer.", bsize=16)
    groups = [("Documents (PDFs)", [("search_docs", "find the best matching passages"), ("list_documents", "which PDFs we have"),
                                    ("get_document_page", "read one full page")]),
              ("Database (SQL)", [("list_tables", "which tables exist"), ("describe_table", "columns and sample rows"),
                                  ("run_sql", "run one read-only SELECT")])]
    for g, (gname, tools) in enumerate(groups):
        y0 = 1.55 + g * 2.7
        text(s, f"Group {gname}", 6.3, y0, 6.4, 0.35, [(gname.upper(), 13, True, MAROON)])
        for i, (n, dsc) in enumerate(tools):
            y = y0 + 0.42 + i * 0.72
            box(s, f"Tool {n}", 6.3, y, 2.6, 0.6, [(n, 14, True, WHITE)], fill=BLUE, radius=0.2)
            text(s, f"Tool desc {n}", 9.1, y + 0.13, 3.65, 0.4, [(dsc, 15, False, INK)])


def tools_call(d):
    s = d.slide("How a tool call works", SEC_D,
                "Walk through the five boxes. The model never touches the database itself. It writes a small request: the tool name and the inputs. "
                "Our code runs it and sends the result back. The model can repeat this a few times, then writes the answer. "
                "Good tools have a clear name, a description that says when to use them, few inputs, and are safe by default.", tag="BUILT")
    flow(s, "Tool call flow", 0.6, 1.55, 12.13, 1.3,
         [("Question", "from the user"), ("Model picks", "which tool + inputs"), ("Harness runs", "the real function"),
          ("Result back", "to the model"), ("Answer", "with sources")],
         fills=[WHITE, WHITE, WHITE, WHITE, BLUE], gap=0.4, tsize=16, dsize=12)
    text(s, "Code title 1", 0.6, 3.15, 6.0, 0.35, [("1. WE WRITE THE TOOL (PYTHON)", 12, True, MUTED)])
    code(s, "Code: tool", 0.6, 3.55, 6.0, 1.75,
         '@mcp.tool()\ndef run_sql(sql: str) -> dict:\n    """Run one read-only SELECT on the\n    sales database. Max 200 rows."""\n    return safe_query(sql)', size=14)
    text(s, "Code title 2", 6.9, 3.15, 5.83, 0.35, [("2. THE MODEL ONLY SENDS THIS", 12, True, MUTED)])
    code(s, "Code: call", 6.9, 3.55, 5.83, 1.75,
         '{\n  "tool": "run_sql",\n  "args": {"sql":\n    "SELECT COUNT(*) FROM orders"}\n}', size=14)
    tips = [("Clear name", "run_sql, not tool_2"), ("Say when to use it", "the description guides the model"),
            ("Few inputs", "simple and typed"), ("Safe by default", "read-only, row limits")]
    for i, (h, b) in enumerate(tips):
        card(s, f"Tip {h}", 0.6 + i * 3.08, 5.6, 2.9, 1.25, h, b, hsize=16, bsize=14, fill=GREEN_FILL, hcolor=GREEN)
