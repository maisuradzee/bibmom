# NOEMA-2026-005 — Run 41 local threaded reduction reproduction

- **სტატუსი:** Draft / Preliminary evidence
- **თარიღი:** 2026-11-28
- Experiment ID: NOEMA005-RUN41-LOCAL-THREADS-20261128
- მტკიცებულების სტატუსი: FACT · REPRODUCED_RESULT · INFERENCE · HYPOTHESIS · UNTESTED IDEA

## საკვლევი კითხვა

ინარჩუნებს თუ არა სრული Neumaier (sum, correction) მდგომარეობა სწორად დამრგვალებულ შედეგს რეალურ OS threads-ზე და აჩვენებს თუ არა GIL-enabled CPython ამ სინთეზურ CPU-bound workload-ზე wall-time აჩქარებას?

## FACT

- გარემო: CPython 3.13.5, GIL-enabled, Linux x86_64, managed container; bare-metal სტატუსი არ არის დადასტურებული.
- გამოყენებულია ორი cancellation layout, სამი reduction მეთოდი, ორი partition strategy და 1/2/4/8 worker.
- თითო კონფიგურაციაზე შესრულდა 2 warm-up და 20 გაზომილი გამეორება.
- 48 კონფიგურაცია × 20 გამეორება = 960 threaded measurement.
- თითო worker იღებს native OS thread ID-ს მხოლოდ run-ის შიგნით; ანგარიშში ინახება მხოლოდ worker-count-ის დამთხვევა და არა thread ID.
- input-ის ზუსტი binary64 reference გამოითვლება Fraction.from_float-ით.
- wall time იზომება perf_counter_ns-ით; process CPU — process_time_ns-ით; memory — tracemalloc-ით.

## REPRODUCED_RESULT

| Reduction method | Correctly rounded |
|---|---:|
| Naive scalar partial | 0 / 320 |
| Neumaier scalar partial merge | 280 / 320 |
| Full Neumaier (sum, correction) state | 320 / 320 |

ყველა 48 threaded კონფიგურაციის median speedup შესაბამის serial baseline-თან შედარებით 1.0-ზე ნაკლები იყო.

| Method | 1 worker | 2 workers | 4 workers | 8 workers |
|---|---:|---:|---:|---:|
| Naive scalar | 0.425495× | 0.317401× | 0.215500× | 0.137690× |
| Neumaier scalar | 0.621691× | 0.499362× | 0.441338× | 0.322174× |
| Full Neumaier state | 0.623855× | 0.546918× | 0.469201× | 0.356527× |

Full-state median tracemalloc peak worker count-ის მიხედვით იყო 9,781 B, 15,626 B, 27,164 B და 50,534 B (1/2/4/8 workers). ეს არ არის RSS, native allocator ან DRAM bandwidth.

## INFERENCE

ამ managed-container გაშვებაში GIL-enabled pure-Python threads-მა CPU-bound cancellation workload-ზე wall-time აჩქარება არ აჩვენა. სრული Neumaier state-მა სწორად დამრგვალებული შედეგი შეინარჩუნა ყველა 320 გაზომილ run-ში, ხოლო scalar partial merge-მა 40 შედეგი დაკარგა. ეს დასკვნა ვრცელდება მხოლოდ მოცემულ სინთეზურ workload-სა და გარემოზე; არ არის უნივერსალური მტკიცება ყველა Python ან native workload-ის შესახებ.

შედეგის მიმართულება თავსებადია წინა Draft PR #148-ის 20-repeat container reproduction-თან, მაგრამ არცერთი მათგანი არ წარმოადგენს დამოუკიდებელ bare-metal ან ARM64 გამეორებას.

## HYPOTHESIS

Free-threaded CPython ან native C/OpenMP reduction შეიძლება განსხვავებულ scaling-ს აჩვენებდეს; ეს უნდა შემოწმდეს იმავე input hash-ებზე და კონტროლირებულ ფიზიკურ მოწყობილობებზე.

## UNTESTED IDEA

შედარდეს full Neumaier state, pairwise tree და exact/superaccumulator native kernel-ით, RSS/native allocation, DRAM bandwidth, CPU pinning და NUMA კონტროლით.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Runner: scripts/run_noema005_local_threaded_repro.py.
2. Parameters: repeat_count=8192, warmups=2, measured_repetitions=20.
3. Layouts: triplet_order და grouped_cancellation; თითო input 24,576 binary64 values.
4. Methods: threaded_naive_scalar, threaded_neumaier_scalar, threaded_neumaier_state.
5. Partitions: contiguous და round_robin; workers: 1, 2, 4, 8.
6. Barrier უზრუნველყოფს worker-ების ერთდროულ start-ს; თითო გაზომილ run-ში distinct native thread count უნდა ემთხვეოდეს worker count-ს.
7. Serial baselines იზომება შესაბამის layout/method-ზე; speedup = serial median wall / threaded median wall.
8. Frozen report ინახავს 960 raw threaded wall samples-ს, input SHA-256-ებს, runner SHA-256-სა და privacy-safe environment metadata-ს.

## შეზღუდვები და რისკები

- ერთი managed Linux x86_64 container; bare-metal სტატუსი უცნობია.
- მხოლოდ GIL-enabled CPython 3.13.5; ARM64 და free-threaded build არ გამოცდილა.
- მხოლოდ სინთეზური cancellation workload, repeat_count=8192.
- ThreadPoolExecutor startup/scheduling შედის wall time-ში.
- process_time_ns process-wide მაჩვენებელია და არა per-thread CPU time.
- tracemalloc არ ზომავს RSS/native memory/DRAM bandwidth-ს.
- CPU pinning, NUMA კონტროლი და დამოუკიდებელი ფიზიკური მოწყობილობის გამეორება არ ჩატარებულა.

## წყაროები

1. Python 3.13 C API — Thread states and the global interpreter lock: https://docs.python.org/3.13/c-api/threads.html
2. PEP 703 — Making the Global Interpreter Lock Optional in CPython: https://peps.python.org/pep-0703/
3. PEP 779 — Criteria for supported status for free-threaded Python: https://peps.python.org/pep-0779/
4. Python threading.get_native_id: https://docs.python.org/3/library/threading.html#threading.get_native_id
5. Python tracemalloc: https://docs.python.org/3/library/tracemalloc.html

## არტეფაქტები

- Frozen report (gzip+base64): data/noema-005/run41-local-threaded-report-2026-11-28.json.gz.b64
- Manifest: data/noema-005/run41-local-threaded-report-2026-11-28.manifest.json
- Report SHA-256: 0a5a872de4cce503f65538cfd7cb2ac6b36a6efaa3b5bb2a5bc7f0b53324a244
- Gzip SHA-256: 439e0f85050758f6b85ff001b627679a1f43872734b1aca8a0686c100a7895ba
- Runner SHA-256: 8018d1a8df78d1f93e109f502a99642d431fd6a99c97fddf69b200959d3ca9d3

## შემდეგი ნაბიჯები

1. იგივე protocol გაუშვას free-threaded CPython 3.13t/3.14t-ზე და physical x86_64/ARM64 მოწყობილობებზე.
2. გაზარდოს input size და დაამატოს representative scientific workloads.
3. დაამატოს RSS/native allocation, DRAM bandwidth, CPU pinning და NUMA metadata — მხოლოდ privacy-safe ფორმით.
4. შეადაროს pairwise tree და exact accumulator native C/OpenMP implementation-ით.
5. მოითხოვოს დამოუკიდებელი numerical-method review.

## შემოწმების სტატუსი

- Local run completed: 48 configurations, 960 threaded measurements, 20 repetitions/configuration.
- Frozen archive, runner hash, report hash and schema are covered by regression tests.
- Exact-head GitHub CI is pending.
- No physical-device, ARM64, free-threaded, RSS or DRAM-bandwidth result is claimed.
- Status remains Draft/Preliminary; no independent external review or Published status is claimed.
