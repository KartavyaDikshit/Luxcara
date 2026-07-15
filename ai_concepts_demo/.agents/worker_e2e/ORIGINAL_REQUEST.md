## 2026-07-15T18:06:03Z
<USER_REQUEST>
You are assigned to create the E2E Test Suite for the AI Concepts Interactive Demo project.
Working Directory: /Users/kartavyadikshit/teamwork_projects/ai_concepts_demo/.agents/worker_e2e
Project Root: /Users/kartavyadikshit/teamwork_projects/ai_concepts_demo
Requirements:
1. Build a comprehensive opaque-box test runner (e.g., `tests/test_e2e.py` or `run_e2e_tests.py`).
2. Implement tests categorized into 4 tiers:
   - Tier 1: Directory scaffolding test - checks existence of all 7 topic directories: `1_RAG_Mastery`, `2_LLM_API`, `3_Prompt_Engineering`, `4_Agents`, `5_Risk_Evaluation`, `6_German_Language`, `7_Legal_Walkthrough`.
   - Tier 2: Notebook validity test - checks that every topic directory contains at least one `.ipynb` file and that every notebook is valid JSON (nbformat compliant).
   - Tier 3: Notebook content verification test - checks that notebooks contain both markdown explanation cells (theory) and python code cells (demonstration/mock execution logic).
   - Tier 4: Scaffolding verifier test - executes `python verify_project.py` and confirms exit code is 0 and stdout reports success.
3. Ensure all tests run cleanly using standard Python standard library or pytest.
4. Run your tests, document results, and publish `TEST_READY.md` in project root with total count, tier summary, and pass criteria.
5. Write a handoff report in your working directory and notify the parent orchestrator via send_message.
</USER_REQUEST>
