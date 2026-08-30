# Iris Current 경로의 기능·책임 중심 명명 정합 Implementation Plan

> 상태: complete — 사용자 최종 범위인 재명명·파일 재배치·참조 갱신 완료 / 추가 검증 종료
>
> 작성일: 2026-08-30

> 최종 범위 변경: 사용자가 재명명·파일 재배치만 수행하도록 제한하고 검증을 종료했다. 아래 원 계획의 추가 생성·full gate·package·PZ 조건은 이번 좁혀진 완료 범위에 적용하지 않는다. 실제 결과는 closeout의 Final user-directed scope를 따른다.

> 이전 후속 실행 범위: 사용자가 인게임 검증을 제외한 재생성·전체 검사·설치 파일 생성을 요청했다. 해당 작업에 필요한 외부 경로 사용을 승인한 것으로 적용한다. 출력은 `C:/Users/MW/PZ-N` 한 루트(짧은 하위 경로)에 한정한다. 실제 입력은 current route가 지정한 `C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/t1-final`의 네 handoff/closeout 파일이며 read-only다. 새 Python 환경 및 실행 scratch는 위 출력 루트에 두고 원본 게임/설치/세이브에 접근하지 않는다. 이번 완료 범위에서 PZ 관찰은 제외하며 그 PASS를 주장하지 않는다.
>
> 개정: 비필수 gate 생략 및 필수 계약을 보존하는 최소 실행 검증; current-only/문서 locator·vocabulary·scope-lock 경계 유지; 구현 미착수
>
> 기준 로드맵: 사용자 제공 「Iris 작업 세션 중심 경로의 기능·책임 중심 명명 정합 로드맵」 integrated roadmap
>
> 양식: `docs/PLAN_TEMPLATE.md`의 12개 항목
>
> 검증 깊이: heavy의 필수 범위 유지 / 중간 focused 의무 0회 / 최종 통합 검증과 같은 subject의 evidence 재사용 우선
>
> 조사 시점 HEAD: `cc095398a273685f0e1c1216447d99927fe99316`

실행 이력: 2026-08-30 owner preapproval로 실행을 시작했다. 원 계획의 설계/검토 문구는 아래에 보존하며 실제 결과는 closeout 문서가 소유한다. 이 문서의 작성 완료와 naming migration의 완료는 별개다. 이번 작성에서는 코드·계약·generated payload·current route를 수정하지 않는다. 아래 파일 목록은 코드에서 확인한 초기 inventory이며, 전수 census나 최종 rename 승인 목록이 아니다. 실제 구현 시 Change 1–3에서 exact subject와 범위를 다시 결속한다.

---

## 1. Objective

Iris의 current durable path 중 실제 책임 대신 과거 작업 세션·단계·차수를 표현하는 이름을 기능·책임 중심으로 정렬한다. 이름과 함께 Lua `require`, installed Python import, generator output, package/install consumer, current route와 검증 결속을 같은 dependency cluster로 이동한다.

목표 결과는 다음과 같다.

1. 현재 기능의 위치를 찾기 위해 `T1/T2`, `Dn`, `round3`, `refactor`의 작업 순서를 알아야 하는 의존을 줄인다.
2. Historical evidence, one-off procedure, domain/version identity, supported compatibility와 current durable responsibility를 구분한다.
3. Generated Lua는 새 canonical filename으로 직접 재생성되며 current runtime/package가 그 파일을 소비한다.
4. 적용 대상마다 old→new 경로, 책임, producer/consumer, compatibility와 binding 판정이 남는다.
5. `broken_active_reference = 0`, `active_unintended_old_dependency = 0`을 선언한 범위에서 확인한다. Repository 전체의 old literal zero는 목표가 아니다.
6. 사용자에게 제공하는 fact, exact FullType, KO/EN 문자열·순서·중복 row와 Menu/Alt 표시 계약을 보존한다.

이번 작업은 기존 Semantic Source / Classification / Layer 3 / DVF / QG / Offline Tooling / Adoption / Runtime Compatibility / Install / Presentation / Package / Publish 책임을 옮기거나 재설계하지 않는다.

---

## 2. Scope

### 2.1 조사 및 구현 범위

- `Iris/media/lua/**`: current Lua module, generated static payload, direct/dynamic `require`와 compatibility facade.
- `Iris/tooling/**`: installed package, CLI dispatch, offline projection/readiness, tests와 fixture resolution.
- `Iris/build/**`: current owner input, generation/install 연결, current test wrapper. `baseline`이나 predecessor source라는 이름만으로 current 여부를 정하지 않는다.
- `Iris/test/**`, `Iris/validation/**`: recurring contract 검사, lifecycle harness, full-gate launcher, environment/source identity와 그 consumer.
- `Iris/_docs/authority/**`, `Iris/_docs/round3/**`, `Iris/_docs/refactor/**`: live contract/route와 historical evidence를 파일 또는 logical asset 단위로 분류한다.
- `Iris/tools/package_iris.ps1`, `tools/check_lua_syntax.ps1`, root test discovery 설정: Iris 경로를 실제로 소비하는 연결만 포함한다.
- `Iris/build/ENTRYPOINTS.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 및 current policy: current locator 설명에 필요한 부분만 포함한다.

Ignored/generated/untracked 파일도 producer 또는 current consumer가 읽는다면 조사한다. 다른 작업의 임시 checkout 복제본은 canonical source로 세지 않으며, 제외 경로와 이유를 기록한다. 외부 handoff·receipt는 current route가 가리키는 exact input만 검토 대상으로 삼고 외부 디렉터리 전체를 정리하지 않는다.

### 2.2 코드에서 확인한 초기 disposition

| 대상 | 확인한 실제 책임과 연결 | 초기 판정 |
|---|---|---|
| `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua` | `Lookup.get(fullType, locale)`가 exact key/명시 locale로 static payload를 지연 로드하고 선택 배열을 검증한다. `IrisAltTooltip.lua`가 require한다. | `current_recurring_function`; rename 후보. |
| `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua` | KO/EN 정적 배열. `tooltip_t2/serialization.py`의 `LUA_NAME`이 filename을 소유한다. | `current_supporting_contract_or_asset`; producer와 함께 이동. |
| `Iris/tooling/src/iris_tooling/domains/tooltip_t2/` | `contract.py`가 adopted handoff를 검증하고 `projection.py`/`serialization.py`가 고정 배열을 생성하며 `cli.py`가 build/finalize한다. | 현재 static projection owner. Package명 후보이며 receipt/finalizer lifecycle 이름과 구분. |
| `Iris/tooling/src/iris_tooling/domains/tooltip_t1/` | 현재 T2가 `contract`/`models`를 import한다. 동시에 human entrypoint는 T1 CLI를 lifecycle-bound로 규정한다. | Package 전체를 recurring으로 단정하지 않는다. Current supporting contract, 반복 소비 helper, lifecycle 절차를 분리 census. |
| `tooltip_t1/d2.py` | `audit.py`가 `HARNESS`, `PROJECTION_BUILDER`, `load_relation`을 import한다. 같은 파일에 `materialize`, 고정 direct-parent identity와 `finalize_bundle`이 있다. | `mixed_responsibility`; 통째로 `menu_relation.py`로 바꿔 해결했다고 하지 않는다. |
| `tooltip_t1/d5.py` | `audit.py`가 exact identity/disposition 관련 함수를 소비한다. 같은 파일에 `T1-D5`, 고정 predecessor, `run_census`, `run_reconcile`이 있다. | `mixed_responsibility`; current consumer를 가진다는 이유로 one-off 절차까지 reusable로 승격하지 않는다. |
| `Iris/_docs/round3/round3_run_contract_tests.py`와 `current_route_required_validations.json` | Current list/selection과 required-validation binding. `main()`은 `--class`를 `choices=["current"]`로 제한하고 historical reproduction은 `repository_local_route_retired`로 보고한다. | Live current-only surface. Current selector와 fail-closed contract만 successor에 보존하고 실제 companion closure를 함께 조사. Historical/diagnostic 정보는 evidence로만 유지. |
| `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json` | `test_iris_legacy_surface_acceptance.py`가 실제로 읽는 supported API baseline. | Historical origin + live supporting contract. 원본 evidence와 successor current projection 필요성을 분리 판정. |
| `Iris/test/run_residual_refactor_acceptance.ps1`와 Lua harness | `test_iris_residual_runtime_acceptance.py`가 wrapper를 호출한다. | Active consumer는 확인됨. Lifecycle/recurring applicability 및 지원 코드의 범위를 추가 확인한 뒤 이름 결정. |
| `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json` | 현재 immutable environment record의 path/hash locator. Launcher/common code가 읽는다. | Live supporting locator 후보. 가리키는 historical record 자체는 rename하지 않는다. |
| `docs/iris_tooltip_t1_display_contract_policy.md`, `Iris/_docs/authority/tooltip_t1/**` | Current authority manifest가 current이자 protected/additive-successor 대상으로 명시한다. | 옛 단계명처럼 보여도 단순 move 금지. 승인된 successor와 current locator 전환으로 처리. |

### Explicitly Out Of Scope

- 다른 Pulse 모듈의 naming, 제품 코드, 의존성 변경.
- Historical plan/review/walkthrough/receipt/closeout, archive logical path, immutable environment record의 일괄 rename·내용 재작성.
- One-off executable retirement, unused/legacy source 삭제, mixed-responsibility 파일의 대규모 분해.
- 이미 retired된 repository-local `historical / diagnostic / all` executable selector의 복원 및 별도 historical runner/replay mechanism 신설.
- Package format, validation membership/판정 의미, supported public API를 새로 설계하는 작업.
- Live game 설치, 기존 세이브 변경, Workshop/Publish/deployment 실행. 필요한 runtime smoke는 별도로 범위가 정해진 격리 설치본을 사용한다.

---

## 3. Non-Goals

- 새 정보, 추천, 효율 평가, 우열 비교 또는 tooltip 문장 개선을 추가하지 않는다.
- Layer 2/3/4 semantic contract, Classification / DVF / QG owner와 Recipe / Right-click의 동등한 관계를 바꾸지 않는다.
- Runtime 성능, FPS, cache 정책, Alt wrapping/layout 개선을 섞지 않는다.
- `Layer 2/3/4`, `PhaseInput`/`PhaseOutput`/`PhaseRunner`, schema/protocol version, generation ID, SHA-256, exact FullType, 실제 runtime session 개념을 작업 단계명으로 취급하지 않는다.
- Naming registry, global naming gate, 별도 proof/validation subsystem을 만들지 않는다.
- 과거 T1/T2/T3 또는 build/validation closeout을 재개방하거나 그 PASS를 새 subject에 귀속하지 않는다.
- Release/Workshop readiness, DVF freeze, Publish Boundary PASS, 모든 외부 모드 호환성을 주장하지 않는다.

---

## 4. Assumptions

### 4.1 현재 저장소 및 실행 전제

1. `docs/Philosophy.md`가 최상위 설계 기준이다. `Iris/AGENTS.md`에 따라 네 bootstrap 문서의 관련 항목을 확인했다.
2. Runtime owner는 Lua이며 offline build/validation implementation owner는 installed `iris_tooling` wheel이다. Caller cwd, `sys.path` 삽입 또는 description-tree predecessor copy를 새 fallback으로 사용하지 않는다.
3. Human command literal owner는 `Iris/build/ENTRYPOINTS.md`, machine navigation은 `Iris/_docs/authority/iris_current_route_index.json`이다. 이 계획은 새 command authority가 아니다.
4. 조사 시점 route에는 T1 `adopted/complete/OPEN/present`, T2 static staging `complete`, `runtime_adopted=true`가 기록되어 있다. 이는 기존 subject의 상태이며 naming successor의 검증 결과가 아니다.
5. 조사 중 아래 두 파일에 이 문서 작성자가 만들지 않은 변경이 확인됐다. 현재 HEAD만으로 이 working tree 전체를 clean baseline이라고 부르지 않는다.

| 기존 변경 | 구현 착수 시 처리 |
|---|---|
| `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua` | 수정·복원·덮어쓰기 금지. 착수 시 diff와 hash를 다시 기록하고 통합된 기준선인지 별도 보존 대상인지 결정. |
| `Iris/test/lua/tooltip_t3_runtime_harness.lua` | 동일. Naming 변경과 runtime/harness 동작 변경을 섞어 byte/behavior parity를 주장하지 않는다. |

마감 조사에서는 `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, `docs/iris_tooltip_t3_static_data_alt_runtime_integration_plan.md`에도 외부 변경이 추가로 확인됐다. 해당 diff는 위 Alt/harness의 옆 배치 후속 수정, source-only 전달, 이번 후속의 package 제외와 PZ 시각 미확인 상태를 기록한다. 이 네 문서도 이번 작성에서는 수정하지 않는다. Naming baseline을 확정할 때 이 후속 변경의 채택 상태를 반영하고, 옆 배치 이전 package를 최신 source와 동일하다고 간주하지 않는다. 본 계획의 미래 rename 검증은 기존 layout 후속의 재개방이나 소급 packaging 요구가 아니다.

6. Clean subject 검증은 exact commit/tree에 결속한다. 구현 착수 때 위 변경의 disposition과 최신 HEAD를 확정하고 필요하면 isolated checkout을 사용한다. 현재 문서의 HEAD를 미래 구현 base로 강제하지 않는다.
7. External handoff, environment, wheel, Lua/PZ 도구의 실제 가용성은 이 문서 작성으로 검증되지 않았다. 실행 시 확인되지 않은 입력이나 누락된 필수 도구는 해당 검증 `BLOCKED`다.
8. 검토 반영 시 `docs/DECISIONS.md`의 「Iris validation — regular authority boundary / historical evidence separation / executable retirement」와 runner `main()`의 current-only 제한을 재확인했다. Historical/diagnostic 기록 보존은 executable selector 존속을 뜻하지 않는다. 기존 계획의 해당 mode 보존 문구는 이 개정으로 정정한다.
9. `docs/EXECUTION_CONTRACT.md`는 disclosure/evidence/closeout 의무의 근거이며 새 설계 권한이 아니다. Authority 문서 처리는 §5 Docs와 Change 5에 배정하고, sealed 상태는 naming closeout으로 자동 갱신하지 않는다.

### 4.2 O1–O3 scope-lock decision gate

아래 세 사항은 cluster 실행 순서, naming convention의 적절한 기존 owner, cost/benefit 예외를 physical migration 전에 확정하는 **scope-lock decision gate**다. 여기서 gate는 필요한 결정을 마친다는 뜻이며 별도 심사·승인 회의·PASS artifact를 요구하지 않는다. 계획의 unresolved defect나 계획 단계의 blocker가 아니다. 아래 실행안은 제안이며 이미 결정된 authority로 사용하지 않는다. Change 1–3의 조사와 disposition으로 해당 cluster의 범위를 정한 뒤 진행하며, 기존 owner-only 결정이나 protected authorization이 실제로 필요한 경우에만 그 절차를 적용한다.

| ID | 쟁점 | 코드에 기반한 제안 | 확정 전 경계 |
|---|---|---|---|
| O1 | Tooling-first 고정 순서 vs runtime-first/dependency-driven | Dependency-driven cluster를 사용한다. 첫 cluster는 가장 명확한 static Tooltip 책임을 기준으로 generator·runtime·harness·route·package를 함께 준비한다. T2가 T1 helper를 import하므로 경계를 가로지르는 선행 변경을 먼저 준비할 수 있다. | Runtime 파일만 먼저 adopt하거나 tooling만 옮긴 상태로 current를 전환하지 않는다. 최종 순서는 binding map에서 확정. |
| O2 | Repository convention vs module-authority-bound convention | `Iris/build/ENTRYPOINTS.md`는 command literal과 명령 관련 naming 예시만 소유한다. 일반 path/test/generated naming convention의 최종 owner는 기존 개발·기여 문서 또는 module 문서 중 실제 역할에 맞는 곳으로 scope lock에서 결정한다. | Human command owner라는 이유만으로 naming convention 전체 owner로 확장하지 않는다. Repository convention과 module-authority binding 중 어느 수준을 채택하는지도 명시하며 새 문서 체계·validator를 만들지 않는다. |
| O3 | Current durable stage-name 제거 원칙 vs cost/benefit keep-as-is | 확인된 순수 durable 작업 단계명은 이동하는 안을 제안한다. Historical/one-off/domain/version/compatibility/mixed는 명시적 retain/defer로 구분한다. | 비용만으로 남긴 순수 durable 항목을 naming 완료로 세지 않는다. Cost/benefit 유지가 승인되면 예외 목록과 claim ceiling을 함께 기록. |

관련 authority에 이미 유효한 exact-scope 승인이 있으면 그 범위에서 사용한다. O1–O3은 Change 3이 소유하는 정상적인 사전 결정 절차로 처리한다. 필요한 owner 판정이나 protected successor authorization은 해당 범위에서만 받고, 일반적인 내부 rename 선택마다 승인을 반복 요구하지 않는다. O1–O3이 계획 작성 시점에 열려 있다는 사실만으로 실행계획의 불완전성이나 새 Critical을 선언하지 않는다.

### 4.3 검토 반영 요약과 이력 경계

| 확인 항목 | 현재 계획의 적용 경계 | 담당 위치 |
|---|---|---|
| R1 — current-only route | Retired selector/replay 복원 금지. V4의 예상 negative invocation nonzero와 validation gate exit `0`을 구분하며 별도 validator를 만들지 않는다. | N5, C3, Change 5, V4/V9. |
| R2 — authority 문서 locator | Sealed 원문 보존과 successor current locator 정합을 문서별 규칙으로 처리한다. | §5 Docs, Change 2/3/5/7. |
| Vocabulary와 사전 결정 | N1–N4는 canonical term을 먼저 선택한 뒤 파생한다. O1–O3은 unresolved defect가 아닌 scope-lock decision gate다. | Change 2, §4.2/Change 3. |
| Capsule/archive와 directory 이동 | Current closure와 historical identity를 분리하고 directory reclassification 영향을 확인한다. | §5 Config, C3/C4. |
| Dynamic inventory와 baseline | 적용 baseline의 pending을 migration 전에 처리하고 inventory를 기존 실행 evidence와 연결한다. | Change 3, V10. |

앞선 통합 검토의 `ChatGPT: FAIL`, `Claude: WARN (plan_level)`와 Claude의 independence 기록은 당시 검토 이력이며 현재 개정의 verdict가 아니다. 계획 수정 자체를 독립 재검토 PASS나 실행 승인으로 기록하지 않는다. 원 verdict의 단일 token 확정이나 필수 근거가 없는 추가 independent-review/seal gate는 생략하며, 실제 적용되는 기존 owner/review 요구만 §7에 따라 유지한다. §4.3은 요약표 한 개와 이 문단 수준을 유지하고 cycle별 표·verdict 문단을 누적하지 않는다. 이후 상세 finding/disposition/개정 이력은 Change 7 note 5의 closeout 문서로 이관하되 원 검토·subject trace를 보존한다. 이관 전에는 원 검토 자료를 참조하며 이번 수정만을 위해 closeout을 미리 만들지 않는다.

---

## 5. Repository Areas Affected

다음은 실제 존재와 연결을 확인한 current readpoint다. 미래 경로는 §6 Change 2에서 별도 후보로 제시한다.

### Code

- Runtime: `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua`, `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`.
- Offline: `Iris/tooling/src/iris_tooling/__main__.py`, `Iris/tooling/src/iris_tooling/domains/tooltip_t1/`, `Iris/tooling/src/iris_tooling/domains/tooltip_t2/`.
- 인접 owner: `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_t1_d3.py`, `Iris/tooling/src/iris_tooling/domains/layer4/tooltip_t1_d4.py`. 실제 lifecycle/producer 책임 판정 후 필요한 reference만 포함.
- Tests: `Iris/tooling/tests/test_tooltip_t1_*.py`, `Iris/tooling/tests/test_tooltip_t2_*.py`, `Iris/tooling/tests/fixtures/tooltip_t1/`, `Iris/test/lua/tooltip_t3_runtime_harness.lua`.
- Runtime wrapper: `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`. `PAYLOAD`, binding path 목록과 harness subprocess 경로를 함께 확인.
- Current route: `Iris/_docs/round3/round3_run_contract_tests.py`.
- Validation consumers: `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`, `iris_clean_checkout_validation_common.py`, `audit_current_route_output_isolation.py`, `inventory_iris_offline_tooling.py`, `write_environment_receipt.py` 및 동일 디렉터리의 launcher/tests.
- Package: `Iris/tools/package_iris.ps1`.
- G5 영향 판정: `Iris/tooling/src/iris_tooling/build/naturalization_compiler_identity.py`. 현재 21-path closure에 Tooltip domain은 직접 포함되지 않는다. 이번 변경이 해당 closure에 닿는지 확인하며 G5 successor를 자동 생성하지 않는다.

### Docs

- 현재 문서: `docs/iris_current_responsibility_naming_alignment_plan.md`.
- Protected policy: `docs/iris_tooltip_t1_display_contract_policy.md`. 이름을 바꿀 경우 원본을 보존하고 additive successor를 사용한다.
- 구현 결과의 durable trace는 향후 `docs/iris_current_responsibility_naming_alignment_closeout.md` 한 문서에 census 요약, exact rename map, retained/deferred ledger, 검증 ceiling을 모은다. 대량 raw census/log는 repository-external 실행 산출물로 둔다.

다음 표는 **향후 구현 중** authority/documentation locator 정합을 소유한다. 이번 개정은 계획 파일만 수정하며, 아래 문서의 기존 working-tree 변경은 보존한다.

| 문서 | Rename의 locator 영향과 처리 규칙 | 소유 Change / 기존 procedure |
|---|---|---|
| `docs/DECISIONS.md` | Required manifest path, Tooltip module identity 등 영향 literal을 entry별로 분류한다. Original sealed text와 당시 path/hash는 제자리 rewrite하지 않는다. 영향이 있으면 같은 decision family에 historical→successor locator의 additive current readpoint/trace를 추가하고 원문은 predecessor로 해석 가능하게 보존한다. 실제로 무효화되는 current locator가 없으면 `no_update`와 이유를 남긴다. | Change 3에서 entry/처리안을 lock → Change 5에서 mapping/current readpoint 추가 → Change 7에서 실제 adoption/ceiling 확인. 문서의 「문서 규칙」 및 Iris governance의 exact-successor/owner 규칙을 따른다. 기존 결정 내용·sealed 상태의 변경이 필요하면 해당 owner 절차를 먼저 적용하며 naming 승인으로 대신하지 않는다. |
| `docs/ARCHITECTURE.md` | Current 구조 설명의 `IrisAltTooltip → IrisTooltipT2Lookup → IrisTooltipT2Data` 등 경로·module identity는 실제 successor chain으로 갱신한다. 날짜/subject가 결속된 historical snapshot은 보존하고 필요한 곳에 predecessor→successor trace를 붙인다. | Change 3에서 current 문단과 historical snapshot을 분리 → Change 5에서 current 구조 설명 갱신 → Change 7에서 code/index와 재대조. 기존 구조 지도/역할 경계와 `DECISIONS.md` 우선순위를 따른다. 설명 변경으로 owner·dependency 의미를 바꾸지 않는다. |
| `docs/ROADMAP.md` | Naming adoption으로 current locator나 현재 상태 설명이 달라지는 항목만 갱신한다. Current를 가리키는 literal이 무효화되면 Change 5에서 successor locator로 정렬한다. Historical 완료 수치/subject는 보존하며, current 상태·다음 gate·locator에 영향이 없으면 `no_update`와 근거를 기록한다. | Change 3에서 영향 여부 lock → Change 5에서 affected current locator 갱신 → Change 7에서 actual 완료/잔여 범위 반영 여부 결정. 기존 「운영 규칙」의 current 상태/다음 gate 역할을 따르고 상세 실행 로그를 넣지 않는다. |
| `Iris/build/ENTRYPOINTS.md` | Actual current CLI/module/runner 경로를 같은 cluster의 successor로 정렬한다. Historical 기록을 근거로 retired selector command를 되살리지 않는다. | Change 5가 human command literal owner 정합을 담당. General naming convention은 O2 판정 대상이며 이 파일의 역할에 자동 추가하지 않는다. |

Sealed/historical literal의 존재 자체는 broken current reference가 아니다. 다만 current readpoint가 없어 옛 경로만 따라가게 되는 상태는 허용하지 않는다. 처리 방법이나 owner procedure가 확정되지 않은 locator row는 scope lock을 통과시키지 않는다.

### Config

- `Iris/tooling/pyproject.toml`, `Iris/tooling/uv.lock`: wheel package membership/import에 필요한 부분만 영향 판정. 의존성 변경 자체는 목적이 아니다.
- `Iris/_docs/authority/iris_current_authority_manifest.json`, `Iris/_docs/authority/iris_current_route_index.json`.
- `Iris/_docs/authority/tooltip_t1/`, `Iris/_docs/authority/tooltip_t2/` 및 D3/D4/D5의 DVF/QG owner registry/schema: physical locator, protected policy, schema compatibility를 구분한다.
- `Iris/_docs/round3/current_route_required_validations.json`, `round3_test_taxonomy.json`, `round3_active_core_closure.json`, `round3_pytest_source_classification.json`: 같은 디렉터리 안에서도 각각의 live consumer와 historical payload를 구분한다.
- `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`와 이를 쓰고 읽는 receipt workflow. Immutable target record와 historical 환경 파일은 보존한다.
- `Iris/validation/clean_checkout/evidence/current_required_v1/manifest.json` 및 `objects/`: protected current capsule의 closure/logical member/hash 연결을 확인한다. Raw object는 binary Git blob으로 보존하고 current consumer가 실제로 필요로 하는 binding만 영향 판정한다.
- `Iris/validation/clean_checkout/authority/iris_historical_archive_v1.json`, `Iris/validation/clean_checkout/authority/iris_historical_removal_v1.json`: archive/removal subject의 original logical path와 hash를 유지한다. Current path 이동과 historical removal/absence assertion을 혼동하지 않으며 archive를 current gate의 입력 의존으로 추가하지 않는다.

### Generated Artifacts

- `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua`: fresh producer output으로 재생성한 뒤 검증된 bytes만 채택.
- External Tooltip projection manifest/receipt/closeout: 새 attempt/root에서 생성. 기존 `final_root`의 파일을 제자리 rename하거나 기존 receipt hash를 덮어쓰지 않는다.
- Fresh package와 격리 설치본: canonical Lua module membership과 bytes를 대조. 기존 package는 source authority가 아니다.
- Current Layer 3 generation/pointer, classification와 use-case payload는 원칙적으로 불변이다. 실제 binding 영향이 드러나면 영향 목록과 필요 검증을 먼저 갱신한다.

---

## 6. Planned Changes

로드맵 Phase 1–7을 아래 Change 1–7에 대응시킨다. Change 1–3은 조사·범위 확정이고, Change 4–5는 cluster 안에서 함께 완료해야 하는 구현·결속 작업이다. Change 5를 전체 rename 뒤로 미뤄 깨진 current 상태를 남기지 않는다.

각 Change의 **Validation은 충족할 확인 조건이지 Change마다 별도 테스트를 실행하라는 지시가 아니다.** 같은 subject/input의 한 검사 결과를 여러 Change와 V-ID에 연결한다. 구현 중 focused checkpoint는 기본 의무 `0회`이며, 구현자가 실패 위험이나 디버깅 필요에 따라 최소 범위를 선택할 수 있다. 여러 cluster를 준비 상태로 묶어 최종 통합 검증으로 닫을 수 있지만, 필수 검증·binding이 끝나기 전에 개별 cluster를 current로 adopt하지 않는다. 실행 횟수와 중복 제거 기준은 §7이 소유한다.

Change 1–7 사이의 별도 입장/퇴장 gate는 두지 않는다. Census·vocabulary·rename map·binding map·문서 확인은 구현 중 같은 작업 기록에 정리하고, 각각의 완료 승인이나 PASS token을 기다리지 않는다. 필요한 범위·baseline·compatibility·보호 변경의 판단은 해당 변경 전에 끝내되, 미결 항목과 의존하지 않는 다른 cluster의 작업까지 일괄 중단하지 않는다. 실제 current adoption/완료에는 §7의 적용되는 필수 조건만 사용한다.

### Change 1 — Current naming census와 변경 전 baseline

**Purpose:** 검색 hit를 실제 책임과 current dependency로 분류하고 비교 가능한 변경 전 상태를 확보한다.

**Files:** §5의 current readpoint, tracked Iris 파일, root의 실제 Iris consumer, current route가 선택하는 external artifact.

**Implementation Notes:**

1. HEAD/tree, working-tree diff, generated/ignored/untracked 상태와 기존 변경을 기록한다. 다른 임시 저장소·build copy는 logical owner와 구분한다.
2. `rg --files`, `git ls-files`, 필요한 범위의 `rg --hidden --no-ignore`로 `tooltip_t1`, `tooltip_t2`, `t1_`, `t2_`, `d1`–`d6`, `round`, `phase`, `refactor`, `residual`, `cleanup`, `final`, `completion`, `migration`, `successor`, `predecessor` 후보를 조사한다. 대소문자·경로 구분자·동적 조합도 확인한다.
3. 각 항목을 `current_recurring_function`, `current_supporting_contract_or_asset`, `oneoff_procedure`, `historical_or_reproduction_record`, `domain_version_or_external_contract`, `mixed_responsibility` 중 하나로 분류한다. Runtime session 의미는 domain 항목의 유지 이유로 명시한다.
4. Candidate마다 `old_path`, symbol, actual responsibility, current dependency evidence, producer/consumer, generated/source, public/internal, binding 영향, historical trace, rename 여부/이유를 기록한다.
5. Migration-specific equivalence baseline은 기존 current artifact/source의 read-only snapshot을 우선한다. Generated Lua raw bytes, exact FullType→KO/EN 배열, public string, selected test identity set, package relative member→hash와 affected route membership을 확보하되 baseline만을 위해 전체 suite·full A/B·generation·package를 다시 실행하지 않는다. 기존 package가 source와 다르면 재사용하지 않고 current source와 package selection rule에서 비교 member set을 확보하거나 필요한 baseline만 생성한다. Lookup은 source/기존 fixture의 expected contract와 최종 V6 evidence로 비교하고, 이것으로 부족한 영향이 있을 때만 변경 전 관찰을 추가한다. 필요한 baseline의 미확보 상태를 기존 PASS에서 추정하지 않는다.
6. Static scan과 별도로 dynamic resolution inventory를 만든다. Lua `package.loaded`/`dofile`, Python `importlib`/`spec_from_file_location`, pytest collection/fixture, `Path.parents[n]`, PowerShell 재귀 copy 및 filename 조합 위치를 포함한다. 각 row에 origin file/symbol, mechanism, 생성·탐색 가능한 target set/pattern, current/historical disposition, affected cluster와 확인할 기존 V-ID를 붙인다. Inventory의 final completeness는 V10이 담당한다.
7. Authority 문서의 path뿐 아니라 qualified Python/Lua module identity도 찾는다. 각 occurrence의 문서/entry, current readpoint 또는 historical/sealed 성격, locator 무효화 여부를 기록해 §5 Docs 처리표와 연결한다.

**Validation:** 발견 후보의 미분류 `0`, 각 판정에 코드/consumer 근거 존재, scan/exclusion 범위 명시, ignored current input 누락 여부 확인. 이 census는 임시 migration evidence이며 regular validation membership을 만들지 않는다.

### Change 2 — Responsibility vocabulary와 exact rename/non-rename map

**Purpose:** 구현보다 넓지 않은 이름을 선택하고 이름을 유지하는 이유도 같은 map에 남긴다.

**Files:** Change 1 inventory와 §5의 actual producer/consumer. 이 단계에서는 physical move하지 않는다.

**Implementation Notes:**

이 Change는 **actual responsibility 확인 → 자산 계열의 canonical term 선택 → 층위별 successor 이름 파생 → exact map 작성** 순서로 수행한다. 이름을 각각 먼저 정한 뒤 마지막 검사에서 어휘를 맞추지 않는다. 기존 vocabulary 산출물에서 완성된 KO/EN 배열 자산 계열을 가리키는 term 하나를 먼저 고르고, 그 term에 실제 역할을 나타내는 접미사를 붙인다. 새 naming registry나 규칙 체계를 만들지 않는다.

이 계획의 공통 term 후보는 **Tooltip Static Data**다. Lua의 `TooltipStaticData`와 Python/harness의 `tooltip_static_data`는 casing/style만 다른 같은 어근이다. N1은 `Lookup`, N2는 자산 자체, N3는 `projection`, N4는 `runtime_harness`로 역할을 구분한다. 아래 제안 이름은 이 공통 term에서 파생한 예시이며, Change 2에서 다른 term을 선택하면 N1–N4를 함께 다시 파생한다. Public/internal 및 binding closure를 확인하기 전에는 canonical successor가 아니다.

| ID | 현재 path 또는 prefix | 제안 successor | 조건 |
|---|---|---|---|
| N1 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua` | Internal static lookup 책임과 supported require 여부 확인. |
| N2 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua` | N1, serializer output, manifest filename, runtime fixture와 같은 cluster. |
| N3 | `Iris/tooling/src/iris_tooling/domains/tooltip_t2/` | `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/` | 공통 term + producer 역할. Installed imports와 CLI dispatch 동시 갱신. CLI token/schema 이름은 별도 compatibility 판정. |
| N4 | `Iris/test/lua/tooltip_t3_runtime_harness.lua` | `Iris/test/lua/tooltip_static_data_runtime_harness.lua` | 공통 term + runtime 검증 역할. Wrapper, binding 목록, 기존 사용자 변경을 함께 disposition. |
| N5 | `Iris/_docs/round3/round3_run_contract_tests.py` | `Iris/validation/current_route/run_contract_tests.py` | Current selector + fail-closed current contract만 보존. Retired historical/diagnostic/all selector를 재도입하지 않음. `directory_reclassification` 영향과 companion closure 확인. |
| N6 | `Iris/_docs/round3/current_route_required_validations.json` | `Iris/validation/current_route/required_validations.json` | Readers/writers, source classification, launcher, package default와 required binding을 함께 갱신. `directory_reclassification`의 discovery/membership 영향 명시. |
| N7 | `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json` | `Iris/validation/clean_checkout/authority/current_environment.json` | Existing receipt workflow가 successor locator를 쓰도록 변경 가능할 때만. Immutable record의 역사명은 유지. |
| N8 | `tooltip_t1/`와 `d2.py`, `d5.py`, D3/D4 support | 단일 package/file successor를 아직 제안하지 않음 | Lifecycle·current helper가 혼재한다. 명확한 logical unit은 별도 map, 혼재 파일은 `good_name_found=false`, `reason=mixed_responsibility`. |

각 최종 map row는 `old_path`, `new_path`, `actual_responsibility`, `rename_reason`, `producer`, direct/dynamic/generated/test/package consumer, `public_or_internal`, `compatibility_status`, `generation_rule_impact`, `path/hash/binding_impact`, `required_validation`, retain/defer 이유를 가진다.

추가로 `migration_kind`에 filename/module rename과 `directory_reclassification` 여부를 구분한다. 후자는 물리적 배치·discovery 분류의 변경이며 semantic authority owner 변경을 허용하는 표지가 아니다. `authority_document_locator_impact`에는 document/entry, old literal, `invalidates_current_locator`, historical/sealed 여부, update/retain/no-update 처리, successor 또는 mapping 위치, owning Change, 적용 procedure와 근거를 기록한다. N5/N6는 특히 source discovery glob, relative root, package/test membership과 capsule closure의 영향을 포함한다. 이 필드는 task-local rename map용이며 새 product schema나 governance registry가 아니다.

`tooltip_t1` package 전체나 테스트를 정규 기능으로 재분류하지 않는다. T1 focused tests는 lifecycle evidence이고 T2 focused tests는 dedicated route다. 경로 rename이 가능해도 applicability와 recurring membership은 그대로 둔다. `finalize`가 실제 finalization 책임을 표현하거나 `v1/v2`가 계약 version이면 이름을 유지할 수 있다.

**Validation:** Canonical term을 successor 이름보다 먼저 선택했는지와 N1–N4의 공통 어근/역할 접미사 파생 관계를 확인한다. 모든 rename target에 정확한 책임과 producer/consumer 존재, 같은 책임의 용어 일치, Windows case-insensitive filename collision 없음, retain/defer별 근거 존재. 외부 consumer가 조사되지 않았다는 사실을 consumer 부재로 기록하지 않는다.

### Change 3 — Dependency/binding closure 및 migration scope lock

**Purpose:** 실제 이동 전에 새 경로가 어떤 identity와 contract를 바꾸는지 결정한다.

**Files:** Runtime/generated chain, `__main__.py`, Tooltip contract/CLI/serializer/tests, route runner/companions, full-gate launchers, package script, current manifests, §5 Docs의 네 문서와 capsule/archive/removal readpoint.

**Implementation Notes:**

다음 cluster를 기본 단위로 검토한다. O1 판정과 dependency 방향에 따라 합치거나 순서를 조정한다.

| Cluster | 함께 닫아야 하는 연결 | 특별 확인 |
|---|---|---|
| C1 Static Tooltip | T2 package/serializer → external Lua·manifest → runtime Data/Lookup → Alt → harness/wrapper → package/install → current artifact locator | T1 helper import, generation filename, admitted input lineage, runtime 변경 baseline. |
| C2 Tooltip supporting contract | Current T1 helper·owner input·policy/contract → T1/T2 reader → tests/CLI/authority map | Mixed 파일은 defer 가능. Protected policy는 additive successor; 과거 handoff의 계약 locator는 별도 보존. |
| C3 Current validation navigation | Current-only runner + taxonomy/closure/source classification/required manifest → full-gate/audit/inventory/CLI → package default → current index/docs | `parents[n]`, `TEST_ROOT`, AST 기반 closure audit, selected test ID, directory reclassification 및 `current_required_v1` capsule closure. Retired selector는 이동 대상 기능이 아님. |
| C4 Environment/compatibility support | Current environment locator + writer/readers; API baseline + 실제 acceptance consumer | Fresh wheel/environment 영향, capsule current binding과 historical archive/removal logical path의 분리. Historical record와 API baseline 원형 보존. |

특히 `tooltip_t2/contract.py:admit()`는 adopted T1 commit에 대해 `git show <commit>:<contract path>`를 실행한다. Current `CONTRACT_FILES`를 새 path로 치환하면 과거 commit에 없는 경로를 조회할 수 있다. 따라서 **current locator와 historical subject의 logical path를 분리**한다. 원본 contract bytes/schema와 sealed handoff를 보존하는 bounded reader/mapping을 우선 검토한다. 새 contract subject가 꼭 필요하면 기존 owner 절차로 새 handoff를 발행하며, 옛 receipt 내부 path/hash를 수정하거나 검증을 생략하지 않는다.

필요한 compatibility adapter마다 consumer, 이유, canonical owner, scope, 유지 조건, 제거 조건 또는 무기한 유지 이유를 기록한다. 새 내부 implementation은 하나만 유지한다. 기존 supported `IrisData`, Browser build/getGroupVariants, Wiki facade와 Alt가 사용하지 않는 `IrisTooltipSummary`를 이번 이름 정비로 제거하지 않는다.

`IrisTooltipT2Lookup`은 현재 확인된 internal consumer를 갖지만 이것만으로 외부 compatibility 계약 유무가 확정되지는 않는다. Supported manifest/current documentation과 실제 packaging surface를 대조해 N1 adapter 필요성을 정한다.

Current runner는 재확인 시 이미 current-only다. 착수 시 다른 subject에서 current 기능과 retired executable selector가 혼재한 것으로 확인되면 이를 그대로 successor로 운반하지 않는다. 이번 naming 범위에서 분리할 수 없는 asset은 `mixed_responsibility`로 physical rename을 defer하고 연결 cluster의 완결 가능성을 다시 판정한다. 별도 historical runner/replay mechanism을 만들지 않는다.

Capsule/archive binding map에는 moved path와 `current_required_v1/manifest.json`의 member/closure, archive/removal의 original logical path 간 관계를 각각 기록한다. Historical object/path/hash는 정규화·재작성하지 않는다. Current capsule binding이 실제로 바뀌면 기존 protected authority의 승인·successor 절차를 명시한 뒤 갱신하고, 영향이 없으면 그 근거를 남긴다. 과거 archive를 새 live dependency로 복원하지 않는다.

Physical migration 전에 적용 cluster의 비교 baseline은 모두 확보돼 있어야 한다. `pending`이 남은 baseline은 먼저 생성·관찰하거나 근거 있는 `not_applicable`로 판정한다. 확보 불가라면 해당 비교가 필요한 cluster를 defer/block하고 완료 scope에서 뺀다. Mutation 이후의 상태를 변경 전 baseline으로 사후 생성하지 않는다. Authority-document locator row도 §5의 update/retain/no-update 및 owning Change를 모두 확정한다.

**Validation:** O1–O3 disposition, exact map, external input/output 범위, 기존 dirty change 처리, public/internal 경계, generated/capsule closure, required validation, protected successor 및 authority-document 처리 모두 명시. 각 검증은 §7에 따라 필수 실행, 동일 subject evidence 재사용, 영향 없음 또는 비필수 gate 생략으로 처리하며 별도 승인 절차나 새 검증 manifest는 만들지 않는다. 채택 cluster의 baseline pending과 미결 문서 locator row는 `0`. Dynamic inventory의 모든 발견 row에 V-ID/처리 근거를 배정하며 최종 실행 확인은 V10에서 닫되 독립 gate로 만들지 않는다. 미결 구현 항목은 retain/defer 및 claim ceiling을 기록하고 그 물리적 변경만 제외한다. Scope lock 이후 새 cluster가 발견되면 실제 영향 항목만 갱신하며 전체 scope-lock 승인 절차를 다시 만들지 않는다.

### Change 4 — Dependency-cluster migration

**Purpose:** Scope-locked current responsibility를 이름과 참조가 일치하는 단위로 이동한다.

**Files:** 채택된 N1–N7 및 census에서 추가 확정된 exact path. C2의 mixed 항목은 승인된 범위만 포함한다.

**Implementation Notes:**

1. Source move, import/require, CLI dispatch, generator constant, output filename, manifest field, fixture/collection, package/include/install, current docs를 같은 cluster에서 수정한다. 변경 전후 이름이 단순 casing만 다르면 Windows에서 임시 경유명을 사용하고 최종 Git path를 확인한다.
2. N2는 generated Lua를 손으로 rename하는 것으로 끝내지 않는다. `serialization.py`의 `LUA_NAME`과 `manifest_bytes()`의 `lua.file_name`, `cli.py`의 artifacts/finalization 소비가 새 output을 일관되게 사용하도록 한다.
3. `lua_bytes()`는 현재 module/global 이름 없이 `return { ... }` 형태를 생성한다. Filename만 달라지는 범위에서는 원래 payload와 successor payload의 **raw bytes 동일**을 요구한다. Manifest/receipt의 locator와 implementation identity 변경은 예상 delta로 별도 비교하며 old/new manifest 전체 byte equality를 강제하지 않는다.
4. Producer/output naming을 바꾼 경우 동일 admitted input과 exact implementation의 external fresh generation A/B를 최종 subject에서 한 쌍 수행한다. 새 A/B끼리는 deterministic Lua/manifest bytes 동일을 요구한다. Change 6/V7에서 같은 결과를 사용하며 cluster마다 새 A/B를 요구하지 않는다. 기존 final root와 실패 attempt는 그대로 둔다.
5. `IrisAltTooltip.lua`의 lookup 교체 외 동작 변경을 금지한다. Lazy load 1회, 실패 후 재시도 없음, exact locale/key, invalid 전체 배열 거부, 0줄 침묵, 중복/문자열 보존, Kahlua `pairs` 경로를 유지한다. Lookup이 immutable proxy를 새로 제공한다고 해석하지 않는다. 현재 구현은 내부 read-only consumer에게 원래 row를 반환한다.
6. Package script는 media를 재귀 copy하고 Layer 3 generation을 별도 선택한다. 따라서 단순 Lua rename도 package membership에 나타난다. 적용되는 모든 cluster를 포함한 최종 fresh package 하나에서 old/new 중복, missing module, require mismatch를 확인한다. 이 package를 격리 설치·PZ smoke에도 재사용하고 member/bytes를 대조하며 중간 cluster별 package를 의무화하지 않는다.

**Validation:** Unplanned file/content delta `0`, 필요한 old alias만 존재, fresh output에서 unintended old filename 재등장 `0`. 필요한 자동 검사는 §7의 최종 통합 실행 또는 선택한 focused 실행의 exit `0`으로 확인한다. Cluster별 독립 focused 실행은 필수가 아니다. Old producer+new consumer 또는 그 역방향인 상태를 current adoption으로 기록하지 않는다.

### Change 5 — Current authority와 validation binding 재결속

**Purpose:** 같은 owner의 successor physical locator가 실제 검증 subject 및 authority 문서의 current readpoint와 일치하도록 한다. §5 Docs 처리표의 구현 owner는 이 Change다.

**Files:** `iris_current_authority_manifest.json`, `iris_current_route_index.json`, required manifest/runner/companion, clean-checkout launchers/common/audit/tests, environment receipt workflow, capsule의 영향받은 current binding, `Iris/build/ENTRYPOINTS.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.

**Implementation Notes:**

1. C3 이동 시 runner만 옮기지 않는다. `DEFAULT_TAXONOMY`, `DEFAULT_CLOSURE`, `DEFAULT_REQUIRED_VALIDATIONS`, `REPO`, source classification 및 `IRIS_ROUND3_REQUIRED_VALIDATIONS_PROJECTION`의 용도를 각각 판정한다. Successor는 `current` selector와 fail-closed current contract만 제공한다. Repository-local `historical / diagnostic / all` executable selector, corpus materialization 및 별도 replay runner는 재도입하지 않는다. Historical/diagnostic taxonomy·disposition·receipt는 기록으로 보존하되 executable 선택 기능으로 해석하지 않는다. Route index의 historical metadata도 같은 경계로 판정한다.
2. `invoke_receipt_bound_full_gate.ps1`, `invoke_deterministic_compare.ps1`, `audit_current_route_output_isolation.py`, inventory와 tests의 hard-coded locator도 같은 successor를 가리키게 한다. Output-isolation audit를 무력화하거나 path check를 느슨하게 하지 않는다.
3. Route/index의 current locator와 역사적 subject/hash를 담은 record를 구분한다. Historical record의 `T1/T2`, `round3`, schema identifier는 original identity로 남길 수 있다. Retained ledger에 consumer와 의미를 적는다.
4. Test 파일/심볼을 바꾸면 before/after collected test ID의 일대일 map과 contract 의미 보존을 확인한다. 개수가 같다는 이유만으로 membership 보존을 주장하지 않는다. Routing denominator, pytest node, standalone validation은 각자의 identity set으로 비교한다.
5. `Iris/tooling/**` source/lock이 바뀌면 existing workflow로 exact source의 wheel/fresh external environment와 새 immutable environment authority를 만든다. Current locator는 workflow를 통해서만 전환한다. `write_environment_receipt.py`의 record naming과 schema contract도 소비자와 함께 확인한다.
6. G5는 declared compiler path-set/source-byte closure에 실제 영향이 있을 때만 기존 append-only mechanism으로 successor를 추가한다. 기존 successor를 수정·재번호화하지 않고, Tooltip 경로를 바꿨다는 이유만으로 G5를 재발행하지 않는다.
7. Protected current policy/contract는 §2의 additive successor 제약을 따른다. 옛 path를 지우지 못한 경우 historical/compatibility trace로 남기고 current writer/reader의 canonical owner는 하나로 유지한다.
8. §5 Docs 처리표와 scope-locked `authority_document_locator_impact`를 실행한다. `DECISIONS.md` sealed 원문/path/hash는 보존하고 같은 family의 additive current readpoint/mapping으로 successor를 연결한다. `ARCHITECTURE.md`의 current 구조 설명은 실제 successor path/module로 고치되 historical snapshot은 보존한다. `ROADMAP.md`의 affected current locator만 정렬하고 actual adoption/completion 상태는 Change 7에서 확인한다. `no_update` 판정도 문서/entry와 이유를 남긴다. 이 계획의 수정이나 machine PASS 자체로 sealed decision/status를 변경하지 않는다.
9. Current capsule에 영향이 있으면 기존 protected binding 절차로 successor를 결속하고 V9에서 closure를 확인한다. `iris_historical_archive_v1.json`, `iris_historical_removal_v1.json`의 original logical path/hash와 raw capsule object는 historical evidence로 보존한다. Directory reclassification 때문에 old removal subject를 새 current subject로 재해석하지 않는다.

**Validation:** V1/V4/V9에서 current route resolution, required manifest load, exact membership map, installed inspect, package/environment/capsule binding, retired selector 재노출 및 historical fallback 부재를 확인한다. 문서별 영향 row를 actual diff와 대조해 stale current locator와 미처리 row `0`, original sealed/historical text의 무단 rewrite `0`을 확인한다. Source/path binding이 바뀐 successor에서 필요한 validation을 실행한다. Predecessor PASS는 evidence trace일 뿐 이 단계의 PASS가 아니다.

### Change 6 — Reference closure와 behavior preservation

**Purpose:** 기능·책임 이름을 쓰는 current tree가 실제로 로드·생성·검증되며 기존 의미를 보존함을 확인한다.

**Files:** Final implementation subject와 fresh generation/package/install artifacts, §7의 기존 검증 경로.

**Implementation Notes:**

- Static residual scan과 dynamic resolution inventory를 V1/V10으로 다시 맞춘다. 각 old reference는 historical, one-off, domain/version, supported compatibility, mixed defer 또는 결함 중 하나로 설명되어야 한다. Authority 문서의 current locator/module identity도 포함한다. Dynamic entry마다 연결된 기존 V-ID의 실제 evidence 또는 근거 있는 retain/defer/N/A 판정을 확인하고 미설명 entry가 있으면 closure를 닫지 않는다.
- Baseline과 successor의 exact FullType set, locale별 line arrays, 순서·중복·빈 배열, Menu/Tooltip public text를 비교한다. Locator/hash delta와 semantic delta를 분리한다.
- 최종 fresh wheel의 실제 producer/inspect/full-gate 실행으로 import/CLI를 함께 확인하고, Change 4의 fresh generation/package 결과를 재사용한다. Source checkout에서만 되는 import는 성공이 아니다. 같은 wheel을 확인하기 위한 별도 import-smoke suite는 기본 실행하지 않는다.
- Exact terminal subject에서 canonical Run A/B와 deterministic comparator를 기본 한 체인 수행한다. 해당 gate가 실행한 runtime `full` harness와 current-route/closure 검증은 대응 V-ID의 evidence로 사용하며 별도 suite를 반복하지 않는다. Unchanged subject의 confidence rerun은 하지 않되 execution-relevant correction이 있으면 affected validation과 mandatory exact-subject gate는 재실행한다.
- Runtime Lua path를 바꿨다면 bounded PZ smoke를 수행한다. 기존 T3 인게임 완료를 새 module path의 evidence로 승계하지 않는다.

**Validation:** §7의 적용 가능한 검사 결과와 exact subject를 기록한다. V10 inventory closure와 V1의 문서 locator 정합 확인을 포함한다. Runtime 미실행은 runtime `not_run` 또는 도구/환경 사유에 따른 `blocked`이며, 자동 테스트 PASS만으로 runtime preservation을 완료하지 않는다.

### Change 7 — Retained names, convention, closeout

**Purpose:** 남은 이름의 이유와 완료 한계를 명확히 남기고 동일한 혼동의 재발을 줄인다.

**Files:** 향후 `docs/iris_current_responsibility_naming_alignment_closeout.md`, O2에서 선택된 existing current documentation owner 및 §5 Docs 처리표에 따른 `DECISIONS.md`/`ARCHITECTURE.md`/`ROADMAP.md`의 영향 항목.

**Implementation Notes:**

1. Initial census와 final ledger를 대조해 unexplained item `0`으로 닫는다. Historical retained, one-off retained, domain/version retained, compatibility retained, mixed-responsibility deferred를 구분한다.
2. D2/D5 등 mixed asset은 concrete current consumer와 lifecycle function을 적은 follow-up 목록으로 남긴다. 이 계획에서 분해하지 않은 구조 문제가 해결됐다고 하지 않는다.
3. Small convention은 permanent path의 subject/책임 우선, lifecycle ID의 execution artifact 사용, domain/version 보호, producer와 generated filename 일치, test의 contract 중심 이름, 새 live authority의 round/refactor 배치 방지, `common/misc/utils`로 모호성 이동 금지, one-off 승격 금지, supported compatibility 보존을 포함한다.
4. Rename map과 retained ledger는 historical locator→successor current locator의 durable trace다. Regular gate가 매번 읽어야 하는 registry로 만들지 않는다.
5. Implementation, machine validation, runtime observation, review 및 owner/adoption을 별도 상태로 기록한다. 검증하지 않은 축은 명시적으로 남긴다. 이후 실행 중 개정의 상세 finding/disposition, cycle별 verdict, 변경 이유·위치 및 subject trace는 `docs/iris_current_responsibility_naming_alignment_closeout.md`에서 관리한다. §4.3은 현재 적용 요약으로만 유지하며 표나 verdict 문단을 cycle마다 추가하지 않는다. 이관은 과거 판정의 삭제·재해석이 아니며 계획 문서를 review ledger로 확장하지 않는다.
6. Change 5의 document disposition을 마감한다. Current 문서의 locator는 actual adopted code/index와 일치해야 하며, `DECISIONS.md`의 additive mapping은 원문/subject trace를 보존해야 한다. `ROADMAP.md`는 실제 결과에 따라 current 상태/다음 gate에 필요한 최소 정보만 갱신한다. 영향이 없어서 갱신하지 않은 문서·entry는 그 근거를 closeout에 남긴다. Cost/benefit으로 유지한 순수 durable stage-name이 있으면 남은 문제와 축소된 완료 scope를 명시하며 전체 naming problem 해결을 주장하지 않는다.

**Validation:** 승인 scope의 unclassified candidate `0`, unintended old active dependency `0`, retained/deferred 이유 누락 `0`, V10의 미설명 dynamic entry `0`, document disposition 미처리 `0`, 완료/미완료 cluster와 non-claim 명확화. 수정된 계획의 자체 확인과 독립 재검토 판정은 구분한다.

---

## 7. Validation Plan

### Automated Validation

실행 command의 current owner는 `Iris/build/ENTRYPOINTS.md`와 각 기존 launcher다. 아래는 검증 적용표이며 full-gate parameter/판정 규칙을 복제하는 새 wrapper가 아니다. Rename된 command/path는 exact map에 따라 owner 문서와 함께 갱신한다. 로그에는 실제 command, exit code, subject commit/tree, 적용 cluster와 artifact binding을 기록한다.

검증 축 V1–V10은 별개의 테스트 suite 10개가 아니다. **추가 테스트·중복 invocation은 기본 0개로 두고, 필수 계약을 충족하는 최소 실행 집합을 선택한다.** `docs/DECISIONS.md`의 clean-checkout 및 workflow consolidation 경계에 따라 기존 required membership, failure attribution, isolation과 A/B fresh-process independence는 줄이지 않는다. 이번 조정은 naming migration의 실행 부담을 줄이는 것이며 기존 regular test를 삭제·skip하거나 검증 시스템 자체를 재설계하는 작업이 아니다.

#### Gate 적용 — 비필수는 생략

여기서 독립 gate는 착수·채택·완료를 별도 통과 판정이나 승인으로 차단하는 절차다. **기존 authority/실제 consumer contract의 적용 근거가 없는 gate는 생략한다.** 아래 표로 적용 여부를 판단하며 이를 위해 gate registry, 새 waiver/승인 문서 또는 별도 검증을 만들지 않는다.

| 구분 | 처리 | 적용 근거·경계 |
|---|---|---|
| Canonical clean-checkout full gate | 구현의 최종 exact subject에서 A/B + comparator 한 체인 유지 | `DECISIONS.md`의 mandatory full-repository reproducibility contract. 현재 required membership과 correction-subject 재검증은 생략 불가. |
| Producer admission / finalization / adoption | 실제 변경된 subject나 consumer가 요구할 때만 유지 | 새 Tooltip staging/handoff가 필요하면 기존 strict admission/finalizer의 필수 검사·metadata를 지킨다. Unchanged T1/T2/DVF input을 naming 작업이라는 이유로 다시 seal/finalize하지 않는다. |
| Protected owner·environment·capsule·G5 절차 | 보호된 delta/closure가 실제로 바뀔 때만 유지 | 해당 authority의 명시적 owner 승인·successor 조건만 적용한다. 영향 없는 identity 재발행·reapproval gate는 생략. |
| 추가 independent review / 통합 verdict / 별도 owner seal | 필수 적용 근거가 없으면 생략 | 기존 governance의 review/owner 축 분리는 보존하되 그것만으로 추가 review 실행 의무를 만들지 않는다. 실제 owner-only 조건은 우회하지 않는다. 생략한 review를 PASS로 쓰지 않는다. |
| Change/cluster별 admission·exit·checkpoint gate | 생략 | 필요한 구현 판단과 evidence는 기존 작업 기록 및 terminal 검증에 통합. 별도 단계 승인·gate receipt 없음. |
| Census·vocabulary·rename/binding map·V1/V10·문서 정합의 독립 gate | 생략 | 판단과 reference closure 자체는 유지하되 별도 validator·approval·PASS artifact로 분리하지 않는다. 필요한 확인을 마치면 다음 작업을 진행한다. |
| Full gate 밖의 보조 current-runner·import·runtime smoke gate | 생략 | 같은 subject의 필수 실행이 덮는 내용은 재사용한다. V4 listing/negative-case 관찰과 uncovered consumer 확인은 필요한 작업으로 남기되 별도 gate가 아니다. |
| Confidence rerun·과거 round의 admission·release/RTC/Publish/Workshop gate | 생략 | 이 naming scope의 필수 근거가 아니며 과거 plan의 ceremony를 상속하지 않는다. 새 release/adoption 범위를 열지 않는다. |

필수 여부가 불명확하면 관련 current authority와 actual consumer만 확인한다. 확인 결과가 일반적인 내부 절차라면 구현자가 생략하고 진행하며, 실제 owner-only/protected 조건이면 해당 부분에만 적용한다. 비필수 gate를 생략하기 위한 사용자 재승인은 요구하지 않는다. 생략 이유는 기존 validation/closeout 기록에 한 줄로 남기고, 모든 생략 항목을 새 ledger로 관리하지 않는다.

Gate를 생략하는 것은 required 검증에서 실패한 것을 무시하거나 필요한 결과의 확인을 없애는 것이 아니다. Generated filename/bytes, active reference, supported compatibility와 package/install 정합은 구현 완료 조건으로 남는다. Runtime path를 바꾸고 behavior preservation을 주장하려면 bounded PZ evidence가 필요하지만 별도의 runtime 승인 위원회나 추가 seal은 만들지 않는다. 필수 근거 없는 gate의 미실행은 `blocked`나 미완료 사유가 아니며, 필수 증거 누락은 기존대로 해당 claim을 제한한다.

#### 최소 실행 구성과 구현 재량

| 구분 | 기본 실행량 / 생략·통합 기준 |
|---|---|
| 새 test file/function/validator | 기본 `0`. Rename map을 그대로 되풀이하는 테스트는 만들지 않는다. 기존 assertion/fixture를 우선 갱신하며 실제로 빠진 failure path가 확인될 때만 최소 보완한다. |
| 중간 focused checkpoint | 의무 `0회`. 개발 중 필요하면 영향을 받는 기존 node/family만 선택하며 매 Change/cluster 뒤의 고정 실행은 없다. 단순 내부 선택에는 추가 승인이 필요 없다. |
| 최종 Python focused | Full gate에 없는 affected contract만 모아 가능한 한 한 번 실행한다. T1 세 파일 전체 실행을 기본으로 하지 않는다. T2 static projection/완료 subject가 바뀌면 기존 dedicated 3-file route를 한 번 유지한다. T1도 실제 변경된 contract family만 추가하며, owner가 full route를 명시적으로 요구한 경우는 그 범위를 지킨다. |
| Runtime harness | 별도 `full`/`smoke` 반복은 기본 `0회`. V9의 registered test가 실행한 실제 `run_harness("full")` 결과로 V6를 닫는다. 미실행·skip·다른 subject이거나 uncovered path가 있으면 기존 wrapper로 빠진 범위만 보완한다. |
| Current-route·reference·dynamic inventory | Baseline 확보 및 최종 대조로 묶는다. V1/V10은 같은 census/ledger를 갱신하고 별도 검사 script를 만들지 않는다. V4의 listing/negative observation도 동일 subject의 기존 실행 결과가 있으면 재사용하며 중간마다 반복하지 않는다. |
| Fresh wheel / installed 확인 | 최종 package source별 wheel/environment 하나를 준비하고 실제 producer/inspect/gate 호출을 공유한다. `installed_inspect`가 required completion metadata이면 실제 inspect를 한 번 수행한다. Standalone import smoke를 별도로 의무화하지 않는다. |
| Fresh generation | Producer/output naming 영향 시 최종 input·implementation별 A/B 한 쌍 + 기존 finalizer. Unchanged upstream T1/DVF generation은 재실행하지 않으며 필요한 successor input만 기존 절차로 준비한다. |
| Fresh package / install | Package consumer 영향 시 최종 fresh package 하나와 격리 설치본 하나를 사용한다. 동일 산출물을 byte/membership 확인과 PZ smoke에 재사용한다. |
| Lua syntax | Lua 변경 시 사용자 지정 필수 명령 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`을 최종 상태에서 한 번 실행한다. 그 검사 대상과 byte-identical임이 확인된 generation/package/install 복사본에는 같은 syntax 검사를 반복하지 않는다. 검사하지 않은 고유 Lua bytes가 있으면 그 파일만 추가 검사한다. |
| Canonical full gate | 최종 exact subject의 Run A/B + comparator **한 체인 필수**. 각 run의 required membership은 전부 실행하며 subset/advisory로 대체하지 않는다. |
| PZ 관찰 | Runtime Lua path 영향 시 최종 격리 package에서 KO/EN을 포함하는 한 번의 bounded 검증 절차로 묶는다. 별도 baseline playtest나 cluster별 반복 관찰은 기본 요구하지 않는다. |

위 횟수는 성공 경로의 최소 기본 구성이지 실패 시 필요한 검증을 금지하는 상한이 아니다. 필요한 검증의 추가·선택은 구현자가 affected contract와 기존 evidence의 빈틈을 기준으로 결정하고 기존 실행 기록에 짧게 근거를 남긴다. 새 승인 gate나 별도 검사 계획서를 만들지 않는다. 실패 수정 또는 execution-relevant subject/input 변경으로 binding이 무효화되면 해당 검증과 필수 successor gate를 다시 실행하며, 횟수를 맞추려고 필요한 재검증을 생략하지 않는다. T1/T2 등 서로 다른 subject의 receipt를 같은 subject인 것처럼 합치지 않는다.

Evidence 재사용은 actual command/result, exact subject 또는 해당 계약이 허용하는 immutable artifact binding, 실행한 assertion/consumer 범위가 일치할 때만 가능하다. 한 결과가 여러 V-ID를 충족해도 실행 횟수는 한 번으로 기록하고, 원 command/exit/subject를 다른 명령의 PASS로 바꾸지 않는다. 특히 registered test의 존재만으로 실행됐다고 간주하지 않고 skip/누락을 확인한다. 이 규칙은 predecessor PASS 상속이나 required standalone route의 실행 생략을 허용하지 않는다.

T2 `cli.finalize()`의 `focused_tests`, `installed_inspect`, `lua_syntax`, `canonical_full_gate` completion metadata 요구는 유지한다. 기존 입력·artifact·subject에 정확히 결속된 실제 결과를 연결할 수는 있지만, byte equality나 full-gate PASS로 미실행 focused/inspect/syntax를 채우지 않는다. T2 dedicated 검사는 현재 full gate의 `not_applicable_dedicated_route`이므로 T2 successor의 완료가 필요한 경우 이 검사까지 full gate에 포함된 것으로 취급하지 않는다.

#### 검증 범위와 evidence 연결

| ID | 적용 조건 / 기존 경로 | 확인할 결과 |
|---|---|---|
| V1 Census/reference/document locator | Change 1/5/6/7의 task-local `rg`/Git/path·문서 diff 조사 | Exact rename map 대비 broken reference 및 unintended old dependency `0`. 문서별 impact/update/retain/no-update row가 actual current locator와 일치하며 original sealed text가 보존됨. No-match인 `rg`의 exit `1`은 test PASS가 아니라 검색 결과로 해석하고 도구 오류와 구분. |
| V2 Installed tooling | 최종 exact wheel + external environment의 실제 build/finalize/inspect/gate route 공유 | 새 import·dispatch·contract locator 해석, source-root fallback 없음, installed source subject 일치. 별도 import suite 없이 실제 consumer 실행을 사용하되 required inspect metadata는 유지. |
| V3 Tooltip focused | Full gate가 덮지 않는 affected T1 node/family와 applicable T2 dedicated route | 고정 T1 3-file 전수 실행 대신 실제 계약 영향으로 선택하고 가능한 한 한 번에 실행. T2 successor 완료에 필요한 dedicated route는 한 번 유지. 필수 assertion 제거, skip으로 PASS 만들기, dedicated→regular 승격 없음. |
| V4 Current-only navigation | 현재 `uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class current --list` 및 successor route | Listing exit `0`, before/after selected exact identity set의 rename map 일치. Successor CLI의 허용 selector는 current뿐이며 historical/diagnostic/all은 argument rejection으로 끝나고 tests/materialization/replay를 실행하지 않음. 이 부정 사례의 예상 nonzero는 성공한 gate exit `0`과 구분해 기록한다. Listing은 tests 실행 PASS가 아님. |
| V5 Lua syntax | 최종 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` 한 번 + 미검사 고유 Lua bytes만 추가 확인 | 정확한 명령 exit `0`. 실제 검사 file set과 fresh output/package/install의 byte identity를 연결한다. Default roots가 external package를 자동 검사한다고 주장하지 않는다. 동일 bytes에 대한 중복 syntax 실행은 생략 가능. |
| V6 Runtime harness | V9가 선택한 `BrowserStateSelectionSearchAcceptanceTest.test_actual_standalone_lua_state_and_cache_contracts`의 실제 `run_harness()` 결과 | Current wrapper에서 기본 mode는 `full`이며 Lookup/Alt/Menu와 Kahlua `next=nil` 검증을 포함한다. Gate에서 실제 실행됐으면 별도 full/smoke command를 요구하지 않는다. 빠진 범위만 `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py full` 또는 적용 가능한 기존 mode로 보완한다. `replacement`는 실제 adapter 변경의 사전 확인이 필요한 경우에만 선택. |
| V7 Deterministic generation | Installed producer의 최종 current admitted input별 fresh external A/B 한 쌍 + 기존 finalizer | Change 4와 같은 결과로 A/B Lua/manifest bytes 동일, successor filename, full exact set/KO·EN 배열 및 baseline payload bytes 보존을 확인. 새 confidence generation 없음. 실패/partial를 complete로 치환하지 않음. |
| V8 Fresh package/install | 최종 `package_iris.ps1` current_runtime_payload 산출물 하나와 그 격리 설치본 | 같은 fresh package로 member rename map, old/new 중복·missing `0`, static data/lookup, pointer-selected generation 및 설치 bytes를 확인하고 PZ 관찰에 재사용. 별도 검사용 package 반복 없음. RTC/Publish PASS는 아님. |
| V9 Canonical full gate | Installed `iris-tooling … validate full` → `invoke_receipt_bound_full_gate.ps1`, 별도 `invoke_deterministic_compare.ps1` | Exact tracked terminal subject의 Run A/B 각각과 comparator 모두 exit `0`, current environment/source binding 및 required capsule closure 유효. Archive/removal identity는 보존하고 외부 historical archive 없이 current route가 동작하는 기존 경계 유지. Focused tests로 대체 금지. |
| V10 Dynamic inventory closure | Change 1/3 inventory와 Change 6의 task-local 수동·정적 대조; 실제 resolution evidence는 V2/V4/V6/V8/V9 재사용 | 선언 scan 범위의 발견 mechanism마다 row가 존재하고 target set/pattern, cluster, 관련 V-ID, actual result 또는 retain/defer/N/A 근거가 기록됨. 새로 발견됐지만 미등록인 mechanism, 근거 없는 제외, 미설명 row 모두 `0`. Required dynamic consumer의 resolution이 미검증이면 해당 cluster는 완료 불가. |

V10은 기존 inventory 작업의 완료 조건에 붙인 task-local ID다. 새 regular test/validator/registry를 추가하거나 validation-of-validation 체계를 만들지 않는다. 이미 실행한 applicable evidence를 연결하며 임의 dynamic input 전체를 증명하거나 동일 검사를 반복하지 않는다. Inventory completeness claim은 선언한 scan 범위에 한정한다.

현재 문서에 남은 `103` route member, canonical `211 pytest + 4 standalone`, T2 `18` dedicated case는 기존 adopted 실행의 서로 다른 denominator다. 이번 census에서 actual subject의 목록을 읽고 baseline을 확정하며 숫자를 맞추려고 검사를 추가·삭제하지 않는다. Parametrization, subtest와 command wrapper를 같은 단위로 합산하지 않는다.

Tests를 옮기면 filename/node ID가 달라질 수 있으므로 exact old→new identity mapping으로 비교한다. Schema version/hash algorithm/FullType는 rename map을 적용할 대상이 아니다. Content-preserving rename과 intentional locator delta의 허용 목록을 분리하고 광범위한 문자열 정규화로 차이를 숨기지 않는다.

전체 테스트 수의 고정 감축률이나 새 collected-count 목표는 두지 않는다. 현재 코드에서 V6 wrapper의 registered test가 `run_harness()`를 호출하고 기본 mode가 `full`인 것은 확인했으므로 이 중복 실행부터 제거한다. 그 밖의 감축은 실제 applicable scope와 terminal evidence coverage에 따라 결정하며, 별도 실행을 생략한 것을 테스트 assertion 수 자체가 줄었다고 보고하지 않는다.

Python standalone 검증은 `uv run python <script>` 규칙을 따르고, installed-package execution은 기존 wheel/receipt boundary를 따른다. Java/Gradle와 JS/TS는 이 계획의 변경 범위가 아니므로 실행 대상으로 추가하지 않는다. 이후 범위가 실제로 확장되면 해당 필수 명령인 `.\gradlew test`, `pnpm biome check .`의 적용을 다시 판정한다.

이번 문서 작성·개정 자체의 확인은 템플릿 12개 항목, 코드 경로 존재, R1/R2와 보완 항목의 문구 정합, diff/whitespace 및 코드 무변경 범위에 한정한다. 위 implementation validation이나 V10의 전체 실행 inventory closure를 수행했다고 기록하지 않는다.

### Manual Validation

Runtime Lua path 변경 시 V8의 최종 fresh package로 준비한 격리 Iris 설치본에서 아래 항목을 한 번의 bounded 절차로 함께 확인한다. 항목마다 새 설치·별도 playtest·추가 보고서를 만들지 않는다.

1. Iris load 및 영향받은 Menu open 경로가 동작한다.
2. KO/EN 각각 Alt Tooltip이 current static text를 표시한다.
3. Alt 해제 시 Iris text가 사라지고 vanilla Tooltip은 보존된다.
4. 빠른 item 전환에 stale text가 남지 않는다.
5. 0줄 및 관찰 대상의 긴 문자열·중복 row가 기존 정책과 일치한다.
6. 검사한 경로에 runtime module-not-found 또는 Iris runtime error가 없다.

설치 package identity, locale, 관찰 item/시나리오와 결과를 한 기록에 남긴다. Representative item은 한 항목이 여러 관찰 조건을 함께 덮도록 최소로 선택하고 전수 표본·고정 item 수를 요구하지 않는다. 실제 오류 주입, 모든 item, 외부 mod 조합으로 확장하지 않는다. 사용자 확인이 필요한 PZ 조작이 있으면 최종 검증 가능한 package와 자동 결과를 먼저 준비한 뒤 한 번에 확인을 요청한다. 같은 package/영향 경로에 대한 성공한 관찰을 confidence 목적으로 반복하지 않는다.

### Validation Limits

- Multiplayer, long-session, 전체 item visual QA, arbitrary external-mod compatibility sweep는 하지 않는다.
- Full Menu semantic audit나 EN 재생산 evidence를 내용이 불변이라는 이유만으로 새로 요구하지 않는다. Source/input이 실제로 바뀌면 해당 영향만 재판정한다.
- Lua syntax/harness는 실제 PZ Kahlua·engine object·font/layout 관찰을 대체하지 않는다.
- Package 생성은 release acceptance, RTC certification, Publish/Workshop/deployment 승인이 아니다.
- 도구·external authority input 누락은 해당 검사 `BLOCKED`, 미실행은 `not_run`이다. Exact relevant command exit `0` 없이 PASS를 쓰지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**Touched; owner 의미 보존.** Route/index, required manifest, active/protected path 목록과 environment/capsule binding의 physical locator가 바뀔 수 있다. `iris_current_authority_manifest.json`의 protected/additive-successor 규칙을 먼저 적용한다. Live validation의 current-only 경계를 보존하며 retired executable selector를 복원하지 않는다. Authority 문서 locator 처리는 §5 Docs 및 Change 5가 소유하고 sealed 원문 보존과 current readpoint 정합을 함께 확인한다.

### Runtime Behavior Surface

**Touched.** Data/Lookup의 Lua resolution path는 실제 runtime 변경이다. 의도한 semantic/display delta는 `0`이며 raw row/string, first-use load, invalid silence, Alt OFF early return, vanilla render 보호와 Kahlua 호환 경로를 보존한다. 조사 시점 기존 Alt/harness 변경의 채택은 별도 baseline 문제다.

### Compatibility Surface

**Potentially touched; supported surface preserved.** Lua require, Python import/CLI, generated filename과 artifact manifest, package path를 조사한다. Supported facade는 유지하며 internal alias는 소비자와 수명 조건이 확인된 경우만 둔다. 실제 schema/protocol identity는 cosmetic rename하지 않는다.

### Sealed Artifact Surface

**Historical preserved; affected current binding re-evaluated.** External T1/T2 handoff/closeout, immutable environment, G5 chain, archive path/hash를 수정하지 않는다. Locator/source 변경의 successor evidence는 기존 workflow에서 발행하고 predecessor PASS를 상속하지 않는다.

### Public-Facing Output Surface

**Meaning unchanged.** Menu/Tooltip text, fact identity, classification, Layer 3 description, Recipe/Right-click meaning과 Alt 표시 계약을 변경하지 않는다. 이름 정비의 부산물로 문장 축약·정규화·중복 제거·fallback을 넣지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **High — mixed responsibility 은폐:** `d2.py`/`d5.py`를 generic 이름으로 바꾸면 lifecycle procedure가 permanent 기능처럼 보인다. 함수/consumer census와 명시적 defer로 막는다.
- **High — current/historical 혼동:** `_docs/round3` 전체 이동 또는 historical API baseline 삭제는 live gate를 깨뜨린다. File/logical asset별 판정과 successor projection을 사용한다.
- **High — retired selector 재운반:** Historical evidence 보존을 실행 모드 보존으로 오독하면 current validation authority를 확장한다. Current-only runner/argument rejection을 V4에서 확인하고 mixed asset은 defer한다.
- **Medium — governance 확대:** Census/rename ledger를 regular registry로 승격하지 않는다. Command owner와 existing owner seal 수준은 O2 판정대로 유지한다.

### Runtime Risk

- **High — generator/require 불일치:** Source만 rename하면 fresh generation에서 옛 파일이 되살아난다. C1 atomic closure, 실제 fresh output/package/harness로 확인한다.
- **High — 기존 변경 혼입:** 현재 Alt/harness dirty delta가 naming baseline에 섞이면 보존 여부를 설명할 수 없다. 착수 시 disposition하고 content delta를 별도로 기록한다.
- **Medium — interpreter 차이:** Desktop Lua 테스트만으로 Kahlua를 보장하지 않는다. `pairs`/`next=nil` fixture를 보존하고 bounded PZ smoke를 수행한다.

### Compatibility Risk

- **High — historical Git locator 파손:** T2 `admit()`의 과거 commit contract lookup에 successor path를 넣지 않는다. Historical path binding과 current locator를 분리하고 fail-closed를 유지한다.
- **High — public/internal 오분류:** Supported facade/API baseline과 실제 consumer를 조사하며 확인되지 않은 외부 사용을 무시하지 않는다.
- **Medium — alias 영구화:** Compatibility reason 없는 old/new implementation 이중 유지 금지. Alias는 같은 canonical owner에 위임한다.

### Regression Risk

- **High — gate stale binding:** Runner, taxonomy, package default, clean-checkout launcher와 audit가 서로 다른 locator를 쓰지 않도록 exact binding map으로 확인한다.
- **High — authority 문서 stale 또는 sealed rewrite:** §5의 문서별 규칙을 Change 3에서 lock하고 Change 5가 구현한다. V1은 새 current 경로의 유효성과 original sealed/historical text 보존을 함께 확인한다.
- **High — count-only 동등성:** Test/member 수가 같아도 다른 기능이 빠질 수 있다. Exact set과 rename map, missing/extra 및 내용 비교로 확인한다.
- **Medium — package 외부 검사 누락:** Default syntax roots가 external package를 검사하지 않을 수 있다. 실제 file set을 기록하고 fresh output/install 검사를 별도 수행한다.
- **Medium — 불필요한 identity 재발행:** Closure가 바뀌지 않은 G5나 unchanged terminal subject를 재검증하지 않는다. 반대로 impacted source는 predecessor evidence로 대체하지 않는다.

---

## 10. Rollback Plan

Rollback 단위는 C1–C4의 dependency cluster다. Exact before path/bytes와 existing dirty delta를 기록하고, 이 작업이 만든 변경만 되돌린다. 전체 working tree reset, unrelated 파일 삭제, historical receipt 수정은 사용하지 않는다.

1. 검증 전 실패하면 해당 cluster의 source move, import/require, generator rule, generated filename, test/fixture, route/manifest, package reference와 미채택 current docs delta를 함께 predecessor 상태로 복원한다. 이미 봉인·채택한 additive decision/trace는 삭제하지 않고 기존 절차의 후속 rollback/correction entry로 상태를 기록한다.
2. 이미 current locator를 채택했다면 existing owner workflow에서 이전 유효 implementation/binding으로 복귀시킨다. 이는 과거 PASS를 새 commit에 상속하는 뜻이 아니다. 복구 subject에 영향받은 필수 검증을 수행한다.
3. External immutable A/B/final receipt와 failure-bearing attempt는 삭제·덮어쓰지 않는다. 후속 수정은 새 attempt/root로 남긴다.
4. Package/install rollback은 격리 검증 설치본에 한정한다. Windows recursive move/delete 전 resolved absolute path가 명시한 target 안인지 검사하고 native PowerShell `-LiteralPath`를 사용한다.
5. Supported adapter가 external contract를 보호한다면 adapter retention을 canonical implementation rollback과 별도로 판정한다.
6. 일부 cluster만 완료되면 완료/복구/미완료 목록을 남기고 전체 migration `complete`라고 기록하지 않는다.

복구 후 `new producer + old consumer`와 `old producer + new consumer` 상태가 남지 않아야 한다. Historical plan/review/closeout은 rollback 대상이 아니다.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수: Hub & Spoke, 다른 Spoke 직접 의존 금지, Pulse 역의존 금지, SPI 원칙과 외부 모드 호환성 우선.
- PZ Iris runtime은 100% Lua. Offline Python 변경으로 runtime/build-time 책임을 섞지 않는다.
- Menu와 Alt Tooltip 두 surface, 최대 4줄, 근거 기반·비추천·비교 금지, item/action/game state 비변경을 유지한다.
- Supported public API와 observable compatibility를 보존한다. `IrisTooltipSummary` 등 이름 정비와 관계없는 legacy 제거는 하지 않는다.
- Current authority manifest의 `protected; additive successor required`, `owner-ratified additive successor required`, package source 변경 시 immutable environment authority 갱신 조건을 따른다.
- Current filename과 historical logical path, schema/version, generation/content identity를 구분한다. Current supporting asset의 역사적 이름이 필요한 경우 이유와 reader를 명시한다.
- Live validation은 current selector와 fail-closed current contract만 유지한다. Historical/diagnostic/all repository-local executable selector와 replay 복원은 허용하지 않는다.
- `DECISIONS.md` 원문 sealed entry는 naming을 이유로 제자리 rewrite하지 않는다. Additive readpoint/mapping, current architecture 설명, roadmap 영향 판정은 §5/Change 5가 소유한다. `EXECUTION_CONTRACT.md` §5–7의 disclosure/evidence/ceiling을 적용하며 새 design authority로 사용하지 않는다.
- Approval은 path 이름만이 아니라 affected exact successor delta에 결속한다. Machine PASS, review, owner adoption/seal은 서로 대체하지 않는다.
- O1–O3은 unresolved defect나 계획 단계 blocker가 아닌 scope-lock decision gate이며 Change 3에서 닫는다. 제안을 이미 결정된 authority로 사용하지 않는다. 기존 권한으로 처리 가능한 내부 선택은 자율적으로 수행하되 필요한 owner 판정·protected 변경 절차를 우회하지 않는다.
- Integrated Review의 원 verdict는 §4.3의 historical trace로 보존한다. 필수 근거 없는 추가 review/verdict/seal gate는 생략하며, 작성자의 계획 수정은 독립 review credit이나 owner seal이 아니다.
- 새 naming test framework, regular validator, 별도 manifest authority를 만들지 않는다. 기존 test assertion/contract를 유지하면서 필요한 path fixture만 변경한다.
- 테스트 최소화는 중복 invocation 제거와 영향 범위 선택으로 수행한다. 중간 checkpoint·새 테스트·별도 import/runtime-smoke suite는 기본 의무가 아니며 §7의 terminal evidence를 공유한다. Mandatory full A/B, 필요한 dedicated route, exact-subject/negative-case/isolation 계약을 약화하지 않는다.
- 비필수 gate는 §7에 따라 생략한다. O1–O3/Change 1–7의 구현 판단과 required outcome을 별도 승인 gate로 승격하지 않으며, 생략을 허가받기 위한 새 gate도 만들지 않는다.
- 최소 diff와 기존 변경 보존. 과거 계획의 특정 branch/attempt/시간 예산/일회성 승인 조건을 이번 작업에 자동 상속하지 않는다.
- Git publication, product Publish, deployment와 release readiness는 이 실행 계획의 명명 완료와 별개다.

---

## 12. Expected Closeout State

목표는 **승인된 naming migration scope의 `complete`**다. 2026-08-30 실행 상태와 exact map, 검증 결과·보류 사유는 `docs/iris_current_responsibility_naming_alignment_closeout.md`에 기록한다. 아래는 변경하지 않은 원래 완료 조건이다.

| 축 | Complete 조건 |
|---|---|
| Inventory/disposition | 선언 scope 조사, unclassified current candidate `0`, V10 미설명 dynamic entry `0`, mixed follow-up과 retained reason 완비. |
| Implementation | 채택된 모든 rename target의 source/producer/consumer/binding 이동 완료. Unintended old implementation 중복 없음. |
| Generation/package/install | Fresh successor filename 직접 생성, Lua 내용 보존, expected exact member/byte parity, unintended duplicate/missing `0`. |
| Current route/authority | Actual successor locator, current-only selector, required membership 및 environment/source/capsule subject 일치. Retired executable selector 재도입 없음. Historical evidence 원형 보존. |
| Authority documentation | §5 문서별 update/retain/no-update 판정과 실제 결과 일치. Stale current locator `0`, sealed/historical 원문 무단 rewrite `0`, additive trace와 owning Change 확인. |
| Machine validation | §7의 최소 실행 집합으로 applicable focused/installed/generation/package 및 canonical Run A/B/comparator를 충족. 같은 actual evidence를 여러 확인 축에 연결할 수 있으며 required command exit `0`과 exact binding을 보존. |
| Runtime | Lua path 변경 시 격리 package의 bounded PZ observation 완료. 다른 subject의 T3 결과를 재사용하지 않음. |
| Trace/convention | Durable old→new map, final retained ledger, O2에 따른 작은 convention, scope/ceiling/non-claim 기록. |
| Review/owner | 실제 필수인 기존 review/owner 절차만 수행하고 상태와 exact subject를 기록. 비필수 추가 gate는 생략하며 그 미실행을 완료 blocker로 두거나 Machine PASS로 채우지 않음. |

Mixed-responsibility 항목을 scope lock에서 명시적으로 defer한 경우 승인된 rename scope의 완료와 structural follow-up을 구분할 수 있다. 비용 때문에 남겨둔 순수 current durable stage-name은 O3의 별도 결정 없이 성공으로 닫지 않는다. O3 예외를 승인받더라도 해당 잔여가 있는 상태에서 전체 naming problem 해결을 주장하지 않는다. 초기 census와 최종 scope 차이도 공개한다.

코드만 바뀌고 필수 검증이 남으면 `implemented_only`, 일부 cluster만 닫혔으면 `partial`, 필수 도구·authority input·owner 판정이 없으면 해당 축 `blocked`다. §7에서 비필수로 생략한 gate는 미완료 항목에 넣지 않으며 PASS로 꾸미지도 않는다. Runtime Lua path를 바꾸고 PZ 검증이 없으면 전체 behavior-preservation 완료를 주장하지 않는다.

최대 claim은 다음 범위다.

> 선언하고 승인한 Iris current repository scope에서 작업 세션·단계 중심 이름으로 판정된 durable path를 기능·책임 중심 이름으로 정렬했으며, affected producer/consumer/runtime/tooling/generation/package/install/current-route reference와 필요한 successor binding을 검증했다. Historical, one-off, domain/version, supported compatibility 및 명시적으로 보류한 mixed responsibility는 이유와 함께 보존했다. Runtime behavior preservation은 실제 관찰한 subject와 경로에만 귀속된다.

All repository naming perfect, architecture redesign complete, mixed files resolved, all legacy removed, full external-mod compatibility, runtime performance improvement, DVF freeze, RTC/Publish/release/Workshop/deployment PASS는 주장하지 않는다.
