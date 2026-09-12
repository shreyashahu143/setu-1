from src.tools.db_tools import init_vector_db

collection = init_vector_db()
results = collection.query(
    query_texts=["where can I get my cracked phone screen repaired?"],
    n_results=1
)

print("Best Match:", results['documents'][0][0])
print("Metadata:", results['metadatas'][0][0])
print("Distance:", results['distances'][0][0])
