"""Tests for the TTL prompt cache.

A. cache logic with a fake Gemini client (create / reuse / refresh before TTL / prompt change / failure back-off / off)
B. the exact request each engine sends WITH a cache (cached_content, no system prompt, no tools) and the fallback
C. (--live) the real fallback on this key: answers still work and the cache is not retried on every request

The success path against the real Gemini cache API can only run on a key that has explicit-cache access.
Run:  python scripts/test_prompt_cache.py [--live]
"""
import sys
import time
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from langchain_core.messages import AIMessage, SystemMessage  # noqa: E402

from app import agent, agent_graph, config, embeddings, personas, prompt_cache  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        fails.append(name)


def reset():
    prompt_cache._entries.clear()
    prompt_cache._state.update(disabled_until=0.0, last_error=None, attempts=0, created=0, hits=0)


# ------------------------------------------------------------------------------------------ A
print("A) cache logic (fake client)")


class FakeCaches:
    def __init__(self, fail=False):
        self.created, self.deleted, self.fail, self.n = [], [], fail, 0

    def create(self, model, config):
        if self.fail:
            raise RuntimeError("404 Not Found")
        self.n += 1
        self.created.append(config.ttl)
        return SimpleNamespace(name=f"cachedContents/c{self.n}")

    def delete(self, name):
        self.deleted.append(name)


fake = FakeCaches()
orig_client, orig_avail = embeddings.client, embeddings.available
embeddings.client = lambda: SimpleNamespace(caches=fake)
embeddings.available = lambda: True
config.PROMPT_CACHE, config.PROMPT_CACHE_TTL_SECONDS = "auto", 3600

gen, sup = personas.get_persona("generalist"), personas.get_persona("support-agent")
sp, tool = agent.system_prompt(gen), agent._decl(gen["tools"])
reset()
n1 = prompt_cache.get(gen, sp, tool)
n2 = prompt_cache.get(gen, sp, tool)
check("first call creates a cache with the TTL", n1 == "cachedContents/c1" and fake.created == ["3600s"])
check("second call reuses it (no second create)", n2 == n1 and len(fake.created) == 1)

prompt_cache._entries["generalist"]["expires"] = time.time() + 10  # inside the refresh margin
n3 = prompt_cache.get(gen, sp, tool)
check("refreshes before the TTL ends and deletes the old cache", n3 == "cachedContents/c2" and fake.deleted == [n1])

n4 = prompt_cache.get(gen, sp + " (a skill was edited)", tool)
check("a changed prompt gets a fresh cache (never stale)", n4 == "cachedContents/c3")

n5 = prompt_cache.get(sup, agent.system_prompt(sup), agent._decl(sup["tools"]))
check("each persona has its own cache", n5 == "cachedContents/c4" and set(prompt_cache.status()["active"]) == {"generalist", "support-agent"})

fake_bad = FakeCaches(fail=True)
embeddings.client = lambda: SimpleNamespace(caches=fake_bad)
reset()
check("API refusal -> None (agent falls back to the full prompt)", prompt_cache.get(gen, sp, tool) is None)
a = prompt_cache.status()["create_attempts"]
prompt_cache.get(gen, sp, tool)
prompt_cache.get(gen, sp, tool)
check("after a refusal it backs off (no retry on every request)", prompt_cache.status()["create_attempts"] == a == 1)
check("the reason is reported in status", "404" in (prompt_cache.status()["last_error"] or ""))

config.PROMPT_CACHE = "off"
embeddings.client = lambda: SimpleNamespace(caches=fake)
before = len(fake.created)
reset()
check("PROMPT_CACHE=off never calls the API", prompt_cache.get(gen, sp, tool) is None and len(fake.created) == before)
config.PROMPT_CACHE = "auto"

# ------------------------------------------------------------------------------------------ B
print("\nB) request shape per engine (stubbed model)")
reset()


class FakeModels:
    def __init__(self, fail_when_cached=False):
        self.configs, self.fail_when_cached = [], fail_when_cached

    def generate_content(self, model, contents, config):
        self.configs.append(config)
        if self.fail_when_cached and config.cached_content:
            raise RuntimeError("cache expired")
        return SimpleNamespace(
            function_calls=[], text="ok",
            usage_metadata=SimpleNamespace(prompt_token_count=100, cached_content_token_count=90),
        )


orig_get = prompt_cache.get
prompt_cache.get = lambda persona, sp_, tool_: "cachedContents/x"

fm = FakeModels()
embeddings.client = lambda: SimpleNamespace(models=fm)
r = agent.run_agent("hi", persona="generalist")
c = fm.configs[0]
check("plain: sends cached_content", c.cached_content == "cachedContents/x")
check("plain: does NOT also send system prompt or tools", c.system_instruction is None and not c.tools)
check("plain: usage reports the cached tokens", r["usage"] == {"calls": 1, "prompt_tokens": 100, "cached_tokens": 90, "prompt_cache": True})

fm = FakeModels(fail_when_cached=True)
embeddings.client = lambda: SimpleNamespace(models=fm)
r = agent.run_agent("hi", persona="generalist")
check("plain: if the cached call fails, retries with the full prompt",
      len(fm.configs) == 2 and fm.configs[1].system_instruction and fm.configs[1].tools and r["answer"] == "ok" and r["usage"]["prompt_cache"] is False)


class Stub:
    instances = []
    fail_cached = False

    def __init__(self, **kw):
        self.kw, self.tools, self.calls = kw, None, []
        Stub.instances.append(self)

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, msgs):
        self.calls.append(msgs)
        if self.kw.get("cached_content") and Stub.fail_cached:
            raise RuntimeError("cache expired")
        return AIMessage(content="ok", usage_metadata={"input_tokens": 100, "output_tokens": 5, "total_tokens": 105,
                                                       "input_token_details": {"cache_read": 90}})


orig_cls = agent_graph.ChatGoogleGenerativeAI
agent_graph.ChatGoogleGenerativeAI = Stub
agent_graph._graphs.clear()
agent_graph._cached_llms.clear()
r = agent_graph.run_agent("hi", persona="generalist")
cached = [i for i in Stub.instances if i.kw.get("cached_content") == "cachedContents/x"]
plain_llm = [i for i in Stub.instances if i.tools is not None][0]
check("langgraph: calls a model pointed at the cache", len(cached) == 1 and len(cached[0].calls) == 1)
check("langgraph: cached request has no system message", not any(isinstance(m, SystemMessage) for m in cached[0].calls[0]))
check("langgraph: the tool-bound model is not used when cached", len(plain_llm.calls) == 0)
check("langgraph: usage reports cached tokens and cache use", r["usage"] == {"calls": 1, "prompt_tokens": 100, "cached_tokens": 90, "prompt_cache": True})

Stub.fail_cached = True
Stub.instances.clear()
agent_graph._graphs.clear()
agent_graph._cached_llms.clear()
r = agent_graph.run_agent("hi", persona="generalist")
plain_llm = [i for i in Stub.instances if i.tools is not None][0]
check("langgraph: if the cached call fails, falls back to the full prompt",
      len(plain_llm.calls) == 1 and isinstance(plain_llm.calls[0][0], SystemMessage) and r["answer"] == "ok")

agent_graph.ChatGoogleGenerativeAI = orig_cls
agent_graph._graphs.clear()
prompt_cache.get = orig_get
embeddings.client, embeddings.available = orig_client, orig_avail
reset()

# ------------------------------------------------------------------------------------------ C
if "--live" in sys.argv:
    print("\nC) live fallback on this key (real Gemini)")
    for name, fn in (("plain", lambda: agent.run_agent("What is the refund window for damaged items?")),
                     ("langgraph", lambda: agent_graph.run_agent("What is the restocking fee for Gold customers?"))):
        r = fn()
        check(f"{name}: answers correctly with the cache enabled-but-unavailable", ("7 days" in r["answer"]) or ("10%" in r["answer"]), f"usage={r['usage']}")
        time.sleep(20)
    s = prompt_cache.status()
    print("      status:", s)
    check("refused once, then backed off (not retried per request)", s["create_attempts"] == 1 and s["created"] == 0)

print("\nRESULT:", "all checks passed" if not fails else f"FAILED: {fails}")
sys.exit(1 if fails else 0)
