# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-26
- **საცავი:** https://github.com/maisuradzee/bibmom
- **ძირითადი branch:** main
- **მიმდინარე main:** `7d9a7e8aef633b3d3ac371e62522fcd0be0b151d` (PR #72 merge)
- **ბოლო დადასტურებული engineering merge:** PR #72 — AquaSignal external checkpoint comparison; მანამდე PR #70 status sync და PR #68/#69 (NOEMA-007 / backup manifest runtime validator) merged.
- **NOEMA-005:** PR #63-ით დაემატა 2,068-case full-width/tie-adjacent MPFR 4.2.1 oracle; hosted x86-64 და ARM64 თითოეულზე 2,068/2,068 bitwise match. PR #66-ით ორიგინალური CPU-thread artifact ZIP-ების SHA-256 და raw report aggregates დამოუკიდებლად გადამოწმდა. Neumaier state merge 48/48, scalar Neumaier 42/48, naive 0/48; wall-time speedup არ დადასტურებულა. კვლევა preliminary რჩება.
- **NOEMA-INFRA-001:** PR #57 same-host restore-drill, PR #64 strict non-secret manifest schema და PR #69 executable Draft 2020-12 runtime validator main-შია; off-host encryption, detached signature verification, key custody, provider retention და clean-host recovery ჯერ არ განხორციელებულა.
- **Latest verified quality CI:** PR #72 exact head, run 45853277201 — SUCCESS; ყველა unit/reproduction/site-build/publication-boundary step წარმატებულია. Main post-merge quality run for `7d9a7e8` ამ audit-ში ჯერ არ დადასტურებულა.
- **Latest verified CPU-thread workflow:** PR #71 exact head, run 45850716742 — GIL-enabled და free-threaded ორივე SUCCESS; PR #73-ის დამატებითი CPU-thread workflow run 45853281867-იც ორივე job-ით SUCCESS.
- **Latest confirmed Pages deployment:** run 45850024682 — build და deploy SUCCESS for `990ba166c7422257291ba2abfc9278ea7099c654`; deployment for current main `7d9a7e8` ამ audit-ში ჯერ არ დადასტურებულა.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | რეალიზებულია როგორც შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs.py, worker.py, workflows.py, scheduler.py, supervisor.py, service.py |
| DISCOVERY · RESEARCH · INNOVATION მოდელი | PR #25-ით main-შია | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-002 SignBase audit | შესრულებული კვლევითი ჩანაწერი | data/audits და research archive |
| NOEMA-003 climate analysis | დრაფტი / გამეორებადი; ERA5 validation gate ვერ გაიარა და საბოლოო დასკვნაში არ გამოიყენება | data/noema-003, scripts და tests |
| NOEMA-005 summation | preliminary; full-width MPFR oracle, CPU-thread results და artifact provenance audit main-შია | 2,068/2,068 MPFR matches თითო hosted x86-64/ARM64-ზე; artifact ZIP SHA-256 და 48-case aggregate-ები გადამოწმებულია; Neumaier-state 48/48, scalar 42/48, naive 0/48; speedup არ დადასტურებულა |
| NOEMA-006 AquaSignal | draft + software prototype; საველე ვალიდაცია არ ჩატარებულა | research/drafts/NOEMA-2026-006-aquasignal-water-early-warning.md, docs/AQUASIGNAL_MVP.md, noema_core/aquasignal.py |
| NOEMA-INFRA-001 reliability | active / engineering; same-host restore-drill, strict metadata schema and runtime JSON Schema validator merged | PR #57, #64, #69; 7 structural schema tests + 7 runtime manifest tests; no real manifest, encryption, signature verification, provider/key custody or clean-host recovery |
| NOEMA-007 Last-Mile Action Gap | draft / discovery + aggregate-only prototype; UNDRR 2026: 64/136 ქვეყანა ოთხივე pillar-ს აცხადებს; WMO-ს 35 validated roadmap-იდან 20-ს აქვს მკაფიო ბიუჯეტი (57.1429%), მათზე ჯამური მოთხოვნა დაახლოებით USD 1.38bn-ია; NEA 2026-11-25 ადასტურებს შვიდი აუზის გეგმებზე კონსულტაციას; საქართველოს last-mile action ჯერ არ გაზომილა | research/drafts/NOEMA-2026-007-global-early-warning-action-gap.md; `data/noema-007/`; `noema_core/action_readiness.py` |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; schema version 2. NOEMA-006 draft კატალოგში არ არის |
| GitHub Pages | ბოლო deployment წარმატებულია | run 45842833997 — build და deploy jobs SUCCESS; https://maisuradzee.github.io/bibmom/ |
| Main quality CI | წარმატებულია | run 45842834069 — 329 tests; validate job SUCCESS |
| Supabase | NOEMA-ს ცალკე მონაცემთა ბაზა არ შექმნილა | ამჟამად გამოიყენება Git-ით ვერსიაკონტროლირებადი JSON კატალოგი; სხვა პროექტის ბაზა არ გამოიყენება |

## ბოლო NOEMA-005 merge/deployment audit

- PR #23 — ARM64 real-thread replication — დახურულია; შედეგები და პროტოკოლი main-შია.
- PR #24 — final-head ARM64 verification archive — დახურულია; final verification, aggregate accuracy და artifact hashes main-შია.
- Main-ის ბოლო commit არის 3ca18de8c05511d31b9b76928ca8a7c285fce0d7.
- PR #24 quality run 45757198868 — SUCCESS, 207 Python tests.
- PR #23 Pages deployment run 45756851227 — build და deploy SUCCESS.
- Main quality run 45757333992 — SUCCESS.
- Main Pages deployment run 45757333935 — build და deploy SUCCESS.
- კვლევის ოთხ ARM64 batch-ში Neumaier compensation-state-ის შედეგი 768/768 იყო; scalar Neumaier 672/768; naive scalar 0/768. ოთხივე final-head runtime-cell median wall-time speedup 1-ზე ნაკლები იყო. Timing-ის ზოგადი აჩქარება არ დადასტურებულა.
- დამოუკიდებელი გარე რეცენზია არ ჩატარებულა; published სტატუსი არ მინიჭებულა.

## მიმდინარე ღია Draft PR-ები

- PR #46 — adaptive integration core capability-binding security hardening; Draft/open; exact-head CI run 45813255101 was successful on its earlier head, but the PR has not been revalidated against the latest main and remains unmerged.
- PR #27 — adaptive integration engine foundation; Draft/open; previous quality checks are historical and must be rerun on a refreshed exact head before merge.
- PR #7 — NOEMA-005 deterministic 330-case cross-platform simulation; this does not test real threaded runtime.
- PR #5 — proposed database/RLS architecture; no PostgreSQL integration, Supabase project creation or migration has been performed.

PR #68 and PR #69 were merged in this run. No new Supabase project was created and no other project's database was used.

## NOEMA DISCOVERY — მიმდინარე აღმოჩენა

WHO-ის 2026-11-19 ფაქტების ფურცელი აღწერს გლობალური სასმელი წყლის უსაფრთხოების მნიშვნელოვან ტვირთს. საქართველოში კი ოფიციალური წყაროები უკვე აღწერს წყლის მონიტორინგის ქსელსა და ლაბორატორიულ კონტროლს. ამიტომ NOEMA არ ამტკიცებს, რომ საქართველოში მონიტორინგი არ არსებობს. შესამოწმებელი შესაძლებლობაა არსებული, ნებადართული sensor/lab მონაცემების შეკავშირება და ოპერატორისთვის ადრეული, აუდიტირებადი სიგნალების მიწოდება.

AquaSignal-ის პირველი ვერსია მხოლოდ ოპერატორის გადაწყვეტილების მხარდაჭერაა. ის არ ცნობს პათოგენებს, არ ადასტურებს წყლის ვარგისიანობას, არ აგზავნის საჯარო გაფრთხილებებს და არ მართავს ფიზიკურ მოწყობილობებს. ზღვრები უნდა მოდიოდეს კონკრეტული ობიექტის დამტკიცებული Water Safety Plan-იდან.

## საჯაროობისა და უსაფრთხოების საზღვარი

- საცავი public-ია; branch-ები და PR-ებიც ყველასთვის ხილულია.
- ამ branch-ში თავსდება მხოლოდ საჯარო წყაროებზე დაფუძნებული ტექსტი და სინთეზური ტესტური მონაცემები.
- ოპერატორის telemetry, ლაბორატორიული ჩანაწერები, credentials და პირადი მონაცემები არ აიტვირთება ნებართვისა და ცალკე უსაფრთხო შენახვის არქიტექტურის გარეშე.
- Pages draft ფაილებს არ აქვეყნებს, მაგრამ GitHub branch-ში draft საჯაროა.
- source permission უცნობია — წვდომა/ხელახალი გამოყენება იბლოკება.

## შემდეგი პრიორიტეტი

1. AquaSignal-ის სინთეზური unit tests და სრული CI წარმატებით დასრულდეს.
2. მოიძებნოს ოფიციალური, ნებადართული data dictionary და ისტორიული paired sensor/lab მონაცემის ხელმისაწვდომობის დადასტურება.
3. საველე პილოტამდე წინასწარ განისაზღვროს baseline, detection delay, sensitivity, positive predictive value და false-alert rate.
4. PR #19 განახლდეს current main-ზე; merge-მდე თავიდან გაეშვას სრული CI და restore drill. შემდეგი ინფრასტრუქტურული ეტაპია encrypted off-host backup, retention/rotation და scheduled restore drills.
5. NOEMA-005 დარჩეს preliminary, სანამ დამოუკიდებელი გარე რეცენზია არ დასრულდება.

**მნიშვნელოვანი:** NOEMA მუშაობს დაგეგმილი გაშვებებისას; ეს დოკუმენტი არ ამტკიცებს უწყვეტ 24/7 სამუშაოს.


## NOEMA Research Portfolio — 2026-11-26

ერთიანი პორტფელი: `data/research-portfolio.json`; schema: `data/research-portfolio.schema.json`; ავტომატური კონტრაქტის ტესტები: `tests/test_research_portfolio.py`.

| ნაკადი | სტატუსი | მთავარი ბლოკერი / შემდეგი ნაბიჯი |
|---|---|---|
| NOEMA-2026-006 AquaSignal | active / prototype; PR #29 Draft/open | main-ში synthetic-tested rules engine; PR #29 exact-head CI SUCCESS (run 45780586227), სრული assessment evidence-ზე operator clearance; field validation/data access still blocked |
| NOEMA-2026-005 numerical reduction | active / preliminary | native C/OpenMP და ალტერნატიული accumulator-ის შედარება; გარე რეცენზია |
| NOEMA-2026-007 Last-Mile Action Gap | active / draft | საქართველოს ერთ აუზში საჯარო, არაპერსონალური workflow/data dictionary და სამი კონტექსტის შედარება |
| NOEMA-INFRA-001 backup/provenance | active / engineering | PR #19-ის WAL-mode regression fix-ის exact-head CI |

NOEMA-2026-005-ის ოთხ ARM64 batch-ში Neumaier compensation-state სწორად დაემთხვა reference-ს 768/768 run-ში; scalar Neumaier — 672/768; naive scalar — 0/768. Timing-ის შედეგები ზოგადი wall-time აჩქარების დასამტკიცებლად საკმარისი არ არის.

NOEMA-2026-007-ის დოკუმენტურმა discovery-მ დაადასტურა, რომ საქართველოში უკვე ვითარდება მრავალსაფრთხიანი გაფრთხილების ICT, მონიტორინგის სადგურები და 11 მდინარის აუზის პროგნოზირების პლატფორმები. ამიტომ კვლევის ფოკუსია არა ახალი ოფიციალური alerting სისტემის დუბლირება, არამედ გაფრთხილებიდან მოქმედებამდე გაზომვადი ხარვეზის დადგენა.

PR #19-ის წინა CI failure კონკრეტულად ეხებოდა WAL-mode backup-ის უარყოფის ტესტს: SQLite-ის immutable read-only რეჟიმი `PRAGMA journal_mode`-ს `delete`-ად აჩვენებდა, მიუხედავად იმისა, რომ ფაილის header WAL mode-ს ინახავდა. იმავე infrastructure branch-ზე დაემატა header byte 18/19-ის შემოწმება და გამკაცრებული regression fixture; ამ ცვლილების CI შედეგი ჯერ pending-ია.

ეს პორტფელი ასახავს დაგეგმილ და დადასტურებულ სამუშაოს; ის არ ნიშნავს ერთდროულ რეალურ გამოთვლით შესრულებას ან უწყვეტ მუშაობას.


## NOEMA run audit — 2026-11-26 (after portfolio merge)

- **Current main:** `062574f7ca5c6671a7a2cb6bcccd99aa5e64b3e1`; PR #28 (four-stream Research Portfolio and NOEMA-007 discovery) was merged after exact-head quality and CPU-thread checks passed.
- **Main quality CI:** [run 45786199787](https://github.com/maisuradzee/bibmom/actions/runs/45786199787) — SUCCESS.
- **GitHub Pages:** [run 45786199915](https://github.com/maisuradzee/bibmom/actions/runs/45786199915) — build and deploy jobs SUCCESS; deployment API reported success for commit `062574f7ca5c6671a7a2cb6bcccd99aa5e64b3e1`.
- **Research portfolio:** `data/research-portfolio.json` contains four active streams. The separate public research catalogue remains 1 preliminary / 0 published; no study was promoted to Published.

### Active stream audit

| Stream | Current evidence | Blocker / next step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | PR #29 adds complete `SignalAssessment` clearance binding and chronology protection: closure cannot predate operator acknowledgement. Exact-head quality CI [45786118869](https://github.com/maisuradzee/bibmom/actions/runs/45786118869) passed (240 Python tests plus frozen research/site checks). | PR #29 is 8 commits ahead / 1 behind current main after PR #28; refresh and rerun. No authorized paired sensor/lab data or field validation. |
| NOEMA-2026-005 numerical reduction | PR #30 exact-head quality [45785996364](https://github.com/maisuradzee/bibmom/actions/runs/45785996364), native OpenMP [45785996326](https://github.com/maisuradzee/bibmom/actions/runs/45785996326), and GIL/free-threaded matrix [45785998339](https://github.com/maisuradzee/bibmom/actions/runs/45785998339) passed. Native workflow validated 20 generated cases and observed 1/2/4/8 OpenMP workers. | Audit found the committed local report has 10 cases while declaring 20 expected; do not use it as a frozen result. Repair and add frozen-report validation. PR #30 is 4 ahead / 1 behind current main. No independent hardware replication. |
| NOEMA-2026-007 warning-to-action gap | Discovery draft and portfolio merged via PR #28. Official UNDRR/WMO and Georgian NEA sources document existing systems and a possible last-mile measurement gap. | No municipal alert-delivery/acknowledgement/action aggregate data or field study; do not duplicate official alerting. |
| NOEMA-INFRA-001 reliability | PR #19's prior WAL-header/backup-restore CI passed on its older branch head. | PR #19 is 32 ahead / 7 behind current main and `mergeable=false`; refresh/rebase and rerun full CI/restore drill. Encryption, off-host storage, retention and scheduled restore drills remain absent. |

### Other open engineering PRs

- PR #27 (adaptive integration engine): previous quality and CPU-thread CI passed on its earlier head; after PR #28 merged it is 37 commits ahead / 1 behind and GitHub reports `mergeable=false`. Refresh and rerun exact-head CI before merge.
- PR #30: initial exact-head CI failed due to C syntax and Python test syntax defects; both were repaired. The corrected exact head passed all three workflows. The frozen-result completeness issue remains open as noted above.
- PR #29: two new regression tests protect acknowledgement/closure chronology; exact-head quality passed. Branch refresh remains required.

### Public-data and publication boundary

- Only public-source research text and synthetic fixtures are committed. No operator telemetry, private laboratory records, credentials, or personal data were added.
- No new Supabase project or external database was created.
- Drafts remain drafts. No independent external review has been completed for these new studies; Published status was not assigned.
- NOEMA advances during scheduled runs only; this status does not claim continuous background execution.


## NOEMA run audit — 2026-11-26 (AquaSignal lifecycle + native OpenMP)

This section supersedes earlier status snapshots in this file where PR #29 or PR #30 are still described as open/diverged.

- **Current main:** `8bb91db62105a83391986d06e88f198b5c7d1670`.
- **PR #29 AquaSignal incident lifecycle:** merged at `5b0f8ea791ca9eee1ff5bc96cbc811ebfe88b960`. Exact-head quality CI [45791736630](https://github.com/maisuradzee/bibmom/actions/runs/45791736630) passed 252 Python tests. A first CI run exposed an acknowledgement-replay ordering regression; it was fixed by checking exact idempotent replay before enforcing monotonic timestamps for new events.
- **PR #30 native OpenMP:** merged at `8bb91db62105a83391986d06e88f198b5c7d1670`. Exact-head quality CI [45792697056](https://github.com/maisuradzee/bibmom/actions/runs/45792697056) passed 264 Python tests; native OpenMP [45792697063](https://github.com/maisuradzee/bibmom/actions/runs/45792697063) passed 20 cases and observed 1/2/4/8 workers; GIL-enabled/free-threaded CPU matrix [45792697098](https://github.com/maisuradzee/bibmom/actions/runs/45792697098) passed.
- **Main quality CI:** [45792961744](https://github.com/maisuradzee/bibmom/actions/runs/45792961744) — SUCCESS, 264 Python tests plus schema, frozen-result, site-build and publication-boundary checks.
- **GitHub Pages:** [45792961703](https://github.com/maisuradzee/bibmom/actions/runs/45792961703) — build and deploy jobs SUCCESS for main commit `8bb91db62105a83391986d06e88f198b5c7d1670`.
- **Research catalogue:** remains 1 preliminary / 0 published. The native OpenMP extension remains a draft addendum; no independent hardware replication or external numerical-method review has been completed.
- **Research portfolio:** four active streams; current statuses are in `data/research-portfolio.json`.

### Active stream status

| Stream | Confirmed progress | Blocker / next step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | PR #29 merged. Immutable incident state validates event chronology, full assessment binding, severity history and acknowledgement/closure audit events. Backdated post-ack assessments are rejected; identical acknowledgement replay remains idempotent. | Synthetic in-memory prototype only. Obtain authorized paired sensor/lab data and site-approved Water Safety Plan limits; then preregister a field evaluation. |
| NOEMA-2026-005 numerical reduction | PR #30 merged. Full raw OpenMP samples archived in `data/noema-005/native-openmp-raw-report-2026-11-26.json`; summary validator reproduces medians, CPU/wall ratios and speedups and checks source/blob provenance. | Native OpenMP evidence is from one hosted x86-64 runner. Add pairwise-tree, long-double and binned/exact baselines; run independent native ARM64/x86-64 replications and seek external review. |
| NOEMA-2026-007 Last-Mile Action Gap | Existing discovery draft retains official UNDRR/WMO and Georgian NEA evidence; no new local dataset was obtained this cycle. | No municipal alert-delivery, acknowledgement or action-completion aggregates; select one basin/municipal workflow and obtain authorized aggregate data without duplicating official alerting. |
| NOEMA-INFRA-001 reliability | Portfolio audit completed; no new backup/restore code was merged this cycle. | PR #19 is 32 commits ahead / 46 behind current main and `mergeable=false`. Refresh carefully, rerun exact-head CI and restore drill; encrypted off-host backup, retention/rotation and scheduled restore exercises remain absent. |

### Other open engineering PRs

- PR #27 (Adaptive Integration Engine) remains Draft/open, 37 commits ahead / 40 behind current main and `mergeable=false`. Earlier credential-normalization and capability-fingerprint review findings remain unresolved; refresh and rerun exact-head CI before integration.
- PR #19 remains Draft/open and divergent as described above. Its older successful CI is not evidence for current main.

### Public-data and publication boundary

- The OpenMP input and AquaSignal fixtures are synthetic; no operator telemetry, private laboratory records, credentials or personal data were committed.
- The archived OpenMP report retains generated timing samples only. The incomplete historical 10/20-case local report remains explicitly invalidated and is not used as evidence.
- No new Supabase project or external database was created.
- No study was promoted to Published. The AquaSignal field study and native OpenMP independent replication remain unvalidated.
- This report records work completed during a scheduled run; it does not claim continuous background execution.


## NOEMA run audit — 2026-11-26 (World Risk Poll + accumulator algorithms)

This section supersedes earlier status snapshots in this file where the current main SHA, PR divergence counts, or the NOEMA-005/NOEMA-007 run state differ.

- **Current main at audit start:** `1422e0f593c43f24836c2349263d43eee127ea47`.
- **NOEMA-2026-005:** Draft PR [#33](https://github.com/maisuradzee/bibmom/pull/33) adds five deterministic binary64 fixtures (15,359 values), exact `Fraction.from_float` reference, strict left-to-right, one adjacent-pair tree, Neumaier, `math.fsum` and 1,200-digit Decimal comparisons. Local tests passed 5/5 on CPython 3.13.5/x86_64. Neumaier, `math.fsum` and Decimal matched 5/5; strict naive and the tested adjacent-pair tree matched 1/5 each. This is accuracy-only; no threading/runtime/memory claim. The first CI run [45795906135](https://github.com/maisuradzee/bibmom/actions/runs/45795906135) failed draft completeness; the next [45796232959](https://github.com/maisuradzee/bibmom/actions/runs/45796232959) passed draft validation but exposed a frozen-result test that compared full ULP snapshots across CPython 3.13 and 3.14. The test has been changed to compare stable input hashes, exact references and accuracy classifications; the latest head is `9cb8438f6ea1a23cfb244231bba6c6da3164f7fc`, and exact-head CI is pending.
- **NOEMA-2026-007:** Draft PR [#34](https://github.com/maisuradzee/bibmom/pull/34) adds Lloyd's Register Foundation's 2025 World Risk Poll warning-to-action evidence, a machine-readable evidence record, Georgia sample caveat and privacy-preserving Action Readiness Ledger proposal. Local tests passed 4/4. Exact-head quality CI [45795911909](https://github.com/maisuradzee/bibmom/actions/runs/45795911909) passed all workflow steps: draft validation, research index, mission/queue/service checks, unit tests, frozen-result reproduction, site build and publication-boundary checks. The source report shows 80% of disaster-impacted respondents received a warning and 64% of warned respondents could act. Georgia had only 99 respondents asked about warnings, below the report's 100-respondent threshold; the 22.8% figure is not a robust country estimate. NOEMA has not independently rerun the 143,459-row microdata; the source repository reports 541 findings checked (487 match, 17 within tolerance, 37 Gallup-only). No microdata or personal data was copied.
- **NOEMA-2026-006 AquaSignal:** PR #29 remains merged. The in-memory incident lifecycle still has no paired sensor/laboratory data or field validation; operator data dictionary and site-approved Water Safety Plan limits remain blockers.
- **NOEMA-INFRA-001:** PR [#19](https://github.com/maisuradzee/bibmom/pull/19) compares to current main as 32 ahead / 49 behind (merge base `f777eb530443e5be33ce6d28591eeb75e2df0fd0`). Its backup/restore implementation is not present in current main. A review comment recommends selective porting to a clean current-main branch rather than blind rebase. Backup encryption, off-host retention/rotation and scheduled restore drills remain absent.
- **PR #27 adaptive integration engine:** branch compares as 37 ahead / 43 behind. Security review comments identify credential-key normalization gaps and missing capability-policy fingerprint comparison at execute time. These are potential policy bypasses, not evidence of an actual credential leak; do not merge until fixed, refreshed and rechecked.
- **Publication:** the catalogue remains 1 preliminary / 0 published. Both new studies remain drafts; no independent external review has been completed.
- **Main CI / Pages:** the current main commit's combined status endpoint returned no status entries in this audit. The last explicitly verified main quality/deploy runs remain [45792961744](https://github.com/maisuradzee/bibmom/actions/runs/45792961744) and [45792961703](https://github.com/maisuradzee/bibmom/actions/runs/45792961703) for the earlier main commit `8bb91db62105a83391986d06e88f198b5c7d1670`; therefore this audit does not claim Pages reflects commit `1422e0f`.
- **Public-data boundary:** only public-source summaries and synthetic fixtures were added. The WRP source dataset is CC BY-SA 4.0 and its microdata was not copied into NOEMA. No private operator telemetry, credentials or personal data were added; no new Supabase project or external database was created.

### Active stream status

| Stream | Current status | Next verified step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | Prototype; PR #29 merged | Obtain authorized paired sensor/lab data and approved site limits before field validation |
| NOEMA-2026-005 numerical reduction | Preliminary; PR #33 Draft, exact-head CI pending | Finish cross-runtime CI, then native C/OpenMP long-double and binned/exact comparison |
| NOEMA-2026-007 Last-Mile Action Gap | Draft; PR #34 exact-head CI success | Obtain authorized municipal aggregate delivery/acknowledgement/action data; Georgia WRP sample is too small |
| NOEMA-INFRA-001 reliability | Engineering; PR #19 divergent | Port backup/restore to a clean branch from current main and run a restore drill |


### Post-merge verification — 2026-11-26

The two independent research PRs were merged only after their exact-head quality CI passed, their branch comparisons showed no behind commits, and the public-data boundary was checked:

- **PR #33 / NOEMA-005** — exact head `9cb8438f6ea1a23cfb244231bba6c6da3164f7fc`; PR quality CI [45796534709](https://github.com/maisuradzee/bibmom/actions/runs/45796534709) SUCCESS; squash merge commit `590b6f7de140356d0eb2188fd82ce6161be96330). Main push quality [45796919557](https://github.com/maisuradzee/bibmom/actions/runs/45796919557) SUCCESS and Pages deployment [45796919732](https://github.com/maisuradzee/bibmom/actions/runs/45796919732) SUCCESS.
- **PR #34 / NOEMA-2026-007** — after merging current main into the branch, exact head `ef6bae6e5792d969753aeffe338203699e9944de`; PR quality CI [45797079222](https://github.com/maisuradzee/bibmom/actions/runs/45797079222) SUCCESS; squash merge commit `50a54227444ae52bdb5641b30e8c430ec7b8a722). Main push quality [45797225139](https://github.com/maisuradzee/bibmom/actions/runs/45797225139) SUCCESS and Pages deployment [45797225190](https://github.com/maisuradzee/bibmom/actions/runs/45797225190) SUCCESS.
- **Current main after both research merges:** `50a54227444ae52bdb5641b30e8c430ec7b8a722`. Pages deployment succeeded for this commit. The public catalogue remains 1 preliminary / 0 published; the new research drafts are in the repository but were not promoted as published website studies.
- **Publication boundary:** the public research catalogue remains 1 preliminary / 0 published. The new accumulator comparison and World Risk Poll analysis remain draft research records; merge into the repository did not promote either to Published.
- **Portfolio sync PR #35:** merged at `9e8acdcf27efcce0712e913aa53ca240dc2ae41b` after exact-head quality CI passed.



## Final current-main audit — 2026-11-26

This is the latest verified state after merging the two research changes and the portfolio/status synchronization.

- **Current main:** `9e8acdcf27efcce0712e913aa53ca240dc2ae41b`.
- **PR #33 — NOEMA-005 accumulator comparison:** merged as `590b6f7de140356d0eb2188fd82ce6161be96330`; exact-head PR quality CI [45796534709](https://github.com/maisuradzee/bibmom/actions/runs/45796534709) SUCCESS.
- **PR #34 — NOEMA-2026-007 World Risk Poll evidence:** merged as `50a54227444ae52bdb5641b30e8c430ec7b8a722`; after refreshing its branch against current main, exact-head PR quality CI [45797079222](https://github.com/maisuradzee/bibmom/actions/runs/45797079222) SUCCESS.
- **PR #35 — portfolio/status synchronization:** merged as `9e8acdcf27efcce0712e913aa53ca240dc2ae41b`; exact-head PR quality CI [45797401361](https://github.com/maisuradzee/bibmom/actions/runs/45797401361) SUCCESS.
- **Current main quality CI:** [45797514610](https://github.com/maisuradzee/bibmom/actions/runs/45797514610) SUCCESS, including unit tests, draft validation, research index/schema, frozen-result reproduction, site build and publication-boundary checks.
- **Current main GitHub Pages deployment:** [45797514326](https://github.com/maisuradzee/bibmom/actions/runs/45797514326) SUCCESS; both build and deploy jobs completed. The deployed site is https://maisuradzee.github.io/bibmom/. The public research catalogue remains 1 preliminary / 0 published; the new research records remain drafts and are not represented as published studies.
- **PR #19 / reliability:** 32 commits ahead / 52 behind current main; backup/restore code is still absent from main. Do not merge the divergent branch blindly.
- **PR #27 / adaptive integration:** 37 commits ahead / 46 behind current main; credential-key normalization and capability-policy fingerprint issues remain open. Do not merge until fixed and revalidated.
- **Active portfolio:** four streams remain active: AquaSignal, NOEMA-005, NOEMA-2026-007 and NOEMA-INFRA-001.
- **Public-data boundary:** WRP microdata was not copied; only cited public-source summaries and synthetic numerical fixtures were added. No personal data, private operator telemetry, credentials, new Supabase project or external database was added.

### Current active stream status

| Stream | Status | Next verified step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | Prototype; PR #29 merged; synthetic-only | Obtain authorized paired sensor/lab data and approved site limits before field validation |
| NOEMA-2026-005 numerical reduction | Preliminary; PR #33 merged; exact-head CI success | Native C/OpenMP long-double, alternative tree and binned/exact comparison; independent ARM64/x86-64 replication |
| NOEMA-2026-007 Last-Mile Action Gap | Draft; PR #34 merged; exact-head CI success | Obtain authorized municipal aggregate delivery/acknowledgement/action data; Georgia WRP warning base is too small |
| NOEMA-INFRA-001 reliability | Engineering; PR #19 divergent 32 ahead / 52 behind | Port backup/restore to a clean current-main branch and run an exact-head restore drill |




## NOEMA run audit — 2026-11-26 (AquaSignal event store + exact binary64 conversion)

This section supersedes earlier status snapshots above where the main SHA, AquaSignal persistence state, NOEMA-005 converter status or PR divergence counts differ.

- **Current main:** `fa0e9ce16392c90340becc4194818eb615a93697` (PR #40 merge commit).
- **PR #40 — AquaSignal local event store:** merged after exact-head verification. [Quality CI 45806582839](https://github.com/maisuradzee/bibmom/actions/runs/45806582839) passed 288 Python tests, including 11 event-store tests, frozen research reproductions, site build and publication-boundary checks. [CPU-thread workflow 45806582809](https://github.com/maisuradzee/bibmom/actions/runs/45806582809) passed GIL-enabled and free-threaded jobs. POSIX filesystem boundary now requires a current-user-owned mode-0700 parent, opens with `O_NOFOLLOW`, verifies a regular current-user-owned file and applies mode 0600 before SQLite opens it.
- **PR #38:** closed as superseded by PR #40; its branch was behind current main and was not merged.
- **PR #39 — NOEMA-005 exact binary64 conversion:** Draft/open, head `38f69c1f6943266eefc626e4674a15b28e23abb5`, mergeable=true. [Quality CI 45805534507](https://github.com/maisuradzee/bibmom/actions/runs/45805534507) and [native x86-64/ARM64 matrix 45805534509](https://github.com/maisuradzee/bibmom/actions/runs/45805534509) passed. The bounded 2,560-bit exact accumulator now has a guard/sticky-bit, ties-to-even converter; boundary self-tests cover normal/subnormal, positive/negative ties, cancellation and overflow. Independent MPFR/SoftFloat cross-check and generated rational cases remain required; no performance or publication claim is made.
- **PR #19 — backup/restore:** Draft/open, 32 commits ahead / 54 behind current main, `mergeable=false`; its backup code is not in main. Selective port to a clean branch is safer than blind rebase.
- **PR #27 — Adaptive Integration Engine:** Draft/open, 37 commits ahead / 48 behind current main, `mergeable=false`; earlier credential-normalization and capability-policy fingerprint findings remain unresolved. Do not merge without a clean refresh and exact-head review.
- **NOEMA-2026-007:** no new municipal dataset or field evidence this cycle. LRF's source-published WRP reproduction remains 487 exact matches, 17 within tolerance and 37 Gallup-only of 541; NOEMA has not independently rerun the respondent-level microdata. Georgia's warning-question base remains 99, below the report's 100-response country threshold.
- **Catalogue:** 1 preliminary / 0 published. No independent external numerical-method review or AquaSignal field validation has been completed.
- **Main post-merge quality / Pages:** no run for merge SHA `fa0e9ce` was returned by the workflow-run lookup at audit time. Therefore this document does not claim that Pages has deployed the merge commit; the successful PR exact-head CI is not a substitute for main deployment confirmation.
- **Public-data boundary:** only synthetic AquaSignal fixtures and public-source summaries are present. No operator telemetry, private laboratory records, credentials, personal data, new Supabase project or external database was added.

### Active portfolio

| Stream | Status | Next verified step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | active / prototype; event store merged; synthetic-only | encrypted/off-host backup and restore controls; then authorized paired sensor/lab data and preregistered field validation |
| NOEMA-2026-005 numerical reduction | active / preliminary; exact converter PR #39 Draft, exact-head CI success | independent MPFR/SoftFloat cross-check and generated rational cases; physical hardware and representative workloads |
| NOEMA-2026-007 Last-Mile Action Gap | active / draft | obtain authorized municipal aggregate delivery/acknowledgement/action data; Georgia WRP sample is too small |
| NOEMA-INFRA-001 reliability | active / engineering; PR #19 divergent | clean current-main port, exact-head CI and restore drill; then encrypted off-host retention |

NOEMA progresses during scheduled runs only; this audit does not claim continuous background work.


## NOEMA run audit — 2026-11-26 (run 7)

### Main and merged research changes

- Base main for the current infrastructure branch: ed3cffa6ed3045985f413b140ad83dc783cdbe17.
- PR #42 merged as 32bd0ea18c40865322bc89f5424d9f84a12ac307: bounded exact integer-unit to binary64 conversion with round-to-nearest, ties-to-even.
- PR #43 merged as ed3cffa6ed3045985f413b140ad83dc783cdbe17: frozen 275-input exact-rounding oracle protocol and CI result. The native C converter matched the Python integer and Decimal references 275/275 on both hosted x86-64 and ARM64 jobs. This is reproduced CI evidence, not MPFR/SoftFloat, formal proof or physical-hardware replication.
- PR #39 was closed as superseded by PR #42; its history was retained.
- PR #29 is merged; AquaSignal remains a synthetic/operator-decision-support prototype without paired field sensor/laboratory validation.

### Current working changes

- PR #44 is the clean current-main port of local verified SQLite backup/restore and operational observability. It includes online backup, WAL inclusion, immutable archive checks, payload/result hashes, audit-chain validation, no-overwrite restore, metrics CLI, health reporting and payload-free supervisor logs.
- The port adds an explicit rejection for final-component symlink backup/restore destinations, including broken symlinks, with a regression test.
- The current implementation is local and unencrypted. Off-host upload, age encryption, signed manifests, key rotation, retention and restore drills remain design-only. RPO/RTO, provider and key custody are not selected.
- PR #19 is the older divergent source branch and is not merged. PR #44 is the clean replacement candidate; close #19 only after #44 has passed final exact-head CI and is merged.
- PR #27 remains a separate draft with credential-normalization and capability-policy review findings. Its branch is 37 commits ahead / 62 behind current main; do not merge without a clean refresh and exact-head security review.
- PR #5 is a database/RLS proposal only (7 commits ahead / 76 behind); its SQL is explicitly marked not executed. No Supabase project or database was created.
- PR #7 is an older cross-platform simulation workflow only (3 commits ahead / 76 behind). It is not merged; current main already has x86-64/ARM64 native OpenMP validation, while Windows/macOS simulation coverage remains optional follow-up.

### Portfolio status

| Stream | Status | Next step |
|---|---|---|
| NOEMA-2026-006 AquaSignal | active / prototype; synthetic-only | obtain authorized paired sensor/lab data; preregister field validation; retain operator confirmation and no automatic actuator |
| NOEMA-2026-005 numerical reduction | active / preliminary; exact converter merged; 275-input oracle CI passed on x86-64 and ARM64 | MPFR/SoftFloat cross-check, accumulator overflow rejection, realistic memory-bound workloads and pinned physical hardware |
| NOEMA-2026-007 Last-Mile Action Gap | active / discovery draft | authorized municipal aggregate delivery/acknowledgement/action data; no new local field dataset this cycle |
| NOEMA-INFRA-001 reliability | active / engineering; clean backup/restore port in PR #44 | exact-head CI and restore drill; then provider/key/RPO/RTO decision and encrypted off-host implementation |

### Publication, deployment and privacy

- Public research catalogue remains 1 preliminary / 0 published. No new research was promoted to Published without independent review.
- The PR #44 quality workflow validates the research catalogue, frozen NOEMA-003/005 results, site build and publication boundary; this does not prove that a main-branch Pages deployment completed.
- No main Pages deployment for merge commit ed3cffa was confirmed during this audit; do not claim the live site includes PR #43 until a successful deployment job is observed.
- Only public documentation, source links, synthetic fixtures and software tests were added. No operator telemetry, private laboratory data, credentials, secret keys, new Supabase project or external database was added.
- NOEMA operates during scheduled runs only; this audit does not claim continuous background execution.


## Final state after run 7 — 2026-11-26

- **Current main:** 70099355579eef8b4767149c5611c711eb222887.
- **PR #44 — verified local backup/restore:** merged as 70099355579eef8b4767149c5611c711eb222887 after exact-head quality CI 45811367125 and CPU-thread workflow 45811367483 succeeded. The quality job ran 303 Python tests, the backup/restore CLI smoke test, frozen NOEMA-003/005 reproductions, site build and publication-boundary checks. The CPU-thread workflow passed both GIL-enabled and free-threaded jobs.
- **PR #19:** closed as superseded by PR #44; old branch history remains available and was not merged.
- **PR #42 / #43:** merged; the exact binary64 converter and 275-input integer/Decimal oracle regression suite are now in main. MPFR/SoftFloat and physical-hardware validation remain outstanding.
- **PR #29:** merged; AquaSignal event lifecycle remains a synthetic prototype with operator-controlled actions and no field validation.
- **PR #27:** still Draft/open, 37 commits ahead / 63 behind; credential normalization and capability-policy review findings remain unresolved. Do not merge without a clean refresh and security review.
- **PR #5:** still Draft/open, 7 commits ahead / 77 behind; database/RLS SQL remains explicitly unexecuted. No Supabase project was created.
- **PR #7:** still Draft/open, 3 commits ahead / 77 behind; Windows/macOS cross-platform simulation coverage is optional follow-up, not merged.
- **Active portfolio:** AquaSignal (synthetic prototype); NOEMA-005 (preliminary, 275/275 converter-oracle matches on hosted x86-64 and ARM64); NOEMA-007 (discovery draft, no new local aggregate dataset); NOEMA-INFRA-001 (local verified backup/restore merged, off-host encryption not implemented).
- **Publication:** public catalogue remains 1 preliminary / 0 published. No independent review was claimed.
- **Deployment:** the PR quality CI built the site and verified the publication boundary, but no successful main-branch Pages deployment for merge SHA 70099355579eef8b4767149c5611c711eb222887 was confirmed in this audit. Do not claim the live Pages site contains this merge yet.
- **Privacy boundary:** no operator telemetry, private lab data, credentials, signing keys, new Supabase project or external database was added. NOEMA progresses during scheduled runs only, not continuously between them.


## Final state after run 8 — 2026-11-26

- **Base main before PR #59 status sync:** `54758dbd3f60298cc1440d30fe44f6f5531f647a`.
- **PR #59 portfolio/status sync:** merged as `b4e5f1fe78843a196adece7190fd65b9a7ae90ba`; this merge carries the corrected four-stream portfolio and current project status into main.
- **PR #55:** merged; synchronized the MPFR cross-check status on main.
- **PR #57:** merged as `5ba61c8932e5dccfa3edc35fc7d8cbed60bb2170`; added `python -m noema_core.jobs_cli --db ~/.noema/noema-jobs.sqlite3 restore-drill`. The command performs a same-host online SQLite backup/restore in a temporary directory, compares job/audit counts and audit-chain hash, verifies backup bytes remain unchanged, and emits aggregate-only JSON. It does not test off-host encryption, key recovery, provider retention or clean-host disaster recovery.
- **PR #58:** merged as current main `54758dbd3f60298cc1440d30fe44f6f5531f647a`; added checked signed 2,560-bit accumulator add/merge, no-mutation-on-overflow behavior, native boundary harness and regression tests. The native workflow now asserts MPFR 4.2.1. The previous 4.2.2 label was corrected after both hosted Ubuntu runners reported 4.2.1.
- **PR #58 exact-head checks:** quality CI [45829393835](https://github.com/maisuradzee/bibmom/actions/runs/45829393835) SUCCESS, 312 Python tests (one skipped); native x86-64/ARM64 [45829393564](https://github.com/maisuradzee/bibmom/actions/runs/45829393564) SUCCESS on both architectures, 50 accumulator cases each; GIL/free-threaded CPU-thread workflow [45829393656](https://github.com/maisuradzee/bibmom/actions/runs/45829393656) SUCCESS, 48 cases and three repetitions in each runtime.
- **Latest main checks:** quality CI [45830239964](https://github.com/maisuradzee/bibmom/actions/runs/45830239964) SUCCESS, 312 tests (one skipped); native x86-64/ARM64 workflow [45829643815](https://github.com/maisuradzee/bibmom/actions/runs/45829643815) SUCCESS; Pages deployment [45830240214](https://github.com/maisuradzee/bibmom/actions/runs/45830240214) build and deploy SUCCESS.
- **Active portfolio:** AquaSignal remains a synthetic/operator-decision-support prototype without paired field sensor/laboratory validation; NOEMA-005 remains preliminary despite the new checked-overflow and MPFR tests; NOEMA-007 remains a discovery draft without local last-mile outcome data; NOEMA-INFRA-001 now has a same-host restore-drill CLI, while encrypted off-host backup and clean-host recovery remain unimplemented.
- **Publication:** public catalogue remains 1 preliminary / 0 published. No study was promoted to Published; independent numerical-method and field review are still outstanding.
- **Privacy and deployment boundary:** only public code, documentation and synthetic fixtures were added. No operator telemetry, private laboratory data, credentials, signing keys, new Supabase project or external database was added. Pages are updated only because the successful deploy job above completed.
- **Next priorities:** independent review of NOEMA-005; representative memory-bandwidth-bound workloads and physical x86-64/ARM64 replication; operator-approved non-production restore drill; then approve RPO/RTO, provider and key custody before off-host backup implementation.


## NOEMA run audit — 2026-11-26 (run 9)

- **Audit base main:** `09b7f0c28c8edebed9d72fc7d264418bd08a8a5f`, after PR #62.
- **NOEMA-2026-007 / PR #62:** merged as `09b7f0c28c8edebed9d72fc7d264418bd08a8a5f`. Exact-head quality CI [45839056275](https://github.com/maisuradzee/bibmom/actions/runs/45839056275) passed; main quality CI [45839308722](https://github.com/maisuradzee/bibmom/actions/runs/45839308722) passed; Pages build/deploy [45839308765](https://github.com/maisuradzee/bibmom/actions/runs/45839308765) both succeeded. The new source snapshot reproduces 64/136 = 47.0588% all-four-pillar reporting and the source-reported preparedness score difference 0.74 to 0.70. These are country-level metrics, not population coverage or causal effects.
- **NOEMA-005 / full-width MPFR and actual CPU threads:** the 2,068-case deterministic MPFR 4.2.1 suite passed on hosted x86-64 and ARM64. The clean-base PR #63 code head `b4df9c9c1f7d2142c8d48e487a73977be70b9966` passed quality CI [45840219937](https://github.com/maisuradzee/bibmom/actions/runs/45840219937), native MPFR x86-64/ARM64 [45840219897](https://github.com/maisuradzee/bibmom/actions/runs/45840219897), and actual CPU-thread jobs [45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895). Each runtime executed 48 cases × 3 repetitions with distinct native thread IDs. Neumaier `(sum, correction)` state merge was correct in 48/48 runs; scalar Neumaier partials in 42/48; naive partials in 0/48. For 2–8 workers, CPU/wall ratio was 1.004–1.031 in GIL-enabled CPython and 1.880–3.922 in free-threaded CPython, but the hosted runners differ in provider/platform. No speedup was observed for the synthetic threaded workload. The current PR #63 also adds a frozen aggregate summary and validator; those new exact-head checks are pending at this status snapshot. PRs #61 and #47 were closed as superseded; their branch histories are retained.
- **AquaSignal:** remains a synthetic operator-side prototype; authorized paired sensor/laboratory data, site-approved limits and field validation remain blockers.
- **NOEMA-INFRA-001:** local same-host SQLite restore-drill CLI remains in main. Encrypted off-host storage, signed manifests, independent key custody, retention and clean-host recovery are not implemented.
- **Portfolio:** all four streams remain active. NOEMA-005 remains preliminary; NOEMA-006 and NOEMA-007 remain unpromoted; no study is Published. The public catalogue remains 1 preliminary / 0 published.
- **Privacy/deployment boundary:** only public official-source metadata, country-level counts and synthetic numerical test inputs were added. No personal/operator data, credentials, signing keys, new Supabase project or external database was added. Pages is current for audit base main only because the successful deploy job above completed.
- NOEMA progresses during scheduled runs only; this entry does not claim continuous background work.


## NOEMA run audit — 2026-11-26 (run 10)

- **Latest research merge:** PR #66 — `45f9511ca1552a9ef680b7d52a3d560bc858a485`.
- **PR #63 — NOEMA-005 full-width MPFR and CPU-thread evidence:** merged as `c89725743a98252da0bfba1ce0bb51472f758e44`. Exact-head quality CI [45841469603](https://github.com/maisuradzee/bibmom/actions/runs/45841469603), GIL-enabled/free-threaded CPU-thread workflow [45841469605](https://github.com/maisuradzee/bibmom/actions/runs/45841469605) and MPFR 4.2.1 x86-64/ARM64 workflow [45841469616](https://github.com/maisuradzee/bibmom/actions/runs/45841469616) all succeeded. The 2,068-case oracle matched on both hosted architectures. The synthetic native-thread run preserved Neumaier state in 48/48 runs; scalarized Neumaier matched 42/48 and naive partial sums 0/48. No threaded wall-time speedup was observed.
- **NOEMA-005 artifact provenance audit:** original ZIPs from [45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895) were downloaded; their 7,620-byte and 7,830-byte archive SHA-256 values independently matched the frozen summary. Reaggregation of both raw 48-case reports reproduced method accuracy counts and metric ranges. This is integrity/reaggregation verification, not a second benchmark execution; the ZIPs retain their 30-day Actions retention.
- **PR #66 — artifact provenance audit:** merged as `45f9511ca1552a9ef680b7d52a3d560bc858a485`; its structured audit JSON and regression test now preserve the verified archive hashes and aggregate comparison in main.
- **PR #64 — NOEMA-INFRA-001 manifest contract:** merged as `6dbb18e2a7cf0427f7d874d0ab903c9293771685`. Exact-head quality CI [45842688777](https://github.com/maisuradzee/bibmom/actions/runs/45842688777) passed 329 Python tests, including 7 focused manifest-schema contract tests, site build and publication-boundary checks.
- **Post-merge main verification:** quality CI [45844512093](https://github.com/maisuradzee/bibmom/actions/runs/45844512093) passed 334 tests. Pages build/deploy [45844512448](https://github.com/maisuradzee/bibmom/actions/runs/45844512448) completed successfully. PR #66 exact-head quality CI [45844362485](https://github.com/maisuradzee/bibmom/actions/runs/45844362485) and GIL-enabled/free-threaded workflow [45844363177](https://github.com/maisuradzee/bibmom/actions/runs/45844363177) both succeeded.
- **NOEMA-2026-006 AquaSignal:** prototype and local event store remain synthetic/operator-side only. Authorized paired sensor/lab data, site-approved Water Safety Plan limits and field validation remain blockers.
- **NOEMA-2026-005:** remains preliminary. Hosted CI is not physical-hardware replication or formal proof; the thread benchmark uses two synthetic cancellation layouts, and representative scientific workloads, memory-bandwidth measurements and independent numerical-method review remain outstanding.
- **NOEMA-2026-007 Last-Mile Action Gap:** the frozen UNDRR source snapshot reproduces 64/136 = 47.0588% all-four-pillar country reporting and the source-reported preparedness score change 0.74 to 0.70. These are country-level capability measures, not population coverage, alert receipt, comprehension or causal impact. Georgian municipal delivery/acknowledgement/action records and field validation remain unavailable.
- **NOEMA-INFRA-001:** the new schema is a strict, non-secret metadata contract only. No real backup manifest, off-host storage, encryption, detached-signature verification, provider, key custody, retention policy or clean-host recovery has been implemented. RPO/RTO and operator-approved restore drill remain outstanding.
- **Portfolio and publication:** all four research streams remain active. The public catalogue remains 1 preliminary / 0 published; no research was promoted to Published and no independent review is claimed.
- **Privacy and deployment boundary:** only public code, design metadata and synthetic fixtures were added. No operator telemetry, private laboratory data, credentials, signing keys, new Supabase project or external database was added. Pages is considered updated only because the main deploy job above succeeded.
- NOEMA progresses during scheduled runs only; this audit does not claim continuous background execution.


## NOEMA run 11 — verified repository update (2026-11-26)

- **Main:** `990ba166c7422257291ba2abfc9278ea7099c654`.
- **PR #68 — NOEMA-007:** merged as `f12a116c86514994ec40c4a953ba6a4f0a4656fc`; exact-head quality CI [45849048113](https://github.com/maisuradzee/bibmom/actions/runs/45849048113) SUCCESS.
- **PR #69 — NOEMA-INFRA-001:** merged as `990ba166c7422257291ba2abfc9278ea7099c654`; exact-head quality CI [45849597538](https://github.com/maisuradzee/bibmom/actions/runs/45849597538) SUCCESS, including 341 Python tests.
- **Post-merge main quality:** [45850024686](https://github.com/maisuradzee/bibmom/actions/runs/45850024686) SUCCESS, 341 tests.
- **Pages:** [45850024682](https://github.com/maisuradzee/bibmom/actions/runs/45850024682) build SUCCESS and deploy SUCCESS.

### Stream status after merge

| Stream | Current state | Remaining blocker |
|---|---|---|
| NOEMA-2026-006 AquaSignal | active prototype; deterministic rules engine and local SQLite event store | explicitly authorized paired sensor/lab data, site Water Safety Plan limits, field validation and independent review |
| NOEMA-2026-005 numerical reduction | active preliminary; MPFR oracle, hosted CPU-thread results and artifact provenance audit | independent numerical review, representative memory-bandwidth workloads and independently selected physical hardware; no general wall-time speedup |
| NOEMA-2026-007 warning-to-action gap | active draft; WMO roadmap aggregates reproduced and privacy-safe aggregate-only contract implemented/tested with synthetic fixtures | official Georgia data dictionary, permission for event-level aggregates, local privacy approval and field evaluation |
| NOEMA-INFRA-001 backup/provenance | active engineering; local restore-drill, strict manifest schema and runtime validator | no encryption, signature verification, off-host provider, key custody, retention policy or clean-host recovery |

The WMO arithmetic is derived only from its rounded published aggregates: 20/35 = 57.1429% of analysed roadmaps had clear budget allocations; USD 1.38bn/20 = approximately USD 69m per budgeted roadmap. This is not an estimate of cost for Georgia or a measure of people warned/protected.

The action-readiness contract separates endpoint delivery receipts from survey-based receipt, comprehension, feasible action, self-reported action and verified action. Tests use synthetic data only; the minimum cell-size floor of 10 is a prototype default, not an anonymisation guarantee. No field event or individual-level data is present.

The backup manifest runtime validator verifies only Draft 2020-12 structure and declared formats. It does not verify signatures, ciphertext, provider retention or restored database contents.


## NOEMA run audit — 2026-11-26 (after PR #72)

- **Current main:** `7d9a7e8aef633b3d3ac371e62522fcd0be0b151d`; PR #72 merged after exact-head quality CI run 45853277201 passed. Its tests cover the existing full AquaSignal lifecycle plus external checkpoint matching, mismatch and input validation.
- **AquaSignal trust boundary:** `AquaSignalStore.verify_checkpoint()` compares the verified local event count and final SHA-256 chain hash with values supplied by a caller. It does not sign or authenticate the checkpoint, prevent rollback, or configure remote storage.
- **NOEMA-007:** PR #73 adds the 2025 UNDRR/WMO anticipatory-action source snapshot and reproducible framework-growth arithmetic. Exact-head quality CI 45853282017 passed, including the new frozen-result reproduction, Python suite, site build and publication-boundary check. CPU-thread workflow 45853281867 passed both GIL-enabled and free-threaded jobs. The PR is 8 commits ahead / 1 behind main after PR #72; GitHub reports mergeable=false, so it was not merged.
- **NOEMA-005:** PR #71 remains Draft/open. Exact-head quality run 45850716864 and real-thread run 45850716742 passed. The new rerun reports 48/48 Neumaier-state accuracy in both modes, but median wall-time speedup is 0.7539× (GIL) and 0.9519× (free-threaded), both below 1. The benchmark remains one hosted x86-64 VM with synthetic fixtures; it is not independent physical-hardware replication.
- **NOEMA-INFRA-001:** PR #69 runtime manifest metadata validator is merged; no real encrypted off-host backup, detached signature verification, key custody, provider retention or clean-host recovery is claimed.
- **Public-safety boundary:** no operator telemetry, laboratory records, personal data, real backup manifest, credentials, signing keys, new Supabase project or external database was added.
- **Deployment:** current-main Pages deployment after PR #72 was not verified in this audit; the last confirmed deployment remains run 45850024682 for commit `990ba166c7422257291ba2abfc9278ea7099c654`.

### Next priorities

1. Refresh PR #73 onto current main and rerun exact-head quality/CPU-thread workflows before considering merge.
2. Refresh PR #71 only after reviewing the new artifact summary; retain Draft and preliminary status until independent numerical review and representative physical x86-64/ARM64 workloads exist.
3. For AquaSignal, define a signed, monotonic external checkpoint protocol and separately administered trust anchor; obtain authorized paired sensor/lab data before any field-performance claim.
4. For NOEMA-INFRA-001, require operator-approved RPO/RTO, provider, key custody and retention before implementing off-host backup.
