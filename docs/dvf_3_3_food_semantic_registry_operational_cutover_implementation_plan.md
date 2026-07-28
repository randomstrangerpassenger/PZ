# Implementation Plan

> 계획명: DVF 3-3 Food Semantic Registry Operational Cutover
>
> 상태: amended-after-independent-review / independent-re-review-pending / exact-owner-authorization-pending / implementation-not-started
>
> Global stage: `G3_registry_food_successor_operational_cutover`
>
> G2 terminal subject commit: `319fa3cf439d72703b888a4ddb19c961c86bf3f7`
>
> Governing boundary-doc descendant: `f68d1db963ed945d4019215d85a6ad8bf8be9211`
>
> Predecessor Food attempt: `attempt-0022`
>
> Predecessor terminal hash seal SHA-256: `9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19`
>
> Maximum terminal claim: `food_semantic_registry_adoption = current_adoption_complete`

---

## 1. Objective

G2에서 봉인한 exact DVF 3-3 food-semantic successor를 Iris Artifact Registry
책임 아래 current facts authority로 process-crash recoverable, manifest-last,
fail-closed transaction을 통해 채택하고, Registry adoption receipt와
Naturalization Phase 2 공식 소비 계약을 봉인한다.

두 개의 기존 경로를 순차 교체하므로 모든 reader가 중간 상태를 절대 관측할 수
있다는 single-filesystem-primitive atomicity나 power-loss atomicity는 주장하지
않는다. Canonical readpoint는 두 파일 교체, post-write verification, adoption
commit, committed-blob identity verification이 모두 끝난 뒤에만 열린다.

이 계획은 다음 모순을 명시적으로 해소한다.

* G2 successor facts는 current facts에 byte-identical하게 채택할 수 있다.
* G2 successor manifest는 `non_current=true`,
  `current_adoption_allowed=false`, attempt-local facts path를 포함하므로 current
  manifest에 그대로 복사할 수 없다.
* 기존 Naturalization v1 동기화 문구의
  `current_input_manifest_sha256 = selected_successor_manifest_sha256`는 위 두 역할을
  혼합한다.

따라서 Registry는 successor facts bytes를 그대로 채택하되, successor manifest를
닫힌 allowlist로 변환한 current-adoption projection을 생성한다. Adoption receipt는
원 successor manifest와 current manifest의 서로 다른 SHA-256, 허용된 field delta,
current facts의 successor byte identity를 함께 결속한다.

---

## 2. Scope

포함 범위:

* sealed G2 terminal evidence와 successor four-identity set 검증
* current facts/manifest preimage 결속
* deterministic current-adoption manifest projection
* current facts/manifest의 cross-checkout byte identity 고정
* candidate-first cutover writer와 exclusive lock/journal/rollback
* exact owner authorization 및 one-use nonce
* current facts와 current manifest의 manifest-last, process-crash-recoverable
  Registry transaction
* append-only Registry adoption receipt
* Naturalization Phase 2 consumer 계약의 v2 adoption projection 동기화
* current-input no-render handoff
* 기존 Registry Runtime Compatibility readpoint의 source-payload staleness 표식
* scoped final validation과 독립 Codex Reviewer closeout
* owner final seal과 terminal hash seal

### Explicitly Out Of Scope

* G2 `attempt-0022` 산출물 수정 또는 재봉인
* 식품 semantic 값·schema·curated approval·proposition 수정
* Layer 4 QG 정책 또는 Layer 4→Layer 3 승격
* rendered description 생성
* Naturalization candidate 생성 또는 Phase 3~8
* Publish Boundary 재시도
* repeated-skeleton detector·threshold·waiver 변경
* Lua/runtime chunk/package 변경
* Registry Runtime Compatibility successor closure 또는 suite 재실행
* Workshop, release readiness
* 전체 `test_*.py`, full-repository gate, historical/obsolete suite

---

## 3. Non-Goals

* Registry Authority Closure 전체를 이 cutover로 대체하지 않는다.
* public prose 품질 또는 Publish acceptance를 주장하지 않는다.
* current manifest를 successor manifest와 거짓 byte-equality로 맞추지 않는다.
* attempt-local successor path를 영구 current facts path로 사용하지 않는다.
* Git checkout line-ending 변환을 authority identity로 오인하지 않는다.
* partial promotion, dual current, predecessor fallback을 허용하지 않는다.

---

## 4. Assumptions and Entry Predicates

다음 exact predicate가 모두 참이어야 candidate build를 시작할 수 있다.

```text
g2_terminal_subject_commit =
  319fa3cf439d72703b888a4ddb19c961c86bf3f7
governing_boundary_doc_commit =
  f68d1db963ed945d4019215d85a6ad8bf8be9211
g2_terminal_and_governing_doc_are_implementation_ancestors = true
reviewed_plan_blob_is_present_at_implementation_base_head = true

food_attempt_id = attempt-0022
food_terminal_hash_seal_sha256 =
  9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19
food_independent_review_sha256 =
  8c71275aee4c397b959d74bed25848850b36d699736cc1e8657287377105bce6
food_final_artifact_manifest_sha256 =
  7e72bb17d7ff45abcf20fe9ca939f8e52779f3fd0e8da4646265c61b1557d620

selected_successor_facts_sha256 =
  1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40
selected_successor_manifest_sha256 =
  d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a
selected_schema_sha256 =
  66f9eb59ea2cfec3fb5d647345ce5ab07ae17d0ba70b62c52b6bcaa7e3f32563
selected_proposition_license_sha256 =
  60f68c3e06fd148fce55072e1b7420165e10db16fc4e4b132b3fba7ae83e6edd

current_facts_preimage_sha256 =
  a89af8d75a78a57bd2ac05f07af4246d1ebab862dd4021bd089c5efa6e533be6
current_manifest_preimage_sha256 =
  db4c5e827c1aad4175894fb0f5b59db9496c5819cacd86a9f703d3542a05be41

food_terminal_status = PASS
food_terminal_value = sealed_successor_handoff_complete
food_post_terminal_claim_bearing_change_count = 0
candidate_entry_tracked_worktree_clean = true
independent_plan_review = PASS
open_critical_count = 0
open_important_count = 0
```

현재 Registry canonical-closure 계획은 live current writer를 금지하고 별도 reviewed
operational-cutover 계획을 요구한다. 이 문서가 그 별도 계획이며 기존 Registry
closure의 다른 WP 또는 terminal claim을 소비하거나 대체하지 않는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/dvf_3_3_food_semantic_registry_cutover.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_registry_cutover.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
* `Iris/tools/package_iris.ps1`
* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_bridge.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_package.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py`

### Current Authority

* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`

### Contracts and Docs

* `.gitattributes`
* `.gitignore`
* `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`
* `Iris/_docs/authority/food_semantic/registry_adoption_contract.json`
* `Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/food_semantic_registry_adoption_contract.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/dvf_3_3_food_semantic_registry_operational_cutover/independent_plan_review.json`

### Generated Attempt Artifacts

* `Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/attempts/<attempt-id>/`
* `candidate/current_facts.jsonl`
* `candidate/current_input_manifest.json`
* `candidate/adoption_projection_diff.json`
* `preflight/current_preimage_report.json`
* `preflight/registry_runtime_compatibility_collision_impact_report.json`
* `preflight/startup_recovery_report.json`
* `reviews/independent_pre_cutover_review.json`
* `authorization/owner_cutover_authorization.json`
* `transaction/cutover_journal.json`
* `transaction/rollback_snapshot_manifest.json`
* `closeout/registry_adoption_receipt.json`
* `closeout/current_identity_report.json`
* `closeout/naturalization_phase2_current_handoff.json`
* `closeout/final_validation_receipt.json`
* `closeout/independent_closeout_review.json`
* `closeout/owner_seal.json`
* `closeout/terminal_hash_seal.json`

---

## 6. Planned Changes

### Change 1 — Successor and Current Preimage Binding

Purpose:

* G2 terminal seal에서 successor four-identity를 재계산한다.
* current facts/manifest의 exact preimage를 결속한다.

Implementation Notes:

* SHA는 working-file bytes와 Git blob bytes를 별도 필드로 기록한다.
* CRLF/LF 차이를 숨기는 임의 normalization hash를 authority SHA로 사용하지 않는다.
* predecessor current facts/manifest가 entry hash와 다르면 candidate도 만들지 않는다.
* G2 산출물은 read-only다.
* independent plan review는 reviewed plan의 working-byte SHA-256과 Git blob ID를
  함께 결속한다.
* `implementation_base_head`는 그 exact reviewed plan blob과 initial/re-review
  record를 처음 함께 포함한 clean commit으로 review binding에 기록한다.
* candidate prepare는 `319fa3cf...`와 `f68d1db9...`가
  `implementation_base_head` 및 implementation commit의 ancestor인지, implementation
  commit에 같은 plan blob이 존재하는지 fail-closed로 검사한다.
* `candidate_entry_tracked_worktree_clean`은 ignored attempt-local evidence를 제외한
  tracked/untracked Git status가 비어 있음을 뜻하며, 현재 untracked draft 상태를
  entry PASS로 간주하지 않는다.

Validation:

* terminal seal→owner seal→review→manifest→successor 연쇄가 일치한다.
* current preimage mismatch count가 0이다.

### Change 2 — Closed Current-Manifest Adoption Projection

Purpose:

* non-current successor manifest에서 current manifest를 결정론적으로 만든다.

허용 변경은 다음뿐이다.

| Field | Successor value | Current projection |
|---|---|---|
| `status` | `sealed_successor_handoff` | `current_authority` |
| `authority_role` | `sealed_non_current_successor` | `successor_current_source_authority` |
| `facts.path` | attempt-local successor path | `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` |
| `facts.role` | `sealed_non_current_successor` | `current_source_authority` |
| `food_semantic_authority.non_current` | `true` | `false` |
| `food_semantic_authority.current_adoption_allowed` | `false` | `true` |
| `food_semantic_authority.registry_adoption_state` | absent | `current` |
| `food_semantic_authority.registry_cutover_attempt_id` | absent | current cutover attempt |
| `food_semantic_authority.source_successor_manifest_sha256` | absent | `selected_successor_manifest_sha256` |
| `source_promotion.food_semantic_successor_binding` | absent | exact predecessor hashes and paths |

그 밖의 모든 field/value는 successor manifest와 deep-equal해야 한다.
`facts.sha256`은 installed current facts의 exact byte SHA와
`selected_successor_facts_sha256` 모두와 같아야 한다.

Validation:

* allowlisted delta 외 manifest difference count가 0이다.
* 2105 rows와 317 target member identity가 유지된다.
* schema/license/proposition inventory hash가 바뀌지 않는다.

### Change 3 — Cross-Checkout Byte Identity

Purpose:

* Windows Git line-ending conversion으로 current authority hash가 checkout마다
  달라지는 문제를 제거한다.

Implementation Notes:

* `.gitattributes`에 아래 exact 두 경로만 `-text`로 추가한다.

```gitattributes
Iris/build/description/v2/data/dvf_3_3_facts.jsonl -text
Iris/build/description/v2/data/dvf_3_3_input_manifest.json -text
```

* broad data/staging pattern은 추가하지 않는다.
* candidate facts/manifest bytes를 그대로 current target에 설치한다.
* transaction receipt는 Git blob identity를
  `pending_adoption_commit`으로 기록한다.
* adoption commit 뒤 final identity receipt와 terminal seal이 Git blob SHA와
  working-file SHA의 equality를 기록한다.
* `.gitignore`에는 아래 exact implementation/test/durable attempt root만
  exception으로 추가한다. 다른 staging 또는 tools/tests pattern을 열지 않는다.

```gitignore
!Iris/build/description/v2/tools/build/dvf_3_3_food_semantic_registry_cutover.py
!Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_registry_cutover.py
!Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/
!Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/**
```

Validation:

* 두 current target의 `git ls-files --eol` 결과가 `attr/-text`다.
* committed blob bytes와 checked-out file bytes가 동일하다.
* exact tool/test/durable attempt evidence의 ignored/untracked count가 0이다.

### Change 4 — Candidate-First Transaction and Recovery

Purpose:

* live target을 쓰기 전에 완전한 candidate와 rollback material을 만든다.

Implementation Notes:

* candidate build는 attempt-local path에만 쓴다.
* owner authorization 전 live write count는 0이다.
* round-global transaction lock은 attempt ID, target path set, current preimage hashes,
  candidate hashes, one-use nonce를 결속한다.
* 새 prepare/apply 전에 모든 prior non-committed journal을 검사한다. Snapshot과
  preimage가 결속된 recoverable state는 lock 아래 복구하고, 복구 불가능하거나
  ambiguous한 state가 하나라도 있으면 새 attempt를 시작하지 않는다.
* lock 획득 뒤 target preimage를 다시 hash한다.
* 두 target의 rollback snapshots를 attempt-local transaction directory에
  exclusive-create하고 hash manifest를 쓴다.
* 각 target은 같은 directory의 temporary file을 flush/fsync한 뒤 `os.replace`한다.
* facts를 먼저, manifest를 마지막에 교체한다. 이 순서는 canonical atomic-visibility
  claim이 아니라 fail-closed recovery order다.
* journal state는
  `prepared → facts_replaced → manifest_replaced → verified → committed`만 허용한다.
* 두 번째 replace 또는 post-write verification이 실패하면 under-lock snapshot으로
  두 target을 복원하고 exact preimage hash를 확인한다.
* 복원 확인 전 lock을 해제하거나 PASS receipt를 쓰지 않는다.
* journal transition별 process-crash fixture는 다음 startup recovery가 두
  preimage를 복원하거나 이미 verified된 두 candidate를 단일 committed state로
  닫는지 검증한다.
* temp-file fsync와 지원되는 플랫폼의 parent-directory fsync 결과를 기록한다.
  Windows에서 directory fsync가 지원되지 않으면 이를 숨기지 않고
  `power_loss_atomicity_claimed=false`로 기록한다.
* transaction tool은 `.git` 조작, commit, reset, checkout을 수행하지 않는다.

Validation:

* missing/forged/replayed/wrong-path/wrong-preimage authorization fixture가
  zero-live-write로 실패한다.
* injected second-replace failure fixture가 두 preimage를 복원한다.
* partial/dual-current terminal state를 PASS로 기록할 수 없다.
* uncoordinated reader에 대한 intermediate visibility zero 또는 power-loss
  atomicity를 PASS로 기록할 수 없다.

### Change 5 — Exact Owner Authorization

Purpose:

* current authority 변경을 구현·review 승인과 분리한다.

Required owner authorization fields:

```text
verdict = PASS
plan_sha256
plan_git_blob_id
implementation_commit
implementation_tree
cutover_attempt_id
pre_cutover_review_sha256
selected_successor_binding_sha256
successor_facts_sha256
successor_manifest_sha256
candidate_current_facts_sha256
candidate_current_manifest_sha256
current_facts_preimage_sha256
current_manifest_preimage_sha256
allowed_target_paths
authorization_nonce
approver_identity
approval_time
```

* authorization은 owner가 exact candidate/review를 확인한 뒤 한 번만 발행한다.
* nonce consumption record가 만들어진 뒤 동일 authorization 재시도는 금지한다.
* shell/path invocation이 claim byte나 nonce consumption을 만들기 전에 실패한 경우는
  같은 attempt에서 호출을 바로잡을 수 있다.
* actual transaction failure나 nonce 소비 뒤 재시도는 새 attempt가 필요하다.

### Change 6 — Adoption Receipt and v2 Naturalization Contract

Purpose:

* successor identity와 current adoption projection을 혼합하지 않고 결속한다.

Adoption receipt required predicates:

```text
status = PASS
food_semantic_registry_adoption = current_adoption_complete
selected_successor_facts_sha256 = current_facts_sha256
selected_successor_manifest_sha256 = predecessor_successor_manifest_sha256
current_manifest_sha256 = projected_current_manifest_sha256
current_manifest_adopted_successor_manifest_sha256 =
  selected_successor_manifest_sha256
manifest_allowlisted_delta_violation_count = 0
current_identity_ambiguity_count = 0
partial_or_dual_current_count = 0
rendered_lua_runtime_package_mutation_count = 0
official_naturalization_retry_allowed = true
```

Naturalization v2 official-consumer predicate:

```text
current_facts_sha256 = selected_successor_facts_sha256
current_manifest.food_semantic_authority.source_successor_manifest_sha256 =
  selected_successor_manifest_sha256
current_manifest_sha256 = registry_adoption_receipt.current_manifest_sha256
current_manifest_projection_validation = PASS
schema_sha256 = selected_schema_sha256
proposition_license_sha256 = selected_proposition_license_sha256
```

기존 v1의 raw manifest byte-equality predicate는
`superseded_for_current_adoption_projection`으로 보존하며 삭제하지 않는다.
non-current compatibility probe 계약은 그대로 유지한다.

### Change 6A — Registry Runtime Compatibility Staleness Disposition

Purpose:

* `Base.LemonGrass` / `Base.Lemongrass`의 predecessor RTC owner disposition이
  요구한 source payload equivalence가 successor food-semantic assertions에서는
  더 이상 참이 아님을 숨기지 않는다.

Implementation Notes:

* pre-cutover collision-impact report는 두 exact key와 comparison group을
  보존하면서 predecessor/source payload-equivalence가 stale임을 기록한다.
* `current_route_required_validations.json`의 기존 RTC durable bundle identity와
  historical PASS는 변경하지 않되, `registry_runtime_compatibility` 아래에
  additive `current_source_alignment`을 추가한다.
* `current_source_alignment.state`는 `stale_requires_successor_rtc`이고
  `applies_when_current_facts_sha256`은 exact successor facts SHA-256이다. 따라서
  marker가 implementation commit에 먼저 들어가도 predecessor current facts에는
  적용되지 않고, facts 교체 직후부터 fail-closed로 활성화된다.
* bridge exporter, RTC live validator, package script는 current facts working-byte
  SHA가 `applies_when_current_facts_sha256`와 같을 때 live/default/canonical-durable
  경로를 `registry_runtime_compatibility_current_source_stale`로 거부한다.
  새 successor RTC closure가 사용하는 isolated candidate probe만 허용한다.
* adoption 뒤 bridge export, runtime/package mutation, publication은 successor RTC
  closure 전까지 허용하지 않는다.
* 이 staleness 표식은 RTC successor closure, collision owner disposition 변경,
  key rename/merge 또는 suite PASS를 주장하지 않는다.
* Naturalization Phase 0/2 current-source inventory는 runtime/package consumer가
  아니므로 exact current facts/manifest projection 검증 뒤 열 수 있다.

Validation:

* case-variant exact member count는 2, comparison collision group count는 1이다.
* successor source payload equivalence는 false이고 이 결과가 staleness marker와
  byte-identical하게 결속된다.
* bridge/package/current-validator focused negative regression은 actual successor
  current facts에서 write-before-failure count 0으로 거부한다.
* `registry_runtime_compatibility_current_source_alignment =
  stale_requires_successor_rtc` non-claim이 adoption receipt, final validation,
  terminal seal에 유지된다.

### Change 7 — Scoped Final Validation and Closeout

Purpose:

* 변경된 current authority와 직접 consumer handoff만 검증한다.

Sequence:

```text
implementation complete
→ Codex Reviewer pre-cutover review PASS
→ exact owner cutover authorization
→ one-use transaction
→ adoption receipt
→ adoption commit (targets/config/contracts/receipt)
→ committed Git blob/working-file identity verification
→ final scoped validation
→ distinct Codex Reviewer closeout review PASS
→ owner final seal
→ terminal hash seal
→ evidence-only closeout commit
```

Terminal seal 뒤 claim-bearing file 변경은 금지한다.
Evidence-only closeout commit은 이미 생성된 claim-bearing bytes를 그대로 기록하며
그 내용을 재작성하지 않는다.

---

## 7. Validation Plan

모든 테스트는 구현과 tracked contract/config 변경, current transaction이 끝난 뒤
마지막에 몰아서 실행한다.

### Automated Validation

다음 세 그룹만 실행한다.

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_food_semantic_registry_cutover.py"
```

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_food_semantic_*.py"
```

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_korean_prose_acceptance_gate.py"
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_korean_prose_semantic_preservation.py"
```

RTC successor closure/suite 전체를 열지 않고, 새 current-source staleness marker를
직접 소비하는 세 guard regression만 실행한다.

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_runtime_compatibility_bridge.py"
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_runtime_compatibility_package.py"
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_runtime_compatibility_current.py"
```

두 번째 pattern이 첫 번째 cutover test를 포함하므로 receipt에는 중복 실행 여부와
각 command의 실제 test count를 기록한다. 동일 test를 두 번 실행하지 않도록 최종
runner는 food-semantic pattern 1회와 D16 두 file 1회씩만 실행하는 것을 기본으로
하며, 위 RTC guard file 세 개를 각각 1회 실행한다.

### Artifact Validation

* adoption receipt/owner authorization/transaction journal/terminal seal JSON parse
* exact path·byte count·SHA-256 재계산
* current facts 2105 rows
* food target 317/317과 proposition 718 identity
* current manifest projection allowlist
* current facts Git blob/working-file identity
* current manifest Git blob/working-file identity
* G2 artifacts mutation count 0
* rendered/Lua/runtime/package mutation count 0
* RTC collision impact와 live additive staleness marker identity
* implementation/preauthorization commit, adoption commit/tree, evidence-only
  closeout commit의 역할 분리

### Validation Limits

실행하지 않는다.

* full-repository gate
* direct all-`test_*.py` discovery
* historical/obsolete/misrouted test
* Registry Runtime Compatibility suite 및 successor RTC closure
* package/release/Workshop suite
* Naturalization Phase 3~8
* Publish Boundary suite
* runtime Lua syntax/package validation
* manual in-game or multiplayer validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched. Current facts와 input manifest를 Registry가 채택한다.

### Runtime Behavior Surface

Not touched. Rendered/Lua/runtime/package는 변경하지 않는다.

### Compatibility Surface

Touched at the Naturalization Phase 2 source-consumer contract and at an additive
Registry Runtime Compatibility current-source staleness marker. RTC successor
closure itself is not performed.

### Sealed Artifact Surface

Touched additively. G2 seal은 불변이며 G3 adoption receipt가 별도 생성된다.

### Public-Facing Output Surface

Not touched in this plan. Public text 변경은 fresh Naturalization/Publish 단계가
소유한다.

---

## 9. Risk Analysis

### Authority Risk

* non-current manifest를 current로 거짓 승격할 위험
* process crash 뒤 partial two-file cutover 또는 dual current
* stale current preimage 위에 successor를 적용할 위험
* owner authorization replay

Mitigation:

* closed projection allowlist
* lock 아래 preimage revalidation
* one-use nonce와 journal
* rollback snapshots와 mandatory startup recovery
* manifest-last order와 canonical readpoint의 post-adoption-commit 지연
* owner authorization과 reviewer gate 분리

### Reproducibility Risk

* Git CRLF conversion으로 SHA가 checkout마다 달라질 수 있다.

Mitigation:

* exact 두 current authority path의 `-text` 고정
* Git blob/working-file dual identity receipt

### Downstream Risk

* Naturalization v1 manifest equality를 그대로 사용하면 current metadata 모순을
  숨길 수 있다.

Mitigation:

* v2 adoption projection contract
* v1 predicate의 explicit supersession record
* fresh Naturalization attempt만 허용

### Runtime Compatibility Staleness Risk

* successor facts는 case-variant collision group의 source payload-equivalence를
  변경한다.

Mitigation:

* exact collision impact report
* prior RTC durable bundle의 historical PASS 보존
* live current-source alignment를 `stale_requires_successor_rtc`로 fail-closed 표식
* successor RTC closure 전 bridge/runtime/package/publication 금지

---

## 10. Rollback Plan

Cutover transaction 안에서 실패하면 under-lock snapshot으로 두 target을 모두
preimage bytes로 복원하고 hash equality를 확인한다. 복원 성공도 adoption PASS가
아니며 failed transaction record를 보존한다.

Git commit 전의 successful filesystem transaction은 아직 canonical adoption이
아니다. Exact current files, `.gitattributes`, `.gitignore`, contracts, RTC
staleness marker와 receipt가 adoption commit에 포함되고 committed blob/working
identity가 확인된 뒤에만 adoption readpoint로 사용할 수 있다.

Commit 뒤 발견된 의미·권위 결함은 predecessor restore로 해결하지 않는다.
새 successor와 새 Registry correction attempt를 사용한다. Partial restore,
silent reset, failure evidence 삭제는 금지한다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`의 근거·책임·fail-loud 원칙을 따른다.
* G2 `attempt-0022`는 byte-preserved한다.
* semantic proposition을 추가·삭제·변경하지 않는다.
* Layer 4 자동 승격은 0이다.
* detector, threshold, waiver를 수정하지 않는다.
* current write는 exact owner authorization 뒤 한 번만 허용한다.
* Codex Reviewer는 owner authorization 또는 owner seal을 대신하지 않는다.
* 사소한 shell/path 오류는 claim byte가 없으면 새 attempt 사유가 아니다.
* nonce 소비 또는 transaction failure 뒤에는 같은 attempt를 재사용하지 않는다.
* 계획 밖 테스트를 실행하지 않는다.
* 새 tool/test/durable attempt evidence는 exact `.gitignore` exception과 VCS
  tracking report 없이 terminal evidence로 사용할 수 없다.
* power-loss atomicity 또는 intermediate reader visibility zero를 주장하지 않는다.

---

## 12. Expected Closeout State

이 계획의 complete 조건:

```text
food_semantic_registry_adoption = current_adoption_complete
current_facts_sha256 = selected_successor_facts_sha256
current_manifest_projection_validation = PASS
current_manifest_adopted_successor_manifest_sha256 =
  selected_successor_manifest_sha256
current_identity_ambiguity_count = 0
partial_or_dual_current_count = 0
G2_mutation_count = 0
rendered_lua_runtime_package_mutation_count = 0
scoped_final_validation = PASS
independent_closeout_review = PASS
owner_final_seal = PASS
terminal_hash_seal = PASS
official_naturalization_retry_allowed = true
registry_runtime_compatibility_current_source_alignment =
  stale_requires_successor_rtc
```

허용 terminal claim:

```text
DVF 3-3 Food Semantic Registry Adoption
= current_adoption_complete
```

필수 non-claims:

```text
Naturalization Phase 3-8 complete = false
Publish Boundary PASS = false
runtime/package compatibility = not evaluated
successor Registry Runtime Compatibility closure = false
public repetition issue removed = not yet claimed
```

다음 정규 단계는 fresh Naturalization attempt Phase 0과 Phase 2 source inventory
reseal이다. 이 계획은 그 retry를 허용하는 current authority handoff까지만 종결한다.
