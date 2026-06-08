# Phase 7b — Per-Directory Disposition Table

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 7b Per-Directory Disposition Schema.
> 측정일: 2026-06-07. Entry Gate: Phase 1 complete + conflict 14.3 resolved (per-directory disposition, glob 금지).
> `baseline_staging_toplevel_count = 11`.

## 핵심 결론: staging 디렉토리는 test fixture라 archive 불가

`Iris/build/description/v2/staging`의 11개 top-level 중 **9개가 tracked 테스트에 참조**된다(아래 `test_refs`).
초기에 "오래된 untracked = archive 가능"으로 5개를 `_archive`로 이관했더니 **`test_build_identity_fallback_*`
등 14개 테스트가 import/실행 단계에서 깨졌고**, 즉시 전수 revert → **407 OK 복구**했다. 즉 staging은
reproduction/test fixture surface이며, **물리 archive sweep의 안전 대상은 사실상 없다**.

reference_check는 active manifest(38)만으로 부족하고 **테스트 참조까지 포함**해야 한다(본 round의 교훈).

## Disposition (11 + 중첩 백업)

`test_refs` = `Iris/build/description/v2/tests` + `Iris/build/tests`의 `test_*.py`가 디렉토리 이름을 참조한 수.

| path (staging/) | disposition | evidence_type | tracked | total | last | test_refs | 사유 |
|---|---|---|---:|---:|---|---:|---|
| `interaction_cluster` | keep_active | reproduction_evidence | 0 | 71 | 06-08 | 39 | 테스트 다수 참조 |
| `source_coverage` | keep_active | reproduction_evidence | 0 | 357 | 06-08 | 25 | 테스트 다수 참조 |
| `body_role` | keep_active | reproduction_evidence | 0 | 1 | 04-05 | 11 | 테스트 참조 |
| `semantic_quality` | keep_active | reproduction_evidence | 0 | 2 | 04-30 | 11 | 테스트 참조 |
| `weak_active_cleanup` | keep_active | reproduction_evidence | 0 | 33 | 05-16 | 7 | 테스트 참조 |
| `source_expansion_distribution_remeasurement_gate` | keep_active | reproduction_evidence | 0 | 32 | 04-30 | 4 | 테스트 참조 |
| `compose_contract_migration` | keep_active | reproduction_evidence (tracked) | 139 | 186 | 06-08 | 2 | tracked + layer4 테스트 |
| `manual_in_game_validation` | keep_active | reproduction_evidence (tracked, 수동 QA) | 35 | 35 | 06-06 | 2 | tracked 수동 QA 증거 |
| `identity_fallback_source_expansion` | keep_active | reproduction_evidence | 0 | 42 | 04-30 | 1 | 테스트 참조 (이관 시 14 테스트 깨짐) |
| `acquisition_lexical_current_readpoint_reconciliation_round` | defer | reproduction_evidence | 0 | 23 | 06-05 | 0 | test-ref 0이나 "current_readpoint"+recent(06-05) → active 가능성, 보류 |
| `second_pass_backlog_132` | delete_candidate | disposable_artifact | 0 | 0 (empty) | — | 0 | 빈 디렉토리(입력 제거됨). **삭제 보류**(계획 규칙) |
| `_archive/p0-2/Iris/Iris/...` (중첩 백업) | defer | staging_intermediate | — | — | — | — | 이동 결정은 본 phase 외부 |

`package_mirror_check`: 전 항목 미러 없음. `decision_owner`: 사용자. `target_destination`/`rollback_path`: archive 0건이므로 전부 `N/A`.

## 규칙 적용 / closeout

- **archive 0건**: 안전하게 archive 가능한 디렉토리 없음(9개 test fixture, 1개 recent defer, 1개 empty delete_candidate-deferred).
- **sealed_evidence 0건**: staging에 sealed runtime artifact 없음 → "sealed는 archive 외 금지" 위반 없음.
- **delete_candidate 미삭제**: `second_pass_backlog_132`(empty)는 본 Change에서 삭제하지 않음(deferral).
- **staging_toplevel_count = 11 유지**: disposition 의도(전부 keep/defer)와 일치 — 감소 없음이 올바른 결과.
- 물리 이관 시도→revert 기록: `phase7b_archive_sweep_note.md`.
