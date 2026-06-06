# Iris Worktree Cleanup Implementation Plan

> 기준일: `2026-06-05`
> 버전: `v0.9`
> 상태: pre-execution consistency fixes (sixth round)
> 상위 기준: `docs/Philosophy.md` > `docs/DECISIONS.md` > `docs/ARCHITECTURE.md` > `docs/ROADMAP.md`
> 선행 근거: `docs/Iris/iris-worktree-cleanup-roadmap.md` (Final Draft, 2026-06-05)
> 약칭: `IWC`
>
> **참고**: 본 plan 본문의 cross-reference 는 section + sub-anchor 기반 (예: "§10 안전 조건", "§6 Phase 6 가드 명령 처리"). 라인번호는 revision 마다 누적 drift 가 발생하므로 본문 내 inline 참조에 사용하지 않는다. 아래 revision summary 의 라인번호는 각 revision 시점의 historical 기록이며 이후 revision 에서 drift 됐을 수 있다.

> v0.9 revision summary (sixth review + self-review consolidation):
> - §6 Phase 6 status 명령 처리 (2곳, Implementation Notes 와 Validation): generic "blocked validation state" → "status blocked validation state" 로 정렬 (v0.8 의 §7 / §9 신규 naming 과 일치).
> - 본문 inline 라인번호 cross-reference 3건 (§6 Phase 4 Validation, §9 Compatibility Risk, §10 Phase 4 rollback) 을 section + sub-anchor 기반으로 교체. 라인번호 drift 의 구조적 문제 해소.
>
> v0.8 revision summary (fifth review + self-review consolidation):
> - §6 Phase 4 Validation archive entry count: PowerShell 5.1 fresh session 에서 `[System.IO.Compression.ZipFile]` 타입이 기본 미로드 → `Add-Type -AssemblyName System.IO.Compression.FileSystem` 을 코드블록 첫 줄에 추가. 본 환경에서 Add-Type 누락 시 `Unable to find type` 실측 확인됨.
> - §6 Phase 6 line 445 static SHA pair check 표현: "보편 재현 가능" → §4 line 150 과 동일하게 "main 작업트리 권한 컨텍스트에서 재현 가능 — main repo 자체의 `safe.directory` 가 통과한 셸에서만" 으로 정렬.
> - §9 Compatibility Risk: dangling 디렉토리 risk 항목에 가드 명령 자체의 safe.directory 실패 모드 추가 ("guard blocked validation state" 처리).
> - §9 Regression Risk: blocked validation state 를 "guard blocked" 와 "status blocked" 로 구분 표기.
> - §10 Phase 4 rollback `Expand-Archive` 맥락 단서 추가 (staging 복원 목적, 검증용 temp dir 패턴과 다름).
>
> v0.7 revision summary (fourth review + self-review consolidation):
> - §6 Phase 4 Validation: archive entry count 대안 명령 (`Expand-Archive + Remove-Item -Recurse -Force <tmp>`) 제거. `[System.IO.Compression.ZipFile]::OpenRead(...).Entries.Count` 만 채택 (§10 의 디렉토리 단위 destructive 명령 금지 규칙과 정합).
> - §6 Phase 4 Bucket D 후보 목록: 본 환경 실측 (2026-06-05) 기준 정확 상위 5개로 갱신. 추가: `structural_signal_authority_classification_round/phase6_remediation/post_remediation_writer_reachability_matrix.jsonl` (33 MB). 제거: `phase2_inventory/occurrence_inventory.jsonl` (25 MB, rank 7 비-탑5). 목록은 "예시, non-exhaustive" 가 아닌 환경 실측. Phase 1 매니페스트가 권위적 목록.
> - §6 Phase 6 line 411: worktree 가드 명령 자체의 safe.directory 실패 처리 명시. 가드 실패 시 → "guard blocked validation state" 로 별도 분류.
> - §7 Automated Validation: 가드 명령 동일 처리 명시.
> - §4 Assumptions line 143 ("보편적으로 재현 가능"): main 작업트리 권한 컨텍스트에서 재현 가능으로 조건 명시.
>
> v0.6 revision summary (third review + self-review consolidation):
> - §6 Phase 4 Validation: `Expand-Archive -PassThru` 제거 (PowerShell 5.1 미지원). `[System.IO.Compression.ZipFile]::OpenRead($archive).Entries.Count` 만 채택하거나 `Expand-Archive` 후 `Get-ChildItem ... -Recurse -File | Measure-Object` 로 대체.
> - §6 Phase 6 merge 확인 명령 (line 399): 각 `rev-parse` 직후 `$LASTEXITCODE` 가드 추가. rev-parse 실패 시 ancestor 판정 중단.
> - §6 Phase 6 line 402 + §4 Assumptions line 134: 사전 검증 사실을 **static SHA pair check** (`git merge-base --is-ancestor 6c12bef b904933` = EXIT 0) 와 **실제 worktree 명령** (`git -C .claude\worktrees\loving-newton-6327e6 ...` 은 환경에 따라 `safe.directory` 로 EXIT 128 가능) 으로 분리 표기.
> - §9 Compatibility Risk: `git check-ignore -v` → `git check-ignore -v -n` 으로 §6 Phase 1 / §7 와 정합.
> - §6 Phase 4 Bucket D 예시: 실제 측정 결과 (`static_report_label_cleanup_round/phase{1,2}_*.json`, `structural_signal_authority_classification_round/`) 로 교체.
> - §5 Generated Artifacts `_tmp_*` 항목: §6 Phase 5 의 조건부 처리에 맞춰 "(조건부, Phase 1 매니페스트 확인 시)" 명시.
>
> v0.5 revision summary (pre-execution consistency fixes):
> - §10 Rollback 안전 조건에 dangling 디렉토리 예외 명시 (inventory + hash + archive + 사용자 승인 통과 후 `Remove-Item -Recurse -Force` 허용).
> - 남은 `tar` 표현 모두 `external zip archive` 계열로 통일 (line 32, 99, 300, 322, 463, 514, 555).
> - §8 Runtime Behavior Surface 의 `Chunk{002..011}.lua` brace 표기 → 명시 리스트.
> - §6 Phase 2 Files 의 `Chunk{002,003,004,005,007,008,010,011}.lua` brace 표기 → 명시 리스트.
> - Phase 6 merge-base 검증 placeholder → 실제 명령 형태 + exit code 기록 기준.
>
> v0.4 revision summary (self-review consolidation):
> - Phase 4 archive 포맷 결정: `.zip` (PowerShell `Compress-Archive` native) 으로 변경. zstd 외부 도구 가정 제거.
> - Phase 4: archive 생성 명령 명시 (PowerShell `Compress-Archive`).
> - §4 Assumptions: JSON 인코딩 (UTF-8 BOM-less) + commit 순서 가정 명시.
> - §2 stale 카운트 정정 (9 → 10), brace 표기 → 명시 리스트.
> - §5 Config: `.claude/settings.local.json` 의 기본 제외 정책 반영 (v0.2 변경의 §5 누락분).
> - §2 Out of Scope: "내부 미커밋 작업 자체 정리" 의미 명확화 (content 자체 수정 ≠ 디렉토리 통째 외부 백업 후 제거).
> - §6 Phase 2: Chunk Lua 도 line-ending vs content diff 식별 대상에 추가.
> - §6 Phase 5: `_tmp_*` 디렉토리 조건부 처리 (실제 존재 시에만).
> - §6 Phase 6: commit 순서 A → B → C 명시 + `loving-newton-6327e6` 의 main ancestor 사실 (`6c12bef`) 반영.
> - §10: `git reset` 문법 모호성 제거 (`git restore --staged` 로 통일 권장).
> - §12: "Phase 1 ~ 5 단일 실행 complete" 표현 완화 (Unclassified 가능성 반영).
>
> v0.3 revision summary (review-driven, second round):
> - Phase 1: `git status --ignored --short` 및 `git check-ignore -v -n` 도입으로 ignored 파일 (`build_static_report_label_cleanup_round.py`) 가시화 보장
> - Phase 6: `git -C <path> status` 가 `safe.directory` dubious ownership 으로 실패할 경우 **blocked validation state** 로 분류 (worktree 상태 실패 아님)
> - Phase 6: dangling 디렉토리 (`sad-dewdney`) 처리에 Get-ChildItem 기반 inventory + file count/size/hash manifest + external archive hash + 명시 사용자 승인 gate 추가
> - §7: `check-ignore` 명령에 `-v -n` 도입 + 출력 해석 semantics 명시 (`!` 접두 = whitelist, 접두 없음 = ignored, `:::` = 매칭 없음)
>
> v0.2 revision summary (first review):
> - validator 명령에 필수 인자 `--manifest`, `--repo-root` 보강 (Phase 2 / 6 / §7)
> - `sad-dewdney`를 dangling 디렉토리로 재분류, registered worktree와 분리 처리
> - Phase 4: 외부 zip archive 외에 tracked cleanup manifest (archive sha256 + per-round disposition) 산출물 추가
> - Phase 4 / 5 검증 명령을 PowerShell 환경으로 정합화
> - Commit B에 명시적 Chunk 리스트로 교체 (brace 표기 제거)
> - Rollback에서 `git restore` / `git reset` 사용 조건 강화 (manifest-owned + 명시 승인)
> - `build_static_report_label_cleanup_round.py` 보류 분류 명시
> - `.gitignore` 화이트리스트 카운트 정정
> - `.claude/settings.local.json` 기본 commit 제외 정책 명시

---

## 1. Objective

Iris 작업트리에 DVF 3.3 다회차 작업 이후 누적된 표면들을 path-class 기반으로 분류·보존·정리하고, 미커밋된 신규 build tool / validator / test / 보조 스크립트 및 기존 implementation·runtime·docs 변경을 검증된 의미 단위로 봉인 가능한 상태로 만든다.

본 plan은 broad ignored-file cleanup, glob 기반 build script 삭제, source/runtime/package output mutation을 사용하지 않는다. validation command가 exit code 0으로 끝난 경우에만 commit readiness를 판정하며, commit 자체의 실행은 본 plan의 mandatory deliverable이 아니라 Phase 6의 결과 기반 결정 항목으로 둔다.

---

## 2. Scope

본 plan은 선행 roadmap의 6개 phase를 그대로 따라간다.

- Phase 1 — Worktree Surface Inventory / Cleanup Manifest
- Phase 2 — Core Change Preservation
- Phase 3 — Documentation And Governance Surface Handling
- Phase 4 — Staging Evidence Disposition
- Phase 5 — Targeted Cleanup Execution
- Phase 6 — Commit Readiness / Worktree Triage / Final Validation

대상 표면:

- tracked implementation 변경 (`compose_layer3_*`, `test_compose_layer3_text_v2.py`, `dvf_3_3_decisions.jsonl`)
- tracked runtime generated data: 수정된 Chunk 8개 (`Chunk002`, `003`, `004`, `005`, `007`, `008`, `010`, `011.lua`. 미수정 `Chunk001/006/009` 는 범위 외)
- tracked UI Lua (`IrisContextMenu.lua`, `IrisWikiPanel.lua`)
- tracked governance docs (`ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`)
- tracked deleted docs (3개 plan, `docs/Iris/` → `docs/Iris/Done/` 이동 쌍)
- untracked build tool / validator / test / 보조 스크립트 (총 10개 = 2 build whitelist + 2 validator whitelist + 4 test whitelist + 1 build non-whitelist (`build_static_report_label_cleanup_round.py`) + 1 ps1)
- untracked `docs/Iris/Done/` plan/review/closeout/walkthrough 추가분
- untracked staging tree (1,818 files / 464 MB)
- `.gitignore` 화이트리스트 변경
- `.claude/worktrees/loving-newton-6327e6`, `.claude/worktrees/sad-dewdney`

### Explicitly Out Of Scope

- Iris architecture redesign.
- `compose_layer3_*` 구조 리팩토링.
- 새 runtime behavior 도입.
- 새 source fact / source decision 작성.
- DVF 3.3 새 라운드 진입.
- release / Workshop / B42 readiness.
- package rebuild.
- staging directory naming rule / folder structure 재설계.
- whitelist 7개 subtree의 SHA-locked sealed 상태 도입.
- `.claude/worktrees/loving-newton-6327e6`, `sad-dewdney` **내부 코드/문서 내용 자체의 수정·리팩토링·재구성** (디렉토리 통째로 외부 백업 후 제거하는 Phase 6 의 dangling 처리 절차와는 별개 — Out Of Scope 항목은 "내부 작업의 content mutation" 만 의미).
- `Iris/_archive`, `Iris/_dev`, `Iris/_docs` 네임스페이스 cleanup.
- broad historical evidence deletion without successor archive/disposition decision.
- 신규 plan 작성 또는 기존 plan 내용 수정.
- 신규 authority surface / sealed artifact 도입.

---

## 3. Non-Goals

- 신규 권한/책임 경계 도입.
- 신규 sealed artifact 도입.
- runtime/build-time boundary 재설계.
- 모든 staging 라운드의 재실행/재생성 검증.
- 외부 zip archive 의 장기 무결성 보증.
- 모든 generated description의 의미적 정확성 검증.
- 게임 내 표시 동등성 보증.
- 멀티플레이/장시간 런타임 동등성 보증.
- Public-Facing Output Surface (Chunk Lua) 의 정확성 검증 — 본 plan은 "기존 변경의 봉인" 처리만 하며, 정확성은 별도 in-game QA로 미룬다.

---

## 4. Assumptions

- 본 plan은 PowerShell (Windows 11) 환경에서 실행된다. Git Bash가 보조로 사용 가능하나, 문서 명령은 PowerShell 기준으로 작성된다.
- 테스트는 `python -m unittest discover` 로 `Iris/build/description/v2/tests/`에서 동작한다 (pytest 의존성 없음).
- `.gitignore`의 화이트리스트 7개 subtree는 의도된 보존 대상이다 (`reviews/*.acquisition.jsonl`은 본 plan 이전부터 존재한 화이트리스트로, 신규가 아님).
- `docs/Iris/` 루트의 plan/closeout 쌍은 매칭되는 staging 디렉토리가 진행 중 상태임을 가리킨다.
- `docs/Iris/Done/`은 완료된 라운드의 종착지이며, 그 하위 plan/closeout/walkthrough/review는 sealed 분류 기준이 된다.
- `compose_layer3_*` 코드 변경과 `Chunk*.lua` 산출물은 동일 빌드 사이클의 페어다 — 분리 시 결정론적 재현성이 끊긴다.
- 작업트리 외부에 압축 후 약 200 MB, 압축 전 sweep 작업 공간으로 약 500 MB 이상의 디스크 여유가 있다.
- `Iris/_archive`, `Iris/_dev`, `Iris/_docs`는 cleanup 범위 밖 격리 네임스페이스다.
- 현재 working directory 는 main worktree 다 (`C:/Users/MW/Downloads/coding/PZ`). `git worktree list`에 등록된 추가 worktree 는 `.claude/worktrees/loving-newton-6327e6` 하나뿐이다.
- `.claude/worktrees/sad-dewdney`는 worktree 레지스트리에 미등록된 dangling 디렉토리로 추정된다 (Phase 6에서 검증 후 처리법 결정).
- 신규 validator 2개와 신규 테스트 4개는 본 plan 실행 전 작성 완료 상태이며, 본 plan은 그것을 검증 통과 후 추적 대상으로 분류한다.
- `tools/check_lua_syntax.ps1`은 Lua 청크 구문 검증에 사용 가능하다.
- `validate_legacy_active_silent_current_surface_guard.py`는 `--manifest` 와 `--repo-root` 인자가 필수이며, 입력 manifest 는 `Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/current_surface_guard_referent_manifest.json` 이다 (Bucket A 화이트리스트 내, 보존됨).
- ignored 파일 inventory: 본 plan은 `git status --short` 대신 `git status --ignored --short` 와 `git check-ignore -v -n` 으로 ignored 파일까지 가시화한다. 이 가정이 깨지면 `build_static_report_label_cleanup_round.py` 같은 ignored-only 파일이 Phase 1 매니페스트에 누락된다.
- `git -C <worktree-path>` 명령은 Git `safe.directory` 검증에 통과하는 사용자 컨텍스트에서 실행된다. 통과하지 못하면 "dubious ownership" 오류로 실패하며, 본 plan은 이를 worktree 상태 실패가 아니라 **blocked validation state** 로 처리한다 (Phase 6 명시).
- 외부 archive 포맷: PowerShell `Compress-Archive` 가 native 지원하는 **`.zip`** 을 사용한다. zstd/`.tar.zst` 는 Windows 10/11 기본 환경에 미지원 — 외부 도구 가정을 제거하기 위함이다.
- 모든 plan 산출 JSON manifest 는 **UTF-8 (BOM-less)** 로 작성한다. PowerShell 기본값 (UTF-16 LE + BOM) 은 `python`/`jq` 파싱 호환성을 위해 사용하지 않는다. 작성 시 `Set-Content -Encoding utf8NoBOM <file>` 또는 `[System.IO.File]::WriteAllText(<file>, <json>, [System.Text.UTF8Encoding]::new($false))` 사용.
- Commit A / B / C 의 순서는 **A → B → C** 다. A (도구·테스트·gitignore) 가 먼저 들어가 다음 단계의 validator/test 환경을 확정하고, B (Layer3 코드+생성물 페어) 가 다음으로 들어가 결정론적 재현성을 봉인하며, C (문서 movement+ledger 갱신) 가 마지막으로 들어가 governance ledger 가 봉인된 코드 상태를 가리키게 한다.
- 사전 검증된 사실 (두 검증 분리):
  - **Static SHA pair check**: `git merge-base --is-ancestor 6c12bef b904933` → EXIT 0 (main 작업트리 권한 컨텍스트에서 재현 가능 — main repo 자체의 `safe.directory` 가 통과한 셸에서만; 본 환경에서 실증 확인됨). `6c12bef` 은 `loving-newton-6327e6` 의 HEAD ("Remove Claude worktrees"), `b904933` 은 main HEAD. ancestor 관계 자체는 확정.
  - **실제 worktree 명령**: `git -C .claude\worktrees\loving-newton-6327e6 rev-parse HEAD` 등은 사용자 셸 권한에 따라 `safe.directory` 검증으로 EXIT 128 ("fatal: detected dubious ownership") 발생 가능. 본 plan 의 Git Bash 환경에서는 EXIT 0 관찰됐으나 다른 환경에서는 다를 수 있음. Phase 6 의 worktree 명령 검증은 `safe.directory` 해결 후에만 신뢰 가능.
- Phase 6 worktree merge 확인은 위 두 검증을 분리 실행한다 — static SHA pair 가 EXIT 0 인 상태에서 실제 worktree 명령이 EXIT 128 이면 ancestor 관계는 알려져 있으나 worktree 명령은 환경 권한 이슈로 `blocked validation state` 로 기록.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
- `Iris/build/description/v2/tools/build/compose_layer3_item.py`
- `Iris/build/description/v2/tools/build/compose_layer3_render.py`
- `Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py` (신규, `.gitignore` 화이트리스트 포함)
- `Iris/build/description/v2/tools/build/build_static_report_label_cleanup_referent_recovery_round.py` (신규, `.gitignore` 화이트리스트 포함)
- `Iris/build/description/v2/tools/build/build_static_report_label_cleanup_round.py` (untracked, `.gitignore` 화이트리스트 미포함 — Phase 1 매니페스트에서 보류/추적/제거 중 하나로 명시 분류 필요)
- `Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py` (신규)
- `Iris/build/description/v2/tools/validate_layer4_absorption_current_surface_guard.py` (신규)
- `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
- `Iris/build/description/v2/tests/test_current_authority_source_path_guard.py` (신규)
- `Iris/build/description/v2/tests/test_layer4_absorption_current_surface_guard.py` (신규)
- `Iris/build/description/v2/tests/test_layer4_trace_edge_authority_admission_round.py` (신규)
- `Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py` (신규)
- `Iris/media/lua/client/Iris/UI/Wiki/IrisContextMenu.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
- `tools/check_lua_syntax.ps1` (신규)

### Docs

- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/Iris/iris-dvf-3-3-adapter-diagnostic-compatibility-final-disposition-round-plan.md` (deleted; Done/으로 이동)
- `docs/Iris/iris-dvf-3-3-silent-21-replacement-authority-reconstruction-round-plan.md` (deleted; Done/으로 이동)
- `docs/Iris/iris-dvf-3-3-silent-metadata-intake-cleanup-round-plan.md` (deleted; Done/으로 이동)
- `docs/Iris/Done/iris-dvf-3-3-*.md` (신규, 23+)
- `docs/Iris/Done/Walkthrough/iris-dvf-3-3-*-walkthrough.md` (신규, 2)
- `docs/Iris/iris-worktree-cleanup-roadmap.md` (선행 참조, 변경 없음)
- `docs/Iris/iris-worktree-cleanup-plan.md` (본 문서)
- `docs/Iris/iris-worktree-cleanup-phase1-manifest.json` (Phase 1 산출물)
- `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-plan.md` (in-progress, 이동 금지)
- `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-closeout.md` (in-progress, 이동 금지)

### Config

- `.gitignore` (화이트리스트 추가)
- `.claude/settings.local.json` (변경 detected — **기본 commit 제외 정책 적용**. 사용자 명시 승인 시에만 별도 commit. §6 Phase 6 / §11 / §12 와 정렬)

### Generated Artifacts

- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk002.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk003.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk004.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk005.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk007.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk008.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk010.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk011.lua`
- `Iris/build/description/v2/staging/**` (1,818 files / 464 MB — 일부 보존, 다수 정리 후보)
- `Iris/build/description/v2/**/__pycache__/`, `*.pyc` (Phase 5 제거 대상)
- `Iris/build/description/v2/tests/_tmp_*/` (Phase 5 **조건부** 제거 대상 — Phase 1 매니페스트에서 실제 존재 확인된 경우에만; 0개이면 skip)
- `Iris/build/package/Iris/...` (Phase 5 조건부 제거 대상)

---

## 6. Planned Changes

### Change 1 — Phase 1 Worktree Surface Inventory / Cleanup Manifest

Purpose:

tracked / untracked / ignored / deleted 표면을 path-level로 분류해 후속 phase의 유일 입력이 되는 매니페스트를 생성한다.

Files:

- 입력: `.gitignore`, `docs/Iris/`, `docs/Iris/Done/`, `Iris/build/description/v2/staging/**`
- 산출: `docs/Iris/iris-worktree-cleanup-phase1-manifest.json` (UTF-8 BOM-less)

Implementation Notes:

- staging 하위 모든 라운드/리프 디렉토리를 목록화한다.
- 각 디렉토리를 5분류로 할당한다.
  - A — whitelist preserve (`.gitignore` 신규 항목과 1:1 일치)
  - B — in-progress 대응 (`docs/Iris/` 루트에 plan 또는 closeout 존재)
  - C — sealed Done disposition (`docs/Iris/Done/`에 plan/closeout 존재, 화이트리스트 외)
  - D — size-first review (large raw JSONL 보유 tree)
  - Unclassified — 자동 제거 금지, 사용자 확인 필요
- reproduce-required no-delete list를 별도 작성한다 (`compose_layer3_*`, `Iris/build/description/v2/tools/build/*.py`, package source, validators).
- 매니페스트는 Phase 4/5의 유일 입력이며, 즉흥 판단은 금지된다.

Validation:

- `git status --short -- Iris` (tracked modified/deleted + untracked-non-ignored)
- `git status --ignored --short -- Iris` (위 + ignored 파일/디렉토리 가시화; `!!` 접두로 표시)
- `git status --ignored --short -- Iris\build\description\v2\tools\build\build_static_report_label_cleanup_round.py` (특정 ignored 파일 매니페스트 포함 강제 — 출력 없으면 Phase 1 실패)
- `git diff --stat -- Iris`
- `git check-ignore -v -n <staging path samples> <tool/build/test 후보 paths>` 출력 해석:
  - 매칭 rule 라인이 `!` 로 시작 → whitelisted (not ignored, Bucket A 후보)
  - 매칭 rule 라인이 `!` 없음 → ignored (Phase 1 분류 대상)
  - `::: ` 라인 → 매칭 rule 없음 (default tracked)
- 매니페스트의 모든 staging 라운드에 5분류 중 하나가 할당되었는지 확인.
- 화이트리스트 분류가 `.gitignore` 신규 항목과 1:1 일치하는지 확인.
- 매니페스트 mutually exclusive 검증: 각 라운드가 정확히 하나의 bucket 에만 속하는지 확인.

---

### Change 2 — Phase 2 Core Change Preservation

Purpose:

current-authority implementation 변경, 신규 validator/test, runtime generated data, UI Lua를 cleanup 대상에서 보호하고 검증 가능한 페어로 유지한다.

Files:

- code: `compose_layer3_text.py`, `compose_layer3_body_profile.py`, `compose_layer3_item.py`, `compose_layer3_render.py`
- tests: `test_compose_layer3_text_v2.py`, 신규 테스트 4개
- validators: `validate_legacy_active_silent_current_surface_guard.py`, `validate_layer4_absorption_current_surface_guard.py`
- runtime: `Chunk002.lua`, `Chunk003.lua`, `Chunk004.lua`, `Chunk005.lua`, `Chunk007.lua`, `Chunk008.lua`, `Chunk010.lua`, `Chunk011.lua` (8개 명시 — `Chunk001/006/009` 범위 외)
- data: `dvf_3_3_decisions.jsonl`
- UI: `IrisContextMenu.lua`, `IrisWikiPanel.lua`

Implementation Notes:

- `compose_layer3_*`와 `Chunk*.lua`를 부분 staging하지 않는다 — 한 묶음으로 보존한다.
- UI Lua 2개와 **수정된 Chunk Lua 8개 모두** line-ending noise vs 실제 content diff를 구분한다 (Chunk 도 컴포저 출력이지만 플랫폼별 line-ending 차이 가능). `git diff --stat` + `git diff --shortstat` + 필요 시 `git diff --ignore-cr-at-eol` 로 확인.
- 신규 테스트 4개와 validator 2개는 본 phase에서 실행 결과를 기록한다.
- `dvf_3_3_decisions.jsonl` 변경은 Layer3 재빌드 사이클의 입력 변경이므로 같은 묶음으로 처리한다.

Validation:

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
- `python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json --repo-root .`
- `python -B Iris\build\description\v2\tools\validate_layer4_absorption_current_surface_guard.py --repo-root .`
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- UI Lua 2개에 대한 content diff 확인 (`git diff --stat -- Iris/media/lua/client/Iris/UI/Wiki/`)
- 수정된 Chunk Lua 8개에 대한 content diff 확인 (`git diff --stat -- Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`) — line-ending only 변경이면 별도 사유 기록

---

### Change 3 — Phase 3 Documentation And Governance Surface Handling

Purpose:

docs 변경을 disposable text churn이 아닌 governance movement로 처리하고, ARCHITECTURE/DECISIONS/ROADMAP의 ledger 갱신이 완료 라운드와 일치하는지 확인한다.

Files:

- deleted: `docs/Iris/` 루트 plan 3건
- new: `docs/Iris/Done/` plan/review/closeout 23+, Walkthrough 2
- updated: `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`
- in-progress (보존, 이동 금지): `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-{plan,closeout}.md`

Implementation Notes:

- deleted plan 3건이 Done/ successor와 1:1 매칭됨을 확인한다.
- orphaned deleted plan이 없는지 확인한다.
- `git mv` 미사용 상태이므로 path-pair 검증으로 history 추적성을 보완한다.
- acquisition-lexical-* 라운드는 in-progress 분류로 이동 대상이 아니다.
- DECISIONS/ARCHITECTURE/ROADMAP의 ledger 변경이 Done/ plan/closeout과 의미 일치하는지 검토한다.

Validation:

- `git diff --name-status -- docs/Iris`
- 삭제된 source docs 3개와 신규 Done/ docs path-pair 비교.
- compact ledger consistency 검토 (DECISIONS.md vs Done/ plan/closeout 라운드 이름 매칭).
- `git log --follow -- docs/Iris/Done/<successor>.md` (선택, history 추적 확인).

---

### Change 4 — Phase 4 Staging Evidence Disposition

Purpose:

1,818 files / 464 MB staging tree를 Bucket A/B/C/D 별로 disposition하고, 제거 대상은 worktree 외부 zip archive 백업 후 삭제한다.

Files:

- Bucket A (보존): whitelist 7개 subtree (5개 신규 compose_contract_migration 라운드 + manual_in_game_validation + 선행 존재하던 `reviews/*.acquisition.jsonl`)
- Bucket B (보존): in-progress 라운드 staging
- Bucket C (백업 후 삭제): `docs/Iris/Done/`에 plan/closeout 있는 whitelist 외 staging tree
- Bucket D (size-first review): 압축 전 크기가 **50 MB 이상**이거나 단일 파일 size 가 **상위 5개 이내** (Bucket A 화이트리스트 제외) 인 staging tree. 본 환경 실측 (2026-06-05 기준, `du -m` 측정값; Phase 1 매니페스트가 권위적 목록):
  - `compose_contract_migration/static_report_label_cleanup_round/phase2_allowed_legacy_residue.json` (55 MB, 50MB+ 임계 통과)
  - `compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_occurrence_classification.json` (55 MB, 50MB+ 임계 통과)
  - `compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/authority_classification_ledger.jsonl` (39 MB, 비-Bucket A 상위 5개 진입)
  - `compose_contract_migration/structural_signal_authority_classification_round/phase6_remediation/post_remediation_writer_reachability_matrix.jsonl` (33 MB, 비-Bucket A 상위 5개 진입)
  - `compose_contract_migration/structural_signal_authority_classification_round/phase4_writer_reachability/writer_reachability_matrix.jsonl` (33 MB, 비-Bucket A 상위 5개 진입)
  - (참고: `compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_surface_classification.jsonl` 34 MB, `layer4_boundary_current_artifact_inventory.jsonl` 22 MB 는 Bucket A 화이트리스트 우선으로 Bucket D 진입 안 함)
  - 임계 미통과 (참고): `phase2_inventory/occurrence_inventory.jsonl` 25 MB (rank 7), `layer4_boundary_exclusion_ledger.jsonl` 13 MB (Bucket A)
- Unclassified (보류): 사용자 확인 후 처리
- 외부 백업 archive: `$env:USERPROFILE\iris-staging-backup-2026-06-05.zip` 또는 동등 외부 경로 (PowerShell native `.zip` 포맷; zstd 외부 도구 가정 제거)
- 추적 산출물 (cleanup manifest): `docs/Iris/iris-worktree-cleanup-phase4-disposition-manifest.json` — archive 경로, archive SHA-256, entry count, 제거 path 리스트, round 별 keep/delete 사유, 외부 참조 scan 결과 수록. **UTF-8 (BOM-less)** 로 작성.

Implementation Notes:

- Bucket A, B는 본 phase에서 절대 건드리지 않는다.
- Archive 생성 명령 (PowerShell, `.zip` 포맷): `Compress-Archive -Path <staging-round-paths> -DestinationPath $env:USERPROFILE\iris-staging-backup-2026-06-05.zip -CompressionLevel Optimal`. 단일 archive 에 여러 round 묶을 경우 round 경로 배열로 전달.
- Bucket C는 라운드 단위 그룹화 압축 → archive SHA-256 기록 → disposition manifest 갱신 → staging에서 제거 순서로 처리한다.
- Bucket D는 size 측정 → 백업 → archive SHA-256 기록 → disposition manifest 갱신 → 제거 후보화 순서로 처리한다.
- closeout/manifest/schema가 sealed 라운드의 유일 local evidence인 경우 보존하며, disposition manifest 의 keep 사유에 명시한다.
- current docs/tests/tools에서 참조되는 evidence는 사전 reference scan 으로 확인 후 보존하며, scan 결과를 disposition manifest 에 기록한다.
- raw evidence 이동/아카이브는 disposition manifest 의 explicit 사유와 함께만 수행한다.
- broad `git clean -X` 사용 금지.
- disposition manifest 는 외부 zip archive 의 장기 무결성에 의존하지 않는 **추적 가능한 successor 기록** 역할을 한다 (Open Question Q1 → tracked manifest 채택).

Validation:

- Bucket A: Phase 4 시작 시점 SHA-256 ↔ Phase 4 종료 시점 SHA-256 동일성 (PowerShell: `Get-ChildItem -Path <A> -Recurse -File | Get-FileHash -Algorithm SHA256 | Select-Object Hash,Path | Sort-Object Path` 으로 시점별 스냅샷 후 diff).
- sealed 라운드의 hash manifest 파일 존재 여부 확인.
- 외부 참조 scan: `rg "staging/<round-path>" docs Iris\build\description\v2\tests Iris\build\description\v2\tools` — 결과를 disposition manifest 에 첨부.
- 외부 archive entry count: **in-place 명령만 채택** (PowerShell 5.1 호환, §10 의 디렉토리 단위 destructive 명령 금지 규칙과 정합):
  ```powershell
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $z = [System.IO.Compression.ZipFile]::OpenRead($archive)
  $count = $z.Entries.Count
  $z.Dispose()
  $count
  ```
  **주의**: PowerShell 5.1 fresh session 에서는 `[System.IO.Compression.ZipFile]` 타입이 기본 미로드 상태다. `Add-Type` 누락 시 `Unable to find type [System.IO.Compression.ZipFile]` 오류 (실측 확인). `Add-Type` 은 코드블록 첫 줄로 의무화. 대안 (`Expand-Archive ... ; Remove-Item -Recurse -Force <tmp>`) 은 §10 Rollback Plan 의 "안전 조건 — 와일드카드 또는 디렉토리 단위 destructive 명령 금지" 규칙과 충돌하므로 본 plan 에서 **사용 금지**. **금지 (PowerShell 5.1 미지원)**: `Expand-Archive ... -PassThru`.
- 외부 archive SHA-256: `Get-FileHash <archive> -Algorithm SHA256` — disposition manifest 의 archive_sha256 필드와 일치 검증.
- disposition manifest JSON parse 검증 (`Get-Content <manifest> -Raw -Encoding utf8 | ConvertFrom-Json`).
- disposition manifest 인코딩 확인: `[System.IO.File]::ReadAllBytes(<manifest>)[0..2]` 가 BOM (`0xEF, 0xBB, 0xBF`) 이 아닌지 확인.
- 보류 처리된 Unclassified 라운드 명시 목록은 disposition manifest 의 unclassified 섹션에 수록.

---

### Change 5 — Phase 5 Targeted Cleanup Execution

Purpose:

low-risk generated residue만 명시적 path 기반으로 제거한다. broad ignored cleanup은 사용하지 않는다.

Files:

- 제거: `Iris/build/description/v2/**/__pycache__/`, `Iris/build/description/v2/**/*.pyc`
- 조건부 제거: `Iris/build/description/v2/tests/_tmp_*/` (Phase 1 매니페스트에서 실제 존재 확인된 경우에만; 0개이면 본 항목 skip)
- 조건부 제거: `Iris/build/package/Iris/...` (source files와 packaging scripts 모두 intact 확인 후에만)
- 검토: UI Lua + Chunk Lua line-ending-only noise (content diff 0인 파일만 revert/refresh 대상)

Implementation Notes:

- `git clean -X` 또는 equivalent broad ignored deletion은 사용 금지.
- package copy 제거 전에 source 와 packaging scripts 양쪽 모두 intact 한지 확인.
- UI Lua는 content diff가 0일 때만 line-ending refresh 수행.
- 모든 제거는 명시적 path 기반.
- glob 기반 `tools/build/*.py` 삭제 금지.

Validation:

- 제거 전후 `git status --short -- Iris` 비교.
- `git diff --stat -- Iris` 로 line-ending noise 잔존 여부 확인.
- package source presence check (PowerShell: `Get-ChildItem Iris\<package-source-path>` 또는 `Test-Path Iris\<package-source-path>`).
- 제거 전후 file count / size 비교 (PowerShell: `(Get-ChildItem -Path Iris\build\description\v2 -Recurse -File).Count`, `(Get-ChildItem -Path Iris\build\description\v2 -Recurse -File | Measure-Object -Property Length -Sum).Sum`).

---

### Change 6 — Phase 6 Commit Readiness / Worktree Triage / Final Validation

Purpose:

남은 worktree가 reviewable하고 일관성 있는지 확인하고, validation pass 여부에 따라 commit readiness 또는 보류 사유를 판정한다.

Files:

- main worktree: `C:/Users/MW/Downloads/coding/PZ` (본 plan 의 실행 위치, 보존)
- registered worktree: `.claude/worktrees/loving-newton-6327e6` (`git worktree list`에 등록, 상태 확인 후 처리)
- dangling 디렉토리 추정: `.claude/worktrees/sad-dewdney` (worktree 레지스트리 미등록 — 별도 처리 트랙)
- 추적 산출물 (dangling inventory): `docs/Iris/iris-worktree-cleanup-phase6-dangling-inventory.json` — sad-dewdney 의 file count, total size, per-file SHA-256, external archive 경로, external archive SHA-256, 제거 승인자/시각 수록
- commit 후보 set:
  - Commit A: 신규 build tool 2 + validator 2 + test 4 + `tools/check_lua_syntax.ps1` + `.gitignore` 화이트리스트
  - Commit B (분리 금지): `compose_layer3_text.py`, `compose_layer3_body_profile.py`, `compose_layer3_item.py`, `compose_layer3_render.py`, `test_compose_layer3_text_v2.py`, `dvf_3_3_decisions.jsonl`, `Chunk002.lua`, `Chunk003.lua`, `Chunk004.lua`, `Chunk005.lua`, `Chunk007.lua`, `Chunk008.lua`, `Chunk010.lua`, `Chunk011.lua`, `IrisContextMenu.lua`, `IrisWikiPanel.lua` (정확한 리스트 — 미수정 `Chunk001/006/009` 는 포함 금지)
  - Commit C: `docs/Iris/` 이동 + `docs/Iris/Done/` 신규 + `ARCHITECTURE.md` + `DECISIONS.md` + `ROADMAP.md`
- `.claude/settings.local.json` (기본 제외, Open Question Q2 → 별도 commit 제외 정책)

Implementation Notes:

- worktree 후보 path 마다 가드 명령으로 worktree 여부를 검증한다: `git -C <path> rev-parse --show-toplevel` 결과가 `<path>` 자신과 일치할 때만 worktree 로 취급한다. 결과가 main worktree 등 상위 경로를 반환하면 dangling 디렉토리로 분류한다.
- 가드 명령 자체 (`git -C <path> rev-parse --show-toplevel`) 가 `safe.directory` dubious ownership 으로 EXIT 128 실패하면, **guard blocked validation state** 로 별도 분류한다 (worktree/orphan 판정 자체 불가). 이 경우 사용자 셸에서 동일 명령을 실행하거나 `git config --global --add safe.directory <abs-path>` 후 재시도해야 후속 처리 진입 가능.
- main worktree (`C:/Users/MW/Downloads/coding/PZ`) 는 본 plan 의 실행 위치이며 cleanup 대상이 아니다.
- `loving-newton-6327e6` 처리 절차:
  - `git -C <path> status --short` 가 "fatal: detected dubious ownership" 으로 실패 시: **status blocked validation state** 로 분류 (§7 Automated Validation 의 두 단계 blocked state 명명과 정합 — 가드 명령 실패는 `guard blocked`, 상태 명령 실패는 `status blocked`). worktree 상태 실패가 아니라 환경 권한 이슈로 기록한다. 해결책: 사용자 셸에서 동일 명령 실행 또는 `git config --global --add safe.directory <abs-path>` 후 재시도.
  - 정상 실행 시: uncommitted 변경 유무 확인 → HEAD merge 여부 확인 → 완료 시에만 `git worktree remove` 후보.
    - merge 확인 실제 명령 (각 단계 후 `$LASTEXITCODE` 가드):
      ```powershell
      $wtHead = git -C .claude\worktrees\loving-newton-6327e6 rev-parse HEAD
      if ($LASTEXITCODE -ne 0) { Write-Host "BLOCKED: worktree rev-parse failed (likely safe.directory)"; return }
      $mainHead = git rev-parse main
      if ($LASTEXITCODE -ne 0) { Write-Host "BLOCKED: main rev-parse failed"; return }
      git merge-base --is-ancestor $wtHead $mainHead
      $mergeBaseExit = $LASTEXITCODE
      echo "MERGE_BASE_EXIT=$mergeBaseExit"
      ```
    - 합격 기준: `MERGE_BASE_EXIT=0` (worktree HEAD 가 main 의 ancestor — merge 됨).
    - 불합격 기준: `MERGE_BASE_EXIT=1` (ancestor 아님 — merge 안 됨). 이 경우 `git worktree remove` 후보 아님.
    - 사전 검증 결과 (두 경로 분리):
      - **Static SHA pair check**: `git merge-base --is-ancestor 6c12bef b904933` 은 EXIT 0 (main 작업트리 권한 컨텍스트에서 재현 가능 — main repo 자체의 `safe.directory` 가 통과한 셸에서만; 본 환경에서 실증 확인됨). ancestor 관계 자체는 확정.
      - **실제 worktree 명령**: `git -C .claude\worktrees\loving-newton-6327e6 rev-parse HEAD` 등은 `safe.directory` 권한 컨텍스트에 따라 EXIT 128 가능. 본 plan 의 Git Bash 환경에서는 EXIT 0 관찰됐으나, 사용자 PowerShell 컨텍스트에서는 `git config --global --add safe.directory <abs-path>` 해결 후 재확인 필요.
- `sad-dewdney` 처리 절차 (가드 결과 worktree 아님으로 확정 시):
  - **주의**: `git -C sad-dewdney status` 는 부모 repo의 결과를 반환 (실측 확인됨). 따라서 git 기반 inventory 는 사용 금지.
  - 1단계 inventory: `Get-ChildItem -Path .claude\worktrees\sad-dewdney -Recurse -Force -File` 로 전체 file 목록 + size 수집.
  - 2단계 hash: 각 파일에 대해 `Get-FileHash -Algorithm SHA256`.
  - 3단계 dangling inventory manifest 작성: file count, total size, per-file SHA-256, list 를 `docs/Iris/iris-worktree-cleanup-phase6-dangling-inventory.json` 에 기록.
  - 4단계 external archive: PowerShell `Compress-Archive` (`.zip`) 또는 동등 도구로 외부 경로에 아카이브 생성 → archive SHA-256 산출 → inventory manifest 의 `external_archive_sha256` 필드에 기록.
  - 5단계 사용자 명시 승인 gate: inventory manifest 검토 → 제거 승인 의사 표시 + 승인 시각 기록. 승인 없이는 다음 단계 진행 금지.
  - 6단계 제거: `Remove-Item -Recurse -Force .claude\worktrees\sad-dewdney` 실행. `git worktree remove` 사용 금지 (레지스트리 미등록).
- commit split 은 validation 4종이 모두 exit code 0 인 경우에만 진행한다.
- validation 미통과 시 commit-ready 주장 금지. 보류 사유를 명시한다. `safe.directory` blocked state 도 validation 미통과 사유에 포함된다.
- **Commit 순서는 A → B → C** 다 (§4 Assumptions 명시). A 가 도구·테스트·gitignore 환경을 먼저 확정 → B 가 Layer3 코드↔Chunk 페어를 봉인 → C 가 governance ledger 를 봉인된 코드 상태에 정렬한다.
- Commit B는 결정론적 재현성 보존을 위해 분리 금지 — Chunk 리스트는 명시적 리스트 사용 (PowerShell 의 brace 미확장 + 미수정 Chunk 포함 위험 방지).
- dangling inventory manifest 는 **UTF-8 (BOM-less)** 로 작성한다 (§4 Assumptions). 작성 명령: `[System.IO.File]::WriteAllText(<path>, ($inventory | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))`.
- `.claude/settings.local.json` 은 기본적으로 모든 commit set 에서 제외한다. 사용자가 명시적으로 포함을 승인할 때에만 별도 commit 으로 처리한다 (Open Question Q2 default).

Validation:

- `git worktree list` (등록된 worktree 확정)
- 각 후보 path 에 대해 `git -C <path> rev-parse --show-toplevel` (worktree vs orphan 가드)
- 각 registered worktree 내부 `git -C <path> status --short`. "fatal: detected dubious ownership" 출력 시 worktree 상태 실패가 아닌 **status blocked validation state** 로 기록 (§7 의 두 단계 blocked state 명명 — `guard blocked` / `status blocked` — 와 정합; 별도 보류 사유).
- dangling 디렉토리 (`sad-dewdney`) inventory: `Get-ChildItem -Path <path> -Recurse -Force -File | Measure-Object -Property Length -Sum`, per-file `Get-FileHash -Algorithm SHA256`, 결과를 `iris-worktree-cleanup-phase6-dangling-inventory.json` 에 기록.
- dangling external archive SHA-256: `Get-FileHash <archive> -Algorithm SHA256` — inventory manifest 의 external_archive_sha256 일치 검증.
- 사용자 승인 gate 통과 기록 (manifest 의 approval 필드).
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
- `python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json --repo-root .`
- `python -B Iris\build\description\v2\tools\validate_layer4_absorption_current_surface_guard.py --repo-root .`
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- 최종 `git status --short -- Iris`
- validation command 4종 + exit code 기록 (텍스트 보고). blocked state 는 exit code 와 별도로 표기.

---

## 7. Validation Plan

### Automated Validation

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
- `python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json --repo-root .`
- `python -B Iris\build\description\v2\tools\validate_layer4_absorption_current_surface_guard.py --repo-root .`
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- `git status --short -- Iris` (tracked + untracked-non-ignored 확인)
- `git status --ignored --short -- Iris` (ignored 파일 포함; `!!` 접두 확인. `build_static_report_label_cleanup_round.py` 포함 여부 강제 확인 대상)
- `git diff --stat -- Iris` (line-ending noise 식별)
- `git check-ignore -v -n <sample paths>` (gitignore 의도 + 출력 semantics 검증):
  - `!` 접두 rule 라인 = whitelisted (not ignored)
  - 접두 없음 rule 라인 = ignored
  - `::: ` 라인 = 매칭 rule 없음 (default tracked)
- `git -C <worktree-candidate> rev-parse --show-toplevel` (registered worktree vs orphan 가드). EXIT 128 dubious ownership 실패 시 → **guard blocked validation state** (worktree/orphan 판정 자체 불가; 후속 처리 진입 금지).
- `git -C <worktree-path> status --short` "dubious ownership" 실패 → **status blocked validation state** (worktree 등록은 확정됐으나 상태 조회 불가).
- 두 blocked state 모두 exit code 와 별도 표기로 보고. `git config --global --add safe.directory <abs-path>` 또는 사용자 셸 권한 컨텍스트에서 재실행이 해결책.
- Bucket A SHA-256 sweep: PowerShell `Get-ChildItem -Recurse -File | Get-FileHash` 시점별 스냅샷 후 diff
- 외부 archive SHA-256: PowerShell `Get-FileHash <archive> -Algorithm SHA256`
- disposition manifest JSON parse: PowerShell `Get-Content <manifest> | ConvertFrom-Json`
- dangling inventory manifest JSON parse: PowerShell `Get-Content <manifest> | ConvertFrom-Json`

### Manual Validation

- 매니페스트의 Unclassified 라운드 수동 검토 (자동 제거 금지).
- docs path-pair 수동 확인 (deleted 3개 ↔ Done/ successor).
- UI Lua line-ending noise vs content diff 수동 식별.
- worktree 정리 전 내부 uncommitted 수동 확인.
- `.claude/settings.local.json` 변경 내용 수동 확인 (본 cleanup 범위 분리 판정).
- DECISIONS/ARCHITECTURE/ROADMAP 갱신이 완료 라운드와 의미 일치하는지 수동 검토.

### Validation Limits

- in-game QA 없음.
- multiplayer validation 없음.
- long-session runtime validation 없음.
- Workshop / B42 readiness validation 없음.
- package deployment validation 없음.
- 모든 staging 라운드 재실행 검증 없음.
- 외부 zip archive 장기 무결성 보증 없음.
- 모든 generated description의 의미적 정확성 검증 없음.
- Chunk Lua 의 게임 내 표시 동등성 검증 없음.
- full runtime equivalence claim 없음.

---

## 8. Risk Surface Touch

### Authority Surface

None — 본 plan은 권한/책임 경계를 바꾸지 않는다. 기존 authority-relevant 변경 (`compose_layer3_*`, current-authority guard) 은 보존 및 검증 대상이며 신규 권한 도입이 아니다.

### Runtime Behavior Surface

Touched — 수정된 Chunk Lua 8개 (`Chunk002.lua`, `Chunk003.lua`, `Chunk004.lua`, `Chunk005.lua`, `Chunk007.lua`, `Chunk008.lua`, `Chunk010.lua`, `Chunk011.lua`) 와 UI Lua 2개의 기존 수정사항이 Commit B 후보로 보존된다. 본 plan은 새 runtime behavior를 도입하지 않고 기존 변경을 봉인하는 절차다.

### Compatibility Surface

Touched — `.gitignore` 화이트리스트 추가가 Commit A 후보로 보존된다. 신규 항목 카운트:

- 신규 코드 화이트리스트 8개 (2 validators + 2 build scripts + 4 tests; `tools/check_lua_syntax.ps1` 은 `tools/` 가 처음부터 미-gitignored 라 별도 화이트리스트 불필요)
- 신규 staging 라운드 화이트리스트 5개 (compose_contract_migration 하위 5개 round, 각 round 디렉토리 + `**` 글로브 2 라인씩)
- `compose_contract_migration/` 부모 디렉토리 재허용 1개
- `manual_in_game_validation/` 디렉토리 + `**` 글로브 1개
- (preexisting, 신규 아님) `reviews/*.acquisition.jsonl` 화이트리스트 — 본 plan 이전부터 존재

staging 신규 라운드의 보존 정책이 확정된다.

### Sealed Artifact Surface

None new sealed — whitelist 7개는 보존 대상이나 본 plan으로 SHA-locked seal 상태가 도입되지는 않는다 (Non-Goal). Bucket A 동등성은 cleanup 전후 sanity check이지 sealed lock 도입이 아니다.

### Public-Facing Output Surface

Boundary deferred — `Chunk*.lua`는 게임 내 표시 데이터 표면이지만, 본 plan은 "이미 존재하는 변경의 봉인"으로 처리한다. 정확성 보증은 별도 in-game QA로 미루며 Validation Limits에 명시한다. roadmap 7항의 충돌은 본 plan에서 "기존 변경의 봉인"으로 해석 고정한다.

---

## 9. Risk Analysis

### Architecture Risk

- broad ignored cleanup으로 reproduce-required Python script가 삭제될 위험 → glob 기반 삭제 금지 제약과 Phase 1 no-delete list로 차단.
- staging 디렉토리 구조 재설계는 Non-Goal — 분류 매니페스트 외 구조 변경 없음.
- 새 authority surface 도입은 Non-Goal — 본 plan은 분류·보존·정리만 수행.
- Phase 1 inventory 가 `git status --short` 만 사용해 `build_static_report_label_cleanup_round.py` 같은 ignored-only 파일을 누락할 위험 → `git status --ignored --short` 와 `git check-ignore -v -n` 의무화 (§6 Phase 1 / §7).

### Runtime Risk

- `compose_layer3_*`와 `Chunk*.lua` 분리 시 결정론적 재현성 손실 → Commit B 분리 금지 제약.
- 외부 zip archive 가 작업트리 내부에 있을 경우 cleanup 후 백업 의미 상실 → 작업트리 외부 경로 의무.
- in-progress 라운드 staging을 잘못 분류해 삭제 → Bucket B는 절대 건드리지 않음 + Phase 1 매니페스트에서 명시.
- 다음 라운드가 read-only input으로 의존하던 staging tree 삭제 → Phase 4 grep 기반 외부 참조 검사로 확인.

### Compatibility Risk

- `.gitignore` 화이트리스트가 의도와 다르게 동작해 staging 라운드가 의도 외 추적됨 → `git check-ignore -v -n` 으로 검증 (§6 Phase 1 / §7 와 정합; `-n` 으로 매칭 없는 path 까지 균일 출력).
- docs 이동이 `git mv` 미사용으로 history rename 추적성 저하 → `git log --follow`로 사후 확인.
- whitelist vs 실제 staging 디렉토리 name 불일치 → 매니페스트 1:1 일치 검증.
- `.claude/settings.local.json`이 본 cleanup 의도 외 변경을 commit set에 끌어들임 → Phase 6 기본 제외 정책 + 사용자 명시 승인 시에만 별도 commit.
- dangling 디렉토리 (`.claude/worktrees/sad-dewdney`) 를 registered worktree 로 잘못 처리해 `git worktree remove` 실패 또는 잘못된 path 의 git 동작 발생 → Phase 6 `git -C <path> rev-parse --show-toplevel` 가드 의무화 + 가드 명령 자체가 `safe.directory` 로 EXIT 128 실패 시 **guard blocked validation state** 로 분류 (§6 Phase 6 가드 명령 처리 / §7 Automated Validation 의 worktree 가드 항목과 정합).
- Phase 4 외부 archive 의 장기 무결성 미보증 → tracked disposition manifest (`docs/Iris/iris-worktree-cleanup-phase4-disposition-manifest.json`) 가 archive SHA-256 와 per-round 사유를 추적 가능한 형태로 보존.

### Regression Risk

- 신규 테스트 4개와 validator 2개가 기존 unittest 환경과 호환되지 않을 가능성 → Phase 2/6에서 명시적 실행 후 exit code 기록.
- `validate_legacy_active_silent_current_surface_guard.py` 의 입력 manifest 가 Bucket A 영역 (`compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/`) 에 있어, Phase 4 가 Bucket A 보존 제약을 어길 경우 validation 자체가 실행 불가 → Bucket A 보존이 validation 의 전제.
- UI Lua의 line-ending noise가 실제 UI 변경을 숨길 가능성 → Phase 2 line-ending vs content diff 구분.
- 워크트리 정리 중 uncommitted 작업 손실 → Phase 6에서 각 worktree `git -C <path> status` 사전 확인.
- Layer4 absorption validator가 Bucket C 제거 후 통과하지 못할 가능성 → Phase 4 → Phase 6 validation 재실행으로 식별.
- Rollback 시 `git restore` 가 manifest-owned 외 path 에 잘못 적용되어 사용자 uncommitted 작업 손실 → §10 Rollback Plan 에 명시한 안전 조건 의무화.
- `git -C <worktree-path>` 명령이 `safe.directory` dubious ownership 으로 실패하여 worktree 상태를 잘못 판단할 위험 → Phase 6 에서 두 단계 분리 처리: 가드 명령 (`rev-parse --show-toplevel`) 실패는 **guard blocked validation state** (worktree/orphan 판정 자체 불가), 상태 명령 (`status --short`) 실패는 **status blocked validation state** (worktree 등록 확정 후 상태 조회 불가). 둘 다 worktree 자체 상태 실패와 분리 처리.
- dangling 디렉토리 (`sad-dewdney`) 의 inventory 를 git 명령으로 시도하면 부모 repo 의 결과를 반환해 잘못된 안전 판정 가능 → Get-ChildItem 기반 inventory + per-file SHA-256 + external archive hash + 명시 사용자 승인 gate 의무화 (§6 Phase 6 / §11).

---

## 10. Rollback Plan

**안전 조건 (모든 rollback 명령에 적용):**

- 어떤 `git restore`, `git reset`, `Remove-Item` 명령이든 **단일 명시 path 만** 대상으로 한다. 와일드카드 또는 디렉토리 단위 destructive 명령은 금지.
- **예외**: dangling 디렉토리 (`.claude/worktrees/sad-dewdney`) 의 `Remove-Item -Recurse -Force` 는 §6 Phase 6 의 6단계 절차 (Get-ChildItem inventory + per-file SHA-256 + external archive + archive SHA-256 + 사용자 명시 승인) 가 모두 추적 manifest (`iris-worktree-cleanup-phase6-dangling-inventory.json`) 에 기록·통과된 경우에만 허용된다. 이 예외는 본 plan 의 단일 명시 path (= sad-dewdney 디렉토리 루트) 에만 적용되며, 다른 디렉토리에는 적용되지 않는다.
- 대상 path 는 반드시 Phase 1 매니페스트의 manifest-owned 항목이거나, 사용자가 명시적으로 승인한 path 여야 한다.
- 작업트리가 dirty 상태에서 `git restore -- <path>` 는 해당 path 의 uncommitted 변경을 영구 삭제한다. 적용 전 반드시 `git diff -- <path>` 로 영향 범위를 확인하고, 사용자 승인을 받는다.
- `git reset --hard` 는 사용 금지. 본 plan 에서 staging 회복은 `git restore --staged -- <single-path>` 로 통일하며, `git reset <commit>` (no path) 도 HEAD 전역 이동 위험으로 사용 금지.
- 외부 백업으로 복구할 때는 disposition manifest 의 archive_sha256 일치 검증 후에만 압축 해제.

**Phase 별 절차:**

- Phase 1 (매니페스트 파일 1개 추가): `Remove-Item docs\Iris\iris-worktree-cleanup-phase1-manifest.json` 으로 즉시 회복.
- Phase 2 (검증만): 변경 없음, rollback 불요.
- Phase 3 (docs 이동 확인): docs 이동이 아직 commit 전이므로 잘못된 처리는 path 단위 점검 후 `git restore --source=HEAD -- docs/Iris/<single-path>` 로 회복 (단, 위 안전 조건 의무).
- Phase 4 (staging 제거): worktree 외부 zip archive 백업 + tracked disposition manifest 로 복구. archive SHA-256 일치 후 `Expand-Archive -Path <archive> -DestinationPath <staging-root>` 으로 해제 (staging 복원 목적 — §6 Phase 4 Validation 의 archive entry count 단계가 금지한 "검증용 temp dir + `Remove-Item -Recurse -Force`" 패턴과 다름; 본 rollback 의 Expand 는 destination 에 데이터를 복원할 뿐 디렉토리 단위 destructive 작업 없음).
- Phase 5 (cache/tmp/package copy 제거): cache/tmp 는 재생성으로 자동 복구. package copy는 빌드 파이프라인 재실행으로 재생성.
- Phase 6 (commit A/B/C):
  - commit 이 이미 생성된 경우: `git revert <commit>` 사용 (history 보존, 안전).
  - commit 직전 단계에서 staging 만 잘못 구성된 경우: `git restore --staged -- <single-path>` 로 staging 만 되돌리고 working tree 는 보존.
  - `git reset <commit>` (no path, no `--hard`) 은 HEAD 를 전역으로 이동시키므로 본 plan 에서는 **사용 금지**. staging 단위 회복은 `git restore --staged -- <single-path>` 로 통일.
- Commit B는 분리 금지 단위이므로 전체를 단일 `git revert` 단위로 처리.
- 워크트리 제거는 registered worktree 한정으로 `git worktree add` 로 재생성 가능. dangling 디렉토리 (`sad-dewdney`) 는 외부 백업 압축 해제로만 복구.
- 워크트리 내부 uncommitted 작업은 복구 불가 — Phase 6 사전 확인 필수.
- validation 실패 시 affected path class만 우선 복구하고 전체 rollback은 피한다.

---

## 11. Governance Constraints

- `Philosophy.md` / `DECISIONS.md` / `ARCHITECTURE.md` / `ROADMAP.md` 준수.
- additive amendment preference: 기존 plan/sealed artifact 직접 수정 대신 cleanup 매니페스트와 분류 결과로 변경 의도 표현.
- minimal diff preservation: line-ending noise는 commit에 포함하지 않는다.
- runtime/build-time separation: cleanup 명목으로 runtime 동작을 바꾸지 않는다.
- `compose_layer3_*` ↔ `Chunk*.lua` 분리 금지.
- broad `git clean -X` 또는 equivalent full ignored cleanup 사용 금지.
- glob 기반 `Iris/build/description/v2/tools/build/*.py` 삭제/아카이브 금지.
- staging whitelist 7개 subtree 절대 건드리지 않음.
- `Iris/_archive`, `Iris/_dev`, `Iris/_docs` 는 cleanup 범위 밖.
- in-progress 라운드 plan/closeout 쌍은 이동 금지.
- FAIL-LOUD 패턴 보존.
- source facts / source decisions / rendered text / runtime Lua / package output 을 cleanup 명목으로 변경하지 않는다.
- validation command가 exit code 0 으로 끝난 경우에만 success claim.
- 기존 authority ownership 우회 금지.
- 새 sealed artifact 도입 금지 (Bucket A 동등성 확인은 lock이 아니다).
- worktree 후보 path 는 `git -C <path> rev-parse --show-toplevel` 가드를 통과한 경우에만 worktree 명령 (`git worktree remove` 등) 의 대상이 된다. 가드 미통과 디렉토리는 일반 디렉토리 처리 경로로만 다룬다.
- `.claude/settings.local.json` 은 사용자 명시 승인 없이는 어떤 commit set 에도 포함되지 않는다 (기본 제외 정책).
- `git restore`, `git reset` 은 manifest-owned 또는 사용자 명시 승인 path 한정으로만 사용한다. 와일드카드 destructive 명령 금지.
- 외부 백업 archive 는 단독으로 evidence successor 역할을 하지 않는다. tracked disposition manifest 가 동반되어야 한다.
- Phase 1 inventory 는 `git status --short` 단독으로 완성되지 않는다. `git status --ignored --short` + `git check-ignore -v -n` 의 출력이 매니페스트에 통합되어야 한다.
- `git -C <worktree-path>` 명령이 `safe.directory` dubious ownership 으로 실패한 경우 worktree 상태 실패가 아니라 blocked validation state 로 분류한다. blocked state 는 별도 보류 사유로 기록되며 commit readiness 판정 통과로 간주하지 않는다.
- dangling 디렉토리 정리는 git 기반 inventory 를 사용하지 않는다. Get-ChildItem inventory + per-file SHA-256 + external archive SHA-256 + 명시 사용자 승인이 모두 추적 가능한 manifest 에 기록된 후에만 `Remove-Item -Recurse -Force` 를 실행한다.

---

## 12. Expected Closeout State

`partial`

이유:

- Phase 1 ~ 5 는 Unclassified 라운드, blocked validation, dangling 디렉토리 승인 등의 사용자 결정 대기가 없을 때 단일 실행으로 `complete` 가능하다. Phase 1 매니페스트에 Unclassified 가 1건이라도 남으면 Phase 1 자체가 `partial`. Phase 6 의 commit readiness 판정은 validation command 4종이 모두 exit code 0 으로 종료된 경우에만 commit 실행으로 진행 가능하다. 본 plan 은 commit 자체를 mandatory 산출물로 두지 않는다 — "commit-ready set 또는 보류 사유" 가 산출물이다.
- Public-Facing Output Surface 충돌 (roadmap 7항) 은 본 plan 범위에서 "기존 변경의 봉인" 으로 해석 고정하지만, runtime chunk 변경의 정확성 보증은 별도 in-game QA 로 미룬다 (Validation Limits 명시).
- main worktree (`C:/Users/MW/Downloads/coding/PZ`) 는 본 plan 의 실행 위치이므로 cleanup 대상에서 제외. `loving-newton-6327e6` 만 registered worktree triage 대상이고, `sad-dewdney` 는 dangling 디렉토리 처리 트랙으로 분리되어 사용자 확인에 따라 `partial` 종료될 수 있다.
- Bucket D (large raw JSONL, 50 MB 임계값 이상 또는 size 상위 5개) 처리가 사용자 확인 대기로 deferred 되면 staging disposition 은 `partial` 이다.
- Unclassified 라운드가 0 개가 아닐 경우 사용자 결정 대기로 `partial` 종료된다.
- `.claude/settings.local.json` 은 기본 제외 정책 적용 → 사용자가 명시 승인하지 않으면 commit set 에 포함되지 않고 분리 사유 명시 후 종료.
- `build_static_report_label_cleanup_round.py` 가 Phase 1 매니페스트에서 추적 / 보류 / 제거 중 하나로 명시 분류될 때까지는 `partial`. ignored-only 파일이라 `git status --ignored` 또는 `git check-ignore` 결과가 매니페스트에 통합되어야 한다.
- `git -C <worktree-path>` 가 `safe.directory` 검증에 실패하여 blocked validation state 가 발생하면 `partial`.
- dangling 디렉토리 (`sad-dewdney`) inventory manifest 가 작성되었으나 사용자 승인 gate 미통과 시 `partial`.

`complete` 로 종료되기 위한 추가 조건:

- 모든 staging 라운드가 Unclassified 없이 5분류 중 하나에 할당되고, Bucket C 가 백업 후 제거되며, Bucket D 가 처리되거나 의도된 보류 상태로 종료된다.
- tracked disposition manifest (`docs/Iris/iris-worktree-cleanup-phase4-disposition-manifest.json`) 가 모든 제거 path 와 archive SHA-256 을 수록하고 JSON parse 검증을 통과한다.
- dangling inventory manifest (`docs/Iris/iris-worktree-cleanup-phase6-dangling-inventory.json`) 가 file count / size / per-file SHA-256 / external archive SHA-256 / 사용자 승인을 모두 포함하고 JSON parse 검증을 통과하거나, sad-dewdney 가 보류 결정으로 보존된다.
- validation command 4종 모두 exit code 0 이며 blocked validation state 가 없다.
- registered worktree triage 결과가 사용자 승인되고, dangling 디렉토리 처리 방향이 명시된다.
- Commit A / B / C 모두 생성되어 worktree 상태가 in-progress 라운드와 보존 영역만 남는다.
- `.claude/settings.local.json` 처리 결정 명시 (기본은 제외).
- `build_static_report_label_cleanup_round.py` 가 추적 / 보류 / 제거 중 하나로 결정됨 (Phase 1 매니페스트에 ignored 파일 가시화 결과 포함).
