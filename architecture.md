# System Architecture

## 1. Architectural Pattern

Setu employs a **Hierarchical Orchestrator-Worker Architecture** with a closed-loop **Self-Learning Knowledge Harvester**, implemented via **LangGraph**.

### Plain-language flow (read this first, diagram is a reference)

1. User submits a query via the Streamlit UI.
2. The **Supervisor Router** classifies it as `SCOUT`, `LINGO`, or `HYBRID`.
3. If `SCOUT` or `HYBRID`: the **Local Scout Agent** queries ChromaDB.
   - If top match similarity ≥ 0.65 → treated as a cache hit, node returned as-is.
   - If top match similarity < 0.65 → `cache_status = "CACHE_MISS"`, control passes to the **Live Harvester Agent**.
4. The Harvester searches external sources, extracts a candidate `StreetInsightNode`, and writes it with `verification_status = "unverified"` (see design.md §2 for the verification gate — unverified nodes are never presented to the user as fact without a disclaimer, and are never used to answer future queries until promoted).
5. If `LINGO` or `HYBRID`: the **Street Lingo Agent** runs in parallel, generating phrase/phonetic/tone guidance.
6. The **Synthesis Node** merges whatever combination of scout/harvested/lingo data exists into one structured response card.
7. Response returned to the Streamlit client.

### Diagram (for reference)

```
┌───────────────────────────────┐
│ User Interface (Streamlit)    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Supervisor Router             │
│ (Llama-3.1-8b via Groq)       │
└───────┬───────────────┬───────┘
        │               │
┌───────┘               └───────┐
▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│ Local Scout Agent         │   │ Street Lingo Agent         │
│ (Gemini-1.5/2.0-Flash)    │   │ (Llama-3.3-70b via Groq)   │
└─────────────┬─────────────┘   └─────────────┬─────────────┘
              │                               │
              ▼                               │
      [ ChromaDB Vector RAG ]                  │
              │                               │
   ┌──────────┴──────────┐                    │
   ▼ (score ≥ 0.65)       ▼ (score < 0.65)     │
[ Cached Node ]   ┌───────────────────────────┐│
      │           │ Live Harvester Agent      ││
      │           │ (DuckDuckGo + Gemini)     ││
      │           └─────────────┬─────────────┘│
      │                         ▼               │
      │           [ Auto-Append to ChromaDB     │
      │             as UNVERIFIED node ]        │
      │                         │               │
      └────────────┬────────────┘               │
                   ▼                            ▼
   ┌───────────────────────────────────────────────────────┐
   │ Synthesis & Output Node (Gemini-1.5/2.0-Flash)         │
   └─────────────────────────┬───────────────────────────────┘
                             ▼
                    [ Streamlit Client ]
```

## 2. Agent Specifications

### Supervisor Router Agent
- **Engine:** `llama-3.1-8b-instant` (Groq Cloud)
- **Responsibility:** Classifies queries into `SCOUT`, `LINGO`, or `HYBRID` intents and parses user entity constraints (e.g., origin state, area name if mentioned).
- **Execution:** Zero-shot classification, deterministic JSON output only (`temperature=0`).
- **Input:** `raw_query: str`, `user_origin: Optional[str]`
- **Output:** `intent: str`, updates `AgentState`

### Local Scout Agent
- **Engine:** `gemini-1.5-flash` / `gemini-2.0-flash` (Google AI Studio)
- **Responsibility:** Executes similarity queries against ChromaDB to identify lanes, landmarks, price ranges, and market rules.
- **Fallback Trigger:** If maximum cosine similarity < 0.65, sets `cache_status = "CACHE_MISS"`.
- **Verification Rule:** Only returns nodes where `verification_status == "verified"` as primary answers. Unverified nodes may be returned but MUST be flagged in `scout_data` with `is_unverified: true` so Synthesis can disclose this to the user.
- **Input:** `raw_query: str`, `intent: str`
- **Output:** `scout_data: Optional[Dict]`, `cache_status: str`

### Street Lingo & Culture Agent
- **Engine:** `llama-3.3-70b-versatile` (Groq Cloud)
- **Responsibility:** Translates outsider intents into natural Nagpuri Varhadi / street Hindi phrases, with phonetic guides and tone guidance.
- **Input:** `raw_query: str`, `user_origin: Optional[str]`
- **Output:** `lingo_data: Optional[Dict]`

### Live Harvester Agent
- **Engine:** `gemini-1.5-flash` (Google AI Studio) + `duckduckgo-search`
- **Responsibility:** Runs targeted queries against regional forums and public discussion sources, parses entities via Pydantic (`StreetInsightNode`), and writes new nodes to ChromaDB with `verification_status = "unverified"` and a `source_urls` field populated.
- **Promotion Rule:** A node is only promoted from `unverified` to `verified` when at least 2 independent source URLs agree on the core fact (area, price band), OR a human manually approves it via the audit step in phases.md Phase 4. Unverified nodes are never silently treated as ground truth.
- **Input:** `raw_query: str`, `scout_data` (for context on what was missing)
- **Output:** `harvested_data: Optional[Dict]`

### Synthesis Node
- **Engine:** `gemini-1.5-flash` (Google AI Studio)
- **Responsibility:** Merges spatial guidance (scout/harvester) with conversational scripts (lingo) into one formatted response. Must explicitly disclose when the underlying data is `unverified` (e.g., "This is based on a recent online mention and hasn't been double-checked — treat pricing as approximate.").
- **Input:** `scout_data`, `harvested_data`, `lingo_data`
- **Output:** `final_payload: str`
