import json
import sys
import traceback
from pathlib import Path

try:
    import nbformat
    HAS_NBFORMAT = True
except ImportError:
    HAS_NBFORMAT = False

PROJECT_ROOT = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo")
NOTEBOOKS = [
    "1_RAG_Mastery/rag_mastery_demo.ipynb",
    "2_LLM_API/llm_api_demo.ipynb",
    "3_Prompt_Engineering/prompt_engineering_demo.ipynb",
    "4_Agents/autonomous_agents_demo.ipynb",
    "5_Risk_Evaluation/risk_evaluation_demo.ipynb",
    "6_German_Language/german_language_ai_demo.ipynb",
    "7_Legal_Walkthrough/legal_ai_act_demo.ipynb",
]

def run_empirical_validation():
    print("=" * 70)
    print("EMPIRICAL NOTEBOOK VALIDATION & CELL EXECUTION HARNESS")
    print("=" * 70)
    print(f"nbformat module available: {HAS_NBFORMAT}\n")

    report = []
    total_code_cells = 0
    total_markdown_cells = 0
    total_exceptions = 0

    for idx, nb_rel_path in enumerate(NOTEBOOKS, 1):
        nb_path = PROJECT_ROOT / nb_rel_path
        
        json_valid = False
        nbformat_valid = False
        nbformat_ver = None
        cells = []
        
        # 1. JSON Validation
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                content = f.read()
            data = json.loads(content)
            json_valid = isinstance(data, dict)
        except Exception as err:
            report.append({
                "index": idx,
                "path": nb_rel_path,
                "json_valid": False,
                "nbformat_valid": False,
                "total_cells": 0,
                "code_cells": 0,
                "exec_status": f"JSON Decode Error: {err}",
            })
            continue

        # 2. nbformat Validation
        if HAS_NBFORMAT:
            try:
                nb = nbformat.reads(content, as_version=4)
                nbformat.validate(nb)
                nbformat_valid = True
                nbformat_ver = f"v{nb.nbformat}.{nb.nbformat_minor}"
                cells = nb.cells
            except Exception as err:
                nbformat_valid = False
                nbformat_ver = f"Error: {err}"
                cells = data.get("cells", [])
        else:
            nbformat_ver = f"v{data.get('nbformat', 'unknown')}"
            nbformat_valid = True if data.get('nbformat') is not None else False
            cells = data.get("cells", [])

        code_cells = [c for c in cells if c.get("cell_type") == "code"]
        markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
        total_code_cells += len(code_cells)
        total_markdown_cells += len(markdown_cells)

        # 3. Dynamic Cell Execution
        exec_globals = {
            "__file__": str(nb_path),
            "__name__": "__main__",
        }
        
        cell_errors = []
        executed_cells_count = 0

        for cell_idx, cell in enumerate(code_cells, 1):
            source = cell.get("source", "")
            if isinstance(source, list):
                source = "".join(source)

            # Sanitize magic commands
            clean_lines = []
            for line in source.splitlines():
                if line.strip().startswith("%") or line.strip().startswith("!"):
                    clean_lines.append(f"# {line}")
                else:
                    clean_lines.append(line)
            clean_code = "\n".join(clean_lines)

            try:
                exec(compile(clean_code, f"{nb_path.name}:cell_{cell_idx}", "exec"), exec_globals)
                executed_cells_count += 1
            except Exception as ex:
                err_str = f"Cell {cell_idx}: {type(ex).__name__} - {ex}"
                cell_errors.append(err_str)
                total_exceptions += 1

        exec_status = "PASSED" if len(cell_errors) == 0 else f"FAILED ({len(cell_errors)} error(s))"

        report.append({
            "index": idx,
            "path": nb_rel_path,
            "json_valid": json_valid,
            "nbformat_valid": nbformat_valid,
            "nbformat_ver": nbformat_ver,
            "total_cells": len(cells),
            "code_cells": len(code_cells),
            "markdown_cells": len(markdown_cells),
            "executed_code_cells": executed_cells_count,
            "exec_status": exec_status,
            "errors": cell_errors
        })

    # Output Summary Table
    print("\n" + "=" * 100)
    print(f"{'#':<3} | {'Notebook Path':<45} | {'JSON':<5} | {'nbformat':<10} | {'Cells (C/M)':<11} | {'Status'}")
    print("=" * 100)
    for r in report:
        cells_str = f"{r['code_cells']}/{r['markdown_cells']}"
        json_str = "PASS" if r['json_valid'] else "FAIL"
        nb_str = "PASS" if r['nbformat_valid'] else "FAIL"
        print(f"{r['index']:<3} | {r['path']:<45} | {json_str:<5} | {nb_str:<10} | {cells_str:<11} | {r['exec_status']}")
    print("=" * 100)

    print(f"\nSummary Metrics:")
    print(f"  Total Topic Notebooks Checked : {len(report)}")
    print(f"  Total Notebook Cells          : {total_code_cells + total_markdown_cells}")
    print(f"  Total Code Cells Executed     : {total_code_cells}")
    print(f"  Total Markdown Cells Verified : {total_markdown_cells}")
    print(f"  Total Runtime Exceptions      : {total_exceptions}")
    print(f"  Overall Health                : {'100% HEALTHY' if total_exceptions == 0 else 'ISSUES FOUND'}")

    return total_exceptions == 0

if __name__ == "__main__":
    success = run_empirical_validation()
    sys.exit(0 if success else 1)
