# NOEMA-2026-005 — Run 33 cross-architecture synthesis

- **თარიღი:** 2026-11-27
- **სტატუსი:** draft / preliminary
- **Experiment:** `NOEMA-2026-005-CROSS-ARCH-RUN33-001`
- **Evidence class:** REPRODUCED_RESULT (aggregate recomputation from two schema-validated source summaries; no new benchmark run)

## საკვლევი კითხვა

რა რჩება საერთო x86-64 და ARM64 hosted CPU-thread ექსპერიმენტებში, როდესაც ერთი და იგივე სინთეზური input hashes და benchmark protocol გამოიყენება, მაგრამ runner/backend გარემოები განსხვავდება?

## მეთოდი

შევადარე ორი საჯარო, machine-readable source summary:

- x86-64: [PR #175](https://github.com/maisuradzee/bibmom/pull/175), source summary Git blob `e78aff2d128553a30bbb550013e730887437f571`, source head `e4863a1ae570b41a54c53389269f05846aacd13d`; workflow runs 46034414138, 46034729099 და 46035393777.
- ARM64: [PR #171](https://github.com/maisuradzee/bibmom/pull/171), merged; source summary Git blob `34075bd02a297f6fee925ed53c1f63e1b4ac81a9`, main snapshot `d4f06672208d808f8827b1528b9a07abe107d111`; workflow run 46032894362.

ორივე summary მიუთითებს CPython 3.14.4-ზე, 65,536 repeat-count-ზე, 196,608 input value/layout-ზე, 1/2/4/8 worker-ზე, ორ ერთნაირ input layout-ზე, contiguous/round-robin partition-ზე, სამ reduction მეთოდზე, ერთ warm-up-ზე და სამ measured repetition-ზე. ორივე source summary-ში input SHA-256-ები ემთხვევა.

არ გამიკეთებია raw report-ების ახალი ჩამოტვირთვა ან ახალი benchmark run. ეს არის უკვე შემოწმებული aggregate summary-ების შედარება. Raw reports და native thread IDs არ გადმომიტანია.

## FACT

- x86-64 წყარო აერთიანებს 6 report-ს, 288 configuration-ს და 864 measured run-ს.
- ARM64 წყარო აერთიანებს 4 report-ს, 192 configuration-ს და 576 measured run-ს.
- ჯამი: 10 hosted runner/runtime report, 480 configuration და 1,440 measured run.
- ორივე არქიტექტურაში გამოყენებული input SHA-256-ები იდენტურია.
- x86-64 workflow 46034729099-ში GIL report AWS runner-ზე შესრულდა, ხოლო free-threaded report Azure-ზე; ეს matched backend pair არ არის.

## REPRODUCED RESULT

| მაჩვენებელი | x86-64 hosted | ARM64 hosted | ჯამი |
|---|---:|---:|---:|
| Neumaier-state exact-reference | 288/288 | 192/192 | **480/480** |
| Scalar Neumaier exact-reference | 252/288 | 168/192 | **420/480** |
| Naive scalar exact-reference | 0/288 | 0/192 | **0/480** |
| Free-threaded CPU/wall >1.05 | 324/432 | 202/288 | ცალკე შენარჩუნებულია |
| GIL CPU/wall >1.05 | 0/432 | 4/288 | ცალკე შენარჩუნებულია |

Neumaier-state median speedup-ის ათი runner/runtime report-ის შედეგებიდან მხოლოდ ორი იყო 1.0-ზე მეტი — ორივე x86-64 Azure free-threaded report (1.317241× და 1.174008×). დანარჩენი რვა report, მათ შორის ოთხივე ARM64 report, 1.0-ზე ქვემოთ იყო.

სრული per-report მნიშვნელობები და denominator-ები მოცემულია [machine-readable synthesis-ში](../../data/noema-005/cross-architecture-run33-summary-2026-11-27.json).

## INFERENCE

- ამ სინთეზურ input-ებზე Neumaier compensation-state-ის exact-reference სიზუსტე ყველა 480 configuration-ში შენარჩუნდა.
- CPU/wall >1.05 აჩვენებს პროცესის aggregate CPU დროის wall-time-ზე გადაჭარბებას; ის არ უდრის throughput-ს ან speedup-ს.
- Azure x86-64 free-threaded შედეგების 1.0-ზე მეტი median არ გადადის AWS x86-64 ან ARM64 hosted report-ებში. ეს არის backend/runner-ზე დამოკიდებული შედეგი.
- ამ მონაცემებით **არ შეიძლება** დასკვნა, რომ x86-64 არქიტექტურა ARM64-ზე სწრაფია ან free-threading ზოგადად აჩქარებს reduction-ს: runner, backend, OS, CPU model, available CPUs და scheduler ერთმანეთისგან კონტროლირებული არ არის.

## HYPOTHESIS

Azure x86-64 hosted free-threaded runner-ის კონკრეტული გარემო შესაძლოა ამ synthetic workload-ის chunk/merge overhead-ს სხვაგვარად აბალანსებდეს. მიზეზი ჯერ არ არის იზოლირებული.

## UNTESTED IDEA

შემდეგი კვლევა უნდა ჩატარდეს კონტროლირებულ ფიზიკურ x86-64 და ARM64 host-ებზე, ერთნაირი OS/runtime build-ით, CPU model/microcode/power policy-ის ჩანაწერით, მინიმუმ 20 measured repetition-ით თითო configuration-ზე, RSS/native allocation, DRAM bandwidth, per-thread CPU clock და context-switch counters-ით. საჭიროა confidence interval-ები და workload-ის რამდენიმე ზომა.

## შეზღუდვები

- GitHub-hosted synthetic CI; არა დამოუკიდებელი physical-device ან external-laboratory replication.
- მხოლოდ სამი measured repetition თითო configuration-ზე.
- x86-64 run 46034729099 backend-confounded-ია.
- ARM64 Ubuntu runner ოთხ process CPU-ს, macOS runner სამს ანგარიშობს.
- `tracemalloc` არ ზომავს process RSS-ს, native allocator-ს ან DRAM bandwidth-ს.
- ეს synthesis ხელახლა ითვლის მხოლოდ უკვე შენახულ aggregate summary-ებს; raw report-ების დამოუკიდებელი ხელახალი დამუშავება არ ჩატარებულა.
- დამოუკიდებელი numerical-method review ჯერ არ დასრულებულა.

**სტატუსი რჩება preliminary. Published არ არის.**
