# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-26
- **საცავი:** https://github.com/maisuradzee/bibmom
- **ძირითადი branch:** main
- **ბოლო დადასტურებული ინოვაციური merge:** PR #25 — commit 5a8eaeb0d833af65f54b1b1213979c597e75b117.
- **NOEMA-005:** ARM64 replication და final-head verification main-შია; კვლევა რჩება preliminary.
- **NOEMA-006 AquaSignal:** PR #25 merged; DISCOVERY / RESEARCH / INNOVATION operating model და operator-side anomaly prototype main-შია.
- **PR #25 quality CI:** run 45768832968 — SUCCESS, exact head 7f0a3f165e54983624f9f874212e17f4cd8edebd; 220 Python tests.
- **PR #25 CPU-thread workflow:** run 45768832918 — ორივე GIL-enabled და free-threaded job SUCCESS.
- **Main quality CI:** run 45769022786 — SUCCESS, 220 Python tests.
- **Main Pages deployment:** run 45769022785 — build და deploy SUCCESS.

## მიმდინარე მდგომარეობა

## Adaptive Integration Engine — Draft PR #27

- **Branch:** `feature/noema-adaptive-integration-engine-v0.1`.
- **Scope:** generic adapter registry, capability validation, dry-run planning, operation-scoped grants and first concrete read-only GitHub public repository adapter.
- **Service wiring:** trusted service grant is limited to `github.repo.metadata`; a metadata-only workflow is scheduled every 6 hours, with first execution delayed by one interval. Repository file reads and all writes remain disabled in the default service.
- **Tests:** 245 tests passed on the framework + adapter snapshot before runtime wiring. Runtime job wiring and its tests are now added; final CI verification is pending for the current head.
- **Review:** PR #27 remains Draft/open and is not merged into main.

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| NOEMA mission/autonomy core | რეალიზებულია როგორც შეზღუდული, ტესტირებადი foundation | noema_core/mission.json, mission.py, jobs.py, worker.py, workflows.py, scheduler.py, supervisor.py, service.py |
| DISCOVERY · RESEARCH · INNOVATION მოდელი | PR #25-ით main-შია | docs/NOEMA_OPERATING_MODEL.md |
| NOEMA-002 SignBase audit | შესრულებული კვლევითი ჩანაწერი | data/audits და research archive |
| NOEMA-003 climate analysis | დრაფტი / გამეორებადი; ERA5 validation gate ვერ გაიარა და საბოლოო დასკვნაში არ გამოიყენება | data/noema-003, scripts და tests |
| NOEMA-005 summation | preliminary; x86-64 და ARM64 რეალური CPU-thread ტესტები | 4 ARM64 batch; Neumaier state 768/768, scalar Neumaier 672/768, naive scalar 0/768; wall-time speedup არ დადასტურებულა |
| NOEMA-006 AquaSignal | draft + software prototype; საველე ვალიდაცია არ ჩატარებულა | research/drafts/NOEMA-2026-006-aquasignal-water-early-warning.md, docs/AQUASIGNAL_MVP.md, noema_core/aquasignal.py |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published | data/research.json; schema version 2. NOEMA-006 draft კატალოგში არ არის |
| GitHub Pages | ბოლო deployment წარმატებულია | run 45757333935 — build და deploy jobs SUCCESS; https://maisuradzee.github.io/bibmom/ |
| Main quality CI | წარმატებულია | run 45757333992 — validate job SUCCESS |
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

- PR #19 — operational observability და SQLite backup/restore; issue body-ში აღწერილი ბოლო CI failure საჭიროებს ცალკე reproduction/fix-ს.
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
4. პარალელურად ცალკე ციკლში გამოსწორდეს PR #19-ის backup/restore ტესტის failure.
5. NOEMA-005 დარჩეს preliminary, სანამ დამოუკიდებელი გარე რეცენზია არ დასრულდება.

**მნიშვნელოვანი:** NOEMA მუშაობს დაგეგმილი გაშვებებისას; ეს დოკუმენტი არ ამტკიცებს უწყვეტ 24/7 სამუშაოს.
