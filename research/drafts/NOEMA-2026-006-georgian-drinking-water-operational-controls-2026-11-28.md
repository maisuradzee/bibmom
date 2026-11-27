# NOEMA-2026-006 — AquaSignal: Georgian drinking-water monitoring control points and response duties

- **ID:** AQUASIGNAL-GEORGIAN-DRINKING-WATER-CONTROLS-2026-11-28
- **ID:** AQUASIGNAL-GEORGIAN-DRINKING-WATER-CONTROLS-2026-11-28
- **სტატუსი:** draft
- **მტკიცებულების სტატუსი:** FACT, INFERENCE, HYPOTHESIS, UNTESTED IDEA
- **თარიღი:** 2026-11-28
- **სფერო:** საქართველო · სასმელი წყლის ხარისხის კონტროლი · სინჯის წერტილები · მიმწოდებლის რეაგირება
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

Which operational sampling points, monitoring duties and response triggers does Georgia's official drinking-water technical regulation define, and how should AquaSignal represent them without confusing raw groundwater observations with compliance at a consumer point?

## ადამიანური სარგებელი და პრიორიტეტი

A correct sampling-point model helps prevent a common category error: a groundwater observation is not automatically evidence of the water delivered at a household tap, a tank outlet, a bottle filling line or a food-production water point. Explicit response and repeat-sampling triggers can also help preserve the chain from an initial signal to confirmatory testing and protective action.

## FACT — ოფიციალური სამართლებრივი ტექსტი

The Legislative Herald's official text of Government Decree №58/2014 states:

1. The regulation covers natural or treated water used for drinking, food preparation and other domestic purposes, and water intended for food or food-product production (Article 1(2)).
2. Monitoring points differ by supply mode: a normally used consumer tap inside a building for a distribution system; the outlet for a tank/cistern; the filling point and retail network for bottled/container water; and water-supply points in food production (Article 1(5)).
3. Suppliers must monitor compliance, record results and make information accessible. When non-compliance is identified, they must inform relevant services, immediately investigate the contamination cause, restrict supply where required and take other public-health protection measures (Articles 1(6)-(7)).
4. Floods and emergencies require enhanced drinking-water quality control in coordination with competent state authorities (Article 3(4)).
5. Following detection of total coliforms and/or E. coli, the regulation describes repeat sampling and simultaneous determination of chlorides, nitrates and nitrites (Article 3(6)).
6. Routine laboratory monitoring includes organoleptic, microbiological and chemical parameters. The chemical list includes pH, ammonia, nitrate, nitrite, chlorides, oxidizability and residual chlorine (Article 3(9)).
7. Drinking-water testing is to be performed in an accredited independent laboratory in accordance with law (Article 4(2)).

Official source: https://matsne.gov.ge/ka/document/view/2196792

## INFERENCE — მნიშვნელობა AquaSignal-ისთვის

AquaSignal should store at least four distinct concepts rather than one generic “water sample”:
- source/matrix (raw groundwater, treated supply, distribution network, tank/cistern, bottled/container, food-production water);
- legal sampling point for the relevant supply mode;
- laboratory result provenance (method, unit, detection limit, QA/QC and accredited-lab status);
- response state (initial signal, repeat sample requested, confirmatory result, supplier/authority notification, protective action and closure).

A raw-groundwater result should not be labeled as consumer-tap compliance unless the sample matrix and point satisfy the relevant legal scope.

## HYPOTHESIS — შემოწმებადი ოპერაციული ღირებულება

If AquaSignal links abnormal results to a documented repeat-sampling trigger, the confirmatory analyte panel and a time-stamped response record, it may reduce the time between an initial signal and a verified response. This hypothesis requires real, authorized supplier/laboratory workflow data and cannot be tested from the legal text alone.

## UNTESTED IDEA — პროტოტიპის იდეა

A privacy-preserving event ledger could represent:
- sample ID and coarse area only;
- matrix and supply mode;
- legally relevant sampling-point class;
- analyte, result, unit, detection limit, method and QA/QC;
- lab accreditation reference;
- repeat-sample parent/child relation;
- notification and response timestamps;
- public release state after disclosure review.

No production system or field deployment is claimed.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Opened the official Matsne PDF/text for Decree №58/2014 on 2026-11-28.
2. Mapped the specific requirements in Articles 1(2)-(3), 1(5)-(7), 3(4), 3(6), 3(9) and 4(2) into a closed JSON Schema.
3. Added deterministic tests for sampling-point separation, supplier duties, emergency and repeat-sampling triggers, routine analytes and privacy limits.
4. Did not infer actual sampling frequency, supplier performance, non-compliance prevalence or laboratory outcomes from legal obligations.

## სამართლებრივი გარდამავალი პერიოდი და შეზღუდვები

A 2026-06-24 amendment to the Law on Water Resources Management sets 2027-09-01 milestones for relevant methodology approval and groundwater nitrate-risk-zone identification: https://manage.matsne.gov.ge/ka/document/view/6904700

The transitional/repeal status of Decree №58/2014 after adoption of a replacement drinking-water regulation must be checked against the then-current consolidated law. This record does not assert a future in-force date and is not legal advice.

Other limits:
- The regulation's drinking-water scope does not automatically cover all raw groundwater or every private source.
- Legal obligations do not prove that a supplier actually performed monitoring or protective action.
- No sample records, supplier identities, coordinates, compliance results or exposure estimates are included.
- Operational usefulness requires authorized data access and independent legal/scientific review.

## ინოვაციის მიღების კრიტერიუმები

A prototype is useful only if it:
1. rejects matrix/sampling-point mismatches;
2. preserves unit, analyte basis and detection limit;
3. distinguishes initial from repeat samples;
4. records independent-lab provenance;
5. cannot mark a protective action as verified without evidence;
6. releases only disclosure-reviewed aggregates.

## შემოწმების სტატუსი

- Official source opened: PASS.
- Legal control points transcribed into structured metadata: PASS.
- JSON Schema and regression tests: added in the research branch.
- Real-world supplier compliance or water-quality results: NOT TESTED.
- Independent legal review and field validation: pending.
- Publication: draft; not Published.


## წყაროები

1. Legislative Herald of Georgia, Government Decree №58/2014, 2014-01-15, Articles 1(2)-(3), 1(5)-(7), 3(4), 3(6), 3(9), 4(2): https://matsne.gov.ge/ka/document/view/2196792
2. Legislative Herald of Georgia, Law amendment dated 2026-06-24, document 6904700, including 2027-09-01 statutory milestones: https://manage.matsne.gov.ge/ka/document/view/6904700


## შემდეგი ნაბიჯები

1. Obtain independent Georgian legal review of the current consolidated text and the transition/repeal date for Decree №58/2014.
2. Obtain authorized supplier/laboratory workflow documentation before designing any operational integration.
3. Test the sampling-point model against a privacy-safe, non-identifying example dataset with explicit matrix and denominator fields.
4. Keep the prototype non-operational until independent laboratory provenance, notification authority and protective-action evidence are verified.
