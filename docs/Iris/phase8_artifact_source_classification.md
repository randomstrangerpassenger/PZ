# Phase 8 — Artifact / Source Classification (확정판)

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §5 Generated Artifacts, §6 Change 8.
> Phase 1 `phase1_artifact_source_classification.md`의 확정판. 측정일 2026-06-07.
> Entry Gate: Phase 1 complete ✓.

artifact를 **(A) sealed runtime data / (B) build output / (C) package output**으로 분류하고 각각의
**generator(source-of-truth 생성기)**를 연결한다. sealed mutation 없음은 SHA로 검증(§Validation).

## A. Sealed Runtime Data — `Iris/media/lua/client/Iris/Data/` (36 tracked, generated, mutation 금지)

`AGGREGATE_MANIFEST_SHA256 = A425385417808AD6756FAE435DC365725CD33B6D43664B585B77C243559F4559`
(per-file SHA는 `phase1_artifact_source_classification.md` 참조). generator-emitted, 수동 편집 금지.

| 아티팩트 | generator | 입력(source) |
|---|---|---|
| `IrisLayer3DataChunks.lua` + `Chunk001..011` (11), `layer3_renderer.lua` | Layer3 compose/export 파이프라인(`compose_layer3_*` + `main.py` export) | descriptions/usecases/overlay JSON (output) |
| `IrisUseCaseDescriptions.lua` + `UseCaseDescriptions/Chunk001..009` (9), `RequirementsLookup.lua` | `convert_descriptions_to_lua.py` | `descriptions_by_fulltype.v2.4.json`, `requirements_by_fulltype.v2.4.json` (output) |
| `IrisUseCaseLabelMap.lua` | `convert_labelmap_to_lua.py` | `usecase_label_map.json`(data/v2.4), `usecases_by_fulltype.v2.4.json` |
| `IrisClassifications.lua`, `IrisData.lua`, `IrisContextOutcomes.lua`, `IrisCapabilities.lua` | `main.py` 분류 파이프라인 | extraction/rule JSON |
| `IrisRecipeIndexData.lua` (+`IrisRecipeIndex.lua` wrapper) | `build_iris_recipe_index_data.py` | `recipe_index.v2.4.json`, `recipe_requirements_index.v2.4.json` |
| `IrisMoveablesIndexData.lua` (+`IrisMoveablesIndex.lua`) | `build_iris_moveables_index_data.py` | `ISMoveableDefinitions` 정적 파싱/덤프 |
| `IrisFixingIndexData.lua` (+`IrisFixingIndex.lua`) | `build_iris_fixing_index_data.py` | `scripts/fixing.txt`, `scripts/vehicles/vehiclesfixing.txt` |
| `IrisTranslationData.lua` | `tools/pipeline/build_iris_translation_data.py` | translation source |

> 주의: 이 36개는 **generated이지만 tracked**다(diff/provenance·런타임 배포 목적). `git`이 추적하되
> 빌드 외 mutation은 금지(SHA 보호). chunking 분할 정책 변경도 non-goal.

## B. Build Output — `Iris/output/` (47 tracked, generated; 일부 source-like)

| 분류 | 아티팩트(예) | generator |
|---|---|---|
| recipe evidence/index | `recipe_index`, `recipes_by_fulltype`, `recipe_evidence_decisions`, `recipe_review_queue`, `recipe_nav_registry`, `recipe_requirements_index`, `recipe_classification_matches`, `recipe_require_fields.v2.5` | `recipe_evidence_pipeline.py` + `tools/pipeline/build_recipe_*` |
| right-click evidence | `evidence_candidates`, `evidence_decisions`, `uniqueness_overlay`, `field_registry`, `review_queue`, `property_based_items`, `diagnostics(.v2.4)` | `rightclick_evidence_pipeline.py` |
| description/usecase | `descriptions_by_fulltype`, `usecases_by_fulltype`, `requirements_by_fulltype`, `capability_by_fulltype`, `tags_by_fulltype`, `layer3_*` | `main.py` / `description_generator.py` |
| build-side runtime Lua 사본 | `IrisClassifications.lua`, `IrisData.lua`, `context_outcomes.lua`, `IrisManualOverrides.lua` | main 파이프라인(런타임 `Iris/Data` 미러) |
| action/legacy | `action_requirement_index`, `action_evidence_classification`, `legacy_inventory`, `legacy_upgrade_candidates` | `build_action_requirement_index`, `classify_action_evidence`, `build_legacy_*` |
| 리포트/SHA/legacy 스냅샷 | `build_report.json/md`(`quality_gates.py`), `layer3_build_sha.txt`, `validation_report`, `regression_test_report`, `legacy_root/` | quality_gates / 각 파이프라인 |
| **source-like(재사용 입력)** | `recipe_index.v2.4.json`, `recipe_requirements_index.v2.4.json`, `recipe_nav_registry.v2.4.json`, `action_requirement_index.v2.4.json` | 위에서 생성되나 index 생성기의 **입력으로 재사용**(INVENTORY.md P1-1) |

> `build_report.json/md`는 build-only report로 live timestamp 포함(매 실행 변동) — sealed 아님(approved_diff AD-0001).

## C. Package Output — `Iris/build/package/` (0 tracked, gitignored)

- `.gitignore:6 Iris/build/*` 규칙으로 ignored. 내용: `Iris/`(패키지 미러) + `Iris.package_manifest.sha256.json`.
- **tracked source와 이미 분리**됨(의도된 상태). 패키징 산출물이며 repo 추적 대상 아님.

## 추적 정책 요약

| Surface | tracked? | 성격 |
|---|---|---|
| `Iris/media/lua/client/Iris/Data/` (36) | tracked | generated runtime, mutation 금지(SHA 보호) |
| `Iris/output/` (47) | tracked | generated build artifact (일부 source-like 재사용) |
| `Iris/build/package/` | ignored | package output (분리 유지) |
| `Iris/build/.../staging/` | 대부분 ignored | reproduction/test fixture (Phase 7b: 보존) |
| active build scripts | tracked(allowlist) | source |
| frozen reproduction scripts (269) | ignored | reproduction evidence |
