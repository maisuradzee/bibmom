# NOEMA — დამოუკიდებელი კვლევითი პლატფორმა

[![NOEMA quality checks](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml)

NOEMA აერთიანებს ცოდნის მოძიებას, წყაროების გადამოწმებას, ჰიპოთეზების ჩამოყალიბებას, კვლევების არქივირებასა და შედეგების გამოქვეყნებას.

## პრინციპები

- მტკიცებულებები, ინტერპრეტაციები და ჰიპოთეზები მკაფიოდ გამოიყოფა.
- არსებით მტკიცებებს ახლავს გადამოწმებადი წყაროები.
- კვლევის მეთოდი, შეზღუდვები და გაურკვევლობები დოკუმენტირდება.
- გამოქვეყნებამდე მასალა გადის სარედაქციო და ტექნიკურ შემოწმებას.
- ავტომატიზაცია არ ნიშნავს დაუდასტურებელი შედეგების ავტომატურ გამოქვეყნებას.

## სტრუქტურა

- `index.html` — მთავარი გვერდი.
- `docs/NOEMA_OPERATING_MODEL.md` — DISCOVERY · RESEARCH · INNOVATION-ის ერთიანი სამუშაო მოდელი.
- `docs/AQUASIGNAL_MVP.md` — წყლის ხარისხის ოპერატორული ადრეული სიგნალის პროტოტიპის არქიტექტურა.
- `docs/AQUASIGNAL_EVENT_STORE.md` — ინციდენტების კერძო, append-only SQLite event store-ის უსაფრთხოების საზღვრები და აღდგენის შეზღუდვები.
- `docs/OFFSITE_BACKUP_ARCHITECTURE.md` — off-host backup/recovery არქიტექტურა; local detached Ed25519 manifest verification უკვე პროტოტიპად არსებობს, მაგრამ encryption/decryption, provider retention, anti-rollback high-water და clean-host restore ჯერ არ არის დანერგილი; `data/noema-backup-manifest.schema.json` განსაზღვრავს მკაცრ, საიდუმლო მასალის არმქონე metadata contract-ს.
- `noema_core/aquasignal.py` — AquaSignal-ის დეტერმინისტული, მხოლოდ გადაწყვეტილების მხარდამჭერი წესების ძრავა.
- `noema_core/aquasignal_store.py` — ინციდენტების replay-ზე დაფუძნებული SQLite persistence, SHA-256 audit chain და unsigned caller-supplied checkpoint-ის hash/count comparison.
- `noema_core/aquasignal_checkpoint.py` — exact canonical payload-ზე detached Ed25519 checkpoint verification, event-chain head matching და caller-managed external monotonic high-water guard; private keys და high-water storage ამ public prototype-ში არ ინახება.
- `noema_core/action_readiness.py` — NOEMA-007-ის event/area aggregate-only warning-to-action metrics validator; endpoint receipts და survey denominators განცალკევებულია.
- `docs/NOEMA007_DISCLOSURE_CONTROL.md` — cross-release differencing/complementary-suppression audit; per-record k-threshold არ ითვლება სრულ privacy guarantee-ად.
- `noema_core/backup_manifest.py` — strict Draft 2020-12 manifest validator, streamed plaintext/ciphertext SHA-256/byte-length verifier და caller-supplied trusted Ed25519 public key-ით exact-byte detached-signature verification; decryption, provider retention, anti-rollback და restore ცალკე ეტაპებია.
- `noema_core/mission.json` და `noema_core/mission.py` — მანქანურად წაკითხვადი მისია, ინფორმაციის წვდომის პოლიტიკა და ავტონომიური მოქმედებების წესები.
- `noema_core/jobs.py`, `noema_core/jobs_cli.py`, `noema_core/worker.py`, `noema_core/supervisor.py`, `noema_core/workflows.py`, `noema_core/scheduler.py` და `noema_core/service.py` — მდგრადი queue/worker, metrics და verified SQLite backup/restore CLI.
- `assets/styles.css` და `assets/articles.css` — მთავარი გვერდისა და კვლევითი სტატიების ვიზუალური სტილები.
- `data/research.json` — საჯარო, ვერსიაკონტროლირებადი კვლევების კატალოგი; `data/research.schema.json` განსაზღვრავს ჩანაწერების სტრუქტურას. ეს არის ამჟამინდელი სტატიკური კატალოგი და არა Supabase/სერვერული მონაცემთა ბაზა.
- `data/research-portfolio.json` და `data/research-portfolio.schema.json` — 3–5 აქტიური კვლევითი ნაკადის საერთო პორტფელი, თითოეული ნაკადის კითხვით, მეთოდით, წყაროებით, რისკებით, სტატუსითა და შემდეგი ნაბიჯით.
- `data/noema-003/` — NOAA-ს ფიქსირებული მონაცემთა ამონარიდი, NASA/HadCRUT5/NOAA snapshot-ები, provenance metadata და გამეორებადი შედეგები.
- `data/noema-005/` — binary64 ჯამის რიგითობის ექსპერიმენტის გაყინული შედეგები, ზუსტი reference შედარება და runtime/CPU-thread benchmark არტეფაქტები.
- `data/noema-007/` — UNDRR/WMO 2026 early-warning და anticipatory-action aggregate snapshots, reproducible arithmetic და privacy-safe action-readiness schema; რეალური event-level მონაცემი ჯერ არ არსებობს.
- `research/drafts/` — სამუშაო ჩანაწერები; Pages არტეფაქტში არ შედის, თუმცა საჯარო GitHub საცავში იკითხება.
- `research/preprints/` — წინასწარი, მომხმარებლისთვის მკაფიო გაფრთხილებით გამოჩენილი კვლევები.
- `research/published/` — სრული გამოქვეყნების საკონტროლო სიის გამვლელი კვლევები.
- `research/TEMPLATE.md` — კვლევის დოკუმენტის შაბლონი.
- `.github/workflows/ci.yml` — საბაზისო შემოწმებები.
- `scripts/build_site.py` — Markdown კვლევების უსაფრთხო HTML-გვერდებად გარდაქმნა და საჯარო არტეფაქტის აწყობა.
- `scripts/validate_drafts.py` — დრაფტების მინიმალური სარედაქციო სისრულის ავტომატური შემოწმება.
- `requirements-site.txt` — ფიქსირებული Markdown renderer ვერსია.
- `.github/workflows/deploy.yml` — საჯარო ფაილების შერჩევა და Pages deployment.

## მიმდინარე კვლევა

- [NOEMA-2026-006 AquaSignal](research/drafts/NOEMA-2026-006-aquasignal-water-early-warning.md) — სასმელი წყლის მონიტორინგის მონაცემების ადრეული სიგნალები; დოკუმენტური discovery, სინთეზური წესების ძრავა და ადგილობრივი event-store პროტოტიპი, საველე ვალიდაციის გარეშე.
undefined

- [NOEMA-2026-001](research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნები; მეთოდოლოგიური გადახედვა: [დამატება A](research/drafts/2026-11-23-methodological-reassessment.md).
- [NOEMA-2026-002](research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი და საბაზისო heuristic-ის ტესტი.
- [NOEMA-2026-003](research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA GlobalTemp-ის ტენდენციის საწყისი წლის მგრძნობელობა და NASA GISTEMP/HadCRUT5-თან cross-dataset გამეორება.
- [NOEMA-2026-005 სამუშაო დრაფტი](research/drafts/NOEMA-2026-005-floating-summation-order.md) — სრული მეთოდოლოგია და ექსპერიმენტის ჟურნალი.
- [NOEMA-2026-005 წინასწარი მომხმარებლის ანგარიში](research/preprints/NOEMA-2026-005-floating-point-summation.md) — საიტზე გამოსაჩენი მოკლე ანგარიში; დამოუკიდებელი რეცენზია ჯერ არ დასრულებულა.
- აუდიტის გამეორებადი სკრიპტი: `scripts/audit_signbase.py`; შედეგები: `data/audits/signbase-v2-audit-2026-11-23.json`.
- მოკლე მიმდევრობების ენტროპიის სიმულაცია: `scripts/short_sequence_bias_simulation.py`.
- NOEMA-003-ის NOAA ანალიზი: `scripts/analyze_noema003.py`; cross-dataset შედარება და HAC ლაგების 1–6 ტესტი: `scripts/compare_noema003_datasets.py`; მონაცემთა snapshot-ები, metadata და შედეგები: `data/noema-003/`.
- NOEMA-005-ის ექსპერიმენტი: `scripts/simulate_noema005_summation.py`; runtime/memory benchmark: `scripts/benchmark_noema005_summation.py`; სრული პროფილის workflow: `.github/workflows/noema005-full-benchmark.yml`; ტესტები: `tests/test_noema005_summation.py` და `tests/test_benchmark_noema005_summation.py`; numerical შედეგები: `data/noema-005/floating-summation-results.json`; benchmark protocol: `data/noema-005/benchmark-protocol.json`; სრული benchmark-ის შეჯამება: `data/noema-005/benchmark-full-profile-summary-2026-11-24.json`.
- NOEMA-007-ის WMO roadmap და anticipatory-action snapshots, aggregate-only action-readiness პროტოტიპი: `data/noema-007/wmo-roadmaps-2026-source-snapshot.json`, `data/noema-007/wmo-roadmaps-2026-derived-results.json`, `scripts/reproduce_noema007_wmo_roadmaps.py`, `data/noema-007/action-readiness-observation.schema.json`, `noema_core/action_readiness.py`; synthetic-only tests `tests/test_noema007_wmo_roadmaps.py` და `tests/test_noema007_action_readiness.py`. WMO-ს 35 validated roadmap-ის published aggregates-იდან 20/35 = 57.1429% შეიცავს მკაფიო budget allocation-ს; USD 1.38bn / 20 = დაახლოებით USD 69m თითო budgeted roadmap-ზე. ეს არ არის warning reach ან protection measure და underlying country-level data დამოუკიდებლად არ გადაგვიმუშავებია. UNDRR/WMO-ის 2026-11-11 განახლებაში 2025 წლის 154-დან 262-მდე active anticipatory-action frameworks-ის ზრდა (NOEMA arithmetic: 70.1299%), 146 activation, 9.6 მილიონი პირდაპირ მიღწეული ადამიანი და USD 119.9m pre-arranged financing არის source-reported aggregates; ეს არ ადასტურებს comprehension-ს, verified protective action-ს ან avoided loss-ს. Snapshot/script/test: `data/noema-007/anticipatory-action-2025-source-snapshot.json`, `scripts/reproduce_noema007_anticipatory_action.py`, `tests/test_noema007_anticipatory_action.py`.
- NOEMA-005-ის რეალური CPU-thread გაგრძელება: `scripts/benchmark_noema005_threaded_reduction.py`; ტესტები: `tests/test_benchmark_noema005_threaded_reduction.py`; GIL/free-threaded CI: `.github/workflows/noema005-threaded-benchmark.yml`; პროტოკოლი: `data/noema-005/threaded-benchmark-protocol.json`; ადგილობრივი GIL-control შეჯამება: `data/noema-005/threaded-benchmark-local-cpython-3.13.5-gil-summary.json`; სრული მეთოდოლოგიური დამატება: `research/drafts/NOEMA-2026-005-real-thread-benchmark-addendum.md`. შედეგების შეჯამებები: `data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json` და `data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json`; preliminary გვერდი განახლებულია real-thread შედეგებით.
- NOEMA-005-ის 2026-11-26 real-thread repeat: `data/noema-005/threaded-rerun-2026-11-26.json`, `scripts/validate_noema005_threaded_rerun.py`, `tests/test_noema005_threaded_rerun.py` და `research/drafts/NOEMA-2026-005-threaded-rerun-audit-2026-11-26.md`. CPython 3.14.4-ის GIL-enabled/free-threaded run-ში Neumaier-state სიზუსტე იყო 48/48 ორივე რეჟიმში, მაგრამ median wall-time speedup — 0.7539× და 0.9519×; ეს არის ერთი hosted x86-64 VM-ის სინთეზური შედეგი და არა ზოგადი აჩქარების მტკიცებულება.
- NOEMA-005-ის native C/OpenMP accumulator comparison: `scripts/noema005_native_accumulator_benchmark.c`; runner `scripts/run_noema005_native_accumulator_benchmark.py`; report validator `scripts/validate_noema005_native_accumulator_report.py`; tests `tests/test_noema005_native_accumulator.py`; x86-64/ARM64 workflow `.github/workflows/noema005-native-accumulator.yml`; draft `research/drafts/NOEMA-2026-005-native-accumulator-2026-11-26.md`. Exact-head x86-64 and ARM64 CI reports are stored as workflow artifacts; the sub-experiment remains draft.
- NOEMA-005-ის დამოუკიდებელი MPFR 4.2.1 cross-check (hosted Ubuntu package): `tests/noema005_mpfr_rounding_harness.c`; ტესტი `tests/test_noema005_mpfr_rounding.py`; signed-range regression `tests/test_noema005_exact_rounding.py`; x86-64/ARM64 workflow `.github/workflows/noema005-native-accumulator.yml`; მეთოდოლოგია `research/drafts/NOEMA-2026-005-mpfr-crosscheck-2026-11-26.md`. 467 synthetic signed inputs თითოეულ hosted architecture-ზე მოწმდება MPFR_RNDN-ის წინააღმდეგ; შედეგი რჩება preliminary და არ წარმოადგენს physical-hardware replication-ს ან formal proof-ს.
- NOEMA-005-ის fixed-width exact accumulator overflow guard: `scripts/noema005_native_accumulator_benchmark.c`; native boundary harness `tests/noema005_accumulator_overflow_harness.c`; Python test `tests/test_noema005_accumulator_overflow.py`; მეთოდოლოგიური დრაფტი `research/drafts/NOEMA-2026-005-checked-overflow-2026-11-26.md`. PR #58 merged; exact-head quality, native x86-64/ARM64 and GIL/free-threaded CI passed. კვლევა preliminary რჩება დამოუკიდებელი numerical-method review-ის, representative workloads-ისა და physical-hardware replication-ის მოლოდინში.
- NOEMA-005-ის ARM64 replication: workflow `.github/workflows/noema005-arm64-replication.yml`; პროტოკოლი `research/drafts/NOEMA-2026-005-arm64-replication-protocol.md`; პირველი batch-ის შეჯამება `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`; სამი batch-ის განმეორების, report/archive hash-ებისა და run metadata-ს ფაილი `data/noema-005/arm64-repeat-validation-2026-11-26.json`; validator `scripts/validate_noema005_arm64_report.py`; ტესტები `tests/test_validate_noema005_arm64_report.py`, `tests/test_noema005_arm64_summary.py` და `tests/test_noema005_arm64_repeat_validation.py`. სამ ARM64 batch-ში Neumaier-state სიზუსტე 576/576 იყო; timing/CPU-wall დიაგნოსტიკა run-sensitive დარჩა. კვლევის სტატუსი რჩება preliminary. ARM64 benchmark workflow is path-filtered: a separate PR that changes only documentation/catalog files does not trigger the ARM64 matrix. In an existing PR that already changes benchmark/protocol paths, a later PR synchronization can still rerun it because pull_request path filtering evaluates the PR's full changed-file set.

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
