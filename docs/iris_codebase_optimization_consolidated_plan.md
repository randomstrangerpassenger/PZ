# Implementation Plan

> Iris 코드베이스 최적화 종합 실행 계획
>
> 기준 커밋: `9dcb16288b79fa911adf601741b913cd71ded145`
>
> 작성 기준일: 2026-08-10
>
> 개정 상태: 2차 종합 검토안 R1~R11과 후속 사실관계·구현 가드 6건 반영. direct UseCase facade field-presence, full-denominator importability, ItemDetail instance identity를 명시적으로 보존한다.

## 1. Objective

첨부된 「Iris 코드베이스 최적화 종합 제안」을 현재 Iris 구현과 기존 경량화 결정에 맞게 재기준화하고, 검증 신뢰성을 먼저 회복한 뒤 런타임 hot path, 생성 Lua, 저장소 중복, Python 검증 도구의 비용을 단계적으로 줄인다.

이 계획은 다음 결과를 목표로 한다.

1. 기본 `pytest` 수집 경로가 stale taxonomy 때문에 중단되지 않으면서도, 봉인된 Round 3 current/historical/diagnostic 권한 경계는 넓히지 않는다.
2. 존재하지 않는 외부·모드 아이템의 정상 조회가 Layer3/UseCase 전체 compatibility facade를 물질화하지 않게 한다.
3. Browser 최초 진입, Alt Tooltip, 검색, 상세 패널의 시간·스캔·복사·fallback 지표를 같은 generation과 locale 기준으로 수집한다.
4. 공개 API의 copy-on-read 및 기존 반환 형식을 유지하면서 Tooltip과 Browser 내부 hot path의 반복 할당을 줄인다.
5. 생성 Lua chunk에서 의미 없는 `nil` 필드와 빈 테이블을 제거하되, EN/KO 내용과 use-case/Layer3 의미 동등성 및 direct UseCase facade의 `debug_lines` field shape를 유지한다.
6. 기존 content-addressed evidence 저장소와 migration 도구를 확장하여, 직접 소비자가 없는 역사적 staging 중복만 참조로 전환한다.
7. current 검증 runner의 반복 Git subprocess를 배치 처리하고, 나머지 subprocess·helper 정리는 계약 동등성이 증명되는 경우에만 수행한다.
8. Browser 증분 빌드, Tooltip 정적 데이터 재구성, `LineCountIndex` 경량화는 계측 임계값을 넘을 때만 채택한다. 채택하지 않는 결정도 근거와 함께 종결 상태로 기록한다.

성공은 단순한 파일 수·코드 줄 수 감소가 아니라 다음 불변 조건과 함께 판단한다.

- Iris는 정적 위키이며 추론, 추천, 비교, 가치 판단을 추가하지 않는다.
- Hub-and-spoke 방향과 공개 facade 호환성을 유지한다.
- current 권한 경로, 필수 검증 ID, 생성 데이터 의미, 검색·분류 순서가 보존된다.
- 정상 miss와 실제 router fault가 관측 가능하게 구분된다.
- 저장소 절감치는 삭제 전 예상치가 아니라 최종 byte census로 보고한다.

---

## 2. Scope

실행은 `Gate A -> Change 3 계측-only commit과 Gate C baseline-0 -> Gate B/Change 2 -> mandatory Change 4/5/9 -> Gate C baseline-1 -> measurement-gated changes -> Change 8 disposition -> closeout` 순서를 따른다. Change 번호는 주제 식별자이며 실행 순서를 뜻하지 않는다. 선행 gate가 실패하면 뒤의 runtime/generated/storage mutation을 시작하지 않는다.

### Gate A — 검증 경로 복구

- Round 3 exact taxonomy는 봉인된 route 실행용으로 보존한다.
- 일반 `pytest` 발견은 owner-approved source classification과 소수의 mixed-source item override를 사용하도록 분리한다.
- 기준 시점의 미분류 49개 source, `pytest.ini`의 explicit ignore 6개, known historical ImportError 2개 및 이후 발견되는 모든 collection blocker를 판정한 manifest를 Change 1의 필수 산출물로 만든다. 미판정 또는 import 불가능 included source는 Gate A를 차단한다.
- 현재 하위 `conftest.py`가 root `--round3-contract=all`을 정상 인식하므로 root plugin을 새로 만들지 않는다. 기존 conftest/source manifest 경계를 확장한다.
- 기본 current 수집, configured full denominator를 실행하는 `--round3-contract=all`, exact current runner가 각각 의도한 범위만 실행하는지 source-set 및 mixed-item equality로 증명한다.
- configured full discovery의 source-denominator collection은 mandatory이며 exit code 0이 아니면 Gate A가 열리지 않는다. `all` execution은 historical/diagnostic correctness를 이번 scope로 끌어들이지 않도록 advisory chain에서 실행한다. 단, 실패가 current, modified source 또는 mandatory invariant에 닿으면 `unvalidated_but_in_scope`가 되어 `complete`를 차단한다.
- 기준 커밋의 Gate A는 현재 열려 있지 않다. Change 1의 manifest/disposition/importability 작업만 먼저 수행할 수 있으며 known historical blocker 두 개가 복원 또는 owner-approved exclusion되고 mandatory current/all collection이 exit 0이 되기 전에는 Gate B 이후 mutation에 착수하지 않는다.

### Gate B — 정상 miss의 전체 facade fallback 제거

- Layer3 renderer 및 UseCases consumer가 `lookup_miss`를 정상적인 부재로 처리한다.
- router 자체가 손상되거나 로드되지 않은 경우에만 compatibility facade로 fallback한다.
- 외부·모드 아이템 miss에서 전체 facade load count가 0인지 검증한다.

### Gate C — 성능 기준선과 채택 임계값 고정

- `baseline-0`은 Change 1 이후, Change 2~5를 포함한 어떤 runtime/generated mutation도 하기 전에 채취한다.
- `baseline-1`은 mandatory runtime/generated Change 2, 4, 5를 완료한 직후, measurement-gated Change 6, 7, 10 전에 채취한다.
- Change 5와 generated-size 비교는 `baseline-0`, Change 6/7/10 채택 판단은 `baseline-1`을 before generation으로 사용한다. 같은 generation의 수치를 섞지 않는다.
- cold Browser open, warm reopen, 첫 Alt, warm Alt, 검색 입력, 상세 패널 선택을 계측한다.
- 시간, 스캔 수, facade fallback, cache hit/miss, 배열 복사 수와 item/method denominator를 자동 수집한다.
- heap API를 런타임에서 신뢰할 수 있을 때만 heap delta를 정식 지표로 삼고, 불가능하면 그 한계를 기록한다.
- 각 measurement-gated 항목의 metric, denominator, trigger, adoption threshold는 Change 3의 표를 baseline 채취 전에 봉인한다.

### Mandatory Optimization Track

- 생성 Lua chunk의 optional `nil` 필드와 빈 `debug_lines` 제거. 단, direct `IrisUseCaseDescriptions` compatibility facade가 materialize될 때 entry별 독립 빈 `debug_lines` table을 복원한다.
- Tooltip 비활성 경로와 내부 렌더 캐시의 반복 할당 제거.
- current Round 3 runner의 Git tracked/ignored 조회 배치화.
- 소비자 폐쇄가 증명된 staging 중복군의 기존 CAS 전환.

### Measurement-Gated Runtime Track

- Browser 증분 build state machine.
- 검색의 primary location 사전 계산, 복사 단일화, 필요 시 debounce.
- 상세 ViewModel capability mask 및 generation/locale cache.
- Tags/ObjectAccess/Variant 내부 hot-path 단축.
- Tooltip 정적 summary index 또는 chunking.
- `LineCountIndex` runtime 검증 경량화 또는 구조 변경.
- Ordering의 decorate-sort-undecorate 전환.

각 항목은 Gate C의 지표에서 비용이 식별되고, 변경 후 지표가 개선되며, 호환성 테스트가 유지될 때만 채택한다. 임계값 미달 항목은 코드 변경 없이 `no-op` 결정으로 닫는다.

### Tooling Track

- current runner의 반복 Git subprocess만 우선 배치화한다.
- Python subprocess 테스트는 CLI/프로세스 경계가 테스트 대상이 아닌 경우에만 in-process로 전환한다.
- JSON/hash/path helper는 현재 producer 3개 이상이 encoding, newline, error, atomicity, cwd 및 CLI 계약까지 동일할 때만 기존 family common module로 추출한다.

### Explicitly Out Of Scope

- Git history rewrite, filter-repo, 과거 pack 제거.
- raw UTF-8 생성 Lua 전환.
- 공개 `IrisData`, Layer3, UseCase facade 삭제 또는 반환 형식 변경.
- Iris Registry의 대규모 물리 분할.
- 고유한 evidence의 일괄 archive 또는 삭제.
- Tooltip 정적 데이터의 근거 없는 최종 구조 선택.
- 다른 모드의 최적화, cross-spoke 의존성, 추천·추론 기능 추가.
- UI 전면 재작성, 테마 변경, 사용자 동작 변경.
- 성능 근거 없는 범용 helper 또는 새 저장 인프라 도입.

---

## 3. Non-Goals

- 이미 완료된 Browser boot-time eager build 제거와 정적 Recipe/Moveables/Fixing/Classifications의 first-use 전환을 다시 구현하지 않는다.
- 기존 CAS object를 새 형식으로 재마이그레이션하지 않는다.
- `round3_test_taxonomy.json`을 일반 pytest 편의를 위해 current 권한 목록으로 자동 확장하지 않는다.
- 모든 Python subprocess 호출을 제거하지 않는다. 현재 조사 기준 Iris에는 관련 호출이 126개 파일, 365개 있으며 상당수는 CLI, cwd, 환경 변수, exit code, stdout/stderr 또는 격리를 검증한다.
- 모든 `load_json`, `write_json`, `sha256_file`, `sys.path` 패턴을 하나의 global helper로 합치지 않는다.
- Lua public API가 반환하는 테이블을 read-only라고 가정하여 defensive copy를 제거하지 않는다.
- fullType만으로 InventoryItem 전체 ViewModel을 cache하거나, 이번 계획을 위해 불완전한 item-state revision을 새로 만들지 않는다.
- 정상 miss를 오류로 승격하거나, 실제 router fault를 조용히 빈 결과로 숨기지 않는다.
- 전체 test suite의 역사적 실패를 이번 최적화의 성공 조건으로 재정의하지 않는다. 다만 current authority route와 변경 관련 검증은 모두 통과해야 한다.

---

## 4. Assumptions

### Constitutional and Authority Assumptions

- `docs/Philosophy.md`가 설계 권한의 최상위 기준이다.
- `docs/ARCHITECTURE.md`가 명시한 Hub-and-spoke, runtime/build-time 분리, public copy-on-read, compatibility facade 보존을 불변 조건으로 사용한다.
- `docs/DECISIONS.md`와 기존 두 경량화 계획의 완료 항목을 predecessor 사실로 취급한다. 이 계획은 기존 결정을 덮어쓰지 않고 잔여 항목을 additive하게 처리한다.
- `Iris/_docs/round3/round3_test_taxonomy.json`과 `current_route_required_validations.json`은 봉인된 route의 exact authority다. 일반 pytest source 분류는 별도 발견 정책이며 이 권한을 대체하지 않는다.
- source classification의 최종 승인 주체는 Iris repository owner다. 실행자는 후보와 근거를 만들 수 있지만 unresolved source를 임의로 current 또는 exclusion으로 승인할 수 없다.
- direct `IrisUseCaseDescriptions` table은 공개 compatibility facade다. 공식 API consumer가 현재 빈 table과 field 부재를 동일하게 처리하더라도 direct facade의 `debug_lines` field와 table type은 보존한다.
- packaged Layer3/UseCase chunk, range/count index, package manifest는 같은 generator generation에서 원자적으로 생성·승격된다는 invariant를 Change 2의 mandatory package validator가 증명해야 한다. 이 증명 없이 `lookup_miss`를 authoritative negative로 채택하지 않는다.

### Current Codebase Readpoint

다음은 기준 커밋에서 직접 확인한 현재 상태다.

- `IrisMain.lua`는 Browser data module을 부팅 시 로드하지만 item index build는 수행하지 않는다. `IrisBrowserData.ensureReady()`가 첫 사용에 동기 build한다.
- Layer3와 UseCase key lookup 및 chunk router는 이미 존재한다.
- `IrisLayer3DataLookup`의 정상 미등록 조회는 `lookup_miss`를 반환하지만, `layer3_renderer.getEntry()`는 이 이유까지 `ensureData()`로 넘겨 전체 `IrisLayer3DataChunks` facade를 로드한다.
- `API/UseCases.lua`의 line/description 조회는 lookup miss 이후 `rawArray("useCaseDescriptions", fullType)`로 내려가 전체 facade를 로드할 수 있다. line-count lookup의 missing key는 이미 authoritative `0, nil`이므로 신규 동작 변경이 아니라 유지 검증 대상이다.
- `IrisTooltipSummary.get()`은 cache hit에서도 tags/connections 배열을 복사한다. 이는 공개 copy-on-read 계약이므로 public 경로에서 제거할 수 없다.
- `IrisAltTooltip`의 Alt 비활성 경로는 현재 빈 `detailLines` table을 만든다. cache key 문자열 조합과 cache-hit line 복사는 Alt 활성 경로에서만 발생한다.
- `IrisBrowserQuery.searchAll()`은 prefix 결과를 재사용하지만 결과를 cache 저장 시 한 번, public 반환 시 한 번 복사한다. item location은 매 결과마다 분류 순회를 수행한다.
- `IrisItemDetailViewModel.fromItem()`은 아이템 종류와 무관하게 food/weapon/literature/moveable method group과 여러 index를 모두 조회하고, generation cache가 없다.
- `IrisItemDetailViewModel`의 `values.revision`은 현재 `fullType|locale`만 담고 읽는 consumer가 없다. instance state나 generation을 포함하지 않으므로 향후 whole-model/static cache key로 재사용할 수 없다.
- 같은 model의 `sourceItem`도 현재 정의 지점 외 consumer가 없지만 public model field이므로 instance별로 보존한다. 교차 오염 검증은 렌더 결과만이 아니라 반환 model의 `sourceItem` identity를 직접 비교해야 한다.
- `IrisObjectAccess.call()`은 호출마다 vararg 배열과 closure를 만들지만 `IrisProtectedCall.engine(fn, ...)`은 직접 인자를 받을 수 있다.
- `IrisUseCaseDescriptionsLookup`은 module load 시 1,631개 `LineCountIndex` entry를 전수 검증한다. 현재 acceptance harness는 손상 entry가 `index_shape_invalid`를 만드는 동작을 계약으로 사용한다.
- 생성 UseCase chunk는 optional `nil` 필드와 1,631개의 빈 `debug_lines`를 포함한다. 의미 보존형 제거 예상치는 현재 chunk 약 1,272,123 bytes 중 약 131,821 bytes이며, 최종 수치는 재생성 후 측정한다.
- `Ordering.lua` comparator는 비교마다 sort key를 다시 계산한다.

### Validation Baseline

- `uv run python -m pytest --collect-only -q`는 기준 커밋에서 exit code 3이다.
- default/current 경로는 `Iris/build/description/v2/tests/conftest.py::pytest_collection_modifyitems`가 unknown description-v2 test ID를 stale taxonomy로 판단해 `RuntimeError`를 던지고, pytest가 이를 `INTERNALERROR`로 종료한다. 이는 test failure(exit 1)나 collection interruption(exit 2)이 아니다.
- 실제 `test_*.py` source는 263개이고, 49개 source가 exact taxonomy에 없다. 기존 taxonomy에 들어 있는 source 중에도 현재 경로에 없는 항목이 있다.
- taxonomy에서 둘 이상의 contract class가 섞인 source는 현재 두 개다.
  - `test_compose_entrypoint_guard_hardening.py`: current + historical
  - `test_package_layer3_chunks_only_contract.py`: current + diagnostic
- 이 실패 상태에서는 후속 런타임 변경을 검증 완료로 판정하지 않는다.
- bare root `uv run python -m pytest -q`는 default current contract만 실행하므로 full denominator가 아니다.
- root `uv run python -m pytest --collect-only -q --round3-contract=all`의 option은 기준 커밋에서 정상 인식된다. 이 변형은 exit code 2이며, 944 tests 수집 뒤 다음 두 historical source가 소실된 producer module을 top-level import하여 두 collection error로 중단된다.
  - `test_phase_d_signal_preservation_supporting_reports.py` → `tools.build.validate_phase_d_signal_preservation` 부재.
  - `test_structural_reclassification_code_path_convergence_supporting_reports.py` → `tools.build.validate_structural_reclassification_convergence` 부재.
- 따라서 default/current stale taxonomy failure와 all-contract historical ImportError는 서로 다른 baseline failure다. root option registration은 변경 대상이 아니며, 두 historical source는 owner-approved producer 복원 또는 `excluded` disposition 전까지 Gate A blocker다.

### Storage Baseline

- `Iris/build`의 현재 물리 크기는 775,851,563 bytes다.
- `Iris/build/description/v2/staging`은 4,552 files, 547,753,911 bytes다.
- tracked staging 중 100 KiB 이상 파일을 SHA-256으로 비교한 read-only 조사에서는 60개 duplicate hash group과 약 100.2 MiB의 중복 초과분이 관찰되었다.
- 기존 `Iris/build/description/v2/evidence/objects/sha256` object store와 `Iris/validation/residual_refactor/migrate_repository_evidence.py`를 확장할 수 있다.
- 위 중복 수치는 후보 상한이며 소비자, authority, 복원 검증을 거친 뒤의 실제 절감치가 아니다.

### Environment Assumptions

- 명령은 Windows PowerShell에서 실행한다.
- Python 검증은 `uv run python ...`, Lua 구문 검증은 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`를 사용한다.
- 전체 discovery 또는 producer 실행은 source tree를 변경할 수 있으므로 clean disposable checkout과 외부 work root에서 수행한다.
- Project Zomboid 런타임 계측은 게임 실행 환경이 제공될 때 수행한다. 제공되지 않으면 자동 harness 결과와 validation limit를 함께 남긴다.

---

## 5. Repository Areas Affected

아래 목록은 예상 touch surface다. measurement-gated 항목이 `no-op`으로 닫히면 해당 파일은 수정하지 않는다.

### Code

- `Iris/build/description/v2/tests/conftest.py`
- owner가 restore를 선택할 때만 새 historical compatibility producer:
  - `Iris/build/description/v2/tools/build/validate_phase_d_signal_preservation.py`
  - `Iris/build/description/v2/tools/build/validate_structural_reclassification_convergence.py`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/Data/IrisRuntimeLookupDiagnostics.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/media/lua/client/Iris/API/Tags.lua`
- `Iris/media/lua/client/Iris/Util/IrisObjectAccess.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Ordering.lua`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua`
- `Iris/validation/residual_refactor/migrate_repository_evidence.py`
- `Iris/validation/residual_refactor/repository_evidence_codec.py`
- 필요한 경우 현재 audit family의 repository evidence resolver

### Tests

- `Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py`
- `Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py`
- `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`
- `Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py`
- `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
- `Iris/build/description/v2/tests/test_phase_d_signal_preservation_supporting_reports.py`
- `Iris/build/description/v2/tests/test_structural_reclassification_code_path_convergence_supporting_reports.py`
- 새 `Iris/build/description/v2/tests/test_round3_pytest_source_classification.py`
- 새 `Iris/build/description/v2/tests/test_lookup_package_parity_contract.py`
- 새 `Iris/build/description/v2/tests/test_generated_lua_sparse_fields_contract.py`
- 새 `Iris/build/description/v2/tests/test_round3_git_batch_contract.py`
- 새 `Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py`
- 새 `Iris/build/description/v2/tests/test_round3_pytest_failure_classification.py`
- 새 `Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py`
- `Iris/test/lua/lazy_lookup_acceptance_harness.lua`
- `Iris/test/lua/browser_state_acceptance_harness.lua`
- `Iris/test/lua/residual_refactor_acceptance_harness.lua`
- 새 source-classification, generator parity, Git batch parity, performance metrics 계약 테스트

### Docs

- `docs/iris_codebase_optimization_consolidated_plan.md`
- 실행 완료 시 additive update 대상:
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- 실행 evidence/decision receipt를 둘 기존 Iris `_docs` 하위의 관련 refactor 디렉터리

### Config

- `pytest.ini`
- `Iris/_docs/round3/round3_test_taxonomy.json`은 exact runner 계약 보정이 필요한 경우에만 수정
- 새 일반 pytest source classification manifest
- 새 configured full-discovery denominator manifest
- `Iris/_docs/round3/current_route_required_validations.json`은 필수 검증 자체가 변경되고 별도 권한 승인이 있을 때만 수정

### Generated Artifacts

- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/Chunk*.lua`
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/LineCountIndex.lua`
- 해당 package/index/hash/manifest 출력
- 선택된 historical staging logical path의 작은 CAS reference manifest
- 기존 `Iris/build/description/v2/evidence/objects/sha256/**` 아래의 신규 unique object
- 계측 baseline, before/after, adoption/no-op 및 최종 byte census receipt

---

## 6. Planned Changes

### Change 1 — 일반 pytest 발견 정책과 봉인 route 권한 분리

Purpose:

stale exact taxonomy 때문에 기본 current 수집이 깨지는 문제와 이미 분류됐지만 import 불가능한 historical source 때문에 full collection이 깨지는 문제를 함께 해소하면서 current authority를 자동 확장하지 않는다.

Files:

- `Iris/build/description/v2/tests/conftest.py`
- 새 `Iris/_docs/round3/round3_pytest_source_classification.json`
- 새 `Iris/_docs/round3/round3_full_discovery_denominator.json`
- source classification 계약 테스트
- exact route 변경이 실제로 필요한 경우에만 `round3_test_taxonomy.json`

Implementation Notes:

1. exact taxonomy와 `round3_run_contract_tests.py`는 test ID 단위의 봉인 route로 그대로 유지한다.
2. 기준 커밋의 하위 `conftest.py`가 root `--round3-contract=all` option을 이미 인식하므로 option ownership을 옮기거나 root plugin을 추가하지 않는다. 기존 conftest에 source manifest, exclusion 및 denominator/importability report hook만 확장한다.
3. 일반 pytest용 source manifest의 분류 기준을 다음과 같이 고정한다.
   - `current`: 현재 지원되는 build/package/runtime artifact 또는 현재 authority 계약을 검증하며 current route의 대상과 모순되지 않는 source.
   - `historical`: superseded/closed round의 재현, 봉인 hash 또는 과거 동작만 검증하고 현재 성공 판정을 만들지 않는 source.
   - `diagnostic`: audit, probe, failure injection, 관찰 도구처럼 current release contract의 필수 성공 조건이 아닌 source.
   - `excluded`: 수집 시 source mutation, 외부 도구 부재, 폐기된 script-style test 등 명시적 이유로 configured denominator 밖에 두는 source. `reason`, `alternative_validation`, `owner`, `reviewed_at`을 필수로 기록한다.
4. 기존 taxonomy의 단일-class source는 기계적으로 초기 후보를 만들 수 있지만, 기준 시점의 미분류 49개 source는 source가 소비하는 authority, 현재 package reachability, required validation과의 관계를 사람이 검토한다. 이 49개 판정표와 owner 승인이 Change 1의 명시적 deliverable이다.
5. 승인 주체는 Iris repository owner다. 실행자가 분류 근거를 만들 수는 있지만 판정 불가 source를 자동으로 `current` 또는 `excluded`에 넣을 수 없다. unresolved가 하나라도 있으면 Gate A 상태는 `blocked`다.
6. `pytest.ini`의 ignore 6개도 같은 판정표에 포함한다. current 역할이면 ignore를 제거하고 denominator에 넣으며, 아니라면 `excluded`의 네 필드를 채운다. 단순히 기존 ignore였다는 사실은 제외 근거가 아니다.
7. source가 이미 historical/diagnostic/current로 분류되었더라도 top-level ImportError, missing dependency, syntax error 또는 collection hook failure로 configured collection을 exit 0으로 만들지 못하면 같은 disposition workflow에 들어간다. 분류 완료는 importability 완료를 뜻하지 않는다.
8. 기준 시점의 known blocker 두 개는 다음 중 하나로 owner가 판정해야 한다.
   - missing historical producer를 exact historical contract로 복원하고 import/collection parity를 검증.
   - `reason`, `alternative_validation`, `owner`, `reviewed_at`을 가진 `excluded`로 전환하고 exact historical taxonomy trace는 삭제하지 않음.
9. 두 mixed source는 source default와 exact item override를 함께 기록한다. mixed-source 수가 늘어나면 자동 오류로 막고 manifest review를 요구한다.
10. 기본 `--round3-contract=current`는 owner-approved current source의 새 test도 수집한다. 이는 일반 발견 정책일 뿐 exact current runner의 필수 ID를 넓히지 않는다.
11. configured full denominator는 다음 source set으로 정의한다.
   - manifest에서 `current`, `historical`, `diagnostic`으로 승인된 모든 description-v2 `test_*.py` source.
   - `pytest.ini`가 지정한 cross-track source.
   - owner-approved 추가 source.
   - `excluded` source는 denominator 밖이지만 제외 이유와 대체 검증이 manifest에 남아야 한다.
12. `pytest_collectreport` 기반 receipt는 denominator source마다 `collected`, `collection_error`, `excluded` 중 하나와 node count/error identity를 기록한다. included source의 `collection_error`가 하나라도 있으면 `--round3-enforce-denominator`는 Gate A를 fail-closed한다.
13. `--round3-enforce-denominator`는 실제 successfully collected source set과 manifest included set의 양방향 equality, mixed-source item override, unknown source 0, `all`에서 included-source policy deselection 0, included-source collection error 0을 검사한다. excluded source는 별도 receipt 영역이며 collected denominator로 세지 않는다. collection node IDs와 count는 execution receipt에도 저장한다.
14. `all`에서도 owner-approved `excluded`는 import 전에 `pytest_ignore_collect`로 건너뛰며, exclusion trace와 alternative validation은 denominator receipt에 남긴다.
15. 미분류 또는 collection-failing source는 item ID 대량 나열 대신 source, classification, import/error identity를 가리키는 fail-closed 메시지를 낸다.
16. `--round3-additional-source`의 canonical path 및 repository-boundary 검사는 보존한다.
17. manifest validator는 실제 source와 manifest의 양방향 차이, invalid class, duplicate override, 사라진 source, approval 누락, included-source importability failure를 검출한다.
18. exact taxonomy를 수정해야 할 경우 exact taxonomy 변경을 먼저 되돌릴 수 있는 별도 owner-approved commit으로 두고, conftest/manifest 변경은 독립 commit에서 관리한다.
19. advisory full execution failure classifier는 source manifest, mixed-item overrides, execution diff의 modified path set과 mandatory invariant ownership을 입력으로 사용한다. 분류 우선순위는 `modified/mandatory/current > historical > diagnostic`이며 unknown 또는 source-level mixed collection error는 보수적으로 `unvalidated_but_in_scope`다. 사람은 severity를 올릴 수만 있고 current/modified failure를 historical로 낮출 수 없다.

Validation:

- 새 test를 current source에 추가한 fixture에서 default collection이 stale 오류 없이 선택하는지 확인한다.
- mixed source의 historical/diagnostic item이 default current에서 선택되지 않는지 확인한다.
- 미분류 source fixture가 source-level 오류로 fail-closed하는지 확인한다.
- 49개 source, ignore 6개, known historical blockers 2개와 추가 collection blocker의 disposition 및 owner approval 누락이 0인지 확인한다.
- included historical source의 missing producer fixture가 collection error로 기록되고 Gate A를 막는지 확인한다.
- owner-approved excluded source는 `all`에서도 import 전에 제외되며 alternative validation identity가 receipt에 남는지 확인한다.
- `all` successfully collected source set과 full denominator included set이 정확히 같고 included-source policy deselection 및 collection error가 0인지 확인한다.
- synthetic current/modified/historical/diagnostic/unknown failure report가 고정된 우선순위로 분류되고 수동 downgrade가 거부되는지 확인한다.
- exact current runner의 선택 ID set과 `current_route_required_validations.json`이 변경 전과 동일한지 비교한다.
- `uv run python -m pytest --collect-only -q --round3-contract=current --round3-enforce-denominator` exit code 0을 요구한다.
- `uv run python -m pytest --collect-only -q --round3-contract=all --round3-enforce-denominator` exit code 0을 요구한다.

---

### Change 2 — 정상 lookup miss와 router fault의 fallback 분리

Purpose:

외부·모드 아이템 또는 Iris 데이터에 없는 item의 정상 miss가 전체 Layer3/UseCase facade를 로드하는 잔존 경로를 제거한다.

Files:

- `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/Data/IrisRuntimeLookupDiagnostics.lua`
- Layer3/UseCase generator 및 package parity validator
- `Iris/test/lua/lazy_lookup_acceptance_harness.lua`
- `test_layer3_lazy_lookup_contract.py`
- `test_usecase_lazy_lookup_contract.py`
- 새 `test_lookup_package_parity_contract.py`

Implementation Notes:

1. runtime 변경 전 mandatory package invariant를 고정하고 검증한다.
   - Layer3 index, Layer3 chunks, UseCase `ChunkIndex`, UseCase chunks, `LineCountIndex`, package manifest는 같은 generator generation ID와 source digest를 공유한다.
   - Layer3 index ↔ chunk 전체 key set, entry count, first/last boundary, module name, recorded hash가 일치한다.
   - UseCase `ChunkIndex` ↔ chunk 전체 key set/count/boundary/hash가 일치한다.
   - UseCase chunk key set과 `LineCountIndex` key set이 정확히 같고 각 count가 실제 public line count와 같다.
   - partial generation 또는 이전 generation index와 새 chunk의 혼합 승격은 package validator가 fail-closed한다.
2. 위 validator가 current packaged generation에서 exit code 0인 경우에만 `lookup_miss`를 authoritative negative로 채택한다. 이 invariant는 measurement-gated Change 7에 의존하지 않는다.
3. lookup reason을 두 범주로 고정한다.
   - authoritative negative: `lookup_miss` 및 정상적인 line-count 부재.
   - router fault: `router_unavailable`, `index_shape_invalid`, `index_content_mismatch`, `module_name_invalid`, `target_module_load_failure`, `compat_read_failure` 등 실제 조회 경로 손상.
4. target chunk를 처음 로드할 때 table shape, entry count, min/max boundary와 key type을 record에 대조한다. 검증 실패는 normal miss가 아니라 `index_content_mismatch`다.
5. UseCase는 `LineCountIndex`에 key가 있는데 target chunk entry가 없으면 `index_content_mismatch`로 처리한다. `LineCountIndex` 자체의 missing key가 `0, nil`을 반환하는 현재 authoritative behavior는 변경하지 않고 유지 검증한다.
6. `layer3_renderer.getEntry()`는 검증된 router의 `lookup_miss`에서 즉시 `nil`을 반환하고 `ensureData()`를 호출하지 않는다.
7. UseCases의 line, description, requirements 조회도 authoritative negative에서 public empty/nil 계약을 직접 반환한다.
8. router fault와 unknown reason에서만 compatibility facade를 요구하며, diagnostics에 consumer와 reason을 기록한다.
9. `layer3_renderer`의 lookup ProtectedCall 실패와 compatibility table read 실패도 silent nil로만 끝내지 않고 각각 `router_unavailable` 또는 `compat_read_failure`를 기록한다. public nil 반환 의미는 유지한다.
10. explicit public facade require와 기존 direct compatibility consumer는 계속 전체 materialization을 허용한다.
11. facade load count는 production global 상태를 노출하기보다 기존 diagnostics 또는 harness의 `package.preload` sentinel로 관측한다.
12. public return shape, 배열 copy-on-read, EN/KO 선택, missing item의 기존 화면 문구는 변경하지 않는다.

Validation:

- 존재하는 key는 target chunk 1개 이하만 로드하고 facade load 0인지 확인한다.
- 존재하지 않는 base item과 index range의 안/밖에 각각 놓이는 임의의 외부/mod fullType은 결과가 nil/empty이고 facade load 0인지 확인한다.
- router unavailable 및 index corruption fixture는 compatibility fallback 1회와 정확한 reason을 기록하는지 확인한다.
- shape는 valid하지만 key coverage/count/hash가 실제 chunks와 다른 package fixture가 mandatory validator에서 실패하는지 확인한다.
- UseCase `ChunkIndex`와 `LineCountIndex`의 key set 또는 count가 다른 fixture가 실패하는지 확인한다.
- runtime target chunk의 count/boundary가 record와 다르면 `index_content_mismatch` fallback이 기록되는지 확인한다.
- existing line-count missing key가 계속 `0, nil`, chunk/facade load 0인지 확인한다.
- explicit public facade require는 계속 전체 데이터와 동일한 결과를 제공하는지 확인한다.

---

### Change 3 — 성능·할당·fallback 계측 기준선

Purpose:

Browser 증분화와 정적 데이터 재구성 같은 구조 변경을 추정이 아니라 재현 가능한 지표로 결정하고, mandatory 변경이 optional 변경의 before 값을 오염시키지 않게 baseline generation을 분리한다.

Files:

- `IrisBrowserData.lua`
- `IrisBrowserItemIndex.lua`
- `IrisBrowserQuery.lua`
- `IrisItemDetailViewModel.lua`
- `IrisAltTooltip.lua`
- `IrisTooltipSummary.lua`
- `IrisRuntimeLookupDiagnostics.lua`
- Browser/Tooltip Lua acceptance harness 및 metrics receipt

Implementation Notes:

1. 기존 build attempts, item scan, elapsed, cache metrics를 재사용하고 다음 지표만 최소 추가한다.
   - cold first open 및 warm reopen elapsed.
   - first Alt 및 warm Alt summary/display-line cache hit/miss.
   - facade fallback count by consumer/reason.
   - search calls, scanned rows, prefix reuse, result/location copy count.
   - detail method attempts, successful capability groups, cache hit/miss.
   - generation/locale invalidation count.
2. production 로그는 DEBUG 또는 명시적 diagnostics 호출에서만 출력한다.
3. 계측만 추가한 독립 commit의 observational parity를 먼저 검증한 뒤 `baseline-0`을 채취한다. `baseline-0` receipt는 commit/tree, PZ build, mod set, locale, item count, query corpus, run count를 포함한다.
4. Change 2, 4, 5 완료 후 같은 조건으로 `baseline-1`을 채취한다. Change 6, 7, 10은 `baseline-1`과 각 변경 직후 after만 비교한다. `baseline-0`은 mandatory Change 5 및 generated size의 before 용도로만 사용한다.
5. 자동 harness는 고정 item fixture와 가짜 clock을 사용하며 operation count 계약을 검증한다. PZ frame responsiveness를 판정하는 항목은 harness operation count만으로 채택하지 않는다.
6. 실제 Project Zomboid에서는 대표 save와 동일 mod set으로 cold/warm 각 10회 측정하고 median, p95, max, item count를 함께 기록한다. 10회 미만이면 exploratory sample로만 남기고 adoption threshold 판정에 쓰지 않는다.
7. heap delta는 신뢰 가능한 API와 고정된 full-GC 전후 경계가 있을 때만 기록한다. 없으면 proxy metric을 heap으로 표기하지 않는다.
8. metric/denominator/trigger/adoption 기준은 `baseline-0` 전에 다음 표로 봉인한다. 호환성 또는 output parity 실패 시 수치 개선과 무관하게 채택하지 않는다.

| Candidate | Before generation | Metric / denominator | Experiment trigger | Adoption requirement |
|---|---|---|---|---|
| Change 5 inactive/warm Tooltip | `baseline-0` | inactive 1,000 renders, warm active 100 renders | mandatory; 아래 값은 adoption threshold가 아니라 acceptance gate | inactive summary load/draw/temporary detail table 0; warm display-line build 1; public/facade shape parity. 미달 시 rollback/fix가 필요하며 `no-op`으로 닫을 수 없음 |
| Change 6A search/location/copy | `baseline-1` | fixed catalog × approved query/prefix corpus; scans and copies per returned row | location traversal 또는 internal+public row copy가 결과 row당 1회를 초과 | targeted operation count 50% 이상 감소, public copy 1회 이하, 결과/order parity |
| Change 6B capability mask | `baseline-1` | 5종 item 각 20개; group method calls/item | 적용 불가 group call이 1회 이상 | 적용 불가 group call 0, 전체 protected method call 30% 이상 감소, model parity |
| Change 6B static projection | `baseline-1` | same-fullType/different-instance 및 ScriptItem↔InventoryItem 교대 corpus, direct model/sourceItem identity, cold 1회 + warm 100회 | generated static projection의 warm rebuild가 1회를 초과하고 purity inventory가 닫힘 | static cache hit 99/100 이상, instance field는 매 호출 갱신, cross-instance/Browser/Wiki contamination 0, model/sourceItem identity 및 output parity |
| Change 6C search debounce | `baseline-1` | 실제 PZ에서 10-character 입력 sequence 10회; handler p95와 input-to-result p95 | handler p95 > 16.7 ms 또는 한 rendered frame당 full search 1회 초과 | handler p95 <= 16.7 ms 또는 30% 이상 감소, input-to-result p95 <= 50 ms, selection parity |
| Change 6C incremental build | `baseline-1` | 실제 PZ cold open 10회; first-ready p95와 longest build slice | cold first-ready p95 > 50 ms 또는 longest slice > 16.7 ms | longest slice <= 16.7 ms, total first-ready p95가 baseline의 120% 이하, final index parity |
| Change 7 Tooltip static data | `baseline-1` | 실제 PZ first Alt 10회; p95와 module-load/validation attribution | first Alt p95 > 16.7 ms이고 static load가 trace의 30% 이상 | first Alt p95 30% 이상 감소 또는 <= 16.7 ms, summary/facade parity |
| Change 7 LineCount validation | `baseline-1` | first lookup의 validation operations 및 실제 PZ attributable time | first Alt/lookup p95 > 16.7 ms이고 line-count validation이 trace의 20% 이상 | runtime operations 90% 이상 감소와 build exhaustive parity; 새 validation ceiling 승인 |
| Change 10 Ordering | `baseline-1` | fixture별 N rows와 sort-key derivations | derivation count > N + constant | derivation count <= N + constant, anchor/order parity |
| Change 8 CAS batch | storage baseline | verified reclaimable bytes − object/reference/manifest 증가분 | safe closed candidate의 batch 순절감 >= 1 MiB | restore/consumer gates 통과, dangling ref 0, 실제 순절감 > 0 |

9. PZ runtime을 요구하는 Change 6C/7의 trigger를 실제 runtime에서 판정할 수 없으면 `adopted` 또는 `no-op`으로 추정하지 않고 `deferred` 및 `unvalidated_but_in_scope`로 남긴다.
10. Change 6A, 6B-capability, 6B-static, 6C-search, 6C-build, 7-Tooltip, 7-LineCount, 10-Ordering은 각자 별도 metric receipt를 가진다. receipt는 exact pytest test ID 또는 manual scenario ID, denominator identity/hash, baseline generation, raw samples, trigger result와 adoption disposition을 포함하며 서로의 aggregate PASS로 대체할 수 없다.

Validation:

- diagnostics 비활성 시 public 결과와 로그량이 바뀌지 않는지 확인한다.
- reset 후 모든 counter가 0이고 generation/locale 전환이 해당 cache만 무효화하는지 확인한다.
- 동일 fixture의 Run A/Run B operation count와 결과 hash가 동일한지 확인한다.
- `baseline-0`과 `baseline-1` receipt의 commit/tree 및 환경 identity가 각각 고정되고 서로 혼용되지 않는지 validator로 확인한다.

---

### Change 4 — 생성 Lua optional field 및 empty-table 경량화

Purpose:

런타임 의미가 없는 `nil` assignment와 demand-loaded chunk의 빈 `debug_lines`를 생성 단계에서 생략하여 package 크기와 lazy lookup table entry 수를 줄이되, direct public compatibility facade의 entry shape는 복원한다.

Files:

- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua`
- generator validation/parity tests
- `UseCaseDescriptions/Chunk*.lua`
- 관련 index/hash/package manifest
- 별도 exporter가 소유하는 Layer3 optional field는 검증 후에만 포함

Implementation Notes:

1. `strength`, `uniqueness`, recipe navigation `category`가 nil인 경우 field 자체를 생략한다.
2. demand-loaded chunk에서는 빈 `debug_lines` field를 생략한다.
3. direct `IrisUseCaseDescriptions` facade가 전체 chunks를 materialize할 때 `entry.debug_lines == nil`인 각 entry에 새 `{}`를 할당한다. 하나의 shared empty table을 재사용하지 않으며 non-empty `debug_lines`는 그대로 둔다.
4. 이 복원은 explicit full facade의 기존 메모리 shape를 보존한다. 따라서 empty-table 절감 claim은 demand lookup 및 package bytes에 한정하고, full facade materialization 후 heap 절감으로 주장하지 않는다.
5. Lua에서 absent와 nil이 동등하더라도 Python structural validator, byte parser, package verifier와 direct Lua facade consumer가 field 존재를 요구하는지 전수 검색한다.
6. debug line이 실제 존재하는 entry는 그대로 생성한다.
7. EN/KO 문자열, line order, source IDs, route, strength/uniqueness 값이 존재하는 경우의 값은 변경하지 않는다.
8. raw UTF-8 전환은 함께 수행하지 않는다. 기존 escaping 정책을 유지한다.
9. regeneration은 clean disposable checkout에서 한 번 수행하고, 두 번째 generation hash가 동일해야 한다.
10. before/after bytes, chunk field counts, facade rehydration counts를 receipt에 기록한다. 예상 131,821 bytes는 목표가 아닌 사전 추정치다.

Validation:

- 모든 source entry를 normalized semantic object로 읽어 before/after parity를 비교한다.
- debug line이 없는 entry의 public API가 계속 `{}`를 반환하고 caller mutation이 cache/source에 전파되지 않는지 확인한다.
- direct `require("Iris/Data/IrisUseCaseDescriptions")` 결과의 모든 entry에서 `type(entry.debug_lines) == "table"`인지 확인한다.
- 두 empty-debug entry의 `debug_lines`가 같은 table을 공유하지 않고, 한 entry의 mutation이 다른 entry에 전파되지 않는지 확인한다.
- facade materialization → lazy lookup과 lazy lookup → facade materialization 순서에서 semantic result, entry field/type 및 non-alias 계약이 동일한지 확인한다. 후자의 경우 facade rehydration이 require-cached chunk entry를 후행 mutation한다는 사실도 fixture에서 명시적으로 관측한다.
- non-empty debug line fixture와 optional 값 존재 fixture를 검증한다.
- generated package/index/hash 검증과 Lua syntax 검사를 통과해야 한다.

---

### Change 5 — Tooltip hot-path allocation 축소

Purpose:

매 프레임 실행되는 Alt Tooltip 경로에서 불필요한 table, key string 및 복사를 줄이되 public defensive copy를 유지한다.

Files:

- `IrisAltTooltip.lua`
- `IrisTooltipSummary.lua`
- Tooltip 관련 Lua harness 및 acceptance tests

Implementation Notes:

1. Alt가 눌리지 않았거나 item이 없으면 좌표·빈 배열·summary module 로드 전에 즉시 반환한다.
2. public `IrisTooltipSummary.get()`은 기존 copy-on-read를 유지한다.
3. Alt renderer만 사용하는 internal cached-summary 접근자를 추가하거나 summary에서 완성된 display lines를 private하게 cache한다. 반환 객체를 renderer가 수정하지 않는다는 범위를 module 내부로 제한한다.
4. display-line cache는 `fullType -> locale -> revision` 중첩 table로 구성하여 매 render의 연결 key 문자열을 제거한다.
5. cache miss에서 저장용·반환용 이중 copy를 만들지 않는다. private cache의 line array는 renderer의 read-only 순회에만 제공한다.
6. `resetDisplayLineCache()`와 summary reset의 기존 dev/test 의미를 유지한다.
7. 성공 시 3/4 line 구성, 실패 시 2 line 구성, 번역 key와 50자 tag truncation은 보존한다.

Validation:

- Alt=false 반복 호출에서 summary load, detail table allocation counter, draw 호출이 0인지 확인한다.
- 동일 fullType/locale/revision warm render에서 summary build와 display-line build가 증가하지 않는지 확인한다.
- locale 또는 revision 변경 시에만 miss가 발생하는지 확인한다.
- public summary 결과를 caller가 변경해도 다음 public 호출과 renderer cache가 변하지 않는지 확인한다.
- 이 Change는 mandatory이므로 위 acceptance gate 또는 public parity가 실패하면 변경을 rollback하고 수정한다. 해결하지 못하면 Change 5는 `blocked`, 일부 다른 Change가 완료된 전체 execution은 `partial`이며 성능 수치만으로 `no-op` 또는 `adopted` 처리하지 않는다.

---

### Change 6 — Browser/Search/Detail 내부 최적화

Purpose:

Browser build 및 상호작용에서 반복 분류 순회, 복사, 무관한 item method 호출, variant 재계산을 줄인다.

Files:

- `IrisBrowserData.lua`
- `IrisBrowserItemIndex.lua`
- `IrisBrowserQuery.lua`
- `IrisBrowserListController.lua`
- `IrisBrowserVariantIndex.lua`
- `IrisItemDetailViewModel.lua`
- `API/Tags.lua`
- `IrisObjectAccess.lua`
- Browser acceptance harness/tests

Implementation Notes:

이 Change는 세 묶음으로 나누어 독립 채택한다.

#### 6A — 낮은 위험의 generation cache

- build finalization에서 presentation order 기준 `primaryLocationByFullType`을 한 번 계산한다. 이는 의미 분류를 바꾸지 않고 기존 `chooseLocation`이 선택하던 첫 위치를 materialize한 것이다.
- prefix cache에는 canonical private rows를 저장하고, public 반환에서만 한 번 복사한다.
- search sort는 `displayName`, `fullType` 순서를 그대로 유지한다.
- Browser build 내부만 사용하는 immutable tags view 또는 membership helper를 추가하되 `Tags.getTagsForItem()`의 public copy는 유지한다.
- Variant generation cache에는 recipe 존재와 primary tag를 fullType별로 memoize한다. group key는 table identity 또는 build 시 부여한 stable bucket ID를 사용하되 외부 노출 순서는 바꾸지 않는다.
- `IrisObjectAccess`에는 `call0`, `call1` 같은 fixed-arity internal path를 추가해 직접 `ProtectedCall.engine(method, target, arg)`를 사용한다. generic `call`은 호환성을 위해 남긴다.

#### 6B — 상세 ViewModel capability mask와 static/instance projection 분리

- `generation + locale + fullType`만으로 완성 ViewModel을 cache하지 않는다. 현재 model은 InventoryItem instance 상태를 포함하므로 fullType-only whole-model cache는 금지한다.
- method 존재와 item type으로 food/weapon/literature/moveable group의 cheap capability mask를 매 입력에 대해 계산한다. 적용되지 않는 group은 engine method를 호출하지 않되 output model의 기존 key와 nil/empty 형식은 유지한다.
- 다음 instance projection은 `fromItem()` 호출마다 새로 읽고 새 readonly model에 합성한다.
  - `sourceItem`, display name, actual weight, category/subcategory.
  - food/weapon/literature/moveable method 결과.
  - item argument를 받는 tags 및 recipe/moveable/fixing connections. fullType-only 순수성이 별도 증명되기 전에는 정적으로 승격하지 않는다.
- static projection cache 후보는 generated fullType fact임이 이미 명확한 Layer3, UseCase lines, capabilities로 제한한다. key는 generation + locale + fullType이며 InventoryItem 또는 ScriptItem reference를 보존하지 않는다.
- 기존 `values.revision = fullType|locale`은 generation과 instance state를 포함하지 않으므로 whole-model 또는 static projection cache key로 사용하지 않는다. public shape 보존이 필요한 동안에는 값만 유지하고, 제거 또는 `staticRevision` 같은 이름으로 변경하려면 별도 consumer census와 field-shape 승인을 거친다. private static cache key는 generation + locale + fullType에서 별도로 구성한다.
- `fromItem()`은 cached static projection을 읽더라도 instance projection과 최종 values/readonly wrapper를 매번 새로 만든다. 한 instance의 table 또는 `sourceItem`이 다른 instance model에 공유되지 않아야 한다.
- 신뢰 가능한 item-state revision을 새로 가정하거나 합성하지 않는다. static projection 효과가 임계값 미만이거나 purity를 증명하지 못하면 capability mask만 채택하고 static cache는 `no-op`으로 닫는다.
- readonly proxy, availability flags, sorted tags, recipe/moveable/fixing/layer3 결과와 Browser/Wiki output shape는 유지한다.

#### 6C — 조건부 search debounce와 incremental Browser build

- 키 입력 연속 측정에서 frame 또는 scan 예산 초과가 확인될 때만 controller-level debounce를 추가한다. keyboard selection과 빈 검색의 즉시 category 복귀는 보존한다.
- cold first open이 고정 임계값을 넘을 때만 build를 `scanning -> classifying -> finalizing -> ready` state machine으로 분해한다.
- 한 tick은 item 수 또는 시간 budget 중 먼저 도달한 한계를 따른다. Browser가 열린 동안에만 진행하고 loading 상태를 명시한다.
- public synchronous compatibility entry가 있다면 completion을 drive할 수 있어야 하며 partial cache를 ready로 노출하지 않는다.
- close/reopen, locale/generation invalidation, build error에서 상태가 일관되게 reset되어야 한다.

Validation:

- 기존 category/subcategory/item order와 representative item의 primary location이 byte-for-byte 동일한지 비교한다.
- 검색 결과 및 정렬이 모든 prefix 단계에서 기존 결과와 동일하고 public result mutation이 cache에 영향을 주지 않는지 확인한다.
- detail model normalized parity와 method-call count 감소를 item type별 fixture로 확인한다.
- 같은 fullType의 서로 다른 InventoryItem 두 개를 교대로 조회해 weight/hunger/thirst/display name 등 instance 값이 섞이지 않는지 확인한다.
- `sourceItem`은 현재 렌더 consumer가 없으므로 화면 문자열만 비교하지 않는다. 반환 model A/B의 `sourceItem`을 각 입력 object와 직접 identity 비교하고 model/table identity가 서로 다른지 확인한다.
- 같은 InventoryItem의 상태를 변경한 뒤 재조회했을 때 instance projection이 갱신되는지 확인한다.
- ScriptItem → InventoryItem, InventoryItem → ScriptItem, Browser → Wiki, Wiki → Browser 순서에서도 static cache가 source object나 instance 값을 전파하지 않는지 확인한다.
- incremental branch가 채택되면 작은 tick budget으로 모든 상태 전이, loading UI, 중간 close/reopen, error reset, deterministic final index를 검증한다.

---

### Change 7 — Tooltip 정적 데이터와 LineCountIndex의 조건부 구조 선택

Purpose:

첫 Alt에서 네 개 정적 index를 모두 상주시킬 가능성과 1,631-entry line-count 전수 검증 비용을 계측 결과에 따라 줄인다.

Files:

- `IrisTooltipSummary.lua`
- `IrisUseCaseDescriptionsLookup.lua`
- `UseCaseDescriptions/LineCountIndex.lua`
- `convert_descriptions_to_lua.py`
- 필요 시 새 compact Tooltip summary 또는 chunk modules
- corruption/parity harness

Implementation Notes:

1. Change 3에서 first Alt module count, elapsed, resident data proxy와 line-count validation operation 수를 먼저 측정한다.
2. Change 2의 same-generation 및 index↔chunk↔line-count parity validator는 이 Change의 선행 불변식이며, 이 Change가 `no-op`이어도 유지된다. Change 7은 runtime validation 비용/구조만 선택하며 authoritative miss의 정당성을 새로 만들지 않는다.
3. Tooltip 정적 데이터는 다음 중 하나만 선택한다.
   - 현 구조 유지: 비용이 임계값 미만이면 no-op.
   - compact summary index: fullType별 sorted tags, connection flags, use-case count를 생성 시 합성.
   - chunked summary: compact index 자체가 과도할 때 fullType router로 분할.
4. `LineCountIndex`도 다음 중 하나만 선택한다.
   - 현 전수 검증 유지.
   - build-time exhaustive validation + runtime top-shape/entry-count/deterministic sentinel validation.
   - compact/chunked summary가 line count를 소유하면 기존 index consumer를 단계적으로 제거.
5. runtime 전수 corruption 검출을 줄이는 선택은 validation ceiling 변경이므로 architecture/decision 문서에 명시한다.
6. build generator는 어떤 선택에서도 full key parity, integer/non-negative count, chunk target 존재, deterministic output을 전수 검증한다.
7. compact data는 기존 Recipe/Moveables/Fixing/Classifications authority의 파생물이며 새 의미 authority가 아니다.

Validation:

- 전체 fullType에 대해 기존 summary와 새 summary의 normalized parity를 비교한다.
- 대표 corruption fixture가 새 runtime validation 범위 안에서 fail-closed하는지 확인한다.
- runtime에서 더 이상 검출하지 않는 내부 entry corruption은 build-time validator가 반드시 검출하는지 확인한다.
- first Alt before/after module load, elapsed, operation count를 비교하고 임계값 미달이면 변경을 채택하지 않는다.

---

### Change 8 — historical staging 중복의 기존 CAS 전환

Purpose:

직접 소비되지 않는 역사적 중복 payload의 repository 물리 중복을 줄이면서 logical path의 추적성, 복원성, authority를 보존한다.

Files:

- `migrate_repository_evidence.py`
- `repository_evidence_codec.py`
- 현재 audit family resolver
- `evidence/objects/sha256/**`
- `evidence/references/**`
- 선택된 staging logical artifacts와 lifecycle manifests

Implementation Notes:

1. tracked staging 전체를 hash, size, producer, role, consumer, authority, required-validation 상태로 inventory한다.
2. consumer exception, 신규 object, reference 및 manifest bytes를 뺀 verified batch 순절감이 1 MiB 미만이면 disposition을 수행하지 않고 Change 8을 `complete/no-op`으로 닫는다. 안전 기준을 낮춰 임계값을 맞추지 않는다.
3. 같은 hash라도 다음은 기본적으로 physical exception이다.
   - current authority 또는 current required validation input.
   - 실행 가능한 source/script.
   - historical runner가 physical path를 직접 여는 input.
   - consumer를 완전히 찾지 못한 파일.
   - 참조보다 작은 파일 또는 1:1 unique object로 절감이 없는 파일.
4. 기존 object store와 reference schema를 확장한다. 별도 CAS를 만들지 않는다.
5. resolver는 physical path 우선 호환성을 지원할 수 있지만, reference를 선택한 뒤 object가 missing/corrupt하면 stale physical data로 조용히 fallback하지 않고 fail-closed한다.
6. migration은 artifact family별 작은 transaction으로 수행한다.
   - inventory/plan
   - unique object promote
   - references write
   - object hash/size verify
   - 외부 임시 위치로 restore
   - original과 byte compare
   - consumer route 검증
   - 승인된 logical duplicate만 disposition
   - dangling reference 0 검증
7. 삭제 또는 외부 archive는 exact target list와 owner 승인이 있는 별도 destructive gate에서만 수행한다. 1 MiB 이상 안전 후보가 있지만 승인이 없으면 Change 8은 `blocked`, 전체 execution은 다른 항목이 완료되었더라도 `partial`로 닫는다.
8. Git history는 건드리지 않는다.

Validation:

- migration tool의 plan/promote/verify/restore/disposition/cleanup 경로를 fixture로 검증한다.
- missing object, wrong hash, wrong size, path traversal, absolute path, unresolved consumer를 fail-closed하는지 확인한다.
- dispose 전 모든 선택 artifact를 외부 임시 위치로 복원하고 byte hash가 원본과 같은지 확인한다.
- current/historical required route를 전환 전후 각각 실행한다.
- 최종 tracked file count, physical bytes, object unique bytes, reference count, dangling refs를 기록한다.

---

### Change 9 — current Round 3 runner의 Git subprocess 배치화

Purpose:

각 test/target path마다 실행되는 `git ls-files --error-unmatch`와 `git check-ignore -q` subprocess를 startup batch query로 치환한다.

Files:

- `Iris/_docs/round3/round3_run_contract_tests.py`
- runner Git query parity tests
- 필요 시 이미 배치 구현이 있는 `round3_generate_evidence.py`의 family-local helper

Implementation Notes:

1. runner가 검사할 canonical repository-relative path set을 먼저 수집한다.
2. tracked set은 한 번의 `git ls-files`로 만들고, ignored 상태는 `git check-ignore --stdin` 배치로 조회한다.
3. path ordering, nonexistent path, ignored-but-untracked, Git command failure의 기존 판정을 fixture로 고정한다.
4. current runner만 변경하고 sealed historical scripts를 범용 helper에 연결하지 않는다.
5. 호출 횟수는 path 수에 비례하지 않는 고정 상한으로 테스트한다.
6. batch helper를 공유할 경우 같은 Round 3 family 안에 두고 stdout encoding, cwd, return-code 계약이 완전히 동일한지 증명한다.

Validation:

- tracked, ignored, untracked, missing, space/Unicode path fixture에서 기존 함수와 batch 결과가 같다.
- Git failure가 성공 또는 empty set으로 오인되지 않는지 확인한다.
- representative current route의 selected test IDs, imported targets, closure 결과가 변경 전과 동일하다.
- subprocess spy로 Git 호출 수가 O(paths)에서 고정 batch 수로 줄었는지 확인한다.

---

### Change 10 — Ordering 및 나머지 runtime micro-optimization

Purpose:

계측에서 확인된 comparator와 protected object access의 반복 비용을 작은 내부 변경으로 줄인다.

Files:

- `Iris/Logic/IrisDesc/Ordering.lua`
- Ordering consumers/tests
- Change 6에서 선택된 `IrisObjectAccess.lua`, Tags, Variant files

Implementation Notes:

1. subcategory sort 전에 code, priority, translated/stable key를 한 번 decorate하고 comparator는 저장된 scalar만 비교한다.
2. anchor 선택과 order가 각각 sort하지 않도록 내부 caller를 `resolveSubcategories` 단일 pass로 모은다.
3. public `compareTags`, `pickAnchor`, `orderSubcategories` 함수는 compatibility wrapper로 유지한다.
4. priority, anchor, fallback code order, locale별 표시 순서를 변경하지 않는다.
5. Change 6의 ObjectAccess/Tags/Variant 최적화도 before counter가 유의미한 경우에만 함께 채택한다.

Validation:

- 전체 알려진 category/subcategory fixture의 anchor와 order parity를 비교한다.
- 같은 입력의 Run A/Run B 결과가 동일하다.
- comparator sort-key 호출 수와 protected call 수가 예상 상한 이하인지 확인한다.

---

### Change 11 — Python subprocess 및 helper의 계약 기반 정리

Purpose:

광범위한 기계적 치환 없이, 실제로 같은 계약을 가진 current producer/test group만 정리한다.

Files:

- AST inventory/decision receipt
- 채택된 current producer/test files
- 해당 family의 기존 common module
- 새 `Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py`

Implementation Notes:

1. subprocess call을 목적별로 분류한다.
   - 유지: CLI entrypoint, exit code, cwd, env, stdout/stderr, timeout, process isolation을 검증.
   - 후보: pure Python function의 결과만 검증하고 import side effect가 없는 test.
2. 후보는 in-process 호출과 기존 subprocess 결과를 같은 fixture에서 비교한 후에만 전환한다.
3. helper 후보는 AST body뿐 아니라 encoding, newline, indent, sort keys, atomic replace, exception type/message, cwd/path, CLI exit 의미까지 fingerprint한다.
4. 동일 current producer가 3개 이상인 group만 기존 `Iris/build/tools/common` 또는 description-v2 family common으로 옮긴다.
5. historical/diagnostic reproduction script는 current helper에 새로 의존시키지 않는다.
6. 기존 Change 8 조사처럼 안전한 group이 없으면 `no-op`으로 종결한다.
7. review census의 `tools/build` 484 files, `load_json` 145 definitions, `write_json` 91 definitions, `sha256_file` 58 definitions는 후보 규모를 보여 주지만 계약 동등성을 증명하지 않는다. producer 3개 이상과 전체 fingerprint 기준을 완화해 adoption을 강제하지 않으며, 결과가 zero-adoption이어도 inventory/decision receipt가 exit 0이면 계획상 유효한 `no-op`이다.

Validation:

- 모든 실행에서 다음 inventory/decision test를 요구한다.
  - `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py::PythonToolingContractCommonizationTest::test_inventory_and_decision_receipt`
  - denominator는 AST inventory가 찾은 전체 subprocess call site와 helper candidate group이며 expected exit은 0이다.
- 하나 이상을 채택하면 다음 parity test도 필수다.
  - `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py::PythonToolingContractCommonizationTest::test_adopted_consumers_preserve_cli_and_output_contract`
  - denominator는 adopted consumer 전부와 pre-change golden cases이며 expected exit은 0이다.
- adopted candidate가 0이면 두 번째 test를 PASS로 가장하지 않고 `not_applicable` evidence를 첫 번째 receipt에 기록한다. `not_applicable`은 closeout state가 아니다.
- 전환된 test의 result/exception/side-effect parity를 비교한다.
- CLI boundary test 수가 줄어들지 않았는지 확인한다.
- helper consumer별 golden output, encoding, newline, deterministic hash를 비교한다.
- full current route elapsed before/after를 기록하고 개선이 없으면 구조 변경을 되돌린다.

---

### Change 12 — 통합 채택 결정과 closeout

Purpose:

각 변경의 효과, 보존된 계약, 남은 validation limit를 권한 문서와 evidence에 반영한다.

Files:

- metrics/adoption/closeout receipt
- `docs/DECISIONS.md`
- 필요 시 `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

Implementation Notes:

1. 각 measurement-gated 항목을 `adopted`, `no-op`, `deferred`, `blocked` 중 하나의 item disposition으로 기록한다. 이는 새 closeout state enum이 아니며 §12에서 `complete`, `partial`, `implemented_only`, `blocked` 중 하나로 환원한다.
2. `no-op`은 실패가 아니라 threshold 미달 또는 이미 충분히 경량인 결정으로, 근거 metric을 포함한다.
3. runtime fallback 의미, source classification과 exact authority의 분리, runtime validation ceiling이 바뀐 경우에만 architecture를 additive하게 갱신한다.
4. roadmap에는 완료된 항목과 남은 owner/action을 분리한다.
5. 최종 size/time 수치는 baseline과 동일한 명령·subject root·item count로 다시 측정한다.
6. 예상치, 부분 측정치, 실제 Project Zomboid 측정치를 섞지 않는다.

Validation:

- receipt가 기준 commit, commands, exit codes, artifact hashes, before/after 지표, validation limits를 포함하는지 확인한다.
- docs의 완료 주장이 실제 exit code 0 결과와 일치하는지 검토한다.
- clean worktree 또는 명시된 generated/evidence diff만 남는지 확인한다.

---

## 7. Validation Plan

### Automated Validation

mandatory chain은 표의 순서대로 실행한다. required exit가 0이 아니면 뒤 단계의 PASS를 주장하지 않는다. `all` execution advisory row만 이 fail-fast chain 밖에서 별도로 실행한다.

아래 test file, class 및 method node ID는 규범적 이름이다. 구현은 표의 이름을 그대로 사용해야 하며, 이름을 바꾸려면 먼저 이 계획과 denominator manifest를 additive하게 개정해 stale command가 남지 않게 한다.

| Change / Gate | Exact command | Denominator | Required exit | 허용되는 claim |
|---|---|---|---:|---|
| Change 1 policy contract | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_round3_pytest_source_classification.py` | 분류 4종, 미분류 49개, ignore 6개, known ImportError 2개와 모든 collection blocker disposition, owner approval, mixed override fixtures | 0 | source policy/importability contract validated |
| Change 1 failure classifier | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_round3_pytest_failure_classification.py` | current/modified/mandatory/historical/diagnostic/unknown 및 mixed source failure fixtures | 0 | advisory failure classification validated |
| Gate A default current collection | `uv run python -m pytest --collect-only -q --round3-contract=current --round3-enforce-denominator` | approved current sources + cross-track source + exact mixed current overrides | 0 | configured current collection closed |
| Gate A full denominator collection | `uv run python -m pytest --collect-only -q --round3-contract=all --round3-enforce-denominator` | 승인된 current + historical + diagnostic included source 전부, cross-track, included-source collection error/deselection 0, excluded receipt 완전성 | 0 | configured full denominator/importability closed; test execution PASS는 아님 |
| Exact current authority | `uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure` | exact taxonomy current IDs + `current_route_required_validations.json` | 0 | sealed current route validated |
| Change 2 package invariant + lazy miss | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_lookup_package_parity_contract.py Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py` | 전체 Layer3/UseCase packaged key set/count/hash/generation + 존재/miss/fault fixtures | 0 | authoritative negative와 fallback 분리 validated |
| Change 3 metrics contract | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py` | baseline identity, reset, instrumentation on/off, fixed operation corpus | 0 | harness operation metrics validated; PZ timing claim은 아님 |
| Change 4 sparse generation/facade | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_generated_lua_sparse_fields_contract.py Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py` | 전체 generated UseCase entries + direct facade field/type/alias + facade→lazy/lazy→facade fixtures + Run A/B | 0 | semantic/package/direct-facade parity validated |
| Change 5 Tooltip allocation | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py` | inactive 1,000 + warm active 100 renders, public mutation fixtures | 0 | Tooltip harness allocation/copy contract validated |
| Change 6A search/location | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_6a_search_location_copy_receipt` | fixed catalog × query/prefix corpus | 0 | Change 6A candidate receipt validated |
| Change 6B capability mask | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_6b_capability_mask_receipt` | five item kinds × 20, applicable/inapplicable group call counts | 0 | capability-mask candidate receipt validated |
| Change 6B static projection | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_6b_static_projection_instance_isolation_receipt` | same-fullType/different-instance + state mutation + direct model/sourceItem identity + ScriptItem↔InventoryItem + Browser↔Wiki, 채택 시 `PZ-6B-INSTANCE-01` | 0 | harness instance isolation validated; adoption에는 named PZ receipt도 필요 |
| Change 6C search debounce | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_6c_search_debounce_receipt` | harness event corpus + `PZ-6C-SEARCH-01` 10-sequence manual receipt | 0 | harness contract validated; adoption에는 named PZ receipt도 필요 |
| Change 6C incremental build | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_6c_incremental_build_receipt` | state-transition corpus + `PZ-6C-BUILD-01` cold-open 10회 receipt | 0 | state-machine contract validated; adoption에는 named PZ receipt도 필요 |
| Change 7 Tooltip static | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_7_tooltip_static_receipt` | fullType summary parity + `PZ-7-TOOLTIP-01` first-Alt 10회 receipt | 0 | static-data candidate contract validated |
| Change 7 LineCount | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_7_linecount_receipt` | full key/count/corruption corpus + `PZ-7-LINECOUNT-01` attribution receipt | 0 | LineCount candidate/ceiling contract validated |
| Change 10 Ordering | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_runtime_optimization_metrics.py::RuntimeOptimizationMetricsTest::test_change_10_ordering_receipt` | full approved category/subcategory fixture corpus | 0 | Ordering candidate receipt validated |
| Change 8 CAS codec/migration | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_repository_evidence_codec.py Iris/build/description/v2/tests/test_repository_evidence_migration.py` | path safety, object/reference, restore, disposition 및 failure fixtures | 0 | migration tooling validated; 실제 disposition/byte saving claim은 아님 |
| Change 9 Git batching | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_round3_git_batch_contract.py` | tracked/ignored/untracked/missing/Unicode fixtures 및 subprocess call bound | 0 | Git query parity validated |
| Change 11 inventory/no-op | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py::PythonToolingContractCommonizationTest::test_inventory_and_decision_receipt` | 전체 AST subprocess/helper inventory와 candidate disposition | 0 | inventory 및 zero-adoption no-op decision validated |
| Change 11 adopted parity | `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_python_tooling_contract_commonization.py::PythonToolingContractCommonizationTest::test_adopted_consumers_preserve_cli_and_output_contract` | adopted consumer 전부 + pre-change golden cases | 0 if any adopted; N/A otherwise | adopted tooling parity validated |
| Lua syntax | `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | repository Lua syntax checker의 configured denominator | 0 | configured Lua syntax PASS |
| Terminal current smoke | `uv run python -m pytest -q --round3-contract=current --round3-enforce-denominator` | approved current pytest denominator | 0 | configured current pytest execution PASS |
| Diff integrity | `git diff --check` | execution diff | 0 | whitespace/error check PASS |

#### Configured full execution — advisory chain

다음 명령은 Change 1의 source disposition/importability gate가 닫힌 뒤 clean disposable checkout에서 실행한다.

```powershell
uv run python -m pytest -q --round3-contract=all --round3-enforce-denominator
```

- 이 command의 denominator는 mandatory full collection row와 동일하다.
- exit 0이면 configured full-suite PASS를 별도로 주장할 수 있다.
- nonzero 자체는 scoped current optimization의 자동 실패가 아니다. Change 1의 validated classifier가 source manifest, mixed override, modified path set과 mandatory ownership으로 각 failure를 `current/modified/mandatory-invariant`, `historical`, `diagnostic`, `excluded-contract-drift`, `unknown`으로 기계 분류한다.
- `current/modified/mandatory` 우선순위는 historical/diagnostic보다 높고, unknown 또는 source-level mixed error는 `unvalidated_but_in_scope`다. 수동 review는 severity를 올릴 수만 있으며 current/modified failure를 historical로 낮출 수 없다.
- `current/modified/mandatory-invariant` failure가 하나라도 있으면 `unvalidated_but_in_scope`이며 전체 `complete`를 차단한다.
- historical/diagnostic에만 한정되고 current exact/focused rows가 모두 0이면 그 failure는 이번 optimization success claim의 `out_of_scope`로 기록할 수 있지만 full-suite PASS를 주장할 수 없다.

#### Generated Data and CAS Transaction Validation

- generator는 clean disposable checkout과 외부 work root에서 실행하고 Run A/Run B generated tree hash를 비교한다. generator가 `--help`를 지원한다고 가정하지 않으며 production tree에서 probe invocation을 하지 않는다.
- normalized semantic parity, key set, line order, EN/KO content, non-empty debug lines, direct facade empty-table rehydration, package/hash/index linkage를 비교한다.
- CAS inventory와 plan은 read-only로 먼저 실행한다. actual command에는 receipt에 봉인된 absolute repo/source/output paths를 사용한다.
- 선택 family는 disposition 전에 외부 임시 위치로 restore하여 original과 SHA-256/size를 비교한다.
- missing/corrupt object, unsafe path, unresolved consumer negative fixtures와 필요한 historical exact route를 실행한다.

#### Performance Parity

- 동일 baseline generation, fixture, locale, item count, query corpus로 before/after operation metrics를 비교한다.
- 실제 시간 수치는 Change 3 표에 따라 같은 PZ 환경에서 cold/warm 각 10회 측정해 median, p95, max를 기록한다.
- public normalized output hash와 direct facade shape는 성능 변경 전후 동일해야 한다.

### Manual Validation

- Project Zomboid를 시작했을 때 Iris가 부팅 시 Browser item scan을 하지 않는지 확인한다.
- Browser 첫 열기, 닫기/재열기, category/subcategory 이동, 전역 검색, prefix 입력/삭제, keyboard 선택을 확인한다.
- 증분 build가 채택된 경우 loading 중 UI가 partial data를 정상 결과처럼 표시하지 않는지 확인한다.
- base item과 외부/mod item을 우클릭해 Iris 진입 및 missing data 표시를 확인한다.
- Alt를 누르지 않은 tooltip, 첫 Alt, warm Alt, locale 변경 후 Alt를 확인한다.
- food, weapon, literature, moveable, unclassified item의 상세 필드와 variant 이동을 비교한다.
- `PZ-6B-INSTANCE-01`: 같은 fullType이지만 weight/food state 또는 display name이 다른 InventoryItem 두 개를 Browser/Wiki에서 교대로 열고, 한 instance 상태 변경 뒤 재조회하여 stale/cross-instance 표시가 없는지 확인한다.
- EN/KO에서 표시 문자열, 정렬, 검색 결과가 동일한 의미를 유지하는지 확인한다.
- DEBUG diagnostics가 꺼진 일반 플레이에서 추가 spam이 없는지 확인한다.
- 선택된 CAS artifact를 실제 tool로 복원하고 사람이 reference의 logical path/role/producer를 확인한다.

### Validation Limits

모든 Heavy closeout은 다음 세 구분을 표로 제출한다.

| Ceiling class | 이 계획에서의 처리 |
|---|---|
| `validated` | exact command, denominator, input identity, exit code 또는 PZ manual receipt가 있는 surface만 기록한다. |
| `out_of_scope` | 장시간 multiplayer, dedicated server, 비-Windows OS, Git history size, raw UTF-8, Registry 분할, 고유 evidence archive, 모든 historical/diagnostic correctness처럼 명시적으로 영향/성공 claim 밖에 둔 영역을 기록한다. |
| `unvalidated_but_in_scope` | adopted runtime change의 PZ 검증 부재, current/modified full-execution failure, 모든 third-party mod/direct consumer 전수 sweep, 알려진 direct consumer 미검증, 안전 CAS candidate의 승인 부재처럼 scope 안이지만 증거가 없는 영역을 기록한다. 해당 영역의 success claim은 금지한다. |

- Change 2가 외부/mod lookup path 자체에 영향을 주므로 모든 제3자 모드·direct consumer의 전수 sweep은 `unvalidated_but_in_scope`다. validated로 주장할 수 있는 범위는 index range 안/밖 synthetic external fullType, 대표 실제 mod set, public facade contract뿐이며 보편 호환성은 주장하지 않는다.
- PZ runtime이 없으면 PZ-dependent Change 6C/7은 `deferred`와 `unvalidated_but_in_scope`다. 이를 `no-op`으로 바꾸지 않는다.
- 신뢰 가능한 Kahlua/PZ heap API가 없으면 heap 수치는 `out_of_scope`가 아니라 해당 heap 절감 claim을 하지 않는 validation limit로 명시한다. operation/module/byte proxy를 heap으로 부르지 않는다.
- configured full execution이 격리된 checkout에서도 실행 불가능하면 full-suite claim은 `unvalidated_but_in_scope`로 남고 전체 `complete`를 허용하지 않는다. 실행 가능하고 historical/diagnostic failure만 있는 경우에는 위 advisory 규칙을 따른다.
- CAS safe candidate가 없거나 batch 순절감이 1 MiB 미만이면 `validated complete/no-op`이다. 1 MiB 이상 safe candidate가 있고 disposition approval만 없으면 Change 8은 `blocked`, 전체 closeout은 `partial`이다.
- full current route, modified-source focused tests, mandatory package invariant 중 하나라도 검증되지 않으면 `complete`가 아니다.

---

## 8. Risk Surface Touch

### Authority Surface

높음. 일반 pytest 발견 정책과 exact Round 3 authority를 분리한다. source classification은 편의용 current 권한 확장이 아니며 exact runner와 required validation manifest가 계속 최종 권한이다.

### Runtime Behavior Surface

중간~높음. lookup miss/fault 분기, Tooltip cache, Browser search/detail/build, optional LineCount validation이 런타임 경로를 건드린다. 모든 변경은 public normalized output parity와 fallback diagnostics를 요구한다.

### Compatibility Surface

중간. 공개 facade와 copy-on-read는 유지하지만, 정상 miss에서 더 이상 전체 facade가 side effect로 로드되지 않는다. 외부 code가 이 비공개 side effect에 의존하는 경우를 호환 계약으로 인정하지 않되 explicit facade require는 보존한다.

### Sealed Artifact Surface

높음. Round 3 taxonomy/required validation과 historical staging을 읽고 일부 reference 전환을 수행할 수 있다. exact authority file의 의미 변경과 logical artifact 삭제는 별도 승인 gate가 필요하다.

### Public-Facing Output Surface

낮음~중간. UI 문구, 정렬, 필드, line order의 변경은 목표가 아니다. loading UI는 incremental build가 채택될 때만 새로 보일 수 있다.

---

## 9. Risk Analysis

### Architecture Risk

- source classification이 exact taxonomy를 사실상 대체하면 current authority가 조용히 넓어질 수 있다.
- executor가 미분류 source나 ignore source를 자체 승인하면 discovery policy가 새 authority가 될 수 있다.
- compact Tooltip summary가 원본 index와 별도 의미 authority로 굳어질 수 있다.
- ItemDetail의 fullType authority와 InventoryItem instance facts를 같은 cache owner가 구분 없이 소유할 수 있다.
- 새 helper 또는 CAS resolver가 family 경계를 넘어 또 다른 중앙 결합점을 만들 수 있다.
- incremental Browser state가 기존 synchronous public facade와 이중 생명주기를 만들 수 있다.

Mitigation:

- exact runner/required IDs는 별도 보존하고 set parity를 검증한다.
- 49개 미분류 source, ignore 6개, known historical ImportError 2개 및 이후의 모든 collection blocker는 owner-approved disposition/importability proof가 없으면 Gate A를 차단한다.
- compact data는 generator가 원본 authority에서 만든 파생물로 명시한다.
- ViewModel을 generated static projection과 per-call instance projection으로 분리하고 whole-model cache를 금지한다.
- 기존 common/CAS 인프라만 확장하고 새 전역 abstraction은 최소화한다.
- partial/ready 상태와 synchronous compatibility 동작을 명시적 state contract로 테스트한다.

### Runtime Risk

- `lookup_miss`와 router fault를 잘못 분류하면 실제 손상이 빈 결과로 숨겨질 수 있다.
- same-generation 또는 index↔chunk coverage가 깨진 package에서 `lookup_miss`를 authoritative로 쓰면 데이터 손실을 정상 부재로 위장할 수 있다.
- private cached table이 renderer 밖으로 유출되면 mutation이 세션 전체에 남을 수 있다.
- detail cache가 locale 또는 generation 전환 후 stale 데이터를 보여줄 수 있다.
- fullType-only whole-model cache가 같은 type의 서로 다른 InventoryItem weight/food 상태/source identity를 교차 오염시킬 수 있다.
- incremental build가 닫힌 UI에서도 계속되거나 partial index를 노출할 수 있다.
- runtime LineCount 검증 축소는 일부 package corruption의 발견 시점을 build-time으로 이동시킨다.

Mitigation:

- reason allowlist와 unknown-reason fail-closed fallback을 둔다.
- Change 2의 full key/count/hash/generation parity를 mandatory로 두고 loaded-chunk count/boundary를 검증한다.
- private accessor의 consumer를 module-local로 제한하고 public copy isolation test를 유지한다.
- 모든 cache key와 reset 계약에 generation/locale을 포함한다.
- 완성 ViewModel은 cache하지 않고 generated static projection만 제한적으로 cache하며 instance projection과 readonly wrapper는 매 호출 새로 만든다.
- 상태 전이와 cancellation harness를 추가한다.
- validation ceiling 변경을 명시하고 build-time exhaustive validator를 필수화한다.

### Compatibility Risk

- 검색 결과 copy 축소가 caller mutation 격리를 깨뜨릴 수 있다.
- optional generated field 생략을 Python validator 또는 문자열 기반 consumer가 구조 변경으로 볼 수 있다.
- 빈 `debug_lines` 생략이 direct `IrisUseCaseDescriptions` facade의 field-presence를 깨뜨릴 수 있다.
- ObjectAccess fixed-arity path가 Java/Kahlua method binding 의미를 바꿀 수 있다.
- Ordering key 사전 계산이 locale 또는 fallback 처리 순서를 바꿀 수 있다.

Mitigation:

- public boundary의 단일 defensive copy는 유지한다.
- 모든 field-name consumer를 검색하고 semantic parity와 public return shape를 함께 검증한다.
- full facade materialization 시 entry별 독립 `{}`를 복원하고 direct field/type/non-alias test를 요구한다.
- fixed-arity는 representative zero/one-argument engine stub에서 generic path와 비교한다.
- 전체 category/subcategory anchor/order golden parity를 요구한다.

### Regression Risk

- pytest 수집 복구 후 이전에 실행되지 않던 current tests가 실제 실패를 드러낼 수 있다.
- CAS 전환 후 direct path consumer 누락이 뒤늦게 발견될 수 있다.
- debounce가 keyboard/programmatic selection 또는 빈 query 복귀를 지연시킬 수 있다.
- 성능 계측 자체가 hot path 비용을 늘릴 수 있다.
- mandatory Tooltip 변경 뒤의 수치를 original baseline으로 오인하면 optional candidate의 효과 판정이 왜곡될 수 있다.

Mitigation:

- 새로 드러난 실패는 수집 문제와 제품 회귀를 분리해 taxonomy로 기록한다.
- consumer scan, restore, current/historical route를 disposition 전 필수 gate로 둔다.
- debounce는 실측 문제가 있을 때만 채택하고 UI event 계약을 테스트한다.
- counters는 DEBUG/diagnostics opt-in이며 production logging을 추가하지 않는다.
- `baseline-0`과 `baseline-1`의 commit/tree/environment identity를 별도 receipt로 봉인한다.

### Storage and Destructive-Action Risk

- hash가 같아도 artifact role 또는 logical provenance가 다를 수 있다.
- reference object 손상, dangling reference, 잘못된 target list가 복구 불가능한 손실을 만들 수 있다.
- 예상 절감치를 달성하려고 current/unique artifact까지 과도하게 전환할 수 있다.

Mitigation:

- role과 logical reference를 보존하고 content equality만으로 삭제를 승인하지 않는다.
- exact absolute target 확인, 외부 restore, byte compare, owner approval 뒤에만 disposition한다.
- unique/current/direct-consumer artifact는 기본 보존한다.
- 최종 실제 절감치가 작더라도 안전 기준을 완화하지 않는다.

---

## 10. Rollback Plan

1. 모든 변경은 Change 단위의 작은 commit 또는 독립 diff로 유지한다. runtime, generated data, CAS disposition을 한 commit에 섞지 않는다.
2. Change 1 실패 시 exact taxonomy 변경이 있었다면 그 owner-approved commit을 먼저 되돌리고, 그다음 denominator/source manifest와 기존 description-v2 conftest 변경을 되돌린다. excluded historical source를 복원했던 경우 producer와 source disposition을 같은 preimage로 함께 복구한다. exact runner와 required-validation manifest는 predecessor 상태로 복구한다.
3. Change 2 실패 시 consumer reason 분기를 되돌려 기존 compatibility fallback으로 복구한다. diagnostics reason 추가는 독립적으로 제거 가능해야 한다.
4. Tooltip/Browser cache 실패 시 public facade와 기존 synchronous code path를 feature-neutral fallback으로 남겨 즉시 되돌릴 수 있게 한다.
5. Change 6B instance-isolation fixture가 실패하면 static projection cache를 제거하고 capability mask-only 구현으로 복귀한다. whole-model cache 또는 임의 item revision 추가로 우회하지 않는다.
6. incremental Browser build는 별도 채택 commit으로 두며, 문제가 생기면 `ensureReady()`의 기존 synchronous implementation으로 복귀한다.
7. generated Lua 최적화 실패 시 기준 commit의 generator, generated tree, direct facade rehydration을 함께 복원한다. generator만, output만 또는 facade adapter만 단독 rollback하지 않는다.
8. `LineCountIndex` 구조 변경 실패 시 기존 1,631-entry index와 전수 runtime validation을 복원한다.
9. CAS logical artifact disposition 전에는 원본을 삭제하지 않는다. disposition 후 rollback은 verified object와 reference manifest로 외부 임시 위치에 restore한 뒤 exact logical path로 복구하고, hash/size 검증 후 reference 전환 diff를 되돌린다.
10. Git batch query 실패 시 per-path 구현으로 되돌리고 selected IDs/closure parity receipt를 보존한다.
11. helper/subprocess 정리는 consumer별로 되돌릴 수 있게 하며 역사적 script에는 migration을 강제하지 않는다.
12. rollback 후 관련 focused tests, current route, Lua syntax, generated parity를 다시 실행한다. exit code 0이 없으면 복구 완료로 주장하지 않는다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 정적 위키, 무추론, 무추천, 무비교 원칙을 지킨다.
- Hub는 shared authority와 routing을 소유하고 spoke 간 직접 결합을 추가하지 않는다.
- runtime path는 build/evidence generation 모듈에 의존하지 않는다.
- public facade, return shape, copy-on-read, translation fallback, ordering을 보존한다.
- direct `IrisUseCaseDescriptions` facade의 `debug_lines` field/type도 public compatibility shape로 보존하며 empty tables를 entry 간 공유하지 않는다.
- 정상적인 데이터 부재와 인프라 손상을 구분하고, 손상을 조용히 정상 결과로 위장하지 않는다.
- exact Round 3 current authority와 required validation IDs를 일반 pytest 편의를 위해 확장하지 않는다.
- source classification과 full denominator는 Iris repository owner의 승인 없이는 authority가 되지 않으며 unresolved source를 자동 제외하지 않는다.
- 이미 분류된 source도 import/collection 불가능하면 Gate A included denominator에 둘 수 없다. producer 복원 또는 owner-approved exclusion 없이 오류를 무시하지 않는다.
- sealed/historical artifact는 additive reference와 복원 경로를 먼저 만들고, 파괴적 disposition은 별도 owner 승인 뒤에만 수행한다.
- 이미 존재하는 CAS, migration codec, family common module을 우선 사용한다.
- 성능 변경은 before/after evidence와 consumer owner가 없으면 채택하지 않는다.
- ItemDetail fullType-only whole-model cache는 금지하며 InventoryItem-dependent facts와 `sourceItem`은 매 호출 다시 읽는다.
- 예상 byte/time 절감치를 완료 수치로 보고하지 않는다.
- raw UTF-8, Git history rewrite, registry 대분할은 별도 계획과 명시적 승인 없이는 시작하지 않는다.
- unrelated dirty worktree 변경을 수정하거나 되돌리지 않는다.
- 문서의 PASS 주장은 AGENTS.md가 지정한 정확한 관련 명령의 exit code 0이 있을 때만 쓴다. 도구 부재는 PASS가 아니라 BLOCKED다.
- Heavy closeout은 `validated`, `out_of_scope`, `unvalidated_but_in_scope`와 non-claims를 반드시 포함한다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

여기서 `complete`는 모든 제안이 코드 변경으로 채택되었다는 뜻이 아니다. 다음 조건을 모두 충족한 상태를 뜻한다.

- Gate A의 owner-approved source classification, current/full denominator collection과 exact current route가 모두 exit code 0이다.
- Gate B의 same-generation/index↔chunk↔line-count invariant와 normal miss/fault 분리가 mandatory focused command에서 exit code 0이다.
- mandatory optimization의 각 항목이 구현되었거나, 안전 gate에서 제외된 정확한 이유가 기록되었다.
- `baseline-0`과 `baseline-1`이 서로 다른 정확한 generation identity로 봉인되었다.
- measurement-gated 항목마다 사전 고정된 metric/denominator/threshold와 `adopted` 또는 근거 있는 `no-op` 결정이 있다. PZ-dependent 항목의 `deferred`는 `complete` 조건을 충족하지 않는다.
- adopted 항목은 current authority route, focused contracts, Lua syntax, semantic parity를 통과했다.
- CAS disposition이 있었다면 restore/byte parity, consumer validation, dangling-reference 0 및 최종 byte census가 있다.
- CAS safe candidate가 없거나 순절감 1 MiB 미만이면 검증된 `no-op` receipt가 있다. 1 MiB 이상 safe candidate가 있으면 disposition approval과 terminal validation까지 끝나야 한다.
- runtime behavior를 채택한 항목은 cold/warm Browser와 Tooltip PZ 결과가 기록되었다.
- §7의 closeout ceiling에서 `unvalidated_but_in_scope`는 exhaustive third-party mod/direct-consumer sweep으로 명시적으로 한정된다. known consumer, representative external/mod fixtures, current/modified code, PZ-required runtime 및 mandatory/adopted surface의 다른 미검증 항목은 비어 있어야 한다.
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`는 실제 변경된 계약만 additive하게 반영한다.

### Closeout State Mapping

| Condition | Overall state |
|---|---|
| 위 `complete` 조건 전부 충족 | `complete`, 반드시 validation ceiling 및 non-claims와 함께 선언 |
| 일부 Change 완료, PZ-dependent candidate가 runtime 부재로 `deferred`, 또는 1 MiB 이상 safe CAS candidate가 approval 부재 | `partial` |
| 코드 변경은 끝났지만 exact current/focused/Lua/PZ 등 요구 검증을 실행하지 못함 | `implemented_only` |
| source classification owner approval, executable validation path, dependency 또는 CAS authority가 없어 더 진행할 수 없음 | `blocked` |

configured full `all` execution이 historical/diagnostic failure만 내고 mandatory collection equality, exact current route, modified-source tests가 모두 통과하면 scoped `complete`는 가능하다. 이때 그 실패는 `out_of_scope`로 개별 매핑하고 `configured full-suite PASS`를 non-claim으로 명시한다. 반대로 current/modified/mandatory-invariant failure가 있으면 `unvalidated_but_in_scope`이므로 `complete`는 불가능하다.

모든 third-party mod/direct consumer의 exhaustive sweep은 Change 2 영향 안의 `unvalidated_but_in_scope`로 남을 수 있다. 이 단일 bounded ceiling은 representative external/mod protocol과 known consumers가 검증되고 universal compatibility를 non-claim으로 명시한 경우에만 scoped `complete`와 양립한다. 새 known consumer failure, 미검증 representative path 또는 보편 호환성 주장은 이 예외에 포함되지 않는다.

Project Zomboid 실행 환경이 없으면 PZ-dependent Change 6C/7을 `no-op`으로 추정하지 않는다. 해당 candidate는 `deferred`, runtime surface는 `unvalidated_but_in_scope`, 전체 상태는 최소 `partial`이다. 자동 검증을 통과하지 못한 항목을 `complete`, PASS, behavior-preserving 또는 universal third-party compatible로 표기하지 않는다.

모든 closeout은 최소한 다음 non-claims를 명시한다.

- deployment 또는 Workshop release-ready를 선언하지 않는다.
- 모든 third-party mod, multiplayer, long-session 호환성을 선언하지 않는다.
- 신뢰 가능한 heap 측정이 없으면 heap 절감을 선언하지 않는다.
- advisory `all` command가 exit 0이 아니면 configured full-suite PASS를 선언하지 않는다.
