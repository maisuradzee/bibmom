#!/usr/bin/env python3
"""Validate a NOEMA backup manifest's non-secret metadata contract only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from noema_core.backup_manifest import validate_backup_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to a JSON metadata manifest")
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate_backup_manifest(document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.exit(2, f"manifest rejected: {exc}\n")
    print("manifest metadata schema: valid")
    print("scope: structure and declared formats only; no signature, ciphertext, storage or SQLite verification")


if __name__ == "__main__":
    main()
