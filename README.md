# NOEMA — დამოუკიდებელი კვლევითი პლატფორმა

[![NOEMA quality checks](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml)

NOEMA აერთიანებს ცოდნის მოძიებას, წყაროების გადამოწმებას, ჰიპოთეზების ჩამოყალიბებას, კვლევების არქივირებასა და შედეგების გამოქვეყნებას.

## პრინციპები

- მტკიცებულებები, ინტერპრეტაციები და ჰიპოთეზები მკაფიოდ გამოიყოფა.
- არსებით მტკიცებებს ახლავს გადამოწმებადი წყაროები.
- კვლევის მეთოდი, შეზღუდვები და გაურკვევლობები დოკუმენტირდება.
- გამოქვეყნებამდე მასალა გადის სარედაქციო და ტექნიკურ შემოწმებას.
- ავტომატიზაცია არ ნიშნავს დაუდასტურებელი შედეგების ავტომატურ გამოქვეყნებას.

## NOEMA Run 57 — 2026-11-28

- ოთხივე აქტიური ნაკადი გადაიხედა; ახალი ნაკადი არ დამატებულა. კატალოგი: **11 Preliminary / 0 Published**.
- [PR #302](https://github.com/maisuradzee/bibmom/pull/302) ამკაცრებს NOEMA-005 Experiment 002-ის frozen verifier-ს: ზუსტად ექვსი runner/architecture/GIL-runtime cell, უნიკალური cell ID-ები, თითო cell-ზე 64 configuration და 192 measured run, თითო method-ზე 48 run, bounded counts და finite/ordered/consistent speedup summary. Mutation tests ამოწმებს per-cell corruption-ს მაშინაც, როცა global totals უცვლელია. ეს არის არსებული hosted snapshot-ის უფრო ძლიერი აუდიტი და არა ახალი CPU benchmark.
- PR #302 exact-head Quality CI [46139381431](https://github.com/maisuradzee/bibmom/actions/runs/46139381431): **878 passed, 1 skipped**. PR გაერთიანდა Main SHA a3e17a3169eb59cdbc85656d8be4dfec8d5f900c.
- INFRA-001 current-Main [Draft PR #304](https://github.com/maisuradzee/bibmom/pull/304) ამატებს 50-ვე named CI step-ის exact-body contract-ს და no-op/unlisted/unnamed-step regression tests-ს; ასევე tracked UTF-8 text credential preflight-ს. Exact-head CI [46139730927](https://github.com/maisuradzee/bibmom/actions/runs/46139730927): **889 passed, 1 skipped**; 474 tracked UTF-8 file შემოწმდა, 3 binary/non-UTF-8 file გამოტოვდა, findings არ ყოფილა.
- PR #304 რჩება Draft: manifest და validator ერთსა და იმავე public repository-შია, scanner pattern-based-ია და დამოუკიდებელ trust anchor-ს არ წარმოადგენს. საჭიროა დამოუკიდებელი security review; external high-water, encrypted offsite backup და clean-host restore არ განხორციელებულა.
- AquaSignal-ის 2026-12-01 გეგმის წარდგენის ვადა 2026-11-28 მდგომარეობით ჯერ არ იყო გასული; ახალი ოფიციალური გეგმა/receipt/approval ან NEA RAR payload არ მიგვიღია. NOEMA-007-ს ახალი ავტორიზებული Georgian warning-event მონაცემები არ დამატებია.
- PR #303 დაიხურა როგორც superseded და არ გაერთიანებულა. PR #291 კვლავ unmerged-ია და current-Main review სჭირდება.
- Post-merge Main Quality CI და Pages deployment PR #302-ის merge commit-ზე დამოუკიდებლად ვერ გადამოწმდა; PR-level site build და publication-boundary checks წარმატებულია, მაგრამ Pages განახლებულად არ გამოცხადებულა.

[Run 57-ის სრული აუდიტი](docs/run-audits/2026-11-28-run-57.md).

## NOEMA Run 56 — 2026-11-28

- ოთხივე აქტიური კვლევითი ნაკადი გადაიხედა; ახალი ნაკადი არ დამატებულა. კატალოგი: **11 Preliminary / 0 Published**.
- [PR #297](https://github.com/maisuradzee/bibmom/pull/297) ამატებს AquaSignal-ის Decree №447/2026 წლიური წყლის მონიტორინგის გეგმის evidence-intake პროტოტიპს. გეგმის ბაიტები და დანართები №1/№2 ჯერ არ მიგვიღია; შედეგი არის `NOT_ASSESSABLE_SOURCE_UNINSPECTED`, არა სამართლებრივი დარღვევა ან შესაბამისობის დასკვნა.
- [PR #298](https://github.com/maisuradzee/bibmom/pull/298) NOEMA-007-ის გაყინული 80.0% warning-receipt და 63.8% conditional action აგრეგატებიდან იღებს დაახლოებით 51.0/29.0/20.0 კომპოზიციას 100 დაზარალებულ ზრდასრულზე. ეს არ არის ახალი მიკრომონაცემთა ანალიზი, მიზეზობრივი შედეგი ან საქართველოს შეფასება; შედეგი ეთანხმება UNDRR-ის 2026-10-13 შეჯამებას.
- AquaSignal-ის PR #297 CI: **868 passed, 1 skipped**. NOEMA-007 PR #298 CI: **874 passed, 1 skipped**. ორივე ზუსტი head SHA შემოწმდა; ორივე PR გაერთიანდა.
- INFRA-001 Draft PR #291 არ გაერთიანებულა. სტატიკური აუდიტი აჩვენებს, რომ workflow contract ამოწმებს step ID-ებსა და aggregate gate-ს, მაგრამ თითოეული step-ის რეალურ command body-ს არ აფიქსირებს; ასევე URL preflight არ არის სრული secret scanner. საჭიროა command fingerprint/expected-command contract და დამოუკიდებელი security review.
- NOEMA-005-ზე ახალი ფიზიკური CPU ექსპერიმენტი არ ჩატარებულა. Run 55-ის hosted artifact reproduction უცვლელია; ფიზიკური x86-64/ARM64, RSS/native memory და DRAM counter-ები კვლავ ბლოკერია.
- Main research SHA: `88ff7ec9bf66eb6cf52087f8f2561f0ace866743`. GitHub Pages deploy: [46137522563](https://github.com/maisuradzee/bibmom/actions/runs/46137522563) — წარმატებული. Post-merge Main Quality CI [46137682863](https://github.com/maisuradzee/bibmom/actions/runs/46137682863) წარმატებით დასრულდა: **874 passed, 1 skipped**. GitHub Pages deployment [46137682856](https://github.com/maisuradzee/bibmom/actions/runs/46137682856) წარმატებით დასრულდა.

[Run 56-ის სრული აუდიტი](docs/run-audits/2026-11-28-run-56.md).

## NOEMA Run 55 — 2026-11-28

- ოთხივე კვლევითი ნაკადი გადაიხედა; ახალი ნაკადი არ დამატებულა. კატალოგი: **9 Preliminary / 0 Published**.
- [PR #285](https://github.com/maisuradzee/bibmom/pull/285) განაახლებს NOEMA-007-ს: `CountryIncomeLevel` მკაფიოდ არის ქვეყნის დონის კლასიფიკაციად მონიშნული და არა რესპონდენტის პირად შემოსავლად; დაემატა ოთხი აღწერითი percentage-point contrast. მიზეზობრივი ან დიზაინზე მორგებული ეფექტი არ არის ნავარაუდევი.
- [PR #288](https://github.com/maisuradzee/bibmom/pull/288) ამატებს NOEMA-005 Experiment 002-ის ექვსი hosted artifact-ის დამოუკიდებელ გამეორებას: 6/6 ZIP და 6/6 JSON SHA-256 დაემთხვა; 384 კონფიგურაცია და 1,152 გაზომილი გაშვება ხელახლა დაითვალა. სრული Neumaier state — 288/288 სწორი დამრგვალება; scalar Neumaier და worker-local `math.fsum` — 252/288; naive — 0/288. threaded კონფიგურაციებს serial baseline-ზე wall-time უპირატესობა არ ჰქონდათ.
- [PR #290](https://github.com/maisuradzee/bibmom/pull/290) აფიქსირებს AquaSignal-ის წყაროებზე წვდომის საზღვრებს: NEA-ს ოფიციალური RAR ბმული იხსნება, მაგრამ ამ გარემოში `application/octet-stream` payload ვერ ჩამოიტვირთა; SHA და დანართის შინაარსი უცნობია. Folketing Q199-ის საბოლოო პასუხის თარიღი 2026-11-16 დადასტურებულია, მაგრამ PDF-ის ტექსტი არ განხილულა.
- [PR #292](https://github.com/maisuradzee/bibmom/pull/292) განაახლებს NOEMA-007-ის საჯარო კატალოგს ვერსიამდე 1.2 და ინახავს ჯგუფების ერთეულის/მტკიცებულების შეზღუდვებს.
- INFRA-001-ის CI recovery წინადადება ჯერ Draft-ია: v3 branch-ის ზუსტ SHA-ზე CI წარმატებულია (875 tests, 1 skipped; 50/50 required steps), 51 draft შემოწმდა, ოთხი მხოლოდ metadata/heading repair გაკეთდა runner-ის დროებით გარემოში; 0 დარჩენილი validation error და 0 source URL issue. კვლევის შინაარსი, ტესტები და frozen results არ შეცვლილა. დამოუკიდებელი security review და მიმდინარე Main-ზე rebase კვლავ აუცილებელია; ცვლილება Main-ში არ გაერთიანებულა.
- კვლევითი Main baseline PR-ების შემდეგ: `cfa02bc52ea467b8f00bcd72266bdcefe07b2eda`. Main Quality CI: **858 passed, 1 skipped**. GitHub Pages build და deploy წარმატებულია.
- შემდეგი AquaSignal ვადა: **2026-12-01** — 2027 წლის სახელმწიფო წყლის მონიტორინგის გეგმის მინისტრისთვის წარდგენის შემოწმება. 2026-11-28 მდგომარეობით ვადა ჯერ არ იყო გასული; წარუდგენლობა ან სამართლებრივი დარღვევა არ დადგენილა.

[Run 55-ის სრული აუდიტი](docs/run-audits/2026-11-28-run-55.md)

## სტრუქტურა

- `index.html` — მთავარი გვერდი.
- `docs/NOEMA_OPERATING_MODEL.md` — DISCOVERY · RESEARCH · INNOVATION-ის ერთიანი სამუშაო მოდელი.
- `docs/AQUASIGNAL_MVP.md` — წყლის ხარისხის ოპერატორული ადრეული სიგნალის პროტოტიპის არქიტექტურა.
- `docs/AQUASIGNAL_EVENT_STORE.md` — ინციდენტების კერძო, append-only SQLite event store-ის უსაფრთხოების საზღვრები და აღდგენის შეზღუდვები.
- `docs/OFFSITE_BACKUP_ARCHITECTURE.md` — off-host backup/recovery არქიტექტურა; local detached Ed25519 manifest verification უკვე პროტოტიპად არსებობს, მაგრამ encryption/decryption, provider retention, anti-rollback high-water და clean-host restore ჯერ არ არის დანერგილი; `data/noema-backup-manifest.schema.json` განსაზღვრავს მკაცრ, საიდუმლო მასალის არმქონე metadata contract-ს.
- `docs/architecture/infra001-independent-trust-domain-and-clean-host-recovery.md` — Run 59-ის უსაფრთხო, vendor-neutral data/control/recovery plane დიზაინი; მხოლოდ არქიტექტურული წინადადებაა და დამოუკიდებელ უსაფრთხოების რეცენზიამდე წარმოებაში არ ინერგება.
- `noema_core/nitrate_nitrite.py` — Decimal-based nitrite basis conversion and a WHO-only combined nitrate/nitrite ratio requiring one same-sample drinking-water record; it does not decide Georgian legal compliance.
- `noema_core/nitrate_benchmarks.py` — source-provenance-aware nitrate reference comparison; rejects matrix/basis mismatches and never decides legal compliance or potability.
- `noema_core/aquasignal_groundwater.py` — metadata-only Decree №447 Article 7(1)-(2) readiness gate: uses hydrogeological-unit scope before groundwater-body designation and never assigns good/poor status; caller attestations are not cryptographic verification.
- `noema_core/annual_plan_deadline.py` — date-explicit classifier for the Decree №447 annual plan submission-to-Minister deadline; it separates submission evidence from public release and never infers non-submission or legal breach from missing public evidence.
- `noema_core/backup_manifest.open_verified_artifact()` — caller must provide a trusted `max_staged_byte_length`; the returned handle contains the exact hash-verified bytes, and callers must consume it rather than reopen the source path. The size cap is a resource bound, not encryption or a production restore pipeline.
- `noema_core/aquasignal.py` — AquaSignal-ის დეტერმინისტული, მხოლოდ გადაწყვეტილების მხარდამჭერი წესების ძრავა.
- `noema_core/aquasignal_store.py` — ინციდენტების replay-ზე დაფუძნებული SQLite persistence, SHA-256 audit chain და unsigned caller-supplied checkpoint-ის hash/count comparison.
- `noema_core/aquasignal_checkpoint.py` — exact canonical payload-ზე detached Ed25519 checkpoint verification, event-chain head matching და caller-managed external monotonic high-water guard; private keys და high-water storage ამ public prototype-ში არ ინახება.
- `noema_core/action_readiness.py` — NOEMA-007-ის event/area aggregate-only warning-to-action metrics validator; endpoint receipts და survey denominators განცალკევებულია.
- `noema_core/backup_manifest.py` — strict Draft 2020-12 manifest validator, streamed plaintext/ciphertext SHA-256/byte-length verifier და caller-supplied trusted Ed25519 public key-ით exact-byte detached-signature verification; decryption, provider retention, anti-rollback და restore ცალკე ეტაპებია.
- `open_verified_artifact()` returns the exact hash-verified bytes in a staged handle; restore callers must consume that handle rather than reopen the source path.
- `noema_core/restore_attestation.py` — same-host/offsite restore-drill attestation completeness gate; it never authenticates caller-supplied evidence by itself.
- `noema_core/mission.json` და `noema_core/mission.py` — მანქანურად წაკითხვადი მისია, ინფორმაციის წვდომის პოლიტიკა და ავტონომიური მოქმედებების წესები.
- `noema_core/jobs.py`, `noema_core/jobs_cli.py`, `noema_core/worker.py`, `noema_core/supervisor.py`, `noema_core/workflows.py`, `noema_core/scheduler.py` და `noema_core/service.py` — მდგრადი queue/worker, metrics და verified SQLite backup/restore CLI.
- `assets/styles.css` და `assets/articles.css` — მთავარი გვერდისა და კვლევითი სტატიების ვიზუალური სტილები.
- `data/research.json` — საჯარო, ვერსიაკონტროლირებადი კვლევების კატალოგი; `data/research.schema.json` განსაზღვრავს ჩანაწერების სტრუქტურას. ეს არის ამჟამინდელი სტატიკური კატალოგი და არა Supabase/სერვერული მონაცემთა ბაზა.
- `data/research-portfolio.json` და `data/research-portfolio.schema.json` — 3–5 აქტიური კვლევითი ნაკადის საერთო პორტფელი, თითოეული ნაკადის კითხვით, მეთოდით, წყაროებით, რისკებით, სტატუსითა და შემდეგი ნაბიჯით.
- `data/noema-003/` — NOAA-ს ფიქსირებული მონაცემთა ამონარიდი, NASA/HadCRUT5/NOAA snapshot-ები, provenance metadata და გამეორებადი შედეგები.
- `data/noema-005/` — binary64 ჯამის რიგითობის ექსპერიმენტის გაყინული შედეგები, ზუსტი reference შედარება და runtime/CPU-thread benchmark არტეფაქტები; 2026-11-27-ის ხუთი hosted GIL/free-threaded run pair (ათი artifact, 1,440 threaded run) sanitized `.json.gz.b64` ფორმით ინახება, thread IDs-ისა და დეტალური host build-ის გარეშე.
- `data/noema-007/` — Georgia basin-plan chronology and COP31 agency-reported early-warning capability signal; UNDRR/WMO 2026 early-warning და anticipatory-action aggregate snapshots, privacy-safe action-readiness schema და WRP 2025-ის დამოუკიდებლად გამეორებული warning/action aggregate; Parquet მხოლოდ ephemeral CI runner-ზე იტვირთება, საცავში რჩება მხოლოდ aggregate JSON.
- `data/noema-006/` — AquaSignal-ის WRP 2025 WP22443 water-harm aggregate, pinned source hashes და strict schema; self-reported harm ცალკეა შენარჩუნებული ლაბორატორიული წყლის ხარისხისგან.
- `scripts/reproduce_aquasignal_wrp2025_water_harm.py` და `.github/workflows/aquasignal-wrp2025-water-harm.yml` — WP22443-ის PROJWT-შეწონილი კატეგორიები და გამომცემლის code-1 + code-3 rounding rule-ის გამეორება.
- `scripts/reproduce_noema007_wrp2025.py` და `.github/workflows/noema007-wrp2025-reproduction.yml` — pinned WRP 2025 Parquet-ის Git blob/SHA-256 შემოწმება და PROJWT-შეწონილი warning/action აგრეგატების დამოუკიდებელი გამეორება.
- `research/drafts/` — სამუშაო ჩანაწერები; Pages არტეფაქტში არ შედის, თუმცა საჯარო GitHub საცავში იკითხება.
- `research/preprints/` — წინასწარი, მომხმარებლისთვის მკაფიო გაფრთხილებით გამოჩენილი კვლევები.
- `research/published/` — სრული გამოქვეყნების საკონტროლო სიის გამვლელი კვლევები.
- `research/TEMPLATE.md` — კვლევის დოკუმენტის შაბლონი.
- `.github/workflows/ci.yml` — საბაზისო შემოწმებები.
- `scripts/build_site.py` — Markdown კვლევების უსაფრთხო HTML-გვერდებად გარდაქმნა და საჯარო არტეფაქტის აწყობა.
- `scripts/validate_drafts.py` — დრაფტების მინიმალური სარედაქციო სისრულის ავტომატური შემოწმება.
- `scripts/verify_noema005_arm64_artifacts.py` — offline verifier for frozen ARM64 benchmark ZIP/raw-report SHA-256, raw-sample accuracy, CPU/wall ratios and recomputed median speedups; raw reports/thread IDs are not committed.
- `requirements-site.txt` — ფიქსირებული Markdown renderer ვერსია.
- `.github/workflows/deploy.yml` — საჯარო ფაილების შერჩევა და Pages deployment.

## მიმდინარე კვლევა

- [NOEMA-2026-006 AquaSignal](research/drafts/NOEMA-2026-006-aquasignal-water-early-warning.md) — სასმელი წყლის მონიტორინგის მონაცემების ადრეული სიგნალები; დოკუმენტური discovery, სინთეზური წესების ძრავა და ადგილობრივი event-store პროტოტიპი, საველე ვალიდაციის გარეშე.
- [AquaSignal — საქართველოს მიწისქვეშა წყლის მონაცემებზე წვდომა და ჭაბურღილების რეგისტრაციის სამართლებრივი ფარგლები](research/drafts/NOEMA-2026-006-georgia-water-data-access-update-2026-11-27.md) — ოფიციალური 2021–2025 ანგარიშის არქივის წვდომა და 2026 წლის №424 რეგულაციით შექმნილი ახალი რეესტრის ფარგლები; პირადი მონაცემები არ არის შეტანილი.

- [AquaSignal — საქართველოს წყლის მონიტორინგის ქსელების ინვენტარი](research/drafts/NOEMA-2026-006-georgia-water-monitoring-inventory-2026-11-26.md) — ოფიციალური ქსელების მასშტაბი და მონაცემთა ხელმისაწვდომობის ზღვარი.
- [AquaSignal — WRP 2025 drinking-water harm independent reproduction](research/preprints/NOEMA-2026-006-aquasignal-wrp2025-water-harm-reproduction.md) — WP22443-ის 7% + 6% = 13% გამომცემლის rounding rule-ით; self-reported harm და არა ლაბორატორიული contamination.
- [AquaSignal — საქართველოს დადგენილება №447: წყლის მონიტორინგის ოპერაციული მოთხოვნები](research/drafts/NOEMA-2026-006-aquasignal-georgia-decree447-water-monitoring-2026-11-28.md) — 1 დეკემბრის წლიური გეგმის ვადა, რისკზე დაფუძნებული/მიკრობიოლოგიური მონიტორინგი, გამოძიებითი პროგრამა და 2028 წლის ბიოტა/ნალექის გარდამავალი მოთხოვნა და 2027 წლის ნიტრატებისადმი მოწყვლადი ზონების იდენტიფიკაციის ვადა; ონკანის წყლის კონტროლი ცალკეა.
- [NOEMA-2026-011 — groundwater quantitative-status readiness and Decree №447 Annex source audit](research/preprints/NOEMA-2026-011-georgia-groundwater-quantitative-readiness.md) — Article 7(1)-(2) primary HTML facts; Annex 2 frequency/method rows remain secondary-transcription-only because the official DOCX was not retrieved or hashed.
- [NOEMA-2026-007 — WRP 2025 გაფრთხილების მიღებისა და მოქმედების შესაძლებლობის დამოუკიდებელი გამეორება](research/preprints/NOEMA-2026-007-wrp2025-warning-action-reproduction.md) — PROJWT-შეწონილი აგრეგატები, ზუსტი მნიშვნელები და საქართველოს 99-კაციანი ბაზის შეზღუდვა.
- [NOEMA-007 — საქართველოს შვიდი მდინარის აუზის MHRM გეგმების სტატუსის შეჯერება](research/drafts/NOEMA-2026-007-georgia-basin-readiness-2026-11-27.md) — NEA 25.11.2026 preparation/consultation notice compared with GEO Outlook's secondary 2024–2026 project-result claim; conflicting stage/ambiguous '4 basins' wording retained as UNRESOLVED_SOURCE_STATUS; no approval or 7/11 coverage claim.
- [NOEMA-2026-007 — საქართველოს ადრეული გაფრთხილების შესაძლებლობები: COP31-ის სააგენტოს სიგნალი](research/drafts/NOEMA-2026-007-georgia-cop31-early-warning-capabilities-2026-11-16.md) — NEA-ს მიერ აღწერილი დაკვირვების ქსელის გაფართოება, პროგნოზირების მოდერნიზაცია და meteo.gov.ge-ზე წვდომა; ეფექტიანობის მაჩვენებლები დამოუკიდებლად დადასტურებული არ არის.
- [NOEMA-2026-007 — საქართველოს გაფრთხილების უფლებამოსილებისა და შესაძლებლობების crosswalk](research/drafts/NOEMA-2026-007-georgia-warning-authority-crosswalk-2026-11-28.md) — NEA-სა და დეპარტამენტების ოფიციალური ფუნქციები, 278 სადგურის 2026-07-14 მდგომარეობით გამოცხადებული რაოდენობა, 298-ის წლის ბოლომდე მიზანი და მეწყრულ უბნებზე 28/22 ინფრასტრუქტურული მაჩვენებელი; სამიზნე მიღწეულ შედეგად არ ითვლება და გაფრთხილების ეფექტიანობა დაუდასტურებელია.

- [NOEMA-2026-001](research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნები; მეთოდოლოგიური გადახედვა: [დამატება A](research/drafts/2026-11-23-methodological-reassessment.md).
- [NOEMA-2026-002](research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი და საბაზისო heuristic-ის ტესტი.
- [NOEMA-2026-003](research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA GlobalTemp-ის ტენდენციის საწყისი წლის მგრძნობელობა და NASA GISTEMP/HadCRUT5-თან cross-dataset გამეორება.
- [NOEMA-2026-005 სამუშაო დრაფტი](research/drafts/NOEMA-2026-005-floating-summation-order.md) — სრული მეთოდოლოგია და ექსპერიმენტის ჟურნალი.
- [NOEMA-2026-005 წინასწარი მომხმარებლის ანგარიში](research/preprints/NOEMA-2026-005-floating-point-summation.md) — საიტზე გამოსაჩენი მოკლე ანგარიში; დამოუკიდებელი რეცენზია ჯერ არ დასრულებულა.
- [NOEMA-005 Run 59 — დამოუკიდებელი x86-64 KVM OpenMP გამეორება](research/drafts/NOEMA-2026-005-run59-independent-x86_64-kvm-replication-2026-11-28.md) — 48 method/worker cell, 960 timed run, 20 repetitions; full Neumaier state 20/20 ორივე synthetic layout-ში; timing აღწერითია და bare-metal შედეგს არ წარმოადგენს.
- Run 34-ის დამატებითი x86-64 real-thread შეჯამება: `data/noema-005/threaded-run-2026-11-27-summary.json` და Schema; 4 hosted artifact, 192 configuration, 576 measured run. Neumaier-state 192/192 სწორი, მაგრამ არცერთმა threaded configuration-მა serial baseline-ს wall-time-ით ვერ აჯობა.
- Run 36-ის დამატებითი x86-64 hosted artifact reproduction: `data/noema-005/threaded-run36-artifact-snapshot.json`, schema `data/noema-005/threaded-run36-artifact-snapshot.schema.json` და reproducer `scripts/reproduce_noema005_run36_threaded.py`. ოთხი PR-triggered artifact, 192 configuration და 576 measured run; Neumaier-state 192/192 სწორია, თუმცა free-threaded median speedup ორ batch-ს შორის 1.1459×-დან 0.9474×-მდე იცვლება. Raw thread IDs და დეტალური kernel/glibc build strings არ ინახება; snapshot-ში რჩება მხოლოდ coarse AWS/Azure runner-family; ფიზიკური მოწყობილობა არ შემოწმებულა.
- აუდიტის გამეორებადი სკრიპტი: `scripts/audit_signbase.py`; შედეგები: `data/audits/signbase-v2-audit-2026-11-23.json`.
- მოკლე მიმდევრობების ენტროპიის სიმულაცია: `scripts/short_sequence_bias_simulation.py`.
- NOEMA-003-ის NOAA ანალიზი: `scripts/analyze_noema003.py`; cross-dataset შედარება და HAC ლაგების 1–6 ტესტი: `scripts/compare_noema003_datasets.py`; მონაცემთა snapshot-ები, metadata და შედეგები: `data/noema-003/`.
- NOEMA-005-ის ექსპერიმენტი: `scripts/simulate_noema005_summation.py`; runtime/memory benchmark: `scripts/benchmark_noema005_summation.py`; სრული პროფილის workflow: `.github/workflows/noema005-full-benchmark.yml`; ტესტები: `tests/test_noema005_summation.py` და `tests/test_benchmark_noema005_summation.py`; numerical შედეგები: `data/noema-005/floating-summation-results.json`; benchmark protocol: `data/noema-005/benchmark-protocol.json`; სრული benchmark-ის შეჯამება: `data/noema-005/benchmark-full-profile-summary-2026-11-24.json`.
- NOEMA-007-ის WMO roadmap და anticipatory-action snapshots, aggregate-only action-readiness პროტოტიპი: `data/noema-007/wmo-roadmaps-2026-source-snapshot.json`, `data/noema-007/wmo-roadmaps-2026-derived-results.json`, `scripts/reproduce_noema007_wmo_roadmaps.py`, `data/noema-007/action-readiness-observation.schema.json`, `noema_core/action_readiness.py`; synthetic-only tests `tests/test_noema007_wmo_roadmaps.py` და `tests/test_noema007_action_readiness.py`. WMO-ს 35 validated roadmap-ის published aggregates-იდან 20/35 = 57.1429% შეიცავს მკაფიო budget allocation-ს; USD 1.38bn / 20 = დაახლოებით USD 69m თითო budgeted roadmap-ზე. ეს არ არის warning reach ან protection measure და underlying country-level data დამოუკიდებლად არ გადაგვიმუშავებია. UNDRR/WMO-ის 2026-11-11 განახლებაში 2025 წლის 154-დან 262-მდე active anticipatory-action frameworks-ის ზრდა (NOEMA arithmetic: 70.1299%), 146 activation, 9.6 მილიონი პირდაპირ მიღწეული ადამიანი და USD 119.9m pre-arranged financing არის source-reported aggregates; ეს არ ადასტურებს comprehension-ს, verified protective action-ს ან avoided loss-ს. Snapshot/script/test: `data/noema-007/anticipatory-action-2025-source-snapshot.json`, `scripts/reproduce_noema007_anticipatory_action.py`, `tests/test_noema007_anticipatory_action.py`.
- NOEMA-005-ის რეალური CPU-thread გაგრძელება: `scripts/benchmark_noema005_threaded_reduction.py`; ტესტები: `tests/test_benchmark_noema005_threaded_reduction.py`; GIL/free-threaded CI: `.github/workflows/noema005-threaded-benchmark.yml`; პროტოკოლი: `data/noema-005/threaded-benchmark-protocol.json`; ადგილობრივი GIL-control შეჯამება: `data/noema-005/threaded-benchmark-local-cpython-3.13.5-gil-summary.json`; სრული მეთოდოლოგიური დამატება: `research/drafts/NOEMA-2026-005-real-thread-benchmark-addendum.md`. შედეგების შეჯამებები: `data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json` და `data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json`; preliminary გვერდი განახლებულია real-thread შედეგებით.
- NOEMA-005 experiment 002 (CPython 3.14.10/3.14.10t; hosted x86-64, ARM64 Ubuntu and ARM64 macOS): frozen sanitized aggregate `data/noema-005/experiment-002-summary.json`; schema `data/noema-005/experiment-002-summary.schema.json`; reproduction `scripts/reproduce_noema005_experiment_002.py`. Six runtime/runner cells, 384 configurations and 1,152 measured runs; full Neumaier state 288/288 correctly rounded, scalar Neumaier 252/288, worker-local `math.fsum` partials 252/288, naive scalar 0/288. No threaded configuration beat its matching serial baseline; result remains preliminary.
- NOEMA-005-ის 2026-11-26 real-thread repeat: `data/noema-005/threaded-rerun-2026-11-26.json`, `scripts/validate_noema005_threaded_rerun.py`, `tests/test_noema005_threaded_rerun.py` და `research/drafts/NOEMA-2026-005-threaded-rerun-audit-2026-11-26.md`. CPython 3.14.4-ის GIL-enabled/free-threaded run-ში Neumaier-state სიზუსტე იყო 48/48 ორივე რეჟიმში, მაგრამ median wall-time speedup — 0.7539× და 0.9519×; ეს არის ერთი hosted x86-64 VM-ის სინთეზური შედეგი და არა ზოგადი აჩქარების მტკიცებულება.
- NOEMA-005-ის OpenMP CPU/wall timing anomaly diagnostic: `scripts/noema005_openmp_timing_diagnostic.c`, `scripts/run_noema005_openmp_timing_diagnostic.py`, schema `data/noema-005/openmp-timing-diagnostic.schema.json`, tests `tests/test_noema005_openmp_timing_diagnostic.py`; per-thread CPU clocks, per-thread affinity, cgroup v2 cpuset/quota and process wall/CPU clocks are recorded in a privacy-minimal hosted-runner artifact. Frozen run 45954993085: 80 runs, 0 CPU/wall anomalies above 4.25, max ratio 4.008956678; raw compressed report and SHA-256 manifest are committed under data/noema-005. This is a diagnostic, not physical-hardware replication.
- NOEMA-005-ის native C/OpenMP accumulator comparison: `scripts/noema005_native_accumulator_benchmark.c`; runner `scripts/run_noema005_native_accumulator_benchmark.py`; report validator `scripts/validate_noema005_native_accumulator_report.py`; tests `tests/test_noema005_native_accumulator.py`; x86-64/ARM64 workflow `.github/workflows/noema005-native-accumulator.yml`; draft `research/drafts/NOEMA-2026-005-native-accumulator-2026-11-26.md`. Exact-head x86-64 and ARM64 CI reports are stored as workflow artifacts; the sub-experiment remains draft.
- NOEMA-005-ის დამოუკიდებელი MPFR 4.2.1 cross-check (hosted Ubuntu package): `tests/noema005_mpfr_rounding_harness.c`; ტესტი `tests/test_noema005_mpfr_rounding.py`; signed-range regression `tests/test_noema005_exact_rounding.py`; x86-64/ARM64 workflow `.github/workflows/noema005-native-accumulator.yml`; მეთოდოლოგია `research/drafts/NOEMA-2026-005-mpfr-crosscheck-2026-11-26.md`. 467 synthetic signed inputs თითოეულ hosted architecture-ზე მოწმდება MPFR_RNDN-ის წინააღმდეგ; შედეგი რჩება preliminary და არ წარმოადგენს physical-hardware replication-ს ან formal proof-ს.
- NOEMA-005-ის fixed-width exact accumulator overflow guard: `scripts/noema005_native_accumulator_benchmark.c`; native boundary harness `tests/noema005_accumulator_overflow_harness.c`; Python test `tests/test_noema005_accumulator_overflow.py`; მეთოდოლოგიური დრაფტი `research/drafts/NOEMA-2026-005-checked-overflow-2026-11-26.md`. PR #58 merged; exact-head quality, native x86-64/ARM64 and GIL/free-threaded CI passed. კვლევა preliminary რჩება დამოუკიდებელი numerical-method review-ის, representative workloads-ისა და physical-hardware replication-ის მოლოდინში.
- NOEMA-005-ის ARM64 replication: workflow `.github/workflows/noema005-arm64-replication.yml`; პროტოკოლი `research/drafts/NOEMA-2026-005-arm64-replication-protocol.md`; პირველი batch-ის შეჯამება `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`; სამი batch-ის განმეორების, report/archive hash-ებისა და run metadata-ს ფაილი `data/noema-005/arm64-repeat-validation-2026-11-26.json`; validator `scripts/validate_noema005_arm64_report.py`; ტესტები `tests/test_validate_noema005_arm64_report.py`, `tests/test_noema005_arm64_summary.py` და `tests/test_noema005_arm64_repeat_validation.py`. სამ ARM64 batch-ში Neumaier-state სიზუსტე 576/576 იყო; timing/CPU-wall დიაგნოსტიკა run-sensitive დარჩა. კვლევის სტატუსი რჩება preliminary. ARM64 benchmark workflow is path-filtered: a separate PR that changes only documentation/catalog files does not trigger the ARM64 matrix. In an existing PR that already changes benchmark/protocol paths, a later PR synchronization can still rerun it because pull_request path filtering evaluates the PR's full changed-file set.
- [NOEMA-2026-010 Run 51 — local OpenMP compensated reduction](research/preprints/NOEMA-2026-010-run51-local-openmp-compensated-reduction.md) — one KVM-virtualized x86-64 host with a four-CPU cgroup quota; full Neumaier state was correct on both adversarial layouts, but this is not bare-metal or independent second-device replication.
- `scripts/verify_noema005_run51_local_openmp.py` recomputes wall/CPU medians, speedup and effective input-scan rate from pinned raw samples and rejects tampered derived fields.
- NOEMA-005 ARM64 Run 33 frozen artifact verification: `data/noema-005/arm64-run33-artifact-verification-2026-11-28.json`, closed schema, offline verifier and regression tests; hosted ZIP/raw-report hashes and aggregates were rechecked. No new benchmark or physical-device replication is claimed.

## Workflow და ეტაპების ორკესტრაცია

`noema_core/workflows.py` ინახავს workflow run-ებსა და step-ებს იმავე SQLite ბაზაში. თითოეულ workflow-ს აქვს იდempotency key, DAG ციკლების/არარსებული დამოკიდებულებების ვალიდაცია, მხოლოდ მზადყოფნაში მყოფი ნაბიჯების dispatch და ჩავარდნილი prerequisite-ის ქვედა ნაბიჯების `blocked` მდგომარეობაში გადაყვანა. ყველა task type-ს უნდა ჰქონდეს trusted `HandlerRegistry`-ში რეგისტრირებული handler. `IntervalScheduler` ქმნის განმეორებად workflow გაშვებებს ინტერვალის მიხედვით, ინახავს თითოეული დაგეგმილი fire-ის სტატუსს და იცავს დუბლირებული გაშვებისგან. გამოტოვებული გაშვებისთვის არსებობს `catch_up_once` და `skip` პოლიტიკა. `WorkerSupervisor`-ის `scheduler` პარამეტრი ყოველ ციკლზე ამოწმებს due schedule-ებს, ქმნის workflow-ს, ასრულებს job-ებს და ავტომატურად აახლებს DAG-ს. ეს არის ინტერვალური scheduler; cron/calendar expression-ები და OS service deployment ჯერ არ არის დამატებული.

## სერვისის გაშვება

NOEMA-ს ერთჰოსტიანი runtime ირთვება ბრძანებით `python -m noema_core.service`. `--check` ამოწმებს mission policy-ს, SQLite/audit მთლიანობასა და შიდა self-check განრიგს. სერვისი ჩაშენებულად ასრულებს მხოლოდ მისიის, queue-ისა და runtime გარემოს ლოკალურ თვითშემოწმებას; გარე ინფორმაციის connector-ები ჯერ არ არის ჩართული. Linux `systemd`-ის ინსტალაციის ინსტრუქცია და უსაფრთხოების პარამეტრები აღწერილია [SERVICE_DEPLOYMENT.md](docs/SERVICE_DEPLOYMENT.md); unit ფაილი: `deploy/systemd/noema.service`.

## ტექნიკური სამუშაოების მართვა

NOEMA-ს შიდა სამუშაოების მართვის პირველი ბირთვი ინახავს დავალებებს მომხმარებლის ლოკალურ `~/.noema/noema-jobs.sqlite3` ბაზაში (ან `NOEMA_JOBS_DB` გარემოს ცვლადით მითითებულ მისამართზე). მას აქვს idempotency key, worker lease და ვადის გასვლის შემდეგ აღდგენა, შეზღუდული retry, შედეგის hash და SHA-256-ით დაკავშირებული audit events. Queue არ ასრულებს თვითნებურ კოდს; სამუშაოს შესრულება მომავალ ეტაპზე მხოლოდ წინასწარ რეგისტრირებულ handler-ებს გადაეცემა. CLI: `python -m noema_core.jobs_cli --help`.

Off-host backup manifest metadata-ს შემოწმება: `python scripts/validate_noema_backup_manifest.py /path/to/manifest.json` (მხოლოდ schema/format validation; არა signature, encryption ან provider verification). 

დავალებების რიგისა და worker execution-ის დეტალები აღწერილია [ავტონომიური მართვის არქიტექტურაში](docs/AUTONOMY_ARCHITECTURE.md).

ლოკალური backup/restore smoke drill: `python -m noema_core.jobs_cli --db ~/.noema/noema-jobs.sqlite3 restore-drill`. ეს ამოწმებს მხოლოდ იმავე ჰოსტზე snapshot/restore გზას და არ ამტკიცებს off-host disaster-recovery მზადყოფნას.

## ძირითადი მისია და ავტონომია

NOEMA-ის დამფუძნებელი მიზანი, ინოვაციების ციკლი, კანონიერად ხელმისაწვდომი ინფორმაციის გამოყენების პრინციპები და ავტონომიური მოქმედებების საზღვრები აღწერილია [ძირითადი მისიის წესდებაში](docs/CORE_MISSION.md). მისიის კონფიგურაცია და მისი შემოწმებადი პოლიტიკა განთავსებულია `noema_core/` პაკეტში. უცნობი წყაროები და მოქმედებები უსაფრთხოების მიზნით იბლოკება; საჯარო წვდომა ავტომატურად არ ანიჭებს ხელახალი გამოყენების უფლებას.

## პროექტის მდგომარეობა

იხილე [მიმდინარე სტატუსი და დადასტურებული შემოწმებები](docs/PROJECT_STATUS.md).

## კვლევის სტანდარტები

- [კვლევითი და სარედაქციო სტანდარტი](docs/RESEARCH_STANDARD.md)
- [NOEMA-002 ბრმა კოდირების პროტოკოლი](research/protocols/NOEMA-002-blind-coding-protocol.md)

## კვლევის სტატუსები

- `draft` — სამუშაო ვერსია.
- `review` — წყაროებისა და არგუმენტების გადამოწმება.
- `preliminary` — საჯარო წინასწარი შედეგი; არა დამოუკიდებლად რეცენზირებული.
- `published` — სრული გამოქვეყნების საკონტროლო სიის გავლილი მასალა.

## გამოქვეყნების უსაფრთხო წესი

GitHub Pages-ის არტეფაქტში შედის `index.html`, `assets/`, `data/research.json`, `data/research.schema.json` და სტატუსის მიხედვით ნებადართული კვლევითი გვერდები. `research/drafts/` არასოდეს კოპირდება საჯარო არტეფაქტში. `research/preprints/` ქვეყნდება მხოლოდ მკაფიო `preliminary` სტატუსითა და რეცენზიის/შეზღუდვების გაფრთხილებით; `research/published/` განკუთვნილია მხოლოდ სრული სარედაქციო საკონტროლო სიის გავლილი კვლევებისთვის.

## ლოკალური გაშვება

გაუშვი `python -m pip install -r requirements-site.txt`, შემდეგ `python scripts/build_site.py --output _site` და `python -m http.server 8000 --directory _site`. ბრაუზერში გახსენი `http://localhost:8000`.

## გამოქვეყნება

პროექტი მომზადებულია GitHub Pages-ზე განსათავსებლად. ერთჯერადი პარამეტრი და პირველი გაშვების ნაბიჯები აღწერილია [DEPLOYMENT.md](docs/DEPLOYMENT.md). რეალური deployment მხოლოდ წარმატებული Actions გაშვების შემდეგ ჩაითვლება დასრულებულად.

## მონაცემთა ბაზა და საჯარო კატალოგი

საიტის მიმდინარე საჯარო მონაცემთა წყარო არის Git-ით ვერსიაკონტროლირებადი `data/research.json`, რომელსაც ამოწმებს `data/research.schema.json` და Python ვალიდატორი. Pages build ქმნის მკაფიო სტატუსის მქონე სტატიებსა და JSON კატალოგს. ეს მიდგომა სწრაფი, გამჭვირვალე და მარტივად აღსადგენია, თუმცა არ არის ტრანზაქციული/ცოცხალი მონაცემთა ბაზა. დინამიკური მომხმარებლის ანგარიშების, კომენტარების, ძიების და audit log-ისთვის საჭიროა NOEMA-ს ცალკე Supabase პროექტი; სხვა პროექტის ბაზა არ უნდა იქნეს გამოყენებული.

## NOEMA-005 native OpenMP experiment

A reproducible C/OpenMP benchmark for compensated reduction, exact synthetic references, wall/process-CPU timing and provenance is available in [`scripts/noema005_openmp_benchmark.c`](scripts/noema005_openmp_benchmark.c). The hosted 20-case result summary, full raw timing report and strict validator are `data/noema-005/native-openmp-ci-summary-2026-11-26.json`, `data/noema-005/native-openmp-raw-report-2026-11-26.json`, `scripts/validate_noema005_openmp_report.py` and `tests/test_validate_noema005_openmp_report.py`. The earlier local report is retained but invalidated because it contains only 10 of 20 expected cases. Methodology and limitations are documented in [`research/drafts/NOEMA-2026-005-openmp-native-addendum.md`](research/drafts/NOEMA-2026-005-openmp-native-addendum.md).


## NOEMA-005 — two-run real-thread comparison (2026-11-26)

Two raw workflow reports from run `45867519546` are preserved as gzip+base64 files under `data/noema-005/raw/`. `scripts/reproduce_noema005_threaded_reruns.py --check` verifies raw report hashes and recomputes the aggregate comparison against run `45850716742`. The free-threaded Neumaier-state median crossed 1.0 only in the second run (0.9519× → 1.0181×); this is run-to-run sensitivity, not a robust speedup claim. The study remains preliminary.

- [AquaSignal — NFA 2026 drinking-water facility control event](research/drafts/NOEMA-2026-006-nfa-2026-drinking-water-facility-control-event-2026-11-27.md) — Zugdidi-ში 2026-08-12-ის ოფიციალური ინსპექტირების metadata; ლაბორატორიული შედეგები/ნიმუშების მნიშვნელი არ გამოქვეყნებულა და ბიზნესის იდენტიფიკატორები გამოტოვებულია.
- [AquaSignal — NFA 2025 სასმელი წყლის მონიტორინგის დარღვევების ფაილის წვდომის კვალი](research/drafts/NOEMA-2026-006-nfa-2025-monitoring-violations-access-lead-2026-11-27.md) — ოფიციალური XLSX ბმული დაფიქსირებულია metadata-only რეჟიმში; ფაილის შიგთავსი, წყლის ცალკე მნიშვნელი და reuse პირობები ჯერ დაუდასტურებელია.
- [AquaSignal — NFA 2026 drinking-water sampling plan](research/drafts/NOEMA-2026-006-nfa-2026-drinking-water-sampling-plan-2026-11-27.md) — 750 დაგეგმილი სინჯი (550 საბაზო + დაახლოებით 200 დამატებითი დაფასოებული წყლისთვის); ეს არ არის ფაქტობრივი აღებული/გამოკვლეული ნიმუშების რაოდენობა ან შედეგი.
- AquaSignal historical groundwater baseline: ENI SEIS/EEA C11, NEA data for 2016–2017 — 34/45 sites, twice-yearly sampling, 33/34 averages above 10 mg NO3/L and all below 50 mg NO3/L; western sites below 1 mg NO3/L. Historical aggregated context only, not current 2026 results.
- Georgia Decree №58/2014: nitrate 50 mg/L as NO3- and nitrite 0.2 mg/L as NO2-; WHO 2026 nitrite guidance 3 mg/L is not a Georgian compliance threshold.
- [AquaSignal — Georgian drinking-water operational controls](research/drafts/NOEMA-2026-006-georgian-drinking-water-operational-controls-2026-11-28.md) — Decree №58/2014 sampling points, population/source-based minimum frequencies, supplier duties, emergency/repeat-sampling triggers and accredited-lab requirement; legal transition review pending; no sample results.
- [AquaSignal — NEA 2021–2025 groundwater monitoring report and nitrate-methodology access lead](research/drafts/NOEMA-2026-006-nea-2021-2025-groundwater-report-access-lead-2026-11-28.md) — official announcement 2026-11-26; public RAR link recorded metadata-only; archive not retrieved/hashed/inspected; 2027-09-01 statutory milestone recorded separately; no sample-level results or thresholds asserted. WHO 2026 comparator (50 mg/L nitrate ion, 3 mg/L nitrite ion, combined ratio <=1) is recorded separately as drinking-water guidance, not Georgian law or an automatic raw-groundwater threshold.
- [AquaSignal — Decree №447 Annex transcription audit](research/drafts/NOEMA-2026-006-decree447-annex-transcription-audit-2026-11-28.md) — primary Matsne main text is separated from Legali.ge's secondary Annex 2 transcription; groundwater frequency and nitrate/low-flow method rows remain unverified until the official DOCX is retrieved and hashed.


## NOEMA Run 40 — new work in review (2026-11-28)

- [AquaSignal PR #223](https://github.com/maisuradzee/bibmom/pull/223): Georgia Decree №447/2026 monitoring framework and explicit NO3/NO3-N unit conversion; exact-head CI passed, Draft pending independent water-chemistry/legal review.
- [INFRA-001 PR #224](https://github.com/maisuradzee/bibmom/pull/224): local SQLite high-water compare-and-advance reference model; exact-head CI passed, Draft pending independent security review.
- [NOEMA-007 PR #225](https://github.com/maisuradzee/bibmom/pull/225): Georgia Decree №440/2026 preliminary flood-risk framework and future statutory milestones; exact-head CI passed, Draft pending independent disaster-risk/legal review.
- Research PRs #223–225 remain Draft and unmerged. The separate status/portfolio PR #226 merged as Main SHA `639ad4485dbf7fc73e523245844cd4bdc663849b`; Main Quality CI and Pages deployment succeeded. See [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for exact run IDs. No research implementation from #223–225 is on Main.


## AquaSignal — current WHO drinking-water guidance (17 June 2026)

The WHO's fourth edition incorporating the third addendum is the current international comparator. Its chemical fact sheet retains nitrate at 50 mg/L as nitrate ion, nitrite at 3 mg/L as nitrite ion, the combined nitrate/nitrite ratio requirement (sum of concentration-to-guideline ratios no greater than 1), and the conversion factor 1 mg/L as nitrate ion = 0.226 mg/L as nitrate-nitrogen. These WHO values are not Georgian legal limits; Government Decree №58/2014's nitrite requirement is recorded separately. A combined ratio requires paired measurements from the same sample and matrix; no such calculation is made without paired data.

- [WHO 2026 Guidelines](https://www.who.int/publications/i/item/9789240121225)
- [WHO 2026 chemical fact sheets PDF](https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/dwq-guidelines-4/gdwq_4ed_with_third-addenda_chemical-fact-sheets.pdf?sfvrsn=77d972e1_5)


## AquaSignal — Georgia water-monitoring framework and nitrate unit crosswalk (2026-11-28)

- Government Decree №447/2026 establishes a risk-based environmental surface-water and groundwater monitoring framework; its annex DOCX remains uninspected, and this is not potable-water compliance evidence.
- The EEA C11 source reports different nitrate bases: rivers/lakes in mg NO3-N/L and groundwater in mg NO3/L. `noema_core/water_chemistry.py` preserves the matrix and original basis while applying the WHO-published rounded 0.226 conversion factor; it does not classify water or apply thresholds.
- [WHO 2026 scope audit](research/drafts/NOEMA-2026-006-who-2026-guidance-scope-audit-2026-11-28.md) separates the consolidated-edition publication date (17 June 2026) from the nitrate/nitrite fact sheet's stated assessment date (2016). The 2026 summary does not identify a new nitrate/nitrite reassessment.
- A combined WHO nitrate/nitrite ratio is not calculated without paired same-sample, same-time, same-matrix measurements and compatible ion reporting bases. WHO guidance remains distinct from Georgian Decree №58/2014.

- [AquaSignal — NEA 2021–2025 groundwater report procurement access lead](research/drafts/NOEMA-2026-006-nea-procurement-access-lead-2026-11-27.md) — official 26.11.2026 report-prepared announcement plus contract T-100801; final PDF/CD, acceptance status, archive checksum and reuse terms remain unverified.


## NOEMA-007 — Georgia multi-hazard basin-plan chronology (2025–2026)

The National Environmental Agency's notices describe distinct stages: four plans discussed as prepared in October 2025; presentation of risk-assessment validation process/results for seven basins in April 2026; and consultation on preparing plans for seven named basins in November 2026. These records do not establish formal approval, publication or implementation of all seven plans. The chronology and its evidence boundaries are recorded in [the Run 44 research note](research/drafts/NOEMA-2026-007-georgia-basin-program-chronology-2026-11-28.md) and [structured source record](data/noema-007/georgia-seven-basin-chronology-2026-11-28.json).


**Run 44 implementation:** [PR #247](https://github.com/maisuradzee/bibmom/pull/247) merged as `218021f38ed8bf3732b449fcdfea2cbbb821e96a`. Main Quality CI and GitHub Pages deployment succeeded on this exact commit.


## NOEMA Run 52 — derived-metric verification and groundwater readiness (2026-11-28)

- [PR #273](https://github.com/maisuradzee/bibmom/pull/273) strengthened the NOEMA-005 Run 51 verifier: speedup and effective input-scan GiB/s are recomputed from pinned raw timing samples rather than trusted from raw summary fields. Corrupted derived values and malformed/nonpositive timing samples are rejected.
- [PR #275](https://github.com/maisuradzee/bibmom/pull/275) adds NOEMA-2026-011 and a synthetic-only AquaSignal groundwater quantitative-readiness gate based on Decree №447 Article 7(1)-(2). The gate never assigns a good/poor status.
- Legali.ge Annex 2 rows are secondary transcription only. The official Matsne DOCX remains not retrieved and unhashed; no Annex-derived schedule is encoded in production.
- The four-stream portfolio remains unchanged. No new NOEMA-005 physical-device run, authorized Georgian warning-event dataset, groundwater water-balance record, or production disaster-recovery drill was obtained in this cycle.


## NOEMA Run 54 — nitrate evidence provenance and high-water write-failure atomicity (2026-11-28)

- [PR #283](https://github.com/maisuradzee/bibmom/pull/283) adds preliminary study **NOEMA-2026-013** on the 2026 New Zealand nitrate/preterm-birth cohort and separates WHO guidance, Georgia Decree №58/2014, the Danish 6 mg/L expert recommendation, peer-reviewed observational evidence and advocacy signals.
- The new benchmark guard compares only matching drinking-water matrices and nitrate bases; it rejects NO3-N/NO3- mismatch and never returns compliance or potability decisions.
- [PR #282](https://github.com/maisuradzee/bibmom/pull/282) adds a synthetic high-water write-abort test: SQLite rollback preserves the prior generation and exact retry succeeds. This is local transaction evidence only, not remote anti-rollback or power-loss proof.
- The Danish report's corrected 2026-01-07 version explicitly fixes NO3-/NO3-N unit confusion and says only one study was suitable for benchmark-dose modelling. The New Zealand cohort is observational and was not independently reproduced by NOEMA.
- NOEMA-005 and NOEMA-007 had no new physical-device or authorised operational dataset respectively; their existing checks were exercised by PR CI.
- Four active streams remain; no fifth stream added. Catalogue: 9 Preliminary / 0 Published.
- Final Main: `cb5f3a507ea96b345c1fce98981149d356b9dabc`. PR #283 exact-head CI passed **856 tests, 1 skipped**. Post-merge Main CI and Pages deployment are not yet independently verified; Pages is not described as updated.
- The 2027 state water-monitoring plan submission-to-Minister deadline is **2026-12-01**. It is not yet due on 2026-11-28; submission and approval remain unverified, and no breach is inferred.

See [Run 54 audit](docs/run-audits/2026-11-28-run-54.md) and [PROJECT_STATUS.md](docs/PROJECT_STATUS.md).

## NOEMA Run 53 — nitrate-zone evidence crosswalk and frozen ARM64 re-audit (2026-11-28)

- [PR #277](https://github.com/maisuradzee/bibmom/pull/277) adds preliminary study **NOEMA-2026-012**. It separates NEAP-4 2024 groundwater-nitrate activity 5.1.8 (reported 100% complete) from the 2026 statutory task in Law No.1766-Vმს-XIმპ, Article 37(2)(b.e), due 2027-09-01. The available sources do not establish that the old programme deliverable and current statutory task are identical; no contradiction or non-compliance is inferred.
- The NEA's 2026-11-26 announcement confirms that the 2021-2025 groundwater report and nitrate field methodology were prepared. Official procurement contract T-100801 (signed 2026-10-09) specifies an interactive-TOC PDF, printed copies and an acceptance act; the 20-calendar-day delivery date was 2026-10-29, but delivery/acceptance evidence was not verified. The RAR bytes remain unretrieved and unhashed.
- AquaSignal's metadata-only evidence gate never determines legal compliance. The new record remains **Preliminary**.
- [PR #278](https://github.com/maisuradzee/bibmom/pull/278) records a second, independently implemented check of the same four hosted ARM64 artifacts already reproduced in Run 45. It confirms no drift (192 cases / 576 runs) but adds no new benchmark data; all median speedups remain below 1.0.
- [PR #279](https://github.com/maisuradzee/bibmom/pull/279) marks Run 53 as a repeat frozen-artifact audit in the portfolio.
- NOEMA-007 received no new authorized Georgian warning-event/after-action dataset; INFRA-001 remains same-host only, with no external high-water authority or clean-host restore.
- Final Main: `c0a6c5a6d46dcaf1ffa22687309f6317256e4fa6`. Main Quality CI passed **839 tests, 1 skipped**; Pages build and deployment succeeded. The catalogue contains 8 Preliminary and 0 Published studies.

