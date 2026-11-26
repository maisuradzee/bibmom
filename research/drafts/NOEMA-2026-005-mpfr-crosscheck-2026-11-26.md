# NOEMA-2026-005 — დამოუკიდებელი MPFR cross-check binary64 rounding-ისთვის

- **ID:** NOEMA-2026-005-MPFR-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** numerical analysis, reproducible computing, IEEE-754 binary64
- **მტკიცებულების სტატუსი:** REPRODUCED RESULT (hosted CI; შეზღუდვებით)

## საკვლევი კითხვა

ემთხვევა თუ არა NOEMA-005-ის bounded C exact-integer-to-binary64 converter-ის შედეგი დამოუკიდებელი MPFR numerical library-ის correctly-rounded reference-ს signed 2,560-bit accumulator-ის მთელ დასაშვებ დიაპაზონში შერჩეულ boundary და deterministic random შემთხვევებზე?

## მეთოდი

C converter წარმოადგენს signed integer-ს, რომლის ერთეულია (2^{-1074}). MPFR reference-ისთვის:

1. GMP mpz_t-ში ზუსტად იკითხება signed decimal integer და მოწმდება დიაპაზონი ([-2^{2559}, 2^{2559}-1]).
2. MPFR მნიშვნელობა ინიციალიზდება 2,624-bit precision-ით. ეს აღემატება მაქსიმალურ 2,560-bit input-ს, ამიტომ integer-ის ჩაწერა ზუსტია.
3. მნიშვნელობა იყოფა (2^{1074})-ზე; ეს არის ზუსტი binary exponent shift.
4. mpfr_get_d(..., MPFR_RNDN) აბრუნებს binary64 მნიშვნელობას round-to-nearest, ties-to-even წესით.
5. C converter-ისა და MPFR-ის 64-bit output bit pattern-ები შედარდება. Python-ის 1,200-digit Decimal reference დამატებით ამოწმებს იმავე შედეგებს.

MPFR-ის ოფიციალური დოკუმენტაცია განსაზღვრავს MPFR_RNDN-ს როგორც round-to-nearest, ties-to-even და აღწერს MPFR-ის correctly-rounded ოპერაციებს. GMP-ის ოფიციალური დოკუმენტაცია განსაზღვრავს mpz_export-ის word order-სა და host-endian პარამეტრებს.

## შედეგები

- არსებული deterministic boundary suite: 275 signed input.
- დამატებითი შემთხვევები: 12 bit-length bucket × 8 deterministic random magnitude × 2 signs = 192 signed input.
- ჯამი: **467 valid signed inputs თითოეულ არქიტექტურაზე**.
- Hosted Linux x86-64: MPFR, C converter და Python Decimal bit-for-bit თანხვედრა — 467/467.
- Hosted Linux ARM64: MPFR, C converter და Python Decimal bit-for-bit თანხვედრა — 467/467.
- ორი signed-range უარყოფითი ტესტი: +2^2559 და -2^2559-1 უარყოფილია; დასაშვები endpoint-ები კვლავ შედის boundary suite-ში.
- PR #48-ის native accumulator workflow-ის ორივე არქიტექტურის job-მა წარმატებით გაიარა MPFR და integer/Decimal oracle ნაბიჯები; repository quality CI-ც წარმატებულია. შემდგომი research-record/portfolio commit-ისთვის exact-head CI ხელახლა უნდა შესრულდეს.

## ინტერპრეტაცია

**REPRODUCED RESULT:** შემოწმებულ 467 შემთხვევაზე bounded C converter ემთხვევა MPFR-ის correctly-rounded binary64 reference-ს ორივე hosted CI არქიტექტურაზე.

**FACT:** MPFR MPFR_RNDN იყენებს IEEE-754 roundTiesToEven წესს; GMP mpz_export მხარს უჭერს explicit least-significant-word-first და native-endian კონვერტაციას.

**INFERENCE:** ეს cross-check მნიშვნელოვნად აძლიერებს converter-ის ტესტურ მტკიცებულებას, რადგან reference აღარ შემოიფარგლება მხოლოდ იმავე Python runtime-ის integer/Decimal იმპლემენტაციებით.

## შეზღუდვები

- Hosted x86-64 და ARM64 CI არ არის დამოუკიდებელი ფიზიკური მოწყობილობების replication.
- ტესტები synthetic integer-unit შემთხვევებია და არა რეალური სამეცნიერო workload-ები.
- ეს არ არის ფორმალური მტკიცება ან დამოუკიდებელი გარე numerical-method review.
- MPFR cross-check ეხება converter-ს და signed parser-ს; exact accumulator-ის add/merge ოპერაციები კვლავ fixed-width modular arithmetic-ს იყენებს. ამ helper-ების overflow guard ჯერ არ არის დამატებული.
- არ გაკეთებულა performance ან memory-bandwidth დასკვნა.

## წყაროები

1. GNU MPFR 4.2.2 Manual, rounding modes and correctly rounded operations: https://mpfr.loria.fr/mpfr-current/mpfr.html (წვდომა: 2026-11-26).
2. GNU MP 6.3.0 Manual, Integer Import and Export: https://gmplib.org/manual/Integer-Import-and-Export (წვდომა: 2026-11-26).
3. IEEE Std 754-2019, IEEE Standard for Floating-Point Arithmetic: https://standards.ieee.org/ieee/754/6210/ (წვდომა: 2026-11-26).

## შემდეგი ნაბიჯები

1. exact accumulator-ის add/merge ოპერაციებს დაემატოს checked-overflow კონტრაქტი და შესაბამისი უარყოფითი ტესტები.
2. pairwise, Neumaier და exact მეთოდები შეფასდეს წარმომადგენლობით memory-bandwidth-bound workload-ებზე.
3. ექსპერიმენტი განმეორდეს დამოუკიდებლად შერჩეულ ფიზიკურ x86-64 და ARM64 მოწყობილობებზე, წინასწარ განსაზღვრული warm-up/repetition პროტოკოლით და uncertainty interval-ებით.
4. შედეგები წარედგინოს დამოუკიდებელ numerical-method review-ს.

## შემოწმების სტატუსი

- Code-only head 1ab5917d961d829a52a850884fac7d829c7fddf4: [quality CI 45819091367](https://github.com/maisuradzee/bibmom/actions/runs/45819091367) SUCCESS; [native x86-64/ARM64 workflow 45819091300](https://github.com/maisuradzee/bibmom/actions/runs/45819091300) SUCCESS.
- ორივე native architecture job-მა MPFR cross-check და Python integer/Decimal oracle tests წარმატებით შეასრულა.
- ამ კვლევითი ჩანაწერისა და პორტფელის დამატების შემდეგ შეიცვალა PR head; საბოლოო exact-head CI-ის შედეგი ცალკე უნდა დადასტურდეს.

## ცვლილებების ისტორია

- 2026-11-26: დაემატა MPFR 4.2.2 cross-check harness, Python test, x86-64/ARM64 CI ნაბიჯი და signed 2,560-bit input range regression.
