from src.agents.scout import scout_node

def test_scout_agent():
    # 1. Known query -> Must be a HIT on Modi No. 3
    hit_state = {"raw_query": "Where can I fix my phone display screen in Sitabuldi?"}
    hit_res = scout_node(hit_state)
    assert hit_res["cache_status"] == "HIT", f"Expected HIT, got {hit_res['cache_status']}"
    assert "Modi No. 3" in hit_res["scout_data"]["sub_lane"], f"Expected Modi No. 3, got {hit_res['scout_data']['sub_lane']}"
    print(f"HIT Test Passed: Matched {hit_res['scout_data']['sub_lane']} (Distance: {hit_res['scout_data']['confidence_distance']})")

    # 2. Unknown query not in seed data -> Must be a CACHE_MISS
    miss_state = {"raw_query": "Where to buy high-end scuba diving equipment in Nagpur?"}
    miss_res = scout_node(miss_state)
    assert miss_res["cache_status"] == "CACHE_MISS", f"Expected CACHE_MISS, got {miss_res['cache_status']}"
    print("CACHE_MISS Test Passed: Unseeded topic correctly flagged for Harvester fallback!")

if __name__ == "__main__":
    test_scout_agent()
