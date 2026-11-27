# NOEMA Service — Linux deployment

## რა მუშაობს ამ ვერსიაში

`python -m noema_core.service` უშვებს ერთჰოსტიან NOEMA runtime-ს და აერთიანებს:

- მდგრად SQLite job queue-ს;
- მხოლოდ trusted `HandlerRegistry`-ში დარეგისტრირებულ handler-ებს;
- dependency-aware Workflow Engine-ს;
- ინტერვალურ Scheduler-ს;
- Worker Supervisor-ს graceful shutdown-ით და შეზღუდული error backoff-ით.

ამ build-ში CLI წინასწარ არეგისტრირებს მხოლოდ სამ ადგილობრივ self-check handler-ს: mission configuration validation, SQLite/audit integrity check და runtime environment report. ისინი ყოველ 300 წამში სრულდება (შეიძლება ინტერვალის შეცვლა გაშვების პარამეტრით). **ეს ჯერ არ არის გარე ინფორმაციის მოძიების ან ახალი კვლევის ავტომატური სისტემა** — გარე წყაროების connector-ები და მათი permission/provenance მოდული ცალკე ტექნიკური ფენებია.

## სწრაფი შემოწმება

Python 3.11+ რეკომენდებულია; runtime იყენებს Python-ის სტანდარტულ ბიბლიოთეკას და ამ service bootstrap-ს დამატებითი pip პაკეტები არ სჭირდება.

Repository root-იდან გაუშვი:

```bash
python -m noema_core.service --check --db /tmp/noema-check.sqlite3
```

შემოწმება ქმნის/ამოწმებს ადგილობრივ DB-ს, mission policy-სა და built-in self-check schedule-ს. წარმატებისას აბრუნებს JSON health report-ს და exit code 0-ს; ხარვეზისას — არანულოვან exit code-ს.

სერვისის foreground რეჟიმში გასაშვებად:

```bash
python -m noema_core.service --db ~/.noema/noema-jobs.sqlite3
```

სერვისი იღებს SIGINT/SIGTERM სიგნალს და ითხოვს graceful stop-ს. სამუშაოს დამუშავების დროს handler-ს ეძლევა დასრულების საშუალება; ხანგრძლივმა handler-მა პერიოდულად უნდა განაახლოს lease heartbeat.

## systemd ინსტალაცია

ქვემოთ მოცემული გზა განკუთვნილია Linux ჰოსტისთვის, სადაც repository მოთავსებულია `/opt/noema`-ში.

1. შექმენი დამოუკიდებელი სისტემური მომხმარებელი და კოდის დირექტორია:

```bash
sudo useradd --system --home-dir /var/lib/noema --create-home --shell /usr/sbin/nologin noema
sudo install -d -o noema -g noema -m 0750 /opt/noema
sudo -u noema git clone https://github.com/maisuradzee/bibmom.git /opt/noema
```

2. შექმენი virtual environment:

```bash
sudo -u noema python3 -m venv /opt/noema/.venv
```

3. შეამოწმე runtime service-ის კონფიგურაცია:

```bash
sudo -u noema /opt/noema/.venv/bin/python -m noema_core.service \
  --check --db /var/lib/noema/noema-jobs.sqlite3
```

4. დააყენე systemd unit:

```bash
sudo install -o root -g root -m 0644 \
  /opt/noema/deploy/systemd/noema.service \
  /etc/systemd/system/noema.service
sudo systemctl daemon-reload
sudo systemctl enable --now noema.service
```

5. შეამოწმე მდგომარეობა და ლოგები:

```bash
sudo systemctl status noema.service
sudo journalctl -u noema.service -f
```

მომსახურების განახლებისას განაახლე repository-ის კოდი და შემდეგ გაუშვი:

```bash
sudo systemctl restart noema.service
```

## უსაფრთხოება და მიმდინარე საზღვრები

- SQLite DB ნაგულისხმევად ინახება owner-only ფაილური უფლებებით (POSIX `0600`); systemd unit იყენებს `UMask=0077`-ს და მონაცემთა დირექტორიას `/var/lib/noema`-ში.
- DB ამ ეტაპზე დაშიფრული არ არის. არ შეინახო მასში passwords, API tokens, credentials ან სენსიტიური პერსონალური მონაცემები.
- systemd ავტომატურად იწყებს სერვისს boot-ზე და ავარიული exit-ის შემდეგ ხელახლა უშვებს მას (`Restart=on-failure`); დაგეგმილი clean stop სერვისს არ აბრუნებს.
- systemd-ის watchdog heartbeat ამ build-ში არ არის ჩართული; restart policy ეყრდნობა process exit-ს.
- interval scheduler იყენებს წამებით განსაზღვრულ ინტერვალს; cron/calendar expression და timezone-aware wall-clock schedule ჯერ არ არის.
- ერთი ჰოსტის SQLite queue არ არის multi-host distributed queue.
- ამ build-ში მხოლოდ შიდა diagnostics სრულდება. ახალი task type-ის დამატება მოითხოვს trusted handler-ის პროგრამულ რეგისტრაციას; payload-იდან კოდის დინამიკური ჩატვირთვა აკრძალულია.
- Pages deployment აქ არ ნიშნავს სერვისის ავტომატურ ჰოსტინგს. systemd unit უნდა დააყენო შენს მიერ მართულ Linux სერვერზე.
