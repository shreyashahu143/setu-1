# src/graph.py

from langgraph.graph import StateGraph, END
from src.schemas.state import AgentState
from src.agents.router import router_node
from src.agents.scout import scout_node
from src.agents.lingo import lingo_node
from src.agents.harvestor import harvester_node
from src.agents.synthesis import synthesis_node

def route_intent(state: AgentState) -> list[str]:
    intent = state.get("intent", "SCOUT")
    if intent == "SCOUT":
        return ["scout"]
    elif intent == "LINGO":
        return ["lingo"]
    elif intent == "HYBRID":
        return ["scout", "lingo"]
    return ["scout"]

def check_cache_status(state: AgentState) -> str:
    status = state.get("cache_status")
    # --- ADD THIS DEBUG PRINT ---
    print(f"🔀 [GRAPH EDGE] Cache Status: {status} -> Routing to {'HARVESTER' if status == 'CACHE_MISS' else 'SYNTHESIS'}")
    # ----------------------------
    if status == "CACHE_MISS":
        return "harvester"
    return "synthesis"

workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("scout", scout_node)
workflow.add_node("harvester", harvester_node)
workflow.add_node("lingo", lingo_node)
workflow.add_node("synthesis", synthesis_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_intent, {"scout": "scout", "lingo": "lingo"})
workflow.add_conditional_edges("scout", check_cache_status, {"harvester": "harvester", "synthesis": "synthesis"})
workflow.add_edge("harvester", "synthesis")
workflow.add_edge("lingo", "synthesis")
workflow.add_edge("synthesis", END)

app = workflow.compile()
