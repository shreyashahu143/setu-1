# src/agents/scout.py

import logging
from src.schemas.state import AgentState
from src.tools.db_tools import query_street_nodes

# Safe threshold: anything <= 0.65 is a valid semantic hit
SIMILARITY_THRESHOLD = 0.55

def scout_node(state: AgentState) -> dict:
    query = state.get("raw_query", "")
    best_match, distance = query_street_nodes(query, top_k=1)
    
    print(f"[DEBUG scout_node] Query: '{query}' | Distance: {distance} | Threshold: {SIMILARITY_THRESHOLD}")
    
    if best_match and distance <= SIMILARITY_THRESHOLD:
        meta = best_match["metadata"]
        scout_payload = {
            "area_name": meta.get("area_name"),
            "sub_lane": meta.get("sub_lane"),
            "category": meta.get("category"),
            "price_band": meta.get("price_band"),
            "bargaining_tactics": meta.get("bargaining_tactics"),
            "status": meta.get("status", "verified"),
            "matched_text": best_match["document"],
            "confidence_distance": round(distance, 4)
        }
        return {
            "cache_status": "HIT",
            "scout_data": scout_payload
        }
    else:
        return {
            "cache_status": "CACHE_MISS",
            "scout_data": None
        }
