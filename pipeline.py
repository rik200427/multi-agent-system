# ─────────────────────────────────────────────────────────────
# Pipeline Orchestrator — direct procedural chain
# Manages state flow: Search → Read → Write → Critique → (Revise or Approve)
# ─────────────────────────────────────────────────────────────

import os
import sys

# allow imports from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from state import ResearchState
from agents.search_agent import search_agent
from agents.reader_agent import reader_agent
from agents.writer_chain import writer_agent
from agents.critic_chain import critic_agent, is_approved


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def initialize_state(query: str) -> ResearchState:
    """Initializes the research state with user query and empty fields."""
    return ResearchState(
        query=query,
        urls=[],
        content=[],
        draft="",
        feedback="",
        final_report="",
        iteration=0
    )


def increment_iteration(state: ResearchState) -> ResearchState:
    """Increment the iteration counter for revision tracking."""
    state["iteration"] += 1
    return state


def finalize_report(state: ResearchState) -> ResearchState:
    """Finalize the report after critique and return the completed state."""
    state["final_report"] = state["draft"]

    if is_approved(state["feedback"]):
        print("\n✓ [Pipeline] Report approved by Critic.")
    else:
        print(f"\n⚠ [Pipeline] Max revisions reached. Returning best available draft.")

    return state


def save_report(path: str, state: ResearchState) -> None:
    """Save the final research report to a UTF-8 markdown file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(state["final_report"])

    print(f"\n✓ Saved final report to: {path}")


# ─────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────

def run_research_pipeline(query: str) -> ResearchState:
    """Runs the complete multi-agent research pipeline on a user query."""
    print(f"\n{'='*70}")
    print("🔍 Multi-Agent Research Pipeline")
    print(f"{'='*70}")
    print(f"Topic: {query}\n")

    state = initialize_state(query)
    state = search_agent(state)
    state = reader_agent(state)
    state = writer_agent(state)
    state = critic_agent(state)

    max_revisions = 2
    while not is_approved(state["feedback"]) and state["iteration"] < max_revisions:
        state = increment_iteration(state)
        state = writer_agent(state)
        state = critic_agent(state)

    state = finalize_report(state)

    print(f"\n{'='*70}")
    print("✓ Research Complete")
    print(f"{'='*70}\n")

    return state


# ─────────────────────────────────────────────────────────────
# Debugging / Direct execution
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_query = "Latest advances in LLMs"
    result = run_research_pipeline(sample_query)

    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)
    print(result["final_report"])

    save_report("final_report.md", result)
