# Luxcara AI Concepts Demo

Welcome to the **Luxcara AI Concepts Demo** repository! This project serves as an interactive educational walkthrough of advanced AI engineering concepts, tailored for enterprise and legal workflows. 

The primary demo is located in the `ai_concepts_demo` directory and is fully self-contained using **mock data and simulated API responses**. This means you do **not** need an OpenAI API key or any external service accounts to run these examples.

---

## 📚 Comprehensive Module Guide

The project is structured into 7 core modules. Below is a deep dive into the theoretical concepts and technical workings demonstrated within each Jupyter Notebook.

### 1. RAG Mastery (`1_RAG_Mastery`)
This module breaks down the end-to-end Retrieval-Augmented Generation (RAG) pipeline, shifting away from generic vector search toward enterprise-grade accuracy.
* **Chunking Strategies:** Explains how to break documents down. We explore fixed-size, sentence-based, and semantic chunking, with a specific focus on recursive character splitting (e.g., 1000 tokens with 200 overlap) which is ideal for long-form investment PDFs.
* **Embeddings & Vector Databases:** Discusses model selection (e.g., `text-embedding-3-small` vs. multilingual models like `multilingual-e5-large`) and indexing strategies (HNSW, IVF) for efficient retrieval.
* **Hybrid Search (BM25 + Vector Search):** Pure vector search fails on exact keywords (like "Fund I" or "IRR"). This section demonstrates how to combine BM25 keyword scoring with Vector semantic scoring using Reciprocal Rank Fusion (RRF).
* **Query Transformations & Re-ranking:** Covers how to rewrite vague user queries, generate hypothetical documents (HyDE) for better matching, and apply a Cross-Encoder to re-rank the final retrieved chunks for maximum relevance.
* **Hallucination Mitigation:** Implements strict system prompts with source grounding ("cite the chunk number"), structured JSON extraction to prevent free-form hallucination, and post-generation confidence scoring.

### 2. LLM API Integration (`2_LLM_API`)
Focuses on building robust, production-ready LLM service connections rather than simple scripts.
* **Authentication & Security:** Best practices for managing API keys (using `.env`, Azure Key Vault, or API gateways for department-level rate limiting), ensuring secrets are never hardcoded.
* **Streaming Generation:** Simulates Server-Sent Events (SSE) to stream tokens back to the user in real-time, greatly improving perceived UI performance compared to waiting for a full response.
* **Error Handling & Resilience:** Implements exponential backoff for rate limits (`429`) and connection timeouts, ensuring the system recovers gracefully under load.
* **Token Management:** Pre-computes token sizes (using `tiktoken` logic) to manage costs. Demonstrates a "Token Budget" class to prevent runaway generation limits per department.
* **Chat Completion Modes:** Contrasts standard Chat Modes with Function Calling (forcing the LLM to output arguments for a specific tool) and persistent Assistant APIs.

### 3. Prompt Engineering (`3_Prompt_Engineering`)
Moves beyond basic prompting into structured frameworks that force the LLM into predictable behaviors.
* **Few-Shot & Zero-Shot:** Demonstrates how providing 2-3 structured examples (Few-shot) drastically improves the consistency of data extraction tasks (like NDA clause extraction) over generic Zero-shot queries.
* **Chain-of-Thought (CoT):** Forces the model to emit its step-by-step reasoning ("Think step by step...") before generating the final answer. This uses more tokens but significantly reduces logical errors in financial analysis.
* **Skeleton-of-Thought:** Instructs the LLM to first output a structured outline, and then fill in the sections, ensuring comprehensive coverage without rambling.
* **Constitutional AI (Self-Constraint):** Embeds behavioral checks into the prompt (e.g., "Am I protecting confidential data?") so the model evaluates its own appropriateness before answering.
* **Prompt Chaining:** Breaks complex tasks down into a pipeline of smaller, specific prompts (e.g., Extract Dates -> Identify Obligations -> Generate Summary) rather than one massive prompt.

### 4. Autonomous Agents (`4_Agents`)
Explores how LLMs can dynamically decide which tools to use rather than following a static script.
* **ReAct (Reason + Act) Loop:** The core pattern of agentic behavior. The agent follows a loop of: *Thought* (I need to find the IRR) -> *Action* (Search database) -> *Observation* (12.5%) -> *Final Answer*.
* **Hierarchical Agents:** Demonstrates delegating tasks. An Orchestrator Agent takes a large request and assigns sub-tasks to specialized agents (e.g., a Research Agent for RAG, an Analysis Agent for calculation, and a Writer Agent for drafting).
* **Safety & Infinite Loop Prevention:** Implements hard constraints (`MAX_ITERATIONS` and `MAX_COST_PER_SESSION`) to ensure an agent doesn't get stuck in an expensive, endless loop trying to solve an impossible task.

### 5. Risk Evaluation (`5_Risk_Evaluation`)
Provides a framework for evaluating LLM outputs objectively to ensure enterprise safety.
* **Quality Evaluation Framework:** Measures outputs against specific dimensions: *Faithfulness* (is it true to context?), *Answer Relevance*, *Completeness*, and *Safety*.
* **Automated Evaluation Pipelines:** Uses an "LLM-as-a-Judge" to automatically score generated responses against a rubric, creating an automated testing suite for prompt changes.
* **Department-Specific Risk Profiles:** Analyzes how risk differs by team (e.g., Fund Management needs absolute numerical accuracy, Legal requires strict confidentiality, and IR needs consistent messaging).
* **Incident Response Plan:** Outlines the steps (Isolate, Assess, Contain, Root Cause, Fix) if a model ever outputs harmful or factually dangerous information.

### 6. German-Language AI (`6_German_Language`)
Specific considerations for Luxcara, which operates in Germany and processes German legal/financial documents.
* **Multilingual Embeddings:** Why English-trained models fail on German syntax, and how to use models like `multilingual-e5-large` to correctly embed German concepts.
* **Compound Noun Handling:** Addresses how to effectively chunk and search for massive German compound words (e.g., *Jahresfehlbetrag*).
* **Tone & Register:** Managing formal (*Sie*) versus informal (*Du*) addressing consistently across generated outputs.

### 7. Legal Walkthrough (`7_Legal_Walkthrough`)
A practical culmination of the concepts above, applied directly to a Legal team scenario.
* **NDA & Contract Analyzer:** Simulates extracting key dates, parties, and obligations from incoming legal documents.
* **EU AI Act Compliance:** Classifies the AI application's risk tier under the EU AI Act, demonstrating how to generate compliance checklists, log usage audits, and evaluate potential copyright watermarking requirements.

---

## 🚀 How to Run

1. Open the repository in your favorite IDE (like VS Code) or launch Jupyter Lab.
2. Navigate into the `ai_concepts_demo/` folder.
3. Open any of the `.ipynb` notebooks in the subdirectories.
4. Run the cells from top to bottom. Because the notebooks use mock data, they will execute immediately without needing environment variables or API keys.

## ✅ Verification & Testing

The project includes built-in verification scripts generated by the multi-agent system:
- `verify_project.py`: Automatically validates the directory structure and notebook JSON syntax.
- `run_e2e_tests.py`: Runs an end-to-end test suite confirming all components are in place.

---
*Built with the Antigravity Teamwork Multi-Agent System.*
