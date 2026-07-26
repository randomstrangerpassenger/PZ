# DVF 3-3 Facts Authority Enrichment Plan

Status: **draft / non-executable / owner review required**

## 1. Purpose

`attempt-0014-remediation`이 증명한 317개 식품 row의 Layer 3-3 semantic information 부족을 DVF Body Compiler나 Layer 4 QG에 전가하지 않고, 별도 DVF 3-3 facts authority round에서 조사·보강·승격하기 위한 계획 초안이다.

이 계획은 facts mutation을 승인하지 않는다. 실행 전 field schema, evidence admissibility, row universe, writer allowlist, owner approval과 exact input hashes를 별도 seal해야 한다.

## 2. Preserved predecessor evidence

- Naturalization predecessor: `attempt-0014-remediation`
- Immutable cause analysis:
  `Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0014-remediation/phase3/repeated_skeleton_cause_analysis.json`
- Blocking semantic condition digest:
  `3707352bc4e8363e712ffc383a0ecdb2d5f1d8cfd74ff54a15531485f934738e`
- Blocked row count: `317`
- Existing repetition limit at the preserved readpoint: `104`
- Minimum semantic partitions needed by the downstream detector at that readpoint: `4`

`317`, `104`, `4`는 enrichment 목표값이나 taxonomy 정답이 아니다. 이 값들은 동일한 approved semantic condition이 현재 downstream realization을 막았다는 predecessor evidence일 뿐이다.

## 3. Authority boundary

### DVF 3-3 facts authority

다음을 소유한다.

- Layer 3-3 body가 소비할 semantic facts와 proposition provenance
- facts field/schema 변경 제안
- raw evidence의 admissibility 판정
- row별 enrichment candidate와 evidence binding
- 새 `dvf_3_3_facts.jsonl` 및 input manifest 승격
- predecessor facts hash의 supersession 기록

### Layer 4 QG

Layer 4 QG는 recipe, right-click source, 요구조건, 사용 맥락 등 상호작용 정보 산출물의 품질 게이트다.

Layer 4 QG는 다음을 소유하지 않는다.

- Layer 3 facts 부족의 기본 routing
- `dvf_3_3_facts.jsonl` writer authority
- food subtype의 자동 추론·승격
- Layer 4 trace를 Layer 3 proposition으로 자동 복사하는 권한

Layer 4 evidence가 enrichment 후보로 유용하더라도 별도 cross-layer promotion decision과 row-level provenance가 없으면 Layer 3 facts authority가 될 수 없다.

## 4. In scope

- 317-row exact predecessor universe 재확인
- current facts에서 실제로 비어 있는 구분 축 census
- 다음 raw candidate input의 provenance·admissibility 조사
  - `Iris/input/items_itemscript.json`
  - `Iris/output/tags_by_fulltype.json`
  - `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`
- evidence-backed food distinction schema 초안
- row별 enrichment candidate와 evidence reference
- facts/manifest candidate diff
- independent validation과 owner approval packet
- naturalization Phase 2 재봉인을 위한 immutable handoff

## 5. Out of scope

- `attempt-0014-remediation` 수정
- naturalization candidate 생성
- naturalization Phase 4~8 실행
- Publish Boundary attempt 실행
- Layer 4 corpus·QG policy·Layer 4 trace 변경
- repeated-skeleton detector, ratio, threshold 또는 waiver 변경
- item ID, hash, 배열 순서, 난수 기반 subtype 생성
- 같은 의미를 표현만 바꿔 여러 facts로 복제
- current runtime/Lua/package mutation

## 6. Candidate semantic dimensions

아래는 조사 대상 후보이며 승인된 schema가 아니다.

- `consumption_role`
  - cooking ingredient
  - ready-to-eat food
  - snack
  - meal component
- `preparation_requirement`
  - none
  - preparation required
  - cooking required
- `edibility_state`
  - raw-edible
  - cooked-only
  - already prepared
- `preservation_mode`
  - fresh
  - dried
  - canned/preserved
  - shelf-stable packaged
- `consumption_medium`
  - solid food
  - beverage
- `distinct_acquisition_or_use_mode`

각 값은 admissible evidence와 qualifier를 가져야 한다. evidence가 없으면 값을 추정하지 않고 row를 unresolved로 유지한다. downstream count를 맞추기 위한 taxonomy 분할은 금지한다.

## 7. Proposed phases

### Phase 0 — Read-only authority preflight

- predecessor attempt와 correction record hash 확인
- current facts/decisions/input-manifest hash 확인
- protected surface snapshot 생성
- Layer 4 QG non-routing contract 확인
- writer allowlist는 비어 있는 상태로 시작

Exit: read-only input identity가 고정되고 authority ambiguity가 `0`이다.

### Phase 1 — Evidence and field census

- 317-row exact universe 재구성
- candidate raw input별 사용 가능한 field와 provenance 집계
- 동일 이름·대소문자·variant family를 별도 식별
- raw field가 사실, 분류, 상호작용 trace 또는 display metadata 중 무엇인지 분류

Exit: evidence coverage와 missingness를 count로 기록하되 enrichment를 아직 쓰지 않는다.

### Phase 2 — Schema and admissibility proposal

- 최소 필요 field와 closed enum 제안
- field별 allowed evidence source와 disallowed inference 정의
- qualifier/modality/condition 보존 규칙 정의
- Layer 4 evidence의 cross-layer promotion 필요 여부를 별도 표시
- owner가 schema와 evidence policy를 승인

Exit: approved schema hash와 admissibility policy hash가 존재한다.

### Phase 3 — Attempt-local enrichment candidate

- row별 evidence-backed facts candidate 생성
- 기존 proposition 보존과 additive field provenance 기록
- unresolved row는 임의 default 없이 fail-loud 유지
- item ID/hash/randomness가 값 선택에 관여하지 않았음을 증명

Exit: enrichment candidate, row diff ledger, provenance ledger가 attempt-local로 존재한다.

### Phase 4 — Facts validation

- schema 및 closed-enum validation
- source reference existence/hash validation
- cross-row determinism
- evidence-to-value consistency
- unsupported fact count `0`
- Layer 4 automatic promotion count `0`
- existing approved fact deletion/strengthening count `0`

Downstream skeleton count는 진단으로만 계산할 수 있으며 facts acceptance 기준을 대신하지 않는다.

### Phase 5 — Owner approval and facts-authority seal

- exact enriched facts hash
- exact updated input-manifest hash
- row universe/key-set digest
- predecessor/successor diff digest
- schema/admissibility/provenance hashes
- independent review result
- owner approval

Exit: facts-authority successor candidate가 sealed된다. 이 단계도 runtime/candidate adoption을 의미하지 않는다.

### Phase 6 — Naturalization handoff

- successor facts와 manifest의 canonical paths/hashes 전달
- naturalization earliest resume phase를 `phase2_source_inventory_reseal`로 고정
- old candidate/human review/handoff/Publish disposition은 재사용 금지

Exit: 새 naturalization attempt를 열 수 있는 input packet이 준비된다.

## 8. Required artifacts

Proposed root:

`Iris/build/description/v2/staging/dvf_3_3_facts_authority_enrichment/<attempt-id>/`

Required candidates:

- `phase0/authority_preflight.json`
- `phase0/protected_surface_snapshot.json`
- `phase1/blocked_row_universe.jsonl`
- `phase1/raw_evidence_field_census.json`
- `phase1/evidence_role_matrix.json`
- `phase2/facts_enrichment_schema.json`
- `phase2/evidence_admissibility_policy.json`
- `phase2/owner_schema_approval.json`
- `phase3/enriched_facts_candidate.jsonl`
- `phase3/facts_diff_ledger.jsonl`
- `phase3/fact_provenance_ledger.jsonl`
- `phase4/facts_validation_report.json`
- `phase4/no_layer4_auto_promotion_report.json`
- `phase4/no_item_id_hash_random_inference_report.json`
- `phase5/facts_authority_seal.json`
- `phase6/naturalization_source_inventory_handoff.json`

## 9. Validation requirements

- predecessor attempt bytes unchanged
- 317-row universe identity exact
- every new field value has admissible evidence
- unsupported enrichment count `0`
- existing proposition deletion count `0`
- modality/qualifier strengthening count `0`
- item-ID-derived classification count `0`
- hash/random-derived classification count `0`
- Layer 4 QG automatic routing count `0`
- Layer 4 trace direct facts-authority read count `0`
- protected current/rendered/Lua/runtime/package mutation count `0` before approved seal
- same inputs produce byte-identical enrichment candidate and ledgers

## 10. Retry and rollback

- 실패한 attempt는 수정하지 않고 새 facts-enrichment attempt를 연다.
- schema나 admissibility policy가 바뀌면 Phase 2부터 다시 실행한다.
- raw evidence set이나 317-row universe가 바뀌면 Phase 0부터 다시 실행한다.
- sealed successor facts가 naturalization에서 semantic preservation을 통과하지 못하면 facts seal을 삭제하지 않고 superseding disposition을 추가한다.
- rollback은 predecessor facts authority hash를 계속 current로 유지하는 방식이며, 실패 candidate를 current facts에 부분 적용하지 않는다.

## 11. Draft completion condition

이 초안은 다음을 승인하지 않는다.

- facts mutation
- Layer 4 QG 변경
- naturalization candidate 생성
- Publish 재시도

실행 계획으로 승격하려면 최소한 schema/admissibility owner, independent reviewer, exact protected paths, writer allowlist, command matrix와 seal contract를 추가 검토해야 한다.
