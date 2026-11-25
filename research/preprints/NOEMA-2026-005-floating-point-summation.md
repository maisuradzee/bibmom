# მცურავი წერტილის ჯამის სიზუსტე: ალგორითმი, რიგითობა და გამეორებადობა

> **სტატუსი: წინასწარი კვლევა (preliminary).** ეს არის AI-ით მომზადებული და კოდით/ტესტებით გამეორებული წინასწარი კვლევითი ანგარიში. რეალური CPU-thread benchmark შესრულდა CPython 3.14.4 GIL-enabled და free-threaded რეჟიმებში; დამოუკიდებელი გარე რეცენზია, სხვა არქიტექტურაზე გამეორება და უახლეს Python patch-ებზე ტესტირება ჯერ არ დასრულებულა. შედეგები არ არის უნივერსალური სიჩქარის ან სიზუსტის გარანტია.

## კვლევის კითხვა

შეიძლება თუ არა ერთი და იმავე რიცხვების მულტისეტმა შეკრების განსხვავებული რიგითობის ან ალგორითმის გამო განსხვავებული შედეგი მოგვცეს? და როგორ იცვლება ამ მეთოდების დროისა და მეხსიერების ფასი სხვადასხვა floating-point/decimal ფორმატში?

## მთავარი მიგნება

დიახ. სასრული სიზუსტის არითმეტიკაში შეკრება ყოველთვის ასოციაციური არ არის. დიდი და მცირე რიცხვების შერევისას დამრგვალებამ მცირე წვლილი შეიძლება დაკარგოს; შემდგომი გაუქმება (cancellation) დაკარგულ ინფორმაციას ვეღარ აღადგენს. ამ კონტროლირებულ ექსპერიმენტში ერთსა და იმავე შეყვანათა დალაგებამ შედეგი შეცვალა. Kahan-ის კომპენსაცია ზოგიერთ შემთხვევას აუმჯობესებდა, მაგრამ ყველა ტესტში საკმარისი არ აღმოჩნდა. Neumaier-ისა და ზუსტი integer accumulator-ის შედეგები ამ კონკრეტულ stress-test-ებში ეტალონს დაემთხვა.

ეს არის კონკრეტული შეყვანებისა და იმპლემენტაციების შედეგი — არა მტკიცება, რომ ერთი მეთოდი ყველა ამოცანაში საუკეთესოა.

## რა შემოწმდა

NOEMA-2026-005-ში შედარებულია binary32, binary64, decimal64 და decimal128 არითმეტიკა. შესწავლილია naive left-to-right, adjacent pairwise, Kahan, Neumaier, math.fsum-ის შედარებითი გზა და ზუსტი integer superaccumulator.

კონტროლირებულ სტრეს-ტესტებში ერთი და იგივე მულტისეტი სხვადასხვა რიგითობით ჯამდებოდა. შედეგები შედარდა ზუსტ რაციონალურ ეტალონს. ცალკე შესრულდა runtime/memory პროფილი 1,024, 8,192 და 65,536 ელემენტზე, ორი warmup-ით და შვიდი გაზომვით თითო შემთხვევაზე.

## შედეგები: სწორად დამრგვალებული ჯამი

- Binary64 cancellation ტესტში naive და adjacent pairwise მეთოდებმა შვიდი დალაგებიდან მხოლოდ ორში მიიღეს სწორად დამრგვალებული შედეგი.
- Kahan-მა იმავე ტესტში ოთხი დალაგება დაამთხვია; Neumaier-მა, math.fsum-მა და integer accumulator-მა — შვიდივე.
- Binary32 ტესტებში Neumaier და integer accumulator ორივე შემოწმებულ stress-case-ში ყველა დალაგებას დაემთხვა; Kahan-ის შედეგი კონკრეტულ ტესტზე იყო დამოკიდებული.
- Decimal64/128 ტესტები აჩვენებს, რომ შედეგზე მოქმედებს precision და შეყვანის რიგითობა; decimal128-ის ერთ კონკრეტულ cancellation მაგალითში მცირე წევრი შენარჩუნდა, მაგრამ ეს ფორმატის ზოგადი გარანტია არ არის.

## შედეგები: runtime და მეხსიერება

<small>ქვემოთ მოცემული მონაცემები არის 65,536 ელემენტის შეყვანის median runtime, ერთ CPython 3.14.4 / Linux x86-64 გარემოში. თითო მეთოდზე შესრულდა 7 გაზომვა. დრო მილიწამებშია.</small>

| ფორმატი | naive | pairwise | Kahan | Neumaier | სხვა გზა / ზუსტი accumulator |
|---|---:|---:|---:|---:|---|
| binary64 | 0.662 | 3.644 | 2.195 | 3.141 | math.fsum 1.104; integer 60.835 |
| binary32 | 81.808 | 88.222 | 324.736 | 320.630 | fsum→binary32 0.383; integer 14.024 |
| decimal64 | 6.362 | 11.759 | 25.327 | 30.652 | integer 37.376 |
| decimal128 | 6.365 | 11.737 | 25.232 | 31.416 | integer 37.210 |

Binary32-ის fsum→binary32 არის უფრო მაღალი სიზუსტით დაგროვებისა და საბოლოო binary32 cast-ის გზა; ის არ არის binary32-native არითმეტიკა. integer ნიშნავს ამ კვლევაში გამოყენებულ Python reference-implementation-ს და არა ოპტიმიზებულ hardware ან production superaccumulator-ს.

ამ ერთ runner-ზე binary64 integer accumulator-ის median იყო 60.835 ms, ხოლო naive მეთოდის — 0.662 ms. ეს დაახლოებით 91.9-ჯერ სხვაობაა ამ კონკრეტულ იმპლემენტაციაში. Decimal integer accumulator-ის tracemalloc peak იყო დაახლოებით 6.85 MB. ეს მეტრიკა ზომავს Python-managed allocation-ს და არა პროცესის სრულ RSS-ს.

## ინტერპრეტაცია და პრაქტიკული რეკომენდაცია

რიცხვითი სისტემის გამეორებადობისთვის საკმარისი არ არის მხოლოდ შეყვანის მონაცემების შენახვა. უნდა დაფიქსირდეს შეკრების მეთოდი, რიგითობა ან reduction tree, precision და rounding mode. რთული ჯამებისთვის სასურველია adversarial cancellation regression-test და ზუსტ ან მაღალი სიზუსტის ეტალონთან შედარება.

NOEMA-ს წინადადებაა მცირე **summation contract**: პროექტმა დოკუმენტურად განსაზღვროს დაგროვების ალგორითმი, input ordering/deterministic reduction tree, regression fixture, ეტალონთან შედარების წესი და დასაშვები შეცდომა. ეს ახალი შეკრების ალგორითმი არ არის; მისი რეალურ წარმოებით სისტემებში ეფექტიანობა ჯერ არ შემოწმებულა.

## დამატებითი შედეგი — განაწილებული შეკრების სიმულაცია

შემოწმდა, ინარჩუნებს თუ არა განაწილებული reduction მცირე რიცხვით კომპონენტებს, როცა თითო worker მხოლოდ ერთ float-ს აბრუნებს. გამოყენებულია `[1e16, 1, -1e16]` triplet 1,000-ჯერ; ზუსტი ჯამი 1,000-ია. ორი partition სტრატეგიის, ხუთი input ordering-ის, 11 worker count-ისა და სამი worker merge ordering-ის კომბინაციამ შექმნა 330 კონფიგურაცია.

| Worker output / merge | ზუსტი დამთხვევა |
|---|---:|
| naive scalar + pairwise | 0/330 |
| Kahan scalar + pairwise | 24/330 |
| Neumaier scalar + pairwise | 114/330 |
| math.fsum scalar + pairwise | 114/330 |
| Neumaier `(sum, compensation)` state + compensated merge | **330/330** |

ეს შედეგი აჩვენებს, რომ ამ კონკრეტულ fixture-ში worker-ის მხოლოდ ერთი scalar შედეგი correction ინფორმაციას კარგავს; compensation state-ის ცალკე გადაცემამ და გლობალურმა Neumaier merge-მა ყველა 330 კონფიგურაციაში 1,000 დააბრუნა. ეს არ არის უნივერსალური გარანტია.

**მკაცრი შეზღუდვა:** ექსპერიმენტი არის დეტერმინისტული map/reduce სიმულაცია და არა რეალური მრავალნაკადიანი, GPU ან ქსელური distributed runtime-ის ტესტი. გამოყენებულია მხოლოდ ერთი synthetic cancellation dataset. რეალურ სისტემაში ეფექტიანობა, concurrency, communication cost და სხვა input distribution-ები ჯერ არ შემოწმებულა.

## დამატებითი შედეგი — რეალური CPU threads და free-threaded CPython

წინა 330-კონფიგურაციანი sharded reduction იყო სიმულაცია. ამ დამატებითმა ექსპერიმენტმა რეალურად გაუშვა `ThreadPoolExecutor` worker-ები ცალკე native OS threads-ზე და შეადარა CPython 3.14.4-ის ჩვეულებრივი GIL-enabled build და 3.14.4t free-threaded build. Python 3.14-ში free-threaded build ოფიციალურად მხარდაჭერილია, მაგრამ კვლავ არჩევითია; GIL-enabled build რჩება ჩვეულებრივ ნაგულისხმევ რეჟიმად.

**მეთოდი:** თითო runtime-ზე ორი deterministic input layout, N=65,536 და თითო layout 196,608 binary64 მნიშვნელობა; ზუსტი ჯამი 65,536. შედარებულია naive scalar partial, Neumaier scalar partial და Neumaier `(sum, compensation)` state merge. Worker count: 1, 2, 4, 8; partition: contiguous და round-robin; warmup: 1; measured repetitions: 3. თითო runtime-ზე 48 configuration და 144 measured run. თითოეულ worker-ს ჰქონდა განსხვავებული native thread ID.

**სიზუსტე — ორივე runtime-ზე იდენტური შედეგი:**

| მეთოდი | Triplet order | Grouped cancellation | სულ |
|---|---:|---:|---:|
| Naive scalar partial | 0/24 | 0/24 | 0/48 |
| Neumaier scalar partial | 24/24 | 18/24 | 42/48 |
| Neumaier compensation-state merge | 24/24 | 24/24 | **48/48** |

Neumaier scalar partial-ის ჩავარდნები დაფიქსირდა grouped-cancellation input-ის contiguous partition-ზე 2 და 8 worker-ის შემთხვევებში. Compensation-state merge-მა ყველა შემოწმებულ synthetic configuration-ში ზუსტი binary64 reference შეინარჩუნა.

**რეალური CPU concurrency:**

| მაჩვენებელი | GIL enabled | Free-threaded |
|---|---:|---:|
| CPU-time/wall-time > 1.05 | 0/144 | 108/144 |
| 2 worker | 0/36 | 36/36 |
| 4 worker | 0/36 | 36/36 |
| 8 worker | 0/36 | 36/36 |

Free-threaded Neumaier-state median CPU-time/wall-time ratio 1/2/4/8 worker-ზე იყო 0.99 / 1.95 / 3.52 / 3.47. ეს მიუთითებს მრავალბირთვიან CPU შესრულებაზე. თუმცა **threaded wall-time speedup serial baseline-თან შედარებით არც ერთ configuration-ში არ დაფიქსირებულა**: საუკეთესო მედიანური speedup იყო 0.777 GIL-enabled და 0.803 free-threaded რეჟიმში. ამ microbenchmark-ზე thread startup/scheduling და Python-level reduction overhead-მა პარალელიზმის სარგებელი გადაფარა.

**Tracemalloc peak — Neumaier state, median bytes (არა RSS):**

- GIL-enabled, 1/2/4/8 worker: 11,535 / 18,490 / 32,216 / 60,284.
- Free-threaded, 1/2/4/8 worker: 95,149 / 185,878 / 366,372 / 731,384.

შედეგები გარემოსა და CPU quota-ზეა დამოკიდებული. ორივე Actions runner იყო Ubuntu 24.04 x86_64, 4 CPU affinity-ით; ეს არ არის დამოუკიდებელი არქიტექტურული გამეორება. Python 3.14.4/3.14.4t ტესტი ზუსტად ფიქსირებული ვერსიის კონტროლია; 2026-11-25-ისთვის უახლესი 3.14 patch იყო 3.14.10, ხოლო უახლესი major — 3.15.2; ისინი ამ ციკლში არ შემოწმებულა.

**მონაცემები და არტეფაქტები:**

- [GIL-enabled result summary JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json)
- [Free-threaded result summary JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json)
- [Threaded benchmark protocol](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-protocol.json)
- [Benchmark script](https://github.com/maisuradzee/bibmom/blob/main/scripts/benchmark_noema005_threaded_reduction.py) და [unit tests](https://github.com/maisuradzee/bibmom/blob/main/tests/test_benchmark_noema005_threaded_reduction.py)
- [GitHub Actions run #45548551086](https://github.com/maisuradzee/bibmom/actions/runs/45548551086) — ორივე runtime matrix job წარმატებით დასრულდა; raw JSON artifacts SHA-256-ით არის მიბმული summary ფაილებში.

**დასკვნა:** real threads-ის არსებობა დადასტურდა. GIL-disabled რეჟიმში multi-worker CPU concurrency დაფიქსირდა, მაგრამ ამ synthetic Python workload-ზე wall-time speedup არ გამოვლინდა. Worker boundary-ზე compensation state-ის გადაცემა ამ ტესტებში scalar partial-ზე უფრო საიმედო აღმოჩნდა. ეს არის კონკრეტული synthetic fixture-ის შედეგი და არა ყველა floating-point reduction-ის უნივერსალური გარანტია.

## შეზღუდვები

- Benchmark runner-ზე დაფიქსირდა CPython 3.14.4 (გამოშვებულია 2026-04-07); ეს არ არის 2026-11-24-ის უახლესი patch release. სხვა ვერსიაზე გამეორება დარჩენილია.

- სრული პროფილი შესრულდა ერთ CPython/Linux runner-ზე; სხვა ოპერაციულ სისტემასა და არქიტექტურაზე შედეგები შეიძლება განსხვავდებოდეს.
- tracemalloc არ ზომავს სრულ პროცესულ RSS-ს და არ ასახავს ყველა native allocation-ს.
- Binary32-ის native-სიმულაცია Python-ის დონეზე ამრგვალებს შუალედურ ოპერაციებს; მისი სიჩქარე hardware binary32 ოპერაციის სიჩქარეს არ წარმოადგენს.
- Decimal კვლევა იყენებს Python decimal.Context-ს მითითებული precision/exponent პარამეტრებით; ის არ ამოწმებს IEEE decimal interchange-ის BID/DPD byte-level კოდირებას.
- Integer accumulator არის reference-oriented Python implementation და არა ოპტიმიზებული production ალგორითმი.
- Synthetic stress-test-ები არ წარმოადგენს რეალური workload-ების შეცდომის სიხშირის შეფასებას.
- რეალური CPU threads შემოწმდა მხოლოდ Ubuntu 24.04 x86_64-ზე; ARM, Windows, macOS, GPU და network-distributed runtime არ შემოწმებულა.
- sharded-reduction სიმულაცია გამეორდა CPython 3.13.5-სა და CPython 3.14.4-ზე ერთნაირი case-matrix SHA-256-ით; რეალური thread benchmark შესრულდა CPython 3.14.4/3.14.4t-ზე. უახლესი 3.14.10/3.15.2 patch/major ვერსიები და სხვა არქიტექტურა დარჩენილია.
- process CPU-time/wall-time ratio აჩვენებს aggregate CPU utilization-ს და არა throughput speedup-ს; ამ კვლევაში threaded wall-time serial baseline-ზე უკეთესი არ იყო.
- free-threaded CPython ოფიციალურად მხარდაჭერილია Python 3.14-დან როგორც optional build (PEP 779); მესამე მხარის extension-ებმა შეიძლება GIL ხელახლა ჩართონ.

## გამეორებადობა და წყარო მონაცემები

- სრული benchmark workflow: [GitHub Actions run #45283854718](https://github.com/maisuradzee/bibmom/actions/runs/45283854718).
- გამოთვლის კოდი: [summation simulation](https://github.com/maisuradzee/bibmom/blob/main/scripts/simulate_noema005_summation.py) და [runtime/memory benchmark harness](https://github.com/maisuradzee/bibmom/blob/main/scripts/benchmark_noema005_summation.py).
- ავტომატური შემოწმებები: [summation unit tests](https://github.com/maisuradzee/bibmom/blob/main/tests/test_noema005_summation.py) და [benchmark tests](https://github.com/maisuradzee/bibmom/blob/main/tests/test_benchmark_noema005_summation.py).
- [Benchmark protocol](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/benchmark-protocol.json)
- [Full profile summary JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/benchmark-full-profile-summary-2026-11-24.json)
- [Summation experiment result JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/floating-summation-results.json)
- [Parallel reduction simulation code](https://github.com/maisuradzee/bibmom/blob/main/scripts/simulate_noema005_parallel_reduction.py), [tests](https://github.com/maisuradzee/bibmom/blob/main/tests/test_noema005_parallel_reduction.py), [protocol](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/parallel-reduction-protocol.json) და [frozen summary JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/parallel-reduction-results.json)
- [Real CPU-thread benchmark script](https://github.com/maisuradzee/bibmom/blob/main/scripts/benchmark_noema005_threaded_reduction.py), [tests](https://github.com/maisuradzee/bibmom/blob/main/tests/test_benchmark_noema005_threaded_reduction.py), [protocol](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-protocol.json), [GIL-enabled summary](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json) და [free-threaded summary](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json).
- [კვლევის სრული სამუშაო ჩანაწერი](https://github.com/maisuradzee/bibmom/blob/main/research/drafts/NOEMA-2026-005-floating-summation-order.md)

## წყაროები

1. Higham, N. J. (1993, July). *The Accuracy of Floating Point Summation*. SIAM Journal on Scientific Computing, 14(4), 783–799. DOI: https://doi.org/10.1137/0914050. Accessed 2026-11-24.
2. Ogita, T., Rump, S. M., & Oishi, S. (2005, January; online 2006-07-25). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. DOI: https://doi.org/10.1137/030601818. Accessed 2026-11-24.
3. Shewchuk, J. R. (1997, October). *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates*. Discrete & Computational Geometry, 18(3), 305–363. DOI: https://doi.org/10.1007/PL00009321. Accessed 2026-11-24.
4. IEEE Computer Society. (2019-07-22). *IEEE Std 754-2019: IEEE Standard for Floating-Point Arithmetic*. https://standards.ieee.org/ieee/754/6210/. Accessed 2026-11-24.
5. Python Software Foundation. (documentation page last updated 2026-10-26 15:00 UTC; no separate page-publication date stated). *Python 3.12.16 documentation: Built-in Functions, sum()*. https://docs.python.org/3.12/library/functions.html#sum. Accessed 2026-11-24.
6. Python Software Foundation. (documentation page last updated 2026-10-26 15:00 UTC; no separate page-publication date stated). *Python 3.12.16 documentation: math.fsum()*. https://docs.python.org/3.12/library/math.html#math.fsum. Accessed 2026-11-24.
7. Python Software Foundation. (documentation page last updated 2026-10-26 15:00 UTC; no separate page-publication date stated). *Python 3.12.16 documentation: decimal module*. https://docs.python.org/3.12/library/decimal.html. Accessed 2026-11-24.
8. NIST. (2010-05-11; site version 1.2.8 dated 2026-09-15). *Digital Library of Mathematical Functions, §3.1*. https://dlmf.nist.gov/3.1. Accessed 2026-11-24.
9. Python Software Foundation. (2026-04-07). *Python 3.14.4 release*. https://www.python.org/downloads/release/python-3144/. Accessed 2026-11-24.
10. Gross, S. (2023-01-09; Steering Council acceptance 2023-10-24). *PEP 703 — Making the Global Interpreter Lock Optional in CPython*. https://peps.python.org/pep-0703/. Accessed 2026-11-25.
11. Wouters, T., Page, M., & Gross, S. (2025-03-13; resolution 2025-06-16). *PEP 779 — Criteria for supported status for free-threaded Python*. https://peps.python.org/pep-0779/. Accessed 2026-11-25.
12. Python Software Foundation. (2025-10-07). *Python 3.14.0 release*. https://www.python.org/downloads/release/python-3140/. Accessed 2026-11-25.
13. Python Software Foundation. (documentation version 3.14.10 released 2026-10-25; individual page has no separate publication date). *Python 3.14 free-threading HOWTO*. https://docs.python.org/3.14/howto/free-threading-python.html. Accessed 2026-11-25.
14. Python Software Foundation. (documentation version 3.14.10 released 2026-10-25; individual page has no separate publication date). *Python 3.14 threading library reference*. https://docs.python.org/3.14/library/threading.html. Accessed 2026-11-25.
15. Python Software Foundation. (documentation version 3.14.10 released 2026-10-25; individual page has no separate publication date). *Python 3.14 time library reference*. https://docs.python.org/3.14/library/time.html. Accessed 2026-11-25.
16. Python Software Foundation. (documentation version 3.14.10 released 2026-10-25; individual page has no separate publication date). *Python 3.14 tracemalloc library reference*. https://docs.python.org/3.14/library/tracemalloc.html. Accessed 2026-11-25.

## შემდეგი ნაბიჯები

1. სრული benchmark-ის გამეორება მინიმუმ სამ დამოუკიდებელ run-ზე და სხვა Python ვერსიასა/არქიტექტურაზე.
2. integer accumulator-ის ოპტიმიზაცია ისე, რომ ზუსტი reference უცვლელი დარჩეს.
3. simulated sharded reduction-ის შემდეგ რეალური CPU threads, GPU და distributed framework-ის შემოწმება; scalar-only და compensation-state API-ების შედარება.
4. რეალური სამეცნიერო მონაცემთა ნაკრების დამატება.
5. დამოუკიდებელი მკვლევრის მიერ მეთოდოლოგიის, ტესტებისა და წყაროების გადამოწმება.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.
