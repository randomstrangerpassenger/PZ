# Iris Checkpoint Allocation Path-Budget Remediation Plan

상태: `owner_approved_by_2026-08-26_execution_prompt / independent_codex_review_pass_actionable_0`

상위 근거: `docs/Philosophy.md`, `docs/EXECUTION_CONTRACT.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/iris_current_historical_physical_separation_and_repository_lightweighting_plan.md`

## 1. Objective

Iris current/historical physical-separation 계획의 Checkpoint A가 실제 baseline test를 시작하기 전에 실패한 Windows path-budget 충돌을 해소한다. `checkpoint` allocation의 경로 표시명만 compact하게 만들고, receipt와 ledger가 소유하는 claim/attempt/run identity 및 canonical gate의 56-character limit는 유지한다.

관측된 실패는 S0 `25fee9103d0c8c2293f06bc498b23bae91aab9dc`에서 canonical launcher exit `2`, `Windows execution checkout root is too long ... (129 > 56)`이다. 계획이 고정한 claim/attempt를 사용하면 가능한 가장 짧은 `C:\x` parent에서도 derived checkout root가 91자로 56자를 초과한다.

## 2. Scope

* `Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1`의 `checkpoint` profile base directory naming
* allocator와 residual protected-surface validator의 새 identity를 결속하는 append-only successor manifest
* `Iris/test/validate_residual_refactor_surfaces.ps1`의 bounded successor-manifest admission
* 이 remediation plan
* 변경 후 exact Checkpoint A Run A/Run B/comparator 재실행

### Explicitly Out Of Scope

* canonical gate의 56-character limit 변경
* `physical-capacity`, `terminal-run-a`, `terminal-run-b` root schema 또는 lifecycle 변경
* allocation receipt/ledger schema, claim ID, attempt ID, run ID 의미 변경
* Iris product/runtime/data/public text 변경
* main lightweighting plan의 Change 1B 이후 구현

## 3. Planned Change

`checkpoint` profile의 base name을 receipt/ledger에 이미 기록되는 full claim/attempt text에서 분리해 `cp-<run-id-first-12>`로 고정한다. `terminal-run-a`의 기존 compact naming 선례와 같은 방식이며 uniqueness는 128-bit generated run ID와 prior-ledger/create-new checks가 계속 소유한다. Full claim ID와 attempt ID는 directory name이 아니라 immutable allocation receipt와 append-only ledger에 그대로 남는다.

기존 evidence-lightweighting protected-surface manifest와 adoption receipt는 sealed historical record로 유지하고 rewrite하지 않는다. 신규 `Iris/validation/clean_checkout/authority/iris_lightweighting_checkpoint_allocator_successor.json`은 S0 predecessor commit/tree, allocator와 residual validator의 before/after Git blob 및 LF-normalized SHA-256, owner와 reason을 기록한다. Residual validator는 이 exact schema/path의 tracked durable manifest만 읽고, predecessor ancestry와 row exact set, before/after identity, current HEAD/working parity를 fail-closed 검증한 뒤 기존 protected-row authorization map에 successor rows를 합성한다.

## 4. Validation Plan

1. exact plan-required claim/attempt와 create-new external parent로 `checkpoint` allocation을 한 번 수행한다.
2. receipt의 claim/attempt/profile/run identity와 empty roots를 확인한다.
3. derived `<work>\x` length가 canonical maximum 56 이하인지 확인한다.
4. successor manifest의 base ancestry, two-row exact set, Git blob/LF hash와 protected-surface authorization을 확인한다.
5. 수정 commit을 새 S0로 삼아 physical-separation 계획의 Checkpoint A Run A/Run B/comparator를 실행한다.

계획에 없는 전체 테스트, runtime/manual test, package test는 실행하지 않는다. Checkpoint A가 실패하면 원래 lightweighting 계획의 progression은 계속 닫힌다.

## 5. Risk Surface Touch

* Authority Surface: current external-root allocator와 protected-surface validator implementation identity가 append-only successor manifest를 통해 바뀐다.
* Runtime Behavior Surface: 없음.
* Compatibility Surface: allocation directory의 비권위적 표시명이 바뀌며 receipt/ledger schema와 CLI는 유지된다.
* Sealed Artifact Surface: 기존 receipt/ledger는 rewrite하지 않는다.
* Public-Facing Output Surface: 없음.

## 6. Rollback

remediation implementation commit을 normal Git revert한다. 이미 생성된 external allocation은 재사용하거나 삭제하지 않고 기존 ledger의 historical attempt로 둔다.

## 7. Governance Constraints

* owner approval은 2026-08-26 사용자 execution prompt가 사전 부여했다.
* 구현 전에 independent Codex Reviewer가 이 bounded remediation을 승인해야 한다.
* allocator identity가 바뀌므로 기존 terminal-v15 environment는 package-source binding이 변하지 않는 한 재봉인하지 않는다.
* 기존 실패 receipt를 수정하거나 성공으로 재분류하지 않는다.
* 성공 시 새 remediation commit을 lightweighting S0로 채택하고 Checkpoint A부터 다시 시작한다.

## 8. Expected Closeout

목표는 `complete`: compact checkpoint allocation이 canonical path budget을 충족하고 새 S0의 Checkpoint A가 Run A/Run B/comparator 모두 exit `0`일 때만 닫는다. 이는 원래 lightweighting 계획 전체의 완료를 뜻하지 않는다.
