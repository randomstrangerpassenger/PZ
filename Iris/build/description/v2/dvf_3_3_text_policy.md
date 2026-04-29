# DVF 3-3 Text Policy

> 참고: 현재 운영 기준 문서는 `docs/dvf_3_3_body_role_policy.md`다. 이 문서는 runtime text policy reference로 유지한다.

> 상태: draft v2  
> 목적: 3-3 본문이 4계층의 대표 작업 맥락을 빌려오되, 3-4 상세 상호작용층으로 붕괴하지 않도록 경계를 고정한다.

---

## 1. 대상 범위

- 이 문서는 DVF 3-3 본문이 `direct use`, `interaction cluster summary`, `role fallback`을 어떻게 사용할 수 있는지 정의한다.
- 현재 문서의 직접 대상은 `interaction cluster`를 통해 4계층 정보를 3-3으로 요약 반영하는 경로다.
- 3-3은 계속 item-centric body이며, 3-4의 대체층이 아니다.

## 2. 3-3이 빌려올 수 있는 것

3-3은 아래 세 가지 유형만 4계층에서 차용할 수 있다.

| 허용 유형 | 설명 | 예시 |
|---|---|---|
| 대표 용도 | 아이템을 이해하는 데 필요한 대표적 쓰임 | `통조림 개봉에 쓰는 도구다` |
| 대표 작업군 | 아이템이 속하는 게임 내 작업 맥락 | `금속 단조 작업에 들어가는 도구다` |
| 대표 상호작용 맥락 | 상세 목록이 아니라 대표 interaction context의 요약 | `총기 개조 작업에 들어가는 부품이다` |

허용되는 문장은 항상 **대표 작업 맥락 + item-centric 설명**으로 닫혀야 한다.

## 3. 3-3이 빌려오면 안 되는 것

3-3은 아래 정보를 4계층에서 가져오면 안 된다.

| 금지 유형 | 설명 |
|---|---|
| 상호작용 목록 | 관련 레시피, 관련 행동, attach 가능한 항목, 사용 가능한 항목 나열 |
| 재료 목록 | 필요 재료, consume/keep 목록, atom requirement 나열 |
| 요구 조건 | skill, tool, stat, container, heat, fuel 등 requirement 상세 |
| 메뉴명/행동명 | 우클릭 메뉴 문자열, 버튼명, action label |
| 세부 절차 | 클릭 순서, 작업 순서, 조합 순서 |
| 내부 분류 정보 | category ID, module/type, pipeline code, `uc.*` 계열 |

## 4. direct use 보존 원칙

- 기존 direct use 문장이 이미 작업 맥락 수준의 구체성을 갖고 있으면 cluster summary로 덮어쓰지 않는다.
- cluster summary는 direct use가 비어 있거나, 지나치게 추상적이거나, role fallback이 공허할 때만 개입한다.
- `더 일반적인 cluster 문장`이 `더 구체적인 direct use 문장`을 밀어내는 것은 금지다.

## 5. 문장 계약

- 3-3 문장은 대표 작업 맥락을 포함한 **한 개의 대표 용도 축**만 다룬다.
- 3-3 문장은 레시피/우클릭 상세를 열거하지 않는다.
- 3-3 문장은 recommendation, comparison, interpretation을 포함하지 않는다.
- 3-3 문장은 3-4와 달리 navigation이나 requirement display를 품지 않는다.

## 6. 허용 표현의 최소 요건

허용 표현은 아래 세 조건을 동시에 만족해야 한다.

1. 게임 내 작업 맥락이 드러난다.
2. item-centric body로 읽힌다.
3. 목록형이 아니라 대표 요약문으로 닫힌다.

구체 표현 골격은 `cluster_abstraction_floor.md`에서 정의한다.

## 7. 금지선

다음 중 하나라도 만족하면 3-3 위반이다.

- `레시피/행동/부품/재료`를 2개 이상 나열한다.
- `우클릭`, `관련 레시피`, `사용 가능한`, `요구 사항`, `필요 재료` 같은 3-4 신호를 직접 노출한다.
- 메뉴명, 행동명, 클릭 경로를 본문에 그대로 쓴다.
- `도구다`, `재료다`, `다양한 작업에 쓰인다` 수준으로 작업 맥락 없이 끝난다.
- `uc.`, `Base.`, `module.` 같은 내부 코드를 드러낸다.

## 8. 판정 기준 문서

- 허용/금지 경계 판정은 `3_3_vs_4_boundary_examples.md`를 기준 예시집으로 삼는다.
- 추상도 하한선과 금지 패턴은 `cluster_abstraction_floor.md`를 따른다.
- merge 우선순위와 4케이스 decision tree는 `use_hint_generation_rules_v2.md`를 따른다.

## 9. 비목표

- 3-3을 4계층 목록 축약본으로 만드는 것
- interaction cluster를 approval backlog cluster와 동일 개념으로 다루는 것
- template 표면형 문제를 이유로 facts, candidate_state, approval 규약을 흔드는 것
