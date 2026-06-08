# Phase 4 (Change 4) — Quality Gates Module Split

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 4, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase1`. cwd: repo root.
> **Closeout State: `complete`** (behavior-preserving split, 전 validation PASS).
> Entry Gate: Phase 1 `complete` ✓ + conflict 14.4 `resolved`("추가 split 필요", 1543 LOC 단일 파일) ✓.

## 변경 요약

`Iris/build/quality_gates.py`(실측 1543 LOC 단일 파일)를 gate별 module + reporting module로 분리하고,
`quality_gates.py`는 **얇은 CLI shim**(bootstrap + `main()` orchestration + `--update-sha`)으로 축소했다.
함수 본문은 **AST 기반 verbatim 추출**(전사 오류 0)로 이동했고, 산출물(build_report.json/md)은
live timestamp를 제외하면 byte-identical임을 입증했다.

## Split 매핑

| 신규 module | 이동 함수 | 의존 |
|---|---|---|
| `Iris/build/quality/config.py` (신규) | (함수 아님) 공유 상수: 경로·`BUILD_VERSION` 파생명·`DETERMINISM_FILES`/`DETERMINISM_BUILD_FILES`·enum | `tools.common.versions` |
| `quality/q1_pass_integrity.py` | `gate_q1` | config(DATA_DIR, BUILD_VERSION), tools.common.io |
| `quality/q2_strong_integrity.py` | `gate_q2` | (순수) |
| `quality/q3_anchor_completeness.py` | `gate_q3` | config(ALLOWED_EXEMPT_REASONS) |
| `quality/q4_determinism.py` | `canonical_sha256`, `gate_q4`, `update_frozen_sha` | config(경로/파일목록), tools.common.io |
| `quality/q5_regression_diff.py` | `gate_q5` + `q5_*` helper 17개 | config, tools.common.io |
| `quality/reporting.py` | `generate_build_report`, `generate_build_report_md` | config(QUALITY_GATES_VERSION), datetime, Counter |
| `quality_gates.py` (shim) | `main` + `__main__` | 위 module 전부 + tools.common.io |

- 총 27개 함수 전수 이동(`gate_q1~q5`, `canonical_sha256`, `update_frozen_sha`, `q5_*`×17, `generate_build_report(_md)`, `main`).
- `config.py`의 `BUILD_DIR`는 옛 module-local `SCRIPT_DIR`와 동일 경로(`Iris/build`)이며 어디에도 import되지 않던 이름이라 안전하게 개명.
- import 해석: shim과 config가 `Iris/build`를 `sys.path`에 두는 기존 bootstrap을 유지 → `from quality.X import` / `from tools.common.X import` 동일 방식으로 resolve(현 namespace-package 관례 유지, `__init__.py` 미추가). package-form 기계 전환(`__init__.py`/`python -m`)은 Change 3 소관.
- 기존 CLI surface(`python -B Iris/build/quality_gates.py`, `--update-sha`)와 `--update-sha` guard semantics는 그대로 유지.

## Validation (§6 Change 4) — 전 항목 PASS

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Quality gate full run | `python -B Iris/build/quality_gates.py` exit 0 + 전 gate PASS | exit 0; Q1·Q2·Q3(5 profiles/57)·Q4(17 files)·Q5 PASS | ✅ |
| Report JSON schema | `git diff --no-index` 빈 diff 또는 approved diff | timestamp 정규화 후 **SAME**; raw diff = timestamp 1줄(approved_diff_log) | ✅ |
| Report MD schema | 동상 | timestamp 정규화 후 **SAME** | ✅ |
| Determinism | 동일 입력 2회 → 내용 일치 | 2회 실행 내용 SAME(timestamp 제외) + Q4(canonical SHA) PASS | ✅ |
| Test baseline | `OK`, ≥ `baseline_test_count`(407) | **Ran 407 tests / OK** (exit 0) | ✅ |

### build_report timestamp 주의

`generate_build_report`는 `datetime.now(timezone.utc)`를 `timestamp` 필드로 넣는다(분리 이전부터 존재).
따라서 build_report.json/md의 raw SHA는 매 실행 변한다 — 이는 split이 만든 drift가 아니다.
behavior 동일성은 **timestamp 정규화 후 byte-identical**(JSON·MD 모두 SAME)로 입증했고,
build_report는 `DETERMINISM_FILES`(Q4 봉인 대상)에 포함되지 않는 build-only report artifact다.
해당 timestamp-only diff는 `docs/Iris/approved_diff_log.md`에 `surface = build_only`로 1건 기록.

## .gitignore (필요 변경)

`.gitignore`의 `Iris/build/*`는 신규 파일을 기본 ignore하므로, 새 `quality/` 패키지가 추적되도록
`tools/common/` 등과 동일한 allowlist 3줄을 추가했다(이 추가 없이는 split module이 untracked되어
fresh checkout에서 shim import가 깨진다 — Change 4 성립의 필요조건):

```
!Iris/build/quality/
Iris/build/quality/*
!Iris/build/quality/*.py
```

## §12 Quantitative Closeout (Change 4)

- [x] quality gate full run PASS
- [x] report schema `git diff --no-index` 빈 diff(= timestamp 정규화 후) + approved diff 1건(timestamp, build_only)
→ **Change 4 = `complete`**.

## 후속 메모

- gate module을 "순수 함수"로 만드는 것(파일 I/O를 main으로 끌어올림)은 본 split의 behavior-preserving 범위를 넘으므로 의도적으로 보류(현 gate는 일부 파일을 직접 읽음 — 동작 보존 우선). 후속 개선 후보.
- `ALLOWED_MIGRATION_TARGETS`는 현 코드에서 미사용으로 보이나 verbatim 보존(별도 dead-code 정리 후보).
