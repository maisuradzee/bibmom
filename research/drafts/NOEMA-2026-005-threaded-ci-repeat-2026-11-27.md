# NOEMA-2026-005 — hosted GIL-enabled and free-threaded CPU-thread repeat

- **ID:** NOEMA-2026-005-REAL-THREADS-002
- **სტატუსი:** draft / preliminary evidence review
- **თარიღი:** 2026-11-27
- **სფერო:** compensated floating-point reduction · actual CPython worker threads

## საკვლევი კითხვა

შეუძლია თუ არა Python-ის free-threaded build-ს ამ კონკრეტულ synthetic reduction workload-ზე რეალური მრავალბირთვიანი CPU execution-ის მიღწევა და იძლევა თუ არა ეს wall-time speedup-ს matching serial baseline-თან შედარებით? რომელი reduction state ინარჩუნებს correctly-rounded result-ს ყველა შემოწმებულ კონფიგურაციაში?

## მეთოდი ან ექსპერიმენტის გეგმა

წყარო: GitHub Actions workflow run [46006107242](https://github.com/maisuradzee/bibmom/actions/runs/46006107242), head `fdfc4d390fdb7cfc45f5879dbc699c3d2165a1e9`. ორი artifact: GIL-enabled #15201571617 და free-threaded #15201906516.

თითოეულ runtime-ში შესრულდა 48 კონფიგურაცია × 3 გამეორება = 144 run. მატრიცა მოიცავდა 1, 2, 4 და 8 worker-ს; `triplet_order` და `grouped_cancellation` input layout-ებს; `contiguous` და `round_robin` partition-ებს; naive scalar, Neumaier scalar და Neumaier state მეთოდებს. თითოეულ input-ში იყო 196,608 binary64 მნიშვნელობა და ზუსტი ჯამი 65,536.

CI-მ გადაამოწმა თითო worker-ის განსხვავებული native thread identity; საჯარო snapshot-ში შენარჩუნებულია მხოლოდ native thread count, ხოლო thread ID-ები და დეტალური host/kernel build სტრიქონები ამოღებულია. Artifact ZIP და source JSON SHA-256-ები frozen report-ებშია ჩაწერილი.

## შედეგები

| Runtime / method | Correctly rounded | Median speedup vs serial | Median process-CPU / wall |
|---|---:|---:|---:|
| GIL — naive scalar | 0/48 | 0.4754× | 1.0077 |
| GIL — Neumaier scalar | 42/48 | 0.7616× | 1.0075 |
| GIL — Neumaier state | 48/48 | 0.7577× | 1.0078 |
| Free-threaded — naive scalar | 0/48 | 0.1634× | 2.8119 |
| Free-threaded — Neumaier scalar | 42/48 | 0.7089× | 2.7220 |
| Free-threaded — Neumaier state | 48/48 | 0.7024× | 2.6761 |

Neumaier state-ის worker-count მედიანები:

| Worker count | GIL CPU/wall | GIL speedup | Free-threaded CPU/wall | Free-threaded speedup |
|---:|---:|---:|---:|---:|
| 1 | 1.0013 | 0.7839× | 0.9929 | 0.6814× |
| 2 | 1.0049 | 0.7594× | 1.9614 | 0.6150× |
| 4 | 1.0122 | 0.7433× | 3.8261 | 0.6963× |
| 8 | 1.0174 | 0.7350× | 3.5207 | 0.7001× |

ყველა 96 threaded configuration-ის speedup matching serial baseline-ზე ნაკლები იყო. Free-threaded 4-worker შემთხვევებში process-CPU/wall დაახლოებით 3.83 მიუთითებს aggregate CPU concurrency-ზე, მაგრამ ამ workload-ში wall-time აჩქარება არ მიღებულა. GIL-enabled build-ში CPU/wall დაახლოებით 1.0 დარჩა.

Neumaier state-მა ორივე runtime-ში 48/48 correctly-rounded run მიიღო. Neumaier scalar-მა 42/48, naive scalar-მა 0/48. ეს შედეგი ეხება მხოლოდ ამ ორ synthetic input layout-ს.

Neumaier state-ის median `tracemalloc` peak იყო 25,413 bytes GIL-enabled და 276,509 bytes free-threaded. ეს არის Python allocation tracing და არა RSS/native memory; runner-ებიც განსხვავებული იყო, ამიტომ footprint-ის cross-runtime შედარებად არ უნდა ჩაითვალოს.

## მტკიცებულებები

- **FACT:** PEP 703 განსაზღვრავს CPython-ის optional-GIL build configuration-ს; ეს არ არის ავტომატური speedup-ის გარანტია. https://peps.python.org/pep-0703/
- **FACT:** Python 3.14-ის free-threading დოკუმენტაცია აღწერს GIL-ის runtime-ზე ხელახლა ჩართვის შესაძლებლობას და extension compatibility-ის შეზღუდვებს. https://docs.python.org/3.14/howto/free-threading-python.html
- **REPRODUCED RESULT:** ორივე GitHub Actions artifact-ის 48-კონფიგურაციიანი ანგარიშები schema-ით და raw sample median-ების ხელახალი გამოთვლით მოწმდება; თითო runtime-ში 144 run.
- **INFERENCE:** free-threaded build-მა ამ Python-level workload-ზე CPU concurrency უზრუნველყო, მაგრამ thread scheduling/merge/allocation overhead-მა serial baseline-ზე უკეთესი wall-time შედეგი არ მოიტანა.
- **HYPOTHESIS:** უფრო დიდი chunk-ები ან native/vectorized reduction kernel შეიძლება overhead-ს უკეთ ამორტიზებდეს; ეს ჯერ არ შემოწმებულა.
- **UNTESTED IDEA:** იგივე exact-reference workload-ის შედარება C/OpenMP და vectorized implementation-ებთან, RSS/native allocation და DRAM bandwidth გაზომვით.

## შეზღუდვები და გაურკვევლობები

- ორივე რეჟიმი hosted x86-64 runner-ზე შესრულდა და არა დამოუკიდებლად კონტროლირებულ ფიზიკურ მოწყობილობაზე.
- GIL და free-threaded რეჟიმები სხვადასხვა hosted runner image-ზე გაეშვა; ეს same-machine controlled comparison არ არის.
- runner-ს 4 CPU affinity ჰქონდა; 8-worker კონფიგურაციები oversubscribed იყო.
- თითო კონფიგურაციას მხოლოდ 3 გამეორება აქვს; confidence interval და დამოუკიდებელი გარე გამეორება არ არსებობს.
- input-ები synthetic cancellation patterns-ია და არა რეალური სამეცნიერო workload.
- `tracemalloc` არ ზომავს RSS-ს, native allocations-ს ან DRAM bandwidth-ს.
- perf_event task-clock და hardware counters არ გაზომილა.
- ახალი physical x86-64 ან ARM64 ექსპერიმენტი ამ ჩანაწერში არ არის.

## წყაროები

1. Gross, S. (2023). PEP 703 — Making the Global Interpreter Lock Optional in CPython. https://peps.python.org/pep-0703/
2. Python Software Foundation. Python 3.14 — Python support for free threading. https://docs.python.org/3.14/howto/free-threading-python.html
3. GitHub Actions workflow run 46006107242 and artifacts 15201571617 / 15201906516; checksums embedded in frozen snapshots.

## შემდეგი ნაბიჯები

1. დამოუკიდებელი physical x86-64 და ARM64 გამეორება, მინიმუმ 20 repetitions per configuration.
2. C/OpenMP and vectorized kernels with identical exact-reference inputs.
3. RSS/native allocation, DRAM bandwidth, task-clock, context-switch and CPU-frequency evidence.
4. Chunk-size and reduction-tree sweeps with confidence intervals.
5. Independent numerical-method review before any publication status.

## შემოწმების სტატუსი

- Frozen sanitized snapshots: GIL-enabled და free-threaded; 48 cases და 144 runs თითო რეჟიმში.
- Reproducer: artifact ZIP-დან snapshot-ის თავიდან შექმნა და SHA-256 provenance.
- Validator: schema, sample medians, CPU/wall ratios, per-worker summary და speedup-vs-serial formula ხელახლა მოწმდება.
- Native thread IDs და დეტალური host/kernel build მონაცემები საჯარო snapshot-ში არ ინახება.
- **Publication:** Draft; დამოუკიდებელი რეცენზია და physical-host replication არ დასრულებულა.
