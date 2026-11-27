# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-27 (run 25, post-merge verified main snapshot)
- **საცავი:** https://github.com/maisuradzee/bibmom
- **მდგომარეობის snapshot main:** 21db09ddf1b98de6a58929c63260de16728f4ff8 (PR #137 run-24 follow-up audit/status merge)
- **Main quality CI:** [45981391575](https://github.com/maisuradzee/bibmom/actions/runs/45981391575) — validate job SUCCESS for the exact main snapshot.
- **GitHub Pages deployment:** [45981391564](https://github.com/maisuradzee/bibmom/actions/runs/45981391564) — build and deploy jobs SUCCESS for the exact main snapshot.
- **PR #113 — run-18 audit/status:** merged as `c507a91a213435cf6992abf37c233426882cb973`; exact post-merge quality CI [45946337600](https://github.com/maisuradzee/bibmom/actions/runs/45946337600) and Pages build/deploy [45946337647](https://github.com/maisuradzee/bibmom/actions/runs/45946337647) both SUCCESS.
- **Run 18 audit:** [docs/run-audits/2026-11-27-run-18.md](run-audits/2026-11-27-run-18.md) — two independent streams advanced: NOEMA-005 local KVM native-thread reruns and NOEMA-007 AER/mobility-inclusive review schema; both research PRs remain Draft.
- **Run 17 audit:** [docs/run-audits/2026-11-27-run-17.md](run-audits/2026-11-27-run-17.md) — separate AquaSignal legal data-access and NOEMA-007 flood-risk governance updates in Draft PRs #108 and #109; exact-head quality CI passed for both.
- **Run 16 audit:** [docs/run-audits/2026-11-27-run-16.md](run-audits/2026-11-27-run-16.md) — NOEMA-007 heat-health readiness discovery and NOEMA-005 ARM64 worker/traced-allocation analysis added in separate Draft PRs #103 and #104.
- **Merged in current main:** PR #97 (AquaSignal official NEA groundwater RAR URL/retrieval boundary), PR #102 (run-15 status/audit synchronization) and PR #105 and #106 (run-16 status/audit and post-merge status synchronization), PR #107 (run-16 source/CI correction), and PR #110 (run-17 audit/status), and PR #113 (run-18 audit/status). PR #113's exact main quality CI and Pages build/deploy passed.
- **Open research/engineering PRs:** 24 (0 open Issues). Current clean-base Run 25 Drafts: #138 AquaSignal definition provenance, #139 NOEMA-007 feasible timely-receipt window, #140 INFRA-001 local high-water reference. Superseded branches #101, #129, #130, #134 and #136 are closed without merging; older active drafts remain separately listed in GitHub.
- **Public research catalogue:** 1 preliminary, 0 published. No research item was promoted to Published.
- **Run 25 audit:** [docs/run-audits/2026-11-27-run-25.md](run-audits/2026-11-27-run-25.md) — three independent clean-base research branches advanced; exact-head Quality CI and CPU-thread workflows succeeded for #138–#140; all remain Draft and are not deployed.


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

