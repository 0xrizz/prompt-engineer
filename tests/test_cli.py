import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.bin = self.root / "bin" / "prompt-eng"

    def run_cli(self, args, env=None):
        cli_env = os.environ.copy()
        if env:
            cli_env.update(env)
        return subprocess.run(
            [sys.executable, str(self.bin)] + args,
            capture_output=True,
            text=True,
            env=cli_env,
            check=False,
        )

    def test_help_command(self):
        res = self.run_cli(["--help"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("scan", res.stdout)
        self.assertIn("transcript", res.stdout)
        self.assertIn("score", res.stdout)
        self.assertIn("diff", res.stdout)
        self.assertIn("list", res.stdout)
        self.assertIn("search", res.stdout)
        self.assertIn("save-prompt", res.stdout)

    def test_no_args_prints_help(self):
        res = self.run_cli([])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Centralized Prompt Engineering Studio", res.stdout)

    def test_score_command_text(self):
        res = self.run_cli(["score", "Write a python unit test for auth middleware"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Clarity", res.stdout)
        self.assertIn("Overall", res.stdout)

    def test_score_command_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Role: Senior Dev\nTask: Build unit test\nFormat: Python unittest")
            f_path = f.name
        try:
            res = self.run_cli(["score", "--file", f_path])
            self.assertEqual(res.returncode, 0)
            self.assertIn("Clarity", res.stdout)
            self.assertIn("Overall", res.stdout)
        finally:
            if Path(f_path).exists():
                Path(f_path).unlink()

    def test_score_command_missing_input(self):
        res = self.run_cli(["score"])
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: Must provide prompt text or --file", res.stderr)

    def test_list_command(self):
        res = self.run_cli(["list"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Tracked Repositories", res.stdout)

    def test_diff_command(self):
        res = self.run_cli(["diff", "Hello world", "Hello brave new world"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Original Prompt", res.stdout)
        self.assertIn("Optimized Prompt", res.stdout)

    def test_save_prompt_and_search_command(self):
        test_repo_dir = self.root / "repos" / "test-repo"
        try:
            # Run save-prompt with content
            res_save = self.run_cli(
                [
                    "save-prompt",
                    "--repo",
                    "test-repo",
                    "--name",
                    "auth-test",
                    "--framework",
                    "RISEN",
                    "--content",
                    "Role: Tester\nTask: Validate authentication token handling\nSteps: Test invalid tokens",
                ]
            )
            self.assertEqual(res_save.returncode, 0)
            self.assertIn("Saved engineered prompt", res_save.stdout)

            # Verify search finds it
            res_search = self.run_cli(["search", "authentication"])
            self.assertEqual(res_search.returncode, 0)
            self.assertIn("test-repo", res_search.stdout)
            self.assertIn("auth-test.md", res_search.stdout)
        finally:
            # Cleanup created files in repos/test-repo
            if test_repo_dir.exists():
                import shutil

                shutil.rmtree(test_repo_dir)

    def test_transcript_command_with_file(self):
        fixture = self.root / "tests" / "fixtures" / "antigravity_sample.jsonl"
        res = self.run_cli(["transcript", "--repo", "sample-repo", "--file", str(fixture)])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Session Context Summary", res.stdout)
        self.assertIn("sample-repo", res.stdout)

    def test_transcript_command_json_format(self):
        fixture = self.root / "tests" / "fixtures" / "antigravity_sample.jsonl"
        res = self.run_cli(
            ["transcript", "--repo", "sample-repo", "--file", str(fixture), "--format", "json"]
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["repo_name"], "sample-repo")
        self.assertEqual(data["harness"], "antigravity")
        self.assertIn("Fix the failing test", data["user_goal"])

    def test_scan_single_repo_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_repo = Path(tmp_dir) / "cli-sample"
            sample_repo.mkdir()
            (sample_repo / "pyproject.toml").write_text(
                '[project]\nname = "cli-sample"\n', encoding="utf-8"
            )
            out_repos = Path(tmp_dir) / "repos"

            # Test scanning by path
            res = self.run_cli(["scan", str(sample_repo), "--output", str(out_repos)])
            self.assertEqual(res.returncode, 0)
            self.assertIn("cli-sample", res.stdout)
            self.assertTrue((out_repos / "cli-sample" / "profile.yaml").exists())

            # Test scanning by --repo flag
            res_flag = self.run_cli(
                ["scan", "--repo", str(sample_repo), "--output", str(out_repos)]
            )
            self.assertEqual(res_flag.returncode, 0)
            self.assertIn("cli-sample", res_flag.stdout)

    def test_scan_single_repo_not_found(self):
        res = self.run_cli(["scan", "/nonexistent/repo/path/xyz"])
        self.assertEqual(res.returncode, 1)
        self.assertIn("Target repository directory not found", res.stderr)

    def test_cli_scaffold_stdout(self):
        res = self.run_cli(
            [
                "scaffold",
                "--repo",
                "sample-repo",
                "--name",
                "test-p",
                "--framework",
                "RISEN",
                "--stdout",
            ]
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("## Role", res.stdout)
        self.assertIn("## Steps", res.stdout)

    def test_cli_lint_clean_and_strict(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(
                "## Role\nEng\n## Input\nIn\n## Steps\n1. Go\n## Expectation\nPass\n## Narrowing\nNone\n"
            )
            f_path = f.name
        try:
            res = self.run_cli(["lint", f_path, "--repo", "cli-sample"])
            self.assertEqual(res.returncode, 0)
            self.assertIn("✓ Lint passed", res.stdout)
        finally:
            Path(f_path).unlink()

    def test_cli_search_json(self):
        res = self.run_cli(["search", "", "--json"])
        self.assertEqual(res.returncode, 0)
        self.assertTrue(res.stdout.strip().startswith("[") or res.stdout.strip().startswith("{"))


if __name__ == "__main__":
    unittest.main()
