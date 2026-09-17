# Technical Design Specification

## 1. Shared State Schema (LangGraph)

The multi-agent graph passes a single typed state dictionary across all nodes:

```python
from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    raw_query: str
    user_origin: Optional[str]              # e.g., 'Telangana', 'Kerala'
    intent: Optional[str]                   # 'SCOUT' | 'LINGO' | 'HYBRID'
    cache_status: Optional[str]             # 'HIT' | 'CACHE_MISS'
    scout_data: Optional[Dict[str, Any]]    # Retrieved lane/goods metadata
    lingo_data: Optional[Dict[str, Any]]    # Phrases, phonetics, and tone tips
    harvested_data: Optional[Dict[str, Any]]# Auto-extracted node on cache miss
    final_payload: Optional[str]            # Formatted output for the UI
```

## 2. Knowledge Base Schemas (Pydantic)

### Street Insight Node

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class StreetInsightNode(BaseModel):
    area_name: str = Field(description="Broad area name, e.g., Sitabuldi, Chitaroli, Itwari")
    sub_lane_or_landmark: str = Field(description="Exact lane or landmark, e.g., Modi No. 2, Modi No. 3")
    specialty_goods_or_food: List[str] = Field(description="Items or services specifically traded here")
    price_band: str = Field(description="Expected price range, e.g., Budget (₹1,200 - ₹1,800 for screen repairs)")
    bargaining_tactics: str = Field(description="Unwritten rules, counter-offer percentages, or timing tips")
    accessibility_notes: str = Field(description="Two-wheeler only, crowded after 6 PM, parking limitations")
    category: str = Field(description="Shopping, Tech Repair, Food, Culture, or General")

    # --- Verification / trust gate fields (closes the "unreviewed auto-write" gap) ---
    verification_status: Literal["seed", "verified", "unverified"] = Field(
        default="unverified",
        description="'seed' = hand-curated at project start. 'verified' = corroborated by 2+ independent "
                    "sources or manually approved. 'unverified' = single-source harvester output, not yet trusted."
    )
    source_urls: List[str] = Field(
        default_factory=list,
        description="URLs the harvester pulled this from. Empty for seed data."
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Harvester's self-reported extraction confidence, 0-1. Below 0.5 nodes are discarded, not stored."
    )
    harvested_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of harvest, for staleness checks. Null for seed data."
    )
```

**Verification gate rules (must be enforced in code, not just documented):**
1. Harvester-extracted nodes are written with `verification_status="unverified"` and `confidence_score` from the extraction step. Nodes with `confidence_score < 0.5` are **not** written to ChromaDB at all — discard and fall back to a graceful "I couldn't confirm this reliably" response.
2. Scout Agent, when retrieving, **must** return `is_unverified: true` in `scout_data` whenever the best match has `verification_status == "unverified"`, so Synthesis can disclose it to the user. Unverified data is never presented as confirmed fact.
3. Promotion to `verified` happens when either (a) a second independent harvest run corroborates the same core fact (area + price band within a reasonable range), or (b) the developer manually reviews and flips the flag during the Phase 4 audit step (see phases.md).
4. Seed data (`data/seed_nagpur.json`) is always `verification_status="seed"` and treated as equivalent to `verified` for retrieval purposes.

### Dialect Node

```python
class DialectNode(BaseModel):
    target_phrase_marathi_hindi: str = Field(description="Spoken street phrase in local dialect")
    phonetic_english: str = Field(description="Phonetic pronunciation guide for non-native speakers")
    literal_translation: str = Field(description="Direct English translation")
    situational_context: str = Field(description="When and where to use this phrase (e.g., auto negotiation)")
    tone_directive: str = Field(description="Assertive, casual, deferential, or firm")
```

## 3. Seed Knowledge Dataset (Sample Baseline)

The initial database (`data/seed_nagpur.json`) seeds the following high-priority entities, all marked `verification_status="seed"`:

- **Sitabuldi Modi No. 2:** Women's ethnic wear, sarees, dress material, high bargaining.
- **Sitabuldi Modi No. 3:** Mobile handset repairs, spare displays, wholesale accessories.
- **Chitaroli:** Clay idols (*murtis*), artisan workshops, late-night hot masala milk stalls.
- **Itwari (Kirana & Mirchi Bazaar):** Bulk wholesale spices, dry fruits, unstitched wedding cloth.
- **Dharampeth:** Elite residential quarter, boutique cafes, jewelry showrooms.
- **Vidarbha Dialect Nuances:** Use of "Hao" for agreement, negotiation script "Bhaiya theek rate lagao, regular aate hain", and Marbat festival protocols.

## 4. Agent Interface Contracts

Pin these exact function signatures so agents built in isolation (different sessions/days) stay compatible.

```python
# agents/router.py
def route_query(state: AgentState) -> AgentState:
    """Reads raw_query, user_origin. Sets intent."""

# agents/scout.py
def scout_lookup(state: AgentState) -> AgentState:
    """Reads raw_query, intent. Sets scout_data, cache_status."""

# agents/lingo.py
def generate_lingo(state: AgentState) -> AgentState:
    """Reads raw_query, user_origin. Sets lingo_data."""

# agents/harvester.py
def harvest_and_index(state: AgentState) -> AgentState:
    """Reads raw_query, scout_data (for context). Sets harvested_data.
    Writes new StreetInsightNode to ChromaDB with verification_status='unverified'
    if confidence_score >= 0.5, else discards and leaves harvested_data as a
    graceful-degradation message."""

# agents/synthesis.py
def synthesize_response(state: AgentState) -> AgentState:
    """Reads scout_data, harvested_data, lingo_data. Sets final_payload.
    MUST check is_unverified flags and disclose accordingly."""
```

## 5. Evaluation Set (required before Phase 4 sign-off)

Maintain `eval/test_queries.json` with at least 15-20 fixed queries covering:
- 5 exact-match queries (should hit seed data, similarity ≥ 0.65)
- 5 near-miss queries (paraphrased, should still hit via embedding similarity)
- 5 guaranteed cache-miss queries (obscure/fictional lanes, should trigger harvester)
- 3-5 dialect-only queries (LINGO intent)

Each entry: `{query, expected_intent, expected_area_or_null, notes}`. Run this set before and after Phase 3 harvester work to produce a measurable "cache hit rate" and "harvester success rate" metric for the README — this is your actual evidence the system works, not just screenshots.
