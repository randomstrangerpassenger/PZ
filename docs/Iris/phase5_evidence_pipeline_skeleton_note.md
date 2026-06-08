# Phase 5 (Change 5) — Evidence Pipeline Execution Skeleton

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 5, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase1`. cwd: repo root.
> **Closeout State: `complete`** (양쪽 pipeline PASS + cross-track 혼입 0 + 전 validation PASS).
> Entry Gate: Phase 1 `complete` ✓ (conflict 불필요).

## 핵심 발견: execution skeleton은 이미 공유 중

매핑 결과, recipe/right-click 두 evidence pipeline은 **이미 공통 stage skeleton
`tools.common.stage_runner.StageRunner`를 둘 다 소비**하고 있었다(`recipe`: announce/save_json,
`rightclick`: run/save_json). 즉 Change 5의 핵심 목표("execution skeleton만 공통화")는 **구조적으로
이미 충족**되어 있었다. 따라서 본 Change는 (a) 남은 안전한 공통 glue를 `evidence_skeleton.py`로 명시하고
(b) 합치면 안 되는 부분을 governance 근거와 함께 문서화하고 (c) 동작 보존을 전수 검증하는 데 집중한다.

## 추가한 공통 helper — `Iris/build/tools/common/evidence_skeleton.py` (신규)

mode-agnostic·output-neutral(stdout만 건드림)인 두 helper. 두 pipeline이 모두 import.

| helper | 역할 | 채택 |
|---|---|---|
| `pipeline_banner(title, width=60)` | 실행 헤더 출력 | recipe(width 60), rightclick(width 70) 양쪽 |
| `require_inputs(named_paths)` | 입력 파일 존재 prereq guard | recipe main (rightclick의 prereq는 phase_s 검증에 통합되어 있어 유지) |

`StageRunner`(stage_runner.py)가 공유 stage runner임을 docstring에 명시.

## 합치지 않은 것 (track authority 분리, §11 — 의도적)

- **canonical-SHA 함수**: 두 track의 canonical 사양이 **다르다** —
  recipe `canonical_sha256`는 compact `separators=(",", ":")`, rightclick `compute_sha256`는 기본(공백 포함).
  병합하면 한쪽 산출물 바이트가 바뀌어 **sealed determinism drift** + track 의미 혼합 → 금지. 각자 유지.
- phase 로직(recipe r1~r5/rq vs rightclick s/c/d/u/f), decision/authority, per-track logging
  (`PipelineLogger`), candidate/proof/field-registry 처리 — 전부 track 모듈에 유지.

## 부수 발견

- `rightclick_evidence_pipeline.py`는 종료 단계에서 `quality_gates.py`를 subprocess로 실행한다(line ~1342).
  그래서 rightclick 실행 시 `build_report.json/md`의 timestamp가 갱신된다(benign — `DETERMINISM_FILES`
  아님, approved_diff AD-0001 surface=build_only 범주). **이는 Change 4 split된 quality_gates shim이
  pipeline subprocess 경유로도 정상 작동함을 부수 입증**한다(전 게이트 PASS).

## Validation (§6 Change 5) — 전 항목 PASS

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Recipe pipeline run | `python -B recipe_evidence_pipeline.py` exit 0 + hash 일치 | exit 0; 산출물 drift 0 | ✅ |
| Right-click pipeline run | `python -B rightclick_evidence_pipeline.py --v24` 동상 | exit 0; 산출물 drift 0 | ✅ |
| Cross-track fixture | track별 산출물 독립(혼입 없음) | `Iris.build.tests.test_evidence_pipeline_cross_track` Ran 1 / OK | ✅ |
| Quality gate rerun | 전체 PASS | `quality_gates.py` All PASSED (exit 0) | ✅ |
| Test baseline | `OK`, ≥ 407 | **Ran 407 / OK** (0 error) | ✅ |
| Sealed Layer3 | 변동 없음 | aggregate `A425…4559` MATCH | ✅ |

> 동작 보존 입증: 편집 후 두 pipeline 재실행 시 `Iris/output`의 모든 evidence `DETERMINISM_FILES`가
> git clean(byte-identical), build_report만 timestamp 변동. helper는 stdout/guard만 다루어 산출물 무영향.

## §12 Quantitative Closeout (Change 5)
- [x] recipe/right-click pipeline 양쪽 PASS
- [x] cross-track 혼입 0건 (cross-track test OK)
→ **Change 5 = `complete`**.
