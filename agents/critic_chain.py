# ─────────────────────────────────────────────────────────────
# Critic Chain — LCEL chain that reviews the Writer's draft
# like a senior researcher, scores it, and decides whether
# to approve it or send it back for revision.
# Input  state fields : query, draft
# Output state fields : feedback
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
    temperature=0.1,       # very low temp — scoring must be consistent
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Prompt ──────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a senior research editor at a professional think tank.
You are reviewing a junior analyst's research report.
Be rigorous, specific, and constructive.

You MUST respond in EXACTLY this format — do not deviate:

SCORE: [single integer 1-10]

STRENGTHS:
- [specific strength 1]
- [specific strength 2]
- [specific strength 3]

WEAKNESSES:
- [specific weakness 1]
- [specific weakness 2]

VERDICT: [APPROVE or REVISE]

INSTRUCTIONS:
[If VERDICT is APPROVE]: Report meets professional standards. Approved for release.
[If VERDICT is REVISE]: List the exact changes the writer must make in the next draft.
Be specific — say which section needs changing and exactly how.

Scoring guide:
8-10 → Well structured, thorough, well cited, clear analysis     → APPROVE
6-7  → Good but missing depth, weak analysis, or citation gaps   → REVISE
1-5  → Poor structure, vague, unsupported claims, off-topic      → REVISE

Only APPROVE if score is 8 or above."""
    ),
    (
        "human",
        """Original research topic: {query}

Report to review:
{draft}

Provide your editorial review now:"""
    )
])

# ── LCEL chain ───────────────────────────────────────────────
critic_chain = critic_prompt | llm | StrOutputParser()


# ── helpers ──────────────────────────────────────────────────
def parse_score(feedback: str) -> int:
    """Extracts the integer score from the critic's feedback string."""
    try:
        for line in feedback.splitlines():
            if line.strip().startswith("SCORE:"):
                score_str = line.replace("SCORE:", "").strip()
                return int("".join(filter(str.isdigit, score_str)))
    except Exception:
        pass
    return 0  # default to 0 if parsing fails — triggers revision


def is_approved(feedback: str) -> bool:
    """Returns True if the Critic approved the report."""
    return "VERDICT: APPROVE" in feedback


# ── Agent function ───────────────────────────────────────────
def critic_agent(state: ResearchState) -> ResearchState:
    """
    Reviews the current draft and returns structured feedback.
    Verdict of APPROVE finalises the report.
    Verdict of REVISE triggers another Writer loop (up to max iterations).
    """
    print(f"\n[Critic Chain] Reviewing draft...")

    feedback = critic_chain.invoke({
        "query": state["query"],
        "draft": state["draft"]
    })

    score   = parse_score(feedback)
    verdict = "APPROVED ✅" if is_approved(feedback) else "REVISE 🔄"

    print(f"[Critic Chain] Score: {score}/10 — Verdict: {verdict}")

    return {**state, "feedback": feedback}


# # ── quick test ───────────────────────────────────────────────
# if __name__ == "__main__":
#     from state import ResearchState

#     test_state: ResearchState = {
#         "query": "latest advances in quantum computing",
#         "urls":  [],
#         "content": [],
#         "draft": """# Quantum Computing: Latest Advances

# ## Executive Summary
# Quantum computing has seen significant breakthroughs in 2024,
# particularly in error correction and qubit stability.
# IBM and Google are leading commercial development efforts.

# ## Key Findings
# ### 1. Error Correction
# Google announced a major error correction milestone in early 2024,
# demonstrating below-threshold error rates for the first time [Source 1].

# ### 2. IBM Quantum
# IBM's 1000+ qubit Condor processor represents the largest quantum
# processor publicly announced to date [Source 1].

# ## Analysis
# The field is moving from theoretical to practical. Error correction
# is the critical bottleneck — solving it unlocks real-world applications.

# ## Conclusion
# Quantum computing is approaching an inflection point where
# practical applications in cryptography and drug discovery become viable.

# ## Sources
# - [Source 1]: https://en.wikipedia.org/wiki/Quantum_computing""",
#         "feedback":     "",
#         "final_report": "",
#         "iteration":    0,
#     }

#     result = critic_agent(test_state)

#     print("\n" + "=" * 60)
#     print("CRITIC FEEDBACK:")
#     print("=" * 60)
#     print(result["feedback"])