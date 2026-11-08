# Pitch Deck Content: Brightline RAG Agent

**Topic:** From normal RAG to agentic RAG, delivered as an MCP server, skills and a plugin.
**Length:** 30 slides. Each slide has on-slide text (keep it short), speaker notes (say it aloud), and a visual suggestion.
**Design hint:** clean white background, one accent blue (`#0066cc`, same as the demo UI), Geist or Inter font, one idea per slide.

All numbers below come from the demo we built and tested. Items we did not test are marked **(not yet tested)**.

---

## Part 1: The problem and the idea (slides 1-4)

### Slide 1: Title
**On slide**
- Ask your documents and your database in one question
- Normal RAG vs agentic RAG, shipped as an MCP server, skills and a plugin
- Brightline RAG Agent: a working demo

**Speaker notes**
This is a working system, not a mock-up. We built it, deployed it, and connected it to Claude.

**Visual:** logo, title, one-line subtitle.

---

### Slide 2: The problem
**On slide**
- Company knowledge lives in two places: documents (PDFs, policies) and databases
- People ask questions that need both
- Today: search the PDF, then ask an analyst for a query, then combine by hand

**Speaker notes**
Example: "Which late deliveries get compensation, and how much?" The rule is in a PDF. The facts are in a database. No single tool answers it.

**Visual:** two silos (document stack, database) with a person copying between them.

---

### Slide 3: What we built, in one slide
**On slide**
- A retrieval layer over 5 policy PDFs and a sales database
- Two doors: `/agent` (answers questions) and `/mcp` (lets any AI agent use the data)
- Skills: playbooks that teach the AI how to combine them
- A plugin and a web UI on top
- Live on Render, free tier

**Speaker notes**
Everything that follows explains one of these five parts.

**Visual:** the five parts as five icons in a row.

---

### Slide 4: The demo company
**On slide**
- Brightline Supplies: a fictional B2B office-supplies seller
- 5 policy PDFs: returns, shipping SLA, pricing, support, warranty
- SQLite database, 6 tables: customers (40), products (30), orders (300), order items (757), shipments (293), support tickets (53)
- Policy numbers in the PDFs match the data, so combined questions have real answers

**Speaker notes**
We generated the data ourselves so the demo is safe to show. The same design works on real documents and databases.

**Visual:** small table-and-PDF thumbnail graphic.

---

## Part 2: Normal RAG vs agentic RAG (slides 5-8)

### Slide 5: Normal RAG, how it works
**On slide**
1. Split documents into chunks
2. Turn chunks into vectors (embeddings)
3. Question comes in, find the closest chunks
4. Give chunks to the LLM, it writes an answer

**Speaker notes**
One pass: retrieve once, generate once. It is simple, cheap and fast. It works well when the answer sits in one or two passages.

**Visual:** straight left-to-right flow: Question, Retrieve, Generate, Answer.

---

### Slide 6: Where normal RAG breaks
**On slide**
- Needs numbers from a database: "Top 5 customers by revenue"
- Needs two sources: "Which orders qualify for the late-delivery credit?"
- Needs several searches: the answer spans three policies that reference each other
- No second chance: if the first retrieval is wrong, the answer is wrong

**Speaker notes**
These are normal business questions, and a single retrieve-then-generate step cannot do them.

**Visual:** three question cards with a red "cannot answer" mark.

---

### Slide 7: Agentic RAG, how it works
**On slide**
- The LLM runs a loop: think, call a tool, read the result, decide the next step
- Tools: search documents, read a page, list tables, describe a table, run SQL
- It stops when it has enough evidence, then answers with citations
- It can fix its own mistakes (for example a failed SQL query)

**Speaker notes**
Our agent runs up to 8 steps. On the late-delivery question it searched the policy first, then inspected the table, then ran one SQL query.

**Visual:** circular loop diagram with the tools around it.

---

### Slide 8: Normal vs agentic, side by side
**On slide**

| | Normal RAG | Agentic RAG |
|---|---|---|
| Retrieval | One pass | Multiple, chosen by the model |
| Sources | Usually documents | Documents, databases, APIs |
| Numbers and aggregates | Weak | Exact, through SQL |
| Self-correction | None | Retries on errors |
| Cost and latency | Lowest | Higher (several model calls) |
| Best for | Simple lookups | Multi-step business questions |

**Speaker notes**
Agentic RAG is not always better. Use normal RAG for simple lookups and the agent when the question needs reasoning across sources.

**Visual:** the table, with the agentic column highlighted.

---

## Part 3: How we built it (slides 9-17)

### Slide 9: Architecture
**On slide**
```
PDFs -> chunk -> embed -> Qdrant ----+
                                     +--> shared retrieval layer --> /mcp   (tools only)
SQLite database -> read-only SQL ----+                          \--> /agent (retrieval + Gemini answer)
```
- One retrieval layer, two doors

**Speaker notes**
Both doors call the same functions. Improve retrieval once and both improve.

**Visual:** the diagram above, drawn cleanly.

---

### Slide 10: Ingestion and chunking
**On slide**
- PDF text read page by page
- Chunks of about 900 characters with 150 characters of overlap, split on paragraphs
- 5 PDFs became 21 chunks
- Each chunk keeps its title, file name and page for citations

**Speaker notes**
Overlap keeps a sentence from being cut in half. Keeping the page number is what makes citations possible.

**Visual:** a page splitting into highlighted chunks.

---

### Slide 11: Hybrid retrieval
**On slide**
- Vector search finds meaning ("money back" matches "refund")
- Keyword search (BM25) finds exact terms ("Platinum", "POL-RET-001")
- Results merged with reciprocal-rank fusion
- Gemini embeddings, 768 dimensions

**Speaker notes**
Policies contain both natural language and exact terms, so using both gives better results than either alone.

**Visual:** two ranked lists merging into one.

---

### Slide 12: The vector store, Qdrant
**On slide**
- Qdrant in embedded mode: files on disk, no separate server
- Each vector stores document, title, page and text
- On free hosting the disk resets, so the app rebuilds the index at startup (a few seconds for 21 chunks)
- Scale path: one config change to Qdrant Cloud

**Speaker notes**
For this size, simple wins. We chose a design that is easy to move to a managed Qdrant when the data grows.

**Visual:** folder icon turning into a cloud icon.

---

### Slide 13: Structured data, safely
**On slide**
- The agent can query the database, but only read-only
- One SELECT per call, writes rejected, 200-row cap, 5-second timeout
- Database opened in read-only mode
- Tested: DROP, DELETE, UPDATE and PRAGMA attempts are all blocked

**Speaker notes**
We do not trust the model to be careful. The tool itself enforces the limits.

**Visual:** padlock over a database.

---

### Slide 14: Tools, what the agent can do
**On slide**
- `search_docs`: hybrid search with citations
- `list_documents`, `get_document_page`: browse and read more context
- `list_tables`, `describe_table`: see the schema first
- `run_sql`: read-only queries
- Clear tool descriptions are the contract: they tell the model when to use each tool

**Speaker notes**
Six tools. Writing good tool descriptions is half the work, because the model decides what to call by reading them.

**Visual:** six tool cards.

---

### Slide 15: Skills, playbooks for the model
**On slide**
- `docs-research`: how to search, cross-check and cite policies
- `sql-analyst`: inspect the schema first, how revenue is defined, how late is defined
- `docs-plus-data`: rule first, facts second, then combine
- Plain `SKILL.md` text files, easy to read, review and version

**Speaker notes**
Tools are the hands, skills are the instructions. Business rules like "revenue excludes cancelled orders" live in a skill, not in code.

**Visual:** three playbook cards.

---

### Slide 16: Tools plus skills beats one giant prompt
**On slide**
- Tools do things; skills say how and when
- Change a business rule by editing a text file, with no code change
- Same skill files are used by our own agent and by Claude
- Smaller, focused instructions are easier to test than one long prompt

**Speaker notes**
This is the maintainability story. Business people can read and review a skill file.

**Visual:** before and after: one long prompt vs three short skills.

---

### Slide 17: The generation agent
**On slide**
- `/agent` runs the loop with Gemini (`gemini-3.1-flash-lite`)
- Loads the skills into its instructions
- Returns the answer, the tool steps taken, and the sources
- Rate-limited per user to protect cost

**Speaker notes**
The UI shows the tool steps so users can see how the answer was reached. That builds trust.

**Visual:** screenshot of a chat answer with the steps panel open.

---

## Part 4: MCP, plugin and connection (slides 18-25)

### Slide 18: MCP in one slide
**On slide**
- MCP (Model Context Protocol) is an open standard for connecting AI agents to tools and data
- Think of it as USB-C for AI: build the connector once, any agent can plug in
- Our server publishes 6 tools at one URL

**Speaker notes**
Without MCP, every agent needs custom code for every data source. With it, you build once.

**Visual:** one server in the middle with many agent logos plugged in.

---

### Slide 19: Two doors, one retrieval layer
**On slide**

| | `/mcp` | `/agent` |
|---|---|---|
| Returns | Passages and rows only | A finished answer |
| LLM on our server | None | Gemini |
| Who writes the answer | The caller (Claude, etc.) | Our agent |
| Best for | Other agents and tools | Our UI and scripts |

**Speaker notes**
We expose only retrieval over MCP. The calling agent reasons for itself, which avoids two models talking to each other and keeps our server cost near zero.

**Visual:** the two doors diagram.

---

### Slide 20: Plugin, packaging for Claude
**On slide**
- A plugin bundles skills, slash commands and the connector
- Commands: `/brightline:ask`, `:policy`, `:late-orders`, `:customer`
- Two builds: a shareable one with no secrets, and a personal one with the connector bundled
- Built by a script from the same skill files

**Speaker notes**
The plugin is a distribution wrapper. The product is the MCP server. We kept the shareable zip free of secrets on purpose.

**Visual:** zip icon with four command chips.

---

### Slide 21: Connect from anywhere
**On slide**
- Claude on the web or desktop: add as a custom connector
- Claude Code: one command to add the server
- Other MCP-capable agents: add the same URL
- Everyone gets the same tools and the same data rules

**Speaker notes**
We tested the connection with a real MCP client and against the live URL. Uploading the plugin in the Claude app itself is **(not yet tested)**.

**Visual:** one URL fanning out to four clients.

---

### Slide 22: Live demo script
**On slide**
1. Docs only: "What is the refund window for damaged items, and who pays return shipping?"
2. Data only: "Top 3 customers by revenue, excluding cancelled orders."
3. Both: "Which delivered orders were late, and what credit does policy give per lateness band?"

**Speaker notes**
Run these three in order. Open the steps panel on the third to show the agent searching the policy, inspecting the table, then running SQL.

**Visual:** three question cards.

---

### Slide 23: Results we verified
**On slide**
- Refund question: 7 days to report damage; Brightline pays return shipping
- Top customers: Zenith Associates ($103,728.50), Xenon Group ($101,192.80), Fairway Solutions ($100,995.00)
- Late deliveries: 50 of 287 delivered shipments; bands 20 (1-2 days, 5%), 17 (3-5 days, 10%), 13 (6+ days, 15%)
- Every number matched a direct SQL check

**Speaker notes**
We did not trust the model's arithmetic. We re-ran the queries independently and the numbers matched.

**Visual:** three result cards with green "verified" ticks.

---

### Slide 24: The user interface
**On slide**
- React app, SmartHub-style look, no build step
- Chat with source citations and a tool-steps panel
- Documents page: test retrieval, open PDFs, re-index
- Data page: browse tables. Skills page. MCP page with connection steps

**Speaker notes**
The UI exists so non-technical users can try it and so we can inspect retrieval quality.

**Visual:** annotated screenshot.

---

### Slide 25: Safety and guardrails
**On slide**
- Database: read-only, single statement, row and time limits
- `/mcp` needs a secret token; the UI and `/agent` need a password
- Per-user rate limit on `/agent`
- Answers cite sources; skills say "if it is not in the sources, say so"
- Retrieved text is treated as untrusted data

**Speaker notes**
Safety is layered: the tools enforce limits, access is controlled, and the instructions push honesty. Nothing relies on the model behaving.

**Visual:** layered shield diagram.

---

## Part 5: Running it (slides 26-28)

### Slide 26: Deployment
**On slide**
- Hosted on Render's free tier from a GitHub repository
- Every push to `main` redeploys automatically
- Secrets (Gemini key, token, password) live in Render settings, not in code
- Index rebuilds itself at startup

**Speaker notes**
Zero hosting cost for the demo. The free tier sleeps after 15 idle minutes, so the first request can take a minute.

**Visual:** GitHub to Render flow.

---

### Slide 27: Maintaining it
**On slide**
- Data freshness: re-index documents on a schedule; the database is queried live
- Treat tool names and descriptions as a versioned contract
- Keep a test set of 30-50 real questions and re-run it after every change
- Log tool calls, failures and empty searches; review weekly
- Skills in git: reviewed like code

**Speaker notes**
Most RAG failures after launch come from stale data and untested changes, not from the model.

**Visual:** maintenance checklist.

---

### Slide 28: Lessons and honest limits
**On slide**
- Free tier: cold starts, limited memory, rate limits
- A model we planned to use was retired, so make the model name a setting
- A library major version changed its API, so pin versions
- The hosted server rejected a non-local hostname until configured
- Token-in-URL is a demo shortcut; production needs OAuth
- Demo data is small and synthetic

**Speaker notes**
Being upfront builds credibility. Each of these was a real issue we hit and fixed.

**Visual:** short "what went wrong, what we did" list.

---

## Part 6: Where this goes (slides 29-30)

### Slide 29: Roadmap
**On slide**
- Real sources: Google Drive and company databases (our original goal)
- Serve skills and commands from the MCP server itself, so any agent gets them
- OAuth sign-in and per-user permissions
- Reranking, table-aware chunking, evaluation dashboard
- Managed Qdrant and paid hosting without cold starts
- Plugin marketplace for one-command team installs

**Speaker notes**
Order by value: real data first, then access control, then quality tooling.

**Visual:** three-step roadmap: Now, Next, Later.

---

### Slide 30: Summary and next step
**On slide**
- Normal RAG answers lookups; agentic RAG answers business questions
- Tools act, skills guide, MCP connects, the plugin packages
- Built, deployed and verified, at no hosting cost
- Next step: point it at one real data source and one real team

**Speaker notes**
End with a concrete ask: pick the first real use case and a pilot group.

**Visual:** the five-part icon row from slide 3, all checked.

---

## Appendix (not slides)

**Suggested demo flow (8 minutes):** slide 22 questions in the live UI, then show the connector in Claude, then run `/brightline:late-orders`.

**If asked about cost:** hosting is free; costs are Gemini API usage (embeddings once per index, generation per `/agent` question). `/mcp` use costs us nothing because the caller's model writes the answer.

**If asked "why not just a bigger prompt?":** the data does not fit in a prompt, changes constantly, and needs exact calculation, which SQL does and the model should not.
