# NOEMA-2026-005 — three-run real-thread comparison and raw-report reproduction

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** floating-point reduction, numerical accuracy and CPU-thread performance
- **მტკიცებულების სტატუსი:** preliminary / reproduced raw-report aggregates

## საკვლევი კითხვა

შენარჩუნებულია თუ არა Neumaier-ის სრული `(sum, correction)` state-ის რიცხვითი სიზუსტე რეალურ Python CPU threads-ზე და რამდენად სტაბილურია მისი wall-time შედეგი განმეორებით hosted-runner ექსპერიმენტებში?

## მოკლე შეჯამება

ამ შედარებაში გადამოწმებულია სამი hosted GitHub Actions run: 45850716742, 45867519546 და ახალი 45897707859. მესამე run-ის ორივე artifact ZIP-ის SHA-256 დაემთხვა GitHub API metadata-ს; raw JSON report-ები დამოუკიდებლად დაიჰეშა, ხელახლა აგრეგირდა და gzip+base64 ფორმით ამ PR-ში ინახება.

Neumaier-state მეთოდმა სამივე run-ში 48/48 სწორად დამრგვალებული შედეგი შეინარჩუნა შესაბამის runtime-ებში. მესამე hosted run-ში free-threaded median speedup 1.2589× იყო matching serial Neumaier baseline-თან, ხოლო GIL-enabled — 0.7576×. ეს ერთი ახალი run-ის შედეგია და არა პორტატული აჩქარების მტკიცებულება; serial math.fsum ამ fixture-ებზე threaded Neumaier-state-ზე მნიშვნელოვნად სწრაფი დარჩა.

## მეთოდი ან ექსპერიმენტის გეგმა

- ორი workflow run: [45850716742](https://github.com/maisuradzee/bibmom/actions/runs/45850716742) და [45867519546](https://github.com/maisuradzee/bibmom/actions/runs/45867519546).
- ორივე run იყენებდა CPython 3.14.4-ს, Linux x86-64 Azure hosted VM-ს და ოთხ ხელმისაწვდომ CPU-ს; ერთი GIL-enabled, მეორე free-threaded build.
- თითო runtime-ში 48 configuration: 2 synthetic cancellation fixture × 4 worker count (1/2/4/8) × 2 partition (contiguous/round-robin) × 3 reduction method; თითო configuration-ზე სამი measured repetition.
- სამი მეთოდი: naive scalar partial, scalar Neumaier partial და სრული Neumaier `(sum, correction)` state merge.
- CPU/wall ratio, wall-time speedup და `tracemalloc` peak ცალ-ცალკე აგრეგირდა.
- ახალი run-ის raw reports ინახება gzip+base64 ტექსტურ ფაილებად; script decompress-ს უკეთებს, ამოწმებს raw report SHA-256-ს და თავიდან ითვლის ყველა frozen aggregate-ს.

## შედეგები

### Neumaier-state accuracy და median wall-time speedup

| Runtime | Run 45850716742 | Run 45867519546 | Accuracy თითო run-ში |
|---|---:|---:|---:|
| GIL-enabled | 0.7539× | 0.7744× | 48/48 ორივეში |
| Free-threaded | 0.9519× | 1.0181× | 48/48 ორივეში |

### მეორე run-ის ყველა მეთოდის შედეგები

| Runtime | Method | Correct | Median speedup | Median CPU/wall |
|---|---|---:|---:|---:|
| GIL-enabled | Naive scalar | 0/48 | 0.4951× | 1.012 |
| GIL-enabled | Scalar Neumaier | 42/48 | 0.7565× | 1.008 |
| GIL-enabled | Neumaier state | 48/48 | 0.7744× | 1.008 |
| Free-threaded | Naive scalar | 0/48 | 0.3682× | 2.258 |
| Free-threaded | Scalar Neumaier | 42/48 | 0.9724× | 2.412 |
| Free-threaded | Neumaier state | 48/48 | 1.0181× | 2.235 |

### FACT

- GitHub API-მ ახალი run-ის ორი artifact დააბრუნა: IDs 15140723434 და 15140468799. მათი archive SHA-256 მნიშვნელობები რეალურად ჩამოტვირთულ ZIP bytes-ს დაემთხვა.
- თითო report-ის raw SHA-256 გადამოწმდა; თითო runtime-ში 48 case იყო.
- თითო case-ის სამივე measured run-ში native thread ID-ების რაოდენობა ემთხვეოდა configured worker count-ს; ეს ადასტურებს native worker-thread-ების გამოყენებას და არა performance gain-ს.

### REPRODUCED RESULT

- ახალი raw reports-იდან დამოუკიდებლად თავიდან დაითვალა accuracy, median speedup, speedup range, median process-CPU/wall ratio, median traced allocation და CPU-parallelism threshold counts.
- ახალი free-threaded Neumaier-state median speedup იყო 1.0181×, მაგრამ range 0.7023×–1.1350×; მხოლოდ ერთი hosted run-ის სამი repetition-იანი configuration-ების median-ია ეს მნიშვნელობა.

### INFERENCE

რიცხვითი სიზუსტე ორივე run-ში სტაბილური იყო, მაგრამ performance result run-sensitive აღმოჩნდა. ერთი free-threaded median-ის 1.0-ზე ოდნავ გადაკვეთა არ წარმოადგენს სანდო აჩქარების მტკიცებულებას. CPU/wall ratio >1.0 აჩვენებს aggregate CPU consumption-ს, მაგრამ თავისთავად wall-time speedup-ს არ ნიშნავს.

### HYPOTHESIS

უფრო ხანგრძლივი workloads, native code ან memory-bandwidth-bound arrays შეიძლება განსხვავებულ პროფილს აჩვენებდეს; ეს ჯერ არ შემოწმებულა დამოუკიდებელ ფიზიკურ hardware-ზე.

### UNTESTED IDEA

წინასწარ დარეგისტრირებული benchmark იგივე input hashes-ით, მინიმუმ 20 repetition თითო cell-ში, დამოუკიდებელ physical x86-64 და ARM64 მოწყობილობებზე, RSS და memory bandwidth გაზომვით და confidence intervals-ით.

## წყაროები

- NOEMA GitHub Actions run 45850716742 — https://github.com/maisuradzee/bibmom/actions/runs/45850716742
- NOEMA GitHub Actions run 45867519546 — https://github.com/maisuradzee/bibmom/actions/runs/45867519546
- Python 3.14 threading documentation — https://docs.python.org/3.14/library/threading.html
- Python 3.14 free-threading HOWTO — https://docs.python.org/3.14/howto/free-threading-python.html
- Higham, N. J. (1993), The Accuracy of Floating Point Summation — https://doi.org/10.1137/0914050
- Ogita, T., Rump, S. M., Oishi, S. (2005), Accurate Sum and Dot Product — https://doi.org/10.1137/030601818

## შემოწმების სტატუსი

- ახალი run-ის ორივე ZIP ჩამოიტვირთა; archive SHA-256 დაემთხვა GitHub artifact metadata-ს.
- ახალი raw JSON reports SHA-256-ით შემოწმდა და ხელახლა აგრეგირდა.
- Reproduction script და mutation tests CI-ში სრულდება.
- შედეგი რჩება preliminary: მხოლოდ hosted x86-64 VM, synthetic cancellation fixtures, სამი repetition თითო configuration; დამოუკიდებელი physical-hardware replication და გარე რეცენზია არ ჩატარებულა.
- GitHub Actions artifact ZIP-ები 30 დღეში იშლება; raw report-ის compressed copy და hash-ები ამ PR-ში ინახება.

## შემდეგი ნაბიჯები

1. იგივე benchmark გაუშვი დამოუკიდებელ physical x86-64 და ARM64 მოწყობილობებზე.
2. გაზარდე measured repetitions მინიმუმ 20-მდე და გამოაქვეყნე uncertainty intervals.
3. დაამატე process RSS/native allocation და memory-bandwidth გაზომვები.
4. შეადარე pairwise, long-double და exact/superaccumulator ალგორითმები.
5. მოითხოვე დამოუკიდებელი numerical-method review; Published სტატუსი არ მიენიჭოს ამ ეტაპზე.


## მესამე hosted run — 2026-11-27 (GitHub Actions 45897707859)

### შედეგები

| Runtime | Method | Correct | Median speedup vs matching serial baseline | Median CPU/wall |
|---|---|---:|---:|---:|
| Free-threaded | Naive scalar | 0/48 | 0.4238× | 2.251 |
| Free-threaded | Scalar Neumaier | 42/48 | 1.3086× | 2.554 |
| Free-threaded | Neumaier state | 48/48 | 1.2589× | 2.418 |
| GIL-enabled | Naive scalar | 0/48 | 0.5096× | 1.010 |
| GIL-enabled | Scalar Neumaier | 42/48 | 0.7524× | 1.003 |
| GIL-enabled | Neumaier state | 48/48 | 0.7576× | 1.003 |

Free-threaded Neumaier-state median speedup by worker count was 0.7733× (1 worker), 1.2125× (2), 1.3546× (4) and 1.3090× (8). On a runner with four available CPUs, 8 workers were slower than 4 workers by this median. Native thread identity matched configured worker count in all 16 cases per runtime. CPU-time/wall-time exceeded 1.05 in 36/48 measured runs in free-threaded mode and 0/48 in GIL-enabled mode.

### Accuracy finding

Scalar Neumaier partials produced correctly rounded results in 42/48 configurations in both runtimes; the full Neumaier compensation-state merge produced 48/48. The six scalar failures occurred in the grouped-cancellation fixture at 2- and 8-worker settings across the two partition strategies. This supports preserving the full (sum, correction) state across partition boundaries for these test inputs.

### Performance caveat

The reported free-threaded 1.2589× median is versus the matching serial Neumaier baseline only. Serial math.fsum was substantially faster: the four-worker contiguous threaded Neumaier-state path took 14.8–16.3× the serial math.fsum wall time on the free-threaded fixtures. The benchmark therefore demonstrates CPU parallelism in the free-threaded Python runtime, not an overall speed advantage over a well-optimized serial algorithm.

### Provenance and reproduction

- Run: https://github.com/maisuradzee/bibmom/actions/runs/45897707859
- Exact tested head: b827c8cb4517311f7d441c336e1f44d6717f2cf5
- Frozen summary: data/noema-005/threaded-rerun-2026-11-27.json
- Reproduction script: scripts/reproduce_noema005_threaded_rerun_2026_11_27.py
- Raw report archive and report hashes are recorded in the summary and preserved in data/noema-005/raw/.

### Limitations

This is one hosted run per runtime, three repetitions per configuration and two synthetic inputs. The free-threaded and GIL-enabled jobs used different hosted VM families (Azure/AWS), so cross-runtime timing comparison is confounded. tracemalloc does not measure RSS/native allocation or DRAM bandwidth. No physical x86-64/ARM64 replication or independent numerical review has been completed.
