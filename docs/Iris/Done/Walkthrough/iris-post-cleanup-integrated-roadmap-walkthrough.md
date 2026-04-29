# Iris Post-Cleanup Integrated Roadmap Walkthrough

_Last updated: 2026-03-31_

## 1. 목적

이 문서는 `docs/iris-post-cleanup-status-model-runtime-adoption-backlog-expansion-execution-plan.md`가 이 세션에서 실제로 어떻게 실행됐는지 따라가기 위한 walkthrough다.

초점은 다섯 가지다.

- weak-active cleanup W-6 결과가 어떤 baseline으로 동결됐는가
- `Phase 0`부터 `Phase 3`까지 실제로 무엇이 구현됐는가
- runtime adoption과 Phase 3 package execution이 어떤 수치로 닫혔는가
- 실제 runtime reflection과 인게임 검증이 어디까지 끝났는가
- 이번 세션의 완료 범위와 잔여 backlog가 무엇인가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-weak-active-cleanup-walkthrough.md`
- `docs/iris-post-cleanup-status-model-runtime-adoption-backlog-expansion-execution-plan.md`

## 2. 시작점과 끝점

이번 작업은 weak-active cleanup W-6 aggregate가 이미 완료된 상태에서 시작했다.

시작 baseline:

- cleanup scope: `830`
- cleanup semantic split: `strong 194 / adequate 458 / weak 178`
- full runtime rows: `2105`
- full runtime semantic split: `strong 1469 / adequate 458 / weak 178`
- runtime-semantic split: `generated::strong 173 / generated::adequate 449 / generated::weak 133 / missing::strong 21 / missing::adequate 9 / missing::weak 45`

이 세션의 끝점은 다음과 같다.

- Phase 0 input freeze 완료
- Phase 1 status model 설계 및 5개 결정 closure 완료
- Phase 2 runtime adoption 완료
- Phase 2 runtime reflection + 인게임 검증 완료
- Phase 3 backlog expansion first pass package execution 완료
- Phase 3 runtime integration / reflection / 인게임 검증 완료

다만 이 walkthrough 시점에서도 `Phase 3 residual backlog 132`는 남아 있다.  
즉, 이번 세션은 post-cleanup integrated roadmap의 **first operational pass**를 끝낸 것이지, weak backlog를 `0`으로 닫은 것은 아니다.

## 3. 전체 흐름

실행 흐름은 크게 6단계였다.

1. `Phase 0`에서 W-6 aggregate를 후속 설계의 authority로 봉인한다.
2. `Phase 1`에서 2-stage status model을 문서와 JSON 양쪽으로 닫는다.
3. `Phase 2`에서 adoption scope를 고정하고 runtime을 rebuild한다.
4. `Phase 2` 결과를 실제 Iris runtime에 reflection하고 인게임 검증으로 닫는다.
5. `Phase 3`에서 backlog `178`을 package 단위로 분해하고 first pass execution을 수행한다.
6. `Phase 3` 결과를 통합 runtime으로 rebuild한 뒤 reflection과 인게임 검증으로 닫는다.

아래부터는 이 6단계를 순서대로 본다.

## 4. Phase 0: Input Freeze

`Phase 0`의 역할은 post-cleanup 이후의 모든 논의를 같은 baseline에 고정하는 것이었다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase0_input_freeze/post_cleanup_baseline_manifest.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase0_input_freeze/post_cleanup_input_note.md`

이 단계에서 고정된 핵심 수치는 다음과 같다.

- cleanup scope row count: `830`
- backlog row count: `178`
- full runtime row count: `2105`
- silent review row count: `75`
- silent review semantic closure: `strong 21 / adequate 9 / weak 45`

이 단계의 의미는 단순하다.

- `integrated_facts.post_cleanup_candidate.jsonl`은 candidate-only artifact다.
- 이후 Phase 1~3은 모두 W-6 aggregate artifact를 authority로 읽는다.
- cleanup 결과를 다시 분류하지 않는다.

## 5. Phase 1: 2-Stage Status Model

`Phase 1`은 cleanup disposition을 runtime contract로 번역하는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase1_status_model/2_stage_status_model_spec.md`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase1_status_model/status_model_decisions.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase1_status_model/runtime_state_transition_rules.md`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase1_status_model/status_combination_matrix.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase1_status_model/ui_quality_indicator_decision.md`

이 단계에서 닫힌 5개 결정은 다음과 같다.

| 결정 | 결과 |
|------|------|
| `generated::weak 133` | `keep_generated_no_indicator` |
| `missing::strong 21` | `adopt_in_phase2` |
| `missing::adequate 9` | `keep_missing` |
| `missing::weak 45` | `lower_than_generated_weak` |
| UI quality exposure | `no_ui_exposure` |

핵심 판단은 이렇다.

- weak-active cleanup은 purge가 아니라 구조화다.
- 이미 runtime-consumable body가 있는 `generated::weak`는 이번 round에서 내리지 않는다.
- `missing::strong 21`은 별도 extra gate 없이 Phase 2에서 바로 adopt한다.
- `missing::adequate 9`은 아직 runtime-consumable identity body가 없어서 유지한다.
- semantic quality는 이번 round에서 UI에 노출하지 않는다.

## 6. Phase 2: Runtime Adoption

### 6-1. Scope Freeze

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/adoption_scope_manifest.json`

고정된 adoption scope는 다음과 같다.

- `adopt_in_phase2 21`
- `keep_generated 755`
- `keep_missing 54`
- `demote_to_missing 0`

즉, 이번 adoption은 `missing::strong 21`만 실제 runtime 채택 대상으로 들어갔다.

### 6-2. Validation / Rebuild

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/adoption_validation_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/dvf_3_3_facts.adopted.jsonl`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/dvf_3_3_rendered.adopted.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/IrisLayer3Data.lua`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/adoption_runtime_summary.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/adoption_diff_report.json`

실행 결과:

- adopt validation: `21 / 21 pass`
- runtime rows: `2105`
- runtime state: `active 2051 / silent 54`
- runtime path: `cluster_summary 1296 / identity_fallback 718 / role_fallback 91 / direct_use 0`

즉, Phase 2는 `21`개의 missing-strong row를 실제 runtime active lane으로 끌어올린 단계였다.

### 6-3. Runtime Reflection / In-Game Validation

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/runtime_reflection/runtime_reflection_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase2_runtime_adoption/phase2_in_game_validation_result.md`

이 단계에서 staged `IrisLayer3Data.lua`는 실제 runtime 경로인 `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`에 반영됐다.

인게임 검증 결과는 `pass_with_note`였다.

- adopted rows는 정상 표시됐다.
- kept-missing rows는 유지됐다.
- discrepancy로 보였던 `Underwear`는 display-name collision이었다.

즉, Phase 2는 실제 게임 환경까지 포함해 정상적으로 닫혔다.

## 7. Phase 3: Backlog Exploration and Package Execution

### 7-1. Exploration / Package Split

먼저 backlog `178`은 exploration을 거쳐 executable package plan으로 분해됐다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_backlog_exploration/backlog_178_subclass_distribution.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_backlog_exploration/backlog_178_cluster_reuse_assessment.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_backlog_exploration/backlog_178_new_cluster_candidates.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_package_plan/backlog_178_package_plan.md`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_pkg3_unclassified_triage/pkg3_unclassified_followon_packages.json`

여기서 `(unclassified) 40`은 단일 덩어리로 처리하지 않고 `PKG-3A ~ PKG-3J`로 다시 쪼갰다.

### 7-2. Package Execution 결과

이번 세션에서 실행된 package first pass 결과는 다음과 같다.

| Package | promote | residual backlog |
|---------|--------:|-----------------:|
| `PKG-1` Resource.4-E | 20 | 29 |
| `PKG-2` Combat reuse | 5 | 47 |
| `PKG-3A` Construction Repair Materials | 3 | 3 |
| `PKG-3B` Vehicle Service Utility | 1 | 4 |
| `PKG-3C` Camping And Fire Setup | 2 | 4 |
| `PKG-3D` Water And Container Handling | 1 | 3 |
| `PKG-3E` Gardening Inputs And Irrigation | 0 | 6 |
| `PKG-3F` Photo Capture Supplies | 0 | 4 |
| `PKG-3G` Household Access And Safety | 1 | 2 |
| `PKG-3H` Fishing Small Gear | 0 | 3 |
| `PKG-3I` Textile Craft Inputs | 0 | 2 |
| `PKG-3J` Painting Finish Tools | 0 | 1 |
| `PKG-4` Combat Devices And Firearms | 10 | 7 |
| `PKG-5` Tool Trap And Utility Net-New | 1 | 13 |
| `PKG-6` Residual Tail | 2 | 4 |

합계:

- promoted rows: `46`
- residual backlog: `132`

이 단계의 핵심은 “178개 전체를 다시 한 번 분해해서, strong 승격 가능한 재사용 lane과 여전히 net-new가 필요한 잔여 lane을 분리했다”는 데 있다.

## 8. Phase 3: Runtime Integration

Package execution 결과는 다시 하나의 integrated runtime batch로 합쳐졌다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/dvf_3_3_facts.phase3_integrated.jsonl`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/dvf_3_3_decisions.phase3_integrated.jsonl`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/dvf_3_3_rendered.phase3_integrated.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/IrisLayer3Data.lua`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_integration_summary.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_integration_diff_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_promoted_item_index.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_residual_backlog_aggregate.json`

실행 결과:

- promoted rows integrated: `46`
- residual backlog aggregate: `132`
- runtime rows: `2105`
- runtime state: `active 2060 / silent 45`
- runtime path: `cluster_summary 1342 / identity_fallback 685 / role_fallback 78 / direct_use 0`

Phase 2 adopted runtime 대비 delta는 다음과 같다.

- `active +9 / silent -9`
- `cluster_summary +46`
- `identity_fallback -33`
- `role_fallback -13`

즉, package execution 결과는 실제 runtime semantic/runtime surface를 다시 한 번 끌어올렸다.

## 9. Validation Strategy Correction

Phase 3 통합에서 중요한 수정이 하나 있었다.

처음에는 full rendered validation을 그대로 hard gate로 걸어서 `737 hard fail / 737 warn`이 잡혔다. 그러나 이것은 Phase 3가 새 문제를 만들었다는 뜻이 아니라, Phase 2 adopted runtime 안에 이미 존재하던 salvage lane까지 절대값으로 다시 세는 문제였다.

그래서 validation 기준을 **absolute gate**에서 **baseline-delta gate**로 바꿨다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase2_baseline_rendered_validation_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_rendered_validation_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_rendered_validation_delta_report.json`

최종 delta 결과:

- baseline hard fail: `773`
- current hard fail: `737`
- introduced hard fail: `0`
- resolved hard fail: `36`
- introduced warn: `0`
- resolved warn: `36`

즉, Phase 3는 새 validation failure를 늘리지 않았고, 오히려 일부를 줄였다.

## 10. Phase 3 Runtime Reflection and In-Game Validation

Phase 3 staged runtime도 실제 Iris runtime에 반영됐다.

핵심 산출물:

- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/runtime_reflection/runtime_reflection_report.json`
- `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_in_game_validation_result.md`

reflection 결과:

- staged Lua SHA = deployed Lua SHA
- `deployed_matches_staged = true`
- promoted row count reflected: `46`
- residual backlog count carried forward: `132`

인게임 검증 결과:

- validation status: `pass`
- promoted sample rows behaved as intended
- sampled residual backlog rows did not gain unintended strong text
- Phase 2 adopted samples continued to render normally
- unexpected UI regression reported 없음

즉, Phase 3도 실제 게임 runtime까지 포함해 반영과 검증이 끝났다.

## 11. 이번 세션에서 실제로 완료된 범위

이번 세션에서 완료된 것은 다음과 같다.

- W-6 aggregate를 authority로 사용하는 post-cleanup baseline freeze
- Phase 1 status model closure
- Phase 2 runtime adoption / reflection / 인게임 검증
- backlog `178`의 package exploration / split
- backlog first pass package execution
- Phase 3 integrated runtime rebuild
- Phase 3 runtime reflection
- Phase 3 인게임 검증

즉, execution plan 기준으로 보면 “생각 정리용 계획”이 아니라 실제 runtime 반영과 검증까지 포함한 operational pass가 끝난 상태다.

## 12. 아직 남아 있는 것

이번 세션 이후에도 남아 있는 것은 있다.

- residual backlog `132`
- net-new cluster가 필요한 lane
- future source-expansion / second-pass backlog closure

대표 residual bucket은 다음과 같다.

- `painting_cluster_absent 15`
- `music_instrument_cluster_absent 14`
- `multiuse_tool_cluster_absent 10`
- `sports_tool_cluster_mismatch 9`
- `gardening_tool_cluster_absent 8`
- `handgun_firearm_cluster_absent 6`

즉, 이번 세션은 post-cleanup integrated roadmap의 **first production pass**를 완료했지만, backlog expansion 자체가 완전히 끝난 것은 아니다.

## 13. 한 줄 결론

이번 세션은 weak-active cleanup 이후의 후속 로드맵을 실제 system/runtime 작업으로 끝까지 밀어 붙여,  
`status model -> adoption -> package execution -> runtime integration -> reflection -> in-game validation`까지 모두 닫은 세션이었다.  
남은 것은 residual backlog `132`를 다루는 다음 expansion pass다.
