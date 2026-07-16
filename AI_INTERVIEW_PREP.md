# AI Interview Prep & Mastery Guide

## 1. RAG — Deep Mastery
### The Full Pipeline (Know Every Step)
*   **[Documents]**
    ↓
*   **[Chunking]** → strategy, size, overlap
    ↓
*   **[Embedding]** → model selection, batch processing
    ↓
*   **[Vector DB]** → storage, indexing (HNSW, IVF), metadata filtering
    ↓
*   **[Query]** → Query transformation (rewriting, HyDE, multi-query)
    ↓
*   **[Retrieval]** → Vector search + Keyword search (Hybrid)
    ↓
*   **[Fusion]** → Reciprocal Rank Fusion or re-ranking
    ↓
*   **[Context Assembly]** → Sliding window, truncation strategy
    ↓
*   **[Generation]** → System prompt, citation format, temperature
    ↓
*   **[Output]** → Structured (JSON), with references
    ↓
*   **[Evaluation]** → Faithfulness, answer relevance, context precision

### Chunking Deep Dive
| Strategy | Token size | Overlap | When to use |
| :--- | :--- | :--- | :--- |
| Fixed-size | 256-1024 | 10-20% | General purpose, simple |
| Sentence-based | By sentence boundaries | 1-2 sentences | Legal/contract documents |
| Semantic | By topic shift (embedding similarity < threshold) | None | Long reports with clear sections |
| Recursive | Mixed (start large, split on special chars) | Varies | Code, markdown, structured docs |

**For Luxcara specifically:** Their documents are likely long-form PDFs (investment memos, fund reports, legal contracts). Best approach:
```python
RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""])
```
*Why 1000 tokens?* Captures enough context for a meaningful paragraph but fits in most model context windows with room for instructions.

### Embedding Models Comparison
| Model | Dimensions | Best for |
| :--- | :--- | :--- |
| `text-embedding-ada-002` | 1536 | General English, cheap |
| `text-embedding-3-small` | 512-1536 | Better quality, cheaper |
| `text-embedding-3-large` | 3072 | Highest quality |
| `intfloat/multilingual-e5-large` | 1024 | Multilingual (German!) |
| `sentence-transformers/distiluse-base-multilingual-cased-v2` | 512 | German documents, runs locally |

**Key insight for Luxcara:** They operate in German. If their documents are in German, English embedding models will perform worse. Mention: *"For German-language investment documents, I'd use `multilingual-e5-large` or a German-specific SentenceTransformer model — ensures that queries like 'Fondsperformance' retrieve semantically relevant German documents."*

### Hybrid Search (BM25 + Vector)
Pure vector search fails on:
*   Exact terms (fund names: "Luxcara Clean Energy Fund I")
*   Rare acronyms ("PPA", "BESS", "IRR")
*   Numbers ("EUR 7.5B")

Hybrid search solves this:
`query = "What is the IRR of Luxcara Clean Energy Fund I?"`
*   **BM25 scores:** "IRR" → high score (rare term) + "Luxcara Clean Energy Fund I" → exact match
*   **Vector scores:** Similar meaning to "fund performance returns"
*   **RFF Fusion:** Combine both scores → rerank → top-7

**Implementation:**
```python
# BM25
from rank_bm25 import BM25Okapi
tokenized_docs = [doc.split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)
bm25_scores = bm25.get_scores(query.split())

# Vector
from openai import OpenAI
client = OpenAI()
query_embedding = client.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
vector_scores = cosine_similarity([query_embedding], doc_embeddings)[0]

# Fusion
from rank_bm25 import K
n = len(documents)
combined = []
for i in range(n):
    bm25_rank = rank_bm25[i]  # position in BM25 ranking
    vec_rank = rank_vector[i]  # position in vector ranking
    rrf_score = 1/(60 + bm25_rank) + 1/(60 + vec_rank)  # RRF with constant k=60
    combined.append((rrf_score, i))
combined.sort(reverse=True)
```

### Query Transformations (Advanced)
When users ask vague questions, raw search fails. Apply these:
1.  **Query Rewriting:** "How's the fund doing?" → "Luxcara Clean Energy Fund I quarterly performance 2026"
2.  **HyDE (Hypothetical Document Embeddings):** Generate a hypothetical ideal document, embed it, search with that instead
3.  **Multi-query:** Generate 3 variations of the question, search all, deduplicate results
4.  **Step-back prompting:** "What are the key metrics for evaluating a clean energy infrastructure fund?" → broader context first

**Code for multi-query:**
```python
prompt = f"""Generate 3 different versions of the following question 
to improve retrieval from an investment document database.
Make each version focus on a different aspect.

Original: {user_query}

Versions (one per line):"""
```

### Re-ranking (Step After Retrieval)
After retrieving 20-30 candidates, re-rank with a cross-encoder (more expensive but more accurate):
```python
from sentence_transformers import CrossEncoder
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
pairs = [[query, chunk] for chunk in candidate_chunks]
scores = model.predict(pairs)
top_k_indices = np.argsort(scores)[-7:][::-1]
```
**Why this matters for Luxcara:** Cross-encoders consider the full query-document pair, catching nuance that bi-encoders (used in vector search) miss. Critical for financial documents where precision matters.

### Hallucination Mitigation — Full Toolkit
**1. Source Grounding (most important)**
```python
SYSTEM_PROMPT = """You are an AI assistant analyzing Luxcara investment documents.
CRITICAL RULES:
- Answer ONLY using the provided context documents
- If the context doesn't contain the answer, say "The provided documents do not contain this information"
- For every claim, cite the document name and chunk number: [Doc: Quarterly Report Q2 2026, Chunk: 4]
- Never infer, guess, or generate financial figures
- If numerical values differ between documents, flag the discrepancy
"""
```

**2. Structured Output Extraction (Prevents Free-Form Hallucinations)**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    response_format={"type": "json_object"},  # Forces JSON output
    temperature=0.0  # Maximum determinism
)
```

**3. Factual Consistency Checking**
After generation, run a separate model call to verify:
```python
verification_prompt = f"""Document: {context}
Generated answer: {output}

Does the answer contain any claims NOT supported by the document?
List each unsupported claim and explain why it's unsupported."""
```

**4. Confidence Scoring**
```python
confidence_prompt = f"""Given the context and the answer, rate your confidence from 0-1:
- 0: Completely guessing
- 0.5: Somewhat supported
- 1.0: Directly stated in context

Answer: {output}
Confidence score:"""
# Reject answers below 0.7 threshold
```

### Self-RAG (Advanced Pattern)
Instead of retrieve-then-generate, interleave retrieval and generation:
1.  Model decides IF retrieval is needed
2.  If yes: retrieves, generates with citations
3.  If no: answers from parametric knowledge
4.  Model evaluates its own output quality
5.  If low quality: retrieves again and regenerates

**For the interview, name-drop this:** *"Self-RAG is interesting for Luxcara because it reduces unnecessary retrieval calls — cheaper, faster, and fewer irrelevant chunks."*

---

## 2. LLM API — Production-Level Knowledge

### Authentication Deep Dive
```python
# NEVER hardcode
# BAD:
api_key = "sk-abc123..."

# GOOD:
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("LLM_API_KEY")

# BETTER for teams:
# Use Azure Key Vault, AWS Secrets Manager, or HashiCorp Vault
# Rotate keys every 90 days
# Scoped keys per department (Fund Management vs Legal vs Accounting)

# BEST for enterprise:
# Use API gateways (Kong, AWS API Gateway) with:
# - Authentication (OAuth2, API keys)
# - Rate limiting (different limits per team)
# - Usage tracking (cost per department)
# - Logging (all requests, no sensitive data)
```

### Streaming (Critical for UI)
```python
from openai import OpenAI
client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a summary"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
        # Send to frontend via WebSocket
```
**Why Luxcara cares:** If they build internal tools, streaming provides better UX — users see text appear in real-time instead of staring at a spinner.

### Error Handling — Production-Ready
```python
import time
from openai import RateLimitError, APIError, APIConnectionError

def call_llm_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1
            )
            return response.choices[0].message.content
        
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        
        except APIConnectionError:
            print(f"Connection error. Retry {attempt+1}/{max_retries}")
            time.sleep(5)
        
        except APIError as e:
            if e.status_code == 400:  # Bad request — don't retry
                raise
            time.sleep(2 ** attempt)
    
    raise Exception("All retries exhausted")
```

### Token Management
```python
# Count tokens before sending (critical for cost control)
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Budget management per department
class TokenBudget:
    def __init__(self, monthly_limit):
        self.monthly_limit = monthly_limit
        self.used = 0
    
    def can_proceed(self, estimated_tokens, cost_per_token):
        cost = estimated_tokens * cost_per_token
        return self.used + cost <= self.monthly_limit
    
    def log_usage(self, tokens_used):
        self.used += tokens_used * 0.00003  # GPT-4 input cost per token
```
**For the interview:** *"For Luxcara, I'd track token usage per department — Fund Management queries might be more complex and expensive than simple document lookups. This helps budget appropriately and identify misuse."*

### Chat Completion Modes
```python
# Chat Mode (standard)
messages = [
    {"role": "system", "content": "You are a financial analyst..."},
    {"role": "user", "content": "Analyze this fund report..."}
]

# Function Calling (for structured tools)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_fund_performance",
            "description": "Get performance data for a fund",
            "parameters": {
                "type": "object",
                "properties": {
                    "fund_name": {"type": "string"},
                    "quarter": {"type": "string"}
                }
            }
        }
    }
]

# Assistant API (for persistent threads/conversations)
# Useful for a chatbot that remembers context across sessions
assistant = client.beta.assistants.create(
    name="Luxcara AI Assistant",
    instructions="Help employees find information...",
    model="gpt-4",
    tools=[{"type": "retrieval"}, {"type": "code_interpreter"}]
)
```

---

## 3. Prompt Engineering — Complete Framework

### Anatomy of a Perfect Prompt
```text
[Role Definition]
You are [expert persona] at [company]. Your expertise is [domain].

[Context]
You have access to the following information:
{context}

[Task]
Your task is to [specific objective].

[Constraints]
- Do NOT [action 1]
- Always [action 2]
- If [condition], then [response]

[Format]
Return your response in the following structure:
- Field 1: [description]
- Field 2: [description]

[Example]
Input: {example_input}
Output: {example_output}

[Input]
{user_query}
```

### All Prompt Patterns (with Luxcara examples)

**1. Zero-shot** (No examples, just instruction)
`Extract the key terms from this investment contract: {text}`

**2. Few-shot** (2-5 examples)
```text
Extract key clauses from NDAs:

Example 1:
Input: "Party A shall maintain confidentiality for 5 years"
Output: Clause: Confidentiality, Duration: 5 years, Parties: Party A

Example 2:
Input: "Any dispute shall be resolved by arbitration in Hamburg"
Output: Clause: Dispute Resolution, Method: Arbitration, Venue: Hamburg

Now extract from:
Input: "{new_contract_text}"
Output:
```

**3. Chain-of-Thought** (Step-by-step reasoning)
```text
Analyze this fund report. Think step by step:
1. First, identify the fund name and reporting period
2. Then, extract the total NAV and comparison to previous quarter
3. Next, identify top 5 holdings and their weights
4. After that, flag any risk warnings or material changes
5. Finally, provide a summary

Report: {report_text}
Analysis:
```

**4. Structured Output** (JSON)
```json
Return the analysis as JSON:
{
  "fund_name": "...",
  "reporting_period": "...",
  "total_nav": {"current": 0, "previous": 0, "change_pct": 0},
  "top_holdings": [{"name": "...", "weight_pct": 0}],
  "risk_flags": ["..."],
  "summary": "..."
}
```

**5. Persona/Role Prompting**
`You are a senior investment analyst at Luxcara with 15 years of experience in clean energy infrastructure. You have personally evaluated over 100 wind, solar, and battery storage projects across Europe. Your analysis is known for being thorough, conservative, and data-driven. Review this investment memorandum and provide your assessment.`

**6. Skeleton-of-Thought** (Structured outline first)
```text
Before writing the full analysis, create a structured outline:
1. Executive Summary (2-3 sentences)
2. Key Metrics (table format)
3. Risk Assessment (high/medium/low per category)
4. Recommendations (action items)

After outlining, expand each section.
```

**7. Constitutional AI** (Self-constraint)
```text
You are an AI assistant for Luxcara. Before answering, check:
- Is this question within my scope (investment document analysis)?
- Do I have sufficient context to answer accurately?
- Could my response be misinterpreted?
- Am I protecting confidential information?

If any check fails, explain why you cannot answer.
```

**8. Prompt Chaining** (Multi-step)
For complex tasks, break into sequential prompts:
*   Step 1: "Extract all dates, monetary values, and party names from this contract." → Intermediate output
*   Step 2: "Based on the extracted fields, identify obligations, deadlines, and penalties." → Intermediate output
*   Step 3: "Generate a summary with upcoming deadlines and action items." → Final output

### Prompt Debugging When Things Go Wrong
| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| Generic answers | Prompt too vague, no constraints | Add specific instructions, format constraints |
| Hallucinated numbers | No grounding instruction | Add "Only use values from the provided text. If not present, say 'not stated'" |
| Too verbose | No length constraint | "Respond in 3 bullet points max" |
| Ignores instructions | System prompt too long, model loses attention | Put most critical instructions first |
| Structured output fails | Model can't follow JSON under pressure | Lower temperature, add example, use response_format |
| Repeats itself | Context too long, no diversity penalty | Increase presence_penalty, reduce max_tokens |

---

## 4. Agents — Complete Understanding

### Agent Types

**1. Simple ReAct Agent (Reason + Act)**
```text
Thought: I need to find the fund's IRR
Action: search_database(query="fund_irr Luxcara Fund I")
Observation: {"irr": "12.5%"}
Thought: I have the IRR. I should format the response.
Action: respond("The IRR is 12.5%")
```
*LangChain implementation:*
```python
from langchain.agents import create_react_agent
from langchain.tools import Tool

tools = [
    Tool(name="Document Search", func=rag_search, description="Search investment documents"),
    Tool(name="Database Query", func=query_fund_database, description="Query fund performance data"),
    Tool(name="Calculator", func=calculate, description="Perform calculations")
]

agent = create_react_agent(llm, tools, prompt)
```

**2. Hierarchical (Your AiSupportAssistant)**
```text
Orchestrator Agent
    → Task Planner: Decomposes "Analyze Q2 performance and draft investor letter"
        → Research Agent: Queries RAG for Q2 data
        → Analysis Agent: Computes metrics
        → Writer Agent: Drafts the letter
    → Quality Checker: Reviews output
    → Final output to user
```
*Benefits for Luxcara:* Different departments need different tools. Fund Management needs database access, Legal needs contract RAG, Accounting needs spreadsheet tools. A hierarchical agent routes work to the right sub-agent.

**3. Tool-Use Agent (OpenAI Function Calling)**
```python
assistant = client.beta.assistants.create(
    name="Luxcara Assistant",
    instructions="Help employees with document analysis...",
    tools=[
        {"type": "retrieval"},  # Built-in RAG
        {"type": "code_interpreter"},  # Run Python code (for calculations)
        {
            "type": "function",
            "function": {
                "name": "get_fund_data",
                "parameters": {"fund_name": {"type": "string"}}
            }
        }
    ]
)
```

### Agent Safety (Critical for Enterprise)

**Infinite loop prevention:**
```python
MAX_ITERATIONS = 10
MAX_TOOL_CALLS = 5
iteration = 0

while iteration < MAX_ITERATIONS:
    response = model.invoke(...)
    if response.tool_calls:
        iteration += 1
        if iteration >= MAX_ITERATIONS:
            return {"error": "Max iterations reached, returning partial results"}
        # execute tool
    else:
        return response.content
```

**Cost control:**
```python
MAX_COST_PER_SESSION = 0.50  # USD
cost_so_far = 0

for step in agent_execution:
    cost_so_far += step.token_count * step.model_cost
    if cost_so_far > MAX_COST_PER_SESSION:
        return {"message": "Budget limit reached for this session. Please refine your query."}
```

**Audit logging:**
```json
{
  "session_id": "abc123",
  "user": "kartavya.dikshit@luxcara.com",
  "department": "Fund Management",
  "query": "What's the IRR of Fund I?",
  "steps": [
    {"step": 1, "action": "thought", "content": "I need to search fund documents"},
    {"step": 2, "action": "tool:rag_search", "input": "IRR Fund I", "output": "12.5%"},
    {"step": 3, "action": "respond", "content": "The IRR is 12.5%"}
  ],
  "total_tokens": 1243,
  "cost": 0.037,
  "duration_ms": 2450
}
```

---

## 5. Risk Evaluation — Complete Framework

### Quality Evaluation Framework
*   **Accuracy:** Is the output factually correct?
*   **Completeness:** Does it cover all required aspects?
*   **Relevance:** Does it address the user's actual question?
*   **Consistency:** Is it internally consistent (no contradictions)?
*   **Timeliness:** Is the information current?
*   **Actionability:** Can the user act on this output?
*   **Safety:** Does it expose confidential data or give dangerous advice?

### Building an Evaluation Pipeline
```python
# Automated evaluation
def evaluate_response(query, context, response, expected=None):
    scores = {}
    
    # 1. Faithfulness (does response stay true to context?)
    faithfulness_prompt = f"""Context: {context}
Response: {response}
Rate faithfulness from 0-1 (how much of the response is supported by context):"""
    scores['faithfulness'] = call_llm(faithfulness_prompt)
    
    # 2. Answer relevance (does it answer the question?)
    relevance_prompt = f"""Question: {query}
Response: {response}
Rate relevance from 0-1:"""
    scores['relevance'] = call_llm(relevance_prompt)
    
    # 3. Hallucination detection
    hallucination_prompt = f"""Context: {context}
Response: {response}
List ANY claims in the response NOT found in context:"""
    hallucinations = call_llm(hallucination_prompt)
    scores['hallucination_count'] = count_claims(hallucinations)
    
    # 4. Numerical accuracy (for financial data)
    if expected:
        from sklearn.metrics import mean_absolute_error
        scores['numerical_error'] = mean_absolute_error(expected, extract_numbers(response))
    
    return scores

# Human evaluation loop
def collect_feedback(response_id, user_rating, user_comment):
    """Store user feedback for model improvement"""
    db.store("evaluation", {
        "response_id": response_id,
        "rating": user_rating,  # 👍 or 👎
        "comment": user_comment,
        "timestamp": datetime.now()
    })
```

### Department-Specific Risk Profiles
| Department | Risk | Mitigation |
| :--- | :--- | :--- |
| Fund Management | Wrong valuations | Human sign-off on all numbers |
| Accounting | Compliance errors | Automated reconciliation with source data |
| Investor Relations | Inconsistent messaging | Centralized response templates, approval workflow |
| Legal | Confidentiality breach | No PII/external data to public LLMs, local models only |
| All | Over-reliance | "AI-assisted, human-verified" policy |
| All | Data leakage | Enterprise tenant (not free ChatGPT), audit logs |

### Incident Response Plan
If an AI tool produces a harmful output:
1.  **Isolate** — Disable the specific tool/feature immediately
2.  **Assess** — How many users saw it? What data was involved? Was any action taken based on it?
3.  **Contain** — If data was sent externally, revoke API keys. If incorrect info was acted on, notify affected parties
4.  **Root cause** — Was it a prompt issue? Retrieval failure? Model limitation?
5.  **Fix** — Update prompt, improve RAG, add guardrails
6.  **Re-deploy** — Test on the failing case, then roll out with monitoring
7.  **Document** — Write up the incident for the AI guidelines

---

## 6. German-Language AI Considerations (Luxcara-Specific)

Since Luxcara operates in Germany and their documents are likely German:

**German-specific challenges:**
*   German sentence structure (verb at end) confuses chunking
*   Compound nouns ("Fondsperformancebewertung") — embedding models may not capture meaning
*   Formal vs informal address (Sie vs du) — prompts must be consistent
*   German-specific financial terms (Jahresfehlbetrag, Gewinnvortrag, stiller Reserve)

**Solutions:**
*   Use multilingual embedding models (not English-only)
*   Chunk by paragraphs (not sentences) for better German coherence
*   Prompt in German for German documents — model thinks better in the document's language
*   Test with German example inputs in few-shot prompts

**Code for German RAG:**
```python
from sentence_transformers import SentenceTransformer
# German-optimized model
model = SentenceTransformer('intfloat/multilingual-e5-large')
text = "Die Fondsperformance hat sich im zweiten Quartal verbessert."
embedding = model.encode(text)
```

---

## 7. Full Walkthrough: "Build an Internal Tool for Legal" (Most Likely Scenario)

They'll probably ask you to design something. Here's your complete framework:

**Step 1: Discovery (5 min)**
*"I'd start by spending a day shadowing the Legal team. What documents do they handle most? NDAs, investment agreements, fund documentation? Where do they spend most time? Manual contract review? Clause extraction? Compliance checking?"*

**Step 2: Scope (MVP)**
*"Start with one high-impact, low-risk task. For example: 'Extract key dates and obligations from incoming NDAs.' This is repetitive, manual, and low-risk if it fails (they can always re-read the contract)."*

**Step 3: Technical Design (Whiteboard)**
`Upload NDA PDF → OCR (if scanned) → Chunk by clause → Embed → Store`
`New NDA received → Extract text → Run extraction prompt against LLM → Return structured JSON`

System Prompt:
*"You are a legal document analyzer for Luxcara. Extract ONLY explicitly stated information. Never infer missing clauses. If a clause type is not present, state 'Not found in document'."*

Output:
```json
{
  "contract_type": "NDA",
  "parties": ["Luxcara GmbH", "..."],
  "effective_date": "...",
  "confidentiality_period_years": 5,
  "governing_law": "...",
  "key_obligations": ["..."],
  "upcoming_deadlines": ["2026-08-15: Annual renewal notice"],
  "risk_flags": ["Unlimited liability clause in section 7.3"]
}
```

**Step 4: Implementation (Tech Stack)**
*"I'd use Python with LangChain for the orchestration layer, Streamlit for a quick UI prototype, and deploy as a Docker container on their internal infrastructure. For storage, local files with a simple SQLite database for tracking."*

**Step 5: Evaluation**
*"Test on 10 NDAs where we know the ground truth. Measure extraction accuracy per field. Goal: >90% accuracy on structured fields before going live."*

**Step 6: Training + Rollout**
*"Create a one-page guide: 'How to use the NDA Analyzer.' Include examples of what it CAN and CANNOT do. Have a feedback button. Shadow the first 3 uses with the Legal team member. Once they're comfortable, let them use it independently."*

**Step 7: Iterate**
*"Collect all feedback. What fields did they need that weren't included? What errors happened? Update the prompt and schema. Repeat monthly."*

---

## 8. Anti-Patterns to Avoid (Interview Landmines)

| Don't say | Instead say |
| :--- | :--- |
| "The LLM is wrong" | "The LLM's output didn't match the source materials — likely a retrieval or grounding issue" |
| "I just use ChatGPT" | "I use OpenAI/Claude APIs with carefully engineered prompts and evaluation pipelines" |
| "Temperature is randomness" | "Temperature controls the probability distribution of token sampling — lower values for deterministic tasks, higher for creative ones" |
| "Embeddings are magic" | "Embeddings map text to high-dimensional vectors where semantic similarity correlates with cosine distance" |
| "I train my own models" | "For enterprise use cases, using foundation models with RAG is more practical — fine-tuning is only needed for very specific domains" |
| "We can automate everything" | "We should start with high-impact, low-risk tasks and gradually increase scope as we validate reliability" |

---

## 9. Your Interview Script (Memorize This Flow)

**When they ask "Tell us about your experience with AI":**
*"I focus on practical AI — building systems that work in enterprise environments, not just proof-of-concepts. At Brainy Insights, I built RAG systems with Claude and NotebookLM specifically for asset management workflows — financial report generation with hallucination mitigation. I also developed hierarchical AI agents for automating complex analysis tasks. Across my work, I've always prioritized: (1) grounding outputs in source data, (2) evaluating for quality and risk systematically, and (3) enabling non-technical users through training and documentation. Luxcara's mission at the intersection of clean energy and finance is exactly where I want to apply this."*

**When they ask about a specific technical decision:**
Use the STAR-decision format:
*   **Situation:** "We needed to automate financial report generation"
*   **Task:** "Ensure outputs were grounded and hallucination-free"
*   **Action:** "Used RAG with Claude, chunked documents at 500 tokens with overlap, implemented citation requirements in the prompt, and set temperature to 0 for consistency"
*   **Result:** "Reliable report generation with <1% hallucination rate"
*   **Decision rationale:** "500-token chunks because financial paragraphs are typically 300-600 tokens. 50-token overlap to avoid cutting sentences. Temperature=0 because we want deterministic outputs for financial data."

**When they ask about evaluating AI quality:**
*"I use a multi-layer approach: (1) Automated metrics — faithfulness scoring, answer relevance, hallucination detection. (2) Human evaluation — spot-check 10% of outputs, especially for new use cases. (3) User feedback — thumbs up/down with optional comments, which feeds into iteration. (4) Continuous monitoring — dashboards tracking accuracy, latency, cost, and failure modes per department."*

**When they ask about risks:**
*"Three risks I always address: (1) Hallucinations — mitigated by RAG, grounding, and low temperature. (2) Data protection — never send sensitive data to public models; use enterprise tenants or local models; train users on what's safe to share. (3) Over-reliance — always keep a human in the loop for significant decisions, and clearly communicate what the AI can and cannot do."*

---

## 10. Your Pre-Call Checklist
- [x] VS Code open with Python environment ready
- [x] GitHub profile open with pinned repos (AiSupportAssistant, ReadIT)
- [x] A test file with a basic RAG workflow ready to show
- [x] Transcripts and certificates ready to send (if asked)
- [x] Water, good internet, quiet room
- [x] Phone away, notifications off
- [x] Have the prep material open in a secondary window for quick reference

*You know this stuff. You've built it. Tomorrow is just about explaining clearly what you already do. Trust your experience.*
