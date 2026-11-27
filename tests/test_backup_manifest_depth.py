from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator

from noema_core.backup_manifest import (
    _MAX_MANIFEST_JSON_DEPTH,
    _check_manifest_json_nesting_depth,
    _load_manifest_bytes,
    validate_backup_manifest,
)


class BackupManifestNestingTests(unittest.TestCase):
    def test_accepts_exact_configured_nesting_depth(self):
        array_depth = _MAX_MANIFEST_JSON_DEPTH - 1
        text = '{"value":' + ('[' * array_depth) + '0' + (']' * array_depth) + '}'
        _check_manifest_json_nesting_depth(text)

    def test_rejects_nesting_above_configured_depth(self):
        array_depth = _MAX_MANIFEST_JSON_DEPTH
        text = '{"value":' + ('[' * array_depth) + '0' + (']' * array_depth) + '}'
        with self.assertRaisesRegex(ValueError, 'nesting exceeds maximum depth 64'):
            _check_manifest_json_nesting_depth(text)

    def test_brackets_and_escaped_quotes_inside_strings_do_not_change_depth(self):
        text = json.dumps({
            'value': 'brackets [] {} and quote " and backslash \\',
        })
        _check_manifest_json_nesting_depth(text)

    def test_manifest_loader_rejects_deep_input_before_schema_validation(self):
        array_depth = _MAX_MANIFEST_JSON_DEPTH
        text = '{"unknown":' + ('[' * array_depth) + '0' + (']' * array_depth) + '}'
        with self.assertRaisesRegex(ValueError, 'nesting exceeds maximum depth 64'):
            _load_manifest_bytes(text.encode('utf-8'))

    def test_manifest_loader_normalizes_recursive_parser_failure(self):
        with patch(
            'noema_core.backup_manifest.json.loads',
            side_effect=RecursionError('synthetic parser recursion'),
        ):
            with self.assertRaisesRegex(ValueError, 'nesting exceeds parser limit'):
                _load_manifest_bytes(b'{}')

    def test_schema_validator_normalizes_recursive_document_failure(self):
        with patch.object(
            Draft202012Validator,
            'iter_errors',
            side_effect=RecursionError('synthetic schema recursion'),
        ):
            with self.assertRaisesRegex(ValueError, 'exceeds schema validation depth'):
                validate_backup_manifest({})


if __name__ == '__main__':
    unittest.main()
