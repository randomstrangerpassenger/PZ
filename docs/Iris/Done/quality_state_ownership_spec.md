# Quality State Ownership Spec

> 상태: draft v0.1  
> 기준일: 2026-04-06  
> 목적: post-migration `quality_state`의 의미, 소유권, 허용 상태 집합, validator 경계를 명시한다.

---

## 1. Scope

이 문서는 다음만 닫는다.

- post-migration `quality_state`의 의미
- `quality_state`의 single writer
- `quality_state` 판정 입력
- validator와 non-writer의 경계

이 문서는 actual Lua consumer code diff, UI copy, `quality_exposed` 집행을 닫지 않는다.

---

## 2. Time Axis

이번 round는 기존 `semantic_quality`의 단순 승격이 아니라 **시간축이 있는 의도적 의미 재설계** 다.

- pre-migration `semantic_quality`
  - problem 2 round authority
  - upstream semantic/body-role diagnostic
  - derived/cache field
- post-migration `quality_state` 또는 재정의된 `semantic_quality`
  - contract migration round 이후 authority
  - downstream publish decision의 입력이 되는 authoritative contract

따라서 이 문서는 problem 2 round의 기존 결정을 뒤집지 않는다. 단지 contract migration round 이후 적용될 새 meaning을 정의한다.

---

## 3. Ownership

`quality_state`의 writer 모델은 단일 writer 구조로 고정한다.

- single writer
  - `quality/publish decision stage`
- non-writer
  - facts stage
  - decisions overlay builder
  - compose
  - structural audit
  - style advisory sensor
  - validator
  - Lua bridge
  - Browser/Wiki consumer

writer가 아닌 어떤 단계도 `quality_state`를 기록, 수정, 보정할 수 없다.

---

## 4. Allowed State Set

current contract migration round에서 emit 가능한 `quality_state`는 다음 셋뿐이다.

- `strong`
- `adequate`
- `weak`

`fail`은 reserved 상태다.

- 이번 round에서 emit 금지
- validator가 emit을 감지하면 hard fail
- 의미 정의는 future round로 이연

---

## 5. Decision Inputs

`quality_state`는 runtime surface 결과가 아니라 offline artifact 근거로만 판정한다.

주요 입력:

- body-role 정합성
- representative use 존재 여부
- `identity_fallback` 또는 과도한 fallback 의존
- sentence/body completeness
- compose 결과
  - repair 성공 여부
  - requeue 여부
  - known residual reason
- structural audit signal
  - `hard_fail`은 `quality_state = weak` 강제 근거가 된다
  - `flag`는 preview/report-only `structural_flag` 메타로만 남는다

비허용 입력:

- Browser/Wiki consumer의 실제 렌더 결과
- user-facing quality 해석
- 추천/비추천/우열 신호

---

## 6. Relationship To Publish State

`quality_state`는 `publish_state`의 입력이지만 동일 값이 아니다.

- `quality_state`는 quality contract다.
- `publish_state`는 visibility contract다.
- weak라고 해서 자동으로 `internal_only`가 되는 것은 아니다.
- current cycle의 `identity_fallback` lane은 explicit policy-isolation 때문에 `internal_only` 예정 lane으로 읽는다.

즉, `quality_state`와 `publish_state`는 연결되지만 1:1 종속 관계로 고정하지 않는다.

---

## 7. Validator Boundary

validator는 `quality_state`를 쓰지 않는다.

validator hard fail 범위:

- non-writer가 `quality_state`를 기록함
- `quality_state`가 누락된 채 `publish_state = exposed`가 emit됨
- reserved state `fail`이 emit됨
- bridge/state artifact 사이에 `quality_state` drift가 존재함
- `structural_flag`가 emitted contract artifact 또는 runtime consumer로 유출됨

validator 비범위:

- Browser/Wiki default surface가 실제로 body를 렌더하는지 여부
- tooltip 또는 runtime consumer UX regression

---

## 8. Implementation Notes

- field 이름은 post-migration에도 `semantic_quality`를 유지할 수 있다.
- 다만 owner와 meaning은 이 문서 기준으로 재정의된다.
- implementation은 field rename 여부와 무관하게 single-writer contract를 만족해야 한다.
