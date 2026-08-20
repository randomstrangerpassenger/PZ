# Implementation Plan — Iris Stateful Artifact Registry Architecture Retirement

계획 상태: `implementation_pending`; Change 4 runtime-contract freeze와 Change 5 전에 R2 owner decision 필요

기준 문서: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`, 요청에 첨부된 `# ROADMAP — Iris Stateful Artifact Registry Architecture Retirement`

코드 조사 readpoint: `main` / commit `eaafed519afb7cd038af3d09443581957b3b478c` / tree `9696bd992ff3a0da03cafb61529e3971793ab159` (2026-08-20 조사 시점). 조사 당시 작업 트리는 사용자 변경으로 dirty였으므로 이 값은 계획 근거일 뿐, 구현 기준선 승인이나 검증 PASS를 뜻하지 않는다.

---

## 1. Objective

Iris의 Stateful Artifact Registry(IAR)가 현재 담당하는 mutable-current 수명주기와 직접 쓰기 메커니즘을 다음 흐름으로 대체할 수 있는지 먼저 증명하고, 증명된 범위만 단계적으로 은퇴한다.

`canonical source → exact input identity → deterministic/idempotent off-live complete generation → stateless validation → generation-derived descriptor → fail-closed safe replacement → runtime/package validation`

목표는 IAR라는 이름이나 파일군의 일괄 삭제가 아니다. 현재의 정확성 의무를 생산자와 소비자 단위로 식별하고, 각 의무가 더 단순한 후속자에 의해 동등하거나 더 강하게 보존됐다는 증거가 있을 때만 구현·필수 검증·패키지 경로에서 stateful lifecycle 의존성을 제거한다.

제품 IAR retirement 실행 결과(`retirement_outcome`)는 다음 셋 중 정확히 하나다.

1. `FULL_RETIREMENT`: Layer 1–5 전체 repository census에서 활성 제품 IAR lifecycle 소비자가 0이고, 역사 증거와 독립 repository-validation governance만 제품 경로 밖에 남는다.
2. `MINIMAL_RESIDUAL`: 제거할 수 없는 최소 primitive와 소비 지점, 불변식, 소유자, 금지된 확장 경계를 명시하고 나머지를 은퇴한다.
3. `RETIREMENT_NOT_ACHIEVABLE`: 결정론·완전 생성·무혼합 교체·호환성 중 하나라도 증명되지 않으면 현재 경로를 보존하고 파괴적 마이그레이션을 수행하지 않는다.

`FULL_RETIREMENT`와 `MINIMAL_RESIDUAL`만 retirement-complete 결과다. `RETIREMENT_NOT_ACHIEVABLE`은 fail-closed 실행 결과이며 retirement completion이 아니다. 이 제품 결과는 `docs/EXECUTION_CONTRACT.md`의 execution closeout state, machine validation, independent review, owner decision/seal, canonical closure eligibility를 대체하지 않는다.

---

## 2. Scope

이 계획은 다음 범위를 포함한다.

* 현재 canonical Layer 3/DVF 3.3 소스, rendered JSON, Lua runtime chunk bundle, generation descriptor, 패키지 검증 사이의 실제 입력·출력·해시·경로 의존성을 고정한다.
* successor 구현 중심은 Layer 3/DVF 3.3이지만, `FULL_RETIREMENT` 판정 범위는 Layer 1–5 전체의 활성 제품 IAR 생산자·소비자다. Layer 1/2/4/5에서 소비자가 발견되면 migrate, minimal residual, retirement-not-achievable 중 하나로 처분한다. 단, Layer 3 외 `migrate`는 DVF 3.3 successor의 자동 일반화가 아니며 실제 중복·동일 의무를 증명한 별도 generalization/owner decision을 선행해야 한다.
* IAR primitive(시도, nonce, receipt, candidate/current, predecessor/successor, adoption, owner authorization, seal, rollback, live gate)를 모든 생산자와 소비 지점별로 분해해 정확성 의무 장부를 만든다.
* 현재 생성기의 비결정론 요소와 생성 산출물의 역유입(backflow)을 제거한 off-live 완전 생성 경로를 만든다.
* descriptor를 권한 토큰이 아닌 순수한 generation identity record로 재정의한다.
* 기존 current를 부분 상태나 혼합 세대에 노출하지 않는 fail-closed 교체와 동일 세대 재적용 no-op을 증명한다.
* 소스 current writer, rendered/runtime adoption writer, RTC, package validator, repository required-validation 및 source-disposition 정책을 후속자 계약으로 옮긴다.
* 기존 IAR 구현과 테스트를 활성 제품 계약, 별도 거버넌스 계약, 역사 재현 증거로 분류한 뒤 분류 결과에 따라 보존·축소·은퇴한다.
* `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`와 IAR를 전제로 작성된 후속 계획들의 책임 문구를 additive amendment로 정렬한다.

### Explicitly Out Of Scope

* Layer 3 문장 의미, 근거, 정보 충분성, body-role 정책 자체의 변경
* Layer 4 QG의 적응형 표현 정책 및 UI 밀도 정책 구현
* Recipe와 Right-click 파이프라인의 의미·권한·출력 계약 변경
* Publish 판정, 공개 텍스트 품질 기준 또는 RTC 의미론의 완화
* Pulse 의존성 구조 변경
* Project Zomboid 런타임의 Python 도입. 런타임은 계속 100% Lua다.
* 사용자-facing 추천, 추측, 자동 행동, 메뉴 밖 상시 오버레이 추가
* 기존 sealed attempt/history의 재작성, 재서명 또는 삭제
* 외부 배포, Steam Workshop 게시, 릴리스 버전 승격
* IAR라는 문자열이나 `registry` 접두사의 기계적 일괄 제거
* 이 계획 작성 시점의 dirty 작업 트리에서 current 산출물을 재생성하거나 채택하는 행위
* 명시적 owner decision 없이 current runtime Lua module/file layout, loader path, stable manifest/pointer 계약을 변경하는 행위

---

## 3. Non-Goals

* 코드 줄 수나 파일 수 감소 자체를 성공 기준으로 삼지 않는다.
* `2,105` facts row와 `11` Lua chunk를 영구 구조 상수로 봉인하지 않는다. 이는 진입 기준선의 exact readpoint이며 후속 generation descriptor는 실제 파일 universe를 명시한다.
* stateful receipt를 stateless descriptor로 이름만 바꾸지 않는다.
* 생성 내용이 같다는 이유만으로 authority/adoption을 암묵적으로 획득하게 하지 않는다.
* RTC의 현재 stale 상태를 IAR 은퇴 과정에서 임의로 PASS로 바꾸지 않는다.
* required-test 개수의 기계적인 동일성만 보존하지 않는다. 각 실패 보호 의무가 후속 테스트에 일대일로 추적되거나 더 세분화되어야 한다.
* source authority, generated artifact identity, RTC applicability, Publish, repository-validation governance를 하나의 통합 PASS로 합치지 않는다.
* 제품 IAR retirement의 machine result를 independent review, owner seal 또는 canonical governance closure로 읽지 않는다.
* Layer 3 외 소비자가 발견됐다는 사실만으로 DVF 3.3 generation contract를 다른 information layer의 공통 Registry로 승격하지 않는다.
* 역사 도구가 현재 경로에서 호출되지 않는다는 추정만으로 삭제하지 않는다.

---

## 4. Assumptions

### 4.1 로드맵 미결정 사항의 계획상 판정

| 로드맵 결정 | 이 계획의 판정 | 코드 근거 및 제약 |
| --- | --- | --- |
| 종료 모델 | `FULL_RETIREMENT`, `MINIMAL_RESIDUAL`, `RETIREMENT_NOT_ACHIEVABLE`의 3상 모델 | 현재 descriptor와 생성기가 후속자 요건을 아직 만족하지 않으므로 은퇴 성공을 선결론으로 둘 수 없다. |
| 거버넌스 포함 여부 | 제품 생성 상태와 거버넌스 프로세스 상태를 분리 | receipt/lifecycle 패턴은 current artifact뿐 아니라 repository validation evidence에도 사용된다. 거버넌스 상태 제거는 별도 owner decision이 필요하다. |
| primitive 처분 단위 | `(primitive × consumption site → correctness obligation)` | 같은 nonce/receipt/role 명칭도 소스 cutover, runtime adoption, clean-checkout evidence에서 서로 다른 의무를 가진다. |
| 실행 순서 | Sequence B: 기준선·입력·결정론 hard gate 우선 | 현재 rendered metadata의 `generated_at`, descriptor의 transaction/staging binding, lifecycle-heavy input manifest 때문에 먼저 동일 바이트 재생성을 증명해야 한다. |
| sealed 분모와 역할 taxonomy | readpoint·의무·source policy는 보존하되 영구 구현 상수로 고정하지 않음 | heading-by-heading additive disposition, 실패 보호 매핑, `unclassified == 0`은 hard requirement다. literal test-node 수 동일성은 요구하지 않는다. |
| terminal claim과 전역 범위 | 리뷰의 Critical을 채택해 machine/product result와 governance closure를 분리하고 Layer 1–5 전역 consumer-zero를 요구 | `FULL_RETIREMENT`는 `active_product_iar_consumer_count_all_layers == 0`일 때만 가능하며 independent review와 owner seal은 별도 기존 governance axis다. |
| runtime Lua layout | 리뷰의 Critical을 채택해 owner-reserved decision으로 유지 | Change 4의 runtime contract 동결과 Change 5 구현 전에 아래 R2 선택과 증거 binding이 필요하다. 결정 전에는 현행 layout 변경이 금지된다. |

### 4.2 리뷰 Critical 판정과 owner-reserved gate

리뷰의 두 Critical을 모두 실행 전 필수 게이트로 채택한다.

* R1 — terminal schema: 이 계획에서 수정 완료. `retirement_outcome`, execution closeout state, validation ceiling, machine validation, independent review, owner decision/seal, canonical closure eligibility를 분리한다. closeout 자체가 review 또는 seal을 수여하지 않는다.
* R2 — runtime layout: `owner_decision_required`. Change 1–3은 진행할 수 있지만, Change 4의 runtime public module/loader contract를 동결하거나 Change 5를 구현하기 전에 다음 중 하나가 exact subject/commit과 결속된 additive owner decision으로 기록돼야 한다.

| R2 선택지 | 허용되는 구현 | 추가 필수 증거 |
| --- | --- | --- |
| A | generation-qualified immutable Lua module set + single atomic manifest/pointer switch | loader/public require 계약, automatic Lua load-result parity, module-cache transition harness, concurrent observation, package parity, manual in-game QA |
| B | generation-root pointer + 별도 single-switch mechanism | A와 동일하며 pointer 원자성의 Windows failure-injection proof 추가 |
| C | 현행 manifest + 11-chunk layout 유지 | current-visible sequential write의 concurrent-observation proof 또는 보호에 필요한 최소 residual. 무혼합을 증명하지 못하면 `MINIMAL_RESIDUAL` 또는 `RETIREMENT_NOT_ACHIEVABLE` |

선택 전 fail-closed 기본값은 “layout mutation 금지”이며 C가 자동 승인됐다는 뜻은 아니다. R2가 없으면 Change 4의 순수 off-live builder 실험까지만 허용하고 runtime contract freeze, protected-current install, layout 변경은 `blocked`로 남긴다.

### 4.3 코드베이스 조사에서 확인된 현재 상태

* `compose_layer3_text.py`는 current 입력으로 facts, decisions, overlay, profiles, identity rules, precedence rules의 6개 키를 사용한다.
* 기본 current 출력 경로에 대한 실쓰기에는 `REGISTRY_REAL_CURRENT_PROTECTED_WRITE_DISABLED`가 적용되어 일반 compose 진입점의 직접 current 쓰기는 이미 차단돼 있다.
* 같은 생성기는 fixture 고정값이 없으면 `datetime.now(timezone.utc).isoformat()`을 rendered metadata에 넣으므로 현재 형태 그대로는 독립 Run A/B byte identity를 만족하지 못한다.
* 현재 generation descriptor는 `transaction_id`, staging의 `candidate.path`, `authority_effect=current_runtime_adoption`을 포함한다. 따라서 content-derived descriptor가 아니며 삭제 후 동일 바이트 재계산 가능한 후속자 계약으로 볼 수 없다.
* 현재 descriptor는 facts hash와 lifecycle-heavy `dvf_3_3_input_manifest.json` hash를 묶지만, compose가 직접 읽는 6개 canonical input 각각을 모두 명시하지 않는다.
* `validated_naturalization_runtime_adoption.py`의 실제 적용 경로는 backup과 rollback을 제공하지만, live chunk directory를 제거한 후 바꾸므로 실패 주입과 관찰자 관점의 무혼합 교체를 별도로 증명해야 한다.
* `dvf_3_3_current_facts_correction*.py`와 `dvf_3_3_food_semantic_registry_cutover.py`는 nonce, one-use owner authorization, lock, receipt, rollback을 포함한 migration-specific source current writer다. 활성 소비 여부를 파일별로 판정해야 한다.
* `export_dvf_3_3_lua_bridge.py`는 기본적으로 staging/historical/diagnostic 경로만 쓰며 live/package 유사 경로를 보호한다. 순수 chunk 생성·bundle 검증 로직과 RTC lifecycle 결합부가 함께 존재한다.
* `dvf_3_3_registry_runtime_compatibility.py`에는 exact-key, case-collision, source/rendered/Lua surface, payload 비교 같은 재사용 가능한 stateless 검증과 attempt/policy/adoption lifecycle이 혼재한다.
* `package_iris.ps1`는 `current_runtime_payload`와 `rtc_certified_payload`를 구분하지만, 현재 descriptor의 transaction/candidate 필드와 RTC lifecycle bundle에 직접 의존한다.
* `current_route_required_validations.json`은 조사 시점에 필수 테스트 148개와 필수 artifact 155개를 선언한다. 이 분모는 구현 시작 시 clean commit에서 다시 census한다.
* 현재 RTC source alignment는 `stale_requires_successor_rtc`, `live_bridge_runtime_package_publication_allowed=false`, `successor_rtc_closure_complete=false`다. IAR 은퇴는 이 상태를 숨기거나 승격하지 않는다.
* `iris_current_authority_manifest.json`과 clean-checkout source-disposition policy는 IAR 역할 taxonomy를 실제로 소비한다. 후속 책임 분류 없이 제거할 수 없다.

### 4.4 실행 전제

* 구현은 사용자의 현재 변경을 보존한 뒤 선택된 정확한 commit에서 만든 별도 clean worktree에서 시작한다.
* 실행 preflight에서 `docs/EXECUTION_CONTRACT.md`를 다시 읽고 raw-byte SHA-256을 기록한다. 계획 수정 readpoint는 v1.3 / `a185bbd78eb849b0310d9aadc9102cb156b892513266fac0ec7903eb3d3a9493`이며, 실행 시 hash가 다르면 최신 원문을 재대조하기 전 진행하지 않는다.
* preflight evidence는 최소 `execution_contract_checked=true`, `execution_contract_path`, `execution_contract_sha256`, `known_conflict_count`, `conflict_disposition`을 기록한다. `known_conflict_count != 0`이면 영향 단계는 owner 또는 상위 authority 판정 전 `blocked`다.
* 진입 readpoint는 commit, tree, Git blob/working hash, source row count, rendered entry count, runtime file universe, descriptor, required validation manifest를 함께 묶는다.
* source의 의미 변경은 Git-authored change로만 일어나며 generated-artifact install이 source authority를 역으로 변경하지 않는다.
* descriptor는 권한 또는 owner approval을 부여하지 않고, exact input/output identity와 generator contract만 기술한다.
* RTC applicability와 current-runtime package validity는 서로 다른 축이다. RTC-certified 패키지는 current generation에 맞는 RTC 증거가 없으면 계속 fail-closed한다.
* `.gitattributes`의 `-text` 대상과 JSON/JSONL/Lua의 EOL·UTF-8 BOM 정책을 input/output contract에 명시한다. decoded-text hash와 raw-byte hash는 이름과 용도를 혼용하지 않는다.
* sealed denominator와 operational census가 다르면 sealed 값을 갱신하지 않는다. operational 값은 실행 기준선으로 사용할 수 있지만 divergence는 owner-visible governance finding으로 별도 기록하고 sealed authority가 요구하는 절차 없이 봉인값을 대체하지 않는다.
* 새 파일명은 아래 계획을 기본값으로 사용하되, Change 1의 소비자 census에서 기존 public import/entrypoint와 충돌이 드러나면 같은 책임 경계를 유지하는 범위에서만 조정한다.

---

## 5. Repository Areas Affected

### Code

현재 생산·채택·소비 경로:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_io.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/validated_naturalization_runtime_adoption.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_facts_correction.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_facts_correction_0002_cutover.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_facts_correction_0003_cutover.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_food_semantic_registry_cutover.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
* `Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py`
* `Iris/tools/package_iris.ps1`

의도한 후속자 모듈(신규):

* `Iris/build/description/v2/tools/build/dvf_3_3_generation_contract.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_complete_generation.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_complete_generation.py`
* `Iris/build/description/v2/tools/build/install_dvf_3_3_complete_generation.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_runtime_compatibility.py`

테스트 및 repository validation:

* `Iris/build/description/v2/tests/test_compose_layer3_text_overlay.py`
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py` 및 관련 current-write 계약 테스트
* `Iris/build/description/v2/tests/test_validated_naturalization_runtime_adoption.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_*.py` RTC 테스트군
* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_current_authority_cutover.py`
* 신규 `Iris/build/description/v2/tests/test_dvf_3_3_complete_generation.py`
* 신규 `Iris/build/description/v2/tests/test_dvf_3_3_generation_install.py`
* 신규 `Iris/build/description/v2/tests/test_dvf_3_3_runtime_compatibility.py`
* `Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/lua_merge_harness.lua`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_lua_load_harness.py`
* `Iris/test/lua/lazy_lookup_acceptance_harness.lua`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/validation/clean_checkout/tests/`
* `Iris/validation/residual_refactor/`

### Docs

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`는 수정 대상이 아니라 실행 preflight 및 closeout 준수 기준이다.
* `docs/Philosophy.md`는 수정 대상이 아니라 준수 기준이다.
* `docs/새 폴더/iris_item_page_information_sufficiency_plan.md`
* `docs/새 폴더/iris_layer3_body_role_realignment_menu_tooltip_core_description_readiness_plan.md`
* `docs/새 폴더/iris_layer4_adaptive_interaction_density_presentation_plan.md`
* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* 신규 `Iris/_docs/round3/iar_stateful_architecture_retirement/` 증거 묶음

### Config

* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/clean_checkout/contracts/canonical_gate.json`
* `Iris/validation/clean_checkout/authority/`의 source-disposition 자료
* `.gitattributes`
* `.gitignore`

Config 변경은 실제 경로·분류·EOL 계약의 변경이 확인될 때만 수행한다. 계획 편의를 위한 광범위한 ignore 또는 taxonomy 완화는 금지한다.

### Generated Artifacts

보호되는 current/readpoint:

* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* `Iris/build/description/v2/data/compose_profiles_v2.json`
* `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
* `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`
* `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`

신규 증거/산출물:

* 외부 output root의 Run A/Run B complete generation과 비교 보고서
* 외부 output root의 failure-injection 및 idempotence 보고서
* `Iris/_docs/round3/iar_stateful_architecture_retirement/baseline_readpoint.json`
* `Iris/_docs/round3/iar_stateful_architecture_retirement/input_backflow_inventory.json`
* `Iris/_docs/round3/iar_stateful_architecture_retirement/obligation_disposition.jsonl`
* `Iris/_docs/round3/iar_stateful_architecture_retirement/protection_mapping.json`
* `Iris/_docs/round3/iar_stateful_architecture_retirement/residual_report.json`
* `Iris/_docs/round3/iar_stateful_architecture_retirement/closeout.json`
* owner-managed 또는 approved governance 위치의 R2 runtime-layout decision evidence

---

## 6. Planned Changes

### Change 1 — 진입 기준선과 활성 소비자 census 고정

Purpose:

IAR 은퇴 전의 정확한 보호 대상과 호출 그래프를 고정하고, dirty working tree나 역사 파일의 존재를 활성 의존성으로 잘못 해석하지 않게 한다.

Files:

* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* 신규 baseline/input/consumer inventory evidence

Implementation Notes:

* 사용자가 선택한 clean commit과 tree에서 별도 worktree를 만들고 모든 기준선 해시를 raw byte 기준으로 계산한다.
* 첫 실행 전에 `EXECUTION_CONTRACT.md` preflight를 수행하고 exact path/hash, 확인 시각(실행 receipt에만), conflict 수와 disposition을 baseline evidence에 결속한다.
* current facts row count, rendered entry identity, runtime manifest와 ordered file universe, descriptor, package input, RTC marker를 하나의 readpoint로 묶는다.
* 조사 시점의 `2,105` facts와 `11` chunks, 필수 테스트 148개, 필수 artifact 155개가 선택된 실행 commit에서도 동일한지 재확인한다. operational census가 다르면 실행 commit의 값으로 operational 기준선을 만들되, sealed denominator 차이는 자동 갱신하지 않고 owner-visible governance finding으로 분리한다.
* Python AST/import, PowerShell invocation, Git tracked path, required-validation, package script, docs entrypoint를 함께 조사한다. 단순 문자열 검색 결과는 호출 증거와 구분한다.
* Layer 1–5 각각에서 각 IAR 관련 파일과 symbol을 `active_product`, `active_governance`, `active_validation`, `historical_reproduction`, `sealed_evidence`, `candidate_only`, `unclassified` 중 하나로 분류하고 layer별·전체 active product consumer count를 낸다.
* Layer 3 외 active product consumer의 후보 disposition이 `migrate`이면 obligation ledger에 `owner_decision_required=true`와 별도 generalization decision의 subject/evidence placeholder를 기록한다. 해당 decision이 없으면 `migrate`를 확정하지 않고 `retain_minimal_residual` 또는 `blocked`/negative outcome으로 판정한다.
* `dvf_3_3_input_manifest.json`은 최소 `generation_content_input`, `source_history_or_adoption_record`, `package_consumer`, `required_validation_consumer`, `historical_trace` 역할을 소비 지점별로 검사한다. 전체 파일에 하나의 총괄 역할을 부여하지 말고 각 역할을 `active`, `superseded`, `historical`, `blocked`로 처분한다.
* glob 단위 삭제 판정을 금지하고 파일·symbol·소비 지점별 판정을 사용한다.
* 기준선 단계는 current source/rendered/runtime/descriptor에 쓰지 않는다.

Validation:

* census의 tracked file universe가 `git ls-files`와 일치한다.
* current writer 목록의 모든 write/replace/unlink/rmtree 경로가 분류되고 `unclassified == 0`이다.
* `active_product_iar_consumer_count_by_layer`가 Layer 1–5를 모두 포함하고 전체 합계가 재계산 가능하다. 이 단계에서는 0을 요구하지 않으며 발견된 각 소비자에 처분 owner를 배정한다.
* Layer 3 외 `migrate` 후보마다 `owner_decision_required=true`이며, 별도 generalization decision이 없는 후보의 확정 migration count는 0이다.
* required validation과 package가 참조하는 모든 IAR 필드가 소비자 장부에 존재한다.
* `dvf_3_3_input_manifest.json`의 역할별 disposition에 미분류가 없고, current descriptor/package가 실제로 소비하는 hash와 의미가 기록돼 있다.
* sealed/operational denominator divergence가 각각 `owner_visible_finding`과 `operational_baseline`으로 분리돼 있다.
* clean commit/tree와 working-tree 상태를 별도 필드로 기록해 dirty 변경을 기준선에 혼입하지 않는다.

---

### Change 2 — canonical input, backflow, 결정론 hard gate

Purpose:

IAR 상태 없이도 동일 입력에서 동일한 완전 generation을 만들 수 있는지, live 경로를 건드리기 전에 증명한다.

Files:

* `compose_layer3_text.py`
* `compose_layer3_io.py`
* `export_dvf_3_3_lua_bridge.py`
* 신규 `dvf_3_3_generation_contract.py`
* 신규 `build_dvf_3_3_complete_generation.py`
* 신규 input/backflow 및 determinism evidence

Implementation Notes:

* 최초 canonical input 가설은 아래 6개 파일이다. Change 1에서 숨은 입력이 발견되면 generator/schema/policy 파일까지 명시적으로 확장한다.
  * `dvf_3_3_facts.jsonl`
  * `dvf_3_3_decisions.jsonl`
  * `dvf_3_3_overlay_support.jsonl`
  * `compose_profiles_v2.json`
  * `compose_profile_identity_hint_rules.json`
  * `compose_profile_conflict_precedence_rules.json`
* 현재 `dvf_3_3_input_manifest.json`은 source history와 adoption state를 포함하므로 그 전체 hash를 생성 내용의 유일 입력 신원으로 사용하지 않는다. descriptor가 실제 canonical files를 직접 열거하고 raw-byte hash를 바인딩한다. 기존 manifest는 Change 1/3 장부 결과에 따라 source-history/adoption evidence 또는 active non-generation consumer로 명시 보존하며, 모호한 “current input” 역할을 남기지 않는다.
* 생성기 구현·schema·serializer·chunking contract의 버전 또는 Git blob/hash를 입력 신원에 포함한다. 로컬 절대경로, 임시 디렉터리, 실행 순번은 제외한다.
* `generated_at`, locale-dependent datetime, filesystem enumeration 순서, process 환경, current output readback, staging candidate, receipt/nonce 같은 비입력 상태가 output bytes에 들어가지 않게 한다.
* 시간 정보가 감사에 필요하면 generation 밖의 실행 receipt에만 기록하며 content identity와 package identity에서 제외한다.
* 생성 산출물이 다음 생성의 입력으로 역유입되는 모든 경로를 탐지하고 차단한다. current rendered/runtime/descriptor를 읽지 않아도 canonical input만으로 완전 generation이 나와야 한다.
* output root는 repo와 protected roots 바깥을 기본값으로 하고, 실행 전에 external-only를 검증한다.
* 서로 다른 clean checkout path와 서로 다른 external output path에서 Run A/Run B를 수행한다. path-control run은 같은 입력을 더 긴/Unicode 경로에서 생성한다.
* Run A 산출물을 지우고 같은 위치에 재생성한 결과도 동일해야 한다.

Validation:

* Hard Gate D1: Run A/Run B/path-control의 파일 universe, 각 raw-byte SHA-256, descriptor bytes가 모두 동일하다.
* Hard Gate D2: 같은 generation을 두 번 실행했을 때 두 번째 실행이 byte-identical하고 protected current mutation count가 0이다.
* Hard Gate D3: canonical input 하나를 1 byte 변경하면 generation identity가 바뀌며, 입력 변경 없이 env/time/path만 바꿔도 identity는 바뀌지 않는다.
* Hard Gate D4: output/backflow inventory의 `unresolved == 0`이다.
* D1–D4 중 하나라도 실패하면 current migration과 IAR 삭제를 시작하지 않고 `RETIREMENT_NOT_ACHIEVABLE` 또는 원인 수정 후 재실행으로 종결한다.

---

### Change 3 — IAR primitive별 정확성 의무와 처분 장부 작성

Purpose:

stateful 메커니즘을 삭제하기 전에 무엇을 보호했는지 보존하고, 제품 상태와 별도 거버넌스 상태를 분리한다.

Files:

* 모든 current writer/adoption/RTC/package/required-validation 소비자
* `Iris/validation/residual_refactor/`
* 신규 `obligation_disposition.jsonl`
* 신규 `protection_mapping.json`

Implementation Notes:

* 장부의 최소 필드는 `information_layer`, `primitive`, `producer_path`, `producer_symbol`, `consumer_path`, `consumer_symbol`, `classification`, `axis`, `correctness_obligation`, `failure_prevented_or_detected`, `successor_mechanism`, `validation_evidence`, `disposition`, `owner_decision_required`다.
* attempt, nonce, receipt, candidate, current, predecessor, successor, adoption, bundle, live gate, rollback, owner authorization, seal, role taxonomy 각각을 모든 소비 지점과 교차한다.
* 처분 값은 `replace_stateless`, `retain_governance`, `retain_minimal_residual`, `historical_read_only`, `remove_after_gate`, `not_applicable`, `blocked`로 제한한다.
* product generation의 attempt/nonce/receipt는 content identity, complete off-live generation, validation, safe replacement로 대체하는 것을 기본으로 한다.
* repository validation evidence의 attempt/receipt가 실행 실패 세탁 방지, 외부 output isolation, exact commit binding을 담당하면 제품 IAR 은퇴와 별개로 `retain_governance` 판정한다.
* source authority adoption을 Git review/commit policy로 옮기는 경우 owner decision과 해당 정책의 검증 지점을 명시한다. 이 계획이 거버넌스 권한을 스스로 폐지하지 않는다.
* `dvf_3_3_input_manifest.json`의 lifecycle-heavy 필드별 생산자·소비자·정확성 의무와 후속자 또는 historical disposition을 별도 rows로 기록한다. 파일 hash 소비와 필드 의미 소비를 구분한다.
* Layer 3 외 row에 `replace_stateless`/migration을 선택하려면 `owner_decision_required=true`를 설정하고, DVF 3.3 contract와의 실제 중복·동일 correctness obligation·비일반화 대안을 다룬 별도 decision evidence를 결속한다. 이 증거가 없으면 해당 row는 migration-complete가 아니다.
* history/sealed attempt는 active dependency에서 제거될 수 있어도 증거 자체는 수정하거나 삭제하지 않는다.
* 각 기존 테스트는 보호 의무에 연결한다. 후속 테스트가 동일 실패를 탐지하면 대체 가능하되, 근거 없는 테스트 삭제는 금지한다.

Validation:

* 모든 primitive와 모든 소비 지점이 정확히 하나 이상의 disposition을 갖고 `unclassified == 0`, `unmapped_failure_protection == 0`이다.
* Layer 1–5가 모두 장부 범위에 포함되고 `unclassified_layer_count == 0`이다.
* `remove_after_gate` 항목은 successor evidence와 마지막 활성 소비자 제거가 모두 완료되기 전 삭제할 수 없다.
* `retain_minimal_residual`에는 최소성 반증 시도와 더 단순한 대안이 실패한 증거가 포함된다.
* product/governance/repository-validation 축을 서로 대체 증거로 사용하지 않는다.

---

### Change 4 — stateless complete-generation contract와 descriptor 도입

Purpose:

canonical input에서 rendered와 전체 Lua runtime bundle을 off-live로 완성하고 자체 검증하는 단일 제품 경로를 만든다.

Files:

* 신규 `dvf_3_3_generation_contract.py`
* 신규 `build_dvf_3_3_complete_generation.py`
* 신규 `validate_dvf_3_3_complete_generation.py`
* `compose_layer3_text.py`
* `export_dvf_3_3_lua_bridge.py`
* 신규 complete-generation 테스트

Implementation Notes:

* R2 owner decision이 없으면 기존 runtime module/file layout을 변경하지 않는 off-live prototype까지만 수행한다. runtime public module/loader contract freeze와 Change 5 진입은 R2 evidence가 exact implementation subject에 결속될 때까지 차단한다.
* complete generation의 파일 universe는 rendered JSON, runtime manifest, manifest가 열거하는 모든 Lua module, content-derived descriptor다. style log와 requeue 자료가 제품 산출물인지 진단 산출물인지 장부에서 분리한다.
* descriptor schema는 최소한 다음을 포함한다.
  * schema/version
  * ordered canonical input path와 raw-byte hash
  * generator/serializer/chunking contract identity
  * ordered output path, media type, raw-byte hash, size
  * output universe hash
  * content-derived `generation_id`
  * runtime public module/loader contract version
* descriptor에서 `attempt_id`, `transaction_id`, nonce, receipt path, owner seal, absolute path, staging candidate path, wall-clock timestamp를 제거한다.
* repository의 protected-current descriptor가 아니라 external/off-live successor generation descriptor를 삭제한 뒤 canonical input과 generator만으로 동일 bytes를 재계산할 수 있어야 한다.
* validator는 descriptor를 신뢰의 시작점으로 삼지 않고 canonical input과 실제 output을 다시 계산/비교한다.
* exact FullType key, case-sensitive identity, ASCII-lower collision group, duplicate, missing/extra entry, payload projection, chunk order, missing/extra file, stale/mixed generation을 fail-closed 검증한다.
* 이 stateless product validator의 claim token은 기존 `Registry Runtime Compatibility`와 구분되는 `generation_key_identity_validation`으로 고정한다. 이 token은 RTC PASS, adoption, Publish 또는 owner seal을 뜻하지 않는다.
* 기존 `lua_merge_harness.lua`와 `validate_dvf_3_3_vnext_lua_load_harness.py`의 검증 의무를 후속 load harness로 보존·확장한다. standalone Lua가 predecessor와 off-live successor bundle을 실제 `require`로 재구성하고, Python driver가 정렬된 exact key/payload projection과 canonical digest를 비교한다.
* 기존 reusable compose/export/RTC pure logic을 가능한 범위에서 추출하고, sealed historical entrypoint의 재현 import는 작은 adapter로 유지한다.
* external/off-live generation root에서 동일 generation을 rebuild하는 경우에만 no-op 또는 byte-identical rewrite를 허용하며 새 authority state를 만들지 않는다. 이 규칙은 protected current install idempotence를 정의하지 않는다.

Validation:

* descriptor field mutation, input hash mutation, output hash mutation, extra/missing file, chunk reorder, case-only collision, mixed-generation fixture가 각각 고유한 오류 코드로 실패한다.
* 현재 readpoint 입력으로 후속자가 만드는 semantic identity, full exact-key universe, payload projection, runtime Lua load 결과가 current predecessor와 parity를 이룬다. 대표 key 수동 확인만으로 이 자동 full-universe 검증을 대체하지 않는다.
* external/off-live successor descriptor를 삭제·재생성했을 때 bytes와 `generation_id`가 동일하며 protected-current descriptor mutation count는 0이다.
* 런타임 대상 디렉터리에 Python 또는 build-time dependency가 들어가지 않는다.

---

### Change 5 — fail-closed safe replacement와 direct-writer 은퇴

Purpose:

검증된 complete generation만 current 위치에 설치하고, 실패 중에도 predecessor 또는 successor 중 하나의 완전한 세대만 관찰되게 한다.

Files:

* 신규 `install_dvf_3_3_complete_generation.py`
* `validated_naturalization_runtime_adoption.py`
* source correction/cutover writers
* `manage_dvf_3_3_runtime_chunk_cutover.py`
* current source/rendered/runtime/descriptor paths
* 신규 install/failure-injection 테스트

Implementation Notes:

* R2 owner decision의 exact path/hash와 선택지 A/B/C가 installer implementation subject에 결속되지 않으면 Change 5는 시작하지 않는다. A/B는 runtime layout authority 변경으로 disclose하고, C는 현행 layout 유지와 residual 판정을 전제로 한다.
* install은 build와 분리한다. build/validate가 모두 PASS하기 전 protected current 쓰기를 시작하지 않는다.
* installer는 expected predecessor generation과 candidate generation을 explicit argument로 받고, 현재가 둘 중 어느 것도 아니면 stale/mixed로 중단한다.
* 같은 `generation_id`의 재적용은 current bytes를 바꾸지 않는 no-op이다.
* already-current install은 build의 byte-identical rewrite 허용과 구분한다. installer는 protected current에 write/replace/delete를 호출하지 않고 `protected_current_mutation_count == 0`인 deterministic no-op으로 끝나야 한다.
* 여러 고정 chunk 파일을 순차 overwrite한 뒤 manifest만 마지막에 쓰는 방식은 reader가 혼합 세대를 볼 수 있으므로 그 자체로 안전하다고 간주하지 않는다.
* R2-A를 선택하면 generation-qualified immutable module/file set을 먼저 설치·검증하고 stable manifest/pointer를 마지막 단일 visibility switch로 바꾼다. R2-B를 선택하면 generation-root pointer를 사용하되 같은 single-switch 불변식을 증명한다. 두 경우 모두 기존 Lua loader/public require 계약 변경을 owner decision과 validation ceiling에 명시한다.
* Windows에서 non-empty directory replace가 원자적이라는 가정은 금지한다. 선택한 파일시스템 primitive는 실제 Windows failure-injection으로 검증한다.
* R2-A/B가 Lua module cache, package search path, zip layout 또는 public loader 계약과 양립하지 않으면 임의로 다른 layout으로 전환하지 않고 R2 재결정을 요청하거나 C의 최소 residual/negative outcome으로 닫는다. 검증 없이 기존 디렉터리를 먼저 삭제하지 않는다.
* R2-C에서는 현행 manifest + 11-chunk layout의 current-visible write를 실제 concurrent reader probe로 검증한다. 순차 교체 중 무혼합을 증명하지 못하면 stateful 보호를 최소 residual로 유지하거나 `RETIREMENT_NOT_ACHIEVABLE`로 닫는다.
* predecessor는 새 generation의 machine validation, repository gate, 선택된 R2 validation, 그리고 governing authority가 요구하는 independent review/owner seal이 모두 exact successor subject에 결속될 때까지 rollback 가능한 형태로 유지한다. predecessor cleanup은 Change 5 install transaction의 일부가 아니라 별도 post-closeout action이며, 삭제 전에 reader liveness와 rollback 필요성을 재검증한다. sealed history는 cleanup 대상이 아니다.
* canonical source 변경은 normal Git-authored diff로 수행한다. migration-specific source current writer는 활성 호출이 0이고 대체 policy가 검증된 뒤 `historical_read_only` 또는 `remove_after_gate`로 전환한다.
* 실 current write를 이미 금지하는 compose guard는 후속 installer 외 직접 writer가 0임이 증명될 때까지 유지하고, 최종에는 더 일반적인 protected-output policy로 이름과 책임을 정리한다.

Validation:

* write/copy/rename/pointer switch 각 경계에 실패를 주입한다. cleanup은 별도 post-closeout 단계로 시험하고 install 성공과 같은 transaction으로 묶지 않는다.
* 모든 실패 시 current reader가 predecessor 완전 세대 또는 successor 완전 세대만 관찰하고 partial/mixed count가 0이다.
* R2-A/B가 실제 single atomic visibility switch를 제공한다면 OS/file-system contract, 사용 primitive, 선형화 지점과 failure boundary를 기록하고 `switch_atomicity=proven`으로 분류한다.
* current-visible file을 둘 이상 순차 변경하거나 single-switch를 형식적으로 증명할 수 없으면 성공 경로와 모든 failure-injection 경로에서 concurrent readers를 반복 실행해 `mixed_generation_observation_count == 0`을 요구하되 결과 등급은 `switch_atomicity=observed_only`로 제한한다. 비관측은 mixing 불가능성 증명이 아니며 atomicity PASS로 승격하지 않는다.
* `observed_only`만 남으면 잔여 mixed-generation risk를 validation ceiling과 explicit non-claims에 기록한다. 별도 correctness mechanism이 불가능성을 증명하지 않는 한 `FULL_RETIREMENT`의 safe-replacement hard gate를 충족하지 못하며 `MINIMAL_RESIDUAL` 또는 `RETIREMENT_NOT_ACHIEVABLE`로 처분한다.
* R2-A/B를 선택하면 automatic Lua load-result parity, `lazy_lookup_acceptance_harness.lua`를 확장한 predecessor→successor module-cache transition test, package parity, manual in-game startup/Browser/Wiki/Tooltip QA를 필수 closeout evidence로 올린다.
* 실패 후 재실행이 수동 receipt 복구 없이 수렴하며 동일 generation 재적용은 no-op이다.
* already-current 재적용 전후 protected file universe의 raw-byte hash와 mutation/write syscall 또는 instrumented writer count가 동일하고 `protected_current_mutation_count == 0`이다.
* expected predecessor 불일치, concurrent install, stale lock/temp, extra current file, descriptor mismatch를 fail-closed한다.
* installer 외 protected current direct writer 수가 0이다. 최소 residual이면 허용 writer와 목적을 exact allowlist로 봉인한다.

---

### Change 6 — RTC와 패키지 검증의 제품 계약 분리

Purpose:

정확한 runtime/package 검증은 보존하면서 IAR lifecycle/adoption 상태를 제품 generation identity에서 제거한다.

Files:

* `dvf_3_3_registry_runtime_compatibility.py`
* `validate_dvf_3_3_registry_runtime_compatibility.py`
* 신규 `dvf_3_3_runtime_compatibility.py`
* `export_dvf_3_3_lua_bridge.py`
* `package_iris.ps1`
* `current_route_required_validations.json`
* RTC/package 테스트

Implementation Notes:

* source/rendered/Lua surface load, exact-key 비교, duplicate/collision, payload parity 같은 pure compatibility logic을 stateless product validator로 추출하고 결과 claim을 `generation_key_identity_validation`으로 보고한다.
* attempt census, policy candidate, canonical durable, owner bind/seal 같은 lifecycle은 소비자 장부에 따라 별도 governance/history adapter에 남기거나 은퇴한다.
* `current_runtime_payload` 패키지는 generation descriptor, ordered file universe, source/rendered/runtime hash, package 내부 parity만으로 검증한다.
* `rtc_certified_payload`는 위 검증에 더해 동일 `generation_id` 또는 exact source/output identity에 적용되는 RTC evidence를 요구한다.
* current generation이 유효하다는 사실이 RTC PASS를 암시하지 않고, RTC stale이라는 사실이 current runtime bytes의 identity를 왜곡하지 않는다.
* `generation_key_identity_validation=PASS`도 `Registry Runtime Compatibility PASS`를 암시하지 않는다. RTC 명칭과 결과 token은 기존 RTC lifecycle validator에만 남긴다.
* 현재 `stale_requires_successor_rtc`는 successor RTC가 실제로 완료되기 전까지 그대로 유지한다. 이 계획의 IAR closeout은 해당 값을 자동 변경하지 않는다.
* 패키지 안에 staging candidate, transaction id, receipt, attempt work root가 필요하지 않게 한다.
* zip과 directory package 모두 exact file universe, no stale/extra chunk, raw-byte parity를 검증한다.

Validation:

* current-runtime package는 correct generation에서 PASS하고 stale/mixed/extra/missing/tampered generation에서 실패한다.
* rtc-certified package는 현재 RTC 상태에서 계속 fail-closed한다. successor RTC 증거를 별도 생성·채택한 경우에만 해당 exact generation에 한해 PASS한다.
* package directory와 zip을 추출해 runtime manifest/chunk/support file identity를 current generation과 비교한다.
* registry lifecycle 필드를 descriptor에서 제거해도 exact-key, collision, payload, package failure coverage가 보호 매핑에서 손실되지 않는다.
* report/closeout가 `generation_key_identity_validation`과 RTC evidence를 별도 path/hash/subject로 기록하며 한 축의 PASS를 다른 축에 복제하지 않는다.

---

### Change 7 — required validation, source policy, history, residual 정리

Purpose:

후속자 계약을 공식 검증 분모에 넣고, 제거된 IAR 구현에 대한 활성 테스트 의존을 없애면서 역사 재현과 실패 보호를 보존한다.

Files:

* `current_route_required_validations.json`
* `round3_test_taxonomy.json`
* clean-checkout gate contracts와 source-disposition authority
* `iris_current_authority_manifest.json`
* IAR 관련 current/historical tests
* `Iris/validation/residual_refactor/`
* 신규 protection/residual reports

Implementation Notes:

* 기존 required test/artifact 각 항목을 `preserved`, `replaced_by`, `historical_optional`, `dedicated_governance_route`, `removed_with_obligation` 중 하나로 판정한다.
* literal test count를 맞추기 위해 중복 테스트를 만들지 않는다. 대신 기존 failure-protection ID가 successor node id와 정확히 연결돼야 한다.
* IAR 역할명을 소비하는 authority manifest를 source authority, generation contract, runtime compatibility, package projection, repository governance의 후속 책임명으로 재분류한다.
* source-disposition policy는 새 테스트와 더 이상 current가 아닌 IAR 재현 테스트를 명시적으로 분류한다. heuristic만으로 historical 처리하지 않는다.
* clean-checkout full repository gate의 required source와 dependency closure를 갱신하고 clean exact commit에서만 재봉인한다.
* sealed historical artifacts와 그 hash는 수정하지 않는다. 필요한 경우 현재 docs/manifest에 successor pointer를 additive하게 추가한다.
* IAR 삭제 전 residual scan을 수행한다. 문자열 잔존이 아니라 활성 import, runtime/package dependency, current write capability, required-validation consumption을 판정한다.
* residual scan은 DVF 3.3/Layer 3에 한정하지 않고 Layer 1–5의 생산자·소비자·role taxonomy·package/validation 결속을 모두 검사한다.
* `dvf_3_3_input_manifest.json`은 장부에서 정한 역할별 disposition을 required validation과 package source classification에 반영하고, active 역할이 남으면 파일 전체를 historical로 표시하지 않는다.
* 최소 residual이 남으면 파일·symbol·consumer·invariant·owner·금지 확장·retirement 재평가 조건을 `residual_report.json`에 명시한다.

Validation:

* official current contract route, configured full repository gate, source-policy impact 검사, clean-checkout determinism을 모두 실행한다.
* required manifest의 모든 successor test/artifact가 clean checkout에서 생성 또는 검증 가능하다.
* `unclassified_source == 0`, `unmapped_required_validation == 0`, `active_removed_symbol_consumer == 0`이다.
* `FULL_RETIREMENT` 후보에서는 `active_product_iar_consumer_count_all_layers == 0`이며 Layer 1–5 개별 count와 합계가 일치한다. 하나라도 남으면 full token을 금지한다.
* historical route가 predecessor evidence를 읽을 수 있고 current route가 historical attempt work root에 의존하지 않는다.

---

### Change 8 — 설계 문서와 후속 계획의 additive closeout

Purpose:

구현 결과의 실제 책임 경계와 문서의 권한 설명을 일치시키고, IAR adoption을 전제한 후속 계획이 폐기된 책임을 다시 도입하지 않게 한다.

Files:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `ENTRYPOINTS.md`
* `INVENTORY.md`
* `docs/새 폴더/`의 IAR 의존 후속 계획 3개
* 신규 closeout evidence

Implementation Notes:

* `DECISIONS.md`의 IAR 관련 sealed heading을 heading-by-heading으로 `preserved obligation`, `superseded mechanism`, `retained governance`, `historical only`, `minimal residual` 중 하나에 매핑하는 additive decision을 추가한다.
* 기존 결정을 소급 수정하거나 역사 용어를 지우지 않는다.
* `ARCHITECTURE.md`는 canonical source, deterministic generation, stateless validation, safe replacement, RTC, package, Publish, repository governance의 분리된 owner를 기록한다.
* `ROADMAP.md`는 실제 종료 판정과 미완료 축을 기록한다. `RETIREMENT_NOT_ACHIEVABLE`이면 은퇴 완료로 표시하지 않는다.
* Layer 3/Layer 4/item-page 후속 계획의 “IAR adoption/current role”을 successor generation/validation 책임 또는 별도 owner decision으로 바꾼다. 각 계획의 의미·UI scope는 바꾸지 않는다.
* `ENTRYPOINTS.md`와 `INVENTORY.md`에는 공식 build/validate/install/package 명령, protected-path policy, historical-only entrypoint를 명시한다.
* closeout에는 execution closeout state와 `retirement_outcome`을 분리하고, validation ceiling(`validated`, `out_of_scope`, `unvalidated_but_in_scope`), machine validation, independent review, owner decision/seal, canonical closure eligibility를 각 evidence path/hash/subject와 함께 별도 기록한다. 하나의 종합 PASS가 축별 실패를 덮지 못하게 한다.
* independent review와 owner seal은 이 계획의 machine execution이 생성하거나 추정하지 않는다. governing decision에서 필요하면 exact terminal subject에 결속된 외부/owner evidence를 소비하고, 없으면 canonical sealed closeout을 주장하지 않는다.
* 제품 `FULL_RETIREMENT`는 independent repository-validation governance 상태의 제거를 뜻하지 않으며 해당 governance는 별도 disposition으로 문서화한다.

Validation:

* 문서에 제거된 active entrypoint, descriptor field, IAR current owner가 남아 있지 않은지 검사한다.
* downstream plan 세 개의 adoption 책임이 실제 후속자 또는 명시적 별도 owner에 연결된다.
* sealed heading disposition 수와 조사 대상 heading 수가 일치하고 미분류가 0이다.
* Layer 1–5 retirement scope, obligation-ledger counters, machine/review/owner axes가 terminal record에 존재하고 서로 대체되지 않는다.
* 문서 closeout의 commit/tree/hash가 최종 clean-checkout 검증 대상과 동일하다.

---

## 7. Validation Plan

### Automated Validation

검증은 단계별로 실행하고, 각 명령이 exact exit code `0`일 때만 해당 항목을 PASS로 기록한다. 아래 `<external-...>` 값은 repository와 protected roots 바깥의 절대경로여야 한다.

0. execution contract 및 owner gate preflight

   * `docs/EXECUTION_CONTRACT.md`를 다시 읽고 raw-byte SHA-256, version, path와 상위 authority conflict 수를 기록한다. 계획 readpoint hash와 다르면 새 원문 기준으로 conflict audit을 다시 수행한다.
   * R2 runtime-layout decision의 선택지, exact subject, evidence path/hash를 확인한다. R2가 없으면 Change 4 runtime contract freeze와 Change 5를 실행하지 않는다.

1. 집중 단위 테스트 및 후속자 failure matrix

   * `uv run python -B -m pytest -q -p no:cacheprovider Iris/build/description/v2/tests/test_dvf_3_3_complete_generation.py Iris/build/description/v2/tests/test_dvf_3_3_generation_install.py Iris/build/description/v2/tests/test_dvf_3_3_runtime_compatibility.py`
   * 기존 compose, adoption, RTC, package 관련 테스트는 protection mapping에 열거된 node id를 explicit 실행한다.

2. 공식 current contract route

   * `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <external-current-report>`
   * preimport closure도 별도 실행한다: `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --preimport-only --out <external-preimport-report>`

3. complete generation determinism/idempotence/path-control

   * 새 builder를 서로 다른 clean checkout과 external output roots에서 Run A/Run B로 실행한다.
   * 새 validator가 두 generation의 ordered file universe와 raw bytes를 비교한다.
   * 같은 external/off-live output을 삭제 후 재생성하고 byte-identical rewrite 또는 no-op을 확인한다. 이 결과를 protected-current install idempotence 증거로 재사용하지 않는다.
   * time, locale, temp path, checkout depth, Unicode path 변화가 descriptor bytes에 영향을 주지 않는지 확인한다.
   * `lua_merge_harness.lua`의 후속 load-result mode를 predecessor와 off-live successor 각각에 실행하고 sorted exact-key/payload projection과 canonical digest가 일치하는지 비교한다. 이 검증은 Lua syntax 검사와 별개다.

4. safe replacement failure injection

   * candidate write, candidate validation, versioned runtime set install, pointer/manifest switch, descriptor install, rendered install 각 단계에서 강제 실패한다.
   * 각 실패 직후와 재시작 후 current identity, reader-visible generation, predecessor recovery, temp residue를 검사한다.
   * 선택한 R2 mechanism이 single atomic visibility switch를 증명하지 못하거나 둘 이상의 current-visible file을 순차 변경하면, 성공·실패 경로 모두에서 concurrent observation probe를 실행한다.
   * safe-replacement report는 `switch_atomicity=proven|observed_only`를 기록한다. `proven`은 OS/file-system contract와 선형화 지점이 결속된 경우에만 허용하며 probe만 통과한 결과는 항상 `observed_only`다.
   * `observed_only`이면 mixing 불가능성을 non-claim으로 남기고, 별도 correctness proof가 없으면 full-retirement 후보에서 제외한다.
   * R2-A/B이면 module-cache transition harness를 실행하고 predecessor key/payload가 successor generation에 섞이지 않는지 검사한다.
   * already-current install을 별도 실행해 protected file universe의 pre/post raw hashes와 instrumented writer/mutation count를 비교하고 `protected_current_mutation_count == 0`을 요구한다.
   * predecessor cleanup은 terminal evidence 이후 별도 probe에서 reader liveness, rollback availability, sealed-history exclusion을 확인하며 install transaction의 PASS 조건과 합치지 않는다.

5. package

   * `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <external-package-root> -Clean -Zip -PackageApplicability current_runtime_payload`
   * `rtc_certified_payload`는 successor RTC가 exact current generation에 대해 별도 PASS한 경우에만 실행한다. 현재 stale 기준선에서는 기대 실패를 오류 코드까지 검증한다.

6. Lua syntax

   * `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`

7. clean-checkout canonical/full repository gate

   * 선택한 exact commit에서 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`을 `-RepositoryRoot`, `-Commit`, `-ClaimId`, `-EnvironmentReceipt`, `-WorkRoot`, `-ResultRoot`, `-OrchestrationReceipt`와 함께 실행한다.
   * 독립 Run A/Run B receipt를 만든 뒤 `invoke_deterministic_compare.ps1`로 full-gate 결정론을 비교한다.
   * required environment receipt와 모든 work/result root는 외부 경로를 사용하고 source checkout이 clean임을 확인한다.

8. repository-level configured validators

   * 변경된 clean-checkout/source-policy/residual-refactor 테스트를 explicit 실행한다.
   * 현재 full repository contract가 선언한 standalone validations를 그대로 실행한다.
   * repository에 Java/Gradle 또는 JS/TS 변경이 생긴 경우에만 각각 `.\gradlew test`, `pnpm biome check .`를 추가한다. 이 계획의 예상 touch surface에는 둘 다 없으므로 실제 변경이 없다면 명령을 실행하지 않고 각각 `NOT_APPLICABLE`로 기록한다.

### Manual Validation

* R2-A/B로 runtime Lua module/file layout 또는 loader pointer를 바꾼 경우 Project Zomboid에서 Iris를 로드해 startup error가 없는지 확인한다. 이 항목은 선택 사항이 아니라 해당 선택지의 필수 validation이다.
* 대표 아이템에 대해 Browser/Wiki 설명과 Right-click 정보가 기존 current와 같은 source/rendered/runtime identity를 사용하는지 확인한다.
* Alt tooltip이 기존 정책대로 최대 4줄이며 추가 오버레이나 추천 문구가 생기지 않았는지 확인한다.
* case-collision 대표군 `Base.LemonGrass` / `Base.Lemongrass`가 의도한 exact-key 경계대로 처리되는지 확인한다.
* predecessor에서 successor로 교체한 뒤 같은 세션 재로드가 지원 대상이면 Lua module cache가 혼합 세대를 노출하지 않는지 확인한다. 지원 대상이 아니면 재시작 요구를 명시하고, automatic harness가 지원/비지원 경계를 fail-closed 검증해야 한다.
* package zip을 별도 위치에 풀어 실제 mod 구조, loader manifest, ordered chunks, support files가 source package report와 일치하는지 검사한다.

### Validation Limits

* 이 계획은 multiplayer 및 전용 서버 검증을 포함하지 않는다.
* 장시간 플레이, 메모리 누수, 모든 아이템에 대한 수동 UI sweep은 수행하지 않는다.
* 외부 mod 전체와의 호환성 sweep은 수행하지 않는다.
* Steam Workshop 배포와 실제 사용자 업그레이드는 수행하지 않는다.
* RTC successor의 의미 검토와 owner adoption은 이 계획이 자동 수행하지 않는다. 별도 승인과 증거가 없으면 stale 상태를 유지한다.
* R2 decision, independent review 또는 owner seal이 필요한데 증거가 없으면 해당 axis를 `unvalidated_but_in_scope` 또는 governing vocabulary의 pending/blocked 결과로 기록하고 canonical sealed closeout을 주장하지 않는다.
* `switch_atomicity=observed_only`는 bounded concurrent probe에서 mixing이 관측되지 않았다는 사실만 검증한다. mixing 불가능성이나 filesystem atomicity는 `unvalidated_but_in_scope`/explicit non-claim으로 남긴다.
* dirty working tree에서 얻은 결과를 clean-checkout PASS로 사용하지 않는다.
* 누락된 필수 도구나 exact command의 non-zero exit는 우회하지 않고 해당 축을 `BLOCKED` 또는 `FAIL`로 기록한다.

---

## 8. Risk Surface Touch

### Authority Surface

높음. current source/rendered/runtime의 채택 방법과 역할 taxonomy가 바뀐다. 다만 source authority, generation identity, RTC, Publish, package, repository governance의 owner를 분리하고 descriptor 자체에는 권한 효과를 부여하지 않는다.

### Runtime Behavior Surface

중간, R2 owner-reserved. Layer 3 의미와 공개 API는 불변이다. 내부 Lua module/file layout 또는 loader pointer도 R2 owner decision 전에는 변경하지 않는다. R2-A/B를 선택한 경우에만 승인된 exact 변경을 수행하며 automatic load/cache/concurrency 검증과 manual in-game QA를 필수로 한다. 런타임은 계속 100% Lua여야 한다.

### Compatibility Surface

높음. exact FullType key, case collision, rendered-to-Lua payload, package applicability, loader/require surface, zip layout을 모두 건드릴 가능성이 있다. byte 및 semantic parity를 함께 요구한다.

### Sealed Artifact Surface

읽기와 참조 갱신만 허용한다. 기존 sealed attempt, receipt, decision, historical artifact는 수정·재서명·삭제하지 않는다. 새 closeout은 additive successor evidence로 남긴다.

### Public-Facing Output Surface

의도된 변경 없음. Browser/Wiki, Recipe, Right-click, Alt tooltip의 문구·근거·줄 수·표시 위치는 그대로여야 한다. 차이가 발견되면 은퇴 마이그레이션의 회귀로 취급한다.

---

## 9. Risk Analysis

### Architecture Risk

* IAR를 제거하면서 같은 state machine을 새 descriptor/installer에 숨겨 재도입할 수 있다. descriptor 허용 필드와 installer의 허용 상태를 작은 schema로 제한한다.
* 제품 상태와 repository governance를 함께 삭제하면 실패 세탁 방지나 exact-commit binding이 사라질 수 있다. obligation ledger의 axis 분리를 hard gate로 둔다.
* canonical input을 잘못 축소하면 hidden input과 backflow가 결정론 증거를 무효화한다. path/env/time/output-read 변화가 identity에 영향을 주지 않는지 독립 checkout에서 검증한다.
* generic registry 후속자를 만들어 새 generated artifact마다 다시 stateful lifecycle을 요구할 위험이 있다. 후속자는 DVF 3.3의 순수 generation contract로 시작하며 공통화는 실제 중복과 동일 의무가 증명된 뒤 별도 결정으로 한다.
* Layer 3 외 consumer에 `migrate`를 지정하면서 별도 generalization decision을 생략하면 DVF 3.3 전용 contract가 사실상 5-layer Registry로 확장될 수 있다. census row의 `owner_decision_required`와 decision evidence가 없으면 migration을 확정하지 않는다.

### Runtime Risk

* 여러 chunk를 순차 교체하면 중간 관찰자가 mixed generation을 읽을 수 있다. generation-qualified immutable set과 단일 switch 또는 증명된 최소 residual이 필요하다.
* concurrent probe의 무관측을 atomicity proof로 오독할 수 있다. `switch_atomicity=observed_only`를 별도 등급으로 유지하고 잔여 risk/non-claim을 terminal record에 남긴다.
* R2 owner decision 없이 layout을 구현 세부로 취급하면 sealed runtime surface를 우회할 수 있다. R2 evidence 없이는 runtime contract freeze와 install을 차단한다.
* Lua `require` cache가 generation 전환을 가릴 수 있다. live reload 지원 범위를 명시하고 cache behavior를 수동·자동 fixture로 검사한다.
* current rendered와 runtime Lua가 서로 다른 generation이 될 수 있다. descriptor/output-universe validation과 install failure injection으로 탐지한다.
* cleanup이 실행 중인 predecessor 파일을 지울 수 있다. rollback 보존 기간과 reader liveness 정책 없이 자동 정리하지 않는다.

### Compatibility Risk

* descriptor schema 변경이 `package_iris.ps1`, required validation, downstream tooling을 동시에 깨뜨릴 수 있다. dual-read transition은 bounded 기간만 허용하고 final residual scan에서 구 schema의 active consumer가 0인지 확인한다.
* case-insensitive Windows path와 case-sensitive FullType key를 혼동할 수 있다. filesystem path 비교와 domain identity 비교를 별도 함수/오류 코드로 유지한다.
* `.gitattributes` EOL 변환 때문에 clean checkout raw hash가 현재 decoded-text hash와 다를 수 있다. hash 종류를 schema field명에 명시하고 package는 raw bytes를 사용한다.
* RTC stale marker를 제거하면 rtc-certified payload가 잘못 허용될 수 있다. RTC applicability는 별도 exact-generation 증거가 없으면 항상 fail-closed한다.

### Regression Risk

* 역사 테스트를 단순 optional로 내리면서 현재 실패 보호가 사라질 수 있다. protection mapping 없이 test disposition을 변경하지 않는다.
* migration-specific writer를 삭제한 뒤 source correction 절차가 사라질 수 있다. Git-authored source change와 full generation/install 절차를 ENTRYPOINTS에 먼저 문서화한다.
* 현재 사용자 변경과 계획 구현이 섞이면 baseline과 closeout identity가 달라진다. 별도 clean worktree와 exact commit binding을 사용한다.
* 후속 계획이 폐기된 IAR role/adoption 문구를 따라 stateful dependency를 재도입할 수 있다. 세 계획을 closeout 대상에 포함한다.

---

## 10. Rollback Plan

* Change 1–4는 protected current에 쓰지 않으므로 실패 시 새 off-live 코드/증거만 되돌리고 기존 IAR 경로를 그대로 유지한다. Change 4의 protected-current descriptor 삭제·재생성은 금지된다.
* 결정론 hard gate가 실패하면 current migration을 시작하지 않는다. 원인과 최소 재현을 남기고 `RETIREMENT_NOT_ACHIEVABLE` 또는 `blocked`로 종료한다.
* 후속자 build/validate는 외부 output root에서만 수행한다. 실패 산출물은 current rollback 대상이 아니다.
* safe install 전 current predecessor generation의 exact descriptor와 file universe를 검증하고 rollback reference로 보존한다.
* install 실패 시 검증된 predecessor pointer/manifest를 복원하거나, switch가 이미 성공했다면 검증된 successor를 유지한다. 부분 세대를 복구 대상으로 선택하지 않는다.
* 각 migration commit은 한 책임 경계만 바꾸게 한다: generation, install, RTC, package, validation, docs. 회귀 시 해당 commit을 Git revert할 수 있어야 한다.
* 구 IAR consumer 제거는 successor consumer가 공식 required route에서 PASS한 다음 commit에서 수행한다. 후속자 회귀 시 제거 commit만 되돌려 bounded dual-read 경로로 복귀할 수 있다.
* sealed history는 rollback 중에도 수정하지 않는다.
* `MINIMAL_RESIDUAL`로 전환할 때는 전체 IAR 복원이 아니라 실패한 의무에 필요한 최소 primitive만 유지한다.
* predecessor cleanup은 terminal machine validation과 필요한 review/owner evidence 이후의 별도 action이므로 rollback 가능성이 필요한 동안 실행하지 않는다. cleanup 검증 실패 시 predecessor를 보존하며 retirement 결과를 과장하지 않는다.
* material current 교체가 있었다면 closeout에 어떤 generation이 남았고 predecessor가 어디에 보존됐는지, 복구 가능 여부를 기록한다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`가 최상위 설계 권한이다. 정보 제공 전용, 근거 보존, Recipe/Right-click 독립성, tooltip 최대 4줄, 런타임 100% Lua를 유지한다.
* `docs/EXECUTION_CONTRACT.md` preflight, claim-evidence binding, validation ceiling, non-claims, allowed closeout state를 준수한다. 실행 중 hash가 plan readpoint와 달라지면 재대조한다.
* `DECISIONS.md`의 sealed 결정을 소급 수정하지 않고 additive successor decision과 heading별 disposition을 사용한다.
* DVF Layer 3, QG Layer 4, Publish, RTC, package projection, repository validation의 책임을 합치지 않는다.
* descriptor는 generation identity record이며 authority/adoption token이 아니다.
* current source 변경과 generated output 교체를 하나의 writer 권한으로 합치지 않는다.
* 검증되지 않은 candidate를 live/current/package 경로에 쓰지 않는다.
* protected current direct write는 successor installer의 exact allowlist 외에는 fail-closed한다.
* `unclassified == 0`, `unmapped_failure_protection == 0`, `active_removed_symbol_consumer == 0`은 삭제 전 hard gate다.
* `FULL_RETIREMENT`에는 Layer 1–5 전체의 `active_product_iar_consumer_count_all_layers == 0`이 추가 hard gate다.
* Layer 3 외 `migrate`는 별도 generalization/owner decision과 exact obligation binding 없이는 허용하지 않는다.
* `switch_atomicity=observed_only`를 `proven` 또는 무혼합 불가능성 증거로 읽지 않는다.
* sealed/history는 read-only이며, history 보존을 active product dependency로 사용하지 않는다.
* current-runtime validity와 RTC-certified applicability를 구분한다. stale RTC를 자동 승격하지 않는다.
* source policy와 required validation을 테스트를 통과시키기 위해 완화하지 않는다. 변경은 명시적 owner disposition과 증거가 있어야 한다.
* clean-checkout claim은 exact tracked commit에서만 가능하다. dirty working result, untracked fixture, 개발자 로컬 cache를 증거로 사용하지 않는다.
* 사용자 소유의 기존 dirty 변경을 덮어쓰거나 정리하지 않는다.
* 경로 glob이나 접두사만으로 파일을 삭제하지 않는다.
* R2 owner decision 없이 runtime Lua module/file layout, loader path, stable pointer/manifest contract를 변경하지 않는다.
* Pulse hub-and-spoke 및 submod 독립성 제약을 유지한다.
* 새로운 generated artifact가 IAR state machine을 기본으로 요구하지 않게 한다. state가 정말 필요하면 최소 residual의 소비 지점과 불변식을 별도 승인한다.
* 검증 명령의 exit code가 0이 아니거나 필수 도구가 없으면 PASS를 주장하지 않는다.
* machine validation, independent review, owner decision/seal, canonical closure eligibility를 서로 대체하지 않는다. closeout artifact가 review나 seal authority를 스스로 생성하지 않는다.

---

## 12. Expected Closeout State

이 계획은 bare `complete`를 terminal claim으로 사용하지 않는다. 최종 기록은 다음 두 값을 분리한다.

* `execution_closeout_state`: `docs/EXECUTION_CONTRACT.md`가 허용하는 `complete`, `partial`, `implemented_only`, `blocked` 중 하나. `complete`는 반드시 validation ceiling과 결합된 `execution_closeout_state=complete`로만 기록한다.
* `retirement_outcome`: `FULL_RETIREMENT`, `MINIMAL_RESIDUAL`, `RETIREMENT_NOT_ACHIEVABLE` 중 하나.

`retirement_outcome`은 이 approved plan 범위의 제품 disposition이며 ecosystem-wide closeout state나 새 governance axis가 아니다. `FULL_RETIREMENT`/`MINIMAL_RESIDUAL`은 증거가 충족될 때 `execution_closeout_state=complete`와 결합할 수 있고, `RETIREMENT_NOT_ACHIEVABLE`은 실제 진척에 따라 `partial` 또는 `blocked`로 환원한다.

정상 목표는 validation ceiling의 `unvalidated_but_in_scope`가 비어 있고 모든 계획 조건이 증거에 결속된 `execution_closeout_state=complete`와, 아래 retirement-complete 결과 중 하나의 조합이다. machine 결과만으로 independent review, owner seal 또는 canonical sealed closure를 선언하지 않는다.

### Product outcome: `FULL_RETIREMENT`

* canonical input과 generator contract가 exact하게 고정돼 있다.
* independent Run A/Run B/path-control이 byte-identical complete generation을 만든다.
* external/off-live successor descriptor가 content-derived이며 삭제 후 동일 bytes로 재생성 가능하다. protected-current descriptor를 재생성 대상으로 사용하지 않는다.
* R2 owner decision과 selected implementation subject가 결속돼 있고, 해당 선택지의 automatic/manual validation을 모두 수행했다.
* safe replacement가 failure-injection과 idempotence를 통과하고 `switch_atomicity=proven`이다. concurrent probe의 `observed_only` 결과만으로 이 조건을 충족하지 않는다.
* already-current install이 protected bytes를 전혀 쓰지 않는 deterministic no-op이며 `protected_current_mutation_count == 0`이다.
* Layer 1–5 각각의 active product IAR lifecycle 소비자 수와 전체 합계가 0이다: `active_product_iar_consumer_count_all_layers == 0`.
* obligation ledger의 `unclassified == 0`, `unmapped_failure_protection == 0`, `unclassified_layer_count == 0`이다.
* Layer 3 외 migrated row가 있다면 각 row에 별도 generalization/owner decision과 exact obligation evidence가 결속돼 있다.
* `dvf_3_3_input_manifest.json`의 generation/history/adoption/package/validation 역할별 disposition이 닫혀 있다.
* `generation_key_identity_validation`, runtime Lua load-result parity와 package generation identity가 검증되고 RTC applicability는 별도 축이다.
* 필수 테스트, source policy, clean-checkout full gate, Lua syntax, package 검증이 exact exit code 0이다.
* sealed history는 보존되고 current product path는 history work root에 의존하지 않는다.
* 설계 문서와 후속 계획이 successor 책임을 정확히 가리킨다.

`FULL_RETIREMENT`는 “Layer 1–5의 활성 제품 Artifact Registry lifecycle dependency 0”만 뜻한다. independent repository-validation governance 제거, RTC PASS, Publish PASS, release readiness, independent review 또는 owner seal을 뜻하지 않는다.

### Product outcome: `MINIMAL_RESIDUAL`

canonical input, determinism, compatibility와 evidence-integrity 조건을 만족하지만 하나 이상의 correctness obligation에 제거 불가능성이 증명된 primitive가 필요한 경우다. residual mechanism 자체가 해당 obligation을 증명해야 하며 concurrent probe의 `observed_only`만으로 residual correctness를 주장하지 않는다. closeout에는 다음을 필수로 포함한다.

* residual file/symbol/consumer/information-layer exact allowlist
* 보호하는 correctness obligation과 실패 사례
* 더 단순한 대안이 실패한 증거
* owner와 변경 금지 경계
* 후속 retirement 재평가 조건
* residual이 새 artifact의 기본 architecture로 확장되지 않음을 검증하는 테스트
* Layer 1–5 active product consumer count와 residual count의 exact reconciliation
* `switch_atomicity=observed_only` 때문에 residual이 필요한 경우 bounded probe 범위와 증명되지 않은 mixing 가능성의 explicit non-claim

`MINIMAL_RESIDUAL`도 product retirement-complete 결과지만 canonical sealed closure는 별도의 required review/owner axes가 충족된 경우에만 주장할 수 있다.

### Product outcome: `RETIREMENT_NOT_ACHIEVABLE`

결정론, 입력 완결성, R2 owner decision, `switch_atomicity=proven` 또는 동등한 무혼합 correctness mechanism, runtime/package parity, obligation replacement, 필요한 cross-layer generalization decision 중 하나라도 hard gate를 통과하지 못하고 최소 residual로도 정직하게 보존할 수 없으면 이 outcome을 사용한다. 이 경우 execution closeout state는 실제 진척에 따라 `partial` 또는 `blocked`이며 retirement-complete가 아니다.

* current IAR 제품 경로는 제거하지 않는다.
* protected current는 진입 readpoint 또는 마지막으로 완전히 검증된 generation으로 유지한다.
* 실패 축, 재현 명령, 증거 hash, 제거를 막은 Layer/소비 지점, 다음 owner decision을 기록한다.
* 은퇴 완료, RTC 완료, Publish 완료, independent review 완료, owner seal, canonical closure, 릴리스 완료를 주장하지 않는다.

### Terminal record requirements

최종 `closeout.json`은 기존 authority axis를 재정의하지 않고 최소한 다음을 서로 독립적으로 보고한다.

* execution contract: checked flag, path, version/hash, known conflict count와 disposition
* exact subject: commit, tree, required source/artifact identities
* execution closeout state와 validation ceiling의 `validated`, `out_of_scope`, `unvalidated_but_in_scope`
* product `retirement_outcome`
* retirement scope surface: Layer 1–5별 active product IAR consumer count와 `active_product_iar_consumer_count_all_layers`
* obligation ledger: `unclassified`, `unmapped_failure_protection`, `unclassified_layer_count`, evidence path/hash
* Layer 3 외 migration: row별 `owner_decision_required`, generalization decision subject/path/hash, obligation-equivalence evidence
* R2 runtime-layout owner decision: selection, exact subject, evidence path/hash
* machine axes: `baseline`, `canonical_inputs`, `determinism`, `complete_generation`, `generation_key_identity_validation`, `safe_replacement`, `switch_atomicity`, `concurrent_observation`, `protected_current_mutation_count`, `lua_load_result_parity`, `direct_writer_residual`, `runtime_compatibility`, `package`, `required_validation`, `source_policy`, `history_preservation`, `documentation`
* `switch_atomicity`: `proven`이면 OS/file-system contract와 선형화 지점 evidence, `observed_only`이면 probe schedule/count/result와 mixing 불가능성 non-claim
* governance axes: independent review, owner decision/seal, canonical closure eligibility의 기존 authority result와 exact evidence binding
* predecessor cleanup: performed/not performed 사실, 이유, rollback availability. 이 필드는 install 성공을 뜻하지 않는다.
* explicit non-claims: RTC, Publish, release/Workshop, deployment, semantic quality, multiplayer/long-session, sealed closeout 중 실제로 선언하지 않는 항목. `switch_atomicity=observed_only`이면 filesystem atomicity와 mixing 불가능성을 반드시 포함한다.

machine validation PASS는 independent review PASS가 아니고, independent review PASS는 owner seal이 아니며, owner seal도 validation을 대체하지 않는다. required governance evidence가 없으면 해당 사실을 validation ceiling/non-claims에 남기고 canonical sealed closeout을 선언하지 않는다.
