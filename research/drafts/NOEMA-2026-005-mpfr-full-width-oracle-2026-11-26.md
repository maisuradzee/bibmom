# NOEMA-005 — MPFR full-width exact-rounding oracle extension

- **ID:** NOEMA-2026-005-ORACLE-03
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი გამოთვლები, IEEE-754 binary64, correctly-rounded conversion
- **ავტორი/მომზადების სისტემა:** NOEMA

## საკვლევი კითხვა

ემთხვევა თუ არა C-ის signed 2,560-bit exact-integer-unit-to-binary64 converter დამოუკიდებელ GNU MPFR 4.2.1 oracle-ს სრულ-width deterministic input-ებზე და ties-to-even midpoint-ის მეზობელ მნიშვნელობებზე?

## მოკლე შეჯამება

ეს კვლევა აფართოებს main-ში არსებულ MPFR cross-check-ს 467 სინთეზური input-იდან 2,068 ახალ, დეტერმინისტულ input-მდე. ახალი ნაკრები შედგება 1,024 seeded signed integer-ისგან, რომელთა bit length 1–2,559 დიაპაზონს ფარავს, და 1,044 tie-adjacent მნიშვნელობისგან. თითოეული input მოწმდება C/MPFR harness-ით და ორ Python reference-თან: integer guard/remainder/ties-to-even oracle და 1,200-digit Decimal rational conversion. ახალი შედეგი ჯერ pending-ია ზუსტი PR head-ის x86-64 და ARM64 workflow-ების დასრულებამდე.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

ხელით შერჩეული boundary cases აუცილებელია, მაგრამ ისინი ვერ ფარავს accumulator-ის ფართო მნიშვნელობათა სივრცეს. დეტერმინისტული seeded შემთხვევები ამცირებს შემთხვევითობისა და ხელახლა გამეორების გაურკვევლობას. MPFR დამატებით გვაძლევს დამოუკიდებელ numerical library oracle-ს, რომელიც არ არის იგივე Python integer ან Decimal implementation.

## არსებული ცოდნა და წყაროები

- **IEEE Std 754-2019**, IEEE Computer Society, 2019-07-22: https://standards.ieee.org/ieee/754/6210/ — binary floating-point ფორმატებისა და rounding-ის ნორმატიული საფუძველი.
- **GNU MPFR Manual**, GNU MPFR project, undated: https://mpfr.loria.fr/mpfr-current/mpfr.html — MPFR-ის ზუსტი მნიშვნელობებისა და rounding mode-ების დოკუმენტაცია.
- **NOEMA main exact-rounding implementation:** https://github.com/maisuradzee/bibmom/blob/main/scripts/noema005_native_accumulator_benchmark.c — signed fixed-width accumulator და binary64 converter.
- **Existing MPFR test harness:** https://github.com/maisuradzee/bibmom/blob/main/tests/noema005_mpfr_rounding_harness.c — exact integer to MPFR reference conversion and bitwise comparison.

## მტკიცებულებები

- **FACT:** MPFR harness input-ს signed 2,560-bit range-ში ამოწმებს, exact integer-ს MPFR-ში 2,624-bit precision-ით გარდაქმნის, ზუსტად ყოფს 2^1074-ზე და საბოლოო binary64-ს MPFR_RNDN-ით იღებს.
- **FACT:** main workflow ამოწმებს, რომ hosted Ubuntu x86-64 და ARM64 runner-ებზე pkg-config --modversion mpfr აბრუნებს 4.2.1-ს.
- **HYPOTHESIS:** სრული-width random და tie-adjacent input-ების გაფართოება გამოავლენს ისეთ rounding defect-ს, რომელიც არსებული 467 შემთხვევით არ გამოვლენილა.
- **UNTESTED IDEA:** იგივე oracle suite-ის მოგვიანებით გაშვება დამოუკიდებლად შერჩეულ ფიზიკურ x86-64 და ARM64 მოწყობილობებზე, runner virtualization-ისგან დამოუკიდებლად.

## კონკურენტი ახსნები

- Converter შეიძლება უკვე სწორად ფარავდეს ამ დიაპაზონს და ახალი შემთხვევები დამატებით დეფექტს ვერ გამოავლენდეს.
- Hosted CI-ში architecture label მიუთითებს runner-ის არქიტექტურაზე, მაგრამ არ ადასტურებს დამოუკიდებელ ფიზიკურ აპარატურას.
- Oracle agreement ამოწმებს კონკრეტულ input space-ს; ის არ არის ფორმალური მტკიცება ყველა შესაძლო accumulator state-ისთვის.

## ჰიპოთეზა

თუ converter სწორად ახორციელებს guard/sticky/ties-to-even rounding-ს ყველა მხარდაჭერილ signed accumulator value-ზე, მაშინ C output bits დაემთხვევა MPFR 4.2.1-ს, Python integer oracle-სა და Decimal reference-ს ყველა 2,068 input-ზე.

## მეთოდი ან ექსპერიმენტის გეგმა

1. ფიქსირებული seed-ით გენერირდება 1,024 signed magnitude; bit length თითო შემთხვევაზე აირჩევა 1–2,559 დიაპაზონიდან.
2. სხვადასხვა exponent-ისთვის იქმნება retained significand-ის even/odd ვარიანტები და midpoint−1, midpoint, midpoint+1 მნიშვნელობები ორივე ნიშნისთვის.
3. tie-adjacent ნაწილი მოიცავს 87 exponent position × 2 significand parity × 3 midpoint offsets × 2 signs = 1,044 input-ს.
4. სრული ნაკრები მოწმდება სამი oracle გზით: C converter vs MPFR 4.2.1; Python integer ties-to-even reference; Python Decimal rational conversion.
5. x86-64 და ARM64 hosted jobs ასრულებს ერთსა და იმავე deterministic suite-ს; workflow-ში MPFR version assertion ფიქსირებს oracle dependency-ს.

## შედეგები და ინტერპრეტაცია

**მიმდინარე მდგომარეობა: pending.** ტესტის კოდი და deterministic input generator დაემატა ცალკე research branch-ზე. ახალი accuracy შედეგი არ ჩაითვლება დადასტურებულად, სანამ ზუსტი branch head-ის quality CI და ორივე native architecture job არ დასრულდება წარმატებით. CI-ის წარმატება იქნება REPRODUCED RESULT მხოლოდ ამ განსაზღვრული test suite-ის ფარგლებში.

## შეზღუდვები და გაურკვევლობები

- 2,068 input არის deterministic synthetic sample და არა ყველა 2,560-bit signed integer-ის ამომწურავი შემოწმება.
- MPFR 4.2.1 hosted Ubuntu runner-ებზე გამოიყენება; ფიზიკური მოწყობილობების დამოუკიდებელი გამეორება არ ჩატარებულა.
- ეს ტესტი ამოწმებს exact integer-ის binary64 rounding-ს და არა ყველა შესაძლო upstream summation workload-ს.
- ეს არ არის ფორმალური verification, arbitrary precision accumulator-ის გარანტია ან performance benchmark.
- Representative scientific workloads, memory-bandwidth measurements და independent numerical-method review კვლავ საჭიროა.

## დასკვნა

ეს გაფართოება ზრდის exact-rounding regression coverage-ს და ამოწმებს converter-ს დამოუკიდებელი MPFR oracle-ით. წარმატებული CI არ ცვლის კვლევის სტატუსს: NOEMA-005 რჩება preliminary, სანამ დამოუკიდებელი numerical review და წარმომადგენლობითი workload-ები არ შეფასდება.

## წყაროები

- IEEE Computer Society, IEEE Std 754-2019: https://standards.ieee.org/ieee/754/6210/
- GNU MPFR project, MPFR Manual: https://mpfr.loria.fr/mpfr-current/mpfr.html
- NOEMA exact-rounding C implementation: https://github.com/maisuradzee/bibmom/blob/main/scripts/noema005_native_accumulator_benchmark.c
- NOEMA MPFR harness: https://github.com/maisuradzee/bibmom/blob/main/tests/noema005_mpfr_rounding_harness.c

## შემდეგი ნაბიჯები

- ზუსტი PR head-ის quality CI და x86-64/ARM64 MPFR jobs-ის დასრულება.
- წარმატების შემთხვევაში, შედეგების რაოდენობისა და run IDs-ის დაფიქსირება.
- დამოუკიდებელი numerical-method review და რეალურ სამეცნიერო workload-ებზე memory/runtime benchmark.

## შემოწმების სტატუსი

- **Draft:** ტესტის კოდი და მეთოდი შექმნილია.
- **CI:** pending.
- **Publication:** არ არის preliminary ან published; არ იცვლება საჯარო კატალოგი.

## ცვლილებების ისტორია

- 2026-11-26 — დაემატა 2,068-case full-width/tie-adjacent MPFR oracle suite; exact-head CI-ის დასრულებამდე შედეგი pending რჩება.
