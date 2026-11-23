# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-24 (ავტომატიზაცია, საჯარო კვლევითი კატალოგი და განხილვის რეჟიმი)
- **საცავი:** [maisuradzee/bibmom](https://github.com/maisuradzee/bibmom)
- **ძირითადი branch:** `main` — უცვლელია
- **სამუშაო branch:** `research/noema-2026-005-mainline-2026-11-24`
- **კვლევითი PR:** [#3 — Draft: NOEMA-2026-005](https://github.com/maisuradzee/bibmom/pull/3) — ღიაა, draft-ია და ჯერ არ გაერთიანებულა.

## მიმდინარე სტატუსი

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| კვლევის სტანდარტი და შაბლონები | მზადაა | `docs/RESEARCH_STANDARD.md`, `research/TEMPLATE.md` |
| NOEMA-002 SignBase აუდიტი | შესრულებულია | ფიქსირებული SignBase snapshot, provenance და JSON შედეგები |
| NOEMA-003 კლიმატური ანალიზი | დრაფტი / გამეორებადი | სამი dataset-ის შედარება, HAC sensitivity, HadCRUT5 200-member ensemble და coverage consistency; ERA5 reconstruction validation gate ვერ გაიარა და საბოლოო დასკვნაში არ გამოიყენება |
| NOEMA-005 summation კვლევა | review + public preliminary brief | სრული ექსპერიმენტი და benchmark დრაფტშია; მომხმარებლის მოკლე ანგარიში გამოყოფილია `research/preprints/`-ში |
| საჯარო კვლევითი კატალოგი | 1 preliminary, 0 published — სამუშაო PR branch-ზე | `data/research.json`, `data/research.schema.json`; Pages build ქმნის 1 preliminary HTML გვერდს |
| კვლევის ბარათები და სტატუსები | კოდში დამატებულია | მთავარი გვერდი აჩვენებს preliminary და published სტატუსებს ცალ-ცალკე |
| ღია განხილვის რეჟიმი | კოდში დამატებულია | GitHub Issues feed, ახალი განხილვის ბმული და მომხმარებლის კომენტარები GitHub-ზე |
| CI და საიტის build | PASS — მიმდინარე ცვლილებების საწყისი შემოწმება | [CI run 45287511224](https://github.com/maisuradzee/bibmom/actions/runs/45287511224): build report — 0 published, 1 preliminary; ცვლილებების ბოლო JSON Schema შესწორება დამატებით CI გადამოწმებას ელოდება |
| GitHub Pages | წინა deployment წარმატებული | [deployment run 45169053640](https://github.com/maisuradzee/bibmom/actions/runs/45169053640); ამ PR-ის ახალი branch ცვლილებები ჯერ არ არის გამოქვეყნებული |
| Supabase მონაცემთა ბაზა | ჯერ არ შექმნილა | ამჟამად გამოიყენება Git-ით ვერსიაკონტროლირებადი JSON კატალოგი; ეს არ არის სერვერული/ტრანზაქციული DB |
| ვიზუალური AI ექსპერიმენტი | შეჩერებულია ნებართვამდე | SignBase-ის გამოსახულებებზე გამოყენების უფლება მოსაპოვებელია |

## ავტომატური კვლევითი ციკლი

- **აქტიურია:** `NOEMA ყოველდღიური კვლევა`.
- **სიხშირე:** ყოველდღე, 08:00, `Asia/Tbilisi`.
- **შემდეგი დაგეგმილი გაშვება:** 2026-11-24, 08:00 (თბილისის დრო).
- ყოველ გაშვებაზე სისტემა აღადგენს საცავის/კვლევების კონტექსტს, აგრძელებს პრიორიტეტულ მიმდინარე სამუშაოს, ამოწმებს წყაროებსა და შედეგებს, აფიქსირებს კოდს/მონაცემებს, აახლებს PR-ს და კატალოგს მხოლოდ იმ შემთხვევაში, თუ წინასწარი შედეგის საჯარო ჩვენების კრიტერიუმები დაკმაყოფილებულია.
- თუ სანდო ახალი შედეგი არ მიიღება, უნდა შესრულდეს არსებული მასალის აუდიტი ან დაფიქსირდეს no-update; ხელოვნური კვლევა არ იქმნება.
- ეს არის **დაგეგმილი ყოველდღიური გაშვება და არა უწყვეტი 24/7 სამუშაო**. თითოეული ციკლი დამოუკიდებლად უნდა დასრულდეს; ავტომატიზაცია არ ნიშნავს, რომ ყველა შემდგომი ოპერაცია უპირობოდ წარმატებული იქნება. GitHub კავშირის/უფლების/CI-ის შეფერხება უნდა დაფიქსირდეს და არა დაიმალოს.

## მონაცემთა კატალოგი და მომხმარებლისთვის მიწოდება

- `data/research.json` არის Git-ით ვერსიაკონტროლირებადი საჯარო კატალოგი; `data/research.schema.json` განსაზღვრავს წყარო/საიტის ჩანაწერის სტრუქტურას.
- `preliminary` კვლევები ინახება `research/preprints/`-ში და მომხმარებლის გვერდზე მკაფიოდ არის მონიშნული როგორც წინასწარი, დამოუკიდებლად არარეცენზირებული.
- `published` კვლევები ინახება `research/published/`-ში მხოლოდ სრული კვლევითი/სარედაქციო საკონტროლო სიის შემდეგ.
- `draft` და `review` ჩანაწერები Pages არტეფაქტში არ ხვდება.
- კატალოგი ამჟამად სტატიკური და ვერსიაკონტროლირებადია. რეალური მომხმარებლის ანგარიშები, ნამდვილი database transactions, უშუალო კომენტარები და რეალურ დროში ძიება მოითხოვს NOEMA-ს ცალკე Supabase პროექტს. სხვა პროექტების ბაზა არ გამოიყენება.

## ბოლო ტექნიკური შემოწმება

- [CI run 45287511224](https://github.com/maisuradzee/bibmom/actions/runs/45287511224) — SUCCESS: ყველა სამუშაო ნაბიჯი დასრულდა წარმატებით; საიტის build-მა 1 preliminary სტატია შექმნა, ხოლო draft ფაილები Pages არტეფაქტში არ მოხვდა.
- [სრული NOEMA-005 benchmark run 45283854718](https://github.com/maisuradzee/bibmom/actions/runs/45283854718) — 12 format/size case და 66 method measurement.
- [წინა Pages deployment run 45169053640](https://github.com/maisuradzee/bibmom/actions/runs/45169053640) — build და deploy წარმატებით დასრულდა. ეს არ ნიშნავს, რომ მიმდინარე PR-ის ცვლილებები უკვე საჯარო გვერდზეა.

## კვლევები

- [NOEMA-2026-001](../research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნების პირველადი კვლევა და მეთოდოლოგიური გადახედვა.
- [NOEMA-2026-002](../research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი.
- [NOEMA-2026-003](../research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA/NASA/HadCRUT5 მონაცემთა ტენდენციების კვლევა.
- [NOEMA-2026-005 სამუშაო დრაფტი](../research/drafts/NOEMA-2026-005-floating-summation-order.md) — სრული ექსპერიმენტული ჟურნალი.
- [NOEMA-2026-005 წინასწარი მომხმარებლის ანგარიში](../research/preprints/NOEMA-2026-005-floating-point-summation.md) — public preliminary brief სამუშაო branch-ზე.

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

- ძირითადი კვლევის სტატუსი: `review`; სრული კვლევითი ჟურნალი რჩება `research/drafts/NOEMA-2026-005-floating-summation-order.md`-ში. მომხმარებლისთვის მომზადებული მოკლე ანგარიში მოთავსებულია `research/preprints/NOEMA-2026-005-floating-point-summation.md`-ში და კატალოგში ჩანს მხოლოდ `preliminary` სტატუსით.
- სამუშაო branch: `research/noema-2026-005-mainline-2026-11-24`, მიმდინარე `main`-ზე დაფუძნებული. ძველი branch, რომელიც main-ს 45 commit-ით ჩამორჩებოდა, არ გაერთიანებულა.
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
- კატალოგში PR-ის ფილიალში 1 preliminary და 0 published item-ია. PR #3 კვლავ draft-ია; merge არ მომხდარა. საჯარო Pages deployment ამ branch-ის ცვლილებებს ჯერ არ შეიცავს.
