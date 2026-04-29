# Iris DVF 3-3 A-4-1 / Cluster-Budget Reopen Round Sizing Governance Amendment Final Integrated Plan

> 상태: Draft v1.2  
> 기준일: 2026-04-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 목적: former `bucket_2 599 net-new cluster required`가 드러낸 big-bang reopen 위험을, future explicitly-opened `A-4-1 rework / cluster budget` reopen round에만 적용되는 bounded subset sizing governance amendment로 봉인한다.  
> 실행 상태: planning only. 이 round는 policy text authority와 supporting provenance만 생성하며, execution plan, same-build mutation, runtime/publish mutation, cluster taxonomy reopen execution을 소유하지 않는다.

> 이 문서는 `A-4-1 rework / cluster budget` round를 지금 여는 문서가 아니다.  
> 이 문서는 future reopen이 실제로 열릴 때 읽을 sizing governance contract를 계획한다.

---

## 0. Round Identity와 Opening Baseline

### 0-1. Round identity

| 항목 | 값 |
|---|---|
| round 이름 | `Iris DVF 3-3 A-4-1 / Cluster-Budget Reopen Round Sizing Governance Amendment` |
| round 성격 | policy-level decision round |
| trigger | former `bucket_2 599 net-new cluster required`가 드러낸 big-bang reopen risk |
| primary question | future cluster-budget reopen round를 어떤 단위와 순서로 쪼개 읽을 것인가 |
| canonical outputs | `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`, `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`, `docs/DECISIONS.md` 신규 entry |
| non-output | actual reopen execution, runtime adoption, publish mutation, current terminal snapshot 재해석 |

### 0-2. Opening read rules

- current `cluster_count_limit = 30` frozen invariant는 그대로 유지한다.
- future reopen 순서는 계속 `policy widening -> 그래도 불가한 item만 A-4-1`을 따른다.
- current terminal snapshot consumer model과 `no_immediate_next_round_planned = true` 읽기 규칙은 그대로 유지한다.
- recent terminal-state decisions(`active_execution_lane_count = 0`, `no_immediate_next_round_planned = true`)와 explicit reopen gate는 이 amendment의 primary authority footing으로 유지한다.
- former `bucket_2 599`는 동기일 뿐이며, current authority artifact를 retroactive mutate하지 않는다.

### 0-3. One-sentence scope lock

> 이번 round는 future `A-4-1 rework / cluster budget` reopen round가 `subset-bounded single-authority sizing rule`을 따르도록 governance text를 봉인하는 것만 다룬다.

---

## 1. 전역 봉인선

### 1-1. Existing decision compatibility

- 2026-04-15 결정인 `current source expansion cycle에서는 A-4-1 interaction cluster budget 30을 재개방하지 않는다`를 유지한다.
- 2026-04-16 결정인 `closure policy widening -> 그래도 canonical close 불가 시 A-4-1` 순서를 유지한다.
- 2026-04-16 이후 terminal snapshot consumer model과 `reopen gate` 읽기 규칙을 유지한다.
- 2026-04-17 결정인 `identity_fallback current roadmap은 terminal policy authority 기준으로 완료 상태다`와 `no immediate next round planned` 읽기 규칙을 유지한다.
- 신규 원칙은 위 결정들을 덮는 상위 원칙이 아니라, 그 아래에서 작동하는 reopen sizing layer다.

### 1-2. Authority footing and Philosophy guardrail

- 이 amendment의 primary authority footing은 recent terminal-state decisions, explicit reopen gate, terminal snapshot consumer model이다.
- `docs/Philosophy.md`의 [5] 역할 침범 금지 원칙은 여기서 round-level 유비로만 보조 사용한다.
- 즉 한 reopen round는 여러 authority lane의 역할을 동시에 먹지 않고, 자기 round manifest가 소유한 bounded subset만 다뤄야 한다.
- 이 유비는 모듈 경계를 round 경계로 번역한 supplementary analogy이며, reopen priority나 item meaning 해석의 근거로 확장하지 않는다.

### 1-3. Hold

이번 round에서 열지 않는 항목은 아래처럼 고정한다.

- former `bucket_2 599` 자체 재해석 또는 retroactive 적용
- net-new cluster priority / ranking 기준 설계
- `30-cap` 재검토
- reopen gate 목록 변경
- closure policy boundary 수정
- runtime / publish contract 변경
- 실제 `A-4-1 rework` execution plan 작성
- terminalized backlog를 unfinished carry-over queue처럼 읽는 재해석

---

## 2. Phase 0 — Scope Lock

**목적:** 이번 amendment가 어디에만 구속되고 무엇을 건드리지 않는지, 그리고 기존 결정과 어떤 계층 관계를 가지는지 문장으로 먼저 봉인한다.

### 2-1. 해야 할 일

- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`를 작성한다.
- 적용 대상을 아래처럼 고정한다.
  - 구속 대상: future explicitly-opened `A-4-1 rework / cluster budget` reopen round
  - 비구속 대상: `scope_policy_override_round`, `runtime_adoption_round`, closure policy round, `future_new_source_discovery_hold`
  - `future_new_source_discovery_hold`는 cluster-budget reopen과 성격이 다른 item-level gate이므로 본 amendment의 적용 대상이 아니라고 즉시 봉인한다.
- 문제의식 provenance 문장을 한 문장으로 고정한다.
  - former `bucket_2 599`가 동기다.
  - 과거 사례가 동기이지만 과거 상태를 mutate하지 않는다고 명시한다.
- 기존 결정과의 관계를 한 문장으로 고정한다.
  - 2026-04-16 `policy widening -> A-4-1` 순서 유지
  - 2026-04-15 `cluster_count_limit = 30` frozen invariant 유지
  - 신규 원칙은 위 둘의 하위 sizing layer로만 기능
- Non-goal을 한 문장씩 고정한다.
  - reopen 여부 판정 규칙 아님
  - gate 정의 변경 아님
  - closure policy boundary 변경 아님
  - execution 개시 아님

### 2-2. 산출물

- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`

### 2-3. Review gate

- Critical
  - 적용 대상이 `future A-4-1 / cluster-budget reopen`을 넘어 다른 reopen family로 확장됨
  - 구속/비구속 대상이 섞여 써져 적용 범위가 모호함
  - former `bucket_2 599`를 current authority mutation 근거처럼 씀
  - `30-cap` 또는 `policy widening -> A-4-1`을 덮는 상위 원칙처럼 서술함
  - Non-goal이 reopen 판정 규칙 또는 execution 개시처럼 읽힘
- Important
  - provenance / relation / non-goal 문장 중 하나라도 결락
- Minor
  - 용어 정합성

### 2-4. 종료 조건

- 적용 대상 정의, provenance, 기존 결정과의 관계, Non-goal이 각각 한 문장 이상으로 모호성 없이 봉인된다.
- review 형식 `Good / Critical / Important / Minor / PASS / FAIL` 기준으로 `PASS`를 받는다.

---

## 3. Phase 1 — Axes 정의

**목적:** sizing governance를 실제 규칙으로 내릴 때 어떤 축을 채택하고 어떤 축을 이번 round 밖으로 남길지 먼저 고정한다.

### 3-1. 해야 할 일

- Phase 0 scope lock 문서에 `axes` 섹션을 추가한다. 별도 파일은 만들지 않는다.
- 축 A `Lane ownership axis`를 아래처럼 고정한다.
  - 허용: `existing-cluster reuse`만 다루는 round, 또는 `net-new cluster design`만 다루는 round
  - 금지: 같은 round manifest 안에서 `reuse`와 `net-new design` authority를 혼재시키는 것
  - 권고안: hard rule 채택
- 축 B `Size cap axis`를 아래처럼 고정한다.
  - 허용: 절대 수치 대신 `subset-bounded` 정성 원칙과 예시 주석
  - 금지: `이번 round는 몇 건 이하`만으로 sizing legitimacy를 판정하는 것
  - `설계·검증 동질성` 기준을 subset 판단 규칙으로 이 축에 통합한다.
  - 결합 규칙: `same representative task context`와 `same evidence / closure logic shape`는 필수 AND다.
  - 결합 규칙: `same validation path / artifact contract`와 `same cluster authoring and review burden`는 same wave 내 일관성 기준으로 묶고, 완전 동일성까지 요구하지 않는다.
- 축 C `Ordering axis`를 아래처럼 고정한다.
  - 허용: explicit reopen gate가 이미 열린 뒤 same reopen wave 안에서 `reusable 먼저 -> net-new subset sequential` 순서를 적용하는 것
  - 금지: reusable 검토 없이 곧바로 net-new cluster reopen으로 점프하는 것
  - 금지: sequencing을 reopen gate timing 또는 reopen admissibility 자체로 재정의하는 것
  - primary authority는 explicit reopen gate와 terminal-state decisions이며, `docs/Philosophy.md` [5]는 round-level sequencing의 보조 유비로만 사용한다.
- 축 D `Priority axis`를 아래처럼 고정한다.
  - 허용: 별도 future round에서 domain-specific 기준과 함께 다시 다루기
  - 금지: 이번 amendment 안에서 priority / ranking rule까지 같이 닫는 것
  - status: explicit out-of-scope

### 3-2. 산출물

- Phase 0 문서의 `axes` 섹션 추가본

### 3-3. Review gate

- Critical
  - 축 A에서 lane ownership 혼재 금지가 hard boundary로 고정되지 않음
  - 축 B가 절대 수치 cap 논의로 다시 미끄러짐
  - 축 C가 `policy widening -> A-4-1` 순서와 충돌함
  - 축 C가 사실상 reopen gate timing 또는 reopen admissibility rule로 회귀함
  - 축 D가 out-of-scope로 봉인되지 않음
- Important
  - 각 축의 허용/금지 문장이 한 쌍으로 작성되지 않음
  - subset-bounded의 의미가 설계·검증 동질성 축과 연결되지 않음
  - 축 B의 4기준 결합 규칙이 누락됨
- Minor
  - 축 이름 표기 흔들림

### 3-4. 종료 조건

- A/B/C는 채택, D는 out-of-scope로 고정된다.
- 각 축마다 허용/금지 문장이 최소 한 문장씩 존재한다.
- review `PASS`

---

## 4. Phase 2 — 원칙 본문 작성

**목적:** Phase 0-1의 scope와 axes를 future reopen round가 바로 읽을 수 있는 governance text authority로 압축한다.

### 4-1. 해야 할 일

- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`를 작성한다.
- 본문 구조를 아래 10개 섹션으로 고정한다.
  1. 적용 대상
  2. 문제의식 provenance
  3. Core principle 요약 문단
  4. Rule 1: Lane ownership separation
  5. Rule 2: Subset-bounded sizing
  6. Rule 3: Sequencing
  7. Hold 문장
  8. 기존 결정과의 관계
  9. Non-goal
  10. Reopen gate와의 연결
- `기존 결정과의 관계` 섹션은 recent terminal-state decisions(`active_execution_lane_count = 0`, `no_immediate_next_round_planned = true`)와 explicit reopen gate를 primary authority footing으로 쓰고, `docs/Philosophy.md` [5]는 supplementary analogy로만 사용한다.
- Rule 1은 축 A를 구현한다.
  - 하나의 reopen round manifest는 `reuse` authority와 `net-new design` authority 중 하나만 소유한다.
  - `reuse subset`과 `net-new subset`은 같은 reopen wave 안에 있더라도 separate sequential round로 분리한다.
- Rule 2는 축 B를 구현한다.
  - 절대 수치 대신 `subset-bounded single-authority sizing` 원칙으로 쓴다.
  - subset 판단 기준으로 최소 아래 4개 `설계·검증 동질성` 기준을 명시한다.
    - same representative task context
    - same evidence / closure logic shape
    - same validation path / artifact contract
    - same cluster authoring and review burden
  - subset admission은 앞의 두 기준을 필수 AND로 통과해야 한다.
  - 뒤의 두 기준은 same wave 내 일관성 기준이며, 완전 동일성을 요구하는 hard AND로 쓰지 않는다.
- Rule 3은 축 C를 구현한다.
  - `reusable 먼저 -> net-new subset sequential` hard rule로 쓴다.
  - reusable 검토를 건너뛴 net-new big-bang reopen을 금지한다.
  - Rule 3의 sequencing은 explicit reopen gate가 이미 열린 뒤 적용되는 wave ordering이지, reopen gate timing이나 reopen admissibility 자체를 정의하지 않는다.
- Hold 문장은 round hold를 정확히 5문 안팎으로 압축하되 아래 금지선을 모두 보존한다.
  - former `bucket_2 599` non-retroactivity
  - priority axis 비개방
  - `30-cap` frozen invariant
  - reopen gate / closure boundary 무변경
  - runtime / publish / terminal snapshot 무변경
- `Reopen gate와의 연결` 섹션에는 아래 문장을 명시한다.
  - 이 원칙이 발동되는 지점은 `A-4-1 rework round opening` 직후의 round manifest 작성 시점이다.
  - 이 원칙은 reopen gate를 대신 정의하지 않는다.

### 4-2. 산출물

- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`

### 4-3. Review gate

- Critical
  - Rule 1-3 중 하나라도 Phase 1 축과 불일치
  - Rule 2가 정성적 subset rule이 아니라 사실상 numeric cap으로 회귀
  - Rule 3가 사실상 reopen gate 재정의 또는 reopen admissibility rule로 회귀
  - hold 문장이 기존 terminal snapshot / reopen gate / runtime-publish contract를 흔듦
  - `manifest 작성 시점` 연결 문장이 빠져 activation point가 모호함
- Important
  - 설계·검증 동질성 4기준 중 하나 누락
  - Rule 2의 4기준 결합 방식이 누락됨
  - 기존 결정과의 관계가 `하위 sizing layer`로 읽히지 않음
  - Non-goal이 reopen gate 재정의처럼 오독될 여지
- Minor
  - 문장 길이 또는 섹션 제목 표기

### 4-4. 종료 조건

- 문서 전체 review가 `Good / Critical / Important / Minor / PASS / FAIL` 형식으로 수행된다.
- 최종 판정이 `PASS`다.

---

## 5. Phase 3 — `DECISIONS.md` 봉인 문장 작성

**목적:** Phase 2의 governance text를 current authority consumer가 바로 읽는 단일 결정 항목으로 압축한다.

### 5-1. 해야 할 일

- `docs/DECISIONS.md`에 신규 entry 1건을 draft한다.
- entry headline은 아래 문구를 기본안으로 사용한다.

```text
## 2026-04-20 — future explicitly-opened A-4-1 / cluster-budget reopen round는 subset-bounded single-authority sizing rule을 따른다
```

- 실제 `docs/DECISIONS.md` 반영 시 headline은 기존 entry 관행에 맞춰 한 줄 헤더로 유지한다.

- 본문 구조는 아래 다섯 블록으로 고정한다.
  - `상태: 채택`
  - `결정`
  - `추가 결정`
  - `이유`
  - `영향`
- `추가 결정`에는 최소 아래 항목을 압축 반영한다.
  - Rule 1: lane ownership 혼재 금지
  - Rule 2: subset-bounded sizing
  - Rule 3: reusable-first sequential ordering
  - authoritative provenance: `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`
  - 문제의식 출처: former `bucket_2 599`, retroactive 적용 없음
  - 기존 `policy widening -> A-4-1` 순서와 `cluster_count_limit = 30` frozen invariant 유지

### 5-2. 산출물

- `docs/DECISIONS.md` 신규 draft entry 1건

### 5-3. Review gate

- Critical
  - 기존 2026-04-15 / 2026-04-16 결정과 직접 충돌
  - 신규 entry가 `30-cap`이나 sequencing을 덮어쓰는 상위 결정처럼 씀
  - provenance 문구가 retroactive rewrite처럼 읽힘
- Important
  - `추가 결정` 압축에서 Rule 1-3 중 하나 누락
  - impact 문장이 `immediate next round planned`처럼 오해될 여지
- Minor
  - 제목 줄바꿈, 날짜, 용어 정렬

### 5-4. 종료 조건

- review `PASS`
- 기존 결정 전체와의 충돌 / 중복 double-check 완료

---

## 6. Phase 4 — 정합성 검토 및 Closeout

**목적:** amendment text가 기존 authority와 forward / backward 양방향으로 맞물리고, current terminal snapshot을 건드리지 않는다는 점을 닫는다.

### 6-1. 점검 항목

1. `Forward consistency`
   - Phase 0 -> Phase 2 -> Phase 3으로 내려오며 의미가 좁아지기만 하고 바뀌지 않는가
2. `Backward consistency`
   - 아래 기존 결정 5개와 충돌이 없는가
   - 2026-04-15 `30-cap frozen`
   - 2026-04-16 `policy widening -> A-4-1`
   - 2026-04-16 residual round frozen-budget hold branch
   - 2026-04-17 `identity_fallback` terminal roadmap completion
   - 2026-04-19 SDRG closeout
3. `Terminal snapshot read rule non-conflict`
   - 닫힌 lane를 active debt 또는 next queue처럼 다시 읽게 만들지 않는가
4. `Reopen gate non-conflict`
   - 자동 next round를 암시하지 않는가
5. `Authority footing consistency`
   - recent terminal-state decisions와 explicit reopen gate가 primary authority로 유지되고, [5] 역할 침범 금지 유비는 보조 지위로만 남는가
6. `Non-mutation confirmation`
   - terminalized lane, runtime, publish, current authoritative artifact가 무변경으로 명시되는가
7. `Future hook scenario`
   - 첫 실제 발동 케이스를 1개 기술하되, 그것이 현재 round opening을 뜻하지 않는다고 함께 적는가
   - template: `이 amendment가 발동되는 첫 상황은 [가상 조건]이다. 단, 이 scenario는 현재 round opening을 의미하지 않으며, no_immediate_next_round_planned = true는 유지된다.`

### 6-2. Closeout 판정

- `A complete`
  - amendment text adopted
  - 비충돌 확인
  - 적용 범위 고정
  - execution ownership은 future round로 분리
- `B not opened`
  - `bucket_1 / bucket_2` execution plan 미개시
  - current terminal snapshot 무변경
  - runtime / publish 무변경

### 6-3. Optional downstream note

- `docs/ROADMAP.md`에는 필요 시 short reference addendum 또는 1줄 참조를 추가할 수 있다.
- `docs/ARCHITECTURE.md`에는 필요 시 `cluster budget reopen은 bounded subset governance를 전제로 한다`는 1줄 boundary note만 추가할 수 있다.
- 두 문서는 authority write surface가 아니며, single source of authority는 계속 `docs/DECISIONS.md`다.

### 6-4. 산출물

- consistency review memo 1건
- closeout note 1건
- 필요 시 optional patch memo 2건

### 6-5. Review gate

- Critical
  - 7개 점검 중 하나라도 `FAIL`
  - amendment가 terminal snapshot current-state consumer를 흔듦
  - future hook scenario가 사실상 immediate reopen announcement처럼 씀
- Important
  - optional downstream note가 authority 문구처럼 과대 작성됨
  - backward check 대상 5개 중 하나라도 누락
- Minor
  - closeout 판정 표기

### 6-6. 종료 조건

- 7개 점검 전부 `PASS`
- 세션 종료 후에도 current state는 `no immediate next round planned`로 읽힌다.

---

## 7. Phase Transition Rule

각 phase는 아래 두 조건이 모두 충족될 때만 다음으로 넘어간다.

1. 해당 phase deliverable이 모두 생성됨
2. 해당 phase review gate가 `PASS`

운영 규칙:

- `FAIL -> 수정 -> 재review`를 반복한다.
- 같은 Critical이 반복되면 이전 phase로 자발 복귀한다.

---

## 8. Review Protocol

모든 phase review는 아래 고정 형식을 따른다.

1. `Good`
2. `Critical`
3. `Important`
4. `Minor`
5. `PASS / FAIL`

`Critical = 0`이면서 핵심 종료 조건이 충족될 때만 `PASS`를 부여한다.
`Important` 미해결 항목은 `PASS`를 막지 않지만, closeout memo에 carry-forward 항목으로 기록한다.

---

## 9. 성공 기준

### 9-1. 최소 성공

- scope lock이 `future reopen sizing governance` 하나로 끝까지 유지된다.
- `30-cap frozen`, `policy widening -> A-4-1`, terminal snapshot read rule이 모두 유지된다.
- lane ownership / subset-bounded sizing / reusable-first sequencing이 단일 policy sentence 체계로 묶인다.
- `DECISIONS.md` 신규 entry가 기존 결정과 충돌 없이 닫힌다.

### 9-2. 좋은 성공

- future `A-4-1` reopen에 대해 big-bang reopen 대신 bounded subset sequence 해석을 제공하는 policy text가 남는다.
- priority axis를 억지로 같이 닫지 않고 별도 future round로 분리한다.
- optional `ROADMAP.md` / `ARCHITECTURE.md` note가 authority와 reference의 위계를 흐리지 않는다.

### 9-3. 실패

- amendment가 현재 lane를 reopen한 것처럼 읽힌다.
- `30-cap` 또는 reopen gate를 사실상 재정의한다.
- policy widening과 cluster-budget reopen의 순서를 뒤집는다.
- `bucket_2 599`를 current authority rewrite 근거로 사용한다.

---

## 10. Read Map

```text
Phase 0  -> scope lock
Phase 1  -> axes definition
Phase 2  -> governance text drafting
Phase 3  -> DECISIONS entry compression
Phase 4  -> consistency review and closeout
```

이 문서의 역할은 future `A-4-1 / cluster-budget reopen`을 지금 실행하는 것이 아니라, reopen이 실제로 열릴 때 어떤 sizing rule을 먼저 읽어야 하는지 governance contract로 봉인하는 데 있다.
