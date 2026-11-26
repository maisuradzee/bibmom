# NOEMA-INFRA-001 — executable high-water compare-and-advance reference model

- **ID:** NOEMA-INFRA-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** research-platform reliability · backup provenance · recovery security
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

შეიძლება თუ არა high-water generation-ის compare-and-advance კონტრაქტის მცირე executable reference model-ით შემოწმება ისე, რომ concurrent writers, stale expected state, rollback, equivocation და ambiguous-commit retry მკაფიოდ გაიმიჯნოს?

## მოკლე შეჯამება

NOEMA-ს არსებული backup manifest validator ამოწმებს ზუსტ manifest bytes-ს, caller-supplied trusted Ed25519 key-სა და ადგილობრივ artifact digest/length-ს. ეს თავისთავად არ ადასტურებს, რომ ხელმოწერილი backup უახლესია. PR #85-ში აღწერილი provider-neutral high-water protocol ამ ხარვეზს გამოყოფს, მაგრამ ჯერჯერობით დიზაინის დოკუმენტია.

ამ ჩანაწერში ემატება **SQLite-ზე დაფუძნებული executable reference model**. ის იყენებს `BEGIN IMMEDIATE`-ს ერთ ფაილურ ბაზაში writers-ის სერიალიზაციისთვის და ამოწმებს generation-ის ერთსაფეხურიან ზრდას, წინა manifest digest-ის მიბმას, stale-state უარყოფას, rollback/equivocation უარყოფას და იდენტური retry-ის idempotency-ს.

ეს მოდელი მხოლოდ კონტრაქტის ლოკალური საცდელი რეალიზაციაა. ის **არ არის დამოუკიდებელი trust domain** და ვერ იცავს იმავე host-ის ან თვითონ SQLite ფაილის rollback/compromise-ისგან.

## რატომ არის ეს მნიშვნელოვანი?

NIST SP 800-209 (2020) ხაზს უსვამს, რომ backup-ის არსებობა საკმარისი არ არის: საჭიროა restore-ის პერიოდული გამოცდა, RPO/RTO-ის განსაზღვრა, recovery copy-ების გამიჯვნა და მათი მთლიანობის შემოწმება. TUF v1.0.36 კი metadata version-ებს rollback-ის აღმოსაჩენად და expiration-ს freeze attack-ის აღმოსაჩენად იყენებს. ეს წყაროები მაღალი დონის უსაფრთხოების პრინციპებს ამყარებს; ისინი არ ამტკიცებს, რომ NOEMA-ს საკუთარი მცირე პროტოკოლი უკვე სრულად უსაფრთხოა.

## მტკიცებულებები

### FACT

- NIST SP 800-209 §4.8, RA-SS-R5 რეკომენდაციას აძლევს periodic test restore-ს; RA-SS-R6 მოითხოვს RPO-ის განსაზღვრას. §4.7 აღწერს cyber-recovery copy-ების production-იდან გამიჯვნასა და immutable storage-ის განხილვას.
- TUF v1.0.36 §5.4–5.5 ამოწმებს metadata version-ებს rollback-ისთვის და expiration time-ს freeze attack-ისთვის. TUF-ის სრული root/role/threshold მექანიზმი ბევრად ფართოა, ვიდრე ეს reference model.
- SQLite `BEGIN IMMEDIATE` ამ reference model-ში ერთ ფაილურ ბაზაზე write transaction-ს იწყებს მანამ, სანამ current state წაიკითხება; ეს მხოლოდ ამ ბაზის ფარგლებში უზრუნველყოფს writers-ის სერიალიზაციას.

### REPRODUCED RESULT — local reference-model tests

10 unit test წარმატებით შესრულდა ლოკალურ სატესტო გარემოში. ტესტები ფარავს:
1. genesis generation-სა და მომდევნო generation-ს;
2. ზუსტად იდენტური retry-ის idempotency-ს;
3. stale expected state-ის უარყოფასა და state-ის უცვლელობას;
4. rollback-ის უარყოფას;
5. ერთი generation-ის სხვადასხვა immutable metadata-ით წარდგენილ equivocation-ს;
6. generation skip-ისა და არასწორი previous digest-ის უარყოფას;
7. ახალი generation-ისთვის ახალი manifest digest-ის მოთხოვნას;
8. დამოუკიდებელი stream-ების იზოლაციას;
9. პროცესის/ობიექტის ხელახლა გახსნის შემდეგ state-ის შენარჩუნებას;
10. ორი concurrent writer-ის შემთხვევაში ზუსტად ერთი წარმატებული advance-ის მიღებას.

ეს არის unit-test შედეგი ერთი local SQLite implementation-ისთვის და არა distributed consistency proof ან production security validation.

## ჰიპოთეზა

თუ high-water authority-ის write operation ატომურად ამოწმებს სრულ expected-state tuple-ს და მხოლოდ შემდეგ ინახავს ზუსტად მომდევნო generation-ს, ორი writer, რომლებიც ერთსა და იმავე ძველ state-ს ხედავენ, ვერ შეძლებს ორივე წარმატებით დაწეროს განსხვავებული ახალი generation.

## შემოწმების მეთოდი

- შეინახე stream ID, generation, manifest SHA-256, immutable object-version ID, previous manifest digest და monotonically increasing state version.
- ყოველი advance დაიწყოს `BEGIN IMMEDIATE`-ით, წაიკითხოს current state და შეადაროს caller-ის სრული expected state.
- იდენტური უკვე committed candidate ჩაითვალოს idempotent retry-ად; სხვა stale state უარყოფილ იქნეს.
- მოითხოვე generation +1 და წინა manifest digest-ის ზუსტი დამთხვევა.
- ერთდროულად გაუშვი ორი დამოუკიდებელი SQLite connection ერთი expected state-ით და განსხვავებული candidate-ებით.
- შეამოწმე, რომ ჩავარდნილი ოპერაციები state-ს არ ცვლის.

## შეზღუდვები და გაურკვევლობები

- SQLite reference database არის იგივე local trust domain-ში; მისი snapshot/rollback ან privileged rewrite high-water-საც უკან დააბრუნებს.
- ხელმოწერის გადამოწმება, key rotation/revocation, trusted time, object immutability/retention და provider authentication ამ მოდელში არ ხდება.
- concurrent test ამოწმებს ორ local thread-სა და ორ SQLite connection-ს ერთ host-ზე; ის არ ამტკიცებს ქსელურ partition-ებზე ან multi-region database-ზე linearizability-ს.
- `BEGIN IMMEDIATE`-ის ქცევა სხვა database/provider-ზე ავტომატურად არ გადაიტანება.
- production adapter-მდე საჭიროა independent trust-domain owner, failure-injection tests, durability/timeout semantics, recovery procedure და external security review.

## დასკვნა

**REPRODUCED RESULT:** ლოკალურ SQLite reference model-ში 10/10 unit test-მა აღწერილი compare-and-advance კონტრაქტი დაადასტურა, მათ შორის concurrent writer-ის ერთგამარჯვებული სცენარი.

**INFERENCE:** ეს მოდელი სასარგებლო conformance baseline-ია მომავალი დამოუკიდებელი high-water service-ისთვის, მაგრამ არ წარმოადგენს production anti-rollback კონტროლს.

## წყაროები

1. Ramaswamy Chandramouli and Doron Pinhas, *NIST SP 800-209: Security Guidelines for Storage Infrastructure*, October 2020, §§4.7–4.8, https://doi.org/10.6028/NIST.SP.800-209
2. The Update Framework, *Specification v1.0.36*, §§5.4–5.5, https://theupdateframework.github.io/specification/v1.0.36/
3. NOEMA repository, *Monotonic high-water protocol for signed backups* (Draft PR #85), https://github.com/maisuradzee/bibmom/pull/85

## ცვლილებების ისტორია

- 2026-11-27: დაემატა local SQLite reference model და 10 conformance-style unit test; production trust-domain claim არ კეთდება.


## შემოწმების სტატუსი

- ლოკალურ სატესტო გარემოში ახალი reference model-ის 10/10 unit test წარმატებით შესრულდა.
- პირველმა GitHub Actions quality run-მა draft validator-ზე შეაჩერა მუშაობა, რადგან შაბლონის ორი სავალდებულო ქართული სათაური აკლდა. სათაურები დაემატა; შემდგომმა exact-head quality CI run 45904140281 და CPU-thread workflow run 45904140275 ორივემ SUCCESS დააბრუნა commit `9c9a9f97eed68a38f450b70f3d43317fc77ec6bb`-ზე.
- PR branch დაფუძნებულია main snapshot `8a69e6d91a6151f61ace784e1d3161833ce4c94b`-ზე და PR #92-ის merge-ის შემდეგ ერთი main commit-ით ჩამორჩება; ნებისმიერი merge-მდე საჭიროა refresh/revalidation.
- არც provider adapter, არც external trust-domain service, არც რეალური backup/restore deployment არ შექმნილა.

## შემდეგი ნაბიჯები

1. დაასრულე exact-head quality CI, მათ შორის draft validation, schema validation, სრული unit suite და site/publication-boundary checks.
2. დამოუკიდებლად გადახედე SQLite concurrency semantics-სა და failure cases-ს; შეინარჩუნე მკაფიო განსხვავება local conformance model-სა და external authority-ს შორის.
3. მხოლოდ პასუხისმგებელი trust-domain owner-ისა და provider-ის დამტკიცების შემდეგ შექმენი ცალკე adapter; დაამატე multi-process, crash-after-commit/unknown-outcome, timeout, backup/restore და rollback-failure injection.
4. ჩაატარე off-host clean-host restore drill, რომელიც მოიცავს manifest, data, configuration, software dependencies, keys და access-control metadata-ს.
