# NOEMA-2026-005 — 2026-11-26 real-thread rerun and frozen-result audit

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი ანალიზი, floating-point reduction და CPU-thread შესრულება
- **კვლევითი ნაკადი:** numerical accuracy and CPU-thread reduction

## საკვლევი კითხვა

ინარჩუნებს თუ არა Neumaier-ის სრული `(sum, correction)` მდგომარეობის გაერთიანება ზუსტ reference შედეგს რეალურ Python CPU threads-ზე და აჩვენებს თუ არა შემოწმებული workload wall-time უპირატესობას შესაბამის serial baseline-თან შედარებით?

## მოკლე შეჯამება

წინა hosted GitHub Actions run [45850716742](https://github.com/maisuradzee/bibmom/actions/runs/45850716742) იყენებდა CPython 3.14.4-ს, GIL-enabled და free-threaded build-ებს, ერთ Linux x86-64 virtual runner-ზე ოთხი ხელმისაწვდომი CPU-ით. თითო runtime-ში 48 configuration და 144 measured run შესრულდა. Neumaier state merge-მა ორივე რეჟიმში 48/48 სწორი შედეგი აჩვენა; scalar Neumaier — 42/48; naive scalar partial — 0/48. ორივე რეჟიმში median wall-time speedup 1-ზე ნაკლები იყო.

ეს ცვლილება გაყინულ metadata-სა და aggregate-ებს ამოწმებს; იგი benchmark-ს თავიდან არ უშვებს და დამოუკიდებელ ფიზიკურ hardware replication-ს არ ამტკიცებს.

## მეთოდი ან ექსპერიმენტის გეგმა

- ორი დეტერმინისტული cancellation fixture: `triplet_order` და `grouped_cancellation`.
- Worker counts: 1, 2, 4 და 8; partitions: contiguous და round-robin.
- Reduction მეთოდები: naive scalar, scalar Neumaier და სრული Neumaier `(sum, correction)` state merge.
- თითო runtime-ზე 48 configuration, თითოეულზე სამი measured repetition.
- CPython 3.14.4 GIL-enabled და free-threaded build; ერთი hosted Linux x86-64 runner, ოთხი CPU affinity.
- Accuracy, median wall-time speedup, process-CPU/wall ratio და traced Python allocation ცალ-ცალკე აღირიცხა.
- Frozen metadata: `data/noema-005/threaded-rerun-2026-11-26.json`; validator: `scripts/validate_noema005_threaded_rerun.py`.

## მტკიცებულებები და ინტერპრეტაცია

### FACT

Workflow 45850716742-ის ჩანაწერი მიუთითებს ორივე runtime job-ის წარმატებით დასრულებაზე და განსხვავებული native thread ID-ების დაფიქსირებაზე. Artifact ID-ები, expiration timestamp-ები და digest-ები შენახულია frozen summary-ში.

### REPRODUCED RESULT — workflow record-ის გაყინული aggregate-ები

| Runtime | მეთოდი | სწორი run-ები | Median wall-time speedup |
|---|---|---:|---:|
| GIL enabled | Naive scalar partial | 0/48 | 0.4918× |
| GIL enabled | Scalar Neumaier partial | 42/48 | 0.7443× |
| GIL enabled | Neumaier state merge | 48/48 | 0.7539× |
| Free-threaded | Naive scalar partial | 0/48 | 0.3183× |
| Free-threaded | Scalar Neumaier partial | 42/48 | 0.9947× |
| Free-threaded | Neumaier state merge | 48/48 | 0.9519× |

Free-threaded state merge-ის median process-CPU/wall ratio იყო 2.084. ეს აჩვენებს aggregate CPU time-ს, რომელიც wall time-ს აჭარბებს, მაგრამ არ არის end-to-end wall-time speedup. ორივე runtime-ის median speedup 1.0-ზე ნაკლები დარჩა.

### Artifact provenance — წინა audit-ის მიერ დაფიქსირებული მნიშვნელობები

- GIL-enabled artifact ID `15132333526`; archive SHA-256 `b1b84fa96480fd989e6b866800004146f36a8c08b05859d3678cf32a3c094be4`; report SHA-256 `b984326a68847e2fac9b3c205a4ef4b3fb59d10e27210460c2061fc9c8ba8eaa`.
- Free-threaded artifact ID `15132228583`; archive SHA-256 `f8adbcd890c436267b6efb2f907b0d1b210d3c1f4e6ea7f2ac7500f987363f41`; report SHA-256 `f23804a230c96358082a6ae6189761e0a571ae4fadc241a4456cccddeb9b24e1`.
- წინა audit-ის ჩანაწერი ამბობს, რომ ZIP-ები ჩამოიტვირთა, digest-ები დაემთხვა და raw per-case reports ხელახლა აგრეგირდა. ეს PR ინახავს ამ ჩანაწერს; ამ ცვლილებაში artifact-ების ხელახალი ჩამოტვირთვა ან reaggregation არ ჩატარებულა.

### INFERENCE

ამ მცირე სინთეზურ Python workload-ში სრული compensation state-მა უკეთესი სიზუსტე შეინარჩუნა scalar partial-ებთან შედარებით, მაგრამ ThreadPool/runtime overhead-მა median wall-time უპირატესობა ვერ გამოაჩინა. CPU/wall ratio თავისთავად bottleneck-ს არ ადგენს.

### HYPOTHESIS

Native reduction ან უფრო დიდი memory-bandwidth-bound workload შეიძლება განსხვავებულ performance profile-ს აჩვენებდეს სრული compensation state-ის შენარჩუნებით; ეს ჯერ შემოწმებული არ არის.

### UNTESTED IDEA

შემდეგი ექსპერიმენტი შეადარებს pairwise, long-double, Neumaier-state და exact/superaccumulator მეთოდებს წინასწარ განსაზღვრულ scientific arrays-ზე, დამოუკიდებელ physical x86-64/ARM64 სისტემებზე, RSS/memory-bandwidth გაზომვით და uncertainty intervals-ით.

## წყაროები

- NOEMA GitHub Actions workflow 45850716742 — https://github.com/maisuradzee/bibmom/actions/runs/45850716742 (hosted benchmark run და artifact metadata).
- Python threading documentation — https://docs.python.org/3/library/threading.html (threading semantics და runtime constraints).
- Higham, N. J. (1993), “The Accuracy of Floating Point Summation,” SIAM Journal on Scientific Computing — https://doi.org/10.1137/0914050 (რიცხვითი შეკრების შეცდომის ანალიზი).
- Ogita, T., Rump, S. M., Oishi, S. (2005), “Accurate Sum and Dot Product,” SIAM Journal on Scientific Computing — https://doi.org/10.1137/030601818 (compensated summation და dot-product მეთოდები).
- IEEE Std 754-2019 — https://standards.ieee.org/ieee/754/6210/ (floating-point arithmetic standard).

## შემოწმების სტატუსი

- Frozen summary validator ამოწმებს workflow/run/head identity-ს, runtime protocol-ს, artifact ID-ებსა და digest-ებს, accuracy counts-ს, median wall-time-ს, CPU/wall ratio-სა და traced-allocation aggregates-ს.
- Unit tests ამოწმებს aggregate mutation-ს, speedup mutation-ს, digest mutation-სა და CLI-ს.
- ეს PR არ ასრულებს ახალ benchmark-ს, raw artifact re-download-ს ან physical-hardware replication-ს.
- კვლევა რჩება preliminary; დამოუკიდებელი numerical-method review ჯერ არ დასრულებულა.

## შემდეგი ნაბიჯები

1. დამოუკიდებელი numerical-method review.
2. Preregistered representative scientific workloads, მათ შორის memory-bandwidth-bound arrays.
3. დამოუკიდებელი physical x86-64 და ARM64 გამეორება.
4. Wall time, process CPU time, RSS და memory bandwidth ცალ-ცალკე გაზომვა.
5. Published სტატუსი არ მიენიჭოს დამოუკიდებელი რეცენზიისა და ყველა publication gate-ის დასრულებამდე.
