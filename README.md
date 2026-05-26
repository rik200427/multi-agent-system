# 🤖 Multi-Agent Research Assistant

A fully autonomous AI research system that **searches, reads, writes, and critiques** on its own. Instead of a single AI answering from memory, a team of specialised agents collaborate to produce a structured, sourced research report on any topic.

Built with **LangChain LCEL · OpenAI GPT-4o-mini · Tavily Search API · BeautifulSoup4**

---

## 📌 What It Does

You give it a topic. It gives you a professional research report — automatically.

```
"Latest advances in quantum computing"
        ↓
[Search Agent]   → finds top 5 live web sources via Tavily
[Reader Agent]   → scrapes and extracts content from each URL
[Writer Chain]   → synthesises a structured markdown report
[Critic Chain]   → scores the report and requests revisions if needed
        ↓
 Final sourced research report  ✓
```

---

## 🏗️ Architecture

```
User Query
    │
    ▼
LangChain LCEL Orchestrator
    │
    ├──▶ Search Agent  (Tavily API)         → urls, snippets
    │
    ├──▶ Reader Agent  (BeautifulSoup4)     → scraped content
    │
    ├──▶ Writer Chain  (GPT-4o-mini)        → markdown draft
    │
    └──▶ Critic Chain  (GPT-4o-mini)        → score + feedback
              │
              └── if REVISE → Writer Chain loops (max 2x)
                  if APPROVE → Final Report
```

All agents communicate through a single **shared state dictionary** — every agent reads from it and writes back to it, acting as one unified pipeline.

---

## 🗂️ Project Structure

```
multi-agent-research/
│
├── agents/
│   ├── search_agent.py      # Tavily API — finds sources
│   ├── reader_agent.py      # BeautifulSoup4 — scrapes URLs
│   ├── writer_chain.py      # LCEL chain — drafts the report
│   └── critic_chain.py      # LCEL chain — reviews and scores
│
├── state.py                 # Shared ResearchState TypedDict
├── pipeline.py              # Orchestrator — chains all agents
├── app.py                   # Streamlit frontend
│
├── .env                     # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Search | Tavily API | Live web search, clean results for LLMs |
| Scraping | BeautifulSoup4 + requests | Extract body text from URLs |
| LLM | OpenAI GPT-4o-mini | Writer and Critic agents |
| Orchestration | LangChain LCEL | Chain agents, route shared state |
| Frontend | Streamlit | Interactive demo UI |
| Config | python-dotenv | Manage API keys via `.env` |
| Resilience | tenacity | Retry API calls with backoff |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/multi-agent-research.git
cd multi-agent-research
```

### 2. Create and activate a virtual environment

```bash
# Create
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — Mac / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

Get your keys here:
- **OpenAI** → https://platform.openai.com/api-keys
- **Tavily** → https://app.tavily.com (free tier)

### 5. Run

**Option A — Command line (pipeline only):**
```bash
python pipeline.py
```

**Option B — Full Streamlit demo:**
```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 🧠 Agent Details

### Search Agent
- Uses the **Tavily Search API** with `search_depth="advanced"`
- Returns the top 5 most relevant URLs and content snippets
- Tavily is purpose-built for LLM pipelines — cleaner results than raw Google scraping

### Reader Agent
- Takes the URLs from the Search Agent
- Scrapes each page using `requests` + `BeautifulSoup4`
- Strips noise (nav, scripts, footers) and extracts clean body text
- Caps each source at 2,000 characters to stay within LLM context limits
- Failed URLs are skipped gracefully — the pipeline continues

### Writer Chain
- An **LCEL chain**: `prompt | llm | StrOutputParser()`
- Receives all scraped content and writes a structured markdown report
- Report format: Executive Summary → Key Findings → Analysis → Conclusion
- On revision loops, incorporates the Critic's specific feedback

### Critic Chain
- Reviews the draft like a senior researcher
- Outputs a structured review: Score (1–10), Strengths, Weaknesses, Verdict
- `APPROVE` (score ≥ 7) → report is finalised
- `REVISE` (score < 7) → feedback is passed back to the Writer
- Maximum **2 revision loops** to control latency and API costs

---

## 💡 Example Output

**Input:**
```
What are the latest advances in quantum computing?
```

**Report structure generated:**
```markdown
# Quantum Computing: Latest Advances

## Executive Summary
...

## Key Findings
### 1. Error Correction Breakthroughs
...
### 2. Hardware Developments
...

## Analysis
...

## Conclusion
...

Sources: [1] arxiv.org/... [2] nature.com/... [3] ibm.com/...
```

**Critic review example:**
```
SCORE: 8
STRENGTHS:
- Well-structured with clear section headings
- All major claims are cited to sources
WEAKNESSES:
- Could expand on commercial implications
VERDICT: APPROVE
```

---

## ⚠️ Known Limitations

| Limitation | Details |
|---|---|
| Sequential pipeline | Agents run one at a time — full run takes ~30–90 seconds |
| Scraping fragility | JavaScript-rendered pages (React/Next.js) may return empty content |
| No persistent memory | State is lost between sessions — each run starts fresh |
| Writer can hallucinate | Critic checks quality, not factual accuracy against sources |
| Free tier limits | Tavily: 1,000 searches/month · OpenAI: usage-based billing |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for GPT-4o-mini |
| `TAVILY_API_KEY` | ✅ Yes | Tavily search API key |

---

## 📋 Requirements

- Python 3.10, 3.11, or 3.12
- See `requirements.txt` for full package list

Key packages:
```
langchain==1.3.1
langchain-openai==1.2.2
openai==2.38.0
tavily-python==0.7.24
beautifulsoup4==4.12.3
streamlit==1.57.0
```
---
