# NOEMA-2026-005 — რეალური CPU threads-ის reduction benchmark

- **ID:** NOEMA-2026-005 (კვლევის გაგრძელება; ახალი დამოუკიდებელი კვლევის ID არ იქმნება)
- **სტატუსი:** draft — რეალური thread benchmark დასრულებულია CPython 3.14.4 GIL-enabled და 3.14.4t free-threaded რეჟიმებში; სხვა არქიტექტურის დამოუკიდებელი გამეორება დარჩენილია
- **თარიღი:** 2026-11-25
- **სფერო:** რიცხვითი ანალიზი, პარალელური გამოთვლები, პროგრამული სისტემები
- **ავტორი/მომზადების სისტემა:** NOEMA research automation

## საკვლევი კითხვა

ინარჩუნებს თუ არა Neumaier-ის თითოეული worker-ის `(sum, compensation)` მდგომარეობის გადაცემა სწორად დამრგვალებულ ჯამს რეალური OS threads-ის გამოყენებისას? როგორ განსხვავდება CPU დრო, wall-clock დრო და Python-ის მიერ ტრეკირებული მეხსიერება GIL-იან და free-threaded CPython-ში?

## მოკლე შეჯამება

NOEMA-005-ის წინა sharded reduction იყო დეტერმინისტული სიმულაცია და არა რეალური thread benchmark. ამ დამატებაში გამოიყენება `ThreadPoolExecutor`, `threading.Barrier` და native thread ID-ები, რათა დადასტურდეს, რომ თითოეული worker ცალკე OS thread-ზე გაეშვა. შედარებულია naive scalar partial, Neumaier scalar partial და Neumaier `(sum, compensation)` state merge.

GitHub Actions-ზე ორი ცალკე Ubuntu 24.04 x86_64 runner-ით შესრულდა CPython 3.14.4 GIL-enabled და 3.14.4t free-threaded benchmark. თითო runtime-ზე 48 configuration × 3 repetition (144 run) შესრულდა. ყველა worker-ის native thread ID განსხვავებული იყო. Neumaier compensation-state merge-მა 48/48 configuration-ში ზუსტი binary64 reference მიიღო ორივე რეჟიმში. Scalar Neumaier partial-მა 42/48, ხოლო naive scalar-მა 0/48. GIL-enabled რეჟიმში CPU-time/wall-time >1.05 შემთხვევა იყო 0/144; free-threaded რეჟიმში — 108/144, ყველა multi-worker configuration-ზე. მიუხედავად რეალური CPU პარალელიზმისა, არც ერთ threaded configuration-ს serial baseline-ზე wall-time speedup არ მიუღია; საუკეთესო მედიანური speedup იყო 0.777 GIL-enabled და 0.803 free-threaded რეჟიმში.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

წინა სიმულაციამ აჩვენა, რომ scalar partial-მა შეიძლება worker-ის შიდა კომპენსაცია დაკარგოს. რეალურ thread pool-ში ამას ემატება GIL-ის რეჟიმი, thread scheduling, CPU quota და runtime overhead. ამიტომ მხოლოდ შუალედური ჯამების მათემატიკური სიმულაცია საკმარისი არ არის შესრულების ან რეალური threading-ის დასადასტურებლად.

## წყაროები

1. **Sam Gross — PEP 703, “Making the Global Interpreter Lock Optional in CPython.”** Python Enhancement Proposals, PEP 703. შეიქმნა 2023-01-09; Steering Council-ის მიღების გადაწყვეტილება 2023-10-24. https://peps.python.org/pep-0703/ — პირველადი ტექნიკური სპეციფიკაცია, რომელიც აღწერს GIL-ის შეზღუდვას და free-threaded build-ის მიზანს. წვდომა: 2026-11-25.
2. **Thomas Wouters, Matt Page და Sam Gross — PEP 779, “Criteria for supported status for free-threaded Python.”** შეიქმნა 2025-03-13; Steering Council-ის resolution: 2025-06-16. https://peps.python.org/pep-0779/ — პირველადი სპეციფიკაცია, რომელმაც Python 3.14-ის free-threaded build ოფიციალურად მხარდაჭერილ, მაგრამ არჩევით რეჟიმად განსაზღვრა. წვდომა: 2026-11-25.
3. **Python Software Foundation — Python 3.14.0 release.** გამოქვეყნდა 2025-10-07. https://www.python.org/downloads/release/python-3140/ — ოფიციალური გამოშვების ჩანაწერი ადასტურებს Python 3.14-ის free-threaded მხარდაჭერის სტატუსს. წვდომა: 2026-11-25.
2. **Python Software Foundation — Python 3.14 HOWTO, “Python support for free threading.”** გამოცემის ცალკე თარიღი გვერდზე მითითებული არ არის. https://docs.python.org/3.14/howto/free-threading-python.html — აღწერს free-threaded build-ს, `sys._is_gil_enabled()`-ს და იმ შემთხვევებს, როდესაც extension-მა შეიძლება GIL ხელახლა ჩართოს. წვდომა: 2026-11-25.
3. **Python Software Foundation — Python 3.14 Library Reference, `threading`.** გამოცემის ცალკე თარიღი გვერდზე მითითებული არ არის. https://docs.python.org/3.14/library/threading.html — აღწერს ThreadPoolExecutor-სა და GIL-ის გავლენას CPU-bound Python კოდზე. წვდომა: 2026-11-25.
4. **Python Software Foundation — Python 3.14 Library Reference, `time`.** https://docs.python.org/3.14/library/time.html — `perf_counter_ns()` და process-wide `process_time_ns()` დროის საზომები. გამოცემის ცალკე თარიღი მითითებული არ არის. წვდომა: 2026-11-25.
5. **Python Software Foundation — Python 3.14 Library Reference, `tracemalloc`.** https://docs.python.org/3.14/library/tracemalloc.html — Python allocation tracing და peak memory; არ უდრის მთლიანი RSS-ის გაზომვას. გამოცემის ცალკე თარიღი მითითებული არ არის. წვდომა: 2026-11-25.
6. **GitHub Actions — actions/setup-python, Advanced usage.** https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md — free-threaded ვერსიის `t` suffix-ის გამოყენება. ცოცხალი დოკუმენტაციაა; გამოცემის თარიღი მითითებული არ არის. წვდომა: 2026-11-25.

## მტკიცებულებები

### FACT — დადასტურებული წყაროებით

- CPython-ის ჩვეულებრივ GIL-enabled build-ში ერთდროულად მხოლოდ ერთი thread ასრულებს Python bytecode-ს; thread-ები მაინც ქმნის concurrency-ს და სასარგებლოა I/O-bound სამუშაოებისთვის.
- CPython 3.13-დან ხელმისაწვდომია free-threaded build; Python 3.14-დან ის ოფიციალურად მხარდაჭერილი, მაგრამ არჩევითი build-ია (PEP 779). GIL-ის ფაქტობრივი მდგომარეობა მაინც უნდა შემოწმდეს გაშვებისას, რადგან build-ის მხარდაჭერა თავისთავად არ ნიშნავს, რომ GIL გამორთულია.
- `process_time_ns()` ზომავს მიმდინარე პროცესის user/system CPU დროს, ხოლო `perf_counter_ns()` გამოიყენება elapsed wall time-ისთვის.
- `tracemalloc` Python-ის მიერ ტრეკირებულ allocation-ებს ზომავს და არა სრულ process RSS-ს ან ყველა native allocation-ს.

### REPRODUCED RESULT — GitHub Actions რეალური thread benchmark

- **გარემო A:** CPython 3.14.4, GIL enabled; Ubuntu 24.04 runner, Linux x86_64, 4 CPU affinity.
- **გარემო B:** CPython 3.14.4 free-threaded build, GIL disabled; Ubuntu 24.04 runner, Linux x86_64, 4 CPU affinity.
- თითო runtime-ზე: N=65,536; თითო layout 196,608 binary64 მნიშვნელობა; ზუსტი ჯამი 65,536.
- input SHA-256 ორივე runtime-ზე დაემთხვა: triplet order `e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291`; grouped cancellation `16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee`.
- worker-ები: 1, 2, 4, 8; partition: contiguous და round-robin; 3 მეთოდი; warmup 1; measured repetitions 3.
- თითო runtime-ზე 48 configuration და 144 measured run. ყველა run-ში configured worker-ების რაოდენობა ემთხვეოდა განსხვავებული native thread ID-ების რაოდენობას.

**სიზუსტე (თითო runtime):**

| მეთოდი | Triplet order | Grouped cancellation | სულ |
|---|---:|---:|---:|
| Naive scalar partial | 0/24 | 0/24 | 0/48 |
| Neumaier scalar partial | 24/24 | 18/24 | 42/48 |
| Neumaier compensation state | 24/24 | 24/24 | **48/48** |

Neumaier scalar partial-ის ჩავარდნები დაფიქსირდა grouped cancellation-ის contiguous partition-ზე 2 და 8 worker-ის კონფიგურაციებში. Compensation-state merge-მა ყველა ამ სინთეზურ კონფიგურაციაში სწორი შედეგი შეინარჩუნა.

**CPU concurrency და wall time:**

| მაჩვენებელი | GIL enabled | Free-threaded |
|---|---:|---:|
| CPU-time/wall-time > 1.05 | 0/144 | 108/144 |
| 2 worker-ის samples > 1.05 | 0/36 | 36/36 |
| 4 worker-ის samples > 1.05 | 0/36 | 36/36 |
| 8 worker-ის samples > 1.05 | 0/36 | 36/36 |
| საუკეთესო threaded/serial speedup | 0.777 | 0.803 |

Free-threaded Neumaier-state median CPU-time/wall-time ratio worker count 1/2/4/8-ზე იყო 0.99 / 1.95 / 3.52 / 3.47. ეს მიუთითებს პროცესის შიგნით მრავალბირთვიან CPU შესრულებაზე, მაგრამ wall-time speedup არ დაფიქსირდა: ამ workload-ზე ThreadPoolExecutor-ის startup/scheduling და Python-level reduction overhead-მა სარგებელი გადაფარა.

**Tracemalloc peak (Neumaier state, median bytes; არა RSS):**

- GIL-enabled, 1/2/4/8 worker: 11,535 / 18,490 / 32,216 / 60,284.
- Free-threaded, 1/2/4/8 worker: 95,149 / 185,878 / 366,372 / 731,384.

**არტეფაქტები და provenance:**

- Actions run: [45548551086](https://github.com/maisuradzee/bibmom/actions/runs/45548551086).
- GIL-enabled artifact ID: `14992217331`; raw JSON SHA-256: `abf11340570a1b251898cfe05bdf1c17bdf5a81e7f621454bef81dd6dd665dd9`.
- Free-threaded artifact ID: `14992547298`; raw JSON SHA-256: `8187a322e27e9ea4e24c970a7cb7677676a6d81fccc005144ee3d7147bf793db`.
- შეჯამებები: `data/noema-005/threaded-benchmark-gil-enabled-2026-11-25.json` და `data/noema-005/threaded-benchmark-free-threaded-2026-11-25.json`.

ეს არის ორი ცალკე runner-ის შედეგი, მაგრამ ორივე Ubuntu x86_64 და ერთნაირი 4-CPU affinity აქვს; ეს არ არის დამოუკიდებელი არქიტექტურული გამეორება.

## კონკურენტი ახსნები

- ThreadPoolExecutor-ის სიჩქარის ცვლილება შეიძლება გამოწვეული იყოს thread startup/scheduling overhead-ით და არა თვითონ შეკრების ალგორითმით.
- process CPU დროის ზრდა შეიძლება შეზღუდოს runner-ის CPU quota-მ ან სხვა პროცესების დატვირთვამ.
- GIL-ის გამორთვისასაც შეიძლება არსებობდეს lock contention, memory bandwidth bottleneck ან runtime overhead.
- scalar partial-ის სიზუსტის დაკარგვა დამოკიდებულია მონაცემთა დაყოფასა და მიმდევრობაზე; ის ყველა შეყვანაზე ერთნაირად არ გამოვლინდება.

## ჰიპოთეზა

**HYPOTHESIS — ამ მონაცემებზე მხარდაჭერილია:** free-threaded CPython-ში Neumaier compensation-state merge ინარჩუნებს სწორად დამრგვალებულ შედეგს ყველა შემოწმებულ worker count/partition-ზე; multi-worker შემთხვევაში process CPU time აღემატება wall time-ს. ეს არ ამტკიცებს უნივერსალურ სიზუსტეს ან wall-time speedup-ს სხვა workload-ებზე.

## შემოწმების მეთოდი

კოდი: `scripts/benchmark_noema005_threaded_reduction.py`.

ტესტები: `tests/test_benchmark_noema005_threaded_reduction.py`.

პროტოკოლი: `data/noema-005/threaded-benchmark-protocol.json`.

- ორი input layout: `[1e16, 1, -1e16]` triplet order და grouped cancellation.
- სრული CI run-ის default N=65,536; თითო layout 196,608 binary64 მნიშვნელობა; ზუსტი ჯამი N.
- worker count: 1, 2, 4, 8; partition: contiguous და round-robin.
- მეთოდები: naive scalar partial, Neumaier scalar partial, Neumaier state merge.
- serial baseline: naive, Neumaier, math.fsum.
- runtime matrix: CPython 3.14.4 GIL-enabled და CPython 3.14.4t free-threaded; ორივე Ubuntu 24.04 runner-ზე. Python 3.14 free-threaded build ოფიციალურად მხარდაჭერილია როგორც optional build (PEP 779).
- warmup 1; measured repetitions 3; შემთხვევითი seed არ გამოიყენება, რადგან input deterministic-ია.
- თითოეული worker-ის native thread ID ინახება; run ჩაიშლება, თუ worker-ები ცალკე native thread-ებზე არ გაეშვა.
- იზომება median wall time, process CPU time, მათი შეფარდება და tracemalloc peak delta.
- performance threshold არ გამოიყენება; შედეგები გარემოსთან ერთად უნდა განიმარტოს.

## შედეგები და ინტერპრეტაცია

- **REPRODUCED RESULT:** ადგილობრივი GIL-enabled control run აღწერილია ზემოთ.
- **REPRODUCED RESULT:** GitHub Actions-ის CPython 3.14.4 და 3.14.4t სრული benchmark დასრულდა; ორივე runtime-ზე 48 configuration × 3 repetitions შესრულდა და ყველა configured worker-ის native thread identity დადასტურდა.
- **INFERENCE:** scalar worker partial-ების შენახვა შეიძლება არ იყოს საკმარისი, რადგან worker-ის შიდა compensation იკარგება; state merge ამ ინფორმაციას ინარჩუნებს.

## შემოწმების სტატუსი

- ადგილობრივი CPython 3.13.5 GIL-enabled control: შესრულებულია; 36 configuration, სრული raw JSON SHA-256 შეჯამებაშია.
- ადგილობრივი unit tests: 5/5 PASS; მცირე smoke run: 24 configuration.
- პირველი Actions attempt `45548429179`: benchmark source-ში JSON newline literal-ის syntax error აღმოჩნდა; სრული benchmark არ შესრულებულა. გასწორებულია.
- პირველი repository CI attempt `45548429197`: draft validator-მა მოითხოვა ზუსტი headings `წყაროები`, `შემოწმების სტატუსი`, `შემდეგი ნაბიჯები`; დამატებულია.
- საწყის კვლევით head `93bb712b889cc9ffb5624b647480abb3291264d8`-ზე repository quality/site CI run `45548551153` და thread benchmark run `45548551086` წარმატებით დასრულდა; ეს შედეგები შემდგომი საბოლოო head-ის შემოწმებას არ ანაცვლებს.
- ორივე runtime-ის raw JSON artifact გადმოწერილია, SHA-256 შემოწმებულია და შეჯამებები repository branch-ზეა დამატებული. საბოლოო PR #21 head `00084792c6d3265b7b046e013ece362f76cf88f6`-ზე quality/site run [45551791989](https://github.com/maisuradzee/bibmom/actions/runs/45551791989) წარმატებით დასრულდა: **176 Python test**, frozen-result reproduction, schema/catalog validation, site build და draft/publication boundary PASS. იმავე head-ის actual CPU-thread run [45551791998](https://github.com/maisuradzee/bibmom/actions/runs/45551791998)-მა GIL-enabled და free-threaded ორივე job წარმატებით დაასრულა. squash merge commit `e84f2b9679c923c673319fc28fc6da5d1e021702`-ზე main quality run [45551962844](https://github.com/maisuradzee/bibmom/actions/runs/45551962844) ასევე SUCCESS იყო.
- PR #21 squash-ით გაერთიანდა 2026-11-25; merge commit: `e84f2b9679c923c673319fc28fc6da5d1e021702`. მომხმარებლის preprint და კატალოგის ჩანაწერი კვლავ `preliminary` სტატუსითაა. Pages deployment run [45551962965](https://github.com/maisuradzee/bibmom/actions/runs/45551962965) წარმატებით დასრულდა; `published` სტატუსი არ გამოიყენება და დამოუკიდებელი გარე რეცენზია არ დასრულებულა.

## შეზღუდვები და გაურკვევლობები

- მხოლოდ ხელოვნური cancellation მონაცემებია გამოყენებული; რეალური სამეცნიერო ან ფინანსური dataset არ გამოიყენება.
- ამ ციკლის CI benchmark არის Ubuntu x86_64-ზე; ARM, Windows და macOS რეალური threaded benchmark არ ჩატარებულა. ორივე job CPython 3.14.4-ზე იყო; 2026-11-25-ისთვის უახლესი 3.14 patch 3.14.10 და უახლესი major 3.15.2 იყო, ამიტომ უახლეს patch/major-ზე გამეორება დარჩენილია.
- free-threaded build ოფიციალურად მხარდაჭერილია Python 3.14-დან, მაგრამ მისი წარმადობა და მესამე მხარის extension-ების თავსებადობა workload-ზეა დამოკიდებული; GIL შეიძლება runtime-ზე ან extension-ის იმპორტისას ხელახლა ჩაირთოს.
- thread pool-ის შექმნისა და scheduling-ის ხარჯი გაზომვაში შედის.
- process CPU დრო პროცესის საერთო დროა და შეიძლება runner-ის scheduling/CPU quota-ით შეიცვალოს.
- tracemalloc არ ზომავს მთლიან RSS-ს.
- GPU, NumPy/BLAS, OpenMP, multiprocessing და network-distributed execution არ შემოწმებულა.

## ეთიკა და უსაფრთხოება

მონაცემები სინთეზურია და პირად/სენსიტიურ ინფორმაციას არ შეიცავს. გარე მონაცემთა ლიცენზია არ გამოიყენება. benchmark არ უნდა ჩაითვალოს კრიტიკული სისტემის სიზუსტის ან წარმადობის გარანტიად.

## დასკვნა

რეალური native threads შემოწმდა GIL-enabled და free-threaded CPython-ში. GIL-enabled რეჟიმში CPU-bound Python loop-მა მრავალბირთვიანი CPU concurrency არ აჩვენა; free-threaded რეჟიმში 2/4/8 worker-ით CPU-time/wall-time 1.05-ს ყველა multi-worker configuration-ზე გადააჭარბა. მიუხედავად ამისა, threaded wall-time serial baseline-ზე უკეთესი არ გახდა. Neumaier compensation-state merge-მა 48/48 synthetic configuration-ში სწორი შედეგი შეინარჩუნა; scalar partial-მა grouped cancellation-ის ორ contiguous worker-count ჯგუფში ინფორმაცია დაკარგა. ეს არის კონკრეტული synthetic workload-ის შედეგი და არა უნივერსალური გარანტია.

## შემდეგი ნაბიჯები

1. იგივე პროტოკოლი გაუშვი უახლეს CPython 3.14.10/3.14.10t და 3.15.2/3.15.2t ვერსიებზე.
2. დაამატე დამოუკიდებელი ARM ან სხვა OS architecture run.
3. შეადარე რეალური workload-ები და არა მხოლოდ cancellation microbenchmark; შეამოწმე native C/OpenMP ან სხვა შემცირების მექანიზმები.
4. memory-ისთვის დაამატე RSS/native allocation საზომი და CPU quota-ის ზუსტი metadata.
5. უახლეს CPython patch/major და ARM/სხვა OS შედეგების შემდეგ განაახლე preliminary გვერდი და კატალოგი მხოლოდ მაშინ, თუ ახალი მტკიცებულება დასკვნას ცვლის; published სტატუსი დამოუკიდებელი რეცენზიის გარეშე არ მიენიჭოს.

## ცვლილებების ისტორია

- 2026-11-25 — დაემატა რეალური ThreadPoolExecutor benchmark, GIL-mode detection, native thread ID verification, CPU/wall timing, memory tracing და GIL-enabled local control JSON.
- 2026-11-25 — PR #21-ის head `00084792c6d3265b7b046e013ece362f76cf88f6`-ზე quality/site (176 tests) და actual CPU-thread benchmark workflows წარმატებით დასრულდა; PR squash-ით merged commit `e84f2b9679c923c673319fc28fc6da5d1e021702`-ში. Pages deployment run `45551962965` წარმატებით დასრულდა.


## Repeat run — 2026-11-26, workflow 45850716742

The exact PR-70 head `48bf7aeea44af78ee85f97463a15894330ddba4c` triggered a fresh hosted run of the existing real-thread workflow. Both GIL-enabled and free-threaded CPython 3.14.4 jobs completed successfully on the same hosted x86-64 runner family (four available CPUs). Each mode executed 48 threaded cases, three repetitions per case, with distinct native thread IDs.

### REPRODUCED RESULT — accuracy and median wall-time speedup

| Runtime | Method | Correct runs | Median speedup vs matching serial |
|---|---|---:|---:|
| GIL enabled | Naive scalar | 0/48 | 0.4918× |
| GIL enabled | Scalar Neumaier | 42/48 | 0.7443× |
| GIL enabled | Neumaier (sum, correction) state merge | 48/48 | 0.7539× |
| Free-threaded | Naive scalar | 0/48 | 0.3183× |
| Free-threaded | Scalar Neumaier | 42/48 | 0.9947× |
| Free-threaded | Neumaier (sum, correction) state merge | 48/48 | 0.9519× |

The free-threaded state-merge cases used more process CPU time than wall time (median process-CPU/wall ratio 2.084), which is evidence of parallel CPU consumption in this synthetic run, **not** evidence of end-to-end acceleration. Its median wall-time speedup remained below 1; a few individual free-threaded cases exceeded 1, but the per-method median did not. No general speedup is claimed.

### Provenance

- GIL-enabled artifact: `noema005-threaded-gil-enabled`, artifact ID `15132333526`; ZIP SHA-256 `b1b84fa96480fd989e6b866800004146f36a8c08b05859d3678cf32a3c094be4`; raw report SHA-256 `b984326a68847e2fac9b3c205a4ef4b3fb59d10e27210460c2061fc9c8ba8eaa`.
- Free-threaded artifact: `noema005-threaded-free-threaded`, artifact ID `15132228583`; ZIP SHA-256 `f8adbcd890c436267b6efb2f907b0d1b210d3c1f4e6ea7f2ac7500f987363f41`; raw report SHA-256 `f23804a230c96358082a6ae6189761e0a571ae4fadc241a4456cccddeb9b24e1`.
- Both artifacts were retained by GitHub Actions until 2026-12-26. Frozen aggregate metadata is stored in `data/noema-005/threaded-rerun-2026-11-26.json` and checked by `scripts/validate_noema005_threaded_rerun.py`.

### INFERENCE and limitations

Free-threaded CPython exposed parallel CPU use but did not produce a median wall-time improvement for this workload. This is consistent with overhead and workload-size limitations, but does not identify the bottleneck. The experiment uses a single hosted virtual x86-64 runner, not independently selected physical hardware; the synthetic cases do not represent memory-bandwidth-bound production arrays. Traced Python allocation peaks are not process RSS and must not be compared directly across runtime modes. The research remains **preliminary** pending independent numerical-method review and replication on independent physical x86-64 and ARM64 systems.

