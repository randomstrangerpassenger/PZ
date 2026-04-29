# Iris DVF 3-3 Body Plan Migration Session Walkthrough

기준일: 2026-04-21  
대상 세션: `Iris DVF 3-3 compose authority migration round` 실행 세션  
상태: A/B/C closeout + same-session D/E-0/E attempt quarantine 기록용 walkthrough

---

## 0. Correction Notice

이 문서의 최초 버전은 same-session Phase D/E-0/E execution attempt를 closeout으로 기록했으나, 후속 검토에서 그 판정은 철회됐다.

현재 correction 기준:

- Phase D/E-0/E attempt에 대응되는 사전 `scope_policy_override_round` opening decision이 없었다.
- D/E attempt가 읽은 `historical_snapshot/full_runtime` facts/decisions source는 `1050` rows였고, 봉인된 current runtime baseline `2105 rows / active 2084 / silent 21`이 아니었다.
- `quality_publish_decision_v2_preview.full.jsonl`은 `body_plan` section 기준으로 `quality_state / publish_state`를 재계산해 `adequate 130`을 만들었으므로, `quality_baseline_v4` 유지 및 current `v5` cutover 없음 결정과 충돌한다.
- `IrisLayer3Data.lua`의 `1050` row generated output은 deployed authority로 읽지 않으며, runtime Lua data는 sealed `quality_publish` bridge baseline으로 복구했다.

따라서 이 문서에서 Phase D/E-0/E 수치는 current pass evidence가 아니라 quarantined diagnostic output으로만 읽는다. Current authoritative read는 Phase A/B/C closeout까지다.

2026-04-22에는 별도 `scope_policy_override_round`인 `Phase D / E-0 / E staged rollout override round`가 opened 상태로 전환됐다. 이 새 round는 `2105 / active 2084 / silent 21` 및 `quality_baseline_v4`를 baseline으로 사용하며, 위의 `1050 / adequate 130` 탐사 로그를 되살리지 않는다.

---

## 1. 문서 목적

이 문서는 이번 세션에서 진행한 Iris DVF 3-3 `sentence_plan -> body_plan` compose authority migration 작업과, 이후 invalidated/quarantined 처리된 same-session Phase D/E-0/E attempt를 추적하기 위한 walkthrough다.

핵심 목적은 세 가지다.

- 어떤 이유로 Phase A/B/C와 Phase D/E-0/E가 분리됐는지 설명한다.
- 이번 세션에서 실제로 어떤 구현, artifact, validation이 생성됐는지 기록한다.
- 이후 세션에서 같은 논쟁을 반복하지 않도록 current authoritative read와 quarantined read를 분리한다.

이 문서는 새 gate를 만들지 않는다. Canonical 상태는 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`가 가진다. D/E-0/E generated artifacts는 quarantine 결정 이후 current pass evidence가 아니다.

---

## 2. 세션 시작 기준선

세션 시작 시 사용자가 제시한 round 정의는 다음이었다.

- 이 round는 "본문을 더 좋게 쓰는 계획"이 아니라 `sentence_plan` runtime authority를 `body_plan`으로 교체하는 실행 계획이다.
- Scope는 Phase A/B/C이며, Phase D structural violation redesign, Phase E-0 regression gate, Phase E full-runtime rollout은 후속 round로 분리한다.
- A gate가 닫혀야 B/C 설계와 집행이 가능하고, B close 없이 C 집행은 금지한다.
- 기존 body-role closeout과 publish-state round는 재오픈하지 않는다.

초기 planning document는 `docs/Iris/iris-dvf-3-3-compose-authority-migration-round-final-integrated-plan.md`로 고정했다.

---

## 3. Phase A Walkthrough

Phase A의 목적은 top docs에서 compose authority lane을 canonical하게 여는 것이었다.

수행한 작업:

- `DECISIONS.md`에 `sentence_plan` 기반 legacy 3-profile에서 `body_plan` 기반 new 6-profile로 교체하는 결정을 기록했다.
- `ARCHITECTURE.md`에 Layer 3 production authority가 `body_plan` section emission 중심으로 이동한다는 read를 추가했다.
- `ROADMAP.md`에 `Iris DVF 3-3 compose authority migration round` addendum을 추가했다.
- 세 접점의 Phase C 기간 작동 방식을 명시했다.
- Adapter 접점을 네 번째 접점으로 추가하고, compose-internal non-writer bridge로 봉인했다.

중요한 Phase A 정리:

- structural signal은 Phase C 동안 observer-only다.
- legacy `quality_flag` family는 Phase D redesign 전까지 existing family frozen이다.
- post-compose decision stage는 flat rendered string과 existing decision input shape를 계속 소비한다.
- adapter는 외부 preprocessor가 아니며 `compose_layer3_text.py` 내부 compatibility path다.

---

## 4. Phase B Walkthrough

Phase B의 목적은 overlay seam과 validator boundary를 닫아 Phase C 구현자가 입력 계약을 추측하지 않게 만드는 것이었다.

수행한 작업:

- `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md`를 canonical Phase B 소속 artifact로 정리했다.
- `docs/Iris/forbidden_patterns.json`을 추가했다.
- `docs/Iris/seam_legality_checklist.md`를 추가했다.
- validator scope를 `dvf_3_3_cross_layer_overlay_spec.md` appendix 수준으로 귀속시켜 canonical 문서 수 증가 위험을 줄였다.

Phase B에서 닫은 boundary:

- validator는 drift-checker / legality-checker까지만 담당한다.
- validator는 rendered 문장을 고치지 않는다.
- required / optional / required_any legality만 검사한다.
- overlay 누락, 중복, 충돌의 hard fail / warn / skip 판정을 문서화했다.
- browser, wiki, Lua bridge는 compose를 대신하지 않는다.
- compose 외부 repair, post-validator rewrite, runtime patch, style linter 승격은 금지했다.

---

## 5. Phase C Walkthrough

Phase C의 목적은 `compose_layer3_text.py`의 runtime authority를 실제로 `sentence_plan`에서 `body_plan`으로 전환하는 것이었다.

### 5.1 Profile Migration

고정한 crosswalk:

| legacy | new |
|---|---|
| `interaction_tool` | `tool_body` |
| `interaction_component` | `material_body` |
| `interaction_output` | `output_body` |
| - | `container_body` |
| - | `wearable_body` |
| - | `consumable_body` |

주요 artifact:

- `profile_migration_table.json`
- `profile_migration_inventory.json`
- `manual_rebucket_candidates.json`
- `docs/Iris/profile_migration_spec.md`

### 5.2 Writer Authority

구현 방향:

- `compose_layer3_text.py` 내부에 `body_plan` builder와 section emission engine을 추가했다.
- legacy `sentence_plan` reader는 제거가 아니라 compatibility adapter input으로 강등했다.
- adapter는 문장을 생성하지 않고 기존 필드를 새 section slot에 배치만 한다.
- empty section의 생성 또는 생략은 adapter가 아니라 compose writer가 `body_plan` 규칙으로 처리한다.
- output은 계속 flat string이다.

### 5.3 Phase C Verification

고정한 검증 축:

- pilot corpus: `48` rows로 `40~60` gate 충족
- golden subset seed: profile별 최소 `5` rows
- determinism: sample/full-runtime repeat-run hash identical
- legacy diff: accidental change `0`

주요 artifact:

- `pilot_corpus_manifest.json`
- `golden_subset_seed.json`
- `compose_determinism_report.json`
- `legacy_vs_bodyplan_diff_report.json`
- `docs/Iris/phase_c_exit_gate.md`
- `docs/Iris/phase_c_adversarial_review.md`
- `docs/Iris/iris-dvf-3-3-compose-authority-migration-round-closeout.md`

중요한 해석:

- per-profile `strong / adequate / weak` triad는 current runtime distribution에 없는 cell을 synthetic row로 만들지 않았다.
- Phase C gate는 authority migration과 deterministic compose verification을 닫는 gate이지, full-runtime quality distribution gate가 아니다.

---

## 6. Phase D Walkthrough

Phase D는 처음 roadmap에서 후속 round로 분리돼 있었다. 같은 세션에서 D/E까지 진행하는 attempt가 있었지만, 사전 `scope_policy_override_round` opening decision 없이 진행됐으므로 current closeout으로 채택하지 않는다.

Phase D의 목적은 `body_plan` section trace 기준으로 structural signal을 재계상하는 것이었다.

추가한 코드:

- `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`

추가한 문서:

- `docs/Iris/iris-dvf-3-3-body-plan-structural-violation-redesign-round.md`

생성한 artifact:

- `body_plan_structural_reclassification.full.jsonl`
- `body_plan_structural_reclassification.summary.full.json`

Phase D attempt 결과:

| 항목 | 값 |
|---|---:|
| row count | `1050` |
| active | `975` |
| silent | `75` |
| `BODY_LACKS_ITEM_SPECIFIC_USE` | `485` |
| `none` | `565` |
| `SECTION_COVERAGE_DEFICIT` | `459` |
| `BODY_LOSES_ITEM_CENTRICITY` | `37` |
| hard block candidate | `0` |

Quarantine boundary:

- 아래 수치는 `1050` row historical snapshot subset 기준 diagnostic output이다.
- 봉인된 current runtime baseline `2105` row 전체를 대표하지 않는다.
- rendered 문장, `quality_state`, `publish_state`를 직접 수정하지 않는다는 observer-only 원칙은 유지하되, 이 attempt의 output은 Phase E-0 gate input으로 채택하지 않는다.

---

## 7. Phase E-0 Walkthrough

Phase E-0 attempt의 목적은 full-runtime body_plan compose output이 regression gate를 통과하는지 확인하는 것이었으나, input baseline이 `1050` row subset이었고 quality/publish axis를 재계산했기 때문에 current gate로 채택하지 않는다.

추가한 코드:

- `Iris/build/description/v2/tools/build/validate_body_plan_full_runtime_regression_gate.py`

생성한 artifact:

- `body_plan_v2_regression_gate_report.json`

Quarantined gate output:

| 기준 | 결과 |
|---|---|
| overall status | `pass` |
| row count consistent | `pass` |
| runtime counts consistent | `pass` |
| determinism pass | `pass` |
| unexpected delta zero | `pass` |
| blocker count zero | `pass` |
| accidental change zero | `pass` |
| publish state no regression | `pass` |
| layer4 hard block zero | `pass` |

Quarantined 주요 수치:

| 항목 | 값 |
|---|---:|
| row count | `1050` |
| active | `975` |
| silent | `75` |
| strong | `360` |
| adequate | `130` |
| weak | `485` |
| exposed | `490` |
| internal_only | `485` |
| unexpected delta | `0` |
| blocker count | `0` |
| accidental change | `0` |
| publish regression | `0` |
| layer4 hard block | `0` |

---

## 8. Phase E Walkthrough

Phase E attempt의 목적은 full-runtime staged `body_plan` output을 Lua runtime bridge에 반영하고, staged authority와 deployed artifact의 parity를 확인하는 것이었으나, `1050` row source와 recalculated quality/publish axis를 사용했으므로 deployed authority로 채택하지 않는다.

추가한 코드:

- `Iris/build/description/v2/tools/build/build_body_plan_v2_runtime_rollout.py`

Attempt 중 갱신됐으나 이후 복구한 runtime artifact:

- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

생성한 reports:

- `body_plan_v2_lua_bridge_report.json`
- `body_plan_v2_runtime_validation_report.json`
- `body_plan_v2_runtime_rollout_report.json`

Quarantined Phase E output:

| 항목 | 값 |
|---|---|
| overall status | `pass` |
| Lua bridge source/runtime entries | `1050 / 1050` |
| runtime publish states | `internal_only 485 / exposed 490` |
| static runtime validation | `ready_for_in_game_validation` |
| generated Lua parity | `pass` |
| Lua hash | `896ffbaf48914c9fb6361ef40dd911aa9a31e4e02e4d83a8f68f10b38be1a7ec` |

Correction boundary:

- runtime-side compose/rewrite는 도입하지 않았다.
- Lua bridge는 staged authority를 소비하는 consumer일 뿐 writer가 아니다.
- 그러나 `1050` row generated `IrisLayer3Data.lua`는 current runtime deployment로 읽지 않는다.
- manual in-game exhaustive sampling 없이 runtime rollout closeout을 선언하지 않는다.

---

## 9. Tests

이번 세션에서 확인한 테스트:

```powershell
python -B -m unittest Iris.build.description.v2.tests.test_body_plan_phase_d_e
```

결과:

```text
Ran 3 tests
OK
```

전체 description v2 테스트:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

결과:

```text
Ran 295 tests
OK
```

---

## 10. Top Docs Update

세션 마지막에 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`를 다시 정리했으나, 후속 검토 이후 한 번 더 correction을 적용했다.

정리한 이유:

- Phase C closeout 당시에는 Phase D/E가 후속 lane으로 남아 있었다.
- 이후 같은 세션에서 사용자의 명시 요청으로 Phase D/E-0/E를 opened/closed했다.
- 따라서 Phase C 기준 문구가 current state처럼 읽히면 phase ownership이 다시 꼬일 수 있었다.

최종 correction 내용:

- `DECISIONS.md`: Phase C closeout은 유지하고, same-session D/E attempt는 quarantine decision으로 내렸다.
- `ARCHITECTURE.md`: 11-53을 current adopted read로 유지하고, 11-54는 D/E attempt quarantine으로 바꿨다.
- `ROADMAP.md`: #20은 Phase C closeout read로 유지하고, #21은 D/E closeout이 아니라 quarantine addendum으로 바꿨다.

검증:

- stale phrase 검색은 top docs 전체를 대상으로 다시 수행해야 한다. 이 문서의 correction 이후 기준은 "D/E/E-0/E closeout이 current state처럼 읽히지 않아야 한다"이다.

---

## 11. Current Authoritative Read

2026-04-21 correction 기준 current read는 다음과 같다.

- Iris DVF 3-3 compose authority migration lane은 A/B/C까지 close 상태다.
- Runtime compose authority는 `body_plan` section emission이다.
- legacy `sentence_plan`은 compose-internal adapter compatibility input으로만 남는다.
- Phase D structural accounting redesign은 current closeout이 아니다.
- Phase E-0 full-runtime regression gate는 current pass가 아니다.
- Phase E runtime Lua rollout은 current deployed closeout이 아니다.
- `IrisLayer3Data.lua`는 sealed `quality_publish` bridge baseline으로 복구된 상태로 읽는다.
- 2026-04-22 `scope_policy_override_round`가 열렸으므로 D/E-0/E는 staged/static rollout 범위에서 다시 진행 가능하다.
- 이 override round의 baseline은 `2105 / active 2084 / silent 21`, publish split `internal_only 617 / exposed 1467`, quality split `strong 1316 / adequate 0 / weak 768`이다.

---

## 12. Explicit Non-Goals After Closeout

Phase C closeout 이후에도 아래 항목은 자동으로 열리지 않는다.

- compose 외부 repair 재도입
- runtime-side compose/rewrite
- `quality_state / publish_state` axis 재정의
- facts 슬롯 확장
- manual in-game exhaustive sampling
- future source expansion

이 항목들이 필요하면 compose migration lane의 연장이 아니라 별도 explicit round로 열어야 한다.
