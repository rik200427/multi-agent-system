# ─────────────────────────────────────────────────────────────
# Reader Agent — scrapes full content from each URL found by
# the Search Agent using requests + BeautifulSoup4.
# Input  state fields : urls, content (snippets from search)
# Output state fields : content (full scraped text, replaces snippets)
# ─────────────────────────────────────────────────────────────

import os
import sys

# allow imports from project root when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from state import ResearchState

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MAX_CHARS_PER_SOURCE = 3000  # cap per source to stay within LLM context
MIN_CHARS_THRESHOLD  = 200   # discard pages with less than this — likely garbage


def scrape_url(url: str) -> str:
    """
    Scrapes a single URL and returns clean body text.
    Returns empty string on any failure — never raises.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # remove noise elements
        for tag in soup(["script", "style", "nav", "footer",
                         "header", "aside", "form", "noscript"]):
            tag.decompose()

        # extract clean text
        text = soup.get_text(separator="\n", strip=True)

        # collapse excessive blank lines
        lines = [line for line in text.splitlines() if line.strip()]
        text  = "\n".join(lines)

        # quality gate — discard near-empty pages
        if len(text) < MIN_CHARS_THRESHOLD:
            print(f"  [Reader Agent] Skipped (too short): {url}")
            return ""

        return text[:MAX_CHARS_PER_SOURCE]

    except requests.exceptions.Timeout:
        print(f"  [Reader Agent] Timeout: {url}")
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"  [Reader Agent] HTTP error {e.response.status_code}: {url}")
        return ""
    except Exception as e:
        print(f"  [Reader Agent] Failed ({type(e).__name__}): {url}")
        return ""


def reader_agent(state: ResearchState) -> ResearchState:
    """
    Scrapes full content from all URLs in state.
    Replaces the short Tavily snippets with full extracted text.
    Skips failed URLs gracefully — pipeline continues regardless.
    """
    urls = state["urls"]
    print(f"\n[Reader Agent] Scraping {len(urls)} URLs...")

    full_content = []

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}")
        text = scrape_url(url)

        if text:
            # label each chunk clearly so the Writer knows which source it came from
            full_content.append(f"SOURCE {i}: {url}\n{'-' * 40}\n{text}")
        else:
            # fall back to the Tavily snippet if scraping failed
            fallback = state["content"][i - 1] if i - 1 < len(state["content"]) else ""
            if fallback:
                print(f"  [Reader Agent] Using Tavily snippet as fallback for source {i}")
                full_content.append(fallback)

    print(f"\n[Reader Agent] Successfully extracted {len(full_content)}/{len(urls)} sources")

    if not full_content:
        print("[Reader Agent] WARNING: No content extracted from any URL.")

    return {**state, "content": full_content}


# # ── quick test ───────────────────────────────────────────────
# if __name__ == "__main__":
#     from state import ResearchState

#     # use a known stable URL for testing
#     test_state: ResearchState = {
#         "query":        "latest advances in quantum computing",
#         "urls":         [
#             "https://en.wikipedia.org/wiki/Quantum_computing",
#             "https://thisisabadurlthatwillfail.xyz",   # tests error handling
#         ],
#         "content":      [
#             "SOURCE: https://en.wikipedia.org/wiki/Quantum_computing\nFallback snippet.",
#             "SOURCE: https://thisisabadurlthatwillfail.xyz\nFallback snippet.",
#         ],
#         "draft":        "",
#         "feedback":     "",
#         "final_report": "",
#         "iteration":    0,
#     }

#     result = reader_agent(test_state)

#     print(f"\n✅ Content chunks : {len(result['content'])}")
#     print(f"\nFirst chunk preview (300 chars):")
#     print(result["content"][0][:300] if result["content"] else "None")