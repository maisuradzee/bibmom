from __future__ import annotations

from decimal import Decimal
import unittest

from noema_core.nitrate_benchmarks import (
    NitrateBenchmark,
    NitrateBenchmarkError,
    NitrateBenchmarkKind,
    NitrateBenchmarkStatus,
    compare_nitrate_to_benchmark,
)
from noema_core.water_chemistry import NitrateBasis, NitrateConcentration


WHO = NitrateBenchmark(
    benchmark_id="WHO-GDWQ-NO3-2026",
    kind=NitrateBenchmarkKind.INTERNATIONAL_GUIDELINE,
    value=Decimal("50"),
    basis=NitrateBasis.NO3,
    matrix="drinking_water",
    source_url="https://www.who.int/publications/i/item/9789240121225",
    publication_date="2026-06-17",
    status=NitrateBenchmarkStatus.GUIDANCE_ONLY,
    scope_note="International drinking-water guideline; nitrate fact sheet assessment date is 2016.",
)

GEORGIA = NitrateBenchmark(
    benchmark_id="GE-DECREE-58-2014-NO3",
    kind=NitrateBenchmarkKind.NATIONAL_REGULATION,
    value=50,
    basis="NO3",
    matrix="drinking_water",
    source_url="https://www.matsne.gov.ge/ka/document/view/2196792",
    publication_date="2014-01-15",
    status="regulatory_scope_review_required",
    scope_note="Apply only after Article 1 scope, currentness and supply-specific legal review.",
)

DENMARK = NitrateBenchmark(
    benchmark_id="DK-EXPERT-REPORT-2026-NO3",
    kind="expert_recommendation",
    value=Decimal("6"),
    basis="NO3",
    matrix="drinking_water",
    source_url="https://mim.dk/media/o4hptfht/nitratereport-jan-7-2026-revised-clean.pdf",
    publication_date="2026-01-07",
    status="recommendation_only",
    scope_note="Expert-group recommendation; not treated by this prototype as an enacted legal limit.",
)


class NitrateBenchmarkTests(unittest.TestCase):
    def measurement(self, value, *, basis="NO3", matrix="drinking_water"):
        return NitrateConcentration(Decimal(str(value)), basis, matrix)

    def test_who_comparison_is_guidance_only_and_never_compliance(self):
        result = compare_nitrate_to_benchmark(self.measurement("51"), WHO)
        self.assertEqual(result.relation, "above_reference")
        self.assertEqual(result.interpretation, "international_guidance_context_only")
        self.assertFalse(result.compliance_decision_permitted)
        self.assertFalse(result.potability_decision_permitted)

    def test_georgian_regulatory_text_requires_scope_and_currentness_review(self):
        result = compare_nitrate_to_benchmark(self.measurement("50"), GEORGIA)
        self.assertEqual(result.relation, "at_reference")
        self.assertEqual(result.interpretation, "legal_scope_and_currentness_review_required")
        self.assertFalse(result.compliance_decision_permitted)

    def test_danish_expert_value_remains_recommendation_only(self):
        result = compare_nitrate_to_benchmark(self.measurement("7"), DENMARK)
        self.assertEqual(result.relation, "above_reference")
        self.assertEqual(result.interpretation, "expert_recommendation_context_only")
        self.assertFalse(result.compliance_decision_permitted)

    def test_raw_groundwater_is_not_compared_to_drinking_water_reference(self):
        with self.assertRaisesRegex(NitrateBenchmarkError, "matrix mismatch"):
            compare_nitrate_to_benchmark(
                self.measurement("10", matrix="groundwater"), WHO
            )

    def test_benchmark_registry_rejects_raw_groundwater_references(self):
        with self.assertRaisesRegex(NitrateBenchmarkError, "only drinking-water"):
            NitrateBenchmark(
                benchmark_id="INVALID-GROUNDWATER-REFERENCE",
                kind="international_guideline",
                value=50,
                basis="NO3",
                matrix="groundwater",
                source_url="https://example.org/groundwater",
                publication_date="2026-01-01",
                status="guidance_only",
                scope_note="Synthetic groundwater reference rejected by the drinking-water-only registry.",
            )

    def test_nitrate_nitrogen_is_not_silently_compared_with_nitrate_ion(self):
        with self.assertRaisesRegex(NitrateBenchmarkError, "basis mismatch"):
            compare_nitrate_to_benchmark(
                self.measurement("1.3", basis="NO3-N"), WHO
            )

    def test_peer_reviewed_study_is_not_an_allowed_benchmark_kind(self):
        with self.assertRaisesRegex(NitrateBenchmarkError, "not an accepted threshold source"):
            NitrateBenchmark(
                benchmark_id="NZ-COHORT-2026",
                kind="peer_reviewed_study",
                value="0.66",
                basis="NO3-N",
                matrix="drinking_water",
                source_url="https://pubmed.ncbi.nlm.nih.gov/42385869/",
                publication_date="2026-09-15",
                status="recommendation_only",
                scope_note="An epidemiological exposure category is not a regulatory threshold.",
            )

    def test_kind_and_status_must_agree(self):
        with self.assertRaisesRegex(NitrateBenchmarkError, "inconsistent"):
            NitrateBenchmark(
                benchmark_id="DK-INVALID",
                kind="expert_recommendation",
                value="6",
                basis="NO3",
                matrix="drinking_water",
                source_url="https://example.org/report.pdf",
                publication_date="2026-01-07",
                status="guidance_only",
                scope_note="A recommendation must not be labelled as international guidance.",
            )

    def test_invalid_numeric_values_are_rejected(self):
        for value in (True, -1, 0, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(NitrateBenchmarkError):
                NitrateBenchmark(
                    benchmark_id="INVALID",
                    kind="international_guideline",
                    value=value,
                    basis="NO3",
                    matrix="drinking_water",
                    source_url="https://example.org/guideline",
                    publication_date="2026-01-01",
                    status="guidance_only",
                    scope_note="Synthetic invalid benchmark used only by a unit test.",
                )

    def test_comparison_relations_are_explicit(self):
        self.assertEqual(compare_nitrate_to_benchmark(self.measurement("49"), WHO).relation, "below_reference")
        self.assertEqual(compare_nitrate_to_benchmark(self.measurement("50"), WHO).relation, "at_reference")
        self.assertEqual(compare_nitrate_to_benchmark(self.measurement("51"), WHO).relation, "above_reference")

    def test_basis_and_matrix_are_preserved_in_result(self):
        result = compare_nitrate_to_benchmark(self.measurement("2.5"), WHO)
        self.assertEqual(result.basis, NitrateBasis.NO3)
        self.assertEqual(result.matrix, "drinking_water")
        self.assertEqual(result.measured_value, Decimal("2.5"))


if __name__ == "__main__":
    unittest.main()
