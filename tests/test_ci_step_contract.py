from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_ci_step_contract import validate_contract


class CiStepContractTests(unittest.TestCase):
    def _fixture(self, root: Path) -> None:
        workflow = (
            "name: sample\n"
            "on:\n  push:\n    branches: [main]\n"
            "jobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@v4\n"
            "      - name: Run tests\n"
            "        id: run_tests\n"
            "        run: python -m unittest discover -s tests\n"
        )
        workflow_path = root / ".github/workflows/ci.yml"
        workflow_path.parent.mkdir(parents=True)
        workflow_path.write_text(workflow, encoding="utf-8")
        lines = workflow.splitlines()
        starts = [i for i, line in enumerate(lines) if line.startswith("      - name: ")]
        steps = []
        for position, start in enumerate(starts):
            end = starts[position + 1] if position + 1 < len(starts) else len(lines)
            name = lines[start][len("      - name: "):]
            body = "\n".join(lines[start + 1:end]).rstrip() + "\n"
            steps.append({"name": name, "body": body})
        manifest = {"schema_version": 1, "workflow_path": ".github/workflows/ci.yml", "steps": steps}
        manifest_path = root / "data/ci-step-command-contract.json"
        manifest_path.parent.mkdir()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def test_unchanged_workflow_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            self.assertEqual(validate_contract(root), [])

    def test_noop_replacement_with_same_step_name_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            path = root / ".github/workflows/ci.yml"
            content = path.read_text(encoding="utf-8").replace(
                "run: python -m unittest discover -s tests", "run: true"
            )
            path.write_text(content, encoding="utf-8")
            self.assertIn("step_body_mismatch:Run tests", validate_contract(root))

    def test_added_step_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            path = root / ".github/workflows/ci.yml"
            path.write_text(path.read_text(encoding="utf-8") + "      - name: Unreviewed\n        run: echo unsafe\n", encoding="utf-8")
            self.assertTrue(any("workflow_steps_not_in_manifest" in item for item in validate_contract(root)))

    def test_unnamed_step_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            path = root / ".github/workflows/ci.yml"
            path.write_text(
                path.read_text(encoding="utf-8") + "      - run: true\n",
                encoding="utf-8",
            )
            self.assertIn("workflow_contains_unnamed_or_uncontracted_step", validate_contract(root))

    def test_duplicate_step_name_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            path = root / ".github/workflows/ci.yml"
            path.write_text(path.read_text(encoding="utf-8") + "      - name: Run tests\n        run: python -m unittest\n", encoding="utf-8")
            self.assertIn("duplicate_step_names", validate_contract(root))

    def test_duplicate_manifest_json_keys_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            path = root / "data/ci-step-command-contract.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            self.assertTrue(any("step_contract_manifest_invalid" in item for item in validate_contract(root)))


if __name__ == "__main__":
    unittest.main()
