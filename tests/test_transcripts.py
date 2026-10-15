import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prompt_eng.models import SessionSummary
from prompt_eng.transcripts.antigravity import parse_antigravity_transcript
from prompt_eng.transcripts.claude import parse_claude_transcript
from prompt_eng.transcripts.resolver import (
    SessionResolver,
    render_session_summary_markdown,
)


class TestTranscripts(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        self.ag_path = self.fixtures_dir / "antigravity_sample.jsonl"
        with open(self.ag_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "type": "USER_INPUT",
                        "content": "Fix the failing test in tests/unit/test_catalog.py",
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "type": "PLANNER_RESPONSE",
                        "tool_calls": [
                            {"toolAction": "Running command", "toolSummary": "Run pytest"}
                        ],
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "type": "TOOL_RESPONSE",
                        "content": "FAILED tests/unit/test_catalog.py - AssertionError: 3 != 4",
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "type": "PLANNER_RESPONSE",
                        "content": "The catalog count expectation is mismatched. Should we update the catalog?",
                    }
                )
                + "\n"
            )

        self.cl_path = self.fixtures_dir / "claude_sample.jsonl"
        with open(self.cl_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "role": "user",
                        "content": "Refactor auth middleware to use bearer token",
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "role": "assistant",
                        "content": "I inspected middleware.ts and encountered a circular import error.",
                    }
                )
                + "\n"
            )

    def test_parse_antigravity(self) -> None:
        summary = parse_antigravity_transcript(self.ag_path, repo_name="0x-arbiter")
        self.assertEqual(summary.harness, "antigravity")
        self.assertIn("Fix the failing test", summary.user_goal)
        self.assertEqual(len(summary.key_tools), 1)
        self.assertIn("AssertionError", summary.errors[0])
        self.assertIn("Should we update the catalog?", summary.last_turn_state)

    def test_parse_claude(self) -> None:
        summary = parse_claude_transcript(self.cl_path, repo_name="agy-os")
        self.assertEqual(summary.harness, "claude-code")
        self.assertIn("Refactor auth middleware", summary.user_goal)
        self.assertIn("circular import error", summary.last_turn_state)

    def test_render_summary_markdown(self) -> None:
        summary = parse_antigravity_transcript(self.ag_path, repo_name="0x-arbiter")
        md = render_session_summary_markdown(summary)
        self.assertIn("## Session Context Summary", md)
        self.assertIn("**Harness**: antigravity", md)
        self.assertIn("Fix the failing test", md)

    def test_render_summary_markdown_empty_fields(self) -> None:
        summary = SessionSummary(
            harness="antigravity",
            session_id="test-123",
            repo_name="empty-repo",
            user_goal="",
            key_tools=[],
            errors=[],
            last_turn_state="",
        )
        md = render_session_summary_markdown(summary)
        self.assertIn("None recorded.", md)
        self.assertIn("No errors detected.", md)

    def test_parse_antigravity_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            parse_antigravity_transcript(Path("/nonexistent/transcript.jsonl"))

    def test_parse_claude_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            parse_claude_transcript(Path("/nonexistent/claude.jsonl"))

    def test_parse_corrupt_lines_handled(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tmp:
            tmp.write("\n")
            tmp.write("invalid json line\n")
            tmp.write(json.dumps({"type": "USER_INPUT", "content": "Hello"}) + "\n")
            tmp_path = Path(tmp.name)

        try:
            summary = parse_antigravity_transcript(tmp_path, repo_name="test")
            self.assertEqual(summary.user_goal, "Hello")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_session_resolver_by_file_path(self) -> None:
        summary_ag = SessionResolver.resolve_session("0x-arbiter", file_path=self.ag_path)
        self.assertEqual(summary_ag.harness, "antigravity")

        summary_cl = SessionResolver.resolve_session("agy-os", file_path=self.cl_path)
        self.assertEqual(summary_cl.harness, "claude-code")

    def test_session_resolver_find_latest_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            session_dir = temp_path / "conv-xyz" / ".system_generated" / "logs"
            session_dir.mkdir(parents=True, exist_ok=True)
            transcript_file = session_dir / "transcript.jsonl"
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({"type": "USER_INPUT", "content": "Do work"}) + "\n")

            harness, found_path = SessionResolver.find_latest_session(
                "my-repo", target_dir=temp_path
            )
            self.assertEqual(harness, "antigravity")
            self.assertEqual(found_path, transcript_file)

    def test_session_resolver_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            with self.assertRaises(FileNotFoundError):
                SessionResolver.find_latest_session("empty-repo", target_dir=temp_path)

    def test_session_resolver_nonexistent_file_path_raises(self) -> None:
        with self.assertRaises(FileNotFoundError) as ctx:
            SessionResolver.resolve_session(
                "my-repo", file_path=Path("/nonexistent/file/transcript.jsonl")
            )
        self.assertIn("Transcript file not found", str(ctx.exception))

    def test_session_resolver_nonexistent_session_id_raises(self) -> None:
        with self.assertRaises(FileNotFoundError) as ctx:
            SessionResolver.resolve_session(
                "my-repo", session_id="definitely-nonexistent-session-id-999"
            )
        self.assertIn(
            "Session 'definitely-nonexistent-session-id-999' not found", str(ctx.exception)
        )

    def test_claude_tool_counting_exact(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tmp:
            tmp.write(json.dumps({"role": "user", "content": "Please run command foo"}) + "\n")
            tmp.write(
                json.dumps(
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "Executing command now"},
                            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
                        ],
                    }
                )
                + "\n"
            )
            tmp_path = Path(tmp.name)

        try:
            summary = parse_claude_transcript(tmp_path, repo_name="claude-repo")
            self.assertEqual(summary.key_tools, ["Bash"])
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_parse_antigravity_xml_sanitization(self) -> None:
        raw_content = (
            "<USER_REQUEST>\n"
            "Implement authentication middleware\n"
            "</USER_REQUEST>\n"
            "<ADDITIONAL_METADATA>\n"
            "The current local time is: 2026-10-15T12:00:00+07:00\n"
            "</ADDITIONAL_METADATA>\n"
            "<USER_SETTINGS_CHANGE>\n"
            "Model changed\n"
            "</USER_SETTINGS_CHANGE>"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": raw_content}) + "\n")
            f.write(
                json.dumps(
                    {
                        "type": "PLANNER_RESPONSE",
                        "content": "I have created the auth middleware class.",
                    }
                )
                + "\n"
            )
            tmp_path = Path(f.name)

        try:
            summary = parse_antigravity_transcript(tmp_path, repo_name="sample-repo")
            self.assertEqual(summary.user_goal, "Implement authentication middleware")
            self.assertNotIn("ADDITIONAL_METADATA", summary.user_goal)
            self.assertIn("I have created the auth middleware class.", summary.last_turn_state)
        finally:
            tmp_path.unlink()

    def test_parse_antigravity_thinking_recovery(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Refactor database"}) + "\n")
            f.write(
                json.dumps(
                    {
                        "type": "PLANNER_RESPONSE",
                        "content": "",
                        "thinking": "Need to migrate schema first.",
                        "tool_calls": [{"name": "run_command"}],
                    }
                )
                + "\n"
            )
            tmp_path = Path(f.name)

        try:
            summary = parse_antigravity_transcript(tmp_path, repo_name="sample-repo")
            self.assertEqual(summary.last_turn_state, "Need to migrate schema first.")
        finally:
            tmp_path.unlink()

    def test_parse_antigravity_metadata_strip_without_user_request(self) -> None:
        raw_content = (
            "Run the migrations now\n<ADDITIONAL_METADATA>\nTime is 12:00\n</ADDITIONAL_METADATA>"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": raw_content}) + "\n")
            tmp_path = Path(f.name)

        try:
            summary = parse_antigravity_transcript(tmp_path, repo_name="sample-repo")
            self.assertEqual(summary.user_goal, "Run the migrations now")
        finally:
            tmp_path.unlink()

    def test_session_resolver_repo_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_home = Path(tmpdir)
            ag_brain = fake_home / ".gemini" / "antigravity" / "brain"

            # Session 1: Older, but belongs to target-repo
            s1_dir = ag_brain / "session-target" / ".system_generated" / "logs"
            s1_dir.mkdir(parents=True, exist_ok=True)
            s1_file = s1_dir / "transcript.jsonl"
            with open(s1_file, "w", encoding="utf-8") as f:
                f.write(
                    json.dumps({"type": "USER_INPUT", "content": "Working in /dev/target-repo"})
                    + "\n"
                )

            # Session 2: Newer, but belongs to other-repo
            s2_dir = ag_brain / "session-other" / ".system_generated" / "logs"
            s2_dir.mkdir(parents=True, exist_ok=True)
            s2_file = s2_dir / "transcript.jsonl"
            with open(s2_file, "w", encoding="utf-8") as f:
                f.write(
                    json.dumps({"type": "USER_INPUT", "content": "Working in /dev/other-repo"})
                    + "\n"
                )

            # Ensure s2 has newer mtime
            os.utime(s1_file, (1000, 1000))
            os.utime(s2_file, (2000, 2000))

            claude_projects = fake_home / ".claude" / "projects"
            cl_repo_dir = claude_projects / "-home-rizz-dev-my-claude-repo"
            cl_repo_dir.mkdir(parents=True, exist_ok=True)
            cl_file = cl_repo_dir / "claude-session.jsonl"
            with open(cl_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({"role": "user", "content": "hi"}) + "\n")

            with patch("pathlib.Path.home", return_value=fake_home):
                harness_ag, found_ag = SessionResolver.find_latest_session("target-repo")
                self.assertEqual(harness_ag, "antigravity")
                self.assertEqual(found_ag, s1_file)

                harness_cl, found_cl = SessionResolver.find_latest_session("my-claude-repo")
                self.assertEqual(harness_cl, "claude-code")
                self.assertEqual(found_cl, cl_file)


if __name__ == "__main__":
    unittest.main()
