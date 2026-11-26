# NOEMA-2026-007 — EW4All measurement crosswalk: from warning reach to verified action

- **ID:** NOEMA-2026-007
- **სტატუსი:** draft / discovery and measurement design
- **თარიღი:** 2026-11-27
- **სფერო:** კატასტროფის რისკის შემცირება · ადრეული გაფრთხილება · საზოგადოებრივი უსაფრთხოება · მონაცემთა მეთოდოლოგია
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

როგორ უნდა გაიზომოს ადრეული გაფრთხილების სრული ჯაჭვი ისე, რომ ტექნიკური მიწოდება, ადამიანის მიერ მიღება, დროულობა, გაგება, მოქმედების შესაძლებლობა, რეალური მოქმედება და ადამიანზე საბოლოო გავლენა ერთმანეთში არ აგვერიოს?

## მოკლე შეჯამება

NOEMA-007-ის არსებული aggregate-only პროტოტიპი უკვე ცალკე ითვლის channel endpoint confirmation-ს, survey-based warning receipt-ს, comprehension-ს, action feasibility-ს, self-reported action-ს და verified action-ს. ახალი გადამოწმება ამ მეტრიკებს აკავშირებს WMO-ს 2024 წლის Early Warnings for All Monitoring & Evaluation Toolkit-ის ოფიციალურ ინდიკატორებთან.

მთავარი მიგნებაა, რომ არსებული პროტოტიპი სწორად ინარჩუნებს რამდენიმე განსხვავებულ denominator-ს, მაგრამ ჯერ არ ფარავს ოფიციალური ჩარჩოს ყველა მოთხოვნას: არ ზომავს ადამიანების უნიკალურ მოსახლეობრივ დაფარვას, receipt-ის დროულობას, warning-event-ების რაოდენობას, ადრეული მოქმედების საბაზისო პერიოდს, წინასწარ შეთანხმებულ დაფინანსებას ან ევაკუაციისთვის exposed-population denominator-ს.

შედეგად შეიქმნა მანქანურად წაკითხვადი crosswalk, მკაცრი JSON Schema და ტესტები. ეს არის კვლევითი/საინჟინრო სპეციფიკაცია და არა ახალი ოპერაციული alerting ან მონაცემთა შეგროვების სისტემა.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

ადრეული გაფრთხილება ვერ ჩაითვლება წარმატებულად მხოლოდ იმიტომ, რომ შეტყობინება გაიგზავნა ან ტექნიკურმა არხმა მისი მიწოდება დაადასტურა. WMO-ს toolkit ადამიანზე ორიენტირებულ, end-to-end მიდგომას მოითხოვს და ცალ-ცალკე აღწერს გაფრთხილების გავრცელებასა და preparedness/response შედეგებს.

UNDRR-ის 2026 წლის COP31 განახლება ციტირებს WMO-ს გენერალური მდივნის განცხადებას, რომ ბოლო ხუთ წელიწადში კატასტროფით დაზარალებულთა ხუთიდან ოთხმა წინასწარი გაფრთხილება მიიღო, თუმცა მესამედმა გაფრთხილების მიღების შემდეგ მოქმედება ვერ შეძლო. ეს მაღალი ღირებულების discovery signal-ია, მაგრამ სტატიის გვერდზე არ არის მითითებული ამ მტკიცების საწყისი survey/dataset, sample frame, weighting ან uncertainty interval. ამიტომ NOEMA ამ რიცხვებს baseline-ად არ იყენებს.

## არსებული ცოდნა და წყაროები

### 1. WMO Early Warnings for All M&E Toolkit (August 2024)

Toolkit-ის მიზანია ერთდროულად გაზომოს გლობალური დაფარვა და გაფრთხილებიდან ადრეულ მოქმედებამდე ეფექტიანობა. ოთხი pillar მოიცავს risk knowledge-ს, detection/forecasting-ს, warning dissemination-ს და preparedness/response-ს.

ამ კვლევისთვის განსაკუთრებით მნიშვნელოვანია:
- **G-3:** მოსახლეობის რაოდენობა ყოველ 100,000 ადამიანზე, რომელიც ადგილობრივი ან ეროვნული გავრცელების მექანიზმებით early-warning ინფორმაციას ფარავს;
- **3.2.1b:** last-mile stakeholder groups-ის მიერ დროული და გასაგები გაფრთხილების მიღების დადასტურება, რომელმაც მათ მოქმედების საშუალება მისცა;
- **4.2:** ადრეულ მოქმედებამდე მიმყვანი გაფრთხილებების რაოდენობის პროცენტული ზრდა;
- **4.3.1:** anticipatory-action-ისთვის წინასწარ შეთანხმებული დაფინანსების მოცულობა;
- **4.4:** გაფრთხილებების, დაფინანსებისა და anticipatory-action-ის feasibility/effectiveness-ის მონიტორინგი;
- **G-6:** გაფრთხილების შემდეგ წინმსწრები ევაკუაციით დაცული რისკის ქვეშ მყოფი მოსახლეობის წილი.

### 2. IFRC report (2025)

IFRC-ის ანგარიში წერს, რომ 2024 წელს 66 ქვეყანას ჰქონდა ადრეულ გაფრთხილებაზე მოქმედების ადგილობრივი გეგმა. ამავე დროს, ანგარიშის შენიშვნით, Sendai Framework Monitor არ აკონკრეტებს, ეს გეგმები დაკავშირებულია anticipatory action-თან თუ preparedness/rapid response-თან, და არის თუ არა ისინი ოპერაციულად მოქმედი. ანგარიში ეფუძნება ლიტერატურას, 18 მთავრობის ნიმუშს და 47 key informant interview-ს; თვითონვე აღნიშნავს, რომ ეს გლობალური შეფასება ამომწურავი არ არის.

### 3. UNDRR COP31 update (12 November 2026)

გვერდი აღწერს გლობალურ პროგრესს და ციტირებს WMO-სა და IFRC-ის ხელმძღვანელების განცხადებებს. განსაკუთრებით საყურადღებოა მიღებასა და მოქმედებას შორის სხვაობა. თუმცა 4/5 და 1/3 პროპორციების მეთოდოლოგია ამ კონკრეტულ გვერდზე მოცემული არ არის. ისინი მხოლოდ source-reported statements-ად ინახება და რაოდენობრივ გამოთვლაში არ გამოიყენება.

## მტკიცებულებები

### FACT — ოფიციალური ჩარჩოს მოთხოვნები

- WMO toolkit განსაზღვრავს G-3 მოსახლეობრივ დაფარვას და G-6 წინმსწრები ევაკუაციით დაცულ რისკის ქვეშ მყოფ მოსახლეობას.
- WMO toolkit-ის 3.2.1b ინდიკატორი ითხოვს last-mile stakeholder feedback-ს დროულ, გასაგებ გაფრთხილებასა და მოქმედების შესაძლებლობაზე.
- Toolkit-ის 4.2 და 4.3.1 ინდიკატორები განასხვავებს early-action შედეგს და მისთვის წინასწარ შეთანხმებულ დაფინანსებას.
- IFRC-ის 2025 წლის ანგარიში აღწერს 66 ქვეყანას ადგილობრივი მოქმედების გეგმებით და მიუთითებს, რომ მათი ოპერაციულობა/anticipatory-action-თან კავშირი ცალკე დასადგენია.

### FACT — არსებული NOEMA პროტოტიპის ველები

- channels[].attempted_endpoints და channels[].confirmed_endpoints ზომავს endpoint-ებს და არა უნიკალურ ადამიანებს.
- survey.received_warning_n, comprehension_assessed_n და comprehension_correct_n ზომავს survey respondent-ების ეტაპებს.
- action_feasibility_assessed_n და action_feasible_n ზომავს შეფასებულ რესპონდენტებში მოქმედების განხორციელებადობას.
- protective_action_reported_n და protective_action_verified_n განასხვავებს თვითრეპორტირებულ და შემოწმებულ მოქმედებას.

### REPRODUCED RESULT

data/noema-007/ew4all-measurement-crosswalk-2026-11-27.json-ში შენახული crosswalk მოწმდება Draft 2020-12 JSON Schema-ით და regression tests-ით. ტესტები ამოწმებს ინდიკატორების უნიკალურობას, denominator metadata-ს, source linkage-ს და იმას, რომ მეთოდოლოგიურად დაუდასტურებელი 4/5 და 1/3 statements არ გამოიყენება quantitative baseline-ად.

### INFERENCE

- ტექნიკური endpoint delivery ვერ ჩაანაცვლებს population coverage-ს.
- respondent-ის მიერ warning receipt ვერ ადასტურებს დროულობას ან გაგებას.
- ცალკე receipt/comprehension/action marginal rates ვერ გამრავლდება joint success rate-ის მისაღებად, თუ ერთსა და იმავე respondent cohort-ზე ერთობლივი განაწილება ცნობილი არ არის.
- action feasibility და action completion სხვადასხვა შედეგია; არცერთი მათგანი ავტომატურად არ ადასტურებს avoided loss-ს.

## კონკურენტი ახსნები

- გაფრთხილების მიღების შემდეგ მოქმედების არქონა შეიძლება გამოწვეული იყოს არა კომუნიკაციის ხარვეზით, არამედ ტრანსპორტის, ფულის, თავშესაფრის, ჯანმრთელობის, ზრუნვის ვალდებულებების, ნდობის ან ადგილობრივი გეგმის არარსებობით.
- ერთსა და იმავე ტერიტორიაზე სხვადასხვა არხის endpoint-ები შეიძლება ერთსა და იმავე ადამიანს ეკუთვნოდეს; მათი ჯამი ადამიანების რაოდენობა არ არის.
- survey-ის non-response, convenience sampling და recall bias შეიძლება შეცვლიდეს receipt/comprehension/action rates-ს.
- warning-event-ების რაოდენობის ზრდა შეიძლება ასახავდეს hazard frequency-ს ან threshold-ის ცვლილებას და არა უკეთეს მოქმედებას.

## ჰიპოთეზა

თუ თითოეული ეტაპი გაზომილი იქნება წინასწარ განსაზღვრული ერთეულით, denominator-ით, დროითი საზღვრითა და provenance-ით, მაშინ NOEMA-007 შეძლებს გამოავლინოს, სად წყდება warning-to-action ჯაჭვი ისე, რომ ტექნიკური delivery არ გამოცხადდეს ადამიანურ დაცვად და descriptive metrics არ გასაღდეს causal impact-ად.

ეს ჰიპოთეზა ჯერ არ შემოწმებულა რეალურ ადგილობრივ მონაცემებზე.

## შემოწმების მეთოდი

1. WMO toolkit-ის ოფიციალური G-3, G-4.2, G-6, 3.2.1b, 4.3.1 და 4.4 ინდიკატორების ამოღება და ზუსტი ერთეულების შენარჩუნება.
2. თითოეული ოფიციალური ინდიკატორის შეჯერება NOEMA-007-ის მიმდინარე schema-ს ველებთან.
3. თითოეულ mapping-ზე დაფიქსირება: alignment, missing evidence, denominator unit, proposed measurement და interpretation boundary.
4. Crosswalk-ის JSON Schema validation და regression tests.
5. რეალური მონაცემის შეგროვებამდე privacy review, survey sampling plan, non-response strategy, event eligibility rules და local authority permission.
6. ნებისმიერი შემდგომი pilot-ისთვის წინასწარ განსაზღვრა baseline/follow-up, hazard mix, geographic scope, measurement window და independent verification procedure.

## შედეგები და ინტერპრეტაცია

Crosswalk-მა გამოავლინა ექვსი განსხვავებული შესაბამისობა:
- G-3 — მიმდინარე endpoint/survey fields არ არის მოსახლეობრივი დაფარვის ეკვივალენტი;
- 3.2.1b — ნაწილობრივი შესაბამისობა, მაგრამ დროული მიღება და ერთობლივი respondent-level outcome ჯერ აკლია;
- 4.2 — respondent-level action counts არ არის warning-event-level early-action rate;
- 4.3.1 — financing metadata საერთოდ არ არსებობს;
- G-6 — evacuation-specific denominator და verification არ არსებობს;
- 4.4 — feasibility-ის ნაწილი არსებობს, მაგრამ plan/finance/activation/after-action lineage აკლია.

ეს არის მეთოდოლოგიური gap analysis და არა ადგილობრივი ეფექტიანობის შეფასება. საქართველოში warning-to-action performance-ის გაზომვისთვის კვლავ საჭიროა უფლებამოსილი warning/after-action aggregate მონაცემები და დამოუკიდებელი privacy review.

## შეზღუდვები და გაურკვევლობები

- არცერთი ადგილობრივი warning event, survey, endpoint log ან personal record არ გამოგვიყენებია.
- UNDRR-ის 4/5 და 1/3 განცხადების საწყისი dataset ამ run-ში ვერ დადგინდა; ეს ციფრები baseline-ად არ გამოიყენება.
- IFRC-ის 66-country finding ანგარიშში source-reported შედეგია და არა NOEMA-ს მიერ ხელახლა დათვლილი გლობალური მონაცემი.
- WMO toolkit ინდიკატორების crosswalk არ ადასტურებს, რომ საქართველოს შესაბამის უწყებებს ამ მონაცემების შეგროვება შეუძლიათ ან მათ ხელახალი გამოყენების ნებართვა არსებობს.
- მიმდინარე NOEMA-007 small-cell rule და release gate არ წარმოადგენს Differential Privacy-ს ან სრულ disclosure-control სისტემას.
- Verified action არ არის causal impact; avoided loss-ის შეფასებას ცალკე კვლევითი დიზაინი სჭირდება.

## დასკვნა

NOEMA-007-ის შემდეგი ღირებული ნაბიჯი არ არის ახალი alerting channel-ის შექმნა. ეს არის measurement integrity: ადამიანების, endpoint-ების, warning events-ის, ადგილობრივი გეგმების, ფინანსებისა და exposed population-ის ერთმანეთისგან გამიჯვნა. ახალი crosswalk ქმნის შემოწმებად საფუძველს, რომ მომავალი pilot-ის შედეგები შედარებადი და ინტერპრეტირებადი იყოს.

## წყაროები

1. World Meteorological Organization and Early Warnings for All partners. *Early Warnings for All: Toolkit for Monitoring & Evaluation*, v1.0, August 2024. https://wmo.int/sites/default/files/2024-09/EW4ALL%20ME%20Toolkit_Final%20Version%201_August2024.pdf
2. International Federation of Red Cross and Red Crescent Societies. *Strengthening National Disaster Risk Management Systems through the Integration of Anticipatory Action*, 2025. https://www.ifrc.org/sites/default/files/2025-09/Strengthening_National_Disaster_Risk_Management_Systems_through_integration_of_anticipatory_action.pdf
3. United Nations Office for Disaster Risk Reduction. *COP31 leaders back a long-term future for Early Warnings for All*, 12 November 2026. https://www.undrr.org/news/cop31-leaders-back-long-term-future-early-warnings-all
4. UNDRR, ITU and UNITAR. *Monitoring & Evaluation of Early Warning for All*, 8 August 2025. https://www.undrr.org/resource/training-course/monitoring-evaluation-early-warning-all

## ცვლილებების ისტორია

- 2026-11-27 — პირველი machine-readable EW4All indicator crosswalk, evidence boundary და denominator-separation tests.
