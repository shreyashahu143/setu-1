from src.graph import app

def run_e2e_tests():
    print("\n==========================================")
    print("TEST 1: Pure SCOUT Query")
    print("==========================================")
    out1 = app.invoke({"raw_query": "Where can I get my phone screen fixed in Sitabuldi?"})
    print(f"Intent detected: {out1['intent']}")
    print(out1["final_payload"])
    assert "Modi No. 3" in out1["final_payload"]

    print("\n==========================================")
    print("TEST 2: Pure LINGO Query")
    print("==========================================")
    out2 = app.invoke({
        "raw_query": "How do I tell an auto driver to charge by meter?",
        "user_origin": "Kerala"
    })
    print(f"Intent detected: {out2['intent']}")
    print(out2["final_payload"])
    assert "What to Say" in out2["final_payload"]

    print("\n==========================================")
    print("TEST 3: HYBRID Query")
    print("==========================================")
    out3 = app.invoke({
        "raw_query": "Where do I buy wedding sarees in Sitabuldi and how should I bargain with the seller?",
        "user_origin": "Telangana"
    })
    print(f"Intent detected: {out3['intent']}")
    print(out3["final_payload"])
    assert "Where to Go" in out3["final_payload"]
    assert "What to Say" in out3["final_payload"]

    print("\n✅ All End-to-End Multi-Agent Pipeline Tests Passed!")

if __name__ == "__main__":
    run_e2e_tests()
