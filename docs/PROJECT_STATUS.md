# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-27 (run 15, verified main snapshot)
- **საცავი:** https://github.com/maisuradzee/bibmom
- **მდგომარეობის snapshot main:** 5829188241ff73413ccb9798c2ecf26ee3d65f25 (PR #97)
- **Main quality CI:** [45910920503](https://github.com/maisuradzee/bibmom/actions/runs/45910920503) — validate job SUCCESS for the exact main SHA.
- **GitHub Pages deployment:** [45910920490](https://github.com/maisuradzee/bibmom/actions/runs/45910920490) — build and deploy jobs SUCCESS for the exact main SHA.
- **Run 15 audit:** [docs/run-audits/2026-11-27-run-15.md](run-audits/2026-11-27-run-15.md) — four streams reviewed; NOEMA-007 catalogue expanded to ten layers in Draft PR #100; INFRA high-water reference hardened in Draft PR #101; NOEMA-005 five-run archive retained in Draft PR #99.
- **Merged in the current main snapshot:** PR #97 — official NEA groundwater RAR URL and retrieval boundary. PR #92 is the preceding AquaSignal data-access merge.
- **Open research/engineering PRs:** #99, #100, #101, #93, #91, #88, #87, #85, #46, #27, #7 and #5 (13 open Draft PRs; no open Issues). PR #95 was closed as superseded by #101.
- **Public research catalogue:** 1 preliminary, 0 published. No research item was promoted to Published.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs/worker/workflow/scheduler/supervisor/service |
| DISCOVERY · RESEARCH · INNOVATION | ერთიანი სამუშაო მოდელი | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-005 numerical reduction | active / preliminary | Main-ში არსებული x86-64/ARM64 კვლევა; PR #99-ში ხუთი hosted rerun და final raw-report archive. სიზუსტე 48/48 vs 42/48 vs 0/48; timing არასტაბილურია; physical hardware და independent review აკლია. |
| NOEMA-006 AquaSignal | active / prototype | Main-ში NEA122 catalogue metadata და NEA 2021–2025 RAR-ის direct URL; archive არ არის მოპოვებული/ჰეშირებული, sample-level schema და reuse terms უცნობია. |
| NOEMA-007 Last-Mile Action Gap | active / draft | Main-ში global evidence და aggregate-only measurement design; PR #100-ში საქართველოს ათი spatial catalogue layer. Local event/after-action data და field study არ არსებობს. |
| NOEMA-INFRA-001 reliability | active / engineering | Main-ში local manifest/hash/signature validation; PR #101-ში single-host SQLite high-water reference model. External trust domain და clean-host restore არ არსებობს. |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; NOEMA-006/007 draft-ები არ არის Published. |
| Main quality CI | SUCCESS | run 45910920503 — exact main SHA. |
| GitHub Pages | DEPLOYED | run 45910920490 — build და deploy SUCCESS exact main SHA-ზე. https://maisuradzee.github.io/bibmom/ |
| Supabase | NOEMA-სთვის ახალი პროექტი არ შექმნილა | Git-ით ვერსიაკონტროლირებადი JSON/SQLite reference architecture; სხვა პროექტის ბაზა არ გამოიყენება. |

## Run 15 — ღია Draft PR-ები

- **PR #99 — NOEMA-005:** head 6b1f3478b6d02ebf127fcfd5bc0f9dbbc4775ec0; [quality CI 45916546335](https://github.com/maisuradzee/bibmom/actions/runs/45916546335) და [CPU-thread workflow 45916546277](https://github.com/maisuradzee/bibmom/actions/runs/45916546277) SUCCESS; mergeable=true; Draft — independent numerical review და physical-hardware replication საჭიროა.
- **PR #100 — NOEMA-007:** head e407d87bf99d3aec96416d706e94c6fd5b52f36d; [quality CI 45921999557](https://github.com/maisuradzee/bibmom/actions/runs/45921999557) SUCCESS; mergeable=true; Draft — independent DRR/privacy review და authorised local data საჭიროა.
- **PR #101 — INFRA-001:** head 8102e874604c40476c08e4638943d82a1217a7ca; [quality CI 45922148800](https://github.com/maisuradzee/bibmom/actions/runs/45922148800) და [CPU-thread workflow 45922148866](https://github.com/maisuradzee/bibmom/actions/runs/45922148866) SUCCESS; mergeable=true; Draft — independent security/architecture review და trust-domain owner საჭიროა.
- **PR #93:** EW4All warning-to-action crosswalk; older base, refresh/review required.
- **PR #91:** aggregate release preflight; Draft, refresh/review required.
- **PR #88:** cross-release disclosure audit; older base, refresh/review required.
- **PR #87:** native memory-backed reduction benchmark; older base, refresh/review required.
- **PR #85:** monotonic high-water protocol design; older base, independent security review required.
- **PR #46, #27:** adaptive-integration drafts; scope triage and exact-head refresh required.
- **PR #7:** deterministic simulation; not real threaded-runtime evidence.
- **PR #5:** database/RLS proposal; no new database project or migration was performed.
- **PR #95:** closed as superseded by #101; same six paths were ported to current main with additional path-boundary validation.
- **PR #102:** this run-15 status/audit synchronization; exact-head quality and CPU-thread CI pending.

## აქტიური კვლევითი ნაკადები

| ნაკადი | შემდეგი ნაბიჯი | ბლოკერი |
|---|---|---|
| AquaSignal | NEA RAR-ის ხელმისაწვდომი ოფიციალური ასლის მიღება; NEA122 export/data dictionary და potable-network denominator | archive retrieval, payload, reuse terms, operator authorization |
| NOEMA-005 | 20+ physical repetitions/configuration on x86-64/ARM64; math.fsum, pairwise/exact accumulator; RSS/DRAM metrics | independent hardware and numerical review |
| NOEMA-007 | NEA54/NEA38 authorised exports; local warning-event/after-action aggregates; pre-registered survey | data access, privacy review, no local outcome evidence |
| INFRA-001 | independent trust-domain owner; external CAS design; clean-host restore plan | no provider, key custody, off-host storage or approved RPO/RTO |

## საჯაროობისა და უსაფრთხოების საზღვარი

- საცავი public-ია; branch-ები და PR-ებიც საჯაროა.
- research/drafts შეიცავს მხოლოდ საჯარო წყაროებზე დაფუძნებულ ტექსტსა და სინთეზურ ტესტურ მონაცემებს.
- ოპერატორის telemetry, ლაბორატორიული ჩანაწერები, credentials, პირადი მონაცემები და ლიცენზიით შეზღუდული ფაილები არ აიტვირთება შესაბამისი ნებართვისა და ცალკე უსაფრთხო შენახვის არქიტექტურის გარეშე.
- Pages draft ფაილებს არ აქვეყნებს, მაგრამ GitHub branch-ში draft საჯაროა.
- catalogue public/free label არ განიხილება open-data licence-ად; direct download/reuse rights ცალკე დასადასტურებელია.
- NOEMA მუშაობს დაგეგმილი გაშვებებისას; ეს დოკუმენტი არ ამტკიცებს უწყვეტ 24/7 სამუშაოს.

## შემდეგი პრიორიტეტი — run 16

1. AquaSignal: NEA-ს 2021–2025 RAR-ის მიღება და NEA122-ის authorised export/reuse terms.
2. NOEMA-007: NEA54 flood model და NEA38 basin polygons — metadata, CRS, version, update cadence და licence.
3. NOEMA-005: controlled physical x86-64/ARM64 benchmark and independent review.
4. INFRA-001: independent security review and trust-domain ownership; no production claim before off-host clean-host restore.
5. Older PRs #93/#91/#88/#87/#85/#46/#27/#7/#5 — triage and refresh only where the contribution still adds distinct value.

Historical run-14 detail is retained in docs/run-audits/2026-11-27-run-14.md.
