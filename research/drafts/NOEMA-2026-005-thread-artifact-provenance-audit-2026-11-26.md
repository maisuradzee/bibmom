# NOEMA-005 — დამოუკიდებელი CPU-thread artifact provenance audit

- **ID:** NOEMA-2026-005-REAL-THREADS-ARTIFACT-AUDIT-001
- **თარიღი:** 2026-11-26
- **სტატუსი:** draft / provenance verification
- **წყარო workflow:** [45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895)
- **წყარო commit:** `b4df9c9c1f7d2142c8d48e487a73977be70b9966`

## მიზანი

გადამოწმდეს, ემთხვევა თუ არა NOEMA-005-ის frozen CPU-thread summary-ში ჩაწერილი GitHub Actions artifact SHA-256-ები რეალურად ჩამოტვირთული ZIP-ების bytes-ს და ხელახლა მიიღება თუ არა ძირითადი accuracy/CPU-time/wall-time აგრეგატები თითოეული JSON report-იდან.

ეს არის **artifact integrity და aggregate reproduction audit**; იგი არ იმეორებს benchmark-ის შესრულებას.

## მეთოდოლოგია

1. GitHub Actions workflow 45840219895-დან ჩამოიტვირთა ორი ორიგინალური artifact ZIP: GIL-enabled და free-threaded.
2. Python standard library-ის `hashlib`-ით გამოითვალა SHA-256 მთელ ZIP byte stream-ზე; `zipfile`-ით ამოიღო ერთი JSON report თითო არქივიდან.
3. თითოეულ report-ში დადასტურდა 48 case და თითო case-ზე 3 repetition.
4. 48 case-ის მიხედვით დამოუკიდებლად დაჯამდა თითოეული მეთოდის correctly-rounded run-ები, სრულად სწორი/ნულოვანი case-ები და 2–8 worker-ის CPU/wall და Neumaier-state speedup დიაპაზონები.
5. შედეგები შედარდა `data/noema-005/real-cpu-thread-summary-2026-11-26.json`-ში შენახულ artifact SHA-ებსა და აგრეგატებთან.

## შედეგები

### Artifact integrity

| Runtime | Artifact ID | ZIP bytes | გამოთვლილი SHA-256 |
|---|---:|---:|---|
| GIL-enabled | 15127921081 | 7,620 | `99e8f5970a73d55dcf6dff0aa3c37dc44312b0112add16404f303343af30775c` |
| Free-threaded | 15127418801 | 7,830 | `95e5d83563404c1e0de979991e5b71bd852f43af9c3ee05d0e5c8f6475a7fcd9` |

ორივე ZIP SHA-256 ზუსტად დაემთხვა frozen summary-ში შენახულ მნიშვნელობას. თითო არქივში აღმოჩნდა ერთი JSON report.

### Aggregate reproduction

| მეთოდი | GIL-enabled | Free-threaded |
|---|---:|---:|
| Naive scalar partials | 0/48 | 0/48 |
| Neumaier scalar partials | 42/48 | 42/48 |
| Neumaier (sum, correction) state merge | 48/48 | 48/48 |

ორივე runtime-ში scalar Neumaier-ის ორი configuration სრულად ჩავარდა: `grouped_cancellation`, contiguous partition, 2 worker და 8 worker. სრული compensation state-ის შენარჩუნება ყველა 48 run-ში სწორ შედეგს ინარჩუნებდა.

**2–8 worker-ის CPU-time/wall-time median ratio:**
- GIL-enabled: 1.004225–1.031445.
- Free-threaded: 1.879923–3.921785.

**Neumaier-state threaded speedup matching serial baseline-თან:**
- GIL-enabled: 0.667336–0.960844.
- Free-threaded: 0.578985–0.797759.

ყველა speedup 1-ზე ნაკლებია. ამიტომ ამ synthetic workload-ზე throughput-ის გაუმჯობესება არ დაფიქსირებულა, მიუხედავად free-threaded run-ში process CPU time-ის პარალელური დაგროვებისა.

## მტკიცებულების სტატუსი

- **FACT:** ჩამოტვირთული ZIP-ების ზომა და SHA-256 მნიშვნელობები ზუსტად დაემთხვა frozen summary-ს.
- **REPRODUCED RESULT:** ორიგინალური JSON report-ებიდან 48 case-ის ხელახალი aggregation-მა იგივე accuracy counts და metric ranges დააბრუნა, რაც frozen summary-შია.
- **INFERENCE:** compensation state-ის worker boundary-ზე შენარჩუნება ამ ორ synthetic cancellation layout-ში მნიშვნელოვანია; scalarized partial compensation საკმარისი არ აღმოჩნდა.
- **INFERENCE:** free-threaded runner-ზე CPU parallelism დაფიქსირდა, მაგრამ ამ workload-ზე wall-time speedup არ დადასტურდა.
- **HYPOTHESIS:** memory-bandwidth-bound ან რეალურ სამეცნიერო workload-ებზე ალგორითმების შეფარდება შეიძლება განსხვავდებოდეს.
- **UNTESTED IDEA:** იგივე პროტოკოლის გამეორება დამოუკიდებლად შერჩეულ ფიზიკურ x86-64 და ARM64 მოწყობილობებზე და pairwise/long-double/exact accumulator მეთოდების დამატება.

## შეზღუდვები

- ეს audit ჩამოტვირთული არტეფაქტების integrity/aggregation შემოწმებაა და არა benchmark-ის დამოუკიდებელი ხელახალი გაშვება.
- GitHub Actions raw artifact-ებს 30 დღით ინახავს; ეს ჩანაწერი ინახავს SHA-ებსა და aggregate შედეგებს, მაგრამ არა ZIP bytes-ს.
- GIL-enabled და free-threaded runner-ები სხვადასხვა host platform/provider-ზე მუშაობდნენ; მათი შედარება კონტროლირებული hardware experiment არ არის.
- workload მთლიანად synthetic cancellation-ია; production scientific data არ გამოყენებულა.
- `process_time_ns` process-wide CPU time-ია; `tracemalloc` არ არის RSS და native allocation-ებს სრულად არ ითვლის.
- დამოუკიდებელი physical-hardware replication და external numerical-method review არ ჩატარებულა.

## წყაროები

- [NOEMA-005 actual CPU-thread workflow 45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895)
- [Frozen aggregate summary](../../data/noema-005/real-cpu-thread-summary-2026-11-26.json)
- [Threaded benchmark implementation](../../scripts/benchmark_noema005_threaded_reduction.py)

## დასკვნა

Artifact provenance და aggregate arithmetic გადამოწმდა ორიგინალური GitHub Actions ZIP-ებიდან. ეს ზრდის NOEMA-005-ის შენახული შედეგების მიკვლევადობას, მაგრამ არ ცვლის კვლევის სტატუსს: NOEMA-005 რჩება **preliminary** და არ იძლევა ზოგადი performance advantage-ის ან ყველა input-ზე ფორმალური სიზუსტის მტკიცებას.
