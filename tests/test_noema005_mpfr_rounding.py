from __future__ import annotations

import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_noema005_exact_rounding import (
    Noema005ExactRoundingOracleTests,
    decimal_rounding_oracle,
)

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "noema005_mpfr_rounding_harness.c"


class Noema005MpfrRoundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("gcc")
        pkg_config = shutil.which("pkg-config")
        if compiler is None or pkg_config is None:
            raise unittest.SkipTest("GCC and pkg-config are required for the MPFR oracle")
        available = subprocess.run(
            [pkg_config, "--exists", "mpfr"],
            check=False,
            capture_output=True,
        )
        if available.returncode != 0:
            raise unittest.SkipTest("MPFR development library is not installed")

        cls.tempdir = tempfile.TemporaryDirectory(prefix="noema005-mpfr-oracle-")
        cls.binary = Path(cls.tempdir.name) / "mpfr-rounding-harness"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra",
                "-Werror", str(HARNESS), "-lmpfr", "-lgmp", "-lm",
                "-o", str(cls.binary),
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

    def test_native_converter_matches_mpfr_and_python_decimal(self):
        values = Noema005ExactRoundingOracleTests.cases()
        rng = random.Random(0x4D5046524E4F454D)
        for bit_length in (1, 2, 52, 53, 54, 1021, 1074, 1075, 2045, 2097, 2558, 2559):
            for _ in range(8):
                magnitude = (1 << (bit_length - 1)) | rng.getrandbits(bit_length - 1)
                values.extend((magnitude, -magnitude))

        completed = subprocess.run(
            [str(self.binary)],
            input="".join(f"{value}\n" for value in values),
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        actual = [int(line, 16) for line in completed.stdout.splitlines()]
        expected = [decimal_rounding_oracle(value) for value in values]
        self.assertEqual(len(actual), len(values))
        self.assertEqual(actual, expected)

    @staticmethod
    def full_width_cases() -> list[int]:
        """Return 1,024 seeded signed integers plus 1,044 tie-adjacent values."""
        rng = random.Random(0x4E4F454D41355F52)
        values: list[int] = []

        for _ in range(1024):
            bit_length = rng.randint(1, 2559)
            magnitude = (1 << (bit_length - 1)) | rng.getrandbits(bit_length - 1)
            values.append(-magnitude if rng.getrandbits(1) else magnitude)

        for highest in range(53, 2559, 29):
            shift = highest - 52
            seed = (1 << 52) | rng.getrandbits(52)
            for significand in (seed & ~1, seed | 1):
                midpoint = (significand << shift) + (1 << (shift - 1))
                for delta in (-1, 0, 1):
                    candidate = midpoint + delta
                    values.extend((candidate, -candidate))
        return values

    def test_native_converter_matches_mpfr_for_full_width_and_tie_adjacent_inputs(self):
        values = self.full_width_cases()
        self.assertEqual(len(values), 2068)

        expected = []
        for value in values:
            with self.subTest(value_bits=abs(value).bit_length(), negative=value < 0):
                integer_result = integer_rounding_oracle(value)
                decimal_result = decimal_rounding_oracle(value)
                self.assertEqual(integer_result, decimal_result)
                expected.append(decimal_result)

        completed = subprocess.run(
            [str(self.binary)],
            input="".join(f"{value}\\n" for value in values),
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        actual = [int(line, 16) for line in completed.stdout.splitlines()]
        self.assertEqual(len(actual), len(values))
        self.assertEqual(actual, expected)

    def test_mpfr_harness_rejects_signed_overflow(self):
        for value in (1 << 2559, -(1 << 2559) - 1):
            with self.subTest(value=value):
                completed = subprocess.run(
                    [str(self.binary)],
                    input=f"{value}\n",
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertIn("invalid or out-of-range", completed.stderr)


if __name__ == "__main__":
    unittest.main()
