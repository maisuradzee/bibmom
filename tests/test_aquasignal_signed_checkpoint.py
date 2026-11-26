from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator, FormatChecker

from noema_core.aquasignal import SignalAssessment
from noema_core.aquasignal_checkpoint import (
    TrustedCheckpointState,
    serialize_checkpoint_payload,
    verify_signed_checkpoint,
)
from noema_core.aquasignal_incidents import record_assessment
from noema_core.aquasignal_store import AquaSignalStore

ROOT = Path(__file__).resolve().parents[1]
KEY_ID = "synthetic-aquasignal-checkpoint-key"
STORE_ID = "a" * 32


class AquaSignalSignedCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-aquasignal-checkpoint-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "private" / "aquasignal.sqlite3"
        self.store = AquaSignalStore(self.database)
        now = datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)
        assessment = SignalAssessment(
            "WATCH", "synthetic-plant-1", "free_chlorine", "synthetic-sensor-1",
            0.9, "mg/L", now, 1, "synthetic checkpoint fixture",
        )
        incident = record_assessment(
            None, assessment, incident_id="synthetic-inc-1",
            event_id="synthetic-evt-1", now=now,
        )
        self.store.append(incident)
        self.local = self.store.verify()
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.trusted_keys = {KEY_ID: self.public_key}

    def make_signed(self, *, sequence=4, event_count=None, last_hash=None, store_id=STORE_ID, key_id=KEY_ID):
        document = {
            "format_version": 1,
            "store_id": store_id,
            "sequence": sequence,
            "created_at_utc": "2026-11-26T10:05:00Z",
            "event_count": self.local["event_count"] if event_count is None else event_count,
            "last_hash": self.local["last_hash"] if last_hash is None else last_hash,
            "signature_format": "ed25519-raw",
            "signing_key_id": key_id,
        }
        payload = serialize_checkpoint_payload(document)
        return payload, self.private_key.sign(payload)

    def verify(self, payload, signature, **kwargs):
        return verify_signed_checkpoint(
            self.store, payload, signature, self.trusted_keys,
            expected_store_id=STORE_ID, **kwargs,
        )

    def test_signed_checkpoint_authenticates_exact_payload_and_local_chain(self):
        payload, signature = self.make_signed()
        result = self.verify(payload, signature)
        self.assertTrue(result["valid"])
        self.assertEqual(result["sequence"], 4)
        self.assertEqual(result["event_count"], self.local["event_count"])
        self.assertEqual(result["last_hash"], self.local["last_hash"])
        self.assertEqual(result["next_trusted_state"]["checkpoint_sha256"], hashlib.sha256(payload).hexdigest())

    def test_checkpoint_signature_cannot_be_reused_after_payload_change(self):
        payload, signature = self.make_signed()
        changed, _ = self.make_signed(sequence=5)
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            self.verify(changed, signature)

    def test_unknown_key_id_is_rejected(self):
        payload, signature = self.make_signed(key_id="untrusted-key")
        with self.assertRaisesRegex(ValueError, "unknown checkpoint signing key"):
            self.verify(payload, signature)

    def test_wrong_store_id_is_rejected(self):
        payload, signature = self.make_signed(store_id="b" * 32)
        with self.assertRaisesRegex(ValueError, "different AquaSignal store"):
            self.verify(payload, signature)

    def test_signed_checkpoint_must_match_local_chain_head(self):
        payload, signature = self.make_signed(last_hash="f" * 64)
        with self.assertRaisesRegex(ValueError, "external checkpoint hash mismatch"):
            self.verify(payload, signature)

    def test_lower_sequence_is_rejected_as_rollback(self):
        payload, signature = self.make_signed(sequence=8)
        state = TrustedCheckpointState(STORE_ID, 9, "0" * 64)
        with self.assertRaisesRegex(ValueError, "rollback detected"):
            self.verify(payload, signature, trusted_state=state)

    def test_same_sequence_with_different_digest_is_rejected(self):
        payload, signature = self.make_signed(sequence=9)
        state = TrustedCheckpointState(STORE_ID, 9, "0" * 64)
        with self.assertRaisesRegex(ValueError, "equivocation detected"):
            self.verify(payload, signature, trusted_state=state)

    def test_high_water_state_is_bound_to_expected_store(self):
        payload, signature = self.make_signed(sequence=10)
        state = TrustedCheckpointState("b" * 32, 9, "0" * 64)
        with self.assertRaisesRegex(ValueError, "different AquaSignal store"):
            self.verify(payload, signature, trusted_state=state)

    def test_same_checkpoint_is_idempotent_at_same_sequence(self):
        payload, signature = self.make_signed(sequence=9)
        state = TrustedCheckpointState(STORE_ID, 9, hashlib.sha256(payload).hexdigest())
        result = self.verify(payload, signature, trusted_state=state)
        self.assertTrue(result["idempotent"])

    def test_higher_sequence_advances_external_high_water_state(self):
        payload, signature = self.make_signed(sequence=10)
        state = TrustedCheckpointState(STORE_ID, 9, "0" * 64)
        result = self.verify(payload, signature, trusted_state=state)
        self.assertEqual(result["next_trusted_state"]["sequence"], 10)

    def test_duplicate_json_keys_are_rejected(self):
        payload, signature = self.make_signed()
        duplicated = payload.replace(b'"format_version":1', b'"format_version":1,"format_version":1')
        with self.assertRaisesRegex(ValueError, "duplicate checkpoint JSON key"):
            self.verify(duplicated, signature)

    def test_noncanonical_json_is_rejected(self):
        payload, signature = self.make_signed()
        noncanonical = b" " + payload
        with self.assertRaisesRegex(ValueError, "canonical encoding"):
            self.verify(noncanonical, signature)

    def test_checkpoint_schema_matches_runtime_contract(self):
        schema = json.loads((ROOT / "data/aquasignal-checkpoint.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        payload, _ = self.make_signed()
        document = json.loads(payload)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)

    def test_invalid_boolean_sequence_is_not_accepted_as_integer(self):
        payload, _ = self.make_signed()
        document = json.loads(payload)
        document["sequence"] = True
        with self.assertRaisesRegex(ValueError, "positive integer"):
            serialize_checkpoint_payload(document)


if __name__ == "__main__":
    unittest.main()
