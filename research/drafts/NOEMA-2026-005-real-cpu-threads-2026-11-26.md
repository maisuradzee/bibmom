# NOEMA-005 — რეალური CPU threads და კომპენსირებული reduction

- **ID:** NOEMA-2026-005-REAL-THREADS-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი სიზუსტე, პარალელური გამოთვლები, Python GIL და free-threaded runtime

## საკვლევი კითხვა

როგორ იცვლება cancellation-heavy reduction-ის სიზუსტე და CPU პარალელიზმი რეალურ native threads-ზე, როცა თითო worker აბრუნებს მხოლოდ scalar compensated sum-ს ან სრულ Neumaier (sum, correction) state-ს?

## ჰიპოთეზა

თუ თითო worker-ის compensation state merge-მდე scalar-ად დაიკეცება, შეიძლება დაიკარგოს ის დაბალი რიგის ინფორმაცია, რომელიც საბოლოო exact-rounded result-ისთვის აუცილებელია. სრულ (sum, correction) წყვილის შენარჩუნებამ შეიძლება გაზარდოს სიზუსტე, ხოლო free-threaded CPython-მა შეიძლება გამოავლინოს CPU-level პარალელიზმი, რომელსაც GIL-enabled runtime ზღუდავს.

## მეთოდი ან ექსპერიმენტის გეგმა

- პროგრამა: `scripts/benchmark_noema005_threaded_reduction.py`.
- ორი deterministic layout: `triplet_order` და `grouped_cancellation`; თითო layout შეიცავს 196,608 binary64 მნიშვნელობას (repeat_count=65,536).
- 4 worker count (1, 2, 4, 8) × 2 partition (contiguous, round_robin) × 3 მეთოდი (naive scalar, Neumaier scalar, Neumaier state) = 48 შემთხვევა თითო runtime-ზე.
- თითო შემთხვევაზე 1 warmup და 3 timed repetition; თითო worker-ის native identity მოწმდება `threading.get_native_id`-ით.
- სიზუსტის reference არის ზუსტი Fraction-იდან სწორად დამრგვალებული binary64 მნიშვნელობა.
- CPU parallelism იზომება process-wide CPU time / wall time შეფარდებით. Memory metric არის tracemalloc peak delta და არა RSS ან native allocation.
- ერთი run იყენებს CPython 3.14.4 GIL-enabled build-ს; მეორე — CPython 3.14.4 free-threaded build-ს, სადაც GIL გამორთულია. ორივე hosted x86-64 runner-ზეა, მაგრამ განსხვავებულ host platform/provider-ზე.

## შედეგები — REPRODUCED RESULT

Exact workflow run: [45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895), source head `b4df9c9c1f7d2142c8d48e487a73977be70b9966`. ორივე runtime-ის artifact წარმატებით აიტვირთა; თითოეულში 48 case და 144 timed repetition არის.

### სიზუსტე

| მეთოდი | GIL-enabled | Free-threaded |
|---|---:|---:|
| Naive scalar partials | 0/48 correct runs | 0/48 |
| Neumaier scalar partials | 42/48 | 42/48 |
| Neumaier (sum, correction) state merge | 48/48 | 48/48 |

Neumaier scalar variant ორივე runtime-ში ვერ გადის ორ კონკრეტულ კონფიგურაციას: grouped_cancellation / 2 workers / contiguous და grouped_cancellation / 8 workers / contiguous. სრულ state-ის შენარჩუნება ყველა 48 შემთხვევაში სწორ შედეგს იძლევა. ეს მიუთითებს, რომ compensation-ის თითო worker-ში გამოყენება საკმარისი არ არის, თუ merge-მდე correction დაიკარგა.

### CPU parallelism და runtime

- GIL-enabled run: 2–8 worker-ის CPU/wall ratio 1.004–1.031.
- Free-threaded run: 2–8 worker-ის CPU/wall ratio 1.880–3.922.
- Free-threaded run-ში process CPU time-ის დაგროვება ადასტურებს ერთზე მეტი CPU-ის ერთდროულ გამოყენებას ამ synthetic workload-ზე.
- მიუხედავად ამისა, Neumaier-state threaded speedup matching serial baseline-თან შედარებით ორივე run-ში 1-ზე ნაკლები იყო: GIL-enabled 0.667–0.961; free-threaded 0.579–0.798. ამ workload-ზე thread-pool overhead-მა throughput არ გააუმჯობესა.

### არტეფაქტები და provenance

- GIL-enabled artifact: ID 15127921081, SHA-256 `99e8f5970a73d55dcf6dff0aa3c37dc44312b0112add16404f303af30775c`.
- Free-threaded artifact: ID 15127418801, SHA-256 `95e5d83563404c1e0de979991e5b71bd852f43af9c3ee05d0e5c8f6475a7fcd9`.
- Raw artifacts GitHub Actions-ში 30 დღით ინახება; შეჯამებული მნიშვნელობები გაყინულია `data/noema-005/real-cpu-thread-summary-2026-11-26.json)-ში.

## მტკიცებულების სტატუსი

- **FACT:** ორივე runner-მა 48 threaded case შეასრულა, თითოეულზე 3 repetition-ით; native thread identity validation წარმატებით დასრულდა.
- **REPRODUCED RESULT:** Neumaier state merge-მა 48/48 run-ში სწორად დააბრუნა შედეგი ორივე runtime-ში; scalarized Neumaier-მა 42/48; naive partials 0/48.
- **REPRODUCED RESULT:** GIL-enabled CPU/wall ratio დარჩა დაახლოებით 1-ზე, ხოლო free-threaded runner-ზე 1.88–3.92 იყო 2–8 worker-ის შემთხვევაში.
- **INFERENCE:** compensation state-ის შენარჩუნება merge boundary-ზე მნიშვნელოვანია; მხოლოდ worker-local compensation გარანტიას არ იძლევა.
- **INFERENCE:** free-threaded runtime იძლევა CPU parallelism-ს ამ test harness-ში, მაგრამ ეს არ ნიშნავს ავტომატურ speedup-ს.
- **HYPOTHESIS:** უფრო დიდ, memory-bandwidth-bound ან რეალურ scientific workloads-ზე შედეგები შეიძლება განსხვავდებოდეს.
- **UNTESTED IDEA:** native C/OpenMP, pairwise tree reduction და exact accumulator-ის შედარება იმავე input/partition matrix-ზე დამოუკიდებელ physical x86-64 და ARM64 სისტემებზე.

## შეზღუდვები და გაურკვევლობები

- ორივე runner hosted x86-64-ია და განსხვავებულ host platform/provider-ზე მუშაობს; GIL-enabled და free-threaded შედეგები კონტროლირებული, ერთი და იმავე აპარატურის შედარება არ არის.
- მხოლოდ ორი synthetic cancellation pattern შემოწმდა; შედეგები არ წარმოადგენს რეალურ სამეცნიერო აპლიკაციებს.
- თითო case-ზე სამი repetition მცირე ნიმუშია; confidence interval არ გამოთვლილა.
- CPU time არის process-wide და არა თითო thread-ის ცალკე profiler.
- tracemalloc არ ითვლის RSS-ს, C heap-ს ან სხვა native allocation-ს.
- benchmark-ის წარმატებული workflow ნიშნავს მეთოდოლოგიისა და report-ის ვალიდაციას; ის არ ნიშნავს, რომ ყველა ალგორითმი ზუსტია ან სწრაფია.
- დამოუკიდებელი ფიზიკური hardware replication და external numerical review არ ჩატარებულა.

## დასკვნა

ამ run-ის ყველაზე მნიშვნელოვანი ტექნიკური შედეგია: Neumaier correction state უნდა შენარჩუნდეს worker boundary-დან საბოლოო merge-მდე. Scalar partial-ად დაკეცვამ ორი deterministic grouped-cancellation configuration ჩააგდო. Free-threaded runtime-მა აჩვენა CPU parallelism, მაგრამ მოცემულ workload-ზე სიჩქარის გაუმჯობესება არ მოუტანია. NOEMA-005 რჩება preliminary.

## წყაროები

1. NOEMA threaded reduction benchmark: https://github.com/maisuradzee/bibmom/blob/main/scripts/benchmark_noema005_threaded_reduction.py
2. Exact workflow run and artifacts: https://github.com/maisuradzee/bibmom/actions/runs/45840219895
3. NOEMA full-width MPFR oracle draft: https://github.com/maisuradzee/bibmom/blob/main/research/drafts/NOEMA-2026-005-mpfr-full-width-oracle-2026-11-26.md

## შემდეგი ნაბიჯები

1. იგივე benchmark გაიმეორე დამოუკიდებელ ფიზიკურ x86-64 და ARM64 სისტემებზე.
2. დაამატე pairwise tree, long double და exact accumulator იმავე worker/partition matrix-ში.
3. ჩაატარე memory-bandwidth-bound და representative scientific workload benchmark-ები.
4. შეაგროვე საკმარისი repetitions და uncertainty intervals; შემდეგ მოითხოვე დამოუკიდებელი numerical-method review.

## შემოწმების სტატუსი

- **Exact-head workflow:** [45840219895](https://github.com/maisuradzee/bibmom/actions/runs/45840219895) — ორივე GIL-enabled და free-threaded job წარმატებით დასრულდა.
- **Quality CI:** [45840219937](https://github.com/maisuradzee/bibmom/actions/runs/45840219937) — success.
- **Native MPFR x86-64/ARM64:** [45840219897](https://github.com/maisuradzee/bibmom/actions/runs/45840219897) — success.
- **სტატუსი:** draft; NOEMA-005 არ გადადის Published-ში.

