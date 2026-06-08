# Phase 3 (Change 3) — ROOT / sys.path Bootstrap Cleanup Batch

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) §6 Change 3.
> 실행일: 2026-06-07. 동반 문서: `phase3_compose_import_contract_note.md`.

Change 3의 bootstrap 정리 batch 기록. 본 round는 **active compose core 한정**으로 부트스트랩을
줄였고, frozen reproduction 스크립트(269개)의 부트스트랩은 incremental migration으로 남긴다
(계획 §12: "ROOT/sys.path count는 baseline 대비 감소", 전수 0 아님).

## 측정 (baseline → after)

| Metric | baseline | after | Δ | 방법 |
|---|---:|---:|---:|---|
| `compose_except_import_count` | 5 | **0** | -5 | compose `try/except ImportError` 전수 제거 |
| `baseline_syspath_insert_count` | 134 | **132** | -2 | item/render의 `sys.path.insert(parent.parent)` 제거 (style import 절대화) |
| `baseline_root_bootstrap_count` | 254 | **253** | -1 | `compose_layer3_text` inline `ROOT = ...parents[2]` → `from tools.common.paths import V2_ROOT as ROOT` |

측정 명령은 `phase1_baseline_metrics.md` 참조 (`$dvPy | Select-String ...`).

## 변경된 파일 (active compose core)

| 파일 | sys.path.insert | ROOT inline | except ImportError |
|---|:--:|:--:|:--:|
| `compose_layer3_text.py` | — | 제거(→paths.V2_ROOT) | 제거 |
| `compose_layer3_identity.py` | — | — | 제거 |
| `compose_layer3_body_profile.py` | — | — | 제거 |
| `compose_layer3_item.py` | 제거 | — | 제거 |
| `compose_layer3_render.py` | 제거 | — | 제거 |

신규 leaf helper: `Iris/build/description/v2/tools/common/paths.py` (`V2_ROOT`/`BUILD_ROOT`/dirs).

## 미적용 (incremental, 후속)

- frozen reproduction 스크립트(269개, gitignored)의 `ROOT = ...` / `sys.path.insert` 부트스트랩은
  유지. 이들은 입력 부재로 실행 불가(동결)하며, 대량 전환은 검증 불가 + minimal diff 위반이므로 보류.
- root build 트리(`Iris/build/tools`)의 스크립트 부트스트랩도 본 round 범위 밖(별도 후속).
- 향후 migration 시 동일 leaf-helper 패턴(`from tools.common.paths import ...`)을 따른다.

## Rollback

- 본 Change는 단일 commit. compose import/bootstrap 복원은 commit revert로 단번에 가능.
- sealed Layer3 artifact는 무변동(SHA `A425…4559` MATCH) — rollback 시에도 sealed 영향 없음.
