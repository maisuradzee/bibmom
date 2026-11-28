## NOEMA — Run 61: source-scope reinspection and INFRA preflight hardening

**Date:** 2026-11-28  
**Starting Main:** `c83e530d4330c21166bc230e8eb645dcf0e1fe51`  
**Active streams reviewed:** 4  
**Catalogue:** 12 Preliminary / 0 Published  
**New streams:** 0

### Work completed

- **AquaSignal:** independently reopened the official NEA 2025 annual-report PDF. Confirmed groundwater 124 = 74 routine + 50 field-instrumental points; 74 laboratory points; 681 analysis-group counts; nitrate field points 30 springs + 19 boreholes + 1 household well; surface-water 238 points / 2,571 samples / 73 parameter-coverage points. The 73 count belongs to surface water (p. 13), not groundwater. The nitrate column is `საყოფაცხოვრებო ჭა` (household well), not `საკონტროლო ჭა` (control well). Arithmetic checks reconcile all regional rows and columns. No sample-level concentrations, laboratory confirmation or vulnerable-zone designation are reported by these tables.
- **AquaSignal / NOEMA-2026-016:** rechecked NFA's official 2023 release and the Public Defender's 2025 report. NFA's 624 and rounded 12% are for combined food and drinking-water samples (>5,000), not water-only. The 520/850 drinking-water figures are planned allocations, not completed samples. No water-only prevalence is calculated.
- **INFRA-001:** created current-Main Draft PR [#319](https://github.com/maisuradzee/bibmom/pull/319), adding legacy encrypted RSA PEM-header detection and fail-closed handling of tracked symlinks to the Run 60 CI contract/scanner. Exact-head Quality CI [46156410077](https://github.com/maisuradzee/bibmom/actions/runs/46156410077) passed 942 tests with one MPFR-dependent skip. Scanner: 501 tracked UTF-8 text files scanned, 3 binary/non-UTF-8 skipped, zero configured findings. PR remains Draft pending independent security review.
- **NOEMA-005:** no new physical CPU experiment. Existing frozen CPU-thread reports and simulations passed CI.
- **NOEMA-007:** no new privacy-approved Georgian warning-event/after-action data; no new operational-effectiveness claim.

### Four-stream portfolio review

| Stream | Status | Next step |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active / Preliminary | Obtain official NEA RAR bytes and authorized sample dictionary; after 2026-12-01 separately verify 2027 plan submission, approval and publication |
| NOEMA-005 | Active / Preliminary | Bare-metal x86-64/ARM64, alternative reductions, native RSS and DRAM counters |
| NOEMA-007 | Active / Preliminary | Privacy-approved Georgian warning-event/after-action data with stage-specific denominators |
| INFRA-001 | Active / Engineering | Independent security review, external trust anchor, encrypted off-host backup and clean-host restore |

No fifth stream was added. No research was promoted to Published.

### CI and deployment

- PR #316 exact-head Quality CI [46155369320](https://github.com/maisuradzee/bibmom/actions/runs/46155369320): SUCCESS.
- Starting Main Quality CI [46155436556](https://github.com/maisuradzee/bibmom/actions/runs/46155436556): SUCCESS on `c83e530d4330c21166bc230e8eb645dcf0e1fe51`. Post-PR #318 Main Quality CI [46156342498](https://github.com/maisuradzee/bibmom/actions/runs/46156342498) and Pages deployment [46156342512](https://github.com/maisuradzee/bibmom/actions/runs/46156342512) succeeded on `34df60f181da4558c02d7c96d767dff1138bb61b`. Post-PR #320 Main is `eb638e37b694cb64871435ab8309aa51ed445207`; Main Quality CI [46156586296](https://github.com/maisuradzee/bibmom/actions/runs/46156586296) and Pages deployment [46156586304](https://github.com/maisuradzee/bibmom/actions/runs/46156586304) succeeded. The first Pages deploy attempt returned HTTP 502; rerunning the deploy job succeeded.
- Starting Main Pages deployment [46155436538](https://github.com/maisuradzee/bibmom/actions/runs/46155436538): SUCCESS on `c83e530d4330c21166bc230e8eb645dcf0e1fe51`.
- PR #319 exact-head Quality CI [46156074951](https://github.com/maisuradzee/bibmom/actions/runs/46156074951): SUCCESS; remains Draft.

### Limitations and safety

The NEA PDF was inspected through the public document reader, but raw bytes were not available for SHA-256. The separate 2021–2025 groundwater RAR remains uninspected. No household coordinates, private-well data, sample-level personal/health records, credentials, private keys or backup payloads were added. No Supabase project or other project's database was created or used.

### Next priorities

1. After 2026-12-01, separately verify the 2027 monitoring plan's submission, ministerial approval and public release.
2. Obtain the NEA RAR and NFA XLSX through authorized routes; hash raw bytes before extraction.
3. Complete independent security review of PR #319 before merge; its base refresh is required because Main advanced after PR #320.
4. Obtain bare-metal x86-64/ARM64 NOEMA-005 measurements and privacy-approved Georgian warning-event data for NOEMA-007.

[Run 61 full audit](docs/run-audits/2026-11-28-run-61.md)

---

## NOEMA — Run 58: AquaSignal aggregate audit and INFRA CI/secret-scan hardening

**Date:** 2026-11-28  
**Starting Main:** `f1924abccb8d184a86758c5c54560f56f5912588`  
**Active streams reviewed:** 4  
**Catalogue:** 11 Preliminary / 0 Published  
**New streams:** 0

### Work completed

#### AquaSignal — NEA 2025 groundwater coverage

Draft PR [#306](https://github.com/maisuradzee/bibmom/pull/306) refreshes stale PR #144 onto current Main. It adds a public aggregate snapshot, closed JSON Schema, regional-table validator and mutation tests. The NEA 2025 annual report describes 124 combined groundwater points (74 routine hydrogeological monitoring + 50 field-instrumental study points), 2 new automatic stations, 74 laboratory-sampling points and 681 analysis-group counts, 73 surface-water parameter-coverage points, and a separate 50-point nitrate field table (30 springs, 19 boreholes, 1 household well). The source term “საყოფაცხოვრებო ჭა” is recorded as **household well**.

The eight laboratory regional rows and five nitrate regional rows are checked independently. The 124/74/50 groundwater and 238/2571/73 surface-water frames remain separate because unique-site overlap is not reported. The nitrate table is field-instrumental coverage only; it contains no sample-level nitrate concentrations, laboratory confirmation or final vulnerable-zone designation. The PDF was inspected through the browser reader; raw bytes were not obtained and SHA-256 is **NOT_COMPUTED**. The separate 2021–2025 groundwater RAR announced on 2026-11-26 remains uninspected.

PR #306 exact-head CI [46144520244](https://github.com/maisuradzee/bibmom/actions/runs/46144520244) passed **911 tests / 1 skipped**; draft validation, research index, frozen reproductions, site build and publication-boundary checks succeeded. Site build reported 0 Published / 11 Preliminary. PR remains Draft pending independent hydrogeological, laboratory and statistical review; not merged.

#### INFRA-001 — CI command and public credential preflight

Draft PR [#307](https://github.com/maisuradzee/bibmom/pull/307) is a clean-current-Main replacement for stale PR #304. It pins all named CI step bodies and adds a tracked UTF-8 text credential scanner. Run 58 self-audit fixes cover encrypted PKCS#8 keys with short final base64 lines and placeholder-looking URL credentials on non-example hosts.

PR #307 exact-head CI [46144710939](https://github.com/maisuradzee/bibmom/actions/runs/46144710939) passed **891 tests / 1 skipped**. The command contract matched all named step bodies; the scanner checked 475 tracked UTF-8 text files, skipped 3 binary/non-UTF-8 files and found no configured patterns. It remains pattern-based, does not scan Git history and is not proof that the repository is secret-free. The manifest/validator share the same public repository and are not an independent trust anchor. PR remains Draft pending independent security review; not merged.

Stale PRs #144 and #304 were closed as superseded; their commits remain in history and were not merged.

#### NOEMA-005

No new physical CPU experiment was run. Existing 330-case parallel-reduction simulation and frozen summaries passed in PR #306 CI. Existing 96-case real-thread summary with 288 timed runs passed in PR #307 CI. These are frozen-result checks, not new hardware measurements. Physical x86-64/ARM64, RSS and DRAM-counter work remains blocked on suitable hardware/access.

#### NOEMA-007

No new authorized Georgian warning-event or after-action dataset was obtained. Existing WRP 2025 and WRP 2026 action-enabler frozen reproductions passed in PR #306 CI. Operational delivery, comprehension, feasible action and after-action effectiveness remain unmeasured.

### Four-stream portfolio review

| Stream | Status | Run 58 blocker / next step |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active / Preliminary | Obtain the 2021–2025 RAR and authorized sample-level dictionary/export; after 2026-12-01 separately verify 2027 plan submission, approval and publication |
| NOEMA-005 | Active / Preliminary | Physical x86-64/ARM64, Pairwise/Binned/Exact methods, RSS/native memory and DRAM counters |
| NOEMA-007 | Active / Preliminary | Privacy-approved warning-event and after-action data with stage-specific denominators |
| INFRA-001 | Active / Engineering | Independent security review; external rollback-resistant trust anchor, encrypted off-host backup and clean-host restore |

No fifth stream was added. Catalogue remains 11 Preliminary / 0 Published. No private coordinates, person-level records, health data, credentials or restricted archive payloads were added. No Supabase project or other project database was created or used.

### Merge and deployment status

Main remains `f1924abccb8d184a86758c5c54560f56f5912588`. PR #306 and #307 have exact-head Quality CI success and are mergeable, but both remain Draft and unmerged pending independent review. No post-merge Main CI or Pages deployment is claimed. No direct commit to Main was made.

### Next priorities

1. AquaSignal: authorized RAR retrieval, archive inventory and SHA-256 after raw bytes are obtained; request the station/sample dictionary and permitted data export.
2. AquaSignal: after 2026-12-01, verify 2027 monitoring-plan submission, ministerial approval and public release separately.
3. INFRA-001: independent security review of PR #307.
4. NOEMA-005: physical x86-64/ARM64 benchmark with alternative algorithms, RSS and DRAM counters.
5. NOEMA-007: authorized event-stage and after-action aggregates.

## NOEMA — Run 57: frozen benchmark cell-matrix guard and CI command/credential preflight

**Date:** 2026-11-28  
**Starting Main:** 7fd05067097581c516ec944635ffc60f06d1fe2a  
**Main after NOEMA-005 PR #302:** a3e17a3169eb59cdbc85656d8be4dfec8d5f900c  
**Active streams reviewed:** 4  
**Catalogue:** 11 Preliminary / 0 Published  
**New streams:** 0

### Work completed

#### NOEMA-005 — exact Experiment 002 cell matrix

Merged [PR #302](https://github.com/maisuradzee/bibmom/pull/302).

- The frozen verifier now requires the exact six runner/architecture/runtime cells, unique cell IDs, 64 configurations and 192 measured runs per cell, and 48 measured runs per method.
- Correctness and diagnostic counters are bounded; speedup summaries must be finite, positive, ordered and consistent with the count of configurations beating the matching serial baseline.
- Mutation tests preserve global totals while corrupting one cell, proving that aggregate totals cannot conceal per-cell substitution.
- No benchmark values or artifacts changed. This is not a new physical-device experiment, RSS measurement or DRAM-counter result.
- Exact-head Quality CI [46139381431](https://github.com/maisuradzee/bibmom/actions/runs/46139381431): 878 passed, 1 skipped. GitHub reported mergeable=true; PR merged at Main SHA a3e17a3169eb59cdbc85656d8be4dfec8d5f900c.

#### INFRA-001 — CI command identity and public credential preflight

Current-Main Draft [PR #304](https://github.com/maisuradzee/bibmom/pull/304).

- Adds an exact-body contract for all 50 named steps in the CI workflow; the contract covers each step's command/action and other body fields, not only its display name.
- Adds regression tests for no-op replacement, changed body, duplicate, unlisted and unnamed steps.
- Adds a tracked UTF-8 text preflight for common provider token formats, complete private-key blocks, credential assignments, URL user-info, sensitive query/fragment names and credential-like path segments. Findings contain path, line and rule only; matched values are never printed.
- Exact current head d7ad3491132fe401e9a25e35f21c960fe1e2ae40, base a3e17a3169eb59cdbc85656d8be4dfec8d5f900c; Quality CI [46139730927](https://github.com/maisuradzee/bibmom/actions/runs/46139730927) succeeded: 889 passed, 1 skipped. The scanner inspected 474 tracked UTF-8 files, skipped 3 binary/non-UTF-8 files and reported no findings.
- PR #304 remains Draft pending independent security review. The manifest and validator are in the same public repository; this is a regression/review guard, not a signed trust anchor. The scanner is pattern-based, does not scan Git history and is not proof that no secret exists. No external high-water service, encrypted offsite backup, production key custody or clean-host restore is claimed.

PR #303 was closed as superseded without merge. Older CI recovery PR #291 remains unmerged and needs a current-Main review before any recovery-workflow integration.

#### AquaSignal — no new source payload

- The Decree №447 annual-plan submission-to-Minister deadline remains 2026-12-01 and had not passed on 2026-11-28.
- No new 2027 plan bytes, submission receipt, ministerial approval, official NEA RAR bytes or procurement acceptance act were obtained.
- The existing source-uninspected state remains; no non-submission, breach, water-quality or legal-compliance conclusion is inferred.

#### NOEMA-007 — no new operational dataset

- No authorized Georgian warning-event/after-action aggregates, stage-specific denominators or WRP survey-design variance/replicate-weight documentation were obtained.
- Existing 51/29/20 aggregate derivation remains a transformation of rounded global aggregates, not raw microdata, a causal result or a Georgia estimate.

### Portfolio status

| Stream | Status | Run 57 result / blocker |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active | 2026-12-01 plan deadline is upcoming; official plan, receipt, approval and annex bytes remain unverified. |
| NOEMA-005 | Active | PR #302 merged; next is physical x86-64/ARM64, representative workloads, 20+ measured repetitions, RSS/native allocation and DRAM/CPU counters. |
| NOEMA-007 | Active | No authorized Georgian warning-event dataset or survey design variance documentation. |
| INFRA-001 | Active | PR #304 Draft, exact-head CI passed; independent security review remains mandatory before merge. External trust anchor, encryption, retention and clean-host restore remain unimplemented. |

No fifth stream added. Catalogue remains 11 Preliminary / 0 Published.

### Main, CI, deployment and safety

- PR #302 exact-head Quality CI [46139381431](https://github.com/maisuradzee/bibmom/actions/runs/46139381431): SUCCESS, 878 passed, 1 skipped.
- PR #304 exact-head Quality CI [46139730927](https://github.com/maisuradzee/bibmom/actions/runs/46139730927): SUCCESS, 889 passed, 1 skipped.
- PR #304 is not merged.
- Post-merge Main Quality CI and Pages deployment for the PR #302 merge commit were not independently verified in this run. PR-level site build and publication-boundary checks passed; Pages is not described as updated.
- No new Supabase project was created and no other project's database was used. No private well coordinates, personal sampling records, WRP microdata, credentials, keys or restricted source payloads were added.

### Next priorities

1. Obtain independent security review for PR #304; do not merge solely on CI success.
2. After 2026-12-01, verify AquaSignal plan submission, ministerial approval and public release separately; obtain official annex/RAR bytes through an authorized route and hash before inspection.
3. NOEMA-005: run physical x86-64/ARM64 experiments only when hardware is available; compare Pairwise/Binned/Exact alternatives and capture RSS/native allocation and hardware DRAM counters.
4. NOEMA-007: obtain authorized Georgian warning-event/after-action aggregates and WRP survey design variance/replicate weights.
5. INFRA-001: after review, implement independent external monotonic high-water trust, encrypted off-host artifact lifecycle, retention verification and clean-host restore.

## NOEMA — Run 56: Decree 447 plan readiness and warning-to-action composition

**Date:** 2026-11-28  
**Starting Main:** `cfa02bc52ea467b8f00bcd72266bdcefe07b2eda`  
**Run 55 documentation sync:** `591f092a2f35dc151e359d53d47bbf9baccb7d2d`  
**AquaSignal research merge:** `0c2491e0f69f3049752eb634d6ce164ecd00d2d1`  
**Final research Main before this status update:** `88ff7ec9bf66eb6cf52087f8f2561f0ace866743`  
**Active streams reviewed:** 4  
**Catalogue:** 11 Preliminary / 0 Published  
**New streams:** 0

### Work completed

#### AquaSignal — NOEMA-2026-014: Decree №447 plan evidence intake

Merged [PR #297](https://github.com/maisuradzee/bibmom/pull/297), rebased after the Run 55 status merge.

- Added `noema_core/monitoring_plan_readiness.py`, a closed JSON intake schema, frozen current-state record, preliminary note and 10 deterministic tests.
- Keeps plan retrieval/inspection, SHA-256, submission to the Minister, ministerial approval, annex inspection and actual monitoring as distinct evidence states.
- Checks the five Article 5 programme categories, three Article 6 monitoring modes and selected Article 4 documentary requirements.
- Requires verified abstraction-data water-balance evidence before a claimed groundwater quantitative-status assessment.
- Output states are only `NOT_ASSESSABLE_SOURCE_UNINSPECTED`, `DOCUMENTARY_GAPS` and `READY_FOR_INDEPENDENT_REVIEW`. No legal-compliance or drinking-water safety verdict is emitted.
- **Current evidence:** the 2027 plan, submission receipt, ministerial approval and official Annex 1/2 bytes are not retrieved. Frozen status is `NOT_ASSESSABLE_SOURCE_UNINSPECTED`. The 2026-12-01 submission deadline is still upcoming as of this run; no non-submission or breach is inferred.
- Exact-head CI [run 46137343181](https://github.com/maisuradzee/bibmom/actions/runs/46137343181): **868 passed, 1 skipped**; all validation, research-index, schema, site-build and publication-boundary steps succeeded.

#### NOEMA-007 — NOEMA-2026-015: per-100 warning-to-action composition

Merged [PR #298](https://github.com/maisuradzee/bibmom/pull/298), rebased on top of AquaSignal PR #297.

- Frozen PROJWT-weighted aggregates: 80.0% warning receipt and 63.8% ability to act among warned respondents.
- Decimal arithmetic yields approximate mutually exclusive shares per 100 disaster-impacted adults: **51.0 warned and able; 29.0 warned but unable; 20.0 not warned**.
- Rounded components sum to 100.0 and agree with the UNDRR 2026-10-13 51/29/20 graphic after whole-percent rounding.
- This is a derivation from already rounded aggregate estimates, not raw-microdata reanalysis, a new survey, a causal effect, or a Georgia national estimate. No design-based confidence intervals were calculated.
- Exact-head CI [run 46137454685](https://github.com/maisuradzee/bibmom/actions/runs/46137454685): **874 passed, 1 skipped**; all validation and publication-boundary steps succeeded.

#### INFRA-001 — static security review of Draft PR #291

PR #291 remains Draft and is not merged. Static review of the v3 branch found two issues that must be addressed before an independent security review can close:

1. `validate_ci_workflow_contract.py` verifies required step IDs, `continue-on-error`, summary-gate placement and manifest equality, but does not bind each validation ID to its actual `run`/ `uses` command. Replacing a validator command with a successful no-op while retaining its ID can evade the current manifest contract and be counted as success by the aggregate gate. Add a versioned expected-command/step fingerprint contract and a regression test.
2. `_safe_public_source_url` inspects only URLs in explicit Sources sections and detects credential-like parameter names in query/fragment. It does not detect arbitrary secret values or opaque credential-like path segments and is not a full repository secret scanner. Keep the documented no-fetch/no-DNS boundary, add a dedicated secret scan, and retain independent review.

No CI recovery change was merged. No production external trust anchor, anti-rollback, encrypted staging or clean-host restore is claimed.

#### NOEMA-005 and remaining portfolio review

- No new physical x86-64/ARM64 device was available; no new hardware benchmark, RSS/native-memory or DRAM-counter result is claimed.
- Run 55's six hosted artifact cells, 384 configurations and 1,152 measured repetitions remain the latest independent artifact reproduction. No hosted threaded configuration beat its matching serial wall-time baseline (0/384).
- NOEMA-007's Georgian operational warning/after-action dataset remains unavailable. The new 51/29/20 composition is global descriptive context only.

### Portfolio status

| Stream | Status | Next step / blocker |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active | After 2026-12-01, retrieve and hash the 2027 plan, submission receipt, approval instrument and Annexes 1/2; independently review the Article 4-7 crosswalk. |
| NOEMA-005 | Active | Physical x86-64/ARM64, 20+ repetitions, representative workloads, RSS/native allocation and DRAM/CPU counters. |
| NOEMA-007 | Active | Obtain survey-design variance documentation/replicate weights and privacy-approved Georgian warning-event/after-action aggregates. |
| INFRA-001 | Active | Fix command-identity and secret-scanning gaps in Draft PR #291; obtain independent security review; then test encrypted staging, external trust anchor/anti-rollback and clean-host restore. |

Catalogue: **11 Preliminary / 0 Published**. No fifth stream added.

### Main, CI, deployment and safety

- PR #297 merged at Main SHA `0c2491e0f69f3049752eb634d6ce164ecd00d2d1`.
- PR #298 merged at Main SHA `88ff7ec9bf66eb6cf52087f8f2561f0ace866743`.
- GitHub Pages build and deployment for final research Main [run 46137522563](https://github.com/maisuradzee/bibmom/actions/runs/46137522563) succeeded.
- Post-merge Main Quality CI [run 46137682863](https://github.com/maisuradzee/bibmom/actions/runs/46137682863) succeeded: **874 passed, 1 skipped**; site build reported 0 Published / 11 Preliminary. GitHub Pages deployment [run 46137682856](https://github.com/maisuradzee/bibmom/actions/runs/46137682856) succeeded for Main SHA `ebf8e50a49f46ae3c03e2ba255f61ce582cc008a`.
- No new Supabase project was created and no other project's database was used.
- No raw WRP microdata, respondent identifiers, private well coordinates, sample-level water observations, credentials or secrets were added.

### Next run priorities

1. After 2026-12-01, verify the Georgian 2027 plan's submission, ministerial approval and public release separately.
2. Obtain official NEA report/methodology archive bytes and Annex 1/2; hash before inspecting.
3. Obtain WRP survey-design variance documentation or replicate weights before any confidence interval.
4. Conduct physical NOEMA-005 x86-64/ARM64 experiments with at least 20 measured repetitions and memory/DRAM counters.
5. Fix the two INFRA-001 static-review findings, then obtain independent security review before merge.
6. Seek authorized Georgian warning-event and after-action aggregates with stage-specific denominators.

## NOEMA — Run 55: research reproduction, source-access audit and CI resilience

**Date:** 2026-11-28  
**Starting Main:** `3a30d172be78e0b286374acd141fbcb7e9e05d26`  
**Main after research merges (before this documentation-only update):** `cfa02bc52ea467b8f00bcd72266bdcefe07b2eda`  
**Active streams reviewed:** 4  
**Catalogue:** 9 Preliminary / 0 Published  
**New streams:** 0

### Work completed

#### NOEMA-007 — warning action-enabler subgroup semantics

Merged [PR #285](https://github.com/maisuradzee/bibmom/pull/285) and [PR #292](https://github.com/maisuradzee/bibmom/pull/292).

- The WRP `CountryIncomeLevel` variable is the World Bank country-income classification at fieldwork (FY2024-25), not respondent or household personal income.
- Derived unadjusted differences from frozen PROJWT-weighted point estimates: 3 vs 1 warning channel +26.7 pp; both household plan + personal agency vs neither +56.4 pp; upper-middle vs low country-income group +27.5 pp; high vs lower-middle +24.0 pp.
- No design-based confidence intervals, effective subgroup sample sizes or causal effects were computed. These are descriptive prioritisation signals only.
- The public catalogue entry is version 1.2. Study remains Preliminary.

#### NOEMA-005 — Experiment 002 independent artifact reproduction

Merged [PR #288](https://github.com/maisuradzee/bibmom/pull/288).

- Six GitHub-hosted runner/runtime cells: x86-64 Ubuntu, ARM64 Ubuntu and ARM64 macOS, each GIL-enabled and free-threaded.
- 384 configurations / 1,152 measured runs (one warm-up, three measured repetitions).
- Run 55 independently downloaded six public artifact ZIPs and verified 6/6 ZIP SHA-256 plus 6/6 embedded JSON SHA-256.
- Recomputed all per-cell correctness, matching-serial speedup, median CPU/wall threshold counts and scalar-partial failure topology; every per-cell metric matched the frozen summary.
- Full Neumaier `(sum, correction)` state: 288/288 correctly rounded; scalar Neumaier: 252/288; worker-local `math.fsum` scalar partials: 252/288; naive scalar: 0/288.
- No threaded configuration beat its matching serial baseline (0/384). Free-threaded CPU/wall ratios show concurrent CPU use in some configurations, not wall-time speedup.
- All six legacy artifact lists were independently checked and empty after cleanup; raw native thread IDs and detailed platform build strings were absent.

**Limits:** all cells are hosted virtual runners; the workload is synthetic/cancellation-heavy; only three measured repetitions; no user-owned physical-device replication, representative scientific workload, RSS/native allocation, DRAM bandwidth, CPU-frequency or context-switch counters. Study remains Preliminary.

#### AquaSignal — source-access and statutory-deadline audit

Merged [PR #290](https://github.com/maisuradzee/bibmom/pull/290).

- The NEA's official 2026-11-26 announcement links the 2021-2025 groundwater report and nitrate-risk field methodology. The official RAR URL resolved, but the payload was served as `application/octet-stream`; this execution environment could not retrieve the bytes. No SHA-256 or annex content is claimed.
- The Folketing MOF Q199 page confirms a final-answer date of 2026-11-16; the answer PDF body remains unreviewed and its policy outcome is unknown.
- The 2027 state water-monitoring plan submission-to-Minister deadline is 2026-12-01. As of 2026-11-28 it was still upcoming. Submission, approval and public release are separate unverified states; no non-compliance inference is made.

#### INFRA-001 — fail-closed CI recovery proposal

The current-Main v3 proposal is in [Draft PR #291](https://github.com/maisuradzee/bibmom/pull/291), based on pre-catalog Main `726c9b335acf386d2dab29b005b7817b1e38d910`; it is not merged and must be rebased after this documentation update.

- 52 workflow steps: 2 fail-fast prerequisites + 48 independent validations, each with a stable ID; a closed 50-ID manifest; unconditional aggregate gate.
- Exact-head CI [run 46136022076](https://github.com/maisuradzee/bibmom/actions/runs/46136022076) passed 875 tests, 1 skipped; all 50/50 required outcomes were observed.
- The uploaded diagnostic artifact showed 51 drafts scanned, four metadata/heading-only repairs, zero remaining validation errors, zero source URL issues, and no changes to research claims, tests or frozen results. Its patch contained no source URL or credential values.
- A regression test now rejects a truncated workflow root/header.
- **Not merged:** independent security review of workflow logic, repair boundaries and diagnostic redaction is still required. No production backup/restore or external anti-rollback capability is claimed.

### Main verification

After PR #292, Main SHA was `cfa02bc52ea467b8f00bcd72266bdcefe07b2eda`.

- Main Quality CI [run 46136189253](https://github.com/maisuradzee/bibmom/actions/runs/46136189253): **858 passed, 1 skipped**.
- GitHub Pages [run 46136189284](https://github.com/maisuradzee/bibmom/actions/runs/46136189284): build and deploy jobs succeeded.
- No new Supabase project was created; no other project's database was used.
- No private well coordinates, sample-level water observations, respondent microdata, personal data, supplier bank details, credentials or secrets were added.

### Next priorities

1. After 2026-12-01, verify the Georgian 2027 monitoring-plan submission, ministerial approval and public release separately.
2. Obtain the NEA RAR through an authorized alternate route or final interactive PDF/acceptance record; hash bytes before inspection.
3. Retrieve and review the Folketing Q199 answer PDF before interpreting its policy outcome.
4. Run NOEMA-005 on controlled physical x86-64 and ARM64 systems with at least 20 measured repetitions, representative workloads, RSS/native allocation and DRAM/CPU counters.
5. For NOEMA-007, obtain design-based variance estimates/effective subgroup sample sizes and authorized operational warning-to-action data; do not infer Georgian operational effectiveness from global survey aggregates.
6. Rebase INFRA-001 onto current Main and obtain independent security review; then test encrypted staging, external trust-anchor/anti-rollback and clean-host restore.

[Full Run 55 audit](run-audits/2026-11-28-run-55.md).

---

## NOEMA — Run 54: nitrate evidence provenance and high-water write-failure atomicity

# NOEMA Run 54 — nitrate evidence provenance and high-water write-failure atomicity

**Date:** 2026-11-28  
**Starting Main:** 5c770ded936a193dc853476ad6a6d546883a0eea  
**Final Main after research merges:** cb5f3a507ea96b345c1fce98981149d356b9dabc  
**Active streams reviewed:** 4  
**Catalogue after merge:** 9 Preliminary / 0 Published

## Work completed

### AquaSignal / NOEMA-2026-006 — deep research and prototype

Added preliminary study **NOEMA-2026-013**, a public-source review of the 2026 New Zealand nitrate/preterm-birth cohort and the provenance of nitrate reference values.

Key evidence distinctions:

- WHO's 2026 consolidated drinking-water volume retains 50 mg/L as nitrate ion (NO3-); the nitrate fact sheet's assessment date is 2016, so the consolidated publication date is not a 2026 nitrate reassessment.
- Georgia Government Decree №58/2014 lists 50 mg/L as NO3- for nitrate within its Article 1 drinking-water scope; currentness and scope must be checked before compliance use.
- The Danish expert group report's corrected 2026-01-07 version recommends 6 mg/L as NO3- for drinking water. It corrected a previous NO3-/NO3-N unit confusion, and it states that only one study was suitable for its benchmark-dose modelling, using five exposure categories. This is an expert recommendation, not an enacted legal limit established by this review.
- Chambers et al. (Environmental Research, 2026; PMID 42385869; DOI 10.1016/j.envres.2026.125169) report an observational association in 735,831 New Zealand singleton births. Exposure is reported as mg/L NO3-N. The authors note residual confounding and exposure misclassification cannot be excluded. NOEMA did not reproduce the cohort analysis; its population-attributable estimate is conditional on a causal assumption.
- Greenpeace's 2026-11-03 report of an open letter by more than 80 organisations is recorded as an advocacy signal, not a WHO decision or revised guideline.
- Danish Parliament question 199 has a final answer dated 2026-11-16, but the answer PDF's substantive content was not reviewed; no policy outcome is inferred.

**Innovation:** added a typed benchmark-provenance helper that:
- compares only drinking-water matrix references;
- rejects NO3-N versus NO3- basis mismatch rather than silently converting;
- distinguishes international guidance, national regulatory text and expert recommendation;
- cannot accept a peer-reviewed study or advocacy statement as a numeric threshold;
- never emits a legal-compliance or potability decision.

Added a closed evidence register, JSON Schema, catalogue metadata, portfolio methodology/risks and CI required-file checks. No Georgian sample-level data or local exposure estimate was created.

### INFRA-001 — independent storage-failure test

Added a synthetic SQLite trigger that aborts the high-water generation upsert after BEGIN IMMEDIATE. The regression test verifies:
1. the write raises the injected error;
2. the previous generation remains unchanged after rollback;
3. after removing the trigger, retrying the exact next generation succeeds.

**Evidence status:** REPRODUCED_RESULT for a deterministic local SQLite transaction test only. It is not a power-loss, filesystem-corruption, host-compromise or remote anti-rollback test. The SQLite reference remains same-host only.

## Other streams reviewed

- **NOEMA-005:** no physical x86-64/ARM64 device, new native-memory/RSS measurement or hardware DRAM counter was available. Existing frozen raw-artifact reproduction and benchmark smoke checks ran in PR CI; no new physical experiment is claimed.
- **NOEMA-007:** no new authorised Georgian warning-event or after-action dataset was obtained. No new operational-effectiveness claim was added.
- **AquaSignal deadline watch:** Government Decree №447 requires the annual state water-monitoring plan to be submitted to the Minister by **2026-12-01**. As of 2026-11-28 the deadline had not yet passed; submission and approval were not verified. Public absence is not evidence of non-submission, and this is not the public-release deadline.

## GitHub and CI

- [PR #282](https://github.com/maisuradzee/bibmom/pull/282) merged as **8025833fa1b9f6318dcec5d83e09b63dff99adda**. Exact-head CI [46130005924](https://github.com/maisuradzee/bibmom/actions/runs/46130005924): SUCCESS, 840 passed / 1 skipped.
- [PR #283](https://github.com/maisuradzee/bibmom/pull/283) merged as **cb5f3a507ea96b345c1fce98981149d356b9dabc**. Exact-head CI [46130165759](https://github.com/maisuradzee/bibmom/actions/runs/46130165759): SUCCESS, 856 passed / 1 skipped, 51/51 steps.
- [PR #281](https://github.com/maisuradzee/bibmom/pull/281) was closed as superseded after its first CI run exposed a test-fixture type error. It was not merged; the corrected branch was recreated from the then-current Main as PR #283.
- Final Main is **cb5f3a507ea96b345c1fce98981149d356b9dabc**.
- Post-merge push-triggered Main Quality CI and GitHub Pages deployment are **not yet independently verified in this run**. The available workflow-run lookup exposes PR-triggered runs only; the final Main commit currently has no reported combined status in the connector response. Therefore Pages is not described as updated.

## Portfolio state

| Stream | Status | Next blocker |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active | Official NEA RAR/final PDF and acceptance act; Danish Q199 answer text; Georgian legal/hydrogeological review |
| NOEMA-005 | Active | Independent bare-metal x86-64/ARM64 hardware and DRAM/RSS measurement |
| NOEMA-007 | Active | Authorised warning-event and after-action aggregates |
| NOEMA-INFRA-001 | Active | External trust anchor, encrypted staging, provider retention and clean-host restore |

No fifth stream was added. NOEMA-2026-013 is a study within AquaSignal, not a new stream.

## Public-data boundary

No private well coordinates, sample identifiers, laboratory records, personal data, supplier banking/contact details, credentials or secrets were added. No Supabase project was created or modified, and no other project's database was used.

## Next priorities

1. Obtain the Danish Parliament Q199 answer PDF and review its substantive content.
2. Obtain the official NEA 2021–2025 groundwater RAR or final interactive PDF and acceptance act for T-100801; verify hashes and reuse rights.
3. After 2026-12-01, separately verify submission and approval of Georgia's 2027 state water-monitoring plan; do not infer breach from missing public evidence.
4. Verify the current legal status and scope of Decree №58/2014; obtain independent Georgian legal, toxicological and hydrogeological review.
5. Run NOEMA-005 on independent bare-metal x86-64 and ARM64 devices.
6. Obtain privacy-approved Georgian warning-event/after-action aggregates for NOEMA-007.
7. Complete INFRA-001 external high-water authority, encrypted staging and permissioned clean-host restore.

**Publication:** NOEMA-2026-013 remains Preliminary. No independent review has occurred.


---

# NOEMA — Run 53: nitrate-zone evidence crosswalk, procurement access route and frozen ARM64 re-audit

**Date:** 2026-11-28  
**Final Main:** `c0a6c5a6d46dcaf1ffa22687309f6317256e4fa6`  
**Merged PRs:** #277, #278, #279  
**Main Quality CI:** [46125953807](https://github.com/maisuradzee/bibmom/actions/runs/46125953807) — SUCCESS, 839 passed / 1 skipped  
**GitHub Pages:** [46125953795](https://github.com/maisuradzee/bibmom/actions/runs/46125953795) — build and deploy SUCCESS  
**Research catalogue:** 8 Preliminary / 0 Published  
**Portfolio:** 4 active streams; no fifth stream added

## Run 53 work

### AquaSignal — NOEMA-2026-012 (deep work)

Compared three primary evidence lanes:

1. NEAP-4 2024 monitoring report, Annex 2 activity 5.1.8, which reports groundwater nitrate-vulnerable-zone identification as implemented (100%) and attributes the work to EU technical-assistance experts.
2. Law No.1766-Vმს-XIმპ (2026-06-24), Article 37(2)(b.e), which requires the Minister to identify groundwater nitrate-polluted/risk zones and define nitrate-vulnerable zones by 2027-09-01.
3. NEA's 2026-11-26 announcement that the 2021-2025 groundwater report and nitrate field methodology were prepared.

**Inference:** these records concern the same broad subject, but available text does not prove that the historical programme deliverable and current statutory task have identical scope, geographic coverage, approval instrument or legal effect. This is an evidence-reconciliation gap, not proof of contradiction or non-compliance.

A primary procurement contract T-100801 (signed 2026-10-09) provides an alternate access route. It specifies an interactive-TOC PDF, 50 printed reports, 50 CD copies and 70 methodology booklets, with delivery within 20 calendar days (calculated date 2026-10-29) and an acceptance act. No delivery/acceptance record was verified; no breach is inferred. The contract says report text/maps are supplied by the contracting authority. Supplier contact, banking and tax details were not copied into the public repository.

Added:
- `noema_core/aquasignal_nitrate_zone_obligation.py`
- `tests/test_aquasignal_nitrate_zone_obligation.py`
- `data/noema-006/nitrate-zone-obligation-crosswalk-2026-11-28.json`
- `data/noema-006/nitrate-zone-obligation-crosswalk.schema.json`
- `research/preprints/NOEMA-2026-012-georgia-groundwater-nitrate-obligation-crosswalk.md`
- preliminary catalogue and AquaSignal portfolio metadata.

The gate is metadata-only. It can reach `READY_FOR_INDEPENDENT_LEGAL_REVIEW`, never `COMPLIANT` or `LEGAL_VIOLATION`. Official RAR bytes remain unavailable and unhashed; no groundwater samples, final zone map or designation instrument were obtained.

### NOEMA-005 — repeat frozen-artifact audit (small independent work)

Four hosted ARM64 ZIP artifacts from workflow run 46032894362 were downloaded and independently rechecked. This is the same frozen artifact set already reproduced in Run 45; Run 53 is a separately implemented cross-check, not new experimental data.

- 4/4 ZIP digests and 4/4 raw JSON SHA-256/byte-length pairs matched.
- 192 configurations / 576 measured runs were re-aggregated.
- Correctly rounded runs: naive 0/192; scalar Neumaier 168/192; full Neumaier state 192/192.
- CPU-time/wall-time ratio above 1.05: GIL 4/288; free-threaded 202/288.
- All per-cell median speedups remain below 1.0.

No new bare-metal x86-64/ARM64 run, RSS/native-memory measurement, DRAM hardware counter or external numerical-method review was performed.

### NOEMA-007 and INFRA-001 audit

- **NOEMA-007:** no new authorized Georgian warning-event or after-action dataset. No operational-effectiveness claim added.
- **INFRA-001:** same-UID and privileged-local-process limitations of 0700/0600 staging remain. No external high-water authority, provider retention proof, encrypted offsite backup or clean-host restore was demonstrated.

## Portfolio and PR state

- AquaSignal, NOEMA-005, NOEMA-007 and INFRA-001 remain active.
- No new fifth stream.
- PRs #277, #278 and #279 were merged after exact-head CI and mergeability checks.
- 40 unrelated open PRs remain; open Issues: 0. Stale CI recovery PRs #252, #251 and #246 were not merged or closed because they require current-Main refresh and separate review.
- No private well coordinates, sample-level data, personal/supplier contact details, bank data or secrets were added. No Supabase project or external database was created or used.

## Next priorities

1. After 2026-12-01, separately verify whether the 2027 state water-monitoring plan was submitted/approved; absence of public evidence must not be treated as proof of non-submission.
2. Obtain the official NEA RAR or final interactive PDF and acceptance act for T-100801; hash each received file and verify reuse terms before extracting data.
3. Obtain final groundwater nitrate-zone maps and formal approval instrument; obtain independent Georgian legal and hydrogeological review.
4. Repeat NOEMA-005 on independent bare-metal x86-64 and ARM64 devices with Pairwise/Exact methods, RSS/native memory and DRAM counters.
5. Obtain privacy-approved Georgian warning-event/after-action aggregates for NOEMA-007.
6. Complete INFRA-001 external high-water authority, encrypted staging and permissioned clean-host restore design.

---

# NOEMA — Run 52: raw-derived benchmark verification and groundwater readiness gate

- **Updated:** 2026-11-28.
- **Verified Main SHA before this status-only update:** `29994967d4669b340c1fd79e8947f4ee9d4530bd`.
- **NOEMA-005 PR #273 merged:** [recompute Run 51 derived metrics from raw samples](https://github.com/maisuradzee/bibmom/pull/273), merge commit `d842a8cf19862044653f5c8bc4058073942c27eb`. Exact-head push CI [46122507698](https://github.com/maisuradzee/bibmom/actions/runs/46122507698) and PR CI [46122514227](https://github.com/maisuradzee/bibmom/actions/runs/46122514227) succeeded. Post-merge Main Quality CI [46122724423](https://github.com/maisuradzee/bibmom/actions/runs/46122724423) and Pages deployment [46122724364](https://github.com/maisuradzee/bibmom/actions/runs/46122724364) succeeded on the merge SHA.
- **AquaSignal PR #275 merged:** [NOEMA-2026-011 groundwater quantitative-status readiness](https://github.com/maisuradzee/bibmom/pull/275), merge commit `29994967d4669b340c1fd79e8947f4ee9d4530bd`. Exact-head push CI [46122798976](https://github.com/maisuradzee/bibmom/actions/runs/46122798976) and PR CI [46122841801](https://github.com/maisuradzee/bibmom/actions/runs/46122841801) succeeded. PR #274 was closed as superseded without merge after its base became stale.
- **NOEMA-005 finding:** the Run 51 verifier now recomputes medians from five raw samples, speedup against the same-layout serial Neumaier baseline, and effective input-scan GiB/s from input bytes and median wall time. It rejects tampered derived values, malformed/nonpositive timing samples, invalid correctness counts and impossible thread-count ranges. The frozen result still represents one KVM-virtualized x86-64 host (Intel Xeon Platinum 8573C) with a four-CPU cgroup quota; no new physical device or independent second-host experiment was performed. Effective input-scan throughput is not a hardware DRAM counter.
- **AquaSignal / NOEMA-2026-011:** official Matsne Decree №447 Article 7(1) uses hydrogeological units until groundwater bodies are designated; Article 7(2) makes an authority-prepared water balance based on abstraction data a prerequisite to the recharge/abstraction balance assessment for quantitative status. The new metadata-only gate returns blocked states or `PREREQUISITES_MET_REQUIRES_AUTHORITY_ASSESSMENT`; it never assigns good/poor status and always requires authority review. Primary source: https://matsne.gov.ge/ka/document/view/7000572.
- **Annex evidence boundary:** Legali.ge's Annex 2 transcription is retained only as `SECONDARY_TRANSCRIPTION_ONLY`. The official Matsne attachment is listed as a 46,049-byte DOCX, but its bytes were not retrieved or hashed. No Annex frequency or sampling method is encoded as an operational rule. No official groundwater water-balance record or sample-level data were obtained.
- **INFRA-001 audit:** PR #272's verified-byte staging is now integrated with the local SQLite restore consumer. Its 0700/0600 staging permissions reduce access by other UIDs but do not isolate against same-UID processes or privileged local actors. This remains same-host reference integration; encryption, secure erasure, external anti-rollback, provider retention and clean-host recovery remain unimplemented.
- **NOEMA-007 audit:** no new authorized Georgian operational warning-event or after-action dataset was obtained; no new operational-effectiveness claim is made.
- **Final Main Quality CI after PR #275:** [46122901289](https://github.com/maisuradzee/bibmom/actions/runs/46122901289) — SUCCESS on `29994967d4669b340c1fd79e8947f4ee9d4530bd`; **828 Python tests passed, 1 skipped**. Site build verified 0 Published, 7 Preliminary and 7 generated HTML pages.
- **Final Pages deployment after PR #275:** [46122901297](https://github.com/maisuradzee/bibmom/actions/runs/46122901297) — build and deploy SUCCESS for the same Main SHA.
- **Portfolio:** four independent active streams remain AquaSignal / NOEMA-2026-006, NOEMA-005, NOEMA-007 and INFRA-001. No fifth stream was added. Catalogue contains **7 Preliminary, 0 Published**; NOEMA-2026-011 is a new study within AquaSignal, not a new stream.
- **GitHub state before this status-only PR:** 40 open PRs, 0 open issues. Legacy recovery PRs #252, #251 and #246 remain stale/unmergeable and were not merged; independent security review remains required.
- **Public-data boundary:** no private water-balance records, abstraction volumes, sample-level observations, personal well-owner identifiers, exact private coordinates, raw survey respondents, secrets or private annex bytes were added. No Supabase project was created or modified; no other project's database was used.

---

# NOEMA — მიმდინარე პროექტის მდგომარეობა

## Run 49 — AquaSignal nitrate/nitrite boundary and INFRA verified-artifact staging

- **Updated:** 2026-11-28.
- **Verified Main SHA:** `c1d2b0636cb7f433e9a5a3dc409b7fc87704a118`.
- **Merged research PR #265:** [AquaSignal nitrate/nitrite crosswalk](https://github.com/maisuradzee/bibmom/pull/265), merge commit `997fe84f3517b83391542318a28ca3918e04677c`. Exact-head push CI [46111385871](https://github.com/maisuradzee/bibmom/actions/runs/46111385871) and PR CI [46111389274](https://github.com/maisuradzee/bibmom/actions/runs/46111389274) succeeded. Main CI [46111461081](https://github.com/maisuradzee/bibmom/actions/runs/46111461081) and Pages deployment [46111461073](https://github.com/maisuradzee/bibmom/actions/runs/46111461073) succeeded.
- **Merged engineering PR #266:** [INFRA-001 verified artifact staging](https://github.com/maisuradzee/bibmom/pull/266), merge commit `c1d2b0636cb7f433e9a5a3dc409b7fc87704a118`. Exact-head push CI [46111601638](https://github.com/maisuradzee/bibmom/actions/runs/46111601638) and PR CI [46111605101](https://github.com/maisuradzee/bibmom/actions/runs/46111605101) succeeded; Python suite: 793 passed, 1 skipped. Main CI [46111676218](https://github.com/maisuradzee/bibmom/actions/runs/46111676218) passed 793 tests with 1 skipped. Pages deployment [46111676232](https://github.com/maisuradzee/bibmom/actions/runs/46111676232) succeeded for this Main SHA.
- **AquaSignal / NOEMA-2026-009:** added WHO 2026 nitrate/nitrite and Georgian Decree №58/2014 crosswalk. WHO guidance: 50 mg/L as NO3-, 3 mg/L as NO2-, combined same-drinking-water-sample ratio. Georgian Decree №58/2014: nitrate 50 mg/L with short-term limiting sign; nitrite 0.2 mg/L with long-term limiting sign; Article 2(21) refers to chemicals sharing the same limiting sign. The interaction is recorded as an inference requiring independent Georgian legal review, not a local compliance rule. Catalogue: 5 Preliminary, 0 Published.
- **AquaSignal implementation:** Decimal nitrite basis conversion (rounded WHO factor 0.304) and WHO-only ratio helper; requires one pseudonymous sample ID, timezone-aware timestamp, drinking-water matrix, mg/L and native ion bases. No Georgian sample data, potability result, exposure estimate or operational alert was created.
- **INFRA-001 implementation:** open_verified_artifact() copies one opened regular-file descriptor into an anonymous TemporaryFile while hashing, verifies exact length/digest and before/after descriptor metadata, and returns the rewound staged handle. During-hash path replacement fails closed; replacement or in-place source mutation after verification cannot alter the staged copy. The restore consumer is not yet wired to this API; TemporaryFile may be disk-backed and is not encryption or secure erase.
- **CI correction:** the first PR #266 head failed one test because the test expected a path replacement during hashing to succeed. The observed implementation correctly failed closed; the test was corrected to assert that behavior. The final exact-head SHA `d820b2807bdddfd41e2559b5041ceb2949552085` passed both push and PR CI.
- **NOEMA-005:** frozen hosted-result reproduction and runtime/memory smoke checks passed in CI; no new physical x86-64 or ARM64 device experiment was performed.
- **NOEMA-007:** no new authorized Georgian operational warning-event or after-action dataset was obtained; no operational effectiveness claim is made.
- **AquaSignal data blocker:** NEA 2021–2025 groundwater RAR remains linked but not extracted/hashed; no paired Georgian nitrate/nitrite sample-level laboratory data, LOD/LOQ or QA/QC were available.
- **Portfolio:** four independent active streams remain AquaSignal / NOEMA-2026-006, NOEMA-005, NOEMA-007 and INFRA-001. No fifth stream added.
- **GitHub state:** 40 open PRs, 0 open issues. PRs #252, #251 and #246 remain stale/unmergeable against current Main and were not merged; refresh and independent security review are still required.
- **Public-data boundary:** no sample records, personal identifiers, exact private coordinates, private well-register data, secrets, provider credentials or Supabase changes were added. No new Supabase project or other project's database was used.

---

## Previous verified status snapshot (Run 48)

- **განახლდა:** 2026-11-28 (Run 48 final — Georgia warning-authority crosswalk and backup path-binding hardening).
- **საცავი:** https://github.com/maisuradzee/bibmom
- **Verified Main SHA before this status-only update:** `4da99b1ae3eda2b9a6b915cd40a0060e2b9c13a9`.
- **Run 48 / NOEMA-007:** PR [#262](https://github.com/maisuradzee/bibmom/pull/262) merged as `d8df7bfade2b9ce2d392576e30691106b6175cce`; exact-head push CI [46107082587](https://github.com/maisuradzee/bibmom/actions/runs/46107082587) and PR CI [46107085468](https://github.com/maisuradzee/bibmom/actions/runs/46107085468) succeeded. Main CI [46107155252](https://github.com/maisuradzee/bibmom/actions/runs/46107155252) passed 764 tests; Pages deployment [46107155134](https://github.com/maisuradzee/bibmom/actions/runs/46107155134) succeeded on that merge SHA.
- **Run 48 / INFRA-001:** PR [#263](https://github.com/maisuradzee/bibmom/pull/263) merged as `4da99b1ae3eda2b9a6b915cd40a0060e2b9c13a9`; exact-head Quality CI [46107271580](https://github.com/maisuradzee/bibmom/actions/runs/46107271580) succeeded with 766 tests (one skipped). The verifier now checks that the final path still names the opened inode after hashing; post-return TOCTOU remains.
- **Final Main Quality CI:** [46107334582](https://github.com/maisuradzee/bibmom/actions/runs/46107334582) — SUCCESS on `4da99b1ae3eda2b9a6b915cd40a0060e2b9c13a9`, 766 tests passed, one skipped.
- **Final Main Pages deployment:** [46107334597](https://github.com/maisuradzee/bibmom/actions/runs/46107334597) — build/deploy SUCCESS for `4da99b1ae3eda2b9a6b915cd40a0060e2b9c13a9`; https://maisuradzee.github.io/bibmom/.
- **INFRA-001 recovery proposal PRs:** #252, #251 and #246 remain open/unmerged and stale against Main. PR #252 is the most complete fail-closed CI-recovery proposal, but it still requires current-Main refresh and independent security review. The local backup path-binding fix in #263 does not make off-host recovery production-ready.
- **აქტიური პორტფელი:** ოთხივე ნაკადი აქტიურია — AquaSignal / NOEMA-2026-006, NOEMA-005, NOEMA-007 და INFRA-001.
- **კვლევის კატალოგი:** 4 Preliminary, 0 Published. Run 48 NOEMA-007 crosswalk remains a draft; no research item was promoted to Published.
- **GitHub state at audit:** 40 open PRs, 0 open issues. Legacy drafts are not treated as completed work.

## Run 38 — ექვსი hosted benchmark cell, ახალი ქართული groundwater access lead და მონაცემთა სანდოობის კონტროლები

### NOEMA-005 — REPRODUCED RESULT (preliminary)
- Experiment 002: CPython 3.14.10 GIL-enabled/free-threaded × x86-64 Ubuntu, ARM64 Ubuntu და ARM64 macOS.
- 6 cells × 64 configurations × 3 repetitions = 1,152 measured runs; თითო მეთოდზე 288 run.
- სწორად დამრგვალებული: naive scalar 0/288; scalar Neumaier 252/288; full Neumaier state 288/288; worker-local math.fsum scalar partials 252/288.
- Scalar Neumaier და worker-local fsum ერთსა და იმავე deterministic grouped-cancellation/contiguous partition-ში (2 და 8 workers) კარგავს residual-ს; full compensation state ამ stress-test-ში ინარჩუნებს სიზუსტეს.
- არცერთმა 384 threaded configuration-მა შესაბამის serial baseline-ს არ აჯობა. Free-threaded CPU/wall ratio >1.05 იყო 34–36/48 configurations/method; GIL-enabled 0/48. CPU concurrency არ უდრის wall-time speedup-ს.
- ექვსი ახალი artifact ZIP და report JSON SHA-256-ით გადამოწმდა; raw native thread IDs და დეტალური host-build strings sanitizer-მა ამოიღო. PR #200-ის cleanup-მა ექვსი ძველი unsanitized artifact წაშალა და GitHub-მა მათი artifact list-ები ცარიელად დაადასტურა.
- Frozen aggregate: `data/noema-005/experiment-002-summary.json`; reproduction: `scripts/reproduce_noema005_experiment_002.py`. შედეგი რჩება Preliminary; hosted synthetic runs არ არის physical x86/ARM replication.

### AquaSignal — ახალი ოფიციალური groundwater source lead
- NEA-ს 2026-11-26 განცხადება ადასტურებს 2021–2025 მიწისქვეშა მტკნარი სასმელი წყლების ჰიდროგეოლოგიური ანგარიშისა და ნიტრატების რისკის საველე მეთოდოლოგიის მომზადებას; მითითებულია საჯარო RAR archive.
- RAR არ ჩამოტვირთულა/არ გახსნილა; sample count, station count, nitrate values, thresholds, site coordinates და reuse terms უცნობია. წყარო metadata-only Draft-ია.
- 2026-06-24 კანონი ადგენს 2027-09-01 milestone-ებს; მეთოდოლოგიის მომზადება არ ამტკიცებს ფორმალურ დამტკიცებას ან ზონების იდენტიფიკაციის დასრულებას.
- PR #202-ით merged strict canonical event JSON parsing; ეს მონაცემთა ინტერპრეტაციის კონტროლია და არა ციფრული ხელმოწერა.

### NOEMA-007 — no-update / blocker
- ახალი ავტორიზებული ქართული alert-to-action ოპერაციული მონაცემები არ მიღებულა. WMO cross-country შედეგები დარჩა კონტექსტად და არა საქართველოს ეფექტიანობის ან მიზეზშედეგობრივი მტკიცებულებად.

### INFRA-001 — engineering hardening, production recovery ჯერ არ დადასტურებულა
- AquaSignal event payload parser/64 KiB bound, NOEMA-005 public-artifact sanitizer/cleanup და INFRA-001 backup-manifest depth limit აუმჯობესებს მონაცემთა სანდოობასა და საჯარო evidence boundary-ს.
- Offsite backup, დამოუკიდებელი key custody, recovery owner, high-water authority და clean-host restore კვლავ დაუდასტურებელია.

### PR / CI
- PR #200 — merged; exact-head Quality 534 tests, x86-64/ARM64 workflows და cleanup SUCCESS.
- PR #202 — merged; exact-head Quality 539 tests და CPU workflow SUCCESS.
- PR #204 — merged; exact-head Quality 544 tests და site build SUCCESS.
- PR #205 — merged; 64 KiB UTF-8 event payload limit, exact-head Quality CI SUCCESS.
- PR #206 — merged; backup-manifest JSON nesting depth limit, exact-head Quality CI SUCCESS.
- PR #207 — merged; CPU benchmark workflow now runs on relevant PR paths only; exact-head Quality/CPU CI SUCCESS.
- PR #196/#201/#203 დაიხურა, როგორც rebased PR-ებით superseded; PR #197/#198/#199-ის commits PR #200-ის merge-ში მოხვდა.
- Run38 documentation/frozen-result synchronization PR #208-ის rebase ვერსია მიმდინარეა; Main-ში პირდაპირი commit არ შესრულებულა.

### შეზღუდვები და შემდეგი პრიორიტეტები
1. NEA RAR-ის ავტორიზებული მიღება, SHA-256, file inventory, data dictionary, station/sample denominators და reuse review.
2. NOEMA-005-ის independent numerical-method review; ფიზიკური x86-64/ARM64 ≥20 repetitions, RSS/native allocation და DRAM bandwidth.
3. საქართველოს alert delivery/receipt/comprehension/protective-action აგრეგირებული მონაცემები.
4. INFRA-001 clean-host restore და დამოუკიდებელი trust-domain.
5. Pages განახლებულად ჩაითვალოს მხოლოდ ამ main snapshot-ზე წარმატებული deploy job-ის შემდეგ.


## Run 11 — კვლევითი მტკიცებულებების შეჯერება და აღდგენის numeric-boundary hardening

- **NOEMA-005 / Draft PR #175:** ექვსი hosted x86-64 და ოთხი hosted ARM64 report-ის cross-architecture aggregate synthesis. საერთო პროტოკოლი და input SHA-256-ები ემთხვევა; 10 report, 480 configuration და 1,440 measured run. Neumaier-state exact-reference 480/480, scalar Neumaier 420/480, naive scalar 0/480. მხოლოდ ორი x86-64 Azure free-threaded report-ის median speedup იყო 1.0-ზე მეტი; ოთხივე ARM64 report და x86-64 AWS free-threaded report 1.0-ზე დაბალია. ეს hosted synthetic, backend-dependent შედეგია და არა causal architecture effect ან ზოგადი free-threading speedup.
- **NOEMA-005 exact-head checks:** PR #175 head `5f56ae3c88f0beaa2b48872f37f455a1fc9ff181`; Quality CI [46037800793](https://github.com/maisuradzee/bibmom/actions/runs/46037800793) — 482 tests SUCCESS; actual CPU-thread workflow [46037800770](https://github.com/maisuradzee/bibmom/actions/runs/46037800770) — GIL-enabled და free-threaded jobs SUCCESS; დამატებითი Quality run [46037792528](https://github.com/maisuradzee/bibmom/actions/runs/46037792528) SUCCESS. GitHub mergeable=true/clean, მაგრამ PR რჩება Draft დამოუკიდებელი numerical review-ის გამო.
- **INFRA-001 / Draft PR #176:** finite numeric guard პორტირებულია მიმდინარე main-ზე. `restore_duration_seconds`, `data_loss_seconds`, `rpo_target_seconds` და `rto_target_seconds` მოწმდება `math.isfinite`-ით; უარყოფილია NaN, ±Infinity, ორივე boolean და ისეთი integer, რომლის finite float conversion overflow-ს იწვევს. Exact-head Quality CI [46037806779](https://github.com/maisuradzee/bibmom/actions/runs/46037806779) — 473 tests SUCCESS; დამატებითი push CI [46037798077](https://github.com/maisuradzee/bibmom/actions/runs/46037798077) SUCCESS. GitHub mergeable=true/clean, მაგრამ PR რჩება Draft დამოუკიდებელი security review-ის გამო.
- **AquaSignal:** WHO-ს 2026-11-19 fact sheet-ის reference years ცალ-ცალკეა შენარჩუნებული: 1.7 მილიარდი ადამიანი 2022 წელს იყენებდა ფეკალური დაბინძურების მქონე წყაროს; safely managed drinking-water coverage 2024 წელს 74% იყო; დაახლოებით 505,000 წლიური დიარეით სიკვდილი WHO-ს შეფასებაა. ეს არ არის საქართველოს prevalence estimate. NEA 2021–2025 RAR-ის payload კვლავ მიუწვდომელია ამ გარემოში; მისი შიგთავსი/ლიცენზია არ არის ნავარაუდევი.
- **AquaSignal / Draft PR #178:** ოფიციალური სახელმწიფო შესყიდვების ხელშეკრულება T-100801 (NAT260019441) ადასტურებს 50 ბეჭდურ ანგარიშს, საბოლოო ინტერაქტიული სარჩევის PDF-ის მომზადებას, 50 CD-ს და 70 ნიტრატების მეთოდოლოგიის ბროშურას. ეს ქმნის NEA-სგან საბოლოო PDF-ის/საჯარო გაცნობის მოთხოვნის ოფიციალურ გზას, მაგრამ არ ადასტურებს საჯარო ჩამოტვირთვას, დასრულებულ მიწოდებას, CD-ის ზუსტ შიგთავსს ან reuse უფლებას. PR შეიცავს მხოლოდ საჯარო კონტრაქტის მეტამონაცემს და არა მიმწოდებლის პირად საკონტაქტო/საბანკო მონაცემებს.
- **NOEMA-007:** WRP 2025-ის pinned Parquet source commit შენარჩუნებულია, მაგრამ 7,070,416-byte payload ვერ იქნა მიღებული UTF-8-only GitHub fetch გზით. NOEMA-ს დამოუკიდებელი aggregate reproduction, local Parquet SHA-256 ან საქართველოს ოპერაციული warning-effectiveness შედეგი არ არსებობს. საქართველოს warning-question base 99 რჩება source ranking threshold 100-ზე ქვემოთ.
- **INFRA-001 evidence boundary:** finite-number guard არის ადგილობრივი validation fix. არც provider, production key, offsite trust-domain, external high-water authority ან clean-host restore არ გამოყენებულა/არ ჩატარებულა. RFC 8259 §6 JSON number grammar-იდან NaN/Infinity-ს გამორიცხავს; Python-ის default decoder ამ tokens-ს extension-ად იღებს.
- **Portfolio synchronization:** PR #177 exact-head CI-ის შემდეგ გაერთიანდა commit `ce1184eaab9e0664548b2716064d2924b76ab79b`-ში; ოთხივე stream-ის source metadata, status_detail და next steps main-შია. Merge commit-ზე Quality CI და Pages deploy წარმატებულია.

### Run 11-ის შეზღუდვები და შემდეგი ნაბიჯები

1. NOEMA-005: კონტროლირებული ფიზიკური x86-64/ARM64 host-ები, მინიმუმ 20 repetition/configuration, RSS/native allocation და DRAM bandwidth.
2. AquaSignal: NEA-სგან checksum-იანი ალტერნატიული RAR/HTTPS მიწოდება, sample-level data dictionary და reuse პირობები; NFA potable-water denominator ცალკე.
3. NOEMA-007: WRP Parquet-ის binary retrieval approved path-ით და დამოუკიდებელი aggregate reproduction; შემდეგ საქართველოს authorized event-level/after-action aggregates.
4. INFRA-001: დამოუკიდებელი recovery owner, security review, key custody, external high-water trust-domain და clean-host restore.
5. Draft PR-ები არ გადავიდეს Published სტატუსში დამოუკიდებელი დარგობრივი/სარედაქციო რეცენზიის გარეშე.

## Run 32 — გლობალური წყლის ზიანისა და გაფრთხილებიდან მოქმედებამდე არსებული ხარვეზის კვლევა

- **PR #162** გაერთიანდა exact head ed63d7451207ec0c86ea1096e95dfb8a6130a9cf-ზე, merge commit c37d8bf08279df7420fa1a27b9d549c02e0584a4. Exact-head Quality CI 46028240754 და CPU-thread workflow 46028240768 წარმატებული იყო; mergeable=true და საჯარო შინაარსი შემოწმდა. Post-merge main Quality CI 46028448316 — 457 tests SUCCESS; Pages build/deploy 46028448436 SUCCESS.
- **AquaSignal / Draft PR #166:** დაემატა LRF World Risk Poll 2025-ის 13%-იანი თვითრეპორტირებული drinking-water harm სიგნალის წყაროებზე დაფუძნებული კვლევითი ჩანაწერი. ჩანაწერი განმარტავს WP22443-ის code 1 + code 3 წესს, PROJWT-ის გამოყენებას, CC BY-SA 4.0 ლიცენზიას და peer-reviewed source-to-point-of-use ლიტერატურას. ეს არის source-published survey result და არა NOEMA-ს დამოუკიდებელი გამეორება, ლაბორატორიული დაბინძურების მტკიცებულება ან საქართველოს prevalence estimate. Exact-head Quality CI 46029419068 SUCCESS; PR Draft და mergeable=true.
- **NOEMA-007 / Draft PR #167:** დაემატა WRP 2025 warning-to-action კვლევითი ჩანაწერი. წყაროს ანგარიშში 80.0% warning receipt და 35.8% unable-to-act სხვადასხვა ბაზებზეა: 24,249 warning-question respondents და 16,996 action-question respondents. საქართველოს warning-question base არის 99, ანგარიშის 100-პირიან country-ranking threshold-ზე ნაკლები; ამიტომ robust national ranking ან ოპერაციული ეფექტიანობის მტკიცება არ კეთდება. Peer-reviewed 2026 warning-response და risk-communication მიმოხილვები დაემატა. Exact-head Quality CI 46029506881 SUCCESS; PR Draft და mergeable=true.
- **NOEMA-005:** ოთხივე აქტიური ნაკადის აუდიტი შესრულდა. ახალი ფიზიკური x86-64/ARM64 ექსპერიმენტი არ ჩატარებულა. PR #165-ის წინა ექვსი hosted artifact hash შემოწმება ძალაში რჩება მხოლოდ მითითებული artifact-ებისთვის; PR ახლა main-ს ჩამორჩება და mergeable=false.
- **INFRA-001:** PR #163-ის non-finite restore-measurement guard-ის exact-head Quality CI 46024546433 წარმატებული იყო, მაგრამ PR base ჩამორჩება მიმდინარე main-ს და mergeable=false. დამოუკიდებელი security review, recovery owner, production key custody, offsite trust-domain და clean-host restore კვლავ არ არსებობს.
- **ძველი Draft PR-ები:** #156, #157, #158, #163, #164 და #165 მიმდინარე main-ს ჩამორჩება და GitHub-ის მიხედვით mergeable=false; მათი განახლება და exact-head CI ხელახლა გაშვება აუცილებელია. არცერთი არ გაერთიანებულა.
- **კვლევის სტატუსი:** data/research.json უცვლელია — 1 Preliminary, 0 Published. PR #166/#167-ის ფაილები research/drafts-შია და Pages build მათ არ აქვეყნებს.
- **უსაფრთხოება:** WRP respondent-level ჩანაწერები არ ჩამოტვირთულა/არ დამატებულა NOEMA-ს საცავში; პირადი/სამედიცინო/ოჯახის/ზუსტი კერძო მდებარეობის მონაცემი არ დამატებულა. Supabase პროექტი არ შექმნილა და სხვა პროექტის ბაზა არ გამოყენებულა.

### კვლევითი დასკვნა

- **AquaSignal:** 13% არის გლობალური თვითრეპორტირებული ზიანის სიგნალი. იგი ვერ ადგენს წყლის ხარისხს, კონკრეტულ დამაბინძურებელს ან მიზეზობრივ კავშირს. საჭიროა დამოუკიდებელი NOEMA reproduction და NEA/NFA-ს ავტორიზებული sample-level მონაცემები.
- **NOEMA-007:** warning receipt არ უდრის comprehension-ს, feasible action-ს ან verified protective action-ს. საქართველოს n=99 warning-question base არ იძლევა ანგარიშის ranking threshold-ის დაკმაყოფილებას. საჭიროა event-level delivery/acknowledgement/after-action მონაცემები.
- **NOEMA-005:** hosted runner-ების შედეგები ვერ ანაცვლებს დამოუკიდებელ ფიზიკურ x86-64/ARM64 replication-ს.
- **INFRA-001:** local validation ვერ ადასტურებს production disaster-recovery მზადყოფნას.

### შემდეგი პრიორიტეტები

1. დამოუკიდებლად გაიმეოროს WRP 2025 WP22443 და warning/action აგრეგატები pinned Parquet commit/blob/hash-ით; მხოლოდ aggregate outputs შეინახოს.
2. მიიღოს NEA 2021–2025 RAR და NEA122 payload ოფიციალური/ავტორიზებული გზით; NFA potable-water sample denominator ცალკე შეინარჩუნოს.
3. მიიღოს საქართველოს warning-event და after-action აგრეგირებული მონაცემები და წინასწარ დაარეგისტრიროს last-mile survey.
4. განაახლოს PR #163/#164/#165 და #156/#157/#158 მიმდინარე main-ზე; rerun exact-head CI და მოითხოვოს დამოუკიდებელი security/GIS/DRR/numerical review.
5. NOEMA-005-ზე ჩაატაროს ფიზიკური x86-64/ARM64 20+ გამეორებით; INFRA-001-ზე მოამზადოს permissioned clean-host restore.

- **Run 32 audit file:** docs/run-audits/2026-11-27-run-32.md
- **Portfolio:** data/research-portfolio.json განახლებულია ოთხივე ნაკადის წყაროებით, ბლოკერებითა და შემდეგი ნაბიჯებით.



## Run 30 — post-merge synchronization

- PR #161 merged as `fdfa25db97534632161e90c0a2fe768cb0c69e9c` after exact-head Quality CI [46014537233](https://github.com/maisuradzee/bibmom/actions/runs/46014537233) and [46014494741](https://github.com/maisuradzee/bibmom/actions/runs/46014494741) SUCCESS, both CPU-thread jobs [46014537203](https://github.com/maisuradzee/bibmom/actions/runs/46014537203) SUCCESS, mergeable=true and public-boundary review.
- Post-merge main Quality CI [46014645053](https://github.com/maisuradzee/bibmom/actions/runs/46014645053) — SUCCESS (457 tests, site build and publication-boundary checks); Pages build/deploy [46014645110](https://github.com/maisuradzee/bibmom/actions/runs/46014645110) — SUCCESS.
- PRs #155–#159 use merge base `2852b7b5ee3fa7470ebc9c3eda339fc0e6235eda`, two commits behind current main. Current GitHub mergeability: #155=true, #156=true, #157=true, #158=false, #159=true. All remain Draft; #156/#159 exact-head checks passed, but rebase/refresh and exact-head revalidation are still preferred before merge so the final reviewed head includes current main changes. No research PR is merged without independent review.
- Main currently has 33 open PRs and 0 open Issues. The research catalogue remains 1 Preliminary / 0 Published. No research PR was merged or promoted to Published in this synchronization.


## Run 30 — evidence integrity, URL metadata და პორტფელის აუდიტი (2026-11-27)

- **PR #160:** Run 29 audit/portfolio ცვლილებები გაერთიანდა exact head `5e44b336ac1cab350db9742b91a784f853933c32`-ზე, merge commit `a14884ca65887b6c324d4e9968b5796362b30503`. PR-ის Quality CI და ორივე CPU-thread job წარმატებული იყო; mergeable=true და საჯარო შინაარსი შემოწმებული იყო. Post-merge main Quality CI [46013610873](https://github.com/maisuradzee/bibmom/actions/runs/46013610873) და Pages build/deploy [46013610962](https://github.com/maisuradzee/bibmom/actions/runs/46013610962) წარმატებულია.
- **NOEMA-005 / PR #159 (Run 31-ში superseded by PR #165):** ექვსი hosted artifact (სამი GIL-enabled/free-threaded workflow pair, 48 კონფიგურაცია × 3 გამეორება თითო artifact-ში; სულ 864 timed repetition) შენარჩუნებულია sanitized ფორმით. Run 30-ში ექვსივე ორიგინალი Actions ZIP და თითოეული ZIP-ის source JSON SHA-256 დამოუკიდებლად შევადარე manifest-ს — 6/6 ZIP და 6/6 source-report hash დაემთხვა. ორი free-threaded snapshot-ის ძველი Base64 დაზიანების გარდა, exact-head validation-მა მესამე, GIL-enabled Run 46011557117 snapshot-შიც არასწორი Base64 სიგრძე გამოავლინა; იგი ორიგინალი ZIP-იდან აღდგა, regenerated gzip SHA-256 დაემთხვა manifest-ს, raw measurements არ შეცვლილა. საბოლოო head `cb25a0b4aad6a8c556cd517c4fe575e0ca0c0cd2`; Quality CI [46013707604](https://github.com/maisuradzee/bibmom/actions/runs/46013707604) და GIL/free-threaded CPU-thread workflow [46013707725](https://github.com/maisuradzee/bibmom/actions/runs/46013707725) SUCCESS. PR Draft-ია; დამოუკიდებელი numerical-method review და physical x86-64/ARM64 replication კვლავ საჭიროა.
- **NOEMA-007 / PR #156:** public source URL guard გაფართოვდა double-percent-encoded credential parameter-ებისა და 
## Run 29 — source-metadata safety და cgroup mountinfo audit (2026-11-27)

- **NOEMA-007 / PR #156:** `source_url` metadata guard ამოწმებს HTTPS URL-ის hostname-ს, უარყოფს user-info credentials-ს, ცნობილ credential-like query/fragment პარამეტრებს, control characters/whitespace-ს, არასწორ port-ს და ზედმეტ parameter count-ს. ჩვეულებრივი საჯარო კატალოგის selector-ები დაშვებულია. URL-ები არ იტვირთება და source authenticity არ მოწმდება. Head `92ded19d5040631bbb73ba09fc4ee4df70f2254d`; exact-head Quality CI [46009306236](https://github.com/maisuradzee/bibmom/actions/runs/46009306236) SUCCESS; CPU-thread workflow [46009306097](https://github.com/maisuradzee/bibmom/actions/runs/46009306097) SUCCESS; mergeable=true; Draft.
- **NOEMA-005 / PR #157:** Linux kernel mountinfo path decoder გაფართოვდა kernel `seq_escape()`-ის path character set-ზე: space, tab, newline, hash და backslash. დაემატა newline/hash და literal escaped-backslash regression checks. Head `40d5bf9617f6ee6d6fc7b1d7da1748b1af429fe0`; exact-head Quality CI [46009633734](https://github.com/maisuradzee/bibmom/actions/runs/46009633734) SUCCESS; mergeable=true; Draft. Live mount namespace და ახალი timing benchmark არ ჩატარებულა.
- **PR #165:** hosted GIL/free-threaded evidence package კვლავ Draft-ია; ამ Run 29 აუდიტში მისი სრული four-artifact reproduction და exact-head status ხელახლა არ შესრულებულა.
- **PR #158:** Run 28 portfolio/status audit კვლავ ღიაა; ამ Run 29 ცვლილებებმა main-ში არაფერი გააერთიანა.
- **AquaSignal:** NEA122 payload/API, sample-level data dictionary და reuse terms კვლავ ბლოკერია; არანაირი ახალი წყლის observation არ შემოტანილა.
- **INFRA-001:** production key custody, independent trust-domain, immutable offsite retention და clean-host restore კვლავ არ არსებობს.
- **საიტი:** main snapshot-ის ბოლო დაფიქსირებული deployment წარმატებულია; PR branch-ების ცვლილებები ჯერ გამოქვეყნებული არ არის.

სრული მეთოდოლოგია, source classification, შეზღუდვები და შემდეგი პრიორიტეტები: [Run 29 audit](run-audits/2026-11-27-run-29.md).

---

## Run 19 — exact research/engineering PR state

- **Main base snapshot:** `84512d4fa57235b06842568ef933a72b2edcd698`.
- **PR #117 — NOEMA-007 mobile-inclusive AER sampling pre-registration:** head `75abf94f3d7c9cc905415844ce60a06614699a6b`; [quality CI 45947883409](https://github.com/maisuradzee/bibmom/actions/runs/45947883409) SUCCESS; [actual CPU-thread workflow 45947883396](https://github.com/maisuradzee/bibmom/actions/runs/45947883396) both GIL-enabled and free-threaded jobs SUCCESS; GitHub mergeable=true. Draft; not merged pending independent accessibility/privacy review and a competent-authority event-review mandate.
- **PR #118 — INFRA-001 restore attestation gate:** current head `aea303043083a33846704a92fcd148ed004ec9aa`; source metadata refreshed to TUF v1.0.37 (last modified 2026-10-08). Exact-head quality CI [45948345409](https://github.com/maisuradzee/bibmom/actions/runs/45948345409) SUCCESS; exact-head CPU-thread workflow [45948345376](https://github.com/maisuradzee/bibmom/actions/runs/45948345376) — GIL-enabled and free-threaded jobs SUCCESS. GitHub mergeable=true. Draft; not merged pending independent security review, recovery-owner assignment and a permissioned clean-host restore drill.
- **Superseded drafts:** PR #115 closed in favor of #117; PR #116 closed in favor of #118. Their replacement branches were recreated from the current main base; no code was merged from the superseded drafts.
- **Open PRs at this snapshot:** 19 research/engineering PRs plus status/audit PR #119 (20 total); **open Issues:** 0. Research catalogue remains 1 Preliminary / 0 Published.
- **Deployment:** neither research PR was merged; no Pages deployment is claimed for either PR branch. Latest verified Pages deployment remains the c507a91 main snapshot above.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs/worker/workflow/scheduler/supervisor/service |
| DISCOVERY · RESEARCH · INNOVATION | ერთიანი სამუშაო მოდელი | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-005 numerical reduction | active / preliminary | PR #87-ის ორი 96 MiB KVM raw JSON ანგარიში დამოუკიდებლად გადაითვალა run 19-ში; source SHA და cgroup პარამეტრები ემთხვევა. Neumaier-state median speedup ორ გაშვებას შორის 12.2–17.5%-ით იცვლება worker-ის მიხედვით; ერთი virtualized x86-64 host, 4-CPU quota. ფიზიკური hardware და representative workload ჯერ არ არის. |
| NOEMA-006 AquaSignal | active / prototype | Main-ში NEA122 catalogue metadata და NEA 2021–2025 RAR direct URL; PR #108-ში Article 32(3) NEA data-request route, Article 31(3) NFA role და Resolution No.424 registry boundary. Archive და sample-level payload კვლავ უცნობია; PR #108 Draft-ია. |
| NOEMA-007 Last-Mile Action Gap | active / draft | PR #112 retains the mobility/AER finding-register proposal; PR #117 adds a pre-registered sampling contract and semantic validator for distinct resident/time-location/partner/service-point/endpoint frames, probability-only population estimates and separate endpoint/person denominators. Exact-head quality CI 45947883409 and both CPU-thread jobs 45947883396 SUCCESS. Synthetic fixtures only; no Georgian event/field pilot. |
| NOEMA-INFRA-001 reliability | active / engineering | Main retains local manifest/hash/signature verification; PR #101 is the single-host high-water reference model; PR #118 adds a strict restore-attestation contract and distinguishes local round-trip from offsite clean-host completeness. Current TUF v1.0.37 head passed exact-head quality CI 45948345409 and both CPU jobs in 45948345376. No provider, external high-water authority or clean-host restore is deployed. |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; Draft კვლევები არ არის Published. |
| Main quality CI | Last verified SUCCESS | run 45946337600 — exact main snapshot c507a91a213435cf6992abf37c233426882cb973; later current main 84512d4fa57235b06842568ef933a72b2edcd698 is not independently verified in this run. |
| GitHub Pages | Last verified DEPLOYED | run 45946337647 — build და deploy SUCCESS exact main snapshot c507a91a213435cf6992abf37c233426882cb973-ზე; 84512d4 current main snapshot-ის deployment ჯერ დაუდასტურებელია. https://maisuradzee.github.io/bibmom/ |
| Supabase | NOEMA-სთვის ახალი პროექტი არ შექმნილა | Git-ით ვერსიაკონტროლირებადი JSON/SQLite reference architecture; სხვა პროექტის ბაზა არ გამოიყენება. |

## Run 18 — ზუსტი PR და CI მდგომარეობა

- **PR #87 — NOEMA-005 memory-backed native reduction:** head `87b4253bac196714e1637226df427a9afafc9fd3`; [quality CI 45945835133](https://github.com/maisuradzee/bibmom/actions/runs/45945835133) SUCCESS. Added two raw local KVM JSON reports and five regression tests. The exact C source blob/SHA-256 was checked against PR #87's source revision. The PR is still based on `b97b30de2c4a25127c81f3ca601203104f9421fd`, behind current main; GitHub reports `mergeable=false`. The original source-revision benchmark and CPU-thread workflows remain documented separately; no physical-host claim is made.
- **PR #112 — NOEMA-007 mobility-aware early-warning inclusion:** head `ba0839cfd76efb023a9c8e78604028eff0ea250e`; [quality CI 45945550160](https://github.com/maisuradzee/bibmom/actions/runs/45945550160) and [CPU-thread workflow 45945550181](https://github.com/maisuradzee/bibmom/actions/runs/45945550181) SUCCESS. Added the AER method note, closed public-safe finding-register schema and eight synthetic schema tests. It was based on main `0a6dbe4c4c0c18f49540f966c89d6b53b99425bf`; after PR #113 advanced main to `c507a91a213435cf6992abf37c233426882cb973`, GitHub reports `mergeable=false`. It remains Draft pending rebase, exact-head CI, independent review and a permissioned Georgian event-review mandate.
- Earlier validation failures on these branches were corrected: draft metadata/headings now satisfy the repository validator; the local benchmark reports are stored as validated JSON (not the first failed compressed representation). Final-head CI above is the authoritative result.
- **Main snapshot:** quality CI [45934655564](https://github.com/maisuradzee/bibmom/actions/runs/45934655564) and Pages build/deploy [45934655643](https://github.com/maisuradzee/bibmom/actions/runs/45934655643) SUCCESS on exact main `0a6dbe4c4c0c18f49540f966c89d6b53b99425bf`. No research PR was merged in run 18; no Pages deployment was claimed for PR branches.

## Run 17 — ზუსტი PR და CI მდგომარეობა

- **PR #108 — AquaSignal Georgia water-data access:** head `abcc7c0b913ea9f962747e1f02b653c26d0d3b03`; [quality CI 45934314385](https://github.com/maisuradzee/bibmom/actions/runs/45934314385) and [CPU-thread workflow 45934314263](https://github.com/maisuradzee/bibmom/actions/runs/45934314263) SUCCESS; original base at PR creation `2291b3bbe326ab2d8416023acdb05bfabd807e2d`; after main advanced to `cc2825245e336b170b54edd241920acd3670b30b`, branch content was synchronized with the run-17 status/audit files; GitHub reports mergeable=true. Open Draft; no request sent or personal data imported. Adds the Article 32(3) NEA request route, Article 31(3) NFA responsibility and Resolution No.424/NEA registry privacy and coverage boundaries. No request was sent and no personal data was imported.
- **PR #109 — NOEMA-007 statutory flood-risk roles:** head `0d398cb2ab3dc436a9ee4b4e56babd712c44dfe9`; [quality CI 45934321333](https://github.com/maisuradzee/bibmom/actions/runs/45934321333) and [CPU-thread workflow 45934321337](https://github.com/maisuradzee/bibmom/actions/runs/45934321337) SUCCESS; original base at PR creation `2291b3bbe326ab2d8416023acdb05bfabd807e2d`; after main advanced to `cc2825245e336b170b54edd241920acd3670b30b`, branch content was synchronized with the run-17 status/audit files; GitHub reports mergeable=true. Open Draft; no official maps or event data ingested. Adds the Article 34 role split and distinguishes flood-specific statutory maps/plans from the eleven-basin multi-hazard programme. No official maps or event data were ingested.

- Main quality CI [45934165599](https://github.com/maisuradzee/bibmom/actions/runs/45934165599) and Pages build/deploy [45934165591](https://github.com/maisuradzee/bibmom/actions/runs/45934165591) succeeded on exact main `cc2825245e336b170b54edd241920acd3670b30b`.
- Existing Draft PRs #99/#100/#101, #103/#104, #85, #91/#93 and #87/#88 use older base snapshots and require current-main refresh plus exact-head CI before merge consideration. Research PRs remain unmerged.

- **PR #110 — run-17 audit/status:** merged as `cc2825245e336b170b54edd241920acd3670b30b`; exact-head quality CI 45934072779 and CPU-thread workflow 45934072768 succeeded; post-merge main quality CI 45934165599 and Pages build/deploy 45934165591 succeeded.

## Run 16 — ზუსტი PR და CI მდგომარეობა

### ახალი კვლევითი სამუშაო

- **PR #103 — NOEMA-007 Georgia heat-health readiness:** current head `bcd205d7837f901be19098c6780fa2b56e8ddd95` (supersedes earlier `e9172ddfebb047f0ddc4295dc31e914d9dfbd8b0`); [quality CI 45928568372](https://github.com/maisuradzee/bibmom/actions/runs/45928568372) SUCCESS; [actual CPU-thread workflow 45928568397](https://github.com/maisuradzee/bibmom/actions/runs/45928568397) — GIL-enabled და free-threaded jobs SUCCESS. Draft; primary NCDC guidance, formal plan status, authorized aggregate data და independent public-health/privacy review აკლია.
- **PR #104 — NOEMA-005 ARM64 scaling analysis:** head `d7c4f4b315a3b8f5fae83961f762cf87f9bf9979`; [quality CI 45928005822](https://github.com/maisuradzee/bibmom/actions/runs/45928005822) SUCCESS. ეს არის frozen summary-ის derived analysis და არა ახალი CPU experiment. Draft; raw ARM64 reports, controlled physical hardware და external review კვლავ საჭიროა.

### არსებული ღია Draft PR-ები

- **PR #99 — NOEMA-005 hosted rerun archive:** head `6b1f3478b6d02ebf127fcfd5bc0f9dbbc4775ec0`; quality CI 45916546335 და CPU-thread workflow 45916546277 SUCCESS. Base snapshot 5829188241; current main-ზე refresh/revalidation საჭიროა.
- **PR #100 — NOEMA-007 Georgia multi-hazard spatial catalogue:** head `e407d87bf99d3aec96416d706e94c6fd5b52f36d`; quality CI 45921999557 SUCCESS. Base snapshot 5829188241; current main-ზე refresh/revalidation საჭიროა.
- **PR #101 — INFRA-001 local high-water reference:** head `8102e874604c40476c08e4638943d82a1217a7ca`; quality CI 45922148800 და CPU-thread workflow 45922148866 SUCCESS. Base snapshot 5829188241; current main-ზე refresh/revalidation საჭიროა; independent security/architecture review და separate trust-domain owner აკლია.
- **PR #93, #91, #88, #87, #85, #46, #27, #7, #5:** ღია Draft/engineering proposals; თითოეულს სჭირდება scope triage, current-main refresh და შესაბამისი exact-head revalidation იქამდე, სანამ merge განიხილება.
- **PR #102, #105 და #106:** გაერთიანებულია main-ში; PR #95 დახურულია როგორც superseded by #101.

არცერთი PR #99–#104 არ გაერთიანებულა ამ ციკლში. Draft სტატუსი შენარჩუნებულია იქ, სადაც დამოუკიდებელი რეცენზია, ავტორიზებული მონაცემი ან production trust boundary ჯერ არ არსებობს.

## შემდეგი პრიორიტეტები

1. NOEMA-005: შეინახოს ARM64 raw artifacts მათი 2026-12-26 retention expiry-მდე; შემდეგ ჩატარდეს მინიმუმ 20 repetition თითო კონფიგურაციაზე კონტროლირებად ARM64/x86-64 hardware-ზე, RSS/native allocation და memory bandwidth-ის ცალკე გაზომვით.
2. NOEMA-007: მოიპოვოს NEA heat-warning metadata, ოფიციალური heat-health plan-ის სტატუსი, primary NCDC guidance და controller-approved aggregate MNCH/heat-exposure data.
3. AquaSignal: მოიპოვოს NEA 2021–2025 RAR-ის ოფიციალური ხელმისაწვდომი ასლი, SHA-256, file inventory, data dictionary და reuse terms.
4. INFRA-001: დამოუკიდებელი trust-domain owner და security review-ის გარეშე არ განხორციელდეს production anti-rollback claim, provider adapter ან key custody.
5. ძველი PR #99/#100/#101 განახლდეს current main-ზე ცალკე branch-ებით და exact-head CI-ით; არ მოხდეს ავტომატური merge მხოლოდ იმიტომ, რომ ძველი head-ის CI წარმატებული იყო.

## უსაფრთხოება და გამოქვეყნება

- საჯარო საცავში არ დამატებულა პირადი, კონფიდენციალური, ოპერატიული ან ლიცენზიით შეზღუდული მონაცემი.
- NOEMA-007-ის heat-health addendum არ შეიცავს app telemetry-ს, IP/location/device identifiers-ს ან individual health records-ს.
- NOEMA-005 addendum იყენებს მხოლოდ უკვე commit-ებულ frozen summary JSON-ს.
- No new Supabase project was created; no other project's database was used.
- No research item was promoted to Published; independent review remains required.


## Run 20 — 2026-11-27

- **AquaSignal / NOEMA-006:** [PR #123](https://github.com/maisuradzee/bibmom/pull/123), head `aaceb0fc085fc3ade38ba94c324734210444b6a8`, Draft, mergeable=true. Added published-aggregate denominator audit: 2020 national/regional counts 502/500; 2021 599/621; 2022 and 2023 reconcile. The 2023 JECM 49.5% vs UNECE/WHO 44.5% remains unresolved. Quality CI 45951993138 and CPU-thread workflow 45951993172 SUCCESS.
- **NOEMA-005:** [PR #124](https://github.com/maisuradzee/bibmom/pull/124), head `cbe526f4aa90c93ed609e6f2dbb54c3079a01743`, Draft, mergeable=true. Frozen OpenMP report audit found 9/80 paired CPU/wall ratios above 4.05 across five cases, max 13.287713, despite four reported effective CPUs. Neumaier accuracy remains 40/40; naive 0/40. Quality CI 45952298256 and dedicated audit workflow 45952298265 SUCCESS.
- **NOEMA-007:** PR #121 head `1c8069a0c2114c816ba89b9a2228d289e3f8642a`; Quality CI 45948750137 and CPU-thread workflow 45948750310 SUCCESS; Draft.
- **INFRA-001:** PR #122 head `794c08716d0a4c216e4d9958e9fe79792019e03d`; Quality CI 45948753708 and CPU-thread workflow 45948753734 SUCCESS; Draft.
- Main `68d1aefbf8fa32d8bfecbfca798eadc7eb2c36a9`: Quality CI 45951718946 SUCCESS; Pages build/deploy 45948563354 SUCCESS. Catalogue remains 1 Preliminary, 0 Published. At the audit snapshot before this status PR there were 22 open PRs and 0 open non-PR issues. No merges, no new Supabase project, and no other project's database used.
- Full methods, source boundaries, limitations, file list and next steps: [Run 20 audit](run-audits/2026-11-27-run-20.md).


## Run 21 — 2026-11-27

- **AquaSignal / NOEMA-2026-006:** [PR #123](https://github.com/maisuradzee/bibmom/pull/123), head `487ff547f6a8b456d4c336a616538020df134b34`, Draft, mergeable=true. Source metadata and portfolio now distinguish the Government of Georgia's UNECE/WHO submission from an independent survey; the report says Georgia is not a Party to the Protocol and did not set 2022–2024 target indicators. Sample-source field, E. coli denominator and urban/rural rows are blank; small rural systems were included in 2024. The 2023 JECM 49.5% and government narrative 44.5% remain unreconciled. Exact-head Quality CI 45961315691 and CPU-thread workflow 45961315674 SUCCESS.
- **NOEMA-005:** [PR #124](https://github.com/maisuradzee/bibmom/pull/124), current observed head `9b42586ef21a6371a881dcae191dd9404075c5b0`, ready for review, mergeable=true. The v2 frozen gzip archive was restored to the deterministic 8,533-byte object matching the manifest; exact-head Quality CI 45961553472 and OpenMP audit 45961553450 SUCCESS; actual CPU-thread workflow 45961553457 was IN PROGRESS at the last check.
- **NOEMA-005 cgroup follow-up:** [PR #126](https://github.com/maisuradzee/bibmom/pull/126), head `d294403ce85d1f01b83e2d5d9b03205ea7a83edd`, Draft, stacked on PR #124. Added a synthetic test for unknown worker cgroup membership and a research note. It must be refreshed against the final parent head and exact-head CI rerun before merge.
- **NOEMA-007:** remains Draft; no authorized Georgian event/after-action data or field partner was obtained in this run.
- **INFRA-001:** remains engineering/Draft; separate trust-domain owner, key custody and clean-host restore evidence remain missing.
- Main snapshot `563cad6fed0c18583f09471e88ea55d5d5c51078`: Quality CI 45957075745 SUCCESS; Pages build/deploy 45957075729 SUCCESS. At this audit snapshot: 22 open PRs, 0 open non-PR issues; catalogue 1 Preliminary, 0 Published. No research item was promoted to Published.
- Full methods, evidence labels, source links, limitations and next steps: [Run 21 audit](run-audits/2026-11-27-run-21.md).


## Run 22 — 2026-11-27

- **Main:** `736012774f411f64e674488fcffaa6aa35680008`. Quality CI [45964685524](https://github.com/maisuradzee/bibmom/actions/runs/45964685524) SUCCESS; Pages build/deploy [45964685539](https://github.com/maisuradzee/bibmom/actions/runs/45964685539) SUCCESS.
- **NOEMA-005:** [PR #124](https://github.com/maisuradzee/bibmom/pull/124) merged at `fa711306d5eb588d1c9e97b207d8358c879fd04a`; [PR #126](https://github.com/maisuradzee/bibmom/pull/126) merged at `fc4b44f768ff5d1256c6f1e5209925cababcd868`. Cross-architecture native results: full Neumaier state and exact superaccumulator rounded correctly in 40/40 cases on both x86-64 and ARM64; naive partials and pairwise tree were 0/40 on both. Python Neumaier-state was 48/48 per environment, but median speedup stayed below 1.0 in all four runner/runtime cells. Hosted-runner, synthetic-workload evidence only; no physical-device or application-workload claim.
- **INFRA-001:** [PR #122](https://github.com/maisuradzee/bibmom/pull/122) merged at `736012774f411f64e674488fcffaa6aa35680008` after exact-head Quality CI [45964506253](https://github.com/maisuradzee/bibmom/actions/runs/45964506253) and both CPU-thread jobs [45964506283](https://github.com/maisuradzee/bibmom/actions/runs/45964506283) succeeded. This is a pure restore-attestation completeness gate with ten synthetic tests, not a real offsite restore or production anti-rollback service.
- **AquaSignal / NOEMA-2026-006:** [PR #128](https://github.com/maisuradzee/bibmom/pull/128) is Draft, current head `272f3a25e402ae26da259f90bd395c3d6af5aa0b`, mergeable=true. Exact-head Quality CI [45964721254](https://github.com/maisuradzee/bibmom/actions/runs/45964721254) SUCCESS. New evidence-led question: public access and comprehensibility of authorized drinking-water results. Public Defender's 2025 report records monitoring visits in five regions, 35 villages and 15 municipalities and recommends a unified information platform plus supplementary channels. This is not a nationally representative sample. JECM's 2023 49.5% and the Government-submitted 44.5% remain unreconciled.
- **NOEMA-007:** remains active/Draft. No authorized Georgian warning-event/after-action aggregates, event-review mandate or field partner were obtained in this run.
- **HadCRUT5 coverage validation:** separate workflow [45963513863](https://github.com/maisuradzee/bibmom/actions/runs/45963513863) failed on the `fa711306` snapshot: sigma RMSE 0.0003516123 °C, max absolute difference 0.0006968631 °C versus 0.0005 °C tolerance; area-fraction max difference was only 3.44e-8. No tolerance was relaxed. The exact ERA5/RMS method, regridding and source-series version require reconciliation before combined-trend results are used.
- **Portfolio:** four active streams (AquaSignal, NOEMA-005, NOEMA-007, INFRA-001); no new stream added and none marked complete. Catalogue remains 1 Preliminary, 0 Published. At this snapshot: 21 open PRs and 0 open non-PR issues. PRs #121/#123 and older drafts still need current-main review/rebase before any merge.
- No personal, household, sample-level, health, private-well or credential data was added. No new Supabase project was created and no other project's database was used.
- Full evidence classifications, methodology, source links, limitations, file/commit list and next steps: [Run 22 audit](run-audits/2026-11-27-run-22.md).



## Run 23 — 2026-11-27

- **Main snapshot:** `0135a361a03b7e213225e2ef4ba5adb922c4d044`. Quality CI [45965380543](https://github.com/maisuradzee/bibmom/actions/runs/45965380543) SUCCESS; Pages build/deploy [45965380585](https://github.com/maisuradzee/bibmom/actions/runs/45965380585) SUCCESS. The two new research PRs below are not merged, so the deployed site remains the main snapshot above.
- **AquaSignal / NOEMA-2026-006:** [PR #129](https://github.com/maisuradzee/bibmom/pull/129), Draft, head `8b5198000b2a9743fd9b217a40ac1308e5328a53`, base `0135a361a03b7e213225e2ef4ba5adb922c4d044`, mergeable=true. Exact-head push Quality CI [45975883608](https://github.com/maisuradzee/bibmom/actions/runs/45975883608) and pull-request Quality CI [45975889729](https://github.com/maisuradzee/bibmom/actions/runs/45975889729) SUCCESS. Adds a closed metadata schema with required supply-type scope, same-period comparability gate, source-observation fixture, research draft and 17 focused tests; full suite: 472 tests, one skipped. WHO 2026 surveillance guidance also informs a proposed, public-safe remedial-action follow-up record. The gate refuses to compare the JECM 2023 49.5% and Government-submitted 44.5% reports while indicator definition, water matrix, standard/version, sampling frame/design, inclusion rule, method, count unit, numerator definition and denominator definition are unknown. The gate now requires all three count-semantics fields and blocks missing/mismatched definitions. It never emits a population-safety or causal claim.
- **NOEMA-007:** [PR #130](https://github.com/maisuradzee/bibmom/pull/130), Draft, head `46ce488a425da256345c41e8eac1a1d6138cbed0`, base `0135a361a03b7e213225e2ef4ba5adb922c4d044`, mergeable=true. Exact-head push Quality CI [45976110643](https://github.com/maisuradzee/bibmom/actions/runs/45976110643) and pull-request Quality CI [45976114767](https://github.com/maisuradzee/bibmom/actions/runs/45976114767) SUCCESS. Extends the aggregate survey contract with optional, backward-compatible self-reported timely-receipt fields and explicit denominators. A paired event-specific rule reference/source URL is required before computing the rate; absent source leaves the rate null. Caller-supplied privacy approval booleans are explicitly treated as unverified declarations, and the validator never authorizes publication. The timing measure is respondent recall only; endpoint receipts remain separate and no raw device logs or Georgian event data were added.
- **NOEMA-005:** [PR #132](https://github.com/maisuradzee/bibmom/pull/132), Draft, head `b4d150a94d9aebbb1ee6c36e67768a805926a22c`, base `0135a361a03b7e213225e2ef4ba5adb922c4d044`, mergeable=true. Exact-head push Quality CI [45974905412](https://github.com/maisuradzee/bibmom/actions/runs/45974905412) and pull-request Quality CI [45974913049](https://github.com/maisuradzee/bibmom/actions/runs/45974913049) SUCCESS; focused reproduction: 5 tests; full suite: 462 tests, one skipped. New hosted x86-64 AWS rerun [45972740197](https://github.com/maisuradzee/bibmom/actions/runs/45972740197) preserves raw reports and verifies input hashes/native thread identities. Full Neumaier state: 48/48 accuracy in both runtimes, but median speedup is only 0.7541x (GIL) and 0.7021x (free-threaded); no speedup claim. This remains hosted virtual hardware, not physical-device replication.
- **INFRA-001 audit:** the restore-attestation evaluator remains a metadata-completeness gate. It does not authenticate signatures, query provider retention, decrypt artifacts, or prove clean-host restoration. Independent recovery owner, key custody, external high-water authority and a permissioned clean-host restore remain outstanding.
- **NOEMA-007 discovery:** the official WMO/UNDRR 2026 report continues to show the gap between country-reported capability and end-to-end completeness: 136 countries report MHEWS, 64 report all four pillars; disaster-risk knowledge is the weakest pillar (72/136). These are country-level capability counts, not population coverage or local Georgian warning effectiveness.
- **Portfolio:** four active streams remain (AquaSignal, NOEMA-005, NOEMA-007, INFRA-001); no stream was added, paused or marked complete. The AquaSignal and NOEMA-007 portfolio changes are in Draft PRs #129 and #130; NOEMA-005 Run 23 raw reports and frozen summary are in Draft PR #132. None is yet on main. Catalogue remains 1 Preliminary, 0 Published. After merging this status audit PR, there are 23 open PRs and 0 open non-PR issues; several older Draft PRs target ancestors of current main and require separate rebase/review before any merge.
- No research PR was merged in this run. No personal, household, sample-level, health, private-well or credential data was added. No new Supabase project was created and no other project's database was used.
- Full methodology, evidence labels, source links, test outcomes, limitations and next steps: [Run 23 audit](run-audits/2026-11-27-run-23.md).


### Run 23 follow-up verification — 2026-11-27

- AquaSignal PR #129 was extended with required `count_unit`, `numerator_definition_id` and `denominator_definition_id`; missing count semantics remain null for the two Georgian 2023 reports. Exact-head CI passed at `8b5198000b2a9743fd9b217a40ac1308e5328a53`.
- NOEMA-007 PR #130 now retains the timely-receipt numerator/denominator but returns a null rate when no event-specific rule reference and HTTPS source are supplied. A provided source is explicitly not independently verified. Caller-supplied privacy approval booleans are not treated as authenticated approval, and the validator returns `publication_authorized_by_validator=false`. Exact-head CI passed at `46ce488a425da256345c41e8eac1a1d6138cbed0`.
- NOEMA-005 PR #132 was updated to `b4d150a94d9aebbb1ee6c36e67768a805926a22c`; exact-head push CI [45974905412](https://github.com/maisuradzee/bibmom/actions/runs/45974905412) and PR CI [45974913049](https://github.com/maisuradzee/bibmom/actions/runs/45974913049) passed.
- Two raw Run 23 artifact ZIPs were independently downloaded from GitHub Actions and their ZIP SHA-256 values and extracted JSON SHA-256 values matched the frozen summary. The 48-case matrices and aggregates were recomputed from raw JSON: full Neumaier state 48/48 in each runtime; median speedup 0.7541x GIL and 0.7021x free-threaded; CPU-time/wall-time >1.05 in 0/48 and 36/48 respectively. This is artifact-level reproduction of a hosted synthetic batch, not a physical-device replication.


## Run 24 — 2026-11-27

- **Main snapshot:** `ff10cbfdb9005ef75245fc95620b1fffc12bdd0c`. PR #131 (Run 23 documentation audit) was merged only after exact-head Quality CI and CPU-thread workflow success. Post-merge Quality CI [45979963023](https://github.com/maisuradzee/bibmom/actions/runs/45979963023) and Pages build/deploy [45979962723](https://github.com/maisuradzee/bibmom/actions/runs/45979962723) both succeeded for this exact SHA.
- **AquaSignal:** review of Draft PR #129 found that equal opaque definition IDs were not bound to trusted source artifacts. Follow-up Draft PR #134 adds SHA-256 and locator metadata for seven material definitions; exact-head CI [45980458985](https://github.com/maisuradzee/bibmom/actions/runs/45980458985) succeeded (22 focused tests; full suite 479). The comparator does not authenticate or fetch source documents; a trusted acquisition layer remains required. Georgian 49.5%/44.5% reports remain non-comparable.
- **NOEMA-005:** review of Draft PR #132 found that its Run 23 verifier did not enforce the full 2-layout × 4-worker × 2-partition matrix. Follow-up Draft PR #133 now validates the complete matrix, numeric bounds, thread identity, timing medians and CPU/wall flags. Final exact-head CI [45980689146](https://github.com/maisuradzee/bibmom/actions/runs/45980689146) succeeded (14 focused tests; full suite 471). Two earlier attempts failed due to the incomplete matrix model and were corrected. Original ZIP SHA remains acquisition-time metadata; the committed verifier re-hashes extracted report bytes only. No physical-device replication or speedup claim.
- **NOEMA-007:** Draft PR #130 remains active; review identified that minimum timely-receipt lead time is not yet bounded by the warning-to-action deadline window. No Georgian field data or authorized event-review mandate was obtained.
- **INFRA-001:** no production offsite/clean-host recovery proof. Independent recovery owner, key custody, external high-water authority and immutable retention remain blockers.
- **Portfolio:** four active streams; no new stream added, paused or completed. Catalogue remains 1 Preliminary, 0 Published. Repository has 25 open PRs and 0 open Issues; older drafts require individual current-main review/rebase.
- No personal, household, sample-level, health, private-well, location-tracking or credential data was added. No new Supabase project was created and no other project's database was used.
- Full findings, methodology, evidence boundaries, CI outcomes and next steps: [Run 24 audit](run-audits/2026-11-27-run-24.md).



### Run 24 follow-up verification — 2026-11-27

- Main advanced to `a48af6aae5c41575d80645b4cb9d81118c212153` after merging the Run 24 documentation audit. Exact-main Quality CI [45981086254](https://github.com/maisuradzee/bibmom/actions/runs/45981086254) and Pages build/deploy [45981086157](https://github.com/maisuradzee/bibmom/actions/runs/45981086157) both succeeded.
- NOEMA-007 follow-up [PR #136](https://github.com/maisuradzee/bibmom/pull/136) constrains the positive minimum timely-receipt lead to the warning issue-to-action-deadline interval and reports the available interval. Exact-head Quality CI [45981048842](https://github.com/maisuradzee/bibmom/actions/runs/45981048842) succeeded; 24 focused tests and 471 full-suite tests passed. PR #136 remains Draft and targets parent PR #130's branch; no field data or authority-approved rule is implied.
- Full follow-up evidence and limitations: [Run 24 follow-up audit](run-audits/2026-11-27-run-24-follow-up.md).



## Run 25 — post-revert status and evidence (2026-11-27)

- **Current main:** `0b22644bb2c669d4d152487e8b3e82a38f7843df`. PR #143 reverted an accidental direct-main write of the run audit file; the audit is being reintroduced only through a proper branch-based PR. No research code or data was committed directly to main. The corrective PR's exact-head Quality CI runs [45989720439](https://github.com/maisuradzee/bibmom/actions/runs/45989720439) and [45989759548](https://github.com/maisuradzee/bibmom/actions/runs/45989759548) both passed. The post-revert main push CI and Pages deployment are not independently verified.
- **Last verified main snapshot:** `21db09ddf1b98de6a58929c63260de16728f4ff8`; Quality CI [45981391575](https://github.com/maisuradzee/bibmom/actions/runs/45981391575) SUCCESS; Pages build/deploy [45981391564](https://github.com/maisuradzee/bibmom/actions/runs/45981391564) SUCCESS. The corrective revert restores the same content tree, but no new deployment is claimed.
- **PR #144 — AquaSignal:** head `8879ac1b0397e2f5f07c72bad6ac97e3024f01d3`, mergeable=true, Draft. Exact-head Quality CI [45990304985](https://github.com/maisuradzee/bibmom/actions/runs/45990304985) SUCCESS, including draft completeness, water-comparability schema/tests, NEA 2025 aggregate snapshot schema/tests, full Python unit suite and site/publication-boundary build. CPU-thread workflow [45990304897](https://github.com/maisuradzee/bibmom/actions/runs/45990304897) — GIL-enabled and free-threaded jobs SUCCESS.
- **PR #145 — NOEMA-007:** head `f00aa59a48458c5eea95f101b17270a7a0046049`, mergeable=true, Draft. Exact-head Quality CI [45990379296](https://github.com/maisuradzee/bibmom/actions/runs/45990379296) SUCCESS; CPU-thread workflow [45990379332](https://github.com/maisuradzee/bibmom/actions/runs/45990379332) — both runtime jobs SUCCESS.
- **PR #146 — INFRA-001:** head `1f493a9ec18d3930e3ea599a51eb4c3970bed876`, mergeable=true, Draft. Exact-head Quality CI [45990428306](https://github.com/maisuradzee/bibmom/actions/runs/45990428306) SUCCESS, including local high-water validation, full Python unit suite and site/publication-boundary build; CPU-thread workflow [45990428281](https://github.com/maisuradzee/bibmom/actions/runs/45990428281) — GIL-enabled and free-threaded jobs SUCCESS.
- **AquaSignal discovery update:** the official NEA 2025 annual-report PDF is accessible at https://nea.gov.ge/en/Download/File/1444. It reports 124 groundwater monitoring points (74 planned + 50 field-instrumental), 681 lab samples from 74 points, nitrate field work at 50 points (19 wells, 30 springs, 1 household well; NEA's source term is “საყოფაცხოვრებო ჭა”, household well), and separate surface-water monitoring at 238 points / 2,571 samples. It separately lists parameter coverage at 73 surface-water points. The 73/74 relationship is unresolved; sample counts are not a compliance numerator/denominator or safety estimate. The distinct 2021–2025 RAR announced 2026-11-26 remains inaccessible through the automated retrieval path.
- **NOEMA-007:** no Georgian event or participant data was obtained. The new lead-window contract is synthetic and mathematical only; it does not authenticate the authority or deadline, and respondent recall is not timestamp-verified receipt.
- **NOEMA-005:** no new scientific benchmark conclusion is claimed in Run 25. The CPU-thread workflows also ran on non-NOEMA-005 research branches due to repository workflow triggers; those generic CI runs are not treated as new research results. Physical x86-64/ARM64 replication, ≥20 repetitions/configuration, RSS/native allocation and memory-bandwidth measurement remain outstanding.
- **INFRA-001:** the local SQLite reference model tests single-file compare-and-advance semantics only. It is not an independent trust domain, production anti-rollback service or clean-host restore.
- **Portfolio:** four active streams remain; no fifth stream added, none paused/completed. Research catalogue remains 1 Preliminary / 0 Published. Repository: 24 open PRs, 0 open Issues.
- No personal, household, private-well, health, device, location-tracking, credential or restricted data was added. No new Supabase project was created and no other project's database was used.
- Full methodology, exact heads, evidence boundaries and next priorities: [Run 25 audit](run-audits/2026-11-27-run-25.md).


## Run 26 — post-merge portfolio and evidence audit (2026-11-27)

- **Main snapshot:** `2469d0c82e065db0a1fe1982f457a1b66fb45ba6`. PR #149 corrected the NEA nitrate point translation in the public Run 25 audit. Exact-head PR CI [45994023360](https://github.com/maisuradzee/bibmom/actions/runs/45994023360) and CPU-thread workflow [45994023267](https://github.com/maisuradzee/bibmom/actions/runs/45994023267) succeeded. Post-merge main Quality CI [45994175616](https://github.com/maisuradzee/bibmom/actions/runs/45994175616) and Pages build/deploy [45994175596](https://github.com/maisuradzee/bibmom/actions/runs/45994175596) succeeded for the exact main SHA.
- **AquaSignal:** the NEA 2025 report's Georgian term `საყოფაცხოვრებო ჭა` means household well, not household well. The corrected public audit is merged; PR #144's data/schema/tests use `control_wells` and exact-head Quality CI [45993708487](https://github.com/maisuradzee/bibmom/actions/runs/45993708487) plus CPU-thread workflow [45993708489](https://github.com/maisuradzee/bibmom/actions/runs/45993708489) succeeded. PR #144 remains Draft and needs base refresh and independent water-quality/statistical review.
- **NOEMA-005:** PR #148's malformed truncated JSON was replaced with a valid compact report preserving 48 configurations and 960 raw wall-time samples. Derived medians and speedups were recomputed from raw samples; one row changed from 1,035,946 ns / 0.322461789 to 1,034,764 ns / 0.322830133. The serial baseline wall medians remain; serial baseline process-CPU details are omitted from the compact JSON. Exact-head Quality CI [45994073404](https://github.com/maisuradzee/bibmom/actions/runs/45994073404) and [45994065722](https://github.com/maisuradzee/bibmom/actions/runs/45994065722) succeeded for head `ee822df98142ee786160a777ed6bc2fb83f25673`. This is a report-integrity correction, not a new benchmark execution or performance conclusion. PR #148 remains Draft and requires base refresh, independent numerical review and physical-device replication.
- **NOEMA-007:** PR #145 remains Draft. Its UTC timestamp and feasible minimum-lead checks passed exact-head CI [45990379296](https://github.com/maisuradzee/bibmom/actions/runs/45990379296) and CPU-thread workflow [45990379332](https://github.com/maisuradzee/bibmom/actions/runs/45990379332); synthetic validation only, no Georgian event or participant data.
- **INFRA-001:** PR #146 remains Draft. Its local SQLite high-water reference model passed Quality CI [45990428306](https://github.com/maisuradzee/bibmom/actions/runs/45990428306) and CPU-thread workflow [45990428281](https://github.com/maisuradzee/bibmom/actions/runs/45990428281); no external trust domain, production anti-rollback service or clean-host restore exists.
- **Portfolio:** four active streams remain; no fifth stream added and none paused/completed. Research catalogue remains 1 Preliminary / 0 Published. Open PRs: 25; open Issues: 0. PRs #144–#148 remain Draft/stale-base; do not merge until refreshed against current main and exact-head checks are repeated.
- **Evidence/safety:** NEA's 2025-09-18 network disclosure (72 groundwater points, 238 surface-water locations, 12 Black Sea locations) and 2025 annual report counts (74 laboratory-sampling points, 73 listed-parameter points, 124 combined reported groundwater monitoring points) are different reporting frames; no 72→74 trend or unique-site count is inferred. The 681 laboratory sample counts are not a compliance denominator or water-safety estimate. No personal, household, private-well-owner, health, device, location-tracking, credential or restricted data was added. No new Supabase project was created and no other project's database was used.
- Full methodology, source boundaries and next steps: [Run 26 audit](run-audits/2026-11-27-run-26.md).


### Run 26 post-merge synchronization

- PR #150 merged as `27edcf226bd27981c32b935d66c697321384a84c`.
- Exact post-merge main Quality CI [45994569018](https://github.com/maisuradzee/bibmom/actions/runs/45994569018) and GitHub Pages build/deploy [45994568948](https://github.com/maisuradzee/bibmom/actions/runs/45994568948) both succeeded.
- The merged Run 26 portfolio records all four active streams, source-frame distinctions, AquaSignal's corrected control-well terminology, and the NOEMA-005 frozen-report packaging/derived-metric audit.


## Run 34 — WRP 2025 independent reproduction and restore numeric hardening (2026-11-27)

- **Main before this research PR:** caf2940614b8a8d7b814cc54129fd963730ca91c. PR #180 merged the INFRA-001 finite-measurement guard. Exact-head Quality CI [46041078881](https://github.com/maisuradzee/bibmom/actions/runs/46041078881) succeeded across schema checks, all Python tests, frozen reproductions, site build and publication-boundary checks.
- **NOEMA-007:** the LRF WRP 2025 Parquet was downloaded in an ephemeral GitHub Actions runner and independently aggregated. Source commit f2b810c3c4333de6347ad2c9eade3c48ae17be4c; Git blob SHA-1 3e785688e067ded5fdfbe9b50721023ecea87826; byte length 7,070,416; local SHA-256 07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b. Workflow [46041436183](https://github.com/maisuradzee/bibmom/actions/runs/46041436183), job 140649865106, artifact 15219814678. Results: 24,249 warning base; 16,996 warned; weighted warning receipt 80.011542% (publisher rounding 80.0%). Among warned: 9,479 able (63.779158%), 7,383 unable (35.759146%), 134 DK/refused (0.461696%). Georgia: 101 impacted, 99 warning-question base, below publisher n>=100 country-ranking threshold.
- **Evidence boundary:** independent arithmetic on the publisher's public microdata is not an independent survey or operational early-warning audit. Survey recall does not establish timestamp-verified delivery, comprehension, feasible action, verified protective action or avoided loss. Global estimates are not Georgian estimates. Raw microdata and respondent identifiers were not committed or uploaded; only aggregate JSON is retained.
- **CI correction:** the first PR's dedicated data workflow succeeded, but main Quality CI stopped at draft validation because the research note lacked the repository's required Georgian headings/date/status metadata. The corrected research record uses the required Georgian headings; a refreshed PR reruns the dedicated dataset workflow and all Quality CI checks.
- **Portfolio:** four active streams remain. NOEMA-007's next blocker is authorised Georgian event-level warning and after-action data. AquaSignal still needs the NEA RAR or authorised alternate PDF transfer, station/sample dictionary and reuse terms. NOEMA-005 still needs physical x86-64/ARM64 replication with at least 20 repetitions per configuration and RSS/native-memory/DRAM-bandwidth measurements. INFRA-001 still needs an independent recovery owner, trust domain and clean-host restore.
- No new Supabase project or other project's database was used. No respondent-level, private, health, location-tracking, credential or restricted data was committed.


### AquaSignal — WRP 2025 WP22443 independent reproduction

The pinned LRF WRP 2025 Parquet was downloaded on an ephemeral GitHub Actions runner. Git blob SHA-1 3e785688e067ded5fdfbe9b50721023ecea87826, byte length 7,070,416 and SHA-256 07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b were verified. Workflow [46042747456](https://github.com/maisuradzee/bibmom/actions/runs/46042747456), job 140654329587, aggregate-only artifact 15221271518.

WP22443 base: 143,459 respondents, 140 countries/territories, zero missing. PROJWT-weighted code 1 (personally experienced) 7.106988%, rounded 7%; code 3 (both) 5.850209%, rounded 6%; publisher rounded sum 13%. Unrounded combined value: 12.957198%. All six response categories and DK/refused remain in the denominator.

Evidence boundary: WP22443 is self-reported serious harm over the past two years, not laboratory contamination, compliance, exposure attribution or a Georgian prevalence estimate. Only aggregate JSON was uploaded; no respondent-level records were committed. Main Quality CI first stopped at draft validation because the heading did not begin with NOEMA-; the corrected preprint now uses the required NOEMA-2026-006 title and will be rechecked in PR #183. The NEA RAR, NFA denominator and paired sample-level data remain blockers.


### NOEMA-005 — two additional hosted x86-64 real-thread run pairs

Workflow runs [46042334393](https://github.com/maisuradzee/bibmom/actions/runs/46042334393) and [46043232025](https://github.com/maisuradzee/bibmom/actions/runs/46043232025) produced four aggregate-only artifacts (48 configurations and 144 measured threaded runs per artifact; 576 runs total). Across 192 configurations: Neumaier-state was correctly rounded in 192/192 runs, scalar Neumaier in 168/192, naive scalar in 0/192. No configuration beat its matching serial baseline (0/192). Free-threaded process CPU/wall ratio exceeded 1.05 in 72/96 configurations; GIL-enabled in 0/96. Native thread counts matched requested worker counts.

Run 1 used the same AWS x86-64 runner family for both runtime modes. Run 2 used AWS for free-threaded and Azure for GIL-enabled, so Run 2 is not a matched cross-mode comparison. These are hosted x86-64 synthetic results, not physical-device or ARM64 replication. tracemalloc is Python allocation accounting only, not RSS/native memory; DRAM bandwidth was not measured. The frozen aggregate summary and four artifact ZIP/JSON hashes are in data/noema-005/threaded-run-2026-11-27-summary.json.


## Run 35 — CPU-thread evidence freeze და WRP survey-input validation (2026-11-27)

### პორტფელის მდგომარეობა

- **AquaSignal / NOEMA-2026-006 — active, preliminary:** WRP 2025 WP22443-ის pinned aggregate უცვლელია. PR #186-ის შემდეგ response code-ები მკაცრად მოწმდება: მხოლოდ integral, non-boolean და გამოქვეყნებულ კოდთა ნაკრებში არსებული მნიშვნელობები მიიღება. PROJWT წონა უნდა იყოს finite, non-negative `numbers.Real`; built-in/NumPy bool და numeric string უარყოფილია. NEA RAR/HTTPS ასლი, მონაცემთა ლექსიკონი, reuse პირობები და NFA denominator კვლავ ბლოკერია.
- **NOEMA-005 — active, preliminary:** PR #184-ით დაემატა ოთხი hosted x86-64 artifact, 192 configuration და 576 measured threaded run. Neumaier-state 192/192 correctly-rounded, scalar Neumaier 168/192, naive scalar 0/192; threaded speedup >1.0 იყო 0/192 configuration-ში. ეს hosted synthetic evidence-ია და არა physical-device ან ARM64 replication.
- **NOEMA-2026-007 — active, preliminary:** PR #185-მა გაამკაცრა warning/action response-code ტიპები რვა warning channel-ზე, WP24215-სა და WP24213-ზე; PR #187-მა PROJWT-ის numeric type validation გაამკაცრა. Pinned WRP aggregate და denominator-ები უცვლელია. საქართველოს უფლებამოსილი event-level warning/after-action მონაცემები კვლავ არ არსებობს.
- **INFRA-001 — active, engineering:** ამ ციკლში production recovery არ შესრულებულა. დამოუკიდებელი recovery owner, trust-domain, key custody, immutable offsite retention და clean-host restore კვლავ აუცილებელია.

### რეალურად შესრულებული სამუშაო

1. **NOEMA-005 — PR #184 merged** as `e7d9652b0bfb6deb99aac58686736cda99ecbad1`. Run 34-ის ოთხი aggregate-only artifact შენარჩუნდა. Exact-head Quality CI [46044459870](https://github.com/maisuradzee/bibmom/actions/runs/46044459870) და CPU-thread workflow [46044459895](https://github.com/maisuradzee/bibmom/actions/runs/46044459895) წარმატებულია. თავდაპირველი privacy test `"thread_id"` substring-ით `thread_identity` protocol აღწერას შეცდომით კრძალავდა; ტესტი გადაკეთდა recursive JSON object-key შემოწმებად. Raw native thread identifiers საცავში არ დამატებულა.
2. **NOEMA-007 — PR #185 merged** as `810da5e4b51b7b2dc5d4700e0fb90b4071e0dfdf`. Python-ში `bool` არის `int`-ის subclass და `True == 1`; ამიტომ response-code membership შემოწმება შეცვლილია strict `numbers.Integral` validation-ით. რვა warning channel, WP24215 და WP24213 უარყოფს bool და float lookalikes. Exact-head Quality CI [46044833779](https://github.com/maisuradzee/bibmom/actions/runs/46044833779) და WRP reproduction [46044833793](https://github.com/maisuradzee/bibmom/actions/runs/46044833793) წარმატებულია.
3. **AquaSignal — PR #186 merged** as `b5267cb7dd7578cc46bd1b1837ce2f77e3852abf`. WP22443 response code-ები მკაცრად მოწმდება; PROJWT წონა უნდა იყოს finite non-negative real numeric value. Exact-head Quality CI [46045040482](https://github.com/maisuradzee/bibmom/actions/runs/46045040482), AquaSignal reproduction [46045040425](https://github.com/maisuradzee/bibmom/actions/runs/46045040425) და push Quality CI [46045036687](https://github.com/maisuradzee/bibmom/actions/runs/46045036687) წარმატებულია.
4. **NOEMA-007 — PR #187 merged** as `8851e8f2d6af2abaf7cd931aaf55d1712d60007b`. PROJWT ახლა მოითხოვს `numbers.Real`-ს; უარყოფილია numeric strings, NumPy bool, NaN, ±Infinity და უარყოფითი წონები. Python/NumPy numeric scalars მხარდაჭერილია. Exact-head Quality CI [46045173173](https://github.com/maisuradzee/bibmom/actions/runs/46045173173), WRP reproduction [46045173225](https://github.com/maisuradzee/bibmom/actions/runs/46045173225) და push Quality CI [46045168260](https://github.com/maisuradzee/bibmom/actions/runs/46045168260) წარმატებულია.

### მტკიცებულების სტატუსი და შეზღუდვები

- **FACT:** Python-ის ოფიციალური დოკუმენტაცია განსაზღვრავს `bool`-ს როგორც `int`-ის subclass-ს; შესაბამისად, bool response code-ის რიცხვად მიღება რეალური ტიპური შეცდომაა. წყარო: https://docs.python.org/3/library/stdtypes.html#boolean-type
- **REPRODUCED RESULT:** Run 34-ის hosted x86-64 aggregate; 576 measured threaded runs, 192 configurations, Neumaier-state 192/192 correctly-rounded. არცერთი threaded configuration არ აჯობა matching serial baseline-ს.
- **REPRODUCED RESULT:** WRP 2025 pinned Parquet-ის warning/action და water-harm aggregate-ები dedicated ephemeral CI workflow-ებში უცვლელად მეორდება; საცავში მხოლოდ aggregate JSON ინახება.
- **INFERENCE:** strict input types ამცირებს malformed synthetic/ingestion input-ის არასწორი კლასიფიკაციის რისკს; ეს არ ცვლის უკვე დათვლილ WRP შედეგებს და არ ადასტურებს მონაცემის წარმომავლობას ან survey methodology-ს.
- **UNTESTED IDEA:** ფიზიკურ x86-64/ARM64-ზე 20+ გამეორება, RSS/native allocation, DRAM bandwidth და CPU-frequency measurements კვლავ არ ჩატარებულა.
- WRP microdata მხოლოდ ephemeral runner-ზე მუშავდება. Raw respondent rows, IDs, health details და household locations საცავში არ ინახება.
- AquaSignal-ის NEA ანგარიში/ნიტრატების მონაცემები და NOEMA-007-ის საქართველოს event-level after-action data ჯერ არ მიგვიღია.
- INFRA-001-ის production clean-host restore არ შესრულებულა. არც ახალი Supabase პროექტი შექმნილა და არც სხვა პროექტის ბაზა გამოყენებულა.

### Main validation

- Main SHA audited: `1278c856857121cb0d3bf623666fe5c495a4975c`.
- Quality CI: [46045601007](https://github.com/maisuradzee/bibmom/actions/runs/46045601007) — SUCCESS, 491 Python tests, schema/frozen-result checks, site build და publication-boundary checks.
- Pages: [46045601021](https://github.com/maisuradzee/bibmom/actions/runs/46045601021) — build/deploy SUCCESS.
- PR #184–#188 merged; მიმდინარე ღია PR-ები 38; ღია Issue 0.
- Research catalogue: 3 Preliminary, 0 Published.

### შემდეგი პრიორიტეტები

1. AquaSignal: NEA-სგან ავტორიზებული HTTPS/checksum-ით დამოწმებული ანგარიშის ასლი, sample/station dictionary, reuse terms და NFA denominator.
2. NOEMA-007: მონაცემთა კონტროლერის მიერ დამტკიცებული ქართული event-level warning/after-action aggregate-ები და წინასწარ განსაზღვრული denominators.
3. NOEMA-005: ფიზიკური x86-64/ARM64 კონტროლირებული benchmark, 20+ repetitions, RSS/native memory და DRAM bandwidth.
4. INFRA-001: დამოუკიდებელი recovery owner, trust-domain, key custody და permissioned clean-host restore.


## Run 36 — NFA 2025 access lead და restore-attestation parser hardening

### შესრულებული სამუშაო

- **AquaSignal / PR #190 (Draft):** NFA-ს ოფიციალური 2026-01-08 გვერდი დააფიქსირებს 2025 Food Department-ის ადმინისტრაციულ მაჩვენებლებს და XLSX endpoint-ს, რომელიც აღწერილია როგორც საკვებისა და სასმელი წყლის მონიტორინგის ნიმუშებში გამოვლენილი დარღვევები. XLSX payload არ ჩამოტვირთულა, არ დაიჰეშა და არ გაიხსნა. წყლის ცალკე მნიშვნელი, სრული ტესტირებული ნიმუშების frame და reuse terms უცნობია. Metadata-only JSON, closed schema, 5 test და draft note დაემატა.
- **INFRA-001 / PR #191 (Draft):** დაემატა `load_restore_attestation_bytes()` და `evaluate_restore_attestation_bytes()`: ზუსტი UTF-8 bytes, 1 MiB ზღვარი, recursive duplicate-key rejection, NaN/Infinity token rejection და object-root მოთხოვნა. დაემატა 6 synthetic regression test. ეს არ ამოწმებს evidence signatures-ს და არ ქმნის production recovery trust-domain-ს.
- **NOEMA-007:** pinned WRP 2025 warning/action reproduction run 46041436183-ის reproduce job ხელახლა შემოწმდა — SUCCESS. ახალი ქართული operational event/after-action მონაცემები არ მიგვიღია.
- **NOEMA-005 / PR #193 (Draft):** PR #190 და #191-ის CPU-thread workflow-ებიდან ოთხი hosted x86-64 artifact ჩამოიტვირთა; ZIP/report SHA-256, input hashes და native-thread counts შემოწმდა. 192 configuration / 576 measured run: Neumaier-state 192/192 სწორად დამრგვალდა, scalar Neumaier 168/192, naive 0/192. Free-threaded Neumaier-state CPU/wall >1.05 იყო 72/96 measured run-ში (24/32 configuration), GIL-enabled 0/96-ში. Median speedup PR190 free-threaded 1.145852x-დან PR191 free-threaded 0.947358x-მდე შეიცვალა; სტაბილური აჩქარება არ დასტურდება. PR193 ინახავს მხოლოდ aggregate snapshot-ს და ავიწროებს benchmark workflow path filters-ს, რათა დოკუმენტაციის PR-ებმა ახალი benchmark არ გამოიწვიოს. ფიზიკური x86-64/ARM64, RSS/native memory და DRAM bandwidth კვლავ ბლოკერებია.

### კვლევითი მიგნებები და მტკიცებულების საზღვრები

- **FACT:** NFA-ს ოფიციალური გვერდი 2025 წელს 21,874 Food Department inspection-ს, 10,521 გადამოწმებულ business operator-ს და 554 critical non-compliance operator-ს ასახელებს; იმავე გვერდიდან ხელმისაწვდომია combined food/drinking-water violations XLSX ბმული.
- **INFERENCE:** violations-only ფაილი ვერ იძლევა non-compliance prevalence-ს სრული tested-sample denominator-ისა და sampling frame-ის გარეშე.
- **HYPOTHESIS:** data-controller-approved, de-identified წყლის აგრეგატები შეიძლება გამოყენებულ იქნეს provenance-preserving მონიტორინგისთვის.
- **UNTESTED IDEA:** ავტორიზებული aggregate export-ის private staging adapter და disclosure-reviewed public output.
- NFA XLSX-ის payload, SHA-256, worksheet/column inventory, row count, water-only denominator და reuse terms უცნობია. 2025 NFA access lead არ ავსებს ცალკე 2024 E. coli მაჩვენებლის დაკარგულ მნიშვნელს.
- RFC 8259 §4 duplicate object names-ის შემთხვევაში parser-ებს შორის განსხვავებულ ქცევას აღწერს; Python 3.14 JSON decoder დოკუმენტაცია ასახელებს object_pairs_hook-სა და non-standard NaN/Infinity-ის ნაგულისხმევ მიღებას. PR #191 strict bytes API ამ ორ ambiguity-ს input boundary-ზე კეტავს.

### Exact-head CI

- PR #190 head `b7503f4c2d5f02feacfef4e4e792cacaf45f8546`: Quality CI [46048328724](https://github.com/maisuradzee/bibmom/actions/runs/46048328724) — SUCCESS, 496 Python tests; CPU-thread workflow [46048328705](https://github.com/maisuradzee/bibmom/actions/runs/46048328705) — GIL-enabled და free-threaded jobs ორივე SUCCESS. საწყისი PR-head run draft validator-ის სავალდებულო ქართული heading-ების გამო ჩავარდა; დრაფტი შაბლონს მოვარგე და ახალ exact head-ზე CI წარმატებით გავიდა.
- PR #191 head `e888bb5c445f81b4ff6ab4f1974019c86daed9f5`: Quality CI [46048363033](https://github.com/maisuradzee/bibmom/actions/runs/46048363033) — SUCCESS, 497 Python tests; CPU-thread workflow [46048363044](https://github.com/maisuradzee/bibmom/actions/runs/46048363044) — GIL-enabled და free-threaded jobs ორივე SUCCESS.
- PR #193 head `30af18b90ec4340a0c5039c8030497199210bc90`: Quality CI [46049582648](https://github.com/maisuradzee/bibmom/actions/runs/46049582648) — SUCCESS, 498 Python tests; Run 36 frozen aggregate reproduction, schema, site build and publication boundary SUCCESS. CPU-thread workflow [46049582641](https://github.com/maisuradzee/bibmom/actions/runs/46049582641) — GIL-enabled და free-threaded jobs ორივე SUCCESS. ეს workflow run PR #193-ში workflow path-filter ცვლილების დასამოწმებლად გაეშვა; მისი ახალი artifacts Run 36 snapshot-ში არ შედის.
- ორივე PR Draft-ად დარჩა; ამ ციკლში არცერთი არ გაერთიანებულა. მათი mergeability=true ამ ჩანაწერში დადასტურებული არ არის.
- Main-ის ბოლო დადასტურებული Quality CI/Pages runs ზემოთ მითითებული 1278 snapshot-ისთვისაა; მიმდინარე main 107a-ზე ახალი deployment არ დამიდასტურებია.

### უსაფრთხოება და შემდეგი ნაბიჯები

- საჯარო საცავში არ დაემატა XLSX payload, respondent-level მონაცემი, operator/personal identifier, credential, private key ან production database content.
- NFA XLSX-ის მიღებამდე საჭიროა data-controller authorization, private inspection, schema, სრული denominator, privacy review და reuse terms.
- INFRA-001-ში შემდეგი ნაბიჯია დამოუკიდებელი security review, recovery owner, separately trusted high-water service და permissioned clean-host restore.
- NOEMA-005-ის შემდეგი ნაბიჯია ფიზიკური მოწყობილობის controlled benchmark; NOEMA-007-ის — authorized Georgian warning/after-action aggregates.
- `data/research.json` main-ზე უცვლელია: 3 Preliminary, 0 Published; PR #193 branch-ში NOEMA-005 Preliminary ჩანაწერი Run 36-ის ახალი aggregate-ებით განახლდა. `RESEARCH_STANDARD.md` და `research/TEMPLATE.md` გადამოწმდა; ახალი Published კვლევა არ შექმნილა.

## Run 37 — scheduled research and engineering audit (2026-11-27)

### Work performed

- **AquaSignal:** added a metadata-only record for the National Food Agency's 2026-08-12 notice about critical hygiene/infrastructure nonconformities and suspension of a drinking-water/lemonade production process in Zugdidi. The public record omits the business name, exact street address, tax identifier and personal data. The notice does not report laboratory water results, sample count, analytes or a denominator; no contamination or prevalence claim is made.
- **NOEMA-005:** audited the Run 36 sanitized artifact snapshot and found that full Linux kernel/glibc platform strings remained in the public runner metadata, contrary to the evidence-minimization intent. PR #193 was corrected to keep only a coarse AWS/Azure hosted-runner family; detailed platform strings and raw thread/process identifiers are excluded. Original ZIP/report hashes and numeric measurements are unchanged. The corrective exact-head CI is pending.
- **NOEMA-007:** re-opened WMO's 2026 MHEWS report page and UNDRR/WMO's 2026-11-12 COP31 update. Source-reported context: 136 countries reported MHEWS as of August 2026; fewer than half had all four pillars; countries with substantial/comprehensive systems had nearly sixfold lower disaster death rates than countries with limited/moderate systems. This is an observational cross-country association, not a causal estimate or Georgian result. PR #194 adds strict URL hygiene to the aggregate warning/evidence-source validator; URLs are not fetched.
- **INFRA-001:** reviewed the strict UTF-8 bytes parser in PR #191. It remains a Draft security change pending independent review; production key custody, offsite retention and clean-host restore remain unimplemented.

### Portfolio and evidence state

- Four active streams remain: AquaSignal, NOEMA-005, NOEMA-007 and INFRA-001.
- No new fifth stream was added.
- No research was promoted to published.
- WRP respondent-level data, private identifiers, raw NFA workbooks, raw thread IDs and secrets were not committed.
- No Supabase project was created and no other project's database was used.

### Pull requests and validation

- PR #190 now includes the metadata-only NFA 2026 inspection event in addition to the 2025 XLSX access lead; exact-head CI is pending.
- PR #193 now minimizes public runner identity; the first CI attempt caught a test assertion that also matched explanatory prose. The assertion was narrowed and a fresh exact-head run is pending.
- PR #194 adds credential-bearing URL rejection for warning and evidence-source URLs; exact-head CI is pending.
- PR #192 carries this portfolio/status synchronization and the Run 37 audit. No new merge or Pages deployment is claimed in this audit.

### Next priorities

1. Obtain an authorized NFA/NEA sample-level data export and its denominator, dictionary, QA/QC and reuse terms.
2. Complete exact-head CI and review for PR #193; retain physical x86-64/ARM64 replication as an external blocker.
3. Run exact-head tests for PR #194 and request independent privacy/GIS/DRR review.
4. Keep PR #191 Draft until independent security review; later require a permissioned clean-host restore before any offsite readiness claim.


### AquaSignal additional official NFA source review

The NFA 2026 State Control Programme (official PDF, accessed 2026-11-27) plans 550 base drinking-water samples: K=1.5 × A=365 = 547.5, rounded to 550, plus approximately 200 additional bottled-water samples, total 750 planned. It also says monitoring of produced bottled-water volume is not planned. These are programme targets, not actual sample counts or results.

The NFA 2026-09-25 Tbilisi kindergarten investigation update reports approximately 70 inspected facilities and 694 combined food/drinking-water samples. It separately reports 129 food samples tested with no violations. The 694 count is not a water-only denominator; the 129 compliant results are food-only. Water-only sample counts and results remain unavailable. No claim is made that drinking water caused the reported norovirus-associated gastroenteritis cases.

### Run 37 validation update

- PR #193 exact-head Quality CI and CPU-thread workflow both succeeded after replacing full runner platform strings with coarse provider-family metadata.
- PR #194 exact-head Quality CI and CPU-thread workflow both succeeded; its URL hygiene guard remains Draft pending independent review.
- PR #190 and PR #192 had new commits after their first CI attempts; latest exact-head checks are being re-evaluated. No Main merge or deployment is claimed from those Draft PRs.


### Main merge update — 2026-11-27

- PR #193 (NOEMA-005 Run 36 artifact reproduction and public runner metadata minimization) merged as `58fe694a4656c1ca020d096af279d1a9eb752e91`. Research remains Preliminary; no peer-reviewed publication claim is made.
- PR #190 (AquaSignal NFA 2025/2026 source access and metadata) merged as `e079dc8141c6a763f1eb79e13c5a56f8f0707c90`. The 750 sample figure remains a plan target, and the 694 investigation count remains combined food/water; actual water-only counts/results are not available.
- PR #192 is refreshed onto the latest main and carries Run 37 portfolio/audit updates; exact-head CI is pending.
- PR #191 remains Draft pending independent security review. PR #194 remains Draft pending fresh exact-head CI and independent privacy/GIS/DRR review.
- Main CI and Pages deployment for the new main tip must be checked separately; no deployment is claimed until its deploy job succeeds.


### Verified Main CI and deployment — 2026-11-27

Main commit `e079dc8141c6a763f1eb79e13c5a56f8f0707c90` passed NOEMA Quality CI run [46056954547](https://github.com/maisuradzee/bibmom/actions/runs/46056954547) and GitHub Pages deployment run [46056954562](https://github.com/maisuradzee/bibmom/actions/runs/46056954562). The site is updated to this exact Main commit.

PR #192 portfolio synchronization head `bcc7f93d95236a880f2b4ebfd0a47a96e2552a03` passed exact-head Quality CI run 46057020903. PR #191 head 1a7d4cc and PR #194 head 24e462d are rebased onto current Main; their new exact-head Quality CI runs are in progress. PR #190 and PR #193 are merged.


## Run 37 — final post-merge status (2026-11-27)

### Main

- Main SHA: `4651645c16b5198723b519d47f841d4523be78f0`.
- NOEMA Quality CI: [46057489444](https://github.com/maisuradzee/bibmom/actions/runs/46057489444) — SUCCESS, 524 Python tests, schema/frozen-result checks, site build and publication-boundary checks passed.
- GitHub Pages: [46057489440](https://github.com/maisuradzee/bibmom/actions/runs/46057489440) — SUCCESS for the exact Main SHA above.
- Site build: 0 published, 3 preliminary; drafts remain outside the public Pages artifact.

### Merged research changes

- PR #193 — NOEMA-005 Run 36 artifact reproduction and public runner identity minimization; merged as `58fe694a4656c1ca020d096af279d1a9eb752e91`.
- PR #190 — AquaSignal NFA 2025/2026 source access and metadata; merged as `e079dc8141c6a763f1eb79e13c5a56f8f0707c90`.
- PR #192 — Run 37 research portfolio, source metadata, draft notes and audit; merged as `4651645c16b5198723b519d47f841d4523be78f0`.

### Remaining Draft work

- PR #194 — URL credential hygiene for NOEMA-007; exact-head Quality CI passed at `24e462dd7e54546f4379159c9b7e6059f657e3fa`; independent privacy/GIS/DRR review remains pending.
- PR #191 — strict restore-attestation JSON ingestion; latest head `88a6e3e3f7934cef625008fbd20b4121b88e376c` has exact-head Quality CI in progress; independent security review remains pending.

### Portfolio

Four streams remain active: AquaSignal, NOEMA-005, NOEMA-007 and INFRA-001. No fifth stream was added. No study was promoted to Published. The repository currently has 40 open PRs and 0 open Issues.


### Remaining Draft PR validation update

- PR #191 latest head `88a6e3e3f7934cef625008fbd20b4121b88e376c`: exact-head Quality CI [46057543397](https://github.com/maisuradzee/bibmom/actions/runs/46057543397) — SUCCESS. The parser normalizes a mocked RecursionError into the domain validation error; independent security review remains pending.
- PR #194 head `24e462dd7e54546f4379159c9b7e6059f657e3fa`: exact-head Quality CI [46057083661](https://github.com/maisuradzee/bibmom/actions/runs/46057083661) — SUCCESS. URL hygiene is documented in RESEARCH_STANDARD; independent privacy/GIS/DRR review remains pending.
- Neither Draft is merged or treated as Published.


## Run 38 audit reference

Detailed audit: [docs/run-audits/2026-11-28-run-38.md](run-audits/2026-11-28-run-38.md). Frozen NOEMA-005 aggregate and reproduction: [summary](../data/noema-005/experiment-002-summary.json), [script](../scripts/reproduce_noema005_experiment_002.py).

Run38 AquaSignal historical baseline/legal crosswalk details: [research draft](../research/drafts/NOEMA-2026-006-nea-2021-2025-groundwater-report-access-lead-2026-11-28.md) and [structured record](../data/noema-006/nea-2021-2025-groundwater-report-access-lead.json).

## Run 38 final merge record

- PR #213 merged at `b3b347bec68e8c22f2781476d55148d576ae028a`.
- Exact-head Quality CI: [46068511890](https://github.com/maisuradzee/bibmom/actions/runs/46068511890) — SUCCESS, 578 Python tests, schema validation, frozen-result reproduction, publication-boundary checks and site build (0 Published, 3 Preliminary).
- Run 39 repository query found 38 open PRs and 0 open Issues; most remaining PRs are legacy Drafts on older base SHAs and need individual triage. No bulk closure was performed.
- Post-merge Main Quality CI [46068624666](https://github.com/maisuradzee/bibmom/actions/runs/46068624666) and Pages [46068624734](https://github.com/maisuradzee/bibmom/actions/runs/46068624734) both succeeded for `b3b347bec68e8c22f2781476d55148d576ae028a`.


## Post-Run38 research-standard synchronization

- PR #214 merged the final portfolio/status synchronization at `8f6203c9a7d671a57c63ec34231b69d60338edc2`.
- PR #215 adds the five-label evidence taxonomy and a template-contract test; final exact-head Quality CI run 46069188841 passed 584 tests and site build (0 Published, 3 Preliminary).
- Main Quality CI [46068888158](https://github.com/maisuradzee/bibmom/actions/runs/46068888158) and Pages [46068888182](https://github.com/maisuradzee/bibmom/actions/runs/46068888182) both succeeded for `8f6203c9a7d671a57c63ec34231b69d60338edc2`.


## Final evidence-standard merge record

- PR #215 merged at `9d2841be14be7fd56b498c0aaac9d1410a585ef8`.
- Final exact-head Quality CI: [46069188841](https://github.com/maisuradzee/bibmom/actions/runs/46069188841) — SUCCESS, 584 Python tests, publication-boundary checks and site build (0 Published, 3 Preliminary).
- This final PR head included the template/standard contract and the post-Run38 status/audit synchronization.
- Run 39 repository query found 38 open PRs and 0 open Issues before the Run 39 audit PR; legacy Drafts require per-PR review.
- Main Quality CI [46069295590](https://github.com/maisuradzee/bibmom/actions/runs/46069295590) and Pages [46069295569](https://github.com/maisuradzee/bibmom/actions/runs/46069295569) both succeeded for `9d2841be14be7fd56b498c0aaac9d1410a585ef8`.


## Run 39 — portfolio, source and engineering audit (2026-11-28)

### Main and CI

- Run 39 audit base Main SHA: `b7c976c481da47470423b219b8e3184c25d09395`.
- Main Quality CI [46069627415](https://github.com/maisuradzee/bibmom/actions/runs/46069627415): SUCCESS, 584 Python tests; schema validation, frozen-result reproduction, benchmark smoke tests, site build and publication-boundary checks passed.
- GitHub Pages [46069627539](https://github.com/maisuradzee/bibmom/actions/runs/46069627539): SUCCESS for the exact Main SHA; site reports 0 Published and 3 Preliminary.
- Repository snapshot before the Run 39 audit PR: 38 open PRs and 0 open Issues. Most remaining PRs are legacy Drafts based on earlier main snapshots; no bulk closure was performed because relevance and supersession need per-PR review.

### Completed research/infrastructure changes

- **AquaSignal — PR #213 merged** as `b3b347bec68e8c22f2781476d55148d576ae028a`. The ENI SEIS II East / EEA C11 indicator records NEA-provided groundwater nitrate data for 2016–2017: 34 of 45 monitoring sites had data, sampling was twice per year, 33/34 site averages were above 10 mg NO3/L by the indicator's “all except one” statement, and all reported averages were below 50 mg NO3/L. Western sites were reported below 1 mg NO3/L, but their count and raw site/sample values are not supplied. This is historical aggregated context, not a 2026 exposure estimate. Matsne Government Decree №58/2014 sets 50 mg/L as NO3- and 0.2 mg/L as NO2- for water within its stated scope; WHO 2026 nitrite guidance of 3 mg/L is not Georgian law. The 2021–2025 NEA RAR remains metadata-only and was not retrieved, hashed or inspected. Exact-head Quality CI [46068511890](https://github.com/maisuradzee/bibmom/actions/runs/46068511890): SUCCESS, 578 tests; post-merge Main CI [46068624666](https://github.com/maisuradzee/bibmom/actions/runs/46068624666) and Pages [46068624734](https://github.com/maisuradzee/bibmom/actions/runs/46068624734): SUCCESS.
- **NOEMA-007 — PR #216 merged** as `5dd5ffeb9402a5228e3f6f0fff76dc6de44a6376`. Runtime and JSON Schema now share the canonical UTC shape `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`; synthetic tests reject arbitrary separators, missing seconds and over-precision, while accepting valid fractional seconds. Exact-head Quality CI [46069012996](https://github.com/maisuradzee/bibmom/actions/runs/46069012996): SUCCESS, 580 tests; post-merge Main CI [46069112780](https://github.com/maisuradzee/bibmom/actions/runs/46069112780) and Pages [46069112858](https://github.com/maisuradzee/bibmom/actions/runs/46069112858): SUCCESS. This is input-contract engineering only; no Georgian operational warning dataset or effectiveness estimate was added.
- **Research standard/template — PR #215 merged** as `9d2841be14be7fd56b498c0aaac9d1410a585ef8`. The five evidence labels FACT, REPRODUCED RESULT, INFERENCE, HYPOTHESIS and UNTESTED IDEA are explicit in the standard and template. The template requires human benefit, provenance, denominators/units, uncertainty, competing explanations and practical-solution safety/feasibility. Exact-head Quality CI [46069188841](https://github.com/maisuradzee/bibmom/actions/runs/46069188841): SUCCESS, 584 tests; Main CI/Pages for that snapshot [46069295590](https://github.com/maisuradzee/bibmom/actions/runs/46069295590) and [46069295569](https://github.com/maisuradzee/bibmom/actions/runs/46069295569): SUCCESS.
- **Run 38 status synchronization — PR #214 merged** as `8f6203c9a7d671a57c63ec34231b69d60338edc2`; Main CI [46068888158](https://github.com/maisuradzee/bibmom/actions/runs/46068888158) and Pages [46068888182](https://github.com/maisuradzee/bibmom/actions/runs/46068888182): SUCCESS.
- **Run 38 evidence-standard status correction — PR #217 merged** as `b7c976c481da47470423b219b8e3184c25d09395`; Main CI/Pages above: SUCCESS. It corrected the final PR #215 test count to 584; Run 39 further corrects the stale open-PR and Pages statements.

### Four-stream review

- **AquaSignal — active / Preliminary.** Historical baseline and legal crosswalk are source-grounded; current NEA RAR, station/sample dictionary, raw sample values, QA/QC, detection limits and reuse terms remain unavailable. Planned NFA counts are not actual water-only denominators.
- **NOEMA-005 — active / Preliminary.** Experiment 002 remains the six-cell hosted comparison (1,152 measured runs) already frozen in Main. No new physical x86-64/ARM64 device run, RSS/native-memory measurement or DRAM-bandwidth result was performed in Run 39; hosted CPU/wall concurrency is not a speedup claim.
- **NOEMA-007 — active / Preliminary.** Canonical timestamp input validation improved; WRP remains global survey context. No authorized Georgian event-level issued/delivered/received/comprehended/feasible/actioned/verified warning dataset is available.
- **NOEMA-INFRA-001 — active / engineering.** Strict restore-attestation and backup-manifest parsers remain synthetic/local controls. No provider, production keys, offsite retention policy or clean-host restore is configured or verified.

### Limitations, safety and next priorities

- No individual NFA/NEA sample, survey respondent, child, business contact, precise private location, credential, key or restricted archive content was added to the public repository.
- No new Supabase project was created and no other project's database was used.
- No research was promoted to Published; the catalogue remains 3 Preliminary and 0 Published.
- Next priorities: obtain an authorized NEA archive and dictionary; perform physical x86-64/ARM64 NOEMA-005 replication with at least 20 repetitions and RSS/DRAM measurements; obtain privacy-approved Georgian warning/after-action aggregates; and conduct an independently owned offsite clean-host restore drill.


## Run 40 — source-grounded water/flood discovery and recovery reference (2026-11-28)

### Main baseline and repository state

- Run 40 research branches are based on Main SHA `2600d28f7c05332ca3faeedcfcbb8c6528d78d08`.
- Baseline Main Quality CI [46070948133](https://github.com/maisuradzee/bibmom/actions/runs/46070948133): SUCCESS, 593 Python tests.
- Baseline Pages deployment [46070948135](https://github.com/maisuradzee/bibmom/actions/runs/46070948135): SUCCESS for the exact Main SHA.
- Repository query after the Run 40 branches: 42 open PRs, 0 open Issues. Existing legacy Drafts were not bulk-closed.

### Research and engineering work completed in separate PRs

- **AquaSignal — PR #223** ([PR](https://github.com/maisuradzee/bibmom/pull/223), head `b684f37a7fc1ff25026ca3ba4a1908c91bda14ae`). Records Government Decree №447/2026, effective from 2026-09-01, including NEA risk-based representative environmental-water monitoring, standardized data formats, public-access/privacy conditions, observational/operational/investigative modes and the groundwater transition to hydrogeological units until groundwater bodies are defined. Adds a Decimal NO3 ↔ NO3-N helper using the WHO-published rounded factor 0.226 and preserves the original water matrix. EEA C11 distinguishes rivers/lakes (mg NO3-N/L) from groundwater (mg NO3/L). Exact-head Quality CI [46072117376](https://github.com/maisuradzee/bibmom/actions/runs/46072117376) and [46072122186](https://github.com/maisuradzee/bibmom/actions/runs/46072122186): SUCCESS, 622 tests; site build reports 0 Published / 3 Preliminary. PR remains Draft pending independent water-chemistry and Georgian legal review. Decree №447 annex DOCX was listed but not retrieved/inspected; no sample-level results or compliance estimate were added.
- **INFRA-001 — PR #224** ([PR](https://github.com/maisuradzee/bibmom/pull/224), head `5a5867a2df69d1bd90de015ced7e474a9847b1fe`). Ports the existing local SQLite high-water compare-and-advance reference model onto the current Main base; adds stricter stream/object-version and expected-state validation, bounded finite busy timeout, idempotent retry, lineage/rollback/equivocation checks and two-connection writer tests. Exact-head Quality CI [46072267138](https://github.com/maisuradzee/bibmom/actions/runs/46072267138) and [46072277514](https://github.com/maisuradzee/bibmom/actions/runs/46072277514): SUCCESS, 610 tests; site build reports 0 Published / 3 Preliminary. PR remains Draft pending independent security review and recovery-owner assignment. This is a single-file SQLite model, not an external trust domain, provider adapter or production anti-rollback service.
- **NOEMA-007 — PR #225** ([PR](https://github.com/maisuradzee/bibmom/pull/225), head `49e6687dd68eca0478b1173810384427236f1091`). Records Government Decree №440/2026: NEA preliminary flood-risk assessment responsibilities, inputs, five principal flood types and two conditional processes, risk criteria, six-year review cycle, methodology deadline 2027-06-01 and first national assessment deadline 2028-12-31. The decree is a risk-discovery/prioritization framework, not evidence of published hazard maps or an operational warning service. One initial test assertion was corrected to match the official text; the final exact-head Quality CI [46072580669](https://github.com/maisuradzee/bibmom/actions/runs/46072580669) and [46072584198](https://github.com/maisuradzee/bibmom/actions/runs/46072584198): SUCCESS, 601 tests; site build reports 0 Published / 3 Preliminary. PR remains Draft pending independent disaster-risk/legal review.

### Four-stream portfolio review

- **AquaSignal — active / Preliminary.** New legal monitoring framework and nitrate unit-basis crosswalk are documented. No Annex DOCX, current NEA annual plan, raw sample results, complete station dictionary or authorized reuse terms have been retrieved. Planned sample counts are not actual denominators.
- **NOEMA-005 — active / Preliminary.** Existing hosted Experiment 002 remains the six-cell, 1,152-measured-run frozen comparison. Run 40 performed no new physical x86-64/ARM64 device experiment, RSS/native-memory measurement or DRAM-bandwidth measurement. No new speedup claim is made.
- **NOEMA-007 — active / Preliminary.** Decree №440 adds a statutory national risk-assessment framework and future milestones. No methodology, first national assessment, risk-area list, hazard/risk maps or authorized Georgian warning/after-action dataset was retrieved.
- **NOEMA-INFRA-001 — active / engineering.** The local high-water reference model is ported in PR #224 but remains a single-host SQLite conformance model. No external authority, provider retention, production key custody or clean-host restore is deployed.

### Evidence, safety and next priorities

- The nitrate conversion factor 0.226 is rounded; it is not suitable as the sole basis for legal pass/fail decisions near a threshold. Surface-water ecological limits, groundwater context and drinking-water compliance remain separate matrices/regimes.
- Decree №447 annexes were not inspected. Operational monthly/quarterly frequency is not generalized to every station/analyte.
- Decree №440 does not measure alert issuance, delivery, receipt, comprehension, feasible action or protective action.
- No personal, child, respondent, business-contact, precise private-location, raw sample, restricted archive, credential or key material was added to the public repository.
- No new Supabase project was created and no other project's database was used.
- No research PR #223–225 was merged in Run 40; all three remain Draft pending their stated independent reviews. The separate status/portfolio synchronization PR #226 contains no research implementation. Main and Pages therefore remain at the baseline SHA above until that documentation-only PR is merged and its deployment is verified.
- The portfolio remains four active streams, three Preliminary catalogue entries and zero Published studies.
- Next priorities: inspect Decree №447 Annex 1/2 and obtain the NEA annual monitoring plan after 2026-12-01; obtain authorized NEA/NFA sample data and dictionary; complete NOEMA-005 physical-device replication with at least 20 repetitions plus RSS/DRAM measurements; monitor the Decree №440 methodology and 2028 assessment milestones; assign an independent recovery owner and design an external high-water trust domain.


## Run 40 post-merge verification — 2026-11-28

- Documentation-only portfolio/status PR #226 merged successfully as Main commit `639ad4485dbf7fc73e523245844cd4bdc663849b`.
- Exact Main Quality CI [46073034749](https://github.com/maisuradzee/bibmom/actions/runs/46073034749): SUCCESS, 593 Python tests; site build job in [46073034713](https://github.com/maisuradzee/bibmom/actions/runs/46073034713): SUCCESS, 0 Published / 3 Preliminary; Pages deploy job in the same workflow: SUCCESS, deployment URL https://maisuradzee.github.io/bibmom/.
- PRs #223, #224 and #225 remain Draft and unmerged pending independent reviews. Their exact-head CI runs remain successful, but each branch is based on prior Main SHA `2600d28f7c05332ca3faeedcfcbb8c6528d78d08`; current Main is `639ad4485dbf7fc73e523245844cd4bdc663849b`. GitHub now reports `mergeable=false` for all three due to base drift. They must be refreshed from current Main and revalidated before any merge.
- Repository snapshot after #226 merge: 42 open PRs, 0 open Issues; 4 active portfolio streams; 3 Preliminary catalogue entries; 0 Published studies.
- The merge of #226 did not merge any of the research implementations from #223–225. No Run 40 research PR is represented as deployed.


## Run 41 — research and engineering continuation (2026-11-28)

**Main base reviewed:** `726c71c9ef1a4e1c00dbc4a44b950e4b371c02f0`.

### Research branches refreshed onto current Main

- **AquaSignal — PR #230**: Government Decree №447/2026 metadata, Georgia nitrate reporting-basis crosswalk, Decimal NO3/NO3-N conversion prototype and WHO 2026 consolidated-edition scope audit. The WHO PDF was inspected: its nitrate/nitrite fact sheet appears on printed pp. 466–472 and states assessment date 2016, while the consolidated edition publication date is 2026-06-17. Exact-head Quality CI succeeded at `8952b8d0d1d25751fbf9ab3219b1999f5e1378c0` (629 tests; exact-head Quality CI run 46075712366); site build: 0 Published / 3 Preliminary. PR remains Draft pending independent water-chemistry and Georgian legal review.
- **INFRA-001 — PR #231**: local SQLite high-water compare-and-advance reference model, canonical ASCII stream identifiers, persisted-state validation and synthetic concurrency/corruption tests. Exact-head Quality CI succeeded at `1265dbe579f88950bb05bb94f4afddc402bb349f` (613 tests); site build: 0 Published / 3 Preliminary. This is same-host conformance only, not an external anti-rollback service or clean-host recovery proof. Draft pending independent security review and recovery-owner assignment.
- **NOEMA-007 — PR #232**: Government Decree №440/2026 preliminary flood-risk assessment framework and statutory milestones. Exact-head Quality CI succeeded at `394babab804457ac59db64cd6044304f5fe52838` (601 tests); site build: 0 Published / 3 Preliminary. It does not establish operational warning delivery or protective-action effectiveness. Draft pending independent disaster-risk and Georgian legal review.

### Other portfolio status

- **NOEMA-005**: no new physical x86-64/ARM64 hardware benchmark was performed in this run. Existing hosted synthetic CPU-thread evidence remains preliminary; access to independently controlled physical devices and RSS/DRAM-bandwidth measurement remains the blocker.
- **AquaSignal**: no NFA/NEA sample-level dataset or paired nitrate/nitrite results were obtained. No local combined ratio, prevalence or compliance result is calculated.
- **NOEMA-007**: no authorized Georgian event-level or warning-response dataset was obtained; statutory risk assessment remains separate from operational warning performance.
- **INFRA-001**: no external high-water authority, production provider adapter, key custody or permissioned clean-host restore was configured.

### Main and publication status

Main remains at `726c71c9ef1a4e1c00dbc4a44b950e4b371c02f0`. Main Quality CI [46073846925](https://github.com/maisuradzee/bibmom/actions/runs/46073846925) and Pages deployment [46073846772](https://github.com/maisuradzee/bibmom/actions/runs/46073846772) both succeeded on that SHA. The three refreshed research PRs are Draft, mergeable and unmerged; no independent external review is recorded. The public site remains at 0 Published / 3 Preliminary until a reviewed publication is approved.


### NOEMA-005 Run 41 independent local-container reproduction

- **PR #233**: [Run 41 20-repeat local threaded reduction reproduction](https://github.com/maisuradzee/bibmom/pull/233), exact head `65ecccf59ff1dc5d401c412b5fa0cfac3e74c3ed`.
- Environment: CPython 3.13.5, GIL-enabled, Linux x86_64 managed container; bare-metal not verified.
- 48 configurations, 20 repetitions each, 960 threaded measurements; full Neumaier state 320/320 correctly rounded, scalar partial merge 280/320, naive 0/320; no threaded configuration exceeded its matching serial baseline.
- Exact-head Quality CI [46076248313](https://github.com/maisuradzee/bibmom/actions/runs/46076248313) succeeded (600 tests; 0 Published / 3 Preliminary). Native thread IDs and host-identifying metadata are not persisted.
- This is not physical x86-64/ARM64, free-threaded, RSS or DRAM-bandwidth evidence. Independent numerical-method review remains required.


## Run 42 — research and engineering continuation (2026-11-28)

- **Main base reviewed:** `1a281d51559bda52552a41a055506630f67059d0` after Run 41 and the current WHO-source provenance update.
- **INFRA-001:** PR #235 fixed an idempotent retry edge in the local SQLite high-water reference model: persisted state is now validated before the retry shortcut. A synthetic regression test reproduces a corrupted `state_version` that previously could be accepted because immutable-candidate comparison intentionally omitted that field. Exact-head Quality CI [46081953230](https://github.com/maisuradzee/bibmom/actions/runs/46081953230) succeeded across all checks; PR #235 merged as `c79ede393ec99a1cb2fe9325c92c80495be6aef5`. This remains a same-host reference model, not an external anti-rollback authority or production recovery service.
- **AquaSignal:** inspected the current WHO consolidated chemical fact-sheet PDF from the 2026 edition. Printed pp. 466–472 retain the nitrate/nitrite fact sheet's assessment date 2016, conversion factor 0.226, nitrate 50 mg/L as ion, nitrite 3 mg/L as ion and combined sum-of-ratios rule. The 2026 consolidated publication date is not a new nitrate/nitrite assessment. Crosswalk source metadata, schema and regression test were updated in PR #237; exact-head Quality CI [46082149711](https://github.com/maisuradzee/bibmom/actions/runs/46082149711) succeeded (666 tests, site build 0 Published / 3 Preliminary). PR #237 merged as `1a281d51559bda52552a41a055506630f67059d0`. WHO guidance remains distinct from Georgian legal standards and raw environmental-water thresholds.
- **NOEMA-007:** NEA's 2026-10-26 notice records a working meeting about a unified national approach to mapping/zoning floods, avalanches, landslides and mudflows under the climate-risk programme. It confirms discussion of methodology, technical-legal harmonization, work plan and expected outcomes only; it does not establish adopted regulations, published maps, risk rankings or operational warning performance. Structured record, closed schema, six tests, portfolio source metadata and explicit CI step merged in PR #238 as `bb4418c1660919637586a753e8bbda8586070781`. Exact-head Quality CI [46082474148](https://github.com/maisuradzee/bibmom/actions/runs/46082474148) succeeded (672 tests; site build 0 Published / 3 Preliminary). The first attempt [46082397472](https://github.com/maisuradzee/bibmom/actions/runs/46082397472) exposed a portfolio-source field-name mismatch (`date` vs required `publication_date`/`accessed_at`); the schema mismatch was corrected and the full suite rerun successfully.
- **NOEMA-005:** Run 41 remains the latest independent local-container reproduction (48 configurations, 20 repetitions/configuration, 960 threaded measurements). No new physical x86-64/ARM64, free-threaded, RSS or DRAM-bandwidth experiment was possible in this run; those remain blocked on controlled hardware.
- **Portfolio:** four active streams remain; no fifth stream was added. NOEMA-007's next step is to monitor formal regulation/map publication and keep map-risk outputs separate from warning-to-action measures. AquaSignal still lacks authorized Georgian sample-level results and complete denominators. INFRA-001 still lacks independent recovery ownership, an external trust domain, provider retention/key custody and a permissioned clean-host restore.
- **Safety:** no raw NFA/NEA workbook, personal/child/respondent data, exact private locations, critical-infrastructure coordinates, credentials or key material were added. No new Supabase project or other project's database was used. All new study outputs remain Draft/Preliminary; no study was marked Published.


### Run 42 final Main snapshot

- Final Main SHA after the Run 42 merges: `bb4418c1660919637586a753e8bbda8586070781`.
- PR #235 (INFRA-001), PR #237 (AquaSignal WHO source-version provenance) and PR #238 (NOEMA-007 hazard-mapping coordination signal) are merged. Each exact-head Quality CI run succeeded; PR #238's initial failure was corrected and rerun.
- Open pull requests: 40; open Issues: 0. Older Draft PRs remain open; several have stale base SHAs and must not be merged without refresh and exact-head CI.
- The PR validation jobs built the public site with 0 Published / 3 Preliminary and passed the publication-boundary check. A post-merge Main Pages deployment job for `bb4418c...` was not independently verified in this run; do not treat Pages as updated until its deploy job is confirmed.
- PR #234 (bounded CI recovery) remains Draft and behind Main. A review comment records a research-integrity issue: it must not move arbitrary URLs from narrative/next-step text into the source list, and must validate credential-like URLs before emitting repair artifacts. No merge is authorized until corrected, refreshed and revalidated.


## Run 43 — Decree №447 annex evidence boundary and CI recovery review (2026-11-28)

- Main baseline reviewed: `4e03bf65ca7ff4986df4680d2f395e1bdc78d2d7`. Four active streams remain; no fifth stream added.
- **AquaSignal:** primary Matsne HTML main text for Decree №447/2026 was rechecked. The official page lists a 46,049-byte DOCX attachment, but the bytes were not retrieved or hashed. Legali.ge's secondary transcription was inspected as a discovery lead for Annex 2 groundwater monitoring frequencies and nitrate/low-flow sampling methods. These annex rows remain `SECONDARY_TRANSCRIPTION_ONLY`; they are not treated as primary facts or automated alert thresholds. A closed-schema audit record, seven synthetic tests, draft note and portfolio provenance update were added.
- **NOEMA-005:** Run 41 remains the latest managed Linux x86_64 GIL-enabled 20-repeat result (48 configurations / 960 threaded measurements). No physical x86-64/ARM64, RSS/native-memory or DRAM-bandwidth experiment was performed in Run 43; no new speedup claim is added.
- **NOEMA-007:** the current NEA public news index was checked. The latest relevant public signals include 25 November 2026 consultations on multi-hazard risk-management plans for seven river basins and the 26 October 2026 hazard-mapping/zoning coordination notice. No adopted technical regulation, published map or Georgian warning-to-action dataset was confirmed.
- **INFRA-001:** reviewed the open bounded-CI-recovery proposal. The existing draft can promote arbitrary narrative URLs into a Sources section. A corrected, separate implementation keeps metadata/heading repairs bounded, never promotes URLs from other sections, flags credential/signed-URL patterns without echoing their values, and retains a final aggregate CI failure gate. It awaits exact-head CI and independent security review.
- No study was promoted to Published. No sample-level, personal, child, respondent, business-contact, precise station-coordinate, restricted attachment, credential or key material was added. No new Supabase project or other project's database was used.
- Next priorities: retrieve/hash the official Decree №447 DOCX; check the annual water-monitoring plan after the 1 December submission deadline; run physical x86-64/ARM64 NOEMA-005 replication with RSS/DRAM measurements; obtain privacy-reviewed Georgian warning/after-action aggregates; complete independent CI recovery security review.


## Run 43 — NOEMA-007 seven-basin plan-status reconciliation (2026-11-28)

- NEA's 2026-11-25 official notice describes a two-day consultation on preparation of multi-hazard risk-management plans for Alazani, Iori, Mtkvari, Khrami-Ktsia, Chorokhi-Acharistskali, Enguri and Rioni; the wider programme target is eleven basins and the listed hazard classes are floods, debris flows, avalanches, landslides, droughts, hailstorms and strong winds.
- GEO Outlook's secondary project-implementer page reports a September 2024–October 2026 project period and says plans were developed for seven basins, but the same sentence also says "for 4 river basins of Georgia". This wording is ambiguous and is not primary proof of approval/adoption/publication.
- The source-status difference is recorded as UNRESOLVED_SOURCE_STATUS. Draft development, consultation/validation, formal approval, publication and implementation are separate states. No 7/11 coverage percentage is calculated.
- The 10-record official spatial-data catalogue remains metadata-only: public/free does not prove direct feature download, an open reuse licence, current model validity or operational forecast capability. No feature payload, station coordinates or household data was added.
- Next: obtain signed/approved plans and official decisions for each basin; compare map/model scale, reference period, scenario assumptions and validation; obtain authorised privacy-reviewed warning/after-action aggregates.


## Run 43 — AquaSignal NEA 2021–2025 report access lead (2026-11-28)

- Re-opened NEA's official 26 November announcement. It says the 2021–2025 groundwater report and nitrate-risk field methodology were prepared and describes quantity/quality assessment, automatic monitoring, historical-data digitization and observation-network development.
- The announcement does not expose sample-level concentrations, station observations or a data dictionary. Its RAR link returned application/octet-stream and could not be inspected; archive remains NOT_RETRIEVED and unhashed.
- Official procurement contract T-100801 (tender NAT260019441), signed 2026-10-09, specifies a final interactive PDF, 50 CD media units and printed deliverables. This does not prove public access, CD contents, formal acceptance or reuse rights.
- Added a strict metadata record/schema, focused tests and a draft access note. No supplier contact/bank/signature data or report payload was copied.
- Next: request the final PDF/public-inspection route, acceptance/delivery act, exact CD contents, data dictionary, checksum and reuse terms from NEA.


## Run 44 — seven-basin programme chronology and CI-recovery review (2026-11-28)

- **Main base:** `a62b2575db43fcf65663abff0367c4e23b78ef60`. README, research standard, project status, template, catalogue, portfolio, schemas, open PRs and issues were audited. Four active streams remain; no fifth stream was added.
- **NOEMA-007:** three NEA primary notices were reconciled: 2025-10-06 (four previously prepared plans discussed; seven remaining basins planned by 2026), 2026-04-02 (risk-assessment validation process/results for seven basins presented to stakeholders), and 2026-11-25 (consultation on preparation of plans for seven named basins). These notices describe different stages. The April notice does not name the basins; the November notice does. No signed final plans, formal approval decisions, public map/model versions or operational warning outcomes were found. GEO Outlook's ambiguous secondary statement remains a separate SECONDARY_CLAIM.
- **NOEMA-007 implementation:** a metadata-only chronology record, closed JSON Schema, seven synthetic tests and a draft note were added on a separate research branch. No coordinates, household data, event telemetry or exposure estimates were added; 7/11 is not reported as an implementation percentage.
- **INFRA-001:** static review of Draft PR #246 at head `4ebb23d898706bb4e0de288063c1fed64a09ed9c` found (a) no explicit required-step manifest in the aggregate CI gate and (b) no maximum URL length or `parse_qsl(max_num_fields=...)` bound in the source URL validator. A review comment records both findings. PR remains Draft/unmerged pending fixes and independent security review.
- **AquaSignal:** no authorized sample-level NEA/NFA data, data dictionary or reuse permission was obtained. The NEA groundwater RAR remains NOT_RETRIEVED. The 2026-12-01 annual-plan submission milestone has not yet passed.
- **NOEMA-005:** no new physical x86-64/ARM64, RSS/native-memory or DRAM-bandwidth experiment was performed; existing frozen evidence is unchanged.
- **Safety:** no personal, child, respondent, exact private-location, station-coordinate, event-level or critical-infrastructure data was added. No new Supabase project was created and no other project's database was used.
- **Next:** obtain signed basin plans and approval decisions; retrieve/inspect the official Decree №447 annex and NEA groundwater report through authorized routes; acquire controlled physical hardware for NOEMA-005; fix PR #246's missing-step and URL-bounds issues before merge.


## Run 44 post-merge verification — 2026-11-28

- PR #247 was merged only after its exact head `62523f36b57e5a44853d11533fd1683b4daa51e6` passed both push Quality CI [46092514227](https://github.com/maisuradzee/bibmom/actions/runs/46092514227) and pull-request Quality CI [46092518104](https://github.com/maisuradzee/bibmom/actions/runs/46092518104); GitHub reported `mergeable=true` before merge.
- Squash merge created Main commit `218021f38ed8bf3732b449fcdfea2cbbb821e96a`.
- Exact Main Quality CI [46092675339](https://github.com/maisuradzee/bibmom/actions/runs/46092675339) succeeded: 712 Python tests; required-file and draft-completeness checks; schema validation; WRP and NOEMA-005 frozen-result reproduction; NOEMA-005 runtime/memory smoke test; public site build and publication-boundary check.
- Exact Main Pages workflow [46092675352](https://github.com/maisuradzee/bibmom/actions/runs/46092675352) completed both build and deploy jobs successfully. Deployment URL: https://maisuradzee.github.io/bibmom/.
- Public catalogue remains 3 Preliminary / 0 Published. The new Georgia seven-basin chronology is a draft evidence note and does not claim formal approval, public map publication or operational warning performance.
- PR #246 remains unmerged pending the two security fixes and independent review; its base is stale after the Main update.


## Run 44 final status-sync verification (2026-11-28)

- Documentation-only PR #248 merged as `cc63c75660096b70cb3f277c5c01b6b55a7200d7`.
- Main Quality CI [46092850682](https://github.com/maisuradzee/bibmom/actions/runs/46092850682) succeeded on that exact SHA: 712 Python tests, all schema/frozen-result/site/publication-boundary checks passed.
- Pages build/deploy [46092850684](https://github.com/maisuradzee/bibmom/actions/runs/46092850684) succeeded on the same SHA; the published site is https://maisuradzee.github.io/bibmom/.
- This entry records the verified Run 44 snapshot; later Main commits may advance independently.


## Run 45 — Georgia early-warning capability signal (2026-11-28)

- **Reviewed Main base:** `f5a7d57d70705f2378a78e76e23013e6fb112835`; this research change is isolated on `research/noema007-cop31-early-warning-capability-signal-2026-11-28` and is not merged.
- **NOEMA-007 primary source:** NEA's 2026-11-16 COP31 notice reports a presentation on hazard assessment/zoning, hydrometeorological observation and forecasting modernization, early-warning mechanisms and digital transformation. It describes agency-reported expansion of the observation network, modern forecasting technologies, improved access to hazard information and the meteo.gov.ge mobile application.
- **Evidence boundary:** the notice provides no station count/inventory, uptime, hazard-specific forecast verification, app reach/accessibility, alert-delivery/receipt/comprehension/action denominators or outcome estimate. The record is classified as an agency-reported capability signal, not an independently reproduced result or evidence of causal impact.
- **Discovery relevance:** the operational gap is now more specific: verify whether reported infrastructure/capability improvements translate into reliable, inclusive last-mile warning receipt and feasible protective action. Keep issued, sent, delivered, acknowledged, understood, feasible and actioned measures separate.
- **Adjacent signal kept out of scope:** NEA's 2026-11-24 COP31 discussion on riverine/marine debris and Black Sea pollution is a separate marine/river pollution discovery lead; it is not merged into drinking-water compliance or warning-effectiveness data.
- **Safety:** only public agency-level claims and public URLs are recorded. No person-level app data, exact private locations, event-level warning logs or critical-infrastructure coordinates are included.
- **Validation:** exact-head CI and merge/deployment status are pending. The note remains in `research/drafts/`; no catalogue status is changed and no study is marked Published.


## Run 45 — AquaSignal Decree 447 monitoring requirements (2026-11-28)

- **Research branch:** `research/aquasignal-decree447-operational-monitoring-2026-11-28`; merged into Main by commit `149b50de310f77e15b7c53627fe79841c2124f8c` (exact Quality CI [46099234948](https://github.com/maisuradzee/bibmom/actions/runs/46099234948) and Pages deployment [46099234911](https://github.com/maisuradzee/bibmom/actions/runs/46099234911) SUCCESS).
- **Primary legal source:** Government Decree №447, adopted 2026-09-15 and effective for relations arising from 2026-09-01; official Matsne HTML Articles 3–7 reviewed.
- **Key requirements:** NEA submits the annual State Water Resources Monitoring Plan by 1 December; the plan is representative/risk-based and standardized; the system includes hydrological, hydrochemical, hydrobiological, hydromorphological and hydrogeological programmes; microbiological monitoring is determined by water-body type, pressures, use and microbial risk; operational monitoring of at-risk bodies is monthly or quarterly; investigative monitoring addresses pollution incidents or unknown reasons for failure to achieve good status.
- **Matrix transition:** priority-substance monitoring in biota/sediment is introduced progressively; until full implementation chemical-status assessment may mainly use water-column results. For substances requiring those matrices, monitoring must start no later than 2028-01-01.
- **Legal scope separation:** the consolidated Water Resources Management Law assigns drinking-water quality state control to NFA (Article 31(3)) and sets 2027-09-01 for a separate human-consumption water quality technical regulation (Article 37(1)(b)(b), commencement in Article 42). Decree 447 is not itself a tap-water compliance standard.
- **Deadline status:** the next 1 December annual-plan deadline is upcoming on 2026-11-28; submission/publication is not yet verified.
- **Limitations:** the official annex DOCX was not downloaded; annex tables, exact station schedules and laboratory methods remain unverified. No sample counts or water-quality results were invented.
- **Safety:** only public legal text and metadata are recorded; no raw lab records, station coordinates, household records or restricted annex payloads were added.
- **Validation:** exact-head CI pending; note remains Draft and is not Published.

## Run 45 — NOEMA-005 ARM64 Run 33 frozen artifact verification (2026-11-28)

- **Research branch:** `research/noema005-arm64-run33-artifact-verification-2026-11-28`; merged via PR #254 as Main commit `0d24667727a8eb90bf420e6c3dc44e4f5185d6d1`; exact-head Quality CI [46100302948](https://github.com/maisuradzee/bibmom/actions/runs/46100302948) SUCCESS. The run only verifies frozen artifacts; no new benchmark is claimed.
- **Frozen source:** experiment `NOEMA-2026-005-REAL-THREADS-ARM64-001`, workflow run [46032894362](https://github.com/maisuradzee/bibmom/actions/runs/46032894362), benchmark head `176ab78fa998060621b4056c65fd2e1f155b1058`.
- **Independent artifact check:** downloaded all four hosted ARM64 ZIP artifacts; all four ZIP SHA-256 values and all four extracted raw-report SHA-256/byte lengths match the frozen manifest. Recomputed aggregates match: 192 configurations / 576 measured runs; naive 0/192, scalar Neumaier 168/192, Neumaier-state 192/192 correctly-rounded runs; GIL-enabled CPU/wall >1.05 samples 4/288; free-threaded 202/288.
- **Performance interpretation:** all four hosted ARM64 runner/runtime cells show median wall-time speedup below 1.0 for all three methods. CPU-time/wall-time above 1.05 indicates concurrent CPU activity, not useful throughput or wall-time acceleration.
- **Innovation:** added an offline artifact verifier that checks ZIP/raw SHA-256, byte lengths, accuracy, CPU/wall counts, median speedups and input-layout hash equivalence without emitting raw thread IDs or full host build strings.
- **Limitations:** hosted runners only; three repetitions per configuration; synthetic cancellation inputs; tracemalloc only; no RSS/native allocator or DRAM bandwidth; no physical-device replication.
- **Next:** pairwise-tree and exact/superaccumulator comparison, representative memory-bandwidth workload, then 20+ repetitions on independent physical x86-64 and ARM64 with RSS/DRAM measurements.
- **Status:** research note remains Draft; no new benchmark is claimed and no catalogue/Published status changes.


### Run 45 verification follow-up

- An independent local SHA-256 pass found one malformed 61-character digest in the verification record for ARM64 Ubuntu free-threaded artifact 15215700349. The downloaded ZIP and frozen summary agree on the corrected 64-character digest; the record was corrected.
- All four raw-report hashes and byte lengths matched. A second independent calculation recomputed each case median from raw `wall_samples_ns` and speedup from the matching serial-baseline median; all stored values matched.
- Regression tests now validate the closed record schema, cross-check every artifact entry against the frozen summary, and reject tampered derived speedups and medians.
- No benchmark measurements or frozen aggregates changed; this is an artifact-record and verifier-integrity correction.


## Run 46 — AquaSignal source-provenance follow-up (2026-11-28)

- Re-opened the NEA 2026-11-26 announcement and followed its official RAR payload link. The announcement page and binary payload are now linked explicitly in the source-access inventory through `announcement_url`.
- The RAR remains `official_report_archive_linked_not_extracted`: no archive SHA-256, internal file list, sample-level schema, data dictionary or reuse terms are claimed.
- A retrieval limitation in this execution environment is recorded narrowly; it does not establish that the official server is generally unavailable.
- No raw water observations, owner identifiers, coordinates or restricted data were imported.

- **PR #255 — AquaSignal source provenance:** merged as `66bd3bf52c42715039798ff4c82649f859c414bc`; exact-head push CI [46100599299](https://github.com/maisuradzee/bibmom/actions/runs/46100599299) and pull-request CI [46100604299](https://github.com/maisuradzee/bibmom/actions/runs/46100604299) both SUCCESS; Main Quality CI and Pages deployment also SUCCESS on the merge SHA.


## Run 46 — INFRA-001 fail-closed CI recovery contract review (2026-11-28)

- **Current proposal:** PR #252, branch `engineering/ci-recovery-required-step-gate-run45-2026-11-28`, remains Draft and unmerged. Its base is `d4ea596120eaca7254052169bc90b532d8210f46`, older than current Main `66bd3bf52c42715039798ff4c82649f859c414bc`; GitHub reports mergeable=false.
- **Finding:** the first workflow-contract validator checked that the final summary step existed and ran always, but did not pin its command or the `STEP_OUTCOMES` environment input. A successful no-op could therefore defeat the intended fail-closed gate while independent checks continued after errors.
- **Fix on PR #252 branch:** require the exact summary command, versioned required-step manifest, `STEP_OUTCOMES`, recovery preflight/report paths and diagnostic upload action/paths; add negative tests for no-op summary, missing input and replaced upload action.
- **Validation:** exact-head Quality CI [46100377784](https://github.com/maisuradzee/bibmom/actions/runs/46100377784) SUCCESS. A review comment records the remaining requirements: refresh from current Main and obtain independent security review.
- **Limitations:** this is workflow-contract hardening, not proof of production backup encryption, external rollback protection, key custody or clean-host recovery. PR #252 is not merged.

## Run 46 — final Main/deployment state (2026-11-28)

- PR #254 merged as Main commit `0d24667727a8eb90bf420e6c3dc44e4f5185d6d1`; exact-head CI [46100302948](https://github.com/maisuradzee/bibmom/actions/runs/46100302948) SUCCESS; Main Quality CI [46100400210](https://github.com/maisuradzee/bibmom/actions/runs/46100400210) and Pages deployment [46100400232](https://github.com/maisuradzee/bibmom/actions/runs/46100400232) SUCCESS.
- PR #255 merged as Main commit `66bd3bf52c42715039798ff4c82649f859c414bc`; exact-head push CI [46100599299](https://github.com/maisuradzee/bibmom/actions/runs/46100599299) and PR CI [46100604299](https://github.com/maisuradzee/bibmom/actions/runs/46100604299) SUCCESS; Main Quality CI [46100659685](https://github.com/maisuradzee/bibmom/actions/runs/46100659685) and Pages deployment [46100659708](https://github.com/maisuradzee/bibmom/actions/runs/46100659708) SUCCESS.
- Research catalogue remains 3 Preliminary / 0 Published; all four portfolio streams remain active. No independent external review is claimed.


## Run 47 — 2026-11-28: warning-to-action reproduction and AquaSignal registry governance

**Main after portfolio/catalogue sync:** 93d90e36ccd17f712bea457f5704bbc95e639bd5

- **NOEMA-007:** PR [#257](https://github.com/maisuradzee/bibmom/pull/257) merged. Pinned LRF 2025 Wave 4 data independently reproduced selected 2026 report aggregates: warning receipt 80.0%; ability to act among warned 63.8%; 1/2/3 warning channels 37.5/50.5/64.2%; plan/agency groups 26.6/49.5/60.0/83.0%; income groups 48.0/46.9/75.5/70.9%. These are descriptive self-reported associations, not causal effects. Georgia base n=99; no national Georgia effectiveness estimate is inferred.
- **AquaSignal:** PR [#259](https://github.com/maisuradzee/bibmom/pull/259) merged. Decree №424's >20 m, post-2026-09-01 fresh-drinking-groundwater well scope, failed/dry wells, 15/10 working-day deadlines, sensitive annex fields and optional sampling states are mapped in a privacy-safe record. No live registry data, personal identifiers, cadastral codes or exact coordinates were accessed.
- **Portfolio/catalogue:** PR [#260](https://github.com/maisuradzee/bibmom/pull/260) merged. Four active streams remain; NOEMA-2026-008 is a Preliminary research item within AquaSignal. No fifth stream was added.
- **Innovation:** the event-level prototype in noema_core/action_readiness.py remains separate from the WRP cross-country survey context; the two-lane architecture is documented in docs/architecture/noema007-warning-to-action-readiness.md.

### Four-stream review

| Stream | Status | Result / blocker |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active | Decree №424 mapped; no authorized NEA registry data or reuse basis |
| NOEMA-005 | Active | Frozen results still reproduce; no new physical x86-64/ARM64, RSS or DRAM experiment |
| NOEMA-007 | Active | WRP action-enablers reproduced; no design-based CI or privacy-approved Georgian event-level validation |
| INFRA-001 | Active | PR #252 remains Draft and mergeable=false; current-Main refresh and independent security review required |

### CI and deployment

- Main Quality CI [46103231565](https://github.com/maisuradzee/bibmom/actions/runs/46103231565): SUCCESS; 756 Python tests passed, one skipped.
- Main Pages deployment [46103231594](https://github.com/maisuradzee/bibmom/actions/runs/46103231594): SUCCESS.
- Site build: 4 Preliminary, 0 Published, 4 generated research HTML pages.
- PR #257 exact-head Quality CI [46102592907](https://github.com/maisuradzee/bibmom/actions/runs/46102592907) and dedicated WRP reproduction [46102593457](https://github.com/maisuradzee/bibmom/actions/runs/46102593457): SUCCESS.
- PR #259 exact-head Quality CI [46102878341](https://github.com/maisuradzee/bibmom/actions/runs/46102878341): SUCCESS.
- PR #260 exact-head Quality CI [46103172098](https://github.com/maisuradzee/bibmom/actions/runs/46103172098): SUCCESS.
- PR #258 closed as superseded without merge.

### Next priorities

1. AquaSignal: obtain NEA register data dictionary and documented third-party access/reuse basis.
2. NOEMA-007: obtain survey variance/replicate-weight documentation and privacy-approved Georgian warning/after-action aggregates.
3. NOEMA-005: run physical x86-64/ARM64 experiments only when suitable hardware is available; measure RSS and DRAM bandwidth.
4. INFRA-001: refresh PR #252 from current Main 93d90e36ccd17f712bea457f5704bbc95e639bd5, rerun exact-head CI and obtain independent security review.

Catalogue: 4 Preliminary, 0 Published. No raw microdata, personal well records, exact coordinates, cadastral identifiers or secrets were added to the public repository.


## Run 48 — 2026-11-28: official warning-authority crosswalk and backup path-binding audit

### NOEMA-007 — official Georgia warning authority/capability crosswalk

- Primary sources reviewed: NEA agency functions; Hydrology Department responsibilities; Geology Department responsibilities; the 2026-07-14 network expansion notice; and the 2025-12-26 multi-hazard forecasting/early-warning workshop notice.
- NEA reports 278 hydrometeorological stations installed and a target of 298 by the end of 2026. The 298 value remains a target, not an achieved November count.
- The same 2026-07-14 notice reports modern monitoring systems on 28 landslide bodies, including 22 integrated into one server platform. These are distinct infrastructure units and are not converted into one coverage percentage.
- NEA's Hydrology Department page describes hydrological forecasts and warnings; the Geology Department page describes geological monitoring, zoning/GIS and groundwater monitoring. The 2025 workshop documents discussion of proposals, not formal protocol adoption.
- No current station inventory, uptime, calibration, hazard-specific forecast skill, warning delivery, comprehension, feasible-action or after-action dataset was retrieved. Agency-reported capacity figures are not independent performance evidence.
- PR [#262](https://github.com/maisuradzee/bibmom/pull/262) merged. It adds a closed JSON Schema, eight focused tests, a draft research note, portfolio source metadata and CI coverage.

### INFRA-001 — local backup artifact path-binding hardening

- Static review found that the streamed artifact verifier checked the opened descriptor before/after hashing but did not confirm that the caller's final path still named the same inode when verification returned.
- PR [#263](https://github.com/maisuradzee/bibmom/pull/263) adds a no-follow final path stat and device/inode comparison, plus deterministic tests for path replacement during hashing and a mismatched path lookup.
- The architecture document records the residual post-return TOCTOU boundary: a future restore consumer must stage verified bytes into a new owner-only temporary file or consume the same verified descriptor and revalidate. The verifier still does not decrypt, authenticate provider storage, prove retention, prevent rollback or perform a restore.
- Exact-head Quality CI [46107271580](https://github.com/maisuradzee/bibmom/actions/runs/46107271580) succeeded with 766 tests (one skipped). PR #263 merged as `4da99b1ae3eda2b9a6b915cd40a0060e2b9c13a9`.

### AquaSignal — no new dataset; access blocker remains

- Rechecked the Decree №447 annual-plan milestone. As of 2026-11-28, the 2026-12-01 submission deadline had not passed; no non-compliance or missed-deadline claim is made.
- Attempted to retrieve the official Decree №447 DOCX annex and NEA 2021–2025 groundwater RAR through the available web/runtime paths. The DOCX endpoint returned an unsupported `application/msword` payload to the web reader; the RAR endpoint returned unsupported `application/octet-stream`; direct runtime downloads failed. No bytes, archive listing, checksum or annex contents were obtained.
- Existing source-access metadata remains accurate: official links are identified, but payload contents, data dictionary, sample-level granularity and reuse terms are unverified. No water-safety threshold or operational alert was changed.

### NOEMA-005 — frozen-result audit only

- Main Quality CI reproduced existing frozen summation, hosted-thread and runtime/memory artifacts successfully.
- No new physical x86-64/ARM64 device experiment, RSS measurement or DRAM-bandwidth benchmark was run in this cycle. No new performance claim is added.

### Four-stream portfolio review

| Stream | Status | Run 48 result / blocker |
|---|---|---|
| AquaSignal / NOEMA-2026-006 | Active / Preliminary | Legal/source-access audit only; DOCX/RAR bytes and reuse terms remain unavailable; 1 Dec deadline is still upcoming as of this audit |
| NOEMA-005 | Active / Preliminary | Frozen reproductions pass; physical device/runtime-memory experiments remain outstanding |
| NOEMA-007 | Active / Preliminary | Official NEA role/capability crosswalk merged; operational warning-chain effectiveness remains unmeasured |
| INFRA-001 | Active / Engineering | Local path-to-inode guard merged; off-host trust domain, retention, anti-rollback and clean-host restore remain unimplemented |

No fifth stream was added. Four catalogue entries remain Preliminary; zero are Published. No private, person-level, exact-coordinate, raw survey or restricted archive data was added to the public repository. No Supabase project or external database was created or used.

### Next priorities

1. AquaSignal: after 2026-12-01, check whether the annual state water-monitoring plan was submitted/published; obtain the official DOCX/RAR through an authorized alternate transfer route and verify its digest before inspecting content.
2. NOEMA-007: obtain a versioned station inventory, formal protocol approval/version and privacy-approved warning-event aggregates with separate stage denominators.
3. NOEMA-005: run physical x86-64/ARM64 comparisons only when suitable hardware is available; include Pairwise/Exact accumulator, RSS and DRAM bandwidth.
4. INFRA-001: refresh PR #252 to current Main, complete failure-injection and obtain independent security review; separately design an external rollback-resistant high-water authority and clean-host restore drill.



## Run 59 — NOEMA-005 independent x86-64 KVM replication (2026-11-28)

- Starting Main: `6038f43548587a35d8dd725bb0fa7480b1a81167`.
- Reused the exact Run 51 C/OpenMP source SHA `5959f479e7f2b45a298975aeed13f3b919a87a77bff64f2b8d649ba72d35d60b`; GCC 14.2.0; two cancellation layouts; 48 method/worker cells; 2 warm-ups and 20 measured repetitions per cell (960 measured runs).
- Second KVM guest reports AMD EPYC 9V74, x86-64, 5 visible CPU IDs and a 4-CPU cgroup quota. Full Neumaier state was exact 20/20 in every worker cell for both layouts; naive and pairwise were 0/20; long double failed the grouped layout. The correctness matrix matches Run 51's separate Intel KVM guest.
- 4-worker median speedup vs serial Neumaier was 2.991x (triplet) and 3.078x (grouped); 5/8-worker rows are oversubscription diagnostics. Runtime is descriptive, not a general speedup claim. CPU/wall ratios above four are retained as quota-period burst diagnostics; no DRAM hardware counters were available.
- Process peak RSS was 281,984/282,112 KiB including the 288 MB input array; no per-method RSS/native-allocation attribution. No bare-metal or ARM64 replication.
- Raw JSONL, compressed/base64 artifact, source/raw/gzip hashes, closed schema, offline verifier and mutation tests are added under NOEMA-005 Run 59. Research remains Preliminary pending physical x86-64/ARM64 replication and independent numerical-method review.
- Portfolio remains four active streams. AquaSignal's NEA 2021–2025 RAR remains linked but uninspected; NOEMA-007 still lacks authorised Georgian warning-event data; INFRA-001 still needs independent security review and an external trust anchor.


## Run 59 — INFRA-001 independent trust-domain architecture (2026-11-28)

- Added `docs/architecture/infra001-independent-trust-domain-and-clean-host-recovery.md`, a public design-only proposal separating immutable backup data, an independently administered signed monotonic checkpoint, and clean-host recovery.
- The design rejects same-host SQLite/high-water state and same-UID 0700/0600 staging as independent trust boundaries; defines role separation, canonical checkpoint fields, anti-rollback and fail-closed restore gates, and pre-implementation acceptance criteria.
- Sources reviewed: NIST SP 800-34 Rev. 1; NIST SP 800-57 Part 1 Rev. 5 final; Rev. 6 Initial Public Draft (not final guidance); CISA 2025 StopRansomware Guide; CISA/FBI/HHS AA20-302A.
- Design only. No private archive, production backup, provider, signing/encryption key, external high-water service or clean-host restore exists. Independent security review, recovery-owner assignment and owner-approved RPO/RTO/retention remain blockers.
- No secrets, credentials, personal data, production endpoint or private backup bytes are added; no Supabase project or other project's database is used.


## Run 60 — AquaSignal monitoring-frame research and INFRA current-Main CI refresh (2026-11-28)

### Main baseline and portfolio

- Starting Main: `a9b44dd36e7b2a88f86c681bf6f2e0de34e599fe`.
- Final Main after AquaSignal PR #311: `e9c0b8e4dd75aa169e95cdbe81a804c8f1b0b0cb`.
- Final documentation Main after PR #313: `ba38115d99a39490c97487d33c2bf2337b3740d8`.
- Final Run 60 Main after PR #314: `053f6a744600625f3e8af1b669ba7c1c5ba1c051`.
- Four independent active streams remain: AquaSignal, NOEMA-005, NOEMA-007 and INFRA-001. No fifth stream was added.
- Catalogue: **12 Preliminary / 0 Published**. NOEMA-2026-016 is a sub-study within AquaSignal, not a new portfolio stream.

### AquaSignal / NOEMA-2026-006

- PR [#311](https://github.com/maisuradzee/bibmom/pull/311) merged on exact head `38ed29ca921e3c16f27b14839b7d137d1f118d91`; exact-head Quality CI [46153938582](https://github.com/maisuradzee/bibmom/actions/runs/46153938582) succeeded: **925 passed, 1 skipped**.
- NEA 2025 aggregate snapshot records distinct reporting frames: 124 combined points, 74 routine hydrogeological points, 50 field-instrumental points, 74 laboratory-sampling points, 681 reported analysis-group counts, 73 surface-water parameter-coverage points and a separate 50-point nitrate field table (30 springs, 19 boreholes, 1 household well). Unique-site overlap and nitrate concentrations are not published in this snapshot.
- Regional laboratory and nitrate rows are checked against their source-table totals. Raw PDF bytes were not available to this runtime; its SHA-256 is not claimed.
- NOEMA-2026-016 cross-checks:
  - NFA official 2023 release: 624 non-compliances and a rounded 12% across more than 5,000 combined food and drinking-water samples. This is not a water-only rate and the exact denominator is not stated in the release.
  - Public Defender's 2025 report: 520 planned drinking-water samples in 2023 and 850 in 2024 (including packaged water). These are plans, not completed sample counts.
  - The same report describes limits in regional/municipal interpretation of published monitoring compilations and recommends a consolidated information platform and locally appropriate communication. Its 35-village/15-municipality/5-region visits are fact-finding, not a representative national water-quality survey.
  - The NFA 2023 XLSX download remains inaccessible to the current reader; no workbook bytes, row-level contents or SHA-256 were obtained.
- New files: `data/noema-006/georgia-drinking-water-monitoring-frames-2023-2024.json` and schema; `noema_core/monitoring_frames.py`; `tests/test_aquasignal_monitoring_frames.py`; `research/preprints/NOEMA-2026-016-georgia-drinking-water-monitoring-disclosure-gap.md`; catalogue and portfolio metadata.
- The new gate rejects planned allocations, mixed food/water summaries, missing exact integer numerator/denominator, missing sampling frame, missing standard/method and invalid numerator bounds. Passing is only a rate-candidate metadata check, not potability, legal compliance or health-risk assessment.
- Sources: [NFA 2023 release](https://nfa.gov.ge/En/News/Details/489); [Public Defender report](https://ombudsman.ge/res/docs/2025041010211260067.pdf); [JECM secondary analysis](https://doi.org/10.52340/jecm.2025.01.25); [NEA 2025 annual report](https://nea.gov.ge/en/Download/File/1444).

### INFRA-001

- PR [#312](https://github.com/maisuradzee/bibmom/pull/312) remains Draft. Exact-head CI was run against Main base `053f6a744600625f3e8af1b669ba7c1c5ba1c051`, head `1e411f583f577d4b05994b38b6777811f9277b47`.
- Exact-head Quality CI [46154613559](https://github.com/maisuradzee/bibmom/actions/runs/46154613559): **938 passed, 1 skipped**. All 50 named CI step bodies match the contract. Public credential preflight scanned 500 tracked UTF-8 text files, skipped 3 binary/non-UTF-8 files and reported 0 configured findings. Since the subsequent docs-only PR #315 will advance Main, PR #312 must be refreshed again before any merge.
- The scanner is pattern-based, does not scan Git history or binary/non-UTF-8 files, and is not proof that the repository contains no secrets. The workflow, manifest and validator share one repository trust boundary. PR #312 remains Draft pending independent security review; no security certification is claimed.
- PR #307 was closed as superseded; its history remains available.

### NOEMA-005 and NOEMA-007

- NOEMA-005: no new physical hardware experiment in Run 60. Run 59's frozen x86-64 KVM replication remains the latest new CPU-thread evidence; bare-metal x86-64 and ARM64, native per-method memory and DRAM counters remain outstanding.
- NOEMA-007: no new privacy-approved Georgian warning-event or after-action data was obtained. No new delivery, comprehension, action or causal-effect metric is claimed.

### CI and deployment

- Main Quality CI after AquaSignal merge [46154013005](https://github.com/maisuradzee/bibmom/actions/runs/46154013005): SUCCESS.
- Main Quality CI after PR #313 [46154330441](https://github.com/maisuradzee/bibmom/actions/runs/46154330441): SUCCESS; 925 tests passed, one skipped.
- Final Run 60 Main Quality CI after PR #314 [46154593098](https://github.com/maisuradzee/bibmom/actions/runs/46154593098): SUCCESS; 925 tests passed, one skipped.
- Main Pages deployment after AquaSignal merge [46154013054](https://github.com/maisuradzee/bibmom/actions/runs/46154013054): SUCCESS.
- Pages deployment after PR #313 [46154330299](https://github.com/maisuradzee/bibmom/actions/runs/46154330299): SUCCESS.
- Final Run 60 Pages deployment after PR #314 [46154593102](https://github.com/maisuradzee/bibmom/actions/runs/46154593102): SUCCESS.
- PR #311 site build and publication-boundary checks passed as part of exact-head CI.
- No private well coordinates, household records, health records, raw sample rows, credentials, private keys or backup bytes were added. No new Supabase project or other project's database was created or used.

### Next priorities

1. AquaSignal: obtain the official NFA 2023 XLSX and data dictionary through an authorized route; reconcile planned 520/850 allocations with actual collected/valid/tested water samples; after 2026-12-01 check the 2027 plan submission, ministerial approval and annexes separately.
2. AquaSignal: obtain NEA 2021–2025 groundwater RAR bytes and reuse terms; verify digest before inspection; keep sample-level, station and public aggregate schemas separate.
3. INFRA-001: independent security review of PR #312, then consider provider-side push protection and an external rollback-resistant trust anchor; no production restore until owner-approved RPO/RTO and clean-host evidence exist.
4. NOEMA-005: physical x86-64/ARM64 experiments with Pairwise/Binned/Exact accumulators, RSS/native allocation, DRAM counters and uncertainty intervals.
5. NOEMA-007: obtain survey variance/replicate-weight documentation and privacy-approved Georgian warning-event aggregates with stage-specific denominators.



### Source-table correction — 2026-11-28

A second inspection of the NEA 2025 report corrected two errors in the first Run 60 transcription. The nitrate table header on p. 11 is **„საყოფაცხოვრებო ჭა“ (household well)**, not „საკონტროლო ჭა“ (control well). The **73 parameter-coverage points** appear under the **surface-water** section on p. 13, not groundwater. Corrected frames: groundwater **124 = 74 + 50**, with **74** laboratory sampling points; surface water **238 points / 2,571 samples / 73 parameter-coverage points**; nitrate field points **30 springs + 19 boreholes + 1 household well = 50**. The previous cross-matrix comparison is withdrawn. PR #316 carries the corrected JSON, schema, validator, tests and documentation. No concentration or compliance conclusion is changed.
