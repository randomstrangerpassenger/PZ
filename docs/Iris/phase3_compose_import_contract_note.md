# Phase 3 (Change 3) — Compose Import Contract + Bootstrap Cleanup

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 3, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase1`. cwd: repo root.
> **Closeout State: `complete`** (conflict 14.2 resolved = package form, 전 validation PASS).
> Entry Gate: Phase 1 `complete` ✓ + conflict 14.2 `resolved`(package form) ✓.

## 변경 요약

compose module의 `try/except ImportError` import dance(5개)를 제거하고 package-internal
**relative import**으로 고정했다. `style.normalizer`의 `sys.path.insert` 부트스트랩(item/render)을
`from tools.style.normalizer import` 절대 import로 교체했고, compose entrypoint의 inline
`ROOT = ...parents[2]`를 leaf helper `tools/common/paths.py`(description-v2 트리)의 `V2_ROOT`로
대체했다. 산출물(sealed Layer3) 무변동을 SHA로, 동작 보존을 test baseline(407 OK)로 입증했다.

## 두 개의 `tools` 트리 (핵심 사실)

이 저장소에는 별개의 `tools` 패키지 루트가 **두 개** 있다. 혼동하면 import가 깨진다:

| tree | 위치 | 소비자 | 포함 |
|---|---|---|---|
| root build | `Iris/build/tools/` | `quality_gates.py` 등 root 스크립트 (`Iris/build`가 sys.path) | `common/`(io, versions), `pipeline/`, `oneshots/` |
| description-v2 | `Iris/build/description/v2/tools/` | `compose_layer3_*` 등 dv 스크립트 (`description/v2`가 sys.path) | `build/`, `style/`, `common/`(신규 paths.py) |

→ compose의 `from tools.common.paths import`는 **description-v2 트리**의 `tools.common.paths`로 해석된다.
계획이 명시한 `Iris/build/tools/common/paths.py` 경로는 root 트리용이라 compose에는 부적합하여,
compose가 보는 트리(`description/v2/tools/common/paths.py`)에 leaf helper를 생성했다(계획 경로 정정).

## 적용 내역

### compose 모듈 (relative import, dance 제거)
- `compose_layer3_text.py`: try/except 제거 → `from .compose_layer3_io/.compose_layer3_body_profile/.compose_layer3_render import`; `from tools.common.paths import V2_ROOT as ROOT` (inline ROOT 제거).
- `compose_layer3_identity.py` / `compose_layer3_body_profile.py`: try/except 제거 → relative.
- `compose_layer3_item.py` / `compose_layer3_render.py`: try/except 제거 → relative; `sys.path.insert` + `from style.normalizer import` → `from tools.style.normalizer import` (`import sys` 제거).

### leaf helper (신규)
- `Iris/build/description/v2/tools/common/paths.py`: stdlib-only leaf. `V2_ROOT`(parents[2]=description/v2), `BUILD_ROOT`(parents[4]=build), `DATA_DIR`/`OUTPUT_DIR`/`STAGING_DIR`. `.gitignore`에 `description/v2/tools/common/*.py` allowlist 추가(미추가 시 untracked).

### caller import 갱신 (bare → package, 계획 "호출자 import line 일괄 갱신")
fallback 제거로 bare import이 깨지므로 compose를 bare로 쓰던 4개 소비자를 package 경로로 갱신:
- `build_body_role_full_preview.py` (test `test_build_body_role_full_preview`가 로드 → 갱신 필수)
- `build_layer3_body_plan_v2_preview.py`
- `build_adapter_native_body_plan_metadata_migration.py` (`import compose_layer3_text` → `from tools.build import compose_layer3_text`)
- `build_runtime_payload_enum_rename_scope_round.py`

## 실행 형태 (package form)

- compose 직실행은 이제 `python -B -m tools.build.compose_layer3_text` (cwd = `Iris/build/description/v2`).
  옛 `python compose_layer3_text.py` (bare, build 디렉토리 cwd)는 더 이상 지원 contract 아님.
- 검증: `python -m tools.build.compose_layer3_text --help` exit 0.

## Validation (§6 Change 3) — 전 항목 PASS

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Active pipeline / compose import | 패키지 import 해석 | replicate(`sys.path.insert(v2)` + `from tools.build.compose_* import`) IMPORT_OK | ✅ |
| Compose standalone | `python -m ...` exit 0 | `python -m tools.build.compose_layer3_text --help` exit 0 | ✅ |
| Test baseline | `OK`, ≥ 407 | **Ran 407 tests / OK** (exit 0, 0 error) | ✅ |
| Build artifact SHA (sealed) | 변동 없음 | sealed Layer3 aggregate `A425…4559` MATCH (변동 0) | ✅ |
| compose_except_import_count | `== 0` (14.2 resolved) | **0** | ✅ |
| root_bootstrap_count | baseline(254) 대비 감소 | **253** | ✅ |

> 첫 baseline 실행에서 `test_build_body_role_full_preview`가 import error(1건)로 실패 → 원인은 소비자의
> bare compose import. caller 갱신 후 재실행 **407 OK / 0 error**. (systematic-debugging로 근본원인 추적)

## §12 Quantitative Closeout (Change 3)
- [x] `compose_except_import_count == 0`
- [x] ROOT/sys.path count baseline 대비 감소 (ROOT 254→253, sys.path 134→132)
→ **Change 3 = `complete`**.
