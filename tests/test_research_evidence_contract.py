from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ResearchEvidenceContractTests(unittest.TestCase):
    def test_template_contains_all_five_evidence_labels(self):
        template = (ROOT / "research/TEMPLATE.md").read_text(encoding="utf-8")
        for label in ("FACT", "REPRODUCED RESULT", "INFERENCE", "HYPOTHESIS", "UNTESTED IDEA"):
            self.assertIn(label, template)

    def test_standard_defines_all_five_evidence_labels(self):
        standard = (ROOT / "docs/RESEARCH_STANDARD.md").read_text(encoding="utf-8")
        for label in ("FACT", "REPRODUCED RESULT", "INFERENCE", "HYPOTHESIS", "UNTESTED IDEA"):
            self.assertIn(label, standard)

    def test_template_requires_provenance_and_human_benefit(self):
        template = (ROOT / "research/TEMPLATE.md").read_text(encoding="utf-8")
        for heading in ("## ადამიანური სარგებელი და პრიორიტეტი", "## მონაცემთა წარმოშობა და საჭიროებები", "## ინოვაცია / პრაქტიკული გადაწყვეტა", "## შეზღუდვები და გაურკვევლობები"):
            self.assertIn(heading, template)

    def test_standard_distinguishes_planned_samples_from_collected_samples(self):
        standard = (ROOT / "docs/RESEARCH_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("planned sample count არ არის collected sample count", standard)


if __name__ == "__main__":
    unittest.main()
