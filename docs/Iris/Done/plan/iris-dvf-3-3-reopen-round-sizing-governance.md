# Iris DVF 3-3 Reopen Round Sizing Governance

> 상태: Adopted v1.0  
> 기준일: 2026-04-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`, `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-amendment-final-integrated-plan.md`  
> 목적: future explicitly-opened `A-4-1 rework / cluster budget` reopen round를 big-bang reopen이 아니라 bounded subset sequence로 읽게 하는 governance text authority를 봉인한다.

> 이 문서는 current round opening을 선언하지 않는다.  
> 이 문서는 explicit reopen gate가 이미 열린 뒤 round manifest를 어떻게 써야 하는지에만 적용된다.

---

## 1. 적용 대상

- 이 원칙은 future explicitly-opened `A-4-1 rework / cluster budget` reopen round에만 적용된다.
- 이 원칙은 `scope_policy_override_round`, `runtime_adoption_round`, closure policy round, `future_new_source_discovery_hold`에는 적용되지 않는다.
- activation point는 explicit reopen gate가 이미 열린 직후의 round manifest 작성 시점이다.

## 2. 문제의식 Provenance

- former `bucket_2 599 net-new cluster required`는 cluster-budget reopen을 한 번에 크게 여는 방식의 위험을 드러낸 동기다.
- 이 원칙은 과거 사례를 현재 authority rewrite 근거로 쓰지 않으며, terminalized lane, runtime/publish contract, historical closeout artifact를 retroactive mutate하지 않는다.

## 3. Core Principle

future explicitly-opened `A-4-1 / cluster-budget reopen` round는 `subset-bounded single-authority sizing rule`을 따른다. 즉 one-shot big-bang reopen이 아니라, 하나의 round manifest가 하나의 authority lane만 소유하는 bounded subset sequence로만 설계한다.

이 원칙의 primary authority footing은 recent terminal-state decisions(`active_execution_lane_count = 0`, `no_immediate_next_round_planned = true`)와 explicit reopen gate다. `docs/Philosophy.md` [5] 역할 침범 금지 원칙은 모듈 경계를 round 경계로 옮기는 supplementary analogy로만 사용한다.

## 4. Rule 1 — Lane Ownership Separation

- 하나의 reopen round manifest는 `existing-cluster reuse` authority와 `net-new cluster design` authority 중 하나만 소유한다.
- `reuse subset`과 `net-new subset`이 모두 필요하더라도 같은 reopen wave 안에서 separate sequential round로 분리한다.
- 같은 round manifest 안에서 reuse와 net-new design authority를 혼재시키는 것은 금지한다.

## 5. Rule 2 — Subset-Bounded Sizing

- round sizing legitimacy는 numeric cap이 아니라 `subset-bounded single-authority sizing`으로 판정한다.
- subset admission은 아래 4기준으로 판정한다.
  - `same representative task context`
  - `same evidence / closure logic shape`
  - `same validation path / artifact contract`
  - `same cluster authoring and review burden`
- 첫 두 기준은 필수 AND다. 즉 대표 작업 맥락과 evidence / closure logic shape가 같이 맞지 않으면 같은 subset으로 묶지 않는다.
- 뒤 두 기준은 same wave 내 일관성 기준이다. validation path와 authoring/review burden은 같은 wave 안에서 일관되게 유지돼야 하지만, 완전 동일성을 hard AND로 요구하지 않는다.
- `이번 round는 몇 건 이하` 같은 numeric cap alone으로 round 크기를 정당화하는 것은 금지한다.

## 6. Rule 3 — Sequencing

- explicit reopen gate가 이미 열린 뒤 같은 reopen wave 안에서는 `reusable 먼저 -> net-new subset sequential` 순서를 hard rule로 따른다.
- reusable 검토를 건너뛴 채 곧바로 net-new cluster reopen으로 점프하는 것은 금지한다.
- 이 sequencing은 wave ordering rule이지, reopen gate timing이나 reopen admissibility 자체를 정의하는 규칙이 아니다.

## 7. Hold

- former `bucket_2 599`는 동기일 뿐이며 retroactive rewrite 근거가 아니다.
- priority / ranking axis는 이번 amendment에서 열지 않는다.
- `cluster_count_limit = 30` frozen invariant는 이 amendment로 바뀌지 않는다.
- reopen gate 목록과 closure policy boundary는 이 amendment로 바뀌지 않는다.
- terminalized lane, runtime/publish contract, current terminal snapshot consumer model은 이 amendment로 바뀌지 않는다.

## 8. 기존 결정과의 관계

- 2026-04-15 결정인 `current source expansion cycle에서는 A-4-1 interaction cluster budget 30을 재개방하지 않는다`를 유지한다.
- 2026-04-16 결정인 `closure policy widening -> 그래도 canonical close 불가 시 A-4-1` 순서를 유지한다.
- 2026-04-16 이후 terminal snapshot consumer model과 explicit reopen gate read rule을 유지한다.
- 2026-04-17 결정인 `identity_fallback current roadmap은 terminal policy authority 기준으로 완료 상태다`와 `no immediate next round planned` 읽기 규칙을 유지한다.
- 이 원칙은 위 결정들의 상위 replacement가 아니라, explicit reopen gate 이후 manifest sizing에만 적용되는 하위 operating layer다.

## 9. Non-goal

- 이 원칙은 reopen gate를 정의하거나 판정하지 않는다.
- 이 원칙은 closure policy widening을 대체하지 않는다.
- 이 원칙은 `30-cap` 재검토를 개시하지 않는다.
- 이 원칙은 runtime/publish mutation이나 execution plan 작성을 개시하지 않는다.

## 10. Reopen Gate와의 연결

- 이 원칙이 발동되는 지점은 future explicitly-opened `A-4-1 rework / cluster budget` round의 opening 직후 round manifest를 작성하는 시점이다.
- 이 원칙은 explicit reopen gate를 대신 정의하지 않는다.
- 이 원칙의 채택은 current state를 reopen 상태로 바꾸지 않으며, `no_immediate_next_round_planned = true` 읽기 규칙은 explicit opening이 있기 전까지 유지된다.

## 11. Review Closeout

- Good: lane ownership, subset-bounded sizing, reusable-first sequencing이 terminal-state decisions와 explicit reopen gate 위에서 충돌 없이 닫혔다.
- Critical: 없음.
- Important: 없음.
- Minor: 없음.
- PASS / FAIL: PASS.
