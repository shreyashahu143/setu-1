import os
from src.agents.router import router_node

def test_router_intents():
    # 1. Test SCOUT
    res_scout = router_node({"raw_query": "Where can I repair my phone screen cheaply in Sitabuldi?"})
    assert res_scout["intent"] in ["SCOUT", "HYBRID"], f"Expected SCOUT, got {res_scout['intent']}"

    # 2. Test LINGO
    res_lingo = router_node({"raw_query": "How do I tell an auto driver to charge fair rate without being rude?"})
    assert res_lingo["intent"] == "LINGO", f"Expected LINGO, got {res_lingo['intent']}"

    # 3. Test HYBRID
    res_hybrid = router_node({"raw_query": "Where do I buy wedding sarees in Itwari and what Marathi phrase to use for bargaining?"})
    assert res_hybrid["intent"] == "HYBRID", f"Expected HYBRID, got {res_hybrid['intent']}"

    print("All 3 Router intent tests passed successfully!")

if __name__ == "__main__":
    test_router_intents()
