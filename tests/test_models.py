import unittest

from prompt_eng.models import (
    HarnessInfo,
    PromptSpec,
    RepoProfile,
    RubricScore,
    SessionSummary,
    StackInfo,
    dump_frontmatter_markdown,
    dump_yaml_simple,
    load_yaml_simple,
    parse_frontmatter_markdown,
)


class TestModels(unittest.TestCase):
    def test_rubric_score_calculation(self):
        score = RubricScore(clarity=8, specificity=7, context=9, completeness=8, structure=8)
        self.assertAlmostEqual(score.overall, 8.0, places=1)

        # Explicit overall is respected if provided
        custom_score = RubricScore(
            clarity=8, specificity=7, context=9, completeness=8, structure=8, overall=9.2
        )
        self.assertEqual(custom_score.overall, 9.2)

    def test_yaml_roundtrip_simple(self):
        data = {
            "name": "0x-arbiter",
            "path": "/home/rizz/dev/0x-arbiter",
            "stack": {
                "language": "python",
                "package_manager": "uv",
            },
            "invariants": ["Zero-stall execution", "Testing domain separation"],
        }
        yaml_str = dump_yaml_simple(data)
        self.assertIn("name: 0x-arbiter", yaml_str)
        self.assertIn("  language: python", yaml_str)
        self.assertIn("- Zero-stall execution", yaml_str)
        parsed = load_yaml_simple(yaml_str)
        self.assertEqual(parsed["name"], "0x-arbiter")
        self.assertEqual(parsed["stack"]["language"], "python")
        self.assertEqual(len(parsed["invariants"]), 2)
        self.assertEqual(parsed["invariants"][0], "Zero-stall execution")

    def test_yaml_types_and_nested_lists(self):
        data = {
            "is_active": True,
            "count": 42,
            "rating": 9.5,
            "empty_val": None,
            "items": [
                {"id": 1, "label": "first"},
                {"id": 2, "label": "second"},
            ],
        }
        yaml_str = dump_yaml_simple(data)
        parsed = load_yaml_simple(yaml_str)
        self.assertEqual(parsed["is_active"], True)
        self.assertEqual(parsed["count"], 42)
        self.assertEqual(parsed["rating"], 9.5)
        self.assertIsNone(parsed["empty_val"])
        self.assertEqual(len(parsed["items"]), 2)
        self.assertEqual(parsed["items"][0]["label"], "first")

    def test_frontmatter_markdown_roundtrip(self):
        meta = {"name": "test-prompt", "framework": "RISEN", "score": {"overall": 8.5}}
        body = "This is the clean prompt content."
        serialized = dump_frontmatter_markdown(meta, body)
        self.assertTrue(serialized.startswith("---\n"))
        self.assertIn("framework: RISEN", serialized)
        self.assertTrue(serialized.endswith("This is the clean prompt content.\n"))

        parsed_meta, parsed_body = parse_frontmatter_markdown(serialized)
        self.assertEqual(parsed_meta["framework"], "RISEN")
        self.assertEqual(parsed_body.strip(), "This is the clean prompt content.")

    def test_parse_frontmatter_without_frontmatter(self):
        raw_markdown = "# Simple Heading\nJust content"
        meta, body = parse_frontmatter_markdown(raw_markdown)
        self.assertEqual(meta, {})
        self.assertEqual(body, raw_markdown)

    def test_dataclasses_instantiation(self):
        stack = StackInfo(
            language="python", package_manager="uv", test_framework="pytest", linter="ruff"
        )
        harness = HarnessInfo(instruction_files=["AGENTS.md"], active_skills=["brainstorming"])
        profile = RepoProfile(
            name="test-repo",
            path="/tmp/test",
            description="Test repo",
            stack=stack,
            harness=harness,
            invariants=["invar1"],
            last_scanned="2026-09-22T00:00:00Z",
        )
        self.assertEqual(profile.name, "test-repo")
        self.assertEqual(profile.stack.language, "python")
        self.assertEqual(profile.harness.active_skills, ["brainstorming"])

        session = SessionSummary(
            harness="antigravity",
            session_id="sess-123",
            repo_name="test-repo",
            user_goal="Implement feature",
            key_tools=["run_command", "view_file"],
            errors=[],
            last_turn_state="COMPLETED",
        )
        self.assertEqual(session.session_id, "sess-123")
        self.assertEqual(session.key_tools, ["run_command", "view_file"])

        score = RubricScore(clarity=9, specificity=9, context=9, completeness=9, structure=9)
        prompt = PromptSpec(
            name="test-spec",
            repo="test-repo",
            framework="RISEN",
            target_harness="antigravity",
            session_id="sess-123",
            score=score,
            content="Prompt text",
            created_at="2026-09-22T00:00:00Z",
        )
        self.assertEqual(prompt.name, "test-spec")
        self.assertEqual(prompt.score.overall, 9.0)


if __name__ == "__main__":
    unittest.main()
