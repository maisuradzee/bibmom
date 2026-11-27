# NOEMA-2026-005 — 2026-11-27 hosted x86-64 threaded rerun

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** რიცხვითი ანალიზი, Python threads და floating-point reduction
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

ინარჩუნებს თუ არა Neumaier compensation-state merge სიზუსტეს ახალ hosted x86-64 runner-ზე და იძლევა თუ არა GIL-enabled/free-threaded CPython რეალურ wall-time უპირატესობას იმავე სინთეზურ workload-ზე?

## მოკლე შეჯამება

GitHub Actions run 45972740197-ზე შესრულდა ახალი CPython 3.14.4 x86-64 AWS hosted-runner batch. ორივე runtime-ში სრული Neumaier state სწორად დამრგვალდა 48/48 measured runs-ში; scalar Neumaier — 42/48; naive scalar — 0/48. თუმცა full-state median wall-time speedup GIL-enabled რეჟიმში 0.7541x, free-threaded რეჟიმში კი 0.7021x იყო. Free-threaded CPU-time/wall-time ratio 36/48 runs-ში აღემატებოდა 1.05-ს, მაგრამ ეს არ გარდაქმნილა wall-time აჩქარებად.

## არსებული ცოდნა და წყაროები

კვლევის რიცხვითი საფუძველი მოიცავს Higham-ის floating-point summation error analysis-ს, Ogita–Rump–Oishi-ის accurate sum/dot-product ალგორითმებს და IEEE 754-2019-ს. Python 3.14 free-threaded build არის optional supported build; კონკრეტული შედეგები დამოკიდებულია workload-ზე, interpreter-ზე, extension compatibility-სა და runner-ზე.

## მტკიცებულებები

- **FACT:** GitHub Actions run 45972740197-მა ორი ცალკე CPython 3.14.4 runtime job გაუშვა: GIL-enabled და free-threaded, ორივე Linux x86-64 AWS hosted runner-ზე, ოთხი available CPU-ით.
- **FACT:** ორივე raw report შეიცავს ერთსა და იმავე canonical input SHA-256 მნიშვნელობებს, 48 კონფიგურაციას, 3 measured repetition-ს თითო კონფიგურაციაზე და native thread identity ჩანაწერებს.
- **REPRODUCED RESULT:** full Neumaier compensation-state merge — 48/48 სწორად დამრგვალებული runs ორივე runtime-ში; scalar Neumaier — 42/48; naive scalar — 0/48.
- **REPRODUCED RESULT:** full-state median speedup: GIL-enabled 0.7541x (range 0.7139–0.7726); free-threaded 0.7021x (range 0.5395–0.7889).
- **REPRODUCED RESULT:** free-threaded CPU-time/wall-time ratio 1.05-ზე მაღალი იყო 36/48 runs-ში; GIL-enabled — 0/48. ეს არის aggregate CPU-use და არა wall-time speedup.
- **INFERENCE:** free-threaded build-ში worker threads რეალურად მოიხმარდა პროცესის CPU დროს პარალელურად, მაგრამ ამ Python-heavy synthetic workload-ზე overhead-მა serial wall-time baseline ვერ დაამარცხა.
- **HYPOTHESIS:** native/GIL-releasing numeric kernels ან larger compute-to-coordination ratio შეიძლება უკეთესად გამოიყენოს free-threaded execution; ეს ჯერ არ შემოწმებულა.
- **UNTESTED IDEA:** შემდეგ ეტაპზე C/OpenMP native kernel-ისა და Python orchestration-ის შედარება ერთი და იმავე frozen input-ზე.

## მეთოდი ან ექსპერიმენტის გეგმა

1. GitHub Actions artifact ZIP-ები ჩამოიტვირთა და მათი SHA-256 შედარდა artifact metadata-სთან.
2. თითოეული JSON report-ის SHA-256 ცალკე შემოწმდა.
3. canonical binary64 input hashes შედარდა წინა run-ის მნიშვნელობებს.
4. თითოეულ runtime-ში შემოწმდა 48 case: ორი layout, ორი partition, ოთხი worker count და სამი reduction method.
5. თითოეულ case-ს ჰქონდა ერთი warm-up და სამი measured repetition.
6. თითოეული measured run-ის native thread IDs უნდა შეესაბამებოდეს worker count-ს და იყოს უნიკალური.
7. process_time_ns/perf_counter_ns თანაფარდობა ცალკე ინახება; იგი არ არის speedup. tracemalloc peak არის Python-traced allocation და არა RSS.
8. Raw JSON-ები gzip+base64 სახით ინახება; reproduce_noema005_run23.py --check ამოწმებს report SHA-ებს, input hashes-ს, thread identity-ს და frozen aggregate-ს.

## შედეგები და ინტერპრეტაცია

| მეთოდი | GIL accuracy | GIL median speedup | Free-threaded accuracy | Free-threaded median speedup |
|---|---:|---:|---:|---:|
| Naive scalar | 0/48 | 0.5069x | 0/48 | 0.1675x |
| Scalar Neumaier | 42/48 | 0.7535x | 42/48 | 0.7101x |
| Neumaier state | 48/48 | 0.7541x | 48/48 | 0.7021x |

წინა hosted run 45867519546-ში free-threaded Neumaier-state median speedup 1.0181x იყო; ახალ AWS hosted run-ში 0.7021x გახდა. ორივე run-ში accuracy 48/48 დარჩა. ეს ცვლილება ადასტურებს run/runner sensitivity-ს და არა უნივერსალურ performance უპირატესობას.

## შეზღუდვები და გაურკვევლობები

- ეს არის GitHub-hosted x86-64 virtual runner და არა დამოუკიდებელი ფიზიკური მოწყობილობა.
- გამოყენებულია ორი სინთეზური cancellation layout და მხოლოდ სამი measured repetition.
- ARM64, Windows, GPU, distributed runtime და რეალური სამეცნიერო workload ამ run-ში არ შემოწმებულა.
- tracemalloc არ ზომავს სრულ RSS-ს, native allocations-ს ან DRAM bandwidth-ს.
- CPU-time/wall-time >1.05 ადასტურებს aggregate CPU consumption-ს, არა wall-time speedup-ს.
- ერთ batch-ზე დაყრდნობით სტაბილური performance distribution ვერ განისაზღვრება.

## დასკვნა

სიზუსტის მხრივ სრული Neumaier compensation state კვლავ 48/48 სწორად დამრგვალდა ორივე runtime-ში. შესრულების მხრივ ახალი hosted batch არ ადასტურებს აჩქარებას: median speedup ორივე runtime-ში 1.0-ზე დაბალია. კვლევა რჩება Preliminary/Draft.

## წყაროები

1. Higham, N. J. (1993). *The Accuracy of Floating Point Summation*. SIAM Journal on Scientific Computing, 14(4), 783–799. https://doi.org/10.1137/0914050
2. Ogita, T., Rump, S. M., & Oishi, S. (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. https://doi.org/10.1137/030601818
3. IEEE Computer Society. (2019). *IEEE Std 754-2019: IEEE Standard for Floating-Point Arithmetic*. https://standards.ieee.org/ieee/754/6210/
4. Python Software Foundation. *Python 3.14 free-threading HOWTO*. https://docs.python.org/3.14/howto/free-threading-python.html
5. GitHub Actions workflow run 45972740197. https://github.com/maisuradzee/bibmom/actions/runs/45972740197

## შემდეგი ნაბიჯები

1. ფიზიკურ x86-64 და ARM64 მოწყობილობებზე მინიმუმ 20 repetitions/configuration.
2. RSS/native allocator და memory bandwidth გაზომვა.
3. C/OpenMP native kernel-ის შედარება Python thread orchestration-თან.
4. დამოუკიდებელი numerical-method review და representative application workload.

## შემოწმების სტატუსი

- ორივე artifact ZIP-ის SHA-256 ემთხვევა GitHub artifact metadata-ს.
- ორივე extracted JSON report-ის SHA-256 ემთხვევა frozen summary-ს.
- canonical input hashes და native thread identity-ები გადამოწმებულია.
- frozen aggregate-ის reproduction შედის CI-ში.
- არ ჩატარებულა physical-device replication ან external peer review.
- სტატუსი რჩება Draft/Preliminary; Published არ არის.
