# NOEMA-005 public benchmark artifact boundary

The benchmark runs collect raw native thread IDs and detailed runtime/platform
strings only in the ephemeral hosted runner workspace. The raw report is
validated there, then passed through the sanitizer script before any Actions
artifact or step-summary publication.

The sanitizer requires, for every measured case, the configured worker count
to match the number of distinct native thread IDs in every repetition. It then
removes the raw IDs and detailed host-build strings, retaining only:
- coarse architecture (x86_64 or arm64);
- a generic github-hosted runner-family label;
- CPython version and GIL mode;
- process-visible CPU count;
- a boolean that native-thread identity validation succeeded.

The sanitization marker is provenance metadata, not an attestation signed by
GitHub. It does not prove hardware identity, eliminate VM-level confounding,
or turn hosted results into physical-device replication. Raw IDs and full
platform strings must never be uploaded as public artifacts or written to the
public step summary.

A cleanup workflow targets the known experiment-002 runs that uploaded
unsanitized artifacts before this boundary was added. Deletion is reported
only after GitHub confirms the artifact list is empty.
