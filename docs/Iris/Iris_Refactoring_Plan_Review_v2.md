# Iris_Refactoring_Plan_Review_v2.md

> Review target: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v2.0, 2026-06-07)
> Review template: `docs/REVIEW_TEMPLATE.md`
> Upstream documents:
> - `docs/Iris/Iris_Refactoring_Plan_Review.md` (v1.0 review, WARN, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap.md` (Draft, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap_Review.md` (WARN, 2026-06-07)
> - `docs/PLAN_TEMPLATE.md`
> Reviewer date: 2026-06-07
> Verification scope: plan v2.0 본문 내적 일관성 + v1.0 review의 R1~R5 및 Non-Critical 반영 여부 + PowerShell 명령 spot check + 실제 파일 경로 재검증

---

## 1. Verdict

**PASS with minor revisions** — execution-ready. PowerShell 명령 syntax 버그 2건만 수정하면 Phase 1 진입 가능.

---

## 2. Executive Summary

v2.0은 v1.0 review가 제기한 **R1(파일 경로)·R2(Change 9 분리)·R3(Change 7 분리)·R4(정량 closeout 기준)·R5(Section 11 거버넌스 출처)를 모두 반영**했고, Non-Critical 4.1~4.11 중 거의 모두에 대응 메커니즘을 추가했다. 그뿐만 아니라 review scope를 넘어선 **새 거버넌스 장치 3종**을 도입했다.

- **Closeout State Semantics** (§12): `complete`/`partial`/`implemented_only`/`blocked` 4상태의 허용/불허 claim을 표로 명시. `implemented_only`가 merge/release claim에 사용 불가함을 governance violation으로 못 박음.
- **Approved Diff Procedure** (§7): SHA drift 허용 절차에 9개 mandatory field (entry_id, before_sha, after_sha, schema_or_behavior_impact 등) 부여. `runtime-impact` 명시 시 Change 9b manual QA 자동 강제 — cross-reference로 회피 경로 차단.
- **Test Baseline Update Rule** (§7): `baseline_test_count` 갱신 가능 조건을 Change 5·10 한정 + amendment entry 동반 + Change당 1회만 허용으로 봉인.

추가로 **Per-Directory Disposition Schema** (Change 7b), **Conflict Resolution Gate Schema** (Change 1), **Manual QA Checklist Schema** (Change 9b), **Path Existence Verification** (§5 Phase 1 Step 0)이 모두 mandatory field 표로 추가되어 schema-driven governance 수준이 v1.0 대비 한 단계 올라갔다.

**Primary strengths**:
- v1.0 review R1~R5 전수 반영 + Non-Critical 대부분 반영
- 4종의 새 schema 표로 phase 진입/종료를 객관화
- Windows 11 + PowerShell 환경을 §4 Assumptions에 명시하고 모든 validation 명령을 PowerShell로 통일
- `implemented_only`의 의미 봉인으로 governance violation 회피
- Phase 1 baseline metrics 11종을 PowerShell 명령과 함께 enumerate
- Change 9b entry gate에 `phase9b_manual_qa_checklist.md`를 **사전 deliverable**로 못 박음 (post-hoc checklist 작성 회피)
- Section 11 인용을 Governing Document Source / Plan Operating Principles 2-tier로 분리, 인용 미확인 항목 라벨링

**Primary risks**:
- **PowerShell regex syntax 버그 2~3건** — `Where-Object Path -notmatch "_archive\|historical"`의 `\|`는 PowerShell 정규식에서 리터럴 `|`가 아니라 이스케이프된 `|` (실제로는 동작하지만 의도가 모호). `Compare-Object` JSON 객체 비교의 깊이 한계.
- **Change 9a Validation "Runtime require smoke"가 manual KO mode 진입을 PowerShell column에 명시** — column header "Command (PowerShell)" 와 실제 manual step 사이 미세 불일치. 내적 일관성은 있음.
- **`baseline_test_count` 측정 방법이 parser 명세 없이 "PASS 총수"로 표현** — `unittest -v` 출력 파싱 규칙 명시 부족.
- **Phase 10 position carryover** (v1.0 review Non-Critical 4.4) — 여전히 마지막에 위치. v2.0이 Phase 10을 "Change 1~9b 통합 matrix"로 의도를 명확히 한 점은 진전이지만 위치는 동일.

**Execution should proceed?**: **Yes.** Required Revisions R1·R2(PowerShell syntax)만 적용하면 Phase 1 진입 가능. 나머지는 phase 진행 중 incremental adjustment로 흡수 가능 수준.

---

## 3. Critical Issues

### Issue 3.1 — PowerShell regex 이스케이프 패턴 일관성

Severity: **High (Pre-execution fix recommended, not blocking)**

Impact: 다음 위치에서 PowerShell regex `|` (alternation) 표기에 `\|` 이스케이프가 사용되어 의도가 모호하다.

- §6 Change 1 baseline metrics `baseline_v24_hardcode_count` 행: `Where-Object Path -notmatch "_archive\|historical"` (본문에 표시되지 않으나 §6 Change 6 Validation 표에서 동일 패턴 등장)
- §6 Change 6 Validation 표 `v2.4 hardcode count` 행: `Select-String -Path Iris\build -Pattern "v2\.4" -Include *.py -Recurse \| Where-Object Path -notmatch "_archive\|historical" \| Measure-Object`

PowerShell 정규식에서 `\|`는 .NET regex 사양상 리터럴 파이프 문자로 해석되어 alternation이 동작하지 않는다 (PowerShell 자체의 escape는 backtick \` 사용). `Where-Object -notmatch "_archive\|historical"`은 의도(`_archive` 또는 `historical`을 포함하는 path 제외)와 달리 `_archive|historical` 리터럴 문자열을 찾는다.

추가로 위 명령에서 `\|`는 PowerShell 파이프 연산자 위치에도 등장 (`Select-String ... \| Where-Object ... \| Measure-Object`). 이 경우 `\|`는 마크다운 표 셀 안에서 파이프 문자를 escape한 것으로 보이며 실제 실행 시 `|`로 풀어야 한다. 검토자가 셀 escape인지 PowerShell escape인지 구분 어려움 — 본문 명시 권장.

Affected Scope:
- §6 Change 1 baseline metrics 표 전체 (모든 행에서 표 셀 escape `\|` 사용)
- §6 Change 6 Validation 표 v2.4 hardcode count 행 (regex `\|` + 셀 escape `\|` 혼재)
- 기타 다른 Change Validation 표의 파이프 사용 명령들

Related Surface:
- 없음 (실행 환경 명령 표기 문제)

Required Fix:
- 마크다운 표 안의 PowerShell 파이프(`|`)는 셀 escape를 위해 `\|`로 표기 — 이 부분은 마크다운 렌더링 후 `|`로 풀림 (의도된 표기)
- regex 안의 alternation은 마크다운 셀 안에서도 `|` (또는 셀 escape 필요 시 `\|`)로 사용하되, 실행 시점에는 `|`임을 본문 주석 또는 부록으로 명시
- 권장: §7 Validation Plan 또는 §6 머리말에 "표 안의 `\|`는 마크다운 셀 escape이며 실행 시 `|`로 해석"을 한 줄 명시

Blocking Reason: 명령 실행 시 의도된 필터가 적용되지 않을 수 있음. Phase 6 v2.4 hardcode count 측정 시 `_archive`/`historical` 예외가 적용되지 않아 closeout 기준 (`v24_hardcode_count == 0`)이 영원히 실패할 위험.

---

### Issue 3.2 — Phase 4 JSON Schema Diff 명령 깊이 한계

Severity: **Medium (Phase 4 진입 전 fix 필요)**

Impact: §6 Change 4 Validation 표 `Report JSON schema` 행:

```
Compare-Object (Get-Content before.json | ConvertFrom-Json) (Get-Content after.json | ConvertFrom-Json)
```

`Compare-Object`는 기본적으로 객체 reference 또는 `.ToString()` 결과를 비교한다. `ConvertFrom-Json`이 반환하는 PSCustomObject는 nested 구조의 깊은 비교를 수행하지 않으며, 두 객체의 첫 레벨 property 이름만 비교한다. 실제로는 schema drift가 깊은 nested 위치에 있어도 `Compare-Object`가 detect하지 못할 수 있다.

특히 Phase 4의 `build_report.json` schema는 nested gate-level 결과를 포함하므로 1-level 비교로는 부족.

Affected Scope: §6 Change 4 Validation 표 `Report JSON schema` 행

Related Surface:
- Sealed Artifact Surface (report schema drift 미감지 시 후속 phase validation 입력 오염)

Required Fix:
- 옵션 A: `Compare-Object` 대신 두 JSON을 normalized string으로 직렬화해 비교 — 예: `(Get-Content before.json | ConvertFrom-Json | ConvertTo-Json -Depth 100) -eq (Get-Content after.json | ConvertFrom-Json | ConvertTo-Json -Depth 100)`
- 옵션 B: Python script로 비교 — `python -c "import json,sys; a=json.load(open('before.json')); b=json.load(open('after.json')); sys.exit(0 if a==b else 1)"`
- 옵션 C: `git diff --no-index before.json after.json` (외부 도구 의존)

Blocking Reason: schema drift 미감지 시 Change 4 closeout이 false-positive로 PASS되어 Change 5 evidence pipeline rerun의 입력이 오염된다.

---

## 4. Non-Critical Issues

### 4.1 `baseline_test_count` parser 명세 부족

§6 Change 1 baseline metrics 표 마지막 행:
```
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py" -v 2>&1 의 PASS 총수
```

"PASS 총수"가 구체적으로 어떤 라인을 카운트하는지 명세 부족. unittest verbose 출력은 다음 두 형식이 혼재:
- 각 테스트당 `test_xxx (...) ... ok`
- 마지막에 `Ran 380 tests in X.XXXs` + `OK`

권장: 다음 둘 중 하나 명시.
- `Ran N tests` 행에서 `N` 추출 (`Select-String -Pattern "^Ran (\d+) tests" | %{ $_.Matches[0].Groups[1].Value }`)
- `OK` 라인의 존재만 확인 + 별도 metric "test_count"는 `Ran N tests` 파싱

### 4.2 `Get-ChildItem` 결과의 `__pycache__` 포함 위험

§6 Change 1 baseline metrics:
- `baseline_build_script_count`: `Get-ChildItem Iris\build\description\v2\tools\build -Filter *.py -Recurse`
- `baseline_tools_build_loc`: 동상

`Iris/build/description/v2/tools/build/` 하위에 `__pycache__/` 디렉토리가 있을 경우 `*.pyc`는 `-Filter *.py`로 제외되나 `__pycache__` 자체는 path traversal 시 포함될 수 있음 (실제 `.py` 파일은 없으나 의도 외 경로 진입). 또한 `baseline_build_script_count`가 active script만 카운트하는지 archive/disposable 포함인지 모호.

권장: `Where-Object FullName -notmatch "__pycache__|_archive"` 추가, 또는 baseline metric 정의에 "active + legacy_archive + duplicate_consolidation_candidate + reproduction_evidence 4종 모두 포함" 명시.

### 4.3 Phase 10 position carryover (v1.0 Non-Critical 4.4)

v1.0 review에서 지적한 "Phase 10이 마지막에 위치해 Phase 2~9 영향을 모두 흡수해야 함"이 v2.0에서도 유지. 다만 v2.0은 Change 10 Files에 "phase별 validation command 정리 — Change 1~9b 표를 통합"을 명시해 **Phase 10이 마지막인 이유를 의도적으로 표명**함. 이는 진전. 그러나 phase 진행 중 발생하는 import contract 변경 (Change 2/3)이 test discovery에 영향을 줄 가능성은 그대로 남음.

권장: 다음 둘 중 하나.
- 옵션 A: 그대로 둠 + Change 2/3 Validation 표에 `test discovery 영향 점검` 행 추가
- 옵션 B: Phase 10을 Phase 3.5 (mid-validation gate)로 이동

옵션 A가 minimal diff 원칙(§11)에 부합. 본 review는 옵션 A 권장.

### 4.4 §5 Path Existence Verification에 빠진 경로

§5 PowerShell block은 11개 경로(runtime 5 + Pulse compat 6)를 verify하지만, plan 본문이 참조하는 다음 경로는 verify 블록에 없음.

- `Iris/build/quality_gates.py` (Change 4 대상)
- `Iris/build/recipe_evidence_pipeline.py`, `Iris/build/rightclick_evidence_pipeline.py` (Change 5 대상)
- `Iris/build/ENTRYPOINTS.md`, `Iris/build/build_import_contract.md`, `Iris/build/description/v2/tools/build/INVENTORY.md` (Change 1 readpoint)
- `Iris/build/tools/common/{io,stage_runner,versions}.py` (Assumption 대상)

이들은 §4 Assumptions에서 존재한다고 가정하나 실제 verify 절차 없음. Phase 1 Step 0에 추가 권장.

### 4.5 "Command (PowerShell)" column header가 manual step에도 사용

§6의 Validation 표는 모든 Change에서 5-column 형식을 사용한다 (Item / Command (PowerShell) / Expected / Failure Criteria / Rollback Trigger). 그러나 일부 행은 manual step:
- §6 Change 1 `Conflict gate completeness`: "phase1_conflict_resolution_gate.md 수동 검토"
- §6 Change 1 `Baseline metrics`: "phase1_baseline_metrics.md 수동 검토"
- §6 Change 9a `Runtime require smoke`: "KO mode 진입 → `[Iris] Bootstrap complete` console 메시지 확인"
- §6 Change 9b `Manual QA matrix`: "phase9b_manual_qa_checklist.md"
- §6 Change 4 `Report Markdown schema`: "before/after diff 수동 비교"
- §6 Change 8 `.gitignore review`: "git diff -- .gitignore 수동 검토"
- §6 Change 10 `Validation matrix dry run`: "phase10_validation_matrix.md 수동 검토"

내적 일관성은 있음 (모든 Change에서 동일 패턴). 다만 가독성을 위해 column header를 "Command or Step"으로 변경하거나, manual step에 `[Manual]` 접두어 추가 권장.

### 4.6 `additive amendment preference` 등 운영 원칙의 cross-document 점검

§11 Plan Operating Principles에 "Additive amendment preference, Minimal diff preservation, No silent compatibility shim"이 운영 원칙으로 라벨링됐다. v1.0 review가 제기한 출처 확인 문제는 해결. 다만 본 plan 외 다른 `docs/Iris/*.md`에서 동일 표현이 인용 출처처럼 등장하는지 cross-document 점검 권장 (review의 future follow-up suggestion에서 언급).

### 4.7 Approved Diff Log의 위치

§7 Approved Diff Procedure는 `docs/Iris/approved_diff_log.md` (신규)에 누적 기록을 제안. 본 log의 owner와 sealed 여부, 외부 검토 가능 여부가 plan에 명시되지 않음. Phase 1 deliverable로 함께 명시 권장 (log 자체가 sealed 또는 evidence-adjacent surface인지 분류).

### 4.8 Change 9b entry gate deliverable의 schema 사전 작성 보장

§6 Change 9b의 `phase9b_manual_qa_checklist.md`는 "entry gate deliverable, Change 진입 전에 작성"으로 명시. 다만 checklist의 baseline_screenshot 촬영은 코드 변경 전에 수행되어야 한다. 즉 "Change 9b 진입 전 작성"이 단순 schema 정의가 아니라 **baseline 캡처까지 완료**를 의미해야 함. 본문 한 줄 명시 권장 ("baseline 캡처는 코드 변경 commit 이전에 수행").

### 4.9 Disposition Schema의 `delete_candidate`

§6 Change 7b Per-Directory Disposition Schema에 `delete_candidate` disposition이 있고 "본 Change에서 실제 삭제하지 않으며 후속 deprecation decision으로 위임"으로 명시. 그러나 `delete_candidate` 행의 target_destination, rollback_path 처리 방식이 모호. 본 Change scope 외이므로 두 field가 비어도 되는지, 또는 placeholder 값이 들어가야 하는지 명시 권장.

### 4.10 `baseline_test_count` Phase 1에서 봉인 vs Test Baseline Update Rule 충돌 없음

`baseline_test_count`는 Phase 1에서 봉인되며 Change 5·10에서만 갱신 가능. 다만 Phase 1의 inventory readpoint 작업 중 test가 추가/제거되면 봉인 시점이 모호. 권장: "Phase 1 종료 commit의 test count = baseline" 명시.

### 4.11 `additive amendment preference` 라벨링의 Section 4 vs Section 11 동기화

§4 Assumptions에 `additive amendment preference`, `minimal diff preservation`을 "본 plan 운영 원칙"으로 라벨링한다고 명시되어 있고, §11 Plan Operating Principles에 본문이 있음. 두 곳의 표현이 정합. 단 §11에는 "향후 governing docs에 명시되면 인용 출처를 이관한다"가 있으나 §4에는 없음. §4도 동일 약속 추가 또는 §11 참조 명시 권장 (minor consistency).

---

## 5. Scope Review

### Scope Drift
**없음.** Scope(§2)와 Out Of Scope, Non-Goals(§3)가 roadmap의 Constraints/Non-Goals와 일관되게 유지. v1.0 대비 §2 Code 경로가 `Iris/Logic/IrisDesc/`, `Iris/UI/Wiki/`, `Iris/UI/Browser/`로 정확화 (R1 반영). §3 Non-Goals에 `implemented_only`를 merge/release closeout으로 사용 금지가 추가되어 governance 강화. §2 Out Of Scope에 Pulse compat wrapper 경로가 `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua`로 정정.

### Missing Scope
- Phase 1 Step 0 path verification에서 `Iris/build/` 하위 파일 누락 (Non-Critical 4.4)
- `approved_diff_log.md`의 surface 분류 누락 (Non-Critical 4.7)

### Explicitly Out Of Scope Consistency
**일관성 양호.** v1.0과 동일하게 모순 없음. v2.0에서 `implemented_only` 의미 봉인 추가로 closeout claim boundary가 §3 + §7 Validation Limits + §12 3중으로 보호됨.

---

## 6. Validation Review

### Missing Validation
- §5 Path Existence Verification에 build 인프라 파일 누락 (Non-Critical 4.4)
- `approved_diff_log.md` 자체의 sealed 여부 검증 누락 (Non-Critical 4.7)
- Phase 9b baseline_screenshot 촬영 시점 명시 누락 (Non-Critical 4.8)

### Weak Validation
- `baseline_test_count` 파싱 규칙 부족 (Non-Critical 4.1)
- `Compare-Object` JSON 깊이 비교 한계 (Critical 3.2)
- PowerShell regex `|` vs 셀 escape `\|` 모호 (Critical 3.1)
- `Get-ChildItem` 결과의 `__pycache__` 처리 모호 (Non-Critical 4.2)

### Validation Ceiling Risk
**낮음 — 적극적으로 차단됨.** §7 Validation Limits에 12개 + `implemented_only` claim 금지 추가로 v1.0 대비 1개 더 차단. §12 Closeout State Semantics가 각 상태의 허용/불허 claim을 표로 봉인. §7 Approved Diff Procedure의 `schema_or_behavior_impact` 필드가 `runtime-impact` 시 manual QA 자동 강제로 cross-reference 차단.

### Validation Practicality
- **realistically executable**: 양호. Critical 3.1·3.2 수정 후 모든 명령이 PowerShell에서 실행 가능.
- **proportionate to risk surface**: 양호. v1.0의 risk mix 문제(Change 7/9) 해소.
- **appropriately scoped**: Phase 10 position carryover (Non-Critical 4.3)가 유일한 잔여 우려. v2.0이 Phase 10 의도를 명확화한 점은 진전.
- **free from unnecessary ceremony**: 양호. Schema 표 도입은 ceremony가 아니라 governance discipline.

---

## 7. Governance Review

### Philosophy.md Compliance
**준수.** §11 Governing Document Source에 11개 항목이 인용 출처와 함께 명시. v1.0의 출처 미확인 문제 해결.

### Architecture Boundary
**준수.** Hub & Spoke 보존, runtime/build-time authority 분리, Recipe/Right-click 2-track 유지가 §11에 인용 출처와 함께 명시.

### Runtime / Build-Time Separation
**준수.** §8 Risk Surface Touch에서 phase별 surface 영향을 분리 표기. Change 1~8, 10은 build-only / doc-only. Change 9a는 behavior-neutral runtime. Change 9b는 runtime UI 영향 + manual QA gate.

### FAIL-LOUD Preservation
**준수.** §11에 인용 명시. §11 Plan Operating Principles의 "No silent compatibility shim" 원칙이 dual-import wrapper에 마감 일자 코멘트를 강제 — silent fallback 누적 차단. §7 Approved Diff Procedure가 SHA drift 회피 경로를 명시 절차로만 허용.

### Authority Ownership
**준수.** §8 Authority Surface에서 v1.0의 "None planned"가 "Concerns controlled"로 정확화됨. evidence skeleton refactor와 classification 작업이 authority-adjacent임을 인정. 이는 v1.0 review의 미세 우려 사항을 자발적으로 격상한 honest amendment.

### Contract Compliance
- `iris_refactoring_final_roadmap_closeout.md` 봉인 영역 침범 없음.
- `phase3_quality_gates_q5_split.md`: Change 4 entry gate에 conflict 14.4 `resolved`로 "추가 split 필요" 판정 요구 — 봉인과 충돌 회피.
- `Iris_Refactoring_Roadmap.md` §14의 6개 conflict: §6 Change 1 Conflict Resolution Gate Schema가 downstream blocking phase 매핑을 명시 — v1.0 review R2 완전 반영.
- `PLAN_TEMPLATE.md`: 12개 섹션 모두 채워짐 + 각 Change가 PLAN_TEMPLATE Change 구조(Purpose/Files/Implementation Notes/Validation/Expected Closeout) 준수.

---

## 8. Risk Surface Touch

### Authority Surface
**Concerns controlled** (v1.0 "None planned"에서 정확화). evidence skeleton과 classification이 authority-adjacent임을 인정. 적절.

### Runtime Behavior Surface
**Concerns** — Phase 9a는 low, Phase 9b는 high. v1.0의 R3 적용으로 분리 명확. Change 9a Validation 표가 manual QA 면제임을 explicit 명시. 적절.

### Compatibility Surface
**Concerns** — direct script execution baseline, public IrisAPI, Pulse wrapper 6개, compose entrypoint. v1.0과 동일. Change 9b에서 Pulse wrapper 제거 명시 차단 + disposition note만 작성.

### Sealed Artifact Surface
**Concerns** — Per-Directory Disposition Schema의 `evidence_type` 필드 (`sealed_evidence` 시 archive 외 disposition 금지)로 v1.0 대비 보호 강화. SHA gate가 모든 Change Validation 표에 일관 적용.

### Public-Facing Output Surface
**Conditional concerns** — Phase 9b 시 concerns, 그 외 None. v2.0에서 "표시 문구/구조 변경은 금지 + manual QA로 보장" 명시.

---

## 9. Risk Review

### Architecture Risk
v1.0 대비 모든 항목에 mitigation 명시 추가. 양호.

### Runtime Risk
- Phase 9b가 표시를 깸 — `phase9b_manual_qa_checklist.md` entry gate deliverable로 사전 차단.
- 진단 능력 저하 — Change 9a closeout 정량 기준 (`generator_debug_count` 의도된 감소량 도달)이 의도된 감소량을 측정 가능하게 함.

### Compatibility Risk
모든 항목에 mitigation. 양호.

### Regression Risk
- Disposition Schema `evidence_type` 필드가 sealed evidence 오판 차단.
- `baseline_test_count` 침범 차단은 Test Baseline Update Rule로 명시.

### Operational Risk
- 12-Change 계획의 partial 누적 — §12 closeout state semantics 분리로 추적 가능성 확보.
- Windows/PowerShell 비호환 — §4 Assumptions + 모든 명령 PowerShell 표기로 차단.

### Validation Risk
- approved diff 회피 — §7 Approved Diff Procedure schema로 차단.
- `implemented_only` 오용 — §12 closeout state semantics로 차단.
- manual QA trigger 누락 — §6 Change 9b Manual QA Trigger Criteria로 차단.
- PowerShell 명령 syntax 버그 (Critical 3.1·3.2) — 본 review의 Required Revisions.

### Governance Risk
- `additive amendment preference` 출처 — §11 Plan Operating Principles로 라벨링.
- gate enforcement — Conflict Resolution Gate Schema + Per-Directory Disposition Schema + Manual QA Checklist Schema 3종으로 schema-driven enforcement 강화.

---

## 10. Required Revisions

### R1 — PowerShell regex 이스케이프 표기 명확화 (Critical 3.1 대응)

Affected section: §6 모든 Change Validation 표 (특히 Change 1 baseline metrics, Change 6 v2.4 hardcode count)

Why required: 표 셀 escape `\|`와 PowerShell pipe operator, regex alternation의 표기가 혼재해 명령 실행 시 의도가 모호.

Minimum acceptable correction:
- §6 또는 §7 머리말에 "표 안의 `\|`는 마크다운 셀 escape이며 실행 시점에 `|`로 풀린다" 한 줄 명시.
- §6 Change 6 v2.4 hardcode count 명령의 regex alternation을 `_archive|historical`로 명시 (현재 `_archive\|historical`).
- 가능하면 baseline metrics 표의 명령들을 인라인 표 형태가 아니라 code block으로 분리해 escape 모호성 제거.

---

### R2 — Phase 4 JSON Schema Diff 명령 교체 (Critical 3.2 대응)

Affected section: §6 Change 4 Validation 표 `Report JSON schema` 행

Why required: `Compare-Object` on PSCustomObject는 첫 레벨만 비교. nested gate-level schema drift 미감지 위험.

Minimum acceptable correction: 다음 셋 중 하나로 교체.
- `(Get-Content before.json | ConvertFrom-Json | ConvertTo-Json -Depth 100) -ne (Get-Content after.json | ConvertFrom-Json | ConvertTo-Json -Depth 100)` (False면 동일)
- `python -c "import json,sys; sys.exit(0 if json.load(open('before.json'))==json.load(open('after.json')) else 1)"`
- `git diff --no-index before.json after.json`

---

## 11. Final Recommendation

**PASS with minor revisions.**

Required Revisions R1·R2(PowerShell syntax 2건)만 적용하면 Phase 1 진입 가능. R1은 §6/§7 머리말 한 줄 + Change 6 명령 한 줄 수정으로 완료. R2는 §6 Change 4 한 줄 교체. 둘 다 코드 변경 없음 — 문서만 수정.

Non-Critical 4.1~4.11은 phase 진행 중 incremental adjustment로 흡수 가능. 다음과 같이 분류:
- Phase 1 진행 중 자연 해소: 4.1 (baseline_test_count parser), 4.2 (`__pycache__`), 4.4 (path verification 확장), 4.10 (baseline 봉인 시점)
- Phase 4 진입 전 권장: 4.7 (approved_diff_log surface)
- Phase 7b 진입 전 권장: 4.9 (delete_candidate field)
- Phase 9b 진입 전 권장: 4.8 (baseline_screenshot 시점)
- 가독성 / consistency: 4.5 (column header), 4.6 (cross-document 점검), 4.11 (§4/§11 동기화), 4.3 (Phase 10 position)

### Blocking conditions
1. R1 — PowerShell regex `_archive|historical` 표기 수정 + 셀 escape 명시 한 줄 추가
2. R2 — Phase 4 JSON schema diff 명령 교체

### Required next actions
1. R1·R2 적용 (수분 작업)
2. Phase 1 진입 — `phase1_inventory_readpoint.md`, `phase1_artifact_source_classification.md`, `phase1_batch1_import_graph.md`, `phase1_conflict_resolution_gate.md`, `phase1_pulse_wrapper_usage_inventory.md`, `phase1_baseline_metrics.md` 6종 deliverable 산출
3. Phase 1 Step 0에서 §5 path 11개 + Non-Critical 4.4 추가 path 검증
4. Phase 1 종료 commit에서 `baseline_test_count` 봉인
5. conflict gate 6/6 충족 시 Phase 1 `complete`
6. Phase 2~10 순차 진입, 각 Change Validation 표 + 정량 closeout 기준 동시 충족

### Out of scope for this review
- 코드 회귀 검증 (각 phase 실행 시점에 수행)
- `docs/EXECUTION_CONTRACT.md` 본문 대조 (별도 검증)
- Pulse / Echo / Fuse / Nerve 영향 분석 (Non-Goals 명시되어 검토 불필요)
- 입력 roadmap 본문 재대조 (roadmap review에서 처리)
- v1.0 review의 closeout 검증 (본 review가 v2.0 변경분에 한정)

---

## 12. Reviewer Notes

### v1.0 → v2.0 변경 반영 매트릭스

| v1.0 review 항목 | v2.0 반영 상태 | 비고 |
| --- | --- | --- |
| R1 (파일 경로 5건 수정) | ✅ 완전 반영 | §5 Code 경로 정정 + §5 Path Existence Verification block 신설 |
| R2 (Change 9 → 9a/9b 분리) | ✅ 완전 반영 | 9a behavior-neutral / 9b renderer split + compat |
| R3 (Change 7 → 7a/7b 분리) | ✅ 완전 반영 | 7a consolidation / 7b archive sweep |
| R4 (정량 closeout 기준) | ✅ 완전 반영 + 강화 | §6 Change 1 Quantitative Baseline 11종 + §12 Per-Change Criteria |
| R5 (§11 거버넌스 출처 확정) | ✅ 완전 반영 | Governing Document Source / Plan Operating Principles 2-tier |
| Non-Critical 4.1 (정량 기준) | ✅ R4와 통합 반영 | — |
| Non-Critical 4.2 (Manual QA trigger) | ✅ 완전 반영 | Change 9b §Manual QA Trigger Criteria + Checklist Schema |
| Non-Critical 4.3 (380 tests 갱신 규칙) | ✅ 완전 반영 | §7 Test Baseline Update Rule |
| Non-Critical 4.4 (Phase 10 position) | ⚠️ 의도 명확화 | Change 10 Files에 "Change 1~9b 통합" 명시 — 위치 유지 |
| Non-Critical 4.5 (Section 11 출처) | ✅ 완전 반영 | R5와 통합 |
| Non-Critical 4.6 (Section 5 ↔ Change 9 일관성) | ✅ 완전 반영 | 모든 경로 enumerate 일관화 |
| Non-Critical 4.7 (family helper trade-off) | ⏸️ 명시 미반영 | Phase 1 결정으로 위임 — 본 plan scope 외 |
| Non-Critical 4.8 (paths_manifest vs JSON) | ⏸️ 명시 미반영 | Phase 1 결정으로 위임 |
| Non-Critical 4.9 (Change 1 14.6 미포함) | ✅ 완전 반영 | §6 Change 1 conflict gate가 14.1~14.6 전수 |
| Non-Critical 4.10 (`Document:` 라벨) | ✅ 완전 반영 | 9b에서 `Disposition note only:` 등 명확 라벨 |
| Non-Critical 4.11 (manual QA checklist 시점) | ✅ 완전 반영 | "entry gate deliverable, Change 진입 전에 작성" 명시 |
| 새 governance 도입 (v1.0 미요구) | ✅ 추가 | Closeout State Semantics, Approved Diff Procedure, Per-Directory Disposition Schema |

### Spot-checked facts (verified 2026-06-07)
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua` 확인 ✓
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua` 확인 ✓
- `Iris/media/lua/client/Iris/IrisMain.lua` 확인 ✓
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` 확인 ✓
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` 확인 ✓
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/{Generator,Logger,Ordering,Renderer,TagParser,Templates}.lua` 6개 확인 ✓
- v1.0 review의 R1 경로 오류 5건 모두 v2.0에서 정정 ✓
- `Iris/build/tools/common/{io,stage_runner,versions}.py` 존재 ✓
- `Iris/build/quality_gates.py` 1542 LOC ✓
- `Iris/build/{recipe,rightclick}_evidence_pipeline.py` 존재 ✓
- v2.0 §11 Governing Document Source의 인용 형식 확인 — 본 review에서 grep 검증한 항목들은 v1.0 review에서 다룸

### Uncertainty disclosure
- `Compare-Object` JSON 깊이 비교 실제 동작은 PowerShell 버전(5.1 vs 7+)에 따라 다를 수 있음. v2.0이 §8에서 "Windows 11 + PowerShell 기본"으로만 명시하므로 5.1로 가정한 review.
- `luac -p`의 Kahlua 환경 호환성은 v1.0 review에서 미확인으로 남겨둠 — v2.0이 §6 Change 9a/9b Validation에서 `luac -p` 사용을 유지하므로 동일 잔여 우려.
- `additive amendment preference` 등이 다른 docs/Iris/*.md에서 인용 출처처럼 등장하는지는 본 review 미확인 (cross-document pollution 가능성 그대로).

### Review limitations
- 본 review는 v1.0 → v2.0 변경분 검토 중심이며, v1.0에서 PASS한 governance/structure 영역은 재검증하지 않음.
- 코드 실제 회귀 가능성은 phase 실행 시점에 별도 검증.
- §6 Change 9b의 manual QA checklist 운영 실효성은 실제 캡처/비교 단계에서만 검증 가능.

### Future follow-up suggestions
- R1·R2 적용 후 short re-review로 PASS 확정 권장.
- Phase 1 deliverable 6종 산출 후 별도 short review로 conflict gate 6/6 충족 + baseline metrics 11/11 측정 확인 권장.
- Change 9b entry gate deliverable `phase9b_manual_qa_checklist.md` 자체의 별도 review (manual QA scenario 적정성).
- 본 plan이 도입한 4종 schema (Conflict Resolution Gate / Per-Directory Disposition / Manual QA Checklist / Approved Diff Log)를 다른 Iris refactor 작업에서도 재사용 가능한 governance pattern으로 추출하는 후속 작업 권장.
