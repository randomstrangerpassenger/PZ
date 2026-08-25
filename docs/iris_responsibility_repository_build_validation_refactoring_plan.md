# Iris 책임 경계·빌드·런타임 구조 리팩터링 Implementation Plan

상태: `approved plan / change_1_through_change_10_authorized`

기준 브랜치/리비전: `main` / `d234723ae92ce83313da0ce83442389e6c4afac8`

작성 기준일: 2026-08-25

상위 근거: `docs/Philosophy.md`, `docs/EXECUTION_CONTRACT.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, 사용자 제공 종합 Roadmap 및 종합 검토안

## 1. Objective

Iris의 현재 제품 경로를 `사실 생성 도구 -> 검증된 현재 데이터 -> 읽기 전용 Lua 런타임 -> Browser/Wiki/Tooltip 표시`로 다시 한정하고, 전역 동작 패치와 평면형 current 빌드 구조를 책임이 명확한 package/module 경계로 교체한다.

이 계획은 단순한 디렉터리 정리나 문서 최신화가 아니다. 다음 구조적 결과를 실제로 만든다.

1. `Iris/`는 게임 상태나 전역 UI 동작을 바꾸지 않는 정보 표시 모듈로 돌아간다.
2. current 빌드 entrypoint, producer, consumer와 validation binding을 명시하고 historical 경로가 current authority로 해석되지 않게 한다. historical payload의 물리적 이동·외부화·삭제는 수행하지 않는다.
3. Description v2의 평면형 Python 스크립트 집합을 설치 가능한 패키지, 명시적 도메인 모듈, 얇은 CLI로 재구성한다.
4. Layer 3 배포 패키지는 정확히 하나의 current generation만 포함한다. source predecessor는 이 계획에서 이동·수정·삭제하지 않는다.
5. Browser, Detail, Wiki의 사실 읽기·모델 조립·표시 책임을 분리하면서 authority manifest에 등록된 공개 진입점은 얇은 facade로 유지하고, manifest 밖이거나 명시적으로 퇴역 승인된 legacy facade만 제거한다.
6. 검증의 authoritative selection rule과 각 failure meaning을 보존하고, 리팩터링으로 경로가 바뀐 source와 contract binding만 successor 경로로 재결속한다. 기존 테스트 family 병합이나 runner 공통화는 수행하지 않는다.

완료 기준은 “기존 current 경로를 그대로 둔 채 새 구조를 추가함”이 아니다. 새 구조가 current authority가 되고 R1이 도입한 temporary migration wrapper와 obsolete current binding은 최종 wave에서 제거되어야 한다. historical payload와 이미 non-current인 predecessor의 물리 삭제는 이 계획의 완료 조건이 아니다.

---

## 2. Scope

이 계획은 다음 실행 범위를 포함한다.

* Iris가 소유한 두 전역 동작 패치와 설치 경로의 무대체 완전 삭제
* current entrypoint/producer/consumer/validation owner 확인과 current authority manifest 재작성
* `Iris/build/description/v2/tools/build`의 Python 패키지화와 도메인별 분해
* 현재 사용 중인 대형 Python 모듈의 실제 책임 분해
* right-click 파이프라인을 v2.4 current-only 구조로 축소
* Layer 3 package projection을 current generation 단일 구조로 축소하되 source predecessor는 그대로 보존
* BrowserData와 Detail ViewModel의 책임 분해
* Browser/Wiki의 공통 사실·표현 모델 정렬과 Wiki의 nil 의미 정확성 수정
* legacy `IrisData`의 Iris 내부 사용 제거와 listed supported thin compatibility adapter 보존, 이를 구현하는 unlisted internal loader의 별도 disposition, supported manifest 밖 Recipe/Moveables/Fixing 인덱스의 deprecated `build()` 정리
* 기존 검증 taxonomy/required manifest를 새 경로로 이관하고 동일 의미 계약을 재봉인
* 관련 architecture/decision/roadmap/entrypoint/inventory 문서의 current-only 갱신

### Explicitly Out Of Scope

* Iris의 사실 내용, 분류 체계, 번역 문구, 한국어 자연화 결과 자체를 새로 설계하는 작업
* 아이템 추천, 효율 판단, 상황 추론, 플레이 조언 등 `Philosophy.md`가 금지하는 기능 추가
* Recipe evidence와 Right-click evidence의 의미론적 병합
* Pulse의 이벤트 버스·API·저장소 책임 변경
* Nerve를 포함한 다른 spoke 모듈의 변경과, 삭제되는 전역 동작 기능의 다른 모듈 재구현
* Git 전체 이력 재작성, 이미 배포된 release tag 변경, 과거 commit의 삭제
* RTC/freeze/release/publish/deploy 승인 자체. 이 계획은 해당 절차에 들어갈 수 있는 current subject를 만든다.
* 모든 외부 모드와의 호환성 전수 조사
* 저장소 전체 언어/빌드 시스템을 하나로 통합하는 작업
* staging/evidence/historical artifact의 외부화·archive·복원·물리 삭제와 저장소 byte 경량화
* IAR/vNext, consumer가 0인 predecessor, inactive Layer 3 source generation과 legacy fixed chunk의 물리 삭제
* `Iris/output`과 `Iris/media`의 byte-identical 생성물 및 그 밖의 중복 payload 제거
* 범용 `PhaseRunner`, typed execution result, 구조화 logging, duplicate helper detector와 build/validation orchestration 공통화
* validation runner/result plugin의 통합 또는 테스트 family·identity의 추가 병합
* AI readpoint, manifest/receipt 탐색 경로와 context surface 최적화
* Wiki layout, panel 크기, scroll과 탐색 흐름 개선

---

## 3. Non-Goals

* 기존 검증 통합 작업을 다시 수행하지 않는다. `round3_test_taxonomy.json`의 current+ok selection, full-gate의 additional source/node, required manifest와 standalone 4개 command로 구성되는 authoritative selection rule을 기준선으로 사용한다. `current pytest 192 + standalone 4 = 196`은 기준 revision에서 파생된 관측값이지 고정 authority가 아니다.
* 이미 `FULL_RETIREMENT`로 결정되고 active consumer가 0인 IAR를 개선 가능한 현행 subsystem처럼 리팩터링하거나 이 계획에서 물리 삭제하지 않는다. current authority/entrypoint로 승격하지 않고 후속 경량화의 입력 상태로 그대로 보존한다.
* 대형 파일을 임의의 줄 수로 나누는 것을 목표로 하지 않는다. 각 새 모듈은 한 종류의 정책 또는 기계적 책임을 소유해야 한다.
* R1이 도입한 temporary migration adapter는 최종 closeout 전에 제거하되 `phase0_supported_api_manifest.json`이 current supported로 지정한 compatibility adapter는 thin current 구현으로 보존한다. 기존 non-current legacy physical file의 정리는 이 계획에서 수행하지 않는다.
* UI 외형, panel 크기, layout, scroll을 변경하지 않는다. 책임 분리 과정에서 `known`, `unknown`, `not_applicable`과 nil/no-op contract의 의미 정확성만 수정한다.
* 테스트 수 증가를 성공 지표로 삼지 않는다. current 의미 계약, 오류 탐지력, 재현 가능성, 실행 경로의 단일성을 지표로 삼는다.

---

## 4. Assumptions

### 4.1 Constitutional and authority assumptions

* `docs/Philosophy.md`가 Iris의 최상위 설계 권위다. Iris는 읽기 전용 사실 표시 모듈이며, 게임 상태나 전역 동작을 바꾸지 않는다.
* Iris 런타임은 100% Lua다. Python은 오프라인 생성·검증에만 존재한다.
* Iris는 Pulse에만 의존할 수 있고, 다른 spoke를 호출하지 않는다.
* Browser, Wiki, Alt Tooltip은 동일한 검증 사실을 다른 표면에서 보여 줄 수 있지만, Tooltip은 최대 4줄 제한을 유지한다.
* Recipe와 Right-click은 독립되고 동등한 사실 관점이다. 두 경로의 기계적 인프라 공통화도 이 계획에서는 수행하지 않는다.
* `docs/ARCHITECTURE.md`와 `docs/DECISIONS.md`가 기록한 IAR `FULL_RETIREMENT` 및 active consumer 0 판정은 유효하다.

### 4.2 Inspected repository baseline

다음 수치는 2026-08-25 기준의 tracked/working-tree 실측값이다. 실행 시작 시 동일 측정 스크립트로 다시 캡처하고 차이가 있으면 기준 manifest를 먼저 갱신한다.

| 대상 | 관측값 | 계획상 의미 |
| --- | ---: | --- |
| `description/v2/tools/build` physical | 511 Python files / 245,689 lines | 평면형 스크립트 집합을 패키지와 CLI로 교체한다. |
| `description/v2/tools/build` tracked | 264 Python files / 159,261 lines | current authority를 새 package로 이동한다. 기존 non-current physical 경로 제거는 후속 경량화 범위다. |
| v2 Python+Lua | 707 files / 401,196 lines | 파일 수 자체보다 current consumer와 책임 경계로 생존 여부를 결정한다. |
| `description/v2/tools/build` denominator의 `sys.path` 조작 | tracked 48곳, physical 161곳 | 최종 current package와 successor test source에서는 0이어야 한다. |
| `dvf_3_3_registry_authority_canonical_closure.py` | 13,219 lines | IAR 퇴역 계열이므로 분해하거나 current package로 이관하지 않는다. 물리 삭제는 후속 경량화 범위다. |
| `IrisBrowserData.lua` | 645 lines | projection/lifecycle/metrics/facade를 분리한다. |
| `IrisItemDetailViewModel.lua` | 413 lines | 엔진 사실 읽기와 모델 조립을 분리한다. |
| Layer 3 generation | 4 generations / 약 9.23 MiB | package에는 current 1개만 투영한다. source predecessor 3개는 현재 bounded rollback target이다. |
| legacy Layer 3 fixed chunks | 11 chunks / 약 0.92 MiB | runtime direct reference뿐 아니라 full-gate `package_runtime_mirror` consumer가 있으므로 main closeout에서 삭제하지 않는다. |

### 4.3 Code-informed decisions

* 13,219줄 canonical closure와 `_dvf_3_3_vnext_common.py` 계열은 current taxonomy, required manifest, full gate의 current implementation이 아니다. 이 계열은 R1의 분해·패키지 이관 대상에서 제외하고 물리 상태를 변경하지 않는다.
* `public_text_quality_acceptance.py`, 자연화 실행기 등 current consumer가 있는 대형 모듈은 퇴역시키지 않고 책임별로 분해한다.
* `IrisBrowserData.lua`는 이미 Category/Item/Classification/Query/Variant index로 일부 위임한다. 새 리팩터링은 이 위임을 무시하고 재작성하지 않고, 남아 있는 projection, lifecycle/cache, metrics, public facade만 분리한다.
* Browser와 Wiki는 이미 `IrisItemDetailViewModel.lua`와 `IrisWikiSections.lua`를 공유한다. 새 “공통 모델”을 중복 생성하지 않고 기존 공통점을 fact reader/model assembler/section projection의 명시적 경계로 강화한다.
* `IrisWikiSections.renderReasonSection()`은 broad Wiki render surface에 포함된 public compatibility wrapper이므로 현재의 `nil`/no-op observable contract를 유지한다. 제거할 결함은 `IrisWikiPanel.lua`의 죽은 내부 호출과 nil section을 불필요한 label로 만드는 내부 동작이며, wrapper 자체가 아니다.
* `IrisLayer3DataChunks.lua`와 `IrisLayer3DataChunkIndex.lua`는 current pointer를 사용하는 안정 facade다. 이 facade는 유지한다. inactive generation 및 legacy fixed chunks의 source는 이 계획에서 변경하지 않는다.
* `Iris/tools/package_iris.ps1`의 `media` 재귀 복사는 inactive generation까지 패키징한다. 패키징은 allowlist와 current pointer 기반 복사로 바꿔야 한다.
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json` v8은 taxonomy뿐 아니라 additional source/node, standalone 4개, source disposition, direct dependency, G4/G5 evidence, frozen predecessor bootstrap, package runtime mirror와 `result_plugin`을 소유한다. 경로 이동은 이 계약 재바인딩과 같은 execution unit에서만 허용한다.
* `Iris/build/description/v2/frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json`은 historical implementation이 아니라 SHA-256으로 pin된 current hermetic gate fixture다.
* `full_repository_gate.json`의 `g4_required_paths`와 `evidence_bindings`가 가리키는 staging 및 `_docs/round3` 파일은 current required evidence다. 이 계획에서는 해당 payload를 이동·외부화·삭제하지 않는다.
* `phase0_supported_api_manifest.json`은 `IrisData`, `IrisBrowserData.getGroupVariants`/`build` 및 broad Wiki render facade를 supported compatibility로 분류한다. `StaticData.getLegacyIrisData`는 그 manifest에 직접 등록되지 않은 internal compatibility loader이며, listed `IrisData` 동작을 운반하는 구현 세부로 별도 분류한다. 이번 계획은 이를 public supported-set으로 승격하지 않고 내부 consumer를 0으로 만든 뒤 thin internal loader로 유지하며, 향후 삭제에는 별도 disposition을 요구한다.

### 4.4 Execution assumptions

* 실행은 wave별 독립 commit으로 수행하며 경로 이동과 authority/validation binding 변경을 같은 execution unit에 둔다.
* R1 범위 밖 historical, evidence, generated payload는 이름이나 consumer 수만으로 이동·삭제하지 않는다.
* current baseline이 실행 시작 시 실패하면 리팩터링으로 실패를 숨기지 않는다. baseline 결과를 blocker로 기록하고 실패 원인을 별도 수정한 뒤 wave를 시작한다.

### 4.5 Review conflict resolutions

* Global compatibility patch: 사용자 지시에 따라 두 patch는 다른 모듈로 이전하지 않고 삭제한다. 다만 구현보다 먼저 두 patch가 막던 defect와 Philosophy 충돌, non-interference claim, external-mod validation ceiling을 successor decision으로 채택한다.
* `IrisData` / legacy facade: current authority의 `public compatibility preserved` 결정을 유지한다. Iris 내부 consumer는 focused API로 이관하고 listed `IrisData` global/module과 `IrisBrowserData.getGroupVariants`의 supported observable shape는 thin adapter로 보존한다. unlisted `StaticData.getLegacyIrisData`는 supported-set을 확장하지 않는 internal loader로만 유지하고 별도 internal contract test를 둔다.
* Layer 3: package current-generation-only는 main closeout의 mandatory condition이다. inactive source generation과 legacy fixed chunks의 물리 삭제는 이 계획에서 열지 않는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/Compat/IrisBulletReloadCompat.lua`
* `Iris/media/lua/client/Iris/Compat/IrisContextMenuTextureCompat.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/` — projection/lifecycle/metrics 모듈
* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
* `Iris/media/lua/client/Iris/UI/Detail/` — fact reader/model assembler 모듈
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
* `Iris/media/lua/client/Iris/Data/IrisData.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisMoveablesIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisFixingIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
* `Iris/build/rightclick_evidence_pipeline.py`
* `Iris/build/description/v2/tools/build/`
* `Iris/tooling/pyproject.toml`
* `Iris/tooling/uv.lock`
* `Iris/tooling/src/iris_tooling/`
* `Iris/tooling/tests/`
* `Iris/validation/clean_checkout/`

### Docs

* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `docs/ARCHITECTURE.md`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* 이 계획의 wave별 execution record와 closeout report

### Config

* `Iris/tooling/pyproject.toml`
* `Iris/tooling/uv.lock`
* Python test discovery/import 설정
* current build/authority manifest schema
* package allowlist/current-generation contract
* 검증 taxonomy와 required validation manifest의 경로 binding
* `pytest.ini`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/clean_checkout/contracts/canonical_gate.json`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json` — launcher가 읽는 stable current locator
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_<wave>_v1.json` — wave별 append-only immutable environment authority

### Generated Artifacts

* `Iris/build/description/v2/frozen_predecessor_inputs/` — current hermetic gate fixture이며 변경하지 않음
* `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/` — package projection 입력이며 source는 변경하지 않음
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/` — package projection 입력이며 source는 변경하지 않음
* `Iris/media/lua/client/Iris/Data/Layer3English/` — package projection 입력이며 source는 변경하지 않음
* repository-external package 및 validation run output

---

## 6. Planned Changes

### Change 1 — current authority snapshot, successor decision, implementation checkpoint 선행 봉인

Purpose:

리팩터링 전후 비교 대상을 하나로 만들고, full-gate와 compatibility successor decision을 implementation보다 먼저 채택한다.

Files:

* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/current_build_manifest.json` — 신규
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/clean_checkout/contracts/canonical_gate.json`
* `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`
* `docs/DECISIONS.md`
* `Iris/_docs/refactor/responsibility_repository_refactor/` — baseline/decision/evidence 기록
* `Iris/_docs/refactor/responsibility_repository_refactor/s0_baseline_adoption.json`

Implementation Notes:

* current entrypoint, producer, consumer, package input과 validation binding을 기계적으로 수집한다.
* `ENTRYPOINTS.md`는 날짜별 누적 로그가 아니라 현재 명령만 설명하는 문서로 다시 쓴다. 이전 내용은 역사 appendix 또는 Git 이력으로 이동한다.
* `current_build_manifest.json`은 각 current entrypoint에 대해 `owner`, `domain`, `module`, `inputs`, `outputs`, `consumers`, `validation_contracts`, `runtime_shipping`, `historical_replacement`를 기록한다.
* current validation authority는 `full_repository_gate.json` v8의 selection rule, taxonomy의 `current + ok`, additional source/node, required manifest, standalone command list다. 기준 revision의 `192 + 4 = 196`, taxonomy 102행, required 61개는 baseline receipt에 파생 측정치로 기록하되 고정 target으로 승격하지 않는다.
* `full_repository_gate.json`이 가진 source disposition, direct dependency, G4/G5 evidence, frozen predecessor fixture, package runtime mirror와 result plugin binding을 baseline inventory에 모두 포함한다.
* 이미 완료된 temporary validation retirement와 regular validation consolidation은 재개하지 않는다. 이 계획은 그 결과를 소비한다.
* `docs/DECISIONS.md`에 implementation 전 successor decision을 추가한다. 이 decision은 (a) 두 global patch의 무대체 삭제, 알려진 방어 defect와 external compatibility ceiling, (b) listed supported `IrisData`/Browser/Wiki facade 보존과 unlisted `StaticData.getLegacyIrisData`의 internal-loader disposition, (c) Layer 3 package-only pruning과 source predecessor hold를 명시한다. historical payload와 sealed artifact의 기존 보존·삭제 authority는 supersede하지 않는다.
* W0 결과는 항상 `s0_baseline_adoption.json`으로 canonicalize한다. expected baseline, actual W0 commit/tree, relationship, Run A/B orchestration receipt hash, comparator receipt hash를 기록한다. 두 commit이 같으면 `relationship = expected_baseline`, `delta = no_delta`로 닫고, 다르면 merge-base, changed-path inventory digest, 차이 사유와 W1 owner adoption을 추가하기 전에는 implementation checkpoint를 열지 않는다.
* current migration map은 변경 대상마다 predecessor path, successor owner/path, affected consumer, validation binding, supported compatibility disposition을 기록한다. historical payload와 R1 범위 밖 file disposition은 작성하지 않는다.
* migration map과 successor decision을 별도 checkpoint commit으로 만들고 재검토·채택한 뒤에만 Change 2 이후로 진행한다. 실행 code와 path migration diff가 이 checkpoint commit에 섞이면 안 된다.
* 문서 상태는 review adoption evidence가 생기기 전까지 `scope_reduced_pending_re_review`를 유지한다. 이번 검토가 채택되면 W1 implementation checkpoint 또는 후속 authority-only commit이 이 계획의 path/hash, owner approval과 승인 대상을 결속하고, 프로젝트에서 이미 쓰는 `approved plan` 및 `change_<n>_authorized` 계열 표현으로 실행 승인을 기록한 뒤 header를 그 기존 승인 상태 표현에 맞춰 갱신한다. `approved_for_execution`을 새 formal closeout state나 governance taxonomy로 추가하지 않는다.

Validation:

* manifest의 모든 current 경로가 존재하고 모든 current entrypoint가 정확히 한 owner를 가진다.
* taxonomy/required/full-gate selection 중 orphan, duplicate, unclassified source가 0이다.
* `full_repository_gate.json`의 모든 required path, frozen predecessor manifest hash, G4/G5 evidence hash, package mirror source가 존재하고 baseline contract와 일치한다.
* current migration map의 모든 대상이 predecessor owner/path와 successor owner/path를 가지며 orphan current consumer가 0일 때만 implementation checkpoint를 PASS한다.
* section 7의 exact S0 full-gate Run A/B와 comparator가 exit `0`이어야 한다.
* `s0_baseline_adoption.json`이 실제 S0 receipt chain과 일치하고, baseline delta가 있으면 W1 owner adoption이 존재한다.
* 동일 clean checkout에서 snapshot 생성 2회의 canonical JSON과 SHA-256이 동일하다.

---

### Change 2 — Iris의 전역 동작 패치 완전 삭제

Purpose:

Iris를 정보 표시 전용 spoke로 복구하고, 다른 시스템의 동작을 변경하는 monkey patch와 그 설치 경로를 대체 구현 없이 삭제한다.

Files:

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/Compat/IrisBulletReloadCompat.lua`
* `Iris/media/lua/client/Iris/Compat/IrisContextMenuTextureCompat.lua`
* 관련 Iris Lua 테스트

Implementation Notes:

* Change 1 successor decision이 adopted 상태인지 먼저 검증한 뒤 `IrisMain.lua`의 install 호출과 두 Iris `Compat` 구현 파일을 같은 wave에서 삭제한다.
* successor decision은 bullet patch가 reload menu를 전면 교체했다는 사실과 texture patch가 null/invalid `tickTexture`의 `getWidthOrig()` 호출을 방어했다는 defect를 명시한다.
* `ISInventoryPaneContextMenu.doReloadMenuForBullets` 교체와 `ISContextMenu.render` wrapper 동작은 현행 기능으로 보존하지 않는다. Iris는 삭제 이후 해당 동작의 정확성이나 외부 모드 조합의 호환성을 주장하지 않는다.
* 삭제되는 코드를 Nerve 또는 다른 모듈로 이동·복제·재구현하지 않는다.
* compat 전용 설정, lifecycle hook, diagnostic, source-shape test가 남아 있으면 함께 제거한다.
* Iris boot 전후로 두 전역 함수의 identity가 바뀌지 않는다는 부재 계약을 동작 테스트로 추가한다.
* null/invalid `tickTexture` fixture에서는 Iris가 sanitize하거나 render를 wrap하지 않고 기존 renderer의 결과/예외를 그대로 노출한다는 non-interference를 검사한다. 이를 외부 compatibility 보존 증거로 해석하지 않는다.

Validation:

* Iris 전체에서 두 전역 함수의 대입/wrapping/installer 참조가 0이다.
* Iris boot가 두 compat 모듈 없이 성공한다.
* 저장소 전체에서 삭제된 patch의 동등 구현과 install hook이 0이다.
* Iris boot 전후 `doReloadMenuForBullets`와 `ISContextMenu.render`가 동일한 원본 함수로 유지된다.
* bounded in-game probe에서 실제 blocker regression이 발견되면 closeout state를 `blocked`, blocking reason을 `PATCH_REGRESSION_PENDING_SEPARATE_DECISION`으로 기록한다. patch 복원이나 타 모듈 이전은 자동 rollback이 아니다.

---

### Change 3 — Description v2 Python을 설치 가능한 도구 패키지로 재구성

Purpose:

수백 개의 root-direct script, `sys.path` 수정, 위치 의존 import를 제거하고 도메인 경계와 실행 API를 명확히 한다.

Files:

* `Iris/tooling/pyproject.toml`
* `Iris/tooling/uv.lock`
* `Iris/tooling/src/iris_tooling/build/`
* `Iris/tooling/src/iris_tooling/domains/classification/`
* `Iris/tooling/src/iris_tooling/domains/rightclick/`
* `Iris/tooling/src/iris_tooling/domains/layer3/`
* `Iris/tooling/src/iris_tooling/domains/layer4/`
* `Iris/tooling/src/iris_tooling/domains/public_text/`
* `Iris/tooling/src/iris_tooling/cli/`
* `Iris/tooling/tests/`
* `Iris/validation/clean_checkout/write_environment_receipt.py`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_<wave>_v1.json`
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1`
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`
* `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/tests/test_repository_runtime_lightweighting_command_wrapper.py`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* `Iris/build/description/v2/tests/artifact_lifecycle_executor_support.py`
* `Iris/build/description/v2/tools/build/`
* 이동되는 source/test를 참조하는 `full_repository_gate.json`, taxonomy, required manifest, `pytest.ini`

Implementation Notes:

* `src` layout과 명시적 package metadata를 도입한다. 모든 current command는 `python -m iris_tooling...` 또는 `[project.scripts]` entrypoint로 실행한다.
* dependency와 build backend를 `Iris/tooling/uv.lock`에 봉인한다. package install/project selection의 exact command는 section 7의 `uv sync --project ... --locked --no-editable`이다.
* 환경 authority는 하나의 조기 terminal receipt가 아니라 wave별 append-only record와 stable locator로 운영한다. `responsibility_refactor_environment_<wave>_v1.json`은 wheel hash, implementation commit/tree, `src/iris_tooling` tree hash, `pyproject.toml`/`uv.lock` blob·hash, interpreter, installed file manifest와 external receipt를 봉인하고, `responsibility_refactor_environment_current.json`은 그중 현재 record의 repo-relative path/hash만 가리킨다.
* `write_environment_receipt.py`는 clean-checkout validation domain의 create-new receipt/record writer만 소유한다. current environment authority resolution, schema/hash 검증, wheel/source/project/lock/installed-manifest 결속과 stale-record rejection의 기존 owner는 `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`에 유지한다. 다른 runner의 공통 인프라로 승격하지 않는다.
* W3는 현행 predecessor `phase0_ratification_attempt_0002.json`을 current environment authority로 읽는 모든 구현·test consumer를 file-by-file census한다. 최소 전환 집합은 위 Files 목록의 세 PowerShell launcher, 두 clean-checkout Python runner/validator, 두 test, residual artifact lifecycle executor와 artifact-lifecycle test support다. W3의 같은 execution unit에서 모두 stable current locator로 전환하고, current implementation/test의 predecessor literal reference를 0으로 만든다.
* predecessor literal은 sealed `phase0_ratification_attempt_0003.json`, historical integration ledger/receipt처럼 provenance chain을 설명하는 exact allowlist에서만 남길 수 있다. allowlist row마다 path, field, historical reason을 기록하며 current environment resolution에는 사용하지 않는다. 단순 repository-wide 문자열 0이 아니라 `current consumer == 0`, `approved historical reference == allowlist와 정확히 일치`를 검증한다.
* W3부터 W5까지 `Iris/tooling/src`, `pyproject.toml` 또는 `uv.lock`을 바꾸는 각 wave는 (1) package source가 동결된 implementation subcommit, (2) 그 exact subject에서 deterministic wheel build, (3) create-new external environment/receipt, (4) immutable wave authority record 추가, (5) stable locator만 갱신하는 authority-only terminal subcommit 순서를 따른다. 마지막 subcommit에는 package source/lock 변경을 금지한다. authority subcommit은 implementation commit/tree와 locator-only delta를 함께 기록해 순환 결속을 피한다.
* W6-W9는 `Iris/tooling/src/iris_tooling`, `pyproject.toml`, `uv.lock`의 대응 blob이 직전 current environment record와 동일하면 새 environment를 만들지 않고 그 record/receipt를 재사용한다. 재사용 시 record의 implementation commit이 해당 wave exact subject의 조상인지, `src/iris_tooling` tree와 project/lock blob이 byte-identical인지, interpreter/installed manifest와 locator hash가 같은지를 기존 clean-checkout validator가 확인한다. 하나라도 다르거나 W6-W9에서 package source/lock이 바뀌면 해당 wave id로 새 implementation subcommit→wheel→environment→record→locator 절차를 수행해야 하며 stale receipt 사용은 BLOCKED다.
* W10은 terminal implementation subject에서 새 wheel과 `terminal` environment receipt를 다시 만들고 terminal immutable record와 stable locator를 authority-only closeout subcommit에서 갱신한다. terminal Run A/B는 이 terminal receipt만 사용한다. W3 receipt를 W4-W5 또는 W10 source에 재사용하지 않는다.
* repository root와 data root는 호출 위치나 `Path(__file__).parents[n]`로 추측하지 않고 CLI 인자 또는 하나의 repository context object로 받는다.
* current module 안의 `sys.path.insert/append`를 모두 제거한다. test도 package install/import를 사용한다.
* root `pytest.ini`의 `pythonpath = . Iris/build`는 명시적으로 disposition한다. installed-package 전환 후 `Iris/build` 주입을 제거하고, repository validation namespace 때문에 root 주입이 필요하다는 동작 증거가 없으면 `.`도 제거한다. 예외가 필요하면 exact consumer와 만료 조건을 authority manifest에 기록하고 `PYTHONPATH`를 비운 clean subject test로 package import가 주입에 의존하지 않음을 확인한다.
* 다음 의존 방향을 강제한다: `cli -> domain orchestration -> domain services`. 범용 core mechanics 계층은 이 계획에서 새로 만들지 않는다.
* 각 도메인은 `inputs`, `normalize`, `evaluate`, `emit`, `validate`를 필요한 만큼만 소유하고 다른 도메인의 내부 모듈을 import하지 않는다.
* W3가 `Iris/tooling/tests/`의 생성·이관을 소유한다. 새 package test source는 생성 또는 이동과 같은 execution unit에서 `full_repository_gate.json.source_disposition_policy`의 정확히 한 역할에 분류한다: current required는 `explicit_current_required_sources`, hermetic fixture는 `hermetic_test_fixture_sources`, historical optional은 `explicit_historical_optional_sources` 또는 명시된 `historical_optional_rule`에 결속한다. 같은 execution unit에서 taxonomy, required manifest와 `pytest.ini` binding도 successor path로 갱신하며, 누락·중복·모호한 분류는 `unclassified_source_policy: fail`에 따라 BLOCKED다.
* current consumer graph에 포함된 구현만 package module로 이관한다. 여러 기존 command를 하나의 범용 command로 병합하거나 비current script를 물리 삭제하는 작업은 수행하지 않는다.
* legacy script 경로의 transition wrapper는 한 wave 동안만 허용한다. wrapper는 경고와 새 command 위임 외 로직을 갖지 않으며 final migration wave에서 0개가 된다.
* `Iris/build/description/v2/tools/build`의 기존 physical 파일은 이 계획에서 일괄 삭제하지 않는다. 다만 final current manifest, official entrypoint와 current import graph는 새 package implementation만 가리켜야 하며 R1이 도입한 temporary wrapper는 제거한다.
* source/test/CLI 경로를 옮기는 commit은 `full_repository_gate.json`의 required source, direct dependency, G4 path, compiler identity, taxonomy/required/pytest binding을 같은 execution unit에서 successor path로 바꾼다. predecessor path를 먼저 삭제하는 commit은 금지한다.

Validation:

* clean environment에서 package install 후 모든 current CLI가 repository cwd와 임의 cwd 양쪽에서 동일하게 실행된다.
* `Iris/tooling/src/iris_tooling/**`와 successor full-gate current test source의 `sys.path.insert/append` 조작이 0이다. baseline의 tracked 48건은 `tools/build` denominator였음을 별도 기록한다.
* `Iris/tooling/src/iris_tooling/**` current module의 `parents[2]`식 repository root 추측이 0이다.
* old/new dual-run 기간에 canonical output과 semantic report가 일치하고, wrapper 제거 후 old path reference가 0이다.
* import graph 검사에서 shared infrastructure의 domain policy import와 domain 간 internal implementation import가 모두 0이고, `Iris/tooling/src/iris_tooling/core/` 같은 새 범용 core 계층이 생성되지 않았다.
* `Iris/tooling/tests/**/*.py`의 모든 source가 current required, hermetic fixture, historical optional 중 정확히 한 disposition을 가지며 unclassified·duplicate·ambiguous source가 0이다. current required test는 full-gate selection/taxonomy/required binding에 포함되고, fixture와 historical optional source는 current denominator에 잘못 편입되지 않는다.
* wave record의 wheel, `src/iris_tooling` tree, project/lock blob과 installed manifest가 receipt 및 검증 대상 subject의 대응 blob과 byte-for-byte 일치하고 stable locator가 해당 record 하나만 가리킨다. record의 implementation commit/tree는 authority-only record/locator subcommit의 부모 구현 subject이며 검증 대상 wave subject의 조상이어야 한다. package source 변경 후 stale wave authority를 current로 사용하는 negative fixture는 실패한다.

---

### Change 4 — current 대형 Python 모듈의 책임 분해

Purpose:

실제 current 품질 경로의 대형 모듈만 책임에 따라 분해하고, 비current IAR/vNext 계열은 읽거나 물리 변경하지 않는다.

Files:

* `Iris/build/description/v2/tools/build/public_text_quality_acceptance.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py`
* 그 밖의 current 2,000줄 이상 모듈

Implementation Notes:

* current 2,000줄 이상 모듈은 consumer와 responsibility map을 작성하고 다음 기준으로 분리한다: parsing, normalization, rule evaluation, aggregation, diagnostics, report rendering, CLI.
* `public_text_quality_acceptance.py`는 reusable evaluator library와 CLI/report adapter로 분리한다. 품질 rule은 pure function으로 만들고 입력 source나 파일 쓰기를 직접 소유하지 않게 한다.
* 자연화 runner는 candidate selection, transformation orchestration, acceptance evaluation, output emission을 분리한다.
* 분해 후 생긴 공통 함수가 domain policy를 내포하면 `core`로 올리지 않고 해당 domain에 둔다.
* current consumer가 없는 파일은 새 package로 이관하거나 분해하지 않는다. 물리 존속 판정은 후속 경량화에 맡긴다.

Validation:

* current 대형 모듈 분해 전후 golden input에 대한 semantic result, issue code, severity, canonical output hash가 일치한다.
* 새 current module의 public API가 domain contract test로 직접 검증된다.
* IAR/vNext와 frozen predecessor 파일의 tracked path, Git blob과 SHA-256이 기준선과 동일하다.

---

### Change 5 — Right-click v2.4 current-only 파이프라인으로 축소

Purpose:

하나의 1,300줄 파이프라인 안에 공존하는 v2/v2.2/v2.3/v2.4 모드와 전역 flag를 제거하고, 현행 v2.4만 current package에 남긴다.

Files:

* `Iris/build/rightclick_evidence_pipeline.py`
* `Iris/tooling/src/iris_tooling/domains/rightclick/`
* `Iris/test/test_rightclick_pipeline.py`
* right-click current fixtures/manifest

Implementation Notes:

* v2.4 input schema, normalization, evidence evaluation, report emission, CLI를 새 right-click domain package로 이동한다.
* 새 current CLI는 v2/v2.2/v2.3 mode와 flag를 포함하지 않는다. 기존 predecessor 파일과 mode 구현은 이 계획에서 이동·수정·삭제하지 않고 current manifest와 official consumer에서만 제외한다.
* 기존 global mode state를 immutable command configuration으로 교체한다.
* 테스트의 `sys.path` 수정과 `Iris/evidence/rightclick` 위치 의존을 제거하고 설치된 package와 explicit fixture root를 사용한다.
* Recipe와 의미 규칙을 공유하지 않는다. 이 계획에서는 right-click과 Recipe의 기계적 helper도 새 공통 계층으로 합치지 않는다.
* old `rightclick_evidence_pipeline.py`는 physical historical predecessor로 그대로 유지하고 migration wrapper나 current entrypoint로 사용하지 않는다. 물리 삭제는 후속 경량화에서 판정한다.
* right-click test/entrypoint 이동 commit에서 full gate의 additional node 9개와 standalone `legacy_rightclick_determinism` command path를 successor로 함께 재바인딩한다.

Validation:

* current CLI의 지원 schema/version이 v2.4 하나뿐이다.
* v2.4 golden fixture의 normalized evidence, issue set, canonical output hash가 전후 동일하다.
* v2/v2.2/v2.3 option을 전달하면 묵시적 fallback 없이 명확히 실패한다.
* full gate의 right-click 9개 current node가 새 package 경로에서 통과한다.

---

### Change 6 — Layer 3 current-only package 강제

Purpose:

source rollback material을 변경하지 않으면서 배포 package에는 current pointer가 선택한 generation만 포함되게 한다.

Files:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`
* `Iris/tools/package_iris.ps1`
* Layer 3 generation/package validators

Implementation Notes:

* current pointer `dvf33-028a396886eee3ed9bbb6f610c64c8e886ac3e3aab7b8c7381d5d4a48d7145e9`를 실행 시점 manifest와 대조한다. pointer가 바뀌었다면 실행 subject의 새 current id를 사용하되 package에는 하나만 남기는 원칙은 동일하다.
* inactive generation 3개와 legacy fixed `IrisLayer3DataChunks/Chunk001..011.lua`는 main closeout에서 source `media`에 `CURRENT_ROLLBACK_TARGET`/package bootstrap predecessor로 보존한다.
* stable facade와 pointer 파일은 유지한다. consumer가 generation id 경로를 직접 require하지 못하게 한다.
* `package_iris.ps1`의 전체 `media` 재귀 복사를 Layer 3 제외 media allowlist + stable facade/pointer/support files + current pointer-selected generation 복사로 교체한다. source predecessor가 존재해도 package로 복사하지 않는다.
* package validator는 generation 디렉터리 수가 정확히 1인지, id가 pointer/descriptor/runtime identity와 일치하는지, legacy fixed chunk가 없는지 검사한다.
* package staging에서 extra generation을 자동으로 무시하지 않고 실패시킨다. 잘못된 source tree를 숨기지 않는다.
* 같은 commit에서 `full_repository_gate.json.bootstrap.package_runtime_mirror`를 generation-qualified successor source/target으로 재바인딩하고 legacy source/target을 current package input에서 제거한다. source file 삭제와 contract rebinding을 혼동하지 않는다.
* inactive source generation과 legacy fixed chunks는 이 계획에서 이동·수정·삭제하지 않는다. package projection만 current generation 하나로 제한한다.

Validation:

* package의 Layer 3 generation 디렉터리가 정확히 1개이고 legacy fixed chunk 디렉터리가 없다.
* source media는 predecessor를 보존할 수 있다. current pointer, stable facade와 package의 generation id 및 observable lookup 결과가 일치해야 한다.
* package에 extra generation 또는 pointer 불일치를 주입한 negative fixture가 실패한다.
* current lookup golden subset, chunk completeness, descriptor hash, runtime identity 검증이 통과한다.
* full-gate package runtime mirror가 legacy source가 아니라 generation-qualified successor를 materialize하며 required path 누락과 unclassified source가 0이다.
* PowerShell 5.1과 PowerShell 7 사용 가능 환경에서 패키지 결과의 canonical file manifest가 동일하다.

---

### Change 7 — BrowserData를 projection, lifecycle, metrics, facade로 분리

Purpose:

Browser의 데이터 투영, cache 생명주기, instrumentation, public query를 한 파일이 함께 소유하는 상태를 해소한다.

Files:

* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua` — 신규
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserLifecycle.lua` — 신규
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserMetrics.lua` — 신규
* 기존 Browser indexes/query modules
* Browser behavior tests

Implementation Notes:

* `IrisBrowserProjectionBuilder`는 검증된 indexes와 query result를 Browser row/model로 투영한다. engine mutation이나 UI widget 생성을 하지 않는다.
* `IrisBrowserLifecycle`은 build state, candidate cache, reset/invalidation을 소유한다. cache key와 invalidation cause를 명시한다.
* `IrisBrowserMetrics`는 instrumentation과 diagnostic snapshot만 소유하며 query 결과를 바꾸지 않는다.
* `IrisBrowserData`는 기존 supported public query API를 위임하는 얇은 facade로 축소한다. 내부 consumer는 새 모듈을 직접 사용하지만 `phase0_supported_api_manifest.json`에 supported로 등록된 `build()`와 `getGroupVariants()` observable contract는 유지한다.
* CategoryIndex, ItemIndex, ClassificationIndex, Query, VariantIndex의 기존 책임은 중복 구현하지 않는다.
* `getGroupVariants`의 내부 구현은 current index/query로 교체해 legacy loader 의존을 제거하되 public facade의 signature/result shape는 보존한다.
* cache가 없는 상태, 빈 결과, 일부 데이터 누락, reset 후 재조회가 모두 정상적인 explicit state가 되게 한다.

Validation:

* 기존 Browser golden query의 item set, ordering, classification, variant grouping이 동일하다.
* build/reset/rebuild/cache-hit/cache-miss 동작 test가 통과한다.
* metrics on/off가 query 결과에 영향을 주지 않는다.
* `IrisBrowserData.lua`가 projection 규칙, cache storage, metric aggregation을 직접 구현하지 않음을 dependency/responsibility test로 확인한다.
* supported `build()`/`getGroupVariants()`의 predecessor→successor observable contract test가 통과한다.

---

### Change 8 — Detail fact reader와 공통 presentation model 분리

Purpose:

엔진 객체 접근, capability hint, API/Layer 3 조회, interaction 정보, immutable model 조립을 분리하고 Browser/Wiki가 같은 사실과 표시 결정을 사용하게 한다.

Files:

* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
* `Iris/media/lua/client/Iris/UI/Detail/IrisItemFactReader.lua` — 신규
* `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua` — 신규
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
* Browser detail renderer/consumer
* detail/wiki/browser tests

Implementation Notes:

* `IrisItemFactReader`만 PZ engine item 메서드와 안전 호출을 소유한다. 반환값은 `known`, `unknown`, `not_applicable`을 구분하며 실패를 false 사실로 바꾸지 않는다.
* food/weapon/literature/moveable 접근은 capability가 확인된 경우에만 수행한다. 접근 불가를 부정 사실로 추론하지 않는다.
* assembler는 engine facts, Iris API indexes, Layer 3 설명, interaction facts를 immutable detail model로 결합한다.
* `IrisItemDetailViewModel.lua`는 호환 facade로 시작하되 migration 후 이름과 실제 책임을 일치시키고 불필요한 facade를 제거한다.
* Browser와 Wiki는 같은 detail model과 section projection을 사용한다. 표면별 차이는 layout과 interaction에만 둔다.
* raw/percent-scaled 등 unit profile과 field visibility를 공통 presentation policy로 이동해 같은 사실이 표면마다 다르게 해석되지 않게 한다.
* Tooltip은 이 모델의 검증 사실 중 최대 4줄만 선택하며 새로운 추론을 추가하지 않는다.

Validation:

* food/weapon/literature/moveable/unknown item fixture의 fact reader behavior test가 통과한다.
* 누락/예외 engine method가 부정 문구로 표시되지 않고 unknown/silent 정책을 따른다.
* 동일 item에 대한 Browser/Wiki의 field value, unit, visibility semantic snapshot이 일치한다.
* Tooltip 4줄 상한, 무근거 문구 0, recommendation/efficiency 표현 0을 검사한다.

---

### Change 9 — supported compatibility 격리, 비공개 legacy 정리, Wiki nil 의미 수정

Purpose:

supported legacy surface는 thin compatibility boundary로 보존하면서 Iris 내부 의존과 비공개 wrapper를 제거하고, Wiki의 죽은 내부 경로와 nil 의미 오류를 정리한다.

Files:

* `Iris/media/lua/client/Iris/Data/IrisData.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisMoveablesIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisFixingIndex.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
* `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`

Implementation Notes:

* repo 내부와 package/runtime load trace에서 `IrisData` global/legacy loader consumer를 조사한다. 발견된 Iris 내부 consumer는 새 index/model API로 즉시 전환한다.
* `IrisData` global과 `Iris/Data/IrisData` module은 manifest-listed supported compatibility이므로 삭제하지 않는다. 독립 authority payload를 중복 소유하지 않는 thin generated adapter로 재구성하고 table identity, classifications/item-groups shape, missing-key behavior를 보존한다.
* `StaticData.getLegacyIrisData()`는 supported manifest에 직접 등록된 public surface라고 주장하지 않는다. listed `IrisData` adapter를 구현하는 unlisted internal loader로 file-level disposition하고, Iris product consumer를 0으로 만든 뒤 thin implementation detail로 유지한다. 이 계획은 이를 supported-set에 추가하지 않으며 향후 삭제·공개 승격은 별도 authority decision을 요구한다.
* `IrisBrowserVariantIndex`와 `IrisBrowserData.getGroupVariants`는 새 focused index를 내부 source로 사용하되 supported adapter signature/result를 유지한다.
* supported API manifest에 없는 Recipe/Moveables/Fixing의 항상 `true`인 deprecated `build()`는 current consumer를 이관한 뒤 제거한다.
* `IrisWikiPanel`의 `renderReasonSection()` 호출과 nil label 생성은 제거한다. `IrisWikiSections`의 public render wrapper surface는 current supported contract이므로 `renderReasonSection()`은 nil을 반환하는 compatibility no-op으로 유지하고 successor decision 없이 삭제하지 않는다.

Validation:

* Iris 내부 product consumer의 legacy `IrisData` fallback 호출은 0이지만 listed supported global/module adapter와 unlisted thin internal loader는 각자의 disposition에 따라 존재한다.
* `phase0_supported_api_manifest.json`에 실제로 listed된 `IrisData`, `getGroupVariants`, `build`, Wiki render facade의 positive/negative observable contract가 predecessor와 동일하다. `StaticData.getLegacyIrisData()`는 별도 internal contract test로 listed `IrisData` 구현에 필요한 table identity/missing-key behavior만 검증하며 public support claim으로 집계하지 않는다.
* Recipe/Moveables/Fixing의 비공개 deprecated `build()` 호출과 정의가 0이다.
* Wiki의 nil section과 빈 데이터 behavior test가 통과하며 layout, panel 크기와 scroll 동작은 기준선에서 변경되지 않는다.

---

### Change 10 — migration wrapper 제거, terminal gate 재봉인, 문서 closeout

Purpose:

새 구조를 보조 경로가 아닌 유일한 current 경로로 만들고, 임시 호환층과 옛 entrypoint를 남기지 않은 상태에서 전체 계약을 재봉인한다.

Files:

* 모든 temporary migration Python/Lua wrapper. current supported compatibility adapter는 제외한다.
* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/current_build_manifest.json`
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/clean_checkout/contracts/canonical_gate.json`
* `docs/ARCHITECTURE.md`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* refactor closeout report/inventory/diff manifests

Implementation Notes:

* old current build binding/import, old right-click current CLI, unsupported migration facade를 금지 패턴 manifest로 등록한다. historical physical path, IAR/vNext, staging/evidence, tracked duplicate output, inactive Layer 3 source generation과 supported Lua facade는 이 계획의 금지 대상이 아니다.
* migration wrapper는 final gate 전에 모두 삭제한다. `phase0_supported_api_manifest.json`에 등록된 `IrisData`, `IrisBrowserData`, Wiki render wrappers와 Layer 3 stable facade는 얇은 current compatibility surface로 유지한다.
* current authority manifest를 새 package/module/entrypoint 기준으로 재생성한다.
* architecture에는 current build/runtime 책임과 entrypoint를 기록하되 historical 문서·payload를 재정리하지 않는다.
* Change 1에서 선행 채택한 decisions를 final implementation identity와 연결한다. 전역 패치 삭제, package current-generation-only, source predecessor hold, supported compatibility 보존을 사후에 새로 결정하지 않는다.
* roadmap에는 각 wave의 terminal commit과 validation receipt를 연결한다.
* current owner/entrypoint delta, API removal list와 package manifest delta를 closeout report에 기록한다. 저장소 byte 경량화 수치는 이 계획의 성과로 기록하지 않는다.

Validation:

* 금지 패턴/경로 검사 결과가 0이다.
* clean subject에서 terminal full gate Run A와 Run B가 모두 exit 0이고 comparator가 PASS한다.
* package manifest가 current authority manifest와 일치한다.
* authoritative predecessor→successor validation ledger의 unmapped/ambiguous contract가 0이고 derived count는 결과로 기록된다.
* 문서의 current entrypoint를 복사해 실행했을 때 별도 `sys.path`/cwd 보정 없이 성공한다.

---

## 7. Validation Plan

### Automated Validation

#### 7.1 실행 전제와 판정 규칙

* 아래 PowerShell 명령은 저장소 root에서 실행한다. `C:\Users\MW\irf`, `C:\Users\MW\iccv`는 저장소와 서로 포함 관계가 없는 owner-controlled external root다.
* create-new 규칙은 공용 parent 자체가 아니라 각 명령의 versioned leaf root(`s0-*`, `env-*`, `receipts\env-*`, `terminal-*`)에 적용한다. leaf가 이미 존재하면 자동 삭제·재사용하지 않고 BLOCKED로 판정한 뒤 새 versioned leaf를 decision에 기록한다.
* native command마다 `$LASTEXITCODE -eq 0`을 확인한다. 필요한 `git`, `uv`, Python, PowerShell 또는 Lua checker가 없으면 PASS가 아니라 BLOCKED다.
* baseline과 terminal full gate의 authority는 `invoke_receipt_bound_full_gate.ps1`이 실행하는 `full_repository_gate.json`이다. standalone 4개 direct 명령은 command identity와 실패 위치를 확인하는 추가 receipt이며 full gate를 대체하지 않는다.
* wave 중 상위 runner 결과를 재사용하려면 subject commit/tree, contract SHA-256, environment receipt SHA-256, authoritative selection digest, command arguments, result/canonical hash가 모두 일치해야 한다. 하나라도 없거나 다르면 독립 재실행하고, 재실행할 수 없으면 BLOCKED다. 단순 status나 test count만으로 nested result를 재사용하지 않는다.

#### 7.2 S0 baseline exact full gate와 standalone 4개

implementation checkpoint 전에 아래 명령을 그대로 실행한다. S0 subject는 실행 시점 W0의 실제 `HEAD`에 기계 결속한다. `d234723ae92ce83313da0ce83442389e6c4afac8`은 예상 baseline일 뿐 강제 checkout target이 아니며, 실제 W0 HEAD가 다르면 두 commit과 delta reason을 S0 adoption record에 기록하고 W1 전에 authority review를 다시 받는다. 환경은 현재 ratified receipt `C:\Users\MW\iccv\receipts\env-v1\environment_receipt.json`이다.

```powershell
$ErrorActionPreference = 'Stop'
$IrisSourceRepository = (Resolve-Path '.').Path
$IrisExpectedS0Commit = 'd234723ae92ce83313da0ce83442389e6c4afac8'
$IrisS0CommitOutput = git -C $IrisSourceRepository rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'W0 HEAD resolution failed' }
$IrisS0Commit = ($IrisS0CommitOutput -join '').Trim()
$IrisS0BaselineRelationship = if ($IrisS0Commit -eq $IrisExpectedS0Commit) { 'expected_baseline' } else { 'head_delta_requires_w1_authority_review' }
$IrisS0Root = "C:\Users\MW\irf\s0-$($IrisS0Commit.Substring(0, 8))-v1"
$IrisS0Repository = Join-Path $IrisS0Root 'repo'
$IrisS0EnvironmentReceipt = 'C:\Users\MW\iccv\receipts\env-v1\environment_receipt.json'
$IrisS0Python = 'C:\Users\MW\iccv\env-v1\Scripts\python.exe'
$IrisS0Claim = 'iris-responsibility-refactor-s0-v1'

if (Test-Path -LiteralPath $IrisS0Root) { throw "S0 root must be absent: $IrisS0Root" }
New-Item -ItemType Directory -Path $IrisS0Root | Out-Null
git clone --no-hardlinks $IrisSourceRepository $IrisS0Repository
if ($LASTEXITCODE -ne 0) { throw 'S0 clone failed' }
git -C $IrisS0Repository checkout --detach $IrisS0Commit
if ($LASTEXITCODE -ne 0) { throw 'S0 checkout failed' }

$IrisS0Gate = Join-Path $IrisS0Repository 'Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1'
$IrisS0Compare = Join-Path $IrisS0Repository 'Iris\validation\clean_checkout\invoke_deterministic_compare.ps1'
& $IrisS0Gate -RepositoryRoot $IrisS0Repository -Commit $IrisS0Commit -ClaimId $IrisS0Claim -EnvironmentReceipt $IrisS0EnvironmentReceipt -WorkRoot (Join-Path $IrisS0Root 'wa') -ResultRoot (Join-Path $IrisS0Root 'ra') -OrchestrationReceipt (Join-Path $IrisS0Root 'ra\orchestration.json')
if ($LASTEXITCODE -ne 0) { throw 'S0 Run A failed' }
& $IrisS0Gate -RepositoryRoot $IrisS0Repository -Commit $IrisS0Commit -ClaimId $IrisS0Claim -EnvironmentReceipt $IrisS0EnvironmentReceipt -WorkRoot (Join-Path $IrisS0Root 'wb') -ResultRoot (Join-Path $IrisS0Root 'rb') -OrchestrationReceipt (Join-Path $IrisS0Root 'rb\orchestration.json')
if ($LASTEXITCODE -ne 0) { throw 'S0 Run B failed' }
& $IrisS0Compare -RepositoryRoot $IrisS0Repository -Commit $IrisS0Commit -ClaimId $IrisS0Claim -EnvironmentReceipt $IrisS0EnvironmentReceipt -RunAOrchestrationReceipt (Join-Path $IrisS0Root 'ra\orchestration.json') -RunBOrchestrationReceipt (Join-Path $IrisS0Root 'rb\orchestration.json') -AttemptRoot (Join-Path $IrisS0Root 'compare')
if ($LASTEXITCODE -ne 0) { throw 'S0 deterministic comparator failed' }

$IrisStandaloneCommands = @(
    @{ Id = 'legacy_rightclick_determinism'; Path = 'Iris\build\tests\test_determinism_rc.py' },
    @{ Id = 'legacy_recipe_evidence_determinism'; Path = 'Iris\build\tests\test_recipe_evidence.py' },
    @{ Id = 'labelmap_fail_loud_coverage'; Path = 'Iris\build\tests\test_fail_loud_coverage.py' },
    @{ Id = 'require_render_contract'; Path = 'Iris\build\test_require_render.py' }
)
Push-Location $IrisS0Repository
try {
    $IrisStandaloneSeed = Join-Path $IrisS0Repository 'Iris\output'
    foreach ($IrisStandalone in $IrisStandaloneCommands) {
        $IrisStandaloneOutput = Join-Path $IrisS0Root ('standalone-' + $IrisStandalone.Id)
        if (Test-Path -LiteralPath $IrisStandaloneOutput) { throw "standalone output root must be absent: $IrisStandaloneOutput" }
        New-Item -ItemType Directory -Path $IrisStandaloneOutput | Out-Null
        Copy-Item -Path (Join-Path $IrisStandaloneSeed '*') -Destination $IrisStandaloneOutput -Recurse
        $env:IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT = $IrisStandaloneOutput
        & $IrisS0Python -B -s (Join-Path $IrisS0Repository $IrisStandalone.Path)
        if ($LASTEXITCODE -ne 0) { throw "S0 standalone failed: $($IrisStandalone.Id)" }
    }
}
finally {
    Remove-Item Env:IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT -ErrorAction SilentlyContinue
    Pop-Location
}
```

W0 실행 bundle은 actual W0 HEAD, expected baseline, `$IrisS0BaselineRelationship`, authoritative pytest selection digest, additional source 5개, right-click additional node 9개, standalone command 4개, derived collected/passed count와 Run A/B/comparator receipt hash를 기록한다. W1은 이를 `Iris/_docs/refactor/responsibility_repository_refactor/s0_baseline_adoption.json` canonical adoption record로 승격한다. actual과 expected가 같으면 `relationship = expected_baseline`, `delta = no_delta`를 명시한다. 다르면 expected/actual commit·tree, merge-base, changed-path inventory digest, 실행 기준을 actual W0로 채택하는 owner decision을 기록하며 이 record가 adopted되기 전 implementation wave는 BLOCKED다. `$IrisS0BaselineRelationship`을 기존 orchestration receipt가 묵시적으로 보유한다고 가정하지 않는다. `192 + 4 = 196`은 W0 receipt의 관측값일 수 있으나 successor의 고정 목표가 아니다.

#### 7.3 Python package install/project selection과 package tests

Change 3이 `Iris/tooling/pyproject.toml`, `Iris/tooling/uv.lock`, `src/iris_tooling`을 만든 뒤 개발 확인은 아래 exact project selection을 사용한다.

```powershell
uv sync --project .\Iris\tooling --locked --no-editable
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling locked install failed' }
uv run --project .\Iris\tooling --locked --no-editable python -B -m pytest .\Iris\tooling\tests
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling package tests failed' }
uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --help
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling installed CLI probe failed' }
```

위 개발 environment는 편의용이며 gate authority가 아니다. 임의 cwd probe는 repository root 밖 create-new leaf에서 설치된 package로 아래처럼 실행한다. `$IrisCliProbePython`은 해당 wave의 immutable authority가 가리키는 interpreter여야 한다.

```powershell
$IrisCliProbeRoot = 'C:\Users\MW\irf\cli-probe-w3-v1'
$IrisCliProbePython = 'C:\Users\MW\iccv\env-iris-refactor-w3-v1\Scripts\python.exe'
if (Test-Path -LiteralPath $IrisCliProbeRoot) { throw "CLI probe leaf must be absent: $IrisCliProbeRoot" }
New-Item -ItemType Directory -Path $IrisCliProbeRoot | Out-Null
Push-Location $IrisCliProbeRoot
try {
    & $IrisCliProbePython -B -s -m iris_tooling --help
    if ($LASTEXITCODE -ne 0) { throw 'iris_tooling arbitrary-cwd CLI probe failed' }
}
finally {
    Pop-Location
}
```

gate용 환경은 저장소 내부 `.venv`가 아니라 wave별 external immutable leaf에 만든다. 아래는 W3 exact command이고 W4와 W5에는 wave id와 create-new leaf만 각각 `w4`, `w5`로 바꿔 같은 절차를 반복한다. W10에는 `terminal` id를 사용한다. 실행 전 current `HEAD`는 package source/lock이 동결된 implementation subcommit이어야 하며 working tree가 깨끗해야 한다.

```powershell
$ErrorActionPreference = 'Stop'
$IrisWaveId = 'w3'
$IrisProject = (Resolve-Path '.\Iris\tooling').Path
$IrisEnvironment = "C:\Users\MW\iccv\env-iris-refactor-$IrisWaveId-v1"
$IrisReceiptRoot = "C:\Users\MW\iccv\receipts\env-iris-refactor-$IrisWaveId-v1"
$IrisEnvironmentReceipt = Join-Path $IrisReceiptRoot 'environment_receipt.json'
$IrisWheelRoot = "C:\Users\MW\irf\wheel-$IrisWaveId-v1"
$IrisAuthorityRoot = '.\Iris\validation\clean_checkout\authority'
$IrisAuthorityRecord = Join-Path $IrisAuthorityRoot "responsibility_refactor_environment_$($IrisWaveId)_v1.json"
$IrisAuthorityLocator = Join-Path $IrisAuthorityRoot 'responsibility_refactor_environment_current.json'

$IrisSourceStatus = git status --porcelain=v1 --untracked-files=all
if ($LASTEXITCODE -ne 0) { throw 'implementation subject status failed' }
if (-not [string]::IsNullOrWhiteSpace(($IrisSourceStatus -join "`n"))) { throw 'implementation subject must be clean' }
$IrisImplementationCommit = ((git rev-parse HEAD) -join '').Trim()
if ($LASTEXITCODE -ne 0) { throw 'implementation commit resolution failed' }
$IrisImplementationTree = ((git rev-parse "$IrisImplementationCommit`^{tree}") -join '').Trim()
if ($LASTEXITCODE -ne 0) { throw 'implementation tree resolution failed' }

foreach ($IrisCreateNewLeaf in @($IrisEnvironment, $IrisReceiptRoot, $IrisWheelRoot)) {
    if (Test-Path -LiteralPath $IrisCreateNewLeaf) { throw "create-new leaf must be absent: $IrisCreateNewLeaf" }
}
New-Item -ItemType Directory -Path $IrisWheelRoot | Out-Null
uv build .\Iris\tooling --wheel --out-dir $IrisWheelRoot
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling deterministic wheel build failed' }
$IrisWheels = @(Get-ChildItem -LiteralPath $IrisWheelRoot -Filter '*.whl' -File)
if ($IrisWheels.Count -ne 1) { throw "expected exactly one wheel, got $($IrisWheels.Count)" }
$IrisWheel = $IrisWheels[0].FullName

$env:UV_PROJECT_ENVIRONMENT = $IrisEnvironment
try {
    uv sync --project $IrisProject --locked --no-install-project
    if ($LASTEXITCODE -ne 0) { throw 'immutable environment dependency install failed' }
}
finally {
    Remove-Item Env:UV_PROJECT_ENVIRONMENT -ErrorAction SilentlyContinue
}
uv pip install --python "$IrisEnvironment\Scripts\python.exe" --no-deps $IrisWheel
if ($LASTEXITCODE -ne 0) { throw 'exact iris_tooling wheel install failed' }

& "$IrisEnvironment\Scripts\python.exe" -B -s .\Iris\validation\clean_checkout\write_environment_receipt.py `
    --environment-root $IrisEnvironment `
    --project .\Iris\tooling\pyproject.toml `
    --lock .\Iris\tooling\uv.lock `
    --wheel $IrisWheel `
    --source-commit $IrisImplementationCommit `
    --source-tree $IrisImplementationTree `
    --out $IrisEnvironmentReceipt `
    --authority-record-out $IrisAuthorityRecord `
    --current-locator-out $IrisAuthorityLocator
if ($LASTEXITCODE -ne 0) { throw 'wave environment receipt/authority creation failed' }
```

receipt는 interpreter bytes/hash, Python version, `uv.lock` SHA-256, installed distribution/version/file manifest, exact project wheel bytes/hash, implementation commit/tree, `src/iris_tooling` tree hash, project/lock blob과 required environment를 담는다. 생성된 immutable authority record와 stable locator만 authority-only terminal subcommit으로 commit한다. 그 subcommit의 diff에 `Iris/tooling/src`, `pyproject.toml`, `uv.lock`이 있으면 실패한다. W3 전환 검증은 current 구현·test의 `phase0_ratification_attempt_0002.json` environment-resolution reference가 0이고 approved historical allowlist만 남았음을 함께 확인한다.

wave별 environment authority는 다음처럼 닫는다.

| Wave | Environment authority |
| --- | --- |
| W0-W2 | predecessor `env-v1` receipt. |
| W3-W5 | package source/lock을 바꾼 각 implementation subject에서 해당 wave의 새 wheel, create-new environment, immutable record와 stable locator를 생성한다. |
| W6-W9 | package source/lock blob이 마지막 current record와 같으면 그 record/receipt를 재사용한다. record implementation commit이 wave subject의 조상이고 `src/iris_tooling` tree/project/lock blob 및 installed manifest가 일치해야 한다. 다르면 stale reuse를 금지하고 해당 wave environment를 새로 만든다. |
| W10 | terminal implementation subject에서 새 `terminal` wheel/environment/record를 만들며 이전 wave receipt를 재사용하지 않는다. |

따라서 Change 6 이후 receipt-bound full gate는 정상 경로에서 마지막 package-source wave의 current record를 사용한다. 단, W6-W9가 package source/lock blob을 바꿨다면 같은 wave id로 environment authority를 먼저 갱신한다. 각 focused/receipt-bound 검증은 같은 ancestry/blob 조건을 적용한다.

#### 7.4 Focused, repository, determinism, failure-path validation

각 wave는 변경한 contract에 해당하는 focused test를 먼저 수행하고, 구조 전환이 끝나는 Change 3, 5, 6, 10에서는 그 commit의 receipt-bound full gate를 수행한다. W3-W5 중 package source/lock을 바꾼 wave는 full-gate 실행 여부와 무관하게 그 wave implementation subject에서 새 wheel/environment authority를 만들고 stable locator를 갱신해야 다음 wave로 진행할 수 있다. 재사용하는 receipt는 §7.3의 ancestry/blob validator를 통과해야 하며 단순히 “직전 receipt”라는 이유만으로 허용하지 않는다.

* Lua syntax: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
* repository/authority: current manifest 경로 존재성, 단일 owner, producer/consumer closure, dynamic/path-built consumer와 current gate/package binding을 검사한다.
* validation migration: R1에서 실제 이동한 source/entrypoint만 predecessor binding에서 successor binding으로 매핑한다. 기존 test family, identity, selection과 failure meaning은 변경하지 않으며 affected binding의 orphan/ambiguous가 0인지 검사한다. derived test count는 결과에만 기록한다.
* frozen fixture: `Iris/build/description/v2/frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json` SHA-256이 `b77720204c6e12f46c122d52c5602eefda311a6f5379b055aee0b843f822dfa2`인지와 manifest materialization 계약을 검사한다.
* G4/G5: `full_repository_gate.json`의 `g4_required_paths`, evidence payload, G5 compiler identity constituent와 handoff path가 모두 존재하고 historical/staging payload의 path와 raw bytes/hash가 기준선에서 변경되지 않았는지 검사한다. R1 source path만 이동했다면 해당 source binding을 같은 commit에서 갱신한다.
* package mirror: `package_runtime_mirror`가 current pointer-selected Layer 3 generation만 materialize하고 stable facade lookup, descriptor, chunk hash가 source와 같은지 검사한다.
* determinism/parity: 동일 input build 2회 canonical hash, 전환 wave의 old/new semantic parity, Browser/Wiki detail snapshot, package file manifest 반복 실행을 비교한다.
* failure path: missing input, corrupt JSON, invalid schema, subprocess failure, pointer mismatch, package extra generation, missing chunk와 unknown engine fact의 false 변환을 negative fixture로 확인한다.

검증 중 old/new dual-run은 허용하지만 terminal full gate는 successor selection만 실행한다. old 경로가 계속 성공하는 것은 acceptance 조건이 아니며, supported compatibility adapter는 old implementation이 아니라 current thin adapter 대상으로 계속 검증한다.

#### 7.5 Package exact command

terminal package output root는 저장소 외부의 absent root로 고정한다.

```powershell
$IrisPackageRoot = 'C:\Users\MW\irf\package-terminal-v1'
if (Test-Path -LiteralPath $IrisPackageRoot) { throw "package root must be absent: $IrisPackageRoot" }
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot $IrisPackageRoot -Clean -Zip -PackageApplicability current_runtime_payload
if ($LASTEXITCODE -ne 0) { throw 'terminal Iris package failed' }
```

생성 package manifest는 allowlist, current generation id 1개, stable facade/pointer/descriptor/chunk hashes, Python 및 predecessor generation/fixed chunk/forbidden path 0을 증명한다. source에 보존된 rollback predecessor 수는 package count assertion에 포함하지 않는다.

#### 7.6 Terminal Run A/Run B exact command

Change 10 terminal commit을 만든 뒤 원 working tree가 아니라 해당 exact commit의 새 clean clone에서 실행한다. `$IrisTerminalCommit`은 실행 시 `HEAD`로 기계 결속하며 임의 입력을 허용하지 않는다.

```powershell
$ErrorActionPreference = 'Stop'
$IrisSourceRepository = (Resolve-Path '.').Path
$IrisTerminalStatus = git -C $IrisSourceRepository status --porcelain=v1 --untracked-files=all
if ($LASTEXITCODE -ne 0) { throw 'terminal clean-status resolution failed' }
if (-not [string]::IsNullOrWhiteSpace(($IrisTerminalStatus -join "`n"))) { throw 'terminal source repository must be clean' }
$IrisTerminalCommitOutput = git -C $IrisSourceRepository rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'terminal commit resolution failed' }
$IrisTerminalCommit = ($IrisTerminalCommitOutput -join '').Trim()
$IrisTerminalRoot = 'C:\Users\MW\irf\terminal-v1'
$IrisTerminalRepository = Join-Path $IrisTerminalRoot 'repo'
$IrisTerminalEnvironmentReceipt = 'C:\Users\MW\iccv\receipts\env-iris-refactor-terminal-v1\environment_receipt.json'
$IrisTerminalClaim = 'iris-responsibility-refactor-terminal-v1'
if (Test-Path -LiteralPath $IrisTerminalRoot) { throw "terminal root must be absent: $IrisTerminalRoot" }
New-Item -ItemType Directory -Path $IrisTerminalRoot | Out-Null
git clone --no-hardlinks $IrisSourceRepository $IrisTerminalRepository
if ($LASTEXITCODE -ne 0) { throw 'terminal clone failed' }
git -C $IrisTerminalRepository checkout --detach $IrisTerminalCommit
if ($LASTEXITCODE -ne 0) { throw 'terminal checkout failed' }

$IrisTerminalGate = Join-Path $IrisTerminalRepository 'Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1'
$IrisTerminalCompare = Join-Path $IrisTerminalRepository 'Iris\validation\clean_checkout\invoke_deterministic_compare.ps1'
& $IrisTerminalGate -RepositoryRoot $IrisTerminalRepository -Commit $IrisTerminalCommit -ClaimId $IrisTerminalClaim -EnvironmentReceipt $IrisTerminalEnvironmentReceipt -WorkRoot (Join-Path $IrisTerminalRoot 'wa') -ResultRoot (Join-Path $IrisTerminalRoot 'ra') -OrchestrationReceipt (Join-Path $IrisTerminalRoot 'ra\orchestration.json')
if ($LASTEXITCODE -ne 0) { throw 'terminal Run A failed' }
& $IrisTerminalGate -RepositoryRoot $IrisTerminalRepository -Commit $IrisTerminalCommit -ClaimId $IrisTerminalClaim -EnvironmentReceipt $IrisTerminalEnvironmentReceipt -WorkRoot (Join-Path $IrisTerminalRoot 'wb') -ResultRoot (Join-Path $IrisTerminalRoot 'rb') -OrchestrationReceipt (Join-Path $IrisTerminalRoot 'rb\orchestration.json')
if ($LASTEXITCODE -ne 0) { throw 'terminal Run B failed' }
& $IrisTerminalCompare -RepositoryRoot $IrisTerminalRepository -Commit $IrisTerminalCommit -ClaimId $IrisTerminalClaim -EnvironmentReceipt $IrisTerminalEnvironmentReceipt -RunAOrchestrationReceipt (Join-Path $IrisTerminalRoot 'ra\orchestration.json') -RunBOrchestrationReceipt (Join-Path $IrisTerminalRoot 'rb\orchestration.json') -AttemptRoot (Join-Path $IrisTerminalRoot 'compare')
if ($LASTEXITCODE -ne 0) { throw 'terminal deterministic comparator failed' }

$IrisTerminalPython = 'C:\Users\MW\iccv\env-iris-refactor-terminal-v1\Scripts\python.exe'
$IrisTerminalCliProbeRoot = Join-Path $IrisTerminalRoot 'cli-probe'
$IrisTerminalCliStdout = Join-Path $IrisTerminalRoot 'cli-probe.stdout.bin'
$IrisTerminalCliStderr = Join-Path $IrisTerminalRoot 'cli-probe.stderr.bin'
if (Test-Path -LiteralPath $IrisTerminalCliProbeRoot) { throw "terminal CLI probe root must be absent: $IrisTerminalCliProbeRoot" }
New-Item -ItemType Directory -Path $IrisTerminalCliProbeRoot | Out-Null
$IrisTerminalCliExitCode = 1
Push-Location $IrisTerminalCliProbeRoot
try {
    & $IrisTerminalPython -B -s -m iris_tooling --help 1> $IrisTerminalCliStdout 2> $IrisTerminalCliStderr
    $IrisTerminalCliExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
if ($IrisTerminalCliExitCode -ne 0) { throw 'terminal arbitrary-cwd installed CLI probe failed' }
```

Run A/B 모두 exit `0`, comparator PASS, source checkout post-status clean, authoritative selection ledger unmapped/ambiguous 0, terminal arbitrary-cwd installed CLI exit `0`일 때만 terminal validation을 PASS로 선언한다. terminal closeout bundle은 CLI argv/cwd/interpreter, stdout/stderr hash와 exit code를 receipt로 기록한다. 또한 terminal subject의 stable environment locator가 `responsibility_refactor_environment_terminal_v1.json` 하나를 가리키고, record의 wheel/`src/iris_tooling` tree/project/lock blob binding이 terminal subject의 대응 blob과 일치해야 한다. record의 implementation commit/tree는 authority-only terminal subcommit의 부모 구현 subject이며 exact terminal subject의 조상이어야 하지 terminal subject와 같을 필요는 없다.

### Manual Validation

* Project Zomboid 지원 버전에서 Iris 단독 boot와 Pulse+Iris boot를 확인한다.
* 메인 메뉴와 in-game에서 script error, duplicate event registration, compat installer 누락 오류가 없는지 확인한다.
* Browser를 열고 category, search, classification, variants, reset/reopen 동작을 확인한다.
* 아이템 context menu에서 Wiki를 열고 food, weapon, literature, moveable, 정보 부족 아이템의 section/단위/빈 상태를 확인한다.
* nil section이 빈 label이나 오류를 만들지 않고 기존 panel/layout/scroll 동작이 변경되지 않았는지 확인한다.
* Alt Tooltip이 최대 4줄이고 Browser/Wiki와 사실 값이 일치하며 추천/효율 판단을 표시하지 않는지 확인한다.
* 한국어/영어 전환에서 unit scaling과 section visibility가 동일 의미를 유지하는지 확인한다.
* Recipe와 Right-click 사실이 각자 독립 표면에서 유지되는지 확인한다.
* Iris boot 전후 `ISInventoryPaneContextMenu.doReloadMenuForBullets`, `ISContextMenu.render` 함수 identity가 같고 Iris가 교체 wrapper/event installer를 남기지 않는지 확인한다. 이는 외부 모드 조합의 동작 보존을 증명하지 않는다.
* synthetic context option에 `tickTexture = nil`과 invalid texture를 넣는 bounded negative probe를 지원 PZ 버전에서 수행하여 engine error/stack과 menu render 결과를 기록한다. 회귀가 관측되면 patch를 복원하거나 Nerve로 옮기지 않고 closeout state `blocked`, reason `PATCH_REGRESSION_PENDING_SEPARATE_DECISION`으로 종료한다.
* bullet reload menu도 vanilla-only와 대표 supported mod 조합의 관측 결과를 별도 receipt로 남긴다. 관측하지 않은 외부 모드에 대한 호환성 주장을 하지 않는다.
* 만들어진 package를 별도 mods 디렉터리에 설치해 inactive Layer 3 generation과 legacy chunk가 포함되지 않았는지 확인한다.
* supported manifest에 실제 listed된 `IrisData`, `IrisBrowserData.getGroupVariants`, `IrisBrowserData.build`, Wiki render facade의 representative observable shape와 missing-key/nil behavior를 확인한다. `StaticData.getLegacyIrisData`는 public supported surface로 집계하지 않고 listed `IrisData`를 운반하는 internal loader contract만 별도로 확인한다.

### Validation Limits

* 이 계획의 closeout에서 장시간 multiplayer 세션, dedicated server 전체 조합, 모든 외부 모드와의 호환성 sweep은 수행하지 않는다.
* 전역 reload/context-menu patch 제거가 외부 모드 interaction defect를 모두 해결하거나 기존 방어 효과를 보존한다는 주장은 `unvalidated_but_in_scope`다. complete는 “Iris가 전역 함수를 더 이상 patch하지 않는다”까지만 주장하며 Project Zomboid/외부 모드 전체 동작 동일성을 주장하지 않는다.
* 위 bounded null/invalid `tickTexture`와 reload probe를 실행하지 못했거나 blocking regression이 관측되면 이 계획은 complete가 아니다. 별도 owner decision 없이 삭제 코드를 복원하거나 다른 spoke에 재구현하지 않는다.
* 이미 배포된 package와 release tag를 다시 검증하거나 변경하지 않는다.
* release/freeze/RTC/publish/deployment 절차 자체는 실행하지 않는다.
* PZ 엔진이 제공하지 않는 headless UI 동작은 자동화만으로 PASS를 선언하지 않고 manual evidence를 남긴다.

---

## 8. Risk Surface Touch

### Authority Surface

높음. Description v2 current entrypoint, authority manifest, generated artifact ownership, validation implementation binding을 변경한다. 다만 Iris의 헌법적 제품 권위와 사실 schema의 의미는 변경하지 않는다. 모든 변경은 current manifest와 decision record로 봉인한다.

### Runtime Behavior Surface

중간에서 높음. Iris boot에서 두 전역 동작 패치를 제거하고, Browser cache/lifecycle, Detail fact access, Wiki nil 의미 처리와 Layer 3 package contents를 변경한다. 사실 내용, Wiki layout/scroll과 game state mutation은 변경하지 않는다.

### Compatibility Surface

중간에서 높음. old Python entrypoint, right-click v2/v2.2/v2.3 mode, 비공개 중복 index implementation과 두 전역 patch를 제거한다. current supported `IrisData`, `IrisBrowserData.getGroupVariants`, `IrisBrowserData.build`, Wiki render facade는 thin adapter로 보존하고 representative contract를 유지한다. unlisted `StaticData.getLegacyIrisData`는 public support claim 없이 internal loader disposition과 contract를 유지한다. Layer 3 source predecessor는 main closeout에서 rollback target으로 남기되 package에는 노출하지 않는다. patch가 방어하던 외부 모드 상호작용은 별도 validation ceiling을 가진다.

### Sealed Artifact Surface

없음. historical, evidence, staging, frozen predecessor와 sealed artifact의 path·bytes를 이동·수정·삭제하지 않는다. terminal 검증은 해당 경로의 기준선 hash가 변경되지 않았음을 확인한다.

### Public-Facing Output Surface

낮음에서 중간. Browser/Wiki/Tooltip의 사실 값과 기존 layout/scroll은 유지하고 unit/visibility 정렬과 nil section 의미 오류만 수정한다.

---

## 9. Risk Analysis

### Architecture Risk

* 새 package를 추가하고 old scripts를 남기면 구조가 더 복잡해질 수 있다. wrapper expiry를 wave acceptance에 포함하고 final wrapper count 0을 강제한다.
* 삭제된 patch가 호환성 명목으로 다른 helper나 spoke에 재도입될 수 있다. 저장소 전체 forbidden-pattern 검사로 동등 구현과 install hook의 재등장을 차단한다.

### Runtime Risk

* global patch 제거로 기존 사용자에게 보이던 reload/context-menu 방어 효과는 의도적으로 사라진다. Iris boot가 함수 identity를 건드리지 않는지는 검증할 수 있지만 외부 조합의 동작 보존은 검증 상한 밖이다. bounded probe 회귀는 별도 decision 전까지 blocker다.
* Browser lifecycle 분리 중 cache invalidation 순서가 바뀔 수 있다. build/reset/rebuild state transition test와 golden query를 둔다.
* engine fact reader 분리 중 nil/exception을 false로 바꾸면 Iris의 무추론 원칙을 위반한다. tri-state result와 negative fixture를 사용한다.
* Layer 3 package projection에서 current generation을 누락하거나 predecessor를 섞을 수 있다. pointer/descriptor/hash와 stable facade lookup을 package 전후 비교하고 extra-generation negative test를 둔다. main closeout에서는 source predecessor를 삭제하지 않는다.

### Compatibility Risk

* 저장소 밖 개인 script가 old Python 경로를 직접 호출할 수 있다. current 공식 consumer를 모두 이관하고 한 wave의 경고 wrapper와 명시적 migration map을 제공한 뒤 제거한다.
* 외부 Lua code가 `IrisData` global이나 `IrisBrowserData.build()`를 호출할 수 있다. 이 둘은 현행 supported authority에 따라 thin adapter로 보존한다. 향후 제거는 이 계획의 암묵적 후속 작업이 아니라 별도 superseding decision, consumer evidence, migration plan을 요구한다.
* PowerShell 버전에 따라 package allowlist 구현이 달라질 수 있다. PS 5.1/7 parity를 가능한 환경에서 확인하고 공통 API만 사용한다.

### Regression Risk

* gate path binding 변경 중 validation contract가 누락되거나 같은 ID의 assertion 의미가 뒤집힐 수 있다. R1에서 실제 이동한 source/entrypoint의 predecessor→successor binding map에 observable property와 failure meaning을 기록하고 orphan/ambiguous 0을 terminal condition으로 둔다. 기존 selection과 identity를 통합하거나 줄이지 않는다.
* current 대형 모듈 분해 중 issue ordering이나 canonical serialization이 바뀔 수 있다. semantic set뿐 아니라 승인된 ordering/canonical hash도 비교한다.

---

## 10. Rollback Plan

실행은 아래 Change↔wave mapping을 따른다. 한 wave는 표에 적힌 Change만 포함하고, path 이동과 `full_repository_gate.json`/canonical gate/manifest rebinding은 같은 wave의 atomic commit으로 취급한다.

| Wave | Change | Rollback unit / exit |
| --- | --- | --- |
| W0 | Change 1 baseline | S0 receipt와 inventory만 생성한다. code mutation 없음. |
| W1 | Change 1 decisions/checkpoint | successor decisions와 current migration map을 별도 review commit으로 봉인한다. implementation action 없음. |
| W2 | Change 2 | 두 global patch와 installer/load binding을 무대체 삭제한다. bounded probe blocker면 정지한다. |
| W3 | Change 3 | `iris_tooling` package, lock, external environment receipt authority를 도입한다. |
| W4 | Change 4 | Description v2 current 대형 모듈을 package owner와 책임별 module로 전환한다. IAR/vNext physical file은 변경하지 않는다. |
| W5 | Change 5 | Right-click v2.4-only current CLI와 9개 additional node/standalone determinism binding을 전환한다. |
| W6 | Change 6 | package를 current Layer 3 generation-only로 바꾼다. source predecessor는 변경하지 않는다. |
| W7 | Change 7 | Browser projection/lifecycle/metrics를 분리하고 supported facade를 보존한다. |
| W8 | Change 8 | Detail fact reader/model assembler와 Wiki/Tooltip shared decisions를 전환한다. |
| W9 | Change 9 | internal legacy consumer와 Wiki nil 의미 오류를 제거하고 supported adapters를 봉인한다. |
| W10 | Change 10 | R1 temporary wrapper 제거, terminal manifests/docs/full gate를 봉인한다. |

각 wave는 이전 wave의 terminal commit을 parent로 하고 실패 시 해당 wave commit만 revert할 수 있어야 한다. W1 review 승인 전 W2 이후 destructive wave를 시작하지 않는다.

* package/generated output은 disposable staging에 만들며 실패 시 tracked current output을 덮어쓰지 않는다.
* Python 전환 중 parity가 깨지면 새 CLI binding만 되돌리고 old current entrypoint로 복귀할 수 있다. 단, final closeout 후에는 old wrapper를 rollback 수단으로 상시 유지하지 않는다.
* W6가 실패하면 package allowlist/manifest binding만 이전 package contract로 revert한다. source predecessor는 이 계획에서 변경되지 않는다.
* runtime wave가 실패하면 Browser/Detail facade binding은 이전 implementation으로 되돌릴 수 있다. 전역 patch 삭제는 이 계획의 rollback 대상에서 제외한다. 예상하지 못한 동작 차이는 closeout state `blocked`, reason `PATCH_REGRESSION_PENDING_SEPARATE_DECISION`으로 기록하며 patch를 복원하거나 Nerve/다른 모듈에 재도입하지 않는다.
* historical evidence와 sealed artifact를 수정하거나 삭제하는 방식으로 rollback하지 않는다. 이 계획의 rollback은 R1이 변경한 current implementation과 binding에만 적용한다.
* destructive rollback에 `git reset --hard`, 전체 workspace 삭제, 광범위 wildcard 삭제를 사용하지 않는다.

---

## 11. Governance Constraints

* `docs/Philosophy.md` 준수는 모든 wave의 최우선 acceptance 조건이다.
* Iris는 정보 표시 전용이다. game state, reload behavior, 전역 context menu rendering을 소유하지 않는다.
* Iris 런타임은 Lua only이며 Python package는 배포 package에 포함하지 않는다.
* Iris는 Pulse 외 spoke에 의존하지 않는다. Pulse 역시 Iris에 의존하지 않는다.
* 삭제되는 전역 patch 기능은 Nerve를 포함한 다른 spoke나 공통 helper로 이전·복제·재구현하지 않는다.
* Browser, Wiki, Tooltip은 검증 사실만 표시한다. 정보 부족은 침묵/unknown으로 처리하고 부정 사실을 추론하지 않는다.
* Alt Tooltip은 최대 4줄을 유지한다.
* Recipe와 Right-click의 의미 authority를 합치지 않는다.
* current authority는 정확히 하나의 producer/entrypoint/owner를 가져야 한다. physical duplicate 제거는 후속 경량화 범위이며 이 계획은 current owner binding만 단일화한다.
* historical, staging, evidence, frozen predecessor와 sealed artifact는 current gate 사용 여부와 무관하게 이 계획에서 이동·수정·삭제하지 않는다.
* sealed artifact는 in-place 수정하지 않는다. correction/amendment record를 사용한다.
* 검증은 fail-closed다. 관련 exact command가 exit `0`이 아니면 PASS를 선언하지 않는다.
* required tool이 없으면 해당 검증은 PASS가 아니라 BLOCKED다.
* current migration map 누락, unresolved dynamic consumer와 gate path 누락은 implementation blocker다.
* clean-checkout subject와 개발 working tree 결과를 혼동하지 않는다.
* 현재 worktree의 사용자 소유 변경과 이 계획에 속하지 않는 모듈을 수정하거나 정리하지 않는다.
* temporary migration adapter는 만료 wave와 removal validation을 가져야 한다. `phase0_supported_api_manifest.json`에 등록된 supported compatibility adapter는 temporary wrapper로 분류하지 않는다.
* 저장소 byte 감소는 이 계획의 목표나 성과 지표가 아니다. historical payload와 물리 duplicate의 존속 여부는 후속 경량화에서 판정한다.
* 전역 patch 삭제는 실행 전에 decision으로 채택하고 알려진 bullet reload/context-menu texture 방어 defect 및 external compatibility validation ceiling을 함께 기록한다. 삭제 기능을 Nerve나 다른 spoke에 재구현하지 않는다.
* supported `IrisData`, BrowserData, Wiki facade와 Layer 3 source predecessor hold는 current decision을 따른다. 이 계획의 구현 편의를 이유로 사후 supersede하지 않는다.
* validation authority는 selection rule과 predecessor→successor contract ledger다. derived count 자체는 authority가 아니다.
* formal closeout state는 `EXECUTION_CONTRACT.md`의 `complete`, `partial`, `implemented_only`, `blocked`만 사용한다. 세부 원인은 별도 blocking/non-claim code로 기록하며 새 state enum을 만들지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

`complete`는 아래 validation ceiling 안에서만 의미가 있다. terminal closeout은 각 행에 실제 receipt/manifest 경로를 1:1로 연결한다.

| Ceiling class | Closeout 범위 |
| --- | --- |
| `validated` | exact clean subject의 full gate Run A/B와 comparator, terminal wheel/source-blob-bound `iris_tooling` environment와 arbitrary-cwd CLI, Lua syntax, package current-generation-only contract, affected validation binding, preserved historical/staging/frozen hashes, supported facade representative contract, Iris의 global patch 부재와 대상 함수 identity, bounded supported-PZ reload/context-menu probe |
| `out_of_scope` | release/freeze/RTC/publish/deployment, 이미 배포된 package/tag, 장시간 multiplayer, dedicated server 전체 조합, historical authority 전체 재실행, staging/evidence/historical/predecessor의 물리 경량화, output/media 중복 제거, runner/helper/AI readpoint 최적화, Wiki layout/scroll 개선 |
| `unvalidated_but_in_scope` | 임의의 제3자 모드 조합에서 두 patch 삭제가 만드는 reload/context-menu 상호작용 결과와 기존 방어 효과의 보존 여부 |

따라서 이 closeout은 `release-ready`, `deployed`, multiplayer/dedicated-server 검증, 모든 외부 모드 compatibility, Project Zomboid 기본 동작의 byte/behavior equivalence를 주장하지 않는다. `unvalidated_but_in_scope` 영역에는 success/compatibility-preserving claim을 붙이지 않는다.

`complete`는 다음 조건을 모두 만족한 상태를 뜻한다.

* Iris boot 경로와 코드에 `IrisBulletReloadCompat`, `IrisContextMenuTextureCompat` 및 해당 전역 monkey patch가 없다.
* 저장소의 다른 모듈에도 두 patch의 동등 구현이나 설치 hook이 없다. Iris boot 전후 대상 전역 함수 identity가 같고 bounded probe receipt가 존재한다. 외부 모드 전체의 동작 동일성은 closeout claim이 아니다.
* current build/authority manifest가 모든 current producer, consumer, entrypoint, validation을 단일하게 설명한다.
* staging/evidence/historical/IAR/vNext와 frozen predecessor payload의 tracked path, Git blob과 SHA-256이 기준선과 동일하며 current build manifest는 이를 새 current implementation으로 승격하지 않는다.
* Description v2 current Python은 설치 가능한 `iris_tooling` package에서 실행되고 `Iris/tooling/src/iris_tooling`과 successor current test source의 `sys.path` 조작과 cwd/root 추측이 0이다. root `pytest.ini`의 `Iris/build` pythonpath 주입도 0이며 승인된 root exception이 있으면 exact consumer/expiry가 기록된다.
* old build/right-click entrypoint migration wrapper가 0이다.
* Right-click current CLI는 v2.4 하나만 지원하고 이전 버전은 current code path에 없다.
* package에는 Layer 3 current generation이 정확히 1개이고 legacy fixed chunks/predecessor generation이 없다. source media의 inactive generation/fixed chunks는 current rollback/package-bootstrap authority가 유지되는 동안 존재할 수 있다.
* BrowserData의 projection/lifecycle/metrics 책임과 Detail의 engine fact reading/model assembly 책임이 분리되어 있다.
* Browser와 Wiki가 동일한 detail model, unit, visibility 결정을 사용하고 Tooltip 4줄/무추론 계약이 유지된다.
* Iris 내부 product path의 legacy `IrisData` fallback과 독립 중복 authority payload는 0이다. listed supported `IrisData` global/module, `IrisBrowserData.getGroupVariants`, `IrisBrowserData.build`, Wiki render facade는 current thin adapter로 존재하고 predecessor observable contract를 만족한다. unlisted `StaticData.getLegacyIrisData`는 public support claim 없이 thin internal loader disposition과 contract를 만족한다. 죽은 Wiki reason data/section 호출은 제거하되 supported render wrapper의 nil/no-op contract는 유지한다.
* R1에서 이동한 source/entrypoint의 predecessor→successor validation binding map에 orphan/ambiguous가 0이고 terminal authoritative selection, test family와 failure meaning이 기준선 계약과 일치한다. derived count는 receipt에만 기록된다.
* terminal stable locator가 terminal immutable environment record 하나를 가리킨다. record의 wheel hash, `src/iris_tooling` tree, `pyproject.toml`/`uv.lock` blob binding과 installed manifest가 exact clean terminal subject의 대응 blob과 일치하고, record의 implementation commit/tree는 authority-only terminal subcommit의 부모 구현 subject이자 terminal subject의 조상이다. implementation commit과 terminal subject의 commit id 자체가 같을 것을 요구하지 않는다. predecessor `phase0_ratification_attempt_0002.json`의 current environment-resolution consumer는 0이고 historical allowlist만 남는다.
* terminal Run A와 Run B가 exact clean subject와 그 terminal immutable environment receipt로 모두 exit `0`이고 comparator가 PASS한다.
* Lua syntax, installed package/terminal arbitrary-cwd CLI, package contract, affected validation binding, determinism, supported facade와 focused runtime behavior 검증이 모두 통과한다.
* `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`, `ENTRYPOINTS.md`, current inventory가 최종 구조와 일치하고 terminal commit/receipt를 가리킨다.

R1 mandatory 항목이 “후속 작업”으로 남거나 R1이 도입한 temporary wrapper가 유지되거나 bounded patch probe/terminal gate가 실행되지 않았다면 closeout은 `complete`가 아니다. 반대로 historical/predecessor 물리 삭제, archive, output/media 중복 제거, runner/helper/AI readpoint 최적화와 Wiki layout/scroll 개선의 미실행은 이 계획의 closeout을 막지 않는다. bounded patch probe에서 blocking regression이 발견되면 별도 successor decision 전까지 closeout state는 `blocked`, blocking reason은 `PATCH_REGRESSION_PENDING_SEPARATE_DECISION`이다.
