import json
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize client with cosine space
client = chromadb.PersistentClient(path="./data/chroma_db")
emb_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.create_collection(
    name="nagpur_street_nodes",
    embedding_function=emb_fn,
    metadata={"hnsw:space": "cosine"}
)

# 2. Load seed JSON
with open("data/seed_nagpur.json", "r", encoding="utf-8") as f:
    nodes = json.load(f)

# 3. Insert records
for n in nodes:
    node_id = f"{n['area_name'].lower()}_{n['sub_lane_or_landmark'].lower()}_{n['category'].lower()}".replace(" ", "_")
    doc_text = (
        f"Area: {n['area_name']}, Lane: {n['sub_lane_or_landmark']}. "
        f"Famous for: {', '.join(n['specialty_goods_or_food'])}. "
        f"Details: {n['bargaining_tactics']}"
    )
    
    collection.add(
        ids=[node_id],
        documents=[doc_text],
        metadatas=[{
            "area_name": n["area_name"],
            "sub_lane": n["sub_lane_or_landmark"],
            "category": n["category"],
            "status": n.get("status", "verified"),
            "price_band": n.get("price_band", ""),
            "bargaining_tactics": n.get("bargaining_tactics", "")
        }]
    )

print(f"Done: Indexed {len(nodes)} records into fresh ChromaDB collection with cosine metric!")
