import logging
import os
import sys
from src.agents.harvestor import harvester_node

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_harvester_flow():
    # Query for something not in the 15 seed nodes
    state = {
        "raw_query": "Where can I buy wholesale ceramic pots and plant containers in Nagpur?"
    }
    
    print("\n--- Running Live Harvester Test ---")
    result = harvester_node(state)
    harvested = result.get("harvested_data")
    
    if harvested:
        print("\n✅ Successfully Harvested Structured Node:")
        print(f"Area:       {harvested.get('area_name')}")
        print(f"Sub-lane:   {harvested.get('sub_lane_or_landmark')}")
        print(f"Goods:      {harvested.get('specialty_goods_or_food')}")
        print(f"Price Band: {harvested.get('price_band')}")
        print(f"Status:     {harvested.get('status')}")
        print(f"Confidence: {harvested.get('confidence_score')}")
    else:
        print("\n⚠️ No confident node passed the gatekeeper (logged to quarantine or search was empty).")
        
if __name__ == "__main__":
    test_harvester_flow()
