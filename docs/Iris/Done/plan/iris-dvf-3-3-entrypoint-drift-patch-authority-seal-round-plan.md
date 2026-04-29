# Iris DVF 3-3 Entrypoint Drift Patch & Authority Seal Round Plan

기준일: `2026-04-23`  
버전: `v0.3`  
상태: opening plan draft (Phase 0 open은 CDPCR-AS Branch B closeout이 top docs에 기록된 이후에만 가능)  
라운드 이름: `Iris DVF 3-3 Entrypoint Drift Patch & Authority Seal Round`  
약칭: `EDPAS`  
상위 기준: `docs/Philosophy.md` > `docs/DECISIONS.md` > `docs/ARCHITECTURE.md` > `docs/ROADMAP.md`  
선행 근거: `CDPCR-AS` Branch B closeout

---

## 1. Round Identity

이 round는 `CDPCR-AS`에서 확인된 Branch B만 수리하는 **entrypoint implementation drift patch + authority seal round**다.

상위 authority는 이미 닫혀 있다.

- default forward authority: `compose_profiles_v2.json + body_plan`
- legacy `sentence_plan`: compatibility / diagnostic input only
- runtime artifact state: `ready_for_in_game_validation`

이번 round의 질문은 아래 하나다.

> direct default compose entrypoint가 더 이상 legacy `compose_profiles.json` / `sentence_plan` direct writer를 default-open하지 않고, `compose_profiles_v2.json + body_plan` authority를 기본값으로 집행하는가?

---

## 2. Phase 0 Open Preconditions

Phase 0를 열기 전에 아래가 충족되어야 한다.

1. 이 plan의 current version이 존재한다.
2. `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-scope-lock.md`가 이 plan과 같은 current version으로 존재한다.
3. CDPCR-AS Branch B closeout이 top docs에 실제로 기록되어 있다.

검증 command:

```text
rg -n "CDPCR-AS.*Branch B|Branch B.*CDPCR-AS|entrypoint implementation drift" docs/DECISIONS.md docs/ARCHITECTURE.md docs/ROADMAP.md
```

결과가 non-empty가 아니면 EDPAS Phase 0는 열 수 없다.

---

## 3. Scope

### In Scope

- `compose_layer3_text.py` direct default entrypoint patch
- no-args/default mode profile source를 `compose_profiles_v2.json`으로 변경
- default path에서 `body_plan` writer branch 진입 보장
- explicit legacy mode surface 추가 또는 정리
  - `default`
  - `compat_legacy`
  - `diagnostic_legacy`
- explicit legacy mode 없이는 `sentence_plan` direct writer 접근 금지
- pre-change hash + file presence snapshot 및 rollback verification
- default/compat/diagnostic path tests
- 2105-row diagnostic parity probe
- top-doc closeout update

### Out of Scope

- semantic redesign
- `quality_state / publish_state` axis 재정의
- `quality_baseline_v4 -> v5` cutover
- runtime-side compose/rewrite
- compose 외부 repair stage 재도입
- Phase C compatibility adapter 제거 또는 위치 이동
- deployed closeout / ready_for_release 선언
- manual in-game validation QA

### Legacy Mapping Rule

이 문서에서 `legacy label`은 v2 resolver가 compatibility mapping으로 해석하는 legacy profile 계열 label을 뜻한다. 대표 예시는 기존 `sentence_plan` profile family의 `interaction_tool`, `interaction_component`, `interaction_output` 같은 legacy compose profile identifier다.

v2 resolver 내부의 legacy label -> body profile compatibility mapping은 EDPAS Phase 2에서 제거하지 않는다.

이 mapping은 `sentence_plan` direct writer가 아니라 `body_plan` emission을 위한 compatibility classification bridge다. EDPAS의 primary goal은 default entrypoint 집행 drift를 닫는 것이므로, mapping cleanup은 Phase 3 parity 통과 이후 별도 cleanup round에서만 검토한다.

---

## 4. Sealed Invariants

아래 값은 round 전 구간에서 유지해야 한다.

| 항목 | 값 |
|---|---|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish_split | `internal_only 617 / exposed 1467` |
| quality_split | `strong 1316 / adequate 0 / weak 768` |
| sealed_staged_lua_parity_hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

Invariant 위반 산출물은 quarantine한다. Closeout은 불가하다.

---

## 5. Artifact Lane

Round-local diagnostic artifacts는 아래 경로에 둔다.

```text
Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/
```

Production code patch는 아래 write surface로 제한한다.

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tests/`
- 필요한 경우 `Iris/build/description/v2/tools/build/build_layer3_body_plan_v2_preview.py`

Top docs는 closeout phase에서만 갱신한다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

---

## 6. Phase Order

```text
Phase 0  opening verification + design adversarial review
Phase 1  pre-change snapshot + surface scan
Phase 2  entrypoint patch
Phase 3  regression and diagnostic parity verification
Phase 4  authority seal closeout
```

Failure path:

```text
patch implementation failure -> rollback -> closed_without_seal_patch_implementation_failed
test regression -> rollback -> closed_without_seal_test_regression
design review guard violation -> rollback -> closed_without_seal_design_guard_violation
parity breach -> rollback -> closed_without_seal_parity_breach
rollback verification failure -> suspended_pending_manual_recovery
```

---

## 7. Phase 0 - Opening Verification + Design Review

### Purpose

EDPAS가 CDPCR-AS Branch B closeout 없이 독립적으로 열리지 않게 하고, production entrypoint patch 설계를 code edit 전에 검토한다.

### Input Preconditions

- EDPAS plan v0.3
- EDPAS scope lock v0.3
- CDPCR-AS Branch B top-doc closeout evidence

### Required Outputs

- `diagnostic/scope_lock_reflection.md`
- `diagnostic/edpas_tier2_design_adversarial_review.md`
- `diagnostic/phase0_opening_seal.json`

### Design Review Targets

`diagnostic/edpas_tier2_design_adversarial_review.md`는 아래 세 항목을 다룬다.

- `compose_profiles_v2.json` 고정 방식
- explicit mode enum 또는 flag surface shape
- implicit legacy source fallback 제거 구현 방식

### Gate

- CDPCR-AS Branch B top-doc evidence command 결과가 non-empty
- scope lock reflection 완료
- design adversarial review 결론 기록 완료
- design review conclusion enum은 `pass`, `pass_with_required_impl_guards`, `fail`, `needs_redesign` 중 하나
- design review conclusion이 `pass` 또는 `pass_with_required_impl_guards`
- design review conclusion이 `fail` 또는 `needs_redesign`이면 Phase 0 close 불가. Plan 재설계 또는 scope 축소 없이는 Phase 1로 진행하지 않는다.
- 이 gate 전에는 Phase 2 patch를 시작할 수 없음

---

## 8. Phase 1 - Pre-change Snapshot + Surface Scan

### Required Steps

- 영향 파일 hash와 파일 존재 여부를 snapshot한다.
- current direct default entrypoint가 여는 profile path를 기록한다.
- explicit legacy mode 설계 surface를 확정한다.
- default mode에서 금지할 legacy access를 목록화한다.
- design review에서 나온 implementation guard를 patch checklist로 변환한다.
- design review guard마다 stable id를 부여한다.
- Phase 2에서 생성할 intended new file list를 기록한다.

Snapshot은 file content hash뿐 아니라 파일 존재 여부(`present` / `absent`)를 함께 기록한다.

Rollback 시:

- `absent -> present`로 전이된 파일은 삭제한다.
- `present -> modified`로 전이된 파일은 snapshot hash 상태로 복원한다.

### Required Outputs

- `diagnostic/pre_change_snapshot.json`
- `diagnostic/entrypoint_surface_scan.json`
- `diagnostic/legacy_access_guard_plan.md`

### Gate

- rollback에 필요한 파일 hash와 file presence가 모두 기록됨
- intended new file list가 기록됨
- default/compat/diagnostic mode behavior가 patch 전에 문서화됨
- design review guard가 patch checklist에 반영됨

---

## 9. Phase 2 - Entrypoint Patch

### Precondition

Phase 2는 아래 조건이 모두 충족되어야 시작할 수 있다.

- Phase 0 design review gate pass
- Phase 1 pre-change snapshot 존재
- Phase 1 rollback file presence 기록 존재
- Phase 1 intended new file list 존재

### Required Changes

- direct default entrypoint의 default profile source를 `compose_profiles_v2.json`으로 변경한다.
- default mode는 `body_plan` writer path로만 진입한다.
- legacy `sentence_plan` direct writer는 explicit legacy mode에서만 접근 가능해야 한다.
- v2 resolver 내부 legacy label -> body profile compatibility mapping은 제거하지 않는다.
- CLI 또는 mode enum은 아래 behavior를 만족해야 한다.

| Mode | Behavior |
|---|---|
| `default` | `compose_profiles_v2.json + body_plan` |
| `compat_legacy` | explicit legacy compatibility path |
| `diagnostic_legacy` | comparison/inspection only, runtime authority 아님 |

### Guard

Default mode에서 `sentence_plan` direct writer가 실행되면 patch failure다.

### Required Outputs

- patched `compose_layer3_text.py`
- updated or added tests
- `diagnostic/removed_or_guarded_legacy_fallbacks.md`

---

## 10. Phase 3 - Regression and Diagnostic Parity Verification

### Canonical Artifact Rule

Phase 3 parity verification은 `diagnostic/` 경로에 diagnostic Lua를 생성하고 sealed hash와 대조한다.

Canonical staged/workspace Lua는 Phase 3에서 재생성하지 않는다. Phase 4 authority seal closeout 이후 별도 staged/workspace rollout 단계에서만 canonical Lua를 재생성할 수 있으며, 이 경우에도 최종 hash는 sealed hash와 일치해야 한다.

### Required Tests

1. no-args/default entrypoint opens `compose_profiles_v2.json`
2. no-args/default entrypoint enters `body_plan` writer path
3. default mode does not execute `sentence_plan` direct writer
4. v2 resolver의 legacy label compatibility mapping을 경유하는 입력이 default mode로 들어와도 `sentence_plan` direct writer 미실행 + `body_plan` writer 실행이 확인됨
5. explicit `compat_legacy` allows legacy path only when requested
6. diagnostic legacy mode cannot become runtime authority
7. unit tests pass
8. 2105-row diagnostic body_plan Lua hash matches sealed hash
9. staged/workspace Lua parity remains `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
10. single-writer and render-only consumer boundary remains unchanged

Parity preservation test fail 시 나머지 테스트는 실행하지 않고 즉시 Rollback Contract를 실행한다.

### Required Outputs

- `diagnostic/default_entrypoint_authority_report.json`
- `diagnostic/compat_legacy_guard_report.json`
- `diagnostic/entrypoint_parity_probe_report.json`
- `diagnostic/design_review_guard_compliance.md`
- `diagnostic/single_writer_boundary_report.md`
- test command output summary in closeout notes

### Gate

- all required tests pass
- sealed hash preserved
- no implicit legacy fallback in default mode
- explicit legacy path cannot be entered accidentally
- 모든 design review guard가 `applied` 또는 `not_applicable`로 기록되고 `violation`이 없음
- Phase 3 실패 시 rollback 후 pre-change snapshot hash와 영향 파일 hash 일치 확인

---

## 11. Rollback Contract

Patch/test/design review guard/parity failure 시 rollback을 수행한다.

Rollback target은 Phase 1 snapshot 상태다. Phase 2 내부 incremental change가 있어도 Phase 2/3 failure 시 Phase 1 snapshot으로 완전 복원한다. Phase 2 도중의 부분 rollback은 round 상태를 변경하지 않는 working revision으로 간주하며, snapshot 복원 계약과 별개다.

Rollback verification은 아래를 확인한다.

- 모든 `present -> modified` 파일이 snapshot hash로 복원됨
- 모든 `absent -> present` 신규 파일이 삭제됨
- Phase 1 intended new file list에 없던 신규 production/test 파일이 남아 있지 않음
- diagnostic failure report가 생성됨

Rollback verification 실패 시 Phase 4로 진행하지 않는다.

Final state:

```text
suspended_pending_manual_recovery
```

이 상태는 terminal state다. Manual recovery round가 EDPAS를 대체하며, EDPAS는 자가 closeout하지 않는다.

---

## 12. Phase 4 - Authority Seal Closeout

### Success Closeout

If Phase 3 passes, close this round as:

```text
closed_with_authority_seal_executed
```

Top docs must record:

- default compose entrypoint is `compose_profiles_v2.json + body_plan`
- legacy `sentence_plan` is compatibility/diagnostic input only
- implicit legacy source fallback is prohibited
- v2 resolver legacy label compatibility mapping, if retained, is not default authority and does not execute `sentence_plan`
- single-writer / post-compose decision stage / render-only consumer contracts are unchanged
- CDPCR-AS Branch B follow-up is closed by EDPAS
- deployed closeout remains pending manual in-game validation QA

### Failure Closeout

If rollback succeeds, closeout state must use one of:

- `closed_without_seal_patch_implementation_failed`
- `closed_without_seal_test_regression`
- `closed_without_seal_design_guard_violation`
- `closed_without_seal_parity_breach`

Closeout memo must include a `failure_category` field matching one of the above.

If rollback verification fails, do not run Phase 4. Mark:

```text
suspended_pending_manual_recovery
```

---

## 13. Reference Read Points

- `docs/DECISIONS.md` 2026-04-23 CDPCR-AS Branch B closeout
- `docs/ARCHITECTURE.md` CDPCR-AS Branch B closeout section
- `docs/ROADMAP.md` CDPCR-AS Branch B closeout addendum
- `docs/Iris/iris-dvf-3-3-compose-default-path-classification-authority-seal-round-plan.md`
- `Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/compose_default_path_classification_memo.md`

The CDPCR-AS closeout markdown file may be used as supplementary traceability evidence, but EDPAS does not require that file name as canonical authority.

---

## 14. One-line Gate

Closeout must make this sentence true:

> 기본 compose entrypoint는 이제 `compose_profiles_v2.json + body_plan` authority를 직접 집행하며, legacy `sentence_plan`은 explicit compatibility/diagnostic mode가 아니면 열리지 않는다.
