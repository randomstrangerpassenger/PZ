# Iris Codebase Refactoring Implementation Plan

> 상태: Draft v6.0 (revised per Review v5 feedback 2026-06-07)
> 기준일: 2026-06-07
> 상위 기준: `docs/Iris/Iris_Refactoring_Roadmap.md`, `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> 구조 양식: `docs/PLAN_TEMPLATE.md`
> 실행 단위: roadmap의 10개 Phase를 12개 Planned Change로 매핑 (Change 7/9 분리). Phase 1을 진입 게이트로 두고 이후 phase는 Phase 1 산출물 의존.
> 실행 환경: Windows 11 + PowerShell 기본. Bash/Unix 명령은 WSL 또는 Git Bash 사용 시에만 유효, 본 계획에서는 PowerShell 등가 명령을 병기.

> 변경 이력:
> - v1.0 (2026-06-07): 초안.
> - v2.0 (2026-06-07): Final Review 반영 — R1~R8 적용, Change 7→7a/7b, Change 9→9a/9b 분할, conflict gate schema 강화, validation matrix 구체화, 정량 closeout 기준 추가, disposition schema 추가, closeout state semantics 분리.
> - v3.0 (2026-06-07): Review v2 반영 — generated data 실제 경로 (`Iris/Data/IrisLayer3DataChunks.lua` + 11 chunks 등) 정정, PowerShell `Select-String -Recurse` 미지원 → `Get-ChildItem -Recurse -File | Select-String` 패턴으로 일괄 교체, IrisMain.lua 변경을 Phase 9a → 9b로 재배치 (manual QA 적용 surface 확장), PowerShell regex escape 규칙 명시, Phase 4 JSON schema diff를 `git diff --no-index` 기반으로 교체, baseline test parser/`__pycache__` 제외/`surface` 필드 등 non-critical 흡수.
> - v4.0 (2026-06-07): Review v3 반영 — Git SHA 비교를 문자열 `<` → `git merge-base --is-ancestor` + SHA 비동일성으로 교체 (Phase 9b manual QA gate 정합성 확보), Phase 6 v2.4 hardcode count를 Phase 1 active script manifest 입력 기반으로 정정 (active pipeline 한정 범위와 명령 정렬), Pulse wrapper untouched 검증을 `git status --short` + `git diff --name-only HEAD` 조합으로 확장 (staged/untracked 누락 방지), chunk count 기대값을 `baseline_layer3_chunk_count`/`baseline_usecase_chunk_count`로 등재, Change 4 `git diff --no-index --exit-code` 자동화 플래그 명시 + Validation 셀 편집 코멘트를 Implementation Notes로 이동, §7 Manual Validation의 Bootstrap 범위를 Phase 9a/9b로 한정.
> - v5.0 (2026-06-07): Review v4 반영 — 상단 status line을 v5.0으로 동기화 (이전 v3.0 표기 잔존 해소), PowerShell 표기 규약 확장 (native exe exit code 접근은 `$LASTEXITCODE`, 표 셀 안의 `\|`는 렌더된 Markdown 기준 표기로 명시, 실행 cwd는 repository root로 고정), `phase1_active_script_manifest.txt` 사용처에 `docs\Iris\` 경로를 일관 명시, Pulse wrapper untouched 두 명령의 역할 분담 (safety net) 한 줄 추가, Approved Diff Procedure에 reviewer 제약 (sealed_artifact / runtime / public_facing / compat surface는 reviewer = 사용자만 허용, self 금지).
> - v6.0 (2026-06-07): Review v5 반영 — Approved Diff `surface` enum에 `build_only` 추가 (build-only artifact를 합법적으로 기록할 surface 값 누락 해소), Pulse wrapper untouched 검증의 stdout/stderr 구분 명시 (stdout 기준 빈 출력 + `$LASTEXITCODE -eq 0`, stderr의 known git warning은 별도 환경 이슈로 기록), §6 Change 10 Validation matrix dry run 행에 `historical` 필터 추가 (다른 phase의 3-filter 규칙과 정렬), `surface = authority` self carve-out에 minimum evidence 요건 추가 (self-judgment 제거 — grep + reference 근거 필수), Change 9b Pulse wrapper untouched 셀의 inline 역할 분담 설명을 Implementation Notes로 이동해 표 가독성 회복.

> PowerShell 표기 규약 (v3.0 신설, v5.0 확장):
> - 본 문서의 PowerShell 명령은 단일 라인 표기 시 `|`를 **regex alternation**이 아닌 **파이프 연산자**로 사용한다.
> - regex 안에서 alternation을 표현할 때는 큰따옴표 안에서 `|`를 escape 없이 그대로 둔다 (예: `-notmatch "_archive|historical"`).
> - **Markdown 표 셀 안의 명령은 렌더된 Markdown 기준 표기**이다. raw 파일에서는 셀 내부의 `|`가 Markdown 표 구분자와 충돌하지 않도록 `\|`로 escape되어 있다. **실행 시에는 렌더링 결과 (또는 raw 파일에서 `\|` → `|` 치환) 를 사용한다.** 자동 복사-실행 워크플로가 있다면 raw 텍스트에서 `\|` → `|` 치환 단계를 거친다 (v5.0 명시).
> - 본문 텍스트의 `|`는 Markdown escape 규칙을 그대로 따른다 (`\|` 표기). 표 셀 외부의 fenced code block (` ```powershell ... ``` `) 안의 명령에는 escape를 적용하지 않는다 — 실행 가능한 원본 그대로다.
> - **Native exe (`git`, `python`, `luac` 등) 호출의 exit code 자동 판정은 `$LASTEXITCODE`로 접근한다** (v5.0 명시). PowerShell의 `$?`는 native exe의 정확한 exit code를 반영하지 않으므로 PASS/FAIL gate에서는 `$LASTEXITCODE`만 진리로 사용한다. 예시:
>
>   ```powershell
>   git merge-base --is-ancestor $baselineCommit $firstCodeCommit
>   if ($LASTEXITCODE -eq 0) { 'PASS' } elseif ($LASTEXITCODE -eq 1) { 'FAIL' } else { 'ERROR' }
>   ```
> - **실행 cwd는 repository root 기준**이다 (v5.0 명시). 본 문서의 모든 상대 경로는 repository root (`C:\Users\MW\Downloads\coding\PZ\`)에서의 상대 경로다. 다른 cwd에서 실행 시 경로 prefix를 명시적으로 추가하거나 `Set-Location` 후 실행한다.

---

## 1. Objective

`docs/Iris/Iris_Refactoring_Roadmap.md`가 정의한 10개 phase를 실행 가능한 12개 Change 단위로 변환한다. 각 Change는 별도 round로 닫히되, 본 계획은 roadmap에서 "별도 판정 필요"로 남긴 6개 conflict (§14.1~§14.6)를 Phase 1 inventory 산출물 위에서 closeout 가능한 **차단성 결정 게이트**로 명시한다. "기록만 한 conflict"는 closeout 통과 사유가 되지 못한다.

직접 코드 변경의 1차 목표는 다음 두 가지로 한정한다.

- description v2 build script군이 family별 재현성 계약과 공통 helper 소비 경로를 갖는 관리 가능한 build surface가 되도록 점진 정리한다.
- build/source/artifact/runtime boundary가 inventory 문서와 코드에서 일관되게 읽히도록 정리하고, runtime/build-time authority 분리, FAIL-LOUD validation, determinism gate, sealed artifact 보존을 유지한다.

본 계획의 closeout claim 보증 한계는 §12와 §7 Validation Limits에서 명시적으로 닫는다.

---

## 2. Scope

이 계획은 다음 surface만 다룬다.

- `Iris/build/` 하위 build pipeline, helper, manifest, quality gate, evidence pipeline.
- `Iris/build/description/v2/tools/build/` 하위 build script군의 family helper 소비 구조와 batch1 import 해소.
- `Iris/build/description/v2/staging/` 하위 종료/진행 중 staging의 per-disposition 분류.
- `Iris/output`, `Iris/build/package`, generated runtime Lua의 tracked/untracked policy 명확화.
- `Iris/media/lua/client/Iris/Logic/IrisDesc/`, `Iris/media/lua/client/Iris/UI/Wiki/`, `Iris/media/lua/client/Iris/UI/Browser/`, `Iris/media/lua/client/Iris/IrisMain.lua` 하위 runtime Lua 중 user-facing behavior를 바꾸지 않는 범위의 책임 분할 (Phase 9a/9b).
- `Iris/build/description/v2/tests/` 및 root build tests의 discovery boundary 정리 (Phase 10).
- `docs/Iris/` 하위 inventory, readpoint, disposition note.

### Explicitly Out Of Scope

- Iris taxonomy, evidence rule, source authority, Layer 3 body policy 재설계.
- Recipe / Right-click evidence 의미 체계 통합 또는 cross-track semantic merge.
- 새 capability, 새 Outcome, 새 Source, 새 테스트 인프라 추가.
- 한국어 설명 문장 rewrite, 추천/비교/해석 문장 추가.
- Lua runtime UI 재설계, chunking 분할 정책 변경.
- Pulse, Echo, Fuse, Nerve, Frame, Cortex, Canvas 등 cross-module 구조 변경.
- deployment, package publishing, Workshop readiness, B42 readiness, production validation 선언.
- runtime optimization 또는 gameplay behavior 변경.
- staging evidence 대량 삭제 또는 archive-by-glob 정리.
- public `IrisAPI` 또는 `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua` compatibility wrapper 제거 (deprecation decision 전).

---

## 3. Non-Goals

- 단일 round 안에서 roadmap 10개 phase 또는 12개 Change를 모두 닫는다.
- Phase 1 inventory 없이 Phase 2~10 중 어느 것이든 착수한다.
- roadmap §14의 conflict 6개 (script count, direct script execution vs package entrypoint, archive 정책, quality_gates split 상태, compatibility surface, runtime cleanup 범위)를 Phase 1 conflict gate 외부에서 임의 결정한다.
- direct script execution baseline을 별도 판정 (conflict 14.2) 결정 전에 깬다.
- runtime Lua 변경 (Phase 9a/9b)에서 manual in-game QA 없이 user-facing behavior change를 성공으로 주장한다.
- generated runtime Lua / generated JSON을 손으로 쪼개거나 의미 수정한다.
- sealed artifact 또는 current readpoint를 본 계획 실행 자체로 mutation한다.
- `380 tests OK` baseline을 §7 Test Baseline Update Rule 이외의 방식으로 약화한다.
- `implemented_only`를 merge/release closeout 또는 behavior-preserving claim으로 사용한다 (§12 참조).

---

## 4. Assumptions

- 본 계획 실행 시점의 readpoint는 `docs/Iris/Iris_Refactoring_Roadmap.md` 2026-06-07 draft 상태와 동일하다.
- `Iris/build/ENTRYPOINTS.md`, `Iris/build/build_import_contract.md`, `Iris/build/description/v2/tools/build/INVENTORY.md`는 phase 진입 시점에 현행화된다 (Phase 1 deliverable).
- Pulse 의존성 없음, Iris standalone 상태가 유지된다.
- Layer 3 runtime data는 chunk-only 구조이며 generated Lua는 수동 편집 대상이 아니다. 실제 sealed artifact 진리 위치는 §5 Generated Artifacts 참조.
- `Iris/build/tools/common/`의 `io.py`, `stage_runner.py`, `versions.py`는 존재하나 모든 script가 소비하지 않는다 (Phase 2/6 대상).
- `Iris/build/quality_gates.py` 현행 상태는 Phase 1 readpoint 확인 후에만 split 여부를 결정한다 (conflict 14.4).
- direct script execution baseline은 roadmap이 명시한 compatibility contract로 가정되며, conflict 14.2 결정 전에는 Phase 3 entry blocker로 둔다.
- archive/delete는 per-file/per-directory disposition 기반으로만 수행한다 (conflict 14.3).
- `380 tests OK` 기준은 Phase 1 시점에 재측정되어 `baseline_test_count`로 봉인된다. 수집 parser는 §7 Test Baseline Update Rule 참조.
- 한국어 KO mode boot 검증과 in-game manual QA가 필요한 phase는 Phase 9b 한정 (`IrisMain.lua` 변경 포함, v3.0 재배치)이며, 그 외 phase는 build-only validation으로 닫힌다.
- 실행 환경 기본은 Windows 11 + PowerShell이며, Unix-only 명령은 PowerShell 등가로 대체 가능한 경우에만 본 계획에서 사용한다 (§7). PowerShell 표기 규약은 머리말 참조.
- `additive amendment preference`, `minimal diff preservation`, `no silent compatibility shim`은 현행 governing docs에서 명시 인용이 확인되지 않은 운영 원칙이므로, 본 계획에서는 §11에서 "본 plan 운영 원칙"으로 라벨링한다 (이 항목들의 사용은 §11에 한정).

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tools/build/**/*.py` — family helper 도입, batch1 import 해소, ROOT/sys.path bootstrap 축소.
- `Iris/build/description/v2/tools/build/compose_layer3_*.py` — compose import dance 정리 (conflict 14.2 결정 의존).
- `Iris/build/tools/common/` — `io.py`, `stage_runner.py`, `versions.py` 확장 또는 추가 helper.
- `Iris/build/quality_gates.py` — gate별 module + reporting/CLI 분리 (Phase 1 readpoint + conflict 14.4 확인 후).
- `Iris/build/recipe_evidence_pipeline.py`, `Iris/build/rightclick_evidence_pipeline.py` — execution skeleton 공통화, authority 분리 유지.
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua` — Phase 9a debug line 축소.
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua` — Phase 9a debug line 축소.
- `Iris/media/lua/client/Iris/IrisMain.lua` — Phase 9b INIT_MODULES helper 흡수 (v3.0: 9a → 9b 재배치, manual QA 적용).
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` — Phase 9b split (section renderer / property extractor / usecase line renderer).
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` — Phase 9b split (interaction collection / UI row rendering).
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Generator.lua` — disposition note만 (compat wrapper, 제거 금지).
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Logger.lua` — 동상.
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Ordering.lua` — 동상.
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Renderer.lua` — 동상.
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/TagParser.lua` — 동상.
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Templates.lua` — 동상.

### Docs

- `docs/Iris/Iris_Refactoring_Plan.md` (본 문서).
- `Iris/build/ENTRYPOINTS.md`, `Iris/build/build_import_contract.md`, `Iris/build/description/v2/tools/build/INVENTORY.md` — Phase 1 readpoint update.
- `docs/Iris/phase1_inventory_readpoint.md` (신규).
- `docs/Iris/phase1_artifact_source_classification.md` (신규).
- `docs/Iris/phase1_batch1_import_graph.md` (신규).
- `docs/Iris/phase1_conflict_resolution_gate.md` (신규, conflict schema는 §6 Change 1 참조).
- `docs/Iris/phase1_pulse_wrapper_usage_inventory.md` (신규).
- `docs/Iris/phase1_baseline_metrics.md` (신규, 정량 baseline).
- `docs/Iris/<phase>_disposition_note.md` (phase 단위 분류표).
- `docs/Iris/phase10_validation_matrix.md` (phase별 PASS/FAIL 매트릭스).
- `docs/Iris/approved_diff_log.md` (신규, §7 Approved Diff Procedure).

### Config

- `.gitignore` — Phase 8 tracked/untracked policy 정리 시 only-if-required 수정.
- `Iris/build/tools/common/versions.py` 또는 신규 manifest — Phase 6 version/path 중앙화.

### Generated Artifacts (v3.0 정정)

본 절은 sealed/generated artifact의 실제 진리 위치다. SHA 검증 및 mutation 금지 보호 범위가 본 목록을 기준으로 한다.

- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` (chunk entrypoint).
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001.lua` ~ `Chunk011.lua` (11개 chunk 파일).
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua` (entrypoint).
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/Chunk001.lua` ~ `Chunk009.lua`.
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/RequirementsLookup.lua`.
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`.
- `Iris/media/lua/client/Iris/Data/IrisCapabilities.lua`.
- `Iris/media/lua/client/Iris/Data/IrisContextOutcomes.lua`.
- `Iris/media/lua/client/Iris/Data/IrisData.lua`.
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua`.
- `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua`, `IrisRecipeIndex.lua`.
- `Iris/media/lua/client/Iris/Data/IrisMoveablesIndexData.lua`, `IrisMoveablesIndex.lua`.
- `Iris/media/lua/client/Iris/Data/IrisFixingIndexData.lua`, `IrisFixingIndex.lua`.
- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua`.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` (generator-emitted runtime helper, mutation 금지).
- `Iris/output/**` — source-like baseline vs generated artifact 분류 (Phase 8).
- `Iris/build/package/**` — package output으로 분리 (Phase 8).
- staging evidence (`Iris/build/description/v2/staging/**`) — per-directory disposition (Phase 7a/7b).

본 목록은 Phase 1 inventory에서 사실관계 재검증 후 `phase1_artifact_source_classification.md`에 봉인된다. 본 목록에 누락된 generated artifact가 발견되면 Phase 1에서 즉시 추가하고 보호 범위를 확장한다.

### Path Existence Verification (Phase 1 Step 0, v3.0 확장)

Phase 1 첫 작업으로 다음 PowerShell 명령으로 경로 존재 여부를 확인한다. 부재 항목은 conflict gate 또는 disposition note로 즉시 이관한다.

```powershell
$paths = @(
  # Runtime Lua targets (Phase 9a/9b)
  'Iris\media\lua\client\Iris\IrisMain.lua',
  'Iris\media\lua\client\Iris\Logic\IrisDesc\Generator.lua',
  'Iris\media\lua\client\Iris\Logic\IrisDesc\Renderer.lua',
  'Iris\media\lua\client\Iris\UI\Wiki\IrisWikiSections.lua',
  'Iris\media\lua\client\Iris\UI\Browser\IrisBrowserInteractionRenderer.lua',
  # Pulse compat wrappers (6 files, disposition only)
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\Generator.lua',
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\Logger.lua',
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\Ordering.lua',
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\Renderer.lua',
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\TagParser.lua',
  'Iris\media\lua\client\Pulse\Iris\Logic\IrisDesc\Templates.lua',
  # Build pipeline entrypoints (Phase 3/4/5)
  'Iris\build\quality_gates.py',
  'Iris\build\recipe_evidence_pipeline.py',
  'Iris\build\rightclick_evidence_pipeline.py',
  # Inventory / contract docs (Phase 1 readpoint)
  'Iris\build\ENTRYPOINTS.md',
  'Iris\build\build_import_contract.md',
  'Iris\build\description\v2\tools\build\INVENTORY.md',
  # Sealed generated artifact entrypoints (Phase 8/9)
  'Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks.lua',
  'Iris\media\lua\client\Iris\Data\IrisUseCaseDescriptions.lua',
  'Iris\media\lua\client\Iris\Data\IrisClassifications.lua',
  'Iris\media\lua\client\Iris\Data\layer3_renderer.lua'
)
$paths | ForEach-Object { [PSCustomObject]@{ Path = $_; Exists = (Test-Path $_) } }
```

각 항목 `Exists = True` 확인이 Phase 1 deliverable. `False`가 1건이라도 발견되면 `phase1_conflict_resolution_gate.md`에 path mismatch를 기록하고 Phase 1을 `blocked`로 강등한다.

추가로 chunk 디렉토리는 enumerate로 확인하며, 측정 결과는 §6 Change 1 Quantitative Baseline의 `baseline_layer3_chunk_count`, `baseline_usecase_chunk_count`로 봉인된다 (v4.0 hard-code 제거).

```powershell
@(
  'Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks',
  'Iris\media\lua\client\Iris\Data\UseCaseDescriptions'
) | ForEach-Object {
  [PSCustomObject]@{
    Dir = $_
    ChunkCount = (Get-ChildItem $_ -Filter 'Chunk*.lua' -ErrorAction SilentlyContinue | Measure-Object).Count
  }
}
```

본 명령의 출력값을 baseline metric으로 등재한 뒤에는 모든 sealed artifact validation이 해당 baseline 값을 참조한다. 측정 시점과 봉인된 값이 다르면 sealed artifact inventory 재측정이 필요하다.

---

## 6. Planned Changes

Roadmap의 10개 phase를 12개 Change로 매핑한다. 각 Change는 독립 commit/round 단위이며, 진입 순서는 Phase 1 → Phase 2~10 의존 관계를 따른다. Change 7과 Change 9는 위험도 분리를 위해 a/b로 분할된다.

### Change 1 — Phase 1: Scope, Inventory, Artifact Boundary Seal

Purpose:

- active source, generated output, staging evidence, package copy, compatibility wrapper, build script disposition을 재측정하고 이후 모든 phase의 분모를 봉인한다.
- roadmap §14의 6개 conflict 게이트 입력을 제공한다.

Files:

- Update: `Iris/build/ENTRYPOINTS.md`, `Iris/build/build_import_contract.md`, `Iris/build/description/v2/tools/build/INVENTORY.md`
- Create: `docs/Iris/phase1_inventory_readpoint.md`
- Create: `docs/Iris/phase1_artifact_source_classification.md`
- Create: `docs/Iris/phase1_batch1_import_graph.md`
- Create: `docs/Iris/phase1_conflict_resolution_gate.md`
- Create: `docs/Iris/phase1_pulse_wrapper_usage_inventory.md`
- Create: `docs/Iris/phase1_baseline_metrics.md`
- Create: `docs/Iris/phase1_active_script_manifest.txt` (v4.0 신설, `active` 분류 build script의 저장소 상대 경로 목록. Change 6 v2.4 hardcode count 등 active 한정 측정의 단일 진리 입력)

Implementation Notes:

- §5 Path Existence Verification (chunk enumerate 포함)을 첫 단계로 수행.
- build script를 `active` / `legacy_archive` / `duplicate_consolidation_candidate` / `reproduction_evidence`로 분류하고, `active` 분류된 경로 (저장소 상대 경로, repo root 기준)를 `docs/Iris/phase1_active_script_manifest.txt`에 한 줄당 한 경로로 봉인한다 (v5.0: 경로 prefix 명시). 본 manifest는 Change 6 등 "active pipeline 한정" 측정의 단일 입력이며, 모든 사용처는 repo root cwd 기준 `docs\Iris\phase1_active_script_manifest.txt`로 호출한다.
- `git ls-files`, `git status`, `git diff --stat`으로 tracked/untracked/ignored 경계를 산출한다.
- `build_identity_fallback_batch1_clothing_surface_reuse.py`를 import하는 모든 caller를 enumerate한 import graph를 만든다.
- Pulse compat wrapper 6개 파일 (`Generator/Logger/Ordering/Renderer/TagParser/Templates.lua`)의 require/use inventory를 grep으로 enumerate한다.
- `Iris/output`, `Iris/build/package`, §5 Generated Artifacts의 sealed artifact list (`Iris/Data/IrisLayer3DataChunks.lua` + chunks, `IrisUseCaseDescriptions.lua` + chunks, `IrisClassifications.lua`, `layer3_renderer.lua` 등)의 tracked policy를 분리해 기록한다.
- script count 차이 (roadmap A 282 vs B 269)는 동일 glob/필터 기준으로 재측정해 conflict 14.1을 닫는다. `__pycache__` 제외 규칙은 §7 Test Baseline Update Rule 적용.
- `quality_gates.py` 현재 함수/CLI surface를 그대로 측정해 conflict 14.4의 입력으로 둔다.
- §6 Quantitative Baseline을 `phase1_baseline_metrics.md`에 기록한다.

#### Conflict Resolution Gate Schema

`phase1_conflict_resolution_gate.md`는 roadmap §14의 6개 conflict 각각에 대해 다음 필드를 반드시 채운다. 한 필드라도 미정인 conflict가 있으면 Phase 1은 `complete`로 닫을 수 없다 (closeout schema는 §12 참조).

| Field | 의미 |
| --- | --- |
| `conflict_id` | `14.1` ~ `14.6` |
| `status` | `resolved` / `blocked` / `deferred` |
| `decision` | resolved 시 결정 내용, blocked/deferred 시 차단 사유 |
| `decision_owner` | 결정 권한 보유자 (default: 사용자) |
| `minimum_evidence` | 결정 근거가 된 산출물 경로 (inventory snippet, grep 결과 등) |
| `downstream_blocking_phase` | 미결정 시 진입 금지되는 Change 번호 |
| `allowed_next_action` | resolved 시 즉시 가능한 다음 단계 |
| `blocked_next_action` | blocked/deferred 시 명시 금지되는 다음 단계 |

다음 downstream blocking 매핑은 필수로 기록한다.

- 14.1 script count → Phase 1 baseline metric blocker (Phase 1 자체)
- 14.2 direct script execution vs package entrypoint → Phase 3 entry blocker
- 14.3 archive policy → Phase 7b entry blocker
- 14.4 quality gate split status → Phase 4 entry blocker
- 14.5 compatibility surface → Phase 9b entry blocker
- 14.6 runtime cleanup scope → Phase 9a/9b split decision blocker

#### Quantitative Baseline (v3.0 정정)

`phase1_baseline_metrics.md`에 다음 수치를 기록한다. 이후 Change들의 closeout 기준 (§12)이 이 baseline을 참조한다. 모든 `Select-String` 호출은 PowerShell 표기 규약 (머리말) 및 PowerShell 5.x/7.x 호환을 위해 `Get-ChildItem -Recurse -File | Select-String -Pattern ...` 패턴을 사용한다.

| Metric | 측정 방법 | 사용 phase |
| --- | --- | --- |
| `baseline_build_script_count` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Measure-Object` | Phase 1 (conflict 14.1), Phase 2/7a |
| `baseline_batch1_import_count` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern 'build_identity_fallback_batch1_clothing_surface_reuse' \| Measure-Object` | Phase 2 closeout |
| `baseline_compose_except_import_count` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter 'compose_layer3_*.py' -Recurse -File \| Select-String -Pattern 'except ImportError' \| Measure-Object` | Phase 3 closeout |
| `baseline_root_bootstrap_count` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern '^ROOT\s*=' \| Measure-Object` | Phase 3 closeout |
| `baseline_syspath_insert_count` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern 'sys\.path\.insert' \| Measure-Object` | Phase 3 closeout |
| `baseline_v24_hardcode_count` | Phase 1이 봉인한 active script manifest (`phase1_inventory_readpoint.md`의 active 분류 + `phase1_artifact_source_classification.md`의 `active` 분류) 경로 목록만 입력으로 사용. 예시 (repo root cwd 기준, v5.0 경로 정정): `Get-Content docs\Iris\phase1_active_script_manifest.txt \| Where-Object { $_ -and (Test-Path $_) } \| ForEach-Object { Get-Item $_ } \| Select-String -Pattern 'v2\.4' \| Measure-Object`. v4.0: 이전 `Iris\build -Filter *.py -Recurse` 기반은 reproduction/legacy script까지 잡아 "active 한정" 범위와 충돌하므로 제거. `__pycache__`/`_archive`/`historical` 등 비active 제외는 manifest 단계에서 일관 적용. | Phase 6 closeout (동일 manifest + 동일 필터로 정렬) |
| `baseline_staging_toplevel_count` | `Get-ChildItem Iris\build\description\v2\staging -Directory \| Measure-Object` | Phase 7b closeout |
| `baseline_tools_build_loc` | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Get-Content \| Measure-Object -Line` | Phase 2/7a 참고 |
| `baseline_generator_debug_count` | `Select-String -Path Iris\media\lua\client\Iris\Logic\IrisDesc\Generator.lua -Pattern 'Logger\.debug\(' \| Measure-Object` | Phase 9a closeout |
| `baseline_renderer_debug_count` | `Select-String -Path Iris\media\lua\client\Iris\Logic\IrisDesc\Renderer.lua -Pattern 'Logger\.debug\(' \| Measure-Object` | Phase 9a closeout |
| `baseline_layer3_chunk_count` | `(Get-ChildItem Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks -Filter 'Chunk*.lua' \| Measure-Object).Count` (v4.0 신설) | Phase 1 sealed artifact inventory, Phase 8/9a SHA 검증 행 수 일치 확인 |
| `baseline_usecase_chunk_count` | `(Get-ChildItem Iris\media\lua\client\Iris\Data\UseCaseDescriptions -Filter 'Chunk*.lua' \| Measure-Object).Count` (v4.0 신설) | Phase 1 sealed artifact inventory, Phase 8/9a SHA 검증 행 수 일치 확인 |
| `baseline_test_count` | §7 Test Baseline Update Rule의 parser 규칙 적용 결과 | Phase 2~10 closeout |

#### Validation (Phase 1)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Path existence | §5 PowerShell block (확장판) | 모든 항목 `Exists = True` | 1건 이상 `False` | conflict gate에 path mismatch 기록 후 Phase 1 `blocked` |
| Chunk count | §5 chunk enumerate block | 측정값이 정수 + `baseline_layer3_chunk_count` / `baseline_usecase_chunk_count`로 봉인 | 측정 실패 또는 봉인 누락 | sealed artifact inventory 재측정 |
| Tracked inventory | `git ls-files Iris \| Measure-Object` | 정수 결과 + classification 표 동기 | classification 표와 file 수 불일치 | inventory readpoint 재측정 |
| Baseline tests | `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` (§7 parser 적용) | `OK` + 통과 수 = `baseline_test_count` | `FAILED` 또는 ERROR | Phase 1 중단, 코드 변경 없음으로 즉시 종료 |
| Conflict gate completeness | Manual: `phase1_conflict_resolution_gate.md` 수동 검토 | 6개 conflict 모두 schema field 충족 | 미정 필드 존재 | Phase 2+ 진입 금지, gate 보강 |
| Baseline metrics | Manual: `phase1_baseline_metrics.md` 수동 검토 | 13개 metric 모두 정수값 (v4.0: chunk count 2종 추가) | 측정 실패 metric 존재 | 해당 metric 재측정 |

Expected Closeout: `complete` (모든 deliverable 작성 + 모든 conflict schema field 충족 + 모든 baseline metric 측정 완료 시).

---

### Change 2 — Phase 2: Description v2 Build Common Helper Extraction

Purpose:

- description v2 build script군을 family별 helper 소비 구조로 정리하고 batch1 library import anti-pattern을 해소한다.

Entry Gate: Phase 1 `complete`.

Files:

- Modify: `Iris/build/description/v2/tools/build/build_identity_fallback_batch1_clothing_surface_reuse.py`
- Modify: `Iris/build/description/v2/tools/build/build_identity_fallback_batch{2..9}_*.py` (Phase 1 graph 기준 enumerate)
- Modify: `Iris/build/tools/common/io.py`, `stage_runner.py`
- Create: `Iris/build/tools/common/family_io.py` 또는 family별 helper module (Phase 1 분류 기준 결정)
- Create: `docs/Iris/phase2_helper_adoption_note.md`
- Create: `docs/Iris/phase2_batch1_import_migration_note.md`

Implementation Notes:

- family별 (identity_fallback, source_coverage, interaction_cluster, weak_active_cleanup, acquisition 등) common I/O, JSONL, hash, markdown report helper를 정리한다.
- batch1에 묶인 상수/유틸을 common helper로 옮긴 뒤 batch1은 다른 batch와 동등한 sibling으로 낮춘다.
- artifact-path-only script는 reproduction contract를 먼저 남긴 뒤 보존/추적 결정 (Phase 7a로 위임 가능).
- direct script execution baseline 보존 여부는 conflict 14.2 결정에 따른다. 결정 전에는 양쪽 호환 (직실행 + helper consumption) 경로 유지.
- dual-import wrapper가 도입되면 wrapper 코멘트에 `TODO: remove by Phase <N> closeout` 형태 마감 일자 명시 — 영구화 방지.

#### Validation (Phase 2)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Family direct script smoke | `python -B Iris\build\description\v2\tools\build\<script>.py` (변경된 script 전수) | exit code 0 + 산출물 hash 일치 | exit code != 0 또는 SHA drift | 해당 family commit revert |
| Test baseline | `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` (§7 parser 적용) | `OK`, 통과 수 ≥ `baseline_test_count` (§7 Test Baseline Update Rule 참조) | `FAILED` 또는 통과 수 감소 (rule 위반) | 마지막 commit revert |
| Artifact SHA | `Get-FileHash Iris\build\description\v2\output\<artifact>` before/after | SHA 일치 또는 approved diff entry 존재 | SHA drift + approved diff 없음 | 해당 helper migration commit revert |
| Batch1 import count | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern 'build_identity_fallback_batch1_clothing_surface_reuse' \| Measure-Object` | Phase 2 closeout 시 `Count == 0` | `Count > 0` 잔존 | closeout 보류, residual round 추가 |

Expected Closeout: 일반적 `partial` (family 단위 sub-round). 모든 family 처리 + `batch1_import_count == 0` 도달 시 `complete`.

---

### Change 3 — Phase 3: Build Import Contract, Compose Contract, Root Bootstrap Cleanup

Purpose:

- compose module의 `try/except ImportError` import dance와 ROOT/sys.path bootstrap 반복을 정리한다.

Entry Gate: Phase 1 `complete` + conflict 14.2 `resolved` 또는 `deferred` (deferred 시 본 Change는 path helper 도입까지만 진행, compose dance 제거는 후속 round).

Files:

- Modify: `Iris/build/description/v2/tools/build/compose_layer3_*.py`
- Create or Modify: `Iris/build/description/v2/tools/build/__init__.py`
- Create: `Iris/build/tools/common/paths.py`
- Update: `Iris/build/build_import_contract.md`
- Create: `docs/Iris/phase3_compose_import_contract_note.md`
- Create: `docs/Iris/phase3_root_bootstrap_cleanup_batch.md`
- Create: `docs/Iris/phase3_unresolved_entrypoint_decision_record.md` (conflict 14.2 deferred 시)

Implementation Notes:

- conflict 14.2 결정에 따라 두 경로 중 하나를 contract로 고정한다.
- 결정이 deferred면 path helper만 도입하고 compose import dance 제거는 후속 round로 둔다.
- 호출자 import line은 contract 결정 이후에만 일괄 갱신한다.
- import cycle 방지를 위해 path helper는 leaf module로 유지.

#### Validation (Phase 3)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Active pipeline smoke | Phase 1 inventory에 enumerate된 entrypoint 전수 직실행 | exit code 0 + 산출물 hash 일치 | exit code != 0 | 해당 commit revert |
| Compose standalone | Phase 1 inventory의 compose 시나리오 직실행 | exit code 0 | exit code != 0 | compose 변경 commit revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |
| Build artifact SHA | `Get-FileHash` before/after | SHA 일치 또는 approved diff | SHA drift + approved diff 없음 | 해당 commit revert |
| Compose except import count | `Get-ChildItem Iris\build\description\v2\tools\build -Filter 'compose_layer3_*.py' -Recurse -File \| Select-String -Pattern 'except ImportError' \| Measure-Object` | Phase 3 `complete` 기준 `Count == 0` (conflict 14.2 resolved일 때만) | conflict 14.2 deferred 상태에서 `Count == 0` 미달성 허용 | — |
| ROOT bootstrap count | `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern '^ROOT\s*=' \| Measure-Object` | `baseline_root_bootstrap_count` 대비 감소 | 감소 없음 | closeout 보류 |

Expected Closeout: conflict 14.2 `resolved` 시 `complete`, `deferred` 시 `partial` + decision record 유지.

---

### Change 4 — Phase 4: Quality Gates Module Split

Purpose:

- `Iris/build/quality_gates.py`를 gate별 책임과 reporting/CLI 책임으로 분리한다.

Entry Gate: Phase 1 `complete` + conflict 14.4 `resolved`로 "추가 split 필요" 판정.

Files:

- Modify: `Iris/build/quality_gates.py` (얇은 CLI shim으로 축소)
- Create: `Iris/build/quality/q1_pass_integrity.py`
- Create: `Iris/build/quality/q2_strong_integrity.py`
- Create: `Iris/build/quality/q3_anchor_completeness.py`
- Create: `Iris/build/quality/q4_determinism.py`
- Create: `Iris/build/quality/q5_regression_diff.py`
- Create: `Iris/build/quality/reporting.py`
- Create: `docs/Iris/phase4_quality_gates_split_note.md`

Implementation Notes:

- 기존 `python -B Iris/build/quality_gates.py` CLI surface와 `--update-sha` flag semantics는 그대로 유지한다.
- `--update-sha`는 별도 승인 scope에서만 실행한다 (본 계획 자동 validation에서 제외).
- gate별 module은 순수 함수 + 명시적 입력/출력으로 분리, reporting module이 JSON/Markdown schema 단일 책임을 가진다.
- Validation에서 schema diff는 `git diff --no-index --exit-code <before> <after>` 를 1차 자동화 신호로 사용한다 (exit code 0 = 빈 diff, 1 = drift, 2 = 입력 오류). v3.0의 `Compare-Object` on PSCustomObject는 nested 깊이 비교가 불완전해서 제거되었으며, JSON canonical 비교가 추가로 필요한 경우 다음 Python one-liner를 보조로 사용한다:

  ```powershell
  python -c "import json,sys;a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));print('SAME' if a==b else 'DIFF')" before.json after.json
  ```

#### Validation (Phase 4)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Quality gate full run | `python -B Iris\build\quality_gates.py` | exit code 0, 전체 gate PASS | exit code != 0 또는 gate FAIL | 즉시 revert |
| Report JSON schema | `git diff --no-index --exit-code before.json after.json` | exit code 0 (빈 diff) 또는 approved diff entry 존재 | exit code != 0 + approved diff 없음 | 즉시 revert |
| Report Markdown schema | `git diff --no-index --exit-code before.md after.md` | exit code 0 (빈 diff) 또는 approved diff entry 존재 | exit code != 0 + approved diff 없음 | 즉시 revert |
| Determinism gate | 동일 입력 2회 실행 → `Get-FileHash` 비교 | SHA 일치 | SHA 불일치 | 즉시 revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

Expected Closeout: `complete` (split + report schema 보존 시).

---

### Change 5 — Phase 5: Evidence Pipeline Execution Skeleton Refactor

Purpose:

- Recipe / Right-click evidence pipeline의 execution skeleton만 공통화하고 evidence decision authority는 분리 유지한다.

Entry Gate: Phase 1 `complete`.

Files:

- Modify: `Iris/build/recipe_evidence_pipeline.py`
- Modify: `Iris/build/rightclick_evidence_pipeline.py`
- Create: `Iris/build/tools/common/evidence_skeleton.py`
- Create: `docs/Iris/phase5_evidence_pipeline_skeleton_note.md`

Implementation Notes:

- Recipe-specific parser/requirements logic은 recipe module에 남긴다.
- Right-click-specific source index validation, candidate generation, proof merge, field registry logic은 right-click module에 남긴다.
- v2.2/v2.3/v2.4 mode handling은 module 내부에서 처리하고 skeleton은 mode-agnostic으로 유지.
- 두 track의 의미 체계 혼합 금지 (governance constraint §11).

#### Validation (Phase 5)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Recipe pipeline run | `python -B Iris\build\recipe_evidence_pipeline.py` | exit code 0 + 산출물 hash 일치 또는 approved diff | exit code != 0 또는 SHA drift + approved diff 없음 | 즉시 revert |
| Right-click pipeline run | `python -B Iris\build\rightclick_evidence_pipeline.py --v24` | 동상 | 동상 | 즉시 revert |
| Cross-track fixture | Phase 1 inventory가 정의한 fixture 실행 | track별 산출물 독립성 유지 (cross-track field 혼입 없음) | cross-track 혼입 감지 | 즉시 revert |
| Quality gate rerun | `python -B Iris\build\quality_gates.py` (Phase 4 산출물 기준) | 전체 PASS | FAIL | 즉시 revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

Expected Closeout: `complete`.

---

### Change 6 — Phase 6: Version and Path Manifest Hardening

Purpose:

- `v2.4`, `v2.5`, output suffix, data root, upstream source candidates, worktree-specific paths를 중앙화한다.

Entry Gate: Phase 1 `complete`.

Files:

- Modify: `Iris/build/tools/common/versions.py`
- Create: `Iris/build/tools/common/paths_manifest.py` 또는 `manifest.json`
- Modify: hard-coded `v2.4` path를 보유한 active pipeline script (Phase 1 grep 결과 기반)
- Create: `docs/Iris/phase6_version_path_manifest_note.md`

Implementation Notes:

- active pipeline에서 hard-coded `v2.4` path를 제거한다.
- `.claude/worktrees/<name>` 같은 local worktree default candidate는 CLI option / 환경변수 / explicit local manifest 중 하나로 이동.
- historical oneshot script의 reproduction path는 예외 문서화로 남긴다 (삭제하지 않음).
- 외부화 후 old artifact lookup이 가능한지 확인 (regression 회피).

#### Validation (Phase 6)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Active pipeline smoke | Phase 1 inventory의 active pipeline 전수 직실행 | exit code 0 + 산출물 hash 일치 | exit code != 0 또는 SHA drift | 즉시 revert |
| Source sync dry run | `python -B <source_sync_script> --dry-run` | exit code 0 + dry-run plan 출력 | exit code != 0 | 즉시 revert |
| Path resolution tests | `python -B -m unittest <path_test_module>` | `OK` | `FAILED` | 즉시 revert |
| v2.4 hardcode count | Phase 1이 봉인한 active script manifest를 입력으로 한 측정 (v4.0 정정, v5.0 경로 정정). repo root cwd 기준: `Get-Content docs\Iris\phase1_active_script_manifest.txt \| Where-Object { $_ -and (Test-Path $_) } \| ForEach-Object { Get-Item $_ } \| Select-String -Pattern 'v2\.4' \| Measure-Object`. `baseline_v24_hardcode_count`와 동일 manifest + 동일 필터를 사용해 baseline ↔ closeout 측정이 정렬된다. | `Count == 0` (active script 한정. oneshot/historical/reproduction은 manifest 단계에서 제외) | `Count > 0` 잔존 | closeout 보류 |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

v4.0 정정: 이전 `Iris\build -Filter *.py -Recurse` 기반 명령은 reproduction/legacy/historical script까지 잡아 "active pipeline 한정" 범위와 명령이 어긋났다 (review v3 측정 결과 32 files / 112 matches). active script manifest를 단일 입력으로 사용함으로써 (a) "active 한정" 범위 의미와 (b) baseline ↔ closeout 명령 정렬을 동시에 달성한다. PowerShell `-notmatch`의 regex `|` alternation 규약은 머리말 참조.

Expected Closeout: `complete`.

---

### Change 7a — Phase 7a: Selective Round Script Consolidation

Purpose:

- 명확히 같은 구조의 sibling script를 안전한 범위에서 통합한다 (archive sweep과 분리).

Entry Gate: Phase 1 `complete`.

Files:

- Consolidation candidates (Phase 1 classification 결과 기반으로 최종 확정):
  - `Iris/build/description/v2/tools/build/build_post_cleanup_phase3_pkg3{a..j}*.py`
  - `Iris/build/description/v2/tools/build/build_source_coverage_{b1..b4,c1a..c1e}*.py`
  - `Iris/build/description/v2/tools/build/build_identity_fallback_batch{2..9}_authority_promotion*.py`
  - `Iris/build/description/v2/tools/build/freeze_quality_baseline_v{1..4}*.py`
  - `Iris/build/description/v2/tools/build/report_*_{draft,final}*.py`
- Create: 통합 entrypoint script + batch config JSON
- Create: `docs/Iris/phase7a_consolidation_note.md`

Implementation Notes:

- batch별 차이가 hidden branch logic이 아닌 단순 설정 차이인 것을 grep + diff로 확인한 후에만 통합한다.
- 통합 후 batch config는 JSON 등 data file로 외부화한다.
- consolidation 후보 1건당 1 commit을 유지해 rollback 단위를 최소화한다.

#### Validation (Phase 7a)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Artifact SHA per candidate | `Get-FileHash <artifact>` before/after | 후보별 SHA 일치 또는 approved diff | SHA drift + approved diff 없음 | 해당 candidate commit revert |
| Related batch tests | Phase 1이 매핑한 batch별 test | 모두 `OK` | `FAILED` | 즉시 revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |
| Hidden branch detection | Manual: 통합 전 `git diff <batch_n>.py <batch_m>.py` 수동 검토 | 단순 설정 차이만 발견 | logic 차이 발견 | 해당 batch는 consolidation 후보에서 제외 |

Expected Closeout: 일반적 `partial` (consolidation 후보를 순차 처리). 모든 승인 후보 완료 시 `complete`.

---

### Change 7b — Phase 7b: Staging and Nested Archive Sweep

Purpose:

- 종료된 staging directory와 nested archive 후보를 per-disposition 기준으로 이관한다.

Entry Gate: Phase 1 `complete` + conflict 14.3 `resolved`.

Files:

- Move: 종료 staging directory → `_archive/staging/<original path>/` (per-directory, `git mv` 기반)
- Disposition note: `_archive/p0-2/Iris/Iris/...` 중첩 백업 (이동 결정은 본 phase 외부)
- Create: `docs/Iris/phase7b_archive_sweep_note.md`
- Create: `docs/Iris/phase7b_per_directory_disposition_table.md` (Disposition Schema 적용)

Implementation Notes:

- archive/delete는 glob 사용 금지. 모든 이동은 `git mv` 기반.
- 진행 중 staging round를 archive로 오인하지 않도록 Phase 1 disposition 표를 기준 진리로 사용.
- hard-coded staging path를 보유한 build script가 깨지지 않는지 grep으로 확인.

#### Per-Directory Disposition Schema

`phase7b_per_directory_disposition_table.md`의 모든 행은 다음 schema를 충족한다.

| Field | 의미 |
| --- | --- |
| `path` | 원본 절대/저장소 상대 경로 |
| `disposition` | `keep_active` / `archive` / `defer` / `delete_candidate` |
| `evidence_type` | `sealed_evidence` / `reproduction_evidence` / `staging_intermediate` / `disposable_artifact` |
| `tracked_status` | `tracked` / `untracked` / `ignored` |
| `reference_check` | 본 path를 참조하는 build script 수 (grep 결과) |
| `package_mirror_check` | `Iris/build/package` 또는 `Iris/output` 미러 존재 여부 |
| `decision_owner` | 결정 권한자 |
| `target_destination` | `archive` 시 `_archive/staging/<original>/` 등. `keep_active`/`defer`/`delete_candidate` 시 `N/A` 허용 |
| `rollback_path` | `git mv` 역적용 명령. `archive`가 아니면 `N/A` 허용 |

규칙:

- `sealed_evidence`는 `archive` 외 disposition 금지 (mutation 금지).
- `delete_candidate`는 본 Change에서 실제 삭제하지 않으며 후속 deprecation decision으로 위임. `target_destination`/`rollback_path`는 `N/A`로 두되 disposition note의 `delete_candidate` 절에 deferral 사유를 명시한다.
- `keep_active`는 본 Change에서 이동 없음. `target_destination`/`rollback_path` 모두 `N/A`.
- `defer`는 본 Change에서 결정 보류. `target_destination`/`rollback_path` 모두 `N/A`이고 `decision_owner`가 후속 결정 시점을 명시한다.

#### Validation (Phase 7b)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Staging path grep | `Get-ChildItem Iris\build -Filter *.py -Recurse -File \| Where-Object FullName -notmatch '__pycache__' \| Select-String -Pattern 'staging/<moved>' \| Measure-Object` | `Count == 0` (이동된 모든 path) | `Count > 0` 잔존 | 해당 이동 `git mv` 역실행 |
| git mv 이동 확인 | `git status --short \| Select-String '^R'` | 이동 행 수 = disposition table archive 수 | 불일치 | disposition table 재확인 |
| Sealed evidence preservation | Phase 8 sealed artifact SHA check (Change 8 산출물 활용) | SHA 일치 | SHA drift | 즉시 revert |
| Staging top-level count | `Get-ChildItem Iris\build\description\v2\staging -Directory \| Measure-Object` | `baseline_staging_toplevel_count` 대비 감소 (disposition table에 명시된 만큼) | 예상 외 감소/증가 | disposition table 재확인 |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

Expected Closeout: 일반적 `partial`. disposition table 전수 처리 시 `complete`.

---

### Change 8 — Phase 8: Generated Artifact and Git Tracking Policy Cleanup

Purpose:

- runtime generated Lua, `Iris/output`, staging evidence, package copy의 source/artifact/tracked 정책을 명확히 한다.

Entry Gate: Phase 1 `complete`.

Files:

- Modify: `.gitignore` (only if required)
- Create: `docs/Iris/phase8_tracking_policy_note.md`
- Create: `docs/Iris/phase8_artifact_source_classification.md` (Phase 1 분류표의 확정판)

Implementation Notes:

- §5 Generated Artifacts 목록 (sealed artifact 진리)을 generator/source manifest와 연결한다.
- `Iris/output` tracked files가 source-like baseline인지 generated artifact인지 분류한다.
- `Iris/build/package`는 package output으로 분리하고 tracked source와 명확히 분리한다.
- `.gitignore` allowlist는 round/evidence 기준으로 정리하되 sealed evidence를 손상하지 않는다.
- sealed artifact mutation 발생 여부를 SHA 비교로 검증.

#### Validation (Phase 8, v3.0 sealed artifact 경로 정정)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Tracked policy delta | `git ls-files Iris/output`, `git ls-files Iris/build/package` before/after | classification table과 동기 | drift | 즉시 revert |
| Generator output hash | Change 4 reporting + Change 5 evidence pipeline 산출물 SHA before/after | 일치 또는 approved diff | drift + approved diff 없음 | 즉시 revert |
| Sealed artifact SHA — Layer3 entrypoint | `Get-FileHash Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks.lua` before/after | 변동 없음 | drift | 즉시 revert |
| Sealed artifact SHA — Layer3 chunks (11개) | `Get-ChildItem Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks -Filter 'Chunk*.lua' \| Get-FileHash` before/after | 11개 전수 변동 없음 | 1건 이상 drift | 즉시 revert |
| Sealed artifact SHA — UseCaseDescriptions entrypoint | `Get-FileHash Iris\media\lua\client\Iris\Data\IrisUseCaseDescriptions.lua` before/after | 변동 없음 | drift | 즉시 revert |
| Sealed artifact SHA — UseCaseDescriptions chunks (9개) + RequirementsLookup | `Get-ChildItem Iris\media\lua\client\Iris\Data\UseCaseDescriptions -Filter '*.lua' \| Get-FileHash` before/after | 10개 전수 변동 없음 | 1건 이상 drift | 즉시 revert |
| Sealed artifact SHA — generated index/data | `Get-FileHash Iris\media\lua\client\Iris\Data\IrisClassifications.lua`, `IrisRecipeIndex.lua`, `IrisMoveablesIndex.lua`, `IrisFixingIndex.lua`, `layer3_renderer.lua` 등 §5 목록 전수 | 변동 없음 | drift | 즉시 revert |
| Package manifest | `Get-ChildItem Iris\build\package -Recurse \| Measure-Object` before/after | 분류 의도에 부합 | drift | 즉시 revert |
| .gitignore review | Manual: `git diff -- .gitignore` 수동 검토 | 의도된 entry만 | 의도 외 변경 | 해당 .gitignore 변경 revert |

Expected Closeout: `complete`.

---

### Change 9a — Phase 9a: Behavior-Neutral Runtime Cleanup (v3.0 축소)

Purpose:

- user-facing behavior와 무관한 runtime Lua 정리에 한정한다. v3.0에서 IrisMain helper 흡수는 9b로 재배치되었다 (review v2의 Medium 지적 반영 — IrisMain bootstrap/dispatch 변경은 require smoke만으로 behavior-neutral 단정 불가).

Entry Gate: Phase 1 `complete` + conflict 14.6에서 9a/9b 분리 승인.

Files:

- Modify: `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua` (debug line 축소 또는 trace mode 분리)
- Modify: `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua` (debug line 축소 또는 trace mode 분리)
- Disposition only: debug text output 또는 `_dev/` 디렉토리 (Phase 1 path 검증에서 실제 존재 확인된 항목 한정. v3.0 검증 결과 `_dev/IrisTranslationDebug.lua`는 부재로 scope 제외)
- Create: `docs/Iris/phase9a_runtime_cleanup_note.md`

Implementation Notes:

- 본 Change는 **표시 경로/dispatch 변경 없이 debug noise 축소**에 한정한다.
- `IrisMain.lua`, `IrisWikiSections.lua`, `IrisBrowserInteractionRenderer.lua`는 본 Change에서 다루지 않는다 (9b로 분리).
- logger/info/warn/error 정책 조정은 release/dev log boundary를 명시한 후에만 시도.

Manual QA Requirement: **면제** (behavior-neutral 한정, 표시 경로 변경 없음).

#### Validation (Phase 9a)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| Lua syntax check | `luac -p Iris\media\lua\client\Iris\Logic\IrisDesc\Generator.lua` 등 변경 파일 전수 | exit code 0 | exit code != 0 | 즉시 revert |
| Runtime require smoke | Manual: KO mode 진입 → `[Iris] Bootstrap complete` console 메시지 확인 | 메시지 출력 | 부재 또는 Lua error | 즉시 revert + runtime validation 재수행 (§10 Rollback) |
| Generator debug count | `Select-String -Path Iris\media\lua\client\Iris\Logic\IrisDesc\Generator.lua -Pattern 'Logger\.debug\('  \| Measure-Object` | `baseline_generator_debug_count` 대비 감소 (의도된 만큼) | 예상 외 변동 | closeout 보류 |
| Renderer debug count | `Select-String -Path Iris\media\lua\client\Iris\Logic\IrisDesc\Renderer.lua -Pattern 'Logger\.debug\('  \| Measure-Object` | `baseline_renderer_debug_count` 대비 감소 | 예상 외 변동 | closeout 보류 |
| Generated data SHA | §6 Change 8 sealed artifact SHA 표 전수 재실행 | 변동 없음 | drift | 즉시 revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

Expected Closeout: `complete` (behavior-neutral 한정, 모든 validation PASS 시).

---

### Change 9b — Phase 9b: IrisMain Helper Absorption + Runtime Renderer Responsibility Split + Compatibility Wrapper Disposition (v3.0 확장)

Purpose:

- IrisMain INIT_MODULES helper 흡수 (v3.0: 9a → 9b 재배치), IrisWikiSections/IrisBrowserInteractionRenderer 책임 분할, Pulse compat wrapper disposition 문서화를 한 Change에서 함께 다룬다. 셋 모두 Browser/Wiki/Tooltip 영향 가능성이 있으므로 manual QA로 묶는다.

Entry Gate: Phase 1 `complete` + conflict 14.5 `resolved` + conflict 14.6에서 9b 진입 승인 + `phase9b_manual_qa_checklist.md` 작성 완료 (entry gate deliverable, baseline screenshot 포함).

Files:

- Modify: `Iris/media/lua/client/Iris/IrisMain.lua` (INIT_MODULES spec 또는 generic dispatch로 작은 helper 흡수)
- Split: `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` → section renderer / property extractor / usecase line renderer
- Split: `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` → interaction collection / UI row rendering
- Disposition note only: Pulse compat wrapper 6개 파일
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Generator.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Logger.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Ordering.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Renderer.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/TagParser.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Templates.lua`
- Create: `docs/Iris/phase9b_irismain_absorption_note.md` (v3.0 신규)
- Create: `docs/Iris/phase9b_runtime_split_note.md`
- Create: `docs/Iris/phase9b_compat_wrapper_disposition_note.md`
- Create: `docs/Iris/phase9b_manual_qa_checklist.md` **(entry gate deliverable, Change 진입 commit 이전에 작성)**

Implementation Notes:

- Pulse compat wrapper 6개는 본 Change에서 **제거하지 않는다**. disposition note만 작성하며 제거는 별도 deprecation decision으로 위임.
- IrisMain helper 흡수는 INIT_MODULES spec 복잡도 증가를 피하기 위해 동치성을 유지하는 최소 변경에 한정한다.
- 각 split은 require path와 caller 전수 갱신을 동반한다. require path 복원 경로를 commit message에 명시 (§10 Rollback).
- public Lua API surface는 변경하지 않는다.
- IrisMain 변경과 UI split은 가능한 한 별도 commit으로 분리해 rollback 입자도를 유지한다 (commit boundary는 manual QA matrix에 함께 기록).
- **Pulse wrapper untouched 검증의 두 명령 역할 분담** (v5.0 도입, v6.0 표 셀에서 이동):
  - `git status --short -- <path>`: staged + working tree + untracked 전부를 잡는 1차 safety net.
  - `git diff --name-only HEAD -- <path>`: working tree와 HEAD의 tracked file 변경만 잡는 보조 검증.
  - 두 명령은 서로 다른 누락 시나리오를 커버하므로 redundancy는 의도된 safety net이다. 단순화하지 않는다.
- **Pulse wrapper untouched 검증의 stdout/stderr 규칙** (v6.0 신설):
  - 통과 조건은 **stdout 기준 빈 출력 + `$LASTEXITCODE -eq 0`**이다.
  - stderr는 판정에 사용하지 않는다. 일부 환경에서 `git`이 known warning (예: `warning: unable to access 'C:/Users/MW/.config/git/ignore'`) 을 stderr로 출력해도, 변경 사실은 stdout에 반영되므로 stdout 기준만 본다.
  - stderr에 출력된 known git warning은 PASS/FAIL 판정에 영향을 주지 않되, `phase9b_runtime_split_note.md`의 환경 이슈 절에 별도 기록한다 (재현/디버깅용).
  - 자동화 예시:

    ```powershell
    $statusOut = (& git status --short -- 'Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/' 2>$null)
    $statusExit = $LASTEXITCODE
    $diffOut = (& git diff --name-only HEAD -- 'Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/' 2>$null)
    $diffExit = $LASTEXITCODE
    $pulseWrapperPass = ([string]::IsNullOrWhiteSpace($statusOut) -and [string]::IsNullOrWhiteSpace($diffOut) -and $statusExit -eq 0 -and $diffExit -eq 0)
    ```

Manual QA Requirement: **필수**. 미수행 시 `implemented_only`로만 closeout 가능 (§12 참조).

#### Manual QA Trigger Criteria

다음 중 하나 이상에 해당하면 manual in-game QA가 필요하다.

- runtime UI module 분리.
- Browser/Wiki/Tooltip 표시 경로 변경.
- 한국어 표시 문구 포함 module 수정.
- public caller가 쓰는 function signature 변경.
- compatibility wrapper disposition 변경.
- bootstrap/dispatch module 변경 (v3.0 추가, `IrisMain.lua` INIT_MODULES 변경 포함).

Change 9b는 위 6개 trigger 중 최소 2~3개에 항상 해당하므로 manual QA는 본 Change 한정으로 강제된다.

#### Manual QA Checklist Schema (v3.0 baseline 촬영 시점 명시)

`phase9b_manual_qa_checklist.md`는 다음 행을 모두 포함한다.

| Field | 의미 |
| --- | --- |
| `surface` | `Browser` / `Wiki` / `Tooltip` / `Bootstrap` (`Bootstrap`은 IrisMain 변경 검증용) |
| `scenario` | 비교 대상 표시 시나리오 (item id + 진입 경로, Bootstrap은 KO/EN mode 진입 sequence) |
| `baseline_screenshot` | Change 9b 진입 commit **이전** (entry gate deliverable 시점) 캡처 경로 |
| `baseline_capture_commit` | baseline 촬영 시점의 HEAD commit SHA |
| `post_change_screenshot` | Change 9b 적용 후 캡처 경로 |
| `post_change_commit` | 비교 대상 commit SHA |
| `comparison_result` | `identical` / `expected_diff` / `regression` |
| `tester` | QA 수행자 (default: 사용자) |
| `verdict` | `PASS` / `FAIL` |

규칙:

- `baseline_screenshot`은 본 Change의 첫 코드 commit이 만들어지기 **전에** 촬영해야 한다. 진입 후 촬영분은 baseline으로 인정되지 않는다.
- baseline ↔ 진입 commit 순서 판정은 다음 명령으로 수행한다 (v4.0 정정 — Git SHA 문자열 `<` 비교는 시간순/조상 관계를 보장하지 않으므로 제거. v5.0 `$LASTEXITCODE` 접근 패턴 명시):

  ```powershell
  git merge-base --is-ancestor $baselineCommit $firstCodeCommit
  $ancestorExit = $LASTEXITCODE
  $baselineSha = (git rev-parse $baselineCommit).Trim()
  $firstCodeSha = (git rev-parse $firstCodeCommit).Trim()
  $sameSha = ($baselineSha -eq $firstCodeSha)
  $verdict = if ($ancestorExit -eq 0 -and -not $sameSha) { 'PASS' } else { 'FAIL' }
  ```

  PowerShell에서 native exe 호출의 exit code는 `$LASTEXITCODE`로만 신뢰할 수 있다 (`$?`는 native exit code의 0/1 차이를 보존하지 않을 수 있다 — 머리말 PowerShell 표기 규약 참조).
- `$ancestorExit -eq 0` (= baseline이 진입 commit의 ancestor) 이고 `$sameSha -eq $false` 일 때만 `baseline_capture_commit`이 유효하다.
- `baseline_capture_commit`이 누락되거나, `$ancestorExit -ne 0` 또는 `$sameSha -eq $true` 이면 checklist 행은 `FAIL`로 간주한다.
- 모든 행이 `PASS`일 때만 `complete` 가능. `regression` 또는 `FAIL` 1건이라도 발견되면 `implemented_only` 또는 revert.

#### Validation (Phase 9b)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| 9a validation 전수 재실행 | §Change 9a Validation 표 | 모두 PASS | 1건 이상 FAIL | 즉시 revert |
| IrisMain syntax + require | `luac -p Iris\media\lua\client\Iris\IrisMain.lua` + KO mode boot smoke | exit code 0 + `[Iris] Bootstrap complete` 메시지 | exit code != 0 또는 메시지 부재 | 즉시 revert |
| Require path enumeration | `Get-ChildItem Iris\media\lua -Filter *.lua -Recurse -File \| Select-String -Pattern 'require.*IrisWikiSections|require.*IrisBrowserInteractionRenderer'` | 모든 caller가 새 require path를 가리킴 | 옛 path 잔존 | caller 갱신 commit 추가 또는 revert |
| Pulse wrapper untouched | `git status --short -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/` + `git diff --name-only HEAD -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/` (역할 분담·stdout/stderr 규칙은 Implementation Notes 참조) | 두 명령 모두 **stdout 기준 빈 출력** + 각 호출 후 `$LASTEXITCODE -eq 0` | 어느 하나라도 stdout 출력 존재 또는 `$LASTEXITCODE -ne 0` | 즉시 revert (본 Change scope 위반) |
| Manual QA matrix | Manual: `phase9b_manual_qa_checklist.md` + 다음 자동 실행 (v5.0 `$LASTEXITCODE` 명시): `git merge-base --is-ancestor $baselineCommit $firstCodeCommit; $ancestorExit = $LASTEXITCODE; $sameSha = ((git rev-parse $baselineCommit) -eq (git rev-parse $firstCodeCommit))` | 모든 행 `verdict = PASS` + `$ancestorExit -eq 0` + `$sameSha -eq $false` | `FAIL` 또는 `regression` 존재 또는 `$ancestorExit -ne 0` 또는 `$sameSha -eq $true` | `implemented_only`로 강등 또는 revert |
| Test baseline | `python -B -m unittest discover ...` (§7 parser) | `OK`, ≥ `baseline_test_count` | `FAILED` | 마지막 commit revert |

Expected Closeout: manual QA 전수 PASS + `git merge-base --is-ancestor` exit 0 + baseline ↔ 진입 SHA 비동일 충족 시 `complete`. manual QA 미수행/미완료 또는 ancestor 명령 실패 시 `implemented_only` (merge/release/behavior-preserving claim 불가). regression 발견 시 revert.

---

### Change 10 — Phase 10: Test Discovery and Validation Surface Normalization

Purpose:

- root build tests, description v2 tests, script-style checks의 discovery policy를 명확히 한다.

Entry Gate: Phase 1 `complete`.

Files:

- Modify: import-time `sys.exit()` style checks → unittest-compatible 형태 (Phase 1 grep 결과 기반)
- Update: `Iris/build/build_import_contract.md` (test discovery scope 명시)
- Create: `docs/Iris/phase10_validation_matrix.md` (phase별 validation command 정리 — Change 1~9b 표를 통합)
- Create: `docs/Iris/phase10_test_discovery_compatibility_note.md`

Implementation Notes:

- pytest/unittest discovery scope를 import contract와 일치시킨다.
- import-time exit를 사용하는 historical script-style checks는 direct execution target으로 분리하거나 unittest로 전환 (low-risk만).
- validation command matrix는 본 계획 전체 phase의 self-check 도구로도 쓰인다.
- Phase 10이 12개 Change 중 마지막에 있는 이유는 minimal diff preservation (§11 운영 원칙) — Change 1~9b를 통과한 명령을 그대로 통합 매트릭스로 굳히는 흐름이 가장 작은 변경이기 때문이다.

#### Validation (Phase 10)

| Item | Command (PowerShell, manual step은 "Manual:" 접두) | Expected | Failure Criteria | Rollback Trigger |
| --- | --- | --- | --- | --- |
| unittest discover | `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` (§7 parser) | `OK`, 통과 수 ≥ `baseline_test_count` (§7 Test Baseline Update Rule 참조) | `FAILED` | 마지막 commit revert |
| Root build tests | Phase 1이 enumerate한 root test 전수 | `OK` | `FAILED` | 즉시 revert |
| pytest | `pytest Iris/build/description/v2/tests` (설치/설정된 경우에만) | `passed` 또는 skip 명시 | `failed` | 즉시 revert |
| Validation matrix dry run | Manual: `phase10_validation_matrix.md` 수동 검토 | Change 1~9b 행 모두 포함 + 사용된 명령 PowerShell 호환 + `__pycache__`/`_archive`/`historical` 3-filter 제외 규칙이 다른 phase와 일관 (v6.0 정정 — 이전 2-filter 누락) | 누락 행 또는 호환 불가 명령 또는 3-filter 정렬 불일치 | matrix 보강 |

Expected Closeout: `complete`.

---

## 7. Validation Plan

### Automated Validation

각 Change §Validation 표가 1차 진리이며, 본 절은 전 계획 공통 항목과 운영 규칙을 정의한다.

- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` (`baseline_test_count` 유지/갱신, Test Baseline Update Rule 참조).
- `python -B Iris/build/quality_gates.py` (Change 4 이후에는 split 모듈 진입, 그 전에는 기존 단일 파일).
- `python -B Iris/build/recipe_evidence_pipeline.py`, `python -B Iris/build/rightclick_evidence_pipeline.py --v24` (Change 5 이후).
- `Get-FileHash` 기반 artifact SHA 비교 (`Iris/build/description/v2/output/**`, `Iris/output/**`, §5 Generated Artifacts 전수).
- `git ls-files`, `git status --short`, `git diff --stat` 기반 inventory delta 검증.
- `Get-ChildItem -Recurse -File ... | Select-String -Pattern ...` 기반 정량 metric 측정 (PowerShell 표기 규약 머리말 참조).
- `git diff --no-index <before> <after>` 기반 schema/report 비교 (Change 4 이후 nested PSCustomObject 한계 회피).

### Manual Validation

- **Phase 9b 한정**: KO mode boot playtest, Browser / Wiki / Tooltip / Bootstrap surface 캡처 비교 (`phase9b_manual_qa_checklist.md` schema 충족, baseline은 `git merge-base --is-ancestor`로 진입 commit 이전임을 자동 검증).
- **Phase 9a/9b 한정**: `[Iris] Bootstrap complete` console 출력 확인 (runtime require smoke). v4.0 범위 한정 — runtime Lua 변경이 없는 Phase 1~8/10은 본 manual smoke 대상이 아니다.
- Phase 7b: per-directory disposition table 수동 검토 + 이동 후 grep 결과 확인.
- Phase 1: conflict resolution gate 문서 + baseline metrics 문서 + path existence 결과 수동 검토.

### Test Baseline Update Rule (v3.0 parser 명시)

`baseline_test_count`는 Phase 1에서 측정해 봉인된다. 측정 명령과 parser 규칙은 다음과 같다.

```
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py" -v 2>&1
```

위 명령의 마지막 출력 블록에서 `Ran N tests in <time>s` 행의 `N`을 정수로 파싱한다. 이후 `OK` 또는 `FAILED (failures=...)` 표시가 동일 블록에 있어야 측정으로 인정한다.

PowerShell 추출 예시:

```powershell
$out = & python -B -m unittest discover -s 'Iris/build/description/v2/tests' -p 'test_*.py' -v 2>&1
$ranLine = ($out | Select-String -Pattern '^Ran (\d+) tests in ' | Select-Object -Last 1)
$baselineTestCount = if ($ranLine) { [int]$ranLine.Matches[0].Groups[1].Value } else { $null }
$status = ($out | Select-String -Pattern '^(OK|FAILED)' | Select-Object -Last 1).Matches[0].Groups[1].Value
```

`$status`가 `OK`일 때만 `$baselineTestCount`를 baseline으로 봉인한다. `FAILED`이면 측정 실패로 간주하고 Phase 1을 `blocked`로 강등한다.

갱신 규칙:

- **갱신 가능**: Phase 5 evidence skeleton 또는 Phase 10 test normalization으로 인해 의도된 신규 테스트가 추가/통합된 경우. 갱신 시 `phase1_baseline_metrics.md`에 amendment entry (이전 값, 새 값, 갱신 사유, 갱신 commit hash, parser 출력 sample)를 기록.
- **갱신 불가**: 단순 helper extraction, consolidation, runtime cleanup, archive sweep 등으로 인한 test count 감소. 이 경우 closeout 보류 + 원인 조사.
- 갱신은 단일 Change 안에서 최대 1회만 허용. 다회 갱신 필요 시 별도 round.

### Approved Diff Procedure (v3.0 surface 분류 추가)

`approved diff`는 SHA drift를 허용하기 위한 명시 절차로만 사용한다. 회피 경로로 쓰이지 않도록 다음 필드를 모두 기록한다.

`docs/Iris/approved_diff_log.md` (신규, 누적 로그):

| Field | 의미 |
| --- | --- |
| `entry_id` | UUID 또는 일련번호 |
| `change` | Change 번호 (1~10, 7a/7b/9a/9b 포함) |
| `artifact` | drift 대상 artifact 경로 |
| `surface` | §8 분류 (`authority` / `runtime` / `compat` / `sealed_artifact` / `public_facing`) 또는 `build_only` (v6.0 추가 — build-only intermediate artifact용. §8 surface 분류에 속하지 않는 일반 build output / intermediate JSONL 등). v3.0 추가 / v6.0 enum 확장 |
| `before_sha` | 변경 전 SHA-256 |
| `after_sha` | 변경 후 SHA-256 |
| `diff_reason` | drift가 발생한 의도 (helper 도입, schema 변경 등) |
| `schema_or_behavior_impact` | `none` / `schema-only` / `runtime-impact` |
| `reviewer` | `self` 또는 `사용자` — surface별 제약은 아래 규칙 참조 (v5.0) |
| `sign_off_date` | 날짜 |
| `closeout_note_reference` | 해당 phase closeout note 링크 |

규칙:

- `runtime-impact`가 명시되면 Phase 9b manual QA가 강제된다 (`surface = runtime` 또는 `public_facing` 자동 매핑).
- `surface = sealed_artifact` entry는 §10 Rollback Plan의 sealed artifact SHA drift 절차와 cross-reference한다.
- `surface = compat` entry는 §11 Compatibility wrapper 제거 금지 원칙을 위반하지 않는 범위 안에서만 허용한다.
- **`reviewer` 제약 (v5.0 신설, v6.0 보강)**:
  - `surface = sealed_artifact`, `runtime`, `public_facing`, `compat` 인 entry는 **`reviewer = 사용자`만 허용**한다. `reviewer = self`는 금지된다. 사유: 이들 surface는 §10 Rollback Plan에서 drift 발견 시 즉시 중단/rollback 대상이므로, self-approved diff가 들어가면 rollback gate와 충돌해 sealed artifact mutation 또는 silent compatibility break가 통과될 수 있다.
  - `surface = authority` 인 entry는 §8에서 controlled concern으로 분류되어 있으므로 기본 `reviewer = 사용자`이지만, authority ownership 이동이 없는 helper-level drift에 한해 `reviewer = self` 가능. 이 경우 **다음 minimum evidence 3종을 `diff_reason`에 함께 명시해야 한다** (v6.0 신설 — self-judgment 회피):
    1. **Track ownership grep 결과**: drift 대상 artifact가 Recipe / Right-click evidence track 어느 한쪽의 source-of-truth가 아님을 grep으로 보인 결과 경로/라인 (예: `Iris/build/recipe_evidence_pipeline.py` / `rightclick_evidence_pipeline.py` 안에서 해당 artifact가 직접 작성/소비되지 않음).
    2. **Authority ownership reference**: `docs/Iris/Iris_Refactoring_Roadmap.md` §7 Authority Surface 또는 본 계획 §8 Authority Surface 절의 인용 (artifact가 controlled concern으로 분류되어 있으나 ownership 이동이 본 drift 범위 밖임을 보이는 인용).
    3. **No facts/decisions/profiles/render 흐름 영향 명시**: §11 governing constraints의 `facts → decisions → profiles → render` 흐름과 SHA 무결성, `fact_origin` 추적에 본 drift가 영향을 주지 않음을 한 줄로 단언 (영향 가능성이 1%라도 있으면 self carve-out 불가, 사용자 reviewer 필수).

    위 3종 중 1건이라도 누락되면 self carve-out 적용 불가 → `reviewer = 사용자` 필수.
  - `surface = build_only` (v6.0 신설 enum) entry는 `reviewer = self` 자유 허용. 단 surface 분류가 build-only가 맞는지 (= sealed/runtime/compat/public_facing/authority 어디에도 속하지 않는지) 는 entry 작성 시 self-check 필요.
- `reviewer = self`가 금지된 surface에 self entry가 발견되면 해당 phase closeout은 즉시 `blocked`로 강등되고, entry 재작성 + 사용자 sign-off 후에만 재진입한다.
- `surface = authority` self carve-out entry에 minimum evidence 3종 중 1건이라도 누락된 경우도 동일하게 `blocked`로 강등된다 (v6.0).
- 본 절차 미준수 시 closeout 통과 불가.

### Validation Limits

- no release readiness validation.
- no Workshop deployment validation.
- no B42 readiness validation.
- no full external ecosystem compatibility sweep.
- no long-session runtime validation.
- no multiplayer validation.
- no modpack compatibility validation.
- no full runtime equivalence claim without manual in-game QA (Phase 9b 한정 manual QA 외).
- no sealed artifact mutation claim unless explicitly performed and validated.
- no deployment/package publishing validation.
- no build-time performance validation.
- no public-facing 문구/한국어 설명 변경 validation (non-goal).
- no `implemented_only` 상태에서 behavior-preserving / merge / release claim.

---

## 8. Risk Surface Touch

### Authority Surface

**Concerns controlled**.

- build helper extraction, family consolidation, stage skeleton sharing은 authority ownership 이동이 아니다.
- Evidence skeleton refactor (Change 5)와 artifact/source classification (Change 1/8)은 authority-adjacent 작업이므로 None이 아닌 controlled concern으로 둔다.
- Recipe / Right-click evidence decision authority는 track별로 유지된다.
- 본 계획 실행이 authority-bearing artifact를 수정할 경우 별도 scope lock + disclosure가 필요하며, 그 시점에 본 문서를 amendment한다.

### Runtime Behavior Surface

**Concerns** (Phase 9a low / Phase 9b high).

- Phase 1~8, Phase 10은 build-only 또는 doc-only로 runtime behavior impact를 제한한다. output hash equivalence로 입증.
- Phase 9a는 behavior-neutral 한정으로 manual QA 면제 (Generator/Renderer debug 축소).
- Phase 9b는 IrisMain INIT_MODULES helper 흡수 + IrisWikiSections + IrisBrowserInteractionRenderer 분할을 다루므로 syntax/require/manual QA boundary가 필요.
- user-facing behavior change는 manual in-game QA 없이 성공 주장 금지.

### Compatibility Surface

**Concerns**.

- direct script execution baseline (conflict 14.2).
- public `IrisAPI`.
- Pulse namespace compatibility wrapper 6개 파일 (`Pulse/Iris/Logic/IrisDesc/*.lua`).
- compose module entrypoint.
- compatibility wrapper 제거/변경은 deprecation decision 또는 compatibility window 없이는 본 계획에서 실행하지 않는다 (Change 9b는 disposition note만 작성).

### Sealed Artifact Surface (v3.0 경로 정정)

**Concerns**.

- generated data, frozen SHA, current readpoint, staging evidence는 sealed 또는 evidence-adjacent surface.
- §5 Generated Artifacts에 enumerate된 모든 항목 — 특히 `Iris/Data/IrisLayer3DataChunks.lua` + 11 chunks, `IrisUseCaseDescriptions.lua` + 9 chunks + `RequirementsLookup.lua`, `IrisClassifications.lua`, `IrisRecipeIndex.lua`, `IrisMoveablesIndex.lua`, `IrisFixingIndex.lua`, `layer3_renderer.lua` — 는 SHA comparison 또는 approved diff 없이 mutation하지 않는다.
- Phase 1, 7a/7b, 8의 분류 작업이 sealed evidence를 untracked/disposable로 오판하지 않도록 disposition 표 (§6 Change 7b Schema)를 단일 진리로 사용.

### Public-Facing Output Surface

**Conditional concerns** (Phase 9b 시 concerns, 그 외 None).

- Browser/Wiki/Tooltip 표시 문구나 구조를 바꾸는 execution은 본 계획 범위 외이며, 발견 시 별도 round로 분리.
- 한국어 설명 문구 변경은 non-goal.
- Phase 9b는 책임 분할 + IrisMain helper 흡수에 한정되며 표시 문구/구조 변경은 금지. manual QA로 보장.

---

## 9. Risk Analysis

### Architecture Risk

- batch1 import 해소 누락으로 dual-import wrapper가 영구화되어 기술 부채 누적 (mitigation: wrapper 코멘트에 마감 일자 명시, Change 2 closeout 정량 기준 `batch1_import_count == 0`).
- compose import dance 제거 방식과 direct script execution baseline 보존이 충돌해 contract drift 발생 (mitigation: conflict 14.2 entry gate).
- `quality_gates.py` split이 reporting schema drift를 일으켜 후속 phase validation이 무의미해짐 (mitigation: Change 4 `git diff --no-index` 기반 schema diff validation).
- evidence pipeline skeleton 공통화가 Recipe / Right-click 의미 체계를 섞어 authority separation 위반 (mitigation: cross-track fixture validation).
- IrisMain helper 흡수 (Phase 9b)가 INIT_MODULES spec 복잡도를 증가시켜 build/runtime boundary가 약화됨 (mitigation: 동치성 유지 최소 변경 + manual QA Bootstrap surface).

### Runtime Risk

- Phase 9b runtime Lua 변경 (IrisMain + UI splits)이 Browser/Wiki/Tooltip 표시를 깸 (mitigation: manual QA checklist Bootstrap surface 포함 + entry gate baseline 시점 규칙).
- Generator/Renderer debug line 축소로 진단 능력 저하 → 후속 incident에서 trace 부족 (mitigation: trace mode 분리 옵션 검토, Change 9a closeout 정량 기준).
- Pulse compat wrapper 6개 파일 변경이 외부 require 경로를 깸 (mitigation: 본 계획에서 제거 금지, disposition note만).

### Compatibility Risk

- direct script execution baseline이 conflict 14.2 결정 전에 깨짐 → 외부 reproduction 손상 (mitigation: Change 3 entry gate).
- version/path manifest migration (Change 6)이 historical oneshot script의 reproduction path를 손상 (mitigation: 예외 문서화, `_archive`/`historical` 제외 grep 규칙).
- test discovery normalization (Change 10)이 default 실행 test 집합을 바꿔 CI/release gate와 충돌 (mitigation: Test Baseline Update Rule + parser 명시).
- archive movement (Change 7b)가 hard-coded staging path를 보유한 build script를 깸 (mitigation: per-directory disposition + staging path grep).

### Regression Risk

- consolidation (Change 7a) 후 output drift (mitigation: 후보별 SHA 비교 + hidden branch detection).
- helper migration (Change 2) 중 common constant/function 누락으로 build 실패 (mitigation: family direct script smoke).
- ROOT/sys.path bootstrap cleanup 중 import cycle (mitigation: path helper leaf module 유지).
- sealed evidence를 untracked/disposable로 오판해 SHA drift 발생 (mitigation: disposition schema의 `evidence_type` 필드 + §5 진리 목록).
- `baseline_test_count` 침범 (mitigation: Test Baseline Update Rule + `Ran N tests` parser).

### Operational Risk

- 12-Change 계획이 크다. partial closeout이 누적되면 상태 추적이 흐려질 수 있다 (mitigation: 각 Change closeout note + §12 의미 분리).
- Windows/PowerShell 환경 외에서 본 계획을 실행할 경우 명령 비호환 발생 가능 (mitigation: PowerShell 표기 규약 머리말 + `Get-ChildItem -Recurse -File | Select-String` 일관 패턴).
- `Select-String -Recurse` 같은 미지원 파라미터 사용 위험 (mitigation: v3.0에서 전수 정정).

### Validation Risk

- approved diff procedure가 회피 경로로 쓰일 수 있음 (mitigation: §7 Approved Diff Procedure schema + `surface` 필드).
- `implemented_only`가 merge/release claim으로 오용 (mitigation: §12 closeout state semantics).
- manual QA trigger 누락 (mitigation: §6 Change 9b Manual QA Trigger Criteria, bootstrap/dispatch trigger 추가).
- nested PSCustomObject schema drift 미감지 (mitigation: Change 4 `git diff --no-index --exit-code` + JSON canonical Python one-liner).
- baseline screenshot 사후 촬영 (mitigation: v4.0 `git merge-base --is-ancestor <baseline_capture_commit> <first_code_commit>` exit 0 + 두 SHA 비동일성 — SHA 문자열 `<` 비교는 시간순/조상 관계를 보장하지 않으므로 제거됨).

### Governance Risk

- governing docs에서 명시 인용되지 않은 운영 원칙 사용 (mitigation: §11에서 "본 plan 운영 원칙"으로 라벨링, §4 Assumptions에도 동일 표기).
- gate enforcement 약함 (mitigation: §6 Change 1 Conflict Resolution Gate Schema).

---

## 10. Rollback Plan

- 각 Phase/Change는 독립 commit 또는 batch commit으로 구현하며, phase 경계에서 `git revert <commit>` 으로 단일 phase를 복원할 수 있다.
- Change 7a는 후보 1건당 1 commit을 유지해 consolidation rollback 단위를 candidate 단위로 최소화한다.
- Change 7b의 모든 이동은 `git mv` 기반이며 disposition table의 `rollback_path` 필드가 역방향 명령을 보유한다.
- build pipeline refactor는 focused validation 통과 전까지 compatibility entrypoint shim (직실행 경로 또는 wrapper)을 유지한다 (마감 일자 코멘트 동반).
- generated artifact 변경은 before/after hash 또는 approved diff entry (§7 Approved Diff Procedure)를 함께 commit해 보존.
- sealed artifact SHA drift가 발견되면 해당 phase를 즉시 중단하고 마지막 known-good commit으로 rollback. §5 Generated Artifacts 목록 + Phase 1 inventory + Phase 8 분류표를 단일 진리로 사용 (v3.0: 실제 경로는 `Iris/Data/IrisLayer3DataChunks.lua` 등).
- runtime Lua 변경 (Phase 9a/9b)에서 Iris Lua error가 발생하면 해당 commit revert + runtime validation 재수행. 이전 module layout과 require path 복원 경로를 commit message에 동봉. Change 9b는 IrisMain 변경과 UI split을 별도 commit으로 분리해 부분 rollback을 가능하게 한다.
- Pulse compat wrapper는 본 계획에서 변경되지 않으므로 rollback 불필요. 변경이 감지되면 그 자체가 scope 위반 → 즉시 revert.
- tracking/ignore policy 변경 (Phase 8)은 inventory manifest를 기준으로 `.gitignore` diff를 역적용해 복구.
- conflict resolution gate (Phase 1 산출물)가 잘못 닫혔다고 판단되면, 해당 phase 진입 전에 gate 문서만 amendment하면 되며 코드 rollback은 불필요.
- Phase 9b에서 manual QA `FAIL`/`regression` 발견 시 closeout을 `implemented_only`로 강등하거나 해당 commit revert. `implemented_only`는 merge/release/behavior-preserving claim에 사용 불가 (§12).
- baseline screenshot이 진입 commit 이후에 촬영되었다고 판정되면 — 즉 `git merge-base --is-ancestor` 호출 후 `$LASTEXITCODE -ne 0` (= ancestor 아님) 이거나 `$baselineSha -eq $firstCodeSha` (= 동일 commit) 이면 — manual QA 결과는 무효이며 baseline을 재촬영한 뒤 Change 9b를 재진입해야 한다 (rollback 대상은 코드가 아니라 manual QA artifact). v4.0: SHA 문자열 `<` 비교는 시간순/조상 관계를 보장하지 않으므로 본 판정에서 제거되었다. v5.0: native exe exit code는 `$LASTEXITCODE`로만 접근한다 (머리말 표기 규약).

---

## 11. Governance Constraints

다음 제약은 모든 Change 실행 중 유지된다.

### Governing Document Source (현행 인용)

- Iris는 100% Lua 기반 위키형 정보 모드로 유지한다. (`docs/Philosophy.md`)
- Iris는 해석, 권장, 비교를 하지 않는다. (`docs/Philosophy.md`)
- runtime/build-time authority 분리를 유지한다. (`docs/ARCHITECTURE.md`)
- FAIL-LOUD validation과 determinism gate를 약화하지 않는다. (`docs/DECISIONS.md`, `docs/ROADMAP.md`)
- generated Lua 또는 generated JSON을 손으로 쪼개거나 의미 수정하지 않는다. (`docs/ARCHITECTURE.md`)
- sealed artifact와 current readpoint를 본 계획 실행으로 mutation하지 않는다. (`docs/DECISIONS.md`)
- `facts → decisions → profiles → render` 흐름, SHA 무결성, `fact_origin` 추적을 보존한다. (`docs/ARCHITECTURE.md`)
- Recipe evidence와 Right-click evidence는 동급의 독립 2-track으로 유지한다. (`docs/DECISIONS.md`, `docs/Iris/Iris_Refactoring_Roadmap.md` §7)
- public Lua API 또는 compatibility wrapper 제거는 deprecation/release decision 없이 진행하지 않는다. (`docs/Iris/Iris_Refactoring_Roadmap.md` §4)
- Pulse 의존성 신설 또는 다른 Pulse module/Core 변경을 하지 않는다. (`docs/Philosophy.md`, `docs/Iris/Iris_Refactoring_Roadmap.md` §4)
- user-facing runtime behavior change는 manual in-game QA 없이 성공으로 주장하지 않는다. (`docs/Iris/Iris_Refactoring_Roadmap.md` §4)
- direct script execution baseline은 conflict 14.2 결정 전까지 깨지지 않는 계약으로 취급한다. (`docs/Iris/Iris_Refactoring_Roadmap.md` §4)

### Plan Operating Principles (본 plan 운영 원칙, 인용 미확인)

다음은 governing docs에서 명시 인용을 확인하지 못한 항목으로, 본 계획의 운영 원칙으로 라벨링한다. 향후 governing docs에 명시되면 인용 출처를 이관한다. §4 Assumptions에도 동일 라벨링을 명시했다.

- **Additive amendment preference**: 기존 문서/decision을 destructive하게 덮어쓰지 않고 amendment 형식으로 누적한다.
- **Minimal diff preservation**: 동일 결과를 만드는 두 변경이 있을 때 더 작은 diff를 선호한다. Change 10이 마지막에 배치된 이유이기도 하다 (§6 Change 10 Implementation Notes).
- **No silent compatibility shim**: 본 계획에서 도입된 dual-import wrapper 또는 호환 shim은 모두 마감 일자 코멘트를 동반한다.

---

## 12. Expected Closeout State

### Closeout State Semantics

본 계획에서 사용하는 closeout 상태는 다음 의미로 고정한다. 상태 간 의미 혼용은 governance violation으로 취급한다.

| State | 의미 | 허용 claim | 불허 claim |
| --- | --- | --- | --- |
| `complete` | 구현 + Change §Validation 표 전수 PASS + 정량 closeout 기준 충족 | 본 Change scope 안에서의 behavior-preserving, determinism, sealed artifact preservation claim | release readiness, deployment readiness, full runtime equivalence (Validation Limits §7) |
| `partial` | 일부 candidate/sub-round 완료. 일부 gate 미해소 또는 잔여 작업 존재 | 진행 상황 보고, 후속 round 트리거 | `complete`가 의미하는 어떤 claim도 불허 |
| `implemented_only` | 구현은 commit됨. validation 또는 manual QA 미수행/미완료 | 코드 변경 자체의 존재 | merge, release, behavior-preserving, behavior-neutral, regression-free claim 모두 불허 |
| `blocked` | conflict gate 미해소 또는 entry gate 미충족으로 진입 자체가 차단 | gate 보강 요청 | 어떤 Change-level claim도 불허 |

`implemented_only`는 **merge 또는 release closeout이 아니다**. Change 9b가 manual QA 없이 commit만 된 경우 본 상태로 머무르며, merge는 manual QA 통과 후에만 가능하다.

### Quantitative Closeout Criteria

각 Change의 `complete` 판정은 §6 §Validation 표 + 다음 정량 기준을 모두 충족해야 한다. baseline 값은 `phase1_baseline_metrics.md` 참조.

| Change | Quantitative Criterion |
| --- | --- |
| 1 | conflict gate 6/6 schema field 충족 + baseline metrics 13/13 측정 완료 (v4.0: chunk count 2종 추가 반영) + §5 Path Existence Verification 전수 `True` + chunk enumerate 측정값이 `baseline_layer3_chunk_count`/`baseline_usecase_chunk_count`로 정수 봉인 + `phase1_active_script_manifest.txt` 한 줄 이상 산출 |
| 2 | `batch1_import_count == 0` (Change 2 전체 `complete` 시) |
| 3 | conflict 14.2 resolved 시 `compose_except_import_count == 0`. ROOT/sys.path count는 baseline 대비 감소 (구체 목표 수치는 Phase 3 진입 시 결정) |
| 4 | quality gate full run PASS + report schema `git diff --no-index` 빈 diff 또는 approved diff 1건만 |
| 5 | recipe/right-click pipeline 양쪽 PASS + cross-track 혼입 0건 |
| 6 | `v24_hardcode_count == 0` (v4.0: `phase1_active_script_manifest.txt` 입력 기반. baseline ↔ closeout 동일 manifest + 동일 필터로 정렬) |
| 7a | consolidation 후보 전수의 artifact SHA 일치 또는 approved diff |
| 7b | disposition table 전수 처리 + `staging_toplevel_count`가 disposition 의도와 일치 + sealed evidence 1건도 archive 외 disposition 없음 |
| 8 | `Iris/output`, `Iris/build/package` classification table 전수 분류 + §5 Generated Artifacts 전수 SHA 변동 0 |
| 9a | `generator_debug_count`, `renderer_debug_count`가 의도된 감소량 도달 + §5 Generated Artifacts SHA 변동 0 (IrisMain 변경 없음 확인 포함) |
| 9b | manual QA checklist 전 행 `verdict = PASS` + `git merge-base --is-ancestor $baselineCommit $firstCodeCommit` 호출 후 `$LASTEXITCODE -eq 0` + `(git rev-parse $baselineCommit) -ne (git rev-parse $firstCodeCommit)` + Pulse wrapper `git status --short` + `git diff --name-only HEAD` 모두 빈 출력 + IrisMain syntax/require smoke PASS |
| 10 | `phase10_validation_matrix.md`가 Change 1~9b 행 전수 포함 + 모든 명령 PowerShell 호환 확인 + `__pycache__`/`_archive`/`historical` 제외 규칙 일관 |

### Per-Change Closeout Expectation

- Change 1 (Phase 1): `complete` (entry gate). 본 계획의 first-mover.
- Change 2 (Phase 2): 일반적 `partial` → 모든 family + `batch1_import_count == 0` 도달 시 `complete`.
- Change 3 (Phase 3): conflict 14.2 `resolved` 시 `complete`, `deferred` 시 `partial` + decision record 유지.
- Change 4 (Phase 4): conflict 14.4가 "추가 split 필요"로 closeout된 시점에만 진입 → `complete`.
- Change 5 (Phase 5): `complete`.
- Change 6 (Phase 6): `complete`.
- Change 7a (Phase 7a): 일반적 `partial` → 모든 승인 후보 완료 시 `complete`.
- Change 7b (Phase 7b): 일반적 `partial` → disposition table 전수 처리 시 `complete`. conflict 14.3 미해소 시 `blocked`.
- Change 8 (Phase 8): `complete`.
- Change 9a (Phase 9a): behavior-neutral 전수 PASS 시 `complete`. conflict 14.6 미해소 시 `blocked`.
- Change 9b (Phase 9b): manual QA 전수 PASS + `git merge-base --is-ancestor` 호출 후 `$LASTEXITCODE -eq 0` + baseline ↔ 진입 SHA 비동일 충족 시 `complete`. manual QA 미수행 또는 `$LASTEXITCODE -ne 0` 또는 두 SHA 동일 (= baseline 사후/동일 촬영) 시 `implemented_only` (merge 불가). conflict 14.5/14.6 미해소 시 `blocked`.
- Change 10 (Phase 10): `complete`.

### Overall Plan Closeout

본 계획의 전체 closeout 기대치: `partial`.

- 12개 Change 모두를 단일 round에서 닫는 것은 비현실적이며, roadmap §14의 6개 conflict가 Phase 1 게이트 산출 이전에는 명시적으로 미결 상태다.
- 실제 round 단위 closeout은 위 표대로 분기되며, 본 문서의 상위 상태는 모든 Change가 `complete`에 도달한 후에만 `complete`로 판정한다. 그 전까지 본 문서는 `partial`로 유지된다.
- `implemented_only` 상태의 Change가 1개라도 남아 있으면 전체 plan은 `partial`을 초과해 `complete`로 판정될 수 없다.
