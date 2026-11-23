# მცურავი წერტილის ჯამის სიზუსტე: ალგორითმი, რიგითობა და გამეორებადობა

> **სტატუსი: წინასწარი კვლევა (preliminary).** ეს არის AI-ით მომზადებული და კოდით/ტესტებით ნაწილობრივ გამეორებული კვლევითი ანგარიში. დამოუკიდებელი გარე რეცენზია და სხვა არქიტექტურაზე გამეორება ჯერ არ დასრულებულა. შედეგები არ უნდა ჩაითვალოს უნივერსალურ სიჩქარის ან სიზუსტის გარანტიად.

## კვლევის კითხვა

შეიძლება თუ არა ერთი და იმავე რიცხვების მულტისეტმა შეკრების განსხვავებული რიგითობის ან ალგორითმის გამო განსხვავებული შედეგი მოგვცეს? და როგორ იცვლება ამ მეთოდების დროისა და მეხსიერების ფასი სხვადასხვა floating-point/decimal ფორმატში?

## მთავარი მიგნება

დიახ. სასრული სიზუსტის არითმეტიკაში შეკრება ყოველთვის ასოციაციური არ არის. დიდი და მცირე რიცხვების შერევისას დამრგვალებამ მცირე წვლილი შეიძლება დაკარგოს; შემდგომი გაუქმება (cancellation) დაკარგულ ინფორმაციას ვეღარ აღადგენს. ამ კონტროლირებულ ექსპერიმენტში ერთსა და იმავე შეყვანათა დალაგებამ შედეგი შეცვალა. Kahan-ის კომპენსაცია ზოგიერთ შემთხვევას აუმჯობესებდა, მაგრამ ყველა ტესტში საკმარისი არ აღმოჩნდა. Neumaier-ისა და ზუსტი integer accumulator-ის შედეგები ამ კონკრეტულ stress-test-ებში ეტალონს დაემთხვა.

ეს არის კონკრეტული შეყვანებისა და იმპლემენტაციების შედეგი — არა მტკიცება, რომ ერთი მეთოდი ყველა ამოცანაში საუკეთესოა.

## რა შემოწმდა

NOEMA-2026-005-ში შედარებულია binary32, binary64, decimal64 და decimal128 არითმეტიკა. შესწავლილია naive left-to-right, adjacent pairwise, Kahan, Neumaier, math.fsum-ის შედარებითი გზა და ზუსტი integer superaccumulator.

კონტროლირებულ სტრეს-ტესტებში ერთი და იგივე მულტისეტი სხვადასხვა რიგითობით ჯამდებოდა. შედეგები შედარდა ზუსტ რაციონალურ ეტალონს. ცალკე შესრულდა runtime/memory პროფილი 1,024, 8,192 და 65,536 ელემენტზე, ორი warmup-ით და შვიდი გაზომვით თითო შემთხვევაზე.

## შედეგები: სწორად დამრგვალებული ჯამი

- Binary64 cancellation ტესტში naive და adjacent pairwise მეთოდებმა შვიდი დალაგებიდან მხოლოდ ორში მიიღეს სწორად დამრგვალებული შედეგი.
- Kahan-მა იმავე ტესტში ოთხი დალაგება დაამთხვია; Neumaier-მა, math.fsum-მა და integer accumulator-მა — შვიდივე.
- Binary32 ტესტებში Neumaier და integer accumulator ორივე შემოწმებულ stress-case-ში ყველა დალაგებას დაემთხვა; Kahan-ის შედეგი კონკრეტულ ტესტზე იყო დამოკიდებული.
- Decimal64/128 ტესტები აჩვენებს, რომ შედეგზე მოქმედებს precision და შეყვანის რიგითობა; decimal128-ის ერთ კონკრეტულ cancellation მაგალითში მცირე წევრი შენარჩუნდა, მაგრამ ეს ფორმატის ზოგადი გარანტია არ არის.

## შედეგები: runtime და მეხსიერება

<small>ქვემოთ მოცემული მონაცემები არის 65,536 ელემენტის შეყვანის median runtime, ერთ CPython 3.14.4 / Linux x86-64 გარემოში. თითო მეთოდზე შესრულდა 7 გაზომვა. დრო მილიწამებშია.</small>

| ფორმატი | naive | pairwise | Kahan | Neumaier | სხვა გზა / ზუსტი accumulator |
|---|---:|---:|---:|---:|---|
| binary64 | 0.662 | 3.644 | 2.195 | 3.141 | math.fsum 1.104; integer 60.835 |
| binary32 | 81.808 | 88.222 | 324.736 | 320.630 | fsum→binary32 0.383; integer 14.024 |
| decimal64 | 6.362 | 11.759 | 25.327 | 30.652 | integer 37.376 |
| decimal128 | 6.365 | 11.737 | 25.232 | 31.416 | integer 37.210 |

Binary32-ის fsum→binary32 არის უფრო მაღალი სიზუსტით დაგროვებისა და საბოლოო binary32 cast-ის გზა; ის არ არის binary32-native არითმეტიკა. integer ნიშნავს ამ კვლევაში გამოყენებულ Python reference-implementation-ს და არა ოპტიმიზებულ hardware ან production superaccumulator-ს.

ამ ერთ runner-ზე binary64 integer accumulator-ის median იყო 60.835 ms, ხოლო naive მეთოდის — 0.662 ms. ეს დაახლოებით 91.9-ჯერ სხვაობაა ამ კონკრეტულ იმპლემენტაციაში. Decimal integer accumulator-ის tracemalloc peak იყო დაახლოებით 6.85 MB. ეს მეტრიკა ზომავს Python-managed allocation-ს და არა პროცესის სრულ RSS-ს.

## ინტერპრეტაცია და პრაქტიკული რეკომენდაცია

რიცხვითი სისტემის გამეორებადობისთვის საკმარისი არ არის მხოლოდ შეყვანის მონაცემების შენახვა. უნდა დაფიქსირდეს შეკრების მეთოდი, რიგითობა ან reduction tree, precision და rounding mode. რთული ჯამებისთვის სასურველია adversarial cancellation regression-test და ზუსტ ან მაღალი სიზუსტის ეტალონთან შედარება.

NOEMA-ს წინადადებაა მცირე **summation contract**: პროექტმა დოკუმენტურად განსაზღვროს დაგროვების ალგორითმი, input ordering/deterministic reduction tree, regression fixture, ეტალონთან შედარების წესი და დასაშვები შეცდომა. ეს ახალი შეკრების ალგორითმი არ არის; მისი რეალურ წარმოებით სისტემებში ეფექტიანობა ჯერ არ შემოწმებულა.

## შეზღუდვები

- სრული პროფილი შესრულდა ერთ CPython/Linux runner-ზე; სხვა ოპერაციულ სისტემასა და არქიტექტურაზე შედეგები შეიძლება განსხვავდებოდეს.
- tracemalloc არ ზომავს სრულ პროცესულ RSS-ს და არ ასახავს ყველა native allocation-ს.
- Binary32-ის native-სიმულაცია Python-ის დონეზე ამრგვალებს შუალედურ ოპერაციებს; მისი სიჩქარე hardware binary32 ოპერაციის სიჩქარეს არ წარმოადგენს.
- Decimal კვლევა იყენებს Python decimal.Context-ს მითითებული precision/exponent პარამეტრებით; ის არ ამოწმებს IEEE decimal interchange-ის BID/DPD byte-level კოდირებას.
- Integer accumulator არის reference-oriented Python implementation და არა ოპტიმიზებული production ალგორითმი.
- Synthetic stress-test-ები არ წარმოადგენს რეალური workload-ების შეცდომის სიხშირის შეფასებას.
- სხვა Python ვერსიაზე/არქიტექტურაზე დამოუკიდებელი benchmark გამეორება და გარე რეცენზია დარჩენილია.

## გამეორებადობა და წყარო მონაცემები

- სრული benchmark workflow: [GitHub Actions run #45283854718](https://github.com/maisuradzee/bibmom/actions/runs/45283854718).
- [Benchmark protocol](https://github.com/maisuradzee/bibmom/blob/research/noema-2026-005-mainline-2026-11-24/data/noema-005/benchmark-protocol.json)
- [Full profile summary JSON](https://github.com/maisuradzee/bibmom/blob/research/noema-2026-005-mainline-2026-11-24/data/noema-005/benchmark-full-profile-summary-2026-11-24.json)
- [Summation experiment result JSON](https://github.com/maisuradzee/bibmom/blob/research/noema-2026-005-mainline-2026-11-24/data/noema-005/floating-summation-results.json)
- [კვლევის სრული სამუშაო ჩანაწერი](https://github.com/maisuradzee/bibmom/blob/research/noema-2026-005-mainline-2026-11-24/research/drafts/NOEMA-2026-005-floating-summation-order.md)

## წყაროები

1. Higham, N. J. (1993), *The accuracy of floating point summation*, SIAM Journal on Scientific Computing. https://doi.org/10.1137/0914050
2. Ogita, T., Rump, S. M., & Oishi, S. (2005), *Accurate Sum and Dot Product*. https://doi.org/10.1137/030601818
3. Shewchuk, J. R. (1997), *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates*. https://doi.org/10.1007/PL00009321
4. IEEE 754-2019, *Standard for Floating-Point Arithmetic*. https://standards.ieee.org/ieee/754/6210/
5. Python 3.12 documentation, sum(): https://docs.python.org/3.12/library/functions.html#sum
6. Python 3.12 documentation, math.fsum(): https://docs.python.org/3.12/library/math.html#math.fsum
7. Python documentation, decimal: https://docs.python.org/3/library/decimal.html
8. NIST Digital Library of Mathematical Functions, §3.1: https://dlmf.nist.gov/3.1

## შემდეგი ნაბიჯები

1. სრული benchmark-ის გამეორება მინიმუმ სამ დამოუკიდებელ run-ზე და სხვა Python ვერსიასა/არქიტექტურაზე.
2. integer accumulator-ის ოპტიმიზაცია ისე, რომ ზუსტი reference უცვლელი დარჩეს.
3. deterministic და nondeterministic parallel reduction tree-ების შემოწმება.
4. რეალური სამეცნიერო მონაცემთა ნაკრების დამატება.
5. დამოუკიდებელი მკვლევრის მიერ მეთოდოლოგიის, ტესტებისა და წყაროების გადამოწმება.

---
**NOEMA სტატუსი:** preliminary · წინასწარი შედეგი · დამოუკიდებელი გარე რეცენზია არ დასრულებულა.
