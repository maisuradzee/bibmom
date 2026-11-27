# AquaSignal — WRP 2025 self-reported drinking-water harm reproduction protocol

- **ID:** AQUASIGNAL-WRP2025-WATER-HARM-REPRO-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** სასმელი წყლის უსაფრთხოება / გამოკითხვის აგრეგატების გამეორება

## საკვლევი კითხვა

შეუძლია თუ არა AquaSignal-ს დამოუკიდებლად გაიმეოროს WRP 2025-ის სასმელ წყალთან დაკავშირებული თვითრეპორტირებული სერიოზული ზიანის 13%-იანი გლობალური მაჩვენებელი გამომცემლის ზუსტი შეწონვისა და დამრგვალების წესით?

## მოკლე შეჯამება

გამომცემლის 2026 წლის ანგარიში ამბობს, რომ სასმელი წყლით გამოწვეული სერიოზული ზიანის თვითრეპორტირებული მაჩვენებელი 13%-ია. გამომცემლის reproduction README განმარტავს, რომ ეს რიცხვი მიიღება WP22443-ის კოდების 1 და 3 ცალ-ცალკე დამრგვალებული შეწონილი პროცენტების შეკრებით. ეს არის გამოკითხვის შედეგი და არა ლაბორატორიულად დადასტურებული წყლის დაბინძურება.

## მტკიცებულებები

**FACT:** WRP 2025 მონაცემთა ლექსიკონი WP22443-ს განსაზღვრავს როგორც სასმელი წყლით ბოლო ორი წლის განმავლობაში სერიოზული ზიანის გამოცდილებას; კოდებია 1=პირადად, 2=ვიცნობ ადამიანს, 3=ორივე, 4=არა, 98=არ ვიცი, 99=უარი.

**FACT:** გამომცემლის reproduction README ამბობს, რომ „personally experienced“ შედეგი არის code 1 და code 3-ის ცალ-ცალკე დამრგვალებული პროცენტების ჯამი და იყენებს half-up დამრგვალებას.

**HYPOTHESIS:** ამ წესის დამოუკიდებელი გამეორება და წყაროს hash-ებით მიბმა გააძლიერებს AquaSignal-ის გლობალური survey baseline-ის სანდოობას, მაგრამ ვერ ჩაანაცვლებს საქართველოს ლაბორატორიულ მონიტორინგს.

## მეთოდი ან ექსპერიმენტის გეგმა

- მონაცემთა წყარო: LRF WRP 2025 Wave 4 Parquet, pinned commit f2b810c3c4333de6347ad2c9eade3c48ae17be4c.
- Git blob SHA-1: 3e785688e067ded5fdfbe9b50721023ecea87826.
- მოსალოდნელი ზომა: 7,070,416 bytes; წყაროს SHA-256: 07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b.
- წონა: PROJWT.
- ცვლადი: WP22443; ყველა არ-null პასუხი რჩება მნიშვნელში, მათ შორის DK/refused.
- code 1 და code 3 შეწონილი პროცენტები ცალ-ცალკე დამრგვალდება half-up წესით, შემდეგ შეიკრიბება.
- Parquet ჩამოიტვირთება მხოლოდ ephemeral GitHub Actions runner-ზე; საცავში ჩაიწერება მხოლოდ aggregate JSON.

## შედეგები და ინტერპრეტაცია

შედეგები დაემატება მხოლოდ მას შემდეგ, რაც dedicated workflow დაადასტურებს source hash-ს, კითხვით ბაზას და გამომცემლის 13%-იან rounded-sum წესს.

## შეზღუდვები და გაურკვევლობები

- WP22443 არის თვითრეპორტირებული სერიოზული ზიანი ბოლო ორი წლის განმავლობაში და არა წყლის ლაბორატორიული ანალიზი.
- გლობალური შეწონილი მაჩვენებელი საქართველოს გავრცელების მაჩვენებლად არ უნდა იქნას წარმოდგენილი.
- საქართველოსთვის საჭიროა NEA-ს მიწისქვეშა წყლების ანგარიში, სადგურების/ნიმუშების ლექსიკონი და NFA-ს შესაბამისობის მონაცემთა მნიშვნელი.

## წყაროები

1. Lloyd's Register Foundation. World Risk Poll 2025: The quiet hazards, 2026. https://www.preventionweb.net/publication/documents-and-publications/world-risk-poll-report-2026-quiet-hazards-how-everyday-risk
2. LRF WRP 2025 Parquet release, pinned commit: https://github.com/lrfoundation/world_risk_poll_data/tree/f2b810c3c4333de6347ad2c9eade3c48ae17be4c
3. WRP 2025 data dictionary: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/WRP_2025/WRP_2025_data_dictionary.csv
4. Publisher reproduction method notes: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/reports/WRP_2025/core_the_quiet_hazards/README.md
5. Publisher reproduction code: https://github.com/lrfoundation/world_risk_poll_data/blob/f2b810c3c4333de6347ad2c9eade3c48ae17be4c/reports/WRP_2025/core_the_quiet_hazards/reproduce.py

## შემდეგი ნაბიჯები

1. Run the pinned Parquet calculation and freeze only aggregate output.
2. Obtain the NEA 2021–2025 hydrogeological report and station/sample dictionary through an authorised transfer route.
3. Obtain NFA drinking-water compliance counts and denominator definitions.
4. Keep self-reported harm separate from microbiological/chemical contamination evidence.

## შემოწმების სტატუსი

Protocol only. The 13% aggregate has not yet been independently reproduced by AquaSignal in this branch.
