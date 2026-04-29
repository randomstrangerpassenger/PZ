# Iris DVF 3-3 Phase D Observer Signal Preservation Patch Round Walkthrough

기준일: 2026-04-24  
대상 작업: `Iris DVF 3-3 Phase D observer-only signal preservation patch round`  
상태: observer patch closeout 완료, current runtime state는 계속 `ready_for_in_game_validation`

---

## 0. 문서 목적

이 문서는 이번 세션에서 Phase D observer signal preservation patch round를 어떻게 정리했고, 무엇을 구현했고, 어떤 산출물과 검증으로 닫았는지 복원하기 위한 walkthrough다.

이 문서는 새 gate나 새 decision source가 아니다. Canonical 상태는 계속 아래 top docs가 가진다.

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

이 문서가 답하려는 질문은 아래 하나다.

> 기존 upstream source-side signal과 Phase D section-derived signal을 같은 슬롯에서 섞지 않고, additive observer lane으로 분리 보존했는가?

현재 답은 **그렇다**다.

---

## 1. 세션 시작 상태

세션 시작 시점의 핵심 상태는 아래와 같았다.

| 축 | 상태 |
|---|---|
| existing Phase D/E staged closeout | 이미 `ready_for_in_game_validation`로 닫혀 있음 |
| existing structural observer artifact | `body_plan_structural_reclassification.2105.jsonl` / `.summary.json` |
| known concern | observer가 source-side explicit family와 section-derived family를 단일 슬롯에서 lossy 하게 읽을 수 있음 |
| hard sealed baseline | `2105` rows / `active 2084` / `silent 21` / publish `617 / 1467` / quality `1316 / 0 / 768` |
| staged/workspace Lua parity hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |

즉 기존 staged/static closeout은 유지해야 했고, 이번 세션의 문제는 runtime writer를 다시 여는 것이 아니라 observer read model을 additive path로 고치는 일이었다.

---

## 2. 계획 문서 정리

먼저 사용자가 제공한 roadmap과 연속 review feedback을 반영해 planning authority를 정리했다.

계획 문서:

- `docs/Iris/iris-dvf-3-3-phase-d-observer-signal-preservation-patch-round-plan.md`

최종 버전은 `v0.3`으로 고정했다. 주요 revision point는 아래였다.

- Phase 2/3를 단일 `signal model design` phase로 통합
- source distribution `617 / 7 / 1481`를 sealed invariant가 아니라 preservation target으로 하향
- `violation_type` field existence와 usable source population을 분리 gate로 봉인
- `blocked_by_missing_violation_type_field`
- `closed_with_upstream_signal_gap_handoff`
- `SECTION_*` namespace를 mandatory naming rule로 확정
- `combined_read`를 `signal_overlap_state`의 값 공간 이름으로 명시
- `IDENTITY_ONLY`, `ACQ_DOMINANT`를 count target이 아니라 existence/no-overwrite target으로 분리
- `violation_flags` fallback을 closed allowlist로 제한

`blocked_by_empty_violation_type_population`에 대해서는 이 walkthrough가 계획 `v0.3` provenance를 주장하지 않는다. 이 state는 아래 `§4-2`에서 이번 구현이 실제로 사용한 gate 상태로만 기록한다. canonical state space로 승격하려면 별도 plan revision 또는 closeout decision wording이 필요하다.

이 planning revision 단계에서 중요한 방향은 하나였다.

> 기존 sealed artifact를 수정하지 않고, 새 observer lane을 분리 생성한다.

---

## 3. 구현 범위

이번 세션에서 추가한 주요 구현 파일은 아래와 같다.

### Production

- `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`는 defect reference로만 유지
- `Iris/build/description/v2/tools/build/report_layer3_body_plan_signal_preservation.py`
- `Iris/build/description/v2/tools/build/build_phase_d_signal_preservation_baseline.py`
- `Iris/build/description/v2/tools/build/validate_phase_d_signal_preservation.py`
- `Iris/build/description/v2/tools/build/build_signal_preservation_crosscheck.py`
- `Iris/build/description/v2/tools/build/build_phase_d_signal_preservation_diagnostic_packet.py`

### Tests

- `Iris/build/description/v2/tests/test_report_layer3_body_plan_signal_preservation.py`
- `Iris/build/description/v2/tests/test_phase_d_signal_preservation_supporting_reports.py`

### Top docs updates

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

계획 `v0.3`와 구현 사이에는 deliberate write-surface drift가 하나 있었다.

계획 `§12 Phase 3`은 primary write surface를 기존 `report_layer3_body_plan_structural_reclassification.py`로 적었지만, 실제 구현은 additive-only 계약을 더 강하게 지키기 위해 별도 script `report_layer3_body_plan_signal_preservation.py`를 새로 만들었다. 이 선택의 목적은 기존 observer script와 기존 structural artifact를 write surface에서 분리해 existing artifact hash 불변을 더 직접적으로 보장하는 데 있었다.

---

## 4. 핵심 구현 변경

### 4-1. Source axis와 section axis 분리

새 row model은 아래 필드를 기준으로 기록한다.

- `source_signal_primary`
- `source_signal_secondary`
- `source_signal_origin`
- `section_signal_primary`
- `section_signal_secondary`
- `section_signal_origin`
- `source_signal_present`
- `section_signal_present`
- `signal_overlap_state`
- `signal_conflict_note`

기존 single-slot observer view와 달리, 이제 source axis와 section axis는 같은 row에 동시에 존재할 수 있다.

### 4-2. Phase 1 gate

구현 안에서 `violation_type` gate를 아래 네 상태로 분리했다.

- `blocked_by_missing_violation_type_field`
- `blocked_by_empty_violation_type_population`
- `closed_with_upstream_signal_gap_handoff`
- `pass`

여기서 `blocked_by_empty_violation_type_population`은 이번 구현이 실제로 가진 gate state다. 이 walkthrough는 그 state가 계획 `v0.3`에 이미 공식 선언돼 있었다고 소급 주장하지 않는다.

이번 sealed input의 actual result는 아래였다.

| 항목 | 값 |
|---|---:|
| rows with `violation_type` field | `2105` |
| rows missing field | `0` |
| non-null `violation_type` population | `624` |
| core source family population | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7` |
| gate result | `pass` |

### 4-3. `violation_flags` fallback 제한

`violation_flags`는 generic proxy path가 아니라 closed allowlist fallback으로만 허용했다.

| flag | promoted source family |
|---|---|
| `BODY_COLLAPSES_TO_ACQUISITION` | `ACQ_DOMINANT` |
| `BODY_LOSES_ITEM_CENTRICITY` | `BODY_LACKS_ITEM_SPECIFIC_USE` |

`SECTION_COVERAGE_DEFICIT`, `INTERACTION_LIST_DUPLICATION`, `CROSS_LAYER_RAW_COPY` 같은 flag는 source axis primary promotion에 쓰지 않는다.

### 4-4. Section naming seal

section-derived family는 `SECTION_*` namespace를 강제했다.

현재 sealed run에서 실제로 관측된 primary section family는 아래 둘뿐이었다.

- `SECTION_FUNCTION_NARROW = 1433`
- `none = 672`

다만 설계상 허용된 primary section family는 아래 6개 전체다.

- `SECTION_BODY_LACKS_ITEM_SPECIFIC_USE`
- `SECTION_FUNCTION_NARROW`
- `SECTION_IDENTITY_ONLY`
- `SECTION_ACQ_DOMINANT`
- `SECTION_LAYER4_ABSORPTION`
- `none`

즉 구현이 두 family만 방출하도록 좁혀진 것은 아니다. 이번 sealed data에서는 나머지 4개 family가 `0` rows였고, 실제 관측값으로는 `SECTION_FUNCTION_NARROW`와 `none`만 발동했다.

---

## 5. Baseline Freeze

기존 staged/static closeout 위에 observer patch를 올리기 전에 baseline freeze를 먼저 만들었다.

산출물:

- `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/phase_d_signal_preservation_baseline.json`
- `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/phase_d_signal_preservation_baseline.md`

Freeze snapshot:

| 축 | 값 |
|---|---:|
| row_count | `2105` |
| runtime_state | `active 2084 / silent 21` |
| runtime_path_total | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| quality split | `strong 1316 / adequate 0 / weak 768` |
| source preservation target | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481` |
| hard block candidate | `0` |
| writer_role | `observer_only` |

Hash snapshot:

| 대상 | SHA256 |
|---|---|
| staged Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| workspace Lua | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| existing structural row artifact | `b41a123d9ef2a2821ff89e0724d714c5d87a5ffd78c4813b6727b42486464072` |
| existing structural summary artifact | `967b341392ec56bac76164e23ccfb62c87f859c1dd45ce8cd260a322b0687837` |
| Phase 0 sealed Lua reference | `9c5ceebea334277cb9b235e67fdfed8f2089d3eb1b7a2519ada424be11945ee9` |

중요한 점은 baseline freeze가 기존 artifact를 교체하지 않았다는 것이다. 이 단계는 이후 validator가 additive-only 계약을 증명하기 위한 anchor다.

이 baseline/read model 선택과 함께, 기존 `report_layer3_body_plan_structural_reclassification.py`는 이번 세션의 primary write target이 아니었다. 기존 structural row/summary artifact hash가 end-to-end unchanged로 유지된 것은 이 implementation choice와 같은 선상에서 읽어야 한다.

---

## 6. Additive Artifact Generation

신규 observer artifact는 아래 경로에 분리 생성했다.

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/
```

생성한 핵심 산출물:

- `body_plan_signal_preservation.2105.jsonl`
- `body_plan_signal_preservation.source_distribution.json`
- `body_plan_signal_preservation.section_distribution.json`
- `body_plan_signal_preservation.crosswalk.json`

### Source distribution result

| 축 | 값 |
|---|---:|
| total | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481` |
| active | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1460` |
| silent | `none 21` |
| target check | `match` |

Existence/no-overwrite target actual observed counts:

| family | source primary | source secondary | replaced by other section |
|---|---:|---:|---:|
| `IDENTITY_ONLY` | `0` | `0` | `0` |
| `ACQ_DOMINANT` | `0` | `0` | `0` |

Closed allowlist activation actual observed counts:

| path | rows |
|---|---:|
| allowlisted `violation_flags -> source_signal_primary` activation | `0` |
| allowlisted `violation_flags -> source_signal_secondary` activation | `0` |

### Section distribution result

| 축 | 값 |
|---|---:|
| total | `SECTION_FUNCTION_NARROW 1433 / none 672` |
| active | `SECTION_FUNCTION_NARROW 1433 / none 651` |
| silent | `none 21` |

### Crosswalk result

| 축 | 값 |
|---|---:|
| `source_only` | `67` |
| `section_only` | `876` |
| `coexist` | `557` |
| `dual_none` | `605` |
| newly observed structural-only rows | `876` |
| `would_have_overwritten_count` | `0` |

이번 결과에서 source-preservation target `617 / 7 / 1481`은 정확히 보존됐고, old artifact가 단일 `FUNCTION_NARROW` view로 뭉개던 row들이 `source_only`, `section_only`, `coexist`로 분해됐다.

---

## 7. Design Read Artifacts

계획 문서에 적어 둔 설계 산출물도 실제 구현 기준으로 같이 만들었다.

- `source_signal_source_map.md`
- `signal_model_design.md`
- `section_signal_derivation_rule.md`

이 문서들이 고정하는 내용은 아래다.

- 기존 observer bug의 read point
- `violation_type` vs `violation_flags` 역할 분리
- closed allowlist fallback
- `source_signal_*` / `section_signal_*` canonical row field
- origin object schema
- `SECTION_*` namespace rule
- `signal_overlap_state` 값 공간

즉 이번 세션은 코드만 추가한 게 아니라, 구현이 어떤 model authority 위에서 읽히는지도 같이 봉인했다.

---

## 8. Validator와 Crosscheck

### 8-1. Observer integrity validator

산출물:

- `phase_d_signal_preservation_validation_report.json`
- `phase_d_signal_preservation_validation_report.md`

overall status:

```text
pass
```

pass 항목의 핵심은 아래였다.

- row count unchanged
- `writer_role = observer_only`
- new row artifact에 `quality_state`, `publish_state` 없음
- runtime_state counts unchanged
- runtime_path_total unchanged
- publish split unchanged
- quality split unchanged
- staged/workspace Lua hash unchanged
- existing structural artifact hash unchanged
- source target check allowed and non-error
- `IDENTITY_ONLY`, `ACQ_DOMINANT` no-overwrite preserved
- source/section/crosswalk/silent consistency pass

실측치 기준으로 `IDENTITY_ONLY`, `ACQ_DOMINANT`는 둘 다 `source primary 0 / source secondary 0 / replaced_by_other_section 0`이었다. 따라서 이번 sealed run에서 validator의 existence/no-overwrite pass는 실제 replacement evidence가 없는 `0-row preserved` 상태를 뜻한다.

### 8-2. Lossy old artifact crosscheck

산출물:

- `signal_preservation_crosscheck_report.json`

핵심 결과:

| 항목 | 값 |
|---|---:|
| upstream `violation_type` distribution | `617 / 7 / 1481` |
| new source distribution | `617 / 7 / 1481` |
| count verification | `match` |
| implementation error rows | `0` |
| lossy old artifact row count | `1500` |

`lossy_old_artifact_row_count 1500`의 구성식은 아래와 같다.

```text
section_only 876 + coexist 557 + source_only 67 = 1500
```

이 수치는 old artifact와 new artifact 사이에서 axis read 결과가 달라진 row의 합이다. `dual_none 605`는 old/new view 모두 실질적으로 empty read로 남으므로 이 lossy count에서 제외한다.

대표적인 row shape는 세 가지였다.

- old artifact가 `FUNCTION_NARROW`였지만 새 artifact에서는 `section_only`
- old artifact가 `FUNCTION_NARROW`였지만 새 artifact에서는 `coexist`
- old artifact가 `none`이었지만 새 artifact에서는 `source_only`

즉 crosscheck는 “새 observer lane이 더 복잡해졌다”가 아니라 “old observer lane이 lossy였고, 새 lane이 source/section을 분리 보존한다”는 증거로 읽힌다.

---

## 9. Diagnostic Packet

최종 diagnostic packet도 생성했다.

산출물:

- `phase_d_signal_preservation_diagnostic_packet.json`

overall status:

```text
pass
```

이 packet은 아래를 묶는다.

- baseline freeze snapshot
- source distribution
- section distribution
- crosswalk
- explicit family preservation check
- structural-only newly observed set
- non-writer seal confirmation
- crosscheck verification

이 packet은 compose repair instruction이나 runtime adoption 변경을 선언하지 않는다. 다음 observer/decision round가 current lane을 읽을 수 있게 summary packet만 제공한다.

---

## 10. Tests

이번 세션에서 마지막으로 다시 돌린 focused test command는 아래였다.

```text
python -B -m unittest Iris.build.description.v2.tests.test_report_layer3_body_plan_signal_preservation Iris.build.description.v2.tests.test_phase_d_signal_preservation_supporting_reports
```

결과:

```text
Ran 4 tests in 0.049s
OK
```

테스트 범위는 아래를 포함한다.

- `violation_type` gate 분기
- source/section axis 분리
- allowlist fallback
- baseline / validator / crosscheck / diagnostic packet supporting reports

계획 `v0.3`의 Phase 3 gate와 실제 test/evidence mapping은 아래처럼 읽는다.

| Scope | Evidence |
|---|---|
| missing field gate | `test_phase1_gate_detects_missing_and_empty_violation_type_population` |
| empty population gate | `test_phase1_gate_detects_missing_and_empty_violation_type_population` |
| upstream signal gap handoff | `test_phase1_gate_returns_handoff_when_core_families_are_absent` |
| `coexist` | `test_build_signal_preservation_report_separates_source_and_section_axes`의 `Base.SourceCoexist` |
| same-surface source/section coexist | `test_build_signal_preservation_report_separates_source_and_section_axes`의 `Base.FlagFallback` |
| `dual_none` | `test_baseline_validation_crosscheck_and_packet_flow`의 synthetic `Base.B` |
| `source_only` | dedicated unit row는 없고, sealed-run artifact/crosswalk evidence `67` rows로 확인 |
| `section_only` | dedicated unit row는 없고, sealed-run artifact/crosswalk evidence `876` rows로 확인 |

즉 4개 테스트가 모든 scope를 1:1로 분리해서 가지는 구조는 아니었다. unit test는 gate, coexist, same-surface coexist, dual_none과 supporting report flow를 직접 덮고, `source_only` / `section_only`는 실제 sealed-run artifact와 crosswalk output에서 관측 증거로 닫았다.

---

## 11. Top Docs Reflection

세션 후반에는 current state를 top docs에도 반영했다.

초기 walkthrough draft 이후, top docs reflection은 search snippet이 아니라 실제 로컬 본문 기준으로 다시 확인했다.

| 문서 | 반영 위치 | 의미 |
|---|---|---|
| `docs/DECISIONS.md` | `2026-04-24` decision | 이번 round를 `closed_with_observer_patch_applied`로 채택 |
| `docs/ARCHITECTURE.md` | `11-59` | additive dual-axis observer lane 정의 |
| `docs/ROADMAP.md` | `Addendum #25` | 이번 round closeout과 immediate next 없음 기록 |

Re-verified local read points:

- `DECISIONS.md`의 `2026-04-24 — Iris DVF 3-3 Phase D observer signal preservation patch round는 additive observer lane으로 닫는다`
- `ARCHITECTURE.md`의 `11-59. Phase D signal preservation patch is an additive dual-axis observer lane over the sealed staged baseline`
- `ROADMAP.md`의 `#25. 2026-04-24 Addendum — Iris DVF 3-3 Phase D observer signal preservation patch round closeout`

ROADMAP numbering continuity도 로컬 본문에서 다시 확인했다.

- `#23. 2026-04-23 Addendum — Iris DVF 3-3 CDPCR-AS Branch B closeout`
- `#24. 2026-04-23 Addendum — Iris DVF 3-3 EDPAS authority seal closeout`
- `#25. 2026-04-24 Addendum — Iris DVF 3-3 Phase D observer signal preservation patch round closeout`

중요한 점은 세 문서 모두 이번 round를 기존 staged/static closeout 위의 additive observer lane으로만 읽도록 적었다는 것이다. `ready_for_in_game_validation` 자체는 바꾸지 않았다.

Closeout wording `closed_with_observer_patch_applied`는 계획 `v0.3`의 failure-branch wording이 아니라, 이번 closeout 시점에 `DECISIONS.md`와 `ROADMAP.md`에서 decision-level로 봉인한 pass-closeout wording이다. 즉 provenance는 plan predeclare가 아니라 top-doc closeout declaration에 있다.

---

## 12. 이번 세션에서 일부러 하지 않은 일

이번 세션은 아래를 의도적으로 건드리지 않았다.

- 기존 `body_plan_structural_reclassification.2105.jsonl` 수정
- 기존 `body_plan_structural_reclassification.2105.summary.json` 수정
- staged Lua 재생성
- workspace Lua 변경
- rendered text 변경
- `quality_state`, `publish_state` 변경
- compose authority 변경
- runtime-side rewrite
- same-build compose repair
- `quality_baseline_v4 -> v5` cutover
- deployed closeout / ready_for_release 선언
- manual in-game validation
- source expansion execution

즉 이번 세션은 observer patch lane만 닫았지, runtime writer lane을 다시 열지 않았다.

---

## 13. Current Read

이번 세션 이후 current read는 아래처럼 정리된다.

1. 기존 staged/static closeout은 그대로 유지된다.
2. source-side explicit family와 section-derived family는 새 additive observer lane에서 분리 보존된다.
3. source preservation target `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`은 `match`다.
4. observer integrity validator와 diagnostic packet은 둘 다 `pass`다.
5. immediate next는 없다.
6. global current-state에서 남아 있는 별도 pending은 여전히 manual in-game validation QA round다.

한 줄로 요약하면:

> 이번 세션은 Phase D observer signal preservation 문제를 additive observer lane으로 닫았고, 기존 sealed staged baseline은 그대로 유지했다.
