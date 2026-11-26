from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "noema005_accumulator_overflow_harness.c"


class Noema005AccumulatorOverflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("gcc")
        if compiler is None:
            raise unittest.SkipTest("GCC is required for the native accumulator overflow harness")
        cls.tempdir = tempfile.TemporaryDirectory(prefix="noema005-overflow-")
        cls.binary = Path(cls.tempdir.name) / "accumulator-overflow-harness"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra",
                "-Werror", str(HARNESS), "-lm", "-o", str(cls.binary),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tempdir"):
            cls.tempdir.cleanup()

    def test_signed_add_merge_and_binary64_paths_reject_overflow_without_mutation(self):
        completed = subprocess.run(
            [str(self.binary)],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            completed.stdout.strip(),
            "checked signed accumulator overflow tests passed",
        )


if __name__ == "__main__":
    unittest.main()
