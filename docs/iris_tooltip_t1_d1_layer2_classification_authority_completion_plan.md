# Iris Tooltip T1-D1 Layer 2 Classification Authority Completion Implementation Plan

> 상태: planned / synchronized for parallel execution / implementation not started / owner-resolution gates required
> 작성일: 2026-08-28
> 기준 로드맵: `ROADMAP — Iris Tooltip T1-D1: Layer 2 Classification Authority Completion`
> 검증 깊이: heavy — authority, provenance, determinism, whole-universe completeness, KO/EN surface binding, T1 re-audit
> 실행 predecessor: Tooltip T1-C final commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
> 병렬 실행 계약: `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`

이 계획은 Tooltip이나 Menu가 직접 classification을 추론하게 만드는 계획이 아니다. Classification owner가 이미 소유하거나 명시적으로 승인한 membership, primary navigation identity, locale surface, authority와 provenance를 하나의 semantic registry에 결속하고 T1-facing canonical JSON 및 T1-D2/T1-D6가 소비할 immutable correction bundle을 생성한다. Menu consumer relation, Menu-facing Lua 전환과 global current adoption은 이 계획에서 수행하지 않는다.

현재 코드 조사에서 확인한 출발점은 다음과 같다. 아래 수치는 조사 시점 관측값이며 exact-subject terminal invariant가 아니다.

| Surface | Current observation | Planning consequence |
| --- | --- | --- |
| T1 support owner | `tooltip_t1_decision_contract.json`과 `audit.py`가 Layer 2/3/4 current owner FullType의 case-sensitive 합집합을 support predicate로 사용한다. 현재 correction baseline은 `2,280`이다. | `2,280`을 영구 고정하지 않고 실행 exact subject에서 같은 owner-ratified predicate로 재도출한다. |
| Layer 2 runtime projection | `IrisClassifications.lua`에는 2,079 exact row, 50 distinct tag, 291 multi-membership row와 27개 `IrisPrimarySubcategory` override가 있다. | current table은 D1의 read-only census baseline이다. D1은 canonical JSON bundle만 만들고 Lua/Menu 전환은 D2/D6에 남긴다. |
| Primary gap | 291개 multi-membership 중 26개만 explicit override와 교차하고 265개에는 explicit `IrisPrimarySubcategory`가 없다. 27번째 override인 `Base.Bleach`는 single-membership row다. `IrisBrowserProjectionBuilder.lua`는 나머지를 presentation rank/description priority로 계산한다. | `291 - 27` 산술로 gap을 추정하지 않는다. presentation order를 semantic primary authority로 승격하지 않고 exact set relation과 owner resolution을 사용한다. |
| `Misc.9-A` | actual table에는 `Misc.9-A` membership row가 408개 있으나 파일 header는 fallback 393개라고 기록한다. Current decision은 `Misc.9-A`를 일반 rule이 아닌 output-stage fallback으로 봉인했다. | header count를 authority로 사용하지 않고 actual row census를 기록한다. raw fallback row를 resolved identity로 승격하지 않는다. |
| Support/membership join | current owner union support는 2,280행이고 raw Layer 2 membership은 2,079행이며, 조사 subject에서 membership record가 없는 support row는 201개다. | census spine은 `support universe LEFT JOIN Layer 2 membership`이다. `no_membership_record`를 `unclassified`와 분리해 owner adjudication 전에 전부 열거한다. |
| Exact identity | exact duplicate FullType은 관측되지 않았고 `Base.LemonGrass`/`Base.Lemongrass` 한 normalized-collision pair가 존재한다. | exact bytes를 보존하고 normalization은 collision report에만 사용한다. |
| Locale labels | `IrisBrowserCategoryIndex.lua`에는 9개 category key와 50개 subcategory key가 있고 KO/EN translation source 모두 59개 key를 각각 한 번 제공한다. 다만 sealed taxonomy와 current EN/Browser fallback의 `1-K/1-L` wording은 서로 다른 의미를 나타낼 가능성이 있다. | 이를 surface defect로 미리 확정하지 않는다. `1-K/1-L/6-F` membership과 surface를 함께 census하고 owner-approved surface를 D1 registry에 결속하되 runtime source는 수정하지 않는다. |
| Menu Layer 2 route | `IrisBrowserProjectionBuilder.lua`가 `StaticData.get("classifications")`의 raw membership을 읽고 presentation order와 override를 적용한다. `IrisBrowserVariantIndex.lua`도 `IrisPrimarySubcategory` compatibility global을 소비한다. | D1은 current route를 관찰·보호하고 D2가 소비할 Classification relation을 발행한다. Menu source 전환은 D2/D6 범위다. |
| T1 Layer 2 route | `layer2_tooltip_input_contract.json`은 `current_route=no_admissible_authority_relation`이고 `audit.py`는 모든 support row에 `CLASSIFICATION_RESOLVED_IDENTITY_MISSING`을 무조건 발행한다. | canonical owner output 채택 후 contract와 audit input wiring을 함께 갱신해야 한다. 기존 audit code를 전혀 바꾸지 않는 방식으로는 D1을 닫을 수 없다. |
| Current producer boundary | installed `iris_tooling`과 `Iris/build/ENTRYPOINTS.md`가 current offline command owner다. Existing `classification` domain은 세 runtime index candidate만 생성·설치하며 Layer 2 owner output은 아직 만들지 않는다. | 새 materializer/validator는 installed classification domain에 추가하고 retired one-shot/source-root script를 current producer로 복원하지 않는다. |

실행 시점에는 clean exact commit/tree, installed wheel identity, current authority/route, T1 support predicate input, classification source, locale source와 T1 contract bundle을 다시 hash-bind한다. 위 dirty-worktree 관측값을 그대로 terminal evidence로 재사용하지 않는다.

---

## 0. Parallel execution synchronization amendment

이 계획은 `iris_tooltip_t1_parallel_workstream_execution_contract.md`를 따른다. 아래의 과거 `converged/deferred` Menu 분기, Menu/runtime/public mutation, global current manifest/route/environment locator 채택, workstream별 canonical full-gate Run A/B/finalizer와 신규 전용 test-file 요구는 실행 범위에서 폐기된다. 동일 내용을 담은 후속 절보다 이 절과 공통 계약이 우선한다.

T1-D1은 T1-D3, T1-D4, T1-D5와 공통 predecessor에서 병렬 실행한다. D1의 terminal output은 Classification owner correction bundle이며 T1-D2가 이를 소비한다. T1-D6가 shared T1 delta와 global current authority를 최종 통합한다.

```text
T1-D1 owner registry/materializer/validator
-> isolated candidate T1 integration delta
-> immutable D1 correction bundle
-> T1-D2
-> T1-D6 global integration
```

D1은 다음 파일을 current로 갱신하지 않는다.

```text
Iris/_docs/authority/iris_current_authority_manifest.json
Iris/_docs/authority/iris_current_route_index.json
Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json
Iris/build/ENTRYPOINTS.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

공통 Tooltip T1 code/contracts/tests에 필요한 변경은 isolated candidate의 `shared_path_delta`로 bundle에 기록하고 current adoption은 주장하지 않는다.

테스트 예산은 기본적으로 새 파일 `0`, 새 top-level test function/family `0`이다. 기존 `test_classification_candidate_install.py`와 Tooltip T1 contract/projection/audit parameter table에 case를 추가한다. 기존 family로 필수 code path를 정직하게 실행할 수 없을 때만 기존 파일 안의 parameterized function 최대 1개 예외를 허용하고 사유를 bundle에 기록한다.

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
-> pre-mutation support freeze
-> support universe LEFT JOIN membership/primary/surface/provenance census
-> bounded owner resolution registry
-> single Classification semantic source
-> Classification-owned deterministic materializer
        +-> canonical Layer 2 owner output -> T1
        +-> D2 handoff relation
-> independent Classification validation
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
- pre-mutation support set freeze와 `support universe LEFT JOIN Layer 2 membership` census spine
- `IrisClassifications.lua` membership, `IrisPrimarySubcategory`, fallback, provenance 상태의 census
- category/subcategory taxonomy와 existing separate KO/EN label key/surface census
- `owner_resolved / fallback_derived / unclassified / no_membership_record` pre-resolution 상태 구분
- single/multi membership과 primary authority source 분리
- `1-K / 1-L / 6-F` actual membership/surface composition과 defect-layer owner adjudication
- 실제 authority gap에 한정한 owner resolution/absence registry
- Classification-owned semantic registry, canonical Layer 2 JSON, validator와 hash-bound candidate/install route
- exact FullType, authority, provenance와 locale surface의 deterministic serialization
- owner가 승인한 KO/EN surface를 current runtime translation source에 설치하지 않고 D1 owner registry/candidate에 결속
- T1-D2가 소비할 exact Classification identity/surface/authority relation bundle
- Menu/runtime/public path의 protected hash와 D1-induced mutation `0` 증명
- T1 Layer 2 input contract와 audit consumer wiring의 successor update
- whole-universe Classification audit와 owner-source correction/regeneration loop
- protected Menu route no-mutation과 D2 handoff relation 확인
- 기존 parameterized family를 사용한 focused validation, candidate Run A/B byte comparison과 immutable bundle validation
- D6 integration proposal과 shared-path delta manifest
- T1-D1 workstream 상태와 current ecosystem adoption을 분리한 closeout

### Explicitly Out Of Scope

- Menu consumer correction closure 또는 independent Menu identity evidence 생성
- full Menu parity verification, Menu UI/layout redesign 또는 independent consumer evidence 생성
- `IrisClassifications.lua`/`IrisPrimarySubcategory` supported facade 제거나 incompatible shape change
- Browser/Menu layout, sorting, primary-source 또는 general presentation behavior 변경
- Tooltip static Lua payload 생성, 4-line assembly 또는 `IrisAltTooltip` runtime 변경
- Layer 3, Layer 4, DVF, QG/locale, Iris presentation-contract correction
- taxonomy/Evidence Allowlist 확대
- `Base.LemonGrass`/`Base.Lemongrass` 병합
- external-mod classification policy 신설
- general translation rewrite 또는 번역 품질 평가; owner-adjudicated exact D1 identity correction만 예외적으로 포함
- T2 handoff 생성, T2 static generation, T3 runtime adoption
- Menu consumer relation, Menu-facing Lua projection, Browser primary-source substitution 또는 D1 내부 Menu convergence
- global current authority manifest/route/environment locator와 governance status adoption
- ecosystem canonical Run A/B/comparator/finalizer; 이는 T1-D6가 통합 subject에서 수행
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
- `menu_consumer_evidence_unverified`는 existing Menu correction에 붙는 descriptive annotation일 뿐 lifecycle state, governance enum, readiness token 또는 semantic owner-output validity 판정으로 승격하지 않는다.
- Canonical owner output 존재만으로 current Menu가 같은 semantic source를 소비한다고 주장하지 않는다.
- D1의 no-Menu-mutation 경계를 Menu/Tooltip divergence의 장기 승인으로 해석하지 않는다. D2가 consumer relation을 별도로 해결한다.
- `1-K/1-L` 관측만으로 surface가 틀렸다고 선결정하지 않는다. `1-K/1-L/6-F` membership과 surface를 owner가 함께 판정한다.
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

첨부된 originating roadmap의 §14.3 충돌과 후속 종합 검토안의 판정 필요 항목은 current code/authority를 기준으로 다음처럼 실행 판정한다. 이 참조는 repository `docs/ROADMAP.md`의 section number를 뜻하지 않는다.

| Conflict | Plan disposition | Basis |
| --- | --- | --- |
| A — denominator | fixed `2,280`이 아니라 exact subject마다 current owner-ratified `current-owner-fulltype-union-v1` predicate로 재도출한다. `2,280`은 predecessor/current baseline comparison 값이다. | current T1 decision contract, `audit.py` support union, `DECISIONS.md` Tooltip T1 readpoint |
| B — primary gap | explicit primary 또는 existing Classification-owner rule이 없는 row는 affected-row owner resolution을 요구한다. 새 global structural tie-break를 implementation 편의로 만들지 않는다. | 291 multi row 중 265 explicit-primary gap, `CategoryPresentationOrder.lua`의 presentation-only ownership |
| C — `Misc.9-A` | existing output-stage fallback 지위만으로 raw `Misc.9-A` occurrence를 resolved identity로 발행하지 않는다. 실제 approved evidence/override로 Misc meaning이 입증된 row만 별도 owner resolution이 가능하며 generic fill count는 0이어야 한다. | `DECISIONS.md` taxonomy boundary, T1 Layer 2 contract의 raw fallback prohibition |
| D — locale/identity conflict | supported KO/EN 중 한쪽이 없으면 identity를 유지한 surface correction이다. `1-K/1-L` 의미 충돌은 `1-K/1-L/6-F` membership과 surface를 owner가 조사해 `surface / membership / both`를 판정한다. D1은 approved registry/candidate만 만들고 runtime locale/fallback source를 수정하지 않는다. | current Layer 2-3 locale contract, sealed taxonomy, actual membership/surface census requirement |
| E — Menu convergence | D1 범위에서 제거한다. D1은 exact Classification relation을 D2 bundle input으로 발행하고 Menu/runtime/public paths를 보호한다. D2가 consumer relation을 해결하며 D6가 integrated adoption을 수행한다. | common parallel-workstream contract and D1→D2 dependency |
| F — decision sealing | existing sealed authority는 그대로 projection하고, census가 실제로 드러낸 primary/absence/provenance gap만 bounded successor decision/registry로 봉인한다. 전체 decision family를 이유 없이 재봉인하지 않는다. | additive amendment/minimal-diff governance |
| G — T1 audit producer | current audit는 Layer 2 failure를 하드코딩하므로 isolated shared-path delta를 허용한다. Classification validator, source/output cross-check와 focused candidate tests를 별도 축으로 두며 global current adoption/full gate는 D6가 수행한다. | `contract.py` hard-coded route assertion과 `audit.py` unconditional S1 correction |
| H — qualified independent review | D1 `complete` 또는 final adoption의 unconditional prerequisite로 두지 않는다. Applicable exact-subject authority가 independent review를 요구할 때만 machine validation/owner seal과 분리된 review axis로 결속하며, 계획이 non-coauthor 자격 요건을 새로 만들지 않는다. | `DECISIONS.md`는 axis separation만 요구하고 universal mandatory review를 규정하지 않음; `current_route_required_validations.json`은 `no_independent_review_pass`를 non-claim으로 명시; originating roadmap/T1 contract에 non-coauthor mandatory gate 없음 |

### Terminal assumptions

- D1 `complete`는 모든 support FullType이 `resolved` 또는 positive-proof `owner_approved_absence`일 때만 가능하다.
- task state는 `complete`, `partial`, `blocked` 중 정확히 하나만 사용하고 `blocking_reason`을 별도 필드로 기록한다. 일부 결과를 보존했으나 owner gap이 남으면 `partial`, 실행 자체가 필수 선행조건에서 진행할 수 없으면 `blocked`다.
- unresolved primary, missing provenance, unsupported fallback 또는 unresolved defect-layer adjudication이 하나라도 남으면 `complete`가 아니다.
- Classification correction이 0이 되어도 other-owner correction은 자동 차감하지 않는다.
- actual output count는 execution subject에서 계산하며 계획에 숫자 상수로 내장하지 않는다.
- Machine validation, independent review와 owner seal은 서로 대체하지 않는 별도 axis다. 다만 current authority에는 originating-roadmap non-coauthor review를 모든 D1 completion/adoption의 mandatory gate로 만드는 근거가 없으므로 이 계획은 이를 새 필수조건으로 만들지 않는다. Applicable exact-subject authority가 independent review를 요구할 때만 별도 review axis로 결속한다.

---

## 5. Repository Areas Affected

아래 new path 이름은 implementation의 intended ownership을 고정한다. 여기서 `W0`는 이 계획의 Change 1에서 수행하는 pre-mutation exact-subject/current-route census를 뜻하며, historical repository-lightweighting W0를 뜻하지 않는다. Change 1 census에서 existing current naming contract와 충돌이 확인되면 같은 ownership을 보존하는 최소 경로 조정만 허용하고 closeout에 기록한다.

### Code

- `Iris/tooling/src/iris_tooling/domains/classification/cli.py`
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_contract.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_materializer.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_classification_candidate_install.py` — 기존 parameterized family/fixture 확장
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`, Browser projection과 KO/EN runtime translation source는 read-only protected paths
- conditional `Iris/tooling/src/iris_tooling/__main__.py` and `Iris/tooling/tests/test_cli.py` only if the existing classification target cannot preserve the new subcommand without top-level routing change

The following files are read-only comparison/regression targets in D1:

- `Iris/media/lua/client/Iris/Logic/CategoryPresentationOrder.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserClassificationIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua` (protected read-only comparison target)
- `Iris/tooling/tests/test_tooltip_t1_projection.py` (unchanged regression target; not a planned edit)

### Docs

- this plan
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` — read-only D6 integration inputs; D1은 successor proposal만 bundle에 기록
- `docs/iris_tooltip_t1_display_contract_policy.md`
- `Iris/build/ENTRYPOINTS.md` — read-only command-owner input; current update는 D6 소유
- `Iris/_docs/authority/iris_authority_classification.md`
- `Iris/_docs/authority/classification_layer2/classification_layer2_resolution_contract.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_owner_output.schema.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_absence_reason_registry.json` (new)
- `Iris/_docs/authority/classification_layer2/classification_layer2_menu_convergence_disposition.json` (new owner scope decision)
- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`

### Config

- `Iris/_docs/authority/iris_current_authority_manifest.json` — read-only D6 integration input
- `Iris/_docs/authority/iris_current_route_index.json` — read-only D6 integration input
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json` — unchanged; integrated membership 판단은 D6 소유
- no Java/Gradle, JS/TS or runtime Lua configuration change; Lua **source** mutation is limited to the conditional §5 Code entries above and occurs only when the selected disposition authorizes that branch

### Generated Artifacts

Tracked current owner inputs/output:

- `Iris/build/classification/data/classification_layer2_resolution_registry.json` (new owner-authored source)
- `Iris/build/classification/data/classification_layer2_surface_catalog.json` (new source-to-locale binding catalog)
- `Iris/build/classification/data/classification_layer2_owner_output.json` (new deterministic current projection)
- `d1_shared_path_delta.json` — T1-D2/D6가 검토할 isolated candidate integration proposal
- `d1_parallel_integration_manifest.json` — common bundle envelope와 protected-path hashes

Repository-external immutable lifecycle artifacts:

- `t1d1_subject_binding.json`
- `t1d1_menu_convergence_scope_disposition.json`
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

### Change 0 — Bind the common parallel-workstream contract before mutation

Purpose:

Bind D1 to the validated T1-C predecessor, common support freeze, D1-exclusive semantic ownership, shared-path proposal boundary and D6-exclusive current adoption boundary.

Files:

- `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`
- repository-external `t1d1_parallel_subject_binding.json`
- repository-external `t1d1_protected_path_baseline.json`

Implementation Notes:

- Verify direct ancestry from T1-C final subject or produce the exact path/blob equivalence manifest required by the common contract.
- Freeze the case-sensitive support set and compare its canonical hash with the other workstream-compatible baseline.
- Freeze Menu/runtime/public, current manifest/route/environment locator and governance docs as protected paths.
- D1 always produces a non-current Classification correction bundle. There is no `converged/deferred` implementation branch in D1.
- Menu consumer evidence, Menu projection and current convergence are T1-D2 responsibilities.
- Any shared Tooltip T1 code/contract delta is recorded in `shared_path_delta`; D1 does not claim current adoption.

Validation:

```text
predecessor inclusion/equivalence valid = true
frozen support predicate = current-owner-fulltype-union-v1
protected current/global path mutation count = 0
Menu/runtime/public mutation count = 0
Menu consumer correction auto-closure count = 0
shared path delta fully enumerated = true
```

---

### Change 1 — Bind the exact subject and census all denominators

Purpose:

Prevent baseline counts, stale artifacts or equal-sized correction classes from defining the execution universe.

Files:

- read-only current authority/route files
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)
- repository-external subject, denominator and membership reports

Implementation Notes:

- Record commit, tree, working-tree cleanliness, installed wheel/package identity and hashes of every semantic/surface input.
- Re-derive the T1 support set from the same case-sensitive owner union adopted by current T1 and freeze its exact FullType list/hash before any D1 mutation.
- Use `support universe LEFT JOIN Layer 2 membership` as the census spine. The owner adjudication loop iterates support rows, not only `IrisClassifications.lua` rows.
- Give every support row exactly one pre-resolution state: `owner_resolved`, `fallback_derived`, `unclassified` or `no_membership_record`. `no_membership_record` means the left join found no Layer 2 row and is not synonymous with an explicit unclassified record.
- Register at least these distinct universes: T1 support, raw Layer 2 membership, Classification correction, Menu consumer correction, 9 category identities, 50 subcategory identities, 59 label keys, 50 combined classification template identities, Layer 3 and Layer 4 owner universes.
- Preserve exact UTF-8 FullType bytes. A lowercase/case-folded key may exist only in a collision report and must never index the output.
- Report actual row-derived counts separately from comments/header counts. The observed `Misc.9-A` 408/header 393 mismatch is a census finding, not a value to normalize away.
- Record the observed 201-row `no_membership_record` cohort for the inspected baseline, but recompute it at execution rather than treating 201 as a fixed invariant.
- D1 mutation may not drop, exclude or normalization-merge a frozen support row. An external owner-authorized support predicate change requires an explicit rebase to a new exact subject and a new pre-mutation freeze.
- Any separately authorized prerequisite correction that changes a hashed semantic/surface input requires a new D1 exact subject, fresh support freeze and new candidate/audit receipts.
- Record the exact set relation `multi=291`, `override=27`, `multi∩override=26`, `multi-without-override=265`, `single∩override=1 (Base.Bleach)` so gap counts are not inferred by invalid subtraction.

Validation:

```text
duplicate_exact_fulltype_count = 0
case_normalization_merge_count = 0
support_derivation_run_a == support_derivation_run_b
support_universe_rows_enumerated == support_count
support_rows_without_layer2_membership_record = observed exact cohort count
pre_mutation_support_hash == post_mutation_audit_support_hash
frozen_support_row_drop_count = 0
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
- Do not modify `DECISIONS.md` in D1. Any actual new owner-policy readpoint is recorded as a D6 integration proposal in the immutable bundle.

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

### Change 3 — Adjudicate identity/surface conflicts and bind exact KO/EN authority

Purpose:

Determine whether the observed `1-K/1-L/6-F` conflict belongs to membership, surface or both, then provide exact public label surfaces without parsing combined templates or creating dual authority.

Files:

- `Iris/build/classification/data/classification_layer2_surface_catalog.json` (new)
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua` (census input; exact fallback correction only when owner-approved and runtime/public mutation is authorized)
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt` (census input; exact locale correction only when owner-approved and runtime/public mutation is authorized)
- `Iris/media/lua/shared/translate/en/Iris_en.txt` (census input; exact locale correction only when owner-approved and runtime/public mutation is authorized)
- `Iris/build/classification/data/classification_layer2_resolution_registry.json` (membership correction when owner-approved)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_census.py` (new)

Implementation Notes:

- Bind 9 category identities to `Iris_Cat_*` keys and 50 subcategory identities to `Iris_Sub_*` keys using current structured metadata.
- Record surface key, locale, exact text, source path/hash, surface authority and provenance.
- Census the exact membership composition of `Tool.1-K`, `Tool.1-L` and `Wearable.6-F` before assigning a defect layer. The inspected baseline has 9, 46 and 26 membership rows respectively; these counts are observations, not policy.
- Present the membership sets, KO/EN values, Browser fallbacks, sealed taxonomy refs and provenance to the Classification/locale owner. The owner records exactly one disposition: `surface_defect`, `membership_defect`, `both`, or `no_defect_with_authority_explanation`.
- If `surface_defect` is selected, bind the approved exact KO/EN surface in the D1 owner registry/candidate and record any runtime-source adoption proposal in the D6 integration manifest. D1 does not mutate translation or Browser fallback files.
- If `membership_defect` is selected, keep affected rows as correction until the owner resolution registry and canonical D1 JSON candidate are corrected. Do not fix membership by changing wording.
- If `both` is selected, require both owner-registry corrections before the D1 bundle can be complete. Current runtime/public adoption remains D6/D2 work.
- If `no_defect_with_authority_explanation` is selected, the decision must state whether the sealed taxonomy wording remains governing and explain why the current EN/fallback wording is not contradictory. If the explanation changes the sealed meaning, add an explicit additive superseding owner decision before materialization; an unexplained or implicitly superseded sealed decision keeps D1 incomplete.
- The surface catalog stores identity-to-key/authority bindings and reads exact public values from the current locale source. It does not become a competing string authority while Menu translations remain stale.
- Preserve the distinction between separate category/subcategory labels and the existing 50 combined Layer 2 sentence/template identities.
- Do not split, regex-parse or reverse-map rendered strings.
- Select semantic category/primary before surface lookup. KO/EN readiness cannot influence primary selection.
- A missing KO or EN surface is a surface correction; do not use the other locale and do not convert it to classification absence.
- Browser fallback strings are not accepted as proof that a requested locale translation key exists. D1 records the approved owner surface and the observed runtime-source divergence without modifying the Browser fallback.

Validation:

```text
invalid_category_surface_ref_count = 0
invalid_subcategory_surface_ref_count = 0
duplicate_locale_key_count = 0
unadjudicated_identity_surface_conflict_count = 0 for D1 complete
unexplained_no_defect_disposition_count = 0
implicit_sealed_decision_supersession_count = 0
surface_authority_contradiction_count = 0 when owner disposition includes surface defect
affected_membership_correction_count = 0 when owner disposition includes membership defect
cross_locale_fallback_count = 0
locale_specific_identity_reselection_count = 0
rendered_string_reverse_parsing_count = 0
```

`surface_authority_contradiction_count = 0` proves only surface convergence. It is never used as proof that affected membership semantics are correct.

---

### Change 4 — Add the Classification-owned materializer, validator and hash-bound adoption route

Purpose:

Generate one deterministic canonical Layer 2 owner output without making `iris_tooling` the semantic owner.

Files:

- `Iris/tooling/src/iris_tooling/domains/classification/cli.py`
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_materializer.py` (new)
- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- `Iris/tooling/tests/test_classification_candidate_install.py`
- `Iris/_docs/authority/classification_layer2/classification_layer2_owner_output.schema.json` (new)
- `Iris/build/classification/data/classification_layer2_owner_output.json` (new)
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua` (read-only protected comparison input)

Implementation Notes:

- Extend the existing classification domain with a distinct `layer2-owner` artifact set while preserving the current three-file runtime-index candidate build/install route and its manifest contract.
- Treat the owner resolution registry as the single semantic source and materialize `classification_layer2_owner_output.json`. Menu-facing Lua projection은 D1에서 생성·설치하지 않는다.
- Build a repository-external candidate and manifest first. Install only the allowlisted Layer 2 artifact-set targets after independent validation and exact manifest hash verification.
- Candidate install은 repository-external D1 owner output과 isolated T1 integration delta에 한정하며 Lua/runtime/public paths를 변경하지 않는다.
- Stable output contains no timestamp, run ID, environment path or elapsed time. Volatile observations go in the external receipt envelope.
- Sort rows by exact FullType bytes and serialize canonical UTF-8 JSON with fixed field ordering and LF newlines.
- Resolved rows contain membership, `category_id`, `primary_subcategory_id`, two surface refs, four KO/EN label values, distinct authority/provenance refs and source subject binding.
- Absence rows contain only the terminal state, approved reason, authority/provenance refs and subject binding.
- Reject consumer-specific fields such as `tooltip_rank`, `menu_rank`, importance, frequency, external-mod status or audit verdict.
- Do not emit Menu consumer identity refs or parity claims.
- Current raw membership table and `IrisPrimarySubcategory` compatibility global은 protected comparison input으로만 사용한다.
- Define `lua_projectable_resolved_count` as the number of canonical owner-output rows whose terminal state is `resolved` and which therefore carry a non-empty membership set plus valid primary. `owner_approved_absence` rows are excluded from this denominator and must not appear in the Lua membership projection.
- The stale `Misc.9-A` header comment is recorded as a non-authoritative source observation and is not used for census counts or modified by D1.
- The validator independently reloads the resolution registry, taxonomy/surface catalog and output; it does not trust producer-provided counts or verdict fields.
- Candidate Run A/B in fresh external roots must be byte-identical before installation.

Validation:

```text
candidate_run_a_bytes == candidate_run_b_bytes
runtime/public mutation count = 0
duplicate_exact_fulltype_count = 0
unresolved_count = 0 for complete candidate
invalid_taxonomy_identity_count = 0
primary_not_in_membership_count = 0
missing_authority_or_provenance_count = 0
self_issued_menu_consumer_evidence_count = 0
self_issued_audit_verdict_count = 0
consumer_specific_semantic_field_count = 0
source tree mutation during candidate build = 0
runtime/source header mutation count = 0
```

---

### Change 5 — Build the isolated T1 integration delta and D2 handoff relation

Purpose:

Verify in an isolated candidate that T1 can consume the canonical owner output, while keeping Menu/current routes protected and packaging the exact Classification relation that T1-D2 will consume.

Files:

- current `IrisClassifications.lua` and Browser projection files (read-only protected comparison inputs)
- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py` (unchanged regression target)
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `docs/iris_tooltip_t1_display_contract_policy.md`

Implementation Notes:

- Build a candidate T1 Layer 2 route that names the canonical JSON path/schema/hash without adopting it as global current.
- Add the owner output hash to the isolated T1 candidate input hashes and exact workstream subject identity.
- For a resolved row, construct S1 only from owner-issued category/primary identity and KO/EN surfaces.
- For a positive-proof absence row, construct legitimate S1 absence without suppressing independent S2-S4 slots.
- Missing row, unresolved state, invalid primary, authority/provenance gap or surface defect remains Classification-owner correction.
- Remove the unconditional `CLASSIFICATION_RESOLVED_IDENTITY_MISSING` emission only after owner output validation succeeds.
- Do not write `IrisClassifications.lua`, Browser projection code, translation/fallback files or other runtime/public paths.
- Emit the exact D1 owner identity/surface/authority relation required by T1-D2. Continue to retain the Menu consumer correction; owner output existence is not Menu consumption evidence and owner output fields must not be compared with themselves.
- Do not modify Layer 3/4 selection, current Tooltip runtime or T2 handoff schema.
- Do not redesign or mutate Menu layout, sorting, primary source or display presentation.
- Do not rewrite the predecessor T1 candidate/finalizer receipts. Produce a new workstream-local candidate and re-audit bundle for D6.

Validation:

```text
t1_candidate_projection_source_relation == canonical Classification registry
runtime/public mutation count = 0
D2 handoff relation complete = true
T1 support set == owner-output applicable set
resolved S1 identity/surfaces == owner output
absence S1 carries positive owner proof
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0 for D1 complete
Classification owner blocker count = 0 for D1 complete
Menu consumer correction is not auto-closed
T2 handoff count remains 0 while any blocker remains
```

---

### Change 6 — Audit the whole universe and verify the protected consumer boundary

Purpose:

Verify every exact support row, D1 owner-output completeness, D2 handoff relation and protected Menu/runtime/public no-mutation boundary.

Files:

- `Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py` (new)
- current T1 audit consumer
- conditional generated Browser/Menu projection and supported facade files as comparison inputs
- repository-external whole-universe, correction and no-regression reports

Implementation Notes:

- Apply one decision matrix to every support FullType: exact row, terminal state, taxonomy validity, membership/primary relation, authority/provenance, locale surface refs, absence proof, no inference and no duplicate.
- Never patch the audit artifact. Correct the owner registry/source, regenerate and re-audit.
- Verify runtime/public target hashes are unchanged and record the actual current Menu path separately from the D1 registry/T1 candidate relation.
- Treat missing Menu consumer evidence only as the existing Menu correction. D1 neither verifies nor closes it.
- Keep Menu parity unresolved and its correction open as required by the current T1 contract; do not turn route equality or owner-output self-comparison into consumer evidence.
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
runtime/public mutation count = 0
protected Menu route observation missing count = 0
D2 handoff relation mismatch count = 0
owner output self-comparison count = 0
```

---

### Change 7 — Run focused, lifecycle and repository validation

Purpose:

Bind implementation, independent validation and T1 re-audit to the same exact subject without self-certification.

Files:

- focused classification/T1 test files
- existing focused-test membership inputs
- repository-external candidate materialization Run A/B, comparator and bundle-validation receipts

Implementation Notes:

- Existing parameterized focused tests cover the predecessor/support freeze, support-left-join census, `no_membership_record`, exact identity, registry/absence schema, primary gap behavior, `Misc.9-A`, `1-K/1-L/6-F` owner disposition, locale binding, deterministic JSON materialization, candidate safety, T1 candidate consumption and protected runtime/public no-mutation.
- Add at most four composite parameter rows across the existing families; each row asserts all related subcases so individual test identities are not multiplied:
  1. **terminal relation:** missing/non-terminal support row, missing primary and primary outside membership all fail-loud with the Classification correction.
  2. **authority and fallback:** missing authority/provenance, unsupported manual override and raw `Misc.9-A` promotion all fail-loud.
  3. **identity and locale:** exact duplicate, case-normalized collision, KO-only/EN-only surface and required-locale absence preserve exact keys and fail the invalid row.
  4. **consumer boundary:** consumer-specific field, owner-output self-attestation and Menu evidence impersonation are rejected while the D2 handoff relation remains separate.
- Run the new Classification candidate twice in fresh repository-external roots and compare canonical bytes.
- Run the isolated T1 candidate and confirm only the D1 Classification target is retired in the candidate ledger. This is a D6 integration proposal, not current adoption.
- Do not add a workstream-specific test file or top-level test family. Add only the four composite rows above to the existing Classification candidate-install and Tooltip T1 families; do not duplicate a subcase already covered by an existing row.
- Canonical repository full-gate Run A/B, global comparator and post-gate finalizer are executed once by T1-D6 after all bundles are integrated.
- Claim PASS only when every exact relevant command exits `0`.

Validation:

The planned focused command is:

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
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

D1 seals focused-test, candidate-determinism, protected-path and bundle-validation receipts. T1-D6 uses the current `ENTRYPOINTS.md` literal to run the integrated canonical full validation once.

---

### Change 8 — Seal the D1 correction bundle for T1-D2 and T1-D6

Purpose:

Seal the validated Classification owner output, shared-path delta, protected-path hashes and D2/D6 integration instructions without performing global current adoption.

Files:

- external `t1d1_closeout.json`
- external `t1d1_parallel_integration_manifest.json`
- external `t1d1_shared_path_delta.json`
- Classification owner registry/output and validation receipts

Implementation Notes:

- Record the canonical registry/JSON hash, producer, validator, exact workstream subject, frozen support hash, D2 handoff relation and protected runtime/public hashes.
- Keep the predecessor T1 formal-complete snapshot and its `5,625` correction ledger as historical subject-bound evidence.
- Mark `workstream_correction_bundle=complete` only if the isolated candidate re-audit reports Classification blocker 0 and `CLASSIFICATION_RESOLVED_IDENTITY_MISSING` 0.
- Preserve DVF, Iris presentation-contract, Menu consumer and QG/locale correction classes exactly as re-audited; do not infer their counts from predecessor arithmetic.
- Keep `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS` and production handoff 0 while any other T2-blocking correction remains.
- If implementation artifacts and validated progress exist but Classification corrections remain, set the task state to `partial` and record a separate blocking reason plus exact owner/reason distribution.
- If a required owner decision, authority, tool or validation precondition prevents a valid artifact/adoption result, set the task state to `blocked` and record the separate blocking reason. Never publish `partial/blocked` as a composite state.
- Current ecosystem adoption remains `pending_T1_D6`; D1 does not update global manifests, routes, environment locator or governance status.
- If an applicable exact-subject authority explicitly requires independent review, record its state and receipt as a separate bundle axis.

Validation:

```text
bundle identifies one Classification owner output
frozen support and protected runtime/public hashes remain unchanged
predecessor authority/evidence remains immutable
workstream closeout subject == validated candidate subject
Classification blocker count = 0 for complete
independent review state recorded separately when applicable authority requires it
other-owner correction classes remain separate
current_ecosystem_adoption = pending_T1_D6
T2 progression remains blocked and production handoff remains absent
```

---

## 7. Validation Plan

### Automated Validation

#### Contract and source validation

- common predecessor/support freeze and D1 protected-path allowlist
- pre-mutation exact support freeze and post-mutation no-drop equality
- support-universe-left-join enumeration and distinct `no_membership_record` cohort
- exact FullType byte round-trip and case-sensitive uniqueness
- taxonomy/category/subcategory identity validity
- membership and primary relation
- authority/provenance reference existence and subject binding
- allowed absence enum and positive owner proof
- `Misc.9-A` fallback non-promotion
- separate category/subcategory surface reference integrity
- KO/EN key uniqueness and exact requested-locale presence
- exact `1-K/1-L/6-F` membership observation and owner defect-layer disposition
- consumer-specific field and self-attestation rejection
- exact runtime/public pre/post hash equality

#### Determinism and mutation isolation

- census Run A/B semantic equality
- owner-output candidate Run A/B byte equality
- stable exact-byte row ordering and canonical JSON serialization
- pre-mutation frozen support hash equality after candidate install and re-audit
- non-target repository source/runtime hash equality before/after candidate runs
- external empty-root enforcement and hash-bound allowlisted install
- isolated JSON candidate and shared-path delta integrity with zero runtime/public mutation
- stale subject/input hash mismatch failure

#### T1 integration and regression

- resolved/absence S1 projection table
- T1 consumer fail-loud correction emission for absent row, non-terminal row, invalid primary membership, missing authority/provenance and missing locale surface
- no raw-tag/name/rendered-string inference in T1
- whole-universe support/output equality
- Classification blocker and reason-code accounting
- exact current Menu route observation and no-mutation proof
- D2 handoff relation completeness without consumer-evidence self-attestation
- Menu correction independence, descriptive `menu_consumer_evidence_unverified` text where applicable and no self-comparison
- unchanged Layer 3/4 projection invariants
- blocked T2 progression and zero production handoff while other blockers remain
- supported `IrisClassifications`, `IrisPrimarySubcategory`, Browser/API facade no-regression report

#### Repository validation

- focused `uv run --project .\Iris\tooling ... pytest` command exits `0`
- exact runtime/public pre/post hash comparator exits `0`
- Classification candidate Run A/B and comparator exit `0`
- T1 candidate re-audit exits `0`
- read-only current membership command exits `0`
- D1 bundle validator exits `0`; integrated full gate/deterministic comparison is D6-owned

Core unconditional zero metrics:

```text
duplicate_exact_fulltype_count
case_normalization_merge_count
support_universe_enumeration_mismatch_count
frozen_support_row_drop_count
invalid_category_id_count
invalid_subcategory_id_count
primary_not_in_membership_count
missing_classification_authority_count
missing_classification_provenance_count
cross_locale_fallback_count
locale_specific_identity_reselection_count
rendered_string_reverse_parsing_count
raw_tag_semantic_inference_count
fulltype_name_inference_count
unsupported_primary_ranking_count
unsupported_misc_fill_count
t1_consumer_negative_fixture_missed_correction_count
self_issued_menu_consumer_evidence_count
self_issued_audit_verdict_count
consumer_specific_semantic_field_count
candidate_build_source_mutation_count
```

Claim-conditional metrics:

```text
unresolved_count = 0                         # T1-D1 complete claim
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0 # T1-D1 complete claim
Classification owner blocker count = 0      # T1-D1 complete claim
unadjudicated_identity_surface_conflict_count = 0 # T1-D1 complete claim
surface_authority_contradiction_count = 0    # when the owner disposition includes a surface defect and D1 claims complete

unauthorized_runtime_public_mutation_count = 0
protected_menu_route_observation_missing_count = 0
D2_handoff_relation_mismatch_count = 0
```

### Validation Ceiling Disclosure

Every terminal receipt and closeout records the three categories required by `docs/EXECUTION_CONTRACT.md` §6-2:

| Category | Required D1 content |
| --- | --- |
| `validated` | exact-subject census completeness, owner-output contract, deterministic candidate, T1 fail-loud fixtures, candidate re-audit, D2 handoff relation과 runtime/public no-mutation |
| `out_of_scope` | full Menu parity, independent Menu evidence, visual layout/text quality, broad UI/in-game acceptance, performance, multiplayer, broad external-mod compatibility, Tooltip runtime and release/deployment |
| `unvalidated_but_in_scope` | any selected-branch effect that remains inside the authorized mutation surface but lacks evidence; this must be empty for a `complete` claim |

The closeout may not move an unvalidated selected-branch effect into `out_of_scope` merely to claim success. If `unvalidated_but_in_scope` is non-empty, use `partial` or `blocked` and identify the missing evidence.

### Manual Validation

- Review every new owner decision family and a stratified sample of single, multi, explicit-primary, fallback-derived and owner-approved-absence rows against its cited authority/provenance.
- Review the complete `no_membership_record` cohort disposition separately from explicit unclassified rows; confirm the frozen support set lost no exact identity.
- Verify `Base.LemonGrass` and `Base.Lemongrass` remain separate exact rows throughout census, output and T1 audit.
- Inspect the 9 category and 50 subcategory surface bindings in both locales without relying on Browser fallback strings; explicitly verify the owner defect-layer disposition and resulting bounded correction for `Iris_Sub_1K`, `Iris_Sub_1L` and `Iris_Sub_6F`.
- Confirm current Menu/runtime/public hashes are unchanged, D2 handoff relation is complete and Menu evidence/parity remains a separate correction.
- When `no_defect_with_authority_explanation` is selected, verify whether it preserves or explicitly supersedes the sealed taxonomy decision and that no implicit meaning change remains.
- If applicable current authority requires independent review, verify its exact-subject receipt separately without treating it as machine validation or owner seal.
- Review closeout language against actual validation scope and correction distribution.
- Run bounded Browser runtime acceptance for facade, grouping and owner-resolved primary behavior; no full in-game visual/UI parity review is implied.

### Validation Limits

- no semantic correctness proof for every individual item classification beyond the approved owner records and cited evidence
- no translation naturalness/quality review
- no actual Tooltip pixel fit, wrapping, four-line assembly or Alt-key behavior
- no independent Menu evidence, full Menu parity verification, Menu source convergence, layout redesign or broad UI acceptance
- no broad translation rewrite beyond exact owner-adjudicated D1 identity-bound locale/fallback corrections
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

None intended. D1 protects runtime/public sources and emits only offline owner output plus isolated integration proposals.

### Compatibility Surface

Touched only at the offline Classification output and isolated T1 candidate boundary. Existing Lua/API/Browser facade shapes and bytes are protected.

### Sealed Artifact Surface

Touched additively. New exact-subject candidate/output/receipts and successor readpoints are added; predecessor T1 evidence and current historical closeout are not rewritten.

### Public-Facing Output Surface

No current public output mutation. Approved category/subcategory KO/EN authority is packaged for D2/D6 adoption without runtime rendering.

---

## 9. Risk Analysis

### Architecture Risk

- The materializer may accidentally become a second classification authority by choosing primary or repairing provenance.
- A tracked owner output may be mistaken for Menu consumer evidence or a general consumer-specific database.
- Retired one-shot/history output may re-enter as current source because the current runtime table lacks row-level provenance.
- Updating T1 audit and Classification materializer together may create self-certification without an independent validator/gate.
- A new output may duplicate rather than converge current Classification ownership if source/producer/installer roles are not explicit.

### Runtime Risk

- A D1 candidate could accidentally mutate protected Menu/runtime paths or imply current convergence.
- Changing `IrisBrowserProjectionBuilder` so the owner primary controls both tag and location may expose previously presentation-derived behavior; bounded Browser contract/runtime acceptance must make this visible.
- Exact locale/fallback correction may alter public labels for the adjudicated identities. A wider translation or presentation change would exceed scope.
- A validated D1 owner output could be mistaken for independent Menu evidence and incorrectly close the Menu correction.

### Compatibility Risk

- Existing `classification` candidate CLI/manifest/install behavior could be broken by overloading its file set.
- Supported `IrisPrimarySubcategory` global and `IrisAPI.Tags` facade could drift even without intentional removal.
- An overly broad candidate allowlist could mutate runtime/public paths or make an isolated delta appear current.
- Case-folded handling on Windows could merge exact identities.
- Label fallback behavior may be mistaken for locale authority and hide missing translation keys.
- Mere KO/EN key presence may be mistaken for semantic agreement despite the current `1-K/1-L` EN/fallback conflict.

### Regression Risk

- The 2,280 baseline may be hard-coded and silently drop a changed exact-subject member.
- A census driven from the 2,079-row membership table rather than the frozen support spine may omit the observed 201-row `no_membership_record` cohort.
- 408 actual `Misc.9-A` rows may be trusted because the header claims a different fallback count.
- 265 observed multi-membership primary gaps may be filled with presentation/alphabetical order.
- The T1 audit may report zero corrections because its changed detector stopped emitting, rather than because the owner output is complete.
- Owner-approved absence may conceal missing provenance, ambiguous primary or producer failure.
- T1 Classification completion may be expanded into T2 OPEN, handoff generation, Menu parity or semantic correctness.
- Other-owner correction counts may be changed by arithmetic rather than new exact-subject re-audit.

### Operational Risk

- Owner adjudication of the observed 265 multi-membership rows without an explicit primary plus the entire `no_membership_record` cohort may be the execution bottleneck. Batch tooling may group evidence, but it cannot choose outcomes or weaken row-level authority/provenance requirements.
- The `1-K/1-L/6-F` defect-layer decision may require coordination between Classification and locale owners. Until the disposition is recorded, neither membership nor surface may be silently normalized.

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
                +--> validation passes
                        |
                        +--> D1 JSON candidate + D2/D6 integration bundle
```

- Build/census failure leaves current `no_admissible_authority_relation`, T1 Classification corrections and blocked T2 progression unchanged.
- Owner gap failure does not reduce the denominator, create a fallback or patch the audit artifact.
- Candidate failure retains the prior tracked Lua projection, Browser consumer and T1 route. D1 candidate installation rejects every runtime/public target.
- Isolated T1 integration failure discards the unadopted shared-path delta. Predecessor T1 evidence and runtime projection remain intact.
- Validation evidence for a failed attempt is preserved as failed lifecycle evidence and never overwritten as PASS.
- A validated bundle can be superseded additively before D6 integration. Keep failed/superseded evidence immutable.
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
D1 attempts Menu convergence or runtime/public mutation
D2 handoff relation is incomplete or self-attested
shared/global path ownership boundary is violated
locale correction expands beyond exact owner-adjudicated and authorized D1 identities
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
- D1 has no Menu convergence branch. It emits the Classification relation for D2 and preserves the current Menu evidence/parity correction.
- D1의 no-Menu-mutation 경계는 architectural steady-state approval이나 future Menu/Tooltip convergence waiver가 아니다.
- Offline Python tooling never becomes PZ runtime logic.
- Existing Lua/API/Browser facade shapes and runtime/public hashes remain unchanged in D1.
- Current/historical/reproduction roles from the authority manifest are preserved. Retired source-root/one-shot scripts are not re-adopted by convenience.
- Audit/census/run receipts are written only to repository-external immutable roots; no mutable latest pointer or stateful registry is introduced.
- Predecessor T1 formal-complete subject and evidence remain immutable.
- D1 does not adopt governance documentation. Any subject-bound successor wording is a D6 integration proposal and cannot replace machine receipts.
- Machine validation, independent review and owner seal remain separate axes. Independent review becomes mandatory only when an applicable current exact-subject authority says so; this plan adds no originating-roadmap non-coauthor prerequisite.
- Existing user changes in the dirty worktree are preserved and unrelated files are not modified.
- Claim PASS only when the exact relevant required command exits `0`; missing tooling is BLOCKED.

---

## 12. Expected Closeout State

Expected workstream target: `complete`, guarded by owner resolution and exact-subject candidate validation. Global current adoption remains pending T1-D6.

`complete` means only:

```text
T1-D1 Layer 2 Classification correction bundle = complete
Classification owner blocker count = 0
CLASSIFICATION_RESOLVED_IDENTITY_MISSING = 0
canonical Layer 2 owner output validated in an isolated candidate
Menu/runtime/public path preserved
T1-D2 input relation sealed
pre-mutation support set preserved with every no-membership row terminally resolved or positively absent
1-K/1-L/6-F defect layer adjudicated and every required bounded correction adopted
T1 consumer negative fixtures prove fail-loud correction emission
current_ecosystem_adoption = pending_T1_D6
new test files/functions = 0 unless the single-function exception is justified
```

It does not mean semantic correctness of every classification was independently proven, independent review passed, Menu consumer evidence/parity correction was closed, current authority was globally adopted, T2 opened, a production handoff was generated, Tooltip runtime was implemented, or release readiness was established.

Expected post-closeout progression while other owner blockers remain:

```text
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production T2 handoff = 0
```

If any exact support row lacks a valid terminal state, primary, authority/provenance or required locale surface, D1 may not claim complete. Use exactly one task state:

- `partial` when valid implementation/evidence was produced but residual Classification corrections remain; record the blocking reason separately.
- `blocked` when an owner decision, authority, tool or validation precondition prevents valid adoption; if applicable authority requires independent review, its missing receipt may be such a separately recorded precondition.

In either case, the closeout enumerates the remaining Classification owner/reason distribution, D2 handoff readiness, validation ceiling and any authority-required independent-review state. The composite label `partial/blocked` is prohibited.
