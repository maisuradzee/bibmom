# NOEMA-2026-005 — ARM64 Run 33: frozen artifact verification

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft
- **თარიღი:** 2026-11-28
- **მტკიცებულების სტატუსი:** FACT / FROZEN_ARTIFACT_REPRODUCED_RESULT / INFERENCE / HYPOTHESIS / UNTESTED IDEA

## საკვლევი კითხვა

შეესაბამება თუ არა 2026-11-27 ARM64 threaded benchmark-ის ოთხი გამოქვეყნებული ZIP არქივი მათ manifest-ში მითითებულ SHA-256-ს, და ემთხვევა თუ არა raw report-ებიდან დამოუკიდებლად დათვლილი accuracy/CPU-parallelism/median-speedup აგრეგატები გაყინულ summary-ს?

## ადამიანური სარგებელი

რიცხვითი სიზუსტის კვლევის შედეგების გამეორებადობა და მტკიცებულების მთლიანობის დაცვა. არასწორად დათვლილი ან შეცვლილი benchmark არქივი შეიძლება შეცდომაში შეიყვანოს ინჟინრები, რომლებიც კრიტიკული გამოთვლითი სისტემების ალგორითმს ირჩევენ.

## წყაროები

1. [Frozen ARM64 benchmark summary](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/arm64-threaded-benchmark-summary-2026-11-27.json)
2. [Original benchmark workflow run 46032894362](https://github.com/maisuradzee/bibmom/actions/runs/46032894362)
3. [Offline verifier implementation](https://github.com/maisuradzee/bibmom/blob/main/scripts/verify_noema005_arm64_artifacts.py) — ამ PR-ში დამატებული პროტოტიპი.

## მეთოდი ან ექსპერიმენტის გეგმა

- ოთხი ZIP artifact ჩამოიტვირთა GitHub Actions artifact ID-ებით.
- თითოეული ZIP-ის SHA-256 ხელახლა გამოითვალა და შედარდა summary manifest-ს.
- თითოეული ZIP-იდან ერთი raw JSON report ამოიღო; raw report-ის SHA-256 და byte length ხელახლა გამოითვალა.
- raw report-ებიდან ხელახლა დაითვალა სწორად დამრგვალებული გაშვებები, CPU-time/wall-time >1.05 ნიმუშები, თითო runner/method median speedup და input hash-ების თანხვედრა.
- benchmark თავიდან არ გაშვებულა; ეს არის frozen artifact verification და არა დამოუკიდებელი ფიზიკური ექსპერიმენტი.

## შედეგები

- **4/4 ZIP SHA-256** დაემთხვა manifest-ს.
- **4/4 raw JSON SHA-256** დაემთხვა manifest-ს; byte length-ებიც დაემთხვა.
- **192 კონფიგურაცია / 576 გაზომილი გაშვება** (3 გამეორება თითო კონფიგურაციაზე).
- Naive scalar: **0/192** სწორად დამრგვალებული გაშვება.
- Scalar Neumaier: **168/192**.
- Neumaier-state: **192/192**.
- CPU-time/wall-time >1.05: GIL-enabled **4/288**, free-threaded **202/288**.
- ყველა ოთხ runner/runtime cell-ში და სამივე მეთოდში median wall-time speedup **1.0-ზე ნაკლებია**.
- ორი deterministic input layout-ის hash-ები ოთხივე არქივში ერთმანეთს ემთხვევა.

## მტკიცებულების ეტიკეტები

- **FACT:** workflow 46032894362 წარმატებით დასრულდა და ოთხი hosted ARM64 runner/runtime cell-ის არქივი გამოქვეყნდა.
- **FROZEN_ARTIFACT_REPRODUCED_RESULT:** ოთხივე ZIP და raw JSON digest დამოუკიდებლად გადაითვალა; aggregate counts და median speedup-ები raw report-ებიდან ხელახლა დაითვალა და summary-ს დაემთხვა.
- **INFERENCE:** ამ synthetic cancellation workload-ზე Neumaier-state ინარჩუნებს exact-reference accuracy-ს, მაგრამ არც ერთ hosted ARM64 cell-ში wall-time აჩქარება არ გამოვლენილა.
- **INFERENCE:** free-threaded პროცესებში CPU-time/wall-time >1.05 ნიმუშები მიუთითებს ერთზე მეტი CPU-ის აგრეგირებულ გამოყენებაზე; ეს არ ნიშნავს სასარგებლო throughput-ის ზრდას.
- **HYPOTHESIS:** native/vectorized ან ნაკლებ Python-level work-ის მქონე reduction არქიტექტურამ შეიძლება გააუმჯობესოს throughput; ჯერ არ შემოწმებულა.
- **UNTESTED IDEA:** Pairwise tree და reproducible exact/superaccumulator შევადაროთ Neumaier-state-ს cancellation-heavy და რეალისტურ memory-bandwidth-bound workload-ებზე.

## შეზღუდვები

- ეს არის გაყინული არქივების დამოუკიდებელი გადამოწმება და არა ახალი benchmark.
- GitHub-hosted ARM64 runners არ უდრის დამოუკიდებელ ფიზიკურ მოწყობილობებს ან გარე ლაბორატორიულ გამეორებას.
- თითო კონფიგურაციაზე მხოლოდ სამი გაზომილი გამეორებაა.
- მონაცემები სინთეზური cancellation fixture-ებია და არა წარმომადგენლობითი აპლიკაციის ან memory-bandwidth workload.
- მეხსიერება იზომება მხოლოდ tracemalloc peak delta-ით; RSS, native allocator overhead და DRAM bandwidth არ გაზომილა.
- runner-ებისა და OS image-ების შედარება მიზეზშედეგობრივად არ შეიძლება.
- raw reports და native thread ID-ები საჯარო საცავში არ ჩაწერილა.

## შემდეგი ნაბიჯები

1. Offline verifier გავუშვათ ჩამოტვირთულ ოთხ არქივზე და შევინახოთ მხოლოდ hash/aggregate report.
2. Pairwise tree და exact/superaccumulator ალგორითმები დავამატოთ ცალკე ექსპერიმენტულ branch-ზე.
3. რეალურ x86-64 და ARM64 მოწყობილობებზე 20+ გამეორება, RSS და DRAM bandwidth გავზომოთ.
4. წარმომადგენლობითი memory-bandwidth workload დავამატოთ cancellation fixture-ის გვერდით.
5. დამოუკიდებელი numerical-method review მივიღოთ.

## შემოწმების სტატუსი

Draft; frozen artifact integrity და aggregate reprocessing შესრულებულია 2026-11-28. ახალი benchmark არ ჩატარებულა. კვლევა არ არის Published.

## დასკვნა

ფაილების მთლიანობა და summary-ის ძირითადი აგრეგატები დამოუკიდებლად განმეორდა. შედეგი ამყარებს რიცხვითი სიზუსტის დასკვნას Neumaier-state-ისთვის, მაგრამ არ ადასტურებს ARM64-ზე threading-ის wall-time სარგებელს. შემდეგი ექსპერიმენტი უნდა ფოკუსირდეს ალგორითმის არქიტექტურასა და მეხსიერების შეზღუდვებზე.

## ცვლილებების ისტორია

- 2026-11-28 — ოთხი hosted ARM64 artifact-ის ZIP/raw SHA-256 და აგრეგატების დამოუკიდებელი გადამოწმება.
