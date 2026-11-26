#!/usr/bin/env python3
"""Verify an exact-byte Ed25519 manifest signature and its local artifact digests."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from noema_core.backup_manifest import verify_signed_backup_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="exact UTF-8 JSON manifest bytes")
    parser.add_argument("--signature", required=True, type=Path, help="detached raw 64-byte Ed25519 signature")
    parser.add_argument("--public-key", required=True, type=Path, help="trusted raw 32-byte Ed25519 public key")
    parser.add_argument("--public-key-id", required=True, help="out-of-band trusted key identifier")
    parser.add_argument("--plaintext", required=True, type=Path, help="plaintext snapshot artifact")
    parser.add_argument("--ciphertext", required=True, type=Path, help="encrypted artifact")
    args = parser.parse_args()

    try:
        result = verify_signed_backup_artifacts(
            args.manifest.read_bytes(),
            args.signature.read_bytes(),
            {args.public_key_id: args.public_key.read_bytes()},
            args.plaintext,
            args.ciphertext,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"backup signature/artifact verification failed: {exc}\n")

    print("detached Ed25519 signature: valid")
    print(f"trusted signing key identifier: {result['signature']['signing_key_id']}")
    print("plaintext and ciphertext SHA-256: valid")
    print(
        "scope: exact manifest bytes and local artifact integrity only; no decryption, "
        "provider object-version/retention verification, SQLite validation or restore"
    )


if __name__ == "__main__":
    main()
