# Iris Tooltip T1-D1 Layer 2 Classification Authority Completion Implementation Plan

> 상태: planned / implementation not started / owner-resolution gates required
> 작성일: 2026-08-28
> 기준 로드맵: `ROADMAP — Iris Tooltip T1-D1: Layer 2 Classification Authority Completion`
> 검증 깊이: heavy — authority, provenance, determinism, whole-universe completeness, KO/EN surface binding, T1 re-audit
> 조사 기준: repository `HEAD 95e17f5b44525a54c202fb7e6e062336d98d4544`, tree `1c672145b3deef3795df181bc106bd776900a84b`, dirty working tree의 current Tooltip T1 successor files 포함

이 계획은 Tooltip이 직접 classification을 추론하게 만드는 계획이 아니다. Classification owner가 이미 소유하거나 명시적으로 승인한 membership, primary navigation identity, locale surface, authority와 provenance를 하나의 canonical Layer 2 owner output으로 발행하고, 기존 T1 audit이 그 output을 읽게 하는 offline correction 계획이다.

현재 코드 조사에서 확인한 출발점은 다음과 같다. 아래 수치는 조사 시점 관측값이며 exact-subject terminal invariant가 아니다.

| Surface | Current observation | Planning consequence |
| --- | --- | --- |
| T1 support owner | `tooltip_t1_decision_contract.json`과 `audit.py`가 Layer 2/3/4 current owner FullType의 case-sensitive 합집합을 support predicate로 사용한다. 현재 correction baseline은 `2,280`이다. | `2,280`을 영구 고정하지 않고 실행 exact subject에서 같은 owner-ratified predicate로 재도출한다. |
| Layer 2 runtime projection | `IrisClassifications.lua`에는 2,079 exact row, 50 distinct tag, 291 multi-membership row와 27개 `IrisPrimarySubcategory` override가 있다. | runtime table 자체를 T1 resolved output으로 사용하지 않는다. Classification owner 내부 census input으로만 사용한다. |
| Primary gap | 291개 multi-membership 중 265개에는 explicit `IrisPrimarySubcategory`가 없다. `IrisBrowserProjectionBuilder.lua`는 presentation rank/description priority로 `primaryLocation`/`primaryTag`를 계산한다. | presentation order를 semantic primary authority로 승격하지 않는다. missing primary는 owner resolution이 필요하다. |
| `Misc.9-A` | actual table에는 `Misc.9-A` membership row가 408개 있으나 파일 header는 fallback 393개라고 기록한다. Current decision은 `Misc.9-A`를 일반 rule이 아닌 output-stage fallback으로 봉인했다. | header count를 authority로 사용하지 않고 actual row census를 기록한다. raw fallback row를 resolved identity로 승격하지 않는다. |
| Exact identity | exact duplicate FullType은 관측되지 않았고 `Base.LemonGrass`/`Base.Lemongrass` 한 normalized-collision pair가 존재한다. | exact bytes를 보존하고 normalization은 collision report에만 사용한다. |
| Locale labels | `IrisBrowserCategoryIndex.lua`에는 9개 category key와 50개 subcategory key가 있고 KO/EN translation source 모두 59개 key를 각각 한 번 제공한다. 다만 sealed taxonomy는 `1-K=Security`, `1-L=Storage`인데 current EN과 Browser fallback은 `1-K=Storage Containers`, `1-L=Bags`여서 identity/surface authority가 충돌한다. | key presence를 surface readiness로 간주하지 않는다. combined template을 역파싱하지 않고, 별도 label을 census한 뒤 충돌 surface는 exact owner correction/approval 대상으로 보낸다. |
| Menu Layer 2 route | `IrisBrowserProjectionBuilder.lua`가 `StaticData.get("classifications")`의 raw membership을 읽고 presentation order와 override를 적용한다. `IrisBrowserVariantIndex.lua`도 `IrisPrimarySubcategory` compatibility global을 소비한다. | D1에서는 route를 관측하고 no-regression만 확인한다. actual Menu source migration과 Menu consumer correction closure는 별도 scope다. |
| T1 Layer 2 route | `layer2_tooltip_input_contract.json`은 `current_route=no_admissible_authority_relation`이고 `audit.py`는 모든 support row에 `CLASSIFICATION_RESOLVED_IDENTITY_MISSING`을 무조건 발행한다. | canonical owner output 채택 후 contract와 audit input wiring을 함께 갱신해야 한다. 기존 audit code를 전혀 바꾸지 않는 방식으로는 D1을 닫을 수 없다. |
| Current producer boundary | installed `iris_tooling`과 `Iris/build/ENTRYPOINTS.md`가 current offline command owner다. Existing `classification` domain은 세 runtime index candidate만 생성·설치하며 Layer 2 owner output은 아직 만들지 않는다. | 새 materializer/validator는 installed classification domain에 추가하고 retired one-shot/source-root script를 current producer로 복원하지 않는다. |

실행 시점에는 clean exact commit/tree, installed wheel identity, current authority/route, T1 support predicate input, classification source, locale source와 T1 contract bundle을 다시 hash-bind한다. 위 dirty-worktree 관측값을 그대로 terminal evidence로 재사용하지 않는다.

---

## 1. Objective

exact-subject T1 support universe의 모든 case-sensitive FullType에 대해 Classification owner가 다음 두 terminal state 중 정확히 하나를 canonical output으로 발행하게 한다.

```text
resolved
owner_approved_absence
```

Resolved row는 다음 관계를 보존한다.

```text
exact FullType bytes
-> classification memberships
-> category identity
-> owner-resolved primary subcategory identity
-> separate category/subcategory surface references
-> exact KO/EN surfaces
-> classification authority reference
-> classification provenance reference
```

Owner-approved absence는 approved Classification evidence를 모두 적용해도 classification을 확정할 수 없다는 positive owner disposition만 표현한다. producer failure, ambiguous primary, missing provenance, locale defect 또는 unsupported inference를 absence로 바꾸지 않는다.

최종 실행 흐름은 다음과 같다.

```text
exact subject + owner-ratified T1 support predicate
-> read-only membership/primary/surface/provenance census
-> bounded owner resolution registry
-> Classification-owned deterministic materializer
-> canonical Layer 2 owner output
-> independent Classification validation
-> T1 Layer 2 consumption
-> new exact-subject T1 re-audit
-> T1-D1 closeout
```

D1 complete의 필수 결과는 다음과 같다.

```text
Classification owner blocker count = 0
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0
```

다른 owner correction이 남으면 `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS`와 production T2 handoff `0`을 유지한다.

---

## 2. Scope

### Included

- clean exact subject와 owner-ratified T1 support universe 재도출
- Classification/Menu/Layer 2 label/Layer 3 등 서로 다른 denominator의 명시적 register
- `IrisClassifications.lua` membership, `IrisPrimarySubcategory`, fallback, provenance 상태의 read-only census
- category/subcategory taxonomy와 existing separate KO/EN label key/surface census
- `owner_resolved / fallback_derived / unclassified` pre-resolution 상태 구분
- single/multi membership과 primary authority source 분리
- 실제 authority gap에 한정한 owner resolution/absence registry
- Classification-owned canonical Layer 2 output schema, materializer, validator와 hash-bound candidate/install route
- exact FullType, authority, provenance와 locale surface의 deterministic serialization
- T1 Layer 2 input contract와 audit consumer wiring의 successor update
- whole-universe Classification audit와 owner-source correction/regeneration loop
- current Menu source route의 read-only dependency observation과 supported facade no-regression 확인
- focused package tests, candidate Run A/B byte comparison과 receipt-bound clean-checkout validation
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, command/authority route의 additive successor adoption
- T1-D1 상태와 T2 progression을 분리한 closeout

### Explicitly Out Of Scope

- current Menu classification source migration
- Menu consumer correction closure 또는 independent Menu identity evidence 생성
- `IrisClassifications.lua`/`IrisPrimarySubcategory` supported facade 제거
- Browser/Menu layout, sorting 또는 presentation behavior 변경
- Tooltip static Lua payload 생성, 4-line assembly 또는 `IrisAltTooltip` runtime 변경
- Layer 3, Layer 4, DVF, QG/locale, Iris presentation-contract correction
- taxonomy/Evidence Allowlist 확대
- `Base.LemonGrass`/`Base.Lemongrass` 병합
- external-mod classification policy 신설
- public translation 문구 재작성 또는 번역 품질 평가
- T2 handoff 생성, T2 static generation, T3 runtime adoption
- package publication, freeze, RTC, Publish, release, Workshop 또는 deployment 판단
- unrelated refactor와 build/validation architecture 재설계

---

## 3. Non-Goals

- coverage를 높이기 위해 새 classification meaning을 발명하지 않는다.
- FullType, display name, description, rendered label 또는 arbitrary raw tag를 해석해 owner gap을 채우지 않는다.
- frequency, utility, importance, representativeness, alphabetical/source/dictionary/Lua iteration order로 primary winner를 만들지 않는다.
- `Misc.9-A`를 unresolved row의 generic catch-all로 사용하지 않는다.
- locale availability에 따라 category/primary identity를 다시 선택하지 않는다.
- owner output이 존재한다는 이유만으로 Menu가 실제로 같은 identity를 소비한다고 self-attest하지 않는다.
- affected-range 검증을 whole-universe semantic-correctness 또는 full Menu parity claim으로 확대하지 않는다.
- current T1 formal-complete predecessor subject와 external receipts를 rewrite하지 않는다.

---

## 4. Assumptions

### Repository and authority assumptions

- authority order는 `Philosophy.md -> DECISIONS.md -> ARCHITECTURE.md -> ROADMAP.md -> current authority manifest/contracts`다.
- PZ runtime Iris는 계속 100% Lua이며 Python은 repository-side offline generation/validation에만 존재한다.
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`는 current runtime/source projection이지만 T1이 요구하는 resolved category/primary/surface/provenance row는 아니다.
- current Classification producer provenance가 census에서 충분히 복원되지 않으면 runtime table 존재만으로 resolved row를 발행하지 않는다.
- owner-authored resolution registry는 coverage filler가 아니라 exact row별 decision/provenance carrier다.
- current dirty working tree의 T1 files는 사용자 작업으로 보존한다. 구현은 clean exact subject를 새로 결속하기 전 어떤 machine PASS도 주장하지 않는다.

### Roadmap conflict dispositions

로드맵 §14.3의 충돌은 current code/authority를 기준으로 다음처럼 실행 판정한다.

| Conflict | Plan disposition | Basis |
| --- | --- | --- |
| A — denominator | fixed `2,280`이 아니라 exact subject마다 current owner-ratified `current-owner-fulltype-union-v1` predicate로 재도출한다. `2,280`은 predecessor/current baseline comparison 값이다. | current T1 decision contract, `audit.py` support union, `DECISIONS.md` Tooltip T1 readpoint |
| B — primary gap | explicit primary 또는 existing Classification-owner rule이 없는 row는 affected-row owner resolution을 요구한다. 새 global structural tie-break를 implementation 편의로 만들지 않는다. | 291 multi row 중 265 explicit-primary gap, `CategoryPresentationOrder.lua`의 presentation-only ownership |
| C — `Misc.9-A` | existing output-stage fallback 지위만으로 raw `Misc.9-A` occurrence를 resolved identity로 발행하지 않는다. 실제 approved evidence/override로 Misc meaning이 입증된 row만 별도 owner resolution이 가능하며 generic fill count는 0이어야 한다. | `DECISIONS.md` taxonomy boundary, T1 Layer 2 contract의 raw fallback prohibition |
| D — one-sided locale | supported KO/EN 중 한쪽이 없으면 semantic identity를 유지한 채 surface correction으로 처리한다. legitimate absence나 반대 locale fallback으로 바꾸지 않는다. 양쪽 key가 있어도 taxonomy와 뜻이 충돌하면 동일하게 owner surface correction이다. | current Layer 2-3 locale contract; 현재 59 separate key는 양 locale에 모두 존재하지만 EN `1-K/1-L` meaning은 sealed taxonomy와 충돌 |
| E — Menu convergence | D1은 canonical owner output 발행, current Menu route 관측과 no-regression까지만 포함한다. actual Menu migration과 consumer correction closure는 후속 Menu-owner scope다. | Classification/Menu correction separation과 current raw-tag Menu route |
| F — decision sealing | existing sealed authority는 그대로 projection하고, census가 실제로 드러낸 primary/absence/provenance gap만 bounded successor decision/registry로 봉인한다. 전체 decision family를 이유 없이 재봉인하지 않는다. | additive amendment/minimal-diff governance |
| G — T1 audit producer | current audit는 Layer 2 failure를 하드코딩하므로 owner output input wiring 변경을 허용한다. 다만 Classification validator, source/output cross-check, focused tests와 clean full gate를 별도 축으로 두어 changed T1 consumer가 유일한 PASS 발급자가 되지 않게 한다. | `contract.py` hard-coded route assertion과 `audit.py` unconditional S1 correction |

### Terminal assumptions

- D1 `complete`는 모든 support FullType이 `resolved` 또는 positive-proof `owner_approved_absence`일 때만 가능하다.
- unresolved primary, missing provenance 또는 unsupported fallback이 하나라도 남으면 결과는 `partial/blocked`다.
- Classification correction이 0이 되어도 other-owner correction은 자동 차감하지 않는다.
- actual output count는 execution subject에서 계산하며 계획에 숫자 상수로 내장하지 않는다.

---

## 5. Repository Areas Affected

아래 new path 이름은 implementation의 intended ownership을 고정한다. W0 current-route census에서 existing current naming contract와 충돌이 확인되면 같은 ownership을 보존하는 최소 경로 조정만 허용하고 closeout에 기록한다.

### Code

- `Iris/tooling/src/iris_tooling/domains/classification/cli.py`
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_contract.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_materializer.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_classification_layer2.py` (new)
- `Iris/tooling/tests/test_classification_candidate_install.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- conditional `Iris/tooling/src/iris_tooling/__main__.py` and `Iris/tooling/tests/test_cli.py` only if the existing classification target cannot preserve the new subcommand without top-level routing change

The following runtime files are read-only compatibility/consumer surfaces in D1:

- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`
- `Iris/media/lua/client/Iris/Logic/CategoryPresentationOrder.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserClassificationIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`
- `Iris/media/lua/shared/translate/en/Iris_en.txt`

### Docs

- this plan
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris_tooltip_t1_display_contract_policy.md`
- `Iris/build/ENTRYPOINTS.md`
- `Iris/_docs/authority/iris_authority_classification.md`
- `Iris/_docs/authority/classification_layer2/classification_layer2_resolution_contract.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_owner_output.schema.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_absence_reason_registry.json` (new)
- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`

### Config

- `Iris/_docs/authority/iris_current_authority_manifest.json`
- `Iris/_docs/authority/iris_current_route_index.json`
- conditional `Iris/validation/clean_checkout/contracts/full_repository_gate.json` if the new focused validator is adopted into recurring membership
- no Java/Gradle, JS/TS or runtime Lua configuration change

### Generated Artifacts

Tracked current owner inputs/output:

- `Iris/build/classification/data/classification_layer2_resolution_registry.json` (new owner-authored source)
- `Iris/build/classification/data/classification_layer2_surface_catalog.json` (new source-to-locale binding catalog)
- `Iris/build/classification/data/classification_layer2_owner_output.json` (new deterministic current projection)

Repository-external immutable lifecycle artifacts:

- `t1d1_subject_binding.json`
- `t1d1_denominator_register.json`
- `t1d1_classification_state_census.jsonl`
- `t1d1_multi_membership_census.jsonl`
- `t1d1_primary_authority_inventory.jsonl`
- `t1d1_identity_surface_authority_map.json`
- `t1d1_owner_decision_gap_report.json`
- `classification_layer2_candidate_manifest.json`
- `t1d1_whole_universe_classification_audit.jsonl`
- `t1d1_owner_output_invariant_report.json`
- `t1d1_supported_facade_no_regression_report.json`
- `t1d1_t1_reaudit_result.json`
- `t1d1_exact_subject_validation_receipt.json`
- `t1d1_closeout.json`

Lifecycle census/audit/receipt artifacts are not regular validation authority and no mutable `latest` pointer or cross-run state registry is created.

---

## 6. Planned Changes

### Change 1 — Bind the exact subject and census all denominators

Purpose:

Prevent baseline counts, stale artifacts or equal-sized correction classes from defining the execution universe.

Files:

- read-only current authority/route files
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)
- repository-external subject, denominator and membership reports

Implementation Notes:

- Record commit, tree, working-tree cleanliness, installed wheel/package identity and hashes of every semantic/surface input.
- Re-derive the T1 support set from the same case-sensitive owner union adopted by current T1, after owner decision adoption and before mutation.
- Register at least these distinct universes: T1 support, raw Layer 2 membership, Classification correction, Menu consumer correction, 9 category identities, 50 subcategory identities, 59 label keys, 50 combined classification template identities, Layer 3 and Layer 4 owner universes.
- Preserve exact UTF-8 FullType bytes. A lowercase/case-folded key may exist only in a collision report and must never index the output.
- Report actual row-derived counts separately from comments/header counts. The observed `Misc.9-A` 408/header 393 mismatch is a census finding, not a value to normalize away.
- Classify each pre-resolution row as `owner_resolved`, `fallback_derived` or `unclassified`; do not mutate any classification in this phase.

Validation:

```text
duplicate_exact_fulltype_count = 0
case_normalization_merge_count = 0
support_derivation_run_a == support_derivation_run_b
every denominator has owner, predicate, subject and count
Classification/Menu correction membership remains separate
```

---

### Change 2 — Establish the Classification resolution and provenance contract

Purpose:

Make membership, primary identity, authority/provenance and genuine absence explicit before materialization.

Files:

- `Iris/_docs/authority/classification_layer2/classification_layer2_resolution_contract.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_absence_reason_registry.json` (new)
- `Iris/build/classification/data/classification_layer2_resolution_registry.json` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_contract.py` (new)
- owner-decision gap reports

Implementation Notes:

- For single non-fallback membership, primary may equal the only membership only when the membership authority/provenance is valid.
- For multi-membership, accept only an explicit current primary, an existing Classification-owner rule with exact scope, or an affected-row owner decision. Presentation rank, description priority and source iteration do not qualify.
- Require `primary_subcategory_id` to be a member of the same row's exact membership set.
- Keep `classification_authority_ref` and `classification_provenance_ref` separate. A broad policy document cannot replace missing row provenance.
- Treat raw `Misc.9-A` fallback rows as `fallback_derived`. They require evidence-backed owner resolution to a real taxonomy identity or owner-approved absence; they cannot pass by preserving the fallback mechanically.
- Define a narrow absence enum for proven evidence exhaustion. Every absence row requires exact authority and provenance references and cannot carry category, primary or locale values.
- Missing category, ambiguous primary, missing authority/provenance, unsupported override, invalid fallback or producer failure remain corrections.
- Owner decision records include subject binding, exact FullType, prior state, selected terminal state, rationale, evidence refs, authority owner and approval identity.
- Do not regenerate the entire decision family in `DECISIONS.md`; only actual new owner policy is added as a successor readpoint after validation.

Validation:

```text
unapproved_manual_override_count = 0
unsupported_primary_ranking_count = 0
primary_not_in_membership_count = 0
unsupported_misc_fill_count = 0
absence_without_authority_count = 0
absence_without_provenance_count = 0
unresolved owner decision count = 0 for D1 complete
```

---

### Change 3 — Bind category/subcategory identities to separate KO/EN surface authority

Purpose:

Provide the exact public label surfaces T1 needs without parsing combined templates or changing semantic identity by locale.

Files:

- `Iris/build/classification/data/classification_layer2_surface_catalog.json` (new)
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua` (read-only source)
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt` (read-only source)
- `Iris/media/lua/shared/translate/en/Iris_en.txt` (read-only source)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)

Implementation Notes:

- Bind 9 category identities to `Iris_Cat_*` keys and 50 subcategory identities to `Iris_Sub_*` keys using current structured metadata.
- Record surface key, locale, exact text, source path/hash, surface authority and provenance.
- Treat `Iris_Sub_1K`/`Iris_Sub_1L` as an observed authority conflict: KO matches the sealed `Security`/`Storage` boundary, while current EN and Browser fallback carry `Storage Containers`/`Bags`. The Classification/locale owner must approve exact successor surfaces or leave the affected identities as correction; the materializer cannot choose wording.
- Preserve the distinction between separate category/subcategory labels and the existing 50 combined Layer 2 sentence/template identities.
- Do not split, regex-parse or reverse-map rendered strings.
- Select semantic category/primary before surface lookup. KO/EN readiness cannot influence primary selection.
- A missing KO or EN surface is a surface correction; do not use the other locale and do not convert it to classification absence.
- Existing fallback strings in `IrisBrowserCategoryIndex.lua` remain current Menu compatibility behavior but are not accepted as proof that a requested locale translation key exists.

Validation:

```text
invalid_category_surface_ref_count = 0
invalid_subcategory_surface_ref_count = 0
duplicate_locale_key_count = 0
surface_authority_contradiction_count = 0 for D1 complete
cross_locale_fallback_count = 0
locale_specific_identity_reselection_count = 0
rendered_string_reverse_parsing_count = 0
```

---

### Change 4 — Add the Classification-owned materializer, validator and hash-bound adoption route

Purpose:

Generate one deterministic canonical Layer 2 owner output without making `iris_tooling` the semantic owner.

Files:

- `Iris/tooling/src/iris_tooling/domains/classification/cli.py`
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_materializer.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- `Iris/tooling/tests/test_classification_layer2.py` (new)
- `Iris/tooling/tests/test_classification_candidate_install.py`
- `Iris/_docs/authority/classification_layer2/classification_layer2_owner_output.schema.json` (new)
- `Iris/build/classification/data/classification_layer2_owner_output.json` (new)
- `Iris/build/ENTRYPOINTS.md`

Implementation Notes:

- Extend the existing classification domain with a distinct `layer2-owner` artifact set while preserving the current three-file runtime-index candidate build/install route and its manifest contract.
- Build a repository-external candidate and manifest first. Install only the allowlisted owner-output target after independent validation and exact manifest hash verification.
- Stable output contains no timestamp, run ID, environment path or elapsed time. Volatile observations go in the external receipt envelope.
- Sort rows by exact FullType bytes and serialize canonical UTF-8 JSON with fixed field ordering and LF newlines.
- Resolved rows contain membership, `category_id`, `primary_subcategory_id`, two surface refs, four KO/EN label values, distinct authority/provenance refs and source subject binding.
- Absence rows contain only the terminal state, approved reason, authority/provenance refs and subject binding.
- Reject consumer-specific fields such as `tooltip_rank`, `menu_rank`, importance, frequency, external-mod status or audit verdict.
- Do not emit Menu consumer identity refs or parity claims.
- The validator independently reloads the resolution registry, taxonomy/surface catalog and output; it does not trust producer-provided counts or verdict fields.
- Candidate Run A/B in fresh external roots must be byte-identical before installation.

Validation:

```text
candidate_run_a_bytes == candidate_run_b_bytes
duplicate_exact_fulltype_count = 0
unresolved_count = 0 for complete candidate
invalid_taxonomy_identity_count = 0
primary_not_in_membership_count = 0
missing_authority_or_provenance_count = 0
self_issued_menu_consumer_evidence_count = 0
self_issued_audit_verdict_count = 0
consumer_specific_semantic_field_count = 0
source tree mutation during candidate build = 0
```

---

### Change 5 — Consume the owner output at the T1 Layer 2 boundary

Purpose:

Replace T1's unconditional Layer 2 correction with consumption of the accepted Classification owner output while keeping Menu correction independent.

Files:

- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `docs/iris_tooltip_t1_display_contract_policy.md`

Implementation Notes:

- Adopt the canonical output path/schema/hash as the current admissible Layer 2 owner route.
- Add the owner output hash to T1 input hashes and exact subject identity.
- For a resolved row, construct S1 only from owner-issued category/primary identity and KO/EN surfaces.
- For a positive-proof absence row, construct legitimate S1 absence without suppressing independent S2-S4 slots.
- Missing row, unresolved state, invalid primary, authority/provenance gap or surface defect remains Classification-owner correction.
- Remove the unconditional `CLASSIFICATION_RESOLVED_IDENTITY_MISSING` emission only after owner output validation succeeds.
- Continue to emit/retain the Menu consumer correction because D1 does not prove current Menu consumption. Owner output fields must not be compared with themselves to claim parity.
- Do not modify Layer 3/4 selection, current Tooltip runtime or T2 handoff schema.
- Do not rewrite the predecessor T1 candidate/finalizer receipts. Produce a new successor re-audit subject.

Validation:

```text
T1 support set == owner-output applicable set
resolved S1 identity/surfaces == owner output
absence S1 carries positive owner proof
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0 for D1 complete
Classification owner blocker count = 0 for D1 complete
Menu consumer correction is not auto-closed
T2 handoff count remains 0 while any blocker remains
```

---

### Change 6 — Audit the whole universe and observe downstream compatibility

Purpose:

Verify every exact row and distinguish Classification completion from Menu/runtime behavior claims.

Files:

- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- current T1 audit consumer
- Browser/Menu supported facade files as read-only comparison inputs
- repository-external whole-universe, correction and no-regression reports

Implementation Notes:

- Apply one decision matrix to every support FullType: exact row, terminal state, taxonomy validity, membership/primary relation, authority/provenance, locale surface refs, absence proof, no inference and no duplicate.
- Never patch the audit artifact. Correct the owner registry/source, regenerate and re-audit.
- Compare the current supported `IrisClassifications` table/global and `IrisPrimarySubcategory` facade shape/hash expectations without migrating them.
- Record the Menu path as `raw classifications -> presentation projection -> Browser` until a future Menu-owner scope changes it.
- Classify Menu parity as unresolved/correction as required by current T1 contract; do not turn route observation into evidence of convergence.
- If only an affected range is independently re-audited, cap the claim at that affected range. Whole-universe completion requires the full exact support set.
- Keep source/runtime hashes stable during census, build and audit.

Validation:

```text
resolved_count + owner_approved_absence_count == support_count
missing/unexpected/duplicate output row count = 0
case_normalization_merge_count = 0
raw_tag_semantic_inference_count = 0 at T1 consumer
fulltype_name_inference_count = 0
unsupported winner/fallback count = 0
supported facade incompatible count = 0
owner output self-comparison count = 0
```

---

### Change 7 — Run focused, lifecycle and repository validation

Purpose:

Bind implementation, independent validation and T1 re-audit to the same exact subject without self-certification.

Files:

- focused classification/T1 test files
- conditional current full-gate membership contract
- repository-external candidate, Run A/B, comparator and closeout receipts

Implementation Notes:

- Focused tests cover exact identity, registry/absence schema, primary gap behavior, `Misc.9-A`, locale binding, deterministic materialization, installer safety and T1 consumption.
- Negative fixtures must include: missing primary, primary outside membership, fallback promoted as resolved, missing provenance, one-sided locale, exact duplicate, case-normalized collision, consumer-specific field and owner-output self-attestation.
- Run the new Classification candidate twice in fresh repository-external roots and compare canonical bytes.
- Run T1 candidate on the new exact subject; confirm only Classification-owner correction is removed by this scope.
- Use the repository-owned receipt-bound full validation for terminal subject evidence. Do not duplicate its validation membership/verdict in a wrapper.
- Promote a new test into regular membership only if it protects a durable current product/validation contract, and record the exact membership delta/reason.
- Claim PASS only when every exact relevant command exits `0`.

Validation:

The planned focused command is:

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_classification_layer2.py `
  .\Iris\tooling\tests\test_classification_candidate_install.py `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py `
  -q
```

Read-only current membership inspection remains:

```powershell
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class current --list
```

Terminal full validation uses the literal owner in `Iris/build/ENTRYPOINTS.md`:

```powershell
iris-tooling --repository-root <repo> validate full `
  --commit <terminal-commit> `
  --claim-id <t1d1-claim-id> `
  --environment-receipt <external-environment-receipt> `
  --work-root <external-empty-work-root> `
  --result-root <external-empty-result-root> `
  --orchestration-receipt <external-new-orchestration-receipt>
```

No runtime Lua file is planned to change, so the Lua syntax command is not part of the default D1 validation set. If execution touches any Lua source despite this boundary, `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` becomes mandatory and the runtime-surface scope/risk must be reopened before claiming completion.

---

### Change 8 — Adopt the successor authority and close T1-D1

Purpose:

Make the validated owner output current without rewriting predecessor evidence or expanding the claim.

Files:

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `Iris/build/ENTRYPOINTS.md`
- `Iris/_docs/authority/iris_current_authority_manifest.json`
- `Iris/_docs/authority/iris_current_route_index.json`
- `Iris/_docs/authority/iris_authority_classification.md`
- external `t1d1_closeout.json`

Implementation Notes:

- Add an additive successor decision/readpoint only for policy actually introduced by the validated resolution contract.
- Record the canonical owner output path, schema/hash, producer, independent validator, exact subject and current consumer relation.
- Keep the predecessor T1 formal-complete snapshot and its `5,625` correction ledger as historical subject-bound evidence.
- Close `T1-D1` only if the new exact-subject T1 re-audit reports Classification blocker 0 and `CLASSIFICATION_RESOLVED_IDENTITY_MISSING` 0.
- Preserve DVF, Iris presentation-contract, Menu consumer and QG/locale correction classes exactly as re-audited; do not infer their counts from predecessor arithmetic.
- Keep `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS` and production handoff 0 while any other T2-blocking correction remains.
- If any Classification correction remains, close as `partial/blocked` with exact owner/reason distribution and no complete claim.
- Documentation-only successor updates cannot rebind or replace machine validation receipts.

Validation:

```text
current authority/route points to one Classification owner output
predecessor authority/evidence remains immutable
closeout subject == validated subject
Classification blocker count = 0 for complete
other-owner correction classes remain separate
T2 progression and handoff state match the re-audit
```

---

## 7. Validation Plan

### Automated Validation

#### Contract and source validation

- exact FullType byte round-trip and case-sensitive uniqueness
- taxonomy/category/subcategory identity validity
- membership and primary relation
- authority/provenance reference existence and subject binding
- allowed absence enum and positive owner proof
- `Misc.9-A` fallback non-promotion
- separate category/subcategory surface reference integrity
- KO/EN key uniqueness and exact requested-locale presence
- consumer-specific field and self-attestation rejection

#### Determinism and mutation isolation

- census Run A/B semantic equality
- owner-output candidate Run A/B byte equality
- stable exact-byte row ordering and canonical JSON serialization
- repository source/runtime hash equality before/after candidate runs
- external empty-root enforcement and hash-bound allowlisted install
- stale subject/input hash mismatch failure

#### T1 integration and regression

- resolved/absence S1 projection table
- no raw-tag/name/rendered-string inference in T1
- whole-universe support/output equality
- Classification blocker and reason-code accounting
- Menu correction independence and no self-comparison
- unchanged Layer 3/4 projection invariants
- blocked T2 progression and zero production handoff while other blockers remain
- supported `IrisClassifications`, `IrisPrimarySubcategory`, Browser/API facade no-regression report

#### Repository validation

- focused `uv run --project .\Iris\tooling ... pytest` command exits `0`
- Classification candidate Run A/B and comparator exit `0`
- T1 candidate re-audit exits `0`
- read-only current membership command exits `0`
- terminal receipt-bound full gate and required deterministic comparison exit `0`

Core unconditional zero metrics:

```text
duplicate_exact_fulltype_count
case_normalization_merge_count
invalid_category_id_count
invalid_subcategory_id_count
primary_not_in_membership_count
missing_classification_authority_count
missing_classification_provenance_count
surface_authority_contradiction_count
cross_locale_fallback_count
locale_specific_identity_reselection_count
rendered_string_reverse_parsing_count
raw_tag_semantic_inference_count
fulltype_name_inference_count
unsupported_primary_ranking_count
unsupported_misc_fill_count
self_issued_menu_consumer_evidence_count
self_issued_audit_verdict_count
consumer_specific_semantic_field_count
source_mutation_count
```

Claim-conditional metrics:

```text
unresolved_count = 0                         # T1-D1 complete claim
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0 # T1-D1 complete claim
Classification owner blocker count = 0      # T1-D1 complete claim
```

### Manual Validation

- Review every new owner decision family and a stratified sample of single, multi, explicit-primary, fallback-derived and owner-approved-absence rows against its cited authority/provenance.
- Verify `Base.LemonGrass` and `Base.Lemongrass` remain separate exact rows throughout census, output and T1 audit.
- Inspect the 9 category and 50 subcategory surface bindings in both locales without relying on Browser fallback strings; explicitly verify the owner disposition for `Iris_Sub_1K` and `Iris_Sub_1L`.
- Review current Menu dependency report and confirm it still names the raw membership/presentation path rather than claiming canonical-output convergence.
- Review closeout language against actual validation scope and correction distribution.
- No in-game/UI acceptance is required when the runtime no-mutation boundary is preserved.

### Validation Limits

- no semantic correctness proof for every individual item classification beyond the approved owner records and cited evidence
- no translation naturalness/quality review
- no actual Tooltip pixel fit, wrapping, four-line assembly or Alt-key behavior
- no Menu source migration or full Menu parity verification
- no Layer 3/4 readiness validation beyond regression/no-change checks
- no arbitrary external-mod compatibility sweep
- no multiplayer, long-session or performance validation
- no package publication, freeze, RTC, Publish, release, Workshop or deployment validation
- an affected-range-only re-audit cannot support a whole-universe completion claim

---

## 8. Risk Surface Touch

### Authority Surface

Touched. Classification membership/primary/surface/provenance relations become one explicit owner output. Semantics remain owned by Classification; `iris_tooling` only materializes and validates approved records.

### Runtime Behavior Surface

None by planned scope. Current Lua classification/Menu/Tooltip files are read-only. If implementation requires Lua mutation or actual Menu convergence, the plan must be amended before that work proceeds.

### Compatibility Surface

Touched at the offline Classification output and T1 input boundary. Existing Lua/API/Browser facades remain supported and must pass no-regression checks.

### Sealed Artifact Surface

Touched additively. New exact-subject candidate/output/receipts and successor readpoints are added; predecessor T1 evidence and current historical closeout are not rewritten.

### Public-Facing Output Surface

Touched at approved category/subcategory KO/EN identity binding only. No new wording, recommendation, ranking or runtime rendering is introduced.

---

## 9. Risk Analysis

### Architecture Risk

- The materializer may accidentally become a second classification authority by choosing primary or repairing provenance.
- A tracked owner output may be mistaken for Menu consumer evidence or a general consumer-specific database.
- Retired one-shot/history output may re-enter as current source because the current runtime table lacks row-level provenance.
- Updating T1 audit and Classification materializer together may create self-certification without an independent validator/gate.
- A new output may duplicate rather than converge current Classification ownership if source/producer/installer roles are not explicit.

### Runtime Risk

- Planned runtime risk is none, but changing `IrisClassifications`, `IrisPrimarySubcategory` or Browser projection would silently alter Menu grouping/primary behavior.
- Premature Menu migration could change search location, primary highlighting or compatibility behavior and incorrectly close Menu correction.

### Compatibility Risk

- Existing `classification` candidate CLI/manifest/install behavior could be broken by overloading its file set.
- Supported `IrisPrimarySubcategory` global and `IrisAPI.Tags` facade could drift even without intentional removal.
- Case-folded handling on Windows could merge exact identities.
- Label fallback behavior may be mistaken for locale authority and hide missing translation keys.
- Mere KO/EN key presence may be mistaken for semantic agreement despite the current `1-K/1-L` EN/fallback conflict.

### Regression Risk

- The 2,280 baseline may be hard-coded and silently drop a changed exact-subject member.
- 408 actual `Misc.9-A` rows may be trusted because the header claims a different fallback count.
- 265 observed multi-membership primary gaps may be filled with presentation/alphabetical order.
- Owner-approved absence may conceal missing provenance, ambiguous primary or producer failure.
- T1 Classification completion may be expanded into T2 OPEN, handoff generation, Menu parity or semantic correctness.
- Other-owner correction counts may be changed by arithmetic rather than new exact-subject re-audit.

---

## 10. Rollback Plan

Use additive candidate adoption rather than in-place authority rewrite.

```text
current predecessor route
        |
        +--> external Layer 2 candidate
                |
                +--> independent validation fails -> candidate remains non-current
                |
                +--> validation passes -> hash-bound tracked install + successor T1 route
```

- Build/census failure leaves current `no_admissible_authority_relation`, T1 Classification corrections and blocked T2 progression unchanged.
- Owner gap failure does not reduce the denominator, create a fallback or patch the audit artifact.
- Candidate/install failure retains the existing classification CLI runtime-index route and does not partially install files.
- T1 integration failure reverts only the unadopted successor contract/consumer wiring; predecessor T1 contract/evidence remains intact.
- Validation evidence for a failed attempt is preserved as failed lifecycle evidence and never overwritten as PASS.
- A validated tracked adoption can be reverted as one bounded successor change: remove the current-route reference to the new output and restore the predecessor T1 input disposition while keeping the failed/superseded evidence trace.
- No destructive reset, broad delete or restoration of stale `docs/Iris/**`/retired producer trees is part of rollback.

Immediate stop conditions:

```text
taxonomy or Evidence Allowlist expansion required
exact FullType loss or merge
unresolved/heuristic primary required
raw Misc fallback required for completion
authority/provenance cannot be established
cross-locale fallback required
supported facade break required
canonical output is nondeterministic
T1 re-audit retains Classification correction
implementation would close Menu correction by self-attestation
runtime Lua mutation is required without plan amendment
```

---

## 11. Governance Constraints

- Preserve `docs/Philosophy.md`: evidence-based information, neutrality, silence when evidence is insufficient, Menu/Tooltip same-facts principle, and 100% Lua PZ runtime.
- Preserve Hub & Spoke boundaries. Iris introduces no dependency on Echo, Fuse, Nerve, Frame, Cortex or Canvas; Pulse gains no Iris dependency.
- Classification/Rule remains the Layer 2 semantic writer; T1 remains a projection/readiness consumer.
- Taxonomy and Evidence Allowlist do not expand for coverage.
- `primary_subcategory` remains a navigation anchor and is not promoted to Layer 3 fact authority or recommendation/ranking.
- Exact case-sensitive FullType bytes are authoritative; normalization is diagnostic only.
- Locale binding follows identity selection. No cross-locale fallback, locale reselection or rendered-string reverse parsing.
- `Misc.9-A` output-stage fallback is not a generic resolved classification rule.
- Owner-approved absence requires positive authority/provenance and cannot conceal a defect.
- Classification owner output cannot issue Menu consumer evidence, audit verdict or T2 progression verdict.
- Current Menu correction remains independent until Menu-owner evidence/migration is separately authorized and validated.
- Offline Python tooling never becomes PZ runtime logic.
- Existing supported facade and current runtime source remain unchanged in this D1 scope.
- Current/historical/reproduction roles from the authority manifest are preserved. Retired source-root/one-shot scripts are not re-adopted by convenience.
- Audit/census/run receipts are written only to repository-external immutable roots; no mutable latest pointer or stateful registry is introduced.
- Predecessor T1 formal-complete subject and evidence remain immutable.
- Documentation adoption is additive and subject-bound; docs-only edits do not replace machine receipts.
- Existing user changes in the dirty worktree are preserved and unrelated files are not modified.
- Claim PASS only when the exact relevant required command exits `0`; missing tooling is BLOCKED.

---

## 12. Expected Closeout State

Expected target: `complete`, guarded by owner resolution and exact-subject validation.

`complete` means only:

```text
T1-D1 Layer 2 Classification authority completion = complete
Classification owner blocker count = 0
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0
canonical Layer 2 owner output adopted
```

It does not mean semantic correctness of every classification was independently proven, Menu correction was closed, T2 opened, a production handoff was generated, Tooltip runtime was implemented, or release readiness was established.

Expected post-closeout progression while other owner blockers remain:

```text
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production T2 handoff = 0
```

If any exact support row lacks a valid terminal state, primary, authority/provenance or required locale surface, expected closeout becomes `partial/blocked`. The closeout must enumerate the remaining Classification owner/reason distribution and may not claim D1 complete.
