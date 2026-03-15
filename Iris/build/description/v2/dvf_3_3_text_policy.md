# DVF 3-3 본문 작성 규약

version: dvf-3-3-text-policy-v1

## 1. 대상 범위

APPROVE_SYNC 1050건. ACQ_ONLY_LOCATION(762) + ACQ_ONLY_METHOD(288) 프로파일만.

## 2. 톤

- 사실문, 위키 톤, 중립 서술
- 해석·권장·비교·추측 금지
- `forbidden_patterns.json` 전체 패턴 적용

## 3. 문장 구조

ACQ_ONLY 프로파일은 정확히 **2문장**으로 구성:

```
{identity_hint}. {acquisition_hint}.
```

- 첫 문장: identity_hint (카테고리 기반 한국어 명사구, 마침표 종결)
- 둘째 문장: acquisition_hint (Phase 2 검토 완료 텍스트 그대로 사용, 마침표 종결)

## 4. identity_hint 소스 계약

**단일 소스 원칙**: 코드 내 임시 딕셔너리 금지.

생성 우선순위:
1. `data/identity_hint_overrides.jsonl`에 해당 fulltype 존재 → override 값
2. `data/identity_category_ko.json`에서 `display_category|type_value` 키 조회
3. 키 미스 → **빌드 FAIL** (silent fallback 금지)

### 제약
- 30자 이하
- 한국어 명사구 (서술형 금지)

## 5. acquisition_hint

- Phase 2 리뷰 완료 텍스트를 **그대로** 사용
- 재작성·요약·편집 금지

## 6. 길이 제한

| 프로파일 | max_length_chars |
|----------|:---:|
| acq_location | 120 |
| acq_method | 120 |

`identity_hint + ". " + acquisition_hint + "."` 전체 길이 기준.

### 초과 시 정책: fail-loud
- 자동 잘라내기 금지
- profile downgrade 금지
- 해당 행을 `dvf_3_3_gaps.json`에 기록
- gap 행은 rendered에 포함되지 않음

### 초기 배치 기준
- `gap_count == 0`만 PASS
- gap 발생 시 identity_hint 축약 또는 override로 해소 후 재빌드

## 7. 층 경계

### 3-4 침범 금지 (상호작용/레시피)
- 리스트형 문장 패턴: `: `, `· `, `1. `
- 키워드: 관련 레시피, 관련 행동, 사용처, 사용 가능한, 만들 수 있는 것

### 3-5 침범 금지 (내부 코드/분류)
- 패턴: `uc.`, `Base.`, `module.`
- 키워드: 분류, 대분류, 소분류, 카테고리

## 8. 금지 톤

- 추천/비교: 추천, 최고의, 보다 나은, 유용, 효율적, 더, 덜
- 확률: 드랍률, 확률, 스폰율, %
- 추측: 아마, 대체로, 보통, 사실상
- 번역투: 되어지다, 에 의하여, 기능을 가지다

## 9. 수량 항등식

```
compose_target_total = 1050
facts_count == decisions_count == rendered_count + gap_count
gap_count == 0  (초기 배치 PASS 기준)
```
