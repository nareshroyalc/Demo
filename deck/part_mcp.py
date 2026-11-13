"""Part 7 concept slides: protocol, why a protocol, what MCP is, client and server, why we used it."""
from lib import *  # noqa: F401,F403

SEC_H = "H. MCP"


def protocol_what(d):
    s = d.slide("What is a protocol?", SEC_H,
                "Before MCP, one simple idea: a protocol. It is a set of rules that both sides agree on, so they can talk without any special setup. "
                "Traffic signals: red means stop in every city. Phone calls: any phone can call any other phone. HTTP: any browser can open any website. "
                "Without a protocol, every pair has to make its own private deal. With one, everyone follows the same rules once.", tag="CONCEPT")
    text(s, "Definition", 0.6, 1.55, 12.13, 0.9,
         [("A protocol is a set of rules both sides agree on,", 26, True, NAVY), ("so they can talk without any special setup.", 26, True, BLUE)])
    ex = [("Traffic signals", "Red means stop in every city. Any driver can drive anywhere."),
          ("Phone calls", "Any phone can call any other phone, whatever the brand."),
          ("The web (HTTP)", "Any browser can open any website.")]
    for i, (h, b) in enumerate(ex):
        card(s, f"Example {h}", 0.6 + i * 4.1, 2.75, 3.93, 1.55, h, b, hsize=18, bsize=15, fill=LIGHT)
    box(s, "Without", 0.6, 4.75, 5.9, 1.6, [("Without a protocol", 18, True, RED),
                                             ("Every pair makes its own private deal.", 17, False, INK),
                                             ("More pairs, more deals, more things to fix.", 17, False, INK)],
        fill=RED_FILL, radius=0.08, align=LEFT, margins=(0.25, 0.15, 0.25, 0.1), anchor=TOP)
    box(s, "With", 6.83, 4.75, 5.9, 1.6, [("With a protocol", 18, True, GREEN),
                                           ("Everyone follows the same rules once.", 17, False, INK),
                                           ("Anything new that follows the rules just works.", 17, False, INK)],
        fill=GREEN_FILL, radius=0.08, align=LEFT, margins=(0.25, 0.15, 0.25, 0.1), anchor=TOP)


def mcp_why(d):
    s = d.slide("Why AI applications need a protocol", SEC_H,
                "Employee A uses Application A. Employee B uses Application B. Both want the AI to create a GitHub issue. Without a standard, each application "
                "builds its own GitHub connector, with its own tool name, its own inputs and its own login. When GitHub changes, every connector breaks separately. "
                "With 5 applications and 10 tools like GitHub, Jira and Slack, that is 50 connectors to build and keep working.", tag="CONCEPT")
    rows = [("Employee A", "Application A", "gh_create_issue(repository, text)"),
            ("Employee B", "Application B", "newIssue(repo_name, title, desc)"),
            ("Employee C", "Application C", "github.issues.create(r, t, b)")]
    for i, (emp, app, conn) in enumerate(rows):
        y = 1.55 + i * 1.0
        box(s, f"Emp {emp}", 0.6, y, 1.9, 0.75, [(emp, 15, True, INK)], fill=GREYFILL, border=GREYLINE, radius=0.2)
        arrow(s, f"ea{i}", 2.5, y + 0.37, 2.9, y + 0.37)
        box(s, f"App {app}", 2.9, y, 2.2, 0.75, [(app, 15, True, WHITE)], fill=BLUE, radius=0.15)
        arrow(s, f"ac{i}", 5.1, y + 0.37, 5.5, y + 0.37)
        box(s, f"Conn {i}", 5.5, y, 4.6, 0.75, [(conn, 13, True, AMBER_INK, MONO)], fill=AMBER_FILL, border=AMBER, dash=True, radius=0.15)
        arrow(s, f"cg{i}", 10.1, y + 0.37, 10.75, 2.67)
    box(s, "GitHub", 10.75, 2.0, 1.98, 1.35, [("GitHub", 18, True, WHITE)], fill=NAVY, radius=0.15)
    text(s, "Conn label", 5.5, 4.55, 4.6, 0.35, [("3 different connectors for the same job", 13, True, AMBER_INK)], align=CENTER)
    card(s, "Problems", 0.6, 5.05, 7.6, 1.8, "The problem", ["Different names, different inputs, different logins.",
                                                       "GitHub changes something: fix every connector, one by one."],
         hsize=17, bsize=15, fill=RED_FILL, hcolor=RED)
    box(s, "Maths", 8.5, 5.05, 4.23, 1.8, [("5 apps × 10 tools", 18, True, INK), ("= 50 connectors", 30, True, RED)],
        fill=WHITE, border=RED, radius=0.08)


def mcp_what(d):
    s = d.slide("What is MCP?", SEC_H,
                "MCP, the Model Context Protocol, is an open protocol for connecting AI applications to tools and data. GitHub builds one MCP server with one tool, "
                "create_issue. Applications A, B and C all connect to that same server, so all three employees use the same tool. 5 applications plus 10 servers "
                "is 15 pieces instead of 50. Note: MCP does not force names. The names match because there is only one server. Like USB-C: one plug for every device.", tag="BUILT")
    for i, c in enumerate(("Application A", "Application B", "Application C")):
        box(s, f"App {c}", 0.6, 1.6 + i * 1.25, 2.4, 0.9, [(c, 15, True, WHITE)], fill=BLUE, radius=0.15)
        arrow(s, f"a{i}", 3.0, 2.05 + i * 1.25, 4.1, 3.1, color=BLUE, head=False)
    box(s, "MCP hub", 4.1, 2.45, 2.4, 1.3, [("MCP", 26, True, WHITE), ("one standard plug", 13, False, "DCE9F8")], fill=NAVY, radius=0.15)
    servers = [("GitHub server", "create_issue(repo, title, body)"), ("Jira server", "create_ticket(...)"), ("Our server", "search_docs, run_sql, ...")]
    for i, (n, t) in enumerate(servers):
        y = 1.6 + i * 1.25
        arrow(s, f"s{i}", 6.5, 3.1, 7.4, y + 0.45, color=BLUE, head=False)
        box(s, f"Server {n}", 7.4, y, 3.4, 0.9, [(n, 15, True, INK), (t, 11, False, MUTED, MONO)], fill=WHITE, border=BLUE, radius=0.15)
    stat(s, "Stat old", 11.2, 1.6, 1.55, "50", "without MCP", color=RED, big_size=32)
    stat(s, "Stat new", 11.2, 3.0, 1.55, "15", "with MCP", color=GREEN, big_size=32)
    box(s, "Note", 0.6, 5.5, 6.3, 1.35, [("Same tool for every employee", 16, True, BLUE),
                                         ("MCP does not rename tools. Names match because there is only one server.", 14, False, INK)],
        fill=PALE, radius=0.08, align=LEFT, margins=(0.25, 0.12, 0.25, 0.1), anchor=TOP)
    example(s, 7.2, 5.5, 5.53, 1.35, "USB-C. One plug shape, and any device works with any charger.", bsize=16)


def mcp_client_server(d):
    s = d.slide("MCP client and server", SEC_H,
                "Three roles. The host is the AI application the person uses. The client is the part inside it that speaks MCP. The server owns the tools and the data, "
                "like our /mcp. One call: the client connects, asks tools/list to see what tools exist, the model picks one, the client sends tools/call, "
                "the server runs it and returns the result. Applications do not hard-code tool names. They discover them, like reading a menu.", tag="BUILT")
    flow(s, "MCP flow", 0.6, 1.55, 12.13, 1.2,
         [("1. Connect", "client to server"), ("2. tools/list", "what tools do you have?"), ("3. Model picks", "one tool + inputs"),
          ("4. tools/call", "server runs it"), ("5. Answer", "model writes it")],
         fills=[WHITE, WHITE, WHITE, WHITE, BLUE], gap=0.35, tsize=16, dsize=12)
    rows = [["Role", "What it is", "Example"],
            ["Host", "The AI application the person uses", "Application A"],
            ["Client", "The part inside it that speaks MCP", "built into Application A"],
            ["Server", "Owns the tools and the data", "GitHub server, our /mcp"]]
    table(s, "Roles", 0.6, 3.05, [1.4, 3.9, 2.4], rows, size=14, row_h=0.5)
    text(s, "Code title", 0.6, 5.2, 7.7, 0.3, [("WHAT TOOLS/LIST SENDS BACK (SHORT)", 12, True, MUTED)])
    code(s, "Code: list", 0.6, 5.5, 7.7, 1.38, '{"name": "search_docs",\n "description": "Search the company policy PDFs",\n "inputSchema": {"query": "string", "k": "integer"}}', size=12)
    example(s, 8.6, 3.05, 4.13, 2.0, "A restaurant menu. You do not need to know the kitchen. You read the menu (tools/list) and order from it (tools/call).", bsize=15)
    card(s, "Key point", 8.6, 5.25, 4.13, 1.63, "Discovered, not hard-coded", "Add a tool to the server and every application sees it.",
         hsize=15, bsize=14, fill=GREEN_FILL, hcolor=GREEN)


def mcp_why_us(d):
    s = d.slide("Why we used MCP in our project", SEC_H,
                "We wrote our search and SQL tools once. Because they are an MCP server, any AI application that speaks MCP can use them with no extra code from us. "
                "We tested the same /mcp link in two different AI applications and changed nothing. A partner company could plug it into their own application tomorrow.", tag="BUILT")
    box(s, "Our tools", 0.6, 2.3, 2.8, 1.6, [("Our 6 tools", 17, True, WHITE), ("written once", 13, False, "DCE9F8")], fill=NAVY, radius=0.15)
    arrow(s, "t-m", 3.4, 3.1, 4.1, 3.1)
    box(s, "MCP door", 4.1, 2.55, 1.9, 1.1, [("/mcp", 20, True, INK, MONO)], fill=WHITE, border=BLUE, border_w=2.25, radius=0.2)
    for i, a in enumerate(("Application A", "Application B", "A partner's app")):
        y = 1.6 + i * 1.15
        arrow(s, f"m{i}", 6.0, 3.1, 6.8, y + 0.42, color=BLUE)
        box(s, f"App {a}", 6.8, y, 2.3, 0.85, [(a, 14, True, WHITE)], fill=BLUE, radius=0.15)
    cards = [("Build once", "Search and SQL written one time."), ("Works anywhere", "Any MCP application can use it."),
             ("No code per user", "New users connect; we build nothing.")]
    for i, (h, b) in enumerate(cards):
        card(s, f"Benefit {h}", 9.5, 1.6 + i * 1.15, 3.23, 1.0, h, b, hsize=15, bsize=12, fill=GREEN_FILL, hcolor=GREEN,
             margins=(0.18, 0.08, 0.18, 0.06))
    example(s, 0.6, 5.25, 12.13, 1.6, "We connected the same /mcp link to two different AI applications. Both found our 6 tools by themselves and answered "
                                      "from our PDFs and database. We changed no code.", label="From our project", bsize=17)
