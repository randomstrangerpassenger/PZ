# Iris DVF 3-3 Round A + Round B Parallel Plan

> 상태: Draft v0.5-planning-authority  
> 기준일: 2026-04-29  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Round A + Round B Parallel Plan` user-provided final roadmap, 2026-04-29  
> 목적: `FUNCTION_NARROW` publish disposition closure와 `LAYER4_ABSORPTION_CONFIRMED` decision namespace sealing을 서로 침범하지 않는 두 round로 분리하되, 산출물 generation의 부분 병렬 가능성과 governance 흐름의 B 선행 직렬 의존성을 함께 고정한다.  
> 실행 상태: planning authority only. 이 문서는 opening decision, canonical artifact, rendered text, Lua bridge, staged/runtime artifact, top docs closeout state를 변경하지 않는다.

---

## 0. Round Identity

### 0-1. 공식명

Round A:

```text
FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal Round
```

Round B:

```text
Iris DVF 3-3 Layer4 Absorption Policy Round
```

### 0-2. 내부 코드명

```text
round_a = function_narrow_disposition_closure_publish_writer_authority_seal_round
round_b = layer4_absorption_policy_round
```

### 0-3. Round 성격

| 항목 | Round A | Round B |
|---|---|---|
| primary purpose | publish writer authority seal | layer-boundary hard-block decision namespace seal |
| default writer role | docs/governance + build delta verification | observer-only until count branch closes |
| production writer expectation | decision-only exception possible; applied writer delta 0 | count 0이면 sealed zero-count, count >= 1이면 blocked |
| axis mutation | forbidden | forbidden |
| staged/runtime mutation | forbidden | forbidden |
| expected runtime state | `ready_for_in_game_validation` 유지 | `ready_for_in_game_validation` 유지 |

### 0-4. Staging roots

Round B 신규 산출물 root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/
```

Round A 신규 산출물 root:

```text
Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/
```

Top-doc 변경은 두 round가 병렬 실행되더라도 같은 파일을 동시에 쓰지 않는다. `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` 업데이트는 B opening -> A opening -> B closeout -> A closeout 순서로 serial write lock을 건다.

---

## 1. Shared Governance Baseline

### 1-1. 공통 invariant 보존 계약

두 round opening decision은 아래 6항목을 그대로 포함해야 한다.

```text
1. staged Lua hash
   0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062 unchanged
   (Round A Case 2 exception에서 N건 publish 복원 decision이 봉인되면
   future activation/write round용 expected hash delta를 기록한다.
   current planning/execution round는 staged Lua hash를 변경하지 않는다.)
2. workspace Lua hash unchanged
   (Round A Case 2 exception에서 canonical workspace Lua write가 별도 activation/write round로 승인되면
   staged Lua hash delta와 같은 branch로 갱신한다.
   current planning/execution round는 workspace Lua hash를 변경하지 않는다.)
3. runtime state: ready_for_in_game_validation 유지
   (Current round:
   current sealed build의 ready_for_in_game_validation을 유지한다.
   Future activation/write round:
   새 staged Lua artifact가 생성되면 그 new build가 ready_for_in_game_validation에 들어갈 수 있으며,
   manual in-game validation은 새 build에 대해 별도로 다시 받는다.)
4. quality_baseline_v4 frozen
5. bridge availability: internal_only 617 / exposed 1467
   (Current round:
   Case 2 exception은 decision delta만 기록하고 current bridge availability는 unchanged로 둔다.
   Future activation/write round:
   Case 2 N건 복원이 적용되면 expected bridge availability는 internal_only 617-N / exposed 1467+N으로 기록한다.
   Case 3 혼입 발견 시 bridge availability assertion은 post-activation decision까지 유보한다.
   항목 1/2/3 및 Case 2/Case 3 branch policy와 연동.)
6. source distribution: BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481 unchanged
```

Round B는 추가로 아래 observer distribution도 unchanged gate로 검증한다.

```text
section distribution: SECTION_FUNCTION_NARROW 1433 / none 672 unchanged
overlap distribution: source_only 67 / section_only 876 / coexist 557 / dual_none 605 unchanged
```

`strong 1316 / adequate 0 / weak 768` quality split은 publish/bridge-relevant composed rows 기준이며 합계는 `2084`다. Total raw row count `2105`와 다를 수 있으므로 invariant 검증에서 두 모수를 혼용하지 않는다.

### 1-2. Adopted upstream decisions

이 계획은 아래 결정을 재심하지 않는다.

- `2026-04-05`: `FUNCTION_NARROW`는 기본 semantic weak precondition을 유지한다.
- `2026-04-08`: `LAYER4_ABSORPTION`은 style 문제가 아니라 layer boundary contract violation으로 분류된다.
- `2026-04-22`: Phase D structural reclassification은 pure observer authority다.
- `2026-04-22`: Phase E는 staged/static rollout과 `ready_for_in_game_validation`까지만 닫는다.
- `2026-04-24`: `LAYER4_ABSORPTION`은 source family로 승격하지 않는다.
- `2026-04-24`: current default structural reclassification path는 `dual_axis_canonical` read model이다.

### 1-3. Shared out-of-scope

- `quality_baseline_v4 -> v5` cutover
- deployed closeout / ready_for_release
- manual in-game validation result declaration
- runtime-side compose/rewrite
- staged/workspace Lua mutation
- source expansion execution
- Phase D observer artifact rewrite

---

## 2. Parallel Sequencing Contract

### 2-1. Default sequencing

```text
산출물 generation은 부분 병렬 가능.
governance 흐름은 B uplink direction으로 직렬.
```

Phase 의존 관계:

- Round B Phase 1 완료 후 Round A Phase 2 Case 3 판정을 닫을 수 있다.
- Round B Phase 4 branch result 확정 후 Round A Phase 5 invariant verification을 실행한다.
- Top-doc write lock은 `B opening -> A opening -> B closeout -> A closeout` 순서를 따른다.

Round A Phase 0/1 documentation drafting과 Round B Phase 0/1 detector design은 병렬 산출물 generation으로 진행할 수 있다. 단, Round A Phase 2 final inventory와 Phase 5 closeout verification은 Round B output을 읽어야 하므로 governance closeout은 B 선행 직렬로 닫는다.

### 2-2. Serial transition trigger

Round B Phase 3에서 namespace 결정이 아래처럼 바뀌면 즉시 직렬 전환한다.

```text
from: decision namespace
to: section-side sub-classification
```

전환 시 처리:

- Round B를 완전 closeout한다.
- Round B closeout에서 source/section axis 영향 여부를 재판정한다.
- Round A Phase 2 inventory와 Phase 5 invariant expected delta를 Round B closeout 이후 다시 고정한다.

### 2-3. Scope exclusion cross-reference

Round A opening decision은 아래를 포함한다.

```text
- 본 round는 LAYER4_ABSORPTION을 정의하거나 활성화하지 않는다.
- 본 round는 새 hard-block namespace를 만들지 않는다.
- 본 round는 Phase D observer signal preservation을 reopen하지 않는다.
- 본 round는 ACQ_DOMINANT residual 재측정을 열지 않는다.
- 본 round는 FUNCTION_NARROW 2차 rollout을 실행하지 않는다.
```

Round B opening decision은 아래를 포함한다.

```text
- 본 round는 FUNCTION_NARROW / ACQ_DOMINANT disposition을 닫지 않는다.
- 본 round는 source axis 또는 section axis 분포를 변경하지 않는다.
- 본 round는 별도 activation round 없이 publish/quality state를 mutate하지 않는다.
- 본 round는 3-4 상세를 3-3 본문으로 흡수하는 방향을 열지 않는다.
```

---

## 3. Round B Plan

### 3-1. Phase 0 - Opening Decision Sealing

산출물:

- `docs/DECISIONS.md` 신규 entry, 날짜 `2026-04-29`
- `docs/ROADMAP.md` 신규 lane
- `phase0_opening/pass_criteria_contract.json`
- `phase0_opening/opening_decision_reflection.md`

Opening decision 필수 포함:

- `2026-04-24` sealed source family 미승격 유지
- `2026-04-08` sealed layer boundary contract violation 분류 유지
- Round A scope exclusion 절 provisional cross-reference
- `count = 0 / count >= 1` branch policy
- 공통 invariant 6항목

`pass_criteria_contract.json` 최소 shape:

```json
{
  "round": "Iris DVF 3-3 Layer4 Absorption Policy Round",
  "round_code": "layer4_absorption_policy_round",
  "writer_role_default": "observer_only",
  "namespace_decision": "decision_namespace",
  "suspect_tier": "not_defined",
  "count_branch_policy": {
    "count_eq_0": "sealed_zero_count_no_writer_mutation",
    "count_gte_1": "policy_sealed_activation_blocked"
  },
  "invariant_contract": {
    "staged_lua_hash_unchanged": true,
    "workspace_lua_hash_unchanged": true,
    "runtime_state": "ready_for_in_game_validation",
    "quality_baseline_v4_frozen": true,
    "bridge_availability": "internal_only 617 / exposed 1467",
    "bridge_availability_exception_policy": "Round A Case 2 or Case 3 exception report updates expected delta",
    "source_distribution": "BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481"
  }
}
```

Closure 조건:

- `DECISIONS.md`와 `ROADMAP.md`가 opening state를 기록한다.
- Round B opening decision은 Round A scope exclusion을 provisional cross-reference로 포함한다.
- Round A opening top-doc 업데이트 후 상호 참조가 최종 확정된다.
- top-doc write lock 순서가 기록된다.

### 3-2. Phase 1 - Detection Rule Definition + Dry-run Measurement

Detector는 문장을 보지 않는다. Detector는 `body_plan` trace와 source artifact provenance만 읽는다.

금지:

```text
- 문장 패턴 매칭
- 한국어 표현 유사도
- "쓰인다", "사용된다" 등 단어 기반 감지
- Layer 4 문장과 Layer 3 문장의 fuzzy match
```

허용:

```text
- Layer 4 interaction list provenance 추적
- interaction/action/recipe/right-click list 데이터가 Layer 3 body 슬롯에 들어왔는지 구조 신호로 검출
- body_plan section trace와 source artifact의 구조적 연결 확인
- list cardinality / source provenance / destination layer 기반 검출
```

#### 3-2-1. CONFIRMED hit 판정 기준

`LAYER4_ABSORPTION_CONFIRMED` hit는 아래 조건을 모두 만족할 때만 true다.

| 조건 | 요구사항 |
|---|---|
| row identity | row가 current 2105-row body_plan/source artifact에 존재한다 |
| destination layer | destination slot이 3-3 body output slot이다 |
| source layer | source provenance가 3-4 interaction-list 계열이다 |
| source object | linked source artifact가 list/cardinality를 가진 interaction/action/recipe/right-click entry를 제공한다 |
| trace edge | compose/body_plan trace가 source object -> 3-3 body output slot 연결을 명시한다 |
| writer boundary | detector output은 `observer_only`이며 rendered text, `quality_state`, `publish_state`를 쓰지 않는다 |

Destination slot canonical label은 실행 Phase 0에서 실제 trace field map으로 확정한다. 계획 기준의 preferred names는 아래다.

```json
{
  "destination_layer_field": "destination_layer",
  "destination_slot_field": "destination_slot",
  "destination_layer_value": "layer3_body",
  "destination_slot_value": "body_3_3",
  "source_provenance_field": "source_provenance",
  "source_layer_value": "layer4_interaction_list"
}
```

실제 artifact가 위 field명을 쓰지 않으면 `phase1_detection/trace_field_map.json`을 먼저 생성하고, detector는 그 map에 기록된 field만 읽는다. Field map은 새 namespace가 아니라 실행 artifact의 schema adapter다.

#### 3-2-2. 4계층 list entry가 3계층 body에 들어왔는지의 구조 판정

아래 중 하나가 trace에서 확인되면 Layer 4 source object로 읽는다.

- `interaction_list`
- `action_list`
- `recipe_interaction_list`
- `right_click_interaction_list`
- `layer4_interactions`

단, source object 이름만으로는 부족하다. 반드시 row-level trace edge가 아래 형태로 닫혀야 한다.

```json
{
  "row_id": "<row id>",
  "source_ref": "<layer4 list artifact ref>",
  "source_cardinality": 1,
  "destination_ref": "body_3_3",
  "edge_type": "placed_in_body_output"
}
```

`source_cardinality >= 1`이어도 destination이 3-4 상세 slot, diagnostic metadata, handoff note, internal trace field이면 hit가 아니다.

#### 3-2-3. Compose trace 활용 방식

Detector는 compose output text를 비교하지 않고 아래 read path를 사용한다.

```text
body_plan row
  -> section trace / body slot trace
  -> source artifact ref
  -> source artifact kind + layer + list cardinality
  -> destination layer/slot
  -> observer-only row output
```

권장 row output fields:

```json
{
  "row_id": "string",
  "full_type": "string",
  "writer_role": "observer_only",
  "layer4_absorption_confirmed": false,
  "hard_block_family": null,
  "hard_block_confidence": null,
  "hard_block_origin": null,
  "source_ref": null,
  "source_kind": null,
  "source_cardinality": 0,
  "destination_layer": null,
  "destination_slot": null,
  "trace_edge_status": "no_hit"
}
```

#### 3-2-4. False positive 방지 보수 조건

아래 row는 hit에서 제외한다.

- 3-4 slot에 정상 배치된 interaction list
- 3-3 body가 interaction list의 존재를 metadata/ref로만 들고 있고 list content를 body output slot에 배치하지 않은 row
- source provenance가 generic item use, category summary, section-derived `SECTION_*` signal뿐인 row
- legacy single-slot diagnostic view에서만 보이는 row
- text body에 비슷한 한국어 표현이 있지만 trace edge가 없는 row
- source artifact ref가 없거나 source cardinality가 0인 row

#### 3-2-5. SUSPECT tier policy

```text
LAYER4_ABSORPTION_SUSPECT 등급은 두지 않는다.
단, 후속 구현에서 텍스트 기반 detector가 혼입되면 이 정책은 무효화되며
SUSPECT tier 도입 round를 별도로 열어야 한다.
```

산출물:

- `phase1_detection/layer4_absorption_provenance_detection.2105.jsonl`
- `phase1_detection/layer4_absorption_provenance_summary.json`
- `phase1_detection/trace_field_map.json`

Branch:

```text
count = 0  -> Phase 2 zero-count production-safe lane
count >= 1 -> Phase 2 dry-run preservation lane
```

### 3-3. Phase 2 - Hard-block Decision Family Definition Sealing

`LAYER4_ABSORPTION_CONFIRMED` definition:

```text
LAYER4_ABSORPTION_CONFIRMED hit = Phase 1 structural detector hit.
SUSPECT tier 없음.
```

Mapping, when activated by a separate writer-eligible branch:

```text
LAYER4_ABSORPTION_CONFIRMED
  -> quality_state = weak
  -> publish_state = internal_only

This is an activation-only mapping.
It is not applied during dry-run inventory or count >= 1 blocked branch.
```

이 mapping은 `2026-04-08` sealed mapping과 동치이며 새 mapping이 아니다.

정당화:

```text
publish 분기 사유는 layer boundary 위반
(3계층 자리에 4계층 컨텐츠 진입)이지 quality weak가 아니다.
quality weak는 동반 라벨이지 publish 분기의 독립 사유가 아니다.
```

본 round의 publish/quality mapping은 Round A에서 봉인되는 일반 원칙, 즉 컨텐츠 위치 정합성 기준의 corollary다. Round A opening decision이 같은 governance turn에서 sealed된다.

위치 위반 해소 시 publish 복원 경로는 본 round 밖이다. 다음 빌드 compose 보정 lane 또는 별도 activation round에서만 연다.

### 3-4. Phase 3 - Decision Namespace Sealing

채택 옵션:

```text
Option 1: decision namespace
```

봉인 문장:

```text
LAYER4_ABSORPTION_CONFIRMED namespace는 제3 structural axis가 아니라,
layer-boundary hard block 처분을 위한 decision namespace이다.
source axis distribution과 section axis distribution은
이 namespace에 의해 변경되지 않는다.
```

정확한 field 이름:

```json
{
  "hard_block_family": "LAYER4_ABSORPTION_CONFIRMED",
  "hard_block_confidence": "confirmed",
  "hard_block_origin": "layer4_interaction_list_provenance_to_layer3_body_slot",
  "hard_block_present": true,
  "decision_namespace": "layer_boundary_hard_block",
  "decision_namespace_authority": "quality_publish_decision_stage_only_when_activated"
}
```

`hard_block_confidence` 허용값:

```text
confirmed
none
```

`suspect`는 허용값이 아니다.

확인 항목:

- source axis `617 / 7 / 1481` unchanged
- section axis `1433 / 672` unchanged
- overlap `67 / 876 / 557 / 605` unchanged

### 3-5. Phase 4 - Disposition Application Branch

#### 4-A. count = 0 sealed zero-count branch

- production labeling path는 `sealed_zero_count`로 읽을 수 있다.
- applied labeling count는 반드시 0이다.
- writer mutation은 실행하지 않는다.
- publish/quality/runtime delta는 0이다.

산출물:

- `phase4_disposition/layer4_absorption_disposition_result.json`

Required summary:

```json
{
  "confirmed_count": 0,
  "production_labeling_path_status": "sealed_zero_count",
  "production_labeling_count": 0,
  "writer_mutation_count": 0,
  "publish_delta": 0,
  "quality_delta": 0
}
```

#### 4-B. count >= 1 dry-run-only branch

- detection inventory를 보존한다.
- writer는 진입하지 않는다.
- production labeling은 blocked다.
- round 상태는 `policy_sealed_activation_blocked`다.
- activation은 in-game validation 이후 별도 activation round에서만 연다.

산출물:

- `phase4_disposition/layer4_absorption_disposition_inventory.json`

Required summary:

```json
{
  "confirmed_count": ">= 1",
  "production_labeling_path_status": "blocked",
  "writer_activation": "blocked",
  "writer_mutation_count": 0,
  "round_status": "policy_sealed_activation_blocked",
  "activation_round_required": true
}
```

### 3-6. Phase 5 - Invariant Verification

산출물:

- `phase5_invariants/layer4_absorption_invariant_verification_report.json`

Required checks:

- 공통 invariant 6항목 pass
- source axis writer 진입 0건
- section axis writer 진입 0건
- source distribution unchanged
- section distribution unchanged
- overlap distribution unchanged

Branch-specific checks:

- 4-A: `CONFIRMED count = 0`, publish/quality writer 진입 0건
- 4-B: writer 진입 0건, detection inventory 보존 확인

### 3-7. Phase 6 - Adversarial Review

Fixed review format:

```text
Critical
Important
Minor
Verdict: PASS | FAIL
```

Review checklist:

- Phase 1~5 빈 공간이 모두 채워졌는가
- `2026-04-05`, `2026-04-08`, `2026-04-22`, `2026-04-24` sealed 결정을 위반하지 않는가
- Round A scope와 충돌하지 않는가
- `count >= 1` branch가 writer blocked로 닫히는가
- decision namespace가 제3 axis로 오해될 여지가 없는가

산출물:

- `phase6_review/layer4_absorption_adversarial_review.md`

### 3-8. Phase 7 - Closeout

산출물:

- `docs/DECISIONS.md` closeout entry
- `docs/ARCHITECTURE.md` namespace 처리 보강
- `docs/ROADMAP.md` Done lane 이동
- Phase 1 detection 산출물 hash와 Phase 4 disposition 산출물 hash를 포함한 본 round staging artifact hash set을 closeout decision에 기록
- `docs/Iris/Done/Walkthrough/iris-dvf-3-3-layer4-absorption-policy-round-walkthrough.md`

`count = 0` closeout 문장:

```text
Layer4 Absorption Policy Round closes with policy sealed
and zero-count production-safe labeling.
No source/section axis mutation. No publish/quality/runtime delta.
```

`count >= 1` closeout 문장:

```text
Layer4 Absorption Policy Round closes as policy_sealed_activation_blocked.
Dry-run inventory is preserved.
Writer activation and production labeling are deferred
to a post-in-game-validation activation round.
```

### 3-9. Round B Validation Gates

```text
Gate B1 - Namespace Gate
  [ ] LAYER4_ABSORPTION_CONFIRMED가 source family로 등록되지 않음
  [ ] section axis family로 승격되지 않음
  [ ] decision namespace라고 명시됨

Gate B2 - Detection Gate
  [ ] detector가 interaction-list provenance 기반
  [ ] 텍스트 매칭 미포함
  [ ] SUSPECT tier 미생성 또는 재도입 조건 명시

Gate B3 - Count Branch Gate
  [ ] count = 0이면 production labeling path는 sealed_zero_count
  [ ] count = 0이어도 writer mutation count는 0
  [ ] count >= 1이면 writer/production labeling blocked
  [ ] count >= 1이어도 dry-run inventory 보존

Gate B4 - Axis Preservation Gate
  [ ] source distribution 617 / 7 / 1481 unchanged
  [ ] section distribution unchanged
  [ ] Phase D observer artifacts 미재작성

Gate B5 - Runtime Invariant Gate
  [ ] staged Lua hash unchanged
  [ ] workspace Lua hash unchanged
  [ ] ready_for_in_game_validation 유지
  [ ] quality_baseline_v4 frozen
```

---

## 4. Round A Plan

### 4-1. Phase 0 - Opening Decision Sealing

산출물:

- `docs/DECISIONS.md` 신규 entry, 날짜 `2026-04-29`
- `docs/Iris/Done/surface_contract_rollout_order.md` Rollout 2 hold 해소 후속 decision 위치 명시
- `docs/ROADMAP.md` 신규 lane
- `phase0_opening/pass_criteria_contract.json`
- `phase0_opening/opening_decision_reflection.md`

핵심 봉인 문장:

```text
This round seals publish writer authority.
The publish branch is determined by whether content is
in the correct layer/position, not by semantic quality strength.
FUNCTION_NARROW and ACQ_DOMINANT blanket isolation
are forbidden from this round onward.
```

Opening decision 필수 포함:

- 일반 원칙 봉인
- `FUNCTION_NARROW` publish disposition: clean branch option C, delta 0
- Case 2 혼입 발견 시 Round A 내부 exception branch로 해당 row만 publish 복원하고 expected delta 갱신
- `FUNCTION_NARROW` blanket isolation: Hold -> Forbidden
- `ACQ_DOMINANT` blanket isolation: Hold -> Forbidden
- `ACQ_DOMINANT` residual remeasurement는 source expansion 이후 별도 round
- `2026-04-05` sealed `FUNCTION_NARROW` precondition 유지
- Round B scope exclusion 절
- 공통 invariant 6항목

### 4-2. Phase 1 - Case Classification Authority and ARCHITECTURE Insertion Plan

일반 원칙:

```text
publish 분기 기준은 컨텐츠 위치 정합성이다.
quality 평가(strong/weak/adequate)는 publish writer가 아니다.
```

Case table:

| Case | 상황 | publish 처리 | 정당화 근거 |
|---|---|---|---|
| Case 1 | 알맞은 자리에 필요한 컨텐츠 부재 (`identity_fallback`) | `internal_only` 정당 | 컨텐츠 부재 |
| Case 2 | 알맞은 자리에 컨텐츠 있음, 폭이 좁거나 획득 비중 강함 (`FUNCTION_NARROW` / `ACQ_DOMINANT`) | publish 미변경 | 위치 정합, 분기 사유 없음 |
| Case 3 | 3계층 자리에 4계층 interaction 컨텐츠 진입 (`LAYER4_ABSORPTION`) | `internal_only` 정당 | 위치/권한 위반 |

ARCHITECTURE 반영 위치:

1. Primary insertion: `docs/ARCHITECTURE.md`의 current 3-axis/publish contract 영역 중 `publish contract와 bridge semantics` 바로 아래에 `publish writer authority` subsection을 추가한다.
2. Closeout addendum: closeout 시 current-state section 말미, 현재 마지막 Iris DVF 3-3 addendum 뒤에 Round A current read를 추가한다.

`ARCHITECTURE.md` mutation은 Phase 7 closeout에서 일어난다. Phase 1은 mutation의 적용 위치와 본문 내용을 결정하는 단계다.

Primary subsection 최소 내용:

```text
publish writer authority는 semantic quality strength가 아니라 layer/position correctness를 본다.
quality_state는 publish branch의 독립 writer가 아니다.
internal_only는 Case 1 또는 Case 3처럼 위치/권한 사유가 있을 때만 정당화된다.
FUNCTION_NARROW / ACQ_DOMINANT 같은 semantic narrowness나 acquisition dominance만으로 blanket isolation을 열 수 없다.
```

### 4-3. Phase 2 - internal_only 617 Reason Inventory

검증 목적:

```text
현재 internal_only 617이 전부 Case 1
(알맞은 자리에 필요한 컨텐츠 부재) 사유인지 확인.
```

검증 입력:

- bridge availability: `internal_only 617 / exposed 1467`
- source distribution: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
- identity_fallback source expansion backlog: `bucket_1 11 / bucket_2 599 / bucket_3 7`
- current default structural artifact:
  - source axis `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
  - section axis `SECTION_FUNCTION_NARROW 1433 / none 672`
  - overlap `source_only 67 / section_only 876 / coexist 557 / dual_none 605`
- Round B Phase 1 detector output, if already generated

#### 4-3-1. Case classification rule

Case 1:

```text
publish_state = internal_only
AND source_signal_primary = BODY_LACKS_ITEM_SPECIFIC_USE
AND no LAYER4_ABSORPTION_CONFIRMED hit
AND no FUNCTION_NARROW / ACQ_DOMINANT-only publish rationale
```

Case 2:

```text
publish_state = internal_only
AND correct layer/position content exists
AND row's only relevant concern is FUNCTION_NARROW or ACQ_DOMINANT
AND no layer-boundary hard-block hit
```

Case 3:

```text
publish_state = internal_only
AND Round B structural detector confirms Layer 4 interaction-list data
    placed into Layer 3 body output slot
```

If Round B detector has not run yet, Round A Phase 2 may produce a provisional inventory but cannot close Case 3 as absent. Final inventory must read Round B Phase 1 or Round B closeout.

#### 4-3-2. Branch policy

```text
전부 Case 1:
  publish delta 0 유지, bridge availability unchanged 확정

Case 2 혼입 발견:
  처리:
    Current round:
      Round A scope 안에서 해당 row의 publish 복원 decision만 봉인
      applied artifact delta는 0 유지
    Future activation/write round:
      decision에 따른 canonical mutation 적용
      expected publish delta = N
  closeout 문장:
    - "publish_restore_decision_count = 0 (Case 2 혼입 없음)"
    - 또는 "publish_restore_decision_count = N (Case 2 N건 복원 decision, exception report 첨부)"
  두 경우 모두 Round A 안에서 처리 완결
  별도 round 인계 없음
  이는 misclassification 정정이지 FUNCTION_NARROW 2차 rollout이 아니다
  Rollout은 family 단위 blanket disposition 적용을 의미하며,
  Case 2 정정은 개별 row의 분류 오류 해소이므로 scope exclusion에 위반되지 않는다
  canonical staged/runtime artifact mutation은 별도 activation/write round 없이는 금지

Case 3 혼입 발견:
  Round B Phase 1 detector가 해당 후보를 verify하면
  Round B count branch는 반드시 count >= 1로 해소
  Round B closes as policy_sealed_activation_blocked
  Round A closeout은 case_1_count = 617 단언 불가
  Round A는 exception report 첨부 후
  post-activation decision까지 bridge availability unchanged 단언 유보
```

산출물:

- `phase2_inventory/internal_only_617_reason_inventory.json`
- optional: `phase2_inventory/internal_only_617_exception_report.json`

Clean branch required summary:

```json
{
  "internal_only_total": 617,
  "case_1_count": 617,
  "case_2_count": 0,
  "case_3_count": 0,
  "publish_delta_expected": 0,
  "round_b_handoff_required": false
}
```

Exception branch summary must replace the clean-branch assumption:

```json
{
  "internal_only_total": 617,
  "case_1_count": "<617 - case_2_count - case_3_count>",
  "case_2_count": "N",
  "case_3_count": "M",
  "publish_delta_expected": "N for Case 2 restore only",
  "case_2_correction_type": "row_level_misclassification_correction_not_function_narrow_second_rollout",
  "round_b_handoff_required": "true when M > 0",
  "bridge_availability_assertion": "deferred_when_case_3_verified",
  "exception_report_required": true
}
```

### 4-4. Phase 3 - Blanket Isolation Forbidden Reclassification

ROADMAP Hold 항목 재분류:

```text
FUNCTION_NARROW blanket isolation: Hold -> Forbidden
ACQ_DOMINANT blanket isolation:    Hold -> Forbidden
```

봉인 문장:

```text
FUNCTION_NARROW and ACQ_DOMINANT may be remeasured or reconsidered
by future scoped decisions, but blanket isolation is no longer
an admissible publish disposition strategy.
```

산출물:

- `phase3_reclassification/blanket_isolation_forbidden_reclassification.json`

Required fields:

```json
{
  "function_narrow_blanket_isolation": "forbidden",
  "acq_dominant_blanket_isolation": "forbidden",
  "future_scoped_decision_allowed": true,
  "future_blanket_isolation_reconsideration_allowed": false
}
```

### 4-5. Phase 4 - Build Delta Verification

Checks:

- compose pipeline `FUNCTION_NARROW` 처리 변경 없음
- staged build delta verification 수행
- clean branch에서는 publish split `internal_only 617 / exposed 1467` unchanged
- quality split `strong 1316 / adequate 0 / weak 768` unchanged
- rendered output delta 확인
- staged/workspace Lua hash branch-aware 확인

Quality split은 publish/bridge-relevant composed rows 기준이며 합계는 `2084`다. Total raw row count `2105`와의 차이는 failure가 아니다.

산출물:

- `phase4_build_delta_verification/function_narrow_disposition_build_delta_verification_result.json`

Clean branch expected summary:

```json
{
  "branch": "clean_case_1_only",
  "function_narrow_compose_behavior_changed": false,
  "publish_split": "internal_only 617 / exposed 1467",
  "quality_split": "strong 1316 / adequate 0 / weak 768",
  "rendered_output_delta": 0,
  "publish_delta": 0,
  "quality_delta": 0,
  "staged_lua_hash_status": "unchanged",
  "workspace_lua_hash_status": "unchanged"
}
```

Case 2 exception branch expected summary:

```json
{
  "branch": "case_2_exception_row_level_correction",
  "function_narrow_compose_behavior_changed": false,
  "decision_delta": {
    "publish_restore_decision_count": "N",
    "quality_delta_decision_count": 0,
    "expected_bridge_availability_after_activation": "internal_only 617-N / exposed 1467+N",
    "expected_hash_delta_after_activation": true
  },
  "applied_artifact_delta": {
    "publish_delta_applied_this_round": 0,
    "quality_delta_applied_this_round": 0,
    "bridge_availability_applied_this_round": "internal_only 617 / exposed 1467",
    "rendered_output_delta_applied_this_round": 0,
    "staged_lua_hash_applied_this_round": "unchanged",
    "workspace_lua_hash_applied_this_round": "unchanged",
    "runtime_state_applied_this_round": "ready_for_in_game_validation unchanged",
    "canonical_staged_runtime_artifact_mutation_allowed_in_this_phase": false,
    "activation_write_round_required": true
  }
}
```

### 4-6. Phase 5 - Invariant Verification

Phase 5는 Round B Phase 4 branch result가 확정된 뒤에만 실행된다. Phase 2에서 Case 3 후보가 없더라도 Round B Phase 1 detection output 또는 Round B closeout reference를 확인한 뒤 final invariant verification을 닫는다.

산출물:

- `phase5_invariants/function_narrow_disposition_invariant_verification_report.json`

Required checks:

- 공통 invariant 6항목 pass
- Phase 2 Case result 반영
- `617` 전부 Case 1이면 expected delta 0 유지
- Case 2 혼입 시 decision delta와 applied artifact delta가 Phase 4 summary에서 분리되어 있는지 확인
- Case 2 혼입 시 invariant 항목 1/2/3/5의 future activation/write expected delta chain이 exception report 및 Phase 4 decision delta와 일치
- Case 2 혼입 시 canonical staged/runtime artifact mutation이 별도 activation/write round 없이는 실행되지 않았음을 확인
- Case 3 혼입 시 Round B `count >= 1` branch와 `policy_sealed_activation_blocked` closeout을 reference하고 bridge availability assertion을 유보
- Round B closeout 또는 Round B Phase 1 detector output reference 기록

### 4-7. Phase 6 - Adversarial Review

Fixed review format:

```text
Critical
Important
Minor
Verdict: PASS | FAIL
```

Review checklist:

- Phase 0 sealed scope 준수
- 일반 원칙 봉인 표현 명확성
- Case 1/2/3 분류 일관성
- forbidden lane 재분류가 두 family 모두 포함하는가
- ROADMAP sequencing 위반 없음
- `ACQ_DOMINANT` residual remeasurement가 scope 밖에 남아 있는가
- `2026-04-05` / `2026-04-08` sealed 결정 위반 없음
- Round B scope와 충돌 없음

산출물:

- `phase6_review/function_narrow_disposition_adversarial_review.md`

### 4-8. Phase 7 - Closeout

산출물:

- `docs/DECISIONS.md` closeout entry
- `docs/ARCHITECTURE.md` publish writer authority 보강
- `docs/ROADMAP.md` Round A Done lane 이동
- `docs/ROADMAP.md` Hold lane의 `FUNCTION_NARROW blanket isolation`과 `ACQ_DOMINANT blanket isolation` 항목을 제거하거나 Forbidden lane으로 이동
- `docs/Iris/Done/Walkthrough/iris-dvf-3-3-function-narrow-disposition-closure-and-publish-writer-authority-seal-round-walkthrough.md`

Clean branch closeout 문장:

```text
Round A closes FUNCTION_NARROW publish disposition as delta 0
and seals publish writer authority.
FUNCTION_NARROW and ACQ_DOMINANT blanket isolation
are forbidden from this point onward.
ACQ_DOMINANT residual remeasurement remains out of scope
and is deferred until after source expansion.
```

Case 2 exception branch closeout 문장:

```text
Round A closes FUNCTION_NARROW publish disposition with
row-level Case 2 misclassification correction.
decision publish_restore_count = N is recorded in the exception report.
applied publish delta in this round remains 0.
This is not FUNCTION_NARROW second rollout.
Canonical staged/runtime artifact mutation remains deferred
until a separate activation/write round.
```

Expected result:

```text
decision delta:
  publish_restore_decision_count = 0 (Case 2 혼입 없음)
  or publish_restore_decision_count = N (Case 2 N건 복원 decision, exception report 첨부)
  quality_delta_decision_count = 0

applied artifact delta in this round:
  publish_delta_applied_this_round = 0
  quality_delta_applied_this_round = 0
  bridge_availability_applied_this_round = internal_only 617 / exposed 1467 unchanged
  staged_lua_hash_applied_this_round = unchanged
  workspace_lua_hash_applied_this_round = unchanged
  runtime_state_applied_this_round = ready_for_in_game_validation unchanged

future activation/write expectation:
  Case 2 expected bridge availability after activation = internal_only 617-N / exposed 1467+N
  Case 2 expected hash delta after activation = recorded
  Case 3 bridge availability assertion = deferred

source distribution = 617 / 7 / 1481 unchanged
```

### 4-9. Round A Validation Gates

```text
Gate A1 - Scope Gate
  [ ] ACQ_DOMINANT residual 재측정 미개방
  [ ] Layer4 Absorption policy 미정의
  [ ] source expansion 미실행

Gate A2 - Publish Principle Gate
  [ ] publish 기준이 위치 정합성으로 정의됨
  [ ] semantic_quality가 publish writer로 승격되지 않음
  [ ] 케이스 1/2/3 분류표 존재

Gate A3 - Blanket Isolation Gate
  [ ] FUNCTION_NARROW blanket isolation forbidden
  [ ] ACQ_DOMINANT blanket isolation forbidden
  [ ] future round에서도 blanket isolation 재후보화 금지 문구 존재

Gate A4 - 617 Inventory Gate
  [ ] clean branch에서는 internal_only 617 사유가 Case 1과 정합
  [ ] Case 2/3 혼입 여부 명시
  [ ] Case 2 혼입 발견 시 Round A 내부 decision delta와 exception report 첨부
  [ ] Case 2 applied artifact delta는 이번 round에서 0으로 유지
  [ ] Case 3 혼입 발견 시 Round B count >= 1 branch 및 activation-blocked handoff 명시

Gate A5 - Invariant Gate
  [ ] current round에서는 staged/workspace Lua hash unchanged
  [ ] Case 2 exception branch에서는 future activation/write expected hash delta와 activation/write round requirement 명시
  [ ] current round에서는 runtime state ready_for_in_game_validation unchanged
  [ ] Case 2 future activation/write round에서 새 build 기준 ready_for_in_game_validation 재설정 필요성 명시
  [ ] current bridge availability unchanged
  [ ] Case 2 future activation/write expected bridge availability documented
  [ ] Case 3 bridge availability assertion deferred until post-activation decision
  [ ] source distribution unchanged
  [ ] quality_baseline_v4 frozen 유지
```

---

## 5. Cross-Round Handoff Rules

### 5-1. Round B -> Round A

Round B Phase 1 detection output은 Round A Phase 2 Case 3 판정의 only accepted input이다.

```text
Round A는 LAYER4_ABSORPTION을 자체 정의하지 않는다.
Round A는 Round B의 observer-only detection result를 읽어 Case 3 handoff 여부만 판단한다.
Round A Case 3 후보가 Round B Phase 1 detector에서 verify되면
Round B count branch는 반드시 count >= 1로 해소된다.
```

### 5-2. Round A -> Round B

Round A Phase 2에서 Case 3 candidate를 발견하면 Round B에 handoff한다. 이 handoff는 Round B namespace나 detector rule을 변경하지 않는다.

Allowed handoff fields:

```json
{
  "row_id": "string",
  "full_type": "string",
  "case_candidate": "Case 3",
  "handoff_reason": "internal_only inventory found possible layer-position violation",
  "round_b_required_action": "verify_against_phase1_detection_rule",
  "round_b_branch_if_verified": "count_gte_1_policy_sealed_activation_blocked"
}
```

### 5-3. Top-doc write lock

두 round는 같은 top docs를 쓰므로 실제 실행 시 아래 순서를 따른다.

1. Round B opening top-doc update
2. Round A opening top-doc update
3. Round B closeout top-doc update
4. Round A closeout top-doc update

이 순서는 병렬 산출물 생성을 막지 않는다. 단, top-doc mutation만 serial이다.

---

## 6. Integrated Completion Checklist

Round A:

```text
1. opening decision 작성 완료
2. publish writer authority 일반 원칙 DECISIONS.md 봉인
3. FUNCTION_NARROW publish disposition delta 0 clean branch 봉인
4. FUNCTION_NARROW blanket isolation forbidden
5. ACQ_DOMINANT blanket isolation forbidden
6. ACQ_DOMINANT residual 재측정 source expansion 이후 유지
7. internal_only 617 inventory pass 또는 exception report 첨부
```

Round B:

```text
8. opening decision 작성 완료
9. LAYER4_ABSORPTION_CONFIRMED decision namespace 봉인
10. not third structural axis 명시
11. interaction-list provenance detection rule 봉인
12. SUSPECT tier 정책 봉인
13. count = 0 / count >= 1 branch 처리 명시
```

Common:

```text
14. source distribution 617 / 7 / 1481 unchanged
15. current bridge availability 617 / 1467 unchanged
    Case 2 future activation/write expected bridge availability documented
    Case 3 bridge availability assertion deferred until post-activation decision
16. current staged/workspace Lua hash unchanged
    Case 2 future activation/write expected hash delta documented
17. current ready_for_in_game_validation 유지
    Case 2 future activation/write 후 새 build 기준 재설정 documented
```

---

## 7. Execution Readiness Summary

이 계획은 두 round를 열기 위한 계획서이며, 현재 turn에서 실행하지 않는 항목은 아래다.

- `DECISIONS.md` opening/closeout entry 작성
- `ARCHITECTURE.md` publish writer authority section 추가
- `ROADMAP.md` lane 이동
- detector implementation
- dry-run measurement
- staged artifact generation
- Lua bridge or runtime mutation

후속 실행자는 이 문서를 planning authority로 읽고, Round B를 먼저 closeout한 뒤 Round A closeout을 닫는다. 병렬 진행 중에도 top-doc writer는 serial로 유지한다.
