# Implementation Plan

> Iris 코드베이스 최적화 종합 로드맵 후속 실행 계획
>
> 기준 커밋: `5b19a5fa58cb883f6b27f433371434a85b41ba0d`
>
> 작성 기준일: 2026-08-11
>
> 선행 계획: `docs/iris_codebase_optimization_consolidated_plan.md`
>
> 상태: 첨부 로드맵과 2026-08-11 두 차례 종합 검토의 Critical 및 Non-Critical 보강 사항을 현재 코드에 맞춰 재기준화한 후속 계획

## 1. Objective

이 계획의 목적은 Iris가 정적 위키라는 전제를 유지하면서, 현재 남아 있는 저장소·생성 도구·생성 Lua·Browser·Tooltip·Detail 런타임 비용을 줄이고 cache lifecycle의 실제 정확성 요구를 evidence로 판정하는 것이다.

이 계획은 FPS, 프레임타임 또는 tick 분산을 일반적인 성공 지표로 삼지 않는다. 대신 다음 항목을 직접 측정하고 검증한다.

1. Browser·Tooltip cache field의 owner를 process-stable, locale-dependent, session-dependent로 분류하고, 실제 session dependency가 확인된 field만 세션 경계에서 무효화한다.
2. Browser candidate cache를 만들 때 동일한 `fullType` 집합을 검색 키, 분류, 주 위치 계산 때문에 반복 순회하는 횟수를 줄인다.
3. public copy-on-read를 유지하면서 Browser 내부 tag·primary·variant·search 계산의 임시 테이블과 반복 정렬을 줄인다.
4. ItemDetail ViewModel과 `IrisObjectAccess`의 반복 method 탐색, vararg table, closure 생성을 줄인다.
5. Tooltip first-use 시 여러 정적 authority를 런타임에서 다시 조합하는 비용과 `LineCountIndex`의 eager load/validation 비용을 분리해 판정한다.
6. direct `require`, compatibility global, legacy key/value semantics, mutation isolation을 유지할 수 있을 때만 중복 생성 Lua payload를 줄인다.
7. Python current execution 안에서 동일 입력의 반복 read/hash가 실제로 확인되는 경로만 run-local reuse 대상으로 삼는다.
8. staging/evidence는 lifecycle과 consumer closure가 닫힌 대상만 CAS 또는 cold archive로 전환하고, 안전 후보가 없으면 no-op으로 종결한다.

선행 `docs/iris_codebase_optimization_consolidated_plan.md`는 이미 구현·검증·review closeout의 provenance 입력이다. 이 문서는 그 계획을 소급 수정하지 않으며, 이미 채택된 sparse UseCase representation, lazy lookup miss/fault 분리, Alt 비활성 경로 최적화, Browser 검색 위치 cache, Ordering decoration, Git path batch query를 다시 구현하지 않는다.

첨부 로드맵의 네 충돌은 현재 authority와 코드 readpoint에 따라 다음처럼 판정한다.

| 충돌 | 이 계획의 판정 | 근거 |
|---|---|---|
| Browser cache의 item 객체 보존 여부 | **A — row 중심 cache + item 객체 유지**를 mandatory 기본안으로 채택한다. item 비보존은 별도 heap/lifetime 측정이 유의미한 절감을 증명할 때만 conditional branch로 재개한다. | 현재 `IrisBrowserData.getItem(fullType)`과 variant/detail 경로가 cache의 item identity를 사용한다. item 비보존은 단순 메모리 최적화가 아니라 재조회·identity·실패 계약 변경이다. |
| legacy `IrisData` 처리 | **정책 A — exact legacy semantic parity**를 채택한다. case-sensitive parser로 확인한 1,360개 assignment/1,360개 unique key의 legacy semantics와 tag order를 독립 table로 보존하며, compact reconstruction은 이를 지킬 때만 measurement-gated로 채택한다. | `ARCHITECTURE.md`는 `IrisData` access를 삭제되지 않은 public adapter로 규정하고 adapter의 runtime 의미 재해석을 금지한다. current authority와의 mutable alias 및 719개 current-only key 유입은 optimization 범위의 compatibility success가 아니다. |
| `LineCountIndex` integrity 처리 | **B — runtime lazy validation 유지**를 채택한다. build/package exhaustive parity를 강화하되 runtime integrity 책임을 이번 계획에서 제거하지 않는다. | 현재 architecture는 line-count index를 routing metadata/authority로 유지하고 lookup corruption을 fail-closed fallback으로 구분한다. authority 이동은 별도 결정 없이 수행할 수 없다. |
| 첫 실행 우선순위 | **B — cache ownership census 후 runtime correctness/cache**를 채택한다. candidate 0 또는 PZ negative evidence면 `complete/no-op`, candidate가 있지만 PZ functional 확인이 불가능하면 `deferred_by_design`이다. | `resetForReload()`의 production caller가 없다는 사실만으로 cache가 save/session-dependent임을 증명할 수 없다. 검증 불가와 dependency 부재를 같은 no-op으로 기록하지 않으며 locale invalidation은 별도 owner를 갖는다. |

종합 검토의 네 blocking condition은 다음 정책으로 해소한다.

| Review blocker | 수정된 정책 |
|---|---|
| optional PZ timing의 mandatory gate 승격 | Phase 0을 PZ 비의존 Change `1a`와 PZ timing Change `1b`로 분리하고 `1a`만 unconditional 선행 gate로 사용한다. |
| session reset의 근거 부족 | cache owner census와 stale reproduction을 production mutation의 entry condition으로 삼고 no-op 종결을 허용한다. |
| generation-wide sort의 locale ownership 누락 | search source owner를 `(generation, locale)`로 고정하고 locale 전환을 key 재생성·재정렬·prefix clear의 단일 transaction으로 만든다. |
| legacy semantics/authority isolation 미결 | exact legacy parity, 독립 mutable table, current authority mutation isolation을 채택한다. current-semantic migration은 이 계획 밖이다. |

2026-08-11 두 번째 종합 검토의 네 blocking condition은 다음처럼 추가 판정한다.

| Review blocker | 수정된 정책 |
|---|---|
| raw Tags authority 노출 가능성 | `Tags.lua`/`IrisAPI.Tags`에 accessor를 추가하지 않는다. Browser build scope에서만 backing classification을 scalar tag로 순회하고 backing table/array를 cache·row·public return에 저장하지 않는다. |
| lookup-first LineCount fail-loud 약화 | 두 entrypoint가 ChunkIndex/LineCountIndex metadata를 함께 lazy materialize하되 **per-index self-state와 predecessor의 비대칭 소비 gate**를 보존한다. `get()`은 두 self-state와 cross-check를, `getLineCount()`은 LineCount self-state와 applicable cross-check만 요구한다. |
| Change 2 PZ functional evidence 부재 | candidate 0=`complete/no-op`, candidate 존재+PZ 불가=`deferred_by_design`, PZ 확인=`adopted`를 직접 결속한다. |
| classification effective-key 사실 충돌 | Lua의 case-sensitive key semantics와 동일한 ordinal parser/receipt를 authority로 삼는다. `Base.LemonGrass`와 `Base.Lemongrass`는 서로 다른 key이며 duplicate는 0이다. |

---

## 2. Scope

실행 순서는 다음과 같이 고정한다.

1. Phase 0a / Change 1a — PZ 비의존 기준선, public/consumer/cache-owner census 및 structural gate
2. Phase 0b / Change 1b — PZ timing receipt와 timing-dependent branch gate
3. Phase 1 — cache owner 판정과 조건부 session invalidation/generation 계약
4. Phase 2 — Browser 단일 row 처리, module-local scalar tag iteration, primary/rank/group 및 `(generation, locale)` search 최적화
5. Phase 3 — ViewModel/ObjectAccess와 비활성 debug/allocation 경량화
6. Phase 4 — Tooltip static projection 및 `LineCountIndex` lazy validation
7. Phase 5 — legacy `IrisData` exact-parity disposition과 생성 Lua compact representation
8. Phase 6 — current Python run-local I/O/hash reuse와 대형 script disposition
9. Phase 7 — staging/evidence lifecycle 재판정
10. Phase 8 — 통합 검증, adoption/no-op/deferred 판정, closeout

Phase 0a만 모든 production mutation의 unconditional 선행 gate다. Phase 0b의 PZ timing receipt 부재는 timing 채택 근거를 요구하는 branch만 `deferred_by_design`으로 닫으며 Browser single-pass, DEBUG guard, cache-owner census 같은 독립 작업을 막지 않는다. 다만 Change 2의 session transition과 Change 4의 Java/Kahlua fast path 같은 engine-bound functional evidence는 timing과 별도 축이며, candidate/implementation이 존재하지만 PZ functional validation을 수행하지 못하면 `unvalidated_but_in_scope`로 남긴다. 생성 Lua 변경은 generator, source runtime tree, disposable package, public facade adapter를 하나의 transaction으로 검증하기 전에는 live source에 승격하지 않는다.

이 계획의 mandatory 범위는 다음과 같다.

* PZ 비의존 baseline/consumer/cache-owner census와 default-off instrumentation 봉인
* session cache invalidation의 evidence-based `adopted`/`complete/no-op`/`deferred_by_design` disposition
* Browser candidate cache의 검색 키/분류/주 위치용 반복 전체 순회 병합
* public `Tags` API를 변경하지 않고 backing array를 유출하지 않는 Browser module-local scalar tag iteration
* `chooseLocation()` rank lookup, generation-local primary tag reuse, variant grouping key 단순화
* `(generation, locale)`별로 이미 정렬된 search source에서 prefix result 재정렬 제거
* ViewModel method list module constant화와 호출당 capability hint 1회 계산
* `IrisObjectAccess` 0인자·1인자 fast path의 Lua parity 및 PZ-gated production-routing disposition
* unguarded dynamic DEBUG message의 caller-side guard
* `LineCountIndex` module-load eager validation을 first-demand lazy validation으로 이동
* 각 high-risk candidate의 채택/no-op/deferred 근거와 validation ceiling 기록

다음은 measurement-gated 범위다.

* Browser item 객체 비보존 branch
* PZ Search/incremental build/Tooltip/LineCount timing receipt와 이에 의존하는 채택 branch
* Java/Kahlua `IrisObjectAccess` fast-path production routing
* Tooltip offline static summary data
* UseCase/Layer3 positional or interned compact representation
* Alt display-line cache의 LRU 또는 크기 제한
* `IrisRecipeIndex` build-time membership Set
* Python run-local read/hash cache
* exact legacy semantics를 보존하는 `IrisData` compact reconstruction
* 대형 Python script 책임 분할
* staging/evidence CAS 또는 cold archive mutation

measurement-gated 항목은 baseline에서 실제 비용이 식별되고, after 측정이 public parity와 함께 개선될 때만 채택한다. 현재 corpus에서 비용이 없거나 절감량이 payload/복잡성 증가보다 작으면 코드 변경 없는 `complete/no-op`으로 닫는다.

### Explicitly Out Of Scope

* FPS, frame time, tick variance를 이 계획의 일반 성공 claim으로 만드는 것
* Project Zomboid engine 또는 타 모드 최적화
* Pulse에서 Iris를 참조하는 역방향 의존성
* Iris와 다른 spoke 간 직접 의존성
* UI 전면 재작성, 테마 변경, 사용자 정보 의미 변경
* 공개 `Tags` API의 Set/array 반환 계약 변경
* `IrisBrowserData.getItem`, `getItems`, `searchAll`, `getGroupVariants`의 공개 반환 shape 변경
* 완성 ItemDetail ViewModel의 `fullType`-only cache
* `IrisData` global/direct require/getGroupVariants surface의 즉시 제거
* legacy `IrisData.Classifications`를 current 2,079-key semantics로 갱신하는 data/compatibility migration
* `LineCountIndex` integrity authority를 build/package로 완전히 이전하는 것
* Git history rewrite, filter-repo 또는 `.git` 크기 축소
* consumer가 살아 있는 evidence의 삭제
* helper 모양이 유사하다는 이유만으로 Python family를 공통화하는 것
* current core 12 또는 allowed tooling 4/4를 convenience import로 확장하는 것
* release, Workshop, B42, multiplayer 또는 long-session readiness 선언

---

## 3. Non-Goals

* 이미 완료된 Browser boot eager build 제거를 다시 수행하지 않는다.
* 이미 완료된 Layer3/UseCase demand chunk lookup을 다른 loading architecture로 교체하지 않는다.
* 이미 채택된 UseCase optional `nil`/빈 `debug_lines` sparse화를 다시 세지 않는다.
* public Browser/Tooltip copy-on-read를 없애 operation count를 낮추지 않는다.
* category/type 문자열을 closed-negative capability authority로 사용하지 않는다.
* physical denominator의 497개 `tools/build` Python script 또는 928개 `Iris/build` Python file을 tracked denominator와 혼합하거나 한 번에 리팩터링하지 않는다.
* historical/diagnostic reproduction script를 current 성능 경로라는 이유로 이동·삭제하지 않는다.
* 모든 DEBUG call을 제거하지 않는다. DEBUG가 활성일 때 필요한 진단 의미는 보존한다.
* Lua string interning 또는 Java object GC 동작을 측정 없이 절감량으로 추정하지 않는다.
* 생성 summary 또는 compact index를 새 semantic authority로 만들지 않는다.

---

## 4. Assumptions

### Constitutional and Authority Assumptions

* `docs/Philosophy.md`가 최상위 설계 권한이다.
* Iris runtime은 100% Lua이며, 오프라인에서 확정된 facts/classification/outcome/description을 표시한다.
* Iris는 해석·권장·비교를 추가하지 않는다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current authority와 선행 closeout을 predecessor 사실로 사용한다.
* `docs/EXECUTION_CONTRACT.md`의 disclosure, claim-evidence binding, validation ceiling, closeout state 규율을 적용한다.
* `Iris/_docs/round3/current_route_required_validations.json`과 exact current runner는 current authority 검증 경로다. configured full discovery와 historical/diagnostic advisory는 이를 대체하지 않는다.
* `IrisData`, public Browser facade, direct UseCase/Layer3 facade, copy-on-read는 compatibility surface다.
* current generated data를 입력으로 만든 Tooltip summary/compact payload는 파생 projection이며 별도 의미 authority가 아니다.

### Current Codebase Readpoint

기준 커밋에서 다음 상태를 직접 확인했다.

* `IrisBrowserData.buildCandidateCache()`는 `createSearchKeys()` 1회, tag/classification 1회, `chooseLocation()` 1회로 같은 `itemsByFullType`을 세 차례 순회한다.
* Browser cache는 `itemsByFullType`, `searchKeysByFullType`, `primaryLocationByFullType`, classification location/index를 분리 보유한다.
* `IrisBrowserData.resetForReload()`는 test/dev caller만 있고 production caller가 없다. 이 사실은 reset wiring 부재를 보여 주지만 cache가 save/session-dependent라는 증거는 아니다.
* `IrisMapIcon.onMainMenuEnter()`와 `Events.OnMainMenuEnter` registration은 이미 존재한다.
* `Tags.getTagsForItem(item)`은 fullType을 다시 해석하고 classification array를 임시 Set으로 변환한다. `Tags.getTags(fullType)` public array copy와 `getTagsForItem()` public Set copy는 유지해야 한다.
* `IrisAPI.lua`는 `require("Iris/API/Tags")`가 반환한 module table 전체를 `IrisAPI.Tags`로 노출한다. 따라서 `Tags.lua`에 이름만 private인 raw accessor를 export하면 실제 public callable surface가 된다.
* `StaticData.lua`는 source header에서 private helper로 선언되고 `IrisAPI.lua`는 `Tags`, `Index`, `Description`, `UseCases`만 public field로 재노출하며 `StaticData`를 노출하지 않는다. Change 3은 이 기존 private boundary를 넓히지 않는다.
* `IrisBrowserClassificationIndex.addItem(index, fullType, tags)`의 production caller는 `IrisBrowserData.lua` 한 곳이다. Change 3은 이 caller와 acceptance harness의 failure-injection boundary를 함께 `addTag`로 이동한다.
* `IrisBrowserClassificationIndex.chooseLocation()`은 category → subcategory → item locations의 중첩 비교를 수행한다.
* `IrisBrowserVariantIndex.groupingKey()`는 subcategory마다 fullType 배열을 만들고 정렬·concat한다.
* `IrisBrowserVariantIndex.calculatePrimary()`는 item list를 만들 때 tag Set을 다시 구성한다.
* `IrisBrowserQuery.searchAll()`은 prefix result가 이미 정렬된 경우에도 매 query에서 `table.sort`한다. 현재 `searchKeysLocale`, `localeInvalidationCount`, `searchPrefixState.locale`가 있어 locale은 이미 살아 있는 invalidation 축이다.
* `IrisItemDetailViewModel.fromItem()`은 method-name table 네 개와 single-method table을 호출마다 만들고, `capabilityHints()`를 group별로 반복 계산한다.
* `IrisObjectAccess.call()`은 모든 호출에서 `{...}`와 익명 closure를 만든다. production call site는 현재 16개이며 대부분 0인자 또는 1인자다.
* dynamic DEBUG concat/search pattern은 production Iris Lua에서 137개가 검색된다. 일부는 이미 `isDebugEnabled()` guard 안이지만 unguarded call은 문자열을 먼저 만든다.
* `IrisUseCaseDescriptionsLookup`은 module load 때 `ChunkIndex`와 `LineCountIndex`를 require하고 1,631개 line-count row를 전수 검증한다.
* `IrisTooltipSummary`는 first-use에 Classifications, Recipe, Moveables, Fixing, UseCase lookup을 불러 summary를 조합한다.
* `IrisAltTooltip.displayLineCache`는 `fullType × locale × revision` 중첩 table이며 production session reset이 없다.
* `IrisRecipeIndex.inGetItemTypes()`는 배열을 선형 검색하지만 current generated group은 `CanOpener` 1개/아이템 1개이므로 현재 Set 전환의 실익은 입증되지 않았다.
* Lua key semantics와 같은 ordinal case-sensitive parser 기준 `IrisData.lua`는 1,360개 assignment/1,360개 unique key, current `IrisClassifications.lua`는 2,079개 assignment/2,079개 unique key이며 duplicate는 양쪽 모두 0이다. `Base.LemonGrass`와 `Base.Lemongrass`는 각 파일에 한 번씩 존재하는 서로 다른 key다. legacy key는 모두 current에 존재하고 current-only key는 719개이며 공통 key의 ordered tag array 값 차이는 4개다. repository internal `ItemGroups` producer는 0개다.
* `IrisBrowserData.getGroupVariants()`와 `StaticData.getLegacyIrisData()`는 external/dynamic compatibility를 위해 남아 있다.
* `layer3_renderer`는 verified `lookup_miss`에서 full facade로 fallback하지 않는다. `IrisBrowserInteractionRenderer`도 UseCases focused API가 존재하면 full facade fallback을 사용하지 않는다. `IrisTooltipSummary.countUseCaseLines()`는 `getLineCount()` reason 발생 시 full `IrisUseCaseDescriptions` facade를 load한다. 세 경로를 서로 다른 fallback owner/counter로 계측하고 우선 재작성하지 않는다.

### Measured Repository Baseline

기준 커밋의 read-only census는 PowerShell `Get-ChildItem -File -Recurse`가 반환한 file의 `Length` 합, 즉 logical file bytes로 측정한다. disk allocation/block usage는 사용하지 않으며 before/after에도 같은 명령과 exact root를 사용한다. scope와 physical/tracked denominator가 다른 수치를 합치지 않는다.

| Scope | Denominator type | Files | Bytes | Approx. MiB |
|---|---|---:|---:|---:|
| `Iris/build` | physical checkout | 6,456 | 777,898,055 | 741.9 |
| `Iris/build/description/v2/staging` | physical checkout | 4,553 | 547,828,971 | 522.5 |
| `Iris/build/description/v2/evidence` | physical checkout | 240 | 186,373,483 | 177.7 |
| existing tracked files under `Iris` | Git tracked | 5,154 | 655,872,180 | 625.5 |
| `Iris/media/lua/client/Iris/Data` | physical checkout | 43 | 2,528,303 | 2.4 |

주요 generated/runtime payload baseline:

| Artifact | Current size |
|---|---:|
| UseCase chunk directory 전체 | 1,230,589 bytes / 12 files |
| Layer3 chunk directory 전체 | 968,181 bytes / 11 files |
| `IrisClassifications.lua` | 111,083 bytes / 2,079 assignments / 2,079 unique keys / duplicate 0 |
| legacy `IrisData.lua` | 75,143 bytes / 1,360 assignments / 1,360 unique keys / duplicate 0 |
| `IrisRecipeIndexData.lua` | 78,265 bytes |
| `UseCaseDescriptions/LineCountIndex.lua` | 61,527 bytes |

Python denominator는 scope와 집계 방법별로 구분한다.

| Denominator ID | Scope/method | Python files |
|---|---|---:|
| `PY-PHYSICAL-TOOLS-BUILD` | physical checkout의 `Iris/build/description/v2/tools/build/**/*.py` | 497 |
| `PY-TRACKED-TOOLS-BUILD` | `git ls-files Iris/build` 중 같은 tools/build subtree의 `.py` | 250 |
| `PY-PHYSICAL-IRIS-BUILD` | physical checkout의 `Iris/build/**/*.py` | 928 |
| `PY-TRACKED-IRIS-BUILD` | `git ls-files Iris/build` 중 `.py` | 483 |

* subprocess reference는 physical `PY-PHYSICAL-IRIS-BUILD`에서 119 files, 정규식 explicit call site 271개다. exact pattern과 source-set hash를 baseline receipt에 기록한다.
* 최대 tracked/physical script는 `dvf_3_3_registry_authority_canonical_closure.py`다. PowerShell `(Get-Content -LiteralPath $path).Count` line-record 기준 13,219줄이며, blank를 제외한 `Measure-Object -Line` 기준은 12,798줄이다. 대형 script disposition은 13,219 line-record를 기준으로 하고 두 수치를 혼용하지 않는다.

Classification baseline은 generic PowerShell `Hashtable`을 사용하지 않는다. 기본 comparer가 case-insensitive라 `Base.LemonGrass`/`Base.Lemongrass`를 잘못 병합하기 때문이다. 단일 canonical Phase 0a PowerShell collector는 .NET `Dictionary<string, ...>(StringComparer.Ordinal)`만 사용하며, exact command text와 그 SHA-256을 receipt에 넣어 같은 collector를 재실행한다. alternate parser 결과를 섞지 않는다.

* parser schema/version과 implementation SHA-256
* legacy/current input file SHA-256
* assignment count, unique key count, exact duplicate key list
* `Base.LemonGrass`와 `Base.Lemongrass` 각각의 occurrence count
* common/current-only/legacy-only key set hash
* ordered tag array가 다른 common key list/hash

현재 readpoint의 input SHA-256은 legacy `17ed88f3fb1ed5b6ab96b021442dfb8e34b757d34b0c0ea05508876f855296b1`, current `98d9ce3162703333b02dd48d62f8739e4606eada321a7731a35e2e586f033563`다. sealing 시 parser가 모든 generated assignment line을 정확히 한 번 소비했는지 fail-closed로 확인하고 위 수치를 재산정한다.

이 수치는 후보 inventory다. 현재 실행 경로의 반복 I/O나 분할 승인 근거를 자동으로 만들지 않는다.

### Environment Assumptions

* 명령은 Windows PowerShell에서 실행한다.
* Python은 `uv run python ...`로 실행한다.
* Lua syntax는 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`로 검증한다.
* Project Zomboid B41/Kahlua runtime이 제공되면 같은 build, machine, save, mod set, locale에서 before/after를 측정한다.
* source-mutating generator와 package build는 clean disposable checkout 및 checkout 밖의 bounded output root에서 실행한다.

---

## 5. Repository Areas Affected

아래는 최대 예상 touch surface다. conditional/no-op branch가 닫히면 해당 파일은 수정하지 않는다.

### Code

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisMapIcon.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserClassificationIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
* `Iris/media/lua/client/Iris/API/Tags.lua`와 `Iris/media/lua/client/Iris/IrisAPI.lua` — protected public surface; Change 3에서 export 추가 금지
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/Util/IrisObjectAccess.lua`
* `Iris/media/lua/client/Iris/Util/IrisLogger.lua`
* `Iris/media/lua/client/Iris/Util/IrisModuleBootstrap.lua`
* `Iris/media/lua/client/Iris/Data/IrisRuntimeLookupDiagnostics.lua` — Change 1이 fallback counter ownership을, Change 6이 lazy index/fallback reason interaction을 소유
* `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua`
* `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua`
* `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
* `Iris/build/main.py`
* `Iris/build/convert_descriptions_to_lua.py`
* `Iris/build/description/v2/tools/build/build_iris_recipe_index_data.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_io.py`
* current package/lookup validator owner files identified by Phase 0 census
* lifecycle candidate가 생긴 경우 기존 `Iris/validation/residual_refactor/` CAS/lifecycle tools

### Tests

* `Iris/test/lua/browser_state_acceptance_harness.lua`
* `Iris/test/lua/legacy_surface_adapter_harness.lua`
* existing Tooltip/Browser/ViewModel/ObjectAccess Lua harnesses
* `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`
* `Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py`
* `Iris/build/description/v2/tests/test_generated_lua_sparse_fields_contract.py`
* `Iris/build/description/v2/tests/test_lookup_package_parity_contract.py`
* `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
* 새 `test_iris_session_cache_ownership.py`와 조건부 invalidation fixture
* 새 `test_iris_browser_single_pass_cache_contract.py`
* 새 `test_iris_tags_public_surface_isolation.py`
* 새 `test_iris_object_access_fast_path.py`
* 새 `test_iris_viewmodel_allocation_contract.py`
* 새 `test_iris_tooltip_summary_projection.py` — conditional
* 새 `test_iris_line_count_lazy_validation.py`
* 새 `test_iris_classification_baseline_receipt.py`
* 새 `test_iris_generated_compact_representation.py` — conditional
* 새 `test_iris_build_run_io_reuse.py` — conditional

### Docs

* `docs/DECISIONS.md` — 실제 채택된 계약만 additive update
* `docs/ARCHITECTURE.md` — cache lifecycle, compatibility reconstruction, lazy validation이 실제 채택된 경우만 update
* `docs/ROADMAP.md` — change disposition과 closeout state update
* `Iris/_docs/refactor/codebase_optimization_followup/` — plan-local baseline, decision, validation, closeout receipts
* `Iris/build/description/v2/tools/build/INVENTORY.md` — Python/build-tool disposition이 실제 변한 경우만 update

### Config

* 기본 설정 변경 없음
* `Iris/IrisConfig.lua`의 DEBUG 기본값 변경 없음
* `.gitignore`는 lifecycle disposition이 실제 승인된 exact path에 한해서만 검토하며 broad rule은 추가하지 않음

### Generated Artifacts

* `Iris/media/lua/client/Iris/Data/IrisData.lua`
* `Iris/media/lua/client/Iris/Data/IrisClassifications.lua` — read-only protected comparison input; 이 계획에서는 content mutation 금지
* `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua` — conditional
* `Iris/media/lua/client/Iris/Data/IrisTooltipSummaryData.lua` — conditional
* `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/*.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/LineCountIndex.lua`
* source/package generation manifest 및 package identity receipt
* lifecycle/CAS reference와 external archive receipt — safe candidate가 있을 때만

---

## 6. Planned Changes

### Change 1 — Change 1a unconditional gate와 Change 1b PZ timing gate 분리

Purpose:

PZ runtime 없이 닫을 수 있는 structural/correctness baseline과 optional timing evidence를 분리해, public/consumer/authority 경계는 구현 전에 고정하되 PZ timing 부재가 독립적인 production mutation을 차단하지 않게 한다.

Files:

* `Iris/_docs/refactor/codebase_optimization/closeout_receipt.json` — read-only predecessor
* 새 `Iris/_docs/refactor/codebase_optimization_followup/baseline_manifest.json`
* 새 `Iris/_docs/refactor/codebase_optimization_followup/consumer_census.json`
* 새 `Iris/_docs/refactor/codebase_optimization_followup/cache_lifetime_baseline.json`
* 새 `Iris/_docs/refactor/codebase_optimization_followup/classification_baseline.json`
* 새 `Iris/_docs/refactor/codebase_optimization_followup/pz_timing_manifest.json` — Phase 0b가 실행될 때만
* 기존 dev instrumentation harness 및 필요한 additive counter

Implementation Notes:

* **Change 1a / Phase 0a — unconditional:** 기준 commit/tree, logical-byte census method, physical/tracked denominator ID와 source-set SHA-256, fullType set hash, instrumentation state를 결속한다. 이 gate는 PZ runtime을 요구하지 않는다.
* Browser build는 engine scan count, Lua full-map pass count, tag array→Set conversion count, `chooseLocation` comparison count, search sort count를 수집한다.
* Browser cache item-reference 수와 가능할 경우 Kahlua/Java heap delta를 기록한다. 신뢰 가능한 heap API가 없으면 item count와 Lua table/row count만 proxy로 기록하고 heap claim은 금지한다.
* Change 5의 Alt active threshold를 위해 hover corpus identity와 render별 fullType resolution, locale resolution, `tostring`, nested lookup, temporary allocation count를 Phase 0a default-off counter에 포함한다.
* Change 7 cold materialization baseline은 `publicTopLevelTableAllocations`, `publicNestedArrayAllocations`, `publicTagScalarWrites`, `auxiliaryTableAllocations`, `decodeIterations`를 센다. `materializationOps`는 이 다섯 counter의 합으로 정의하고 동일 Lua harness/legacy corpus에서만 비교한다.
* `IrisData`, `getGroupVariants`, `LineCountIndex`, direct chunk/facade require의 repository consumer, test consumer, documented external surface를 분리한다.
* dynamic require/string-built path를 포함하는 consumer census 없이 compatibility surface를 제거하지 않는다.
* fallback counter는 `layer3_renderer`, `IrisBrowserInteractionRenderer`, `IrisTooltipSummary.countUseCaseLines()` 세 owner를 별도 row로 가진다. normal Layer3/UseCase miss와 Tooltip line-count fallback을 하나의 합계로 숨기지 않는다.
* `IrisRuntimeLookupDiagnostics.lua`의 Change 1 책임은 additive fallback owner/counter와 default-off operation instrumentation에 한정한다. lazy index state/reason behavior 변경은 Change 6에서만 수행한다.
* classification collector는 ordinal case-sensitive parser/input/implementation hash와 assignment/unique/duplicate/current-only/differing-key 결과를 `classification_baseline.json`에 봉인한다.
* denominator equality는 단순 row count가 아니라 fullType set hash, mod-set identity, denominator source-set SHA-256이 모두 같을 때만 인정한다.
* **Change 1b / Phase 0b — measurement-gated:** PZ build, machine, save, mod set, locale, item corpus, run order를 결속하고, 환경이 제공될 때 `PZ-6C-SEARCH-01`, `PZ-6C-BUILD-01`, `PZ-7-TOOLTIP-01`, `PZ-7-LINECOUNT-01`을 cold/warm 각 10회 측정한다.
* Phase 0b가 없으면 timing 근거가 필요한 Tooltip projection, item 비보존 등 해당 branch만 `deferred_by_design`으로 닫는다. Phase 0a를 통과한 Browser single-pass, DEBUG guard, ViewModel/ObjectAccess Lua fixture, lazy integrity work는 계속 진행할 수 있으며 ObjectAccess production routing은 별도 PZ functional gate를 따른다.
* PZ 없이 채택한 변경은 operation/allocation/byte/parity까지만 claim하고 latency, heap, FPS, frame-time 개선은 claim하지 않는다.

Validation:

* Phase 0a baseline receipt schema/identity/hash 및 denominator-ID test
* instrumentation default-off test
* 동일 corpus 반복 측정의 fullType/mod-set/source-set denominator equality
* consumer census exact source-set/hash test
* 세 fallback owner counter의 정상 miss/fault fixture
* Alt hover corpus와 active-render counter의 default-off 및 denominator equality
* legacy cold direct-require materialization counter schema/default-off/semantic denominator equality
* 같은 immutable legacy input과 harness identity로 cold materialization을 clean Lua state에서 최소 2회 반복하고, 다섯 counter와 derived `materializationOps`가 회차 간 exact equality인지 검증
* ordinal classification parser 재실행 결과와 receipt 1:1 equality
* source mutation 0 확인
* Phase 0b가 실행되면 PZ environment identity와 raw sample count 검증, 실행되지 않으면 의존 branch만 `deferred_by_design`인지 검증

---

### Change 2 — cache owner census와 조건부 production session invalidation

Purpose:

Browser·Tooltip cache field의 lifetime owner를 먼저 증명하고, 실제 session-dependent engine object 또는 재현된 stale field에만 production session invalidation을 연결한다. session dependency 부재, candidate의 functional 검증 불가, confirmed dependency를 서로 다른 disposition으로 닫는다.

Files:

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisMapIcon.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* 관련 lookup reset owner — 실제 session-dependent cache census에 포함될 때만
* `cache_owner_census.json`과 조건부 `session_invalidation_receipt.json`

Implementation Notes:

* `_cache`, `itemsByFullType`/row `item`, primary/classification maps, search keys/sorted source/prefix state, `IrisAPI` reference, Tooltip authority modules, `summaryByFullType`, display lines를 최소 field 단위로 census한다.
* 각 field를 `process_stable_static`, `locale_dependent`, `session_dependent_engine_object` 중 하나로 분류하고 owner, construction input, invalidation trigger, evidence를 기록한다. 알 수 없는 field를 session-dependent로 추정하지 않는다.
* census completeness는 문서에 열거한 row 존재만 보지 않는다. source/runtime fixture에서 추출한 actual cache owner/field key set과 receipt row key set의 exact equality를 요구하고 누락/초과 row가 있으면 fail-closed한다.
* Change 2 disposition은 다음 네 갈래로 고정한다.
  * census candidate 0 → production diff 0, `complete/no-op`
  * candidate 1개 이상 + PZ session transition 실행 불가 → production diff 0, `deferred_by_design`, `unvalidated_but_in_scope`
  * PZ evidence에서 save A/B session-bound identity 차이 또는 stale value reproduction 확인 → `adopted`
  * PZ transition을 실행했으나 candidate가 process-stable임을 negative fixture로 확인 → production diff 0, evidence-bound `complete/no-op`
* entry condition이 충족되면 session boundary ownership은 `IrisMain`의 단일 production handler에 둔다. `IrisMapIcon.onMainMenuEnter()`는 기존 UI button cleanup만 소유하고 전체 cache lifecycle owner가 되지 않는다.
* `Events.OnMainMenuEnter`가 여러 module에서 같은 cache를 중복 reset하지 않도록 single-writer를 둔다.
* Browser reset이 채택되면 session-dependent field와 lazy reference만 비우고 generation/epoch를 정확히 한 번 단조 증가시킨다. next build가 같은 transition을 다시 증가시키지 않도록 state machine을 명시한다.
* locale-dependent search keys/sorted source/prefix state의 in-session invalidation은 Change 3이 소유한다. locale 전환을 session reset에 결속하지 않는다.
* process-stable generated modules와 Tooltip summary를 무조건 unload하지 않는다. display line은 locale/revision ownership 및 Change 5 retention 정책으로 처리하고, session dependency가 별도로 증명된 경우에만 이 handler에 포함한다.
* reset이 채택되면 handler는 각 owner를 먼저 `invalidating`/unusable로 표시한 뒤 reference를 비운다. 일부 owner reset이 실패하면 diagnostics에 reason/owner를 남기고 해당 owner를 `invalid`로 유지해 stale data read를 금지하며, 다음 access는 clean rebuild/reload를 시도하거나 fail-closed한다. 실패 owner를 `ready`로 되돌리지 않는다.

Validation:

* source/runtime actual cache key set과 census receipt row key set exact equality
* census의 모든 cache field에 category/owner/input/invalidation/evidence가 존재함
* candidate 0일 때 production wiring diff 0과 `complete/no-op` disposition
* candidate 1개 이상/PZ unavailable fixture가 `deferred_by_design`·production diff 0·`unvalidated_but_in_scope`로 닫히며 no-op으로 기록되지 않음
* reset이 채택되면 session A build → main menu → session B build에서 generation 증가 정확히 1회
* session reuse test는 row나 static ScriptItem identity가 아니라 census에서 session-dependent로 판정된 engine object identity와 stale field value만 비교함
* 같은 session에서 process-stable row/item identity parity와 warm reopen 추가 full scan 0
* locale 전환은 Change 3 transaction만 발생하고 session reset count 0
* `OnMainMenuEnter` handler 중복 등록/중복 reset 0
* census가 `session_dependent_engine_object`로 판정한 모든 owner 각각의 reset failure injection 뒤 state=`invalid`, stale read 0, rebuild 또는 reason-coded fail-closed
* PZ 환경이 있으면 save A → main menu → save B Browser/Tooltip smoke를 별도 functional evidence로 기록하되, timing receipt로 취급하지 않음

---

### Change 3 — Browser row 중심 단일-pass candidate cache

Purpose:

item index 이후 세 차례 수행되는 full-map pass를 하나의 row materialization pass로 병합하고, public 반환 계약을 유지한 채 중복 내부 table과 tag reconstruction을 줄인다.

Files:

* `IrisBrowserData.lua`
* `IrisBrowserItemIndex.lua`
* `IrisBrowserClassificationIndex.lua`
* `IrisBrowserQuery.lua`
* `IrisBrowserVariantIndex.lua`
* `StaticData.lua` — existing private loader reuse
* `Tags.lua`와 `IrisAPI.lua` — protected public export manifest; implementation 변경 금지
* `Iris/test/lua/browser_state_acceptance_harness.lua` — classification failure-injection stub을 `addItem`에서 `addTag`로 이동

Implementation Notes:

* generation-local private row는 최소 다음 필드를 가진다.
  * `fullType`
  * `item`
  * `displayName`
  * folded search key
  * primary Browser location
  * primary classification tag
* item 객체는 mandatory path에서 row에 유지한다. `IrisBrowserData.getItem(fullType)`은 같은 object identity를 반환한다.
* `Tags.lua`에는 Browser 전용 accessor를 추가하지 않는다. `IrisAPI.Tags`가 module table 전체를 public 노출하므로 이름만 private인 exported function도 금지한다.
* Browser build는 existing private `StaticData` loader로 classification table을 build scope에서 한 번 얻고 이미 알고 있는 fullType의 tag array를 그 scope 안에서 scalar string으로만 순회한다. backing table/array는 function 밖으로 반환하거나 callback에 전달하지 않고 row/cache/public result에도 저장하지 않는다.
* `IrisBrowserClassificationIndex.addItem(index, fullType, tags)` table boundary는 `addTag(index, fullType, tag)` scalar boundary로 바꾼다. Browser build가 per-item `hasAnyTag`를 별도로 추적해 predecessor `taggedCount` 의미를 유지하고 duplicate/invalid tag도 기존 bucket/count behavior와 대조한다.
* `browser_state_acceptance_harness.lua`의 classification failure-injection stub도 실제 revised call path인 `addTag`를 대상으로 바꾼다. injected failure fixture는 stub call count가 1 이상임을 먼저 확인해 호출되지 않은 stub으로 test가 조용히 통과하지 못하게 한다.
* row에는 필요한 derived scalar인 primary tag/location만 저장한다. classification bucket에는 fullType/row identity만 넣고 backing tag array identity를 보존하지 않는다.
* classification bucket과 search index는 row 또는 fullType을 참조하며 display name/folded key/primary를 별도 fullType table에 중복하지 않는다.
* category/subcategory presentation order에서 `"Category.Subcategory" -> rank` map을 generation마다 한 번 만든다.
* primary Browser location은 tag를 classification bucket에 추가하는 같은 loop에서 최소 rank로 계산한다.
* `calculatePrimary()`에 필요한 primary tag도 같은 tag loop에서 계산하고 row에 저장한다. item list 렌더 시 `Tags.getTagsForItem()`을 다시 호출하지 않는다.
* variant grouping cache key는 generation-scoped `categoryName .. "." .. subcategoryName`을 사용한다. 이를 위해 `getFoldedCountCacheKey(subData)`를 `getFoldedCountCacheKey(categoryName, subcategoryName)`로 바꾸고 `_calculateFoldedCount()`와 display-group cache caller가 exact owner identity를 전달한다. 기존 fullType 정렬·concat key는 제거한다.
* search용 sorted row list의 cache key는 generation 단독이 아니라 `(generation, normalizedLocale)`다. locale A에서 만든 display name/order를 locale B에서 재사용하지 않는다.
* locale mismatch 처리는 search key 재생성, 같은 comparator를 사용한 global row list full re-sort, `searchPrefixState` clear를 하나의 invalidation transaction으로 수행한다. transaction 도중 partially refreshed state를 public query가 관찰할 수 없게 candidate를 완성한 뒤 교체한다.
* prefix filtering은 해당 `(generation, locale)`의 정렬된 상위집합 순서를 보존하므로 매 query `table.sort`를 수행하지 않는다.
* public search/getItems 결과는 consumer-local table을 계속 반환한다. internal row를 밖으로 노출하지 않는다.
* item 비보존 branch는 Change 1에서 heap/lifetime 절감이 material하고 `getItem` identity/lookup failure 계약을 보존할 설계가 승인된 경우에만 별도 commit으로 시험한다. 그렇지 않으면 no-op으로 닫는다.

Validation:

* engine item scan 1회, post-index full-map materialization pass 1회
* candidate item count, classification bucket, primary location, primary tag parity
* `IrisAPI.Tags` exported key set/signature가 predecessor와 exact equality이고 새 callable surface 0
* `getTags()` array와 `getTagsForItem()` Set 반환값을 mutate한 뒤 current classification/다음 Tags call/Browser result 불변
* Lua harness가 cycle guard와 `rawequal`을 사용해 Browser internal cache 및 public result graph를 재귀 순회하고 fixture의 backing classification top-level/nested sentinel identity 비도달 확인
* missing classification module, malformed top-level table, malformed per-key tag array에서 predecessor build state/taggedCount/errorCount/warning·failure reason parity
* `addTag(index, fullType, tag)`의 valid/invalid/duplicate/multi-classification bucket·location·count parity와 table-valued `addItem` boundary 부재
* `browser_state_acceptance_harness.lua`의 `addTag` failure-injection stub call count 1 이상, injected reason/state parity, legacy `addItem` stub 잔존 0
* public Browser row mutation이 다음 호출/cache에 영향 0
* 검색 empty/case/prefix/backspace/generation parity
* locale A sorted source 생성 → 같은 session의 locale B 전환 → 첫 query 결과가 locale B 기준 full re-sort와 동일
* locale 전환 transaction의 full sort 1회, 이후 같은 locale prefix query의 추가 full sort 0회
* locale 전환 시 search key/sorted source/prefix state owner key가 모두 `(generation, locale B)`로 일치
* locale B candidate 완성 전 injected query/failure가 partial B state를 관찰하지 않고 기존 A snapshot 또는 완성된 B snapshot만 관찰
* variant folded count, representative, order parity
* `getFoldedCountCacheKey(categoryName, subcategoryName)` signature/caller 및 duplicate-key/collision parity
* 같은 fullType item object identity parity

---

### Change 4 — ItemDetail ViewModel과 ObjectAccess fast path

Purpose:

ViewModel 한 번 생성하는 동안 반복되는 method-name table, capability hint 계산, generic vararg/closure allocation을 줄인다.

Files:

* `IrisItemDetailViewModel.lua`
* `IrisObjectAccess.lua`
* `IrisProtectedCall.lua` — signature 변경 없이 필요한 test hook만 검토
* ObjectAccess production consumer 16개

Implementation Notes:

* food/weapon/literature/moveable method 목록과 single-field method 목록을 module constants로 이동한다.
* `fullType`, `itemType`, category, capability hints를 `fromItem()` 호출당 한 번 계산한다.
* `groupApplicable()`은 이미 계산된 hints를 입력으로 받고 method-presence fallback을 유지한다.
* custom, contradictory, same-canonical hybrid item을 보존하기 위해 category/type hint가 false여도 method-presence 확인을 건너뛰지 않는다.
* `IrisObjectAccess.call0(target, methodName)`과 `call1(target, methodName, arg)`를 추가한다.
* public generic `call(target, methodName, ...)`은 0/1 argument를 fast path로 routing하고 2개 이상은 현재 unpack 기반 fallback을 유지한다.
* fast path는 `ProtectedCall.engine(method, target[, arg])`처럼 function/arguments를 직접 전달해 `{...}`와 wrapper closure를 만들지 않는다.
* 최대 1인자 수혜처는 `IrisBrowserItemIndex`의 `ObjectAccess.call(allItems, "get", i)` item scan이며 current corpus에서 약 2,200회다. Detail/ViewModel과 Browser scan counter를 분리해 한쪽의 절감을 다른 쪽에 귀속하지 않는다.
* Java/Kahlua method binding, nil result, missing method, thrown error 반환 shape `(ok, result)`를 유지한다.
* call0/call1의 Lua fixture는 implementation eligibility를 제공하지만 Java/Kahlua production routing adoption에는 representative PZ functional evidence가 필요하다. PZ가 없으면 fast path는 public generic path에 승격하지 않고 `deferred_by_design`으로 둔다. 이미 구현됐다면 rollback 전 상태만 `implemented_only`이며, generic path rollback과 production diff 0을 검증한 최종 closeout은 deferred branch를 가진 overall `partial`이다.
* 완성 ViewModel 또는 InventoryItem-dependent section을 fullType으로 cache하지 않는다.
* readonly proxy 개선은 원본 array length를 side metadata로 노출해 실제 scan 감소가 측정될 때만 conditional로 수행한다.

Validation:

* 0/1/2+ argument generic/fast path parity
* Lua function stub와 representative Java/Kahlua object method parity
* PZ functional evidence unavailable fixture에서 fast-path production routing이 adopted/complete로 잘못 봉인되지 않음
* missing method, thrown error, nil/false/0 result parity
* Detail/ViewModel item 100개 corpus의 method attempt/engine call/temporary table count before-after
* Browser `allItems:get(i)` full scan의 call1 invocation/temporary vararg table/wrapper closure count before-after
* food/weapon/literature/moveable/custom/hybrid output parity
* 같은 fullType의 서로 다른 InventoryItem `sourceItem`, weight, food state 교차 오염 0

---

### Change 5 — DEBUG와 Tooltip/display cache allocation 경량화

Purpose:

DEBUG=false에서 dynamic message가 먼저 구성되는 경로와 revision 축이 계속 누적될 수 있는 Tooltip display cache를 정리한다.

Files:

* `IrisLogger.lua`
* `IrisModuleBootstrap.lua`
* dynamic DEBUG call owner modules
* `IrisAltTooltip.lua`
* 필요 시 `IrisTooltipSummary.lua`

Implementation Notes:

* static literal debug call은 그대로 둘 수 있다. concat, `tostring`, `string.format`, byte/table dump가 있는 unguarded call만 caller-side `isDebugEnabled()`로 감싼다.
* loop 안에서는 guard를 iteration마다 다시 resolve하지 않고 function-local boolean을 한 번 얻는다.
* lazy callback 방식은 DEBUG=false에서도 closure를 만들 수 있으므로 기본 해법으로 사용하지 않는다.
* DEBUG=true message 내용과 ordering은 유지한다.
* `displayLineCache[fullType]`는 현재 locale/revision entry 하나만 보존해 locale/revision 전환 시 이전 nested entry를 교체한다.
* fullType entry 수 제한은 Change 1의 hover corpus와 memory proxy에서 material한 증가가 확인될 때만 LRU/상한으로 채택한다.
* Alt active path의 `ItemKey.getFullTypeFromItem`, `TranslationResolver.getLangKey`, `tostring` key 변환, nested detail-line lookup은 measurement-gated 후보로 포함한다. render당 call/allocation counter가 material할 때만 동일 tooltip item/locale/revision 범위의 derived key를 재사용하며 InventoryItem instance fact를 fullType 전역 cache로 승격하지 않는다.
* display line/summary cache를 Change 2 session handler에서 비우는 것은 해당 field가 session-dependent로 판정될 때만 수행한다. locale/revision retention은 이 Change가 독립 소유한다.
* `ipairs(x or {})`, module-local empty table, bootstrap fallback allocation은 hot path counter가 실제 비용을 보인 owner에만 좁게 적용한다.

Validation:

* DEBUG=false dynamic message build counter 0
* DEBUG=true 기존 대표 log text/order parity
* inactive Alt temporary table 0과 warm line copy 0 predecessor invariant 유지
* Alt active cold/warm render의 fullType/locale/tostring/nested lookup call 및 temporary allocation count before-after; threshold 미달이면 no-op
* locale/revision 전환 뒤 old nested cache entry 잔존 0
* display line output/최대 4줄/높이 parity

---

### Change 6 — Tooltip static projection과 LineCount lazy validation

Purpose:

Tooltip first-use의 여러 module load/runtime 조합 비용을 줄일 수 있는지 판정하고, 별도 결정 없이 integrity contract를 제거하지 않으면서 `LineCountIndex` eager 비용을 지연한다.

Files:

* `IrisTooltipSummary.lua`
* `IrisUseCaseDescriptionsLookup.lua`
* `convert_descriptions_to_lua.py`
* Recipe/Moveables/Fixing/Classifications owning generator
* package/lookup validator
* conditional `IrisTooltipSummaryData.lua`

Implementation Notes:

* mandatory 변경은 `ChunkIndex`/`LineCountIndex` require와 validation을 module top-level에서 제거하되 기존 `get()`과 `getLineCount()` fail-loud/independent-validity contract를 모두 보존하는 것이다. 양 public lookup entrypoint의 first demand에서 두 index metadata를 함께 lazy materialize하되 composite all-or-nothing verdict를 만들지 않는다.
* `ensureIndexMetadataSnapshot()`은 두 index를 모두 require/self-validate하고 다음 세 field를 하나의 immutable snapshot으로 atomic publish한다.
  * `chunkState = unloaded | valid | invalid(reason)`
  * `lineCountState = unloaded | valid | invalid(reason)`
  * `crossCheckState = not_applicable | valid | invalid(index_content_mismatch)`
* `crossCheckState`는 두 self-state가 모두 `valid`일 때만 entry-count를 비교해 `valid`/`invalid`가 되며, 어느 한 self-state가 invalid면 `not_applicable`이다. snapshot atomicity는 partial publication만 막고 독립 self-validity를 하나의 valid/invalid flag로 합치지 않는다.
* entrypoint별 gate는 다음처럼 고정한다.
  * `get()` → `chunkState=valid`, `lineCountState=valid`, `crossCheckState=valid` 필요
  * `getLineCount()` → `lineCountState=valid`이고 `crossCheckState!=invalid` 필요; `chunkState` self-invalid 자체는 실패 조건이 아님
* 첫 `get(fullType)`은 integrity gate를 통과한 뒤에만 record 탐색을 시작한다. invalid LineCountIndex, index entry-count mismatch, router-record 부재+line-count 존재, entry/line-count 한쪽 부재, `#entry.lines` mismatch의 기존 reason과 fallback 순서를 유지한다.
* 첫 `getLineCount(fullType)`도 두 index metadata의 load/self-validation을 시도하고 둘 다 valid면 entry-count를 cross-check하지만 description chunk는 불러오지 않는다. ChunkIndex missing/malformed + valid LineCountIndex이면 cross-check는 `not_applicable`이고 predecessor처럼 정상 count 또는 `(0, nil)`을 반환한다.
* chunk index와 line-count index는 각각 독립적인 `unloaded`, `valid`, `invalid(reason)` state를 가진다. `get()`은 target chunk 전체의 record count/first/last shape를 기존처럼 검증하고 requested entry의 line-count를 검증한다. unrelated description chunk는 load하지 않는다.
* loaded target chunk의 line-count content cross-check는 predecessor처럼 requested fullType 한 건에만 수행한다. 같은 chunk의 다른 entry는 해당 key가 나중에 requested될 때 검사하며, 이 Change에서 chunk 전체 line-count scan으로 확대하지 않는다.
* invalid index는 기존 reason-coded fallback을 유지하며 정상 miss로 위장하지 않는다.
* valid integrity snapshot에서 LineCountIndex에 fullType이 없으면 `getLineCount(fullType)`은 predecessor와 동일하게 authoritative negative `0, nil`을 반환한다. absent key는 fallback이나 `lookup_miss`가 아니다.

Entrypoint state matrix:

| ChunkIndex self-state | LineCountIndex self-state | Cross-check | `get()` | `getLineCount()` |
|---|---|---|---|---|
| valid | valid | valid | 정상 | 정상 |
| invalid | valid | not_applicable | chunk reason fallback | 정상 count 또는 `(0, nil)` |
| valid | invalid | not_applicable | line-count reason fallback | line-count reason fallback |
| valid | valid | `index_content_mismatch` | `index_content_mismatch` fallback | `index_content_mismatch` fallback |
* package validator는 chunk key/count/boundary/hash/generation과 line count를 전수 비교한다. runtime lazy validation은 이 build/package 검증을 보완하며 대체되지 않는다.
* `IrisRuntimeLookupDiagnostics.lua`에서 Change 6이 소유하는 변경은 index materialization state/count와 기존 fallback reason의 owner attribution뿐이다. normal miss/fault vocabulary를 새로 만들지 않는다.
* `IrisTooltipSummary.countUseCaseLines()`가 first `getLineCount()`에서 invalid index를 만나 full `IrisUseCaseDescriptions` facade로 fallback하는 시점도 module load가 아니라 첫 Tooltip demand로 이동한다. Change 1 counter로 이 fallback 시점/owner를 관측하고 정상 miss와 분리한다.
* Tooltip static projection은 `PZ-7-TOOLTIP-01`과 `PZ-7-LINECOUNT-01`에서 first-use 비용이 확인될 때만 채택한다.
* projection은 기존 Classifications/Recipe/Moveables/Fixing/UseCase count에서 결정론적으로 생성한다.
* tag strings, connection flags, useCaseCount는 compact tuple/intern table로 표현할 수 있지만 public `IrisTooltipSummary.get()`은 기존 sorted tags/connections/useCaseCount/revision shape를 copy-on-read로 반환한다.
* 새 generator module이 필요하면 current core 12/allowed tooling 4/4 admission을 먼저 해결한다. slot 승인 없이 convenience generator를 추가하지 않는다. 승인되지 않으면 Tooltip projection branch는 `deferred_by_design` 또는 no-op이다.
* projection payload bytes, first Alt loaded module/byte count, build determinism을 함께 비교한다. package bytes만 늘고 first-use 절감이 material하지 않으면 채택하지 않는다.

Validation:

* require-only 시 chunk/line-count require 및 validation scan 0
* first `get()` 시 ChunkIndex/LineCountIndex materialization·self-validation 각 1회와 applicable entry-count cross-check 1회, repeat `get()` validation 0
* first `getLineCount()` 시 ChunkIndex/LineCountIndex materialization·self-validation 시도 각 1회, 양쪽 valid fixture의 entry-count cross-check 1회, description chunk materialization 0, repeat `getLineCount()` validation 0
* `getLineCount()` 선행 뒤 first `get()`에서 metadata validation 0, target description chunk만 demand load
* `get()`-first fixture에서 router record 없음+LineCount entry 존재가 `lookup_miss`가 아니라 `index_content_mismatch`
* corrupt LineCountIndex 상태의 first call이 `get()`일 때 predecessor reason/fallback parity
* entry-count mismatch 상태의 first call이 `getLineCount()`일 때 count 미반환 및 predecessor `index_content_mismatch` fallback parity
* missing ChunkIndex + valid LineCountIndex와 malformed ChunkIndex + valid LineCountIndex에서 first `getLineCount()` count/absent parity, fallback counter 증가 0, full facade load 0
* valid ChunkIndex + malformed LineCountIndex에서 `get()`/`getLineCount()` 모두 predecessor line-count reason fallback
* valid LineCountIndex absent key의 exact result `(0, nil)` 및 fallback counter 증가 0
* target chunk 전체 record shape와 requested entry 한 건의 line-count 검증, same-chunk unrequested entry scan 0, unrelated chunk load 0
* valid/missing/malformed/count mismatch/module mismatch reason parity
* Tooltip first demand의 LineCount invalid → full facade fallback timing/owner counter와 output parity
* Tooltip 기존 runtime 조합 결과와 generated projection 전 fullType parity
* sorted tags, Recipe/Moveables/Fixing flags, useCaseCount parity
* public mutation isolation과 revision determinism
* source/package generated identity 및 disposable package smoke

---

### Change 7 — exact-parity legacy IrisData compact reconstruction disposition

Purpose:

현재 75,143-byte legacy classification payload를 exact legacy semantics와 authority isolation을 훼손하지 않는 compact representation으로 줄일 수 있는지 판정한다. parity 또는 material한 byte/load 이득이 없으면 기존 파일을 유지하는 `complete/no-op`으로 닫는다.

Files:

* `Iris/Data/IrisData.lua`
* `Iris/Data/IrisClassifications.lua` — read-only comparison authority
* `StaticData.lua`
* `IrisBrowserData.lua`
* `IrisBrowserVariantIndex.lua`
* `Iris/build/main.py`

Implementation Notes:

* 이 Change는 measurement-gated이며 **정책 A — exact legacy semantic parity**를 적용한다. Phase 0a ordinal parser receipt의 1,360 assignment/1,360 unique key/duplicate 0, tag array 값·순서, missing-key `nil`을 compatibility fixture로 봉인한다.
* compact candidate는 tag dictionary/tuple 등 독립 representation에서 `IrisData.Classifications` public table을 materialize할 수 있다. current `IrisClassifications` table 또는 그 nested tag array를 public legacy table에 직접 alias하지 않는다.
* `IrisData = IrisData or {}` global identity, direct require side effect, public mutable table shape를 유지한다. external code가 legacy table 또는 nested tag array를 mutate해도 current `IrisAPI.Tags`/`IrisClassifications` 결과는 변하지 않아야 한다.
* 동일한 tag tuple을 intern하더라도 public materialization 시 legacy key마다 새 nested array를 만든다. key A의 tag array mutation은 같은 tuple을 가진 key B에 전파되지 않아야 한다.
* current-only 719개 key를 legacy table에 추가하지 않고, 현재 값이 다른 공통 4개 key도 legacy fixture 값을 유지한다. 이 숫자는 line-record parser의 baseline이며 executable parity fixture/hash가 최종 authority다.
* current `IrisData.ItemGroups` producer는 만들지 않는다. 외부 code가 prepopulate한 `IrisData.ItemGroups`는 덮어쓰거나 제거하지 않는다.
* `StaticData.getLegacyIrisData()`와 `IrisBrowserData.getGroupVariants(groupId)` signature/`nil`/order behavior를 유지한다.
* `getGroupVariants`는 이 계획에서는 permanent named compatibility adapter다. 제거 후보 전환은 repository/test/dynamic external consumer proof와 별도 architecture decision이 있는 후속 계획에서만 가능하다.
* generator는 legacy fixture로부터 compact payload를 결정론적으로 쓴다. current classification content 갱신을 optimization generator의 부수 효과로 만들지 않는다.
* adoption threshold는 baseline receipt에 미리 봉인하고 source/package domain을 합산하지 않는다.
  * source `IrisData.lua` logical bytes: 기준 75,143 bytes보다 `max(4,096 bytes, 10%)` 이상 감소
  * source `Iris/Data` domain total logical bytes: 비증가
  * disposable package `IrisData.lua`: source candidate와 byte-identical이며 동일 절감량
  * disposable package `Iris/Data` domain total logical bytes: 비증가
  * `publicTopLevelTableAllocations=1`, `publicNestedArrayAllocations=classification_baseline.json.legacy.uniqueKeyCount`, `publicTagScalarWrites=baseline` exact equality
  * candidate `materializationOps`: baseline의 110% 이하
* 위 domain/operation 조건 중 하나라도 충족하지 못하면 no-op이다. 이 operation proxy는 latency가 아니며 PZ timing이 없으면 latency 개선을 claim하지 않는다.
* repository consumer census에서 exact old-byte/hash를 요구하는 historical tool은 current runtime generation과 분리하고 필요하면 historical fixture를 별도 경로에 보존한다. undocumented third-party total compatibility는 claim하지 않는다.
* 모든 known direct/external consumer 검증 전에는 `IrisData.lua`, global, StaticData key, Browser adapter를 제거하지 않는다.

Validation:

* `require("Iris/Data/IrisData")` 및 global `IrisData` shape
* baseline legacy unique key map/tag array value·order/missing-key `nil` exact semantic parity
* case-sensitive assignment/unique/duplicate/current-only/differing-key receipt 재현과 input/parser hash parity
* current-only key 부재와 current-different legacy key 보존
* public legacy top-level/nested mutation 후 current `IrisClassifications` 및 `IrisAPI.Tags` 결과 불변
* 동일 tag tuple을 가진 legacy key A nested array mutation 후 key B 결과/identity 불변
* external prepopulated `ItemGroups` 보존
* missing/present group variant result/order parity
* current source/package direct require smoke
* source artifact/domain과 disposable package artifact/domain의 logical bytes를 각각 before/after 비교하고 어느 domain도 합산으로 상쇄하지 않음
* cold materialization 다섯 counter와 derived `materializationOps` before/after; public identity가 다르거나 110% ceiling 초과 시 `complete/no-op`
* 같은 immutable legacy input과 harness identity를 사용한 clean Lua state 최소 2회의 다섯 counter 및 derived `materializationOps` exact equality; 회차 간 값이 다르면 baseline/adoption 판정 차단
* 두 개의 서로 다른 clean output root에서 동일 legacy input으로 생성한 file set/bytes/manifest hash 일치
* historical exact-byte consumer가 발견되면 별도 disposition 없이는 변경 차단

---

### Change 8 — generated Lua compact representation

Purpose:

이미 적용된 sparse field 제거 다음 단계로, internal UseCase/Layer3 chunk의 반복 field name/state string을 줄이되 facade와 renderer의 공개 shape를 보존한다.

Files:

* `convert_descriptions_to_lua.py`
* `export_dvf_3_3_lua_bridge.py`
* UseCase/Layer3 chunk lookup/renderer/facade
* generated chunk directories와 manifests

Implementation Notes:

* 이 Change는 measurement-gated다. 먼저 각 반복 field/state string의 byte contribution과 decode table/closure/runtime cost를 산출한다.
* internal chunk는 positional tuple, field dictionary, interned state/source ID 중 가장 작은 독립 후보로 생성한다.
* compatibility facade는 현재 named table shape, optional field absence, `debug_lines={}` rehydration을 유지한다.
* lookup router는 target chunk 하나만 demand-load하는 invariant를 유지한다.
* Layer3 `source`, `publish_state`, `text_ko` 의미와 public renderer output을 변경하지 않는다.
* package manifest는 representation schema version, generator identity, chunk count/key range/hash를 결속한다.
* direct chunk require가 supported surface인지 Phase 0 census로 판정한다. supported direct chunk consumer가 있으면 adapter 없이는 positional representation을 채택하지 않는다.
* before-after package bytes와 runtime decoded table/temporary allocation을 함께 본다. byte 절감만 있고 runtime 비용이 악화되면 no-op으로 닫는다.

Validation:

* full key/entry semantic parity
* public facade exact shape 및 consumer-local mutation parity
* Layer3 text/source/publish-state parity
* UseCase line order/requirements/capabilities parity
* 서로 다른 두 clean output root에서 generator를 한 번씩 실행한 file set/bytes/manifest byte-identical determinism
* chunk demand-load count와 fallback count parity
* package file set/hash/identity validation

---

### Change 9 — RecipeIndex 및 기타 low-cardinality candidate disposition

Purpose:

로드맵에 포함된 linear membership, readonly array, empty table/bootstrap 후보를 현재 cardinality와 hot-path 증거로 판정한다.

Files:

* `IrisRecipeIndex.lua`
* `build_iris_recipe_index_data.py`
* `IrisItemDetailViewModel.lua`
* `IrisModuleBootstrap.lua`
* 후보 owner module

Implementation Notes:

* current `getItemTypes.CanOpener`는 1개 item이므로 Set 생성은 기본 no-op이다.
* generator가 미래 group cardinality threshold를 넘는 경우에만 membership Set 또는 dual representation을 생성한다.
* readonly array length side metadata는 실제 `copyArray`/`arrayLength` scan count가 material할 때만 추가한다.
* module bootstrap table/fallback closure는 module load 1회 비용이므로 hot-path candidate와 섞지 않는다.
* `ipairs(x or {})`는 shared immutable empty constant가 mutation되지 않는 read-only loop에서만 교체한다.

Validation:

* current no-op 근거에 exact group count/length 기록
* Set branch가 채택되면 membership true/false 및 public data shape parity
* readonly length/copy parity와 Kahlua iteration compatibility
* bootstrap failure fallback log parity

---

### Change 10 — Python current run-local I/O/hash reuse

Purpose:

global helper 강제 공통화 없이, 하나의 current producer/validator 실행 안에서 같은 immutable input을 반복 read/hash하는 비용만 줄인다.

Files:

* `compose_layer3_text.py`와 현재 owning compose modules
* `export_dvf_3_3_lua_bridge.py`
* `convert_descriptions_to_lua.py`
* current package/validation entrypoint
* active core/allowed tooling manifest — admission/ownership이 실제 변할 때만

Implementation Notes:

* Phase 0에서 denominator ID와 함께 `(resolved path, size, mtime_ns)`별 read/hash count를 instrumentation-only로 수집한다.
* first read는 resolved path, `size`, `mtime_ns`, bytes, SHA-256을 run context에 저장한다. 후속 lookup은 먼저 stat identity를 비교하고 동일할 때 bytes와 hash를 함께 재사용한다. stat identity가 달라지면 즉시 다시 읽고 hash를 재계산한다.
* same-process immutable input만 재사용한다. phase 사이 write가 가능한 path는 cache하지 않거나 writer가 atomic replace 직후 exact path를 explicit invalidate한다. 같은 size/mtime을 인위적으로 복원하는 mutation은 immutable-input 계약 위반으로 fixture에서 별도 탐지하며 stat cache의 correctness claim으로 숨기지 않는다.
* JSON object, JSONL rows, SHA-256을 서로 다른 cache namespace로 둔다.
* pure validator는 parsed input을 받을 수 있게 하되 CLI, cwd, stdout/stderr, exit code, atomic write 계약은 entrypoint가 계속 소유한다.
* cross-script global helper는 전체 path/encoding/newline/error/atomicity 계약이 같은 current consumer 3개 이상이 다시 확인될 때만 별도 승인한다. 선행 closeout의 exact group 0 결론을 근거 없이 뒤집지 않는다.
* 13,219 line-record/12,798 nonblank-line `dvf_3_3_registry_authority_canonical_closure.py`는 sealed governance owner다. authority/registry/render/receipt 책임 분할은 별도 owner plan, import graph, mode/CLI golden, allowed-module disposition이 승인될 때만 착수한다. 이 계획의 mandatory 완료 조건은 아니다.
* subprocess는 process boundary가 계약인 테스트/CLI에서 유지한다. 단지 호출 수를 줄이기 위해 in-process로 바꾸지 않는다.

Validation:

* same input read/hash count before-after
* first read의 bytes/hash 저장과 unchanged stat의 bytes/hash reuse count
* parsed payload/hash/output bytes/exit code/stdout/stderr parity
* size/mtime_ns 변화, atomic replacement, explicit invalidation 뒤 stale cache 0과 reload/hash 재계산
* CLI golden 및 working-directory/error fixture
* current exact route와 clean disposable generator determinism
* 분할 branch는 모든 public symbol/import/mode/receipt schema parity가 있을 때만 채택

---

### Change 11 — staging/evidence lifecycle 재판정

Purpose:

현재 저장소의 큰 물리량을 lifecycle/consumer closure 기준으로 다시 분류하되, 절감량을 위해 안전 조건을 완화하지 않는다.

Files:

* existing lifecycle manifests and CAS codec under `Iris/validation/residual_refactor/`
* `Iris/build/description/v2/staging`
* `Iris/build/description/v2/evidence`
* 새 plan-local eligibility/consumer/restore/final census receipts

Implementation Notes:

* predecessor의 306 duplicate groups/113,083,892 gross bytes는 후보 baseline일 뿐 safe deletion 목록이 아니다.
* current authority, current-required evidence, historical reproduction, diagnostic-only, generated projection, disposable 역할을 재분류한다.
* exact path, content hash, producer, consumer, required reference, recovery source를 각 row에 기록한다.
* safe candidate 조건은 consumer closure, authority 비해당, exact CAS/archive restore, byte parity, dangling reference 0, owner disposition을 모두 요구한다.
* content equality만으로 provenance가 다른 artifact를 합치지 않는다.
* safe candidate 0이면 mutation 없는 no-op으로 닫는다.
* cold archive는 checkout 밖의 owner-managed exact root에 만들고 verify/restore 뒤에만 local disposition을 수행한다.
* recursive delete/move 전 exact absolute path가 workspace의 승인된 staging/evidence 대상 안인지 검증한다.

Validation:

* byte count, duplicate gross/net bytes, eligibility count
* current/historical consumer closure
* CAS/archive verify/restore exact byte parity
* dangling reference 0
* source/current/package protected hash no-mutation
* final physical census는 실제 disposition 뒤 측정하고 예상 절감과 분리

---

### Change 12 — 통합 adoption 결정과 closeout

Purpose:

각 Change의 mandatory/conditional 결과를 숨김 없이 `adopted`, `complete/no-op`, `deferred_by_design`, `blocked`로 종결하고 top-level authority에는 실제 변경된 계약만 반영한다.

Files:

* `Iris/_docs/refactor/codebase_optimization_followup/closeout_receipt.json`
* `validation_matrix.json`
* `protected_surface_manifest.json`
* 필요한 경우 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`

Implementation Notes:

* before/after corpus와 implementation commit/tree를 각 claim에 결속한다.
* Phase 0a와 unconditional Change가 모두 구현·검증되고, owner/measurement-gated Change가 사전 정의된 disposition으로 닫혀야 한다. optional timing branch의 deferred는 `complete`와 양립하지만 engine-bound `unvalidated_but_in_scope` deferred는 양립하지 않는다.
* conditional Change는 사전 정의한 threshold에 따라 adopted/no-op/deferred로 닫는다.
* Phase 0b PZ timing/heap 증거가 없는 branch에 performance 또는 memory 개선 claim을 붙이지 않는다. 그 부재는 Phase 0a와 독립적인 pure-Lua structural/correctness adoption을 차단하지 않는다. PZ functional evidence 부재는 Change 2/4의 별도 closeout mapping을 따른다.
* configured full advisory failure는 modified/mandatory dependency intersection으로 분류하되 full-suite PASS로 다시 쓰지 않는다.
* independent review와 owner/manual runtime evidence는 서로 대체하지 않는다.

Validation:

* closeout schema, artifact hash, implementation commit/tree binding
* protected current/source/package surface diff
* all mandatory focused/current/Lua/package rows의 evidence presence와 PZ timing/functional row의 executed/deferred/overall-effect 분리
* validation ceiling의 `validated`, `out_of_scope`, `unvalidated_but_in_scope` 분리
* top-level docs의 claim과 machine receipt 1:1 equality

---

## 7. Validation Plan

### Automated Validation

계획 실행 중 각 Change는 focused command를 먼저 실행하고, phase adoption 시 integration command를 실행한다. prior review에서 관측된 current route 470 tests/약 307초, contract runner 219 tests/약 171초, configured full 645 tests/약 406초는 scheduling 참고치일 뿐 current PASS/count authority가 아니다. 각 실제 integration 회차는 command, test count, exit code, wall-clock을 receipt에 기록하고 변경마다 configured full을 중복 실행하지 않는다.

```powershell
uv run python -m pytest -q --round3-contract=all <plan-focused-test-files>
```

```powershell
uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure
```

```powershell
uv run python -m pytest -q --round3-contract=current --round3-enforce-denominator
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

필수 자동 validation axis:

* cache-owner census와 조건부 session state transition/generation/reset ownership
* Browser item/classification/primary/`(generation, locale)` search/variant parity
* public Tags export manifest/copy-on-read/backing authority isolation과 direct facade shape
* ViewModel instance isolation와 ObjectAccess Kahlua-compatible fast path
* DEBUG false/true behavior
* Tooltip summary/LineCount valid, missing, corrupt package 및 `get()`-first / `getLineCount()`-first per-index/cross-check integrity parity
* generator deterministic bytes와 source/package identity
* `layer3_renderer`, `IrisBrowserInteractionRenderer`, `IrisTooltipSummary` fallback instrumentation
* `getFoldedCountCacheKey(categoryName, subcategoryName)` caller/collision parity
* ordinal classification baseline receipt와 legacy `IrisData` exact semantics, direct require/global/cross-key mutation isolation/external ItemGroups compatibility
* Python run-local cache stale-input guard와 CLI parity
* lifecycle consumer/restore/dangling-reference guard

Generated data는 checkout 밖의 두 빈 output root에 같은 input identity로 두 번 생성하고 file set, byte hash, manifest hash를 비교한다. source tree나 existing `Iris/build/package/Iris`에 `-Clean`을 실행하지 않는다.

Configured full `--round3-contract=all` execution은 clean disposable checkout에서 advisory로 실행한다. current/modified/mandatory invariant failure는 blocking이며, historical/diagnostic-only failure는 dependency intersection과 함께 분리 기록한다. exit code가 0이 아니면 configured full-suite PASS를 주장하지 않는다.

### Manual Validation

Project Zomboid B41 환경이 제공되면 다음 functional smoke를 별도 축으로 확인한다. 특히 Change 2 candidate와 Change 4 Java/Kahlua fast path는 standalone Lua evidence만으로 engine-bound functional validation을 대체하지 않는다.

* save A에서 Browser 첫 열기와 warm reopen
* Change 2 reset이 채택된 경우 main menu 복귀 후 save B 진입 및 census가 session-dependent로 판정한 exact field의 잔존 여부
* category → subcategory → item 선택과 keyboard/mouse selection
* 이름/fullType 검색, 대소문자, prefix 추가/삭제, locale 변경
* 같은 display name variant folding과 primary marker/order
* base item과 mod item의 Browser/Wiki detail
* 같은 fullType이지만 instance state가 다른 두 InventoryItem 교대 표시
* Alt inactive, first Alt, warm Alt, locale 전환, 4줄 제한
* Layer3/UseCase missing key와 corrupt dev fixture의 miss/fault 구분
* DEBUG off에서 spam/동적 dump 부재, DEBUG on에서 대표 진단 유지
* direct legacy facade를 사용하는 dev fixture와 external-style dynamic require

Phase 0b가 실행되어 성능 채택을 주장하는 항목은 같은 PZ build/machine/save/mod-set/locale에서 before/after 각 10회 raw sample을 기록한다. median, p95, max, cold/warm 구분과 run order를 남긴다. PZ timing이 없으면 timing-dependent branch만 `deferred_by_design`이며, standalone Lua operation/allocation/byte/parity evidence로 latency/heap 개선을 주장하지 않는다. PZ functional evidence가 없는 engine-bound candidate/implementation은 별도로 `unvalidated_but_in_scope`와 branch disposition을 기록한다.

### Validation Limits

기본적으로 다음은 수행하지 않는다.

* multiplayer/dedicated server validation
* 장시간 memory leak/soak validation
* B42 validation
* 모든 third-party mod와 undocumented dynamic consumer 전수 sweep
* Workshop upload, deployment, release readiness validation
* Git history 크기 축소 검증
* 실제 LLM token usage 개선 측정

Pure-Lua transformation은 focused Lua fixture, exact current route, package parity로 mandatory runtime evidence를 닫을 수 있다. 반면 session transition과 Java/Kahlua method binding은 engine-bound surface이므로 candidate/implementation이 존재할 때 PZ functional evidence가 없으면 `unvalidated_but_in_scope`다. Change 2는 production diff 0의 `deferred_by_design`으로 overall `partial`이다. Change 4 fast-path routing code가 tree에 남으면 `implemented_only`, generic path rollback과 production diff 0까지 검증하면 deferred branch를 가진 overall `partial`이다. known external/direct consumer, representative mod item, generated facade도 계획이 직접 변경하고 validation하지 못하면 같은 ceiling을 적용한다. 신뢰 가능한 heap API가 없으면 item/table proxy까지만 기록하고 heap 절감은 non-claim이다.

---

## 8. Risk Surface Touch

### Authority Surface

중간~높음. Tooltip projection과 compact generated representation은 기존 authority의 파생물이어야 하며 새 의미 authority가 되어서는 안 된다. `Tags.lua`/`IrisAPI.Tags` export는 늘리지 않고 Browser가 backing tag array를 외부 object graph에 저장하지 않는다. `LineCountIndex` runtime validation 책임은 유지하고 module-load에서 first-demand로 시점만 지연한다. legacy `IrisData`는 current authority와 alias되지 않는 exact-parity compatibility table로 유지한다.

### Runtime Behavior Surface

높음. evidence가 있을 때의 session invalidation, Browser cache 표현, `(generation, locale)` search ordering, primary 계산, ObjectAccess, Tooltip summary/LineCount loading을 직접 건드린다. 사용자 표시 의미는 바꾸지 않지만 state/lazy-loading/failure path가 변한다.

### Compatibility Surface

높음. public Tags, Browser return rows, `IrisData` global/direct require, UseCase/Layer3 facade, Java/Kahlua protected method call을 보존해야 한다. internal chunk direct require가 supported인지 census로 확인한다.

### Sealed Artifact Surface

높음. generated Lua, package manifest, current-route validator, staging/evidence lifecycle을 다룬다. 선행 closeout evidence와 기존 종합 계획은 수정하지 않는다.

### Public-Facing Output Surface

중간. Browser order/primary marker, Tooltip lines, ItemDetail facts, Layer3/UseCase text가 사용자에게 보인다. 의도된 wording/meaning 변경은 없다.

---

## 9. Risk Analysis

### Architecture Risk

* row cache가 새 classification authority로 오인될 수 있다.
* Tooltip static projection이 원본 indexes와 별도 truth source로 굳어질 수 있다.
* `IrisData` reconstruction이 legacy semantics를 current semantics로 바꾸거나 current writer authority와 mutable alias될 수 있다.
* run-local Python cache가 phase mutation을 숨기거나 current core/allowed tooling 경계를 우회할 수 있다.
* 대형 script 분할이 기존 sealed mode/receipt ownership을 훼손할 수 있다.

Mitigation:

* row/projection은 generation-local derived view로 명시한다.
* generator parity와 same-generation package identity를 필수화한다.
* `IrisData`는 ordinal parser로 봉인한 1,360-key legacy map을 key별 독립 nested array로 materialize하며 current top-level/nested table을 참조하지 않고 새 ItemGroups semantics를 만들지 않는다.
* Python reuse는 single-process immutable input과 explicit invalidation에 한정한다.
* module admission/owner plan 없는 대형 분할은 no-op/deferred로 닫는다.

### Runtime Risk

* owner evidence 없는 session reset은 process-stable cache를 불필요하게 버리고 cold rebuild를 추가할 수 있으며, 부분 reset 실패 뒤 owner state를 ready로 남기면 stale data가 재사용될 수 있다.
* primary location과 primary tag를 한 loop에서 계산하면서 서로 다른 priority 규칙을 혼동할 수 있다.
* prefix result 재정렬 제거가 `(generation, locale)` source ordering을 보장하지 못하면 locale 전환 뒤 결과 순서를 바꿀 수 있다.
* fixed-arity ObjectAccess가 Java/Kahlua self binding을 바꿀 수 있다.
* lazy integrity가 per-index self-state와 applicable cross-check를 분리하지 않으면 unrelated ChunkIndex failure가 valid LineCount 결과를 fallback시킬 수 있다. 반대로 양 index가 self-valid일 때 cross-check를 생략하면 mismatch가 normal miss/count로 축소될 수 있고, metadata 활성화 비용은 첫 lookup에 집중될 수 있다.
* display-line cache 상한이 warm reuse를 악화시킬 수 있다.

Mitigation:

* cache owner census를 entry gate로 두고, reset은 invalidate-first state transition과 failure injection을 통과한 경우에만 채택한다.
* Browser presentation rank와 description primary priority를 별도 map/field로 유지한다.
* `(generation, locale)` search source를 먼저 stable sort하고 locale transaction으로 일괄 교체한 상위집합에서만 order-preserving filter한다.
* call0/call1을 generic path와 Kahlua fixture에서 대조하고 engine evidence가 없으면 production routing을 채택하지 않는다.
* `ensureIndexMetadataSnapshot()`이 두 self-state와 applicable cross-check를 atomic publish하게 하되 all-or-nothing verdict를 금지한다. `get()`은 Chunk+LineCount+cross-check를 요구하고, `getLineCount()`은 LineCount와 non-invalid cross-check만 요구하는 상태 행렬 및 corruption-first reason golden을 통과하게 한다.
* cache 상한은 measurement-gated로 유지한다.

### Compatibility Risk

* Browser 최적화 helper를 `Tags.lua`에 export하면 `IrisAPI.Tags`의 암묵적 public API가 되고 backing classification mutation 경로를 만들 수 있다.
* compact legacy materializer가 case-sensitive key, tag order, missing-key `nil`을 바꾸거나 public mutation을 current authority/같은 tuple의 다른 key에 전파할 수 있다.
* compact chunk를 직접 require하는 external consumer가 named fields를 기대할 수 있다.
* ObjectAccess nil/false/0 처리 차이가 caller behavior를 바꿀 수 있다.
* runtime lazy validation과 build validator가 다른 reason vocabulary를 사용할 수 있다.

Mitigation:

* Tags/IrisAPI export manifest를 동결하고 Browser build-scope scalar iteration만 허용하며 public return 및 cache object graph mutation-isolation test를 둔다.
* ordinal legacy-map golden과 authority/cross-key mutation-isolation test를 모두 통과하지 못하면 Change 7은 no-op으로 닫고 exact-byte consumer는 historical fixture disposition 없이는 변경하지 않는다.
* direct chunk consumer census와 adapter가 없으면 compact representation을 채택하지 않는다.
* result-shape matrix를 fast/generic path에 적용한다.
* 기존 fallback reason을 golden contract로 고정한다.

### Regression Risk

* Browser single-pass refactor가 unclassified item 또는 multi-classification item을 누락할 수 있다.
* variant grouping key 단순화가 잘못된 category/subcategory owner를 전달받으면 cache collision을 만들 수 있다.
* DEBUG guard가 필요한 진단을 제거할 수 있다.
* generated compact decoder가 optional nil/empty table rehydration을 놓칠 수 있다.
* Python read cache가 file replacement를 보지 못할 수 있다.
* lifecycle 재분류가 current/historical required input을 잘못 disposition할 수 있다.
* case-insensitive baseline collector가 Lua에서 서로 다른 key를 병합할 수 있다.

Mitigation:

* all-item count와 대표 multi-classification golden을 사용한다.
* grouping key에 generation owner와 exact category/subcategory를 결속하고 duplicate-key assertion을 둔다.
* DEBUG=true golden text를 유지한다.
* direct facade full-denominator shape test를 둔다.
* file identity와 explicit invalidation을 cache key/contract에 포함한다.
* deletion default-deny, consumer closure, external restore, dangling reference 0을 요구한다.
* ordinal comparer와 parser/input hash가 없는 classification receipt는 sealing하지 않는다.

### Destructive-Action Risk

* staging/evidence는 tracked 여부와 무관하게 current/historical evidence일 수 있다.
* CAS object 또는 cold archive 손상은 원본 disposition 뒤 복구 불가능 손실을 만들 수 있다.

Mitigation:

* exact absolute target, role, consumer, hash, restore source를 mutation 전에 검증한다.
* 원본은 verified restore와 owner disposition이 모두 끝나기 전 제거하지 않는다.
* broad glob/recursive root mutation을 금지한다.

---

## 10. Rollback Plan

1. Change별로 독립 review/commit 가능한 단위를 유지한다. session, Browser, ViewModel/ObjectAccess, generated data, Python, repository disposition을 한 commit에 섞지 않는다.
2. Change 2 census candidate가 0이거나 PZ negative evidence가 있으면 no-op, candidate가 있지만 PZ functional evidence가 없으면 production diff 0의 deferred로 닫는다. 채택 뒤 실패하면 single session handler wiring과 generation 변경을 함께 되돌리고 invalid owner가 stale-ready로 복귀하지 않았음을 확인한 뒤 기존 dev/test reset API만 유지한다.
3. Change 3 실패 시 row cache를 predecessor `itemsByFullType`/search/location 구조로 복원한다. public facade와 새 parity test는 유지해 다음 시도의 guard로 사용한다.
4. item 비보존 conditional branch가 실패하면 mandatory item-retaining row cache로 복귀한다.
5. ObjectAccess fast path failure 또는 PZ functional evidence 부재 시 call0/call1 production routing만 제거하고 fast-path routing diff 0을 검증한다. rollback 완료 후 최종 overall state는 `partial`이며, ViewModel constant/hint 재사용은 독립적으로 유지할 수 있게 한다.
6. Tooltip projection 실패 시 current runtime composition path로 복귀한다. `LineCountIndex` lazy validation은 독립 commit이면 별도 유지/rollback할 수 있다.
7. per-index lazy metadata snapshot이 `get()`-first/`getLineCount()`-first 상태 행렬, corruption reason golden, ChunkIndex-only invalid에서의 LineCount 정상 소비 중 하나라도 통과하지 못하면 module-load eager validation을 복원한다. lazy benefit을 위해 fail-loud 범위를 줄이거나 predecessor의 비대칭 validity를 넓히지 않는다.
8. legacy `IrisData` compact reconstruction이 exact semantic/mutation isolation/threshold 중 하나라도 실패하면 기준 commit의 generated `IrisData.lua`를 복원해 `complete/no-op`으로 닫는다. global/direct require/getGroupVariants adapter는 어떤 경우에도 먼저 제거하지 않는다.
9. compact representation 실패 시 generator, chunks, lookup decoder, public facade adapter, package manifest를 같은 preimage로 함께 되돌린다.
10. Python cache 실패 시 cache layer만 제거하고 instrumentation/baseline은 보존한다.
11. CAS/archive disposition 뒤 문제를 발견하면 verified object/archive에서 외부 임시 경로로 먼저 복원하고 byte compare 후 exact logical path로 복구한다.
12. rollback 뒤 focused tests, exact current route, Lua syntax, generated/package parity를 다시 실행한다. exit code 0이 없으면 복구 완료를 주장하지 않는다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`의 hub-and-spoke, Iris 100% Lua runtime, 정적 위키, 무추론·무추천·무비교 원칙을 지킨다.
* Pulse는 Iris에 의존하지 않는다.
* Iris는 다른 spoke에 직접 의존하지 않는다.
* runtime은 build/evidence Python module을 require하지 않는다.
* public Tags copy-on-read와 Browser/Tooltip consumer-local copy를 유지한다.
* `Tags.lua`/`IrisAPI.Tags`에 Browser raw accessor나 새 callable surface를 추가하지 않고 backing classification table/array를 Browser row/cache/public result에 저장하지 않는다.
* InventoryItem instance facts와 `sourceItem`은 fullType 전역 cache로 승격하지 않는다.
* legacy `IrisData` direct require/global/adapter는 별도 compatibility proof와 owner 결정 없이 제거하지 않는다.
* legacy `IrisData.Classifications`는 current classification authority와 top-level/nested mutable alias를 공유하지 않으며, current-semantic migration은 별도 data/compatibility decision 없이는 수행하지 않는다.
* session reset은 cache-owner census와 PZ functional confirmation 없이 correctness 변경으로 채택하지 않는다. candidate가 있으나 PZ가 없으면 no-op이 아니라 deferred다. locale invalidation은 session owner에 흡수하지 않는다.
* generated Tooltip summary/compact data는 기존 authority에서 결정론적으로 생성되는 projection이다.
* normal miss와 routing/target corruption을 구분하고 corruption을 empty success로 숨기지 않는다.
* `LineCountIndex` runtime integrity contract는 이 계획에서 제거하지 않는다. first `get()`과 first `getLineCount()`은 두 index의 self-state를 함께 lazy materialize하고, 둘 다 valid일 때만 entry-count를 cross-check한다. `get()`은 양 self-state와 valid cross-check를 요구하지만 `getLineCount()`은 valid LineCount self-state와 non-invalid cross-check만 요구하며, ChunkIndex-only invalid를 LineCount failure로 확대하지 않는다.
* classification compatibility receipt는 Lua와 같은 case-sensitive key semantics를 사용하며 case-insensitive parser 결과를 authority로 인정하지 않는다.
* current core 12와 allowed tooling 4/4는 explicit admission/disposition 없이 확장하지 않는다.
* Python helper는 path/encoding/newline/error/atomicity/cwd/CLI 계약이 같은 exact consumer group에서만 공통화한다.
* tracked는 authority를, ignored는 disposable을 자동 의미하지 않는다.
* current/historical/diagnostic/package/runtime 결과를 하나의 bare PASS로 합치지 않는다.
* source/static guard는 실제 PZ/Kahlua validation을 대체하지 않는다.
* optional PZ timing receipt 부재는 timing-dependent branch의 claim/adoption만 제한하며 Phase 0a structural/correctness 작업의 mutation eligibility를 차단하지 않는다.
* PZ functional evidence는 timing과 별도다. session-bound cache와 Java/Kahlua binding candidate가 존재하면 standalone Lua evidence만으로 runtime validation complete를 주장하지 않는다.
* 선행 plan/closeout receipt/sealed evidence를 수정하지 않는다.
* unrelated dirty worktree 변경을 수정, 정리, stage, rollback하지 않는다.
* validation command exit code 0인 경우에만 해당 axis PASS를 주장한다. 필요한 tool 부재는 BLOCKED다.
* 예상 byte/operation/time 절감치를 완료 수치로 보고하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: conditional `complete`

`complete`는 engine-bound candidate가 0/PZ-negative이거나 필요한 PZ functional evidence가 제공되는 경우의 목표다. Change 2 candidate 또는 Change 4 fast-path routing candidate가 존재하지만 PZ 환경이 없으면 현실적 목표는 production code 미채택/verified rollback 기준 `partial`이며, unvalidated routing code가 남으면 `implemented_only`다.

이 계획의 `complete`는 모든 conditional candidate가 구현됐다는 뜻이 아니다. 다음 조건을 모두 만족하는 상태다.

* Phase 0a unconditional gate와 모든 unconditional Change가 구현·검증되고, Phase 0b 및 owner/measurement-gated branch가 disposition으로 닫히며 아래 branch mapping상 `complete`와 양립한다.
* cache owner census가 actual cache key set과 exact equality로 모든 field를 분류하고, Change 2는 candidate 0/PZ-negative=`complete/no-op`, candidate+PZ-unavailable=`deferred_by_design`, PZ-confirmed=`adopted`로 닫힌다.
* Browser single-pass, module-local scalar tag iteration, frozen Tags export, primary/`(generation, locale)` search/variant parity가 focused/current/Lua validation으로 닫힌다.
* ViewModel 결과/instance isolation이 검증되고 ObjectAccess fast path를 production routing에 채택했다면 PZ Java/Kahlua functional parity가 있다.
* DEBUG=false allocation과 DEBUG=true diagnostic parity가 검증된다.
* first-`get()`/first-`getLineCount()` per-index lazy snapshot이 상태 행렬을 그대로 재현한다. ChunkIndex-only invalid에서 `getLineCount()`은 정상 count 또는 absent-key `(0, nil)`을 유지하고 fallback counter를 늘리지 않으며, 양쪽 self-valid count mismatch는 두 entrypoint 모두 `index_content_mismatch`로 닫힌다.
* ordinal parser receipt가 1,360/1,360 legacy, 2,079/2,079 current, duplicate 0, current-only 719, differing common key 4를 재현한다. legacy `IrisData`는 exact semantics와 current/cross-key mutation isolation을 검증한 compact candidate를 채택하거나 기존 payload 유지 no-op으로 닫힌다. `getGroupVariants`는 permanent adapter로 남는다.
* Phase 0b와 Changes 4/5/7~11의 measurement/engine-gated branch마다 `adopted`, `complete/no-op`, `deferred_by_design`, `blocked` 중 하나와 근거가 있다.
* adopted generated change는 source/package determinism과 public facade parity를 통과한다.
* repository disposition이 있었다면 restore parity, dangling reference 0, final byte census가 있다.
* exact current route, focused tests, Lua syntax, mandatory package validator가 exit code 0이며 integration command의 실제 wall-clock이 기록된다.
* mandatory runtime surface에 `unvalidated_but_in_scope`가 없다.
* `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`는 실제 채택된 계약만 additive하게 반영한다.

Closeout mapping:

| Condition | Overall state |
|---|---|
| 위 complete 조건 전부 충족 | `complete` |
| mandatory implementation 일부 완료 또는 engine-bound candidate가 있으나 production code는 미채택 | `partial` |
| code는 구현됐으나 current/Lua/package 또는 required PZ functional 검증 미실행 | `implemented_only` |
| authority, tooling, dependency 또는 owner disposition 부재로 unconditional 작업 진행 불가 | `blocked` |

Branch disposition은 overall state로 다음처럼 환원한다.

| Branch disposition | Overall closeout effect |
|---|---|
| `adopted` + 모든 required evidence PASS | `complete`와 양립 |
| evidence-bound `complete/no-op` | `complete`와 양립 |
| optional timing/heap branch의 `deferred_by_design` | non-claim을 기록하면 `complete`와 양립 |
| Change 2 candidate 또는 Java/Kahlua fast-path의 PZ functional evidence 부재 | production code 미채택/verified rollback이면 `partial`; unvalidated routing code가 tree에 남으면 `implemented_only`; `complete` 불가 |
| unconditional branch의 unresolved `blocked` | overall `blocked` |

Optional Tooltip projection, compact representation, item 비보존, Recipe Set, Python cache, CAS/archive가 threshold 미달로 `complete/no-op`이 되는 것은 전체 `complete`와 양립한다. PZ timing benchmark 부재는 Phase 0b 의존 branch만 deferred로 만들고 Browser single-pass·DEBUG guard·per-index lazy metadata snapshot 같은 pure-Lua structural/correctness work를 막지 않는다. 반면 Change 2 candidate와 ObjectAccess Java/Kahlua production routing은 PZ functional evidence 부재를 timing carve-out으로 숨길 수 없으며 production diff 상태에 따라 overall `partial`/`implemented_only`가 된다. latency/heap/FPS/frame-time claim은 계속 금지한다.

모든 closeout은 다음 non-claims를 명시한다.

* FPS, frame-time, tick 개선을 선언하지 않는다.
* 신뢰 가능한 heap 측정이 없으면 heap 절감을 선언하지 않는다.
* configured full advisory가 exit 0이 아니면 full-suite PASS를 선언하지 않는다.
* 모든 third-party mod, multiplayer, long-session 호환성을 선언하지 않는다.
* release-ready, Workshop-ready, B42-ready, deployed를 선언하지 않는다.
* 실제 LLM token before/after가 없으면 token 효율 개선율을 선언하지 않는다.
