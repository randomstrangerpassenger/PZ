# Iris DVF 3-3 Layer4 Boundary Current Corpus Lock Round Plan

> 상태: Draft v0.3-minor-review-applied
> 기준일: 2026-05-31
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Iris DVF 3-3 Layer4 Boundary Current Corpus Lock Round` (2026-05-31 user-provided synthesis)
> review input: `REVIEW - Iris DVF 3-3 Layer4 Boundary Current Corpus Lock Round Plan 종합 검토안` (2026-05-31 user-provided synthesis), Critical 2, Major 3, and selected required minor revisions incorporated in v0.2. Follow-up minor/NC feedback incorporated in v0.3.
> 직접 상위 readpoint:
> - 2026-04-29 Layer4 Absorption Policy Round `closed_with_policy_sealed_zero_count_production_safe`
> - 2026-04-29 Layer4 Absorption is sealed as a decision namespace, not a structural axis
> - 2026-05-29 Structural Signal Scope Split Seal Round `closed_with_structural_signal_scope_split_sealed_observer_only`
> - 2026-05-29 Structural Signal Authority Classification Round `closed_with_structural_signal_authority_classification_sealed`
> - 2026-05-29 Structural Signal Current Readpoint Seal Round `closed_with_structural_signal_current_readpoint_doc_absorption_only`
> - 2026-05-30 ACQ_DOMINANT Current Baseline Remeasurement Round `closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> contract vocabulary: `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`. The template is an execution-plan form only and does not create semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> execution_scale: `governance`
> scope_qualifier: `docs_static_artifact_authority_corpus_lock`
> 실행 상태: planning authority only. This document opens no `LAYER4_ABSORPTION_CONFIRMED` count, runtime mutation, publish mutation review, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 `LAYER4_ABSORPTION_CONFIRMED` current remeasurement를 수행하기 전에, current checkout에서 측정 대상 artifact universe와 제외 surface를 봉인하는 것이다.

이 round는 count round가 아니다. 이번 round가 답해야 하는 질문은 다음으로 제한한다.

```text
current checkout 기준으로 LAYER4_ABSORPTION_CONFIRMED를 후속 측정할 때
어떤 artifact surface를 measurement corpus로 읽을 수 있고,
어떤 surface는 historical / diagnostic / report-only / preview-only / staging / test / reference-only로 제외해야 하며,
과거 zero-count closeout을 current count로 직접 승계하지 않는다는 조건을 어떻게 봉인할 것인가?
```

Round id:

```text
layer4_boundary_current_corpus_lock_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/
```

Expected success closeout branches:

```text
closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight
closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_machine_preflight
```

Blocked closeout branches:

```text
blocked_with_layer4_corpus_basis_unstable
blocked_with_layer4_surface_inventory_incomplete
blocked_with_layer4_surface_classification_unresolved
blocked_with_layer4_partition_integrity_failed
blocked_with_layer4_manifest_validation_failed
blocked_with_layer4_preflight_guard_failed
blocked_with_non_mutation_invariant_failed
blocked_with_validation_failed
blocked_with_claim_overreach
```

Closeout records must separate `docs/EXECUTION_CONTRACT.md` state from branch label:

```text
contract_closeout_state = complete | blocked

branch_closeout =
  closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight
  | closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_machine_preflight
  | blocked_with_layer4_corpus_basis_unstable
  | blocked_with_layer4_surface_inventory_incomplete
  | blocked_with_layer4_surface_classification_unresolved
  | blocked_with_layer4_partition_integrity_failed
  | blocked_with_layer4_manifest_validation_failed
  | blocked_with_layer4_preflight_guard_failed
  | blocked_with_non_mutation_invariant_failed
  | blocked_with_validation_failed
  | blocked_with_claim_overreach
```

Success may claim only:

```text
Current checkout 기준 LAYER4_ABSORPTION_CONFIRMED 후속 측정을 위한 artifact universe,
current measurement corpus, excluded surface classes, no-inheritance rule,
and manifest / partition prerequisite were locked within this round's validation ceiling.
```

Success must not claim:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출
Layer4 absorption problem resolved
Layer4 hard-block policy revalidated as current count
Layer4 boundary policy redesign
structural signal disposition completion
FUNCTION_NARROW second rollout
ACQ_DOMINANT publish review
publish mutation review
source facts mutation
source decisions mutation
rendered text mutation
runtime Lua mutation
packaged Lua mutation
runtime rollout
manual in-game validation
deployment
Workshop readiness
B42 readiness
release readiness
ready_for_release
```

---

## 2. Scope

This is a governance-scale docs/static-artifact, authority-corpus, no-count lock round. It creates or seals a future measurement corpus authority and reclassifies current checkout artifact surfaces for downstream `LAYER4_ABSORPTION_CONFIRMED` measurement. It does not mutate runtime/source surfaces, but it touches governed authority and sealed artifact surfaces.

It may create round-local evidence artifacts and, only after hard gate and review, additive governance-doc candidate updates.

In scope:

* Scope statement that this round is a corpus-lock prerequisite, not a count measurement.
* Predecessor readpoint inventory for Layer4, structural signal, `FUNCTION_NARROW`, and `ACQ_DOMINANT`.
* Forbidden reopen list for closed readpoints.
* Body-role `LAYER4_ABSORPTION` lint substrate anchor for the actual current build artifact/input consumed by the lint path.
* Canonical token / matching semantics / `LAYER4_ABSORPTION_CONFIRMED` literal-vs-synthetic reconciliation.
* Scan root coverage matrix and known-surface checklist.
* Current checkout artifact surface inventory for Layer4 boundary / absorption / confirmed signals.
* Authority-class mapping for inventory rows using `primary_class` plus `secondary_tags`.
* Inclusion / exclusion partition for current measurement corpus.
* Partition integrity hard gate.
* No-inheritance rule demoting prior Layer4 zero-count to historical readpoint only.
* Current corpus manifest, checkout basis, dirty-tree handling, and hash basis pinning.
* Measurement preflight guard design or round-local guard implementation.
* Deterministic generation rules for inventory, classification, partition, and manifest artifacts.
* Adversarial review and gated additive documentation promotion, if needed.
* Evidence-bound closeout with explicit validation ceiling and non-claims.

### Explicitly Out Of Scope

* Actual `LAYER4_ABSORPTION_CONFIRMED` current count.
* 2026-04-29 Layer4 zero-count remeasurement.
* Layer4 policy redesign.
* Layer4 as a structural axis.
* Layer 3-3 / Layer 4 boundary semantics rewrite.
* Publish writer authority redefinition.
* Structural signal classification rerun.
* Structural signal disposition completion.
* `FUNCTION_NARROW` disposition reopen or second rollout.
* `ACQ_DOMINANT` disposition reopen or publish mutation review.
* Source expansion.
* Identity fallback work.
* Acquisition hint work.
* Body recompose.
* Runtime Lua regeneration.
* Packaged Lua regeneration.
* Browser / Wiki / Tooltip behavior change.
* Current runtime baseline re-seal.
* Manual in-game validation.
* Multiplayer validation.
* Long-session runtime validation.
* B42 validation.
* Release / Workshop readiness.
* Historical report cleanup.
* Diagnostic fixture deletion.
* Staging artifact deletion.

---

## 3. Non-Goals

This plan does not attempt to:

* Turn lexical occurrence search into current authority.
* Promote historical closeout artifacts to current measurement corpus.
* Promote diagnostic-only fixtures to current writer input.
* Promote report-only or preview-only artifacts to publish candidates.
* Treat staging residue as current corpus by default.
* Treat prior zero-count as current count.
* Treat an empty included corpus as `LAYER4_ABSORPTION_CONFIRMED = 0`.
* Reopen `FUNCTION_NARROW`, `ACQ_DOMINANT`, or structural signal closed readpoints.
* Decide whether Layer4 absorption should be fixed, rewritten, or published.
* Claim runtime behavior preservation beyond explicit non-mutation evidence.
* Claim public rollout, deployment, or release readiness.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style information module and must not become a recommendation, comparison, or gameplay-policy system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints at execution start.
* Layer4 Absorption is sealed as a decision namespace, not a structural axis.
* The 2026-04-29 Layer4 zero-count is a historical predecessor readpoint, not a direct current count.
* `FUNCTION_NARROW` residual remains report / preview structural flag only and does not open a second rollout.
* `ACQ_DOMINANT` remains closed as no publish candidate according to the 2026-05-30 current-baseline remeasurement closeout.
* Structural signal authority classification remains a non-writer precedent and is not rerun by this round.
* Default compose current authority inputs remain guarded under `Iris/build/description/v2/data/`.
* Runtime/build-time separation remains intact.
* Current runtime baseline is read-only reference only:

```text
row_count = 2105
runtime_state = adopted 2084 / unadopted 21
deployable authority = IrisLayer3DataChunks manifest + Chunk001..011
monolith = absent
```

Corpus assumptions that must be verified by generated artifacts:

```text
corpus_basis_state = stable | unstable
inventory_coverage_state = complete | incomplete
lint_substrate_anchor_state = anchored | missing | unstable
scan_root_coverage_state = complete | incomplete
known_surface_checklist_state = complete | incomplete
partition_integrity_state = pass | fail
no_inheritance_rule_state = sealed | missing
preflight_guard_state = pass | fail | not_implemented
```

Expected success requires:

```text
corpus_basis_state = stable
inventory_coverage_state = complete
lint_substrate_anchor_state = anchored
scan_root_coverage_state = complete
known_surface_checklist_state = complete
partition_integrity_state = pass
no_inheritance_rule_state = sealed
```

`preflight_guard_state = not_implemented` is allowed only if the closeout explicitly downgrades the preflight guard to design-only and does not claim machine-enforced guard coverage. If machine-enforced guard coverage is claimed, `preflight_guard_state` must be `pass`.

Body-role lint substrate assumptions:

* Execution must prove the actual current build substrate consumed by body-role `LAYER4_ABSORPTION` lint before defining `current_measurement_corpus`.
* Current code-path candidate is `Iris/build/description/v2/tools/build/build_body_role_lint_feedback.py`.
* Candidate lint substrate inputs are:

```text
Iris/build/description/v2/output/dvf_3_3_rendered.json
Iris/build/description/v2/data/dvf_3_3_facts.jsonl
Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl
Iris/build/description/v2/tools/style/rules/structural_rules.json
```

* Candidate lint outputs are reference/report outputs, not current measurement corpus by default:

```text
Iris/build/description/v2/staging/body_role/phase4/body_role_lint_report.json
Iris/build/description/v2/staging/body_role/phase4/role_check_feedback.jsonl
```

* `LAYER4_ABSORPTION` must be verified as an active rule in `structural_rules.json`.
* `current_measurement_corpus` membership is equivalent to membership in the actual body-role `LAYER4_ABSORPTION` lint substrate. A report, doc, staging packet, diagnostic output, or generated summary that references the substrate is not itself a substrate member.
* `layer4_boundary_lint_substrate_anchor.json` is the single source of truth for `lint_substrate_member`. Inventory records may carry the field, but classification must consume the anchor rather than infer substrate membership from lexical references.
* If `lint_substrate_member = true`, the row's `primary_class` is `current_measurement_corpus`. Any fixture, staging, diagnostic, or historical nature is recorded only as `secondary_tags`.
* `Iris/build/description/v2/output/dvf_3_3_rendered.json` has known dual-role risk. `docs/DECISIONS.md` 2026-04-04 style runtime closeout and `docs/Iris/Done/dvf_3_3_body_closeout.md` distinguish this path as a fixture while treating `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json` as authoritative full rendered. If the substrate anchor proves `output/dvf_3_3_rendered.json` is the body-role lint substrate input, this round's focal role for that path is `primary_class = current_measurement_corpus` and any fixture lineage is only a secondary tag. If the actual lint substrate is another rendered artifact, this path remains `primary_class = test_fixture` or another excluded class, and the delta must be recorded in the substrate anchor rationale.
* If the execution cannot prove the actual current lint substrate, closeout must be `blocked_with_layer4_corpus_basis_unstable`.
* Lexical scan role is `diagnostic_discovery_only`.
* Measurement corpus role is `substrate_anchored`.

Token and matching assumptions:

```text
canonical_reason_code = LAYER4_ABSORPTION
LAYER4_ABSORPTION_CONFIRMED_literal_status = actual_literal | synthetic_measurement_label
matching_semantics = case_insensitive_substring_with_separator_variants
separator_variants = [_\-\s]
lexical_scan_role = diagnostic_discovery_only
```

Token tiering assumptions:

```text
primary_reason_code_tokens =
  LAYER4_ABSORPTION
  LAYER4_ABSORPTION_CONFIRMED
  L4_ABSORPTION

canonical_variant_tokens =
  layer4_absorption
  layer4_absorption_confirmed
  Layer4 Absorption
  Layer 4 Absorption
  absorption_confirmed

broad_context_tokens =
  Layer4
  layer4
  Layer 4
  absorption
  hard_block
  boundary
```

Broad context token scan is diagnostic-only and must be bounded to substrate/known-surface roots or require co-occurrence with a primary/variant token in the same file unless the scan root coverage matrix explicitly justifies broader scanning.

Classification assumptions:

```text
primary_class = exactly one
secondary_tags = zero or more
classification_precedence_applied = true
writer_input_class = forbidden_in_this_round
current_writer_candidate = diagnostic_flag_only
```

Checkout and determinism assumptions:

```text
checkout_ref = git_commit_sha + dirty_tree_state + included_surface_content_digest_manifest
dirty_tree_handling = explicit
corpus_basis_hash = required
artifact_hash_manifest = required
path_normalization = repo_relative_posix_path
path_sort = lexical_stable
locale = fixed
occurrence_id = stable_hash(path + token + line_or_offset)
json_key_order = stable
jsonl_row_order = path_then_offset
```

Template/contract assumptions:

* Execution must record `template_authority_checked = true` for `docs/PLAN_TEMPLATE.md`.
* Execution must record `execution_contract_checked = true` for `docs/EXECUTION_CONTRACT.md`.

Path assumptions:

* Repository root is `C:\Users\MW\Downloads\coding\PZ`.
* The plan artifact location follows the current repository's Iris plan-file convention and does not mean the round has executed.
* Round-local generated artifacts are placed only under the round-local artifact root.
* If shared tooling changes become necessary, execution must stop and amend scope before mutating shared tools.

Validation assumptions:

* Missing tools or blocked validation commands must be recorded as `blocked` or `not_run`, not `pass`.
* JSON / JSONL parse, partition consistency, determinism, and non-mutation evidence are required for `complete`.
* Non-mutation hash scope must be explicit:

```text
non_mutation_hash_scope =
  source facts
  source decisions
  rendered text
  runtime Lua
  packaged Lua
  bridge payload
  quality_state
  publish_state
  runtime_state
```

* Python unittest and Lua syntax validation are required only if the execution touches shared pipeline code, Lua/runtime surfaces, or wants to claim those exact surfaces by command-level validation. If this remains docs/artifact-only, non-mutation hash evidence plus diff review may satisfy the stated ceiling.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/
```

Shared repo tools are not planned mutation targets. Any need to patch shared tools requires a plan amendment or a separate implementation scope.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-layer4-boundary-current-corpus-lock-round-plan.md
```

Potential additive docs candidate after hard gate:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/docs_addendum_candidate.md
```

Potential live governance docs only after gated promotion:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

### Config

None expected.

### Generated Artifacts

Round-local generated artifacts may be created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/
```

Expected generated artifacts:

```text
layer4_boundary_scope_statement.md
layer4_boundary_predecessor_readpoints.json
layer4_boundary_forbidden_reopen_list.json
template_contract_attestation.json
layer4_boundary_lint_substrate_anchor.json
layer4_boundary_token_form_manifest.json
layer4_boundary_matching_semantics.json
layer4_boundary_scan_root_coverage_matrix.json
layer4_boundary_scan_root_coverage_report.json
layer4_boundary_known_surface_checklist.json
layer4_boundary_deterministic_generation_rules.json
layer4_boundary_current_artifact_inventory.jsonl
layer4_boundary_inventory_summary.json
layer4_boundary_lexical_scan_diagnostic.txt
layer4_boundary_surface_classification.jsonl
layer4_boundary_classification_summary.json
layer4_corpus_partition.json
layer4_boundary_exclusion_ledger.jsonl
layer4_corpus_partition_gate_report.json
layer4_boundary_unclassified_report.json
layer4_boundary_no_inheritance_rule.md
layer4_boundary_current_corpus_manifest.json
layer4_boundary_current_corpus_manifest.sha256
layer4_boundary_checkout_basis_manifest.json
layer4_boundary_corpus_basis_hash.json
layer4_boundary_manifest_validation_report.json
layer4_boundary_preflight_report.json
layer4_boundary_manifest_update_procedure.md
layer4_boundary_closeout_validation_report.json
layer4_boundary_current_corpus_lock_closeout.md
docs_addendum_candidate.md
artifact_hash_manifest.json
```

Conditional generated artifacts:

```text
layer4_boundary_empty_corpus_rationale.md
  condition = included_corpus_count == 0

layer4_boundary_preflight_negative_tests.json
  condition = machine-enforced preflight branch is implemented

layer4_boundary_validation_side_effect_restore_report.json
  condition = validation/helper scripts regenerate rendered/runtime/package/state artifacts or otherwise create side effects
```

---

## 6. Planned Changes

### Change 1 - Scope and Readpoint Seal

Purpose:

Open the round as a corpus-lock prerequisite and prevent count, runtime mutation, publish mutation review, and closed-readpoint reopen.

Files:

```text
layer4_boundary_scope_statement.md
layer4_boundary_predecessor_readpoints.json
layer4_boundary_forbidden_reopen_list.json
template_contract_attestation.json
```

Implementation Notes:

* Record round classification:

```text
execution_scale = governance
scope_qualifier = docs_static_artifact_authority_corpus_lock
corpus_lock_only = true
count_measurement_allowed = false
source_mutation_allowed = false
rendered_mutation_allowed = false
runtime_lua_mutation_allowed = false
packaged_lua_mutation_allowed = false
state_field_mutation_allowed = false
publish_mutation_review_allowed = false
structural_signal_disposition_reopen_allowed = false
function_narrow_second_rollout_allowed = false
acq_dominant_publish_review_allowed = false
```

* Record why this is governance-scale:

```text
This round creates/seals a future measurement corpus authority and reclassifies current checkout artifact surfaces for downstream LAYER4_ABSORPTION_CONFIRMED measurement. It does not mutate runtime/source surfaces, but it touches governed authority and sealed artifact surfaces.
```

* Record predecessor readpoints as predecessor references, not current count authority.
* Record that the strongest possible success branch is corpus lock with no count inheritance.
* Record forbidden reopen items:

```text
FUNCTION_NARROW second rollout
ACQ_DOMINANT publish mutation review
structural signal disposition completion
Layer4 structural-axis redesign
runtime rollout
release readiness
```

* Verify and record planning authority references:

```text
template_authority_checked = true
execution_contract_checked = true
```

Validation:

* Scope statement exists and states no count / no runtime mutation / no publish review.
* Predecessor readpoints are separated from current deliverables.
* Forbidden reopen list exists.
* `execution_scale = governance` and `scope_qualifier = docs_static_artifact_authority_corpus_lock` are present.
* Template/contract attestation exists.
* Scope wording does not declare Layer4 measurement complete.

---

### Change 2 - Current Artifact Surface Universe Inventory

Purpose:

Enumerate the current checkout artifact universe that may contain Layer4 boundary, absorption, confirmed, or related structural signals.

Files:

```text
layer4_boundary_lint_substrate_anchor.json
layer4_boundary_token_form_manifest.json
layer4_boundary_matching_semantics.json
layer4_boundary_scan_root_coverage_matrix.json
layer4_boundary_scan_root_coverage_report.json
layer4_boundary_known_surface_checklist.json
layer4_boundary_deterministic_generation_rules.json
layer4_boundary_current_artifact_inventory.jsonl
layer4_boundary_inventory_summary.json
layer4_boundary_lexical_scan_diagnostic.txt
```

Implementation Notes:

* Before lexical scanning, generate `layer4_boundary_lint_substrate_anchor.json` that proves the body-role `LAYER4_ABSORPTION` lint's current substrate. Minimum required fields:

```text
body_role_lint_code_path
active_rule_source
active_rule_id = LAYER4_ABSORPTION
active_rule_enabled = true
rendered_path
facts_path
overlay_path
rules_path
report_output_path
feedback_output_path
lint_substrate_anchor_state = anchored | missing | unstable
measurement_corpus_role = substrate_anchored
lexical_scan_role = diagnostic_discovery_only
```

* Current code-path candidate and substrate candidates:

```text
body_role_lint_code_path = Iris/build/description/v2/tools/build/build_body_role_lint_feedback.py
rendered_path = Iris/build/description/v2/output/dvf_3_3_rendered.json
facts_path = Iris/build/description/v2/data/dvf_3_3_facts.jsonl
overlay_path = Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl
rules_path = Iris/build/description/v2/tools/style/rules/structural_rules.json
report_output_path = Iris/build/description/v2/staging/body_role/phase4/body_role_lint_report.json
feedback_output_path = Iris/build/description/v2/staging/body_role/phase4/role_check_feedback.jsonl
```

* If the actual lint substrate differs from these candidates, the execution must record the discovered substrate and explain the delta before inventory. If no substrate can be proven, close as `blocked_with_layer4_corpus_basis_unstable`.
* Define token and matching semantics before scanning. The scan uses tiered tokens:

```text
primary_reason_code_tokens:
LAYER4_ABSORPTION
LAYER4_ABSORPTION_CONFIRMED
L4_ABSORPTION

canonical_variant_tokens:
layer4_absorption
layer4_absorption_confirmed
Layer4 Absorption
Layer 4 Absorption
absorption_confirmed

broad_context_tokens:
Layer4
layer4
Layer 4
absorption
hard_block
boundary
FUNCTION_NARROW
ACQ_DOMINANT
```

* Record:

```text
LAYER4_ABSORPTION_CONFIRMED_literal_status = actual_literal | synthetic_measurement_label
matching_semantics = case_insensitive_substring_with_separator_variants
separator_variants = [_\-\s]
lexical_scan_role = diagnostic_discovery_only
broad_context_token_policy = bounded_to_substrate_or_known_surface_roots_or_requires_primary_token_cooccurrence
```

* Generate `layer4_boundary_scan_root_coverage_matrix.json` before inventory. Required fields:

```text
root_path
root_class
scan_required = true | false
scan_mode = lexical | manifest_reference | hash_reference | excluded
reason
expected_surface_types
exclusion_basis
result_count
coverage_state = covered | excluded | missing | blocked
```

* Minimum root categories:

```text
current data root
current rendered/output root
current runtime deployable root
current docs/governance root
round-local staging root
historical staging/archive root
diagnostic/report root
test fixture root
tool/script root
```

* Generate `layer4_boundary_known_surface_checklist.json` with every known surface in one of:

```text
present_in_inventory
explicitly_excluded_with_reason
missing_blocked
```

Minimum known surfaces:

```text
data-root compose output
deployable chunk authority
sprint7 authoritative rendered
output/dvf_3_3_rendered.json test fixture
body_role_lint_report.json report-only
resolver compatibility diagnostic fixture
compose_contract_migration staging dirs
historical snapshots
```

* Generate deterministic-generation rules:

```text
path_normalization = repo_relative_posix_path
path_sort = lexical_stable
locale = fixed
occurrence_id = stable_hash(path + token + line_or_offset)
json_key_order = stable
jsonl_row_order = path_then_offset
```

* Record every inventory row with:

```text
occurrence_id
path
line
token
artifact_kind
source_root
surface_role_initial
current_checkout_exists
staging
report
preview
diagnostic
historical
test_fixture
current_writer_candidate = diagnostic_flag_only
candidate_reason
lint_substrate_member = true | false
lint_substrate_member_source = layer4_boundary_lint_substrate_anchor.json
matching_rule_id
source_root_coverage_id
known_surface_checklist_id
```

* Treat repo-wide lexical scan as diagnostic input only.
* Broad context token hits are bounded diagnostic evidence and must not force inclusion if the substrate anchor says `lint_substrate_member = false`.
* Separate production/current-authority compose output, deployable chunk authority, rendered artifact, report/preview output, diagnostic fixture, staging residue, historical snapshot, and test fixture.
* Record missing referenced artifacts as missing/historical references, not current corpus.
* No row may be classified as `writer_input` in this round. A writer-looking surface is a scope-boundary event and must block or be explicitly moved to a separate round.

Validation:

* Lint substrate anchor exists and `lint_substrate_anchor_state = anchored`.
* `LAYER4_ABSORPTION` active rule is proven from `structural_rules.json`.
* Token-form manifest exists and includes canonical `LAYER4_ABSORPTION`.
* Matching semantics are recorded before scan.
* `LAYER4_ABSORPTION_CONFIRMED_literal_status` is recorded.
* Scan root coverage matrix parses.
* Scan root coverage report has `scan_root_coverage_state = complete`.
* `missing_required_root_count = 0`.
* `unjustified_excluded_root_count = 0`.
* Known-surface checklist has `known_surface_checklist_state = complete`.
* `known_surface_missing_unexplained_count = 0`.
* Deterministic generation rules are recorded.
* Inventory JSONL parses.
* Every row has path, occurrence, artifact kind, initial classification, and candidate reason.
* Every row is linked to a scan root coverage id and matching rule id.
* All required scan roots and known-surface checklist entries are covered, explicitly excluded with sealed reason, or blocked.
* Lexical scan output is labeled diagnostic and not current corpus.
* Inventory does not calculate `LAYER4_ABSORPTION_CONFIRMED` count.

---

### Change 3 - Authority-Class Mapping and Inclusion / Exclusion Partition

Purpose:

Classify inventory rows with deterministic `primary_class` and `secondary_tags`, then build the substrate-anchored current measurement corpus partition.

Files:

```text
layer4_boundary_surface_classification.jsonl
layer4_boundary_classification_summary.json
layer4_corpus_partition.json
layer4_boundary_exclusion_ledger.jsonl
```

Implementation Notes:

* Assign exactly one `primary_class` to every inventory row and zero or more `secondary_tags`:

```text
current_measurement_corpus
current_authority_reference_only
runtime_identity_reference_only
observer_only
report_only
preview_only
diagnostic_only
historical
staging_residue
test_fixture
excluded_unknown
```

* `secondary_tags` may include:

```text
staging_path
historical_reference
diagnostic_payload
report_payload
preview_payload
test_fixture_payload
runtime_identity_reference
governance_doc_reference
tooling_reference
lint_substrate_member
```

* Classification precedence:

```text
current_measurement_corpus
> current_authority_reference_only
> runtime_identity_reference_only
> observer_only
> report_only
> preview_only
> diagnostic_only
> test_fixture
> staging_residue
> historical
> excluded_unknown
```

This precedence determines `primary_class`. Any additional nature is recorded in `secondary_tags`.

* `current_measurement_corpus` is not inferred from token presence. It is exactly the set of artifacts marked as actual body-role lint substrate members by `layer4_boundary_lint_substrate_anchor.json`.
* `lint_substrate_member = true` implies `primary_class = current_measurement_corpus`.
* `lint_substrate_member = false` means the row cannot be included in `current_measurement_corpus`, even if it references `LAYER4_ABSORPTION`, `LAYER4_ABSORPTION_CONFIRMED`, or other broad context tokens.
* Reports, docs, staging packets, summaries, and diagnostics that mention the substrate are classified by their own surface role, not as substrate members.
* For `Iris/build/description/v2/output/dvf_3_3_rendered.json`, classification must record a dual-role rationale:

```text
if substrate_anchor_confirms_this_path:
  primary_class = current_measurement_corpus
  secondary_tags include test_fixture_lineage if applicable
else:
  primary_class = test_fixture or other excluded class
  substrate_delta_reason required
```

* Use the following classification questions:

```text
Does this artifact belong to the current body-role lint substrate?
Does downstream LAYER4_ABSORPTION measurement directly consume this substrate?
current checkout에 존재하는가?
default compose current path가 읽는가?
runtime deployable identity 확인용인가?
report / preview / diagnostic / test / historical / staging 목적인가?
과거 closeout trace인가, current input authority인가?
```

* `excluded_unknown` is not a success class. Any remaining `excluded_unknown` blocks complete closeout.
* Any conversion from `excluded_unknown` to a terminal class requires an explicit classification update artifact and rerun of the partition integrity gate.
* `current_writer_candidate` is a diagnostic flag only. It cannot become `primary_class = writer_input`.
* `writer_input_class = forbidden_in_this_round`.
* If a writer-looking surface is found, execution must record a scope-boundary event and close blocked or open a separate explicit round.
* If `surface_role_initial != primary_class`, a `reclassification_reason` is required.
* Excluded rows must carry a sealed-decision or architecture-anchor reason.
* Included rows must carry an inclusion reason.

Validation:

* Every inventory row has exactly one `primary_class`.
* `secondary_tags` parse passes for every row.
* `classification_precedence_applied = true`.
* `primary_class_exactly_one = true`.
* `lint_substrate_member_source = layer4_boundary_lint_substrate_anchor.json` for every row that carries `lint_substrate_member`.
* Every `lint_substrate_member = true` row has `primary_class = current_measurement_corpus`.
* Every `primary_class = current_measurement_corpus` row has `lint_substrate_member = true`.
* Substrate references where `lint_substrate_member = false` are not promoted to corpus.
* `output/dvf_3_3_rendered.json` dual-role rationale is present if that path appears in inventory or known-surface checklist.
* `unknown_count = 0`.
* `unclassified_count = 0`.
* `multi_class_count = 0`.
* `excluded_unknown_count = 0`.
* `writer_input_class_count = 0`.
* Any `current_writer_candidate = true` row has `diagnostic_flag_only = true` and blocks unless explained as non-writer.
* Every initial/final classification delta has `reclassification_reason`.
* Included and excluded path sets do not overlap.
* Diagnostic, historical, report-only, preview-only, staging residue, and test fixture rows are excluded from current measurement corpus.

---

### Change 4 - Partition Integrity Hard Gate

Purpose:

Prove the substrate anchor, root coverage, known-surface checklist, and partition are exhaustive, mutually exclusive, and deterministic before any manifest or closeout claim.

Files:

```text
layer4_corpus_partition_gate_report.json
layer4_boundary_unclassified_report.json
```

Implementation Notes:

* Validate:

```text
lint_substrate_anchor_state = anchored
scan_root_coverage_state = complete
missing_required_root_count = 0
unjustified_excluded_root_count = 0
known_surface_checklist_state = complete
known_surface_missing_unexplained_count = 0
inventory_count = classified_count
inclusion_union_exclusion = universe
inclusion_intersection_exclusion = empty
unknown_count = 0
unclassified_count = 0
multi_class_count = 0
excluded_unknown_count = 0
primary_class_exactly_one = true
secondary_tags_parse = pass
classification_precedence_applied = true
```

* If the gate fails, close as the specific blocked branch:

```text
blocked_with_layer4_surface_inventory_incomplete
blocked_with_layer4_surface_classification_unresolved
blocked_with_layer4_partition_integrity_failed
```

Validation:

* Gate report parses.
* Gate report includes the exact counts above.
* No silent pass with missing substrate, missing required roots, unknown rows, unclassified rows, multi-class rows, or `excluded_unknown` rows.
* Failure branch is specific and does not claim corpus lock.

---

### Change 5 - No-Inheritance Rule and Historical Count Demotion

Purpose:

Seal that the 2026-04-29 zero-count closeout is historical predecessor evidence only and cannot be used as current count.

Files:

```text
layer4_boundary_no_inheritance_rule.md
```

Implementation Notes:

* State the no-inheritance rule:

```text
Prior Layer4 zero-count closeout is not inherited as current measurement result.
Corpus lock does not imply LAYER4_ABSORPTION_CONFIRMED count.
An empty current_measurement_corpus set is not the same as current count 0.
```

* Record that any current count must be produced by a separate downstream remeasurement round that consumes the locked manifest or partition.
* Record that no new count is produced in this round.
* If `included_corpus_count = 0`, require `layer4_boundary_empty_corpus_rationale.md` and prohibit any count-0 claim.

Validation:

* No-inheritance rule exists in manifest / partition / closeout wording.
* Historical count is explicitly demoted to predecessor readpoint.
* Closeout claim boundary includes no-count language.
* If included corpus is empty, sealed empty-corpus rationale exists and includes `prohibit_count_0_claim = true`.

---

### Change 6 - Current Corpus Manifest and Basis Pinning

Purpose:

Create the locked current corpus manifest that downstream `LAYER4_ABSORPTION_CONFIRMED` measurement must consume.

Files:

```text
layer4_boundary_current_corpus_manifest.json
layer4_boundary_current_corpus_manifest.sha256
layer4_boundary_checkout_basis_manifest.json
layer4_boundary_corpus_basis_hash.json
layer4_boundary_manifest_validation_report.json
layer4_boundary_manifest_update_procedure.md
artifact_hash_manifest.json
```

Implementation Notes:

* Manifest must include:

```text
round_id
checkout_ref
git_commit_sha
dirty_tree_state
included_surface_content_digest_manifest
corpus_basis_hash
dirty_tree_handling
created_at
lint_substrate_anchor
matching_semantics_ref
scan_root_coverage_ref
known_surface_checklist_ref
included_surfaces
excluded_surfaces
reference_only_surfaces
runtime_identity_reference_surfaces
prohibited_surface_classes
measurement_preconditions
classification_precedence_ref
no_inheritance_rule_ref
non_claims
manifest_hash
```

* Included corpus may be empty only if the manifest clearly says that this is not a current count result.
* If included corpus is empty, the manifest must reference `layer4_boundary_empty_corpus_rationale.md`.
* Excluded surface classes must be fail-loud if a future measurement tries to consume them as count input.
* Hash manifest covers the lint substrate anchor, token/matching manifests, scan root coverage matrix/report, known-surface checklist, deterministic-generation rules, inventory, classification ledger, partition, exclusion ledger, no-inheritance rule, manifest, and gate reports.
* `checkout_ref` must be reproducible:

```text
checkout_ref = git_commit_sha + dirty_tree_state + included_surface_content_digest_manifest
dirty_tree_handling = explicit
corpus_basis_hash = required
```

* Manifest update procedure must state:

```text
manifest_update_requires:
  classification update artifact
  partition gate rerun
  manifest hash refresh
  closeout/update note
```

Validation:

* Manifest JSON parses.
* Manifest schema validation passes.
* Manifest hash file matches manifest content.
* Checkout basis manifest exists.
* Dirty tree state is explicit.
* Corpus basis hash exists and covers included surfaces.
* Included paths exist, or missing paths are explicitly blocked.
* Included and excluded paths remain mutually exclusive.
* Prohibited classes are not present in included surfaces.
* Manifest basis does not use historical staged hashes as current basis.
* Manifest references the lint substrate anchor and scan root coverage report.
* Manifest update procedure exists.

---

### Change 7 - Measurement Preflight Guard

Purpose:

Prevent downstream measurement from bypassing the locked corpus manifest or partition.

Files:

```text
layer4_boundary_preflight_report.json
```

Conditional file if machine-enforced guard is implemented:

```text
layer4_boundary_preflight_negative_tests.json
```

Optional file if machine-enforced guard is implemented:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_measurement_preflight.py
```

Implementation Notes:

* Downstream measurement must fail loud when:

```text
manifest is missing
manifest hash mismatches
measurement reads a path absent from manifest / partition
measurement reads excluded surface class as count input
repo-wide lexical scan is used as count source instead of diagnostic appendix
```

* If no preflight script is implemented in this round, closeout branch must be:

```text
closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight
```

This is the default expected branch for this corpus-lock round.

* If machine-enforced preflight is implemented and negative tests pass, closeout branch may be:

```text
closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_machine_preflight
```

* Machine-enforced preflight is optional and should not be pursued if it expands scope, pressures shared tooling, or delays corpus-lock closeout. In those cases, close with the design-preflight branch.
* If implemented, keep the script round-local unless a separate plan approves shared tooling mutation. Any desire to create shared measurement framework tooling is out of scope for this round.
* Future manifest expansion must follow `layer4_boundary_manifest_update_procedure.md`; direct manifest edits without classification update, partition gate rerun, manifest hash refresh, and update note are invalid.

Validation:

* For design-only branch, preflight report states `preflight_guard_state = not_implemented` and `machine_enforcement_claimed = false`.
* For machine branch, no-manifest negative test fails as expected.
* For machine branch, hash mismatch negative test fails as expected.
* For machine branch, excluded-class injection negative test fails as expected.
* For machine branch, included-only dry run passes.
* Report states whether preflight is design-only or machine-enforced.

---

### Change 8 - Adversarial Review, Gated Documentation Promotion, and Closeout

Purpose:

Review claim boundary, optionally promote additive docs, and close the round without count or runtime claims.

Files:

```text
layer4_boundary_closeout_validation_report.json
layer4_boundary_current_corpus_lock_closeout.md
docs_addendum_candidate.md
```

Potential live docs after hard gate only:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

* Run adversarial review before live docs promotion.
* Additive docs candidate must state:

```text
current corpus locked
no count inheritance
no LAYER4_ABSORPTION_CONFIRMED count
no runtime mutation
no publish mutation review
no release readiness
closeout_provenance = AI-assisted draft, user-curated, reviewed before promotion
```

* Existing sealed entries must not be rewritten.
* If live docs already contain equivalent wording, use no-op evidence closeout or keep the addendum as candidate only.
* Closeout must include validation ceiling:

```text
validated
out_of_scope
unvalidated_but_in_scope
```

Validation:

* Closeout validation report parses.
* Adversarial review verdict is `PASS` for success closeout.
* AI-assisted/user-curated/reviewed provenance is recorded if any promoted sealed surface uses this plan's wording.
* Additive-only diff inspection passes if live docs are touched.
* Non-claim checklist passes.
* `git diff --stat` and `git diff` show only planned files.

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
template_authority_checked = true
execution_contract_checked = true
lint_substrate_anchor_validation
LAYER4_ABSORPTION active-rule validation
token-form manifest validation
matching-semantics validation
LAYER4_ABSORPTION_CONFIRMED literal/synthetic label reconciliation
broad context token bound/co-occurrence policy validation
scan_root_coverage_matrix JSON parse
scan_root_coverage_report validation
mandatory_root_coverage_count
missing_required_root_count = 0
unjustified_excluded_root_count = 0
known_surface_checklist validation
known_surface_missing_unexplained_count = 0
manifest schema validation
manifest hash validation
checkout_ref reproducibility validation
dirty_tree_handling validation
corpus_basis_hash validation
artifact hash manifest validation
deterministic_generation_rule validation
inventory row coverage check
authority classification coverage check
primary_class_exactly_one = true
secondary_tags_parse = pass
classification_precedence_applied = true
lint_substrate_member equivalence check
substrate reference non-promotion check
output/dvf_3_3_rendered.json dual-role rationale check if present
reclassification_reason coverage check
current_writer_candidate diagnostic-flag-only check
writer_input_class_count = 0
partition integrity check
inclusion / exclusion mutual exclusivity check
unknown_count = 0 check
unclassified_count = 0 check
multi_class_count = 0 check
excluded_unknown_count = 0 check
no-inheritance rule presence check
empty-corpus rationale check if included_corpus_count = 0
excluded class non-consumption check
2-run determinism digest match for inventory / classification / partition / manifest
preflight negative tests if machine-enforced preflight is implemented
preflight design-only non-enforcement disclosure if machine preflight is not implemented
manifest update procedure validation
non-mutation hash diff for source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, quality_state, publish_state, and runtime_state when those surfaces are included in the stated ceiling
validation side-effect restore report if validation/helper scripts regenerate any rendered/runtime artifact
hard gate all_gates_pass check
```

Required Python regression validation only if shared Python tooling is changed or if closeout claims Python pipeline integrity by exact command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Success condition:

```text
exit code = 0
```

Required Lua syntax validation only if Lua/runtime surfaces are changed or if closeout claims Lua syntax validation by exact command:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Success condition:

```text
exit code = 0
```

If the exact command cannot be run, the result must be recorded as `blocked` or `not_run`, not `pass`.

If Python unittest or Lua syntax validation is skipped for a docs/static-artifact-only closeout, the closeout validation report must state the explicit skip rationale and must not claim Python pipeline or Lua syntax validation.

### Manual Validation

* Review scope statement for corpus-lock-only posture.
* Review predecessor readpoints and forbidden reopen list.
* Review execution scale declaration.
* Review template/contract attestation.
* Review lint substrate anchor against the current code path and active structural rule.
* Review `output/dvf_3_3_rendered.json` dual-role rationale if the path appears as both substrate candidate and known fixture surface.
* Review lexical scan token set before accepting inventory completeness.
* Review token tiering and broad context token bounds.
* Review matching semantics and literal/synthetic label reconciliation.
* Review scan root coverage matrix.
* Review known-surface checklist.
* Review current artifact inventory for over-inclusion and under-inclusion.
* Review sample rows for each primary class and secondary tag combination.
* Review `lint_substrate_member` equivalence with `current_measurement_corpus`.
* Review that substrate references were not promoted to corpus membership.
* Review classification precedence and reclassification reasons.
* Review exclusion ledger against sealed decision and architecture anchors.
* Review partition gate counts.
* Review no-inheritance wording for count overclaim.
* Review empty-corpus rationale if applicable.
* Review checkout basis, dirty-tree handling, corpus basis hash, and manifest hash pin.
* Review manifest update procedure.
* Review preflight guard status, especially design-only versus machine-enforced claim.
* Review closeout claim boundary and non-claims.
* Review docs addendum candidate or live-doc diff for additive-only wording.

### Validation Limits

This execution will not perform:

* `LAYER4_ABSORPTION_CONFIRMED` final count.
* Runtime rollout validation.
* Manual in-game validation.
* Multiplayer validation.
* Long-session runtime validation.
* B42 validation.
* Workshop validation.
* Release validation.
* Deployment validation.
* Browser / Wiki / Tooltip UX validation.
* Full external mod compatibility sweep.
* Source expansion validation.
* Publish mutation validation.
* Publish mutation review.
* Structural signal disposition completion validation.
* Full runtime equivalence validation beyond stated non-mutation evidence.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This is a governance-scale authority-corpus lock round. The round creates or seals a Layer4 measurement corpus boundary authority for future measurement. It does not create writer authority, publish authority, runtime authority, quality authority, or default compose authority.

### Runtime Behavior Surface

None intended. Lua runtime, packaged Lua, Browser, Wiki, Tooltip behavior, runtime chunks, and bridge payloads remain unchanged.

### Compatibility Surface

None intended for runtime compatibility. Internal workflow compatibility may be affected if a preflight guard is implemented, because future measurement must consume the locked manifest or partition.

### Sealed Artifact Surface

Touched additively. New round-local sealed artifacts may be created, including substrate anchor, root coverage, partition, manifest, and preflight evidence. Existing sealed artifacts and historical bodies are consumed read-only and must not be rewritten.

### Public-Facing Output Surface

None intended. The round does not change item description, tooltip, wiki text, Browser sorting/filtering, README public claims, Workshop status, or release posture.

---

## 9. Risk Analysis

### Architecture Risk

* Body-role lint substrate could remain unanchored, leaving the current measurement corpus token-anchored rather than substrate-anchored.
* Canonical `LAYER4_ABSORPTION` and synthetic/actual `LAYER4_ABSORPTION_CONFIRMED` semantics could be confused.
* `output/dvf_3_3_rendered.json` could be silently treated as fixture in one classifier path and substrate in another without a focal dual-role decision.
* A report or diagnostic artifact that references the lint substrate could be promoted to corpus membership if `lint_substrate_member` is inferred from text instead of the substrate anchor.
* Historical Layer4 zero-count could be misread as current count.
* Diagnostic, report-only, preview-only, staging, or test artifacts could be promoted into current measurement corpus.
* Corpus-lock gate and downstream measurement gate could collapse into one round.
* Empty included corpus could be overclaimed as current count 0.
* Structural signal, `FUNCTION_NARROW`, or `ACQ_DOMINANT` closed readpoints could be reopened by wording.
* A new machine-enforced guard could accidentally create shared tooling policy without explicit scope.

### Runtime Risk

* Expected runtime risk is none if scope is respected.
* Validation commands or helper scripts could accidentally regenerate rendered or runtime artifacts.
* Any side-effect mutation must block non-mutation closeout until restored and explained.

### Compatibility Risk

* Public or internal wording could imply compatibility preservation without compatibility testing.
* Future measurement workflows may fail if the manifest guard is too strict and no update procedure is documented.
* Excluding a legitimate current measurement input could cause downstream undercount.

### Regression Risk

* Required scan roots may be missed without root coverage evidence.
* Known surfaces may be neither inventoried nor explicitly excluded.
* Inventory may miss a current-looking surface.
* Path aliases may double-count the same artifact.
* Token search may include broad false positives or miss variants.
* Broad context tokens such as `boundary`, `absorption`, and `hard_block` may inflate diagnostic inventory if not bounded by root or co-occurrence policy.
* Authority classification may leave ambiguous rows if `primary_class` / `secondary_tags` precedence is not applied.
* Exclusion reasons may lack sealed authority.
* Preflight guard may be claimed as implemented when it is only documented.
* Docs promotion may duplicate existing current readpoint wording.
* Dirty working tree state may make `checkout_ref` non-reproducible if not recorded.
* 2-run determinism may be meaningless if path ordering, occurrence id, and JSON key order are not fixed.
* Missing validation tools may be misreported as pass.

---

## 10. Rollback Plan

Rollback is docs/artifact rollback, not runtime rollback.

1. Review touched files with:

```powershell
git diff --stat
git diff
```

2. Remove or quarantine only artifacts created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/
```

3. If optional round-local helper scripts were created and are invalid, remove or quarantine only those helper scripts.

4. If shared tooling was changed without an approved scope amendment, stop and revert only changes made by this round after identifying them.

5. If `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` receive invalid additive wording, correct with additive clarification when possible. If duplicate text was added by this round, remove only that duplicate addition.

6. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` changed unexpectedly, stop and identify the exact source of mutation before reverting only this round's changes.

7. If validation commands regenerate output as side effects, restore the pre-validation frozen snapshot and rerun non-mutation hash diff before making any non-mutation claim.

8. If inventory, classification, partition, or manifest validation fails, close with the specific blocked branch instead of rewriting the claim boundary into success.

9. If a sealed closeout later proves incorrect, do not rewrite the sealed body directly. Add a later correction or supersession artifact.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains a wiki-style information module: no interpretation, recommendation, comparison, or gameplay policy expansion.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation must remain intact.
* This round is governance-scale and must be reported as an authority/sealed-artifact surface touch.
* Current measurement corpus authority must not become writer authority.
* Default compose current authority remains under `Iris/build/description/v2/data/`.
* Body-role `LAYER4_ABSORPTION` lint substrate must be anchored before current measurement corpus is defined.
* Lexical scan remains diagnostic discovery only.
* Current measurement corpus must be substrate-anchored.
* `current_measurement_corpus` membership is equivalent to actual body-role lint substrate membership, as sealed by `layer4_boundary_lint_substrate_anchor.json`.
* Artifacts that reference or report on the substrate are not substrate members by reference alone.
* `output/dvf_3_3_rendered.json` dual-role handling must be explicitly recorded if it appears as both body-role lint substrate candidate and known fixture surface.
* Canonical reason code `LAYER4_ABSORPTION` and `LAYER4_ABSORPTION_CONFIRMED` label status must be reconciled before inventory closeout.
* Broad context token scanning must be bounded by root or primary-token co-occurrence policy.
* Scan root coverage matrix and known-surface checklist must pass before inventory completeness is claimed.
* Classification must use exactly one `primary_class` and zero or more `secondary_tags`.
* Classification precedence and reclassification reasons must be recorded.
* `current_writer_candidate` is diagnostic flag-only.
* `writer_input_class` is forbidden in this round.
* Historical, diagnostic, report-only, preview-only, staging, and test surfaces must not be promoted to current writer input.
* Prior zero-count closeout must not be inherited as current count.
* Empty included corpus must not be claimed as count 0.
* Empty included corpus requires sealed empty-corpus rationale.
* Checkout reference must include git commit, dirty tree state, and included surface digest manifest.
* Deterministic generation rules must be recorded before 2-run determinism can be claimed.
* `FUNCTION_NARROW` second rollout remains forbidden.
* `ACQ_DOMINANT` publish mutation review remains closed unless a separate explicit round opens it.
* Structural signal disposition completion remains out of scope.
* Publish mutation review is forbidden inside this corpus-lock round.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, and state fields remain non-mutation targets.
* Existing sealed artifacts are consumed read-only.
* Missing, unknown, or unclassified surface evidence must block rather than silently pass.
* Missing required scan root, unjustified excluded root, known-surface unexplained miss, or `excluded_unknown_count > 0` must block complete closeout.
* Validation may not be claimed as passed unless the exact relevant command exits with code `0`.
* Conditional artifacts must be generated only when their condition is met; absence of `layer4_boundary_validation_side_effect_restore_report.json` is acceptable when no side effect occurred and the closeout says so.
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

`partial` and `implemented_only` are not planned sealed success states for this corpus-lock round. `complete` is valid only within the validation ceiling stated in this plan and only if:

```text
scope statement exists
execution_scale = governance
scope_qualifier = docs_static_artifact_authority_corpus_lock
template_authority_checked = true
execution_contract_checked = true
predecessor readpoints are separated from current deliverables
forbidden reopen list exists
lint_substrate_anchor_state = anchored
LAYER4_ABSORPTION active rule is verified
canonical token / matching semantics are recorded
LAYER4_ABSORPTION_CONFIRMED literal/synthetic label status is reconciled
broad context token policy is bounded
scan_root_coverage_state = complete
missing_required_root_count = 0
unjustified_excluded_root_count = 0
known_surface_checklist_state = complete
known_surface_missing_unexplained_count = 0
current artifact inventory exists
surface classification ledger exists
exclusion ledger exists
partition exists
primary_class_exactly_one = true
secondary_tags_parse = pass
classification_precedence_applied = true
lint_substrate_member equivalence passes
substrate reference non-promotion check passes
output/dvf_3_3_rendered.json dual-role rationale exists if applicable
writer_input_class_count = 0
current_writer_candidate is diagnostic_flag_only
reclassification_reason coverage passes
unknown_count = 0
unclassified_count = 0
multi_class_count = 0
excluded_unknown_count = 0
partition integrity passes
no-inheritance rule exists
empty-corpus rationale exists if included_corpus_count = 0
current corpus manifest exists
checkout_ref = git_commit_sha + dirty_tree_state + included_surface_content_digest_manifest
dirty_tree_handling is explicit
corpus_basis_hash exists
manifest hash validates
manifest validation passes
preflight status is accurately reported as design-only or machine-enforced
required preflight tests pass if machine enforcement is claimed
non-mutation evidence passes for every surface included in the stated ceiling
JSON/JSONL parse passes
2-run determinism passes for generated inventory / classification / partition / manifest
hard gate all_gates_pass = true
closeout non-claims are explicit
claim boundary does not exceed corpus lock
```

Expected complete branch:

```text
contract_closeout_state = complete
branch_closeout =
  closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight
  | closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_machine_preflight
```

Default expected complete branch:

```text
closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight
```

The machine-preflight branch is optional and should be used only if round-local implementation and negative tests are completed without shared-tooling scope expansion.

Expected final claim boundary:

```text
Current checkout 기준으로 LAYER4_ABSORPTION_CONFIRMED 후속 측정에 사용할 artifact universe,
current measurement corpus, excluded surface classes, no-inheritance rule,
and manifest / partition prerequisite were locked.
```

Expected non-claims:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출 아님
Layer4 absorption resolved 아님
Layer4 policy redesign 아님
structural signal disposition completion 아님
FUNCTION_NARROW second rollout 아님
ACQ_DOMINANT publish review 아님
publish mutation review 아님
source/rendered/runtime mutation 아님
runtime rollout 아님
manual in-game validation pass 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
```
