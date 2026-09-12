import os
import json
from langchain_groq import ChatGroq
from src.schemas.state import AgentState

from dotenv import load_dotenv

load_dotenv()

# Qwen 3.8 27B model for regional cultural & multilingual reasoning
lingo_llm = ChatGroq(
    model_name="qwen/qwen3.8-27b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

LINGO_PROMPT = """You are a local Nagpuri street dialect and cultural coach in Nagpur, Maharashtra.
You help interstate newcomers (from states like Telangana, Kerala, Tamil Nadu, Andhra Pradesh) navigate everyday conversations without sounding like vulnerable targets for overcharging.

User Query: "{query}"
User Origin / Native Background: "{user_origin}"

Provide local street advice in JSON format matching this schema:
{{
  "spoken_script": "The exact short sentence to say to the vendor/driver in Nagpuri street Hindi or local Varhadi Marathi blend",
  "phonetic_english": "How to pronounce it clearly in English letters",
  "literal_meaning": "Direct English translation of what they are saying",
  "tone_directive": "Tone advice: e.g., 'Say it casually and firmly without hesitation. Do not use overly polite formal words.'",
  "cultural_insight": "A 1-2 sentence tip explaining the local convention (e.g., auto meter habits, 'Hao' usage, bargaining norms)"
}}

Rules:
- Keep the spoken script short and realistic (1 to 2 sentences max).
- Emphasize local markers (e.g., Vidarbha usage of 'Hao' for agreement, 'Bhaiya theek rate lagao', 'Bardi jana hai').
- Avoid textbook Marathi; use the natural spoken dialect of Nagpur streets.
- Return ONLY valid JSON. No markdown code blocks, no intro or outro text.
"""

def lingo_node(state: AgentState) -> dict:
    query = state.get("raw_query", "")
    origin = state.get("user_origin") or "South India"
    
    prompt = LINGO_PROMPT.format(query=query, user_origin=origin)
    response = lingo_llm.invoke(prompt)
    
    try:
        cleaned_content = response.content.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(cleaned_content)
        return {
            "lingo_data": parsed
        }
    except Exception as e:
        # Graceful fallback payload
        return {
            "lingo_data": {
                "spoken_script": "Bhaiya, theek rate lagao, regular aate hain hum.",
                "phonetic_english": "Bhai-ya, theek rate la-gao, reg-u-lar aa-tay hain hum.",
                "literal_meaning": "Brother, charge a fair rate, we come here regularly.",
                "tone_directive": "Say it firmly and casually.",
                "cultural_insight": "Vendors charge a premium if they sense you are new. Showing familiarity with rates brings prices down."
            }
        }
