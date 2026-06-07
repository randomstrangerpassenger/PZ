# Phase 1 (Change 1) — Closeout Note

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 1, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase1`. cwd: repo root.
> **Closeout State: `complete`** (entry gate / first-mover).

Change 1은 코드 변경 없이 inventory·baseline·conflict gate를 측정·봉인하는 진입 게이트다.
runtime Lua / sealed artifact / build code는 일절 수정하지 않았다(doc + 측정만).

## Validation 표 결과 (§6 Change 1)

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Path existence | 모든 항목 `Exists = True` | runtime/wrapper/entrypoint/inventory/sealed 21/21 + sealed 추가 16/16 | ✅ |
| Chunk count | 정수 + baseline 봉인 | Layer3 **11**, UseCase **9** | ✅ |
| Tracked inventory | 정수 + classification 동기 | `git ls-files Iris` = **567**; tracked build `.py` 73 전수 분해 정합 | ✅ |
| Baseline tests | `OK` + 통과 수 = baseline | `Ran 407 tests` / `OK` / `$LASTEXITCODE=0` → `baseline_test_count = 407` | ✅ |
| Conflict gate completeness | 6개 conflict schema field 충족 | 6/6 (8 field 전수). 14.2 `deferred`, 나머지 `resolved` | ✅ |
| Baseline metrics | 13개 metric 모두 정수 | 13/13 측정·봉인 | ✅ |

## Quantitative Closeout Criteria (§12 Change 1) 충족

- [x] conflict gate **6/6** schema field 충족
- [x] baseline metrics **13/13** 측정 완료
- [x] §5 Path Existence Verification 전수 `True`
- [x] chunk enumerate 측정값이 `baseline_layer3_chunk_count`(11)/`baseline_usecase_chunk_count`(9)로 정수 봉인
- [x] `phase1_active_script_manifest.txt` 한 줄 이상 산출 (**38** 줄)

→ 5개 정량 기준 + Validation 표 전수 PASS → **Change 1 = `complete`**.

## Deliverables (7 created + 3 amended + 1 closeout)

Created: `phase1_inventory_readpoint.md`, `phase1_baseline_metrics.md`,
`phase1_active_script_manifest.txt`, `phase1_batch1_import_graph.md`,
`phase1_pulse_wrapper_usage_inventory.md`, `phase1_artifact_source_classification.md`,
`phase1_conflict_resolution_gate.md`. (+ 본 `phase1_closeout_note.md`)

Amended (additive, 2026-06-07 절): `Iris/build/ENTRYPOINTS.md`,
`Iris/build/build_import_contract.md`,
`Iris/build/description/v2/tools/build/INVENTORY.md`.

## 다음 단계 게이트 (사용자 결정 필요)

| Change | 진입 조건 | 현재 상태 |
|---|---|---|
| **Change 3** (Phase 3) | conflict **14.2** resolved/deferred | **사용자 결정 대기** — direct-exec vs `python -m`. deferred 시 path helper까지만 |
| Change 4 (Phase 4) | conflict 14.4 resolved("추가 split 필요") | ✅ 충족 (진입 가능, 실행 승인 필요) |
| Change 7b (Phase 7b) | conflict 14.3 resolved | ✅ 충족 (disposition table 작성 후) |
| Change 9a (Phase 9a) | conflict 14.6 + behavior-neutral | ✅ 충족 |
| Change 9b (Phase 9b) | conflict 14.5 + 14.6 + manual QA checklist + **in-game QA** | ⚠️ manual in-game QA는 사용자만 수행 가능 |
| Change 2/5/6/7a | Phase 1 complete | ✅ 충족 (코드 리팩토링 라운드 — 별도 착수 승인 권장) |

`implemented_only`/`blocked` 없음. Phase 1은 `complete`로 닫힌다.
