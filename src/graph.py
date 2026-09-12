from langgraph.graph import StateGraph, END
from src.schemas.state import AgentState
from src.agents.router import router_node
from src.agents.scout import scout_node
from src.agents.lingo import lingo_node
from src.agents.synthesis import synthesis_node

def route_intent(state: AgentState) -> list[str]:
    intent = state.get("intent", "SCOUT")
    if intent == "SCOUT":
        return ["scout"]
    elif intent == "LINGO":
        return ["lingo"]
    elif intent == "HYBRID":
        # Run both scout and lingo
        return ["scout", "lingo"]
    return ["scout"]

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Register Nodes
workflow.add_node("router", router_node)
workflow.add_node("scout", scout_node)
workflow.add_node("lingo", lingo_node)
workflow.add_node("synthesis", synthesis_node)

# 3. Define Flow
workflow.set_entry_point("router")

# Router branches out based on intent
workflow.add_conditional_edges(
    "router",
    route_intent,
    {
        "scout": "scout",
        "lingo": "lingo"
    }
)

# Workers feed into Synthesis
workflow.add_edge("scout", "synthesis")
workflow.add_edge("lingo", "synthesis")
workflow.add_edge("synthesis", END)

# 4. Compile Application
app = workflow.compile()
