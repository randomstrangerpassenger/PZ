# Use Hint Generation Rules v2

> 목적: direct use, interaction cluster summary, role fallback을 충돌 없이 병합한다.

---

## 1. 입력 축

- `direct_use`
- `cluster_summary`
- `role_fallback`

3-3 use hint는 위 세 축 중 하나 또는 둘의 조합으로 나온다.

## 2. source 우선순위

기본 우선순위는 아래와 같다.

1. 충분히 구체적인 `direct_use`
2. `cluster_summary`
3. `role_fallback`

다만 더 상위 source가 더 빈약하면 하위 source가 대체할 수 있다.

## 3. direct use 충분성 기준

`direct_use`는 아래를 만족하면 충분히 구체적인 것으로 본다.

- 게임 내 작업 맥락이 직접 드러난다
- `too_generic_use`에 걸리지 않는다
- `borrowed_list_structure`에 걸리지 않는다
- role fallback 수준의 공허한 명사구가 아니다

## 4. 병합 4케이스

### Case 1. direct use 충분 -> 유지

- `direct_use`가 충분히 구체적이면 그대로 유지한다.
- cluster summary는 이 경우 대체권을 갖지 않는다.

### Case 2. direct use 추상적 -> cluster 대체 또는 보강

- `direct_use`가 너무 추상적이면 cluster summary가 우선한다.
- 다만 `direct_use` 안에 보존 가치가 있는 부분이 있으면 cluster summary로 보강할 수 있다.

### Case 3. role fallback 공허 -> cluster 우선

- `role_fallback`이 `도구다`, `재료다` 수준이면 cluster summary가 우선한다.
- 이 경우 `role_fallback_too_hollow`를 기록한다.

### Case 4. cluster 없음 -> 기존 경로 유지

- cluster가 없으면 기존 `direct_use -> role_fallback` 경로를 유지한다.
- cluster 부재 자체가 회귀 사유가 되어서는 안 된다.

## 5. 출력 기록

최종 use hint 생성 시 최소 아래 필드를 남긴다.

- `use_source`
- `merge_case`
- `preserved_direct_use`
- `cluster_used`

## 6. 금지선

- 더 일반적인 cluster 문장으로 더 구체적인 direct use를 덮어쓰지 않는다.
- cluster summary를 3-4 목록 요약본처럼 쓰지 않는다.
- 메뉴명, action label, recipe title, requirement list를 use hint에 직접 넣지 않는다.

## 7. 판정 기준 문서

- 경계 판정: `3_3_vs_4_boundary_examples.md`
- 추상도 하한선: `cluster_abstraction_floor.md`
- 전체 정책: `dvf_3_3_text_policy.md`
