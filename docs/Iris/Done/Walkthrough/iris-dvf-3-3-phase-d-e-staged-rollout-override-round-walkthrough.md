# Iris DVF 3-3 Phase D/E Staged Rollout Override Round Walkthrough

기준일: 2026-04-22  
대상 라운드: `Iris DVF 3-3 compose authority migration — Phase D / E-0 / E staged rollout override round`  
상태: staged/static closeout 완료, `ready_for_in_game_validation`

---

## 0. 문서 목적

이 문서는 Phase D/E-0/E staged rollout override round에서 실제로 무엇을 고쳤고, 어떤 산출물로 검증했는지 추적하기 위한 walkthrough다.

이 문서는 새 gate나 새 decision source가 아니다. Canonical 상태는 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`가 가진다. 이 문서는 이후 세션에서 “왜 이 수치를 썼는가”, “어느 문제를 어디서 고쳤는가”, “무엇은 아직 검증하지 않았는가”를 빠르게 복원하기 위한 작업 로그다.

---

## 1. Round Opening

이 라운드는 2026-04-21에 quarantined 처리된 same-session Phase D/E attempt를 되살린 것이 아니다. 2026-04-22에 별도 `scope_policy_override_round`로 다시 연 staged/static rollout round다.

Top docs에 기록한 opening decision은 세 가지다.

| 문서 | 기록 내용 |
|---|---|
| `DECISIONS.md` | Phase D/E staged rollout override round opening |
| `DECISIONS.md` | Phase D는 pure observer authority |
| `DECISIONS.md` | Phase E는 staged/static까지만 닫고 in-game validation은 제외 |
| `ARCHITECTURE.md` | `11-55` staged-only lane open |
| `ROADMAP.md` | `22. 2026-04-22 Addendum` |

Phase 0 seal artifact:

`Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/phase0_governance_seal.json`

---

## 2. Baseline

이번 round의 공식 baseline은 2026-04-15 identity_fallback source expansion closeout 이후의 current runtime snapshot이다.

| 축 | 값 | 기준 artifact |
|---|---:|---|
| total rows | `2105` | `subset_runtime_summary.json` |
| runtime_state | `active 2084 / silent 21` | `subset_runtime_summary.json` |
| runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` | `subset_runtime_summary.json` |
| publish split | `internal_only 617 / exposed 1467` | `subset_publish_preview_summary.json` |
| quality distribution | `strong 1316 / adequate 0 / weak 768` | `quality_baseline_v4.json` |

Publish split과 quality distribution은 active rows 기준이다. Silent `21` rows는 두 split의 모수에서 제외한다.

중요한 해석:

| 구분 | 의미 |
|---|---|
| `identity_fallback 17` | runtime path residual |
| `internal_only 617` | publish visibility isolation lane |

두 수치는 같은 축이 아니다. `600 promoted / residual 17` 이후에도 publish split은 `internal_only 617 / exposed 1467`로 유지된다.

---

## 3. Quarantine 문제 재발 방지

이 round가 해결해야 했던 가장 큰 문제는 이전 attempt의 세 가지 혼선이었다.

| 이전 혼선 | 이번 round 처리 |
|---|---|
| `1050` row historical snapshot을 current runtime처럼 사용 | `2105` current runtime source로 재진입 |
| `adequate 130`을 새 quality distribution처럼 기록 | `quality_baseline_v4`의 `strong 1316 / adequate 0 / weak 768`만 gate로 사용 |
| Lua artifact를 row-loss 상태로 갱신 | bridge row count `2105`, publish split `617 / 1467`, staged/workspace byte parity 검증 |

관련 quarantine read는 기존 walkthrough의 correction notice와 top docs에 남겨 두었다.

---

## 4. Phase 0 Walkthrough

Phase 0의 목적은 D/E execution 이전에 governance를 먼저 봉인하는 것이었다.

수행한 작업:

| 작업 | 결과 |
|---|---|
| scope override decision 기록 | 완료 |
| Phase D observer-only decision 기록 | 완료 |
| Phase E staged/static-only decision 기록 | 완료 |
| walkthrough quarantine warning 유지 | 완료 |
| `IrisLayer3Data.lua` baseline hash 확인 | `9c5ceebea334277cb9b235e67fdfed8f2089d3eb1b7a2519ada424be11945ee9` |
| `quality_baseline_v4` distribution 확인 | `strong 1316 / adequate 0 / weak 768` |

Phase 0 closeout artifact:

`Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/phase0_governance_seal.json`

---

## 5. Phase D Walkthrough

Phase D는 `body_plan` section trace를 기준으로 structural signal을 다시 계상하되, writer가 되지 않는 observer-only phase다.

입력은 2026-04-15 subset rollout artifact로 전환했다.

| 입력 | 경로 |
|---|---|
| facts | `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_overlay_facts.jsonl` |
| decisions | `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_overlay_decisions.jsonl` |
| surface signal | `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_surface_contract_signal.jsonl` |

생성한 주요 산출물:

| 산출물 | 목적 |
|---|---|
| `layer3_body_source_overlay.2105.jsonl` | body writer input seam |
| `dvf_3_3_rendered_v2_preview.2105.json` | body_plan rendered preview |
| `body_plan_structural_reclassification.2105.jsonl` | row-level structural signal |
| `body_plan_structural_reclassification.2105.summary.json` | aggregate summary |

Phase D 결과:

| 축 | 값 |
|---|---:|
| row count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| writer role | `observer_only` |
| hard block candidate | `0` |
| `quality_state` field in row artifact | 없음 |

Phase D에서 중요한 점은 `quality_state`, `publish_state`, rendered text를 수정하지 않았다는 것이다. 이 phase는 signal report만 생성한다.

---

## 6. Phase E-0 Walkthrough

Phase E-0는 full-runtime regression gate다. 여기서는 9개 gate axis와 별도 quality distribution gate를 모두 pass해야 한다.

중간에 한 번 gate가 막혔다.

| blocked 원인 | 판정 |
|---|---|
| sprint7 source의 runtime path가 `1440 / 617 / 48`로 측정됨 | 잘못된 입력 source |
| official baseline은 `2040 / 17 / 48` | 2026-04-15 subset rollout artifact 기준 |

해결:

| 수정 | 결과 |
|---|---|
| Phase D/E-0 입력을 04-15 subset rollout facts/decisions/rendered/publish summary로 전환 | runtime path gate pass |
| regression gate script가 `runtime_summary_path`를 받도록 수정 | runtime path baseline source 명확화 |
| quality distribution을 `quality_baseline_v4` sealed axis로 분리 | `adequate 130` 재발 차단 |

E-0 gate report:

`Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_regression_gate_report.2105.json`

E-0 결과:

| gate | 결과 |
|---|---|
| row count consistent | pass |
| runtime_state counts consistent | pass |
| runtime path counts consistent | pass |
| publish split consistent | pass |
| determinism pass | pass |
| accidental change zero | pass |
| unexpected delta zero | pass |
| publish_state regression zero | pass |
| LAYER4 hard block zero | pass |
| quality distribution gate | pass |

Snapshot:

| 축 | 값 |
|---|---:|
| rows | `2105` |
| active / silent | `2084 / 21` |
| runtime path | `2040 / 17 / 48` |
| publish split | `617 / 1467` |
| quality distribution | `1316 / 0 / 768` |
| blocker count | `0` |

---

## 7. Phase E Walkthrough

Phase E는 staged/static rollout만 수행했다. 실제 in-game validation은 하지 않았다.

생성한 artifact:

| 산출물 | 역할 |
|---|---|
| `IrisLayer3Data.body_plan_v2.2105.staged.lua` | staged Lua artifact |
| `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` | workspace Lua data |
| `body_plan_v2_lua_bridge_report.2105.json` | bridge export report |
| `body_plan_v2_runtime_validation_report.2105.json` | static runtime readiness report |
| `body_plan_v2_runtime_rollout_report.2105.json` | rollout/parity report |

Bridge result:

| 축 | 값 |
|---|---:|
| source entries | `2105` |
| runtime entries | `2105` |
| internal_only | `617` |
| exposed | `1467` |

Parity result:

| 대상 | SHA256 |
|---|---|
| staged Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| workspace Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| expected generated payload | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

Static runtime status:

`ready_for_in_game_validation`

---

## 8. 구현 수정 목록

이번 walkthrough에서 추적해야 할 코드 변경은 다음과 같다.

| 파일 | 수정 이유 |
|---|---|
| `build_layer3_body_source_overlay.py` | missing cluster label을 current-session overlay 생성에서 controlled diagnostic으로 허용하는 옵션 추가 |
| `report_layer3_body_plan_structural_reclassification.py` | `writer_role: observer_only` 및 `signal_distribution` 기록 |
| `report_layer3_body_plan_v2_delta.py` | Korean identity surface normalization을 variants 기반으로 수정해 `탄약` / `탄약이다` 같은 false unexpected 차단 |
| `report_compose_determinism.py` | full-runtime determinism 입력 경로를 CLI로 받을 수 있게 수정 |
| `validate_body_plan_full_runtime_regression_gate.py` | 2105 baseline, runtime summary, quality_baseline_v4, 9-axis gate와 quality gate 분리 |
| `build_body_plan_v2_runtime_rollout.py` | staged Lua artifact 생성, byte-level parity, bridge row count/publish split 검증 |

이 수정들은 writer를 추가하지 않는다. Compose writer는 여전히 `body_plan` writer 하나이며, Phase D/E scripts는 report/export/validation path다.

---

## 9. 검증

실행한 검증:

| 검증 | 결과 |
|---|---|
| Phase D `quality_state` 문자열 검색 | 없음 |
| E-0 regression gate | pass |
| staged/workspace Lua `Get-FileHash` | 동일 |
| forbidden closeout wording scan on current-session JSON | clean |
| unit test suite | `295 tests OK` |

사용한 test command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

결과:

```text
Ran 295 tests in 9.779s
OK
```

---

## 10. Current Authoritative Read

이번 round 완료 후 현재 상태는 다음처럼 읽는다.

| 항목 | 상태 |
|---|---|
| Phase 0 | closed |
| Phase D | closed, pure observer |
| Phase E-0 | closed, regression gate pass |
| Phase E | staged/static closed |
| Runtime data artifact | staged/workspace parity pass |
| In-game validation | pending |
| Release readiness | not declared |

허용되는 terminal label:

`ready_for_in_game_validation`

사용하면 안 되는 해석:

| 금지 해석 | 이유 |
|---|---|
| user-facing runtime까지 검증 완료 | manual in-game validation 미수행 |
| quality_baseline_v5로 전환 | SAPR와 v4 유지 decision 위반 |
| Phase D가 quality/publish를 다시 썼다 | Phase D는 observer-only |
| 1050 row artifact가 current state다 | quarantine된 diagnostic artifact |

---

## 11. Next

다음에 열 수 있는 자연스러운 round는 manual in-game validation QA round다.

그 round의 입력은 이번 산출물이다.

| 입력 | 경로 |
|---|---|
| staged/static rollout report | `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_runtime_rollout_report.2105.json` |
| runtime validation report | `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_runtime_validation_report.2105.json` |
| workspace Lua | `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` |

다만 사용자의 운영 방침상, 남은 static/docs/data 문제를 더 정리한 뒤 마지막에 통합 in-game validation을 수행해도 된다. 그 경우 이 round의 상태는 계속 `ready_for_in_game_validation`으로 유지한다.

