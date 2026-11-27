#!/usr/bin/env python3
"""Verify a backup manifest's declared plaintext and ciphertext file digests."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from noema_core.backup_manifest import verify_backup_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to a JSON metadata manifest")
    parser.add_argument("--plaintext", required=True, type=Path, help="plaintext snapshot file")
    parser.add_argument("--ciphertext", required=True, type=Path, help="encrypted artifact file")
    args = parser.parse_args()

    try:
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
        verify_backup_artifacts(document, args.plaintext, args.ciphertext)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.exit(2, f"backup artifact verification failed: {exc}\n")

    print("backup manifest metadata schema: valid")
    print("plaintext artifact: SHA-256 and byte length match")
    print("ciphertext artifact: SHA-256 and byte length match")
    print(
        "scope: file integrity only; no detached signature authentication, decryption, "
        "provider retention, SQLite integrity or restore verification"
    )


if __name__ == "__main__":
    main()
