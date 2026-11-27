# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-27 (run 16, verified main snapshot)
- **საცავი:** https://github.com/maisuradzee/bibmom
- **მდგომარეობის snapshot main:** 965e2ac58467220e830a663b48bba58f383648fc (PR #106 status-only follow-up)
- **Main quality CI:** [45928441338](https://github.com/maisuradzee/bibmom/actions/runs/45928441338) — validate job SUCCESS for the exact main snapshot.
- **GitHub Pages deployment:** [45928441209](https://github.com/maisuradzee/bibmom/actions/runs/45928441209) — build and deploy jobs SUCCESS for the exact main snapshot.
- **Run 16 audit:** [docs/run-audits/2026-11-27-run-16.md](run-audits/2026-11-27-run-16.md) — NOEMA-007 heat-health readiness discovery and NOEMA-005 ARM64 worker/traced-allocation analysis added in separate Draft PRs #103 and #104.
- **Merged in current main:** PR #97 (AquaSignal official NEA groundwater RAR URL/retrieval boundary), PR #102 (run-15 status/audit synchronization) and PR #105 and #106 (run-16 status/audit and post-merge status synchronization). PR #106's base snapshot CI and Pages deployment passed.
- **Open research/engineering PRs:** #104, #103, #101, #100, #99, #93, #91, #88, #87, #85, #46, #27, #7 and #5 (14 open PRs; 0 open Issues).
- **Public research catalogue:** 1 preliminary, 0 published. No research item was promoted to Published.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs/worker/workflow/scheduler/supervisor/service |
| DISCOVERY · RESEARCH · INNOVATION | ერთიანი სამუშაო მოდელი | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-005 numerical reduction | active / preliminary | Main-ში x86-64/ARM64 real-thread კვლევა; PR #99-ში ხუთი hosted rerun/raw archive; PR #104-ში ARM64 worker-scaling და traced-allocation-ის derived analysis. ფიზიკური კონტროლირებადი hardware, representative workloads და external numerical review აკლია. |
| NOEMA-006 AquaSignal | active / prototype | Main-ში NEA122 catalogue metadata და NEA 2021–2025 RAR direct URL; archive არ არის მოპოვებული/ჰეშირებული, sample-level schema და reuse terms უცნობია. |
| NOEMA-007 Last-Mile Action Gap | active / draft | Main-ში global evidence და aggregate-only measurement design; PR #100-ში საქართველოს ათი spatial catalogue layer; PR #103-ში heat-health readiness addendum. Local warning-event/health-outcome aggregates და formal heat-health plan status ჯერ არ არის დადასტურებული. |
| NOEMA-INFRA-001 reliability | active / engineering | Main-ში local manifest/hash/signature validation; PR #101-ში single-host SQLite high-water reference model. External trust domain, off-host retention და clean-host restore არ არსებობს. |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; Draft კვლევები არ არის Published. |
| Main quality CI | SUCCESS | run 45928441338 — exact verified baseline SHA. |
| GitHub Pages | DEPLOYED | run 45928441209 — build და deploy SUCCESS exact verified baseline SHA-ზე. https://maisuradzee.github.io/bibmom/ |
| Supabase | NOEMA-სთვის ახალი პროექტი არ შექმნილა | Git-ით ვერსიაკონტროლირებადი JSON/SQLite reference architecture; სხვა პროექტის ბაზა არ გამოიყენება. |

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
