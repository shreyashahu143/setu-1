# src/tools/db_tools.py

import json
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./data/chroma_db"
COLLECTION_NAME = "nagpur_street_nodes"

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def query_street_nodes(query_text: str, top_k: int = 1):
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k
    )
    
    # Check if empty
    if not results or not results["documents"] or len(results["documents"][0]) == 0:
        return None, 1.0
    
    # Chroma returns 2D lists: list of results per query
    best_doc = results["documents"][0][0]
    best_meta = results["metadatas"][0][0]
    best_distance = float(results["distances"][0][0])
    
    return {
        "document": best_doc,
        "metadata": best_meta
    }, best_distance

