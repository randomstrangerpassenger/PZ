# Iris DVF 3-3 Compose Authority Migration Round Closeout

기준일: `2026-04-21`

## Verdict

`Iris DVF 3-3 compose authority migration round`는 `A + B + C` scope 기준으로 close한다.

이 closeout은 본문 품질 일반 개선 round가 아니라, `sentence_plan` runtime authority를 `body_plan` compose authority로 상위 교체한 결과를 고정한다. Phase D structural redesign, Phase E-0 full-runtime regression gate, Phase E runtime Lua consumer rollout은 이 closeout에 포함하지 않는다.

## Completion Criteria Read

| # | 기준 | 판정 | 근거 |
|---|---|---|---|
| 1 | top docs가 authority migration round로 일관되게 설명 | pass | `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 2026-04-21 closeout read 반영 |
| 2 | A/B closeout 이후 facts / overlay / validator / writer / runtime 경계 고정 | pass | `dvf_3_3_cross_layer_overlay_spec.md` appendix가 validator scope를 닫고, writer/runtime 경계는 `ARCHITECTURE.md`에 반영 |
| 3 | A closeout 이후 네 접점 Phase C 작동 방식 문서화 | pass | structural signal observer-only, legacy `quality_flag` frozen, post-compose flat-string compatible, adapter non-writer bridge |
| 4 | legacy 3 -> new 6 crosswalk artifact 고정 | pass | `profile_migration_table.json`, `profile_migration_inventory.json`, `manual_rebucket_candidates.json`, `profile_migration_spec.md` |
| 5 | adapter 경유 row 포함 모든 row가 body_plan section emission 규칙으로 조립 | pass | `compose_layer3_text.py`의 `compose_profiles_v2` path가 `body_plan` writer authority |
| 6 | pilot corpus 40~60개 통과 | pass | `pilot_corpus_manifest.json`: `48` rows |
| 7 | 신규 profile별 대표 아이템 최소 5개 확보 | pass with constraint | `golden_subset_seed.json`: profile별 `5`개, overall `strong 18 / adequate 7 / weak 5`; per-profile triad unavailable cells documented |
| 8 | 동일 입력 2회 compose 시 동일 section order / output 보장 | pass | `compose_determinism_report.json`: sample/full-runtime `entries_sha256` identical |
| 9 | legacy diff accidental change가 허용 범위 밖으로 남지 않음 | pass | `legacy_vs_bodyplan_diff_report.json`: `accidental_change_count = 0`, `blocker_count = 0` |
| 10 | structural violation / audit redesign은 이번 종료 조건에서 제외 | pass | `phase_c_exit_gate.md`, `phase_c_adversarial_review.md`, ROADMAP Hold에 명시 |

## Gate Evidence

- `pilot_corpus_manifest.json`: selected `48`, profile coverage `output 10 / tool 5 / material 6 / consumable 11 / wearable 11 / container 5`.
- `golden_subset_seed.json`: selected `30`, profile별 `5`, observed-quality mix `strong 18 / adequate 7 / weak 5`.
- `compose_determinism_report.json`: `overall_pass = true`, sample hash `f081cf7323f694de6e5b967bbcba263e6f6d09f16bf6ac5d193e08bd6b34f7b4`, full-runtime hash `ac6b56ce3c8289b6514c59eb264e0ff85299a267c1b484fe5b818ff6bc2d1218`.
- `legacy_vs_bodyplan_diff_report.json`: `expected_delta 975 / no_delta 75`, `unexpected_reason_counts {}`, `accidental_change_count 0`.

## Boundary Held

- `sentence_plan`은 legacy v1 baseline과 compatibility input으로만 남는다.
- compatibility adapter는 compose-internal non-writer bridge이며, row count threshold gate가 아니다.
- validator는 drift / legality checker이며 rendered 문장을 수정하지 않는다.
- runtime consumer, Lua bridge, Browser/Wiki는 staged flat string authority만 소비한다.
- Phase D/E-0/E는 explicit next-round opening 없이는 시작하지 않는다.
