# Approved Diff Log

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §7 Approved Diff Procedure.
> 누적 로그. `approved diff`는 SHA drift를 명시 승인하기 위한 절차이며, 회피 경로로 쓰지 않는다.
> `reviewer` 제약(v5/v6): `sealed_artifact`/`runtime`/`public_facing`/`compat`는 `reviewer = 사용자`만 허용,
> `self` 금지. `authority` self carve-out은 minimum evidence 3종 필수. `build_only`는 `self` 허용(분류 self-check 필요).

## Entries

### AD-0001 — build_report.json/md live timestamp (Change 4)

| Field | Value |
|---|---|
| `entry_id` | AD-0001 |
| `change` | 4 (Phase 4 — quality_gates.py split) |
| `artifact` | `Iris/output/build_report.json`, `Iris/output/build_report.md` |
| `surface` | `build_only` (DETERMINISM_FILES/sealed/runtime/compat/public_facing/authority 어디에도 속하지 않는 build-only report artifact) |
| `before_sha` | `DD169C6BD5BA8E5A32B1E559E23CA8AA0A3DB09437C5846113F574967A122695` (build_report.json, 분리 전 실행) |
| `after_sha` | run-variant (timestamp-only). 분리 후 실행마다 `timestamp` 필드만 변동. **timestamp 정규화 후 content는 before와 byte-identical(JSON·MD 모두 SAME)** |
| `diff_reason` | `generate_build_report`가 `datetime.now(timezone.utc)`를 `timestamp` 필드로 기록(분리 이전부터 존재). raw SHA가 매 실행 달라지는 것은 split이 만든 drift가 아니라 기존 비결정 필드 때문이다. |
| `schema_or_behavior_impact` | `none` (schema·gate 결과·통계 전부 동일. timestamp 값만 상이) |
| `reviewer` | `self` (`surface = build_only` → self 허용. 본 artifact가 sealed/runtime/compat/public_facing/authority 아님을 self-check 완료) |
| `sign_off_date` | 2026-06-07 |
| `closeout_note_reference` | `docs/Iris/phase4_quality_gates_split_note.md` |

근거: `phase4_quality_gates_split_note.md` Validation 표(Report JSON/MD schema = timestamp 정규화 후 SAME,
raw `git diff --no-index` = timestamp 1줄). build_report는 Q4 `DETERMINISM_FILES` 봉인 대상이 아니다.
