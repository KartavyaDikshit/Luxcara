#!/usr/bin/env python3
import json
import traceback
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo")
TOPICS = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough",
]

def run_notebook_stress_test():
    report = []
    total_cells_executed = 0
    total_code_cells = 0
    total_markdown_cells = 0
    failures = []

    print("=" * 70)
    print("EMPIRICAL NOTEBOOK EXECUTION RUNNER & NBFORMAT VALIDATOR")
    print("=" * 70)

    for topic in TOPICS:
        topic_dir = PROJECT_ROOT / topic
        nb_files = list(topic_dir.glob("*.ipynb"))
        
        print(f"\n--- Testing Topic Directory: {topic} ---")
        if not nb_files:
            print(f"FAILED: No notebooks found in {topic}")
            failures.append((topic, "No notebooks found"))
            continue

        for nb_path in nb_files:
            rel_path = nb_path.relative_to(PROJECT_ROOT)
            print(f"Validating nbformat structure & executing: {rel_path}")
            
            # 1. Structure / Schema checks
            try:
                with open(nb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"  ❌ JSON Load Error: {e}")
                failures.append((str(rel_path), f"JSON Load Error: {e}"))
                continue

            nbformat = data.get("nbformat")
            nbformat_minor = data.get("nbformat_minor")
            cells = data.get("cells", [])
            metadata = data.get("metadata", {})

            print(f"  Format: nbformat v{nbformat}.{nbformat_minor}")
            print(f"  Total cells: {len(cells)}")
            
            if nbformat is None:
                failures.append((str(rel_path), "Missing nbformat version"))

            # 2. Cell iteration and execution
            exec_namespace = {"__name__": "__main__"}
            nb_code_cells = 0
            nb_markdown_cells = 0

            for cell_idx, cell in enumerate(cells, start=1):
                cell_type = cell.get("cell_type")
                source = cell.get("source", [])
                if isinstance(source, list):
                    code_str = "".join(source)
                else:
                    code_str = str(source)

                if cell_type == "markdown":
                    nb_markdown_cells += 1
                    total_markdown_cells += 1
                elif cell_type == "code":
                    nb_code_cells += 1
                    total_code_cells += 1
                    if not code_str.strip():
                        continue
                    
                    # Clean up magic lines if any (e.g. %pip, !pip) for pure python exec
                    clean_lines = []
                    for line in code_str.splitlines():
                        if line.strip().startswith("%") or line.strip().startswith("!"):
                            # Skip Jupyter magics or comment them out
                            clean_lines.append(f"# {line}")
                        else:
                            clean_lines.append(line)
                    executable_code = "\n".join(clean_lines)

                    try:
                        exec(compile(executable_code, filename=f"{rel_path}:Cell_{cell_idx}", mode="exec"), exec_namespace)
                        total_cells_executed += 1
                    except Exception as err:
                        tb = traceback.format_exc()
                        print(f"  ❌ Runtime Error in Cell {cell_idx}:\n{tb}")
                        failures.append((str(rel_path), f"Cell {cell_idx} failed with {type(err).__name__}: {err}"))

            print(f"  Summary for {rel_path.name}: Markdown={nb_markdown_cells}, Code={nb_code_cells}, Status={'PASSED' if not any(f[0] == str(rel_path) for f in failures) else 'FAILED'}")

    print("\n" + "=" * 70)
    print("EMPIRICAL EXECUTION RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total Notebooks Verified: {len(TOPICS)}")
    print(f"Total Markdown Cells: {total_markdown_cells}")
    print(f"Total Code Cells: {total_code_cells}")
    print(f"Total Code Cells Executed Successfully: {total_cells_executed}")
    print(f"Total Failures: {len(failures)}")
    if failures:
        print("Failures Detail:")
        for target, msg in failures:
            print(f"  - {target}: {msg}")
    print("=" * 70)
    return len(failures) == 0

if __name__ == "__main__":
    success = run_notebook_stress_test()
    sys.exit(0 if success else 1)
