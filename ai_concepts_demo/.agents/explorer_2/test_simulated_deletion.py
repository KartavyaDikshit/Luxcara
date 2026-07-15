import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo")
TOPIC_DIRECTORIES = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough",
]
STUB_FILES = [
    "1_RAG_Mastery/rag_mastery.ipynb",
    "2_LLM_API/llm_api.ipynb",
    "3_Prompt_Engineering/prompt_engineering.ipynb",
    "4_Agents/agents.ipynb",
    "5_Risk_Evaluation/risk_evaluation.ipynb",
    "6_German_Language/german_language.ipynb",
    "7_Legal_Walkthrough/legal_walkthrough.ipynb",
]

print("=== SIMULATING TIER 3 TEST WITHOUT STUB FILES ===")
failures = []
for topic_dir in TOPIC_DIRECTORIES:
    dir_path = PROJECT_ROOT / topic_dir
    all_notebooks = list(dir_path.glob("*.ipynb"))
    filtered_notebooks = [nb for nb in all_notebooks if f"{topic_dir}/{nb.name}" not in STUB_FILES]
    
    print(f"\nDirectory: {topic_dir}")
    print(f"  Notebooks evaluated: {[nb.name for nb in filtered_notebooks]}")
    
    for nb_path in filtered_notebooks:
        with open(nb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cells = data.get("cells", [])
        has_markdown = False
        has_code = False
        for cell in cells:
            cell_type = cell.get("cell_type")
            source = cell.get("source", "")
            source_str = "".join(source) if isinstance(source, list) else str(source)
            if cell_type == "markdown" and source_str.strip():
                has_markdown = True
            elif cell_type == "code" and source_str.strip():
                has_code = True
        
        if not has_markdown or not has_code:
            failures.append((nb_path.name, has_markdown, has_code))
            print(f"  ❌ FAIL: {nb_path.name} (MD: {has_markdown}, Code: {has_code})")
        else:
            print(f"  ✓ PASS: {nb_path.name} (MD: {has_markdown}, Code: {has_code})")

print("\n" + "=" * 50)
print(f"Total failures after stub removal: {len(failures)}")
if len(failures) == 0:
    print("ALL NOTEBOOK CONTENT VERIFICATIONS PASSED SUCCESSFULLY!")
else:
    print(f"Failures remaining: {failures}")
