# Iris_Refactoring_Plan_Review.md

> Review target: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v1.0, 2026-06-07)
> Review template: `docs/REVIEW_TEMPLATE.md`
> Upstream documents:
> - `docs/Iris/Iris_Refactoring_Roadmap.md` (Draft, 2026-06-07)
> - `docs/Iris/Iris_Refactoring_Roadmap_Review.md` (WARN, 2026-06-07)
> - `docs/PLAN_TEMPLATE.md`
> Reviewer date: 2026-06-07
> Verification scope: plan 본문 내적 일관성 + 실제 파일 경로 spot check + 직전 roadmap review (R1~R5) 반영 여부 + 인용 문서 grep

---

## 1. Verdict

**WARN** — Phase 1 진입 직전 수정 필수 사항 있음. Phase 2+ 진입 전에는 직전 roadmap review의 R3·R4·R5 carryover도 해결해야 함.

---

## 2. Executive Summary

검토 대상은 `Iris_Refactoring_Roadmap.md`의 10개 Phase를 `PLAN_TEMPLATE.md` 12-section 구조에 맞춰 10개 Planned Change로 1:1 매핑한 실행 계획이다. 직전 roadmap review에서 발견된 **R1(마크다운 이스케이프)과 R2(Section 14 conflict 해소 시점·위치 명시)는 이 plan 단계에서 해결**되었다 — 본문에 백슬래시 이스케이프 없음(template 자체는 escape 잔존), Phase 1 deliverable로 `phase1_conflict_resolution_gate.md`를 명시 신설하고 Change 3·4·7·9 본문이 해당 conflict 해소를 진입 게이트로 참조한다. Pulse compat wrapper 제거를 Change 9에서 명시적으로 제외하고 disposition note만 작성하도록 가둬 둔 점, 기존 `Iris/build/tools/common/{io,stage_runner,versions}.py` 존재를 Section 4 Assumptions에서 인정한 점도 review에서 지적한 Non-Critical 사항을 반영했다.

**Primary strengths**:
- 마크다운 렌더링이 깨끗하다 (template의 `\#`/`\*` escape pollution이 plan 본문에 전염되지 않음)
- Phase 1을 모든 후속 phase의 입력 게이트로 봉인, conflict resolution gate 산출을 first deliverable로 둠
- 각 Change가 conflict 14.N과 명시적으로 연결됨 (Change 3↔14.2, Change 4↔14.4, Change 7↔14.3, Change 9↔14.6)
- Validation Plan(Section 7)에 concrete grep 명령 다수 (`grep -RnE "except ImportError|sys\.path\.insert|v2\.4" Iris/build`)
- Rollback Plan(Section 10)이 phase별 복원 경로 구체화
- Pulse compat wrapper retire를 본 계획 범위 밖으로 명시 차단

**Primary risks**:
- **파일 경로 오류 5건** — Section 5 Code 절과 Change 9 Files 절의 Lua 파일 경로 중 다수가 실제 위치와 다르다. 본 검토에서 `ls` 직접 확인 결과 5/6 경로 실패.
- **직전 roadmap review R3(Phase 9 split) carryover** — Change 9가 여전히 Low Risk(debug 축소, IrisMain helper) + High Risk(IrisWikiSections/IrisBrowserInteractionRenderer split + Pulse wrapper disposition note)를 한 phase에 묶음
- **직전 R4(Phase 7 split) carryover** — Change 7이 High Risk(round consolidation, output drift 가능) + Medium Risk(staging archive sweep) 묶음
- **직전 R5(Success Criteria 정량 기준) carryover** — plan에는 Success Criteria 자체가 없음. PLAN_TEMPLATE에 Success Criteria 절이 없는 게 사실이나, Section 12 Expected Closeout State는 정성 표현(`complete`/`partial`/`implemented_only`)만 사용
- **Section 11에서 인용한 거버넌스 제약 일부의 출처 미확인** — "additive amendment preference, minimal diff preservation"이 `docs/Philosophy.md`/`docs/DECISIONS.md`/`docs/ROADMAP.md`에서 발견되지 않음 (grep 결과)

**Execution should proceed?**:
- Phase 1 진입은 **R1(파일 경로 일괄 수정)** 적용 후 가능. 경로 오류는 Phase 1 자체에도 영향을 줌(Section 5에서 잘못된 경로를 readpoint로 봉인할 위험).
- Phase 2 이후 진입 전에는 **R2(Change 7/9 분리)**와 **R3(정량 closeout 기준)**가 추가되어야 함. 그렇지 않으면 phase 단위 회귀 격리가 어렵고 closeout 판정이 정성적이 됨.

---

## 3. Critical Issues

### Issue 3.1 — 파일 경로 5건 오류

Severity: **Critical (Blocking)**

Impact: Section 5 Code 절과 Change 9 Files 절에 명시된 Lua 파일 경로 5건이 실제 디렉토리 구조와 일치하지 않는다. 본 검토에서 `ls`로 직접 확인:

| 계획 명시 경로 | 실제 위치 | 검증 |
|---|---|---|
| `Iris/media/lua/client/Iris/Generator.lua` | `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua` | ❌ |
| `Iris/media/lua/client/Iris/Renderer.lua` | `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua` | ❌ |
| `Iris/media/lua/client/Iris/IrisMain.lua` | `Iris/media/lua/client/Iris/IrisMain.lua` | ✓ |
| `Iris/media/lua/client/Iris/IrisWikiSections.lua` | `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` | ❌ |
| `Iris/media/lua/client/Iris/IrisBrowserInteractionRenderer.lua` | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` | ❌ |
| `Iris/media/lua/shared/Pulse/IrisDesc*.lua` | `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/{Generator,Logger,Ordering,Renderer,TagParser,Templates}.lua` | ❌ |

실제 디렉토리 구조:
- `Iris/media/lua/shared/`는 `translate/`만 포함, `Pulse/` 하위 없음
- runtime IrisDesc는 `Iris/Logic/IrisDesc/` 하위에 6개 파일 (Generator/Logger/Ordering/Renderer/TagParser/Templates)
- Pulse compat wrapper는 `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/` 하위에 동일 6개 파일을 미러링

Affected Scope:
- Section 5 Code 절 (잘못된 readpoint 봉인 위험)
- Change 9 Files 절 전체 (Generator/Renderer/Wiki/Browser/Pulse 경로 모두)
- Phase 1 inventory가 잘못된 경로를 기반으로 산출될 위험
- Phase 9 grep/diff/manual QA가 잘못된 위치를 가리켜 실제 코드를 못 찾을 위험

Related Surface:
- Runtime Behavior Surface (Phase 9 대상 파일이 잘못 지정됨)
- Sealed Artifact Surface (Pulse wrapper inventory가 잘못 잡힘)

Required Fix:
- 위 표의 "실제 위치" 컬럼으로 5개 경로 일괄 수정
- Pulse compat wrapper glob을 `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua`로 명시 (6개 파일 enumerate 권장)
- Section 5 Code 절과 Change 9 Files 절 양쪽에서 수정 일관성 확보

Blocking Reason: Phase 1 readpoint가 잘못된 경로 위에 봉인되면 후속 phase 모두 잘못된 분모를 사용한다. Phase 9 진입 시 grep이 실제 파일을 못 찾아 split 작업이 시작도 못 함.

---

### Issue 3.2 — Roadmap Review R3 carryover (Change 9 위험도 혼재)

Severity: **High (Blocking for Phase 9 entry)**

Impact: 직전 roadmap review가 Critical Issue 3.3으로 지적한 Phase 9 위험도 혼재가 본 plan에서 그대로 carryover됐다. Change 9가 다음 작업을 한 phase commit batch로 묶는다:
- Generator/Renderer debug 라인 축소 (Low Risk, debug gate로 보호됨)
- IrisMain.lua helper 통합 (Low Risk, INIT_MODULES 데이터 흡수)
- **IrisWikiSections.lua 분리** (High Risk, 607 LOC user-facing UI)
- **IrisBrowserInteractionRenderer.lua 분리** (High Risk, user-facing UI)
- **Pulse compat wrapper disposition note** (Medium Risk, 제거는 제외되나 disposition 판정 자체는 governance 영향)
- `_dev/` 파일 정리 (Low Risk)

Section 9 Risk Analysis도 "Phase 9 runtime Lua 변경이 Browser/Wiki/Tooltip 표시를 깨고, manual QA가 늦어져 silent regression이 사용자 시점에 노출"을 Runtime Risk로 인정하지만 Change 9 본문은 여전히 단일 phase. Section 12 Expected Closeout에서 "manual QA 수행 시 partial/complete, 미수행 시 implemented_only"로 끝내는 결정도 Low Risk 작업까지 manual QA gate에 묶이는 부작용이 있다 (debug 축소가 manual QA를 기다리는 구조).

Affected Scope:
- Change 9 전체
- Section 7 Manual Validation 절 (Phase 9 한정 manual QA 항목이 너무 많은 작업을 트리거)
- Section 9 Runtime Risk
- Section 12 Phase 9 closeout 분기

Related Surface:
- Runtime Behavior Surface
- Public-Facing Output Surface (Wiki/Browser split)
- Compatibility Surface (Pulse wrapper disposition)

Required Fix: Change 9를 두 개로 분리.
- Change 9a — Behavior-Neutral Runtime Cleanup: Generator/Renderer debug 라인 축소, IrisMain INIT_MODULES helper 흡수, `_dev/IrisTranslationDebug.lua` 및 `_dev/media/` 미사용 검증, debug text 산출물 archive 후보 분류. Validation: Lua syntax + `[Iris] Bootstrap complete` console smoke + 380 tests OK. **Manual in-game QA 불필요**.
- Change 9b — Runtime Renderer Responsibility Split + Compatibility Wrapper Disposition: IrisWikiSections.lua 분리, IrisBrowserInteractionRenderer.lua 분리, Pulse compat wrapper disposition note 작성. Validation: 위 + manual in-game QA(Browser/Wiki/Tooltip 화면 비교) + conflict 14.5 별도 결정 확인.

Blocking Reason: 위험도가 다른 작업을 한 commit batch로 묶으면 회귀 발견 시 어느 변경이 원인인지 격리하기 어렵고, Low Risk 작업이 manual QA 대기 상태로 묶여 phase 진행이 느려진다.

---

### Issue 3.3 — Roadmap Review R4 carryover (Change 7 위험도 혼재)

Severity: **High (Blocking for Phase 7 entry)**

Impact: 직전 roadmap review의 Non-Critical 4.1이 본 plan에서 carryover됐다. Change 7이 다음을 한 phase에 묶음:
- Consolidation: `build_post_cleanup_phase3_pkg3{a..j}`, `build_source_coverage_{b1..b4,c1a..c1e}`, `build_identity_fallback_batch{2..9}_authority_promotion`, `freeze_quality_baseline_v{1..4}`, `report_*_{draft,final}` 통합 (High Risk, output drift / hidden branch logic 위험)
- Archive sweep: 종료 staging directory를 `_archive/staging/<original>/`로 `git mv` (Medium Risk, 진행 중 round 오인 위험)
- `_archive/p0-2/Iris/Iris/...` 중첩 백업 disposition note (Low Risk, 본 phase 외부 결정으로 분리됨)

Section 9 Regression Risk에 "consolidation 후 output drift (동일해 보이는 batch에 숨은 branch logic 존재 가능)"가 인정되지만 phase 단위는 그대로다.

Affected Scope:
- Change 7 전체
- Section 12 Expected Closeout (Change 7 `partial` 사유)

Related Surface:
- Sealed Artifact Surface (output drift 위험)
- Authority Surface는 영향 없음

Required Fix: Change 7을 두 개로 분리.
- Change 7a — Selective Round Script Consolidation: 통합 후보별 SHA 비교, batch config JSON 외부화, 통합 entrypoint 생성. Validation: artifact SHA 비교, 380 tests OK.
- Change 7b — Staging and Nested Archive Sweep: per-directory disposition, `git mv` 기반 이동, hard-coded staging path grep 사전 검증. Validation: grep 결과 검증, 380 tests OK.

Blocking Reason: 동일 phase 내에서 High와 Medium 위험을 섞으면 rollback granularity가 비대해진다. Change 7b는 7a보다 먼저 또는 독립으로 진행 가능 (의존성 없음).

---

## 4. Non-Critical Issues

### 4.1 R5 carryover — 정량 closeout 기준 부재
직전 roadmap review의 R5(Success Criteria 정량 기준 복원)가 plan에 반영되지 않았다. PLAN_TEMPLATE에 별도 Success Criteria 절이 없는 것은 사실이지만, Section 7 Validation Plan과 Section 12 Expected Closeout State에 grep-checkable 정량 기준을 분산 포함하면 plan-only 보강 가능. 다음 정량 항목 권장:
- `grep -RnE "from tools\.build\.build_identity_fallback_batch1" Iris/build | wc -l == 0` (Change 2 closeout)
- `grep -RnE "except ImportError" Iris/build/description/v2/tools/build/compose_layer3_*.py | wc -l == 0` (Change 3 closeout)
- staging top-level 디렉토리 수 (Phase 1 baseline → Change 7b 종료 시 비교)
- `tools/build/` Python LOC 변동률 (Phase 1 baseline → 전체 종료 시)
- Generator.lua + Renderer.lua의 `Logger.debug(` 호출 횟수 (Change 9a baseline → 종료 시)

본 항목은 `phase1_inventory_readpoint.md`에 baseline 측정을 함께 포함하면 자연스럽게 닫힌다.

### 4.2 Manual QA trigger 기준 미정의
Change 9 Validation에 "manual in-game QA — Browser / Wiki / Tooltip 화면 캡처 비교 (behavior claim 전 필수)"가 있고 deliverable로 `phase9_manual_qa_checklist.md`가 있으나, **어떤 변경이 manual QA를 trigger하는가**의 기준이 plan 본문에 없다. Change 9가 두 파트로 분리되면(Issue 3.2 R3) trigger 기준은 "Change 9b 진입 시 자동 trigger, Change 9a는 manual QA 면제"로 자연 해결되지만, 분리 전에는 다음 기준 추가 권장:
- Lua module이 새로 생성되거나 분할된 경우
- 함수 시그니처가 외부 caller에게 노출되는 경우
- 한국어 표시 문구가 포함된 module을 수정한 경우
- INIT_MODULES spec이 변경된 경우 (boot sequence 영향)

### 4.3 380 tests baseline의 phase별 갱신 규칙 부재
Section 4 Assumptions에 "380 tests OK 기준은 Phase 1 시점에 재측정된다"가 있지만, Change 5(evidence pipeline skeleton)와 Change 10(test discovery normalization)이 test count 자체를 변경할 수 있는 phase다. baseline이 변동되면 Change 6 이후의 `380 tests OK 유지` 비교가 깨진다. Rollback Plan 또는 Validation Plan에 "phase별 baseline 갱신 규칙: Change N에서 test count 변동 시 closeout 문서에 신규 baseline 명시" 추가 권장.

### 4.4 Phase 10 position carryover
Phase 10(test discovery normalization)이 여전히 마지막이다. roadmap review Non-Critical 4.9에서 지적한 대로, Change 2/3/4/5의 import contract 변경이 test discovery에 영향을 줄 수 있는 구조라면 Phase 10은 Phase 3 직후로 이동하는 게 자연스럽다. 또는 Phase 10을 "Phase 1과 Phase 4 사이의 mid-validation gate"로 재배치. 최소한 Section 12 Expected Closeout에서 "Phase 10이 마지막에 위치하는 이유"를 한 줄로 정당화 권장.

### 4.5 Section 11 거버넌스 제약 일부 출처 미확인
Section 11 본문에 "추가 제약 (`docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` 현행): additive amendment preference, minimal diff preservation, 기존 authority ownership 보존"이 명시되어 있으나, 본 검토에서 `grep "additive amendment\|minimal diff" docs/Philosophy.md docs/DECISIONS.md docs/ROADMAP.md` 결과 **매치 없음**. PLAN_TEMPLATE 예시 문구를 그대로 인용한 것으로 보임 (template Section 11에 "additive amendment preference"가 example로 등장). 출처 미확인 제약을 거버넌스 규약으로 사용하면 후속 phase에서 해석 분쟁 가능. 두 가지 처리 옵션:
- 옵션 A: 실제 출처가 있다면 docs 내 정확한 위치 인용 (`docs/Philosophy.md:LXX`)
- 옵션 B: 출처가 없으면 "본 plan 자체 운영 원칙"으로 라벨링 변경 또는 제거

### 4.6 Section 5 Code의 Pulse wrapper glob과 Change 9 Files 불일치
Section 5 Code에 `Iris/media/lua/shared/Pulse/IrisDesc*.lua`로 표기, Change 9 Files에 `Iris/media/lua/shared/Pulse/IrisDesc*.lua (compatibility wrapper)`로 표기. 둘 다 잘못된 경로지만 일관되게 잘못됨. Issue 3.1과 함께 일괄 수정. 정확한 enumerate:
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Generator.lua`
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Logger.lua`
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Ordering.lua`
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Renderer.lua`
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/TagParser.lua`
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Templates.lua`

### 4.7 Change 2 Files의 family helper 위치 모호
Change 2 Files에 "Create: `Iris/build/tools/common/family_io.py` 또는 family별 helper module (Phase 1 분류 기준 결정)"로 표기. 두 옵션을 Phase 1 결정으로 위임한 점은 합리적이나, 두 옵션의 trade-off가 plan에 명시되지 않음. 단일 `family_io.py`는 family 간 격리 약화 위험, family별 module은 import surface 비대화 위험. Implementation Notes에 trade-off 한 줄 추가 권장.

### 4.8 Change 6의 `paths_manifest.py` vs `manifest.json` 선택 위임
Change 6 Files에 "Create: `Iris/build/tools/common/paths_manifest.py` 또는 `manifest.json` (Phase 1 분류 기준 결정)"로 표기. Change 2와 같은 패턴. Python module은 코드 호출 측 부담 적음 / JSON은 외부 도구 접근 가능. 어느 결정이 든 후속 phase의 import 경로에 영향. 결정 기준 한 줄 추가 권장.

### 4.9 Change 1 conflict resolution gate의 14.6 미포함
Change 1 Purpose에 "roadmap section 14의 6개 conflict 중 14.1 (script count), 14.4 (quality_gates split 현황), 14.5 (compatibility surface)의 게이트 입력을 제공한다"고 명시. 14.2(direct script execution baseline), 14.3(archive 정책), 14.6(runtime cleanup 범위) 3개의 입력 제공자가 누구인지 본문 명시 부족. Files에 `phase1_conflict_resolution_gate.md`가 6개 모두를 포함한다고 명시되지만, Purpose 본문이 3개만 언급. 본문 갱신 권장 — Purpose에 6개 모두 명시.

### 4.10 Change 9의 Pulse wrapper 처리 명확성
Change 9 Implementation Notes에 "Pulse IrisDesc compatibility wrapper는 본 phase에서 제거하지 않는다"가 있고 Section 8 Compatibility Surface에서도 동일하게 명시. 다만 Change 9 Files에 "Document: `Iris/media/lua/shared/Pulse/IrisDesc*.lua` (compatibility wrapper disposition note만, 제거 금지)"로 표기되어 있어, "수정 없음 + disposition note만 작성"이 명확하나 `Document:` 라벨이 PLAN_TEMPLATE 표준 라벨이 아님(Modify/Create/Move/Split 사용 중). 라벨 통일 권장.

### 4.11 `phase9_manual_qa_checklist.md` 산출 시점
Change 9 Files에 deliverable로 `phase9_manual_qa_checklist.md`가 명시되지만, 이 체크리스트가 Change 9 진입 전에 완성되어야 하는지 phase 진행 중에 작성되는지 본문에 없음. Issue 3.2 R3 적용 시 "Change 9b 진입 전 작성"으로 명시 가능. 진입 게이트로 두지 않으면 manual QA가 ad-hoc하게 진행될 위험.

---

## 5. Scope Review

### Scope Drift
**없음.** Scope(Section 2)와 Out Of Scope, Non-Goals(Section 3)가 roadmap의 Constraints/Non-Goals와 일관되게 좁혀짐. roadmap에 없는 새 surface 도입 없음. PLAN_TEMPLATE에 Scope 절이 있는 구조이며 모두 채워짐.

### Missing Scope
- **Pulse compat wrapper 6개 파일의 grep / require 사용처 inventory** — Section 5 Generated Artifacts 또는 Change 1 deliverable에 명시되지 않음. wrapper retire 결정이 본 계획 범위 외이지만, retire 시점이 왔을 때 사용처를 모르면 결정 자체가 불가능. Phase 1 inventory가 사용처 매핑까지 산출하는지 본문 모호.
- **`Iris/output/` 44개 entry의 source/generated 1차 분류표 입력 owner** — Change 1 deliverable에 `phase1_artifact_source_classification.md`가 있고, Change 8에서 `phase8_artifact_source_classification.md`(확정판)를 만든다. Phase 1과 Phase 8 사이 누가 분류 정확성을 검증하는지 owner 모호. roadmap review Non-Critical 4.5 carryover.
- **`Iris/build/package/Iris/...` 미러링 산출물 분류** — Change 1 Implementation Notes에 "Iris/output, Iris/build/package, Iris/media/lua/client/Iris/IrisLayer3Data.lua 및 chunks의 tracked policy를 분리"가 있으나, `Iris/build/package/Iris/media/lua/client/Iris/Compat/` 같이 깊이 미러링된 산출물의 분류 owner 모호.

### Explicitly Out Of Scope Consistency
**일관성 양호.** Section 2 Explicitly Out Of Scope 10개 항목과 Section 3 Non-Goals 8개 항목, Section 11 Governance Constraints 13개 항목 간 모순 없음. roadmap의 Constraints 12개 + Non-Goals 13개와도 정합. 두 출처 모두에서 다음이 일관:
- 재설계 금지 (taxonomy / evidence / Source authority / Layer 3 body / UI / chunking / cross-module)
- 선언 금지 (release / deployment / Workshop / B42 / production / runtime equivalence)
- 확장 금지 (capability / Outcome / Source / 설명 문장 rewrite)

---

## 6. Validation Review

### Missing Validation
- **파일 경로 자체에 대한 사전 검증 (Issue 3.1 cause)** — Section 5 Code의 경로가 실제 존재하는지 plan 자체에서 검증되지 않음. Phase 1 첫 단계에 "Section 5의 모든 경로를 `ls`로 존재 검증" 추가 권장.
- **Pulse compat wrapper 사용처 grep** — Change 9 Implementation Notes에 "compatibility surface, deprecation decision 필요"만 있고, 사용처 매핑은 별도 산출물로 없음. 본 plan에서 retire하지 않더라도 inventory는 phase 1에서 만들어두는 게 미래 결정의 입력이 된다.
- **`additive amendment preference` 등 인용 거버넌스의 출처 검증 (Non-Critical 4.5)** — 본 plan 자체로는 검증되지 않음. self-review gate에 포함 권장.

### Weak Validation
- **"focused unittest where available"** (Change 2)와 **"focused root build tests"** (Change 10) — "where available"이 회피 경로. Phase 1 inventory에서 각 family의 unittest 존재 여부를 enumerate한 후 closeout 기준으로 사용해야 함.
- **"output hash 또는 approved diff"** (Change 2/4/5/6/7) — `approved diff`의 self-approval 기준이 없음. 단일 maintainer 환경이라도 "diff 검토 사유를 closeout note에 기록"같은 최소 규약 권장.
- **"path resolution unit tests 또는 focused script tests"** (Change 6) — 어느 쪽으로 가는지 결정 기준 없음. Implementation Notes에 결정 트리거 추가 권장.
- **Lua syntax check `luac -p` 또는 동등** (Change 9) — Kahlua 환경에서 `luac -p`가 모든 PZ Lua를 검증하는지 확인되지 않음. Phase 9 진입 전 `luac -p`가 환경에서 동작하는지 sanity check 필요.

### Validation Ceiling Risk
**낮음 — 적극적으로 차단됨.** Section 7 Validation Limits에 12개 항목이 명시적으로 차단되어 있고, "public-facing 문구/한국어 설명 변경 validation (non-goal)"이 추가되어 roadmap의 11개보다 1개 더 차단. Section 12 Expected Closeout이 phase별 `implemented_only` 옵션을 명시해 manual QA 미수행 시 closeout이 자동으로 다운그레이드되도록 함 — 과대 주장 회피 메커니즘.

다만:
- "approved diff" 라벨이 ceiling 회피 경로로 쓰일 수 있음 (위 Weak Validation 참조)
- Section 4 Assumptions의 "한국어 KO mode boot 검증과 in-game manual QA가 필요한 phase는 Phase 9 한정"이 정확하나, Issue 3.2 R3 적용 시 "Change 9b 한정"으로 더 좁혀야 함.

### Validation Practicality
- **realistically executable**: 대부분 그러함. 단일 maintainer + PZ Lua 환경 가정. Change 9b의 manual QA는 reproducible scenario(어떤 아이템 / 어떤 화면 / 어떤 캡처 비교) 사전 정의가 있어야 매 phase 일관 실행 가능.
- **proportionate to risk surface**: Change 7/9의 위험 mix 외에는 양호. Change 4(quality_gates split)에 reporting JSON/Markdown schema diff를 검증으로 둔 점은 적절.
- **appropriately scoped**: Phase 10 position이 어색 (Non-Critical 4.4). 그 외 양호.
- **free from unnecessary ceremony**: 양호. 새 test infra 도입 차단, dual-import wrapper TODO 마감 일자 명시 등 운영 부담 최소화.

---

## 7. Governance Review

### Philosophy.md Compliance
**준수.** Section 11에 "Iris는 100% Lua 기반 위키형 정보 모드", "Iris는 해석, 권장, 비교를 하지 않는다", "facts → decisions → profiles → render", "FAIL-LOUD validation과 determinism gate" 명시. roadmap의 Constraints와 정합. 다만 Section 11의 일부 인용 출처 미확인 (Non-Critical 4.5).

### Architecture Boundary
**준수.** Hub & Spoke 보존(Pulse 의존성 없음, 다른 module 변경 없음), runtime/build-time authority 분리, Recipe / Right-click 2-track 유지가 Section 11에 명시.

### Runtime / Build-Time Separation
**준수.** Change 1~8, 10은 build-only 또는 doc-only. Change 9만 runtime. Section 8 Risk Surface Touch가 phase별 surface 영향을 분리해 표기.

### FAIL-LOUD Preservation
**준수.** Section 11에 "FAIL-LOUD validation과 determinism gate를 약화하지 않는다" 명시. Change 2의 dual-import wrapper TODO 마감 일자 코멘트가 silent fallback 방지에 기여. Change 3의 `grep "except ImportError"` 빈도 추적이 silent compatibility shim 누적 차단.

### Authority Ownership
**준수.** Section 8 Authority Surface에 "build helper extraction, family consolidation, stage skeleton sharing은 authority ownership 이동이 아니다", "Recipe / Right-click evidence decision authority는 track별로 유지" 명시. Change 5의 "두 track의 의미 체계 혼합 금지" 거버넌스 제약과 정합.

### Contract Compliance
- `iris_refactoring_final_roadmap_closeout.md` (2026-05-08) + v4.1 addendum (2026-05-12): 봉인 영역 침범 없음. Section 4 Assumptions에 "Layer 3 runtime data는 chunk-only 구조이며 generated Lua는 수동 편집 대상이 아니다" 명시.
- `phase3_quality_gates_q5_split.md`: Change 4 진입을 conflict 14.4 결정에 종속시켜 봉인과 충돌 회피.
- `docs/PLAN_TEMPLATE.md`: 12개 섹션 구조 모두 채워짐. ✓
- `docs/EXECUTION_CONTRACT.md`: 본 검토 범위에서 직접 대조 안 함. Section 5 명시된 `direct script execution baseline`이 EXECUTION_CONTRACT.md에 정의되는지는 별도 검증 필요.
- `Iris_Refactoring_Roadmap.md`: plan이 roadmap의 10 phase를 1:1 매핑하므로 직접 정합. 다만 roadmap review가 권장한 phase 분리(R3/R4)가 반영되지 않음 — roadmap 본문은 따르되 roadmap review의 권장은 미반영.

---

## 8. Risk Surface Touch

### Authority Surface
**None planned.** Section 8에서 "build helper extraction, family consolidation, stage skeleton sharing은 authority ownership 이동이 아니다" 명시. authority-bearing artifact 수정 시 별도 scope lock + disclosure + amendment 명시. 적절.

### Runtime Behavior Surface
**Potential impact, Phase 9 한정.** Section 8이 Change 1~8, 10은 build-only로 제한, Change 9만 runtime impact 명시. 단 Issue 3.1 경로 오류로 인해 실제로 어느 파일을 다루는지 plan으로는 정확히 알 수 없는 상태. 경로 수정 후 재확인 필요.

### Compatibility Surface
**Concerns 있음 — 적절히 식별됨.** 4개 surface 명시:
- direct script execution baseline (conflict 14.2)
- public `IrisAPI`
- Pulse namespace compat wrapper
- compose module entrypoint

Change 9에서 Pulse wrapper 제거를 명시 차단하고 disposition note만 작성하도록 가둠. 적절. 다만 경로 오류(Issue 3.1)로 인해 실제 disposition 대상 file을 본 plan으로는 정확히 가리킬 수 없음.

### Sealed Artifact Surface
**Concerns 있음 — 적절히 보호됨.** Section 8에 `IrisLayer3Data.lua`, Layer3 chunks, UseCaseDescriptions chunks, classification/index generated data를 sealed로 명시. Phase 1/7/8 분류 작업이 sealed evidence를 untracked/disposable로 오판하지 않도록 disposition 표를 단일 진리로 사용한다는 원칙 명시.

**Minor gap**: Section 4 Generated Artifacts 절에 sealed artifact 목록이 enumerate되어 있으나, 동일 파일들이 Section 5 Generated Artifacts에도 있고 `Iris/build/description/v2/output/**`과 `Iris/output/**`이 어느 쪽이 sealed인지는 분류표(Phase 1/8) 산출 전까지 모호. 이건 본 plan의 한계가 아니라 의도된 결과 — 분류 자체가 산출물이므로.

### Public-Facing Output Surface
**기본 목표 None.** 한국어 설명 변경이 Non-Goals. Browser/Wiki/Tooltip 표시는 Change 9b(분리 시) 대상이며 manual QA 게이트로 보호. 적절.

---

## 9. Risk Review

### Architecture Risk
- batch1 import 해소 누락으로 dual-import wrapper 영구화 — Change 2 Implementation Notes의 "TODO/스코프 마감 일자를 wrapper 코멘트에 명시"로 부분 완화. 추적 메커니즘 추가 권장.
- compose import dance 정리와 direct script execution baseline 보존 충돌 — Change 3가 conflict 14.2에 종속되어 적절히 대응.
- `quality_gates.py` split의 reporting schema drift — Change 4 Validation의 "before/after report JSON/Markdown schema diff (unchanged 또는 approved diff)"로 차단. self-approval 기준은 미정 (Weak Validation 6 참조).
- evidence pipeline skeleton 공통화의 Recipe/Right-click 의미 체계 혼합 — Change 5 Implementation Notes "두 track의 의미 체계 혼합 금지" 명시 + governance constraint로 차단.
- runtime UI split (Change 9b)의 INIT_MODULES spec 복잡도 — Issue 3.2 R3로 분리 시 자연 완화. 분리 전 진입 시 위험 잔존.

### Runtime Risk
- Issue 3.1 경로 오류 carryover — Change 9가 잘못된 파일을 가리키면 runtime 변경 자체가 실제 코드에 적용 안 됨.
- Phase 9 runtime 변경 silent regression — Change 9 분리(Issue 3.2 R3)로 9a는 무관, 9b만 위험 한정.
- `_dev/IrisTranslationDebug.lua`, `_dev/media/`가 실제 runtime require되는데도 archive 후보 오판 — Change 9 Implementation Notes "runtime 미참조 확인 후에만 archive 또는 ignore 후보로 둔다"로 차단. grep으로 require 추적이 deliverable에 포함되는지 명시 권장.
- Generator/Renderer debug line 축소로 진단 능력 저하 — Section 9 Runtime Risk에 명시. trace mode 분리 옵션이 Implementation Notes에 있으나 trade-off 판단 기준 부족.
- Pulse compat wrapper 외부 require 경로 — Change 9에서 제거 차단으로 mitigate.

### Compatibility Risk
- direct script execution baseline이 conflict 14.2 결정 전 깨질 위험 — Change 3가 명시적으로 14.2 종속, 결정 미뤄지면 `partial` closeout으로 contract drift 차단.
- version/path manifest migration이 historical oneshot script reproduction path 손상 — Change 6 Implementation Notes의 "historical oneshot script의 reproduction path는 예외 문서화로 남긴다 (삭제하지 않음)"로 차단.
- test discovery normalization이 default 실행 test 집합 변경 — Change 10이 마지막에 위치해 phase 2~9 영향 흡수 부담. Non-Critical 4.4.
- archive movement가 hard-coded staging path를 보유한 build script 깸 — Change 7 Validation의 "staging path reference grep (`grep -Rn "staging/<moved>" Iris/build`)"로 차단.

### Regression Risk
- consolidation 후 output drift (Change 7) — Implementation Notes의 "batch별 차이가 hidden branch logic이 아닌 단순 설정 차이인 것을 grep + diff로 확인한 후에만 통합"으로 차단. 하지만 grep + diff 정확도 자체는 sample size에 의존.
- helper migration 중 common constant/function 누락 (Change 2) — Validation의 "family별 direct script smoke"로 부분 차단. 누락 발견은 사후적.
- ROOT/sys.path bootstrap cleanup 중 import cycle (Change 3) — Implementation Notes의 "path helper는 `Iris.build.tools.common.paths`처럼 leaf module로 유지"로 차단.
- sealed evidence 오판으로 SHA drift — Phase 1/7/8의 disposition 표 단일 진리 정책으로 차단. 분류 정확도에 의존.
- `380 tests OK` baseline 침범 — Phase 1 재측정 + 모든 phase Validation에 `380 tests OK 유지` 명시. baseline 갱신 규칙은 미정 (Non-Critical 4.3).

### Validation Risk
- "manual QA where required"의 trigger 기준 부재 (Non-Critical 4.2) — Issue 3.2 R3 적용 시 자연 해결.
- "focused unittest where available"의 회피 경로 (Weak Validation 5)
- "approved diff"의 self-approval 기준 모호 (Weak Validation 6)
- `luac -p`의 Kahlua 호환성 미확인 (Weak Validation 8)
- 파일 경로 오류로 Validation 명령 자체가 실제 파일을 못 찾을 위험 (Issue 3.1)

### Governance Risk
- 낮음. Constraints / Non-Goals / Validation Limits / Compatibility Surface 단단함.
- Minor: Section 11 인용 거버넌스 일부 출처 미확인 (Non-Critical 4.5).
- Minor: Change 2 dual-import wrapper의 silent compatibility shim 누적 잠재 — TODO 마감 일자로 부분 완화.

---

## 10. Required Revisions

### R1 — Section 5 + Change 9 파일 경로 5건 일괄 수정 (Critical 3.1 대응)

Affected section: Section 5 Code, Change 9 Files

Why required: 5/6 파일 경로가 실제 디렉토리와 다름. 잘못된 경로 위에 Phase 1 readpoint가 봉인되면 모든 후속 phase가 잘못된 분모를 사용. Phase 9 grep/manual QA가 실제 코드를 가리키지 못함.

Minimum acceptable correction:
- `Iris/media/lua/client/Iris/Generator.lua` → `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua`
- `Iris/media/lua/client/Iris/Renderer.lua` → `Iris/media/lua/client/Iris/Logic/IrisDesc/Renderer.lua`
- `Iris/media/lua/client/Iris/IrisWikiSections.lua` → `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/IrisBrowserInteractionRenderer.lua` → `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/shared/Pulse/IrisDesc*.lua` → `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua` (6개 파일 enumerate 권장)

Phase 1 첫 단계에 "Section 5의 모든 경로를 `ls`로 존재 검증" 추가 권장 (재발 차단).

---

### R2 — Change 9를 9a / 9b로 분리 (Critical 3.2 대응)

Affected section: Change 9, Section 7 Manual Validation, Section 9 Runtime Risk, Section 12 Expected Closeout

Why required: 한 Change에 Low Risk(debug 축소, IrisMain helper)와 High Risk(Wiki/Browser split, Pulse wrapper disposition)가 묶이면 회귀 격리가 어렵고, Low Risk 작업이 manual QA 대기 상태로 묶임.

Minimum acceptable correction:
- Change 9a — Behavior-Neutral Runtime Cleanup: Generator.lua/Renderer.lua debug 축소, IrisMain.lua helper 흡수, `_dev/` 미사용 검증. Validation: Lua syntax + console smoke + 380 tests OK. Manual QA 면제.
- Change 9b — Runtime Renderer Responsibility Split + Compat Disposition: IrisWikiSections.lua 분리, IrisBrowserInteractionRenderer.lua 분리, Pulse compat wrapper disposition note. Validation: 9a + Browser/Wiki/Tooltip manual QA + conflict 14.5 결정 확인 + `phase9_manual_qa_checklist.md` 사전 완성.
- Section 7 Manual Validation을 "Change 9b 한정"으로 정정.
- Section 12 Expected Closeout 분기 분리 (9a → `complete`, 9b → manual QA에 따라).

---

### R3 — Change 7을 7a / 7b로 분리 (Critical 3.3 대응)

Affected section: Change 7, Section 12 Expected Closeout

Why required: High Risk(consolidation) + Medium Risk(archive sweep)가 한 phase에 묶이면 rollback granularity 비대화.

Minimum acceptable correction:
- Change 7a — Selective Round Script Consolidation: 통합 후보별 SHA 비교, batch config JSON 외부화. Closeout: `partial` (후보별 sub-round).
- Change 7b — Staging and Nested Archive Sweep: per-directory disposition, `git mv` 이동. Closeout: `complete`.
- 7b는 7a 의존성 없음 — 독립 또는 선행 진행 가능.

---

### R4 — 정량 closeout 기준 추가 (Non-Critical 4.1 대응, 권장)

Affected section: Section 7 Automated Validation, Section 12 Expected Closeout, Change 1 deliverable

Why required: 정성 closeout 기준만으로는 phase 종료 판정이 모호. self-disagreement 여지 큼.

Minimum acceptable correction: 다음 grep-checkable 기준을 Change별로 분산 추가:
- Change 2 closeout 기준: `grep -RnE "from tools\.build\.build_identity_fallback_batch1" Iris/build/description/v2/tools/build | wc -l == 0`
- Change 3 closeout 기준: `grep -RnE "except ImportError" Iris/build/description/v2/tools/build/compose_layer3_*.py | wc -l == 0`
- Change 7b closeout 기준: staging top-level 디렉토리 수 (Phase 1 baseline → 종료 시 비교)
- Change 9a closeout 기준: Generator.lua + Renderer.lua의 `Logger.debug(` 호출 수 (Phase 1 baseline → 종료 시 측정)
- Phase 1 deliverable `phase1_inventory_readpoint.md`에 위 기준의 baseline을 측정값으로 함께 기록.

---

### R5 — Section 11 인용 거버넌스 제약의 출처 확정 (Non-Critical 4.5 대응)

Affected section: Section 11 마지막 bullet

Why required: "additive amendment preference, minimal diff preservation"이 인용 문서에서 grep으로 발견되지 않음. 출처 미확인 제약은 거버넌스 분쟁 위험.

Minimum acceptable correction:
- 옵션 A: 실제 출처 확인 후 정확한 위치 인용 (`docs/Philosophy.md:LXX`).
- 옵션 B: "본 plan 자체 운영 원칙"으로 라벨 변경하고 인용 문서 제거.
- 옵션 C: PLAN_TEMPLATE 예시 인용임을 본문에 명시.

---

## 11. Final Recommendation

**WARN — Phase 1 진입은 R1 후 가능, Phase 2+ 진입은 R2·R3 후 가능. R4·R5는 권장.**

Phase 1은 R1(파일 경로 수정) 적용만으로 진입 가능. Phase 1이 산출하는 inventory가 R4의 baseline 측정과 자연스럽게 연동되므로, Phase 1 진행 중 R4도 함께 적용 가능.

Phase 2 이후 진입 전에는 R2(Change 9 분리)와 R3(Change 7 분리)가 적용되어야 함. 이 둘은 plan 본문 수정만으로 가능하며 코드 변경 없음. Phase 1 deliverable인 `phase1_conflict_resolution_gate.md`가 14.6(runtime cleanup 범위)을 닫는 시점에 R2가 자연 강제됨 — Phase 1 진입 후 R2를 닫는 흐름이 자연스러움.

R5는 거버넌스 신뢰도 문제이며 Phase 1 deliverable 산출 전까지는 부분적으로 미뤄도 됨.

### Blocking conditions
1. **R1** — Section 5/Change 9 파일 경로 5건 오류. Phase 1 진입 직전 수정 필수.
2. **R2** — Change 9 위험도 혼재. Phase 2~8 진입은 영향 없으나 Phase 9 진입 전 분리 필수.
3. **R3** — Change 7 위험도 혼재. Phase 7 진입 전 분리 필수.

### Required next actions
1. R1 일괄 수정 (수분 작업).
2. Phase 1 진입 — `phase1_inventory_readpoint.md`, `phase1_artifact_source_classification.md`, `phase1_batch1_import_graph.md`, `phase1_conflict_resolution_gate.md` 산출.
3. Phase 1 진행 중 R4 baseline 측정값 함께 기록.
4. Phase 1 closeout 후 plan 본문에 R2·R3·R5 적용 (Phase 2 이전).
5. R4 grep-checkable 기준을 각 Change Validation 절에 분산 반영.
6. Phase 2~8 순차 진입, 각 Change closeout 시 R4 정량 기준 확인.
7. Phase 9 진입 전 9a/9b 분리 완료 + `phase9_manual_qa_checklist.md` 사전 작성.
8. Phase 10 진입.

### Out of scope for this review
- 코드 회귀 검증 (각 phase 실행 시점에 수행)
- `docs/EXECUTION_CONTRACT.md` 본문 대조 (별도 검증)
- Pulse / Echo / Fuse / Nerve 영향 분석 (Non-Goals 명시되어 검토 불필요)
- 입력 roadmap 본문 재대조 (roadmap review에서 처리)
- R1 수정안 자체의 코드 적용 검증 (plan 수정 후 별도)

---

## 12. Reviewer Notes

### Spot-checked facts (verified 2026-06-07)
- `Iris/media/lua/client/Iris/IrisMain.lua` 존재 확인 — 유일하게 정확한 경로
- `Iris/media/lua/client/Iris/Logic/IrisDesc/{Generator,Logger,Ordering,Renderer,TagParser,Templates}.lua` 존재 확인 — runtime IrisDesc 실제 위치
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` 존재 확인 — 607 LOC, Change 9b 분리 후보
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` 존재 확인 — 212 LOC, Change 9b 분리 후보
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/` 존재 확인 — 6개 파일 미러링, Pulse compat wrapper 실제 위치
- `Iris/media/lua/shared/` 하위는 `translate/`만 존재 — plan이 명시한 `shared/Pulse/...` 경로는 미존재
- `Iris/build/tools/common/{io.py, stage_runner.py, versions.py}` 존재 확인 — Change 2/6의 "확장 대상" 일치
- `Iris/build/quality_gates.py` = 1542 LOC 확인 — Change 4 분할 정당성
- `Iris/build/{recipe,rightclick}_evidence_pipeline.py` 존재 확인 — Change 5 대상 일치
- `Iris/build/{ENTRYPOINTS,build_import_contract}.md` 존재 확인 — Change 1 readpoint 대상
- `grep "additive amendment\|minimal diff" docs/Philosophy.md docs/DECISIONS.md docs/ROADMAP.md` 결과 매치 없음 — Section 11 인용 출처 미확인

### Uncertainty disclosure
- 본 검토는 `docs/EXECUTION_CONTRACT.md` 본문을 읽지 않음. Section 4 Assumptions의 "direct script execution baseline은 compatibility contract"가 해당 문서에 정의되는지 미확인.
- "approved diff"의 self-approval 기준은 maintainer 운영 방식에 의존 — 본 검토에서 표준 제시 불가.
- `luac -p`의 Kahlua 환경 호환성 미확인 — Phase 9 syntax check 실효성 별도 검증 필요.
- Pulse compat wrapper 6개 파일 외부 require 사용처 매핑 미수행 — Phase 1 inventory에 포함 권장.

### Review limitations
- 본 검토는 governance/structure + 파일 경로 spot check 중심. 코드 실제 회귀 가능성은 phase 실행 시점에 별도 검증.
- Section 14의 6개 conflict 자체의 maintainer 결정 내용은 본 검토 범위 외 — `phase1_conflict_resolution_gate.md` 산출 후 별도 short follow-up review 권장.
- PLAN_TEMPLATE 자체에 Success Criteria 절이 없는 구조적 한계로 인해 R4는 Section 7/12에 분산 반영하는 우회 접근.

### Future follow-up suggestions
- R1~R3 적용 후 본 검토를 짧게 재실행 (re-review)하여 R4·R5 진행률 점검 권장.
- Phase 1 deliverable 산출 후 `phase1_conflict_resolution_gate.md` 자체를 별도 review template으로 검토 권장.
- Change 9b의 manual QA checklist(`phase9_manual_qa_checklist.md`)는 Change 9b 진입 전 별도 review가 필요 — manual QA 정의는 governance 면에서 가장 약한 지점.
- Section 11 인용 거버넌스 일부 미확인 출처(R5)는 본 plan 외 다른 docs/Iris 문서의 동일 패턴이 있는지 점검 권장 (cross-document pollution 가능성).
