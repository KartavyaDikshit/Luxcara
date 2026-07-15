#!/usr/bin/env python3
import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path
import subprocess

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

def step1_json_and_nbformat():
    print("=== STEP 1: JSON Syntax & NBFormat Structure Validation ===")
    all_valid = True
    notebook_count = 0
    errors = []

    for topic_dir in TOPIC_DIRECTORIES:
        dir_path = PROJECT_ROOT / topic_dir
        if not dir_path.is_dir():
            print(f"ERROR: Topic directory missing: {topic_dir}")
            all_valid = False
            continue
        
        for nb_path in sorted(dir_path.glob("*.ipynb")):
            notebook_count += 1
            rel_path = nb_path.relative_to(PROJECT_ROOT)
            try:
                with open(nb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"❌ FAIL JSON Decode: {rel_path} -> {e}")
                errors.append((str(rel_path), f"JSON Error: {e}"))
                all_valid = False
                continue

            # nbformat validation checks
            if not isinstance(data, dict):
                print(f"❌ FAIL Schema: {rel_path} root is not a dict")
                errors.append((str(rel_path), "Root is not JSON object"))
                all_valid = False
                continue

            if "cells" not in data or not isinstance(data["cells"], list):
                print(f"❌ FAIL Schema: {rel_path} missing or invalid 'cells'")
                errors.append((str(rel_path), "Missing or non-list 'cells'"))
                all_valid = False

            if "nbformat" not in data or not isinstance(data["nbformat"], int):
                print(f"❌ FAIL Schema: {rel_path} missing or invalid 'nbformat'")
                errors.append((str(rel_path), "Missing or invalid 'nbformat' integer"))
                all_valid = False

            if "metadata" not in data or not isinstance(data["metadata"], dict):
                print(f"❌ FAIL Schema: {rel_path} missing or invalid 'metadata'")
                errors.append((str(rel_path), "Missing or non-dict 'metadata'"))
                all_valid = False

            # Check individual cells
            cell_issues = 0
            for idx, cell in enumerate(data.get("cells", [])):
                if not isinstance(cell, dict):
                    cell_issues += 1
                    continue
                if "cell_type" not in cell or cell["cell_type"] not in ["code", "markdown", "raw"]:
                    cell_issues += 1
                if "source" not in cell:
                    cell_issues += 1

            if cell_issues > 0:
                print(f"❌ FAIL Schema: {rel_path} has {cell_issues} malformed cells")
                errors.append((str(rel_path), f"{cell_issues} malformed cells"))
                all_valid = False
            else:
                print(f"✓ PASS: {rel_path} (cells: {len(data.get('cells', []))}, nbformat: v{data.get('nbformat')})")

    print(f"\nStep 1 Completed: Verified {notebook_count} notebooks. Errors found: {len(errors)}\n")
    return all_valid, errors, notebook_count


def step2_execute_notebook_code():
    print("=== STEP 2: Notebook Code Cells Execution Runner ===")
    executed_count = 0
    failed_notebooks = []

    for topic_dir in TOPIC_DIRECTORIES:
        dir_path = PROJECT_ROOT / topic_dir
        for nb_path in sorted(dir_path.glob("*.ipynb")):
            executed_count += 1
            rel_path = nb_path.relative_to(PROJECT_ROOT)
            print(f"\nExecuting notebook [{executed_count}]: {rel_path}")
            
            with open(nb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Global namespace for notebook execution
            nb_globals = {"__name__": "__main__", "__file__": str(nb_path)}
            
            code_cell_index = 0
            cell_errors = []
            
            for idx, cell in enumerate(data.get("cells", [])):
                if cell.get("cell_type") == "code":
                    code_cell_index += 1
                    source = cell.get("source", "")
                    if isinstance(source, list):
                        code = "".join(source)
                    else:
                        code = str(source)
                    
                    if not code.strip():
                        continue

                    # Filter out ipython shell magics if any (e.g. !pip or %matplotlib) or transform them
                    clean_lines = []
                    for line in code.splitlines():
                        stripped = line.strip()
                        if stripped.startswith("!") or stripped.startswith("%"):
                            clean_lines.append(f"# {line}")  # comment magic
                        else:
                            clean_lines.append(line)
                    executable_code = "\n".join(clean_lines)

                    try:
                        exec(executable_code, nb_globals)
                    except Exception as e:
                        tb = traceback.format_exc()
                        print(f"  ❌ Cell {idx+1} (Code Cell #{code_cell_index}) ERROR: {type(e).__name__}: {e}")
                        cell_errors.append({
                            "cell_index": idx + 1,
                            "code_index": code_cell_index,
                            "error": str(e),
                            "traceback": tb
                        })

            if cell_errors:
                failed_notebooks.append((str(rel_path), cell_errors))
                print(f"  ❌ Notebook {rel_path} failed with {len(cell_errors)} code cell error(s)")
            else:
                print(f"  ✓ Notebook {rel_path} executed cleanly (evaluated {code_cell_index} code cells)")

    print(f"\nStep 2 Completed: Executed {executed_count} notebooks. Failed notebooks: {len(failed_notebooks)}\n")
    return len(failed_notebooks) == 0, failed_notebooks


def step3_verify_project_edge_cases():
    print("=== STEP 3: Edge Case Testing for verify_project.py ===")
    results = []

    # 1. Normal run
    res = subprocess.run([sys.executable, str(PROJECT_ROOT / "verify_project.py")], capture_output=True, text=True)
    results.append(("Normal project state", res.returncode == 0, res.returncode, res.stdout, res.stderr))
    print(f"1. Normal run: exit code {res.returncode} (expected 0) -> {'PASS' if res.returncode == 0 else 'FAIL'}")

    # 2. Extra non-ipynb files in topic directory (e.g. README.md, extra python file, hidden file)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        # Add extra files in topic 1
        (tmp_root / "1_RAG_Mastery" / "notes.txt").write_text("extra text file")
        (tmp_root / "1_RAG_Mastery" / "extra_script.py").write_text("print('hello')")
        (tmp_root / "1_RAG_Mastery" / ".hidden_file").write_text("hidden")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Extra non-ipynb files in topic dir", res.returncode == 0, res.returncode, res.stdout, res.stderr))
        print(f"2. Extra non-ipynb files: exit code {res.returncode} (expected 0) -> {'PASS' if res.returncode == 0 else 'FAIL'}")

    # 3. Extra directory / extra files at root
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        (tmp_root / "8_Extra_Topic").mkdir()
        (tmp_root / "extra_file.txt").write_text("extra")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Extra top-level directory/file", res.returncode == 0, res.returncode, res.stdout, res.stderr))
        print(f"3. Extra root dir/file: exit code {res.returncode} (expected 0) -> {'PASS' if res.returncode == 0 else 'FAIL'}")

    # 4. Missing required directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        shutil.rmtree(tmp_root / "1_RAG_Mastery")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Missing required directory", res.returncode == 1, res.returncode, res.stdout, res.stderr))
        print(f"4. Missing directory: exit code {res.returncode} (expected 1) -> {'PASS' if res.returncode == 1 else 'FAIL'}")

    # 5. Path exists but is a file instead of a directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        shutil.rmtree(tmp_root / "2_LLM_API")
        (tmp_root / "2_LLM_API").write_text("not a dir")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Directory path is a file", res.returncode == 1, res.returncode, res.stdout, res.stderr))
        print(f"5. Directory replaced by file: exit code {res.returncode} (expected 1) -> {'PASS' if res.returncode == 1 else 'FAIL'}")

    # 6. Topic directory contains 0 .ipynb files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        for f in (tmp_root / "3_Prompt_Engineering").glob("*.ipynb"):
            f.unlink()
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Directory with 0 .ipynb files", res.returncode == 1, res.returncode, res.stdout, res.stderr))
        print(f"6. 0 notebooks in topic dir: exit code {res.returncode} (expected 1) -> {'PASS' if res.returncode == 1 else 'FAIL'}")

    # 7. Notebook with syntax corrupt JSON
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        (tmp_root / "4_Agents" / "corrupt.ipynb").write_text("{ invalid json ...")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Corrupt JSON notebook", res.returncode == 1, res.returncode, res.stdout, res.stderr))
        print(f"7. Syntax corrupt JSON: exit code {res.returncode} (expected 1) -> {'PASS' if res.returncode == 1 else 'FAIL'}")

    # 8. Notebook with root JSON element as array instead of object
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "ai_concepts_demo"
        shutil.copytree(PROJECT_ROOT, tmp_root, ignore=shutil.ignore_patterns(".agents", ".git", ".pytest_cache"))
        
        (tmp_root / "5_Risk_Evaluation" / "array_root.ipynb").write_text("[1, 2, 3]")
        
        res = subprocess.run([sys.executable, str(tmp_root / "verify_project.py")], capture_output=True, text=True)
        results.append(("Array root JSON notebook", res.returncode == 1, res.returncode, res.stdout, res.stderr))
        print(f"8. Array root JSON notebook: exit code {res.returncode} (expected 1) -> {'PASS' if res.returncode == 1 else 'FAIL'}")

    print("\nStep 3 Completed.\n")
    return results


def step4_run_e2e_tests():
    print("=== STEP 4: Running run_e2e_tests.py ===")
    res = subprocess.run([sys.executable, str(PROJECT_ROOT / "run_e2e_tests.py")], capture_output=True, text=True)
    print(f"Exit code: {res.returncode}")
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)
    return res.returncode == 0, res.stdout, res.stderr


if __name__ == "__main__":
    s1_pass, s1_errs, nb_count = step1_json_and_nbformat()
    s2_pass, s2_errs = step2_execute_notebook_code()
    s3_results = step3_verify_project_edge_cases()
    s4_pass, s4_out, s4_err = step4_run_e2e_tests()

    summary_file = Path("/Users/kartavyadikshit/teamwork_projects/ai_concepts_demo/.agents/challenger_2/empirical_results.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "step1_valid": s1_pass,
            "step1_notebook_count": nb_count,
            "step1_errors": s1_errs,
            "step2_valid": s2_pass,
            "step2_failures": s2_errs,
            "step3_results": [(t[0], t[1], t[2]) for t in s3_results],
            "step4_passed": s4_pass,
            "step4_stdout": s4_out,
            "step4_stderr": s4_err,
        }, f, indent=2)
    print(f"Empirical test execution finished. Results saved to {summary_file}")
