"""Dedicated skills slides (inserted after 'Skills and connectors')."""
from lib import *  # noqa: F401,F403

SEC_E = "E. Personas, skills, connectors, plugins"


def skills_playbooks(d):
    s = d.slide("Skills: playbooks for the agent", SEC_E,
                "A skill is a short written playbook that tells the agent how and when to do a job. We have three, as plain text files. "
                "Business rules like revenue excludes cancelled orders live in a skill, not in code, so anyone can read and change them.", tag="BUILT")
    skills = [("docs-research", "Policy questions", "Search the PDFs, follow cross-references, cite every claim."),
              ("sql-analyst", "Numbers from the database", "Check the schema first. Revenue and late deliveries have fixed definitions."),
              ("docs-plus-data", "A rule applied to real data", "Rule first, facts second, then combine and show a table.")]
    for i, (n, use, how) in enumerate(skills):
        y = 1.55 + i * 1.6
        card(s, f"Skill {n}", 0.6, y, 6.3, 1.45, n, [f"Use when: {use}", how], hsize=18, bsize=15, fill=LIGHT)
    text(s, "Code title", 7.2, 1.55, 5.5, 0.35, [("INSIDE SKILLS/SQL-ANALYST/SKILL.MD", 12, True, MUTED)])
    code(s, "Code: skill", 7.2, 1.95, 5.53, 2.75, "---\nname: sql-analyst\ndescription: Use when the user asks for\n  numbers, counts or rankings.\n---\n1. Call list_tables, then describe_table.\n2. Revenue = SUM(quantity * unit_price\n   * (1 - discount_pct/100.0)).\n3. Exclude Cancelled orders.", size=13)
    example(s, 7.2, 4.95, 5.53, 1.9, "A recipe card in a kitchen. The cook (the model) already knows how to cook. The card says how this restaurant makes this dish.", bsize=16)


def skills_flow(d):
    s = d.slide("How a skill reaches the agent", SEC_E,
                "The skill files sit in a folder. The persona decides which skills the agent may follow. Their text is added to the system prompt, so the agent reads the playbook before it answers. "
                "The same SKILL.md files also work in the Claude plugin. Tools are the hands, skills are the instructions, personas are the roles.", tag="BUILT")
    flow(s, "Skill path", 0.6, 1.6, 12.13, 1.3, [("skills/ folder", "SKILL.md text files"), ("Persona", "picks which skills"), ("System prompt", "skill text is added"), ("Agent", "follows the playbook")],
         fills=[WHITE, WHITE, WHITE, BLUE], gap=0.6, tsize=17, dsize=13)
    rows = [["", "What it is", "Our example"],
            ["Tool", "The hands: it does something", "run_sql, search_docs"],
            ["Skill", "The playbook: how and when", "docs-plus-data"],
            ["Persona", "The role: which tools and skills are allowed", "Policy Advisor"]]
    table(s, "Tools skills personas", 0.6, 3.3, [1.8, 6.0, 4.33], rows, size=16, row_h=0.55)
    text(s, "Code title", 0.6, 5.6, 7.6, 0.3, [("HOW THE HARNESS ADDS SKILLS TO THE CALL", 12, True, MAROON)])
    code(s, "Code: skills in call", 0.6, 5.9, 7.6, 1.0,
         'skills = [s for s in load_skills() if s["name"] in persona["skills"]]\n'
         'sp = BASE_RULES + persona["instructions"] + "\\n".join(s["body"] for s in skills)', size=11)
    card(s, "Benefit", 8.5, 5.6, 4.23, 1.3, "Change a rule without code", "Edit one text file. Our agent and the Claude plugin both read it.", hsize=15, bsize=13, fill=GREEN_FILL, hcolor=GREEN)
