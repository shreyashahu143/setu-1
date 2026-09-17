# Project Rules (for Claude Code / Antigravity)

These rules are binding for any code generated in this repo. If a request conflicts with these rules, flag the conflict instead of silently picking one side.

## 1. Environment & Tooling
- **Python version:** 3.11+
- **Package manager:** `uv` (fallback to `pip` with a `requirements.txt` if `uv` is unavailable — do not mix both in the same repo)
- **Virtual environment:** always create and activate one; never install packages globally
- **Secrets:** all API keys (Groq, Google AI Studio) go in a `.env` file loaded via `python-dotenv`. Never hardcode a key in source. Never print a key to logs or terminal output, even for debugging.

## 2. Project Structure (do not deviate without updating this file)

```
setu/
├── agents/
│   ├── router.py
│   ├── scout.py
│   ├── lingo.py
│   ├── harvester.py
│   └── synthesis.py
├── tools/
│   └── search_tools.py
├── data/
│   └── seed_nagpur.json
├── eval/
│   └── test_queries.json
├── schemas.py
├── graph.py          # LangGraph StateGraph assembly lives here, not in app.py
├── app.py            # Streamlit entry point only — no business logic here
├── memory.md
├── rules.md
├── prd.md / architecture.md / design.md / phases.md
├── .env.example
└── README.md
```

## 3. Code Conventions
- Every agent function takes `AgentState` in and returns `AgentState` out (see design.md §4 for exact signatures). No agent function should have side effects on global state outside ChromaDB writes.
- Use type hints everywhere. No bare `dict` or `Any` where a Pydantic model or TypedDict field exists.
- LLM calls: always set `temperature=0` for router/classification calls. Synthesis and lingo generation can use `temperature=0.3-0.5` for more natural phrasing — state the value explicitly in the function, don't leave it as a library default.
- Structured LLM outputs (router intent, harvester extraction) must be parsed via Pydantic `model_validate_json` or equivalent — never regex-parse an LLM's JSON-ish output.
- Logging: use Python's `logging` module, not `print()`, for anything beyond a quick throwaway script. Log at minimum: cache hits/misses, harvester triggers, harvester discard events (confidence < 0.5), and promotion events.

## 4. The Verification Gate Is Non-Negotiable
This is the single most important rule in this file. Per design.md §2:
- Harvester nodes are written as `verification_status="unverified"`, never as `"verified"`.
- Nodes with `confidence_score < 0.5` are **discarded**, not stored.
- Any response built on unverified data must disclose that fact to the user in plain language.
- If you (the coding agent) are asked to implement a shortcut that skips this gate "to save time" or "for the MVP," push back and point to this rule before proceeding — this gate is the difference between the reliability requirement in prd.md being true or false.

## 5. Testing
- Every agent gets at least one test in a corresponding `tests/test_<agent>.py` using fixed, hand-written inputs — not live API calls in the test suite (mock the LLM/search calls).
- `eval/test_queries.json` (design.md §5) is run manually, not as part of unit tests, since it requires live LLM/DB calls. Track results as dated entries in `memory.md`, not just console output.

## 6. Commit Discipline
- One logical change per commit (one agent, one bugfix, one schema change). No "misc fixes" commits.
- Commit message format: `[phase-N] short description` (e.g., `[phase-2] implement scout agent with similarity fallback`).

## 7. What NOT to do
- Do not add new external API dependencies beyond Groq, Google AI Studio, DuckDuckGo Search, and ChromaDB without updating prd.md's cost-efficiency NFR first.
- Do not expand scope to cities beyond Nagpur or to out-of-scope items listed in prd.md §3 without an explicit instruction to update the PRD first.
- Do not remove or weaken the verification gate (§4 above) even if it's the fastest path to a working demo.
