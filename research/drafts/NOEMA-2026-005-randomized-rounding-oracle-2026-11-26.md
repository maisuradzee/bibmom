# NOEMA-005 — deterministic full-width exact-rounding oracle extension

- **ID:** NOEMA-2026-005-ORACLE-02
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი გამოთვლები, IEEE-754 binary64, გამეორებადი ტესტირება
- **ავტორი/მომზადების სისტემა:** NOEMA

## საკვლევი კითხვა

ემთხვევა თუ არა C exact-integer-unit-to-binary64 converter-ის შედეგი ორ დამოუკიდებლად დაწერილ Python reference-ს ხელმოწერილი 2,560-ბიტიანი accumulator-ის უფრო ფართო, დეტერმინისტულ ნიმუშზე, განსაკუთრებით ties-to-even საზღვრებთან?

## მოკლე შეჯამება

ეს დამატება აფართოებს უკვე არსებულ 275-შემთხვევიან boundary/oracle ტესტს. გეგმა ამატებს 1,024 seeded random signed integer-ს სრული მხარდაჭერილი bit-width დიაპაზონიდან და midpoint-ის მეზობელ შემთხვევებს სხვადასხვა exponent-ზე. საბოლოო მტკიცებულების სტატუსი დამოკიდებულია exact-head x86-64 და ARM64 CI-ის დასრულებაზე.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

ზღვრული მაგალითები აუცილებელია, მაგრამ შეზღუდული რაოდენობის ხელით შერჩეული მნიშვნელობები ვერ ფარავს 2,560-ბიტიანი signed input-ის ფართო სივრცეს. დეტერმინისტული random და tie-adjacent ტესტები ზრდის შეცდომის აღმოჩენის შანსს ისე, რომ ყველა შეყვანა ხელახლა მიიღება ფიქსირებული seed-ით.

## არსებული ცოდნა და წყაროები

- NOEMA-005-ის არსებული converter და 275-input oracle ტესტი: [PR #42](https://github.com/maisuradzee/bibmom/pull/42) და [exact-rounding test source](https://github.com/maisuradzee/bibmom/blob/main/tests/test_noema005_exact_rounding.py).
- არსებული exact-head x86-64/ARM64 validation: [workflow run 45809003616](https://github.com/maisuradzee/bibmom/actions/runs/45809003616). ეს hosted CI შედეგია და არა დამოუკიდებელი ფიზიკური აპარატურის გამეორება.
- IEEE binary floating-point-ის ნორმატიული საფუძველი: [IEEE Std 754-2019](https://doi.org/10.1109/IEEESTD.2019.8766229).

## მტკიცებულებები

- **FACT:** binary64 converter-ის მიმდინარე იმპლემენტაცია იყენებს guard/sticky bits-ს და round-to-nearest, ties-to-even წესს; იგი შეზღუდულია 2,560-ბიტიანი accumulator-ის დიაპაზონით.
- **REPRODUCED RESULT:** PR #42-ის წინარე CI-ში 275 შეყვანა დაემთხვა integer და Decimal reference-ებს ორივე hosted architecture-ზე.
- **HYPOTHESIS:** სრული width-ის დეტერმინისტული random და midpoint-adjacent ტესტები გამოავლენს ისეთ rounding edge case-ს, რომელიც არსებული 275-შემთხვევიანი ნაკრებით არ იფარება.
- ახალი ტესტის შედეგი ამ დოკუმენტის საწყის ვერსიაში ჯერ **UNTESTED IDEA**-ა, სანამ ზუსტი PR head-ის ორივე architecture job არ დასრულდება.

## კონკურენტი ახსნები

- converter შეიძლება უკვე სწორად ფარავდეს მთელ ამ დიაპაზონს და გაფართოებულმა ნაკრებმა ახალი შეცდომა ვერ გამოავლინოს;
- ორი Python reference ერთმანეთისგან განსხვავებული ალგორითმით არის დაწერილი, მაგრამ ორივე CPython-ში სრულდება და არც ერთი არ არის MPFR/SoftFloat;
- hosted runner-ის architecture label არ უდრის დამოუკიდებელ ფიზიკურ მოწყობილობაზე კონტროლირებულ გამეორებას.

## ჰიპოთეზა

თუ converter სწორად ახორციელებს guard/sticky/ties-to-even ლოგიკას signed 2,560-bit accumulator-ის ფარგლებში, მაშინ C-ის output bits ზუსტად დაემთხვევა integer reference-სა და 1,200-digit Decimal rational conversion-ს ყველა გაყინულ და დეტერმინისტულად გენერირებულ შეყვანაზე.

## მეთოდი ან ექსპერიმენტის გეგმა

1. გამოიყენე ფიქსირებული PRNG seed და შექმენი 1,024 signed magnitude, რომელთა bit length თანაბრად აირჩევა 1-დან 2,559-მდე.
2. სხვადასხვა exponent-ისთვის შექმენი retained significand-ის even და odd ვარიანტები და შეამოწმე midpoint - 1, midpoint და midpoint + 1, დადებითი და უარყოფითი ნიშნებით.
3. ყველა integer გადაამოწმე ორ reference-თან: Python integer guard/remainder/ties-to-even ალგორითმთან და 1,200-digit Decimal rational conversion-თან.
4. იგივე decimal input-ები მიაწოდე C harness-ს და შეადარე binary64 output bit-for-bit.
5. გაუშვი NOEMA quality CI და native accumulator workflow x86-64 და ARM64 hosted runners-ზე.

## შედეგები და ინტერპრეტაცია

პირველმა exact-head CI ციკლმა გამოავლინა ორი დამოუკიდებელი პრობლემა:
- draft ფაილი არ აკმაყოფილებდა საცავის სარედაქციო validator-ის metadata/section კონტრაქტს;
- C harness-ისთვის გენერირებული input იყენებდა literal backslash+n-ს newline-ის ნაცვლად, რის გამოც parser აბრუნებდა exit code 2-ს.

ორივე ხარვეზი გასწორებულია ამ PR-ის შემდეგ commit-ში. ეს არის **REPRODUCED RESULT** მხოლოდ CI failure-ის მიზეზის შესახებ; ახალი converter accuracy შედეგი კვლავ pending-ია, სანამ ხელახალი exact-head workflow დასრულდება.

## შეზღუდვები და გაურკვევლობები

- ორი Python reference დამოუკიდებელი იმპლემენტაციაა, მაგრამ ორივე CPython-ში სრულდება; ეს არ არის MPFR, SoftFloat, ფორმალური მტკიცება ან დამოუკიდებლად შენარჩუნებული numerical library.
- ტესტი ამოწმებს უკვე დაგროვილი exact integer-ის rounding-ს; ის არ ამტკიცებს arbitrary unbounded input count-ისას accumulation/merge ოპერაციების overflow safety-ს.
- 2,560-bit accumulator-ის გარეთ მნიშვნელობები ამ ტესტის ფარგლებს გარეთაა.
- hosted x86-64/ARM64 CI არ წარმოადგენს დამოუკიდებელ physical-hardware replication-ს.
- შესრულების ან ენერგომოხმარების შესახებ დასკვნა არ კეთდება.

## დასკვნა

გაფართოებული ტესტი ღირებულია როგორც უფრო ფართო regression gate, მაგრამ კვლევის სტატუსი უნდა დარჩეს draft/preliminary. წარმატებული CI იქნება გამეორებადი პროგრამული ტესტის მტკიცებულება და არა სრული მათემატიკური ან ფორმალური დადასტურება.

## წყაროები

- [NOEMA PR #42](https://github.com/maisuradzee/bibmom/pull/42)
- [NOEMA exact-rounding CI run 45809003616](https://github.com/maisuradzee/bibmom/actions/runs/45809003616)
- [IEEE Std 754-2019](https://doi.org/10.1109/IEEESTD.2019.8766229)

## შემდეგი ნაბიჯები

- exact-head x86-64 და ARM64 CI ხელახლა გაუშვი;
- თუ ყველა შემთხვევა გაივლის, ჩაწერე რეალური შემთხვევების რაოდენობა და workflow run IDs;
- შემდეგ ეტაპზე მოითხოვე MPFR ან SoftFloat cross-check და დამოუკიდებელი numerical-method review.

## შემოწმების სტატუსი

- **Draft:** ახალი test extension შექმნილია.
- **Initial CI:** ჩავარდა სარედაქციო კონტრაქტისა და harness newline-ის შეცდომით.
- **Current exact-head CI:** pending; შედეგი ჯერ არ უნდა ჩაითვალოს დადასტურებულად.

## ცვლილებების ისტორია

- 2026-11-26 — დაემატა deterministic full-width random და tie-adjacent oracle protocol; initial CI-ის ორი შეცდომა დაფიქსირდა და გასწორდა.
