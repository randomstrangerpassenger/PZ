# Iris Layer 4 Gate 3 Source Migration Unblock Walkthrough

Date: 2026-08-21

## 1. Scope and starting state

This walkthrough is a follow-up execution record under the existing Layer 4 adaptive interaction presentation plan. It is not a new roadmap or plan. The historical blocked closeout and its planning-time crosswalk remain unchanged.

The initial worktree already contained a user-modified Layer 4 plan, untracked decision packet and blocked closeout, an untracked focused contract test, and an untracked `__pycache__/`. Those pre-existing changes were preserved. The nine reported mismatches were the complete fresh difference set; repository-wide recipe-decision census found exactly one zero-input/nonzero-keep recipe and no other `NO` recipe rule.

## 2. Nine-item investigation and disposition

| Item / relation | Classification and evidence | Owning material | Result |
|---|---|---|---|
| `Base.UnusableMetal / can_scrap_moveables` | Stale/incorrect legacy producer fact. In `addScrapDefinition`, this item occurs in the final `_unusableItem` slot, not either tool slot. QG's `input_material` exclusion agrees with the raw role. | Raw `lua/client/Moveables/ISMoveableDefinitions.lua`; legacy producer `Iris/evidence/rightclick/pipeline.py` | Removed from legacy capability output by correcting role-aware extraction. |
| `Base.UnusableWood / can_scrap_moveables` | Same producer-role error. The raw Wood and Log definitions place it in `_unusableItem`. | Same raw Lua and legacy producer | Removed from legacy capability output. |
| `Base.WeldingMask / can_scrap_moveables` | Same broad-reference extraction error, but a different role: it is required protective clothing in `_tools2`, not the interaction-executing item. ItemScript identifies `Type=Clothing`; QG's `equip` exclusion is consistent. | Raw moveables Lua, `Iris/input/items_itemscript.json`, legacy producer | Removed from legacy capability output; executable tools remain. |
| `Base.BallPeenHammer / uc.action.construction` | Valid QG-only information, not an identifier mismatch. ItemScript `Tags=Hammer` resolves through `rule_tooldef_hammer`; the registry has a local PASS/STRONG override alias to `uc.action.construction`; canonical QG output records `TAG_RESOLVES_TO_TYPE`. The static legacy v1 producer does not expand this newer tag relation. | `Iris/input/items_itemscript.json`, `Iris/input/rightclick_source_index.v2.4.json`, `Iris/output/action_evidence_classification.v2.4.json`, `Iris/build/data/v2.4/use_case_registry.v2.4.json`, canonical QG use-case output | Kept in QG; no legacy backfill and no deletion for count matching. |
| `Base.GardenSaw / uc.action.wood_cutting` | Valid QG-only information. ItemScript `Tags=Saw` resolves through `rule_tooldef_saw`; registry alias/override and canonical QG evidence identify the wood-cutting relation. | Same QG evidence chain, using the saw rule | Kept in QG. |
| `Base.HammerStone / uc.action.construction` | Valid QG-only information. ItemScript `Tags=Hammer` resolves through the same construction rule and registry decision. | Same QG evidence chain, using the hammer rule | Kept in QG. |
| `Base.HandTorch / remove_battery` | QG omission caused by a local decision edge case, not a justified `NO`. Raw `scripts/recipes.txt` declares `recipe Remove Battery`, `keep Torch/HandTorch/Rubberducky2`, `Result:Battery`, and explicit battery-removal callbacks. The recipe index preserves the keep relation, but the producer previously required a matched input to PASS. | Raw recipe, `Iris/output/recipe_index.v2.4.json`, `Iris/build/recipe_evidence_pipeline.py` | QG decision changed from `NO` to `PASS`; linked as `role=keep`. |
| `Base.Rubberducky2 / remove_battery` | Same keep-only producer edge case and raw recipe evidence. | Same recipe/QG producer chain | QG decision changed from `NO` to `PASS`; linked as `role=keep`. |
| `Base.Torch / remove_battery` | Same keep-only producer edge case and raw recipe evidence. | Same recipe/QG producer chain | QG decision changed from `NO` to `PASS`; linked as `role=keep`. |

There was no evidence of a mere display-name mapping error, a need to mix legacy and QG presentation, a wider inclusion-policy defect, or a need to redesign Layer 4 authority/source migration.

## 3. Source corrections and generated results

The legacy scrap producer now parses only the two declared tool slots and rejects clothing from the executing-item set. Its focused regression reads the repository raw source and fixes the expected set at `Base.BlowTorch`, `Base.Hammer`, `Base.Saw`, and `Base.Screwdriver`, while explicitly rejecting the three false facts.

The recipe producer now treats either an explicit input or an explicit keep relation as a positive recipe participation relation. A generic regression enumerates every zero-input/nonzero-keep recipe and requires `PASS` plus `role=keep`; the current census contains exactly one such recipe (`remove_battery`). The normal producer/integrator/nav chain was run, then its owned regression baselines and frozen hashes were updated through the repository's guarded quality-gate workflow.

The Gate 3 validator compares the legacy producer outputs to canonical QG producer output (`Iris/output/usecases_by_fulltype.v2.4.json`). Installed runtime parity remains a separate check; an older installed projection is not used as a substitute for the source-migration authority. Historical `L4-RAT-08 preserve_legacy` dispositions remain visible as history and were not used as evidence or as a gate override.

## 4. Changed files

Owner logic and regression controls:

- `Iris/evidence/rightclick/pipeline.py`
- `Iris/build/recipe_evidence_pipeline.py`
- `Iris/test/test_rightclick_pipeline.py`
- `Iris/build/tests/test_recipe_evidence.py`
- `Iris/build/data/v2.4/expected_diff.json`
- `Iris/build/data/v2.4/frozen_sha.v2.4.json`
- `Iris/build/description/v2/tools/build/validate_interaction_presentation_contract.py`
- `Iris/test/test_interaction_presentation_contract.py`

Regenerated producer outputs and quality reports:

- `Iris/output/capability_by_fulltype.json`
- `Iris/media/lua/client/Iris/Data/IrisCapabilities.lua`
- `Iris/output/recipe_evidence_decisions.v2.4.json`
- `Iris/output/usecases_by_fulltype.v2.4.json`
- `Iris/output/recipe_nav_registry.v2.4.json`
- `Iris/output/build_report.json`
- `Iris/output/build_report.md`
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/contract_report.json`
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/path_selection.json`
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/preseal_no_current_mutation.json`
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/stable_id_plumbing_candidate.json`

Documentation:

- `docs/iris_layer4_gate3_source_migration_unblock_walkthrough.md`
- `docs/새 폴더/iris_layer4_adaptive_interaction_density_presentation_plan.md` (additive follow-up synchronization only)

The old decision packet and blocked closeout are preserved as historical records with an additive ineligibility notice. Their inferred approval and the old ignored owner seal are not consumed by the fresh Gate 3 validator and cannot authorize implementation.

The user's 2026-08-21 follow-up explicitly approves one narrow runtime fact correction: retaining the regenerated `IrisCapabilities.lua` with the three false `can_scrap_moveables` facts removed. This approval does not cover adaptive policy, `L4-RAT-01`–`L4-RAT-07`, publication of the three QG-only facts, or an implementation subject.

## 5. Crosswalk before and after

| Crosswalk | Legacy before | QG before | Mapped before | Legacy/QG only before | Legacy after | QG after | Mapped after | Legacy/QG only after |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Capability | 86 | 86 | 83 | 3 / 3 | 83 | 86 | 83 | 0 / 3 |
| Recipe | 794 | 791 | 791 | 3 / 0 | 794 | 794 | 794 | 0 / 0 |

The only remaining crosswalk differences are the three valid QG-only capability relations listed above. They are not Gate 3 blockers.

## 6. QG-only publication and IPS impact

After the later, separately authorized removal of the legacy presentation fallback, Ball Peen Hammer and Stone Hammer construction plus Garden Saw wood cutting will become newly visible public Layer 4 information. They were deliberately retained because canonical QG evidence supports them. This walkthrough does not perform that public/runtime cutover.

The preserved Item-Page Information Sufficiency result is a retired one-off assessment. Because the canonical QG use-case producer output changed for the three battery-removal relations, that prior snapshot is recorded as `stale` for this changed input scope. No removed evaluator was restored and no additive IPS successor was created.

## 7. Validation log

Intermediate generation and diagnostics:

| Command | Exit code | Result |
|---|---:|---|
| `uv run python -B Iris/evidence/rightclick/pipeline.py --media-root .` (first corrected-parser attempt) | 1 | Fail-loud detection of the function declaration as a call; parser was locally corrected before any successful output claim. |
| `uv run python -B Iris/evidence/rightclick/pipeline.py --media-root .` (rerun) | 0 | 83 legacy capability facts generated. |
| `uv run python -B Iris/evidence/rightclick/generate_lua.py` | 0 | Legacy capability Lua regenerated. |
| `uv run python -B Iris/build/recipe_evidence_pipeline.py` | 0 | 322 PASS, 0 NO, 0 REVIEW recipe rules. |
| `uv run python -B Iris/build/tools/pipeline/build_usecases_by_fulltype.py` | 0 | Canonical use cases regenerated; 794 recipe-ui relations. |
| `uv run python -B Iris/build/tools/pipeline/build_recipe_nav_registry.py` | 0 | 322 eligible recipe rules. |
| `uv run python -B Iris/build/tests/test_recipe_evidence.py` (first run) | 1 | New keep-only assertions passed; downstream Q4/Q5 correctly rejected three stale frozen expectations. |
| `uv run python -B Iris/build/quality_gates.py` (diagnostic run) | 1 | Confirmed the only failures were the three expected producer-output baseline deltas. |
| `uv run python -B Iris/build/quality_gates.py --update-sha` | 0 | Q5 guarded update accepted the evidenced deltas; fresh Q4 re-check PASS. |
| `uv run python -B Iris/build/tests/test_recipe_evidence.py` (rerun) | 0 | All recipe evidence and full quality gates PASS. |
| `uv run python -m pytest -q Iris/test/test_rightclick_pipeline.py` | 0 | 9 passed, 1 skipped (pre-existing absent optional baseline), 1 cache warning. |
| `uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py` (pre-synchronization check) | 0 | 13 passed; used only as an intermediate check, not the final Gate 3 result. |

Final required validation is recorded below after the plan synchronization and fresh Gate 3 run.

| Command | Exit code | Result |
|---|---:|---|
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | 0 | `Lua syntax validation OK: 128 files`. |
| `uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py` | 0 | 13 passed; one non-failing pytest cache permission warning. Fresh report records Gate 3 PASS and unapproved adaptive policy. |
| `uv run python -B Iris/build/quality_gates.py` (final) | 0 | Q1–Q5 all PASS; Q4 mismatches 0 and Q5 unexpected changes 0. |
| `git diff --check` | 0 | No whitespace error; Git emitted only line-ending conversion warnings. |
| `uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py` (detached clean committed worktree) | 0 | 13 passed; proves the tracked validator/test/data subject reproduces without the original working tree or old owner seal. |

## 8. Final Gate 3 decision

**PASS.** The final fresh contract report has `execution_status=PASS`, `capability_only=0`, `recipe_only=0`, and `qg_only=3`; `contract_errors` is empty. Capability counts are legacy/QG/mapped `83/86/83`. Recipe counts are legacy/QG/mapped `794/794/794`, with `qg_recipe_only=0`.

The fresh validator does not load or hash the old owner seal. It reports `owner_policy_seal_status=unapproved_new_seal_required`, `L4-RAT-08=not_applicable_no_recipe_only`, and blocks Change 2+ as `blocked_pending_owner_policy_seal`. A later implementation requires explicit approval of `L4-RAT-01`–`L4-RAT-07`, publication of the three QG-only facts, and the exact implementation subject, followed by a new decision packet/seal. The specific Gate 3 source-migration blocker is removed; adaptive implementation remains unapproved.

## 9. Non-claim boundary

This work corrected source facts, QG recipe evidence, generated evidence products, regression controls, and the Gate 3 crosswalk. It did **not** implement adaptive UI, dense/small presentation behavior, fallback cutover, runtime interaction rendering, a mixed legacy/QG display, or any later Layer 4 implementation change. A Gate 3 PASS only means the existing Layer 4 plan may resume at its next applicable gate.
