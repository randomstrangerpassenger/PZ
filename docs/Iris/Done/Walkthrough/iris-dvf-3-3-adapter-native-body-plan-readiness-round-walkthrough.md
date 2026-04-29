# Iris DVF 3-3 Adapter / Native Body Plan Readiness Round Walkthrough

기준일: 2026-04-25  
대상 라운드: `Iris DVF 3-3 Adapter / Native Body Plan Readiness Round`  
상태: readiness closeout 완료, execution pending

---

## 0. 문서 목적

이 문서는 현재 세션에서 adapter/native body_plan migration debt를 어떻게 재정의했고, 어떤 계획 문서와 readiness artifact를 만들었으며, 어떤 수치로 Phase 0-8을 닫았는지 추적하기 위한 walkthrough다.

이 문서는 새 gate나 새 decision source가 아니다. Canonical 상태는 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`가 가진다. 이 문서는 이후 세션에서 “왜 이 round가 readiness closeout인지”, “무엇이 아직 execution pending인지”, “어느 artifact를 다음 round 입력으로 써야 하는지”를 빠르게 복원하기 위한 작업 로그다.

---

## 1. Session Input

이번 세션의 출발점은 user-provided roadmap과 multi-review feedback이었다.

핵심 요구:

| 요구 | 처리 |
|---|---|
| persisted old 3-profile label inventory | Phase 1 inventory로 측정 |
| v2 resolver fallback dependency inventory | Axis 3/4로 분리 측정 |
| 78 fallback row subclassification | `mechanical_ready / schema_gap`으로 분류 |
| execution queue seal | active 2084 row만 queue로 봉인 |
| silent 21 handling | execution queue가 아니라 inventory record로 분리 |
| status flow correction | Phase 6 `ready`, closeout `sealed`로 정리 |
| observer-only invariant verification | Phase 5 report로 검증 |
| top docs closeout | Phase 7 PASS 후 Phase 8에서만 반영 |

최종 사용 계획 문서:

`docs/Iris/iris-dvf-3-3-adapter-native-body-plan-readiness-round-plan.md`

최종 사용 계획 문서 버전:

`Draft v1.4-synthesis`

이 표기는 plan artifact가 planning authority로 작성된 draft였고, 그 draft를 기준으로 Phase 0-8을 실행했다는 뜻이다. Closeout authority는 Phase 6 readiness report, Phase 7 review, 그리고 Phase 8 top docs update가 가진다.

---

## 2. Current Problem Reframing

이번 세션에서 adapter/native body_plan migration debt는 아래처럼 재정의했다.

| 축 | 현재 해석 |
|---|---|
| 기존 문제 매핑 | legacy 3-profile -> native 6-profile migration 후속 debt |
| 재정의 | body_plan authority는 작동하고 adapter는 non-writer로 봉인됐지만, existing 3-3 row의 persisted `compose_profile`은 아직 old 3-profile label 상태 |
| 현재 닫힌 것 | default body_plan authority, EDPAS guard, compatibility adapter non-writer boundary, readiness inventory/queue/checklist |
| 실제 미해결 | `persisted_old_profile_count 2105`, active old-profile row `2084`, `legacy_fallback_target` dependency row `78` |
| 다음 라운드 범위 | active execution queue 2084개를 native metadata로 이전하고 silent 21 intake 여부를 execution opening에서 별도 결정 |
| 완료 조건 | active old-profile count 0, legacy fallback target count 0, default adapter dependency 0, rendered/Lua regression pass, 이후 별도 cleanup round에서 adapter diagnostic-only 또는 removal |

중요한 판정:

`readiness closeout complete, execution pending`

즉 migration debt 해결 준비는 끝났지만, migration debt 자체는 아직 open이다.

---

## 3. Phase 0 Opening

`docs/DECISIONS.md`에 2026-04-25 opening addendum을 추가했다.

Opening 핵심:

| 항목 | 값 |
|---|---|
| round type | `readiness_only` |
| writer role | `observer_only` |
| sealed artifact mutation | 금지 |
| rendered text mutation | 금지 |
| Lua bridge mutation | 금지 |
| legacy count reduction | 요구하지 않음 |
| execution round | 별도 opening 필요 |

Phase 0 artifact:

| artifact | 역할 |
|---|---|
| `phase0_opening/pass_criteria_contract.json` | Phase 6 report schema와 expected count 고정 |
| `phase0_opening/opening_decision_reflection.md` | opening decision 반영 메모 |

Status flow는 이 phase에서 명시적으로 닫았다.

| status | Phase 6 | Closeout |
|---|---|---|
| `execution_queue_status` | `ready` | `sealed` |
| `silent_metadata_inventory_status` | `ready` | `sealed` |

---

## 4. Implementation Script

이번 세션에서 readiness artifact 생성 스크립트를 추가했다.

`Iris/build/description/v2/tools/build/build_adapter_native_body_plan_readiness.py`

Script SHA-256:

```text
54ED577666D7891F6819A9913A495A987D2D0C9214A02881035D67EA674F95F5
```

이 스크립트는 readiness round 내부 diagnostic builder다. 후속 execution round는 이 스크립트를 migration executor로 재사용하지 않고, 별도 opening decision과 별도 execution tooling을 가져야 한다.

실행 명령:

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_readiness.py
```

스크립트 역할:

| 단계 | 출력 |
|---|---|
| Phase 0 | pass criteria / opening reflection |
| Phase 1 | 2105-row inventory + summary |
| Phase 2 | legacy source shape / taxonomy |
| Phase 3 | removal checklist / gate spec / resolver mode policy |
| Phase 4 | active execution queues + silent inventory |
| Phase 5 | observer invariant preservation report |
| Phase 6 | readiness report JSON/MD |

이 스크립트는 sealed rendered text, Lua bridge output, runtime artifact, resolver code를 수정하지 않는다. 신규 diagnostic/readiness artifact만 아래 root에 작성한다.

`Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/`

---

## 5. Phase 1 Inventory

Phase 1 output:

| artifact | 역할 |
|---|---|
| `phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.jsonl` | row-level inventory |
| `phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.summary.json` | count summary |

측정 결과:

| 축 | 값 |
|---|---:|
| inventory total | `2105` |
| active old profile | `2084` |
| silent old profile | `21` |
| persisted old profile | `2105` |
| resolver reached count | `2084` |
| legacy fallback target | `78` |
| non-fallback active metadata swap | `2006` |
| fallback-dependent active | `78` |
| silent metadata inventory | `21` |
| unresolved profile | `0` |
| unknown resolution source | `0` |

Resolution source distribution:

| normalized source | count |
|---|---:|
| `body_plan_v2` | `2006` |
| `legacy_fallback_target` | `78` |

---

## 6. Fallback Subclassification

78 fallback-dependent row는 모두 `mechanical_ready`로 분류되었다.

| subclass | count |
|---|---:|
| `mechanical_ready` | `78` |
| `schema_gap` | `0` |

이 결과 때문에 schema extension round는 이번 closeout 기준으로 자동 개방되지 않는다. 다만 policy상 `fallback_schema_gap_count > 0`이 되는 future run에서는 full adapter-removal execution이 block되고 schema extension round closeout이 선행되어야 한다.

---

## 6-1. Phase 2 Legacy Source Shape Definition

Phase 2 output:

| artifact | 봉인한 내용 |
|---|---|
| `phase2_definition/legacy_source_shape_definition.md` | legacy source shape의 세 축 정의 |
| `phase2_definition/legacy_profile_taxonomy.json` | old 3-profile label과 native target resolution rule |
| `phase2_definition/resolver_dependency_taxonomy.json` | Axis 4 reach scope와 resolver cleanup ownership |

핵심 정의:

| 축 | 정의 |
|---|---|
| Axis 2 | decisions row의 `compose_profile`이 `interaction_tool / interaction_component / interaction_output`인 persisted source shape debt |
| Axis 4 | active rendered preview row가 v2 resolver compatibility mapping reach scope에 들어가는지 측정 |
| Axis 3 | rendered preview의 `resolution_source == legacy_fallback_target` true fallback dependency |
| Axis 1 | `sentence_plan` artifact residue는 이번 round scope 밖 |

Target resolution rule:

| class | target rule |
|---|---|
| `non_fallback_active` | rendered preview의 `entry.resolved_profile` 사용 |
| `fallback_mechanical_ready` | fallback 후 resolved native target 사용 |
| `fallback_schema_gap` | `target_native_profile = null`, `schema_extension_required` |
| `silent_metadata_inventory` | direct legacy mapping을 proposal로만 기록, execution target으로 봉인하지 않음 |

---

## 6-2. Phase 3 Adapter Removal Checklist

Phase 3 output:

| artifact | 봉인한 내용 |
|---|---|
| `phase3_checklist/adapter_removal_checklist.md` | adapter removal 전제 gate 목록 |
| `phase3_checklist/adapter_removal_gate_spec.json` | readiness / execution / cleanup round responsibility split |
| `phase3_checklist/legacy_resolver_mode_policy.md` | resolver code modification ownership |

핵심 결정:

| round | responsibility |
|---|---|
| readiness round | inventory, queues, checklist, invariant report 생성. legacy count reduction 없음 |
| execution round | active old-profile count와 legacy fallback reach count를 data 수준에서 0으로 낮춤. resolver code modification 금지 |
| resolver cleanup round | diagnostic-only isolation 또는 complete removal 판단. 별도 opening 필요 |

Phase 3 policy는 `diagnostic-only isolation first`를 execution round에 넣지 않는다. Execution round는 resolver code state를 unchanged로 두고, cleanup round가 adapter code state를 결정한다.

Silent total close는 execution round 조건이 아니다. Silent 21 intake는 §1-7 decision에 따라 execution round opening에서 별도 결정한다.

---

## 7. Phase 4 Queues and Silent Inventory

Phase 4 output:

| artifact | line count | 의미 |
|---|---:|---|
| `phase4_active_execution_queue/execution_queue_non_fallback_active.2006.jsonl` | `2006` | fallback까지 가지 않는 active old-profile row |
| `phase4_active_execution_queue/execution_queue_fallback_dependent_active.78.jsonl` | `78` | `legacy_fallback_target`까지 도달한 active row |
| `phase4_silent_inventory/silent_metadata_inventory.21.jsonl` | `21` | execution queue가 아닌 silent metadata record |
| `phase4_summary/phase4_summary.json` | - | Phase 4 aggregate |

Phase 4 summary:

| 필드 | 값 |
|---|---:|
| queue A | `2006` |
| queue B | `78` |
| sealed active execution queue total | `2084` |
| silent metadata inventory | `21` |
| inventory total | `2105` |
| schema gap | `0` |
| unresolved | `0` |

Silent 21은 이번 readiness closeout에서 execution intake로 봉인하지 않았다. Intake 여부는 execution round opening에서 별도 결정한다.

---

## 8. Phase 5 Observer Invariants

Phase 5 output:

`phase5_invariants/observer_invariant_preservation_report.json`

결과:

| invariant | 결과 |
|---|---|
| row count | pass |
| active count | pass |
| silent count | pass |
| staged Lua hash unchanged | pass |
| workspace Lua hash unchanged | pass |
| runtime state unchanged | pass |
| additive observer lane hashes unchanged | pass |
| structural reclassification canonical hashes unchanged | pass |
| quality baseline v4 frozen | pass |
| internal_only bridge availability unchanged | pass |

중요 값:

| 축 | 값 |
|---|---|
| Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| runtime state | `ready_for_in_game_validation` |
| quality baseline v4 | `strong 1316 / adequate 0 / weak 768` |
| bridge availability | `internal_only 617 / exposed 1467` |

---

## 9. Phase 6 Readiness Report

Phase 6 output:

| artifact | 역할 |
|---|---|
| `phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.json` | final machine read point |
| `phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.md` | human summary |

Phase 6 result:

| 필드 | 값 |
|---|---|
| `overall_status` | `pass` |
| `execution_queue_status` | `ready` |
| `silent_metadata_inventory_status` | `ready` |
| `new_registration_guard_status` | `defined_and_dry_run_passed` |
| `observer_invariant_preservation_status` | `pass` |

중요한 해석:

Phase 6 report는 readiness report이므로 `ready`가 맞다. `sealed`는 Phase 7 adversarial review pass 이후 closeout snapshot에서만 읽는다.

Plan/report status reconciliation:

| source | `execution_queue_status` | `silent_metadata_inventory_status` | interpretation |
|---|---|---|---|
| plan v1.4 §9-2 Phase 6 report shape, as-uploaded if still stale | `sealed` | `sealed` | stale Phase 6 JSON example; violates §1-4 status semantics and requires backflow |
| plan v1.4 §1-4 status semantics intent | `ready` at Phase 6, `sealed` at closeout | `ready` at Phase 6, `sealed` at closeout | intended lifecycle |
| corrected plan §9-2 target state | `ready` | `ready` | required backflow state for Phase 6 report shape |
| generated Phase 6 report | `ready` | `ready` | actual artifact state |
| plan v1.4 §13-3 closeout pass JSON | `sealed` | `sealed` | closeout snapshot only |
| Phase 8 closeout snapshot | `sealed` | `sealed` | after Phase 7 PASS |

따라서 walkthrough의 governing interpretation은 `Phase 6 = ready`, `closeout = sealed`다. 후속 세션에서 plan §9-2가 `sealed / sealed`로 보이는 copy를 읽는다면, 그 copy는 Phase 6 status backflow가 미반영된 stale plan으로 보고 §9-2를 `ready / ready`로 정정해야 한다. `sealed / sealed`는 Phase 6 report shape가 아니라 plan §13-3 closeout pass JSON과 Phase 8 closeout snapshot에만 해당한다.

---

## 10. Phase 7 Review

Phase 7 output:

`phase7_review/adapter_native_body_plan_readiness_adversarial_review.md`

Review verdict:

`PASS`

Review에서 확인한 것:

| 질문 | 판정 |
|---|---|
| legacy count를 줄였는가 | 아니오 |
| sealed runtime/rendered/Lua hash를 바꿨는가 | 아니오 |
| schema-gap row를 숨겼는가 | 아니오, count `0` |
| status field가 enum을 따르는가 | 예 |
| Phase 6 report가 final read point인가 | 예 |
| 후속 execution/schema/cleanup/QA opening을 분리했는가 | 예 |

이 review는 Phase 8 top-doc update만 허용한다. Adapter removal, resolver cleanup, rendered text mutation, Lua bridge mutation, deployed closeout, manual in-game validation pass는 허용하지 않는다.

---

## 11. Phase 8 Top Docs Update

Phase 7 PASS 이후 top docs를 갱신했다.

| 문서 | 반영 |
|---|---|
| `docs/DECISIONS.md` | opening addendum + readiness closeout addendum |
| `docs/ARCHITECTURE.md` | 새 `11-61. Adapter removal criterion seal is closed as readiness-only inventory` 추가 |
| `docs/ROADMAP.md` | 새 `27. 2026-04-25 Addendum` 추가 |

Top-doc actual wording check:

| 문서 | 확인한 wording |
|---|---|
| `ARCHITECTURE.md` | `## 11-61. Adapter removal criterion seal is closed as readiness-only inventory` |
| `ARCHITECTURE.md` first sentence | `2026-04-25 기준 ... removal criterion을 sealed한 readiness-only round로 닫혔다. 이 section은 11-53의 compatibility adapter boundary를 수정하지 않고 ...` |
| `ROADMAP.md` Done 대응 | readiness plan v1.4, Phase 0-7 artifacts, inventory/queues/checklist/review 완료를 `### Done`에 기록 |
| `ROADMAP.md` conditional schema extension 대응 | `fallback_schema_gap_count > 0`일 때만 별도 opening, 이번 closeout 기준 `0`이므로 자동 개방되지 않음 |
| `ROADMAP.md` execution round 대응 | Adapter / Native Body Plan Execution Round를 별도 opening decision으로 열고 active execution queue `2084`를 입력으로 사용 |
| `ROADMAP.md` manual QA 대응 | manual in-game validation QA는 global pending으로 유지 |

Closeout snapshot:

| 필드 | 값 |
|---|---|
| closeout state | `closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready` |
| persisted old profile | `2105` |
| legacy fallback target | `78` |
| execution queue status | `sealed` |
| sealed active execution queue count | `2084` |
| silent metadata inventory status | `sealed` |
| silent metadata inventory count | `21` |
| schema gap disclosed | `true` |
| overall status | `pass` |

Top docs가 명시적으로 선언하지 않는 것:

- adapter removed
- legacy count reduced
- resolver compatibility mapping cleanup executed
- runtime QA pass
- deployed closeout
- ready for release

---

## 12. Final Artifact Map

Readiness root:

`Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/`

생성된 주요 산출물:

| phase | artifact |
|---|---|
| Phase 0 | `phase0_opening/pass_criteria_contract.json` |
| Phase 0 | `phase0_opening/opening_decision_reflection.md` |
| Phase 1 | `phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.jsonl` |
| Phase 1 | `phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.summary.json` |
| Phase 2 | `phase2_definition/legacy_source_shape_definition.md` |
| Phase 2 | `phase2_definition/legacy_profile_taxonomy.json` |
| Phase 2 | `phase2_definition/resolver_dependency_taxonomy.json` |
| Phase 3 | `phase3_checklist/adapter_removal_checklist.md` |
| Phase 3 | `phase3_checklist/adapter_removal_gate_spec.json` |
| Phase 3 | `phase3_checklist/legacy_resolver_mode_policy.md` |
| Phase 4 | `phase4_active_execution_queue/execution_queue_non_fallback_active.2006.jsonl` |
| Phase 4 | `phase4_active_execution_queue/execution_queue_fallback_dependent_active.78.jsonl` |
| Phase 4 | `phase4_silent_inventory/silent_metadata_inventory.21.jsonl` |
| Phase 4 | `phase4_summary/phase4_summary.json` |
| Phase 5 | `phase5_invariants/observer_invariant_preservation_report.json` |
| Phase 6 | `phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.json` |
| Phase 6 | `phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.md` |
| Phase 7 | `phase7_review/adapter_native_body_plan_readiness_adversarial_review.md` |

---

## 13. Reproduction Notes

Readiness artifact를 재생성하려면 repo root에서 아래 명령을 실행한다.

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_readiness.py
```

Expected summary:

```json
{
  "overall_status": "pass",
  "inventory_total": 2105,
  "persisted_old_profile_count": 2105,
  "active_old_profile_count": 2084,
  "silent_old_profile_count": 21,
  "legacy_fallback_target_count": 78,
  "non_fallback_active_metadata_swap_count": 2006,
  "fallback_dependent_active_count": 78,
  "fallback_mechanical_ready_count": 78,
  "fallback_schema_gap_count": 0,
  "silent_metadata_inventory_count": 21,
  "sealed_execution_queue_count": 2084,
  "unresolved_profile_count": 0
}
```

Line count quick check:

| file | expected lines |
|---|---:|
| `adapter_native_body_plan_readiness_inventory.2105.jsonl` | `2105` |
| `execution_queue_non_fallback_active.2006.jsonl` | `2006` |
| `execution_queue_fallback_dependent_active.78.jsonl` | `78` |
| `silent_metadata_inventory.21.jsonl` | `21` |

---

## 14. Next Round Handoff

다음 실질 해결 라운드는 `Adapter / Native Body Plan Execution Round`다.

Execution round input:

| input | count |
|---|---:|
| active queue A | `2006` |
| active queue B | `78` |
| active total | `2084` |

Execution round target:

| target | value |
|---|---:|
| active old profile count | `0` |
| legacy fallback target count | `0` |
| adapter default dependency count | `0` |

Execution round constraints:

- resolver code modification is not allowed
- rendered output regression must be `0 delta`
- Lua bridge hash must be unchanged or revalidated
- silent 21 intake must be decided at execution opening

After execution:

| follow-up | condition |
|---|---|
| Schema Extension Round | only if future `fallback_schema_gap_count > 0` |
| Resolver Compatibility Mapping Cleanup Round | after execution proves default adapter dependency count is 0 |
| Manual In-Game Validation QA | separate global pending round |

---

## 15. Current State Summary

이번 세션의 closeout은 다음처럼 읽는다.

```text
readiness closeout complete
execution pending
adapter not removed
legacy labels not reduced
runtime state unchanged: ready_for_in_game_validation
```
