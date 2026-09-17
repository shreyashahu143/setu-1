# Execution Roadmap & Solo Developer Workflow

## 1. Project Phase Breakdown

```
[ Phase 1: Foundation ] ──► [ Phase 2: Core Graph ] ──► [ Phase 3: Auto-Harvester ] ──► [ Phase 4: Field Validation ]
   (Days 1 to 3)              (Days 4 to 8)                (Days 9 to 14)                  (Days 15 to 20)
```

Each day below has an explicit **Done when** criterion. Do not move to the next day until it's met — this is what keeps a coding agent (or you) from declaring victory prematurely.

### Phase 1: Knowledge Schema & Seed Foundation (Days 1–3)

- **Day 1:** Set up repo, virtual environment, and Pydantic schemas in `schemas.py` (including `verification_status`, `source_urls`, `confidence_score` fields per design.md §2).
  - **Done when:** `schemas.py` imports cleanly, `StreetInsightNode(...)` and `DialectNode(...)` instantiate without validation errors in a throwaway script.
- **Day 2:** Populate `data/seed_nagpur.json` with 15 curated gold-standard entries, all `verification_status="seed"`.
  - **Done when:** JSON validates against `StreetInsightNode` schema for all 15 entries (write a one-off validation script, don't eyeball it).
- **Day 3:** Initialize local persistent ChromaDB and verify vector retrieval with test queries.
  - **Done when:** 5 manual test queries against known seed entries return the correct node as the top match.

### Phase 2: Core Multi-Agent Graph (Days 4–8)

- **Day 4:** Implement `agents/router.py` with Groq `llama-3.1-8b-instant`.
  - **Done when:** 10 hand-written test queries (mix of SCOUT/LINGO/HYBRID intent) classify correctly, output is valid JSON every time (temperature=0).
- **Day 5:** Implement `agents/scout.py` connecting ChromaDB with similarity scoring, including the `is_unverified` flag logic.
  - **Done when:** Scout correctly distinguishes cache hit vs. miss on 5 known-good and 5 known-bad queries.
- **Day 6:** Implement `agents/lingo.py` with Groq `llama-3.3-70b-versatile`.
  - **Done when:** Output includes all 5 `DialectNode` fields, phonetic guide is legible to a non-Hindi speaker (sanity check this yourself).
- **Day 7:** Implement `agents/synthesis.py` and assemble the graph using LangGraph `StateGraph`. Confirm synthesis discloses unverified data per design.md §4.
  - **Done when:** Full graph runs end-to-end on a single hardcoded cache-hit query and produces a coherent `final_payload`.
- **Day 8:** Run terminal benchmark tests using `eval/test_queries.json` (see design.md §5) — at minimum the 5 exact-match + 5 near-miss subset (harvester not built yet).
  - **Done when:** ≥8/10 of those queries return the expected intent and expected area. Log failures in `memory.md`, don't silently skip them.

### Phase 3: Live Harvester & Self-Learning Loop (Days 9–14)

- **Day 9:** Implement `tools/search_tools.py` using `duckduckgo-search` targeted at regional forums.
  - **Done when:** 3 manual searches for known Nagpur-area topics return at least one usable result each.
- **Day 10:** Build `agents/harvester.py` with structured Pydantic extraction on `gemini-1.5-flash`, enforcing the `confidence_score < 0.5 → discard` rule.
  - **Done when:** Extraction produces valid `StreetInsightNode` objects with `verification_status="unverified"` and populated `source_urls` on 3 test cache-miss queries.
- **Day 11:** Wire automatic ChromaDB insertion upon successful node extraction (confidence ≥ 0.5 only).
  - **Done when:** A harvested node is retrievable in a follow-up query, correctly flagged `is_unverified=true`.
- **Day 12:** Connect the conditional edge in LangGraph: `scout_agent` triggers `harvester_agent` on `CACHE_MISS`.
  - **Done when:** A single end-to-end query with no seed match correctly flows through harvester → synthesis → disclosed-as-unverified response.
- **Days 13–14:** Stress-test cache-miss scenarios using the 5 guaranteed-miss queries in `eval/test_queries.json`; verify database growth and check for garbage/malformed nodes.
  - **Done when:** All 5 either produce a reasonable unverified node or gracefully degrade ("couldn't find reliable info") — never a hallucinated confident answer.

### Phase 4: Interface & Field Validation (Days 15–20)

- **Days 15–16:** Build a minimal Streamlit UI (`app.py`) with origin-state customization.
  - **Done when:** A friend unfamiliar with the code can run `streamlit run app.py` and submit a query without your help.
- **Days 17–18:** Run user testing sessions with 3–5 interstate friends from Telangana, Kerala, or Tamil Nadu.
  - **Done when:** Each tester completes at least 3 queries; note every case where the answer was wrong, confusing, or the disclosure of "unverified" wasn't clear.
- **Days 19–20:** Audit database logs, manually promote corroborated `unverified` nodes to `verified` per design.md §2, clean noisy/garbage nodes, re-run the full `eval/test_queries.json` set for a final before/after metric, and document results in `README.md`.
  - **Done when:** README includes a concrete before/after number (e.g., cache hit rate, harvester success rate) — not just "it works."

## 2. Solo Developer Daily Cadence

- **Morning Log Audit (30 mins):** Review failed queries and inspect ChromaDB for malformed auto-harvested nodes. Log anything notable in `memory.md`.
- **Focused Implementation (60–90 mins):** Code and test exactly one graph node or tool at a time.
- **Evening Validation (15 mins):** Execute the 3 fixed sanity queries (exact match, dialect guidance, zero-shot harvest) to ensure zero regressions. Update `memory.md` with what changed and what's still open.
