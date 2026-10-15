import json
import unittest
from pathlib import Path


class TestSkillsSetup(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_workspace_skills_json(self):
        skills_json = self.root / ".agents" / "skills.json"
        self.assertTrue(skills_json.exists())
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        self.assertIn("entries", data)
        self.assertEqual(data["entries"][0]["path"], ".agents/skills")

    def test_local_skill_shadowing_files(self):
        ag_skill = self.root / ".agents" / "skills" / "prompt-architect" / "SKILL.md"
        cl_skill = self.root / ".claude" / "skills" / "prompt-architect" / "SKILL.md"
        self.assertTrue(ag_skill.exists(), "Antigravity local skill missing")
        self.assertTrue(cl_skill.exists(), "Claude Code local skill missing")

        content = ag_skill.read_text(encoding="utf-8")
        self.assertIn("name: prompt-architect", content)
        self.assertIn("author: 0xrizz", content)
        self.assertIn('version: "4.0.0"', content)
        self.assertIn("35 frameworks across 7 intent categories", content)
        self.assertIn("Graph-of-Thoughts", content)
        self.assertIn("Meta-Prompting", content)
        self.assertIn("Buffer-of-Thoughts", content)
        self.assertIn("Medprompt", content)
        self.assertIn("Attention & Cognitive Dynamics", content)
        self.assertIn("WCAG 2.2", content)

        cl_content = cl_skill.read_text(encoding="utf-8")
        self.assertIn("author: 0xrizz", cl_content)
        self.assertEqual(content, cl_content)

    def test_instruction_files_contain_sop(self):
        ag_md = self.root / "AGENTS.md"
        cl_md = self.root / "CLAUDE.md"
        self.assertTrue(ag_md.exists())
        self.assertTrue(cl_md.exists())
        self.assertIn("prompt-eng", ag_md.read_text(encoding="utf-8"))
        self.assertIn("prompt-eng", cl_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
