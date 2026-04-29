# Iris DVF 3-3 Body Role Walkthrough

_Last updated: 2026-04-05_

## 1. 목적

이 문서는 `docs/dvf_3_3_body_role_execution_plan.md`가 이번 세션에서 실제로 어떻게 구현되고 검증됐는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 3-3 body role이 facts 확장 없이 decisions overlay와 compose 내부 repair로 닫혔는가
- Phase 1 audit과 Phase 2 agreement가 실제 수치로 어떻게 고정됐는가
- structural lint와 semantic linkage가 왜 현재 빌드를 소급 수정하지 않는 피드백 경로로 남았는가
- golden subset, regression, hard-fail gate가 full authority 기준으로 어떻게 닫혔는가
- identity_fallback 617 expansion plan이 어떤 backlog 입력으로 정리됐는가
- build/runtime/in-game까지 이번 round가 왜 closeout으로 읽히는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/dvf_3_3_body_role_execution_plan.md`
- `docs/dvf_3_3_body_closeout.md`

## 2. 시작점과 끝점

이번 작업은 sprint7 second-pass authority가 이미 존재하는 상태에서 시작했다.

시작 baseline:

- authority facts/decisions/rendered: `sprint7_overlay_preview_*`
- row count: `2105`
- origin counts: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- compose 상태: `primary_use` 중심 단일 경로
- decisions 상태: `layer3_role_check` 없음
- structural body-role lint: 없음

이번 세션의 끝점은 다음과 같다.

- Phase 0~9 범위 구현 및 산출물 작성 완료
- Phase 2 agreement: `1.0`
- full preview rendered rows: `2105`
- introduced hard fail: `0`
- regression rejected rows: `0`
- golden subset defined: `100`
- in-game validation: `pass`

즉, 이번 round는 초안 작성이 아니라 **policy -> audit -> overlay -> compose -> lint feedback -> regression -> runtime/in-game closeout**까지 한 번에 닫은 세션이었다.

## 3. 전체 흐름

실행 흐름은 크게 9단계였다.

1. Phase 0에서 3-3 body 역할과 3-3/3-4 경계를 하위 운영 문서로 재봉인한다.
2. Phase 1에서 현행 2105 row를 read-only audit으로 분류한다.
3. Phase 5를 병렬로 돌려 `identity_fallback 617`의 source expansion plan을 만든다.
4. Phase 2에서 `layer3_role_check` overlay와 validator를 추가한다.
5. Phase 3에서 compose가 overlay를 소비하고 repair를 내부 분기로 수행하게 만든다.
6. Phase 4에서 structural pattern을 lint/feedback 경로로 추가한다.
7. Phase 6에서 semantic weak candidate만 산출하고 자동 재분류는 막는다.
8. Phase 7에서 full preview, golden subset, regression, hard-fail gate를 닫는다.
9. Phase 8/9에서 override 기준, closeout 문서, in-game validation 기록까지 마무리한다.

아래부터는 이 순서를 그대로 따라간다.

## 4. Phase 0: Policy와 Boundary 재봉인

가장 먼저 닫은 것은 코드가 아니라 정책 문서였다.

핵심 문서:

- `docs/dvf_3_3_body_role_policy.md`
- `docs/3_3_vs_3_4_boundary_examples.md`

여기서 고정한 문장은 세 가지다.

- 3-3은 residual이 아니라 authoritative wiki body다.
- 3-3은 1·2·4 정보를 일부 포함할 수 있다.
- 단, 3-4 상세를 통째로 흡수하면 안 된다.

중요한 점은 이 문서들이 상위 문서의 하위 운영 문서로만 선언됐다는 것이다. 즉, body-role round는 새 헌법을 만든 것이 아니라 기존 `Philosophy/DECISIONS/ARCHITECTURE/ROADMAP`를 body-role에 적용 가능한 형태로 재봉인한 것이다.

## 5. Phase 1: Read-Only Audit

현행 body-role 상태는 먼저 손대지 않고 읽기 전용으로 분해했다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/report_layer3_body_adequacy_audit.py`

핵심 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/full_preview/layer3_body_adequacy_audit.full.jsonl`
- `Iris/build/description/v2/staging/body_role/phase7/full_preview/layer3_body_adequacy_summary.full.json`

최종 full audit 분포는 다음과 같이 닫혔다.

- row count: `2105`
- `item_centric`: `1440`
- `function_locked`: `48`
- `identity_echo`: `617`

origin 분포도 거의 그대로 대응한다.

- `cluster_summary`: `1440`
- `role_fallback`: `48`
- `identity_fallback`: `617`

이 숫자의 의미는 명확하다.

- 현재 3-3의 대부분은 이미 item-centric cluster body로 서 있다.
- 문제의 중심은 `identity_fallback 617`과 `role_fallback/function_locked 48`이다.
- 따라서 이번 round의 목표는 facts를 다시 만들기보다, **현행 facts가 3-3 body처럼 읽히도록 판정과 조합 경로를 다시 세우는 것**이었다.

## 6. Phase 5: identity_fallback 617 Expansion Plan

Phase 5는 Phase 1 직후 병렬로 돌렸다. runtime을 바꾸는 단계가 아니라 backlog 입력 정리 단계이기 때문이다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/build_identity_fallback_expansion_plan.py`

핵심 산출물:

- `Iris/build/description/v2/staging/body_role/phase1_parallel/identity_fallback_expansion_plan.json`

최종 bucket 분포:

- `bucket_1_existing_cluster_reusable`: `11`
- `bucket_2_net_new_cluster_required`: `599`
- `bucket_3_out_of_dvf_scope_group_c`: `7`

이 결과는 중요한 해석을 준다.

- `identity_fallback` 문제의 대부분은 compose tweak만으로 사라질 문제가 아니다.
- `617` 중 `599`는 결국 net-new cluster 설계가 필요한 backlog다.
- 따라서 이번 round는 `identity_only`를 숨기거나 삭제하지 않고, rendered 진단 메타와 expansion plan으로 추적하는 쪽이 맞다.

## 7. Phase 2: decisions overlay와 agreement

facts 슬롯은 끝까지 늘리지 않았다. 대신 decisions 쪽에 body-role 전용 overlay를 얹었다.

핵심 파일:

- `Iris/build/description/v2/tools/build/body_role_schema.py`
- `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- `Iris/build/description/v2/tools/build/validate_layer3_role_check.py`

추가한 핵심 필드:

- `layer3_role_check`
- `representative_slot`
- `body_slot_hints`
- `representative_slot_override`

허용 role check는 네 값으로 고정했다.

- `ADEQUATE`
- `FUNCTION_NARROW`
- `IDENTITY_ONLY`
- `ACQ_DOMINANT`

full agreement 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/full_preview/layer3_role_check_agreement.full.json`

최종 결과:

- row count: `2105`
- role check agreement rate: `1.0`
- representative_slot_override agreement rate: `1.0`
- full agreement rate: `1.0`
- mismatch count: `0`

expected/actual role check counts도 완전히 일치했다.

- `ADEQUATE`: `1440`
- `FUNCTION_NARROW`: `48`
- `IDENTITY_ONLY`: `617`

즉, Phase 2는 “수동 taxonomy를 나중에 참고하자”가 아니라 **수동 audit의 분포를 기계 overlay로 봉인한 단계**였다.

## 8. Phase 3: compose 내부 분기와 repair 흡수

이번 round의 기술적 핵심은 repair를 compose 외부 단계로 두지 않은 점이다.

핵심 파일:

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/data/compose_profiles.json`

실행 구조는 다음처럼 바뀌었다.

- 이전: `compose -> rendered`
- 현재: `compose(overlay 소비 + sentence plan 선택 + 내부 repair + quality_flag 태깅) -> rendered`

여기서 중요한 원칙은 세 가지였다.

- facts는 그대로 둔다.
- representative 선택은 `representative_slot`으로만 한다.
- repair는 compose 함수 내부에서만 수행한다.

`quality_flag`는 상태 축이 아니라 진단 메타데이터로만 남겼다. 허용값도 세 개로 고정했다.

- `function_narrow`
- `identity_only`
- `acq_dominant_reordered`

runtime 쪽에서는 이 진단 메타를 소비하지 않도록 처리했다.

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`

즉, rendered에는 진단 흔적이 남지만 Lua bridge와 UI surface에는 올라가지 않는다.

## 9. Phase 4와 Phase 6: structural lint와 semantic feedback

Phase 4와 6은 현재 빌드를 되감아 고치는 단계가 아니라, 다음 빌드 overlay 재판정에 연결되는 피드백 경로로 고정했다.

핵심 파일:

- `Iris/build/description/v2/tools/build/build_body_role_lint_feedback.py`
- `Iris/build/description/v2/tools/build/report_semantic_axis_linkage.py`
- `Iris/build/description/v2/tools/style/rules/structural_rules.json`

핵심 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/full_preview/body_role_full_preview_lint_report.json`
- `Iris/build/description/v2/staging/body_role/phase7/full_preview/body_role_full_preview_feedback.jsonl`

full preview lint 결과:

- surface rows: `2084`
- hard block rows: `0`
- feedback rows: `644`
- `BODY_LACKS_ITEM_SPECIFIC_USE`: `617`
- `SINGLE_FUNCTION_LOCK`: `27`

여기서 중요한 해석은 두 가지다.

- `LAYER4_ABSORPTION` introduced hard fail은 `0`이다.
- feedback `644`는 “지금 빌드를 실패시킨 row”가 아니라, 다음 round에서 `layer3_role_check` 재판정이나 source expansion 우선순위를 밀어주는 row다.

Phase 6도 같은 원칙을 따른다.

- semantic axis auto update: `false`
- requires decisions entry: `true`

즉, semantic weak candidate는 산출하지만 semantic axis를 자동으로 바꾸지 않는다. 이 결정 덕분에 기존 2-stage model 계약을 깨지 않고 body-role round를 닫을 수 있었다.

## 10. Phase 7: Full Preview, Golden Subset, Regression

formal closeout의 중심은 fixture가 아니라 full authority preview였다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/build_body_role_full_preview.py`
- `Iris/build/description/v2/tools/build/build_body_role_golden_subset.py`
- `Iris/build/description/v2/tools/build/report_body_role_regression.py`
- `Iris/build/description/v2/tools/build/report_layer3_role_check_agreement.py`

핵심 summary:

- `Iris/build/description/v2/staging/body_role/phase7/full_preview/body_role_full_preview_summary.json`

최종 full preview 수치:

- audit rows: `2105`
- overlay rows: `2105`
- rendered rows: `2105`
- agreement pass: `true`
- agreement rate: `1.0`
- baseline hard fail: `663`
- candidate hard fail: `663`
- introduced hard fail: `0`
- lint feedback rows: `644`
- semantic candidate rows: `644`
- regression overlap rows: `2084`
- regression rejected rows: `0`
- regression golden changed rows: `0`

여기서 hard fail `663`은 새로 생긴 문제가 아니라 authority baseline에 이미 있던 동일 count다. 핵심은 `introduced_hard_fail_count = 0`이라는 점이다.

golden subset 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/body_role_golden_subset.json`

golden subset은 `100`개로 고정했고, lane도 강제 포함했다.

- `multiuse_tool`: `1`
- `weapon_tool_hybrid`: `10`
- `distinctive_mechanic_item`: `10`
- `identity_role_fallback_row`: `20`
- `item_centric_fill`: `60`

regression 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/full_preview/body_role_full_preview_regression.json`

최종 결과:

- overlap rows: `2084`
- unchanged: `2084`
- rejected: `0`
- golden changed: `0`

즉, full preview closeout 시점에는 **meaning-preserving diff 승인조차 필요 없을 정도로 authority와 exact match**였다.

## 11. Phase 8: Regression Pack과 Manual Override 기준

Phase 8에서는 회귀 검토용 exemplar pack과 override 기준을 문서로 닫았다.

핵심 산출물:

- `Iris/build/description/v2/dvf_3_3_body_regression_pack.json`
- `Iris/build/description/v2/manual_override_body_policy.md`

regression pack lane 분포:

- `multiuse_tool`: `1`
- `weapon_tool_hybrid`: `12`
- `distinctive_mechanic_item`: `12`
- `acquisition_heavy_item`: `12`
- `identity_role_fallback_row`: `24`
- `cluster_summary_dominant_row`: `0`

마지막 lane이 `0`이라는 점도 중요하다. 이건 pack 누락이 아니라 **현재 surface authority에서 `cluster_summary + function_locked` 조합이 실제로 없다는 뜻**이다.

즉, regression pack은 이상적인 분류표가 아니라, 현재 production authority 위에서 실제로 잡히는 exemplar만 담는 운영 문서다.

## 12. Phase 9: Closeout과 In-Game Validation

마지막 단계는 문서 closeout과 수동 인게임 검증 기록이었다.

closeout 문서:

- `docs/dvf_3_3_body_closeout.md`

인게임 validation 산출물:

- `Iris/build/description/v2/staging/body_role/phase7/body_role_in_game_validation_result.json`
- `Iris/build/description/v2/staging/body_role/phase7/body_role_in_game_validation_result.md`

최종 인게임 결과:

- validation date: `2026-04-05`
- status: `pass`
- reported by: `user`
- basis: `all sampled body-role items displayed as expected in-game`
- surface scope:
  - `Iris context menu`
  - `Iris wiki panel`
  - `Iris browser`

이 결과로 이번 round는 build closeout만이 아니라 **runtime/in-game closeout**까지 포함한 상태로 읽히게 됐다.

## 13. 핵심 entrypoint

이번 walkthrough를 코드 기준으로 따라가려면 아래 파일들이 핵심이다.

- `Iris/build/description/v2/tools/build/report_layer3_body_adequacy_audit.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_expansion_plan.py`
- `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- `Iris/build/description/v2/tools/build/validate_layer3_role_check.py`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tools/build/build_body_role_lint_feedback.py`
- `Iris/build/description/v2/tools/build/report_semantic_axis_linkage.py`
- `Iris/build/description/v2/tools/build/build_body_role_full_preview.py`
- `Iris/build/description/v2/tools/build/build_body_role_golden_subset.py`
- `Iris/build/description/v2/tools/build/report_body_role_regression.py`
- `Iris/build/description/v2/tools/build/build_body_role_regression_pack.py`
- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`

## 14. 검증과 완료 판정

대표 테스트 명령은 다음이었다.

- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"`

최종 결과:

- 전체 테스트 `189`건 통과
- agreement pass
- golden subset defined
- regression rejected `0`
- introduced hard fail `0`
- in-game validation pass

현재 완료 판정은 이렇게 읽는다.

- DVF 3-3 body-role roadmap 범위는 완료
- 3-3 body는 authoritative wiki body로 closeout됨
- compose가 repair를 수행하고 linter/gate는 veto와 피드백을 수행하는 구조가 고정됨
- `IDENTITY_ONLY 617`은 숨겨진 실패가 아니라 expansion backlog 입력으로 명시적으로 남음
- 이번 round는 build/runtime/in-game pass까지 반영된 closeout 상태임

반대로 아직 후속 과제로 남는 것은 다음이다.

- `identity_fallback 617` source expansion 실행
- `bucket_2_net_new_cluster_required 599`에 대한 cluster 설계
- semantic weak candidate를 실제 semantic axis에 반영할지에 대한 별도 `DECISIONS.md`
- future source expansion 이후 분포 재측정

즉, 이번 round는 body-role roadmap을 끝낸 것이지, DVF/Iris 전체의 backlog를 없앤 것은 아니다.
