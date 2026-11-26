# NOEMA-2026-006 — AquaSignal ხელმოწერილი მონოტონური checkpoint-ის პროტოკოლი

- **ID:** NOEMA-2026-006
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** წყლის უსაფრთხოების ოპერატორული ინციდენტების provenance და აღდგენის სანდოობა
- **ავტორი/მომზადების სისტემა:** NOEMA

## საკვლევი კითხვა

შეუძლია თუ არა detached signature-ით ხელმოწერილ, ვერსირებულ checkpoint-ს დააკავშიროს AquaSignal-ის event-store იდენტობა და hash-chain-ის მიმდინარე თავი, ხოლო ცალკე სანდო monotonic high-water მნიშვნელობამ გამოავლინოს ძველ checkpoint-ზე rollback?

## მოკლე შეჯამება

ამ branch-ში ემატება checkpoint-ის payload-ის მკაცრი canonical UTF-8 JSON კონტრაქტი, Ed25519 detached-signature verification, store identity-ისა და event-chain head-ის შედარება და caller-supplied high-water state-ის sequence/equivocation შემოწმება. კოდი არ ინახავს private key-ს ან trusted high-water state-ს. ეს უკანასკნელი caller-მა ატომურად უნდა შეინახოს SQLite ბაზისგან განცალკევებულ, დამოუკიდებლად დაცულ trust domain-ში.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

წყლის სისტემის ოპერატორული ინციდენტების ისტორიის მთლიანობა და rollback-ის აღმოჩენა შეიძლება დაეხმაროს ანგარიშვალდებულ რეაგირებასა და შემდგომ აუდიტს. პროტოტიპი არ ადგენს დამაბინძურებლების არსებობას, არ ადასტურებს წყლის სასმელად ვარგისიანობას და არ ცვლის ლაბორატორიულ ანალიზს ან Water Safety Plan-ს.

## არსებული ცოდნა და წყაროები

- IETF RFC 8032 (2017), *Edwards-Curve Digital Signature Algorithm (EdDSA)*, https://www.rfc-editor.org/rfc/rfc8032.html — Ed25519-ის detached signature-ისა და verification-ის სტანდარტული ალგორითმი.
- The Update Framework Specification v1.0.36, https://theupdateframework.github.io/specification/v1.0.36/ — signed version metadata, rollback/freeze attack-ის წინააღმდეგ version/high-water შემოწმების დიზაინის მაგალითი. NOEMA-ის ეს პროტოტიპი TUF implementation არ არის.
- NOEMA AquaSignal local event-store contract: `noema_core/aquasignal_store.py`, `docs/AQUASIGNAL_EVENT_STORE.md` — local SQLite event-chain replay და hash/count comparison.

წვდომის თარიღი: 2026-11-26.

## მტკიცებულებები

- **FACT:** main branch-ზე უკვე არსებობს append-only SQLite event chain და unsigned hash/count comparison API. ეს branch ამატებს ცალკე verifier-სა და synthetic tests-ს; ზუსტი head-ის CI შესრულება ჯერ დასრულებული არ არის.
- **REPRODUCED RESULT:** ამ ეტაპზე ახალი CI result არ არის ნაჩვენები; test fixtures სინთეზურია და საველე deployment-ს არ წარმოადგენს.
- **INFERENCE:** ხელმოწერილი payload-ის local chain head-თან შედარება და external high-water state-თან sequence-ის შემოწმება შეიძლება გამოავლენდეს payload-ის ცვლილებას, local chain mismatch-სა და ძველ sequence-ზე დაბრუნებას, თუ public key და external state ნამდვილად სანდოა.
- **HYPOTHESIS:** ცალკე ადმინისტრირებულ monotonic service-ს შეუძლია უზრუნველყოს საჭირო high-water guarantee atomic compare-and-advance ოპერაციით; ასეთი სერვისი ამ repository-ში არ არის დანერგილი ან გამოცდილი.
- **UNTESTED IDEA:** key rotation/revocation, threshold signing, remote immutable retention, clean-host restore და failed-verification monitoring.

## კონკურენტი ახსნები

- Sequence-ის მატება თავისთავად არ იცავს rollback-ისგან, თუ trusted state იმავე SQLite backup-ში ინახება.
- სწორი signature ადასტურებს მხოლოდ იმას, რომ კონკრეტული key-ით ზუსტად ეს bytes მოაწერეს; ის არ ამტკიცებს, რომ checkpoint უახლესია ან key კომპრომეტირებული არ არის.
- იგივე sequence-ზე განსხვავებული ხელმოწერილი payload შეიძლება მიუთითებდეს key misuse-ზე, state corruption-ზე ან producer bug-ზე; პროტოტიპი ასეთ equivocation-ს უარყოფს, მაგრამ მიზეზს ვერ ადგენს.

## ჰიპოთეზა

თუ checkpoint მოიცავს `store_id`, sequence, event count და chain tail hash-ს, ხოლო Ed25519 signature გადამოწმდება ცალკე trusted public key-ით, მაშინ payload tampering და local chain mismatch უარყოფილი იქნება. Rollback-ის აღმოჩენა მიიღწევა მხოლოდ მაშინ, როცა ბოლო მიღებული sequence და digest ინახება SQLite-ისგან დამოუკიდებელ, rollback-resistant trust domain-ში.

## შემოწმების მეთოდი

1. დახურული checkpoint object გადაიქცევა canonical UTF-8 JSON bytes-ად; duplicate key-ები, non-standard constants და non-canonical encoding უარყოფილია.
2. Detached Ed25519 signature მოწმდება caller-supplied trusted public-key map-ით.
3. მოწმდება მოსალოდნელი store identifier და ადგილობრივი replay-ით გადამოწმებული event count/tail hash.
4. Sequence შედარდება caller-supplied trusted high-water state-თან: დაბალი sequence არის rollback; იგივე sequence განსხვავებული digest-ით არის equivocation; იდენტური replay idempotent-ია.
5. წარმატებისას ბრუნდება next high-water state; caller-მა ის ატომურად უნდა შეინახოს SQLite-ის გარეთ.
6. ყველა ტესტი იყენებს synthetic incident-ებსა და მხოლოდ ტესტის პროცესში გენერირებულ ephemeral key-ებს.

## შედეგები და ინტერპრეტაცია

კოდი და ტესტები დამატებულია:
- `noema_core/aquasignal_checkpoint.py`
- `data/aquasignal-checkpoint.schema.json`
- `tests/test_aquasignal_signed_checkpoint.py`
- `docs/AQUASIGNAL_EVENT_STORE.md`

ზუსტი head-ის CI ჯერ pending-ია; PASS არ არის ნაჩვენები და ტესტების შედეგი არ უნდა ჩაითვალოს დადასტურებულად CI-ის დასრულებამდე.

## შეზღუდვები და გაურკვევლობები

- Public key უნდა მოდიოდეს დამოუკიდებლად authenticated არხიდან; იმავე backup object-იდან ჩამოტვირთული key სანდო trust anchor არ არის.
- High-water state უნდა ინახებოდეს ატომურად SQLite-ის გარეთ და სხვა rollback domain-ში; ლოკალური JSON ფაილი ან იგივე backup anti-rollback-ს არ უზრუნველყოფს.
- არ არსებობს production signer, key rotation/revocation, threshold signing, remote checkpoint service ან immutable provider retention.
- არ არსებობს clean-host recovery და operator-approved access-control integration.
- არ არსებობს ნებადართული paired sensor/laboratory მონაცემი, site-approved thresholds ან field validation.

## დასკვნა

ეს არის უსაფრთხოების კონტრაქტის software prototype და არა production anti-rollback service. საველე მონაცემის ან წყლის ხარისხის ეფექტიანობის შესახებ დასკვნა არ კეთდება. კვლევა რჩება draft/preliminary და საჭიროებს exact-head CI-ს, დამოუკიდებელ cryptographic review-სა და external high-water service-ის ცალკე დიზაინს.

## წყაროები

1. Josefsson, S. & Liusvaara, I. (2017). RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA). IETF. https://www.rfc-editor.org/rfc/rfc8032.html
2. The Update Framework Specification v1.0.36. https://theupdateframework.github.io/specification/v1.0.36/

## შემოწმების სტატუსი

- Unit/schema tests დაწერილია; exact-head CI pending.
- Private key, real store identifier და operational records არ ინახება public repository-ში.
- Rollback protection არ არის დასრულებული, სანამ caller არ გამოიყენებს დამოუკიდებელ atomic high-water store-ს.

## შემდეგი ნაბიჯები

1. დაასრულე exact-head quality CI და გამოასწორე ყველა აღმოჩენილი ხარვეზი.
2. მოითხოვე დამოუკიდებელი cryptographic protocol review.
3. შეიმუშავე external high-water compare-and-advance adapter key custody/recovery პროცედურით.
4. საველე მტკიცებები დაბლოკილი დარჩეს, სანამ authorized water-system data და operator approvals არ იქნება.
