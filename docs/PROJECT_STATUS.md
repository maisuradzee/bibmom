# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-27 (run 18, post-merge verified main snapshot)
- **საცავი:** https://github.com/maisuradzee/bibmom
- **მდგომარეობის snapshot main:** c507a91a213435cf6992abf37c233426882cb973 (PR #113 run-18 audit/status merge)
- **Main quality CI:** [45946337600](https://github.com/maisuradzee/bibmom/actions/runs/45946337600) — validate job SUCCESS for the exact main snapshot.
- **GitHub Pages deployment:** [45946337647](https://github.com/maisuradzee/bibmom/actions/runs/45946337647) — build and deploy jobs SUCCESS for the exact main snapshot.
- **PR #113 — run-18 audit/status:** merged as `c507a91a213435cf6992abf37c233426882cb973`; exact post-merge quality CI [45946337600](https://github.com/maisuradzee/bibmom/actions/runs/45946337600) and Pages build/deploy [45946337647](https://github.com/maisuradzee/bibmom/actions/runs/45946337647) both SUCCESS.
- **Run 18 audit:** [docs/run-audits/2026-11-27-run-18.md](run-audits/2026-11-27-run-18.md) — two independent streams advanced: NOEMA-005 local KVM native-thread reruns and NOEMA-007 AER/mobility-inclusive review schema; both research PRs remain Draft.
- **Run 17 audit:** [docs/run-audits/2026-11-27-run-17.md](run-audits/2026-11-27-run-17.md) — separate AquaSignal legal data-access and NOEMA-007 flood-risk governance updates in Draft PRs #108 and #109; exact-head quality CI passed for both.
- **Run 16 audit:** [docs/run-audits/2026-11-27-run-16.md](run-audits/2026-11-27-run-16.md) — NOEMA-007 heat-health readiness discovery and NOEMA-005 ARM64 worker/traced-allocation analysis added in separate Draft PRs #103 and #104.
- **Merged in current main:** PR #97 (AquaSignal official NEA groundwater RAR URL/retrieval boundary), PR #102 (run-15 status/audit synchronization) and PR #105 and #106 (run-16 status/audit and post-merge status synchronization), PR #107 (run-16 source/CI correction), and PR #110 (run-17 audit/status), and PR #113 (run-18 audit/status). PR #113's exact main quality CI and Pages build/deploy passed.
- **Open research/engineering PRs:** #117, #118, #112, #109, #108, #104, #103, #101, #100, #99, #93, #91, #88, #87, #85, #46, #27, #7 and #5 (19 open research/engineering PRs; run-19 status/audit PR #119 is separate; 0 open Issues).
- **Public research catalogue:** 1 preliminary, 0 published. No research item was promoted to Published.


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

