# Phase 3 Reviewer Decision Sheet

매 row마다 아래 순서로만 판단한다.

1. Phase 2 snapshot이 닫힌 입력인가.
2. 이 row는 `ACQ_HINT`인가 `ACQ_NULL`인가.
3. 이 정보는 버킷 공통인가, 개별 아이템 고유인가.
4. 이 정보는 3-4 상호작용층으로 보내야 하는가.
5. 추천이나 비교 없이 중립 본문 문장으로 설 수 있는가.
6. 이미 3-1 / 3-2에서 충분한가.
7. 애매함의 원인이 정보 부족인가, 층 경계 충돌인가.

판정 규칙:

- 정보 부족이면 `KEEP_SILENT`
- 네 문항을 모두 통과하면 `PROMOTE_ACTIVE`
- 충돌이나 rule gap이면 `MANUAL_OVERRIDE_CANDIDATE`

기록 규칙:

- 모든 row는 reason_code를 남긴다.
- `PROMOTE_ACTIVE`만 compose_profile을 채운다.
- `MANUAL_OVERRIDE_CANDIDATE`는 notes를 남긴다.
