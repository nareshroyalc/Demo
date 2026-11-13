"""Slides 37-53: streaming, demo, deployment, providers, wrap-up."""
from lib import *  # noqa: F401,F403

SEC_I, SEC_J, SEC_K, SEC_L = "I. Our architecture and the live demo", "J. Deploying on Render", "K. Model providers and self-hosting", "L. Wrap-up"


def s37_wait(d):
    s = d.slide("Streaming: show the work live", SEC_I,
                "An agent can take 5 to 20 seconds to answer. A blank screen for that long feels broken. Streaming shows the work while it happens: first the tool calls, then the answer as it is written. "
                "The agent is not faster. It only feels faster, and the audience can see how it thinks. The 19 seconds is from one test run of our combined question.", tag="BUILT")
    box(s, "No stream panel", 0.6, 1.55, 12.13, 2.0, [], fill=RED_FILL, radius=0.05)
    text(s, "No stream title", 0.9, 1.65, 6.0, 0.4, [("Without streaming", 18, True, RED)])
    flow(s, "Wait", 0.9, 2.3, 11.5, 0.95, [("Ask", ""), ("... about 19 seconds of nothing ...", ""), ("The full answer appears", "")], fills=[WHITE, WHITE, WHITE], borders=[RED, RED, RED], gap=0.5)
    box(s, "Stream panel", 0.6, 3.75, 12.13, 2.0, [], fill=GREEN_FILL, radius=0.05)
    text(s, "Stream title", 0.9, 3.85, 6.0, 0.4, [("With streaming", 18, True, GREEN)])
    flow(s, "Live", 0.9, 4.5, 11.5, 0.95, [("Ask", ""), ("Searching the policy...", ""), ("Looking at the tables...", ""), ("Running SQL...", ""), ("Answer types out", "")],
         fills=[WHITE, WHITE, WHITE, WHITE, GREEN], borders=[GREEN] * 5, gap=0.3, tsize=13)
    example(s, 0.6, 5.95, 7.0, 0.95, "A pizza tracker: you see making, baking, on the way.", bsize=16)
    card(s, "Same cost", 7.85, 5.95, 4.88, 0.95, "Same cost", "Same model calls and tokens. Only the delivery changes.", hsize=14, bsize=13, fill=GREEN_FILL, hcolor=GREEN)


def s38_how_stream(d):
    s = d.slide("How streaming works", SEC_I,
                "The server sends small messages, called events, while the agent works. The browser draws each one as it arrives. There are five kinds: start, step, result, token and done. "
                "The technology is called server-sent events: one normal web request that stays open. It is like live sports commentary: the commentator talks during the match, not after it.", tag="BUILT")
    xs = (1.9, 6.4, 10.9)
    for x, name in zip(xs, ("Browser", "Server /agent/stream", "Agent and tools")):
        box(s, f"Lifeline {name}", x - 1.3, 1.5, 2.6, 0.6, [(name, 14, True, WHITE)], fill=BLUE if name != "Browser" else NAVY, radius=0.2)
        arrow(s, f"Line {name}", x, 2.1, x, 6.85, color=GREYLINE, width=1.5, dash=True, head=False)

    def msg(y, x1, x2, label, color=MUTED, bold=False):
        arrow(s, f"Msg {label}", x1, y, x2, y, color=color, width=1.75)
        lo, hi = min(x1, x2), max(x1, x2)
        text(s, f"Label {label}", lo + 0.1, y - 0.33, hi - lo - 0.2, 0.3, [(label, 13, bold, INK)], align=CENTER)

    msg(2.55, xs[0], xs[1], "question")
    msg(2.95, xs[1], xs[2], "run the agent")
    msg(3.4, xs[2], xs[1], "steps and words come back as they happen", color=AMBER)
    for i, (lab, col) in enumerate((("step: search_docs", BLUE), ("result: 5 passages", BLUE), ("step: run_sql", BLUE), ("result: 3 rows", BLUE), ("token, token, token ...", GREEN), ("done: answer, sources, usage", NAVY))):
        msg(3.95 + i * 0.5, xs[1], xs[0], lab, color=col, bold=True)
    card(s, "Five events", 8.2, 4.1, 4.5, 2.7, "Five kinds of event", ["start, step, result", "token (answer words)", "done (the full result)"], hsize=15, bsize=15, fill=PALE)


def s39_timeline(d):
    s = d.slide("A real run, with times", SEC_I,
                "This is a real timeline from our test, one run on the free Gemini key. The question was: which delivered orders were late, and what credit does the policy give per band? "
                "The user sees the first action after about 2 seconds, not after 19. Notice the long gap before describe_table: that is the model thinking, and it varies from run to run, so say about.", tag="BUILT")
    x0, x1, y = 0.9, 12.4, 3.6
    scale = (x1 - x0) / 19.0
    arrow(s, "Time axis", x0, y, x1, y, color=MUTED, width=2.5, head=False)
    for t in (0, 5, 10, 15, 19):
        arrow(s, f"Tick {t}", x0 + t * scale, y - 0.08, x0 + t * scale, y + 0.08, color=MUTED, width=1.5, head=False)
        text(s, f"Tick label {t}", x0 + t * scale - 0.4, y + 0.12, 0.8, 0.3, [(f"{t} s", 12, False, MUTED)], align=CENTER)
    events = [(2.2, "search_docs", 1, BLUE), (3.0, "5 passages", -1, BLUE), (4.2, "list_tables", 2, BLUE), (15.2, "describe_table", 1, BLUE),
              (16.2, "run_sql: 3 rows", -1, BLUE), (17.9, "answer words", 2, GREEN), (18.6, "done", -2, NAVY)]
    for t, lab, level, col in events:
        cx = x0 + t * scale
        box(s, f"Dot {lab}", cx - 0.1, y - 0.1, 0.2, 0.2, [], fill=col, shape=MSO_SHAPE.OVAL)
        ly = y - 0.45 - 0.55 * level if level > 0 else y + 0.5 + 0.5 * (-level - 1) + 0.05
        top = ly if level > 0 else ly
        if level > 0:
            arrow(s, f"Leader {lab}", cx, y - 0.1, cx, ly + 0.3, color=col, width=1.25, head=False)
            text(s, f"Event {lab}", cx - 0.9, ly, 1.8, 0.3, [(f"{t:.1f} s  {lab}", 12, True, col)], align=CENTER)
        else:
            arrow(s, f"Leader {lab}", cx, y + 0.1, cx, ly, color=col, width=1.25, head=False)
            text(s, f"Event {lab}", cx - 0.9, ly, 1.8, 0.3, [(f"{t:.1f} s  {lab}", 12, True, col)], align=CENTER)
    card(s, "Takeaway 1", 0.6, 5.2, 5.9, 1.6, "First action after about 2 seconds", "Not after 19. The user sees progress at once.", hsize=18, bsize=16, fill=GREEN_FILL, hcolor=GREEN)
    card(s, "Takeaway 2", 6.83, 5.2, 5.9, 1.6, "The long gap is the model thinking", "It changes from run to run. Say “about”.", hsize=18, bsize=16, fill=AMBER_FILL, hcolor=AMBER_INK)


def s40_cost(d):
    s = d.slide("Does streaming cost more?", SEC_I,
                "No. It is the same work, delivered differently. The only way streaming could cost more is a bad design, such as asking the model twice. We do not do that. "
                "Be honest about the small downsides: more moving parts, and if the connection drops the user sees a partial answer. We did not measure the extra server work on a very small free plan.", tag="BUILT")
    rows = [["", "Without streaming", "With streaming"],
            ["Model calls", "the same", "the same"],
            ["Tokens billed", "the same", "the same"],
            ["Free limit (15 requests a minute)", "counts the same", "counts the same"],
            ["What the user feels", "waits for everything", "sees progress at once"]]
    table(s, "Cost table", 0.6, 1.55, [4.2, 3.9, 4.03], rows, size=16, row_h=0.62)
    example(s, 0.6, 4.9, 5.9, 1.95, "A parcel is the same parcel whether or not you get tracking updates.", bsize=19)
    card(s, "Honest downsides", 6.83, 4.9, 5.9, 1.95, "Small downsides", ["More moving parts.", "A dropped connection shows a partial answer.", "Answer words come at the end, after the tools."], hsize=17, bsize=15, fill=AMBER_FILL, hcolor=AMBER_INK)


def s41_stream_code(d):
    s = d.slide("A little code", SEC_I,
                "That is all of it: a generator on one side, a reader on the other. The server sends each event as one line of text. The browser reads the lines as they arrive.", tag="BUILT")
    text(s, "Server title", 0.6, 1.55, 6.0, 0.4, [("Server (Python, simplified)", 17, True, BLUE)])
    code(s, "Code: server", 0.6, 2.05, 6.0, 3.3, 'def generate():\n    for event in agent.stream(question):\n        # step, result, token, done\n        yield f"data: {json.dumps(event)}\\n\\n"\n\nreturn StreamingResponse(\n    generate(),\n    media_type="text/event-stream")', size=14)
    text(s, "Browser title", 6.95, 1.55, 5.8, 0.4, [("Browser (JavaScript, simplified)", 17, True, BLUE)])
    code(s, "Code: browser", 6.95, 2.05, 5.78, 3.3, 'const reader = response.body.getReader();\nwhile (true) {\n  const { value, done } = await reader.read();\n  if (done) break;\n  // split into events,\n  // then update the chat on screen\n}', size=14)
    arrow(s, "Server to browser", 6.6, 3.7, 6.95, 3.7, color=BLUE, width=2.5)
    example(s, 0.6, 5.6, 12.13, 1.25, "One side writes events one line at a time. The other side reads each line as soon as it arrives.", bsize=18)


def s42_graph_stream(d):
    s = d.slide("How LangGraph helps", SEC_I,
                "LangGraph can tell us two things while it runs. Updates: a step has finished. Messages: the words the model is writing right now. "
                "Our hand-written loop can stream the steps too, but its final answer arrives in one piece. The LangGraph version streams the words as well.", tag="BUILT")
    box(s, "Screen 1", 0.6, 1.55, 5.9, 3.4, [], fill=WHITE, border=BLUE, radius=0.04)
    box(s, "Screen 1 bar", 0.6, 1.55, 5.9, 0.55, [("updates: a step finished", 15, True, WHITE)], fill=BLUE, radius=0.04)
    for i, t in enumerate(("search_docs  done", "list_tables  done", "run_sql  3 rows")):
        box(s, f"Update {i}", 0.9, 2.35 + i * 0.75, 5.3, 0.55, [(t, 14, True, INK, MONO)], fill=PALE, radius=0.2, align=LEFT, margins=(0.2, 0, 0.1, 0))
    box(s, "Screen 2", 6.83, 1.55, 5.9, 3.4, [], fill=WHITE, border=NAVY, radius=0.04)
    box(s, "Screen 2 bar", 6.83, 1.55, 5.9, 0.55, [("messages: words being written", 15, True, WHITE)], fill=NAVY, radius=0.04)
    text(s, "Typing", 7.1, 2.35, 5.4, 2.4, [("The refund window for damaged items is 7 days of delivery, and the company pays the return shipping|", 17, False, INK)])
    code(s, "Code: stream modes", 0.6, 5.2, 7.2, 0.95, 'for mode, payload in graph.stream(inputs, config,\n        stream_mode=["updates", "messages"]):', size=14)
    example(s, 8.1, 5.2, 4.63, 1.65, "A kitchen with two screens: one for each dish as it is finished, one for the chef writing the menu card.", bsize=14)


def s43_demo(d):
    s = d.slide("Live demo script", SEC_I,
                "Open the tool steps panel so the audience sees the agent working. Wake the server five minutes before. Only the presenter uses it, because the free Gemini key allows about 15 requests a minute. "
                "Keep a screen recording ready as a backup.", tag="BUILT")
    steps = [("Documents only", "“What is the refund window for damaged items?”"), ("Database only", "“Top 3 customers by revenue, excluding cancelled orders.”"),
             ("Both", "“Which delivered orders were late, and what credit does the policy give per band?”"), ("Personas", "Ask the same question as Policy Advisor, Data Analyst and Support Agent."),
             ("Skills", "Ask the Data Analyst for total revenue and show the sql-analyst rule."),
             ("Plugin", "Build the zip, then run the slash command in the AI app.")]
    for i, (h, q) in enumerate(steps):
        y = 1.55 + i * 0.9
        num(s, 0.6, y + 0.1, i + 1, d=0.55, size=18)
        card(s, f"Step {i + 1}", 1.4, y, 7.0, 0.8, h, q, hsize=15, bsize=13, fill=LIGHT, anchor=MIDDLE, margins=(0.22, 0.05, 0.22, 0.05))
    card(s, "Presenter tips", 8.75, 1.55, 3.98, 5.1, "Presenter tips", ["Open the tool-steps panel.", "Wake the server 5 minutes early.", "Only the presenter uses the demo.", "Keep a screen recording ready.", "Never show a link that holds a token."], hsize=18, bsize=16, fill=AMBER_FILL, hcolor=AMBER_INK)


def s44_verified(d):
    s = d.slide("What we checked", SEC_I,
                "Trust, but check. We recalculated every number with direct SQL. Both agent versions gave the same answers, and our attempts to change the database were blocked.", tag="BUILT")
    res = [("Refund", "Report damage within 7 days. The company pays return shipping."), ("Top customers", "Zenith Associates, Xenon Group, Fairway Solutions."),
           ("Late deliveries", "50 of 287. The three bands had 20 (5%), 17 (10%) and 13 (15%)."), ("Safe and consistent", "Both agent versions agree. Attempts to change the database were blocked.")]
    for i, (h, b) in enumerate(res):
        x, y = 0.6 + (i % 2) * 6.15, 1.55 + (i // 2) * 2.7
        card(s, f"Result {h}", x, y, 5.98, 2.5, h, b, hsize=22, bsize=19, fill=GREEN_FILL, hcolor=GREEN, margins=(0.22, 0.14, 1.0, 0.12))
        box(s, f"Tick {h}", x + 5.2, y + 0.15, 0.6, 0.6, [("OK", 14, True, WHITE)], fill=GREEN, shape=MSO_SHAPE.OVAL, margins=(0, 0, 0, 0))


def s45_deploy(d):
    s = d.slide("From laptop to a public link", SEC_J,
                "Put the code on GitHub. Connect GitHub to Render. Set a build command and a start command. Add secrets as environment variables. Render gives you a public link.", tag="BUILT")
    flow(s, "Deploy", 0.6, 1.7, 12.13, 1.4, [("Your laptop", "write and test"), ("GitHub", "git push"), ("Render", "builds and runs it"), ("Public link", "https://your-app.onrender.com")],
         fills=[WHITE, WHITE, BLUE, WHITE], gap=0.7, tsize=17, dsize=13)
    text(s, "Cmd label", 0.6, 3.5, 6.0, 0.35, [("THE TWO COMMANDS RENDER NEEDS", 13, True, MUTED)])
    code(s, "Code: build", 0.6, 3.9, 12.13, 0.7, "Build:  pip install -r requirements.txt", size=16)
    code(s, "Code: start", 0.6, 4.75, 12.13, 0.7, "Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT", size=16)
    example(s, 0.6, 5.7, 12.13, 1.15, "Like posting a letter: you hand it over, and the post office delivers it to a public address.", bsize=17)


def s46_secrets(d):
    s = d.slide("Secrets and access", SEC_J,
                "Keep keys in environment variables, never in code. We protect /mcp with a token and the website with a password. Lock the front door, and give each visitor the right key. "
                "The free plan sleeps after 15 idle minutes and its disk is wiped. Our app rebuilds its search index at startup to handle this.", tag="BUILT")
    cards = [("Environment variables", "Keys live in Render's settings. They are never in the code or on GitHub."), ("A token for /mcp", "Other agents must send the token to use our data."),
             ("A password for the site", "People need the password to open the page and ask questions.")]
    for i, (h, b) in enumerate(cards):
        card(s, f"Secret {h}", 0.6 + i * 4.1, 1.55, 3.93, 2.9, h, b, hsize=20, bsize=17, fill=LIGHT)
    card(s, "Free plan reality", 0.6, 4.75, 12.13, 2.1, "The free plan, honestly", ["It sleeps after 15 idle minutes, so the first request can take a minute.", "Its disk is wiped when it restarts, so our app rebuilds its search index at startup."], hsize=19, bsize=17, fill=AMBER_FILL, hcolor=AMBER_INK)


def s47_update(d):
    s = d.slide("Updating and fixing problems", SEC_J,
                "Every push to the main branch deploys again by itself. If the new version fails its health check, the old one keeps running, so a mistake does not take the site down. "
                "Read the logs. Keep a switch to go back: we can set the agent back to the simple loop with one setting.", tag="BUILT")
    box(s, "Push", 0.6, 2.2, 1.9, 1.2, [("Push", 17, True, INK), ("to main", 13, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Build", 3.2, 2.2, 1.9, 1.2, [("Build", 17, True, INK), ("install, start", 13, False, MUTED)], fill=WHITE, border=BLUE)
    box(s, "Health check", 5.8, 1.85, 2.4, 1.9, [("Health check", 15, True, INK), ("OK?", 15, True, BLUE)], fill=PALE, border=BLUE, shape=MSO_SHAPE.DIAMOND)
    box(s, "New live", 9.0, 1.3 + 0.35, 3.7, 1.1, [("New version is live", 16, True, WHITE)], fill=GREEN)
    box(s, "Old runs", 9.0, 3.45, 3.7, 1.1, [("Old version keeps running", 16, True, AMBER_INK)], fill=AMBER_FILL, border=AMBER)
    arrow(s, "p to b", 2.5, 2.8, 3.2, 2.8)
    arrow(s, "b to h", 5.1, 2.8, 5.8, 2.8)
    arrow(s, "yes", 8.2, 2.5, 9.0, 2.2, color=GREEN, width=2.25)
    arrow(s, "no", 8.2, 3.1, 9.0, 3.9, color=AMBER, width=2.25)
    text(s, "Yes", 8.2, 1.95, 0.7, 0.3, [("yes", 13, True, GREEN)])
    text(s, "No", 8.3, 3.55, 0.7, 0.3, [("no", 13, True, AMBER_INK)])
    card(s, "Tips", 0.6, 4.95, 12.13, 1.9, "If something fails", ["Read the logs first. The error is usually in the last few lines.", "Keep a switch to go back. We can set the agent to the simple loop with one setting."], hsize=18, bsize=16, fill=LIGHT)


def s48_providers(d):
    s = d.slide("Where to get models", SEC_K,
                "These are ways to use models without owning hardware. Many providers copy the OpenAI-style API, so switching is often just a new link and a new key. "
                "Verify current free tiers, limits and model names before presenting, because they change often.", tag="CONCEPT")
    provs = [("Gemini API", "Google. A free tier that is good for learning."), ("Groq", "Very fast hosted open models."), ("OpenRouter", "One key for many models."),
             ("Hugging Face", "A model hub plus hosted use."), ("Together", "Hosted open models."), ("Mistral", "Its own models through an API.")]
    for i, (h, b) in enumerate(provs):
        x, y = 0.6 + (i % 3) * 4.1, 1.55 + (i // 3) * 1.7
        card(s, f"Provider {h}", x, y, 3.93, 1.5, h, b, hsize=19, bsize=15, fill=LIGHT)
    text(s, "Code label", 0.6, 5.05, 12.0, 0.35, [("MANY PROVIDERS ACCEPT THE SAME STYLE OF CALL", 13, True, MUTED)])
    code(s, "Code: openai style", 0.6, 5.45, 12.13, 1.4, 'from openai import OpenAI\nclient = OpenAI(base_url="https://<provider-endpoint>/v1", api_key="...")\nclient.chat.completions.create(model="<model>", messages=[...])', size=14)


def s49_free(d):
    s = d.slide("Free tiers and their catches", SEC_K,
                "Put model names in settings, not in code. Add retries and fallbacks. These are lessons we learned on our own project. Verify the details of any provider's free tier before presenting.", tag="BUILT")
    cards = [("Strict limits", "We hit 15 requests a minute on our Gemini key."), ("Models get retired", "Our first model name stopped working for new users."),
             ("Features can be missing", "The explicit prompt-cache feature gave an error on our key."), ("Treat keys like passwords", "Never put them in code, chats or slides.")]
    for i, (h, b) in enumerate(cards):
        x, y = 0.6 + (i % 2) * 6.15, 1.55 + (i // 2) * 2.7
        card(s, f"Catch {h}", x, y, 5.98, 2.5, h, b, hsize=22, bsize=19, fill=AMBER_FILL if i < 3 else RED_FILL, hcolor=AMBER_INK if i < 3 else RED)


def s50_selfhost(d):
    s = d.slide("Running open models yourself", SEC_K,
                "Run a model on your own computer or server. A small model of a few billion parameters, made smaller by compression called quantization, can run on a modern laptop. Bigger models need GPUs. "
                "Verify tool and model names, and hardware advice, before presenting. We did not run these ourselves.", tag="CONCEPT")
    flow(s, "Local", 0.6, 1.6, 12.13, 1.2, [("Your agent code", ""), ("Local server", "for example Ollama"), ("Model files", "on your own disk")], fills=[WHITE, BLUE, WHITE], gap=0.8, tsize=17, dsize=13)
    text(s, "Tools label", 0.6, 3.15, 5.8, 0.35, [("TOOLS", 13, True, MUTED)])
    for i, t in enumerate(("Ollama", "LM Studio", "llama.cpp", "vLLM")):
        pill(s, f"Tool {t}", 0.6 + i * 1.5, 3.55, 1.4, 0.45, t, size=14)
    text(s, "Models label", 6.85, 3.15, 5.8, 0.35, [("MODEL FAMILIES", 13, True, MUTED)])
    for i, t in enumerate(("Qwen", "Llama", "Gemma", "DeepSeek", "Mistral")):
        pill(s, f"Model {t}", 6.85 + i * 1.2, 3.55, 1.1, 0.45, t, size=13)
    code(s, "Code: local", 0.6, 4.35, 5.9, 1.2, "ollama run <model-name>\n# then call http://localhost:11434 from your app", size=14)
    example(s, 6.85, 4.35, 5.88, 1.2, "A student runs a small Qwen model offline on a laptop. No data leaves the machine.", bsize=15)
    card(s, "Rule of thumb", 0.6, 5.8, 12.13, 1.05, "Rule of thumb", "A small model (a few billion parameters), compressed, can run on a modern laptop. Bigger models need GPUs.", hsize=15, bsize=15, fill=AMBER_FILL, hcolor=AMBER_INK)


def s51_choose(d):
    s = d.slide("How to choose", SEC_K,
                "Ask four questions: privacy, cost, quality and effort. You can mix them: keep private data local and use the cloud for the hard thinking.", tag="CONCEPT")
    rows = [["You need", "Good choice"], ["To learn fast and cheaply", "A free-tier hosted API"], ["The best quality", "A frontier model API"],
            ["Data that must stay private", "An open model you run yourself"], ["Speed for many users", "Fast hosted inference"]]
    table(s, "Choice table", 0.6, 1.55, [5.5, 6.63], rows, size=18, row_h=0.75)
    card(s, "Mix", 0.6, 5.5, 12.13, 1.35, "You can mix them", "Keep private data local, and use the cloud for the hard thinking.", hsize=19, bsize=18, fill=PALE)


def s52_next(d):
    s = d.slide("What to build next", SEC_L,
                "These are project ideas for students. The staircase is a learning path: Python and APIs, then prompting, then RAG, then agents and tools, then MCP and deploying. Start with one and finish it.", tag=None)
    labels = ("Python + APIs", "Prompting", "RAG", "Agents + tools", "MCP + deploy")
    for i, lab in enumerate(labels):
        h = 0.9 + i * 0.75
        box(s, f"Step {i + 1}", 0.6 + i * 1.28, 6.85 - h, 1.22, h, [(str(i + 1), 18, True, WHITE)], fill=BLUE if i < 4 else NAVY, shape=MSO_SHAPE.RECTANGLE, anchor=TOP, margins=(0.05, 0.08, 0.05, 0.05))
        text(s, f"Step label {i + 1}", 0.6 + i * 1.28, 6.85 - h - 0.62, 1.22, 0.55, [(lab, 12, True, INK)], align=CENTER, anchor=2 if False else TOP)
    ideas = [("A study assistant", "RAG over your own notes."), ("A data assistant", "An agent with read-only SQL over a campus or sports dataset."),
             ("A data server", "An MCP server that shares any dataset with any AI tool."), ("Improve our demo", "Add an intent classifier, a reranker and a test set.")]
    for i, (h, b) in enumerate(ideas):
        card(s, f"Idea {h}", 7.3, 1.55 + i * 1.35, 5.43, 1.2, h, b, hsize=17, bsize=15, fill=LIGHT)


def s53_summary(d):
    s = d.prs.slides.add_slide(d.L_TITLE_ONLY)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY)
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.5), Inches(12.1), Inches(0.9)
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MIDDLE
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.alignment = LEFT
    r = p.add_run()
    r.text = "Summary"
    r.font.size, r.font.bold, r.font.name = Pt(40), True, FONT
    r.font.color.rgb = rgb(WHITE)
    blocks = [("LLM", "the language engine"), ("+ your data", "RAG"), ("+ tools", "agents and a harness"), ("connected with", "MCP"), ("packaged as", "personas, skills, plugins")]
    bw = (12.13 - 4 * 0.35) / 5
    for i, (a, b) in enumerate(blocks):
        x = 0.6 + i * (bw + 0.35)
        box(s, f"Block {i + 1}", x, 1.9, bw, 1.6, [(a, 16, True, WHITE), (b, 14, False, "CFE0F5")], fill=BLUE if i != 4 else "2F7FD1", radius=0.12, gap=4)
        if i < 4:
            arrow(s, f"Block arrow {i + 1}", x + bw, 2.7, x + bw + 0.35, 2.7, color="7FB2EA", width=2.25)
    box(s, "Deployed", 0.6, 3.85, 12.13, 0.7, [("deployed, so others can use it", 18, True, NAVY)], fill=WHITE, radius=0.3)
    text(s, "Key sentence", 0.6, 4.95, 12.13, 1.2, [("An agent is an LLM with a harness.", 28, True, WHITE), ("RAG is how it reads your data.", 28, True, "7FB2EA")], align=CENTER, gap=4)
    text(s, "Thanks", 0.6, 6.3, 12.13, 0.6, [("Thank you, VIT-AP. Questions?", 22, True, WHITE)], align=CENTER)
    s.notes_slide.notes_text_frame.text = ("One sentence to remember: an agent is an LLM with a harness, and RAG is how it reads your data. "
                                           "Share the project link and the word list. Open the Q&A.")


ORDER = [s37_wait, s38_how_stream, s43_demo, s44_verified,
         s45_deploy, s46_secrets, s47_update, s48_providers, s49_free, s50_selfhost, s51_choose, s52_next, s53_summary]
