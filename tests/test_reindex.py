import json

from src.tools.db_tools import get_chroma_collection


col = get_chroma_collection()

with open("data/seed_nagpur.json", "r", encoding="utf-8") as f:
    nodes = json.load(f)

for n in nodes:
    node_id = (
        f"{n['area_name'].lower()}_"
        f"{n['sub_lane_or_landmark'].lower()}_"
        f"{n['category'].lower()}"
    ).replace(" ", "_")

    document = (
        f"Area: {n['area_name']}, "
        f"Lane: {n['sub_lane_or_landmark']}. "
        f"Goods: {', '.join(n['specialty_goods_or_food'])}. "
        f"Tips: {n['bargaining_tactics']}"
    )

    metadata = {
        "area_name": n["area_name"],
        "sub_lane": n["sub_lane_or_landmark"],
        "category": n["category"],
        "status": n.get("status", "verified"),
        "price_band": n.get("price_band", ""),
        "bargaining_tactics": n.get("bargaining_tactics", ""),
    }

    col.upsert(
        ids=[node_id],
        documents=[document],
        metadatas=[metadata],
    )

print(f"Re-indexed successfully! {len(nodes)} nodes.")