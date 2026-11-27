# მცურავი წერტილის ჯამის სიზუსტე: ალგორითმი, რიგითობა და გამეორებადობა

> **სტატუსი: წინასწარი კვლევა (preliminary).** ანგარიში აერთიანებს CPython 3.14.4-ის წინა x86-64/ARM64 hosted runs-ს და Run 38 experiment 002-ის CPython 3.14.10 GIL-enabled/free-threaded ექვს hosted cell-ს. Run 38-ში Neumaier-state სიზუსტე 288/288 იყო, მაგრამ არცერთმა 384 threaded configuration-მა შესაბამის serial baseline-ს არ აჯობა. ფიზიკური მოწყობილობის დამოუკიდებელი გამეორება, RSS/DRAM გაზომვები და გარე numerical-method review ჯერ არ დასრულებულა. შედეგები არ არის უნივერსალური სიჩქარის ან სიზუსტის გარანტია.

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

## ARM64 რეალური CPU-thread გამეორება (2026-11-26)

**სტატუსი:** preliminary — ეს არის NOEMA-2026-005-ის გამეორებითი დამატება და არა ახალი კვლევის ID.

**საკვლევი კითხვა:** ინარჩუნებს თუ არა კომპენსირებული reduction-ის სიზუსტე შედეგს რეალურ ARM64 CPU threads-ზე, როგორც GIL-enabled, ისე free-threaded CPython რეჟიმში?

### მეთოდი

- GitHub Actions-ის ორი ARM64 runner ოჯახი: `ubuntu-24.04-arm` (4 process-visible CPU) და `macos-15` (3 process-visible CPU).
- თითო runner-ზე CPython 3.14.4 GIL-enabled და 3.14.4 free-threaded build.
- 2 deterministic binary64 layout × 4 worker count (1, 2, 4, 8) × 2 partition strategy × 3 reduction methods × 3 measured repetitions.
- თითო runtime cell: 48 configuration, 144 measured run.
- Seed არ გამოიყენება; input values კონსტრუირებულია დეტერმინისტულად. ორივე input-ის SHA-256 ერთნაირია ოთხივე runner-ზე.
- exact reference მიიღება input binary64 მნიშვნელობების ზუსტი რაციონალური ჯამიდან და ერთხელ binary64-ში დამრგვალებით.
- process CPU time / wall time გამოიყენება პარალელური CPU მოხმარების ინდიკატორად; `tracemalloc` ზომავს Python allocation-ებს და არა RSS-ს.

### შედეგები

| ARM64 runner/runtime | Neumaier state — სწორი შედეგი | CPU/wall >1.05 | State მეთოდის მედიანური speedup |
|---|---:|---:|---:|
| Ubuntu, GIL enabled | 48/48 | 0/144 | 0.738 |
| Ubuntu, free-threaded | 48/48 | 108/144 | 0.666 |
| macOS, GIL enabled | 48/48 | 0/144 state-method samples (2/144 ყველა მეთოდზე) | 0.908 |
| macOS, free-threaded | 48/48 | 100/144 | 0.922 |

ოთხივე runtime-ზე ჯამურად:
- **Neumaier state:** 192/192 სწორად დამრგვალებული შედეგი.
- **Neumaier scalar partial:** 168/192.
- **Naive scalar partial:** 0/192.
- **Free-threaded CPU/wall threshold:** 208/288 sample.
- **GIL-enabled CPU/wall threshold:** 2/288 sample.

### ინტერპრეტაცია

**FACT:** ყველა runner-ზე ყველა worker-ის native thread ID განსხვავებული იყო; workflow-მა ARM64 არქიტექტურა და რეალური GIL მდგომარეობა runtime-ზე გადაამოწმა.

**REPRODUCED RESULT:** Neumaier-ის `(sum, compensation)` state-ის გადაცემამ ოთხივე ARM64 runtime-ზე ზუსტი reference შეინარჩუნა ყველა გაზომილ გამეორებაში.

**INFERENCE:** free-threaded CPython-მა ორივე ARM64 runner ოჯახზე aggregate multi-core CPU execution აჩვენა. ეს არ ნიშნავს ავტომატურ wall-time აჩქარებას.

**HYPOTHESIS:** compensation-state reduction-ის სიზუსტე შესაძლოა ამ ტიპის binary64 cancellation input-ებზე runtime/არქიტექტურის მიმართ მდგრადი იყოს; საჭიროა სხვა CPU-ები, უფრო ხანგრძლივი გაზომვები და რეალური workload-ები.

**UNTESTED IDEA:** native C/OpenMP reduction-ის შედარება იმავე ARM64 runner-ებზე.

Threaded Neumaier-state მეთოდის median speedup ყველა 48 კონფიგურაციაზე თითოეულ runtime-ში 1.0-ზე ნაკლები იყო. macOS free-threaded რეჟიმში მხოლოდ 2-worker ჯგუფის median speedup აღმოჩნდა 1.03; ეს ერთი სამჯერადი benchmark პროფილია და არა ზოგადი წარმადობის მტკიცებულება. CPU/wall >1.05 მაჩვენებელი CPU პარალელურ მოხმარებას მიუთითებს და არა უფრო სწრაფ დასრულებას.

8 worker-ზე `tracemalloc` peak დაახლოებით 60 KB იყო GIL-enabled და დაახლოებით 731 KB free-threaded რეჟიმში. ეს არ არის RSS და native allocation-ებს სრულად არ მოიცავს.

x86-64 წინა შედეგებთან შედარება მხოლოდ აღწერითია: runner-ები და CPU-ები განსხვავდება, ამიტომ სხვაობა მხოლოდ არქიტექტურას ვერ მიეწერება.

### მონაცემები და გამეორება

- შედეგების შეჯამება: [ARM64 benchmark JSON](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json).
- benchmark კოდი: [threaded reduction script](https://github.com/maisuradzee/bibmom/blob/main/scripts/benchmark_noema005_threaded_reduction.py); [ARM64 report validator](https://github.com/maisuradzee/bibmom/blob/main/scripts/validate_noema005_arm64_report.py); [replication protocol](https://github.com/maisuradzee/bibmom/blob/main/research/drafts/NOEMA-2026-005-arm64-replication-protocol.md).
- workflow: [run 45752987940](https://github.com/maisuradzee/bibmom/actions/runs/45752987940).
- quality/site CI: [run 45752987825](https://github.com/maisuradzee/bibmom/actions/runs/45752987825).
- benchmark run head: `4fe358edd532d1861544951682e9125f67a4e156`.
- raw report JSON-ების SHA-256 და Actions artifact digest შეჯამების ფაილშია; raw artifacts 2026-12-26-მდე ინახება.
- CI-მ ოთხივე ARM64 job, report validator, unit tests, schema/catalog validation, frozen-result reproduction და site build წარმატებით შეასრულა.

### შეზღუდვები

- Hosted VM-ები კონტროლირებულ ლაბორატორიულ აპარატურას არ წარმოადგენს.
- Ubuntu და macOS runner-ები განსხვავდება CPU-ით, OS-ით და core count-ით.
- მხოლოდ CPython 3.14.4 და სამი measured repetition შემოწმდა.
- სინთეზური cancellation input-ები არ წარმოადგენენ ტიპურ სამეცნიერო workload-ს.
- `tracemalloc` არ ზომავს RSS-ს ან ყველა native allocation-ს.
- დამოუკიდებელი გარე რეცენზია ჯერ არ ჩატარებულა; კვლევის სტატუსი რჩება preliminary.

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


17. GitHub. (documentation snapshot accessed 2026-11-26; page does not state a publication date). *GitHub-hosted runners reference*. https://docs.github.com/en/actions/reference/runners/github-hosted-runners. Accessed 2026-11-26.
18. GitHub. (2025-01-16). *Linux arm64 hosted runners now available for free in public repositories (Public Preview)*. https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/. Accessed 2026-11-26.
19. Python Software Foundation. (documentation version 3.14.10 released 2026-10-25; individual page has no separate publication date). *Python 3.14 free-threading HOWTO*. https://docs.python.org/3.14/howto/free-threading-python.html. Accessed 2026-11-26.

## შემდეგი ნაბიჯები

1. ARM64-ის შემდეგი გამეორება Windows ARM64-ზე ან სხვა დამოუკიდებელ ARM64 runner-ზე.
2. Python ThreadPoolExecutor-ის შედარება native C/OpenMP reduction-თან იმავე runner-ზე.
3. მინიმუმ 20 measured repetition და დროის განაწილების/დისპერსიის ანგარიშგება.
4. RSS/native allocation გაზომვის დამატება `tracemalloc`-ის პარალელურად.
5. დამოუკიდებელი მკვლევრის მიერ მეთოდოლოგიის, ტესტებისა და წყაროების გადამოწმება.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.

## ARM64-ის დამოუკიდებელი მეორე გამეორება — 2026-11-26

**REPRODUCED RESULT:** PR #23-ის მეორე ARM64 workflow run-მა `45754595646` ოთხივე runner/runtime უჯრედში იგივე სინთეზური input hash-ები გამოიყენა და 48 configuration × 3 repetition შეასრულა თითო უჯრედში. Neumaier `(sum, compensation)` state-მა კვლავ მიიღო 192/192 სწორად დამრგვალებული შედეგი; scalar Neumaier — 168/192; naive scalar — 0/192. პირველ batch-თან შედარებით ზუსტი შედეგი უცვლელად განმეორდა: ორ batch-ზე Neumaier-state 384/384, scalar Neumaier 336/384 და naive scalar 0/384.

| ARM64 runtime cell | Neumaier-state accuracy | CPU/wall >1.05 | Median state speedup |
|---|---:|---:|---:|
| Ubuntu 24.04 ARM64, GIL enabled | 48/48 | 0/144 | 0.737 |
| Ubuntu 24.04 ARM64, free-threaded | 48/48 | 108/144 | 0.704 |
| macOS 15 ARM64, GIL enabled | 48/48 | 1/144 (naive scalar sample) | 0.896 |
| macOS 15 ARM64, free-threaded | 48/48 | 103/144 | 0.676 |

**INFERENCE:** ზუსტი რიცხვითი შედეგი ამ ორ ARM64 batch-ში გამეორდა. ამავე დროს, CPU-time/wall-time 1.05 threshold-ის გადაკვეთის რაოდენობა შეიცვალა: free-threaded 208/288-დან 211/288-მდე, GIL-enabled 2/288-დან 1/288-მდე. ამიტომ ეს threshold-count მგრძნობიარეა კონკრეტული გაშვების პირობებზე და არ უნდა განვიხილოთ როგორც სტაბილური პარალელიზმის ან წარმადობის საზომი.

მეორე batch-ის ოთხივე runtime cell-ში Neumaier-state median wall-time speedup 1.0-ზე ნაკლები იყო. CPU-ის aggregate დროის ზრდა არ ნიშნავს მოკლე დასრულების დროს. Python-ის ოფიციალური დოკუმენტაცია ასევე აფრთხილებს, რომ free-threaded build-ის შესრულება workload-სა და hardware-ზეა დამოკიდებული და დამატებითი single-thread/memory overhead შეიძლება ჰქონდეს.

**FACT:** Python 3.14 free-threading HOWTO აღწერს `sys._is_gil_enabled()`-ით მიმდინარე GIL მდგომარეობის შემოწმებას და აღნიშნავს, რომ free-threaded რეჟიმი ყველა workload-ს ავტომატურად არ აჩქარებს. GitHub-ის runner reference ასახელებს Ubuntu ARM64 runner-ს 4 CPU-ით და macOS 15 ARM64 M1 runner-ს 3 CPU-ით.

**UNTESTED IDEA:** იგივე პროტოკოლის Windows ARM64-ზე ან სხვა დამოუკიდებელ ARM64 გარემოში გამეორება; native C/OpenMP reduction-ის შედარება; მინიმუმ 20 measured repetition და RSS/native allocation გაზომვა.

**მონაცემები და provenance:** [მეორე batch-ის სრული aggregate/provenance JSON](../data/noema-005/arm64-repeat-validation-2026-11-26.json); [ARM64 workflow run 45754595646](https://github.com/maisuradzee/bibmom/actions/runs/45754595646); [quality/site run 45754595614](https://github.com/maisuradzee/bibmom/actions/runs/45754595614). ოთხივე raw report ZIP ჩამოიტვირთა და შემოწმდა; SHA-256, byte length, artifact ID და archive SHA-256 ინახება JSON-ში. GitHub Actions raw artifacts ინახება 30 დღე; JSON-ში ჩაწერილი hash-ები მათ მუდმივ არქივად არ აქცევს.

**შეზღუდვები:** hosted VM-ები კონტროლირებული ლაბორატორიული აპარატურა არ არის; Ubuntu და macOS CPU/OS/core count-ით განსხვავდება; თითო უჯრედში მხოლოდ სამი გაზომილი გამეორებაა; მონაცემები ხელოვნური cancellation fixture-ებია; `tracemalloc` არ ზომავს სრულ RSS-ს ან ყველა native allocation-ს. დამოუკიდებელი გარე რეცენზია არ ჩატარებულა.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.


## ARM64-ის მესამე დამოუკიდებელი გამეორება — 2026-11-26

**REPRODUCED RESULT:** მესამე benchmark batch-მა `45756074975` ოთხივე ARM64 runtime cell-ზე იგივე 48 configuration × 3 repetition პროტოკოლი შეასრულა. Neumaier-state კვლავ სწორად დამრგვალდა 192/192 measured run-ში; scalar Neumaier — 168/192; naive scalar — 0/192. სამი batch-ის ჯამური შედეგია: Neumaier-state **576/576**, scalar Neumaier **504/576**, naive scalar **0/576**.

| ARM64 runtime cell | Neumaier-state accuracy | CPU/wall >1.05 | Median state speedup |
|---|---:|---:|---:|
| Ubuntu 24.04 ARM64, GIL enabled | 48/48 | 0/144 | 0.739 |
| Ubuntu 24.04 ARM64, free-threaded | 48/48 | 108/144 | 0.702 |
| macOS 15 ARM64, GIL enabled | 48/48 | 0/144 | 0.812 |
| macOS 15 ARM64, free-threaded | 48/48 | 106/144 | 1.003 |

**INFERENCE:** რიცხვითი სიზუსტე სამ დამოუკიდებელ batch-ში უცვლელი დარჩა. წარმადობის დიაგნოსტიკური მაჩვენებლები უფრო ცვალებადია: CPU/wall >1.05 threshold free-threaded რეჟიმში შეიცვალა 208/288 → 211/288 → 214/288, ხოლო GIL-enabled რეჟიმში 2/288 → 1/288 → 0/288. მესამე batch-ში macOS free-threaded state-method median speedup მხოლოდ 1.003 იყო (დაახლოებით 0.3%); ეს ერთი hosted-runner-ის სამჯერადი გაზომვაა და არ წარმოადგენს საიმედო აჩქარების მტკიცებულებას.

**მნიშვნელოვანი მეთოდოლოგიური შესწორება:** CPU-time/wall-time >1.05 threshold არის აღწერითი დიაგნოსტიკა და არა წინასწარ განსაზღვრული სტატისტიკური ტესტი. მისი გადაკვეთის რაოდენობა batch-ებს შორის იცვლება. წარმადობის დასკვნისთვის საჭიროა მეტი გამეორება, dispersion/confidence interval, RSS/native allocation და იგივე აპარატურაზე native C/OpenMP კონტროლი.

**მონაცემები და provenance:** [სამივე batch-ის შედეგები, report/archive hash-ები და run-ების metadata](../data/noema-005/arm64-repeat-validation-2026-11-26.json); [მესამე ARM64 run 45756074975](https://github.com/maisuradzee/bibmom/actions/runs/45756074975); [quality/site run 45756074962](https://github.com/maisuradzee/bibmom/actions/runs/45756074962); [x86-64 threaded benchmark 45756074982](https://github.com/maisuradzee/bibmom/actions/runs/45756074982). ოთხივე raw report ZIP ჩამოიტვირთა და SHA-256-ით შემოწმდა. GitHub Actions artifacts 30 დღე ინახება; hash-ები provenance-ს ინარჩუნებს, მაგრამ raw reports-ის მუდმივ არქივს არ წარმოადგენს.

**შეზღუდვები:** hosted VM-ები კონტროლირებული ლაბორატორიული აპარატურა არ არის; Ubuntu და macOS runner-ები CPU/OS/core count-ით განსხვავდება; თითო უჯრედში მხოლოდ სამი measured repetition ჩატარდა; მონაცემები სინთეზური cancellation fixture-ებია; `tracemalloc` არ ზომავს სრულ RSS-ს ან ყველა native allocation-ს. დამოუკიდებელი გარე რეცენზია არ ჩატარებულა.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.


## საბოლოო PR-head ARM64 verification — მეოთხე batch

**REPRODUCED RESULT:** საბოლოო PR head `f944a7d26323342ce596437163fcb2a483778107`-ზე ARM64 workflow run `45756479611` ოთხივე runner/runtime უჯრედში წარმატებით დასრულდა. Neumaier-state კვლავ სწორად დამრგვალდა 192/192 measured run-ში; scalar Neumaier — 168/192; naive scalar — 0/192. ოთხი დამოუკიდებელი batch-ის ჯამური შედეგია: Neumaier-state **768/768**, scalar Neumaier **672/768**, naive scalar **0/768**.

| ARM64 runtime cell | Neumaier-state accuracy | CPU/wall >1.05 | Median state speedup |
|---|---:|---:|---:|
| Ubuntu 24.04 ARM64, GIL enabled | 48/48 | 0/144 | 0.739 |
| Ubuntu 24.04 ARM64, free-threaded | 48/48 | 108/144 | 0.663 |
| macOS 15 ARM64, GIL enabled | 48/48 | 0/144 | 0.794 |
| macOS 15 ARM64, free-threaded | 48/48 | 99/144 | 0.858 |

**INFERENCE:** ზუსტი შედეგი ოთხივე batch-ში უცვლელი დარჩა. CPU/wall threshold-ის რაოდენობა კვლავ მერყეობდა: free-threaded 208/288 → 211/288 → 214/288 → 207/288; GIL-enabled 2/288 → 1/288 → 0/288 → 0/288. მეოთხე batch-ში ოთხივე runtime-cell state-method median speedup 1.0-ზე ნაკლები იყო. მესამე batch-ის ერთ cell-ში 1.003 median speedup იყო, რაც სხვა batch-ებში არ განმეორდა; ეს კიდევ ერთხელ აჩვენებს, რომ სამი measured repetition-ით წარმადობის მცირე განსხვავებები სანდოდ ვერ ფასდება.

**FACT:** Python-ის ოფიციალური `time.process_time()` დოკუმენტაცია განსაზღვრავს მას როგორც მიმდინარე პროცესის user+system CPU time-ის ჯამს; `perf_counter()` გამოიყენება elapsed duration-ის გასაზომად. შესაბამისად, მათი შეფარდება პროცესის aggregate CPU consumption-ს ასახავს და თავისთავად wall-time speedup-ს არ ნიშნავს.

**მონაცემები და provenance:** [ოთხივე batch-ის report/archive hash-ები და run metadata](../data/noema-005/arm64-repeat-validation-2026-11-26.json); [final-head ARM64 run 45756479611](https://github.com/maisuradzee/bibmom/actions/runs/45756479611); [final-head quality run 45756479168](https://github.com/maisuradzee/bibmom/actions/runs/45756479168); [x86-64 threaded run 45756479254](https://github.com/maisuradzee/bibmom/actions/runs/45756479254). ოთხივე raw report ZIP ჩამოიტვირთა და SHA-256-ით შემოწმდა. GitHub Actions artifacts 30 დღე ინახება; JSON-ში შენახული hash-ები provenance-ს უზრუნველყოფს, მაგრამ raw reports-ის მუდმივ არქივს არ წარმოადგენს.

**შეზღუდვები:** hosted VM-ები კონტროლირებული ლაბორატორიული აპარატურა არ არის; Ubuntu და macOS runner-ები CPU/OS/core count-ით განსხვავდება; თითო უჯრედში მხოლოდ სამი measured repetition ჩატარდა; მონაცემები სინთეზური cancellation fixture-ებია; `tracemalloc` არ ზომავს სრულ RSS-ს ან ყველა native allocation-ს. დამოუკიდებელი გარე რეცენზია არ ჩატარებულა.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.


## შედეგები

### Neumaier-state accuracy და median wall-time speedup

| Runtime | Run 45850716742 | Run 45867519546 | Accuracy თითო run-ში |
|---|---:|---:|---:|
| GIL-enabled | 0.7539× | 0.7744× | 48/48 ორივეში |
| Free-threaded | 0.9519× | 1.0181× | 48/48 ორივეში |

### მეორე run-ის ყველა მეთოდის შედეგები

| Runtime | Method | Correct | Median speedup | Median CPU/wall |
|---|---|---:|---:|---:|
| GIL-enabled | Naive scalar | 0/48 | 0.4951× | 1.012 |
| GIL-enabled | Scalar Neumaier | 42/48 | 0.7565× | 1.008 |
| GIL-enabled | Neumaier state | 48/48 | 0.7744× | 1.008 |
| Free-threaded | Naive scalar | 0/48 | 0.3682× | 2.258 |
| Free-threaded | Scalar Neumaier | 42/48 | 0.9724× | 2.412 |
| Free-threaded | Neumaier state | 48/48 | 1.0181× | 2.235 |

### FACT

- GitHub API-მ ახალი run-ის ორი artifact დააბრუნა: IDs 15140723434 და 15140468799. მათი archive SHA-256 მნიშვნელობები რეალურად ჩამოტვირთულ ZIP bytes-ს დაემთხვა.
- თითო report-ის raw SHA-256 გადამოწმდა; თითო runtime-ში 48 case იყო.
- თითო case-ის სამივე measured run-ში native thread ID-ების რაოდენობა ემთხვეოდა configured worker count-ს; ეს ადასტურებს native worker-thread-ების გამოყენებას და არა performance gain-ს.

### REPRODUCED RESULT

- ახალი raw reports-იდან დამოუკიდებლად თავიდან დაითვალა accuracy, median speedup, speedup range, median process-CPU/wall ratio, median traced allocation და CPU-parallelism threshold counts.
- ახალი free-threaded Neumaier-state median speedup იყო 1.0181×, მაგრამ range 0.7023×–1.1350×; მხოლოდ ერთი hosted run-ის სამი repetition-იანი configuration-ების median-ია ეს მნიშვნელობა.

### INFERENCE

რიცხვითი სიზუსტე ორივე run-ში სტაბილური იყო, მაგრამ performance result run-sensitive აღმოჩნდა. ერთი free-threaded median-ის 1.0-ზე ოდნავ გადაკვეთა არ წარმოადგენს სანდო აჩქარების მტკიცებულებას. CPU/wall ratio >1.0 აჩვენებს aggregate CPU consumption-ს, მაგრამ თავისთავად wall-time speedup-ს არ ნიშნავს.

### HYPOTHESIS

უფრო ხანგრძლივი workloads, native code ან memory-bandwidth-bound arrays შეიძლება განსხვავებულ პროფილს აჩვენებდეს; ეს ჯერ არ შემოწმებულა დამოუკიდებელ ფიზიკურ hardware-ზე.

### UNTESTED IDEA

წინასწარ დარეგისტრირებული benchmark იგივე input hashes-ით, მინიმუმ 20 repetition თითო cell-ში, დამოუკიდებელ physical x86-64 და ARM64 მოწყობილობებზე, RSS და memory bandwidth გაზომვით და confidence intervals-ით.

## წყაროები

- NOEMA GitHub Actions run 45850716742 — https://github.com/maisuradzee/bibmom/actions/runs/45850716742
- NOEMA GitHub Actions run 45867519546 — https://github.com/maisuradzee/bibmom/actions/runs/45867519546
- Python 3.14 threading documentation — https://docs.python.org/3.14/library/threading.html
- Python 3.14 free-threading HOWTO — https://docs.python.org/3.14/howto/free-threading-python.html
- Higham, N. J. (1993), The Accuracy of Floating Point Summation — https://doi.org/10.1137/0914050
- Ogita, T., Rump, S. M., Oishi, S. (2005), Accurate Sum and Dot Product — https://doi.org/10.1137/030601818

## შემოწმების სტატუსი

- ახალი run-ის ორივე ZIP ჩამოიტვირთა; archive SHA-256 დაემთხვა GitHub artifact metadata-ს.
- ახალი raw JSON reports SHA-256-ით შემოწმდა და ხელახლა აგრეგირდა.
- Reproduction script და mutation tests CI-ში სრულდება.
- შედეგი რჩება preliminary: მხოლოდ hosted x86-64 VM, synthetic cancellation fixtures, სამი repetition თითო configuration; დამოუკიდებელი physical-hardware replication და გარე რეცენზია არ ჩატარებულა.
- GitHub Actions artifact ZIP-ები 30 დღეში იშლება; raw report-ის compressed copy და hash-ები ამ PR-ში ინახება.

## შემდეგი ნაბიჯები

1. იგივე benchmark გაუშვი დამოუკიდებელ physical x86-64 და ARM64 მოწყობილობებზე.
2. გაზარდე measured repetitions მინიმუმ 20-მდე და გამოაქვეყნე uncertainty intervals.
3. დაამატე process RSS/native allocation და memory-bandwidth გაზომვები.
4. შეადარე pairwise, long-double და exact/superaccumulator ალგორითმები.
5. მოითხოვე დამოუკიდებელი numerical-method review; Published სტატუსი არ მიენიჭოს ამ ეტაპზე.

## 2026-11-27 — hosted ARM64 real-thread replication (Run 33)

### FACT

Four GitHub-hosted ARM64 runner/runtime cells completed: Ubuntu 24.04 ARM and macOS 15 ARM64, each with GIL-enabled and free-threaded CPython 3.14.4. Each cell ran 48 configurations × 3 measured repetitions (one warm-up), for 192 configurations and 576 measured runs overall. The exact-head benchmark workflow was [46032894362](https://github.com/maisuradzee/bibmom/actions/runs/46032894362); Quality CI was [46032894345](https://github.com/maisuradzee/bibmom/actions/runs/46032894345).

### REPRODUCED RESULT

| Hosted ARM64 runner | Runtime | Naive exact | Scalar Neumaier exact | Neumaier state exact | Median speedup: naive / scalar / state |
|---|---|---:|---:|---:|---:|
| Ubuntu 24.04 ARM | GIL | 0/48 | 42/48 | 48/48 | 0.4940× / 0.7365× / 0.7334× |
| Ubuntu 24.04 ARM | Free-threaded | 0/48 | 42/48 | 48/48 | 0.1787× / 0.6423× / 0.6401× |
| macOS 15 ARM64 | GIL | 0/48 | 42/48 | 48/48 | 0.4025× / 0.7368× / 0.8375× |
| macOS 15 ARM64 | Free-threaded | 0/48 | 42/48 | 48/48 | 0.2135× / 0.6458× / 0.6202× |

Across the four cells, Neumaier state was correctly rounded in 192/192 configurations, scalar Neumaier in 168/192 and naive scalar in 0/192. Process CPU/wall >1.05 occurred in 202/288 free-threaded samples and 4/288 GIL-enabled samples. Nevertheless, every runner/runtime cell had median speedup below 1.0 for all three methods. This workload did not show a median wall-time speedup from threading.

Artifact ZIP SHA-256 values were recomputed from the downloaded ZIP bytes and matched GitHub artifact API digests; raw report SHA-256 values are recorded in [the aggregate summary](../../data/noema-005/arm64-threaded-benchmark-summary-2026-11-27.json). Raw reports and native thread IDs are not committed.

### INFERENCE

Free-threaded builds showed aggregate CPU use beyond elapsed wall time for many multi-worker samples, but this did not translate into lower median wall time. Thread scheduling, partitioning and merge overhead appear to dominate the small deterministic cancellation workload. CPU/wall >1.05 is not a throughput or speedup metric.

### LIMITATIONS

These are hosted ARM64 CI runners, not independently controlled physical devices or external-laboratory replication. Only three measured repetitions per configuration were run. Inputs are synthetic cancellation fixtures. Memory was measured with tracemalloc peak delta only; process RSS, native allocations and DRAM bandwidth were not measured. macOS reported three process CPUs; Ubuntu reported four CPUs and a four-CPU affinity mask, so absolute cross-runner comparisons are confounded. Independent numerical review is still outstanding.

### HYPOTHESIS / UNTESTED IDEA

A larger representative workload, native reduction kernel, alternative chunk sizes or memory-bandwidth-bound arrays may change the balance. The next test should use at least 20 measured repetitions on controlled physical x86-64 and ARM64 hosts, with RSS/native allocation, DRAM bandwidth, per-thread CPU clocks and uncertainty intervals.

**NOEMA status remains preliminary; no published status is claimed.**


## 2026-11-27 Run 34 — two additional hosted x86-64 GIL/free-threaded run pairs

Two further workflow pairs were executed on the same deterministic 196,608-value cancellation workloads. Each artifact contains 48 configurations (two layouts × two partitions × four worker counts × three algorithms), three measured repetitions per configuration, and one warm-up.

| Measure | GIL-enabled (2 artifacts) | Free-threaded (2 artifacts) |
|---|---:|---:|
| Configurations | 96 | 96 |
| Measured threaded runs | 288 | 288 |
| Neumaier-state exact configurations | 32/32 | 32/32 |
| Scalar Neumaier exact configurations | 28/32 | 28/32 |
| Naive scalar exact configurations | 0/32 | 0/32 |
| CPU/wall ratio >1.05 | 0/96 | 72/96 |
| Wall-time speedup >1 | 0/96 | 0/96 |

Across all four artifacts: Neumaier-state was correctly rounded in 192/192 measured runs; scalar Neumaier in 168/192; naive scalar in 0/192. No threaded configuration exceeded its matching serial baseline.

The two run-pair medians for Neumaier-state speedup were:
- Run 46042334393: GIL-enabled AWS 0.7557×; free-threaded AWS 0.7341×.
- Run 46043232025: GIL-enabled Azure 0.7683×; free-threaded AWS 0.6839×.

The first pair is a same-runner-family comparison. The second pair is not a matched cross-mode comparison because the GIL-enabled job ran on Azure and the free-threaded job on AWS. Both remain hosted x86-64 evidence, not physical-device or independently administered replication.

Native thread counts matched requested worker counts in all configurations. Free-threaded process CPU/wall ratio >1.05 in 72/96 configurations shows concurrent CPU use, but does not imply wall-time speedup. The benchmark's tracemalloc values represent Python-traced allocations only, not process RSS or native allocator memory.

Artifact manifest:
- Run 46042334393: GIL artifact 15220093434; free-threaded artifact 15220252412.
- Run 46043232025: GIL artifact 15221052559; free-threaded artifact 15220578066.
- ZIP and source JSON SHA-256 values are frozen in data/noema-005/threaded-run-2026-11-27-summary.json.

**Interpretation:** compensation-state merging remains the only tested algorithm that preserved the correctly rounded result in every configuration. These runs show that free-threaded CPython can use multiple CPU cores on this workload, but none of the tested threaded configurations was faster than its matching serial baseline. The next step is physical x86-64/ARM64 replication with at least 20 repetitions, RSS/native allocation and DRAM-bandwidth measurement.


## 2026-11-27 Run 36 — two further hosted x86-64 artifact pairs

Two additional GIL-enabled/free-threaded workflow pairs were generated by the CPU-thread workflow during validation of Draft PRs #190 and #191. The four original ZIP artifacts were downloaded, their archive and embedded JSON SHA-256 values recomputed, the fixed input hashes checked, and the native-thread counts validated in memory. The public snapshot retains per-configuration correctness and Neumaier-state aggregates only; raw timing arrays and native thread IDs are not committed.

| Measure | GIL-enabled | Free-threaded |
|---|---:|---:|
| Reports | 2 | 2 |
| Configurations | 32 | 32 |
| Measured runs | 96 | 96 |
| Neumaier-state correctly rounded | 96/96 | 96/96 |
| Scalar Neumaier correctly rounded | 84/96 | 84/96 |
| Naive scalar correctly rounded | 0/96 | 0/96 |
| Neumaier-state CPU/wall ratio >1.05 | 0/96 runs | 72/96 runs (24/32 configurations) |

Across all four artifacts, Neumaier-state was correctly rounded in 192/192 measured runs, scalar Neumaier in 168/192 and naive scalar in 0/192.

Neumaier-state median speedup against the matching serial baseline varied by report:

| Workflow pair | Runtime | Runner family | Median speedup | Configurations >1.0 |
|---|---|---|---:|---:|
| PR #190 / run 46048328705 | GIL-enabled | AWS x86-64 | 0.765178× | 0/16 |
| PR #190 / run 46048328705 | Free-threaded | Azure x86-64 | 1.145852× | 12/16 |
| PR #191 / run 46048363044 | GIL-enabled | Azure x86-64 | 0.797322× | 0/16 |
| PR #191 / run 46048363044 | Free-threaded | Azure x86-64 | 0.947358× | 3/16 |

The free-threaded median crossed from above 1.0 to below 1.0 between two short hosted runs. The first pair also used different runner families across runtime modes; the second used the same Azure runner family but separate hosted jobs/VMs. This is run-sensitive evidence, not a robust or portable speedup claim.

Native thread counts matched the requested worker counts in all 192 configurations. For Neumaier-state, process CPU/wall ratio >1.05 occurred in 72/96 free-threaded measured runs (24/32 configurations) and 0/96 GIL-enabled runs. This indicates concurrent CPU use, not lower wall time by itself.

Median tracemalloc peak for Neumaier-state was 25,353 bytes (PR190 GIL), 276,809 bytes (PR190 free-threaded), 25,425 bytes (PR191 GIL) and 277,669 bytes (PR191 free-threaded). Tracemalloc is Python-traced allocation only; it is not process RSS, native allocator memory or DRAM bandwidth.

The frozen per-configuration aggregate and original archive/report hashes are in [the Run 36 snapshot](../../data/noema-005/threaded-run36-artifact-snapshot.json). Reproduction: `python scripts/reproduce_noema005_run36_threaded.py --check`. Supplying the original ZIPs through `--artifacts-dir` additionally verifies the original archive/report digests and reconstructs the sanitized snapshot.

### Evidence status and limitations

**REPRODUCED RESULT:** four exact hosted x86-64 workflow artifacts, 192 configurations and 576 measured runs. The benchmark workflows were triggered by unrelated Draft PR validation rather than a separately planned experiment. Only two synthetic cancellation layouts, 65,536 repeats, three measured repetitions/configuration and four CPUs of affinity were used. No physical x86-64 or ARM64 host, representative application workload, process RSS/native allocation, DRAM bandwidth, CPU-frequency or context-switch counters were measured. No causal or cross-architecture claim is made.

**INFERENCE:** free-threaded CPython used multiple CPU cores on many configurations, but that concurrency did not yield a stable wall-time advantage for the compensated state reduction.

**NEXT TEST:** run at least 20 measured repetitions/configuration on controlled physical x86-64 and ARM64 systems, with representative numerical workloads, RSS/native allocation, DRAM bandwidth and uncertainty intervals.

**NOEMA status remains preliminary; no Published status is claimed.**


**Run 36 public-evidence minimization note:** the sanitized snapshot retains only the coarse hosted Linux provider family (`aws`/`azure`) needed to distinguish runner pools. Kernel release and glibc build strings from raw `platform` metadata are excluded; raw artifacts remain outside the public repository.


## Run 38 — experiment 002: worker-local math.fsum partials and ARM64 hosted replication

### მეთოდოლოგია

Experiment 002 used CPython 3.14.10 in GIL-enabled and free-threaded builds across three GitHub-hosted runner cells: x86-64 Ubuntu, ARM64 Ubuntu and ARM64 macOS. Each cell contained 64 configurations (2 layouts × 4 worker counts × 2 partition strategies × 4 methods), one warmup and three measured repetitions: 192 measured runs/cell, 1,152 overall.

Compared methods:
- naive scalar reduction;
- scalar Neumaier partials;
- full Neumaier compensation-state merge;
- worker-local math.fsum scalar partials.

The last method is intentionally distinct from one global math.fsum call: each worker returns one rounded scalar, then the partial scalars are merged. Python's documentation describes math.fsum's partial-sum approach and its floating-point/rounding assumptions: https://docs.python.org/3.14/library/math.html#math.fsum.

### Accuracy

| Method | Correctly rounded measured runs |
|---|---:|
| Naive scalar | 0/288 |
| Scalar Neumaier partials | 252/288 |
| Full Neumaier state | 288/288 |
| Worker-local math.fsum scalar partials | 252/288 |

Both scalar-partial methods failed in the same deterministic stress case in every cell: grouped-cancellation layout, contiguous partition, worker counts 2 and 8; each affected configuration failed all three repetitions. This is evidence that accurate worker-local scalar sums do not preserve all residual information across every partition boundary. The full compensation state preserved the exact reference in these tested cases.

### Runtime

No threaded configuration beat its matching serial baseline: 0/384. The range of per-cell median speedups was:

| Method | Minimum to maximum median speedup across six cells |
|---|---:|
| Naive scalar | 0.185162–0.568829 |
| Scalar Neumaier partials | 0.571729–0.771480 |
| Full Neumaier state | 0.705763–0.773336 |
| Worker-local math.fsum partials | 0.050252–0.193933 |

The median process CPU/wall ratio exceeded 1.05 in 34–36 of 48 free-threaded configurations per method, but in 0/48 GIL-enabled configurations. This indicates concurrent CPU use in many free-threaded cases; it does not demonstrate lower wall time. The worker-local fsum scalar-partial method was especially slow in this matrix.

### Public evidence and provenance

The six public workflow artifacts were sanitized before upload. Raw native thread IDs and detailed host-build strings were removed only after the sanitizer validated distinct native thread identity for each worker/repetition. The six artifact ZIP SHA-256 digests and six sanitized report JSON SHA-256 digests are frozen in [experiment-002-summary.json](../../data/noema-005/experiment-002-summary.json). Run [x86-64](https://github.com/maisuradzee/bibmom/actions/runs/46064056998), [ARM64](https://github.com/maisuradzee/bibmom/actions/runs/46064056947), and [legacy-artifact cleanup](https://github.com/maisuradzee/bibmom/actions/runs/46064057021) provide the workflow records. GitHub confirmed that the six targeted prior unsanitized artifact lists are empty.

Reproduction:
- Summary/schema and aggregate arithmetic: `python scripts/reproduce_noema005_experiment_002.py --check`.
- Full artifact reproduction: download the six sanitized ZIPs into one directory, name them `github-actions-artifact-<artifact_id>.zip`, then run `python scripts/reproduce_noema005_experiment_002.py --artifact-dir <directory>`.

### Evidence status and limitations

**REPRODUCED RESULT:** six sanitized hosted reports, 384 configurations and 1,152 measured runs; artifact and report hashes were checked against GitHub artifact metadata.

**INFERENCE:** full Neumaier compensation state preserved the reference more reliably than either scalar-partial method in this cancellation-heavy synthetic matrix. Free-threaded execution used multiple CPUs in many configurations, but no threaded configuration was faster than its matching serial baseline.

**LIMITATIONS:** three measured repetitions are exploratory; hosted VMs are not physical-device replication; runner families are not controlled same-hardware comparisons; tracemalloc is not process RSS/native allocation or DRAM bandwidth; no representative production workload, GPU, network-distributed reduction or Windows run was tested.

**Status remains preliminary. No Published status is claimed.**
