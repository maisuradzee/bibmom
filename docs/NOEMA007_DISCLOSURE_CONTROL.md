# NOEMA-007 — Cross-release disclosure control boundary

- **Date:** 2026-11-26
- **Status:** design audit / synthetic counterexample; no real survey data used

## Purpose

NOEMA-007 currently validates one event/area aggregate record at a time. It rejects non-zero cell counts below a configured threshold (minimum 10), disallows direct identifiers and raw message/device data, and requires data-controller and privacy-review approval flags.

That is a useful input contract, but it is not a complete disclosure-control system. A per-record threshold does not reason about relationships among multiple releases, overlapping cohorts, complements, repeated time windows, or query history.

## FACT — current implementation boundary

- The validator accepts one record per call.
- It has no release-ledger identifier, canonical query fingerprint, cohort lineage, overlap graph, complementary-suppression state, or cumulative privacy-loss budget.
- The approval fields are caller-supplied booleans and dates. They are not cryptographic evidence of an actual independent review.
- The schema's minimum cell size is at least 10, and non-zero values from 1 to 9 are rejected in an individual record.

These statements describe the current code/schema contract. They do not imply that a real public dataset has been released.

## REPRODUCED RESULT — synthetic differencing counterexample

The regression test constructs two synthetic aggregate records for the same event, hazard, area, warning reference and measurement window:

- Release A: received_warning_n = 80
- Release B: received_warning_n = 79
- Each record independently satisfies the current per-record validation contract and the configured minimum cell size of 10.
- If the two releases represent nested cohorts, subtraction reveals a difference of 1.

The cohort relationship is deliberately a test assumption: the current schema does not carry a query predicate or cohort-lineage field with which to prove or disprove that relationship. No personal records or real operational data are used.

## INFERENCE

A per-record small-cell threshold cannot, by itself, guarantee privacy across a sequence of related aggregate releases. A release system must reason over the full release history and the relationship between query populations. The synthetic example is a narrow counterexample to a stronger claim; it is not a measurement of a real disclosure event.

This concern is consistent with the broader statistical-database literature. Dinur and Nissim (2003) show that multiple subset-sum answers can permit reconstruction even when answers are perturbed. NIST SP 800-188 recommends selecting an explicit data-sharing model, assessing release risk, using governance such as a Disclosure Review Board, and conducting re-identification studies. NIST SP 800-226 describes differential privacy as a quantitative privacy-loss framework and highlights implementation hazards.

## Proposed release architecture

1. **Trusted query construction.** The server-side query planner, not a public caller, creates canonical population and cohort predicates. A stable query fingerprint and parent/child cohort lineage are retained in a restricted release ledger.
2. **Batch release review.** Before publishing any event/area aggregate, compare it with all prior releases for the same population and overlapping measurement windows. Check nested differences, complements, repeated queries, sparse combinations and suppression interactions.
3. **Complementary suppression.** If suppressing one small cell would allow it to be reconstructed from row/column totals or other released aggregates, suppress additional cells or withhold the related table.
4. **Formal privacy option.** For repeated public query access, evaluate a differential-privacy mechanism with an explicit, composition-aware privacy budget and a documented threat model. Do not treat a noisy answer or a k threshold as a privacy proof.
5. **Governance.** Store the actual review decision, reviewer identity in a restricted system, approval scope, policy version and release hash. Public JSON must not contain reviewer personal details or secrets.
6. **Fail closed.** If query lineage, overlap information, release history, suppression state or privacy-budget accounting is unavailable, do not publish the new aggregate.

## Security and privacy limits

- The synthetic test demonstrates only a direct nested-count difference of one.
- It does not implement a complete overlap detector and cannot identify unknown relationships from counts alone.
- A query fingerprint does not itself prove that two cohorts are disjoint; lineage must be produced by a trusted query planner.
- A privacy budget is meaningful only when the mechanism, adjacency definition, sensitivity, contribution bounds, composition rule and randomness are correctly implemented and audited.
- No personal data, sensor records, message logs, device identifiers, private keys or operational data are added to this public repository.

## Next validation steps

- Define a canonical query/cohort model and a restricted release-ledger schema.
- Add a batch planner that rejects declared nested differences below the release threshold and detects complementary-suppression paths.
- Threat-model false cohort-disjointness claims, repeated releases and time-window differencing.
- Have an independent privacy specialist and the authorized data controller review the release model before any real dataset is accepted.
- Keep the current aggregate-only validator as a structural input check; do not label it anonymization or differential privacy.

## Sources

1. Garfinkel, S., Guttman, B., Near, J., Dajani, A., & Singer, P. (2023). *De-Identifying Government Datasets: Techniques and Governance*. NIST SP 800-188. https://doi.org/10.6028/NIST.SP.800-188
2. Near, J., Darais, D., & Lefkovitz, N. (2025). *Guidelines for Evaluating Differential Privacy Guarantees*. NIST SP 800-226. https://doi.org/10.6028/NIST.SP.800-226
3. Dinur, I., & Nissim, K. (2003). *Revealing information while preserving privacy*. PODS 2003, 202–210. https://doi.org/10.1145/773153.773173
