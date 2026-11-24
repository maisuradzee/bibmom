# NOEMA-2026-005 — მცურავი წერტილის ჯამის სიზუსტე: მიმდევრობა და კომპენსირებული ალგორითმები

- **ID:** NOEMA-2026-005
- **სტატუსი:** review
- **თარიღი:** 2026-11-23
- **სფერო:** რიცხვითი ანალიზი, კომპიუტერული მათემატიკა, გამოთვლების სანდოობა
- **ავტორი/მომზადების სისტემა:** NOEMA — AI-ით მხარდაჭერილი კვლევითი ციკლი

## საკვლევი კითხვა

რამდენად ცვლის მცურავი წერტილის რიცხვების შეკრების მიმდევრობა საბოლოო შედეგს binary32 და binary64 ფორმატებში, ძლიერ გაუქმებად (cancellation) ამოცანებში, და რომელი გავრცელებული ალგორითმები აღადგენს სწორად დამრგვალებულ ჯამს კონტროლირებულ შემთხვევებში?

## მოკლე შეჯამება

კვლევა შეკრების რიგითობის გავლენას ოთხ რიცხვით ფორმატში ამოწმებს: binary32, binary64, decimal64 და decimal128. თითოეულ ფორმატში გამოყენებულია ორი კონტროლირებული, ხელოვნურად აგებული შემთხვევა — cancellation და half-ULP დაგროვება. თითოეული ფორმატის ორი შემთხვევა ჯამში 12 დალაგებას მოიცავს; ოთხივე ფორმატში სულ 48 დალაგებაა.

Binary32/binary64-ში შედარებულია ექვსი მეთოდი: naive, adjacent pairwise, Kahan, Neumaier, `math.fsum`-ზე დაფუძნებული გზა და ზუსტი integer superaccumulator. Decimal64/decimal128-ში შედარებულია ხუთი მეთოდი: naive, pairwise, Kahan, Neumaier და ზუსტი integer superaccumulator. Binary32-ის `math.fsum_then_round_binary32` უფრო მაღალი სიზუსტის საკონტროლო გზაა და არა binary32-native შეკრება.

ორობით ფორმატებში ეტალონი არის წარმოდგენილი შეყვანების ზუსტი Fraction ჯამი, შემდეგ შესაბამის ფორმატში სწორად დამრგვალებული. Decimal ფორმატებში იგივე მიდგომა გამოიყენება წარმოდგენილი Decimal მნიშვნელობებისთვის; ზუსტი ჯამი გროვდება (10^{E_{tiny}}) ერთეულებში და საბოლოოდ მრგვალდება decimal Context-ში. Decimal ექსპერიმენტი Python `decimal.Context`-ით ემულირებს არჩეულ precision/exponent/clamp პარამეტრებს; ის არ არის IEEE decimal interchange encoding-ის იმპლემენტაცია.

შედეგები აჩვენებს, რომ რიგითობა და არითმეტიკის სიზუსტე მნიშვნელოვანია: decimal64 cancellation ტესტში naive შეკრებამ 3/7 დალაგება სწორად დაამრგვალა, ხოლო decimal128-ის 34-ციფრიანმა სიზუსტემ ამ კონკრეტულ შემთხვევაზე ყველა მეთოდს 7/7 შედეგი მისცა. Decimal half-ULP ტესტებში naive მეთოდი 4/5, pairwise კი 3/5 დალაგებაზე სწორად დამრგვალდა; Kahan, Neumaier და integer superaccumulator ორივე decimal ფორმატში 5/5-ით დაემთხვა ეტალონს.

ეს შედეგები ეხება მხოლოდ წინასწარ განსაზღვრულ synthetic stress cases-ს. ისინი არ აფასებს რეალური პროგრამული დატვირთვების შეცდომის სიხშირეს და არ ადგენს მეთოდების უნივერსალურ რეიტინგს.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

რიცხვითი შეკრება გამოიყენება სტატისტიკაში, სამეცნიერო მოდელირებაში, ფინანსურ გამოთვლებში, გეომეტრიულ ალგორითმებსა და მანქანურ სწავლებაში. binary64-ში მნიშვნელობებს სასრული სიზუსტე აქვთ; როცა ძალიან მცირე წევრი ბევრად დიდ შუალედურ ჯამს ემატება, მისი წვლილი შეიძლება დამრგვალებამ დაკარგოს. მოგვიანებით დიდი დადებითი და უარყოფითი წევრების გაუქმებისას დაკარგული მცირე წვლილი ვეღარ აღდგება.

პრობლემა მხოლოდ „ცუდი მონაცემი“ არ არის. ერთი და იგივე რიცხვების განსხვავებული მიმდევრობა განსხვავებულ შედეგს იძლევა. პარალელური გამოთვლებისას კი შემცირების ხის ან thread-ების განრიგის შეცვლამ შეიძლება შედეგი შეცვალოს, თუ შეკრების წესი წინასწარ განსაზღვრული არ არის.

## არსებული ცოდნა და წყაროები

1. **Nicholas J. Higham — “The Accuracy of Floating Point Summation.”** *SIAM Journal on Scientific Computing*, 14(4), 783–799, July 1993. DOI: [10.1137/0914050](https://doi.org/10.1137/0914050). Accessed: 2026-11-24.
   რეცენზირებული ნაშრომი აანალიზებს შეკრების რამდენიმე მეთოდს, რიგითობასა და rounding error-ს; ავტორი პირდაპირ აღნიშნავს, რომ არც ერთი მეთოდი ყველა შემთხვევაში უნივერსალურად ყველაზე ზუსტი არ არის.

2. **Takeshi Ogita, Siegfried M. Rump & Shin’ichi Oishi — “Accurate Sum and Dot Product.”** *SIAM Journal on Scientific Computing*, 26(6), 1955–1988, January 2005; online publication: 25 July 2006. DOI: [10.1137/030601818](https://doi.org/10.1137/030601818). Accessed: 2026-11-24.
   აღწერს error-free transformation-ზე დაფუძნებულ ზუსტ/მაღალი სიზუსტის შეკრებისა და dot-product ალგორითმებს.

3. **Jonathan Richard Shewchuk — “Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates.”** *Discrete & Computational Geometry*, 18(3), 305–363, October 1997. DOI: [10.1007/PL00009321](https://doi.org/10.1007/PL00009321). Accessed: 2026-11-24.
   ავტორის პირველადი ნაშრომი აჩვენებს ადაპტიური სიზუსტის გამოყენებას და სანდო გეომეტრიული predicate-ების აგებას.

4. **IEEE Computer Society — IEEE Std 754-2019, “IEEE Standard for Floating-Point Arithmetic.”** Published: 22 July 2019; board approval: 13 June 2019. [IEEE Standards record](https://standards.ieee.org/ieee/754/6210/). Accessed: 2026-11-24.
   პირველადი სტანდარტი განსაზღვრავს binary/decimal ფორმატებსა და ოპერაციებს; ნორმატიული შედეგი დამოკიდებულია შეყვანებზე, ოპერაციების მიმდევრობასა და დანიშნულების ფორმატზე.

5. **Python Software Foundation — Python 3.12.16 documentation, Built-in Functions: `sum()`.** Version label: Python 3.12.16 documentation; page last updated: 26 October 2026 (15:00 UTC). No separate page-publication date is stated. [Official documentation](https://docs.python.org/3.12/library/functions.html#sum). Accessed: 2026-11-24.
   დოკუმენტაცია აღნიშნავს, რომ Python 3.12-დან float-ების `sum()` ალგორითმი შეიცვალა და უმეტეს build-ზე უფრო მაღალი სიზუსტე აქვს; ამიტომ კვლევის naive baseline ხელითაა განსაზღვრული.

6. **Python Software Foundation — Python 3.12.16 documentation, `math.fsum()`.** Version label: Python 3.12.16 documentation; page last updated: 26 October 2026 (15:00 UTC). No separate page-publication date is stated. [Official documentation](https://docs.python.org/3.12/library/math.html#math.fsum). Accessed: 2026-11-24.
   აღწერს partial sums-ის შენარჩუნებას და აფრთხილებს ზოგიერთ პლატფორმაზე extended precision-ის გამო შესაძლო double-rounding-ს.

7. **Python Software Foundation — Python 3.12.16 documentation, `decimal` module.** Version label: Python 3.12.16 documentation; page last updated: 26 October 2026 (15:00 UTC). No separate page-publication date is stated. [Official documentation](https://docs.python.org/3.12/library/decimal.html). Accessed: 2026-11-24.
   აღწერს Context-ის precision, rounding, exponent bounds და clamp პარამეტრებს, რომლებსაც decimal64/decimal128 ემულაცია ეყრდნობა.

8. **National Institute of Standards and Technology — NIST Digital Library of Mathematical Functions, §3.1 “Arithmetics and Error Measures.”** DLMF released: 11 May 2010; current site version recorded as 1.2.8 (15 September 2026). [NIST DLMF](https://dlmf.nist.gov/3.1). Accessed: 2026-11-24.
   რიცხვითი არითმეტიკისა და შეცდომის საზომების მეთოდოლოგიური საცნობარო წყარო.

9. **Python Software Foundation — Python 3.14.4 release.** Released: 7 April 2026. [Python.org release record](https://www.python.org/downloads/release/python-3144/). Accessed: 2026-11-24.
   ამ წყაროს მიზანია benchmark provenance-ში დაფიქსირებული CPython 3.14.4 ვერსიის გამოშვების თარიღის გადამოწმება; ის არ ნიშნავს, რომ ეს ვერსია 2026-11-24-ის უახლესი patch release იყო.

## მტკიცებულებები

### FACT — წყაროებით დადასტურებული

- binary64 ფორმატს 53-ბიტიანი significand precision აქვს; ათობითი ჩანაწერის ყველა წილადი ზუსტად არ წარმოდგება binary64-ში.
- შეკრების სხვადასხვა ალგორითმს განსხვავებული შეცდომის პროფილი აქვს; Higham-ის ანალიზი არ ამტკიცებს ერთი მეთოდის უნივერსალურ უპირატესობას.
- Python-ის ჩაშენებული sum() float-ებისთვის Python 3.12-ში შეიცვალა; ამიტომ სხვადასხვა Python ვერსიაში მისი შედეგის ინტერპრეტაცია ვერსიის გათვალისწინებას მოითხოვს.
- math.fsum() შუალედურ partial sums-ს ინახავს და უფრო ზუსტ ჯამს ისახავს მიზნად, თუმცა Python-ის დოკუმენტაციაში პლატფორმული caveat-იც არის მითითებული.

### REPRODUCED RESULT — ამ ციკლში ხელახლა მიღებული

**ექსპერიმენტი A — cancellation triplets**

- შეყვანა: 1,000-ჯერ გამეორებული სამეული [1e16, 1.0, -1e16], სულ 3,000 binary64 წევრი.
- ზუსტი რაციონალური ჯამი: 1,000.
- ერთი და იგივე მულტისეტი შემოწმდა შვიდი დალაგებით: თავდაპირველი სამეულები, შებრუნებული, აბსოლუტური მნიშვნელობით ზრდად/კლებად დალაგებული, ორი დაჯგუფებული ვარიანტი და ფიქსირებული seed-ით შემთხვევითი არევა.
- შეყვანის პირობითობის მაჩვენებელი sum(|xᵢ|)/|sum(xᵢ)| იყო 2×10¹⁶.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| ჩვეულებრივი მარცხნიდან-მარჯვნივ | 2/7 | 100% |
| წყვილური adjacent reduction | 2/7 | 100% |
| Kahan | 4/7 | 100% |
| Neumaier | 7/7 | 0% |
| math.fsum | 7/7 | 0% |
| ზუსტი integer accumulator | 7/7 | 0% |

ფიქსირებული seed-ით არეულ მიმდევრობაში naive და pairwise მეთოდებმა 0 მიიღეს, Kahan-მა — 768, ხოლო Neumaier-მა, math.fsum-მა და integer superaccumulator-მა — 1,000.

**ექსპერიმენტი B — half-ULP დაგროვება**

- შეყვანა: [1.0] + 1,024-ჯერ გამეორებული 2⁻⁵³ + [-1.0], სულ 1,026 წევრი.
- 2⁻⁵³ არის 1.0-ის გარშემო binary64 ULP-ის ნახევარი.
- ზუსტი ჯამი: 2⁻⁴³ = 1/8,796,093,022,208.
- შემოწმდა ხუთი დალაგება; პირობითობის მაჩვენებელი დაახლოებით 1.7592×10¹³ იყო.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| ჩვეულებრივი მარცხნიდან-მარჯვნივ | 4/5 | 100% |
| წყვილური adjacent reduction | 3/5 | 0.09765625% |
| Kahan | 5/5 | 0% |
| Neumaier | 5/5 | 0% |
| math.fsum | 5/5 | 0% |
| ზუსტი integer accumulator | 5/5 | 0% |

### დამატებითი ზუსტი დაგროვების კონტროლი — 2026-11-24

დაემატა integer superaccumulator: ყოველი სასრული binary64 მნიშვნელობა გარდაიქმნება ზუსტ მთელ რიცხვად, რომლის ერთეულია 2⁻¹⁰⁷⁴ — binary64-ის უმცირესი დადებითი subnormal მნიშვნელობა. დაგროვება სრულდება Python-ის arbitrary-precision integer-ით, შუალედური მცურავი წერტილის შეკრების გარეშე, ხოლო საბოლოო ჯამი binary64-ში მხოლოდ ერთხელ მრგვალდება.

- Cancellation შემთხვევა: 7/7 დალაგებაში სწორად დამრგვალებული შედეგი.
- Half-ULP შემთხვევა: 5/5 დალაგებაში სწორად დამრგვალებული შედეგი.
- ორივე შემთხვევის ყველა 12 დალაგებაში integer-ის ზუსტი ერთეულები ემთხვევა Fraction-ით გამოთვლილ წარმოდგენილი შეყვანების ჯამს.

**შეზღუდვა:** დაგროვების გზა ცალკეა, მაგრამ საბოლოო rational-to-binary64 გარდაქმნა იყენებს Python `Fraction`-ის კონვერტაციას. ამიტომ ეს არის ზუსტი დაგროვების დამოუკიდებელი კონტროლი და არა დამოუკიდებელი floating-point rounding implementation.



### ექსპერიმენტი C — binary32 cancellation triplets

- შეყვანა: 100-ჯერ გამეორებული სამეული [1e8, 1.0, -1e8]; ყველა წევრი წინასწარ წარმოდგენილია binary32-ში; სულ 300 წევრი.
- ზუსტი ჯამი წარმოდგენილი binary32 წევრებისთვის: 100.
- შემოწმდა იგივე მულტისეტის 7 დალაგება.
- პირობითობის მაჩვენებელი: 200,000,001.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| binary32 naive | 1/7 | 156% |
| binary32 pairwise | 2/7 | 100% |
| binary32 Kahan | 1/7 | 100% |
| binary32 Neumaier | 7/7 | 0% |
| math.fsum შემდეგ binary32 cast | 7/7 | 0% |
| ზუსტი binary32 integer accumulator | 7/7 | 0% |

### ექსპერიმენტი D — binary32 half-ULP დაგროვება

- შეყვანა: [1.0] + 128-ჯერ გამეორებული 2⁻²⁴ + [-1.0], სულ 130 binary32 წევრი.
- 2⁻²⁴ არის 1.0-ის გარშემო binary32 ULP-ის ნახევარი.
- ზუსტი ჯამი: 2⁻¹⁷ = 1/131,072.
- შემოწმდა 5 დალაგება; პირობითობის მაჩვენებელი: 262,145.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| binary32 naive | 4/5 | 100% |
| binary32 pairwise | 3/5 | 0.78125% |
| binary32 Kahan | 5/5 | 0% |
| binary32 Neumaier | 5/5 | 0% |
| math.fsum შემდეგ binary32 cast | 5/5 | 0% |
| ზუსტი binary32 integer accumulator | 5/5 | 0% |

Binary32 ეტალონისთვის გამოყენებულია წარმოდგენილი binary32 მნიშვნელობების ზუსტი Fraction ჯამი, რომელიც პირდაპირ მრგვალდება binary32-ზე round-to-nearest, ties-to-even წესით. დამრგვალების კოდი მუშაობს მთელ რიცხვით შეფარდებებზე; binary64 შუამავალი cast არ გამოიყენება ეტალონის დასადგენად.

**მნიშვნელოვანი განსხვავება:** naive/pairwise/Kahan/Neumaier ალგორითმებში ყოველი შუალედური არითმეტიკული შედეგი binary32-ში მრგვალდება. `math.fsum_then_round_binary32` სპეციალურად არის ფართო სიზუსტის კონტროლი: შეყვანები ზუსტ binary32 მნიშვნელობებად გადადის, `math.fsum` აგროვებს მათ Python float სიზუსტით და ბოლოს ხდება ერთი binary32 cast. ეს არ არის binary32-native შეკრება.

**Integer accumulator:** თითოეული binary32 წევრი გარდაიქმნება 2⁻¹⁴⁹ ერთეულებად და გროვდება arbitrary-precision integer-ით; საბოლოო რაციონალური შედეგი პირდაპირ binary32-ზე მრგვალდება ties-to-even წესით. 12-ვე binary32 დალაგებაში accumulator-ის შედეგი ზუსტ ეტალონს დაემთხვა.


### INFERENCE — შედეგების ინტერპრეტაცია

- ერთსა და იმავე binary64 წევრთა მულტისეტზე რიგითობამ შეიძლება საბოლოო ჯამი შეცვალოს; პირველ ტესტში შეცდომა ზუსტი ჯამის 100%-ს აღწევდა.
- Kahan მნიშვნელოვნად ეხმარება ზოგიერთ cancellation შემთხვევას, მაგრამ ამ ტესტებში უნივერსალური გარანტია არ აჩვენა.
- Neumaier-მა ორივე აგებულ სტრეს-ტესტში ყველა შემოწმებულ დალაგებაზე სწორად დამრგვალებული ჯამი აღადგინა. ეს არის ამ ტესტების შედეგი და არა ზოგადი მათემატიკური გარანტიის მტკიცება.
- წყვილური შეკრება ავტომატურად ზუსტი არ არის; მისი შედეგიც დამოკიდებულია შემცირების ხეზე და შეყვანის დალაგებაზე.
- math.fsum ამ გაშვებულ CPython გარემოში ყველა შემოწმებულ დალაგებაზე დაემთხვა ზუსტად გამოთვლილი ჯამის binary64 დამრგვალებას.

### INFERENCE — binary32 შედეგები

- Binary32 შემთხვევებშიც ერთი და იგივე მულტისეტის დალაგება საბოლოო შედეგს ცვლის; naive შეკრებამ cancellation ტესტში მაქსიმუმ 156% ფარდობითი შეცდომა აჩვენა.
- Kahan-ის შედეგი დამოკიდებულია შემთხვევაზე: binary32 cancellation ტესტში მხოლოდ 1/7 დალაგება სწორად დამრგვალდა, ხოლო half-ULP ტესტში 5/5.
- Neumaier-მა და ზუსტმა integer accumulator-მა ორივე binary32 სტრეს-ტესტში ყველა დალაგება სწორად დაამრგვალა.
- math.fsum-then-cast-ის შედეგი არ უნდა გაიგივდეს binary32-native ალგორითმებთან: ეს არის უფრო მაღალი სამუშაო სიზუსტით დაგროვებისა და საბოლოო binary32 cast-ის შედარებითი კონტროლი.
- შედეგები ეხება მხოლოდ ამ synthetic შემთხვევებს; მეთოდების უნივერსალურ რეიტინგს არ ადგენს.


### ექსპერიმენტი E — decimal64 cancellation triplets

- ფორმატი: precision 16, Emin = −383, Emax = +384, Etiny = −398, clamp = 1; დამრგვალება — ROUND_HALF_EVEN.
- შეყვანა: 100-ჯერ გამეორებული `[1e16, 1, -1e16]`, სულ 300 Decimal წევრი; ზუსტი ჯამი 100.
- იგივე მულტისეტი შემოწმდა 7 დალაგებით.
 
| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| naive | 3/7 | 100% |
| pairwise | 4/7 | 100% |
| Kahan | 5/7 | 81% |
| Neumaier | 7/7 | 0% |
| ზუსტი integer accumulator | 7/7 | 0% |

### ექსპერიმენტი F — decimal64 half-ULP დაგროვება

- შეყვანა: `[1]` + 100-ჯერ გამეორებული (5\times10^{-16}) + `[-1]`; სულ 102 წევრი.
- ზუსტი ჯამი: (5\times10^{-14}); half-ULP არის 1-ის გარშემო 16-ნიშნა decimal precision-ის ზღვარზე.
- შემოწმდა 5 დალაგება.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| naive | 4/5 | 100% |
| pairwise | 3/5 | 1% |
| Kahan | 5/5 | 0% |
| Neumaier | 5/5 | 0% |
| ზუსტი integer accumulator | 5/5 | 0% |

### ექსპერიმენტი G — decimal128 cancellation triplets

- ფორმატი: precision 34, Emin = −6143, Emax = +6144, Etiny = −6176, clamp = 1; დამრგვალება — ROUND_HALF_EVEN.
- შეყვანა: decimal64-ის იგივე 300 წევრიანი cancellation მულტისეტი; ზუსტი ჯამი 100.
- შერჩეულ 7 დალაგებაში ხუთივე მეთოდმა 7/7 სწორად დამრგვალებული შედეგი მიიღო; მაქსიმალური ფარდობითი შეცდომა იყო 0%. ეს კონკრეტული შეყვანისათვის decimal128-ის 34-ნიშნა precision-ით მცირე წევრის შენარჩუნების შედეგია და არა ყველა decimal128 გამოთვლის გარანტია.

### ექსპერიმენტი H — decimal128 half-ULP დაგროვება

- შეყვანა: `[1]` + 100-ჯერ გამეორებული (5\times10^{-34}) + `[-1]`; სულ 102 წევრი.
- ზუსტი ჯამი: (5\times10^{-32}); შემოწმდა 5 დალაგება.

| მეთოდი | სწორად დამრგვალებული შედეგი | მაქსიმალური ფარდობითი შეცდომა |
|---|---:|---:|
| naive | 4/5 | 100% |
| pairwise | 3/5 | 1% |
| Kahan | 5/5 | 0% |
| Neumaier | 5/5 | 0% |
| ზუსტი integer accumulator | 5/5 | 0% |

### INFERENCE — decimal შედეგები

- Decimal64-ის 16-ნიშნა precision cancellation მაგალითში მცირე ერთეულის წევრის დაკარგვას იწვევს რიგითობაზე დამოკიდებულად; decimal128-ის 34-ნიშნა precision ამ კონკრეტულ 1e16 + 1 − 1e16 შემთხვევას ყველა შემოწმებულ რიგში ინარჩუნებს.
- Half-ULP მაგალითებში ორივე decimal ფორმატში naive და pairwise მეთოდები რიგითობაზე მგრძნობიარეა.
- Kahan-ის შედეგი დამოკიდებულია როგორც precision-ზე, ისე კონკრეტულ რიგზე; decimal64 cancellation-ში 5/7, decimal64 half-ULP-ში 5/5, decimal128 cancellation-ში 7/7, decimal128 half-ULP-ში 5/5.
- Neumaier-მა და integer superaccumulator-მა ოთხივე decimal stress case-ის ყველა შემოწმებულ რიგში სწორად დამრგვალებული ჯამი მიიღეს.
- Python `decimal.Context`-ის შედეგები ამ კვლევაში ამოწმებს მითითებული precision/exponent/clamp პარამეტრებით არითმეტიკას. ეს არ ამტკიცებს decimal64/decimal128 interchange encoding-ის შესაბამისობას ყველა byte-level დეტალში.


### ჰიპოთეზა

ძლიერ გაუქმებად ჯამებში პროგრამული სისტემის გამეორებადობა გაუმჯობესდება, თუ სისტემა ერთდროულად აფიქსირებს (ა) შეყვანის მიმდევრობას ან შემცირების ხეს, (ბ) შეკრების ალგორითმს და (გ) ზუსტი/მაღალი სიზუსტის ეტალონთან შედარებულ შეცდომის ტესტს.

ამ ჰიპოთეზის ვიწრო ნაწილი შემოწმდა: ერთნაირი მულტისეტის რამდენიმე დალაგებამ განსხვავებული შედეგი წარმოქმნა. დამატებით, 330-კონფიგურაციან sharded-reduction სიმულაციაში Neumaier-ის სრული (sum, compensation) state 330/330 შემთხვევაში დაემთხვა ეტალონს, ხოლო scalar partial-ების მეთოდები სრულ დამთხვევას ვერ აღწევდა.

## კონკურენტი ახსნები

1. **მხოლოდ რიგითობაა მთავარი:** ტესტებში რიგითობა აშკარად ცვლის შედეგს, მაგრამ Higham-ის ანალიზი აჩვენებს, რომ ალგორითმის არჩევანიც დამოუკიდებელი ფაქტორია. ამიტომ რიგითობა ერთადერთი ახსნა არ არის.
2. **კომპენსირებული შეკრება ყოველთვის ზუსტია:** ჩვენი შედეგები ამას არ ამტკიცებს. Kahan-ის ჩავარდნა ერთ-ერთ ტესტში საპირისპირო მაგალითია; Neumaier-ის წარმატებაც მხოლოდ აგებულ შემთხვევებზე ვრცელდება.
3. **წყვილური შეკრება ყოველთვის უკეთესია:** დაბალანსებული ხე ხშირად ამცირებს შეცდომის დაგროვებას, მაგრამ ჩვენი კონკრეტული cancellation მიმდევრობები აჩვენებს, რომ წყვილური ხეც შეიძლება მნიშვნელოვნად შეცდეს.
4. **სწორი პასუხი მხოლოდ უფრო მაღალი precision-ით მიიღება:** Ogita–Rump–Oishi და Shewchuk აღწერენ იმავე precision-ის არითმეტიკით error-free transformation-სა და ადაპტიურ მიდგომებს; ამიტომ დამატებითი სიზუსტე ერთადერთი გამოსავალი არ არის.
5. **თითო worker-ის ზუსტი scalar partial საკმარისია:** სიმულაციაში math.fsum-ის worker-local scalar-იც მხოლოდ 114/330 კონფიგურაციაში დაემთხვა გლობალურ ეტალონს; compensation-ის ცალკე გადაცემა ამ fixture-ზე უფრო გამძლე აღმოჩნდა.

## შემოწმების მეთოდი

1. **Binary64:** შეყვანები შეიქმნა Python binary64 float მნიშვნელობებიდან; ეტალონი გამოითვალა `Fraction.from_float(value)`-ების ზუსტი ჯამით და შემდეგ დამრგვალდა binary64-ში.
2. **Binary32:** თითოეული შეყვანა ჯერ binary32-ში გარდაიქმნა; naive/pairwise/Kahan/Neumaier-ის ყველა primitive არითმეტიკული ოპერაციის შედეგი ხელახლა მრგვალდება binary32-ში. ეტალონისთვის გამოყენებულია ზუსტი Fraction ჯამის პირდაპირი ties-to-even binary32 quantizer — binary64 შუალედური დამრგვალების გარეშე.
3. **Decimal64/decimal128:** Python `decimal.Context` დაყენებულია precision, Emin, Emax, clamp=1 და ROUND_HALF_EVEN პარამეტრებით. თითოეული arithmetic primitive Context-ის მეთოდით სრულდება, რის შედეგადაც მისი შედეგი არჩეულ decimal precision-ში მრგვალდება. ეს არის arithmetic emulation და არა interchange encoding-ის ბიტური იმპლემენტაცია.
4. ყველა ფორმატში ზუსტი integer accumulator შეყვანებს გარდაქმნის შესაბამისი ფორმატის უმცირესი subnormal ერთეულების (binary32 (2^{-149}), binary64 (2^{-1074}), decimal (10^{E_{tiny}})) მთელ რაოდენობად; შემდეგ საბოლოო შედეგი ერთხელ მრგვალდება ფორმატის შესაბამისი კონტექსტით.
5. თითოეულ ფორმატში გამოყენებულია cancellation და half-ULP შემთხვევა; ორივე შემთხვევის ყველა დალაგება ერთსა და იმავე შეყვანის მულტისეტს ინარჩუნებს. Random shuffle იყენებს seed-ს 20261123.
6. სწორად დამრგვალებულად ჩაითვალა მეთოდი, რომლის შედეგიც ემთხვევა შეყვანილი წარმოდგენილი მნიშვნელობების ზუსტ ჯამს შესაბამის ფორმატში დამრგვალებულ ეტალონს.
7. შედეგები, პარამეტრები და გარემოს provenance ინახება `data/noema-005/floating-summation-results.json`-ში. გამეორებადი კოდი: `scripts/simulate_noema005_summation.py`; ტესტები: `tests/test_noema005_summation.py`.
8. Sharded reduction სიმულაციაში გამოყენებულია ზემოთ აღწერილი 330 კონფიგურაცია; სრული case matrix-ის SHA-256, input SHA-256, seed-ები და partition/merge პარამეტრები ინახება `data/noema-005/parallel-reduction-results.json`-სა და `data/noema-005/parallel-reduction-protocol.json`-ში. გამეორებადი კოდი: `scripts/simulate_noema005_parallel_reduction.py`; ტესტები: `tests/test_noema005_parallel_reduction.py`.

### ავტომატური ტესტები

- Binary64/32: ზუსტი Fraction ეტალონი, rounding boundaries, subnormal cases, order sensitivity, non-finite rejection და შედეგების deterministic generation.
- Decimal64/128: Context-ის precision/exponent/clamp პარამეტრები, ზუსტი integer accumulator-ის Fraction reference-თან დამთხვევა ყველა დალაგებაზე, decimal64/128 cancellation ქცევა, half-ULP order sensitivity და non-finite rejection.
- NOEMA-005-ის summation suite შეიცავს 20 unit test-ს; benchmark harness-ს — 2 unit test-ს. სრული საცავის CI suite შეიცავს 74 ტესტს.

### Runtime/memory benchmark protocol — 2026-11-24

დაემატა ცალკე გამეორებადი benchmark harness ოთხივე ფორმატისა და ყველა შესაბამისი მეთოდისათვის: `scripts/benchmark_noema005_summation.py`.

- დრო: `time.perf_counter_ns`; თითო მეთოდის runtime იზომება ცალკე, warmup-ის შემდეგ და შეჯამდება median-ით.
- მეხსიერება: `tracemalloc`-ით ერთი invocation-ის peak traced Python-managed bytes; ეს არ არის სრული RSS და არ ითვლის ყველა native C/extension allocation-ს.
- თითო format/size შემთხვევაში ყველა მეთოდი იღებს ერთსა და იმავე უცვლელ, seed-ით გენერირებულ შეყვანის სიას; ინახება input SHA-256.
- სრული ადგილობრივი პროფილი: sizes 1,024 / 8,192 / 65,536; 2 warmup; 7 repetitions; seed 20261124.
- CI smoke პროფილი: sizes 128 / 512; 1 warmup; 2 repetitions. ბოლო CI-მ გაზომა 8 format/size შემთხვევა და 44 method measurement. CI ამოწმებს ოთხივე ფორმატის დაფარვას, გაზომვების სტრუქტურასა და ვალიდურ მნიშვნელობებს; დროის მყარ ზღვარს არ აწესებს.
- პროტოკოლი: `data/noema-005/benchmark-protocol.json`.

**სტატუსის შენიშვნა:** CI smoke test harness-ის სტრუქტურას ამოწმებს. სრული პროფილი შესრულდა ცალკე GitHub Actions run #4-ზე; შედეგები ქვემოთაა შეჯამებული. ეს არის ერთი CPython/Linux runner-ის აღწერითი გაზომვა და არა სხვადასხვა მანქანაზე განმეორებული performance კვლევა.


### Full runtime/memory profile results — 2026-11-24

სრული პროფილი გაეშვა ცალკე workflow-ით: [run #4](https://github.com/maisuradzee/bibmom/actions/runs/45283854718). შესრულდა 12 format/size შემთხვევა და 66 method measurement. გარემო: CPython 3.14.4, Linux x86-64 (AWS runner); sizes 1,024 / 8,192 / 65,536; 2 warmup; 7 timed repetitions; seed 20261124. ქვემოთ მოცემულია ყველაზე დიდი შეყვანის — 65,536 წევრის — median runtime და `tracemalloc` peak.

| ფორმატი | მეთოდი | median runtime (ms) | peak traced Python bytes |
|---|---|---:|---:|
| binary64 | naive left-to-right | 0.662 | 160 |
| binary64 | adjacent pairwise | 3.644 | 1,593,864 |
| binary64 | Kahan | 2.195 | 232 |
| binary64 | Neumaier | 3.141 | 232 |
| binary64 | math.fsum | 1.104 | 181 |
| binary64 | integer superaccumulator | 60.835 | 4,384 |
| binary32 | naive left-to-right | 81.808 | 3,756 |
| binary32 | adjacent pairwise | 88.222 | 1,597,321 |
| binary32 | Kahan | 324.736 | 3,832 |
| binary32 | Neumaier | 320.630 | 3,832 |
| binary32 | math.fsum then binary32 cast | 0.383 | 536 |
| binary32 | integer superaccumulator | 14.024 | 3,704 |
| decimal64 | naive left-to-right | 6.362 | 480 |
| decimal64 | adjacent pairwise | 11.759 | 6,312,528 |
| decimal64 | Kahan | 25.327 | 1,032 |
| decimal64 | Neumaier | 30.652 | 1,032 |
| decimal64 | integer superaccumulator | 37.376 | 6,853,728 |
| decimal128 | naive left-to-right | 6.365 | 480 |
| decimal128 | adjacent pairwise | 11.737 | 6,312,528 |
| decimal128 | Kahan | 25.232 | 1,032 |
| decimal128 | Neumaier | 31.416 | 1,032 |
| decimal128 | integer superaccumulator | 37.210 | 6,853,728 |

**დაკვირვებები და ინტერპრეტაცია**

- ამ კონკრეტულ CPython/Linux პროფილში binary64 integer accumulator-ის median იყო 60.835 ms, naive-ის — 0.662 ms (დაახლოებით 91.9× განსხვავება). ეს accumulator-ის მიმდინარე Python reference-implementation-ის ხარჯია და არა ზუსტი summation-ის ფუნდამენტური სიჩქარის ქვედა ზღვარი.
- Decimal64/128-ში exact integer accumulator-მა დაახლოებით 37 ms და 6.85 MB peak traced allocation აჩვენა; pairwise-ს ჰქონდა დაახლოებით 11.7 ms და 6.31 MB. მიმდინარე exact accumulator-ის რეალიზაცია მეხსიერების/დროის თვალსაზრისით ოპტიმიზაციას საჭიროებს.
- Pairwise მეთოდის peak memory იზრდება შეყვანის ზომასთან ერთად, რადგან რეალიზაცია ქმნის შუალედურ სამუშაო სიებს; Kahan/Neumaier-ის ამ იმპლემენტაციებს გაცილებით მცირე traced peak ჰქონდათ, თუმცა მეტი დრო სჭირდებოდათ.
- Binary32-ის native-emulation გზები ყოველ ელემენტზე Python-level rational rounding-ს ასრულებს; მათი მაღალი დრო არ ასახავს hardware binary32 ოპერაციის სიჩქარეს. `math.fsum then binary32 cast` ფართო სიზუსტის საკონტროლო გზაა და native binary32 მეთოდებთან პირდაპირი სიჩქარის შედარება არ შეიძლება.
- Decimal64 და decimal128-ის დროები ახლოსაა, რადგან benchmark-ში გამოყენებული შეყვანები ორივე precision-ში წარმოდგენადია; ეს არ ადასტურებს ზოგად თანაბარ ხარჯს ყველა decimal მონაცემზე.
- დროები არის ერთი runner-ის median-ები. სხვა Python build, არქიტექტურა, load, allocator ან input distribution შეიძლება მნიშვნელოვნად განსხვავდებოდეს. `tracemalloc` არ არის RSS და არ ითვლის ყველა native allocation-ს.

სრული 66-გაზომვიანი report ინახება `data/noema-005/benchmark-full-profile-summary-2026-11-24.json`-ში. ორიგინალი report JSON-ის SHA-256: `cb902442026cfe4b74a506d01c568efdb6e009a27f38014ce0548c6bf36f4ce9`; Actions artifact ID `14870647841` (30-დღიანი retention).

### REPRODUCED RESULT — simulated sharded reduction (2026-11-24)

**საკითხი:** თუ თითო worker მხოლოდ ერთ დამრგვალებულ scalar partial-ს აბრუნებს, ინარჩუნებს თუ არა საერთო reduction მცირე კომპონენტებს? შედარებულია scalar partial-ები და worker-ის სრული Neumaier state `(sum, compensation)`.

- შეყვანა: binary64 `[1e16, 1.0, -1e16]` triplet 1,000-ჯერ; სულ 3,000 მნიშვნელობა. შეყვანილი float-ების ზუსტი Fraction ჯამი არის 1,000; სწორად დამრგვალებული binary64 ეტალონიც 1,000.
- მონაცემთა SHA-256 (canonical big-endian binary64): `3a825f21d910a331c4ff4c3a796cacbc9ebb72e02db1686352447c4207fc1bc2`.
- დიზაინი: 2 partition strategy (round-robin, contiguous) × 5 input ordering × 11 worker count × 3 worker merge ordering = **330 კონფიგურაცია**. Seed-ები: input permutation 20261124; worker permutation `20261125 + worker_count`. SHA-256-key permutation სპეციალურადაა განსაზღვრული Python ვერსიებს შორის სტაბილურობისთვის.
- თითო worker-ის scalar შედეგები pairwise tree-ით გაერთიანდა; state ვარიანტში თითო worker-მა გადასცა ორივე კომპონენტი და საბოლოო reducer-მა ყველა კომპონენტს Neumaier summation გაუკეთა.

| Worker output / merge | სწორად დამრგვალებული შედეგი |
|---|---:|
| naive scalar + pairwise merge | 0/330 |
| Kahan scalar + pairwise merge | 24/330 |
| Neumaier total scalar + pairwise merge | 114/330 |
| math.fsum scalar + pairwise merge | 114/330 |
| Neumaier `(sum, compensation)` state + compensated global merge | **330/330** |

- ყველა 330 state-merge შედეგი იყო 1,000; scalar partial მეთოდებმა სხვადასხვა კონფიგურაციაში დაკარგეს მცირე კომპონენტები ან მიიღეს სხვა შედეგი. მაქსიმალური scalar output ამ აგებულ ტესტში 1,216 იყო.
- სრული 330-კონფიგურაციანი case matrix-ის SHA-256: `ad15ddf2119ac798e66ffa22bfe6854801a9b9d810283c03212c516c14008625`. შეჯამება ინახება `data/noema-005/parallel-reduction-results.json`-ში; პარამეტრები — `data/noema-005/parallel-reduction-protocol.json`-ში; კოდი — `scripts/simulate_noema005_parallel_reduction.py`.

**მნიშვნელოვანი შეზღუდვა:** ეს არის დეტერმინისტული map/reduce სიმულაცია და არა რეალური threads, GPU, network/distributed runtime ან production workload. შედეგი ამტკიცებს მხოლოდ იმას, რომ ამ კონკრეტულ cancellation fixture-ში scalar partial-მა ინფორმაცია დაკარგა, ხოლო compensation state-ის გადაცემამ შეინარჩუნა. ის არ ამტკიცებს Neumaier state-ის უნივერსალურ სიზუსტეს ყველა მონაცემზე ან ყველა merge tree-ზე.

**INFERENCE:** განაწილებულ ჯამში მხოლოდ worker-ის საბოლოო scalar-ის გადაცემა შეიძლება არასაკმარისი იყოს. კონტრაქტმა უნდა განსაზღვროს partial state-ის ფორმა და მისი გაერთიანების ალგორითმი; ალტერნატივაა ზუსტი accumulator state.

**HYPOTHESIS:** რთულ cancellation workload-ებში worker compensation-ის შენარჩუნება და მისი კონტროლირებული global merge ზრდის სწორად დამრგვალებული შედეგის მიღების შანსს scalar-only reduction-თან შედარებით. ეს ჰიპოთეზა ამ fixture-ზე შემოწმდა, მაგრამ რეალურ პარალელურ სისტემაზე ჯერ არა.

## შეზღუდვები და გაურკვევლობები

- ეს არის ხელოვნურად აგებული რიცხვითი სტრეს-ტესტები და არა რეალური ფინანსური, კლიმატური ან საინჟინრო მონაცემების აუდიტი.
- შემოწმებულია binary32, binary64, decimal64 და decimal128 ფორმატების ემულაცია; შედეგები ყველა მონაცემთა განაწილებაზე ან რეალურ workload-ზე არ განზოგადდება.
- Decimal64/decimal128 ნაწილი იყენებს Python `decimal.Context`-ს შესაბამის precision, exponent, clamp და ROUND_HALF_EVEN პარამეტრებით. ის არ ამოწმებს IEEE decimal interchange-ის BID/DPD კოდირებას ან byte-level თავსებადობას.
- Binary32-ის `math.fsum_then_round_binary32` არის ფართო სიზუსტის კონტროლი და არა binary32-native მეთოდი.
- ზუსტი integer accumulator-ის დაგროვება სრულდება arbitrary-precision integer-ით; decimal-ში საერთო quantum შეყვანებიდან დინამიკურად განისაზღვრება. საბოლოო rounding იყენებს შესაბამისი ფორმატის Fraction/Context converter-ს. ეს არ არის დამოუკიდებელი hardware rounding implementation.
- ოთხფორმატიანი accuracy და runtime/memory პროფილი შესრულდა ერთ CPython/Linux გარემოში. Sharded-reduction სიმულაციის საწყისი გაშვება შესრულდა CPython 3.13.5/Linux x86_64-ზე; იგივე 330-case summary და case-matrix SHA-256 ხელახლა დადასტურდა [CI run 45325226165](https://github.com/maisuradzee/bibmom/actions/runs/45325226165)-ში, CPython 3.14.4/Linux x86_64/glibc 2.43-ზე. ეს არის cross-version გამეორება, მაგრამ არა cross-architecture ან hardware-parallel გამეორება.
- Python 3.12-დან ჩაშენებული sum() float-ებისთვის გაუმჯობესებულ ალგორითმს იყენებს; აქ naive baseline ხელითაა განსაზღვრული, როგორც მარცხნიდან-მარჯვნივ დაგროვება.
- დამატებულია runtime/memory benchmark harness; CI smoke-მა 8 format/size შემთხვევა და 44 method measurement შეასრულა, ხოლო სრული პროფილმა — 12 შემთხვევა და 66 გაზომვა ერთ CPython/Linux runner-ზე. ეს არ არის cross-platform გამეორება; `tracemalloc` ზომავს მხოლოდ Python-managed allocations-ს და არა სრულ RSS-ს. Thread/GPU parallel reduction მხოლოდ სიმულაციითაა წარმოდგენილი; რეალური thread scheduling, GPU kernel, network transport და distributed runtime ჯერ არ გამოკვლეულა.
- ზუსტი reference ეხება მხოლოდ რეალურად წარმოდგენილ შეყვანებს; ის არ ამოწმებს შეყვანის წყაროს სიზუსტეს ან შემდგომი მოდელის სისწორეს.
- შედეგები არ წარმოადგენს ყველა პლატფორმაზე method-ի უნივერსალურ გარანტიას ან წარმოების workload-ის error-rate შეფასებას.

## ეთიკა და უსაფრთხოება

ადამიანის მონაცემები, პერსონალური ინფორმაცია ან ცოცხალ სისტემებზე ექსპერიმენტი არ გამოყენებულა. მთავარი რისკია რიცხვითი შედეგის ზედმეტი ნდობა: ფინანსურ, სამედიცინო, საავიაციო, სამრეწველო ან გეომეტრიულ უსაფრთხოებაზე მოქმედ სისტემაში მხოლოდ ერთი სტრეს-ტესტი ან კომპენსირებული ჯამი საკმარისი არ არის. ასეთ გარემოში საჭიროა ამოცანის სპეციფიკური შეცდომის ზღვარი, დამოუკიდებელი ვალიდაცია და საჭიროებისას interval/exact/adaptive precision.

## დასკვნა

ამ კვლევაში შეკრების მიმდევრობამ ერთი და იმავე binary64 რიცხვების მულტისეტისთვის შედეგი შეცვალა; პირველ ტესტში naive და pairwise მეთოდების მაქსიმალური ფარდობითი შეცდომა 100% იყო. Kahan-ის კომპენსაცია ყველა შემთხვევას ვერ აგვარებდა, ხოლო Neumaier-მა, math.fsum-მა და ზუსტმა integer accumulator-მა ორივე აგებულ ტესტში ყველა შემოწმებულ დალაგებაზე სწორად დამრგვალებული შედეგი მიიღეს.

მთავარი პრაქტიკული დასკვნაა: რიცხვითი პროგრამის გამეორებადობისთვის უნდა დაფიქსირდეს არა მხოლოდ მონაცემები, არამედ შეკრების ალგორითმი, რიგითობა/შემცირების ხე და განაწილებულ გამოთვლაში worker partial state-ის ფორმა. შედეგი არ ამტკიცებს უნივერსალურ ალგორითმს; იგი გვთავაზობს შემოწმების წესს, რომლითაც ასეთი შეცდომები კონკრეტულ პროექტში ადრეულ ეტაპზე გამოვლინდება.

## ახალი იდეა — summation contract

NOEMA სთავაზობს რიცხვით პროექტებს მცირე “summation contract”-ს:

- მიუთითონ დაგროვების ალგორითმი;
- განსაზღვრონ input ordering ან deterministic reduction tree;
- შეინახონ adversarial cancellation regression fixture;
- შეადარონ შედეგი ზუსტ ან მაღალი სიზუსტის ეტალონს;
- ჩაწერონ runtime, precision, rounding mode და შეცდომის დასაშვები ზღვარი;
- განაწილებულ გამოთვლაში განსაზღვრონ worker state: მხოლოდ scalar partial თუ compensation/exact accumulator state, და როგორ ხდება მისი გლობალური merge.

ეს არ არის ახალი შეკრების ალგორითმი; ეს არის გამეორებადობისა და აუდიტის დიზაინ-წესი. მისი რეალურ პროექტებში ეფექტიანობა ჯერ არ შემოწმებულა.

## შემდეგი ნაბიჯები

1. განმეორდეს სრული benchmark სულ მცირე სამ დამოუკიდებელ run-ზე და სხვა Python ვერსიასა/არქიტექტურაზე; გაიმიჯნოს noise და runtime-specific შედეგები.
2. დაიხვეწოს exact integer accumulator-ის ალგორითმი, განსაკუთრებით binary64/decimal-ში, და ხელახლა გაიზომოს დრო/მეხსიერება ისე, რომ ზუსტი ეტალონი უცვლელი დარჩეს.
3. სიმულაციის შემდეგ შემოწმდეს რეალური CPU threads, GPU და მინიმუმ ერთი distributed framework; შეადარდეს scalar-only და compensation-state API-ები.
4. დაემატოს რეალური სამეცნიერო მონაცემთა ნაკრები, რომლის შეყვანის სიზუსტე და provenance დამოუკიდებლად დოკუმენტირებულია.
5. დამოუკიდებელმა მკვლევარმა გადაამოწმოს binary32 quantizer, decimal Context-ის პარამეტრები, exact accumulator, benchmark-ის მეთოდოლოგია, ტესტები და გამოყენებული წყაროები.

## ქართულენოვანი ვებსაიტისთვის მომზადებული ტექსტი

### რატომ შეიძლება ერთი და იგივე რიცხვების ჯამი განსხვავებული იყოს?

კომპიუტერი ათობითი რიცხვების უმეტესობას ზუსტად ვერ ინახავს: ის მათ სასრული სიზუსტის ორობით ფორმაში წარმოადგენს. როცა ძალიან მცირე რიცხვს ძალიან დიდ შუალედურ ჯამს ვუმატებთ, მცირე წვლილი შეიძლება დამრგვალებამ დაკარგოს. თუ შემდეგ დიდი დადებითი და უარყოფითი რიცხვები ერთმანეთს გააუქმებს, დაკარგული წვლილი ვეღარ აღდგება.

NOEMA-ს კონტროლირებულმა ექსპერიმენტმა ერთი და იგივე რიცხვები სხვადასხვა რიგით შეაჯამა binary32, binary64, decimal64 და decimal128 ფორმატებში. შედეგები აჩვენებს, რომ precision, შეკრების მეთოდი და მიმდევრობა ერთად განსაზღვრავს საბოლოო ჯამს. ერთ-ერთ ტესტში ჩვეულებრივმა შეკრებამ ზუსტი ჯამის ნაცვლად ნული დააბრუნა. Kahan-ის მეთოდმაც ყველა დალაგებაში ვერ აღადგინა შედეგი, ხოლო Neumaier-მა და integer superaccumulator-მა ამ კონკრეტულ ტესტებში ყველა რიგზე ზუსტი, სწორად დამრგვალებული ჯამი მიიღეს.

ეს არ ნიშნავს, რომ ერთი ალგორითმი ყველა ამოცანაში საუკეთესოა. კვლევა აჩვენებს უფრო ზოგად პრაქტიკულ წესს: სამეცნიერო პროგრამამ უნდა დააფიქსიროს შეკრების მეთოდი და რიგითობა, ხოლო რთული ჯამები ზუსტ ან მაღალი სიზუსტის ეტალონთან შეამოწმოს.

## წყაროები

- **Nicholas J. Higham — “The Accuracy of Floating Point Summation.”** *SIAM Journal on Scientific Computing*, 14(4), 783–799, July 1993. DOI: [10.1137/0914050](https://doi.org/10.1137/0914050). Accessed: 2026-11-24.
   რეცენზირებული ნაშრომი აანალიზებს შეკრების რამდენიმე მეთოდს, რიგითობასა და rounding error-ს; ავტორი პირდაპირ აღნიშნავს, რომ არც ერთი მეთოდი ყველა შემთხვევაში უნივერსალურად ყველაზე ზუსტი არ არის.

- **Takeshi Ogita, Siegfried M. Rump & Shin’ichi Oishi — “Accurate Sum and Dot Product.”** *SIAM Journal on Scientific Computing*, 26(6), 1955–1988, January 2005; online publication: 25 July 2006. DOI: [10.1137/030601818](https://doi.org/10.1137/030601818). Accessed: 2026-11-24.
   აღწერს error-free transformation-ზე დაფუძნებულ ზუსტ/მაღალი სიზუსტის შეკრებისა და dot-product ალგორითმებს.

- **Jonathan Richard Shewchuk — “Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates.”** *Discrete & Computational Geometry*, 18(3), 305–363, October 1997. DOI: [10.1007/PL00009321](https://doi.org/10.1007/PL00009321). Accessed: 2026-11-24.
   ავტორის პირველადი ნაშრომი აჩვენებს ადაპტიური სიზუსტის გამოყენებას და სანდო გეომეტრიული predicate-ების აგებას.

- **IEEE Computer Society — IEEE Std 754-2019, “IEEE Standard for Floating-Point Arithmetic.”** Published: 22 July 2019; board approval: 13 June 2019. [IEEE Standards record](https://standards.ieee.org/ieee/754/6210/). Accessed: 2026-11-24.
   პირველადი სტანდარტი განსაზღვრავს binary/decimal ფორმატებსა და ოპერაციებს; ნორმატიული შედეგი დამოკიდებულია შეყვანებზე, ოპერაციების მიმდევრობასა და დანიშნულების ფორმატზე.

- **Python Software Foundation — Python 3.12.16 documentation, Built-in Functions: `sum()`.** Version release: 25 October 2026. [Official documentation](https://docs.python.org/3.12/library/functions.html#sum). Accessed: 2026-11-24.
   დოკუმენტაცია აღნიშნავს, რომ Python 3.12-დან float-ების `sum()` ალგორითმი შეიცვალა და უმეტეს build-ზე უფრო მაღალი სიზუსტე აქვს; ამიტომ კვლევის naive baseline ხელითაა განსაზღვრული.

- **Python Software Foundation — Python 3.12.16 documentation, `math.fsum()`.** Version release: 25 October 2026. [Official documentation](https://docs.python.org/3.12/library/math.html#math.fsum). Accessed: 2026-11-24.
   აღწერს partial sums-ის შენარჩუნებას და აფრთხილებს ზოგიერთ პლატფორმაზე extended precision-ის გამო შესაძლო double-rounding-ს.

- **Python Software Foundation — Python 3.12.16 documentation, `decimal` module.** Version release: 25 October 2026. [Official documentation](https://docs.python.org/3.12/library/decimal.html). Accessed: 2026-11-24.
   აღწერს Context-ის precision, rounding, exponent bounds და clamp პარამეტრებს, რომლებსაც decimal64/decimal128 ემულაცია ეყრდნობა.

- **National Institute of Standards and Technology — NIST Digital Library of Mathematical Functions, §3.1 “Arithmetics and Error Measures.”** DLMF released: 11 May 2010; current site version recorded as 1.2.8 (15 September 2026). [NIST DLMF](https://dlmf.nist.gov/3.1). Accessed: 2026-11-24.
   რიცხვითი არითმეტიკისა და შეცდომის საზომების მეთოდოლოგიური საცნობარო წყარო.

- **Python Software Foundation — Python 3.14.4 release.** Released: 7 April 2026. [Python.org release record](https://www.python.org/downloads/release/python-3144/). Accessed: 2026-11-24.
   ამ წყაროს მიზანია benchmark provenance-ში დაფიქსირებული CPython 3.14.4 ვერსიის გამოშვების თარიღის გადამოწმება; ის არ ნიშნავს, რომ ეს ვერსია 2026-11-24-ის უახლესი patch release იყო.

## შემოწმების სტატუსი

- [x] README, კვლევითი სტანდარტი, შაბლონი, არსებული დრაფტების სია, გამოქვეყნებული კვლევების დირექტორია, საჯარო ინდექსი და არსებული NOEMA-002 პროტოკოლი გადამოწმებულია.
- [x] შერჩეულია წინა NOEMA კვლევებისგან განსხვავებული საკითხი.
- [x] გამოყენებულია პირველადი სტანდარტი, ოფიციალური დოკუმენტაცია და რეცენზირებული რიცხვითი ანალიზის ნაშრომები.
- [x] Binary32/binary64: 2 stress test თითო ფორმატში, 12 დალაგება თითო ფორმატში, 6 method; decimal64/decimal128: 2 stress test თითო ფორმატში, 12 დალაგება თითო ფორმატში, 5 method.
- [x] შედეგები შედარებულია Fraction-ით გამოთვლილ ზუსტ რაციონალურ ეტალონთან და 2⁻¹⁰⁷⁴ ერთეულებზე დაფუძნებულ ზუსტ integer accumulator-თან.
- [x] Binary32 გაფართოების CI წარმატებულია: [run 45281284340](https://github.com/maisuradzee/bibmom/actions/runs/45281284340); 66 repository-wide test, NOEMA-005 binary32/binary64 frozen JSON comparison და ყველა workflow ნაბიჯი გაიარა.
- [x] შედეგების JSON და SHA-256 ჩანაწერები მომზადებულია.
- [x] Binary64 + binary32 გაფართოების სრული CI დადასტურდა [run 45281284340](https://github.com/maisuradzee/bibmom/actions/runs/45281284340)-ით; 66 ტესტი, frozen JSON, site build, publication boundary და SignBase audit წარმატებულია.
- [x] ოთხივე ფორმატის CI წარმატებულია: [run 45282263124](https://github.com/maisuradzee/bibmom/actions/runs/45282263124); 72 repository-wide test და frozen JSON reproduction PASS.
- [x] უახლესი სრული CI წარმატებულია: [run 45283388439](https://github.com/maisuradzee/bibmom/actions/runs/45283388439); 74 repository-wide test, ოთხივე ფორმატის frozen JSON reproduction, 8 benchmark format/size შემთხვევა და 44 method measurement, NOEMA-003/HadCRUT5 წყაროთა შემოწმება, SignBase audit, site build და publication boundary PASS.
- [x] runtime/memory benchmark harness და CI smoke test დამატებულია; CI smoke-პროფილი გაიარა.
- [x] სრული benchmark პროფილი: 12 format/size cases, 66 method measurements, 3 input size, 7 timed repetitions; შედეგები და შეზღუდვები დოკუმენტირებულია.
- [ ] სრული პროფილის განმეორება სხვა Python ვერსიაზე/არქიტექტურაზე და რამდენიმე დამოუკიდებელ run-ზე.
- [ ] სხვა runtime/არქიტექტურაზე დამოუკიდებელი გამეორება.
- [ ] დამოუკიდებელი სამეცნიერო და სარედაქციო განხილვა.
- [ ] გამოქვეყნების მზადყოფნის დადასტურება.

## ცვლილებების ისტორია

- 2026-11-24 — sharded reduction-ის 330-case შედეგი ხელახლა დადასტურდა CPython 3.14.4-ზე; იგივე case-matrix SHA-256 დაემთხვა CPython 3.13.5-ის საწყის გაშვებას.
- 2026-11-24 — Python 3.12 docs-ის წყაროს თარიღი დაზუსტდა: 2026-10-26 არის გვერდის last-updated timestamp და არა interpreter release date.
- 2026-11-24 — დაემატა 330-კონფიგურაციანი sharded reduction სიმულაცია; scalar partial-ები შეადარდა Neumaier compensation state-ის გადაცემას. Input SHA-256 და case-matrix SHA-256 გაყინულია JSON-ში.

- 2026-11-24 — წყაროებს დაემატა სრული ციტირება, ავტორები, გამოცემის თარიღი/ვერსია და წვდომის თარიღი; CPython 3.14.4-ის benchmark provenance ოფიციალურ Python.org release record-თან გადამოწმდა.

- 2026-11-23 — შეიქმნა NOEMA-2026-005 დრაფტი; დაემატა გამეორებადი binary64 summation ექსპერიმენტი, ზუსტი Fraction reference, შედეგების JSON და შვიდი ერთეული ტესტი.
- 2026-11-24 — დაემატა 2⁻¹⁰⁷⁴-ზე მასშტაბირებული integer superaccumulator, სამი ახალი unit test და CI-ში გაყინული შედეგის ხელახალი გამოთვლის შემოწმება.
- 2026-11-24 — CI run 45280161907 წარმატებით დასრულდა binary64 ვერსიისთვის: 62 repository-wide test.
- 2026-11-24 — დაემატა binary32 ემულაცია, პირდაპირი ties-to-even ეტალონი, 2 დამატებითი სტრეს-ტესტი და ოთხი ახალი unit test.
- 2026-11-24 — CI run 45281284340 წარმატებით დასრულდა: 66 repository-wide test; binary32/binary64 frozen JSON match, site build, publication boundary და SignBase audit PASS.
- 2026-11-24 — დაემატა decimal64/decimal128 arithmetic emulation, ორი stress case თითო format-ზე, exact integer superaccumulator და ექვსი დამატებითი unit test.
- 2026-11-24 — CI run 45282263124 წარმატებით დასრულდა: 72 repository-wide test; ოთხივე ფორმატის frozen JSON reproduction, NOEMA-003 checks, site build, publication boundary და SignBase audit PASS.
- 2026-11-24 — დაემატა runtime/memory benchmark harness, benchmark protocol, ორი unit test და CI smoke-profile validation; full local performance report ჯერ არ არის დასრულებული.
- 2026-11-24 — decimal integer accumulator ოპტიმიზებულია ადაპტიურ საერთო exponent-ზე; Etiny-grid helper შენარჩუნებულია დამოუკიდებელი ზუსტი reference ტესტისთვის.
- 2026-11-24 — benchmark-ის პირდაპირი CLI გაშვების import path გასწორდა; decimal integer accumulator-ის შედეგის ფორმატირება დასტაბილურდა და provenance აღწერა კოდთან გათანაბრდა.
- 2026-11-24 — CI run 45283388439 წარმატებით დასრულდა: 74 repository-wide test; ოთხივე ფორმატის frozen JSON reproduction, benchmark smoke (8 cases / 44 method measurements), NOEMA-003/HadCRUT5 წყაროთა აუდიტი, SignBase audit და site publication boundary PASS.
- 2026-11-24 — სრული benchmark run 45283854718 წარმატებით დასრულდა: 12 format/size შემთხვევა და 66 method measurement; report-ის არტეფაქტი SHA-256 provenance-ით შენახულია, ხოლო median runtime/peak memory შეჯამებულია ამ დრაფტში.
