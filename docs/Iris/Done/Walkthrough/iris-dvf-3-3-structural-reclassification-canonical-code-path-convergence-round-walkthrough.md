# Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round Walkthrough

기준일: 2026-04-24  
대상 라운드: `Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round`  
상태: default observer code-path convergence closeout 완료, current runtime state는 계속 `ready_for_in_game_validation`

---

## 0. 문서 목적

이 문서는 이번 세션에서 structural reclassification default observer path를 어떻게 dual-axis canonical model로 수렴시켰고, 어떤 산출물과 검증으로 닫았는지 복원하기 위한 walkthrough다.

이 문서는 새 gate나 새 decision source가 아니다. Canonical 상태는 계속 아래 top docs가 가진다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

이 문서가 답하려는 질문은 아래 하나다.

> legacy structural reclassification default path가 더 이상 single-slot lossy observer view를 current authority로 쓰지 않고, source axis와 section axis를 물리적으로 분리한 dual-axis canonical artifact set을 default로 emit하는가?

현재 답은 **그렇다**다.

---

## 1. 세션 시작 상태

세션 시작 시점의 핵심 상태는 아래와 같았다.

| 축 | 상태 |
|---|---|
| `2026-04-22` staged/static closeout | 이미 닫힘, current state `ready_for_in_game_validation` |
| `2026-04-23` EDPAS | direct default entrypoint authority seal 완료 |
| `2026-04-24` additive signal preservation round | `body_plan_signal_preservation.*` lane으로 closeout 완료 |
| remaining divergence | default structural reclassification artifact는 여전히 old single-slot summary shape |
| core risk | source axis와 section axis가 물리적으로 다른 슬롯으로 분리되지 않고, single-slot lossy observer view가 default 해석으로 남음 |
| hard sealed Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| baseline row count | `2105` |

즉 이번 round의 문제는 runtime writer를 다시 여는 일이 아니었다. additive lane에서 이미 닫은 dual-axis canonical read contract를 default structural code path와 plain-name artifact topology로 수렴시키는 일이었다.

---

## 2. Planning Authority 정리

먼저 사용자가 제공한 최종 통합 로드맵을 기반으로 계획 문서를 만들었다.

계획 문서:

- `docs/Iris/iris-dvf-3-3-structural-reclassification-canonical-code-path-convergence-round-final-integrated-plan.md`

초기 계획은 review feedback을 거쳐 `v0.3`으로 정리됐다. 주요 보정은 아래였다.

| 검토 축 | 최종 처리 |
|---|---|
| `signal_preservation` disposition | `regenerate + supersession`으로 명시 |
| additive lane 위치 | adopted traceability baseline으로 유지 |
| current default-path authority | plain-name structural reclassification canonical artifact set으로 이동 |
| exact-match gate | source / section / overlap 모두 exact match required |
| exception table | `empty and non-operational for this round` |
| handoff semantics | `closed_with_distribution_handoff_to_next_round`로 pass closeout과 분리 |
| `.summary.json` compatibility | stable summary subset + `legacy_compat_summary` |
| field naming provenance | `body_plan_signal_preservation.2105.jsonl` naming 승계 |
| Tier classification | `Tier 2`, but not `scope_policy_override_round` |

이 planning phase에서 가장 중요한 결정은 아래였다.

> `body_plan_signal_preservation.*`를 parallel canonical로 추가하지 않고, default structural path 자체를 dual-axis canonical path로 수렴시킨다.

---

## 3. Formal Phase 0-3 산출물

로드맵이 요구한 formal 산출물을 round staging root에 생성했다.

Staging root:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/
```

Phase 0 opening:

| 산출물 | 역할 |
|---|---|
| `phase0_opening/scope_lock.md` | branch, scope, supersession frame 봉인 |
| `phase0_opening/baseline_freeze.json` | hard invariant, legacy hash, reference counts 기록 |
| `phase0_opening/non_writer_boundary.md` | forbidden writer surface와 allowed observer output 정리 |
| `phase0_opening/tier_classification_memo.md` | Tier 2 / non-scope-policy-override 분류 |
| `phase0_opening/structural_reclassification_code_path_convergence_tier2_design_adversarial_review.md` | Tier 2 design review와 required guards |

Phase 1 snapshot:

| 산출물 | 역할 |
|---|---|
| `phase1_snapshot/pre_change_snapshot.json` | legacy artifact hash, lossy distribution, additive field naming verification |
| `phase1_snapshot/legacy_read_model_scan.md` | old single-slot read model defect evidence |
| `phase1_snapshot/entrypoint_surface_scan.json` | entrypoint/build/test surface scan |
| `phase1_snapshot/legacy_access_guard_plan.md` | default vs explicit legacy access policy |

Walkthrough-level consumer scan summary:

| Plan §3-3 category | Walkthrough evidence |
|---|---|
| build/validation scripts | `entrypoint_surface_scan.json`의 `build_script 4`, `wrapper 1` |
| wrapper/default script | `cli_direct 1`, all resolved to canonical script |
| test harness | `test_harness 2` |
| staging report generator | Phase 5 support scripts emit `entrypoint_surface_guard`, `hash_guard`, `crosscheck`, `diagnostic_packet` |
| `*.summary.json` consumer | `validate_body_plan_full_runtime_regression_gate.py` updated for nested `legacy_compat_summary` with old top-level fallback |
| legacy summary key dependency | stable summary subset and `legacy_compat_summary` documented in `legacy_access_guard_plan.md` and validated in Phase 5 |

Phase 2 contract:

| 산출물 | 역할 |
|---|---|
| `phase2_contract/canonical_read_contract.md` | dual-axis canonical read contract |
| `phase2_contract/source_axis_contract.md` | source axis authority and output fields |
| `phase2_contract/section_axis_contract.md` | section axis derivation and namespace |
| `phase2_contract/overlap_semantics.md` | `signal_overlap_state` value space |
| `phase2_contract/pre_approved_exception_table.md` | empty and non-operational exception structure |

Phase 3 patch notes:

| 산출물 | 역할 |
|---|---|
| `phase3_patch/legacy_mode_notes.md` | explicit legacy diagnostic path notes |
| `phase3_patch/default_vs_legacy_read_matrix.md` | default canonical vs diagnostic legacy matrix |

---

## 4. 구현 범위

이번 세션에서 핵심 production path를 바꿨다.

Primary implementation:

- `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`

이 script는 이제 default 실행에서 dual-axis canonical artifact set을 emit한다. legacy single-slot view는 삭제하지 않고 explicit diagnostic flag로 격리했다.

Supporting validation/report scripts:

- `Iris/build/description/v2/tools/build/build_structural_reclassification_entrypoint_surface_scan.py`
- `Iris/build/description/v2/tools/build/build_structural_reclassification_entrypoint_surface_guard.py`
- `Iris/build/description/v2/tools/build/build_structural_reclassification_artifact_hash_guard.py`
- `Iris/build/description/v2/tools/build/validate_structural_reclassification_convergence.py`
- `Iris/build/description/v2/tools/build/build_structural_reclassification_convergence_crosscheck.py`
- `Iris/build/description/v2/tools/build/build_structural_reclassification_diagnostic_packet.py`

Updated consumer:

- `Iris/build/description/v2/tools/build/validate_body_plan_full_runtime_regression_gate.py`

이 consumer는 canonical summary의 nested `legacy_compat_summary.legacy_family_reclassification_counts`를 읽을 수 있게 보강했다. old top-level key fallback도 유지했다.

Tests:

- `Iris/build/description/v2/tests/test_body_plan_phase_d_e.py`
- `Iris/build/description/v2/tests/test_structural_reclassification_code_path_convergence_supporting_reports.py`
- `Iris/build/description/v2/tests/test_structural_reclassification_entrypoint_surface_scan.py`

---

## 5. Core Code-Path Convergence

### 5-1. Default path

`report_layer3_body_plan_structural_reclassification.py`의 default behavior는 아래처럼 바뀌었다.

| 항목 | current behavior |
|---|---|
| read model | `dual_axis_canonical` |
| row output | `phase4_artifacts/body_plan_structural_reclassification.2105.jsonl` |
| summary output | `phase4_artifacts/body_plan_structural_reclassification.2105.summary.json` |
| writer role | `observer_only` |
| source fields | `source_signal_primary`, `source_signal_secondary`, `source_signal_origin`, `source_signal_present` |
| section fields | `section_signal_primary`, `section_signal_secondary`, `section_signal_origin`, `section_signal_present` |
| overlap field | `signal_overlap_state` |

### 5-2. Legacy path

Legacy single-slot read는 explicit-only diagnostic path로 격리했다.

| 항목 | current behavior |
|---|---|
| invocation | `--emit-legacy-view` |
| row output | `diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.2105.jsonl` |
| summary output | `diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.summary.json` |
| authority status | current default authority 아님 |

### 5-3. Summary compatibility

plain-name `.summary.json`은 current authority summary가 됐다. 동시에 기존 consumer breakage를 줄이기 위해 stable subset을 유지한다.

Required anchors:

- `current_read_model = dual_axis_canonical`
- `summary_schema_version = body-plan-structural-reclassification-summary-stable-v1`
- `linked_artifacts`
- `legacy_compat_summary`

`legacy_compat_summary`는 current authority key가 아니라 diagnostic/compat subsection이다.

### 5-4. Code-level non-writer guard

Plan §5-4 / §7-1 완료 조건 7의 code-level proof는 아래 조합으로 닫았다.

| guard path | proof |
|---|---|
| explicit writer role tag | `report_layer3_body_plan_structural_reclassification.py`가 canonical rows와 summary에 `writer_role = observer_only`를 기록한다 |
| script-level forbidden field list | 같은 script의 `FORBIDDEN_WRITER_FIELDS`가 `quality_state`, `publish_state`, `text_ko`, `rendered_text`, `quality_publish_decision_preview`를 금지 field로 검사한다 |
| round-level convergence validator | `validate_structural_reclassification_convergence.py`가 `quality_baseline_v4`까지 포함해 forbidden writer fields를 다시 검사하고 `observer_only_contract_preserved`, `forbidden_writer_fields_absent`, `artifact_validation_report_pass`를 hard guard로 둔다 |
| focused test coverage | `test_body_plan_phase_d_e`가 default canonical artifact validation pass를 확인하고, `test_structural_reclassification_code_path_convergence_supporting_reports`가 convergence validator pass와 closeout state를 확인한다 |

Artifact-level proof는 §6의 `writer_role_observer_only`와 `forbidden_writer_fields_absent` pass, round-level proof는 §7의 `convergence_validation_report.json = pass`로 이어진다.

---

## 6. Canonical Artifact Regeneration

Default execution으로 canonical artifact set을 생성했다.

Canonical artifacts:

| 산출물 | 역할 |
|---|---|
| `phase4_artifacts/body_plan_structural_reclassification.2105.jsonl` | current default row artifact |
| `phase4_artifacts/body_plan_structural_reclassification.2105.summary.json` | current default summary |
| `phase4_artifacts/body_plan_structural_reclassification.source_distribution.json` | source distribution |
| `phase4_artifacts/body_plan_structural_reclassification.section_distribution.json` | section distribution |
| `phase4_artifacts/body_plan_structural_reclassification.overlap_distribution.json` | overlap distribution |
| `phase4_artifacts/body_plan_structural_reclassification.crosswalk.json` | old/new crosswalk and no-overwrite checks |
| `phase4_artifacts/body_plan_structural_reclassification.artifact_validation_report.json` | artifact-level self-validation |

Diagnostic legacy artifacts:

| 산출물 | 역할 |
|---|---|
| `diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.2105.jsonl` | explicit legacy row view |
| `diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.summary.json` | explicit legacy summary |

Artifact-level self-validation result:

| check | result |
|---|---|
| `writer_role_observer_only` | `pass` |
| `canonical_rows_expose_dual_axis_fields` | `pass` |
| `forbidden_writer_fields_absent` | `pass` |
| `source_summary_internally_consistent` | `pass` |
| `section_summary_internally_consistent` | `pass` |
| `overlap_summary_internally_consistent` | `pass` |
| `crosswalk_totals_consistent` | `pass` |
| `summary_pointer_integrity` | `pass` |

---

## 7. Validation Gate

Round-level validation artifacts:

| 산출물 | result |
|---|---|
| `phase5_validation/entrypoint_surface_guard_report.json` | `pass` |
| `phase5_validation/artifact_hash_guard_report.json` | `pass` |
| `phase5_validation/convergence_crosscheck_report.json` | `match` |
| `phase5_validation/convergence_validation_report.json` | `pass` |
| `phase5_validation/diagnostic_packet.json` | `pass` |

Exact-match targets:

| axis | expected | observed | result |
|---|---:|---:|---|
| source `BODY_LACKS_ITEM_SPECIFIC_USE` | `617` | `617` | `match` |
| source `FUNCTION_NARROW` | `7` | `7` | `match` |
| source `none` | `1481` | `1481` | `match` |
| section `SECTION_FUNCTION_NARROW` | `1433` | `1433` | `match` |
| section `none` | `672` | `672` | `match` |
| overlap `source_only` | `67` | `67` | `match` |
| overlap `section_only` | `876` | `876` | `match` |
| overlap `coexist` | `557` | `557` | `match` |
| overlap `dual_none` | `605` | `605` | `match` |

Legacy-vs-canonical crosscheck:

| metric | value |
|---|---:|
| `lossy_old_artifact_row_count` | `1500` |
| `overwrite_resolution_count` | `557` |
| `section_only_newly_visible_count` | `876` |
| `would_have_overwritten_count` | `0` |
| `IDENTITY_ONLY` replacement count | `0` |
| `ACQ_DOMINANT` replacement count | `0` |

Entrypoint surface guard:

| metric | value |
|---|---:|
| surface count | `8` |
| all surfaces resolve to canonical script | `pass` |
| all surfaces use dual-axis read model | `pass` |
| implicit legacy fallback count | `0` |

Surface breakdown:

| surface kind | count | role |
|---|---:|---|
| `cli_direct` | `1` | direct default script entrypoint |
| `build_script` | `4` | supporting report generators |
| `wrapper` | `1` | round-level convergence validator |
| `test_harness` | `2` | focused regression tests |

Runtime/hash guard:

| check | value |
|---|---|
| staged Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| workspace Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| runtime status | `ready_for_in_game_validation` |

---

## 8. Tests Run

이번 세션에서 아래 unittest 축을 실행했고 모두 통과했다.

```text
python -B -m unittest Iris.build.description.v2.tests.test_body_plan_phase_d_e
python -B -m unittest Iris.build.description.v2.tests.test_report_layer3_body_plan_signal_preservation
python -B -m unittest Iris.build.description.v2.tests.test_phase_d_signal_preservation_supporting_reports
python -B -m unittest Iris.build.description.v2.tests.test_structural_reclassification_code_path_convergence_supporting_reports
python -B -m unittest Iris.build.description.v2.tests.test_structural_reclassification_entrypoint_surface_scan
```

Test role mapping:

| module | role |
|---|---|
| `test_body_plan_phase_d_e` | default structural reclassification emits dual-axis summary, stable summary subset, explicit legacy diagnostic mode, regression gate compatibility |
| `test_report_layer3_body_plan_signal_preservation` | additive lane helper behavior remains compatible with inherited dual-axis naming/reference model |
| `test_phase_d_signal_preservation_supporting_reports` | additive lane supporting reports remain intact as traceability baseline |
| `test_structural_reclassification_code_path_convergence_supporting_reports` | new round Phase 5 guards, exact-match pass path, handoff branch, hash/runtime guard, diagnostic packet |
| `test_structural_reclassification_entrypoint_surface_scan` | entrypoint surface scan discovers direct/build/test surfaces and classifies them for guard validation |

Combined observed result:

```text
Ran 11 tests ... OK
```

Walkthrough 문서 작성 단계에서는 코드가 추가로 바뀌지 않았으므로 tests를 다시 실행하지 않았다.

---

## 9. Top Docs 반영

Phase 6 closeout으로 top docs를 갱신했다.

| 문서 | 반영 내용 |
|---|---|
| `docs/DECISIONS.md` | `closed_with_canonical_code_path_convergence_applied` decision, new canonical baseline hash set, legacy hash historical trace |
| `docs/ARCHITECTURE.md` | `11-60` current default structural reclassification architecture, `11-59` additive lane traceability 유지, default-path wording supersession, divergence status closed |
| `docs/ROADMAP.md` | `#26` closeout addendum, Done/Doing/Next/Hold 갱신; Doing은 없음, Next는 별도 manual in-game validation QA round |

Important wording:

- `body_plan_signal_preservation.*`는 adopted traceability baseline으로 유지한다.
- current default-path observer authority는 plain-name `body_plan_structural_reclassification.2105.*` canonical set으로 이동했다.
- old `phase_d_e_current_session/body_plan_structural_reclassification.2105.*` hash set은 historical trace다.
- writer/runtime authority는 reopen하지 않는다.

---

## 10. Closeout State

Closeout artifact:

- `Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/closeout/closeout_memo.md`

Final state:

| 항목 | 값 |
|---|---|
| overall status | `pass` |
| closeout state | `closed_with_canonical_code_path_convergence_applied` |
| top-doc current-state reflection | allowed |
| handoff state used | no |

New canonical baseline hash set:

| artifact | SHA256 |
|---|---|
| row | `6e84bb2f9622b79493473631d391a01c857c04ddbea869993a99856283ecb6d9` |
| summary | `8b6b7b34ba4c5de9bf6df6d8bcdfeacc6ec86ebda9f0c0b883672177d7b508cf` |
| source distribution | `1c8f8a3431d01f6780f8fe1a602db24ef3ae38febd936df0dec98e8fe80c41b0` |
| section distribution | `b587c663ba928bd7e6a9f8609caba9e3620c92acb6f3fa8359d868b558c0c490` |
| overlap distribution | `831303f7134bf7d8887efed18aaa69ee373fa1ae9b19002302fbb4ad32b973fc` |
| crosswalk | `3d60c945d958778ec89b13ab3efff93732726b969a11e4da9887247b488b817b` |
| artifact validation | `683323b9d52887d2ecf172e97bc6b8d7475a9ac3a8d04deec1db44fcf7c800a7` |

Historical legacy artifact hash set:

| artifact | SHA256 |
|---|---|
| legacy row | `B41A123D9EF2A2821FF89E0724D714C5D87A5FFD78C4813B6727B42486464072` |
| legacy summary | `967B341392EC56BAC76164E23CCFB62C87F859C1DD45CE8CD260A322B0687837` |

---

## 11. What Is Closed

이번 round에서 닫혔다고 말해도 되는 것:

- legacy structural reclassification default code path convergence 완료
- canonical dual-axis read default화 완료
- source/section overwrite 제거 완료
- legacy single-slot view explicit diagnostic-only 격리 완료
- observer artifact baseline regenerate 완료
- exact-match source/section/overlap validation pass
- top docs current-state reflection 완료

이번 round에서 닫혔다고 말하면 안 되는 것:

- deployed closeout
- release readiness
- manual in-game validation completion
- semantic carry adoption
- `quality_baseline_v4 -> v5`
- runtime-side rewrite
- writer authority migration

---

## 12. Non-Reopen Clause

이번 closeout은 아래를 자동 재개방하지 않는다.

- `2026-04-22` staged/static closeout
- `2026-04-23` EDPAS direct default entrypoint authority seal
- `2026-04-24` additive signal preservation closeout

`body_plan_signal_preservation.*` lane은 invalidated artifact가 아니다. 이 lane은 additive preservation evidence와 crosscheck reference로 남고, current default-path authority wording만 이번 convergence round에 의해 superseded된 것으로 읽는다.
