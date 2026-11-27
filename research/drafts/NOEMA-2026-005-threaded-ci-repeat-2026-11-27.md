# NOEMA-2026-005 — hosted GIL-enabled and free-threaded CPU-thread repeats

- **ID:** NOEMA-2026-005-REAL-THREADS-002
- **სტატუსი:** draft / preliminary evidence review
- **თარიღი:** 2026-11-27
- **სფერო:** compensated floating-point reduction · actual CPython worker threads

## საკვლევი კითხვა

შეუძლია თუ არა Python-ის free-threaded build-ს ამ კონკრეტულ synthetic reduction workload-ზე რეალური მრავალბირთვიანი CPU execution-ის მიღწევა და იძლევა თუ არა ეს wall-time speedup-ს matching serial baseline-თან შედარებით? რამდენად მგრძნობიარეა შედეგი hosted runner გარემოს მიმართ და რომელი reduction state ინარჩუნებს correctly-rounded result-ს?

## მეთოდი ან ექსპერიმენტის გეგმა

სამი დამოუკიდებელი GitHub Actions workflow run იქნა გამოყენებული:

- [Run 46006107242](https://github.com/maisuradzee/bibmom/actions/runs/46006107242), head `fdfc4d390fdb7cfc45f5879dbc699c3d2165a1e9`, artifacts 15201571617 (GIL-enabled) და 15201906516 (free-threaded).
- [Run 46007383552](https://github.com/maisuradzee/bibmom/actions/runs/46007383552), head `3cfe55c5748333ccba18efd0209dd14e66ed8499`, artifacts 15200953902 (GIL-enabled) და 15200369413 (free-threaded).
- [Run 46011557117](https://github.com/maisuradzee/bibmom/actions/runs/46011557117), head `ce095d7be7c4b96ffca423ee66a1f38157cf99e4`, artifacts 15203113651 (GIL-enabled) და 15204417524 (free-threaded). ორივე coarse runner kernel flavor `azure` იყო.

თითოეულ artifact-ში შესრულდა 48 კონფიგურაცია × 3 გამეორება = 144 run. ჯამში ექვს artifact-ში არის 288 კონფიგურაცია და 864 run. მატრიცა მოიცავდა 1, 2, 4 და 8 worker-ს; `triplet_order` და `grouped_cancellation` input layout-ებს; `contiguous` და `round_robin` partition-ებს; naive scalar, Neumaier scalar და Neumaier state მეთოდებს. თითო input-ში იყო 196,608 binary64 მნიშვნელობა და ზუსტი ჯამი 65,536.

CI-მ გადაამოწმა თითო worker-ის განსხვავებული native thread identity. საჯარო snapshot-ში შენარჩუნებულია მხოლოდ native thread count; thread ID-ები და დეტალური host/kernel build სტრიქონები ამოღებულია. დამატებით, validator recursively ამოწმებს ყველა nested report/manifest object-ს და უარყოფს host, runner, device, PID/TID, native-thread-ID, cgroup path და დეტალური kernel/build identity ველებს. ეს არის key-name allow/deny guard და არა arbitrary string-value secret scanner. Manifest ინახავს artifact ID-ებს, workflow head SHA-ებსა და ZIP/source JSON SHA-256-ებს. Runner-ის მხოლოდ coarse kernel-flavor suffix (azure/aws) ინახება შედარების კონტექსტისთვის; ეს არ არის CPU model-ის ან cloud host-ის იდენტიფიკაცია.

## შედეგები

| Runtime / runner flavor | Method | Correctly rounded | Median speedup vs serial | Median process-CPU / wall |
|---|---|---:|---:|---:|
| GIL / azure | naive scalar | 0/48 | 0.4754× | 1.0077 |
| GIL / azure | Neumaier scalar | 42/48 | 0.7616× | 1.0075 |
| GIL / azure | Neumaier state | 48/48 | 0.7577× | 1.0078 |
| GIL / azure (repeat 2) | naive scalar | 0/48 | 0.4893× | 1.0143 |
| GIL / azure (repeat 2) | Neumaier scalar | 42/48 | 0.7577× | 1.0092 |
| GIL / azure (repeat 2) | Neumaier state | 48/48 | 0.7551× | 1.0085 |
| Free / aws | naive scalar | 0/48 | 0.1634× | 2.8119 |
| Free / aws | Neumaier scalar | 42/48 | 0.7089× | 2.7220 |
| Free / aws | Neumaier state | 48/48 | 0.7024× | 2.6761 |
| Free / azure (repeat 2) | naive scalar | 0/48 | 0.4620× | 2.2335 |
| Free / azure (repeat 2) | Neumaier scalar | 42/48 | 1.2527× | 2.4095 |
| Free / azure (repeat 2) | Neumaier state | 48/48 | 1.2494× | 2.3899 |
| GIL / azure (repeat 3) | naive scalar | 0/48 | 0.4625× | 1.0148 |
| GIL / azure (repeat 3) | Neumaier scalar | 42/48 | 0.7549× | 1.0085 |
| GIL / azure (repeat 3) | Neumaier state | 48/48 | 0.7603× | 1.0091 |
| Free / azure (repeat 3) | naive scalar | 0/48 | 0.3526× | 2.5835 |
| Free / azure (repeat 3) | Neumaier scalar | 42/48 | 1.2009× | 2.6056 |
| Free / azure (repeat 3) | Neumaier state | 48/48 | 1.1491× | 2.2683 |

Neumaier state-ის worker-count მედიანები:

| Runtime / runner | Worker | CPU/wall | Speedup |
|---|---:|---:|---:|
| GIL / azure | 1 | 1.0012 | 0.7874× |
| GIL / azure | 2 | 1.0049 | 0.7638× |
| GIL / azure | 4 | 1.0124 | 0.7547× |
| GIL / azure | 8 | 1.0168 | 0.7391× |
| Free / aws | 1 | 0.9951 | 0.7031× |
| Free / aws | 2 | 1.9726 | 0.6470× |
| Free / aws | 4 | 3.8794 | 0.7286× |
| Free / aws | 8 | 3.4299 | 0.7024× |
| GIL / azure repeat 2 | 1 | 1.0012 | 0.7780× |
| GIL / azure repeat 2 | 2 | 1.0047 | 0.7595× |
| GIL / azure repeat 2 | 4 | 1.0118 | 0.7489× |
| GIL / azure repeat 2 | 8 | 1.0165 | 0.7348× |
| Free / azure repeat 2 | 1 | 1.0030 | 0.7656× |
| Free / azure repeat 2 | 2 | 1.9812 | 1.1859× |
| Free / azure repeat 2 | 4 | 3.0512 | 1.3065× |
| Free / azure repeat 2 | 8 | 3.2209 | 1.2620× |
| GIL / azure repeat 3 | 1 | 1.0012 | 0.7718× |
| GIL / azure repeat 3 | 2 | 1.0059 | 0.7452× |
| GIL / azure repeat 3 | 4 | 1.0129 | 0.7549× |
| GIL / azure repeat 3 | 8 | 1.0170 | 0.7359× |
| Free / azure repeat 3 | 1 | 1.0032 | 0.7426× |
| Free / azure repeat 3 | 2 | 1.9666 | 1.1129× |
| Free / azure repeat 3 | 4 | 3.4115 | 1.1887× |
| Free / azure repeat 3 | 8 | 3.3496 | 1.1662× |

ყველა ექვს artifact-ში Neumaier state-მა 48/48 correctly-rounded run მიიღო; Neumaier scalar-მა 42/48; naive scalar-მა 0/48. GIL-enabled Azure repeat-ები ახლოს იყო (0.7577×, 0.7551× და 0.7603×). Free-threaded Azure repeat-ებმა 1.2494× და 1.1491× აჩვენა, ხოლო free-threaded AWS run-ში median speedup 0.7024× იყო. ეს აძლიერებს გარემოს მიმართ მგრძნობელობის სიგნალს, მაგრამ runner flavor-ის განსხვავება მიზეზობრიობას არ ამტკიცებს.

Free-threaded 4-worker შემთხვევაში სამივე run აჩვენებს CPU concurrency-ს (CPU/wall 3.879 AWS; 3.051 Azure repeat 2; 3.411 Azure repeat 3), მაგრამ wall-time შედეგები მნიშვნელოვნად განსხვავდება. შესაბამისად, free-threading-ის უნივერსალური აჩქარების მტკიცება დაუშვებელია. GIL-enabled run-ებში CPU/wall დაახლოებით 1.0 იყო.

## მტკიცებულებები

- **FACT:** PEP 703 განსაზღვრავს CPython-ის optional-GIL build configuration-ს; ეს არ არის ავტომატური speedup-ის გარანტია. https://peps.python.org/pep-0703/
- **FACT:** Python 3.14-ის free-threading დოკუმენტაცია აღწერს GIL-ის runtime-ზე ხელახლა ჩართვის შესაძლებლობას და extension compatibility-ის შეზღუდვებს. https://docs.python.org/3.14/howto/free-threading-python.html
- **REPRODUCED RESULT:** ექვსი GitHub Actions artifact-ის 48-კონფიგურაციიანი ანგარიშები schema-ით და raw sample median-ების ხელახალი გამოთვლით მოწმდება; თითო artifact-ში 144 run. მესამე workflow run-მა დაამატა ერთი GIL-enabled და ერთი free-threaded Azure repeat.
- **INFERENCE:** ამ workload-ზე free-threaded build-ს შეუძლია native worker-ებით CPU concurrency; მაგრამ wall-time speedup დამოკიდებულია hosted environment-ზე და ერთ run-ს უნივერსალურ performance claim-ად ვერ განვაზოგადებთ.
- **HYPOTHESIS:** CPU microarchitecture, frequency, cache/memory subsystem ან runner scheduling განსხვავებები შეიძლება ხსნიდეს free-threaded შედეგების განსხვავებას; ეს ფაქტორები ცალკე არ გაზომილა.
- **UNTESTED IDEA:** იგივე exact-reference workload-ის შედარება C/OpenMP და vectorized implementation-ებთან, RSS/native allocation, DRAM bandwidth და perf counters-ით.

## შეზღუდვები და გაურკვევლობები

- ორივე რეჟიმი hosted x86-64 runner-ზე შესრულდა და არა დამოუკიდებლად კონტროლირებულ ფიზიკურ მოწყობილობაზე.
- GIL-enabled და free-threaded რეჟიმები ზოგ run-ში სხვადასხვა runner kernel flavor-ზე გაეშვა; ეს same-machine controlled comparison არ არის.
- runner-ს 4 CPU affinity ჰქონდა; 8-worker კონფიგურაციები oversubscribed იყო.
- თითო კონფიგურაციას მხოლოდ 3 გამეორება აქვს; confidence interval და დამოუკიდებელი გარე გამეორება არ არსებობს. სამი workflow run ერთი და იმავე hosted provider-ისა და ერთი არქიტექტურის ფარგლებშია, მაგრამ ერთი და იმავე ფიზიკური host-ის controlled pairing არ არის.
- input-ები synthetic cancellation patterns-ია და არა რეალური სამეცნიერო workload.
- `tracemalloc` არ ზომავს RSS-ს, native allocations-ს ან DRAM bandwidth-ს.
- perf_event task-clock, hardware counters, CPU frequency და context-switch counts არ გაზომილა.
- ახალი physical x86-64 ან ARM64 ექსპერიმენტი ამ ჩანაწერში არ არის.

## წყაროები

1. Gross, S. (2023). PEP 703 — Making the Global Interpreter Lock Optional in CPython. https://peps.python.org/pep-0703/
2. Python Software Foundation. Python 3.14 — Python support for free threading. https://docs.python.org/3.14/howto/free-threading-python.html
3. GitHub Actions runs 46006107242, 46007383552 and 46011557117; artifacts and SHA-256 provenance are in `data/noema-005/threaded-ci-repeat-manifest-2026-11-27.json`.

## შემდეგი ნაბიჯები

1. დამოუკიდებელი physical x86-64 და ARM64 გამეორება, მინიმუმ 20 repetitions per configuration.
2. C/OpenMP and vectorized kernels with identical exact-reference inputs.
3. RSS/native allocation, DRAM bandwidth, task-clock, context-switch and CPU-frequency evidence.
4. Chunk-size and reduction-tree sweeps with confidence intervals.
5. Independent numerical-method review before any publication status.

## შემოწმების სტატუსი

- ექვსი frozen sanitized snapshot: სამი GIL-enabled და სამი free-threaded; 48 cases და 144 runs თითო artifact-ში.
- CI validator ამოწმებს უკვე შენახულ ექვს snapshot-ს, manifest-ის hash-ებს, schema-სა და raw sample-ებიდან ხელახლა გამოთვლილ summary-ს; CI ავტომატურად არ ჩამოტვირთავს ორიგინალ artifact ZIP-ებს.
- ცალკე reproducer CLI იღებს ორიგინალ artifact ZIP-ს და თავიდან ქმნის sanitized JSON snapshot-სა და provenance fields-ს. Run 29-ში ექვსივე ორიგინალი ZIP და source JSON SHA-256-ით გადამოწმდა. მანამდე აღმოჩენილი ორი free-threaded snapshot აღდგა შესაბამისი source artifact-ებიდან; მესამე repeat pair-ის დამატების შემდეგ Run 46011557117-ის GIL-enabled snapshot-შიც გამოვლინდა ერთი ზედმეტი Base64 padding/სიგრძის დაზიანება. იგი ხელახლა შეიქმნა ორიგინალი artifact ZIP-იდან; regenerated gzip SHA-256 დაემთხვა manifest-ში არსებულ `30efa08d70a6c7555283d567ab6f68567430cb96af3aba7066049c89f1926175` მნიშვნელობას. ექვსივე snapshot ახლა ინახავს 3 workflow run × 2 runtime pair-ს; raw measurement values არ შეცვლილა.
- `sanitized_gzip_sha256` არის საცავში შენახული ზუსტი compressed bytes-ის hash. gzip/deflate output შეიძლება Python/zlib runtime-ებს შორის განსხვავდებოდეს; cross-runtime reproduction-ისას JSON payload და source ZIP/report hashes უნდა შედარდეს, ხოლო stored-byte hash მხოლოდ კონკრეტულ არტეფაქტს ეკუთვნის.
- Validator: schema, source manifest, sample medians, CPU/wall ratios, per-worker summary და speedup-vs-serial formula ხელახლა მოწმდება; recursive public-boundary tests ყველა nested object-ში კრძალავს host/runner/device/native-thread identity keys-ს და ამოწმებს, რომ coarse architecture/CPU-count metadata დაშვებულია.
- Native thread IDs და დეტალური host/kernel build მონაცემები საჯარო snapshot-ში არ ინახება.
- **Publication:** Draft; დამოუკიდებელი რეცენზია და physical-host replication არ დასრულებულა.
