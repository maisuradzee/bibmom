# NOEMA-007 — Risk-baseline freshness evaluator (prototype)

- **Status:** Draft engineering prototype
- **Scope:** source metadata and declared update-cycle review
- **Related research:** [dynamic risk-baseline freshness and interoperability](../research/drafts/NOEMA-2026-007-dynamic-risk-baseline-freshness-2026-11-27.md)

## Purpose

The 2026 joint ITU/UNDRR/WMO/IFRC report identifies fragmented risk data, outdated or incomplete exposure/vulnerability baselines, and weak operational links between planning data and warning decisions. This prototype addresses only one narrow part of that problem: deterministic review of a dataset's last-updated date against an update interval explicitly declared by its source owner or an applicable standard.

It does not establish whether a dataset is substantively accurate, complete, fit for a particular hazard, or legally reusable.

## Deterministic semantics

For a supplied `as_of_date`:

- **current** — the date is before `dataset_updated_date + declared_update_interval_days`;
- **due** — the date equals that declared due date;
- **overdue** — the date is after that due date;
- **unknown** — either the dataset update date or a source-declared interval is missing.

A missing interval is never replaced with a NOEMA-invented universal threshold. The retrieval timestamp is provenance only; it is not a substitute for the dataset's update date. Future dates and invalid UTC/date representations fail validation.

## Data and safety boundary

- The schema is closed and rejects unlisted fields.
- The input contains source metadata only; no people, household locations, device identifiers, or sensitive vulnerability records.
- URLs are validated syntactically but never fetched. Credential-like query/fragment parameter names are checked across `&` and `;` separators and up to four percent-decoding passes; this catches common double-encoded names but remains a heuristic, not a complete secret scanner.
- `licence_status` is preserved as metadata; it does not grant permission.
- The result always sets `ingestion_authorized: false`.
- `due`, `overdue`, and `unknown` require human review. The module does not send alerts, set hazard thresholds, or replace official risk decisions.

## Evidence classification

- **FACT:** The joint 2026 report describes risk-data fragmentation and outdated/incomplete exposure and vulnerability baselines. Source: https://www.undrr.org/publication/documents-and-publications/leveraging-ai-enhance-multi-hazard-early-warning-systems
- **FACT:** Visser, H., de Bruin, S. P., Bouwer, L. M., & Petersen, A. C. (2026), *Temporal characteristics of disaster data: how to avoid misconceptions, misinterpretation or misuse*, International Journal of Disaster Risk Reduction, 142, 106188, DOI: https://doi.org/10.1016/j.ijdrr.2026.106188. The article identifies data reliability, extreme values, population/GDP normalization, trend-model choices and expert judgment as factors that can distort disaster-data trend claims; it does not prescribe a universal dataset update interval.
- **FACT:** OGC API – Features defines standard discovery/query building blocks and metadata for geospatial feature collections; it is an interoperability interface standard, not a universal freshness policy. Source: https://www.ogc.org/standards/ogcapi-features/
- **INFERENCE:** A metadata-first evaluator can expose missing update-cycle declarations without accessing sensitive feature data.
- **REPRODUCED RESULT:** Synthetic unit tests exercise current/due/overdue/unknown boundaries and fail-closed validation. No real Georgia dataset has been evaluated.
- **HYPOTHESIS:** A source-owner-maintained inventory of update intervals and versions may reduce unnoticed baseline drift in operational review.
- **UNTESTED IDEA:** Compare the metadata evaluator's review flags with independent GIS/DRR expert audits on permissioned, non-sensitive datasets.

## Limitations and next steps

1. No official Georgian hazard/exposure/vulnerability layer has been ingested.
2. No universal staleness threshold is defined or implied.
3. No accuracy, false-positive, false-negative, or operational-impact metric is available.
4. OGC API – Features conformance, CRS compatibility, spatial coverage, and temporal alignment are not implemented by this narrow freshness evaluator.
5. Independent GIS/DRR and data-governance review is required before any operational use.

Next: inventory public metadata and source-owner-declared update cycles; keep each layer's reference date, updated date, retrieval time, licence and version separate; then validate synthetic interoperability cases before considering any permissioned real-data pilot.
