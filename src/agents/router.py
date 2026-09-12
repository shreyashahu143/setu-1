import os
import json
from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain_groq import ChatGroq
from src.schemas.state import AgentState
from dotenv import load_dotenv

load_dotenv()

class RouterDecision(BaseModel):
    intent: Literal["SCOUT", "LINGO", "HYBRID"]
    primary_topic: str = Field(description="Core object or topic, e.g., 'phone repair', 'auto fare negotiation'")
    user_origin_inferred: Optional[str] = Field(default="Unknown", description="Origin state if mentioned")

# Fast free-tier classifier on Groq
router_llm = ChatGroq(
    model_name="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)

ROUTER_PROMPT = """You are the intent classification router for an interstate relocation assistant in Nagpur, Maharashtra.
Analyze the user's input and classify it strictly into one of three intents:

1. SCOUT: Queries about market lanes, shops, where to buy, food spots, areas, prices, or repairs.
2. LINGO: Queries asking how to talk to locals, dialect phrases, auto driver negotiation words, or cultural customs.
3. HYBRID: Queries containing BOTH a destination/shopping intent AND a conversational/bargaining instruction.

Input: {query}

Respond strictly in JSON format matching this schema:
{{
  "intent": "SCOUT" | "LINGO" | "HYBRID",
  "primary_topic": "short topic name",
  "user_origin_inferred": "state name or Unknown"
}}
"""

def router_node(state: AgentState) -> dict:
    prompt = ROUTER_PROMPT.format(query=state["raw_query"])
    response = router_llm.invoke(prompt)
    
    try:
        # Clean potential markdown wrapping from LLM
        cleaned_content = response.content.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(cleaned_content)
        return {
            "intent": parsed.get("intent", "SCOUT"),
            "user_origin": state.get("user_origin") or parsed.get("user_origin_inferred", "Unknown")
        }
    except Exception:
        # Defensive fallback if JSON parsing fails
        return {"intent": "SCOUT"}
