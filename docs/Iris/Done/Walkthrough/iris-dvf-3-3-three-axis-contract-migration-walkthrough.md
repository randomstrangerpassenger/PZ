# Iris DVF 3-3 Three-Axis Contract Migration Walkthrough

_Last updated: 2026-04-07_

## 1. 목적

이 문서는 [docs/iris-dvf-3-3-three-axis-contract-migration-execution-plan.md](./iris-dvf-3-3-three-axis-contract-migration-execution-plan.md)가 이번 세션에서 실제로 어떻게 구현됐는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 왜 이번 round를 problem 2의 연장이 아니라 별도 contract migration round로 읽어야 하는가
- `runtime_state / quality_state / publish_state` 3축이 어떤 순서로 문서와 산출물에 도입됐는가
- 왜 current cycle은 `B-path`를 채택했고, `identity_fallback`를 `internal_only`로 격리하는 방식으로 gate를 통과했는가
- offline preview, Lua bridge, runtime consumer가 어떤 파일과 어떤 수치로 실제 연결됐는가
- 왜 Phase 6은 단순 smoke check가 아니라 contract migration validation pack으로 구성됐는가
- 세션 후반 loose ammo 우클릭 오류를 어떻게 추적하고 어떤 범위로 고쳤는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-dvf-3-3-problem-2-walkthrough.md`
- `docs/iris-dvf-3-3-three-axis-contract-migration-execution-plan.md`

## 2. 시작점과 현재 끝점

이번 세션은 problem 2 round closeout 이후 상태에서 시작했다.

시작점은 다음처럼 고정돼 있었다.

- `active`는 이미 runtime 채택 상태였고 quality-pass 의미를 갖지 않았다.
- `semantic_quality`는 semantic axis의 derived/cache field로만 남아 있었다.
- `quality_baseline_v1`은 이미 동결돼 있었지만, `requeue_tolerability`와 `lane_stability`는 아직 `DECISIONS.md` 항목으로 채택되지 않았다.
- `publish_state` 축은 존재하지 않았고, `semantic_quality`는 여전히 `no_ui_exposure`로 묶여 있었다.

이번 세션의 끝점은 다음처럼 읽는다.

- Phase 0 완료
- Phase 1 완료
- Phase 2를 `B-path` 기준으로 완료
- Phase 3 완료
- Phase 3A 완료
- Phase 4 계약 명세 완료
- Phase 5 build/runtime wiring 완료
- Phase 6 manual validation pack 작성 완료
- 세션 후반 수동 인게임 재검증에서 loose ammo 우클릭 문제까지 해결되어 `.223 탄약`, `.308 탄약`, `9mm 탄약`, `산탄총 탄약`이 정상 동작함이 확인됨

다만 이 walkthrough 시점의 공식 closeout 판정은 아직 Phase 7 재봉인 전이다. 즉, 이번 세션은 **3축 계약 migration을 build/runtime/in-game 확인 직전까지 실제로 밀어 넣고, 마지막 closeout 문서 봉인만 남긴 상태**로 끝났다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 다섯 줄로 요약된다.

- 기존 2단 모델은 폐기되지 않았고, 3축 모델의 runtime 축으로 그대로 남았다.
- `semantic_quality`는 새 필드를 만들지 않고 post-migration authoritative quality contract로 재정의됐다.
- `publish_state`는 offline에서 결정되고 runtime Lua는 그것을 렌더 분기만 하는 consumer로 남았다.
- current cycle은 `B-path`를 채택해 `identity_fallback 617`을 `internal_only`로 격리하고 나머지 active surface를 `exposed`로 읽었다.
- 세션 후반 loose ammo 오류 수정까지 포함하면, 이번 round는 “계약 설계”가 아니라 **실제 runtime contract migration execution session**으로 읽는 것이 맞다.

## 4. 전체 흐름

실행 흐름은 크게 9단계였다.

1. 실행 계획을 3축 contract migration round로 재작성한다.
2. 선행조건과 threshold adoption evidence를 만든다.
3. `DECISIONS.md`에 threshold 2건과 `B-path` 실행 경로를 채택한다.
4. `identity_fallback`를 policy-isolation lane으로 분리하고 partial baseline v2를 동결한다.
5. 5-gate 재평가로 Phase D를 reopen하고, 이어서 Phase 3A guardrail을 봉인한다.
6. Phase 4에서 quality ownership, publish contract, Lua bridge semantics, constitutional guardrail을 문서화한다.
7. offline preview, Lua bridge, runtime consumer를 실제 코드로 연결하고 `quality_baseline_v3`를 동결한다.
8. manual in-game validation pack을 만든다.
9. 인게임에서 발견된 loose ammo 우클릭 오류를 추적해 vanilla bullet reload 경로를 nil-safe shim으로 보강한다.

아래부터는 이 9단계를 순서대로 본다.

## 5. 계획 재작성과 guardrail 반영

이번 세션의 첫 작업은 로드맵을 단순 초안이 아니라 실행 가능한 contract migration plan으로 재작성하는 것이었다.

핵심 문서:

- `docs/iris-dvf-3-3-three-axis-contract-migration-execution-plan.md`

이 문서는 여러 차례 수정됐다. 특히 review feedback을 반영하면서 다음 항목을 명시적으로 고쳤다.

- `Phase 3A`를 별도 게이트로 추가
- `quality adjudicator`를 single writer로, validator를 drift checker only로 분리
- `internal_only`가 runtime artifact에서 사라지는 것이 아니라 row와 `publish_state`를 유지한 채 default surface에서만 숨겨진다는 점을 명시
- `A-path / B-path`를 path-aware gate 구조로 재정의
- `quality_state = fail`을 reserved로 봉인
- `semantic_quality` 승격이 단순 승격이 아니라 의도적 의미 재설계임을 명시
- `fact_origin`이 quality proxy로 읽히지 않도록 합헌 가드레일을 추가

즉, 이번 세션은 구현보다 먼저 “어떤 구현이 합헌이고 어떤 구현이 위헌인가”를 문서에서 미리 닫는 데서 시작했다.

## 6. Phase 0과 Phase 1: 선행조건 정산, threshold adoption, 경로 선택

가장 먼저 만든 runtime authority artifact는 다음과 같다.

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase_0_precondition_checklist.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/threshold_adoption_evidence.json`

그 다음 `DECISIONS.md`와 `ROADMAP.md`에 threshold adoption을 반영했다.

Phase 1의 핵심은 세 가지였다.

- `requeue_tolerability` threshold 채택
- `lane_stability` threshold 채택
- current execution path를 `B-path`로 고정

이때 `B-path`는 다음처럼 읽혔다.

- `identity_fallback` lane은 삭제나 silent 전환이 아니라 **policy-isolation lane**으로 남긴다.
- exposed surface 판정은 나머지 active population 기준으로 읽는다.
- isolated lane은 이후 `internal_only` 후보군이 된다.

이 선택의 근거는 숫자로 분명했다.

- active total: `2084`
- identity fallback: `617`
- exposed candidate active total: `1467`

즉, `identity_fallback 617`을 현재 UI 노출 surface에서 분리하면, 나머지 lane은 quality gate와 requeue tolerability를 현실적으로 통과시킬 수 있었다.

## 7. Phase 2와 Phase 3: B-path isolation, partial baseline v2, Phase D reopen

`B-path` 채택 이후 만든 핵심 산출물은 다음과 같다.

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_policy_isolation_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase2_b_path_execution_manifest.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v2_partial.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v2_partial_observation_2.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase_d_reopen_iteration_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase_d_opening_evidence.json`

여기서 중요한 것은 full runtime 전체를 다시 좋은 것으로 읽은 것이 아니라, `publish_state = exposed` 예정 population만 별도로 읽었다는 점이다.

iteration 2 기준 gate 결과는 다음과 같이 닫혔다.

- `baseline_v2_frozen = pass`
- `quality_ratio_sustained = pass`
- `requeue_tolerability = pass`
- `lane_stability = pass`
- `runtime_regression_clear = pass`

핵심 수치는 다음과 같다.

- exposed candidate active total: `1467`
- isolated identity fallback count: `617`
- exposed candidate quality ratio: `0.8970688479890934`
- exposed candidate requeue ratio: `0.004771642808452625`

그 결과 Phase D는 [phase_d_opening_evidence.json](../Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase_d_opening_evidence.json) 기준 `phase_d_reopened_for_contract_migration`로 재개방됐다. 선택된 migration scenario는 `Scenario X`였고, 문서 안에서 이 시나리오는 기존 comparative scenario의 `Scenario C` 발전형으로 매핑됐다.

## 8. Phase 3A와 Phase 4: contract legality를 먼저 봉인하고 나서 구현한다

Phase 3A는 “이제 구현해도 되는가”를 닫는 사전 합법화 단계였다.

핵심 문서:

- `docs/phase4_entry_contract_guardrails.md`
- `docs/quality_state_ownership_spec.md`
- `docs/publish_state_spec.md`
- `docs/lua_bridge_publish_state_contract.md`
- `docs/philosophy_constitutionality_check.md`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase3a_guardrail_seal.json`

이 단계에서 실제로 봉인한 것은 다음과 같다.

- compose 외부 repair 단계는 금지되지만, quality/publish decision stage는 별도 contract stage로 허용
- quality owner는 single writer 하나만 허용
- validator는 drift checker only
- `quality_state = fail`은 reserved
- `internal_only` row는 runtime artifact에 남고, browser/wiki default surface가 `publish_state`를 보고 숨김 처리
- `fact_origin`은 provenance only이며 quality proxy로 쓰면 위헌

즉, Phase 4 구현은 자유로운 발명이 아니라, 이미 Phase 3A에서 legality가 닫힌 범위 안에서만 진행됐다.

## 9. Phase 5 구현 1: offline preview와 validator를 먼저 만든다

3축 계약을 바로 runtime에 꽂지 않고, 먼저 offline preview를 만들었다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/report_quality_publish_decision_preview.py`
- `Iris/build/description/v2/tools/build/validate_quality_publish_decision_preview.py`

핵심 테스트:

- `Iris/build/description/v2/tests/test_quality_publish_decision_preview.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview.jsonl`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_summary.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_validation_report.json`

preview summary는 다음처럼 닫혔다.

- total rows: `2105`
- active total: `2084`
- silent total: `21`
- quality state counts: `strong 1316 / adequate 0 / weak 768`
- publish state counts: `internal_only 617 / exposed 1467`
- identity fallback internal only count: `617`
- rendered missing active count: `0`

이 단계의 의미는 단순하다.

- quality/publish decision은 runtime이 아니라 offline에서 완전히 결정된다.
- preview validator가 `pass`이기 전에는 bridge와 consumer migration으로 넘어가지 않는다.

## 10. Phase 5 구현 2: Lua bridge와 runtime consumer를 실제로 연결한다

offline preview가 닫힌 뒤, bridge와 consumer를 실제로 바꿨다.

핵심 코드 변경:

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

핵심 runtime 검증 코드:

- `Iris/build/description/v2/tools/build/validate_interaction_cluster_phase_d_runtime.py`
- `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py`
- `Iris/build/description/v2/tests/test_style_runtime_closeout.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_lua_bridge_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_runtime_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v3.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase5_quality_publish_build_report.json`

이 단계에서 고정된 contract는 다음과 같다.

- `IrisLayer3Data.lua`는 `publish_state`를 row 단위로 가진다.
- `internal_only` row도 runtime artifact에는 남는다.
- `layer3_renderer.lua`는 `publish_state = internal_only`인 경우 default layer3 section 렌더를 숨긴다.
- browser/wiki consumer는 publish_state를 읽어 렌더만 분기하고, 품질 판단은 하지 않는다.

`quality_baseline_v3.json` 기준 상태는 다음과 같이 닫혔다.

- full runtime snapshot quality ratio: `0.6314779270633397`
- publish surface counts: `internal_only 617 / exposed 1467`
- exposed quality ratio: `0.8970688479890934`
- runtime validation status: `ready_for_in_game_validation`

즉, v3 baseline은 “preview가 맞다” 수준이 아니라, **preview + bridge + runtime validation이 전부 닫힌 상태**를 freeze한 것이다.

## 11. Phase 6 준비: manual in-game validation pack

Phase 5 closeout 이후에는 바로 closeout으로 가지 않고, 수동 인게임 검증용 pack을 만들었다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/build_quality_publish_phase5_runtime.py`
- `Iris/build/description/v2/tools/build/build_quality_publish_phase6_validation_pack.py`
- `Iris/build/description/v2/tools/build/build_quality_publish_phase6_in_game_result_template.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase6_in_game_validation_pack.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase6_in_game_validation_checklist.md`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/in_game_validation_result.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/in_game_validation_result.md`

중요한 점은 이 단계가 단순 smoke check가 아니라 contract migration validation pack이라는 것이다. 체크 항목은 처음부터 다음 다섯 축으로 구성됐다.

- `internal_only` row가 default surface에서 실제로 숨겨지는가
- `exposed` row의 3-3 body가 browser/wiki에서 정상 표시되는가
- context menu와 tooltip에서 regression이 없는가
- 1-3 / 2-3 등 다른 layer에 regression이 없는가
- 추가 field와 분기로 인한 성능 regression이 없는가

즉, Phase 6은 “대충 열어보고 끝”이 아니라, bridge contract migration이 실제 게임 안에서 맞게 소비되는지 검증하는 마지막 게이트였다.

## 12. 세션 후반 incident: loose ammo 우클릭 오류

세션 후반 실제 인게임 검증 중 예상하지 않았던 오류가 하나 나왔다.

- `.223 탄약` 우클릭 시 `Iris: View More`가 보이지 않거나
- 1발/묶음 상태 모두 우클릭 시 error가 발생했다

처음에는 Iris context menu가 stack-wrapped item을 제대로 못 푸는 문제로 보였기 때문에, 먼저 [IrisContextMenu.lua](../Iris/media/lua/client/Iris/UI/Wiki/IrisContextMenu.lua)를 일반화했다.

1차 수정 내용:

- direct `InventoryItem`
- `candidate.items`
- `candidate:getItems()`
- Java list `container:get(0)`

를 모두 따라가 첫 실제 inventory item을 찾게 바꿨다.

그다음 실제 원인을 찾기 위해 `C:\Users\MW\Zomboid\console.txt`를 읽었고, stack trace는 vanilla 쪽 `ISInventoryPaneContextMenu.doReloadMenuForBullets`를 가리켰다. 즉, 우리 메뉴 엔트리가 붙기 전에 vanilla loose ammo reload menu 경로 자체가 터지고 있었다.

원인은 두 겹이었다.

- vanilla `createMenu`가 stack wrapper를 `v.items[1]` 전용으로만 가정
- `doReloadMenuForBullets` tooltip 생성에서 `item:getGunType()`가 비어 있는 탄창/탄약 경로를 nil-safe 없이 처리

그래서 최종 수정은 `IrisContextMenu.lua` 안에서 vanilla bullet reload 경로를 좁게 shim하는 방식으로 넣었다.

핵심 추가 내용:

- `safeInvoke(...)`
- `buildAmmoReloadTooltipDescription(...)`
- `patchVanillaBulletReloadMenu()`

이 shim은 다음을 보장한다.

- `bullet:getFullType()`가 nil이면 바로 return
- inventory iteration이 nil-safe로 진행
- magazine tooltip에서 `gunType`이 없는 경우도 죽지 않음
- weapon branch는 기존 vanilla `doBulletMenu`를 그대로 사용
- patch는 `_irisSafeBulletReloadPatchApplied` guard로 중복 적용되지 않음

즉, 이번 수정은 `.223 탄약`만 예외 처리한 것이 아니라, **같은 loose ammo reload path를 타는 탄약 전반**에 적용되는 공통 보강이었다.

## 13. 세션 종료 시점의 인게임 결과

세션 후반 재검증에서 사용자가 직접 다음을 확인했다.

- `.223 탄약` 우클릭 정상
- `.308 탄약` 우클릭 정상
- `9mm 탄약` 우클릭 정상
- `산탄총 탄약` 우클릭 정상
- `Iris: View More` 정상 표시
- browser/wiki 열기 정상
- 에러 재발 없음

이 결과는 아직 별도 closeout packet으로 재봉인되지는 않았지만, 세션 운영 관점에서는 **Phase 6 manual validation의 핵심 blocking issue가 해소됐다**는 뜻이다.

정적 검증 상태도 다시 맞춰졌다.

- `quality_publish_runtime_report.json = ready_for_in_game_validation`
- `test_interaction_cluster_phase_d_runtime`
- `test_style_runtime_closeout`
- 전체 `203 tests`

모두 통과했다.

## 14. 현재 남은 일

이번 세션에서 사실상 contract migration 구현은 끝났다. 남은 것은 closeout 봉인이다.

남은 작업은 다음 세 가지다.

- `in_game_validation_result.json/.md`를 실제 pass 결과로 동결
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 final closeout 반영
- round closeout packet 작성

즉, 현재 상태를 가장 정확하게 한 줄로 쓰면 이렇다.

**3축 contract migration은 build/runtime/in-game 수준에서 구현과 재검증까지 완료됐고, 공식 문서 재봉인만 남아 있다.**
