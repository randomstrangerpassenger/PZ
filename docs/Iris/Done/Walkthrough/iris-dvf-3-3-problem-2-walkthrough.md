# Iris DVF 3-3 Problem 2 Walkthrough

_Last updated: 2026-04-06_

## 1. 목적

이 문서는 [docs/iris-dvf-3-3-problem-2-final-integrated-execution-plan.md](./iris-dvf-3-3-problem-2-final-integrated-execution-plan.md)가 이번 세션에서 실제로 어떻게 구현되고 어디까지 닫혔는지 한 번에 따라가기 위한 walkthrough다.

초점은 다섯 가지다.

- 왜 이번 round의 출발점을 `active = runtime-adopted`, not `quality-pass`로 고정했는가
- `semantic_quality`가 새 runtime 상태 축이 아니라 기존 semantic axis의 derived/cache field로 어떻게 연결됐는가
- compose가 `semantic_quality`를 실제로 어떻게 소비하고 requeue/repair를 남기게 됐는가
- 왜 Phase A~C는 완료로 읽히고, Phase D는 일부 산출물이 있어도 여전히 닫힌 상태로 남는가
- 왜 이번 round에는 추가 인게임 검증이 필수 조건이 아닌가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-dvf-3-3-body-role-walkthrough.md`
- `docs/iris-dvf-3-3-problem-2-final-integrated-execution-plan.md`

## 2. 시작점과 현재 종료 판정

이번 round는 body-role closeout 이후 baseline에서 시작했다.

시작 baseline:

- total rows: `2105`
- active: `2084`
- silent: `21`
- active origin shorthand: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`

이 숫자가 뜻하는 바는 단순하다.

- current `active`는 이미 runtime 채택 상태다.
- active 안에 `identity_fallback 617`과 `role_fallback` 계열이 살아 있으므로, active를 곧바로 quality-pass로 다시 읽으면 기존 2-stage model의 runtime axis와 semantic axis가 다시 섞인다.

현재 종료 판정은 다음처럼 읽는다.

- Phase A 완료
- Phase B 완료
- Phase C 완료
- Phase D는 **판단 입력 산출물까지는 생성됐지만, 게이트를 통과하지 못해 닫힌 상태**

즉, 이번 round는 “active 의미 재정의까지 완료”가 아니라, **active 내부 semantic quality feedback loop를 구축하고 운영 기준선을 동결한 상태**로 끝난다.

## 3. 가장 중요한 결론

이번 round의 핵심 결론은 네 줄로 요약된다.

- `semantic_quality`는 새 runtime 상태 축이 아니다.
- `semantic_quality`는 decisions overlay에 기록되는 derived/cache field다.
- compose는 이 필드를 써서 repair와 requeue를 수행하지만, active/silent 외부 계약과 Lua bridge 계약은 바꾸지 않는다.
- 따라서 이번 round는 build/validator/operating artifact closeout으로 읽히고, 추가 인게임 검증은 필수 조건이 아니다.

## 4. Phase A: active 내부 품질 분포를 실측한다

Phase A의 목적은 감이 아니라 숫자로 현재 active 내부 품질 분포를 고정하는 것이었다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/report_layer3_active_quality_audit.py`
- `Iris/build/description/v2/tools/build/report_generated_weak_body_role_cross_analysis.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseA/layer3_active_quality_audit.jsonl`
- `Iris/build/description/v2/staging/semantic_quality/phaseA/layer3_active_quality_summary.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseA/cross_analysis_generated_weak_vs_body_role.json`

active audit 결과는 다음처럼 닫혔다.

- active total: `2084`
- `semantic strong`: `1316`
- `semantic adequate`: `0`
- `semantic weak`: `768`
- `quality_ratio`: `0.6315`
- `strong + FUNCTION_NARROW protected`: `20`

여기서 중요한 해석은 두 가지다.

- current active는 quality-pass 집합이 아니다.
- 동시에 active 내부 semantic 분포는 추적 가능한 숫자로 이미 고정 가능하다.

교차 분석도 같이 닫혔다.

- legacy/current active `generated::weak`: `133`
- body-role diagnostic union: `644`
- generated weak breakdown:
  - `ADEQUATE 111`
  - `FUNCTION_NARROW 6`
  - `IDENTITY_ONLY 16`

즉, 기존 `generated::weak 133`과 body-role diagnostic은 일부 겹치지만 동일 집합이 아니다. 이 점이 확인됐기 때문에, 기존 5개 핵심 결정을 바로 뒤집지 않고 Phase B/C로 넘어갈 수 있었다.

## 5. Phase B: `semantic_quality`를 overlay와 compose에 연결한다

Phase B의 핵심은 `semantic_quality`를 새 runtime 상태처럼 승격하지 않고, overlay와 compose에만 연결하는 것이었다.

핵심 파일:

- `Iris/build/description/v2/tools/build/body_role_schema.py`
- `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- `Iris/build/description/v2/tools/build/validate_layer3_role_check.py`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tools/build/build_body_role_full_preview.py`

여기서 고정한 규칙은 다음과 같다.

- `semantic_quality`는 derived/cache field다.
- 독립 수동 수정 대상이 아니다.
- authority drift가 감지되면 validator hard fail이다.

매핑 규칙도 A-3 기준으로 닫혔다.

- `ADEQUATE -> 기존 semantic 유지`
- `FUNCTION_NARROW -> 기본 weak, 단 기존 strong은 보호`
- `IDENTITY_ONLY -> weak`
- `ACQ_DOMINANT -> adequate`

compose 행동은 runtime 차단이 아니라 repair/diagnostic/requeue로만 연결했다.

- `strong + FUNCTION_NARROW`: semantic strong 유지, representative focus repair 적용
- `weak + IDENTITY_ONLY`: `quality_flag = identity_only`, requeue 등록
- `weak + FUNCTION_NARROW`: `quality_flag = function_narrow`, representative repair + requeue 등록
- `weak + ACQ_DOMINANT`: `quality_flag = acq_dominant_reordered`, acquisition/order repair 적용

이 단계에서 중요한 점은 “semantic axis에 행동 권한을 준다”와 “active 의미를 바꾼다”를 분리했다는 것이다. 이번 round는 전자까지만 수행했다.

## 6. Phase C: 추적, 재큐잉, baseline 동결

Phase C는 feedback loop를 운영 artifact로 고정하는 단계였다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/report_quality_tracking.py`
- `Iris/build/description/v2/tools/build/freeze_quality_baseline_v1.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_tracking_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseC/compose_requeue_candidates.jsonl`
- `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_baseline_v1.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_baseline_v1.md`
- `docs/semantic_quality_ui_exposure_agenda.md`

tracking 결과는 current baseline에서 다음처럼 닫혔다.

- total rows: `2105`
- active total: `2084`
- silent count: `21`
- semantic strong: `1316`
- semantic adequate: `0`
- semantic weak: `768`
- `quality_ratio`: `0.6315`
- `total_quality_ratio`: `0.6252`

weak breakdown도 같이 남긴다.

- `identity_only 617`
- `function_narrow 7`
- `acq_dominant 0`
- `adequate_preserved_weak 144`

requeue 결과는 다음처럼 닫혔다.

- requeue candidates: `624`
- `NEEDS_SOURCE_EXPANSION 617`
- `NEEDS_CLUSTER_REDESIGN 7`

이 숫자가 뜻하는 바도 분명하다.

- 현재 weak-active의 대부분은 compose tweak보다 source expansion backlog에 가깝다.
- 그러므로 이번 round에서 active를 곧바로 quality-pass 의미로 다시 정의하는 것은 시기상조다.

Phase C의 최종 산출물은 `quality baseline v1`이다. 이 baseline이 있기 때문에 이후 build에서 `quality_ratio`, lane loss, requeue 감소를 비교할 기준점이 생긴다.

## 7. Phase D: 재정의는 자동으로 열리지 않는다

Phase D는 “산출물이 생겼다”와 “phase가 열렸다”를 분리해서 읽어야 한다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/report_active_semantics_redefinition_simulation.py`
- `Iris/build/description/v2/tools/build/report_phase_d_readiness.py`
- `Iris/build/description/v2/tools/build/report_phase_d_gate_threshold_proposal.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseD/active_semantics_redefinition_simulation.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_readiness_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_gate_threshold_proposal.json`

시뮬레이션은 A/B/C 세 시나리오를 비교한다.

- Scenario A: `active = semantic adequate 이상`
- Scenario B: `active = adequate 이상 + body-role ADEQUATE`
- Scenario C: `active 유지, quality-pass 별도 추적`

current simulation 수치는 다음처럼 닫혔다.

- A: `active 1316`, `silent +768`
- B: `active 1296`, `silent +788`
- C: `active 2084`, `silent +0`

lane 손실은 더 직접적이다.

- A는 `identity_fallback 617` 전량 손실, `weapon_tool_hybrid 8` 손실
- B는 `identity_fallback 617`, `role_fallback 27` 전량 손실
- C만 current lane loss `0`

그 다음 readiness report에서 실제 게이트 상태를 본다.

현재 상태:

- `baseline_v1_frozen = pass`
- `quality_ratio_sustained = pass`
- `runtime_regression_clear = pass`
- `requeue_tolerability = pending_policy`
- `lane_stability = pending_policy`

즉, Phase D는 “준비 중”이 아니라 **의도적으로 closed**다. 아직 수치 근거는 충분히 쌓였지만, `requeue tolerability`와 `lane stability`를 어떤 문턱으로 닫을지 결정이 나지 않았기 때문이다.

## 8. threshold proposal이 뜻하는 것

이번 세션에서는 Phase D를 억지로 열지 않고, 대신 non-binding proposal artifact를 추가했다.

proposal 기준:

- requeue candidate ratio vs active `<= 0.10`
- lane loss ratio `<= 0.20`
- baseline count `< 10`인 small lane은 loss `0`

이 proposal은 [docs/DECISIONS.md](./DECISIONS.md)에 채택된 결정이 아니다. 운영자가 나중에 threshold를 닫을 때 참고하는 candidate다.

current proposal evaluation은 다음과 같다.

- requeue ratio: `0.2994`
- threshold pass: `false`
- lane stability:
  - A: fail
  - B: fail
  - C: pass

따라서 현재 operating recommendation은 단 하나다.

- `Phase D closed`
- `Scenario C 유지`

## 9. 왜 이번 round는 여기서 끝난다고 봐도 되는가

이번 round의 원래 목적은 active 내부에 semantic quality feedback loop를 구축하는 것이었다. 그 기준에서는 이미 필요한 것이 다 들어갔다.

- active 내부 semantic 분포를 수치로 본다.
- compose가 semantic quality에 따라 repair/requeue를 수행한다.
- requeue backlog가 source expansion 우선순위 입력으로 남는다.
- quality baseline이 동결된다.
- Phase D를 열 수 있는지 readiness로 판정한다.

반대로 이번 round의 비목표는 끝까지 유지됐다.

- active/silent 외부 계약 변경 없음
- 신규 runtime 상태 축 없음
- `no_ui_exposure` 실행 없음
- facts 슬롯 확장 없음
- Lua bridge 계약 변경 없음

따라서 이 round는 “재정의까지 못 가서 미완료”가 아니라, **원래 설계대로 A~C를 닫고 D를 closed 상태로 보존한 완료**로 읽는 것이 맞다.

## 10. 인게임 검증이 왜 필수는 아닌가

이번 round에는 추가 인게임 검증이 필수 조건이 아니다.

이유는 세 가지다.

- 이번 변경은 internal tracking, overlay, compose repair, requeue artifact 중심이다.
- Lua bridge 계약을 바꾸지 않았다.
- UI surface에 새 semantic quality 신호를 노출하지 않았다.

즉, 이번 round는 body-role round처럼 “실제 user-facing text surface가 바뀌었는지”를 검증하는 작업이 아니다. current full preview 기준 regression도 `0`이고 runtime regression signal도 `0`이므로, build/runtime 계약상 이번 closeout에는 추가 인게임 확인이 필요하지 않다.

다만 다음 경우에는 인게임 검증이 다시 필요하다.

- Phase D를 실제로 열어 active 의미를 재정의할 때
- `no_ui_exposure`를 재검토해 UI/validator surface를 바꿀 때
- Lua bridge나 rendered 소비 규약을 바꿀 때

즉, **이번 round에는 불필요하지만, future contract change round에서는 다시 필요**하다.

## 11. 핵심 entrypoint

코드 기준으로 이번 walkthrough를 따라가려면 아래 파일들이 핵심이다.

- `Iris/build/description/v2/tools/build/report_layer3_active_quality_audit.py`
- `Iris/build/description/v2/tools/build/report_generated_weak_body_role_cross_analysis.py`
- `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- `Iris/build/description/v2/tools/build/validate_layer3_role_check.py`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tools/build/report_quality_tracking.py`
- `Iris/build/description/v2/tools/build/freeze_quality_baseline_v1.py`
- `Iris/build/description/v2/tools/build/report_active_semantics_redefinition_simulation.py`
- `Iris/build/description/v2/tools/build/report_phase_d_readiness.py`
- `Iris/build/description/v2/tools/build/report_phase_d_gate_threshold_proposal.py`
- `Iris/build/description/v2/tools/build/build_body_role_full_preview.py`

## 12. 검증과 현재 완료 판정

대표 검증 명령은 다음과 같다.

- `python -B Iris/build/description/v2/tools/build/build_body_role_full_preview.py`
- `python -B Iris/build/description/v2/tools/build/report_phase_d_readiness.py`
- `python -B Iris/build/description/v2/tools/build/report_phase_d_gate_threshold_proposal.py`
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"`

current verification 결과:

- full preview rendered rows: `2105`
- introduced hard fail: `0`
- regression rejected: `0`
- `quality_ratio` 2회 연속 동일
- 전체 tests: `197` pass

현재 완료 판정은 이렇게 읽는다.

- DVF 3-3 problem 2 round의 **A~C 범위는 완료**
- Phase D는 **close 조건을 충족하지 못해 보류가 아니라 closed**
- current operating recommendation은 `active 유지 + quality-pass 별도 추적`, 즉 Scenario C다
- 추가 인게임 검증은 이번 round closeout의 필수 항목이 아니다

반대로 아직 future 과제로 남는 것은 다음이다.

- `requeue tolerability` threshold의 명시적 채택
- `lane stability` threshold의 명시적 채택
- threshold 채택 이후 Phase D 재개방 여부 판단
- 필요 시 active 의미 재정의용 staged migration
- future UI/Lua/runtime 계약 변경 round에서의 인게임 검증

즉, 이번 round는 roadmap을 실패한 것이 아니라, **원래 설계된 지점까지 정확히 닫고 다음 decision point를 명시한 상태**다.
