# NOEMA-2026-006 — NEA 2021 hydrogeological bulletin: additional official access lead

- **ID:** NOEMA-2026-006
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** groundwater monitoring · source discovery · data provenance
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

Does the NEA's official geology bulletin index expose a distinct historical groundwater report that can serve as a source-access lead without being confused with the newly announced 2021–2025 archive?

## FACT — official listing

The National Environmental Agency's official Geology bulletin index lists **“2021 წლის საინფორმაციო ჰიდროგეოლოგიური ანგარიში”** under November 2021 and exposes a download link.

- Official index: https://nea.gov.ge/weather/Departments/Geology/Biulettins
- Linked file endpoint: https://nea.gov.ge/weather/Download/File/1183

The index listing is distinct from the 2026-11-26 announcement of a separate report covering the 2021–2025 observation period. These two records must not be treated as the same document or dataset.

## REPRODUCED RESULT — retrieval boundary

The web reader followed the official download link but rejected the response because its reported content length was 22,990,164 bytes, above the reader's limit. A container-side direct retrieval attempt failed at DNS resolution in this execution environment.

The PDF bytes were not retrieved or inspected. No page count, table, station list, sample count, observation result, SHA-256, licence or reuse permission is claimed.

## INFERENCE

The bulletin index provides a second official access route for a historical 2021 hydrogeological report. If the payload and methods can later be inspected, it may help establish a historical comparison baseline. That comparison is not currently possible because the report's internal definitions, station identifiers, sampling frame and methods have not been verified.

## HYPOTHESIS

A versioned archive of official hydrogeological bulletins, each paired with a stable station dictionary and explicit reuse terms, could reduce the risk of conflating network counts, sampling frames and observation periods in AquaSignal.

## მეთოდი ან ექსპერიმენტის გეგმა

- Open the official NEA bulletin index.
- Follow only the official download link for the November 2021 report.
- Record the listing title, month, URL and retrieval boundary.
- Keep the historical bulletin separate from the 2021–2025 RAR announcement.
- Do not extract or publish any observations until the file is obtained, provenance is hashed, schema is inspected and reuse conditions are verified.

## შეზღუდვები და უსაფრთხოება

- No PDF bytes were retrieved; the index metadata is the only inspected evidence.
- The retrieval failure is specific to this execution environment and does not prove that the NEA server is generally unavailable.
- No raw water observations, coordinates, private-well owner details, health records or personal data were added.
- The public listing does not establish a licence for reuse.

## შემდეგი ნაბიჯები

1. Obtain the PDF through an official alternate route or authorised direct download.
2. Compute and record its SHA-256 before inspection.
3. Extract only public report metadata and aggregate values after confirming reuse conditions.
4. Compare with the 2021–2025 report only after checking definitions, sampling frames and stable station identifiers.

## შემოწმების სტატუსი

- FACT: official NEA index lists the November 2021 hydrogeological bulletin and links a file.
- REPRODUCED RESULT: the reader's size-limit failure and local DNS retrieval failure were observed; no file-content reproduction occurred.
- INFERENCE: this is an additional official historical access lead, not evidence of sample-level availability.
- UNTESTED IDEA: a harmonised, versioned groundwater-bulletin archive.

## წყაროები

- National Environmental Agency of Georgia. *2021 წლის საინფორმაციო ჰიდროგეოლოგიური ანგარიში* (November 2021 listing). https://nea.gov.ge/weather/Departments/Geology/Biulettins
- National Environmental Agency of Georgia. Linked file endpoint. https://nea.gov.ge/weather/Download/File/1183

## ცვლილებების ისტორია

- 2026-11-27: initial metadata-only discovery record.
