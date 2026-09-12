from typing import TypedDict, Optional, Literal, Dict, Any

class AgentState(TypedDict):
    raw_query: str
    user_origin: Optional[str]              # e.g., 'Telangana', 'Kerala'
    intent: Optional[Literal["SCOUT", "LINGO", "HYBRID"]]
    cache_status: Optional[Literal["HIT", "CACHE_MISS"]]
    scout_data: Optional[Dict[str, Any]]    # Matched lane node from Chroma
    lingo_data: Optional[Dict[str, Any]]    # Street scripts & tone notes
    harvested_data: Optional[Dict[str, Any]]# Freshly extracted node on miss
    final_payload: Optional[str]            # Final combined response
