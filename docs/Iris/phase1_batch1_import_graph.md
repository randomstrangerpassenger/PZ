# Phase 1 — batch1 Library Import Graph

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 1 / Change 2.
> 측정일: 2026-06-07 (repo root cwd).
> 대상 모듈: `Iris/build/description/v2/tools/build/build_identity_fallback_batch1_clothing_surface_reuse.py`
> 관련 metric: `baseline_batch1_import_count = 22` (Phase 2 closeout 목표 `== 0`).

## 요약

`build_identity_fallback_batch1_clothing_surface_reuse.py`는 batch1 전용 빌드 스크립트이면서
동시에 다른 batch/bucket/phase 스크립트들이 공통 I/O·유틸을 끌어다 쓰는 **사실상의 공유 라이브러리**로
소비되고 있다(계획이 지적한 anti-pattern). Phase 2는 이 공통 심볼을
`Iris/build/tools/common/` 계열 helper로 이전한 뒤 batch1을 다른 batch와 동등한 sibling으로 강등한다.

- caller 파일 수: **20**
- import 라인 수: **22** (`baseline_batch1_import_count`와 일치. batch1 파일 자기 참조 0건)
- import 형태: `from tools.build.build_identity_fallback_batch1_clothing_surface_reuse import ...`
- 모듈 경로 표기: 모두 `tools.build....` dotted path (direct script execution 시 sys.path bootstrap 의존 — conflict 14.2 / Phase 3 연계)

## 가장 많이 재사용되는 심볼 (단일 라인 import 기준)

| 심볼 | 성격 | Phase 2 이전 대상 |
|---|---|---|
| `load_json` | JSON 입력 helper | → common I/O helper |
| `write_json` | JSON 출력 helper | → common I/O helper |
| `normalize_counter` | 카운터 정규화 유틸 | → common 유틸 helper |
| `main` (as `build_batch1_preview`) | batch1 preview 진입점 | batch1 고유 — 이전 아님, caller가 sibling 호출로 유지 |

multi-line `import (` 블록(아래 표의 해당 라인)은 위 심볼의 상위집합을 가져오며, 정확한 심볼 목록은
Phase 2 진입 시 각 블록을 펼쳐 확정한다.

## Caller Inventory (22 import 라인 / 20 파일)

모든 경로는 `Iris/build/description/v2/tools/build/` 하위. 라인 번호는 2026-06-07 기준.

| # | Caller 파일 | 라인 | import 형태 |
|---|---|---:|---|
| 1 | `build_identity_fallback_batch2_accessory_headgear_reuse.py` | 15 | `import (` (multi) |
| 2 | `build_identity_fallback_batch3_food_storage_reference_reuse.py` | 14 | `import (` (multi) |
| 3 | `build_identity_fallback_batch4_medical_kitchen_explosive_reuse.py` | 13 | `import (` (multi) |
| 4 | `build_identity_fallback_batch5_residual_taxonomy.py` | 12 | `import load_json, write_json` |
| 5 | `build_identity_fallback_batch5a_electronics_partial_reuse.py` | 13 | `import (` (multi) |
| 6 | `build_identity_fallback_batch6_residual_family_split_taxonomy.py` | 11 | `import load_json, write_json` |
| 7 | `build_identity_fallback_batch7_adhesive_repair_supply.py` | 14 | `import (` (multi) |
| 8 | `build_identity_fallback_batch7_authority_promotion.py` | 17 | `import (` (multi) |
| 9 | `build_identity_fallback_batch8_solid_fuel_material.py` | 14 | `import (` (multi) |
| 10 | `build_identity_fallback_batch8_authority_promotion.py` | 17 | `import (` (multi) |
| 11 | `build_identity_fallback_batch9_metalworking_consumable_supply.py` | 14 | `import (` (multi) |
| 12 | `build_identity_fallback_batch9_authority_promotion.py` | 17 | `import (` (multi) |
| 13 | `build_identity_fallback_batch1_authority_promotion.py` | 19 | `import (` (multi) |
| 14 | `build_identity_fallback_batch1_authority_promotion.py` | 35 | `import main as build_batch1_preview` |
| 15 | `build_identity_fallback_bucket1_crowbar_reuse.py` | 13 | `import (` (multi) |
| 16 | `build_identity_fallback_bucket1_crowbar_authority_promotion.py` | 17 | `import (` (multi) |
| 17 | `build_identity_fallback_bucket1_wrench_reuse.py` | 13 | `import (` (multi) |
| 18 | `build_identity_fallback_bucket1_wrench_authority_promotion.py` | 17 | `import (` (multi) |
| 19 | `build_identity_fallback_bucket1_residual_taxonomy.py` | 11 | `import load_json, write_json` |
| 20 | `build_identity_fallback_phase3_residual_taxonomy_manifest.py` | 12 | `import load_json, normalize_counter, write_json` |
| 21 | `build_identity_fallback_phase6_executable_subset_rollout.py` | 16 | `import (` (multi) |
| 22 | `build_identity_fallback_phase6_executable_subset_rollout.py` | 32 | `import (` (multi) |

> 2개 파일이 import 라인을 2개씩 보유: `build_identity_fallback_batch1_authority_promotion.py`(19, 35),
> `build_identity_fallback_phase6_executable_subset_rollout.py`(16, 32). 따라서 distinct caller 파일 = 20, import 라인 = 22.

## Phase 2 함의

- 위 22개 라인 전부가 common helper import로 전환되거나 caller가 sibling 호출로 바뀌면
  `batch1_import_count == 0`(Phase 2 closeout 정량 기준)에 도달한다.
- `main as build_batch1_preview`(라인 35)는 batch1 고유 진입점 호출이므로 helper 이전 대상이 아니라
  batch1을 sibling으로 강등한 뒤에도 sibling-to-sibling 호출로 남을 수 있다. Phase 2 진입 시
  이 라인의 처리 방식(공통화 vs 유지)을 명시한다.
- 측정 명령: `$dvPy | Select-String -Pattern 'build_identity_fallback_batch1_clothing_surface_reuse' | Measure-Object`
  (`$dvPy`는 `phase1_baseline_metrics.md` 공통 정의 참조).
