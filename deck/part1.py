"""Slides 1-22: welcome, AI basics, LLMs, agents, personas / skills / plugins."""
from lib import *  # noqa: F401,F403


# ------------------------------------------------------------------ A. welcome
def s01_title(d):
    s = d.prs.slides.add_slide(d.L_TITLE)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY)
    text(s, "Tag", 0.8, 2.0, 6.2, 0.4, [("NOW, OUR REAL PROJECT", 14, True, "7FB2EA")])
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.8), Inches(2.5), Inches(6.3), Inches(1.75)
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = TOP
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.alignment = LEFT
    r = p.add_run()
    r.text = "From zero to deployed AI agents"
    r.font.size, r.font.bold, r.font.name = Pt(48), True, FONT
    r.font.color.rgb = rgb(WHITE)
    sub = s.placeholders[1]
    sub.left, sub.top, sub.width, sub.height = Inches(0.8), Inches(4.4), Inches(6.1), Inches(1.2)
    set_text(sub, [("How modern AI works, and how we built one that answers from documents and a database.", 20, False, "CFE0F5")],
             align=LEFT, anchor=TOP, margins=(0, 0, 0, 0))
    box(s, "Illustration: PDF", 7.6, 1.55, 1.5, 1.95, [], fill=WHITE, shape=MSO_SHAPE.FOLDED_CORNER)
    for i, wd in enumerate((1.0, 1.0, 0.7, 1.0, 0.8)):
        box(s, f"Illustration: PDF line {i + 1}", 7.85, 1.95 + i * 0.3, wd, 0.1, [], fill=GREYLINE, shape=MSO_SHAPE.RECTANGLE)
    text(s, "Label: PDFs", 7.2, 3.6, 2.3, 0.4, [("5 policy PDFs", 14, False, "CFE0F5")], align=CENTER)
    box(s, "Illustration: database", 7.65, 4.5, 1.4, 1.6, [], fill=WHITE, shape=MSO_SHAPE.CAN)
    text(s, "Label: database", 7.2, 6.2, 2.3, 0.4, [("Sales database", 14, False, "CFE0F5")], align=CENTER)
    box(s, "Illustration: AI agent", 10.0, 3.0, 1.9, 1.9, [("AI", 28, True, WHITE), ("agent", 16, False, WHITE)], fill=BLUE, shape=MSO_SHAPE.OVAL)
    box(s, "Illustration: answer", 10.0, 5.55, 2.8, 0.95, [("Answer with sources", 16, True, NAVY)], fill=WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT)
    arrow(s, "Arrow: PDFs to agent", 9.2, 2.6, 10.1, 3.45, color="7FB2EA", width=2.25)
    arrow(s, "Arrow: database to agent", 9.15, 5.2, 10.1, 4.5, color="7FB2EA", width=2.25)
    arrow(s, "Arrow: agent to answer", 10.95, 4.95, 10.95, 5.5, color="7FB2EA", width=2.25)
    s.notes_slide.notes_text_frame.text = (
        "We now know what RAG is. Let us use it on a real project. Our agent reads 5 policy PDFs and a sales database, "
        "and answers one question with sources. Everything from here on is something we actually built and tested.")
    logo(s, 11.25, 0.3, 1.75, panel=True)


def s02_problem(d):
    s = d.slide("One question no tool can answer today", "A. The problem",
                "Today we learn how to automate the middle box. A support worker opens the PDF in one window, asks a colleague for a database query, "
                "and joins the two answers by hand. Plain RAG only reads documents, so it cannot answer this alone. Next we see how an agent uses both.")
    box(s, "Question card", 0.6, 1.55, 12.13, 1.05, [("“Which late deliveries get a refund, and how much do we owe?”", 26, True, WHITE)], fill=NAVY, radius=0.1)
    box(s, "Question", 0.6, 3.35, 2.1, 1.2, [("Question", 16, True, INK)], fill=WHITE, border=BLUE)
    box(s, "Source: PDF", 3.4, 2.95, 3.0, 1.0, [("Policy PDF", 16, True, INK), ("holds the rule", 13, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Source: database", 3.4, 4.2, 3.0, 1.0, [("Database", 16, True, INK), ("holds the facts", 13, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Human step", 7.2, 3.35, 3.0, 1.2, [("A person joins them", 16, True, AMBER_INK), ("by hand", 14, False, AMBER_INK)], fill=AMBER_FILL, border=AMBER, dash=True)
    box(s, "Answer", 10.8, 3.35, 1.93, 1.2, [("Answer", 16, True, WHITE)], fill=BLUE)
    arrow(s, "a1", 2.7, 3.7, 3.4, 3.45)
    arrow(s, "a2", 2.7, 4.2, 3.4, 4.7)
    arrow(s, "a3", 6.4, 3.45, 7.2, 3.8)
    arrow(s, "a4", 6.4, 4.7, 7.2, 4.15)
    arrow(s, "a5", 10.2, 3.95, 10.8, 3.95)
    example(s, 0.6, 5.55, 12.13, 1.35,
            "A support worker opens the policy PDF in one window, asks a colleague to run a database query, and joins the two answers by hand. "
            "Next we see how an agent does that middle step for us.")


# ------------------------------------------------------------------ B. AI basics
def s03_map(d):
    s = d.slide("The AI map", "B. AI, ML, deep learning, generative AI",
                "Think of circles inside circles. AI is the big idea. Machine learning is one way to build AI. Deep learning is one kind of machine learning. "
                "Generative AI is deep learning that creates new things. Today we live in the smallest circle, plus the tools around it.")
    cx, cy = 3.5, 4.25
    for name, dia, fill, col in (("AI", 5.3, PALE, BLUE), ("Machine learning", 4.2, "D3E4F8", BLUE), ("Deep learning", 3.1, "9CC4EE", NAVY), ("Generative AI", 2.0, BLUE, WHITE)):
        box(s, f"Ring: {name}", cx - dia / 2, cy - dia / 2, dia, dia, [], fill=fill, shape=MSO_SHAPE.OVAL)
    text(s, "Label AI", cx - 1.2, cy - 2.55, 2.4, 0.35, [("AI", 16, True, BLUE)], align=CENTER)
    text(s, "Label ML", cx - 1.4, cy - 2.05, 2.8, 0.35, [("Machine learning", 15, True, BLUE)], align=CENTER)
    text(s, "Label DL", cx - 1.2, cy - 1.5, 2.4, 0.35, [("Deep learning", 15, True, NAVY)], align=CENTER)
    text(s, "Label GenAI", cx - 0.9, cy - 0.3, 1.8, 0.6, [("Generative", 15, True, WHITE), ("AI", 15, True, WHITE)], align=CENTER)
    rows = [("AI", "Machines that do smart tasks.", "Example: a chess program."),
            ("Machine learning", "Learns from data.", "Example: a spam filter."),
            ("Deep learning", "Networks with many layers.", "Example: unlocking a phone with your face."),
            ("Generative AI", "Creates text, images and code.", "Example: writing an email for you.")]
    for i, (h, a, b) in enumerate(rows):
        card(s, f"Level: {h}", 7.0, 1.55 + i * 1.36, 5.73, 1.22, h, [a, b], hsize=17, bsize=14)


def s04_learn(d):
    s = d.slide("How machines learn", "B. AI, ML, deep learning, generative AI",
                "There are three ways. Supervised: the machine sees examples with the right answers. Unsupervised: it finds groups with no answers. "
                "Reinforcement: it learns by trying and getting points. Most business machine learning is supervised, such as fraud or churn prediction.")
    cols = [("Supervised", "Learns from examples that come with answers.", "Show 10,000 emails marked spam or not spam."),
            ("Unsupervised", "Finds groups in data that has no answers.", "Group shoppers by what they buy."),
            ("Reinforcement", "Learns by trying and getting points.", "A game program gets points when it wins.")]
    for i, (h, how, ex) in enumerate(cols):
        x = 0.6 + i * 4.1
        box(s, f"Panel {h}", x, 1.55, 3.93, 4.5, [], fill=LIGHT, radius=0.05)
        if i == 0:
            for j, (lab, fc) in enumerate((("spam", RED_FILL), ("ok", GREEN_FILL), ("spam", RED_FILL))):
                box(s, f"Email {j}", x + 0.45 + j * 1.1, 1.8, 0.95, 0.6, [(lab, 14, True, INK)], fill=fc, border=GREYLINE, radius=0.2)
        elif i == 1:
            for (dx, dy, col) in ((0.5, 0.2, BLUE), (0.8, 0.45, BLUE), (0.6, 0.55, BLUE), (1.9, 0.25, AMBER), (2.15, 0.5, AMBER), (1.95, 0.6, AMBER), (3.1, 0.3, GREEN), (3.3, 0.55, GREEN), (3.05, 0.6, GREEN)):
                box(s, f"Dot {dx}{dy}", x + dx, 1.85 + dy, 0.26, 0.26, [], fill=col, shape=MSO_SHAPE.OVAL)
        else:
            box(s, "Try", x + 0.5, 1.9, 1.3, 0.6, [("try a move", 13, True, INK)], fill=WHITE, border=BLUE, radius=0.2)
            box(s, "Points", x + 2.2, 1.9, 1.3, 0.6, [("+1 point", 13, True, WHITE)], fill=GREEN, radius=0.2)
            arrow(s, "Try to points", x + 1.8, 2.2, x + 2.2, 2.2)
        text(s, f"Title {h}", x + 0.3, 2.85, 3.3, 0.45, [(h, 22, True, BLUE)])
        text(s, f"How {h}", x + 0.3, 3.4, 3.35, 0.9, [(how, 16, False, INK)])
        text(s, f"Ex {h}", x + 0.3, 4.4, 3.35, 1.5, [("Example", 12, True, MUTED), (ex, 15, False, INK)], gap=2)
    box(s, "Note", 0.6, 6.25, 12.13, 0.6, [("Most business machine learning is supervised, like fraud or churn prediction.", 15, True, NAVY)], fill=PALE, radius=0.3)


def s05_neural(d):
    s = d.slide("Neural networks and deep learning", "B. AI, ML, deep learning, generative AI",
                "A neural network is layers of numbers called weights. Training means changing the weights until the answers get better. "
                "Deep just means many layers. The dotted line at the bottom is training: when the answer is wrong, we change the weights.")
    xs, counts = [0.9, 2.7, 4.5, 6.3, 8.1], [3, 4, 4, 3, 2]
    ys = []
    for c in counts:
        top = 3.45 - (c - 1) * 0.5
        ys.append([top + k * 1.0 for k in range(c)])
    for li in range(4):
        for ya in ys[li]:
            for yb in ys[li + 1]:
                arrow(s, "link", xs[li] + 0.18, ya, xs[li + 1] - 0.18, yb, color=GREYLINE, width=0.75, head=False)
    for li, col in enumerate(xs):
        for ya in ys[li]:
            box(s, f"Node {li}", col - 0.18, ya - 0.18, 0.36, 0.36, [], fill=BLUE if 0 < li < 4 else NAVY, shape=MSO_SHAPE.OVAL)
    for xx, lab in zip(xs, ("Input", "Layer 1", "Layer 2", "Layer 3", "Output")):
        text(s, f"Layer label {lab}", xx - 0.7, 5.15, 1.4, 0.3, [(lab, 13, True, MUTED)], align=CENTER)
    text(s, "Input hint", 0.1, 5.45, 1.8, 0.5, [("pixels, words", 12, False, MUTED)], align=CENTER)
    text(s, "Output hint", 7.2, 5.45, 1.8, 0.5, [("cat? 92%", 12, False, MUTED)], align=CENTER)
    arrow(s, "Feedback", 8.1, 6.25, 0.9, 6.25, color=AMBER, width=2.25, dash=True)
    arrow(s, "Feedback up left", 0.9, 6.25, 0.9, 5.95, color=AMBER, width=2.25, dash=True, head=False)
    arrow(s, "Feedback up right", 8.1, 5.95, 8.1, 6.25, color=AMBER, width=2.25, dash=True, head=False)
    text(s, "Feedback label", 2.2, 6.38, 5.5, 0.35, [("wrong answer? change the weights, then try again", 13, True, AMBER_INK)], align=CENTER)
    card(s, "How training works", 9.4, 1.55, 3.33, 2.4, "Training", ["A network is layers of numbers called weights.", "Training changes the weights until the answers get better."], hsize=18)
    example(s, 9.4, 4.15, 3.33, 2.7, "Teaching a child what a cat is. Show many cats. Each time the child is wrong, correct them. Slowly the child gets it right.")


def s06_transformers(d):
    s = d.slide("Transformers, the big idea from 2017", "B. AI, ML, deep learning, generative AI",
                "A transformer reads all the words at once and decides which words are linked. This is called attention. "
                "The paper was named Attention Is All You Need, in 2017. Every big model today is a larger transformer.")
    words1 = ["The", "bank", "raised", "interest", "rates"]
    words2 = ["we", "sat", "on", "the", "river", "bank"]
    for i, w in enumerate(words1):
        hi = w in ("bank", "rates")
        box(s, f"S1 {w}", 0.6 + i * 1.3, 1.65, 1.2, 0.55, [(w, 16, True, WHITE if hi else INK)], fill=BLUE if hi else GREYFILL, radius=0.2)
    bracket(s, "Link 1", 0.6 + 1 * 1.3 + 0.6, 0.6 + 4 * 1.3 + 0.6, 2.25, 0.4)
    text(s, "Meaning 1", 0.6, 2.8, 6.5, 0.4, [("bank = a place for money (linked to “rates”)", 14, False, MUTED)])
    for i, w in enumerate(words2):
        hi = w in ("river", "bank")
        box(s, f"S2 {w}", 0.6 + i * 1.3, 3.55, 1.2, 0.55, [(w, 16, True, WHITE if hi else INK)], fill=BLUE if hi else GREYFILL, radius=0.2)
    bracket(s, "Link 2", 0.6 + 4 * 1.3 + 0.6, 0.6 + 5 * 1.3 + 0.6, 4.15, 0.4)
    text(s, "Meaning 2", 0.6, 4.7, 7.6, 0.4, [("bank = the side of a river (linked to “river”)", 14, False, MUTED)])
    example(s, 8.7, 1.55, 4.03, 3.5, "“The bank raised interest rates” and “we sat on the river bank”. Attention is how the model knows which bank is meant.", bsize=18)
    flow(s, "Pipeline", 0.6, 5.5, 12.13, 1.1, [("Text in", ""), ("Tokens", "small pieces"), ("Embeddings", "numbers for meaning"), ("Attention layers", "which words are linked?"), ("Next word chances", "")],
         fills=[WHITE, WHITE, WHITE, BLUE, WHITE])


# ------------------------------------------------------------------ C. LLMs
def s07_llm(d):
    s = d.slide("What an LLM really is", "C. LLMs, big models, open models",
                "A large language model guesses the next token, again and again. It does not look things up. It writes text that sounds right. "
                "That is why it can sound sure and still be wrong. The chances on the slide are only an illustration.")
    box(s, "Prompt", 0.6, 1.6, 3.4, 0.9, [("The refund window is", 18, True, INK)], fill=GREYFILL, radius=0.15)
    box(s, "LLM", 4.4, 1.6, 1.6, 0.9, [("LLM", 20, True, WHITE)], fill=NAVY, radius=0.15)
    arrow(s, "Prompt to LLM", 4.0, 2.05, 4.4, 2.05)
    text(s, "Guess label", 0.6, 2.85, 6.0, 0.35, [("The model guesses the next token (illustrative chances):", 14, True, MUTED)])
    for i, (tok, pct) in enumerate((("30", 62), ("14", 18), ("7", 12), ("60", 8))):
        y = 3.35 + i * 0.62
        text(s, f"Token {tok}", 0.6, y, 0.9, 0.45, [(tok, 16, True, INK)], anchor=MIDDLE)
        box(s, f"Bar {tok}", 1.5, y + 0.03, 4.6 * pct / 62, 0.4, [], fill=BLUE if i == 0 else SKY, shape=MSO_SHAPE.RECTANGLE)
        text(s, f"Pct {tok}", 1.6 + 4.6 * pct / 62, y, 0.9, 0.45, [(f"{pct}%", 14, False, MUTED)], anchor=MIDDLE)
    box(s, "Output", 0.6, 5.95, 5.5, 0.7, [("The refund window is 30 ... and it repeats", 15, True, NAVY)], fill=PALE, radius=0.2)
    defs = [("Token", "a small piece of a word"), ("Context window", "how much text it can read at once"),
            ("Temperature", "how random the answer is"), ("Training vs inference", "learning vs using it")]
    for i, (h, b) in enumerate(defs):
        card(s, f"Term {h}", 7.0, 1.55 + i * 1.02, 5.73, 0.9, None, [f"{h}: {b}"], fill=LIGHT, bsize=15, anchor=MIDDLE)
    example(s, 7.0, 5.7, 5.73, 1.2, "The word suggestions on your phone keyboard, but trained on a huge part of the internet.")


def s08_frontier(d):
    s = d.slide("Frontier models", "C. LLMs, big models, open models",
                "Frontier means the best available today. It changes every few months, so learn the ideas, not the names. "
                "Verify current model names before presenting.")
    cards = [("Reasoning", "Works through hard problems step by step."), ("Writing code", "Writes, reviews and fixes software."),
             ("Images and long documents", "Reads pictures and hundreds of pages.")]
    for i, (h, b) in enumerate(cards):
        x = 0.6 + i * 4.1
        card(s, f"Strength {h}", x, 1.55, 3.93, 2.3, h, b, hsize=22, bsize=18, fill=LIGHT)
    card(s, "How you use them", 0.6, 4.15, 6.0, 2.7, "How you use them", ["You use them through an API.", "You pay for each use.", "You do not get the model files."], hsize=20, bsize=19, fill=PALE)
    example(s, 6.9, 4.15, 5.83, 2.7, "A developer asks the model to review code. A lawyer asks it to summarize a 200-page contract.", bsize=19)


def s09_open(d):
    s = d.slide("Open models, and three ways to use any model", "C. LLMs, big models, open models",
                "Open-weight models share their model files, so you can run them yourself. Open-weight is not always open-source, so read the license. "
                "In our own Gemini account we even saw Gemma models, which are open-weight. Verify the family names before presenting.")
    card(s, "Open-weight", 0.6, 1.55, 5.4, 2.2, "Open-weight models", ["The model files are shared, so you can run them yourself."], hsize=18, bsize=16, fill=LIGHT)
    for i, fam in enumerate(("Llama", "Qwen", "Gemma", "DeepSeek", "Mistral")):
        pill(s, f"Family {fam}", 0.85 + (i % 3) * 1.65, 2.75 + (i // 3) * 0.5, 1.5, 0.4, fam)
    ways = [("Chat app", "the easiest way"), ("Hosted API", "paid, or a free tier"), ("Run it yourself", "your machine, your data")]
    for i, (h, b) in enumerate(ways):
        x = 6.4 + i * 2.15
        box(s, f"Door {h}", x, 1.55, 2.0, 2.2, [(h, 17, True, WHITE), (b, 13, False, "DCE9F8")], fill=BLUE if i < 2 else NAVY, radius=0.12, gap=4)
    text(s, "Doors label", 6.4, 3.85, 6.3, 0.35, [("Three ways to use any model", 14, True, MUTED)], align=CENTER)
    example(s, 0.6, 4.55, 7.2, 2.3, "A hospital cannot send patient notes to an outside company. So it runs an open model on its own servers.", bsize=20)
    card(s, "License note", 8.1, 4.55, 4.63, 2.3, "Careful", ["Open-weight is not always open-source.", "Read the license before you use a model."], hsize=19, bsize=18, fill=AMBER_FILL)


def s10_companies(d):
    s = d.slide("How companies use LLMs", "C. LLMs, big models, open models",
                "Most companies use the same recipe: a model, plus company data, plus the power to act, plus safety rules. "
                "The model is only one part. The rest of today is about the other parts.")
    cx, cy = 3.6, 4.2
    box(s, "LLM center", cx - 0.9, cy - 0.9, 1.8, 1.8, [("LLM", 24, True, WHITE)], fill=NAVY, shape=MSO_SHAPE.OVAL)
    sats = [("Company data", "documents, databases", 3.6, 1.6), ("Tools and actions", "search, query, send", 0.6, 5.5), ("Safety rules", "permissions, review", 5.35, 5.5)]
    for name, det, sx, sy in sats:
        box(s, f"Satellite {name}", sx - 0.0, sy, 2.3, 1.0, [(name, 15, True, INK), (det, 12, False, MUTED)], fill=WHITE, border=BLUE, radius=0.15)
    arrow(s, "to data", cx, 2.6, cx, 3.3, head=False, color=BLUE)
    arrow(s, "to tools", 1.75, 5.5, 2.9, 4.7, head=False, color=BLUE)
    arrow(s, "to safety", 6.5, 5.5, 4.3, 4.7, head=False, color=BLUE)
    card(s, "Common uses", 8.0, 1.55, 4.73, 3.0, "Common uses", ["Support assistants", "Coding helpers", "Document search", "Data analysis", "Report writing"], hsize=18, bsize=16, fill=LIGHT)
    example(s, 8.0, 4.75, 4.73, 2.1, "A bank assistant reads the policy documents, checks the account data, and writes a draft reply. A person approves it.")


def s11_limits(d):
    s = d.slide("What a plain LLM cannot do", "C. LLMs, big models, open models",
                "These limits lead to the next two sections. Real example from our project: the model name we first chose was shut down for new users, "
                "and our free key allowed only 15 requests per minute. Real systems must handle changing models and limits.")
    lim = ["It can make things up", "It has a knowledge cut-off date", "It can read only a limited amount at once", "It costs money for every use", "It can leak private data if you are careless"]
    for i, l in enumerate(lim):
        box(s, f"Limit {i}", 0.6, 1.55 + i * 0.78, 5.6, 0.64, [(l, 16, True, INK)], fill=RED_FILL, radius=0.2, align=LEFT, margins=(0.25, 0.05, 0.1, 0.05))
    box(s, "Problem 1", 6.8, 1.55, 2.7, 1.2, [("It does not know our private data", 15, True, INK)], fill=GREYFILL, border=GREYLINE)
    box(s, "Fix 1", 10.2, 1.55, 2.53, 1.2, [("Fix 1: RAG", 17, True, WHITE), ("give it the documents", 13, False, "DCE9F8")], fill=BLUE)
    arrow(s, "p1", 9.5, 2.15, 10.2, 2.15)
    box(s, "Problem 2", 6.8, 3.05, 2.7, 1.2, [("It cannot act or calculate", 15, True, INK)], fill=GREYFILL, border=GREYLINE)
    box(s, "Fix 2", 10.2, 3.05, 2.53, 1.2, [("Fix 2: agents", 17, True, WHITE), ("and tools", 13, False, "DCE9F8")], fill=BLUE)
    arrow(s, "p2", 9.5, 3.65, 10.2, 3.65)
    example(s, 6.8, 4.65, 5.93, 2.2, "In our own project the model name we first chose was shut down for new users, and our free key allowed only 15 requests per minute. Real systems must handle changes like this.", label="From our project")


# ------------------------------------------------------------------ D. Agents
def s12_agent_vs_llm(d):
    s = d.slide("A plain LLM is not an agent", "D. Agent = LLM + harness",
                "An LLM answers once. An agent works step by step toward a goal. The difference is everything we build around the model.")
    box(s, "Panel LLM", 0.6, 1.55, 5.7, 3.6, [], fill=LIGHT, radius=0.05)
    text(s, "LLM title", 0.9, 1.7, 5.0, 0.5, [("A plain LLM: one answer", 20, True, BLUE)])
    box(s, "Ask", 0.95, 3.0, 1.9, 0.9, [("Question", 16, True, INK)], fill=WHITE, border=BLUE)
    box(s, "One answer", 3.6, 3.0, 2.3, 0.9, [("Answer", 16, True, WHITE)], fill=BLUE)
    arrow(s, "ask to answer", 2.85, 3.45, 3.6, 3.45)
    box(s, "Panel agent", 6.7, 1.55, 6.03, 3.6, [], fill=PALE, radius=0.05)
    text(s, "Agent title", 7.0, 1.7, 5.4, 0.5, [("An agent: works in steps", 20, True, BLUE)])
    flow(s, "Agent step", 6.95, 2.8, 5.55, 1.1, [("Goal", ""), ("Look up", ""), ("Do math", ""), ("Check", ""), ("Answer", "")], fills=[WHITE, WHITE, WHITE, WHITE, BLUE], gap=0.15, tsize=13)
    arrow(s, "Loop back", 11.3, 3.95, 8.6, 3.95, color=AMBER, dash=True, width=2)
    text(s, "Loop label", 8.2, 4.1, 4.3, 0.4, [("repeat until the goal is reached", 12, False, AMBER_INK)], align=CENTER)
    example(s, 0.6, 5.4, 12.13, 1.45, "Asking a friend one question is like using an LLM. Hiring an assistant who looks things up, does the math, and comes back with an answer is like an agent.")


def s13_harness(d):
    s = d.slide("Agent = LLM + harness", "D. Agent = LLM + harness",
                "Think of an engine inside a car. The engine alone cannot drive anywhere. The harness is the rest of the car: the loop that keeps going, the tools, "
                "the memory, the control over what goes into the prompt, and the safety rules. In our project the harness is a loop that can call six tools and stops after eight steps.", tag="BUILT")
    text(s, "Explanation", 0.6, 1.6, 5.3, 2.9, [("The LLM is the engine.", 24, True, BLUE), ("It reads and writes language.", 16, False, INK), ("", 10, False, INK),
                                               ("The harness is everything around it.", 24, True, BLUE), ("The loop, the tools, the memory, the context control and the safety rules.", 16, False, INK)])
    box(s, "Analogy card", 0.6, 4.55, 5.3, 1.7, [("Think of a car", 16, True, BLUE), ("An engine alone cannot drive anywhere. The body, wheels, steering and brakes make it useful.", 16, False, INK)],
        fill=PALE, radius=0.1, align=LEFT, margins=(0.25, 0.1, 0.25, 0.1))
    text(s, "Caption", 0.6, 6.45, 5.3, 0.5, [("In our project: a loop that can call 6 tools and stops after 8 steps.", 12, False, MUTED)])
    box(s, "Harness container", 6.3, 1.6, 6.5, 5.25, [], fill=LIGHT, border=BLUE, border_w=2.25, radius=0.05)
    text(s, "Harness label", 6.6, 1.7, 3.0, 0.4, [("THE HARNESS", 14, True, BLUE)])
    box(s, "LLM engine", 6.6, 3.15, 2.0, 2.4, [("LLM", 30, True, WHITE), ("the engine", 14, False, "CFE0F5")], fill=NAVY, radius=0.12)
    for i, (n, dt) in enumerate((("Loop", "think, act, look, repeat"), ("Tools", "search documents, run SQL"), ("Memory", "saved chat state"),
                                 ("Context control", "keep the prompt short and clear"), ("Safety rules", "read-only data, limits, review"))):
        py = 2.2 + i * 0.88
        box(s, f"Harness part {n}", 9.3, py, 3.25, 0.74, [(n, 15, True, INK), (dt, 12, False, MUTED)], fill=WHITE, border=BLUE, radius=0.2)
        arrow(s, f"LLM to {n}", 8.6, 4.35, 9.3, py + 0.37, color=BLUE)


def s14_langchain(d):
    s = d.slide("LangChain, the building blocks", "D. Agent = LLM + harness",
                "LangChain is a toolbox with ready-made parts. The text in quotes in a tool is not just a comment: the model reads it to decide when to use the tool.", tag="BUILT")
    for i, (h, b, col) in enumerate((("Model connector", "talks to Gemini", BLUE), ("Tool", "a function the model can call", "2F7FD1"), ("Prompt", "the instructions", "5B9BE3"), ("Retriever", "finds the right text", "8DBCEE"))):
        box(s, f"Brick {h}", 0.6 + i * 3.08, 1.6, 2.9, 1.3, [(h, 17, True, WHITE if i < 3 else NAVY), (b, 13, False, "EAF2FC" if i < 3 else NAVY)], fill=col, radius=0.1)
    code(s, "Code: tool", 0.6, 3.25, 7.4, 2.3, '@tool\ndef run_sql(sql: str):\n    """Run ONE read-only SQLite SELECT."""\n    return retrieval.run_sql(sql)', size=16)
    text(s, "Code hint", 0.6, 5.7, 7.4, 0.6, [("The text in the triple quotes is read by the model. It decides when to use this tool.", 14, False, MUTED)])
    example(s, 8.4, 3.25, 4.33, 3.1, "Lego bricks. You build faster because you do not make every brick yourself.", bsize=20)


def s15_langgraph(d):
    s = d.slide("LangGraph, the agent as a map", "D. Agent = LLM + harness",
                "In LangGraph you draw the agent as a map: steps, arrows and shared state. Think of a subway map: the agent moves from station to station "
                "until it reaches the last stop. Five lines define the whole loop. The tool can even draw this picture for us.", tag="BUILT")
    box(s, "Start", 0.6, 3.0, 1.1, 0.7, [("start", 14, True, INK)], fill=GREYFILL, shape=MSO_SHAPE.OVAL)
    box(s, "Agent node", 2.4, 2.7, 1.9, 1.3, [("agent", 17, True, WHITE), ("LLM + tools", 13, False, "DCE9F8")], fill=BLUE)
    box(s, "Tools node", 2.4, 5.0, 1.9, 1.3, [("tools", 17, True, INK), ("run them", 13, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "End", 5.2, 3.0, 1.1, 0.7, [("end", 14, True, INK)], fill=GREYFILL, shape=MSO_SHAPE.OVAL)
    arrow(s, "start to agent", 1.7, 3.35, 2.4, 3.35)
    arrow(s, "agent to end", 4.3, 3.35, 5.2, 3.35)
    text(s, "done label", 4.3, 2.95, 0.9, 0.3, [("done", 12, False, MUTED)], align=CENTER)
    arrow(s, "agent to tools", 3.0, 4.0, 3.0, 5.0, color=BLUE)
    arrow(s, "tools to agent", 3.7, 5.0, 3.7, 4.0, color=BLUE)
    text(s, "needs tool", 0.5, 4.3, 2.4, 0.3, [("needs a tool?", 12, False, MUTED)], align=RIGHT)
    code(s, "Code: graph", 6.9, 1.6, 5.83, 2.9, 'g = StateGraph(MessagesState)\ng.add_node("agent", agent_node)\ng.add_node("tools", ToolNode(tools))\ng.add_conditional_edges("agent", tools_condition)\ng.add_edge("tools", "agent")', size=15)
    example(s, 6.9, 4.75, 5.83, 2.1, "A subway map. The agent travels from station to station (think, use a tool) until it reaches the last stop.", bsize=18)


def s16_vs(d):
    s = d.slide("LangChain agent vs LangGraph agent", "D. Agent = LLM + harness",
                "They are not enemies. Today a LangChain agent actually runs on LangGraph inside. LangChain is the quick path, and LangGraph is the control panel. "
                "Many real products use both. Verify the exact library names before presenting, because they change.", tag="BUILT")
    rows = [["", "LangChain agent", "LangGraph agent"],
            ["What it is", "A ready-made agent: give it a model and tools", "An agent you draw yourself with steps and arrows"],
            ["Setup", "A few lines", "More code, more control"],
            ["Flow", "One simple loop", "Any flow: branches, loops, parallel steps"],
            ["Memory", "Basic", "Saved at every step (checkpoints)"],
            ["Human approval", "Possible with extra hooks", "Easy: pause at any step"],
            ["Many agents", "Hard", "Natural: each agent is one step"],
            ["Best for", "A quick start, simple assistants", "Complex, long, business-critical flows"],
            ["In our project", "We used its tool and model parts", "We drew the loop with it"]]
    table(s, "Comparison table", 0.6, 1.5, [2.2, 4.9, 5.03], rows, size=13, row_h=0.48)
    card(s, "Taxi", 0.6, 5.95, 5.95, 0.95, "LangChain agent = a taxi", "Say where you want to go.", hsize=14, bsize=13, fill=PALE)
    card(s, "Route", 6.78, 5.95, 5.95, 0.95, "LangGraph agent = plan the route yourself", "You choose every stop and every turn.", hsize=14, bsize=13, fill=PALE)


def s17_two_ways(d):
    s = d.slide("Our agent built two ways", "D. Agent = LLM + harness",
                "We built the same agent as a hand-written loop and again with LangGraph. Both used the same tools in the same order on all three test questions and the answers matched. "
                "LangGraph added saved memory, so the follow-up and for Gold worked without sending the old chat again. The cost was about 31 MB more memory.", tag="BUILT")
    box(s, "Lane 1 label", 0.6, 1.6, 2.6, 1.0, [("Hand-written loop", 16, True, INK)], fill=GREYFILL)
    flow(s, "Plain", 3.5, 1.6, 9.2, 1.0, [("Question", ""), ("Call model", ""), ("Run tool", ""), ("Answer", "")], fills=[WHITE, WHITE, WHITE, WHITE], gap=0.5)
    box(s, "Lane 2 label", 0.6, 3.0, 2.6, 1.0, [("LangGraph", 16, True, WHITE)], fill=BLUE)
    flow(s, "Graph", 3.5, 3.0, 9.2, 1.0, [("Question", ""), ("agent step", ""), ("tools step", ""), ("Answer + memory", "")], fills=[WHITE, WHITE, WHITE, BLUE], gap=0.5)
    for i, (h, b) in enumerate((("Same answers", "Same tools, same order, on all 3 test questions."), ("Saved memory", "“And for Gold?” worked with no old chat re-sent."), ("Small cost", "About 31 MB more memory."))):
        card(s, f"Result {h}", 0.6 + i * 4.1, 4.5, 3.93, 2.2, h, b, hsize=21, bsize=18, fill=GREEN_FILL, hcolor=GREEN)


def s18_when(d):
    s = d.slide("When to use which", "D. Agent = LLM + harness",
                "Start with the simplest thing that works. Real products add a database for chat memory, short summaries of long chats, and automatic retries. "
                "LangGraph gives places to plug these in.")
    box(s, "Bike panel", 0.6, 1.55, 5.9, 3.7, [], fill=LIGHT, radius=0.05)
    text(s, "Bike title", 0.9, 1.7, 5.3, 0.5, [("A simple loop = a bicycle", 20, True, BLUE)])
    bullets(s, "Bike list", 0.9, 2.4, 5.3, 2.7, ["One user at a time", "Short tasks", "No saved memory needed", "Easy to read and teach"], size=20, gap=12)
    box(s, "Truck panel", 6.83, 1.55, 5.9, 3.7, [], fill=PALE, radius=0.05)
    text(s, "Truck title", 7.13, 1.7, 5.3, 0.5, [("A framework = a truck", 20, True, BLUE)])
    bullets(s, "Truck list", 7.13, 2.4, 5.3, 2.7, ["Memory across sessions", "A person approves a step", "Long-running work", "Many agents working together"], size=20, gap=12)
    example(s, 0.6, 5.5, 12.13, 1.35, "A bicycle is fine for the shop down the road. You need a truck only when you move house.", bsize=18)


# ------------------------------------------------------------------ E. Personas, skills, plugins
def s19_personas(d):
    s = d.slide("Personas", "E. Personas, skills, connectors, plugins",
                "A persona is a role. One employee wearing different hats. The server enforces the limits, not only the prompt: a tool outside the persona's list is never shown "
                "to the model, and it is refused if the model tries to call it.", tag="BUILT")
    for i, (h, b) in enumerate((("Support Agent", "6 tools"), ("Data Analyst", "SQL tools only"), ("Policy Advisor", "document tools only"))):
        box(s, f"Persona {h}", 0.6, 1.6 + i * 1.3, 3.2, 1.1, [(h, 17, True, INK), (b, 13, False, MUTED)], fill=WHITE, border=BLUE, radius=0.15)
        arrow(s, f"to agent {i}", 3.8, 2.15 + i * 1.3, 4.7, 3.4, color=BLUE)
    box(s, "Agent box", 4.7, 2.7, 2.2, 1.4, [("Agent", 20, True, WHITE), ("with that role", 13, False, "DCE9F8")], fill=BLUE)
    code(s, "Code: persona file", 7.3, 1.6, 5.43, 2.6, "---\nname: Policy Advisor\ntools: search_docs, list_documents,\n       get_document_page\nskills: docs-research\n---\nYou explain policies exactly.\nYou cannot see orders.", size=14)
    card(s, "Why", 0.6, 5.55, 5.9, 1.3, "Least privilege", "Give each role only the tools it needs.", hsize=16, bsize=15, fill=PALE)
    example(s, 6.83, 4.5, 5.9, 2.35, "One employee wearing different hats: support worker, data analyst, policy advisor.", bsize=20)


def s20_persona_results(d):
    s = d.slide("Persona test results", "E. Personas, skills, connectors, plugins",
                "This is called least privilege: give each role only what it needs. These are real results from our tests.", tag="BUILT")
    res = [("Policy Advisor", "Asked for customer revenue.", "Said no. Never touched SQL."),
           ("Data Analyst", "Asked for the refund window.", "Said no. Never touched the documents."),
           ("Support Agent", "Gold customer, 4 days late.", "Used the 10% credit and wrote a reply for the customer.")]
    for i, (h, q, a) in enumerate(res):
        x = 0.6 + i * 4.1
        card(s, f"Result {h}", x, 1.6, 3.93, 4.4, h, [f"Question: {q}", "", f"Result: {a}"], hsize=22, bsize=19, fill=LIGHT, margins=(0.22, 0.14, 0.9, 0.12))
        box(s, f"Check {h}", x + 3.3, 1.72, 0.45, 0.45, [("OK", 11, True, WHITE)], fill=GREEN, shape=MSO_SHAPE.OVAL, margins=(0, 0, 0, 0))
    box(s, "Note", 0.6, 6.25, 12.13, 0.6, [("The server blocks the tools, not just the prompt.", 16, True, NAVY)], fill=PALE, radius=0.3)


def s21_skills(d):
    s = d.slide("Skills and connectors", "E. Personas, skills, connectors, plugins",
                "A skill is a written playbook, like a recipe card. A connector is a link to data or an app. A recipe is useless without a kitchen, and a kitchen without a recipe makes a mess.", tag="BUILT")
    box(s, "Skill panel", 0.6, 1.55, 6.0, 5.3, [], fill=LIGHT, radius=0.04)
    text(s, "Skill title", 0.9, 1.7, 5.4, 0.45, [("Skill = a recipe card", 20, True, BLUE)])
    code(s, "Code: skill file", 0.9, 2.3, 5.4, 3.0, "---\nname: docs-plus-data\ndescription: Use when a question needs a\n  policy rule AND facts from the database.\n---\n1. Rule first (search_docs).\n2. Facts second (run_sql).\n3. Combine them.", size=13)
    text(s, "Skill note", 0.9, 5.6, 5.4, 1.1, [("A plain text file. Anyone can read it, review it and change it.", 17, False, INK)])
    box(s, "Connector panel", 6.9, 1.55, 5.83, 5.3, [], fill=PALE, radius=0.04)
    text(s, "Connector title", 7.2, 1.7, 5.3, 0.45, [("Connector = a link to data or an app", 20, True, BLUE)])
    box(s, "Agent", 7.2, 3.4, 1.7, 1.2, [("Agent", 17, True, WHITE)], fill=BLUE)
    box(s, "Connector", 9.4, 3.4, 1.2, 1.2, [("link", 15, True, INK)], fill=WHITE, border=BLUE, shape=MSO_SHAPE.OVAL)
    box(s, "Data", 11.1, 2.7, 1.45, 0.9, [("Documents", 13, True, INK)], fill=WHITE, border=BLUE)
    box(s, "App", 11.1, 4.1, 1.45, 0.9, [("Database", 13, True, INK)], fill=WHITE, border=BLUE)
    arrow(s, "a to c", 8.9, 4.0, 9.4, 4.0)
    arrow(s, "c to d", 10.6, 3.8, 11.1, 3.2)
    arrow(s, "c to a", 10.6, 4.2, 11.1, 4.55)
    text(s, "Connector note", 7.2, 5.4, 5.3, 1.3, [("The agent reaches data through the connector. Ours uses MCP (a few slides ahead).", 17, False, INK)])


def s22_plugins(d):
    s = d.slide("Plugins, the package", "E. Personas, skills, connectors, plugins",
                "A plugin puts skills, shortcuts and connector settings into one package, like a welcome kit for a new employee. Never put a password or token in a file you plan to share. "
                "Ours has 3 skills and 4 commands, and we made two versions: a safe one to share and a personal one with a secret inside.", tag="BUILT")
    box(s, "Skills", 0.6, 1.7, 2.4, 0.9, [("3 skills", 16, True, INK)], fill=WHITE, border=BLUE)
    box(s, "Commands", 0.6, 2.9, 2.4, 0.9, [("4 commands", 16, True, INK)], fill=WHITE, border=BLUE)
    box(s, "Plugin zip", 4.0, 2.1, 2.6, 1.3, [("Plugin zip", 18, True, WHITE), ("safe to share", 13, False, "DCE9F8")], fill=BLUE)
    box(s, "Upload", 7.6, 2.1, 2.2, 1.3, [("Upload to", 15, True, INK), ("Claude", 15, True, INK)], fill=WHITE, border=BLUE)
    arrow(s, "s to zip", 3.0, 2.15, 4.0, 2.6)
    arrow(s, "c to zip", 3.0, 3.35, 4.0, 2.95)
    arrow(s, "zip to upload", 6.6, 2.75, 7.6, 2.75)
    box(s, "Connector secret", 0.6, 4.4, 2.4, 0.9, [("Connector settings", 14, True, AMBER_INK), ("(a secret)", 12, False, AMBER_INK)], fill=AMBER_FILL, border=AMBER, dash=True)
    box(s, "Personal zip", 4.0, 4.3, 2.6, 1.1, [("Personal zip", 17, True, AMBER_INK), ("never share", 13, False, AMBER_INK)], fill=AMBER_FILL, border=AMBER, dash=True)
    arrow(s, "secret to zip", 3.0, 4.85, 4.0, 4.85, color=AMBER, dash=True)
    text(s, "Commands title", 10.1, 1.6, 2.6, 0.35, [("Our commands", 14, True, MUTED)])
    for i, c in enumerate(("/brightline:ask", "/brightline:policy", "/brightline:late-orders", "/brightline:customer")):
        box(s, f"Cmd {c}", 10.1, 2.0 + i * 0.55, 2.63, 0.45, [(c, 12, True, CODE_INK, MONO)], fill=CODE_BG, radius=0.3, margins=(0.05, 0, 0.05, 0))
    example(s, 0.6, 5.7, 12.13, 1.15, "A welcome kit for a new employee: the handbook, the login details and the shortcuts, all in one box.")
