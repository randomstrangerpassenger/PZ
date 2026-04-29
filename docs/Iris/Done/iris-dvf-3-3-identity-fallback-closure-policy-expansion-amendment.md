# Iris DVF 3-3 Identity Fallback Closure Policy Expansion Amendment

> 상태: FINAL v1.0  
> 기준일: 2026-04-16  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/iris-dvf-3-3-identity-fallback-residual-round-final-integrated-execution-plan.md`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_post_closeout_branch_decision.json`  
> 목적: current residual round closeout 이후, `carry_forward_hold`의 상당 부분이 아이템 문제가 아니라 closure policy boundary의 문제였음을 반영해 **별도 closure policy round** 기준을 고정한다. current residual round execution artifact는 그대로 유지하고, policy 변경은 별도 round authority로만 다룬다.

> 이 문서는 current residual round execution 결과를 소급 수정하지 않는다.  
> current executed round는 그대로 닫힌 상태로 유지하고, 이후 policy amendment가 필요한 경우 어떤 기준으로 reopen할지 정의하는 문서다.

---

## 0. 이 amendment가 아닌 것

아래 해석은 금지한다.

- current residual round의 실행 결과를 소급해서 다시 분류하는 것
- `carry_forward_hold 4`를 same-session unfinished queue로 읽는 것
- `bucket_3_scope_hold 7`을 closure policy amendment만으로 다시 여는 것
- closure policy 수정과 `A-4-1 rework / cluster budget` round opening을 같은 일로 읽는 것
- publish exposure 변경, runtime Lua overwrite, manual in-game validation을 policy amendment와 섞는 것

즉 이 amendment는 **current round reopen**이 아니라, `maintain_frozen_budget_hold` 이후에 별도 policy round를 열 경우 따라야 할 기준 재정의다.

---

## 1. Opening baseline

### 1-1. Current authority baseline

이 amendment는 아래 closeout snapshot을 baseline으로 사용한다.

| 항목 | 값 |
|---|---|
| promoted executable subset baseline | `600` |
| current runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| residual round closeout split | `absorption 2 / direct_use 4 / carry_forward_hold 4` |
| current frozen hold accounting | `carry_forward_hold 4 + bucket_3_scope_hold 7 = 11` |
| current selected branch | `maintain_frozen_budget_hold` |
| cluster budget | `30 / 30` (frozen) |

### 1-2. Amendment authority input

1. `docs/Iris/Done/iris-dvf-3-3-identity-fallback-residual-round-final-integrated-execution-plan.md`
2. `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json`
3. `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_report.json`
4. `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_post_closeout_branch_decision.json`

### 1-3. Policy round separation

이 amendment의 해석 단위는 `current residual round`가 아니라 **future closure policy round** 다.

- current round: 그대로 closed
- current branch: `maintain_frozen_budget_hold`
- future policy round: current closed state 위에서만 별도로 open

---

## 2. 제안별 최종 판정

| 제안 | 판정 | current authority |
|---|---|---|
| `direct_use` admissibility 확장 | 채택 | non-cluster closure path로 재정의 |
| dominant/dual-context 허용 | 축소 채택 | structural convergence만 허용 |
| recipe/build chain evidence 승격 | 분리 채택 | declared chain만 허용 |
| policy 확장 → 그래도 안 되면 `A-4-1` | 채택 | reopen 순서 원칙으로 고정 |

---

## 3. `direct_use` admissibility 재정의

### 3-1. 정의

`direct_use`는 "weapon-only 예외 경로"가 아니라 **item-specific evidence로 cluster를 열지 않고 닫는 non-cluster closure 경로** 다.

### 3-2. 확정 기준

아래 조건을 모두 충족하면 weapon 여부와 무관하게 `direct_use` 경로로 확정할 수 있다.

- item-specific evidence `2`개 이상 존재
- 증거들이 같은 대표 작업 맥락으로 수렴
- 한 문장 3-3 body로 닫힌다
- downstream 검증을 새로 요구하지 않는다

### 3-3. 결과적 의미

- `direct_use`는 더 이상 weapon-only 운영 관행에 묶이지 않는다.
- cluster를 새로 열 필요가 없는 closure면 `direct_use`를 우선 검토할 수 있다.
- 다만 item-specific evidence 없이 broad category wording으로 밀어붙이는 것은 계속 금지한다.

### 3-4. 예상 적용

- `Base.Sledgehammer`
- `Base.Sledgehammer2`

위 두 item은 demolition-dominant evidence가 이미 있으므로, future policy round에서는 `direct_use` primary candidate로 재분류할 수 있다.

---

## 4. dominant/dual-context 구조적 판정 기준

### 4-1. dominant-context

주 맥락이 명확하고 부 맥락이 종속적이면 주 맥락으로 닫는다.

예시:

- `farming.WateredCan`: 원예 dominant, 물 취급 부 맥락

### 4-2. dual-context 예외 허용

두 맥락이 **같은 대표 작업 맥락으로 구조적으로 수렴**할 때만 한 문장으로 닫는다.

허용 기준:

- compose profile의 `slot_sequence`가 두 맥락을 구조적으로 수용한다
- 두 맥락이 별도 대표 작업 맥락 두 개를 유지한 채 병렬로 남지 않는다
- item-specific representative utility가 한 문장 3-3 body로 닫힌다

### 4-3. 금지선

아래 판정은 금지한다.

- "문장이 자연스럽다"
- "style상 부드럽다"
- "compose 결과가 보기 좋다"

판정 기준은 어디까지나 **구조적 수렴 가능 여부** 다. style이나 surface naturalness는 closure admissibility 기준이 아니다.

### 4-4. 예상 적용

- `farming.WateredCan`: dominant-context 판정 후보
- `Base.HandScythe`: manual validation 뒤 dominant-context 또는 structural dual-context 수렴 여부 판정 후보

---

## 5. declared transform/build chain evidence boundary

### 5-1. 허용

아래는 evidence로 인정한다.

- recipe transform fact
- build requirement fact
- declared transform/build chain

허용 조건:

- chain의 각 단계가 독립적으로 선언된 구조적 사실이다
- transform과 requirement가 모두 바닐라 선언 구조 안에 있다
- chain이 한 단계 또는 매우 짧은 deterministic chain이다
- item-specific representative utility를 한 문장 3-3 body로 닫을 수 있다

### 5-2. 금지

아래는 허용하지 않는다.

- chain 전체를 묶어서 최종 용도를 해석하는 것
- "더 파면 이런 의미일 것이다" 식의 utility inference
- declared fact를 넘어서 derived utility interpretation으로 가는 것

예시:

- 허용: `Base.Rope`는 제작/건설 requirement fact와 transform fact를 가진다
- 금지: `Base.Rope`의 주요 용도는 탈출/이동이라고 해석하는 것

### 5-3. 결과적 의미

`Base.Rope`는 future policy round에서 "결속/건설 재료" 수준까지는 닫을 수 있지만, "탈출 도구"라는 대표 의미를 current policy amendment만으로 채택하지는 않는다.

---

## 6. 순서 원칙

future reopen 순서는 아래처럼 고정한다.

1. closure policy를 먼저 확장한다
2. 그래도 canonical close가 안 되는 item만 `A-4-1 rework / cluster budget` round로 보낸다

즉 current authority는 `cluster budget reopen first`가 아니라 **policy widening first** 다.

---

## 7. item-level expected effect

| item | current residual-round closeout | future policy-round expected path |
|---|---|---|
| `Base.Sledgehammer` | `carry_forward_hold` | `direct_use` candidate |
| `Base.Sledgehammer2` | `carry_forward_hold` | `direct_use` candidate |
| `farming.WateredCan` | `carry_forward_hold` | dominant-context 기반 `direct_use` 또는 absorption 재검토 |
| `Base.HandScythe` | `direct_use` closeout 완료 | future rule에서는 dominant/dual-context 판정 기준의 reference case |
| `Base.Rope` | `carry_forward_hold` | declared transform/build chain 기반 `direct_use` candidate |
| `bucket_3_scope_hold 7` | frozen hold | 변경 없음 |

---

## 8. future amendment application

이 amendment는 current residual round plan 본문을 소급 수정하지 않는다.  
대신 future closure policy round 또는 plan amendment에서 아래 구조를 따라야 한다.

- Section `3-2`: `direct_use` fit check를 본 문서의 non-cluster closure 정의로 교체
- Section `3-3a`: dominant/dual-context structural convergence 규칙 신설
- Section `3-3b`: declared transform/build chain evidence 허용선과 derived utility interpretation 금지선 신설

즉 current `FINAL v1.0` residual round plan은 historical execution authority로 유지하고, policy 변경은 별도 amendment authority 위에서만 적용한다.

---

## 9. Success / Failure

### 9-1. Success

- current residual round와 policy amendment가 섞이지 않는다
- `direct_use`가 weapon-only 관행에서 분리된다
- dominant/dual-context 판정이 style judgement가 아니라 structural rule로 고정된다
- declared chain과 derived interpretation의 경계가 분명해진다
- `A-4-1`은 policy widening 이후의 후순위 gate로만 남는다

### 9-2. Failure

- current executed round 결과를 policy amendment로 소급 변경한다
- dual-context 허용을 style judgement로 열어버린다
- declared chain evidence를 utility interpretation까지 확장한다
- policy 문제와 taxonomy 문제를 구분하지 않은 채 곧바로 `A-4-1`을 연다
