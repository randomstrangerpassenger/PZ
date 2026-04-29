# Iris DVF 3-3 Entrypoint Authority Seal Session Walkthrough

기준일: 2026-04-23  
대상 작업: `CDPCR-AS Branch B closeout` + `EDPAS authority seal closeout`  
상태: entrypoint authority seal 완료, deployed closeout은 별도 QA round pending

---

## 0. 문서 목적

이 문서는 이번 세션에서 실제로 무엇을 판단했고, 무엇을 수정했으며, 어떤 산출물로 검증했는지 복원하기 위한 walkthrough다.

이 문서는 새 gate나 decision source가 아니다. Canonical 상태는 계속 아래 top docs가 가진다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

이 문서는 이후 세션에서 다음 질문에 빠르게 답하기 위한 작업 로그다.

> shipped body_plan artifact authority와 direct default compose entrypoint authority의 불일치가 실제로 닫혔는가?

현재 답은 **닫혔다**다. 단, deployed/in-game validation은 아직 별도 QA round다.

---

## 1. 시작 상태

세션 시작 시점의 핵심 상태는 아래와 같았다.

| 축 | 상태 |
|---|---|
| shipped/staged artifact | `body_plan` 기반 2105-row Lua artifact 생성 및 parity hash 확인 완료 |
| static runtime state | `ready_for_in_game_validation` |
| sealed hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| 남은 의심점 | direct default `compose_layer3_text.py` entrypoint가 아직 legacy `compose_profiles.json` / `sentence_plan`을 default-open할 수 있음 |

즉 runtime에 ship된 artifact는 이미 body_plan 기반이었지만, compose 기본 진입점의 authority가 같은 body_plan source로 봉인되어 있는지는 별도 확인이 필요했다.

세션 전 구간의 sealed invariant는 아래 6종으로 읽었다.

| 축 | 값 |
|---|---|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish_split | `internal_only 617 / exposed 1467` |
| quality_split | `strong 1316 / adequate 0 / weak 768` |
| sealed_staged_lua_parity_hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

---

## 2. CDPCR-AS 계획 정리와 실행

먼저 사용자가 제공한 CDPCR-AS roadmap/review feedback을 바탕으로 계획 문서를 정리했다.

Plan document:

- `docs/Iris/iris-dvf-3-3-compose-default-path-classification-authority-seal-round-plan.md`

최종 계획 버전은 `v1.4`로 정리했다. 주요 보강은 아래였다.

- Branch 판정 primary signal을 `legacy_default_open`으로 고정
- `gating_coverage_status`와 `context_coverage_status` 분리
- Branch D와 rollback verification failure terminal state 추가
- Tier 1-only re-scope와 suspended state transition 정리
- Phase 8 Branch B/C는 canonical artifact 재생성 없이 read-only integrity confirmation만 수행하도록 제한

---

## 3. CDPCR-AS Phase 0-1

CDPCR-AS Phase 0에서는 round-local opening seal을 diagnostic lane에 만들었다.

Diagnostic root:

```text
Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/
```

작성한 Phase 0/1 artifacts:

- `scope_lock.md`
- `tier2_design_adversarial_review.md`
- `phase0_opening_seal.json`
- `probe_invocation_preflight.json`

Phase 1 probe 결과:

| 항목 | 결과 |
|---|---|
| method | `i` existing preview wrapper / CLI options |
| original file mutation | 없음 |
| Phase 3 skip 필요 여부 | false |

---

## 4. CDPCR-AS Phase 2-4 결과

Phase 2 branch trace에서 네 invocation class를 분리했다.

| Class | Role | legacy_default_open | 결과 |
|---|---|---:|---|
| `build_script` | gating | false | staged generation lane은 body_plan source |
| `cli_direct` | gating | true | direct default entrypoint가 legacy `compose_profiles.json` open |
| `test_harness` | context-only | false | body_plan test path 존재 |
| `preview_wrapper` | context-only | false | wrapper default는 `compose_profiles_v2.json` |

핵심 산출물:

- `compose_default_path_branch_trace_report.json`
- `compose_default_path_parity_probe_report.json`
- `compose_default_path_classification_memo.md`

Phase 3 parity probe에서는 diagnostic body_plan Lua가 sealed staged Lua hash와 일치했다.

```text
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
```

그러나 Phase 2에서 `cli_direct.legacy_default_open = true`가 확인되었으므로 CDPCR-AS는 Branch B로 분류했다.

Closeout:

- `cdpcr_as_closeout_branch_b.md`
- `baseline_integrity_confirmation_branch_b.json`

Top docs 반영:

- `DECISIONS.md`: CDPCR-AS Branch B closeout
- `ARCHITECTURE.md`: 11-57
- `ROADMAP.md`: Addendum #23

중요한 해석:

> CDPCR-AS는 evidence round로 닫혔다. Seal은 실행하지 않았고, 후속 `entrypoint drift patch + authority seal round`를 예약했다.

---

## 5. EDPAS 계획과 Scope Lock

CDPCR-AS Branch B 후속으로 EDPAS를 열었다.

Plan/scope documents:

- `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-plan.md`
- `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-scope-lock.md`

초안 v0.1 이후 review feedback을 반영해 `v0.3`까지 정리했다.

주요 보강:

- CDPCR-AS Branch B top-doc closeout 실존 검증 gate
- Tier 2 design adversarial review gate
- `pass_with_required_impl_guards` guard compliance tracking
- `legacy label` scope 정의
- Phase 1 snapshot을 rollback target으로 고정
- file presence와 intended new file list 기록
- `closed_without_seal_design_guard_violation` failure category 추가

---

## 6. EDPAS Phase 0-1

EDPAS diagnostic root:

```text
Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/
```

Phase 0 artifacts:

- `scope_lock_reflection.md`
- `edpas_tier2_design_adversarial_review.md`
- `phase0_opening_seal.json`

Design review conclusion:

```text
pass_with_required_impl_guards
```

Guard IDs:

- `EDPAS-G1`: default direct entrypoint opens `compose_profiles_v2.json`
- `EDPAS-G2`: default mode rejects non-v2 profile files
- `EDPAS-G3`: legacy source opens only through explicit legacy modes
- `EDPAS-G4`: default mode cannot call `compose_item_legacy`
- `EDPAS-G5`: v2 legacy label mapping remains body_plan-only
- `EDPAS-G6`: diagnostic legacy cannot write canonical authority artifacts

Phase 1 artifacts:

- `pre_change_snapshot.json`
- `entrypoint_surface_scan.json`
- `legacy_access_guard_plan.md`

Snapshot recorded:

- `compose_layer3_text.py`
- `test_compose_layer3_text_v2.py`
- `build_layer3_body_plan_v2_preview.py`
- intended new file list: none

---

## 7. EDPAS Code Patch

Primary changed production file:

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`

Test file updated:

- `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`

Patch summary:

- Added argparse CLI surface.
- Added explicit modes:
  - `default`
  - `compat_legacy`
  - `diagnostic_legacy`
- Added constants:
  - `LEGACY_PROFILES_PATH`
  - `BODY_PLAN_PROFILES_PATH`
  - `EDPAS_DIAGNOSTIC_DIR`
- Added `default_entrypoint_paths(...)`.
- Added `resolve_entrypoint_paths(...)`.
- Added `enforce_entrypoint_mode_contract(...)`.
- Changed `main(...)` to resolve mode, enforce contract, then call `build_rendered(...)`.

Current default behavior:

```text
mode = default
profiles_path = Iris/build/description/v2/data/compose_profiles_v2.json
```

Legacy direct writer access is explicit-only:

```text
--mode compat_legacy
--mode diagnostic_legacy
```

Default mode rejects legacy profile sources before legacy dispatch.

---

## 8. EDPAS Test Coverage

Existing body_plan tests remained passing. Added/verified tests include:

- default entrypoint resolves `compose_profiles_v2.json`
- default entrypoint rejects legacy profiles
- default entrypoint handles v2 legacy label compatibility mapping through body_plan writer
- `diagnostic_legacy` rejects canonical output path

Test results:

| Command | Result |
|---|---|
| `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` | `299` pass |
| `python -B -m unittest Iris.build.description.v2.tests.test_compose_layer3_text_v2` | `7` pass |

Both runs completed with `failures = 0` and `errors = 0`.

---

## 9. EDPAS Parity Verification

Patched direct default entrypoint was run against the 2105-row source in default mode with diagnostic output path overrides into the EDPAS diagnostic lane.

Generated diagnostic artifacts:

- `diagnostic_default_entrypoint_rendered.2105.json`
- `diagnostic_default_entrypoint_style_log.2105.jsonl`
- `diagnostic_default_entrypoint_IrisLayer3Data.body_plan_v2.2105.lua`
- `diagnostic_default_entrypoint_lua_bridge_report.2105.json`

Hash comparison:

| Artifact | SHA-256 |
|---|---|
| diagnostic Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| sealed staged Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| workspace Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

Canonical staged/workspace Lua artifacts were not regenerated during Phase 3.

---

## 10. EDPAS Reports and Closeout

Phase 2/3 reports:

- `removed_or_guarded_legacy_fallbacks.md`
- `default_entrypoint_authority_report.json`
- `compat_legacy_guard_report.json`
- `entrypoint_parity_probe_report.json`
- `design_review_guard_compliance.md`
- `single_writer_boundary_report.md`

Closeout:

- `Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/edpas_closeout.md`

Closeout state:

```text
closed_with_authority_seal_executed
```

Design review guard violations:

```text
0
```

---

## 11. Top-doc Updates

Top docs were updated in two waves.

### First wave: CDPCR-AS Branch B

- `DECISIONS.md`: CDPCR-AS Branch B, seal not executed, EDPAS reserved
- `ARCHITECTURE.md`: 11-57, diagnostic observer lane closed as Branch B
- `ROADMAP.md`: Addendum #23

### Second wave: EDPAS authority seal

- `DECISIONS.md`: EDPAS closed with authority seal executed
- `ARCHITECTURE.md`: 11-58, direct default entrypoint sealed to body_plan authority
- `ROADMAP.md`: Addendum #24

### Final current-read clarification

After checking the user's "problem 1" wording, top docs were further clarified:

- `DECISIONS.md`: the compose entrypoint vs shipped body_plan authority mismatch is solved as of EDPAS
- `ARCHITECTURE.md`: 11-57 is historical drift evidence; 11-58 is current architecture
- `ROADMAP.md`: CDPCR-AS follow-up was opened and closed by EDPAS; problem 1 is solved

---

## 12. Current State

Current read:

| Problem | Current status |
|---|---|
| shipped body_plan artifact vs direct default compose entrypoint mismatch | solved by EDPAS |
| default compose entrypoint source | `compose_profiles_v2.json + body_plan` |
| legacy `sentence_plan` path | explicit `compat_legacy` / `diagnostic_legacy` only |
| sealed Lua parity | preserved |
| 6 sealed invariants | preserved |
| in-game/deployed validation | still pending separate QA round |

The important interpretation is:

> CDPCR-AS found the drift. EDPAS fixed and sealed it. The remaining work is not this entrypoint mismatch; it is deployed/manual validation or optional cleanup.

Cleanup note: the production code now contains `EDPAS_DIAGNOSTIC_DIR` to constrain `diagnostic_legacy` output. This is acceptable for this round's guard, but a future cleanup round may rename it to a semantic diagnostic output constant if desired.

---

## 13. Remaining Work Deferred to Separate Rounds

Not part of this session's closeout:

- manual in-game validation QA round
- optional v2 resolver legacy label compatibility mapping cleanup round
- deployed closeout / ready_for_release declaration
- `quality_baseline_v4 -> v5` cutover

These require separate opening decisions.
