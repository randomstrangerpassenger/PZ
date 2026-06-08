# Phase 8 (Change 8) — Generated Artifact & Git Tracking Policy

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 8, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase6`. cwd: repo root.
> **Closeout State: `complete`**. Entry Gate: Phase 1 complete ✓.
> 분류 확정판: `phase8_artifact_source_classification.md`.

## 추적 정책 (확정)

| Surface | 정책 | 근거 |
|---|---|---|
| `Iris/media/lua/client/Iris/Data/` (sealed runtime, 36) | **tracked**, mutation 금지 | generated이나 런타임 배포 + diff/provenance 위해 추적. 빌드 외 변경 금지(SHA 보호 A425…4559) |
| `Iris/output/` (build 산출물, 47) | **tracked** | generated이나 회귀 비교(Q4 determinism)·provenance 위해 추적. 일부는 index 생성기 입력으로 재사용 |
| `Iris/build/package/` | **ignored** | package output, tracked source와 분리(`.gitignore:6 Iris/build/*`) |
| `Iris/build/.../staging/` | 대부분 **ignored** | reproduction/test fixture (Phase 7b: 보존, archive 불가) |
| active build scripts | **tracked** (allowlist) | source-of-truth |
| frozen reproduction scripts (269) | **ignored** | reproduction evidence (Phase 1) |

## `.gitignore` 검토 (only-if-required)

본 Change에서 `.gitignore`의 **추가 변경은 불필요**(only-if-required 조건 미충족)하다. 현행 allowlist 정책은:

- `Iris/build/*` ignore + 디렉토리별 `!` negation으로 active source를 명시 추적(tools/common, tools/pipeline, tests, compose core, index 생성기 등).
- 본 refactoring 중 필요에 의해 추가된 negation:
  - `Iris/build/quality/*.py` (Change 4 — split된 quality gate 모듈 추적용).
  - `Iris/build/description/v2/tools/common/*.py` (Change 3 — compose용 paths.py 추적용).
- 이 정책은 **sealed evidence를 손상하지 않으며**, generated runtime/output는 의도적으로 tracked, package는 ignored로 이미 올바르게 분리되어 있다.

→ 추가 정리 불필요. 변경 시 sealed/active surface 손상 위험만 발생하므로 minimal-diff 원칙상 **무변경**.

## Validation — 전 항목 PASS

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Sealed artifact SHA (§5 전수) | mutation 없음 | aggregate `A425…4559` MATCH (36/36 무변동) | ✅ |
| Tracked policy delta | classification table과 동기 | `git ls-files`: Iris/output **47**, Iris/build/package **0**, Iris/Data **36** (Phase 1과 동일) | ✅ |
| Generator output hash | Change 4 reporting / Change 5 evidence 산출물 일치 | Change 4/5/6 검증에서 evidence DETERMINISM_FILES drift 0 | ✅ |
| Package manifest | 분류 의도 부합 | `Iris/build/package` ignored, source와 분리 | ✅ |
| `.gitignore` review | 의도된 entry만 | 본 Change 무변경 (현행 정책 일관) | ✅ |
| Test baseline | `OK`, ≥ 407 | 407 OK (불변 — doc-only Change) | ✅ |

## §12 Quantitative Closeout (Change 8)
- [x] `Iris/output`, `Iris/build/package` classification table 전수 분류 (`phase8_artifact_source_classification.md`)
- [x] §5 Generated Artifacts 전수 SHA 변동 0 (sealed aggregate MATCH)
→ **Change 8 = `complete`** (doc 확정판 + 추적 정책 확정, `.gitignore` 무변경).
