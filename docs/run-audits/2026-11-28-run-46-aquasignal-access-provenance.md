# Run 46 — AquaSignal official report link provenance

- **Date:** 2026-11-28
- **Stream:** NOEMA-2026-006 / AquaSignal
- **Evidence status:** FACT for the announcement page and its linked payload URL; UNTESTED for archive contents and reuse rights.

## Research question

Can the 2021–2025 NEA groundwater report be linked to its official announcement and payload without implying that the archive itself has been inspected?

## Findings

- **FACT:** The National Environmental Agency's 2026-11-26 announcement page is https://www.nea.gov.ge/Ge/News/3461.
- **FACT:** The announcement page links a RAR payload hosted under the official MEPA FTP domain. The exact payload URL is retained in the source-access inventory.
- **FACT:** The source-access inventory already distinguishes the announcement from the archive payload; this run adds an explicit `announcement_url` relation to the payload record.
- **INFERENCE:** Explicitly linking the page and payload improves provenance and makes future hash/retrieval checks reproducible.
- **UNTESTED:** The archive's internal file list, report contents, sample-level fields, data dictionary, archive SHA-256, acceptance/delivery status and reuse terms.

## Method

1. Re-opened the official NEA announcement page.
2. Followed the linked RAR payload reference.
3. Did not extract or publish the archive.
4. Updated only public-source metadata, schema, regression tests, portfolio and project status.

## Safety and limitations

The public repository contains only the official page URL, the already-public payload URL and retrieval-status metadata. It contains no archive bytes, raw water measurements, well-owner details, private coordinates or credentials. A retrieval limitation in this execution environment is not evidence that the official host is generally unavailable.

## Next step

Obtain the RAR through an authorized route, compute its SHA-256 before extraction, inspect the internal file list and licence/reuse terms, and publish only a de-identified public schema or aggregate methodology if permitted. Keep sample-level data private unless explicit public reuse rights are established.
