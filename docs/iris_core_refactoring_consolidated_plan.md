# Iris 핵심 리팩토링 종합 실행 계획

> 상태: 3차 개정본 후속 정밀 피드백 반영 계획
>
> 기준일: 2026-08-02
>
> 입력: 사용자 제공 `Iris 핵심 리팩토링 종합 로드맵`, 네 차례의 종합 검토안(최신: `Iris 핵심 리팩토링 종합 실행 계획 3차 개정본 — 최종 종합 검토안`), 사용자 후속 정밀 피드백 N1–N3 및 추가 5개 항목, 현재 working tree의 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `EXECUTION_CONTRACT.md`, Iris 런타임·빌드·테스트 코드
>
> 실행 게이트: Change 1의 read-only inventory와 baseline capture는 즉시 허용한다. Change 2는 mode별 manifest source, staged validator identity, sealed-reservation guard를 가진 fail-closed validation-asset validator와 negative fixtures를 먼저 만들고 통과시킨 뒤 characterization asset을 활성화한다. 이 공통 infrastructure gate는 모든 후속 runtime-visible work의 선행 조건이다. 이후 Changes 3–6의 각 runtime-visible subchange는 자신이 건드리는 pre-refactor behavior axis의 Lua/PZ evidence와 staged/clean-checkout VCS 재현성만 `validated`이면 시작할 수 있으며, 관련 없는 미검증 PZ axis를 기다리지 않는다. 미래 target acceptance contract는 각 구현 Change가 소유한다. 기존 package projection을 대상으로 한 `-Clean` 실행은 금지한다.

## 1. Objective

현재 Iris 코드베이스에서 실제로 남아 있는 중복, 암묵 상태, UI 재구축 비용, 테스트의 구현 결합, 빌드 도구의 책임 혼합을 단계적으로 줄인다. 리팩토링 전후에 현재 runtime authority, current-route 계약, 패키지 payload, public-facing text와 Phase 0 supported API manifest에 열거된 API·module path·global alias·public facade의 동일성 또는 승인된 변화 관계를 증명한다. manifest 밖의 알려지지 않은 외부 consumer는 보증하지 않는다.

이 계획은 첨부 로드맵의 제안을 그대로 재실행하지 않는다. 코드베이스 확인 결과 이미 완료된 `IrisProtectedCall`, `IrisModuleBootstrap`, `IrisItemAccess`, Layer 3 chunk-only runtime 전환, `compose_layer3_text.py` 분해, current/historical/diagnostic 테스트 경계는 기준선으로 고정한다. 실행 대상은 그 이후에도 남은 residual 문제로 한정한다.

성공 상태는 다음과 같다.

* Browser와 Wiki가 동일한 사실 수집 모델을 사용하되 각 UI 렌더러와 상호작용은 독립적으로 유지된다.
* `Description` 공개 API의 중복 실행 경로가 하나로 합쳐지고, runtime Generator 제거 여부는 sealed offline equivalent 증거로만 결정된다.
* Browser 선택 처리, BrowserData build-state, 검색용 정규화, 상세 스크롤이 명시적인 계약과 실제 Lua/PZ behavior test를 가진다.
* 현재 사용 중인 capability, taxonomy, 전역 데이터 경계가 `dead code`로 오인되어 제거되지 않고, 실제 caller와 compatibility 기준에 따라 정리된다.
* 빌드 도구 분해는 current core closure와 allowed tooling 경계를 우회하지 않으며, CLI·바이트·실패 동작을 보존한다.
* staging, package, temporary, historical copy는 역할이 증명된 경우에만 disposition을 부여하며, tracked/ignored 상태만으로 이동하거나 삭제하지 않는다.

---

## 2. Scope

* Iris Lua runtime의 description, Browser, Wiki, tooltip, static-data access 경계
* Iris runtime behavior를 검증하는 Lua dev harness 및 Python contract tests
* current-route가 직접 소비하는 build core와 allowed tooling 중 승인된 범위
* current, package projection, historical reproduction, diagnostic, temporary artifact의 역할 inventory
* standalone Lua와 in-game PZ harness를 통한 machine-readable behavior characterization
* 리팩토링 후 current-route, Lua syntax, disposable package candidate identity, 수동 in-game UI 회귀 검증
* 이 계획에서 새로 만드는 validation infrastructure는 이 리팩토링의 characterization, acceptance, evidence schema, package 및 clean-checkout support asset 검증에만 한정

### Explicitly Out Of Scope

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 11개 chunk가 가진 current runtime 내용의 재작성
* DVF System의 facts, decisions, profile, body plan, rendered body, adoption state 또는 public text의 의미·품질 변경
* Iris Artifact Registry, Publish Boundary, DVF Body Compiler의 authority 재배치
* monolith `IrisLayer3Data.lua`를 current runtime authority로 복귀시키는 작업
* Project Zomboid B42 대응, Workshop 배포, release readiness 또는 production deployment
* Pulse나 다른 spoke가 Iris에 의존하도록 만드는 변경
* Java/JVM runtime을 Iris에 추가하는 변경
* 증거 없는 staging 대량 삭제, Git history rewrite, Git LFS·외부 저장소 migration
* 전체 build script를 파일명 glob으로 통합·보관·삭제하는 작업
* unrelated UI redesign, taxonomy 정책 변경, 신규 추천·비교·판단 기능
* `IrisMain.lua` 전체 초기화 상태의 재설계. 이 계획의 상태 전환 범위는 `IrisBrowserData` build-state다.
* machine-readable supported API manifest 밖의 알려지지 않은 모든 외부 mod 호환성 보증

---

## 3. Non-Goals

* 파일 수나 줄 수 자체를 품질 지표로 삼지 않는다.
* 모든 source-reading test를 제거하지 않는다. authority·forbidden-path·dependency-closure처럼 소스 형태가 계약인 테스트는 유지한다.
* 모든 lazy `require` 실패를 영구 negative cache로 만들지 않는다. 세션 중 불변이라고 증명된 optional module에만 적용한다.
* `can_*` capability를 현재 semantic authority로 승격하지 않는다. 기존 상호작용 표시에 필요한 compatibility projection으로만 다룬다.
* Browser와 Wiki를 하나의 UI로 합치지 않는다. 공유 대상은 read-only detail model과 formatter 계약이다.
* 이미 분해된 `compose_layer3_text.py` 모듈을 다시 합치거나 동일 책임의 두 번째 common package를 만들지 않는다.
* `.gitignore`를 짧게 만드는 것 자체를 목표로 하지 않는다. 현재 파일은 VCS role allowlist 계약으로 취급한다.
* validation asset validator를 일반 repository governance framework나 다른 모듈의 범용 정책 엔진으로 확장하지 않는다.

---

## 4. Assumptions

* 프로젝트의 최상위 권위는 `docs/Philosophy.md`이며, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 현재 working-tree 상태를 실행 기준으로 사용한다. `docs/EXECUTION_CONTRACT.md`는 이 계획의 disclosure, claim-evidence binding, validation ceiling, standard closeout state 의무를 제공하며 상위 architecture나 module policy를 재정의하지 않는다.
* 현재 runtime authority는 Layer 3 chunk manifest와 chunk 11개다. source, rendered, Lua bridge, package projection은 문서화된 writer/consumer 경계를 우회해 직접 수정하지 않는다.
* 현재 package/current-runtime identity와 full current-route `145/145` 결과는 보호할 기준선이다. 실행 시작 시 비파괴 명령으로 새 baseline을 다시 캡처하며, 기존 문서 숫자를 무조건 재사용하지 않는다.
* `Iris/_docs/round3/round3_active_core_closure.json`의 current core 12개와 allowed tooling 4개는 별도 검토 없이 확장하지 않는다. allowed tooling은 현재 `4/4`로 잔여 slot이 0이다.
* `Iris/build/description/v2/tools/build/INVENTORY.md`가 기록한 disposition에 따라 `tools/build/*.py`의 archive/delete eligible 집합은 현재 0이다. 후속 증거가 없으면 이 결론을 유지한다.
* 기존 working tree의 다른 문서 변경은 이 계획과 무관한 사용자 변경으로 간주하고 보존한다.
* in-game behavior 검증에는 Project Zomboid B41 호환 실행 환경과 Iris dev mode를 사용할 수 있다고 가정한다. 사용할 수 없으면 해당 PZ-dependent 축은 `unvalidated_but_in_scope`로 남기고 behavior equivalence 또는 plan `complete`를 주장하지 않는다.
* 새 모듈 이름이나 evidence 경로가 기존 manifest·`.gitignore` 계약에 걸리면, 우회 추가하지 않고 먼저 승인된 additive manifest 변경을 만든다.
* `Iris/build/package`는 기존 package peer의 read-only 비교 surface다. 모든 package 생성은 checkout 밖의 고유 disposable `-OutputRoot`에서 수행한다.
* planning readpoint의 resolved standalone 실행기는 PUC-Rio Lua `5.4.8`이다. 실제 실행 시 executable path, implementation, version output을 다시 캡처하며, PUC Lua 결과를 Project Zomboid B41 Kahlua runtime equivalence로 자동 승격하지 않는다.

### Codebase Inspection Readpoint

2026-08-02 코드 확인에서 다음 residual을 확인했다.

* `API/Description.lua`의 `getDescriptionBlocks()`와 `getDescription()`가 Generator 로드, tag 조회, protected generation을 각각 수행한다.
* `Logic/IrisDesc/Generator.lua`는 runtime에서 TagParser, Ordering, Templates, Renderer를 연결한다. 따라서 단순 중복 제거와 Generator 완전 제거는 서로 다른 위험 수준이다.
* `IrisBrowserListController.lua`에는 category, subcategory, item 선택 payload fallback과 debug table dump가 반복된다.
* `IrisBrowserDetail.lua`의 mouse-wheel 경로는 scroll 값 변경 후 `showDetail()`을 호출해 child widget 전체를 다시 만든다.
* `IrisBrowserData.build()`는 핵심 dependency가 없을 때도 `_built=true`가 될 수 있어 빈 index가 성공 상태로 고정될 수 있다.
* `IrisBrowserBase.ensureBrowserDataBuilt()`와 `IrisBrowserData.lua`의 여러 query facade가 `_built` boolean을 직접 읽는다. 문자열 state를 그대로 대입하면 Lua truthiness 때문에 최초 build와 retry를 무음 skip할 수 있다.
* `IrisBrowserQuery.searchAll()`은 매 검색마다 display name과 full type을 소문자로 변환한다. 같은 파일의 `getGroupVariants()`는 `IrisData.ItemGroups` 전역을 읽지만 현재 내부 caller가 확인되지 않았다.
* `IrisWikiSections.lua`의 legacy renderer와 core renderer는 weight, type, module, food/weapon facts를 중복 조립한다. food 수치는 한 경로에서 `* 100`, 다른 경로에서는 raw value를 사용하므로 실제 단위를 먼저 characterization해야 한다.
* `API/UseCases.lua`의 capability API는 `IrisBrowserInteractionCollector.lua`가 현재 소비한다. 이는 즉시 삭제 가능한 dead code가 아니다.
* `API/StaticData.lua`는 optional data load cache를 제공하지만 실패를 cache하지 않는다. 재시도 가능성이 필요한 모듈과 세션 중 불변 모듈을 분리해야 한다.
* `tools/common/`에는 현재 `paths.py`만 있고, `public_text_quality_acceptance.py`, `export_dvf_3_3_lua_bridge.py`, `_dvf_3_3_vnext_common.py`에는 serialization, path, hashing, contract, orchestration 책임이 함께 있다.
* 테스트는 `Iris/test/`, `Iris/build/tests/`, `Iris/build/description/v2/tests/`, `Iris/validation/clean_checkout/tests/` 네 root에 존재한다. 일부 contract test는 Lua source string에 결합돼 있으나 모든 `read_text()` 사용이 구조 결합을 뜻하지는 않는다.
* working copy의 `Iris/build/description/v2/staging/`은 약 5.2천 파일, 4.59 GB이고 그중 Git tracked surface도 크다. current, rollback, probe, candidate, historical copy가 섞여 있어 크기만으로 처분할 수 없다.
* `package_iris.ps1`는 `-OutputRoot`를 지원하지만 기본값은 `Iris/build/package`이며, 기존 output에 `-Clean`을 주면 해당 package root를 삭제한다. baseline/closeout 명령은 기본 output을 사용하지 않는다.
* `Iris/build/description/v2/tests/*`는 기본 ignore되고 파일별 exact `!` 규칙으로 추적된다. Change 2의 세 characterization test와 Changes 3–6에서 실제 생성하는 acceptance test는 현재 exact allowlist가 없으므로 각 소유 changeset에서 `.gitignore`를 함께 갱신해야 한다.
* `tools/check_lua_syntax.ps1`는 `luac`를 필수로 하며 기본 root에 기존 package projection도 포함한다. 이 계획은 source root를 명시하고 disposable package는 별도로 검사한다.
* runtime code에는 `unpack`/`table.unpack`, `tostring`, `string.format`, Java/Kahlua object invocation 등 VM/dialect-sensitive 경로가 실제 존재한다. fixture별 dialect classification 없이 standalone output을 PZ behavior로 해석하지 않는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/media/lua/client/Iris/API/Description.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/API/UseCases.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/*.lua`
* `Iris/media/lua/client/Iris/UI/Browser/*.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua` (new, shared read-only model)
* `Iris/media/lua/client/Iris/UI/Tooltip/*.lua` only when taxonomy/static-data access normalization requires it
* `Iris/_dev/media/lua/client/Iris/Dev/IrisDesc/TestHarness.lua`
* `Iris/_dev/media/lua/client/Iris/Dev/PreRefactorCharacterizationHarness.lua` (new, PZ baseline harness)
* `Iris/_dev/media/lua/client/Iris/Dev/*AcceptanceHarness.lua` (new in owning Changes 3–6)
* `Iris/test/lua/pre_refactor_characterization_harness.lua` (new, standalone baseline harness)
* `Iris/test/run_pre_refactor_characterization.ps1` (new)
* `Iris/test/validate_validation_assets.ps1` (new in Change 2)
* `Iris/test/validate_disposable_package.ps1` (new in Change 2)
* `Iris/build/description/v2/tests/test_iris_*_characterization.py` and `test_iris_*_acceptance.py` (new in owning Change)
* `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py` (read-only partial-reuse candidate)
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py` (read-only external-checkout lifecycle candidate)
* `Iris/build/description/v2/tools/common/*.py` only after Change 7 approval gate
* `Iris/build/description/v2/tools/build/public_text_quality_acceptance.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py` only for caller inventory and bounded extraction; no broad rewrite

### Docs

* `docs/iris_core_refactoring_consolidated_plan.md`
* `docs/EXECUTION_CONTRACT.md` (read-only execution-obligation input)
* `Iris/_docs/refactor/core_refactor/` (phase inventory, decisions, validation evidence, closeout)
* `Iris/build/description/v2/tools/build/INVENTORY.md` if a newly proven disposition or tool-family boundary changes its current record
* `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` only when execution establishes a durable architecture or authority decision not already present

### Config

* `.gitignore` only as an exact counterpart to an approved role/manifest change
* 신규 Python characterization/acceptance test별 exact `.gitignore` `!` rule은 각 소유 Change와 같은 changeset의 필수 변경
* `Iris/_docs/round3/round3_test_taxonomy.json` when affected tests change route class
* `Iris/_docs/round3/round3_active_core_closure.json` only through the reviewed Change 7 scope
* `Iris/_docs/round3/current_route_required_validations.json` only if a new required validation is explicitly adopted
* `Iris/tools/package_iris.ps1` only if package re-entry protection is proven insufficient; no routine refactor

### Generated Artifacts

Protected no-mutation baselines:

* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* current package peer of the same manifest and chunks

New execution evidence may be generated under `Iris/_docs/refactor/core_refactor/`. Evidence must record hashes and counts but must not become a second runtime or source authority. Disposable package candidate는 checkout 밖의 고유 temporary root에만 생성하며 authority 또는 durable artifact가 아니다.

---

## 6. Planned Changes

### Change 1 — Phase 0: Authority, Behavior, and Repository Baseline Lock

Purpose:

리팩토링 전에 현재 authority와 repository 역할을 비파괴적으로 고정하고, behavior 실행 가능 범위와 첨부 로드맵의 충돌 항목에 코드 기반 결정을 부여한다.

Files:

* `Iris/_docs/refactor/core_refactor/phase0_baseline.md`
* `Iris/_docs/refactor/core_refactor/phase0_protected_surface_manifest.json`
* `Iris/_docs/refactor/core_refactor/phase0_decision_matrix.md`
* `Iris/_docs/refactor/core_refactor/phase0_repository_role_inventory.json`
* `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`
* `Iris/_docs/refactor/core_refactor/phase0_behavior_execution_capability.json`
* `Iris/_docs/refactor/core_refactor/phase0_lua_vm_dialect_inventory.json`
* `Iris/_docs/refactor/core_refactor/phase0_dialect_divergence_inventory.json`
* `Iris/_docs/refactor/core_refactor/generator_parity_corpus.json`
* `Iris/_docs/refactor/core_refactor/phase0_build_import_inventory.json`
* `Iris/_docs/refactor/core_refactor/phase0_package_identity_baseline.json`
* `Iris/_docs/round3/round3_active_core_closure.json` (read-only input)
* `Iris/_docs/round3/current_route_required_validations.json` (read-only input)
* `Iris/build/description/v2/tools/build/INVENTORY.md` (read-only input unless new proof changes disposition)
* `docs/EXECUTION_CONTRACT.md` (read-only input)
* `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py` (read-only reuse inventory)
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py` (read-only reuse inventory)

Implementation Notes:

* 이 phase는 read-only inventory와 hash capture만 수행한다. runtime/build code, `.gitignore`, manifests, package output을 수정하지 않는다.
* `EXECUTION_CONTRACT.md`의 현재 version/hash와 적용되는 disclosure, evidence, validation ceiling, closeout obligation을 authority inventory에 기록한다. 이 문서는 module architecture authority로 승격하지 않는다.
* clean-checkout 공용 코드의 `canonical_json_bytes`, `sha256_bytes`, `ensure_external_root`, `git_bytes`/`git_text`, `git_identity`, `tracked_paths`, `blob_id`, `bytes_at_commit`/`json_at_commit`와 외부 clone/cleanup 경로를 inventory한다. Phase 0 decision matrix의 기본 disposition은 `partial_reuse`다. 기존 helper는 commit/tree·tracked/blob·canonical hash·external-root·disposable checkout lifecycle을 담당하고, 신규 validator는 이 계획의 manifest schema/lifecycle/mode orchestration만 담당한다. closure/allowlist 충돌이 확인되면 별도 구현으로 바꾸되 exact 중복 책임과 사유를 기록한다.
* 시작 commit, dirty paths, Python, standalone Lua candidates, `luac`, PZ dev-mode availability를 기록한다. 기존 dirty paths는 baseline hash 대상과 작업 diff에서 분리한다.
* 각 standalone interpreter candidate에 대해 resolved executable path, implementation, version, `-v` command output, supported version policy, target `project_zomboid_b41_kahlua` dialect와의 관계를 기록한다. planning readpoint의 PUC Lua `5.4.8`은 재확인 대상이며 Kahlua equivalence 증거가 아니다.
* facts, decisions, rendered, live chunk manifest/chunks, 기존 package peer의 path, count, hash를 읽기 전용으로 기록한다. `package_iris.ps1`는 Phase 0에서 실행하지 않는다.
* Browser/Wiki에서 대표 item fixture를 정한다. 최소 food, weapon, literature, moveable, multi-classification, Layer 3 adopted, Layer 3 unadopted, missing optional data 항목을 포함한다.
* supported external API surface를 machine-readable하게 열거한다. 각 row는 `symbol`, `module_path`, `signature_or_shape`, `compatibility_role`, `known_internal_callers`, `support_status`를 가지며, 최소 `IrisAPI` facade functions, public module paths, `Description`, `UseCases` capability facade, Wiki public functions, compatibility global aliases를 포함한다. compatibility claim은 이 manifest에 열거된 surface로 제한한다.
* `_built`를 직접 읽거나 쓰는 모든 Browser consumer와 writer, 실제 build/retry trigger와 event를 inventory한다. `IrisMain` 전체 초기화는 별도 표면으로 표시하고 이 계획의 mutation scope에서 제외한다.
* `export_dvf_3_3_lua_bridge`, `public_text_quality_acceptance`, `_dvf_3_3_vnext_common`의 direct import, transitive import, path execution, historical caller 수를 fresh inventory로 고정한다. 계획 본문에 과거 고정 caller 숫자를 사용하지 않는다.
* standalone Lua에서 실행 가능한 pure/stub logic과 PZ object/UI가 필요한 behavior를 함수·fixture 단위로 분류한다. 각 row에 `dialect_sensitive`, sensitivity reasons, required PZ cross-check를 기록한다.
* dialect divergence inventory는 최소 `unpack/table.unpack`, 숫자 `tostring`, `#` 연산, 정수·부동 나눗셈, 숫자 `string.format`, table iteration/ordering, Java/Kahlua object invocation을 다룬다.
* standalone interpreter 정책은 `PUC Lua 5.1.x가 있으면 우선 사용, 없으면 승인된 5.4.x를 auxiliary tier로 사용`이다. 어느 경우에도 standalone 결과만으로 Kahlua/PZ equivalence를 주장하지 않는다.
* `generator_parity_corpus.json`은 `IrisAPI.Tags`가 읽는 current frozen classification source, Browser primary-subcategory 입력 경로, runtime item universe의 열거 가능성을 추적한다. 각 row는 full type, ordered/canonicalized tags, primary-subcategory variant, source hashes와 canonical row identity를 가진다.
* corpus는 source authority, enumeration algorithm, source counts, emitted row count, duplicate/unresolved count, completeness verdict를 가진다. runtime item universe 또는 primary-subcategory 경우를 완전히 열거하지 못하면 `complete=false`로 기록하고 Generator full-removal branch를 `deferred_by_design`으로 고정한다.
* 다음 결정은 `selected`, `deferred`, `not_applicable`, `blocked` 중 하나로 명시한다.
  * runtime Generator: facade dedup만 수행할지 sealed offline description으로 완전 대체할지
  * staging: in-place role manifest 유지, non-destructive archive, disposable-only deletion 중 허용 범위
  * Python common modules: current core 12와 allowed tooling `4/4`를 유지할지, slot 교체/상향을 별도 승인할지
  * taxonomy/global: compatibility facade 유지 기간과 external caller 조사 범위
  * `.gitignore`: role manifest 변경의 exact projection이 필요한지
  * food 단위 불일치가 실제 기존 표시 오류로 판정될 경우: 기존 동작 보존, 별도 승인 changeset에서 수정, 이번 계획 밖 분리 중 하나
* repository artifact를 `current_authority`, `current_package_projection`, `required_sealed_evidence`, `historical_reproduction`, `diagnostic`, `regenerable_projection`, `disposable_local_residue`, `unresolved`로 분류한다.
* root `.tmp/`, root `.tmp_tests/`, `Iris/build/description/v2/.tmp_tests/`, 각 test root 아래 temporary directory, `console_log.txt`, 열람 불가능한 임시 경로를 inventory한다. 열람 불가능한 항목은 `unresolved`로 보존한다.
* `tracked`, `ignored`, `large`, `duplicate filename`은 role 판정 근거로 기록할 수 있지만 단독 disposition 근거로 사용하지 않는다.
* 어떤 protected hash라도 baseline capture 중 예상과 다르면 구현을 시작하지 않고 authority drift 조사로 전환한다.

Validation:

* `EXECUTION_CONTRACT.md` version/hash와 이 계획에 적용되는 claim-evidence, ceiling, closeout obligation이 Phase 0 authority inventory에 존재한다.
* clean-checkout 공용 코드의 실제 symbol/hash와 `partial_reuse` 경계가 decision matrix에 기록되고, 기존 validator 수정 없이 재사용 가능한지 판정된다.
* manifest의 모든 path가 존재 여부, Git tracking 상태, role, writer, consumer, hash 정책을 가진다.
* runtime/package current surface와 historical/probe surface가 disjoint인지 검사한다.
* current core 12와 allowed tooling `4/4`, 잔여 slot 0의 baseline을 machine-readable하게 고정한다.
* Change 2 및 후속 acceptance에서 생성할 Python/Lua/PowerShell/dev harness/fixture/schema/validator/corpus/ceiling asset 후보 전체에 `git check-ignore -v`를 실행해 현재 ignore source를 기록한다. 이 phase에서는 `.gitignore`를 바꾸지 않는다.
* Generator corpus의 `complete=true`는 source denominator와 emitted identities가 exact match하고 unresolved row가 0인 경우에만 허용한다.
* 기존 package peer의 pre/post read-only hash가 동일하다. Phase 0에는 package 생성 또는 `-Clean` 명령이 없다.
* current-route나 syntax preflight가 output을 만들 수 있으면 Phase 0에서 실행하지 않고 Change 2 이후 disposable validation으로 분류한다.

---

### Change 2 — Phase 1: Executable Behavior Characterization Gate

Purpose:

현재 pre-refactor tree에 실제로 존재하는 동작만 standalone Lua와 Project Zomboid에서 관찰해 machine-readable baseline으로 남긴다. 미래 target contract는 baseline denominator에서 제외하고 각 구현 Change가 소유한다. 이 Change의 validator는 이 계획의 validation assets 전용이며 repository-wide governance 기능을 새로 소유하지 않는다.

Files:

* `Iris/_dev/media/lua/client/Iris/Dev/IrisDesc/TestHarness.lua`
* `Iris/_dev/media/lua/client/Iris/Dev/PreRefactorCharacterizationHarness.lua` (new)
* `Iris/test/lua/pre_refactor_characterization_harness.lua` (new)
* `Iris/test/run_pre_refactor_characterization.ps1` (new)
* `Iris/test/validate_validation_assets.ps1` (new, fail-closed manifest/VCS validator)
* `Iris/test/validate_disposable_package.ps1` (new, first-mutation prerequisite)
* `Iris/test/fixtures/core_refactor/` (new, including invalid/empty/duplicate asset-manifest fixtures)
* `Iris/build/description/v2/tests/test_iris_pre_refactor_description_characterization.py` (new)
* `Iris/build/description/v2/tests/test_iris_pre_refactor_browser_characterization.py` (new)
* `Iris/build/description/v2/tests/test_iris_pre_refactor_detail_characterization.py` (new)
* 관련 기존 `test_phase5_*_contract.py`, Browser/Wiki contract tests
* `.gitignore`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/refactor/core_refactor/phase1_behavior_evidence.schema.json`
* `Iris/_docs/refactor/core_refactor/phase1_evidence_binding.schema.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.schema.json`
* `Iris/_docs/refactor/core_refactor/phase1_pre_refactor_headless_baseline.jsonl`
* `Iris/_docs/refactor/core_refactor/phase1_pre_refactor_headless_baseline.binding.json`
* `Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl`
* `Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.binding.json`
* `Iris/_docs/refactor/core_refactor/phase1_target_contract_ownership.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json`

Implementation Notes:

Time-axis split:

* 모든 evidence row는 `time_axis` (`pre_refactor_characterization` 또는 `post_refactor_acceptance`), `owner_change`, `baseline_denominator_included`를 가진다.
* Change 2의 PASS denominator에는 `pre_refactor_characterization` row만 들어간다. 아직 존재하지 않는 API/model/scroll target의 fixture는 실행하지 않으며 PASS denominator에 포함하지 않는다.
* `phase1_target_contract_ownership.json`은 미래 acceptance owner만 선언한다. Change 3은 Description single-path, Change 4는 state API/selection/search, Change 5는 detail model/incremental scroll, Change 6은 capability/variant/taxonomy/tooltip acceptance를 동일 changeset에서 추가한다.
* 미래 contract draft가 필요하면 `status=not_executed_future_contract`, `baseline_denominator_included=false`로만 기록한다. 이를 현재 behavior PASS로 해석하면 fail-loud한다.
* 각 구현 Change의 완료 조건은 `관련 pre-refactor baseline과의 승인된 관계 검증 + 해당 Change 소유 post-refactor acceptance PASS`다.
* 공통 infrastructure gate(manifest/schema validator negative matrix, asset lifecycle, VCS mode source, staged validator identity, disposable package no-mutation)는 하나의 전체 선행 조건이다. behavior characterization gate는 다음 축별로 독립 판정한다.

| Owner | Required pre-refactor axis |
|---|---|
| Change 3 | Description block/string/fallback 및 Generator mandatory facade axis |
| Change 4 | selection, BrowserData current build/dependency behavior, search/order axis |
| Change 5 | shared detail/raw food axis와 별도의 PZ scroll/click axis; 각 subchange는 자신이 만지는 axis만 요구 |
| Change 6 | capability, variant, taxonomy presentation, tooltip/public facade axis |

* 공통 infrastructure가 PASS한 뒤 특정 axis가 `validated`이면 해당 owner의 그 axis subchange는 진행할 수 있다. 관련 없는 PZ axis의 `unvalidated_but_in_scope`는 그 진행을 막지 않는다. Change 2 자체를 standard `complete`로 닫으려면 모든 mandatory characterization axis가 완료돼야 하며, 일부만 완료되면 `partial` 또는 blocking condition에 맞는 standard state로 보고하되 이미 validated인 axis의 후속 진행 자격은 유지한다.

Execution vehicle and VM policy:

* `run_pre_refactor_characterization.ps1`는 Phase 0에서 선택한 interpreter를 실제 실행하고 resolved executable path, implementation, version output을 evidence에 기록한다. Python test는 결과를 parse할 수 있지만 source string을 behavior 대용으로 사용하지 않는다.
* standalone harness는 현재 production module만 load하고 필요한 `require`, PZ globals, InventoryItem getter, list selection을 최소 stub으로 제공한다. 미래 state machine이나 view model specification double을 current baseline으로 실행하지 않는다.
* standalone evidence의 기본 role은 `auxiliary_standalone`이다. `dialect_sensitive=false`, VM identity complete, Phase 0 divergence check 통과, 같은 fixture의 PZ cross-check 일치가 모두 성립할 때만 target runtime behavior와 결속할 수 있다.
* Description byte/numeric formatting, food display, `unpack/table.unpack`, Java/Kahlua invocation, table-order dependent 경로는 기본 `dialect_sensitive=true`이며 PZ tier evidence가 필수다.
* PZ object/widget 의존 범위는 production package에 포함되지 않는 `_dev` overlay의 `PreRefactorCharacterizationHarness.lua`로 실행한다. 기존 `DEV_TESTHARNESS_MODULE`, `DEBUG`, `RUN_TESTS_ON_START` 경로 또는 명시적 dev command를 사용한다.
* 실행 결과는 JSONL로 남긴다. 각 row는 기존 identity/result 필드 외에 `subject_commit`, `subject_tree`, `subject_worktree_patch_sha256_or_null`, `producer_base_commit`, `producer_base_tree`, `producer_worktree_state`, `producer_overlay_sha256_or_null`, `lua_implementation`, `lua_version`, `lua_executable_path`, `lua_version_output`, `target_runtime_dialect`, `execution_environment`, `dialect_sensitive`, `dialect_reasons`, `evidence_role`, `stubbed_dependencies`를 필수로 가진다.
* production/runtime `subject_*`는 검증 대상 identity이고 `producer_*`는 harness가 실행된 base 및 overlay identity다. 둘을 같다고 가정하지 않으며 dirty subject/producer는 canonical tracked diff와 required untracked-input manifest로 만든 overlay SHA-256을 함께 기록한다.
* evidence JSONL은 자기 hash나 자신을 포함하는 commit을 내부에 요구하지 않는다. JSONL을 닫은 뒤 별도 binding record가 `evidence_sha256`과 schema version을 기록하고, 구현 changeset이 commit된 뒤 Change 9 closeout record가 그 구현 commit을 `final_changeset_commit`으로 결속한다. closeout record 자신의 commit hash를 내부에 넣는 순환 계약은 만들지 않는다.
* stdout/console-only 결과는 closeout evidence가 아니다. in-game writer를 사용할 수 없으면 console을 외부 수집기로 JSONL artifact에 materialize하고 hash를 기록한다.

Pre-refactor characterization coverage:

* `Description.getDescriptionBlocks`, `getDescription`, `getDescriptionForItem`의 반환값, nil/fallback, block ordering, log/failure 경계를 fixture로 고정한다.
* Browser 선택 payload를 `event item`, `selected index`, `missing selection`, `out-of-range index`로 나눠 결과를 검증한다.
* 현재 BrowserData의 `_built=false → build() → _built=true`, already-built skip, dependency 누락 시 empty classification cache가 성공으로 고정되는 결과, query facade의 boolean gate를 캡처한다. 이를 바람직한 target contract로 승인하지 않는다.
* 검색은 display name/full type 일치, case folding, 정렬 안정성, empty query를 검증한다.
* view model 도입 전 Browser와 Wiki 각각의 raw field, availability, section inclusion을 고정한다. 아직 존재하지 않는 shared view-model assembly를 실행하지 않는다.
* food hunger/thirst/stress/boredom 단위는 기대값을 먼저 추정하지 않고 동일 item의 실제 PZ getter raw value와 두 renderer 출력을 함께 캡처한다.
* scroll/click test는 PZ in-game harness에서만 behavior claim을 허용한다. standalone/source guard만 실행한 경우 해당 축은 `unvalidated_but_in_scope`다.
* normalization/rebuild 호출 횟수 같은 counter가 필요하면 standalone stub counter 또는 `_dev` instrumentation을 이 Change의 명시적 test asset으로 구현한다. production에 숨은 counter를 추가하지 않으며, counter가 없으면 성능 claim을 관찰된 결과 수준으로 낮춘다.
* Change 6의 gate를 위해 현재 capability facade, group variants, category/subcategory presentation label, tooltip tag/access 결과를 캡처한다.
* source-string assertion은 다음 두 부류로 분류한다.
  * 유지: forbidden require/path, current/historical closure, hard architecture boundary
  * behavior로 전환: helper 함수명, 소스 배열 순서, 내부 호출 횟수처럼 외부 동작과 무관한 구현 세부
* 모든 test file을 한 번에 이동하지 않는다. 변경 모듈의 test만 behavior contract로 전환하고 네 test root의 route 역할은 유지한다.
* 신규 Python test 세 개와 필요한 fixture 경로마다 exact `.gitignore` `!` rule을 동일 changeset에 추가한다. broad test-directory unignore는 하지 않는다.
  * `!Iris/build/description/v2/tests/test_iris_pre_refactor_description_characterization.py`
  * `!Iris/build/description/v2/tests/test_iris_pre_refactor_browser_characterization.py`
  * `!Iris/build/description/v2/tests/test_iris_pre_refactor_detail_characterization.py`
* `validate_disposable_package.ps1`를 Change 2에서 만들고 첫 production mutation 전에 실행한다. Change 7까지 생성을 미루지 않는다.
* Change 2의 첫 executable deliverable은 `phase1_validation_asset_manifest.schema.json`, `validate_validation_assets.ps1`, manifest negative fixtures다. 이 validator가 자기 무결성 negative matrix를 통과하기 전에는 characterization asset PASS나 Change 2 완료를 선언하지 않는다.
* `phase1_validation_asset_manifest.json` root는 `schema_version`, `generation`, `expected_required_count`, ordinal 정렬된 `expected_required_asset_ids`, `expected_required_asset_ids_sha256`, `sealed`, `assets` 배열을 필수로 가진다. `expected_required_count`는 0보다 커야 하고 active required row 수 및 expected ID 수와 정확히 같아야 한다.
* `asset_id`는 lowercase ASCII `[a-z0-9][a-z0-9._-]*`로 제한한다. `expected_required_asset_ids_sha256`의 canonical source는 선언 배열이 아니라 `assets`에서 `required=true`인 row의 `asset_id`를 유도한 집합이다. 이를 `StringComparer.Ordinal`로 정렬하고 LF로 join한 뒤 trailing LF를 붙인 UTF-8(no BOM) bytes로 hash한다. digest는 SHA-256 lowercase hexadecimal이다. 선언된 `expected_required_asset_ids`는 이 유도·정렬 배열과 순서까지 exact match해야 한다.
* manifest `path`는 이 계획의 portable validation asset에 한해 ASCII repository-relative canonical path로 제한한다. `/` separator만 사용하고 drive/UNC/leading slash, empty·`.`·`..` segment, repeated/trailing slash를 금지하며 `[A-Za-z0-9._/-]+`와 일치해야 한다. mode adapter는 validated `RepositoryRoot` 아래로 resolve되는 file임을 확인하고 LocalCandidate/CleanCheckout에서는 `Test-Path -PathType Leaf`, StagedChangeset에서는 index object type `blob`을 요구한다.
* manifest는 Phase 0 Generator corpus와 VM/dialect inventory, Lua/PZ harness, PowerShell runners, Python tests, fixtures, evidence/binding/manifest schema, generated baseline/acceptance evidence, validation-asset/package validator, ceiling 파일을 열거한다. 각 row는 비어 있지 않은 `asset_id`, `path`, `required`, `lifecycle_state`, `artifact_class`, `route_class_or_null`, `owner_change`, `tracked_required`, `clean_checkout_required`를 가진다. `asset_id`와 canonical path는 각각 유일해야 한다.
* row type/enum은 manifest schema와 integrity core가 모두 검사한다. `artifact_class`는 `python_test`, `validation_support_asset`, `fixture`, `schema`, `evidence`, `binding_record`, `inventory`, `corpus`, `validator`, `ceiling` 중 하나다. `route_class_or_null`은 Python test에만 `current|historical|diagnostic` 중 하나이고 나머지 class에서는 null이다. `owner_change`는 정수 `1..9`, `tracked_required`와 `clean_checkout_required`는 boolean이며 active/sealed required row에서는 둘 다 true여야 한다.
* 기존 clean-checkout common의 Git bytes/identity/tracking/canonical hash/external-root helper와 외부 clone/cleanup lifecycle을 read-only로 부분 재사용한다. 신규 PowerShell validator는 mode source 선택, Iris refactor manifest lifecycle, Lua/PowerShell preflight만 소유한다. 이 경계를 repository-wide governance API로 일반화하지 않는다.
* 이 재사용은 `validation_support_asset` 경계에 머물며 current build core 12나 allowed tooling `4/4` import slot을 확장하지 않아야 한다. Phase 0 closure check가 새 current dependency를 발견하면 Change 2를 시작하지 않고 별도 slot/route review로 보낸다.
* validation asset lifecycle은 다음으로 고정한다.

| Manifest state | Meaning | Denominator treatment |
|---|---|---|
| absent | 소유 Change가 아직 시작되지 않아 row가 없음 | 제외 |
| `required=false`, `lifecycle_state=reserved_future` | future asset 예약 row | 제외 |
| `required=true`, `lifecycle_state=required_active` | 소유 Change에서 파일과 검증이 활성화됨 | required denominator에 포함 |
| `required=true`, `lifecycle_state=sealed` | Change 9 final manifest가 봉인한 active asset | final denominator에 포함 |

* root `sealed=true`는 `reserved_future_count=0`이고 모든 row가 `required=true`, `lifecycle_state=sealed`인 경우에만 허용한다.
* Python wrapper tests만 round3 taxonomy route를 가진다. Lua/PZ harness와 PowerShell runner는 `validation_support_asset`이며 taxonomy test가 아니다. 이들이 emit하는 test case/evidence row가 `route_class`를 가진다.
* Change 2에서는 미래 acceptance asset을 등록하지 않거나 `required=false` 예약 row로만 둔다. 후속 Change가 acceptance asset을 생성하면 같은 changeset에서 row를 `required=true`로 활성화하고 expected ID set/count/hash, manifest generation, exact `.gitignore` rule(필요한 경우)을 함께 갱신한다. denominator 일부만 갱신된 상태는 validator failure다.
* evidence-consuming Python test는 evidence 파일 존재, schema version, expected fixture identity, expected execution-environment row, subject identity, producer identity와 별도 evidence binding을 모두 확인한다. 하나라도 없거나 불일치하면 skip이 아니라 failure다. 실행 환경 부재는 test 내부 skip으로 숨기지 않고 상위 ceiling에서 `unvalidated_but_in_scope` 또는 mandatory axis의 `blocked`로 기록한다.
* 각 validation row를 `validated`, `out_of_scope`, `unvalidated_but_in_scope` 중 하나로 분류한다. `unvalidated_but_in_scope`에는 equivalence, pass, complete claim을 부여하지 않는다.
* `phase1_validation_ceiling.json`은 Change 2가 최초 생성하고 `generation=1`, `last_updated_by_change=2`를 기록한다. 각 mergeable Change 종료 시 같은 파일을 새 generation으로 갱신하며 Change 9가 최종 hash와 classification을 봉인한다.
* Changes 3–6의 runtime-visible subchange는 자신이 건드리는 behavior axis가 `validated` baseline을 가진 경우에만 착수한다. PZ-dependent baseline을 만들 수 없으면 해당 subchange는 blocked이며 source contract만으로 대체하지 않는다.

Validation:

* 현재 tree에 존재하는 pre-refactor behavior만 실제 실행돼 schema-valid baseline을 만든다. 미래 acceptance row count는 baseline denominator에서 `0`이어야 한다.
* standalone row는 VM identity와 dialect classification을 가지며, 승격 조건을 충족하지 않은 row는 `auxiliary_standalone`을 유지한다.
* PZ-dependent baseline이 필요한 runtime surface는 PZ evidence 없이는 `validated`가 될 수 없다.
* Python test case와 emitted evidence row는 current, historical, diagnostic 중 route class를 가진다. support asset 자체는 artifact class를 가진다.
* current-route에 추가하는 경우 closure/allowed tooling을 암묵 확장하지 않는다.
* negative fixture가 의도한 실패를 내고 protected surface를 수정하지 않음을 검증한다.
* asset validator negative matrix는 manifest 없음, invalid JSON/schema version/generation/sealed flag, `assets` property 없음, non-array/empty `assets`, required denominator 0·count/ID/hash mismatch, non-ASCII/absolute/non-canonical path, directory path, empty/non-ASCII ID, actual/expected duplicate path·ID, non-ordinal declared ID order, missing/invalid row field type·enum, invalid lifecycle, future row의 잘못된 activation, sealed manifest의 reserved row를 모두 non-zero로 거부한다.
* `StagedChangeset` negative matrix는 `working-tree manifest=current, index manifest=stale, new asset와 allow rule만 staged`인 경우와 `working-tree validator hash != index validator hash`인 경우를 포함하며 둘 다 non-zero여야 한다.
* Section 7 asset validator가 각 mode가 지정한 source에서 manifest JSON text를 취득한 뒤 integrity core에 넘기고, local candidate, staged changeset, clean checkout 단계별 required asset 상태를 fail-closed로 검사해야 한다. required asset을 0건 검사한 성공은 허용하지 않는다.
* 세 characterization Python test는 대응 JSONL 없음, schema 불일치, fixture/environment/subject/producer/binding identity 누락 fixture에서 모두 실패하며 skip count는 0이어야 한다.
* CleanCheckout negative test는 잘못된 target commit, repository 내부/상위 work·result root, dirty materialized checkout, cleanup 실패를 각각 non-zero로 처리하고 원본 worktree status/hash가 전후 동일함을 요구한다.
* disposable package validator와 existing package pre/post no-mutation check가 첫 production mutation 전에 exit `0`이어야 한다.
* evidence와 binding에는 asset path, tracked/ignored 상태, subject/producer identity, interpreter identity, time axis, route/artifact class, test count, closed artifact SHA-256가 포함된다.
* 공통 infrastructure gate는 전체 PASS여야 한다. 그 뒤 Changes 3–6의 runtime-visible subchange는 자신과 연결된 baseline axis가 `validated`인 경우에만 착수하며 unrelated 미검증 axis는 해당 subchange의 blocker가 아니다. Change 9 integrated closeout은 모든 mandatory axis를 다시 요구한다.

---

### Change 3 — Phase 2: Description API Single Execution Path

Purpose:

`Description.lua` 공개 API의 중복 generation 경로를 제거하고, runtime Generator의 존속 여부를 별도 증거 게이트로 분리한다.

Files:

* `Iris/media/lua/client/Iris/API/Description.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/Ordering.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/Templates.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua`
* `Iris/media/lua/client/Iris/Logic/IrisDesc/TagParser.lua`
* Change 2 pre-refactor description characterization evidence
* `Iris/_dev/media/lua/client/Iris/Dev/DescriptionAcceptanceHarness.lua` (new)
* `Iris/build/description/v2/tests/test_iris_description_single_path_acceptance.py` (new)
* `Iris/_docs/refactor/core_refactor/phase2_description_acceptance.jsonl`
* `Iris/_docs/refactor/core_refactor/phase2_description_acceptance.binding.json`
* `Iris/_docs/refactor/core_refactor/phase2_before_after_matrix.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json` (additive update)
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json` (generation update)
* `.gitignore` exact rule `!Iris/build/description/v2/tests/test_iris_description_single_path_acceptance.py`
* `Iris/_docs/refactor/core_refactor/phase2_generator_disposition.md`

Implementation Notes:

Mandatory branch:

* `getDescriptionBlocks()`를 generation의 단일 구현 경로로 둔다.
* `getDescription()`는 `getDescriptionBlocks()`의 결과를 기존 separator와 fallback 규칙으로 join한다.
* `getDescriptionForItem()`과 기존 caller signature, return type, nil/error fallback을 유지한다.
* duplicate dependency load, tag lookup, protected call, debug message를 한 번만 수행한다.
* 같은 changeset에서 Description single-path post-refactor acceptance test를 추가한다. Change 2 baseline에는 이 미래 test가 포함되지 않는다.
* before/after 관계는 기본 `preserve_exact`이며, pre-refactor Description baseline과 target acceptance가 모두 PASS해야 mandatory branch가 완료된다.

Conditional full-removal branch:

* Phase 0에서 current Generator input corpus를 exact row set으로 열거해 `generator_parity_corpus.json`에 full type, tags, primary subcategory, source identity, row count를 고정할 수 있어야 한다.
* Description bytes와 ordering은 dialect-sensitive이므로 열거된 전체 corpus를 실제 PZ/Kahlua harness로 실행해 모든 row의 block ordering, text bytes 또는 사전 승인된 normalization parity가 일치한 경우에만 `Logic/IrisDesc/Generator.lua`와 하위 runtime generation을 제거 대상으로 연다. standalone 결과는 auxiliary evidence일 뿐 full-removal 승인 근거가 아니다.
* corpus를 완전히 열거할 수 없거나 전체 corpus를 실행할 수 없으면 full removal은 자동으로 `deferred_by_design`이다. 대표 fixture는 mandatory facade regression에는 사용할 수 있지만 full removal 승인 근거가 아니다.
* Layer 3 body가 subcategory template description을 자동 대체한다고 가정하지 않는다. Browser/Wiki에서 실제 소비 목적이 다르면 Generator를 compatibility implementation으로 유지한다.
* 제거 시에도 `Description` facade는 유지하며, offline data adapter가 같은 API를 제공한다.
* parity가 불완전하면 full removal은 `deferred_by_design`으로 닫고 mandatory branch만 완료한다. 이것은 계획 실패가 아니라 명시적 closeout 분기다.

Validation:

* 공개 함수별 before/after 반환값과 block ordering이 동일하다.
* mandatory branch는 대표/negative fixture parity를 요구한다. full-removal branch는 pinned current corpus 전수 parity와 `0` mismatch를 요구한다.
* generation 실패, tags missing, item missing의 fallback과 log cardinality를 비교한다.
* protected current Layer 3/public text hash는 변하지 않는다.
* acceptance asset 전체가 파일 생성과 같은 changeset에서 manifest `required=true`/`required_active`로 활성화되고 expected ID set/count/hash와 generation이 갱신되며, `test_iris_description_single_path_acceptance.py` exact unignore가 존재한다.
* acceptance Python test는 대응 JSONL 없음, schema/fixture/PZ environment/subject/producer/binding identity 불일치를 skip하지 않고 failure로 처리한다.

---

### Change 4 — Phase 3: Browser Selection, BrowserData Build-State, Search, and Logging

Purpose:

Browser의 반복 선택 처리와 `IrisBrowserData` build-state를 명시화하고, 결과를 바꾸지 않는 범위에서 검색·folded count 비용을 줄인다. `IrisMain` 전체 초기화 상태는 변경하지 않는다.

Files:

* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* Change 2 pre-refactor Browser characterization evidence
* `Iris/_dev/media/lua/client/Iris/Dev/BrowserAcceptanceHarness.lua` (new)
* `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py` (new)
* `Iris/_docs/refactor/core_refactor/phase3_browser_acceptance.jsonl`
* `Iris/_docs/refactor/core_refactor/phase3_browser_acceptance.binding.json`
* `Iris/_docs/refactor/core_refactor/phase3_before_after_matrix.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json` (additive update)
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json` (generation update)
* `.gitignore` exact rule `!Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`

Implementation Notes:

* `resolveSelectedPayload(list, eventItem)` helper를 만들어 event payload 우선, selected-index fallback, invalid selection nil의 순서를 단일화한다.
* category/subcategory/item handler는 helper 결과만 소비한다. 상태 전이는 `from`, `to`, `reason`, stable identity만 compact log로 남긴다.
* 전체 selected table key/value dump는 제거하거나 명시적 verbose diagnostic flag 아래로 제한한다. 일반 debug mode의 로그량을 item 수에 비례시키지 않는다.
* `IrisBrowserData`는 `getBuildState()`, `isReady()`, `ensureReady()` 공개 상태 계약을 제공한다. `IrisBrowserBase`, `IrisBrowser`, query facade와 Phase 0에서 발견한 모든 consumer는 이 API만 사용한다.
* internal state는 최소 `uninitialized`, `building`, `ready`, `retryable_failed`를 가진다. `ensureReady()`는 `building` 재진입을 중복 build로 만들지 않고 상태/이유를 반환한다.
* `_built` boolean을 compatibility field로 임시 유지한다면 state와 boolean은 private `setBuildState()` 한 곳에서만 함께 쓴다. `ready`와 승인된 `degraded_ready`만 true가 될 수 있으며 consistency guard가 불일치를 fail-loud로 보고한다.
* repository guard는 bare `_built` token이 아니라 `IrisBrowserData._built` 또는 resolved `IrisBrowserData` identity를 동반한 direct read/write만 검사한다. `IrisFixingIndex._built`, `IrisMoveablesIndex._built`, `IrisRecipeIndex._built` 같은 다른 모듈의 자기 상태는 위반이 아니다.
* guard는 `IrisBrowserData.lua`의 single writer와 명시된 compatibility allowlist 외의 qualified access를 금지한다. 이 source guard는 runtime behavior 대용이 아니라 hard compatibility boundary다.
* 핵심 dependency 부재 상태를 `ready`로 표시하지 않는다. 재시도 시 이전 partial cache를 원자적으로 교체한다.
* `retryable_failed`의 retry trigger와 event는 Phase 0 caller inventory에서 정한 `IrisBrowserBase.ensureBrowserDataBuilt()`/Browser open 경로로 고정한다. 숨은 tick retry는 추가하지 않는다.
* `degraded_ready`는 optional dependency failure에만 허용한다. `getBuildState()`가 failure code와 dependency identity를 반환하고 dev/user log에서 관찰 가능해야 하며, reset/retry 조건을 명시한다. required dependency 실패와 같은 성공 상태로 취급하지 않는다.
* build 시 item마다 normalized display name/full type search key를 한 번 계산한다. 검색 결과의 display name, location, 정렬 규칙은 유지한다.
* folded count cache는 VariantIndex의 canonical grouping 결과를 key로 사용하고 build generation이 바뀔 때만 invalidate한다.
* `StaticData` negative cache는 세션 중 불변인 optional generated module에만 적용한다. dev/test reload를 위한 reset hook과 failure reason을 제공한다.
* 기존 `ensureDeps()`를 무조건 하나로 합치지 않는다. Browser, MapIcon 등 각 consumer의 필수/선택 dependency 차이를 먼저 표로 만든 뒤 공통 loader가 실제로 동일한 경우만 공유한다.
* 같은 changeset에서 post-refactor state/selection/search acceptance를 추가한다. Change 2의 current `_built` baseline을 target state-machine PASS로 사용하지 않는다.
* before/after matrix는 selection/search/output parity를 `preserve_exact`로, dependency 누락 시 empty-success에서 `retryable_failed`로 바뀌는 동작을 명시적 `approved_change`로 분류한다.

Validation:

* 선택 fallback matrix의 결과가 기존 valid-path 동작과 일치한다.
* critical dependency가 뒤늦게 준비되면 failed 상태에서 ready로 복구된다.
* search fixture 결과, 정렬, classification location이 before/after 동일하다.
* 같은 query 반복 시 normalization 호출 감소는 standalone stub counter 또는 Change 2의 명시적 `_dev` instrumentation으로 확인한다. counter가 구현되지 않으면 호출 횟수·성능 개선 claim만 보류하며 selection/search/build-state functional acceptance는 실패시키지 않는다.
* build-state 네 전이, `building` 재진입, boolean compatibility consistency를 actual standalone Lua와 PZ Browser-open path에서 검증한다.
* 로그는 동일 전이를 식별할 수 있으면서 전체 payload dump를 만들지 않는다.
* Change 2 pre-refactor matrix와 Change 4 post-refactor acceptance가 모두 PASS하고, `approved_change` row가 Phase 0 decision과 일치해야 완료한다.
* acceptance assets는 파일 생성과 같은 changeset에서 manifest `required=true`/`required_active`로 활성화하고 expected ID set/count/hash와 manifest/ceiling generation을 갱신한다.
* acceptance Python test는 대응 JSONL 없음, schema/fixture/PZ environment/subject/producer/binding identity 불일치를 skip하지 않고 failure로 처리한다.

---

### Change 5 — Phase 4: Shared Item Detail View Model and Incremental Scroll

Purpose:

Browser와 Wiki의 사실 추출 중복을 제거하되 UI ownership을 합치지 않고, 상세 화면 scroll마다 widget을 재생성하는 경로를 분리한다.

Files:

* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua` (new)
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
* `Iris/media/lua/client/Iris/Util/IrisItemAccess.lua`
* `Iris/media/lua/client/Iris/Util/IrisObjectAccess.lua`
* Change 2 pre-refactor Browser/Wiki detail characterization evidence
* `Iris/_dev/media/lua/client/Iris/Dev/DetailAcceptanceHarness.lua` (new)
* `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py` (new)
* `Iris/_docs/refactor/core_refactor/phase4_detail_acceptance.jsonl`
* `Iris/_docs/refactor/core_refactor/phase4_detail_acceptance.binding.json`
* `Iris/_docs/refactor/core_refactor/phase4_before_after_matrix.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json` (additive update)
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json` (generation update)
* `.gitignore` exact rule `!Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py`

Implementation Notes:

* 새 view model은 read-only table을 반환하며 다음 raw facts를 한 번만 수집한다.
  * identity: full type, display name, module, item type
  * core: weight, category/subcategory, tags
  * food/weapon/literature/moveable 등 type-specific raw values
  * Layer 3 display payload와 adoption-aware availability
  * UseCase/capability compatibility projection에 필요한 raw identifiers
* view model은 추천, 우선순위, 품질 판정, compare score를 만들지 않는다.
* Browser와 Wiki는 동일 model을 입력으로 받지만 각자의 label, button, navigation, interaction handler를 유지한다.
* `IrisWikiSections`의 legacy/new renderer family는 caller inventory 후 model-based renderer로 순차 migration한다. 외부 caller가 남은 함수는 compatibility wrapper로 유지하고 deprecation 근거를 기록한다.
* food 단위는 Phase 1 결과로 raw unit과 각 기존 display formatter를 먼저 기술한다. 한 경로의 `* 100`을 추측으로 다른 경로에 복사하지 않는다.
* Phase 1이 기존 표시 오류를 확인하면 Phase 0 decision matrix에서 `preserve_existing_behavior`, `fix_in_separate_approved_changeset`, `split_out_of_this_plan` 중 하나를 선택한다. view-model migration에 bug fix를 조용히 섞지 않는다.
* `IrisBrowserDetail`을 content rebuild와 scroll offset 적용으로 나눈다. item identity나 locale이 바뀔 때만 content를 rebuild하고 wheel event는 기존 child의 위치/clip만 갱신한다.
* PZ UI 제약으로 child 재배치가 불가능한 경우, 최소한 immutable section model을 재사용하고 event handler/expensive data collection은 재실행하지 않는 fallback을 채택한다.
* 같은 changeset에서 view-model, shared raw field, availability, scroll/click target post-refactor acceptance를 추가한다. 아직 존재하지 않는 view model을 Change 2 baseline에서 실행하지 않는다.
* before/after matrix는 raw facts/section inclusion을 기본 `preserve_exact`로 두고, current full rebuild에서 incremental scroll로의 변화는 명시적 `approved_change`로 기록한다. food bug disposition은 Phase 0 선택과 분리한다.

Validation:

* 같은 item의 Browser/Wiki shared field가 동일한 raw value와 availability state를 가진다.
* KO/EN locale에서 label은 달라도 raw fact와 section inclusion rule은 일치한다.
* food fixture의 PZ getter raw value, model value, formatter output 관계가 명시된 contract와 일치한다.
* 연속 wheel event의 child identity, click target, visual scroll 범위는 PZ in-game harness에서만 검증한다. 실행하지 못하면 `unvalidated_but_in_scope`이며 incremental-scroll subchange를 완료로 닫지 않는다.
* expensive build counter를 사용한다면 Change 2의 standalone stub 또는 명시적 `_dev` instrumentation asset과 evidence row를 함께 제공한다. 그렇지 않으면 counter 기반 성능 claim만 보류하며 shared raw-field, section, food, scroll/click functional acceptance 자체를 counter 부재로 실패시키지 않는다.
* recipe/capability button과 item navigation은 기존 target과 동일하게 동작한다.
* Change 2 pre-refactor detail/scroll baseline과 Change 5 post-refactor acceptance가 모두 PASS해야 하며 PZ widget axis가 없으면 incremental-scroll subchange는 완료할 수 없다.
* acceptance assets는 파일 생성과 같은 changeset에서 manifest `required=true`/`required_active`로 활성화하고 expected ID set/count/hash와 manifest/ceiling generation을 갱신한다.
* acceptance Python test는 대응 JSONL 없음, schema/fixture/PZ environment/subject/producer/binding identity 불일치를 skip하지 않고 failure로 처리한다.

---

### Change 6 — Phase 5: Legacy API, Global Data, and Taxonomy Boundary

Purpose:

실제 사용 중인 compatibility API를 보존하면서 caller가 없는 global/legacy surface만 증거에 따라 축소한다.

Files:

* `Iris/media/lua/client/Iris/IrisAPI.lua`
* `Iris/media/lua/client/Iris/API/UseCases.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserClassificationIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisData.lua`
* `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* `Iris/_docs/refactor/core_refactor/phase5_compatibility_inventory.md`
* `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`
* Change 2 pre-refactor capability/variant/taxonomy/tooltip characterization evidence
* `Iris/_dev/media/lua/client/Iris/Dev/LegacySurfaceAcceptanceHarness.lua` (new when runtime subchange is selected)
* `Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py` (new when runtime subchange is selected)
* `Iris/_docs/refactor/core_refactor/phase5_legacy_surface_acceptance.jsonl`
* `Iris/_docs/refactor/core_refactor/phase5_legacy_surface_acceptance.binding.json`
* `Iris/_docs/refactor/core_refactor/phase5_before_after_matrix.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json` (additive update)
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json` (generation update)
* `.gitignore` exact rule `!Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py` when created

Implementation Notes:

* repository-wide Lua caller와 supported external API manifest를 분리해 inventory한다. dynamic require와 PZ event registration도 포함한다. 알려지지 않은 전체 외부 mod 호환성을 주장하지 않는다.
* caller inventory, docs clarification, static wrapper classification은 read-only/static subchange다. capability, group variants, taxonomy presentation, tooltip result, public facade를 바꾸는 runtime-visible subchange는 관련 Change 2 pre-refactor baseline이 `validated`이기 전에는 착수하지 않는다.
* `IrisBrowserQuery.getGroupVariants()`는 내부 caller 부재와 `IrisData.ItemGroups` 제공 여부를 함께 검증한다.
  * external compatibility가 없으면 함수와 global read를 제거한다.
  * external compatibility 가능성이 있으면 `IrisBrowserVariantIndex` adapter로 구현하고 기존 signature를 유지한다.
* `getCapabilities()`와 `hasCapability()`는 현재 Browser interaction에 사용되므로 즉시 삭제하지 않는다. evidence-driven current outcome과 legacy `can_*` projection을 이름과 module boundary로 구분한다.
* `IrisData = IrisData or {}` global은 generated legacy surface로 취급한다. current consumers를 `StaticData`/module return value로 migration한 뒤에도 external compatibility alias가 필요하면 read-only facade로 제한한다.
* classification/taxonomy 의미 authority는 Classification/Rule 계층에 남는다. `IrisBrowserCategoryIndex.lua`는 기존 category/subcategory code의 presentation projection과 label/translation fallback owner일 뿐 taxonomy authority가 아니다.
* generated `IrisData.lua`와 `IrisClassifications.lua` 사이의 중복은 source authority와 generator를 확인한 뒤에만 축소한다. 손으로 generated table을 병합하지 않는다.
* runtime-visible subchange를 선택하면 같은 changeset에서 Change 6 소유 post-refactor acceptance와 before/after matrix를 추가한다. 기본 관계는 `preserve_exact`이며 승인된 facade deprecation/adapter만 명시적 예외다.

Validation:

* 삭제 또는 adapter 전환 전후 repository caller count와 supported API manifest의 signature/module/global compatibility matrix가 기록된다.
* classification 선택, multi-category item, variant group, tooltip tag 결과가 동일하다.
* missing generated module과 legacy global-only fixture가 fail-loud 또는 documented fallback으로 동작한다.
* runtime에서 semantic inference나 신규 추천이 추가되지 않았음을 확인한다.
* runtime-visible subchange는 관련 pre-refactor baseline과 Change 6 acceptance가 모두 PASS해야 완료한다. static-only disposition은 runtime equivalence를 주장하지 않는다.
* 생성된 acceptance assets는 파일 생성과 같은 changeset에서 manifest `required=true`/`required_active`로 활성화하고 expected ID set/count/hash와 manifest/ceiling generation을 갱신한다.
* acceptance Python test는 대응 JSONL 없음, schema/fixture/PZ environment/subject/producer/binding identity 불일치를 skip하지 않고 failure로 처리한다. PZ 환경이 없어 runtime subchange를 선택할 수 없는 경우 test skip 대신 해당 subchange를 `blocked` 또는 `unvalidated_but_in_scope`로 남긴다.

---

### Change 7 — Phase 6: Bounded Build Tool Decomposition

Purpose:

현재 재현성과 current-route governance를 보존하면서 대형 build tooling의 순수 계약, serialization, filesystem, orchestration 책임을 제한적으로 분리한다.

Files:

Initial reviewed targets:

* `Iris/build/description/v2/tools/build/public_text_quality_acceptance.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py` (caller/family inventory 우선)
* `Iris/build/description/v2/tools/common/paths.py`
* `Iris/build/description/v2/tools/common/`의 승인된 신규 leaf modules
* `Iris/test/validate_disposable_package.ps1` (Change 2 prerequisite; existing validation input)
* 관련 current/historical/diagnostic tests
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `.gitignore`의 exact allowlist rows if required

Implementation Notes:

* `compose_layer3_text.py`와 6개 보조 모듈은 이미 분해된 current core이므로 residual defect가 없는 한 변경하지 않는다.
* `dvf_3_3_registry_authority_canonical_closure.py`와 sealed historical/reproduction script family는 initial target에서 제외한다.
* 함수 inventory를 다음 책임으로 분류한다.
  * pure schema/contract validation
  * canonical serialization and hashing
  * protected path and long-path filesystem handling
  * domain evaluation/metrics
  * orchestration, CLI parsing, exit/failure mapping
* 기존 `compose_layer3_io.py`, `tools/common/paths.py`, `naturalization_compiler_identity.py`와 책임이 겹치는지 먼저 검사한다. 동일 의미가 아니면 억지로 합치지 않는다.
* extraction은 leaf-first로 수행한다. 새 leaf는 stdlib-only 또는 명시된 단방향 dependency만 가지며 build script를 역으로 import하지 않는다.
* 기존 entrypoint 파일과 public import symbol은 compatibility wrapper로 유지한다. import blast radius는 Phase 0 fresh inventory의 exact caller set을 사용하며 과거 고정 숫자에 의존하지 않는다.
* public text tool의 protected-foundation, policy, human-review, official-attempt phases는 도메인 경계를 보존한다. 단순 파일 크기 감소를 위해 phase ownership을 섞지 않는다.
* exporter는 adoption contract, registry compatibility preflight, Lua serialization, chunk bundle validation, write orchestration을 별도 경계로 나누되 최종 writer는 기존 entrypoint 한 곳으로 유지한다.
* allowed tooling은 현재 `4/4`, 잔여 slot 0이다. 신규 leaf가 current route에 필요하면 다음 중 하나를 명시적으로 선택한다: `max_allowed_modules` 상향 승인, 기존 slot 교체 승인, current-route가 import하지 않는 leaf로 제한, `deferred_by_design`.
* 신규 helper를 current-route에서 import하려면 exact module, owner class, caller, reason, 선택한 slot disposition을 별도 review하고 manifest에 반영한다. current core count 12는 유지한다.
* historical route가 old import path를 요구하면 compatibility wrapper를 보존한다. historical reproduction을 current code style에 맞추기 위해 대량 수정하지 않는다.
* package validation은 `Iris/test/validate_disposable_package.ps1`를 통해 checkout 밖의 새 GUID output root에서만 실행한다. 기존 `Iris/build/package`는 writer target이 아니며 read-only pre/post hash 비교 대상이다.

Validation:

* 모든 기존 CLI의 arguments, default path, stdout/stderr class, exit code, negative failure가 동일하다.
* canonical JSON/JSONL/Lua bytes, chunk ordering, hashes, package projection identity가 동일하다.
* import graph에 cycle과 closure bypass가 없다.
* current, historical, diagnostic route를 각각 실행하고 결과를 분리 보고한다.
* 신규 helper가 승인된 allowlist와 `.gitignore` exact rule에 모두 나타나며 clean checkout에서 누락되지 않는다.
* live runtime, existing package peer, disposable candidate package identity를 별도 row로 보고하고 existing package pre/post hash change가 0인지 검증한다.

---

### Change 8 — Optional Phase 7: Repository Role Manifest and Evidence-Driven Disposition

Purpose:

core runtime refactor와 독립된 optional workstream으로 current/historical/package/staging/temporary copy의 역할을 찾기 쉽게 만들고, 증명된 disposable residue만 별도 changeset에서 안전하게 정리한다.

Files:

* `Iris/_docs/refactor/core_refactor/phase0_repository_role_inventory.json` (Phase 0 파일을 갱신; 중복 manifest를 만들지 않음)
* `Iris/_docs/refactor/core_refactor/phase7_disposition_report.md`
* `Iris/build/description/v2/staging/`의 승인된 대상만
* `Iris/build/package/` (read-only existing package role/hash input)
* root `.tmp/`, root `.tmp_tests/`, `Iris/build/description/v2/.tmp_tests/`, test root 아래 temporary directories, `console_log.txt` only if classified disposable
* `.gitignore` only for exact approved role projections
* `Iris/build/description/v2/tools/build/INVENTORY.md`

Implementation Notes:

* Phase 0의 `phase0_repository_role_inventory.json`을 writer, consumer, reproduction command, package reachability, required-validation reference로 보강한다. Phase 7용 중복 role manifest를 만들지 않는다.
* 동일 이름의 `IrisLayer3DataChunks.lua`, chunks, `IrisMain.lua` copy마다 content hash와 route reachability를 기록한다.
* disposition 규칙은 다음과 같다.
  * current authority/current package/required sealed evidence: in-place preserve
  * historical reproduction: 명시된 route와 reproduction record를 유지; 위치 변경은 별도 path migration 증거가 있을 때만
  * regenerable projection: generator, input hash, exact reproduction이 모두 검증된 경우 clean/rebuild 가능
  * disposable local residue: consumer 0, tracked required reference 0, package reachability 0, reproduction requirement 0일 때만 삭제 후보
  * unresolved: 보존
* archive/delete eligible 집합이 0이면 no-op closeout을 정상 결과로 기록한다.
* 열람 불가능하거나 permission/long-path 문제로 검사하지 못한 대상은 삭제하지 않고 `unresolved`로 유지한다.
* test root는 먼저 logical runner/taxonomy로 정규화한다. physical 이동은 import path, docs, clean-checkout, historical route를 모두 갱신할 별도 필요가 확인된 경우에만 수행한다.
* `.gitignore`의 broad relaxation이나 filename-glob delete rule을 금지한다. manifest 변경과 1:1 대응하는 exact rule만 허용한다.
* material deletion은 core runtime changeset과 분리된 별도 승인 changeset에서만 수행하고, 대상 path/hash/복구 경로를 사전에 기록한다.
* 이 optional workstream의 no-op, `deferred_by_design`, unresolved non-current residue는 mandatory Changes 1–5의 closeout을 지연시키지 않는다. current/package/required-evidence 충돌을 발견한 경우에만 core closeout을 block한다.

Validation:

* 모든 disposition row는 evidence pointer와 reversible 여부를 가진다.
* disposable package candidate가 current source만 소비하며 historical/probe copy를 포함하지 않음을 검사한다. 기존 package peer는 수정하지 않는다.
* current-route required artifacts가 이동/삭제 대상에 포함되지 않는다.
* clean checkout에서 current tests, package, required manifests가 동일하게 해석된다.

---

### Change 9 — Phase 8: Integrated Closeout and Re-entry Guards

Purpose:

각 phase의 결과를 하나의 closeout으로 묶고, 이후 변경이 제거된 중복이나 forbidden authority path를 되살리지 못하게 한다.

Files:

* `Iris/_docs/refactor/core_refactor/final_closeout.md`
* `Iris/_docs/refactor/core_refactor/final_validation_matrix.json`
* `Iris/_docs/refactor/core_refactor/protected_surface_no_mutation_report.json`
* `Iris/_docs/refactor/core_refactor/final_supported_api_compatibility_report.json`
* `Iris/_docs/refactor/core_refactor/final_package_identity_report.json`
* `Iris/_docs/refactor/core_refactor/final_evidence_binding_report.json`
* `Iris/_docs/refactor/core_refactor/phase1_validation_ceiling.json` (final generation seal)
* `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json` (final tracking seal)
* 필요한 경우 승인된 focused current-route validation
* 필요한 경우 `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`의 additive update

Implementation Notes:

* phase별 plan-specific state와 Section 12의 standard closeout state 환원 결과를 함께 기록한다.
* Generator full removal, global alias removal, staging cleanup처럼 조건부인 branch는 선택되지 않았다는 사실만으로 failure로 만들지 않는다. 대신 mandatory branch와 보존 근거가 완료돼야 한다.
* source-string guard는 이름이나 파일 배치가 아니라 다음 hard boundary만 감시한다.
  * current runtime은 chunk-only authority를 사용한다.
  * runtime이 source facts/decisions/rendered JSON을 읽지 않는다.
  * Browser/Wiki 공유 model이 inference/recommendation policy를 만들지 않는다.
  * current core/allowed tooling이 manifest를 우회하지 않는다.
  * package가 historical/probe/stale monolith를 포함하지 않는다.
* closeout 문구는 runtime behavior pass, build contract pass, package identity pass, public-text no-mutation을 별도 축으로 보고한다. bare `PASS`를 전체 완성으로 확장하지 않는다.
* 각 validation axis는 `validated`, `out_of_scope`, `unvalidated_but_in_scope` 중 하나여야 한다. mandatory axis에 `unvalidated_but_in_scope`가 남으면 behavior equivalence와 plan `complete`를 금지한다.
* supported API compatibility는 Phase 0 manifest에 열거된 surface만 평가한다.
* package report는 live runtime, existing read-only package peer, disposable candidate package를 별도 identity row로 유지하고 existing peer의 pre/post hash change가 0임을 요구한다.
* Change 2가 만든 validation ceiling의 generation chain을 Changes 3–7의 갱신과 대조하고, `sealed_by_change=9`, final generation, content hash를 기록한다.
* validation asset manifest의 모든 reserved future row를 active/sealed 또는 명시적 제거로 해소한다. root를 `sealed=true`로 전환하고 final `expected_required_count`, ordinal required asset ID set/hash, generation, previous hash를 closeout에 봉인한다.
* final evidence binding report는 각 evidence의 subject commit/tree, producer base/overlay, evidence SHA-256과 검증 대상 구현 commit을 `final_changeset_commit`으로 연결한다. 이 record가 들어가는 closeout commit 자체를 record 내부에 요구하지 않는다.
* Change 9는 `seal candidate commit → exact commit CleanCheckout → terminal binding attestation commit` 순서로 닫는다. terminal binding은 seal candidate의 commit/tree, receipt, canonical result, stdout, stderr, manifest와 validator blob의 SHA-256 및 disposable-checkout cleanup 상태를 기록한다. 이 evidence-only attestation commit은 새 runtime subject로 재귀 해석하지 않고 sealed manifest/runtime 내용을 바꾸지 않는다.
* `final_evidence_binding_report.json`은 seal candidate 이후에만 생성 가능한 terminal closeout attestation이므로 sealed candidate manifest의 required denominator에 다시 넣지 않는다. 이는 검증 asset 누락 예외가 아니라 자기 결과를 자기 입력으로 만드는 순환을 피하기 위한 post-seal `EXECUTION_CONTRACT.md` historical-trace record이며, 후속 attestation commit에서 tracked 상태를 요구한다.
* pre-refactor characterization과 각 Change 소유 post-refactor acceptance의 time axis/denominator가 섞이지 않았는지 검증한다.

Validation:

* Section 7의 automated/manual matrix가 모두 결과와 evidence path를 가진다.
* protected surface before/after hash 차이가 0이다. 승인된 변경이 있다면 exact changed set과 writer chain을 별도 기록한다.
* disposable package candidate만 생성·정리됐으며 existing package peer는 변경되지 않았다.
* final validation asset manifest 자체가 supported schema이고 non-empty exact denominator, unique non-empty ASCII ID/path, ordinal ID set/hash를 가지며 `reserved_future_count=0`이고 모든 row가 `required=true`, `lifecycle_state=sealed`다.
* final manifest를 대상으로 index manifest와 index validator identity가 기록된 StagedChangeset, target implementation commit의 fresh CleanCheckout validator가 모두 exit `0`이고, 모든 required path가 tracked, non-ignored, clean-checkout present이며 올바른 route/artifact class와 test discovery를 가진다.
* evidence binding report의 subject, producer, artifact hash, final implementation changeset 연결이 비순환이고 각 ceiling claim과 1:1로 일치한다.
* external result root를 정리하기 전에 terminal binding attestation이 추적된 commit으로 materialize됐고 receipt/stdout/stderr/canonical-result hash가 원본 external files와 일치함을 다시 검증한다.
* final Git diff에는 계획 범위 밖 사용자 변경이 섞이지 않는다.

---

## 7. Validation Plan

### Validation Evidence Classification

모든 validation axis는 다음 중 정확히 하나로 보고한다.

| Classification | Meaning | Allowed claim |
|---|---|---|
| `validated` | 명시된 실제 실행기에서 schema-valid evidence가 생성되고 판정자가 성공했다. | 해당 axis에 한해 pass/equivalence claim 가능 |
| `out_of_scope` | Section 2 또는 Validation Limits에서 의도적으로 제외됐다. | 비검증 사실만 기록; 계획 완료를 막지 않음 |
| `unvalidated_but_in_scope` | 계획 범위지만 실행 환경·fixture·판정 증거가 없어 검증하지 못했다. | pass/equivalence/complete claim 금지; mandatory axis면 standard closeout `complete` 금지 |

Validation status와 별도로 evidence role을 `runtime_behavior`, `auxiliary_standalone`, `source_contract`, `static_guard` 중 하나로 기록한다.

* Python source inspection은 `source_contract` 또는 `static_guard`다.
* standalone 실행은 기본 `auxiliary_standalone`이다. VM identity complete, `dialect_sensitive=false`, divergence check 통과, 동일 PZ fixture cross-check 일치가 모두 증명된 경우에만 target runtime observation과 결속한다.
* `runtime_behavior`는 실제 PZ/Kahlua 실행 또는 위 승격 조건을 충족한 exact fixture에만 허용한다.
* `pre_refactor_characterization`과 `post_refactor_acceptance`는 서로 다른 denominator다. 미래 acceptance row를 baseline PASS에 포함하거나 baseline 관찰을 target contract PASS로 재사용하면 validation failure다.

### Evidence Identity Binding

| Identity | Meaning | Storage |
|---|---|---|
| `subject_commit`, `subject_tree`, `subject_worktree_patch_sha256_or_null` | 실제 검증 대상 production/runtime source와 overlay | evidence row |
| `producer_base_commit`, `producer_base_tree`, `producer_worktree_state`, `producer_overlay_sha256_or_null` | harness/runner가 실행된 base 및 working state | evidence row |
| `evidence_sha256` | 닫힌 JSONL artifact bytes의 SHA-256 | 별도 binding record 또는 validation asset manifest |
| `final_changeset_commit` | evidence가 검증한 코드·asset을 담은 구현 commit | 구현 commit 이후 작성하는 Change 9 binding report |

* subject와 producer identity는 독립적으로 검증하고 같음을 전제하지 않는다. dirty overlay는 canonical tracked diff와 required untracked-input identity를 포함한 SHA-256 없이는 재현 가능한 subject/producer로 인정하지 않는다.
* evidence file은 자기 `evidence_sha256`이나 자신을 포함하는 commit을 내부에 쓰지 않는다. hash는 file close 후 외부 binding에 기록하고, `final_changeset_commit`은 검증 대상 구현 commit을 가리키며 이후 closeout record의 자기 commit은 가리키지 않는다.

### Validation Preconditions

다음 preflight가 exit code `0`이어야 해당 검증을 시작한다.

```powershell
Get-Command python -ErrorAction Stop

function Invoke-NativeVersionCapture {
    param([Parameter(Mandatory = $true)][string] $ExecutablePath)

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $ExecutablePath
    $startInfo.Arguments = '-v'
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    if (-not $process.Start()) { throw "failed to start: $ExecutablePath" }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $normalized = (@($stdout.Trim(), $stderr.Trim()) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join "`n"
    $capture = [pscustomobject]@{
        executable_path = $ExecutablePath
        exit_code = $process.ExitCode
        stdout = $stdout
        stderr = $stderr
        normalized_version_output = $normalized
    }
    $process.Dispose()
    return $capture
}

$luaCommand = Get-Command lua -ErrorAction Stop
$luacCommand = Get-Command luac -ErrorAction Stop
$luaVersion = Invoke-NativeVersionCapture -ExecutablePath $luaCommand.Source
$luacVersion = Invoke-NativeVersionCapture -ExecutablePath $luacCommand.Source
if ($luaVersion.exit_code -ne 0) { throw 'lua version preflight failed' }
if ($luacVersion.exit_code -ne 0) { throw 'luac version preflight failed' }
```

* preflight는 PowerShell 5.1 native stderr를 `ErrorRecord`로 해석하지 않도록 stdout/stderr를 별도 redirect한다. 성공 여부는 native process exit code로만 판정하고, 두 stream을 `Trim`한 뒤 stdout→stderr 순서와 LF separator로 만든 normalized version output을 증거에 기록한다.
* preflight artifact는 executable path, implementation, parsed version, 원본 stdout/stderr, normalized version output, selected interpreter policy, target `project_zomboid_b41_kahlua` relation을 기록한다.
* PUC Lua 5.1.x가 가용하면 standalone tier에서 우선한다. 5.4.x만 가용하면 auxiliary tier로 사용할 수 있지만 Kahlua/PZ equivalence를 주장하지 않는다. planning readpoint의 `5.4.8`은 고정 실행 결과가 아니라 재확인 대상이다.
* `lua`는 standalone auxiliary harness, `luac`는 syntax 검사에 사용한다.
* 도구가 없으면 해당 axis는 자동 pass가 아니라 `unvalidated_but_in_scope` 또는 `blocked`다.
* Project Zomboid B41 build, dev overlay, KO/EN locale 준비 여부를 별도 preflight artifact로 기록한다.

### Automated Validation

실행 시작과 각 mergeable phase 종료 시 필요한 범위를 수행하고, 최종 closeout에서 전체 matrix를 다시 실행한다.

Standalone Lua pre-refactor auxiliary characterization:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\test\run_pre_refactor_characterization.ps1 -OutputPath .\Iris\_docs\refactor\core_refactor\phase1_pre_refactor_headless_baseline.jsonl
```

* runner는 선택된 실제 interpreter를 호출하고 JSONL schema, pre-refactor denominator, negative cases, exit code, VM identity를 검증한다.
* 현재 Description, selection, `_built` boolean behavior, search에서 PZ stub을 사용한 항목은 evidence row에 명시한다. 미래 state API/view model acceptance를 실행하지 않는다.
* dialect-sensitive row는 auxiliary로 유지하고 PZ baseline과 별도 보고한다.

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

* current-route contract, required artifact, build closure를 검증한다.
* 기준선 `145/145`는 현재 문서상의 기대값이며, 실행 시 manifest가 승인되어 변경되었다면 새 pinned denominator와 변경 근거를 함께 기록한다.

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical
```

* build helper extraction이나 compatibility wrapper 변경이 historical reproduction에 닿을 때 필수다.

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic
```

* diagnostic 결과는 advisory와 blocking을 구분해 기록한다.

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

* 전체 v2 test discovery는 route runner와 별도 결과로 보고한다. historical/diagnostic test가 포함될 수 있으므로 current-route authority와 동일시하지 않는다.
* characterization/acceptance Python test는 대응 evidence JSONL과 binding record를 필수 입력으로 취급한다. 파일 부재, JSONL/schema 오류, expected fixture 또는 execution-environment row 부재, subject/producer identity 또는 evidence SHA-256 binding 불일치는 assertion failure이며 skip으로 환원하지 않는다.
* Change 2 진행 중 owner eligibility는 exact characterization test module과 axis denominator를 지정한 focused invocation으로 판정한다. PZ 같은 실행 환경이 준비되지 않은 경우 evidence-consuming test를 skip하지 않고 해당 axis invocation만 non-zero로 닫아 `unvalidated_but_in_scope` 또는 `blocked`로 기록한다. 이미 validated인 다른 axis와 공통 infrastructure PASS는 유지된다.
* 전체 v2 discovery와 모든 mandatory characterization을 묶은 integrated invocation은 Change 2 standard `complete` 및 Change 9 closeout gate다. 이 full invocation의 non-zero는 전체 완료를 막지만 unrelated validated axis의 이미 부여된 후속 진행 자격을 소급 취소하지 않는다.

Validation asset manifest integrity core:

```powershell
function Test-ValidationAssetManifestIntegrity {
    param(
        [Parameter(Mandatory = $true)][string] $ManifestJsonText,
        [Parameter(Mandatory = $true)][string] $SourceLabel
    )

if ([string]::IsNullOrWhiteSpace($ManifestJsonText)) {
    throw "empty asset manifest content: $SourceLabel"
}
try {
    $assetManifest = $ManifestJsonText | ConvertFrom-Json -ErrorAction Stop
}
catch {
    throw "invalid asset manifest JSON: $SourceLabel"
}

if ((-not ($assetManifest.schema_version -is [int])) -and
        (-not ($assetManifest.schema_version -is [long]))) {
    throw 'schema_version must be an integer'
}
if ([long]$assetManifest.schema_version -ne 1) {
    throw 'unsupported asset manifest schema_version'
}
if (-not ($assetManifest.sealed -is [bool])) { throw 'sealed must be boolean' }
if (((-not ($assetManifest.generation -is [int])) -and
        (-not ($assetManifest.generation -is [long]))) -or
        [long]$assetManifest.generation -le 0) {
    throw 'generation must be a positive integer'
}
if (-not ($assetManifest.PSObject.Properties.Name -contains 'assets')) {
    throw "asset manifest missing 'assets' array"
}
if (-not ($assetManifest.assets -is [System.Array])) { throw "'assets' must be an array" }
$assets = @($assetManifest.assets)
if ($assets.Count -eq 0) { throw "'assets' must not be empty" }

if (((-not ($assetManifest.expected_required_count -is [int])) -and
        (-not ($assetManifest.expected_required_count -is [long]))) -or
        [long]$assetManifest.expected_required_count -le 0) {
    throw 'expected_required_count must be a positive integer'
}
$expectedRequiredCount = [long]$assetManifest.expected_required_count
if (-not ($assetManifest.expected_required_asset_ids -is [System.Array])) {
    throw 'expected_required_asset_ids must be an array'
}
$declaredExpectedRequiredIdValues = @($assetManifest.expected_required_asset_ids)
$emptyExpectedRequiredIds = @($declaredExpectedRequiredIdValues |
    Where-Object { (-not ($_ -is [string])) -or [string]::IsNullOrWhiteSpace($_) })
if ($emptyExpectedRequiredIds.Count -ne 0) {
    throw 'expected required asset ID must not be empty'
}
$declaredExpectedRequiredIds = [string[]]@($declaredExpectedRequiredIdValues)
$duplicateExpectedRequiredIds = @($declaredExpectedRequiredIds | Group-Object |
    Where-Object Count -gt 1)
if ($duplicateExpectedRequiredIds.Count -ne 0) {
    throw 'duplicate expected required asset ID'
}
$expectedRequiredIds = [string[]]@($declaredExpectedRequiredIds)
[System.Array]::Sort($expectedRequiredIds, [System.StringComparer]::Ordinal)
if (($declaredExpectedRequiredIds -join "`0") -cne
        ($expectedRequiredIds -join "`0")) {
    throw 'expected required asset IDs are not in ordinal order'
}

$requiredRowFields = @(
    'asset_id', 'path', 'required', 'lifecycle_state', 'artifact_class',
    'route_class_or_null', 'owner_change', 'tracked_required',
    'clean_checkout_required'
)
$allowedArtifactClasses = @(
    'python_test', 'validation_support_asset', 'fixture', 'schema',
    'evidence', 'binding_record', 'inventory', 'corpus', 'validator', 'ceiling'
)
$allowedRouteClasses = @('current', 'historical', 'diagnostic')
foreach ($asset in $assets) {
    foreach ($field in $requiredRowFields) {
        if (-not ($asset.PSObject.Properties.Name -contains $field)) {
            throw "asset row missing field '$field': $($asset.asset_id)"
        }
    }
    if ((-not ($asset.asset_id -is [string])) -or
            [string]::IsNullOrWhiteSpace($asset.asset_id)) { throw 'invalid asset_id' }
    if ($asset.asset_id -cnotmatch '^[a-z0-9][a-z0-9._-]*$') {
        throw "asset_id must be lowercase ASCII: $($asset.asset_id)"
    }
    if ((-not ($asset.path -is [string])) -or
            [string]::IsNullOrWhiteSpace($asset.path)) { throw 'invalid asset path' }
    if ($asset.path -cnotmatch '^[A-Za-z0-9._/-]+$' -or
            $asset.path.StartsWith('/') -or $asset.path.EndsWith('/') -or
            $asset.path.Contains('//') -or $asset.path.Contains('\')) {
        throw "asset path must be canonical repository-relative ASCII: $($asset.path)"
    }
    $pathSegments = @($asset.path.Split('/'))
    if (@($pathSegments | Where-Object { $_ -in @('', '.', '..') }).Count -ne 0) {
        throw "asset path contains forbidden segment: $($asset.path)"
    }
    if (-not ($asset.required -is [bool])) { throw 'required must be boolean' }
    if ((-not ($asset.lifecycle_state -is [string])) -or
            $asset.lifecycle_state -notin @('reserved_future', 'required_active', 'sealed')) {
        throw "invalid lifecycle_state: $($asset.asset_id)"
    }
    if ((-not ($asset.artifact_class -is [string])) -or
            $asset.artifact_class -notin $allowedArtifactClasses) {
        throw "invalid artifact_class: $($asset.asset_id)"
    }
    if ($asset.artifact_class -eq 'python_test') {
        if ((-not ($asset.route_class_or_null -is [string])) -or
                $asset.route_class_or_null -notin $allowedRouteClasses) {
            throw "python test requires route class: $($asset.asset_id)"
        }
    }
    elseif ($null -ne $asset.route_class_or_null) {
        throw "non-test asset route must be null: $($asset.asset_id)"
    }
    if (((-not ($asset.owner_change -is [int])) -and
            (-not ($asset.owner_change -is [long]))) -or
            [long]$asset.owner_change -lt 1 -or [long]$asset.owner_change -gt 9) {
        throw "invalid owner_change: $($asset.asset_id)"
    }
    if (-not ($asset.tracked_required -is [bool]) -or
            -not ($asset.clean_checkout_required -is [bool])) {
        throw "tracking flags must be boolean: $($asset.asset_id)"
    }
    if ($asset.required -and $asset.lifecycle_state -notin @('required_active', 'sealed')) {
        throw "invalid active lifecycle: $($asset.asset_id)"
    }
    if (-not $asset.required -and $asset.lifecycle_state -ne 'reserved_future') {
        throw "invalid future lifecycle: $($asset.asset_id)"
    }
    if ($asset.required -and
            (-not $asset.tracked_required -or -not $asset.clean_checkout_required)) {
        throw "active asset must require tracking and clean checkout: $($asset.asset_id)"
    }
}

$duplicateAssetIds = @($assets | Group-Object asset_id | Where-Object Count -gt 1)
if ($duplicateAssetIds.Count -ne 0) {
    throw 'duplicate asset_id'
}
$normalizedAssetPaths = @($assets | ForEach-Object {
    ([string]$_.path).ToLowerInvariant()
})
$duplicateAssetPaths = @($normalizedAssetPaths | Group-Object | Where-Object Count -gt 1)
if ($duplicateAssetPaths.Count -ne 0) {
    throw 'duplicate asset path'
}

$requiredAssets = @($assets | Where-Object { $_.required -eq $true })
$actualRequiredIds = [string[]]@($requiredAssets.asset_id)
[System.Array]::Sort($actualRequiredIds, [System.StringComparer]::Ordinal)
if ($requiredAssets.Count -ne $expectedRequiredCount -or
        $expectedRequiredIds.Count -ne $expectedRequiredCount -or
        ($actualRequiredIds -join "`0") -cne ($expectedRequiredIds -join "`0")) {
    throw 'required asset denominator mismatch'
}
$reservedFutureAssets = @($assets | Where-Object lifecycle_state -eq 'reserved_future')
if ($assetManifest.sealed -and $reservedFutureAssets.Count -ne 0) {
    throw 'sealed manifest contains reserved future asset'
}
$unsealedRequiredAssets = @($requiredAssets | Where-Object lifecycle_state -ne 'sealed')
if ($assetManifest.sealed -and $unsealedRequiredAssets.Count -ne 0) {
    throw 'sealed manifest contains unsealed required asset'
}
$sealedRequiredAssets = @($requiredAssets | Where-Object lifecycle_state -eq 'sealed')
if (-not $assetManifest.sealed -and $sealedRequiredAssets.Count -ne 0) {
    throw 'unsealed manifest contains sealed required asset'
}
$canonicalIds = ($actualRequiredIds -join "`n") + "`n"
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$actualIdHashBytes = $sha256.ComputeHash($utf8NoBom.GetBytes($canonicalIds))
$actualIdHash = [System.BitConverter]::ToString($actualIdHashBytes).Replace('-', '').ToLowerInvariant()
$sha256.Dispose()
if ([string]$assetManifest.expected_required_asset_ids_sha256 -cnotmatch '^[0-9a-f]{64}$') {
    throw 'required asset identity hash must be lowercase SHA-256 hexadecimal'
}
if ($actualIdHash -ne [string]$assetManifest.expected_required_asset_ids_sha256) {
    throw 'required asset identity hash mismatch'
}
return $assetManifest
}
```

위 integrity core는 파일 경로를 직접 읽지 않는다. `Iris/test/validate_validation_assets.ps1`의 mode adapter가 지정 source에서 얻은 exact JSON text와 source label을 넘겨 모든 mode에서 먼저 실행한다. manifest content 없음/parse 실패/schema·generation·sealed mismatch/non-array·empty assets/0 denominator/missing row field/type·enum mismatch/non-ASCII·non-canonical·empty·duplicate ID 또는 path/lifecycle mismatch/non-ordinal ID order/count·ID set·hash mismatch와 sealed manifest의 reserved row는 모두 non-zero다. 실제 file leaf 여부는 validated `RepositoryRoot`를 가진 mode adapter가 별도로 강제한다.

VCS validation stages:

```powershell
$repositoryRoot = [System.IO.Path]::GetFullPath((git rev-parse --show-toplevel).Trim())
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_validation_assets.ps1 -Mode LocalCandidate -RepositoryRoot $repositoryRoot
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_validation_assets.ps1 -Mode StagedChangeset -RepositoryRoot $repositoryRoot
$targetCommit = (git -C $repositoryRoot rev-parse HEAD).Trim()
$workRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("iris-core-refactor-clean-work-" + [guid]::NewGuid().ToString("N"))
$resultRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("iris-core-refactor-clean-result-" + [guid]::NewGuid().ToString("N"))
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_validation_assets.ps1 -Mode CleanCheckout -RepositoryRoot $repositoryRoot -TargetCommit $targetCommit -WorkRoot $workRoot -ResultRoot $resultRoot
```

| Mode | Manifest source and validator identity | Required checks |
|---|---|---|
| `LocalCandidate` | working-tree manifest + working-tree validator | integrity, 모든 active required path가 validated root 아래 `Test-Path -PathType Leaf`, `git check-ignore` non-ignored; 아직 untracked인 상태 자체는 실패 아님 |
| `StagedChangeset` | manifest는 `git show :Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json`; validator는 index blob을 외부 temp에 materialize한 copy | working/index validator SHA-256 일치, index manifest integrity, active required path의 index object type이 `blob`, HEAD 대비 activation과 staged file·allowlist·denominator 원자성 |
| `CleanCheckout` | target commit의 detached external checkout 안 manifest + 같은 commit의 validator | clean checkout identity/manifest integrity, 모든 required path가 validated checkout root 아래 tracked·non-ignored `Test-Path -PathType Leaf`, Python discovery/route, support asset class와 emitted-case route |

`StagedChangeset` source/validator protocol:

* bootstrap은 working-tree `validate_validation_assets.ps1` bytes와 `git show :Iris/test/validate_validation_assets.ps1` bytes의 SHA-256이 같지 않으면 실행을 중단한다.
* `-RepositoryRoot`는 모든 mode에서 mandatory다. validator는 absolute resolved path를 받고 `git -C $RepositoryRoot rev-parse --show-toplevel`의 resolved result와 exact path identity가 같음을 확인한다. 모든 Git·Test-Path 대상은 이 root를 기준으로 resolve하며 외부 materialized validator는 `$PSScriptRoot`나 현재 directory로 repository를 추론하지 않는다.
* index validator bytes는 검증된 repository-external GUID temp path에 materialize하고 그 copy를 `-RepositoryRoot`와 함께 실행한다. 실행 evidence는 validator index blob ID, SHA-256, repository root identity, temp path, cleanup status를 기록한다.
* materialized index validator는 manifest를 반드시 `git show :Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json`에서 읽는다. `HEAD:path`는 activation delta 비교용, working-tree path는 diagnostic comparison용일 뿐 integrity PASS 입력이 아니다.
* index의 required path는 `git cat-file -t :$assetPath` 결과가 `blob`이어야 한다. `tree`, missing object, submodule/gitlink나 다른 object type은 file asset이 아니므로 실패한다.
* Change 2 closeout은 validator index blob/hash를 prerequisite identity로 봉인한다. Changes 3–9에서 validator가 이 identity와 다르면 explicit validator-revision changeset, 전체 negative matrix, manifest generation update 없이는 실패한다.
* working-tree manifest만 최신이고 index manifest가 stale/missing인 fixture, validator working/index hash가 다른 fixture, index manifest만 갱신되고 asset/allow rule이 빠진 fixture를 모두 non-zero로 검증한다.

`CleanCheckout` external lifecycle:

* target은 StagedChangeset을 통과해 commit된 exact implementation commit이며 `git_identity`의 commit/tree를 receipt에 기록한다. staged tree를 clean-checkout commit으로 가장하지 않는다.
* `work_root`와 `result_root`는 기존 `ensure_external_root`로 source checkout의 내부·상위가 아니고 서로 disjoint인 빈 GUID 경로임을 확인한다.
* 기존 clean-checkout lifecycle의 bounded clone/cleanup 알고리즘을 재사용해 `git clone --no-local --no-checkout` 후 target commit을 detached checkout한다. 기존 full-repository gate의 `source checkout 자체가 clean` 전제는 가져오지 않고, Phase 0에서 기록한 pre-existing dirty baseline이 전후 exact same일 것을 요구한다. materialized checkout은 clean하고 HEAD commit/tree가 target과 같을 때만 committed validator를 실행한다.
* `result_root`에 manifest/validator blob ID, required denominator/hash, discovery 결과, source worktree pre/post status, checkout cleanup status를 포함한 receipt, canonical result, stdout, stderr를 기록하고 각 file SHA-256를 계산한다. repository 내부에는 실행 중 evidence를 쓰지 않는다.
* disposable checkout은 success/failure 모두 `finally`에서 exact validated external path만 제거한다. cleanup 실패는 전체 validation failure이며 경로를 receipt에 남긴다.
* `result_root`는 disposable checkout과 별도 생명주기를 가진다. receipt/canonical-result/stdout/stderr hash가 Change 9 terminal binding attestation에 기록되고 그 attestation이 tracked commit으로 영속화됐음을 확인하기 전에는 success result root를 삭제하지 않는다. failure result는 failure disposition record가 동일 hash를 결속할 때까지 보존한다.
* durable binding 직전에 external file hash를 다시 계산해 attestation 값과 exact match를 확인한다. attestation 완료 후 executor가 exact validated result root를 정리하며, cleanup 실패는 closeout failure로 남긴다.
* source worktree의 tracked/non-ignored status와 protected hashes는 실행 전후 같아야 한다. 기존 사용자 dirty row가 있으면 보존할 수 있지만 새 delta는 0이어야 한다.

* `git check-ignore` exit `0`은 ignored failure, exit `1`은 non-ignored continue, 그 외는 Git error failure다. `git ls-files`는 LocalCandidate mode에 사용하지 않고 StagedChangeset/CleanCheckout에서만 tracking 판정에 사용한다.
* manifest는 자기 schema와 validator 자신을 포함해 Python tests, Lua/PZ harness, PowerShell runners, fixtures, evidence/binding schema, package validator, Generator corpus, VM/dialect inventory, validation ceiling, 활성화된 acceptance asset을 포괄한다.
* future row는 Change 2에서 `required=false` 예약 상태이거나 absent여야 한다. 소유 Change의 StagedChangeset mode는 파일, exact allow rule, `required=true` activation, expected ID set/count/hash를 원자적으로 대조한다. Change 9 CleanCheckout mode는 sealed final denominator를 요구한다.

Lua syntax source root:

```powershell
Get-Command luac -ErrorAction Stop
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 -Roots "Iris\media\lua"
```

* 기존 `Iris/build/package`를 검사 root에 포함하지 않는다. production source Lua 전체와 새 view-model module을 검사한다.
* `_dev` harness와 disposable candidate package Lua는 standalone runner와 disposable package validator가 `luac -p`로 별도 검사한다.

Disposable package validation:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_disposable_package.ps1
```

* validator는 기존 `Iris/build/package`의 file/hash manifest를 먼저 read-only로 캡처하고, checkout 밖인지 확인한 새 GUID temp root를 만든다.
* validator 내부의 유일한 package invocation은 다음 형태다. 새 경로이므로 `-Clean`을 사용하지 않는다.

```powershell
$packageCandidateRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("iris-core-refactor-package-" + [guid]::NewGuid().ToString("N"))
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot $packageCandidateRoot -Zip
```

* resolved candidate root가 repository root 또는 기존 package root와 같거나 그 아래면 fail-loud한다.
* live runtime, existing package peer, disposable candidate를 별도 identity row로 비교한다. manifest 1개와 chunk 11개의 exact identity, stale monolith·historical/probe exclusion, 새 runtime module 포함을 확인한다.
* candidate Lua는 candidate root에서 `luac -p`로 검사한다.
* existing package의 pre/post hash change는 `0`이어야 한다. 성공/실패 모두 exact validated candidate root만 정리하며 기존 package를 삭제하거나 덮어쓰지 않는다.
* 이 validator는 Change 2 validation infrastructure로 먼저 생성·추적되며 Change 3의 첫 production mutation 전에 반드시 exit `0`이어야 한다.

Focused validation:

* Change 2 pre-refactor Description/Browser/detail/legacy-surface characterization denominator
* Change 3 Description block/string target acceptance와 negative fallback tests
* Change 4 Browser selection and BrowserData build-state target acceptance
* search/folded count result parity and deterministic ordering tests
* Browser/Wiki detail-model parity tests
* food unit fixture tests
* in-game scroll/click target tests와, 구현된 경우 명시적 dev instrumentation counter
* build CLI golden bytes, hashes, exit/failure tests
* protected source/rendered/runtime/package hash comparison
* clean-checkout import and allowlist projection checks
* 각 구현 Change의 `pre-refactor baseline 관계 matrix + owner-specific post-refactor acceptance PASS`

top-level validation wrapper가 exit code `0`을 반환하고 schema-valid evidence가 생성된 경우에만 해당 validation을 통과했다고 기록한다. 내부 명령의 non-match exit code는 wrapper가 명시적으로 해석하고, ignored/error 상태는 non-zero 또는 throw로 승격한다.

### Validation Ceiling Lifecycle

* Change 2가 `phase1_validation_ceiling.json` generation 1을 생성해 pre-refactor coverage와 미검증 axis를 기록한다.
* Changes 3–7의 각 mergeable phase는 동일 파일의 generation을 1 증가시키고 `last_updated_by_change`, 이전 generation hash, 새/해소/잔존 axis를 기록한다.
* 미래 acceptance는 소유 Change가 실행된 뒤에만 ceiling을 낮출 수 있다. draft나 auxiliary standalone row는 PZ-required ceiling을 해소하지 않는다.
* Change 9는 generation chain과 previous-hash 연결을 검증하고 final generation/hash를 봉인한다.
* validation asset manifest도 독립적인 generation/previous-hash chain을 가진다. required activation마다 expected ID set/count/hash를 같은 generation에서 갱신하며, ceiling이 참조한 evidence asset generation과 manifest generation이 어긋나면 failure다.
* 각 ceiling row는 evidence binding의 subject/producer identity, evidence SHA-256, 해당 구현 Change의 `final_changeset_commit`을 참조한다. evidence가 closeout record 자체의 commit을 요구하는 순환 binding은 failure다.
* Change 9 final generation은 sealed manifest의 `reserved_future_count=0`, StagedChangeset index source label/validator blob, CleanCheckout target commit/tree와 cleanup receipt를 모두 참조한다.

### Manual Validation

Project Zomboid B41에서 production package에 포함되지 않는 `_dev` overlay를 적용하고 `DEBUG + RUN_TESTS_ON_START` 또는 문서화된 dev command를 실행한다. Change 2에서는 `PreRefactorCharacterizationHarness`, 이후에는 각 Change 소유 acceptance harness를 사용하며 time axis와 owner를 JSONL에 기록한다. KO/EN 각각 다음을 확인한다.

* pre-refactor: 현재 `_built` boolean, dependency 누락 시 empty-success, current selection/search/detail/scroll/food/capability/tooltip 결과
* post-refactor Change 4: BrowserData ready, required dependency failure, optional `degraded_ready` reason 노출, Browser 재진입에 의한 retry 성공
* category → subcategory → item 선택과 keyboard/mouse selection fallback
* 이름/full type 검색, 대소문자 검색, 결과 정렬, variant folded count
* food, weapon, literature, moveable, multi-classification item의 Browser 상세와 Wiki context-menu 상세
* Layer 3 adopted/unadopted item의 표시 차이와 empty-section 처리
* recipe/capability interaction button과 target navigation
* 빠른 wheel 반복에서 상세 내용이 깜빡이거나 handler를 잃지 않는지
* 일반 debug mode에서 선택 payload 전체 dump가 반복되지 않는지
* dev harness가 비-dev runtime에 load되지 않는지

Manual result는 fixture identity, time axis, owner change, item full type, locale, PZ version, Kahlua target dialect, 실행 event, input identity, expected, observed, PASS/FAIL 판정자, screenshot/log pointer, commit/tree를 JSONL evidence에 남긴다. PZ widget/scroll/click axis를 실행하지 못하면 `unvalidated_but_in_scope`이며 Changes 4–5의 해당 subchange는 완료로 닫지 않는다.

### Validation Limits

* multiplayer validation은 수행하지 않는다.
* 장시간 세션 memory/leak soak test는 수행하지 않는다.
* supported API manifest 밖의 전체 외부 mod compatibility sweep는 수행하지 않는다.
* B42 runtime validation은 수행하지 않는다.
* Workshop upload, production deployment, release readiness는 검증하지 않는다.
* staging 전체의 역사적 artifact byte reproduction은 Change 8에서 실제 이동/삭제 대상이 생긴 경우에만 해당 대상 범위로 수행한다.
* public text의 언어 품질 재평가는 수행하지 않는다. 이 계획에서는 no-mutation identity만 검증한다.

위 항목은 `out_of_scope`다. 반면 Changes 3–6이 직접 변경하는 PZ-dependent behavior는 실행하지 못했다는 이유로 이 목록에 옮기지 않고 `unvalidated_but_in_scope`로 유지한다.

---

## 8. Risk Surface Touch

### Authority Surface

Runtime description source 선택, taxonomy/global data adapter, build helper allowlist가 authority처럼 오인될 위험이 있다. current Layer 3 chunk bundle, DVF source/rendered writer, package writer는 변경하지 않는다. 새 view model, Browser taxonomy presentation projection, helper, disposable package candidate는 consumer/implementation/evidence 역할만 가진다.

### Runtime Behavior Surface

Description fallback, Browser 선택, BrowserData build/retry, 검색 정렬, 상세 section inclusion, scroll behavior, Wiki/Browser interaction을 직접 건드린다. 실제 Lua/PZ behavior baseline과 작은 phase별 변경이 필수다.

### Compatibility Surface

`Description`, `UseCases`, `IrisData`, Wiki section functions, BrowserData facade, exporter public functions와 CLI가 외부 또는 historical caller에 노출됐을 수 있다. supported API manifest와 caller inventory 없이 signature나 module path를 제거하지 않는다.

### Sealed Artifact Surface

facts, decisions, rendered body, runtime chunks, required current-route artifacts와 existing package peer는 보호 surface다. 계획의 기본 상태는 no-mutation이며, package build는 disposable output에서만 수행하고 protected hash drift가 있으면 closeout을 중단한다.

### Public-Facing Output Surface

Description text, Browser/Wiki labels, food numeric formatting, Layer 3 body가 사용자에게 보인다. 의도된 wording 변경은 없으며 output parity 또는 명시적 formatter contract가 필요하다.

---

## 9. Risk Analysis

### Architecture Risk

* 공유 view model이 UI helper가 아니라 새로운 policy layer로 커질 수 있다.
* Python common package가 current core closure를 우회하는 사실상 새 core가 될 수 있다.
* runtime Generator를 Layer 3와 동일한 의미로 오인하면 서로 다른 description 역할이 사라질 수 있다.
* global 제거가 module-return 방식과 load-order 계약을 동시에 깨뜨릴 수 있다.
* Iris 전용 validation adapter가 기존 clean-checkout common과 경쟁하는 범용 governance framework로 커질 수 있다.

Mitigation:

* 공유 모듈은 raw facts/availability만 반환하고 렌더링·추천·authority 판단을 금지한다.
* build helper는 leaf dependency와 exact allowlist review를 요구한다.
* Generator full removal은 별도 parity gate를 통과한 경우에만 수행한다.
* compatibility facade를 먼저 두고 caller 0 증거 후 제거한다.
* 기존 dependency-free common을 read-only 부분 재사용하고 신규 validator ownership을 이 계획의 manifest/evidence에만 제한한다.

### Runtime Risk

* BrowserData build-state 전환 오류로 Browser가 영구 failed 또는 중복 build 상태가 될 수 있다.
* string state가 기존 `_built` boolean consumer에서 truthy로 평가돼 build/retry가 무음 skip될 수 있다.
* 미래 state/view-model acceptance를 current characterization으로 오인하면 존재하지 않는 동작을 baseline으로 승인할 수 있다.
* PUC Lua 결과를 Kahlua/PZ와 동일시하면 dialect-sensitive output에서 false green/false red가 생길 수 있다.
* scroll 최적화가 clip, child position, click target을 어긋나게 할 수 있다.
* negative cache가 늦게 로드되는 PZ module 복구를 막을 수 있다.
* normalized search cache가 locale 변경 후 stale해질 수 있다.

Mitigation:

* 공개 state API, single writer, direct-consumer guard, 실제 state transition/retry tests를 둔다.
* pre-refactor와 post-refactor denominator를 분리하고 acceptance는 소유 Change에 둔다.
* VM identity와 dialect inventory를 필수화하고 sensitive axis는 PZ cross-check 없이는 runtime PASS로 승격하지 않는다.
* locale/item identity/build generation을 cache invalidation key로 사용한다.
* negative cache는 세션 불변 generated module에만 적용하고 reset hook을 둔다.
* scroll에는 PZ UI 제약용 fallback을 유지한다.

### Compatibility Risk

* 외부 mod가 `IrisData`, `Description`, Wiki renderer, capability API를 직접 호출할 수 있다.
* historical build scripts가 exporter/public-text module의 내부 symbol을 import한다.
* 파일 이동이 `.gitignore` exact-unignore, package inclusion, clean checkout을 깨뜨릴 수 있다.
* 신규 behavior test가 exact unignore 없이 로컬에만 남아 clean checkout denominator에서 사라질 수 있다.

Mitigation:

* repository 및 documented external caller inventory를 분리 기록한다.
* 기존 import path와 public symbol wrapper를 유지한다.
* clean checkout과 historical route를 필수 gate로 둔다.
* supported API manifest 밖의 알려지지 않은 외부 mod에는 호환성 완료 claim을 하지 않는다.

### Regression Risk

* source-string test만 통과하고 실제 PZ runtime behavior가 깨질 수 있다.
* Browser/Wiki 통합 중 field omission이나 food 단위가 달라질 수 있다.
* repository cleanup이 required evidence를 잃게 만들 수 있다.
* validation asset manifest의 `assets`나 required denominator가 비어 wrapper가 아무 파일도 검사하지 않고 성공할 수 있다.
* StagedChangeset이 working-tree manifest/validator를 읽으면 stale index 상태가 통과할 수 있다.
* evidence가 자기 hash나 자신을 포함하는 commit을 요구하면 충족 불가능한 순환 identity가 생길 수 있다.
* sealed manifest에 reserved row가 남거나 locale 정렬로 required-ID hash가 달라질 수 있다.
* 외부 clean checkout의 target·root·cleanup이 불명확하면 원본 worktree 변경이나 잔여 checkout이 생길 수 있다.
* evidence가 없는데 Python test가 skip되면 test denominator만 채운 false green이 생길 수 있다.
* package가 새 Lua module을 누락하거나 stale copy를 포함할 수 있다.
* 기본 package output의 `-Clean`이 비교 대상인 existing package peer를 삭제할 수 있다.

Mitigation:

* characterization → focused implementation → integrated validation 순서를 지킨다.
* 대표 fixture와 raw getter 비교를 사용한다.
* deletion default를 deny로 두고 role evidence를 요구한다.
* manifest root/schema/non-empty exact denominator, sealed-reservation, ordinal ASCII ID hash와 duplicate·activation negative matrix를 먼저 검증한다.
* StagedChangeset은 index manifest와 materialized index validator만 PASS 입력으로 사용하고 working/index stale·hash mismatch fixture를 둔다.
* subject/producer/artifact/final implementation commit을 비순환 binding으로 분리하고 evidence 부재·schema/fixture/environment/identity 불일치를 skip이 아닌 failure로 고정한다.
* existing external-root/clone/finally-cleanup lifecycle을 재사용하고 source worktree pre/post identity를 비교한다.
* package는 checkout 밖 disposable output으로만 만들고 live/existing/candidate identity와 existing pre/post no-mutation을 분리 검증한다.

---

## 10. Rollback Plan

* 각 Change를 독립적으로 review/commit 가능한 단위로 유지한다. 하나의 대형 commit으로 합치지 않는다.
* validation 실패 시 해당 Change의 코드와 새 evidence wiring만 되돌리고, Phase 0 baseline과 실패 기록은 보존한다.
* compatibility wrapper 제거 후 caller가 발견되면 동일 public signature의 wrapper를 복원하고 내부 새 구현으로 delegate한다.
* BrowserData build-state/cache 변경 실패 시 공개 state API와 compatibility boolean 변경을 함께 되돌리되 behavior test는 유지해 재진입 조건으로 사용한다.
* scroll 최적화 실패 시 content/view model 분리는 유지하고 `showDetail()` rebuild fallback만 복원한다.
* Generator full-removal branch 실패 시 `Description` single execution path는 유지하고 기존 Generator backend를 복원한다.
* build helper extraction 실패 시 entrypoint와 symbols를 원래 파일로 되돌리고 allowlist/`.gitignore` additive change도 함께 되돌린다. disposable candidate output만 폐기하고 current protected artifacts나 existing package peer를 재생성·삭제하지 않는다.
* artifact disposition 실행 후 문제가 발견되면 사전 기록된 exact hash와 recovery path에서 복원한다. 복구 증거가 없는 material deletion은 애초에 허용하지 않는다.
* CleanCheckout failure 또는 binding 불일치 시 external result root를 먼저 삭제하지 않는다. receipt/stdout/stderr/canonical-result hash와 failure disposition을 durable record로 결속한 뒤 exact validated root만 정리한다.
* authority drift가 발견되면 이전 authority를 추측으로 덮어쓰지 않고 `blocked_authority_drift`로 닫아 별도 reconciliation plan을 연다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`의 hub-and-spoke, 100% Lua runtime, offline compiler, no runtime inference 원칙을 유지한다.
* `docs/EXECUTION_CONTRACT.md`의 disclosure, claim-evidence 1:1 binding, validation ceiling, `complete`/`partial`/`implemented_only`/`blocked` 환원 규율을 적용한다. 이 계약을 architecture나 Iris module policy authority로 사용하지 않는다.
* Iris runtime은 sealed facts/outcomes/descriptions를 표시하며 자체적인 의미 추론, 추천, 비교, 우선순위 결정을 추가하지 않는다.
* DVF Body Compiler는 body production, Iris Artifact Registry는 lifecycle/authority/runtime-package identity, Publish Boundary는 public text/release/manual QA를 소유한다.
* current Layer 3 chunk manifest/chunks만 runtime authority다. stale monolith나 historical candidate를 current path로 재도입하지 않는다.
* current, historical, diagnostic, package, public-text axis의 결과를 하나의 bare `PASS`로 합치지 않는다.
* current core 12는 convenience import 때문에 확장하지 않는다. allowed tooling은 `4/4`로 잔여 slot이 없으며 변경은 exact module, owner/reason, slot disposition을 가진 reviewed additive change여야 한다.
* `.gitignore`는 role-based VCS tracking contract다. broad cleanup pattern으로 대체하지 않는다.
* tracked는 authority를 뜻하지 않고 ignored는 disposable을 뜻하지 않는다.
* sealed artifact는 append-only/additive evidence를 우선하며 기존 protected artifact를 조용히 재작성하지 않는다.
* package 명령은 항상 checkout 밖의 bounded unique `-OutputRoot`를 사용한다. 기본 `Iris/build/package`에 `-Clean`을 실행하지 않는다.
* source/static guard는 실제 Lua/PZ runtime behavior evidence를 대체하지 않는다.
* validation asset adapter는 이 계획 전용이며 기존 `Iris/validation/clean_checkout`의 repository/commit/external-root authority를 복제하거나 대체하지 않는다.
* StagedChangeset success claim은 index manifest와 materialized index validator identity에만 결속한다. working-tree content는 staged PASS authority가 아니다.
* Pulse는 Iris 또는 다른 submod에 의존하지 않는다.
* 계획 범위 밖 사용자 변경을 수정, 정리, stage하지 않는다.
* validation command가 exit code `0`인 경우에만 통과를 주장한다.
* manifest·evidence denominator가 비었거나 schema/identity가 불완전한 no-op validation success는 exit code와 무관하게 non-compliant failure다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

Plan-specific state는 다음 standard closeout state로 환원한다.

| Plan-specific state | Standard closeout state |
|---|---|
| `blocked_*` reason code | `blocked` |
| `not_applicable` conditional branch | `complete` |
| `deferred_by_design`인 선택되지 않은 conditional branch | `complete` |
| `deferred_by_design` 때문에 mandatory 범위가 미완료 | `partial` |
| mandatory 구현은 끝났지만 필수 validation이 미완료 또는 `unvalidated_but_in_scope` | `implemented_only` |
| 일부 mandatory 구현만 완료되고 진행 가능하지만 미완료 | `partial` |

`complete`는 모든 조건부 branch를 강제로 실행했다는 뜻이 아니다. 다음 조건을 모두 만족한 상태다.

* mandatory Changes 1–5와 integrated validation이 완료된다.
* Change 6–7의 각 candidate가 증거에 따라 `implemented`, `deferred_by_design`, `not_applicable` 중 하나로 닫히고 standard state 환원 결과가 기록된다.
* Generator full removal을 선택하지 않은 경우 facade dedup과 backend 보존 근거가 완료돼 있다.
* optional Change 8은 no-op, `deferred_by_design`, 또는 별도 disposition changeset으로 닫힐 수 있으며, current/package/required-evidence 충돌이 없는 한 core `complete`를 막지 않는다.
* current authority, existing package peer, public-facing protected text에 승인되지 않은 변화가 없다. package candidate만 disposable output에서 생성됐다.
* supported API manifest에 열거된 compatibility surface가 검증됐다.
* 자동 검증과 필수 PZ validation이 모두 실제 실행돼 schema-valid evidence가 남고, mandatory axis에 `unvalidated_but_in_scope`가 없다.
* mandatory characterization/acceptance Python test가 대응 evidence 부재를 skip으로 숨기지 않았으며 evidence schema, fixture, environment, subject/producer identity와 external evidence SHA-256 binding을 모두 검증했다.
* Change 2 pre-refactor denominator와 Changes 3–6 owner-specific acceptance denominator가 분리돼 있고, 각 구현 axis의 before/after 관계가 승인된 matrix와 일치한다.
* VM identity 또는 dialect relation이 없는 standalone row는 runtime behavior PASS에 사용되지 않았으며, dialect-sensitive mandatory axis는 PZ/Kahlua evidence를 가진다.
* final validation asset manifest는 non-empty exact required denominator, unique lowercase-ASCII ID/path, ordinal canonical hash, `reserved_future_count=0`을 가진 `sealed=true` 상태이며, index-source StagedChangeset과 target-commit fresh CleanCheckout validation 및 ceiling generation chain이 Change 9에서 봉인됐다.
* final evidence binding은 subject, producer, artifact hash, 구현 changeset을 순환 없이 연결하고 external checkout cleanup receipt와 source worktree no-mutation을 포함한다.
* terminal binding attestation이 tracked commit으로 영속화되고 external receipt/canonical-result/stdout/stderr hash와 다시 일치한 뒤 result root cleanup이 완료되며, exact path와 cleanup 결과가 operational closeout에 기록된다.

PZ in-game 환경 부재 상태에서 code implementation까지 끝났다면 standard state는 `implemented_only`다. implementation 착수 전 필수 characterization이나 authority/approval에 막혔다면 standard state는 `blocked`이고 `blocked_pz_behavior_evidence_missing`, `blocked_authority_drift` 같은 reason code를 함께 기록한다. current-route failure, package identity mismatch, 신규 test VCS 누락도 같은 방식으로 `blocked`에 환원한다.
