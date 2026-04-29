# Iris DVF 3-3 Profile Migration Spec

기준일: `2026-04-21`

## 목적

이 문서는 `sentence_plan` 기반 legacy 3-profile을 `body_plan` 기반 new 6-profile로 옮기는 Phase C migration contract를 고정한다. compose authority는 `compose_layer3_text.py` 내부 writer 하나가 가진다. preview builder나 adapter는 별도 writer가 아니다.

## Canonical Artifact

- `Iris/build/description/v2/staging/compose_contract_migration/profile_migration_table.json`
- `Iris/build/description/v2/staging/compose_contract_migration/profile_migration_inventory.json`
- `Iris/build/description/v2/staging/compose_contract_migration/manual_rebucket_candidates.json`
- `Iris/build/description/v2/staging/compose_contract_migration/golden_subset_seed.json`
- `Iris/build/description/v2/staging/compose_contract_migration/pilot_corpus_manifest.json`
- `Iris/build/description/v2/staging/compose_contract_migration/legacy_vs_bodyplan_diff_report.json`

## Crosswalk

| legacy profile | default new profile | 상태 |
|---|---|---|
| `interaction_tool` | `tool_body` | active |
| `interaction_component` | `material_body` | active |
| `interaction_output` | `output_body` | reserved_no_current_rows at initial small snapshot, active in full-runtime preview |
| `—` | `container_body` | reserved_new_branch, active in full-runtime preview |
| `—` | `wearable_body` | reserved_new_branch, active in full-runtime preview |
| `—` | `consumable_body` | reserved_new_branch, active in full-runtime preview |

## Resolution Rules

1. `identity_hint`는 `compose_profile_identity_hint_rules.json`의 family target으로 먼저 해석한다.
2. `selected_role`는 `tool -> tool_body`, `material -> material_body`, `output -> output_body`로 해석한다.
3. `identity_family_target`과 `selected_role_target`이 같으면 `identity_role_aligned`다.
4. 둘이 충돌할 때 `identity_family_target`이 precedence eligible target(`consumable_body / wearable_body / container_body`)이면 `identity_family_precedence`를 쓴다.
5. 그 외 충돌은 `selected_role_precedence`로 닫는다.
6. family target만 있으면 `identity_family_target`, role target만 있으면 `selected_role_target`, 둘 다 없으면 legacy fallback target을 쓴다.

## Full-Runtime Snapshot

`dvf_3_3_rendered_v2_preview.full.json` 기준:

| resolved profile | count |
|---|---|
| `tool_body` | `207` |
| `material_body` | `115` |
| `consumable_body` | `128` |
| `wearable_body` | `450` |
| `container_body` | `42` |
| `output_body` | `33` |

resolution source 분포:

| source | count |
|---|---|
| `identity_family_target` | `753` |
| `selected_role_precedence` | `101` |
| `identity_role_aligned` | `55` |
| `identity_family_precedence` | `39` |
| `selected_role_target` | `27` |

## Quality Availability Matrix

`coverage_quality_candidate`는 현재 runtime에서 아래처럼 관측된다.

| profile | strong | adequate | weak |
|---|---:|---:|---:|
| `tool_body` | `207` | `0` | `0` |
| `material_body` | `104` | `0` | `11` |
| `consumable_body` | `0` | `128` | `0` |
| `wearable_body` | `0` | `2` | `448` |
| `container_body` | `42` | `0` | `0` |
| `output_body` | `33` | `0` | `0` |

이 matrix는 중요한 해석 제한을 만든다.

- current runtime은 **모든 profile에서 strong / adequate / weak triad를 제공하지 않는다**.
- 따라서 golden seed는 `per-profile triad`가 아니라 `profile minimum coverage + observed-quality coverage` 기준으로 고정한다.
- 이 제약은 compose writer bug가 아니라 current profile contract와 input distribution의 결과다.

## Golden Seed Read

`golden_subset_seed.json`은 아래를 고정한다.

- profile별 최소 `5`개, 총 `30`개
- overall quality mix: `strong 18 / adequate 7 / weak 5`
- overall body-balance mix: `identity-heavy 12 / use-heavy 3 / acquisition-heavy 4 / mixed-body 11`
- boundary tag mix: `selected_role_precedence`, `identity_family_precedence`, `selected_role_target`, `missing_required_sections`, `quality:adequate`, `quality:weak`

이 seed는 이후 drift 감지 기준이다. 단, per-profile triad unavailable 상태를 무시하고 gate를 과장 해석하지 않는다.
