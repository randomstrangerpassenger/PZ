# Iris DVF 3-3 Phase D/E Staged Rollout Override Round Plan

기준일: 2026-04-22  
버전: v1.1  
상태: planning authority only  
라운드 이름: `Iris DVF 3-3 compose authority migration — Phase D / E-0 / E staged rollout override round`

---

## 1. Round Identity

이 round는 `scope_policy_override_round`다. v0.2에서 Hold로 분리했던 Phase D / E-0 / E를 같은 세션의 실행 범위로 다시 연다.

이 round의 closeout은 **staged/static rollout**까지만이다. Manual in-game validation과 deployed closeout 선언은 본 round 종료 조건에 포함하지 않는다.

이 round는 body_plan migration 이후의 후속 검증과 staged/static rollout만 다룬다. Compose 설계 변경, `quality_state / publish_state` axis 재정의, facts 슬롯 확장, compose 외부 repair 재도입은 non-goal이다.

---

## 2. Scope

### 포함

- Phase 0: governance sealing
- Phase D: `body_plan` section trace 기반 structural reclassification
- Phase E-0: `2105` baseline 대비 full-runtime regression gate
- Phase E: staged Lua bridge artifact, `IrisLayer3Data.lua` 갱신, parity hash 확인
- `ready_for_in_game_validation` 상태 생성

### 제외

- Manual in-game validation
- Deployed closeout 선언
- `quality_state / publish_state` axis 재계산
- `quality_baseline_v4 -> v5` cutover
- facts 슬롯 확장
- runtime Lua consumer contract 변경
- compose 외부 repair 재도입

---

## 3. Phase Order

```text
Phase 0 -> Phase D -> Phase E-0 -> Phase E -> closeout wording branch
```

각 phase는 직전 phase의 closeout artifact를 입력으로 사용한다. 병렬 집행은 금지한다.

---

## 4. Baseline

본 round의 공식 baseline은 2026-04-19 SDRG terminal handoff의 `2105` runtime 기준이다.

| 항목 | 값 |
|---|---|
| total rows | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| quality baseline | `quality_baseline_v4` |
| quality distribution | `strong 1316 / adequate 0 / weak 768` |
| quality reference path | `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json` |

기존 walkthrough의 `1050`, `adequate 130` 수치는 탐사 로그다. Current authoritative baseline으로 읽지 않는다.

Publish split은 active rows 기준이다. Silent rows `21`은 `internal_only / exposed` split 모수에서 제외된다.

Quality distribution 역시 active rows 기준이다. Silent rows `21`은 `strong / adequate / weak` 분포 모수에서 제외된다.

Runtime path의 `identity_fallback 17`과 publish split의 `internal_only 617`은 의도적으로 별도 계약이다. 2026-04-15 `600 promoted / residual 17` closeout 이후에도 publish split은 `617`을 유지하도록 봉인됐다. Phase E-0 gate는 두 수치를 독립 축으로 검증한다.

---

## 5. Phase 0 — Governance Sealing

### 목적

Phase D artifact 생성 전에 scope override와 writer boundary를 봉인한다.

### Required Outputs

- 결정 1: `DECISIONS.md`에 `scope_policy_override_round opening` 결정 추가
  - 이유 기본값: v0.2 §2-1 4번째 결정의 명시 경로에 따라 Phase D/E-0/E scope 확장을 governance 봉인 상태에서 여는 것
- 결정 2: `DECISIONS.md`에 Phase D는 pure observer이며 `quality_state / publish_state`를 수정하지 않는다는 결정 추가
  - 이유 기본값: 2026-04-06 single writer 봉인 및 2026-04-19 SAPR v5 cutover 없음 봉인을 Phase D 진행 중에도 유지하는 것
- 결정 3: `DECISIONS.md`에 Phase E는 staged/static rollout까지만 닫고 deployed closeout은 제외한다는 결정 추가
  - 이유 기본값: in-game validation 없이 deployed closeout을 선언하지 않는 기존 round closeout 관례와 정합하는 것
- walkthrough §6~§8을 탐사 로그로 재분류하고, `1050 / adequate 130`이 current baseline이 아님을 명시
- `IrisLayer3Data.lua` baseline hash가 2105 기준 sealed bridge와 일치하는지 확인
- `quality_baseline_v4.json`의 quality distribution을 확인하고 Phase E-0 gate 입력으로 전달
- 필요 시 `ROADMAP.md`에 본 round addendum 추가

### Exit Gate

- DECISIONS 3개 결정 기록 완료
- walkthrough 재분류 경고 블록 삽입 완료
- `IrisLayer3Data.lua` hash가 2105 baseline 기준값과 일치하거나, rollback 불가 대안 decision이 기록됨
- `quality_baseline_v4.json` 분포 수치가 `strong 1316 / adequate 0 / weak 768`과 일치함이 확인됐고 Phase E-0 gate 입력으로 전달됨

---

## 6. Phase D — Structural Reclassification

### 목적

`body_plan` section trace를 기준으로 structural signal을 재계상한다. Phase D는 rendered text, `quality_state`, `publish_state`를 직접 변경하지 않는다.

### Inputs

- Phase 0 closure
- `2105` row 기준 body_plan compose result
- 기존 body-role structural lint signal family

### Required Outputs

- `body_plan_structural_reclassification.full.jsonl`
- `body_plan_structural_reclassification.summary.full.json`

### Required Signal Families

- `LAYER4_ABSORPTION`
- `IDENTITY_ONLY`
- `BODY_LACKS_ITEM_SPECIFIC_USE`
- `FUNCTION_NARROW`
- `ACQ_DOMINANT`

### Writer Boundary

- `writer_role: observer_only`
- `quality_state` 필드 출력 금지
- `strong / adequate / weak` 분포 report 금지
- report는 `signal_distribution`과 hard-block candidate만 기록

### Exit Gate

- row count = `2105`
- active / silent = `2084 / 21`
- output artifact에 `quality_state` 필드 없음
- hard_block_candidate count 기록됨
- rendered / quality / publish 변경 없음

---

## 7. Phase E-0 — Full-Runtime Regression Gate

### 목적

`body_plan` compose 결과가 sealed `2105` baseline 대비 regression을 유발하지 않았는지 전수 검증한다.

### Required Output

- `body_plan_v2_regression_gate_report.json`

### Gate Axes

| 축 | pass 기준 |
|---|---|
| row count | `2105` 유지 |
| runtime_state | `active 2084 / silent 21` 유지 |
| runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` 유지 |
| publish split | `internal_only 617 / exposed 1467` 유지 |
| determinism | 동일 입력 2회 compose 결과 동일 |
| accidental change | legacy vs body_plan diff accidental `0` |
| unexpected delta | 예상 외 row/field delta `0` |
| publish regression | `exposed -> internal_only` 역행 `0` |
| LAYER4 hard block | Phase D hard_block_candidate `0` |

### Quality Distribution Gate

- 기준은 `quality_baseline_v4`
- `strong / adequate / weak` 분포는 sealed regression axis다.
- required value: `strong 1316 / adequate 0 / weak 768`
- 분포 변경 감지 시 즉시 중단하고 writer 추적

### Exit Gate

- 9개 gate 축 전부 pass
- quality distribution gate pass

---

## 8. Phase E — Staged / Static Rollout

### 목적

E-0 pass 이후 staged body_plan output을 Lua bridge로 export하고, `IrisLayer3Data.lua` 갱신 및 parity hash 확인까지 수행한다.

게임 내부 manual validation은 본 round scope가 아니다.

### Required Outputs

| 산출물 | 내용 |
|---|---|
| `body_plan_v2_lua_bridge_report.json` | Lua bridge export 기록 |
| staged Lua bridge artifact | staging 경로에 생성 |
| `IrisLayer3Data.lua` | 기존 hash 기록 후 갱신 |
| `body_plan_v2_runtime_validation_report.json` | staged / workspace parity hash 확인 |
| `body_plan_v2_runtime_rollout_report.json` | row count, publish split, bridge hash 기록 |

### Bridge Contract

- `internal_only` row 제거 금지
- `internal_only` row의 3-3 body를 nil 처리 금지
- bridge row count = `2105`
- publish split = `internal_only 617 / exposed 1467`
- publish_state visibility contract 유지

### Exit Gate

- staged Lua bridge artifact 생성 완료
- `IrisLayer3Data.lua` 갱신 완료
- staged / workspace parity hash 일치
- runtime validation status = `ready_for_in_game_validation`
- closeout 문구가 staged/static 범위를 넘지 않음

---

## 9. Closeout Wording

### 허용 문구

- `staged closed`
- `static rollout closed`
- `ready_for_in_game_validation`
- `staged parity verified`
- `artifact parity verified`
- `bridge parity verified`
- `Lua bridge staged rollout pass`

### 금지 문구

- `deployed closeout`
- `Phase E pass`
- `full round close`
- `rollout pass`
- `user-facing surface verified`

---

## 10. Closeout Branch

### Case A — in-game validation 미수행

본 round의 기본값이다.

- Phase D: closed as pure observer
- Phase E-0: closed as regression gate pass
- Phase E: staged/static rollout closed
- `IrisLayer3Data.lua` parity pass
- static runtime validation = `ready_for_in_game_validation`
- deployed closeout 미선언
- in-game validation lane은 별도 QA round pending

### Case B — in-game validation 수행

본 round 밖의 별도 QA round 전용 branch다.

Case B로 전환하려면 Phase 0 scope override decision을 사전에 갱신하거나, 중간에 명시적 decision update로 manual in-game validation을 본 round scope에 포함해야 한다.

실제 in-game validation pass가 기록된 경우에만 별도 QA round에서 `deployed closeout`, `runtime rollout closeout`, `ready_for_release` 문구를 허용한다.

---

## 11. Round Closeout Criteria

아래 10개가 모두 만족되면 본 round를 close한다.

1. Phase 0 DECISIONS 3개 결정 기록 완료
2. walkthrough §6~§8 탐사 로그 재분류 경고 블록 삽입 완료
3. `2105` baseline 재시작 확인
4. Phase D pure observer artifact 생성, `quality_state` 필드 없음
5. Phase E-0 regression gate 9개 축 pass
6. quality distribution gate = `quality_baseline_v4`, `strong 1316 / adequate 0 / weak 768`
7. Phase E staged/static rollout 완료, parity hash 일치, status = `ready_for_in_game_validation`
8. `deployed closeout` / `full round close` 미사용
9. in-game validation 처리 방식이 `DECISIONS.md`에 기록됨
10. `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 본 round 결과 반영

---

## 12. Sealed Decisions

| 날짜 | 결정 | 본 round 정합 경로 |
|---|---|---|
| 2026-04-05 | body-role structural lint feedback-only | Phase D pure observer |
| 2026-04-06 | single writer | Phase D quality/publish 미수정 |
| 2026-04-06 | compose 외부 repair 금지 | 본 round 미도입 |
| 2026-04-06 | bridge `internal_only` 보존 | Phase E bridge row count `2105` |
| 2026-04-19 | SAPR `quality_baseline_v4` 봉인 | Phase E-0 quality distribution 일치 확인 |
| v0.2 §2-1 | 재개방은 scope_policy_override_round로만 | Phase 0 DECISIONS 기록 |
| v0.2 §7 Hold | D/E-0/E 후속 분리 | override round로 해제, deployed closeout 제외 |

---

## 13. Next Candidates

본 round 이후 후보는 짧은 메모로만 남긴다.

아래 항목은 후보 목록일 뿐이며, 개시 결정 자체는 별도 round opening이 필요하다.

- Manual in-game validation round
- `quality_baseline_v5` cutover round
- identity_fallback source expansion Group B
