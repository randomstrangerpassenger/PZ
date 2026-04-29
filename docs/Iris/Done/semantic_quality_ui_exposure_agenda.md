# Semantic Quality UI Exposure Agenda

## Scope

- 이 문서는 `no_ui_exposure` 계약을 바꾸는 실행 문서가 아니다.
- 목적은 future round에서 어떤 조건이 성숙하면 UI 재검토를 열 수 있는지 질문 목록을 고정하는 것이다.
- current round에서는 internal tracking, compose repair, requeue 운영까지만 수행한다.

## Current Baseline Input

- quality baseline v1 기준 `quality_ratio = 0.6315`
- `semantic_strong 1316 / semantic_adequate 0 / semantic_weak 768`
- weak breakdown: `identity_only 617 / function_narrow 7 / adequate_preserved_weak 144`
- compose requeue candidates: `624`
- current 상태에서는 UI 노출을 재검토할 성숙도에 도달하지 않았다고 본다.

## Candidate Reopen Gate

- 아래 항목은 **후속 decision 후보**이며, 현재 채택된 규칙이 아니다.
- `quality_ratio < 0.80` 구간에서는 UI 재검토를 열지 않는다.
- `0.80 <= quality_ratio < 0.85` 구간에서는 internal review까지만 허용하고 user-facing proposal은 열지 않는다.
- `quality_ratio >= 0.85`가 최소 2회 연속 build에서 유지되고 lane stability 조건이 통과될 때만 UI 재검토 의제를 정식 안건으로 올린다.
- 위 quality gate 외에도 `identity_fallback`, `role_fallback`, `multiuse tool`, `weapon/tool hybrid` lane에서 급격한 coverage 손실이 없어야 한다.
- requeue candidate 규모는 active 재정의를 논의할 수준까지 충분히 줄어야 한다. 구체 threshold는 Phase D 전 별도 결정으로 닫는다.

## UI Option Candidates

### Option A. Neutral Indicator

- rendered나 detail panel에 `quality_flag` 또는 `semantic_quality`를 직접 설명 없이 중립 메타데이터로 노출한다.
- 장점은 weak row 존재를 숨기지 않고 내부 상태를 투명하게 보여준다는 점이다.
- 단점은 사용자가 이를 추천/비추천 신호로 오독할 가능성이 높다.

### Option B. Filter-Only Exposure

- 기본 화면은 그대로 두고, 고급 필터에서 `quality-pass only` 또는 `hide weak` 같은 필터를 제공한다.
- 장점은 default contract를 덜 흔들면서 power-user control을 줄 수 있다는 점이다.
- 단점은 필터 존재 자체가 current active 의미를 quality-pass처럼 오해하게 만들 수 있다.

### Option C. Weak Hide or Default Suppression

- weak row를 기본 surface에서 숨기거나 별도 접힘 상태로 둔다.
- 장점은 current surface trust를 빠르게 올릴 수 있다는 점이다.
- 단점은 active/silent 외부 계약과 2-stage model closure를 사실상 다시 여는 강한 변경이라, Phase D decision 이전에는 검토 대상일 뿐 실행 후보가 아니다.

## Constitutional Collision Review

- `semantic_quality`는 해석, 권장, 비교를 위한 값이 아니다.
- UI 문구가 `더 좋다`, `추천`, `신뢰 가능`, `낮은 품질` 같은 가치판단 표현으로 번역되면 헌법과 충돌한다.
- ranking, sorting, recommendation, replacement suggestion에 `semantic_quality`를 직접 쓰는 것은 금지 후보로 본다.
- 허용 가능성이 있는 형태가 있다면 neutral metadata, optional filter, internal debug surface처럼 비해석적 사용에 한정해야 한다.

## Open Questions

- `adequate_preserved_weak 144`를 UI 논의에서 weak로 읽을지, legacy-semantic hold row로 분리해 읽을지
- `strong + FUNCTION_NARROW 20`처럼 semantic strong이지만 body-role repair가 필요한 row를 어떤 disclosure class로 둘지
- UI가 아니라 validator, debug panel, export packet 같은 semi-internal surface를 먼저 열어야 하는지
- active 재정의 없이 filter만 도입하는 경우도 2-stage closure 재오픈으로 봐야 하는지

## Decision Boundary

- 이 문서는 재검토 질문을 정리한 agenda다.
- `no_ui_exposure` 계약은 그대로 유지한다.
- 실제 실행은 별도 `DECISIONS.md` 항목과 별도 round 승인 없이는 열리지 않는다.
