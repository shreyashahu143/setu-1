# src/agents/harvester.py

import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.schemas.state import AgentState
from src.schemas.node import StreetInsightNode
from src.tools.search_tools import search_community_discussions
from src.tools.db_tools import get_chroma_collection

load_dotenv()
logger = logging.getLogger(__name__)

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Primary: The cutting-edge reasoning model
primary_llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=api_key,
    temperature=0.1
)

# Resilient Fallback: Highly available, ultra-stable production model
backup_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.1
)

HARVESTER_SYSTEM_PROMPT = """You are an expert local knowledge extraction agent for Nagpur, Maharashtra.
Analyze the following deep webpage scrapes and extract ground-truth commercial street insights.

Rules:
1. Target: Identify the specific market area, traditional sub-lane, or prominent landmark where these shops are clustered (e.g., 'Itwari Wholesale Market', 'Kamptee Road', 'Cotton Market', 'Ghat Road', 'Sitabuldi').
2. If multiple local brick-and-mortar storefront addresses point to the same neighborhood or lane, classify that area as the primary geographic hub.
3. If the scraped text reveals a specific market street name, extract it into sub_lane_or_landmark.
4. Set the confidence_score based on whether you found clear physical addresses in Nagpur. If you found at least one concrete Nagpur business market area, score it >= 0.80.

Return ONLY valid JSON matching this schema:
{
  "area_name": "Broad locality, e.g., Sitabuldi, Itwari, Sadar, Dharampeth, Mahal, Gandhibagh, Cotton Market, Kamptee",
  "sub_lane_or_landmark": "Specific lane or landmark, e.g., Near Netaji Market, Sarafa Bazaar, Kirana Oli, Ghat Road Junction",
  "specialty_goods_or_food": ["item1", "item2"],
  "price_band": "Estimated street price tier (e.g., Wholesale Budget, Mid-range)",
  "bargaining_tactics": "Bargaining tips or specific local shopping advice",
  "accessibility_notes": "Two-wheeler friendly, heavy traffic notes, or parking availability",
  "category": "Shopping",
  "status": "unverified",
  "mention_frequency": 1,
  "upvote_weight": 1,
  "confidence_score": 0.85
}
"""

def log_to_quarantine(node_data: Dict[str, Any], raw_query: str):
    buffer_path = "data/staging_buffer.json"
    os.makedirs(os.path.dirname(buffer_path), exist_ok=True)
    
    entries = []
    if os.path.exists(buffer_path):
        try:
            with open(buffer_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []
            
    node_data["query_context"] = raw_query
    node_data["status"] = "quarantine"
    entries.append(node_data)
    
    with open(buffer_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    logger.info(f"Node logged to quarantine: {node_data.get('area_name', 'Unknown')}")

def extract_text_from_content(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
        return "".join(text_parts)
    return str(content)

def auto_write_to_chroma(node: StreetInsightNode):
    try:
        collection = get_chroma_collection()
        node_id = f"harvested_{node.area_name.lower()}_{node.sub_lane_or_landmark.lower()}_{node.category.lower()}".replace(" ", "_")
        
        doc_text = (
            f"Area: {node.area_name}, Lane: {node.sub_lane_or_landmark}. "
            f"Famous for: {', '.join(node.specialty_goods_or_food)}. "
            f"Details: {node.bargaining_tactics}"
        )
        
        collection.add(
            ids=[node_id],
            documents=[doc_text],
            metadatas=[{
                "area_name": node.area_name,
                "sub_lane": node.sub_lane_or_landmark,
                "category": node.category,
                "status": "unverified",
                "price_band": node.price_band,
                "bargaining_tactics": node.bargaining_tactics
            }]
        )
        logger.info(f"Autonomous storage write successful: {node_id}")
    except Exception as e:
        logger.error(f"Failed to auto-persist node to ChromaDB collection: {e}")

def harvester_node(state: AgentState) -> dict:
    query = state.get("raw_query", "")
    snippets = search_community_discussions(query, max_results=5)
    
    if not snippets:
        return {"harvested_data": None}

    prompt = f"{HARVESTER_SYSTEM_PROMPT}\n\nSearch Snippets:\n{snippets}\n\nOriginal Query: {query}"
    
    # Execution block with high-availability model fallback
    try:
        try:
            logger.info("Attempting processing via primary engine (Gemini 3.8 Flash)...")
            response = primary_llm.invoke(prompt)
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                logger.warning("Primary engine experiencing high demand (503). Instantly failing over to stable backup...")
                response = backup_llm.invoke(prompt)
            else:
                raise e
                
        raw_text = extract_text_from_content(response.content)
        cleaned = raw_text.strip().replace("```json", "").replace("```", "").strip()
        extracted = json.loads(cleaned)
        
        if not extracted or not extracted.get("area_name") or extracted.get("area_name") == "Unknown":
            return {"harvested_data": None}
            
        validated_node = StreetInsightNode(**extracted)
        
        if (
            validated_node.sub_lane_or_landmark 
            and validated_node.confidence_score >= 0.65
            and "nagpur" in str(snippets).lower()
        ):
            auto_write_to_chroma(validated_node)
            return {"harvested_data": validated_node.model_dump()}
        else:
            log_to_quarantine(validated_node.model_dump(), query)
            return {"harvested_data": None}
            
    except Exception as e:
        logger.error(f"Harvester runtime node execution failure: {e}")
        return {"harvested_data": None}
