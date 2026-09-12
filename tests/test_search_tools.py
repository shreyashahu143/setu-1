from src.tools.search_tools import search_community_discussions

def test_forum_search():
    query = "wholesale plant nursery ceramic pots"
    results = search_community_discussions(query)
    
    print("\n--- Scraped Community Snippets ---")
    print(results[:500] if results else "No snippets retrieved.")
    print("----------------------------------\n")
    
    assert len(results) > 0, "Failed to retrieve community search snippets!"
    print("Search Tool Test Passed!")

if __name__ == "__main__":
    test_forum_search()
