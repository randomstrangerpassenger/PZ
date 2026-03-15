# acquisition_hint 운영 규약

> Iris 3계층 DVF v4 봉인 문서. 이 문서는 `acquisition_hint` 슬롯의 운영 정책을 정의한다.

---

## 1. 핵심 축 재정의

3계층 개별 설명의 기본 축은 다음 세 가지다.

| 축 | 슬롯 | 질문 |
|----|------|------|
| 정체성 | `identity_hint` | 이것은 어떤 물건인가? |
| 용도 | `primary_use` | 무엇에 쓰는가? |
| **획득성** | `acquisition_hint` | 어디서/어떻게 얻는가? |

`acquisition_hint`는 `identity_hint`, `primary_use`와 동급의 전 아이템 공통 검토 대상이다.

---

## 2. 검토 범위 및 방향

- **검토 대상**: active·silent **무관**, 전 아이템이 검토 대상
- **"silent라서 검토 제외"는 금지**. 검토 결과로서 silent를 유지하는 것은 허용되나, 검토 자체를 건너뛰는 것은 금지
- **검토 방향 역전**: "넣을 이유가 있는가?"가 아니라 **"안 넣을 근거가 있는가?"**를 묻는다. 근거가 없으면 넣는다

---

## 3. null 허용 사유

`acquisition_hint = null`은 다음 두 가지 사유에 한해서만 허용된다.

| 사유 코드 | 의미 | 예시 |
|----------|------|------|
| `STANDARDIZATION_IMPOSSIBLE` | 중립 사실로 표준화 불가 | 획득 장소가 너무 다양하고 일관된 표현이 어려운 경우 |
| `UBIQUITOUS_ITEM` | 범용 아이템이라 장소 특정 무의미 | 어디서나 발견되는 아이템 |

### 구조적 추적

- `acquisition_hint = null`이면 **state 무관** `decisions`의 `acquisition_null_reason` 필드에 위 사유 코드 중 하나를 필수 기재
- `acquisition_hint ≠ null`이면 `acquisition_null_reason = null`
- DVF `validate_layer3_decisions.py`가 facts↔decisions 교차 검증으로 자동 강제
- facts 엔트리가 존재하지 않는 아이템은 교차 검증 skip

---

## 4. 표현 규약

### 허용
- 장소명: "약국이나 병원에서 발견된다"
- 획득 경로명: "채집으로 구할 수 있다"
- 방식명: "제작으로 얻는다"
- 건조한 명사구 형태

### 금지 (hard_fail)
- 확률/빈도: "드랍률", "확률", "스폰율", "%"
- 효율/추천: "효율적", "추천", "가장 빠른", "최적", "노리는 게 좋다"
- 비교: "~보다 잘 나오는", "~에서 더 많이"
- 가이드성 표현 일체

### 비권장 (warning)
- 컨테이너 레벨: "서랍", "캐비닛" — 건물/장소명 수준 우선
- 구체적 위치: "~층", "~번째 방", "좌표"

---

## 5. 슬롯 값 계약 (전체 슬롯 공통)

`acquisition_hint`를 포함한 모든 슬롯에 적용되는 작성 규칙:

1. **줄바꿈 금지**: 슬롯 값에 `\n` 포함 시 HARD FAIL
2. **비소수점 마침표 금지**: 문장 종결 마침표는 template이 부여하므로 슬롯에 포함 금지. 소수점("3.5g")은 허용
3. **단일 절 단위**: 하나의 사실 조각만 담는다

---

## 6. 구조 금지

- 2.5계층 또는 별도 "파밍 장소 전용 시스템" 추가 금지
- 기존 `acquisition_hint` + `slot_meta.acquisition_hint` 필드 구조 유지, 의미만 재정의

---

## 7. 소스 우선순위와 충돌 처리

획득성 검토 시 근거 우선순위는 다음과 같다.

1. `items_itemscript`
2. `tags_by_fulltype`
3. local Iris outputs/docs
4. 기존 수동 샘플

- 상위 소스와 하위 소스가 충돌하면 상위 소스를 우선한다
- 상위 소스를 우선해도 장소/경로/방식 수준의 중립 문장으로 표준화가 닫히지 않으면 `acquisition_hint = null`로 두고 `acquisition_null_reason = STANDARDIZATION_IMPOSSIBLE`로 종결한다
- 위와 같이 `STANDARDIZATION_IMPOSSIBLE`로 종결하는 경우 왜 표준화가 불가능했는지 `notes`를 남긴다

---

## 8. notes 의무 사용 조건

- `ACQ_NULL + STANDARDIZATION_IMPOSSIBLE`이면 `notes` 필수
- `MANUAL_OVERRIDE_CANDIDATE`이면 `notes` 필수
- `notes`에는 충돌한 소스 또는 수동 오버라이드가 필요한 이유를 최소 1문장으로 남긴다

---

## 9. v2 예약 사항 (현재 구현하지 않음)

`slot_meta.acquisition_hint` 내부 값 검증은 v2 DVF 범위로 예약한다.

예정 필드:
- `mode`: `loot` / `forage` / `craft` / `zombie` / `trade` / `spawn`
- `location_tags`: `["pharmacy", "hospital"]` 등 표준 태그

v1에서는 자유 형식 object로 유지하되, 작성 시 위 구조를 권장한다.
