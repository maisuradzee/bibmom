# NOEMA Run 55 — NOEMA-007 catalogue clarification

The public catalogue entry for `NOEMA-2026-007` is version 1.2. This is a metadata clarification of the existing WRP 2025 / 2026 action-enablers study, not a new study and not a new dataset.

## Unit correction

The pinned WRP 2025 data dictionary defines `CountryIncomeLevel` as the World Bank country-income group at fieldwork (FY2024-25). It is a **country-level classification**, not the respondent's personal or household income. The catalogue and preprint now label the subgroup comparison accordingly.

## Derived descriptive contrasts

From the frozen PROJWT-weighted point estimates:
- Three vs one warning channel: +26.7 percentage points (64.2% − 37.5%).
- Both household plan + personal agency vs neither: +56.4 pp (83.0% − 26.6%).
- Upper-middle vs low country-income group: +27.5 pp (75.5% − 48.0%).
- High vs lower-middle country-income group: +24.0 pp (70.9% − 46.9%).

These are unadjusted differences between weighted point estimates. The reproduction does not provide design-based confidence intervals, effective subgroup sample sizes or causal effects. The numbers are prioritisation signals for further research, not evidence that adding channels or plans causes an individual to act.

## Evidence status

- **FACT:** source variable is country-level `CountryIncomeLevel`, pinned in the WRP public data dictionary.
- **REPRODUCED RESULT:** arithmetic differences are recomputed from the frozen weighted aggregate and checked by CI.
- **INFERENCE:** subgroup gaps may motivate an equity-focused follow-up.
- **UNTESTED IDEA:** causal mechanisms or household-level income gradients require microdata, survey-design variance estimation and independent review.

The study remains Preliminary; no Published status is claimed.
