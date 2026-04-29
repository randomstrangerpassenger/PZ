# Iris DVF 3-3 Phase D Observer Signal Preservation Patch Round Plan

기준일: `2026-04-23`  
버전: `v0.3`  
상태: planning authority only, revised after integrated review v0.2  
라운드 이름: `Iris DVF 3-3 Phase D observer-only signal preservation patch round`  
상위 기준: `docs/Philosophy.md` > `docs/DECISIONS.md` > `docs/ARCHITECTURE.md` > `docs/ROADMAP.md`

---

## 1. Round Identity

이 라운드는 Phase D의 observer-only follow-up이다. 목적은 `report_layer3_body_plan_structural_reclassification.py`의 input model 정합성을 복구하고, observer lane signal 산출물을 `source_signal`과 `section_signal`로 분리 보존하는 것이다.

이 라운드는 staged rollout override round가 아니다. 기존 staged Lua bridge artifact, workspace Lua, parity hash, `quality_state`, `publish_state`, rendered text, compose authority, quality/publish single-writer contract는 전부 봉인 상태로 둔다.

핵심 질문은 아래 하나다.

> 기존 upstream source-side signal과 Phase D section-derived signal이 같은 슬롯에서 서로 덮어써지지 않고, 신규 observer artifact에 동시에 보존되는가?

---

## 2. Scope

### In Scope

- baseline freeze snapshot 생성
- upstream `violation_type` / `violation_flags` field existence와 read map 작성
- source family taxonomy 분리
- `source_signal` / `section_signal` 내부 canonical model 설계
- section-derived family naming rule 확정
- origin field format 확정
- `report_layer3_body_plan_structural_reclassification.py`의 observer input model 패치
- 신규 additive row artifact 생성
- source / section / crosswalk summary artifact 생성
- observer integrity validator 작성 및 실행
- row-level crosscheck report 생성
- diagnostic read packet 생성
- closeout 시 top docs 반영안 작성 및 반영

### Out of Scope

- 기존 `body_plan_structural_reclassification.2105.jsonl` 수정
- 기존 `body_plan_structural_reclassification.2105.summary.json` 수정
- staged Lua bridge artifact 재생성
- workspace `IrisLayer3Data.lua` 변경
- `quality_state` / `publish_state` 재정의
- rendered text 변경
- compose 단계 변경
- quality/publish decision stage 변경
- `quality_baseline_v4 -> v5` cutover
- runtime-side rewrite
- deployed closeout / ready_for_release 선언
- in-game validation
- source expansion execution
- downstream policy reclassification for signal families
- `source_signal` / `section_signal` 용어의 전역 canonical 승격

---

## 3. Sealed Invariants

아래 값은 라운드 전 구간에서 유지해야 하는 hard sealed invariant다.

| 항목 | 값 |
|---|---|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path_total | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish_split | `internal_only 617 / exposed 1467` active 기준 |
| quality_split | `strong 1316 / adequate 0 / weak 768` active 기준 |
| hard_block_candidate_count | `0` |
| writer_role | `observer_only` |
| staged Lua parity hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| Phase 0 Lua hash | `9c5ceebea334277cb9b235e67fdfed8f2089d3eb1b7a2519ada424be11945ee9` |

Silent `21` rows는 row artifact와 total 기준 summary에 포함한다. Silent rows는 upstream field가 있으면 `source_signal`을 가질 수 있고, section trace가 있으면 `section_signal`을 가질 수 있다. 따라서 silent row의 `signal_overlap_state`는 `source_only`, `section_only`, `coexist`, `dual_none` 모두 허용한다. 단, silent rows는 active 기준 publish split과 quality split의 모수에는 넣지 않는다.

---

## 4. Baseline Reference / Preservation Target

아래 값은 hard sealed invariant가 아니라 source preservation target이다. 불일치 시 observer patch가 silent repair를 수행하지 않고 crosscheck handoff로 닫는다.

| 항목 | 기준 |
|---|---|
| count-preservation target | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481` |
| existence/no-overwrite target | `IDENTITY_ONLY`, `ACQ_DOMINANT` |
| count basis | total `2105` 기준 |
| mismatch handling | `closed_with_observer_patch_and_source_count_handoff` 가능 |
| blocked condition | mismatch가 implementation overwrite 또는 artifact mutation에서 온 경우만 blocked |

`IDENTITY_ONLY`와 `ACQ_DOMINANT`는 이번 라운드에서 count-preservation target이 아니다. 검증 기준은 `source_signal_primary` 또는 `source_signal_secondary`에 기록되고 `SECTION_*` family로 대체되지 않는 existence/no-overwrite target이다.

이 섹션의 target count는 source-side signal preservation check를 위한 기준값이다. Staged Lua hash, publish split, quality split 같은 hard invariant와 같은 의미로 읽지 않는다.

---

## 5. Artifact Lane

신규 산출물은 기존 staged/static closeout artifact와 분리한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/
```

기존 read-only artifact는 아래 경로에서 읽는다.

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/
```

신규 필수 산출물:

| 산출물 | 역할 |
|---|---|
| `phase_d_signal_preservation_baseline.{json,md}` | baseline freeze machine snapshot and human readout |
| `source_signal_source_map.md` | upstream field existence and read map |
| `signal_model_design.md` | canonical model, origin format, family taxonomy |
| `section_signal_derivation_rule.md` | section-derived naming and derivation rule |
| `body_plan_signal_preservation.2105.jsonl` | 신규 row-level observer artifact |
| `body_plan_signal_preservation.source_distribution.json` | source_signal active/total/silent distribution |
| `body_plan_signal_preservation.section_distribution.json` | section_signal active/total/silent distribution |
| `body_plan_signal_preservation.crosswalk.json` | source x section crosswalk |
| `phase_d_signal_preservation_validation_report.{json,md}` | observer integrity validator result and readout |
| `signal_preservation_crosscheck_report.json` | old lossy view vs new preserved view crosscheck |
| `phase_d_signal_preservation_diagnostic_packet.json` | next observer/decision round input packet |

If Phase 2 splits the model design note further, the new design artifact must be added to this table before Phase 3 implementation starts.

---

## 6. Current Bug Diagnosis

현재 `report_layer3_body_plan_structural_reclassification.py`는 section trace와 upstream proxy flags를 하나의 `legacy_family_reclassification` 슬롯으로 접는다.

확인된 핵심 지점:

```text
proxy_flags = set(str(value) for value in structural_row.get("violation_flags", []))
```

현재 진단은 "observer가 `violation_type` explicit family를 읽지 않는다"는 것이다. Phase 1은 이것이 단순 observer read bug인지, upstream artifact에 `violation_type` field 자체가 없는 전제 실패인지 먼저 구분해야 한다.

`violation_type` field 자체가 없다면 이 라운드는 patch phase로 진행하지 않는다. 그 경우 upstream producer round가 선행되어야 한다.

---

## 7. Internal Terms and Family Taxonomy

이 섹션의 용어는 본 라운드 observer artifact 내부 scope에서만 유효하다.

### `source_signal`

Compose 이전 facts/decisions overlay 또는 surface contract signal에 이미 존재하던 source-side signal이다. Upstream field 이름은 그대로 `violation_type` / `violation_flags`로 읽는다.

이 정의는 §10 Phase 1 gate가 `violation_type` field existence를 `confirmed as present`로 통과한 전제하에 유효하다.

Core source-preservation target family:

- `BODY_LACKS_ITEM_SPECIFIC_USE`
- `FUNCTION_NARROW`
- `IDENTITY_ONLY`
- `ACQ_DOMINANT`

Upstream structural probe family:

- `LAYER4_ABSORPTION`

Out-of-scope semantic mapping family:

- `ADEQUATE`

`LAYER4_ABSORPTION`은 source hard requirement가 아니다. 이 라운드는 해당 신호를 source family로 승격하지 않는다. Upstream에 structural probe로 존재하는지만 기록하고, section-derived 값과 덮어쓰기 없이 공존 가능한지 검증한다.

`ADEQUATE`는 Phase 1 gate 대상이 아니다. 존재 여부는 note로 기록할 수 있지만 이 라운드의 preservation target으로 삼지 않는다.

### `section_signal`

Phase D가 `body_plan` section trace를 읽어 재계산한 structural observer signal이다. Source-side explicit signal을 덮어쓰지 않는다.

Section-derived family naming rule은 고정한다.

```text
section_signal family values MUST use SECTION_* namespace.
```

Allowed primary section families:

- `SECTION_BODY_LACKS_ITEM_SPECIFIC_USE`
- `SECTION_FUNCTION_NARROW`
- `SECTION_IDENTITY_ONLY`
- `SECTION_ACQ_DOMINANT`
- `SECTION_LAYER4_ABSORPTION`
- `none`

Source family values must not use `SECTION_` prefix. Section family values must use `SECTION_` prefix except `none`. Validator는 이 namespace boundary를 overwrite 판정 기준으로 사용한다.

### `dual_none`

`source_signal`과 `section_signal`이 모두 비어 있는 경우다. 단순 remainder `none`과 구분한다.

### `combined_read`

`combined_read`는 `signal_overlap_state` 필드의 값 공간 이름이다.

허용 값은 아래 네 개뿐이다.

- `source_only`
- `section_only`
- `coexist`
- `dual_none`

---

## 8. Phase Order

```text
Phase 0  baseline freeze
Phase 1  source_signal source map and violation_type field gate
Phase 2  signal model design
Phase 3  implementation patch
Phase 4  additive artifact generation
Phase 5  observer integrity validation
Phase 6  overwrite absence crosscheck
Phase 7  diagnostic packet
Phase 8  top-doc reflection and closeout
```

Phase 2는 기존 초안의 canonical model design과 section_signal derivation rule을 단일 design phase로 통합한다. Section naming, canonical fields, origin format, silent row handling, validator preconditions가 같은 phase에서 닫히기 전에는 implementation patch를 시작할 수 없다.

Phase 3 이후 실패하면 기존 artifact와 Lua hash가 불변인지 확인한 뒤 closeout을 중단한다. Existing artifact를 수정하는 rollback path는 사용하지 않는다.

---

## 9. Phase 0 - Baseline Freeze

### Purpose

패치 전에 current sealed baseline과 기존 artifact hash를 고정한다.

### Required Inputs

- `dvf_3_3_rendered_v2_preview.2105.json`
- `body_plan_structural_reclassification.2105.jsonl`
- `body_plan_structural_reclassification.2105.summary.json`
- `body_plan_v2_regression_gate_report.2105.json`
- `body_plan_v2_runtime_validation_report.2105.json`
- staged Lua artifact
- workspace Lua artifact
- current quality baseline reference

### Required Outputs

- `phase_d_signal_preservation_baseline.json`
- `phase_d_signal_preservation_baseline.md`

### Gate

- hard sealed values match Section 3
- Section 4 preservation target is recorded but not treated as hard invariant
- existing structural artifact SHA-256 recorded
- staged Lua hash matches sealed value
- Phase 0 Lua hash matches sealed value
- existing row artifact contains no `quality_state` / `publish_state`
- no new signal preservation artifact has been generated yet

---

## 10. Phase 1 - Source Signal Source Map and Field Gate

### Purpose

Observer code가 실제로 어떤 upstream field에서 무엇을 읽는지 구현 전에 확정하고, `violation_type` field 자체가 존재하는지 전제 검증을 끝낸다.

### Required Output

- `source_signal_source_map.md`

### Required Content

For each core source-preservation family, record:

- upstream producer
- current upstream field
- current observer read point
- current observer defect, if any
- required new read point
- fallback or escalation rule

Core source-preservation families:

- `BODY_LACKS_ITEM_SPECIFIC_USE`
- `FUNCTION_NARROW`
- `IDENTITY_ONLY`
- `ACQ_DOMINANT`

Additional note targets:

- `LAYER4_ABSORPTION`: upstream structural probe family, read point or upstream-missing note allowed
- `ADEQUATE`: out-of-scope semantic mapping family, gate 대상 제외

The map must explicitly answer:

- whether `violation_type` field exists in the upstream artifact schema
- whether `violation_type` has row-level non-null values
- whether `violation_flags` handling preserves or hides each core source family
- exact code snippet that substitutes `violation_flags` for explicit `violation_type`
- whether the "line 85 overwrite" diagnosis matches the source map
- which families are not recorded upstream at all
- escalation path for upstream-missing families

### Gate

- `violation_type` field existence is confirmed before Phase 2
- if `violation_type` field itself is absent, stop with `blocked_by_missing_violation_type_field`
- if `violation_type` field exists but row-level non-null population is `0`, stop with `blocked_by_empty_violation_type_population`
- if `violation_type` field exists and row-level non-null population is non-zero, but core source-preservation target family population is `0`, close with `closed_with_upstream_signal_gap_handoff`
- core source-preservation family read points are identified or family-level upstream gaps are explicitly marked for handoff
- `LAYER4_ABSORPTION` has read point or upstream-missing note
- `ADEQUATE` is not used as a Phase 1 pass/fail gate
- `violation_flags` replacement point is identified
- upstream-missing family is not patched in this round; it is handed off

---

## 11. Phase 2 - Signal Model Design

### Purpose

Code edit 전에 canonical model, section naming, section derivation, silent row behavior, origin format, validator preconditions를 한 번에 확정한다.

### Required Outputs

- `signal_model_design.md`
- `section_signal_derivation_rule.md`

### Canonical Row Model

Patch 후 observer 내부 canonical row model은 아래 필드를 가진다.

| 필드 | 형식 | 의미 |
|---|---|---|
| `source_signal_primary` | string or `none` | 가장 우선 보존할 upstream 원신호 |
| `source_signal_secondary` | array of strings | 보조 source-side signal |
| `source_signal_origin` | array of origin objects | source signal provenance |
| `section_signal_primary` | string or `none` | section trace 재계산 결과 |
| `section_signal_secondary` | array of strings | 보조 section-derived signal |
| `section_signal_origin` | array of origin objects | section signal provenance |
| `source_signal_present` | bool | source axis populated 여부 |
| `section_signal_present` | bool | section axis populated 여부 |
| `signal_overlap_state` | enum | `combined_read` 값 |
| `signal_conflict_note` | string or null | 공존/불일치 설명 |

Origin object format:

```json
{
  "artifact": "relative/or/absolute/path",
  "producer": "producer_name",
  "row_key": "Base.ItemType",
  "field": "violation_type",
  "json_path": "$.violation_type"
}
```

`source_signal_origin` and `section_signal_origin` are always arrays. Empty origin is represented as `[]`, not `null`.

### Source / Section Rules

1. `source_signal`과 `section_signal`은 동시에 존재할 수 있다.
2. `section_signal`은 `source_signal`을 제거하거나 대체하지 않는다.
3. Explicit `violation_type`이 있으면 source primary로 우선 보존한다.
4. `violation_flags`는 explicit `violation_type`이 없을 때 fallback primary로 사용할 수 있고, explicit이 있을 때는 secondary 또는 auxiliary provenance로만 기록한다. `violation_flags -> source_signal_primary` 승격은 Phase 1 source map에서 승인된 closed allowlist mapping으로만 허용한다. Generic proxy normalization이나 ad hoc heuristic은 금지한다.
5. `dual_none`은 source와 section이 모두 비어 있을 때만 허용한다.
6. `none` distribution은 `dual_none`만 집계한다. `source_only` / `section_only` / `coexist` row를 remainder로 접지 않는다.
7. `SECTION_*` namespace rule is mandatory before validator implementation.
8. Silent rows follow the same `combined_read` enum but remain excluded from active publish/quality split baselines.

### Section Derivation Rule

`section_signal_derivation_rule.md` must include:

- allowed `SECTION_*` families
- mapping from body_plan emitted/missing section trace to section_signal
- `SECTION_LAYER4_ABSORPTION` handling rule
- silent row handling rule
- `hard_block_candidate` handling rule
- why section_signal is not a quality/publish writer input
- validator interpretation of same-surface source and section families

### Gate

- `SECTION_*` naming rule is fixed, not a default proposal
- source family names and section family names cannot be confused in logs
- `LAYER4_ABSORPTION` cannot overwrite source-side family because section value must be `SECTION_LAYER4_ABSORPTION`
- origin object format is fixed
- silent row `combined_read` behavior is fixed
- `hard_block_candidate_count` remains observer-only evidence
- validator design is not finalized before this phase passes
- no planned write to existing `body_plan_structural_reclassification.2105.*`
- no planned write to Lua artifacts
- no planned write to quality/publish artifacts
- default execution path for this round points at the new artifact root

---

## 12. Phase 3 - Implementation Patch

### Write Surface

Primary write surface:

- `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`

Allowed supporting write surface:

- `Iris/build/description/v2/tests/`
- optional new validator script under `Iris/build/description/v2/tools/build/`

Top docs are not updated in this phase.

### Required Changes

- read explicit `violation_type` for source primary preservation
- read `violation_flags` as fallback/secondary source signal
- preserve core source family taxonomy from Section 7
- derive `SECTION_*` section signal from body_plan trace without replacing source signal
- emit fixed origin object arrays
- add new row artifact schema
- add source distribution summary
- add section distribution summary
- add crosswalk summary
- ensure new artifact excludes `quality_state`, `publish_state`, rendered text
- ensure writer_role is fixed to `observer_only`

### Gate

- implementation can generate new artifacts without touching existing structural artifacts
- existing tests pass or test delta is explained
- new focused tests cover `coexist`, `source_only`, `section_only`, `dual_none`
- focused tests cover same-surface source/section coexist, such as `BODY_LACKS_ITEM_SPECIFIC_USE` with `SECTION_BODY_LACKS_ITEM_SPECIFIC_USE`

---

## 13. Phase 4 - Additive Artifact Generation

### Required Row Artifact

`body_plan_signal_preservation.2105.jsonl`

Required row fields:

```text
row_id
writer_role
round_id
runtime_state
source_signal_primary
source_signal_secondary
source_signal_origin
section_signal_primary
section_signal_secondary
section_signal_origin
source_signal_present
section_signal_present
signal_overlap_state
signal_conflict_note
```

Forbidden row fields:

- `quality_state`
- `publish_state`
- rendered text

### Required Summary Artifacts

1. `body_plan_signal_preservation.source_distribution.json`
   - active 기준 count
   - total 기준 count
   - silent count 별도 표기
   - Section 4 target check result
   - silent subcount consistency rule:
     `source_distribution.silent_count + source_distribution.active_count == 2105`

2. `body_plan_signal_preservation.section_distribution.json`
   - active 기준 count
   - total 기준 count
   - silent count 별도 표기

3. `body_plan_signal_preservation.crosswalk.json`
   - source x section matrix
   - source-only count
   - section-only count
   - coexist count
   - dual-none count
   - silent count 별도 표기
   - silent subcount consistency rule:
     `crosswalk.silent_count == source_distribution.silent_count`
   - explicit family preservation delta
   - newly observed structural-only rows
   - would-have-overwritten count
   - note that would-have-overwritten is diagnostic only, not an actual overwrite

### Gate

- row_count is `2105`
- `writer_role` is `observer_only` for every row
- source distribution target check is recorded as `match`, `mismatch_handoff`, or `implementation_error`
- active, total, and silent bases are all present in summary artifacts
- silent rows are separated from publish/quality split reasoning

---

## 14. Phase 5 - Observer Integrity Validation

### Required Outputs

- `phase_d_signal_preservation_validation_report.json`
- `phase_d_signal_preservation_validation_report.md`

### Required Checks

- `row_count == 2105`
- every row has `writer_role == observer_only`
- row artifact has no `quality_state`
- row artifact has no `publish_state`
- row artifact has no rendered text
- runtime path total unchanged: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- publish split unchanged: `internal_only 617 / exposed 1467`
- quality split unchanged: `strong 1316 / adequate 0 / weak 768`
- staged Lua parity hash unchanged
- Phase 0 Lua hash unchanged
- existing structural artifact byte-level hash unchanged
- count-preservation target check outcome is either `match` or `mismatch_handoff`
- `implementation_error` outcome is a validator failure, not a handoff
- existence/no-overwrite target is preserved for `IDENTITY_ONLY` and `ACQ_DOMINANT`
- only `dual_none` contributes to signal `none`
- `SECTION_LAYER4_ABSORPTION` does not overwrite source-side family
- source summary totals are internally consistent
- section summary totals are internally consistent
- crosswalk totals are internally consistent
- silent row subcounts are internally consistent
- `hard_block_candidate_count` is not interpreted as writer effect

### Gate

All hard invariant checks must pass. Source distribution target mismatch can proceed only when the report classifies it as `mismatch_handoff`, not `implementation_error`.

---

## 15. Phase 6 - Overwrite Absence Crosscheck

### Required Output

- `signal_preservation_crosscheck_report.json`

### Required Content

- existing artifact `proxy_violation_flags` / `legacy_family_reclassification` distribution
- new artifact `source_signal` distribution
- row-level diff between old lossy view and new preserved view
- rows where source signal is preserved but section signal differs
- rows where upstream source signal is missing and cannot be reconstructed
- rows where source and section signal match
- `would-have-overwritten` count and example rows

### Numeric Check

The total source distribution must be checked against Section 4:

```text
BODY_LACKS_ITEM_SPECIFIC_USE 617
FUNCTION_NARROW 7
none 1481
```

If it does not match, the round does not silently repair the count. The report records mismatch cause and hands it off as a next-round input unless the mismatch is caused by implementation overwrite, artifact mutation, or model bug.

Existence/no-overwrite target check for `IDENTITY_ONLY` and `ACQ_DOMINANT` is performed in §14 validator, not in this numeric check.

---

## 16. Phase 7 - Diagnostic Packet

### Required Output

- `phase_d_signal_preservation_diagnostic_packet.json`

### Required Content

- baseline freeze snapshot
- source distribution
- section distribution
- crosswalk
- explicit family preservation check
- structural-only newly observed set
- candidate-only note
- non-writer seal confirmation
- crosscheck result
- handoff reason if source distribution does not match Section 4

### Packet Non-Goals

The packet must not include:

- compose repair instruction
- immediate requeue instruction
- publish mutation trigger
- runtime adoption change declaration

---

## 17. Phase 8 - Top-Doc Reflection and Closeout

Top docs are updated only after Phase 5 and Phase 7 pass.

### `DECISIONS.md`

Record:

- this round is Phase D observer-only signal preservation patch round
- additive-only contract
- existing artifact and Lua hash unchanged
- `source_signal` / `section_signal` are round-local terms
- source distribution count is a preservation target, not a hard sealed invariant
- `LAYER4_ABSORPTION` is recorded only as an upstream structural probe in this round and is not promoted to a source preservation family
- `ADEQUATE` is not a preservation target in this round
- sealed non-goals remain closed
- closeout artifact locations

### `ARCHITECTURE.md`

Record near the current Iris DVF 3-3 addenda after the EDPAS section:

- Phase D observer lane read model update
- source-side family ownership boundary
- section-side family ownership boundary
- `dual_none` definition
- `SECTION_*` namespace rule
- new observer artifact role and location

### `ROADMAP.md`

Record:

- Done: observer signal-preservation patch artifacts and validator pass
- Next: crosscheck mismatch handoff handling only if mismatch exists

No term-promotion Next item is added by this round. Canonical promotion of `source_signal` / `section_signal` requires a separate explicit opening decision.

---

## 18. Closeout Criteria

The round may close only when all items are true.

1. `violation_type` field existence has been confirmed as present before implementation.
2. `report_layer3_body_plan_structural_reclassification.py` separates source and section canonical models.
3. New row artifact preserves source-side family and section-derived family simultaneously.
4. Core source families and `SECTION_*` section families do not overwrite each other in a single slot.
5. `dual_none` is distinct from generic remainder `none`.
6. row_count, active/silent split, runtime_path_total, publish split, quality split, staged Lua hash all remain unchanged.
7. Silent rows are represented in total and silent subcounts without changing active publish/quality baselines.
8. New row artifact is `observer_only` and has no `quality_state` / `publish_state`.
9. Source distribution, section distribution, and crosswalk summaries are separate artifacts.
10. Existing artifact byte-level hash is unchanged.
11. Observer integrity validator passes all hard invariant checks.
12. Source distribution mismatch, if any, is classified as handoff rather than implementation error.
13. Diagnostic read packet is generated.
14. Top docs reflect the closeout without declaring deployed closeout, term promotion, or quality baseline cutover.

---

## 19. Failure Branches

### Missing `violation_type` Field

If `violation_type` field itself is absent from the upstream artifact schema, do not enter implementation patch.

Closeout wording:

```text
blocked_by_missing_violation_type_field
```

Recovery path: write a quarantine/blocking decision and open a separate upstream producer round before retrying this preservation patch.

### Empty `violation_type` Population

If `violation_type` field exists but row-level non-null population is `0`, do not enter implementation patch.

Closeout wording:

```text
blocked_by_empty_violation_type_population
```

Recovery path: write a quarantine/blocking decision and open a separate upstream producer or population-repair round before retrying this preservation patch.

### Source Distribution Mismatch

If source distribution does not match the Section 4 preservation target, do not repair it inside this round. Generate the crosscheck report and diagnostic packet with `handoff_required: true`.

Closeout wording:

```text
closed_with_observer_patch_and_source_count_handoff
```

This branch is allowed only when hard invariants pass and the mismatch is not caused by implementation overwrite or artifact mutation.

### Integrity Validation Failure

If any hard invariant changes, stop closeout and quarantine new outputs.

Closeout wording:

```text
blocked_by_observer_integrity_failure
```

Recovery path: write a quarantine decision for this round, separate the cause, then open a follow-up round. Do not silently retry inside this round after an integrity failure.

### Existing Artifact Hash Drift

If the existing structural artifact hash changes, stop closeout and quarantine all new outputs until the write source is identified.

Closeout wording:

```text
blocked_by_additive_only_contract_breach
```

Recovery path: write a quarantine decision for this round, identify the mutating command or code path, then open a follow-up repair round. Do not close this round as pass.

### Upstream-Missing Family

If a family is not recorded upstream and cannot be reconstructed without source expansion or upstream producer patch, record it in `source_signal_source_map.md` and hand it off.

Closeout wording:

```text
closed_with_upstream_signal_gap_handoff
```

This branch is distinct from missing `violation_type` field. Field absence blocks the round; family absence can be handed off if the field/schema exists.

### Handoff Priority Rule

If `closed_with_upstream_signal_gap_handoff` and `closed_with_observer_patch_and_source_count_handoff` are both triggered, closeout wording records both handoffs.

Ordering rule:

- if the primary cause is upstream field/family absence, record `closed_with_upstream_signal_gap_handoff` first
- if the primary cause is preserved-source count mismatch with intact upstream field/schema, record `closed_with_observer_patch_and_source_count_handoff` first

---

## 20. Explicit Non-Actions

Section 2 is the canonical out-of-scope list. This section only restates the high-risk non-actions:

- no `quality_state` / `publish_state` rewrite
- no same-build re-compose
- no runtime bridge rewrite
- no staged Lua artifact replacement
- no deployed closeout
- no source expansion execution
- no canonical promotion of `source_signal` / `section_signal`

---

## 21. One-Line Gate

Closeout must make this sentence true:

> Phase D observer artifacts now preserve upstream source-side signals and section-derived structural signals as separate axes, while every sealed runtime, quality, publish, Lua parity, and existing artifact hash invariant remains unchanged.
