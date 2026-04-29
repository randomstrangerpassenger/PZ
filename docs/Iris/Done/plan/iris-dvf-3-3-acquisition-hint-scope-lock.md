# Iris DVF 3-3 Acquisition Hint Scope Lock

> 상태: Draft v0.1  
> 기준일: 2026-04-08  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 동반 문서: `docs/iris-dvf-3-3-acquisition-hint-korean-standardization-execution-plan.md`  
> 목적: acquisition lexical round가 한국어 엔진 개발, style gate 승격, state 재판정으로 번지지 않도록 범위를 먼저 봉인한다.

> 이 문서는 상위 문서의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 라운드 정체성

이번 라운드는 아래 한 줄로 닫는다.

> acquisition을 핵심 축으로 올려도 버틸 수 있는  
> **한국어 입력 표준화 계층**을 먼저 세우고,  
> 그 계층으로 닫히지 않는 잔여분만 최소 범위 구조 예외로 봉인한다.

이 문장은 아래 셋을 동시에 뜻한다.

- 이번 라운드는 한국어 엔진 개발이 아니다.
- 이번 라운드는 compose 고도화 경쟁이 아니다.
- 이번 라운드는 state/publish/style authority를 다시 여는 라운드가 아니다.

---

## 1. Hard No List

이번 라운드에서 열지 않는 항목은 아래처럼 고정한다.

- `josa_adaptive` 도입
- `phrasebook_ko.json` / `ko_particles.json` 활성화
- `acquisition_hint` 배열화
- acquisition 기반 active/silent 자동 재판정
- `identity_hint` / `primary_use` 동일 수준 자연화 round 확대
- sentence_plan 4블록 상한 변경
- style linter gate 승격
- compose 외부 repair/rewrite 재도입

위 항목이 필요해지는 순간, 그 작업은 이번 라운드 scope 밖이다.

---

## 2. 운영 불변식

- 모든 자연화 판단은 오프라인 Python에서만 수행한다.
- A축이 1차 경로다.
  - canonical lexicon + normalization layer
- B축은 조건부다.
  - acquisition 슬롯 한정 micro-josa shim
- S축은 독립 작업이다.
  - suppress 경로 식별과 제거
- `facts.acquisition_hint = null`이면 `decisions.acquisition_null_reason`이 따라와야 한다.
- style linter hit는 facts/decisions 재오픈 근거가 아니다.
- staging-first 운영을 유지한다.
- `staging/gate`를 우회한 direct write는 금지한다.
- gate 통과 후 `staging -> canon promotion`만 허용한다.

---

## 3. Conditional Exception Rule

micro-josa는 기본 경로가 아니다.  
Phase 5 rebuild와 regression이 먼저 닫힌 뒤, 아래 조건 코드를 평가한다.

- `COUNT`
  - residual mismatch `> 30`
- `GOLDEN_FAIL`
  - golden subset acquisition block mismatch
- `PROFILE_CONCENTRATION`
  - 동일 canonical family 또는 상위 노출 profile 집중

세 조건이 모두 미충족이면 B축은 닫힌다.

열리더라도 범위는 아래처럼 봉인한다.

- acquisition_hint 슬롯 전용
- 조사 pair 최대 5종
- self-contained 결정론 함수 1개
- v2 조사 엔진과 독립

---

## 4. Suppress Read Rule

current zero-hit나 warn 감소는 lexical closure의 증거가 아니다.  
exact phrase exception, simple discovery shape exception, manual override 우회가 남아 있으면 그것은 **표준화 완료**가 아니라 **suppress 운영 상태**다.

따라서 이번 라운드의 성공은 아래 둘 중 하나로만 인정한다.

- canonical normalization으로 닫힘
- `STANDARDIZATION_IMPOSSIBLE` 또는 `UBIQUITOUS_ITEM`으로 구조화됨

---

## 5. 종료 문장

이번 라운드의 종료 조건은 다음 self-check가 통과하는 상태다.

- 이번 라운드를 한 문장으로 설명했을 때
  - `한국어 엔진 개발`
  - `style gate 승격`
  - `active/silent 재판정`
  중 어느 것도 언급되지 않는다.

> 이건 acquisition 입력 계약 정리 작업이다.  
> 한국어 엔진 개발이 아니다.
