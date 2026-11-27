# NOEMA-2026-007 — Georgia heat-health readiness

- **ID:** NOEMA-2026-007
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** public health · extreme heat · early warning · privacy-preserving measurement
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

Can Georgia's existing official meteorological warning channel be evaluated alongside authorized, privacy-preserving heat-exposure and maternal/newborn/child health indicators, so health authorities can identify preparedness gaps without creating a duplicate warning service or collecting individual app/health telemetry?

## მოკლე შეჯამება

This addendum identifies a high-value measurement opportunity at the intersection of extreme heat, official warnings and maternal/newborn/child health. It records official Georgian warning-channel and app-privacy evidence, a new WHO/WMO/UNICEF/UNFPA indicator framework, and a cautious measurement design. It does not claim that Georgia lacks a heat-health plan, that health outcomes are already integrated with NEA warnings, or that a local health burden has been quantified.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

WHO describes rapid health impacts during and immediately after extreme heat and recommends heat-health action plans and early-warning systems. Its 2026 joint indicator framework highlights monitoring gaps for pregnant/postpartum women, newborns and children. A well-designed measurement layer could help authorized health authorities examine whether warnings, exposure and routine health surveillance are aligned, while avoiding a parallel public-warning channel.

## არსებული ცოდნა და წყაროები

- **FACT — NEA warning capability:** on 2026-06-11, the National Environmental Agency (NEA) described its ICT system as collecting, processing and analysing information from multiple sources and disseminating relevant warnings, with a weather/hydrometeorological warning app.
- **FACT — app privacy boundary:** NEA's official notice says the app displays weather information, forecasts, warnings and maps without registration. It may use selected/current location (current location only with permission), device IP, request date/time and technical logs. The notice says it does not collect names, personal numbers, email addresses, phone numbers, passwords or profile data.
- **FACT — international health indicators:** WHO/WMO/UNICEF/UNFPA published priority indicators for maternal, newborn and child health under heat exposure on 2026-10-21. The domains include routine MNCH monitoring, public-health surveillance, climate-and-health monitoring and heat-exposure measurement.
- **FACT — global heat context:** WHO's 2026-07-31 fact sheet describes heat as an environmental and occupational health hazard and provides global estimates and vulnerability factors. Those global estimates are not Georgian baselines.
- **SECONDARY SIGNAL:** 1TV reported NCDC/Ministry public heat recommendations on 2026-08-03. The primary NCDC release was not independently retrieved; this media report is not treated as an official technical guideline or proof of a formal national heat-health action plan.

## მტკიცებულებები

### FACT

1. NEA publicly describes a multi-source ICT early-warning system and a weather-warning application.
2. NEA publishes an app privacy notice that describes selected/current location, IP, request time and technical logs as possible app data.
3. WHO/WMO/UNICEF/UNFPA published a joint MNCH heat-indicator framework on 2026-10-21.
4. WHO's 2026-07-31 fact sheet identifies rapid heat-health impacts and vulnerable groups, but its global figures do not quantify Georgia.

### INFERENCE

These sources create a practical opportunity to evaluate the connection between meteorological warnings, heat exposure and health-sector readiness. They do not establish that the connection is currently absent or present in Georgia.

## კონკურენტი ახსნები

- Georgia may already have heat-health coordination or action plans that are not visible in the sources reviewed.
- NEA's multi-hazard ICT system may include heat-relevant warnings even if the public announcement does not describe a health-specific protocol.
- A lack of public aggregate health data may reflect privacy or publication policy rather than a lack of internal surveillance.
- Observed changes in health indicators during hot periods may be driven by seasonality, air pollution, infection, demographic change, care access or reporting delays.

## ჰიპოთეზა

An aggregate-only linkage of official warning metadata, daily heat exposure and authorized routine health indicators may help authorities identify unusual heat-period patterns and preparedness gaps without tracking individuals.

## შემოწმების მეთოდი

1. **Exposure:** obtain daily observed/forecast temperature and humidity by station or approved area, with timestamps, quality flags, forecast issue time and revision history.
2. **Warning:** record official warning issue time, validity window, hazard level and geographic scope. Keep warning availability separate from app views, endpoint receipts and verified people reached.
3. **Health indicators:** use only controller-approved aggregates aligned to the WHO 2026 framework, such as preterm births, stillbirths, low birthweight, pregnancy hypertension, child deaths and health-facility visits. Each indicator must retain its own numerator, denominator, geography, period and reporting delay.
4. **Action readiness:** document the responsible authority, official trigger, protective-action playbook, accessible communication channels and after-action review. Do not issue, modify or override official warnings.
5. **Analysis:** pre-register temporal/spatial matching and assess seasonality, air pollution, infection, demographic changes, care access and reporting-delay confounders. Begin with descriptive/exploratory analysis; do not claim causality without an appropriate design.
6. **Privacy:** do not collect app telemetry, device identifiers, individual location, pregnancy/newborn/child records or household-level vulnerability profiles. Apply controller-approved aggregation and small-cell suppression before any release.

## შედეგები და ინტერპრეტაცია

No local health-outcome analysis has been performed. The present result is a documented evidence gap and a proposed measurement design. The existence of an official warning channel is established; the presence, reach and effectiveness of a Georgian heat-health action protocol are not.

## შეზღუდვები და გაურკვევლობები

- The existence of NEA warnings does not prove that heat-health alerts are issued, reach vulnerable people or trigger health-sector action.
- WHO global mortality/exposure estimates are not Georgia-specific baselines.
- Area-level associations are vulnerable to ecological fallacy and confounding.
- The formal status of a Georgian heat-health action plan and the primary NCDC guidance remain unverified.
- No authorized Georgia-specific heat-exposure/health-outcome aggregate dataset, data dictionary, controller permission or denominator has been obtained.
- The app privacy notice is a public policy statement, not an app telemetry export or delivery-receipt dataset.

## დასკვნა

Heat-health readiness is a high-potential extension of NOEMA-007's warning-to-action research, particularly for pregnant/postpartum women, newborns and children. It remains a discovery and measurement-design result only. No operational warning, clinical recommendation or individual risk classification is produced.

## წყაროები

1. National Environmental Agency of Georgia. (2026-06-11). *The National Environmental Agency hosted a presentation of the Information and Communication Technology (ICT) system.* https://nea.gov.ge/En/News/2411
2. National Environmental Agency of Georgia. (undated; accessed 2026-11-27). *Weather Application Privacy Notice.* https://nea.gov.ge/En/weather-app-privacy-notice
3. WHO, WMO, UNICEF and UNFPA. (2026-10-21). *Priority indicators to monitor the impact of heat exposure on maternal, newborn and child health.* https://www.who.int/publications/i/item/9789240125063
4. World Health Organization. (2026-07-31). *Heat and health.* https://www.who.int/news-room/fact-sheets/detail/climate-change-heat-and-health
5. 1TV Georgia. (2026-08-03). *NCDC issues advisory as summer heatwaves intensify.* Secondary media report; primary NCDC notice not independently retrieved. https://1tv.ge/lang/en/news/ncdc-issues-advisory-as-summer-heatwaves-intensify/

## შემდეგი ნაბიჯები

1. Request NEA warning metadata schema, heat-related warning triggers, issue/validity timestamps and geographic scope.
2. Verify the formal Georgian heat-health action-plan status and retrieve the primary NCDC public guidance.
3. Request authorized area/time aggregate MNCH indicators with denominators, reporting delays and data-controller approval.
4. Only after these prerequisites, define a pilot protocol; keep NOEMA as an evaluation layer and do not create a parallel warning channel.

## შემოწმების სტატუსი

- Source URLs checked on 2026-11-27.
- NEA and WHO material reviewed as primary official sources; the NCDC advisory remains secondary reporting.
- No local health data, app telemetry, personal data or operational warning records were accessed.
- Draft completeness and research-index CI are pending after this revision.
- Independent public-health, disaster-risk and privacy review has not occurred.

## ცვლილებების ისტორია

- 2026-11-27: initial evidence inventory and privacy-preserving measurement design.
- 2026-11-27: aligned metadata and required sections with `research/TEMPLATE.md` after draft-validator feedback.
