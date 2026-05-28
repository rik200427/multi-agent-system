# ─────────────────────────────────────────────────────────────
# Shared state schema for the multi-agent research pipeline.
# Every agent receives this dict and returns an updated version.
# ─────────────────────────────────────────────────────────────

from typing import TypedDict, List

class ResearchState(TypedDict):
    query: str           # original user question
    urls: List[str]      # URLs found by Search Agent
    content: List[str]   # scraped text chunks from Reader Agent
    draft: str           # report draft produced by Writer Chain
    feedback: str        # critique and score from Critic Chain
    final_report: str    # approved final output
    iteration: int       # number of Writer → Critic revision loops run