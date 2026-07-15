import json
from pathlib import Path

root = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo")
dirs = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough"
]

print("=== DETAILED NOTEBOOK INVENTORY ===")
for d in dirs:
    dp = root / d
    nbs = sorted(list(dp.glob("*.ipynb")))
    print(f"\nDirectory: {d}")
    for nb in nbs:
        with open(nb, "r", encoding="utf-8") as f:
            data = json.load(f)
        cells = data.get("cells", [])
        md_count = sum(1 for c in cells if c.get("cell_type") == "markdown" and "".join(c.get("source", "")).strip())
        code_count = sum(1 for c in cells if c.get("cell_type") == "code" and "".join(c.get("source", "")).strip())
        print(f"  File: {nb.name}")
        print(f"    Total cells: {len(cells)}")
        print(f"    Markdown cells with content: {md_count}")
        print(f"    Code cells with content: {code_count}")
