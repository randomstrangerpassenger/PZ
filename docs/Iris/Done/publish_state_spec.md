# Publish State Spec

> 상태: draft v0.1  
> 기준일: 2026-04-06  
> 목적: `publish_state`의 상태 정의, writer, 초기 정책, quality와의 경계를 명시한다.

---

## 1. Scope

이 문서는 `publish_state`를 visibility contract로 정의한다. 이 contract는 runtime availability와 default user-facing visibility를 분리하기 위해 도입한다.

---

## 2. State Set

`publish_state`의 정의는 다음과 같다.

- `internal_only`
  - runtime artifact에는 존재한다
  - bridge row와 3-3 body는 유지된다
  - Browser/Wiki default surface에는 기본적으로 노출하지 않는다
- `exposed`
  - default surface 노출 허용
  - quality badge 없음
- `quality_exposed`
  - quality metadata를 동반한 노출
  - current round에서는 reserved future state로만 둔다

---

## 3. Writer Model

`publish_state`의 authoritative writer는 `quality/publish decision stage` 하나뿐이다.

non-writer:

- overlay builder
- compose
- structural audit
- style advisory sensor
- validator
- Lua bridge
- Browser/Wiki consumer

consumer는 `publish_state`를 읽어 분기할 수 있지만, state를 생성하거나 수정할 수 없다.

---

## 4. Initial Policy For Current Cycle

current contract migration cycle의 초기 정책은 다음처럼 읽는다.

- `identity_fallback` explicit isolation lane
  - planned `publish_state = internal_only`
- non-isolated exposed-candidate population
  - planned `publish_state = exposed`
  - 단, actual writer는 여전히 `quality/publish decision stage`다
- surface contract authority migration round
  - structural audit는 `recommended_tier` recommendation만 제공한다
  - `IDENTITY_ONLY` / explicit `BODY_LACKS_ITEM_SPECIFIC_USE`만 current rollout open lane이다
  - `FUNCTION_NARROW`, `ACQ_DOMINANT`는 current hold다
- `quality_exposed`
  - not implemented
  - not emitted

이 정책은 B-path current cycle 기준이다. future cycle에서 path나 threshold가 바뀌면 policy도 새 decision이 필요하다.

---

## 5. Relationship To Quality State

`publish_state`는 `quality_state`를 참고하지만, 그 자체가 quality judgment를 user-facing interpretation으로 번역해서는 안 된다.

- 허용:
  - `quality_state`를 offline publish decision 입력으로 사용
- `internal_only`로 default visibility를 억제
- `recommended_tier`를 decision input으로만 참고
- 금지:
  - `publish_state`를 추천/비추천 신호로 번역
  - `publish_state`를 UI quality badge로 노출
  - fallback provenance를 quality proxy처럼 제시

---

## 6. Artifact Semantics

`internal_only`와 `exposed`는 row 존재 여부를 바꾸는 상태가 아니다.

- 둘 다 runtime artifact에 존재할 수 있다
- 둘 다 bridge row를 가진다
- 차이는 default consumer visibility뿐이다

따라서 `publish_state`는 deletion contract가 아니라 visibility contract다.

---

## 7. Validation Split

offline validator가 보는 범위:

- `publish_state` emitted consistency
- `quality_state`와의 contract drift
- bridge row/body 누락

Phase 6 in-game validation이 보는 범위:

- `internal_only` row가 default Browser/Wiki surface에서 실제로 숨겨지는지
- `exposed` row가 정상적으로 렌더되는지
- other consumer regression
