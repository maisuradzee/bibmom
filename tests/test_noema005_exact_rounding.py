from __future__ import annotations

import random
import shutil
import struct
import subprocess
import tempfile
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "noema005_exact_rounding_harness.c"


def integer_rounding_oracle(units: int) -> int:
    """Round an exact signed integer multiple of 2**-1074 to binary64 bits."""
    negative = units < 0
    magnitude = abs(units)
    sign = (1 << 63) if negative else 0
    if magnitude == 0:
        return 0

    highest = magnitude.bit_length() - 1
    if highest <= 51:
        return sign | magnitude

    discarded = highest - 52
    significand = magnitude >> discarded
    if discarded:
        remainder = magnitude & ((1 << discarded) - 1)
        halfway = 1 << (discarded - 1)
        if remainder > halfway or (remainder == halfway and (significand & 1)):
            significand += 1
            if significand == (1 << 53):
                significand >>= 1
                highest += 1

    exponent = highest - 51
    if exponent >= 0x7FF:
        return sign | (0x7FF << 52)
    return sign | (exponent << 52) | (significand & ((1 << 52) - 1))


def decimal_rounding_oracle(units: int) -> int:
    """Use an exact terminating Decimal rational before CPython's binary64 conversion."""
    with localcontext() as context:
        # The largest supported 2560-bit numerator has fewer than 800 decimal
        # digits; 1200 digits preserve the terminating rational exactly.
        context.prec = 1200
        exact_value = Decimal(units) / Decimal(1 << 1074)
        rounded = float(exact_value)
    return struct.unpack(">Q", struct.pack(">d", rounded))[0]


class Noema005ExactRoundingOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("gcc")
        if compiler is None:
            raise unittest.SkipTest("GCC is required for the native exact-rounding harness")
        cls.tempdir = tempfile.TemporaryDirectory(prefix="noema005-rounding-oracle-")
        cls.binary = Path(cls.tempdir.name) / "exact-rounding-harness"
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

    @staticmethod
    def cases() -> list[int]:
        one = 1 << 1074
        half_ulp_at_one = 1 << 1021
        max_finite = ((1 << 53) - 1) << 2045
        overflow_midpoint = max_finite + (1 << 2044)
        values = [
            0, 1, -1,
            (1 << 52) - 1, 1 << 52, (1 << 52) + 1,
            one,
            one + half_ulp_at_one - 1,
            one + half_ulp_at_one,
            one + half_ulp_at_one + 1,
            one + 3 * half_ulp_at_one,
            one - (1 << 1020) - 1,
            one - (1 << 1020),
            one - (1 << 1020) + 1,
            -one - half_ulp_at_one,
            max_finite,
            overflow_midpoint - 1,
            overflow_midpoint,
            overflow_midpoint + 1,
            -max_finite,
            -overflow_midpoint,
            (1 << 2559) - 1,
            -(1 << 2559),
        ]

        rng = random.Random(0x4E4F454D4135)
        for bit_length in (
            2, 3, 51, 52, 53, 54, 100, 1020, 1021, 1022, 1073,
            1074, 1075, 1126, 1127, 2044, 2045, 2097, 2098, 2558, 2559,
        ):
            for _ in range(6):
                magnitude = (1 << (bit_length - 1)) | rng.getrandbits(bit_length - 1)
                values.extend((magnitude, -magnitude))
        return values

    def test_native_converter_matches_two_independent_exact_oracles(self):
        values = self.cases()
        for value in values:
            with self.subTest(value_bits=abs(value).bit_length(), negative=value < 0):
                self.assertEqual(
                    integer_rounding_oracle(value),
                    decimal_rounding_oracle(value),
                    "independent Python integer and exact Decimal references disagree",
                )

        completed = subprocess.run(
            [str(self.binary)],
            input="".join(f"{value}\n" for value in values),
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        actual = [int(line, 16) for line in completed.stdout.splitlines()]
        expected = [decimal_rounding_oracle(value) for value in values]
        self.assertEqual(len(actual), len(values))
        self.assertEqual(actual, expected)

    def test_boundary_suite_includes_overflow_tie_and_signed_extremes(self):
        values = self.cases()
        self.assertIn(((1 << 53) - 1) * (1 << 2045) + (1 << 2044), values)
        self.assertIn(-(1 << 2559), values)
        self.assertGreaterEqual(len(values), 250)


if __name__ == "__main__":
    unittest.main()
