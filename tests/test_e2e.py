# tests/test_e2e.py
import subprocess
import sys
import unittest
from pathlib import Path


class TestE2E(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.bin = self.root / "bin" / "prompt-eng"

    def test_e2e_initial_scan_populated(self):
        # Verify repos directory has profiles from initial live scan
        repos_dir = self.root / "repos"
        self.assertTrue(repos_dir.exists())
        self.assertTrue((repos_dir / "0x-arbiter" / "profile.yaml").exists())

    def test_e2e_scan_and_profile_flow(self):
        # Run scan on dev root
        res_scan = subprocess.run(
            [sys.executable, str(self.bin), "scan", "--root", "/home/rizz/dev"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_scan.returncode, 0, f"Scan failed: {res_scan.stderr}")

        # Verify repos directory has profiles
        repos_dir = self.root / "repos"
        self.assertTrue(repos_dir.exists())
        self.assertTrue((repos_dir / "0x-arbiter" / "profile.yaml").exists())

        # Test listing
        res_list = subprocess.run(
            [sys.executable, str(self.bin), "list"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_list.returncode, 0)
        self.assertIn("0x-arbiter", res_list.stdout)

        # Test profile inspection
        res_prof = subprocess.run(
            [sys.executable, str(self.bin), "profile", "0x-arbiter"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_prof.returncode, 0)
        self.assertIn("language: python", res_prof.stdout)


if __name__ == "__main__":
    unittest.main()
