# Iris Responsibility/Repository Build/Validation Refactoring Walkthrough

> Session date: 2026-08-25 KST  
> Current status: `complete` within the stated validation ceiling  
> W0 baseline: `22e94077dd057a943ba2e6ff03f25f5880b3126c`  
> Validated terminal implementation: `d3dfec94c45cb21d27ac54120e2551532ded3e9b`  
> Validated terminal tree: `54223d37e8deeaf26c8a0fcaf073ea1ab171cd64`  
> Completed closeout carrier: `0944368546a323d2bee0498295dad9465066d9e3`  
> Top-document synchronization: `8d0283604cb261567708f75c053a5556783c4761`
> Bounded correction baseline: `0311718b2334fc3b45908b2f0d2117c7dc57569a`
> Bounded correction validated terminal: `cbfb4f2e0067413f5334b1ca40c3cd89a090606a`
> Bounded correction terminal tree: `afcf40cc7b4003571fc137c89d7b99d2042e9d9b`
> Boundary-hardening implementation terminal: `377601a199d661513288b7f68f920b1bf53f0aad`
> Boundary-hardening wheel writer: `584903590b7e45b6919b55ee8b63d87226de1446`
> Boundary-hardening machine-validation subject: `d586dc0c88657c1e340b00bb2798268caacc9fca`
> Boundary-hardening Reviewer carrier: `d6db16dc41e94fdf99dc124fdef139cfd9d05994`

## 1. Document Role

이 문서는 `docs/iris_responsibility_repository_build_validation_refactoring_plan.md`에
따라 수행된 W0–W10 구현, terminal validation, owner bounded PZ probe와 closeout을
한 흐름으로 설명하는 narrative walkthrough다.

이 Walkthrough는 다음 역할을 갖지 않는다.

- Canonical validator, 새 validation authority 또는 새 closeout state가 아니다.
- Adopted plan, environment authority, terminal receipt 또는
  `Iris/_docs/refactor/responsibility_repository_refactor/implementation_closeout.json`을
  대체하지 않는다.
- 세션 중 사용한 read-only byte/line 집계나 외부 PZ console 진단을 정규 검사기로
  승격하지 않는다.
- Release/freeze/RTC/Publish/deployment, 모든 외부 모드 compatibility, runtime
  performance 또는 실제 GPT/Codex token 절감률을 승인하지 않는다.

## 2. Starting Point and Boundary

W0는 comparator의 environment restoration을 교정한 commit
`22e94077dd057a943ba2e6ff03f25f5880b3126c`에서 시작했다. 이 subject의 clean
Run A/B, deterministic comparator와 standalone validation 4개가 PASS해 실제
baseline으로 채택됐다.

작업은 다음 경계를 유지했다.

- Iris는 정보 표시 전용 spoke이며 Project Zomboid 전역 reload/context-menu
  동작을 소유하지 않는다.
- Current authority와 owner는 단일화하지만 historical/staging/evidence/frozen
  predecessor의 물리 파일은 계획이 요구하지 않는 한 삭제하지 않는다.
- Description v2 predecessor source는 reproduction material로 남기고 current
  consumer만 설치형 package로 이동한다.
- Source Layer 3 inactive generation과 legacy fixed chunks는 rollback/bootstrap
  predecessor로 보존하되 current package에는 싣지 않는다.
- Owner approval gate는 세션 시작 시 project owner가 미리 승인했다.
- 계획에 명시된 테스트만 마지막 terminal batch에 모아 실행했으며 ad hoc
  inspection을 canonical validation으로 취급하지 않았다.

## 3. Successor Decisions

W1 commit `e455fc21d50d78d529251e0327ef082a9e327e66`은 구현 전에 다음 successor
결정을 채택했다.

- `IrisBulletReloadCompat`와 `IrisContextMenuTextureCompat`는 다른 모듈로
  이동하거나 복제하지 않고 삭제한다.
- 삭제 뒤 Iris가 보장하는 것은 PZ 전역 함수의 non-interference다. 임의 외부
  모드 조합의 compatibility는 `unvalidated_but_in_scope`다.
- Listed `IrisData`, Browser `build/getGroupVariants`, Wiki render facade는 thin
  compatibility adapter로 보존한다.
- Layer 3 package는 current pointer-selected generation 하나만 포함한다.
- Current Description v2/right-click owner는 locked installable `iris_tooling`
  package로 이동한다.

Baseline adoption, successor decision과 current migration map은
`Iris/_docs/refactor/responsibility_repository_refactor/`에 기록했다.

## 4. Implementation Waves

| Wave | Commit | Result |
| --- | --- | --- |
| W2 | `35a3a1f4` | Iris global bullet-reload replacement와 context-menu render wrapper 및 install path 제거 |
| W3 | `996724ba` / authority `707f1f59` | Locked installable `iris_tooling` package, explicit repository context와 immutable environment authority 도입 |
| W4 | `3a02185a` / authority `652cab65` | Public-text input/evaluation/naturalization/emission 책임 분리 |
| W5 | `c1128b96` / authority `0c087738` | Right-click current pipeline을 v2.4 하나로 제한하고 capability/infra/pipeline owner 분리 |
| W6 | `96fec29b` | Package projection을 current Layer 3 generation-only로 변경 |
| W7 | `bfd78aa5` | Browser monolith를 projection builder, lifecycle, metrics와 supported facade로 분리 |
| W8 | `05809f54` | Detail engine fact reader, immutable model assembler와 presentation policy 분리 |
| W9 | `5e810430` | Listed compatibility facade를 thin adapter로 격리하고 내부 legacy fallback/no-op build surface 제거 |
| W10 | `792917ca` onward | Current manifests, entrypoints, validation binding, terminal environment와 closeout 정렬 |

### Offline tooling

Current offline build entrypoint는 `Iris/tooling/src/iris_tooling`이다. CLI는
`--repository-root`로 repository context를 명시적으로 받고 installation path나 cwd를
root로 추측하지 않는다. Current imports와 successor test source의 `sys.path`
bootstrap은 0이며 `Iris/build/description/v2/tools/build`는 current command authority가
아닌 reproduction predecessor다.

Right-click CLI는 v2.4만 지원한다. Classification, Layer 3, Layer 4와 public-text도
같은 installed package 아래에서 domain별 owner를 갖는다.

### Runtime responsibility

Browser runtime은 다음 경계로 나뉜다.

`projection builder -> generation lifecycle -> diagnostic metrics -> IrisBrowserData supported facade`

Detail runtime은 다음 경계로 나뉜다.

`IrisItemFactReader -> IrisItemDetailModelAssembler -> IrisItemDetailPresentation -> Browser/Wiki/Alt Tooltip`

FactReader는 engine 접근과 tri-state fact를 소유하고 assembler는 UI가 소비할
immutable model을 만든다. Unit/visibility 결정은 presentation policy에서 공유한다.
Supported facade의 signature/result shape는 유지하지만 facade가 독립 legacy payload를
다시 소유하지 않는다.

### Package projection

`Iris/tools/package_iris.ps1`은 current pointer가 선택한 immutable Layer 3 generation
하나만 package에 투영한다. Source tree의 inactive generation 3개와 legacy fixed chunk
11개는 변경·삭제하지 않지만 package output에는 존재하지 않는다. Pointer, descriptor,
chunk/index와 package lookup identity가 같은 generation을 가리키지 않으면 fail-closed한다.

## 5. Terminal Corrections and Exact Subject

초기 W10 adoption 뒤 clean full gate가 드러낸 validation/package ownership 문제는
terminal subject 전에 같은 구현 범위 안에서 교정했다.

| Commit range | Correction |
| --- | --- |
| `db6c0e5b..9f22b0be` | Superproject cleanliness, terminal environment binding, residual locale reset, global-patch absence axis와 authority line endings 정렬 |
| `d715c9ec..4a3806e0` | Explicit current source census, package migration을 가로지르는 G5 identity, compiler aggregate와 tracked package source 정렬 |
| `132dce2f..fbbe7925` | Installed compiler import boundary 완성, terminal environment v4와 final compiler identity 결속 |
| `2e160745..d3dfec94` | Successor owner contract, guard mock namespace와 terminal projection identity 정렬 |

최종 machine-validation subject는
`d3dfec94c45cb21d27ac54120e2551532ded3e9b`, tree
`54223d37e8deeaf26c8a0fcaf073ea1ab171cd64`다. 사후 closeout/documentation
carrier는 이 subject를 다시 정의하지 않는다.

Terminal environment v4는 다음 authority chain으로 결속된다.

`responsibility_refactor_environment_current.json -> responsibility_refactor_environment_terminal_v4.json -> external environment receipt -> installed wheel/interpreter manifest`

External receipt SHA-256은
`8c158f61990c4fbc2e2706d4375743cc0261470433a545c7a1d75b5733d5f941`다.

## 6. Automated Validation

계획에 명시된 terminal validation 결과는 다음과 같다.

| Validation | Result |
| --- | --- |
| Focused affected batch | `20 passed / 14 subtests` |
| Installed `iris_tooling` tests | `17 passed` |
| Installed package CLI | PASS |
| Repository 밖 arbitrary-cwd terminal CLI | PASS |
| Lua syntax | `174 files` PASS |
| Clean Run A | pytest `202`, subtests `109`, standalone `4`, exit `0` |
| Clean Run B | pytest `202`, subtests `109`, standalone `4`, exit `0` |
| Deterministic comparator | `succeeded`, exit `0` |

Run A/B canonical result SHA-256은 모두
`ecdcb453fd2b6e98d922a3a886e870828e3a89e88d1e308348370402b1d72326`이다.
Comparator receipt SHA-256은
`47ec5b00f5d9e0bd9841d4d3fb7946aa567d8b5771894b7bca7f1c931f6f3d5e`다.

Run A/B와 comparator의 실제 path/hash 연결은
`Iris/_docs/refactor/responsibility_repository_refactor/implementation_closeout.json`에
있다. 이 Walkthrough는 그 receipt를 복제하거나 새 gate를 만들지 않는다.

## 7. Bounded PZ Probe and External-Mod Observation

Repository owner는 Iris-only supported 환경에서 다음 bounded probe를 수행했다.

- PZ boot와 save load 정상
- Iris Browser search/selection 정상
- Detail, Wiki와 Alt Tooltip 정상
- Firearm/ammunition reload menu와 동작 정상
- Inventory/world context menu 정상
- Lua 오류와 명백한 회귀 없음

첫 실행은 CheatMenuRebirth가 함께 활성화된 상태였다. 이 조합에서는 context menu가
열린 뒤 vanilla `ISContextMenu.render` line 475가 null `tickTexture`에
`getWidthOrig()`를 호출하며 약 86초 동안 exception cycle 317개를 기록했다.

Historical `IrisContextMenuTextureCompat`는 바로 이 null을 fallback texture로 바꾸던
global render wrapper였다. 현재 Iris product code는 `tickTexture`를 설정하지 않고,
계획은 해당 patch를 non-interference 원칙에 따라 복원하거나 다른 spoke로 이전하지
않도록 결정했다. 외부 모드를 끄고 Iris-only로 재검증했을 때 오류는 전혀 발생하지
않았다.

따라서 판정은 다음과 같다.

- Supported Iris-only bounded probe: PASS
- CheatMenuRebirth-enabled combination: compatibility PASS 아님
- Arbitrary third-party mod combinations: `unvalidated_but_in_scope`
- Global context-menu patch restoration: 하지 않음

외부 `console.txt` 조회는 이 원인을 진단한 일회성 입력이며 repository authority나
tracked proof artifact가 아니다.

## 8. Physical and Efficiency Boundary

정량 observation의 exact range는 W0 baseline `22e94077`에서 completed closeout
carrier `09443685`까지다.

### Package payload

| Layer 3 package-related payload | Bytes |
| --- | ---: |
| Four source generations | `9,682,320` |
| Legacy fixed chunks | `968,181` |
| Predecessor package-visible total | `10,650,501` |
| Current selected generation | `1,954,408` |
| Package-excluded delta | `8,696,093` (`81.65%`, 약 `8.29 MiB`) |

이 `81.65%`는 Layer 3 generation/fixed payload 범위다. 전체 mod ZIP 감소율이나
source repository 삭제량이 아니다.

### Product and repository

- Tracked product Lua `Iris/media/lua/client/Iris`:
  `12,796,668 -> 12,718,204` bytes, `78,464` bytes(`0.61%`) 감소.
- Product Lua changed-line net: `1,159` additions, `2,599` deletions,
  net `1,440` lines 감소.
- Repository 전체 tracked blob:
  `790,473,779 -> 791,495,072` bytes, `1,021,293` bytes(`0.13%`) 증가.
- 새 installable `iris_tooling` source는 `851,379` bytes이며 predecessor source는
  reproduction material로 보존됐다.

따라서 current package/runtime surface는 좁아졌지만 repository physical
lightweighting은 달성하지 않았다. Naive full-repository scan byte proxy도 개선됐다고
말할 수 없다.

Runtime wall-clock/CPU/memory/FPS와 실제 GPT/Codex prompt selection, cache hit,
input/output/tool token telemetry는 계측하지 않았다. Owner/entrypoint 단일화와 explicit
repository context는 유지보수·탐색 경계를 개선하지만 확정 performance/token
개선률은 없다. 이 read-only 집계는 canonical metric이나 validator가 아니다.

## 9. Closeout and Documentation

Automated validation 뒤 commit `7f18092c`는 manual probe가 남은 상태를 정직하게
`partial`로 기록했다. Repository owner의 Iris-only bounded probe PASS 뒤
`0944368546a323d2bee0498295dad9465066d9e3`에서 closeout을 stated validation ceiling
내 `complete`로 갱신했다.

`8d0283604cb261567708f75c053a5556783c4761`은 `ARCHITECTURE.md`, `DECISIONS.md`와
`ROADMAP.md`를 구현 구조, terminal/manual validation, external-mod ceiling과 physical
measurement boundary에 맞춘 documentation-only readpoint다.

Current readpoints는 다음과 같다.

- Plan: `docs/iris_responsibility_repository_build_validation_refactoring_plan.md`
- Architecture: `docs/ARCHITECTURE.md`
- Decisions: `docs/DECISIONS.md`
- Roadmap: `docs/ROADMAP.md`
- Entrypoints: `Iris/build/ENTRYPOINTS.md`
- Current migration map:
  `Iris/_docs/refactor/responsibility_repository_refactor/current_migration_map.json`
- Closeout:
  `Iris/_docs/refactor/responsibility_repository_refactor/implementation_closeout.json`
- Environment locator:
  `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`

## 10. Final State and Non-Claims

Governing plan의 W0–W10 구현, exact-subject terminal validation과 supported Iris-only
bounded PZ probe는 완료됐다. Formal closeout state는 stated validation ceiling 안에서
`complete`다.

이 closeout은 다음을 주장하지 않는다.

- 모든 외부 모드 조합과 삭제한 patches의 과거 방어 효과 보존
- Release/freeze/RTC/Publish/deployment 또는 Workshop readiness
- 장시간 multiplayer/dedicated-server matrix
- Project Zomboid 기본 동작의 byte/behavior equivalence
- Repository physical lightweighting 완료
- Runtime performance 또는 실제 GPT/Codex token 효율 개선률

Historical/predecessor 물리 삭제, output/media 중복 제거와 별도 lightweighting은 이
계획의 완료 조건이 아니며 후속 authority 없이는 이 Walkthrough로 열리지 않는다.

## 11. Bounded Public-Text Correction Wave

### 11.1 Why the correction was opened

완료 처리된 1차 refactor를 다시 설계한 것이 아니다. W4에서 책임 이름과 package
boundary는 나뉘었지만, 실제 implementation은 여전히 다음 두 파일에 집중돼 있었다.

| Pre-correction file | Lines | Correction result |
| --- | ---: | --- |
| `build/public_text_quality_acceptance.py` | `5,107` | `3`줄 compatibility façade |
| `build/run_dvf_3_3_korean_prose_naturalization.py` | `4,095` | `8`줄 compatibility façade/entrypoint |

또한 naturalization source에는 세 개의 사용자 attachment absolute path가 default로,
non-current right-click capability에는 한 개의 PZ media absolute path가 남아 있었다.
Current right-click CLI가 해당 capability를 소비하지 않는데도 module이 wheel에 포함되는
상태였다.

이 wave는 이 네 가지 잔여 문제만 대상으로 삼았다. Validation consolidation, broader
lightweighting, runtime/UI/package 변경과 retired compatibility patch 복원은 열지 않았다.

### 11.2 Implemented owner split

Acceptance의 responsibilities는 다음 owner들로 이동했다.

| Responsibility | Owner |
| --- | --- |
| Repository context/constants | `acceptance_context.py` |
| Git, filesystem, strict JSON, write-once mechanics | `acceptance_infrastructure.py` |
| Contract parsing/identity | `acceptance_contracts.py` |
| Evaluation rules | `acceptance_rules.py` |
| Report projection | `acceptance_reporting.py` |
| Artifact emission | `acceptance_emission.py` |
| Foundation application | `acceptance_foundation_application.py` |
| Attempt lifecycle/VCS preflight | `acceptance_attempt_context.py` |
| Policy phases | `acceptance_policy.py` |
| Adversarial assurance | `acceptance_assurance.py` |
| Phase dispatch/disposition | `acceptance_disposition.py` |
| Validation API | `acceptance_validation.py` |
| Run/validation command surfaces | `acceptance_cli.py`, `acceptance_validation_cli.py` |

Naturalization은 context, infrastructure, preparation, projection, transformation, review,
handoff와 application owner로 분리했다. `public_text.cli`는 `naturalization`,
`acceptance`, `acceptance-validate` command를 각 owner로 전달한다.

옛 acceptance 파일은 기존 import consumer가 validation symbols를 계속 찾을 수 있도록
재수출만 한다. 옛 naturalization runner는 application symbols, parser와 `main`을
재수출하고 direct script invocation을 domain CLI로 전달한다. 이 호환 책임 때문에 두
façade를 완전히 삭제하지 않았다.

### 11.3 Explicit context and right-click disposition

Phase 0 provenance는 `NaturalizationProvenanceInputs`와
`--roadmap-input`, `--plan-review-input`, `--cycle2-review-input`으로 명시한다. 세
attachment path는 더 이상 source default가 아니다. Repository source 파일을 결속할
때도 installed wheel의 `__file__`을 source root로 해석하지 않고
`--repository-root`가 설정한 repository context를 사용한다.

`rightclick/capability.py`는 현재 consumer graph에서 old test만 소비했고 current CLI는
이미 `pipeline_v24.py`만 호출했다. 따라서 capability module `633`줄을 current package에서
제거하고 tests를 실제 v2.4 contract와 package exclusion에 맞췄다. Historical
`Iris/evidence/rightclick/pipeline.py`는 그대로 남겼으며 current authority로 승격하거나
삭제하지 않았다.

### 11.4 Terminal corrections discovered by the final gate

최종 검증에서 세 가지 owner-boundary defect를 확인하고 같은 범위 안에서 수정했다.

- Legal rendered input의 `body_plan: null`을 빈 plan으로 census한다.
- Acceptance infrastructure가 사용하는 Git helper를 실제 infrastructure owner로 옮겼다.
- Repository source identity는 installed package 경로가 아니라 explicit repository
  context의 source path로 계산하고, constituent tests도 실제 함수 owner를 patch한다.

G5 current compiler identity는 append-only successor 0006으로 갱신했고 terminal-v9
wheel/environment/receipt를 exact implementation commit에 결속했다. 실패했던 중간
environment/receipt leaf와 probe leaf는 재사용하거나 current authority로 승격하지
않았다.

### 11.5 Validation result

Machine-validation subject는 `cbfb4f2e0067413f5334b1ca40c3cd89a090606a`, tree는
`afcf40cc7b4003571fc137c89d7b99d2042e9d9b`다.

| Validation | Result |
| --- | --- |
| Focused affected batch | `24 passed in 32.39s`, exit `0` |
| Installed arbitrary-CWD naturalization | adversarial fixture `8/8`, required failure reason `8/8`, exit `0` |
| Explicit-root current right-click | candidate `1,470`, PASS `57`, NO `1,400`, REVIEW `13`, exit `0` |
| Lua syntax | `174 files`, exit `0` |
| Clean Run A | pytest identity `205`, subtest `109`, standalone `4`, exit `0` |
| Clean Run B | pytest identity `205`, subtest `109`, standalone `4`, exit `0` |
| Deterministic comparator | `succeeded`, exit `0` |
| Installed arbitrary-CWD `--help` | exit `0` |

Run A/B canonical result SHA-256은 모두
`ba7049aec35a76f175136996c6fb8cf1dc10140bb801dcea93d26db7f5b38819`다.
Comparator fingerprint SHA-256은
`3ee8c24d433e2bbc72cafdc0f6334e91c4d3b85ba164784cb6616c766a1faa16`이다.
Source checkout과 clean clone의 post-status는 clean이고 external execution mutation은
`0`이다.

### 11.6 Size and claim boundary

Correction baseline에서 terminal까지 `Iris/tooling/src`는 `9,715` additions와
`10,069` deletions로 net `354` lines 감소했다. 두 monolith의 façade 자체는 각각
`5,107 -> 3`, `4,095 -> 8` lines로 줄었지만 implementation은 명시적 owner modules로
이동했으므로 이 비율을 전체 구현량 감소로 읽으면 안 된다. Append-only G5/environment
authority와 focused contracts를 포함한 tracked tree 전체는 문서 전 terminal에서 net
`620` lines 증가했다.

따라서 확인된 개선은 owner locality, entrypoint 명료성, machine-local default 제거와
non-current wheel surface 축소다. Runtime wall-clock/CPU/memory/FPS와 실제
GPT/Codex prompt/cache/token telemetry는 측정하지 않았으므로 performance 또는 token
효율 개선률은 주장하지 않는다. 이 집계는 Walkthrough 설명용 일회성 observation이며
canonical validator, seal, receipt 또는 metric authority가 아니다.

Product Lua, UI, package/public-text output schema와 의도된 runtime behavior 변경은 없다.
CheatMenuRebirth 조합은 계속 compatibility nonclaim이며 global context-menu patch는
복원하지 않았다. 기존 owner-attested Iris-only PZ boot/save load, Browser/Detail/Wiki/Alt
Tooltip, reload/context-menu PASS의 범위를 universal external-mod compatibility로 넓히지
않는다.

## 12. Public-Text Responsibility-Boundary Hardening Wave

### 12.1 Scope and resulting graph

이 wave는 bounded correction을 재설계하지 않았다. 남아 있던 transitive wildcard namespace, dynamic `__all__`, 실제 installed-wheel Phase 0 explicit-input 증빙과 terminal 귀속만 닫았다. 대상 25개 owner/CLI/application/façade에서 `import *`와 `globals()` export는 0건이다.

Owner별 직접 dependency는 다음처럼 고정됐다. 표의 dependency는 module 단위 요약이며 각 module source가 실제 symbol-level import와 fixed tuple export를 authority로 가진다.

| Owner | Direct public-text dependencies |
| --- | --- |
| `inputs` | 없음 |
| `acceptance_context` | repository context, compiler identity |
| `acceptance_infrastructure` | `acceptance_context`, `inputs` |
| `acceptance_contracts` | `acceptance_context`, `acceptance_infrastructure` |
| `acceptance_rules` | `acceptance_context`, `acceptance_contracts`, `acceptance_infrastructure`, `evaluate` |
| `acceptance_reporting` | `acceptance_context`, `acceptance_infrastructure`, `acceptance_rules` |
| `acceptance_emission` | `acceptance_context`, `acceptance_infrastructure` |
| `acceptance_foundation_application` | context, contracts, emission, infrastructure, reporting, rules |
| `acceptance_attempt_context` | context, emission, foundation application, infrastructure, reporting, rules, compiler identity |
| `acceptance_policy` | attempt context, context, emission, infrastructure, rules |
| `acceptance_assurance` | attempt context, context, emission, infrastructure, policy, rules |
| `acceptance_disposition` | assurance, attempt context, context, emission, infrastructure, policy, rules |
| `acceptance_validation` | assurance, attempt context, context, disposition, infrastructure, policy, rules |
| `acceptance_cli` | context, disposition, foundation application, infrastructure |
| `acceptance_validation_cli` | context, foundation application, infrastructure, validation |
| `naturalization_context` | repository context, compiler identity |
| `naturalization_infrastructure` | `inputs`, `naturalization_context` |
| `naturalization_preparation` | inputs, context, infrastructure, compose text |
| `naturalization_projection` | context, infrastructure, compose profile/identity/text, compiler identity |
| `naturalization_transformation` | context, infrastructure, projection, compose text, compiler identity |
| `naturalization_review` | naturalization detector, context, infrastructure, projection |
| `naturalization_handoff` | context, infrastructure, projection, transformation |
| `naturalization_application` | inputs, infrastructure, preparation, projection, transformation, review, handoff |
| `public_text.cli` | `inputs`; command별 acceptance/naturalization owner를 lazy import |
| Build façades | 위 owner의 호환 symbol만 명시적으로 import/re-export |

Cross-owner에서 사용되는 helper는 `run_git`, `parse_policy_timestamp`, `without_volatile_fields`, `manifest_binding_rows`, `load_phase0_context`, `require_phase2_seal`처럼 public contract 이름을 갖는다. `_private` helper import는 0건이다.

### 12.2 Exact compatibility façade exports

Acceptance façade의 fixed API는 다음과 같다.

```text
DISPOSITION_CLASSES, FOUNDATION_SCHEMA_VERSION, FoundationContractError,
NATURALIZATION_COMPILER_IMPLEMENTATION_FILES, PHASE0_REQUIRED_VCS_CONSUMERS,
REPO_ROOT, TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID, build_compiler_identity,
build_foundation, build_protected_snapshot_identity_from_bytes,
build_protected_snapshot_present_row_from_bytes,
build_text_constituent_identity_from_bytes, canonical_hash,
compute_candidate_metric_snapshot, evaluate_threshold, handoff_artifact_path,
head_text_constituent_record, human_review_blocker_count, is_ignored, is_tracked,
load_json_strict, normalize_text_line_endings, phase0_required_vcs_preflight,
pretty_json_bytes, repo_relative, run_official_mode, sha256_file,
validate_candidate_handoff, validate_foundation, validate_official_attempt,
write_once_or_same
```

Naturalization façade의 fixed API는 다음과 같다.

```text
COMPILER_IMPLEMENTATION_PATHS, EVALUATION_SUBJECT_KIND,
EXPECTED_COMPILER_FIX_COMMIT, EXPECTED_CURRENT_FACTS_SHA256,
EXPECTED_CURRENT_MANIFEST_SHA256, EXPECTED_FOUNDATION_CONTRACT_SHA256,
EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
EXPECTED_FOUNDATION_READINESS_SHA256,
EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
EXPECTED_PARTICLE_CORRECTION_COMMIT,
EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256,
EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256, EXPECTED_START_COMMIT,
EXPECTED_START_TREE, FOUNDATION_CONTRACT,
FOUNDATION_READINESS_CORRECTION_REBIND,
FOUNDATION_READINESS_CURRENT_INPUT_REBIND, NaturalizationError,
PARTICLE_CORRECTION_PROJECTION_REPORT, PRESERVED_PREDECESSOR_ATTEMPT_IDS,
REGISTRY_ADOPTION_CONTRACT, REGISTRY_NATURALIZATION_HANDOFF, REPO_ROOT,
attempt_root_for, build_compiler_identity, build_parser, canonical_hash,
implementation_hash, implementation_identity, load_json, main, phase_root,
run_naturalization_mode, sha256_file
```

두 façade에는 함수·class 정의가 없고 공개 namespace는 각각 이 목록과 일치한다.

### 12.3 Installed-wheel Phase 0 and validator correction

Final wheel은 `C:\Users\MW\irf\wheel-terminal-v15\iris_tooling-0.1.0-py3-none-any.whl`이며 SHA-256은 `b8fed67c1f453fa3ba12fc8b90cb6dfac176f3ce783ef060ff88a683384d298f`다. Environment receipt는 `C:\Users\MW\iccv\receipts\env-iris-refactor-terminal-v15\environment_receipt.json`, SHA-256 `dde23f3df4532e40d98a2117829820963e22110e796545e50986223d89e4f3e8`이다.

Repository 밖 `C:\Users\MW\irf\v15p\c`에서 다음 실제 positive route를 실행했다.

```powershell
C:\Users\MW\iccv\env-iris-refactor-terminal-v15\Scripts\python.exe -B -s -m iris_tooling `
  --repository-root C:\Users\MW\irf\v15p\r public-text naturalization `
  --attempt-id attempt-0027-hardening-phase0-positive --mode phase0-preflight `
  --attempt-root C:\Users\MW\irf\v15p\p `
  --roadmap-input C:\Users\MW\irf\v13p\i\roadmap.txt `
  --plan-review-input C:\Users\MW\irf\v13p\i\plan-review.txt `
  --cycle2-review-input C:\Users\MW\irf\v13p\i\cycle2-review.txt
```

세 binding role의 explicit path, expected/actual SHA와 `hash_match=true`, blocker `0`, status `PASS`, exit `0`을 확인했다. 같은 attempt에 installed wheel의 formal naturalization validator를 `--require-phase0 --no-write`로 실행해 `errors=[]`, `status=PASS`, exit `0`을 확인했다.

첫 Reviewer는 builder가 current manifest/source를 따르는 반면 validator가 historical fixed current hash와 historical particle bytes equality를 요구하는 P1을 발견했다. Validator가 canonical `INPUT_MANIFEST`와 실제 source rows를 재계산하도록 수정하고, historical registry/foundation identities는 고정한 채 particle projection `after_sha256`과 current implementation hash를 별도로 검증하게 했다. 이 보정 뒤 builder와 validator가 같은 authority 계약으로 PASS했다.

Cycle-2 input을 생략한 negative command는 정확한 required-three-input 오류와 exit `2`를 반환했고 `C:\Users\MW\irf\v15p\n`을 만들지 않았다. Source checkout과 clean clone status는 모두 clean이다. 이 external attempt output은 canonical validator나 repository authority로 승격하지 않는다.

### 12.4 Exact attribution and terminal result

| Role | Commit / tree |
| --- | --- |
| Package implementation terminal | `377601a199d661513288b7f68f920b1bf53f0aad` / `c7f082763ba92492a4f75b25b07595d0926a805f` |
| Exact installed-wheel source/writer | `584903590b7e45b6919b55ee8b63d87226de1446` / `10ff8ea79914241314f59b5e652dbf7f81562bb7` |
| Machine validation/environment authority subject | `d586dc0c88657c1e340b00bb2798268caacc9fca` / `05de8fafbf86045dd9fa7f93aeee0c96873cf0c6` |
| Independent Reviewer carrier | `d6db16dc41e94fdf99dc124fdef139cfd9d05994` / `f3ff2cc1a53469ac54424957d93034418addb1da` |

세 implementation/wheel/machine subject의 `Iris/tooling/src` tree는 `365e7686cb53a2b0e10f7de4421eb2e4f9f4274e`로 동일하다. Reviewer와 documentation carrier는 machine PASS를 상속하거나 재정의하지 않는다.

| Validation | Final result |
| --- | --- |
| Focused owner/façade/import/package/right-click contracts | `68 passed in 94.79s` |
| Installed Phase 0 positive + formal validator | 둘 다 `PASS`, exit `0` |
| Missing-input negative | exit `2`, output root 미생성 |
| Explicit-root right-click | candidates `1,470`; PASS `57`, NO `1,400`, REVIEW `13` |
| Lua syntax | `174 files`, exit `0` |
| Clean Run A | `209 passed / 109 subtests / 4 standalone`, mutation `0` |
| Clean Run B | `209 passed / 109 subtests / 4 standalone`, mutation `0` |
| Comparator | status `PASS`, raw bytes equal, exit `0` |
| Codex Reviewer | `PASS / APPROVED`, actionable `0`, unsupported `0` |

Run A/B canonical SHA-256은 모두 `15577164525fbfa142d3cc258c549d6a0d157ec85c14ab44faf84a64d632bdca`다. Reviewer raw review와 receipt는 `Iris/_docs/refactor/responsibility_repository_refactor/public_text_boundary_hardening_{codex_review.md,review_receipt.json}`에 둔다.

### 12.5 Non-claims

Current package machine-local source path, deleted right-click capability reference와 baseline 이후 `Iris/media` 변경은 각각 0건이다. Product Lua/UI/CheatMenu, package/public-text output schema와 intended runtime behavior를 변경하지 않았고 retired global context-menu patch를 복원하지 않았다.

이번 wave는 성능, runtime wall-clock/CPU/memory/FPS, 실제 GPT/Codex token 개선률을 측정하지 않았다. 기존 bounded correction의 owner locality와 explicit dependency가 유지보수 경계를 줄였다는 구조적 결과만 채택하며, package/source line delta를 performance나 token 절감률로 환산하지 않는다.
