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


## Third hosted rerun — 2026-11-26, workflow 45876372172

A separate CI invocation on the INFRA proposal branch ran the same actual CPU-thread benchmark. The GIL-enabled and free-threaded jobs both passed. The raw reports were downloaded from artifacts 15144913096 and 15143614730; the ZIP hashes below matched the GitHub artifact digests, and the decompressed report hashes were independently computed before aggregation.

### REPRODUCED RESULT — third run

| Runtime | Method | Correct runs | Median wall-time speedup | Speedup range | Median process-CPU / wall |
|---|---|---:|---:|---:|---:|
| GIL enabled | Naive scalar | 0/48 | 0.4984× | 0.4410–0.5242 | 1.014 |
| GIL enabled | Scalar Neumaier | 42/48 | 0.7597× | 0.7182–0.7817 | 1.004 |
| GIL enabled | Neumaier state merge | 48/48 | 0.7593× | 0.7232–0.7819 | 1.005 |
| Free-threaded | Naive scalar | 0/48 | 0.1713× | 0.1259–0.4949 | 2.630 |
| Free-threaded | Scalar Neumaier | 42/48 | 0.7165× | 0.5675–0.8197 | 2.621 |
| Free-threaded | Neumaier state merge | 48/48 | 0.7144× | 0.5705–0.7589 | 2.582 |

Both runtimes used CPython 3.14.4 and four-CPU affinity. The runner platform was Linux x86-64 AWS virtual infrastructure. Each runtime executed 48 configurations × 3 measured repetitions; each configured worker was represented by a distinct native thread ID.

### Provenance

- GIL-enabled artifact ID 15144913096; ZIP SHA-256 `c6d0af0f76109b36a58ed74ad4768c28737cce72a770efd3e28cdd084cd6a2c5`; raw JSON SHA-256 `534e2db427a9ec0cb247c7faaef8dea4eb62ce2e3a70c467cf97b05b320a5827`.
- Free-threaded artifact ID 15143614730; ZIP SHA-256 `57027cffa4326bc833975af0912dc6f49023fdeac9bc7295c93dcf7feee64698`; raw JSON SHA-256 `3d03785c2fe68fa3a9e1da20f93447d399ae0cca52ee1f36434d08ea008f30c4`.
- Both ZIPs expire 2026-12-26; raw JSON reports are preserved under `data/noema-005/raw/run-45876372172-*.json.gz.b64`.
- Exact tested workflow head: `821582d173951550bb854164fa24a6cb3a7cce11`.

### INFERENCE and limitations

The third run's Neumaier-state method remained 48/48 correct in both runtimes, but median wall-time speedup was below 1 in both modes. The free-threaded process-CPU/wall ratio and 36/48 cases above 1.05 show parallel CPU consumption in this synthetic run, not end-to-end acceleration. Across three runs, GIL-enabled medians stayed below 1 (0.7539×, 0.7744×, 0.7593×); free-threaded medians varied (0.9519×, 1.0181×, 0.7144×). The one value above 1 did not repeat.

The third run used AWS-hosted virtual runners while the first two used Azure-hosted virtual runners, but all had four available CPUs and none was independently selected physical hardware. The experiment still uses only two synthetic cancellation layouts and three measured repetitions. This remains a preliminary reproducibility observation, not a portable performance claim.
