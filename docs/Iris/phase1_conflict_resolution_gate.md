# Phase 1 — Conflict Resolution Gate

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 1 Conflict Resolution Gate Schema, §12 Closeout.
> 상위 roadmap: `docs/Iris/Iris_Refactoring_Roadmap.md` §14.1~§14.6.
> 측정일: 2026-06-07 (repo root cwd).
> 게이트 규칙: 6개 conflict 각각이 schema field 8종을 **전수** 충족해야 Phase 1을 `complete`로 닫을 수 있다.
> `status`는 `resolved`/`blocked`/`deferred` 중 하나이며, `deferred`/`blocked`도 모든 field가 채워지면 closeout schema는 충족한다(단, 해당 downstream Change는 진입 제한).

## 상태 요약

| conflict | status | decision_owner | downstream blocking | 한 줄 |
|---|---|---|---|---|
| 14.1 script count | **resolved** | 사용자(측정 기반) | Phase 1 baseline | A/B는 동일 디렉토리 다른 시점값. canonical = 281 |
| 14.2 direct exec vs package entry | **resolved** (2026-06-07) | 사용자 | Phase 3 | **package form 채택** — `python -m`/패키지 import 표준화 (roadmap A) |
| 14.3 archive/delete 정책 | **resolved** | 사용자(plan/roadmap) | Phase 7b | per-file/per-directory disposition only, glob 금지 |
| 14.4 quality_gates split 상태 | **resolved** | 사용자(측정 기반) | Phase 4 | 1324 LOC 단일 파일 → 추가 split 필요 |
| 14.5 compatibility surface | **resolved** | 사용자(governing docs) | Phase 9b | Pulse wrapper + IrisAPI + direct-exec = compat surface |
| 14.6 runtime cleanup 범위 | **resolved** | 사용자(plan) | 9a/9b split | 두 축 모두, 위험도별 9a/9b 분리 |

**6/6 전부 resolved** (2026-06-07: 14.2가 사용자 결정 "package form"으로 deferred → resolved 갱신). 14.1·14.3·14.4·14.5·14.6은 기존 plan/roadmap/governing docs가 이미 확정한 사항을 측정으로 재확인했고, 14.2는 사용자가 직접 판정했다.

---

## 14.1 Build script count

- **conflict_id**: 14.1
- **status**: `resolved`
- **decision**: roadmap A(282)/B(269)는 서로 다른 측정값이 아니라 **동일 디렉토리(`Iris/build/description/v2/tools/build/*.py`)를 다른 시점에 잰 값**이다. B의 269는 2026-05-04 `INVENTORY.md` "Python scripts in this directory" 값과 일치하고, A의 282는 그 직후 시점의 근사값이다(약 한 달간 round 누적으로 스크립트 증가). 2026-06-07 canonical 재측정값(동일 glob/필터: `-Filter *.py -Recurse -File | Where FullName -notmatch '__pycache__'`)은 **281**로 봉인한다.
- **decision_owner**: 사용자 (측정 기반 — `baseline_build_script_count`)
- **minimum_evidence**: `docs/Iris/phase1_baseline_metrics.md` metric #1 (=281); `Iris/build/description/v2/tools/build/INVENTORY.md` 2026-05-04 값(269); `phase1_active_script_manifest.txt`(active 38 분리).
- **downstream_blocking_phase**: Phase 1 baseline metric blocker (Phase 1 자체).
- **allowed_next_action**: `baseline_build_script_count = 281`을 분모로 Phase 2/7a 측정 진행.
- **blocked_next_action**: (없음 — resolved)

## 14.2 Direct script execution vs package entrypoint

- **conflict_id**: 14.2
- **status**: `resolved` (2026-06-07 update: `deferred` → `resolved`, 계획 §10 gate amendment)
- **decision**: **package form 채택** (roadmap A 방향). import 계약을 `python -m` 패키지 실행 + 패키지 import(`from tools...`)로 표준화한다. 이에 따라 direct script execution baseline은 더 이상 불변 계약이 아니며, Change 3에서 compose `try/except ImportError` dance 제거 + `ROOT`/`sys.path.insert` bootstrap 정리가 허용된다. Change 2의 helper 추출도 dual-compat shim 없이 패키지 import로 직접 진행한다. **불변 조건: 실행/import 방식 변경이 산출물 바이트(SHA)를 바꾸지 않을 것**(determinism gate — family smoke + Artifact SHA로 입증). 이는 기존 `build_import_contract.md`의 "direct script execution remains the compatibility baseline" 및 "Requiring every ... script to support `python -m`"(Not supported yet) 입장의 **명시적 반전**이며, 계약 문서는 Change 3에서 갱신한다.
- **decision_owner**: 사용자 (2026-06-07 결정: "패키지 형태로 가자")
- **minimum_evidence**: 사용자 결정(2026-06-07); `phase1_baseline_metrics.md` `baseline_syspath_insert_count = 134`, `baseline_root_bootstrap_count = 254`, `baseline_compose_except_import_count = 5`; `build_import_contract.md` "Common helper import rule"(이미 `from tools.common.io import`를 패키지 import로 규정 — package form과 정합).
- **downstream_blocking_phase**: Phase 3 (Change 3) — 이제 full compose/bootstrap 정리로 진입 가능.
- **allowed_next_action**: Change 2 = batch1 공통 helper를 `tools/common`으로 (패키지 import 기준) 추출 + 20 caller repoint → `batch1_import_count == 0`. Change 3 = `__init__.py`/패키지 마커 + `tools/common/paths.py` leaf helper + compose dance 제거 + bootstrap 정리, `python -m` 실행 계약으로 `build_import_contract.md`/`ENTRYPOINTS.md` 갱신.
- **blocked_next_action**: 산출물 SHA drift를 동반하는 import 전환(approved diff 없이 금지). **적용 범위(active 한정 vs 269 reproduction 전수)** 는 Change 2/3 진입 시 확정 — 권장: active pipeline(38) + batch1 caller 우선 전환, reproduction 전수 bootstrap 제거는 별도 sub-round로 분리(대량 SHA 위험·minimal diff).

## 14.3 Archive/delete 정책

- **conflict_id**: 14.3
- **status**: `resolved`
- **decision**: archive/delete는 **per-file/per-directory disposition 기반으로만** 수행하고 filename-glob sweep 및 staging evidence 대량 삭제는 금지(roadmap B 채택). 본 계획 §2 Scope/§3 Non-Goals가 이미 이를 확정했고, `INVENTORY.md`도 "no file ... archive/delete eligible by filename glob"을 명시한다. top-level staging 축소 목표(roadmap A)는 blanket 적용이 아니라 Phase 7b per-directory disposition table이 정한 범위 내에서만 반영한다.
- **decision_owner**: 사용자 (계획 §2/§3 + roadmap B)
- **minimum_evidence**: 계획 §2 "staging evidence 대량 삭제 또는 archive-by-glob 정리"(Out of Scope), §3 Non-Goals; roadmap §14.3 B; `Iris/build/description/v2/tools/build/INVENTORY.md` "Classification Decision"; `baseline_staging_toplevel_count = 11`.
- **downstream_blocking_phase**: Phase 7b (Change 7b) entry blocker.
- **allowed_next_action**: Change 7b는 `phase7b_per_directory_disposition_table.md`(Disposition Schema)를 작성해 per-directory `git mv` 이관만 수행.
- **blocked_next_action**: glob 기반 archive sweep, sealed evidence를 archive 외 disposition으로 이동, staging 대량 삭제.

## 14.4 `quality_gates.py` split 상태

- **conflict_id**: 14.4
- **status**: `resolved`
- **decision**: 현재 readpoint에서 split은 **미완료**이며 **추가 split 필요**(roadmap B 확인). `Iris/build/quality_gates.py`는 **1324 LOC 단일 파일**로 `gate_q1`~`gate_q5`(+ 다수 `q5_*` helper) + `generate_build_report`/`generate_build_report_md`(reporting) + `update_frozen_sha` + `main`이 전부 인라인이고, `Iris/build/quality/` 패키지는 존재하지 않는다. 따라서 Change 4(gate별 module + reporting/CLI 분리)는 진입 정당.
- **decision_owner**: 사용자 (측정 기반)
- **minimum_evidence**: `quality_gates.py` LOC = 1324; def surface(`gate_q1/q2/q3/q4/q5`, `generate_build_report`, `generate_build_report_md`, `update_frozen_sha`, `main`); `Test-Path Iris\build\quality` = False.
- **downstream_blocking_phase**: Phase 4 (Change 4) entry blocker.
- **allowed_next_action**: Change 4 진입 — `quality/q1_pass_integrity.py`~`q5_regression_diff.py` + `reporting.py` 분리, `quality_gates.py`는 얇은 CLI shim으로 축소(기존 CLI surface/`--update-sha` semantics 유지).
- **blocked_next_action**: split 중 report JSON/Markdown schema drift(§6 Change 4 `git diff --no-index` 빈 diff 위반) 발생 시 진행 금지.

## 14.5 Compatibility surface

- **conflict_id**: 14.5
- **status**: `resolved`
- **decision**: compatibility surface는 **None이 아니라**(roadmap A 기각) **Pulse namespace compatibility wrapper 6개 + public `IrisAPI` + direct script execution contract + compose module entrypoint**으로 확정(roadmap B). 이는 governing docs가 이미 명시한 사실의 재확인이다. Pulse wrapper 6개는 thin 리다이렉트 shim(`return require("Iris/Logic/IrisDesc/<M>")`)이며 내부 명시적 require 0건, sealed protected-surface 해시에 포함. 제거/변경은 deprecation/release decision 없이는 금지.
- **decision_owner**: 사용자 (governing docs: ARCHITECTURE.md/ROADMAP.md)
- **minimum_evidence**: `docs/ARCHITECTURE.md:348`("`Pulse/Iris/Logic/IrisDesc/*`는 compatibility wrapper"), `docs/ROADMAP.md:494`; `docs/Iris/phase1_pulse_wrapper_usage_inventory.md`(6/6 tracked, 내부 require 0); `docs/Iris/Done/iris-dvf-3-3-...protected-surface-hashes.{before,after}.json`(보호 해시 등재); 계획 §8 Compatibility Surface.
- **downstream_blocking_phase**: Phase 9b (Change 9b) entry blocker.
- **allowed_next_action**: Change 9b는 `phase9b_compat_wrapper_disposition_note.md`에 disposition note만 작성(제거 아님).
- **blocked_next_action**: Pulse wrapper 6개 또는 public `IrisAPI` 제거/변경(deprecation decision 전). Change 9b에서 6개 wrapper의 `git status --short`/`git diff --name-only HEAD` 비-빈 출력 발생 시 scope 위반.

## 14.6 Runtime cleanup 범위

- **conflict_id**: 14.6
- **status**: `resolved`
- **decision**: 두 runtime cleanup 축을 **모두 실행하되 위험도로 분리**한다(plan 채택). 축1(Generator/Renderer debug noise 축소) = behavior-neutral → **Phase 9a**, manual QA 면제. 축2(IrisMain INIT_MODULES helper 흡수 + IrisWikiSections/IrisBrowserInteractionRenderer 책임 분할 + Pulse compat wrapper disposition) = 표시 경로 영향 가능 → **Phase 9b**, manual in-game QA 필수. (v3.0에서 IrisMain helper 흡수는 9a→9b로 재배치됨.)
- **decision_owner**: 사용자 (계획 §6 Change 9a/9b)
- **minimum_evidence**: 계획 §6 Change 9a(축소 범위·manual QA 면제), Change 9b(IrisMain+UI split·manual QA 필수); `baseline_generator_debug_count = 28`, `baseline_renderer_debug_count = 15`; roadmap §14.6 A/B 두 축.
- **downstream_blocking_phase**: Phase 9a/9b split 결정 blocker.
- **allowed_next_action**: Change 9a(behavior-neutral)와 Change 9b(manual QA)를 각각 별도 entry gate로 진입. 9a는 conflict 14.6 + behavior-neutral 한정, 9b는 추가로 14.5 resolved + `phase9b_manual_qa_checklist.md`(baseline screenshot 포함) 필요.
- **blocked_next_action**: 9a에서 IrisMain/IrisWikiSections/IrisBrowserInteractionRenderer 변경(9b 전용). 9b를 manual QA 없이 behavior-preserving으로 closeout.

---

## Closeout 판정

- schema field 충족: **6/6 conflict 전수 8 field 충족** → Phase 1 conflict gate completeness PASS.
- 2026-06-07 update: 14.2가 사용자 결정으로 `resolved`(package form) 갱신 → **6/6 resolved**. Phase 3 full 진입 가능.
- 잘못 닫혔다고 판단되는 conflict는 해당 downstream Change 진입 **전에** 본 문서만 amendment하면 되며 코드 rollback 불필요(계획 §10).
