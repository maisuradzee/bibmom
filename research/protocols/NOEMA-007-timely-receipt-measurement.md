# NOEMA-2026-007 — გაფრთხილების დროული მიღების ცალკე გაზომვა

- **ID:** NOEMA-2026-007
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** მრავალსაფრთხიანი ადრეული გაფრთხილება, საზოგადოებრივი ჯანმრთელობა და რეაგირების შეფასება
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

როგორ უნდა გაიმიჯნოს გაფრთხილების მიღება და მისი დროული მიღება ისე, რომ survey-ის თვითრეპორტირებული პასუხები, endpoint-ის მიწოდების დადასტურება და რეალური დამცავი მოქმედება ერთმანეთში არ აირიოს?

## მოკლე შეჯამება

NOEMA-007-ის action-readiness კონტრაქტს დაემატა არჩევითი, უკუთავსებადი timely-receipt ველი. ის ითვლის მხოლოდ იმ რესპონდენტებს, რომლებიც აცხადებენ, რომ გაფრთხილება მიიღეს და ცალკე აფასებენ, მოვიდა თუ არა ის წინასწარ განსაზღვრულ მინიმალურ დროში მოქმედების deadline-მდე. ეს მაჩვენებელი self-reported რჩება; endpoint receipt-ები და raw device logs არ გამოიყენება.

## არსებული ცოდნა და წყაროები

UNDRR/IFRC/ITU/WMO-ის 2026 AER მეთოდოლოგია აფასებს მონიტორინგს, პროგნოზს, გაფრთხილების გავრცელებას, კომუნიკაციას/კოორდინაციასა და დროულ/შესაბამის რეაგირებას. იგი learning-oriented, non-punitive მიმოხილვის ჩარჩოა.

WMO/UNDRR-ის 2026 MHEWS ანგარიში ცალ-ცალკე აღწერს ქვეყნის დონეზე სისტემის ოთხ საყრდენს და მიუთითებს, რომ შემდგომი ეტაპი ეფექტიანობისა და გაფრთხილებიდან მოქმედებამდე პროცესის გაზომვაა. ქვეყნის შესაძლებლობა არ უდრის ინდივიდუალური შეტყობინების დროულ მიღებას.

## მტკიცებულებები

- **FACT:** AER-ის ოფიციალური მეთოდოლოგია განიხილავს დაკვირვებას/პროგნოზს, გაფრთხილების გავრცელებას, კომუნიკაციას/კოორდინაციასა და რეაგირებას.
- **FACT:** WMO/UNDRR-ის 2026 ანგარიშის საჯარო გვერდი აღნიშნავს, რომ MHEWS-ის შესაძლებლობების შეფასებასთან ერთად საჭიროა ეფექტიანობის, ქცევითი პასუხისა და დამცავი მოქმედების გაზომვა, სადაც მონაცემები არსებობს.
- **INFERENCE:** მხოლოდ "მიიღო თუ არა" კითხვამ შეიძლება გამოტოვოს, რომ შეტყობინება ძალიან გვიან მივიდა და რეაგირების დრო აღარ დარჩა.
- **HYPOTHESIS:** event-specific minimum lead-time წესით გაზომილი timely receipt უფრო გამოსადეგია action-readiness შეფასებისთვის, ვიდრე receipt-ის ერთადერთი მაჩვენებელი.
- **UNTESTED IDEA:** შემდგომში შეიძლება შეიქმნას სხვადასხვა საფრთხისთვის წინასწარ დამტკიცებული minimum lead-time profiles; ეს მოითხოვს პასუხისმგებელი უწყების hazard-specific playbook-ს და არ უნდა განისაზღვროს NOEMA-ს მიერ.

## კონკურენტი ახსნები

- დაგვიანება შეიძლება გამოწვეული იყოს გაფრთხილების გამოცემით, არხით, ქსელით, მოწყობილობით ან რესპონდენტის გახსენების შეცდომით.
- მოქმედების დაგვიანება შეიძლება განპირობებული იყოს ტრანსპორტის, თავშესაფრის, ფინანსების, შეზღუდული შესაძლებლობის ან ინსტიტუციური კოორდინაციის ბარიერებით და არა მხოლოდ შეტყობინების დროთი.
- სხვადასხვა საფრთხესა და მოქმედებას განსხვავებული lead time სჭირდება; უნივერსალური ზღვარი დაუშვებელია.

## ჰიპოთეზა

თუ survey წინასწარ განსაზღვრავს event-specific action deadline-სა და მინიმალურ lead time-ს, ხოლო timely receipt-ს ცალკე denominator-ით ითვლის მხოლოდ იმ რესპონდენტებში, რომლებმაც გაფრთხილების მიღება განაცხადეს და დროის შეფასება შეძლეს, მაშინ receipt-ისა და action readiness-ის განსხვავება უფრო გამჭვირვალე გახდება.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Survey-ში არჩევითად დაემატა ოთხი ველი: timing assessment count, timely receipt count, minimum lead seconds და measurement basis.
2. timing assessment count ვერ გადააჭარბებს self-reported receipt count-ს; timely receipt count ვერ გადააჭარბებს timing assessment count-ს.
3. ყველა ოთხი ველი ერთად უნდა იყოს წარმოდგენილი; ნაწილობრივი ჩანაწერი უარყოფილია.
4. minimum lead time არის არაუარყოფითი მთელი წამები და განისაზღვრება კონკრეტული event-ის action deadline-მდე.
5. basis ამ ეტაპზე მხოლოდ respondent_recall-ია. Endpoint logs ცალკე ერთეულად რჩება; პიროვნებასთან დაკავშირებული device logs არ ინახება.
6. ძველი schema-v1 survey ჩანაწერები timing ველების გარეშე კვლავ ვალიდურია; ასეთ ჩანაწერში timely receipt არის null და არა ნული.
7. სინთეზური ტესტები ამოწმებს denominator-ებს, ზღვარს, ნაწილობრივ ველებსა და zero-denominator ქცევას.

## შედეგები და ინტერპრეტაცია

ეს ცვლილება ზომავს დამატებით survey outcome-ს, მაგრამ არ ამტკიცებს, რომ საქართველოში გაფრთხილება დაგვიანებულია ან რომ ახალი ველი რეალურ ქცევას გააუმჯობესებს. საველე მონაცემი და უფლებამოსილი event-review ჯერ არ არსებობს.

## შეზღუდვები და გაურკვევლობები

- respondent recall შეიძლება იყოს არაზუსტი და susceptible იყოს recall bias-ს.
- survey denominator არ უდრის event population-ს, თუ probability design, response/nonresponse და weighting არ არის განსაზღვრული.
- self-reported timely receipt არ არის timestamp-ით დადასტურებული receipt.
- minimum lead time უნდა დაამტკიცოს პასუხისმგებელმა უწყებამ კონკრეტული საფრთხისა და action playbook-ის მიხედვით.
- არ ჩატარებულა საველე პილოტი, causal evaluation ან საქართველოს alert-delivery მონაცემების ანალიზი.

## დასკვნა

NOEMA-007 ახლა ცალკე გამოყოფს timely receipt-ს, receipt-ს, comprehension-ს, feasibility-სა და action-ს. ეს აუმჯობესებს გაზომვის დიზაინს, მაგრამ არ ქმნის ოფიციალურ გაფრთხილების არხს და არ ცვლის სახელმწიფო უწყების პასუხისმგებლობას.

## წყაროები

1. UNDRR, IFRC, ITU & WMO. *After-Event Review (AER): Methodological guidance on conducting after-event reviews of Early Warning Systems*. 2026. https://www.undrr.org/publication/documents-and-publications/after-event-review-aer-methodological-guidance-conducting
2. WMO. *Global Status of Multi-Hazard Early Warning Systems 2026*. 2026-11-11. https://wmo.int/resources/publication-series/global-status-multi-hazard-early-warning-systems/gsmhews-2026
3. UNDRR. *Global Status of Multi-Hazard Early Warning Systems 2026*. 2026. https://www.undrr.org/reports/global-status-mhews-2026

## შემდეგი ნაბიჯები

1. უფლებამოსილი უწყების მიერ hazard-specific action deadline და minimum lead-time წესის დამტკიცება.
2. Survey instrument-ის cognitive testing და accessibility review.
3. მხოლოდ უფლებამოსილი, privacy-reviewed event aggregate-ებით პილოტის წინასწარი რეგისტრაცია.
4. Receipt, timely receipt, comprehension, feasibility და action ცალ-ცალკე denominator-ებით გამოქვეყნება.

## შემოწმების სტატუსი

- AER და MHEWS 2026 ოფიციალური წყაროები გახსნილია; მეთოდოლოგიური ინტერპრეტაცია წყაროების აღწერას შეესაბამება.
- ცვლილება არის schema/validator/protocol extension; რეალური event data არ გამოიყენება.
- Survey timing არის self-reported და არა device-log verified.
- სტატუსი რჩება Draft; დამოუკიდებელი DRR, survey-methodology, accessibility და privacy review საჭიროა.
