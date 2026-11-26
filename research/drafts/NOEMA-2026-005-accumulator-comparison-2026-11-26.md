# NOEMA-2026-005 — accumulator comparison addendum

- **ID:** NOEMA-2026-005-ACCUM-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი ანალიზი, binary64 reduction, პარალელური გამოთვლების ალგორითმები
- **ავტორი/მომზადების სისტემა:** NOEMA research automation; local CPython 3.13.5 / Linux x86_64 run

## საკვლევი კითხვა

როგორ განსხვავდება მკაცრი left-to-right binary64 ციკლი, ერთი ფიქსირებული adjacent-pair reduction tree, Neumaier compensation, Python `math.fsum` და მაღალი სიზუსტის Decimal baseline იმავე binary64 input-ების ზუსტად დათვლილ ჯამთან შედარებით?

## მოკლე შეჯამება

ხუთი დეტერმინისტული სინთეზური fixture-ით (სულ 15,359 მნიშვნელობა) Neumaier, `math.fsum` და 1,200-ნიშნა Decimal baseline ზუსტად დაემთხვა Fraction-ზე დაფუძნებულ reference-ს 5/5 შემთხვევაში. მკაცრი naive loop და ერთი კონკრეტული pairwise tree დაემთხვა 1/5 შემთხვევაში. ეს არის ალგორითმის სიზუსტის მცირე ტესტი და არა threaded runtime benchmark.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

NOEMA-005-ის წინა OpenMP შედეგებმა აჩვენა, რომ thread-local compensated state შეიძლება cancellation-heavy სინთეზურ fixture-ებში ზუსტ reference-ს ემთხვეოდეს. შემდეგი ნაბიჯია იმის დადგენა, რამდენად მდგრადია ეს შედეგი სხვა reduction სტრუქტურებთან და სხვა input განაწილებებთან. Reduction tree-ის შეცვლა მარტო არ იძლევა უნივერსალურ სიზუსტის გარანტიას.

## არსებული ცოდნა და წყაროები

- Python documentation, `math.fsum`: https://docs.python.org/3/library/math.html#math.fsum — ზუსტი floating-point summation-ის სტანდარტული ბიბლიოთეკის comparator; ამ ექსპერიმენტში oracle არ არის.
- Python documentation, `Fraction.from_float`: https://docs.python.org/3/library/fractions.html#fractions.Fraction.from_float — binary64 მნიშვნელობის ზუსტი რაციონალური წარმოდგენა, რომელიც გამოიყენება reference-ის ასაგებად.
- Python documentation, `decimal`: https://docs.python.org/3/library/decimal.html — მაღალი სიზუსტის decimal comparator-ის განხორციელება.

## მტკიცებულებები

### REPRODUCED RESULT

- `triplet_order`, `grouped_cancellation`, `multi_exponent_residuals`, `subnormal_residual` და `seeded_binary64_mixture` fixtures-ის input hashes და შედეგები გაყინულია `data/noema-005/accumulator-comparison-2026-11-26.json)-ში.
- Neumaier, `math.fsum` და Decimal 1,200-ნიშნა baseline ზუსტად დაემთხვა reference-ს 5/5 fixture-ზე.
- Strict left-to-right loop და ერთი adjacent-pair tree ზუსტად დაემთხვა 1/5 fixture-ზე; ორივემ ვერ გაიარა სამი cancellation/residual fixture და seeded mixed-exponent fixture.
- Seeded mixed-exponent fixture-ზე naive loop 3 ULP-ით, ხოლო pairwise tree 1 ULP-ით განსხვავდებოდა exact rounded reference-ისგან.

## კონკურენტი ახსნები

- Pairwise tree-ის შედეგი დამოკიდებულია კონკრეტულ partition/order-ზე; ეს ერთი adjacent-pair tree არ წარმოადგენს ყველა შესაძლო tree-ს.
- ხუთი fixture არ ფარავს ყველა შესაძლო finite input distribution-ს.
- Decimal comparator-ის სიზუსტე არ უნდა აირიოს C `long double`-ში ან native binned accumulator-ში.

## ჰიპოთეზა

კომპენსირებული ან ბინირებული accumulator შეიძლება იყოს უფრო მდგრადი cancellation-heavy workload-ებისთვის, ვიდრე naive reduction ან ერთი ფიქსირებული pairwise tree. ეს ჰიპოთეზა საჭიროებს native C/OpenMP და დამოუკიდებელ hardware ტესტს.

## შემოწმების მეთოდი

- ყველა input გენერირდება მეხსიერებაში დეტერმინისტული წესებით; seeded binary64 mixture იყენებს ფიქსირებულ PRNG seed-ს.
- Reference არის `sum(Fraction.from_float(x))`, რომელიც ზუსტად აგროვებს წარმოდგენილ binary64 მნიშვნელობებს და ბოლოს ერთხელ მრგვალდება binary64-ზე.
- შედარებულია strict left-to-right loop, adjacent-pair tree, Neumaier, `math.fsum` და 1,200-ნიშნა Decimal.
- თითოეული fixture-ისთვის ინახება SHA-256 input hash, hexadecimal result, exact-match flag და ULP distance.
- გაშვება: `python scripts/compare_noema005_accumulators.py --output data/noema-005/accumulator-comparison-2026-11-26.json`.

## შედეგები და ინტერპრეტაცია

| მეთოდი | ზუსტი დამთხვევა |
|---|---:|
| Strict left-to-right binary64 | 1 / 5 |
| Adjacent-pair tree | 1 / 5 |
| Neumaier compensated | 5 / 5 |
| `math.fsum` | 5 / 5 |
| Decimal, 1,200 digits | 5 / 5 |

შედეგი აჩვენებს, რომ ამ fixture-ებზე მხოლოდ tree reduction-ის გამოყენება საკმარისი არ აღმოჩნდა. ეს არ ნიშნავს, რომ ყველა pairwise tree არაზუსტია, ან რომ Neumaier ყველა input-ზე სწორად დამრგვალებულ შედეგს უზრუნველყოფს.

## შეზღუდვები და გაურკვევლობები

- ყველა input სინთეზურია; რეალური workload-ის განაწილება არ გამოგვიკვლევია.
- pairwise შედარება მოიცავს მხოლოდ ერთ deterministic adjacent-pair tree-ს.
- Decimal baseline არის arbitrary-precision decimal და არა C `long double`.
- არ გაზომილა runtime, memory, memory bandwidth, energy, threads ან OpenMP scaling.
- შესრულებულია მხოლოდ ერთ ადგილობრივ x86_64 გარემოში; დამოუკიდებელი hardware replication და გარე numerical-method review არ ჩატარებულა.

## დასკვნა

ეს შედეგი ამართლებს შემდეგ ეტაპზე native C/OpenMP ალტერნატივების შედარებას, მაგრამ ჯერ არ იძლევა წარმოებაში კონკრეტული accumulator-ის არჩევის საფუძველს. არსებული OpenMP benchmark უნდა გაფართოვდეს long-double, ალტერნატიული pairwise partitioning და binned/exact accumulator-ით, იგივე გაყინულ fixture-ებზე.

## წყაროები

1. Python Software Foundation, *math — Mathematical functions*, `math.fsum`, https://docs.python.org/3/library/math.html#math.fsum (წვდომა: 2026-11-26).
2. Python Software Foundation, *fractions — Rational numbers*, `Fraction.from_float`, https://docs.python.org/3/library/fractions.html#fractions.Fraction.from_float (წვდომა: 2026-11-26).
3. Python Software Foundation, *decimal — Decimal fixed-point and floating-point arithmetic*, https://docs.python.org/3/library/decimal.html (წვდომა: 2026-11-26).

## შემდეგი ნაბიჯები

1. native C/OpenMP benchmark-ში დაამატე C `long double`, alternative pairwise partitions და binned/exact accumulator.
2. ყველა მეთოდი შეადარე იმავე fixture hashes-სა და exact reference-ს.
3. გაზომე runtime, memory traffic და thread scaling ცალკე correctness შედეგებისგან.
4. გაიმეორე დამოუკიდებელ x86_64 და ARM64 hardware-ზე.
5. მოითხოვე დამოუკიდებელი numerical-method review.

## შემოწმების სტატუსი

- Local unit tests: 5/5 passed (CPython 3.13.5, Linux x86_64).
- Frozen-result reproduction: passed locally; script SHA-256 recorded in JSON.
- GitHub CI: first run failed only the draft-completeness validator because this document lacked required template metadata/sections; this revision adds the missing fields. CI rerun is pending.
- Research status: draft; not Published.

## ცვლილებების ისტორია

- 2026-11-26 — დაემატა deterministic accumulator comparison, frozen input/result hashes და five-test reproduction suite.
- 2026-11-26 — CI draft validator-ის მოთხოვნების შესაბამისად დაემატა metadata, წყაროები, მეთოდი, შემდეგი ნაბიჯები და შემოწმების სტატუსი.
