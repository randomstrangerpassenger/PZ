# DVF 3-3 vNext Delta Disposition Policy

Status: authoritative rubric for the delta disposition guard-seal round.

This document owns the disposition enum, runtime eligibility rule, rationale code meanings,
and the selected `publish_state` branch for this round. Staging copies are derived evidence.

## Disposition Enum

- `approved`: contract-conformant delta with sealed per-row source evidence, deterministic parity evidence, consumer migration anchor, current vocabulary conformance, and no single-authority violation.
- `deferred`: reviewed row that remains non-runtime-eligible until a later source, migration, publish-preview, or review scope opens.
- `rejected`: row that must not enter current authority, approved cutover input, or runtime-eligible manifests before correction and re-parity.

Only `approved` rows may set `runtime_eligible=true`. `deferred` and `rejected` rows must set `runtime_eligible=false`.

## Branch Selection

`publish_state` uses branch B: predecessor-only legacy visibility disposition is recorded, but it is excluded from classification rows. This is not policy mutation, payload-equality reopening, or silent deletion.

## Rationale Codes

- `SOURCE_CHAIN_TEXT_DELTA_APPROVED`: direct `text_ko` payload delta is source-chain backed and not blocked by a rejected state axis.
- `GOVERNED_STATE_DELTA_REJECTED_POLICY_NO_MUTATION`: governed-derived state delta would move a previously adopted row to unadopted during a non-cutover, no-policy-mutation round.
- `TEXT_DELTA_REJECTED_BY_STATE_AXIS`: text delta is source-backed but shares a key with a rejected state-axis delta and is not runtime-eligible in this round.
- `NEGATIVE_CASE_EXPECTED_FAIL`: synthetic guard/test case is expected to trip fail-loud behavior.

The rubric is contract and consistency based. It is not public-facing text quality acceptance, release readiness, runtime rollout, or publish policy mutation.

## Reviewer Schema

Disposition rows must split `reviewer_role` from `reviewer_identity`. This automated execution records the independence limitation when the same tool identity supplies validation and closeout evidence.
