# Phase 1 Baseline Metrics

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) — §6 Change 1 Quantitative Baseline.
> 측정일: 2026-06-07
> 측정 환경: Windows 11 + PowerShell, repository root cwd (`C:\Users\MW\Downloads\coding\PZ\`).
> 봉인 상태: SEALED. 이후 모든 Change closeout(§12)은 본 문서 값을 참조한다.

이 문서는 Change 1(Phase 1)이 측정·봉인한 정량 baseline이다. 각 metric은 계획 §6
Quantitative Baseline 표의 측정 방법을 그대로 따랐다. PowerShell 표기 규약(계획 머리말)에 따라
`Get-ChildItem -Recurse -File | Select-String -Pattern ...` 패턴을 사용하고, `__pycache__`는 전수 제외했다.

## Sealed Values (13/13)

| # | Metric | Value | 사용 phase |
|---|---|---:|---|
| 1 | `baseline_build_script_count` | **281** | Phase 1 (conflict 14.1), Phase 2/7a |
| 2 | `baseline_batch1_import_count` | **22** | Phase 2 closeout |
| 3 | `baseline_compose_except_import_count` | **5** | Phase 3 closeout |
| 4 | `baseline_root_bootstrap_count` | **254** | Phase 3 closeout |
| 5 | `baseline_syspath_insert_count` | **134** | Phase 3 closeout |
| 6 | `baseline_v24_hardcode_count` | **43** | Phase 6 closeout |
| 7 | `baseline_staging_toplevel_count` | **11** | Phase 7b closeout |
| 8 | `baseline_tools_build_loc` | **85549** | Phase 2/7a 참고 |
| 9 | `baseline_generator_debug_count` | **28** | Phase 9a closeout |
| 10 | `baseline_renderer_debug_count` | **15** | Phase 9a closeout |
| 11 | `baseline_layer3_chunk_count` | **11** | Phase 1 sealed inventory, Phase 8/9a SHA 검증 행 수 |
| 12 | `baseline_usecase_chunk_count` | **9** | Phase 1 sealed inventory, Phase 8/9a SHA 검증 행 수 |
| 13 | `baseline_test_count` | **407** | Phase 2~10 closeout |

## Measurement Commands (재현용)

공통: `$dvDir = 'Iris\build\description\v2\tools\build'`, `$dvPy = Get-ChildItem $dvDir -Filter *.py -Recurse -File | Where-Object FullName -notmatch '__pycache__'`

| # | Metric | Command |
|---|---|---|
| 1 | build_script_count | `$dvPy.Count` |
| 2 | batch1_import_count | `($dvPy \| Select-String -Pattern 'build_identity_fallback_batch1_clothing_surface_reuse' \| Measure-Object).Count` |
| 3 | compose_except_import_count | `(Get-ChildItem $dvDir -Filter 'compose_layer3_*.py' -Recurse -File \| Select-String -Pattern 'except ImportError' \| Measure-Object).Count` |
| 4 | root_bootstrap_count | `($dvPy \| Select-String -Pattern '^ROOT\s*=' \| Measure-Object).Count` |
| 5 | syspath_insert_count | `($dvPy \| Select-String -Pattern 'sys\.path\.insert' \| Measure-Object).Count` |
| 6 | v24_hardcode_count | `(Get-Content docs\Iris\phase1_active_script_manifest.txt \| Where-Object { $_ -and (Test-Path $_) } \| ForEach-Object { Get-Item $_ } \| Select-String -Pattern 'v2\.4' \| Measure-Object).Count` |
| 7 | staging_toplevel_count | `(Get-ChildItem 'Iris\build\description\v2\staging' -Directory \| Measure-Object).Count` |
| 8 | tools_build_loc | `($dvPy \| Get-Content \| Measure-Object -Line).Lines` |
| 9 | generator_debug_count | `(Select-String -Path 'Iris\media\lua\client\Iris\Logic\IrisDesc\Generator.lua' -Pattern 'Logger\.debug\(' \| Measure-Object).Count` |
| 10 | renderer_debug_count | `(Select-String -Path 'Iris\media\lua\client\Iris\Logic\IrisDesc\Renderer.lua' -Pattern 'Logger\.debug\(' \| Measure-Object).Count` |
| 11 | layer3_chunk_count | `(Get-ChildItem 'Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks' -Filter 'Chunk*.lua' \| Measure-Object).Count` |
| 12 | usecase_chunk_count | `(Get-ChildItem 'Iris\media\lua\client\Iris\Data\UseCaseDescriptions' -Filter 'Chunk*.lua' \| Measure-Object).Count` |
| 13 | test_count | §7 Test Baseline Update Rule parser (아래 참조) |

## `baseline_test_count` Parser Evidence (§7 Test Baseline Update Rule)

```
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py" -v
```

- `Ran 407 tests in ...` 행 파싱 → `baseline_test_count = 407`
- 동일 블록 status 행: `OK`
- `$LASTEXITCODE = 0`
- 측정 시 unittest 결과는 stderr로 출력되므로 `2>&1 | Out-File`로 캡처 후 `Select-String 'Ran (\d+) tests in '` / `^(OK|FAILED)`를 `Select-Object -Last 1`로 추출.

계획 §3/§4의 prior 참조값 `380 tests OK`는 Phase 1 재측정으로 **407 OK**로 봉인된다(테스트 증가에 따른 상향이며 baseline 약화 아님). 이후 갱신은 §7 Test Baseline Update Rule(Phase 5/10 한정, 단일 Change 1회)만 허용.

## Notes / 측정 정합성

- conflict 14.1: roadmap A(282)/B(269)는 동일 디렉토리(`description/v2/tools/build/*.py`)를 다른 시점에 잰 값으로, 현재 canonical 측정값은 **281**(2026-06-07, excl `__pycache__`, recursive). 상세는 `phase1_conflict_resolution_gate.md` §14.1.
- `Iris\build\description\v2\.tmp_tests\` 및 `tests\tmp*`는 권한 거부되는 전이적(transient) 임시 디렉토리이며 `tools\build` 스캔 범위 밖이라 metric 1·8에 영향 없음. whole-`Iris/build` 스캔 시에만 권한 오류 발생.
- metric 2(batch1_import_count=22)는 정의상 batch1 파일 자신의 자기 참조 라인도 포함할 수 있다. Phase 2 closeout 기준(`== 0`)은 caller import 해소 + 파일 sibling 강등 후 판정하며, 자기 참조/주석 라인 잔존 여부는 Phase 2 진입 시 import graph(`phase1_batch1_import_graph.md`)로 분해한다.

## Amendment Log

| 일자 | metric | 이전 값 | 새 값 | 사유 | commit |
|---|---|---|---|---|---|
| (없음) | | | | | |
