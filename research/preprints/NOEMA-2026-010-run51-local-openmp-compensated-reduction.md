# NOEMA-005 Run 51 — რეალური OpenMP CPU threads და compensated reduction

- **ID:** NOEMA-2026-010
- **სტატუსი:** preliminary
- **მტკიცებულების სტატუსი:** REPRODUCED RESULT
- **თარიღი / ბოლო განახლება:** 2026-11-28
- **სფერო / გეოგრაფიული ფარგლები:** რიცხვითი ანალიზი; ერთი Linux x86-64 ვირტუალიზებული გარემო
- **კვლევითი ნაკადი:** NOEMA-005 — რიცხვითი სიზუსტე და პარალელური გამოთვლები

## საკვლევი კითხვა

ინარჩუნებს თუ არა თითოეული OpenMP worker-ის სრული Neumaier `(sum, correction)` state-ის შენარჩუნება და ორივე კომპონენტის შემდგომი compensated merge სწორ binary64 ჯამს adversarial cancellation მიმდევრობებზე, naive partial, pairwise partial და `long double` ალტერნატივებთან შედარებით; რა runtime-სა და პროცესის CPU დროს იძლევა 1, 2, 4, 5 და 8 რეალური OpenMP thread?

## ადამიანური სარგებელი და პრიორიტეტი

- **ვის ეხმარება:** სამეცნიერო/საინჟინრო გამოთვლების, სიმულაციების, აგრეგაციებისა და მონაცემთა დამუშავების სისტემების შემქმნელებს.
- **სავარაუდო მასშტაბი:** პოტენციურად ფართო, მაგრამ ამ ექსპერიმენტით რეალური მომხმარებლების ან production სისტემების ზემოქმედება არ გაზომილა.
- **გადაუდებლობა:** საშუალო; რიცხვითი სიზუსტის შეცდომა შეიძლება შეუმჩნევლად გავრცელდეს downstream გამოთვლებში.
- **წარმატების საზომი:** ორივე წინასწარ განსაზღვრულ მიმდევრობაზე ყველა გაზომილ worker-count-ში ზუსტად სწორი binary64 შედეგი; raw timing/CPU samples-ის hash-ით დაცვა და ხელახალი შემოწმება.

## მოკლე შეჯამება

2026-11-28 ადგილობრივ Linux x86-64 გარემოში შესრულდა OpenMP C harness 2 სინთეზურ layout-ზე, 36,000,000 binary64 ელემენტით თითო layout-ზე (288,000,000 input bytes), 1 warm-up-ითა და 5 გაზომილი გამეორებით თითოეულ 48 მეთოდი/layout/worker კონფიგურაციაზე. Full Neumaier state-მა 5/5 სწორი შედეგი მიიღო ორივე layout-ზე და ყველა მოთხოვნილ worker-count-ში. Naive და pairwise ვარიანტებმა ამ კონკრეტულ adversarial input-ებზე 0/5 სწორი შედეგი მიიღეს. შედეგი ერთი ვირტუალიზებული გარემოს გამეორებადი ექსპერიმენტია და არა bare-metal დამოუკიდებელი გამეორება ან ზოგადი performance მტკიცება.

## მტკიცებულების ეტიკეტები

- **FACT:** გარემო იყო Linux x86-64, Intel Xeon Platinum 8573C ვირტუალიზებული host, CPU IDs `0-4`, cgroup quota `4.0` CPU, GCC 14.2.0, OpenMP ჩართული და `LDBL_MANT_DIG=64`. 5 და 8 worker-იანი კონფიგურაციები CPU quota-ს გადაჭარბებული დიაგნოსტიკური შემთხვევებია.
- **REPRODUCED RESULT:** 2 layout × 24 case = 48 case; თითოეულ case-ში 1 warm-up და 5 გაზომილი გამეორება. Full Neumaier state-მა 48/48 case-ში 5/5 სწორად დააბრუნა. Raw JSONL gzip/base64 არტეფაქტი და C source SHA-256 დაცულია.
- **INFERENCE:** თითოეული worker-ის მხოლოდ scalar partial sum-ის გადაცემა საკმარისი არ არის იმ შემთხვევაში, როდესაც worker-local rounding error correction იკარგება. ამ synthetic test-ზე სრული `(sum, correction)` state-ის merge აუცილებელი აღმოჩნდა.
- **HYPOTHESIS:** უფრო ფართო exponent range-ზე და განსხვავებულ cancellation/conditioning პროფილებზე fixed-width binned ან exact accumulator შეიძლება უკეთესად აკონტროლებდეს სიზუსტეს, მაგრამ memory/runtime ფასი ცალკე უნდა გაიზომოს.
- **UNTESTED IDEA:** NUMA-aware hierarchical merge, exact/binned accumulator და cache/DRAM counter-ებით benchmark bare-metal x86-64 და ARM64 მოწყობილობებზე.

## არსებული ცოდნა და წყაროები

1. Higham, N. J. (1993). *The Accuracy of Floating Point Summation*. SIAM Journal on Scientific Computing, 14(4), 783–799. https://doi.org/10.1137/0914050 — floating-point summation error analysis.
2. Ogita, T., Rump, S. M., & Oishi, S. (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. https://doi.org/10.1137/030601818 — compensated/accurate summation methods.
3. IEEE Computer Society. (2019). *IEEE Std 754-2019: IEEE Standard for Floating-Point Arithmetic*. https://standards.ieee.org/ieee/754/6210/ — binary floating-point arithmetic semantics.

## მონაცემთა წარმოშობა და საჭიროებები

- **მონაცემთა წყარო / მფლობელი:** NOEMA-ს მიერ გენერირებული სინთეზური input; გარე ან პირადი მონაცემი არ გამოყენებულა.
- **ვერსია / პერიოდი:** Run 51, 2026-11-28.
- **ფაილები:** `scripts/noema005_run51_openmp.c`; `data/noema-005/run51-local-openmp-report-2026-11-28.json`; `data/noema-005/raw/run51-local-openmp-2026-11-28.jsonl.gz.b64`.
- **Input:** `N=12,000,000`; triplet `[2^53, 1, -2^53]` განმეორებით; grouped `[2^53]*N + [1]*N + [-2^53]*N`. ზუსტი მათემატიკური ჯამი ორივე შემთხვევაში `N`-ია.
- **Source SHA-256:** `5959f479e7f2b45a298975aeed13f3b919a87a77bff64f2b8d649ba72d35d60b`.
- **Raw stdout SHA-256:** `708ba0d32a7dcf2dfc6888f12f8f6729793b8381e9cc32db23192746848933f7`.
- **Compressed raw SHA-256:** `faad5cac57d5198fc3e1d162cd1ed26f31b87b69970d7286d036b820d44321e6`.
- **Build:** `gcc -O3 -std=c11 -fopenmp -fno-fast-math -ffp-contract=off -Wall -Wextra -Werror scripts/noema005_run51_openmp.c -lm`.
- **Run:** `./noema005_run51_openmp 12000000 5 1`.

## შემოწმების მეთოდი

- 4 serial მეთოდი: naive, Neumaier, `long double`, recursive pairwise.
- 4 OpenMP მეთოდი: naive worker partials, full Neumaier `(sum, correction)` state, `long double` partials, pairwise worker partials.
- მოთხოვნილი worker-count: 1, 2, 4, 5, 8; თითოეული run-ში ფაქტობრივი thread-count `omp_get_num_threads()`-ით ჩაიწერა.
- 2 input layout; თითო layout 36 მილიონი ელემენტი / 288 MB.
- 1 warm-up და 5 timed repetition თითო case-ზე; wall time `CLOCK_MONOTONIC`, process CPU time `CLOCK_PROCESS_CPUTIME_ID`.
- correctness oracle: ზუსტი მთელი `N=12,000,000`, რომელიც ამ მასშტაბზე binary64-ში ზუსტად წარმოდგენადია.
- compiler flags კრძალავს fast-math გარდაქმნებს და floating-point contraction-ს.

## შედეგები და ინტერპრეტაცია

| მეთოდი | Triplet | Grouped |
|---|---:|---:|
| Serial naive | 0/5 | 0/5 |
| Serial Neumaier | 5/5 | 5/5 |
| Serial long double (`mant_dig=64`) | 5/5 | 0/5 |
| Serial pairwise | 0/5 | 0/5 |
| OpenMP naive partials — ყველა worker-count | 0/5 | 0/5 |
| OpenMP full Neumaier state — ყველა worker-count | 5/5 | 5/5 |
| OpenMP long-double partials | 5/5 | 0/5 |
| OpenMP pairwise partials | 0/5 | 0/5 |

**REPRODUCED RESULT:** OpenMP full Neumaier state-ის median wall-time (ms) triplet layout-ზე იყო 1/2/4/5/8 worker-ისთვის 59.829 / 33.100 / 22.936 / 24.950 / 23.541; grouped layout-ზე 62.562 / 31.514 / 31.224 / 28.997 / 23.997. ამ ერთ run-ში worker-count-ის მიხედვით მონოტონური scaling არ გამოვლინდა; 5/8 worker-იანი შედეგები quota/virtualized scheduling-ის გამო მხოლოდ დიაგნოსტიკურია და speedup-ის ზოგად მტკიცებად არ გამოიყენება.

**შეზღუდვა:** cgroup CPU quota 4 CPU იყო, მიუხედავად 5 ხილული CPU ID-ისა. ამიტომ 5 და 8 worker-იანი timing შედეგები oversubscription/burst დიაგნოსტიკაა და არა სუფთა scaling curve. Effective input-scan GiB/s არის bytes/time შეფასება; ეს არ არის DRAM hardware counter. Peak RSS დაახლოებით 282,000 KiB იყო თითო layout-ის პროცესულ მაქსიმუმზე და არა თითოეული ალგორითმის ცალკე allocation.

## კონკურენტი ახსნები და დამოუკიდებელი გამეორება

- შედეგები სპეციფიკურია ორი adversarial მიმდევრობისთვის; სხვა განაწილებები, signed zero, subnormal, overflow/underflow, NaN/Infinity და სხვადასხვა exponent distribution არ შემოწმებულა.
- `long double` შედეგი დამოკიდებულია პლატფორმის mantissa სიგანეზე; ამ გარემოში `LDBL_MANT_DIG=64`.
- ეს ერთი ვირტუალიზებული გარემოა. სხვა ფიზიკურ x86-64 ან ARM64 მოწყობილობაზე დამოუკიდებელი გამეორება არ ჩატარებულა.
- Timing-ის run-to-run variability, CPU quota და virtualized scheduling speedup-ის განზოგადებას ზღუდავს.

## ინოვაცია / პრაქტიკული გადაწყვეტა

- **პროტოტიპი:** OpenMP reduction pattern, რომელიც თითო worker-ის სრულ Neumaier state-ს ინახავს და merge-ისას ორივე კომპონენტს compensated accumulator-ში ამატებს.
- **ადამიანური სარგებელი:** numerical reliability-ის გაუმჯობესების შესაძლო გზა პარალელურ scientific/engineering aggregation-ში.
- **განხორციელებადობა:** C/OpenMP პროტოტიპი მცირე და პორტირებადია; ზუსტი accumulator-ის memory/runtime trade-off ჯერ შესაფასებელია.
- **უსაფრთხოება / failure modes:** არ გამოიყენოთ როგორც production correctness guarantee ამ ორი synthetic test-ის საფუძველზე; input domain, overflow policy, NaN policy და reference oracle კონკრეტული ამოცანისთვის ცალკე უნდა განისაზღვროს.
- **შემდეგი ტესტი:** bare-metal x86-64 და ARM64, pairwise/binned/exact accumulator, RSS და hardware DRAM counters, დამოუკიდებელი reviewer.

## შეზღუდვები და გაურკვევლობები

არ ჩატარებულა bare-metal ან მეორე მოწყობილობის დამოუკიდებელი გამეორება; არ გაზომილა hardware DRAM bandwidth, NUMA locality, cache misses ან energy; არ შემოწმებულა arbitrary real-world data. `REPRODUCED RESULT` ეხება მხოლოდ დაცულ synthetic raw artifact-სა და ამ გარემოში შესრულებულ C harness-ს. კვლევა არ არის დამოუკიდებლად რეცენზირებული.

## დასკვნა

ამ კონკრეტულ adversarial binary64 workload-ზე full Neumaier state-მა შეინარჩუნა ზუსტი შედეგი serial და OpenMP worker-count-ების ყველა გაზომილ კონფიგურაციაში. Scalar naive/pairwise partials და ამ გარემოს 64-bit-mantissa `long double` grouped layout-ზე ჩავარდა. 5/8 worker timing-ები CPU quota-ს გადაჭარბებითაა მიღებული და ზოგად speedup-ს არ ამტკიცებს. შემდეგი პრიორიტეტია bare-metal დამოუკიდებელი გამეორება და exact/binned accumulator-ის შედარება.

## ცვლილებების ისტორია

- 2026-11-28 — Run 51 ადგილობრივი OpenMP benchmark; raw artifact, source hash, verifier, schema და CI regression test დაემატა.
