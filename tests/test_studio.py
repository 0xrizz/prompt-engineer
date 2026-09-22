"""Tests for Studio Suite utilities (Scorer, Diff, and Catalog)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from prompt_eng.models import dump_frontmatter_markdown
from prompt_eng.studio.catalog import query_prompt_catalog
from prompt_eng.studio.diff import compare_prompt_diff
from prompt_eng.studio.scorer import evaluate_rubric, render_rubric_table


class TestStudio(unittest.TestCase):
    def test_rubric_evaluator(self) -> None:
        vague_prompt = "do the thing"
        score = evaluate_rubric(vague_prompt)
        self.assertLessEqual(score.overall, 5.0)

        structured_prompt = """
        Role: Expert Python Engineer
        Task: Refactor auth handler
        Context: Using fastapi 0.110 in 0x-arbiter
        Format: Return only python code block with unit test
        Constraints: Do not modify existing db schemas
        """
        good_score = evaluate_rubric(structured_prompt)
        self.assertGreaterEqual(good_score.overall, 7.0)
        table = render_rubric_table(good_score)
        self.assertIn("Clarity", table)
        self.assertIn("Overall", table)

    def test_diff_engine(self) -> None:
        before = "Write tests"
        after = "Write tests for auth handler using pytest"
        diff_output = compare_prompt_diff(before, after)
        self.assertIn("Write tests", diff_output)
        self.assertIn("auth handler", diff_output)

    def test_catalog_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repos_dir = Path(tmp)
            p_dir = repos_dir / "0x-arbiter" / "prompts"
            p_dir.mkdir(parents=True)
            content = dump_frontmatter_markdown(
                {"framework": "RISEN", "target": "eval"}, "Write benchmark"
            )
            (p_dir / "eval-benchmark.md").write_text(content, encoding="utf-8")

            results = query_prompt_catalog(repos_dir, "benchmark")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["repo"], "0x-arbiter")

    def test_catalog_query_edge_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repos_dir = Path(tmp)
            # Empty repos directory
            self.assertEqual(query_prompt_catalog(repos_dir, "test"), [])
            # Non-existent directory
            self.assertEqual(query_prompt_catalog(repos_dir / "missing", "test"), [])

            # Repo with score dictionary in frontmatter
            p_dir = repos_dir / "backend-core" / "prompts"
            p_dir.mkdir(parents=True)
            scored_content = dump_frontmatter_markdown(
                {"framework": "CO-STAR", "score": {"overall": 8.5}},
                "Implement database connection pool with healthcheck",
            )
            (p_dir / "db-pool.md").write_text(scored_content, encoding="utf-8")

            # Corrupted markdown file
            (p_dir / "corrupted.md").write_bytes(b"\x80\x81\x82 invalid binary")

            # Query all with empty string
            all_results = query_prompt_catalog(repos_dir, "")
            self.assertGreaterEqual(len(all_results), 1)
            matched = next(r for r in all_results if r["file"] == "db-pool.md")
            self.assertEqual(matched["framework"], "CO-STAR")
            self.assertEqual(matched["overall_score"], 8.5)


if __name__ == "__main__":
    unittest.main()
