"""Demo slides: personas, skills, and exporting the plugin."""
from lib import *  # noqa: F401,F403

SEC_I = "I. Our architecture and the live demo"


def demo_personas(d):
    s = d.slide("Demo: one question, three personas", SEC_I,
                "Pick the persona in the dropdown and ask the same question three times. Keep the tool-steps panel open: the audience can see which tools each persona is allowed to use. "
                "Policy Advisor gives the rule but cannot see orders. Data Analyst gives the numbers but cannot see the policy and says so. Support Agent has both and writes the reply. "
                "The server blocks the tools, not just the prompt. Wording will vary a little each time.", tag="BUILT")
    box(s, "Question", 0.6, 1.55, 12.13, 0.85,
        [("Ask each persona: “A Gold customer’s order was 4 days late. What do we owe them?”", 21, True, WHITE)], fill=NAVY, radius=0.12)
    personas = [("Policy Advisor", "Document tools only", "search_docs  list_documents  get_document_page",
                 ["Gives the late-delivery credit rule.", "Says it cannot see the order."]),
                ("Data Analyst", "SQL tools only", "list_tables  describe_table  run_sql",
                 ["Gives the order data.", "Says it cannot see the policy and suggests switching persona."]),
                ("Support Agent", "All 6 tools", "documents + SQL",
                 ["Finds the 10% credit in the policy.", "Writes a reply for the customer."])]
    for i, (n, sub, tools, sees) in enumerate(personas):
        x = 0.6 + i * 4.1
        box(s, f"Persona {n}", x, 2.7, 3.93, 0.85, [(n, 19, True, WHITE), (sub, 13, False, "DCE9F8")], fill=BLUE, radius=0.12)
        box(s, f"Tools {n}", x, 3.65, 3.93, 0.55, [(tools, 11, False, CODE_INK, MONO)], fill=CODE_BG, radius=0.2)
        card(s, f"Sees {n}", x, 4.3, 3.93, 1.55, "WHAT YOU SHOULD SEE", sees, hsize=11, bsize=14, fill=LIGHT)
    box(s, "Takeaway", 0.6, 6.1, 12.13, 0.75,
        [("Same question, same data, three different jobs. The role decides what the agent can do.", 17, True, NAVY)], fill=PALE, radius=0.15)


def demo_skills(d):
    s = d.slide("Demo: a skill changes the answer", SEC_I,
                "Ask the Data Analyst: what is our total revenue? Its sql-analyst skill says to leave out cancelled orders, so it returns 2,067,781.74. "
                "A plain sum with no such rule gives 2,112,172.34, which counts 6 cancelled orders and is 44,390.60 too high. Both numbers come from our own SQL on the demo database. "
                "Optional: edit the rule in the skill file, restart the server, ask again, and the agent follows the new rule.", tag="BUILT")
    steps = [("Open the skill", "skills/sql-analyst/SKILL.md says: Exclude Cancelled orders."),
             ("Pick Data Analyst", "Its persona file lists the sql-analyst skill."),
             ("Ask", "“What is our total revenue?”"),
             ("Check the SQL in the steps panel", "The query leaves out status = 'Cancelled'.")]
    for i, (h, b) in enumerate(steps):
        y = 1.55 + i * 1.15
        num(s, 0.6, y + 0.18, i + 1, d=0.6, size=19)
        card(s, f"Step {i + 1}", 1.4, y, 5.9, 1.0, h, b, hsize=16, bsize=14, fill=LIGHT, anchor=MIDDLE)
    box(s, "With skill", 7.7, 1.55, 5.03, 1.75, [("With the skill", 15, True, GREEN), ("$2,067,781.74", 34, True, GREEN),
                                                  ("cancelled orders left out", 13, False, INK)], fill=GREEN_FILL, border=GREEN, radius=0.1)
    box(s, "Without rule", 7.7, 3.5, 5.03, 1.75, [("A plain sum, no rule", 15, True, RED), ("$2,112,172.34", 34, True, RED),
                                                   ("counts 6 cancelled orders: $44,390.60 too high", 13, False, INK)], fill=RED_FILL, border=RED, radius=0.1)
    card(s, "Why", 7.7, 5.45, 5.03, 1.4, "Why it matters", "The business rule lives in one text file, not in code. Change the file and the agent follows it.",
         hsize=15, bsize=14, fill=PALE)
    text(s, "Source", 0.6, 6.3, 6.7, 0.5, [("Both numbers come from our own SQL on the demo database.", 12, False, MUTED)])


def demo_plugin(d):
    s = d.slide("Demo: export the agent as a plugin", SEC_I,
                "This turns our skills and commands into one package other people can install. Run the build script, and it makes a zip with the plugin file, the three skills, "
                "the four commands and a short readme. The safe zip has no link and no secret in it, so it can be shared. The connector is added separately in the AI app, "
                "and that link holds a token, so it never goes into a shared file. After the upload, type the slash command and the report appears.", tag="BUILT")
    flow(s, "Export flow", 0.6, 1.55, 12.13, 1.2,
         [("skills/ + commands/", "our text files"), ("build script", "one command"), ("plugin .zip", "safe to share"),
          ("Upload", "in the AI app"), ("Slash command", "runs the skill")],
         fills=[WHITE, WHITE, BLUE, WHITE, WHITE], gap=0.35, tsize=15, dsize=12)
    text(s, "Code title", 0.6, 3.05, 5.9, 0.3, [("1. BUILD IT", 12, True, MUTED)])
    code(s, "Code: build", 0.6, 3.4, 5.9, 0.85, "python scripts/build_plugin.py\n# writes dist/...-plugin.zip", size=14)
    card(s, "Zip contents", 0.6, 4.45, 5.9, 2.4, "Inside the zip", ["plugin.json: the name and version", "3 skills: docs-research, sql-analyst, docs-plus-data",
                                                               "4 commands: ask, policy, late-orders, customer", "a short readme"],
         hsize=16, bsize=14, fill=LIGHT)
    text(s, "Try title", 6.9, 3.05, 5.83, 0.3, [("2. TRY IT AFTER THE UPLOAD", 12, True, MUTED)])
    code(s, "Code: try", 6.9, 3.4, 5.83, 0.85, "/smartagent:late-orders\n# shortcut that follows the docs-plus-data skill", size=14)
    card(s, "You should see", 6.9, 4.45, 5.83, 1.35, "WHAT YOU SHOULD SEE", ["The credit rule with its citation, a table by lateness band,",
                                                                         "the total credit, and the 5 worst cases."], hsize=11, bsize=14, fill=PALE)
    box(s, "Secret warning", 6.9, 5.95, 5.83, 0.9, [("No token in the shared zip.", 15, True, AMBER_INK),
                                                    ("Add the connector link separately in the AI app.", 13, False, AMBER_INK)],
        fill=AMBER_FILL, border=AMBER, dash=True, radius=0.12)
