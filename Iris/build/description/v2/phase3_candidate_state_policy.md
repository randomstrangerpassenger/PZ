# Phase 3 Candidate State Policy

> 목적은 `KEEP_SILENT / PROMOTE_ACTIVE / MANUAL_OVERRIDE_CANDIDATE`의 뜻과 진입 경계를 고정하는 것이다.

---

## 1. 상태 정의

### `KEEP_SILENT`

- 3-3을 깨울 자격이 없다.
- 획득 정보가 있더라도 버킷 공통, 범용, 상호작용층 대체, 문장 가치 부족이면 여기로 닫는다.

### `PROMOTE_ACTIVE`

- 3-3 본문 가치가 있어 활성화 가능하다.
- 개별 아이템 이해를 실제로 늘리는 획득성이 있고, 중립적 문장으로 설 수 있어야 한다.

### `MANUAL_OVERRIDE_CANDIDATE`

- 구조 충돌 또는 규칙 공백으로 자동 판정을 보류한다.
- “애매하면 일단 manual”이 아니라, rule gap이나 layer collision이 확인된 경우만 쓴다.

## 2. Promote 테스트

`PROMOTE_ACTIVE`는 아래 네 문항을 모두 통과해야 한다.

1. 이 획득 정보가 이 아이템의 개별 이해를 실제로 더하는가.
2. 아이템 고유성 또는 맥락 구체성이 있는가.
3. 3-4 상호작용층으로 보내야 할 정보가 아닌가.
4. 추천이나 비교 없이 중립적 본문 문장으로 설 수 있는가.

하나라도 실패하면 `PROMOTE_ACTIVE`로 닫지 않는다.

## 3. 애매함 처리

- 정보가 약해서 애매하면 `KEEP_SILENT`
- 층 경계가 충돌해서 애매하면 `MANUAL_OVERRIDE_CANDIDATE`

애매함을 reviewer 재량으로 뭉개지 않는다.

## 4. 상태별 필드 계약

- `KEEP_SILENT`: keep 계열 reason_code 필수, compose_profile 금지, notes 금지
- `PROMOTE_ACTIVE`: promote 계열 reason_code 필수, compose_profile 필수, notes 금지
- `MANUAL_OVERRIDE_CANDIDATE`: manual 계열 reason_code 필수, compose_profile 금지, notes 필수

## 5. 금지선

- `MANUAL_OVERRIDE_CANDIDATE`를 예외 수집 통으로 사용하지 않는다.
- comparison, recommendation, interpretation을 판정 근거로 쓰지 않는다.
- 3-4 listification을 3-3 promote로 바꾸지 않는다.
