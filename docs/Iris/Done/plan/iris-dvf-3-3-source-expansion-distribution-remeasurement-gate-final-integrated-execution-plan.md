# Iris DVF 3-3 Source Expansion Distribution Remeasurement Gate Final Integrated Execution Plan

> 상태: FINAL v1.2  
> 기준일: 2026-04-19  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-execution-plan.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-walkthrough.md`, `docs/Iris/Done/iris-dvf-3-3-role-fallback-hollow-followup-walkthrough.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-terminalization-walkthrough.md`  
> authority input: `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`, `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json`, `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json`, `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_summary.json`, `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_terminal_status.json`  
> 목적: source expansion round closeout 이후 5축 분포 delta를 fresh recompute 기준으로 계측하고 `PASS / REVIEW / DRIFT`로 adjudication한 뒤 future semantic decision input으로 넘기는 SDRG(Source-Expansion Distribution Remeasurement Gate)의 responsibility boundary, baseline chain, artifact contract를 고정한다.  
> 실행 상태: planning only. v1.2는 latest current handoff authority 정합성, round-level exit status, baseline lifecycle, reporting term definition까지 정리한 final sealed plan이다.

> 이 문서는 source expansion execution을 소유하지 않는다.  
> SDRG는 source expansion round가 닫힌 뒤 동작하는 offline advisory observer gate다.

---

## 0. 전제 봉인

### 0-1. 이 라운드의 정체성

이 작업은 **authority 재계측 라운드**다. 설명을 더 채우거나 본문을 수정하는 작업이 아니다.

- source expansion = coverage 작업
- 재측정 = authority 작업
- 둘은 분리된 라운드이며, 섞이면 drift가 발생한다

### 0-2. Gate 정체성 한 줄 봉인

> SDRG(Source-Expansion Distribution Remeasurement Gate)는 source expansion round 종료 후 5축 분포의 delta를 계측하고 보고하는 offline advisory observer gate다. enforcement authority 없음, runtime 노출 없음, pipeline mutate 없음.

### 0-3. 전역 금지선

이 라운드 어느 단계에서도 아래는 절대 금지다.

- facts 슬롯 확장
- compose 외부 repair stage 재도입
- `surface_quality`, `surface_active`, `runtime_only` 등 신규 상태 축 도입
- structural feedback을 같은 build 내 즉시 re-compose로 되감기
- terminalized lane(`identity_fallback`, `role_fallback hollow`) 재개방
- 30-cap frozen budget 위반
- single writer 원칙(quality/publish decision stage) 침범
- SDRG를 enforcement gate로 승격
- SDRG 결과를 runtime consumer에 노출
- baseline을 Lua bridge에 export
- `3-4` 상세 흡수

### 0-4. Staging root와 구현 경계

새 gate 산출물은 아래 루트로 고정한다.

- `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/`

이 루트는 source expansion round output을 **읽는 observer root**다.  
source expansion round의 batch artifact와 terminal status를 대체하지 않는다.

권장 하위 디렉터리:

- `phase1_baseline_freeze/`
- `phase2_3_trigger_prerequisites/`
- `phase4_fresh_recompute/`
- `phase5_distribution_delta/`
- `phase6_semantic_decision/`
- `phase6_5_retroactive_backfill/`
- `closeout/`
- `group_b_pre_wiring/`

---

## 1. Phase 1 — Baseline Authority Freeze

**목적:** 이후 모든 delta 계산의 비교 기준을 잠근다.

### 1-1. baseline은 2층으로 고정한다

Phase 1은 baseline을 하나의 "현재 값"으로 뭉개지 않는다.  
반드시 아래 두 레이어를 함께 기록한다.

- `pre-expansion comparison baseline`
- `current handoff authority`

운영 규칙:

- SDRG의 delta 계산 기준은 **`current handoff authority`** 다.
- `pre-expansion comparison baseline`은 historical comparison reference일 뿐, current delta 기준이 아니다.
- 두 레이어를 같은 "현재 값" 레이블 아래 합치지 않는다.

### 1-2. 동결 대상 (5축 baseline)

| 축 | baseline layer | 값 | 출처 |
|---|---|---|---|
| Audit | `pre-expansion comparison baseline` | `2105 rows`, `active 2084 / silent 21`, `cluster_summary 1440 / identity_fallback 617 / role_fallback 48` | `5-y0` body-role closeout 직후 facts stage 비교 기준 |
| Audit | `current handoff authority` | `2105 rows`, `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` | `identity_fallback_terminal_handoff.json` |
| Overlay | `current handoff authority` | `quality_baseline_v4` 기준, three-axis contract 교차 분포 | decisions stage |
| Lint | `current handoff authority` | `BODY_LACKS_ITEM_SPECIFIC_USE 617`, `SINGLE_FUNCTION_LOCK 27` | style linter |
| Quality | `current handoff authority` | `strong 1316 / adequate 0 / weak 768`, `quality_ratio 0.6315` | compose semantic_quality |
| Publish | `current handoff authority` | `internal_only 617 / exposed 1467` | quality/publish decision |

보조 provenance 메모:

- `source_coverage_runtime_summary.json`의 `cluster_summary 1275 / identity_fallback 718 / role_fallback 100 / direct_use 12`는 **source-coverage integrated intermediate snapshot** 이다.
- 이 값은 SDRG의 `current handoff authority`가 아니라 upstream provenance reference로만 남긴다.
- current handoff authority의 canonical read point는 latest terminal handoff artifact다.

active/silent split 메모:

- latest `identity_fallback_terminal_handoff.json`은 `runtime_row_count`와 `runtime_path_counts`를 canonical current handoff field로 제공한다.
- current handoff authority 단계에서 `active/silent` split은 canonical field가 아니다.
- retroactive first application에서 active/silent split이 필요하면 `Phase 6.5 recoverability precheck`가 복원 가능 여부를 먼저 판정한다.

status/handoff 역할 메모:

- `terminal_status.json`은 lane closeout authority다.
- `terminal_handoff.json`은 downstream read authority다.

### 1-3. 책임 경계와 gate 비중첩 선언

Phase 1에서 아래 경계를 함께 봉인한다.

- SDRG는 `T-Gates(T1~T4)`와 중복되지 않는다.
- SDRG는 `Q-Gates(Q1~Q5)`와 중복되지 않는다.
- Q-Gates는 evidence pipeline 전용으로 봉인돼 있으며 SDRG는 Q-Gate 판정에 영향을 주지 않는다.

### 1-4. terminalized lane 읽기 규칙

baseline은 planning artifact가 아니라 current-state authority다.

- `identity_fallback`는 `identity_fallback_terminal_status.json` 기준으로 읽는다.
- `role_fallback hollow`는 `role_fallback_hollow_terminal_status.json` 기준으로 읽는다.
- closed lane을 열린 debt처럼 읽지 않는다.

### 1-5. baseline version chain 분리

`SDRG baseline version`과 `quality baseline version`은 같은 namespace가 아니다.

- SDRG baseline version: `pre_expansion_baseline_vN`
- quality baseline version: `quality_baseline_vN`

두 version tag는 동일 artifact 안에 공존할 수 있지만, 승계 규칙은 따로 가진다.

- SDRG baseline 승계는 `pre_expansion_baseline_vN -> pre_expansion_baseline_vN+1`
- quality baseline 승계는 `quality_baseline_vN -> quality_baseline_vN+1`
- 둘 사이의 carry 여부는 `baseline_carry_decision_vN.json`이 별도 판정한다.
- `pre-expansion comparison baseline`은 최초 freeze 이후 immutable historical reference로 고정되며, `vN` chain에서 계속 참조되지만 자체는 승계되지 않는다.
- 각 round의 comparison baseline은 그 round 시작 시 별도로 freeze한다.

### 1-6. 산출물 contract

- `phase1_baseline_freeze/pre_expansion_baseline_v0.json`
- `phase1_baseline_freeze/baseline_authority_snapshot.md`

`pre_expansion_baseline_v0.json` 최소 필드:

- `baseline_version`
- `snapshot_timestamp`
- `source_round_id`
- `comparison_baseline`
- `current_handoff_authority`
- `overlay_baseline`
- `lint_baseline`
- `quality_baseline`
- `publish_baseline`
- `closed_lane_read_points`
- `baseline_namespace_chain`

### 1-7. 종료 조건

- "무엇과 비교하느냐" 논쟁이 사라진다.
- 모든 후속 delta가 `current handoff authority`를 기준으로 계산된다.
- `pre-expansion comparison baseline`은 historical reference로만 남는다.

### 1-8. Hold

- baseline 확정 전 SDRG trigger 착수
- planning 문서를 baseline authority로 사용하는 것

---

## 2-3. SDRG Trigger Prerequisites — Source Expansion Closeout는 별도 owner가 가진다

**목적:** SDRG가 source expansion execution을 소유하지 않는다는 점을 기계적으로 고정한다.

### 2-3.1. upstream owner 분리

source expansion inventory 정리, batch execution, batch closeout은 **별도 Source Expansion Round Execution Plan** 의 책임이다.  
SDRG는 그 round가 닫힌 뒤에만 진입한다.

즉 이 문서는 아래를 정의하지 않는다.

- expansion inventory 작성
- batch 우선순위 결정
- source patch 작성
- source expansion batch closeout

위 항목은 source expansion round 문서가 담당한다.

### 2-3.2. current upstream execution metadata

현재 남은 source expansion 실행 범위는 upstream metadata로만 기록한다.

- `bucket_1_existing_cluster_reusable`: `11`
- `bucket_2_net_new_cluster_required`: `599`

이 수치는 SDRG가 실행 범위를 결정하는 값이 아니라, Phase 5에서 `expected expansion scope`를 설명할 때 참조하는 upstream context다.

### 2-3.3. Phase 4 진입 전 필수 closeout artifact

SDRG는 아래 artifact가 존재할 때만 Phase 4로 진입한다.

- `source_expansion_round_terminal_status.json` 또는 동등한 terminal status artifact
- `source_expansion_execution_inventory.json` 또는 동등한 upstream execution inventory
- `source_expansion_subset_manifest.json` 또는 동등한 upstream subset manifest
- expansion batch closeout log bundle

legacy round처럼 표준 terminal artifact가 없다면, SDRG 진입 전에 아래 adapter artifact를 먼저 만든다.

- `phase2_3_trigger_prerequisites/source_expansion_closeout_authority.json`

이 adapter는 legacy closeout artifact를 current SDRG trigger contract로 정렬하는 전용 summary다.

### 2-3.4. 산출물 contract

- `phase2_3_trigger_prerequisites/source_expansion_trigger_prerequisites.json`
- `phase2_3_trigger_prerequisites/source_expansion_closeout_authority.json`
- `phase2_3_trigger_prerequisites/expected_expansion_scope_reference.json`

`source_expansion_trigger_prerequisites.json` 최소 필드:

- `baseline_version`
- `upstream_owner_document`
- `required_closeout_artifacts`
- `trigger_status`
- `expected_expansion_scope`

### 2-3.5. 종료 조건

- SDRG가 source expansion round를 소유하지 않는다는 점이 문서상 명확해진다.
- Phase 4 진입 authority가 batch 실행 서술이 아니라 closeout artifact 존재 여부로 기계화된다.

---

## 4. Phase 4 — Fresh Recompute

**목적:** source expansion 결과를 임시 수선이 아닌 **전체 재계산**으로 읽는다.

### 4-1. 핵심 원칙

- structural feedback은 fresh recompute 원칙으로 next-build 입력만 생성한다.
- "보이는 문제를 즉석에서 re-compose해서 덮는 것"이 아니다.
- SDRG는 compose 외부 repair gate가 아니다.
- recompute는 기존 pipeline contract 안에서 수행되고, SDRG는 그 산출물을 adjudication input으로 읽는다.

### 4-2. 실행 순서

1. facts/decisions 입력 재생성
2. decisions overlay 재생성
3. compose 재실행
4. rendered / preview / regression pack 재생성
5. audit / lint / publish report 재생성

### 4-3. 산출물 contract

- `phase4_fresh_recompute/post_expansion_recompute_manifest.json`
- `phase4_fresh_recompute/post_expansion_rendered_snapshot.json`
- `phase4_fresh_recompute/post_expansion_regression_pack.json`
- `phase4_fresh_recompute/post_expansion_remeasurement_v0.json`

`post_expansion_remeasurement_v0.json`은 Phase 1 baseline과 동일한 5축 스키마를 따른다.

### 4-4. 종료 조건

- "수선된 결과"가 아니라 "재계산된 결과"가 확보된다.
- 이후 모든 판정은 이 recompute 산출물 기준으로만 이뤄진다.

### 4-5. Hold

- recompute 없이 delta 계산 착수
- recompute 중 lint rule 수정
- SDRG가 compose/normalizer 재실행을 유발하는 것

---

## 5. Phase 5 — 5축 분포 재측정 및 Drift Adjudication

**목적:** source expansion 뒤 분포 변화를 정량화하고, 개선인지 drift인지 판정한다.

측정과 판정은 같은 입력 위에서 이뤄지므로 한 phase로 묶는다.

### 5-1. 재측정 5축

**Audit 분포**

- `dvf_3_3_facts_full.jsonl` row count
- `fact_origin` breakdown
- `runtime_state` split
- `decision_use_source` 또는 동등한 path breakdown

`decision_use_source` 정의:

- `decision_use_source`는 일부 integrated runtime summary가 제공하는 **reporting-only path breakdown field** 다.
- state model 축이 아니라, decision이 어떤 source/path 계열에서 왔는지 집계하는 관측용 필드다.
- 해당 field가 없으면 동등한 `path breakdown` 또는 `decision source breakdown` field로 대체한다.

**Overlay 분포**

- decisions overlay row count
- three-axis contract 교차 분포
- `identity_fallback -> cluster_summary / direct_use / ...` 이동량
- `semantic_quality`가 overlay derived/cache field로 올라간 구조 전제 유지

**Lint 분포**

- `BODY_LACKS_ITEM_SPECIFIC_USE`
- `SINGLE_FUNCTION_LOCK`
- `LAYER4_ABSORPTION` hard block 잔량
- 신규 hard fail 여부

중요: SDRG는 lint rule을 읽기만 한다. lint rule 수정 권한은 없다.

**Quality 분포**

- `strong / adequate / weak` 비율
- `quality_ratio`
- `generated::weak / missing::*` counts
- exposed subset quality ratio

**Publish 분포**

- `internal_only / exposed` split
- quality ratio 변화와 publish 변화의 상관
- source expansion이 exposed 증가를 만들었는지, internal_only만 늘렸는지

### 5-2. 판정 등급

| 등급 | 기준 |
|---|---|
| `PASS` | delta가 expansion의 예상 범위 안 |
| `REVIEW` | delta가 예상 범위 밖이지만 expansion 내용으로 설명 가능 |
| `DRIFT` | delta가 expansion으로 설명되지 않음. 별도 원인 조사 round 필요 |

판정은 5축 각각 독립적으로 부여한다.  
단일 마스터 점수로 압축하지 않는다.

### 5-3. 축별 rubric

아래 rule은 판정 rubric이며, 마스터 점수가 아니다.

**Audit**

- row count delta가 expected expansion scope 대비 `+10%` 초과면 `REVIEW`
- row count delta가 음수면 `DRIFT`

**Overlay**

- expansion 완료 후 `identity_fallback` count가 증가하면 `REVIEW`
- expected target lane 감소가 설명 없이 멈추면 `DRIFT`

**Lint**

- 신규 hard fail `1건 이상`이면 `DRIFT`
- hard fail 증가 `0`이고 warn 증가 없음이면 `PASS`

**Quality**

- weak 절대수 감소 없이 strong만 증가하면 `PASS`
- weak가 expansion 대상 수보다 더 증가하면 `DRIFT`

**Publish**

- internal_only와 exposed가 설명 가능한 비율로 같이 움직이면 `PASS`
- exposed만 단독 감소하고 explanation이 없으면 `DRIFT`

### 5-4. 최소 통과 게이트

1. hard fail 증가 `0`
2. regression rejected 증가 `0`
3. publish 증가가 있으면 quality 악화 없이 설명 가능
4. weak 증가가 있으면 source expansion 과도기인지 contract drift인지 구분 가능
5. lint가 줄지 않았는데 exposed만 증가하면 `REVIEW` 이상 부여

terminalized lane 재개방 금지선은 Phase 0-3에서 이미 봉인되므로, 최소 통과 gate 항목으로 중복 기재하지 않는다.

### 5-5. 산출물 contract

- `phase5_distribution_delta/post_source_expansion_audit_distribution.json`
- `phase5_distribution_delta/post_source_expansion_quality_distribution.json`
- `phase5_distribution_delta/post_source_expansion_overlay_distribution.json`
- `phase5_distribution_delta/post_source_expansion_lint_distribution.json`
- `phase5_distribution_delta/post_source_expansion_publish_distribution.json`
- `phase5_distribution_delta/distribution_delta_report_v0.json`
- `phase5_distribution_delta/baseline_carry_decision_v0.json`

`distribution_delta_report_v0.json` 최소 필드:

- `baseline_version`
- `post_expansion_version`
- `axis_deltas`
- `axis_adjudication`
- `round_exit_status`
- `expected_explanation`
- `rubric_applied`
- `gate_findings`

`baseline_carry_decision_v0.json` 최소 필드:

- `baseline_version`
- `quality_baseline_version`
- `candidate_next_baseline`
- `carry_decision`
- `carry_reason`
- `followup_round_required`

### 5-6. 종료 조건

- "늘었다/줄었다"가 아니라 각 축의 delta가 수치로 고정된다.
- 각 변화가 `PASS / REVIEW / DRIFT` 중 하나로 분류된다.

### 5-7. Round-level exit status

축별 판정은 독립적으로 유지하되, round closeout을 위해 아래 exit rule을 함께 기록한다.

```text
any DRIFT -> round_exit_status = DRIFT
no DRIFT, any REVIEW -> round_exit_status = REVIEW
all PASS -> round_exit_status = PASS
```

운영 규칙:

- `round_exit_status`는 마스터 점수가 아니라 closeout status다.
- `round_exit_status = DRIFT`이면 `immediate_next_round_planned = true`를 자동으로 세팅한다.
- 이때 다음 round의 기본 scope는 `DRIFT`가 발생한 축을 대상으로 한 원인 조사 round다.
- `round_exit_status = PASS` 또는 `REVIEW`이면 immediate next round는 자동으로 열지 않는다. 별도 명시가 있어야 한다.

---

## 6. Phase 6 — Semantic Decision Gate

**목적:** 재측정 결과를 본문 수정으로 바로 돌리지 않고, **future semantic decision 입력**으로 넘긴다.

### 6-1. 왜 별도 phase인가

semantic axis 반영은 recompute 결과를 보고 자동 반영하는 것이 아니라 **명시적 의사결정 단계**다.

- Pulse는 capability를 제공한다.
- 제품적 정책은 하위 모듈이 가진다.
- Iris는 오프라인 산출물 소비 구조다.

따라서 분포 재계산과 정책 판정을 한 덩어리로 뭉개면 안 된다.

### 6-2. Phase 3A guardrail과의 관계

SDRG Phase 6은 semantic axis 반영 여부에 대한 **decision input**만 생성한다.  
three-axis contract migration의 `Phase 3A guardrail gate`는 별도 gate이며 SDRG가 그것을 trigger하거나 소비하지 않는다.

- SDRG Phase 6 산출물은 future `Phase 3A` 선행 입력이 될 수 있다.
- 그러나 그 연결은 `Phase 3A` 계획 문서에서 별도로 선언돼야 한다.

### 6-3. 판단 질문

- weak candidate 일부를 semantic axis에 승격할 것인가, backlog signal로 남길 것인가
- net-new cluster reopen subset을 더 열 것인가
- publish split 조정이 필요한가
- exposed 기준을 강화해야 하는가
- `DRIFT` 판정 항목에 대해 별도 원인 조사 round를 열 것인가

### 6-4. 산출물 contract

- `phase6_semantic_decision/semantic_decision_input_packet.json`
- `phase6_semantic_decision/semantic_decision_review.md`
- 필요 시 `phase6_semantic_decision/decisions_md_patch_proposal.md`

`semantic_decision_input_packet.json` 최소 필드:

- `delta_report_ref`
- `axis_signal_summary`
- `candidate_semantic_updates`
- `decision_required_items`

### 6-5. 종료 조건

- semantic 반영 여부가 "분위기상"이 아니라 decision artifact로 닫힌다.
- `DRIFT` 항목에 대한 처리 경로가 명시된다.

### 6-6. Hold

- 이 단계에서 본문 compose 재실행
- decision 없이 다음 단계 착수

---

## 6.5. Phase 6.5 — Retroactive Backfill First Application

**목적:** Option C 원칙에 따라 SDRG의 첫 적용 사례로 `identity_fallback 617` backfill artifact를 생성한다.  
이 단계는 optional이 아니라 **current SDRG round의 필수 mainline** 이다.

### 6.5-1. 위치 원칙

backfill artifact는 문서 반영보다 먼저 생성돼야 한다.

- backfill 없는 상태에서 `DECISIONS.md`에 backfill 원칙을 추가하지 않는다.
- "구현 -> 문서 순서" 원칙을 유지한다.
- 모든 backfill artifact에 `retroactive = true`를 명시한다.

### 6.5-2. 축별 재구성 가능성 사전 확인

backfill 실행 전 아래 선판정 artifact를 만든다.

- `phase6_5_retroactive_backfill/retroactive_axis_recoverability_precheck.json`

각 축은 아래 셋 중 하나로 먼저 분류한다.

- `recoverable`
- `partial_recoverable`
- `unrecoverable`

이 precheck 없이 backfill 본 실행에 들어가지 않는다.

### 6.5-3. backfill 핵심 원칙

- terminalized lane 재개방이 아니라 **소급 관측 artifact 생성** 이다.
- runtime path / publish split mutate 금지
- backfill이 `scope_policy_override_round` / `runtime_adoption_round` trigger가 되어서는 안 됨
- 재구성 불가능한 축은 `unrecoverable`로 남긴다

### 6.5-4. 산출물 contract

- `phase6_5_retroactive_backfill/retroactive_axis_recoverability_precheck.json`
- `phase6_5_retroactive_backfill/pre_expansion_baseline_v0_retroactive.json`
- `phase6_5_retroactive_backfill/post_expansion_remeasurement_v0_retroactive.json`
- `phase6_5_retroactive_backfill/distribution_delta_report_v0_retroactive.json`
- `phase6_5_retroactive_backfill/baseline_carry_decision_v0_retroactive.json`

### 6.5-5. 종료 조건

- SDRG first-application backfill artifact가 supporting evidence로 생성된다.
- 문서 반영이 backfill artifact를 참조할 수 있다.

---

## 7. Phase 7 — 문서 반영 및 Terminal Snapshot

**목적:** 이번 round를 다시 planning artifact로 읽지 못하게 current-state snapshot을 남기고 문서를 업데이트한다.

artifact 없는 문서 변경은 금지다.

### 7-1. DECISIONS.md 신규 항목 (3건)

1. `source expansion round 종료 후 SDRG를 돌린다`
2. `SDRG는 advisory observer이며 enforcement authority를 갖지 않는다`
3. `SDRG backfill artifact는 terminalized lane을 재개방하지 않는다`

### 7-2. ROADMAP.md 반영 원칙

ROADMAP 반영은 원문 추적성을 해치지 않도록 아래 규칙을 따른다.

- `5-y0 Next`의 기존 `audit / overlay / lint` 분포 재측정 항목은 원문을 보존한 채 Done으로 승격한다.
- 추가된 `quality / publish` 두 축은 별도 확장 line으로 기록한다.
- 하나의 문장으로 덮어써서 `3축 -> 5축` 원문을 지우지 않는다.
- 신규 addendum: `Iris DVF 3-3 source-expansion distribution remeasurement gate`

### 7-3. ARCHITECTURE.md 신규 섹션

- SDRG 책임 분해
- pipeline side branch로서의 위치
- 4종 artifact chain 설명
- Philosophy / 3축 모델 정합성 기술

### 7-4. Terminal Snapshot 필수 항목

- baseline (Phase 1 출력)
- trigger prerequisites (Phase 2-3 출력)
- recompute output (Phase 4 출력)
- 분포 delta (Phase 5 출력)
- drift adjudication (Phase 5 출력)
- decision required items (Phase 6 출력)
- retroactive backfill refs (Phase 6.5 출력)
- immediate next round 존재 여부

### 7-5. 산출물 contract

- `closeout/source_expansion_remeasurement_terminal_status.json`
- `closeout/source_expansion_remeasurement_terminal_handoff.json`
- `closeout/source_expansion_remeasurement_closeout.md`

`source_expansion_remeasurement_terminal_status.json` 최소 필드:

- `baseline_ref`
- `trigger_prerequisites_ref`
- `recompute_ref`
- `axis_status_summary`
- `drift_adjudication_summary`
- `round_exit_status`
- `decision_required_items`
- `retroactive_backfill_ref`
- `immediate_next_round_planned`

`source_expansion_remeasurement_terminal_handoff.json` 최소 필드:

- `baseline_ref`
- `trigger_prerequisites_ref`
- `recompute_ref`
- `delta_report_ref`
- `carry_decision_ref`
- `retroactive_backfill_ref`
- `round_exit_status`
- `drift_investigation_scope`
- `next_round_open_conditions`

### 7-6. 종료 조건

- 다음 세션에서 "지금 이게 열린 queue인가, 이미 닫힌 authority인가"가 다시 논쟁되지 않는다.
- `distribution_delta_report_v0.json`과 `source_expansion_remeasurement_terminal_status.json`이 같은 `round_exit_status`를 기록한다.
- `round_exit_status = DRIFT`일 때만 `immediate_next_round_planned = true`가 자동 세팅된다.

### 7-7. Hold

- 기존 closed addendum 본문 수정
- `5-y0` 원문을 덮어써 추적성을 잃는 방식의 수정
- terminal snapshot 없이 세션 종료

---

## 8. Phase 8 — Group B 569 Pre-wiring

**목적:** Group B round가 열릴 때 SDRG가 자동 trigger될 수 있도록 사전 배선한다.  
이 단계는 **preferred precondition** 이지 enforcement authority가 아니다.

### 8-1. 준비 사항

- Group B round 시작 직전 pre-expansion baseline freeze 절차 문서화
- expansion closeout artifact -> SDRG trigger 연결 규칙 정의
- delta report의 expected expansion scope를 Group B `569` 기준으로 추정
- `quality_baseline_v4 -> v5` 승계 가능성 평가

### 8-2. 산출물 contract

- `group_b_pre_wiring/group_b_pre_wiring_runbook.md`
- `group_b_pre_wiring/sdrg_trigger_procedure.md`
- `group_b_pre_wiring/group_b_expected_delta_template.json`

### 8-3. 종료 조건

- Group B round 시작 전에 SDRG trigger wiring이 준비된다.
- 미완료일 경우에도 Group B round는 수동 baseline freeze 절차로 대체 착수 가능하다.

### 8-4. Hold

- Group B round 자체를 이 Phase에서 실행
- Group B item 선별 기준을 SDRG가 결정
- pre-wiring 단계에서 baseline carry를 미리 확정

---

## 9. Gate 요약

| 게이트 | 진입 조건 |
|---|---|
| Phase 1 진입 | 선행 조건 없음. 이 round의 시작점 |
| Phase 2-3 진입 | Phase 1 baseline freeze 완료 |
| Phase 4 진입 | source expansion round terminal status artifact 또는 동등 adapter authority 생성 완료 |
| Phase 5 진입 | Phase 4 recompute 산출물 확보 완료 |
| Phase 6 진입 | Phase 5 5축 재측정 완료, delta report 작성 완료 |
| Phase 6.5 진입 | Phase 6 decision artifact 생성 완료 |
| Phase 7 진입 | Phase 6.5 retroactive backfill artifact 생성 완료 |
| Phase 8 진입 | Phase 7 terminal snapshot 생성 완료 |

---

## 10. 성공 기준

### 최소 성공

- source expansion과 distribution remeasurement를 별도 round로 끝까지 분리한다.
- Phase 1 baseline이 comparison baseline과 current handoff authority를 분리해 고정된다.
- recompute 없이 delta를 재는 shortcut이 발생하지 않는다.
- 5축 delta report가 `PASS / REVIEW / DRIFT`로 axis별 판정을 남긴다.
- SDRG 결과가 runtime, Lua bridge, enforcement gate로 승격되지 않는다.
- terminalized lane이 재개방되지 않는다.
- backfill artifact가 `retroactive = true`로 문서 반영 전에 생성된다.

### 좋은 성공

- delta가 source expansion 범위와 설명 가능 범위 안에서 깔끔하게 정리된다.
- baseline carry 여부가 `v5 승계 / freeze / 별도 round` 중 하나로 문서화된다.
- Group B 569가 열릴 때 baseline freeze와 SDRG trigger가 기계적으로 이어질 수 있다.

### 실패

- `pre-expansion comparison baseline`과 `current handoff authority`를 다시 하나의 "현재 값"으로 합친다.
- SDRG 문서가 source expansion batch execution을 직접 소유한다.
- lint, quality, publish를 같은 단계에서 묶어 즉시 repair로 되감는다.
- backfill을 optional appendix로 밀어 문서 반영보다 뒤에 둔다.
- terminalized lane을 backfill 명목으로 reopen한다.
- Phase 7 terminal snapshot 없이 "대충 끝난 것처럼" 문서만 갱신한다.

---

## 11. Spot Check 메모

- `exec_subset_600` lineage artifact가 `DECISIONS 2026-04-15`의 `600 promote / residual 17` closeout authority와 일치하는지 spot check를 권장한다.
- 이 spot check는 SDRG 구현 전 validation memo이며, gate enforcement 권한은 아니다.
