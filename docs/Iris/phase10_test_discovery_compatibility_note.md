# Phase 10 — Test Discovery & Validation Surface Compatibility

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 10.
> Entry Gate: Phase 1 complete ✓. 동반: `phase10_validation_matrix.md`.

## Discovery 정책 (현행 — 이미 정립됨)

| 도구 | scope | 비고 |
|---|---|---|
| `unittest discover` (primary baseline) | `Iris/build/description/v2/tests` (`-p "test_*.py"`) | `baseline_test_count = 407` OK. 본 plan 전 phase의 회귀 가드 |
| `pytest` | `pytest.ini` + `Iris/build/tests/conftest.py`로 scope 제한 | conftest가 root build test 폴더 collection을 unittest-호환 파일로 한정 |
| 직접 실행 (script-style) | root build test 중 import-time `sys.exit()` 보유분 | `python -B Iris/build/tests/<test>.py` |
| `python -m unittest <dotted>` | unittest-호환 개별 test | 예: `Iris.build.tests.test_evidence_pipeline_cross_track` |

## Root build tests 분류 (`Iris/build/tests/`, 실측)

| 파일 | 유형 | discovery |
|---|---|---|
| `test_evidence_pipeline_cross_track.py` | unittest.TestCase | `unittest`/`pytest` 가능 |
| `regression_test_outcomes.py` | `__main__` 가드 | import 안전, 직접 실행 |
| `test_fail_loud_coverage.py` | `__main__` 가드 | import 안전, 직접 실행 |
| `test_layer3_pipeline.py` | `__main__` 가드 (파이프라인 실행) | 직접 실행 |
| `test_wearable_6f.py` | `__main__` 가드 | 직접 실행 |
| `test_description_generator.py` | **import-time `sys.exit()`** (script-style) | **직접 실행 전용** |
| `test_determinism_rc.py` | **import-time `sys.exit()`** (script-style) | **직접 실행 전용** |
| `test_recipe_evidence.py` | **import-time `sys.exit()`** (script-style) | **직접 실행 전용** |

## 결정: script-style 변환 — 미실시 (low-risk-only, 의도)

import-time `sys.exit()` 3건(`test_description_generator`, `test_determinism_rc`, `test_recipe_evidence`)을
unittest로 전환하지 **않는다**:

- `pytest.ini` + `conftest.py`가 **이미 root build test collection을 unittest-호환으로 한정**하여 discovery
  충돌이 없다. `build_import_contract.md`가 이들을 "direct execution targets until converted"로 명시.
- 이들은 파이프라인 실행/검증 로직을 import 시점에 수행하는 historical script-style checks로, unittest 전환은
  behavior 변경 위험이 있고 계획은 "low-risk만" 허용. → 현행 정책(직접 실행 타깃) 유지가 minimal-diff.
- default `unittest discover -s description/v2/tests`는 이들을 수집하지 않으므로 407 baseline에 영향 없다.

따라서 Phase 10의 discovery 정규화는 **정책 문서화 + validation matrix 통합**으로 닫고, 코드 변환은 보류한다.

## Tracked vs. on-disk surface (중요 — baseline 재현성)

`unittest discover`의 **407은 디스크 기준**이다: `Iris/build/description/v2/tests/`에 **디스크 190개(`test_*.py`)** 가 있으나
`.gitignore`(`Iris/build/description/v2/tests/*` ignore + curated `!` allowlist)로 **추적은 6개뿐**:
`test_build_iris_index_data`, `test_compose_layer3_text_v2`, `test_current_authority_source_path_guard`,
`test_layer4_absorption_current_surface_guard`, `test_layer4_trace_edge_authority_admission_round`,
`test_legacy_active_silent_current_surface_guard`. 나머지(예: `test_wiki_fallback_contract.py`)는 **미추적 로컬 fixture**.

- 따라서 407 baseline은 **로컬 working tree 재현**(gitignored fixture 포함)이며, fresh clone의 추적 테스트 수와 다르다.
  본 plan 전 phase가 동일하게 로컬-디스크 407을 게이트로 사용 → 일관.
- **Change 9b 영향**: 9b split이 미추적 fixture `test_wiki_fallback_contract.py`(IrisWikiSections의 `getRuntimeLangKey`
  위치를 핀)를 깼다. **디스크에서 combined 검사로 수정 → 407 green 복귀**(commit 대상 아님 — gitignored).
  **추적 테스트 6개는 `IrisWikiSections` 미핀 → 9b는 추적 표면 무영향**(grep 확인). 추적 정책 변경(이 fixture 추적화)은
  Change 8 tracking policy 범주의 별도 결정 — 본 round 미실시(curated allowlist 존중).

## Validation
- `unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` → `OK`, 407 (불변, 로컬-디스크 기준).
- `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track` → `OK`.
- `pytest` (설치 시) → conftest scope 내 수집 (미설치면 skip — 위 unittest 명령이 fallback).
- `phase10_validation_matrix.md` → Change 1~9b 행 전수 + PowerShell 호환 + 3-filter 일관.
