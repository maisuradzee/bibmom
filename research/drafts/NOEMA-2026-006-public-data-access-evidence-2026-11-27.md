# NOEMA-2026-006 — AquaSignal — საჯარო მონაცემთა წვდომის მტკიცებულების დონეები

- **ID:** NOEMA-2026-006
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** წყლის მონიტორინგი · მონაცემთა წარმომავლობა · საჯარო ინფორმაციის წვდომა
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

როგორ უნდა განასხვაოს AquaSignal-მა საჯარო კატალოგში მონაცემთა ჩანაწერის არსებობა რეალური payload-ის ჩამოტვირთვისგან, schema/data dictionary-ის შემოწმებისგან, reuse უფლებისგან და sample-level მონაცემის კანონიერად დამუშავების შესაძლებლობისგან?

## მიგნებები და მტკიცებულების სტატუსი

### FACT — NEA122 კატალოგის ჩანაწერი

MEPA-ს ოფიციალური სივრცითი მონაცემების კატალოგში NEA122 აღწერილია როგორც მიწისქვეშა მტკნარი სასმელი წყლების მონიტორინგის წერტილების point layer. ჩანაწერში გაზიარების ტიპი მითითებულია როგორც „საჯარო“, ღირებულება — „უფასო“, ტექნიკური layer — Groundwtaer_Monitoring_Stations_NEA, ხოლო საბოლოო პროდუქტის განთავსების URL ცარიელია; შენახვის ადგილი აღწერილია როგორც SQL SDE სერვერი და პერსონალური კომპიუტერი. კატალოგის ჩანაწერის თარიღია 2026-03-06.

წყარო: https://portal.mepa.gov.ge/En/User/data?Links-sort=ResponsiblePerson-asc

### FACT — 2021–2025 ანგარიშის განცხადება

NEA-მ 2026-11-26 გამოაცხადა 2021–2025 წლების მიწისქვეშა წყლების მონიტორინგის ანგარიში და ნიტრატების რისკის საველე მეთოდოლოგია, დააკავშირა RAR არქივი. ამ ციკლში ვებ-კლიენტმა application/octet-stream არქივის გახსნა ვერ დაამუშავა. ეს მხოლოდ გამოყენებული retrieval path-ის შეზღუდვაა; იგი არ ამტკიცებს, რომ არქივი საჯაროდ მიუწვდომელია ან დაზიანებულია.

წყარო: https://nea.gov.ge/ajs/News/3461

## მთავარი დასკვნა

**INFERENCE:** კატალოგში public/free კლასიფიკაცია თავისთავად არ ამტკიცებს:
- ჩამოსატვირთ payload-ს ან მოქმედ public API-ს;
- schema/data dictionary-ის ხელმისაწვდომობას;
- sample-level ლაბორატორიულ შედეგებს;
- ღია მონაცემთა ლიცენზიას ან კომერციული/მეორადი გამოყენების უფლებას;
- კონკრეტული სადგურის აქტიურობას ან გაზომვის პერიოდულობას.

NEA122 არის სადგურების სივრცითი კატალოგის ჩანაწერი და არა წყლის ხარისხის ნიმუშების დროითი სერია. სადგურის წერტილის layer-იდან არ უნდა შეიქმნას ხელოვნური sample/result feed.

## ინოვაციური გადაწყვეტა — fail-closed access evidence state machine

დაემატა noema_core/source_access_evidence.py და source-access-evidence JSON Schema. თითოეული წყარო იღებს ცალკე მტკიცებულების ველებს: კატალოგის ხილვადობა/ფასი, payload-ის მიღება და SHA-256, schema/data dictionary-ის დათვალიერება და SHA-256, reuse terms, sample-level მონაცემის არსებობა და წერილობითი ავტორიზაცია.

მდგომარეობები პროგრესირებს მხოლოდ შესაბამისი მტკიცებულების არსებობისას: CATALOG_METADATA_ONLY, PAYLOAD_RETRIEVED_SCHEMA_UNINSPECTED, REUSE_UNVERIFIED, NO_SAMPLE_LEVEL_DATA, AUTHORIZATION_REQUIRED და CONTROLLED_INGESTION_ELIGIBLE. restricted პირობები ყოველთვის იძლევა BLOCKED_RESTRICTED შედეგს.

## მეთოდი ან ექსპერიმენტის გეგმა

- ოფიციალური MEPA spatial catalogue-ის NEA122 ჩანაწერის დოკუმენტური შემოწმება.
- NEA-ს 2026-11-26 განცხადებისა და RAR ბმულის არსებობის შემოწმება; არქივის შიგთავსი არ ჩაითვალა შემოწმებულად.
- დახურული JSON Schema და დეტერმინისტული Python state validator.
- სინთეზური ტესტები: public/free vs payload, hash-ის სავალდებულოობა, schema-ის მიმდევრობა, reuse evidence, authorization, duplicate source IDs და HTTPS წყაროები.
- არანაირი HTTP retrieval ან მონაცემთა ingestion არ სრულდება ამ მოდულით.

## შეზღუდვები და გაურკვევლობები

- არც NEA122-ის payload ჩამოგვიტვირთავს და არც მისი schema დაგვითვალიერებია.
- RAR არქივის შიგთავსი, ზომა, შიდა ფაილები და reuse პირობები უცნობია.
- არ შეგროვებულა სადგურის კოორდინატები, ჭაბურღილის მფლობელის/ოჯახის მონაცემები ან sample-level შედეგები.
- ეს მოდული არ აკეთებს HTTP retrieval-ს, ლიცენზიის იურიდიულ ინტერპრეტაციას ან მონაცემთა ingestion-ს.
- CONTROLLED_INGESTION_ELIGIBLE მხოლოდ წინაპირობების ვალიდაციის შედეგია; იგი არ ანიჭებს სამართლებრივ უფლებას და არ იწყებს იმპორტს.

## შემდეგი ნაბიჯები

NEA-სგან მოითხოვოს NEA122-ის ექსპორტის/სერვისის URL, data dictionary, CRS, აქტიური/არააქტიური სადგურის სტატუსი, განახლების cadence და reuse პირობები; RAR-ისთვის გამოიყენოს ოფიციალური ალტერნატიული ჩამოტვირთვის არხი და შიგთავსის SHA-256/ფაილების ინვენტარი მხოლოდ მიღების შემდეგ. NFA-ს სასმელი წყლის შესაბამისობის მონაცემები დარჩეს ცალკე წყაროდ.

## შემოწმების სტატუსი

- FACT წყაროები: ოფიციალური MEPA კატალოგი და NEA განცხადება.
- REPRODUCED RESULT: სინთეზური unit tests უნდა შესრულდეს exact-head CI-ში.
- INFERENCE: public/free catalogue metadata არ უდრის sample-level feed-ს ან reuse licence-ს.
- გარე წყლის ხარისხის/სტატისტიკური რეცენზია არ ჩატარებულა; Draft სტატუსი შენარჩუნებულია.

## წყაროები

- National Environmental Agency of Georgia. (2026-03-06 catalogue record). NEA122 groundwater monitoring spatial-data record. https://portal.mepa.gov.ge/En/User/data?Links-sort=ResponsiblePerson-asc
- National Environmental Agency of Georgia. (2026-11-26). 2021–2025 groundwater monitoring report and nitrate-risk field methodology announcement. https://nea.gov.ge/ajs/News/3461
