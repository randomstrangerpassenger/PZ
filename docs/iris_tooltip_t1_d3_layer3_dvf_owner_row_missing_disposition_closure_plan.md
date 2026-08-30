# Iris Tooltip T1-D3 Layer 3 DVF Owner Row Missing Disposition Closure Implementation Plan

> 상태: planned / synchronized for parallel execution / implementation not started / owner adjudication required
> 작성일: 2026-08-28
> 기준 로드맵: `Tooltip T1-C: Upstream Correction Closure and T2 Readiness Opening`의 bounded DVF D3 slice
> 검증 깊이: metadata-only 경로는 standard, generation/public-output 경로는 heavy
> 실행 predecessor: Tooltip T1-C final commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
> 병렬 실행 계약: `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`
> 종합 검토 반영: current authoritative T1 audit를 target primary authority로 사용하고, 별도 five-gate completion framework를 두지 않으며, regular test identity delta와 producer-independent non-target invariance verdict를 formal evidence로 결속한다.
> Cycle 2 판정: pre-D3 existing candidate/material의 content identity는 고정하되 DVF owner의 unchanged approval은 D3 adjudication 중 완료할 수 있다. Historical predecessor lineage가 검증되지 않으면 closeout claim은 current-subject frozen target으로 한정한다.

이 계획은 175개의 빈 Tooltip 문장을 작성하는 계획이 아니다. Current Tooltip T1 support universe에는 Layer 3 DVF owner row가 없는 exact FullType 175개가 있지만, 코드 조사 결과 이 175개는 모두 pointer-selected current Layer 3 universe 바깥에 있다. 따라서 먼저 이 차이가 의도된 DVF 부재인지, source/input/generation 누락인지, 또는 support/universe owner 경계 문제인지 current authority로 판정해야 한다.

계획 작성 시점의 read-only 관측은 다음과 같다. 이 수치와 해시는 실행 시점 owner verdict나 terminal authority가 아니며, clean exact subject에서 다시 고정하고 비교해야 한다.

| Surface | Current code observation | Planning consequence |
| --- | --- | --- |
| T1 support union | `audit.py`가 current Layer 2, pointer-selected Layer 3, current Layer 4 owner FullType의 case-sensitive union을 만들며 현재 2,280개다. | D3는 이 owner-ratified support predicate를 재설계하지 않는다. 최초 target 175를 별도로 동결하고 denominator를 조용히 줄이지 않는다. |
| Current Layer 3 | generation `dvf33-028a3968...7145e9`의 `dvf_3_3_rendered.json`은 2,105개 exact entry를 가진다. | Current generation membership과 D3 target membership을 별도 set으로 취급한다. |
| Current selected/absence partition | 2,105개 중 single-core owner fact row 1,314개, `core_source_fact_ids=[]` row 791개, malformed role-material row 0개다. | 기존 1,314와 791은 current Layer 3 내부에서 완전히 partition된다. D3가 이를 편의상 재작성하지 않는다. |
| D3 target identity | `support - current Layer 3 = 175`이며 ordered newline identity의 조사 시점 SHA-256은 `accbe1ae691e41b1697f080f26b8206a08e261039bb7919879f67f4b5d7ef238`다. | 이 hash는 계획 근거일 뿐이다. 실행은 clean exact subject의 current authoritative T1 audit가 산출한 exact `DVF_OWNER_ROW_MISSING` set을 primary authority로 freeze하고, 검증 가능한 predecessor evidence가 있으면 lineage cross-check로 결속한다. |
| 175의 current owner-set 분포 | 171개는 Layer 4 owner input에만 있고 4개(`Base.BareHands`, `Base.Cigar`, `Base.Crayons`, `Base.Cube`)는 Layer 2에만 있다. Layer 2와 Layer 4 양쪽에 동시에 속한 target은 0개다. | D3의 첫 mutation 전에 DVF owner-boundary와 possible transfer를 진단하고 필요한 row를 escalation한다. 이 관측이나 transfer-only 상태만으로 target을 DVF denominator에서 제거하지 않는다. |
| 171 Layer 4-only row | 171개 모두 `uc.exclusion.equip_clothing` 한 건만 가지며 current T1 selection 결과는 `ineligible_exclusion`, selected public interaction 0개다. 구성은 Bandage 34, Wound 60, ZedDmg 74, stubble appearance 3이다. | Exclusion-only row가 support union에 있다는 사실은 diagnostic evidence다. 이를 곧바로 legitimate Layer 3 absence나 support-owner defect로 확정하지 않는다. |
| Current owner publisher | `build_layer3_english_localization.py`는 current generation의 exactly one `core_source_fact_id`가 있는 row만 `tooltip_t1_layer3_owner_input.json`에 발행한다. Explicit absence row는 발행하지 않는다. | A와 B를 함께 표현할 successor owner-output contract와 owner disposition input이 필요하다. |
| Current T1 audit | `audit.py`는 current generation row가 있고 core IDs가 비어 있을 때만 `DVF_CORE_DESCRIPTION_ABSENCE_PROVED`로 compact한다. Layer 3 row 자체가 없으면 무조건 `DVF_OWNER_ROW_MISSING` correction을 만든다. | D3 B를 metadata-only로 닫으려면 explicit owner absence를 검증·소비하는 audit 경로가 필요하다. Technical defect를 absence로 바꾸는 fallback은 만들지 않는다. |
| Current authority coupling | `layer3_tooltip_input_contract.json`과 `contract.py`가 producer, schema, entry count 1,314를 고정하고 있다. | D3 output schema successor와 contract validation을 함께 변경해야 하며 generated file만 단독 수정해서는 안 된다. |
| Generation lifecycle | canonical seven-input generation, external complete-generation candidate, immutable install, expected predecessor check와 single pointer switch가 이미 구현돼 있다. | Generation-bearing A가 실제로 남을 때만 existing lifecycle을 재사용한다. 별도 generation authority나 ad hoc live writer를 만들지 않는다. |

---

## 0. Parallel execution synchronization amendment

이 계획은 공통 병렬 실행 계약을 따른다. T1-D3는 T1-D1, T1-D4, T1-D5와 동시에 별도 clean worktree에서 실행하고, current ecosystem을 직접 갱신하지 않은 immutable DVF correction bundle을 T1-D6에 전달한다.

이 절은 후속 절의 current manifest/route/environment locator, `ENTRYPOINTS.md`, governance status 직접 채택, workstream별 canonical full-gate Run A/B/finalizer, current generation pointer switch와 신규 `test_tooltip_t1_d3.py` 요구를 폐기한다. 동일 내용을 담은 후속 문구보다 이 절과 공통 계약이 우선한다.

Generation-bearing A가 필요한 경우 D3는 repository-external complete-generation successor candidate와 validation/rollback manifest까지만 만든다. Current generation/pointer adoption은 T1-D6 integrated subject에서 별도 검증 후 수행한다.

공통 Tooltip T1 code/contracts/tests 변경은 isolated candidate의 `shared_path_delta`로 기록한다. Global current adoption 경로와 governance docs는 read-only다.

테스트 예산은 새 파일 `0`, 새 top-level function/family `0`이다. D3 fact/absence/invalid-disposition case는 기존 Tooltip T1 contract/audit parameter table에 통합한다. Generation-bearing 경로는 기존 DVF complete-generation/install test parameterization만 재사용한다. 기존 family로 필수 경로 실행이 불가능할 때만 기존 파일 안 parameterized function 최대 1개 예외를 허용한다.

---

## 1. Objective

Clean exact subject의 current authoritative T1 audit가 `DVF_OWNER_ROW_MISSING`으로 재구성한 D3 frozen exact 175 FullType 각각에 대해, current DVF authority 아래 다음 중 정확히 하나의 terminal disposition을 발행할 수 있는 owner-owned correction 경로를 구현한다. Verified predecessor evidence가 있고 exact set equality가 성립할 때만 이 target을 predecessor의 최초 exact 175와 같은 lineage로 주장하며, predecessor evidence를 primary mutation authority로 승격하지 않는다.

```text
A — approved DVF Layer 3 fact row

or

B — approved legitimate absence
```

A는 pre-D3 existing semantic material을 이미 존재하던 approval 또는 D3 중 DVF owner의 unchanged approval과 KO/EN authority에 결속한 row다. B는 current authority 기준으로 공개 가능한 approved core-description material이 없고 그 부재가 technical, locale, quality, approval-pending 결함이 아님을 DVF owner가 positive evidence로 승인한 row다.

최종 실행 흐름은 다음과 같다.

```text
clean exact subject
-> current authoritative T1 audit target reconstruction
-> optional verified predecessor lineage cross-check
-> exact 175 freeze
-> read-only source/fact/readiness/generation/locale census
-> owner-boundary diagnosis and current-authority consumption
-> DVF owner adjudication
-> metadata-only A/B publication first
-> conditional generation-bearing A correction only if required
-> current owner projection regeneration
-> whole-T1 re-audit
-> same-subject validation and additive closeout
```

D3 complete의 필수 결과는 다음과 같다.

```text
A + B = 175
unresolved_or_blocked = 0
D3 initial target DVF_OWNER_ROW_MISSING = 0
```

Current authority가 일부 identity를 A/B로 닫지 못하면 구현 결과를 보존하되 D3 closeout은 `partial` 또는 `blocked`로 남긴다. 175/175 count를 맞추기 위해 semantic prose, translation, alias, fallback 또는 false absence를 만들지 않는다.

---

## 2. Scope

### Included

- 실행 시점 clean current subject의 authoritative T1 audit identity 결속과, 사용 가능한 경우 predecessor Tooltip T1 corrective subject의 lineage cross-check
- D3 frozen exact 175 target의 case-sensitive ordered freeze와 immutable hash 기록. Verified-equal predecessor lineage가 없으면 historical `최초 exact 175` claim을 하지 않는다.
- 175, 1,314, 791, 2,105, 2,072, 33, 2,280 set의 count와 exact membership 관계 재구성
- current Layer 2/Layer 4에서 175가 support union에 들어오는 경로의 read-only census
- `Iris/input/items_itemscript.json`, current DVF facts/decisions/input manifest, role-material contracts, current generation, KO/EN projection과 owner output의 exact LEFT JOIN census
- current facts, existing candidate와 approval state, role-material, generation과 locale evidence를 사용하는 per-target root-cause diagnosis
- 기존 791 provenance의 read-only regression report
- cross-owner transfer 후보의 diagnostic/escalation 기록. Transfer-only 상태는 최초 175의 A/B terminal contract를 대신하지 않는다.
- current Layer 3 role-material mapping을 applicable current authority로 직접 소비하고, mapping identity를 그 근거 아래 발행된 B의 observable re-audit trigger에 결속
- generation-bearing path에서 기존 current authority가 요구하는 applicable RTC validation만 실행
- independent review가 기존 applicable authority에 의해 요구되는 경우 machine/task completion과 분리된 exact-subject governance axis로 기록
- A, B, pending technical correction, blocked/escalation을 구분하는 owner adjudication registry
- A에 대한 existing fact/source/authority/content identity binding
- B에 대한 reason, owner, acceptance evidence, applicable scope와 re-audit condition binding
- current Layer 3 owner output의 successor schema와 producer/validator
- explicit legitimate absence를 소비하는 Tooltip T1 audit successor
- metadata-only correction에서 current generation/pointer/KO·EN payload의 byte identity 증명
- pre-D3 existing material이 terminal owner approval을 얻었으나 current input/generation defect 때문에 빠졌을 때만 실행하는 conditional complete-generation successor
- affected-range validation과 whole-T1 re-audit
- current 1,314 selected-unverified state, 791 current absence-side state와 다른 correction owner 분포의 non-target reconciliation
- isolated installed-wheel candidate, immutable D3 bundle과 D6 integration manifest
- current human/machine route와 governance docs에 대한 bounded successor proposal; actual adoption은 D6 소유

### Explicitly Out Of Scope

- 새 Layer 3 semantic sentence 작성
- body summary, truncation, rewrite, rendered-text reverse parsing 또는 item-name inference
- acquisition information이나 Layer 4 interaction을 core description으로 승격
- similar-item text의 unsupported copy
- KO↔EN 번역, raw-text fallback 또는 locale별 fact reselection
- exact FullType의 lowercase/DisplayName/fuzzy/heuristic alias 결합
- current support predicate 또는 전체 Tooltip T1 contract 재설계
- 최초 175를 explicit owner decision 없이 다른 owner denominator로 이전
- 기존 1,314의 independent Menu parity `verified` 승격
- 기존 791 전체의 semantic truth 재감사
- Layer 2, Layer 4, Menu consumer, QG/locale 또는 presentation-contract blocker 자동 수정
- Tooltip T2 handoff/static payload 생성
- `IrisAltTooltip` runtime, 4-line assembly, visual fit 또는 in-game UI 변경
- full DVF truth/public-text quality/freeze 재판정
- package publication, Publish Boundary, release, Workshop 또는 deployment 판단
- D3 lifecycle command, census, external receipt를 새 regular validation authority나 stateful registry로 추가
- retired `Iris/build/description/v2/tools/build` 경로의 current writer 복원
- unrelated refactor, dependency 변경 또는 architecture redesign
- global current authority manifest/route/environment locator, command owner와 governance status 직접 갱신
- workstream별 ecosystem canonical Run A/B/comparator/finalizer 반복

---

## 3. Non-Goals

- 175를 모두 public Layer 3 body가 있어야 하는 item으로 간주하지 않는다.
- 171 exclusion-only Layer 4 row를 보고 자동으로 `B` 또는 support-owner defect를 발행하지 않는다.
- 4 Layer 2-only row의 이름, script fields 또는 classification membership으로 설명을 만들지 않는다.
- current DVF universe 2,105를 2,280으로 강제 확대하는 것을 목표로 하지 않는다.
- 반대로 current DVF universe 바깥이라는 사실만으로 175를 모두 legitimate absence로 닫지 않는다.
- search miss, fact row miss 또는 historical exclusion 문구를 positive absence proof로 사용하지 않는다.
- current 791의 `core_source_fact_ids=[]`를 D3 target 175에 복사해 B count를 맞추지 않는다.
- current owner output의 existence를 independent Menu consumer evidence로 사용하지 않는다.
- generation identity 변화만으로 기존 1,314의 semantic identity가 바뀌었다고 간주하지 않는다.
- D3 correction count 0을 전체 T1 blocker 0 또는 T2 `OPEN`과 동일시하지 않는다.
- owner review와 machine validation을 서로 대체하지 않는다.

---

## 4. Assumptions

### Repository and authority assumptions

- authority order는 `Philosophy.md -> DECISIONS.md -> ARCHITECTURE.md -> ROADMAP.md -> current authority manifest/contracts`다.
- Iris runtime은 계속 100% Lua이며 D3 diagnosis/generation/validation은 repository-side offline Python tooling에서만 수행한다.
- installed `iris_tooling` package가 current implementation/command owner다. Description-tree predecessor scripts는 historical evidence일 뿐 current 실행 권한이 없다.
- `tooltip_t1_layer3_owner_input.json`은 generated owner projection이고, human/owner adjudication authority 자체가 아니다.
- `dvf_3_3_rendered.json`은 pointer-selected current generation의 canonical runtime projection이지만, D3가 새 source fact를 역추출하는 authority는 아니다.
- current Layer 3 role-material mapping과 policy ratification은 applicable current authority로 직접 소비한다. 별도 D3-wide applicability gate를 만들지 않으며, authority conflict나 exact row 적용 불능은 해당 row의 `blocked_escalation`으로 fail-loud한다.
- repository-external D3 census, diagnosis와 closeout artifacts는 lifecycle evidence이며 regular validation authority가 아니다.
- 사용자 작업 중인 D1 plan 변경은 D3 구현과 무관한 dirty state로 보존한다. D3 machine validation은 별도 clean exact subject에서만 수행한다.

### Exact target assumptions

- 계획 조사 시점에는 exact target이 `support - pointer-selected Layer 3`와 일치하고 count가 175다.
- 실행 시 clean exact subject에서 current authoritative T1 audit를 재실행하고, 그 audit가 산출한 DVF `DVF_OWNER_ROW_MISSING` exact set을 primary freeze source로 사용한다.
- verified predecessor T1 correction ledger/receipt가 있으면 subject/hash와 exact set을 supporting lineage evidence로 비교한다. External predecessor artifact가 없다는 사실만으로 current authoritative audit가 deterministic하게 복원한 exact 175를 막지 않는다.
- current target을 authoritative하게 복원할 수 없거나, verified predecessor와 current reconstruction이 실제로 충돌하거나, governing target authority가 없거나, exact identity ambiguity가 남으면 D3를 `blocked`로 둔다.
- current re-audit에서 set delta가 발견되더라도 D3 frozen 175는 mutation accounting denominator로 유지하고 delta는 별도 reconciliation row로 기록한다.
- owner transfer가 승인되더라도 target을 175에서 삭제하지 않는다. Original A/B success contract를 충족하지 않는 transfer-only row가 남으면 D3는 `complete`가 아니다. 별도 owner decision이 terminal contract 자체를 supersede하는 경우에만 successor plan/authority에서 다시 정의한다.

### Owner adjudication assumptions

- A가 소비하는 semantic fact/material/candidate content와 source provenance는 D3 시작 이전부터 존재해야 한다. Pre-D3 identity/hash로 고정할 수 없는 content는 A 후보가 아니다.
- `approval_pending_existing_material`은 위 pre-D3 candidate를 DVF owner가 D3 adjudication 중 내용 변경 없이 승인할 수 있는 bounded 경로다. Approval timing만 D3 중일 수 있으며 candidate bytes, semantic proposition, sentence와 source binding은 바꿀 수 없다.
- D3 중 new semantic proposition, new sentence, rewrite, candidate modification 또는 replacement candidate를 만들지 않는다. Pre-D3 candidate identity와 owner-approved identity가 다르면 A로 닫지 않고 fail-loud한다.
- A가 terminal이 되는 시점에는 DVF owner approval, exact KO authority와 exact EN authority가 모두 확정되고 same candidate/fact identity에 결속돼야 한다. Tooling은 approval을 자동 발급하지 않는다.
- B는 `no current approved description-eligible material`에 대한 positive owner decision을 요구한다.
- `pipeline omission`, `manifest omission`, `generation/version mismatch`, `identity defect`, `locale gap`, `approval pending`, candidate rejection 자체, `review_required`, quality concern은 B reason이 아니다.
- 기존 vocabulary로 B reason을 표현할 수 없으면 구현자가 임의 확장하지 않는다. DVF owner가 subject-bound decision receipt를 발행하고 D6 integration proposal에 reason-registry successor를 포함해야 한다. 그 authority가 없으면 해당 row는 `blocked_escalation`으로 남긴다.
- 한 locale이라도 exact approved surface가 없으면 A는 terminal이 아니다.

### Conditional generation assumptions

- metadata-only A/B로 target을 닫을 수 있으면 current seven-input generation과 pointer를 바꾸지 않는다.
- generation-bearing A가 남을 때만 current canonical input을 corrected successor로 갱신하고 complete-generation path를 실행한다.
- generation installation 전에 expected predecessor identity와 predecessor restore availability를 결속하고, executed generation/install path에 대해 기존 current authority가 요구하는 applicable RTC validation을 실행한다. D3 전용 RTC applicability gate는 만들지 않는다.
- generation-bearing correction은 D3 target을 하나의 successor generation에 모으고 unrelated semantic rewrite를 함께 싣지 않는다.

---

## 5. Repository Areas Affected

아래에서 `(new)`는 이 계획이 의도하는 새 path이고 `(conditional)`은 owner diagnosis 결과에 따라 실제 modification에서 제외될 수 있는 path다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_t1_d3.py` (new) — exact-target freeze, census, diagnosis, adjudication validation과 D3 candidate materialization owner
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py` — lifecycle-bound D3 command routing
- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py` — approved A/B registry를 current owner output으로 deterministic projection
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py` — explicit Layer 3 owner absence의 typed validation이 필요한 경우 최소 확장
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py` — owner-output successor schema, dynamic exact-set/count binding과 absence contract validation
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py` — explicit DVF absence row 소비, D3 target reconciliation와 whole-universe re-audit
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d3_invariance.py` (new) — frozen pre-mutation baseline과 post-mutation artifact를 producer output과 독립적으로 비교하는 final non-target verdict owner
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- D3 cases are added to the existing Tooltip T1 parameterized families; no D3-specific test file
- `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json`
- `Iris/tooling/src/iris_tooling/build/build_dvf_3_3_complete_generation.py` (conditional; reuse preferred, modify only if an evidenced current contract defect exists)
- `Iris/tooling/src/iris_tooling/build/validate_dvf_3_3_complete_generation.py` (conditional)
- `Iris/tooling/src/iris_tooling/build/install_dvf_3_3_complete_generation.py` (conditional)
- `Iris/build/description/v2/tests/test_dvf_3_3_complete_generation.py` (conditional validation coverage)
- `Iris/build/description/v2/tests/test_dvf_3_3_generation_install.py` (conditional validation coverage)
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py` (conditional, executed path에 대해 existing current authority가 요구할 때)
- `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py` (conditional package projection regression)

### Docs

- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` — read-only D6 integration inputs; D3 proposal은 bundle에 기록
- `docs/iris_tooltip_t1_display_contract_policy.md` — Layer 3 explicit absence input semantics가 바뀌는 경우 bounded successor clarification
- `docs/iris_tooltip_t1_d3_layer3_dvf_owner_row_missing_disposition_closure_plan.md`
- `Iris/build/ENTRYPOINTS.md` — read-only command-owner input

### Config

- `Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.schema.json` (new)
- `Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.json` (new, owner-approved exact 175 registry)
- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json` — approved absence reason이 current vocabulary에 없을 때만 prior `DECISIONS.md` owner seal을 투영하는 additive extension
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json`
- `Iris/_docs/authority/iris_current_authority_manifest.json` — read-only D6 integration input
- `Iris/_docs/authority/iris_current_route_index.json` — read-only D6 integration input
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` (conditional generation-bearing path)
- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` (conditional)
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` (conditional)
- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` (conditional)
- `Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json` (conditional)

### Generated Artifacts

- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json` — successor owner output; approved fact rows와 explicit legitimate-absence rows를 구분
- repository-external `Layer3English/**` candidate (conditional generation/public-key proposal)
- repository-external `IrisLayer3Generations/<successor-generation-id>/**` candidate (conditional)
- current `IrisLayer3DataCurrent.lua` and current generation descriptor remain protected read-only paths
- repository-external immutable D3 result root:
  - `subject_binding.json`
  - `d3_exact_target_freeze.jsonl`
  - `d3_set_relation_report.json`
  - `d3_target_census.jsonl`
  - `d3_existing_791_provenance_report.jsonl`
  - `d3_root_cause_ledger.jsonl`
  - `d3_owner_adjudication_report.json`
  - `d3_a_correction_queue.jsonl`
  - `d3_b_publication_queue.jsonl`
  - `d3_blocked_escalation_queue.jsonl`
  - `d3_producer_non_target_observation.json`
  - `d3_independent_non_target_invariance_verdict.json`
  - `d3_generation_validation_report.json` (conditional)
  - `d3_whole_t1_reaudit_report.json`
  - `d3_axis_separated_closeout_record.json`
  - `d3_parallel_integration_manifest.json`
  - `d3_shared_path_delta.json`
  - `run_receipt.json`

---

## 6. Planned Changes

### Change 1 — Exact subject, target and protected-baseline freeze

Purpose:

최초 175 target과 기존 1,314/791/current generation state를 mutation 전에 고정한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_t1_d3.py` (new)
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py`
- repository-external `subject_binding.json`, `d3_exact_target_freeze.jsonl`, `d3_set_relation_report.json`

Implementation Notes:

- exact clean commit/tree, installed wheel identity, T1 contract bundle, current authority manifest/route와 pointer-selected generation을 hash-bind한다.
- 같은 clean exact subject에서 current authoritative T1 audit를 재실행하고 `owner=DVF owner`, `reason_code=DVF_OWNER_ROW_MISSING`, `t2_blocking=true`인 exact rows를 primary target으로 추출한다.
- row를 case-sensitive UTF-8 exact FullType로 정렬해 175개 target set과 ordered-set SHA-256을 발행한다.
- current support predicate를 독립적으로 재실행해 `support`, current Layer 3, owner fact, current absence-side set을 재구성하고 audit target과 exact set equality를 확인한다.
- 검증 가능한 predecessor T1 correction ledger/receipt가 있으면 predecessor target과 current target의 exact set을 비교해 `lineage_status=verified_equal`과 exact relation을 기록한다. Predecessor evidence가 없으면 `lineage_status=unavailable_supporting_lineage`로 기록하되 current reconstruction이 authoritative하고 deterministic하면 진행한다.
- verified predecessor target과 current target이 다르면 어느 쪽도 자동 대체하지 않고 added/removed/currently-moved delta를 기록한 뒤 governing target conflict로 fail-loud한다.
- `verified_equal`일 때만 predecessor의 historical `최초 exact 175`와 동일 set이라는 claim을 허용한다. `unavailable_supporting_lineage`에서는 `current subject authoritative audit에서 frozen exact target`까지만 주장한다.
- baseline에 current facts/decisions/manifest, generation/pointer, owner output, KO/EN public keys와 whole-T1 subject hash를 포함한다.
- current 175 밖 새 finding을 D3 mutation set에 자동 추가하지 않는다.

Validation:

```text
frozen target count = 175
duplicate exact FullType = 0
current audit target == independently reconstructed support - current Layer 3
verified predecessor/current target conflict = 0
lineage claim wording matches lineage_status
silent denominator shrink = 0
automatic identity normalization = 0
```

Predecessor evidence availability는 PASS 조건이 아니다. Current target authority/identity를 확립할 수 없거나 target identity가 계획 조사값과 다르면 조사 hash를 억지로 맞추지 않고 subject delta를 fail-loud한다.

---

### Change 2 — Exact-set reconstruction and read-only evidence census

Purpose:

175의 원인을 count 추정이 아니라 current source/fact/generation/locale evidence로 분해한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_t1_d3.py`
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/build/description/v2/data/layer3_body_role_realign/*.json`
- pointer-selected `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/<generation-id>/dvf_3_3_rendered.json`
- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`
- `Iris/media/lua/client/Iris/Data/Layer3English/**`
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`
- `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`
- `Iris/input/items_itemscript.json`

Implementation Notes:

- frozen 175를 census spine으로 사용하고 다음 relation을 LEFT JOIN한다.

```text
T1 support-source membership
current item-script identity
current DVF facts/decisions/manifest membership
role-material/readiness mapping
existing candidate/body-plan relation and approval state
pointer-selected generation membership
current owner fact projection
KO public surface
EN public surface
```

- 각 non-escalation row에 `canonical_fact_presence`, `fact_id`, `role_material_readiness`, `source_authority`, `source_provenance`, `generation_membership`, `ko/en_surface`, `possible_identity_relation`, 단일 `working_cause`, `responsible_owner`, `evidence_refs`를 기록한다.
- working cause는 roadmap의 bounded vocabulary를 사용한다.

```text
owner_projection_omission
current_input_or_generation_omission
exact_identity_binding_defect
approval_pending_existing_material
version_or_generation_mismatch
no_approved_description_material
```

Authority basis를 확립할 수 없는 row는 substantive `working_cause` single-value requirement에서 제외한다. 대신 `working_cause=null`, `intended_disposition=blocked_escalation`, `escalation_reason_code`, `supporting_evidence`를 요구해 diagnosis-final escalation state로 표현한다. 이는 A/B terminal disposition이 아니다.

- `no_approved_description_material`은 search miss가 아니라 current canonical source coverage와 owner role-material decision의 positive evidence를 요구한다.
- `approval_pending_existing_material` row는 pre-D3 candidate content/source identity와 hash를 고정한다. DVF owner가 same identity를 D3 중 unchanged approval하고 terminal 시점의 KO/EN authority가 같은 fact에 결속되면 A로 전환할 수 있다. Approval 미완료 또는 candidate identity 변경은 B로 바꾸지 않고 `blocked_escalation` 또는 applicable technical correction으로 남긴다. Candidate rejection 자체도 B를 생성하지 않는다. 다만 rejection 후 별도 owner adjudication이 current description-eligible material 부재를 positive하게 확정하고 technical/locale/quality/`review_required` defect exclusion evidence를 결속하면 working cause를 `no_approved_description_material`로 재판정해 existing B contract로 legitimate absence를 닫을 수 있다.
- historical taxonomy/exclusion 문서는 candidate evidence로만 기록하며 current fact/absence authority로 승격하지 않는다.
- 기존 791은 mutation하지 않고 provenance class만 보고한다. T1가 current generation의 empty core IDs에서 파생한 상태인지, 별도 owner absence decision이 있는지, 근거를 확립할 수 없는지를 분리한다.
- alternate spelling/case/name relation은 diagnostic candidate로만 기록하고 binding하지 않는다.

Validation:

```text
target census rows = 175
missing target census row = 0
multiple primary working cause = 0
non-escalation row without one working cause = 0
blocked escalation without escalation reason/evidence = 0
row without evidence refs = 0
automatic alias = 0
rendered prose used as new semantic authority = 0
Layer 4 promoted to Layer 3 = 0
approval-pending candidate content mutation = 0
candidate rejection used directly as B reason = 0
rejected candidate reclassified to B without separate positive absence adjudication = 0
```

Count equality와 exact set equality는 별도 필드로 기록한다.

---

### Change 3 — DVF owner adjudication registry and conditional authority use

Purpose:

Diagnosis을 implementation convenience가 아닌 explicit owner decision으로 A/B/hold에 연결한다.

Files:

- `Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.schema.json` (new)
- `Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.json` (new)
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json` (conditional additive vocabulary)
- repository-external DVF owner decision receipt; tracked governance successor는 D6 proposal
- repository-external `d3_owner_adjudication_report.json`과 queue files

Implementation Notes:

- registry는 exact frozen 175를 key set으로 갖고 각 row에 다음을 요구한다.

```text
exact_full_type
responsible_owner
working_cause  # required for non-escalation rows; null for blocked escalation
escalation_reason_code  # required only for blocked escalation
intended_disposition
supporting_evidence
required_correction_if_any
authority_decision_ref
```

- A row는 다음 필드를 요구한다.

```text
canonical_fact_id
approved_layer3_description_identity
pre_d3_candidate_identity
pre_d3_candidate_content_hash
owner_approval_ref
approved_ko_surface_ref
approved_en_surface_ref
provenance_ref
source_authority_ref
content_hash_binding
```

- B row는 다음 core contract 필드를 요구한다.

```text
absence_reason_code
owner
acceptance_evidence
applicable_scope
reaudit_condition
```

- technical/locale/quality/`review_required` defect exclusion은 permanent B row 필드를 세 갈래로 과구조화하지 않는다. Producer와 분리된 validator-side evidence report가 각 B의 acceptance evidence를 대조해 exclusion verdict를 발행한다. Tracked terminal B의 `acceptance_evidence`는 이 immutable exclusion-verdict artifact identity/hash를 참조해야 한다.
- B adoption은 `owner-proposed B candidate -> producer-independent defect-exclusion verdict -> tracked terminal B successor` 순서로 수행한다. Proposed B candidate나 self-report는 A/B completion count에 들어가지 않는다.

- `pending_required_technical_correction`과 `blocked_escalation`을 diagnosis-final non-A/B disposition으로 schema에 명시한다. 두 상태는 A/B terminal count에 들어가지 않는다.
- 171 exclusion-only Layer 4-only row와 4 Layer 2-only row의 owner-boundary를 current evidence로 제시하되 automatic transfer를 금지한다.
- cross-owner transfer 후보는 diagnostic/escalation으로만 기록한다. 승인된 transfer가 있더라도 original 175 accounting, destination owner, acceptance와 re-audit condition을 보존하며 transfer-only row는 D3 complete로 세지 않는다. A/B terminal contract를 바꾸려면 이 계획 밖의 explicit successor authority가 필요하다.
- 791 provenance는 read-only regression evidence이며 registry-level success gate가 아니다.
- current mapping은 별도 applicability gate 없이 applicable authority로 소비한다. 그 mapping을 근거로 발행한 B의 `reaudit_condition`에는 exact mapping identity 변경을 observable trigger로 포함한다.
- RTC는 generation/install 등 실제 executed path에 existing current authority가 요구하는 validation만 적용한다. Independent review도 existing applicable authority가 명시적으로 요구할 때 별도 exact-subject axis로 기록하며 machine/task D3 completion을 자동 대체하거나 새 universal gate로 확장하지 않는다.
- reason vocabulary가 부족하면 implementation code가 자유문자열 reason을 만들지 않는다. Subject-bound DVF owner decision receipt와 D6 integration proposal이 없으면 해당 row를 `blocked_escalation`으로 남겨야 한다.

Validation:

```text
registry target rows = 175
registry exact key set == frozen target set
owner-less row = 0
evidence-less row = 0
automatic A/B = 0
technical defect classified as B = 0
locale defect classified as B = 0
review_required classified as B = 0
unapproved prose accepted as A = 0
A without terminal owner approval = 0
pre-D3 candidate / owner-approved content identity mismatch = 0
terminal B without exclusion-verdict artifact binding = 0
```

---

### Change 4 — Metadata-only fact/absence owner projection

Purpose:

Generation을 바꿀 필요가 없는 A/B를 current DVF owner output에서 먼저 닫는다.

Files:

- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_t1_d3.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d3_invariance.py`
- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`
- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- existing `test_tooltip_t1_contract.py` parameter table; no D3-specific test file

Implementation Notes:

- owner output을 successor schema로 올리고 approved fact rows와 approved absence rows를 구조적으로 분리한다. Existing fact entry shape는 compatibility projection으로 보존한다.
- fact row는 existing `fact_id`, source/authority ref, exact KO/EN surface와 content binding만 복사한다. 새 sentence, translation, truncation 또는 rendered-body parsing을 수행하지 않는다.
- absence row는 owner adjudication registry의 exact B fields를 그대로 projection한다. Readiness나 missing lookup만으로 B를 생성하지 않는다.
- owner output의 generation binding은 fact rows가 참조하는 current generation과 일치해야 한다. Metadata-only B만 추가되는 경우 generation ID와 pointer는 바뀌지 않는다.
- mutation producer는 target 밖 fact/absence row를 변경하지 않았다는 lifecycle observation을 발행할 수 있지만 final invariance verdict를 소유하지 않는다.
- final invariance verdict는 producer를 import하거나 producer self-report를 신뢰하지 않는 별도 comparator가 frozen pre-mutation baseline과 post-mutation owner output/generation/locale artifacts를 직접 읽어 exact non-target byte/canonical identity를 비교해 발행한다.
- producer observation과 independent comparator가 불일치하면 fail-loud하고 complete closeout을 금지한다.
- owner output contract는 고정 숫자 1,314만 검사하지 않고 schema, exact set partition, manifest/count/hash binding을 검사한다. Actual counts는 adjudication 결과에서 계산하고 contract code에 예상 A/B 숫자를 선결정하지 않는다.
- current 791은 read-only provenance/regression evidence로만 사용한다. D3 target B를 기존 791로 합쳐 provenance를 지우거나 D3 success gate로 만들지 않는다.

Validation:

```text
new semantic proposition = 0
new authored description = 0
new locale translation = 0
fact_id drift = 0
KO/EN authority drift = 0
generation identity changed = 0
current pointer changed = 0
EN runtime payload write set = empty
target outside mutation = 0
producer-independent non-target invariance failures = 0
```

---

### Change 5 — Tooltip T1 explicit owner-absence consumption and D3 re-audit

Purpose:

T1이 positive DVF absence와 technical missing owner row를 구분하고 D3 corrected subject를 whole-universe로 다시 감사하게 한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json`

Implementation Notes:

- S2 판정 순서를 명시적으로 고정한다.

```text
valid approved fact row -> selected A
valid approved absence row -> legitimate absence B
approved fact/material with invalid/missing projection -> correction
no valid fact or absence owner row -> DVF_OWNER_ROW_MISSING
```

- valid B는 exact FullType, reason, owner, evidence, scope와 re-audit condition을 모두 검증한 뒤에만 `_slot_absent`로 들어간다.
- B가 존재해도 conflicting fact row, technical defect evidence 또는 locale defect가 함께 있으면 fail-loud한다.
- existing pointer-selected 1,314 fact rows의 Menu parity는 independent consumer evidence가 없으므로 계속 `unverified_without_independent_consumer_evidence`다.
- existing 791은 frozen baseline에서 owner-issued state와 T1-derived classification을 구분해 관찰하고, D3가 일괄 owner-approved로 rewrite하지 않는다. D3 mutation 이후 final state는 producer-independent comparator로 baseline과 대조한다.
- other-owner correction은 같은 re-audit에서 delta를 측정하되 자동 resolution하지 않는다.
- D3 corrected row가 모두 A/B여도 전체 T1 blocker가 남으면 `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS`를 유지하고 production handoff는 만들지 않는다.

Validation:

```text
initial D3 target = 175
resolved A + resolved B + unresolved/blocked = 175
both A and B for same target = 0
neither A nor B on complete target = 0
1,314 automatic verified transition = 0
unapproved 791 mutation = 0
other-owner automatic resolution = 0
cross-locale fallback = 0
```

---

### Change 6 — Conditional current DVF input/generation correction

Purpose:

Metadata-only correction 후에도 pre-D3 existing material이 이미 approved였거나 D3 owner adjudication에서 unchanged approval되어 A가 되었지만 current input/generation defect 때문에 materialize되지 못한 target만 current stateless generation path에서 복구한다.

Files:

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` (conditional)
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` (conditional)
- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` (conditional)
- `Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json` (conditional)
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` (conditional)
- existing `Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py`
- existing `Iris/tooling/src/iris_tooling/build/build_dvf_3_3_complete_generation.py`
- existing `Iris/tooling/src/iris_tooling/build/validate_dvf_3_3_complete_generation.py`
- existing `Iris/tooling/src/iris_tooling/build/install_dvf_3_3_complete_generation.py`
- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`
- repository-external successor generation candidate; current pointer remains read-only

Implementation Notes:

- execution condition은 `pending_required_technical_correction` 중 pre-D3 existing fact/material이 terminal owner approval과 both-locale authority를 얻었고 defect가 manifest/input/binding/generation membership으로 입증된 row가 하나 이상인 경우다.
- D3에서 sentence를 새로 쓰거나 candidate text를 고치지 않는다. Pre-D3 content hash와 exact byte identity가 같은 owner-approved bytes와 registered transformation만 canonical generation input에 채택한다.
- conditional mutation은 exact target row와 required manifest/count binding에 한정한다. Existing 1,314와 non-target 791의 semantic content를 보존한다.
- complete-generation candidate는 repository-external empty root에 두 번 생성해 generation ID와 ordered output bytes를 비교한다.
- validator가 canonical seven-input identity, descriptor, output universe, exact key set, locale relation과 proposed pointer payload를 검증한다. D3는 current install/pointer switch를 수행하지 않는다.
- candidate manifest는 current predecessor ID, expected pointer switch와 rollback availability를 기록해 D6가 integrated adoption을 검증할 수 있게 한다.
- Existing current authority가 candidate generation path 자체에 요구하는 applicable validation은 D3에서 실행하되 current pointer adoption은 D6에 남긴다.
- Candidate English projection과 Tooltip owner output을 같은 proposed generation에서 생성하고 KO/EN key relation을 검증한다.
- generation이 바뀌면 existing 1,314의 shared-authority relation을 predecessor에서 승계했다고 간주하지 않고 successor generation의 fact relation과 current Menu consumption path에서 다시 파생한다. Independent consumer evidence가 없으면 상태는 계속 `unverified_without_independent_consumer_evidence`다.
- generation-bearing D3 correction은 하나의 immutable successor generation에 모은다.
- generation-bearing branch의 non-target fact/absence/public payload invariance도 frozen baseline과 successor artifacts를 producer-independent comparator가 직접 비교한다.

Validation:

```text
deterministic Run A/B generation identity
exact canonical input identity
complete output universe
corrected FullType presence
pointer/generation agreement
KO/EN semantic fact identity agreement
content/hash binding
pre-D3 candidate identity == terminal owner-approved candidate identity
terminal owner approval + KO authority + EN authority present
predecessor rollback availability
non-target semantic regression = 0
successor-generation 1,314 shared-authority relation re-derived
```

금지 transformation count는 모두 0이어야 한다.

```text
new authored sentence
summary
truncation
acquisition promotion
Layer 4 promotion
unsupported cross-item reuse
name inference
locale fallback
```

---

### Change 7 — Exact-subject candidate validation, reconciliation and bundle closeout

Purpose:

D3 result, whole-T1 state와 claim boundary를 같은 final subject에 결속한다.

Files:

- existing Tooltip T1 focused test files
- conditional generation/RTC/package test files
- repository-external D3 reports and receipt
- D6 integration proposal and shared-path delta

Implementation Notes:

- workstream subject는 commit/tree, candidate wheel, frozen current authority inputs, target freeze, adjudication registry, owner output, proposed generation candidate와 applicable validation receipt를 묶는다.
- final report는 target A/B/blocked count, remaining `DVF_OWNER_ROW_MISSING`, no-content-invention, locale, exact identity, non-target regression, whole-T1 re-audit와 applicable validation 결과를 포함한다.
- predecessor T1 closeout, predecessor generation과 D3 pre-mutation registry를 제자리 수정하지 않는다. Successor adoption/closeout을 additive record로 남긴다.
- generation이 바뀌면 predecessor/successor ID, key-count delta, public count delta와 rollback relation을 기록한다.
- complete bundle closeout은 모든 target row가 terminal A/B이고 focused/candidate required command와 existing authority가 요구하는 executed-path validation이 exit 0일 때만 쓴다. Global current adoption과 ecosystem formal closeout은 D6에 남긴다.
- D3 complete를 full T1 correction, T2 `OPEN`, runtime/release completion으로 확대하지 않는다.

Validation:

```text
target A + B = 175
unresolved/blocked = 0
D3 initial target DVF_OWNER_ROW_MISSING = 0
producer-independent non-target invariance failures = 0
same-subject required validation failures = 0
```

위 조건을 충족하지 않으면 `partial` 또는 `blocked` closeout만 발행한다.

---

### Change 8 — Seal the D3 bundle and hand off to T1-D6

Purpose:

구현된 D3 owner result, shared integration delta, protected-path hashes와 claim boundary를 immutable bundle로 봉인한다.

Files:

- repository-external `d3_parallel_integration_manifest.json`
- repository-external `d3_shared_path_delta.json`
- D3 owner registry/output/candidate and validation receipts

Implementation Notes:

- D3 lifecycle command와 receipt는 workstream-local lifecycle evidence이며 regular validation authority로 등록하지 않는다.
- New test identity를 만들지 않고 existing T1/DVF parameterized families에 cases를 추가한다. Test file/function denominator delta의 기본 기대값은 `0`이다.
- Metadata-only와 generation-bearing bundle의 validation ceiling을 구분한다.
- D6 integration proposal은 current command/docs/manifest adoption을 수행하거나 그 완료를 주장하지 않는다.
- existing T1 formal-complete record와 predecessor current generation을 삭제하거나 rewrite하지 않는다.

Validation:

- bundle schema/hash/predecessor/support compatibility valid
- protected global current path mutation 0
- new test file/function denominator delta 0 unless the one-function exception is justified
- retired source-root writer re-adoption 0
- stale bare `DVF PASS`, T2 `OPEN`, release-ready overclaim 0

---

## 7. Validation Plan

### Automated Validation

#### Always required

- 기존 Tooltip T1 parameterized families에 최대 네 composite rows만 추가한다. 이미 동등한 fail-loud path를 실행하는 row가 있으면 새 row를 추가하지 않고 그 assertion을 확장한다.
  1. **disposition contract:** missing/invalid owner row, incomplete A, non-positive B와 unresolved transfer를 함께 검증한다.
  2. **no invention and locale:** alias/fallback/inference, new sentence, one-sided KO/EN과 stale approval binding을 함께 거부한다.
  3. **metadata boundary:** metadata-only path의 generation/pointer/locale bytes와 EN runtime write-set 불변을 함께 검증한다.
  4. **invariance verdict:** exact/case collision, target/non-target partition과 producer/comparator disagreement를 함께 fail-loud한다.
- current authoritative T1 audit target freeze, independent current set reconstruction과 optional verified predecessor lineage reconciliation
- schema validation for owner adjudication and owner output
- case-sensitive identity and normalized-collision detection
- no automatic alias/fallback/inference guards
- A completeness and B positive-proof completeness
- approval-pending existing material의 pre-D3 content hash, unchanged owner approval과 terminal KO/EN authority binding
- metadata-only generation/pointer/locale byte-identity check
- metadata-only EN runtime payload write-set empty check
- target/non-target mutation partition을 frozen pre-mutation baseline과 post-mutation artifacts에서 직접 비교하는 producer-independent invariance verdict
- producer observation과 independent comparator verdict의 disagreement fail-loud assertion
- focused Tooltip T1 lifecycle tests:

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

- focused pytest file/function denominator delta를 측정하고 기본값 `0`을 bundle에 공개
- installed package candidate run to a repository-external empty root
- new exact-subject whole-T1 audit and D3 reconciliation
- D3 candidate materialization Run A/Run B digest comparison and immutable bundle validation; canonical repository full validation은 T1-D6가 integrated subject에서 한 번 수행
- `git diff --check`

#### Required only for generation-bearing/public-output path

- complete generation and install focused tests:

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\build\description\v2\tests\test_dvf_3_3_complete_generation.py .\Iris\build\description\v2\tests\test_dvf_3_3_generation_install.py -q
```

- generation/install path에 대해 existing current authority가 요구하는 current-route applicable RTC tests
- current generation KO/EN exact key-set and semantic identity relation
- successor generation 기준 existing 1,314 shared-authority relation 재파생과 `unverified_without_independent_consumer_evidence` state 보존
- package build to an external root and Layer 3 projection/lookup validation:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <external-package-root> -Clean -Zip -PackageApplicability current_runtime_payload
powershell -ExecutionPolicy Bypass -File .\Iris\tools\validate_layer3_package_projection.ps1 -DataRoot <external-package-data-root> -ExpectedGenerationId <successor-generation-id>
powershell -ExecutionPolicy Bypass -File .\Iris\tools\validate_runtime_lookup_indexes.ps1 -DataRoot <external-package-data-root>
```

모든 PASS 주장은 exact relevant command exit `0`과 same-subject receipt가 있을 때만 한다. 계획에 적은 placeholder는 실행 시 validated exact path/identity로 치환한다.

### Manual Validation

- owner가 175 row의 source/provenance와 A/B/hold adjudication을 검토한다.
- 791 provenance report는 read-only regression evidence로 검토하고, cross-owner transfer 후보는 diagnostic/escalation으로 검토한다. 어느 쪽도 별도 D3 universal success gate가 아니다.
- B reason이 technical/locale/quality/review defect를 숨기지 않는지 표본이 아니라 전체 175에 대해 owner review한다.
- A의 KO/EN이 같은 semantic fact를 표현하는 terminal owner-approved surface인지 확인한다. `approval_pending_existing_material`에서 승인된 A는 pre-D3 candidate bytes/source binding과 exact identity가 같은지도 확인한다.
- generation-bearing correction이면 changed public text가 기존 approved surface의 복구인지, D3-authored prose가 아닌지 검토한다.
- whole-T1 owner distribution delta와 other-owner count를 검토한다.

이 manual review는 in-game UI acceptance가 아니라 offline authority/adjudication review다.

### Validation Limits

- independent Menu consumer fact-identity observation을 새로 수행하지 않는다.
- existing 1,314의 full Menu parity를 검증하지 않는다.
- actual Tooltip 4-line assembly, Alt input, font/UI-scale visual fit을 검증하지 않는다.
- PZ in-game runtime behavior, long-session, multiplayer 또는 arbitrary external-mod compatibility를 검증하지 않는다.
- 전체 2,105 DVF fact truth나 public-text 문체/품질을 재검증하지 않는다.
- DVF freeze, Publish Boundary, package publication, release/Workshop/deployment readiness를 판정하지 않는다.
- 다른 T1 owner correction의 semantic correctness를 검증하지 않는다.
- B의 semantic judgment를 tooling이 대체하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**높음.**

- exact 175 DVF Layer 3 fact/absence disposition
- current Tooltip-facing DVF owner output schema
- 필요 시 exact FullType ↔ current DVF fact/input binding
- explicit legitimate absence vocabulary와 owner evidence
- possible support/DVF cross-owner boundary decision

Tooltip T1의 semantic authority는 확대하지 않는다. T1은 validated owner output을 소비할 뿐 A/B를 만들지 않는다.

### Runtime Behavior Surface

**Metadata-only path에서는 없음 / generation-bearing path에서는 conditional.**

- Metadata-only B 또는 existing fact projection correction은 Lua logic과 current generation을 바꾸지 않는다.
- Generation-bearing A가 있으면 runtime이 읽는 static Layer 3 payload와 public key set이 successor generation으로 바뀔 수 있다.
- 어떤 경로에서도 Lua runtime semantic inference, fallback 또는 repair를 추가하지 않는다.

### Compatibility Surface

**직접 변경 의도 없음 / generation-bearing exact-key surface는 conditional.**

- public Lua API와 stable facade를 유지한다.
- payload schema와 require/global contract를 incompatible하게 바꾸지 않는다.
- new alias/fallback contract를 만들지 않는다.
- generation이 바뀌면 pointer, chunks, lookup, package exact-key integrity를 current validators로 검증한다.

### Sealed Artifact Surface

**높음, mutation은 conditional.**

- predecessor T1 correction/closeout
- current facts/decisions/input manifest
- role-material authority
- pointer-selected generation/descriptor/pointer
- KO/EN companion projection

Metadata-only path는 generation artifacts를 read-only로 유지한다. Generation-bearing path는 immutable successor와 additive evidence만 허용한다.

### Public-Facing Output Surface

**Metadata-only B는 없음 / generation-bearing A는 conditional.**

- Existing approved fact가 current public generation에서 누락된 defect였다면 corrected Layer 3 text가 새로 보일 수 있다.
- D3는 그 text를 작성하지 않고 existing approved locale authority를 복구한다.
- public count/key delta를 closeout에 명시한다.

---

## 9. Risk Analysis

### Architecture Risk

- current 175가 정확히 `support - Layer 3`라는 이유만으로 DVF가 다른 owner universe를 흡수할 위험
- 반대로 171 exclusion-only/4 Layer2-only 관측만으로 support owner defect를 선결정하고 D3 denominator를 줄일 위험
- T1 audit 또는 D3 tooling이 DVF semantic author/absence judge가 될 위험
- owner adjudication registry와 generated owner output이 dual semantic authority가 될 위험
- metadata-only absence를 Layer 3 generation entry로 강제해 current DVF universe 의미를 바꿀 위험
- existing current generation lifecycle 옆에 D3 전용 live writer/pointer 경로를 만들 위험
- retired source-root tooling을 current execution path로 복원할 위험

### Runtime Risk

- generation-bearing correction이 stale predecessor, wrong pointer 또는 mixed generation chunks를 노출할 위험
- KO와 EN이 서로 다른 fact/generation에 결속될 위험
- owner output은 corrected됐지만 runtime public payload가 stale인 split-brain 위험
- normal verified miss를 runtime fallback으로 바꾸는 위험
- metadata-only path에서 의도치 않게 English payload/current pointer를 재생성하는 위험

### Compatibility Risk

- exact identity correction 중 case normalization이나 heuristic alias로 distinct FullType을 병합할 위험
- public key count 변화가 stable lookup/facade/package contract와 어긋날 위험
- `Base.LemonGrass`/`Base.Lemongrass` 같은 existing case collision을 D3 validation parser가 collapse할 위험
- package에 predecessor/current generation이 함께 들어갈 위험
- support universe와 runtime item universe를 같은 contract로 오인할 위험

### Regression Risk

- technical omission을 legitimate absence로 세탁할 위험
- `review_required`, missing locale, approval pending 또는 quality concern을 B로 닫을 위험
- `approval_pending_existing_material`을 핑계로 D3 중 candidate content를 수정·교체한 뒤 pre-existing material처럼 승인할 위험
- current 791의 T1-derived state를 owner-issued B로 소급 rewrite할 위험
- existing 1,314 fact/surface semantic content가 generation-wide rewrite로 drift할 위험
- existing 1,314를 independent evidence 없이 `verified`로 승격할 위험
- target 밖 Layer 3 row 또는 other-owner correction count가 바뀌고 attribution이 누락될 위험
- acquisition/Layer 4/rendered prose가 core fact로 승격될 위험
- owner output schema count를 hard-code해 후속 exact subject에서 stale contract를 만들 위험
- focused D3 validation을 integrated D6 canonical gate로 과장할 위험
- D3 complete를 T1/T2/runtime/freeze/release completion으로 확대할 위험

---

## 10. Rollback Plan

### Before owner adoption

- repository-external census/diagnosis candidate가 실패하면 current source, owner output, generation과 pointer를 변경하지 않는다.
- failed candidate는 PASS로 덮어쓰지 않고 failed immutable evidence로 남기거나 폐기한다.
- current authoritative audit와 independent reconstruction으로 governing target을 확립할 수 없거나 verified predecessor와 실제 충돌하면 D3를 `blocked`로 두고 175 closure를 강제하지 않는다. Supporting predecessor artifact의 단순 unavailable은 단독 blocker가 아니다.

### Metadata-only correction

- invalid owner adjudication/absence row는 owner registry successor에서 supersede하고 해당 FullType을 `unresolved/blocked`로 되돌린다.
- prior `tooltip_t1_layer3_owner_input.json` schema/output과 T1 consumer behavior를 복구한다.
- underlying generation, pointer, KO/EN payload는 metadata-only path에서 애초에 변경하지 않는다.
- 다른 absence identity나 fuzzy alias로 우회하지 않는다.

### Generation-bearing correction

- predecessor generation은 immutable하게 유지한다.
- candidate manifest에 D6가 검증할 expected predecessor와 restore availability를 기록한다.
- candidate/validation/install failure에서는 current pointer를 바꾸지 않고 D3 bundle을 `blocked` 또는 `implemented_only`로 봉인한다.
- current pointer switch와 실제 rollback 실행은 D6 integration 범위다. D3는 predecessor 복구 절차와 검증 가능한 rollback metadata만 제공한다.
- invalid successor generation과 failure receipt는 historical trace로 남기고 제자리 수정하지 않는다.
- candidate rollback simulation은 owner output과 EN companion이 declared predecessor generation에 다시 일치하는지 검증한다.

### Documentation and authority

- adopted registry/contract/docs를 조용히 rewrite하지 않는다.
- 오류 발견 시 additive successor/supersession record를 만든다.
- predecessor T1 formal-complete record와 D3 failed/partial closeout을 삭제하지 않는다.

### Immediate stop conditions

다음 중 하나라도 발생하면 complete closure를 중단한다.

```text
A에 새 semantic sentence가 필요함
A에 임의 KO/EN translation 또는 fallback이 필요함
B 근거가 technical/locale/quality/review defect뿐임
canonical source authority를 확립할 수 없음
exact identity가 unresolved임
current authorities가 conflict함
owner가 absence를 승인하지 않음
approval-pending candidate의 pre-D3 identity/hash를 고정할 수 없거나 owner-approved identity와 달라짐
required reason vocabulary가 승인되지 않음
owner transfer가 denominator shrink에만 사용됨
current mapping authority가 conflict하거나 exact row에 적용될 수 없음
executed generation/install path가 요구하는 current RTC validation을 식별·실행할 수 없음
generation-bearing candidate가 D6 adoption에 필요한 predecessor restore metadata를 제공하지 못함
```

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 evidence, neutrality, insufficient evidence에서의 silence, Menu/Tooltip same-facts와 100% Lua runtime 원칙을 보존한다.
- Iris는 Pulse 외 다른 Spoke를 직접 참조하지 않는다.
- DVF System은 Layer 3 semantic composition/owner authority를 유지한다.
- T1은 projection/readiness/audit만 소유하고 semantic fact나 legitimate absence를 발명하지 않는다.
- Layer 3는 optional explanation layer이며 모든 item에 body를 강제하지 않는다.
- `core_description`과 `acquisition_information`을 분리한다.
- Layer 4 interaction은 Layer 3 role material로 승격하지 않는다.
- rendered prose에서 source fact를 역파싱하지 않는다.
- exact FullType은 case-sensitive identity다.
- DisplayName, lowercase, fuzzy match, heuristic alias와 predecessor spelling 자동 치환을 금지한다.
- identity를 locale보다 먼저 선택한다.
- KO와 EN은 같은 semantic fact identity에 결속한다.
- cross-locale raw-text fallback과 locale별 fact substitution을 금지한다.
- technical defect, review state와 missing locale를 legitimate absence로 숨기지 않는다.
- Pre-D3 existing candidate/material은 DVF owner가 D3 adjudication 중 unchanged approval할 수 있지만, D3가 content를 작성·수정·교체하거나 tooling이 approval을 자동 발급하지 않는다.
- current 175 denominator를 explicit authority 없이 축소하지 않는다.
- existing 1,314의 semantic identity/content와 unverified Menu parity state를 보존한다.
- existing 791을 convenience B registry로 일괄 rewrite하지 않는다.
- historical/predecessor/reproduction artifact는 diagnosis evidence로만 사용하고 current authority로 자동 승격하지 않는다.
- metadata-only와 generation-bearing correction을 분리하고 cheaper valid path를 먼저 닫는다.
- generation-bearing correction은 canonical seven-input stateless generation, immutable successor와 single pointer contract를 사용한다.
- predecessor generation과 sealed T1/D3 evidence를 보존한다.
- installed `iris_tooling` package가 current implementation/command owner다.
- output은 repository-external immutable empty root를 사용하고 mutable latest pointer/stateful registry를 만들지 않는다.
- D3 lifecycle command/receipt는 새 regular validation authority로 승격하지 않는다. 신규 D3 test file/function을 만들지 않고 기존 parameterized family의 case delta만 공개한다.
- owner output이 Menu consumer evidence를 self-attest하지 않는다.
- same-subject exact relevant command exit `0` 없이는 PASS를 주장하지 않는다.
- D3 result를 full T1 closure, T2 `OPEN`, runtime, RTC 전체, freeze, Publish, package publication, release, Workshop 또는 deployment PASS로 확대하지 않는다.

---

## 12. Expected Closeout State

### Planning-time expected closeout

Expected closeout target: **conditional / owner-gated**

D3 closeout은 다음 중 하나다.

```text
complete
partial
blocked
```

- `complete`: exact 175 전부가 validated owner-approved A 또는 B이고 existing current authority가 요구하는 모든 executed-path validation이 same-subject로 닫혔다.
- `partial`: 유효한 A/B와 correction을 보존했지만 일부 owner/authority/locale/identity/technical blocker가 남았다.
- `blocked`: current governing target authority, canonical source basis 또는 required owner decision이 없거나 verified predecessor/current target이 실제로 충돌해 의미 있는 mutation으로 진행할 수 없다.
- implementation은 끝났지만 required validation이 없으면 `implemented_only` ceiling을 사용하고 `complete`를 주장하지 않는다.

Planning-time census가 `171 exclusion-only + 4 Layer 2-only`를 가리키므로 current owner evidence가 175 전부를 A/B로 닫지 못하면 `partial` 또는 `blocked`가 정상적인 fail-loud 종결이다. `complete`를 목표 수치로 강제하지 않는다.

### Complete criteria

다음 조건을 모두 만족해야 한다.

1. D3 frozen exact 175가 immutable target freeze에 결속된다. `lineage_status=verified_equal`일 때만 predecessor의 historical 최초 exact 175와 동일 set임을 주장하고, `unavailable_supporting_lineage`이면 current-subject target claim으로 한정한다.
2. duplicate, lost target와 silent denominator shrink가 0이다.
3. 175 전부가 정확히 하나의 terminal A 또는 B를 가진다.
4. `A + B = 175`, `unresolved/blocked = 0`, D3 initial target 범위의 `DVF_OWNER_ROW_MISSING = 0`이다. Target 밖 새 finding은 별도 reconciliation에 남긴다.
5. 모든 A가 exact FullType, canonical fact ID, pre-D3 material identity/hash, terminal owner approval, approved description identity, KO/EN, provenance/source authority와 content/hash binding을 가진다. D3 중 unchanged approval된 candidate는 pre-D3 identity와 terminal approved identity가 exact-equal하다.
6. 모든 B가 exact FullType, approved reason, owner, acceptance evidence, applicable scope와 observable re-audit condition을 가지며 acceptance evidence는 producer-independent defect-exclusion verdict artifact identity/hash를 참조한다.
7. technical/locale/quality/review defect가 B로 전환된 수가 0이다.
8. new prose, summary, truncation, acquisition/Layer 4 promotion, unsupported copy, name inference와 locale fallback이 0이다.
9. frozen pre-mutation baseline과 post-mutation artifacts를 mutation producer와 분리된 comparator가 비교한 결과 existing 1,314 및 모든 non-target surface에 D3-induced semantic regression이 없다.
10. existing 1,314의 automatic Menu parity verified transition이 0이다.
11. existing 791에 authority 없는 mutation이 없다.
12. 모든 A의 KO/EN은 같은 semantic fact identity에 결속된다.
13. generation correction이 있었다면 current stateless generation/immutable install/single-pointer/rollback contract를 만족하고 successor generation 기준으로 existing 1,314 shared-authority relation을 재파생한다.
14. final corrected subject에서 affected-range validation과 whole-T1 re-audit가 모두 수행된다.
15. focused/candidate/bundle validation이 exact relevant command exit 0이며 integrated canonical full validation은 T1-D6에 유보된다.
16. other-owner correction은 자동 해결되지 않고 delta/owner attribution이 보존된다.
17. 전체 T1 blocker가 남으면 `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS`를 유지한다.
18. predecessor T1 correction state와 predecessor generation이 historical trace로 남는다.
19. D3 lifecycle command/receipt가 regular validation authority로 승격되지 않았고 test file/function denominator delta가 기본값 `0`으로 공개된다.
20. 791 provenance는 read-only evidence, transfer는 diagnostic/escalation, mapping은 current applicable authority, RTC는 existing authority가 요구하는 executed-path validation, independent review는 applicable할 때 별도 governance axis로 유지되며 이들을 새 universal D3 completion gate로 사용하지 않는다.

### Expected successful D3 claims

Complete 후 다음만 주장할 수 있다.

- Current-subject D3 frozen exact 175가 current DVF authority 아래 A 또는 B로 disposition되었다.
- `lineage_status=verified_equal`인 경우에만 위 set이 predecessor의 historical 최초 exact 175와 동일하다고 추가 주장할 수 있다. `unavailable_supporting_lineage`에서는 이 historical lineage claim을 하지 않는다.
- D3 target의 `DVF_OWNER_ROW_MISSING`이 0이다.
- D3가 새 Layer 3 semantic prose나 locale translation을 작성하지 않았다.
- 모든 A가 exact fact identity와 같은-fact KO/EN authority에 결속된다.
- 모든 B가 explicit owner/evidence/reason/scope/re-audit condition을 가진다.
- 기존 selected/absence-side state와 other-owner correction에 bounded regression 검사를 수행했다.
- workstream exact subject에서 affected/whole-T1 candidate re-audit와 applicable focused validation을 수행했다.
- generation correction이 있었다면 existing DVF generation lifecycle을 사용했다.

### Explicitly not established

D3만으로 다음은 성립하지 않는다.

- existing 1,314의 independent Menu parity verification
- full Layer 3 Menu parity
- Tooltip T1 전체 upstream correction closure 또는 global current adoption
- T2 readiness `OPEN`
- T2 static generation 또는 runtime adoption
- actual Alt Tooltip/4-line visual fit
- full DVF truth/public-text quality audit
- DVF freeze readiness
- Runtime Compatibility 전체 PASS
- Publish Boundary PASS
- package publication, release, Workshop 또는 deployment readiness

D3의 terminal boundary는 다음과 같다.

```text
current DVF source/owner authority
-> exact 175 A/B disposition
-> Tooltip T1 projection/readiness re-audit
-> remaining owner blockers preserved
-> T2 OPEN only in a later whole-T1 zero-blocker decision
```
