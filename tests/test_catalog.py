import tempfile
import unittest
from pathlib import Path

from prompt_eng.models import dump_frontmatter_markdown
from prompt_eng.studio.catalog import query_prompt_catalog


class TestCatalogSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repos_dir = Path(self.tmp.name)

        # Setup Repo A
        (self.repos_dir / "repo-a" / "prompts").mkdir(parents=True)
        meta_a1 = {"name": "p1", "framework": "RISEN", "score": {"overall": 8.5}}
        meta_a2 = {"name": "p2", "framework": "CO-STAR", "score": {"overall": 6.0}}
        (self.repos_dir / "repo-a" / "prompts" / "p1.md").write_text(
            dump_frontmatter_markdown(meta_a1, "Execute authentication tests"),
            encoding="utf-8",
        )
        (self.repos_dir / "repo-a" / "prompts" / "p2.md").write_text(
            dump_frontmatter_markdown(meta_a2, "Create marketing promo copy"),
            encoding="utf-8",
        )

        # Setup Repo B
        (self.repos_dir / "repo-b" / "prompts").mkdir(parents=True)
        meta_b1 = {"name": "p3", "framework": "RISEN", "score": {"overall": 7.5}}
        (self.repos_dir / "repo-b" / "prompts" / "p3.md").write_text(
            dump_frontmatter_markdown(meta_b1, "Refactor database migrations"),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_search_by_framework(self):
        results = query_prompt_catalog(self.repos_dir, "", framework="RISEN")
        self.assertEqual(len(results), 2)
        names = [r["file"] for r in results]
        self.assertIn("p1.md", names)
        self.assertIn("p3.md", names)

    def test_search_by_min_score(self):
        results = query_prompt_catalog(self.repos_dir, "", min_score=8.0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["file"], "p1.md")

    def test_search_by_repo_filter(self):
        results = query_prompt_catalog(self.repos_dir, "", repo="repo-b")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["file"], "p3.md")


if __name__ == "__main__":
    unittest.main()
