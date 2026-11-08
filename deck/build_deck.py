"""Build the full webinar deck:  python deck/build_deck.py [--part1]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import Deck  # noqa: E402
import part1  # noqa: E402

OUT = Path(__file__).resolve().parent / "VIT-AP_AI_Webinar.pptx"
d = Deck()
order = [part1.s01_title, part1.s02_problem, part1.s03_map, part1.s04_learn, part1.s05_neural, part1.s06_transformers,
         part1.s07_llm, part1.s08_frontier, part1.s09_open, part1.s10_companies, part1.s11_limits,
         part1.s12_agent_vs_llm, part1.s13_harness, part1.s14_langchain, part1.s15_langgraph, part1.s16_vs, part1.s17_two_ways, part1.s18_when,
         part1.s19_personas, part1.s20_persona_results, part1.s21_skills, part1.s22_plugins]
try:
    import part2
    order += part2.ORDER
except ImportError:
    pass
try:
    import part3
    order += part3.ORDER
except ImportError:
    pass
for fn in order:
    fn(d)
d.prs.save(OUT)
print(f"saved {OUT}  ({len(d.prs.slides)} slides)")
