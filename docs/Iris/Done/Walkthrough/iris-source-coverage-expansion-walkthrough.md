# Iris Source Coverage Expansion Walkthrough

_Last updated: 2026-03-29_

## 1. 목적

이 문서는 `docs/iris-source-coverage-expansion-roadmap.md`가 실제로 어떻게 실행됐는지 한 번에 따라가기 위한 walkthrough다.

이 walkthrough의 초점은 세 가지다.

- 어떤 기준선에서 출발했는가
- `B / C` backlog가 어떤 순서로 정리되었는가
- 최종적으로 staged source coverage가 어떻게 integrated runtime까지 올라갔는가

상위 기준은 다음 문서들이다.

- `Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

## 2. 시작점과 끝점

이 작업은 historical runtime milestone 위에서 시작했다.

- 시작 runtime rows: `1050`
- 시작 active rows: `975`
- 시작 silent rows: `75`
- 시작 path distribution: `identity_fallback 716 / cluster_summary 222 / role_fallback 112 / direct_use 0`

이 walkthrough 시점의 rebuilt integrated runtime은 다음 상태까지 올라갔다.

- rebuilt runtime rows: `2105`
- rebuilt active rows: `2030`
- rebuilt silent rows: `75`
- rebuilt path distribution: `cluster_summary 1275 / identity_fallback 718 / role_fallback 112 / direct_use 0`
- automated runtime status: `ready_for_in_game_validation`

즉, 이번 로드맵은 "uncovered item universe를 staged package로 밀어 올린 뒤, 그 결과를 실제 runtime bridge까지 재구축하는 것"까지를 포함한다.

## 3. 전체 흐름

실행 흐름은 크게 6단계로 볼 수 있다.

1. Block A에서 baseline과 uncovered universe를 동결한다.
2. Block B에서 `B / C` split과 phase order를 고정한다.
3. Block C에서 `B` package 5개를 staging한다.
4. 이어서 `C` package 10개를 staging한다.
5. 남은 `hold` subset을 정책적으로 닫는다.
6. staged `B/C` package를 merged runtime으로 재구성한다.

아래부터는 이 6단계를 순서대로 본다.

## 4. Block A: Baseline Freeze

Block A의 역할은 숫자 논쟁을 끝내고 이후 계산이 모두 같은 기준선을 보게 만드는 것이었다.

핵심 산출물:

- `Iris/build/description/v2/staging/source_coverage/block_a/block_a_baseline_summary.json`
- `Iris/build/description/v2/staging/source_coverage/block_a/coverage_baseline_note.md`
- `Iris/build/description/v2/staging/source_coverage/block_a/silent_rows_note.md`
- `Iris/build/description/v2/staging/source_coverage/block_a/wearable_preflight_decision.json`

이 단계에서 고정된 핵심 판단은 다음과 같다.

- canonical item universe는 `2285`
- repo 내부 baseline drift는 `2281` vs `2285`로 명시 기록
- earlier proposal-era `2282`는 canonical baseline이 아니라 pre-freeze planning figure로 취급
- uncovered total은 `1235`
- provisional split은 `B = 589`, `C = 646`
- `silent 75`는 별도 감사 대상
- Wearable은 residual 후순위가 아니라 사전 preflight 대상

이 시점의 의미는 간단하다.

- 이후 숫자는 더 이상 제안서 숫자가 아니라 repo artifact 숫자로 읽는다.
- 따라서 walkthrough의 `2285`는 `2282 -> 2285` 수정이라기보다, proposal-era `2282`를 버리고 Block A artifact 기준 `2285`를 canonical로 동결한 결과다.
- `direct_use`는 기대 경로가 아니라 명시적 hold로 본다.

## 5. Block B: `B / C` Split과 우선순위 고정

Block B는 backlog를 실행 가능한 package 단위로 재배열한 단계다.

핵심 산출물:

- `Iris/build/description/v2/staging/source_coverage/block_b/uncovered_group_inventory.json`
- `Iris/build/description/v2/staging/source_coverage/block_b/group_priority_matrix.json`
- `Iris/build/description/v2/staging/source_coverage/block_b/tier_selection.json`

이 단계에서 고정된 실행 순서는 다음과 같다.

- `B-1 Consumable 344`
- `B-2 Literature 102`
- `B-3 Resource 56`
- `B-W Wearable 73`
- `B-4 Residual 14`
- `C-1 Hold 646`

중요한 점은 두 가지다.

- `B`는 이미 `IrisData` 분류가 있는 backlog이므로 즉시 package화 가능한 lane이다.
- `C`는 분류와 runtime coverage가 모두 없는 backlog이므로 곧바로 package화하지 않고 먼저 다시 쪼갠다.

## 6. Block C-1: `B` Package 5개 Staging

`B` lane은 package builder를 통해 순서대로 staging되었다.

대표 산출물 묶음:

- `Iris/build/description/v2/staging/source_coverage/block_c/b1_consumable_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/b2_literature_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/b3_resource_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/bw_wearable_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/b4_residual_package/`

결과 요약:

- `B-1`: `344` rows
- `B-2`: `102` rows
- `B-3`: `56` rows
- `B-W`: `73` rows
- `B-4`: `14` rows
- 합계: `589` rows

이 단계가 끝나면 post-`B` projection이 생성된다.

- `Iris/build/description/v2/staging/source_coverage/post_b/post_b_projection_summary.json`

여기서 `direct_use`는 여전히 `0`으로 남았고, 따라서 open하지 않고 그대로 hold 유지로 고정됐다.

## 7. Block C-2: `C` Lane 분해와 Package 10개 Staging

`C-1 646`은 바로 package화하지 않았다. 먼저 좁은 subset으로 쪼갠 뒤 executable lane만 순차 처리했다.

초기 분해 산출물:

- `Iris/build/description/v2/staging/source_coverage/c1_scope/c1_scope_summary.json`
- `Iris/build/description/v2/staging/source_coverage/c1_scope/c1_priority_matrix.json`
- `Iris/build/description/v2/staging/source_coverage/c1_scope/c1_first_subset_plan.md`

그 뒤 실제로 staging된 `C` package는 10개다.

- `C1-A VehicleMaintenance 92`
- `C1-C Moveable furniture 140`
- `C1-B Portable storage 35`
- `C1-E Security 8`
- `C1-D Appearance 51`
- `C1-RA Desk and pocket smalls 18`
- `C1-RB Household care 18`
- `C1-RD Scrap and empty-material 20`
- `C1-RC Play, media, and novelty 47`
- `C1-RE Utility miscellany 37`

합계는 `466` rows다.

이 단계가 끝난 뒤 post-`C` projection이 생성된다.

- `Iris/build/description/v2/staging/source_coverage/post_c/post_c_projection_summary.json`
- `Iris/build/description/v2/staging/source_coverage/post_c/post_c_remeasurement_note.md`

post-`C` projection의 핵심 숫자는 다음과 같다.

- projected runtime rows: `2105`
- projected active rows: `2030`
- projected silent rows: `75`

즉, 이 시점까지는 아직 "projection은 맞지만 실제 runtime bridge는 아직 sample-sized" 상태였다.

## 8. Hold Policy Closure

`C` backlog를 모두 package로 밀어붙이지 않고, 마지막 `180` rows는 정책적으로 닫았다.

hold subset은 3개다.

- `C1-H1 94`
- `C1-H2 77`
- `C1-RH 9`

핵심 산출물:

- `Iris/build/description/v2/staging/source_coverage/post_c/hold_policy_summary.json`
- `Iris/build/description/v2/staging/source_coverage/post_c/hold_reentry_matrix.json`
- `Iris/build/description/v2/staging/source_coverage/post_c/hold_policy_note.md`

정책 판단은 이렇게 고정됐다.

- `C1-H1`: `state_overlay_excluded`
- `C1-H2`: `state_overlay_excluded`
- `C1-RH`: `manual_outlier_hold`

실질 기준은 이렇게 읽으면 된다.

- `state_overlay_excluded`: body-state / damage overlay처럼 애초에 ordinary item-summary package로 넣으면 안 되는 rows
- `manual_outlier_hold`: inventory-facing row는 맞지만 corpse / hidden prop / placeholder 성격이 섞여 있어 지금 당장 하나의 stable cluster로 묶으면 안 되는 rows

즉, 이 의미는 "더 package를 만들면 된다"가 아니라 "다른 semantic contract가 필요하다"는 뜻이다.

## 9. Integrated Runtime Rebuild

여기서부터가 로드맵의 마지막 기술 단계다.

projection만으로 끝내지 않고, staged `B/C` package를 실제 runtime batch로 다시 합쳤다.

핵심 builder:

- `Iris/build/description/v2/tools/build/build_interaction_cluster_source_coverage_runtime.py`

이 builder가 하는 일은 다음과 같다.

1. historical full runtime의 facts/decisions를 읽는다.
2. staged `B/C` package 15개의 facts/decisions를 읽는다.
3. 중복 없이 한 batch로 합친다.
4. merged facts/decisions로 `rendered`를 다시 만든다.
5. `IrisLayer3Data.lua`를 다시 export한다.
6. runtime report를 다시 만들어 automated checkpoint를 갱신한다.

핵심 산출물:

- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_facts.integrated.jsonl`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_decisions.integrated.jsonl`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_rendered.integrated.json`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/phase_d_runtime_report.integrated.json`

재빌드 결과는 다음과 같다.

- merged package count: `15`
- merged package item count: `1055`
- rebuilt runtime rows: `2105`
- rebuilt active rows: `2030`
- rebuilt silent rows: `75`
- rebuilt path counts: `cluster_summary 1275 / identity_fallback 718 / role_fallback 112 / direct_use 0`
- projection match: `true`
- runtime status: `ready_for_in_game_validation`

즉, 이 시점부터는 더 이상 "merge plan" 단계가 아니라 "rebuilt runtime이 실제로 존재하는 단계"다.

## 10. Rebuild Checkpoint의 의미

integrated runtime이 올라간 뒤 rebuild checkpoint도 다시 기록된다.

핵심 산출물:

- `Iris/build/description/v2/staging/source_coverage/post_c/runtime_rebuild_checkpoint.json`
- `Iris/build/description/v2/staging/source_coverage/post_c/runtime_rebuild_checkpoint.md`

이 checkpoint가 말하는 핵심은 단순하다.

- 상태는 더 이상 `blocked_on_merged_rendered_batch`가 아니다.
- 현재 상태는 `ready_for_in_game_validation`이다.
- 남은 필수 closeout은 automated build가 아니라 manual in-game checklist다.

## 11. 이 walkthrough를 어떤 순서로 읽으면 좋은가

숫자부터 보고 싶으면 아래 순서가 빠르다.

1. `Iris/build/description/v2/staging/source_coverage/block_a/block_a_baseline_summary.json`
2. `Iris/build/description/v2/staging/source_coverage/post_b/post_b_projection_summary.json`
3. `Iris/build/description/v2/staging/source_coverage/post_c/post_c_projection_summary.json`
4. `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json`

판단 기준부터 보고 싶으면 아래 순서가 낫다.

1. `docs/iris-source-coverage-expansion-roadmap.md`
2. `docs/DECISIONS.md`
3. `docs/ROADMAP.md`
4. `Iris/build/description/v2/staging/source_coverage/post_c/hold_policy_note.md`
5. `Iris/build/description/v2/staging/source_coverage/post_c/runtime_rebuild_checkpoint.md`

구현 entrypoint부터 보고 싶으면 아래 파일들이 핵심이다.

- `Iris/build/description/v2/tools/build/report_source_coverage_block_a.py`
- `Iris/build/description/v2/tools/build/report_source_coverage_block_bc.py`
- `Iris/build/description/v2/tools/build/build_source_coverage_*package.py`
- `Iris/build/description/v2/tools/build/report_source_coverage_post_b.py`
- `Iris/build/description/v2/tools/build/report_source_coverage_post_c.py`
- `Iris/build/description/v2/tools/build/report_source_coverage_hold_policy.py`
- `Iris/build/description/v2/tools/build/build_interaction_cluster_source_coverage_runtime.py`

## 12. 완료 판정

이번 walkthrough 기준 완료 판정은 다음처럼 읽는다.

- `source coverage expansion roadmap` 범위는 사실상 완료
- staged package drafting도 완료
- hold policy closure도 완료
- integrated runtime rebuild도 완료
- 남은 필수 작업은 manual in-game validation

반대로 아직 별도 후속 과제로 남아 있는 것은 다음이다.

- 2-stage semantic/runtime status model
- identity fallback reduction strategy
- weak-active cleanup
- legacy historical-runtime builder path cleanup

즉, "이번 로드맵은 인게임 검토만 남았다"와 "Iris 전체 후속 과제가 없다"는 같은 말이 아니다.
