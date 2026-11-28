# NOEMA-2026-007 — Georgia warning authority and capability crosswalk

- **ID:** NOEMA-2026-007 (continuation; no new stream)
- **თარიღი:** 2026-11-28
- **სტატუსი:** draft
- **Evidence classes:** FACT, INFERENCE, HYPOTHESIS and UNTESTED IDEA
- **Scope:** official Georgian institutional roles and public early-warning capability signals

## საკვლევი კითხვა

What do Georgia's official public sources establish about the National Environmental Agency's warning, hydrological observation and geological monitoring responsibilities, and what remains unknown about network coverage and the end-to-end warning-to-action chain?

## Human benefit and priority

- **Potential beneficiaries:** communities exposed to floods, landslides, debris flows, avalanches, drought and other hydrometeorological/geological hazards; local and central decision-makers.
- **Potential scale:** national institutional scope, but exposed-population coverage is not measured by the sources reviewed.
- **Urgency:** potentially high because hazard warnings are time-sensitive; current operational effectiveness cannot be ranked without event-level data.
- **Potential benefit mechanism:** clearer source/authority provenance and separate warning-chain denominators can help identify whether the limiting stage is observation, forecast, issuance, dissemination, receipt, comprehension or feasible action.
- **Success measure:** versioned station inventory and forecast verification plus separately denominated warning issuance, delivery, acknowledgement, comprehension, feasible action and verified protective action.

## FACT — official source statements

1. NEA's public functions page says the Agency establishes monitoring systems for meteorological, hydrological, geological and environmental processes; collects and disseminates monitoring data; produces forecasts and issues warnings within its competence; and provides warning information to central and local authorities and mass media. It also lists hazard monitoring, risk assessment and participation in preventive/risk-reduction measures. Source: [NEA — Agency's functions](https://www.nea.gov.ge/En/Functions).
2. The Hydrology Department page lists stationary surface-water observation-network oversight, hydrological forecasts, preparation and dissemination of warnings about expected hydrological events to decision-makers, interested persons/legal entities and mass media, and GIS/data-quality work. Source: [NEA — Hydrology Department](https://nea.gov.ge/en/Departments/Hydrology).
3. The Geology Department page lists regular geological monitoring, landslide/debris-flow monitoring, hazard-zoning maps, GIS catalogues, instrumental monitoring in extremely sensitive areas, fresh-drinking-groundwater monitoring and annual hydrogeological bulletins. Source: [NEA — Geology Department](https://nea.gov.ge/En/Departments/Geology).
4. On 14 July 2026, NEA reported 278 hydrometeorological stations already installed and a target of 298 stations/watchpoints by the end of 2026. The same notice describes online transmission and an ICT system for collection, processing, analysis and warning dissemination. It also reports modern monitoring systems on 28 landslide bodies, 22 of which were integrated into one server platform. Source: [NEA — hydrometeorological network expansion](https://nea.gov.ge/En/News/2419).
5. On 26 December 2025, NEA reported a workshop where proposals for national multi-hazard forecasting platforms and early-warning protocols were discussed. The notice documents a discussion and project direction, not formal protocol adoption. Source: [NEA — multi-hazard forecasting and early-warning workshop](https://nea.gov.ge/En/News/2360).

## Evidence classification

### FACT

- The Agency and department pages describe institutional functions and responsibilities.
- The 278 installed stations and 298 year-end target are agency-reported figures as of the 14 July 2026 notice; the target is not an observed result.
- The 28 landslide-body and 22 platform-integration counts are separate agency-reported infrastructure figures.
- The 2025 workshop is evidence that proposals were discussed, not that a final national protocol was adopted.

### INFERENCE

- The public sources establish institutional and technical capability signals, but not the completeness, reliability or equitable reach of the warning chain.
- Station counts, landslide-monitoring bodies and platform integrations measure different outputs and must not be combined into one coverage percentage.
- The next decision-relevant step is to connect an authorised warning event to its issuing authority, forecast/station provenance, dissemination stages and feasible protective-action evidence.

### HYPOTHESIS

A versioned, metadata-only authority and capability crosswalk linked to each authorised warning event could make missing ownership, provenance and warning-chain stages easier to identify without duplicating official warning issuance.

### UNTESTED IDEA

Build a read-only warning-event evidence registry containing official reference IDs, authority, hazard, coarse area, issue/validity timestamps, source version, playbook version and aggregate stage denominators. Personal delivery telemetry and household locations must remain outside the public system.

## მეთოდი ან ექსპერიმენტის გეგმა

- Method: source-by-source extraction from official NEA public pages and notices; preserve publication/access dates and exact claim boundaries in a closed JSON record.
- Reproduction: no quantitative experiment was performed. The numeric claims are copied as agency-reported figures, not independently measured by NOEMA.
- Validation: Draft 2020-12 schema plus regression tests ensure the 298 figure remains a target, the 278 figure retains its 14 July 2026 as-of date, the 28/22 landslide figures remain separate, and no operational-performance or last-mile claim is invented.
- Exclusions: no station coordinates, private locations, app telemetry, person-level warnings, operational records or critical-infrastructure geometry were collected.

## What is not established

- The 298 year-end target was not independently checked as achieved by 28 November 2026.
- No current station inventory, hazard/region coverage, active dates, uptime, calibration, telemetry completeness or maintenance data were retrieved.
- No hazard-specific forecast skill, lead-time, probability-of-detection, false-alarm or uncertainty metrics were retrieved.
- No denominators were found for warnings issued, sent, delivered, acknowledged, understood, feasible or actioned.
- No app active-user, accessibility, language-coverage or offline-channel metrics were published in the inspected sources.
- Formal adoption, funding, operationalization and independent evaluation of the 2025 workshop proposals were not established.

## Innovation / practical design

A future read-only warning-event evidence registry should bind:
- issuing authority and official warning reference;
- hazard and coarse geographic area;
- issue, validity and revision timestamps;
- station/forecast provenance and model version;
- pre-agreed action-playbook identifier;
- separate aggregate denominators for each warning-chain stage;
- after-action review and corrective-action closure.

It must not issue warnings, recommend evacuation, control infrastructure or override competent authorities. Public releases require data-controller approval, independent privacy review, coarse geography and small-cell suppression. The registry is a design proposal, not a deployed operational service.

## შემდეგი ნაბიჯები

1. Obtain a versioned station inventory with active dates, hazard/region coverage, uptime, telemetry completeness, calibration and maintenance metadata.
2. Obtain hazard-specific forecast verification and lead-time distributions.
3. Verify the approved version and effective date of any national multi-hazard early-warning protocol.
4. Obtain privacy-approved aggregate warning-event and after-action data with distinct denominators for delivery, comprehension, feasibility and verified action.
5. Independently review the measurement design with disaster-risk-reduction and privacy specialists.

## შემოწმების სტატუსი

Draft. The source inventory is primary-source documentary work. The numerical capacity figures are agency-reported, not independently audited. No field study, operational warning-chain dataset, causal evaluation or independent peer review was completed. This is not a national warning-system performance assessment.

## წყაროები

- [NEA — Agency's functions](https://www.nea.gov.ge/En/Functions)
- [NEA — Hydrology Department](https://nea.gov.ge/en/Departments/Hydrology)
- [NEA — Geology Department](https://nea.gov.ge/En/Departments/Geology)
- [NEA — hydrometeorological network expansion, 14 July 2026](https://nea.gov.ge/En/News/2419)
- [NEA — multi-hazard forecasting and early-warning workshop, 26 December 2025](https://nea.gov.ge/En/News/2360)

## Change history

- 2026-11-28 — added official agency/department responsibility crosswalk and preserved station/platform counts with their original qualifiers.
