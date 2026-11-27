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
- **Open research/engineering PRs:** #112, #109, #108, #104, #103, #101, #100, #99, #93, #91, #88, #87, #85, #46, #27, #7 and #5 (17 open research/engineering PRs; status-only PR #110 is separate; 0 open Issues).
- **Public research catalogue:** 1 preliminary, 0 published. No research item was promoted to Published.


## Run 19 — exact research/engineering PR state

- **Main base snapshot:** `84512d4fa57235b06842568ef933a72b2edcd698`.
- **PR #117 — NOEMA-007 mobile-inclusive AER sampling pre-registration:** head `75abf94f3d7c9cc905415844ce60a06614699a6b`; [quality CI 45947883409](https://github.com/maisuradzee/bibmom/actions/runs/45947883409) SUCCESS; [actual CPU-thread workflow 45947883396](https://github.com/maisuradzee/bibmom/actions/runs/45947883396) both GIL-enabled and free-threaded jobs SUCCESS; GitHub mergeable=true. Draft; not merged pending independent accessibility/privacy review and a competent-authority event-review mandate.
- **PR #118 — INFRA-001 restore attestation gate:** head `7d13db087ef9f1d0ad2e959545ea12bd4ec63c82`; [quality CI 45947828733](https://github.com/maisuradzee/bibmom/actions/runs/45947828733) SUCCESS; [actual CPU-thread workflow 45947828727](https://github.com/maisuradzee/bibmom/actions/runs/45947828727) both GIL-enabled and free-threaded jobs SUCCESS; GitHub mergeable=true. Draft; not merged pending independent security review, recovery-owner assignment and a permissioned clean-host restore drill.
- **Superseded drafts:** PR #115 closed in favor of #117; PR #116 closed in favor of #118. Their replacement branches were recreated from the current main base; no code was merged from the superseded drafts.
- **Open PRs:** 19; **open Issues:** 0. Research catalogue remains 1 Preliminary / 0 Published.
- **Deployment:** neither research PR was merged; no Pages deployment is claimed for either PR branch. Latest verified Pages deployment remains the c507a91 main snapshot above.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs/worker/workflow/scheduler/supervisor/service |
| DISCOVERY · RESEARCH · INNOVATION | ერთიანი სამუშაო მოდელი | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-005 numerical reduction | active / preliminary | PR #87-ზე დაემატა ორი ადგილობრივი 96 MiB OpenMP/KVM rerun, 15-კონფიგურაციანი raw JSON ანგარიშები და ხუთი provenance/accuracy ტესტი; exact-head quality CI 45945835133 SUCCESS. ერთი KVM x86-64 VM, 4-CPU quota; 8-worker oversubscribed. ფიზიკური hardware და representative workload ჯერ არ არის. |
| NOEMA-006 AquaSignal | active / prototype | Main-ში NEA122 catalogue metadata და NEA 2021–2025 RAR direct URL; PR #108-ში Article 32(3) NEA data-request route, Article 31(3) NFA role და Resolution No.424 registry boundary. Archive და sample-level payload კვლავ უცნობია; PR #108 Draft-ია. |
| NOEMA-007 Last-Mile Action Gap | active / draft | PR #112-ზე დაემატა 2026-07-15 UNDRR-led After-Event Review მეთოდოლოგიის crosswalk, mobile-population inclusion-ის review protocol და დახურული aggregate-only finding-register schema; 8 synthetic schema checks და exact-head quality/CPU CI SUCCESS. ქართული event data/field pilot არ არსებობს. |
| NOEMA-INFRA-001 reliability | active / engineering | Main-ში local manifest/hash/signature validation; PR #101-ში single-host SQLite high-water reference model. External trust domain, off-host retention და clean-host restore არ არსებობს. |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; Draft კვლევები არ არის Published. |
| Main quality CI | SUCCESS | run 45934655564 — exact verified main SHA 0a6dbe4c4c0c18f49540f966c89d6b53b99425bf. |
| GitHub Pages | DEPLOYED | run 45934655643 — build და deploy SUCCESS exact main SHA 0a6dbe4c4c0c18f49540f966c89d6b53b99425bf-ზე. https://maisuradzee.github.io/bibmom/ |
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
