# Iris DVF 3-3 Layer4 Confirmed Detector Field Map Seal Round Plan

> 상태: Draft v0.3-conditional-pass-applied
> 기준일: 2026-05-31
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP — Iris DVF 3-3 Layer4 Confirmed Detector Field Map Seal Round` (2026-05-31 user-provided synthesis)
> review input: `REVIEW — Iris DVF 3-3 Layer4 Confirmed Detector Field Map Seal Round` (2026-05-31 user-provided synthesis), WARN with Critical 1, Major 1, Important 4, Minor 6 incorporated in v0.2; Conditional PASS with Critical 0, Important 1, Minor 4 incorporated in v0.3 by removing the no-readable-edge-zero occurrence branch and live-corpus occurrence count path.
> 직접 상위 readpoint:
> - 2026-04-29 Layer4 Absorption Policy Round predecessor zero-count: historical only, no current count inheritance
> - 2026-05-29 Structural Signal Scope Split Seal Round `closed_with_structural_signal_scope_split_sealed_observer_only`
> - 2026-05-29 Structural Signal Authority Classification Round `closed_with_structural_signal_authority_classification_sealed`
> - 2026-05-29 Structural Signal Current Readpoint Seal Round `closed_with_structural_signal_current_readpoint_doc_absorption_only`
> - 2026-05-30 ACQ_DOMINANT Current Baseline Remeasurement Round `closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate`
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> contract vocabulary: `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.
> execution_scale: `governance`
> scope_qualifier: `docs_static_artifact_detector_field_map_seal`
> 실행 상태: planning authority only. This document opens no `LAYER4_ABSORPTION_CONFIRMED` count, runtime mutation, publish mutation review, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 current corpus 안에서 `LAYER4_ABSORPTION_CONFIRMED` detector가 실제로 읽을 수 있는 Layer4 source object to Layer3 body slot trace edge field map을 확인하고, count 산출 이전의 detector-readiness / field-map / trace-edge 판정 권한을 봉인하는 것이다.

이번 round가 답해야 하는 질문은 다음으로 제한한다.

```text
current measurement corpus 4개 path 안에
Layer4 source object identity/path/type,
Layer3 target row/item/body slot/body section,
그리고 source -> target explicit trace edge를 detector가 읽을 수 있는 canonical field map이 있는가?

없거나 모호하다면,
count를 산출하지 않고 어떤 unavailable / blocked branch로 닫아야 하는가?
```

Round id:

```text
layer4_confirmed_detector_field_map_seal_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/
```

Closeout branch taxonomy:

```text
complete_success:
  closed_with_layer4_confirmed_detector_field_map_sealed

complete_negative_seal:
  closed_with_confirmed_measurement_unavailable_trace_absent

blocked:
  blocked_with_trace_fields_present_but_ambiguous_detector_blocked
  blocked_with_anchor_required
  blocked_with_definition_referent_missing
  blocked_with_detector_field_requirement_unsealed
  blocked_with_current_corpus_schema_inventory_incomplete
  blocked_with_trace_candidate_classification_incomplete
  blocked_with_field_to_requirement_mapping_incomplete
  blocked_with_manifest_validation_failed
  blocked_with_no_count_guard_failed
  blocked_with_review_gate_failed
  blocked_with_non_mutation_invariant_failed
  blocked_with_validation_failed
  blocked_with_claim_overreach
```

Closeout records must separate `docs/EXECUTION_CONTRACT.md` state from branch label:

```text
contract_closeout_state = complete | blocked

branch_closeout =
  closed_with_layer4_confirmed_detector_field_map_sealed
  | closed_with_confirmed_measurement_unavailable_trace_absent
  | blocked_with_trace_fields_present_but_ambiguous_detector_blocked
  | blocked_with_anchor_required
  | blocked_with_definition_referent_missing
  | blocked_with_detector_field_requirement_unsealed
  | blocked_with_current_corpus_schema_inventory_incomplete
  | blocked_with_trace_candidate_classification_incomplete
  | blocked_with_field_to_requirement_mapping_incomplete
  | blocked_with_manifest_validation_failed
  | blocked_with_no_count_guard_failed
  | blocked_with_review_gate_failed
  | blocked_with_non_mutation_invariant_failed
  | blocked_with_validation_failed
  | blocked_with_claim_overreach
```

Success may claim only:

```text
Current locked corpus 기준으로 LAYER4_ABSORPTION_CONFIRMED detector가 사용할 수 있는
field map이 sealed 되었거나, trace edge field 부재로 confirmed measurement unavailable이 sealed 되었다.
Field-map sealed branch는 occurrence 수와 무관하게 downstream count round로 handoff한다.
Ambiguous trace fields are blocked, not complete success.
```

Success must not claim:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출
live-corpus occurrence count 산출
zero-occurrence closeout
Layer4 absorption resolved
Layer4 policy redesign
SUSPECT tier coverage
source facts mutation
source decisions mutation
rendered text mutation
runtime Lua mutation
packaged Lua mutation
bridge payload mutation
quality_state mutation
publish_state mutation
runtime_state mutation
Browser / Wiki / Tooltip behavior change
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

This is a governance-scale docs/static-artifact detector field-map seal round. It consumes the 2026-05-31 current corpus lock read-only and decides whether a confirmed detector has a hash-stable field contract for a later count round.

In scope:

* Phase 0 definition referent verification before any detector field requirement is pinned.
* Identification of the sealed `LAYER4_ABSORPTION_CONFIRMED` definition surface from canonical docs, archived addendum, VCS history, or prior round staging artifact.
* Definition referent sha256 / commit / readpoint pinning, including a check that source object to body slot edge granularity is actually sealed.
* Fixed consumption of the current measurement corpus locked by the previous round:

```text
Iris/build/description/v2/data/dvf_3_3_facts.jsonl
Iris/build/description/v2/output/dvf_3_3_rendered.json
Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl
Iris/build/description/v2/tools/style/rules/structural_rules.json
```

* Physical path pin for the locked corpus under repository root `C:\Users\MW\Downloads\coding\PZ`:

```text
C:\Users\MW\Downloads\coding\PZ\Iris\build\description\v2\data\dvf_3_3_facts.jsonl
C:\Users\MW\Downloads\coding\PZ\Iris\build\description\v2\output\dvf_3_3_rendered.json
C:\Users\MW\Downloads\coding\PZ\Iris\build\description\v2\staging\body_role\phase2\layer3_role_check_overlay.jsonl
C:\Users\MW\Downloads\coding\PZ\Iris\build\description\v2\tools\style\rules\structural_rules.json
```

* Manifest sha256 read-only verification:

```text
d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402
```

* Detector field requirement spec for `LAYER4_ABSORPTION_CONFIRMED`.
* Full schema and field-path inventory for the locked corpus. This field-level inventory consumes the prior corpus membership lock and does not rederive corpus membership classification.
* Candidate classification for source object fields, target body slot fields, explicit trace edge fields, forbidden fields, and ambiguous fields.
* Nested array/object traversal and stringified JSON candidate detection for false-absence prevention.
* Edge semantics seal for confirmed true conditions.
* Field-to-requirement mapping and named branch determination.
* Branch alias mapping for any shorthand used by review or closeout:

```text
Branch A = complete_success / FIELD_MAP_SEALED
Branch B = complete_negative_seal / TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE
Branch C = blocked ambiguous disposition / TRACE_EDGE_FIELDS_PRESENT_BUT_AMBIGUOUS
```

* Detector field map manifest or blocked/unavailable manifest.
* No-count guard evidence.
* Optional schema/synthetic-fixture readiness harness only if Branch A field map is sealed. This harness must not scan live corpus rows for occurrence counts.
* Branch A handoff to a separate downstream authoritative count round. This round must not seal live-corpus occurrence counts.
* Branch B downstream count round disposition as one of `cancelled`, `not_applicable_under_current_corpus`, or `redefined_as_future_anchor_or_definition_round` before any count claim is opened.
* Branch C handling only as an approved blocked disposition. If not approved, ambiguous cases block execution rather than becoming a completed outcome.
* Adversarial review and hard gate before any live canonical doc promotion.
* Staged seal draft for `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.
* Single-phase gated promotion only after review PASS.

### Explicitly Out Of Scope

* `LAYER4_ABSORPTION_CONFIRMED` current count.
* Live-corpus occurrence count under any branch.
* SUSPECT tier design or detection.
* `LAYER4_ABSORPTION_CONFIRMED` definition redesign.
* Defining `LAYER4_ABSORPTION_CONFIRMED` in this round if no sealed definition referent exists.
* Layer4 policy redesign.
* Layer4 absorption resolved declaration.
* Layer4 source absorption into Layer3 by publish mutation.
* Layer3 body rewrite.
* Body recompose.
* Source expansion.
* `FUNCTION_NARROW` or `ACQ_DOMINANT` reopen.
* Structural signal classification rerun.
* Adding new absorption-trace fields to source/rendered/body artifacts to resolve Branch B.
* Machine-enforced preflight implementation unless explicitly added as round-local scope.
* Runtime Lua regeneration.
* Packaged Lua regeneration.
* Browser / Wiki / Tooltip behavior change.
* Manual in-game validation.
* Multiplayer validation.
* Long-session runtime validation.
* Deployment / Workshop / B42 / release readiness.
* Historical, diagnostic, report-only, preview-only, staging residue, or test fixture promotion to current detector authority.
* Repository-wide machine-enforced preflight claim from a round-local readiness harness.

---

## 3. Non-Goals

This plan does not attempt to:

* Infer confirmed status from text similarity, expression pattern, keyword residue, body text substring, or section labels.
* Treat category tags, `cluster_summary`, diagnostic provenance, report provenance, or preview fields as trace edges.
* Treat source object and target body slot co-occurrence in the same row as an explicit edge by itself.
* Collapse ambiguous edge candidates into FIELD-MAP-SEALED.
* Collapse absent trace edges into Layer4 absorption resolved.
* Treat trace absence as proof that real Layer4 absorption is 0.
* Inherit the 2026-04-29 zero-count as a current measurement.
* Mutate source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state`.
* Produce live-corpus occurrence counts such as readable trace edge count, confirmed candidate count, or rejected fallback counts.
* Seal zero occurrences as a current confirmed count or as a substitute for a downstream count round.
* Add new absorption-trace fields to source/rendered/body artifacts in order to make Branch B countable.
* Resolve Branch B by promoting Layer4 absorption into a structural axis.
* Claim machine-enforced guard coverage if the round only produces a design/spec guard.
* Claim repository-wide preflight enforcement from a round-local readiness harness.
* Promote staging outputs into live canonical docs before review PASS and hard gate.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style information module and must not become a recommendation, comparison, interpretation, or gameplay-policy system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints at execution start.
* `LAYER4_ABSORPTION_CONFIRMED` trace-edge definition is not assumed as usable until Phase 0 identifies and pins the sealed definition referent.
* If no sealed definition referent is found, or if the referent lacks source object to body slot edge granularity, the round must block with `blocked_with_definition_referent_missing` or `blocked_with_detector_field_requirement_unsealed` rather than inventing a definition.
* SUSPECT tier is outside this scope.
* 2026-04-29 Layer4 zero-count is historical predecessor only and must not be inherited as current count.
* 2026-05-31 Layer4 Boundary Current Corpus Lock Round locked the current measurement corpus and excluded surface classes, but did not seal a field-level detector contract or count.
* Current corpus inputs are read-only and limited to the 4 locked paths.
* Excluded surface count remains `460` and must not be promoted into detector authority.
* `included_corpus_count = 4`, `inventory_count = 21914`, and `classified_count = 21914` are predecessor readpoints to verify, not new count claims.
* `preflight_guard_state = not_implemented` and `machine_enforcement_claimed = false` remain true unless this round explicitly implements and validates a machine guard.

Detector assumptions:

* `confirmed` true requires explicit Layer4 source object to Layer3 body slot trace edge.
* Detector-readable field requirements must distinguish required, optional, forbidden, missing, malformed, and ambiguous behavior.
* Missing required field must fail loud or route to unavailable/blocked branch.
* Ambiguous edge-like fields must route to Branch C rather than forced A/B disposition.
* Trace edge field absence routes to `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE`.
* Field-map sealed status is occurrence-count independent. If a field map is sealed, authoritative occurrence counting is handed off to a separate downstream count round.
* Branch B must include downstream count round disposition: `cancelled`, `not_applicable_under_current_corpus`, or `redefined_as_future_anchor_or_definition_round`.
* Branch C is active only as an approved blocked disposition. Ambiguous fields do not become complete success.

Checkout and determinism assumptions:

```text
checkout_ref = git_commit_sha + dirty_tree_state + included_surface_content_digest_manifest
path_normalization = repo_relative_posix_path
path_sort = lexical_stable
json_key_order = stable
jsonl_row_order = path_then_offset
field_path_order = lexical_stable
occurrence_id = stable_hash(path + field_path + row_or_offset + value_shape)
value_shape_traversal = nested arrays and nested objects traversed
stringified_json_candidate_detection = required
unsupported_value_shape_count = recorded
```

Template/contract assumptions:

* Execution must record `template_authority_checked = true` for `docs/PLAN_TEMPLATE.md`.
* Execution must record `execution_contract_checked = true` for `docs/EXECUTION_CONTRACT.md`.
* `docs/PLAN_TEMPLATE.md` is treated as the recognized workspace execution-plan form for this task because the session instructions require it. It is a form, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
* `docs/EXECUTION_CONTRACT.md` is treated as the recognized workspace execution disclosure/evidence/closeout contract for this task. It constrains reporting and closeout discipline, but does not create module policy or override higher authority documents.
* Missing tools or blocked validation commands must be recorded as `blocked` or `not_run`, not `pass`.

Path assumptions:

* Repository root is `C:\Users\MW\Downloads\coding\PZ`.
* This plan artifact location follows the current repository's Iris active-plan convention and does not mean the round has executed.
* Round-local generated artifacts are placed only under the round-local artifact root.
* Shared repo tools are not planned mutation targets. Any need to patch shared tools requires a plan amendment or separate implementation scope.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/
```

Shared tools are not planned mutation targets.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-layer4-confirmed-detector-field-map-seal-round-plan.md
```

Potential staged docs candidate after hard gate:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/docs_addendum_candidate.md
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
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/
```

Expected generated artifacts:

```text
layer4_confirmed_definition_referent_verification.md
layer4_confirmed_definition_referent_pin.json
layer4_confirmed_authority_input_lock.md
layer4_confirmed_corpus_physical_path_pin.json
layer4_confirmed_detector_field_requirement.md
layer4_confirmed_corpus_field_inventory.json
layer4_confirmed_corpus_field_inventory.summary.json
layer4_confirmed_trace_candidate_classification.jsonl
layer4_confirmed_trace_candidate_classification.summary.json
layer4_confirmed_readable_field_manifest.json
layer4_confirmed_forbidden_field_manifest.json
layer4_confirmed_ambiguous_field_manifest.json
layer4_confirmed_edge_semantics_seal.md
layer4_confirmed_field_to_requirement_mapping.json
layer4_confirmed_branch_taxonomy_manifest.json
layer4_confirmed_branch_determination.md
layer4_confirmed_detector_field_map_manifest.json
layer4_confirmed_detector_field_map_manifest.sha256
layer4_confirmed_blocked_or_unavailable_manifest.json
layer4_confirmed_downstream_count_round_disposition.json
layer4_confirmed_no_count_guard_evidence.json
layer4_confirmed_synthetic_fixture_readiness_probe_report.json
layer4_confirmed_review_report.md
layer4_confirmed_staged_seal_packet.md
layer4_confirmed_evidence_capsule.md
layer4_confirmed_closeout_validation_report.json
artifact_hash_manifest.json
docs_addendum_candidate.md
```

Conditional generated artifacts:

```text
layer4_confirmed_trace_absent_unavailable_rationale.md
  condition = detector_closeout_branch == TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE

layer4_confirmed_ambiguous_detector_blocked_rationale.md
  condition = detector_closeout_branch == blocked_with_trace_fields_present_but_ambiguous_detector_blocked

layer4_confirmed_blocked_anchor_required_rationale.md
  condition = detector_closeout_branch == blocked_with_anchor_required
```

---

## 6. Planned Changes

### Change 0 — CONFIRMED Definition Referent Verification

Purpose:

Verify the sealed referent for the trace-edge `LAYER4_ABSORPTION_CONFIRMED` definition before any detector field requirement is derived.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_definition_referent_verification.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_definition_referent_pin.json
```

Implementation Notes:

* Search canonical `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, archived addenda, VCS history, and corpus-lock staging outputs for the sealed definition referent.
* Pin the accepted referent by sha256, commit/readpoint, path, and section if found.
* Verify that the definition body includes explicit Layer4 source object to Layer3 body slot trace-edge granularity.
* If the referent is absent, ambiguous, or lacks edge granularity, block with `blocked_with_definition_referent_missing` or `blocked_with_detector_field_requirement_unsealed`.
* This change may not create or redefine the `LAYER4_ABSORPTION_CONFIRMED` definition.

Validation:

* `definition_referent_gate_pass` is true before Change 1 runs.
* Accepted definition referent path/readpoint/hash is recorded.
* Edge granularity check passes.
* Missing referent routes to blocked branch, not field requirement derivation.

---

### Change 1 — Authority / Input Lock and Detector Definition Contract Pin

Purpose:

Fix the round input authority and express the Phase 0-verified sealed `LAYER4_ABSORPTION_CONFIRMED` definition as a minimal detector field requirement without redefining the concept.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_authority_input_lock.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_corpus_physical_path_pin.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_detector_field_requirement.md
```

Implementation Notes:

* Pin the 4 locked corpus paths as the only detector input universe.
* Pin repository-relative and physical absolute paths for the 4 locked corpus paths.
* Reconfirm predecessor manifest sha256.
* Record historical zero-count no-inheritance.
* Record `confirmed definition referent verified / SUSPECT out of scope`.
* State that this round is field-map readiness only, not count.

Validation:

* Input manifest hash matches the predecessor readpoint.
* Included corpus count remains `4`.
* Excluded surface count remains `460`.
* Physical path pin resolves under repository root.
* Corpus outside the 4 locked paths is not consumed as detector authority.
* Count / policy / SUSPECT scope leak count is `0`.

---

### Change 2 — Locked Corpus Schema / Field Inventory

Purpose:

Inventory actual field names, nested paths, row/object schemas, list element schemas, occurrence counts, and value shapes inside the locked corpus. This change consumes the already-locked corpus membership and does not rederive or reopen corpus membership classification.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_corpus_field_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_corpus_field_inventory.summary.json
```

Implementation Notes:

* Record top-level and nested field paths for every included file.
* Traverse nested arrays and nested objects.
* Detect stringified JSON candidates and record whether they were parsed, rejected, or unsupported.
* Group candidate fields using terms such as `layer4`, `source`, `source_object`, `trace`, `edge`, `slot`, `body_slot`, `section`, `body_plan`, `layer3`, `origin`, and `provenance`.
* Record field path, occurrence count, value shape, nesting shape, and file/path provenance.
* Record `unsupported_value_shape_count`.
* Separate category tags and diagnostic labels from possible edge fields.

Validation:

* All included corpus rows/objects parse successfully.
* Malformed JSON/JSONL count is `0`.
* Unknown schema path count is `0`.
* `nested_array_object_traversal_check` passes.
* `stringified_json_candidate_detection_check` passes.
* `unsupported_value_shape_count` is recorded.
* Field path inventory is generated deterministically.
* 2-run inventory digest matches.
* Corpus outside the locked 4 paths is not read as authority.

---

### Change 3 — Trace Candidate Classification

Purpose:

Classify field paths into detector-readable candidates, detector-forbidden fields, ambiguous fields, and non-trace fields.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_trace_candidate_classification.jsonl
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_trace_candidate_classification.summary.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_readable_field_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_forbidden_field_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_ambiguous_field_manifest.json
```

Implementation Notes:

Candidate classes:

```text
source_object_identity
source_object_path
source_object_type
layer3_target_identity
layer3_body_slot
explicit_trace_edge
body_text_only
category_tag_only
diagnostic_only
historical_only
report_only
preview_only
ambiguous
non_trace
```

Classification rules:

* `body_text_only` is never confirmed evidence.
* `cluster_summary` or any category tag is not a trace edge by itself.
* Section label only is not an edge.
* Diagnostic/report provenance is not detector authority.
* Source object and target slot co-occurrence alone is not an explicit edge.

Validation:

* Every candidate field receives exactly one classification.
* Ambiguous field count and reason are recorded.
* Readable / forbidden / ambiguous manifests parse.
* Forbidden classes have explicit detector non-consumption rules.
* Classification exhaustiveness check passes.

---

### Change 4 — Edge Semantics Seal and Field-to-Requirement Mapping

Purpose:

Seal the minimum edge semantics that can make confirmed true and map the inventory/classification results to the detector field requirement.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_edge_semantics_seal.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_field_to_requirement_mapping.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_branch_determination.md
```

Implementation Notes:

Confirmed edge minimum:

```text
source side:
  Layer4 source object id or equivalent stable identity
  source artifact/path/class/type traceability

target side:
  Layer3 row/item identity
  Layer3 body slot or body_plan section

edge side:
  field structure expresses source -> target relation
  co-occurrence is insufficient
  optional edge fields have explicit missing behavior

disallowed:
  text similarity
  keyword match
  body text substring
  section label only
  category tag only
  diagnostic/report flag only
```

Validation:

* All candidate fields are mapped or explicitly rejected.
* Source-only / target-only / text-only / diagnostic-only / category-tag-only fixtures evaluate false.
* Ambiguous edge candidates route to fail-loud or an approved blocked Branch C disposition.
* Two independent static sub-checks are recorded separately:
  * static field-presence gate
  * static per-row edge-readability gate
* This does not claim runtime dual-zero validation.
* The static per-row edge-readability gate is fixture/schema based and does not count live corpus occurrences.

---

### Change 5 — Detector Field Map Manifest / Branch Determination

Purpose:

Seal either the canonical detector field map or a blocked/unavailable disposition manifest.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_detector_field_map_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_detector_field_map_manifest.sha256
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_blocked_or_unavailable_manifest.json
```

Implementation Notes:

Manifest fields:

```text
field_map_version
input_manifest_sha256
included_corpus_paths
source_object_identity_fields
source_object_path_fields
source_object_type_fields
target_row_identity_fields
target_body_slot_fields
explicit_trace_edge_fields
required_fields
optional_fields
forbidden_fields
missing_field_behavior
ambiguous_field_behavior
detector_closeout_branch
```

Allowed branch family:

```text
complete_success:
  FIELD_MAP_SEALED

complete_negative_seal:
  TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE

blocked:
  TRACE_EDGE_FIELDS_PRESENT_BUT_AMBIGUOUS
  BLOCKED_ANCHOR
  DEFINITION_REFERENT_MISSING
  FIELD_MAP_REJECTED_TEXT_ONLY
  FIELD_MAP_REJECTED_DIAGNOSTIC_ONLY
```

Validation:

* Manifest schema validation passes.
* Required field absence behavior is tested.
* Forbidden field consumption check passes.
* 2-run manifest hash matches.
* Branch decision matches field mapping report.
* `branch_taxonomy_consistency_check` passes.
* `branch_alias_to_named_taxonomy_mapping_check` passes.
* `complete_vs_blocked_closeout_state_consistency_check` passes.
* Branch A always hands off to a downstream authoritative count round; this round does not inspect or seal live-corpus occurrence counts.
* If Branch B is selected, downstream count round disposition is recorded before any count claim is opened.

---

### Change 6 — Schema / Synthetic Fixture Readiness Probe and No-Count Guard

Purpose:

Allow only schema/synthetic-fixture readiness probing when Branch A is sealed, and otherwise block count output with an unavailable/blocked artifact.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_no_count_guard_evidence.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_synthetic_fixture_readiness_probe_report.json
```

Implementation Notes:

* Branch A may allow a schema/synthetic-fixture readiness probe.
* Branch B/C must skip detector count and produce unavailable/blocked closeout evidence.
* The readiness probe may use synthetic positive/negative fixtures or schema-level checks only.
* The readiness probe must not scan live corpus rows for occurrence counts.
* The primary round claim remains field-map readiness.
* No-count guard must prevent text-only, diagnostic-only, and category-tag-only fallback.
* If a round-local readiness harness is created, it must fail without a sealed field map.
* A round-local readiness harness does not imply repository-wide machine-enforced preflight unless separately scoped and validated.

Readiness probe report fields, if applicable:

```text
fixture_case_count
positive_fixture_pass
source_only_fixture_rejected
target_only_fixture_rejected
text_only_fixture_rejected
category_tag_only_fixture_rejected
diagnostic_only_fixture_rejected
ambiguous_fixture_routes_to_blocked
live_corpus_occurrence_count_performed = false
readiness_probe_exit_branch
```

Validation:

* Round-local readiness harness execution fails without a sealed field map, if such a harness exists.
* Text-only fallback fixture is rejected.
* Diagnostic-only fallback fixture is rejected.
* Category-tag-only fallback fixture is rejected.
* `live_corpus_occurrence_count_performed = false`.
* Readiness probe result branch matches manifest branch.
* Source/rendered/runtime/state hash delta is `0`.

---

### Change 7 — Adversarial Review / Hard Gate

Purpose:

Review Change 0 through Change 6 outputs before any live governance doc promotion.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_review_report.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_closeout_validation_report.json
```

Implementation Notes:

* Use `docs/REVIEW_TEMPLATE.md` 12-section structure: Verdict, Executive Summary, Critical Issues, Non-Critical Issues, Scope Review, Validation Review, Governance Review, Risk Surface Review, Risk Review, Required Revisions, Final Recommendation, Reviewer Notes.
* Promotion is forbidden unless review verdict is PASS or explicitly accepted Conditional PASS.
* Review must check count / policy / SUSPECT / release leakage.

Validation:

* Review issue count is recorded.
* Each issue is actionable.
* Scope self-consistency passes.
* Gating order is respected.
* Gate booleans are individually recorded:

```text
definition_referent_gate_pass
field_map_gate_pass
branch_semantics_gate_pass
schema_traversal_gate_pass
no_count_guard_pass
non_mutation_gate_pass
review_gate_pass
claim_ceiling_gate_pass
all_gates_pass
```

* `all_gates_pass = true` is allowed only if every named gate is true.

---

### Change 8 — Staged Seal Draft

Purpose:

Prepare branch-specific closeout wording and canonical doc update candidates in staging only.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_staged_seal_packet.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/layer4_confirmed_evidence_capsule.md
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/docs_addendum_candidate.md
```

Implementation Notes:

* Draft DECISIONS closeout entry.
* Draft ARCHITECTURE additive facts / evidence capsule.
* Draft ROADMAP status update.
* Include AI-assisted provenance if promoted wording comes from this plan or generated artifacts.
* Record provenance fields in the staged seal packet:

```text
seal_packet.ai_assisted_origin
seal_packet.generated_by
seal_packet.reviewed_by
seal_packet.promotion_timestamp
```

* Include non-claims.

Validation:

* Staged draft branch names match manifest branch.
* Non-claims are present.
* Frozen surface hash-level non-mutation is preserved.
* Live write is not performed before review PASS.

---

### Change 9 — Gated Promotion / Closeout

Purpose:

Promote the reviewed branch outcome to live canonical docs in a single phase, if and only if hard gate permits.

Files:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

* Add dated DECISIONS closeout entry.
* Add ARCHITECTURE additive evidence capsule.
* Update ROADMAP state.
* State the final branch explicitly.
* Do not rewrite existing sealed entries except by additive clarification or supersession if needed.

Validation:

* `definition_referent_gate_pass = true`.
* `field_map_gate_pass = true` or a complete-negative/blocked branch has an explicit branch reason.
* `branch_semantics_gate_pass = true`.
* `schema_traversal_gate_pass = true`.
* `no_count_guard_pass = true`.
* `non_mutation_gate_pass = true`.
* `review_gate_pass = true`.
* `claim_ceiling_gate_pass = true`.
* `all_gates_pass = true` only when every named gate is true.
* Closeout branch matches manifest branch.
* Source/rendered/runtime/state mutation delta is `0`.
* Top-doc addendum includes non-claims.
* Additive-only diff inspection passes.
* Validation ceiling is stated.

---

## 7. Validation Plan

### Automated Validation

Required change review:

```powershell
git diff --stat
git diff
```

Required load-bearing artifact validation:

```text
JSON parse for every generated JSON artifact
JSONL parse for every generated JSONL artifact
template_authority_checked = true
execution_contract_checked = true
definition_referent_gate_pass
definition_referent_sha256_or_readpoint_pin
definition_edge_granularity_check
input_manifest_sha256 match
included_corpus_count = 4
locked corpus path set equals predecessor corpus lock
locked corpus physical path pin check
excluded surface non-consumption check
detector field requirement parse/check
field inventory completeness check
schema_traversal_gate_pass
nested_array_object_traversal_check
stringified_json_candidate_detection_check
unsupported_value_shape_count recorded
candidate classification exhaustiveness check
readable / forbidden / ambiguous manifest validation
field-to-requirement mapping completeness check
edge semantics seal presence check
manifest schema validation
manifest hash validation
required field absence behavior check
forbidden field consumption check
ambiguous field branch-routing check
branch_taxonomy_consistency_check
branch_alias_to_named_taxonomy_mapping_check
complete_vs_blocked_closeout_state_consistency_check
downstream_count_round_disposition_check
FIELD_MAP_SEALED_downstream_count_handoff_check
branch_c_approval_or_blocked_disposition_check
live_corpus_occurrence_count_absence_check
text-only fallback absence check
keyword fallback absence check
body text substring fallback absence check
category-tag-only fallback absence check
diagnostic/report-only fallback absence check
branch determination / manifest consistency check
no-count guard check
2-run determinism digest match for field inventory / classification / mapping / manifest
artifact hash manifest validation
field_map_gate_pass
branch_semantics_gate_pass
schema_traversal_gate_pass
no_count_guard_pass
non_mutation_gate_pass
review_gate_pass
claim_ceiling_gate_pass
all_gates_pass
non-mutation hash diff for source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, quality_state, publish_state, and runtime_state when those surfaces are included in the stated ceiling
```

Optional repo ceremony validation:

```text
Python unittest, Lua syntax, lint, or broader repo checks only if touched surface requires them
or if closeout explicitly claims those exact validations.
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

If Python unittest or Lua syntax validation is skipped for a docs/static-artifact-only closeout, the closeout validation report must state the explicit skip rationale and must not claim Python pipeline or Lua syntax validation.

### Manual Validation

* Review that the round is field-map readiness only and count-later.
* Review the sealed `LAYER4_ABSORPTION_CONFIRMED` definition referent path/readpoint/hash and edge granularity.
* Review direct predecessor readpoints and no-inheritance rule.
* Review branch taxonomy separation: complete success, complete negative seal, blocked.
* Review Branch A/B/C shorthand mapping to named taxonomy.
* Review detector field requirement for definition expansion.
* Review physical path pin for the 4 locked corpus paths.
* Review field inventory samples for each locked corpus path.
* Review nested array/object traversal and stringified JSON candidate handling.
* Review candidate classification reasons, especially for `provenance`, `cluster_summary`, body text, section labels, and diagnostic/report fields.
* Review that explicit trace edge requires source -> target relation, not co-occurrence.
* Review required / optional / forbidden field separation.
* Review Branch B wording if selected.
* Review Branch B downstream count round disposition if selected.
* Review Branch C wording if ambiguous fields are present.
* Review no-count guard evidence and confirm no live-corpus occurrence count was performed.
* Review synthetic fixture readiness probe report, if present, for claim overreach.
* Review staged top-doc addendum candidate for additive-only wording.
* Review final diff for non-claims and validation ceiling.

### Validation Limits

This execution will not perform:

* `LAYER4_ABSORPTION_CONFIRMED` final count.
* Layer4 absorption resolved validation.
* Layer4 policy redesign validation.
* SUSPECT tier validation.
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

Touched. This round seals detector field-map/readiness authority for a future `LAYER4_ABSORPTION_CONFIRMED` count round. It does not create writer authority, publish authority, runtime authority, quality authority, or default compose authority.

### Runtime Behavior Surface

None intended. Runtime Lua, packaged Lua, runtime chunks, bridge payloads, Browser, Wiki, and Tooltip behavior remain unchanged.

### Compatibility Surface

None intended for runtime compatibility. Internal workflow compatibility may be affected if future count rounds are required to consume the sealed field map or blocked/unavailable manifest.

### Sealed Artifact Surface

Touched additively. New round-local sealed artifacts may be created, including field requirement, field inventory, trace candidate classification, field map manifest, branch determination, review report, and closeout packet. Existing sealed artifacts are consumed read-only.

### Public-Facing Output Surface

None intended. The round does not change item descriptions, tooltip content, wiki text, Browser sorting/filtering, README public claims, Workshop status, or release posture.

---

## 9. Risk Analysis

### Architecture Risk

* Sealed `LAYER4_ABSORPTION_CONFIRMED` definition referent may be missing or may lack source object to body slot edge granularity.
* Text similarity, keyword match, or body text substring could accidentally become a substitute for explicit trace edge.
* Category tags or `cluster_summary` could be mistaken for source -> target trace edges.
* Diagnostic/report/preview/historical fields could be promoted to detector authority.
* Source object and target body slot co-occurrence could be treated as an edge without relation structure.
* Ambiguous edge candidates could be forced into Branch A or Branch B instead of Branch C.
* Trace edge absence could be overclaimed as actual Layer4 absorption zero.
* A readiness probe could be overread as a live-corpus occurrence count if the no-count guard is weakened.
* Branch B could be incorrectly "fixed" by adding new absorption-trace fields inside this round.
* Detector readiness and absorption resolution could be conflated.

### Runtime Risk

* Expected runtime risk is none if scope is respected.
* Validation commands or helper scripts could accidentally regenerate rendered or runtime artifacts.
* Any side-effect mutation must block non-mutation closeout until restored and explained.

### Compatibility Risk

* Public or internal wording could imply compatibility preservation without compatibility testing.
* Future count workflows may fail if the manifest is too strict and no update procedure exists.
* Future count workflows may undercount if a legitimate explicit trace field is incorrectly rejected.

### Regression Risk

* Field inventory may miss nested objects, arrays, optional fields, or stringified JSON.
* Same field names may mean different things across artifacts.
* Optional field handling may weaken FAIL-LOUD behavior.
* Synthetic fixture readiness output may be overread as current count evidence.
* Branch C blocked disposition may be written like a completed outcome.
* Top-doc promotion may create DECISIONS / ARCHITECTURE / ROADMAP wording drift.
* Dirty working tree state may make artifact hashes non-reproducible if not recorded.
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
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_seal_round/
```

3. If optional round-local helper scripts were created and are invalid, remove or quarantine only those helper scripts.

4. If shared tooling was changed without an approved scope amendment, stop and revert only changes made by this round after identifying them.

5. If `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` receive invalid additive wording, correct with additive clarification when possible. If duplicate text was added by this round, remove only that duplicate addition.

6. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` changed unexpectedly, stop and identify the exact source of mutation before reverting only this round's changes.

7. If validation commands regenerate output as side effects, restore the pre-validation frozen snapshot and rerun non-mutation hash diff before making any non-mutation claim.

8. If definition referent verification fails, close with `blocked_with_definition_referent_missing` or `blocked_with_detector_field_requirement_unsealed` instead of deriving a field requirement.

9. If field inventory, classification, mapping, or manifest validation fails, close with the specific blocked branch instead of rewriting the claim boundary into success.

10. If a sealed closeout later proves incorrect, do not rewrite the sealed body directly. Add a later correction or supersession artifact.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains a wiki-style information module: no interpretation, recommendation, comparison, or gameplay policy expansion.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation must remain intact.
* Existing `LAYER4_ABSORPTION_CONFIRMED` definition remains sealed only if Phase 0 verifies a sealed definition referent.
* If the definition referent is missing or lacks edge granularity, this round must block rather than define it.
* SUSPECT tier remains out of scope.
* The 2026-05-31 locked corpus must not be reopened by this round.
* The detector authority corpus is limited to the 4 locked paths.
* The 4 locked paths must be pinned by repository-relative and physical absolute path.
* Excluded surfaces must not be promoted to current detector authority.
* Historical, diagnostic, report-only, preview-only, staging residue, and test fixture surfaces must not be promoted to current measurement corpus.
* The 2026-04-29 Layer4 zero-count must not be inherited as current count.
* Confirmed true requires an explicit Layer4 source object to Layer3 body slot trace edge.
* Text similarity, keyword match, body text substring, expression pattern, and section label-only matching are forbidden.
* Category tag-only, diagnostic-only, report-only, preview-only, and historical-only fields are forbidden detector evidence.
* Co-occurrence of source and target fields is not sufficient without source -> target relation structure.
* Missing required fields must fail loud or route to blocked/unavailable branch.
* Ambiguous trace fields must route to Branch C and must not be forced into A/B.
* Branch C is an approved blocked disposition only; it is not a complete success outcome.
* Trace-edge-field absence must use measurement-unavailable language.
* Field-map sealed status is occurrence-count independent and must hand off to a separate downstream authoritative count round.
* This round must not use no-readable-edge-zero or any other zero-occurrence closeout branch.
* This round must not scan live corpus rows to produce readable trace edge count, confirmed candidate count, rejected fallback count, or any current count substitute.
* Branch B must record downstream count round disposition as `cancelled`, `not_applicable_under_current_corpus`, or `redefined_as_future_anchor_or_definition_round`.
* Branch B must not be resolved by adding new absorption-trace fields to source/rendered/body artifacts inside this round.
* Machine-enforced preflight must not be claimed unless implemented and validated.
* A round-local readiness harness must not be represented as repository-wide machine-enforced preflight.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, and `runtime_state` remain non-mutation targets.
* Existing sealed artifacts are consumed read-only.
* Live canonical docs promotion requires review PASS or accepted Conditional PASS.
* Additive docs wording must preserve non-claims and validation ceiling.
* Validation may not be claimed as passed unless the exact relevant command exits with code `0`.
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

`partial` and `implemented_only` are not planned sealed success states for this detector field-map seal round. `complete` is valid only within the validation ceiling stated in this plan and only if:

```text
scope statement exists
execution_scale = governance
scope_qualifier = docs_static_artifact_detector_field_map_seal
template_authority_checked = true
execution_contract_checked = true
definition_referent_gate_pass = true
sealed definition referent path/readpoint/hash is pinned
definition edge granularity check passes
predecessor corpus lock is verified
input_manifest_sha256 matches predecessor
included_corpus_count = 4
locked corpus physical path pin exists
detector field requirement exists
locked corpus field inventory exists
nested_array_object_traversal_check passes
stringified_json_candidate_detection_check passes
unsupported_value_shape_count is recorded
trace candidate classification exists
readable / forbidden / ambiguous manifests exist
edge semantics seal exists
field-to-requirement mapping exists
all candidate fields are mapped or explicitly rejected
required / optional / forbidden fields are separated
missing field behavior is recorded
ambiguous field behavior is recorded
text-only fallback is absent
keyword fallback is absent
body text substring fallback is absent
category-tag-only fallback is absent
diagnostic/report-only fallback is absent
field map manifest or blocked/unavailable manifest exists
detector_closeout_branch is explicit
branch determination matches mapping and manifest
branch_taxonomy_consistency_check passes
branch_alias_to_named_taxonomy_mapping_check passes
complete_vs_blocked_closeout_state_consistency_check passes
downstream_count_round_disposition_check passes if Branch B is selected
FIELD_MAP_SEALED_downstream_count_handoff_check passes if Branch A is selected
branch_c_approval_or_blocked_disposition_check passes if ambiguous fields exist
no-count guard evidence exists
live_corpus_occurrence_count_absence_check passes
synthetic fixture readiness probe is absent unless Branch A field map is sealed
synthetic fixture readiness probe, if present, is bounded as schema/fixture evidence and not final count
JSON/JSONL parse passes
2-run determinism passes for generated field inventory / classification / mapping / manifest
artifact hash manifest exists
review gate PASS or accepted Conditional PASS exists
field_map_gate_pass is recorded
branch_semantics_gate_pass is recorded
schema_traversal_gate_pass is recorded
no_count_guard_pass is recorded
non_mutation_gate_pass is recorded
review_gate_pass is recorded
claim_ceiling_gate_pass is recorded
hard gate all_gates_pass = true only when every named gate is true
non-mutation evidence passes for every surface included in the stated ceiling
closeout non-claims are explicit
claim boundary does not exceed detector field-map readiness
```

Expected branch taxonomy:

```text
complete_success:
  FIELD_MAP_SEALED

complete_negative_seal:
  TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE

blocked:
  TRACE_EDGE_FIELDS_PRESENT_BUT_AMBIGUOUS
  BLOCKED_ANCHOR
  DEFINITION_REFERENT_MISSING
  FIELD_MAP_REJECTED_TEXT_ONLY
  FIELD_MAP_REJECTED_DIAGNOSTIC_ONLY
```

Default expected branch:

```text
No default success branch. Branch must be selected by field inventory, trace candidate classification, and field-to-requirement mapping evidence.
```

Expected final claim boundary:

```text
Current locked corpus 기준으로 LAYER4_ABSORPTION_CONFIRMED detector field map이 sealed 되었거나,
trace edge field 부재로 confirmed measurement unavailable이 sealed 되었다.
FIELD_MAP_SEALED는 occurrence 수와 무관하게 downstream authoritative count round로 handoff한다.
Ambiguous trace fields are blocked, not complete success.
```

Expected non-claims:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출 아님
live-corpus occurrence count 산출 아님
zero-occurrence closeout branch 아님
Layer4 absorption resolved 아님
Layer4 policy redesign 아님
SUSPECT tier coverage 아님
FUNCTION_NARROW second rollout 아님
ACQ_DOMINANT publish review 아님
publish mutation review 아님
source/rendered/runtime/state mutation 아님
runtime rollout 아님
manual in-game validation pass 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
새 absorption-trace field 추가 아님
CONFIRMED 정의 재정의 아님
repository-wide machine-enforced preflight 아님
```
