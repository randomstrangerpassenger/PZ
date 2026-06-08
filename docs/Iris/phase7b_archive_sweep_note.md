# Phase 7b (Change 7b) — Staging Archive Sweep Note

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 7b, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase6`. cwd: repo root.
> **Closeout State: `complete`** (disposition table 전수 처리; 안전 archive 대상 0건).
> Entry Gate: Phase 1 complete + conflict 14.3 resolved (per-directory disposition, glob 금지) ✓.

## 수행 내용

1. 11개 staging top-level 디렉토리 + 중첩 백업을 per-directory schema로 분류 →
   `docs/Iris/phase7b_per_directory_disposition_table.md`.
2. 물리 archive 시도(오래된 untracked 5개: `body_role`, `semantic_quality`,
   `source_expansion_distribution_remeasurement_gate`, `identity_fallback_source_expansion`,
   `weak_active_cleanup`를 `Iris/_archive/staging/`로 이관).
3. **test baseline이 14 errors로 실패** (`test_build_identity_fallback_*` 등) — 이관된 디렉토리들이
   tracked 테스트의 fixture였음. **즉시 전수 revert → 407 OK 복구.**
4. test-reference 재측정 결과 11개 중 **9개가 테스트 참조**(`interaction_cluster` 39, `source_coverage` 25,
   `body_role`/`semantic_quality` 11, ...). 따라서 **staging은 reproduction/test fixture surface이며 안전
   archive 대상이 없다**고 결론.

## 교훈 (계획 보강 포인트)

- Change 7b `reference_check`는 **active build script만으로 부족**하다 — **테스트 참조까지 포함**해야 안전.
  본 round에서 active-manifest grep만으로 archive를 판단했다가 fixture를 끊어 14 테스트가 깨졌다.
- "오래된 untracked staging = disposable"이라는 직관은 **틀렸다**. 오래된 디렉토리도 현행 테스트 fixture로 쓰인다.

## Validation

| Item | 결과 | PASS |
|---|---|:---:|
| 물리 이관 후 test baseline | 14 errors → **revert** | (감지·복구) |
| revert 후 test baseline | **Ran 407 / OK** | ✅ |
| sealed Layer3 aggregate | `A425…4559` MATCH (sweep 중에도 무변동) | ✅ |
| git tracked 변화 | 없음 (staging untracked; 이관/revert 모두 repo 무영향) | ✅ |
| staging_toplevel_count | 11 유지 (disposition 의도 = 전부 keep/defer와 일치) | ✅ |
| disposition table 전수 | 11 + 중첩 백업 분류 완료 | ✅ |

## §12 Quantitative Closeout (Change 7b)
- [x] disposition table 전수 처리
- [x] `staging_toplevel_count`가 disposition 의도(keep_active 9 + defer 1 + delete_candidate 1, archive 0)와 일치 → 11 유지
- [x] sealed evidence 1건도 archive 외 disposition 없음 (staging에 sealed 없음, archive 0건)
→ **Change 7b = `complete`** (per-directory disposition 결과: staging은 test fixture라 보존; 안전 sweep 대상 없음).
