# Iris DVF 3-3 Source Expansion Distribution Remeasurement Gate Walkthrough

_Last updated: 2026-04-19_

## 1. 목적

이 문서는 `identity_fallback` source expansion closeout 이후 이번 세션에서 새로 구현한 `SDRG(Source-Expansion Distribution Remeasurement Gate)`가 무엇을 읽고, 무엇을 만들고, 어디에서 closeout됐는지를 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 왜 SDRG를 source expansion execution과 분리된 observer gate로 잠갔는가
- baseline을 왜 `comparison baseline`과 `current handoff authority` 두 층으로 나눴는가
- 왜 Phase 2-3을 batch execution이 아니라 trigger prerequisite authority로 축소했는가
- fresh recompute와 5축 adjudication이 어떤 artifact chain으로 닫혔는가
- retroactive backfill first application과 terminal status/handoff가 왜 mainline에 들어갔는가
- Group B `569` pre-wiring이 왜 enforcement가 아니라 preferred precondition으로만 남았는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/Iris/Done/iris-dvf-3-3-source-expansion-distribution-remeasurement-gate-final-integrated-execution-plan.md`

## 2. 시작점과 끝점

이번 세션의 시작점은 두 가지 authority가 이미 닫혀 있는 상태였다.

- `identity_fallback` terminal handoff
  - runtime row count: `2105`
  - runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish split: `internal_only 617 / exposed 1467`
- historical source expansion comparison baseline
  - runtime path counts: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`

이번 세션의 종료점은 root-level SDRG manifest 기준 아래와 같다.

- round status: `completed`
- trigger status: `ready_for_phase4_fresh_recompute`
- round exit status: `PASS`
- axis adjudication: `audit PASS / overlay PASS / lint PASS / quality PASS / publish PASS`
- immediate next round planned: `false`
- retroactive backfill mode: `observer_only_first_application`
- Group B pre-wiring: `preferred_precondition = true`, `manual_baseline_freeze_fallback_allowed = true`

즉 이번 세션은 plan 문서만 쓴 것이 아니라, `Phase 1 -> Phase 8`까지 builder/test/artifact/canonical docs를 실제로 닫은 구현 세션이었다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 일곱 줄로 요약된다.

- SDRG는 source expansion batch owner가 아니라 **closeout 이후 observer gate** 로 구현됐다.
- delta 계산 기준은 historical comparison baseline이 아니라 **latest current handoff authority** 다.
- recompute는 repair가 아니라 current authority를 다시 읽는 observer snapshot으로 고정됐다.
- 5축 adjudication 결과 current round는 전축 `PASS`다.
- `round_exit_status`는 축별 verdict를 덮어쓰는 점수가 아니라 closeout status로만 계산된다.
- retroactive backfill은 optional appendix가 아니라 **first-application mainline artifact** 로 구현됐다.
- current SDRG는 닫혔고, 남은 것은 `semantic decision input` 뿐이다. 즉시 열리는 next round는 없다.

## 4. 전체 흐름

이번 세션의 구현 흐름은 크게 여섯 단계였다.

1. plan 문서를 v1.2까지 수정해 baseline 분리, trigger prerequisite 분리, backfill mainline 승격, exit status 규칙을 봉인했다.
2. `Phase 1 / 2-3` builder를 구현해 baseline freeze와 trigger prerequisite artifact를 생성했다.
3. `Phase 4 / 5` builder를 구현해 fresh recompute snapshot, 5축 distribution files, delta report, baseline carry decision을 생성했다.
4. `Phase 6 / 6.5 / 7 / 8` builder를 구현해 semantic decision packet, retroactive backfill, terminal status/handoff, Group B pre-wiring을 생성했다.
5. full runner를 추가해 SDRG 전체 artifact chain을 root manifest/status 하나로 재생성할 수 있게 했다.
6. `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`에 current SDRG closeout read point를 addendum으로 반영했다.

아래부터는 이 순서를 그대로 따라간다.

## 5. Plan Revision: 왜 v1.2까지 밀어 올렸는가

처음부터 바로 builder를 쓰지 않고, 먼저 plan을 current authority에 맞게 다시 잠갔다.

핵심 수정 포인트는 네 가지였다.

- baseline을 단일 "현재 값"이 아니라
  - `pre-expansion comparison baseline`
  - `current handoff authority`
  로 분리했다.
- SDRG 문서에서 source expansion execution phase를 제거하고 `Phase 2-3 Trigger Prerequisites`로 축소했다.
- retroactive backfill을 optional appendix가 아니라 `Phase 6.5` mainline으로 승격했다.
- `round_exit_status` 규칙을 추가했다.
  - any `DRIFT` -> `DRIFT`
  - no `DRIFT`, any `REVIEW` -> `REVIEW`
  - all `PASS` -> `PASS`

추가로 implementation 관점에서 중요한 메모도 문서에 넣었다.

- `terminal_status.json` = lane closeout authority
- `terminal_handoff.json` = downstream read authority

이 구분은 이후 builder payload와 canonical docs sync에 그대로 반영됐다.

## 6. Phase 1 / 2-3: Baseline Freeze와 Trigger Prerequisite

첫 구현은 아래 두 phase였다.

구현 스크립트:

- `Iris/build/description/v2/tools/build/build_source_expansion_distribution_remeasurement_gate_phase1_3.py`

검증 스크립트:

- `Iris/build/description/v2/tests/test_build_source_expansion_distribution_remeasurement_gate_phase1_3.py`

핵심 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/phase1_baseline_freeze/pre_expansion_baseline_v0.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase1_baseline_freeze/baseline_authority_snapshot.md`
- `staging/source_expansion_distribution_remeasurement_gate/phase2_3_trigger_prerequisites/source_expansion_closeout_authority.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase2_3_trigger_prerequisites/expected_expansion_scope_reference.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase2_3_trigger_prerequisites/source_expansion_trigger_prerequisites.json`

여기서 고정된 핵심 값은 다음과 같다.

- comparison baseline:
  - runtime row count: `2105`
  - active / silent: `2084 / 21`
  - runtime path counts: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- current handoff authority:
  - runtime row count: `2105`
  - runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish split: `internal_only 617 / exposed 1467`
- provenance-only intermediate snapshot:
  - `source_coverage_runtime_summary.json`
  - runtime path counts: `cluster_summary 1275 / direct_use 12 / identity_fallback 718 / role_fallback 100`

trigger prerequisite 쪽에서 기계적으로 잠근 값은 아래와 같다.

- `bucket_1_existing_cluster_reusable = 11`
- `bucket_2_net_new_cluster_required = 599`
- `trigger_status = ready_for_phase4_fresh_recompute`

이 구현의 핵심은 SDRG가 source expansion을 "설명"할 수는 있어도, execution owner로 읽히지 않도록 machine-readable prerequisite만 남겼다는 점이다.

## 7. Phase 4 / 5: Fresh Recompute와 5축 Adjudication

그다음에는 recompute와 delta adjudication을 붙였다.

구현 스크립트:

- `Iris/build/description/v2/tools/build/build_source_expansion_distribution_remeasurement_gate_phase4_5.py`

검증 스크립트:

- `Iris/build/description/v2/tests/test_build_source_expansion_distribution_remeasurement_gate_phase4_5.py`

핵심 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/phase4_fresh_recompute/post_expansion_recompute_manifest.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase4_fresh_recompute/post_expansion_rendered_snapshot.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase4_fresh_recompute/post_expansion_regression_pack.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase4_fresh_recompute/post_expansion_remeasurement_v0.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/post_source_expansion_audit_distribution.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/post_source_expansion_overlay_distribution.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/post_source_expansion_lint_distribution.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/post_source_expansion_quality_distribution.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/post_source_expansion_publish_distribution.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/distribution_delta_report_v0.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase5_distribution_delta/baseline_carry_decision_v0.json`

여기서 가장 중요한 구현 선택은 recompute를 "다시 compose해서 고친 결과"가 아니라 **current authority observer snapshot** 으로 읽었다는 점이다.

그래서 current delta는 모두 `0`으로 닫혔다.

- audit delta:
  - runtime row count: `0`
  - runtime path counts: `cluster_summary 0 / identity_fallback 0 / role_fallback 0`
- overlay delta: `0`
- lint delta: `0`
- quality delta: `0`
- publish delta: `0`

이에 따라 current adjudication은 전축 `PASS`다.

- `audit PASS`
- `overlay PASS`
- `lint PASS`
- `quality PASS`
- `publish PASS`
- `round_exit_status = PASS`

여기서 `baseline_carry_decision_v0.json`도 같이 만들었지만, 이건 baseline 승격을 자동으로 밀어붙이지 않는다. current 값은 아래처럼 닫혔다.

- `carry_decision = defer_to_phase6_semantic_decision`
- `followup_round_required = false`

즉 Phase 5는 "모든 게 좋아 보이니 곧바로 v5로 올린다"가 아니라, "distribution drift는 없고, policy decision은 아직 explicit하게 남긴다"로 닫혔다.

## 8. Phase 6 / 6.5: Semantic Decision Input과 Retroactive Backfill

그다음 단계에서는 future decision input과 first-application backfill을 mainline에 올렸다.

구현 스크립트:

- `Iris/build/description/v2/tools/build/build_source_expansion_distribution_remeasurement_gate_phase6_8.py`

검증 스크립트:

- `Iris/build/description/v2/tests/test_build_source_expansion_distribution_remeasurement_gate_phase6_8.py`

Phase 6 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/semantic_decision_input_packet.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/semantic_decision_review.md`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/decisions_md_patch_proposal.md`

이 packet에서 current decision-required item은 세 가지다.

- `baseline_carry_decision`
- `weak_signal_handling`
- `drift_investigation_scope`

현재 상태는 아래처럼 읽힌다.

- baseline carry: required `true`, default path `defer_until_explicit_phase6_decision`
- weak signal handling: required `true`, default path `keep_as_backlog_signal`
- drift investigation: required `false`, default path `none`

즉 SDRG는 semantic decision의 **입력**만 만든다. decision 자체를 자동으로 닫지 않는다.

Phase 6.5 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/phase6_5_retroactive_backfill/retroactive_axis_recoverability_precheck.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_5_retroactive_backfill/pre_expansion_baseline_v0_retroactive.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_5_retroactive_backfill/post_expansion_remeasurement_v0_retroactive.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_5_retroactive_backfill/distribution_delta_report_v0_retroactive.json`
- `staging/source_expansion_distribution_remeasurement_gate/phase6_5_retroactive_backfill/baseline_carry_decision_v0_retroactive.json`

recoverability precheck의 핵심 결론은 아래와 같다.

- `audit`: `partial_recoverable`
  - runtime row/path counts는 복원 가능
  - active/silent split in current handoff는 canonical downstream field가 아님
- `overlay`: `recoverable`
- `lint`: `recoverable`
- `quality`: `recoverable`
- `publish`: `recoverable`

즉 backfill은 "모든 걸 완벽히 복구한다"가 아니라, **무엇이 observer-side로 복원 가능한지 먼저 판정한 뒤 그 한도 안에서만 artifact를 만든다** 는 원칙으로 구현됐다.

## 9. Phase 7 / 8: Terminal Snapshot과 Group B 569 Pre-wiring

observer gate도 결국 current-state consumer가 읽을 root surface가 필요하다. 그래서 terminal status/handoff와 Group B pre-wiring을 같이 붙였다.

Phase 7 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/closeout/source_expansion_remeasurement_terminal_status.json`
- `staging/source_expansion_distribution_remeasurement_gate/closeout/source_expansion_remeasurement_terminal_handoff.json`
- `staging/source_expansion_distribution_remeasurement_gate/closeout/source_expansion_remeasurement_closeout.md`

current terminal closeout은 아래처럼 읽힌다.

- axis adjudication: `audit PASS / overlay PASS / lint PASS / quality PASS / publish PASS`
- `round_exit_status = PASS`
- `immediate_next_round_planned = false`
- `next_round_kind = none`

여기서 중요한 건 `round_exit_status`가 마스터 점수가 아니라 **closeout status** 라는 점이다. DRIFT가 없으므로 next round가 자동으로 열리지 않는다.

Phase 8 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/group_b_pre_wiring/group_b_pre_wiring_runbook.md`
- `staging/source_expansion_distribution_remeasurement_gate/group_b_pre_wiring/sdrg_trigger_procedure.md`
- `staging/source_expansion_distribution_remeasurement_gate/group_b_pre_wiring/group_b_expected_delta_template.json`

여기서 고정한 값은 다음과 같다.

- `group_label = Group B 569`
- `preferred_precondition = true`
- `manual_baseline_freeze_fallback_allowed = true`

즉 current architecture는 Group B가 열릴 때 SDRG wiring을 미리 준비해 두되, SDRG가 Group B execution을 막는 enforcement gate는 아니라는 점을 구현 artifact에서도 그대로 유지했다.

## 10. Root Runner와 Current Read Point

마지막으로 phase별 builder를 하나의 entrypoint로 묶었다.

구현 스크립트:

- `Iris/build/description/v2/tools/build/build_source_expansion_distribution_remeasurement_gate.py`

검증 스크립트:

- `Iris/build/description/v2/tests/test_build_source_expansion_distribution_remeasurement_gate.py`

root 산출물:

- `staging/source_expansion_distribution_remeasurement_gate/source_expansion_distribution_remeasurement_gate_manifest.json`
- `staging/source_expansion_distribution_remeasurement_gate/source_expansion_distribution_remeasurement_gate_status.md`

이 root manifest가 current canonical read point다.

여기서 다음이 한 번에 보인다.

- `round_status = completed`
- `trigger_status = ready_for_phase4_fresh_recompute`
- `round_exit_status = PASS`
- `immediate_next_round_planned = false`
- current handoff authority
- axis adjudication
- decision required items
- retroactive backfill mode
- Group B pre-wiring summary

즉 다음 세션은 더 이상 phase별 파일을 일일이 따라가며 "지금 어디까지 왔는가"를 다시 해석할 필요가 없다.

## 11. Canonical Docs Sync

artifact chain이 먼저 닫힌 뒤에야 canonical docs를 올렸다.

업데이트한 문서:

- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`

이번 sync에서 고정한 핵심 해석은 세 가지다.

- SDRG는 source expansion closeout 위의 observer side branch다.
- current closeout은 `PASS / no immediate next round planned`다.
- retroactive backfill은 terminalized lane reopen이 아니라 observer-side first application이다.

특히 ROADMAP에는 기존 `5-y0 Next`의 `audit / overlay / lint` remeasurement를 artifact 기준으로 Done에 올리고, 추가된 `quality / publish` 두 축도 별도 확장으로 같이 닫았다는 점을 명시했다.

## 12. 테스트와 구현 메모

이번 세션에서 직접 확인한 테스트는 아래 네 가지다.

- `test_build_source_expansion_distribution_remeasurement_gate_phase1_3.py`
- `test_build_source_expansion_distribution_remeasurement_gate_phase4_5.py`
- `test_build_source_expansion_distribution_remeasurement_gate_phase6_8.py`
- `test_build_source_expansion_distribution_remeasurement_gate.py`

묶음 기준으로는 아래 명령으로 `4`건을 통과시켰다.

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_build_source_expansion_distribution_remeasurement_gate*.py"
```

구현 중 실제로 한 번 수정한 부분도 있었다.

- `build_source_expansion_distribution_remeasurement_gate_phase4_5.py`는 처음에 `python file.py` direct run 시 `ModuleNotFoundError: No module named 'tools'`가 났다.
- 해결은 `MODULE_ROOT`를 `sys.path`에 넣는 bootstrap 한 줄을 추가하는 방식으로 했다.
- 이후 테스트와 direct builder 실행 모두 통과했다.

## 13. 현재 읽기 규칙

이번 세션 이후 current SDRG는 아래처럼 읽는 것이 맞다.

- source expansion execution owner가 아니다.
- current baseline은 `identity_fallback_terminal_handoff.json` 기준이다.
- historical comparison baseline은 delta reference가 아니라 side-by-side context다.
- `distribution_delta_report_v0.json`의 축별 verdict가 1차 authority다.
- round-level closeout은 `source_expansion_remeasurement_terminal_status.json`과 `source_expansion_remeasurement_terminal_handoff.json`이 맡는다.
- root-level first read point는 `source_expansion_distribution_remeasurement_gate_manifest.json`이다.
- next round는 자동으로 열리지 않는다.
- 남은 것은 semantic carry/weak signal에 대한 **explicit decision** 뿐이다.

한 줄로 요약하면, 이번 세션은 `source expansion 후 분포를 다시 잰다`는 계획을 실제로 **baseline freeze -> observer recompute -> 5축 PASS adjudication -> retroactive first application -> terminal snapshot** 체계로 구현해 current authority로 고정한 세션이었다.
