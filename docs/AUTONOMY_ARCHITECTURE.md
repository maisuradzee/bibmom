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
- **მრავალპროცესიანი claim ტესტი:** რამდენიმე დამოუკიდებელი Python process ერთ SQLite ფაილს იყენებს; ტესტი ამოწმებს, რომ თითოეული job მხოლოდ ერთხელ და სხვადასხვა worker-ზე ნაწილდება. ეს ადასტურებს ერთ ჰოსტზე პროცესების კოორდინაციას და არა სხვადასხვა მანქანაზე distributed execution-ს.
- **ფაილის წვდომა:** POSIX სისტემებზე DB ფაილს ენიჭება owner-only `0600` რეჟიმი; `:memory:` უარყოფილია, რადგან ის პროცესებს შორის საერთო საცავი არ არის.
- **მთლიანობის აუდიტი:** მოწმდება SQLite integrity, payload/result SHA-256 და audit hash-chain; დაზიანებული ან არასწორი JSON ჩანაწერი integrity report-ში ჩავარდნად აღირიცხება.

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

## Durable workflow DAG Engine

`WorkflowEngine` workflow-ის განსაზღვრებას, ნაბიჯებსა და დამოკიდებულებებს იმავე SQLite მონაცემთა ბაზაში ინახავს, სადაც სამუშაოების რიგია. თითოეულ ნაბიჯს აქვს უნიკალური ID, allowlisted `job_type`, JSON payload და prerequisite-ების სია. `start()` ჯერ ამოწმებს ყველა dependency-ს, უცნობ ნაბიჯებსა და ციკლებს; შემდეგ მხოლოდ root ნაბიჯებს აგზავნის რიგში. დასრულებული ნაბიჯის წარმატების შემდეგ `advance()` მის შვილ ნაბიჯებს ხდის ხელმისაწვდომს. თუ prerequisite საბოლოოდ ჩავარდა, მის ქვედა ნაბიჯებს ენიჭება `blocked` მდგომარეობა. Workflow-ის idempotency key ხელს უშლის ერთი და იმავე განსაზღვრების დუბლირებულ შექმნას, ხოლო თითოეული step-ის job enqueue იყენებს თავის deterministic idempotency key-ს, რათა crash-ის შემდეგ dispatch უსაფრთხოდ განმეორდეს.

ყველა workflow transition ემატება საერთო queue audit hash-chain-ში. Workflow არ ატვირთავს handler-ს დინამიკურად: ყველა `job_type` წინასწარ უნდა იყოს რეგისტრირებული trusted `HandlerRegistry`-ში. Queue-ის retry/lease მექანიზმი იძლევა *at-least-once* შესრულების სემანტიკას; ამიტომ handler-მა გარე side effect-ები idempotent უნდა გახადოს. Exactly-once შესრულება არ არის გარანტირებული.

`WorkflowEngine.advance(workflow_id)` ამოწმებს უკვე გაშვებულ job-ებს და dispatch-ს აკეთებს იმ ნაბიჯებზე, რომელთა წინაპირობებიც წარმატებით დასრულდა. ამ ვერსიაში advance-ის გამოძახება ხდება workflow runner/scheduler-ის მხრიდან; worker supervisor-ს workflow engine-თან მუდმივი ინტეგრაცია ჯერ არ აქვს. CI smoke-test ახორციელებს ორეტაპიან workflow-ს ბოლომდე.

## Worker Supervisor

`WorkerSupervisor` უზრუნველყოფს მუდმივ სამუშაო ციკლს: `Worker.run_once()`-ის განმეორებით გამოძახებას, უმოქმედობისას ლოდინს, გარე `threading.Event`-ით graceful stop-ს, მაქსიმალური სამუშაოების/დროის/idle-ციკლების ლიმიტებს და transient შეცდომებზე ზრდად, მაგრამ შეზღუდულ backoff-ს. თანმიმდევრული ინფრასტრუქტურული შეცდომების ლიმიტის მიღწევისას supervisor უსაფრთხოდ ჩერდება და აბრუნებს შესრულების ანგარიშს (`SupervisorReport`). ხანგრძლივ handler-ს კვლავ თავად მოეთხოვება `context.heartbeat()`.

Supervisor არ აყენებს process-wide signal handler-ებს და არ ირჩევს handler-ებს job payload-იდან. სერვისის bootstrap-მა უნდა დაარეგისტრიროს მხოლოდ trusted handler-ები, გაუზიაროს supervisor-ს stop event და SIGINT/SIGTERM-ზე მოითხოვოს graceful stop. Worker-ის გაჩერების შემდეგ მოუმთავრებელი job-ის lease-ის ვადის გასვლა აღდგება queue-ის მომდევნო claim-ზე.

## განზრახ შეზღუდვები

1. ეს არის ერთი ჰოსტის SQLite რიგი და არა მრავალმანქანიანი distributed queue. SQLite WAL არ უნდა ჩაითვალოს მრავალრეგიონულ ან არასაიმედო network filesystem-ზე კოორდინაციის გარანტიად.
2. Queue არ ქმნის handler-ებს დინამიკურად, არ ასრულებს shell ბრძანებებს და არ იღებს arbitrary code-ს payload-იდან.
3. მონაცემთა ბაზა ამ ეტაპზე დაშიფრული არ არის. მასში არ უნდა ჩაიწეროს credentials, API tokens, პაროლები ან სენსიტიური პერსონალური ინფორმაცია. საიდუმლოებები უნდა ინახებოდეს ცალკე secret store-ში, ხოლო job payload-ში — მხოლოდ უსაფრთხო reference.
4. Hash-chain არის ცვლილებების აღმოჩენის მექანიზმი; მასზე წვდომის მქონე მავნე ადმინისტრატორს შეუძლია მთელი ჯაჭვის ხელახლა გამოთვლა. ამიტომ საჭიროა შეზღუდული filesystem წვდომა და პერიოდული დამოუკიდებელი backup.
5. Worker-ები მხოლოდ იმ ტიპებს ამუშავებენ, რომლებზეც handler წინასწარ არის რეგისტრირებული. უცნობი ტიპის job რიგში რჩება; ეს განზრახ fail-closed ქცევაა.
6. Supervisor და durable workflow DAG engine კოდშია; რეალური OS service deployment, scheduler/cron და workflow engine-ის უწყვეტ supervisor integration, multi-host distributed execution და გარე source connectors ჯერ არ არის დამატებული.

## შემდეგი ტექნიკური ფენები — კვლევის დაწყების გარეშე

- scheduler/cron integration და workflow engine-ის მუდმივი კავშირი WorkerSupervisor-თან;
- service deployment, watchdog და restart policy;
- source connector registry, provenance, rate limits და per-source permission evidence;
- scheduler, bounded concurrency, quotas და back-pressure;
- metrics, structured logs, alerts, backup/restore და recovery drill;
- უსაფრთხო secrets integration და კერძო drafts storage;
- multi-host execution მხოლოდ მაშინ, როცა შესაბამისი სერვერი/ინფრასტრუქტურა რეალურად განისაზღვრება და ტესტირდება.
