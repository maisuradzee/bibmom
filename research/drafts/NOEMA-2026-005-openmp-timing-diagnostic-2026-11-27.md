# NOEMA-2026-005 — OpenMP CPU/wall timing diagnostic protocol

- **ID:** NOEMA-2026-005-OPENMP-TIMING-DIAG-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** Linux CPU/thread timing, affinity, cgroup v2 and numerical benchmark provenance

## საკვლევი კითხვა

შეიძლება თუ არა წინა OpenMP ექსპერიმენტში დაფიქსირებული process-CPU/wall-time შეუსაბამობის გამეორება, თუ თითოეული worker-ის CPU clock და affinity უშუალოდ worker thread-ში იზომება, ხოლო process-ის cgroup v2 შეზღუდვები დამოუკიდებლად იკითხება?

## მოკლე შეჯამება

2026-11-26-ის გაყინულ raw ანგარიშში 80 OpenMP გაზომვიდან 9-ის process-CPU/wall ratio აღემატებოდა 4.05-ს, მაქსიმუმით 13.287713, მაშინ როცა runner-ის მეტამონაცემები ოთხ ეფექტურ CPU-ს (cpuset 0-3) მიუთითებდა. ეს მონაცემები timing/provenance ანომალიად ჩაითვალა და შესაბამისი speedup მაჩვენებლები მასშტაბირების მტკიცებულებად არ გამოიყენება, სანამ კონტროლირებადი ხელახალი გაზომვა არ ჩატარდება.

## არსებული ცოდნა და წყაროები

- Linux man-pages, clock_gettime(2): https://man7.org/linux/man-pages/man2/clock_gettime.2.html
- Linux man-pages, sched_getaffinity(2): https://man7.org/linux/man-pages/man2/sched_getaffinity.2.html
- Linux kernel, cgroup v2: https://docs.kernel.org/admin-guide/cgroup-v2.html
- OpenMP API Specification 5.1, omp_get_wtime: https://www.openmp.org/spec-html/5.1/openmpsu185.html

## მტკიცებულებები

- **FACT:** Linux CLOCK_PROCESS_CPUTIME_ID ითვლის პროცესის ყველა thread-ის CPU დროს; CLOCK_THREAD_CPUTIME_ID — მიმდინარე thread-ის CPU დროს.
- **FACT:** sched_getaffinity() აბრუნებს გამომძახებელი thread-ის affinity mask-ს.
- **FACT:** cgroup v2 cpuset.cpus.effective და cpu.max აღწერს ეფექტურ CPU set-სა და CPU bandwidth quota-ს.
- **FACT:** omp_get_wtime() აბრუნებს elapsed wall time-ს; OpenMP 5.1 აღნიშნავს, რომ დროის ბაზა thread-specific-ია და სხვადასხვა thread-ს შორის თანმიმდევრულობა გარანტირებული არ არის.
- **HYPOTHESIS:** ძველი შეუსაბამობა შეიძლება უკავშირდებოდეს runner-ის cgroup path-ის არასწორ იდენტიფიკაციას, worker affinity-ს, clock accounting-ს ან ძველ raw sample-ებს. ძველი ანგარიში მიზეზს ვერ არჩევს.
- **UNTESTED IDEA:** იგივე დიაგნოსტიკის გამეორება ფიზიკურ x86-64 და ARM64 მოწყობილობებზე და perf stat task-clock/context-switch counters-თან შედარება, თუ უფლებები ხელმისაწვდომია.

## მეთოდი ან ექსპერიმენტის გეგმა

scripts/noema005_openmp_timing_diagnostic.c-ის GCC/OpenMP build გაეშვება worker-ების 1, 2, 4 და 8 რაოდენობით, ერთი warm-up-ით და თითო კონფიგურაციაზე 20 გაზომვით. თითოეული გაშვება იყენებს ერთსა და იმავე დეტერმინისტულ არითმეტიკულ workload-ს.

თითოეულ გაზომვაზე აღირიცხება:

- CLOCK_MONOTONIC wall time სრული parallel region-ის გარშემო;
- CLOCK_PROCESS_CPUTIME_ID სრული parallel region-ის გარშემო;
- CLOCK_THREAD_CPUTIME_ID თითოეულ worker-ში;
- getrusage(RUSAGE_THREAD) როგორც მეორე thread-CPU წყარო;
- sched_getaffinity(0) და sched_getcpu() თითოეულ worker-ში;
- omp_get_wtime() იმავე encountering thread-ში;
- process affinity, cgroup v2 cpuset.cpus.effective, cpu.max და cpu.stat delta.

ანგარიში აერთიანებს worker affinity mask-ებს და თითოეული გაშვებისთვის ითვლის კონსერვატიულ CPU-capacity ზღვარს. ზღვარზე 0.25 CPU-ით მეტი ratio ინიშნება anomaly-დ და არ იშლება. ყველა raw run ინახება GitHub Actions artifact-ში.

## შედეგები და ინტერპრეტაცია

**REPRODUCED RESULT — ერთი კონტროლირებადი hosted Linux run:** workflow run 45954993085-მა შექმნა 80 გაზომვა (1, 2, 4 და 8 worker; 20 გამეორება თითოეულზე; 8,000,000 iteration თითო გაზომვაზე). ყველა run-ში რეალური OpenMP thread-ების რაოდენობა მოთხოვნილს დაემთხვა.

გარემო: x86-64, GCC 13.3.0, Python 3.12.16, Linux kernel 7.0.0-1014-aws. process affinity და cgroup cpuset ორივე იყო 0-3; მიმდინარე cgroup-ის cpu.max იყო "max 100000" (ამ cgroup-ში quota არ იყო მითითებული).

| Worker-ები | Median process-CPU / wall ratio | Anomaly |
|---:|---:|---:|
| 1 | 0.999966709 | 0/20 |
| 2 | 2.000455849 | 0/20 |
| 4 | 4.001551167 | 0/20 |
| 8 | 3.946946747 | 0/20 |

მაქსიმალური process-CPU/wall ratio იყო 4.008956678; 80-დან არცერთი არ გასცდა 4.25 დიაგნოსტიკურ ზღვარს (ოთხი ეფექტური CPU + 0.25 margin). წინა ანგარიშის 13.287713 მაქსიმუმი ამ ერთ hosted run-ში არ გამეორებულა.

300 thread sample-ზე CLOCK_THREAD_CPUTIME_ID და getrusage(RUSAGE_THREAD) აბსოლუტური სხვაობის მედიანა იყო 332 ns, მაქსიმუმი 4,663 ns; 296/300 sample განსხვავდებოდა 1 µs-ზე ნაკლებით და ყველა 5 µs-ზე ნაკლებით. Per-thread CPU დროების ჯამი process CPU დროის მედიანურად 99.47–99.99%-ს შეადგენდა worker-ების მიხედვით.

**REPRODUCED RESULT:** frozen raw report დამოუკიდებლად გადაიკითხა; SHA-256, schema, 80 raw run, თითოეული ratio, ოთხი worker median და anomaly count ხელახლა გამოითვალა. არქივი: data/noema-005/raw/openmp-timing-diagnostic-2026-11-27.json.gz.b64; manifest: data/noema-005/openmp-timing-diagnostic-manifest-2026-11-27.json.

**INFERENCE:** ახალი instrumentation-ის ამ ერთ hosted გარემოში process CPU და per-thread CPU accounting ერთმანეთთან თანხვედრაშია და ოთხი CPU-ს ზღვარს არ სცდება. ეს ამყარებს ახალ გაზომვის გზას, მაგრამ არ ადგენს ძველი ანომალიის მიზეზს და არ ამტკიცებს ფიზიკურ hardware-ზე scaling-ს.

## შეზღუდვები და გაურკვევლობები

- cgroup cpu.stat არის cgroup-ის ყველა პროცესის აგრეგატი და არა მხოლოდ benchmark process-ის CPU აღრიცხვა.
- ამ run-ში cgroup v2 threaded subtree-ის არსებობა და თითოეული thread-ის cgroup membership ცალკე არ შემოწმებულა; worker affinity კი თითოეულ thread-ში პირდაპირ გაიზომა.
- მხოლოდ მიმდინარე cgroup-ის cpu.max ჩაიწერა; ancestor quota-ების ჯაჭვი ცალკე არ აღირიცხა. cpuset/affinity-ის ოთხი CPU ამ run-ის concurrency-ის ზედა ზღვარს მაინც ადგენდა.

- GitHub-hosted virtual runner არ არის დამოუკიდებელი ფიზიკური hardware replication.
- getrusage(RUSAGE_THREAD)-ის გარჩევადობა CLOCK_THREAD_CPUTIME_ID-ზე დაბალია.
- არითმეტიკული workload სინთეზურია და არ ზომავს resident-array DRAM bandwidth-ს ან რეალურ სამეცნიერო პროგრამას.
- hardware performance counters გარანტირებული არ არის.
- ეს დიაგნოსტიკა არ ამტკიცებს ზოგად speedup-ს ან რიცხვითი სიზუსტის უნივერსალურ გარანტიას.

## დასკვნა

ძველი timing anomaly-ს მიზეზი ჯერ უცნობია. ახალი ინსტრუმენტაცია პირდაპირ ზომავს worker-level CPU clocks და affinity-ს, რაც runner-level metadata-სთან შეუსაბამობის გარჩევას გაამარტივებს. სანამ განმეორებადი raw artifact და დამოუკიდებელი ფიზიკური გამეორება არ იქნება, მასშტაბირების მტკიცება არ გამოქვეყნდება.

## წყაროები

- Linux man-pages, clock_gettime(2), accessed 2026-11-27: https://man7.org/linux/man-pages/man2/clock_gettime.2.html
- Linux man-pages, sched_getaffinity(2), accessed 2026-11-27: https://man7.org/linux/man-pages/man2/sched_getaffinity.2.html
- Linux kernel documentation, cgroup v2, accessed 2026-11-27: https://docs.kernel.org/admin-guide/cgroup-v2.html
- OpenMP API Specification 5.1, accessed 2026-11-27: https://www.openmp.org/spec-html/5.1/openmpsu185.html

## შემდეგი ნაბიჯები

1. შესწორებული exact-head CI-ის გავლა და raw artifact-ის ჩამოტვირთვა.
2. 80 run-ის CPU/wall ratio, per-thread CPU sum, affinity union და cgroup quota-ს დამოუკიდებელი შემოწმება.
3. საჭიროების შემთხვევაში დიაგნოსტიკის მეორე hosted run.
4. ფიზიკურ x86-64 და ARM64 მოწყობილობებზე მინიმუმ 20 გამეორება თითო კონფიგურაციაზე, RSS/native allocation და memory bandwidth-ის გაზომვით.

## შემოწმების სტატუსი

- Frozen report captured 2026-11-27T06:55:42.790124Z; raw JSON SHA-256 da570bbb5783cb27b12e54ebc0bd8d6bd76e0a7be54c39e89edbe85a48822926.
- Source SHA-256 73660e5d83e0e1ae4decf07f20e8a9d9b06df2a315529b42f8bb6d7630300673; artifact ID 15178317416; workflow run 45954993085.
- დამოუკიდებელი frozen reproduction script: scripts/reproduce_noema005_openmp_timing_diagnostic.py --check.

- C diagnostic source, Python runner, schema და სინთეზური ტესტები დაემატა PR #124-ში.
- პირველი hosted run-მა 80 raw run შექმნა; max process-CPU/wall ratio იყო 4.026760538 და 0/80 აღემატებოდა capacity+0.25 ზღვარს, მაგრამ ტესტის/დრაფტის ვალიდაციის შეცდომის გამო artifact არ აიტვირთა.
- ეს პირველი run მხოლოდ წინასწარი execution signal-ია და საბოლოო frozen result არ არის.
- კვლევა რჩება Draft; ფიზიკური მოწყობილობის გამეორება და დამოუკიდებელი review არ ჩატარებულა.


## Measurement-integrity follow-up — schema v2

The next diagnostic revision closes two gaps in the first hosted run:

1. Each OpenMP worker now compares its `/proc/thread-self/cgroup` unified membership with the process leader's `/proc/self/cgroup` membership. Only a boolean match result is recorded; cgroup paths and host identifiers are never published.
2. The runner walks the visible cgroup v2 hierarchy from the current cgroup to the cgroup2 mount root and reads each ancestor's `cpu.max`. It uses the minimum finite quota as the effective quota. If any ancestor quota file is unreadable, the chain is incomplete. If any worker's cgroup differs from the process leader, membership is unverified, or the quota chain is incomplete, the report withholds the effective-capacity and anomaly threshold rather than asserting a potentially incorrect CPU ceiling.

The report schema is now version 2 while the validator retains compatibility with the previously frozen version-1 report. This preserves the earlier artifact as an immutable historical result. New v2 reports include per-run and aggregate counts of cgroup mismatches and unverified worker memberships.

**FACT:** Linux process CPU time includes all threads; cgroup v2 controller limits are hierarchical. The updated measurement therefore treats process-level metadata as insufficient unless worker membership and visible ancestor quota constraints are checked.

**UNTESTED until the next workflow run:** the enhanced instrumentation has not yet produced a new hosted artifact. No conclusion is drawn about whether it changes the previous 80-run result.


## Frozen-source provenance correction

The first schema-v2 instrumentation change modified the live C source file, which caused the version-1 frozen-result reproducer to compare the old report's source digest against the new source and fail. This was a provenance defect in the reproduction path, not a failure of the historical measurements.

The exact version-1 C source from the original diagnostic commit is now preserved at `scripts/archive/noema005_openmp_timing_diagnostic_v1.c`. The frozen-report reproducer hashes this archived source, while new runs compile the current schema-v2 source. Historical evidence is therefore immutable and is not silently reinterpreted using a later implementation.


## Follow-up: affinity/cpuset upper bound versus exact cgroup quota

The first schema-v2 hosted run (80 samples, 20 per worker count) verified all 300 worker cgroup-membership checks and found zero worker/process cgroup mismatches. However, one or more visible ancestor `cpu.max` files were unreadable, so the runner correctly withheld an exact effective CPU-capacity claim and its anomaly threshold. The raw maximum process-CPU/wall ratio was 4.005002215, but that run did not classify it against a threshold.

The next revision separates two concepts:
- **Known CPU upper bound:** minimum of process affinity count, effective cpuset size and the union of observed worker affinity masks, provided all workers match the process cgroup and the observed process task count equals the OpenMP team size.
- **Exact effective CPU capacity:** reported only when the complete visible cgroup v2 ancestor `cpu.max` chain is readable; otherwise it remains null.

The anomaly threshold is based on the known affinity/cpuset upper bound plus 0.25 CPU, not on an incompletely observed quota. This can detect ratios that exceed the hard observed CPU-set ceiling while avoiding a false claim about an unknown lower quota. The report also counts unreadable quota levels without exposing their paths.

**UNTESTED until the next workflow run:** the final upper-bound implementation has not yet produced its hosted artifact. The earlier 80-run artifact is retained only as a diagnostic observation with an unevaluated threshold, not as a no-anomaly result.
