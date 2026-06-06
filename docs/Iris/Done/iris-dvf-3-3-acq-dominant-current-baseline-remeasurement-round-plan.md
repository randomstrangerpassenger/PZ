# Iris DVF 3-3 ACQ_DOMINANT Current Baseline Remeasurement Round Plan

> 상태: Draft v0.2-review-applied
> 기준일: 2026-05-30
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - ACQ_DOMINANT Current Baseline Remeasurement Round` (2026-05-30 user-provided synthesis)
> review input: `REVIEW - ACQ_DOMINANT Current Baseline Remeasurement Round Plan` (2026-05-30 user-provided synthesis), Critical 1 and Important 3 revisions incorporated in v0.2.
> 직접 상위 readpoint:
> - 2026-05-28 Branch B reconstructed structural observer authority
> - 2026-05-29 Structural Signal Scope Split Seal Round `closed_with_structural_signal_scope_split_sealed_observer_only`
> - 2026-05-29 Structural Signal Authority Classification Round `closed_with_structural_signal_authority_classification_sealed`
> - 2026-05-29 Structural Signal Current Readpoint Seal Round `closed_with_structural_signal_current_readpoint_doc_absorption_only`
> - 2026-05-29 ACQ_DOMINANT Current Baseline Remeasurement deferred measurement debt mapping
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> contract vocabulary: `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`. The template is an execution-plan form only and does not create semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. This document opens no source mutation, rendered text mutation, runtime Lua mutation, packaged Lua mutation, `quality_state`, `publish_state`, `runtime_state`, publish mutation review, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 current artifact 기준으로 남아 있는 `ACQ_DOMINANT` residual occurrence를 재측정하고, surface distribution과 occurrence별 authority class를 봉인한 뒤 `publish_candidate_count`를 산출하는 것이다.

이 round는 `ACQ_DOMINANT`를 수정하는 round가 아니다. 이 round가 답해야 하는 질문은 다음으로 제한한다.

```text
current artifact 기준 ACQ_DOMINANT residual은 몇 개이고,
어느 surface에 남아 있으며,
각 occurrence는 어떤 authority class에 속하고,
publish writer input 또는 forbidden writer reach 후보가 존재하는가?
```

Round id:

```text
acq_dominant_current_baseline_remeasurement_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/acq_dominant_current_baseline_remeasurement_round/
```

Expected success closeout branches:

```text
closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate
closed_with_acq_dominant_current_baseline_and_publish_candidates_found
```

Blocked closeout branches:

```text
blocked_with_current_artifact_baseline_unstable
blocked_with_unclassified_acq_dominant_occurrences
blocked_with_family_consistency_conflict
blocked_with_non_mutation_invariant_failed
blocked_with_validation_failed
blocked_with_claim_overreach
```

Closeout records must separate contract state from branch label:

```text
contract_closeout_state = complete | blocked

branch_closeout =
  closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate
  | closed_with_acq_dominant_current_baseline_and_publish_candidates_found
  | blocked_with_current_artifact_baseline_unstable
  | blocked_with_unclassified_acq_dominant_occurrences
  | blocked_with_family_consistency_conflict
  | blocked_with_non_mutation_invariant_failed
  | blocked_with_validation_failed
  | blocked_with_claim_overreach
```

`partial` and `implemented_only` are not accepted as sealed measurement closeout states for this round. If execution writes artifacts but cannot satisfy the required validation ceiling, it must not assign a success branch; it must resume validation or close with `contract_closeout_state = blocked` and the most specific `branch_closeout`.

Success may claim only:

```text
current artifact 기준 ACQ_DOMINANT residual count, surface distribution, authority class distribution, and publish_candidate_count were measured and sealed within this round's validation ceiling.
```

Success must not claim:

```text
ACQ_DOMINANT semantic quality complete
ACQ_DOMINANT disposition complete beyond the measured closeout branch
structural signal family disposition completion
publish mutation review completion
source expansion completion
rendered/runtime equivalence beyond non-mutation hash evidence
runtime rollout
deployment
Workshop readiness
release readiness
ready_for_release
```

---

## 2. Scope

This is a measurement-only, static inventory, authority classification, publish-candidate gate, and non-mutation validation round.

In scope:

* Current artifact universe definition for `ACQ_DOMINANT` measurement.
* Round opening scope lock and mutation-forbidden manifest.
* Current artifact manifest and hash manifest.
* Exact `ACQ_DOMINANT` occurrence inventory.
* Surface distribution measurement.
* Occurrence-level authority classification.
* Static membership and execution-reach proof for publish candidate determination.
* Consistency cross-check against the sealed family-wide structural signal authority classification.
* Non-mutation proof for source facts, source decisions, rendered text, runtime Lua, packaged Lua, and state fields.
* Hard gate, validation report, branch decision, and evidence-bound closeout.
* Additive docs addendum candidate only after validation passes, if governance absorption is needed.

### Explicitly Out Of Scope

* `ACQ_DOMINANT` wording rewrite.
* `ACQ_DOMINANT` semantic quality improvement.
* Acquisition explanation rewrite.
* ACQ_ONLY surface-form change.
* Compose-time subject synthesis change.
* Publish mutation review.
* Publish mutation execution.
* Source facts rewrite.
* Source decisions rewrite.
* Rendered output regeneration as an adopted output. Transient validation-side regeneration, if any, must be restored and is not adopted.
* Runtime Lua regeneration.
* Packaged Lua regeneration.
* Browser / Wiki / Tooltip behavior change.
* Manual in-game QA.
* Multiplayer validation.
* Deployment validation.
* Release readiness, Workshop readiness, B42 readiness, or `ready_for_release`.
* Structural signal disposition completion.
* Structural signal current readpoint reopening.
* Structural signal authority classification rerun.
* `FUNCTION_NARROW` second rollout.
* `FUNCTION_NARROW` or `ACQ_DOMINANT` blanket isolation reopen.
* Source expansion Group B/C.
* Candidate-state reevaluation outside measured `publish_candidate_count`.
* Repo-wide token cleanup.
* Diagnostic, test, or historical artifact deletion.

---

## 3. Non-Goals

This plan does not attempt to:

* Treat `ACQ_DOMINANT` residual existence as publish mutation pressure.
* Decide whether any measured publish candidate should be mutated.
* Rejudge the semantic correctness of acquisition dominance labels.
* Promote historical, diagnostic, report, preview, staging, or test occurrences to current writer authority.
* Reopen the 2026-05-29 structural signal current readpoint seal.
* Reopen the 2026-05-29 structural signal authority classification seal.
* Convert observer/readpoint/report/diagnostic/test evidence into default compose writer input.
* Relax the default compose data-root guard.
* Change user-facing Iris tooltip, wiki, or menu behavior.
* Claim runtime behavior preservation beyond explicit static and non-mutation evidence.
* Claim public rollout or release readiness.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style information module and must not become recommendation, comparison, or gameplay-policy authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints at execution start.
* Current structural signal basis is the 2026-05-28 Branch B reconstructed observer-only authority plus the 2026-05-29 scope split, authority classification, and current readpoint seals.
* Family-wide structural signal authority classification facts remain read-only inputs:

```text
occurrence_count = 40110
unknown_count = 0
unclassified_count = 0
observer_only = 15108
report_only = 21
historical = 1813
diagnostic = 22822
test = 346
mutation_candidate_count = 0
```

* `ACQ_DOMINANT` is not a publish writer input, runtime input, quality input, default compose input, source-row writer input, or blanket isolation candidate before this current-baseline remeasurement.
* `publish_candidate_count = 0` closes the measured debt without follow-up publish review.
* `publish_candidate_count >= 1` transfers the measured candidate set to a separate `ACQ_DOMINANT Disposition / Publish Review Round` only if the family-wide consistency rules in this plan pass.
* This round itself does not open publish mutation review.

Universe and notion assumptions that must be verified by generated artifacts:

```text
acq_dominant_universe_relation_to_family =
  subset | equal | partially_disjoint | outside_family_scope

publish_candidate_relation_to_mutation_candidate =
  same_notion | narrower_notion | broader_notion | different_notion
```

This plan's default expected relation is:

```text
acq_dominant_universe_relation_to_family = subset
publish_candidate_relation_to_mutation_candidate = same_notion
```

Any `partially_disjoint`, `outside_family_scope`, `narrower_notion`, `broader_notion`, or `different_notion` result must be documented before candidate transfer can be considered. Documentation of notion difference is not sufficient by itself. A candidate-transfer complete closeout is allowed only when every candidate is proven to be outside the prior family-wide classification universe or caused by a documented current artifact universe delta. Otherwise, any measured `publish_candidate_count >= 1` that conflicts with sealed family-wide `mutation_candidate_count = 0` must close as `blocked_with_family_consistency_conflict`.

Family taxonomy projection for cross-check:

```text
writer_input                -> mutation_candidate
forbidden_writer_reach      -> mutation_candidate
observer_only               -> observer_only
report_only                 -> report_only
historical                  -> historical
diagnostic                  -> diagnostic
test                        -> test
preview_only                -> mapped_non_writer_surface
runtime_adjacent_non_writer -> mapped_non_writer_surface
unknown                     -> blocked
```

`writer_input_count >= 1` is treated as a direct conflict with the sealed non-writer family mapping unless outside-prior-universe proof or documented current artifact universe delta explains it before Phase 5 closes.

Current runtime assumptions:

```text
current runtime hash manifest = current_runtime_hash_manifest.json
sha256 = 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
deployable authority = IrisLayer3DataChunks.lua manifest + Chunk001..011
row_count = 2105
runtime_state = adopted 2084 / unadopted 21
monolith = absent
```

Path assumptions:

* Repository root is `C:\Users\MW\Downloads\coding\PZ`.
* Current artifact inputs for default compose authority must resolve under `Iris/build/description/v2/data/`; non-data-root current-authority input remains fail-loud.
* Staging, diagnostic, test, historical, report, and preview artifacts may be scanned for occurrence measurement, but they do not become current writer inputs by being scanned.

Validation assumptions:

* Missing validation tools or blocked validation commands must be recorded as `blocked` or `not_run`, not `pass`.
* JSON/JSONL parse, determinism, and hash-diff evidence are required because this is a measurement and sealed-baseline round.
* Python unittest and Lua syntax commands are required only for a success closeout that claims the stated validation ceiling. If either command cannot run, closeout cannot be `complete`.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under the round-local artifact root if deterministic report generation requires them:

```text
Iris/build/description/v2/staging/compose_contract_migration/acq_dominant_current_baseline_remeasurement_round/
```

Repo-level build tools are not planned mutation targets. If execution requires changes to shared tooling, the round must stop and either amend the plan or open a separate implementation scope.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-acq-dominant-current-baseline-remeasurement-round-plan.md
```

Potential additive docs candidate after hard gate:

```text
Iris/build/description/v2/staging/compose_contract_migration/acq_dominant_current_baseline_remeasurement_round/docs_addendum_candidate.md
```

Direct updates to `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are not part of the measurement body. If needed, they require a gated additive-docs step after evidence and claim-boundary review.

### Config

None expected.

### Generated Artifacts

Round-local generated artifacts may be created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/acq_dominant_current_baseline_remeasurement_round/
```

Expected generated artifacts:

```text
phase0_scope_lock.json
phase0_non_goal_manifest.json
phase0_closeout_branch_contract.json
acq_dominant_token_form_manifest.json
acq_dominant_remeasurement_basis_manifest.json
authority_taxonomy_lock_note.md
phase1_current_basis_stability_anchor.json
phase1_family_universe_relation.json
phase1_current_artifact_manifest.json
phase1_artifact_hash_manifest.json
phase2_acq_dominant_occurrence_inventory.jsonl
phase2_occurrence_summary.json
phase3_surface_distribution.json
acq_dominant_surface_matrix.csv
phase4_authority_classification.jsonl
phase4_authority_class_counts.json
phase4_unknown_or_forbidden_writer_reach.jsonl
phase4_family_taxonomy_projection.json
phase5_publish_candidate_gate.json
phase5_candidate_transfer_packet.jsonl
acq_dominant_current_baseline_seal.json
acq_dominant_baseline_hash_manifest.json
phase6_non_mutation_hash_diff.json
phase6_validation_report.json
acq_dominant_current_baseline_remeasurement_closeout.md
docs_addendum_candidate.md
```

`phase5_candidate_transfer_packet.jsonl` is a conditional artifact:

```text
conditional_artifact = true
condition = publish_candidate_count >= 1 AND family_consistency_crosscheck_pass = true
```

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope, Measurement Basis, and Taxonomy Lock

Purpose:

Open the round as measurement-only, lock the current artifact basis, and define authority classes before scanning.

Files:

```text
phase0_scope_lock.json
phase0_non_goal_manifest.json
phase0_closeout_branch_contract.json
acq_dominant_token_form_manifest.json
acq_dominant_remeasurement_basis_manifest.json
authority_taxonomy_lock_note.md
```

Implementation Notes:

* Record round classification:

```text
measurement_only = true
source_mutation_allowed = false
rendered_mutation_allowed = false
runtime_lua_mutation_allowed = false
packaged_lua_mutation_allowed = false
state_field_mutation_allowed = false
publish_mutation_review_allowed = false
blanket_isolation_reopen_allowed = false
```

* Define current artifact, reference artifact, historical artifact, diagnostic artifact, test artifact, report artifact, preview artifact, and runtime-adjacent non-writer artifact roles.
* Lock authority class candidates:

```text
writer_input
observer_only
report_only
preview_only
diagnostic
test
historical
runtime_adjacent_non_writer
unknown
forbidden_writer_reach
```

* Lock terminal class precedence:

```text
writer_input
> forbidden_writer_reach
> runtime_adjacent_non_writer
> observer_only / report_only / preview_only / diagnostic / test / historical
> unknown
```

* Generate `acq_dominant_token_form_manifest.json` before inventory. It must include:

```text
canonical_identifier
allowed_enum_forms
allowed_label_forms
known_alias_or_variant_forms
excluded_similar_tokens
token_form_source
```

* Define publish candidate formula:

```text
publish_candidate_count =
  count(authority_class in ["writer_input", "forbidden_writer_reach"])
```

* `unknown` and unclassified classes are blocking states, not publish or non-publish assumptions.
* Define `phase0_closeout_branch_contract.json` with `contract_closeout_state`, `branch_closeout`, and hard-gate-to-branch mapping. The only planned contract states for sealed closeout are `complete` and `blocked`.

Validation:

* Scope lock JSON parses.
* Non-goal manifest lists every forbidden mutation surface.
* Token-form manifest exists and is the authority for Phase 2 inventory completeness.
* Authority taxonomy is mutually exclusive enough for occurrence classification.
* Terminal class precedence is explicit.
* Closeout branch contract maps all hard-gate failures to one normalized branch.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation reopen remains forbidden.
* This phase performs no occurrence mutation or publish review.

---

### Change 2 - Phase 1 Current Artifact Manifest and Hash Baseline

Purpose:

Build the current artifact universe for `ACQ_DOMINANT` measurement and establish hash-level baseline evidence.

Files:

```text
phase1_current_basis_stability_anchor.json
phase1_family_universe_relation.json
phase1_current_artifact_manifest.json
phase1_artifact_hash_manifest.json
```

Implementation Notes:

* Enumerate every scanned artifact with:

```text
path
scan_root
scan_root_role
surface_role
artifact_kind
current_target
generated_or_hand_authored
historical_or_current
hash
scan_included
writer_input_candidate
excluded_path_family
exclusion_reason
```

* Separate current target artifacts from reference, historical, diagnostic, test, report, and preview artifacts.
* Normalize path aliases before counting files.
* Do not treat staging or generated report paths as current writer input solely because they contain `ACQ_DOMINANT`.
* Record explicit exclusion reasons for any path family not scanned.
* Generate `phase1_current_basis_stability_anchor.json` by checking current measurement basis against pre-existing sealed build-time anchors:

```text
Branch B reconstruction artifact set sealed hash / manifest
Structural Signal Scope Split Seal evidence-root manifest
Structural Signal Authority Classification Seal evidence-root manifest
Structural Signal Current Readpoint Seal docs-only absorption evidence
```

* Generate `phase1_family_universe_relation.json` with:

```text
acq_dominant_universe_relation_to_family
publish_candidate_relation_to_mutation_candidate
family_universe_anchor
current_artifact_universe_delta_count
current_artifact_universe_delta_reason
```

* If the current measurement basis cannot be tied to a pre-existing sealed build-time anchor, close as `blocked_with_current_artifact_baseline_unstable`.

Validation:

* Current basis stability anchor exists and passes.
* Manifest JSON parses.
* Every scanned file has `surface_role`.
* Every scanned file has `scan_root` and `scan_root_role`.
* Every excluded path family has `excluded_path_family` and `exclusion_reason`.
* Unknown surface count is `0`.
* Duplicate normalized path count is `0`, or duplicates are explicitly mapped.
* `phase1_family_universe_relation.json` declares universe and notion relation before Phase 4/5 classification.
* Artifact hash manifest exists before occurrence inventory generation.

---

### Change 3 - Phase 2 ACQ_DOMINANT Occurrence Inventory

Purpose:

Statically enumerate every `ACQ_DOMINANT` occurrence across the locked artifact universe.

Files:

```text
phase2_acq_dominant_occurrence_inventory.jsonl
phase2_occurrence_summary.json
```

Implementation Notes:

* Scan only token forms authorized by `acq_dominant_token_form_manifest.json`.
* Assign stable occurrence ids.
* Record:

```text
occurrence_id
token_form
token_form_manifest_digest
path
line_or_json_pointer
context_excerpt_or_field
surface_role
artifact_kind
row_key
context_field
row_linked
file_only
generated_or_hand_authored
current_or_historical
duplicate_group
unique_source_occurrence
```

* Separate grep-like raw occurrence count from logical unique source occurrence count.
* Keep file-only occurrences in the inventory instead of dropping them.
* Do not promote historical or diagnostic occurrences into writer authority during inventory.
* Inventory completeness is judged against `canonical_identifier`, `allowed_enum_forms`, `allowed_label_forms`, and `known_alias_or_variant_forms`; excluded similar tokens must be listed but not counted.

Validation:

* JSONL parses.
* `acq_dominant_occurrence_count` is calculated.
* Every counted row references an allowed token form.
* Excluded similar token count is reported separately.
* Row-linked and file-only counts are both reported.
* Duplicate accounting rule is documented.
* A two-run determinism check reproduces occurrence ids and counts, but determinism is not treated as token-form completeness without the token-form manifest check.
* No occurrence proceeds to closeout without Phase 4 classification.

---

### Change 4 - Phase 3 Surface Distribution Measurement

Purpose:

Measure where `ACQ_DOMINANT` residuals remain and separate current, historical, generated, report, diagnostic, test, and writer-adjacent surfaces.

Files:

```text
phase3_surface_distribution.json
acq_dominant_surface_matrix.csv
```

Implementation Notes:

* Calculate:

```text
total occurrence count
unique row count
file count
surface_role count
current count
historical count
generated count
hand-authored count
row-linked count
file-only count
writer-adjacent candidate surface count
```

* Distribution is descriptive. It does not create publish mutation authority.
* Report-only, diagnostic, test, historical, preview, runtime-adjacent non-writer, and writer-adjacent surfaces must be visible as separate buckets.
* `phase3_surface_distribution.json` is the canonical measurement artifact.
* `acq_dominant_surface_matrix.csv` is a derived view-only artifact and cannot override the canonical JSON counts.

Validation:

* Phase 2 inventory total equals Phase 3 distribution total.
* Surface matrix and canonical JSON counts agree; disagreement blocks closeout and canonical JSON remains the authority.
* `surface_role` missing count is `0`.
* Current/historical and generated/hand-authored separations are explicit.
* Writer-adjacent surface count is not interpreted as publish candidate count without Phase 4 reach proof.

---

### Change 5 - Phase 4 Authority Classification and Writer Reach Proof

Purpose:

Classify every `ACQ_DOMINANT` occurrence by authority class and determine whether any occurrence reaches publish writer input or forbidden writer reach.

Files:

```text
phase4_authority_classification.jsonl
phase4_authority_class_counts.json
phase4_unknown_or_forbidden_writer_reach.jsonl
phase4_family_taxonomy_projection.json
```

Implementation Notes:

* Join the Phase 2 inventory and Phase 3 surface distribution.
* Assign exactly one terminal authority class or a blocking `unknown`.
* Apply terminal class precedence from Phase 0 when multiple signals are present. `unknown` is not a low-priority fallback; it is used only when the occurrence cannot be classified by the locked taxonomy and therefore blocks success closeout.
* Record classification evidence:

```text
classification_reason
surface_membership_basis
static_writer_membership
execution_reach_basis
default_compose_writer_reach
quality_publish_writer_reach
runtime_writer_reach
lua_bridge_writer_reach
browser_wiki_consumer_reach
forbidden_writer_reach
```

* Classification must distinguish semantic strength from writer authority.
* `writer_input` is not assumed from the token name. It must be proven by current writer path membership.
* `forbidden_writer_reach = true` is a blocking or candidate-transfer condition, not a permission to mutate in this round.
* Generate `phase4_family_taxonomy_projection.json` by mapping the 10-class round taxonomy into the family-wide structural classification taxonomy:

```text
writer_input                -> mutation_candidate
forbidden_writer_reach      -> mutation_candidate
observer_only               -> observer_only
report_only                 -> report_only
historical                  -> historical
diagnostic                  -> diagnostic
test                        -> test
preview_only                -> mapped_non_writer_surface
runtime_adjacent_non_writer -> mapped_non_writer_surface
unknown                     -> blocked
```

Validation:

* Classification coverage is `100%`.
* `unknown_count = 0` for success.
* `unclassified_count = 0` for success.
* `writer_input_count` is reported.
* `forbidden_writer_reach_count` is reported.
* Static membership and execution-reach proof are both present for any candidate.
* Projection to the family taxonomy is complete.
* Family-wide `mutation_candidate_count = 0` consistency cross-check is prepared for Phase 5.

---

### Change 6 - Phase 5 Publish-Candidate Gate and Family Consistency Cross-Check

Purpose:

Calculate `publish_candidate_count`, decide the follow-up branch, and check consistency with the sealed family-wide classification.

Files:

```text
phase5_publish_candidate_gate.json
phase5_candidate_transfer_packet.jsonl
```

Implementation Notes:

* Calculate:

```text
publish_candidate_count =
  writer_input_count + forbidden_writer_reach_count
```

* Use `phase5_candidate_transfer_packet.jsonl` only if all of the following are true:

```text
publish_candidate_count >= 1
family_consistency_crosscheck_complete = true
family_consistency_crosscheck_pass = true
unexplained_family_conflict_count = 0
```

* If `publish_candidate_count = 0`, record:

```text
follow_up_publish_review_required = false
closeout_branch = closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate
```

* If `publish_candidate_count >= 1` and every candidate is proven to be outside the prior family-wide classification universe or caused by a documented current artifact universe delta, record:

```text
follow_up_publish_review_required = true
closeout_branch = closed_with_acq_dominant_current_baseline_and_publish_candidates_found
candidate_set_transferred_to = ACQ_DOMINANT Disposition / Publish Review Round
candidate_transfer_reason = outside_prior_family_universe | documented_current_artifact_universe_delta
```

* If family-wide `mutation_candidate_count = 0` conflicts with measured `publish_candidate_count`, do not force success. Candidate-transfer closeout is allowed only under the predefined universe/delta conditions above. Otherwise record:

```text
family_consistency_crosscheck_pass = false
unexplained_family_conflict_count >= 1
closeout_branch = blocked_with_family_consistency_conflict
```

* If `writer_input_count >= 1` occurs inside the prior family-wide universe and no outside-prior-universe proof or documented current artifact universe delta explains it, the round must close as `blocked_with_family_consistency_conflict`.
* `phase5_candidate_transfer_packet.jsonl` must record:

```text
conditional_artifact = true
condition = publish_candidate_count >= 1 AND family_consistency_crosscheck_pass = true
```

Validation:

* Publish candidate formula is recorded.
* Candidate rows, if any, have occurrence ids and reach proof.
* `unknown_count = 0` and `unclassified_count = 0` are required before candidate branch closeout.
* `family_consistency_crosscheck_complete = true`.
* `family_consistency_crosscheck_pass = true` for any `complete` closeout.
* `unexplained_family_conflict_count = 0` for any `complete` closeout.
* This phase does not open publish mutation review.

---

### Change 7 - Phase 6 Baseline Seal, Non-Mutation Validation, and Hard Gate

Purpose:

Seal the measured baseline and prove this round did not mutate source, rendered, runtime, packaged, or state surfaces.

Files:

```text
acq_dominant_current_baseline_seal.json
acq_dominant_baseline_hash_manifest.json
phase6_non_mutation_hash_diff.json
phase6_validation_report.json
```

Implementation Notes:

* Seal:

```text
occurrence inventory hash
surface distribution hash
authority classification hash
publish candidate gate hash
round artifact hash manifest
closeout branch input
```

* Verify unchanged:

```text
source facts
source decisions
rendered text
runtime Lua
packaged Lua
quality_state
publish_state
runtime_state
default compose current authority inputs
```

* If validation commands regenerate files as side effects, restore the pre-validation frozen snapshot before making any non-mutation claim.
* Any transient rendered or generated-artifact regeneration caused by validation must be restored before closeout and must not become an adopted output.
* Hard gate must include:

```text
json_parse_pass
jsonl_parse_pass
determinism_pass
current_basis_stability_anchor_pass
occurrence_inventory_complete
surface_distribution_complete
authority_classification_complete
unknown_count_zero
unclassified_count_zero
publish_candidate_gate_complete
family_consistency_crosscheck_complete
family_consistency_crosscheck_pass
unexplained_family_conflict_count_zero
non_mutation_hash_diff_pass
python_unittest_pass
lua_syntax_pass
claim_boundary_pass
all_gates_pass
```

Validation:

* JSON/JSONL parse passes.
* Two-run determinism passes.
* Current build-time basis stability anchor passes.
* Python unittest command exits `0`.
* Lua syntax command exits `0`.
* Non-mutation hash diff passes.
* Family consistency cross-check passes with unexplained conflict count `0`.
* Hard gate `all_gates_pass = true` is required for `complete`.

---

### Change 8 - Phase 7 Closeout, Candidate Transfer, and Gated Docs Absorption

Purpose:

Close the round according to measured `publish_candidate_count`, preserve non-claims, and produce additive docs candidate only if needed.

Files:

```text
acq_dominant_current_baseline_remeasurement_closeout.md
docs_addendum_candidate.md
```

Implementation Notes:

* Branch rule:

```text
publish_candidate_count = 0
AND family_consistency_crosscheck_pass = true
-> closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate
-> no follow-up publish review

publish_candidate_count >= 1
AND family_consistency_crosscheck_pass = true
AND every candidate is outside the prior family-wide universe OR caused by documented current artifact universe delta
-> closed_with_acq_dominant_current_baseline_and_publish_candidates_found
-> transfer measured candidate set to separate ACQ_DOMINANT Disposition / Publish Review Round
-> no mutation or review inside this round

unknown_count > 0 or unclassified_count > 0
-> blocked_with_unclassified_acq_dominant_occurrences
-> no disposition completion claim

current_basis_stability_anchor_pass = false
-> blocked_with_current_artifact_baseline_unstable

family_consistency_crosscheck_pass = false
or unexplained_family_conflict_count > 0
-> blocked_with_family_consistency_conflict

non_mutation_hash_diff_pass = false
-> blocked_with_non_mutation_invariant_failed

required validation command fails or is not run
-> blocked_with_validation_failed

claim_boundary_pass = false
or closeout wording exceeds evidence ceiling
-> blocked_with_claim_overreach
```

* `complete` in the candidate-transfer branch means the measurement round completed its own deliverables: measured baseline seal, candidate proof, and transfer packet. It does not mean `ACQ_DOMINANT disposition complete`.
* Closeout must explicitly list claimed and not-claimed areas.
* `docs_addendum_candidate.md` is an additive candidate, not automatic governance-body mutation.
* Any later update to `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` must preserve the measured claim boundary and avoid declaring release, deployment, semantic quality, or full disposition completion.

Validation:

* Closeout branch matches measured gate result.
* Non-claim section is present.
* Candidate transfer packet exists if and only if `publish_candidate_count >= 1` and `family_consistency_crosscheck_pass = true`.
* No publish mutation review is opened by closeout wording.
* Additive docs candidate, if present, does not modify sealed historical bodies.

---

## 7. Validation Plan

### Automated Validation

Required change review:

```powershell
git diff --stat
git diff
```

Required artifact validation:

```text
JSON parse for every generated JSON artifact
JSONL parse for every generated JSONL artifact
CSV parse or row-count check for acq_dominant_surface_matrix.csv
token-form manifest completeness check
current build-time basis stability anchor check
scan root / exclusion rule coverage check
sha256 hash manifest for every generated artifact
2-run determinism digest match for generated measurement artifacts
inventory total vs distribution total consistency check
canonical JSON distribution vs CSV derived view consistency check
authority classification coverage check
publish candidate formula check
family-wide mutation_candidate_count consistency cross-check
family_consistency_crosscheck_pass check
unexplained_family_conflict_count = 0 check
non-mutation hash diff
hard gate all_gates_pass check
```

Required Python regression validation for success closeout:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Success condition:

```text
exit code = 0
```

Required Lua syntax validation for success closeout:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Success condition:

```text
exit code = 0
```

If the exact command cannot be run, the result must be recorded as `blocked` or `not_run`, not `pass`.

### Manual Validation

* Review Phase 0 scope lock for measurement-only posture.
* Review `acq_dominant_token_form_manifest.json` before accepting inventory completeness.
* Review `phase1_current_basis_stability_anchor.json` against pre-existing sealed evidence roots.
* Review current artifact manifest for over-inclusion and under-inclusion.
* Review scan root and exclusion reason coverage.
* Review sample occurrence rows across current, historical, diagnostic, test, report, preview, and runtime-adjacent surfaces.
* Review duplicate accounting to ensure repeated generated output is not confused with unique source residual.
* Review authority classification samples for each terminal class.
* Review terminal class precedence cases where multiple signals are present.
* Review static writer membership and execution-reach proof for any candidate.
* Review family-wide consistency cross-check, especially universe/delta proof for any candidate-transfer branch.
* Review closeout claim boundary and non-claims.

### Validation Limits

This execution will not perform:

* Manual in-game validation.
* Runtime behavior validation.
* Deployment validation.
* Multiplayer validation.
* Long-session runtime validation.
* External ecosystem compatibility sweep.
* Workshop validation.
* Release validation.
* B42 readiness validation.
* Full runtime equivalence validation beyond non-mutation hash evidence.
* Semantic quality revalidation.
* Publish mutation validation.
* Publish mutation review.
* Source expansion validation.
* Browser / Wiki / Tooltip behavior validation.

---

## 8. Risk Surface Touch

### Authority Surface

Touched as measurement evidence only. The round adds a measured `ACQ_DOMINANT` baseline, surface distribution, authority classification, and publish-candidate gate. It does not create writer authority, publish authority, quality authority, runtime authority, or default compose authority.

### Runtime Behavior Surface

None intended. Runtime Lua, packaged Lua, Browser, Wiki, Tooltip behavior, Lua bridge payload, and deployed runtime data remain unchanged.

### Compatibility Surface

None intended. External mod compatibility and PZ runtime behavior are not mutation targets and are not validated beyond non-mutation evidence.

### Sealed Artifact Surface

Touched additively. New round-local sealed measurement artifacts may be created. Existing sealed bodies and prior round artifacts are consumed read-only and must not be modified. The current build-time measurement basis must be tied to a pre-existing sealed anchor before the new baseline can be sealed.

### Public-Facing Output Surface

None. The round does not change user-facing text, UI, tooltip content, wiki content, package output, release notes, Workshop state, or public readiness claims.

---

## 9. Risk Analysis

### Architecture Risk

* `ACQ_DOMINANT` residual presence could be misread as publish mutation requirement.
* Historical, diagnostic, test, report, or preview artifacts could be promoted to current writer authority.
* The measurement round could accidentally reopen structural signal current readpoint seal or authority classification seal.
* `unknown` or unclassified occurrence could be silently treated as non-publish.
* Semantic strength could be confused with writer authority.
* Candidate discovery could be handled as mutation permission inside this round instead of transfer to a separate round.
* A measured candidate inside the prior family-wide universe could be incorrectly transferred instead of blocked as a family consistency conflict.

### Runtime Risk

* Validation or helper generation could accidentally refresh rendered output or runtime chunks.
* A measurement script could scan and rewrite generated artifacts if not kept read-only.
* Runtime Lua or state fields could change as side effects, invalidating non-mutation closeout.
* Transient validation regeneration could be mistaken for an adopted output if not restored before closeout.

### Compatibility Risk

* The closeout could imply compatibility preservation without compatibility testing.
* Overbroad docs wording could imply public readiness, deployment, or runtime equivalence.
* A future publish review could be inferred from residual count alone instead of measured candidate proof.

### Regression Risk

* Current artifact manifest could omit a relevant path family and undercount residuals.
* Generated report repetition could inflate unique residual count.
* Path aliases could double-count the same artifact.
* Static grep could miss token-shape variants.
* Token-form determinism could be mistaken for token-form completeness.
* Surface distribution counts could disagree with the canonical occurrence inventory.
* Family-wide `mutation_candidate_count = 0` could be ignored if measured candidates appear.
* `family_consistency_crosscheck_complete` could be mistaken for `family_consistency_crosscheck_pass`.
* Missing validation tools could be misreported as pass.

---

## 10. Rollback Plan

Rollback is measurement-artifact rollback, not product/runtime rollback.

1. Review touched files with:

```powershell
git diff --stat
git diff
```

2. Remove or quarantine only artifacts created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/acq_dominant_current_baseline_remeasurement_round/
```

3. If optional round-local helper scripts were created, remove or quarantine only those helper scripts after confirming they are not shared repo tools.

4. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, `quality_state`, `publish_state`, `runtime_state`, or sealed historical bodies changed unexpectedly, stop and identify the exact change source before reverting only changes made by this round.

5. If validation commands regenerated output as a side effect, restore the pre-validation frozen snapshot and rerun non-mutation hash diff.

6. If candidate rows are found but closeout wording opens mutation inside this round, rewrite closeout to candidate-transfer wording or close blocked.

7. If measured inventory is incomplete, authority classification has unknowns, or family consistency conflicts remain unresolved, close with the normalized blocked branch:

```text
blocked_with_unclassified_acq_dominant_occurrences
blocked_with_family_consistency_conflict
blocked_with_non_mutation_invariant_failed
blocked_with_validation_failed
blocked_with_claim_overreach
```

8. If current build-time basis stability cannot be tied to the pre-existing sealed anchors, close as:

```text
blocked_with_current_artifact_baseline_unstable
```

9. If non-mutation evidence fails, validation fails, or the closeout wording exceeds the evidence ceiling, close with the corresponding normalized branch:

```text
blocked_with_non_mutation_invariant_failed
blocked_with_validation_failed
blocked_with_claim_overreach
```

10. If a sealed closeout later proves incorrect, do not rewrite the sealed body directly. Add a later correction or supersession artifact.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains a 100% Lua wiki-style module and does not take on recommendation, comparison, gameplay policy, runtime stability, or cross-module authority roles.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation remains intact.
* Offline measurement artifacts do not become runtime Lua or source writer authority.
* Default compose current authority remains under `Iris/build/description/v2/data/`.
* Non-data-root current-authority input must fail loud.
* Current writer authority and observer/report/diagnostic/test/historical authority remain separated.
* `publish_candidate` and sealed family-wide `mutation_candidate` notion relation must be declared before Phase 5 branch closeout.
* Candidate transfer is forbidden unless the candidate is outside the prior family-wide universe or caused by a documented current artifact universe delta.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation reopen is forbidden.
* Publish mutation review is forbidden inside this measurement round.
* Historical, diagnostic, test, report, and preview surfaces must not be promoted to current writer input.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, and state fields remain non-mutation targets.
* Existing sealed artifacts are consumed read-only.
* Missing, unknown, or unclassified occurrence evidence must block rather than silently fall back.
* Validation may not be claimed as passed unless the exact relevant command exits with code `0`.
* Additive docs wording, if generated, must preserve non-claims and cannot update sealed governance state automatically.
* Release readiness, Workshop readiness, deployment readiness, B42 readiness, and `ready_for_release` claims are forbidden.

---

## 12. Expected Closeout State

Expected contract closeout state:

```text
complete
```

Planned non-success contract closeout state:

```text
blocked
```

`partial` and `implemented_only` are not planned sealed closeout states for this measurement round. `complete` is valid only within the validation ceiling stated in this plan and only if:

```text
current artifact manifest exists
current basis stability anchor exists and passes
artifact hash manifest exists
ACQ_DOMINANT token-form manifest exists
ACQ_DOMINANT occurrence inventory exists
surface distribution exists
authority classification ledger exists
family taxonomy projection exists
classification coverage = 100%
unknown_count = 0
unclassified_count = 0
writer_input_count is reported
forbidden_writer_reach_count is reported
publish_candidate_count is calculated and sealed
static membership and execution-reach proof support candidate gate
family_consistency_crosscheck_complete = true
family_consistency_crosscheck_pass = true
unexplained_family_conflict_count = 0
source facts unchanged
source decisions unchanged
rendered text unchanged
runtime Lua unchanged
packaged Lua unchanged
quality_state unchanged
publish_state unchanged
runtime_state unchanged
JSON/JSONL parse passes
2-run determinism passes
Python unittest exits 0
Lua syntax exits 0
hard gate all_gates_pass = true
closeout non-claims are explicit
```

When these conditions pass, the closeout records:

```text
contract_closeout_state = complete
```

Branch-specific complete closeout:

```text
publish_candidate_count = 0
AND family_consistency_crosscheck_pass = true
-> closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate
-> follow-up publish review not required

publish_candidate_count >= 1
AND family_consistency_crosscheck_pass = true
AND every candidate is outside the prior family-wide universe OR caused by documented current artifact universe delta
-> closed_with_acq_dominant_current_baseline_and_publish_candidates_found
-> measured candidate set transferred to separate ACQ_DOMINANT Disposition / Publish Review Round
-> measurement deliverables complete only; ACQ_DOMINANT disposition completion is not claimed
```

Expected blocked closeout branch mapping:

```text
blocked_with_current_artifact_baseline_unstable
-> current_basis_stability_anchor_pass = false
-> current artifact universe cannot be tied to pre-existing sealed build-time evidence
-> scan root / exclusion coverage cannot establish stable basis

blocked_with_unclassified_acq_dominant_occurrences
-> occurrence_inventory_complete = false
-> authority_classification_complete = false
-> unknown_count > 0
-> unclassified_count > 0
-> token-form manifest completeness check fails

blocked_with_family_consistency_conflict
-> family_consistency_crosscheck_pass = false
-> unexplained_family_conflict_count > 0
-> writer_input_count >= 1 inside prior family-wide universe without outside-prior-universe proof or documented current artifact universe delta
-> publish_candidate_count >= 1 without outside-family-universe proof or documented current artifact universe delta

blocked_with_non_mutation_invariant_failed
-> non-mutation hash diff fails

blocked_with_validation_failed
-> validation fails

blocked_with_claim_overreach
-> closeout wording exceeds evidence ceiling
```

Expected final claim boundary:

```text
current artifact 기준 ACQ_DOMINANT residual distribution을 재측정했고,
모든 occurrence의 authority class를 분류했으며,
publish_candidate_count를 기준으로 후속 publish review 필요 여부를 봉인했다.
```

Expected non-claims:

```text
ACQ_DOMINANT semantic quality 완료 아님
ACQ_DOMINANT disposition complete 전면 선언 아님
structural signal family disposition completion 아님
publish mutation review 완료 아님
publish mutation 실행 아님
source expansion 완료 아님
rendered/runtime equivalence 독립 검증 완료 아님
runtime rollout 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
```
