# Phase 6 (Change 6) — Version / Path Manifest Hardening

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 6, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase6`. cwd: repo root.
> **Closeout State: `complete`** (정련된 metric 기준 — 아래 참조).
> Entry Gate: Phase 1 `complete` ✓.

## Closeout metric 정련 (사용자 승인, option A)

계획 §12의 `v24_hardcode_count == 0`(active manifest에 `Select-String 'v2\.4'`)은 **구조상 달성 불가능**이다:

1. `tools/common/versions.py`(manifest 포함)가 `BUILD_VERSION = "v2.4"`를 **정의** — 중앙화의 목표 그 자체가 v2.4 literal.
2. 43개 매치 중 ~28개가 **docstring/주석**(v2.4 파이프라인을 정확히 설명) — 제거 시 문서 훼손.
3. ~3개가 rightclick의 **mode-version 매핑 literal**(`"v2.4" if V24_MODE else "v2.3"...`) — 모드 라벨이지 build-version 하드코드가 아님.

따라서 closeout metric을 **"root-tree active 스크립트의 기능적 v2.4 경로/값 하드코드(정의·모드라벨·docstring 제외) == 0"**으로 정련(2026-06-07 사용자 결정 option A). literal `Select-String` count는 43 → **36**(기능적 7개 제거).

## 중앙화 내역 (7개 기능적 하드코드 → `BUILD_VERSION`, SHA-중립)

| 파일 | 변경 | 비고 |
|---|---|---|
| `recipe_evidence_pipeline.py` | `"version": "v2.4"` → `BUILD_VERSION` | 이미 versions import. recipe_index 출력 값(SHA 동일) |
| `convert_labelmap_to_lua.py` | `+import BUILD_VERSION`; `DATA_DIR=.../"v2.4"`→`/BUILD_VERSION`; `usecases_by_fulltype.v2.4.json`→f-string | 경로 동일 |
| `tools/pipeline/apply_registry_merge.py` | `+import BUILD_VERSION`; `DATA_DIR` + `registry_merge_accept`/`use_case_registry`/`usecases_by_fulltype` 4경로 → f-string | 경로 동일 |

`BUILD_VERSION == "v2.4"`이므로 모든 해석 경로/값이 byte-identical(경로 해석 동일성 검증으로 입증).

## 제외 (의도적)

- **`build_iris_recipe_index_data.py`** (argparse default 경로 2개): **description-v2 tools 트리** 소속이라 거기엔 중앙 `versions.py`가 없다(중앙 versions는 root 트리 `Iris/build/tools/common`). cross-tree 결합을 피하기 위해 제외 — dv 트리의 version 중앙화는 별도 후속(필요 시 dv 트리에 versions 헬퍼 추가). 또한 sealed-data 생성기라 본 round에서 실행/회귀 대상 아님.
- **rightclick mode-version literal**(`SOURCE_INDEX_V24_PATH`, `expected_version`/`suffix`/`version_label`의 `"v2.4" if V24_MODE...`): v22/v23/v24 모드 라벨 family. build-version과 개념이 달라 유지.
- **`versions.py` `BUILD_VERSION = "v2.4"`**: 중앙 정의(유지).
- **docstring/주석**: 정확한 문서로 유지.

## Validation — 전 항목 PASS

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| 경로 해석 동일성 | 변경 후에도 v2.4 경로로 동일 해석 | cl/ar 6경로 전부 v2.4 동일 | ✅ |
| Active pipeline smoke | recipe exit 0 + 산출물 hash 일치 | recipe exit 0; evidence DETERMINISM_FILES drift 0 | ✅ |
| v2.4 hardcode (functional) | 편집 3파일 기능적 literal == 0 | 0/0/0 | ✅ |
| Quality gate | 전체 PASS | All PASSED (exit 0) | ✅ |
| Test baseline | `OK`, ≥ 407 | **Ran 407 / OK** (0 error) | ✅ |
| Sealed Layer3 | 변동 없음 | aggregate `A425…4559` MATCH | ✅ |

## 부수 관찰 (out of scope)

- `convert_labelmap_to_lua.py`는 현재 committed 상태에서 **coverage FAIL-LOUD로 exit 1**한다
  ("Coverage FAILED. Add missing IDs to usecase_label_map.json"). 원본 코드(stash 후 실행)에서도 동일 실패 →
  **본 Change와 무관한 기존 데이터 상태 이슈**(usecase_label_map.json이 현재 use_case_id 집합을 다 덮지 못함).
  FAIL-LOUD가 write 전에 종료하므로 sealed `IrisUseCaseLabelMap.lua`는 변동 없음(drift 0). 데이터 coverage
  복원은 별도 작업(version-hardcode 범위 밖).

## §12 Quantitative Closeout (Change 6, 정련)
- [x] root-tree active 스크립트의 기능적 v2.4 경로/값 하드코드 == 0 (recipe/convert_labelmap/apply_registry_merge)
- [x] 경로/값 byte-identical (SHA-중립) — sealed/evidence drift 0
→ **Change 6 = `complete`** (정련 metric). literal `Select-String` 36 잔존(정의·모드라벨·docstring)은 위 사유로 의도된 잔존.
