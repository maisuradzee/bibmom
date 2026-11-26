# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-26
- **საცავი:** https://github.com/maisuradzee/bibmom
- **ძირითადი branch:** main
- **ბოლო დადასტურებული ინოვაციური merge:** PR #25 — commit 5a8eaeb0d833af65f54b1b1213979c597e75b117.
- **NOEMA-005:** ARM64 replication და MPFR 4.2.2 cross-check main-შია; exact-head 467/467 synthetic inputs თითო hosted x86-64/ARM64 გარემოზე დაემთხვა MPFR/Python references; add/merge overflow guard და დამოუკიდებელი physical-hardware replication დარჩენილია.
- **NOEMA-006 AquaSignal:** PR #25 merged; DISCOVERY / RESEARCH / INNOVATION operating model და operator-side anomaly prototype main-შია.
- **PR #25 quality CI:** run 45768832968 — SUCCESS, exact head 7f0a3f165e54983624f9f874212e17f4cd8edebd; 220 Python tests.
- **PR #25 CPU-thread workflow:** run 45768832918 — ორივე GIL-enabled და free-threaded job SUCCESS.
- **Main quality CI:** run 45769022786 — SUCCESS, 220 Python tests.
- **Main Pages deployment:** run 45769022785 — build და deploy SUCCESS.

## მიმდინარე მდგომარეობა

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | რეალიზებულია როგორც შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs.py, worker.py, workflows.py, scheduler.py, supervisor.py, service.py |
| DISCOVERY · RESEARCH · INNOVATION მოდელი | PR #25-ით main-შია | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-002 SignBase audit | შესრულებული კვლევითი ჩანაწერი | data/audits და research archive |
| NOEMA-003 climate analysis | დრაფტი / გამეორებადი; ERA5 validation gate ვერ გაიარა და საბოლოო დასკვნაში არ გამოიყენება | data/noema-003, scripts და tests |
| NOEMA-005 summation | preliminary; x86-64/ARM64 რეალური CPU-thread ტესტები და MPFR 4.2.2 rounding cross-check main-შია | Neumaier-state 768/768 ARM64 batch-ებში; MPFR oracle 467/467 თითო hosted არქიტექტურაზე; checked add/merge overflow და representative workloads დარჩენილია; wall-time speedup არ დადასტურებულა |
| NOEMA-006 AquaSignal | draft + software prototype; საველე ვალიდაცია არ ჩატარებულა | research/drafts/NOEMA-2026-006-aquasignal-water-early-warning.md, docs/AQUASIGNAL_MVP.md, noema_core/aquasignal.py |
| NOEMA-007 Last-Mile Action Gap | draft / discovery; UNDRR 2026: 136 ქვეყნიდან 64-ს ოთხივე pillar აქვს; 2022-ის შემდეგ capability scores თითქმის უცვლელია და preparedness 0.74-დან 0.70-მდე დაეცა; საქართველოში NEA-ის 7 აუზის გეგმებზე კონსულტაცია მიმდინარეობს; ადგილობრივი last-mile ეფექტიანობა ჯერ არ გაზომილა | research/drafts/NOEMA-2026-007-global-early-warning-action-gap.md |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; schema version 2. NOEMA-006 draft კატალოგში არ არის |
| GitHub Pages | ბოლო deployment წარმატებულია | run 45769302330 — build და deploy jobs SUCCESS; https://maisuradzee.github.io/bibmom/ |
| Main quality CI | წარმატებულია | run 45769302290 — validate job SUCCESS |
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

## ღია Draft PR-ები

- PR #19 — operational observability და SQLite backup/restore; WAL-mode regression fixture-ის გასწორება და CLI round-trip CI წარმატებულია exact head `0c4f456f17851918bf7f30af7ff4d3c369f6eec7`-ზე ([run 45774768045](https://github.com/maisuradzee/bibmom/actions/runs/45774768045)). თუმცა branch current main-თან diverged-ია: 32 commits ahead / 6 behind; საჭიროა refresh/rebase და ახალი exact-head CI.
- PR #7 — 330-case deterministic simulation-ის cross-platform reproduction; ეს რეალურ multi-thread runtime-ს არ ამოწმებს.
- PR #5 — მონაცემთა ბაზისა და RLS-ის არქიტექტურული წინადადება; რეალური PostgreSQL/Supabase ინტეგრაცია არ ჩატარებულა.

ეს PR-ები ამ ციკლში უცვლელი დარჩა. არცერთი ახალი Supabase პროექტი არ შექმნილა.

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
