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

პირველი hosted diagnostic execution-მა შექმნა 80 გაზომვა. CI-ის ლოგში მაქსიმალური process-CPU/wall ratio იყო 4.026760538, worker-ების მიხედვით median ratio-ები კი დაახლოებით 1.0000, 2.0004, 4.0032 და 3.9478 იყო 1, 2, 4 და 8 worker-ზე. capacity+0.25 ზღვარს არცერთი გაზომვა არ გადასცდა.

ეს მხოლოდ წინასწარი execution signal-ია: იმავე workflow run-ში privacy test-ის assertion-მა CI შეაჩერა artifact upload-მდე. ამიტომ raw report ჯერ არ არის შენახული GitHub artifact-ში და ეს გაშვება საბოლოო frozen result-ად არ ჩაითვლება. შესწორებული workflow-ის შედეგი ცალკე უნდა შეფასდეს.

## შეზღუდვები და გაურკვევლობები

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

- C diagnostic source, Python runner, schema და სინთეზური ტესტები დაემატა PR #124-ში.
- პირველი hosted run-მა 80 raw run შექმნა; max process-CPU/wall ratio იყო 4.026760538 და 0/80 აღემატებოდა capacity+0.25 ზღვარს, მაგრამ ტესტის/დრაფტის ვალიდაციის შეცდომის გამო artifact არ აიტვირთა.
- ეს პირველი run მხოლოდ წინასწარი execution signal-ია და საბოლოო frozen result არ არის.
- კვლევა რჩება Draft; ფიზიკური მოწყობილობის გამეორება და დამოუკიდებელი review არ ჩატარებულა.
