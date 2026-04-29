# Philosophy Constitutionality Check

> 상태: draft v0.1  
> 기준일: 2026-04-06  
> 목적: three-axis contract design이 `Philosophy.md`의 반해석 원칙과 충돌하지 않는지 구체적으로 판정한다.

---

## 1. Role

이 문서는 로드맵 Section 3의 사전 가드레일을 대체하지 않는다.

- Section 3
  - migration round 전체에 적용되는 상위 금지선
- 이 문서
  - `quality_state / publish_state / bridge contract` 설계안에 대한 구체적 합헌 판정문

---

## 2. Constitutional

아래 항목은 현재 설계 기준으로 합헌이다.

- `internal_only`
  - default non-rendering policy일 뿐이며, user-facing 해석 문구를 만들지 않는다
- `exposed`
  - 사실 기반 body를 그대로 노출한다
- `publish_state`를 offline visibility contract로만 사용하는 것
- `fact_origin` provenance 표기
  - 단, source provenance 사실만 말할 때에 한한다

---

## 3. Unconstitutional

아래 항목은 현재 설계 기준으로 위헌이다.

- quality badge
  - 예: "품질이 낮음", "신뢰도 낮음", "추천하지 않음"
- quality ranking, sorting, recommendation
- `fact_origin`을 quality surrogate나 quality proxy로 사용하는 것
- `fallback 기반`, `일반 분류 기반` 같은 문구를 품질 우열 신호처럼 노출하는 것
- `quality_exposed`를 current round에서 구현하는 것

---

## 4. `fact_origin` Guardrail

`fact_origin`은 provenance/factual source 표기 only로 제한한다.

허용:

- source class 또는 provenance를 사실 그대로 기록
- offline audit/debug input으로 사용

금지:

- user에게 "이 설명은 덜 믿어도 된다"는 의미로 읽히게 만드는 UI copy
- fallback 여부를 품질 해석으로 번역
- provenance를 recommendation이나 warning으로 바꾸는 것

---

## 5. Result

current Phase 4 draft는 아래 조건을 지키는 한 합헌으로 판정한다.

- `publish_state`는 visibility contract로만 사용
- default surface는 quality 해석 문구를 표시하지 않음
- `fact_origin`은 provenance-only guardrail을 지킴
- `quality_exposed`는 future round까지 보류

이 조건이 깨지면 current draft는 즉시 재검토 대상이 된다.
