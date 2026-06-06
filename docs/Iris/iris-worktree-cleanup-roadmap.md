# Iris Worktree Cleanup Roadmap

> 상태: Draft
> 기준일: 2026-06-05
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> 목적: Iris 작업트리에 누적된 DVF 3.3 라운드 잔여물을 무손실로 정리하고, 미커밋된 신규 코드/런타임/문서 변경을 의미 단위로 봉인한다.

## 1. Problem Statement

- Iris 작업트리에 DVF 3.3 다회차 리팩토링을 거치면서 staging 잔여물이 1,818개 / 약 464MB 규모로 누적되었다.
- 신규 빌드 도구 2개, validator 2개, 테스트 4개, 보조 스크립트 1개가 작성되었으나 커밋되지 않은 채로 남아 있다.
- 완료된 plan 3건이 `docs/Iris/` 루트에서는 deleted 상태이고 `docs/Iris/Done/`에는 untracked 상태로 이동되어, git 시점에는 단순 삭제로 보인다.
- 빌드 파이프라인 (`compose_layer3_*`) 수정사항과 그 산출물인 `IrisLayer3DataChunks/Chunk*.lua` 8개, Wiki UI 2개가 한 묶음으로 커밋되지 않으면 결정론적 재현성이 끊긴다.
- `.claude/worktrees/` 아래 두 개의 워크트리가 정리되지 않고 남아 있다.
- 작업트리의 신호-잡음 비율이 낮아 다음 라운드 진입 판단을 흐린다.

---

## 2. Current State

- **추적 modified (21개)**:
  - 빌드 파이프라인: `compose_layer3_text.py`, `compose_layer3_body_profile.py`, `compose_layer3_item.py`, `compose_layer3_render.py`, `test_compose_layer3_text_v2.py`
  - 데이터: `dvf_3_3_decisions.jsonl`
  - 런타임 산출물: `Chunk002/003/004/005/007/008/010/011.lua`
  - UI: `IrisContextMenu.lua`, `IrisWikiPanel.lua`
  - 상위 문서: `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`
- **추적 deleted (3개)**: `docs/Iris/` 루트 plan 3건 — 실제로는 `docs/Iris/Done/`로 이동된 것이며, 추적되지 않은 동일 파일이 untracked로 보인다.
- **미추적 (49 그룹)**:
  - 신규 빌드 도구 2: `build_legacy_active_silent_current_surface_guard_round.py`, `build_static_report_label_cleanup_referent_recovery_round.py`
  - 신규 validator 2: `validate_legacy_active_silent_current_surface_guard.py`, `validate_layer4_absorption_current_surface_guard.py`
  - 신규 테스트 4: `test_current_authority_source_path_guard.py`, `test_layer4_absorption_current_surface_guard.py`, `test_layer4_trace_edge_authority_admission_round.py`, `test_legacy_active_silent_current_surface_guard.py`
  - 신규 스크립트 1: `tools/check_lua_syntax.ps1`
  - `docs/Iris/Done/` 신규 plan/review/closeout/walkthrough 23+ 건
  - `docs/Iris/` 루트 진행 중 라운드 1건: `acquisition-lexical-current-readpoint-reconciliation-round` (plan + closeout)
  - `Iris/build/description/v2/staging/` 하위 다수
- **`.gitignore` 변경**: 신규 코드와 5개 compose_contract_migration 라운드 디렉토리 + `manual_in_game_validation` 화이트리스트 추가.
- **staging 화이트리스트 (보존 대상)**:
  - `compose_contract_migration/legacy_active_silent_current_surface_guard_round/`
  - `compose_contract_migration/structural_signal_scope_re_seal_round/`
  - `compose_contract_migration/layer4_boundary_current_corpus_lock_round/`
  - `compose_contract_migration/layer4_trace_edge_authority_admission_round/`
  - `compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/`
  - `manual_in_game_validation/`
  - `reviews/*.acquisition.jsonl`
- **격리 네임스페이스 (보존 대상)**: `Iris/_archive` (216K), `Iris/_dev` (16K), `Iris/_docs` (8MB)
- **워크트리**: `.claude/worktrees/loving-newton-6327e6` (modified content), `.claude/worktrees/sad-dewdney`
- **현재 validation 신뢰도**: pytest는 기존 테스트만 통과. 신규 테스트 4개는 아직 커밋 전이라 CI 검증 이력 없음.

---

## 3. Desired Outcome

- 작업트리에 신규 빌드/런타임/문서 변경이 의미 단위 커밋으로 봉인되어 있다.
- staging 디렉토리는 화이트리스트 라운드 + 진행 중 라운드만 남아 있다.
- `.claude/worktrees/` 아래는 활성 워크트리만 남아 있다.
- 진행 중 라운드 (acquisition-lexical-current-readpoint-reconciliation-round)의 데이터/문서는 무손실 보존된다.
- 제거된 staging 자산은 빌드 파이프라인으로 재생성 가능함이 1회 이상 확인되거나, tar 백업으로 복구 가능하다.
- 다음 DVF 3.3 라운드 진입 시 git status가 잡음 없이 진행 중 작업만 보여준다.
- 작업트리 신호-잡음 비율이 다음 라운드 판단을 흐리지 않는 수준으로 정상화된다.

---

## 4. Constraints

- `Philosophy.md` / `DECISIONS.md` / `ARCHITECTURE.md` / `ROADMAP.md` 준수.
- **Determinism preservation**: `compose_layer3_*` 모듈 수정과 그 산출물인 `Chunk*.lua` 변경은 동일 커밋에 묶여야 한다.
- staging 화이트리스트 7개 항목은 절대 건드리지 않는다.
- 진행 중 라운드 산출물 (`docs/Iris/` 루트에 plan이 남아 있는 라운드의 staging 디렉토리)은 절대 제거하지 않는다.
- `Iris/_archive`, `Iris/_dev`, `Iris/_docs` 네임스페이스는 변경 금지.
- Authority surface / sealed artifact를 새로 만들지 않는다 (이 로드맵은 정리 절차이지 새 권한을 도입하지 않는다).
- FAIL-LOUD 패턴 유지.
- runtime/build-time 분리 유지.

---

## 5. Non-Goals

- 빌드 파이프라인 재실행 / Layer3 데이터 전체 재생성.
- `compose_layer3_*` 모듈 구조 리팩토링.
- staging 디렉토리 구조 재설계.
- DVF 3.3 의 새 라운드 진입.
- 릴리스 패키징 / Steam Workshop 업로드 준비.
- `_archive` / `_dev` / `_docs` 네임스페이스 손질.
- 신규 plan 작성 또는 기존 plan 내용 수정.
- 신규 sealed artifact 도입.

---

## 6. Proposed Approach

3계층 정리를 순차 적용한다.

1. **무위험 자동 정리** — 캐시·임시 파일·빈 디렉토리 등 손상 불가 대상부터 제거하여 후속 phase의 노이즈를 줄인다.
2. **커밋 단위 묶음** — 미커밋 변경을 의미 단위 3개 커밋으로 분리해 history 가독성과 rollback 단위를 확보한다.
3. **선별적 staging 정리** — 보존/제거 매니페스트를 먼저 만들고, tar 백업을 확보한 뒤, 화이트리스트와 진행 중 라운드 외 staging 라운드만 제거한다.

리스크 감소 원칙:
- 모든 제거 결정은 phase 1에서 만든 매니페스트를 입력으로만 동작한다 (즉흥 판단 금지).
- staging 라운드 제거 전 tar 백업 1회를 작업트리 외부에 의무 보관.
- 커밋은 의미 단위로 분리해 단일 revert로 rollback 가능하게 한다.
- 결정론적 재현성을 보장해야 하는 빌드 코드 + 산출물 페어 (커밋 B)는 분리 금지.

---

## 7. Authority / Surface Impact

### Authority Surface

None — 이 로드맵은 권한/책임 경계를 바꾸지 않는다.

### Runtime Behavior Surface

변경됨 — `Chunk{002..011}.lua`, `IrisContextMenu.lua`, `IrisWikiPanel.lua` 의 기존 수정사항이 커밋되면 런타임 표현이 봉인된다. 단, 이 로드맵은 새 변경을 도입하지 않고 **이미 존재하는 변경을 봉인하는 절차**다.

### Compatibility Surface

변경됨 — `.gitignore` 화이트리스트 항목 (신규 코드 9개 + staging 라운드 6개) 추가가 커밋된다. 이로써 staging 신규 라운드의 보존 정책이 확정된다.

### Sealed Artifact Surface

화이트리스트에 명시된 5개 `compose_contract_migration` 라운드 + `manual_in_game_validation` 산출물은 본 로드맵 이후 봉인 보존 대상이 된다. 화이트리스트 외 staging 라운드는 봉인 대상이 아니었고, 제거 후에도 봉인 위반이 아니다.

### Public-Facing Output Surface

변경됨 — `IrisLayer3DataChunks/Chunk*.lua` 는 게임 내 표시되는 한국어 설명 데이터의 공개 표면이며, 본 로드맵의 커밋 B가 그 표면을 확정한다.

---

## 8. Phases

### Phase 1 — 정리 매니페스트 작성

Goal: 보존/제거 목록을 한 곳에 묶어 후속 phase의 입력으로 사용한다.

Primary Changes:

- staging 하위 모든 라운드 디렉토리를 목록화.
- 각 라운드를 4분류 중 하나로 할당:
  - (a) **화이트리스트** — `.gitignore` 신규 항목과 일치
  - (b) **진행 중** — `docs/Iris/` 루트에 대응 plan이 남아 있음
  - (c) **완료** — `docs/Iris/Done/` 에 대응 plan/closeout 존재
  - (d) **분류 불가** — 위 셋 중 어디에도 매칭 안 됨
- 산출물: `docs/Iris/iris-worktree-cleanup-phase1-manifest.json`

Expected Risks:

- 라운드 디렉토리명이 plan 파일명과 정확히 매칭되지 않을 가능성.
- (d) 분류 불가 라운드가 다수 발견될 가능성.

Expected Validation:

- 매니페스트의 모든 라운드 디렉토리에 4분류 중 하나가 할당되었는지 확인.
- 화이트리스트가 `.gitignore` 변경 내용과 1:1 일치 검증.

Expected Deliverables:

- 보존/제거 대상 매니페스트 1개.

---

### Phase 2 — 무위험 자동 정리

Goal: 누구도 손상시킬 수 없는 명백한 잔재 제거.

Primary Changes:

- staging 하위 `__pycache__/` 전체 제거.
- staging 하위 빈 디렉토리 제거.
- 명백한 임시 파일 패턴 (`*.tmp`, `*.bak`) 제거.

Expected Risks:

- 거의 없음 (Python 캐시는 재생성됨).

Expected Validation:

- 제거 전후 staging 파일 수 비교.
- 신규 빌드 도구 1회 import 테스트로 캐시 재생성 정상 동작 확인.

Expected Deliverables:

- 정리 전후 사이즈/파일수 비교 보고.

---

### Phase 3 — 커밋 단위 분리

Goal: 미커밋 변경을 의미 단위 3개 커밋으로 봉인.

Primary Changes:

- **커밋 A — 빌드 도구·테스트·gitignore**: 신규 빌드 도구 2 + validator 2 + 테스트 4 + `tools/check_lua_syntax.ps1` + `.gitignore` 화이트리스트.
- **커밋 B — Layer3 재빌드 봉인**: `compose_layer3_*` 4개 + `test_compose_layer3_text_v2.py` + `dvf_3_3_decisions.jsonl` + `Chunk{002..011}.lua` 8개 + `IrisContextMenu.lua`, `IrisWikiPanel.lua`. 이 묶음은 결정론적 재현성을 보존하기 위해 절대 분리 금지.
- **커밋 C — 문서 봉인**: `docs/Iris/` plan 3건의 `Done/` 이동 + `docs/Iris/Done/` 신규 plan/review/closeout/walkthrough 23+ + `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md` 갱신.

Expected Risks:

- 커밋 B를 분리하면 compose 코드 ↔ Chunk 산출물 재현성 손실.
- docs 이동이 `git mv` 미사용으로 delete + add 두 변경으로 추적되어 history rename 추적성 저하.

Expected Validation:

- 커밋 B 직후 `pytest Iris/build/description/v2/tests` 통과.
- 커밋 C 직후 `git log --follow` 로 plan 이동의 history 연속성 확인.

Expected Deliverables:

- 커밋 3개 (A → B → C 순).

---

### Phase 4 — 워크트리 트리아지

Goal: dangling 워크트리 정리.

Primary Changes:

- `git worktree list` 로 활성 워크트리 확인.
- `.claude/worktrees/loving-newton-6327e6`, `.claude/worktrees/sad-dewdney` 각각 작업 완료 여부 확인.
- 각 워크트리 디렉토리 내 uncommitted 변경 유무 확인 (`git status` in worktree).
- HEAD가 main에 머지되었는지 확인.
- 완료된 워크트리는 `git worktree remove` 로 정리.
- 진행 중인 워크트리는 그대로 둔다.

Expected Risks:

- 진행 중 워크트리를 잘못 삭제 시 작업 손실.

Expected Validation:

- 제거된 워크트리가 `git worktree list` 에서 사라졌는지 확인.

Expected Deliverables:

- 정리된 워크트리 목록 / 보존된 워크트리 목록.

---

### Phase 5 — staging 선별 정리

Goal: Phase 1 매니페스트의 제거 대상을 백업 후 삭제.

Primary Changes:

- staging 전체 tar 백업 1회 (작업트리 외부 위치, 예: `~/iris-staging-backup-<date>.tar.zst`).
- 매니페스트의 (c) **완료** 분류 라운드 디렉토리 순차 제거.
- (d) **분류 불가** 라운드는 사용자 확인 후 처리 (자동 제거 금지).
- (a) **화이트리스트** 및 (b) **진행 중** 라운드는 손대지 않는다.

Expected Risks:

- 제거된 라운드의 후속 라운드가 그 산출물을 입력으로 가정했을 가능성.
- 백업 위치를 작업트리 안에 두면 백업 의미 상실.

Expected Validation:

- 제거 후 staging 화이트리스트 라운드 디렉토리들이 그대로 있는지 확인.
- 빌드 파이프라인 1회 dry run 또는 import 검사 (선택).
- 백업 tar 무결성 확인 (`tar -tf` 으로 entry 수 검증).

Expected Deliverables:

- 백업 tar 1개 (작업트리 외부).
- 제거된 라운드 목록.

---

### Phase 6 — 사후 검증

Goal: 정리 후 작업트리 상태 안정성 확인.

Primary Changes:

- `git status` 가 진행 중 라운드 + `.claude` 워크트리 영역만 보여주는지 확인.
- `pytest Iris/build/description/v2/tests` 전체 실행.
- Chunk Lua 구문 검증 (`tools/check_lua_syntax.ps1` 적용).
- staging 사이즈 측정 (목표: 200MB 미만).

Expected Risks:

- 거의 없음 (검증 phase).

Expected Validation:

- pytest 통과.
- Lua 구문 오류 없음.
- 작업트리 신호-잡음 비율 정상화 확인.

Expected Deliverables:

- 사후 검증 보고 (간단한 텍스트).

---

## 9. Validation Expectations

### Expected Validation Depth

standard

### Expected Validation Areas

- determinism (compose_layer3 ↔ Chunk 페어 일관성)
- regression (pytest 전체)
- runtime (Chunk Lua 구문 검증)
- compatibility (`.gitignore` 화이트리스트 의도대로 동작)

### Known Validation Limits

- in-game QA 없음 (이 로드맵의 범위 밖).
- 멀티플레이 검증 없음.
- 장시간 런타임 검증 없음.
- Steam Workshop 호환성 sweep 없음.
- staging 제거 후 모든 라운드 재실행 검증 없음 (선택적 1회만).
- 백업 tar의 장기 무결성 검증 없음.

---

## 10. Risk Assessment

### High Risk

- 진행 중 라운드 (acquisition-lexical-current-readpoint-reconciliation-round) staging 데이터를 잘못 분류해 삭제하는 경우.
- 커밋 B의 compose ↔ Chunk 페어를 분리하여 결정론적 재현성을 잃는 경우.

### Medium Risk

- 워크트리 정리 중 미커밋 작업 손실.
- docs 이동이 `git mv` 미사용으로 처리되어 history 추적성 저하.
- 화이트리스트 vs 실제 staging 디렉토리명 불일치로 매니페스트 오류.
- 백업 tar 위치를 작업트리 내부에 두는 실수.

### Low Risk

- `__pycache__` 제거 후 재생성 시점 차이.
- `.gitignore` 패턴 모호성으로 인한 의도 외 추적 포함.

---

## 11. Rollback Strategy

- 각 phase는 독립 커밋 또는 독립 백업으로 분리되어 있으므로 단위별로 되돌릴 수 있다.
- **커밋 A/B/C**: `git reset --hard <prev>` 또는 `git revert <commit>` 로 rollback. 커밋 B는 분리 불가 단위이므로 전체를 revert.
- **워크트리 제거**: `git worktree add` 로 재생성 가능. 단 워크트리 내부 uncommitted 작업은 복구 불가 → Phase 4에서 반드시 사전 확인.
- **staging 제거**: Phase 5의 tar 백업으로 복구. 백업이 작업트리 외부에 있어야 의미 있음.
- **무위험 정리 (Phase 2)**: 캐시 재생성으로 자동 복구.

전체 로드맵을 중단해야 할 경우, Phase 5 진입 전에 멈추면 데이터 손실 없이 종료 가능.

---

## 12. Success Criteria

- 신규 빌드 도구 2 + validator 2 + 테스트 4 + 보조 스크립트 1 모두 커밋되어 추적됨.
- `IrisLayer3DataChunks` 변경이 단일 커밋으로 봉인됨 (compose 코드와 동일 커밋).
- staging 화이트리스트 7개 항목 그대로 보존.
- 진행 중 라운드 산출물 무손실.
- staging 사이즈 200MB 미만으로 감소.
- pytest 전체 통과.
- 작업트리 `git status` 가 진행 중 작업 영역만 표시.
- 다음 DVF 3.3 라운드 진입 시 작업트리 잡음 없음.

---

## 13. Expected Claim Boundary

This roadmap does NOT automatically imply:

- full runtime equivalence (Chunk 변경 봉인일 뿐, 정확성 검증은 별도)
- full compatibility preservation (in-game / multiplayer 미검증)
- release readiness
- deployment readiness (Steam Workshop 미준비)
- production validation
- architectural correctness
- 빌드 파이프라인 재실행 시 모든 라운드 산출물 재생성 성공
- 제거된 staging 라운드의 사후 복구 가능성 (Phase 5 백업 외 경로 없음)

unless explicitly validated later.

Do not claim success beyond validated scope.
