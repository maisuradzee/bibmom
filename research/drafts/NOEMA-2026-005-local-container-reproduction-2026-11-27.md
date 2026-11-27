# NOEMA-2026-005 — დამოუკიდებელი GIL-enabled კონტეინერის გამეორება

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft / independent reduced-size reproduction
- **თარიღი:** 2026-11-27
- **მტკიცებულების სტატუსი:** REPRODUCED_RESULT
- **რეფერენსი:** scripts/benchmark_noema005_threaded_reduction.py (Git blob c585bdec3f8316f85bbde77f6a1be9301fa169d2)

## საკვლევი კითხვა

ინარჩუნებს თუ არა სრული Neumaier (sum, correction) მდგომარეობის გადაცემა სწორად დამრგვალებულ შედეგს რეალურ OS threads-ზე, და იძლევა თუ არა Python-ის GIL-enabled build მრავალ-thread შესრულების აჩქარებას ამ სინთეზურ cancellation workload-ზე?

## მეთოდი ან ექსპერიმენტის გეგმა

- გარემო: CPython 3.13.5, GIL enabled, Linux x86_64 container; /proc/cpuinfo-ის მოდელის სტრიქონი AMD EPYC 9V74 80-Core Processor; პროცესის affinity 0–4; cgroup cpu.max = 400000 100000 (4 CPU-equivalent quota). ეს არ არის bare-metal დადასტურება.
- ორი input layout: triplet_order და grouped_cancellation; თითოეულში N=8192 triplet, 24,576 binary64 მნიშვნელობა.
- 3 მეთოდი: naive scalar partial, Neumaier scalar partial, სრული Neumaier (sum, correction) state.
- 2 partition: contiguous და round_robin.
- 4 worker count: 1, 2, 4, 8.
- სულ 48 კონფიგურაცია; თითოეულზე 2 warm-up და 20 გაზომილი გამეორება — 960 threaded გაზომვა, 320 თითო მეთოდზე.
- თითოეული worker იღებს OS native thread ID-ს; barrier უზრუნველყოფს, რომ ყველა worker ერთ run-ში რეალურად გაეშვას. თითოეულ გამეორებაში უნიკალური native thread-ების რაოდენობა worker count-ს ემთხვევა.
- სიზუსტის reference გამოითვლება Fraction.from_float-ით binary64 input-ების ზუსტი ჯამისთვის.
- runtime იზომება perf_counter_ns-ით და process_time_ns-ით; memory — tracemalloc peak-ით. ThreadPoolExecutor-ის startup/scheduling შედის wall time-ში.
- raw wall-time samples, serial baseline medians, input SHA-256, runner SHA-256 და 48-კონფიგურაციანი matrix ინახება JSON report-ში.

## მტკიცებულებები და შედეგები

### FACT — გარემო და მეთოდი

ამ გაშვებაში გამოყენებული იყო GIL-enabled CPython 3.13.5. Python-ის ოფიციალური დოკუმენტაცია განმარტავს, რომ GIL-enabled build-ში Python bytecode-ს ერთდროულად ერთი thread ასრულებს; PEP 703 აღწერს GIL-ის optional/free-threaded კონფიგურაციას, ხოლო PEP 779 განსაზღვრავს free-threaded build-ის მხარდაჭერის კრიტერიუმებს.

### REPRODUCED_RESULT — სიზუსტე

| მეთოდი | სწორად დამრგვალებული შედეგები |
|---|---:|
| Naive scalar partial | 0 / 320 |
| Neumaier scalar partial | 280 / 320 |
| სრული Neumaier (sum, correction) state | 320 / 320 |

ეს მაჩვენებლები ვრცელდება მხოლოდ მოცემულ ორ სინთეზურ layout-სა და ამ გარემოზე.

### REPRODUCED_RESULT — runtime

ყველა 48 threaded კონფიგურაციაში median speedup matching serial baseline-თან შედარებით 1.0-ზე ნაკლები იყო.

| მეთოდი | 1 worker | 2 workers | 4 workers | 8 workers |
|---|---:|---:|---:|---:|
| Naive scalar | 0.4967× | 0.3973× | 0.3077× | 0.1909× |
| Neumaier scalar | 0.6498× | 0.6040× | 0.5505× | 0.3972× |
| სრული Neumaier state | 0.6356× | 0.5887× | 0.5167× | 0.4123× |

Median process-CPU / wall-time თანაფარდობა 0.942–0.986 დიაპაზონში იყო. ეს შედეგი თავსებადია GIL-enabled pure-Python workload-ზე CPU პარალელიზმის არქონასთან, თუმცა არ წარმოადგენს უნივერსალურ დასკვნას ყველა workload-ისთვის.

### REPRODUCED_RESULT — Python-traced memory

სრული Neumaier state-ის median tracemalloc peak worker count-ის მიხედვით: 1 worker — 9,639 B; 2 — 15,174 B; 4 — 26,602 B; 8 — 49,630 B. ეს არ არის RSS, native allocation ან DRAM bandwidth.

### INFERENCE

ამ workload-ზე სრული Neumaier state-მა შეინარჩუნა სწორი დამრგვალება ყველა გაზომილ კონფიგურაციაში, scalar partial merge-მა კი 40/320 შემთხვევა დაკარგა. GIL-enabled pure-Python threads-მა აჩქარება არ აჩვენა; მეტი worker ზრდიდა wall time-სა და traced allocation-ს.

### HYPOTHESIS

Free-threaded CPython ან C/OpenMP native reduction-მა შეიძლება შეცვალოს scaling, მაგრამ ეს ცალკე გარემოსა და workload-ზე უნდა შემოწმდეს.

### UNTESTED IDEA

შედარდეს სრული Neumaier state, pairwise tree და exact/superaccumulator C/OpenMP kernel-ით, იგივე input hash-ებზე და native memory-bandwidth/RSS გაზომვით.

## შეზღუდვები

1. მხოლოდ ერთი Linux x86_64 container; CPU მოდელის სტრიქონი host-იდანაა, bare-metal სტატუსი არ დადასტურებულა.
2. cgroup quota 4 CPU-equivalent-ია, affinity კი 5 CPU-ს მოიცავს; host scheduling კონტროლირებადი არ იყო.
3. არ იყო ხელმისაწვდომი ARM64 ან free-threaded CPython.
4. N=8192 უფრო მცირეა, ვიდრე hosted workflow-ის N=65536; ეს არის reduced-size დამოუკიდებელი გამეორება და არა სრული CI matrix-ის ზუსტი გამეორება.
5. workload სინთეზური cancellation input-ია და არა რეალური სამეცნიერო dataset.
6. process_time_ns process-wide მაჩვენებელია; tracemalloc მხოლოდ Python-traced allocation-ს ზომავს და არა RSS/native memory-ს.
7. ThreadPoolExecutor startup/scheduling შედის runtime-ში; thread pinning და NUMA კონტროლი არ ჩატარებულა.

## წყაროები

1. PEP 703 — Making the Global Interpreter Lock Optional in CPython, https://peps.python.org/pep-0703/
2. PEP 779 — Criteria for supported status for free-threaded Python, https://peps.python.org/pep-0779/
3. Python 3.14.10 documentation — Thread states and the global interpreter lock, https://docs.python.org/3.14/c-api/threads.html
4. Python 3.14.10 documentation — C API Extension Support for Free Threading, https://docs.python.org/3.14/howto/free-threading-extensions.html

## გამეორების არტეფაქტები

- Runner: scripts/reproduce_noema005_local_container.py
- Runner SHA-256: e252e625752e1d46dd57c01d1b726d0cddc6620b19748951575be8f446772d8c
- Frozen report: data/noema-005/local-container-repro-2026-11-27.json
- Report SHA-256: f8743906f198721d4df2cc4549f82924ea8f39495b05fa035bf3922362992b06
- Input SHA-256: triplet_order = 2f19dc716781185edce36e180984a7dd23c70f8fe2596e73afd272acba9f7a2d; grouped_cancellation = 0157b24f78ca70640f01f2801a74e0c287a79f15604d1946eb1b3295f81e39c1
- Local validation: 7/7 tests passed before repository integration.

## შემდეგი ნაბიჯები

1. იგივე protocol გაუშვას CPython 3.14.10 GIL-enabled და 3.14.10t free-threaded build-ებზე.
2. გაიმეოროს ფიზიკურ x86_64 და ARM64 მოწყობილობებზე, მინიმუმ 20 repetition/configuration და N=65536 ან მეტი.
3. დაამატოს RSS/native allocation, memory bandwidth, CPU pinning და NUMA metadata.
4. შეადაროს C/OpenMP, pairwise tree და exact accumulator რეალისტურ workload-ზე.
5. მოითხოვოს დამოუკიდებელი რიცხვითი ანალიზის რეცენზია.

## შემოწმების სტატუსი

- Frozen JSON schema: ადგილობრივად ვალიდურია.
- Reproduction regression tests: 7/7 passed.
- სტატუსი: Draft / Preliminary evidence only; Published არ არის.


## Archive packaging clarification — Run 11

The first repository copy of the JSON report was truncated at the repository text-transfer boundary and failed JSON parsing before the focused tests could start. The measurement result was not accepted on that malformed copy. This corrected compact snapshot preserves all 48 configurations and all 960 raw wall-time samples. It retains serial baseline wall medians (the values used for each speedup) but omits serial baseline process-CPU medians and serial accuracy counts from the JSON; those measurement details are not used to recompute the threaded speedup and the methodology/limitations remain documented above. The original measurement runner SHA-256 remains e252e625752e1d46dd57c01d1b726d0cddc6620b19748951575be8f446772d8c; the new frozen report SHA-256 is 5d4df2abfef211e338922b59ee1cfa3957dfb14485b69a2fbfacc47c98af7853. No new benchmark run is claimed by this packaging correction.


The compact-report validation also found one row whose stored `median_wall_ns` and speedup did not match its preserved 20 wall-time samples. All 48 derived median and speedup fields were recomputed from the raw sample arrays using the runner's stated median and matching-serial-baseline rules. The affected row was `triplet_order / threaded_naive_scalar / round_robin / 2 workers`: median changed from 1,035,946 ns to 1,034,764 ns and speedup from 0.322461789 to 0.322830133. The 20 raw timings were not changed. This is a derived-field correction, not a new benchmark run.
