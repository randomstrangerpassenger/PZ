# Phase 1 — Inventory Readpoint

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 1.
> 측정일: 2026-06-07 (repo root cwd: `C:\Users\MW\Downloads\coding\PZ\`).
> 상태: SEALED. 본 readpoint가 Change 2~10의 분모(active/legacy/tracked 경계)를 봉인한다.

이 문서는 Phase 1이 재측정한 **active source / generated output / staging evidence / package copy /
compatibility wrapper / build script disposition**의 단일 읽기점이다. 세부 산출물은 아래로 링크된다.

## Deliverable 링크

| 산출물 | 내용 |
|---|---|
| `phase1_baseline_metrics.md` | 13개 정량 baseline (SEALED) |
| `phase1_active_script_manifest.txt` | active build/generation 스크립트 38개 (active 한정 측정 단일 입력) |
| `phase1_batch1_import_graph.md` | batch1 라이브러리 import graph (20 caller / 22 line) |
| `phase1_pulse_wrapper_usage_inventory.md` | Pulse compat wrapper 6개 사용 인벤토리 |
| `phase1_artifact_source_classification.md` | runtime sealed / output / package 분류 + SHA baseline |
| `phase1_conflict_resolution_gate.md` | roadmap §14.1~§14.6 게이트 (6/6 schema 충족) |

## 1. Path / Chunk 검증 (Step 0)

- §5 Path Existence: **21/21 `Exists = True`** (runtime Lua 5 + Pulse wrapper 6 + build entrypoint 3 + inventory doc 3 + sealed entrypoint 4).
- 추가 sealed artifact 존재: **16/16** (§5 Generated Artifacts 목록).
- chunk: Layer3 = **11** (`baseline_layer3_chunk_count`), UseCase = **9** (`baseline_usecase_chunk_count`).

## 2. Build Script Disposition (4-classification)

분류 기준: 프로젝트가 git-tracked로 유지하는지(= 유지 의도) + 역할(생성 파이프라인 / 검증 / 1회성 라운드).

### 2.1 `Iris/build` tracked Python 73개 분해 (전수 정합)

| 분류 | count | 구성 |
|---|---:|---|
| **active** (build/generation) | **38** | root entrypoint 7(`main`,`description_generator`,`convert_descriptions_to_lua`,`convert_labelmap_to_lua`,`quality_gates`,`recipe_evidence_pipeline`,`rightclick_evidence_pipeline`) + `tools/pipeline` 13 + `tools/common` 3 + dv build core 12 + dv tools 3(`postproc_ko`,validator 2) |
| **active-validation** (tests) | 16 | root `tests/` 9 + `description/v2/tests/` 6 + `test_require_render.py` 1 |
| **legacy_archive** | 15 | `tools/oneshots/` (ENTRYPOINTS.md: "not part of the active build contract") |
| **reproduction_evidence** (tracked) | 4 | `staging/compose_contract_migration/<round>/generate_round_artifacts.py` ×4 |
| 합계 | **73** | (38+16+15+4) |

### 2.2 `Iris/build/description/v2/tools/build/` 281개 (`baseline_build_script_count`)

| 분류 | count | 비고 |
|---|---:|---|
| **active** (tracked core) | 12 | index generator 3(`build_iris_{recipe,moveables,fixing}_index_data`) + guard/recovery round 2 + compose core 7(`compose_layer3_*`) |
| **reproduction_evidence** (untracked, gitignored) | 269 | `INVENTORY.md`: 전수 "reproduce-required". filename-glob archive/delete 금지(conflict 14.3) |

> 269개 중 Phase 7a **consolidation 후보 family**(단순 설정 차이 sibling): `identity_fallback batch{2..9}`,
> `source_coverage {b1..b4,c1a..c1e}`, `post_cleanup phase3_pkg3{a..j}`, `role_fallback_hollow`,
> `freeze_quality_baseline_v{1..4}`, `report_*_{draft,final}`. 실제 통합 여부는 Phase 7a가
> grep+diff로 hidden branch 부재 확인 후 결정(Phase 1은 후보 식별까지만).

### 2.3 Family inventory (출처: `INVENTORY.md`, 2026-05-04 기준 참고치)

acquisition 18 · body_plan_structural 21 · body_role 12 · identity_fallback 40 · interaction_cluster 29 ·
post_cleanup 27 · quality_publish 12 · reports_misc 19 · role_fallback_hollow 35 · second_pass 15 ·
source_coverage 23 · 기타. (현 시점 총수는 281로 증가 — family별 재계수는 Phase 2/7a 진입 시.)

## 3. Tracked / Untracked / Ignored 경계

| Surface | 디스크 | tracked | 비고 |
|---|---|---:|---|
| `Iris/build/**/*.py` (description/v2/tools/build) | 281 | 12 | 269 gitignored (reproduction) |
| `Iris/build/*.py` (tracked 전체, 재귀) | — | 73 | §2.1 분해 |
| `Iris/media/lua/client/Iris/Data/` (sealed runtime) | 36 | 36 | mutation 금지, SHA 봉인 |
| `Iris/output/` (build 산출물) | 47 | 47 | generated, 일부 source-like |
| `Iris/build/package/` (package 산출물) | 존재 | 0 | `.gitignore:6 Iris/build/*` ignored |
| Pulse compat wrapper `Pulse/Iris/Logic/IrisDesc/*.lua` | 6 | 6 | thin redirect, 제거 금지 |

- `git ls-files`는 pathspec에 `--`를 붙여야 디렉토리 하위 glob이 정확하다(`-- '<dir>/*.ext'`). `--` 없는 leading-path glob은 빈 결과를 낼 수 있어 측정에서 디렉토리 pathspec을 신뢰 기준으로 사용.
- `.gitignore`의 `Iris/build/*`가 build 직하를 ignore하나 기존 tracked 73개는 추적 유지 → tracked/untracked 혼재. 정합성 정리는 Change 8(only-if-required).

## 4. Compatibility / Sealed Surface

- **Pulse wrapper 6개**: thin 리다이렉트 shim, 내부 명시적 require 0, sealed protected-surface 해시 등재. compat surface 확정(conflict 14.5). 제거 금지.
- **Sealed runtime data 36개**: `phase1_artifact_source_classification.md` SHA baseline으로 봉인. Phase 8/9a가 변동 0 검증.
- **direct script execution baseline**: conflict 14.2 결정 전까지 불변 계약(governance §11).

## 5. Conflict Gate 요약 (상세: `phase1_conflict_resolution_gate.md`)

- resolved: 14.1(281), 14.3(per-file disposition), 14.4(추가 split 필요), 14.5(compat surface=B), 14.6(9a/9b 양축).
- **deferred (사용자 결정 대기): 14.2** (direct-exec vs package entrypoint) → Phase 3 entry 제한.
- 6/6 schema field 충족 → conflict gate completeness PASS.

## 6. Baseline 동기화 (inventory ↔ 기존 contract docs)

- `ENTRYPOINTS.md`/`build_import_contract.md`/`INVENTORY.md`는 이전 roadmap(`iris-refactoring-final-roadmap-v1.md`, `iris_refactor_roadmap_v2.0.md`) 기준(2026-05-04/05)이며, 본 readpoint 기준으로 Phase 1에서 현행화 주석을 추가한다(`phase1_inventory_readpoint.md` 참조 포인터 삽입).
