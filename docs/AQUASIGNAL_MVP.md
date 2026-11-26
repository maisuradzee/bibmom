# AquaSignal — operator-side water anomaly MVP

**NOEMA direction:** DISCOVERY → RESEARCH → INNOVATION  
**Date:** 2026-11-26  
**Status:** prototype specification; not validated for operational deployment

## Problem framing

Water safety requires both risk management and verification. Existing laboratories and regulators remain essential. AquaSignal is proposed as an additional operator decision-support layer that can join authorized sensor telemetry with laboratory results and site-specific control plans.

It is not a consumer water-safety app, a pathogen detector, a regulatory system or a replacement for laboratory analysis.

## Intended users and decision

**Users:** authorized water-supply operators, laboratory quality staff and competent public-health or regulatory personnel.

**Decision supported:** whether a reading or short time series requires an operator to inspect the instrument, follow an approved corrective-action procedure, collect a confirmatory sample or escalate through the existing water-safety plan.

The MVP does not tell residents that water is safe or unsafe and does not issue public health instructions.

## Inputs

Each sensor observation must include:

- asset and parameter identifiers;
- sensor and source identifiers;
- numeric value and unit;
- timezone-aware observation timestamp;
- calibration-valid-until timestamp;
- source provenance and instrument metadata.

A separate laboratory record should carry sample ID, sampling location/time, method, laboratory identity, accreditation scope where relevant, result, unit, reporting limit and chain-of-custody metadata. Laboratory records are not yet ingested by the prototype.

## Rule engine

The module noema_core/aquasignal.py implements a deterministic first slice:

| State | Meaning | System behavior |
|---|---|---|
| DATA_QUALITY_HOLD | no data, stale data, future timestamp or invalid calibration | do not infer normality; request data/instrument review |
| NORMAL | latest valid reading is inside the supplied operational range | record only; never certify potability |
| WATCH | one or not-yet-persistent operational deviation | ask operator to verify sensor and gather evidence |
| ALERT | configured consecutive deviations reached | request operator review and approved response procedure |
| CRITICAL_CANDIDATE | supplied critical boundary crossed | urgent operator verification; not an automatic public warning |

All boundaries, freshness windows, consecutive-count requirements and gaps are supplied by the responsible operator from the approved site-specific Water Safety Plan and instrument specification. The code contains no universal water-quality thresholds.

A single assessment accepts readings from one sensor and one source only. Mixing sensors or units is rejected. Missing or stale data cannot be interpreted as normal. The engine keeps the operator-review requirement true for every state.

## Safety and security controls

- No automatic valve operation, dosing change, shutdown or public notification.
- No user or household personal data in the MVP.
- No secrets or credentials in Git, JSON fixtures or logs.
- Public-source metadata may be cited; licensed or operator data requires explicit permission and a separate reuse decision.
- All thresholds are site-specific and versioned outside the code.
- Sensor alarms must be reconciled with calibration, maintenance, process context and laboratory verification.
- The word NORMAL means only “inside configured operational bounds”; it is not a health-based compliance or potability conclusion.

## Pilot design

Before a pilot, obtain written authorization and a data dictionary from one water supplier or laboratory. Use a time-bounded, non-personal historical dataset with paired sensor and laboratory observations, instrument calibration records and known incident/maintenance annotations.

Pre-register the evaluation before inspecting outcomes:

- detection delay from the first independently verified operational deviation;
- sensitivity and positive predictive value against the agreed reference labels;
- false alerts per asset-day;
- missed events and their severity;
- stale/missing data rate and calibration failures;
- operator acknowledgement and resolution time;
- subgroup and site differences.

A pilot must include a baseline using the operator's existing monitoring process. Do not infer that AquaSignal reduces disease or improves water safety from sensor-alert metrics alone.

## Stop conditions

Stop or disable the affected rule if timestamps, calibration or units cannot be trusted; if false alerts overwhelm operators; if a threshold's authority/version is unknown; if a data permission expires; or if the system's output could be mistaken for an official public warning.

## Current implementation

- noema_core/aquasignal.py — pure, deterministic rules; no network or hardware access.
- tests/test_aquasignal.py — synthetic unit tests for normal, watch, persistent alert, critical candidate, stale data, calibration failure, time gaps, future timestamps and invalid input.

This is a software-behavior prototype only. It has not been tested against a live water network, laboratory time series or field sensor.
