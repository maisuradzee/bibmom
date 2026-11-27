# NOEMA-2026-007 — Georgia river-basin multi-hazard readiness: source-grounded local case

- **ID:** NOEMA-2026-007 (continuation; no new stream)
- **თარიღი:** 2026-11-27
- **სტატუსი:** draft
- **Evidence classes:** FACT, INFERENCE, HYPOTHESIS and UNTESTED IDEA are separated below
- **Scope:** local application of the global warning-to-action measurement gap

## Research question

What can be measured between official multi-hazard risk planning and feasible, verified protective action in Georgia's river-basin communities, without duplicating or overriding official warning authorities?

## FACT — official source statements

1. On 25 November 2026, Georgia's National Environmental Agency reported a two-day consultation on multi-hazard risk-management plans for seven river basins: Alazani, Iori, Mtkvari, Khrami-Ktsia, Chorokhi-Acharistskali, Enguri and Rioni. The same announcement says the wider programme aims to develop risk-management and mitigation measures for climate-related hazards across eleven river basins. It lists floods, debris flows, avalanches, landslides, droughts, hailstorms and strong winds. Source: [NEA, 25 November 2026](https://nea.gov.ge/En/News/3459).
2. On 16 November 2026, NEA described work on hazard assessment/risk zoning, hydrometeorological observation and forecasting modernization, early-warning mechanisms, a public meteo.gov.ge application, observation-network expansion and improved hazard-information access. It also described sustainability, institutional capacity, regional cooperation and cross-border hydrometeorological data exchange as programme topics. Source: [NEA, 16 November 2026](https://nea.gov.ge/En/News/3457).
3. NEA's Geology Department describes regular spring/autumn geological monitoring in urban settlements and surrounding areas; emergency risk assessment and recommendations for geological hazards; annual bulletins and next-year forecasts; hazard-zoning maps; Tbilisi geological-hazard monitoring; GIS databases/cadastres; and instrumental monitoring at critically active landslide/debris-flow sites. Source: [NEA Geology Department](https://nea.gov.ge/ge/Departments/Geology). The same page also links a 2025 geological-process bulletin with a 2026 forecast.

## INFERENCE — the measurable gap

These sources establish a substantial institutional and planning context. They do not publish basin-by-basin implementation status or the end-to-end warning outcomes needed to estimate last-mile effectiveness. In particular, the announcements do not provide unique exposed-population denominators, timely human receipt, comprehension, feasible action, independently verified protective action, missed/false warning rates or after-action corrective-action closure.

The seven basins discussed at a consultation must not be divided by the eleven-basin programme target to create a progress percentage: consultation scope is not an implementation numerator and the target is not a measured coverage denominator.

The public mobile application is an information channel, not evidence that every exposed person receives, understands or can act on a warning.

## HYPOTHESIS

For a selected basin and hazard, an evaluation layer that binds each official warning event to a geographic scope, issue/validity times, pre-agreed action playbook, responsible institutions and after-action record may reveal where the chain fails: data/forecast, dissemination, timely human receipt, comprehension, feasibility, action or follow-up.

This hypothesis is not yet tested in Georgia with event-level data.

## UNTESTED IDEA — safe pilot design

Start with one authorised basin and one hazard in shadow/evaluation mode only:

- ingest only official warning-event metadata and approved plan/playbook identifiers;
- calculate separate event-level denominators for eligible population, channel delivery, unique timely receipt, comprehension, feasible action and verified action;
- use privacy-reviewed aggregate outputs with small-cell suppression and a trusted release ledger;
- include non-digital channels and accessibility/language measures;
- never send warnings, instruct evacuation, control infrastructure or override the competent authority.

## Data and governance requirements

Before any pilot, obtain:
- the approved basin plan and the responsible authority's warning/action responsibilities;
- permissioned warning-event metadata (unique event ID, hazard, area, issue time, validity, lead time, source and revisions);
- a pre-registered eligible-population denominator and channel coverage definition;
- survey sampling frame, response/non-response handling, comprehension instrument and feasibility/action measures;
- after-action reviews and corrective-action closure records;
- data-controller approval, lawful basis, retention limits and independent privacy review.

No personal, device, message-body, household-location or operational telemetry data was added to the public repository.

## Reproducibility and limitations

The source snapshot is stored in `data/noema-007/georgia-basin-multihazard-2026-11-27.json` with a closed Draft 2020-12 schema. Tests protect the seven-versus-eleven interpretation boundary, hazard taxonomy, explicit absence of last-mile outcome measures and the privacy boundary. The snapshot is a source-grounded inventory, not a risk map, forecast, impact assessment or evidence of programme completion.

No field data, survey, warning-event microdata, plan implementation record or causal evaluation was available in this cycle. Status remains draft pending authorised local data and independent disaster-risk-reduction/privacy review.

## საკვლევი კითხვა

როგორ გაიზომოს ოფიციალური მრავალსაფრთხიანი გაფრთხილებიდან დროულ, გასაგებ და რეალურად შესაძლებელ დამცავ მოქმედებამდე გზა საქართველოს მდინარის აუზებში?

## მეთოდი ან ექსპერიმენტის გეგმა

- გამოიყენე მხოლოდ NEA-ს ოფიციალური განცხადებები და დეპარტამენტის ფუნქციების გვერდი.
- შეინახე წყაროს თარიღი, URL, ზუსტი მტკიცება და მონაცემთა საზღვარი JSON snapshot-ში.
- მკაფიოდ განასხვავე კონსულტაციაზე განხილული 7 აუზი და პროგრამის 11 აუზის მიზანი; არ გამოთვალო მათგან განხორციელების პროცენტი.
- გაუშვი JSON Schema და interpretation/privacy regression tests.

## წყაროები

- [NEA — შვიდი მდინარის აუზის მრავალსაფრთხიანი გეგმების კონსულტაცია, 25.11.2026](https://nea.gov.ge/En/News/3459)
- [NEA — ადრეული გაფრთხილების სისტემების განვითარება, 16.11.2026](https://nea.gov.ge/En/News/3457)
- [NEA — გეოლოგიის დეპარტამენტის ფუნქციები](https://nea.gov.ge/ge/Departments/Geology)

## შემდეგი ნაბიჯები

მიიღე უფლებამოსილი ერთი აუზის გეგმა და warning-event/after-action აგრეგატები; წინასწარ განსაზღვრე eligible-population denominator, survey sampling frame, timely receipt, comprehension, feasibility და verified-action საზომები. ჩაატარე დამოუკიდებელი DRR/privacy review.

## შემოწმების სტატუსი

წყაროების snapshot და ტესტები დაემატა ცალკე research branch-ზე. exact-head quality CI ამ revision-ზე ჯერ pending-ია. საველე მონაცემი, warning-event microdata ან ეფექტიანობის შეფასება არ ჩატარებულა; კვლევა რჩება draft.

## Data-access blocker — 2025 geological bulletin

The NEA Geology Department page links the official 2025 geological-process results and 2026 forecast PDF:
[2025 geological bulletin](https://ftp.mepa.gov.ge/Public/NEA/%E1%83%92%E1%83%94%E1%83%9D%E1%83%9A%E1%83%9D%E1%83%92%E1%83%98%E1%83%A3%E1%83%A0%E1%83%98%20%E1%83%91%E1%83%98%E1%83%A3%E1%83%9A%E1%83%94%E1%83%A2%E1%83%94%E1%83%9C%E1%83%98%202025%20%281%29.pdf).

The linked PDF is 704,801,491 bytes. The retrieval tool rejected it as too large, so the bulletin's contents were not inspected and no hazard counts, locations, forecasts or outcome values have been extracted. This is a retrieval/tool limit, not evidence that the official server is unavailable. The source snapshot records it as `linked_not_fetched`; a smaller official summary, chapter extract or permissioned data export is the next safe route.

## Expanded local spatial-data discovery — official geospatial catalogue

A page-by-page audit of the Ministry's spatial-data inventory identified ten relevant NEA catalogue records. The inventory distinguishes spatial geometry from station-system metadata and model output; it does not provide the feature payloads in the rows inspected.

| ID | Catalogue layer | What the row establishes | Access/interpretation boundary |
|---|---|---|---|
| NEA38 | Main river basin/sub-basin polygons | Public/free; catalogue date 2025-10-16; portal map `/Ge/user/map/16`; six visible technical sub-basin layer names | A map URL exists, but a downloadable feature service, complete layer set and reuse licence are not confirmed |
| NEA54 | Flood-hazard modelling | Public/free; catalogue date 2025-07-28; hydraulic-model assets for arrival time, depth, duration, velocity, water-surface elevation and flood extent; listed return periods 2/5/25/50/100/500 years | SQL SDE storage; no portal map/download endpoint or payload retrieved; model scenarios are not current forecasts |
| NEA55 | Regional avalanche modelling | Public/free; three regions (Northeast, Northwest, Southwest); 30/100/300-year scenarios; with/without-forest scenarios; SHP/TIF asset names | SQL SDE storage; no portal map/download endpoint or payload retrieved |
| NEA56 | Local avalanche modelling by basin/sub-basin | Public/free; 30/100/300-year scenarios; relief, maximum height/pressure, accumulation and velocity asset names | Stored on disks/local computers; separate from NEA55; no payload retrieved; no forest-scenario claim is made |
| NEA57 | Clidata station metadata | Public/free polygon layer `Meteo_Network`; catalogue date 2025-07-28 | Metadata about stations in Clidata, not meteorological time-series observations |
| NEA58 | Aquarius station metadata | Public/free polygon layer `Hydro_Network`; catalogue date 2025-07-28 | Metadata about stations in Aquarius, not hydrological time-series observations |
| NEA65 | Recorded landslide outlines | Public/free polygon layer; catalogue date 2025-07-28 | Recorded outlines are not, by themselves, susceptibility, active movement or a forecast |
| NEA66 | Tbilisi geological-hazard zoning | Public/free polygon layer; scale 1:25,000; catalogue date 2026-03-06 | SQL SDE/local PC; no portal map/download endpoint or payload retrieved |
| NEA123 | Hydrological stations | Public/free point layer for active stations; catalogue date 2026-03-09 | SQL SDE/local PC; exact point features and reuse terms not retrieved |
| NEA124 | Meteorological stations/posts | Public/free point layer for active stations/posts; catalogue date 2026-03-09 | SQL SDE/local PC; exact point features and reuse terms not retrieved |

The official catalogue rows were checked on three pages:
- [Page 2 — flood layers, basin polygons and Tbilisi geology](https://portal.mepa.gov.ge/En/User/data?Links-page=2&Links-sort=Descrioption-desc)
- [Page 5 — avalanche, station metadata and geological layers](https://portal.mepa.gov.ge/En/User/data?Links-page=5&Links-sort=GeoDataId-desc)
- [Page 6 — active hydrological/meteorological station points and landslide layer](https://portal.mepa.gov.ge/En/User/data?Links-page=6&Links-sort=UnitName-desc)

**Important distinctions:** NEA55 is the regional avalanche model; NEA56 is a separate local basin/sub-basin model. NEA57 and NEA58 are station metadata for Clidata and Aquarius, not observation feeds. NEA65 is a recorded-landslide outline layer, not a forecast. NEA54's return periods and model assets are catalogue descriptions, not event probabilities validated for a particular place or a current warning.

The rows classify these layers as public/free, but this is not an open-data licence. A portal map for NEA38 is not proof of direct feature download. No payload, coordinates, CRS, model rasters, time series, update cadence or reuse permission was obtained. The snapshot stores catalogue metadata only and intentionally contains no household, station-coordinate or event-level operational records.
