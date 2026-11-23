# NOEMA — მიმდინარე პროექტის მდგომარეობა

- **განახლდა:** 2026-11-24 (NOEMA-005 კვლევითი ციკლის განახლება)
- **საცავი:** [maisuradzee/bibmom](https://github.com/maisuradzee/bibmom)
- **ძირითადი branch:** `main`

## სტატუსი

| კომპონენტი | მდგომარეობა | მტკიცებულება |
|---|---|---|
| GitHub საცავი და კოდის შენახვა | მზადაა | მთავარი branch და ფაილები ხელმისაწვდომია |
| კვლევის სტანდარტი და შაბლონები | მზადაა | `docs/RESEARCH_STANDARD.md`, `research/TEMPLATE.md` |
| მონაცემთა აუდიტი NOEMA-002 | შესრულებულია | ფიქსირებული SignBase snapshot და JSON შედეგი |
| NOEMA-003 ტემპერატურის ტენდენციის ანალიზი | დრაფტი / გამეორებადი; HadCRUT5 ensemble და ოფიციალური coverage კომპონენტის cross-check შესრულებულია | სამი პროდუქტის snapshot, OLS/Theil–Sen და HAC 1–6; 200-member HadCRUT5 slope distribution; ოფიციალური coverage 1σ სერია summary-series-ის 95% საზღვრებთან/ensemble SD-თან RMSE 3.55×10⁻⁸°C-ით ემთხვევა; coverage slope-error RMS ზედა ზღვარი 0.0029339°C/ათწლეული; APCC ERA5 reconstruction ორჯერ სრულად გამოითვალა, მაგრამ ორივე გაშვებამ RMS gate ვერ გაიარა და მისი trajectory არ გამოიყენება |
| Python ტესტები და მონაცემთა რეპროდუქცია | PASS | [CI run 45169053632](https://github.com/maisuradzee/bibmom/actions/runs/45169053632) წარმატებულია; **52 Python unit test**, სამი ტემპერატურული შედეგის reproducibility, HadCRUT source SHA-256 და 200-member frozen JSON შემოწმდა |
| სტატიკური საიტის build | წარმატებულია | CI და Pages build job |
| GitHub Pages deployment | PASS | [უახლესი deployment — run 45169053640](https://github.com/maisuradzee/bibmom/actions/runs/45169053640) წარმატებით დასრულდა |
| საჯარო კვლევების ინდექსი | ცარიელია განზრახ | კვლევები ჯერ `draft/review` სტატუსშია |
| ვიზუალური AI ექსპერიმენტი | დაწყებამდეა | SignBase-ის გამოსახულებებზე გამოყენების ნებართვა მოსაპოვებელია |
| Supabase | გადადებულია | ამ ეტაპზე სტატიკურ JSON ინდექსს ვიყენებთ |

## ბოლო ტექნიკური შემოწმება

- [CI run 45169053632](https://github.com/maisuradzee/bibmom/actions/runs/45169053632) — წარმატებული; **52 Python unit test** გაიარა. NOAA trend analysis, cross-dataset/HAC comparison და HadCRUT5 200-member analysis ხელახლა გამოითვალა; frozen JSON და წყაროების SHA-256 დაემთხვა; public build-ის დრაფტების გამორიცხვის კონტროლიც წარმატებულია.
- [Pages deployment run 45169053640](https://github.com/maisuradzee/bibmom/actions/runs/45169053640) — build და deploy წარმატებულია.

NOEMA-003-ის cross-dataset და HAC robustness განახლება თავდაპირველად დადასტურდა commit-ზე `653820747cc42f1074306cb7f5081bc956cc3116`:

- [CI run 45137630834](https://github.com/maisuradzee/bibmom/actions/runs/45137630834) — წარმატებული; **34 Python unit test** გაიარა.
- [Pages deployment run 45137630882](https://github.com/maisuradzee/bibmom/actions/runs/45137630882) — build და deploy წარმატებულია.
- სამი წყაროს snapshot-ის SHA-256 ისევ ემთხვევა ფიქსირებულ manifest-ს.
- 1979–2025 ფანჯარაში OLS დახრილობები: NASA GISTEMP 0.20556, HadCRUT5 0.20723, NOAA GlobalTemp 0.19848 °C/ათწლეულში.
- სამივე პროდუქტის OLS დახრილობა დადებითია; მაქსიმალურ-მინიმალური განსხვავება დაახლოებით 4.41%-ია.
- HAC Bartlett lag 1–6 sensitivity ყველა პროდუქტზე ხელახლა გამოითვალა; ყველა ლაგზე მიახლოებითი 95%-იანი ქვედა ზღვარი დადებითია.
- HadCRUT5 v5.2.0.0-ის 200 realization ცალკე გაანალიზდა 1979–2025 წლების 47-წლიან ფანჯარაში: median slope 0.2072945°C/ათწლეული; 2.5–97.5 პროცენტილი 0.2012860–0.2129688°C/ათწლეული; 200/200 დადებითი. ეს არის ensemble-member trend distribution და არა frequentist confidence interval. Coverage uncertainty ცალკეა დაფიქსირებული და trend percentiles-ში არ არის გავრცელებული.
- CI ადასტურებს ორივე გამოთვლითი სკრიპტის შედეგების JSON-თან შინაარსობრივ თანხვედრას.
- დრაფტების ვალიდაციამ დაადასტურა 4 draft ფაილი; საჯარო ინდექსი კვლავ შეიცავს 0 გამოქვეყნებულ კვლევას. საიტის build წარმატებულია და დრაფტები Pages არტეფაქტში არ შედის.

Pages deployment workflow ავტომატურად იშვება `main` branch-ზე push-ისას.

## კვლევები

- [NOEMA-2026-001](../research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნების პირველადი კვლევა, მეთოდოლოგიური გადახედვით.
- [NOEMA-2026-002](../research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი.
- [NOEMA-2026-003](../research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA GlobalTemp v6.1.0 მონაცემში დათბობის ხაზოვანი ტენდენციის საწყისი წლის მგრძნობელობა.
- [NOEMA-002 blind coding protocol](../research/protocols/NOEMA-002-blind-coding-protocol.md) — მომავალი ექსპერტულ-ალგორითმული შედარების პროტოკოლი.

ყველა კვლევა ამ ეტაპზე დრაფტად რჩება. საჯარო Pages ინდექსში მათი დამატება არ მომხდარა. NOEMA-003-ის cross-dataset შედარება, HAC lag robustness და HadCRUT5-ის 200-member trend distribution შესრულებულია; coverage uncertainty-ის სრული trend-level მოდელირება და დამოუკიდებელი სარედაქციო რეცენზია ჯერ დარჩენილია.

## ავტომატიზაცია

აქტიურია `NOEMA კვლევითი ციკლი` — ყოველდღიური გაშვება 09:00 საათზე, `Asia/Tbilisi` დროის სარტყელში. ინსტრუქცია განახლებულია ისე, რომ ყოველი ციკლი ჯერ არსებულ კვლევებს ამოწმებს, დუბლირებას ერიდება და GitHub write-access-ის არსებობისას ახალ კვლევას `research/drafts/`-ში ინახავს და ხელახლა ამოწმებს. ავტომატიზაცია არ აქვეყნებს კვლევებს და არ ცვლის საჯარო ინდექსს.

**მნიშვნელოვანი:** დაგეგმილი კვლევითი ციკლი და GitHub Actions CI ორი სხვადასხვა მექანიზმია. CI კოდს ამოწმებს; კვლევითი ავტომატიზაცია ახალ კვლევით მასალას ამზადებს. მათი სრული უწყვეტი ინტეგრაცია ცალკე სამუშაო ეტაპია.

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


## NOEMA-005 — binary64 summation order (2026-11-24)

- სტატუსი: `review`; კვლევა კვლავ `research/drafts/`-შია და საჯარო ინდექსში არ არის დამატებული.
- სამუშაო განახლება დაფუძნებულია მიმდინარე `main` branch-ზე; ძველი კვლევითი branch ჩამორჩებოდა მთავარს და მისი პირდაპირი გაერთიანება არ გამოიყენება.
- ორი კონტროლირებული synthetic შემთხვევა: cancellation triplets (3,000 წევრი, 7 დალაგება) და half-ULP დაგროვება (1,026 წევრი, 5 დალაგება); სულ 12 დალაგება და ექვსი მეთოდი.
- შედარებულია naive left-to-right, adjacent pairwise, Kahan, Neumaier, `math.fsum` და 2⁻¹⁰⁷⁴ ერთეულებზე დაფუძნებული ზუსტი integer superaccumulator.
- ეტალონი არის წარმოდგენილი binary64 შეყვანების ზუსტი Fraction ჯამი. Integer accumulator-ის დაგროვება ცალკე ხდება arbitrary-precision integer-ით; საბოლოო binary64 კონვერტაცია იყენებს Python Fraction-ის rational rounding-ს და ამიტომ სრულად დამოუკიდებელ rounding implementation-ად არ არის წარმოდგენილი.
- ახალი CI კონტროლი ხელახლა აგებს კვლევის JSON შედეგს და ადარებს გაყინულ snapshot-ს; გარემოს ვერსიის/პლატფორმის მეტამონაცემები შედარებისგან გამორიცხულია, მაგრამ არტეფაქტში რჩება.
- GitHub Actions CI წარმატებით დასრულდა: [run 45280161907](https://github.com/maisuradzee/bibmom/actions/runs/45280161907), 62 Python unit test; NOEMA-003-ის გამოთვლები, HadCRUT5-ის წყაროთა SHA-256, NOEMA-005-ის frozen JSON, site build, draft-publication boundary, SignBase აუდიტი და HTML შემოწმება წარმატებულია. კვლევა არ ამტკიცებს მეთოდის უნივერსალურ უპირატესობას და არ იყენებს რეალური წარმოების workload-ის error-rate შეფასებას.
- Binary32 გაფართოება დაემატა: 2 დამატებითი stress test, 12 order, 6 method; პირდაპირი Fraction-to-binary32 ties-to-even reference და 4 ახალი unit test. CI შედეგი ამ გაფართოებისთვის ჯერ არ არის დადასტურებული.
- შემდეგი ეტაპები: decimal64/decimal128, ხარჯის (runtime/memory) გაზომვა, პარალელური reduction tree-ების კვლევა და დამოუკიდებელი რეცენზია. PR #2 კვლავ draft-ია; merge და საჯარო გამოქვეყნება არ მომხდარა.
