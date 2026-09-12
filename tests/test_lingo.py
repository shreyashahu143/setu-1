import os
from src.agents.lingo import lingo_node



def test_lingo_agent():
    state = {
        "raw_query": "How do I tell an auto driver to take me to Sitabuldi without overcharging?",
        "user_origin": "Telangana"
    }
    result = lingo_node(state)
    lingo = result.get("lingo_data", {})
    
    print("\n--- Lingo Agent Output ---")
    print(f"Spoken Script: {lingo.get('spoken_script')}")
    print(f"Phonetics:     {lingo.get('phonetic_english')}")
    print(f"Tone:          {lingo.get('tone_directive')}")
    print(f"Cultural Tip:  {lingo.get('cultural_insight')}")
    
    assert "spoken_script" in lingo, "Missing spoken_script in output"
    assert "phonetic_english" in lingo, "Missing phonetic_english in output"
    print("\nLingo Agent Test Passed!")

if __name__ == "__main__":
    test_lingo_agent()
