import subprocess
import sys
import unittest
from pathlib import Path

class TestScaffolding(unittest.TestCase):
    def test_package_import(self):
        import prompt_eng
        self.assertTrue(hasattr(prompt_eng, "__version__"))
        self.assertEqual(prompt_eng.__version__, "0.1.0")

    def test_bin_executable_runs(self):
        root = Path(__file__).resolve().parent.parent
        bin_path = root / "bin" / "prompt-eng"
        self.assertTrue(bin_path.exists(), "bin/prompt-eng does not exist")
        res = subprocess.run([sys.executable, str(bin_path), "--version"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("prompt-eng 0.1.0", res.stdout.strip())

if __name__ == "__main__":
    unittest.main()
