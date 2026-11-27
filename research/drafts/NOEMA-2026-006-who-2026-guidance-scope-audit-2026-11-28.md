# AquaSignal — WHO 2026 consolidated guidance: nitrate/nitrite scope audit

- **სტატუსი:** draft
- **ID:** AQUASIGNAL-WHO-2026-THIRD-ADDENDUM-NITRATE-NITRITE-SCOPE
- **თარიღი:** 2026-11-28
- **მტკიცებულების სტატუსი:** FACT · INFERENCE · HYPOTHESIS · UNTESTED IDEA
- **ფარგლები:** international drinking-water guidance; not Georgian legal advice or a local water-quality assessment.

## საკვლევი კითხვა

Does the WHO publication dated 17 June 2026 represent a new nitrate/nitrite chemical reassessment, or does it consolidate an existing fact sheet whose assessment date is older?

## FACT

WHO published the *Guidelines for drinking-water quality: fourth edition incorporating the first, second and third addenda* on 17 June 2026 (ISBN 978-92-4-012122-5). The publication is the current consolidated edition.

The linked Chapter 12 chemical-fact-sheet PDF contains the nitrate/nitrite fact sheet on printed pages 466–472. That fact sheet explicitly gives **assessment date 2016**. It states:
- nitrate: 50 mg/L as nitrate ion;
- nitrite: 3 mg/L as nitrite ion;
- combined nitrate/nitrite: the sum of each concentration divided by its guideline value must not exceed 1;
- conversion factors: 0.226 for nitrate ion to nitrate-nitrogen and 0.304 for nitrite ion to nitrite-nitrogen.

WHO's summary of the 2026 edition highlights updates for small water supplies, water safety plans and sanitary inspections, microbial pathogens, and pesticides used for vector control. It does not identify nitrate/nitrite as a newly reassessed chemical topic.

## INFERENCE

The 2026 consolidated edition is the current WHO publication to cite, but the nitrate/nitrite health assessment should not be described as newly reassessed in 2026. Preserve both dates: consolidated-edition publication date **2026-06-17** and chemical assessment date **2016**.

## GEORGIAN LEGAL SCOPE

WHO guidance is not Georgian law. Government Decree №58/2014 is a separate national legal source; its nitrite value is recorded as 0.2 mg/L as NO2- for water within the decree's scope. The WHO value of 3 mg/L must not replace that national requirement. Raw environmental groundwater, surface water and water supplied for drinking are distinct matrices and legal scopes.

## HYPOTHESIS

AquaSignal can safely calculate the WHO combined ratio only when nitrate and nitrite values are paired to the same sample identifier, collection time and water matrix, and both are reported as the corresponding ions in compatible units.

## UNTESTED IDEA

Add a sample-pair validation layer that rejects mismatched sample IDs, timestamps, matrices, reporting bases, missing QA/QC and unapproved reuse permissions before any combined-ratio calculation.

## DATA AND LIMITATIONS

No paired Georgian nitrate/nitrite sample-level dataset is available in this audit. No combined ratio, local prevalence or compliance result is calculated. The published 0.226 and 0.304 conversion factors are rounded and are not sufficient on their own for a near-threshold legal decision. No raw samples, coordinates or personal data are included.

## Sources

1. WHO, *Guidelines for drinking-water quality: fourth edition incorporating the first, second and third addenda*, 17 June 2026: https://www.who.int/publications/i/item/9789240121225
2. WHO, Chapter 12 chemical fact sheets, nitrate/nitrite, printed pp. 466–472; assessment date 2016: https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/dwq-guidelines-4/gdwq_4ed_with_third-addenda_chemical-fact-sheets.pdf?sfvrsn=77d972e1_5
3. Government of Georgia, Decree №58/2014, 15 January 2014: https://www.matsne.gov.ge/ka/document/view/2196792

## ცვლილებების ისტორია

- 2026-11-28: initial source-scope audit; publication date and chemical assessment date stored separately.
