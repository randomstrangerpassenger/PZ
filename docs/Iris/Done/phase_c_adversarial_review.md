# Iris DVF 3-3 Compose Authority Migration Phase C Adversarial Review

기준일: `2026-04-21`

## Review Target

- `docs/Iris/profile_migration_spec.md`
- `docs/Iris/phase_c_exit_gate.md`
- `docs/Iris/Done/dvf_3_3_compose_v2_spec.md`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/staging/compose_contract_migration/profile_migration_table.json`
- `Iris/build/description/v2/staging/compose_contract_migration/golden_subset_seed.json`
- `Iris/build/description/v2/staging/compose_contract_migration/compose_determinism_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/legacy_vs_bodyplan_diff_report.json`

## Adversarial Questions

| 질문 | 판정 | 근거 |
|---|---|---|
| `body_plan` writer가 `compose_layer3_text.py` 내부 single writer인가 | pass | preview builder는 `build_rendered()` wrapper이고, validator/runtime가 문장을 고치지 않는다. |
| compatibility adapter가 외부 preprocessor로 승격됐는가 | pass | adapter behavior는 compose-internal v2 path 안에 있으며 external rewrite path가 없다. |
| new 6-profile resolution이 decisions overlay와 충돌하는가 | pass | `identity_hint` family target, `selected_role` target, precedence rule은 compose-internal resolution trace로 남고 overlay를 변경하지 않는다. |
| `container_body / wearable_body / consumable_body` branch가 legacy 3-profile을 재오픈하는가 | pass | branch는 new profile target이며 legacy profile은 fallback baseline으로만 남는다. |
| structural signal을 Phase C blocker로 끌어왔는가 | pass | `missing_required_sections`와 structural-like signal은 observer/quality evidence로 기록되며 Phase D redesign으로 넘긴다. |
| golden seed가 runtime에 없는 synthetic quality case를 만들어 gate를 맞췄는가 | pass | seed는 full-runtime preview에서만 뽑았고 synthetic row를 만들지 않았다. |
| legacy diff에서 accidental change가 남았는가 | pass | `legacy_vs_bodyplan_diff_report.json`의 `accidental_change_count = 0`. |

## Golden Seed Wording Reconciliation

원문 gate의 `strong / adequate / weak 각각 포함`은 아래처럼 해석한다.

- `profile별 최소 5개`는 per-profile requirement다.
- `strong / adequate / weak 각각 포함`은 current runtime에서 관측 가능한 overall quality mix requirement다.
- per-profile triad는 current runtime distribution상 만족 불가능하므로 exit blocker로 승격하지 않는다.

이 해석이 필요한 이유:

- `tool_body`, `container_body`, `output_body`는 current runtime에서 strong-only다.
- `consumable_body`는 current runtime에서 adequate-only다.
- `wearable_body`는 current runtime에서 adequate/weak only다.
- `material_body`는 current runtime에서 strong/weak only다.
- synthetic row를 만들어 per-profile triad를 맞추는 것은 Phase C의 runtime authority validation이 아니라 fixture invention이 된다.

따라서 Phase C의 golden seed gate는 `profile minimum coverage + observed-quality coverage + explicit unavailable cells`로 닫는다.

## Verdict

Phase C adversarial review는 **pass with documented wording reconciliation**으로 판정한다.

남기는 조건:

- per-profile quality triad를 future gate로 요구하려면 Phase D/E 이후 실제 runtime row나 profile rule이 해당 quality state를 노출해야 한다.
- Phase C closeout은 current observed distribution을 조작하지 않고, unavailable cells를 artifact에 남기는 방식으로 닫는다.
- Phase D structural redesign, Phase E-0 regression gate, Phase E runtime Lua rollout은 이번 verdict에 포함하지 않는다.
