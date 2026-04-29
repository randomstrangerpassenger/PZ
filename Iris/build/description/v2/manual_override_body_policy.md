# DVF 3-3 Manual Override Body Policy

이 문서는 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/dvf_3_3_body_role_execution_plan.md`의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

## 목적

이 문서는 DVF 3-3 body-role 경로에서 자동 compose/repair 규칙으로 계속 왜곡되는 row를 manual override로 승격하는 기준을 고정한다.

수동 override는 일반 경로의 대체물이 아니다. 기본 원칙은 다음과 같다.

- facts는 늘리지 않는다.
- repair는 compose 내부에 둔다.
- manual override는 일반 규칙이 반복적으로 대표성을 훼손할 때만 연다.

## override 진입 기준

다음 중 하나라도 충족하면 manual override 검토 대상으로 올릴 수 있다.

1. representative ordering 실패
   - 대표 기능보다 부차 기능이 계속 선두에 오고, `representative_slot_override`와 compose repair를 적용해도 왜곡이 남는 경우
2. distinctive mechanic 중심 아이템
   - 특수 메커니즘이 실제 아이템 정체성의 중심인데, 현재 deterministic rule은 이를 후경으로 밀어 의미를 잃게 만드는 경우
3. 복합 multiuse 왜곡
   - 하나의 row가 무기/도구, 휴대/보관, 제작/소비처럼 복수 축을 동시에 갖고 있어 일반 규칙이 계속 대표성을 흔드는 경우

## override 비대상

다음은 manual override 사유가 아니다.

- 단순 acquisition 후행화 문제
- `IDENTITY_ONLY` row 전체를 일괄 예외 처리하려는 경우
- source expansion으로 해결해야 하는 `identity_fallback` 부족
- style lexical 문제만 있는 경우

이 경우는 각각 Phase 3 repair, Phase 5 expansion, style/normalizer 경로에서 해결한다.

## 제출 단위

manual override 후보는 row 단위로 제출한다. 제출 packet에는 다음 항목이 있어야 한다.

- `item_id`
- 현재 rendered 문장
- 원하는 rendered 문장
- 왜 자동 compose/repair가 실패하는지 한 문장 설명
- 근거 facts 슬롯 목록
- 해당 row가 속한 regression lane

## review 체크리스트

override 검토자는 아래를 확인한다.

1. 원하는 문장이 facts 밖의 새 정보를 추가하지 않는가
2. 3-4 상세를 흡수하지 않는가
3. 대표 기능이 실제로 아이템 정체성 중심인가
4. 일반 규칙으로 같은 결과를 재현할 수 없는가
5. override가 lane 전체가 아니라 row 한정 예외로 남는가

## 구현 경로

manual override가 승인되면 기존 `manual_override_text_ko` 경로를 재사용한다.

- compose는 해당 row를 직접 rendered로 보낸다.
- style rules는 건너뛴다.
- legacy postproc만 적용한다.

이 동작은 `docs/DECISIONS.md`와 `docs/ARCHITECTURE.md`의 기존 `manual_override_text_ko` 계약을 따른다.

## Phase 8 regression lane 연결

manual override review는 아래 lane 우선순위를 따른다.

- `multiuse tool`
- `weapon/tool hybrid`
- `distinctive mechanic item`
- `acquisition-heavy item`
- `identity/role fallback row`
- `cluster_summary dominant row`

특히 다음 경우는 우선 검토한다.

- `FUNCTION_NARROW + representative_slot_override = true`
- `BODY_LACKS_ITEM_SPECIFIC_USE`가 반복되고 source expansion 없이 해결 불가한 row
- full preview regression은 안정적이지만 semantic weak candidate로 계속 남는 row

## 종료 규칙

manual override는 예외다. 다음 중 하나가 충족되면 override를 줄이거나 제거하는 쪽을 우선한다.

- source expansion으로 item-specific body가 새로 확보된 경우
- compose 일반 규칙이 같은 결과를 안정적으로 재현할 수 있게 된 경우
- regression pack lane에서 더 이상 반복 왜곡이 관찰되지 않는 경우
