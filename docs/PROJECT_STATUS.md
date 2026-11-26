# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-26 — NOEMA-005-ის ARM64 რეალური CPU-thread replication შესრულებულია ოთხ hosted runner/runtime უჯრედზე; PR #23-ის quality CI და ARM64 workflow წარმატებულია, merge/deployment ჯერ არ მომხდარა.
- **საცავი:** [maisuradzee/bibmom](https://github.com/maisuradzee/bibmom)
- **ძირითადი branch:** `main` — მიმდინარე base commit `d46c10cf384f2eba09b4d332a323c19554f552b6`; PR #23-ის ცვლილებები ჯერ branch-ზეა.
- **მიმდინარე კვლევითი branch:** `research/noema005-arm64-replication-2026-11-26` (PR #23, მხოლოდ NOEMA-005 კვლევა, კოდი, მონაცემები, ტესტები და workflow).
- **ბოლო კვლევითი merge:** [PR #21 — NOEMA-005 real CPU-thread benchmark](https://github.com/maisuradzee/bibmom/pull/21), squash-ით merged 2026-11-25; commit `e84f2b9679c923c673319fc28fc6da5d1e021702`.
- **მიმდინარე NOEMA-005 კვლევითი PR:** [PR #23 — ARM64 real-thread replication](https://github.com/maisuradzee/bibmom/pull/23), Draft; benchmark run head `4fe358edd532d1861544951682e9125f67a4e156`. ოთხივე ARM64 job და quality/site CI წარმატებულია. კვლევის სტატუსი რჩება `preliminary`; დამოუკიდებელი გარე რეცენზია ჯერ არ დასრულებულა.

## მიმდინარე სტატუსი

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| კვლევის სტანდარტი და შაბლონები | მზადაა | `docs/RESEARCH_STANDARD.md`, `research/TEMPLATE.md` |
| NOEMA-002 SignBase აუდიტი | შესრულებულია | ფიქსირებული SignBase snapshot, provenance და JSON შედეგები |
| NOEMA-003 კლიმატური ანალიზი | დრაფტი / გამეორებადი | სამი dataset-ის შედარება, HAC sensitivity, HadCRUT5 200-member ensemble და coverage consistency; ERA5 reconstruction validation gate ვერ გაიარა და საბოლოო დასკვნაში არ გამოიყენება |
| NOEMA-005 summation კვლევა | preliminary public brief + x86-64 და ARM64 real-thread გაგრძელება | ARM64 replication-ის შედეგები და პროტოკოლი PR #23-შია; 192/192 Neumaier-state შედეგი; დამოუკიდებელი გარე რეცენზია დარჩენილია |
| საჯარო კვლევითი კატალოგი | main: 1 preliminary, 0 published; PR #23: ჩანაწერის v1.4 განახლება | Git JSON კატალოგი, schema version 2; არსებული NOEMA-2026-005 ჩანაწერი განახლდება ARM64 შედეგებით; ახალი ID არ შექმნილა |
| კვლევის ბარათები და სტატუსები | კოდში დამატებულია | მთავარი გვერდი აჩვენებს preliminary და published სტატუსებს ცალ-ცალკე |
| ღია განხილვის რეჟიმი | კოდში დამატებულია | GitHub Issues feed, ახალი განხილვის ბმული და მომხმარებლის კომენტარები GitHub-ზე |
| CI და საიტის build | PR #23 head-ზე SUCCESS; main deployment ჯერ არ განახლებულა | [quality/site run 45752987825](https://github.com/maisuradzee/bibmom/actions/runs/45752987825) — PASS; [ARM64 replication run 45752987940](https://github.com/maisuradzee/bibmom/actions/runs/45752987940) — 4/4 runner/runtime PASS; PR ჯერ Draft-ია |
| GitHub Pages | DEPLOYED — წარმატება დადასტურებულია | [deployment run 45551962965](https://github.com/maisuradzee/bibmom/actions/runs/45551962965) წარმატებით დასრულდა main SHA `e84f2b9679c923c673319fc28fc6da5d1e021702`-ზე; [საიტი](https://maisuradzee.github.io/bibmom/) |
| Supabase მონაცემთა ბაზა | ჯერ არ შექმნილა | ამჟამად გამოიყენება Git-ით ვერსიაკონტროლირებადი JSON კატალოგი; ეს არ არის სერვერული/ტრანზაქციული DB |
| ვიზუალური AI ექსპერიმენტი | შეჩერებულია ნებართვამდე | SignBase-ის გამოსახულებებზე გამოყენების უფლება მოსაპოვებელია |

## ავტომატური კვლევითი ციკლი

- **მდგომარეობა:** დაგეგმილი გაშვებები აქტიურია; თითოეული გაშვება არის ცალკე სამუშაო ციკლი და არა უწყვეტი 24/7 მუშაობა.
- ყოველი ციკლი main-ის კვლევით/ტექნიკურ მდგომარეობას აღადგენს, ირჩევს ყველაზე ღირებულ დაუსრულებელ ამოცანას და ასრულებს რეალურ კოდს/ტესტს/აუდიტს.
- public საცავში branch-ები და PR-ებიც საჯაროა. ამიტომ `research/drafts/`-ში თავსდება მხოლოდ უსაფრთხო, საჯაროდ ხილვადი სინთეზური კვლევითი მასალა; პირადი/შეზღუდული დრაფტები არ აიტვირთება.
- კერძო არქივი ჯერ არ არსებობს. მის არქიტექტურაზე მუშაობა შეიძლება დოკუმენტაციით; ახალი Supabase პროექტი არ შექმნილა და სხვა პროექტის ბაზა არ გამოიყენება.
- თუ სანდო ახალი შედეგი არ მიიღება, უნდა შესრულდეს არსებული მასალის audit ან no-update; ხელოვნური კვლევა არ იქმნება.
- CI/deployment-ის ყველა მტკიცება უნდა უკავშირდებოდეს ზუსტად შემოწმებულ head SHA-სა და შესაბამის run-ს.

## გამოქვეყნების უსაფრთხოების ბლოკერი

GitHub საცავი public-ია. Pages build draft/review ფაილებს გამორიცხავს, მაგრამ branch/PR ფაილები GitHub-ზე მაინც საჯაროა. ამიტომ პირადი ან შეზღუდული კვლევითი მასალა აქ არ უნდა აიტვირთოს. NOEMA-005-ის მიმდინარე გაგრძელება იყენებს მხოლოდ სინთეზურ მონაცემებს, კოდს, საჯარო დოკუმენტაციასა და runtime metadata-ს. მომხმარებლის გვერდზე კვლევა ჩანს მხოლოდ `preliminary` სტატუსით და დამოუკიდებელი რეცენზიის არქონის გაფრთხილებით.

## მონაცემთა კატალოგი და მომხმარებლისთვის მიწოდება

- `data/research.json` არის Git-ით ვერსიაკონტროლირებადი საჯარო კატალოგი; `data/research.schema.json` განსაზღვრავს წყარო/საიტის ჩანაწერის სტრუქტურას (schema version 2 მოითხოვს წყაროს სრულ ციტირებას, ავტორებს, გამოცემის თარიღსა და წვდომის თარიღს).
- `preliminary` კვლევები ინახება `research/preprints/`-ში და მომხმარებლის გვერდზე მკაფიოდ არის მონიშნული როგორც წინასწარი, დამოუკიდებლად არარეცენზირებული.
- `published` კვლევები ინახება `research/published/`-ში მხოლოდ სრული კვლევითი/სარედაქციო საკონტროლო სიის შემდეგ.
- `draft` და `review` ჩანაწერები Pages არტეფაქტში არ ხვდება.
- კატალოგი ამჟამად სტატიკური და ვერსიაკონტროლირებადია. რეალური მომხმარებლის ანგარიშები, ნამდვილი database transactions, უშუალო კომენტარები და რეალურ დროში ძიება მოითხოვს NOEMA-ს ცალკე Supabase პროექტს. სხვა პროექტების ბაზა არ გამოიყენება.

## 2026-11-25 — რეალური CPU-thread benchmark

- კვლევის საწყისი branch: `research/noema005-real-thread-cpu-2026-11-25`; PR #21 verification branch: `research/noema005-final-verification-2026-11-25`; PR head: `00084792c6d3265b7b046e013ece362f76cf88f6`; squash merge commit: `e84f2b9679c923c673319fc28fc6da5d1e021702`.
- დაემატა რეალური `ThreadPoolExecutor` benchmark, native thread ID verification, GIL-state detection, CPU/wall timers, tracemalloc peak, protocol, tests და CI workflow.
- GitHub Actions run [45548551086](https://github.com/maisuradzee/bibmom/actions/runs/45548551086): CPython 3.14.4 GIL-enabled და 3.14.4t free-threaded; თითო runtime-ზე 48 configuration × 3 repetitions = 144 run; ორივე job SUCCESS.
- ყველა worker-ს განსხვავებული native thread ID ჰქონდა. Neumaier compensation-state merge: 48/48 სწორად დამრგვალებული configuration ორივე runtime-ზე; Neumaier scalar partial: 42/48; naive scalar: 0/48.
- CPU-time/wall-time >1.05: GIL-enabled 0/144; free-threaded 108/144 (2/4/8 worker-ების ყველა sample). მიუხედავად CPU concurrency-ისა, threaded wall-time serial baseline-ზე უკეთესი არ იყო; მაქსიმალური მედიანური speedup 0.777 და 0.803.
- შედეგების JSON: `data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json` და `data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json`; raw artifact SHA-256-ები ინახება ორივე ფაილში. სრული raw JSON artifacts ხელმისაწვდომია Actions run-ის artifact-ებში (30 დღე).
- `research/preprints/NOEMA-2026-005-floating-point-summation.md` და `data/research.json` main-ში განახლებულია; კატალოგში სტატუსი რჩება `preliminary`, schema v2 უცვლელია.
- free-threaded Python ოფიციალურად მხარდაჭერილია როგორც optional build Python 3.14-დან (PEP 779). ამ ციკლის pinned version იყო 3.14.4; 2026-11-25-ის უახლესი 3.14.10 და 3.15.2 არ შემოწმებულა.
- საბოლოო PR head `00084792c6d3265b7b046e013ece362f76cf88f6`-ზე [quality/site run 45551791989](https://github.com/maisuradzee/bibmom/actions/runs/45551791989) — SUCCESS, 176 ტესტი; [thread benchmark run 45551791998](https://github.com/maisuradzee/bibmom/actions/runs/45551791998) — ორივე runtime SUCCESS. squash merge commit `e84f2b9679c923c673319fc28fc6da5d1e021702`-ზე [main quality run 45551962844](https://github.com/maisuradzee/bibmom/actions/runs/45551962844) — SUCCESS, 176 ტესტი.
- [GitHub Pages deployment run 45551962965](https://github.com/maisuradzee/bibmom/actions/runs/45551962965) — SUCCESS; deployment payload-ის `pages_build_version` ემთხვევა merge SHA `e84f2b9679c923c673319fc28fc6da5d1e021702`-ს. Pages environment URL: https://maisuradzee.github.io/bibmom/.
- PR #19 კვლავ Draft-ია; CI run [45400018018](https://github.com/maisuradzee/bibmom/actions/runs/45400018018) ჩავარდა ერთ ტესტზე: `test_restore_rejects_non_self_contained_wal_mode_snapshot` — მოსალოდნელი `JobQueueError` არ იქნა გაშვებული. სხვა unit tests და შემდგომი reproduction/build ნაბიჯები skip გახდა.
- PR #5 (DB/RLS architecture) და PR #7 (cross-platform reproduction) კვლავ Draft-ებია და main-ის უფრო ძველ base SHA-ზე დგანან; არცერთი არ გაერთიანებულა.

## ბოლო ტექნიკური შემოწმება

- [CI run 45324726883](https://github.com/maisuradzee/bibmom/actions/runs/45324726883) — SUCCESS PR head `eafb239c526d8138a17b60c81c49f18b8d1e73db`-ზე: 87 Python test; research schema v2, source publication/access-date validation, all frozen result reproductions, 330-case parallel reduction simulation, benchmark smoke, site build და draft-exclusion boundary PASS.
- შუალედურ run `45323886583`-ში აღმოჩნდა, რომ `build_site.py` ჯერ მხოლოდ schema v1-ს იღებდა; validator/schema contract გასწორდა და მიმდინარე head-ზე build წარმატებით დასრულდა.
- [სრული NOEMA-005 benchmark run 45283854718](https://github.com/maisuradzee/bibmom/actions/runs/45283854718) — 12 format/size case და 66 method measurement.
- [წინა Pages deployment run 45169053640](https://github.com/maisuradzee/bibmom/actions/runs/45169053640) — ისტორიული deployment; მიმდინარე NOEMA-005 განახლება ცალკე დადასტურებულია run 45551962965-ით.

## კვლევები

- [NOEMA-2026-001](../research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნების პირველადი კვლევა და მეთოდოლოგიური გადახედვა.
- [NOEMA-2026-002](../research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი.
- [NOEMA-2026-003](../research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA/NASA/HadCRUT5 მონაცემთა ტენდენციების კვლევა.
- [NOEMA-2026-005 სამუშაო დრაფტი](../research/drafts/NOEMA-2026-005-floating-summation-order.md) — სრული ექსპერიმენტული ჟურნალი.
- [NOEMA-2026-005 წინასწარი მომხმარებლის ანგარიში](../research/preprints/NOEMA-2026-005-floating-point-summation.md) — public preliminary brief main-ზე; PR #3 merged.

## NOEMA-003 — HadCRUT5 ensemble trend analysis (2026-11-23)

- ოფიციალური Met Office HadCRUT.5.2.0.0 ensemble-series და summary-series CSV-ები წარმატებით ჩამოიტვირთა GitHub Actions run [45145461903](https://github.com/maisuradzee/bibmom/actions/runs/45145461903)-ში. წყაროთა არტეფაქტი: ID `14802644447`.
- ორივე CSV byte-for-byte შენახულია `data/noema-003/hadcrut5-5.2.0.0/`-ში. SHA-256, byte length, source URLs და retrieval provenance ინახება `source-manifest.json`-ში.
- პერიოდი: 1979–2025, 47 სრული წლიური მნიშვნელობა; 200 `Realization` სერია. 2026 წლის არასრული მნიშვნელობა გამორიცხულია.
- თითოეული realization-ის OLS slope დამოუკიდებლად გამოითვალა. Median = **0.2072945°C/ათწლეული**; empirical 2.5–97.5 percentile interval = **0.2012860–0.2129688°C/ათწლეული**; ყველა 200 slope დადებითია.
- Ensemble-mean-ის slope (0.2072271°C/ათწლეული) პრაქტიკულად ემთხვევა გამოქვეყნებული summary-series-ის slope-ს (0.2072271°C/ათწლეული); მაქსიმალური წლიური ანომალიის სხვაობა 3.01×10⁻⁸°C-ია.
- ფართობის საშუალო დაფარვა 1979–2025 პერიოდში 99.46%-ია; 2025 წელს 99.50%. დამატებითი coverage uncertainty აღწერილია ცალკე და slope პროცენტილებში არ გავრცელებულა, რადგან დროითი კოვარიაცია არ მოდელირებულა.
- შედეგები: `ensemble-trend-results-1979-2025.json`; გამოთვლის სკრიპტი: `scripts/analyze_hadcrut_ensemble.py`; ტესტები: `tests/test_analyze_hadcrut_ensemble.py`.
- ძირითადი CI workflow განახლებულია: ის ხელახლა ითვლის 200-member განაწილებას, ადარებს გაყინულ JSON-ს და ამოწმებს ორივე CSV-ის SHA-256-ს. HadCRUT download workflow-ში ასევე გასწორდა, რომ ორიგინალი ფაილის სახელები შეინარჩუნოს.
- ძველი HadCRUT.5.1.0.0 მესამე მხარის mirror-ით მიღებული შედეგები მხოლოდ pilot იყო; ისინი 5.2.0.0 საბოლოო შედეგებად აღარ გამოიყენება.
- საჯარო ინდექსი უცვლელია: **0 გამოქვეყნებული კვლევა**. NOEMA-003 კვლავ `draft`-ია.
- HadCRUT5-ის time-varying spatial mask ამოღებულია ოფიციალური `analysis.anomalies.ensemble_mean.nc` ფაილიდან. 1979–2025-ის 47 წლიური `Fraction of area represented` მნიშვნელობა ოფიციალურ CSV-ს ემთხვევა მაქსიმალური 3.45×10⁻⁸ სხვაობით. Masked grid-იდან აღდგენილი global annual mean summary-series-ს მაქსიმუმ 3.40×10⁻⁸°C სხვაობით ემთხვევა. `analysis.weights.nc` არის land–ocean blend weight და არა coverage mask.
- ოფიციალური annual coverage uncertainty-ის საშუალო 1σ არის 0.0046862566°C; 2025 წლის მაჩვენებელი 0.004196998°C. Summary-series-ის 95% საზღვრებიდან და 200-member წლიური SD-დან quadrature-ით აღდგენილ coverage 1σ სერიასთან RMSE არის 3.55×10⁻⁸°C, მაქსიმალური სხვაობა 1.399×10⁻⁷°C. ეს არის ორი ოფიციალური CSV-ის შიდა consistency check და არა ERA5-ის დამოუკიდებელი რეკონსტრუქცია.
- ოფიციალური წლიური coverage 1σ მნიშვნელობებიდან გამოთვლილი კოვარიაციისგან დამოუკიდებელი OLS slope-error RMS ზედა ზღვარი არის 0.0029338712°C/ათწლეული (Minkowski-ის უტოლობა); ეს არ არის ნდობის ინტერვალი.
- ERA5 coverage trajectory-ის პირველი center-bin მეთოდი validation-ს ვერ გასცდა: RMSE 0.000352°C, მაქსიმალური წლიური სხვაობა 0.000692°C, კორელაცია 0.971126. შემდეგი conservative cell-overlap regridding-ით სრულად შესრულებულმა run-ებმა [45165452937](https://github.com/maisuradzee/bibmom/actions/runs/45165452937) და [45167639382](https://github.com/maisuradzee/bibmom/actions/runs/45167639382) პრაქტიკულად იგივე აცდენა აჩვენა: RMSE 0.0003516123°C, მაქსიმალური სხვაობა 0.0006968631°C (2012), კორელაცია 0.971882; RMSE-ის ზღვარი 0.000500°C იყო. ამიტომ grid-cell საზღვრის დამუშავება ძირითადი მიზეზი არ აღმოჩნდა და ERA5-ით აღდგენილი coverage-error trajectory დასკვნაში არ გამოიყენება.
- ბოლო სრულმა workflow-მ 40-ივე საცნობარო წლის ჩამოტვირთვა, დამუშავება და 5° anomaly snapshot-ის შენახვა წარმატებით დაასრულა; ჩავარდა მხოლოდ ოფიციალურ წლიურ coverage sigma-სთან ვალიდაციის gate. სრული 5° anomaly snapshot და 40 საწყისი ფაილის SHA-256 სია დაცულია Actions artifact-ში [run 45167639382](https://github.com/maisuradzee/bibmom/actions/runs/45167639382), artifact ID 14815616537. თავად 40 ორიგინალი NetCDF ფაილი საცავში არ არის დაკომიტებული.
- HadCRUT5-ის ოფიციალური annual coverage sigma ცალკე დოკუმენტირებულია; interannual covariance აქ არ არის აღდგენილი. ამიტომ არ ვაერთიანებთ coverage RMS ზედა ზღვარს 200-member percentile interval-თან ერთ საერთო 95%-იან დიაპაზონად.
- დარჩენილია: ERA5-ის ორიგინალი 31 კმ-იანი reference realization-ის ან იმავე CDS source stream-ის იდენტური ასლის მიღება, provenance-ის გადამოწმება და დამოუკიდებელი მეთოდოლოგიური რეცენზია.


## NOEMA-005 — summation accuracy across binary32, binary64, decimal64 and decimal128 (2026-11-24)

- ძირითადი კვლევის სტატუსი: `preliminary` main-ზე (PR #3 merged); სრული კვლევითი ჟურნალი რჩება `research/drafts/NOEMA-2026-005-floating-summation-order.md`-ში. მომხმარებლისთვის მომზადებული მოკლე ანგარიში მოთავსებულია `research/preprints/NOEMA-2026-005-floating-point-summation.md`-ში და კატალოგში ჩანს მხოლოდ `preliminary` სტატუსით.
- მიმდინარე გაგრძელების branch: `research/noema005-real-thread-cpu-2026-11-25`, დაფუძნებულია main SHA `f777eb530443e5be33ce6d28591eeb75e2df0fd0`-ზე. ძველი stale branch main-ში არ გაერთიანებულა.
- კვლევის მოცულობა: 4 ფორმატი; თითოეულში 2 synthetic stress case, სულ 48 input ordering. Binary32/binary64-ში თითო 6 method; decimal64/decimal128-ში თითო 5 method.
- Binary32-ის oracle პირდაპირი rational-to-binary32 round-to-nearest ties-to-even quantizer-ია; native binary32 მეთოდებში ყოველი შუალედური არითმეტიკული ოპერაცია binary32-ში მრგვალდება. `math.fsum_then_round_binary32` ცალკე wider-precision comparison path-ია.
- Decimal64/decimal128 გამოიყენებს Python `decimal.Context` arithmetic emulation-ს: precision 16/34, Emin/Emax −383/+384 და −6143/+6144, Etiny −398/−6176, clamp=1, ROUND_HALF_EVEN. ეს არ არის decimal interchange BID/DPD byte-level implementation.
- ზუსტი integer accumulator-ები იყენებს binary32-ის (2^{-149}), binary64-ის (2^{-1074}) grid-ს; decimal-ში შეყვანებში არსებულ უმცირეს exponent-ს საერთო quantum-ად. Final rounding შესაბამისი Fraction/Context conversion-ით სრულდება; ეს დამოუკიდებელი hardware rounding implementation არ არის.
- NOEMA-005 summation suite შეიცავს 20 unit test-ს; benchmark suite — 2 test-ს. სრული საცავის CI suite — **74 test**.
- უახლესი სრული CI: [run 45283388439](https://github.com/maisuradzee/bibmom/actions/runs/45283388439) — SUCCESS. 74 ტესტი; NOEMA-003 trend/cross-dataset/HadCRUT5 200-member შედეგები და source SHA-256; NOEMA-005-ის ოთხივე ფორმატის frozen JSON reproduction; benchmark smoke; draft/index validation; site build; publication boundary; SignBase audit და HTML checks — PASS.
- Benchmark harness: `scripts/benchmark_noema005_summation.py`; protocol: `data/noema-005/benchmark-protocol.json`; სრული პროფილის შეჯამება: `data/noema-005/benchmark-full-profile-summary-2026-11-24.json`. CI smoke profile-მა შეამოწმა 8 format/size შემთხვევა და 44 method measurement.
- სრული benchmark run [45283854718](https://github.com/maisuradzee/bibmom/actions/runs/45283854718) წარმატებულია: 12 format/size შემთხვევა, 66 method measurement, sizes 1,024 / 8,192 / 65,536, 2 warmup, 7 repetitions, seed 20261124. გარემო: CPython 3.14.4, Linux x86-64 (AWS runner). Original JSON report SHA-256: `cb902442026cfe4b74a506d01c568efdb6e009a27f38014ce0548c6bf36f4ce9`; artifact ID `14870647841`, archive SHA-256 `0a6977db72fbc5a64bd7609b6d0d78c18c59276138e402928f06ccf1e2acef28`.
- 65,536 input-ზე binary64 integer accumulator-ს ჰქონდა 60.835 ms median და 4,384 bytes peak traced memory; decimal64 integer accumulator-ს — 37.376 ms და 6,853,728 bytes; decimal128-ს — 37.210 ms და იგივე peak. ეს შედეგები ასახავს ამ კონკრეტულ Python reference implementation-ს და არა ალგორითმის აბსტრაქტულ ქვედა ზღვარს.
- Binary32-ის native emulation ახორციელებს Python-level rounding-ს ყოველ ოპერაციაზე; ამიტომ მისი დროები hardware binary32-ის სიჩქარეს არ ასახავს. `math_fsum_then_round_binary32` wider precision comparison path-ია.
- `tracemalloc` ზომავს Python-managed traced allocations-ს, არა სრულ RSS-ს და არა ყველა native allocation-ს. ერთი runner-ის შედეგები აღწერითია და უნივერსალურ performance ranking-ს არ ამტკიცებს.
- შემდეგი ნაბიჯებია: სრული პროფილის განმეორება სხვა Python ვერსიაზე/არქიტექტურაზე და რამდენიმე run-ზე; ზუსტი integer accumulator-ის ოპტიმიზაცია; parallel reduction tree-ების კვლევა; რეალური მონაცემთა ნაკრების შერჩევა და დამოუკიდებელი მეთოდოლოგიური რეცენზია.
- კვლევის ყველა ექსპერიმენტი synthetic stress case-ია; real workload error rate ან უნივერსალური method ranking არ დასტურდება. საჭიროა სხვა Python ვერსიაზე/არქიტექტურაზე გამეორება, parallel reduction tree-ების შეფასება, რეალური მონაცემთა ნაკრების კვლევა და დამოუკიდებელი მეთოდოლოგიური რეცენზია.
- main-ის კატალოგში 1 preliminary და 0 published item-ია. PR #3 merged არის 2026-11-24; მისი post-merge Pages deployment ამ ციკლში დამოუკიდებლად არ გადამოწმებულა.


## 2026-11-26 — NOEMA-005 ARM64 replication

- **საკვლევი branch/PR:** `research/noema005-arm64-replication-2026-11-26`, [PR #23](https://github.com/maisuradzee/bibmom/pull/23).
- **ARM64 benchmark-ის შემოწმებული head:** `4fe358edd532d1861544951682e9125f67a4e156`.
- **ახალი ექსპერიმენტი:** Ubuntu 24.04 ARM64 და macOS 15 ARM64; თითოეულზე CPython 3.14.4 GIL-enabled და free-threaded; 48 configuration × 3 repetition თითო runtime-ზე.
- **მიგნება:** Neumaier compensation-state reduction 192/192 სწორად დამრგვალებული შედეგით; scalar Neumaier 168/192; naive scalar 0/192. Free-threaded რეჟიმში CPU/wall ratio >1.05 დაფიქსირდა 208/288 sample-ში, GIL-enabled რეჟიმში 2/288-ში. ეს CPU-ის პარალელურ გამოყენებას ასახავს და არა wall-time speedup-ს.
- **შედეგების ფაილი:** `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`; raw report SHA-256 და Actions artifact digest შენახულია.
- **CI:** [quality/site #45752987825](https://github.com/maisuradzee/bibmom/actions/runs/45752987825) PASS; [ARM64 #45752987940](https://github.com/maisuradzee/bibmom/actions/runs/45752987940) ოთხივე job PASS.
- **deployment:** PR ჯერ Draft-ია; Pages deployment არ გაშვებულა ამ PR-ის ცვლილებებისთვის.
- **შემდეგი პრიორიტეტი:** Windows ARM64/სხვა არქიტექტურის გამეორება, native C/OpenMP შედარება, 20+ repetition და RSS/native memory გაზომვა.


## 2026-11-26 — NOEMA-005 ARM64 დამოუკიდებელი განმეორების აუდიტი

- მეორე ARM64 benchmark batch შესრულდა PR #23-ის head `8bf2268b3179260976cea8f9260b52b182937814`-ზე; [ARM64 workflow run 45754595646](https://github.com/maisuradzee/bibmom/actions/runs/45754595646), [quality/site run 45754595614](https://github.com/maisuradzee/bibmom/actions/runs/45754595614) და [x86-64 threaded benchmark run 45754595595](https://github.com/maisuradzee/bibmom/actions/runs/45754595595) — სამივე SUCCESS ზუსტად ამ head-ზე.
- ოთხივე ARM64 raw report ZIP ჩამოიტვირთა და შემოწმდა. report SHA-256, archive SHA-256, byte length, artifact ID, გარემო და გაზომვები ჩაიწერა `data/noema-005/arm64-repeat-validation-2026-11-26.json`-ში.
- მეორე batch: 4 runtime cell × 48 configuration × 3 repetition = 192 configuration / 576 measured runs. Neumaier state: 192/192; scalar Neumaier: 168/192; naive scalar: 0/192.
- პირველი batch-ის შედარება: Neumaier-state სიზუსტე ორივე batch-ში 192/192; ორ batch-ზე ჯამურად 384/384. CPU/wall >1.05 threshold-ის რაოდენობა იცვლებოდა: free-threaded 208/288 → 211/288; GIL-enabled 2/288 → 1/288. ეს ადასტურებს, რომ threshold-count run-sensitive დიაგნოსტიკაა და არა სტაბილური performance endpoint.
- მეორე batch-ის ოთხივე runtime-cell Neumaier-state median speedup 1.0-ზე ნაკლები იყო (0.737, 0.704, 0.896, 0.676). ზოგადი wall-time აჩქარება არ დადასტურდა.
- ოფიციალური Python 3.14 free-threading HOWTO ადასტურებს, რომ free-threaded build-ს შეუძლია CPU ბირთვებზე thread-ების პარალელური შესრულება, მაგრამ ყველა workload ავტომატურად არ ჩქარდება და build-ს აქვს single-thread/memory overhead. GitHub runner-ის მიმდინარე reference ადასტურებს ubuntu-24.04-arm-ის 4 CPU-სა და macos-15 ARM64 M1-ის 3 CPU-ს.
- ARM64 workflow-ის path filter შევიწროვდა: კატალოგის, preprint-ის, შედეგების არქივისა და summary-test-ის მხოლოდ დოკუმენტური ცვლილება აღარ იწყებს ძვირადღირებულ benchmark-ს; workflow, benchmark code, validator, core tests ან replication protocol-ის ცვლილება კვლავ იწყებს.
- კვლევის სტატუსი რჩება `preliminary`; დამოუკიდებელი გარე რეცენზია არ ჩატარებულა. PR-ის merge და Pages deployment ამ ეტაპზე ჯერ არ არის დადასტურებული.


## 2026-11-26 — NOEMA-005 ARM64 მესამე გამეორება

- მესამე დამოუკიდებელი ARM64 benchmark: [run 45756074975](https://github.com/maisuradzee/bibmom/actions/runs/45756074975) — ოთხივე Ubuntu/macOS × GIL/free-threaded job SUCCESS; ზუსტი benchmark head `a77c0d5b659c1ad9e73e15ed718b2baf34a8839a`.
- იმავე head-ზე [quality/site run 45756074962](https://github.com/maisuradzee/bibmom/actions/runs/45756074962) და [x86-64 CPU-thread benchmark run 45756074982](https://github.com/maisuradzee/bibmom/actions/runs/45756074982) SUCCESS.
- ოთხივე მესამე-batch raw artifact ჩამოიტვირთა და SHA-256-ით შემოწმდა. Artifact ID, archive digest, report digest, bytes და runner metadata დაემატა `data/noema-005/arm64-repeat-validation-2026-11-26.json`-ს.
- სამივე ARM64 batch-ში Neumaier-state ზუსტი შედეგი შენარჩუნდა: **576/576**; scalar Neumaier **504/576**; naive scalar **0/576**.
- Timing შედეგები არასტაბილურია: CPU/wall >1.05 threshold free-threaded რეჟიმში 208/288 → 211/288 → 214/288; GIL-enabled 2/288 → 1/288 → 0/288. მესამე batch-ში macOS free-threaded state-method median speedup 1.003 იყო; დანარჩენი სამი runtime-cell median 1.0-ზე ნაკლები. სამი repetition-ით ეს არ არის სანდო აჩქარების მტკიცებულება.
- კვლევის სტატუსი რჩება `preliminary`; გარე რეცენზია არ ჩატარებულა. PR #23-ის merge/deployment სტატუსი უნდა დადასტურდეს ცალკე.


## 2026-11-26 — PR #23 merge და Pages deployment

- [PR #23](https://github.com/maisuradzee/bibmom/pull/23) წარმატებით გაერთიანდა squash-ით. Merge commit: `4d950bdd154fc56ca665802794b0ba1d5ff15e25`; main-ის SHA ამ merge-ის შემდეგ ემთხვევა ამ commit-ს.
- [Main quality run #45756851261](https://github.com/maisuradzee/bibmom/actions/runs/45756851261) — SUCCESS.
- [Pages deployment #45756851227](https://github.com/maisuradzee/bibmom/actions/runs/45756851227) — build და deploy jobs SUCCESS; GitHub Pages deployment დასრულებულია. საჯარო მისამართი: https://maisuradzee.github.io/bibmom/.
- PR-ის final-head ARM64 verification: [run 45756479611](https://github.com/maisuradzee/bibmom/actions/runs/45756479611) — ოთხივე runner/runtime job SUCCESS; Neumaier-state 192/192.
- მეოთხე batch-ის ოთხივე raw artifact ჩამოიტვირთა და SHA-256-ით შემოწმდა. Final-head report/archive hash-ები, runner metadata და შედეგები არქივდება `data/noema-005/arm64-repeat-validation-2026-11-26.json`-ში.
- ოთხი ARM64 batch-ის კუმულაციური სიზუსტე: Neumaier-state **768/768**, scalar Neumaier **672/768**, naive scalar **0/768**. Timing-ის მცირე განსხვავებები არ იძლევა ზოგადი speedup-ის დასკვნის საფუძველს.
- README-ში დაზუსტდა GitHub Actions PR path-filter-ის სემანტიკა: ცალკე docs-only PR არ ააქტიურებს ARM64 matrix-ს, თუმცა უკვე benchmark-ფაილების შემცველ PR-ში შემდგომი synchronize შეიძლება ხელახლა აამუშაოს workflow, რადგან PR path filter მთელ PR diff-ს ამოწმებს.
- კვლევა რჩება `preliminary`; დამოუკიდებელი გარე რეცენზია არ ჩატარებულა. `published` სტატუსი არ მინიჭებულა.
