# Iris_Refactoring_Plan_Review_v4.md

> Review target: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v4.0, 2026-06-07)
> Review template: `docs/REVIEW_TEMPLATE.md`
> Upstream documents:
> - `docs/Iris/Iris_Refactoring_Plan_Review_v3.md` (v3 review, PASS, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review_v2.md` (v2 review, PASS with minor revisions, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review.md` (v1 review, WARN, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap.md` (Draft, 2026-06-07)
> - `docs/PLAN_TEMPLATE.md`
> Reviewer date: 2026-06-07
> Verification scope: v3.0 → v4.0 변경분 내적 일관성 + v3 review의 Non-Critical 4.1~4.5 반영 여부 + v4.0이 self-catch한 2건의 정확성 보강 평가 + PowerShell `$LASTEXITCODE` 접근 명시 여부

---

## 1. Verdict

**PASS** — Phase 1 진입 가능. 본 review가 제기하는 항목은 모두 Non-Critical polish 수준이며, 어느 항목도 진입을 차단하지 않는다.

---

## 2. Executive Summary

v4.0은 v3 review의 **Non-Critical 4.1~4.5를 전수 반영**했고, 추가로 **v3 review가 놓친 정확성 결함 2건을 maintainer가 self-catch**해 자발적으로 수정했다. 두 self-catch는 본 reviewer가 v3 review에서 명령을 실제로 시뮬레이션하지 않고 표면적으로만 평가한 결과 놓친 실질적 정확성 issue다.

**Self-caught beyond v3 review scope**:
- **Git SHA 문자열 `<` 비교가 시간순/조상 관계를 보장하지 않음** — v3.0이 도입한 `baseline_capture_commit < 첫 코드 commit` 규칙은 hex string 비교에 불과해 forensic 가치가 없었다. v4.0이 `git merge-base --is-ancestor <baseline> <first>` exit 0 + 두 SHA 비동일성 검사로 교체. baseline screenshot 사후 촬영 forensic이 비로소 실제로 작동.
- **`git diff <path>`만으로는 staged 변경과 untracked 추가를 잡지 못함** — v3.0의 Pulse wrapper untouched validation `git diff Iris/.../Pulse/.../IrisDesc/`는 working tree vs HEAD만 비교. staged-only 변경(아직 commit 안 됨)이나 untracked 신규 파일은 빈 diff로 통과. v4.0이 `git status --short -- <path>` + `git diff --name-only HEAD -- <path>` 조합으로 보완.

**v3 review Non-Critical 5/5 반영**:
- 4.1 baseline_v24 필터 정렬 → `phase1_active_script_manifest.txt` 신설 + baseline·closeout 동일 manifest+필터 정렬
- 4.2 `git diff --exit-code` → Change 4 validation 명령에 명시
- 4.3 Change 4 셀 편집 코멘트 → Implementation Notes로 이동
- 4.4 "모든 phase 공통" Bootstrap 범위 → "Phase 9a/9b 한정"으로 정정
- 4.5 chunk count hard-code → `baseline_layer3_chunk_count` / `baseline_usecase_chunk_count` 등재

**Primary strengths**:
- **`phase1_active_script_manifest.txt`** 신설로 "active 한정" 측정에 단일 진리 입력 패턴 확립 — 향후 다른 active-한정 metric 추가 시 동일 manifest 재사용 가능
- **`git merge-base --is-ancestor` 기반 forensic** — 단순 문자열 비교가 아닌 git history 기반 정확한 ancestor 관계 검증
- **Pulse wrapper untouched 2-command 조합** — `git status --short`(staged/untracked 포함) + `git diff --name-only HEAD`(working tree 백업) 양방향 검증
- **baseline metrics 11 → 13** chunk count 2종 추가로 generator-emitted artifact의 변경 가능성을 baseline에 등재
- v3 review가 식별한 모든 Non-Critical을 phase 진입 전 일괄 흡수

**Primary risks**:
- 없음 (Critical 수준). 본 review는 3건의 매우 미세한 polish 항목만 식별.

**Execution should proceed?**: **Yes, immediately.** Phase 1 진입 전 필수 수정 없음. 본 review의 Non-Critical은 모두 phase 진행 중 또는 다음 plan 갱신 시 흡수 가능.

---

## 3. Critical Issues

**없음.** v4.0은 v3 review의 모든 Non-Critical을 해소했고, v3 review가 놓친 2건의 정확성 issue도 maintainer self-catch로 closure. v4.0이 도입한 신규 메커니즘(`git merge-base --is-ancestor`, 2-command Pulse wrapper untouched, active script manifest) 중 어느 것도 Critical 결함을 노출하지 않는다.

---

## 4. Non-Critical Issues

### 4.1 PowerShell `$LASTEXITCODE` 접근 명시 부족

§6 Change 9b Manual QA Checklist Schema와 §12 Quantitative Closeout Criteria Change 9b 행에서 `git merge-base --is-ancestor <baseline_capture_commit> <first_code_commit>`의 exit code로 PASS/FAIL을 판정한다. PowerShell은 native exe의 exit code를 자동으로 throw하지 않으므로 `$LASTEXITCODE`에 명시적으로 접근해야 한다.

현재 plan 본문:
```powershell
git merge-base --is-ancestor <baseline_capture_commit> <first_code_commit>
```
exit code `0` 일 때만 유효.

권장 보완 (PowerShell 자동화 시점에 필요):
```powershell
git merge-base --is-ancestor <baseline_capture_commit> <first_code_commit>
if ($LASTEXITCODE -eq 0) {
  # ancestor — baseline 유효
} elseif ($LASTEXITCODE -eq 1) {
  # not ancestor — baseline 사후 촬영 또는 무관 분기
} else {
  # error — git 호출 실패
}
```

또한 두 SHA 비동일성 검증도 다음과 같이 명시 가능:
```powershell
$baselineSha = git rev-parse <baseline_capture_commit>
$firstCodeSha = git rev-parse <first_code_commit>
if ($baselineSha -ne $firstCodeSha) {
  # 서로 다른 commit — 정상
}
```

권장 수정: §6 Change 9b Manual QA Checklist Schema 규칙 절 또는 §7 Validation Plan에 PowerShell 자동화 시 `$LASTEXITCODE` 접근 패턴을 한 블록으로 추가.

### 4.2 상단 status line "Draft v3.0" 미수정

파일 line 3:
```
> 상태: Draft v3.0 (revised per `Iris_Refactoring_Plan_Review_v2.md` 2026-06-07)
```

변경 이력은 v4.0까지 명시되어 있으나 status line은 v3.0 그대로. 사용자가 status line만 보면 현재 버전을 v3.0으로 오인할 수 있음. cross-document 인용에도 영향.

권장 수정:
```
> 상태: Draft v4.0 (revised per `Iris_Refactoring_Plan_Review_v3.md` 2026-06-07)
```

### 4.3 `git status --short -- <path>` 와 `git diff --name-only HEAD -- <path>` 의 역할 분담 명시 부족

§6 Change 9b Validation `Pulse wrapper untouched` 행:
```
git status --short -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/
+ git diff --name-only HEAD -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/
```

두 명령은 일부 영역이 중복 (staged + working tree)이고 `git status --short`가 단독으로도 staged + working tree + untracked를 모두 잡는다. `git diff --name-only HEAD`의 추가 가치는 redundancy(`git status` 자체 fault에 대한 safety net) 또는 PowerShell 환경에서의 exit code 다양화 가능성.

현재 plan은 두 명령의 역할 분담을 명시하지 않음. 다음 둘 중 하나 권장:
- 옵션 A: 한 줄 설명 추가 — "두 명령의 합집합으로 staged/working/untracked 어느 layer에서든 변경이 잡히도록 보강"
- 옵션 B: `git status --short -- <path>` 단독 사용 + "필요 시 `git diff --name-only HEAD` 보조"로 단순화

본 review는 옵션 A 권장 (현재 redundancy의 의도 보존).

---

## 5. Scope Review

### Scope Drift
**없음.** Scope(§2), Out Of Scope, Non-Goals(§3)가 roadmap의 Constraints/Non-Goals와 일관 유지. v4.0이 §5 Code 절 및 Generated Artifacts 절을 그대로 유지.

### Missing Scope
v3 review에서 식별한 missing scope 1건(Iris/build/description/v2/output 분류 owner):
- 본 review 다시 확인 — v4.0이 `phase1_artifact_source_classification.md` deliverable로 흡수. Phase 1 inventory가 산출. ✓

본 review에서 새로 발견한 missing scope: 없음.

### Explicitly Out Of Scope Consistency
**일관성 양호.** v3.0과 동일하게 모순 없음. Non-Goals 9개 항목(v3.0의 8개 + `implemented_only` claim 금지) 유지.

---

## 6. Validation Review

### Missing Validation
- 본 review 4.1: PowerShell `$LASTEXITCODE` 접근 명시 누락

### Weak Validation
v3 review에서 식별한 weak validation 모두 v4.0에서 해소:
- `baseline_test_count` parser → v3.0 PowerShell extraction 예시 유지
- `Compare-Object` JSON 깊이 한계 → v3.0 + v4.0 `git diff --no-index --exit-code` 명시
- PowerShell regex `|` vs 셀 escape → v3.0 머리말 규약 유지
- `Get-ChildItem` `__pycache__` 처리 → v3.0 + v4.0 active script manifest 추가
- 본 v4 review 4.1의 `$LASTEXITCODE`는 weak validation 잔여 가능

### Validation Ceiling Risk
**낮음 — 적극적으로 차단됨.** §7 Validation Limits 13개 유지. v4.0에서 `git merge-base --is-ancestor` + SHA 비동일성 forensic으로 Change 9b의 `implemented_only` 강등 trigger가 한 단계 더 정밀해짐.

### Validation Practicality
- **realistically executable**: 양호. Critical 없음. PowerShell `$LASTEXITCODE` 접근 패턴이 자동화 시 필요하나, manual review 시점에는 명령 실행 후 console에서 exit code를 직접 확인하는 것으로 대체 가능.
- **proportionate to risk surface**: 양호. Pulse wrapper 2-command redundancy + Manual QA forensic 강화로 9b risk를 더 정밀하게 차단.
- **appropriately scoped**: 양호. Phase 10 position carryover 정당화 유지.
- **free from unnecessary ceremony**: 양호. v4.0이 추가한 active script manifest는 후속 Phase에서 재사용 가능한 single source of truth라 ceremony 아닌 discipline.

---

## 7. Governance Review

### Philosophy.md Compliance
**준수.** §11 Governing Document Source 12개 항목 인용 출처와 함께 유지.

### Architecture Boundary
**준수.** Hub & Spoke, runtime/build-time separation, Recipe/Right-click 2-track 유지.

### Runtime / Build-Time Separation
**준수.** Phase 1~8/10은 build-only, Phase 9a는 behavior-neutral runtime, Phase 9b는 runtime + UI + dispatch surface.

### FAIL-LOUD Preservation
**준수.** §11 운영 원칙 `No silent compatibility shim` 유지. v4.0이 추가한 `git merge-base --is-ancestor` + SHA 비동일성 forensic은 silent baseline 사후 촬영을 명령 exit code 단계에서 차단. `git status` + `git diff` 2-command은 silent staged/untracked 변경을 차단.

### Authority Ownership
**준수.** §8 Authority Surface "Concerns controlled" 유지.

### Contract Compliance
- `iris_refactoring_final_roadmap_closeout.md` 봉인 영역 침범 없음.
- `phase3_quality_gates_q5_split.md` 봉인 충돌 회피 유지.
- `Iris_Refactoring_Roadmap.md` §14의 6개 conflict gate schema 유지.
- `PLAN_TEMPLATE.md` 12-section 구조 준수.

---

## 8. Risk Surface Touch

### Authority Surface
**Concerns controlled.** v4.0 변경 없음.

### Runtime Behavior Surface
**Concerns** (Phase 9a low / Phase 9b high). v4.0이 Change 9b forensic 강화 (ancestor 명령 + SHA 비동일성).

### Compatibility Surface
**Concerns** — v3.0과 동일. Pulse compat wrapper 검증을 2-command 조합으로 강화.

### Sealed Artifact Surface
**Concerns**. v3.0의 §5 16+개 sealed artifact 보호 유지 + v4.0 chunk count baseline 등재로 정량 보호 추가.

### Public-Facing Output Surface
**Conditional concerns** — Phase 9b 시 concerns. v4.0 변경 없음.

---

## 9. Risk Review

### Architecture Risk
- v4.0이 변경 없음. mitigation 모두 유지.

### Runtime Risk
- Phase 9b runtime Lua 변경 mitigation에 `git merge-base --is-ancestor` + baseline 시점 forensic 명시 추가.

### Compatibility Risk
- Change 6 mitigation의 `_archive`/`historical` 제외 → v4.0이 `phase1_active_script_manifest.txt` 입력 기반으로 강화. legacy/reproduction script 자동 제외 보장.

### Regression Risk
- 모든 mitigation 유지. chunk count baseline 등재로 generator-emitted 변경 추적 가능.

### Operational Risk
- 13-Change 계획 (v4.0이 active script manifest 추가했지만 Change 수는 12 유지).
- partial closeout 누적 추적은 §12 의미 분리.
- PowerShell `$LASTEXITCODE` 접근 미명시는 자동화 시점의 operational risk (본 review 4.1).

### Validation Risk
- approved diff `surface` 필드 + cross-reference 유지.
- `implemented_only` 오용 차단 유지.
- manual QA trigger 6번째 (`bootstrap/dispatch module 변경`) 유지.
- nested PSCustomObject 한계 → `git diff --no-index --exit-code` 명시.
- baseline screenshot 사후 촬영 → `git merge-base --is-ancestor` 명령 결과 검증 (v4.0 정정).
- Pulse wrapper untouched → `git status` + `git diff` 2-command (v4.0 보강).

### Governance Risk
- `additive amendment preference` 등 운영 원칙 라벨링 유지.
- gate enforcement는 4종 schema + active script manifest로 강화.

---

## 10. Required Revisions

**없음.** v4.0은 Phase 1 진입 전 차단성 수정 사항이 없다.

본 review의 Non-Critical 4.1~4.3는 모두 polish 수준이며 다음 시점에 흡수 가능:

| Non-Critical | 흡수 시점 | 처리 비용 |
| --- | --- | --- |
| 4.1 PowerShell `$LASTEXITCODE` 접근 패턴 | §7 또는 §6 Change 9b에 PowerShell 자동화 블록 추가 | 5분 |
| 4.2 status line v3.0 → v4.0 갱신 | 즉시 한 줄 수정 | 30초 |
| 4.3 `git status` + `git diff` 역할 분담 명시 | §6 Change 9b 셀에 한 줄 설명 추가 | 1분 |

전체 7분 작업.

---

## 11. Final Recommendation

**PASS.**

v1.0(WARN) → v2.0(PASS w/ minor) → v3.0(PASS) → v4.0(PASS, 더 단단해짐). 4 iteration 만에 execution-ready 상태에서 한 단계 더 정확성 보강 단계로 진입.

v3.0 → v4.0의 핵심 progress:

1. **v3 review의 Non-Critical 5/5 전수 반영** (active script manifest, exit-code 플래그, 셀 코멘트 이동, Manual Validation 범위 한정, chunk count baseline 등재)
2. **v3 review가 놓친 정확성 결함 2건 self-catch** (string SHA 비교 vs git ancestor 관계, git diff 단독 vs status+diff 2-command 조합)
3. **새 거버넌스 pattern** (`phase1_active_script_manifest.txt` single source of truth, `git merge-base --is-ancestor` forensic, Pulse wrapper 2-command 검증)
4. **§12 Quantitative Closeout Criteria 강화** (Change 1에 13/13 metric + manifest 산출, Change 6에 manifest 입력, Change 9b에 ancestor 명령 + SHA 비동일성 + 2-command)

### Blocking conditions
없음.

### Required next actions
1. **Phase 1 진입** — `phase1_inventory_readpoint.md`, `phase1_artifact_source_classification.md`, `phase1_batch1_import_graph.md`, `phase1_conflict_resolution_gate.md`, `phase1_pulse_wrapper_usage_inventory.md`, `phase1_baseline_metrics.md`, `phase1_active_script_manifest.txt` 7종 + `approved_diff_log.md` = 8종 deliverable 산출.
2. **§5 Path Existence Verification 전수 `True` 확인** + chunk enumerate를 `baseline_layer3_chunk_count` / `baseline_usecase_chunk_count`로 봉인.
3. **`baseline_test_count` 봉인** — §7 parser 적용 후 `$status == 'OK'`일 때만 봉인.
4. **`phase1_active_script_manifest.txt` 산출** — active 분류 build script 경로를 한 줄당 한 경로로 작성. Change 6의 baseline ↔ closeout 정렬에 입력.
5. **conflict gate 6/6 + 13개 baseline metric 충족** → Phase 1 `complete` 판정.
6. **Phase 2~10 순차 진입** — 각 Change Validation 표 + §12 Quantitative Closeout Criteria 동시 충족.
7. **본 review의 Non-Critical 4.1~4.3** — phase 진행 중 또는 다음 plan 갱신 시 흡수.

### Optional follow-ups (non-blocking)
- 본 review 4.1: PowerShell `$LASTEXITCODE` 접근 블록 추가.
- 본 review 4.2: status line v4.0 갱신.
- 본 review 4.3: Pulse wrapper 2-command 역할 분담 한 줄 추가.

### Out of scope for this review
- 코드 회귀 검증 (각 phase 실행 시점에 수행)
- `docs/EXECUTION_CONTRACT.md` 본문 대조 (별도 검증)
- Pulse / Echo / Fuse / Nerve 영향 분석 (Non-Goals)
- 입력 roadmap 본문 재대조 (roadmap review에서 처리)
- v1·v2·v3 review의 closeout 검증 (본 review가 v3 → v4 변경분에 한정)

---

## 12. Reviewer Notes

### v3.0 → v4.0 변경 반영 매트릭스

| v3 review 항목 | v4.0 반영 상태 | 비고 |
| --- | --- | --- |
| Non-Critical 4.1 (baseline_v24 필터 정렬) | ✅ 완전 반영 | `phase1_active_script_manifest.txt` 신설 + baseline·closeout 동일 manifest |
| Non-Critical 4.2 (`git diff --exit-code`) | ✅ 완전 반영 | Change 4 Validation에 `--exit-code` 명시 + Implementation Notes에 exit code semantics |
| Non-Critical 4.3 (Change 4 셀 편집 코멘트) | ✅ 완전 반영 | Compare-Object 제거 메모를 Implementation Notes로 이동 |
| Non-Critical 4.4 (Bootstrap 범위 한정) | ✅ 완전 반영 | §7 Manual Validation "Phase 9a/9b 한정" 명시 |
| Non-Critical 4.5 (chunk count baseline) | ✅ 완전 반영 + 강화 | `baseline_layer3_chunk_count`, `baseline_usecase_chunk_count` 신설 + 13/13 metric으로 등재 |
| v3 review가 놓친 SHA 문자열 비교 (v4.0 self-catch) | ✅ self-catch | `git merge-base --is-ancestor` + SHA 비동일성 검사로 교체 |
| v3 review가 놓친 git diff 단독 한계 (v4.0 self-catch) | ✅ self-catch | `git status --short` + `git diff --name-only HEAD` 2-command 조합 |

### v3 review reviewer self-reflection

본 reviewer가 v3 review에서 명령을 실제 실행/시뮬레이션하지 않고 표면적으로만 평가해 다음 2건을 놓쳤다:

1. **`baseline_capture_commit < 첫 코드 commit` 규칙**: v3.0이 도입한 이 규칙은 SHA hex string의 lexicographic 비교를 사용한다. 실제로 SHA는 hash 값이며 시간순/조상 관계와 무관하다. 예: `0a1b2c... < f9e8d7...`은 string으로는 true지만 두 commit의 ancestor 관계와 일치할 보장이 전혀 없다. v3 review에서 이 결함을 catch했어야 했다.
2. **`git diff Iris/.../Pulse/.../IrisDesc/` 단독 사용**: working tree vs HEAD 비교만 수행. staged-only 변경 (commit 안 된 `git add`)이나 untracked 신규 파일은 잡지 못한다. "빈 diff" expected가 staged + untracked를 통과시키는 결함이었다. v3 review에서 git 명령 semantics를 시뮬레이션했다면 catch 가능했다.

이 2건은 v4.0 maintainer가 self-catch해 modular하게 보강한 결과 plan의 정확성이 한 단계 올라갔다.

### Spot-checked facts (verified 2026-06-07)
- `git merge-base --is-ancestor <A> <B>` exit code semantics 확인: 0 = A is ancestor of B, 1 = not ancestor, other = error. v4.0 본문과 일치.
- `git status --short -- <path>`는 staged + working tree + untracked를 모두 path-scoped로 출력 — v4.0 본문과 일치.
- `git diff --name-only HEAD -- <path>`는 working tree vs HEAD의 파일명만 출력. staged-only 변경 미포함 (그래서 `git status`와 조합 필요).
- §5 Generated Artifacts 16+개 경로 v3 review에서 실파일 일치 spot check 완료 — v4.0 변경 없음.
- `phase1_active_script_manifest.txt` 신규 deliverable로 §5 Docs에 명시 — Files 절과 정합.

### Uncertainty disclosure
- PowerShell `git` native exe 호출 시 `$LASTEXITCODE` 접근이 명령마다 일관되게 동작하는지는 PowerShell 5.x vs 7.x 버전 차이 가능성. 본 review에서 단일 버전 검증.
- `git rev-parse <commit>`이 short SHA vs full SHA 비교 시 동일성 판정 일치 여부는 git 버전 의존. v4.0이 사용하는 비교 패턴(`-ne`)은 PowerShell string 비교이므로 동일 길이 SHA여야 정확한 비교.
- `luac -p`의 Kahlua 환경 호환성은 v1·v2·v3·v4 review 모두 미확인 (잔여 uncertainty 유지).

### Review limitations
- 본 review는 v3 → v4.0 변경분 검토 중심. v3.0에서 PASS한 영역(특히 §11 governance citation, schema 4종, Closeout State Semantics)은 재검증하지 않음.
- 본 reviewer는 PowerShell 5.x 환경 가정 평가. PowerShell 7.x에서의 `$LASTEXITCODE`나 native exe 통신 차이는 별도 검증 필요.
- `phase1_active_script_manifest.txt`의 실제 산출 형식(한 줄당 한 경로, encoding, line ending)이 plan에 정의되어 있으나, Phase 1 실행 시점에 Windows CRLF vs Unix LF 등 환경 차이로 인한 issue 가능성은 phase 진입 시 별도 sanity check 권장.

### Future follow-up suggestions
- **Phase 1 deliverable 산출 직후 short follow-up review** — 8종 deliverable의 schema 충족 + 13개 baseline metric 측정값의 sanity check + `phase1_active_script_manifest.txt`의 active 경로 분류 적정성 검토.
- **Change 9b entry gate deliverable 별도 review** — `phase9b_manual_qa_checklist.md`의 scenario coverage 적정성 + baseline 시점 forensic 실제 동작 확인.
- **본 plan이 도입한 5종 schema** (Conflict Resolution Gate / Per-Directory Disposition / Manual QA Checklist / Approved Diff Log / Active Script Manifest) + PowerShell 표기 규약 + `git merge-base --is-ancestor` 기반 forensic을 Iris 외 다른 Pulse 모듈 refactor에서 재사용 가능한 governance pattern으로 추출 권장.
- **`additive amendment preference` 등 운영 원칙의 governing docs 명시 인용**이 확보되는 시점에 §11에서 Plan Operating Principles → Governing Document Source로 이관 (v3.0이 약속한 절차).
- **PowerShell `$LASTEXITCODE` 접근 패턴**이 plan에 명시되면 다른 git-exit-code 의존 validation(Change 4 `git diff --no-index --exit-code`, Change 9b `git merge-base --is-ancestor`)에도 동일 패턴 적용. 일관성 확보.
