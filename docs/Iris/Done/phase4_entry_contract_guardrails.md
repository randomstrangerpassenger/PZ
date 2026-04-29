# Phase 4 Entry Contract Guardrails

> 상태: sealed v1.0  
> 기준일: 2026-04-06  
> 목적: Phase 4 진입 전에 C-1, C-2, I-1, I-2를 선행 봉인하고, contract design과 implementation이 기존 closeout 원칙을 침범하지 않도록 guardrail을 고정한다.

이 문서는 `docs/iris-dvf-3-3-three-axis-contract-migration-execution-plan.md`의 `Phase 3A` companion 문서다. 효력은 2026-04-06자 `DECISIONS.md` guardrail 항목 채택으로 발생했다.

---

## 1. 범위

이 문서는 다음 네 질문에만 답한다.

1. post-compose에 별도 decision stage를 둘 수 있는가
2. `quality_state`의 single writer는 누구인가
3. `internal_only`의 Lua bridge/runtime semantics는 무엇인가
4. 이번 round에서 `quality_state`가 실제로 허용하는 값은 무엇인가

이 문서는 threshold 숫자, A/B path 선택, UI copywriting, actual implementation diff를 닫지 않는다.

---

## 2. Decision Stage Legality

기존 원칙인 `compose 외부 repair 단계 금지`는 유지한다. 다만 이번 round에서는 아래처럼 적용 범위를 재정의한다.

- 계속 금지되는 것
  - post-compose repair
  - post-compose rewrite
  - post-compose lint fix
  - post-compose text mutation
- 허용되는 것
  - post-compose `quality/publish decision stage`

허용 근거는 다음과 같다.

- 이 stage는 rendered text를 고치지 않는다.
- 이 stage는 `quality_state`와 `publish_state`를 최종 결정하는 contract decision stage다.
- 즉, compose 바깥의 또 다른 repair layer가 아니라 ownership이 다른 결정 layer다.

따라서 이번 round에서 허용되는 것은 "compose 밖에서 다시 고치기"가 아니라, "compose가 끝난 산출물에 대해 노출 계약을 판정하기"다.

---

## 3. Single Writer Rule

이번 round에서 `quality_state`와 `publish_state`의 기록자는 하나뿐이다.

- single writer: `quality/publish decision stage`
- non-writer:
  - overlay builder
  - compose
  - validator
  - Browser/Wiki consumer
  - Lua bridge

validator의 역할은 다음으로 한정한다.

- drift checker only
- ownership 위반 감지
- bridge contract drift 감지
- emitted state inconsistency 감지

validator는 어떤 경우에도 `quality_state`나 `publish_state`를 기록하거나 수정하지 않는다.

---

## 4. `semantic_quality`의 의미 재설계

이번 round는 `semantic_quality`의 단순 승격이 아니라 **의도적 의미 재설계** 다.

- pre-migration `semantic_quality`
  - upstream semantic/body-role diagnostic
  - derived/cache field
  - current problem 2 closeout authority
- post-migration redefined `semantic_quality` 또는 `quality_state`
  - downstream publish decision을 구동하는 authoritative contract
  - `quality/publish decision stage`의 단일 기록 대상

중요한 점은 다음이다.

- 이는 기존 closeout을 부정하는 것이 아니다.
- 시간축이 다르다.
- problem 2 round의 `semantic_quality = derived/cache` 결정은 pre-migration authority로 유지된다.
- contract migration round 이후에만 redefined semantic contract가 새 authority가 된다.

향후 `DECISIONS.md` closeout 문구도 이 시간축을 유지해야 한다.

---

## 5. Allowed State Set

이번 round의 `quality_state` 실제 허용값은 다음 셋으로 한정한다.

- `strong`
- `adequate`
- `weak`

`fail`은 reserved 상태다.

- 이번 round에서는 emit 금지
- validator가 `quality_state = fail`을 감지하면 hard fail
- `fail`의 의미는 별도 round에서 정의되기 전까지 contract에 포함시키지 않는다

---

## 6. Lua Bridge Runtime Semantics

`internal_only`는 runtime artifact와 user-facing default surface를 분리하기 위한 상태다. 따라서 bridge semantics는 다음처럼 고정한다.

- Lua bridge는 `internal_only` row를 제거하지 않는다.
- Lua bridge는 `internal_only` row의 3-3 body를 nil로 만들지 않는다.
- Lua bridge는 row와 3-3 body와 `publish_state`를 함께 유지한다.
- Browser/Wiki consumer가 `publish_state`를 읽어 default surface 렌더 여부만 분기한다.

즉, `internal_only`는 **bridge availability 감소** 가 아니라 **consumer visibility suppression** 이다.

---

## 7. Validator vs Runtime Consumer Boundary

validator와 runtime consumer의 책임은 명시적으로 분리한다.

validator hard fail 범위:

- field ownership 위반
- bridge contract drift
- emitted `quality_state / publish_state` 불일치
- reserved state emit

Phase 6 in-game validation 범위:

- `internal_only`인데 Browser/Wiki default surface가 실제로 렌더됨
- consumer layer의 `publish_state` 분기 오작동
- tooltip 또는 다른 consumer surface regression

즉, validator는 offline artifact integrity를 본다. 실제 consumer rendering은 Phase 6에서 본다.

---

## 8. Phase 4 Entry Checklist

Phase 4 진입 전 아래 항목이 모두 `DECISIONS.md`에서 채택되어야 한다.

- `quality/publish decision stage` legality
- `quality_state / publish_state` single writer rule
- validator drift-checker-only rule
- post-migration semantic contract의 시간축 명시
- `quality_state` allowed state set
- Lua bridge `internal_only` semantics
- validator와 runtime consumer boundary

현재 status:

- 2026-04-06 기준 전 항목 채택 완료
- current cycle의 `Phase 3A`는 sealed로 읽는다
- Phase 4는 이 문서와 `DECISIONS.md`를 authority input으로 사용한다
