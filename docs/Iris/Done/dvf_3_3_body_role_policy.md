# DVF 3-3 Body Role Policy

> 이 문서는 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 1. 목적

이 문서는 DVF 3-3이 어떤 본문이어야 하는지와 3-4 상세 상호작용층을 어디서 끊어야 하는지를 운영 규약으로 고정한다.

3-3은 residual slot이 아니라 위키 본문층이다. 다만 1·2·4계층 정보를 일부 포함할 수 있고, 그 사실만으로 위반이 되지 않는다. 금지선은 3-4 상세를 통째로 흡수하는 경우에만 적용한다.

## 2. 기본 역할

- 3-3은 item-centric body다.
- 3-3은 아이템 자기 시점의 대표 용도와 작업 맥락을 짧게 압축한다.
- 3-3은 authoritative wiki body로 읽히지만, 상위 기준 문서보다 우선하지 않는다.
- 3-3은 1·2·4계층 정보를 일부 차용할 수 있다.
- 3-3은 3-4의 목록형 상세, 절차, 조건, 메뉴 문자열을 흡수하지 않는다.

## 3. 3-3이 포함할 수 있는 것

3-3은 아래 유형을 포함할 수 있다.

| 허용 유형 | 설명 | 예시 |
|---|---|---|
| 아이템 정체성 힌트 | 아이템이 무엇인지 짧게 잡아주는 본문 도입 | `도구`, `부품`, `재료` |
| 대표 용도 | 아이템을 이해하는 데 가장 먼저 필요한 중심 기능 | `통조림 개봉에 쓰는 도구다` |
| 대표 작업 맥락 | 작업군 수준의 상호작용 요약 | `금속 단조 작업에 들어가는 도구다` |
| 후행 획득 맥락 | 본문을 보조하는 획득 문장 | `주방과 조리 도구 보관 장소에서 발견된다` |

핵심은 본문이 항상 아이템 자기 시점으로 닫혀야 한다는 점이다.

## 4. 3-3이 흡수하면 안 되는 것

3-3은 아래 정보를 3-4에서 통째로 가져오면 안 된다.

| 금지 유형 | 설명 |
|---|---|
| 상호작용 목록 | 관련 레시피, attach 대상, 우클릭 가능 항목 열거 |
| 요구 조건 상세 | 재료, skill, tool, heat, fuel, container requirement |
| 절차 | 클릭 순서, 조합 순서, 단계별 작업 흐름 |
| 메뉴/행동 문자열 | 우클릭 메뉴명, 버튼명, action label |
| 내부 코드 | module/type, pipeline code, `uc.*`, `Base.*` 등 내부 표식 |

## 5. direct use와 cluster summary의 관계

- direct use가 이미 작업 맥락 수준의 구체성을 가지면 cluster summary로 덮어쓰지 않는다.
- cluster summary는 direct use가 비어 있거나 지나치게 추상적일 때만 개입한다.
- 더 일반적인 cluster 문장이 더 구체적인 direct use를 밀어내면 안 된다.
- role fallback이나 identity fallback은 본문을 살리는 임시 경로일 수 있지만, 대표 본문으로 오인하지 않는다.

## 6. 본문 조합 원칙

- 대표 문장은 하나의 중심 용도 축으로 닫는다.
- 획득 문장은 포함 가능하지만 본문 선두를 점거하지 않게 후행 슬롯으로 둔다.
- 2계층 정보가 들어와도 item-specific use가 살아 있으면 허용된다.
- `도구다`, `재료다` 수준의 일반론만으로 끝나면 body-role 실패로 본다.
- 대표성 왜곡이 있으면 representative slot을 주절로 복구하고, 충돌하는 identity echo는 후퇴 또는 제거한다.

## 7. 경계 판정 기준

다음 중 하나라도 만족하면 3-3 위반으로 본다.

- 레시피/행동/재료/대상을 둘 이상 나열한다.
- requirement나 절차를 설명한다.
- 메뉴명, 클릭 경로, action label을 직접 노출한다.
- 내부 분류 코드나 파이프라인 코드를 드러낸다.
- item-specific use 없이 일반 분류 레이블만 반복한다.

## 8. 참조 문서

- 경계 예시집: `docs/3_3_vs_3_4_boundary_examples.md`
- 기존 runtime text policy reference: `Iris/build/description/v2/dvf_3_3_text_policy.md`
- 추상도 하한선: `Iris/build/description/v2/cluster_abstraction_floor.md`

## 9. 비목표

- 3-3을 3-4 목록 축약본으로 만드는 것
- 본문 표면형 문제를 이유로 facts 재판정 규약을 다시 여는 것
- 3-3을 recommendation, comparison, interpretation 층으로 확장하는 것
