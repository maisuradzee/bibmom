# NOEMA-2026-005 — რეალური CPU threads-ის reduction benchmark

- **ID:** NOEMA-2026-005 (კვლევის გაგრძელება; ახალი დამოუკიდებელი კვლევის ID არ იქმნება)
- **სტატუსი:** draft — მეთოდი და ადგილობრივი GIL-control შედეგი; free-threaded CI გაშვება ჯერ pending
- **თარიღი:** 2026-11-25
- **სფერო:** რიცხვითი ანალიზი, პარალელური გამოთვლები, პროგრამული სისტემები
- **ავტორი/მომზადების სისტემა:** NOEMA research automation

## საკვლევი კითხვა

ინარჩუნებს თუ არა Neumaier-ის თითოეული worker-ის `(sum, compensation)` მდგომარეობის გადაცემა სწორად დამრგვალებულ ჯამს რეალური OS threads-ის გამოყენებისას? როგორ განსხვავდება CPU დრო, wall-clock დრო და Python-ის მიერ ტრეკირებული მეხსიერება GIL-იან და free-threaded CPython-ში?

## მოკლე შეჯამება

NOEMA-005-ის წინა sharded reduction იყო დეტერმინისტული სიმულაცია და არა რეალური thread benchmark. ამ დამატებაში გამოიყენება `ThreadPoolExecutor`, `threading.Barrier` და native thread ID-ები, რათა დადასტურდეს, რომ თითოეული worker ცალკე OS thread-ზე გაეშვა. შედარებულია naive scalar partial, Neumaier scalar partial და Neumaier `(sum, compensation)` state merge.

ადგილობრივ CPython 3.13.5 GIL-enabled კონტროლში 36 threaded configuration შესრულდა. ყველა configured worker სხვადასხვა native thread-ზე გაეშვა, მაგრამ process CPU / wall-time ratio დაახლოებით 0.96–0.99 იყო — ამ გარემოში CPU-bound Python bytecode-ის რეალური მრავალბირთვიანი პარალელიზმი არ დაფიქსირებულა. `grouped_cancellation` შემთხვევაში 2-worker contiguous დაყოფაზე Neumaier scalar partial-მა 0/2 სწორად დამრგვალებული შედეგი აჩვენა, ხოლო compensation-state merge-მა 2/2. ეს ადგილობრივი, მცირე smoke-run-ია და არა სრული benchmark.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

წინა სიმულაციამ აჩვენა, რომ scalar partial-მა შეიძლება worker-ის შიდა კომპენსაცია დაკარგოს. რეალურ thread pool-ში ამას ემატება GIL-ის რეჟიმი, thread scheduling, CPU quota და runtime overhead. ამიტომ მხოლოდ შუალედური ჯამების მათემატიკური სიმულაცია საკმარისი არ არის შესრულების ან რეალური threading-ის დასადასტურებლად.

## არსებული ცოდნა და წყაროები

1. **Sam Gross — PEP 703, “Making the Global Interpreter Lock Optional in CPython.”** Python Enhancement Proposals, PEP 703. შეიქმნა 2023-01-09; Steering Council-ის მიღების გადაწყვეტილება 2023-10-24. https://peps.python.org/pep-0703/ — პირველადი ტექნიკური სპეციფიკაცია, რომელიც აღწერს GIL-ის შეზღუდვას და free-threaded build-ის მიზანს. წვდომა: 2026-11-25.
2. **Python Software Foundation — Python 3.14 HOWTO, “Python support for free threading.”** გამოცემის ცალკე თარიღი გვერდზე მითითებული არ არის. https://docs.python.org/3.14/howto/free-threading-python.html — აღწერს free-threaded build-ს, `sys._is_gil_enabled()`-ს და იმ შემთხვევებს, როდესაც extension-მა შეიძლება GIL ხელახლა ჩართოს. წვდომა: 2026-11-25.
3. **Python Software Foundation — Python 3.14 Library Reference, `threading`.** გამოცემის ცალკე თარიღი გვერდზე მითითებული არ არის. https://docs.python.org/3.14/library/threading.html — აღწერს ThreadPoolExecutor-სა და GIL-ის გავლენას CPU-bound Python კოდზე. წვდომა: 2026-11-25.
4. **Python Software Foundation — Python 3.14 Library Reference, `time`.** https://docs.python.org/3.14/library/time.html — `perf_counter_ns()` და process-wide `process_time_ns()` დროის საზომები. გამოცემის ცალკე თარიღი მითითებული არ არის. წვდომა: 2026-11-25.
5. **Python Software Foundation — Python 3.14 Library Reference, `tracemalloc`.** https://docs.python.org/3.14/library/tracemalloc.html — Python allocation tracing და peak memory; არ უდრის მთლიანი RSS-ის გაზომვას. გამოცემის ცალკე თარიღი მითითებული არ არის. წვდომა: 2026-11-25.
6. **GitHub Actions — actions/setup-python, Advanced usage.** https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md — free-threaded ვერსიის `t` suffix-ის გამოყენება. ცოცხალი დოკუმენტაციაა; გამოცემის თარიღი მითითებული არ არის. წვდომა: 2026-11-25.

## მტკიცებულებები

### FACT — დადასტურებული წყაროებით

- CPython-ის ჩვეულებრივ GIL-enabled build-ში ერთდროულად მხოლოდ ერთი thread ასრულებს Python bytecode-ს; thread-ები მაინც ქმნის concurrency-ს და სასარგებლოა I/O-bound სამუშაოებისთვის.
- CPython 3.13-დან ხელმისაწვდომია free-threaded build, რომელსაც GIL-ის გამორთვა შეუძლია. GIL-ის ფაქტობრივი მდგომარეობა უნდა შემოწმდეს გაშვებისას; build-ის მხარდაჭერა თავისთავად არ ნიშნავს, რომ GIL ნამდვილად გამორთულია.
- `process_time_ns()` ზომავს მიმდინარე პროცესის user/system CPU დროს, ხოლო `perf_counter_ns()` გამოიყენება elapsed wall time-ისთვის.
- `tracemalloc` Python-ის მიერ ტრეკირებულ allocation-ებს ზომავს და არა სრულ process RSS-ს ან ყველა native allocation-ს.

### REPRODUCED RESULT — ადგილობრივი GIL-enabled control run

- გარემო: CPython 3.13.5, Linux 6.18.57, x86_64; CPU affinity: 5 CPU; GIL ჩართულია.
- მონაცემები: ორი synthetic layout, თითოეულში N=16,384 და 49,152 binary64 მნიშვნელობა; ზუსტი ჯამი 16,384.
- worker-ები: 1, 2, 4; partition: contiguous და round-robin; მეთოდები: naive scalar, Neumaier scalar, Neumaier state.
- warmup: 1; გაზომილი გამეორება: 2; სულ 36 threaded configuration.
- ყველა configuration-ში დაფიქსირდა მოთხოვნილი რაოდენობის განსხვავებული native thread ID.
- `triplet_order`/contiguous შემთხვევაში Neumaier scalar და state ორივე 2/2 სწორად დამრგვალდა; naive scalar — 0/2.
- `grouped_cancellation`/2 workers/contiguous შემთხვევაში Neumaier scalar — 0/2; Neumaier state — 2/2; naive scalar — 0/2.
- CPU-time/wall-time ratio ყველა ამ ნაჩვენებ GIL-enabled configuration-ში 1-ზე დაბალი იყო (დაახლოებით 0.96–0.99), რაც CPU-bound Python კოდისთვის მრავალბირთვიან პარალელურ შესრულებას არ ადასტურებს.
- შერჩეული შედეგების JSON: `data/noema-005/threaded-benchmark-local-cpython-3.13.5-gil-summary.json`; სრული 36-configuration ანგარიში ინახება ცალკე raw JSON ფაილად, SHA-256 `d5ef839ad32d9515dc3c78555f33abc43e1eae3ccc8a3f0050dc13686bc65717`.

ეს შედეგები არის ერთი გარემოს მცირე კონტროლი. ისინი არ ადასტურებს free-threaded შესრულებას და არ უნდა განზოგადდეს სხვა CPU/runtime-ზე.

## კონკურენტი ახსნები

- ThreadPoolExecutor-ის სიჩქარის ცვლილება შეიძლება გამოწვეული იყოს thread startup/scheduling overhead-ით და არა თვითონ შეკრების ალგორითმით.
- process CPU დროის ზრდა შეიძლება შეზღუდოს runner-ის CPU quota-მ ან სხვა პროცესების დატვირთვამ.
- GIL-ის გამორთვისასაც შეიძლება არსებობდეს lock contention, memory bandwidth bottleneck ან runtime overhead.
- scalar partial-ის სიზუსტის დაკარგვა დამოკიდებულია მონაცემთა დაყოფასა და მიმდევრობაზე; ის ყველა შეყვანაზე ერთნაირად არ გამოვლინდება.

## ჰიპოთეზა

**HYPOTHESIS:** free-threaded CPython-ში Neumaier compensation-state merge შეინარჩუნებს ამ synthetic შემთხვევების სწორად დამრგვალებულ შედეგს ყველა worker count/partition-ზე, ხოლო CPU-time/wall-time ზოგ კონფიგურაციაში 1-ს გადააჭარბებს. სიჩქარის გაუმჯობესება გარანტირებული არ არის.

## შემოწმების მეთოდი

კოდი: `scripts/benchmark_noema005_threaded_reduction.py`.

ტესტები: `tests/test_benchmark_noema005_threaded_reduction.py`.

პროტოკოლი: `data/noema-005/threaded-benchmark-protocol.json`.

- ორი input layout: `[1e16, 1, -1e16]` triplet order და grouped cancellation.
- სრული CI run-ის default N=65,536; თითო layout 196,608 binary64 მნიშვნელობა; ზუსტი ჯამი N.
- worker count: 1, 2, 4, 8; partition: contiguous და round-robin.
- მეთოდები: naive scalar partial, Neumaier scalar partial, Neumaier state merge.
- serial baseline: naive, Neumaier, math.fsum.
- runtime matrix: CPython 3.14.4 GIL-enabled და CPython 3.14.4t free-threaded; ორივე Ubuntu 24.04 runner-ზე.
- warmup 1; measured repetitions 3; შემთხვევითი seed არ გამოიყენება, რადგან input deterministic-ია.
- თითოეული worker-ის native thread ID ინახება; run ჩაიშლება, თუ worker-ები ცალკე native thread-ებზე არ გაეშვა.
- იზომება median wall time, process CPU time, მათი შეფარდება და tracemalloc peak delta.
- performance threshold არ გამოიყენება; შედეგები გარემოსთან ერთად უნდა განიმარტოს.

## შედეგები და ინტერპრეტაცია

- **REPRODUCED RESULT:** ადგილობრივი GIL-enabled control run აღწერილია ზემოთ.
- **PENDING:** GitHub Actions-ის 3.14.4 და 3.14.4t სრული benchmark; სანამ ორივე job არ დასრულდება, free-threaded დასკვნა არ კეთდება.
- **INFERENCE:** scalar worker partial-ების შენახვა შეიძლება არ იყოს საკმარისი, რადგან worker-ის შიდა compensation იკარგება; state merge ამ ინფორმაციას ინარჩუნებს.

## შეზღუდვები და გაურკვევლობები

- მხოლოდ ხელოვნური cancellation მონაცემებია გამოყენებული; რეალური სამეცნიერო ან ფინანსური dataset არ გამოიყენება.
- ამ ციკლის CI benchmark არის Ubuntu x86_64-ზე; ARM, Windows და macOS რეალური threaded benchmark არ ჩატარებულა.
- free-threaded CPython-ის შედეგები დამოკიდებულია runtime ვერსიასა და CPU-ზე; free-threaded რეჟიმი ჯერ evolving ტექნოლოგიაა.
- thread pool-ის შექმნისა და scheduling-ის ხარჯი გაზომვაში შედის.
- process CPU დრო პროცესის საერთო დროა და შეიძლება runner-ის scheduling/CPU quota-ით შეიცვალოს.
- tracemalloc არ ზომავს მთლიან RSS-ს.
- GPU, NumPy/BLAS, OpenMP, multiprocessing და network-distributed execution არ შემოწმებულა.

## ეთიკა და უსაფრთხოება

მონაცემები სინთეზურია და პირად/სენსიტიურ ინფორმაციას არ შეიცავს. გარე მონაცემთა ლიცენზია არ გამოიყენება. benchmark არ უნდა ჩაითვალოს კრიტიკული სისტემის სიზუსტის ან წარმადობის გარანტიად.

## დასკვნა

რეალური native threads-ის კონტროლი შესრულდა GIL-enabled გარემოში. პირველადი შედეგი ადასტურებს, რომ thread-ების რაოდენობის გაზრდა თავისთავად CPU პარალელიზმს არ ნიშნავს. scalar Neumaier partial-ის ერთ კონკრეტულ დაყოფაში კომპენსაციის დაკარგვა დაფიქსირდა; state merge-მა ეს კონკრეტული შემთხვევა შეინარჩუნა. free-threaded benchmark ჯერ შესასრულებელია.

## ცვლილებების ისტორია

- 2026-11-25 — დაემატა რეალური ThreadPoolExecutor benchmark, GIL-mode detection, native thread ID verification, CPU/wall timing, memory tracing და GIL-enabled local control JSON.
- შემდეგი ცვლილება — GitHub Actions free-threaded run-ის შედეგების დამატება და independent CPU architecture validation.
