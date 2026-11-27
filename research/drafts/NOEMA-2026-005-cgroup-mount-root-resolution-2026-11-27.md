# NOEMA-2026-005 — cgroup v2 mount-root path resolution hardening

- **ID:** NOEMA-2026-005-CGROUP-MOUNT-ROOT-001
- **სტატუსი:** draft engineering validation
- **თარიღი:** 2026-11-27
- **სფერო:** benchmark environment provenance · cgroup v2 path resolution

## საკვლევი კითხვა

შეუძლია თუ არა benchmark-ის cgroup v2 resolver-ს `/proc/self/cgroup` membership path-ის cgroup2 mount-ში გადატანა mount-ის გამოცხადებული root-ისა და mount point-ის გამოყენებით ისე, რომ sibling-prefix და path-traversal alias-ები უარყოს?

## მეთოდი ან ექსპერიმენტის გეგმა

Path mapping ამოღებულია ცალკე pure helper-ში — `_relative_cgroup_path(membership, mount_root)`. helper აბრუნებს mount-relative path-ს მხოლოდ მაშინ, როცა membership ზუსტად ემთხვევა mount root-ს ან მისი segment-delimited descendant-ია. ტესტები ფარავს:

- cgroup2 mount root-ს `/`-ზე;
- non-root bind/subtree mount root-ს;
- membership-ის ზუსტ დამთხვევას;
- sibling სახელებს საერთო ტექსტური prefix-ით (`/system.slice2` და `/system.slice`);
- relative, repeated-separator და parent-traversal input-ებს;
- mountinfo-ში escaped space, tab, newline, hash და backslash ველებს; escaped backslash-ის შემდეგ literal `\\012` მიმდევრობაც ხელუხლებლად რჩება.

ეს helper არ კითხულობს system files-ს, არ პოულობს mount-ებს და არ ადგენს CPU capacity-ს.

## მტკიცებულებები

- **FACT:** `/proc/<pid>/mountinfo`-ის field 4 აღწერს mount-ის root-ს filesystem-ში, ხოლო field 5 — mount point-ს process root-ის მიმართ. Linux man-pages, `proc_pid_mountinfo(5)`: https://man7.org/linux/man-pages/man5/proc_pid_mountinfo.5.html
- **FACT:** cgroup v2-ის `cpu.max` და `cpuset.cpus.effective` სხვადასხვა CPU კონტროლისა და ხელმისაწვდომობის ინტერფეისებია. Linux kernel documentation: https://docs.kernel.org/admin-guide/cgroup-v2.html
- **INFERENCE:** segment-aware mapping ამცირებს იმის რისკს, რომ ტექსტური sibling-prefix-ის დამთხვევამ არასწორი cgroup directory მოაგვაროს.
- **REPRODUCED RESULT:** დამატებული unit tests ამოწმებს pure mapping helper-ს; ისინი არ წარმოადგენს live mount-namespace ტესტს ან ახალ timing benchmark-ს.
- **HYPOTHESIS:** path mapping-ის ცალკე ტესტები benchmark-ის environment provenance-ს უფრო აუდიტირებადს ხდის bind mount-ებისა და container mount namespace-ების პირობებში.

## შეზღუდვები და გაურკვევლობები

- ცვლილების ფარგლებში cgroup mount namespace არ შექმნილა ან შეცვლილა.
- ფიზიკურ მოწყობილობაზე გამეორება არ ჩატარებულა.
- ახალი CPU/wall გაზომვა არ არის წარმოდგენილი.
- ძველი 13.287713 anomaly კვლავ აუხსნელია; ეს ცვლილება მის მიზეზს არ ადგენს.
- CPU capacity კვლავ არ გამოითვლება, თუ worker membership ან ancestor quota evidence არასრულია.

## წყაროები

1. Linux kernel source, `fs/proc_namespace.c`, `mangle()` and `show_mountinfo()`: https://github.com/torvalds/linux/blob/master/fs/proc_namespace.c — the current implementation escapes space, tab, newline, backslash and hash in mount paths.
2. Linux kernel documentation, `seq_file` — `seq_escape()` emits escaped characters in octal form: https://docs.kernel.org/next/filesystems/seq_file.html
3. Linux man-pages project. `proc_pid_mountinfo(5)` — field 4 mount root and field 5 process-relative mount point: https://man7.org/linux/man-pages/man5/proc_pid_mountinfo.5.html
4. Linux kernel documentation. Control Group v2: https://docs.kernel.org/admin-guide/cgroup-v2.html

## შემდეგი ნაბიჯები

1. გაუშვი exact-head Quality CI და არსებული CPU/wall diagnostic workflow.
2. ახალი hosted artifact გააანალიზე ცალკე და არ ჩაანაცვლო გაყინული ძველი ჩანაწერები.
3. გაიმეორე ექსპერიმენტი დამოუკიდებლად კონტროლირებულ ფიზიკურ x86-64 და ARM64 მოწყობილობებზე, external task-clock/context-switch მტკიცებულებით.

## შემოწმების სტატუსი

- **კოდი:** pure path-mapping helper და segment/traversal regression tests დამატებულია.
- **Frozen შედეგები:** ძველი raw archives უცვლელია; ამ PR-ში ახალი frozen შედეგი არ შექმნილა.
- **Benchmark:** ახალი შედეგი მხოლოდ შესაბამისი CI workflow-ის დასრულების შემდეგ შეფასდება.
- **Publication:** Draft; დამოუკიდებელი benchmark-method review და ფიზიკური მოწყობილობების გამეორება ჯერ არ ჩატარებულა.
