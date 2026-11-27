# NOEMA-2026-007 addendum — Georgia heat-health readiness

**Date:** 2026-11-27  
**Evidence status:** Preliminary discovery and measurement design; no local health outcome analysis  
**Parent study:** NOEMA-2026-007 — the portfolio's existing warning-to-action research stream.

## Research question

Can Georgia's existing official meteorological warning channel be evaluated alongside authorized, privacy-preserving heat-exposure and maternal/newborn/child health indicators, so health authorities can identify preparedness gaps without creating a duplicate warning service or collecting individual app/health telemetry?

## Verified evidence

### FACT — Georgia has an official multi-source warning capability

On 2026-06-11, the National Environmental Agency (NEA) described its ICT system as collecting, processing and analysing information from multiple sources and disseminating relevant warnings. The agency also described a mobile application for weather and hydrometeorological warnings. This is evidence of an official warning channel and institutional capability; it is not proof of heat-specific health triggers or health-sector response integration.

Source: [NEA — ICT system presentation, 2026-06-11](https://nea.gov.ge/En/News/2411).

### FACT — the weather app has a published privacy boundary

NEA's Weather Application Privacy Notice says the app displays weather information, forecasts, warnings and maps and does not require registration or an account. It may use a selected location, current location only with user permission, device IP, request date/time and technical logs. The notice says it does not collect names, personal numbers, email addresses, phone numbers, passwords or profile data.

Source: [NEA Weather Application Privacy Notice](https://nea.gov.ge/En/weather-app-privacy-notice).

**Interpretation boundary:** a privacy notice describing data the app may process is not a delivery receipt dataset, population-coverage measure or health-outcome linkage. NOEMA will not ingest app-level location, IP, device identifiers, message receipts or individual health records.

### FACT — a new international health-monitoring framework exists

On 2026-10-21, WHO published *Priority indicators to monitor the impact of heat exposure on maternal, newborn and child health*, jointly developed with WMO, UNICEF and UNFPA. It organizes indicators across routine maternal/newborn/child health monitoring, public-health surveillance, climate-and-health monitoring and heat-exposure measurement. The publication describes combined analysis of health indicators and heat-exposure data as a way to identify trends and potential impacts.

Source: [WHO publication 9789240125063, 2026-10-21](https://www.who.int/publications/i/item/9789240125063).

The WHO 2026-07-31 heat-and-health fact sheet reports global estimates and identifies older people, outdoor/manual workers, urban/rural poor and people with underlying illness as vulnerable groups. Its global estimates are not Georgian baselines and must not be transferred to local municipalities.

Source: [WHO — Heat and health, 2026-07-31](https://www.who.int/news-room/fact-sheets/detail/climate-change-heat-and-health).

### SECONDARY SIGNAL — public advice was reported, primary notice not retrieved

On 2026-08-03, 1TV reported public heat-health recommendations attributed to Georgia's NCDC/Ministry of Health. The NCDC website currently indicates reconstruction. This is retained only as a secondary signal; it is not treated as an independently retrieved NCDC technical guideline or a formal national heat-health action plan.

Source: [1TV report, 2026-08-03](https://1tv.ge/lang/en/news/ncdc-issues-advisory-as-summer-heatwaves-intensify/).

## Evidence classification

- **FACT:** NEA publicly describes an ICT early-warning system and weather app; an official app privacy notice exists.
- **FACT:** WHO/WMO/UNICEF/UNFPA published a 2026 MNCH heat-indicator framework.
- **INFERENCE:** these sources create a practical opportunity to evaluate the connection between meteorological warnings, heat exposure and health-sector readiness.
- **HYPOTHESIS:** an aggregate-only linkage may help authorities detect unusual heat-period changes and target preparedness actions without tracking individuals.
- **UNTESTED IDEA:** a Heat-Health Readiness measurement layer that consumes approved warning metadata and area/time aggregates, then produces a non-operational evidence report for authorized reviewers.

## Proposed measurement design

1. **Exposure:** daily observed/forecast temperature and humidity by station or approved area, with timestamp, quality flag, forecast issue time and revision history.
2. **Warning:** official warning issue time, validity window, hazard level and geographic scope. Keep issue/availability separate from app views, endpoint receipts and verified people reached.
3. **Health indicators:** only controller-approved aggregates aligned with the WHO 2026 framework, such as preterm births, stillbirths, low birthweight, pregnancy hypertension, child deaths and health-facility visits. Each indicator must retain its own numerator, denominator, geography, period and reporting delay.
4. **Action readiness:** document the responsible authority, official trigger, protective-action playbook, accessible communication channels and after-action review. Do not issue, modify or override official warnings.
5. **Analysis:** pre-register temporal/spatial matching, seasonality, air pollution, infection, demographic changes, care access and reporting-delay confounders. Begin with descriptive and exploratory analysis; no causal claim without an appropriate design.
6. **Privacy:** do not collect app telemetry, device identifiers, individual location, pregnancy/newborn/child records or household-level vulnerability profiles. Apply controller-approved aggregation and small-cell suppression before any release.

## Human benefit and urgency

Extreme heat can cause rapid health impacts, and WHO describes the need for timely intervention when heat alerts are issued. Maternal, newborn and child outcomes deserve explicit monitoring because the 2026 joint framework identifies important measurement gaps. The potential human benefit is high, but Georgia-specific burden, geographic distribution and current response gaps have not been quantified in this addendum.

## Risks and blockers

- The existence of NEA warnings does not prove that heat-health alerts are issued, reach all vulnerable people or trigger health-sector action.
- WHO global mortality/exposure estimates are not Georgia-specific baselines.
- Ecological fallacy and confounding can produce misleading area-level associations.
- The formal status of a Georgian heat-health action plan and the primary NCDC guidance remain unverified.
- No authorized Georgia-specific heat-exposure/health-outcome aggregate dataset, data dictionary, controller permission or denominator has been obtained.

## Next step

Request from NEA and the health authorities the warning metadata schema, formal heat-health action-plan status, primary NCDC guidance, and authorized area/time aggregate MNCH indicators with denominators and reporting delays. Only then define a pilot protocol. Keep this work inside NOEMA-007's four-pillar warning-to-action measurement programme; do not create a fifth portfolio stream or a parallel public warning channel.
