# Original User Request

## 2026-07-15T18:05:33Z

Build an interactive educational demo using Jupyter Notebooks to showcase the internal workings of advanced RAG, LLM APIs, Prompt Engineering, Agents, Risk Evaluation, and German-language AI considerations.

Working directory: ~/teamwork_projects/ai_concepts_demo
Integrity mode: development

## Requirements

### R1. Project Scaffolding
Create a well-structured directory layout covering all 7 requested topics: `1_RAG_Mastery`, `2_LLM_API`, `3_Prompt_Engineering`, `4_Agents`, `5_Risk_Evaluation`, `6_German_Language`, and `7_Legal_Walkthrough`.

### R2. Interactive Notebooks with Mock Data
Inside each topic directory, create at least one Jupyter Notebook (`.ipynb`). The notebooks should contain a mix of Markdown cells explaining the theory and Python cells demonstrating the concepts.
Use mock data, simulated LLM API responses, and dummy embeddings so that all notebooks can execute end-to-end without requiring actual API keys.

### R3. Verification Script
Create a Python script `verify_project.py` in the root directory that automatically verifies the scaffolding. It should check that all 7 directories exist, each contains at least one `.ipynb` file, and that the notebooks are valid JSON files.

## Acceptance Criteria

### Verification
- [ ] Running `python verify_project.py` exits with code 0.
- [ ] The `verify_project.py` script confirms the existence of the 7 specific directories.
- [ ] The `verify_project.py` script confirms at least one `.ipynb` file is present in each directory.
