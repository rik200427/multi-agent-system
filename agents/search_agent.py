# ─────────────────────────────────────────────────────────────
# Search Agent — uses Tavily API to find the top 5 live web
# sources for the user's research query.
# Input  state fields : query
# Output state fields : urls, content (snippets)
# ─────────────────────────────────────────────────────────────

import os
import sys

# allow imports from the project root when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tavily import TavilyClient
from dotenv import load_dotenv
from state import ResearchState

load_dotenv()

# initialise Tavily client once at module load
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_agent(state: ResearchState) -> ResearchState:
    """
    Searches the web for the user's query using Tavily.
    Populates state with URLs and initial content snippets.
    The Reader Agent will later scrape full content from these URLs.
    """
    query = state["query"]
    print(f"\n[Search Agent] Searching for: '{query}'")

    try:
        results = client.search(
            query=query,
            search_depth="advanced",  # deeper crawl on free tier
            max_results=5,
            include_raw_content=False  # snippets only — Reader handles full scrape
        )


        urls = []
        snippets = []

        for r in results.get("results", []):  #get method for safe access in case "results" key is missing
            url     = r.get("url", "")
            content = r.get("content", "")

            if url and content:
                urls.append(url)
                snippets.append(f"SOURCE: {url}\n{content}")

        print(f"[Search Agent] Found {len(urls)} sources:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")

        if not urls:
            print("[Search Agent] WARNING: No results returned by Tavily.")

        return {**state, "urls": urls, "content": snippets}  #This is immutable-style update

    except Exception as e:
        print(f"[Search Agent] ERROR: {e}")
        # return state unchanged so pipeline can handle the failure gracefully
        return {**state, "urls": [], "content": []}


# ── quick test ───────────────────────────────────────────────
# if __name__ == "__main__":
#     from state import ResearchState

#     test_state: ResearchState = {
#         "query":        "latest advances in quantum computing 2024",
#         "urls":         [],
#         "content":      [],
#         "draft":        "",
#         "feedback":     "",
#         "final_report": "",
#         "iteration":    0,
#     }

#     result = search_agent(test_state)

#     print(f"\n✅ URLs found   : {len(result['urls'])}")
#     print(f"✅ Snippets     : {len(result['content'])}")
#     print(f"\nFirst snippet preview:\n{result['content'][0][:300] if result['content'] else 'None'}")




#Tavily return format example:
# results = {
#     "results": [
#         {
#             "url": "https://example.com",
#             "content": "Some text..."
#         },
#         {
#             "url": "https://another.com",
#             "content": "More text..."
#         }
#     ]
# }