# NOEMA — ავტონომიური სამუშაოების მართვის არქიტექტურა

## დანიშნულება

ეს მოდული ქმნის NOEMA-ს გრძელვადიანი ავტომატიზაციის საყრდენს: სამუშაოს მიღება, უსაფრთხო რიგში შენახვა, მუშაკისთვის მინიჭება, შესრულების შედეგის დაფიქსირება, ჩავარდნის შემდეგ ხელახალი ცდა და აუდიტის კვალის შენარჩუნება.

## არსებული, კოდში რეალიზებული შესაძლებლობები

- **მდგრადი საცავი:** SQLite მონაცემთა ბაზა, WAL რეჟიმი და `synchronous=FULL`.
- **დუბლიკატისგან დაცვა:** idempotency key ერთი და იმავე განსაზღვრების ხელახლა დამატებას არსებულ დავალებაზე აბრუნებს; იმავე key-ის სხვა payload/type-ზე გამოყენება შეცდომაა.
- **სამუშაოს მდგომარეობები:** `queued`, `running`, `succeeded`, `failed`, `blocked` (ამ ვერსიაში `blocked` დაცულია სქემაში, მაგრამ ჯერ არ გამოიყენება workflow policy engine-ით).
- **Worker lease:** მუშაკი იღებს ვადიან lease-ს; heartbeat განაახლებს მას. ვადის გასვლისას შემდეგი claim ოპერაცია ძველ lease-ს აღადგენს და retry-ლიმიტს ითვალისწინებს.
- **შეზღუდული retry:** მცდელობების ზედა ზღვარი და დაგვიანებული ხელახალი გაშვება.
- **შედეგის მთლიანობა:** payload/result ინახება canonical JSON-ად, SHA-256 hash-ით; payload-ის შეცვლა worker-ის claim-ს აჩერებს.
- **აუდიტის ჯაჭვი:** ყველა მდგომარეობის ცვლილება ემატება SHA-256-ით დაკავშირებულ მოვლენათა რიგს; `verify_audit_log()` ცვლილებას ან რიგის წყვეტას აფიქსირებს.
- **მკაცრი handler allowlist:** `HandlerRegistry` მხოლოდ პროგრამის კოდში წინასწარ რეგისტრირებულ handler-ებს იღებს. Queue payload არ გამოიყენება კოდის დინამიკური იმპორტისთვის ან შესრულებისთვის.
- **სატესტო health-check:** CI ქმნის დროებით DB-ს, ამატებს/ასრულებს დავალებას, ამოწმებს worker-სა და მთლიანობას.
- **მრავალპროცესიანი claim ტესტი:** რამდენიმე დამოუკიდებელი Python process ერთ SQLite ფაილს იყენებს; ტესტი ამოწმებს, რომ თითოეული job მხოლოდ ერთხელ და სხვადასხვა worker-ზე ნაწილდება. ეს ამოწმებს ერთ ჰოსტზე პროცესების კოორდინაციას და არა სხვადასხვა მანქანას შორის distributed execution-ს.
- **ფაილის წვდომა:** POSIX სისტემებზე DB ფაილს ენიჭება owner-only `0600` რეჟიმი; `:memory:` რეჟიმი უარყოფილია, რადგან ის პროცესებს შორის საერთო საცავი არ არის.
- **მთლიანობის აუდიტი:** მოწმდება SQLite integrity, payload/result SHA-256-ები და აუდიტის ჯაჭვი; შეცვლილი ან დაზიანებული ჩანაწერი integrity report-ში ჩავარდნად აისახება.

## მინიმალური გამოყენება

```python
from noema_core import HandlerRegistry, JobQueue, Worker

queue = JobQueue()  # ~/.noema/noema-jobs.sqlite3
queue.enqueue(
    "research.normalize",
    {"source_snapshot": "sha256:..."},
    idempotency_key="normalize-snapshot-001",
    max_attempts=3,
)

registry = HandlerRegistry()
registry.register(
    "research.normalize",
    lambda payload, context: {
        "normalized": True,
        "source_snapshot": payload["source_snapshot"],
    },
)

outcome = Worker(queue, "worker-local-1", registry).run_once()
print(outcome.outcome if outcome else "no ready jobs")
```

ხანგრძლივ handler-ს შეუძლია პერიოდულად გამოიძახოს `context.heartbeat()`. Handler-მა უნდა მიიღოს მხოლოდ მონაცემის მითითებები/იდენტიფიკატორები და არა პაროლები, API გასაღებები ან სხვა საიდუმლოებები.

## CLI

```bash
python -m noema_core.jobs_cli --help
python -m noema_core.jobs_cli enqueue --type research.normalize --payload '{"source_snapshot":"sha256:..."}'
python -m noema_core.jobs_cli list
python -m noema_core.jobs_cli verify
```

ნაგულისხმევი DB მდებარეობაა `~/.noema/noema-jobs.sqlite3`; მისი შეცვლა შესაძლებელია `NOEMA_JOBS_DB` გარემოს ცვლადით ან CLI-ის `--db` პარამეტრით. CLI არ ბეჭდავს job payload-ს `list` ბრძანებისას.

## განზრახ შეზღუდვები

1. ეს არის ერთი ჰოსტის SQLite რიგი და არა მრავალმანქანიანი distributed queue. SQLite WAL არ უნდა ჩაითვალოს მრავალრეგიონულ ან არასაიმედო network filesystem-ზე კოორდინაციის გარანტიად.
2. Queue არ ქმნის handler-ებს დინამიკურად, არ ასრულებს shell ბრძანებებს და არ იღებს arbitrary code-ს payload-იდან.
3. მონაცემთა ბაზა ამ ეტაპზე დაშიფრული არ არის. მასში არ უნდა ჩაიწეროს credentials, API tokens, პაროლები ან სენსიტიური პერსონალური ინფორმაცია. საიდუმლოებები უნდა ინახებოდეს ცალკე secret store-ში, ხოლო job payload-ში — მხოლოდ უსაფრთხო reference.
4. Hash-chain არის ცვლილებების აღმოჩენის მექანიზმი; მასზე წვდომის მქონე მავნე ადმინისტრატორს შეუძლია მთელი ჯაჭვის ხელახლა გამოთვლა. ამიტომ საჭიროა შეზღუდული filesystem წვდომა და პერიოდული დამოუკიდებელი backup.
5. Worker-ები მხოლოდ იმ ტიპებს ამუშავებენ, რომლებზეც handler წინასწარ არის რეგისტრირებული. უცნობი ტიპის job რიგში რჩება; ეს განზრახ fail-closed ქცევაა.
6. Worker-ის ამ ვერსიას აქვს `run_once()` და handler-ის lease heartbeat; მუდმივად მომუშავე supervisor/service, scheduler, distributed multi-host execution და გარე source connectors ჯერ არ არის დამატებული.

## შემდეგი ტექნიკური ფენები — კვლევის დაწყების გარეშე

- durable workflow/DAG dependencies და ეტაპების მდგომარეობები;
- worker supervisor: მუდმივი ციკლი, graceful shutdown, heartbeat და crash recovery;
- source connector registry, provenance, rate limits და per-source permission evidence;
- scheduler, bounded concurrency, quotas და back-pressure;
- metrics, structured logs, alerts, backup/restore და recovery drill;
- უსაფრთხო secrets integration და კერძო drafts storage;
- multi-host execution მხოლოდ მაშინ, როცა შესაბამისი სერვერი/ინფრასტრუქტურა რეალურად განისაზღვრება და ტესტირდება.
