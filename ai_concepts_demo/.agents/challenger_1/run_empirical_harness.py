#!/usr/bin/env python3
import json
import os
import shutil
import sys
import tempfile
import traceback
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TOPIC_DIRECTORIES = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough",
]

def run_task1_nbformat_validation():
    print("=== TASK 1: JSON Syntax & NBFormat Structure Validation ===")
    all_notebooks = list(PROJECT_ROOT.glob("*/*.ipynb"))
    print(f"Found {len(all_notebooks)} notebooks across all topic directories.")
    
    results = {}
    for nb in sorted(all_notebooks):
        rel_path = nb.relative_to(PROJECT_ROOT)
        status = {"json_valid": False, "nbformat_keys": False, "cell_structure_valid": False, "issues": []}
        try:
            with open(nb, "r", encoding="utf-8") as f:
                data = json.load(f)
            status["json_valid"] = True
            
            if not isinstance(data, dict):
                status["issues"].append("JSON root is not dict")
            else:
                nbformat = data.get("nbformat")
                nbformat_minor = data.get("nbformat_minor")
                cells = data.get("cells")
                metadata = data.get("metadata")
                
                if nbformat is None or not isinstance(nbformat, int):
                    status["issues"].append(f"Invalid nbformat: {nbformat}")
                if nbformat_minor is None or not isinstance(nbformat_minor, int):
                    status["issues"].append(f"Invalid nbformat_minor: {nbformat_minor}")
                if metadata is None or not isinstance(metadata, dict):
                    status["issues"].append("Missing or invalid metadata dict")
                if cells is None or not isinstance(cells, list):
                    status["issues"].append("Missing or invalid cells list")
                else:
                    status["nbformat_keys"] = len(status["issues"]) == 0
                    
                    # Validate each cell structure
                    cell_errors = []
                    for idx, cell in enumerate(cells):
                        if not isinstance(cell, dict):
                            cell_errors.append(f"Cell {idx} is not dict")
                            continue
                        c_type = cell.get("cell_type")
                        if c_type not in ["markdown", "code", "raw"]:
                            cell_errors.append(f"Cell {idx} unknown cell_type '{c_type}'")
                        if "source" not in cell:
                            cell_errors.append(f"Cell {idx} missing 'source'")
                        if c_type == "code":
                            if "outputs" not in cell or not isinstance(cell.get("outputs"), list):
                                cell_errors.append(f"Cell {idx} (code) missing valid 'outputs' list")
                            if "execution_count" not in cell:
                                cell_errors.append(f"Cell {idx} (code) missing 'execution_count'")
                    if cell_errors:
                        status["issues"].extend(cell_errors)
                    else:
                        status["cell_structure_valid"] = True
        except Exception as e:
            status["issues"].append(f"JSON load error: {e}")
            
        results[str(rel_path)] = status
        print(f"  {rel_path}: JSON={status['json_valid']} NBKeys={status['nbformat_keys']} CellsValid={status['cell_structure_valid']}")
        if status["issues"]:
            print(f"    Issues: {status['issues']}")
    return results

def run_task2_dynamic_code_execution():
    print("\n=== TASK 2: Dynamic Execution of All Code Cells Across Notebooks ===")
    all_notebooks = list(PROJECT_ROOT.glob("*/*.ipynb"))
    
    execution_summary = {}
    
    for nb in sorted(all_notebooks):
        rel_path = str(nb.relative_to(PROJECT_ROOT))
        with open(nb, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        code_cells = []
        cells = data.get("cells", [])
        for idx, cell in enumerate(cells):
            if cell.get("cell_type") == "code":
                src = cell.get("source", "")
                if isinstance(src, list):
                    src_str = "".join(src)
                else:
                    src_str = str(src)
                if src_str.strip():
                    code_cells.append((idx, src_str))
                    
        print(f"\nNotebook: {rel_path} — Found {len(code_cells)} executable code cells out of {len(cells)} total cells.")
        
        cell_results = []
        # Create a clean global namespace for executing notebook code cells in sequence
        exec_globals = {"__name__": "__main__"}
        
        for c_idx, code_str in code_cells:
            try:
                # Compile first to catch syntax errors cleanly
                compiled_code = compile(code_str, filename=f"{rel_path}_cell_{c_idx}", mode="exec")
                exec(compiled_code, exec_globals)
                cell_results.append({"cell_index": c_idx, "status": "PASS", "error": None})
                print(f"  ✓ Cell {c_idx}: PASS")
            except Exception as err:
                tb_str = traceback.format_exc()
                cell_results.append({"cell_index": c_idx, "status": "FAIL", "error": str(err), "traceback": tb_str})
                print(f"  ❌ Cell {c_idx}: FAIL - {type(err).__name__}: {err}")
                
        execution_summary[rel_path] = {
            "total_cells": len(cells),
            "code_cells_count": len(code_cells),
            "executed": len(cell_results),
            "failures": [r for r in cell_results if r["status"] == "FAIL"]
        }
        
    return execution_summary

def run_task3_verify_project_edge_cases():
    print("\n=== TASK 3: Edge Case Testing of verify_project.py ===")
    from verify_project import verify_project, REQUIRED_DIRECTORIES
    
    edge_cases_results = []
    
    # Test Case 3.1: Standard run on real PROJECT_ROOT
    res_nominal = verify_project(PROJECT_ROOT)
    edge_cases_results.append(("Nominal project root", res_nominal, True))
    
    # Test Case 3.2: Extra files/directories in root and topic dirs
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Recreate valid structure
        for d in REQUIRED_DIRECTORIES:
            (tmp_path / d).mkdir()
            (tmp_path / d / "demo.ipynb").write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}')
            
        # Add extra file in topic dir
        (tmp_path / "1_RAG_Mastery" / "extra_notes.txt").write_text("Extra file content")
        (tmp_path / "1_RAG_Mastery" / "another_notebook.ipynb").write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}')
        # Add extra unrequired directory
        (tmp_path / "8_Extra_Topic").mkdir()
        (tmp_path / "8_Extra_Topic" / "extra.ipynb").write_text('{"cells": []}')
        
        res_extra = verify_project(tmp_path)
        edge_cases_results.append(("Valid structure + extra non-ipynb files & extra topic dir", res_extra, True))

    # Test Case 3.3: Missing required directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for d in REQUIRED_DIRECTORIES[:-1]: # leave out 7_Legal_Walkthrough
            (tmp_path / d).mkdir()
            (tmp_path / d / "demo.ipynb").write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}')
        res_missing = verify_project(tmp_path)
        edge_cases_results.append(("Missing topic directory", res_missing, False))

    # Test Case 3.4: Topic directory replaced by a plain file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for d in REQUIRED_DIRECTORIES[:-1]:
            (tmp_path / d).mkdir()
            (tmp_path / d / "demo.ipynb").write_text('{}')
        (tmp_path / REQUIRED_DIRECTORIES[-1]).write_text("I am a file, not a directory")
        res_not_a_dir = verify_project(tmp_path)
        edge_cases_results.append(("Topic directory is a file", res_not_a_dir, False))

    # Test Case 3.5: Empty topic directory (0 notebooks)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for d in REQUIRED_DIRECTORIES:
            (tmp_path / d).mkdir()
        # leave 1_RAG_Mastery empty
        for d in REQUIRED_DIRECTORIES[1:]:
            (tmp_path / d / "demo.ipynb").write_text('{}')
        res_empty_dir = verify_project(tmp_path)
        edge_cases_results.append(("Empty topic directory (0 .ipynb)", res_empty_dir, False))

    # Test Case 3.6: Invalid JSON content (corrupt syntax)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for d in REQUIRED_DIRECTORIES:
            (tmp_path / d).mkdir()
            (tmp_path / d / "demo.ipynb").write_text('{"cells": [} INVALID JSON')
        res_corrupt_json = verify_project(tmp_path)
        edge_cases_results.append(("Corrupt JSON file", res_corrupt_json, False))

    # Test Case 3.7: JSON root element is list instead of dict
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for d in REQUIRED_DIRECTORIES:
            (tmp_path / d).mkdir()
            (tmp_path / d / "demo.ipynb").write_text('[1, 2, 3]')
        res_list_root = verify_project(tmp_path)
        edge_cases_results.append(("JSON root is list, not dict", res_list_root, False))

    print("\nSummary of Edge Case Tests on verify_project.py:")
    for desc, actual, expected in edge_cases_results:
        status_symbol = "✓ PASS" if actual == expected else "❌ FAIL"
        print(f"  {status_symbol} - {desc}: Got exit return boolean {actual} (Expected: {expected})")
        
    return edge_cases_results

def run_task4_e2e_runner():
    print("\n=== TASK 4: Run E2E Test Runner ===")
    res = subprocess.run([sys.executable, "run_e2e_tests.py"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    print(f"Return code: {res.returncode}")
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
    return res

if __name__ == "__main__":
    t1 = run_task1_nbformat_validation()
    t2 = run_task2_dynamic_code_execution()
    t3 = run_task3_verify_project_edge_cases()
    t4 = run_task4_e2e_runner()
