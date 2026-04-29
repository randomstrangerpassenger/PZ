# Iris DVF 3-3 Semantic Axis Policy Round Walkthrough

_Last updated: 2026-04-19_

## 1. 목적

이 문서는 `Iris DVF 3-3 Semantic Axis Policy Round(SAPR)`가 이번 세션에서 어떻게 닫혔는지 한 번에 따라가기 위한 walkthrough다.

이번 walkthrough의 초점은 여섯 가지다.

- 왜 SAPR를 implementation round가 아니라 policy authority round로 봉인했는가
- 왜 시작점을 `SDRG PASS + semantic decision input`으로 고정했는가
- 왜 weak를 단일 묶음이 아니라 family 단위로 분해했는가
- 왜 `Option C`가 선택됐고, 왜 current round에서 `quality_baseline_v4`를 유지했는가
- canonical 3문서가 어떤 문장으로 갱신됐는가
- 무엇이 이번 round의 완료 범위이고, 무엇이 별도 execution round로 남았는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/Iris/iris-dvf-3-3-semantic-axis-policy-round-final-integrated-plan.md`

## 2. 시작점과 끝점

이번 세션의 시작점은 `SDRG`가 이미 observer authority로 닫혀 있고, semantic decision이 별도 explicit round로만 남아 있는 상태였다.

- `round_exit_status = PASS`
- current handoff authority
  - runtime row count: `2105`
  - runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish split: `internal_only 617 / exposed 1467`
- historical comparison baseline
  - runtime path counts: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- `quality_baseline_v4`
  - `strong 1316 / adequate 0 / weak 768`
  - `quality_ratio = 0.6314779270633397`
- decision-required item
  - `quality_baseline_v4 -> v5` 승계 여부
  - weak signal을 semantic axis candidate로 다룰지 여부

이번 세션의 종료점은 SAPR closeout 기준 아래와 같다.

- selected option: `Option C — signal-type differential`
- current baseline decision: `quality_baseline_v4` 유지
- carry result
  - `ADMIT_AS_AXIS_CANDIDATE`
    - `structural feedback weak candidate`
    - `source-expansion post-round new weak`
  - `KEEP_OBSERVER_ONLY`
    - `body-role mapping weak`
    - `adequate 유지군`
    - `legacy/generated weak reference`
  - `CARRY_TO_BASELINE_V5`
    - 없음
- `immediate_next_round_planned = false`

즉 이번 세션은 코드를 바꾸는 execution round가 아니라, `DECISIONS.md / ARCHITECTURE.md / ROADMAP.md`를 동시에 갱신하는 policy authority closeout이었다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 일곱 줄로 요약된다.

- SAPR는 weak signal을 한 번에 승격하는 round가 아니라 weak-family carry policy를 닫는 round로 구현됐다.
- `semantic_decision_input_packet.json`은 끝까지 decision input only로 유지됐다.
- weak family는 `observer-only / candidate / carry` 세 상태로만 읽히게 봉인됐다.
- current selection은 `Option C`이고, candidate admission만 허용하며 actual carry는 닫지 않았다.
- current round에서 `quality_baseline_v4 -> v5` 승계는 채택되지 않았다.
- runtime/publish 계약, single writer, `no_ui_exposure`, retroactive boundary는 그대로 유지됐다.
- SAPR는 terminalized 상태로 닫혔고, 후속 구현이 필요하면 별도 execution round로만 이어진다.

## 4. 전체 흐름

이번 세션의 흐름은 크게 일곱 단계였다.

1. plan 문서를 v1.1까지 수정해 Option A 경계, dual-layer baseline, sealed legacy weak reference를 다시 봉인했다.
2. `Phase 0 / 1`에서 input freeze와 scoping 문서를 만들고 round 범위를 두 질문으로 고정했다.
3. `Phase 2`에서 weak taxonomy 5군과 current-state diagnostic을 만들었다.
4. `Phase 3`에서 admission rule 4문과 Option A-E를 enumerate했다.
5. `Phase 4`에서 carry policy를 `KEEP_OBSERVER_ONLY / ADMIT_AS_AXIS_CANDIDATE / CARRY_TO_BASELINE_V5` 3상태로 고정하고 `Option C`를 선택했다.
6. `Phase 5 / 6`에서 canonical patch draft와 consumer-side consistency review를 만들었다.
7. `Phase 7 / 8`에서 canonical 3문서를 반영하고 closeout report, optional implementation handoff를 남겼다.

아래부터는 이 순서를 그대로 따라간다.

## 5. Plan Revision: 왜 v1.1까지 다시 잠갔는가

바로 artifact를 쓰지 않고 먼저 계획 문서를 수정한 이유는 SAPR의 핵심 경계가 처음부터 흔들렸기 때문이다.

수정한 핵심 포인트는 다음과 같다.

- `Option A`와 `backlog-only 채택 불가`의 충돌을 제거했다.
  - `Option A`를 explicit gated carry 아래의 `all KEEP_OBSERVER_ONLY` 인스턴스로 재정의했다.
- `generated::weak 133`을 재판정 대상처럼 읽히지 않게 바꿨다.
  - `sealed legacy weak reference`
- Phase 0 baseline을 dual-layer로 분리했다.
  - `historical_comparison_baseline`
  - `current_handoff_authority`
- `all delta reasoning in SAPR uses current_handoff_authority unless explicitly marked historical`를 고정했다.
- `consecutive-build`와 actual carry의 관계를 분리했다.
  - admission precondition과 explicit carry decision을 다르게 읽게 했다.

즉 v1.1의 역할은 SAPR가 “이미 답을 정해 둔 round”처럼 읽히지 않게 하고, 동시에 sealed rule을 다시 열지 못하게 하는 것이었다.

## 6. Phase 0 / 1: Input Freeze와 Scope Lock

첫 산출물은 아래 세 파일이었다.

- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase0_input_freeze/sapr_input_freeze.json`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase0_input_freeze/sapr_input_freeze.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase1_scoping/sapr_scoping_v0_1.md`

여기서 고정한 핵심 값은 다음과 같다.

- round scope
  - weak signal을 semantic axis 후보로 다룰 것인가
  - `quality_baseline_v4`를 `v5`로 승계할 것인가
- canonical input
  - `semantic_decision_input_packet.json`
  - `semantic_decision_review.md`
  - `decisions_md_patch_proposal.md`
  - `quality_baseline_v4.json`
  - `source_expansion_remeasurement_terminal_handoff.json`
  - `source_expansion_remeasurement_terminal_status.json`
  - `body_role_lint_report.json`
- dual-layer baseline
  - historical comparison baseline: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
  - current handoff authority: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- current quality snapshot
  - `strong 1316 / adequate 0 / weak 768`

또한 Phase 3 entry mode는 아래처럼 읽혔다.

- prior patch proposal: present
- admissibility: pass
- 결과: `expansion mode`

즉 SAPR는 빈 종이 위에서 시작한 것이 아니라, `SDRG`가 남긴 decision input을 읽되 current round scope 밖의 선택은 다시 열지 않는 방식으로 출발했다.

## 7. Phase 2: Weak Taxonomy와 Current-State Diagnostic

그다음에는 weak를 policy input 형태로 다시 분해했다.

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase2_diagnostic/semantic_weak_taxonomy.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase2_diagnostic/sapr_current_state_diagnostic.json`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase2_diagnostic/sapr_current_state_diagnostic.md`

여기서 고정한 family는 다섯 개다.

- `body-role mapping weak`
  - current snapshot: `624`
- `adequate 유지군`
  - current snapshot: `0`
- `structural feedback weak candidate`
  - current projection: `624`
- `legacy/generated weak reference`
  - sealed reference: `133`
- `source-expansion post-round new weak`
  - current snapshot: `0`

current weak cross-cut은 아래처럼 읽혔다.

- weak total: `768`
- weak by fact origin
  - `identity_fallback 617`
  - `cluster_summary 144`
  - `role_fallback 7`
- weak by structural flag
  - `BODY_LACKS_ITEM_SPECIFIC_USE 617`
  - `FUNCTION_NARROW 7`
  - `none 144`

이 단계의 핵심은 recommendation을 하지 않고, “어떤 정책이 어느 row 범위를 건드리게 되는가”만 수치로 잠근 것이다.

## 8. Phase 3: Admission Rule과 Option Enumeration

그다음에는 어떤 weak가 candidate family 자격을 갖는지부터 먼저 봉인했다.

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase3_options/semantic_axis_candidate_admission_rule.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase3_options/sapr_policy_options_enumeration.md`

admission rule은 네 문장으로 닫혔다.

1. `auto update` 금지
2. same-build mutation 금지
3. source expansion 이후 재측정에서 재현성 확보
4. explicit `DECISIONS.md` 채택 이후에만 axis carry 허용

그 위에서 Option A-E를 모두 열거했다.

- `Option A`
  - explicit gated carry 아래의 all-`KEEP_OBSERVER_ONLY`
- `Option B`
  - consecutive-build conditional promote
- `Option C`
  - signal-type differential
- `Option D`
  - manual batch promote
- `Option E`
  - hybrid

여기서 중요한 봉인선은 두 가지였다.

- `Option A`는 ungated backlog-only가 아니다.
- `Option D / E`의 `semantic_quality_override`는 writer가 아니라 decision-stage input으로만 읽혀야 한다.

즉 Phase 3의 역할은 “무슨 옵션을 고를까”보다 먼저 “선택 가능한 옵션의 경계가 어디까지인가”를 잠그는 것이었다.

## 9. Phase 4: 왜 Option C가 선택됐는가

정책 선택 산출물은 아래 세 개였다.

- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase4_selection/baseline_carry_policy.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase4_selection/semantic_weak_carry_matrix.json`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase4_selection/sapr_policy_selection.md`

선정안은 `Option C — signal-type differential`이었다.

선택 결과는 아래처럼 닫혔다.

- `KEEP_OBSERVER_ONLY`
  - `body-role mapping weak`
  - `adequate 유지군`
  - `legacy/generated weak reference`
- `ADMIT_AS_AXIS_CANDIDATE`
  - `structural feedback weak candidate`
  - `source-expansion post-round new weak`
- `CARRY_TO_BASELINE_V5`
  - 없음

이 선택의 의미는 단순하다.

- weak 전체를 한 번에 승격하지 않는다.
- structural/post-round family만 operating-rule candidate로 인정한다.
- current round에서 writer는 활성화하지 않는다.
- current round에서 `quality_baseline_v4`는 그대로 유지한다.

즉 SAPR는 “candidate family는 있다”까지는 닫았지만, “지금 곧바로 carry한다”까지는 가지 않았다.

## 10. Phase 5 / 6: Patch Draft와 Consistency Review

선택안이 고정된 뒤에는 patch draft와 consumer-side review를 만들었다.

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase5_patch_draft/sapr_decisions_patch_draft.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase5_patch_draft/sapr_architecture_patch_draft.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase5_patch_draft/sapr_roadmap_patch_draft.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/phase6_consistency_review/sapr_consistency_review.md`

Phase 6 review는 다섯 시나리오를 모두 `PASS`로 닫았다.

- next-build consumption
- single-writer 지위 유지
- validator drift-checker-only 지위 유지
- publish_state 연쇄 영향 차단
- gate threshold 영향

여기서 최종적으로 다시 확인한 것은 아래 네 가지다.

- current round는 `quality_state`를 emit하지 않는다.
- `quality/publish decision stage` single writer 지위는 유지된다.
- `internal_only 617 / exposed 1467` split은 바뀌지 않는다.
- threshold reopen이 필요하면 별도 round로만 넘긴다.

## 11. Phase 7 / 8: Canonical Docs Sync와 Optional Handoff

canonical output과 closeout은 아래 파일들로 닫혔다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/closeout/sapr_closeout_report.md`
- `Iris/build/description/v2/staging/semantic_axis_policy_round/handoff/sapr_implementation_handoff.md`

`DECISIONS.md`에는 새 SAPR 항목이 추가됐다.

- semantic weak candidate는 자동 반영되지 않는다.
- semantic axis 반영은 explicit decision으로만 닫는다.
- runtime/publish 계약은 이번 round에서 변경하지 않는다.
- `no_ui_exposure`는 유지한다.

`ARCHITECTURE.md`에는 두 가지가 반영됐다.

- weak candidate carry policy가 SAPR에서 policy-resolved hold로 닫혔다는 점
- current semantic decision authority after SAPR read point

`ROADMAP.md`에는 두 가지가 반영됐다.

- body-role addendum에 `SAPR semantic weak carry policy closeout 완료`
- SDRG addendum의 Q1/Q2를 resolved 상태로 이동

즉 Phase 7의 역할은 staging provenance를 남기는 것만이 아니라, current canonical read point를 앞으로도 흔들리지 않게 만드는 것이었다.

## 12. Closeout과 Reopen 조건

closeout report는 SAPR를 아래처럼 terminalized 상태로 기록한다.

- selected option: `Option C`
- current baseline decision: `v4 유지`
- `immediate_next_round_planned = false`

허용되는 reopen 조건은 세 가지뿐이다.

1. source-expansion 이후 새 weak family가 생김
2. UI 정책이 바뀌어 weak를 exposed surface까지 끌고 가야 함
3. baseline drift가 누적돼 `v5` 이후 재승계가 필요함

허용되지 않는 reopen 사유도 같이 봉인했다.

- 문장이 어색해 보여서
- weak 수치가 보기 싫어서
- `active`를 quality-pass처럼 보이게 하고 싶어서

즉 SAPR는 “다음에 마음이 바뀌면 다시 열 수 있는 문서”가 아니라, reopen 조건이 좁게 잠긴 governance artifact다.

## 13. 검증 메모

이번 세션에서 실행한 검증은 문서/JSON 정합성 수준이다.

- `sapr_input_freeze.json` 파싱 확인
- `sapr_current_state_diagnostic.json` 파싱 확인
- `semantic_weak_carry_matrix.json` 파싱 확인
- canonical 3문서 반영 구간 spot-check

즉 이번 round는 builder/test 중심 구현 세션이 아니라 policy authority closeout 세션이었고, 검증도 그 성격에 맞게 artifact consistency 확인 위주로 수행됐다.

## 14. 현재 읽기 규칙

이번 세션 이후 current SAPR는 아래처럼 읽는 것이 맞다.

- implementation round가 아니다.
- `semantic_decision_input_packet.json`은 decision input only다.
- weak family는 single writer 바깥에서 direct write instruction이 되지 않는다.
- current build의 `quality_state`와 `publish_state`는 바뀌지 않는다.
- candidate family는 operating-rule input으로만 유지된다.
- baseline `v5`는 아직 없다.
- 후속 구현이 필요하면 `sapr_implementation_handoff.md`를 시작점으로 한 별도 execution round로만 연다.

한 줄로 요약하면, 이번 세션은 `SDRG가 남긴 두 질문`을 실제로 **input freeze -> weak taxonomy -> option enumeration -> differential selection -> canonical docs sync -> terminal closeout** 체계로 닫아 current semantic decision authority로 고정한 세션이었다.
