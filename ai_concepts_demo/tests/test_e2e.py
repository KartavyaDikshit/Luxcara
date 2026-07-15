"""Comprehensive End-to-End Test Suite for AI Concepts Interactive Demo."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOPIC_DIRECTORIES = [
    "1_RAG_Mastery",
    "2_LLM_API",
    "3_Prompt_Engineering",
    "4_Agents",
    "5_Risk_Evaluation",
    "6_German_Language",
    "7_Legal_Walkthrough",
]


class TestTier1DirectoryScaffolding(unittest.TestCase):
    """Tier 1: Directory scaffolding test - checks existence of all 7 topic directories."""

    def test_topic_directories_exist(self):
        for topic_dir in TOPIC_DIRECTORIES:
            dir_path = PROJECT_ROOT / topic_dir
            with self.subTest(topic_dir=topic_dir):
                self.assertTrue(
                    dir_path.exists(),
                    f"Directory '{topic_dir}' does not exist at project root: {dir_path}",
                )
                self.assertTrue(
                    dir_path.is_dir(),
                    f"Path '{topic_dir}' exists but is not a directory: {dir_path}",
                )


class TestTier2NotebookValidity(unittest.TestCase):
    """Tier 2: Notebook validity test - checks presence and JSON/nbformat validity of .ipynb files."""

    def test_notebooks_exist_and_valid_json(self):
        for topic_dir in TOPIC_DIRECTORIES:
            dir_path = PROJECT_ROOT / topic_dir
            if not dir_path.is_dir():
                self.fail(f"Topic directory '{topic_dir}' missing for notebook validity test.")

            notebook_files = list(dir_path.glob("*.ipynb"))
            with self.subTest(topic_dir=topic_dir):
                self.assertGreater(
                    len(notebook_files),
                    0,
                    f"Topic directory '{topic_dir}' contains no .ipynb notebook files.",
                )

            for nb_path in notebook_files:
                with self.subTest(notebook=nb_path.name):
                    self.assertTrue(nb_path.is_file(), f"{nb_path} is not a file.")
                    try:
                        with open(nb_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except json.JSONDecodeError as err:
                        self.fail(
                            f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' is not valid JSON: {err}"
                        )

                    self.assertIsInstance(
                        data,
                        dict,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' JSON root is not an object.",
                    )
                    self.assertIn(
                        "cells",
                        data,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' missing 'cells' key.",
                    )
                    self.assertIsInstance(
                        data["cells"],
                        list,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' 'cells' is not a list.",
                    )
                    self.assertIn(
                        "nbformat",
                        data,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' missing 'nbformat' key.",
                    )


class TestTier3NotebookContentVerification(unittest.TestCase):
    """Tier 3: Notebook content verification test - checks markdown theory & python code cells."""

    def test_notebook_content_structure(self):
        for topic_dir in TOPIC_DIRECTORIES:
            dir_path = PROJECT_ROOT / topic_dir
            if not dir_path.is_dir():
                self.fail(
                    f"Topic directory '{topic_dir}' missing for notebook content verification."
                )

            notebook_files = list(dir_path.glob("*.ipynb"))
            if not notebook_files:
                self.fail(f"Topic directory '{topic_dir}' contains no .ipynb files.")

            for nb_path in notebook_files:
                with self.subTest(notebook=nb_path.name):
                    with open(nb_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    cells = data.get("cells", [])
                    has_markdown = False
                    has_code = False

                    for cell in cells:
                        cell_type = cell.get("cell_type")
                        source = cell.get("source", "")
                        if isinstance(source, list):
                            source_str = "".join(source)
                        else:
                            source_str = str(source)

                        if cell_type == "markdown" and source_str.strip():
                            has_markdown = True
                        elif cell_type == "code" and source_str.strip():
                            has_code = True

                    self.assertTrue(
                        has_markdown,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' does not contain any markdown explanation (theory) cells.",
                    )
                    self.assertTrue(
                        has_code,
                        f"Notebook '{nb_path.relative_to(PROJECT_ROOT)}' does not contain any executable python code cells.",
                    )


class TestTier4ScaffoldingVerifier(unittest.TestCase):
    """Tier 4: Scaffolding verifier test - executes python verify_project.py."""

    def test_verify_project_execution(self):
        verifier_script = PROJECT_ROOT / "verify_project.py"
        self.assertTrue(
            verifier_script.is_file(),
            f"Script 'verify_project.py' not found at project root: {verifier_script}",
        )

        res = subprocess.run(
            [sys.executable, str(verifier_script)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )

        self.assertEqual(
            res.returncode,
            0,
            f"verify_project.py failed with returncode {res.returncode}.\nStderr: {res.stderr}\nStdout: {res.stdout}",
        )
        self.assertTrue(
            "passed" in res.stdout.lower() or "success" in res.stdout.lower(),
            f"verify_project.py stdout did not report success or passed status.\nStdout: {res.stdout}",
        )


if __name__ == "__main__":
    unittest.main()
