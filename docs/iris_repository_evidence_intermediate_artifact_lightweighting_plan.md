# Implementation Plan

> 상태: implementation planned / `PREDECESSOR_UNSEALED`
> 작성일: 2026-08-10
> 최종 수정일: 2026-08-10
> 관찰 기준 readpoint: commit `1e0b706db7a5e965f26008f89017a5f648c5fb12`, tree `95ad6e2439e494c78fe1b6022fb6a95476f301c7` + 아래 predecessor-seal pre-commit census; 이 조합은 실행 subject가 아님
> 실행 기준 readpoint: `UNSEALED`; C0-a predecessor commit/tree가 유일한 predecessor adoption 경로
> 양식: `docs/PLAN_TEMPLATE.md`
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> 선행 완료 계획: `docs/iris_repository_runtime_lightweighting_plan.md`

---

## 1. Objective

Working tree에서 완료로 정리 중인 Iris repository/runtime lightweighting predecessor를 먼저 exact subject로 봉인한 뒤, 그 current authority, historical reproduction, receipt-bound validation, 공개 Lua 계약을 보존하면서 저장소에 남은 build evidence와 intermediate artifact의 물리적 중복을 줄인다. 주된 목표는 runtime Lua 재설계가 아니라 다음 네 storage surface의 후속 경량화다.

1. baseline/final 전체 snapshot을 반복 보존하는 lifecycle manifest v1
2. attempt마다 동일 payload를 복사하는 historical staging
3. 동일 ledger/view를 여러 파일로 materialize한 `2105_baseline_consumption_audit`
4. checkout 안에 상시 남아 있는 `_archive`, `.pyc`, stale package projection

Repository/evidence closeout 뒤에는 `IrisMain.lua`의 남은 boot-time static-data preload만 별도 runtime checkpoint로 줄인다. 이미 demand-load되는 Layer3 11개 청크와 UseCaseDescriptions 9개 청크는 유지한다. Compatibility facade와 Browser/Tooltip allocation은 consumer/heap evidence를 수집하는 측정 범위로만 두며, 증거 없이 제거하거나 재설계하지 않는다.

2026-08-10 current working tree 실측은 다음과 같다. 이 값은 계획 시점 baseline이며, 실제 실행은 별도 physical subject와 clean validation subject에서 다시 봉인한다.

| Surface | Files | Bytes | Codebase observation |
| --- | ---: | ---: | --- |
| `Iris/` 전체 | 7,782 | 1,346,575,791 | tracked 610,417,076 bytes, ignored 736,146,216 bytes다. |
| `Iris/build/description/v2/staging/` | 5,208 | 1,081,097,121 | tracked 3,405 files / 444,175,472 bytes다. |
| 자연화 public-text closure | 701 | 546,889,988 | 17개 numbered attempt와 8개 development probe가 있다. |
| `2105_baseline_consumption_audit` | 43 | 198,171,920 | `classified_ledger.jsonl`과 `consumption_inventory.jsonl`은 각각 24,084,549 bytes다. |
| lifecycle manifest v1 pair | 15,027 rows | 105,988,328 | baseline 7,512 rows, final 7,515 rows이며 exact shared row는 6,737개다. |
| `Iris/_archive/` | 86 | 74,806,195 | 모두 ignored local historical/diagnostic payload다. |
| `Iris/build/package/` | 103 | 2,863,665 | ignored projection이며 package script는 이미 external `-OutputRoot`를 요구한다. |
| `Iris/**/*.pyc` | 445 | 10,104,228 | tracked 1개 / 9,677 bytes가 포함된다. |
| runtime Lua | 103 | 2,924,937 | repository 경량화의 주 용량 표적이 아니다. |

### Predecessor seal pre-commit census

위 commit/tree만으로는 working-tree에 존재하는 predecessor closeout 상태를 재현할 수 없다. 다음 9개 row는 C0-a predecessor seal commit에 전부 포함되어야 할 변경의 사전 census다. Raw SHA-256은 checkout bytes, Git blob OID는 동일 bytes를 Git object로 materialize했을 때의 identity다. 이 table과 hash metadata만으로 bytes의 durable availability를 제공할 수 없으므로 base+uncommitted-delta subject 또는 patch/blob-bundle fallback으로 채택하지 않는다.

| Status | Path | Bytes | Raw SHA-256 | Git blob OID |
| --- | --- | ---: | --- | --- |
| `M` | `Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json` | 6,883 | `a3c7e3c24fd4c45d2596385f14fba5a735d21f8d04dc6469f81a0b6fdb8debff` | `bf52d7c048d675a865b8978a4d6cde6e55658da4` |
| `M` | `Iris/_docs/refactor/repository_runtime_lightweighting/validation_checkpoint_manifest.json` | 57,530 | `558a9850c483e1900016a5392717191704acecd5ba870a6de81ebbcec9c981da` | `b59fcc33d6bf6148b16d33caf4426720b7c94afc` |
| `M` | `Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py` | 8,518 | `27a0a40a864e53749cedddc50b50a600f6f360914d0c83d5c81d7c6ee07225e1` | `f6fb2b876e91094c2dc721aab39ad025504bec5b` |
| `M` | `Iris/test/validate_residual_refactor_surfaces.ps1` | 43,114 | `ca65672b414cc679d0be4c73794e89253ed3b602596075d5653ce3a535820454` | `8ca6e6415948337a08c330fda228b09b06804909` |
| `M` | `Iris/validation/residual_refactor/report_inventory.py` | 21,978 | `a69242a301d210b15997eeb7ab34ad3222bd0f4e774f878bf832ef434b4a65f3` | `948f08b741125208c532fda222fe5c2c48bf3809` |
| `M` | `docs/ARCHITECTURE.md` | 79,839 | `526a81f02043bf3f990cab9cb9da903993f8f16fbab129bed8db267f812ee7e3` | `a7a45a53d721d97281f45be694043ee576e6893f` |
| `M` | `docs/DECISIONS.md` | 236,741 | `797d6eff31baac4776befe1f414154a83b8a66eda1c88f69f62bdb11e7832f35` | `3fbedf0fcd43cadb5399baba64759250e8cd081d` |
| `M` | `docs/ROADMAP.md` | 81,956 | `f1df8afb11d89e063cff015aa6360592e5bbd7c5c6c9b355a889558cabd1286f` | `7f1c9e854ef313accb8bac0710a1d46e125521fd` |
| `??` | `Iris/_docs/refactor/repository_runtime_lightweighting/tooling_track_adoption_receipt.json` | 12,499 | `4356e47b58eea3ba6fdd132a1cdbf12d736a14e16ead45e1bd2c73e5e9966a2d` | `8d3347f688949646f0330da1a68a9a99b57a52a7` |

Planning seed는 authority가 아니다. C0-a generator가 generator path/Git blob/raw SHA, canonical JSON schema, UTF-8/LF/key/row ordering, exact argv를 receipt에 봉인한 뒤 위 census에서 seed를 계산한다. 어느 row/hash라도 달라지면 기존 seed를 폐기하고 fresh census에서 다시 계산한다.

현재 staging의 재측정 기준은 5,208 files / 1,081,097,121 bytes다. 전체 regular file을 raw SHA-256으로 묶고 각 group의 `size * (count - 1)`을 합한 결과는 443 duplicate groups, 1,837 member files, 1,394 excess copies, 39 rounds, 481,097,523 bytes의 working-tree upper bound다. Tracked staging만 같은 방식으로 계산하면 307 groups, 1,160 member files, 853 excess copies, 27 rounds, 137,168,441 bytes다. 입력 로드맵의 472.71 MiB/136.5 MB는 다른 readpoint/population의 제안치로 보존하되 실행 denominator로 사용하지 않는다.

현재 코드에서 확인된 선행 사실은 다음과 같다.

* `Iris/_docs/refactor/repository_runtime_lightweighting/work_root_contract.json`은 이미 `objects/sha256/<prefix>/<sha256>`, atomic create-new promotion, dangling reference `0`, 외부 work/result root를 계약한다.
* `report_artifact_lifecycle.py`는 lifecycle v1 full manifest를 생성하고, `promote_artifact_lifecycle_evidence.py`와 `execute_artifact_lifecycle.py`는 `artifact_role_manifest.jsonl`과 `final_artifact_role_manifest.jsonl`의 exact path/hash를 직접 소비한다.
* `2105_baseline_consumption_audit`는 보관 문서만이 아니다. `_dvf_3_3_vnext_common.py`, `consumer_universe_denominator_lock_common.py`, `dvf_3_3_consumer_migration_normalization_common.py`, `dvf_3_3_shared_disposition_consumption_common.py`, `dvf_3_3_terminal_disposition_adjudication_common.py`가 physical path를 직접 읽는다.
* 자연화 closure의 `attempt-0023`/`attempt-0024` payload는 `validated_naturalization_runtime_adoption.py`, public-text 도구와 runtime/package tests에서 exact path/SHA로 결속되어 있다.
* `IrisMain.lua`의 `INIT_MODULES`는 `IrisRecipeIndex`, `IrisMoveablesIndex`, `IrisFixingIndex`, `IrisClassifications`, `IrisBrowserData`를 boot에 require한다. 반면 `API/StaticData.lua`와 `IrisBrowser.lua`에는 이미 first-use loader/cache 경계가 있다.
* `IrisLayer3DataChunks.lua`와 `IrisUseCaseDescriptions.lua`는 direct compatibility require 시 전체 청크를 병합한다. 내부 lookup router는 이미 binary-search와 chunk cache를 사용한다.
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p 'test_phase5_iris_main_function_specs_contract.py'`의 현재 관찰 결과는 4 tests / 1 failure / exit `1`이다. 실패 원인은 현재 source에는 이미 없는 `local function buildBrowserData(moduleResult)`을 요구하는 stale diagnostic expectation이다. 이는 predecessor PASS가 아니라 Change 6 전에 봉인·수정·채택해야 할 known baseline failure다.
* Current working tree의 residual validator는 exit `1`, exact throw `repository lightweighting protected-surface successor differs from HEAD` 상태다. C0-a commit 직후 같은 baseline evidence와 exact argv를 사용해 clean materialization에서 재실행하고 exit `0`가 되지 않으면 predecessor seal을 채택하지 않는다.
* Working-tree `protected_surface_successor_manifest.json` v2는 v1의 39 revisions/146 added protected rows를 `historical_manifest_attestation.interpretation=embedded_identity_chain_only`로 보존하고 active revisions 2개/active entries 5개(activation delta 1개, added protected row 4개)를 직접 검증한다. 두 번째 active revision의 `protection_predecessor_commit/tree`는 durable commit `0da5e67dea0e51340a9c8097a347f000e7fe8255` / tree `e38a184a317cb7f6f1919c39466c4e734911ff81`에 결속하고, pruned `dac450...` / `ba415...`는 `evidence_subject_commit/tree`로만 보존해 active predecessor로 역참조하지 않는다. Current required residual contract test도 두 active revision ID를 순서대로 요구하며, 그 final protected identity는 Git blob `f6fb2b876e91094c2dc721aab39ad025504bec5b`, LF SHA-256 `5d212bceb65e8e1bad91235ee5febf035fcf24085201722826b8f242a655329e`로 active protected row와 일치한다. `.gitignore`는 v1 chain에는 있으나 v2 active row에는 없으므로 Change 1/3/4 편집 가능성은 이 축소에 기대지 않고 새 successor policy와 owner approval로 별도 승인한다.
* 현재 source scan에서는 `report_inventory.py`의 lifecycle v1 exact-path reference가 발견되지 않았다. Change 2에서 동일 source blob에 대해 scan을 재실행하고 no-change disposition을 receipt에 봉인한다.

완료 상태에서는 동일 payload가 hash당 한 번만 물리적으로 보존되고, historical attempt는 content reference와 chronology만 보유한다. 기존 v1 manifest와 historical tree는 새 representation에서 byte-identical하게 복원할 수 있어야 하며, current/historical/full-gate validation과 공개 사용자 결과는 변하지 않아야 한다.

---

## 2. Scope

실행 순서는 절감 잠재력이 아니라 위험과 authority 의존성을 기준으로 고정한다.

0. predecessor subject와 successor authority/current-route adoption bootstrap
1. local residue cleanup과 재발 방지
2. lifecycle manifest v2의 additive 도입과 v1 reconstruction
3. historical staging CAS resolver/restore 기반 구축과 pilot
4. `2105_baseline_consumption_audit` normalization 및 나머지 staging migration
5. `_archive` cold archive externalization
6. 남은 runtime eager-load reduction
7. compatibility/allocation evidence 수집과 최종 disposition

각 storage change는 `inventory -> consumer migration -> dual-read/reconstruction -> clean validation -> successor seal -> old payload disposition` 순서를 지킨다. 원본 payload 삭제는 같은 change의 구현 단계가 아니라 마지막 disposition 단계다.

Lifecycle/staging/archive 작업은 새 successor claim `iris_repository_evidence_lightweighting` 아래에서 수행한다. 완료된 `repository_runtime_lightweighting` v1 receipt와 protected-surface successor를 덮어쓰지 않고, 새 evidence root와 additive successor chain을 만든다.

Change 0은 predecessor identity와 successor validation wiring을 봉인한다. Storage/runtime payload migration은 Change 0의 clean validation이 모두 PASS한 뒤 Change 1부터 시작한다.

### C0-a sealed residual baseline contract

C0-a의 residual authority는 아래 pre-C0-a baseline 두 파일의 raw bytes다. 둘의 `subject_commit`/`subject_tree`는 baseline이 관찰한 역사적 subject이고, C0-a validation subject인 새 HEAD와 같아서는 안 된다. Baseline을 C0-a HEAD에서 다시 생성하거나 `-Mode Baseline`으로 갱신해 before/after를 같게 만드는 anti-tautology 경로는 금지한다.

| Role | Exact repository source | Bytes | Raw SHA-256 | Git blob OID | Schema | Sealed baseline subject |
| --- | --- | ---: | --- | --- | --- | --- |
| protected baseline authority | `Iris/_docs/refactor/residual_refactor/phase0_protected_surface_manifest.json` | 13,141 | `aaaecb90efb3bfd36b9b096aaa51b96b45800c1004ca912f75560c45b32b38c2` | `6461f002790d29164d6ab11f0f8f45d726430530` | `iris-residual-protected-surface-v1`; 26 rows | commit `c8b96e40251b9043bae04261a8acd033660e0d45`; tree `1178ed0256296f9ac8a898efb77bb40abb4ee8ea` |
| supported-API baseline authority | `Iris/_docs/refactor/residual_refactor/phase0_supported_api_manifest.json` | 12,300 | `4f968193283e675cc1126a977cdf5735c1f91443fe68df2bdadc2f1ad2e1100f` | `2551cfcf6fbce5bc3785f2667ec42c899c837f63` | `iris-residual-supported-api-v1`; 20 surfaces | same commit/tree |

`Iris/_docs/refactor/residual_refactor/final_protected_surface_report.json`은 raw SHA-256 `853d991def3908fe1dc8f9f1b81bf0a407813b2cbb04c2fa8b226589f8f269b2`, Git blob `49e8bed1b0c9a394a6261da1199ece54184e9c4e`지만 내부 baseline SHA가 `44084abb9285624abd071cce7237ced376bd826726c7119a39240ca6744a2870`여서 현재 sealed protected baseline과 다르다. 이 파일의 disposition은 `stale_report_reference`이며 baseline authority나 C0-a expected report로 사용하거나 rewrite하지 않는다. C0-a의 fresh external report가 위 `aaaecb90...`을 기록해야 한다. `final_supported_api_compatibility_report.json`의 recorded baseline `4f968193...`은 supported baseline과 일치하지만 역시 과거 report이지 입력 authority가 아니다.

C0-a validator가 소비하는 effective authorization map은 protected baseline의 `approved_activation_deltas`, `Iris/validation/clean_checkout/authority/offline_build_validation_protected_surface_delta.json`의 offline delta, v2 successor가 attestation한 v1 historical revisions, v2 `active_revisions`를 이 순서로 접은 결과다. 따라서 `authorized_by_active_delta`는 단순히 v2 `active_revisions`에 직접 등장한다는 뜻이 아니라 이 exact fold 결과에 path와 expected Git blob/LF hash가 모두 일치한다는 뜻이다. Offline delta는 schema `iris-residual-protected-surface-delta-v1`, raw SHA-256 `4d6a3a2d1c050502a7597075653dd02663fc7567c31df7690148b6a8914abbb3`, Git blob `ed2d8b08c3daea113365ff902c01cc256e8c4a86`로 고정한다. V1 attestation은 commit `1e0b706db7a5e965f26008f89017a5f648c5fb12`, Git blob `9bd5e937db13bfd3a88510c36d4f27491673fa0a`, LF SHA-256 `02d9973baffd843de2f19b972440ca7c0f83567d0edd2426c41ecc936dad55be`; v2 active anchor는 commit `ae7b3172cc80b5bf3b2aaed15654d41f707c9134`, tree `6d3ee190ccd0889c6bf684916533008d2268e2f8`다.

현재 baseline 대비 달라진 6개 row는 C0-a expected subject에서 다음과 같이 처분한다.

| Path | Baseline raw SHA-256 | Expected C0-a Git blob / LF SHA-256 | Effective authorization source | Planned disposition |
| --- | --- | --- | --- | --- |
| `Iris/_docs/round3/current_route_required_validations.json` | `0ea650737ab6ccdcc5a2c325c7efddc72fa376fa848e8f8ffd254498e36dc6a1` | `75177ba2ac4b819fc3c120161854eb6b8662f9a7` / `c8a66a0dcb32b2745b810c2658b93baa2ead05426be80c51e47e131ceb48b369` | attested v1 `runtime_track_c48_implementation_v1` | `authorized_by_active_delta` |
| `Iris/_docs/round3/round3_test_taxonomy.json` | `b7706d03f2372881592669f115a52cdac811df61d53dc09f162a458a77c2cac2` | `2ea96ff51a53421d8ed3c1f689d80bcd37579a8d` / `25c4570a82c3132118b84a7ab07b80f1b196595c437056ae87489fb8bec2745f` | attested v1 `runtime_track_c48_implementation_v1` | `authorized_by_active_delta` |
| `Iris/build/description/v2/tools/build/INVENTORY.md` | `f97414d7f65501fb6d6dc977599eea948c24558eda04649d393d277be8addc11` | `d68370d57924038d25b71118cb03a2340a02c221` / `1b6f0a409e136a543f2247b81ad7396ee2470e5609476e15e252e94ad79d57c9` | active v2 `tooling_track_v2_durable_protection_successor_v1` | `authorized_by_active_delta` |
| `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py` | `0886f63a9c4f5de6645e43c318d5e65cb90e963bc81ab53e9e22dc210bff296e` | `85df1cdfa2f0af3ec828eee9573208eacdb7835c` / `12a7da6c13cf6a7def4afeabaf9dd37843363c074fe3e333bf79746ceafca45c` | offline delta manifest | `authorized_by_active_delta` |
| `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py` | `e7d42626d5be9e53f3533ed9e17521679888f0827331aa1f0749466b06783858` | `d18d2cd00006d4e432721ebf9aaf85da0738c244` / `1284853e48033938988f30b64bab19306122348429f5df771c6fb506339ca6c7` | attested v1 `common_clean_checkout_git_long_path_followup_v1` | `authorized_by_active_delta` |
| `Iris/tools/package_iris.ps1` | `a1fca567d4ce06037dff904bf934ee1f751a9b56e79347b8c86b185f1ebfd1cb` | `3b986cd1aa82efe9461f040e659193ea7f765891` / `45a41c0734601c51375606eb80c339e680ebe8665d60ae3e4960f71389e08522` | attested v1 `runtime_track_c48_implementation_v1` | `authorized_by_active_delta` |

C0-a clean run은 각 row에 대해 baseline row, authorization chain, expected blob, expected LF hash를 독립 재계산한다. 하나라도 없거나 불일치하면 해당 row를 자동 승인하지 않고 `requires_new_successor_delta`로 재분류해 C0-a를 중단하고 owner-approved additive successor를 별도 계획한다. 현재 6개 중 `stale_baseline_row`로 제거할 row는 없다. Fresh `final_protected_surface_report.json`은 baseline rows `26`, authorized changed baseline rows `6`, folded unique added protected rows `60`, total report rows `86`, `unauthorized_changed_count=0`, sealed baseline SHA를 각각 명시적 필드 또는 phase-validator 계산으로 기록·검증해야 한다.

### Successor adoption identities

다음 exact path/schema가 새 claim의 authority와 validation wiring을 구성한다.

| Role | Exact path | Required schema/identity |
| --- | --- | --- |
| predecessor subject | `Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json` | `iris_repository_evidence_lightweighting_predecessor_subject_v1` |
| owner approval | `Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json` | `iris_repository_evidence_lightweighting_owner_policy_approval_v1` |
| successor output/storage policy | `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json` | `iris_repository_evidence_lightweighting_output_policy_v1` |
| test taxonomy | `Iris/_docs/round3/round3_test_taxonomy.json` | existing `round3-test-taxonomy-v1`에 successor test IDs additive adoption |
| required validations | `Iris/_docs/round3/current_route_required_validations.json` | existing `round3-current-route-required-validations-v1`에 successor required IDs additive adoption |
| full-gate selection | `Iris/validation/clean_checkout/contracts/full_repository_gate.json` | existing `iris-clean-checkout-full-repository-gate-v7`; exact identity를 항상 결속하되 taxonomy-driven current selection이 새 IDs를 이미 고르면 content change는 하지 않음 |
| successor adoption receipt | `Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json` | `iris_repository_evidence_lightweighting_required_validation_adoption_v1` |

Successor policy는 repository-local CAS를 `raw_byte_representation_only`로 선언한다. CAS object/reference는 source, rendered, runtime 또는 semantic authority가 아니며 기존 artifact role/receipt identity만 운반한다. Owner approval은 repository-local CAS promotion, cold-store backend, deletion authority를 각각 독립 boolean/selection으로 기록하고, 승인되지 않은 축을 묵시적으로 허용하지 않는다.

`invoke_receipt_bound_full_gate.ps1`와 `invoke_deterministic_compare.ps1`는 기존 `repository_runtime_lightweighting_output_policy.json` binding을 유지하면서 새 successor policy, owner approval, predecessor subject, taxonomy, required-validations, `full_repository_gate.json`, adoption receipt의 exact Git blob/raw SHA를 추가로 결속한다. 새 focused test를 직접 실행한 결과는 이 adoption receipt와 full-gate binding 없이는 current-route PASS가 아니다.

Bootstrap adoption test의 exact taxonomy/current-required IDs는 다음 네 개로 고정한다. 모두 source `Iris/build/description/v2/tests/test_repository_evidence_required_validation_adoption.py`, `contract_class=current`, `state=ok`이어야 하며 `current_route_required_validations.json.required_tests`와 full-gate current selection에 포함한다.

* `test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_predecessor_subject_is_exact`
* `test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_successor_policy_owner_approval_and_representation_boundary_are_adopted`
* `test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_taxonomy_required_validation_and_full_gate_are_bound`
* `test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_durable_cas_roots_are_trackable_and_clean_checkout_available`

### Execution Gates

* current working tree의 기존 수정은 사용자 소유로 간주한다. Predecessor adoption은 위 9-row census 전부를 포함한 C0-a commit/tree 하나만 허용한다. Base+dirty delta, hash-only manifest, patch/blob-bundle 또는 일부-row commit fallback은 금지한다.
* C0-a의 허용 dirty-delta scope는 위 9개 predecessor census path로 한정한다. Commit 뒤 그 9개 path는 HEAD와 byte-identical하고 uncommitted delta가 0이어야 하며, 두 validation checkout은 repository 전체가 clean이어야 한다.
* C0-a validation은 C0-a commit/tree, 9-row expected final blob set, sealed residual baseline identities만 결속한다. 아직 생성되지 않은 `predecessor_subject_manifest.json`을 요구하거나 재구성하지 않는다. Active protection predecessor `0da5e67d...`는 실제 Git object/tree/HEAD ancestry로 검증하고, `dac450...` evidence subject는 format-bound embedded evidence identity일 뿐 active predecessor로 rev-parse하지 않는다. Residual test의 folded final added-row identity는 census의 `f6fb...` / `5d212...`와 일치해야 한다. C0-a 뒤 sealed commit의 두 clean materialization에서 HEAD-bound residual validation이 exit `0`로 전환되지 않으면 C0-b로 진행하지 않는다.
* C0-b가 `predecessor_subject_manifest.json`을 생성·commit한 뒤 physical census subject와 두 clean validation subject가 동일한 C0-a predecessor commit/tree와 C0-b manifest SHA에서 파생됨을 검증한다. Physical subject는 ignored/local payload를 포함할 수 있지만 tracked bytes는 C0-a와 같아야 하며, clean validation subjects는 dirty/untracked repository state가 없어야 한다.
* Independent materialization은 동일 sealed commit에서 만든 서로 다른 두 checkout directory와 서로 다른 empty/non-nested external work/result roots를 뜻한다. 두 materialization은 동일 `.gitattributes` raw SHA, path별 attributes와 recorded `core.autocrlf`을 사용하고 각각 raw hash/Git blob set을 독립 계산한다. 기존 dirty working tree와 한 checkout을 두 번 읽는 것은 independent로 세지 않는다.
* C0-c의 focused/current/historical validation, receipt-bound full-gate Run A/B와 deterministic compare가 모두 exit `0`이고 receipt identity가 C0-a/C0-b subject와 일치하기 전에는 `.pyc`/package 삭제를 포함한 Change 1~7 physical/runtime mutation을 시작하지 않는다.
* `Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json`의 기존 owner approval은 이 후속 migration의 repository-local CAS promotion 또는 cold-store 선택 승인으로 확대 해석하지 않는다.
* authoritative physical census와 byte reduction receipt는 실제 ignored/local payload가 존재하는 physical subject에서 생성한다. clean checkout은 validation authority일 뿐 local physical byte denominator를 대신하지 않는다.
* duplicate census는 `duplicate_census_manifest.json`의 subject commit/tree 또는 predecessor-subject SHA, generator path/blob/SHA, exact argv, population roots, include/exclude rules, row count, manifest SHA로 봉인한다. Change 실행 중 새로 생긴 object/reference는 baseline denominator에 역편입하지 않는다.
* lifecycle v2는 baseline 7,512 rows와 final 7,515 rows를 모두 재구성하고 exact shared 6,737 rows를 보존하는 test가 PASS하기 전에는 v1 pair를 disposition하지 않는다.
* staging path를 직접 읽는 consumer가 하나라도 남아 있으면 해당 payload를 reference-only entry로 바꾸지 않는다. AST/parser scan, lexical fallback, runtime command-manifest scan으로 executable read/write를 찾고 docs/comment/reference-only hit와 분리한다. 동적이어서 판정할 수 없는 hit는 blocking `unresolved_executable_reference`다.
* CAS object는 raw byte SHA-256, byte length, media type, original relative path, attempt/phase identity, producer version을 가진다. Machine-specific external absolute path 금지는 이 계획이 새로 생성하는 successor evidence에 적용한다. Immutable predecessor evidence의 기존 absolute path를 소급 rewrite하지 않는다.
* `.gitignore` default-deny를 보완해 `Iris/build/description/v2/evidence/objects/sha256/**`와 `Iris/build/description/v2/evidence/references/**`의 approved files만 allowlist한다. Durable promotion 전 `git check-ignore`, `git ls-files --error-unmatch`, clean-checkout physical existence/hash 검증이 모두 PASS해야 한다.
* current-required 또는 clean-checkout historical-reproduction payload는 repository-available CAS에 둔다. 외부 cold archive만으로 이동하는 대상은 복구 위치의 지속성, hash 검증, restore test, owner disposition이 별도로 승인된 항목으로 제한한다.
* Runtime Change 6은 repository/evidence changes의 terminal clean validation 뒤 별도 checkpoint에서만 시작한다.
* Compatibility facade, `IrisData.lua`, `LineCountIndex.lua`, Browser/Tooltip cache 변경은 Change 7의 측정/consumer gate가 열어 주지 않으면 구현하지 않는다.

### Explicitly Out Of Scope

* Layer3 11개 청크 또는 UseCaseDescriptions 9개 청크의 재분할/positional schema 전환
* Python 파일 수나 LOC만을 근거로 한 build tooling 통합 또는 삭제
* 트랙 종료 script, test, PowerShell harness의 일괄 축소
* `IrisLayer3DataChunks.lua`, `IrisUseCaseDescriptions.lua`, `IrisData.lua` public surface의 즉시 제거
* `Iris/output/` 5.89 MB와 `historical_reproduction_corpus.zip` 6.93 MB의 자동 disposition
* source/rendered/runtime authority 내용, Layer3 2,105-entry 의미, 한국어 문구, UI 구조 변경
* package publication, release/Workshop/B42 readiness
* Pulse 또는 다른 Pulse submod 변경

---

## 3. Non-Goals

* 압축률이나 파일 수만으로 current authority와 historical reproduction 필요성을 재분류하지 않는다.
* Git tracked/ignored 상태를 보존/삭제 판정으로 사용하지 않는다.
* CAS reference를 새로운 semantic authority로 만들지 않는다.
* historical attempt chronology, failed attempt, owner attestation을 성공 attempt로 합치지 않는다.
* normalized view에서 원래 JSONL row 의미나 ordering을 다시 해석하지 않는다.
* `.pyc`와 package residue의 local 절감량을 tracked repository 절감량으로 보고하지 않는다.
* staging physical duplicate, tracked duplicate, `2105` normalization candidate처럼 모집단이 겹치는 절감량을 합산하지 않는다.
* runtime source byte 감소를 Kahlua heap 또는 boot-time 개선 수치로 대신하지 않는다.
* 외부 mod consumer 조사 없이 compatibility facade를 proxy/metatable view로 바꾸지 않는다.
* heap/allocation 측정 없이 Browser search, grouping, variant 또는 tooltip cache를 선행 변경하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 권위이며 Iris는 100% Lua wiki-style viewer라는 경계를 유지한다.
* Working-tree `docs/DECISIONS.md`와 `docs/ROADMAP.md`는 기존 repository/runtime lightweighting을 완료로 정리하지만, Change 0 seal 전에는 그 상태를 predecessor authority로 주장하지 않는다. 봉인된 predecessor 완료 상태가 채택된 뒤에만 이 계획이 계승한다.
* current source/rendered/runtime chunk chain은 storage migration과 독립된 보호 표면이다.
* `Iris/_docs/refactor/repository_runtime_lightweighting/`의 predecessor closeout 변경은 C0-a commit/tree가 모두 durable하게 포함한 뒤에만 predecessor subject가 된다. Working delta/hash metadata 자체는 adoption identity가 아니다.
* current lifecycle v1 writer의 canonical JSONL ordering과 SHA-256은 deterministic하다.
* lifecycle v2의 baseline+delta는 compact storage format이지만, v1 baseline/final stream을 exact bytes로 복원하는 codec을 제공한다.
* 기존 `objects/sha256/<prefix>/<sha256>` 계약, external root allocator, command receipt chain은 구현 precedent로 재사용할 수 있다. 새 scope의 owner approval과 schema identity는 별도로 필요하다.
* repository-local CAS에 같은 SHA가 이미 있으면 byte identity를 검증하고 재사용하되 overwrite하지 않는다.
* `classified_ledger.jsonl`과 `consumption_inventory.jsonl`의 현재 byte identity는 재측정해 receipt에 결속한다. 두 이름의 역할이 같다고 의미적으로 가정하지 않는다.
* `Iris/build/package`는 direct package-specific rule이 아니라 상위 `.gitignore`의 `Iris/build/*` default-ignore에 의해 ignored된다. `Iris/tools/package_iris.ps1`는 explicit external `-OutputRoot` 없이는 fail-loud하고, `Iris/test/validate_disposable_package.ps1`는 local peer를 mutation하지 않는다.
* `StaticData.get()`은 session-stable lazy cache이며 `IrisAPI.Tags`/`Index`의 first-use caller가 필요한 static data를 로드할 수 있다.
* standalone Lua harness는 module load/count/parity contract를 증명하지만 실제 Project Zomboid/Kahlua memory와 first-use latency를 대체하지 않는다.
* Byte-exact reconstruction subject는 `core.autocrlf`, `.gitattributes` raw SHA-256, 대상 path별 `git check-attr -a`, checkout raw SHA와 Git blob OID를 함께 기록한다. 현재 관찰값 `core.autocrlf=true` 자체를 다른 subject에 일반화하지 않는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* `Iris/validation/residual_refactor/report_inventory.py`
* `Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* `Iris/validation/residual_refactor/repository_evidence_codec.py` (new)
* `Iris/validation/residual_refactor/migrate_repository_evidence.py` (new)
* `Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1`
* `Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1`
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/_docs/round3/round3_run_contract_tests.py` (read-only CLI/selection verification; existing flags로 exact taxonomy/required-validation binding이 불가능할 때만 conditional edit)
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py`
* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_consumer_migration_normalization_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py`
* `Iris/build/description/v2/tools/build/validated_naturalization_runtime_adoption.py`
* direct historical payload readers listed by the finalized migration consumer manifest
* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`

### Tests

* `Iris/build/description/v2/tests/test_artifact_lifecycle_inventory.py`
* `Iris/build/description/v2/tests/test_artifact_lifecycle_promotion.py`
* `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py`
* `Iris/build/description/v2/tests/test_repository_evidence_codec.py` (new)
* `Iris/build/description/v2/tests/test_repository_evidence_migration.py` (new)
* `Iris/build/description/v2/tests/test_repository_evidence_required_validation_adoption.py` (new)
* `Iris/build/description/v2/tests/test_phase5_iris_main_function_specs_contract.py`
* `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`
* `Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py`
* `Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py`
* `Iris/test/lua/browser_state_acceptance_harness.lua`
* `Iris/test/lua/lazy_lookup_acceptance_harness.lua`
* `Iris/test/validate_disposable_package.ps1`
* `Iris/test/validate_residual_refactor_surfaces.ps1`

### Docs

* `docs/iris_repository_evidence_intermediate_artifact_lightweighting_plan.md`
* `docs/ARCHITECTURE.md` (closeout 시 additive boundary 반영)
* `docs/DECISIONS.md` (adoption/hold/rollback decision 반영)
* `docs/ROADMAP.md` (실제 완료 범위만 반영)

### Config

* `.gitignore`
* `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json` (new, owner approval required)
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json` (read and identity-bind; taxonomy-driven selection이 부족할 때만 conditional edit)
* required-validation/protected-surface manifest의 additive successor 파일; 기존 sealed manifest는 overwrite하지 않는다.

### Generated Artifacts

* `Iris/_docs/refactor/repository_evidence_lightweighting/` (new predecessor/approval/adoption manifests, hashes, receipts, migration/restore evidence)
* `Iris/build/description/v2/evidence/objects/sha256/` (current-required/historical-reproduction unique objects only)
* `Iris/build/description/v2/evidence/references/` 아래의 tracked attempt/phase reference manifests
* external run-scoped `objects/`, `phases/`, `logs/`, `package/` roots
* external compressed cold archive and its repository-side hash/schema/restore manifest
* predecessor `artifact_role_manifest.jsonl` / `final_artifact_role_manifest.jsonl` reconstruction outputs; validation 중에만 external root에 materialize한다.

---

## 6. Planned Changes

### Change 0 — Execution identity and successor validation bootstrap

Purpose:

Predecessor closeout subject와 successor policy/owner/current-route adoption을 먼저 봉인해 이후 모든 census, mutation, receipt가 하나의 재현 가능한 execution identity를 계승하게 한다.

Files:

* `Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json` (new)
* `Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json` (new)
* `Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json` (new)
* `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json` (new)
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json` (conditional content change)
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/build/description/v2/tests/test_repository_evidence_required_validation_adoption.py` (new)

Implementation Notes:

* C0-a — predecessor seal: 위 9-row census의 exact bytes를 모두 포함한 predecessor closeout commit을 만든다. 이 phase의 gate는 9-row final Git blob set, 두 clean materialization과 §2 sealed residual baseline Closeout이다. `predecessor_subject_manifest.json`은 아직 존재하지 않으며 요구하지 않는다. Working delta fallback은 없다.
* C0-b — predecessor identity seal: `predecessor_subject_manifest.json`을 생성해 commit한다. Manifest는 C0-a commit/tree, 9-row blob set, C0-a residual receipts를 결속하며 두 independent clean checkout에서 byte-exact하게 재구성한다.
* C0-c — bootstrap successor seal: successor policy, owner approval, required-validation adoption receipt, taxonomy, required-validations, launcher/compare binding, adoption test를 구현해 한 clean commit으로 봉인한다. `full_repository_gate.json`은 새 current+ok IDs가 기존 taxonomy-driven selection으로 실제 선택되지 않을 때만 최소 변경하며, 변경하지 않아도 exact existing blob/raw SHA를 adoption receipt와 launchers에 결속한다.
* C0-c commit의 두 independent clean materialization에서 focused, current, historical, receipt-bound Run A/B와 deterministic compare를 실행한다. Source checkout dirty rejection, policy/identity drift와 missing current selection은 fail-loud한다.
* Successor policy는 allowed durable CAS/reference roots, external roots, representation-only authority boundary, tracking requirement, owner-gated cold-store/delete 축과 required receipt fields를 정의한다.
* Owner approval은 exact policy Git blob/raw SHA와 predecessor subject manifest를 가리킨다. Generic task approval이나 predecessor policy approval을 재사용하지 않는다.
* 새 lifecycle/CAS/adoption tests는 `round3_test_taxonomy.json`에서 current/diagnostic class와 state를 명시하고, closeout에 필요한 current tests는 `current_route_required_validations.json.required_tests`에 exact test ID로 추가한다.
* Full-gate launcher와 deterministic compare는 predecessor subject, 새 policy, owner approval, taxonomy, required-validation, full-gate contract, adoption receipt를 모두 implementation identity와 inner/orchestration receipt에 결속한다.
* Bootstrap은 census + governance/validation artifact 작성과 commit만 허용하며 storage/runtime payload migration 권한이 아니다. 각 commit은 좁은 scope로 만들고 다음 phase는 직전 commit의 clean validation이 PASS한 뒤에만 시작한다.

Validation:

* C0-a predecessor commit/tree가 9-row pre-commit census의 final Git blob set을 전부 포함하고 해당 9 paths의 dirty delta 0
* C0-a의 두 clean materialization에서 sealed two-file EvidenceRoot를 사용한 `validate_residual_refactor_surfaces.ps1` exact invocation exit `0`; known `differs from HEAD` throw 0, unauthorized changed 0, 6-row authorization disposition 동일
* C0-b predecessor manifest가 C0-a commit/tree/9-row set을 byte-exact 재구성하고 physical census subject 및 두 clean subjects가 같은 manifest SHA에 결속
* C0-c의 두 independent materialization에서 commit/tree, `.gitattributes` SHA, recorded `core.autocrlf`, raw hash/Git blob set과 external-root isolation 동일
* policy/approval/schema/path mismatch, missing committed input, dirty checkout, hash drift fail-loud
* 위 네 exact test ID가 taxonomy와 required-validations에 존재하고 `round3_run_contract_tests.py --class current --taxonomy Iris/_docs/round3/round3_test_taxonomy.json --required-validations Iris/_docs/round3/current_route_required_validations.json --enforce-current-build-closure`에서 실제 선택됨
* receipt-bound Run A/B와 deterministic compare receipt에 새 policy/approval/taxonomy/required-validation/adoption identity가 존재
* 모든 phase별 exact command exit `0`; 그 전 실행 상태는 계속 blocked

---

### Change 1 — Local residue cleanup and recurrence guard

Purpose:

C0-c의 terminal clean validation이 PASS한 뒤 authority/historical evidence를 건드리지 않고 `.pyc` 445개와 stale `Iris/build/package` projection을 제거하고 재발을 막는다.

Files:

* `.gitignore`
* `Iris/_docs/round3/__pycache__/round3_run_contract_tests.cpython-314.pyc` (tracked deletion candidate)
* ignored `Iris/**/__pycache__/**`, `Iris/**/*.pyc`
* ignored `Iris/build/package/**`
* `Iris/test/validate_disposable_package.ps1`

Implementation Notes:

* 이 change는 작은 local cleanup이지만 physical mutation이므로 C0-c terminal validation 전에는 실행하지 않는다. 삭제 직전 `predecessor_subject_manifest.json`, successor policy, owner approval과 adoption receipt의 raw SHA/Git blob을 다시 검증한다.
* 먼저 package projection의 source identity/parity를 external candidate에서 재검증한다.
* `.gitignore`를 `Iris/build/description/v2/**`에만 한정된 현재 rule에서 repository-wide Iris Python cache를 포함하도록 확장한다.
* tracked `.pyc`는 source가 아니며 삭제 뒤 `uv run python -B`/`PYTHONDONTWRITEBYTECODE=1` 경로로 재생성되지 않아야 한다.
* local `build/package`는 삭제하되 package script와 validation은 external temporary/result root만 사용한다.
* 이 change의 byte receipt는 tracked deletion, ignored bytecode, package projection을 분리한다.

Validation:

* `git ls-files -- '*.pyc'` 결과 0
* `Get-ChildItem -LiteralPath Iris -Recurse -File -Filter '*.pyc'` 결과 0
* disposable package가 external root에서 source와 동일하게 재생성됨
* package validation 전후 `Iris/build/package`가 존재하지 않음
* cleanup receipt의 predecessor-subject, successor policy, owner approval과 adoption receipt SHA가 Change 0 bootstrap identity와 동일
* current/protected-surface validation exit 0

---

### Change 2 — Lifecycle Manifest v2: baseline plus delta

Purpose:

약 105,988,328 bytes인 v1 baseline/final full-manifest pair를 normalized baseline + final delta로 전환하되 두 v1 stream을 완전히 복원한다.

Files:

* `Iris/validation/residual_refactor/repository_evidence_codec.py` (new)
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* `Iris/validation/residual_refactor/report_inventory.py` (inventory/measurement contract 영향 판정 및 필요 시 additive successor 지원)
* `Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* lifecycle 관련 focused tests
* new successor evidence root의 v2 nodes/baseline/delta/receipt

Implementation Notes:

* v2 row key는 repository-relative POSIX `path` 하나이며 중복 key를 금지한다. Baseline row는 key의 Unicode code-point lexical order로 정렬한다.
* Canonical JSON은 UTF-8 without BOM, LF, object key Unicode code-point lexical order, compact separator `,`/`:`, `ensure_ascii=false`, final newline 1개로 직렬화한다. Path별 `git check-attr -a`, `core.autocrlf`, `.gitattributes` identity를 receipt에 결속한다.
* v2는 `path`, consumer identity, node identity, relation edge를 dictionary/node table로 정규화한다. Dictionary/node IDs는 canonical raw bytes SHA-256에서 파생하고 collision 또는 동일 ID의 상이 bytes를 fail-loud한다.
* baseline은 전체 logical state를 표현하고 final은 row key당 정확히 하나의 `add`, `remove`, `replace` delta만 저장한다. Delta는 row key lexical order 뒤 operation precedence `remove < replace < add`로 정렬한다. `remove`는 `before_sha256`, `replace`는 `before_sha256`과 canonical replacement row, `add`는 canonical new row를 기록하며 missing/wrong before hash를 거부한다.
* codec은 `v2 -> v1 baseline JSONL`과 `v2 baseline + delta -> v1 final JSONL`을 deterministic하게 제공한다.
* migration receipt는 v1 두 파일의 raw SHA-256/bytes/row count와 reconstructed output의 동일성을 결속한다.
* 기존 promoter/executor는 transition 동안 v1과 v2를 모두 읽되, 같은 invocation에서 서로 다른 representation을 혼합하지 않는다.
* 현재 scan에서는 `report_inventory.py`의 lifecycle v1 exact-path reference가 발견되지 않았다. Change 2는 동일 sealed source blob에 대해 AST/lexical scan을 재실행한다. 영향이 있으면 v1/v2 representation을 동일 logical role로 집계하되 physical bytes는 분리하는 additive reader/test를 넣고, direct/indirect reference가 모두 없으면 scan argv/result/blob을 결속한 no-change disposition을 receipt에 남긴다.
* `validation_checkpoint_manifest.json`과 `protected_surface_successor_manifest.json`의 현재 sealed identity를 수정하지 않는다. 새 successor manifest가 predecessor identity, v2 identity, reconstruction proof를 연결한다.
* v1 pair disposition은 모든 executable consumer가 v2 codec 또는 reconstructed external view를 사용하고 receipt-bound Run A/B가 PASS한 뒤 별도 owner gate에서 수행한다.
* 약 96.5 MiB 절감은 예상치일 뿐 acceptance threshold가 아니다. correctness와 reconstruction이 우선이다.

Validation:

* baseline 7,512 rows와 final 7,515 rows reconstruction
* exact shared row 6,737개와 add/remove/change set parity
* raw SHA-256, byte length, row order, newline convention의 byte-identical parity
* 같은 input에서 v2 artifacts와 reconstructed streams가 byte-stable
* duplicate row key/op, non-canonical JSON, wrong delta order, malformed deletion/replace before hash, unknown node, duplicate edge, dangling node/reference fail-loud tests
* `report_inventory.py`가 v1/v2 logical count와 physical-byte denominator를 혼동하지 않는 focused test 또는 sealed no-impact receipt
* v1 pair를 제외한 뒤 successor chain으로 protected/current/historical/full-gate가 통과하는 dry run

---

### Change 3 — Historical staging CAS foundation and largest-round pilot

Purpose:

동일 historical payload를 attempt마다 복사하는 구조를 unique content object + attempt/phase reference로 전환한다. 첫 pilot은 546,889,988-byte 자연화 public-text closure로 제한한다.

Files:

* `.gitignore`
* `Iris/validation/residual_refactor/migrate_repository_evidence.py` (new)
* `Iris/validation/residual_refactor/repository_evidence_codec.py` (new)
* successor output policy, allocator/command wrapper integration
* `Iris/build/description/v2/evidence/objects/sha256/**` approved immutable objects
* `Iris/build/description/v2/evidence/references/**` tracked attempt/phase reference manifests
* `Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/**`
* `validated_naturalization_runtime_adoption.py`와 finalized consumer graph가 열거한 direct readers/tests

Implementation Notes:

* migration CLI는 최소 `inventory`, `plan`, `promote`, `verify`, `restore`, `materialize`, `disposition-check` 단계를 분리한다.
* object key는 raw bytes의 lowercase SHA-256이다. create-new 뒤 즉시 hash/size를 검증하며 기존 object와 byte가 다르면 fail-loud한다.
* reference manifest는 original relative path, round/attempt/phase, object SHA-256, size, media type, producer/version, chronology와 disposition을 보존한다.
* `.gitignore`의 `Iris/build/description/v2/*` default-deny 아래에서 durable object/reference root를 directory 단계별로 다시 열고, approved immutable object와 canonical reference manifest만 allowlist한다. Temporary materialization, logs, partial files와 ad-hoc staging reference는 계속 ignored한다.
* executable direct-path consumer는 공통 resolver를 통해 external materialized view를 받거나 immutable object를 직접 읽도록 먼저 이동한다. validation에 사용되는 exact legacy path를 silent fallback으로 찾지 않는다.
* Consumer coverage는 (1) Python AST/PowerShell parser/Lua require-string scan, (2) `rg` lexical fallback, (3) taxonomy와 command manifest가 열거한 current/historical/diagnostic/package entrypoint의 runtime file-open trace를 합친다. Machine-readable consumer manifest가 각 hit를 `executable_read`, `executable_write`, `docs_or_comment`, `reference_only`, `unresolved_dynamic`으로 분류하며, `unresolved_dynamic`은 migration blocker다.
* `attempt-0023`/`attempt-0024` current adoption inputs처럼 exact path/SHA로 보호된 파일은 consumer migration과 successor seal 전까지 physical payload로 유지한다.
* pilot은 duplicate group 하나에서 원본 tree restore를 검증한 뒤 attempt 단위로 확대한다. 한 번에 closure 전체를 치환하지 않는다.
* repository-available CAS에는 clean-checkout historical reproduction에 필요한 unique object만 둔다. transient/diagnostic copy는 external result root 또는 Change 5 cold archive disposition으로 보낸다.
* symbolic link/hard link는 Windows checkout portability와 Git semantics가 달라 기본 representation으로 사용하지 않는다.

Validation:

* `old attempt path -> old SHA -> CAS object -> restored path -> same SHA` 전수 검증
* attempt/phase chronology와 failed/superseded 상태 parity
* zero dangling reference, zero orphan retained object, zero duplicate object body
* direct-reader consumer manifest coverage와 legacy silent fallback 0
* every durable object/reference에 `git check-ignore` non-match, `git ls-files --error-unmatch` 성공, pre/post tracked-set census의 replacement inclusion
* clean checkout에서 reference가 가리키는 repository-available object가 실제 존재하고 raw SHA/size가 일치하며 external ambient object가 없어도 restore 가능
* selected naturalization/public-text/runtime-adoption tests exit 0
* current, historical, diagnostic, package, receipt-bound full-gate parity

---

### Change 4 — `2105_baseline_consumption_audit` normalization and staged rollout

Purpose:

198,171,920-byte audit tree를 canonical occurrence stream과 deterministic derived views로 바꾸고, 나머지 staging duplicate migration에 같은 CAS contract를 적용한다.

Files:

* `.gitignore`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/**`
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py`
* `consumer_universe_denominator_lock_common.py`
* `dvf_3_3_consumer_migration_normalization_common.py`
* `dvf_3_3_shared_disposition_consumption_common.py`
* `dvf_3_3_terminal_disposition_adjudication_common.py`
* `validate_dvf_3_3_shared_disposition_consumption.py`
* 해당 current/historical route tests와 CAS migration tests

Implementation Notes:

* `raw_occurrences.jsonl`을 canonical occurrence input으로 두고 반복되는 `path`, `context`, `referent`, `evidence_anchor`를 dictionary/node identity로 정규화한다.
* `classified_ledger`, `consumption_inventory`, `surface_inventory`, `referent_map`, `consumer_type_map`, CSV/Markdown views의 authority role과 consumer를 각각 기록한다. byte-identical하다는 이유만으로 role을 합치지 않는다.
* 현재 direct readers는 physical `AUDIT_ROOT` 상수 대신 resolver/materializer contract를 사용한다. line count, row ordering, accepted/change-required predicate와 hash-bound anchors는 바꾸지 않는다.
* derived view는 external run root에서 deterministic하게 materialize하고, required historical view만 CAS/reference로 보존한다.
* `classified_ledger.jsonl`과 `consumption_inventory.jsonl`의 byte identity는 한 canonical object와 두 logical references로 표현한다.
* `2105` migration receipt가 닫힌 뒤 같은 방식으로 staging duplicate groups를 value/risk 순으로 진행한다. 각 round는 독립 migration manifest와 rollback boundary를 가진다.
* Post-CAS `rg`와 Python backend는 모두 resolver가 external run root에 복원한 동일한 sealed legacy audit view를 scan한다. Production denominator scan은 repository evidence/CAS object/reference roots를 명시적으로 제외해 evidence가 자기 자신을 consumer로 세는 것을 막고, 두 backend의 argv/root/include/exclude와 restored-view SHA를 receipt에 기록한다.
* 최종 staging closeout은 Change 0에서 봉인한 현재 census의 443 duplicate groups / 39 rounds / 481,097,523-byte working-tree upper bound를 denominator로 삼고 모든 group을 `migrated`, `required_physical_exception`, `not_byte_identical` 중 하나로 분류한다. Tracked subpopulation은 307 groups / 27 rounds / 137,168,441 bytes다. 실행 중 생성된 successor object/reference는 이 denominator에 추가하지 않고 별도 post-migration population으로 보고한다.
* 입력 로드맵의 472.71 MiB는 이전 readpoint의 staging working-tree regular-file population에 `size * (count - 1)`을 적용한 raw duplicate-saving estimate이며 현재 실행 수치가 아니다. `2105` 125.75 MiB는 198,171,920-byte audit tree를 canonical occurrence/object + logical references + derived-on-demand view로 바꾼다는 proposal candidate이지만 sealed post-representation component sum이 없다. 실행 전 `2105_normalization_candidate_manifest.json`에 source paths, pre/post component bytes와 formula, overlap set, generator identity를 생성해 봉인하며, 이 manifest가 없으면 125.75 MiB를 claim하지 않는다.

Validation:

* 모든 original audit view의 raw SHA-256/row count/ordering reconstruction parity
* current execution authority로 선언된 `classified_ledger.jsonl` consumer 결과 parity
* direct consumer tests와 denominator/terminal disposition routes exit 0
* 동일 reconstructed legacy view에 대한 `rg`/Python scan backend denominator parity와 fallback fail-loud 유지
* sealed 443-group denominator에 미분류 group 0; tracked/working-tree population과 proposal estimate를 분리
* staging object/group마다 focused restore, round마다 current+historical checkpoint, Change 4 종료 시 receipt-bound full-gate Run A/B와 deterministic compare
* migration 전후 tracked bytes, working-tree bytes, ignored bytes, unique object bytes를 별도 기록

---

### Change 5 — Cold archive externalization

Purpose:

현재 ignored `Iris/_archive` 74,806,195 bytes를 checkout 밖의 compressed, hash-verified cold archive로 옮기고 repository에는 작은 restore manifest만 남긴다.

Files:

* `Iris/_archive/**`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* `Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tools/validate_layer4_absorption_current_surface_guard.py`
* new cold-archive manifest/receipt under successor evidence root

Implementation Notes:

* 기존 archive/verify/restore/delete prerequisite flow를 확장해 `_archive` exact selection을 받는다. 새 parallel delete mechanism을 만들지 않는다.
* 가장 큰 세 JSONL 70,529,421 bytes를 포함해 selection의 original path/hash/size/schema/role을 manifest에 기록한다.
* external archive 형식은 Python `zipfile`의 ZIP/Deflate level 9로 고정하고 Python/zlib producer version을 environment receipt에 결속한다. Selection은 regular file만 포함하며 directory entry는 쓰지 않는다. Member name은 repository-relative POSIX path이고 Unicode code-point lexical order로 기록하며 timestamp는 `1980-01-01T00:00:00`, `create_system=3`, `external_attr=(0o100644 << 16)`를 사용한다. UTF-8 filename flag는 Python `zipfile`이 non-ASCII member name에 자동 설정하는 값만 허용하고 ASCII name에 강제하지 않는다. Data descriptor, extra field, per-member/global comment는 비운다. Embedded canonical operation manifest도 한 member로 포함하고 동일 producer identity/input의 archive raw SHA가 재현되어야 한다.
* repository manifest는 backend kind, opaque store identifier, archive raw SHA/bytes, format profile/version, embedded-manifest SHA를 기록하되 machine absolute path는 기록하지 않는다.
* archive copy, archive verify, clean external restore, restored byte parity, owner delete approval 순서가 모두 닫힌 뒤에만 local `_archive` payload를 제거한다.
* external store의 지속성/접근성이 승인되지 않으면 Change 5는 `blocked` 또는 명시적 `deferred`로 남기고 local payload를 보존하며, 어느 경우든 이 계획의 overall closeout은 `partial`이다.
* `Iris/output/`과 `historical_reproduction_corpus.zip`은 이 change에 편승해 삭제하지 않는다.

Validation:

* every selected member의 archive/restore raw SHA-256 parity
* 동일 Python/zlib producer identity와 같은 selection을 두 external root에서 archive했을 때 ZIP raw bytes/SHA, member ordering, normalized metadata가 동일; 다른 producer identity 간 raw SHA portability는 claim하지 않음
* missing/corrupt archive, wrong store identity, path traversal, duplicate member, partial restore fail-loud tests
* restored historical validation route와 guard 결과 parity
* local delete 뒤 repository manifest에서 dangling reference 0
* 최소 약 65.5 MiB라는 예상 절감량은 physical receipt로만 확정

---

### Change 6 — Remaining runtime eager-load reduction

Purpose:

Repository/evidence closeout 뒤 `OnGameBoot`에서 실제 사용 전 필요하지 않은 static data/module registration을 first-use로 이동한다.

Files:

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
* 필요할 때만 `Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/build/description/v2/tests/test_phase5_iris_main_function_specs_contract.py`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* IrisMain/Browser/lazy lookup contract tests와 Lua harness

Implementation Notes:

* Runtime mutation 전 focused diagnostic의 current known baseline을 봉인한다. 현재 source에는 `buildBrowserData` helper/`invoke`가 없고 BrowserData는 `ready`만 가진 registration-only spec이며, `INIT_MODULES`의 `loadModule` 기대 목록은 11개다. Stale diagnostic에서 helper 존재와 `invoke = buildBrowserData` 기대를 제거하고 registration-only assertion으로 교정하되 source를 되돌리지 않으며, test/source/successor adoption identity를 함께 봉인한다.
* 우선 `INIT_MODULES`에서 `Iris/Data/IrisRecipeIndex`, `Iris/Data/IrisMoveablesIndex`, `Iris/Data/IrisFixingIndex`, `Iris/Data/IrisClassifications`의 boot require를 제거한다. 이후 exact expected `loadModule` 목록은 순서대로 `Iris/IrisAPI`, `Iris/UI/Tooltip/IrisAltTooltip`, `Iris/Compat/IrisContextMenuTextureCompat`, `Iris/Compat/IrisBulletReloadCompat`, `Iris/UI/Wiki/IrisContextMenu`, `Iris/UI/Browser/IrisBrowserData`, `Iris/UI/Browser/IrisMapIcon` 7개다. `IrisAPI.Tags`와 `IrisAPI.Index`는 이미 `StaticData.get()`을 통해 first-use load한다.
* `IrisBrowserData` boot registration은 현재 full `getAllItems()` scan을 하지 않지만 여러 Browser dependency를 require한다. before/after module/heap evidence가 있을 때만 `IrisBrowser.lua`의 existing lazy `safeRequire` 경계로 완전히 이동한다.
* BrowserData registration도 제거할 evidence가 승인되면 위 목록에서 `Iris/UI/Browser/IrisBrowserData`만 빠진 6개가 된다. 이 optional step은 별도 focused receipt와 first Browser call proof 없이는 수행하지 않는다.
* tooltip hook, context-menu compat/hook, bullet reload compat, map icon init과 public `IrisAPI` assignment 순서는 보존한다.
* `StaticData`의 failure cache와 dev/test reset semantics를 유지한다. First-use failure는 boot `runModuleSpec` 실패와 같은 reason-code family로 error/warn log에 한 번 이상 보이고 caller에 failure를 반환해야 한다. Tick별 retry나 silent fallback을 추가하지 않으며 fault-injection test로 one-shot visibility와 cached failure를 검증한다.
* source 기준 약 191.9~200 KiB eager parsing 감소는 후보 수치다. 실제 성능 claim은 Kahlua/PZ 측정으로만 승인한다.
* Layer3/UseCase chunk files, routers, indices와 direct full-materialization facades는 수정하지 않는다.

Validation:

* focused exact command: `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p 'test_phase5_iris_main_function_specs_contract.py'`; current known 4 tests / 1 stale-spec failure를 수정한 뒤 exit `0`
* taxonomy diagnostic exact command: `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic --taxonomy Iris/_docs/round3/round3_test_taxonomy.json --required-validations Iris/_docs/round3/current_route_required_validations.json`; raw exit `0`
* test expectation drift는 `stale_test_corrected`, `preserved_contract`, `intentional_successor_change` 중 하나로 disposition하고 test/source/adoption identity를 결속한다. Raw failure를 adapter로 PASS 처리하지 않는다.
* boot require/module counter: target static data 0, Browser full scan 0
* first Tags/Index/Alt Tooltip/Browser call 뒤 필요한 module만 한 번 load
* missing/corrupt static module fault injection에서 first-use caller failure, same-family reason code, warn/error visibility 1회 이상, silent fallback 0, cached retry storm 0
* first Alt Tooltip와 first Browser latency, boot parsing/memory before/after raw sample
* Layer3 single lookup 최대 1/11, UseCase single lookup 최대 1/9, tooltip line-count description chunk 0, compatibility fallback 0 유지
* Browser same-generation warm reopen scan 증가 0
* public output, tooltip 최대 4줄, Browser/Wiki/detail/localization parity
* Lua syntax와 standalone harness exit 0, manual PZ smoke 완료

---

### Change 7 — Compatibility/allocation evidence and bounded closeout

Purpose:

남은 compatibility/full-materialization 및 allocation candidate를 증거에 따라 `adopt`, `defer`, `separate successor required` 중 하나로 disposition하고 전체 계획의 측정 경계를 봉인한다.

Files:

* `IrisLayer3DataChunks.lua`
* `IrisUseCaseDescriptions.lua`
* `IrisData.lua`
* `UseCaseDescriptions/LineCountIndex.lua`
* `IrisUseCaseDescriptionsLookup.lua`
* `IrisBrowserData.lua`, `IrisBrowserQuery.lua`, `IrisBrowserVariantIndex.lua`
* successor evidence root의 consumer census, heap/allocation sample, final inventory, closeout receipt

Implementation Notes:

* repository/internal direct require와 알려진 external mod consumer evidence를 분리한다.
* Layer3/UseCase direct facade는 full table/global/`_requirementsLookup` 계약을 유지하는 것이 기본 disposition이다.
* `IrisData.lua`는 1,360 classification key와 global compatibility surface를 소비자 조사 없이 canonical view로 바꾸지 않는다. 현재 `ItemGroups` fallback의 실제 consumer/result도 별도로 확인한다.
* `LineCountIndex.lua` 63,166 bytes는 description chunk 0-load lookup을 유지하는 대안이 측정으로 우세할 때만 별도 successor plan을 연다.
* Browser search-string/location/category/display-name/variant/cache-copy와 tooltip cache는 raw heap/allocation sample 없이 변경하지 않는다.
* 최종 measurement report는 tracked repository bytes, working-tree physical bytes, ignored/untracked bytes, unique content bytes, runtime Lua bytes, runtime memory/allocation을 분리한다.
* compatibility 변경을 하지 않는 `deferred` disposition도 이 계획의 유효한 complete 결과다. 실제 public facade 변경은 별도 owner-approved plan을 요구한다.

Validation:

* consumer census가 path, require form, expected shape, internal/external provenance를 기록
* before/after physical inventory와 object/reference counts
* 서로 중첩되는 절감 후보를 합산하지 않는 machine-checkable summary
* predecessor/successor receipt chain, current/historical/diagnostic/package/full-gate final PASS
* closeout validation matrix는 각 planned claim을 `validated`, `out_of_scope`, `unvalidated_but_in_scope` 중 하나로 분류하고 command/receipt/evidence identity 또는 이유를 기록
* closeout docs는 실제 adoption, deferred, blocked와 validation ceiling만 반영하며 `unvalidated_but_in_scope`가 있는 change를 complete로 쓰지 않음

---

## 7. Validation Plan

### Automated Validation

각 command는 exact relevant change가 적용된 clean/disposable subject에서 exit `0`일 때만 PASS로 기록한다.

* Change 0 phase validator: C0-a predecessor commit/tree·9-row final blob set·sealed residual identities, C0-b predecessor manifest reconstruction, C0-c policy/approval/taxonomy/required-validation/full-gate/adoption identity를 phase별로 재계산하고 receipt와 대조한다. Base+dirty delta 입력은 schema에서 거부한다.
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_artifact_lifecycle_*.py"`
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_repository_evidence_*.py"`
* `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --taxonomy Iris/_docs/round3/round3_test_taxonomy.json --required-validations Iris/_docs/round3/current_route_required_validations.json --enforce-current-build-closure`
* `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class historical --taxonomy Iris/_docs/round3/round3_test_taxonomy.json --required-validations Iris/_docs/round3/current_route_required_validations.json`
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p 'test_phase5_iris_main_function_specs_contract.py'`
* `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic --taxonomy Iris/_docs/round3/round3_test_taxonomy.json --required-validations Iris/_docs/round3/current_route_required_validations.json`
* Diagnostic route는 raw result와 approved disposition을 분리하고 raw failure를 PASS로 다시 쓰지 않는다. 현재 known baseline은 focused command 4 tests / 1 failure / exit `1`이므로 Change 6 착수 전 stale expectation correction과 focused/diagnostic exit `0`가 필수다.
* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
* `powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\test\validate_disposable_package.ps1`
* C0-a residual validation은 각 clean materialization마다 새 empty external evidence root를 발급하고 아래 exact preparation/invocation을 사용한다. `Closeout`이 실제 읽는 protected/supported baseline 두 파일만 raw-byte copy하며 `phase0_package_identity_baseline.json`은 복사하지 않는다. Copy 전 repository source identity와 copy 후 bytes/SHA를 §2 sealed table과 대조하고, report가 생기기 전 root가 두 baseline 파일 외에는 비어 있음을 확인한다.

```powershell
$repositoryRoot = [IO.Path]::GetFullPath((git rev-parse --show-toplevel).Trim()).TrimEnd([char[]]@('\', '/'))
$evidenceRoot = [IO.Path]::GetFullPath('<allocator-issued-empty-evidence-root>').TrimEnd([char[]]@('\', '/'))
Copy-Item -LiteralPath (Join-Path $repositoryRoot 'Iris/_docs/refactor/residual_refactor/phase0_protected_surface_manifest.json') -Destination (Join-Path $evidenceRoot 'phase0_protected_surface_manifest.json')
Copy-Item -LiteralPath (Join-Path $repositoryRoot 'Iris/_docs/refactor/residual_refactor/phase0_supported_api_manifest.json') -Destination (Join-Path $evidenceRoot 'phase0_supported_api_manifest.json')
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repositoryRoot 'Iris/test/validate_residual_refactor_surfaces.ps1') -Mode Closeout -RepositoryRoot $repositoryRoot -EvidenceRoot $evidenceRoot
```

* Exact expanded argv, normalized roots, source/copy SHA와 generated report SHA는 run-local external receipt에 기록한다. Windows native absolute path identity는 `GetFullPath` 후 trailing `\`/`/` 제거 및 ordinal-ignore-case로 비교한다. Repository에 채택하는 logical path는 `/` separator의 repository-relative form으로만 쓰고, external root는 opaque allocator ID와 receipt hash로 결속해 machine-specific absolute path를 successor evidence에 넣지 않는다. Exit `0`, fresh protected report의 baseline SHA `aaaecb90efb3bfd36b9b096aaa51b96b45800c1004ca912f75560c45b32b38c2`, baseline rows 26, authorized changed baseline rows 6, folded unique added rows 60, total report rows 86, unauthorized changed 0을 모두 만족해야 PASS다.
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1` Run A / Run B. 각 invocation은 exact `-RepositoryRoot`, sealed `-Commit`, `-ClaimId iris_repository_evidence_lightweighting`, environment receipt, 새 empty/non-nested work/result roots와 orchestration receipt를 기록한다.
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`. 동일 sealed commit/claim/environment와 Run A/B orchestration receipts를 exact parameter로 소비한다.
* lifecycle v1/v2 reconstruction, CAS restore, cold archive restore, zero-dangling-reference, deterministic compare tests
* `git check-ignore` non-match, `git ls-files --error-unmatch`, clean-checkout object existence/hash, pre/post tracked-set replacement inclusion
* 대상 path별 `git check-attr -a`, `git config --get core.autocrlf`, `.gitattributes` raw SHA와 checkout raw SHA/Git blob parity
* pre/post Git tracked set, ignored set, file bytes, SHA duplicate groups와 unique object bytes census

Validation command에 필요한 work/result root는 allocator가 새롭고 비어 있으며 상호 비포함인 외부 경로로 발급한다. repository-local output, reused root, ambient `PYTHONPATH`/`PYTEST_ADDOPTS`, Python bytecode 생성은 fail-loud한다.

Full-gate cadence는 비용과 결함 격리를 함께 고정한다.

1. C0-a: 두 independent clean materialization에서 9-row final blob set과 sealed two-file baseline을 사용한 HEAD-bound residual validation만 실행한다. Predecessor manifest는 아직 생성·요구·재구성하지 않는다.
2. C0-b: predecessor manifest를 생성·commit한 뒤 두 independent clean materialization에서 C0-a subject reconstruction과 physical/clean subject binding validation을 실행한다.
3. C0-c: focused + current + historical + receipt-bound full-gate Run A/B + deterministic compare를 실행한다.
4. CAS object 또는 duplicate group 단위: hash/restore/consumer focused tests만 실행한다.
5. 각 migration round 종료: current + historical route와 tracked/reference integrity checkpoint를 실행한다.
6. Change 2, Change 3, Change 4, Change 5 각각의 terminal successor adoption/disposition 직전: receipt-bound full-gate Run A/B와 deterministic compare를 실행한다.
7. Change 6 runtime mutation 전에는 직전 storage terminal full-gate receipt를 요구하고, Change 6 종료에는 focused diagnostic, full diagnostic, Lua/package/current/full-gate Run A/B와 deterministic compare를 다시 실행한다.
8. Change 7 closeout은 마지막 full-gate receipt들을 재사용하되 identity가 하나라도 drift했으면 전부 재실행한다. 모든 object마다 full gate를 실행하지 않는다.

### Manual Validation

Runtime Change 6에 한해 같은 Project Zomboid build, machine, save, mod set에서 다음을 before/after로 확인한다.

* game boot와 main-menu/game 진입 시 오류/log
* 첫 Alt Tooltip의 표시, 최대 4줄, first-use latency
* 첫 Browser/Wiki open, category/subcategory/item/detail navigation과 first-use latency
* 같은 generation의 Browser 재오픈과 반복 검색
* recipe/moveables/fixing 연결 정보와 localization
* compatibility facade를 직접 require하는 dev probe의 full-table/global shape
* 가능하면 Kahlua heap snapshot 또는 동일한 대체 memory instrumentation

### Validation Limits

Closeout validation matrix는 계획의 모든 claim/surface를 다음 세 상태 중 하나로만 기록한다.

* `validated`: exact command exit `0` 또는 명시된 manual evidence와 receipt identity가 있음
* `out_of_scope`: Non-Goals/Explicitly Out Of Scope에 포함되고 complete claim에 사용되지 않음
* `unvalidated_but_in_scope`: 계획 범위지만 환경/증거/승인 부족으로 검증되지 않음. 해당 change와 전체 상태를 `partial` 또는 `blocked`로 제한함

현재 예상 ceiling은 다음과 같다.

* multiplayer validation 없음 — `out_of_scope`
* long-session memory/GC validation 없음 — `out_of_scope`
* 전체 외부 mod compatibility sweep 없음 — `out_of_scope`
* release/Workshop deployment validation 없음 — `out_of_scope`
* external cold-store의 장기 운영 SLA — Change 5의 backend 지속성 승인을 받지 못하면 `unvalidated_but_in_scope`
* raw PZ/Kahlua timing 또는 heap sample — Change 6 성능 claim에 필요하며 없으면 `unvalidated_but_in_scope`; functional repository change만 complete 가능
* Git history packfile 크기 감소 — 별도 rewrite 없이는 `out_of_scope`
* `Iris/output/`과 historical reproduction ZIP disposition — `out_of_scope`

---

## 8. Risk Surface Touch

### Authority Surface

영향 있음. Change 0이 predecessor subject와 successor policy/current-route adoption을 먼저 봉인한다. 이후 lifecycle manifest representation, historical staging reference, `2105` current execution inputs와 archive reference가 대상이다. Payload 위치/형식은 바뀔 수 있지만 source/runtime authority와 historical identity는 바뀌지 않는다.

### Runtime Behavior Surface

Change 0~5에는 의도된 영향이 없다. Change 6에서 boot module timing, first-use timing과 실패 발생 시점이 바뀌지만 API 결과, 사용자 표시 결과와 failure visibility는 유지한다.

### Compatibility Surface

Change 6의 boot ordering에 영향 가능성이 있다. Full-materialization facade, `IrisData` global, `LineCountIndex`는 Change 7에서 evidence만 수집하며 별도 승인 없이 변경하지 않는다.

### Sealed Artifact Surface

영향 있음. 기존 lifecycle v1 manifest, protected-surface/checkpoint manifest, attempt payload와 historical archive가 seal/reference chain에 포함된다. 기존 sealed artifact는 수정하지 않고 successor relation과 restore proof를 추가한다.

### Public-Facing Output Surface

의도된 변경 없음. Tooltip/Wiki/Browser 문구, 분류, ordering, 최대 4줄, public Lua return shape를 보존한다.

---

## 9. Risk Analysis

### Architecture Risk

* predecessor subject, successor policy 또는 required-validation identity 중 하나가 drift하면 서로 다른 실행을 같은 successor claim으로 오인할 수 있다.
* C0-a/C0-b/C0-c commit 순서가 생략되거나 validation receipt가 다른 HEAD를 가리키면 dirty state를 sealed state로 오인할 수 있다.
* C0-a가 C0-b에서만 생성되는 predecessor manifest를 요구하면 phase graph가 순환한다. C0-a는 commit/tree·9-row set·sealed baseline만 검증하고 manifest 생성/재구성은 C0-b로 제한한다.
* 현재 protected baseline과 불일치하는 과거 final report를 authority로 쓰거나 C0-a HEAD에서 baseline을 재생성하면 stale-reference 또는 before=after tautology가 승인될 수 있다. Exact two-file baseline identity와 fresh external report binding을 강제한다.
* 6개 drift를 delta 이름만으로 승인하면 다른 blob/line-ending representation이 숨어들 수 있다. Path별 effective source, expected Git blob, LF SHA를 모두 비교하고 불일치 row는 `requires_new_successor_delta`로 fail-closed한다.
* CAS/reference layer가 historical evidence의 새 hidden authority가 될 위험이 있다. Object는 raw-byte storage이고 authority는 기존 role/receipt chain이라는 점을 schema와 docs에 고정한다.
* 기존 `repository_runtime_lightweighting` scope와 후속 claim을 섞으면 predecessor receipt를 소급 변경할 수 있다. 별도 policy/evidence root/successor schema를 사용한다.
* repository-available object와 external cold object의 경계가 흐려지면 clean checkout reproduction이 외부 상태에 암묵적으로 의존할 수 있다.
* `.gitignore` allowlist가 불완전하면 tracked payload를 ignored CAS로 치환하는 tracking loss를 deduplication으로 오인할 수 있다.

### Runtime Risk

* boot preload 제거는 첫 Tooltip/Browser/API 호출 latency를 이동시킨다.
* `IrisBrowserData` module registration까지 지연하면 context-menu 또는 map-icon 초기화 순서에서 누락된 dependency가 드러날 수 있다.
* StaticData failure cache 때문에 first-use 시 일시적 dependency failure가 session 전체에 고정될 수 있고 boot-time log보다 발견이 늦어질 수 있으므로 reason-code/log/caller visibility를 명시적으로 검증한다.

### Compatibility Risk

* direct historical file readers는 reference JSON을 원래 payload로 오인할 수 있다.
* external mods가 full-materialization facade나 `IrisData` global을 직접 사용할 수 있다.
* PowerShell/Windows path, LF/CRLF, Unicode JSONL 차이가 hash/reconstruction parity를 깨뜨릴 수 있다.

### Regression Risk

* v2 delta에서 remove/replace ordering이나 node dictionary collision이 final state를 잘못 복원할 수 있다.
* `2105` derived view normalization이 row order, line count, accepted predicate를 바꿀 수 있다.
* archive deletion 전에 manifest/store binding이 틀리면 historical payload를 복구할 수 없다.
* local residue cleanup 수치를 tracked/CAS 절감량과 중복 보고할 수 있다.
* stale diagnostic expectation을 source contract로 오인하거나 raw diagnostic failure를 disposition adapter로 숨기면 Change 6 regression이 검출되지 않을 수 있다.

---

## 10. Rollback Plan

Change 0은 storage/runtime payload migration을 하지 않지만 predecessor 및 governance/validation 파일을 commit한다. Rollback은 `git reset`이나 history 삭제를 사용하지 않는다.

* C0-a residual validation이 실패하거나 sealed baseline/report identity가 다르면 그 commit을 predecessor authority로 채택하지 않는다. 6개 drift 중 authorization chain/blob/LF가 어긋난 row는 `requires_new_successor_delta`로 기록하고, baseline/report를 재생성하거나 과거 stale report를 rewrite하지 않는다. 기본 처리는 branch/commit을 inactive evidence로 보존하고 후속 phase를 중단하는 것이다. 이미 통합된 경우에만 owner 승인 아래 additive revert commit으로 pre-C0-a tree를 복원한다.
* C0-b predecessor manifest reconstruction이 실패하면 manifest commit을 inactive로 두고 C0-c를 시작하지 않는다. 원본 predecessor commit은 자동으로 되돌리지 않는다.
* C0-c focused/current/historical/full-gate가 실패하면 taxonomy, required-validations, conditional full-gate contract, launchers, policy/approval/adoption changes는 미채택 상태다. Branch가 아직 통합되지 않았으면 그대로 inactive로 보존하고, 이미 통합됐다면 pre-C0-c exact blobs를 복원하는 additive rollback commit을 만든다.

Change 1은 `.pyc`를 다시 보존하지 않는다. 필요하면 Python이 external cache에 재생성한다. Package projection은 current source에서 external root로 재생성한다.

Change 2는 v1 writer/reader를 transition 동안 유지한다. v2 validation이 실패하면 v2 artifacts와 successor adoption만 폐기하고 기존 `artifact_role_manifest.jsonl`, `final_artifact_role_manifest.jsonl` identity로 돌아간다. v1 pair를 disposition한 뒤의 rollback은 v2 codec이 external root에 exact v1 bytes를 복원하고 hash를 확인한 다음 original paths에 atomic하게 재승격한다.

Change 3~4는 각 migration batch에서 original payload를 delete-eligible로 바꾸기 전에 tracked CAS/reference inclusion과 clean-checkout restore rehearsal을 완료한다. 실패하면 reference adoption을 취소하고 CAS object에서 original attempt tree/view를 byte-identical하게 복원한다. Ignored/untracked object에만 의존한 batch는 promotion 자체를 무효로 하며 partial batch를 다음 batch와 섞지 않는다.

Change 5는 external archive와 restore receipt가 모두 PASS하기 전 local `_archive`를 유지한다. 삭제 후 failure가 발견되면 archive의 embedded manifest로 original relative paths에 복원하고 전수 SHA를 다시 검증한다.

Change 6은 제거한 `INIT_MODULES` entries를 복구한다. First-use latency, missing module, failure visibility, public-output parity 문제가 하나라도 재현되면 해당 module만 기존 boot require로 되돌리고 runtime checkpoint를 `partial`로 남긴다. Diagnostic test expectation은 source rollback과 같은 commit에서 predecessor expectation으로 되돌려 test/source identity가 갈라지지 않게 한다.

Change 7의 compatibility surface는 기본적으로 변경하지 않는다. 별도 successor가 승인되어 변경한 경우에만 legacy facade/file을 복구하는 독립 rollback을 사용한다.

Rollback은 기존 receipt, failed attempt, migration journal을 삭제하거나 성공으로 다시 쓰지 않는다. 새 rollback receipt가 predecessor/successor identity와 복원 결과를 append-only로 기록한다.

---

## 11. Governance Constraints

* `docs/Philosophy.md` 준수
* Iris는 Pulse만 의존할 수 있으며 다른 Pulse submod를 참조하지 않음
* Iris runtime은 100% Lua를 유지하고 storage/build migration Python을 runtime에 포함하지 않음
* runtime/build-time separation 유지
* current source/rendered/runtime authority와 storage representation 분리
* 기존 sealed artifact/decision은 수정하지 않고 additive successor 사용
* predecessor adoption은 committed C0-a commit/tree만 허용하고 base+dirty-delta/hash-only fallback 금지
* C0-a는 predecessor manifest를 생성·요구하지 않고 sealed residual baseline 두 파일과 9-row set만 검증; predecessor manifest 생성·commit·reconstruction은 C0-b에만 허용
* residual baseline authority는 pre-C0-a commit `c8b96e40251b9043bae04261a8acd033660e0d45`의 exact protected/supported bytes이며 C0-a HEAD에서 재생성 금지
* stale protected final report는 `stale_report_reference`로만 보존하고 authority 또는 expected output으로 사용 금지; 6-row drift는 path/blob/LF/effective authorization source를 모두 검증
* successor policy, owner approval, taxonomy, required-validation, full-gate adoption을 exact identity로 봉인하며 focused test PASS만으로 current adoption 주장 금지
* owner approval 없는 repository-local CAS promotion, external cold-store adoption, payload deletion 금지
* durable repository CAS object/reference는 approved `.gitignore` allowlist와 tracked clean-checkout availability를 가져야 하며 ignored replacement를 절감으로 보고하지 않음
* tracked/ignored 상태가 아니라 role, consumer, hash, restore proof로 disposition 결정
* current authority와 historical reproduction input 삭제 금지
* dangling reference, orphan retained object, unclassified artifact는 fail-loud
* 이 계획이 신규 생성하는 successor evidence에 machine-specific external absolute payload path 기록 금지. Immutable predecessor evidence를 이 규칙 때문에 소급 수정하지 않음
* public/compatibility surface는 consumer proof 없이 제거하지 않음
* Layer3/UseCase demand-load architecture와 compatibility full-table contract 분리
* 해석, 권장, 비교를 runtime/public output에 추가하지 않음
* 서로 다른 byte denominator와 중첩 절감량을 합산하지 않음
* exact relevant validation command exit `0`이 아니면 PASS claim 금지
* raw diagnostic failure를 approved/deferred disposition만으로 PASS로 변환하지 않음
* manual PZ evidence가 없으면 runtime performance/complete claim 금지

---

## 12. Expected Closeout State

현재 계획 상태는 `PREDECESSOR_UNSEALED`다. C0-a~C0-c가 predecessor/successor/current-route identity를 commit하고 모든 필수 검증을 통과하면 Change 1~7을 순서대로 실행한다. 목표 closeout은 `complete`다.

`complete`는 다음 bounded state를 의미한다.

* local `.pyc`/package residue가 제거되고 repository 안에 재생성되지 않는다.
* predecessor subject, successor policy/owner approval, taxonomy/required-validation/full-gate/adoption receipt가 하나의 execution identity로 봉인된다.
* lifecycle v2가 v1 baseline/final을 exact reconstruction하며 v1 full-pair의 current checkout 상시 보존을 대체한다.
* 봉인된 443-group/39-round staging census의 모든 group이 CAS로 이동하거나 exact consumer/authority에 결속된 `required_physical_exception`/`not_byte_identical`로 봉인되고, migrated payload는 SHA당 한 번만 저장되며 attempt chronology/reference/restore가 유지된다.
* `2105` canonical/derived view가 기존 consumer 결과를 보존한다.
* 승인된 `_archive` selection이 external cold archive에서 복구 가능하다.
* boot static-data eager require가 줄고 first-use/public behavior가 보존된다.
* compatibility/allocation 후보는 증거에 따라 명시적으로 deferred 또는 별도 successor 대상으로 disposition된다.
* current/historical/diagnostic/package/Lua/purity와 receipt-bound Run A/B/deterministic compare가 요구된 범위에서 exit `0`이며 CAS/reference는 clean checkout에서 tracked/available하다.
* `complete`를 주장할 때 validation matrix의 모든 in-scope claim은 `validated`다. `unvalidated_but_in_scope`가 하나라도 있으면 전체 상태는 `partial` 또는 `blocked`이고, `out_of_scope` 항목은 complete claim에 사용되지 않는다.
* 최종 보고는 tracked, working-tree, ignored, unique content, runtime Lua, runtime memory를 분리하고 중복 절감량을 합산하지 않는다.

외부 cold-store 지속성/owner deletion approval이 없으면 Change 5는 `blocked`로 두고 전체 상태를 `partial`로 닫는다. 그 이유는 cold archive externalization이 이 계획이 약속한 4대 storage outcome 중 하나라서 local `_archive` payload 보존 상태로는 해당 in-scope outcome이 검증되지 않기 때문이다. Manual Project Zomboid runtime evidence가 없으면 repository/evidence track은 완료할 수 있지만 Runtime Change 6은 `implemented_only`이고 전체 상태는 `partial`이다. 반면 compatibility facade를 변경하지 않고 `deferred`로 결론내는 것은 Change 7이 애초에 adoption이 아니라 evidence-based disposition을 완료 조건으로 정의했기 때문에 `complete`를 막지 않는다.

이 계획의 완료는 모든 historical artifact 삭제, 모든 compatibility facade 제거, runtime heap 최적화, release/Workshop readiness를 의미하지 않는다. 허용되는 최종 claim은 다음으로 제한한다.

**Iris의 repository evidence와 intermediate artifact 물리 중복을 줄이면서 authority/reference/restore chain과 공개 동작을 보존하고, 남은 boot eager-load를 측정된 compatibility boundary 안에서 축소했다.**
