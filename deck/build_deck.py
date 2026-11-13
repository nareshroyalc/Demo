"""Build the full webinar deck:  python deck/build_deck.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import Deck  # noqa: E402
import part1 as p1  # noqa: E402
import part2 as p2  # noqa: E402
import part3 as p3  # noqa: E402
import part_intro as pi  # noqa: E402
import part_skills as ps  # noqa: E402

OUT = Path(__file__).resolve().parent / "VIT-AP_AI_Webinar.pptx"
dv = pi.divider
order = [
    pi.intro, pi.agenda,
    dv(1), p1.s03_map, p1.s04_learn, p1.s05_neural, p1.s06_transformers,
    dv(2), p1.s07_llm, p1.s08_frontier, p1.s09_open, p1.s10_companies, p1.s11_limits,
    dv(3), p1.s12_agent_vs_llm, p1.s13_harness, pi.tools_what, pi.tools_call,
    p1.s14_langchain, p1.s15_langgraph, p1.s16_vs, p1.s17_two_ways, p1.s18_when,
    dv(4), p1.s19_personas, p1.s20_persona_results, p1.s21_skills, ps.skills_playbooks, ps.skills_flow, p1.s22_plugins,
    dv(5), p2.s23_rag, p2.s24_extract, p2.s25_chunk, p2.s26_embed, p2.s27_store, p2.s28_retrieve,
    dv(6), p2.s29_hybrid, p1.s01_title, p1.s02_problem, p2.s30_agentic, p2.s31_test,
    dv(7), p2.s32_mcp, p2.s33_ourmcp, p2.s34_share, p2.s35_safe,
    dv(8), p2.s36_arch, p3.s37_wait, p3.s38_how_stream, p3.s43_demo, p3.s44_verified,
    dv(9), p3.s45_deploy, p3.s46_secrets, p3.s47_update,
    dv(10), p3.s48_providers, p3.s49_free, p3.s50_selfhost, p3.s51_choose,
    p3.s52_next, p3.s53_summary,
]
d = Deck()
for fn in order:
    fn(d)
d.prs.save(OUT)
print(f"saved {OUT}  ({len(d.prs.slides)} slides)")
