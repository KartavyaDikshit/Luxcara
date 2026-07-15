# Project: AI Concepts Interactive Demo

## Overview
An interactive educational demo using Jupyter Notebooks to showcase internal workings of RAG, LLM APIs, Prompt Engineering, Agents, Risk Evaluation, German-language AI, and Legal Walkthrough. Includes a root-level verification script `verify_project.py`.

## Code Layout
- `1_RAG_Mastery/` - Notebook(s) on Advanced RAG (retrieval, chunking, embeddings, re-ranking)
- `2_LLM_API/` - Notebook(s) on LLM APIs (simulated requests, streaming, parameters, mock data)
- `3_Prompt_Engineering/` - Notebook(s) on Prompting techniques (few-shot, chain-of-thought, system prompts)
- `4_Agents/` - Notebook(s) on AI Agents (tool calling, reasoning loops, multi-agent concepts)
- `5_Risk_Evaluation/` - Notebook(s) on Risk & Evaluation (red-teaming, benchmarks, hallucination detection)
- `6_German_Language/` - Notebook(s) on German NLP/AI considerations (tokenization, compound words, nuances)
- `7_Legal_Walkthrough/` - Notebook(s) on Legal/EU AI Act compliance walkthroughs
- `verify_project.py` - Scaffolding and validity verification script in project root

## Architecture & Interface Contracts
- `verify_project.py`: Needs to exit with code 0 on success, non-zero on failure. Checks 7 specific directories exist, contain at least one `.ipynb` notebook file each, and all `.ipynb` files parse cleanly as valid JSON.
- Notebooks (`.ipynb`): Valid JSON standard format (nbformat v4 schema), executing without external network API calls (using mock data & simulated responses).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | E2E Testing Track | Create comprehensive opaque-box E2E test suite & `TEST_READY.md` | None | PLANNED |
| 2 | Scaffolding & Verifier | Create 7 topic directories and `verify_project.py` verifier script | None | PLANNED |
| 3 | Notebook Content Creation | Build interactive educational Jupyter Notebooks across all 7 topic directories with mock data & theory | M2 | PLANNED |
| 4 | Final E2E Test & Coverage Pass | Pass 100% E2E tests and perform coverage hardening | M1, M2, M3 | PLANNED |
