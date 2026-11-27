# NOEMA-2026-007 — Independent WRP 2025 warning-to-action reproduction protocol

- **ID:** NOEMA-2026-007-WRP2025-WARNING-ACTION-REPRO-001
- **Status:** draft / reproducibility protocol; result pending CI execution
- **Date:** 2026-11-27
- **Research question:** can NOEMA independently reproduce the publisher's global warning-receipt and ability-to-act aggregates from the pinned public WRP 2025 microdata while preserving exact denominators and privacy boundaries?

## Source and provenance

- Lloyd's Register Foundation, *World Risk Poll 2025*, public Wave 4 Parquet release.
- Repository: https://github.com/lrfoundation/world_risk_poll_data
- Pinned commit: \`f2b810c3c4333de6347ad2c9eade3c48ae17be4c\`
- File: \`WRP_2025/WRP_2025.parquet\`
- Git blob SHA-1: \`3e785688e067ded5fdfbe9b50721023ecea87826\`
- Expected byte length: 7,070,416
- Licence: CC BY-SA 4.0; attribution and share-alike terms are recorded in the result metadata.

The microdata is downloaded only to an ephemeral GitHub Actions runner. The repository stores the pinned source metadata and aggregate-only output, never respondent-level rows or identifiers.

## Variables and method

- Weight: \`PROJWT\` (population-projection weight).
- Warning base: \`WP24181\` non-null; the eight warning channels are \`WP24181\`–\`WP24188\` as individually named in the source dictionary.
- A respondent is classified as warned when any channel equals code 1. Codes 2, 97 (does not apply), 98 (don't know) and 99 (refused) are retained in the asked denominator and do not count as a warning.
- Ability-to-act base: all respondents classified as warned; \`WP24215\` codes 1, 2, 98 and 99 remain in the denominator.
- Georgia: \`COUNTRY_ISO3=GEO\`; impacted base (\`WP24213=1\`) and warning-question base are counted separately.

Weighted percentages are calculated as the sum of PROJWT for the selected response divided by the sum of PROJWT for the full asked base. The script uses \`math.fsum\`, validates finite non-negative weights, checks the pinned Git blob hash and byte length, and fails if the expected source denominators or rounded publisher aggregates do not match.

## Publisher reference values to reproduce

The source report's README gives:

- 143,459 respondents in 140 countries/territories;
- 24,249 respondents asked about warning channels;
- 16,996 warned respondents asked about ability to act;
- 80.0% received at least one warning;
- 63.8% able and 35.8% unable to act; approximately 0.5% answered don't know/refused;
- Georgia: 101 impacted respondents, 99 in the warning-question base; the report's country-ranking threshold is n>=100.

These are publisher reference values, not NOEMA results until the dedicated workflow succeeds.

## Evidence classification

- **FACT:** the pinned public release and data dictionary define the variables, codes and licence.
- **REPRODUCED RESULT:** reserved for the aggregate JSON emitted by the dedicated workflow after Git blob SHA-1, byte length, denominators and rounded values all match.
- **INFERENCE:** Georgia's warning-question base is below the publisher's threshold; no national ranking should be inferred.
- **UNTESTED IDEA:** connect the survey findings to authorised Georgian event-level warning and after-action records, if the relevant data controller approves access.

## Limitations

Survey warning receipt and self-reported ability to act do not measure message timeliness, comprehension, feasibility for every exposed person, verified protective action or avoided loss. This is not a national operational audit and does not establish causal warning effectiveness. The global weighted result must not be presented as a Georgian estimate.
