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


## Run 38 verification

PR #200's exact-head x86-64 and ARM64 workflows uploaded six sanitized JSON reports. The six ZIP digests and six report JSON digests were recomputed and frozen in data/noema-005/experiment-002-summary.json. The sanitizer validated distinct native thread identities for every worker/repetition before removing those IDs and detailed host-build strings.

Legacy unsanitized experiment-002 artifacts from runs 46063057964, 46063057969, 46063291466, 46063291702, 46063405483 and 46063405600 were targeted by cleanup run 46064057021. The final six lists were empty; run 46063405483 had two artifacts deleted and run 46063405600 had four deleted. No raw native thread ID or detailed host-build string was committed.


## Retention and re-verification boundary — 2026-11-28

The six sanitized experiment-002 ZIP artifacts are retained by GitHub Actions until
2026-12-27. The frozen manifest records both ZIP and report-JSON SHA-256 values.
This follow-up rechecked all six ZIP digests against GitHub artifact metadata, but
the connector available for this run exposed artifact metadata rather than ZIP
bytes; the six report-JSON digests were therefore not recomputed again here.
The optional `--artifact-dir` mode in
`scripts/reproduce_noema005_experiment_002.py` verifies ZIP and report bytes when
the archives are supplied. Preserve sanitized reports in a durable, reviewed
public snapshot before artifact expiry if long-term raw-report reproduction is
required. Do not commit unsanitized reports or native thread identifiers.
