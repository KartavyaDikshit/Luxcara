#!/usr/bin/env python3
"""
AI Concepts Interactive Demo — Root Project Verifier
Verifies that required topic directories exist, contain at least one Jupyter Notebook (.ipynb),
and that all notebook files parse cleanly as valid JSON.
"""

import json
import sys
from pathlib import Path

REQUIRED_DIRECTORIES = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough",
]


def verify_project(root_path: Path) -> bool:
    """
    Scans root_path for required topic directories and valid .ipynb files.
    Returns True if all requirements pass, False otherwise.
    """
    print("=" * 65)
    print("AI Concepts Interactive Demo — Project Structure Verification")
    print("=" * 65)

    all_passed = True
    summary_results = []
    total_notebooks_checked = 0
    total_invalid_notebooks = 0

    for idx, dir_name in enumerate(REQUIRED_DIRECTORIES, 1):
        target_dir = root_path / dir_name
        print(f"\n[{idx}/7] Checking topic directory: '{dir_name}'")

        if not target_dir.exists():
            print(f"  ❌ FAIL: Directory '{dir_name}' does not exist.")
            all_passed = False
            summary_results.append((dir_name, "MISSING", 0, []))
            continue

        if not target_dir.is_dir():
            print(f"  ❌ FAIL: Path '{dir_name}' exists but is not a directory.")
            all_passed = False
            summary_results.append((dir_name, "NOT_A_DIRECTORY", 0, []))
            continue

        ipynb_files = sorted(list(target_dir.glob("*.ipynb")))
        notebook_count = len(ipynb_files)

        if notebook_count == 0:
            print(f"  ❌ FAIL: No .ipynb notebook files found in '{dir_name}'.")
            all_passed = False
            summary_results.append((dir_name, "NO_NOTEBOOKS", 0, []))
            continue

        invalid_files = []
        for nb_file in ipynb_files:
            total_notebooks_checked += 1
            rel_nb_path = nb_file.relative_to(root_path)
            try:
                with open(nb_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if not isinstance(data, dict):
                    print(
                        f"  ❌ INVALID JSON CONTENT: '{rel_nb_path}' root element is not a JSON object."
                    )
                    invalid_files.append((nb_file.name, "Root element is not JSON object"))
                    total_invalid_notebooks += 1
                    all_passed = False
                else:
                    print(f"  ✓ PASS: '{rel_nb_path}' (valid JSON)")
            except json.JSONDecodeError as err:
                print(
                    f"  ❌ INVALID JSON: '{rel_nb_path}' failed to parse: {err}"
                )
                invalid_files.append((nb_file.name, str(err)))
                total_invalid_notebooks += 1
                all_passed = False
            except Exception as err:
                print(f"  ❌ FILE READ ERROR: '{rel_nb_path}': {err}")
                invalid_files.append((nb_file.name, str(err)))
                total_invalid_notebooks += 1
                all_passed = False

        if len(invalid_files) == 0:
            summary_results.append(
                (dir_name, "OK", notebook_count, ipynb_files)
            )
        else:
            summary_results.append(
                (dir_name, "INVALID_NOTEBOOKS", notebook_count, invalid_files)
            )

    print("\n" + "=" * 65)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 65)
    for dir_name, status, count, details in summary_results:
        if status == "OK":
            print(f"  ✓ {dir_name}: OK ({count} notebook(s) verified)")
        elif status == "MISSING":
            print(f"  ❌ {dir_name}: Directory missing")
        elif status == "NOT_A_DIRECTORY":
            print(f"  ❌ {dir_name}: Not a directory")
        elif status == "NO_NOTEBOOKS":
            print(f"  ❌ {dir_name}: Directory contains 0 .ipynb files")
        elif status == "INVALID_NOTEBOOKS":
            print(
                f"  ❌ {dir_name}: Contains invalid JSON notebook(s) ({len(details)}/{count} failed)"
            )

    print("-" * 65)
    print(f"Total Required Directories Verified: {sum(1 for _, st, _, _ in summary_results if st == 'OK')}/{len(REQUIRED_DIRECTORIES)}")
    print(f"Total Notebook Files Checked: {total_notebooks_checked}")
    print(f"Total Invalid Notebook Files: {total_invalid_notebooks}")
    print(f"Overall Status: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 65)

    return all_passed


def main():
    root_path = Path(__file__).resolve().parent
    success = verify_project(root_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
