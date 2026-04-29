# Iris DVF 3-3 EDPAS Scope Lock

기준일: `2026-04-23`  
버전: `v0.3`  
상태: scope lock draft; Phase 0 open pending CDPCR-AS Branch B top-doc evidence verification and design review seal  
라운드: `Iris DVF 3-3 Entrypoint Drift Patch & Authority Seal Round`  
약칭: `EDPAS`  
선행 근거: `CDPCR-AS` Branch B closeout

---

## 1. Scope Boundary

이 scope lock은 CDPCR-AS에서 확정된 Branch B만 수리한다.

수리 대상은 direct default compose entrypoint가 아직 legacy `compose_profiles.json`을 여는 implementation drift다.

---

## 2. Required Opening Evidence

Phase 0 open 전 아래 command 결과가 non-empty여야 한다.

```text
rg -n "CDPCR-AS.*Branch B|Branch B.*CDPCR-AS|entrypoint implementation drift" docs/DECISIONS.md docs/ARCHITECTURE.md docs/ROADMAP.md
```

미확인 상태에서는 EDPAS를 열 수 없다.

---

## 3. Sealed Invariants

아래 invariant는 round 전 구간에서 유지한다.

| 항목 | 값 |
|---|---|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish_split | `internal_only 617 / exposed 1467` |
| quality_split | `strong 1316 / adequate 0 / weak 768` |
| sealed_staged_lua_parity_hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

Invariant 위반 시 즉시 quarantine한다.

---

## 4. Allowed Write Surface

### Production Code

아래 파일만 production code write surface로 연다.

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tests/`

아래 파일은 필요성이 명확할 때만 secondary write surface로 연다.

- `Iris/build/description/v2/tools/build/build_layer3_body_plan_v2_preview.py`

### Round-local Diagnostic Lane

아래 경로는 round-local diagnostic artifact 경로다.

```text
Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/
```

### Closeout Docs

아래 top docs는 Phase 4 closeout 때만 갱신한다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

---

## 5. Prohibited Write Surface

이번 round에서 아래 mutation은 금지한다.

- `quality_publish_decision_*.jsonl` canonical rewrite
- `body_plan_structural_reclassification_*.jsonl` canonical rewrite
- `quality_baseline_v4` 수정
- `quality_baseline_v5` cutover
- runtime-side compose/rewrite 추가
- compose 외부 repair stage 추가
- Phase C compatibility adapter 제거 또는 위치 이동
- v2 resolver legacy label -> body profile mapping 제거 (see §7)
- manual in-game validation 결과 선언
- deployed closeout / ready_for_release 선언

---

## 6. Canonical Artifact Rule

Phase 3 parity verification은 diagnostic path에서만 Lua를 생성한다.

Canonical staged/workspace Lua는 Phase 3에서 재생성하지 않는다. Phase 4 authority seal closeout 이후 별도 staged/workspace rollout 단계에서만 canonical Lua를 재생성할 수 있으며, 이 경우에도 최종 hash는 sealed hash와 일치해야 한다.

---

## 7. Legacy Access Boundary

Default mode에서 금지한다.

- legacy `compose_profiles.json` default open
- legacy `sentence_plan` direct writer execution
- legacy file presence 기반 implicit fallback

Explicit mode에서만 허용한다.

- `compat_legacy`
- `diagnostic_legacy`

이 문서에서 `legacy label`은 v2 resolver가 compatibility mapping으로 해석하는 legacy profile 계열 label을 뜻한다. 대표 예시는 기존 `sentence_plan` profile family의 `interaction_tool`, `interaction_component`, `interaction_output` 같은 legacy compose profile identifier다.

v2 resolver 내부의 legacy label -> body profile compatibility mapping은 `sentence_plan` writer가 아니므로 이번 round에서 제거하지 않는다.

---

## 8. Rollback Contract

Phase 1에서 아래를 snapshot한 뒤 production write를 시작한다.

- file presence: `present` / `absent`
- file content hash for present files
- intended new file list

Rollback 시:

- `absent -> present` 신규 파일은 삭제한다.
- `present -> modified` 파일은 snapshot hash 상태로 복원한다.

Rollback target은 Phase 1 snapshot 상태다. Phase 2 내부 incremental change가 있어도 Phase 2/3 failure 시 Phase 1 snapshot으로 완전 복원한다. Phase 2 도중의 부분 rollback은 round 상태를 변경하지 않는 working revision으로 간주하며, snapshot 복원 계약과 별개다.

Rollback verification 실패 시 round는 아래 상태로 멈춘다.

```text
suspended_pending_manual_recovery
```

이 상태는 terminal state다. Manual recovery round가 EDPAS를 대체하며, EDPAS는 자가 closeout하지 않는다.

---

## 9. Design Review Gate

Phase 2 patch 시작 전 아래 artifact가 존재해야 한다.

```text
Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/edpas_tier2_design_adversarial_review.md
```

이 artifact는 아래를 검토한다.

- `compose_profiles_v2.json` 고정 방식
- explicit mode enum 또는 flag surface shape
- implicit legacy source fallback 제거 구현 방식

Conclusion enum은 아래 넷 중 하나다.

- `pass`
- `pass_with_required_impl_guards`
- `fail`
- `needs_redesign`

Conclusion이 `pass` 또는 `pass_with_required_impl_guards`가 아니면 Phase 2를 시작하지 않는다. `pass_with_required_impl_guards`인 경우 각 guard는 stable id를 가져야 하며 Phase 3 `design_review_guard_compliance.md`에서 `applied` / `not_applicable` / `violation` 중 하나로 추적되어야 한다.

Stable id는 Phase 1 pre-change scan 단계에서 각 guard에 부여한다.

---

## 10. Success Gate

아래 gate들은 authority seal closeout 선언의 기술적 전제다. Closeout 시 top docs에 기록할 선언문은 plan §12를 따른다.

아래가 모두 참일 때만 authority seal closeout을 선언한다.

- no-args/default compose entrypoint opens `compose_profiles_v2.json`
- no-args/default compose entrypoint enters `body_plan` writer path
- default mode에서 `sentence_plan` direct writer 미실행
- v2 resolver의 legacy label compatibility mapping을 경유하는 입력도 default mode에서는 `body_plan` writer로 처리됨
- explicit legacy mode 없이는 legacy path 접근 불가
- tests pass
- 모든 design review guard가 `applied` 또는 `not_applicable`로 기록되고 `violation`이 없음
- diagnostic 2105-row Lua hash matches `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
- single-writer / post-compose decision stage / render-only runtime consumer 계약 유지

---

## 11. Current State After Scope Lock Draft

EDPAS plan/scope lock docs exist, but Phase 0 is not closed.

Next step:

```text
Phase 0 - opening verification + design adversarial review
```
