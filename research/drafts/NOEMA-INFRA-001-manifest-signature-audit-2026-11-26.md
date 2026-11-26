# NOEMA-INFRA-001 — backup manifest signature implementation audit

- **ID:** NOEMA-INFRA-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** research platform provenance, signed backups and recovery
- **ავტორი/მომზადების სისტემა:** NOEMA

## საკვლევი კითხვა

რომელი backup-manifest security controls არის რეალურად დანერგილი main branch-ზე და რომელი რჩება მხოლოდ არქიტექტურულ გეგმად? შეესაბამება თუ არა კვლევითი პორტფელი და არქიტექტურის დოკუმენტაცია მიმდინარე კოდს?

## მოკლე შეჯამება

აუდიტმა დაადასტურა, რომ main-ზე უკვე არსებობს strict Draft 2020-12 metadata schema, runtime validator, exact-byte Ed25519 detached-signature verifier და plaintext/ciphertext digest/length checker. ამავე დროს, არქიტექტურის ადრეულ სექციებში წერია, თითქოს signature verification საერთოდ არ არსებობს, ხოლო section 11 მას უკვე აღწერს. ეს branch ასწორებს ამ წინააღმდეგობას და პორტფელის blocker-ებს.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

არაზუსტი სტატუსი იწვევს დუბლირებულ საინჟინრო სამუშაოს და შეიძლება შექმნას მცდარი შთაბეჭდილება როგორც არსებული შესაძლებლობების, ისე რეალური disaster-recovery readiness-ის შესახებ. ხელმოწერის შემოწმება არ უდრის დაშიფვრას, off-site retention-ს ან აღდგენის წარმატებულ გამოცდას.

## მტკიცებულებები

- **FACT:** main branch-ზე არსებობს `verify_backup_manifest_signature` და `verify_signed_backup_artifacts` ფუნქციები `noema_core/backup_manifest.py`-ში.
- **FACT:** verifier იღებს exact UTF-8 manifest bytes-ს, უარყოფს duplicate JSON keys/non-standard constants-ს, ამოწმებს caller-supplied trusted Ed25519 public key-ს და შემდეგ ამოწმებს plaintext/ciphertext SHA-256 და byte length-ს.
- **FACT:** `tests/test_backup_manifest_signature.py` იყენებს ephemeral test key-ებს და synthetic files-ს.
- **REPRODUCED RESULT:** ამ აუდიტში CI თავიდან არ გაშვებულა; exact-head CI-ის შედეგი pending-ია.
- **INFERENCE:** სწორი signature ადასტურებს, რომ კონკრეტული key აკონტროლებდა ზუსტად ამ bytes-ს; ის არ ამტკიცებს, რომ backup უახლესია ან key კომპრომეტირებული არ არის.
- **HYPOTHESIS:** ცალკე trusted monotonic high-water state-მა შეიძლება გამოავლინოს ძველ signed backup-ზე rollback, თუ მისი update ატომურია და თავად state rollback-ს არ ექვემდებარება.
- **UNTESTED IDEA:** backup-generation sequence/freshness metadata და external atomic compare-and-advance adapter.

## არსებული ცოდნა და წყაროები

- IETF RFC 8032 (2017), *Edwards-Curve Digital Signature Algorithm (EdDSA)*, https://www.rfc-editor.org/rfc/rfc8032.html — Ed25519 signing/verification specification.
- The Update Framework Specification v1.0.36, https://theupdateframework.github.io/specification/v1.0.36/ — signed version metadata და rollback/freeze checks-ის დიზაინის წყარო. NOEMA-ის backup manifest TUF implementation არ არის.

წვდომის თარიღი: 2026-11-26.

## მეთოდი ან ექსპერიმენტის გეგმა

1. main branch-ის `noema_core/backup_manifest.py`, `tests/test_backup_manifest_signature.py`, `requirements-test.txt` და `docs/OFFSITE_BACKUP_ARCHITECTURE.md` წაკითხვა.
2. ფუნქციების/ტესტების შედარება არქიტექტურის section 3, 8, 10 და 11-ის მტკიცებებთან.
3. პორტფელის blocker-ებისა და next-step ჩანაწერების შედარება კოდთან.
4. დოკუმენტაციის განახლება ისე, რომ schema validation, local artifact hash verification, detached signature verification და provider/restore controls მკაფიოდ გაიმიჯნოს.

## შედეგები და ინტერპრეტაცია

ამ branch-ში შესწორებულია:
- `docs/OFFSITE_BACKUP_ARCHITECTURE.md` — ადრეული სექციები აღარ უარყოფს უკვე არსებულ signature verifier-ს; section 10 რჩება hash-only tool-ის საზღვრად; section 11 აღწერს signature path-ს.
- `data/research-portfolio.json` — detached signature verification აღარ არის blocker; დარჩენილია production key custody, encryption/decryption, off-host provider, rollback state, clean-host restore და RPO/RTO.

ეს არის სტატუსის აუდიტი და არა ახალი production backup pipeline.

## კონკურენტი ახსნები

შესაძლოა დოკუმენტაციის წინააღმდეგობა გამოწვეული იყოს ეტაპობრივი განვითარებისას section-ების არათანმიმდევრული განახლებით. აუდიტი არ ადგენს, რომ რეალური backup job ან deployment მუშაობს.

## ჰიპოთეზა

თუ დოკუმენტაცია განასხვავებს უკვე არსებულ local verifier-სა და ჯერ არარსებულ production recovery controls-ს, შემდეგი საინჟინრო სამუშაო აღარ გაიმეორებს signature verification-ს და ფოკუსირდება rollback-resistant state-სა და რეალურ restore chain-ზე.

## შეზღუდვები და გაურკვევლობები

- არ არის production signing-key custody, rotation/revocation ან threshold policy.
- არ არის encryption/decryption pipeline ან off-host provider.
- არ არის immutable object retention, rollback-resistant high-water store, clean-host restore ან approved RPO/RTO.
- არ არის გამოყენებული operator-approved production/staging database.
- ეს აუდიტი არ ასრულებს restore drill-ს და არ ამტკიცებს disaster-recovery readiness-ს.

## დასკვნა

Detached Ed25519 signature verification უკვე არსებობს როგორც local prototype და არ უნდა ჩაითვალოს მომავალი, ჯერ დაუნერგავი feature-ად. Production backup/recovery კვლავ დაბლოკილია დამოუკიდებელი key custody-ით, encryption/decryption-ით, off-site retention-ით, anti-rollback state-ითა და clean-host restore validation-ით.

## წყაროები

1. Josefsson, S. & Liusvaara, I. (2017). RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA). IETF. https://www.rfc-editor.org/rfc/rfc8032.html
2. The Update Framework Specification v1.0.36. https://theupdateframework.github.io/specification/v1.0.36/

## შემოწმების სტატუსი

- კოდისა და ტესტების არსებობა main branch-ზე დადასტურებულია repository read.
- exact-head CI pending; ამ branch-ისთვის PASS არ არის ნაჩვენები.
- private keys, credentials, real manifests ან database dumps არ დაემატა.
- არ შექმნილა ახალი Supabase project და არ გამოყენებულა სხვა პროექტის ბაზა.

## შემდეგი ნაბიჯები

1. გაატარე exact-head quality CI.
2. დაამატე monotonic generation/high-water contract და synthetic rollback tests.
3. შეათანხმე key custody, encryption, provider retention, ownership და RPO/RTO.
4. მხოლოდ ამის შემდეგ დაგეგმე encrypted off-host backup და clean-host restore drill.
