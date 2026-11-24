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
- `noema_core/mission.json` და `noema_core/mission.py` — მანქანურად წაკითხვადი მისია, ინფორმაციის წვდომის პოლიტიკა და ავტონომიური მოქმედებების წესები.
- `noema_core/jobs.py`, `noema_core/worker.py`, `noema_core/supervisor.py`, `noema_core/workflows.py` და `noema_core/jobs_cli.py` — მდგრადი დავალებების რიგი, allowlisted worker, supervisor loop და დამოკიდებულებებზე დაფუძნებული workflow-ები.
- `assets/styles.css` და `assets/articles.css` — მთავარი გვერდისა და კვლევითი სტატიების ვიზუალური სტილები.
- `data/research.json` — საჯარო, ვერსიაკონტროლირებადი კვლევების კატალოგი; `data/research.schema.json` განსაზღვრავს ჩანაწერების სტრუქტურას. ეს არის ამჟამინდელი სტატიკური კატალოგი და არა Supabase/სერვერული მონაცემთა ბაზა.
- `data/noema-003/` — NOAA-ს ფიქსირებული მონაცემთა ამონარიდი, NASA/HadCRUT5/NOAA snapshot-ები, provenance metadata და გამეორებადი შედეგები.
- `data/noema-005/` — binary64 ჯამის რიგითობის ექსპერიმენტის გაყინული შედეგები და ზუსტი reference შედარება.
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

- [NOEMA-2026-001](research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნები; მეთოდოლოგიური გადახედვა: [დამატება A](research/drafts/2026-11-23-methodological-reassessment.md).
- [NOEMA-2026-002](research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი და საბაზისო heuristic-ის ტესტი.
- [NOEMA-2026-003](research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA GlobalTemp-ის ტენდენციის საწყისი წლის მგრძნობელობა და NASA GISTEMP/HadCRUT5-თან cross-dataset გამეორება.
- [NOEMA-2026-005 სამუშაო დრაფტი](research/drafts/NOEMA-2026-005-floating-summation-order.md) — სრული მეთოდოლოგია და ექსპერიმენტის ჟურნალი.
- [NOEMA-2026-005 წინასწარი მომხმარებლის ანგარიში](research/preprints/NOEMA-2026-005-floating-point-summation.md) — საიტზე გამოსაჩენი მოკლე ანგარიში; დამოუკიდებელი რეცენზია ჯერ არ დასრულებულა.
- აუდიტის გამეორებადი სკრიპტი: `scripts/audit_signbase.py`; შედეგები: `data/audits/signbase-v2-audit-2026-11-23.json`.
- მოკლე მიმდევრობების ენტროპიის სიმულაცია: `scripts/short_sequence_bias_simulation.py`.
- NOEMA-003-ის NOAA ანალიზი: `scripts/analyze_noema003.py`; cross-dataset შედარება და HAC ლაგების 1–6 ტესტი: `scripts/compare_noema003_datasets.py`; მონაცემთა snapshot-ები, metadata და შედეგები: `data/noema-003/`.
- NOEMA-005-ის ექსპერიმენტი: `scripts/simulate_noema005_summation.py`; runtime/memory benchmark: `scripts/benchmark_noema005_summation.py`; სრული პროფილის workflow: `.github/workflows/noema005-full-benchmark.yml`; ტესტები: `tests/test_noema005_summation.py` და `tests/test_benchmark_noema005_summation.py`; numerical შედეგები: `data/noema-005/floating-summation-results.json`; benchmark protocol: `data/noema-005/benchmark-protocol.json`; სრული benchmark-ის შეჯამება: `data/noema-005/benchmark-full-profile-summary-2026-11-24.json`.

## Workflow და ეტაპების ორკესტრაცია

`noema_core/workflows.py` ინახავს workflow run-ებსა და step-ებს იმავე SQLite ბაზაში. თითოეულ workflow-ს აქვს იდempotency key, DAG ციკლების/არარსებული დამოკიდებულებების ვალიდაცია, მხოლოდ მზადყოფნაში მყოფი ნაბიჯების dispatch და ჩავარდნილი prerequisite-ის ქვედა ნაბიჯების `blocked` მდგომარეობაში გადაყვანა. ყველა task type უნდა ჰქონდეს trusted `HandlerRegistry`-ში რეგისტრირებული handler. `WorkflowEngine.advance()` აახლებს job-ების მდგომარეობას და შემდეგი ნაბიჯების dispatch-ს; scheduler/continuous orchestration ინტეგრაცია შემდეგი ფენაა.

## ტექნიკური სამუშაოების მართვა

NOEMA-ს შიდა სამუშაოების მართვის პირველი ბირთვი ინახავს დავალებებს მომხმარებლის ლოკალურ `~/.noema/noema-jobs.sqlite3` ბაზაში (ან `NOEMA_JOBS_DB` გარემოს ცვლადით მითითებულ მისამართზე). მას აქვს idempotency key, worker lease და ვადის გასვლის შემდეგ აღდგენა, შეზღუდული retry, შედეგის hash და SHA-256-ით დაკავშირებული audit events. Queue არ ასრულებს თვითნებურ კოდს; სამუშაოს შესრულება მომავალ ეტაპზე მხოლოდ წინასწარ რეგისტრირებულ handler-ებს გადაეცემა. CLI: `python -m noema_core.jobs_cli --help`.

დავალებების რიგისა და worker execution-ის დეტალები აღწერილია [ავტონომიური მართვის არქიტექტურაში](docs/AUTONOMY_ARCHITECTURE.md).

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
