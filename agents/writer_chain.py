# ─────────────────────────────────────────────────────────────
# Writer Chain — LCEL chain that synthesises scraped content
# into a structured markdown research report.
# On revision loops, incorporates Critic feedback into the rewrite.
# Input  state fields : query, content, feedback, iteration
# Output state fields : draft
# ─────────────────────────────────────────────────────────────

import os
import sys

# allow imports from project root when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import ResearchState

load_dotenv()

# ── LLM ─────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,       # low temp = factual, consistent output
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Prompt ──────────────────────────────────────────────────
write_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research analyst and technical writer.
Your job is to synthesise information from multiple web sources into a
professional, well-structured research report in markdown format.

Follow this exact structure:
# [Report Title]

## Executive Summary
2-3 sentences summarising the key findings.

## Key Findings
### 1. [Finding Title]
Detailed explanation with inline source citations like [Source 1], [Source 2].

### 2. [Finding Title]
...

### 3. [Finding Title]
...

## Analysis
Deeper interpretation of the findings. What do they mean collectively?
What patterns or themes emerge across sources?

## Conclusion
Final takeaways. What should the reader walk away knowing?

## Sources
List all sources used as:
- [Source 1]: URL
- [Source 2]: URL

Rules:
- Only use information from the provided sources — never hallucinate
- Cite sources inline using [Source N] notation
- Be detailed and thorough — this is a professional report
- Use clear markdown formatting throughout"""
    ),
    (
        "human",
        """Research topic: {query}

Source material:
{content}

{feedback_instruction}

Write the full research report now:"""
    )
])

# ── LCEL chain ───────────────────────────────────────────────
writer_chain = write_prompt | llm | StrOutputParser()


# ── Agent function ───────────────────────────────────────────
def writer_agent(state: ResearchState) -> ResearchState:
    """
    Drafts a structured markdown research report from scraped content.
    On revision loops (iteration > 0), rewrites incorporating Critic feedback.
    """
    print(f"\n[Writer Chain] Drafting report (iteration {state['iteration']})...")

    # build feedback instruction only on revision loops
    feedback_instruction = ""
    if state.get("feedback") and state["iteration"] > 0:
        feedback_instruction = f"""IMPORTANT — You are rewriting a previous draft.
The Critic reviewed your last draft and gave this feedback:

{state['feedback']}

Address every point in the feedback in this new version.
Improve the sections that were criticised. Keep what was praised."""

    # join all content chunks into one block
    combined_content = "\n\n---\n\n".join(state["content"])

    draft = writer_chain.invoke({
        "query":               state["query"],
        "content":             combined_content,
        "feedback_instruction": feedback_instruction
    })

    print(f"[Writer Chain] Draft complete — {len(draft)} characters")
    return {**state, "draft": draft}


# ── quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    from state import ResearchState

    test_state: ResearchState = {
        "query":   "latest advances in quantum computing",
        "urls":    ["https://en.wikipedia.org/wiki/Quantum_computing"],
        "content": [
            """SOURCE 1: https://en.wikipedia.org/wiki/Quantum_computing
----------------------------------------
Quantum computing is a type of computation that harnesses quantum mechanical
phenomena such as superposition and entanglement. IBM released a 1000+ qubit
processor in 2023. Google claimed quantum supremacy in 2019. Major challenges
include error correction and qubit stability at scale."""
        ],
        "draft":        "",
        "feedback":     "",
        "final_report": "",
        "iteration":    0,
    }

    result = writer_agent(test_state)

    print("\n" + "=" * 60)
    print("DRAFT REPORT PREVIEW (first 800 chars):")
    print("=" * 60)
    print(result["draft"][:800])