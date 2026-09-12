import json
from src.schemas.node import StreetInsightNode

with open("data/seed_nagpur.json", "r") as f:
    data = json.load(f)

assert len(data) >= 15, f"Expected at least 15 nodes, got {len(data)}"
for item in data:
    StreetInsightNode(**item)
print(f"Validation successful: {len(data)} nodes match StreetInsightNode schema!")
