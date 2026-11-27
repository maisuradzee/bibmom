# NOEMA-2026-005 — cgroup v2 mount-root path resolution hardening

- **ID:** NOEMA-2026-005-CGROUP-MOUNT-ROOT-001
- **Status:** draft engineering validation
- **Date:** 2026-11-27
- **Scope:** benchmark environment provenance; cgroup v2 membership-to-mount mapping

## Research question

Can the benchmark's cgroup v2 resolver map the membership path from `/proc/self/cgroup` into a cgroup2 mount using the mount's declared root and mount point, while rejecting sibling-prefix and path-traversal aliases?

## Change

The path-prefix logic has been extracted into a pure helper, `_relative_cgroup_path(membership, mount_root)`, and the resolver now uses that helper. Synthetic tests cover:

- a cgroup2 mount rooted at `/`;
- a bind/subtree mount with a non-root mount root;
- exact membership-to-mount-root equality;
- sibling names sharing a textual prefix (for example `/system.slice2` versus `/system.slice`);
- relative and parent-traversal inputs;
- mountinfo escaped space, tab and backslash fields.

The helper does not read system files, discover mounts, or infer CPU capacity. It only returns a relative path when the membership is exactly the mount root or a segment-delimited descendant.

## Evidence classification

- **FACT:** `/proc/<pid>/mountinfo` field 4 describes the root of the mount within the filesystem and field 5 describes the mount point relative to the process root. Linux man-pages, `proc_pid_mountinfo(5)`: https://man7.org/linux/man-pages/man5/proc_pid_mountinfo.5.html
- **FACT:** cgroup v2 exposes `cpu.max` and `cpuset.cpus.effective` as distinct CPU-control/capacity interfaces. Linux kernel cgroup v2 documentation: https://docs.kernel.org/admin-guide/cgroup-v2.html
- **INFERENCE:** segment-delimited mapping tests reduce the chance that a textual sibling-prefix match resolves the wrong cgroup directory.
- **REPRODUCED RESULT:** the added unit tests exercise the pure mapping helper. They do not constitute a new timing benchmark or a live mount-namespace test.
- **HYPOTHESIS:** explicit path mapping tests make the benchmark's environment provenance easier to audit across bind mounts and container mount namespaces.

## Limitations

- No cgroup mount namespace was created or altered by this change.
- No physical-host replication was performed.
- No new CPU/wall measurement is claimed.
- The existing archived 13.287713 anomaly remains unresolved; this change does not explain it.
- CPU capacity is still withheld when worker membership or ancestor quota evidence is incomplete.

## Next steps

Run the existing exact-head cgroup timing workflow, inspect the new hosted artifact separately from frozen archives, then repeat on independently controlled physical x86-64 and ARM64 hosts with external task-clock/context-switch evidence.
