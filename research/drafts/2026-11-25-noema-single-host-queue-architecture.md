# ერთჰოსტიანი NOEMA runtime: SQLite queue თუ ცალკე message broker?

- **ID:** NOEMA-2026-006
- **სტატუსი:** draft
- **თარიღი:** 2026-11-25
- **სფერო:** სისტემური არქიტექტურა / საიმედოობა / ინფრასტრუქტურა
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow (AI-assisted desk research)

## საკვლევი კითხვა

არსებული NOEMA runtime-ისთვის, რომელიც ერთ Hetzner Linux სერვერზე უნდა გაეშვას, საკმარისია თუ არა SQLite-ზე დაფუძნებული მდგრადი job queue და systemd, თუ საწყის ეტაპზევე აუცილებელია ცალკე message broker (მაგალითად Redis ან RabbitMQ)?

## მოკლე შეჯამება

არსებული კოდის, SQLite-ის ოფიციალური დოკუმენტაციისა და systemd-ის სახელმძღვანელოს მიხედვით, **ერთ სერვერზე არსებული, ზომიერი დატვირთვის NOEMA runtime-ის საწყის გაშვებაზე SQLite + systemd ტექნიკურად გამართლებული არჩევანია**. SQLite უზრუნველყოფს ტრანზაქციულ ჩაწერას და ერთდროულად რამდენიმე მკითხველს; WAL რეჟიმში მკითხველები და writer ერთმანეთს ნაკლებად ბლოკავენ, თუმცა ერთ მომენტში მხოლოდ ერთი writer მუშაობს. systemd-ის `Restart=on-failure` განკუთვნილია ხანგრძლივი სერვისის ავარიული აღდგენისთვის.

ეს არ ადასტურებს, რომ SQLite გაუძლებს NOEMA-ს მომავალ, ჯერ გაუზომავ დატვირთვას. ცალკე broker საჭიროა მაშინ, როცა რეალური მოთხოვნები მოითხოვს მრავალ ჰოსტზე განაწილებულ worker-ებს, მაღალ ჩაწერის კონკურენციას, დამოუკიდებელ queue availability-ს ან უფრო რთულ delivery/consumer semantics-ს. ამჟამად NOEMA-ს საკუთარი დოკუმენტაციაც პირდაპირ ზღუდავს არქიტექტურას ერთ ჰოსტზე და აცხადებს, რომ გარე კვლევითი connector-ები ჯერ არ არის ჩართული.

**მთავარი რეკომენდაცია:** არ დავამატოთ Redis/RabbitMQ მხოლოდ „მომავლისთვის“. ჯერ გავუშვათ არსებული runtime ერთ სერვერზე, ჩავატაროთ დატვირთვისა და აღდგენის ტესტები, შევაგროვოთ queue latency, lock contention, job throughput და recovery მონაცემები. შემდეგ გადავწყვიტოთ, საჭიროა თუ არა broker ან PostgreSQL-ზე გადასვლა.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

დამატებითი ინფრასტრუქტურა ზრდის ოპერაციულ სირთულეს, უსაფრთხოების ზედაპირს, ხარჯსა და აღდგენის სამუშაოს. მეორე მხრივ, ზედმეტად მარტივი queue შეიძლება გახდეს bottleneck, თუ NOEMA-ს ბევრი worker ან ხანგრძლივი კვლევითი workflow დაემატება. სწორი გადაწყვეტილება უნდა დაეყრდნოს მიმდინარე კოდის შესაძლებლობებს და გაზომილ დატვირთვას და არა მხოლოდ ზოგად არქიტექტურულ მოდას.

## არსებული ცოდნა და წყაროები

1. **SQLite — Write-Ahead Logging.** SQLite-ის ოფიციალური დოკუმენტაცია განმარტავს WAL ფაილს, checkpoint-სა და WAL-ის შენახვის პირობებს. URL: https://www.sqlite.org/wal.html (წვდომა: 2026-11-25). ამყარებს მტკიცებას, რომ WAL არის მონაცემთა ბაზის მდგრადი მდგომარეობის ნაწილი და მისი განცალკევება ძირითადი DB ფაილისგან შეიძლება დასრულებული ტრანზაქციების დაკარგვას ან დაზიანებას იწვევდეს.
2. **SQLite — Isolation In SQLite.** SQLite-ის ოფიციალური დოკუმენტაცია. URL: https://sqlite.org/isolation.html (წვდომა: 2026-11-25). ამყარებს მტკიცებას, რომ SQLite წერს სერიალიზებულად — ერთდროულად მხოლოდ ერთი writer; რამდენიმე connection-ს შეუძლია მუშაობა, მაგრამ write transaction-ები რიგრიგობით სრულდება.
3. **SQLite — Using the Online Backup API.** SQLite-ის ოფიციალური დოკუმენტაცია. URL: https://sqlite.org/backup.html (წვდომა: 2026-11-25). აღწერს online backup-ს, რომელიც ქმნის snapshot-ს და საშუალებას იძლევა backup-ის დროს სხვა კავშირებმაც განაგრძონ მუშაობა; უბრალო ფაილის კოპირებას აქვს შეზღუდვები და ავარიისას შეიძლება backup დაზიანდეს.
4. **systemd.service — Service unit configuration.** freedesktop.org-ის ოფიციალური სახელმძღვანელო, ვერსია 258, მოძიებული 2026-11-25. URL: https://www.freedesktop.org/software/systemd/man/258/systemd.service.html. ამყარებს მტკიცებას, რომ `Restart=on-failure` რეკომენდებულია ხანგრძლივი სერვისებისთვის, რათა ავარიული დასრულების შემდეგ ავტომატური აღდგენა სცადოს; restart ექვემდებარება start-rate limiting-ს.
5. **NOEMA repository — README.md**, branch `infra/hetzner-noema-bootstrap`, წვდომა: 2026-11-25. URL: https://github.com/maisuradzee/bibmom/blob/infra/hetzner-noema-bootstrap/README.md. აღწერს მიმდინარე runtime-ის შემადგენლობასა და იმას, რომ გარე ინფორმაციის connector-ები ჯერ არ არის ჩართული.
6. **NOEMA repository — docs/SERVICE_DEPLOYMENT.md**, branch `infra/hetzner-noema-bootstrap`, წვდომა: 2026-11-25. URL: https://github.com/maisuradzee/bibmom/blob/infra/hetzner-noema-bootstrap/docs/SERVICE_DEPLOYMENT.md. აღწერს ერთჰოსტიან SQLite queue-ს, systemd deployment-ს, მიმდინარე შეზღუდვებსა და backup-ის საჭიროებას.
7. **NOEMA repository — noema_core/jobs.py და noema_core/supervisor.py**, branch `infra/hetzner-noema-bootstrap`, წვდომა: 2026-11-25. URL: https://github.com/maisuradzee/bibmom/tree/infra/hetzner-noema-bootstrap/noema_core. კოდის დათვალიერებით დადასტურდა idempotency key, expiring worker lease, შეზღუდული retry, payload/result hash, SHA-256 chained audit log და supervisor-ის bounded backoff. Supervisor-ის docstring პირდაპირ აღნიშნავს, რომ ეს არ არის multi-host scheduler.

## მტკიცებულებები

### FACT — SQLite-ის კონკურენტულობის ზღვარი

SQLite-ის ოფიციალური isolation დოკუმენტაციის მიხედვით, ერთ მონაცემთა ბაზაზე ერთდროულად მხოლოდ ერთი writer ასრულებს write transaction-ს. რამდენიმე reader დაშვებულია. WAL რეჟიმი აუმჯობესებს reader/writer თანაარსებობას, მაგრამ არ აუქმებს ერთ writer-ის შეზღუდვას.

### FACT — WAL ფაილი მონაცემთა ბაზის ნაწილია

WAL რეჟიმში `-wal` ფაილი შეიცავს ჯერ checkpoint-ით მთავარ DB ფაილში არ გადატანილ committed მდგომარეობას. SQLite აფრთხილებს, რომ DB ფაილის WAL ფაილისგან განცალკევებამ შეიძლება დაკარგოს committed ტრანზაქციები ან დააზიანოს ბაზა. ამიტომ backup/restore არ უნდა გაკეთდეს live DB-ის მხოლოდ ერთი ფაილის დაუფიქრებელი კოპირებით.

### FACT — უსაფრთხო live backup-ის მექანიზმი არსებობს

SQLite Online Backup API ქმნის snapshot-ს და წყაროს მხოლოდ წაკითხვის მოკლე პერიოდებში კეტავს; სხვა კავშირებს შეუძლიათ მუშაობის გაგრძელება. ეს არის უკეთესი საფუძველი აპლიკაციის დონის backup-სთვის, ვიდრე live ფაილის უბრალო copy.

### FACT — systemd უზრუნველყოფს პროცესის აღდგენის საბაზისო მექანიზმს

systemd-ის დოკუმენტაცია `Restart=on-failure`-ს რეკომენდაციას უწევს ხანგრძლივი სერვისებისთვის. ეს აღადგენს პროცესს ავარიული exit-ის შემდეგ, მაგრამ თავისთავად არ ამოწმებს კვლევის შედეგის სისწორეს, არ უზრუნველყოფს DB backup-ს და არ უდრის application-level watchdog-ს.

### FACT — NOEMA-ს მიმდინარე კოდი უკვე შეიცავს რიგის რამდენიმე მნიშვნელოვან მექანიზმს

კოდის დათვალიერებით:
- დავალების ხელახალი დუბლირებისგან დაცვა ხდება idempotency key-ით;
- worker იღებს ვადიან lease-ს;
- დაკარგული/ვადაგასული lease-ის აღდგენა queue-ის დიზაინის ნაწილია;
- retry შეზღუდულია;
- payload და result ინახავს SHA-256 hash-ს;
- audit events დაკავშირებულია hash chain-ით;
- supervisor იყენებს შეზღუდულ exponential backoff-ს;
- handler-ები წინასწარ allowlist-ით რეგისტრირდება და arbitrary code არ სრულდება.

ეს არის კოდის არსებობის შემოწმება და არა production დატვირთვის benchmark.

### FACT — მიმდინარე სისტემა ერთ ჰოსტზეა გათვლილი

NOEMA-ს deployment დოკუმენტაცია პირდაპირ ამბობს, რომ SQLite queue ერთ ჰოსტზეა და არ წარმოადგენს distributed queue-ს. მიმდინარე service bootstrap ასრულებს მხოლოდ ადგილობრივ self-check-ებს; გარე წყაროების research connector-ები ჯერ არ არის ჩართული.

## კონკურენტი ახსნები

1. **SQLite საკმარისია:** თუ ერთ სერვერზეა worker-ები, queue-ის write rate ზომიერია და ოპერაციული სიმარტივე პრიორიტეტულია, SQLite ამცირებს დამოკიდებულებებს და აღდგენის ზედაპირს.
2. **SQLite მალე გახდება bottleneck:** თუ ბევრი worker ხშირად ცვლის queue-ის მდგომარეობას, single-writer serialization და lock contention შეიძლება throughput-ს ზღუდავდეს.
3. **Broker თავიდანვე სჯობს:** ეს შეიძლება გამართლდეს მხოლოდ მაშინ, თუ უკვე არსებობს მრავალჰოსტიანი worker-ების, queue-ის დამოუკიდებელი availability-ის ან broker-specific delivery semantics-ის მკაფიო მოთხოვნა. ამჟამინდელი კოდი ასეთ მოთხოვნას არ ადასტურებს.
4. **PostgreSQL შეიძლება იყოს შუალედური ნაბიჯი:** თუ საჭიროა მრავალპროცესიანი/მრავალჰოსტიანი საერთო state და ტრანზაქციული query-ები, PostgreSQL შეიძლება უფრო ბუნებრივი იყოს, ვიდრე SQLite-ის შენარჩუნება და ცალკე broker-ის დამატება. ეს ვარიანტი ცალკე უნდა შემოწმდეს.

## ჰიპოთეზა

**H1:** NOEMA-ს ამჟამინდელი ერთჰოსტიანი runtime-ისთვის SQLite + systemd საკმარისია პირველი deployment-ისა და საწყისი კვლევითი ციკლებისთვის, თუ queue-ის კონკურენტულობა და მონაცემთა მოცულობა გაზომილ ზღვარში რჩება.

**H2:** ცალკე broker ან საერთო სერვერული DB საჭირო გახდება მხოლოდ მაშინ, როცა ტესტი აჩვენებს მიუღებელ queue wait time-ს, lock contention-ს, throughput-ის გაუარესებას ან მრავალჰოსტიანი execution-ის რეალურ მოთხოვნას.

ეს ჰიპოთეზებია და ჯერ არ არის ექსპერიმენტულად დადასტურებული.

## შემოწმების მეთოდი

შემდეგი benchmark უნდა ჩატარდეს Hetzner-ის staging სერვერზე ან მის ეკვივალენტურ სატესტო გარემოში:

1. ერთი worker და შემდეგ 2, 4, 8 worker ერთსა და იმავე SQLite ფაილზე.
2. 1k, 10k და 100k მცირე job-ების enqueue/claim/complete ციკლი.
3. გაზომვა: jobs/sec, p50/p95 enqueue-to-start latency, p95 completion latency, SQLITE_BUSY/lock wait, CPU, RAM, disk I/O და WAL ზომა.
4. ჩავარდნის ტესტები: worker process kill, service restart, host reboot, ვადაგასული lease-ის აღდგენა და განმეორებითი job submission.
5. backup ტესტი: Online Backup API ან `VACUUM INTO`; აღდგენა ცალკე DB-ში; `PRAGMA integrity_check` და audit-chain verification.
6. შედარება PostgreSQL ან broker-backed პროტოტიპთან მხოლოდ იმ შემთხვევაში, თუ SQLite ტესტი წინასწარ განსაზღვრულ SLO-ს ვერ აკმაყოფილებს.

წინასწარი სამუშაო SLO (სატესტო კრიტერიუმი და არა არსებული შედეგი): მცირე job-ებისთვის p95 queue wait < 2 წამი 4 worker-ის პირობებში; crash/reboot-ის შემდეგ ყველა დაუმთავრებელი job უნდა იყოს ან ხელახლა დასამუშავებელი, ან მკაფიო failed/blocked მდგომარეობაში; არც ერთი დასრულებული job არ უნდა დაიკარგოს backup/restore ტესტში. ეს ზღვარი უნდა გადაიხედოს რეალური NOEMA workload-ის მიხედვით.

## შედეგები და ინტერპრეტაცია

**ლიტერატურული/კოდის მიმოხილვის შედეგი:** SQLite + systemd-ის გამოყენება საწყის ერთჰოსტიან deployment-ზე დასაბუთებულია. მიმდინარე queue-ის კოდი შეიცავს idempotency-ს, lease-ს, bounded retry-სა და audit integrity-ს; SQLite-ის დოკუმენტაცია ადასტურებს ტრანზაქციულ სერიალიზაციას და WAL-ის შესაბამის შეზღუდვებს; systemd უზრუნველყოფს პროცესის ავტომატურ აღდგენას.

**რაოდენობრივი ექსპერიმენტი ჯერ არ ჩატარებულა.** ამიტომ არ გვაქვს რეალური throughput, p95 latency, worker-ის ოპტიმალური რაოდენობა ან CPX32/CPX42-ის რესურსული დასაბუთება. ამ კვლევიდან არ შეიძლება დავასკვნათ, რომ არჩეული Hetzner SKU კონკრეტულ დატვირთვას გაუძლებს.

## შეზღუდვები და გაურკვევლობები

- წყაროების მიმოხილვა არ ცვლის დატვირთვის benchmark-ს.
- მიმდინარე service-ის ფუნქციონალი ჯერ მხოლოდ ადგილობრივ self-check-ებს მოიცავს და არა გარე კვლევას.
- SQLite-ის შედეგები დამოკიდებულია filesystem-ზე, storage latency-ზე, transaction-ის ხანგრძლივობასა და worker-ების ქცევაზე.
- WAL არ უნდა განთავსდეს ისეთ network filesystem-ზე, რომლის locking/shared-memory სემანტიკა SQLite-ის მოთხოვნებს არ აკმაყოფილებს.
- systemd restart ვერ აღადგენს დაკარგულ დისკს ან დაზიანებულ/დაკარგულ backup-ს.
- SHA-256 audit chain მონაცემთა ცვლილებას აფიქსირებს, მაგრამ თავისთავად არ იცავს იმ შემთხვევისგან, როცა თავდამსხმელს შეუძლია DB და მთელი chain თავიდან გადააკეთოს.
- Hetzner-ის კონკრეტული instance-ის performance ამ კვლევაში არ გაზომილა.

## დასკვნა

**NOEMA-ს პირველი Hetzner deployment-ისთვის რეკომენდებულია არსებული SQLite queue + systemd არქიტექტურის შენარჩუნება, დამატებითი Redis/RabbitMQ-ის გარეშე.** ეს არის ყველაზე დაბალი სირთულის და მიმდინარე კოდთან თავსებადი არჩევანი.

აუცილებელი პირობები:
- SQLite-ის backup უნდა იყოს WAL-aware და აღდგენა რეგულარულად უნდა შემოწმდეს;
- უნდა დაემატოს/გაიზომოს queue latency, lock contention და job throughput;
- უნდა შესრულდეს process crash და host reboot recovery ტესტები;
- multi-host execution-ის ან გაზომილი bottleneck-ის გამოჩენისას ხელახლა შეფასდეს PostgreSQL/broker არქიტექტურა.

## წყაროები

- SQLite, “Write-Ahead Logging”, https://www.sqlite.org/wal.html
- SQLite, “Isolation In SQLite”, https://sqlite.org/isolation.html
- SQLite, “Using the SQLite Online Backup API”, https://sqlite.org/backup.html
- freedesktop.org, “systemd.service”, https://www.freedesktop.org/software/systemd/man/258/systemd.service.html
- NOEMA repository, README.md, https://github.com/maisuradzee/bibmom/blob/infra/hetzner-noema-bootstrap/README.md
- NOEMA repository, SERVICE_DEPLOYMENT.md, https://github.com/maisuradzee/bibmom/blob/infra/hetzner-noema-bootstrap/docs/SERVICE_DEPLOYMENT.md
- NOEMA repository, jobs.py / supervisor.py, https://github.com/maisuradzee/bibmom/tree/infra/hetzner-noema-bootstrap/noema_core

## ცვლილებების ისტორია

- 2026-11-25 — პირველი კვლევითი დრაფტი; წყაროების მიმოხილვა და repository code inspection. რაოდენობრივი benchmark დაგეგმილია, მაგრამ არ ჩატარებულა.
