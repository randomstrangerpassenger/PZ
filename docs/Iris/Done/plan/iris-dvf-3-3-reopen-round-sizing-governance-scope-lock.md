# Iris DVF 3-3 Reopen Round Sizing Governance Scope Lock

> 상태: Final v1.0  
> 기준일: 2026-04-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 동반 문서: `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-amendment-final-integrated-plan.md`, `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`  
> 목적: future explicitly-opened `A-4-1 rework / cluster budget` reopen round에만 적용되는 sizing governance amendment의 범위와 금지선을 먼저 봉인한다.

> 이 문서는 current round opening을 선언하지 않는다.  
> 이 문서는 future reopen이 실제로 열릴 때 읽을 scope contract만 고정한다.

---

## 1. 적용 대상 정의

- 구속 대상: future explicitly-opened `A-4-1 rework / cluster budget` reopen round.
- 비구속 대상: `scope_policy_override_round`, `runtime_adoption_round`, closure policy round, `future_new_source_discovery_hold`.
- `future_new_source_discovery_hold`는 item-level evidence gate이므로 cluster-budget reopen sizing amendment의 적용 대상이 아니다.

## 2. 문제의식 Provenance

- former `bucket_2 599 net-new cluster required`는 big-bang reopen 위험을 드러낸 동기다.
- 과거 사례는 동기일 뿐이며, 이 amendment는 과거 closeout, terminal snapshot, runtime/publish authority를 retroactive mutate하지 않는다.

## 3. 기존 결정과의 관계

- 2026-04-16 `closure policy widening -> 그래도 canonical close 불가 시 A-4-1` 순서는 그대로 유지한다.
- 2026-04-15 `cluster_count_limit = 30` frozen invariant는 그대로 유지한다.
- 이 amendment는 recent terminal-state decisions와 explicit reopen gate 위에서만 작동하는 하위 sizing layer이며, current `no_immediate_next_round_planned = true` 읽기 규칙을 바꾸지 않는다.

## 4. Non-goal

- 이 amendment는 reopen 여부 판정 규칙이 아니다.
- 이 amendment는 reopen gate 정의를 바꾸지 않는다.
- 이 amendment는 closure policy boundary를 바꾸지 않는다.
- 이 amendment는 execution plan을 개시하지 않는다.

## 5. Axes

### 5-1. Axis A — Lane ownership

- 허용: 한 reopen round manifest가 `existing-cluster reuse` authority만 소유하거나, `net-new cluster design` authority만 소유하는 것.
- 금지: 같은 round manifest 안에서 `reuse`와 `net-new design` authority를 혼재시키는 것.

### 5-2. Axis B — Subset-bounded sizing

- 허용: 절대 수치 cap 대신 `subset-bounded single-authority sizing` 원칙으로 round 크기를 정하는 것.
- 금지: `이번 round는 몇 건 이하` 같은 numeric cap만으로 sizing legitimacy를 판정하는 것.
- subset admission은 `same representative task context`와 `same evidence / closure logic shape`를 필수 AND로 통과해야 한다.
- `same validation path / artifact contract`와 `same cluster authoring and review burden`는 same wave 내 일관성 기준으로 맞아야 하며, 완전 동일성을 hard AND로 요구하지 않는다.

### 5-3. Axis C — Ordering

- 허용: explicit reopen gate가 이미 열린 뒤 same reopen wave 안에서 `reusable 먼저 -> net-new subset sequential` 순서를 적용하는 것.
- 금지: reusable 검토 없이 곧바로 net-new cluster reopen으로 점프하는 것.
- 금지: sequencing을 reopen gate timing 또는 reopen admissibility 자체로 재정의하는 것.

### 5-4. Axis D — Priority

- 허용: priority / ranking 기준은 별도 future round에서 domain-specific 기준과 함께 다시 다루는 것.
- 금지: 이번 amendment 안에서 priority / ranking rule을 같이 닫는 것.
- 상태: explicit out-of-scope.

## 6. Review Closeout

- Good: scope는 `future A-4-1 / cluster-budget reopen`으로만 잠겼고, `future_new_source_discovery_hold`는 즉시 비구속 대상으로 봉인됐다.
- Critical: 없음.
- Important: 없음.
- Minor: 없음.
- PASS / FAIL: PASS.
