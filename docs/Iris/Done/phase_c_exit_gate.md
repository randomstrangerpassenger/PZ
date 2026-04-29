# Iris DVF 3-3 Compose Authority Migration Phase C Exit Gate

기준일: `2026-04-21`

## 상태 요약

Phase C는 `body_plan` writer wiring, preview/full-runtime verification, determinism, diff review, adversarial wording reconciliation까지 도달했다. `golden subset triad wording`은 current runtime 분포와 충돌하므로, `phase_c_adversarial_review.md` 기준으로 `profile minimum coverage + observed-quality coverage + explicit unavailable cells` 해석을 채택한다.

## Satisfied

| 항목 | 현재 상태 | 근거 |
|---|---|---|
| compose writer authority | pass | `Iris/build/description/v2/tools/build/compose_layer3_text.py`가 `compose_profiles_v2` 입력에서 `body_plan`을 직접 조립한다. |
| preview authority single-writer | pass | `build_layer3_body_plan_v2_preview.py`는 별도 writer가 아니라 `build_rendered()` wrapper다. |
| pilot corpus | pass | `pilot_corpus_manifest.json`: `48` rows, profile minimum `5` 충족 |
| determinism | pass | `compose_determinism_report.json`: sample/full-runtime 2회 모두 `entries_sha256` identical |
| legacy diff accidental change | pass | `legacy_vs_bodyplan_diff_report.json`: `accidental_change_count = 0` |
| unexpected blocker inventory | pass | `dvf_3_3_body_plan_v2_blockers.summary.full.json`: `blocker_count = 0` |
| full-runtime preview regeneration | pass | `dvf_3_3_rendered_v2_preview.full.json`: `975` active composed / `75` silent |

## Constrained

| 항목 | 현재 상태 | 설명 |
|---|---|---|
| golden subset seed freeze | pass with constraint | `golden_subset_seed.json`: `30` rows, profile별 `5`개, overall strong/adequate/weak mix 포함 |
| per-profile strong/adequate/weak triad | not satisfiable on current runtime | `tool_body`, `container_body`, `output_body`는 strong-only, `consumable_body`는 adequate-only, `wearable_body`는 adequate/weak only, `material_body`는 strong/weak only |

현재 runtime에서 관측된 profile-quality matrix:

| profile | available quality |
|---|---|
| `tool_body` | `strong` only |
| `material_body` | `strong`, `weak` |
| `consumable_body` | `adequate` only |
| `wearable_body` | `adequate`, `weak` |
| `container_body` | `strong` only |
| `output_body` | `strong` only |

따라서 golden seed gate는 현재 이렇게 읽는다.

- `profile minimum coverage`는 충족한다.
- `overall quality mix`는 충족한다.
- `per-profile triad`는 current runtime input/profile distribution상 충족 불가능하다.
- 이 항목은 seed artifact에 `observed-quality coverage`와 `unavailable_profile_quality_cells`로 명시해 두었다.

## Closed Reconciliation

| 항목 | 현재 상태 | 설명 |
|---|---|---|
| exit gate wording reconciliation | closed | `phase_c_adversarial_review.md`가 `strong / adequate / weak 각각 포함`을 current runtime의 overall observed-quality mix로 확정했다. |
| final adversarial sign-off | pass with documented constraint | migration table / compose v2 spec / exit memo review는 synthetic quality row를 만들지 않는 조건으로 pass 처리했다. |

## Current Gate Read

현재 시점의 gate read는 아래다.

1. `sentence_plan -> body_plan` writer authority 교체는 runtime code 기준으로 실제 반영되었다.
2. preview/full-runtime verification, determinism, diff, blocker inventory는 현재 green이다.
3. golden seed는 artifact로 고정되었고, `per-profile quality triad`는 current runtime distribution상 unavailable cell로 기록한다.
4. 따라서 Phase C는 **implementation complete / verification green / adversarial review pass with documented wording reconciliation** 상태로 읽는다.
5. Phase D structural redesign, Phase E-0 regression gate, Phase E runtime Lua rollout은 이 gate에 포함하지 않는다.
