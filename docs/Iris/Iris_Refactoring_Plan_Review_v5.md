# Iris_Refactoring_Plan_Review_v5.md

> Review target: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v5.0, 2026-06-07)
> Review template: `docs/REVIEW_TEMPLATE.md`
> Upstream documents:
> - `docs/Iris/Iris_Refactoring_Plan_Review_v4.md` (v4 review, PASS, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review_v3.md` (v3 review, PASS, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review_v2.md` (v2 review, PASS with minor revisions, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review.md` (v1 review, WARN, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap.md` (Draft, 2026-06-07)
> - `docs/PLAN_TEMPLATE.md`
> Reviewer date: 2026-06-07
> Verification scope: v4.0 → v5.0 변경분 내적 일관성 + v4 review의 Non-Critical 4.1~4.3 반영 여부 + v5.0이 self-introduced한 3개 governance 개선 평가

---

## 1. Verdict

**PASS** — Phase 1 진입 가능. 본 review가 제기하는 항목은 매우 미세한 polish 수준이며, 어느 항목도 진입을 차단하지 않는다.

---

## 2. Executive Summary

v5.0은 v4 review의 **Non-Critical 4.1~4.3을 전수 반영**했고, 추가로 **3가지 governance 강화**를 self-introduce해 plan의 운영 안전성을 한 단계 더 올렸다. 특히 **Approved Diff Procedure에 reviewer 제약 신설**은 v1 review에서부터 weakness로 지적되어온 "approved diff self-approval 회피 경로"를 마침내 closure한다.

**v4 review Non-Critical 3/3 반영**:
- 4.1 PowerShell `$LASTEXITCODE` 접근 패턴 → 머리말 PowerShell 표기 규약에 명시 + Change 9b Manual QA matrix 행에 full pattern 적용
- 4.2 상단 status line v3.0 → v5.0 동기화
- 4.3 Pulse wrapper 2-command 역할 분담 → Change 9b Validation 셀에 명시적 설명 추가 (safety net redundancy 의도 명문화)

**v5.0 self-introduced 거버넌스 강화 3건**:
- **Markdown 표 셀 escape convention 명시** — raw 파일의 `\|`는 셀 escape이며 실행 시 `|`로 치환. 머리말 PowerShell 표기 규약에 명문화. 자동 복사-실행 워크플로 시 raw → render 단계 명시.
- **실행 cwd = repository root 고정** — 모든 상대 경로는 repo root 기준. 다른 cwd 실행 시 prefix 또는 `Set-Location` 명시 요구.
- **Approved Diff Procedure에 reviewer 제약 신설** (v5.0 핵심 governance 강화):
  - `surface = sealed_artifact / runtime / public_facing / compat` → `reviewer = 사용자만 허용`, `self` 금지
  - `surface = authority` → 기본 `reviewer = 사용자`, helper-level drift에 한해 self 허용 (with `diff_reason`에 "no authority ownership change" 명시 필요)
  - build-only intermediate artifact만 `reviewer = self` 자유 허용
  - 위반 시 phase closeout 즉시 `blocked` 강등 + entry 재작성 + 사용자 sign-off 후 재진입
  - 이로써 sealed artifact mutation 또는 silent compatibility break가 self-approved diff로 통과될 수 없게 됨

**Primary strengths**:
- v1~v4 review의 모든 Non-Critical을 누적 흡수 완료
- v1 review부터 제기되어온 "approved diff self-approval" weakness 마침내 closure
- PowerShell 표기 규약의 완성도(`|` alternation, `$LASTEXITCODE`, 셀 escape, cwd) — 자동화 가능한 명령 표기 체계 확립
- Pulse wrapper 2-command 역할 분담의 redundancy 의도 명문화
- Approved Diff reviewer 제약을 surface-based로 분류해 micro-governance 도입

**Primary risks**:
- 없음 (Critical 수준). 본 review는 3건의 매우 미세한 polish 항목만 식별.

**Execution should proceed?**: **Yes, immediately.** Phase 1 진입 전 필수 수정 없음. 본 review의 Non-Critical은 모두 phase 진행 중 또는 다음 plan 갱신 시 흡수 가능.

---

## 3. Critical Issues

**없음.** v5.0은 v4 review의 모든 Non-Critical을 해소했고, 새로 도입한 3개 governance 개선(표 셀 escape 규약, cwd, approved diff reviewer 제약) 중 어느 것도 Critical 결함을 노출하지 않는다.

---

## 4. Non-Critical Issues

### 4.1 Change 10 Validation 행과 §12 Change 10 closeout 기준의 제외 필터 불일치

§6 Change 10 Validation 표 `Validation matrix dry run` 행:
```
Expected: Change 1~9b 행 모두 포함 + 사용된 명령 PowerShell 호환 + __pycache__/_archive 제외 규칙 일관
```

§12 Quantitative Closeout Criteria Change 10:
```
phase10_validation_matrix.md가 Change 1~9b 행 전수 포함 + 모든 명령 PowerShell 호환 확인 + __pycache__/_archive/historical 제외 규칙 일관
```

§6 Change 1 baseline_v24_hardcode_count, §6 Change 6 closeout, §6 Change 6 v3.0 정정 본문 모두 **3-filter** (`__pycache__` / `_archive` / `historical`)를 canonical 규칙으로 사용. Change 10 Validation 행만 `historical`이 누락되어 **2-filter**로 표기됨.

권장 수정: §6 Change 10 Validation `Validation matrix dry run` 행 Expected 컬럼을 "`__pycache__`/`_archive`/`historical` 제외 규칙 일관"으로 통일.

영향: 매우 작음. Change 10이 마지막 통합 매트릭스 산출 phase이므로 누락된 필터 항목이 closeout 통과 시점에 catch될 가능성 높음. 사전 통일이 더 안전.

### 4.2 `surface = authority` self-approval carve-out의 self-judgment 가능성

§7 Approved Diff Procedure reviewer 제약 규칙:
```
surface = authority 인 entry는 §8에서 controlled concern으로 분류되어 있으므로 기본 reviewer = 사용자이지만,
authority ownership 이동이 없는 helper-level drift에 한해 reviewer = self 가능.
이 경우 diff_reason에 "no authority ownership change" 명시 필요.
```

이 carve-out은 의도된 유연성이지만, "no authority ownership change" 판정 자체가 maintainer self-judgment이다. 다른 surface(sealed_artifact / runtime / public_facing / compat)는 self 자체를 금지하는 데 비해 authority만 self carve-out이 있어 thin loophole 가능성.

권장 보완 (optional):
- 옵션 A: authority도 self 완전 금지로 통일.
- 옵션 B: carve-out 유지하되 "no authority ownership change" 판정의 minimum evidence를 한 줄 추가 (예: 해당 artifact가 Recipe/Right-click track 어느 쪽에도 source-of-truth가 아님을 grep으로 확인 + 산출물 reference).

본 review는 옵션 B 권장 (기존 carve-out 의도 보존 + 미세 governance 강화).

### 4.3 Change 9b Pulse wrapper untouched 셀의 inline 설명 길이

§6 Change 9b Validation `Pulse wrapper untouched` 행 Command 셀:
```
git status --short -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/
+ git diff --name-only HEAD -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/
(v4.0 확장, v5.0 역할 분담 명시: git status --short는 staged + working tree + untracked 전부를 잡는 1차 safety net이고
git diff --name-only HEAD는 working tree와 HEAD의 tracked file 변경만 잡는 보조 검증으로,
두 명령이 서로 다른 누락 시나리오를 커버하므로 둘 다 빈 출력일 때만 통과한다 — redundancy는 의도된 safety net이다)
```

내용은 정확하고 v4 review 4.3을 정확히 closure하나, 표 셀 안의 inline 설명이 길어 표 가독성을 떨어뜨림. 또한 다른 셀의 짧은 명령들과 비대칭.

권장 수정: 설명을 Change 9b Implementation Notes 절로 이동하고, Validation 셀은 두 명령만 남김. Implementation Notes에 다음 한 단락 추가:
```
Pulse wrapper untouched 검증은 두 명령을 함께 사용한다. git status --short는 staged + working tree + untracked 전부를 잡는 1차 safety net이고,
git diff --name-only HEAD는 working tree와 HEAD의 tracked file 변경만 잡는 보조 검증이다.
두 명령이 서로 다른 누락 시나리오를 커버하므로 둘 다 빈 출력일 때만 통과한다 — redundancy는 의도된 safety net이다.
```

영향: 매우 작음. 가독성/표 구조 일관성 polish.

---

## 5. Scope Review

### Scope Drift
**없음.** Scope(§2), Out Of Scope, Non-Goals(§3)가 roadmap의 Constraints/Non-Goals와 일관 유지. v5.0이 §2/§3 변경 없음.

### Missing Scope
v4 review에서 식별한 missing scope 모두 v5.0에서 유지 또는 흡수:
- Pulse compat wrapper 6개 require/use inventory → `phase1_pulse_wrapper_usage_inventory.md` deliverable ✓
- `Iris/output/` 분류 owner → `phase1_artifact_source_classification.md` + Phase 8 `phase8_artifact_source_classification.md` ✓
- `Iris/build/package/Iris/...` 미러 분류 → §5 Generated Artifacts + Phase 8 책임 ✓

본 review에서 새로 발견한 missing scope: 없음.

### Explicitly Out Of Scope Consistency
**일관성 양호.** v4.0과 동일. Non-Goals 9개 항목 + Out Of Scope 10개 항목 간 모순 없음.

---

## 6. Validation Review

### Missing Validation
없음. v4 review에서 식별한 PowerShell `$LASTEXITCODE` 접근 누락은 v5.0 머리말 + Change 9b Manual QA matrix에서 모두 closure.

### Weak Validation
v1 review의 "approved diff self-approval 회피 경로" weakness — v5.0 `reviewer` 제약으로 마침내 closure ✓. 본 review에서 추가로 식별한 weak validation: 없음.

### Validation Ceiling Risk
**낮음 — 추가 차단됨.** v5.0의 Approved Diff Procedure reviewer 제약이 ceiling 회피 경로를 surface별로 봉인. `sealed_artifact / runtime / public_facing / compat` surface는 self-approval 자체가 금지되어 manual QA gate와 sealed artifact preservation gate를 우회할 수 없음. authority는 thin carve-out 잔존 (본 review 4.2).

### Validation Practicality
- **realistically executable**: 양호. v5.0의 `$LASTEXITCODE` 패턴이 PowerShell 환경에서 자동화 가능한 형태로 명시.
- **proportionate to risk surface**: 양호. Approved Diff reviewer 제약이 surface 위험도와 정렬 (high-risk surface = self 금지, low-risk surface = self 허용).
- **appropriately scoped**: 양호.
- **free from unnecessary ceremony**: 양호. Approved Diff reviewer 제약이 ceremony가 아닌 governance discipline.

---

## 7. Governance Review

### Philosophy.md Compliance
**준수.** §11 Governing Document Source 12개 항목 인용 출처와 함께 유지.

### Architecture Boundary
**준수.** Hub & Spoke, runtime/build-time separation, Recipe/Right-click 2-track 유지.

### Runtime / Build-Time Separation
**준수.** v5.0 변경 없음. Phase 1~8/10 build-only, Phase 9a behavior-neutral runtime, Phase 9b runtime + UI + dispatch surface.

### FAIL-LOUD Preservation
**준수.** v5.0의 Approved Diff reviewer 제약이 silent self-approved drift를 surface별로 차단. 머리말의 `$LASTEXITCODE` 명시로 native exe exit code의 silent fallback 위험 해소.

### Authority Ownership
**준수.** §8 Authority Surface "Concerns controlled" 유지. v5.0의 approved diff reviewer carve-out은 authority ownership 이동 없는 helper-level drift에 한정.

### Contract Compliance
- `iris_refactoring_final_roadmap_closeout.md` 봉인 영역 침범 없음.
- `phase3_quality_gates_q5_split.md` 봉인 충돌 회피 유지.
- `Iris_Refactoring_Roadmap.md` §14의 6개 conflict gate schema 유지.
- `PLAN_TEMPLATE.md` 12-section 구조 준수.

---

## 8. Risk Surface Touch

### Authority Surface
**Concerns controlled.** v5.0의 Approved Diff reviewer carve-out이 authority surface에 thin loophole 가능성을 도입하나, "no authority ownership change" 명시 요구로 self-judgment 트래킹 가능 (본 review 4.2).

### Runtime Behavior Surface
**Concerns** — Phase 9a low / Phase 9b high. v5.0의 reviewer 제약이 runtime surface self-approval을 금지해 강화.

### Compatibility Surface
**Concerns** — v4.0과 동일. v5.0의 reviewer 제약이 compat surface self-approval을 금지해 강화.

### Sealed Artifact Surface
**Concerns**. v5.0의 reviewer 제약이 sealed_artifact surface self-approval을 금지해 강화. 이는 §10 Rollback Plan의 sealed artifact SHA drift 절차와 정합.

### Public-Facing Output Surface
**Conditional concerns** — Phase 9b 시 concerns. v5.0의 reviewer 제약이 public_facing surface self-approval을 금지해 강화.

---

## 9. Risk Review

### Architecture Risk
v5.0 추가 변경 없음. mitigation 모두 유지.

### Runtime Risk
- v5.0의 reviewer 제약으로 runtime-impact approved diff의 self-approval 차단.

### Compatibility Risk
- v5.0의 reviewer 제약으로 compat surface approved diff의 self-approval 차단.

### Regression Risk
- v5.0의 reviewer 제약으로 sealed_artifact approved diff의 self-approval 차단 → SHA drift silent통과 위험 추가 감소.

### Operational Risk
- v5.0의 PowerShell 표기 규약 확장 (`$LASTEXITCODE`, cwd, 셀 escape)으로 자동화 시점의 operational risk 추가 감소.

### Validation Risk
- v5.0의 reviewer 제약으로 approved diff 회피 경로 closure → v1 review부터 누적되어온 self-approval weakness 해소.
- `$LASTEXITCODE` 명시로 native exe exit code silent fallback 위험 해소.
- baseline screenshot 사후 촬영 → `$LASTEXITCODE` 기반 forensic으로 정확화 (v5.0).

### Governance Risk
- gate enforcement는 4종 schema + active script manifest + reviewer 제약으로 한 단계 더 강화.

---

## 10. Required Revisions

**없음.** v5.0은 Phase 1 진입 전 차단성 수정 사항이 없다.

본 review의 Non-Critical 4.1~4.3은 모두 매우 미세한 polish 수준이며 다음 시점에 흡수 가능:

| Non-Critical | 흡수 시점 | 처리 비용 |
| --- | --- | --- |
| 4.1 Change 10 Validation 필터 `historical` 추가 | 다음 plan 갱신 시 한 셀 수정 | 30초 |
| 4.2 authority carve-out minimum evidence 보강 | 다음 plan 갱신 시 한 줄 추가 | 1분 |
| 4.3 Pulse wrapper 셀 설명 Implementation Notes로 이동 | 다음 plan 갱신 시 절 이동 | 2분 |

전체 약 4분 작업.

---

## 11. Final Recommendation

**PASS.**

v1.0(WARN) → v2.0(PASS w/ minor) → v3.0(PASS) → v4.0(PASS) → v5.0(PASS, governance 완성도 ↑). 5 iteration 만에 execution-ready 상태에서 governance discipline까지 다듬어진 완성형 plan.

v4.0 → v5.0의 핵심 progress:

1. **v4 review의 Non-Critical 3/3 전수 반영** (`$LASTEXITCODE`, status line, Pulse wrapper 역할 분담)
2. **표 셀 escape convention 명시** — 자동 복사-실행 워크플로 가능
3. **실행 cwd = repository root 고정** — 상대 경로 모호성 해소
4. **Approved Diff Procedure reviewer 제약 신설** — sealed_artifact/runtime/public_facing/compat surface self 금지 + authority carve-out + build-only self 허용 (v1 review부터 누적되어온 self-approval weakness 마침내 closure)
5. **§12 Change 9b Quantitative Criterion에 `$LASTEXITCODE` pattern 명시** — closeout 판정 명령이 PowerShell 자동화 가능 형태로 굳어짐

### Blocking conditions
없음.

### Required next actions
1. **Phase 1 진입** — `phase1_inventory_readpoint.md`, `phase1_artifact_source_classification.md`, `phase1_batch1_import_graph.md`, `phase1_conflict_resolution_gate.md`, `phase1_pulse_wrapper_usage_inventory.md`, `phase1_baseline_metrics.md`, `docs/Iris/phase1_active_script_manifest.txt` 7종 + `approved_diff_log.md` = 8종 deliverable 산출 (cwd = repo root).
2. **§5 Path Existence Verification 전수 `True` 확인** + chunk enumerate를 `baseline_layer3_chunk_count` / `baseline_usecase_chunk_count`로 봉인.
3. **`baseline_test_count` 봉인** — §7 parser 적용 후 `$status == 'OK'`일 때만 봉인.
4. **`docs/Iris/phase1_active_script_manifest.txt` 산출** — active 분류 build script 경로를 한 줄당 한 경로로 작성. Change 6의 baseline ↔ closeout 정렬에 입력.
5. **conflict gate 6/6 + 13개 baseline metric 충족** → Phase 1 `complete` 판정.
6. **Phase 2~10 순차 진입** — 각 Change Validation 표 + §12 Quantitative Closeout Criteria 동시 충족.
7. **본 review의 Non-Critical 4.1~4.3** — 다음 plan 갱신 시 흡수.

### Optional follow-ups (non-blocking)
- 본 review 4.1: Change 10 Validation 필터 `historical` 추가.
- 본 review 4.2: authority carve-out minimum evidence 보강 (옵션 A 또는 B).
- 본 review 4.3: Pulse wrapper 셀 설명 Implementation Notes로 이동.

### Out of scope for this review
- 코드 회귀 검증 (각 phase 실행 시점에 수행)
- `docs/EXECUTION_CONTRACT.md` 본문 대조 (별도 검증)
- Pulse / Echo / Fuse / Nerve 영향 분석 (Non-Goals)
- 입력 roadmap 본문 재대조 (roadmap review에서 처리)
- v1·v2·v3·v4 review의 closeout 검증 (본 review가 v4 → v5 변경분에 한정)

---

## 12. Reviewer Notes

### v4.0 → v5.0 변경 반영 매트릭스

| v4 review 항목 | v5.0 반영 상태 | 비고 |
| --- | --- | --- |
| Non-Critical 4.1 (PowerShell `$LASTEXITCODE`) | ✅ 완전 반영 | 머리말 PowerShell 표기 규약 확장 + 예시 block + Change 9b Manual QA matrix full pattern |
| Non-Critical 4.2 (status line v3.0 → v4.0) | ✅ 완전 반영 + 강화 | status line v5.0으로 동기화 |
| Non-Critical 4.3 (Pulse wrapper 2-command 역할 분담) | ✅ 완전 반영 | Change 9b Validation 셀에 명시적 설명 추가 (safety net redundancy 의도) |
| v1 review weak validation (approved diff self-approval) — 누적 carryover | ✅ closure | §7 Approved Diff Procedure reviewer 제약 신설 |
| v5.0 self-introduced 1 (표 셀 escape convention) | ✅ self-introduced | 머리말 PowerShell 표기 규약 |
| v5.0 self-introduced 2 (cwd = repository root) | ✅ self-introduced | 머리말 PowerShell 표기 규약 |
| v5.0 self-introduced 3 (approved diff reviewer 제약) | ✅ self-introduced | sealed/runtime/public_facing/compat self 금지 + authority carve-out + build-only self 허용 |

### Spot-checked facts (verified 2026-06-07)
- 상단 status line "Draft v5.0" 확인 (v4 review 4.2 closure)
- 머리말 PowerShell 표기 규약 line 21-28: `$LASTEXITCODE` 사용 규칙 + 예시 block + cwd repository root 명시
- 머리말 line 19-20: Markdown 표 셀 escape convention 명시
- §5 Code line 249: `docs/Iris/phase1_active_script_manifest.txt` 경로 명시
- §6 Change 1 baseline_v24_hardcode_count line 293: `Get-Content docs\Iris\phase1_active_script_manifest.txt` repo root 기준
- §6 Change 9b Validation line 777 (Pulse wrapper untouched): 두 명령 + 역할 분담 명시 (v4 review 4.3 closure)
- §6 Change 9b Validation line 778 (Manual QA matrix): `$ancestorExit = $LASTEXITCODE; $sameSha = ((git rev-parse $baselineCommit) -eq (git rev-parse $firstCodeCommit))` 명시
- §7 Approved Diff Procedure reviewer 제약 (line 884, 893-897) 신설 확인
- §10 Rollback Plan line 1031: `$LASTEXITCODE -ne 0` + `$baselineSha -eq $firstCodeSha` 패턴
- §12 Change 9b Quantitative Criterion line 1095: `$LASTEXITCODE -eq 0` 패턴
- §12 Per-Change Change 9b line 1110: `$LASTEXITCODE -eq 0` 패턴

### Uncertainty disclosure
- `surface = authority` self carve-out의 "no authority ownership change" 판정 적정성은 case-by-case 결정. 본 review에서 단일 판정 기준 제시 불가 (본 review 4.2).
- PowerShell 5.x vs 7.x `$LASTEXITCODE` 동작 차이 가능성 — v4 review에서 미확인으로 남김. v5.0이 환경 가정 (Windows 11 + PowerShell 5.x/7.x)을 명시하나 native exe 호출 시점의 정확한 동작은 phase 진입 후 sanity check.
- `luac -p`의 Kahlua 환경 호환성은 v1~v5 review 전수 미확인 (잔여 uncertainty 유지).

### Review limitations
- 본 review는 v4 → v5.0 변경분 검토 중심. v4.0에서 PASS한 영역 재검증 안 함.
- §7 Approved Diff Procedure reviewer 제약의 surface 분류 정확성은 phase 진입 후 실제 approved diff entry가 생성될 때 case-by-case 검증 필요.
- Markdown 표 셀 escape convention의 자동 복사-실행 워크플로는 실행 환경 의존 — 본 review에서 simulation 안 함.

### Future follow-up suggestions
- **Phase 1 deliverable 산출 직후 short follow-up review** — 8종 deliverable + 13개 baseline metric 측정값 + reviewer 제약을 따르는 approved_diff_log.md 초기 구조 sanity check.
- **Change 9b entry gate deliverable 별도 review** — `phase9b_manual_qa_checklist.md`의 scenario coverage + `$LASTEXITCODE` 패턴 실제 동작 확인.
- **본 plan이 도입한 5종 schema** (Conflict Resolution Gate / Per-Directory Disposition / Manual QA Checklist / Approved Diff Log with reviewer 제약 / Active Script Manifest) + PowerShell 표기 규약 (확장판) + `git merge-base --is-ancestor` 기반 forensic을 Iris 외 다른 Pulse 모듈 refactor에서 재사용 가능한 governance pattern 라이브러리로 추출 권장.
- **Approved Diff Procedure reviewer 제약 운영 실효성** — Phase 진행 중 실제 approved diff entry가 발생하면 surface 분류와 reviewer 판정의 일관성을 cross-document 모니터링 권장.
- **`additive amendment preference` 등 운영 원칙 governing docs 인용 이관** — v3.0이 약속한 절차, 다음 governing docs 갱신 시 이관 권장.
