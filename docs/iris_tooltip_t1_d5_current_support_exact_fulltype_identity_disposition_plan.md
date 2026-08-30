# Iris Tooltip T1-D5 Current Support Exact FullType Identity Disposition Implementation Plan

> 대상: Tooltip T1-C upstream correction closure 중 `Iris presentation-contract owner` 귀속 `SUPPORT_NORMALIZED_COLLISION` 2건
> exact subjects: `Base.LemonGrass`, `Base.Lemongrass`
> predecessor: commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
> 계획 작성 기준일: 2026-08-29
> 상태: planned / synchronized for parallel execution
> 병렬 실행 계약: `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`

계획 작성 시점의 current Iris 구현을 읽어 확인한 사실은 다음과 같다. 이 표는 owner disposition을 대신하지 않으며, 실행 시 clean exact subject에서 다시 생성해야 하는 planning-time census다.

| 관찰 지점 | `Base.LemonGrass` | `Base.Lemongrass` | 계획상 의미 |
|---|---:|---:|---|
| `Iris/input/items_itemscript.json` | present | present | 둘 다 exact source row이며 속성도 동일하지 않다. DisplayName만으로 같은 identity라고 판정할 수 없다. |
| `IrisClassifications.lua` | `Consumable.3-A`, `Consumable.3-E` | `Consumable.3-E` | Layer 2는 두 exact key를 서로 다른 membership으로 보존한다. |
| pointer-selected Layer 3 rendered data | present | present | 두 exact key가 current generation에 각각 존재한다. |
| `tooltip_t1_layer3_owner_input.json` | present | present | 서로 다른 `fact_id`와 exact `source_ref`를 가진다. |
| `upstream_usecases_by_fulltype.json` | present | absent | Layer 4 owner membership은 두 key 사이에서 다르다. |
| current T1 support union | present | present | Layer 2 + Layer 3 + Layer 4의 case-sensitive union이므로 둘 다 denominator에 남는다. |
| normalized diagnostic class `base.lemongrass` | member | member | 계획 시점에는 두 row뿐이지만 authoritative identity나 disposition denominator로 사용하지 않는다. |

Planning checkout `1f901df719c2684d351b86e45efe448be6eaf4bf`는 predecessor의 descendant가 아니지만, predecessor와 current `tooltip_t1` code/tests/authority 및 `Iris/build/ENTRYPOINTS.md`의 diff는 비어 있다. 이는 planning-time equivalence observation일 뿐이다. 실제 D5 실행은 clean integration subject에서 predecessor inclusion을 ancestry 또는 exact path/blob equivalence manifest로 다시 증명해야 한다.

---

## 0. Parallel execution synchronization amendment

T1-D5는 공통 병렬 실행 계약을 따르며 T1-D1, T1-D3, T1-D4와 동일 predecessor에서 별도 clean worktree로 동시에 실행한다. D5의 output은 immutable disposition/correction bundle과 D6 integration manifest다.

후속 절의 workstream별 canonical full-gate Run A/B, Tooltip T1 finalizer와 governance docs 직접 채택 요구는 폐기된다. D5는 existing focused parameterized families, candidate Run A/B bytes, reconciliation과 bundle integrity만 검증한다. Integrated canonical Run A/B/comparator/finalizer와 global current adoption은 T1-D6가 한 번 수행한다.

테스트 예산은 새 파일 `0`, 새 top-level function/family `0`이다. Existing Tooltip T1 audit family의 mandatory three cases와 contract family의 composite negative rows만 추가한다. 기존 family로 필수 code path를 실행할 수 없을 때만 기존 파일 안 parameterized function 최대 1개 예외를 허용한다.

---

## 1. Objective

`Base.LemonGrass`와 `Base.Lemongrass`에 대해 current source authority와 current support entry path를 exact case-sensitive identity로 동결하고, `Iris presentation-contract owner`가 다음을 issuance-bound, content-applicable machine-readable disposition으로 확정하게 한다.

1. 두 FullType의 current identity relation
2. 각 exact FullType의 Tooltip current support disposition
3. 둘 다 support에 남는 경우 `SUPPORT_NORMALIZED_COLLISION` raw observation과 target correction row(및 그에 따른 T2-blocking correction)를 분리하는 terminal mechanism
4. disposition을 다시 심사해야 하는 기계 평가 가능한 조건

승인된 disposition은 normalized key를 authoritative key로 승격하지 않은 채 isolated Tooltip T1 successor candidate에 적용한다. Support derivation, support census, readiness row와 candidate projection에서 exact spelling과 cardinality를 보존하고, raw collision observation과 blocking correction lifecycle을 별도 산출물로 기록한다.

D5의 성공 결과는 T1-D6가 소비할 수 있는 immutable correction bundle이다. D5만으로 전체 upstream correction closure, `T2_FULL_DATA_PROGRESSION = OPEN`, production T2 handoff, runtime Tooltip 변경 또는 release readiness를 주장하지 않는다.

---

## 2. Scope

다음 작업을 포함한다.

- predecessor inclusion/equivalence와 clean exact execution subject 결속
- declared exact target 두 row 및 normalized diagnostic class 전체의 read-only discovery census
- source item, Layer 2, pointer-selected Layer 3, Layer 3 Tooltip owner input, Layer 4 owner input, current T1 support union과 existing correction의 exact entry-path matrix
- normalization 사용 지점과 authoritative keying 위험의 static inventory
- current T1 support derivation부터 readiness/correction/candidate artifacts까지 stage별 exact-key set과 role 검증
- D5 owner disposition schema와 tracked authority record
- disposition issuance provenance, content applicability, evidence, owner approval, cross-record relation과 re-audit predicate 검증
- owner-approved disposition의 current support predicate 및 collision correction lifecycle 적용
- raw collision detector를 보존하면서 owner가 선택한 Branch A terminal mechanism의 exact semantics 적용
- existing Tooltip T1 parameterized test family의 mandatory three-case extension
- affected-range와 whole-universe before/after comparison
- same-input D5 Run A/Run B canonical byte determinism
- D5 candidate Run A/B byte determinism과 immutable bundle validation; integrated canonical gate는 D6 소유
- repository-external immutable D5 bundle, artifact SHA-256와 D6 integration manifest 생성
- D5-bounded contract/shared-path proposal; global current/governance adoption은 D6 input으로 이관

### Explicitly Out Of Scope

- 일반적인 case-collision/alias/canonical-name framework 구축
- support predicate를 normalized identity나 case-insensitive set으로 변경
- declared pair 외 다른 FullType의 semantic support 재심사
- DisplayName, item name, locale prose 또는 spelling appearance를 이용한 semantic identity 추론
- Layer 2 classification, Layer 3 fact 또는 Layer 4 interaction semantic correction 자체
- upstream owner authority를 presentation owner denylist로 우회
- Tooltip KO/EN 문장 작성 또는 수정
- Menu parity correction 또는 독립 consumer evidence 생성
- `IrisAltTooltip.lua`, Alt 입력, 4-line assembly와 runtime rendering 변경
- PZ runtime FullType resolution semantics의 일반 certification
- package/install/runtime payload 변경
- `T2_FULL_DATA_PROGRESSION = OPEN` 전환
- production T2 handoff 생성
- T1-C predecessor closeout 또는 기존 external evidence root 수정
- 전체 T1 formal closeout의 역사 재작성
- 다른 D1/D3/D4/D6 owner correction의 구현
- `Iris/_docs/authority/iris_current_authority_manifest.json`, `iris_current_route_index.json`, current environment locator 또는 cross-D-stage global current-authority integration 갱신
- release, Workshop, deployment 또는 full external-mod compatibility 판정

---

## 3. Non-Goals

- `Base.LemonGrass`와 `Base.Lemongrass` 중 보기 좋은 spelling을 도구가 canonical spelling으로 고르는 것이 아니다.
- payload나 DisplayName이 같거나 비슷하다는 이유로 exact identity를 합치는 것이 아니다.
- correction count를 predecessor의 숫자에 맞추기 위해 다른 owner row를 더하거나 빼는 것이 아니다.
- raw collision observation 자체를 없애는 것이 아니다.
- `SUPPORT_NORMALIZED_COLLISION` reason code를 삭제하거나 target-specific skip-list를 추가하는 것이 아니다.
- owner disposition을 code constant, allowlist 또는 audit expectation으로 대체하는 것이 아니다.
- repository-external D5 evidence를 current runtime/package authority로 승격하는 것이 아니다.
- existing six-family Tooltip T1 lifecycle validation을 새 standalone validation system으로 복제하는 것이 아니다.
- D5 focused success를 whole-T1, runtime, package 또는 product readiness success로 확대하는 것이 아니다.

---

## 4. Assumptions

### Repository and authority assumptions

- `docs/Philosophy.md`가 최상위 설계 권위이며 Iris는 근거 기반 정보만 표시하고 runtime에서 item/game state를 변경하지 않는다.
- `docs/DECISIONS.md`의 current Tooltip T1 boundary와 `Iris/_docs/authority/tooltip_t1/**`가 D5의 직접 machine authority다.
- Current support predicate는 `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json`의 `current-owner-fulltype-union-v1`이며 case-sensitive Layer 2 + pointer-selected Layer 3 + current Layer 4 owner FullType union이다.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py::run_candidate`가 current support census, readiness manifest, correction ledger와 progression의 package-owned producer다.
- `Iris/build/ENTRYPOINTS.md`가 human command literal owner이고 `Iris/_docs/authority/iris_current_route_index.json`가 machine navigation projection이다.
- Repository-external census, audit, correction bundle과 receipts는 lifecycle evidence이며 regular validation authority가 아니다.
- Planning checkout의 unrelated modified/untracked D1/D3/D4 plan 문서는 D5 실행이 수정·정리·채택하지 않는다.

### Exact target assumptions

- Owner disposition 전 `Base.LemonGrass`와 `Base.Lemongrass`는 서로 다른 exact Unicode/code-point identity다.
- Planning-time current support count는 `2,280`이고 normalized class `base.lemongrass`의 support member는 정확히 두 row다. 이 수치는 실행 subject에서 재측정하며 고정 expectation으로 사용하지 않는다.
- Planning-time membership은 두 target 모두 Layer 2와 Layer 3에 present이고, Layer 4에는 `Base.LemonGrass`만 present다.
- `items_itemscript.json`의 두 row는 속성이 다르므로 DisplayName equality나 historical payload equivalence는 current semantic identity 판정 근거가 될 수 없다.
- Historical RTC bundle의 `reference`/`exception` role은 `role_resolution_power: none`이므로 D5 presentation support disposition을 대신하지 않는다. 필요한 경우 provenance/evidence로만 참조한다.

### Roadmap conflict dispositions

| 로드맵 보류 항목 | 이 계획의 disposition | 근거 |
|---|---|---|
| Phase 1 census breadth | normalized class 전체를 **discovery census**로 열거하되 official disposition denominator는 declared exact pair다. Discovery 결과가 pair와 정확히 일치할 때만 cardinality 2를 확정한다. 제3 variant가 나오면 자동 편입하지 않고 scope ratification 전까지 `blocked`다. | 제3 variant silent omission은 막되 D5의 declared two-subject authority를 normalization으로 확대하지 않는다. |
| Branch A terminal mechanism | **Option A, correction-row closure를 governing D5 completion contract로 채택한다.** 모든 성공 mechanism에서 raw two-member observation과 두 exact support identity는 유지하되 `SUPPORT_NORMALIZED_COLLISION` correction-row target set과 T2-blocking target set은 모두 empty여야 한다. Owner는 implementation mutation 전에 predicate refinement 또는 이 동일 terminal invariant를 만족하는 selectable current mechanism을 승인한다. `blocking_axis_transition`은 D5 complete path에서 제외한다. | D5 problem은 owner 귀속 correction 2건의 closure다. Raw observation은 별도 artifact로 보존할 수 있지만, 별도 상위 authority가 resolved correction-row persistence를 승인하지 않은 상태에서 current progression의 non-blocking filter만으로 D5 closure까지 확장하지 않는다. 더 엄격한 fail-closed 해석을 사용한다. |
| Runtime evidence 필요성 | D5의 기본 필수 evidence로 두지 않는다. Current offline source/owner rows로 owner adjudication packet을 구성한다. Owner가 runtime resolution evidence 없이는 결정할 수 없다고 명시하면 추측하지 않고 `blocked`다. | T1은 offline contract/audit owner이며 runtime interpretation은 current claim boundary 밖이다. |
| Disposition tracked path | `Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.schema.json`과 `...disposition.json`을 사용한다. | Presentation-contract owner authority와 current T1 contract bundle 아래에 둔다. |
| Fixture upper bound | 기존 `test_tooltip_t1_audit.py` parameterized family에 로드맵의 세 case를 정확히 mandatory set으로 추가한다. 새 defect가 실제로 발견되지 않는 한 추가 D5 fixture/test file을 만들지 않는다. | 새 independent validation family를 만들지 않는다는 공통 제약을 지킨다. |
| Closeout vocabulary | D5 lifecycle terminal은 `complete` 또는 `blocked`만 사용한다. 단, existing Tooltip T1 candidate는 canonical gate 전까지 기존 `partial/implemented_only` ceiling을 그대로 사용한다. | D5 disposition과 existing T1 formal-closeout vocabulary를 섞지 않는다. |
| Global current-authority adoption | D5는 direct owner disposition record, D5 application evidence와 D6 integration manifest까지만 만든다. Global authority manifest/index/environment locator 갱신은 D6가 소유한다. | 상위 로드맵의 `global current authority locator update` non-goal과 D5→D6 handoff 경계를 보존한다. |
| P-1~P-12 contract hash rebind | 자동 승계를 가정하지 않는다. D5 owner ratification에 before/after bundle hash, prior decision-contract identity와 P-1~P-12 non-hash invariant digest를 포함한다. | Sealed decision anchor 변경을 명시적으로 승인하고 predecessor hash를 historical trace로 보존한다. |
| Independent review | Independent review는 D5 completion gate로 새로 추가하지 않는다. Existing owner approval, focused candidate validation과 bundle validator를 사용하고 integrated canonical gate는 D6가 소유한다. | Independent-review satisfaction 자체는 D5 positive claim이 아니다. |

### Owner adjudication assumptions

- Tooling은 evidence packet, schema와 consistency를 검증하지만 `identity_relation`이나 `support_disposition` 값을 생성하지 않는다.
- Owner는 각 exact target마다 승인 record를 발행하고 두 record의 relation이 상호 모순되지 않게 한다.
- Owner는 Branch A를 선택할 경우 correction terminal mechanism도 implementation mutation 전에 별도 승인한다. Schema와 tooling에는 default mechanism이 없다.
- Branch A의 owner 선택권은 fixed correction-row closure를 달성하는 implementation mechanism 선택권이다. Owner가 D5 완료 골대를 임의로 완화하거나 non-blocking correction-row persistence를 승인하는 권한이 아니며, 어떤 successful mechanism이든 raw pair observation 유지, exact support identity 보존, correction-row target set `empty`와 T2-blocking target set `empty`를 모두 만족해야 한다.
- Branch A는 두 target을 support에 유지한다.
- Branch B는 presentation-only exclusion overlay를 만들지 않는다. Excluded target이 Layer 2 또는 Layer 3 current union member로 남아 있으면 relevant upstream owner correction 전까지 D5는 blocked다.
- Branch C는 evidence insufficiency를 기록하고 기존 support/correction state를 유지한 채 blocked로 종료한다.
- `subject_commit`/`subject_tree`는 disposition 발행 provenance다. 발행 라운드 self-consistency에는 사용하지만 후속 subject 적용 가능성을 commit equality로 판정하지 않는다.
- 후속 subject applicability는 **declared exact target-scoped** input path/content hash, support predicate와 comparison/schema version으로 계산한 versioned `applicability_fingerprint`, 그리고 exact collision-class member-set guard를 포함한 structured `re_audit_condition`으로 판정한다.

### Execution assumptions

- D5 mutation과 final validation은 dedicated clean subject에서 수행한다.
- Issuance subject는 disposition record를 아직 포함하지 않은 clean census/owner-decision evidence subject다. Tracked disposition은 그 issuance provenance를 가리키는 application successor에 추가되므로 자기 자신의 commit hash를 포함하려는 순환 binding을 만들지 않는다.
- Application successor와 그 뒤 D6 subject는 issuance commit/tree equality가 아니라 approved declared-target-scoped content applicability fingerprint로 disposition을 소비한다.
- Predecessor가 ancestor가 아니면 exact T1 code/tests/contracts/command owner 및 D5가 읽는 current input의 path/blob equivalence manifest를 먼저 생성한다.
- Output root는 repository-external empty directory다.
- Current source/runtime input은 read-only이며 audit 실행 전후 SHA-256이 같아야 한다.
- Missing required tooling, non-clean issuance subject, issuance self-inconsistency, content-stale disposition 또는 external-root 위반은 fail-closed `blocked`다.

---

## 5. Repository Areas Affected

### Code

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d5.py` (new) — D5 discovery census, disposition validation/application support, stage-set reporting, before/after reconciliation과 bundle assembly
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py` — existing `tooltip-t1` target 아래 lifecycle-bound `d5-census`/`d5-reconcile` route 추가; normal build/finalize route 보존
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py` — D5 schema/record를 contract bundle에 포함하고 issuance/applicability/evidence/approval/re-audit/cross-record consistency 검증
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py` — validated disposition load, unconditional raw collision observation, approved correction-row-eliminating reconciliation, D5 stage-set/closure provenance output
- `Iris/tooling/tests/test_tooltip_t1_contract.py` — D5 authority schema, issuance/applicability separation, content-stale/conflicting disposition와 contract rebind validation
- `Iris/tooling/tests/test_tooltip_t1_audit.py` — existing parameterized family에 mandatory positive/negative three-case 추가 및 progression regression
- `Iris/tooling/tests/test_tooltip_t1_projection.py` — planned edit 없음; exact-key/candidate selection regression 대상으로 재실행
- `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json` — D5 expectation을 self-seeding하지 않는 최소 tracked fixture binding이 필요할 때만 additive update

### Docs

- `docs/iris_tooltip_t1_d5_current_support_exact_fulltype_identity_disposition_plan.md`
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` — read-only D6 integration inputs; D5 successor proposal은 bundle에 기록
- `docs/iris_tooltip_t1_display_contract_policy.md` — current support collision disposition consumption rule
- `Iris/build/ENTRYPOINTS.md` — read-only command-owner input

### Config

- `Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.schema.json` (new)
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.json` (new; owner-approved exact target records)
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json` — expanded contract bundle SHA-256를 P-1~P-12에 canonical rebind; support predicate 의미는 유지
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json` — reason code와 `t2_blocking: true`를 유지하고 acceptance를 valid D5 disposition 또는 corrected upstream authority에 결속
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json` — D5 lifecycle output과 non-regular-validation boundary 명시

`Iris/_docs/authority/iris_current_authority_manifest.json`, `Iris/_docs/authority/iris_current_route_index.json`와 current environment locator는 planned D5 write set이 아니다. Pre-existing `tooltip_t1/**` authority classification을 D5가 확장 해석하지 않으며, cross-D-stage/global integration은 D6가 D5 bundle을 검증한 뒤 별도 수행한다.

### Generated Artifacts

모든 artifact는 repository-external immutable result root에 생성하며 predecessor root나 mutable `latest` pointer를 수정하지 않는다.

- `subject_binding.json`
- `predecessor_equivalence_manifest.json`
- `d5_discovery_normalized_class.json`
- `d5_target_freeze.json`
- `d5_source_authority_census.json`
- `d5_support_entry_path_matrix.json`
- `d5_pre_mutation_support_set.json`
- `d5_pre_mutation_correction_ledger.json`
- `d5_normalization_usage_report.json`
- `d5_keying_path_inventory.json`
- `d5_stage_exact_key_sets_before.json`
- `d5_owner_disposition_validation_report.json`
- `d5_disposition_applicability_report.json`
- `d5_contract_bundle_rebind_receipt.json`
- `d5_post_disposition_support_set.json`
- `d5_raw_collision_observation.json`
- `d5_correction_reconciliation.json`
- `d5_closure_provenance.json`
- `d5_stage_exact_key_sets_after.json`
- `d5_exact_identity_preservation_report.json`
- `d5_affected_range_audit.json`
- `d5_whole_universe_impact_report.json`
- `d5_before_after_correction_ledger.json`
- `d5_determinism_report.json`
- `d5_validation_denominator_before_after.json`
- `d5_validation_ceiling.json`
- `d5_reconciliation_receipt.json`
- `integration_manifest.json`
- `artifact_digests.json`
- `run_receipt.json`
- existing Tooltip T1 candidate artifacts including `tooltip_support_universe_census.jsonl`, `tooltip_support_universe_summary.json`, `tooltip_readiness_manifest.jsonl`, `upstream_correction_ledger.jsonl`, `t2_progression_record.json` and `axis_separated_closeout_record.json`

No generated artifact is added under `Iris/media/lua/**`, package output, current generation pointer or predecessor external closeout root.

---

## 6. Planned Changes

### Change 1 — Bind the exact subject and freeze discovery/target/baseline sets

Purpose:

Mutation 전에 execution subject, predecessor relation, target denominator와 current support/correction baseline을 exact bytes로 고정한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d5.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py`
- `Iris/build/ENTRYPOINTS.md` (read-only command-owner input)
- repository-external census artifacts

Implementation Notes:

- `d5-census`는 clean checkout과 repository-external empty output root를 강제한다.
- `git_subject()`의 commit/tree/clean state에 더해 predecessor ancestry를 기록한다.
- Ancestry가 없으면 다음을 포함한 exact equivalence manifest를 만든다.
  - `Iris/tooling/src/iris_tooling/domains/tooltip_t1/**`
  - existing three Tooltip T1 test files와 fixture
  - `Iris/_docs/authority/tooltip_t1/**`
  - `Iris/build/ENTRYPOINTS.md`
  - current support input/readpoint paths used by `_source_hashes()`
- Declared target은 exact ordered set `Base.LemonGrass`, `Base.Lemongrass`로 보존한다.
- Discovery census는 `items_itemscript.json`, Layer 2, pointer-selected Layer 3, Layer 3 owner input, Layer 4 owner input과 support union에서 `ascii-lower/base lower == base.lemongrass`인 모든 exact value를 one-to-many relation으로 방출한다.
- Discovery set이 declared pair와 다르면 target을 자동 확대/축소하지 않고 scope mismatch로 중단한다.
- 각 target에 다음을 기록한다.
  - exact source row presence와 canonical row hash
  - Layer 2/3/4 membership 및 exact authority ref
  - current support membership과 union entry paths
  - Layer 3 owner `fact_id`/source ref presence
  - current collision observation과 correction row
  - normalized diagnostic key
- Count만 저장하지 않고 sorted exact set과 set digest를 함께 저장한다.
- Census command는 tracked source/support/correction을 변경하지 않는다.

Validation:

- wrong/dirty subject가 nonzero로 실패한다.
- predecessor ancestry 또는 declared path/blob equivalence 중 하나가 성립한다.
- discovery exact set과 declared target exact set이 동일하다.
- duplicate exact target, missing target, unexpected third variant와 case-insensitive materialization이 fail-loud하다.
- census 전후 `_source_hashes()`가 동일하다.

---

### Change 2 — Add the issuance-bound, content-applicable presentation owner disposition authority

Purpose:

Tool-generated inference가 아닌 owner-approved identity/support decision을 D5-owned tracked authority proposal로 표현하고 후속 subject 및 D6에서 재심사 가능하게 한다.

Files:

- `Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.schema.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`

Implementation Notes:

- Root record는 schema version, issuance subject, predecessor binding, target-set hash, source-census hash, owner/approval identity, decision status와 owner-selected collision terminal mechanism을 포함한다.
- Per-target record는 최소 다음을 포함한다.
  - `exact_full_type`
  - `source_authority_refs`와 bound SHA-256
  - `identity_relation`
  - `support_disposition`
  - `owner`
  - `approval_ref`
  - `evidence_refs`
  - `acceptance_condition`
  - `applicability_binding`
  - structured `re_audit_condition`
- `identity_relation`은 두 record가 같은 relation/group을 상호 참조해야 하며 contradictory pair를 허용하지 않는다.
- `support_disposition`은 owner vocabulary만 허용한다. 최소 branch는 다음과 같다.
  - `retain_current_support_identity`
  - `exclude_after_upstream_authority_withdrawal`
  - `blocked_insufficient_evidence`
- Branch A terminal mechanism은 schema가 선결정하지 않는다. Owner는 implementation 전에 다음 중 하나를 exact decision record에 선택한다.
  - `unresolved_disposition_predicate_refinement_v1`
  - `owner_approved_existing_mechanism_v1`; 이 값은 자유 형식 escape hatch가 아니며 current authority의 exact `mechanism_contract_ref`, expected raw-observation set `declared pair`, expected correction-row set `empty`, expected T2-blocking set `empty`와 approval hash가 모두 있어야 한다.
- `resolved_observation_blocking_axis_transition_v1`은 D5 successful mechanism enum에서 제거한다. 이 값이나 correction-row persistence를 요구하는 equivalent mechanism이 들어오면 complete-path authority로 소비하지 않고 `blocked`다.
- `owner_approved_existing_mechanism_v1`은 referenced emission behavior가 **current audit implementation에 이미 존재하고**, current authority contract가 그 behavior 및 correction-row-eliminating terminal sets를 식별할 때만 selectable하다. Referenced emission path가 없거나 correction-row set이 non-empty이면 tooling은 새 behavior를 합성·수용하지 않으며 별도 상위 completion-contract decision 전까지 `blocked`다.
- Planning-time current `audit.py` inspection에서는 disposition-bound third emission route가 확인되지 않았으므로 `owner_approved_existing_mechanism_v1`은 현재 selectable하지 않다. Execution subject에서 exact existing implementation/contract ref가 새로 확인되지 않는 한 owner는 이를 선택할 수 없다.
- Schema에는 default mechanism이 없고 tooling은 current code shape를 근거로 값을 자동 채우지 않는다. Owner mechanism decision이 없으면 Branch A implementation, mechanism-dependent fixture와 correction mutation을 시작하지 않는다.
- Branch B이면 excluded target이 current Layer 2/3/4 union member인지 검사한다. 하나라도 남으면 disposition을 support denylist로 적용하지 않고 `upstream_authority_correction_required`로 차단한다.
- Branch C record는 evidence insufficiency를 보존하지만 complete-path application authority가 아니다.
- `subject_commit`/`subject_tree`는 `issuance_subject` 아래에 두고 발행 provenance 및 D5 issuance-round self-consistency만 증명한다. 후속 D6/regular subject와 commit/tree가 다르다는 이유만으로 disposition을 stale로 만들지 않는다.
- Issuance subject는 tracked disposition을 포함하기 전의 clean evidence subject이며 application successor가 record를 채택한다. 이 two-subject lifecycle은 self-referential commit/tree binding을 금지한다.
- `applicability_binding`은 다음 current content를 exact path/semantic subset/hash로 canonicalize한 **declared exact target-scoped** `applicability_fingerprint`를 가진다.
  - declared pair의 target source row hash/set
  - 각 declared exact target의 Layer 2 membership boolean과 matching row hash 또는 canonical absence marker
  - 각 declared exact target의 pointer-selected Layer 3 membership boolean과 matching row hash 또는 canonical absence marker
  - 각 declared exact target의 Layer 4 membership boolean과 matching row hash 또는 canonical absence marker
  - support predicate ID/version
  - comparison algorithm/version
  - disposition schema/version
- Layer 2/3/4 whole-universe hash는 applicability fingerprint 입력이 아니다. Declared pair와 무관한 FullType의 owner correction은 disposition을 stale로 만들지 않으며 whole-universe regression audit에서 별도로 관찰한다.
- `re_audit_condition`은 위 target-scoped fingerprint 구성요소 중 하나가 달라지거나 normalized collision-class의 current exact member set이 approved declared pair와 달라지면 true가 되는 versioned structured predicate다. Commit/tree equality는 predicate 입력이 아니다. 제3 variant 출현은 whole-universe fingerprint가 아니라 이 exact member-set guard와 Phase 1 discovery census가 fail-closed한다.
- Consumption rule은 다음과 같다.

  ```text
  issuance validation:
    record issuance commit/tree == issuance candidate commit/tree

  later applicability:
    recomputed content fingerprint == approved applicability_fingerprint
    AND re_audit_condition == false
  ```

- 따라서 `same bound content + different commit/tree`는 applicable이고, `changed bound content + same commit/tree`는 stale이다.
- Historical RTC `reference/exception` roles는 `role_resolution_power: none` evidence로만 연결하고 selected support decision 값으로 복사하지 않는다.
- `contract.py`는 schema뿐 아니라 exact count, exact key spelling, issuance self-consistency, approval/evidence hash, relation symmetry, selected mechanism contract와 applicability/re-audit predicate를 검증한다.
- New contract files가 `CONTRACT_FILES`에 들어가므로 non-decision bundle SHA-256가 바뀐다. 이를 automatic carry-forward로 취급하지 않는다.
- Owner ratification은 시간 순서를 갖는 두 단계이며 한 번의 사후 승인으로 합치지 않는다.
  - pre-mutation owner approval: selected branch, per-target `identity_relation`, per-target `support_disposition`, Branch A terminal mechanism과 issuance evidence/applicability candidate
  - post-implementation owner approval: P-1~P-12 contract-bundle rebind receipt와 final application/adoption result
- Post-implementation approval은 pre-mutation semantic decision을 소급 생성·대체하거나 mutation 이전 승인 부재를 치유하지 못한다.
- `tooltip_t1_decision_contract.json`의 top-level D5 rebind record는 post-implementation owner-ratification scope에 다음을 포함한다.
  - predecessor decision-contract Git blob/SHA-256
  - previous non-decision bundle SHA-256와 P-1~P-12 previous `contract_sha256` set
  - new non-decision bundle SHA-256
  - P-1~P-12의 ID/status/required choice/selected choice/owner/support-predicate non-hash invariant digest before/after
  - invariant equality result
  - exact owner approval ref/hash
- Owner가 이 rebind를 승인한 뒤에만 P-1~P-12 `contract_sha256`를 new bundle identity로 갱신한다. Previous hashes와 predecessor blob identity는 rebind record 및 Git history에 superseded historical trace로 남긴다.
- Rebind는 P-1~P-12의 semantic choice를 재개방하거나 변경하지 않는다. Non-hash invariant digest가 다르면 D5 rebind로 처리하지 않고 별도 authority decision 전까지 blocked다.

Validation:

- missing/inconsistent issuance subject, missing evidence, invalid approval hash, duplicated/case-mutated key, conflicting relation, unselected/unsupported mechanism과 non-machine-evaluable re-audit predicate가 nonzero로 실패한다.
- exactly two valid records와 exact target-set hash를 요구한다.
- tooling이 disposition value를 자동 생성하거나 DisplayName/source spelling으로 채우는 경로가 없다.
- same content/different commit fixture는 applicable이어야 하고 changed content/same commit fixture는 stale이어야 한다.
- unrelated FullType의 Layer 2/3/4 membership/row change fixture는 applicable을 유지하고, declared target의 동일 surface change fixture는 stale이어야 한다.
- normalized collision-class exact member set에 제3 variant가 추가되는 fixture는 target-scoped fingerprint가 우연히 같더라도 `re_audit_condition = true`로 차단돼야 한다.
- P-1~P-12 rebind approval, before/after bundle hashes, predecessor trace와 non-hash invariant equality가 모두 검증돼야 한다.
- Branch B foreign-authority conflict가 support mutation 전에 차단된다.

---

### Change 3 — Inventory normalization and make exact-key preservation observable

Purpose:

Collision detector가 발화한다는 사실을 넘어, authoritative T1 path 어디에서도 normalized key가 merge/overwrite/silent-loss를 일으키지 않음을 직접 검증한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d5.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`

Implementation Notes:

- Static inventory denominator는 execution subject에서 exact file list와 각 file SHA-256를 먼저 봉인한 다음 아래 path universe로 한정한다.
  - `Iris/tooling/src/iris_tooling/domains/tooltip_t1/**/*.py`
  - `Iris/tooling/tests/test_tooltip_t1_contract.py`
  - `Iris/tooling/tests/test_tooltip_t1_projection.py`
  - `Iris/tooling/tests/test_tooltip_t1_audit.py`
  - `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json`
  - `Iris/_docs/authority/tooltip_t1/*.json`
- 이 declared universe에서 `.lower()`, `.casefold()`, normalization/comparison helper, dict/set key construction, JSON/JSONL serialization과 D5 disposition lookup을 조사해 다음으로 분류한다.
  - diagnostic grouping
  - comparison only
  - authoritative keying
- `authoritative normalized-key storage path count = 0` claim은 이 exact scan manifest에만 결속한다. Iris 전체 repository 또는 runtime/PZ 전체에 대한 static-analysis claim으로 확대하지 않으며 scan-universe 밖은 Validation Limits에 기록한다.
- Current `normalized_collisions()`는 diagnostic one-to-many grouping으로 유지한다.
- Exact primary key는 original `full_type` string이다. Normalized key는 owner record lookup, readiness row lookup, correction ownership 또는 support inclusion/exclusion key로 사용하지 않는다.
- Stage report는 단순히 모든 stage set이 같다고 가정하지 않고 각 stage의 역할별 expected set을 기록한다.
  - source/adjacent membership: 실제 Layer 2/3/4 exact sets
  - support derivation/census/readiness/candidate audit rows: owner-approved support exact set
  - raw collision observation: supported normalized-class exact member set
  - Branch A target correction-row/T2-blocking sets: fixed `empty`; Branch B: upstream withdrawal 뒤 resulting support에서 재도출한 exact sets
- Branch A의 mechanism-independent expected sets는 다음과 같다.
  - support/readiness/candidate target set: 두 exact identities
  - raw collision observation target set: 두 exact identities
  - `SUPPORT_NORMALIZED_COLLISION` correction-row target set: empty
  - T2-blocking `SUPPORT_NORMALIZED_COLLISION` target set: empty
- 위 네 집합이 Branch A의 governing completion contract다. D5의 `correction closure`는 raw diagnostic observation 보존과 별개로 target correction row 자체가 사라지고 T2-blocking target set도 empty인 상태를 뜻한다. Owner-approved existing mechanism도 이 exact state를 바꿀 수 없다.
- Branch B는 upstream authority withdrawal 후 재도출된 exact support set을 expected set으로 사용한다. Count-only equality는 허용하지 않는다.
- JSON/JSONL canonical serialization과 sorted ordering 뒤 exact spelling을 다시 읽어 set/digest를 비교한다.
- `case_normalization_merge`, `normalized_key_overwrite`, `unexpected_exact_duplicate`, `unexpected_support_row_loss`, `exact_spelling_mutation`을 explicit zero metrics로 방출한다.

Validation:

- declared static scan manifest 안에서 authoritative normalized-key storage path count가 `0`이다.
- support/readiness/candidate stages에서 owner-expected exact set delta가 `0`이다.
- raw observation과 correction set을 별도 assertion으로 검증한다.
- case-insensitive PowerShell object materialization을 authoritative parser로 사용하지 않는다.

---

### Change 4 — Apply the disposition without weakening collision detection

Purpose:

Validated owner disposition을 current T1 support/correction lifecycle에 적용하되 support union, raw detector와 exact identity를 보존한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`

Implementation Notes:

- `run_candidate`는 support union을 기존 case-sensitive expression으로 먼저 계산한다.
- `support_collisions = normalized_collisions(support)`는 disposition 존재 여부와 무관하게 항상 실행하고 summary/raw D5 artifact에 기록한다.
- Exact collision group마다 validated D5 disposition을 exact member set으로 lookup한다.
- Disposition applicability는 current commit/tree equality가 아니라 Change 2의 recomputed declared-target-scoped content fingerprint로 판정한다. Issuance provenance가 다른 commit을 가리켜도 content binding이 같으면 적용하며, 같은 commit이라도 bound target content가 다르면 stale로 차단한다.
- Owner가 predicate refinement를 선택한 경우에만 다음 emission predicate를 구현한다.

  ```text
  emit blocking SUPPORT_NORMALIZED_COLLISION correction
  = raw normalized collision exists
    AND no content-applicable owner disposition covers the exact member set
  ```

- Owner-approved existing mechanism을 선택한 경우 current implementation에 referenced emission behavior가 실제 존재해야 하며, current `mechanism_contract_ref`가 raw observation `declared pair`, correction-row set `empty`, T2-blocking set `empty`와 closure provenance를 정의해야 한다. Emission path가 없거나 correction row를 유지하면 D5 tooling이 새 third mechanism을 즉석에서 해석하지 않고 별도 상위 completion-contract decision 전까지 차단한다.
- 어느 successful Branch A mechanism이든 두 audit row와 support membership을 유지하고 target `SUPPORT_NORMALIZED_COLLISION` correction-row set 및 T2-blocking correction set을 모두 empty로 만든다.
- Branch B는 support union input owners가 approved withdrawal을 이미 반영한 뒤 union을 다시 도출한다. T1 local denylist, negative overlay 또는 post-union row drop을 만들지 않는다.
- Branch C/invalid/content-stale disposition이면 current unresolved blocking correction 두 건을 그대로 발행한다.
- `SUPPORT_NORMALIZED_COLLISION` reason code와 owner 및 Registry의 unresolved default `t2_blocking: true`는 유지한다. Applicable D5 closure는 reason/detector를 삭제하지 않고 target correction emission만 해소한다. 이 D5 complete path는 해당 reason의 non-blocking correction row를 만들지 않는다.
- Closure provenance는 다음을 구별한다.
  - `owner_disposition_reconciliation`
  - `upstream_authority_withdrawal_then_support_rederivation`
  - forbidden `detector_disable`
  - forbidden `reason_code_removal`
  - forbidden `pre_owner_denominator_exclusion`
  - forbidden `unsupported_normalized_merge`
- Raw observation은 `tooltip_support_universe_summary.json#normalized_full_type_collisions`와 D5 dedicated artifact에 남는다.
- Progression과 owner blocker count는 기존처럼 실제 `t2_blocking is True` correction view에서 계산한다. D5는 다른 owner correction을 수정하지 않는다.
- Planning-time Branch A 예상 target delta는 correction row `2 -> 0`, T2-blocking correction `2 -> 0`이다. Raw collision observation은 declared pair로 유지한다. 실행은 actual exact ledger diff를 기록하고 전체 numeric total을 hard-code하지 않는다.

Validation:

- raw collision detector output은 Branch A에서도 present다.
- valid disposition이 없거나 content-stale이면 blocking correction 두 건이 present다.
- same bound content/different commit이면 approved disposition은 applicable이고, changed bound content/same commit이면 stale이다.
- unrelated FullType의 Layer 2/3/4 change는 applicable을 유지하고 declared exact target의 Layer 2/3/4 membership/row change는 stale이다.
- current normalized collision-class exact member set이 declared pair와 다르면 target-scoped fingerprint 일치 여부와 무관하게 re-audit가 발화한다.
- valid Branch A disposition이면 raw observation은 declared pair, support/readiness target set은 둘 다 present이고 correction-row target set과 T2-blocking correction target set은 모두 empty다.
- detector/reason removal, skip-list, normalize-and-merge와 pre-owner row drop metric은 모두 `0`이다.
- non-target support membership과 non-target correction row의 unexpected delta가 `0`이다.

---

### Change 5 — Extend the existing parameterized validation family

Purpose:

Owner-only closure와 exact-key preservation을 최소한의 반증 가능한 fixtures로 고정한다.

Files:

- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py` (regression execution only)
- `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json` (conditional)

Implementation Notes:

- 새 D5 test file이나 standalone validator family를 만들지 않는다.
- Owner mechanism decision이 승인된 뒤 Existing `test_whole_universe_audit_progression` 또는 같은 파일의 단일 parameterized family에 정확히 다음 세 mandatory audit cases를 추가한다.
  1. `Base.LemonGrass`/`Base.Lemongrass` positive exact-row preservation 및 raw-observation/resolved-correction separation
  2. normalized key를 authoritative output key로 사용해 merge/overwrite하는 negative fixture
  3. selected mechanism 기준 valid owner disposition 없이 T2-blocking collision state가 해소되는 negative fixture
- Negative fixtures는 prohibited implementation이 실제로 fail-loud함을 증명해야 한다. 단순히 expected value를 current output에서 복사하지 않는다.
- Existing `nonblocking_correction` test는 generic progression filter contract의 regression으로 보존하되 D5 completion evidence로 사용하지 않는다. D5 target correction rows가 non-blocking으로 남는 candidate는 complete validation에서 실패해야 한다.
- Contract negative coverage는 기존 contract parameterized family의 네 composite rows로 묶는다.
  1. issuance/applicability: wrong subject, same content/different commit, changed content/same commit
  2. target scope: unrelated Layer 2/3/4 change, declared-target change, third collision-class member, wrong/incomplete exact pair
  3. approval/relation: cross-record conflict, invalid approval, Branch B upstream conflict
  4. mechanism/rebind: rejected blocking-axis transition, non-empty correction expectation, unselected mechanism, unauthorized P-1~P-12 rebind
- 새 test file/family를 만들지 않고 각 composite row가 관련 subcase를 함께 assertion한다.
- Projection test는 Layer 4 selection behavior가 D5에 의해 달라지지 않았음을 재실행한다.
- Focused pytest collection은 fixture row 증가로 달라질 수 있으므로 implementation 전후 `--collect-only` exact identities/count를 기록한다. Regular current pytest denominator, required standalone denominator와 recurring execution-unit denominator도 current command owner 결과에서 before/after로 각각 기록하며 서로 합산하지 않는다.

Validation:

- Mandatory positive case에서 exact target count `2`, exact spelling mutation `0`, raw group count `1`, correction-row target count `0`과 T2-blocking target correction count `0`을 각각 검사한다.
- 두 negative cases가 prohibited behavior를 놓치면 test가 실패한다.
- Existing focused families의 prior assertions를 약화하지 않는다.
- `d5_validation_denominator_before_after.json`에 focused lifecycle pytest collection, regular current pytest, required standalone과 recurring execution units의 distinct before/after count/set digest/delta reason을 필수 기록한다.

---

### Change 6 — Re-audit the affected range and whole universe

Purpose:

D5 application이 target에만 승인된 효과를 만들고 Layer 2/3/4 selection 및 다른 owner correction을 손상하지 않았음을 exact before/after relation으로 검증한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d5.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- repository-external predecessor/candidate/reconciliation roots

Implementation Notes:

- `d5-reconcile` route contract는 다음 required inputs를 가진다.

  ```powershell
  iris-tooling --repository-root <repo> build tooltip-t1 d5-reconcile --before-root <external-immutable-before-root> --after-root <external-immutable-after-root> --disposition <tracked-disposition-path> --output-root <external-empty-root>
  ```

- `before-root`는 predecessor ancestry/equivalence가 검증된 canonical T1 candidate root이고 `subject_binding.json`, `run_receipt.json`, support census/summary, readiness manifest와 correction ledger를 포함해야 한다.
- `after-root`는 approved disposition/application subject의 canonical T1 candidate root이며 동일 required artifact set과 valid receipt를 포함해야 한다.
- `disposition`은 tracked D5 disposition exact path이고 its issuance/applicability/approval hashes가 after-root에 결속돼야 한다.
- `output-root`는 repository-external, non-existing 또는 empty, before/after와 서로 다른 immutable destination이어야 한다.
- Reconcile route는 before/after artifacts를 수정하지 않고 exact row/set/digest comparison, closure provenance, selected-mechanism state, denominator report와 bundle inputs만 쓴다.
- `d5_reconciliation_receipt.json`은 before/after run receipt hashes, disposition/applicability identity, selected mechanism, output artifact hashes와 native exit status를 결속한다.
- Missing artifact, receipt/hash mismatch, wrong predecessor relation, after subject/applicability mismatch, same before/after root, repository-internal/non-empty output, unexplained target/non-target delta 또는 mutable pointer가 있으면 artifact를 partial success로 채택하지 않고 nonzero로 실패한다.
- Before baseline은 predecessor-equivalent clean subject에서 생성한 canonical support census, readiness manifest, correction ledger와 source hashes다.
- After candidate는 validated D5 authority를 포함한 clean subject의 normal `build tooltip-t1` output이다.
- Affected range는 target별 다음을 비교한다.
  - source/Layer 2/3/4 membership
  - support state와 inclusion rule
  - owner disposition lookup/binding
  - readiness row presence
  - raw collision group membership
  - correction row/state
  - Layer 4 selected identity tuple
  - closure provenance
- Whole universe는 exact sets/digests와 attributed row deltas를 비교한다.
  - support universe
  - Layer 2 classification membership
  - pointer-selected Layer 3 membership
  - Layer 4 owner membership과 selected identity tuples
  - readiness manifest FullType set
  - correction ledger keyed by exact FullType/layer/reason/owner/locale/selected identity
  - progression owner distribution
- Branch A에서 non-target delta는 모두 zero여야 한다. Branch B의 upstream correction delta는 owner-approved expected exact rows와 일치해야 하며 unrelated delta가 없어야 한다.
- Other-owner ledger의 current actual result를 기록하며 predecessor count에 맞춰 arithmetic rewrite하지 않는다.
- Run A와 Run B는 distinct empty roots에서 same exact subject/input으로 실행하고 canonical D5 result bytes를 비교한다.

Validation:

- non-target support membership unexpected delta `0`
- Layer 2/3/4 D5-induced unexpected selection delta `0`
- other-owner arithmetic rewrite `0`
- case-normalization merge/overwrite `0`
- unexpected duplicate/loss/spelling mutation `0`
- Run A/Run B canonical bytes identical
- input source mutation `0`

---

### Change 7 — Ratify the bounded D5 candidate and validate the bundle

Purpose:

D5 disposition/application, contract-bundle delta, focused candidate validation과 immutable bundle을 같은 issuance/application evidence chain에 결속한다.

Files:

- repository-external D5 owner approval/rebind receipts
- repository-external D5 shared-path delta and integration manifest
- isolated Tooltip T1 candidate

Implementation Notes:

- D5 owner decision, isolated contract/code delta와 candidate hash inputs를 workstream validation 전에 완성한다.
- Pre-mutation owner approval은 exact clean issuance candidate commit/tree, target-set/census hash, schema/record hash, selected branch, per-target semantic/support disposition, collision terminal mechanism과 target-scoped applicability fingerprint candidate에 결속한다.
- Implementation과 검증 뒤 별도의 post-implementation owner approval이 P-1~P-12 contract-bundle rebind receipt 및 final application/adoption evidence를 ratify한다. 이 사후 승인은 pre-mutation semantic approval을 소급 생성하거나 대체하지 않는다.
- Governance/current paths는 protected read-only inputs다. D5 disposition과 application delta는 isolated bundle authority이며 global current가 아니다.
- D6는 immutable D5 integration manifest, applicability fingerprint와 rebind receipt를 검증한 뒤 global manifest/index/locator integration 여부를 별도 authority로 결정한다. D5 complete는 그 D6 action이 이미 수행됐다는 뜻이 아니다.
- Existing focused command를 그대로 사용한다.

  ```powershell
  uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
  ```

- Normal Tooltip T1 candidate는 repository-external empty root에 생성한다.

  ```powershell
  iris-tooling --repository-root <repo> build tooltip-t1 --output-root <external-empty-root> --decision-contract-sha256 <sha256> --verify-invariants
  ```

- D5 candidate를 distinct external roots에 두 번 생성해 canonical D5 result bytes를 비교한다.
- Canonical clean-checkout Run A/B, repository comparator와 Tooltip T1 finalizer는 T1-D6가 integrated subject에서 한 번 실행한다.
- D5 correction 감소가 있어도 다른 blockers가 남는 동안 progression은 blocked이고 production T2 handoff는 `0`이다.
- Focused pytest의 file/function denominator delta를 기록하며 기본 기대값은 `0`이다.

Validation:

- Focused command exit `0`
- installed-package Tooltip T1 candidate exit `0`
- D5 candidate Run A/B bytes identical
- bundle validator exit `0`
- all workstream receipts share exact candidate commit/tree and artifact hashes
- P-1~P-12 rebind owner approval and non-hash invariant equality
- global current-authority manifest/index/locator D5-induced delta `0`
- no production T2 handoff emitted while any blocking correction remains

---

### Change 8 — Seal the D5 bundle and hand off only to T1-D6

Purpose:

Owner authority와 lifecycle evidence를 역할별로 분리하고 D6가 검증할 수 있는 immutable integration bundle을 만든다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d5.py`
- repository-external D5 bundle
- repository-external D6 integration proposal

Implementation Notes:

- Tracked `tooltip_t1_d5_current_support_disposition.json`이 authority-bearing owner record다.
- External bundle은 census, before/after, validation, provenance와 integration evidence만 소유한다.
- `integration_manifest.json`은 최소 다음을 결속한다.
  - D5 issuance subject commit/tree와 application subject commit/tree
  - T1-C predecessor commit/tree와 ancestry/equivalence evidence
  - approved target exact set/hash
  - owner disposition path/hash/approval, issuance provenance와 applicability fingerprint
  - P-1~P-12 before/after contract-bundle rebind receipt와 non-hash invariant equality
  - before/after support exact sets/hashes
  - before/after raw collision and blocking correction exact sets/states
  - closure provenance
  - affected-range/whole-universe reports
  - validation denominator before/after report
  - validation ceiling record
  - focused tests, candidate materialization Run A/B, affected-range audit와 bundle-validator receipt hashes
  - every bundle artifact SHA-256
- `artifact_digests.json`는 자기 자신과 mutable pointer를 제외한 canonical sorted artifact list를 가진다.
- Bundle writer는 existing non-empty root, issuance provenance inconsistency, content-applicability mismatch, missing required artifact, hash mismatch와 repository-internal output을 거부한다.
- D5 completion은 owner disposition, exact-key preservation, correction reconciliation과 D6 integration readiness까지만 주장한다.
- `d5_validation_ceiling.json`은 `validated`, `out_of_scope`, `unvalidated_but_in_scope`를 별도 arrays로 기록한다. Owner semantic judgment의 correctness는 `unvalidated_but_in_scope`이고, tooling은 disposition 존재/binding/authority/application invariants만 validated로 기록한다.
- D5 bundle은 D6가 global current-authority integration을 판단할 input이다. Bundle sealing 자체가 manifest/index/locator integration을 수행하거나 그 완료를 주장하지 않는다.
- Governance status 반영과 global current-authority adoption은 D6가 모든 workstream bundle을 통합한 뒤 수행한다. D5는 이를 직접 수행하거나 docs-only successor를 발행하지 않는다.

Validation:

- required artifact missing `0`
- artifact hash mismatch `0`
- issuance-provenance inconsistency `0`
- disposition applicability mismatch `0`
- unauthorized P-1~P-12 rebind `0`
- validation denominator undisclosed delta `0`
- mutable latest pointer created `0`
- predecessor artifact rewrite `0`
- current runtime/package authority promotion `0`
- global current-authority manifest/index/locator mutation `0`
- production T2 handoff created `0`

---

## 7. Validation Plan

### Automated Validation

#### Subject and census gates

- clean exact subject and commit/tree binding
- predecessor ancestry or exact path/blob equivalence manifest
- declared pair exact cardinality and normalized-class discovery equality
- exact source/Layer 2/3/4/support membership matrix
- pre/post input SHA-256 equality

#### Contract and owner disposition gates

- JSON schema validation
- exact target key spelling and pair completeness
- issuance subject/tree self-consistency and target-set/source-census hash binding
- owner/approval/evidence reference validation
- cross-record identity relation consistency
- declared exact target-scoped applicability fingerprint and machine-evaluable exact-member-set re-audit predicate
- same content/different commit applicability positive case
- changed content/same commit staleness negative case
- unrelated FullType Layer 2/3/4 change remains-applicable case
- declared-target Layer 2/3/4 change becomes-stale case
- third normalized collision-class member forces-re-audit case
- owner-selected Branch A terminal mechanism and mechanism-contract validation, including rejection of blocking-axis transition and every non-empty correction-row expectation
- P-1~P-12 rebind approval, historical previous hash trace and non-hash invariant equality
- Branch B upstream-authority conflict fail-closed validation

#### Focused tests

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

- exact pair positive preservation fixture
- normalized authoritative-key merge/overwrite negative fixture
- disposition-less correction closure negative fixture
- existing progression, whole-universe, projection and finalizer regressions
- owner-selected mechanism case는 raw observation `declared pair`, correction-row target `empty`, T2-blocking target `empty`라는 공통 completion invariant로 고정

#### Candidate and D5 reconciliation

- D5 census to repository-external empty root
- normal installed-package Tooltip T1 candidate
- before/after exact support/correction comparison
- role-aware stage exact-set comparison
- closure provenance validation
- non-target and Layer 2/3/4 whole-universe invariance
- D5 candidate materialization Run A/Run B byte comparison
- required `d5-reconcile` before/after/disposition/output contract and fail-closed path checks

#### Integrated canonical validation ownership

- focused lifecycle pytest `--collect-only` exact identity/count before/after disclosure
- focused lifecycle pytest, regular current pytest, required standalone와 recurring execution-unit exact denominator before/after disclosure; four reported axes remain distinct and no arithmetic aggregate is reported as another denominator
- D5 candidate Run A/B byte comparison and bundle validator
- receipt-bound canonical full gate Run A/B, repository comparator와 Tooltip T1 post-gate finalizer는 T1-D6가 integrated subject에서 한 번 수행
- D5 integration bundle digest verification

Only an exact relevant command exiting `0` is reported as PASS. Missing `uv`, installed package/environment authority, canonical launcher inputs or PowerShell requirements makes the corresponding gate BLOCKED.

### Manual Validation

- Inspect the two source item rows side by side and confirm the owner packet does not reduce them to DisplayName equality.
- Inspect exact Layer 2 memberships, Layer 3 fact IDs/source refs and Layer 4 membership difference.
- Inspect the owner disposition and verify that relation/support values are owner-authored rather than inferred by tooling.
- Confirm raw collision observation remains visible after Branch A closure.
- Confirm no target skip-list, normalized allowlist, post-union denylist or reason-code deletion was introduced.
- Inspect target readiness rows and correction ledger before/after using exact case-sensitive keys.
- Inspect non-target support/correction delta and any legitimate Branch B upstream delta attribution.
- Confirm D5 scope 밖의 tracked runtime Lua, current generation pointer와 package-related source path에 unexpected file delta가 `0`이다. Visual rendering 또는 package output equivalence는 이 검사로 주장하지 않는다.
- Confirm final claims distinguish raw observation, correction row and T2-blocking correction count.

### Validation Limits

- No actual PZ runtime FullType resolution test
- No `IrisAltTooltip` visual rendering or font/UI-scale fit test
- No multiplayer or long-session runtime validation
- No Menu parity completion test beyond existing current T1 relation checks
- No semantic correctness judgment of owner disposition by tooling
- No complete semantic review of other owner corrections
- No external mod compatibility sweep
- No package/install/deployment validation
- No release/Workshop readiness validation
- No T2 static generator/runtime validation
- Static normalization inventory의 `0` claim은 declared Tooltip T1 code/test/fixture/authority scan manifest에만 적용되며 Iris 전체 repository, runtime Lua 또는 PZ engine은 scan claim 밖이다.
- Independent-review satisfaction은 D5 positive claim이 아니며 새 completion gate로 검증하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

Affected.

- Adds an issuance-bound, content-applicable owner authority record for two exact support identities.
- Consumes an owner-selected rule for when `SUPPORT_NORMALIZED_COLLISION` represents an unresolved owner correction.
- Preserves the support predicate itself as a case-sensitive explicit union.
- Does not give T1 tooling semantic identity authority.
- Does not update the global current-authority manifest/index/environment locator; that integration remains D6-owned.

### Runtime Behavior Surface

No D5-owned runtime mutation for Branch A.

- No runtime Lua or Alt Tooltip behavior changes.
- Branch B cannot complete through presentation-only mutation. Required upstream correction is separately owned and keeps D5 blocked until applied and re-audited; that separate correction's runtime surface must be declared and validated by its own plan and is not covered by this D5 claim.

### Compatibility Surface

No supported public API/SPI/package-format change.

- Exact case-sensitive identity preservation is strengthened in the offline T1 lifecycle.
- General runtime compatibility remains outside the claim.

### Sealed Artifact Surface

Affected additively.

- T1-C predecessor artifacts and closeout remain immutable.
- New D5 successor evidence, receipts and D6 manifest are sealed in a repository-external root.
- P-1~P-12 contract-bundle rebind is separately owner-ratified and preserves predecessor hashes/blob identity as historical trace.
- No mutable latest pointer is introduced.

### Public-Facing Output Surface

None.

- Tooltip text, slot ordering, locale surfaces, Menu output and runtime selection are not changed by Branch A.
- D5 decides support authority/correction readiness, not displayed wording.

---

## 9. Risk Analysis

### Architecture Risk

- **Normalized key becomes authoritative.** A `rows[full_type.lower()] = row` shape can silently overwrite one identity. Mitigation: exact primary keys, one-to-many diagnostic grouping, negative fixture and stage exact-set report.
- **Presentation owner bypasses upstream authority.** Branch B could become a local denylist. Mitigation: support remains re-derived from the exact union; any still-present upstream membership blocks application.
- **Historical RTC role is misread as current support decision.** Mitigation: record `role_resolution_power: none` and treat historical bundle as evidence only.
- **Non-blocking progression semantics are mistaken for D5 correction closure.** Mitigation: generic `t2_blocking is True` filtering remains intact, but D5 complete independently requires the target correction-row set itself to be empty; schema rejects blocking-axis transition and any existing mechanism with a non-empty correction expectation.
- **Contract bundle rebind changes unrelated decisions.** Mitigation: owner-ratified before/after rebind receipt, predecessor hash trace and P-1~P-12 non-hash invariant equality are mandatory.
- **D5 crosses into global authority integration.** Mitigation: manifest/index/environment locator are excluded from the D5 write set and D6 consumes the sealed integration manifest.

### Runtime Risk

- Direct runtime risk is low because runtime Lua/package paths are out of scope.
- An accidental source mutation during census/audit could alter current payload. Mitigation: repository-external outputs, clean subject and before/after source hashes.
- Branch B may require actual upstream data changes with wider runtime implications. Mitigation: D5 stops blocked and does not absorb that work.

### Compatibility Risk

- Case-insensitive tooling or Windows object materialization can collapse the pair. Mitigation: Python JSON parsing, exact strings, canonical set digests and explicit duplicate/loss metrics.
- A third case variant can appear after planning. Mitigation: normalized-class discovery census and scope-mismatch stop.
- Re-audit predicate can become stale prose or conflict with commit binding. Mitigation: commit/tree is issuance provenance only; applicability is a versioned declared-target-scoped content fingerprint plus exact collision-member-set guard, with positive/negative cross-subject fixtures.

### Regression Risk

- Removing two blocking corrections may accidentally modify unrelated owner counts. Mitigation: exact row-key ledger diff, not aggregate arithmetic.
- Raw observation may disappear when correction emission is refined. Mitigation: detector runs before disposition reconciliation and has its own mandatory artifact/assertion.
- Support rows may survive census but disappear from readiness/candidate output. Mitigation: role-aware stage exact-set comparison after serialization.
- Existing T1 candidate/formal-closeout vocabulary may be conflated with D5 lifecycle state. Mitigation: preserve `partial/implemented_only` before canonical gate while D5 uses only `complete/blocked`.
- Dirty planning workspace can be mistaken for execution subject. Mitigation: dedicated clean subject is mandatory; current dirty docs are not adopted implicitly.

---

## 10. Rollback Plan

### Before owner disposition

- Discard repository-external census/diagnostic roots.
- Do not modify support, correction, current source/runtime or predecessor artifacts.
- If census, equivalence or evidence is incomplete, retain the existing two blocking corrections and mark D5 blocked.

### After disposition but before application

- Reject invalid, issuance-inconsistent or content-stale owner record without applying it. A later commit/tree alone is not a rejection reason when applicability content is unchanged.
- Preserve the prior valid tracked authority or use an additive superseding owner record according to current governance; do not rewrite external predecessor evidence.
- Keep current support union and blocking corrections unchanged.

### After application candidate

- Do not adopt the candidate if exact row loss, normalized overwrite, unsupported exclusion, non-target delta, detector weakening, missing provenance, issuance/applicability inconsistency, unauthorized contract rebind or nondeterminism appears.
- Revert only D5-owned code/contracts/docs through a normal inverse commit. Do not use destructive workspace reset or remove unrelated user changes.
- Return to the predecessor-equivalent T1 behavior in which both exact support rows and two blocking corrections remain.
- Delete no material evidence; failed external attempts remain immutable or are discarded only when explicitly classified as disposable candidate roots.

### After D5 bundle sealing

- A new corrective successor supersedes the faulty D5 authority/application; existing receipts and closeouts remain immutable evidence.
- Do not edit a validated machine subject in place or relabel an integration proposal as adopted current authority.
- Never rollback by disabling collision detection, deleting the reason code or adding a target skip-list.

### Immediate stop conditions

- predecessor inclusion/equivalence cannot be established
- execution checkout is dirty
- normalized discovery class differs from the declared pair
- exact source authority for either target cannot be reconstructed
- disposition/approval/evidence is missing, stale or contradictory
- owner requires runtime evidence that D5 cannot produce
- Branch A terminal mechanism is not owner-approved or lacks exact expected-state/contract binding
- disposition issuance provenance and current applicability are conflated
- P-1~P-12 rebind approval, predecessor hash trace or non-hash invariant equality is missing
- Branch B target remains asserted by any current support-union owner
- support mutation occurs before disposition validation
- normalized key becomes an authoritative lookup/storage/output key
- raw detector or reason code is weakened/removed
- target exact row disappears or spelling changes unexpectedly
- non-target or other-owner delta cannot be exactly attributed
- validation denominator before/after delta is undisclosed
- D5 attempts to update global current-authority manifest/index/environment locator
- mandatory negative fixture does not fail prohibited behavior
- D5 candidate materialization Run A/Run B differs/fails, or D6 later rejects the bundle
- D5 bundle hash/subject validation fails

---

## 11. Governance Constraints

- Preserve `docs/Philosophy.md` and Iris's evidence-based, neutral, read-only information role.
- Preserve Hub & Spoke boundaries; D5 introduces no dependency on another spoke.
- Keep PZ runtime Iris 100% Lua and keep D5 tooling offline Python only; no JVM/Lua mixing is introduced.
- T1 audit/tooling validates and consumes owner disposition; it does not author semantic identity decisions.
- Branch A correction terminal mechanism도 presentation-contract owner가 implementation 전에 선택하며 tooling/schema가 default를 발행하지 않는다.
- Exact FullType is authoritative. Normalization is diagnostic/comparison-only and one-to-many.
- Owner disposition precedes support/correction mutation.
- Support remains a case-sensitive exact union; no local denylist or silent denominator exclusion.
- Foreign upstream authority is corrected by its owner, not overridden by presentation tooling.
- Detector preservation, reason-code preservation and fail-loud unknown-reason policy are mandatory.
- Raw observation, owner disposition, correction row, blocking axis and support membership remain separate artifacts/claims.
- Existing Layer 2/3/4 semantic selection, locale/Menu readiness and 0~4 fixed-slot contract are not reopened.
- Runtime/build-time and authority/lifecycle evidence separation remain intact.
- Disposition commit/tree는 issuance provenance이고 후속 applicability는 declared-target-scoped content fingerprint와 exact collision-member-set guard가 소유한다.
- P-1~P-12 contract bundle hash rebind는 explicit owner approval, predecessor hash trace와 non-hash invariant equality 없이는 수행하지 않는다.
- D5는 global current-authority manifest/index/environment locator를 갱신하지 않으며 D6가 sealed integration bundle을 소비한다.
- Repository-external immutable output and no mutable latest pointer are mandatory.
- Predecessor closeout, failed attempts and historical RTC evidence are not rewritten.
- Other owner corrections are reported from actual current audit; no arithmetic normalization to predecessor counts.
- Minimal diff and additive successor preference apply.
- Existing Tooltip T1 focused families are reused, and D6 remains the sole canonical full-gate/comparator/finalizer owner; no independent validator framework is introduced.
- Focused pytest, regular current pytest, standalone validation과 recurring execution-unit denominator는 before/after로 각각 공개하며 합산하지 않는다.
- Independent review는 새 D5 completion gate나 positive claim으로 추가하지 않는다.
- Missing required tooling or nonzero exact validation command means BLOCKED, not assumed PASS.
- D5 complete does not imply T2 OPEN, production handoff, runtime adoption, package/install, compatibility or release readiness.

---

## 12. Expected Closeout State

### Planning-time expected closeout

**Conditional `complete`; otherwise `blocked`.**

Planning-time evidence strongly supports that the discovery class is exactly the declared pair and that current T1 already preserves both exact keys through source, Layer 2 and Layer 3. It does not authorize the semantic/support answer. `Iris presentation-contract owner` must still approve the relation and per-target support disposition.

Current code shape에서는 raw collision summary와 correction emission이 이미 분리돼 있어 predicate refinement가 최소-diff planning recommendation이다. 그러나 owner는 schema default 없이 correction-row-eliminating mechanism을 pre-mutation 승인해야 한다. Owner-selected mechanism이 발행되기 전에는 Branch A implementation과 mechanism-dependent validation을 시작하지 않는다.

이 계획은 로드맵 충돌 판정으로 **Option A — correction-row closure**를 채택한다. Branch A 공통 terminal invariant는 raw pair observation 유지, 두 exact support identity 보존, `SUPPORT_NORMALIZED_COLLISION` correction-row target set `empty`와 T2-blocking target set `empty`다. `resolved_observation_blocking_axis_transition_v1` 및 correction-row persistence를 요구하는 existing mechanism은 별도 상위 completion-contract 변경 없이는 D5 complete authority가 아니다.

### Complete criteria

D5 is `complete` only when all of the following hold.

- exact execution subject and predecessor ancestry/equivalence are bound
- normalized discovery class equals the declared exact pair
- source/support entry-path census is complete
- exactly two valid owner disposition records are issuance/evidence/approval-bound and content-applicable to the application subject
- cross-record identity relation is consistent
- applicable branch and Branch A terminal mechanism are owner-approved
- pre-mutation semantic/mechanism approval precedes every mutation, and a separate post-implementation approval ratifies the rebind receipt and final application/adoption evidence without retroactive substitution
- same content/different commit remains applicable and changed content/same commit is stale
- unrelated FullType Layer 2/3/4 changes remain applicable, declared-target Layer 2/3/4 changes become stale, and a third collision-class member forces re-audit
- P-1~P-12 contract-bundle rebind is owner-approved, predecessor hashes are preserved and all non-hash invariants are equal
- Branch B, if selected, has completed upstream authority withdrawal before support re-derivation
- raw collision detector remains active
- Branch A raw observation equals the declared pair, while the `SUPPORT_NORMALIZED_COLLISION` correction-row target set and T2-blocking target set are both empty
- owner-expected support exact set equals actual support/readiness/candidate exact set
- forbidden merge/overwrite/loss/duplicate/spelling-mutation metrics are zero
- prohibited closure provenance counts are zero
- non-target support and Layer 2/3/4 unexpected deltas are zero
- unrelated owner correction arithmetic rewrite is zero
- mandatory three fixtures pass, including negative controls
- focused pytest, regular current pytest, standalone and recurring execution-unit denominator before/after reports are complete and kept separate
- focused command, installed candidate, D5 candidate Run A/B and bundle validator all exit `0`
- D5 candidate Run A/B canonical result is byte-identical
- immutable bundle, hashes, run receipt and D6 integration manifest validate
- validation ceiling records `validated`, `out_of_scope` and `unvalidated_but_in_scope`
- D5-induced global current-authority manifest/index/environment-locator and governance status delta is zero
- no production T2 handoff is emitted while other blockers remain

If evidence is insufficient, runtime evidence is declared mandatory but unavailable, upstream authority correction remains outstanding, or any invariant/gate fails, D5 remains `blocked`. Partial code or a candidate audit may be retained as implementation evidence but does not change the D5 terminal vocabulary or current correction state.

### Validation ceiling closeout

The D5 closeout and `d5_validation_ceiling.json` must classify claims as follows.

```text
validated:
- disposition schema, issuance provenance, approval/evidence and content applicability binding
- owner-selected mechanism application consistency
- owner disposition closure (record issued, binding valid, application consistent)
- exact-key preservation, closure provenance and whole-universe bounded invariants
- focused tests, candidate materialization determinism, affected-range audit and bundle integrity

unvalidated_but_in_scope:
- owner semantic judgment correctness for identity_relation/support_disposition
  (owner authority decides it; tooling validates only existence/binding/application)

out_of_scope:
- runtime FullType interpretation and visual behavior
- Menu parity completion, package/install, full RTC, release/deployment
- D6 global current-authority manifest/index/environment-locator integration
```

Missing or overlapping classification blocks D5 closeout. `unvalidated_but_in_scope` is not silently promoted to machine-validated.

Closeout may state `owner disposition closure = complete`; it must not state or imply `owner semantic judgment correctness = validated`.

### Expected successful D5 claims

```text
Tooltip T1-D5 exact FullType support disposition closure = complete
approved D5 exact target set has issuance-bound, content-applicable presentation-owner disposition
case-sensitive exact identity preservation = validated for the D5/T1 offline path
raw normalized collision observation = explicitly reported
unresolved T2-blocking SUPPORT_NORMALIZED_COLLISION target correction = 0
  only when the owner-selected Branch A mechanism's applicability and terminal conditions hold
SUPPORT_NORMALIZED_COLLISION correction-row target set = empty
resolved_observation_blocking_axis_transition_v1 = excluded from D5 complete path
forbidden normalized merge/overwrite/row loss = 0
D5 immutable correction bundle = ready for T1-D6 integration
```

If the phrase `SUPPORT_NORMALIZED_COLLISION = 0` is used, the artifact and axis must be named. Raw observation, correction row and T2-blocking correction count are not interchangeable.

### Explicitly not established

- all Tooltip T1 upstream corrections complete
- `T2_FULL_DATA_PROGRESSION = OPEN`
- production T2 handoff exists
- T2 static Tooltip generator/runtime is ready
- PZ runtime treats the two FullTypes as the same or different object
- Tooltip/Menu visual/runtime parity is complete
- Layer 2/3/4 semantic correctness outside the approved D5 disposition
- general case-collision framework is complete
- full Runtime Compatibility PASS
- package/install/release/Workshop/deployment readiness
- independent-review satisfaction
- global current-authority manifest/index/environment-locator integration complete
