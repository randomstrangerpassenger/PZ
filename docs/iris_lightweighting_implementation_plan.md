# Implementation Plan

> 계획명: Iris 저장소·런타임 데이터·생산기 경량화 및 잔여 구조 정리
>
> 작성일: 2026-09-16
>
> 상태: 제안 계획 — 구현 미착수
>
> 입력: 사용자가 제공한 두 분석의 종합 로드맵
>
> 개정: 2026-09-16 사용자 요청 반영. 저장소 적용 범위, 단순 개선의 착수 조건, B→Menu 후보 연결, Recovery 설치 및 중복 검사·Gate 최소화
>
> 양식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)
>
> 조사 기준: 현재 working tree의 Iris 코드와 문서. 미커밋 수정·추가 파일을 포함하며 clean HEAD와 동일하다고 가정하지 않는다.

## 1. Objective

Iris의 근거·설명·공개 동작을 유지하면서 중복 데이터 저장, Lua 정적 테이블 생성, DVF 생산기의 복사·탐색, Browser 상세 재생성에 드는 비용을 줄인다. 변경마다 직접 줄이려는 비용의 핵심 지표를 선택하고, 측정한 범위 안에서 효과를 판단한다. 서로 다른 효과를 하나의 경량화 수치로 합산하지 않는다.

Change 1 이후 핵심 최적화의 우선순위는 **EvolvedRecipe 공통화 → Tooltip 중복 제거 → 빌드 계산량 축소**다. 보관 후보 실험과 Browser 부분 갱신은 각각 독립적인 트랙으로 진행할 수 있으며, 보관 실험의 완료를 런타임·빌드·UI 변경의 선행 조건으로 두지 않는다. 비활성 자료의 보관 위치 변경과 청크화는 해당 트랙의 조사·측정 조건을 충족할 때만 적용한다.

이번 실행 subject는 `iris-runtime-build-storage-optimization-2026-09-16`으로 구별한다. 이는 문서상 작업 식별자이며 새 authority/schema가 아니다. 기존 repository lightweighting terminal closeout의 재개·후속 봉인으로 취급하지 않는다.

문서 작성 자체의 산출물은 이 계획서다. 아래 변경·검증 명령은 후속 구현을 위한 것이며, 이번 작성에서 코드 변경·자료 삭제·authority 채택·패키지 생성·게임 실행을 수행한 것으로 간주하지 않는다.

---

## 2. Scope

| 트랙 | 포함 범위 | 결과를 판단할 지표 |
| --- | --- | --- |
| R: 저장소 경량화 | expression revisions, evidence/receipt, 비활성 generation, Git/LFS 원인 조사, 캐시 ignore | 선택 표본의 보관 bytes와 복원·reader 소비. 실제 이동 시에만 순 저장량; Git/LFS는 원인 조사 |
| D: 런타임 데이터 | EvolvedRecipe 표현 공유, Tooltip base/variant 표현 공유, 조건부 lazy chunk | 기본은 생성 table 수·Lua bytes. 청크 도입 시에만 최초 로드 비용 중 하나 추가 선택 |
| B: 생산기 최적화 | recovery의 provenance 재탐색과 전체 `deepcopy` 축소 | 해당 생산 구간 시간 또는 peak memory 중 주지표 하나, 출력 의미와 입력 불변성 |
| U: UI 반응성 | Browser 상세 내부 검색·펼치기/접기의 부분 갱신 | 정적 model/무관한 child 재생성 횟수, focus·스크롤·요구조건 상태 보존 |
| S: 잔여 구조 정리 | 실제 중복 실행자, adapter 계약, 순수 정적 recovery data, 테스트 실행 경로 안내, `.gitattributes` | 남은 구현 중복·유지 경로와 회귀 계약 |

### Explicitly Out Of Scope

- r1~r5 즉시 삭제, r6 `audit.json` 삭제 또는 LFS 해제, 비활성 generation 일괄 삭제.
- `Iris/build/description/composition/blocks.json`과 `descriptions.json` 제거·임시 캐시 취급.
- Git history rewrite, `git gc`/prune/LFS prune를 통한 즉석 저장소 축소, 공유 이력 변경.
- 기존 accepted/current authority와 product pointer 전환, B/C 공동 활성화, strict finalization, 공개 배포.
- 기존 repository lightweighting terminal subject 재개·재측정·재판정, 기존 adoption/terminal PASS의 이번 subject로의 승계. 현재 tree에 없는 `docs/iris_lightweighting_terminal_closeout.json`의 복원·대체·삭제 처분 변경도 제외한다.
- 설명 문장 개선·누락 사실 보완·purpose 재판정. 별도 DVF 표현 과제의 상태를 이 작업으로 닫지 않는다.
- 테스트 위치 이동·unittest ID 변경·framework 통일, 일반 pytest의 범위를 늘려 전용 producer 경로를 흡수하는 작업.
- 2026-09-16에 완료된 책임 분리의 재수행, `registry.zip`과 `_dev` harness의 크기만을 이유로 한 제거.
- 다른 모듈의 기능 수정, Java 런타임 도입, B42 포팅, 외부 모드 전수 호환성 검증.

---

## 3. Non-Goals

- 파일 수·줄 수를 줄이는 것 자체를 성공으로 삼지 않는다.
- 원본 authority를 새 압축 포맷으로 대체하거나 보관 manifest를 새로운 사실 owner로 만들지 않는다.
- 런타임에서 문장을 재조합·번역·요약하거나 유효한 상호작용을 다시 판정하지 않는다.
- 성능을 이유로 실제 플레이어 상태에 따라 달라지는 요구조건을 정적 캐시에 고정하지 않는다.
- 기존 PASS의 재발행, 불필요한 전수 hash 증명·재생산·봉인, 새로운 validation authority를 만들지 않는다.
- 수 GB 절감을 사전에 보장하지 않는다. 파일 전체 중복과 revision 내부의 부분 중복은 다른 문제다.

---

## 4. Assumptions

### 적용할 설계·상태 기준

1. [Philosophy.md](Philosophy.md)가 최상위 기준이다. PZ에서 실행되는 Iris는 100% Lua이며 정보만 제공한다. Menu/Alt Tooltip 두 표면과 Tooltip 최대 네 줄, 근거 부족 시 침묵, 레시피·우클릭의 동등성을 유지한다.
2. [DECISIONS.md](DECISIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)의 최신 관련 기록을 적용한다. 2026-09-16 리팩토링 완료는 저장소 Iris 실행에 대한 수락이며 별도 후보 ZIP·전체 설명 품질·release 완료가 아니다.
3. [기존 리팩토링 계획·실행 기록](iris_refactoring_implementation_plan.md)의 r1~r5 보관 no-op, 테스트 위치·ID 유지, registry 실행자 세 개 archive 결정을 승계한다. 이 계획은 해당 보존 결정을 뒤집지 않는다.
4. 저장소에는 이미 관련 dirty 변경이 있다. 구현 착수 시 그 시점의 입력과 변경 범위를 기록하고, 기존 변경을 reset/clean하거나 옛 HEAD를 현재 구현으로 간주하지 않는다.
5. 현재 route와 환경 진입점은 `Iris/_docs/authority/iris_current_route_index.json`, `Iris/validation/execution/required_validations.json`, `Iris/validation/execution/current_environment.json`이다. historical locator 이름만 보고 이전 runner를 재가동하지 않는다.

### 기존 terminal closeout과 이번 subject의 경계

- `ROADMAP.md`의 **Iris repository lightweighting execution**과 `DECISIONS.md`의 **Terminal closeout — exact W10 및 local-custody correction**은 기존 작업을 complete로 기록한다. 해당 implementation subject는 `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3`이며 당시 W10·final measurements·machine/reviewer PASS는 그 subject에 남는다.
- 이번 R 트랙은 현재 tree의 추가·잔존 자료와 새 저장 후보를 조사한다. 과거의 잔여 0 판정을 현재 tree에 다시 요구하거나, 현재 대용량 파일을 과거 closeout 실패의 근거로 사용하지 않는다. 기존 숫자·ceiling을 새 subject의 성능 기준으로 자동 승계하지 않는다.
- 기존 adoption `Iris/validation/clean_checkout/authority/iris_current_historical_lightweighting_adoption_v1.json`, archive/removal authority 및 terminal 관련 기록은 보호한다. 그 기록의 과거 archive/removal 권한을 이번 대상의 제거 권한으로 사용하지 않는다.
- `docs/iris_lightweighting_terminal_closeout.json`은 개정 시점의 tree에서 존재하지 않음을 확인했다. 부재만으로 삭제 이유·정당성을 판정하지 않으며, 해당 readpoint의 처분은 이 계획 밖이다. 기존 `DECISIONS.md`의 참조를 새 보고서로 치환하지 않는다.
- 이번 결과 문서는 `docs/iris_runtime_build_storage_optimization_closeout.md`로 구별한다. 기존 terminal closeout의 복구본·대체 readpoint·재봉인 결과가 아니다.

### 종합 검토에 대한 개정 판단

검토안의 공통 합의와 작성자의 적용 판단을 구분한다. 핵심 구현 방향은 유지하며, R1·R2의 severity 충돌을 두 검토자가 합의한 Critical로 재표현하지 않는다.

| 검토 항목 | 이번 계획의 적용 판단 |
| --- | --- |
| R1: 과거 terminal과의 경계 | 위 별도 subject·보호 대상·부재 readpoint 제외를 명시하여 모호성을 해소한다. 과거 작업을 재개하지 않는다. |
| R2 / W3: 채택 기준과 계측 비용 | 단순 개선은 실제 중복·계산량 감소와 정확성으로 판단한다. 새 저장·설치·로딩 경계를 도입할 때만 사전 개선 하한을 정한다. 별도 측정 회차나 공통 개선율 gate는 만들지 않는다. |
| W1: 보관 실험 선행 | Change 2를 독립적인 소규모 실험으로 제한한다. CAS/chunk 일반화는 자동 구현 범위에서 제외한다. |
| W2: 대형 통합 node | 변경 경계에 필요한 node를 선택한다. 기존 필수 assertion은 유지하되 helper 기반 focused 경로를 같은 테스트 파일에서 보완할 수 있다. |
| N1 / N2 / N3 | 무매칭 attribute 규칙 유지 원칙, Change 9의 정식 진입과 이관 대기 구별, gate 설정의 전체 경로를 반영한다. |
| N4: Lua aliasing 검증 | 기존 EvolvedRecipe 테스트의 실제 `lua -e` 경로와 Browser interaction Lua harness를 §7에 연결하고, 추가할 assertion을 구별한다. |

### 코드·파일 조사에서 확인한 기준선

아래는 계획 작성 시점의 읽기 전용 관찰이다. 파일 크기는 논리적 파일 길이이며 디스크 할당량·ZIP 크기·실제 PZ 메모리와 같지 않다. 입력이 바뀌면 구현 착수 시 재측정한다.

| 대상 | 확인값·구현 | 계획에 주는 제약 |
| --- | --- | --- |
| `Iris/_docs/authority/dvf/layer3_expression/successors/` | 32 files, 4,892,955,122 bytes ≈ 4.56 GiB | r1~r6의 저장 구조가 큰 비용이지만 untracked 여부는 삭제 근거가 아님 |
| r6 `audit.json` | 416,054,423 bytes ≈ 396.8 MiB | r6 manifest의 member이며 adoption의 B/C residual이 직접 path/hash로 참조함 |
| `IrisEvolvedRecipeLookup.lua` | 1,742,824 bytes; 252 FullTypes / 2,203 relations | 각 relation에 locale label/action/display와 conditions 테이블을 반복 출력 |
| `IrisTooltipStaticData.lua` / `IrisTooltipRecipeVariants.lua` | 각각 1,116,186 / 768,344 bytes, 합계 약 1.80 MiB | 두 데이터 파일의 합계를 단일 파일 크기로 취급하지 않음 |
| `IrisLayer3Generations/` | 12 directories / 168 files, 27,494,356 bytes ≈ 26.22 MiB | default pointer가 고른 세대 외 11개도 참조 조사 전에는 제거 불가 |
| `composition/blocks.json` / `descriptions.json` | 각각 38,288,656 / 53,854,570 bytes | 현재 생산·검수·B/C 입력이므로 review dump와 구별 |
| `composition/quality_review/` | 16 files, 152,507,929 bytes | 하위 파일별 검수·재현 역할 분류가 필요 |
| `Iris/tooling/.tmp/` | 692 files, 23,802,433 bytes | `.gitignore`는 root `.tmp`와 tooling `.venv`만 포함; `uv-cache`는 ignore 미적용 |
| legacy `Iris/build/description/v2/tools/` | 재귀 집계 Python 파일 234개 | 로드맵의 “217 build scripts”와 집계 범위가 다름. 파일 수를 중복 실행자 수로 사용하지 않음 |
| Git objects | `git count-objects -vH`: loose 2.50 GiB, packs 164.59 MiB | `.git` 전체·LFS 수치와 구별. 명령의 garbage 경고는 원인 조사 입력이며 삭제 판정이 아님 |

추가로 확인한 동작은 다음과 같다.

- `Iris/tools/package_iris.ps1`은 legacy/product generation 전체를 복사하지 않고 선택된 세대를 투영한다. `Iris/test/validate_disposable_package.ps1`은 legacy 경로의 단일 세대를 검사한다. Product 후보 경로는 별도 product integration 검사가 필요하다.
- `IrisTooltipStaticDataLookup.get/open`은 이미 최초 사용 시 보호된 `require`를 한다. 남은 문제는 최초 사용 시의 통짜 payload와 반복 테이블이다. `open`은 base 일치·variant 배열·양 언어·행 수·identity를 검증한다.
- `recipe_variants.project_interaction_variants`는 공통 prefix를 각 variant에 복사하고 `variants_bytes`는 base와 전체 KO/EN 행 배열을 다시 기록한다. 과거 recipe 전용 projection과 후보 interaction projection은 둘 다 존재한다.
- `recovery_expression.produce`는 `deepcopy(inputs)` 후 provenance마다 남은 facts를 `any(...)`로 재탐색한다. `recovery.acquisition_content/acquisition_successor`도 큰 acquisition payload를 복사한다.
- `IrisBrowserDetail.showDetail`에는 FullType/locale/generation이 같은 경우의 재사용 분기가 이미 있다. 다만 `IrisBrowserInteractionRenderer.ensureSearchEntry`의 상세 검색과 toggle들은 `showDetail(..., true)`를 호출하여 전체 child 제거와 `DetailViewModel.fromItem`을 다시 수행한다. 모든 검색이 무조건 전체 재생성된다는 주장은 사용하지 않는다.
- `content_addressed_archive.py`는 기존의 파일 단위 CAS ZIP 구현이다. `source_rows`가 모든 object bytes를 메모리에 모으며 `tracked_git_blob`는 `git show`를 읽는다. LFS pointer와 실제 payload를 구별하지 않고 그대로 적용할 수 없다.
- root `pytest.ini`의 testpaths는 제한적이지만 전용 producer source와 repository runner 분류가 별도로 존재한다. 기본 pytest에서 수집되지 않는다는 이유만으로 검증 누락으로 판정하지 않는다.

---

## 5. Repository Areas Affected

아래는 후속 구현의 후보 범위다. 이 문서 작성에서 수정하는 파일은 계획서 하나다.

### Code

- 보관: `Iris/validation/artifacts/content_addressed_archive.py`, `archive_and_prune_artifacts.py`, `inventory_artifact_lifecycle.py`, `lifecycle_delta_codec.py`.
- EvolvedRecipe: `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py`와 `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua`의 생성 경로.
- Tooltip: `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/{serialization,recipe_variants,projection,install,contract}.py`, `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua`.
- 생산기: `Iris/tooling/src/iris_tooling/domains/layer3/{recovery,recovery_expression,recovery_adjudication,recovery_relations}.py`. 다른 분리 모듈은 실제 profiling·호출 관계상 필요한 경우에만 포함한다.
- Browser: `Iris/media/lua/client/Iris/UI/Browser/{IrisBrowserDetail,IrisDetailChildren,IrisBrowserInteractionRenderer,IrisBrowserInteractionProjection,IrisBrowserInteractionState}.lua`, `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`.
- 패키지: `Iris/tools/package_iris.ps1`, `Iris/tools/Layer3PackageProjection.psm1` 및 해당 후보 install 경로.
- 잔여 구조: `Iris/tooling/src/iris_tooling/build/`, `domains/public_text/composition/`, `common/`, `Iris/build/description/v2/tools/`, `Iris/validation/source_analysis/`의 실제 중복 구간만.

### Docs

- 이 계획서와 후속 실행 결과 문서 `docs/iris_runtime_build_storage_optimization_closeout.md`(후속 작성 예정).
- 실제 변경이 채택된 경우에만 `docs/ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`에 구현·측정·수락 범위를 반영한다.
- 기존 refactoring·Tooltip supply·Menu 후보 closeout은 과거 subject 기록으로 유지한다.

### Config

- `.gitignore`: 확인된 tooling 캐시 경로의 제한적 ignore.
- `.gitattributes`: 실제 속성 결과를 보존할 수 있는 중복 규칙만 조건부 정리.
- `Iris/tooling/pyproject.toml`, root `pytest.ini`, `Iris/validation/execution/required_validations.json`, `Iris/validation/execution/contracts/repository_test_gate.json`, `Iris/_docs/round3/round3_pytest_source_classification.json`: 검증 진입점 조사 대상. 경량화를 위해 수집 범위·거부 조건을 완화하지 않는다.

### Generated Artifacts

- EvolvedRecipe 및 Tooltip의 Lua 후보, 후보 owner/manifest, 격리 stage와 ZIP.
- expression/evidence 보관 후보와 복원 시험 디렉터리. 기본 위치는 기존 허용 경로 안의 실행 전용 임시 영역이며 새로운 정규 authority tree를 만들지 않는다.
- current/accepted authority, r1~r6 원본, composition 입력, active generation은 보호 대상이다. 생성된 Lua를 수작업으로 고치지 않는다.

---

## 6. Planned Changes

### Change 1 — 입력·역할·측정 기준 고정

**Purpose:** 로드맵의 과거 추정과 현재 코드를 분리하고 각 트랙의 실제 개선 기준을 정한다.

**Files:** §5의 대상과 기존 route/환경/검증 분류, `b/`, `g/`, `i/`, `_docs/refactor/`, `_docs/round3/`.

**Implementation Notes:**

1. 작업 시작 시 tracked/dirty/untracked/ignored 상태와 보호할 현재 입력을 기록한다. 기존 작업의 대용량 복제본을 또 만들지 않고, 변경할 소스와 필요한 입력만 실행 경계에 제공한다.
2. 자료마다 writer, reader, current/accepted 참조, historical 재현 역할, 대체 저장 위치를 확인한다. `b/g/i`는 receipt뿐 아니라 `system-temp`·checkout·test-output을 포함하므로 디렉터리 이름으로 일괄 분류하지 않는다.
3. 각 변경에 아래 표의 직접 지표를 선택한다. 주지표 하나와 필요한 보조지표까지만 기본 측정하며, 모든 변경에 ZIP·cold/warm·heap·peak memory·latency 측정을 요구하지 않는다.
4. 시간 지표를 선택한 경우에만 같은 입력·환경의 짧은 반복 표본으로 변동폭을 구한다. 메모리 지표를 선택하지 않았다면 table 수·파일 크기를 실제 PZ heap 절감으로 환산하지 않는다. 실제 게임 기능 관찰과 성능 계측은 구별한다.
5. Git common directory와 worktree 경로를 확인한 뒤 loose/pack/LFS 저장량을 각각 조사한다. 로드맵의 `.git 5.1GB / LFS 2GB`는 재확인 전까지 과거 관찰값으로만 둔다.
6. 줄이려는 비용·기준 입력·관련 검사만 기존 실행 기록에 짧게 남긴다. 단순 중복 공유·set 조회·국소 복사 축소는 사전 수치 하한이나 별도 benchmark 없이 구현할 수 있다. 새 loader·저장 형식·설치 계약·복구 경로를 추가할 때만 구현 전에 최소 개선 기준과 허용 회귀를 정한다. 별도 machine gate/authority 파일은 만들지 않는다. 수치 하한을 선택한 경우 결과를 본 뒤 유리하게 낮추지 않는다.

**변경별 채택/no-op 기준:**

| 대상 | 기본 직접 지표 | 채택 기준 — 단순 변경은 사전 수치 하한 불필요 |
| --- | --- | --- |
| R / Change 2 | 대표 표본의 압축·중복 제거 후 보관 bytes | 기존 도구 실험은 overhead 포함 효과와 복원·reader 소비로 판단. 새 저장 형식 개발을 선택할 때만 사전 수치 하한 적용 |
| D / Change 3·4 | 고유 table 수, 보조로 Lua bytes | 동일 의미·공유 오염 없음·실제 중복 감소·과도한 복잡도 증가 없음. table은 중복 계수하지 않음. 설치 계약 확장 시에만 사전 개선 하한 적용 |
| B / Change 5 | 탐색·복사 횟수 또는 해당 구간 시간·peak memory 중 하나 | 단순 개선은 불필요한 순회·복사 감소와 입력 불변성으로 판단 가능. 시간/메모리 개선을 주장할 때만 해당 지표 확인 |
| U / Change 6 | 같은 item의 검색/toggle당 정적 model·무관한 child 재생성 횟수 | 해당 대표 동작에서 불필요한 정적 model 재생성 0회와 무관한 section child 제거·생성 0회. 변경 section의 필요한 갱신은 제외 |
| S / Change 8 | 실제 이중 구현 또는 별도 유지 경로 수 | 적어도 하나의 확인된 이중 구현/유지 경로를 없애고 동등한 새 경로를 만들지 않음. 정리할 중복이 없으면 no-op |
| Change 7의 ignore/attributes·역할 조사 | 재누적 방지·effective 속성·보존 처분 | 성능 하한 적용 대상이 아님. 확인된 캐시 ignore 또는 동일 속성의 단순화가 없으면 no-op |
| Change 9 | dedup 이후 남은 최초 로드 비용 중 한 지표 | table/loaded bytes/시간/메모리 중 하나의 최소 개선과 새 파일·계약·실패점 비용을 정식 진입 전에 고정 |

Change 1은 독립 측정 회차나 공통 착수 Gate가 아니다. 각 변경에서 필요한 입력 확인만 먼저 하고 구현·비교를 이어간다. 단순 개선은 수치 하한 미정으로 차단하지 않는다. 새 저장·설치·로딩 경계를 도입하는 후보만 해당 기준을 먼저 확정한다. 독립 트랙은 다른 트랙의 준비를 기다리지 않는다.

사전 수치 하한을 적용한 후보만 하한 미달 시 no-op으로 처분한다. 단순 변경은 위 표의 정확성·실제 비용 감소·복잡도 기준으로 판단한다. 새 loader·contract member·복구 경로·실패점이 생기면 그 수와 유지 책임을 함께 기록한다. 같은 효과를 더 단순한 표현으로 얻을 수 있거나 새 유지비를 정당화할 직접 개선이 없으면 채택하지 않는다. 기존 두 파일 설치 단위 등 단순한 경계를 넘는 변화는 작은 byte 절감만으로 정당화하지 않는다. 정확성·호환성 회귀는 절감량과 상쇄하지 않으며, 수정해 재검증하거나 해당 후보를 철회한다.

**Validation:** 역할 미확인 항목은 보존한다. 후속 변경마다 동일 의미 입력의 Before/After와 실제 명령·exit·실행 환경을 연결한다. 새로운 일반 검증 체계나 전수 hash 증명 의무를 만들지 않는다.

### Change 2 — expression/evidence 저장 구조의 비파괴 후보

**Purpose:** 대표 자료의 작은 보관·복원 실험으로 저장 구조 개선의 타당성을 판단한다. R 트랙 밖의 구현 진행을 차단하지 않는다.

**이번 결과의 범위:** 대형 expression/evidence 자료는 이번 회차에서 보관 타당성 조사까지다. r1~r6 내부 중복의 정규화나 원본 제거를 완료 목표로 삼지 않는다. 실제 저장소 경량화 적용은 Change 7의 역할이 확인된 재생성 가능한 캐시·임시 출력에 한정하며, 보호 자료의 저장량 감소와 구분해 보고한다. 표본 실험만 끝났다면 대형 자료 경량화 완료라고 하지 않는다.

**Files:** `content_addressed_archive.py`, `lifecycle_delta_codec.py`, expression successors와 선택된 historical evidence.

**Implementation Notes:**

1. r1~r5의 원래 위치와 r6의 adoption/member를 유지한 상태로 대표 자료만 후보 저장·복원한다. 시작 전에 표본 목록·최대 입력 bytes·임시 디스크 사용 상한을 정하고 r1~r6 전량 복제를 기본 실험으로 삼지 않는다. reader 검사는 선택한 자료의 필요한 참조 범위만 준비하며 활성 reader는 바꾸지 않는다.
2. 기존 파일 단위 CAS에서 완전히 같은 bytes가 차지하는 비율, 압축 효과, revision 사이 부분 중복을 구별한다. 내용이 조금 다른 수백 MB JSON은 현재 CAS에서 하나의 object로 공유되지 않는다.
3. 파일 단위 표본의 결과로 공통 evidence object·revision mapping·chunk 저장의 필요성과 예상 이득까지만 판단한다. 새로운 CAS/chunk codec 개발은 이 작은 실험의 자동 후속이 아니다. 이득이 충분하고 변경 범위·기준을 별도로 구체화한 경우에만 후속 후보로 남긴다. 기존 `lifecycle_delta_codec`는 lifecycle manifest용이므로 임의의 expression JSON에 바로 적용하지 않는다.
4. LFS 파일은 Git pointer OID/size와 실제 payload의 일치를 확인해 보관한다. `tracked_git_blob`로 pointer만 보관한 결과를 r6 payload 복원 성공으로 보고하지 않는다. dirty tracked bytes도 HEAD blob으로 대체하지 않는다. 기존 도구로 payload를 안전하게 공급할 수 없는 표본은 제한 사항으로 기록하고 input domain 확장을 후속 후보로 분리한다.
5. 현재 CAS가 `dict[str, bytes]`를 사용하므로 정한 표본 상한을 넘기지 않는다. 실제 메모리 문제를 발견하지 않은 상태에서 streaming archive framework를 개발하지 않는다. 큰 범위에서 bounded-memory 변경이 필요하면 범위·효과를 별도 산정하고 이번 실험은 중단 또는 축소한다.
6. manifest는 원래 logical path와 source identity를 보존하는 보관 metadata로 한정한다. 활성 consumer는 materialized 입력을 계속 소비하며, historical 복원은 명시적인 요청 경로로 유지한다.

**Validation:** 기본은 선택한 표본의 압축 크기·복원·기존 reader 소비다. CAS 코드를 실제 변경한 경우에만 해당 create/verify/restore·경로 이탈·object 손상/누락 테스트를 추가 실행한다. 이는 보관 변경에 필요한 복원 검사이며 전체 생태계 재봉인이 아니다. 원본 삭제가 없는 단계는 “표본 저장 후보 가능/불가/입력 제한”으로 보고하며 실제 디스크 절감 완료라고 하지 않는다. 후보와 원본의 동시 보관으로 늘어난 임시 용량도 기록한다.

### Change 3 — EvolvedRecipe 반복 표현 공통화

**Purpose:** 2,203 relation의 반복 locale/conditions 테이블을 줄인다.

**Files:** `domains/layer4/evolved_recipe.py::render_runtime`, generated `IrisEvolvedRecipeLookup.lua`, `Iris/tooling/tests/test_evolved_recipe.py`.

**Implementation Notes:**

1. offline producer에서 동일 conditions, target label, action, display의 정확한 값 tuple을 정규화하고 안정된 순서로 공유 상수를 출력한다.
2. relation ID, source FullType, target/food type, role, action key, canonical ordinal과 각 relation의 구별은 유지한다. 공유는 내용이 동일한 내부 값에 한정한다.
3. `.get(fullType)`의 `available` / `verified_empty` / `fault`와 source identity 검사, `relationCount`·`fullTypeCount`를 보존한다.
4. relation 소비자의 mutation 여부를 먼저 확인한다. 공유 table을 readonly 내부 값으로 다룰 수 없는 경계에는 소유권을 분리한다. 단순 shared reference 도입으로 다른 item 결과가 오염되면 채택하지 않는다.
5. 전체 record를 로드 후 다시 펼치는 중간 테이블을 만들지 않는다. Lua 문자열 interning이 이미 제공하는 이득과 새로 줄어드는 table 할당을 구분한다.

**Validation:** 기존 owner/projection 및 실제 Lua 조회 경로를 확장하여 모든 relation·양 언어·순서의 동등성, 잘못된 FullType, 공유 오염을 확인한다. §7의 기존 `lua -e` 블록과 interaction harness를 연결한다. 생성 table 수와 Lua bytes를 Change 1의 기준에 비교한다. cold/warm 시간·PZ heap 계측은 그 효과를 별도로 주장하거나 구체적 회귀가 발견된 경우에만 추가한다. owner 사실은 재판정하지 않는다.

### Change 4 — Tooltip base/variant 중복 제거

**Purpose:** 기존 opening 선택 의미를 보존하면서 두 Lua 파일이 중복 저장하는 base와 공통 행을 공유한다.

**Files:** `tooltip_static_data_projection`의 producer/serializer/parser/install, `IrisTooltipStaticDataLookup.lua`, Tooltip tests/harness, `Layer3PackageProjection.psm1`.

**Implementation Notes:**

1. 기본안은 기존 두 파일 설치 단위를 유지하면서 producer가 동일 행 배열·문자열을 공유 상수로 출력하는 방식이다. 행 조립·유효 후보 선택은 계속 offline producer가 소유한다.
2. base를 참조로 바꾸더라도 잘못 섞인 StaticData와 Variants를 거부하는 기존 계약을 보존한다. `entry.base` 제거와 `sameRows` 삭제만으로 끝내지 않는다. 정상 설치의 owner 검증과 runtime의 stale pair 거부를 함께 설계한다.
3. runtime에 S1~S4 의미를 해석하는 prefix+delta 합성기를 추가하지 않는다. 최종 KO/EN view와 그 참조 관계를 offline에서 확정하고 runtime은 선택·검증만 수행한다.
4. `read_static_data`는 현재 Lua literal 형식의 parser이므로 serializer만 바꾸면 install과 테스트가 깨질 수 있다. parser/producer API, consumer, candidate owner를 같은 변경 단위로 맞춘다.
5. 과거 recipe 전용 `project_recipe_variants`의 `without_recipe`와 후보용 `project_interaction_variants`의 recipe/rightclick/evolved_recipe 세 종류를 모두 유지한다.
6. `Lookup.get/open`, locale 제한, 빈 행·잘못된 배열·중복 ID 거부, 오류 시 Iris 침묵, opening당 단일 선택과 locale 변경 시 선택 identity 유지를 보존한다. Alt·한 역할 한 줄·최대 네 줄·`fit_failed` 의미도 유지한다.
7. 처음에는 `install.FILES`와 `Get-IrisTooltipOwner`의 두 파일 제한 안에서 해결한다. 파일 추가가 필요하다는 발견은 Change 9의 **설계 이관 대기**로 기록하며 즉시 청크 구현이나 installer 확장을 시작하지 않는다. 두 파일 안의 대안을 적용하거나 해당 부분을 no-op으로 닫고, 청크의 정식 진입은 dedup 결과 평가 후 별도로 결정한다.

**Validation:** 기존 serialization/projection, 공급→install→package 통합, `tooltip_static_data_runtime_harness.lua`를 사용한다. base/variant 불일치, 잘못된 참조, locale 전환, empty/fault, 선택 분포를 바꾸는 중복 제거 여부와 전체 public 행·순서를 검사한다. 문구를 줄여 얻은 크기 감소는 수락하지 않는다.

### Change 5 — DVF 생산기의 중첩 탐색·전체 복사 축소

**Purpose:** source/fact 의미를 바꾸지 않고 Recovery의 불필요한 탐색·복사 비용을 줄이며 선택한 직접 지표로 효과를 확인한다.

**Files:** `recovery_expression.py::normalize/produce/prepare`, `recovery.py::acquisition_content/acquisition_successor` 및 실제 profiling으로 확인된 복사 지점.

**Implementation Notes:**

1. `regular['facts']`의 provenance ref를 한 번 순회해 set으로 모은 뒤 provenance mapping을 membership으로 필터링한다. 현재 provenance×facts 재탐색을 facts의 ref 수 + provenance 수에 비례하는 처리로 바꾼다.
2. `deepcopy(inputs)` 대신 facts/provenance의 readonly 공유와 실제 수정되는 `applications`, bindings, required axes/result/fact refs 가지의 복사를 분리한다. downstream `expression.produce`의 mutation 여부까지 확인한 뒤 공유한다.
3. `normalize`에서 여러 fact가 같은 provenance를 참조하면 불변 payload를 매번 복사하지 않도록 한다. canonical sorting과 identity 계산 입력을 유지한다.
4. acquisition의 authority/binding 정규화는 변경되는 header·row만 복사하는 방식으로 검토한다. baseline acquisition, results/traces/provenance가 다음 호출에서 오염되지 않아야 한다.
5. 단순히 모든 `deepcopy`를 얕은 복사로 치환하지 않는다. 복사 제거 효과가 미미하거나 mutation 소유권이 불명확한 곳은 유지한다.

**Validation:** 기존 recovery 전용 계약으로 facts/provenance/qualifier scope, expanded/compact refs, omission/unresolved, acquisition 의미 보존을 확인한다. 같은 입력 반복 호출과 호출 순서 변경에서 baseline 오염이 없는지 검사한다. Change 1에서 고른 탐색·복사 횟수 또는 생산 구간 시간·peak memory 중 하나를 비교하며 장시간 acceptance 전체 실행 시간을 producer 속도로 대체하지 않는다. 두 지표의 동시 계측은 별도 근거가 있을 때만 수행한다.

### Change 6 — Browser 상세의 국소 갱신

**Purpose:** 상세 내부 검색·toggle마다 설명과 상호작용 전체를 재생성하는 비용을 줄인다.

**Files:** `IrisBrowserDetail.lua`, `IrisDetailChildren.lua`, `IrisBrowserInteractionRenderer.lua`, `IrisBrowserInteractionProjection.lua`, `IrisBrowserInteractionState.lua`, 관련 Detail model.

**Implementation Notes:**

1. 기존 `showDetail` 재사용 분기는 유지하고, 상세 내부 검색·상호작용 toggle·target group toggle을 각각 영향받는 section 갱신으로 연결한다.
2. 정적 identity/설명, 상호작용 목록, 동적 요구조건의 수명을 분리한다. 정적 model은 FullType·locale·실제 model/product revision·generation이 같은 동안만 재사용한다.
3. 변경 section 아래 child 위치와 전체 content height를 다시 계산하고 현재 scroll을 유효 범위로 제한한다. persistent search entry의 focus, 입력·IME 상태, suppress flag와 visibility를 유지한다.
4. item/locale/revision 변경, 폭·폰트 변경 등 전체 layout 무효화 조건에서는 기존 전체 rebuild를 사용한다. 새 부분 갱신 실패를 stale 설명 유지로 숨기지 않는다.
5. 플레이어 skill·inventory·learned recipe 등 요구조건 상태는 기존 refresh 시점에 다시 읽는다. 모델 재사용을 위해 동적 상태를 freeze하거나 game state를 변경하지 않는다.

6. **B→Menu 반영 경로:** 현재 `product_projection.MENU_RUNTIME` 밖의 InteractionRenderer/Projection/State 및 기존 공유 Lua는 retained B media 보호 대상일 수 있다. 먼저 실제 변경 파일과 목록을 대조한다. 해당 파일을 바꾸면 기존 B 후보 생산 경로로 최종 공유 Lua를 포함한 새 ZIP과 owner를 만들고, Menu는 그 정확한 ZIP path/hash/owner를 명시적 입력으로 소비한다. 변경 EvolvedRecipe/Tooltip 자료도 같은 후보에 묶을 수 있다. guard를 끄거나 `MENU_RUNTIME`을 무조건 확장하지 않는다. 기존 B 후보 계약이 이 변경을 수용하지 못하면 해당 통합만 blocked로 남기고 별도 owner 판단이 필요한 이유를 기록한다. 무관한 트랙은 계속 진행한다. accepted/current/live 전환은 수행하지 않는다.

**Validation:** 기존 Browser state/search·Detail ViewModel·single-pass 계약과 UI harness에 실제 변경 경로만 추가한다. 같은 item의 상세 검색/toggle에서 정적 model과 무관한 child의 재생성이 줄어드는지 측정한다. 선택 전환·KO/EN·스크롤·focus·요구조건 변화·product fault를 확인하고 실제 PZ에서 입력 반응과 표시를 관찰한다.

### Change 7 — 저장소 정리의 조건부 적용

**Purpose:** 역할이 확인된 캐시·historical 자료만 정리하고 반복 누적을 줄인다.

**Files:** `.gitignore`, `.gitattributes`, quality review, `b/g/i`, `_docs/refactor`, `_docs/round3`, 비활성 generation 후보.

**Implementation Notes:**

1. `/Iris/tooling/.tmp/uv-cache/`처럼 확인한 캐시에만 ignore를 추가한다. `.tmp` 전체를 숨기기 전에 그 안의 작업 산출물 역할을 확인한다. ignore는 디스크 삭제가 아니며 기존 tracked 파일을 untrack하지 않는다.
2. quality review 파일별로 현재 검수 입력/결과, historical 근거, 재생성 가능한 임시 dump를 구분한다. composition의 `blocks.json`·`descriptions.json`은 이 정리 대상에서 제외한다.
3. receipt 복사본은 current 환경·closeout·재현 reader의 참조를 조사하고 Change 2의 복원 가능한 보관 방식이 실제 적용 가능한 경우에만 위치 변경 후보로 삼는다. 원 receipt나 유일한 증거를 삭제하지 않는다.
4. 비활성 generation은 pointer 외 descriptor·테스트 fixture·baseline·historical 복원 참조도 확인한다. 이동이 현재 경로 소비를 깨면 보관 유지로 닫는다. 패키지 절감 효과를 주장하지 않는다.
5. **이번에 실제 정리할 수 있는 대상:** `/Iris/tooling/.tmp/uv-cache/`의 재생성 가능한 캐시, 이번 실행이 만든 임시 stage/실패 checkout, `quality_review`에서 current 검수·근거·유일한 기록이 아님이 확인된 재생성 가능한 dump다. 후보 경로라는 이유만으로 전부 삭제하지 않는다. 대상별 생성 주체·현재 reader 부재·재생성 방법·보존 제외 이유를 한 목록에 남기고, 열린 작업에서 사용 중이지 않은 정확한 경로만 정리한다. Windows에서는 실제 절대 경로와 reparse 여부를 확인하고 허용 디렉터리 밖으로 나가는 대상을 거부한다. 별도 전체 archive/복원 Gate는 캐시 삭제에 요구하지 않는다. 역할이 불명확한 기존 사용자 자료는 보존한다. historical/authority 자료의 이동·원본 제거는 별도 보존 처분·복원 조건이 필요한 후속 범위이며 r1~r5, r6 audit, 보호 composition 파일은 계속 보존한다. 이번 계획 수정 자체로 삭제를 실행하지 않는다.
6. `.gitattributes`는 순서·범위·override를 포함한 effective `filter/diff/merge/text/eol`이 같은 경우만 단순화한다. 기존 LFS 또는 `-text` 범위를 바꾸는 wildcard 묶기는 제외한다. 속성 정리에 `git add --renormalize`를 섞지 않는다.
   현재 매칭 파일이 없는 규칙은 `git check-attr`의 현재 결과만으로 삭제하지 않고 기본 유지한다. 미래 생성 경로·historical 복원 경로까지 용도가 폐기되었음을 확인한 별도 처분이 있을 때만 제거 후보로 삼는다.
7. `_archive/registry.zip`은 이미 결정된 보관 결과다. `_dev`는 `run_pz_core_refactor_harness.ps1` 등의 consumer를 조사하며 개발 harness라는 이유만으로 제거하지 않는다.

**Validation:** ignore 대상/비대상에 `git check-ignore` 결과를 확인하고 attributes는 대상·인접 경로의 `git check-attr` 결과를 비교한다. 보관 위치가 바뀌면 기존 reader/restore 계약과 legacy/product package 경로를 검사한다. `.git` 분석 결과는 원인·가능한 별도 조치까지만 보고한다.

### Change 8 — 완료된 리팩토링을 제외한 구조 정리

**Purpose:** 남아 있는 실제 코드 중복과 유지비만 줄인다.

**Files:** legacy tools, `iris_tooling/build`, `domains/layer3/recovery*`, source inventory와 테스트 실행 안내.

**Implementation Notes:**

1. legacy tree와 installed package의 import/CLI/dynamic loader/검증 consumer를 연결해 실제 이중 구현, 호환 adapter, historical writer를 구분한다. `compose_layer3_*` adapter와 `common/repository_context` 재수출은 중복 본체로 세지 않는다.
2. 기존 inventory 도구와 producer source 목록을 사용하고, 호출 계약이 같은 반복 runner만 공통 함수로 줄인다. 명령 이름·인자·cwd·exit·오류 처리·출력 위치는 유지한다.
3. 이미 분리된 recovery source/claims/question/phrase 모듈은 재분리하지 않는다. 순수 표·vocabulary가 유지보수 부담으로 남은 경우에만 데이터 분리를 검토한다. 실행 규칙·source-bound predicate·검토 판정까지 임의 JSON으로 옮기지 않는다.
4. 새 data resource가 필요한 경우 wheel 포함, 명시적 repository context, loader 검증, producer source inventory를 함께 갱신한다. 같은 내용을 Python과 JSON 양쪽에 유지하지 않는다.
5. 테스트 위치는 유지하고 root pytest / tooling pytest / validation tests / 전용 producer 경로의 실행 책임과 누락 여부만 정리한다. 분류되지 않은 실제 검사만 기존 owner 체계에서 보완한다.

**Validation:** 실제 영향받는 CLI/context/import 및 dedicated/current route 검사만 실행한다. 일반 pytest 미수집을 이유로 source classification을 완화하지 않는다. 남은 대상이 없거나 효과가 없으면 근거와 함께 no-op으로 닫는다.

### Change 9 — 중복 제거 후에만 lazy chunk 도입 판단

**Purpose:** Change 3·4 이후에도 최초 로드 비용이 큰 경우에만 필요한 데이터의 부분 로딩을 도입한다.

**Files:** 해당 producer/lookup, 생성 index/chunk, Tooltip install/owner, package projection.

**Implementation Notes:**

1. **정식 진입:** Change 3·4의 적용 또는 no-op 결과를 평가한 뒤 남은 최초 로드 비용을 확인하고, Change 1의 기준을 고정한 후 제한된 chunk 후보를 만든다. 크기만으로 자동 착수하지 않는다. **설계 이관 대기:** Change 4 중 파일 추가 필요가 발견된 경우에는 제약만 기록한다. 이 기록은 정식 진입 조건을 충족하거나 패키지 계약 확장을 허용한 것으로 취급하지 않는다.
2. producer가 FullType→chunk index와 안정된 partition을 생성한다. 작은 index와 해당 chunk만 require하고, 정상 조회와 실패 결과의 수명을 명시한다. 전체 scan이나 사용자 선택 예측은 추가하지 않는다.
3. Tooltip opening당 단일 bilingual identity, EvolvedRecipe relation 순서, unsupported/fault 침묵을 유지한다. 손상된 chunk를 legacy·다른 locale·stale global로 보충하지 않는다.
4. Tooltip은 현재 설치·검증이 두 파일로 고정되어 있으므로 파일 목록 계약·owner identity·install/rollback·package allowlist를 함께 확장해야 한다. 기존 Layer3 lazy lookup은 참고하되 해당 authority를 Tooltip에 재사용하지 않는다.
5. 파일 수·첫 접근 I/O·Kahlua 비용이 이득을 상쇄하면 단일 모듈을 유지한다. 청크화 보류는 Change 3·4의 완료를 막지 않는다.

**Validation:** 최초 index-only 상태, 첫 item의 제한된 chunk load, 같은 chunk 재사용, missing/corrupt chunk 거부, 완전한 candidate install/restore/package를 확인한다. Change 1에서 정한 직접 지표 하나로 선행 결과와 비교하며, 실제 PZ에서는 조회·공존 동작을 관찰한다. PZ latency/heap 개선을 주장할 때만 그에 맞는 게임 계측을 추가한다.

### 실행 순서와 의존성

Change 1은 각 트랙에 필요한 입력·기준을 준비한다. 준비된 트랙은 다른 트랙의 조사 완료를 기다리지 않는다.

- R: `Change 1 → Change 2 대표 표본 실험`. Change 7의 자료 이동은 역할 분류·복원 조건을 충족할 때만 진행하며, 캐시 ignore는 해당 분류만 준비되면 가능하다.
- D: `Change 1 → Change 3 → Change 4`. 이는 핵심 최적화의 우선순위이며 Change 2 결과에 의존하지 않는다.
- B/U: Change 5·6은 각자의 기준이 준비되면 별도 변경 단위로 진행한다. 다른 트랙의 PASS를 재사용하지 않는다.
- S: Change 8은 잔여 중복이 확인된 곳에만 적용한다.
- 청크: Change 9는 Change 3·4의 결과 평가 후 정식 진입한다. Change 4의 이관 대기 기록만으로 실행하지 않는다.

각 변경은 입력·소스 수정·필요한 생성물·관련 검증을 하나의 검토 가능한 단위로 남긴다. 자료 정리와 런타임 표현 변경을 한꺼번에 적용하지 않는다.

Change 번호는 별도 승인·PR·Gate 횟수가 아니다. 실제 의존성에 따라 독립 변경의 순서를 조정하고, 데이터 공유와 해당 consumer 변경을 한 검증 묶음으로 처리할 수 있다. Change 5·6·9를 이번에 완료하면 그 범위는 후속 최적화에서 반복하지 않는다.

---

## 7. Validation Plan

### Automated Validation

#### 최소 실행 정책

**신규 정규 Gate·validator·승인 단계는 0개, repository full gate는 기본 0회**다. 기존 제품 계약이 요구하거나 runner/분류/전체 실행 경로를 실제 변경한 경우에만 해당 기존 Gate를 최종 묶음에서 실행한다. 각 Change와 아래 명령 목록은 매번 전부 실행하는 체크리스트가 아니다. 실행 범위·횟수는 이 절을 따르며, 선택한 제품 계약 내부의 필수 assertion·실패 주입·결정성 검사는 유지한다.

| 검증 | 최소 실행 방식 |
| --- | --- |
| Before 및 비용 비교 | 동일 입력·구현·환경·검사 범위의 기존 결과 재사용. 없을 때만 필요한 부분을 한 번 확보; 별도 전체 기준선 회차 없음 |
| EvolvedRecipe/Tooltip/Browser | 중간에는 바뀐 동작의 기존 node만 선택. 최종 관련 변경을 묶어 영향받은 focused 검사 1회 |
| B→Menu/install/package | 공유 Lua·표현·parser·설치 변경을 같은 최종 후보로 모아 필요한 통합 1회. 한 node 내부의 필수 반복 생산은 유지 |
| Recovery | 최종 생산기 묶음에서 필요한 후보 생산·전용 계약·의미/입력 불변성 확인 1회. 동일 Before가 유효하면 재생산하지 않음 |
| Lua 문법/harness | 실제 변경한 source와 후보 stage를 정확한 기존 문법 명령으로 검사. 통합 검사가 같은 파일·경로에서 수행한 동일 검사는 중복 실행 생략 |
| 보관/캐시 | 표본은 선택 범위 복원·reader 소비 1회. CAS 코드 미변경이면 전체 archive suite 생략. 캐시는 대상 역할·경계 및 정리 결과만 확인 |
| CLI/구조/설정 | 실제 변경된 계약의 기존 node만 선택. 파일명·줄 수·추출 구조를 따라가는 테스트 추가 금지 |
| 실제 PZ | 최종 runtime 후보의 변경 동작을 한 세션에 묶어 관찰. 내부 추출마다 재실행하거나 변경하지 않은 표면의 전수 QA를 추가하지 않음 |

- 통합 결과가 같은 최종 subject의 동일 node/harness를 실제 포함하면 focused 검사 중복 실행을 대체한다. legacy와 product, 다른 입력·파일 세트는 같은 검사로 취급하지 않는다.
- 새 테스트는 기존 검사에 없는 mutation isolation, stale pair 거부, 부분 갱신 회귀 등 실제 변경 위험에만 추가하고 기존 fixture/helper를 사용한다. 테스트 수 축소를 위해 보호 조건을 삭제하지 않는다.
- 관련 코드·입력·환경 변경, 실패 수정 또는 누락된 위험이 있을 때만 해당 검사를 재실행한다. 통과 후 안심 목적의 확대·반복은 하지 않는다.
- 수집 단계가 계약을 따로 바꾸는 경우 외에는 별도 collect-only 회차를 추가하지 않는다. 기존 baseline 검증, 동일 후보의 패키지 검사, Origin 보존 확인은 가능한 한 같은 실행 흐름에서 처리한다.
- 차단·미검증은 해당 트랙과 실제 의존 변경에만 적용한다. 다른 트랙의 구현·검증·개별 완료를 막지 않으며, 실패·skip을 PASS로 바꾸지 않는다.

PowerShell과 실제 검증 Subject의 repository root를 기준으로 한다. Python은 `uv run ... python`으로 실행한다. 아래 Python 예시는 이 절의 non-editable 설치를 한 번 완료한 환경을 전제로 하며 모두 `--no-sync`로 실행한다. 설치·source 확인은 같은 최종 묶음에서 재사용하고 node마다 재설치하지 않는다. 아래는 **구현 후 적용할 기존 명령의 선택표**이며 이 계획 작성에서 실행한 PASS 목록이 아니다. 실제 변경에 해당하는 node만 선택하고, 모두 통과한 뒤 이유 없이 재실행하거나 범위를 확대하지 않는다.

검사 선택은 다음 순서로 한다.

1. 변경한 producer/serializer/lookup의 입력·출력·실패·소유권 계약을 직접 검사하는 기존 focused node를 먼저 고른다. 전체 relation/public row의 KO/EN·순서 동등성은 그대로 확인하되, 이를 위해 upstream corpus 전체를 여러 번 생산할 필요는 없다.
2. 기존 node가 필요한 계약과 무관한 반복 생산을 한꺼번에 수행하면 같은 테스트 파일의 helper를 재사용해 좁은 focused node를 보완한다. 기존 통합 node·필수 assertion·required runner/ID는 제거하거나 약화하지 않는다. 새 정규 validator나 별도 authority를 만들지 않는다.
3. parser/install member/owner/package 또는 B→C 인계 경계가 실제로 바뀔 때 해당 통합 node를 선택한다. 의미 있는 기존 필수 계약이 적용되는 경우에는 비용을 이유로 생략하지 않는다.
4. 특히 `test_s2_supply_and_owner_integration`은 supply·handoff·T2 반복 생산과 bytes 비교, 후보 직렬화·설치·package 검사를 포함한다. 이 node를 선택하면 그 기존 비용을 포함한 실행이라고 기록하며 “반복 생산 없는 focused 검사”라고 표현하지 않는다. 매 수정마다 실행하는 기본 명령으로 두지 않는다.
5. 새 표현의 의미·참조·순서 확인과 기존 작은 fixture의 determinism 검사는 유지한다. 추가 old/new raw-byte 동일성, full corpus 반복 생산·hash 증명·재봉인은 이 작업의 새 수락 요건이 아니다.

| 변경 | 기본 검증 경로 | 필수 확인 |
| --- | --- | --- |
| CAS/보관 | 선택 표본의 기존 create/verify/restore. 보관 코드 변경 시 `Iris/validation/artifacts/tests/test_content_addressed_archive.py`의 영향 node | 표본 복원·reader 소비, 코드 변경 시 corruption·missing·path escape 거부 |
| EvolvedRecipe | `Iris/tooling/tests/test_evolved_recipe.py::test_candidate_projection_is_deterministic_and_owner_traced`의 실제 Lua 블록 및 아래 interaction harness | owner 의미·정렬, 실제 generated lookup의 relation 동등성·aliasing |
| Tooltip | `Iris/tooling/tests/test_tooltip_t2_serialization.py`, `Iris/tooling/tests/test_tooltip_t2_projection.py::test_projection` / `test_reader_order`, 기존 Lua harness | 양 언어 행·base binding·선택 수명. install/package 변경 시에만 관련 통합 node 추가 |
| Recovery | `Iris/build/description/v2/tests/test_layer3_recovery.py`의 전용 실행 | 명시적 후보·installed identity, 의미·참조·입력 불변성 |
| Browser | `test_iris_detail_view_model_acceptance.py`, `test_iris_browser_state_selection_search_acceptance.py`, `test_iris_browser_single_pass_cache_contract.py` 중 영향 node | 부분 갱신·cache 무효화·상태·스크롤·동적 요구조건 |
| Package | `test_package_layer3_chunks_only_contract.py`, `test_layer3_product_integration.py` 중 영향 node | legacy/product 분기, 올바른 member만 패키징, 설치 복구 |
| 잔여 구조 | `Iris/tooling/tests/test_cli.py`, `test_repository_context.py`와 해당 source/runner 검사 | 호환 entrypoint·resource·분류 유지 |

일반 focused Python 검사의 예다. 각 줄은 해당 변경에 대한 선택지이며 전부 실행할 목록이 아니다. Tooltip 예시는 대형 supply 통합 node를 포함하지 않는다. 전체 generated 행의 semantic parity나 새 aliasing assertion은 구현 시 같은 기존 검사 경로에 보완한다.

```powershell
uv run --project .\Iris\tooling --no-sync python -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_evolved_recipe.py::test_candidate_projection_is_deterministic_and_owner_traced -q
uv run --project .\Iris\tooling --no-sync python -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_serialization.py .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_projection .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_reader_order -q
uv run --project .\Iris\tooling --no-sync python -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\validation\artifacts\tests\test_content_addressed_archive.py -q
```

`--noconftest` focused 결과는 repository source classification/full gate 통과를 뜻하지 않는다. 실제 변경이 분류·runner를 건드리면 해당 기존 검사를 별도로 사용한다.

**EvolvedRecipe의 Lua aliasing 경로:** 위 Python node는 현재도 generated `IrisEvolvedRecipeLookup.lua`를 `dofile`하는 `runtime_script`를 `subprocess.run(['lua', '-e', ...], check=True)`로 실행한다. Python 객체 비교만 수행하는 테스트가 아니다. 다만 현재 assertion이 새로운 공유 구조의 오염 방지를 이미 증명한다고 간주하지 않는다.

- 구현 시 같은 Lua 블록에 서로 다른 FullType이 같은 interned table을 사용하는 fixture, KO/EN 연속 조회, 동일 relation 재조회와 consumer 사용 전후의 내용 보존을 추가한다.
- 실제 소비 경계는 `Iris/test/lua/browser_interaction_density_acceptance_harness.lua`의 `IrisBrowserInteractionProjection` 경로에 연결한다. 현재 harness의 synthetic relation 검사에 generated fixture를 사용하는 case를 추가하고, UI 소유 결과를 수정해도 원본 공유 값·다른 FullType/locale가 오염되지 않는지 확인한다.
- 내부 readonly 값을 고의로 수정할 수 없도록 새 public 불변성 API를 만드는 것은 요구하지 않는다. 조사에서 mutable 반환을 약속한 경계가 발견되면 그 경계의 소유권 분리와 mutation isolation을 검사한다. 별도 Lua harness 파일을 새로 만드는 대신 기존 두 실행 경로를 사용한다.

해당 interaction harness를 보완한 경우의 기존 실행 형식은 아래와 같다. 현재 파일에는 새 aliasing case가 아직 없으며, 기존 파일을 한 번 실행한 것만으로 새 공유 구현 검증을 주장하지 않는다.

```powershell
lua .\Iris\test\lua\browser_interaction_density_acceptance_harness.lua .
```

Recovery는 non-editable installed package와 정확한 `IRIS_LAYER3_RECOVERY_CANDIDATE`를 준비한 뒤 아래 기존 계약을 실행한다. 최종 source 묶음이 확정되었을 때 실제 Subject에서 다음 설치를 한 번 수행하고, 기존 `installed_identity`와 source 대응 확인을 재사용한다. 실행 모듈이 그 Subject의 `Iris/tooling/.venv/Lib/site-packages`에 있어야 한다. 이후 후보 생산과 검사 모두 `--no-sync`를 사용해 editable 재동기화를 방지한다. source가 다시 바뀌면 관련 검사를 하기 전에 설치본을 갱신한다. 후보가 없는데 r6의 과거 receipt를 새 소스 검증으로 대체하지 않는다. 환경 변수는 실행 전에 저장하고 종료 후 복원한다.

```powershell
uv sync --project .\Iris\tooling --locked --no-editable --reinstall-package iris-tooling
if ($LASTEXITCODE -ne 0) { throw 'Non-editable subject installation failed' }
```

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_recovery.py -q
```

Tooltip와 Menu 동시 integration이 실제로 필요한 변경만 아래 명령을 사용한다. [기존 계획 §7](iris_refactoring_implementation_plan.md#7-validation-plan)의 명시적 corpus 입력, `IRIS_SHARED_MENU_VALIDATION`과 동일 프로세스 B→C 인계를 준비한다. 필요한 후보 환경을 준비하지 않은 명령을 독립적인 전체 gate처럼 실행하지 않는다. 이 묶음이 필수인 변경에서 기존 반복 생산·bytes assertion을 끄지 않으며, 필수가 아닌 변경에서는 더 좁은 검사 결과의 범위만 보고한다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\iris-lightweighting-integration -x -q -s
```

Lua 변경 시 정확한 관련 문법 명령을 실행한다. 기본 Roots는 runtime과 기존 build package이므로 새 후보 stage의 파일도 포함되는지 확인하고, stage가 다르면 같은 도구의 Roots로 별도 검사한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

repository full gate가 실제로 필요한 변경은 기존 `invoke_repository_tests.ps1` / `run_repository_tests.py`의 환경 receipt·명시적 commit·외부 disposable checkout 요구를 따른다. 현재 dirty working tree를 임의 commit하거나 clean이라고 주장하여 진입 조건을 우회하지 않는다. Run A/B+comparator는 기존 적용 계약이 요구하는 경우에만 실행한다.

통과 판정은 **관련 명령 exit 0과 필요한 case의 실제 실행**에 한정한다. required tool·입력 누락, skip, 미관찰을 PASS로 바꾸지 않는다. 새 runtime 표현은 old/new Lua bytes가 달라지는 것이 정상이며, 의미·행·상태·순서 동등성과 결정적 새 출력으로 검증한다. 기존 owner가 요구하는 입력/member hash 검사는 보존하되 추가 전수 동일성 증명을 만들지 않는다.

### Manual Validation

아래 목록은 변경 동작에 해당하는 관찰 선택지다. 최종 후보 한 세션에서 필요한 항목만 확인하고, 미변경 동작의 별도 재수락이나 전수 수동 검토를 요구하지 않는다. source와 후보 ZIP이 서로 다르면 관찰한 쪽의 결과만 주장한다.

- 동일 후보로 KO/EN Alt 열기·닫기, item 전환, opening 중 locale 변경, recipe/rightclick/evolved_recipe 표시를 확인한다. 최대 네 줄과 `fit_failed` 처리를 확인한다.
- Browser 상세 내부 검색·IME·focus·펼치기/접기·긴 목록·스크롤·item/locale/revision 전환을 확인한다. skill/inventory 등 상태 변화 후 요구조건이 갱신되는지 확인한다.
- Lua 데이터 공유·청크를 변경했다면 실제 PZ Kahlua에서 초기 조회와 재조회, Menu/Tooltip 공존을 확인한다. 일반 Lua harness의 성공으로 실제 게임 검증을 대신하지 않는다.
- package/install을 변경했다면 실제 검증한 후보 경로와 source 실행을 구별하고, 부분 설치 실패 뒤 원래 파일 세트로 복구되는지 확인한다.
- 저장 구조 후보는 선택한 historical 자료의 복원과 reader 소비를 확인하며 활성 자료를 옮겨 놓고 장애 여부를 시험하지 않는다.

### Validation Limits

- 이번 계획 작성은 문서 구조·경로·코드 근거 확인까지다. 성능 benchmark, 테스트 suite, 패키징, PZ는 미실행이다.
- 후속 구현에서도 외부 모드 전수, multiplayer, B42, 장시간 세션·모든 해상도/배율을 자동 포함하지 않는다.
- 일반 Lua의 메모리·시간 표본은 Kahlua 성능 보장이 아니다. 프로세스 peak memory와 Python allocator 측정도 구별한다.
- 실제 PZ 기능 관찰은 유지하되, heap/latency 개선을 주장하지 않는 데이터 공유·UI 재생성 축소에 별도 PZ profiler 환경을 의무화하지 않는다. 선택하지 않은 성능 지표는 미측정으로 남긴다.
- 원본을 유지한 archive 후보는 순 working tree 용량을 줄이지 않는다. 별도 보존 처분 없이 원본 제거 절감량을 성과에 합산하지 않는다.
- Java/Gradle 및 JS/TS 변경은 이 계획에 없다. 범위가 별도로 추가될 때 사용자 지정 `.\gradlew test`, `pnpm biome check .`를 적용한다.

---

## 8. Risk Surface Touch

### Authority Surface

표현 owner·source 판정은 유지한다. 보관 형식·producer source inventory·candidate member/파일 목록을 바꾸는 단계는 기존 ownership 계약에 영향을 줄 수 있다. 변경된 locator나 serialization을 새 사실 채택으로 취급하지 않는다.

### Runtime Behavior Surface

공유 table의 aliasing, cold load, lookup 오류, Tooltip 선택 수명, Browser partial refresh와 cache 무효화에 닿는다. 공개 의미가 같더라도 런타임 검증이 필요하다.

### Compatibility Surface

Lua/Kahlua 문법·표준 API 차이, 기존 facade/CLI, literal parser, wheel resource, Windows 긴 경로·LFS·reparse point, package 두 파일 계약에 닿는다.

### Sealed Artifact Surface

r6 adoption와 그 member, accepted/current corpus·receipt 외에 기존 repository lightweighting의 terminal subject·W10·final measurements·adoption/archive/removal authority도 보호한다. 특히 `Iris/validation/clean_checkout/authority/iris_current_historical_lightweighting_adoption_v1.json`, `Iris/validation/clean_checkout/authority/iris_historical_archive_v1.json`, `Iris/validation/clean_checkout/authority/iris_historical_removal_v1.json`은 이번 최적화로 재작성하지 않는다.

현재 tree에 없는 `docs/iris_lightweighting_terminal_closeout.json`은 historical readpoint로만 식별하며, 이 계획에서 복원·대체·처분을 결정하지 않는다. 새 보관 후보·runtime 후보에 과거 terminal PASS를 승계하지 않고 이번 결과는 `docs/iris_runtime_build_storage_optimization_closeout.md`로 구별한다. 실제 자료 이동은 해당 대상의 기존 reader·복원 계약과 별도 처분에 종속된다.

### Public-Facing Output Surface

목표는 동일한 KO/EN 텍스트·순서·부재/실패·Tooltip 네 줄·상호작용 선택이다. 원문 축약이나 슬롯 재정렬을 최적화에 섞지 않는다. Browser 부분 갱신의 focus/scroll과 Tooltip opening 상태는 사용자에게 보이는 동작으로 다룬다.

---

## 9. Risk Analysis

### Architecture Risk

- CAS를 authority로 사용하거나 runtime에서 의미를 재구성하면 offline/runtime 경계를 훼손한다. producer가 의미를 확정하고 runtime은 읽기·선택·표시만 수행한다.
- 새 공통화가 이전 리팩토링의 adapter/context 소유권을 무너뜨릴 수 있다. 이미 완료된 분리는 유지하고 실제 중복만 제거한다.

### Runtime Risk

- 공유 table 수정이 다른 FullType/locale에 전파될 수 있다. consumer mutation 조사와 오염 검사를 선행한다.
- partial refresh로 동적 요구조건·높이·검색 focus가 stale해질 수 있다. 정적/동적 경계와 전체 무효화 조건을 명시한다.
- chunk 추가는 I/O와 require 실패점을 늘린다. dedup 후 측정 결과가 뒷받침될 때만 도입한다.

### Compatibility Risk

- Lua serializer 변경이 `read_static_data`와 두 파일 install/owner를 깨뜨릴 수 있다. producer/parser/consumer/package를 함께 수정한다.
- LFS pointer를 실체로 오인하거나 attributes 우선순위를 바꾸면 복원·입력 identity가 달라진다. 실제 payload와 effective attribute를 확인한다.
- Kahlua에는 일반 Lua와 다른 API 제약이 있다. 기존 `pairs` 기반 검증과 metatable 거부 등 방어를 유지한다.

### Regression Risk

- 복사 축소로 baseline을 오염시키거나 canonical order를 바꿀 수 있다. 입력 불변성과 다중 호출을 검사한다.
- “큰 파일/기본 pytest 미수집”만 보고 authority·전용 검증을 제거할 수 있다. 역할/consumer 조사와 최신 no-op 결정을 우선한다.
- 기존 CAS의 whole-file 보관은 절감이 작고 메모리 부담이 클 수 있다. 이를 실패로 숨기지 않고 후보 보류 근거로 기록한다.
- 대형 통합 node와 모든 지표 계측이 실제 최적화보다 커질 수 있다. 변경별 직접 지표와 검사 경계를 구현 전에 정하고, 필수 계약을 유지하는 좁은 검사를 우선한다.
- 사전 수치 하한을 적용한 후보에서 결과를 본 뒤 하한을 낮추면 채택 근거가 사라진다. 기준을 바꿔야 할 새 원인이 발견되면 기존 결과와 판단을 보존하고 새 범위·기준으로 구별한다. 이전 미달을 PASS로 바꾸지 않는다.

---

## 10. Rollback Plan

1. 구현은 트랙별 작은 변경 단위로 나누고 기존 dirty 변경과 구별한다. 실패 시 이번에 변경한 소스·후보 파일만 되돌리며 저장소 전체 reset/clean은 사용하지 않는다.
2. EvolvedRecipe/Tooltip은 이전 producer·lookup·generated file 세트·owner/manifest를 함께 복구한다. 서로 다른 버전의 StaticData/Variants를 혼합하지 않는다. 청크를 도입했다면 index와 chunks도 같은 설치 단위로 복원한다.
3. Browser는 부분 갱신 연결을 이전 full rebuild 경로로 복구한다. 잘못된 model 캐시를 유지한 채 렌더링만 돌리지 않는다.
4. Recovery는 후보 출력과 cache를 재사용하지 않고 해당 실행의 소스 변경을 되돌린다. adopted r6와 baseline은 처음부터 수정하지 않는다.
5. 보관 후보 단계에서는 원본이 유지된다. 이후 별도 처분으로 이동한 자료만 기존 restore 도구로 검증된 원래 logical path에 복구한다. 손상 archive를 덮어쓰거나 현재 자료 위로 강제 복원하지 않는다.
6. `.gitignore`/`.gitattributes`는 변경한 규칙만 복구한다. Git 이력·object 저장소는 이 계획에서 수정하지 않는다.
7. 검증 실패·BLOCKED와 수정 후 재실행은 각각 기록한다. rollback 성공이 실패했던 후보의 PASS가 되지는 않는다.
8. 과거 terminal closeout/adoption/처분 기록은 이번 rollback 대상도 아니다. 부재 documentary readpoint를 복구 작업에 끼워 넣지 않는다.

---

## 11. Governance Constraints

- [Philosophy.md](Philosophy.md)의 Hub & Spoke/SPI와 모듈 역할을 유지한다. Pulse가 Iris를 참조하거나 다른 spoke가 Iris를 직접 의존하게 만들지 않는다.
- PZ runtime은 Lua, offline 도구는 Python으로 유지한다. 정보 표시 외 game state 변경·권장·효율 평가를 추가하지 않는다.
- r1~r5 보관, r6 adoption/audit, composition의 현행 입력, 테스트 위치/ID 유지, registry archive 결정을 존중한다.
- 기존 repository lightweighting complete subject와 이번 최적화 subject를 구별한다. 과거 W10·terminal PASS·adoption 권한을 재사용하거나 부재 readpoint의 처분을 이 작업에서 재개하지 않는다.
- 사실·표현·Tooltip 조립·패키지·validation owner의 경계를 유지한다. 보관 metadata와 성능 보고서를 새로운 authority로 승격하지 않는다.
- 기존 owner의 필수 검사는 수행하되 추가 raw-byte 동일성 증명·전체 재생산·새 봉인을 자동 의무로 만들지 않는다. 2026-09-16의 검증 한계 기록을 과거로 소급 변경하지 않는다.
- 누락된 도구·입력은 BLOCKED, 미실행 게임 관찰은 미검증으로 기록한다. 정확한 관련 명령 exit 0 없이 PASS를 주장하지 않는다.
- 계획 작성 요청은 계획 작성까지의 범위다. 이 문서 존재만으로 물리적 삭제·current 전환·공개 배포에 대한 실행 지시가 생기지 않는다.

---

## 12. Expected Closeout State

후속 구현의 목표는 **선택한 실행 범위의 `complete`**다. 적용한 최적화와 기준 미달로 채택하지 않은 후보를 구별해 보고하며, no-op을 성능 개선 완료로 표시하지 않는다. 다음을 충족해야 한다.

- [ ] 변경에 필요한 입력·직접 지표·복잡도 판단과 적용/no-op/보류 목록을 기록했다. 사전 수치 하한은 새 저장·설치·로딩 경계를 도입하는 후보에만 적용한다.
- [ ] Change 2는 대형 자료의 보관 타당성 조사로 닫고 표본 실험을 실제 저장량 절감으로 표현하지 않는다. Change 7에서 실제 정리한 캐시·임시 출력만 별도 절감량으로 보고한다. 대상이 없거나 역할이 불명확하면 no-op/보존으로 남기며 R 미완료가 D/B/U를 막지 않는다.
- [ ] Change 3·4는 public 계약을 유지한 table 수·Lua bytes 기준으로 채택 여부가 결정되어 있다. 단순 공유는 실제 중복 감소·정확성·복잡도로 판단하며, 측정하지 않은 cold/warm·heap 절감을 주장하지 않는다.
- [ ] Change 5는 의미·입력 불변성과 선택한 탐색·복사 횟수 또는 생산 구간 시간·peak memory 기준으로 채택 여부가 결정되어 있다.
- [ ] Change 6은 실제 동작·상태 보존과 정적 model/무관한 child 재생성 기준으로 채택 여부가 결정되어 있다. 입력 지연율을 측정하지 않았다면 이를 수치 성과로 제시하지 않는다.
- [ ] Change 7·8·9는 각각 적용, 근거 있는 no-op, 조건 미충족 보류 중 하나로 닫혀 있다. 미적용을 구현 완료로 표시하지 않는다.
- [ ] §7에서 선택한 해당 자동 검사가 exit 0이고, 최종 runtime 변경 묶음에 필요한 실제 PZ 관찰을 수행했다. 동일 최종 subject의 통합 결과로 중복 검사를 대체한 범위를 기록한다. 검증한 source/후보 ZIP과 관찰 범위를 구별한다.
- [ ] 기존 dirty 작업과 protected authority를 보존하고 변경 단위별 rollback이 가능하다.
- [ ] 최종 결과에 선택한 직접 지표의 효과와 미측정 지표, 실제 명령·실패·수정·미검증 범위를 기록했다. 기존 terminal을 대체하지 않는 `docs/iris_runtime_build_storage_optimization_closeout.md`를 사용한다.

자동 검사만 끝나고 필요한 PZ 관찰이 남으면 `implemented_only`, 필수 도구·입력을 확보하지 못하면 해당 트랙은 `blocked`, 선택한 범위의 필수 변경·측정·수락이 일부 남으면 `partial`로 보고한다. 효과가 하한에 못 미쳐 후보를 철회한 no-op과 미검증·실패를 구별한다. 조건부 청크화·자료 이동의 근거 있는 보류는 다른 트랙 완료와 병기할 수 있다. 전체 범위가 미완료이면 트랙별 완료만 보고하고 전체 complete로 확대하지 않는다. Current 활성화·release·설명 품질 과제 완료는 이 계획의 closeout에 포함하지 않는다.
