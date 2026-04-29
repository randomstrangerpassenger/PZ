# Iris DVF 3-3 Identity Fallback Source Expansion Execution Plan

> 상태: Revised Draft v0.2  
> 기준일: 2026-04-14  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 동반 문서: `docs/iris-dvf-3-3-identity-fallback-source-expansion-scope-lock.md`  
> 입력 기준: `identity_fallback 617 Source Expansion 로드맵 v1.0` (2026-04-13)  
> canonical input: `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.json`  
> 목적: `identity_fallback 617`의 source evidence를 확충해 기존 facts 슬롯을 채우고, `cluster_summary` 중심 승격과 `publish_state` 회복을 현재 three-axis contract 안에서 순차 실행한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 실행 판정

이번 라운드는 production data expansion track이다.

- compose 재설계 라운드가 아니다.
- style 개선 라운드가 아니다.
- active/silent 의미 재정의 라운드가 아니다.
- quality/publish/runtime 축 구조를 다시 짜는 라운드가 아니다.

이번 라운드의 직접 목적은 다음 둘이다.

1. `identity_fallback`에 머무는 `617`개 row의 source evidence를 확보해 기존 facts 슬롯을 채운다.
2. 그 결과를 통해 `identity_fallback -> cluster_summary` 중심 경로 전환과 `internal_only -> exposed` 전환을 안정적으로 늘린다.

이번 라운드의 성공 기준은 문장 체감 품질이 아니라 아래 변화량으로 읽는다.

- `identity_fallback` 절대량 감소
- `cluster_summary` 또는 제한적 `direct_use` 증가
- `internal_only -> exposed` 전환 증가
- current exposed surface의 regression `0`

`direct_use`는 금지 경로가 아니지만 기본 추진 경로도 아니다.  
기본 승격 경로는 `cluster_summary`로 두고, item-specific 사실이 이미 충분해 새 슬롯 확장 없이 닫히는 subset만 제한적으로 `direct_use`를 허용한다.

---

## 1. Current Authority Baseline

current authority baseline은 아래처럼 고정한다.

| 항목 | 값 |
|---|---|
| total rows | 2105 |
| active | 2084 |
| silent | 21 |
| active origin | `cluster_summary 1440 / identity_fallback 617 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| handoff alignment | `617 / 617 / 617` |
| bucket split | `bucket_1 11 / bucket_2 599 / bucket_3 7` |

authority input artifact는 아래 4개를 함께 읽는다.

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_policy_isolation_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_summary.json`

선행 라운드 상태는 아래처럼 닫힌 것으로 전제한다.

- role_fallback hollow terminalized
- acquisition lexical round closed
- surface contract authority migration closed
- body-role round closed

즉 본 execution plan은 old `phase1_parallel` 재해석이 아니라 current `phaseE` handoff artifact를 기준으로 여는 새 source expansion round다.

---

## 2. 불변 원칙

- downstream 파이프라인은 `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime` 순서를 유지한다.
- facts 슬롯은 확장하지 않고, current slot 체계 안에서만 값을 채운다.
- `style linter`는 계속 advisory-only다.
- current authoritative compose path 이름은 `cluster_summary / identity_fallback / role_fallback / direct_use`로만 읽는다.
- `special_context` 같은 비-canonical 명칭은 planning memo일 수는 있어도 authoritative lane으로 승격하지 않는다.
- `publish_state` 승격은 source ownership 강화 뒤에만 검토한다.
- `bucket_3`는 current round에서 실행하지 않는다.
- `FUNCTION_NARROW`, `ACQ_DOMINANT` blanket isolation은 current round에서 reopen하지 않는다.
- `3-3`은 item-specific body를 유지하고 `3-4` 상세를 흡수하지 않는다.
- regression gate의 보호 대상은 round opening baseline `exposed 1467`에 이후 batch에서 정식 promote된 row를 합친 **current exposed surface 전체**다.
- 신규 facts 작성은 current lexical authority 기준을 따른다.
  - item-native / effect-first phrasing
  - 번역투 compound 제거
  - acquisition discovery/location 자연화
- candidate artifact와 공식 runtime artifact는 분리 보관한다.

---

## 3. 실행 모델

이번 라운드는 `617`을 item-by-item 수동 집필로 처리하지 않는다.  
실행 모델은 아래 3-lane으로 고정한다.

| lane | 의미 |
|---|---|
| `reuse-fast lane` | 기존 cluster 재사용만으로 deterministic replace 가능한 lane |
| `net-new cluster lane` | source discovery와 새 cluster 설계가 필요한 main lane |
| `hold lane` | current contract 밖이거나 evidence 확보가 안 되어 이번 라운드에서 닫지 않는 lane |

`bucket_2 599`는 semantic family가 아니라 **source-discovery family** 기준으로 묶는다.  
같은 family의 정의는 "같은 source 구조를 새로 열 수 있는가"다.

lane 안에서는 아래 triage를 함께 쓴다.

| 구분 | 의미 |
|---|---|
| `targeted` | existing repo source만으로 evidence 확보 가능 |
| `partial` | 일부 evidence는 있으나 추가 조사 필요 |
| `manual` | 구조화 evidence가 없어 in-game manual 확인 필요 |

각 family는 실행 라벨도 같이 가진다.

| 라벨 | 의미 |
|---|---|
| `reuse-only` | source는 이미 있고 조합만 바꾸면 됨 |
| `new-cluster-only` | source는 있으나 새 cluster 규약이 필요 |
| `mapping-patch` | 기존 추출 파이프라인에 mapping rule만 추가하면 됨 |
| `new-extractor-required` | 새 extractor 스크립트 작성이 필요함 |

기본 우선순위는 아래처럼 둔다.

1. `bucket_1 reuse-fast lane`
2. `bucket_2 targeted`
3. `bucket_2 partial`
4. `manual lane`
5. `bucket_3 hold`

---

## 4. Staging Root 제안

이번 라운드의 staging 루트는 아래처럼 고정하는 것을 기본안으로 둔다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase0_scope_lock/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase2_bucket1_reuse/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/batches/batch_N/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/manual_lane/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase7_closeout/`

이 루트 아래의 preview/candidate와 official runtime promotion 결과는 반드시 분리한다.

---

## 5. Phase 0 — Scope Lock

### 목적

모든 후속 논의가 "`617`을 어떤 source/cluster로 승격시킬 것인가"에만 수렴하게 만든다.

### 작업

- `identity_fallback_source_expansion_backlog.json`을 단일 canonical input으로 선언
- baseline `2105 / 2084 / 21`, `1440 / 617 / 48`, `617 / 1467`, `11 / 599 / 7`을 round opening snapshot으로 고정
- hold 목록을 companion scope lock 문서에 명문화
- 선행 라운드 닫힘 상태를 명시 재확인

### 산출물

- `docs/iris-dvf-3-3-identity-fallback-source-expansion-scope-lock.md`
- `round_opening_baseline_snapshot.json`

### Gate

- scope lock 문서가 완성되고 이후 phase가 같은 분모를 본다.

---

## 6. Phase 1 — Execution Manifest

### 목적

`617` 전체를 그대로 본실행으로 가져가지 않고, deterministic lane과 설계 lane을 먼저 분리한다.

### Phase 1-A. `bucket_1` 재사용 군 매핑

#### 작업

- `11`개 row 각각에 대해 current cluster inventory에서 재사용 대상 cluster 식별
- 해당 cluster의 `source.raw` evidence가 그 item에도 사실적으로 성립하는지 검증
- 검증 통과 항목은 `reuse-fast lane`으로 분류
- 실패 항목은 `bucket_2`로 재이관

#### 산출물

- `bucket_1_cluster_reuse_mapping.json`

### Phase 1-B. `bucket_2 599` lane 분류

#### 작업

- `599`를 semantic family가 아니라 source-discovery family 기준으로 군집화
- item별 `targeted / partial / manual` lane 부여
- family별 `reuse-only / new-cluster-only / mapping-patch / new-extractor-required` 실행 라벨 부여
- 기존 추출 파이프라인에 mapping rule을 추가하는 수준은 `mapping-patch`로, 새 extractor 스크립트 작성이 필요한 수준만 `new-extractor-required`로 구분

#### 산출물

- `bucket_2_domain_inventory.json`
- `bucket_2_source_triage.json`
- `bucket_2_lane_summary.json`

### Phase 1-C. Cluster Design Planning 및 Batch Schedule

#### 작업

- `targeted + partial` lane 기준으로 net-new cluster 후보 목록 도출
- cluster별 예상 커버리지 산출
- 적은 cluster로 많은 row를 덮는 방향으로 우선순위 결정
- batch 크기와 순서를 확정
- 이 단계는 cluster 후보 목록과 batch 일정만 확정한다. 실제 `sentence_plan / compose_profile / required_any` 정의는 Phase 3에서 수행한다.

#### 산출물

- `bucket_2_cluster_design_plan.json`
- `bucket_2_batch_schedule.json`

### Gate

- 전체 backlog가 `reuse-fast lane / net-new cluster lane / hold lane`으로 갈라진다.
- `bucket_2 599`가 item pile이 아니라 execution manifest로 변환된다.

---

## 7. Phase 2 — Bucket 1 선소거

### 목적

대형 `bucket_2` 착수 전에 현재 계약 안에서 deterministic replace 경로가 실제로 작동하는지 기술 경로를 먼저 검증한다.

### Phase 2-A. Facts / Decisions Patch 준비

#### 작업

- 재사용 cluster 기반 facts patch 초안 작성
- `primary_use`, `acquisition_hint`, `slot_meta` 등 기존 슬롯에 필요한 값 채움
- decisions patch 초안 작성
- `compose_profile`을 `identity_fallback`에서 해당 cluster profile로 전환
- `reason_code` 갱신

#### 산출물

- `bucket_1_facts_patch_candidate.jsonl`
- `bucket_1_decisions_patch_candidate.jsonl`

### Phase 2-B. Preview & Delta Gate

#### 작업

- patch 적용 후 dry-run 수행
- `compose -> normalizer -> style linter -> rendered`
- `quality_state / publish_state` 전환 preview 확인

#### Gate

- introduced hard fail = `0`
- introduced warn regression = `0`
- 해당 gate 시작 시점의 전체 exposed surface rendered regression = `0`
- B-path lane accounting 확인
  - `identity_fallback` lane의 row가 silent loss, row 삭제, bridge 제거 없이 source promotion 경로로만 감소했는지 확인
  - `requeue_tolerability / lane_stability`가 current path-aware gate를 계속 만족하는지 검증

#### 산출물

- `bucket_1_preview_report.json`
- `bucket_1_delta_gate.json`

### Phase 2-C. Authority Promotion & Runtime Reflection

#### 작업

- gate 통과 시 facts/decisions 정식 반영
- rendered authority 재생성
- Lua bridge export
- deployed runtime과 staged Lua hash 일치 확인

### Phase 2-D. In-game Validation

#### 작업

- Browser/Wiki surface에서 `11`개 item 본문 표시 확인
- 기존 exposed item regression 부재 확인
- context menu / other layer 안정성 확인

#### 산출물

- `bucket_1_closeout_packet.json`

### 종료 조건

- delta gate pass
- in-game validation pass
- B-path lane accounting 확인

예상 projection (종료 조건 아님):

- `identity_fallback -11 / cluster_summary +11`
- `internal_only -> exposed` 전환 가능성 있음
  - `publish_state`는 quality ownership 및 publish policy 검토 후 별도 결정

---

## 8. Phase 3 — Bucket 2 Net-New Cluster Taxonomy 설계

### 목적

`599` row를 바로 구현하지 않고, batch별 source-expansion taxonomy를 먼저 설계한다.

### 작업

- Phase 1의 batch schedule 기준으로 batch `N`별 cluster 정의 작성
- family/cluster 후보마다 아래 항목을 명시
  - 어떤 item 집합을 한 family로 묶는지
  - 현재 `identity_fallback`으로 남은 구조적 이유
  - 어떤 source를 추가 확보해야 하는지
  - 확보 뒤 기대 승격 경로가 current authoritative path인 `cluster_summary / direct_use` 중 무엇인지
  - 새 validator / audit 포인트가 무엇인지
- batch 설계 메모에서 `special_context` 같은 비-canonical 용어를 쓰더라도 그것은 planning memo일 뿐 authoritative lane이 아님을 명시
- cluster definition field를 아래처럼 고정
  - `cluster_id`
  - `sentence_plan`
  - `compose_profile` mapping
  - `required_any`

### 산출물

- `batch_N_cluster_definitions.json`
- `batch_N_smoke_samples.json`

### Gate

- 전체 batch에 대해 taxonomy가 먼저 닫힌다.
- implementation이 taxonomy 실패 비용을 떠안지 않는다.

---

## 9. Phase 4 — 반복 Batch 실행

### 목적

Phase 3에서 설계한 batch를 `targeted -> partial` 순서로 순차 실행한다.

### Phase 4-A. Source Evidence Authoring

#### 작업

- 해당 batch item의 `source.raw` evidence 작성
- `media/scripts/*.txt`, `media/lua/client/*` 중심으로 사실 추출
- partial lane은 추가 조사 병행
- 신규 facts 값은 current lexical authority 기준을 따른다.
  - item-native / effect-first phrasing
  - 번역투 compound 제거
  - acquisition discovery/location 자연화
- facts patch 작성
- decisions patch 작성

#### 산출물

- `batch_N_source_raw/`
- `batch_N_facts_patch.jsonl`
- `batch_N_decisions_patch.jsonl`

### Phase 4-B. Pipeline Dry-run & Delta Gate

#### 작업

- `compose -> normalizer -> style linter -> rendered` dry-run
- `quality_state / publish_state` 전환 preview

#### Gate

- introduced hard fail = `0`
- introduced warn regression = `0`
- 해당 gate 시작 시점의 전체 exposed surface rendered regression = `0`
- B-path lane accounting 확인
  - `identity_fallback` lane의 row가 silent loss, row 삭제, bridge 제거 없이 source promotion 경로로만 감소했는지 확인
  - `requeue_tolerability / lane_stability`가 current path-aware gate를 계속 만족하는지 검증

#### 산출물

- `batch_N_preview_report.json`
- `batch_N_delta_gate.json`

### Phase 4-C. Authority Promotion

#### 작업

- gate 통과 시 facts/decisions 정식 반영
- rendered authority 재생성
- Lua bridge export
- deployed/staged hash 확인

### Phase 4-D. In-game Validation

#### 작업

- batch 대상 item Browser/Wiki surface 확인
- regression 부재 확인
- pass 기록

#### 산출물

- `batch_N_closeout_packet.json`

### Batch Gate

- batch `N` closeout 이후에만 batch `N+1` 착수
- 실패 시 해당 batch 내부에서 수정 후 재실행
- 동일 batch에서 2회 이상 gate 실패 시 해당 family의 cluster taxonomy를 Phase 3 수준에서 재검토

---

## 10. Phase 5 — Manual Lane & Residual 처리

### 목적

Phase 1-B에서 `manual`로 분류된 item과 Phase 4 잔여분을 current contract 안에서 처리한다.

### 작업

- in-game manual 확인을 통한 evidence 수집
- 수집 evidence를 기준으로 cluster mapping 재판정
- facts/decisions patch 작성
- preview -> promotion -> validation 반복
- evidence 확보 불가능한 최종 residual은 `carry_forward_hold`로 봉인

### 산출물

- `manual_lane_evidence_collection.json`
- `manual_lane_batch_closeout_packets/`
- `residual_carry_forward_hold.json`

### Gate

- manual lane은 evidence 부족으로만 남고, 구조 예외라는 이름으로 우회되지 않는다.

---

## 11. Phase 6 — Subset Rollout 검증

### 목적

대량 일괄 promote가 아니라 family별 작은 promote 묶음이 current three-axis contract와 충돌하지 않는지 검증한다.

### 판정 기준

- `runtime_state`: `active / silent` 유지
- `quality_state`: `strong / adequate / weak` 유지
- `publish_state`: `internal_only / exposed` 유지

### 작업

- source expansion으로 stronger quality ownership을 얻은 subset만 `publish_state` 승격 검토
- preview에서 contract violation 여부 확인
- subset 단위 promote의 안정성을 문서화

### 산출물

- `subset_rollout_validation_report.json`
- `subset_publish_preview_diff.json`

### Gate

- subset promote가 publish split을 안정적으로 갱신한다.
- preview 상 contract 위반이 없다.
- B-path lane accounting 확인
  - `identity_fallback` lane의 row가 silent loss, row 삭제, bridge 제거 없이 source promotion 경로로만 감소했는지 확인
  - `requeue_tolerability / lane_stability`가 current path-aware gate를 계속 만족하는지 검증

---

## 12. Phase 7 — Round Closeout & Remeasurement

### 목적

라운드 전체를 닫고 분포를 공식 재측정한다.

### 재측정 항목

1. `identity_fallback` 감소량
2. `cluster_summary / direct_use` 증가량
3. `internal_only -> exposed` 전환 수
4. structural lint 신규 문제 여부
5. requeue와 lane stability가 current path-aware gate를 계속 만족하는지

### 산출물

- `source_expansion_round_closeout.json`
- `quality_baseline_v5.json`
- `post_expansion_distribution_remeasurement.json`
- `final_runtime_snapshot.json`

### Gate

- post-round baseline이 current v4와 명확히 비교 가능하다.
- source expansion 성과와 residual hold가 분리 기록된다.

---

## 13. Phase 8 — Semantic Axis 반영 여부 별도 결정

### 목적

source expansion 완료가 semantic axis 반영의 자동 트리거가 되지 않도록 분리한다.

### 작업 원칙

- 이 phase는 별도 round opening으로만 처리
- source expansion remeasurement가 stable해야 착수 가능
- `DECISIONS.md`에 명시적 semantic decision이 있어야 함
- 그 전에는 current semantic 판정 체계를 변경하지 않음

### 의미

이번 execution plan은 Phase 8의 직접 실행 문서가 아니라, **Phase 8을 이번 라운드 scope 밖으로 밀어두는 문서**다.

---

## 14. 종료 조건 요약

이번 라운드는 아래 순서를 모두 통과했을 때 종료로 본다.

```text
Phase 0  Scope Lock
    ->
Phase 1  Execution Manifest
    ->
Phase 2  Bucket 1 deterministic replace
    ->
Phase 3  Batch taxonomy design
    ->
Phase 4  Targeted/partial batch execution
    ->
Phase 5  Manual lane and residual
    ->
Phase 6  Subset rollout validation
    ->
Phase 7  Closeout and remeasurement
    ->
Phase 8  Separate semantic decision round
```

실행 중 self-check는 한 줄로 닫는다.

> 이번 round의 본질은 `identity_fallback 617` source expansion이다.  
> compose/style/state 구조를 다시 여는 라운드가 아니다.
