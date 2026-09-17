from src.schemas.state import AgentState

def synthesis_node(state: AgentState) -> dict:
    scout_data = state.get("scout_data")
    lingo_data = state.get("lingo_data")
    harvested_data = state.get("harvested_data")
    cache_status = state.get("cache_status")
    intent = state.get("intent", "SCOUT")
    
    sections = []
    
    # 1. Location & Lane Section
    if scout_data:
        status_tag = " [Verified Street Guide]" if scout_data.get("status") == "verified" else " [Community Tip]"
        lane_card = (
            f"### 📍 Where to Go{status_tag}\n"
            f"- **Area & Lane:** {scout_data.get('area_name')}, {scout_data.get('sub_lane')}\n"
            f"- **Category:** {scout_data.get('category')}\n"
            f"- **Price Estimate:** {scout_data.get('price_band')}\n"
            f"- **Bargaining & Access:** {scout_data.get('bargaining_tactics')}"
        )
        sections.append(lane_card)
    elif harvested_data:
        lane_card = (
            f"### 📍 Where to Go [Community Discovery - Unverified]\n"
            f"- **Area & Lane:** {harvested_data.get('area_name')}, {harvested_data.get('sub_lane_or_landmark')}\n"
            f"- **Category:** {harvested_data.get('category', 'Shopping')}\n"
            f"- **Price Estimate:** {harvested_data.get('price_band', 'Street rates apply')}\n"
            f"- **Bargaining & Access:** {harvested_data.get('bargaining_tactics', 'Negotiate firmly')}\n"
            f"- *Note: Freshly harvested from local community discussions. Treat prices as approximate.*"
        )
        sections.append(lane_card)
    elif cache_status == "CACHE_MISS" and intent in ["SCOUT", "HYBRID"]:
        miss_card = (
            "### 📍 Where to Go\n"
            "*We couldn't find a verified traditional lane for this in our database yet.* "
            "Our background harvester has been notified to look into local discussions."
        )
        sections.append(miss_card)
        
    # 2. Local Street Script & Culture Section
    if lingo_data:
        vocab_note = f"- **Local Term Alert:** {lingo_data.get('local_term_replacement')}\n" if lingo_data.get('local_term_replacement') and lingo_data.get('local_term_replacement') != "null" else ""
        script_card = (
            "### 🗣️ What to Say (Street Script)\n"
            f"{vocab_note}"
            f"- **Say this:** \"{lingo_data.get('spoken_script')}\"\n"
            f"- **Pronunciation:** *{lingo_data.get('phonetic_english')}*\n"
            f"- **Meaning:** {lingo_data.get('literal_meaning')}\n"
            f"- **Tone Advice:** {lingo_data.get('tone_directive')}\n"
            f"- **Local Insight:** {lingo_data.get('cultural_insight')}"
        )
        sections.append(script_card)
        
    final_payload = "\n\n".join(sections)
    return {"final_payload": final_payload}
