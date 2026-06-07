# Iris_Refactoring_Plan_Review_v3.md

> Review target: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v3.0, 2026-06-07)
> Review template: `docs/REVIEW_TEMPLATE.md`
> Upstream documents:
> - `docs/Iris/Iris_Refactoring_Plan_Review_v2.md` (v2 review, PASS with minor revisions, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Plan_Review.md` (v1 review, WARN, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap.md` (Draft, 2026-06-07)
> - `docs/PLAN_TEMPLATE.md`
> Reviewer date: 2026-06-07
> Verification scope: v3.0 변경분 내적 일관성 + v2 review의 R1·R2 및 Non-Critical 4.1~4.11 반영 여부 + §5 Generated Artifacts 실제 경로 spot check + PowerShell 명령 syntax 재검증

---

## 1. Verdict

**PASS** — Phase 1 진입 가능. 본 review가 제시하는 항목은 모두 Non-Critical polish 수준이며, 어떤 항목도 진입을 차단하지 않는다.

---

## 2. Executive Summary

v3.0은 v2 review가 제기한 **R1(PowerShell regex 이스케이프)·R2(Phase 4 JSON schema diff)를 모두 반영**했고, Non-Critical 4.1~4.11 중 actionable한 11개 항목 거의 전수에 대응 메커니즘을 추가했다. 추가로 본 review가 놓쳤던 **3가지 중요한 오류**를 maintainer가 self-catch하여 자발적으로 수정했다.

**Self-caught beyond v2 review scope**:
- **§5 Generated Artifacts 경로 일제 정정** — v2까지 `Iris/media/lua/client/Iris/IrisLayer3Data.lua`로 잘못 표기되어 있던 sealed artifact 경로가 실제 위치(`Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` + 11 chunks + UseCaseDescriptions + 9 chunks + RequirementsLookup + Classifications/Capabilities/ContextOutcomes/Data/UseCaseLabelMap/Recipe·Moveables·Fixing Index·Data·layer3_renderer 등 총 16+개)로 일제 정정. v1·v2 review가 모두 놓친 path 오류.
- **PowerShell `Select-String -Recurse` 비존재 catch** — PowerShell 5.1의 `Select-String`은 `-Recurse` 파라미터가 없다. v2까지 baseline metrics 명령들이 이를 가정한 표기 — v3.0이 `Get-ChildItem -Recurse -File | Select-String -Pattern ...` 패턴으로 전수 교체. v1·v2 review 미감지.
- **`IrisMain.lua` 변경을 Phase 9a → 9b로 재배치** — INIT_MODULES 변경이 bootstrap/dispatch surface에 영향을 줄 수 있다는 보수적 판단. v2 review가 "INIT_MODULES spec 변경"을 Manual QA trigger 후보로 언급했으나 phase 재배치까지 권장하지는 않았음 — maintainer가 더 엄격하게 해석.

**Primary strengths**:
- **PowerShell 표기 규약**을 front matter에 신설 — regex `|` vs 셀 escape `\|` 모호성 영구 해소
- **§5 Generated Artifacts**를 sealed artifact 진리 목록으로 봉인 + Phase 1 inventory에서 재검증 약속
- **Path Existence Verification 확장** — 11 → 20개 path + chunk enumerate (11 + 9 기대값) 검증
- **Manual QA Checklist Schema에 `baseline_capture_commit` 필드 추가** — baseline 사후 촬영 forensic 차단
- **Approved Diff Log에 `surface` 필드 추가** — runtime/sealed/compat surface 자동 매핑으로 manual QA cross-reference 강화
- **Per-Directory Disposition Schema에 `N/A` 규칙 명시** — `delete_candidate` deferral 사유 기록 강제
- **Test Baseline Update Rule에 parser regex 예시 명시** — `^Ran (\d+) tests in ` + `^(OK|FAILED)` 추출 명확화
- **Manual QA Trigger Criteria에 6번째 trigger** (`bootstrap/dispatch module 변경`) 추가
- **Rollback Plan에 baseline 사후 촬영 무효 규칙** 추가
- **Quantitative Closeout Criteria** 모든 Change에 적용 + Change 1에 chunk enumerate 일치 조건 추가
- **"Command (PowerShell, manual step은 'Manual:' 접두)"** column header convention 도입
- **§11 Plan Operating Principles**가 §6 Change 10 본문과 cross-reference (Phase 10 마지막 배치 정당화)

**Primary risks**:
- 없음 (Critical 수준). 본 review는 5건의 Non-Critical polish 항목만 식별.

**Execution should proceed?**: **Yes, immediately.** Phase 1 진입 전 필수 수정 없음. 본 review의 Non-Critical은 Phase 진행 중 incremental adjustment로 흡수 가능 또는 reviewer 권장 사항.

---

## 3. Critical Issues

**없음.** v3.0은 v2 review의 Critical 2건(R1·R2)을 완전히 해소했고, v3.0이 도입한 새 규약(PowerShell 표기 규약, §5 Generated Artifacts 봉인, baseline_capture_commit forensic 등) 중 어느 것도 Critical 결함을 노출하지 않았다.

---

## 4. Non-Critical Issues

### 4.1 `baseline_v24_hardcode_count` 필터와 Phase 6 closeout 필터 불일치

§6 Change 1 baseline metrics:
```
baseline_v24_hardcode_count:
Get-ChildItem Iris\build -Filter *.py -Recurse -File
  | Where-Object { $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch '_archive' }
  | Select-String -Pattern 'v2\.4' | Measure-Object
```

§6 Change 6 Validation `v2.4 hardcode count`:
```
Get-ChildItem Iris\build -Filter *.py -Recurse -File
  | Where-Object { $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch '_archive' -and $_.FullName -notmatch 'historical' }
  | Select-String -Pattern 'v2\.4' | Measure-Object
```

baseline은 `historical` 제외 안 함, Phase 6 closeout은 제외함. 결과:
- `baseline_v24_hardcode_count`: active + historical에서 v2.4 등장 횟수
- Phase 6 closeout `Count == 0`: active에서만 v2.4 등장 0회 (historical 잔존 허용)

기능적으로는 의도된 차이로 보임 (active pipeline의 v2.4를 0으로 만들고 historical은 보존). 단 다음 모호함:

- baseline의 "사용 phase: Phase 6 closeout"이 직접 비교가 아니라 시작 상태 기록임을 본문에 명시하지 않음.
- 두 명령의 필터 차이를 §6 또는 §12 Quantitative Closeout Criteria에 한 줄로 정당화 권장.

권장 수정: `baseline_v24_hardcode_count`의 "사용 phase" 컬럼 옆에 "(시작 상태 기록, Phase 6 closeout은 별도 필터의 Count == 0 사용)" 한 줄 추가, 또는 baseline 필터를 Phase 6 closeout과 동일하게 통일.

### 4.2 `git diff --no-index` exit code 자동화 명시 부족

§6 Change 4 Validation `Report JSON schema`/`Report Markdown schema` 행:
```
git diff --no-index --stat before.json after.json
git diff --no-index before.md after.md
```

자동화 시 PASS/FAIL 판정에 사용하려면 `--exit-code` 플래그가 필요 (`git diff` 기본은 stdout만 출력, exit code는 항상 0). 현재 표현은 출력을 사람이 보고 판정하는 형태에 가까움.

권장 수정: 자동 PASS/FAIL이 필요한 경우 `git diff --no-index --exit-code <before> <after>`로 표기 (exit 0 = identical, exit 1 = diff). Python one-liner backup도 `sys.exit(0)` / `sys.exit(1)` 사용 중이므로 일관됨.

### 4.3 Change 4 Validation 표 셀에 편집상 코멘트 잔존

§6 Change 4 Validation `Report JSON schema` 행 셀 안에 "v3.0: `Compare-Object` on `PSCustomObject`는 nested 비교 불완전하여 제거" 텍스트가 포함되어 있다. 변경 이력 코멘트가 validation 명령 셀에 섞여 있어 표 읽기를 방해.

권장 수정: 해당 코멘트를 Change 4 Implementation Notes 절 또는 Change 4 표 직후 보조 텍스트(이미 한 줄 있음 — `git diff --no-index`는 두 임의 경로를 비교할 수 있어 ...)로 이동, 셀에는 명령만 남김.

### 4.4 §7 Manual Validation "모든 phase 공통" 표현의 적용 범위

§7 Manual Validation:
```
- 모든 phase 공통: `[Iris] Bootstrap complete` console 출력 확인 (runtime require smoke).
```

Phase 1~8과 Phase 10은 runtime Lua를 변경하지 않으므로 boot smoke가 매번 필요하지 않다. 실제 의도는 "runtime Lua 변경이 있는 Phase 9a·9b에서 공통" 또는 "phase closeout 직전에 한 번"으로 보임.

권장 수정: "모든 phase 공통"을 "Phase 9a·9b 모든 commit closeout, 그 외 phase는 inventory 변경 후 1회"로 명시.

### 4.5 Chunk enumerate 기대값 (Layer3 11 / UseCase 9) hard-coded

§5 Path Existence Verification chunk enumerate block + §6 Change 1 Validation `Chunk count` 행이 11 / 9를 기대값으로 명시. 향후 generator 출력 변경 시 두 곳을 동기 amendment해야 함.

본 plan이 명시한 amendment surface는 `phase1_baseline_metrics.md`. chunk count도 baseline metric으로 추가하면 단일 진리 출처가 통일됨.

권장 수정: `baseline_layer3_chunk_count`, `baseline_usecase_chunk_count`를 Quantitative Baseline 표에 추가. 현재 11 / 9 hard-coded는 Phase 1 측정값으로 봉인 + 향후 변경 시 amendment entry 동일 규칙 적용.

---

## 5. Scope Review

### Scope Drift
**없음.** Scope(§2), Out Of Scope, Non-Goals(§3)가 roadmap의 Constraints/Non-Goals와 일관 유지. v3.0이 §2 Code 경로에 `Iris/media/lua/client/Iris/IrisMain.lua`를 명시 추가하여 Phase 9b의 IrisMain 변경 surface를 scope 내로 명확히 포함. §2 Out Of Scope의 Pulse compat wrapper 경로(`Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua`)도 정확.

### Missing Scope
v2 review에서 지적한 missing scope 3건:
- Pulse compat wrapper 6개 파일 grep/require 사용처 inventory → `phase1_pulse_wrapper_usage_inventory.md` deliverable로 흡수 ✓
- `Iris/output/` 44개 entry 분류 owner → §5 Generated Artifacts 봉인 + Phase 1 deliverable로 흡수 ✓
- `Iris/build/package/Iris/...` 미러 산출물 분류 → §5 Generated Artifacts + Phase 8 책임 ✓

본 review에서 발견한 추가 missing scope:
- `Iris/build/description/v2/output/`(staging-adjacent output) 분류 — `Iris/build/description/v2/output/`은 Phase 2 Validation에서 SHA 비교 대상이나 §5 Generated Artifacts에는 enumerate되지 않음. Phase 1 inventory에 포함 권장 (현재 §5 acquisition/normalization/style 산출물도 미enumerate).

### Explicitly Out Of Scope Consistency
**일관성 양호.** v2.0과 동일하게 모순 없음. v3.0에서 §3 Non-Goals에 "`implemented_only`를 merge/release closeout 또는 behavior-preserving claim으로 사용한다"를 8번째 항목으로 추가해 closeout claim discipline 강화.

---

## 6. Validation Review

### Missing Validation
- 본 review 4.1: baseline vs closeout 필터 정당화 누락
- 본 review 4.2: `git diff --no-index --exit-code` 자동화 명시 누락
- 본 review 4.5: chunk count metric의 baseline 봉인 메커니즘 누락

### Weak Validation
v2 review에서 지적한 weak validation 4건:
- `baseline_test_count` parser 부족 → §7 PowerShell extraction 예시 + regex `^Ran (\d+) tests in ` 명시 ✓
- `Compare-Object` JSON 깊이 한계 → `git diff --no-index` + Python one-liner 교체 ✓
- PowerShell regex `|` vs 셀 escape `\|` 모호 → 머리말 표기 규약으로 영구 해소 ✓
- `Get-ChildItem` `__pycache__` 처리 → 모든 명령에 `Where-Object FullName -notmatch '__pycache__'` 추가 ✓

본 review에서 발견한 추가 weak validation:
- 본 review 4.2의 `git diff --no-index` 자동화
- 본 review 4.1의 baseline 필터 정렬

### Validation Ceiling Risk
**낮음 — 적극적으로 차단됨.** §7 Validation Limits 13개 + Approved Diff Procedure schema의 `surface` 필드 cross-reference + Manual QA Checklist Schema의 baseline_capture_commit 강제로 ceiling 회피 경로가 v2 대비 한 단계 더 좁아짐. §12 Closeout State Semantics가 각 상태의 허용/불허 claim 표를 봉인.

### Validation Practicality
- **realistically executable**: 양호. v3.0이 PowerShell 5.x 호환을 전수 보증. Critical 없음.
- **proportionate to risk surface**: 양호. IrisMain 9a→9b 재배치로 위험도 정합성 추가 개선.
- **appropriately scoped**: Phase 10 position carryover (v2 review Non-Critical 4.3)가 §11 운영 원칙(`minimal diff preservation`) + §6 Change 10 본문 cross-reference로 정당화. 본 review는 정당화 수락.
- **free from unnecessary ceremony**: 양호. Schema 표 도입은 ceremony가 아니라 discipline.

---

## 7. Governance Review

### Philosophy.md Compliance
**준수.** §11 Governing Document Source 12개 항목 인용 출처와 함께 유지. v3.0이 §4 Assumptions에 `no silent compatibility shim`을 추가하여 §11 운영 원칙 3종과 동기.

### Architecture Boundary
**준수.** Hub & Spoke 보존, runtime/build-time authority 분리, Recipe/Right-click 2-track 유지.

### Runtime / Build-Time Separation
**준수.** §8 Risk Surface Touch에서 phase별 surface 영향 분리. v3.0이 IrisMain을 9b로 이동하여 build/runtime boundary 약화 위험을 manual QA로 흡수. Architecture Risk §9에 "IrisMain helper 흡수 (Phase 9b)가 INIT_MODULES spec 복잡도를 증가시켜 build/runtime boundary가 약화됨 (mitigation: 동치성 유지 최소 변경 + manual QA Bootstrap surface)" 명시.

### FAIL-LOUD Preservation
**준수.** §11 운영 원칙 `No silent compatibility shim` + Change 2 dual-import wrapper 마감 일자 코멘트 강제 + §7 Approved Diff Procedure schema가 silent SHA drift 차단.

### Authority Ownership
**준수.** §8 Authority Surface "Concerns controlled". v3.0이 Evidence skeleton refactor와 classification 작업이 authority-adjacent임을 명시 유지.

### Contract Compliance
- `iris_refactoring_final_roadmap_closeout.md` 봉인 영역 침범 없음 — chunk-only 구조와 generated Lua 수동 편집 금지 §4 Assumptions에 명시.
- `phase3_quality_gates_q5_split.md`: Change 4 entry gate가 conflict 14.4 "추가 split 필요" 판정 요구. 봉인 충돌 회피.
- `Iris_Refactoring_Roadmap.md` §14의 6개 conflict: §6 Change 1 Conflict Resolution Gate Schema 충족.
- `PLAN_TEMPLATE.md`: 12개 섹션 준수 + 각 Change Purpose/Files/Implementation Notes/Validation/Expected Closeout 구조 준수.
- v3.0이 §1 Objective에 "본 계획의 closeout claim 보증 한계는 §12와 §7 Validation Limits에서 명시적으로 닫는다" 명시 추가.

---

## 8. Risk Surface Touch

### Authority Surface
**Concerns controlled.** v3.0 변경 없음. 적절.

### Runtime Behavior Surface
**Concerns** — Phase 9a low / Phase 9b high. v3.0이 IrisMain을 9b로 이동하면서 9b의 surface가 (UI 분할 + IrisMain dispatch + Pulse wrapper disposition) 3축으로 확장됨. 단, 모두 manual QA로 묶이므로 governance 일관성 유지. Architecture Risk와 Runtime Risk에 mitigation 명시.

### Compatibility Surface
**Concerns** — v2와 동일. Pulse compat wrapper 6개 enumerate + Change 9b에서 제거 명시 차단.

### Sealed Artifact Surface (v3.0 경로 정정)
**Concerns**. v3.0의 §5 Generated Artifacts 정정으로 보호 범위가 16+개 sealed artifact로 명확화. Phase 8 Validation 표가 Layer3 chunks(11) + UseCaseDescriptions chunks+RequirementsLookup(10) + 기타 generated index/data를 모두 별도 행으로 SHA 비교. v2 대비 보호 grain이 매우 정밀해짐.

### Public-Facing Output Surface
**Conditional concerns** — Phase 9b 시 concerns, 그 외 None.

---

## 9. Risk Review

### Architecture Risk
v3.0이 모든 항목에 mitigation 유지 + IrisMain Phase 9b 재배치에 따른 build/runtime boundary 약화를 새 risk로 인정하고 mitigation(동치성 유지 + manual QA Bootstrap surface) 명시.

### Runtime Risk
- IrisMain INIT_MODULES 변경 — manual QA Bootstrap surface로 검증.
- Pulse compat wrapper 외부 require — Change 9b 제거 금지로 mitigate.
- Generator/Renderer debug 축소 진단 능력 저하 — trace mode 분리 옵션 검토 + 정량 baseline.

### Compatibility Risk
- v3.0이 Change 6 mitigation에 `_archive`/`historical` 제외 grep 규칙 명시 추가.
- Test Baseline Update Rule parser 명시로 Change 10 default test 집합 변경 위험 감소.

### Regression Risk
- §5 Generated Artifacts 진리 목록 봉인으로 sealed evidence 오판 위험 감소.
- Disposition Schema `evidence_type` + `sealed_evidence` archive 외 disposition 금지 규칙.
- `Ran N tests` parser로 baseline_test_count 침범 차단.

### Operational Risk
- v3.0이 PowerShell `Select-String -Recurse` 비존재를 명시 인정 + 전수 정정.
- partial closeout 누적 추적은 §12 의미 분리로 보호.

### Validation Risk
- approved diff `surface` 필드 추가로 runtime-impact 자동 매핑.
- baseline screenshot 사후 촬영을 `baseline_capture_commit < 첫 코드 commit` 규칙으로 차단.
- `git diff --no-index` 자동화 시 `--exit-code` 명시 권장 (본 review Non-Critical 4.2).

### Governance Risk
- §4 Assumptions와 §11 Plan Operating Principles 동기화 완료.
- gate enforcement는 4종 schema(Conflict Resolution Gate / Per-Directory Disposition / Manual QA Checklist / Approved Diff Log)로 강화.

---

## 10. Required Revisions

**없음.** v3.0은 Phase 1 진입 전 차단성 수정 사항이 없다.

본 review의 Non-Critical 4.1~4.5는 모두 polish 수준이며 다음 시점에 흡수 가능:

| Non-Critical | 흡수 시점 | 처리 비용 |
| --- | --- | --- |
| 4.1 baseline_v24 필터 정렬 | Phase 1 baseline metric 측정 시 한 줄 주석 | 1분 |
| 4.2 `git diff --exit-code` | Change 4 진입 전 명령 수정 | 1분 |
| 4.3 Change 4 셀 편집 코멘트 이동 | 다음 plan 갱신 시 | 1분 |
| 4.4 "모든 phase 공통" 범위 | 다음 plan 갱신 시 | 1분 |
| 4.5 chunk count baseline 등재 | Phase 1 baseline 측정 시 metric 2종 추가 | 5분 |

전체 5분 작업.

---

## 11. Final Recommendation

**PASS.**

v3.0은 v1.0(WARN) → v2.0(PASS with minor revisions) → v3.0(PASS)로 3 iteration 만에 execution-ready 상태에 도달했다. v2.0 대비 다음 5가지 progress:

1. **v2 review의 R1·R2 전수 반영** (PowerShell regex / Phase 4 JSON schema)
2. **v2 review의 Non-Critical 4.1~4.11 거의 전수 반영** (parser, `__pycache__`, Phase 10 정당화, Path Verification 확장, column header convention, surface field, baseline_capture_commit, N/A 규칙, §4/§11 동기화)
3. **v2 review가 놓친 3건 self-catch** (sealed artifact 경로, PowerShell `Select-String -Recurse` 비존재, IrisMain bootstrap 보수적 분류)
4. **새 거버넌스 장치** (PowerShell 표기 규약, §5 Generated Artifacts 진리 봉인, chunk enumerate validation, Manual QA Trigger Criteria 6번째 trigger)
5. **§12 Quantitative Closeout Criteria 강화** (Change 1에 chunk count 일치, Change 9a에 IrisMain 변경 없음 확인, Change 9b에 baseline_capture_commit < 첫 코드 commit, Change 10에 `__pycache__`/`_archive`/`historical` 제외 규칙 일관)

### Blocking conditions
없음.

### Required next actions
1. **Phase 1 진입** — `phase1_inventory_readpoint.md`, `phase1_artifact_source_classification.md`, `phase1_batch1_import_graph.md`, `phase1_conflict_resolution_gate.md`, `phase1_pulse_wrapper_usage_inventory.md`, `phase1_baseline_metrics.md` 6종 + `approved_diff_log.md` 1종 = 7종 deliverable 산출.
2. **§5 Path Existence Verification 전수 `True` 확인** + chunk enumerate (Layer3 11 / UseCase 9) 일치 확인.
3. **`baseline_test_count` 봉인** — §7 parser 적용 후 `$status == 'OK'`일 때만 봉인. 본 review 4.5 반영 시 `baseline_layer3_chunk_count`, `baseline_usecase_chunk_count`도 함께 봉인.
4. **conflict gate 6/6 충족** — Phase 1 `complete` 판정.
5. **Phase 2~10 순차 진입** — 각 Change Validation 표 + §12 Quantitative Closeout Criteria 동시 충족.
6. **본 review의 Non-Critical 4.1~4.5** — Phase 진행 중 incremental 흡수.

### Optional follow-ups (non-blocking)
- 본 review 4.1: `baseline_v24_hardcode_count`에 "(시작 상태 기록)" 주석 추가 또는 필터 통일.
- 본 review 4.2: `git diff --no-index --exit-code` 명시.
- 본 review 4.5: `baseline_layer3_chunk_count`, `baseline_usecase_chunk_count` baseline metric 등재.

### Out of scope for this review
- 코드 회귀 검증 (각 phase 실행 시점에 수행)
- `docs/EXECUTION_CONTRACT.md` 본문 대조 (별도 검증)
- Pulse / Echo / Fuse / Nerve 영향 분석 (Non-Goals)
- 입력 roadmap 본문 재대조 (roadmap review에서 처리)
- v1·v2 review의 closeout 검증 (본 review가 v2 → v3 변경분에 한정)

---

## 12. Reviewer Notes

### v2 → v3.0 변경 반영 매트릭스

| v2 review 항목 | v3.0 반영 상태 | 비고 |
| --- | --- | --- |
| R1 (PowerShell regex 이스케이프) | ✅ 완전 반영 + 강화 | 머리말 "PowerShell 표기 규약" 신설, Change 6 명령 정정 |
| R2 (Phase 4 JSON schema diff) | ✅ 완전 반영 | `git diff --no-index` + Python one-liner backup + Compare-Object 제거 명시 |
| Non-Critical 4.1 (baseline_test_count parser) | ✅ 완전 반영 | §7 PowerShell extraction 예시 + regex 명시 |
| Non-Critical 4.2 (`__pycache__` 처리) | ✅ 완전 반영 | 모든 baseline metric에 `Where-Object FullName -notmatch '__pycache__'` |
| Non-Critical 4.3 (Phase 10 position) | ✅ 완전 반영 | §6 Change 10 + §11 minimal diff preservation cross-reference |
| Non-Critical 4.4 (Path Existence Verification 확장) | ✅ 완전 반영 + 강화 | 11 → 20개 + chunk enumerate 추가 |
| Non-Critical 4.5 (Column header consistency) | ✅ 완전 반영 | "Command (PowerShell, manual step은 'Manual:' 접두)" |
| Non-Critical 4.6 (cross-document pollution 점검) | ⏸️ 후속 follow-up | actionable 아님 — v2 review에서도 future suggestion으로 분류 |
| Non-Critical 4.7 (approved_diff_log surface 분류) | ✅ 완전 반영 | `surface` 필드 추가 + 자동 매핑 규칙 |
| Non-Critical 4.8 (baseline_screenshot 시점) | ✅ 완전 반영 + 강화 | `baseline_capture_commit < 첫 코드 commit` 강제 규칙 |
| Non-Critical 4.9 (delete_candidate N/A 처리) | ✅ 완전 반영 | N/A 규칙 + deferral 사유 명시 강제 |
| Non-Critical 4.10 (baseline_test_count 봉인 시점) | ✅ 완전 반영 | §7 Test Baseline Update Rule에 명시 |
| Non-Critical 4.11 (§4/§11 동기화) | ✅ 완전 반영 | §4 Assumptions에 `no silent compatibility shim` 추가 |
| 본 review가 놓친 path 오류 (v3.0 self-catch) | ✅ self-catch | §5 Generated Artifacts 16+개 enumerate |
| 본 review가 놓친 `Select-String -Recurse` (v3.0 self-catch) | ✅ self-catch | `Get-ChildItem -Recurse -File | Select-String` 패턴 일괄 적용 |
| IrisMain 9a → 9b 재배치 (v3.0 self-catch) | ✅ self-catch | bootstrap/dispatch trigger 추가 + Bootstrap surface 신설 |

### Spot-checked facts (verified 2026-06-07)
§5 Generated Artifacts 16개 sealed artifact 경로 본 검토에서 실파일 일치 확인:
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001~011.lua` (11개) ✓
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua` ✓
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/Chunk001~009.lua` (9개) + `RequirementsLookup.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisCapabilities.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisContextOutcomes.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisData.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua` + `IrisRecipeIndexData.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisMoveablesIndex.lua` + `IrisMoveablesIndexData.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisFixingIndex.lua` + `IrisFixingIndexData.lua` ✓
- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua` ✓
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` ✓

Runtime + Pulse compat 11개 경로 v1·v2 review에서 검증 완료.

### Uncertainty disclosure
- PowerShell 7+ (Core) 환경에서는 `Select-String -Recurse`가 새로 추가되었을 수 있음. v3.0이 명시하는 환경 가정은 Windows 11 + PowerShell 5.1 기본이므로 본 review는 5.1 기준으로 평가. 7+ 사용 시 명령 단순화 가능하나 5.1 호환 위해 현재 표기 유지가 합리적.
- `git diff --no-index --exit-code`의 PowerShell 자동화 시점의 정확한 exit code 처리는 phase 실행 시점에 별도 sanity check 필요.
- `luac -p`의 Kahlua 환경 호환성은 v1·v2 review와 동일하게 미확인. v3.0이 §6 Change 9a/9b에서 `luac -p` 사용을 유지하므로 동일 잔여 우려. 본 review에서 새 risk로 격상하지 않음.

### Review limitations
- 본 review는 v2 → v3.0 변경분 검토 중심이며, v2에서 PASS한 governance/structure 영역은 재검증하지 않음.
- §5 Generated Artifacts 외 다른 경로(`Iris/output/**`, `Iris/build/package/**`)의 실제 entry 수는 Phase 1 inventory에서 산출 예정이므로 본 review에서 spot check하지 않음.
- §6 Change 7a consolidation 후보 5개 family의 실제 sibling script 개수와 hidden branch logic 존재 여부는 Phase 1 inventory + Phase 7a 진행 시점에 검증 — 본 review 범위 외.
- Manual QA Checklist의 scenario 적정성(어떤 item id를 어떤 진입 경로로 검증해야 충분한가)은 별도 review 권장.

### Future follow-up suggestions
- **Phase 1 deliverable 산출 직후 short follow-up review** — `phase1_conflict_resolution_gate.md`의 6개 conflict 결정 적정성 검토 + `phase1_baseline_metrics.md`의 11개(또는 본 review 4.5 적용 시 13개) metric 측정값의 sanity check.
- **Phase 9b entry gate deliverable `phase9b_manual_qa_checklist.md` 별도 review** — scenario coverage(Browser/Wiki/Tooltip/Bootstrap 각 surface별 적정 시나리오) 적정성. v3.0이 Manual QA Checklist Schema의 scenario 컬럼을 정의했으나 실제 scenario 적정성은 phase 진입 직전 별도 review가 필요.
- **본 plan이 도입한 4종 schema** (Conflict Resolution Gate / Per-Directory Disposition / Manual QA Checklist / Approved Diff Log)와 PowerShell 표기 규약을 Iris 외 다른 Pulse 모듈 refactor 작업에서 재사용 가능한 governance pattern으로 추출하는 후속 작업 권장.
- **`additive amendment preference` 등 운영 원칙이 governing docs에 명시 인용되는 시점**에 §11에서 Plan Operating Principles → Governing Document Source로 이관 (v3.0이 약속한 절차).
