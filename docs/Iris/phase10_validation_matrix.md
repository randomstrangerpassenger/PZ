# Phase 10 — Validation Matrix (Change 1–9b 통합)

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 10, §7, §12.
> Entry Gate: Phase 1 complete ✓. 본 매트릭스는 전체 plan의 self-check 도구다.
> 실행 환경: Windows 11 + PowerShell, repo root cwd. baseline: `phase1_baseline_metrics.md`.

## 공통 규약 (3-filter + PowerShell)

- **3-filter 제외 규칙 (v6.0)**: build script 스캔은 `__pycache__` + `_archive` + `historical`을 일관 제외한다.
  공통 정의: `$dvPy = Get-ChildItem 'Iris\build\description\v2\tools\build' -Filter *.py -Recurse -File | Where-Object { $_.FullName -notmatch '__pycache__|_archive|historical' }`
- active 한정 측정은 `docs\Iris\phase1_active_script_manifest.txt`를 단일 입력으로 사용.
- native exe(`git`/`python`/`luac`) PASS/FAIL은 `$LASTEXITCODE`로 판정.
- 표 셀의 `\|`는 렌더 기준 표기 — 실행 시 `|`(파이프).

## 전체 공통 validation

| Item | Command | Expected |
|---|---|---|
| Test baseline | `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` (§7 parser) | `OK`, ≥ `baseline_test_count` (407) — **로컬-디스크 기준**(추적 6 / 디스크 190, gitignored fixture 포함; `phase10_test_discovery_compatibility_note.md`) |
| Cross-track test | `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track` | `OK` |
| Sealed Layer3 무변동 | `Iris/Data` 36개 SHA-256 aggregate | `A425385417808AD6756FAE435DC365725CD33B6D43664B585B77C243559F4559` MATCH |

## Change별 validation matrix

| Change | 핵심 Item | Command (요약) | Expected | closeout |
|---|---|---|---|---|
| **1** | path/chunk/metric/conflict gate | §5 path block; chunk enumerate; 13 metric; conflict gate 6/6 | 21/21 True; chunk 11/9; metric 13/13; gate 6/6 | complete |
| **3** | compose package form | `luac -p compose_layer3_*`; `compose_except_import_count`; `^ROOT =`/`sys.path.insert` count; `python -B -m tools.build.compose_layer3_text --help` | except 0; ROOT 254→253; syspath 134→132; smoke exit 0 | complete |
| **4** | quality_gates split | `python -B Iris/build/quality_gates.py`; report JSON/MD `git diff --no-index`(timestamp 정규화); determinism | exit 0 전 gate PASS; schema SAME; 407 | complete |
| **5** | evidence skeleton | `python -B Iris/build/recipe_evidence_pipeline.py`; `... rightclick_evidence_pipeline.py --v24`; cross-track | exit 0 + evidence DETERMINISM_FILES drift 0; 혼입 0 | complete |
| **6** | v2.4 중앙화 | `Get-Content docs\Iris\phase1_active_script_manifest.txt \| ? { $_ -and (Test-Path $_) } \| % { Get-Item $_ } \| Select-String 'v2\.4'`; 편집 3파일 기능적 literal | 기능적 hardcode(root-tree) 0; 경로 동일 | complete |
| **7a** | (제외) | — | frozen 스크립트 — `phase7a_deferral_note.md` | deferred |
| **7b** | staging disposition | `Get-ChildItem ...\staging -Directory \| Measure`; test-ref 측정 | disposition table 전수; archive 0(test fixture); 407 | complete |
| **8** | tracking policy | `git ls-files Iris/output`(47)/`Iris/build/package`(0)/`Iris/Data`(36); sealed aggregate | classification 동기; sealed MATCH | complete |
| **9a** | Renderer debug 게이팅 | `luac -p Renderer.lua/Generator.lua`; `if debugEnabled` guards; KO 부팅 `[Iris] Bootstrap complete` | luac 0; ungated debug Renderer 15→0; 부팅 OK | complete |
| **9b** | Browser/Wiki split | `luac -p` 4파일; Pulse `git status`/`git diff` 빈 출력; `git merge-base --is-ancestor a5054f3 <firstCode>`; Menu QA | luac 0; Pulse untouched; ancestor exit 0; Menu identical | complete |
| **10** | test discovery + 본 matrix | `unittest discover`(407); root build tests; 본 matrix dry-run | OK; Change 1~9b 행 전수 + PowerShell 호환 + 3-filter 일관 | complete |

## §12 Change 10 closeout 기준
- [x] `phase10_validation_matrix.md`가 **Change 1~9b 행 전수 포함** (7a는 deferral 명시)
- [x] 모든 명령 **PowerShell 호환** 확인
- [x] **`__pycache__`/`_archive`/`historical` 3-filter** 규칙 일관 (위 공통 규약)
→ **Change 10 = `complete`**.

> 제외(deferred): Phase 2(`phase2_deferral_note.md`), Phase 7a(`phase7a_deferral_note.md`) — frozen reproduction 스크립트.
