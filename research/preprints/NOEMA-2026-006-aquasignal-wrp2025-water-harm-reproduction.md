# NOEMA-2026-006 — AquaSignal: WRP 2025 self-reported drinking-water harm, independent reproduction

- **ID:** AQUASIGNAL-WRP2025-WATER-HARM-REPRO-001
- **სტატუსი:** preliminary
- **თარიღი:** 2026-11-27
- **სფერო:** სასმელი წყლის უსაფრთხოება / გამოკითხვის აგრეგატების გამეორება
- **ავტორი/მომზადების სისტემა:** NOEMA

## საკვლევი კითხვა

შეუძლია თუ არა AquaSignal-ს დამოუკიდებლად გაიმეოროს WRP 2025-ის სასმელ წყალთან დაკავშირებული თვითრეპორტირებული სერიოზული ზიანის 13%-იანი გლობალური მაჩვენებელი გამომცემლის ზუსტი შეწონვისა და დამრგვალების წესით?

## მოკლე შეჯამება

NOEMA-მ LRF-ის საჯარო WRP 2025 Parquet მონაცემთა ნაკრებიდან დამოუკიდებლად გამოთვალა WP22443-ის ექვსი პასუხის კატეგორიის PROJWT-შეწონილი წილები. მონაცემთა ბაზა მოიცავს 143,459 რესპონდენტს 140 ქვეყანაში/ტერიტორიაზე; WP22443-ის არ-null ბაზა 143,459-ია. პირადად განცდილი ზიანის გამომცემლის მაჩვენებელი მიიღება code 1-ის და code 3-ის ცალ-ცალკე დამრგვალებული პროცენტების შეკრებით: 7% + 6% = 13%.

## მტკიცებულებები

**FACT:** WP22443-ის კოდებია 1=პირადად განიცადა, 2=იცნობს ადამიანს, 3=ორივე, 4=არა, 98=არ ვიცი, 99=უარი. გამომცემლის მეთოდის README მიუთითებს, რომ „personally harmed“ მაჩვენებელი არის code 1 და code 3-ის ცალ-ცალკე დამრგვალებული შეწონილი პროცენტების ჯამი.

**REPRODUCED RESULT:** AquaSignal-ის dedicated GitHub Actions workflow-მა 2026-11-27 ჩამოტვირთა pinned Parquet, გადაამოწმა Git blob SHA-1 3e785688e067ded5fdfbe9b50721023ecea87826, ზომა 7,070,416 bytes და SHA-256 07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b. დამოუკიდებელმა დათვლამ მიიღო:
- code 1: 6,280 პასუხი; weighted 7.106988%; half-up rounded 7%;
- code 3: 3,889 პასუხი; weighted 5.850209%; half-up rounded 6%;
- გამომცემლის rounded-sum: 13%;
- ორი დაუმრგვალებელი წილის ჯამი: 12.957198%;
- ყველა ექვსი კატეგორიის weighted წილების ჯამი: 100%.

**INFERENCE:** WRP 2025-ის გლობალური თვითრეპორტირებული harm indicator 13% რიცხვობრივად გამეორდა. ეს არ არის საქართველოს დაბინძურების გავრცელების მაჩვენებელი და არ ადგენს ქიმიურ ან მიკრობიოლოგიურ შესაბამისობას.

## მეთოდი ან ექსპერიმენტის გეგმა

- წყარო: Lloyd's Register Foundation WRP 2025 Wave 4 Parquet, pinned commit f2b810c3c4333de6347ad2c9eade3c48ae17be4c.
- Git blob SHA-1: 3e785688e067ded5fdfbe9b50721023ecea87826; byte length 7,070,416; SHA-256 07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b.
- წონა: PROJWT.
- ცვლადი: WP22443; ყველა არ-null პასუხი რჩება მნიშვნელში, მათ შორის DK/refused.
- კატეგორიები 1, 2, 3, 4, 98 და 99 ცალ-ცალკე დაითვალა.
- გამომცემლის rounding rule: თითოეული კატეგორიის weighted percentage დამრგვალდა half-up წესით; პირადი harm არის rounded code 1 + rounded code 3.
- Parquet ჩამოიტვირთა მხოლოდ ephemeral GitHub Actions runner-ზე; საცავში ინახება მხოლოდ aggregate JSON. Artifact ID 15221271518 შეიცავს მხოლოდ aggregate JSON-ს.

## შედეგები და ინტერპრეტაცია

| WP22443 კატეგორია | ნედლი რაოდენობა | შეწონილი % | გამომცემლის დამრგვალება |
|---|---:|---:|---:|
| პირადად განიცადა (1) | 6,280 | 7.106988% | 7% |
| იცნობს ადამიანს (2) | 9,927 | 9.722437% | 10% |
| ორივე (3) | 3,889 | 5.850209% | 6% |
| არა (4) | 122,178 | 75.817029% | 76% |
| არ ვიცი (98) | 1,087 | 1.362313% | 1% |
| უარი (99) | 98 | 0.141024% | 0% |

გამომცემლის პირადი harm indicator: 7% + 6% = 13%. ეს არ ნიშნავს, რომ გამოკითხულთა 13%-ს წყალში ლაბორატორიულად დადასტურებული დამაბინძურებელი აღმოაჩნდა.

## შეზღუდვები და გაურკვევლობები

- WP22443 არის თვითრეპორტირებული სერიოზული ზიანი ბოლო ორი წლის განმავლობაში და არა ლაბორატორიული წყლის ხარისხის მაჩვენებელი.
- გლობალური შეწონილი მაჩვენებელი საქართველოს გავრცელების მაჩვენებლად არ უნდა იქნას წარმოდგენილი.
- თვითრეპორტირებული ზიანი არ ადგენს კონკრეტულ დამაბინძურებელს, ექსპოზიციის წყაროს ან მიზეზობრივ კავშირს.
- საქართველოსთვის საჭიროა NEA-ს 2021–2025 წლების ჰიდროგეოლოგიური ანგარიში, სადგურებისა და ნიმუშების ლექსიკონი და NFA-ს სასმელი წყლის შესაბამისობის მონაცემთა მნიშვნელი.
- წყარო ლიცენზირებულია CC BY-SA 4.0-ით; raw microdata და რესპონდენტების იდენტიფიკატორები საცავში არ ინახება.

## წყაროები

1. Lloyd's Register Foundation. World Risk Poll 2025: The quiet hazards, 2026. https://www.preventionweb.net/publication/documents-and-publications/world-risk-poll-report-2026-quiet-hazards-how-everyday-risk
2. LRF WRP 2025 Parquet release, pinned commit: https://github.com/lrfoundation/world_risk_poll_data/tree/f2b810c3c4333de6347ad2c9eade3c48ae17be4c
3. WRP 2025 data dictionary: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/WRP_2025/WRP_2025_data_dictionary.csv
4. Publisher reproduction method notes: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/reports/WRP_2025/core_the_quiet_hazards/README.md
5. Publisher reproduction code: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/reports/WRP_2025/core_the_quiet_hazards/reproduce.py

## შემდეგი ნაბიჯები

1. NEA-სგან ოფიციალური RAR ანგარიშის ან ავტორიზებული ალტერნატიული PDF ასლის მიღება, SHA-256 და reuse პირობების შემოწმება.
2. NFA-ს სასმელი წყლის შესაბამისობის რაოდენობებისა და შესაბამისი მნიშვნელების მოპოვება.
3. NEA-ს სადგურებისა და ნიმუშების ID-ების ლექსიკონის შემოწმება.
4. წყაროსა და საბოლოო მოხმარების წერტილში paired sampling-ის დიზაინის მომზადება მხოლოდ შესაბამისი უწყების ნებართვით.
5. დამოუკიდებელი წყლის ხარისხის/ეპიდემიოლოგიური რეცენზია; სტატუსი Published არ მიენიჭოს მის დასრულებამდე.

## შემოწმების სტატუსი

- Dedicated workflow: run 46042747456, job 140654329587 — SUCCESS.
- Aggregate artifact ID 15221271518; ZIP SHA-256 1bbfe95a666eb31930763f487fd1959ab320e43061980b4c8cbae82549be60be; JSON SHA-256 be009bee5bec7a2d2600c7f14a73f16dd1fba27eaba7855b7321d3c35a4bf53f.
- Main Quality CI-ის პირველი მცდელობა მხოლოდ draft-ის პირველი სათაურის ფორმატზე შეჩერდა; corrected record იწყება NOEMA-2026-006 სათაურით და ახალი PR-ში ხელახლა მოწმდება.
- სტატუსი: preliminary; დამოუკიდებელი გარე რეცენზია დასრულებული არ არის.
