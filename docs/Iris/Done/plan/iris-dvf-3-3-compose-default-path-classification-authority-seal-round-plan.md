# Iris DVF 3-3 Compose Default Path Classification & Authority Seal Round Plan

기준일: `2026-04-22`  
버전: `v1.4`  
상태: planning authority draft; Phase 0 close requires Tier 2 design adversarial review artifact  
라운드 이름: `Iris DVF 3-3 Compose Default Path Classification & Authority Seal Round`  
약칭: `CDPCR-AS`  
상위 기준: `docs/Philosophy.md` > `docs/DECISIONS.md` > `docs/ARCHITECTURE.md` > `docs/ROADMAP.md`  
authority input: `Iris DVF 3-3 Compose Default Path Classification Round - 통합 로드맵 v1.0`, `CDPCR-AS v1.0 통합 최종 검토안`, `CDPCR-AS v1.1 통합 최종 검토안`, `CDPCR-AS v1.2 통합 최종 검토안`, `CDPCR-AS v1.3 operational completeness feedback` (2026-04-22 user-provided reviews)

---

## 1. Round Identity

이 round는 **implementation-drift verification + authority seal round**다.

이미 상위 문서는 `compose_profiles_v2` 경로의 runtime compose authority를 `body_plan` writer로 닫아 두었다. 따라서 CDPCR-AS의 질문은 "authority가 무엇인가"를 다시 판정하는 것이 아니라, **이미 채택된 `body_plan` authority가 기본 compose entrypoint에서 실제로 집행되는가**를 확인하는 것이다.

| Tier | 성격 | 활성 조건 |
|---|---|---|
| Tier 1 | pure observer diagnostic | 항상 실행 |
| Tier 2 | targeted authority seal | Phase 4 판정이 Branch A이고 Phase 0 design review gate가 닫혔을 때만 실행 |

이 문서는 "본문을 더 좋게 쓰는 계획"이 아니다.  
이 문서는 **기본 compose entrypoint가 legacy `sentence_plan` path로 미끄러지는 구현 drift가 있는지 먼저 확인하고, 증거와 설계 review가 충분할 때만 default authority를 `compose_profiles_v2 + body_plan`으로 봉인하는 실행 계획**이다.

### Scope Lock

이번 round의 Tier 1은 observer lane이며 수정 라운드가 아니다. Tier 1에서는 어떤 runtime canonical 산출물도 수정하지 않는다.

### Non-goals

이번 round에서 열지 않는 항목은 아래처럼 봉인한다.

- semantic redesign
- `quality_state / publish_state` axis 재정의
- runtime-side compose/rewrite
- compose 외부 repair stage 재도입
- staged/static closeout을 deployed closeout으로 승격
- Phase C compatibility adapter 제거 또는 위치 이동
- `quality_baseline_v4 -> v5` cutover
- manual in-game validation 또는 ready-for-release 선언

---

## 2. Global Invariants and File Integrity Contract

아래 수치는 Tier 1, Tier 2, closeout 전 구간에서 변경 불가능한 sealed invariant다.

| 항목 | 값 |
|---|---|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish_split | `internal_only 617 / exposed 1467` |
| quality_split | `strong 1316 / adequate 0 / weak 768` |
| sealed_staged_lua_parity_hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

Invariant 위반 산출물은 즉시 quarantine한다. 위반 상태에서는 closeout을 선언할 수 없다.

### mtime / hash contract split

- Tier 1 전 구간: sealed Lua 파일 mtime과 hash 불변이 모두 필수다.
- Tier 2 전 구간: sealed invariant는 hash 값 유지로 판정한다. Phase 5~8 code path 변경과 재생성 때문에 mtime이 바뀌는 것은 허용되지만, hash 불일치는 drift로 판정한다.
- Branch B/C 전 구간: canonical artifact 재생성은 금지하며, sealed/workspace Lua mtime과 hash 불변을 read-only로 확인한다.

---

## 3. Tier 1 Non-writer Clause

Tier 1의 모든 산출물은 `observer_only`다. Tier 1은 아래 namespace를 authority mutation 대상으로 삼지 않는다.

- `IrisLayer3Data*.lua`
- `dvf_3_3_rendered_*.json`
- `quality_publish_decision_*.jsonl`
- `body_plan_structural_reclassification_*.jsonl`
- `body_plan_v2_*.json`

Tier 1 산출물 경로는 아래 한 곳으로만 제한한다.

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/
```

Tier 1에서 이 경로 밖으로 diagnostic artifact가 생성되면 round contract violation으로 기록한다.

Tier 2 rollback verification용 reference artifact(예: `tier2_pre_change_snapshot.json`)는 state를 기록만 하는 read-only artifact이므로 `diagnostic/` 하위에 둘 수 있다. 이들은 runtime canonical authority가 아니다.

---

## 4. Phase Order

```text
Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4

Branch A -> Phase 5 -> Phase 6 -> Phase 7 -> Phase 8 -> Phase 9
Tier 1-only Branch A -> Phase 8(read-only integrity only) -> Phase 9
Branch B -> Phase 8(read-only integrity only) -> Phase 9
Branch C -> Phase 8(read-only integrity only) -> Phase 9
Branch D -> rollback -> Phase 8(read-only integrity only) -> Phase 9
Branch D + rollback verification failure -> suspended_pending_manual_recovery (Phase 9 미실행)
```

운영 규칙은 아래처럼 고정한다.

- Phase 0은 round-local opening seal이며, top docs adopted entry를 쓰지 않는다.
- Phase 1~4는 Tier 1 observer lane이다.
- Phase 5~7은 Branch A에서만 열리는 Tier 2 authority seal lane이다.
- Tier 1-only re-scope된 Branch A는 Phase 5~7을 건너뛰고 Phase 8 Branch B/C scope(read-only integrity confirmation)로 이동한 뒤 Phase 9 closeout한다.
- Branch B/C에서는 Tier 2를 건너뛰고 read-only integrity confirmation만 수행한다.
- Branch D는 Phase 4 classification branch가 아니라, Branch A Tier 2 실행 후 Phase 8에서 발생할 수 있는 `tier_2_induced_drift` 실패 상태다.
- Phase 9에서만 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`를 closeout state로 갱신한다.

---

## 5. Phase 0 - Opening Seal

### 목적

CDPCR-AS를 semantic/quality repair round 또는 authority 재심 round로 오해하지 않도록, round-local scope와 Tier 2 design review gate를 먼저 봉인한다.

### Required Outputs

Phase 0은 top docs를 수정하지 않는다. Phase 0 산출물은 round-local diagnostic path에만 둔다.

- `diagnostic/scope_lock.md`
- `diagnostic/tier2_design_adversarial_review.md`
- `diagnostic/phase0_opening_seal.json`

### Tier 2 Design Review Requirement

Tier 2 design adversarial review는 Phase 0 내부에서 수행한다. Phase 0 시작 자체의 precondition은 이 plan v1.4의 채택뿐이며, review는 Phase 0 close gate의 blocker다.

`diagnostic/tier2_design_adversarial_review.md`는 Tier 2 코드 변경 시작 전에 존재해야 하는 설계 가드 artifact다. Review 대상은 아래 세 가지다.

- `compose_profiles_v2.json` 고정 방식
- explicit mode enum 또는 flag surface shape
- implicit legacy fallback 제거 구현 방식

이 review 기록 없이 Phase 0은 close할 수 없고, Branch A 판정이 나오더라도 Phase 5~7을 실행할 수 없다.

### Tier 2 Design Review Failure Path

Tier 2 design review fail 시 design을 수정하여 재review한다. 재review는 최대 3회까지 시도한다. 그 이후에도 design이 수렴하지 않으면 이 plan을 Tier 1-only로 re-scope하고 `diagnostic/scope_lock.md`에 기록한다.

Tier 1-only re-scope 시 Branch A 판정이 나와도 Phase 5~7은 실행하지 않는다. Phase 9 closeout wording은 아래 문구로 기록한다.

> Tier 1 verification closed, Tier 2 seal withheld due to design review non-convergence.

### Required Wording

문서 어딘가에 아래 문장이 그대로 존재해야 한다.

> 이번 round의 Tier 1은 observer lane이며 수정 라운드가 아니다.

### Exit Gate

- `diagnostic/` 경로 생성 완료
- `diagnostic/scope_lock.md` 작성 완료
- `diagnostic/tier2_design_adversarial_review.md` 작성 및 review 결론 기록 완료
- invariant block과 non-writer clause가 round-local artifact에 존재
- semantic redesign, quality/publish axis 재정의, runtime-side compose/rewrite 금지가 명시됨
- `rg -n "CDPCR-AS|Compose Default Path Classification" docs/DECISIONS.md docs/ARCHITECTURE.md docs/ROADMAP.md` 결과가 empty임으로 top docs adopted entry가 Phase 0에서 작성되지 않았음을 확인

### Plan State Transition

이 plan의 상태 전이 규칙은 identifier-style로 고정한다.

- `draft` -> `in_execution`
- `draft` -> `tier_1_only_in_execution`
- `in_execution` -> `closed_A`
- `in_execution` -> `closed_B`
- `in_execution` -> `closed_C`
- `in_execution` -> `closed_D`
- `in_execution` -> `suspended_pending_manual_recovery`
- `tier_1_only_in_execution` -> `closed_A_tier2_withheld`
- `tier_1_only_in_execution` -> `closed_B_tier2_withheld`
- `tier_1_only_in_execution` -> `closed_C_tier2_withheld`

`suspended_pending_manual_recovery`는 terminal state다. Manual recovery round가 CDPCR-AS를 대체하며, CDPCR-AS 자체는 자가 closeout하지 않는다.

---

## 6. Phase 1 - Probe Pre-flight

### 목적

`compose_layer3_text.py` 원본을 수정하지 않고 body_plan writer를 직접 호출할 수 있는 방법을 확정한다.

### Required Checks

| 단계 | 내용 |
|---|---|
| 1-a | 기존 flag, 환경변수, CLI 옵션 enumeration. `build_layer3_body_plan_v2_preview.py` 포함 |
| 1-b | 기존 수단이 없으면 diagnostic wrapper 설계만 검토. 구현은 아직 하지 않음 |
| 1-c | invocation method를 `(i)`, `(ii)`, `(iii)` 중 하나로 확정 |

### Method Values

| 값 | 의미 |
|---|---|
| `(i)` | 기존 flag 사용. 원본 무변경 |
| `(ii)` | diagnostic wrapper 필요. 원본 무변경, wrapper는 Phase 3-a에서 `diagnostic/` 경로에만 구현 |
| `(iii)` | 둘 다 불가. Phase 3 skip, Phase 4에서 Branch C 직접 채택 |

### Required Output

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/probe_invocation_preflight.json
```

### Exit Gate

- method가 `(i)`, `(ii)`, `(iii)` 중 하나로 확정됨
- `compose_layer3_text.py` 원본 파일 무변경 확인
- wrapper가 필요한 경우에도 Phase 1에서는 설계만 기록하고 파일 생성은 Phase 3-a까지 보류

---

## 7. Phase 2 - Branch Trace Evidence Collection

### 목적

legacy `sentence_plan` branch가 production/staged artifact 생성 경로에서 **default로 열리는지** 기록한다.

### Invocation Classes

| 부류 | 설명 |
|---|---|
| `build_script` | current staged Lua 생성에 실제 사용되는 경로 |
| `cli_direct` | CLI direct invocation entrypoint |
| `test_harness` | `tests/test_compose_layer3_text_v2.py` 포함 |
| `preview_wrapper` | `build_layer3_body_plan_v2_preview.py` |

### Invocation Class Roles

| 구분 | Class | 역할 |
|---|---|---|
| Gating | `build_script`, `cli_direct` | Branch 판정 결정권. 이 둘의 `legacy_default_open` 값이 판정을 확정한다 |
| Context-only | `test_harness`, `preview_wrapper` | 참고 증거. 단독으로 Branch 판정을 바꾸지 않는다 |

### Required Fields Per Class

- `legacy_sentence_plan_branch_hits`
- `body_plan_branch_hits`
- `trace_method`
- `trace_status`
- `legacy_supported`
- `legacy_default_open`

`legacy_supported`와 `legacy_default_open`은 반드시 분리해서 기록한다. legacy branch가 코드에 남아 있다는 사실과, default path에서 열린다는 사실은 같은 판정이 아니다.

`trace_status`는 아래 enum만 허용한다.

- `complete`
- `partial`
- `untraceable`

Coverage는 gating과 context를 분리해 계산한다.

- `gating_coverage_status`: `build_script`, `cli_direct`만으로 계산한다. 둘 다 `complete`이면 `complete`, 하나라도 `partial` 또는 `untraceable`이면 `incomplete`다.
- `context_coverage_status`: `test_harness`, `preview_wrapper`만으로 계산한다. 둘 다 `complete`이면 `complete`, 하나라도 `partial` 또는 `untraceable`이면 `incomplete`다. 참고용이며 Branch 판정을 직접 바꾸지 않는다.
- context-only class가 incomplete이면 Branch A를 차단하지 않고, closeout memo에 `supplementary_coverage_incomplete`로 기록한다.

### Required Output

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/compose_default_path_branch_trace_report.json
```

### Exit Gate

- 4개 invocation class 결과가 모두 존재
- `gating_coverage_status`와 `context_coverage_status`가 명시됨
- `legacy_default_open`이 boolean으로 기록됨
- legacy/body_plan branch hit 수치가 정수로 기록됨
- trace 수단이 `coverage.py`, import hook, log inspection 등 구체적 방법으로 남음
- `test_harness` 또는 `preview_wrapper`에서만 `legacy_sentence_plan_branch_hits > 0`이 발생하고 gating class 둘 다 `legacy_default_open = false`이면, 이 hit는 Branch 판정에 영향을 주지 않는다고 명시됨

---

## 8. Phase 3 - Parity Probe Execution

### 목적

default를 body_plan으로 고정했을 때 sealed staged Lua hash와 동일한 내용이 나오는지 확인한다.

Phase 1 method가 `(iii)`이면 Phase 3은 skip하고, Phase 4에서 Branch C를 직접 채택한다.

### Required Steps

| 단계 | 내용 |
|---|---|
| 3-a | 선택된 method로 diagnostic rendered artifact 생성. method `(ii)`이면 이 시점에 diagnostic wrapper를 `diagnostic/` 하위에만 구현한다. 파일명은 `diagnostic_` prefix 필수 |
| 3-b | diagnostic rendered artifact를 staged Lua 대응 형식으로 직렬화하고 SHA-256 계산 |
| 3-c | diagnostic hash와 sealed hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` 비교 |

### Required Output

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/compose_default_path_parity_probe_report.json
```

### Required Result Values

- `hash_comparison = match`
- `hash_comparison = mismatch`
- `phase_skipped = true`

`skip_reason` enum은 아래만 허용한다.

- `probe_method_iii`

### Exit Gate

- diagnostic artifact가 `diagnostic/` 밖으로 나가지 않음
- sealed Lua 파일은 읽기만 수행하고 재생성/덮어쓰기 금지
- Tier 1 기준 sealed Lua mtime/hash 불변 확인
- hash 비교 결과 또는 skip 사유가 명시됨

---

## 9. Phase 4 - Classification Decision

### 목적

Phase 2~3 증거로 CDPCR-AS 판정 branch를 확정한다.

### Primary Signal

Branch 판정의 primary signal은 `legacy_default_open`이다. `legacy_sentence_plan_branch_hits`는 trace 방식에 따라 코드 초기화나 compatibility object load만으로 잡힐 수 있으므로 Branch B 보조 evidence로만 사용한다.

Branch 판정 결정권은 gating class인 `build_script`와 `cli_direct`에만 있다. Context-only class인 `test_harness`와 `preview_wrapper`는 원인 설명과 regression coverage를 보강하지만, 단독으로 Branch A/B/C 판정을 바꾸지 않는다.

### Branch A - cleanup_debt_no_default_drift

아래 조건이 모두 성립해야 한다.

- `gating_coverage_status = complete`
- `build_script.legacy_default_open = false`
- `cli_direct.legacy_default_open = false`
- `hash_comparison = match`
- `sealed_staged_lua_file_integrity = unchanged`

해석: default production/staged path는 legacy `sentence_plan` branch를 열지 않으며, default를 body_plan으로 봉인해도 sealed Lua 내용이 바뀌지 않는다. Phase 0 design review gate가 닫혀 있으면 Tier 2 진입 가능.

### Branch B - entrypoint_implementation_drift

아래 조건 중 하나 이상이면 Branch B다.

- `build_script.legacy_default_open = true`
- `cli_direct.legacy_default_open = true`
- `hash_comparison = mismatch`

`legacy_sentence_plan_branch_hits > 0`은 Branch B를 보강하는 supplementary evidence다. 단독으로 Branch B를 만들지는 않는다.

해석: 이미 채택된 authority 자체가 미결인 것이 아니라, default entrypoint 구현이 legacy path를 열거나 sealed parity와 drift를 만든다. Seal round 내부에서 patch-required 상태로 기록하되, Tier 2 seal은 실행하지 않는다.

### Branch C - evidence_augmentation_required

아래 조건 중 하나 이상이면 Branch C다.

- `gating_coverage_status = incomplete`
- `probe_method = "iii"`
- `sealed_staged_lua_file_integrity = changed`
- `legacy_sentence_plan_branch_hits > 0`이지만 그 hit이 default path 외 경로(`test_harness`, `preview_wrapper`, 초기화, compatibility load 등)에서 발생했음을 증명할 trace evidence가 없음
- Phase 2/3 결과가 A/B 어느 쪽도 만족하지 않음

해석: 증거가 판정을 지지하지 않는다. Trace widening 또는 evidence round 방법론 보강이 필요하다.

### Branch D - tier_2_induced_drift

Branch D는 Phase 4에서 직접 선택되는 classification branch가 아니다. Branch A로 Tier 2를 실행한 뒤 Phase 8 `parity preservation test`가 실패했을 때만 발생하는 별도 실패 상태다.

해석: 증거가 부족한 것이 아니라, Tier 2 patch가 sealed baseline을 깨뜨렸다. 필요한 후속 작업은 trace widening이 아니라 Tier 2 design revision이다.

### Required Output

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/compose_default_path_classification_memo.md
```

### Exit Gate

- branch가 `A`, `B`, `C` 중 하나로 확정
- 후속 예약 round가 명시됨
- non-writer clause 위반 내용 없음
- 위반이 있으면 closeout 대신 failure/quarantine으로 기록

---

## 10. Phase 5 - Default Authority Source Seal

Branch A 전용 Tier 2 phase다. Branch B/C에서는 실행하지 않는다.

### 목적

기본 실행이 읽는 authority source를 `compose_profiles_v2.json + body_plan`으로 단일화한다.

### Design Rule

legacy 삭제가 아니라 default authority 박탈이다. legacy 파일과 branch는 compatibility/diagnostic 용도로 남을 수 있지만, 기본 실행에서 읽히면 안 된다.

### Pre-change Snapshot

Tier 2 변경 시작 전 영향 받는 파일들의 pre-change hash를 아래 artifact에 기록한다.

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/tier2_pre_change_snapshot.json
```

Rollback이 필요하면 이 snapshot과의 hash 일치를 기준으로 복구 완료를 검증한다.

### Required Changes

- default profile resolution을 `compose_profiles_v2.json`으로 고정
- profile 미지정 시 legacy profile로 떨어지는 암묵 fallback 제거
- `body_plan` section emission path를 default writer path로 고정
- `sentence_plan` 직접 writer path를 default branch에서 제거
- legacy 파일 존재만으로 legacy path로 미끄러지는 암묵 fallback 제거

### Required Outputs

- `diagnostic/tier2_pre_change_snapshot.json`
- 수정된 default profile resolver
- 수정된 default compose dispatch
- default path에서 제거된 legacy fallback 목록

### Exit Gate

인자 없이 실행하면 무조건 `body_plan` writer path로 진입한다.

---

## 11. Phase 6 - Legacy Path Isolation

Branch A 전용 Tier 2 phase다. Branch B/C에서는 실행하지 않는다.

### 목적

legacy `sentence_plan` 경로를 제거하지 않고 명시적 격리 구역으로 이동시킨다.

### Execution Modes

| 모드 | 역할 |
|---|---|
| `default` | body_plan writer. 인자 없는 기본 실행 |
| `compat_legacy` | legacy adapter 경유. explicit flag 필수 |
| `diagnostic_legacy` | 비교/검사용 artifact 생성 전용. runtime authority 아님 |

### Required Changes

- explicit mode enum 또는 flag 구현
- `compat_legacy` 없이는 `sentence_plan` 관련 입력 소비 금지
- diagnostic mode는 runtime authority가 아닌 비교/검사용 artifact 생성 모드로 제한
- compat adapter는 `compose_layer3_text.py` 내부에 유지하되 default branch에 직접 붙지 않게 경로 분리
- compat mode에서도 최종 emission은 반드시 `body_plan` section emission을 거친다

### Required Outputs

- explicit mode enum 또는 flag
- compat path 분리 결과
- diagnostic path 분리 결과
- legacy access guard

### Exit Gate

사용자가 의도적으로 legacy mode를 켜지 않는 한 legacy path는 실행되지 않는다.

---

## 12. Phase 7 - Single-writer Invariant Recheck

Branch A 전용 Tier 2 phase다. Branch B/C에서는 실행하지 않는다.

### 목적

default entrypoint를 고정하는 과정에서 writer ownership이 흐려지지 않게 한다.

### Check Matrix

| 항목 | 기대 결과 |
|---|---|
| compose가 유일한 writer인가 | `Yes` |
| validator는 drift/legality checker로만 남는가 | `Yes` |
| quality/publish decision stage가 post-compose single writer인가 | `Yes` |
| Lua bridge와 runtime consumer가 render-only인가 | `Yes` |
| compat adapter가 문장 생성 없이 배치만 하는가 | `Yes` |
| default path에서 `sentence_plan` direct writer invocation이 없는가 | `Yes` |

### Required Outputs

- writer ownership check report
- non-writer consumer boundary check
- adapter behavior check
- default path sentence_plan direct writer invocation check

### Exit Gate

`default authority를 바꿨더니 사실상 writer가 둘이 됐다`는 해석이 나오지 않아야 한다.

---

## 13. Phase 8 - Regression Test & Baseline Integrity Confirmation

Phase 8 범위는 branch별로 다르다.

### Branch A Scope

Branch A에서는 Tier 2 변경 이후 full-runtime rerun과 regression gate를 수행한다.

| 테스트 | 기대 결과 |
|---|---|
| default authority test | 인자 없이 compose 실행 시 `compose_profiles_v2 + body_plan` 확인 |
| no implicit legacy fallback test | legacy 파일이 존재해도 explicit flag 없이는 legacy path 진입 금지 |
| explicit compat test | explicit compat flag가 있을 때만 legacy adapter 경유 허용 |
| diagnostic isolation test | diagnostic mode 산출물이 runtime canonical authority를 대체하지 않음 |
| single-writer invariant test | compose 외 writer 없음, post-compose decision stage shape 불변 |
| determinism test | 동일 입력 2회 실행 시 동일 hash |
| parity preservation test | invariant block의 6종 수치 전부 유지. Tier 2 변경 후 재생성된 staged Lua hash가 `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`와 일치 |

Branch A baseline re-run은 아래를 수행한다.

- current `2105` runtime source 사용
- full-runtime compose를 default entrypoint로 재실행
- regression gate 재확인
- Lua bridge export 재확인
- staged/workspace parity 재확인
- runtime rollout report는 `ready_for_in_game_validation`까지만 해석

### Branch A Failure Path

Phase 8 `parity preservation test`가 fail하면 나머지 Branch A 테스트는 실행하지 않고 즉시 rollback sequence로 진입한다.

1. Tier 2 변경을 rollback한다.
2. `diagnostic/tier2_pre_change_snapshot.json`과 rollback 이후 영향 파일 hash가 일치하는지 검증한다.
3. rollback 이후 Phase 8을 Branch B/C scope(read-only integrity confirmation)로 재실행한다.
4. branch를 `Branch D - tier_2_induced_drift`로 재분류한다.
5. 실패 원인을 `compose_default_path_classification_memo.md` 보충 섹션에 기록한다.
6. Branch D follow-up reservation을 적용한다.

### Branch D Rollback Verification Failure

Rollback 후 `diagnostic/tier2_pre_change_snapshot.json`과 영향 파일 hash가 불일치하면 round close 불가다.

1. 실패 상태를 `diagnostic/rollback_verification_failure_report.json`에 기록한다.
2. 영향 파일 현재 hash를 failure report에 포함한다.
3. Phase 9로 진행하지 않고 round를 `suspended`로 표기한다.
4. 별도 manual recovery round opening이 선행되어야 한다.

### Branch B/C Scope

Branch B/C에서는 canonical artifact 재생성, full-runtime compose rerun, Lua bridge export를 수행하지 않는다.

Branch B/C Phase 8은 read-only integrity confirmation만 수행한다.

- sealed staged Lua hash 불변 확인
- workspace Lua hash 불변 확인
- mtime 불변 확인
- `diagnostic/` 밖 artifact 생성 없음 확인
- top docs 미수정 확인

### Required Outputs

- Branch A: refreshed regression gate report
- Branch A: refreshed Lua bridge report
- Branch A: refreshed parity confirmation
- Branch A: entrypoint authority seal report
- Branch B/C: read-only baseline integrity confirmation
- Branch D: tier2 induced drift failure report
- Branch D: rollback read-only baseline integrity confirmation
- Rollback verification failure: rollback verification failure report

### Exit Gate

- Branch A: `기본 진입점만 바꿨다`는 말이 숫자와 산출물 수준에서도 참이어야 한다.
- Branch B/C: canonical artifact가 재생성되지 않았고 sealed/workspace Lua가 불변이어야 한다.
- Branch D: rollback 이후 pre-change snapshot hash와 영향 파일 hash가 일치하고, read-only integrity confirmation이 pass여야 한다.
- Rollback verification failure: Phase 8은 close되지 않는다. Round는 `suspended_pending_manual_recovery`로 머무르며 manual recovery round opening까지 Phase 9로 진행할 수 없다.

---

## 14. Phase 9 - Closeout Documentation

Phase 9에서만 top docs를 갱신한다. Phase 0에서는 top docs adopted entry를 작성하지 않는다.

### Branch-specific Closeout Wording

| Branch | Required closeout wording |
|---|---|
| A | `implementation-drift verification + authority seal round closed with seal executed` |
| B | `closed without seal - entrypoint implementation drift, entrypoint drift patch + authority seal round reserved` |
| C | `closed without seal - evidence augmentation required, trace widening reserved` |
| D | `closed without seal - tier_2_induced_drift, Tier 2 design revision round reserved` |

Tier 2 design review non-convergence로 Tier 1-only re-scope된 경우에는 아래 문구를 사용한다.

> Tier 1 verification closed, Tier 2 seal withheld due to design review non-convergence.

이 Tier 1-only wording은 위 branch-specific wording을 대체한다.

### DECISIONS.md Required Entries

Branch A에서만 아래 항목을 adopted authority로 기록한다.

- default compose entrypoint는 `compose_profiles_v2 + body_plan`이다.
- legacy `sentence_plan`은 compatibility/diagnostic input으로만 남는다.
- implicit legacy fallback은 금지한다.
- single-writer / post-compose decision stage / render-only runtime consumer 계약은 유지한다.

모든 branch에서 아래 항목은 기록한다.

- CDPCR-AS classification 결과는 `A/B/C` 중 하나이며, Phase 8 induced drift가 발생하면 closeout state는 `D`다.
- Branch B/C/D 또는 design review non-convergence 시 seal은 집행되지 않았다.
- 후속 round 예약 항목은 branch별로 분리한다.

### ARCHITECTURE.md Required Entries

- canonical forward read는 유지
- compat adapter는 존재하지만 default authority가 아님
- default/compat/diagnostic path를 명시적으로 구분
- `CDPCR-AS - diagnostic observer lane closed as <A|B|C|D>` 형식으로 기록
- 기존 `11-53 / 11-55 / 11-56` 자동 재오픈 없음 명시

### ROADMAP.md Required Entries

- Branch A: `implementation-drift verification + authority seal round closed with seal executed`
- Branch B: `closed without seal - entrypoint implementation drift, entrypoint drift patch + authority seal round reserved`
- Branch C: `closed without seal - evidence augmentation required, trace widening reserved`
- Branch D: `closed without seal - tier_2_induced_drift, Tier 2 design revision round reserved`
- Branch A이면 다음 단계는 manual in-game validation QA round 또는 선택적 cleanup round
- Branch B이면 `entrypoint drift patch + authority seal round`
- Branch C이면 `CDPCR trace widening / evidence augmentation round`
- Branch D이면 `Tier 2 design revision round`
- deployed closeout은 여전히 열리지 않음

### Exit Gate

Branch A closeout에서는 다음 문장이 성립해야 한다.

> artifact는 이미 body_plan인데, 이제 기본 compose entrypoint도 정말 body_plan authority로 봉인됐다. 그리고 그것은 증거를 먼저 확인한 다음에 봉인됐다.

Branch B/C/D closeout과 Tier 1-only re-scope closeout에서는 위 문장을 쓰지 않는다. 대신 "seal not executed" 또는 "Tier 2 seal withheld"를 명시한다.

---

## 15. Branch Follow-up Reservation

| Branch | 예약 round | QA round 관계 |
|---|---|---|
| A | `Compose Default Path Cleanup Round` 선택적 예약 | manual in-game validation QA round와 독립 병렬 가능 |
| B | `entrypoint drift patch + authority seal round` | QA round 대기 |
| C | `CDPCR trace widening / evidence augmentation round` | QA round 병렬 가능 |
| D | `Tier 2 design revision round` | QA round 대기 |

네 타입 모두 CDPCR-AS closeout과 동시 개최할 수 없다. closeout 이후 별도 decision으로만 개최한다.

---

## 16. Reference Read Points

CDPCR-AS는 아래 current authority와 정합해야 한다.

- `docs/DECISIONS.md` 2026-04-06 single-writer 봉인 결정 블록
- `docs/DECISIONS.md` 2026-04-20 `sentence_plan` legacy baseline 보존 결정
- `docs/DECISIONS.md` 2026-04-20 compatibility adapter compose-internal non-writer bridge 결정
- `docs/DECISIONS.md` 2026-04-22 Phase D/E staged rollout override round closeout 결정
- `docs/ARCHITECTURE.md` `11-53`
- `docs/ARCHITECTURE.md` `11-55`
- `docs/ARCHITECTURE.md` `11-56`

이 read point들은 CDPCR-AS가 authority 재심 round가 아니라 implementation-drift verification round임을 고정한다.

---

## 17. Artifact Index

### Tier 1 Diagnostic Artifacts

All Tier 1 artifacts must stay under:

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/
```

| Phase | 산출물 |
|---|---|
| 0 | `diagnostic/scope_lock.md` |
| 0 | `diagnostic/tier2_design_adversarial_review.md` |
| 0 | `diagnostic/phase0_opening_seal.json` |
| 1 | `diagnostic/probe_invocation_preflight.json` |
| 2 | `diagnostic/compose_default_path_branch_trace_report.json` |
| 3 | `diagnostic/compose_default_path_parity_probe_report.json` |
| 4 | `diagnostic/compose_default_path_classification_memo.md` |
| 8 Branch B/C | `diagnostic/read_only_baseline_integrity_confirmation.json` |
| 8 Branch D | `diagnostic/read_only_baseline_integrity_confirmation.json` after rollback |
| 8 Branch D | `diagnostic/tier2_induced_drift_failure_report.json` |
| Phase 8 rollback verification failure | `diagnostic/rollback_verification_failure_report.json` |

### Tier 2 Production-scoped Changes

Tier 2 artifacts are not constrained to `diagnostic/` because Branch A explicitly edits the production default entrypoint. Their write surface is limited to default path resolution, explicit mode separation, test/report outputs, and closeout documentation.

| Phase | 산출물 |
|---|---|
| 5 | `diagnostic/tier2_pre_change_snapshot.json` / default profile resolver / default compose dispatch patch / removed fallback list |
| 6 | explicit mode enum or flag / compat path separation / diagnostic path separation / legacy access guard |
| 7 | writer ownership check report / boundary check / adapter behavior check / sentence_plan direct writer check |
| 8 Branch A | refreshed regression gate / Lua bridge report / parity confirmation / entrypoint authority seal report |
| 9 | `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` closeout entries |

---

## 18. Current Read Rule

CDPCR-AS는 `Phase D/E staged rollout override round`를 자동 재오픈하지 않는다. 기존 staged/static closeout과 sealed parity hash는 baseline으로 읽고, 이번 round의 첫 질문은 아래 하나다.

> 현재 default compose path가 이미 채택된 `body_plan` authority를 그대로 집행하는가, 아니면 legacy `sentence_plan` path로 미끄러지는 implementation drift가 남아 있는가?

증거가 Branch A를 지지할 때만 default authority seal을 집행한다. 증거가 Branch B/C이면 seal을 집행하지 않고, entrypoint drift patch + authority seal round 또는 trace widening으로 넘긴다. Branch A 실행 후 Tier 2 patch가 baseline을 깨뜨리면 Branch D로 닫고 Tier 2 design revision으로 넘긴다. Rollback 검증이 실패하면 Phase 9로 진행하지 않고 suspended 상태에서 manual recovery round를 먼저 연다.
