import json
import os
import sys

PROJECT_ROOT = "/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo"

notebook_paths = [
    "1_RAG_Mastery/rag_mastery_demo.ipynb",
    "2_LLM_API/llm_api_demo.ipynb",
    "3_Prompt_Engineering/prompt_engineering_demo.ipynb",
    "4_Agents/autonomous_agents_demo.ipynb",
    "5_Risk_Evaluation/risk_evaluation_demo.ipynb",
    "6_German_Language/german_language_ai_demo.ipynb",
    "7_Legal_Walkthrough/legal_ai_act_demo.ipynb"
]

def verify_all():
    all_passed = True
    print("=== VERIFYING NOTEBOOKS JSON & EXECUTION ===")
    
    for rel_path in notebook_paths:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        print(f"\nChecking: {rel_path}")
        
        # 1. Existence check
        if not os.path.exists(full_path):
            print(f"  ❌ FAILED: File does not exist at {full_path}")
            all_passed = False
            continue

        # 2. JSON validation
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                nb = json.load(f)
            print("  ✓ Valid JSON format")
        except Exception as e:
            print(f"  ❌ FAILED: Invalid JSON - {str(e)}")
            all_passed = False
            continue

        # Check nbformat fields
        if nb.get("nbformat") != 4 or "cells" not in nb:
            print("  ❌ FAILED: Missing nbformat version 4 structure")
            all_passed = False
            continue

        # 3. Code Execution Verification
        code_cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
        print(f"  Executing {len(code_cells)} code cells...")
        
        global_env = {}
        for idx, cell in enumerate(code_cells, 1):
            code_text = "".join(cell.get("source", []))
            try:
                exec(code_text, global_env)
            except Exception as e:
                print(f"  ❌ FAILED Code Cell {idx} in {rel_path}:\n{e}")
                all_passed = False
                break
        else:
            print(f"  ✓ All {len(code_cells)} code cells executed successfully without error!")

    if all_passed:
        print("\n🎉 ALL 7 NOTEBOOKS PASSED VERIFICATION PERFECTLY!")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED ON ONE OR MORE NOTEBOOKS!")
        sys.exit(1)

if __name__ == "__main__":
    verify_all()
