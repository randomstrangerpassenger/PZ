# Lua Bridge Publish State Contract

> 상태: draft v0.1  
> 기준일: 2026-04-06  
> 목적: `publish_state` 도입 이후 bridge와 consumer의 책임 분리를 명시한다.

---

## 1. Contract Goal

Lua bridge contract의 목표는 다음 하나다.

- runtime artifact availability를 줄이지 않은 채
- Browser/Wiki default surface visibility만 제어한다

즉, bridge는 data carrier이고, default consumer가 visibility branch를 담당한다.

---

## 2. Bridge Output Rule

`IrisLayer3Data.lua` 계열 bridge는 row 단위로 다음을 보존해야 한다.

- row 존재
- 3-3 body
- `publish_state`
- 기존 runtime lookup에 필요한 다른 field

금지:

- `internal_only` row 삭제
- `internal_only`의 3-3 body nil 처리
- `publish_state`를 consumer 대신 bridge에서 해석해 row를 누락시키는 것

---

## 3. Consumer Rule

Browser/Wiki default consumer는 `publish_state`를 읽어 렌더 여부만 분기한다.

- `internal_only`
  - default body surface 렌더 안 함
- `exposed`
  - 기존과 동일하게 body 렌더 허용

consumer 금지:

- quality_state를 직접 해석해 recommendation처럼 표시
- `fact_origin`을 quality proxy처럼 번역
- bridge payload를 다시 써서 state를 바꾸는 것

---

## 4. Validator Boundary

validator는 bridge payload integrity까지만 본다.

hard fail 예시:

- emitted row에 `publish_state`가 없음
- `publish_state = internal_only`인데 bridge row가 누락됨
- `publish_state = internal_only`인데 bridge 3-3 body가 누락됨
- non-writer가 `publish_state`를 기록함

validator 비범위:

- Browser/Wiki default surface가 실제로 body를 렌더하는지 여부
- context menu, tooltip, layered consumer UX behavior

이 영역은 Phase 6 in-game validation pack의 책임이다.

---

## 5. Consumer Regression Checklist Input

Phase 6 validation은 최소한 아래를 확인해야 한다.

- `internal_only` row는 runtime artifact에 남아 있는가
- Browser/Wiki default surface는 `internal_only`를 렌더하지 않는가
- `exposed` row는 정상 렌더되는가
- tooltip과 다른 consumer는 회귀가 없는가

이 문서는 그 validation pack의 contract input으로 사용한다.
